"""
Analysis Endpoint - 이력서-JD 매칭 분석 API
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import Optional, List
from uuid import UUID
import logging

from pydantic import BaseModel, Field

from app.models.schemas import (
    FileTypeEnum,
    ErrorCodeEnum,
    AnalysisRequestParams,
    AnalysisResultData,
    AnalysisResponse,
    CategoryScore,
)
from app.services.ingestion_service import (
    IngestionService,
    IngestionResult,
    get_ingestion_service,
)
from app.core.rag.retriever import (
    DocumentRetriever,
    get_retriever,
    analyze_skill_gaps,
    MatchResult,
)
from app.core.rag.vector_store import get_vector_store, VectorStore

# 로거 설정
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter()


# ============================================================================
# Request/Response 스키마
# ============================================================================


class IngestRequest(BaseModel):
    """벡터화 요청"""

    file_id: UUID = Field(..., description="벡터화할 파일 ID")
    skip_if_exists: bool = Field(
        default=True,
        description="이미 벡터화된 경우 스킵",
    )


class IngestResponse(BaseModel):
    """벡터화 응답"""

    success: bool
    file_id: str
    document_id: Optional[str] = None
    chunk_count: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    processing_time_ms: float = 0.0
    message: str
    error: Optional[str] = None


class MatchRequest(BaseModel):
    """매칭 분석 요청"""

    resume_id: UUID = Field(..., description="이력서 문서 ID (documents 테이블의 id)")
    jd_id: UUID = Field(..., description="채용공고 문서 ID (documents 테이블의 id)")


class MatchResponse(BaseModel):
    """매칭 분석 응답"""

    success: bool
    data: Optional[dict] = None
    message: str


class DocumentStatusResponse(BaseModel):
    """문서 상태 응답"""

    file_id: str
    filename: Optional[str] = None
    file_type: Optional[str] = None
    embedding_status: Optional[str] = None
    chunk_count: int = 0
    created_at: Optional[str] = None


class DocumentListResponse(BaseModel):
    """문서 목록 응답"""

    success: bool
    documents: List[DocumentStatusResponse]
    total: int
    message: str


# ============================================================================
# 벡터화 (Ingestion) 엔드포인트
# ============================================================================


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    summary="문서 벡터화",
    description="""
    ## 업로드된 문서를 벡터화하여 Supabase에 저장

    이 엔드포인트는 업로드 완료된 문서(file_id)를 벡터화합니다.

    ### 처리 과정:
    1. 텍스트를 의미 단위로 청킹 (섹션 보존)
    2. OpenAI text-embedding-3-small로 임베딩 생성
    3. Supabase pgvector에 저장

    ### 주의사항:
    - 업로드가 먼저 완료되어야 합니다 (`POST /api/v1/upload`)
    - 이미 벡터화된 문서는 기본적으로 스킵됩니다
    """,
    tags=["analysis"],
)
async def ingest_document(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
) -> IngestResponse:
    """문서 벡터화"""
    try:
        # 1. 문서 존재 확인
        vector_store = get_vector_store()
        doc = vector_store.get_document_by_file_id(request.file_id)

        # 이미 완료된 경우
        if doc and doc.get("embedding_status") == "completed" and request.skip_if_exists:
            return IngestResponse(
                success=True,
                file_id=str(request.file_id),
                document_id=doc.get("id"),
                chunk_count=doc.get("chunk_count", 0),
                message="Document already vectorized (skipped)",
            )

        # 2. Ingestion 실행
        # 주의: 실제로는 upload_result가 필요하므로,
        # 여기서는 이미 저장된 문서 정보로 처리해야 함
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "DOCUMENT_NOT_FOUND",
                        "message": f"Document with file_id {request.file_id} not found. Please upload first.",
                    },
                },
            )

        # 이미 문서가 있는 경우 상태 업데이트
        vector_store.update_document_status(
            request.file_id,
            embedding_status="processing",
        )

        return IngestResponse(
            success=True,
            file_id=str(request.file_id),
            document_id=doc.get("id"),
            chunk_count=doc.get("chunk_count", 0),
            message="Document is being processed",
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Ingest error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": ErrorCodeEnum.INTERNAL_SERVER_ERROR.value,
                    "message": str(e),
                },
            },
        )


# ============================================================================
# 매칭 분석 엔드포인트
# ============================================================================


@router.post(
    "/match",
    response_model=MatchResponse,
    status_code=status.HTTP_200_OK,
    summary="이력서-JD 매칭 분석",
    description="""
    ## 이력서와 채용공고 간 매칭 분석

    두 문서(이력서, JD)가 벡터화된 후 호출합니다.

    ### 분석 내용:
    - **overall_similarity**: 전체 문서 유사도 (0-1)
    - **match_score**: 매칭 점수 (0-100)
    - **match_grade**: 등급 (S/A/B/C/D)
    - **section_scores**: 섹션별 점수

    ### 선행 조건:
    1. 이력서 업로드 및 벡터화 완료
    2. JD 업로드 및 벡터화 완료
    """,
    tags=["analysis"],
)
async def analyze_match(request: MatchRequest) -> MatchResponse:
    """이력서-JD 매칭 분석"""
    try:
        # 1. 두 문서가 벡터화되었는지 확인 (id로 조회)
        vector_store = get_vector_store()

        resume_doc = vector_store.get_document_by_id(request.resume_id)
        jd_doc = vector_store.get_document_by_id(request.jd_id)

        if not resume_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "RESUME_NOT_FOUND",
                        "message": f"Resume document not found: {request.resume_id}",
                    },
                },
            )

        if not jd_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "JD_NOT_FOUND",
                        "message": f"Job description document not found: {request.jd_id}",
                    },
                },
            )

        # 벡터화 상태 확인
        if resume_doc.get("embedding_status") != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": "RESUME_NOT_VECTORIZED",
                        "message": "Resume is not vectorized yet. Please wait for vectorization to complete.",
                        "details": {"status": resume_doc.get("embedding_status")},
                    },
                },
            )

        if jd_doc.get("embedding_status") != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": "JD_NOT_VECTORIZED",
                        "message": "Job description is not vectorized yet. Please wait for vectorization to complete.",
                        "details": {"status": jd_doc.get("embedding_status")},
                    },
                },
            )

        # 2. 매칭 분석 실행 (file_id 사용 - retriever는 file_id 기반)
        retriever = get_retriever()
        resume_file_id = UUID(resume_doc.get("file_id"))
        jd_file_id = UUID(jd_doc.get("file_id"))

        # 3. 전체 텍스트 가져오기 (유사 기술 분석용)
        resume_text = resume_doc.get("cleaned_text") or resume_doc.get("text_content", "")
        jd_text = jd_doc.get("cleaned_text") or jd_doc.get("text_content", "")

        match_result = retriever.analyze_match(
            resume_file_id=resume_file_id,
            jd_file_id=jd_file_id,
            resume_text=resume_text,
            jd_text=jd_text,
        )

        # 4. 응답 구성
        return MatchResponse(
            success=True,
            data=match_result.to_dict(),
            message="Match analysis completed successfully",
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Match analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": ErrorCodeEnum.INTERNAL_SERVER_ERROR.value,
                    "message": str(e),
                },
            },
        )


@router.post(
    "/gap-analysis",
    response_model=MatchResponse,
    status_code=status.HTTP_200_OK,
    summary="스킬 갭 분석",
    description="""
    ## 이력서-JD 간 스킬 갭 분석

    매칭 분석에 더해 강점/약점을 분류하고 추천을 제공합니다.
    """,
    tags=["analysis"],
)
async def analyze_gaps(request: MatchRequest) -> MatchResponse:
    """스킬 갭 분석"""
    try:
        # 문서 확인 (id로 조회)
        vector_store = get_vector_store()

        resume_doc = vector_store.get_document_by_id(request.resume_id)
        jd_doc = vector_store.get_document_by_id(request.jd_id)

        if not resume_doc or resume_doc.get("embedding_status") != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": "RESUME_NOT_READY",
                        "message": "Resume is not ready for analysis",
                    },
                },
            )

        if not jd_doc or jd_doc.get("embedding_status") != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": "JD_NOT_READY",
                        "message": "Job description is not ready for analysis",
                    },
                },
            )

        # 갭 분석 실행 (file_id 사용)
        resume_file_id = UUID(resume_doc.get("file_id"))
        jd_file_id = UUID(jd_doc.get("file_id"))

        # 전체 텍스트 가져오기 (유사 기술 분석용)
        resume_text = resume_doc.get("cleaned_text") or resume_doc.get("text_content", "")
        jd_text = jd_doc.get("cleaned_text") or jd_doc.get("text_content", "")

        gap_result = analyze_skill_gaps(
            resume_file_id=resume_file_id,
            jd_file_id=jd_file_id,
            resume_text=resume_text,
            jd_text=jd_text,
        )

        return MatchResponse(
            success=True,
            data=gap_result,
            message="Gap analysis completed successfully",
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Gap analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": ErrorCodeEnum.INTERNAL_SERVER_ERROR.value,
                    "message": str(e),
                },
            },
        )


# ============================================================================
# 문서 관리 엔드포인트
# ============================================================================


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="벡터화된 문서 목록 조회",
    tags=["analysis"],
)
async def list_documents(
    file_type: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> DocumentListResponse:
    """벡터화된 문서 목록 조회"""
    try:
        vector_store = get_vector_store()

        if file_type:
            try:
                file_type_enum = FileTypeEnum(file_type.lower())
                docs = vector_store.get_documents_by_type(file_type_enum, status_filter)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "error": {
                            "code": "INVALID_FILE_TYPE",
                            "message": f"Invalid file_type: {file_type}",
                        },
                    },
                )
        else:
            # 전체 요약 조회
            summary = vector_store.get_all_documents_summary()
            return DocumentListResponse(
                success=True,
                documents=[],
                total=summary.get("total_documents", 0),
                message=f"Total documents: {summary}",
            )

        documents = [
            DocumentStatusResponse(
                file_id=str(doc.get("file_id")),
                filename=doc.get("filename"),
                file_type=doc.get("file_type"),
                embedding_status=doc.get("embedding_status"),
                chunk_count=doc.get("chunk_count", 0),
                created_at=doc.get("created_at"),
            )
            for doc in docs
        ]

        return DocumentListResponse(
            success=True,
            documents=documents,
            total=len(documents),
            message=f"Found {len(documents)} documents",
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"List documents error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": ErrorCodeEnum.INTERNAL_SERVER_ERROR.value,
                    "message": str(e),
                },
            },
        )


@router.get(
    "/documents/{file_id}",
    response_model=DocumentStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="문서 상태 조회",
    tags=["analysis"],
)
async def get_document_status(file_id: UUID) -> DocumentStatusResponse:
    """특정 문서 상태 조회"""
    try:
        vector_store = get_vector_store()
        stats = vector_store.get_document_stats(file_id)

        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "DOCUMENT_NOT_FOUND",
                        "message": f"Document not found: {file_id}",
                    },
                },
            )

        return DocumentStatusResponse(
            file_id=str(stats.get("file_id")),
            filename=stats.get("filename"),
            file_type=stats.get("file_type"),
            embedding_status=stats.get("embedding_status"),
            chunk_count=stats.get("chunk_count", 0),
            created_at=str(stats.get("created_at")) if stats.get("created_at") else None,
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Get document status error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": ErrorCodeEnum.INTERNAL_SERVER_ERROR.value,
                    "message": str(e),
                },
            },
        )


@router.delete(
    "/documents/{file_id}",
    status_code=status.HTTP_200_OK,
    summary="문서 삭제",
    tags=["analysis"],
)
async def delete_document(file_id: UUID):
    """문서 및 벡터 삭제"""
    try:
        vector_store = get_vector_store()
        deleted = vector_store.delete_document(file_id)

        if deleted:
            return {
                "success": True,
                "message": f"Document {file_id} deleted successfully",
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "DOCUMENT_NOT_FOUND",
                        "message": f"Document not found: {file_id}",
                    },
                },
            )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Delete document error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": ErrorCodeEnum.INTERNAL_SERVER_ERROR.value,
                    "message": str(e),
                },
            },
        )


# ============================================================================
# Health Check
# ============================================================================


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="분석 서비스 헬스 체크",
    tags=["analysis"],
)
async def analysis_health_check():
    """분석 서비스 헬스 체크"""
    try:
        # Supabase 연결 확인
        vector_store = get_vector_store()
        summary = vector_store.get_all_documents_summary()

        return {
            "status": "ok",
            "service": "analysis",
            "supabase": "connected",
            "documents": summary.get("total_documents", 0),
        }

    except Exception as e:
        return {
            "status": "degraded",
            "service": "analysis",
            "supabase": "disconnected",
            "error": str(e),
        }

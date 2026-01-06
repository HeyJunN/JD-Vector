"""
Upload Endpoint - PDF 파일 업로드 API
"""

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, status
from typing import Optional
import logging

from app.models.schemas import (
    UploadResponse,
    UploadResponseData,
    ErrorResponse,
    ErrorDetail,
    FileTypeEnum,
    ParserTypeEnum,
    ErrorCodeEnum,
)
from app.services.upload_service import (
    process_pdf_upload,
    UploadServiceError,
    get_upload_statistics,
)

# 로거 설정
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter()


# ============================================================================
# 에러 코드 → HTTP 상태 코드 매핑
# ============================================================================

ERROR_STATUS_MAP = {
    ErrorCodeEnum.FILE_TOO_LARGE: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    ErrorCodeEnum.INVALID_FILE_TYPE: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    ErrorCodeEnum.PDF_PARSE_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
    ErrorCodeEnum.FILE_UPLOAD_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCodeEnum.VALIDATION_ERROR: status.HTTP_400_BAD_REQUEST,
    ErrorCodeEnum.INTERNAL_SERVER_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


def get_http_status_code(error_code: ErrorCodeEnum) -> int:
    """에러 코드에 해당하는 HTTP 상태 코드 반환"""
    return ERROR_STATUS_MAP.get(error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# Upload Endpoint
# ============================================================================


@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "PDF 파일 업로드 및 파싱 성공",
            "model": UploadResponse,
        },
        400: {
            "description": "잘못된 요청 (유효성 검사 실패)",
            "model": ErrorResponse,
        },
        413: {
            "description": "파일 크기 초과",
            "model": ErrorResponse,
        },
        415: {
            "description": "지원하지 않는 파일 형식",
            "model": ErrorResponse,
        },
        422: {
            "description": "PDF 파싱 실패",
            "model": ErrorResponse,
        },
        500: {
            "description": "서버 내부 오류",
            "model": ErrorResponse,
        },
    },
    summary="PDF 파일 업로드 및 텍스트 추출",
    description="""
    ## PDF 파일 업로드 및 텍스트 추출 엔드포인트

    사용자의 이력서 또는 채용 공고(JD) PDF 파일을 업로드하고,
    텍스트를 추출하여 분석에 활용할 수 있도록 정제합니다.

    ### 주요 기능:
    - **자동 파서 선택**: file_type에 따라 최적의 PDF 파서 자동 선택
      - 이력서 (resume) → PyPDF (LangChain 호환)
      - 채용공고 (job_description) → pdfplumber (테이블 추출)
    - **텍스트 정제**: LLM 입력에 적합하도록 불필요한 공백, 줄바꿈 제거
    - **언어 감지**: 문서의 주 언어 자동 판별 (ko/en/mixed)
    - **메타데이터 추출**: 작성자, 페이지 수, 생성일 등

    ### 파일 제한:
    - 최대 크기: 20MB
    - 허용 형식: PDF (application/pdf)

    ### 반환값:
    - `text_content`: 원본 추출 텍스트
    - `cleaned_text`: 정제된 텍스트 (AI 분석용)
    - `metadata`: PDF 메타데이터 (페이지 수, 언어, 작성자 등)
    """,
    tags=["upload"],
)
async def upload_pdf(
    file: UploadFile = File(
        ...,
        description="업로드할 PDF 파일",
        media_type="application/pdf",
    ),
    file_type: str = Form(
        ...,
        description="파일 용도: 'resume' (이력서) 또는 'job_description' (채용공고)",
        example="resume",
    ),
    extract_tables: bool = Form(
        default=False,
        description="테이블 추출 여부 (pdfplumber 사용 시)",
    ),
    parser_type: str = Form(
        default="auto",
        description="PDF 파서 타입: 'auto', 'pypdf', 'pdfplumber', 'pymupdf'",
        example="auto",
    ),
) -> UploadResponse:
    """
    PDF 파일 업로드 및 텍스트 추출

    Args:
        file: 업로드할 PDF 파일
        file_type: 파일 용도 (resume/job_description)
        extract_tables: 테이블 추출 여부 (기본값: False)
        parser_type: PDF 파서 타입 (기본값: auto)

    Returns:
        UploadResponse: 파싱 결과 및 메타데이터

    Raises:
        HTTPException: 파일 업로드/파싱 실패 시
    """
    try:
        # 1. Enum 변환 및 유효성 검사
        try:
            file_type_enum = FileTypeEnum(file_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": ErrorCodeEnum.VALIDATION_ERROR.value,
                        "message": f"Invalid file_type: {file_type}. Must be 'resume' or 'job_description'.",
                        "details": {
                            "allowed_values": [e.value for e in FileTypeEnum],
                        },
                    },
                },
            )

        try:
            parser_type_enum = ParserTypeEnum(parser_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": ErrorCodeEnum.VALIDATION_ERROR.value,
                        "message": f"Invalid parser_type: {parser_type}. Must be one of: {[e.value for e in ParserTypeEnum]}",
                        "details": {
                            "allowed_values": [e.value for e in ParserTypeEnum],
                        },
                    },
                },
            )

        # 2. 파일명 검증
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": ErrorCodeEnum.VALIDATION_ERROR.value,
                        "message": "Filename is required",
                        "details": {},
                    },
                },
            )

        logger.info(
            f"Upload request received: {file.filename} "
            f"(type: {file_type_enum.value}, parser: {parser_type_enum.value})"
        )

        # 3. 업로드 서비스 호출
        response_data = process_pdf_upload(
            upload_file=file,
            file_type=file_type_enum,
            parser_type=parser_type_enum,
            extract_tables=extract_tables,
        )

        # 4. 통계 로깅
        stats = get_upload_statistics(response_data)
        logger.info(f"Upload statistics: {stats}")

        # 5. 성공 응답 반환
        return UploadResponse(
            success=True,
            data=response_data,
            message=f"PDF file '{file.filename}' uploaded and parsed successfully",
        )

    except UploadServiceError as e:
        # 정의된 서비스 예외
        logger.error(f"Upload service error: {e.message}", exc_info=True)

        http_status = get_http_status_code(e.code)

        raise HTTPException(
            status_code=http_status,
            detail={
                "success": False,
                "error": {
                    "code": e.code.value,
                    "message": e.message,
                    "details": e.details,
                },
            },
        )

    except HTTPException:
        # FastAPI HTTPException은 그대로 전파
        raise

    except Exception as e:
        # 예상하지 못한 예외
        logger.error(f"Unexpected error in upload endpoint: {str(e)}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": ErrorCodeEnum.INTERNAL_SERVER_ERROR.value,
                    "message": "An unexpected error occurred during file upload",
                    "details": {"error": str(e)},
                },
            },
        )


# ============================================================================
# Health Check Endpoint (for upload service)
# ============================================================================


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="업로드 서비스 헬스 체크",
    description="업로드 서비스가 정상 작동하는지 확인합니다.",
    tags=["upload"],
)
async def upload_health_check():
    """업로드 서비스 헬스 체크"""
    return {
        "status": "ok",
        "service": "upload",
        "message": "Upload service is running",
    }

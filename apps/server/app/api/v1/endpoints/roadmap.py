"""
Roadmap Endpoint - 맞춤형 학습 로드맵 생성 API
"""

from fastapi import APIRouter, HTTPException, status
from uuid import UUID
import logging

from app.models.schemas import (
    RoadmapGenerateRequest,
    RoadmapResponse,
    ErrorCodeEnum,
)
from app.services.roadmap_service import generate_roadmap
from app.core.rag.vector_store import get_vector_store

# 로거 설정
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter()


# ============================================================================
# 로드맵 생성 엔드포인트
# ============================================================================


@router.post(
    "/generate",
    response_model=RoadmapResponse,
    status_code=status.HTTP_200_OK,
    summary="맞춤형 학습 로드맵 생성",
    description="""
    ## 이력서-JD 스킬 갭 분석 결과를 바탕으로 학습 로드맵 생성

    스킬 갭 분석이 완료된 이력서와 JD를 기반으로,
    주차별 학습 계획, 체크리스트, 추천 리소스를 포함한 맞춤형 로드맵을 생성합니다.

    ### 주요 기능:
    - **AI 기반 커리큘럼**: GPT-4o mini가 생성하는 개인화된 학습 계획
    - **주차별 계획**: 4-12주 단위로 구성 가능 (기본 8주)
    - **체크리스트**: 각 주차마다 실행 가능한 태스크 제공
    - **리소스 추천**: 기술 키워드별 공식 문서, 튜토리얼 링크 자동 매핑
    - **프론트엔드 관점**: React 지망생이 이해하기 쉬운 설명 포함

    ### 선행 조건:
    1. 이력서 업로드 및 벡터화 완료
    2. JD 업로드 및 벡터화 완료

    ### 요청 예시:
    ```json
    {
      "resume_id": "uuid-of-resume-document",
      "jd_id": "uuid-of-jd-document",
      "target_weeks": 8
    }
    ```

    ### 응답 예시:
    ```json
    {
      "success": true,
      "data": {
        "total_weeks": 8,
        "match_grade": "C",
        "target_grade": "A",
        "summary": "현재 React 기초는 갖추었으나, TypeScript와 상태관리 경험이 부족합니다...",
        "key_improvement_areas": ["TypeScript", "상태관리", "테스트"],
        "weekly_plan": [
          {
            "week_number": 1,
            "title": "TypeScript 기초 다지기",
            "duration": "1 week",
            "description": "JavaScript에 타입을 더하는 TypeScript의 기본 개념을 학습합니다...",
            "keywords": ["typescript", "javascript"],
            "tasks": [
              {
                "task": "TypeScript 공식 핸드북 1-5장 학습",
                "completed": false,
                "priority": "high"
              }
            ],
            "resources": [
              {
                "title": "TypeScript 공식 핸드북",
                "url": "https://www.typescriptlang.org/docs/handbook/intro.html",
                "type": "documentation",
                "description": "TypeScript 핵심 개념 학습"
              }
            ]
          }
        ]
      },
      "message": "Roadmap generated successfully"
    }
    ```
    """,
    tags=["roadmap"],
)
async def create_roadmap(request: RoadmapGenerateRequest) -> RoadmapResponse:
    """맞춤형 학습 로드맵 생성"""
    try:
        # 1. 문서 존재 및 벡터화 상태 확인
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

        # 2. 로드맵 생성
        roadmap_data = generate_roadmap(
            resume_id=request.resume_id,
            jd_id=request.jd_id,
            target_weeks=request.target_weeks or 8,
        )

        # 3. 응답 구성
        return RoadmapResponse(
            success=True,
            data=roadmap_data,
            message="Roadmap generated successfully",
        )

    except HTTPException:
        raise

    except ValueError as e:
        logger.error(f"Roadmap generation validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e),
                },
            },
        )

    except Exception as e:
        logger.error(f"Roadmap generation error: {e}", exc_info=True)
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
    summary="로드맵 서비스 헬스 체크",
    tags=["roadmap"],
)
async def roadmap_health_check():
    """로드맵 서비스 헬스 체크"""
    try:
        # OpenAI API 키 설정 확인
        from app.core.config import settings

        has_api_key = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "")

        return {
            "status": "ok" if has_api_key else "degraded",
            "service": "roadmap",
            "openai_configured": has_api_key,
            "llm_model": settings.LLM_MODEL,
        }

    except Exception as e:
        return {
            "status": "error",
            "service": "roadmap",
            "error": str(e),
        }

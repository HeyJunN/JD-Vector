"""
Pydantic Schemas for Request/Response Models
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4


# ============================================================================
# Enums
# ============================================================================


class FileTypeEnum(str, Enum):
    """파일 타입 구분"""

    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"


class ParserTypeEnum(str, Enum):
    """PDF 파서 타입"""

    PYPDF = "pypdf"
    PDFPLUMBER = "pdfplumber"
    PYMUPDF = "pymupdf"
    AUTO = "auto"


class ErrorCodeEnum(str, Enum):
    """에러 코드"""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    PDF_PARSE_ERROR = "PDF_PARSE_ERROR"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_UPLOAD_ERROR = "FILE_UPLOAD_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


# ============================================================================
# Request Schemas
# ============================================================================


class UploadRequestParams(BaseModel):
    """
    업로드 요청 파라미터 (multipart/form-data의 필드)
    실제 파일은 FastAPI의 UploadFile로 처리됨
    """

    model_config = ConfigDict(use_enum_values=True)

    file_type: FileTypeEnum = Field(
        ...,
        description="파일 용도 (resume: 이력서, job_description: 채용공고)",
    )
    extract_tables: bool = Field(
        default=False,
        description="테이블 추출 여부 (pdfplumber 사용 시)",
    )
    parser_type: ParserTypeEnum = Field(
        default=ParserTypeEnum.AUTO,
        description="사용할 PDF 파서 (기본값: auto - file_type에 따라 자동 선택)",
    )


# ============================================================================
# Response Schemas
# ============================================================================


class PDFMetadata(BaseModel):
    """PDF 메타데이터"""

    model_config = ConfigDict(use_enum_values=True)

    author: Optional[str] = Field(None, description="문서 작성자")
    created_date: Optional[str] = Field(None, description="문서 생성 일자")
    modified_date: Optional[str] = Field(None, description="문서 수정 일자")
    title: Optional[str] = Field(None, description="문서 제목")
    subject: Optional[str] = Field(None, description="문서 주제")
    page_count: int = Field(..., description="총 페이지 수")
    has_tables: bool = Field(False, description="테이블 포함 여부")
    language: str = Field(default="unknown", description="문서 주 언어 (ko/en/mixed/unknown)")
    parser_used: ParserTypeEnum = Field(..., description="사용된 파서")
    file_size_bytes: int = Field(..., description="파일 크기 (바이트)")
    extraction_time_ms: float = Field(..., description="텍스트 추출 소요 시간 (밀리초)")


class UploadResponseData(BaseModel):
    """업로드 성공 응답 데이터"""

    model_config = ConfigDict(use_enum_values=True)

    file_id: UUID = Field(default_factory=uuid4, description="생성된 파일 고유 ID")
    filename: str = Field(..., description="원본 파일명")
    file_type: FileTypeEnum = Field(..., description="파일 용도")
    text_content: str = Field(..., description="추출된 텍스트 내용")
    cleaned_text: str = Field(..., description="정제된 텍스트 (LLM 입력용)")
    word_count: int = Field(..., description="단어 수")
    char_count: int = Field(..., description="문자 수")
    metadata: PDFMetadata = Field(..., description="PDF 메타데이터")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성 시각")


class UploadResponse(BaseModel):
    """업로드 API 응답"""

    success: bool = Field(..., description="성공 여부")
    data: Optional[UploadResponseData] = Field(None, description="응답 데이터")
    message: str = Field(..., description="응답 메시지")


# ============================================================================
# Error Schemas
# ============================================================================


class ErrorDetail(BaseModel):
    """에러 상세 정보"""

    model_config = ConfigDict(use_enum_values=True)

    code: ErrorCodeEnum = Field(..., description="에러 코드")
    message: str = Field(..., description="에러 메시지")
    details: Optional[Dict[str, Any]] = Field(None, description="추가 상세 정보")


class ErrorResponse(BaseModel):
    """에러 응답"""

    success: bool = Field(False, description="성공 여부 (항상 False)")
    error: ErrorDetail = Field(..., description="에러 정보")


# ============================================================================
# Analysis Schemas (Phase 3용 준비)
# ============================================================================


class SkillItem(BaseModel):
    """기술 스택 항목"""

    name: str = Field(..., description="기술명")
    category: str = Field(..., description="카테고리 (언어/프레임워크/도구 등)")
    proficiency: Optional[str] = Field(None, description="숙련도 (if available)")


class AnalysisRequestParams(BaseModel):
    """분석 요청 파라미터 (Phase 3)"""

    resume_file_id: UUID = Field(..., description="이력서 파일 ID")
    jd_file_id: UUID = Field(..., description="채용공고 파일 ID")


class CategoryScore(BaseModel):
    """기술 스택 카테고리별 점수"""

    category: str = Field(..., description="카테고리명 (언어/프레임워크/도구 등)")
    score: float = Field(..., ge=0.0, le=100.0, description="점수 (0-100)")
    matched_skills: List[str] = Field(default_factory=list, description="매칭된 기술 목록")
    missing_skills: List[str] = Field(default_factory=list, description="부족한 기술 목록")


class AnalysisResultData(BaseModel):
    """분석 결과 데이터"""

    match_score: float = Field(..., ge=0.0, le=100.0, description="전체 매칭 점수")
    match_grade: str = Field(..., description="매칭 등급 (S/A/B/C/D)")
    category_scores: List[CategoryScore] = Field(..., description="카테고리별 점수 (Radar Chart용)")
    resume_skills: List[SkillItem] = Field(..., description="이력서에서 추출된 기술")
    jd_skills: List[SkillItem] = Field(..., description="JD에서 요구하는 기술")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="코사인 유사도 점수")


class AnalysisResponse(BaseModel):
    """분석 결과 응답 (Phase 3)"""

    success: bool = Field(..., description="성공 여부")
    data: Optional[AnalysisResultData] = Field(None, description="분석 결과 데이터")
    message: str = Field(..., description="응답 메시지")


# ============================================================================
# Roadmap Schemas (Phase 5용 준비)
# ============================================================================


class RoadmapItem(BaseModel):
    """로드맵 항목"""

    title: str = Field(..., description="할 일 제목")
    description: str = Field(..., description="상세 설명")
    priority: int = Field(..., ge=1, le=3, description="우선순위 (1:높음, 3:낮음)")
    estimated_weeks: int = Field(..., description="예상 소요 주차")
    category: str = Field(..., description="카테고리")


class RoadmapResponse(BaseModel):
    """로드맵 생성 응답 (Phase 5)"""

    success: bool = Field(..., description="성공 여부")
    data: Optional[List[RoadmapItem]] = Field(None, description="로드맵 항목 리스트")
    message: str = Field(..., description="응답 메시지")

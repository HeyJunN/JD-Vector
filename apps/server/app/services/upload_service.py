"""
Upload Service - 파일 업로드 비즈니스 로직
"""

import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
import logging

from fastapi import UploadFile

from app.core.config import settings
from app.models.schemas import (
    FileTypeEnum,
    ParserTypeEnum,
    UploadResponseData,
    PDFMetadata,
    ErrorCodeEnum,
)
from app.utils.pdf_parser import parse_pdf, is_valid_pdf
from app.core.rag.document_loader import load_document

# 로거 설정
logger = logging.getLogger(__name__)


# ============================================================================
# 예외 클래스
# ============================================================================


class UploadServiceError(Exception):
    """업로드 서비스 기본 예외"""

    def __init__(self, code: ErrorCodeEnum, message: str, details: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class FileTooLargeError(UploadServiceError):
    """파일 크기 초과 예외"""

    def __init__(self, size: int, max_size: int):
        super().__init__(
            code=ErrorCodeEnum.FILE_TOO_LARGE,
            message=f"File size ({size} bytes) exceeds maximum allowed size ({max_size} bytes)",
            details={"file_size": size, "max_size": max_size},
        )


class InvalidFileTypeError(UploadServiceError):
    """잘못된 파일 타입 예외"""

    def __init__(self, content_type: str):
        super().__init__(
            code=ErrorCodeEnum.INVALID_FILE_TYPE,
            message=f"Invalid file type: {content_type}. Only PDF files are allowed.",
            details={"content_type": content_type, "allowed_types": settings.ALLOWED_FILE_TYPES},
        )


class PDFParseError(UploadServiceError):
    """PDF 파싱 실패 예외"""

    def __init__(self, original_error: str):
        super().__init__(
            code=ErrorCodeEnum.PDF_PARSE_ERROR,
            message="Failed to parse PDF file",
            details={"error": original_error},
        )


class FileUploadError(UploadServiceError):
    """파일 업로드 처리 실패 예외"""

    def __init__(self, original_error: str):
        super().__init__(
            code=ErrorCodeEnum.FILE_UPLOAD_ERROR,
            message="Failed to process uploaded file",
            details={"error": original_error},
        )


# ============================================================================
# 파일 검증
# ============================================================================


def validate_file_size(file: UploadFile) -> None:
    """
    파일 크기 검증

    Args:
        file: 업로드된 파일

    Raises:
        FileTooLargeError: 파일 크기 초과 시
    """
    # UploadFile은 size 속성이 없으므로, 파일을 읽어서 확인
    # 하지만 이는 비효율적이므로, 임시 저장 후 검증하는 방식 사용
    pass  # 임시 저장 시 검증


def validate_content_type(content_type: str) -> None:
    """
    파일 MIME 타입 검증

    Args:
        content_type: 파일 MIME 타입

    Raises:
        InvalidFileTypeError: 허용되지 않은 타입일 시
    """
    if content_type not in settings.ALLOWED_FILE_TYPES:
        raise InvalidFileTypeError(content_type)


def validate_pdf_file(file_path: Path) -> None:
    """
    PDF 파일 유효성 검증

    Args:
        file_path: PDF 파일 경로

    Raises:
        PDFParseError: 유효하지 않은 PDF일 시
    """
    if not is_valid_pdf(file_path):
        raise PDFParseError("Invalid or corrupted PDF file")


# ============================================================================
# 임시 파일 관리
# ============================================================================


def save_upload_file_temporarily(upload_file: UploadFile) -> Path:
    """
    업로드된 파일을 임시 디렉토리에 저장

    Args:
        upload_file: FastAPI UploadFile

    Returns:
        저장된 임시 파일 경로

    Raises:
        FileUploadError: 파일 저장 실패 시
        FileTooLargeError: 파일 크기 초과 시
    """
    try:
        # 임시 파일 생성 (자동 삭제되지 않도록 delete=False)
        suffix = Path(upload_file.filename).suffix if upload_file.filename else ".pdf"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_path = Path(temp_file.name)

        # 파일 내용 복사
        bytes_written = 0
        chunk_size = 1024 * 1024  # 1MB chunks

        try:
            while chunk := upload_file.file.read(chunk_size):
                bytes_written += len(chunk)

                # 크기 제한 확인
                if bytes_written > settings.MAX_UPLOAD_SIZE:
                    temp_file.close()
                    temp_path.unlink()  # 임시 파일 삭제
                    raise FileTooLargeError(bytes_written, settings.MAX_UPLOAD_SIZE)

                temp_file.write(chunk)

        finally:
            temp_file.close()

        logger.info(f"File saved temporarily: {temp_path} ({bytes_written} bytes)")
        return temp_path

    except FileTooLargeError:
        raise
    except Exception as e:
        logger.error(f"Failed to save upload file: {str(e)}")
        raise FileUploadError(str(e))


def cleanup_temp_file(file_path: Path) -> None:
    """
    임시 파일 삭제

    Args:
        file_path: 삭제할 파일 경로
    """
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Temporary file deleted: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to delete temporary file {file_path}: {str(e)}")


# ============================================================================
# 메인 비즈니스 로직
# ============================================================================


def process_pdf_upload(
    upload_file: UploadFile,
    file_type: FileTypeEnum,
    parser_type: ParserTypeEnum = ParserTypeEnum.AUTO,
    extract_tables: bool = False,
) -> UploadResponseData:
    """
    PDF 파일 업로드 처리 메인 함수

    전체 플로우:
    1. 파일 검증 (MIME 타입)
    2. 임시 저장
    3. 파일 크기 및 PDF 유효성 검증
    4. PDF 파싱
    5. Document 생성
    6. 응답 데이터 구성
    7. 임시 파일 정리

    Args:
        upload_file: FastAPI UploadFile
        file_type: 파일 용도 (resume/job_description)
        parser_type: PDF 파서 타입 (기본값: AUTO)
        extract_tables: 테이블 추출 여부

    Returns:
        UploadResponseData

    Raises:
        UploadServiceError: 처리 중 에러 발생 시
    """
    temp_path: Optional[Path] = None

    try:
        # 1. MIME 타입 검증
        content_type = upload_file.content_type or "application/octet-stream"
        validate_content_type(content_type)

        # 2. 임시 파일 저장
        temp_path = save_upload_file_temporarily(upload_file)
        file_size_bytes = temp_path.stat().st_size

        # 3. PDF 유효성 검증
        validate_pdf_file(temp_path)

        # 4. 파일 ID 생성
        file_id = uuid4()
        filename = upload_file.filename or f"{file_id}.pdf"

        # 5. PDF 파싱
        logger.info(f"Parsing PDF: {filename} (type: {file_type}, parser: {parser_type})")

        try:
            parsed_result = parse_pdf(
                file_path=temp_path,
                file_type=file_type,
                parser_type=parser_type,
                extract_tables=extract_tables,
            )
        except Exception as e:
            logger.error(f"PDF parsing failed for {filename}: {str(e)}")
            raise PDFParseError(str(e))

        # 6. Document 생성 (Phase 3에서 활용)
        try:
            documents, metadata = load_document(
                file_path=temp_path,
                file_id=file_id,
                filename=filename,
                file_type=file_type,
                parser_type=parser_type,
                extract_tables=extract_tables,
                use_langchain_loader=False,  # 커스텀 파서 사용
            )
            logger.info(f"Created {len(documents)} document(s) from {filename}")
        except Exception as e:
            logger.error(f"Document creation failed for {filename}: {str(e)}")
            # Document 생성 실패는 치명적이지 않으므로 경고만 로깅
            # 파싱된 텍스트는 이미 있으므로 계속 진행

        # 7. 응답 데이터 구성
        pdf_metadata = PDFMetadata(
            author=parsed_result["metadata"].get("author"),
            created_date=parsed_result["metadata"].get("created_date"),
            modified_date=parsed_result["metadata"].get("modified_date"),
            title=parsed_result["metadata"].get("title"),
            subject=parsed_result["metadata"].get("subject"),
            page_count=parsed_result["metadata"]["page_count"],
            has_tables=parsed_result["metadata"].get("has_tables", False),
            language=parsed_result["metadata"]["language"],
            parser_used=parsed_result["parser_used"],
            file_size_bytes=file_size_bytes,
            extraction_time_ms=parsed_result["metadata"]["extraction_time_ms"],
        )

        response_data = UploadResponseData(
            file_id=file_id,
            filename=filename,
            file_type=file_type,
            text_content=parsed_result["text_content"],
            cleaned_text=parsed_result["cleaned_text"],
            word_count=parsed_result["word_count"],
            char_count=parsed_result["char_count"],
            metadata=pdf_metadata,
        )

        logger.info(f"Upload processed successfully: {filename} (ID: {file_id})")
        return response_data

    except UploadServiceError:
        # 이미 정의된 예외는 그대로 전파
        raise

    except Exception as e:
        # 예상하지 못한 예외
        logger.error(f"Unexpected error during upload processing: {str(e)}", exc_info=True)
        raise UploadServiceError(
            code=ErrorCodeEnum.INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred during file processing",
            details={"error": str(e)},
        )

    finally:
        # 8. 임시 파일 정리
        if temp_path:
            cleanup_temp_file(temp_path)


# ============================================================================
# Supabase Storage 연동 준비 (Phase 3)
# ============================================================================


async def upload_to_supabase_storage(
    file_path: Path,
    bucket_name: str,
    destination_path: str,
) -> str:
    """
    Supabase Storage에 파일 업로드 (Phase 3에서 구현)

    Args:
        file_path: 업로드할 파일 경로
        bucket_name: Supabase 버킷 이름
        destination_path: 저장될 경로

    Returns:
        파일 URL
    """
    # Phase 3에서 Supabase 클라이언트와 연동하여 구현
    raise NotImplementedError("Supabase Storage upload will be implemented in Phase 3")


async def delete_from_supabase_storage(
    bucket_name: str,
    file_path: str,
) -> None:
    """
    Supabase Storage에서 파일 삭제 (Phase 3에서 구현)

    Args:
        bucket_name: Supabase 버킷 이름
        file_path: 삭제할 파일 경로
    """
    # Phase 3에서 Supabase 클라이언트와 연동하여 구현
    raise NotImplementedError("Supabase Storage deletion will be implemented in Phase 3")


# ============================================================================
# 유틸리티 함수
# ============================================================================


def get_upload_statistics(response_data: UploadResponseData) -> Dict[str, Any]:
    """
    업로드 통계 정보 추출 (로깅, 모니터링용)

    Args:
        response_data: 업로드 응답 데이터

    Returns:
        통계 정보 dict
    """
    return {
        "file_id": str(response_data.file_id),
        "filename": response_data.filename,
        "file_type": response_data.file_type,
        "file_size_bytes": response_data.metadata.file_size_bytes,
        "page_count": response_data.metadata.page_count,
        "word_count": response_data.word_count,
        "language": response_data.metadata.language,
        "parser_used": response_data.metadata.parser_used,
        "extraction_time_ms": response_data.metadata.extraction_time_ms,
        "has_tables": response_data.metadata.has_tables,
    }

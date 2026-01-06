"""
Document Loader for RAG Pipeline
PDF 파싱 결과를 LangChain Document 객체로 변환
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from uuid import UUID

from langchain.schema import Document

from app.utils.pdf_parser import parse_pdf
from app.models.schemas import FileTypeEnum, ParserTypeEnum


# ============================================================================
# Document 변환 함수
# ============================================================================


def create_document_from_parsed_result(
    parsed_result: Dict[str, Any],
    file_id: UUID,
    filename: str,
    file_type: FileTypeEnum,
) -> Document:
    """
    PDF 파싱 결과를 LangChain Document 객체로 변환

    Args:
        parsed_result: parse_pdf()의 반환값
        file_id: 파일 고유 ID
        filename: 원본 파일명
        file_type: 파일 용도

    Returns:
        LangChain Document 객체
    """
    # cleaned_text를 Document의 page_content로 사용
    page_content = parsed_result["cleaned_text"]

    # 메타데이터 구성
    metadata = {
        # 파일 식별 정보
        "file_id": str(file_id),
        "filename": filename,
        "file_type": file_type.value,
        "source": filename,
        # PDF 메타데이터
        "page_count": parsed_result["metadata"].get("page_count", 0),
        "language": parsed_result["metadata"].get("language", "unknown"),
        "parser_used": parsed_result["parser_used"].value,
        # 문서 정보
        "author": parsed_result["metadata"].get("author"),
        "title": parsed_result["metadata"].get("title"),
        "subject": parsed_result["metadata"].get("subject"),
        "created_date": parsed_result["metadata"].get("created_date"),
        # 통계 정보
        "word_count": parsed_result["word_count"],
        "char_count": parsed_result["char_count"],
        "has_tables": parsed_result["metadata"].get("has_tables", False),
        # 처리 정보
        "extraction_time_ms": parsed_result["metadata"].get("extraction_time_ms", 0),
        "loaded_at": datetime.utcnow().isoformat(),
    }

    # None 값 제거 (LangChain Document는 None을 잘 처리하지만 깔끔하게)
    metadata = {k: v for k, v in metadata.items() if v is not None}

    return Document(page_content=page_content, metadata=metadata)


def create_documents_by_page(
    parsed_result: Dict[str, Any],
    file_id: UUID,
    filename: str,
    file_type: FileTypeEnum,
) -> List[Document]:
    """
    PDF 파싱 결과를 페이지별 LangChain Document 리스트로 변환
    (주의: pdf_parser.py는 페이지별 텍스트를 반환하지 않으므로, 이 함수는 PyPDFLoader 사용 시에만 유효)

    현재는 단일 Document 반환 (향후 확장 가능)

    Args:
        parsed_result: parse_pdf()의 반환값
        file_id: 파일 고유 ID
        filename: 원본 파일명
        file_type: 파일 용도

    Returns:
        LangChain Document 리스트
    """
    # 현재 구현: 전체 텍스트를 하나의 Document로
    # Phase 3에서 text_splitter로 청킹 수행 예정
    doc = create_document_from_parsed_result(parsed_result, file_id, filename, file_type)
    return [doc]


# ============================================================================
# LangChain PyPDFLoader 통합
# ============================================================================


def load_pdf_with_langchain(
    file_path: Path,
    file_id: UUID,
    file_type: FileTypeEnum,
) -> List[Document]:
    """
    LangChain의 PyPDFLoader를 직접 사용하여 PDF 로드
    (우리 커스텀 파서 대신 LangChain 네이티브 방식 사용 시)

    Args:
        file_path: PDF 파일 경로
        file_id: 파일 고유 ID
        file_type: 파일 용도

    Returns:
        LangChain Document 리스트 (페이지별)
    """
    # Lazy import to avoid Windows compatibility issues
    try:
        from langchain_community.document_loaders import PyPDFLoader
    except ImportError as e:
        raise ImportError(
            "langchain_community.document_loaders.PyPDFLoader is not available. "
            f"Error: {str(e)}"
        )

    loader = PyPDFLoader(str(file_path))
    documents = loader.load()

    # 우리 메타데이터 추가
    for i, doc in enumerate(documents):
        doc.metadata.update(
            {
                "file_id": str(file_id),
                "file_type": file_type.value,
                "page": i + 1,
                "total_pages": len(documents),
                "loaded_at": datetime.utcnow().isoformat(),
            }
        )

    return documents


# ============================================================================
# 통합 Document Loader
# ============================================================================


def load_document(
    file_path: Path,
    file_id: UUID,
    filename: str,
    file_type: FileTypeEnum,
    parser_type: ParserTypeEnum = ParserTypeEnum.AUTO,
    extract_tables: bool = False,
    use_langchain_loader: bool = False,
) -> tuple[List[Document], Dict[str, Any]]:
    """
    PDF를 로드하고 LangChain Document로 변환하는 통합 함수

    Args:
        file_path: PDF 파일 경로
        file_id: 파일 고유 ID
        filename: 원본 파일명
        file_type: 파일 용도
        parser_type: 파서 타입 (기본값: AUTO)
        extract_tables: 테이블 추출 여부
        use_langchain_loader: LangChain PyPDFLoader 직접 사용 여부

    Returns:
        (Document 리스트, 파싱 메타데이터)
    """
    if use_langchain_loader:
        # LangChain 네이티브 로더 사용
        documents = load_pdf_with_langchain(file_path, file_id, file_type)
        metadata = {
            "page_count": len(documents),
            "parser_used": "langchain_pypdf",
            "extraction_time_ms": 0,
        }
        return documents, metadata

    else:
        # 우리 커스텀 파서 사용
        parsed_result = parse_pdf(
            file_path=file_path,
            file_type=file_type,
            parser_type=parser_type,
            extract_tables=extract_tables,
        )

        # Document 객체 생성
        documents = create_documents_by_page(parsed_result, file_id, filename, file_type)

        # 메타데이터 반환 (응답 생성용)
        metadata = {
            "text_content": parsed_result["text_content"],
            "cleaned_text": parsed_result["cleaned_text"],
            "word_count": parsed_result["word_count"],
            "char_count": parsed_result["char_count"],
            "metadata": parsed_result["metadata"],
            "parser_used": parsed_result["parser_used"],
            "tables": parsed_result.get("tables"),
        }

        return documents, metadata


# ============================================================================
# Document 유틸리티
# ============================================================================


def enrich_document_metadata(
    document: Document,
    additional_metadata: Dict[str, Any],
) -> Document:
    """
    Document의 메타데이터를 추가 정보로 보강

    Args:
        document: LangChain Document
        additional_metadata: 추가할 메타데이터

    Returns:
        메타데이터가 보강된 Document
    """
    document.metadata.update(additional_metadata)
    return document


def get_document_summary(document: Document) -> Dict[str, Any]:
    """
    Document의 요약 정보 추출

    Args:
        document: LangChain Document

    Returns:
        요약 정보 dict
    """
    content_preview = document.page_content[:200] + "..." if len(document.page_content) > 200 else document.page_content

    return {
        "content_length": len(document.page_content),
        "content_preview": content_preview,
        "metadata_keys": list(document.metadata.keys()),
        "file_id": document.metadata.get("file_id"),
        "file_type": document.metadata.get("file_type"),
        "language": document.metadata.get("language"),
        "page_count": document.metadata.get("page_count"),
    }


def merge_documents(documents: List[Document], separator: str = "\n\n") -> Document:
    """
    여러 Document를 하나로 병합

    Args:
        documents: Document 리스트
        separator: 구분자

    Returns:
        병합된 단일 Document
    """
    if not documents:
        return Document(page_content="", metadata={})

    if len(documents) == 1:
        return documents[0]

    # 페이지 내용 병합
    merged_content = separator.join(doc.page_content for doc in documents)

    # 첫 번째 문서의 메타데이터 기반으로 병합
    merged_metadata = documents[0].metadata.copy()
    merged_metadata["merged_from_pages"] = len(documents)
    merged_metadata["original_page_count"] = documents[0].metadata.get("page_count", len(documents))

    return Document(page_content=merged_content, metadata=merged_metadata)


# ============================================================================
# Phase 3 준비: Vector Store 연동용 함수
# ============================================================================


def prepare_documents_for_embedding(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Document]:
    """
    Document를 임베딩하기 좋은 크기로 청킹
    (실제 청킹은 text_splitter.py에서 수행, 이 함수는 인터페이스만 제공)

    Args:
        documents: Document 리스트
        chunk_size: 청크 크기
        chunk_overlap: 청크 오버랩

    Returns:
        청킹된 Document 리스트
    """
    # Phase 3에서 text_splitter.py와 연계하여 구현 예정
    # 현재는 그대로 반환
    return documents


def add_embedding_metadata(
    documents: List[Document],
    embedding_model: str = "text-embedding-3-small",
    embedding_dimension: int = 1536,
) -> List[Document]:
    """
    임베딩 관련 메타데이터 추가

    Args:
        documents: Document 리스트
        embedding_model: 임베딩 모델명
        embedding_dimension: 임베딩 차원

    Returns:
        메타데이터가 추가된 Document 리스트
    """
    for doc in documents:
        doc.metadata.update(
            {
                "embedding_model": embedding_model,
                "embedding_dimension": embedding_dimension,
                "ready_for_embedding": True,
            }
        )
    return documents

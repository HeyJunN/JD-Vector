"""
Vector Store Module for RAG Pipeline
Supabase pgvector를 사용한 벡터 저장 및 검색

주요 기능:
- 문서 메타데이터 저장 (documents 테이블)
- 청크 및 임베딩 저장 (document_chunks 테이블)
- 문서 조회 및 삭제
- tenacity 기반 재시도 로직
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime

from supabase import create_client, Client
from langchain.schema import Document
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from app.core.config import settings
from app.models.schemas import FileTypeEnum

# 로거 설정
logger = logging.getLogger(__name__)


# ============================================================================
# 재시도 설정
# ============================================================================

# 재시도 대상 예외들
RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    OSError,
)

# 재시도 데코레이터 (3회 시도, 지수 백오프)
def create_retry_decorator(max_attempts: int = 3):
    """재시도 데코레이터 생성"""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception),  # 모든 예외에 대해 재시도
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )


# ============================================================================
# Supabase 클라이언트
# ============================================================================


class SupabaseClientManager:
    """Supabase 클라이언트 관리자 - 연결 문제 시 재생성 지원"""

    def __init__(self):
        self._client: Optional[Client] = None

    def get_client(self, force_new: bool = False) -> Client:
        """
        Supabase 클라이언트 가져오기

        Args:
            force_new: True면 새 클라이언트 강제 생성
        """
        if self._client is None or force_new:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

            logger.debug("Creating new Supabase client")
            self._client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY,
            )

        return self._client

    def reset_client(self):
        """클라이언트 리셋 (연결 문제 시)"""
        self._client = None
        logger.info("Supabase client reset")


# 글로벌 클라이언트 매니저
_client_manager = SupabaseClientManager()


def get_supabase(force_new: bool = False) -> Client:
    """Supabase 클라이언트 가져오기"""
    return _client_manager.get_client(force_new)


def reset_supabase_client():
    """클라이언트 리셋"""
    _client_manager.reset_client()


# ============================================================================
# 데이터 모델
# ============================================================================


@dataclass
class DocumentRecord:
    """documents 테이블 레코드"""

    file_id: UUID
    filename: str
    file_type: str
    raw_text: Optional[str] = None
    cleaned_text: Optional[str] = None
    word_count: int = 0
    char_count: int = 0
    page_count: int = 0
    chunk_count: int = 0
    language: str = "unknown"
    author: Optional[str] = None
    title: Optional[str] = None
    embedding_status: str = "pending"
    content_hash: Optional[str] = None  # 중복 방지용 해시

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "file_id": str(self.file_id),
            "filename": self.filename,
            "file_type": self.file_type,
            "raw_text": self.raw_text,
            "cleaned_text": self.cleaned_text,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "page_count": self.page_count,
            "chunk_count": self.chunk_count,
            "language": self.language,
            "author": self.author,
            "title": self.title,
            "embedding_status": self.embedding_status,
            "content_hash": self.content_hash,
        }

    def to_dict_minimal(self) -> Dict[str, Any]:
        """최소 데이터만 포함 (텍스트 제외)"""
        return {
            "file_id": str(self.file_id),
            "filename": self.filename,
            "file_type": self.file_type,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "page_count": self.page_count,
            "chunk_count": self.chunk_count,
            "language": self.language,
            "author": self.author,
            "title": self.title,
            "embedding_status": self.embedding_status,
        }


@dataclass
class ChunkRecord:
    """document_chunks 테이블 레코드"""

    document_id: UUID
    file_id: UUID
    chunk_index: int
    content: str
    section_type: Optional[str] = None
    char_count: int = 0
    token_count: int = 0
    embedding: Optional[List[float]] = None
    embedding_model: str = "text-embedding-3-small"

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = {
            "document_id": str(self.document_id),
            "file_id": str(self.file_id),
            "chunk_index": self.chunk_index,
            "content": self.content,
            "section_type": self.section_type,
            "char_count": self.char_count,
            "token_count": self.token_count,
            "embedding_model": self.embedding_model,
        }
        # 임베딩이 있으면 추가
        if self.embedding:
            data["embedding"] = self.embedding
        return data


# ============================================================================
# Vector Store 클래스
# ============================================================================


class VectorStore:
    """Supabase pgvector 기반 벡터 저장소 (재시도 로직 포함)"""

    # 배치 크기 (작게 설정하여 안정성 확보)
    DEFAULT_BATCH_SIZE = 20

    def __init__(self, client: Optional[Client] = None):
        self._external_client = client
        self._retry_count = 0
        self._max_retries = 3

    @property
    def client(self) -> Client:
        """클라이언트 가져오기 (연결 실패 시 재생성)"""
        if self._external_client:
            return self._external_client
        return get_supabase()

    def _get_fresh_client(self) -> Client:
        """새 클라이언트 강제 생성"""
        if self._external_client:
            return self._external_client
        return get_supabase(force_new=True)

    def _execute_with_retry(self, operation_name: str, operation_func):
        """
        재시도 로직이 포함된 실행 래퍼

        Args:
            operation_name: 작업 이름 (로깅용)
            operation_func: 실행할 함수 (client를 인자로 받음)
        """
        last_error = None

        for attempt in range(1, self._max_retries + 1):
            try:
                # 첫 시도는 기존 클라이언트, 재시도는 새 클라이언트
                client = self.client if attempt == 1 else self._get_fresh_client()
                return operation_func(client)

            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # 연결 관련 에러인지 확인
                is_connection_error = any(
                    keyword in error_str
                    for keyword in ["disconnect", "connection", "timeout", "closed", "reset"]
                )

                if is_connection_error and attempt < self._max_retries:
                    logger.warning(
                        f"[{operation_name}] Attempt {attempt}/{self._max_retries} failed: {e}. Retrying..."
                    )
                    reset_supabase_client()
                    import time
                    time.sleep(1 * attempt)  # 지수 백오프
                else:
                    logger.error(f"[{operation_name}] Failed after {attempt} attempts: {e}")
                    raise

        raise last_error

    # ------------------------------------------------------------------------
    # 문서 저장
    # ------------------------------------------------------------------------

    def save_document(self, record: DocumentRecord) -> Dict[str, Any]:
        """
        문서 메타데이터 저장 (재시도 포함)

        Args:
            record: DocumentRecord 객체

        Returns:
            저장된 레코드
        """
        def _save(client: Client):
            result = (
                client.table("documents")
                .insert(record.to_dict())
                .execute()
            )

            if result.data:
                logger.info(f"Document saved: {record.file_id}")
                return result.data[0]
            else:
                raise Exception("Failed to save document: no data returned")

        return self._execute_with_retry(f"save_document({record.file_id})", _save)

    def save_chunks(
        self,
        chunks: List[ChunkRecord],
        batch_size: Optional[int] = None,
    ) -> int:
        """
        청크 배치 저장 (재시도 포함)

        Args:
            chunks: ChunkRecord 리스트
            batch_size: 배치 크기 (기본값: 20)

        Returns:
            저장된 청크 수
        """
        if not chunks:
            return 0

        batch_size = batch_size or self.DEFAULT_BATCH_SIZE
        saved_count = 0
        total_batches = (len(chunks) + batch_size - 1) // batch_size

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_data = [chunk.to_dict() for chunk in batch]
            batch_num = i // batch_size + 1

            def _save_batch(client: Client, data=batch_data):
                result = (
                    client.table("document_chunks")
                    .insert(data)
                    .execute()
                )
                return result

            try:
                result = self._execute_with_retry(
                    f"save_chunks(batch {batch_num}/{total_batches})",
                    _save_batch
                )

                if result.data:
                    saved_count += len(result.data)
                    logger.info(
                        f"Saved chunk batch {batch_num}/{total_batches}: "
                        f"{len(result.data)} chunks"
                    )

            except Exception as e:
                logger.error(f"Failed to save chunk batch {batch_num}: {e}")
                raise

        return saved_count

    def save_document_with_chunks(
        self,
        document: DocumentRecord,
        chunks: List[ChunkRecord],
    ) -> Dict[str, Any]:
        """
        문서와 청크를 함께 저장

        Args:
            document: 문서 레코드
            chunks: 청크 레코드 리스트

        Returns:
            저장 결과 요약
        """
        # 1. 문서 저장
        doc_result = self.save_document(document)
        document_id = UUID(doc_result["id"])

        # 2. 청크에 document_id 설정
        for chunk in chunks:
            chunk.document_id = document_id

        # 3. 청크 저장
        chunk_count = self.save_chunks(chunks)

        # 4. 문서의 chunk_count 및 status 업데이트 (최소 페이로드)
        self.update_document_status(
            document.file_id,
            chunk_count=chunk_count,
            embedding_status="completed" if chunk_count > 0 else "pending",
        )

        return {
            "document_id": str(document_id),
            "file_id": str(document.file_id),
            "chunk_count": chunk_count,
        }

    # ------------------------------------------------------------------------
    # 문서 조회
    # ------------------------------------------------------------------------

    def get_document_by_id(self, doc_id: UUID) -> Optional[Dict[str, Any]]:
        """id(PK)로 문서 조회"""
        def _get(client: Client):
            result = (
                client.table("documents")
                .select("id, file_id, filename, file_type, embedding_status, chunk_count, word_count, char_count, page_count, language, created_at, updated_at")
                .eq("id", str(doc_id))
                .execute()
            )

            if result.data:
                return result.data[0]
            return None

        return self._execute_with_retry(f"get_document_by_id({doc_id})", _get)

    def get_document_by_file_id(self, file_id: UUID) -> Optional[Dict[str, Any]]:
        """file_id로 문서 조회 (업로드 시 생성된 ID)"""
        def _get(client: Client):
            result = (
                client.table("documents")
                .select("id, file_id, filename, file_type, embedding_status, chunk_count, word_count, char_count, page_count, language, created_at, updated_at")
                .eq("file_id", str(file_id))
                .execute()
            )

            if result.data:
                return result.data[0]
            return None

        return self._execute_with_retry(f"get_document_by_file_id({file_id})", _get)

    def get_document_by_content_hash(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """content_hash로 문서 조회 (중복 방지용)"""
        def _get(client: Client):
            result = (
                client.table("documents")
                .select("id, file_id, filename, file_type, embedding_status, chunk_count, word_count, char_count, page_count, language, content_hash, created_at")
                .eq("content_hash", content_hash)
                .execute()
            )

            if result.data:
                return result.data[0]
            return None

        return self._execute_with_retry(f"get_document_by_content_hash({content_hash[:16]}...)", _get)

    def get_chunks_by_document_id(
        self,
        doc_id: UUID,
        include_embedding: bool = False,
    ) -> List[Dict[str, Any]]:
        """document_id(PK)로 청크 조회"""
        def _get(client: Client):
            columns = (
                "*" if include_embedding
                else "id, document_id, file_id, chunk_index, content, section_type, char_count, token_count, created_at"
            )

            result = (
                client.table("document_chunks")
                .select(columns)
                .eq("document_id", str(doc_id))
                .order("chunk_index")
                .execute()
            )

            return result.data or []

        return self._execute_with_retry(f"get_chunks_by_document_id({doc_id})", _get)

    def get_chunks_by_file_id(
        self,
        file_id: UUID,
        include_embedding: bool = False,
    ) -> List[Dict[str, Any]]:
        """file_id로 청크 조회"""
        def _get(client: Client):
            columns = (
                "*" if include_embedding
                else "id, document_id, file_id, chunk_index, content, section_type, char_count, token_count, created_at"
            )

            result = (
                client.table("document_chunks")
                .select(columns)
                .eq("file_id", str(file_id))
                .order("chunk_index")
                .execute()
            )

            return result.data or []

        return self._execute_with_retry(f"get_chunks({file_id})", _get)

    def get_documents_by_type(
        self,
        file_type: FileTypeEnum,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """파일 타입으로 문서 목록 조회"""
        def _get(client: Client):
            query = (
                client.table("documents")
                .select("id, file_id, filename, file_type, embedding_status, chunk_count, created_at")
                .eq("file_type", file_type.value)
            )

            if status:
                query = query.eq("embedding_status", status)

            result = query.order("created_at", desc=True).execute()
            return result.data or []

        return self._execute_with_retry(f"get_documents_by_type({file_type.value})", _get)

    # ------------------------------------------------------------------------
    # 문서 업데이트 (최적화: status와 updated_at만)
    # ------------------------------------------------------------------------

    def update_document_status(
        self,
        file_id: UUID,
        embedding_status: Optional[str] = None,
        chunk_count: Optional[int] = None,
    ) -> bool:
        """
        문서 상태 업데이트 (최소 페이로드 - raw_text 미포함)

        Args:
            file_id: 파일 ID
            embedding_status: 임베딩 상태
            chunk_count: 청크 수

        Returns:
            성공 여부
        """
        def _update(client: Client):
            # 최소한의 데이터만 업데이트
            update_data: Dict[str, Any] = {}

            if embedding_status is not None:
                update_data["embedding_status"] = embedding_status
            if chunk_count is not None:
                update_data["chunk_count"] = chunk_count

            # 업데이트할 데이터가 없으면 스킵
            if not update_data:
                return True

            result = (
                client.table("documents")
                .update(update_data)
                .eq("file_id", str(file_id))
                .execute()
            )

            return bool(result.data)

        return self._execute_with_retry(f"update_status({file_id})", _update)

    # ------------------------------------------------------------------------
    # 문서 삭제
    # ------------------------------------------------------------------------

    def delete_document(self, file_id: UUID) -> bool:
        """
        문서 및 관련 청크 삭제

        Args:
            file_id: 파일 ID

        Returns:
            삭제 성공 여부
        """
        def _delete(client: Client):
            # RPC 함수 사용 (CASCADE로 청크도 삭제됨)
            result = client.rpc(
                "delete_document_by_file_id",
                {"target_file_id": str(file_id)},
            ).execute()

            deleted = result.data if result.data else False
            if deleted:
                logger.info(f"Document deleted: {file_id}")
            return deleted

        return self._execute_with_retry(f"delete_document({file_id})", _delete)

    # ------------------------------------------------------------------------
    # 통계 조회
    # ------------------------------------------------------------------------

    def get_document_stats(self, file_id: UUID) -> Optional[Dict[str, Any]]:
        """문서 통계 조회 (file_id 기준)"""
        def _get(client: Client):
            logger.debug(f"Looking up document with file_id: {file_id}")

            # documents 테이블에서 직접 조회
            doc_result = (
                client.table("documents")
                .select("id, file_id, filename, file_type, embedding_status, chunk_count, created_at")
                .eq("file_id", str(file_id))
                .execute()
            )

            if not doc_result.data:
                logger.warning(f"No document found in documents table for file_id: {file_id}")
                return None

            doc = doc_result.data[0]

            # 청크 수 계산 (더 정확한 값)
            chunk_result = (
                client.table("document_chunks")
                .select("id", count="exact")
                .eq("file_id", str(file_id))
                .execute()
            )

            chunk_count = chunk_result.count if chunk_result.count else 0

            return {
                "id": doc["id"],
                "file_id": doc["file_id"],
                "filename": doc["filename"],
                "file_type": doc["file_type"],
                "embedding_status": doc["embedding_status"],
                "chunk_count": chunk_count,
                "created_at": doc["created_at"],
            }

        return self._execute_with_retry(f"get_stats({file_id})", _get)

    def get_all_documents_summary(self) -> Dict[str, Any]:
        """전체 문서 요약"""
        def _get(client: Client):
            # 최소 컬럼만 조회
            docs_result = (
                client.table("documents")
                .select("id, file_type, embedding_status")
                .execute()
            )

            docs = docs_result.data or []

            summary = {
                "total_documents": len(docs),
                "by_type": {
                    "resume": 0,
                    "job_description": 0,
                },
                "by_status": {
                    "pending": 0,
                    "processing": 0,
                    "completed": 0,
                    "failed": 0,
                },
            }

            for doc in docs:
                file_type = doc.get("file_type", "unknown")
                status = doc.get("embedding_status", "unknown")

                if file_type in summary["by_type"]:
                    summary["by_type"][file_type] += 1
                if status in summary["by_status"]:
                    summary["by_status"][status] += 1

            return summary

        return self._execute_with_retry("get_summary", _get)


# ============================================================================
# 헬퍼 함수
# ============================================================================


def create_document_record(
    file_id: UUID,
    filename: str,
    file_type: FileTypeEnum,
    raw_text: str,
    cleaned_text: str,
    metadata: Dict[str, Any],
) -> DocumentRecord:
    """업로드 결과에서 DocumentRecord 생성"""
    return DocumentRecord(
        file_id=file_id,
        filename=filename,
        file_type=file_type.value,
        raw_text=raw_text,
        cleaned_text=cleaned_text,
        word_count=metadata.get("word_count", 0),
        char_count=metadata.get("char_count", 0),
        page_count=metadata.get("page_count", 0),
        language=metadata.get("language", "unknown"),
        author=metadata.get("author"),
        title=metadata.get("title"),
        embedding_status="pending",
    )


def create_chunk_records(
    file_id: UUID,
    chunks_with_embeddings: List[Dict[str, Any]],
) -> List[ChunkRecord]:
    """
    청킹 및 임베딩 결과에서 ChunkRecord 리스트 생성

    Args:
        file_id: 파일 ID
        chunks_with_embeddings: embed_documents()의 결과

    Returns:
        ChunkRecord 리스트
    """
    records = []

    for i, item in enumerate(chunks_with_embeddings):
        doc = item["document"]
        embedding = item["embedding"]

        record = ChunkRecord(
            document_id=UUID("00000000-0000-0000-0000-000000000000"),  # 나중에 설정됨
            file_id=file_id,
            chunk_index=doc.metadata.get("chunk_index", i),
            content=doc.page_content,
            section_type=doc.metadata.get("section_type"),
            char_count=len(doc.page_content),
            token_count=doc.metadata.get("estimated_tokens", 0),
            embedding=embedding,
        )
        records.append(record)

    return records


# ============================================================================
# 싱글톤 인스턴스
# ============================================================================

_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """VectorStore 싱글톤"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def reset_vector_store():
    """VectorStore 리셋 (테스트용)"""
    global _vector_store
    _vector_store = None
    reset_supabase_client()

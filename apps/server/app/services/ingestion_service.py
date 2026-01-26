"""
Ingestion Service - 문서 벡터화 파이프라인
업로드된 문서를 청킹, 임베딩, 저장하는 전체 플로우 관리

파이프라인:
1. 문서 텍스트 → LangChain Document 변환
2. Document → 섹션 기반 청킹
3. 청크 → OpenAI 임베딩 생성
4. 임베딩 → Supabase pgvector 저장
"""

import logging
import hashlib
from typing import Dict, Any, Optional, List
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime

from langchain.schema import Document

from app.models.schemas import FileTypeEnum, UploadResponseData
from app.core.rag.text_splitter import (
    chunk_document,
    add_token_counts,
    get_chunk_summary,
    ChunkConfig,
)
from app.core.rag.embeddings import (
    embed_documents,
    embed_documents_async,
    estimate_embedding_cost,
    EmbeddingClient,
    AsyncEmbeddingClient,
)
from app.core.rag.vector_store import (
    VectorStore,
    DocumentRecord,
    ChunkRecord,
    get_vector_store,
    create_document_record,
    create_chunk_records,
)

# 로거 설정
logger = logging.getLogger(__name__)


# ============================================================================
# 결과 데이터 클래스
# ============================================================================


@dataclass
class IngestionResult:
    """Ingestion 결과"""

    success: bool
    file_id: UUID
    document_id: Optional[str] = None
    chunk_count: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    processing_time_ms: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "file_id": str(self.file_id),
            "document_id": self.document_id,
            "chunk_count": self.chunk_count,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": self.estimated_cost_usd,
            "processing_time_ms": self.processing_time_ms,
            "error": self.error,
        }


# ============================================================================
# Ingestion Service
# ============================================================================


class IngestionService:
    """문서 벡터화 파이프라인 서비스"""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_client: Optional[EmbeddingClient] = None,
    ):
        self.vector_store = vector_store or get_vector_store()
        self.embedding_client = embedding_client or EmbeddingClient()

    def ingest_document(
        self,
        upload_result: UploadResponseData,
        chunk_config: Optional[ChunkConfig] = None,
        skip_if_exists: bool = True,
    ) -> IngestionResult:
        """
        업로드된 문서를 벡터화하여 저장

        Args:
            upload_result: 업로드 서비스의 응답 데이터
            chunk_config: 청킹 설정 (None이면 기본값)
            skip_if_exists: 이미 존재하면 스킵

        Returns:
            IngestionResult
        """
        import time
        start_time = time.time()

        file_id = upload_result.file_id
        file_type = FileTypeEnum(upload_result.file_type)

        print(f"[INGEST] Starting ingestion for file_id: {file_id}, file_type: {file_type}")

        try:
            # 1. 파일 내용 해시 계산 (중복 방지용)
            print(f"[INGEST] Calculating content hash for file_id: {file_id}")
            print(f"[INGEST] Text length: {len(upload_result.cleaned_text)} characters")
            content_hash = hashlib.sha256(
                upload_result.cleaned_text.encode('utf-8')
            ).hexdigest()
            print(f"[INGEST] Content hash calculated: {content_hash[:16]}...")
            logger.info(f"Content hash for {file_id}: {content_hash[:16]}...")

            # 2. 같은 내용의 문서가 이미 벡터화되었는지 확인 (토큰 절약)
            if skip_if_exists:
                print(f"[INGEST] Checking if document already exists for file_id: {file_id}")
                # 먼저 같은 file_id 확인
                existing = self.vector_store.get_document_by_file_id(file_id)
                if existing and existing.get("embedding_status") == "completed":
                    print(f"[INGEST] Document already ingested (same file_id): {file_id}")
                    logger.info(f"Document already ingested (same file_id): {file_id}")
                    return IngestionResult(
                        success=True,
                        file_id=file_id,
                        document_id=existing["id"],
                        chunk_count=existing.get("chunk_count", 0),
                        error="Already exists (skipped)",
                    )
                print(f"[INGEST] No existing document found for file_id: {file_id}, proceeding with ingestion")

                # 같은 내용의 다른 파일이 있는지 확인 (content_hash 기준)
                # TEMPORARY FIX: content_hash 중복 체크 비활성화 (file_id 불일치 문제 해결)
                print(f"[INGEST] Skipping content_hash duplicate check (disabled)")
                # print(f"[INGEST] Checking content_hash: {content_hash[:16]}...")
                # existing_by_hash = self.vector_store.get_document_by_content_hash(content_hash)
                # if existing_by_hash:
                #     print(f"[INGEST] Found existing document with same content_hash!")
                #     print(f"[INGEST] Existing: file_id={existing_by_hash.get('file_id')}, status={existing_by_hash.get('embedding_status')}")
                # if existing_by_hash and existing_by_hash.get("embedding_status") == "completed":
                #     print(
                #         f"[INGEST] Same content already vectorized! Skipping to save tokens. "
                #         f"Original file_id: {existing_by_hash.get('file_id')}, "
                #         f"New file_id: {file_id}"
                #     )
                #     logger.info(
                #         f"Same content already vectorized! Skipping to save tokens. "
                #         f"Original file_id: {existing_by_hash.get('file_id')}, "
                #         f"New file_id: {file_id}"
                #     )
                #     return IngestionResult(
                #         success=True,
                #         file_id=file_id,
                #         document_id=existing_by_hash["id"],
                #         chunk_count=existing_by_hash.get("chunk_count", 0),
                #         error=f"Same content already vectorized (skipped to save tokens)",
                #     )
                # print(f"[INGEST] No duplicate content found, proceeding with full ingestion")

            # 2. 문서 상태를 processing으로 업데이트 (또는 새로 저장)
            logger.info(f"Starting ingestion for: {file_id}")

            # 3. LangChain Document 생성
            document = Document(
                page_content=upload_result.cleaned_text,
                metadata={
                    "file_id": str(file_id),
                    "filename": upload_result.filename,
                    "file_type": file_type.value,
                    "word_count": upload_result.word_count,
                    "char_count": upload_result.char_count,
                    "page_count": upload_result.metadata.page_count,
                    "language": upload_result.metadata.language,
                },
            )

            # 4. 청킹
            print(f"[INGEST] Chunking document: {file_id}")
            logger.info(f"Chunking document: {file_id}")
            chunks = chunk_document(
                document=document,
                file_type=file_type,
                config=chunk_config,
                preserve_sections=True,
            )
            chunks = add_token_counts(chunks)

            chunk_summary = get_chunk_summary(chunks)
            print(f"[INGEST] Chunking complete: {chunk_summary['total_chunks']} chunks")
            logger.info(f"Chunking complete: {chunk_summary['total_chunks']} chunks")

            # 5. 비용 추정 및 로깅
            texts = [c.page_content for c in chunks]
            cost_estimate = estimate_embedding_cost(texts)
            print(f"[INGEST] Estimated embedding cost: ${cost_estimate['estimated_cost_usd']:.6f}")
            logger.info(f"Estimated embedding cost: ${cost_estimate['estimated_cost_usd']:.6f}")

            # 6. 임베딩 생성
            print(f"[INGEST] Generating embeddings for {len(chunks)} chunks")
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            embedded_chunks = embed_documents(chunks, self.embedding_client)
            print(f"[INGEST] Embeddings generated successfully")

            # 7. 레코드 생성
            doc_record = DocumentRecord(
                file_id=file_id,
                filename=upload_result.filename,
                file_type=file_type.value,
                raw_text=upload_result.text_content,
                cleaned_text=upload_result.cleaned_text,
                word_count=upload_result.word_count,
                char_count=upload_result.char_count,
                page_count=upload_result.metadata.page_count,
                chunk_count=len(chunks),
                language=upload_result.metadata.language,
                author=upload_result.metadata.author,
                title=upload_result.metadata.title,
                embedding_status="processing",
                content_hash=content_hash,  # 중복 방지용 해시
            )

            chunk_records = create_chunk_records(file_id, embedded_chunks)

            # 8. Supabase에 저장
            print(f"[INGEST] Saving to Supabase: {file_id}")
            logger.info(f"Saving to Supabase: {file_id}")
            save_result = self.vector_store.save_document_with_chunks(
                document=doc_record,
                chunks=chunk_records,
            )
            print(f"[INGEST] Save result: {save_result}")

            # 9. 결과 반환
            processing_time = (time.time() - start_time) * 1000

            result = IngestionResult(
                success=True,
                file_id=file_id,
                document_id=save_result["document_id"],
                chunk_count=save_result["chunk_count"],
                total_tokens=chunk_summary.get("estimated_tokens", 0),
                estimated_cost_usd=cost_estimate["estimated_cost_usd"],
                processing_time_ms=processing_time,
            )

            logger.info(f"Ingestion complete: {file_id} ({processing_time:.0f}ms)")
            return result

        except Exception as e:
            print(f"[INGEST] ERROR: Ingestion failed for {file_id}: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Ingestion failed for {file_id}: {e}", exc_info=True)

            # 상태를 failed로 업데이트
            try:
                self.vector_store.update_document_status(file_id, embedding_status="failed")
            except Exception:
                pass

            return IngestionResult(
                success=False,
                file_id=file_id,
                error=str(e),
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def ingest_from_text(
        self,
        file_id: UUID,
        filename: str,
        file_type: FileTypeEnum,
        text_content: str,
        cleaned_text: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_config: Optional[ChunkConfig] = None,
    ) -> IngestionResult:
        """
        텍스트에서 직접 벡터화 (업로드 결과 없이)

        Args:
            file_id: 파일 ID
            filename: 파일명
            file_type: 파일 타입
            text_content: 원본 텍스트
            cleaned_text: 정제된 텍스트
            metadata: 추가 메타데이터
            chunk_config: 청킹 설정

        Returns:
            IngestionResult
        """
        import time
        start_time = time.time()

        metadata = metadata or {}

        try:
            # 1. LangChain Document 생성
            document = Document(
                page_content=cleaned_text,
                metadata={
                    "file_id": str(file_id),
                    "filename": filename,
                    "file_type": file_type.value,
                    **metadata,
                },
            )

            # 2. 청킹
            chunks = chunk_document(
                document=document,
                file_type=file_type,
                config=chunk_config,
                preserve_sections=True,
            )
            chunks = add_token_counts(chunks)

            # 3. 임베딩
            texts = [c.page_content for c in chunks]
            cost_estimate = estimate_embedding_cost(texts)

            embedded_chunks = embed_documents(chunks, self.embedding_client)

            # 4. 레코드 생성
            doc_record = DocumentRecord(
                file_id=file_id,
                filename=filename,
                file_type=file_type.value,
                raw_text=text_content,
                cleaned_text=cleaned_text,
                word_count=len(cleaned_text.split()),
                char_count=len(cleaned_text),
                page_count=metadata.get("page_count", 1),
                chunk_count=len(chunks),
                language=metadata.get("language", "unknown"),
                embedding_status="processing",
            )

            chunk_records = create_chunk_records(file_id, embedded_chunks)

            # 5. 저장
            save_result = self.vector_store.save_document_with_chunks(
                document=doc_record,
                chunks=chunk_records,
            )

            processing_time = (time.time() - start_time) * 1000

            return IngestionResult(
                success=True,
                file_id=file_id,
                document_id=save_result["document_id"],
                chunk_count=save_result["chunk_count"],
                total_tokens=sum(c.metadata.get("estimated_tokens", 0) for c in chunks),
                estimated_cost_usd=cost_estimate["estimated_cost_usd"],
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Ingestion from text failed: {e}", exc_info=True)
            return IngestionResult(
                success=False,
                file_id=file_id,
                error=str(e),
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def delete_document(self, file_id: UUID) -> bool:
        """문서 및 벡터 삭제"""
        return self.vector_store.delete_document(file_id)

    def get_document_status(self, file_id: UUID) -> Optional[Dict[str, Any]]:
        """문서 상태 조회"""
        return self.vector_store.get_document_stats(file_id)


# ============================================================================
# 비동기 Ingestion Service
# ============================================================================


class AsyncIngestionService:
    """비동기 문서 벡터화 파이프라인"""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_client: Optional[AsyncEmbeddingClient] = None,
    ):
        self.vector_store = vector_store or get_vector_store()
        self.embedding_client = embedding_client or AsyncEmbeddingClient()

    async def ingest_document(
        self,
        upload_result: UploadResponseData,
        chunk_config: Optional[ChunkConfig] = None,
        skip_if_exists: bool = True,
    ) -> IngestionResult:
        """비동기 문서 벡터화"""
        import time
        start_time = time.time()

        file_id = upload_result.file_id
        file_type = FileTypeEnum(upload_result.file_type)

        try:
            # 이미 존재하는지 확인
            if skip_if_exists:
                existing = self.vector_store.get_document_by_file_id(file_id)
                if existing and existing.get("embedding_status") == "completed":
                    return IngestionResult(
                        success=True,
                        file_id=file_id,
                        document_id=existing["id"],
                        chunk_count=existing.get("chunk_count", 0),
                        error="Already exists (skipped)",
                    )

            # Document 생성
            document = Document(
                page_content=upload_result.cleaned_text,
                metadata={
                    "file_id": str(file_id),
                    "filename": upload_result.filename,
                    "file_type": file_type.value,
                },
            )

            # 청킹
            chunks = chunk_document(document, file_type, chunk_config, True)
            chunks = add_token_counts(chunks)

            # 비동기 임베딩
            embedded_chunks = await embed_documents_async(chunks, self.embedding_client)

            # 레코드 생성 및 저장
            doc_record = DocumentRecord(
                file_id=file_id,
                filename=upload_result.filename,
                file_type=file_type.value,
                raw_text=upload_result.text_content,
                cleaned_text=upload_result.cleaned_text,
                word_count=upload_result.word_count,
                char_count=upload_result.char_count,
                page_count=upload_result.metadata.page_count,
                chunk_count=len(chunks),
                language=upload_result.metadata.language,
                embedding_status="processing",
            )

            chunk_records = create_chunk_records(file_id, embedded_chunks)
            save_result = self.vector_store.save_document_with_chunks(doc_record, chunk_records)

            processing_time = (time.time() - start_time) * 1000

            return IngestionResult(
                success=True,
                file_id=file_id,
                document_id=save_result["document_id"],
                chunk_count=save_result["chunk_count"],
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Async ingestion failed: {e}", exc_info=True)
            return IngestionResult(
                success=False,
                file_id=file_id,
                error=str(e),
                processing_time_ms=(time.time() - start_time) * 1000,
            )


# ============================================================================
# 싱글톤 및 팩토리
# ============================================================================

_ingestion_service: Optional[IngestionService] = None
_async_ingestion_service: Optional[AsyncIngestionService] = None


def get_ingestion_service() -> IngestionService:
    """IngestionService 싱글톤"""
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service


def get_async_ingestion_service() -> AsyncIngestionService:
    """AsyncIngestionService 싱글톤"""
    global _async_ingestion_service
    if _async_ingestion_service is None:
        _async_ingestion_service = AsyncIngestionService()
    return _async_ingestion_service

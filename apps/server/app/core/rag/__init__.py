"""
RAG (Retrieval-Augmented Generation) Pipeline Module

Phase 3 구현:
- text_splitter: 문서 청킹
- embeddings: OpenAI 임베딩 생성
- vector_store: Supabase pgvector 연동
- retriever: 유사도 검색 및 매칭 분석
- document_loader: PDF → LangChain Document 변환
"""

from app.core.rag.text_splitter import (
    chunk_document,
    chunk_documents,
    add_token_counts,
    get_chunk_summary,
    ChunkConfig,
    SectionType,
)

from app.core.rag.embeddings import (
    EmbeddingClient,
    AsyncEmbeddingClient,
    embed_documents,
    embed_documents_async,
    estimate_embedding_cost,
    get_embedding_client,
    get_async_embedding_client,
)

from app.core.rag.vector_store import (
    VectorStore,
    DocumentRecord,
    ChunkRecord,
    get_vector_store,
    get_supabase,
    create_document_record,
    create_chunk_records,
)

from app.core.rag.retriever import (
    DocumentRetriever,
    MatchResult,
    ChunkMatch,
    SectionScore,
    get_retriever,
    analyze_skill_gaps,
)

from app.core.rag.document_loader import (
    load_document,
    create_document_from_parsed_result,
    merge_documents,
)

__all__ = [
    # Text Splitter
    "chunk_document",
    "chunk_documents",
    "add_token_counts",
    "get_chunk_summary",
    "ChunkConfig",
    "SectionType",
    # Embeddings
    "EmbeddingClient",
    "AsyncEmbeddingClient",
    "embed_documents",
    "embed_documents_async",
    "estimate_embedding_cost",
    "get_embedding_client",
    "get_async_embedding_client",
    # Vector Store
    "VectorStore",
    "DocumentRecord",
    "ChunkRecord",
    "get_vector_store",
    "get_supabase",
    "create_document_record",
    "create_chunk_records",
    # Retriever
    "DocumentRetriever",
    "MatchResult",
    "ChunkMatch",
    "SectionScore",
    "get_retriever",
    "analyze_skill_gaps",
    # Document Loader
    "load_document",
    "create_document_from_parsed_result",
    "merge_documents",
]

"""
Embeddings Module for RAG Pipeline
OpenAI text-embedding-3-small을 사용한 텍스트 벡터화

주요 기능:
- 단일/배치 텍스트 임베딩 생성
- 비용 최적화를 위한 배치 처리
- 에러 핸들링 및 재시도 로직
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from openai import OpenAI, AsyncOpenAI
from openai import RateLimitError, APIError, APIConnectionError
from langchain.schema import Document

from app.core.config import settings

# 로거 설정
logger = logging.getLogger(__name__)


# ============================================================================
# 상수 및 설정
# ============================================================================

# OpenAI 임베딩 모델 정보
EMBEDDING_MODELS = {
    "text-embedding-3-small": {
        "dimension": 1536,
        "max_tokens": 8191,
        "price_per_1m_tokens": 0.02,  # USD
    },
    "text-embedding-3-large": {
        "dimension": 3072,
        "max_tokens": 8191,
        "price_per_1m_tokens": 0.13,  # USD
    },
    "text-embedding-ada-002": {
        "dimension": 1536,
        "max_tokens": 8191,
        "price_per_1m_tokens": 0.10,  # USD
    },
}

# 기본 배치 크기 (OpenAI는 한 번에 최대 2048개까지 처리 가능)
DEFAULT_BATCH_SIZE = 100

# 재시도 설정
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1


# ============================================================================
# 임베딩 설정
# ============================================================================


@dataclass
class EmbeddingConfig:
    """임베딩 설정"""

    model: str = "text-embedding-3-small"
    dimension: int = 1536
    batch_size: int = DEFAULT_BATCH_SIZE
    max_retries: int = MAX_RETRIES
    retry_delay: float = RETRY_DELAY_SECONDS

    def __post_init__(self):
        # 모델 정보 검증
        if self.model in EMBEDDING_MODELS:
            model_info = EMBEDDING_MODELS[self.model]
            self.dimension = model_info["dimension"]


# ============================================================================
# 동기 임베딩 클라이언트
# ============================================================================


class EmbeddingClient:
    """OpenAI 임베딩 클라이언트 (동기)"""

    def __init__(self, config: Optional[EmbeddingConfig] = None):
        self.config = config or EmbeddingConfig(
            model=settings.EMBEDDING_MODEL,
            dimension=settings.EMBEDDING_DIMENSION,
        )
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        """OpenAI 클라이언트 (lazy initialization)"""
        if self._client is None:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is not set")
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    def embed_text(self, text: str) -> List[float]:
        """
        단일 텍스트를 임베딩 벡터로 변환

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터 (1536차원 리스트)
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        for attempt in range(self.config.max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.config.model,
                    input=text,
                )
                return response.data[0].embedding

            except RateLimitError as e:
                logger.warning(f"Rate limit hit, retrying ({attempt + 1}/{self.config.max_retries}): {e}")
                if attempt < self.config.max_retries - 1:
                    import time
                    time.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    raise

            except (APIError, APIConnectionError) as e:
                logger.error(f"API error during embedding: {e}")
                if attempt < self.config.max_retries - 1:
                    import time
                    time.sleep(self.config.retry_delay)
                else:
                    raise

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        여러 텍스트를 배치로 임베딩

        Args:
            texts: 임베딩할 텍스트 리스트

        Returns:
            임베딩 벡터 리스트
        """
        if not texts:
            return []

        # 빈 텍스트 필터링 및 인덱스 추적
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)

        if not valid_texts:
            return [[] for _ in texts]

        # 배치 처리
        all_embeddings: List[List[float]] = []

        for batch_start in range(0, len(valid_texts), self.config.batch_size):
            batch_end = min(batch_start + self.config.batch_size, len(valid_texts))
            batch = valid_texts[batch_start:batch_end]

            batch_embeddings = self._embed_batch(batch)
            all_embeddings.extend(batch_embeddings)

            logger.info(f"Embedded batch {batch_start // self.config.batch_size + 1}: {len(batch)} texts")

        # 결과를 원래 순서대로 재배열
        result = [[] for _ in texts]
        for i, embedding in zip(valid_indices, all_embeddings):
            result[i] = embedding

        return result

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """배치 임베딩 (내부 함수)"""
        for attempt in range(self.config.max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.config.model,
                    input=texts,
                )
                # 응답 순서 보장
                embeddings = [None] * len(texts)
                for item in response.data:
                    embeddings[item.index] = item.embedding
                return embeddings

            except RateLimitError as e:
                logger.warning(f"Rate limit hit on batch, retrying ({attempt + 1}/{self.config.max_retries})")
                if attempt < self.config.max_retries - 1:
                    import time
                    time.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    raise

            except (APIError, APIConnectionError) as e:
                logger.error(f"API error during batch embedding: {e}")
                if attempt < self.config.max_retries - 1:
                    import time
                    time.sleep(self.config.retry_delay)
                else:
                    raise


# ============================================================================
# 비동기 임베딩 클라이언트
# ============================================================================


class AsyncEmbeddingClient:
    """OpenAI 임베딩 클라이언트 (비동기)"""

    def __init__(self, config: Optional[EmbeddingConfig] = None):
        self.config = config or EmbeddingConfig(
            model=settings.EMBEDDING_MODEL,
            dimension=settings.EMBEDDING_DIMENSION,
        )
        self._client: Optional[AsyncOpenAI] = None

    @property
    def client(self) -> AsyncOpenAI:
        """AsyncOpenAI 클라이언트 (lazy initialization)"""
        if self._client is None:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is not set")
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    async def embed_text(self, text: str) -> List[float]:
        """단일 텍스트 비동기 임베딩"""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        for attempt in range(self.config.max_retries):
            try:
                response = await self.client.embeddings.create(
                    model=self.config.model,
                    input=text,
                )
                return response.data[0].embedding

            except RateLimitError as e:
                logger.warning(f"Rate limit hit, retrying ({attempt + 1}/{self.config.max_retries})")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    raise

            except (APIError, APIConnectionError) as e:
                logger.error(f"API error during async embedding: {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay)
                else:
                    raise

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """여러 텍스트 비동기 배치 임베딩"""
        if not texts:
            return []

        # 빈 텍스트 필터링
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)

        if not valid_texts:
            return [[] for _ in texts]

        # 배치 처리
        all_embeddings: List[List[float]] = []

        for batch_start in range(0, len(valid_texts), self.config.batch_size):
            batch_end = min(batch_start + self.config.batch_size, len(valid_texts))
            batch = valid_texts[batch_start:batch_end]

            batch_embeddings = await self._embed_batch_async(batch)
            all_embeddings.extend(batch_embeddings)

            logger.info(f"Embedded batch {batch_start // self.config.batch_size + 1}: {len(batch)} texts")

        # 결과 재배열
        result = [[] for _ in texts]
        for i, embedding in zip(valid_indices, all_embeddings):
            result[i] = embedding

        return result

    async def _embed_batch_async(self, texts: List[str]) -> List[List[float]]:
        """비동기 배치 임베딩 (내부 함수)"""
        for attempt in range(self.config.max_retries):
            try:
                response = await self.client.embeddings.create(
                    model=self.config.model,
                    input=texts,
                )
                embeddings = [None] * len(texts)
                for item in response.data:
                    embeddings[item.index] = item.embedding
                return embeddings

            except RateLimitError as e:
                logger.warning(f"Rate limit hit on async batch, retrying ({attempt + 1}/{self.config.max_retries})")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    raise

            except (APIError, APIConnectionError) as e:
                logger.error(f"API error during async batch embedding: {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay)
                else:
                    raise


# ============================================================================
# Document 임베딩 헬퍼 함수
# ============================================================================


def embed_documents(
    documents: List[Document],
    client: Optional[EmbeddingClient] = None,
) -> List[Dict[str, Any]]:
    """
    LangChain Document 리스트를 임베딩

    Args:
        documents: Document 리스트
        client: 임베딩 클라이언트 (None이면 새로 생성)

    Returns:
        임베딩 정보가 포함된 dict 리스트
        [{"document": Document, "embedding": List[float], "token_count": int}, ...]
    """
    if client is None:
        client = EmbeddingClient()

    # 텍스트 추출
    texts = [doc.page_content for doc in documents]

    # 배치 임베딩
    embeddings = client.embed_texts(texts)

    # 결과 구성
    results = []
    for doc, embedding in zip(documents, embeddings):
        results.append({
            "document": doc,
            "embedding": embedding,
            "content": doc.page_content,
            "metadata": doc.metadata,
            "char_count": len(doc.page_content),
        })

    return results


async def embed_documents_async(
    documents: List[Document],
    client: Optional[AsyncEmbeddingClient] = None,
) -> List[Dict[str, Any]]:
    """Document 리스트 비동기 임베딩"""
    if client is None:
        client = AsyncEmbeddingClient()

    texts = [doc.page_content for doc in documents]
    embeddings = await client.embed_texts(texts)

    results = []
    for doc, embedding in zip(documents, embeddings):
        results.append({
            "document": doc,
            "embedding": embedding,
            "content": doc.page_content,
            "metadata": doc.metadata,
            "char_count": len(doc.page_content),
        })

    return results


# ============================================================================
# 비용 추정 유틸리티
# ============================================================================


def estimate_embedding_cost(
    texts: List[str],
    model: str = "text-embedding-3-small",
) -> Dict[str, Any]:
    """
    임베딩 비용 추정

    Args:
        texts: 임베딩할 텍스트 리스트
        model: 사용할 모델

    Returns:
        비용 추정 정보
    """
    if model not in EMBEDDING_MODELS:
        model = "text-embedding-3-small"

    model_info = EMBEDDING_MODELS[model]

    # 대략적인 토큰 수 추정 (4글자 = 1토큰 가정)
    total_chars = sum(len(text) for text in texts)
    estimated_tokens = total_chars // 4

    # 비용 계산
    cost_per_token = model_info["price_per_1m_tokens"] / 1_000_000
    estimated_cost = estimated_tokens * cost_per_token

    return {
        "model": model,
        "text_count": len(texts),
        "total_characters": total_chars,
        "estimated_tokens": estimated_tokens,
        "estimated_cost_usd": round(estimated_cost, 6),
        "price_per_1m_tokens": model_info["price_per_1m_tokens"],
    }


# ============================================================================
# 싱글톤 클라이언트 (편의용)
# ============================================================================

_embedding_client: Optional[EmbeddingClient] = None
_async_embedding_client: Optional[AsyncEmbeddingClient] = None


def get_embedding_client() -> EmbeddingClient:
    """동기 임베딩 클라이언트 싱글톤"""
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = EmbeddingClient()
    return _embedding_client


def get_async_embedding_client() -> AsyncEmbeddingClient:
    """비동기 임베딩 클라이언트 싱글톤"""
    global _async_embedding_client
    if _async_embedding_client is None:
        _async_embedding_client = AsyncEmbeddingClient()
    return _async_embedding_client

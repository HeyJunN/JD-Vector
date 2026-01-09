"""
Retriever Module for RAG Pipeline
이력서와 JD 간 유사도 검색 및 매칭 분석

주요 기능:
- Supabase RPC를 통한 벡터 유사도 검색
- 이력서-JD 매칭 점수 계산
- 섹션별 상세 분석
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from dataclasses import dataclass, field

from supabase import Client

from app.core.rag.vector_store import get_supabase
from app.core.rag.embeddings import EmbeddingClient, get_embedding_client

# 로거 설정
logger = logging.getLogger(__name__)


# ============================================================================
# 결과 데이터 클래스
# ============================================================================


@dataclass
class ChunkMatch:
    """청크 매칭 결과"""

    chunk_id: str
    chunk_index: int
    content: str
    section_type: Optional[str]
    similarity: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "section_type": self.section_type,
            "similarity": round(self.similarity, 4),
        }


@dataclass
class SectionScore:
    """섹션별 점수"""

    section_type: str
    score: float
    chunk_count: int
    matched_chunks: List[ChunkMatch] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_type": self.section_type,
            "score": round(self.score, 2),
            "chunk_count": self.chunk_count,
            "top_matches": [m.to_dict() for m in self.matched_chunks[:3]],
        }


@dataclass
class MatchResult:
    """전체 매칭 결과"""

    resume_file_id: UUID
    jd_file_id: UUID
    overall_similarity: float
    match_score: float  # 0-100 점수
    match_grade: str  # S, A, B, C, D
    section_scores: List[SectionScore] = field(default_factory=list)
    chunk_matches: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resume_file_id": str(self.resume_file_id),
            "jd_file_id": str(self.jd_file_id),
            "overall_similarity": round(self.overall_similarity, 4),
            "match_score": round(self.match_score, 1),
            "match_grade": self.match_grade,
            "section_scores": [s.to_dict() for s in self.section_scores],
            "chunk_match_count": len(self.chunk_matches),
        }


# ============================================================================
# Retriever 클래스
# ============================================================================


class DocumentRetriever:
    """문서 유사도 검색 및 매칭 분석"""

    def __init__(
        self,
        client: Optional[Client] = None,
        embedding_client: Optional[EmbeddingClient] = None,
    ):
        self.client = client or get_supabase()
        self.embedding_client = embedding_client or get_embedding_client()

    # ------------------------------------------------------------------------
    # 기본 검색
    # ------------------------------------------------------------------------

    def search_similar(
        self,
        query: str,
        match_count: int = 10,
        filter_file_type: Optional[str] = None,
        filter_file_id: Optional[UUID] = None,
        similarity_threshold: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        쿼리 텍스트와 유사한 청크 검색

        Args:
            query: 검색 쿼리 텍스트
            match_count: 반환할 결과 수
            filter_file_type: 파일 타입 필터
            filter_file_id: 특정 파일 ID 필터
            similarity_threshold: 최소 유사도 임계값

        Returns:
            유사한 청크 리스트
        """
        # 쿼리 임베딩 생성
        query_embedding = self.embedding_client.embed_text(query)

        # Supabase RPC 호출
        result = self.client.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_count": match_count,
                "filter_file_type": filter_file_type,
                "filter_file_id": str(filter_file_id) if filter_file_id else None,
                "similarity_threshold": similarity_threshold,
            },
        ).execute()

        return result.data or []

    def search_in_document(
        self,
        query: str,
        file_id: UUID,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """특정 문서 내에서 유사한 청크 검색"""
        return self.search_similar(
            query=query,
            match_count=top_k,
            filter_file_id=file_id,
        )

    # ------------------------------------------------------------------------
    # 문서 간 매칭
    # ------------------------------------------------------------------------

    def match_documents(
        self,
        resume_file_id: UUID,
        jd_file_id: UUID,
        top_k_per_chunk: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        이력서와 JD 청크 간 매칭

        Args:
            resume_file_id: 이력서 파일 ID
            jd_file_id: JD 파일 ID
            top_k_per_chunk: 각 이력서 청크당 반환할 JD 매칭 수

        Returns:
            청크별 매칭 결과
        """
        result = self.client.rpc(
            "match_documents_by_file",
            {
                "resume_file_id": str(resume_file_id),
                "jd_file_id": str(jd_file_id),
                "top_k": top_k_per_chunk,
            },
        ).execute()

        return result.data or []

    def calculate_overall_similarity(
        self,
        file_id_a: UUID,
        file_id_b: UUID,
    ) -> float:
        """두 문서 간 전체 유사도 계산"""
        result = self.client.rpc(
            "calculate_overall_similarity",
            {
                "file_id_a": str(file_id_a),
                "file_id_b": str(file_id_b),
            },
        ).execute()

        return result.data if result.data else 0.0

    # ------------------------------------------------------------------------
    # 종합 분석
    # ------------------------------------------------------------------------

    def analyze_match(
        self,
        resume_file_id: UUID,
        jd_file_id: UUID,
    ) -> MatchResult:
        """
        이력서-JD 종합 매칭 분석

        Args:
            resume_file_id: 이력서 파일 ID
            jd_file_id: JD 파일 ID

        Returns:
            MatchResult
        """
        logger.info(f"Analyzing match: resume={resume_file_id}, jd={jd_file_id}")

        # 1. 전체 유사도 계산
        overall_similarity = self.calculate_overall_similarity(
            resume_file_id,
            jd_file_id,
        )

        # 2. 청크별 매칭
        chunk_matches = self.match_documents(
            resume_file_id,
            jd_file_id,
            top_k_per_chunk=3,
        )

        # 3. 섹션별 점수 계산
        section_scores = self._calculate_section_scores(chunk_matches)

        # 4. 최종 점수 및 등급 계산
        match_score = self._calculate_match_score(overall_similarity, section_scores)
        match_grade = self._get_match_grade(match_score)

        return MatchResult(
            resume_file_id=resume_file_id,
            jd_file_id=jd_file_id,
            overall_similarity=overall_similarity,
            match_score=match_score,
            match_grade=match_grade,
            section_scores=section_scores,
            chunk_matches=chunk_matches,
        )

    def _calculate_section_scores(
        self,
        chunk_matches: List[Dict[str, Any]],
    ) -> List[SectionScore]:
        """청크 매칭 결과에서 섹션별 점수 계산"""
        section_data: Dict[str, List[float]] = {}

        for match in chunk_matches:
            section = match.get("resume_section_type") or "unknown"
            similarity = match.get("similarity", 0)

            if section not in section_data:
                section_data[section] = []
            section_data[section].append(similarity)

        # 섹션별 평균 점수 계산
        section_scores = []
        for section, similarities in section_data.items():
            avg_score = sum(similarities) / len(similarities) if similarities else 0
            section_scores.append(
                SectionScore(
                    section_type=section,
                    score=avg_score * 100,  # 0-100 스케일
                    chunk_count=len(similarities),
                )
            )

        # 점수 높은 순으로 정렬
        section_scores.sort(key=lambda x: x.score, reverse=True)
        return section_scores

    def _calculate_match_score(
        self,
        overall_similarity: float,
        section_scores: List[SectionScore],
    ) -> float:
        """
        최종 매칭 점수 계산

        가중치:
        - 전체 유사도: 40%
        - 섹션별 평균: 60%
        """
        # 전체 유사도 점수 (0-100)
        overall_score = overall_similarity * 100

        # 섹션별 평균 점수
        if section_scores:
            section_avg = sum(s.score for s in section_scores) / len(section_scores)
        else:
            section_avg = 0

        # 가중 평균
        final_score = (overall_score * 0.4) + (section_avg * 0.6)

        return min(100, max(0, final_score))

    def _get_match_grade(self, score: float) -> str:
        """점수에 따른 등급 반환"""
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"


# ============================================================================
# 고급 분석 함수
# ============================================================================


def analyze_skill_gaps(
    resume_file_id: UUID,
    jd_file_id: UUID,
    retriever: Optional[DocumentRetriever] = None,
) -> Dict[str, Any]:
    """
    스킬 갭 분석 (Phase 4/5에서 LLM과 연계하여 확장 예정)

    현재는 섹션별 유사도 기반으로 간단한 분석 제공
    """
    if retriever is None:
        retriever = DocumentRetriever()

    match_result = retriever.analyze_match(resume_file_id, jd_file_id)

    # 섹션별 강점/약점 분류
    strengths = []
    weaknesses = []

    for section in match_result.section_scores:
        if section.score >= 70:
            strengths.append({
                "section": section.section_type,
                "score": section.score,
                "status": "strong",
            })
        elif section.score < 50:
            weaknesses.append({
                "section": section.section_type,
                "score": section.score,
                "status": "needs_improvement",
            })

    return {
        "match_result": match_result.to_dict(),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendation": _generate_recommendation(match_result),
    }


def _generate_recommendation(match_result: MatchResult) -> str:
    """간단한 추천 메시지 생성"""
    grade = match_result.match_grade
    score = match_result.match_score

    if grade == "S":
        return "Excellent match! Your profile closely aligns with the job requirements."
    elif grade == "A":
        return "Great match! You meet most of the requirements. Consider highlighting your relevant experience."
    elif grade == "B":
        return "Good match! Focus on strengthening the areas where you scored lower."
    elif grade == "C":
        return "Fair match. Consider gaining more experience in the required skills."
    else:
        return "The job requirements differ significantly from your current profile. Consider upskilling or looking for more suitable positions."


# ============================================================================
# 싱글톤
# ============================================================================

_retriever: Optional[DocumentRetriever] = None


def get_retriever() -> DocumentRetriever:
    """DocumentRetriever 싱글톤"""
    global _retriever
    if _retriever is None:
        _retriever = DocumentRetriever()
    return _retriever

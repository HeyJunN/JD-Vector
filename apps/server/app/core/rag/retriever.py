"""
Retriever Module for RAG Pipeline
이력서와 JD 간 유사도 검색 및 매칭 분석

주요 기능:
- Supabase RPC를 통한 벡터 유사도 검색
- 이력서-JD 매칭 점수 계산
- 섹션별 상세 분석
- 유사 기술 가점 (Similar Technology Bonus)
- 섹션별 가중치 적용 (자격요건 > 우대사항 > 기타)
- 건설적 피드백 메시지 생성
"""

import logging
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from uuid import UUID
from dataclasses import dataclass, field

from supabase import Client

from app.core.rag.vector_store import get_supabase
from app.core.rag.embeddings import EmbeddingClient, get_embedding_client

# 로거 설정
logger = logging.getLogger(__name__)


# ============================================================================
# 유사 기술 매핑 (Similar Technology Mapping)
# ============================================================================

# 기술 그룹: 동일 그룹 내 기술은 유사한 것으로 간주
SIMILAR_TECH_GROUPS: List[Set[str]] = [
    # Frontend Frameworks
    {"react", "vue", "vue.js", "vuejs", "angular", "svelte", "preact"},
    # Backend Frameworks (Python)
    {"django", "flask", "fastapi", "tornado", "pyramid"},
    # Backend Frameworks (JavaScript/Node)
    {"express", "express.js", "expressjs", "nest", "nestjs", "nest.js", "koa", "hapi"},
    # Backend Frameworks (Java)
    {"spring", "spring boot", "springboot", "spring framework"},
    # Relational Databases
    {"mysql", "postgresql", "postgres", "mariadb", "oracle", "mssql", "sql server"},
    # NoSQL Databases
    {"mongodb", "mongo", "couchdb", "dynamodb", "firestore"},
    # Cache/In-Memory
    {"redis", "memcached", "elasticache"},
    # Cloud Providers
    {"aws", "amazon web services", "gcp", "google cloud", "azure", "microsoft azure"},
    # Container/Orchestration
    {"docker", "kubernetes", "k8s", "docker swarm", "podman"},
    # CI/CD
    {"jenkins", "github actions", "gitlab ci", "circleci", "travis ci", "argocd"},
    # CSS Frameworks
    {"tailwind", "tailwindcss", "bootstrap", "bulma", "material ui", "mui", "chakra ui"},
    # State Management
    {"redux", "mobx", "zustand", "recoil", "vuex", "pinia"},
    # Testing
    {"jest", "mocha", "vitest", "pytest", "junit", "cypress", "playwright"},
    # Message Queue
    {"kafka", "rabbitmq", "sqs", "redis pub/sub", "nats"},
    # Search Engine
    {"elasticsearch", "opensearch", "solr", "algolia"},
    # Mobile Development
    {"react native", "flutter", "swift", "kotlin", "swiftui"},
    # ORM
    {"sqlalchemy", "typeorm", "prisma", "sequelize", "hibernate", "django orm"},
    # Programming Languages (Similar paradigm)
    {"python", "ruby"},
    {"java", "kotlin", "scala"},
    {"javascript", "typescript", "js", "ts"},
    {"go", "golang", "rust"},
    {"c", "c++", "cpp"},
]

# 섹션별 가중치 (Section Weights)
SECTION_WEIGHTS: Dict[str, float] = {
    "requirements": 1.5,      # 자격요건: 가장 중요
    "preferred": 1.2,         # 우대사항: 중요
    "responsibilities": 1.0,  # 주요업무: 표준
    "tech_stack": 1.3,        # 기술스택: 중요
    "benefits": 0.5,          # 복리후생: 낮음
    "company_info": 0.5,      # 회사소개: 낮음
    "unknown": 0.8,           # 미분류: 약간 낮음
}

# 유사 기술 보너스 점수 (0.0 ~ 1.0)
SIMILAR_TECH_BONUS = 0.15  # 15% 보너스


# ============================================================================
# 유사 기술 헬퍼 함수
# ============================================================================


def _normalize_tech_name(tech: str) -> str:
    """기술명 정규화 (소문자, 공백 제거)"""
    return tech.lower().strip()


def _extract_tech_keywords(text: str) -> Set[str]:
    """텍스트에서 기술 키워드 추출"""
    # 기본 정규화
    text = text.lower()

    # 일반적인 기술명 패턴 추출
    # 알파벳, 숫자, 점, 하이픈으로 구성된 단어
    pattern = r'\b[a-z][a-z0-9\.\-\+]*(?:\.[a-z]+)?\b'
    matches = re.findall(pattern, text)

    # 2글자 이상인 것만 필터링 (단, js, ts, go 등 예외)
    tech_keywords = set()
    allowed_short = {"js", "ts", "go", "r", "c"}
    for match in matches:
        if len(match) >= 2 or match in allowed_short:
            tech_keywords.add(match)

    return tech_keywords


def _find_similar_techs(tech: str) -> Set[str]:
    """주어진 기술과 유사한 기술 그룹 반환"""
    normalized = _normalize_tech_name(tech)
    for group in SIMILAR_TECH_GROUPS:
        if normalized in group:
            return group
    return set()


def _calculate_similar_tech_bonus(
    resume_text: str,
    jd_text: str,
) -> Tuple[float, List[Dict[str, Any]]]:
    """
    유사 기술 보너스 계산

    Returns:
        (bonus_score, similar_tech_details)
    """
    resume_techs = _extract_tech_keywords(resume_text)
    jd_techs = _extract_tech_keywords(jd_text)

    similar_matches = []

    for jd_tech in jd_techs:
        similar_group = _find_similar_techs(jd_tech)
        if not similar_group:
            continue

        # 이력서에서 유사 기술 찾기
        for resume_tech in resume_techs:
            if resume_tech in similar_group and resume_tech != jd_tech:
                similar_matches.append({
                    "jd_required": jd_tech,
                    "resume_has": resume_tech,
                    "relationship": "similar_technology",
                })

    # 중복 제거 및 보너스 계산
    unique_matches = []
    seen = set()
    for match in similar_matches:
        key = (match["jd_required"], match["resume_has"])
        if key not in seen:
            seen.add(key)
            unique_matches.append(match)

    # 보너스: 유사 기술 매칭당 일정 보너스, 최대 15%
    if unique_matches:
        bonus = min(SIMILAR_TECH_BONUS, len(unique_matches) * 0.03)
    else:
        bonus = 0.0

    return bonus, unique_matches


def get_section_weight(section_type: str) -> float:
    """섹션 타입에 따른 가중치 반환"""
    return SECTION_WEIGHTS.get(section_type, 0.8)


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
    similar_tech_matches: List[Dict[str, Any]] = field(default_factory=list)
    similar_tech_bonus: float = 0.0
    feedback: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resume_file_id": str(self.resume_file_id),
            "jd_file_id": str(self.jd_file_id),
            "overall_similarity": round(self.overall_similarity, 4),
            "match_score": round(self.match_score, 1),
            "match_grade": self.match_grade,
            "section_scores": [s.to_dict() for s in self.section_scores],
            "chunk_match_count": len(self.chunk_matches),
            "similar_tech_matches": self.similar_tech_matches,
            "similar_tech_bonus": round(self.similar_tech_bonus * 100, 1),
            "feedback": self.feedback,
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
        resume_text: Optional[str] = None,
        jd_text: Optional[str] = None,
    ) -> MatchResult:
        """
        이력서-JD 종합 매칭 분석

        Args:
            resume_file_id: 이력서 파일 ID
            jd_file_id: JD 파일 ID
            resume_text: 이력서 전체 텍스트 (유사 기술 분석용)
            jd_text: JD 전체 텍스트 (유사 기술 분석용)

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

        # 3. 섹션별 점수 계산 (가중치 적용)
        section_scores = self._calculate_section_scores(chunk_matches)

        # 4. 유사 기술 보너스 계산
        similar_tech_bonus = 0.0
        similar_tech_matches = []
        if resume_text and jd_text:
            similar_tech_bonus, similar_tech_matches = _calculate_similar_tech_bonus(
                resume_text, jd_text
            )
            if similar_tech_matches:
                logger.info(
                    f"Found {len(similar_tech_matches)} similar tech matches, "
                    f"bonus: {similar_tech_bonus:.2%}"
                )

        # 5. 최종 점수 및 등급 계산 (보너스 포함)
        match_score = self._calculate_match_score(
            overall_similarity, section_scores, similar_tech_bonus
        )
        match_grade = self._get_match_grade(match_score)

        # 6. 건설적 피드백 생성
        feedback = self._generate_feedback(
            match_score=match_score,
            match_grade=match_grade,
            section_scores=section_scores,
            similar_tech_matches=similar_tech_matches,
        )

        return MatchResult(
            resume_file_id=resume_file_id,
            jd_file_id=jd_file_id,
            overall_similarity=overall_similarity,
            match_score=match_score,
            match_grade=match_grade,
            section_scores=section_scores,
            chunk_matches=chunk_matches,
            similar_tech_matches=similar_tech_matches,
            similar_tech_bonus=similar_tech_bonus,
            feedback=feedback,
        )

    def _calculate_section_scores(
        self,
        chunk_matches: List[Dict[str, Any]],
    ) -> List[SectionScore]:
        """
        청크 매칭 결과에서 섹션별 점수 계산 (가중치 적용)

        섹션 가중치:
        - requirements: 1.5x (자격요건)
        - preferred: 1.2x (우대사항)
        - tech_stack: 1.3x (기술스택)
        - responsibilities: 1.0x (주요업무)
        - unknown: 0.8x (미분류)
        """
        section_data: Dict[str, List[float]] = {}

        for match in chunk_matches:
            # JD 섹션 기준으로 매칭 점수 계산 (어떤 JD 요구사항에 매칭되었는지)
            jd_section = match.get("jd_section_type") or "unknown"
            resume_section = match.get("resume_section_type") or "unknown"
            similarity = match.get("similarity", 0)

            # JD 섹션 기준으로 점수 집계 (JD 요구사항 충족 여부가 중요)
            if jd_section not in section_data:
                section_data[jd_section] = []
            section_data[jd_section].append(similarity)

        # 섹션별 가중 평균 점수 계산
        section_scores = []
        for section, similarities in section_data.items():
            avg_score = sum(similarities) / len(similarities) if similarities else 0

            # 가중치 적용
            weight = get_section_weight(section)
            weighted_score = avg_score * 100 * weight  # 가중치 적용된 0-100+ 스케일

            section_scores.append(
                SectionScore(
                    section_type=section,
                    score=weighted_score,
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
        similar_tech_bonus: float = 0.0,
    ) -> float:
        """
        최종 매칭 점수 계산 (유사 기술 보너스 포함)

        가중치:
        - 전체 유사도: 30%
        - 섹션별 가중 평균: 55%
        - 유사 기술 보너스: 최대 15%

        점수 조정:
        - 섹션 가중치가 적용되어 점수가 100을 초과할 수 있음
        - 최종 점수는 0-100 범위로 정규화
        """
        # 전체 유사도 점수 (0-100)
        overall_score = overall_similarity * 100

        # 섹션별 가중 평균 점수 (가중치 적용으로 100 초과 가능)
        if section_scores:
            # 가중치 합으로 나누어 정규화
            total_weight = sum(get_section_weight(s.section_type) for s in section_scores)
            if total_weight > 0:
                section_avg = sum(s.score for s in section_scores) / total_weight
            else:
                section_avg = sum(s.score for s in section_scores) / len(section_scores)
        else:
            section_avg = 0

        # 유사 기술 보너스 (0-15 점)
        tech_bonus_score = similar_tech_bonus * 100

        # 가중 평균 계산
        base_score = (overall_score * 0.30) + (section_avg * 0.55)

        # 보너스 추가 (기본 점수의 보정)
        final_score = base_score + tech_bonus_score

        # 점수가 너무 낮은 경우 바닥 점수 보정 (완전히 무관하지 않은 이상 최소 점수 보장)
        if overall_similarity > 0.3:
            final_score = max(final_score, 35)  # 어느 정도 관련 있으면 최소 35점

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

    def _generate_feedback(
        self,
        match_score: float,
        match_grade: str,
        section_scores: List[SectionScore],
        similar_tech_matches: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        건설적 피드백 생성

        점수가 낮더라도 긍정적인 요소를 찾아 피드백 제공
        """
        feedback: Dict[str, Any] = {
            "summary": "",
            "strengths": [],
            "improvements": [],
            "potential": [],
            "action_items": [],
        }

        # 강점 분석 (높은 점수 섹션)
        for section in section_scores:
            if section.score >= 70:
                feedback["strengths"].append({
                    "section": section.section_type,
                    "score": round(section.score, 1),
                    "message": self._get_strength_message(section.section_type),
                })

        # 개선 필요 영역 (낮은 점수 섹션)
        for section in section_scores:
            if section.score < 50:
                feedback["improvements"].append({
                    "section": section.section_type,
                    "score": round(section.score, 1),
                    "message": self._get_improvement_message(section.section_type),
                })

        # 잠재력 (유사 기술 매칭)
        if similar_tech_matches:
            for match in similar_tech_matches[:5]:  # 최대 5개
                feedback["potential"].append({
                    "type": "similar_technology",
                    "jd_requires": match["jd_required"],
                    "you_have": match["resume_has"],
                    "message": f"'{match['resume_has']}' 경험이 '{match['jd_required']}'로 전환 가능합니다.",
                })

        # 등급별 요약 및 액션 아이템
        feedback["summary"] = self._get_grade_summary(match_grade, match_score)
        feedback["action_items"] = self._get_action_items(
            match_grade, section_scores, similar_tech_matches
        )

        return feedback

    def _get_strength_message(self, section_type: str) -> str:
        """섹션별 강점 메시지"""
        messages = {
            "requirements": "자격요건에서 높은 일치도를 보입니다. 핵심 역량이 잘 부합합니다.",
            "preferred": "우대사항에서 강점을 보입니다. 경쟁력 있는 지원자입니다.",
            "tech_stack": "기술 스택이 잘 매칭됩니다. 기술적 적합도가 높습니다.",
            "responsibilities": "업무 경험이 주요업무와 잘 일치합니다.",
            "unknown": "관련 경험이 확인됩니다.",
        }
        return messages.get(section_type, "해당 영역에서 강점을 보입니다.")

    def _get_improvement_message(self, section_type: str) -> str:
        """섹션별 개선 메시지"""
        messages = {
            "requirements": "자격요건 일부 항목에서 보완이 필요합니다. 관련 경험을 이력서에 더 구체적으로 기술해보세요.",
            "preferred": "우대사항 관련 경험을 추가로 어필하면 좋겠습니다.",
            "tech_stack": "일부 기술 스택 경험을 보완하면 경쟁력이 높아집니다.",
            "responsibilities": "해당 업무 경험을 더 강조해보세요.",
            "unknown": "관련 내용을 이력서에 추가해보세요.",
        }
        return messages.get(section_type, "해당 영역 경험을 보완하면 좋겠습니다.")

    def _get_grade_summary(self, grade: str, score: float) -> str:
        """등급별 요약 메시지"""
        summaries = {
            "S": f"탁월한 적합도({score:.0f}점)! 이 포지션에 매우 적합한 프로필입니다. 자신있게 지원하세요.",
            "A": f"우수한 적합도({score:.0f}점)! 대부분의 요구사항을 충족합니다. 강점을 잘 어필하세요.",
            "B": f"양호한 적합도({score:.0f}점)입니다. 핵심 역량은 갖추고 있으며, 일부 영역 보완 시 경쟁력이 높아집니다.",
            "C": f"기본 적합도({score:.0f}점)를 충족합니다. 성장 가능성과 열정을 어필하면 좋겠습니다.",
            "D": f"현재 적합도({score:.0f}점)는 낮지만, 유사 기술 경험이나 학습 의지를 강조해보세요. 모든 시작은 도전에서 비롯됩니다.",
        }
        return summaries.get(grade, f"매칭 점수: {score:.0f}점")

    def _get_action_items(
        self,
        grade: str,
        section_scores: List[SectionScore],
        similar_tech_matches: List[Dict[str, Any]],
    ) -> List[str]:
        """등급별 액션 아이템"""
        actions = []

        # 낮은 점수 섹션 개선 제안
        low_sections = [s for s in section_scores if s.score < 50]
        if low_sections:
            actions.append(f"'{low_sections[0].section_type}' 관련 경험을 이력서에 보완하세요.")

        # 유사 기술 활용 제안
        if similar_tech_matches:
            tech = similar_tech_matches[0]
            actions.append(
                f"'{tech['resume_has']}' 경험을 '{tech['jd_required']}'로 "
                "전환할 의지를 커버레터에 언급하세요."
            )

        # 등급별 일반 조언
        if grade in ("D", "C"):
            actions.append("기술 학습 계획이나 성장 의지를 어필하세요.")
            actions.append("해당 분야 사이드 프로젝트 경험이 있다면 강조하세요.")
        elif grade == "B":
            actions.append("강점 영역을 구체적 성과와 함께 강조하세요.")
        elif grade in ("A", "S"):
            actions.append("구체적인 성과 수치를 포함하여 임팩트를 강조하세요.")

        return actions[:4]  # 최대 4개


# ============================================================================
# 고급 분석 함수
# ============================================================================


def analyze_skill_gaps(
    resume_file_id: UUID,
    jd_file_id: UUID,
    resume_text: Optional[str] = None,
    jd_text: Optional[str] = None,
    retriever: Optional[DocumentRetriever] = None,
) -> Dict[str, Any]:
    """
    스킬 갭 분석 (향상된 피드백 포함)

    Args:
        resume_file_id: 이력서 파일 ID
        jd_file_id: JD 파일 ID
        resume_text: 이력서 전체 텍스트 (유사 기술 분석용)
        jd_text: JD 전체 텍스트 (유사 기술 분석용)
        retriever: DocumentRetriever 인스턴스

    Returns:
        상세 분석 결과 (피드백 포함)
    """
    if retriever is None:
        retriever = DocumentRetriever()

    match_result = retriever.analyze_match(
        resume_file_id=resume_file_id,
        jd_file_id=jd_file_id,
        resume_text=resume_text,
        jd_text=jd_text,
    )

    # 섹션별 강점/약점 분류
    strengths = []
    weaknesses = []

    for section in match_result.section_scores:
        if section.score >= 70:
            strengths.append({
                "section": section.section_type,
                "score": round(section.score, 1),
                "status": "strong",
            })
        elif section.score < 50:
            weaknesses.append({
                "section": section.section_type,
                "score": round(section.score, 1),
                "status": "needs_improvement",
            })

    return {
        "match_result": match_result.to_dict(),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "feedback": match_result.feedback,
        "similar_technologies": match_result.similar_tech_matches,
    }


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

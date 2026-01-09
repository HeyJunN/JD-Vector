"""
Text Splitter for RAG Pipeline
문서를 의미 단위(섹션)로 분할하고 청킹하는 모듈

핵심 전략:
1. 섹션 헤더 감지 (이력서/JD 각각의 패턴)
2. 섹션별 분리 후 개별 청킹
3. 청크에 섹션 타입 메타데이터 추가
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.models.schemas import FileTypeEnum


# ============================================================================
# 섹션 타입 정의
# ============================================================================


class SectionType(str, Enum):
    """문서 섹션 타입"""

    # 이력서 섹션
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    SKILLS = "skills"
    EDUCATION = "education"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    AWARDS = "awards"
    CONTACT = "contact"

    # JD 섹션
    COMPANY_INFO = "company_info"
    RESPONSIBILITIES = "responsibilities"
    REQUIREMENTS = "requirements"
    PREFERRED = "preferred"
    BENEFITS = "benefits"
    SALARY = "salary"

    # 공통
    UNKNOWN = "unknown"


# ============================================================================
# 섹션 헤더 패턴 정의 (한국어/영어)
# ============================================================================

# 이력서 섹션 패턴
RESUME_SECTION_PATTERNS: Dict[SectionType, List[str]] = {
    SectionType.SUMMARY: [
        r"(?i)^[\s]*(?:summary|profile|about\s*me|자기\s*소개|소개|요약|개요)",
        r"(?i)^[\s]*(?:professional\s*summary|career\s*summary|executive\s*summary)",
    ],
    SectionType.EXPERIENCE: [
        r"(?i)^[\s]*(?:experience|work\s*experience|employment|career|경력|경험|이력|직장\s*경력)",
        r"(?i)^[\s]*(?:professional\s*experience|work\s*history|업무\s*경력|근무\s*경력)",
    ],
    SectionType.SKILLS: [
        r"(?i)^[\s]*(?:skills|technical\s*skills|기술|스킬|역량|기술\s*스택|보유\s*기술)",
        r"(?i)^[\s]*(?:core\s*competencies|expertise|technologies|tools)",
    ],
    SectionType.EDUCATION: [
        r"(?i)^[\s]*(?:education|academic|학력|교육|학교)",
        r"(?i)^[\s]*(?:educational\s*background|학력\s*사항)",
    ],
    SectionType.PROJECTS: [
        r"(?i)^[\s]*(?:projects|프로젝트|포트폴리오|portfolio)",
        r"(?i)^[\s]*(?:personal\s*projects|side\s*projects|개인\s*프로젝트)",
    ],
    SectionType.CERTIFICATIONS: [
        r"(?i)^[\s]*(?:certifications?|licenses?|자격증|자격\s*사항|면허)",
        r"(?i)^[\s]*(?:professional\s*certifications?|certificates?)",
    ],
    SectionType.AWARDS: [
        r"(?i)^[\s]*(?:awards?|honors?|achievements?|수상|수상\s*경력|성과)",
    ],
    SectionType.CONTACT: [
        r"(?i)^[\s]*(?:contact|연락처|인적\s*사항|개인\s*정보)",
    ],
}

# JD 섹션 패턴
JD_SECTION_PATTERNS: Dict[SectionType, List[str]] = {
    SectionType.COMPANY_INFO: [
        r"(?i)^[\s]*(?:about\s*us|company|회사\s*소개|기업\s*소개|우리\s*회사)",
        r"(?i)^[\s]*(?:who\s*we\s*are|our\s*company|회사\s*정보)",
    ],
    SectionType.RESPONSIBILITIES: [
        r"(?i)^[\s]*(?:responsibilities|duties|role|담당\s*업무|주요\s*업무|업무\s*내용)",
        r"(?i)^[\s]*(?:what\s*you.+do|job\s*description|하는\s*일|역할)",
        r"(?i)^[\s]*(?:key\s*responsibilities|업무\s*소개)",
    ],
    SectionType.REQUIREMENTS: [
        r"(?i)^[\s]*(?:requirements?|qualifications?|자격\s*요건|필수\s*요건|지원\s*자격)",
        r"(?i)^[\s]*(?:what\s*we.+looking|필수\s*조건|기본\s*자격|required)",
        r"(?i)^[\s]*(?:must\s*have|minimum\s*requirements?|필수\s*사항)",
    ],
    SectionType.PREFERRED: [
        r"(?i)^[\s]*(?:preferred|nice\s*to\s*have|우대\s*사항|우대\s*조건|플러스)",
        r"(?i)^[\s]*(?:bonus|plus|desired|선호\s*사항|가점\s*사항)",
    ],
    SectionType.BENEFITS: [
        r"(?i)^[\s]*(?:benefits?|perks?|복리\s*후생|혜택|베네핏|복지)",
        r"(?i)^[\s]*(?:what\s*we\s*offer|우리가\s*제공|근무\s*환경)",
    ],
    SectionType.SALARY: [
        r"(?i)^[\s]*(?:salary|compensation|연봉|급여|보상|처우)",
        r"(?i)^[\s]*(?:pay|remuneration|급여\s*조건)",
    ],
}


# ============================================================================
# 섹션 감지 헬퍼 함수
# ============================================================================


def detect_section_type(
    line: str,
    file_type: FileTypeEnum,
) -> Optional[SectionType]:
    """
    텍스트 라인에서 섹션 헤더를 감지

    Args:
        line: 검사할 텍스트 라인
        file_type: 파일 타입 (resume/job_description)

    Returns:
        감지된 섹션 타입 또는 None
    """
    # 파일 타입에 따른 패턴 선택
    patterns = (
        RESUME_SECTION_PATTERNS
        if file_type == FileTypeEnum.RESUME
        else JD_SECTION_PATTERNS
    )

    # 라인 정규화 (앞뒤 공백, 특수문자 제거)
    cleaned_line = line.strip()

    # 너무 긴 라인은 헤더가 아님
    if len(cleaned_line) > 100:
        return None

    # 각 섹션 타입의 패턴과 매칭
    for section_type, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, cleaned_line):
                return section_type

    return None


def is_section_header(line: str, file_type: FileTypeEnum) -> bool:
    """라인이 섹션 헤더인지 확인"""
    return detect_section_type(line, file_type) is not None


# ============================================================================
# 섹션 기반 문서 분할
# ============================================================================


@dataclass
class TextSection:
    """분할된 섹션 정보"""

    section_type: SectionType
    content: str
    start_line: int
    end_line: int


def split_into_sections(
    text: str,
    file_type: FileTypeEnum,
) -> List[TextSection]:
    """
    텍스트를 섹션 단위로 분할

    Args:
        text: 전체 텍스트
        file_type: 파일 타입

    Returns:
        섹션 리스트
    """
    lines = text.split("\n")
    sections: List[TextSection] = []

    current_section_type = SectionType.UNKNOWN
    current_content_lines: List[str] = []
    current_start_line = 0

    for i, line in enumerate(lines):
        detected_type = detect_section_type(line, file_type)

        if detected_type is not None:
            # 이전 섹션 저장 (내용이 있는 경우)
            if current_content_lines:
                content = "\n".join(current_content_lines).strip()
                if content:  # 빈 섹션은 저장하지 않음
                    sections.append(
                        TextSection(
                            section_type=current_section_type,
                            content=content,
                            start_line=current_start_line,
                            end_line=i - 1,
                        )
                    )

            # 새 섹션 시작
            current_section_type = detected_type
            current_content_lines = [line]  # 헤더도 포함
            current_start_line = i
        else:
            current_content_lines.append(line)

    # 마지막 섹션 저장
    if current_content_lines:
        content = "\n".join(current_content_lines).strip()
        if content:
            sections.append(
                TextSection(
                    section_type=current_section_type,
                    content=content,
                    start_line=current_start_line,
                    end_line=len(lines) - 1,
                )
            )

    return sections


# ============================================================================
# 청킹 설정
# ============================================================================


@dataclass
class ChunkConfig:
    """청킹 설정"""

    chunk_size: int = 1000
    chunk_overlap: int = 200
    separators: List[str] = None

    def __post_init__(self):
        if self.separators is None:
            # 기본 구분자: 단락 > 문장 > 단어 순서로 분할 시도
            self.separators = [
                "\n\n",  # 빈 줄 (단락 구분)
                "\n",  # 줄바꿈
                ". ",  # 문장 끝
                "! ",
                "? ",
                "; ",
                ", ",  # 절 구분
                " ",  # 단어
                "",  # 마지막 수단: 글자 단위
            ]


# 파일 타입별 기본 설정
DEFAULT_CHUNK_CONFIGS: Dict[FileTypeEnum, ChunkConfig] = {
    # 이력서: 섹션이 짧으므로 작은 청크
    FileTypeEnum.RESUME: ChunkConfig(
        chunk_size=800,
        chunk_overlap=150,
    ),
    # JD: 상세 설명이 길 수 있으므로 큰 청크
    FileTypeEnum.JOB_DESCRIPTION: ChunkConfig(
        chunk_size=1000,
        chunk_overlap=200,
    ),
}


# ============================================================================
# 메인 청킹 함수
# ============================================================================


def create_text_splitter(config: ChunkConfig) -> RecursiveCharacterTextSplitter:
    """RecursiveCharacterTextSplitter 생성"""
    return RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        separators=config.separators,
        length_function=len,
        is_separator_regex=False,
    )


def chunk_document(
    document: Document,
    file_type: FileTypeEnum,
    config: Optional[ChunkConfig] = None,
    preserve_sections: bool = True,
) -> List[Document]:
    """
    LangChain Document를 청크로 분할

    Args:
        document: 원본 Document
        file_type: 파일 타입
        config: 청킹 설정 (None이면 기본값 사용)
        preserve_sections: 섹션 경계 보존 여부

    Returns:
        청킹된 Document 리스트
    """
    if config is None:
        config = DEFAULT_CHUNK_CONFIGS.get(
            file_type,
            ChunkConfig(),  # 기본값
        )

    text = document.page_content
    base_metadata = document.metadata.copy()

    if preserve_sections:
        # 섹션 기반 청킹
        return _chunk_with_sections(text, file_type, config, base_metadata)
    else:
        # 단순 청킹
        return _chunk_simple(text, config, base_metadata)


def _chunk_with_sections(
    text: str,
    file_type: FileTypeEnum,
    config: ChunkConfig,
    base_metadata: Dict[str, Any],
) -> List[Document]:
    """섹션을 보존하면서 청킹"""
    sections = split_into_sections(text, file_type)
    splitter = create_text_splitter(config)

    chunks: List[Document] = []
    global_chunk_index = 0

    for section in sections:
        # 섹션 내용이 청크 크기보다 작으면 그대로 사용
        if len(section.content) <= config.chunk_size:
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update(
                {
                    "chunk_index": global_chunk_index,
                    "section_type": section.section_type.value,
                    "section_start_line": section.start_line,
                    "section_end_line": section.end_line,
                    "is_full_section": True,
                }
            )
            chunks.append(
                Document(
                    page_content=section.content,
                    metadata=chunk_metadata,
                )
            )
            global_chunk_index += 1
        else:
            # 섹션 내용이 크면 청킹
            section_chunks = splitter.split_text(section.content)

            for i, chunk_text in enumerate(section_chunks):
                chunk_metadata = base_metadata.copy()
                chunk_metadata.update(
                    {
                        "chunk_index": global_chunk_index,
                        "section_type": section.section_type.value,
                        "section_chunk_index": i,
                        "section_chunk_total": len(section_chunks),
                        "section_start_line": section.start_line,
                        "section_end_line": section.end_line,
                        "is_full_section": False,
                    }
                )
                chunks.append(
                    Document(
                        page_content=chunk_text,
                        metadata=chunk_metadata,
                    )
                )
                global_chunk_index += 1

    return chunks


def _chunk_simple(
    text: str,
    config: ChunkConfig,
    base_metadata: Dict[str, Any],
) -> List[Document]:
    """단순 청킹 (섹션 무시)"""
    splitter = create_text_splitter(config)
    chunk_texts = splitter.split_text(text)

    chunks: List[Document] = []
    for i, chunk_text in enumerate(chunk_texts):
        chunk_metadata = base_metadata.copy()
        chunk_metadata.update(
            {
                "chunk_index": i,
                "section_type": SectionType.UNKNOWN.value,
            }
        )
        chunks.append(
            Document(
                page_content=chunk_text,
                metadata=chunk_metadata,
            )
        )

    return chunks


# ============================================================================
# 고급 청킹 함수
# ============================================================================


def chunk_documents(
    documents: List[Document],
    file_type: FileTypeEnum,
    config: Optional[ChunkConfig] = None,
    preserve_sections: bool = True,
) -> List[Document]:
    """
    여러 Document를 일괄 청킹

    Args:
        documents: Document 리스트
        file_type: 파일 타입
        config: 청킹 설정
        preserve_sections: 섹션 경계 보존 여부

    Returns:
        청킹된 Document 리스트
    """
    all_chunks: List[Document] = []

    for doc in documents:
        chunks = chunk_document(doc, file_type, config, preserve_sections)
        all_chunks.extend(chunks)

    # 전체 청크 인덱스 재할당
    for i, chunk in enumerate(all_chunks):
        chunk.metadata["global_chunk_index"] = i

    return all_chunks


def estimate_token_count(text: str, model: str = "text-embedding-3-small") -> int:
    """
    텍스트의 토큰 수 추정 (OpenAI 모델 기준)

    간단한 휴리스틱:
    - 영어: ~4 글자 = 1 토큰
    - 한국어: ~2 글자 = 1 토큰
    """
    # 한글 비율 계산
    korean_chars = len(re.findall(r"[가-힣]", text))
    total_chars = len(text)

    if total_chars == 0:
        return 0

    korean_ratio = korean_chars / total_chars

    # 가중 평균으로 토큰 수 추정
    # 한국어 비율이 높을수록 글자당 토큰 수가 높음
    chars_per_token = 4 - (korean_ratio * 2)  # 4 (영어) ~ 2 (한국어)

    return int(total_chars / chars_per_token)


def add_token_counts(chunks: List[Document]) -> List[Document]:
    """청크에 토큰 수 추정치 추가"""
    for chunk in chunks:
        chunk.metadata["estimated_tokens"] = estimate_token_count(chunk.page_content)
        chunk.metadata["char_count"] = len(chunk.page_content)

    return chunks


# ============================================================================
# 유틸리티 함수
# ============================================================================


def get_chunk_summary(chunks: List[Document]) -> Dict[str, Any]:
    """청킹 결과 요약"""
    if not chunks:
        return {"total_chunks": 0}

    total_chars = sum(len(c.page_content) for c in chunks)
    total_tokens = sum(c.metadata.get("estimated_tokens", 0) for c in chunks)

    section_counts: Dict[str, int] = {}
    for chunk in chunks:
        section = chunk.metadata.get("section_type", "unknown")
        section_counts[section] = section_counts.get(section, 0) + 1

    return {
        "total_chunks": len(chunks),
        "total_characters": total_chars,
        "estimated_tokens": total_tokens,
        "avg_chunk_size": total_chars // len(chunks) if chunks else 0,
        "section_distribution": section_counts,
    }


def merge_small_chunks(
    chunks: List[Document],
    min_chunk_size: int = 100,
) -> List[Document]:
    """
    너무 작은 청크를 인접 청크와 병합

    Args:
        chunks: 청크 리스트
        min_chunk_size: 최소 청크 크기

    Returns:
        병합된 청크 리스트
    """
    if len(chunks) <= 1:
        return chunks

    merged: List[Document] = []
    buffer: Optional[Document] = None

    for chunk in chunks:
        if buffer is None:
            buffer = chunk
        elif len(buffer.page_content) < min_chunk_size:
            # 버퍼가 너무 작으면 현재 청크와 병합
            buffer = Document(
                page_content=buffer.page_content + "\n\n" + chunk.page_content,
                metadata={
                    **buffer.metadata,
                    "merged": True,
                    "original_chunks": buffer.metadata.get("original_chunks", 1) + 1,
                },
            )
        else:
            merged.append(buffer)
            buffer = chunk

    # 마지막 버퍼 처리
    if buffer is not None:
        merged.append(buffer)

    return merged

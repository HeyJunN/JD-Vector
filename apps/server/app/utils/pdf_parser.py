"""
PDF Parsing Utilities
다양한 PDF 라이브러리를 활용한 텍스트 추출 및 정제
"""

import re
import unicodedata
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List
from io import BytesIO
import time

# PDF 파싱 라이브러리
import pypdf
import pdfplumber
import fitz  # PyMuPDF

from app.models.schemas import ParserTypeEnum, FileTypeEnum


# ============================================================================
# 텍스트 정제 (Text Cleaning)
# ============================================================================


def clean_text(text: str, aggressive: bool = False) -> str:
    """
    PDF에서 추출한 텍스트를 LLM 입력에 적합하게 정제

    Args:
        text: 원본 텍스트
        aggressive: True면 더 강력한 정제 수행 (페이지 번호, 헤더/푸터 제거 등)

    Returns:
        정제된 텍스트
    """
    if not text:
        return ""

    # 1. 유니코드 정규화 (NFD -> NFC)
    text = unicodedata.normalize("NFC", text)

    # 2. 제어 문자 제거 (줄바꿈, 탭 제외)
    text = "".join(char for char in text if unicodedata.category(char)[0] != "C" or char in "\n\t\r")

    # 3. 탭을 공백으로 변환
    text = text.replace("\t", " ")

    # 4. 캐리지 리턴 제거
    text = text.replace("\r", "")

    # 5. 연속된 공백을 하나로
    text = re.sub(r" +", " ", text)

    # 6. 줄 끝의 불필요한 하이픈 제거 (단어 분절)
    # "computa-\ntional" -> "computational"
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    # 7. 연속된 줄바꿈을 최대 2개로 제한
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 8. 각 줄의 앞뒤 공백 제거
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    # 9. Aggressive 모드: 추가 정제
    if aggressive:
        # 페이지 번호 패턴 제거 (단독 숫자 라인)
        text = re.sub(r"^\d+$", "", text, flags=re.MULTILINE)

        # 2글자 이하의 단독 라인 제거 (헤더/푸터 가능성)
        lines = [line for line in text.split("\n") if len(line.strip()) > 2 or line.strip() == ""]
        text = "\n".join(lines)

    # 10. 시작/끝 공백 제거
    text = text.strip()

    return text


def detect_language(text: str) -> str:
    """
    텍스트의 주 언어를 간단한 휴리스틱으로 판별

    Args:
        text: 분석할 텍스트

    Returns:
        언어 코드: 'ko' (한국어), 'en' (영어), 'mixed' (혼합), 'unknown'
    """
    if not text or len(text.strip()) < 10:
        return "unknown"

    # 한글 유니코드 범위: AC00-D7A3
    korean_chars = len(re.findall(r"[가-힣]", text))

    # 영문 알파벳
    english_chars = len(re.findall(r"[a-zA-Z]", text))

    total_chars = korean_chars + english_chars

    if total_chars == 0:
        return "unknown"

    korean_ratio = korean_chars / total_chars
    english_ratio = english_chars / total_chars

    # 판별 기준
    if korean_ratio > 0.6:
        return "ko"
    elif english_ratio > 0.6:
        return "en"
    elif korean_ratio > 0.2 and english_ratio > 0.2:
        return "mixed"
    else:
        return "unknown"


# ============================================================================
# PDF 파서 구현
# ============================================================================


def parse_with_pypdf(file_path: Path) -> Tuple[str, Dict[str, Any]]:
    """
    PyPDF를 사용한 PDF 파싱 (LangChain PyPDFLoader의 기반)

    Args:
        file_path: PDF 파일 경로

    Returns:
        (추출된 텍스트, 메타데이터)
    """
    text_parts = []
    metadata = {
        "page_count": 0,
        "author": None,
        "created_date": None,
        "modified_date": None,
        "title": None,
        "subject": None,
    }

    try:
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            metadata["page_count"] = len(reader.pages)

            # 메타데이터 추출
            if reader.metadata:
                metadata["author"] = reader.metadata.get("/Author", None)
                metadata["title"] = reader.metadata.get("/Title", None)
                metadata["subject"] = reader.metadata.get("/Subject", None)

                # 날짜 정보 (D:YYYYMMDDHHmmSS 형식)
                created = reader.metadata.get("/CreationDate", None)
                if created:
                    metadata["created_date"] = str(created)

                modified = reader.metadata.get("/ModDate", None)
                if modified:
                    metadata["modified_date"] = str(modified)

            # 각 페이지에서 텍스트 추출
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

    except Exception as e:
        raise ValueError(f"PyPDF parsing failed: {str(e)}")

    full_text = "\n\n".join(text_parts)
    return full_text, metadata


def parse_with_pdfplumber(
    file_path: Path, extract_tables: bool = False
) -> Tuple[str, Dict[str, Any], Optional[List[List[List[str]]]]]:
    """
    pdfplumber를 사용한 PDF 파싱 (테이블 추출 가능)

    Args:
        file_path: PDF 파일 경로
        extract_tables: 테이블 추출 여부

    Returns:
        (추출된 텍스트, 메타데이터, 테이블 데이터)
    """
    text_parts = []
    all_tables = []
    metadata = {
        "page_count": 0,
        "has_tables": False,
    }

    try:
        with pdfplumber.open(file_path) as pdf:
            metadata["page_count"] = len(pdf.pages)

            # PDF 메타데이터
            if pdf.metadata:
                metadata["author"] = pdf.metadata.get("Author", None)
                metadata["title"] = pdf.metadata.get("Title", None)
                metadata["subject"] = pdf.metadata.get("Subject", None)
                metadata["created_date"] = pdf.metadata.get("CreationDate", None)
                metadata["modified_date"] = pdf.metadata.get("ModDate", None)

            for page in pdf.pages:
                # 텍스트 추출
                text = page.extract_text()
                if text:
                    text_parts.append(text)

                # 테이블 추출
                if extract_tables:
                    tables = page.extract_tables()
                    if tables:
                        metadata["has_tables"] = True
                        all_tables.append(tables)

    except Exception as e:
        raise ValueError(f"pdfplumber parsing failed: {str(e)}")

    full_text = "\n\n".join(text_parts)
    return full_text, metadata, all_tables if extract_tables else None


def parse_with_pymupdf(file_path: Path) -> Tuple[str, Dict[str, Any]]:
    """
    PyMuPDF(fitz)를 사용한 빠른 PDF 파싱

    Args:
        file_path: PDF 파일 경로

    Returns:
        (추출된 텍스트, 메타데이터)
    """
    text_parts = []
    metadata = {
        "page_count": 0,
        "author": None,
        "created_date": None,
        "modified_date": None,
        "title": None,
        "subject": None,
    }

    try:
        doc = fitz.open(file_path)
        metadata["page_count"] = len(doc)

        # 메타데이터 추출
        doc_metadata = doc.metadata
        if doc_metadata:
            metadata["author"] = doc_metadata.get("author", None)
            metadata["title"] = doc_metadata.get("title", None)
            metadata["subject"] = doc_metadata.get("subject", None)
            metadata["created_date"] = doc_metadata.get("creationDate", None)
            metadata["modified_date"] = doc_metadata.get("modDate", None)

        # 각 페이지에서 텍스트 추출
        for page in doc:
            text = page.get_text()
            if text:
                text_parts.append(text)

        doc.close()

    except Exception as e:
        raise ValueError(f"PyMuPDF parsing failed: {str(e)}")

    full_text = "\n\n".join(text_parts)
    return full_text, metadata


# ============================================================================
# 자동 파서 선택 및 통합 인터페이스
# ============================================================================


def select_parser_auto(file_type: FileTypeEnum) -> ParserTypeEnum:
    """
    파일 타입에 따라 최적의 파서를 자동 선택

    Args:
        file_type: 파일 용도 (resume/job_description)

    Returns:
        선택된 파서 타입
    """
    if file_type == FileTypeEnum.JOB_DESCRIPTION:
        # JD는 테이블과 복잡한 레이아웃이 많음 -> pdfplumber
        return ParserTypeEnum.PDFPLUMBER
    else:
        # 이력서는 일반적인 텍스트 추출로 충분 -> pypdf (LangChain 통합)
        return ParserTypeEnum.PYPDF


def parse_pdf(
    file_path: Path,
    file_type: FileTypeEnum,
    parser_type: ParserTypeEnum = ParserTypeEnum.AUTO,
    extract_tables: bool = False,
) -> Dict[str, Any]:
    """
    PDF 파일을 파싱하고 텍스트 추출 및 정제를 수행하는 통합 함수

    Args:
        file_path: PDF 파일 경로
        file_type: 파일 용도
        parser_type: 파서 타입 (AUTO면 자동 선택)
        extract_tables: 테이블 추출 여부

    Returns:
        {
            'text_content': 원본 텍스트,
            'cleaned_text': 정제된 텍스트,
            'metadata': 메타데이터 dict,
            'parser_used': 사용된 파서,
            'tables': 테이블 데이터 (옵션),
            'extraction_time_ms': 소요 시간
        }
    """
    start_time = time.time()

    # 파서 자동 선택
    if parser_type == ParserTypeEnum.AUTO:
        parser_type = select_parser_auto(file_type)

    # 파서별 처리
    tables = None

    try:
        if parser_type == ParserTypeEnum.PYPDF:
            text, metadata = parse_with_pypdf(file_path)

        elif parser_type == ParserTypeEnum.PDFPLUMBER:
            text, metadata, tables = parse_with_pdfplumber(file_path, extract_tables)

        elif parser_type == ParserTypeEnum.PYMUPDF:
            text, metadata = parse_with_pymupdf(file_path)

        else:
            raise ValueError(f"Unsupported parser type: {parser_type}")

    except Exception as e:
        # 파싱 실패 시 fallback 시도
        try:
            # pypdf로 재시도
            if parser_type != ParserTypeEnum.PYPDF:
                text, metadata = parse_with_pypdf(file_path)
                parser_type = ParserTypeEnum.PYPDF
            else:
                raise e
        except Exception as fallback_error:
            raise ValueError(f"All parsers failed: {str(fallback_error)}")

    # 텍스트 정제
    # JD는 aggressive 모드로 정제 (페이지 번호, 헤더/푸터 제거)
    aggressive = file_type == FileTypeEnum.JOB_DESCRIPTION
    cleaned_text = clean_text(text, aggressive=aggressive)

    # 언어 감지
    language = detect_language(cleaned_text)

    # 소요 시간 계산
    extraction_time_ms = (time.time() - start_time) * 1000

    # 결과 구성
    result = {
        "text_content": text,
        "cleaned_text": cleaned_text,
        "word_count": len(cleaned_text.split()),
        "char_count": len(cleaned_text),
        "metadata": {
            **metadata,
            "language": language,
            "parser_used": parser_type,
            "extraction_time_ms": round(extraction_time_ms, 2),
        },
        "parser_used": parser_type,
    }

    if tables:
        result["tables"] = tables

    return result


# ============================================================================
# 유틸리티 함수
# ============================================================================


def get_pdf_page_count(file_path: Path) -> int:
    """
    PDF 페이지 수를 빠르게 확인 (파싱 없이)

    Args:
        file_path: PDF 파일 경로

    Returns:
        페이지 수
    """
    try:
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            return len(reader.pages)
    except Exception:
        return 0


def is_valid_pdf(file_path: Path) -> bool:
    """
    유효한 PDF 파일인지 검증

    Args:
        file_path: PDF 파일 경로

    Returns:
        유효성 여부
    """
    try:
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            # 최소 1페이지 이상이어야 함
            return len(reader.pages) > 0
    except Exception:
        return False

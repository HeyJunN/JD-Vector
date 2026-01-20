"""
Roadmap Service - 맞춤형 학습 로드맵 생성 (고도화 버전)

주요 기능:
- 스킬 갭 분석 결과를 바탕으로 전략적 학습 커리큘럼 생성
- 주차별 학습 계획 및 체크리스트 제공
- 고퀄리티 한국어 학습 리소스 매핑 (유튜브, 인프런, 공식 문서)
- GPT-4o mini를 활용한 개인화된 로드맵 생성
- 프론트엔드-백엔드 브릿지 전략 반영
- 등급별 로드맵 생성 전략 차별화
"""

import logging
import json
from typing import List, Dict, Any, Optional, Set
from uuid import UUID
from openai import OpenAI

from app.core.config import settings
from app.core.rag.retriever import DocumentRetriever, get_retriever, analyze_skill_gaps
from app.models.schemas import (
    RoadmapWeek,
    RoadmapTask,
    LearningResource,
    RoadmapData,
)

# 로거 설정
logger = logging.getLogger(__name__)


# ============================================================================
# 고퀄리티 한국어 학습 리소스 매핑 (확장 버전)
# ============================================================================

# 프론트엔드 기술 리소스
FRONTEND_RESOURCES: Dict[str, List[Dict[str, Any]]] = {
    "react": [
        {
            "title": "React 공식 문서 (한글)",
            "url": "https://ko.react.dev/learn",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "React 공식 튜토리얼 및 가이드 (한글 번역)",
            "estimated_hours": 20,
        },
        {
            "title": "생활코딩 React",
            "url": "https://www.youtube.com/playlist?list=PLuHgQVnccGMCRv6f8H9K5Xwsdyg4sFhdi",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "beginner",
            "description": "생활코딩의 React 기초 강의",
            "estimated_hours": 10,
        },
        {
            "title": "노마드코더 React 마스터클래스",
            "url": "https://nomadcoders.co/react-for-beginners",
            "type": "course",
            "platform": "Nomad",
            "difficulty": "intermediate",
            "description": "실전 프로젝트로 배우는 React",
            "estimated_hours": 15,
        },
        {
            "title": "드림코딩 React 완전 정복",
            "url": "https://www.youtube.com/playlist?list=PLv2d7VI9OotTVOL4QmPfvJWPJvkmv6h-2",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "intermediate",
            "description": "실무 중심 React 강의",
            "estimated_hours": 12,
        },
    ],
    "typescript": [
        {
            "title": "TypeScript 공식 핸드북 (한글)",
            "url": "https://typescript-kr.github.io/",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "TypeScript 공식 문서 한글 번역",
            "estimated_hours": 15,
        },
        {
            "title": "타입스크립트 입문 - 캡틴판교",
            "url": "https://joshua1988.github.io/ts/",
            "type": "tutorial",
            "platform": "Docs",
            "difficulty": "beginner",
            "description": "국내 최고의 TypeScript 입문 가이드",
            "estimated_hours": 10,
        },
        {
            "title": "노마드코더 TypeScript 마스터클래스",
            "url": "https://nomadcoders.co/typescript-for-beginners",
            "type": "course",
            "platform": "Nomad",
            "difficulty": "intermediate",
            "description": "실전 TypeScript 프로젝트",
            "estimated_hours": 12,
        },
        {
            "title": "드림코딩 TypeScript",
            "url": "https://www.youtube.com/watch?v=5oGAkQsGWkc",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "intermediate",
            "description": "TypeScript 핵심 개념 정리",
            "estimated_hours": 8,
        },
    ],
    "javascript": [
        {
            "title": "모던 JavaScript 튜토리얼",
            "url": "https://ko.javascript.info/",
            "type": "tutorial",
            "platform": "Docs",
            "difficulty": "beginner",
            "description": "가장 자세한 JavaScript 한글 튜토리얼",
            "estimated_hours": 30,
        },
        {
            "title": "생활코딩 JavaScript",
            "url": "https://www.youtube.com/playlist?list=PLuHgQVnccGMBB348PWRN0fREzYcYgFybf",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "beginner",
            "description": "JavaScript 기초부터 차근차근",
            "estimated_hours": 15,
        },
        {
            "title": "JavaScript ES6+ 제대로 알아보기",
            "url": "https://www.inflearn.com/course/ecmascript-6-flow",
            "type": "course",
            "platform": "Inflearn",
            "difficulty": "intermediate",
            "description": "최신 JavaScript 문법 마스터",
            "estimated_hours": 10,
        },
    ],
    "next.js": [
        {
            "title": "Next.js 공식 문서 (한글)",
            "url": "https://nextjs.org/docs",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "intermediate",
            "description": "Next.js 13+ App Router 공식 가이드",
            "estimated_hours": 12,
        },
        {
            "title": "노마드코더 Next.js 시작하기",
            "url": "https://nomadcoders.co/nextjs-fundamentals",
            "type": "course",
            "platform": "Nomad",
            "difficulty": "intermediate",
            "description": "Next.js 풀스택 프로젝트",
            "estimated_hours": 15,
        },
    ],
    "vue": [
        {
            "title": "Vue.js 공식 가이드 (한글)",
            "url": "https://v3.ko.vuejs.org/guide/introduction.html",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "Vue 3 Composition API 공식 문서",
            "estimated_hours": 15,
        },
        {
            "title": "Vue.js 시작하기 - 캡틴판교",
            "url": "https://joshua1988.github.io/vue-camp/",
            "type": "tutorial",
            "platform": "Docs",
            "difficulty": "beginner",
            "description": "Vue.js 기초 완벽 가이드",
            "estimated_hours": 12,
        },
    ],
    "html": [
        {
            "title": "MDN HTML 가이드 (한글)",
            "url": "https://developer.mozilla.org/ko/docs/Learn/HTML",
            "type": "documentation",
            "platform": "MDN",
            "difficulty": "beginner",
            "description": "HTML 기초부터 심화까지",
            "estimated_hours": 10,
        },
    ],
    "css": [
        {
            "title": "MDN CSS 가이드 (한글)",
            "url": "https://developer.mozilla.org/ko/docs/Learn/CSS",
            "type": "documentation",
            "platform": "MDN",
            "difficulty": "beginner",
            "description": "CSS 기초부터 레이아웃까지",
            "estimated_hours": 12,
        },
        {
            "title": "생활코딩 CSS",
            "url": "https://www.youtube.com/playlist?list=PLuHgQVnccGMDaVaBmkX0qfB45R_bYrV62",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "beginner",
            "description": "CSS 기초 강의",
            "estimated_hours": 8,
        },
    ],
    "tailwind": [
        {
            "title": "Tailwind CSS 공식 문서",
            "url": "https://tailwindcss.com/docs",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "Tailwind CSS 공식 가이드",
            "estimated_hours": 5,
        },
    ],
}

# 백엔드 기술 리소스
BACKEND_RESOURCES: Dict[str, List[Dict[str, Any]]] = {
    "node.js": [
        {
            "title": "Node.js 공식 가이드",
            "url": "https://nodejs.org/ko/docs/guides/",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "Node.js 공식 한글 문서",
            "estimated_hours": 10,
        },
        {
            "title": "생활코딩 Node.js",
            "url": "https://www.youtube.com/playlist?list=PLuHgQVnccGMA9QQX5wqj6ThK7t2tsGxjm",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "beginner",
            "description": "Node.js 기초 강의",
            "estimated_hours": 12,
        },
        {
            "title": "노마드코더 Node.js 마스터클래스",
            "url": "https://nomadcoders.co/nodejs-masterclass",
            "type": "course",
            "platform": "Nomad",
            "difficulty": "intermediate",
            "description": "실전 Node.js 프로젝트",
            "estimated_hours": 15,
        },
    ],
    "express": [
        {
            "title": "Express.js 공식 가이드",
            "url": "https://expressjs.com/ko/guide/routing.html",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "Express.js 라우팅 및 미들웨어 (한글)",
            "estimated_hours": 8,
        },
        {
            "title": "Express.js 입문 - 인프런",
            "url": "https://www.inflearn.com/course/node-js",
            "type": "course",
            "platform": "Inflearn",
            "difficulty": "beginner",
            "description": "Express.js 기초 강의",
            "estimated_hours": 10,
        },
    ],
    "fastapi": [
        {
            "title": "FastAPI 공식 튜토리얼",
            "url": "https://fastapi.tiangolo.com/ko/tutorial/",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "FastAPI 완벽 가이드 (한글)",
            "estimated_hours": 10,
        },
    ],
    "django": [
        {
            "title": "Django 공식 튜토리얼 (한글)",
            "url": "https://docs.djangoproject.com/ko/stable/intro/tutorial01/",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "Django 기초부터 배포까지",
            "estimated_hours": 15,
        },
        {
            "title": "점프 투 장고",
            "url": "https://wikidocs.net/book/4223",
            "type": "tutorial",
            "platform": "Docs",
            "difficulty": "beginner",
            "description": "Django 입문 한글 가이드",
            "estimated_hours": 20,
        },
    ],
    "python": [
        {
            "title": "점프 투 파이썬",
            "url": "https://wikidocs.net/book/1",
            "type": "tutorial",
            "platform": "Docs",
            "difficulty": "beginner",
            "description": "파이썬 기초 완벽 가이드",
            "estimated_hours": 20,
        },
        {
            "title": "생활코딩 Python",
            "url": "https://www.youtube.com/playlist?list=PLuHgQVnccGMCzOGBzSdxHSMW1_MkBLmHc",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "beginner",
            "description": "파이썬 기초 강의",
            "estimated_hours": 10,
        },
    ],
    "rest api": [
        {
            "title": "REST API 제대로 알고 사용하기",
            "url": "https://meetup.nhncloud.com/posts/92",
            "type": "article",
            "platform": "Docs",
            "difficulty": "beginner",
            "description": "REST API 설계 원칙 한글 가이드",
            "estimated_hours": 3,
        },
    ],
}

# 데이터베이스 리소스
DATABASE_RESOURCES: Dict[str, List[Dict[str, Any]]] = {
    "sql": [
        {
            "title": "생활코딩 SQL",
            "url": "https://www.youtube.com/playlist?list=PLuHgQVnccGMCgrP_9HL3dAcvdt8qOZxjW",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "beginner",
            "description": "SQL 기초 쿼리 학습",
            "estimated_hours": 8,
        },
        {
            "title": "SQL 첫걸음 - 인프런",
            "url": "https://www.inflearn.com/course/sql-first-step",
            "type": "course",
            "platform": "Inflearn",
            "difficulty": "beginner",
            "description": "SQL 기초 무료 강의",
            "estimated_hours": 10,
        },
    ],
    "postgresql": [
        {
            "title": "PostgreSQL 공식 튜토리얼",
            "url": "https://www.postgresql.org/docs/current/tutorial.html",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "intermediate",
            "description": "PostgreSQL 공식 가이드",
            "estimated_hours": 12,
        },
    ],
    "mongodb": [
        {
            "title": "MongoDB University (한글 자막)",
            "url": "https://learn.mongodb.com/",
            "type": "course",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "MongoDB 무료 온라인 강의",
            "estimated_hours": 15,
        },
        {
            "title": "생활코딩 MongoDB",
            "url": "https://www.youtube.com/playlist?list=PLuHgQVnccGMBjM7HU3kKV_oNu8a3eHUj1",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "beginner",
            "description": "MongoDB 기초 강의",
            "estimated_hours": 6,
        },
    ],
    "redis": [
        {
            "title": "Redis 공식 문서",
            "url": "https://redis.io/docs/",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "intermediate",
            "description": "Redis 기본 사용법",
            "estimated_hours": 8,
        },
    ],
}

# 도구 및 인프라 리소스
TOOLS_RESOURCES: Dict[str, List[Dict[str, Any]]] = {
    "git": [
        {
            "title": "생활코딩 Git",
            "url": "https://www.youtube.com/playlist?list=PLuHgQVnccGMATJK16UJ9Fjay0ozrSZKiI",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "beginner",
            "description": "Git 기초 완벽 가이드",
            "estimated_hours": 6,
        },
        {
            "title": "Git 공식 문서 (한글)",
            "url": "https://git-scm.com/book/ko/v2",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "Pro Git 한글판",
            "estimated_hours": 15,
        },
    ],
    "docker": [
        {
            "title": "생활코딩 Docker",
            "url": "https://www.youtube.com/playlist?list=PLuHgQVnccGMDeMJsGq2O-55Ymtx0IdKWf",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "intermediate",
            "description": "Docker 입문 강의",
            "estimated_hours": 8,
        },
        {
            "title": "Docker 공식 문서",
            "url": "https://docs.docker.com/get-started/",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "intermediate",
            "description": "Docker 시작하기",
            "estimated_hours": 10,
        },
    ],
    "kubernetes": [
        {
            "title": "Kubernetes 공식 튜토리얼 (한글)",
            "url": "https://kubernetes.io/ko/docs/tutorials/",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "advanced",
            "description": "Kubernetes 기초",
            "estimated_hours": 20,
        },
    ],
    "aws": [
        {
            "title": "AWS 시작 가이드 (한글)",
            "url": "https://aws.amazon.com/ko/getting-started/",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "intermediate",
            "description": "AWS 클라우드 서비스 입문",
            "estimated_hours": 15,
        },
    ],
    "testing": [
        {
            "title": "Jest 공식 문서 (한글)",
            "url": "https://jestjs.io/docs/getting-started",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "intermediate",
            "description": "Jest 테스팅 프레임워크",
            "estimated_hours": 8,
        },
    ],
}

# 상태관리 리소스
STATE_MANAGEMENT_RESOURCES: Dict[str, List[Dict[str, Any]]] = {
    "redux": [
        {
            "title": "Redux 공식 튜토리얼",
            "url": "https://ko.redux.js.org/tutorials/essentials/part-1-overview-concepts",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "intermediate",
            "description": "Redux Toolkit 완벽 가이드",
            "estimated_hours": 10,
        },
    ],
    "zustand": [
        {
            "title": "Zustand 공식 문서",
            "url": "https://github.com/pmndrs/zustand",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "Zustand 상태관리 라이브러리",
            "estimated_hours": 4,
        },
    ],
}

# 배포 및 인프라 리소스
DEPLOYMENT_RESOURCES: Dict[str, List[Dict[str, Any]]] = {
    "deployment": [
        {
            "title": "Vercel 배포 가이드",
            "url": "https://vercel.com/docs",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "Vercel을 사용한 배포 완벽 가이드",
            "estimated_hours": 4,
        },
        {
            "title": "Netlify 배포 가이드",
            "url": "https://docs.netlify.com/",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "Netlify로 프론트엔드 배포하기",
            "estimated_hours": 3,
        },
        {
            "title": "생활코딩 배포",
            "url": "https://www.youtube.com/watch?v=AXQ7HoJAUPM",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "beginner",
            "description": "웹 애플리케이션 배포 기초",
            "estimated_hours": 2,
        },
    ],
    "vercel": [
        {
            "title": "Vercel 배포 가이드",
            "url": "https://vercel.com/docs",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "Vercel을 사용한 배포 완벽 가이드",
            "estimated_hours": 4,
        },
    ],
    "netlify": [
        {
            "title": "Netlify 배포 가이드",
            "url": "https://docs.netlify.com/",
            "type": "documentation",
            "platform": "Official",
            "difficulty": "beginner",
            "description": "Netlify로 프론트엔드 배포하기",
            "estimated_hours": 3,
        },
    ],
}

# 포트폴리오 및 이력서 리소스
CAREER_RESOURCES: Dict[str, List[Dict[str, Any]]] = {
    "portfolio": [
        {
            "title": "개발자 포트폴리오 만들기 - 드림코딩",
            "url": "https://www.youtube.com/watch?v=LKe8TBHQa_w",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "beginner",
            "description": "효과적인 개발자 포트폴리오 작성법",
            "estimated_hours": 2,
        },
        {
            "title": "주니어 개발자 포트폴리오 최적화",
            "url": "https://yozm.wishket.com/magazine/detail/1687/",
            "type": "article",
            "platform": "Docs",
            "difficulty": "beginner",
            "description": "주니어 개발자를 위한 포트폴리오 가이드",
            "estimated_hours": 1,
        },
        {
            "title": "노마드코더 포트폴리오 Tips",
            "url": "https://www.youtube.com/watch?v=oKlYAi48raY",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "beginner",
            "description": "개발자 포트폴리오 작성 팁",
            "estimated_hours": 1,
        },
    ],
    "resume": [
        {
            "title": "개발자 이력서 작성법 - 원티드",
            "url": "https://www.wanted.co.kr/events/22_11_s01_b01",
            "type": "article",
            "platform": "Docs",
            "difficulty": "beginner",
            "description": "합격하는 개발자 이력서 작성법",
            "estimated_hours": 2,
        },
        {
            "title": "주니어 개발자 이력서 작성 - 드림코딩",
            "url": "https://www.youtube.com/watch?v=USSW-KJfkv0",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "beginner",
            "description": "신입 개발자 이력서 작성 가이드",
            "estimated_hours": 1,
        },
        {
            "title": "개발자 이력서 작성 베스트 프랙티스",
            "url": "https://github.com/JSpiner/RESUME",
            "type": "article",
            "platform": "GitHub",
            "difficulty": "beginner",
            "description": "개발자 이력서 템플릿 및 작성법",
            "estimated_hours": 2,
        },
    ],
    "interview": [
        {
            "title": "프론트엔드 면접 질문 모음",
            "url": "https://github.com/h5bp/Front-end-Developer-Interview-Questions",
            "type": "article",
            "platform": "GitHub",
            "difficulty": "intermediate",
            "description": "프론트엔드 개발자 면접 질문 핸드북",
            "estimated_hours": 10,
        },
        {
            "title": "JavaScript 면접 준비",
            "url": "https://github.com/yangshun/front-end-interview-handbook",
            "type": "article",
            "platform": "GitHub",
            "difficulty": "intermediate",
            "description": "프론트엔드 면접 핸드북 (한글 포함)",
            "estimated_hours": 8,
        },
        {
            "title": "코딩 테스트 준비 - 프로그래머스",
            "url": "https://programmers.co.kr/learn/challenges",
            "type": "tutorial",
            "platform": "Docs",
            "difficulty": "intermediate",
            "description": "코딩 테스트 문제 풀이",
            "estimated_hours": 20,
        },
        {
            "title": "개발자 면접 준비 - 노마드코더",
            "url": "https://www.youtube.com/watch?v=M51L_J5Fy9E",
            "type": "video",
            "platform": "YouTube",
            "difficulty": "beginner",
            "description": "개발자 면접 팁과 노하우",
            "estimated_hours": 2,
        },
    ],
}

# 전체 리소스 통합
TECH_RESOURCES: Dict[str, List[Dict[str, Any]]] = {
    **FRONTEND_RESOURCES,
    **BACKEND_RESOURCES,
    **DATABASE_RESOURCES,
    **TOOLS_RESOURCES,
    **STATE_MANAGEMENT_RESOURCES,
    **DEPLOYMENT_RESOURCES,
    **CAREER_RESOURCES,
}


# ============================================================================
# 리소스 검색 헬퍼
# ============================================================================


def get_resources_for_keyword(keyword: str) -> List[LearningResource]:
    """기술 키워드에 맞는 학습 리소스 반환 (고퀄리티 한국어 리소스)"""
    normalized = keyword.lower().strip()

    # 직접 매칭
    if normalized in TECH_RESOURCES:
        return [
            LearningResource(
                title=res["title"],
                url=res["url"],
                type=res["type"],
                platform=res["platform"],
                difficulty=res["difficulty"],
                description=res.get("description"),
                estimated_hours=res.get("estimated_hours"),
            )
            for res in TECH_RESOURCES[normalized]
        ]

    # 부분 매칭 (예: "react hooks" -> "react")
    for tech, resources in TECH_RESOURCES.items():
        if tech in normalized or normalized in tech:
            return [
                LearningResource(
                    title=res["title"],
                    url=res["url"],
                    type=res["type"],
                    platform=res["platform"],
                    difficulty=res["difficulty"],
                    description=res.get("description"),
                    estimated_hours=res.get("estimated_hours"),
                )
                for res in resources
            ]

    # 매칭되지 않으면 빈 리스트 반환 (구글 검색 링크 제거)
    logger.warning(f"No predefined resources found for keyword: {keyword}")
    return []


# ============================================================================
# OpenAI 클라이언트
# ============================================================================


def get_openai_client() -> OpenAI:
    """OpenAI 클라이언트 생성"""
    return OpenAI(api_key=settings.OPENAI_API_KEY)


# ============================================================================
# 로드맵 생성 프롬프트 (고도화 버전)
# ============================================================================


def build_roadmap_prompt(
    gap_analysis: Dict[str, Any],
    target_weeks: int,
    resume_text: str,
    jd_text: str,
) -> str:
    """로드맵 생성을 위한 전략적 프롬프트 구성"""
    match_result = gap_analysis.get("match_result", {})
    match_score = match_result.get("match_score", 0)
    match_grade = match_result.get("match_grade", "D")
    feedback = gap_analysis.get("feedback", {})
    weaknesses = gap_analysis.get("weaknesses", [])
    strengths = gap_analysis.get("strengths", [])

    # 개선 필요 섹션 추출
    improvement_sections = [w["section"] for w in weaknesses] if weaknesses else []
    strong_sections = [s["section"] for s in strengths] if strengths else []

    # 액션 아이템 추출
    action_items = feedback.get("action_items", [])

    # 등급별 전략 설정
    grade_strategy = {
        "D": "기초 강화형 로드맵: 해당 분야의 기초부터 차근차근 다져나가는 커리큘럼을 구성하세요. 첫 2주는 기본 개념 이해에 집중하고, 이후 점진적으로 난이도를 높입니다.",
        "C": "핵심 역량 보완형 로드맵: 부족한 핵심 기술에 집중하되, 기존 강점을 활용하여 빠르게 성장할 수 있는 전략을 세우세요.",
        "B": "실전 프로젝트형 로드맵: 이미 기초는 갖춘 상태이므로, 실전 프로젝트를 통해 경험을 쌓는 데 집중하세요.",
        "A": "심화 및 최적화형 로드맵: 고급 기술과 베스트 프랙티스를 학습하여 전문성을 높이는 데 집중하세요.",
        "S": "전문가 수준 유지형 로드맵: 최신 트렌드와 고급 아키텍처 패턴을 학습하여 경쟁력을 유지하세요.",
    }

    strategy = grade_strategy.get(match_grade, grade_strategy["C"])

    # 프론트엔드-백엔드 브릿지 전략
    bridge_strategy = ""
    # JD에서 백엔드 키워드 검출
    backend_keywords = ["backend", "server", "api", "database", "node", "express", "django", "fastapi", "spring"]
    jd_is_backend_focused = any(keyword in jd_text.lower() for keyword in backend_keywords)

    # 이력서에서 프론트엔드 키워드 검출
    frontend_keywords = ["frontend", "react", "vue", "angular", "ui", "ux", "css", "html"]
    resume_is_frontend = any(keyword in resume_text.lower() for keyword in frontend_keywords)

    if resume_is_frontend and jd_is_backend_focused:
        bridge_strategy = """
**🔗 프론트엔드-백엔드 브릿지 전략 (중요!)**
이 로드맵은 프론트엔드 개발자가 백엔드 역량을 보완하는 과정입니다.
- **1-2주차**: 반드시 'REST API 설계 원칙', '데이터 구조 이해', 'HTTP 통신 심화' 등 프론트엔드 개발자를 위한 백엔드 협업 지식을 포함하세요.
- **학습 방향**: 백엔드를 전문적으로 깊게 파기보다는, 프론트엔드 개발자가 백엔드와 효율적으로 협업하고 API를 이해할 수 있는 수준을 목표로 합니다.
- **실전 프로젝트**: 간단한 CRUD API를 직접 만들어보며 백엔드 로직을 체험하세요.
"""

    prompt = f"""당신은 주니어 개발자를 위한 전문 커리어 코치입니다.
사용자의 이력서와 목표 채용공고 간의 스킬 갭을 분석한 결과를 바탕으로,
실행 가능한 {target_weeks}주 학습 로드맵을 생성해주세요.

## 현재 상황 분석
- **매칭 점수**: {match_score:.1f}점 ({match_grade}등급)
- **강점 영역**: {', '.join(strong_sections) if strong_sections else '분석 필요'}
- **개선 필요 영역 (중요!)**: {', '.join(improvement_sections) if improvement_sections else '없음'}

## 피드백 요약
{feedback.get('summary', '분석 결과 없음')}

## 핵심 액션 아이템 (반드시 로드맵에 반영!)
{chr(10).join(f'- {item}' for item in action_items) if action_items else '- 없음'}

{bridge_strategy}

## 등급별 로드맵 전략
{strategy}

## 이력서 (현재 역량) - 처음 500자
```
{resume_text[:500]}...
```

## 채용공고 (목표 요구사항) - 처음 500자
```
{jd_text[:500]}...
```

## 로드맵 생성 핵심 원칙

1. **부족한 기술 중심 (70% 이상)**:
   - 개선 필요 영역({', '.join(improvement_sections)})에 주차별 계획의 최소 70%를 할애하세요.
   - 강점 영역은 간단히 복습하는 수준으로만 포함합니다.

2. **실용성과 구체성**:
   - 주니어 개발자가 실제로 따라할 수 있는 구체적인 학습 계획
   - 각 주차마다 명확한 학습 목표와 체크 가능한 태스크

3. **프론트엔드 관점 (사용자는 프론트엔드 지망생)**:
   - React 지망생이 이해하기 쉬운 비유와 설명 사용
   - 프론트엔드 개발자의 관점에서 백엔드 기술을 설명

4. **점진적 난이도**:
   - 기초부터 심화까지 단계적으로 구성
   - 주차가 진행될수록 프로젝트 난이도 상승

5. **프로젝트 중심**:
   - 각 주차마다 실습 가능한 프로젝트 예시 포함
   - 포트폴리오에 추가할 수 있는 실전 프로젝트 제안

## 출력 형식 (JSON)

다음 JSON 스키마로 응답해주세요:

{{
  "total_weeks": {target_weeks},
  "match_grade": "{match_grade}",
  "target_grade": "A",
  "summary": "로드맵 전략 및 목표 요약 (3-4문장, 동기부여가 되는 톤)",
  "key_improvement_areas": {json.dumps(improvement_sections, ensure_ascii=False)},
  "weekly_plan": [
    {{
      "week_number": 1,
      "title": "주차 제목 (예: TypeScript 기초 완성하기)",
      "duration": "1 week",
      "description": "이번 주 학습 목표와 내용을 프론트엔드 관점에서 친절하게 설명 (3-4문장, 왜 중요한지 포함)",
      "keywords": ["typescript", "javascript"],
      "tasks": [
        {{
          "task": "TypeScript 공식 핸드북 1-5장 학습 및 실습",
          "completed": false,
          "priority": "high"
        }},
        {{
          "task": "간단한 Todo 앱을 TypeScript로 리팩토링",
          "completed": false,
          "priority": "high"
        }},
        {{
          "task": "TypeScript 타입 추론 연습 문제 10개 풀기",
          "completed": false,
          "priority": "medium"
        }}
      ]
    }},
    ...
  ]
}}

**중요 제약사항**:
- tasks는 주차당 3-5개로 제한 (너무 많으면 압도됨)
- keywords는 반드시 **소문자로만** 작성하고, 프론트엔드 아이콘 라이브러리(react-icons, simple-icons)와 호환되는 표준 단어를 사용하세요
  - ✅ 좋은 예: "react", "typescript", "javascript", "html", "css", "git", "docker", "api", "deployment", "portfolio", "resume", "interview"
  - ❌ 나쁜 예: "React", "TypeScript", "type system" (대문자나 공백 포함)
  - 개선 필요 영역의 기술이 keywords에 반드시 포함되어야 함
  - 주차당 keywords는 2-4개로 제한 (핵심 기술만)
- description은 친절하고 동기부여가 되는 톤으로 작성
- 유효한 JSON만 반환 (주석이나 추가 텍스트 없이)
"""

    return prompt


# ============================================================================
# 로드맵 생성 함수
# ============================================================================


def generate_roadmap_with_llm(
    gap_analysis: Dict[str, Any],
    target_weeks: int,
    resume_text: str,
    jd_text: str,
) -> Dict[str, Any]:
    """
    GPT-4o mini를 사용하여 전략적 맞춤형 로드맵 생성

    Args:
        gap_analysis: 스킬 갭 분석 결과
        target_weeks: 목표 학습 주차
        resume_text: 이력서 전체 텍스트
        jd_text: JD 전체 텍스트

    Returns:
        로드맵 JSON 데이터
    """
    try:
        client = get_openai_client()
        prompt = build_roadmap_prompt(gap_analysis, target_weeks, resume_text, jd_text)

        logger.info(f"Generating strategic roadmap with GPT-4o mini (target: {target_weeks} weeks)")

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "당신은 주니어 개발자의 커리어 성장을 돕는 전문 코치입니다. 스킬 갭을 전략적으로 메우는 로드맵을 생성하며, 항상 유효한 JSON만 반환합니다.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=settings.LLM_TEMPERATURE,
            response_format={"type": "json_object"},
        )

        # JSON 파싱
        roadmap_json = json.loads(response.choices[0].message.content)
        logger.info(f"Roadmap generated: {roadmap_json.get('total_weeks')} weeks, "
                   f"{len(roadmap_json.get('weekly_plan', []))} weeks planned")

        return roadmap_json

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        raise ValueError("LLM returned invalid JSON")

    except Exception as e:
        logger.error(f"Error generating roadmap with LLM: {e}", exc_info=True)
        raise


def normalize_keyword(keyword: str) -> str:
    """
    키워드 정규화 (프론트엔드 아이콘 매핑용)

    - 소문자 변환
    - 공백 제거 또는 하이픈으로 변환
    - 특수문자 제거
    """
    # 소문자 변환
    keyword = keyword.lower().strip()

    # 공백을 하이픈으로 변환 (예: "rest api" -> "rest-api")
    # 단, 일부 키워드는 공백 제거 (예: "type system" -> "typescript")
    if " " in keyword:
        # 특별 케이스 처리
        replacements = {
            "rest api": "api",
            "type system": "typescript",
            "state management": "redux",
            "web api": "api",
            "front end": "frontend",
            "back end": "backend",
        }
        if keyword in replacements:
            keyword = replacements[keyword]
        else:
            # 일반적으로는 하이픈으로 변환하지 않고 공백 제거
            keyword = keyword.replace(" ", "")

    # 점(.) 제거 (예: "next.js" -> "nextjs")
    keyword = keyword.replace(".", "")

    return keyword


def enrich_roadmap_with_resources(roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    로드맵에 키워드 기반 고퀄리티 학습 리소스 추가

    키워드 정규화 및 리소스 자동 매핑

    Args:
        roadmap_data: LLM이 생성한 로드맵 JSON

    Returns:
        리소스가 추가된 로드맵 JSON
    """
    weekly_plan = roadmap_data.get("weekly_plan", [])

    for week in weekly_plan:
        keywords = week.get("keywords", [])

        # 키워드 정규화 (소문자 변환, 공백 제거)
        normalized_keywords = [normalize_keyword(kw) for kw in keywords]
        week["keywords"] = normalized_keywords

        resources = []

        # 각 키워드별 리소스 수집 (중복 제거)
        seen_urls = set()
        for keyword in normalized_keywords:
            keyword_resources = get_resources_for_keyword(keyword)
            for resource in keyword_resources:
                if resource.url not in seen_urls:
                    resources.append(resource.model_dump())
                    seen_urls.add(resource.url)

        # 난이도별 정렬 (beginner -> intermediate -> advanced)
        difficulty_order = {"beginner": 1, "intermediate": 2, "advanced": 3}
        resources.sort(key=lambda r: difficulty_order.get(r.get("difficulty", "intermediate"), 2))

        # 최대 6개로 제한 (초급 2개, 중급 2개, 고급 2개 정도)
        week["resources"] = resources[:6]

    return roadmap_data


# ============================================================================
# 메인 서비스 함수
# ============================================================================


def generate_roadmap(
    resume_id: UUID,
    jd_id: UUID,
    target_weeks: int = 8,
    retriever: Optional[DocumentRetriever] = None,
) -> RoadmapData:
    """
    맞춤형 학습 로드맵 생성 (고도화 버전)

    Args:
        resume_id: 이력서 문서 ID
        jd_id: JD 문서 ID
        target_weeks: 목표 학습 기간 (주)
        retriever: DocumentRetriever 인스턴스

    Returns:
        RoadmapData
    """
    if retriever is None:
        retriever = get_retriever()

    logger.info(f"Generating strategic roadmap: resume={resume_id}, jd={jd_id}, weeks={target_weeks}")

    # 1. 스킬 갭 분석 (기존 retriever 활용)
    from app.core.rag.vector_store import get_vector_store

    vector_store = get_vector_store()
    resume_doc = vector_store.get_document_by_id(resume_id)
    jd_doc = vector_store.get_document_by_id(jd_id)

    if not resume_doc or not jd_doc:
        raise ValueError("Document not found")

    resume_file_id = UUID(resume_doc.get("file_id"))
    jd_file_id = UUID(jd_doc.get("file_id"))

    resume_text = resume_doc.get("cleaned_text") or resume_doc.get("text_content", "")
    jd_text = jd_doc.get("cleaned_text") or jd_doc.get("text_content", "")

    gap_analysis = analyze_skill_gaps(
        resume_file_id=resume_file_id,
        jd_file_id=jd_file_id,
        resume_text=resume_text,
        jd_text=jd_text,
        retriever=retriever,
    )

    logger.info(f"Gap analysis completed: grade={gap_analysis.get('match_result', {}).get('match_grade')}, "
               f"weaknesses={len(gap_analysis.get('weaknesses', []))}")

    # 2. GPT-4o mini로 전략적 로드맵 생성
    roadmap_json = generate_roadmap_with_llm(
        gap_analysis=gap_analysis,
        target_weeks=target_weeks,
        resume_text=resume_text,
        jd_text=jd_text,
    )

    # 3. 키워드 기반 고퀄리티 리소스 추가
    roadmap_json = enrich_roadmap_with_resources(roadmap_json)

    # 4. Pydantic 모델로 변환
    roadmap_data = RoadmapData(**roadmap_json)

    logger.info(f"Strategic roadmap generation completed: {roadmap_data.total_weeks} weeks, "
               f"{len(roadmap_data.weekly_plan)} weeks planned, "
               f"target grade: {roadmap_data.target_grade}")

    return roadmap_data

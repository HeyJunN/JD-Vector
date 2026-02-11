"""
Custom CORS Middleware for Vercel deployments
Vercel 배포 URL 패턴을 자동으로 인식하여 CORS를 허용합니다.
"""

import re
from typing import List
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SmartCORSMiddleware(BaseHTTPMiddleware):
    """
    Vercel 도메인 패턴을 자동으로 인식하는 스마트 CORS 미들웨어

    허용되는 패턴:
    - localhost (개발 환경)
    - *.vercel.app (Vercel 배포)
    - 환경 변수로 지정된 특정 도메인
    """

    def __init__(
        self,
        app,
        allowed_origins: List[str],
        allow_credentials: bool = True,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
    ):
        super().__init__(app)
        self.allowed_origins = allowed_origins
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods or ["*"]
        self.allow_headers = allow_headers or ["*"]

        # Vercel 도메인 패턴 (정규식)
        self.vercel_pattern = re.compile(
            r'^https?://[a-zA-Z0-9-]+\.vercel\.app$'
        )

    def is_origin_allowed(self, origin: str) -> bool:
        """
        Origin이 허용되는지 확인
        1. 명시적으로 허용된 origins 리스트에 있는지 확인
        2. Vercel 도메인 패턴과 일치하는지 확인
        """
        if not origin:
            return False

        # 1. 명시적으로 허용된 origins
        if origin in self.allowed_origins:
            return True

        # 2. Vercel 도메인 패턴 매칭
        if self.vercel_pattern.match(origin):
            return True

        return False

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")

        # Preflight 요청 처리 (OPTIONS)
        if request.method == "OPTIONS":
            if origin and self.is_origin_allowed(origin):
                return Response(
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Credentials": str(self.allow_credentials).lower(),
                        "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
                        "Access-Control-Allow-Headers": ", ".join(self.allow_headers),
                        "Access-Control-Max-Age": "600",  # 10분간 preflight 캐싱
                    },
                )

        # 실제 요청 처리
        response = await call_next(request)

        # CORS 헤더 추가
        if origin and self.is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = str(self.allow_credentials).lower()
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)

        return response


def get_allowed_origins_from_csv(origins_csv: str) -> List[str]:
    """
    쉼표로 구분된 origins 문자열을 리스트로 변환
    공백 제거 및 빈 문자열 필터링

    Args:
        origins_csv: 쉼표로 구분된 origins 문자열

    Returns:
        정제된 origins 리스트
    """
    if not origins_csv:
        return []

    origins = [origin.strip() for origin in origins_csv.split(",")]
    return [origin for origin in origins if origin]  # 빈 문자열 제거

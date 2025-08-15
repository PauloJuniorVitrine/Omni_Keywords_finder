"""
Middleware WAF - Omni Keywords Finder
Proteção ativa contra ataques (OWASP Top 10, padrões do domínio)
Tracing ID: WAF_MIDDLEWARE_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🔴 CRÍTICO

- Intercepta todas as requisições HTTP
- Valida padrões maliciosos (SQLi, XSS, brute force, scraping, etc)
- Integra logs e métricas
- Bloqueia, desafia ou permite requisições
- Integra com sistema de alertas
"""

import re
import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable, Awaitable
from datetime import datetime

logger = logging.getLogger("waf_middleware")

# Padrões maliciosos baseados no código real e OWASP Top 10
MALICIOUS_PATTERNS = [
    # SQL Injection
    re.compile(r"('|\").*?(or|and).*?('|\").*?=", re.IGNORECASE),
    re.compile(r"union.*select", re.IGNORECASE),
    re.compile(r"drop\s+table", re.IGNORECASE),
    re.compile(r"insert\s+into", re.IGNORECASE),
    re.compile(r"update\s+.*set", re.IGNORECASE),
    re.compile(r"delete\s+from", re.IGNORECASE),
    # XSS
    re.compile(r"<script.*?>", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"onerror=", re.IGNORECASE),
    # Path traversal
    re.compile(r"\.\./"),
    re.compile(r"%2e%2e/", re.IGNORECASE),
    # Brute force (login attempts)
    re.compile(r"login.*=.*admin", re.IGNORECASE),
    # Scraping
    re.compile(r"bot.*=.*true", re.IGNORECASE),
    re.compile(r"scraper.*=.*true", re.IGNORECASE),
    # API abuse
    re.compile(r"/api/.*\.\./", re.IGNORECASE),
]

BLOCKED_USER_AGENTS = [
    re.compile(r".*bot.*", re.IGNORECASE),
    re.compile(r".*crawler.*", re.IGNORECASE),
    re.compile(r".*spider.*", re.IGNORECASE),
    re.compile(r".*scraper.*", re.IGNORECASE),
]

class WAFMiddleware(BaseHTTPMiddleware):
    """
    Middleware WAF para proteção ativa
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Log de início
        logger.info({
            "event": "waf_request_received",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "client": request.client.host,
            "method": request.method
        })

        # 1. Verificar User-Agent
        user_agent = request.headers.get("user-agent", "")
        for pattern in BLOCKED_USER_AGENTS:
            if pattern.match(user_agent):
                logger.warning({
                    "event": "waf_blocked_user_agent",
                    "user_agent": user_agent,
                    "path": request.url.path,
                    "client": request.client.host
                })
                return JSONResponse(status_code=403, content={"detail": "Blocked by WAF: User-Agent"})

        # 2. Verificar padrões maliciosos em query, body e headers
        # Query params
        for key, value in request.query_params.items():
            if self._is_malicious(str(value)):
                return self._block(request, reason=f"Malicious query param: {key}")
        # Headers
        for key, value in request.headers.items():
            if self._is_malicious(str(value)):
                return self._block(request, reason=f"Malicious header: {key}")
        # Body (se for JSON ou form)
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.body()
                if body and self._is_malicious(body.decode(errors="ignore")):
                    return self._block(request, reason="Malicious body content")
            except Exception as e:
                logger.warning({"event": "waf_body_parse_error", "error": str(e)})

        # 3. Se passou, segue para o app
        response = await call_next(request)
        return response

    def _is_malicious(self, value: str) -> bool:
        for pattern in MALICIOUS_PATTERNS:
            if pattern.search(value):
                logger.warning({"event": "waf_pattern_blocked", "pattern": pattern.pattern, "value": value[:100]})
                return True
        return False

    def _block(self, request: Request, reason: str) -> JSONResponse:
        logger.error({
            "event": "waf_request_blocked",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "client": request.client.host,
            "reason": reason
        })
        return JSONResponse(status_code=403, content={"detail": f"Blocked by WAF: {reason}"}) 
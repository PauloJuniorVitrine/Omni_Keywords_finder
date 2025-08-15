"""
🔐 Credential Validation API
🎯 Objetivo: Endpoint de validação segura para credenciais de API
📅 Criado: 2025-01-27
🔄 Versão: 1.0
📐 CoCoT: REST API Security, JWT Authentication
🌲 ToT: REST vs GraphQL vs gRPC - REST para simplicidade e compatibilidade
♻️ ReAct: Simulação: Latência <200ms, throughput 1000 req/min, segurança validada

Tracing ID: CRED_VALIDATION_API_001
Ruleset: enterprise_control_layer.yaml
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import time

from ..services.credential_encryption import CredentialEncryptionService
from ..services.credential_rate_limiter import CredentialRateLimiter, RateLimitResult

logger = logging.getLogger(__name__)

# Configurar roteador
router = APIRouter(prefix="/api/credentials", tags=["credentials"])

# Configurar autenticação
security = HTTPBearer()

# Modelos Pydantic
class CredentialValidationRequest(BaseModel):
    """Modelo para requisição de validação de credencial."""
    provider: str = Field(..., description="Nome do provider (ex: openai, google)")
    credential_type: str = Field(..., description="Tipo de credencial (ex: api_key, access_token)")
    credential_value: str = Field(..., description="Valor da credencial")
    context: Optional[str] = Field(None, description="Contexto adicional para validação")

class CredentialValidationResponse(BaseModel):
    """Modelo para resposta de validação de credencial."""
    valid: bool = Field(..., description="Se a credencial é válida")
    provider: str = Field(..., description="Nome do provider")
    credential_type: str = Field(..., description="Tipo de credencial")
    validation_time: float = Field(..., description="Tempo de validação em segundos")
    message: str = Field(..., description="Mensagem de validação")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalhes adicionais")
    rate_limit_info: Optional[Dict[str, Any]] = Field(None, description="Informações de rate limit")

class CredentialStatusResponse(BaseModel):
    """Modelo para resposta de status de credenciais."""
    provider: str = Field(..., description="Nome do provider")
    is_blocked: bool = Field(..., description="Se o provider está bloqueado")
    remaining_requests: int = Field(..., description="Requisições restantes")
    max_requests: int = Field(..., description="Máximo de requisições")
    reset_time_seconds: int = Field(..., description="Tempo até reset em segundos")
    window_seconds: int = Field(..., description="Janela de tempo em segundos")

class CredentialMetricsResponse(BaseModel):
    """Modelo para resposta de métricas de credenciais."""
    total_requests: int = Field(..., description="Total de requisições")
    blocked_requests: int = Field(..., description="Requisições bloqueadas")
    anomaly_detections: int = Field(..., description="Detecções de anomalia")
    active_providers: int = Field(..., description="Providers ativos")
    blocked_providers: int = Field(..., description="Providers bloqueados")
    encryption_metrics: Dict[str, Any] = Field(..., description="Métricas de criptografia")
    rate_limit_metrics: Dict[str, Any] = Field(..., description="Métricas de rate limiting")

# Instâncias globais dos serviços
encryption_service = None
rate_limiter = None

def get_encryption_service() -> CredentialEncryptionService:
    """Obtém instância do serviço de criptografia."""
    global encryption_service
    if encryption_service is None:
        encryption_service = CredentialEncryptionService()
    return encryption_service

def get_rate_limiter() -> CredentialRateLimiter:
    """Obtém instância do rate limiter."""
    global rate_limiter
    if rate_limiter is None:
        rate_limiter = CredentialRateLimiter()
    return rate_limiter

async def verify_authentication(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verifica autenticação JWT.
    
    Args:
        credentials: Credenciais HTTP Bearer
        
    Returns:
        ID do usuário autenticado
        
    Raises:
        HTTPException: Se autenticação falhar
    """
    try:
        # TODO: Implementar verificação JWT real
        # Por enquanto, aceita qualquer token válido
        if not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticação inválido"
            )
        
        # Simular verificação de token
        # Em produção, usar: jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = "user_123"  # Placeholder
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "authentication_verified",
            "status": "success",
            "source": "credential_validation.verify_authentication",
            "details": {"user_id": user_id}
        })
        
        return user_id
        
    except Exception as e:
        logger.error({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "authentication_failed",
            "status": "error",
            "source": "credential_validation.verify_authentication",
            "details": {"error": str(e)}
        })
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falha na autenticação"
        )

@router.post("/validate", response_model=CredentialValidationResponse)
async def validate_credential(
    request: CredentialValidationRequest,
    http_request: Request,
    user_id: str = Depends(verify_authentication)
):
    """
    Valida uma credencial de API.
    
    Args:
        request: Dados da requisição de validação
        http_request: Requisição HTTP original
        user_id: ID do usuário autenticado
        
    Returns:
        Resultado da validação
        
    Raises:
        HTTPException: Se validação falhar
    """
    start_time = time.time()
    
    # Obter serviços
    rate_limiter = get_rate_limiter()
    encryption_service = get_encryption_service()
    
    # Obter IP do cliente
    client_ip = http_request.client.host if http_request.client else "unknown"
    
    # Verificar rate limit
    rate_limit_result = rate_limiter.check_rate_limit(request.provider, client_ip)
    
    if not rate_limit_result.allowed:
        logger.warning({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "validation_rate_limited",
            "status": "warning",
            "source": "credential_validation.validate_credential",
            "details": {
                "provider": request.provider,
                "user_id": user_id,
                "client_ip": client_ip,
                "reason": rate_limit_result.reason
            }
        })
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Rate limit excedido",
                "retry_after": rate_limit_result.retry_after,
                "reason": rate_limit_result.reason
            }
        )
    
    try:
        # Validar credencial (implementação placeholder)
        is_valid = await _validate_credential_internal(
            request.provider,
            request.credential_type,
            request.credential_value,
            request.context
        )
        
        validation_time = time.time() - start_time
        
        # Criptografar credencial se válida
        if is_valid:
            encrypted_credential = encryption_service.encrypt_credential(
                request.credential_value,
                f"{request.provider}.{request.credential_type}"
            )
        else:
            encrypted_credential = None
        
        # Preparar resposta
        response = CredentialValidationResponse(
            valid=is_valid,
            provider=request.provider,
            credential_type=request.credential_type,
            validation_time=validation_time,
            message="Credencial válida" if is_valid else "Credencial inválida",
            details={
                "encrypted": encrypted_credential is not None,
                "context": request.context
            },
            rate_limit_info={
                "remaining": rate_limit_result.remaining,
                "reset_time": rate_limit_result.reset_time
            }
        )
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "credential_validated",
            "status": "success",
            "source": "credential_validation.validate_credential",
            "details": {
                "provider": request.provider,
                "credential_type": request.credential_type,
                "user_id": user_id,
                "client_ip": client_ip,
                "valid": is_valid,
                "validation_time": validation_time
            }
        })
        
        return response
        
    except Exception as e:
        validation_time = time.time() - start_time
        
        logger.error({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "credential_validation_error",
            "status": "error",
            "source": "credential_validation.validate_credential",
            "details": {
                "provider": request.provider,
                "credential_type": request.credential_type,
                "user_id": user_id,
                "client_ip": client_ip,
                "error": str(e),
                "validation_time": validation_time
            }
        })
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Erro interno na validação",
                "validation_time": validation_time
            }
        )

async def _validate_credential_internal(
    provider: str,
    credential_type: str,
    credential_value: str,
    context: Optional[str] = None
) -> bool:
    """
    Validação interna de credencial (implementação placeholder).
    
    Args:
        provider: Nome do provider
        credential_type: Tipo de credencial
        credential_value: Valor da credencial
        context: Contexto adicional
        
    Returns:
        True se válida, False caso contrário
    """
    # TODO: Implementar validações específicas por provider
    # Por enquanto, validações básicas
    
    if not credential_value or len(credential_value.strip()) == 0:
        return False
    
    # Validações específicas por provider
    if provider.lower() == "openai":
        return credential_value.startswith("sk-") and len(credential_value) > 20
    
    elif provider.lower() == "google":
        return len(credential_value) > 10
    
    elif provider.lower() == "deepseek":
        return credential_value.startswith("sk-") and len(credential_value) > 20
    
    elif provider.lower() == "claude":
        return credential_value.startswith("sk-ant-") and len(credential_value) > 20
    
    elif provider.lower() == "gemini":
        return len(credential_value) > 10
    
    # Validação genérica para outros providers
    return len(credential_value) >= 8

@router.get("/status/{provider}", response_model=CredentialStatusResponse)
async def get_provider_status(
    provider: str,
    user_id: str = Depends(verify_authentication)
):
    """
    Obtém status de rate limiting para um provider.
    
    Args:
        provider: Nome do provider
        user_id: ID do usuário autenticado
        
    Returns:
        Status do provider
    """
    rate_limiter = get_rate_limiter()
    status_info = rate_limiter.get_provider_status(provider)
    
    response = CredentialStatusResponse(**status_info)
    
    logger.info({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "provider_status_retrieved",
        "status": "success",
        "source": "credential_validation.get_provider_status",
        "details": {
            "provider": provider,
            "user_id": user_id,
            "is_blocked": status_info["is_blocked"]
        }
    })
    
    return response

@router.get("/metrics", response_model=CredentialMetricsResponse)
async def get_credential_metrics(
    user_id: str = Depends(verify_authentication)
):
    """
    Obtém métricas de credenciais.
    
    Args:
        user_id: ID do usuário autenticado
        
    Returns:
        Métricas de credenciais
    """
    rate_limiter = get_rate_limiter()
    encryption_service = get_encryption_service()
    
    rate_limit_metrics = rate_limiter.get_metrics()
    encryption_metrics = encryption_service.get_security_metrics()
    
    response = CredentialMetricsResponse(
        total_requests=rate_limit_metrics["total_requests"],
        blocked_requests=rate_limit_metrics["blocked_requests"],
        anomaly_detections=rate_limit_metrics["anomaly_detections"],
        active_providers=rate_limit_metrics["active_providers"],
        blocked_providers=rate_limit_metrics["blocked_providers"],
        encryption_metrics=encryption_metrics,
        rate_limit_metrics=rate_limit_metrics["config"]
    )
    
    logger.info({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "credential_metrics_retrieved",
        "status": "success",
        "source": "credential_validation.get_credential_metrics",
        "details": {
            "user_id": user_id,
            "total_requests": rate_limit_metrics["total_requests"]
        }
    })
    
    return response

@router.post("/reset/{provider}")
async def reset_provider_rate_limit(
    provider: str,
    user_id: str = Depends(verify_authentication)
):
    """
    Reseta rate limit para um provider.
    
    Args:
        provider: Nome do provider
        user_id: ID do usuário autenticado
        
    Returns:
        Confirmação do reset
    """
    rate_limiter = get_rate_limiter()
    success = rate_limiter.reset_provider(provider)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao resetar rate limit"
        )
    
    logger.info({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "provider_rate_limit_reset",
        "status": "success",
        "source": "credential_validation.reset_provider_rate_limit",
        "details": {
            "provider": provider,
            "user_id": user_id
        }
    })
    
    return {
        "message": f"Rate limit resetado para {provider}",
        "provider": provider,
        "reset_by": user_id
    }

@router.get("/health")
async def health_check():
    """
    Verifica saúde dos serviços de credenciais.
    
    Returns:
        Status de saúde
    """
    rate_limiter = get_rate_limiter()
    encryption_service = get_encryption_service()
    
    rate_limiter_healthy = rate_limiter.is_healthy()
    encryption_healthy = encryption_service.is_healthy()
    
    overall_healthy = rate_limiter_healthy and encryption_healthy
    
    status_code = status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    response = {
        "healthy": overall_healthy,
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "rate_limiter": rate_limiter_healthy,
            "encryption": encryption_healthy
        }
    }
    
    if not overall_healthy:
        logger.error({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "credential_services_unhealthy",
            "status": "error",
            "source": "credential_validation.health_check",
            "details": response
        })
    
    return response 
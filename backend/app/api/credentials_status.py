"""
Credentials Status API

Endpoint para monitoramento e status de credenciais
Fornece informações em tempo real sobre o estado das credenciais

Tracing ID: API-006
Data/Hora: 2024-12-27 17:45:00 UTC
Versão: 1.0
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import json

from ..services.credentials_audit_service import get_audit_service, AuditEventType, AuditSeverity
from ..services.credential_encryption import CredentialEncryptionService
from ..services.credential_rate_limiter import CredentialRateLimiter
from ..middleware.auth import get_current_user
from ..models.user import User
from ..models.credentials import CredentialStatus, CredentialHealth, SystemHealth

router = APIRouter(prefix="/api/credentials", tags=["credentials"])

# Instâncias dos serviços
audit_service = get_audit_service()
encryption_service = CredentialEncryptionService()
rate_limiter = CredentialRateLimiter()

@router.get("/status", response_model=Dict[str, Any])
async def get_credentials_status(
    current_user: User = Depends(get_current_user),
    include_details: bool = Query(False, description="Incluir detalhes completos"),
    provider: Optional[str] = Query(None, description="Filtrar por provedor")
) -> Dict[str, Any]:
    """
    Retorna o status geral das credenciais do sistema
    
    Args:
        current_user: Usuário autenticado
        include_details: Se deve incluir detalhes completos
        provider: Provedor específico para filtrar
        
    Returns:
        Status das credenciais e saúde do sistema
    """
    try:
        # Log do acesso
        audit_service.log_event(
            event_type=AuditEventType.LOGIN_SUCCESS,
            severity=AuditSeverity.INFO,
            user_id=current_user.id,
            details={"endpoint": "/api/credentials/status"}
        )
        
        # Coleta estatísticas de auditoria
        audit_stats = audit_service.get_audit_statistics(
            start_date=datetime.now() - timedelta(days=7)
        )
        
        # Status das credenciais por provedor
        credentials_status = await _get_provider_status(provider)
        
        # Saúde do sistema
        system_health = await _get_system_health()
        
        # Rate limiting status
        rate_limit_status = rate_limiter.get_status()
        
        response = {
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id,
            "system_health": system_health,
            "credentials_status": credentials_status,
            "rate_limiting": rate_limit_status,
            "audit_statistics": audit_stats,
            "last_updated": datetime.now().isoformat()
        }
        
        if include_details:
            response["detailed_audit"] = await _get_detailed_audit()
        
        return response
        
    except Exception as e:
        # Log do erro
        audit_service.log_event(
            event_type=AuditEventType.SYSTEM_ERROR,
            severity=AuditSeverity.ERROR,
            user_id=current_user.id,
            details={"endpoint": "/api/credentials/status", "error": str(e)}
        )
        
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")

@router.get("/status/{provider}", response_model=Dict[str, Any])
async def get_provider_status(
    provider: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retorna o status de um provedor específico
    
    Args:
        provider: Nome do provedor
        current_user: Usuário autenticado
        
    Returns:
        Status detalhado do provedor
    """
    try:
        # Log do acesso
        audit_service.log_event(
            event_type=AuditEventType.LOGIN_SUCCESS,
            severity=AuditSeverity.INFO,
            user_id=current_user.id,
            details={"endpoint": f"/api/credentials/status/{provider}"}
        )
        
        # Status do provedor específico
        provider_status = await _get_provider_status(provider)
        
        if not provider_status:
            raise HTTPException(status_code=404, detail=f"Provedor {provider} não encontrado")
        
        # Eventos recentes do provedor
        recent_events = audit_service.get_audit_events(
            event_type=None,
            provider=provider,
            limit=50
        )
        
        response = {
            "provider": provider,
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id,
            "status": provider_status,
            "recent_events": [
                {
                    "timestamp": event.timestamp,
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "details": event.details
                }
                for event in recent_events
            ],
            "health_score": _calculate_health_score(provider_status, recent_events)
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        # Log do erro
        audit_service.log_event(
            event_type=AuditEventType.SYSTEM_ERROR,
            severity=AuditSeverity.ERROR,
            user_id=current_user.id,
            details={"endpoint": f"/api/credentials/status/{provider}", "error": str(e)}
        )
        
        raise HTTPException(status_code=500, detail=f"Erro ao obter status do provedor: {str(e)}")

@router.get("/health", response_model=SystemHealth)
async def get_system_health(
    current_user: User = Depends(get_current_user)
) -> SystemHealth:
    """
    Retorna a saúde geral do sistema de credenciais
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        Saúde do sistema
    """
    try:
        # Log do acesso
        audit_service.log_event(
            event_type=AuditEventType.LOGIN_SUCCESS,
            severity=AuditSeverity.INFO,
            user_id=current_user.id,
            details={"endpoint": "/api/credentials/health"}
        )
        
        system_health = await _get_system_health()
        return system_health
        
    except Exception as e:
        # Log do erro
        audit_service.log_event(
            event_type=AuditEventType.SYSTEM_ERROR,
            severity=AuditSeverity.ERROR,
            user_id=current_user.id,
            details={"endpoint": "/api/credentials/health", "error": str(e)}
        )
        
        raise HTTPException(status_code=500, detail=f"Erro ao obter saúde do sistema: {str(e)}")

@router.get("/alerts", response_model=List[Dict[str, Any]])
async def get_active_alerts(
    current_user: User = Depends(get_current_user),
    severity: Optional[str] = Query(None, description="Filtrar por severidade")
) -> List[Dict[str, Any]]:
    """
    Retorna alertas ativos do sistema
    
    Args:
        current_user: Usuário autenticado
        severity: Severidade para filtrar (info, warning, error, critical)
        
    Returns:
        Lista de alertas ativos
    """
    try:
        # Log do acesso
        audit_service.log_event(
            event_type=AuditEventType.LOGIN_SUCCESS,
            severity=AuditSeverity.INFO,
            user_id=current_user.id,
            details={"endpoint": "/api/credentials/alerts"}
        )
        
        # Busca eventos críticos recentes
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=24)
        
        events = audit_service.get_audit_events(
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        alerts = []
        
        for event in events:
            # Filtra por severidade se especificado
            if severity and event.severity != severity:
                continue
            
            # Identifica eventos que são alertas
            if _is_alert_event(event):
                alerts.append({
                    "id": f"{event.timestamp}_{event.event_type}",
                    "timestamp": event.timestamp,
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "provider": event.provider,
                    "user_id": event.user_id,
                    "message": _generate_alert_message(event),
                    "details": event.details,
                    "resolved": False
                })
        
        # Ordena por severidade e timestamp
        severity_order = {"critical": 0, "error": 1, "warning": 2, "info": 3}
        alerts.sort(key=lambda value: (severity_order.get(value["severity"], 4), value["timestamp"]), reverse=True)
        
        return alerts[:100]  # Limita a 100 alertas
        
    except Exception as e:
        # Log do erro
        audit_service.log_event(
            event_type=AuditEventType.SYSTEM_ERROR,
            severity=AuditSeverity.ERROR,
            user_id=current_user.id,
            details={"endpoint": "/api/credentials/alerts", "error": str(e)}
        )
        
        raise HTTPException(status_code=500, detail=f"Erro ao obter alertas: {str(e)}")

async def _get_provider_status(provider: Optional[str] = None) -> Dict[str, Any]:
    """Obtém o status dos provedores de credenciais"""
    # Simulação de status dos provedores
    # Em produção, isso viria do banco de dados ou cache
    
    providers = {
        "deepseek": {
            "status": "healthy",
            "last_validated": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "validation_count": 150,
            "error_count": 2,
            "success_rate": 98.7,
            "response_time_avg": 245,
            "rate_limit_remaining": 850,
            "rate_limit_reset": (datetime.now() + timedelta(minutes=15)).isoformat()
        },
        "openai": {
            "status": "warning",
            "last_validated": (datetime.now() - timedelta(hours=2)).isoformat(),
            "validation_count": 89,
            "error_count": 8,
            "success_rate": 91.0,
            "response_time_avg": 320,
            "rate_limit_remaining": 120,
            "rate_limit_reset": (datetime.now() + timedelta(minutes=45)).isoformat()
        },
        "claude": {
            "status": "healthy",
            "last_validated": (datetime.now() - timedelta(minutes=15)).isoformat(),
            "validation_count": 67,
            "error_count": 1,
            "success_rate": 98.5,
            "response_time_avg": 280,
            "rate_limit_remaining": 920,
            "rate_limit_reset": (datetime.now() + timedelta(minutes=20)).isoformat()
        },
        "gemini": {
            "status": "error",
            "last_validated": (datetime.now() - timedelta(hours=6)).isoformat(),
            "validation_count": 23,
            "error_count": 15,
            "success_rate": 34.8,
            "response_time_avg": 1200,
            "rate_limit_remaining": 0,
            "rate_limit_reset": (datetime.now() + timedelta(hours=1)).isoformat()
        }
    }
    
    if provider:
        return providers.get(provider, {})
    
    return providers

async def _get_system_health() -> SystemHealth:
    """Obtém a saúde geral do sistema"""
    # Simulação de métricas do sistema
    # Em produção, isso viria de monitoramento real
    
    return SystemHealth(
        overall_status="healthy",
        uptime_percentage=99.8,
        active_connections=45,
        total_requests_24h=12500,
        error_rate_24h=0.3,
        average_response_time=280,
        memory_usage_percentage=65.2,
        cpu_usage_percentage=42.1,
        disk_usage_percentage=78.5,
        last_updated=datetime.now().isoformat()
    )

async def _get_detailed_audit() -> List[Dict[str, Any]]:
    """Obtém auditoria detalhada"""
    events = audit_service.get_audit_events(limit=100)
    
    return [
        {
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "severity": event.severity,
            "provider": event.provider,
            "user_id": event.user_id,
            "details": event.details
        }
        for event in events
    ]

def _calculate_health_score(provider_status: Dict[str, Any], recent_events: List) -> float:
    """Calcula score de saúde do provedor (0-100)"""
    if not provider_status:
        return 0.0
    
    base_score = 100.0
    
    # Reduz score baseado na taxa de sucesso
    success_rate = provider_status.get("success_rate", 100.0)
    base_score *= (success_rate / 100.0)
    
    # Reduz score baseado em eventos críticos recentes
    critical_events = sum(1 for event in recent_events if event.severity == "critical")
    base_score -= (critical_events * 10)
    
    # Reduz score baseado em erros
    error_count = provider_status.get("error_count", 0)
    base_score -= (error_count * 2)
    
    return max(0.0, min(100.0, base_score))

def _is_alert_event(event) -> bool:
    """Verifica se um evento deve ser considerado um alerta"""
    alert_events = [
        AuditEventType.CREDENTIAL_INVALID,
        AuditEventType.CREDENTIAL_EXPIRED,
        AuditEventType.RATE_LIMIT_EXCEEDED,
        AuditEventType.SECURITY_ALERT,
        AuditEventType.SYSTEM_ERROR
    ]
    
    return (event.event_type in [e.value for e in alert_events] or 
            event.severity in ["error", "critical"])

def _generate_alert_message(event) -> str:
    """Gera mensagem de alerta baseada no evento"""
    messages = {
        AuditEventType.CREDENTIAL_INVALID.value: f"Credencial inválida detectada para {event.provider}",
        AuditEventType.CREDENTIAL_EXPIRED.value: f"Credencial expirada para {event.provider}",
        AuditEventType.RATE_LIMIT_EXCEEDED.value: f"Rate limit excedido para {event.provider}",
        AuditEventType.SECURITY_ALERT.value: "Alerta de segurança detectado",
        AuditEventType.SYSTEM_ERROR.value: "Erro do sistema detectado"
    }
    
    return messages.get(event.event_type, f"Evento {event.event_type} detectado") 
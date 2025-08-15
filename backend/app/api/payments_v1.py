"""
API de Pagamentos V1 - Omni Keywords Finder
Sistema robusto de pagamentos com múltiplos gateways e segurança avançada
Prompt: Melhoria do sistema de pagamentos V1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Header
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ..schemas.payment_v1_schemas import (
    PaymentRequest,
    PaymentResponse,
    PaymentRefundRequest,
    PaymentWebhookData,
    PaymentListRequest,
    PaymentMethod,
    PaymentStatus,
    Currency
)
from ..services.payment_v1_service import PaymentV1Service
from ..utils.auth_utils import get_current_user, require_permissions
from ..utils.rate_limiter import RateLimiter
from ..utils.security_utils import sanitize_input

# Configuração
router = APIRouter(prefix="/api/v1/payments", tags=["pagamentos v1"])
payment_service = PaymentV1Service()
rate_limiter = RateLimiter(
    redis_url="redis://localhost:6379",
    default_limits={"payments": {"requests": 100, "window": 3600}}
)

# Logger
logger = logging.getLogger(__name__)

@router.post("/process", response_model=Dict[str, Any])
async def process_payment(
    payment_request: PaymentRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Processa um pagamento
    
    Requer permissão: payments:process
    """
    try:
        # Verificar permissões
        await require_permissions(current_user, ["payments:process"])
        
        # Rate limiting
        await rate_limiter.check_rate_limit(
            "payment_process",
            identifier=current_user.get("id", "anonymous"),
            limits={"requests": 50, "window": 300}
        )
        
        # Log da requisição
        logger.info(f"Requisição de pagamento recebida: {payment_request.payment_id}")
        
        # Processar pagamento
        result = payment_service.process_payment(payment_request)
        
        if result.success:
            return {
                "success": True,
                "payment_id": result.payment_id,
                "status": result.status,
                "message": result.message,
                "data": result.data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "payment_id": result.payment_id,
                    "status": result.status,
                    "message": result.message,
                    "error_code": result.error_code,
                    "error_details": result.error_details
                }
            )
        
    except ValidationError as e:
        logger.error(f"Erro de validação no pagamento: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Dados inválidos: {str(e)}")
        
    except Exception as e:
        logger.error(f"Erro ao processar pagamento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{payment_id}", response_model=Dict[str, Any])
async def get_payment(
    payment_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtém detalhes de um pagamento
    
    Requer permissão: payments:read
    """
    try:
        # Verificar permissões
        await require_permissions(current_user, ["payments:read"])
        
        # Rate limiting
        await rate_limiter.check_rate_limit(
            "payment_query",
            identifier=current_user.get("id", "anonymous"),
            limits={"requests": 100, "window": 300}
        )
        
        # Sanitizar payment_id
        payment_id = sanitize_input(payment_id)
        
        # Obter pagamento
        payment = payment_service.get_payment(payment_id)
        
        if not payment:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")
        
        return {
            "success": True,
            "payment": payment,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter pagamento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/", response_model=Dict[str, Any])
async def list_payments(
    # Filtros
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    payment_method: Optional[str] = None,
    
    # Paginação
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    
    # Ordenação
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    
    # Filtros de tempo
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    
    # Autenticação e autorização
    current_user: Dict = Depends(get_current_user)
):
    """
    Lista pagamentos com filtros
    
    Requer permissão: payments:read
    """
    try:
        # Verificar permissões
        await require_permissions(current_user, ["payments:read"])
        
        # Rate limiting
        await rate_limiter.check_rate_limit(
            "payment_list",
            identifier=current_user.get("id", "anonymous"),
            limits={"requests": 30, "window": 300}
        )
        
        # Sanitizar inputs
        if customer_id:
            customer_id = sanitize_input(customer_id)
        
        if status:
            status = sanitize_input(status)
        
        if payment_method:
            payment_method = sanitize_input(payment_method)
        
        # Criar filtros
        filters = PaymentListRequest(
            customer_id=customer_id,
            status=status,
            payment_method=payment_method,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
            start_date=start_date,
            end_date=end_date
        )
        
        # Listar pagamentos
        payments = payment_service.list_payments(filters)
        
        return {
            "success": True,
            "payments": payments,
            "total": len(payments),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except ValidationError as e:
        logger.error(f"Erro de validação na listagem: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Parâmetros inválidos: {str(e)}")
        
    except Exception as e:
        logger.error(f"Erro ao listar pagamentos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{payment_id}/refund", response_model=Dict[str, Any])
async def process_refund(
    payment_id: str,
    refund_request: PaymentRefundRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Processa reembolso de um pagamento
    
    Requer permissão: payments:refund
    """
    try:
        # Verificar permissões
        await require_permissions(current_user, ["payments:refund"])
        
        # Rate limiting
        await rate_limiter.check_rate_limit(
            "payment_refund",
            identifier=current_user.get("id", "anonymous"),
            limits={"requests": 10, "window": 3600}
        )
        
        # Sanitizar payment_id
        payment_id = sanitize_input(payment_id)
        
        # Verificar se payment_id coincide
        if refund_request.payment_id != payment_id:
            raise HTTPException(status_code=400, detail="Payment ID não coincide")
        
        # Log da requisição
        logger.info(f"Requisição de reembolso recebida: {refund_request.refund_id}")
        
        # Processar reembolso
        result = payment_service.process_refund(refund_request)
        
        if result.success:
            return {
                "success": True,
                "refund_id": refund_request.refund_id,
                "payment_id": result.payment_id,
                "status": result.status,
                "message": result.message,
                "data": result.data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "refund_id": refund_request.refund_id,
                    "payment_id": result.payment_id,
                    "status": result.status,
                    "message": result.message,
                    "error_code": result.error_code,
                    "error_details": result.error_details
                }
            )
        
    except ValidationError as e:
        logger.error(f"Erro de validação no reembolso: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Dados inválidos: {str(e)}")
        
    except Exception as e:
        logger.error(f"Erro ao processar reembolso: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/webhook")
async def process_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None),
    paypal_signature: Optional[str] = Header(None)
):
    """
    Processa webhook de pagamento
    
    Endpoint público para receber notificações dos gateways
    """
    try:
        # Obter payload
        payload = await request.body()
        
        # Determinar assinatura baseado no provedor
        signature = None
        if stripe_signature:
            signature = stripe_signature
        elif paypal_signature:
            signature = paypal_signature
        
        if not signature:
            logger.warning("Webhook recebido sem assinatura")
            raise HTTPException(status_code=400, detail="Assinatura não fornecida")
        
        # Log do webhook
        logger.info(f"Webhook recebido: {len(payload)} bytes")
        
        # Processar webhook
        result = payment_service.process_webhook(payload, signature)
        
        if result.success:
            return {
                "success": True,
                "message": "Webhook processado com sucesso",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            logger.error(f"Erro no processamento do webhook: {result.message}")
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "message": result.message,
                    "error_code": result.error_code
                }
            )
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/methods")
async def get_payment_methods():
    """
    Obtém métodos de pagamento disponíveis
    """
    return {
        "success": True,
        "payment_methods": [method.value for method in PaymentMethod],
        "currencies": [currency.value for currency in Currency],
        "statuses": [status.value for status in PaymentStatus],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/{payment_id}/status")
async def get_payment_status(
    payment_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtém status de um pagamento
    
    Requer permissão: payments:read
    """
    try:
        # Verificar permissões
        await require_permissions(current_user, ["payments:read"])
        
        # Rate limiting
        await rate_limiter.check_rate_limit(
            "payment_status",
            identifier=current_user.get("id", "anonymous"),
            limits={"requests": 200, "window": 300}
        )
        
        # Sanitizar payment_id
        payment_id = sanitize_input(payment_id)
        
        # Obter pagamento
        payment = payment_service.get_payment(payment_id)
        
        if not payment:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")
        
        return {
            "success": True,
            "payment_id": payment_id,
            "status": payment["status"],
            "status_code": payment["status_code"],
            "amount": payment["amount"],
            "currency": payment["currency"],
            "payment_method": payment["payment_method"],
            "created_at": payment["created_at"],
            "updated_at": payment["updated_at"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter status do pagamento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{payment_id}/cancel")
async def cancel_payment(
    payment_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Cancela um pagamento
    
    Requer permissão: payments:cancel
    """
    try:
        # Verificar permissões
        await require_permissions(current_user, ["payments:cancel"])
        
        # Rate limiting
        await rate_limiter.check_rate_limit(
            "payment_cancel",
            identifier=current_user.get("id", "anonymous"),
            limits={"requests": 20, "window": 3600}
        )
        
        # Sanitizar payment_id
        payment_id = sanitize_input(payment_id)
        
        # Obter pagamento
        payment = payment_service.get_payment(payment_id)
        
        if not payment:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")
        
        # Verificar se pode ser cancelado
        if payment["status"] not in [PaymentStatus.PENDING.value, PaymentStatus.PROCESSING.value]:
            raise HTTPException(
                status_code=400,
                detail="Pagamento não pode ser cancelado"
            )
        
        # Cancelar pagamento
        payment_service._update_payment_status(payment_id, PaymentStatus.CANCELLED.value)
        
        logger.info(f"Pagamento cancelado: {payment_id}")
        
        return {
            "success": True,
            "payment_id": payment_id,
            "status": PaymentStatus.CANCELLED.value,
            "message": "Pagamento cancelado com sucesso",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao cancelar pagamento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/stats/summary")
async def get_payment_stats(
    period: str = "daily",
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtém estatísticas de pagamentos
    
    Requer permissão: payments:read
    """
    try:
        # Verificar permissões
        await require_permissions(current_user, ["payments:read"])
        
        # Rate limiting
        await rate_limiter.check_rate_limit(
            "payment_stats",
            identifier=current_user.get("id", "anonymous"),
            limits={"requests": 10, "window": 300}
        )
        
        # Obter pagamentos
        filters = PaymentListRequest(limit=1000)  # Limite alto para estatísticas
        payments = payment_service.list_payments(filters)
        
        # Calcular estatísticas
        total_payments = len(payments)
        total_amount = sum(p["amount"] for p in payments)
        
        # Por status
        status_counts = {}
        for payment in payments:
            status = payment["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Por método
        method_counts = {}
        for payment in payments:
            method = payment["payment_method"]
            method_counts[method] = method_counts.get(method, 0) + 1
        
        # Por moeda
        currency_totals = {}
        for payment in payments:
            currency = payment["currency"]
            currency_totals[currency] = currency_totals.get(currency, 0) + payment["amount"]
        
        return {
            "success": True,
            "period": period,
            "stats": {
                "total_payments": total_payments,
                "total_amount": total_amount,
                "status_counts": status_counts,
                "method_counts": method_counts,
                "currency_totals": currency_totals
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/health")
async def payment_health_check():
    """
    Verificação de saúde do sistema de pagamentos
    """
    try:
        # Verificar banco de dados
        test_filters = PaymentListRequest(limit=1)
        payments = payment_service.list_payments(test_filters)
        
        # Verificar configuração do gateway
        gateway_config = payment_service.gateway_config
        
        return {
            "status": "healthy",
            "database": "connected",
            "gateway_provider": gateway_config.provider,
            "gateway_environment": gateway_config.environment,
            "total_payments": len(payments),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro na verificação de saúde: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Middleware para capturar métricas de pagamento
@router.middleware("http")
async def payment_metrics_middleware(request: Request, call_next):
    """Middleware para capturar métricas de pagamento"""
    try:
        # Capturar informações da requisição
        start_time = datetime.now(timezone.utc)
        
        # Processar requisição
        response = await call_next(request)
        
        # Calcular métricas de performance
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        # Registrar métrica de performance se for endpoint de pagamento
        if request.url.path.startswith("/api/v1/payments") and duration > 1.0:
            logger.warning(f"Pagamento lento detectado: {request.url.path} - {duration:.2f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"Erro no middleware de pagamentos: {str(e)}")
        return await call_next(request)

# Tratamento de erros global
@router.exception_handler(Exception)
async def payment_exception_handler(request: Request, exc: Exception):
    """Tratamento global de exceções para pagamentos"""
    logger.error(f"Exceção não tratada em pagamentos: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Erro interno do servidor",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    ) 
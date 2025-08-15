"""
Rate Limiting específico para execuções - Omni Keywords Finder
Prompt: Implementação de rate limiting para execuções
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import time
import logging
from functools import wraps
from typing import Optional, Dict, Any
from flask import request, jsonify, g, current_app
from backend.app.utils.log_event import log_event

try:
    from infrastructure.security.rate_limiting_inteligente import (
        get_rate_limiter,
        RateLimitConfig
    )
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    logging.warning("Rate limiting não disponível. Usando fallback simples.")

class ExecucaoRateLimitConfig:
    """Configuração específica de rate limiting para execuções"""
    
    def __init__(self):
        # Limites para execuções individuais
        self.individual_requests_per_minute = 10
        self.individual_requests_per_hour = 100
        self.individual_requests_per_day = 1000
        
        # Limites para execuções em lote
        self.batch_requests_per_minute = 2
        self.batch_requests_per_hour = 20
        self.batch_requests_per_day = 200
        
        # Limite de execuções por lote
        self.max_execucoes_per_batch = 50
        
        # Tempo de bloqueio após exceder limite
        self.block_duration_minutes = 15

def execucao_rate_limited():
    """
    Decorator para rate limiting específico de execuções.
    Aplica limites diferenciados para execuções individuais e em lote.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not RATE_LIMITING_AVAILABLE:
                # Fallback: permitir requisição se rate limiting não estiver disponível
                return func(*args, **kwargs)
            
            try:
                # Obter identificador do usuário
                user_id = getattr(g, 'user_id', None)
                if not user_id:
                    return jsonify({
                        "erro": "Usuário não autenticado",
                        "codigo": "UNAUTHORIZED"
                    }), 401
                
                # Determinar tipo de execução (individual ou lote)
                is_batch = request.endpoint == 'execucoes.executar_lote'
                
                # Configurar limites baseado no tipo
                if is_batch:
                    requests_per_minute = ExecucaoRateLimitConfig().batch_requests_per_minute
                    requests_per_hour = ExecucaoRateLimitConfig().batch_requests_per_hour
                    requests_per_day = ExecucaoRateLimitConfig().batch_requests_per_day
                    endpoint_type = "batch"
                else:
                    requests_per_minute = ExecucaoRateLimitConfig().individual_requests_per_minute
                    requests_per_hour = ExecucaoRateLimitConfig().individual_requests_per_hour
                    requests_per_day = ExecucaoRateLimitConfig().individual_requests_per_day
                    endpoint_type = "individual"
                
                # Verificar rate limit
                rate_limiter = get_rate_limiter()
                
                # Verificar limite por minuto
                minute_key = f"execucao:{user_id}:{endpoint_type}:minute:{int(time.time() / 60)}"
                minute_count = rate_limiter.get_count(minute_key)
                
                if minute_count >= requests_per_minute:
                    log_event('warning', 'Execucao', 
                             detalhes=f'Rate limit excedido: {minute_count}/{requests_per_minute} por minuto para usuário {user_id}')
                    return jsonify({
                        "erro": "Limite de execuções por minuto excedido",
                        "codigo": "RATE_LIMIT_EXCEEDED",
                        "detalhes": {
                            "limite": requests_per_minute,
                            "atual": minute_count,
                            "reset_em": 60 - (int(time.time()) % 60)
                        }
                    }), 429
                
                # Verificar limite por hora
                hour_key = f"execucao:{user_id}:{endpoint_type}:hour:{int(time.time() / 3600)}"
                hour_count = rate_limiter.get_count(hour_key)
                
                if hour_count >= requests_per_hour:
                    log_event('warning', 'Execucao', 
                             detalhes=f'Rate limit excedido: {hour_count}/{requests_per_hour} por hora para usuário {user_id}')
                    return jsonify({
                        "erro": "Limite de execuções por hora excedido",
                        "codigo": "RATE_LIMIT_EXCEEDED",
                        "detalhes": {
                            "limite": requests_per_hour,
                            "atual": hour_count,
                            "reset_em": 3600 - (int(time.time()) % 3600)
                        }
                    }), 429
                
                # Verificar limite por dia
                day_key = f"execucao:{user_id}:{endpoint_type}:day:{int(time.time() / 86400)}"
                day_count = rate_limiter.get_count(day_key)
                
                if day_count >= requests_per_day:
                    log_event('warning', 'Execucao', 
                             detalhes=f'Rate limit excedido: {day_count}/{requests_per_day} por dia para usuário {user_id}')
                    return jsonify({
                        "erro": "Limite de execuções por dia excedido",
                        "codigo": "RATE_LIMIT_EXCEEDED",
                        "detalhes": {
                            "limite": requests_per_day,
                            "atual": day_count,
                            "reset_em": 86400 - (int(time.time()) % 86400)
                        }
                    }), 429
                
                # Incrementar contadores
                rate_limiter.increment(minute_key, 60)
                rate_limiter.increment(hour_key, 3600)
                rate_limiter.increment(day_key, 86400)
                
                # Log de sucesso
                log_event('info', 'Execucao', 
                         detalhes=f'Rate limit OK: {minute_count + 1}/{requests_per_minute} por minuto para usuário {user_id}')
                
                # Executar função original
                return func(*args, **kwargs)
                
            except Exception as e:
                logging.error(f"Erro no rate limiting de execuções: {e}")
                # Em caso de erro, permitir a requisição
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

def validate_batch_size():
    """
    Decorator para validar tamanho do lote de execuções.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json()
                if data and isinstance(data, dict) and 'execucoes' in data:
                    batch_size = len(data['execucoes'])
                    max_size = ExecucaoRateLimitConfig().max_execucoes_per_batch
                    
                    if batch_size > max_size:
                        log_event('warning', 'Execucao', 
                                 detalhes=f'Lote muito grande: {batch_size}/{max_size} execuções')
                        return jsonify({
                            "erro": f"Lote muito grande. Máximo de {max_size} execuções permitidas.",
                            "codigo": "BATCH_SIZE_EXCEEDED",
                            "detalhes": {
                                "tamanho_atual": batch_size,
                                "tamanho_maximo": max_size
                            }
                        }), 400
                
                return func(*args, **kwargs)
                
            except Exception as e:
                logging.error(f"Erro na validação de tamanho do lote: {e}")
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

def get_execucao_rate_limit_stats(user_id: str) -> Dict[str, Any]:
    """
    Obtém estatísticas de rate limiting para execuções de um usuário.
    """
    if not RATE_LIMITING_AVAILABLE:
        return {"erro": "Rate limiting não disponível"}
    
    try:
        rate_limiter = get_rate_limiter()
        current_time = int(time.time())
        
        stats = {
            "individual": {
                "minute": rate_limiter.get_count(f"execucao:{user_id}:individual:minute:{current_time // 60}"),
                "hour": rate_limiter.get_count(f"execucao:{user_id}:individual:hour:{current_time // 3600}"),
                "day": rate_limiter.get_count(f"execucao:{user_id}:individual:day:{current_time // 86400}")
            },
            "batch": {
                "minute": rate_limiter.get_count(f"execucao:{user_id}:batch:minute:{current_time // 60}"),
                "hour": rate_limiter.get_count(f"execucao:{user_id}:batch:hour:{current_time // 3600}"),
                "day": rate_limiter.get_count(f"execucao:{user_id}:batch:day:{current_time // 86400}")
            },
            "limits": {
                "individual": {
                    "per_minute": ExecucaoRateLimitConfig().individual_requests_per_minute,
                    "per_hour": ExecucaoRateLimitConfig().individual_requests_per_hour,
                    "per_day": ExecucaoRateLimitConfig().individual_requests_per_day
                },
                "batch": {
                    "per_minute": ExecucaoRateLimitConfig().batch_requests_per_minute,
                    "per_hour": ExecucaoRateLimitConfig().batch_requests_per_hour,
                    "per_day": ExecucaoRateLimitConfig().batch_requests_per_day,
                    "max_size": ExecucaoRateLimitConfig().max_execucoes_per_batch
                }
            }
        }
        
        return stats
        
    except Exception as e:
        logging.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        return {"erro": "Erro ao obter estatísticas"} 
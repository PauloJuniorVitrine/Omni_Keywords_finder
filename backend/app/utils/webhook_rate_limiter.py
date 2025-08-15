"""
Rate Limiter Especializado para Webhooks - Omni Keywords Finder
Controle de taxa para webhooks com diferenciação por tipo de cliente
Prompt: Revisão de segurança de webhooks
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
import redis
from collections import defaultdict

class ClientTier(Enum):
    """Tipos de cliente para rate limiting"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

@dataclass
class RateLimitConfig:
    """Configuração de rate limiting por tipo de cliente"""
    requests_per_hour: int
    requests_per_minute: int
    burst_limit: int
    window_size: int = 3600  # 1 hora em segundos

@dataclass
class RateLimitResult:
    """Resultado da verificação de rate limiting"""
    allowed: bool
    remaining: int
    reset_time: int
    retry_after: Optional[int] = None
    reason: Optional[str] = None

class WebhookRateLimiter:
    """Rate limiter especializado para webhooks"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Inicializa o rate limiter"""
        self.redis_client = None
        self.use_redis = False
        
        # Configurar Redis se disponível
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                self.use_redis = True
                logging.info("Rate limiter usando Redis")
            except Exception as e:
                logging.warning(f"Redis não disponível, usando memória: {str(e)}")
        
        # Configurações por tipo de cliente
        self.client_configs = {
            ClientTier.FREE: RateLimitConfig(
                requests_per_hour=100,
                requests_per_minute=10,
                burst_limit=5
            ),
            ClientTier.BASIC: RateLimitConfig(
                requests_per_hour=1000,
                requests_per_minute=100,
                burst_limit=20
            ),
            ClientTier.PREMIUM: RateLimitConfig(
                requests_per_hour=10000,
                requests_per_minute=1000,
                burst_limit=100
            ),
            ClientTier.ENTERPRISE: RateLimitConfig(
                requests_per_hour=100000,
                requests_per_minute=10000,
                burst_limit=1000
            )
        }
        
        # Fallback para memória
        self.memory_storage = defaultdict(list)
        
        # Logger
        self.logger = logging.getLogger("webhook_rate_limiter")
    
    def _get_client_tier(self, api_key: Optional[str] = None, user_id: Optional[str] = None) -> ClientTier:
        """Determina o tier do cliente baseado em API key ou user_id"""
        # Em produção, isso seria consultado no banco de dados
        if api_key:
            # Simular verificação de API key
            if api_key.startswith("enterprise_"):
                return ClientTier.ENTERPRISE
            elif api_key.startswith("premium_"):
                return ClientTier.PREMIUM
            elif api_key.startswith("basic_"):
                return ClientTier.BASIC
            else:
                return ClientTier.FREE
        
        if user_id:
            # Simular verificação de usuário
            # Em produção, consultaria o banco de dados
            return ClientTier.BASIC
        
        return ClientTier.FREE
    
    def _get_identifier(self, ip_address: str, api_key: Optional[str] = None, user_id: Optional[str] = None) -> str:
        """Gera identificador único para rate limiting"""
        if api_key:
            return f"webhook:api:{api_key}"
        elif user_id:
            return f"webhook:user:{user_id}"
        else:
            return f"webhook:ip:{ip_address}"
    
    def _check_redis_rate_limit(
        self,
        identifier: str,
        config: RateLimitConfig,
        current_time: int
    ) -> RateLimitResult:
        """Verifica rate limit usando Redis"""
        try:
            # Chaves para diferentes janelas de tempo
            hour_key = f"{identifier}:hour:{current_time // 3600}"
            minute_key = f"{identifier}:minute:{current_time // 60}"
            burst_key = f"{identifier}:burst:{current_time}"
            
            # Pipeline para operações atômicas
            pipe = self.redis_client.pipeline()
            
            # Verificar limite por hora
            pipe.get(hour_key)
            pipe.ttl(hour_key)
            
            # Verificar limite por minuto
            pipe.get(minute_key)
            pipe.ttl(minute_key)
            
            # Verificar burst limit
            pipe.get(burst_key)
            pipe.ttl(burst_key)
            
            results = pipe.execute()
            
            hour_count = int(results[0]) if results[0] else 0
            hour_ttl = results[1] if results[1] > 0 else 3600
            minute_count = int(results[2]) if results[2] else 0
            minute_ttl = results[3] if results[3] > 0 else 60
            burst_count = int(results[4]) if results[4] else 0
            burst_ttl = results[5] if results[5] > 0 else 1
            
            # Verificar limites
            if hour_count >= config.requests_per_hour:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=current_time + hour_ttl,
                    retry_after=hour_ttl,
                    reason="Hourly limit exceeded"
                )
            
            if minute_count >= config.requests_per_minute:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=current_time + minute_ttl,
                    retry_after=minute_ttl,
                    reason="Minute limit exceeded"
                )
            
            if burst_count >= config.burst_limit:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=current_time + burst_ttl,
                    retry_after=burst_ttl,
                    reason="Burst limit exceeded"
                )
            
            # Incrementar contadores
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)
            pipe.incr(burst_key)
            pipe.expire(burst_key, 1)
            pipe.execute()
            
            return RateLimitResult(
                allowed=True,
                remaining=min(
                    config.requests_per_hour - hour_count - 1,
                    config.requests_per_minute - minute_count - 1,
                    config.burst_limit - burst_count - 1
                ),
                reset_time=current_time + min(hour_ttl, minute_ttl, burst_ttl)
            )
            
        except Exception as e:
            self.logger.error(f"Erro no Redis rate limiting: {str(e)}")
            # Fallback para memória
            return self._check_memory_rate_limit(identifier, config, current_time)
    
    def _check_memory_rate_limit(
        self,
        identifier: str,
        config: RateLimitConfig,
        current_time: int
    ) -> RateLimitResult:
        """Verifica rate limit usando memória (fallback)"""
        try:
            # Limpar registros antigos
            self._cleanup_old_records(identifier, current_time)
            
            # Obter registros atuais
            records = self.memory_storage[identifier]
            
            # Contar requisições por janela
            hour_count = len([r for r in records if current_time - r < 3600])
            minute_count = len([r for r in records if current_time - r < 60])
            burst_count = len([r for r in records if current_time - r < 1])
            
            # Verificar limites
            if hour_count >= config.requests_per_hour:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=current_time + 3600,
                    retry_after=3600,
                    reason="Hourly limit exceeded"
                )
            
            if minute_count >= config.requests_per_minute:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=current_time + 60,
                    retry_after=60,
                    reason="Minute limit exceeded"
                )
            
            if burst_count >= config.burst_limit:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=current_time + 1,
                    retry_after=1,
                    reason="Burst limit exceeded"
                )
            
            # Adicionar registro atual
            records.append(current_time)
            
            return RateLimitResult(
                allowed=True,
                remaining=min(
                    config.requests_per_hour - hour_count - 1,
                    config.requests_per_minute - minute_count - 1,
                    config.burst_limit - burst_count - 1
                ),
                reset_time=current_time + 60
            )
            
        except Exception as e:
            self.logger.error(f"Erro no memory rate limiting: {str(e)}")
            # Em caso de erro, permitir a requisição
            return RateLimitResult(
                allowed=True,
                remaining=config.requests_per_hour - 1,
                reset_time=current_time + 3600
            )
    
    def _cleanup_old_records(self, identifier: str, current_time: int):
        """Remove registros antigos da memória"""
        if identifier in self.memory_storage:
            records = self.memory_storage[identifier]
            # Manter apenas registros da última hora
            self.memory_storage[identifier] = [
                r for r in records if current_time - r < 3600
            ]
    
    def check_rate_limit(
        self,
        ip_address: str,
        api_key: Optional[str] = None,
        user_id: Optional[str] = None,
        endpoint_id: Optional[str] = None
    ) -> RateLimitResult:
        """
        Verifica se a requisição está dentro dos limites de taxa
        
        Args:
            ip_address: Endereço IP do cliente
            api_key: API key do cliente (opcional)
            user_id: ID do usuário (opcional)
            endpoint_id: ID do endpoint (opcional)
            
        Returns:
            RateLimitResult com informações sobre o rate limiting
        """
        try:
            current_time = int(time.time())
            
            # Determinar tier do cliente
            client_tier = self._get_client_tier(api_key, user_id)
            config = self.client_configs[client_tier]
            
            # Gerar identificador
            identifier = self._get_identifier(ip_address, api_key, user_id)
            if endpoint_id:
                identifier += f":{endpoint_id}"
            
            # Verificar rate limit
            if self.use_redis and self.redis_client:
                result = self._check_redis_rate_limit(identifier, config, current_time)
            else:
                result = self._check_memory_rate_limit(identifier, config, current_time)
            
            # Log do resultado
            self._log_rate_limit_check(
                identifier, client_tier, result, ip_address, api_key, user_id
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar rate limit: {str(e)}")
            # Em caso de erro, permitir a requisição
            return RateLimitResult(
                allowed=True,
                remaining=1000,
                reset_time=int(time.time()) + 3600
            )
    
    def _log_rate_limit_check(
        self,
        identifier: str,
        client_tier: ClientTier,
        result: RateLimitResult,
        ip_address: str,
        api_key: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Log da verificação de rate limiting"""
        log_data = {
            "identifier": identifier,
            "client_tier": client_tier.value,
            "allowed": result.allowed,
            "remaining": result.remaining,
            "reset_time": result.reset_time,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if api_key:
            log_data["api_key"] = api_key[:8] + "..."  # Mascarar API key
        
        if user_id:
            log_data["user_id"] = user_id
        
        if result.reason:
            log_data["reason"] = result.reason
        
        if result.allowed:
            self.logger.info(f"Rate limit check passed: {json.dumps(log_data)}")
        else:
            self.logger.warning(f"Rate limit exceeded: {json.dumps(log_data)}")
    
    def get_rate_limit_info(
        self,
        ip_address: str,
        api_key: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtém informações sobre rate limiting do cliente"""
        client_tier = self._get_client_tier(api_key, user_id)
        config = self.client_configs[client_tier]
        
        return {
            "client_tier": client_tier.value,
            "limits": {
                "requests_per_hour": config.requests_per_hour,
                "requests_per_minute": config.requests_per_minute,
                "burst_limit": config.burst_limit
            },
            "window_size": config.window_size
        }
    
    def reset_rate_limit(
        self,
        ip_address: str,
        api_key: Optional[str] = None,
        user_id: Optional[str] = None,
        endpoint_id: Optional[str] = None
    ) -> bool:
        """Reseta rate limiting para um identificador específico"""
        try:
            identifier = self._get_identifier(ip_address, api_key, user_id)
            if endpoint_id:
                identifier += f":{endpoint_id}"
            
            if self.use_redis and self.redis_client:
                # Remover chaves do Redis
                pattern = f"{identifier}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            else:
                # Remover da memória
                if identifier in self.memory_storage:
                    del self.memory_storage[identifier]
            
            self.logger.info(f"Rate limit reset for: {identifier}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao resetar rate limit: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas do rate limiter"""
        stats = {
            "storage_type": "redis" if self.use_redis else "memory",
            "client_configs": {
                tier.value: {
                    "requests_per_hour": config.requests_per_hour,
                    "requests_per_minute": config.requests_per_minute,
                    "burst_limit": config.burst_limit
                }
                for tier, config in self.client_configs.items()
            }
        }
        
        if not self.use_redis:
            stats["memory_entries"] = len(self.memory_storage)
        
        return stats 
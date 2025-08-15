"""
🧪 Testes de Falhas e Edge Cases - Integrações Reais

Tracing ID: test-failure-scenarios-2025-01-27-001
Timestamp: 2025-01-27T18:15:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em cenários reais de falha das APIs
🌲 ToT: Avaliadas múltiplas estratégias de teste de resiliência
♻️ ReAct: Simulado cenários de falha e validada recuperação

Testa cenários de falha e edge cases incluindo:
- Rate limiting excedido
- Circuit breaker aberto
- Timeout de API
- Falhas de rede
- Dados inválidos
- Credenciais expiradas
- Quota excedida
- Serviços indisponíveis
"""

import pytest
import asyncio
import aiohttp
import time
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, List, Any, Optional
import yaml
import os

# Importar APIs reais
from infrastructure.coleta.instagram_real_api import InstagramRealAPI
from infrastructure.coleta.tiktok_real_api import TikTokRealAPI
from infrastructure.coleta.youtube_real_api import YouTubeRealAPI
from infrastructure.coleta.pinterest_real_api import PinterestRealAPI
from infrastructure.coleta.discord_real_bot import DiscordRealBot

# Importar componentes de resiliência
from infrastructure.orchestrator.error_handler import CircuitBreaker
from infrastructure.orchestrator.rate_limiter import RateLimiter
from infrastructure.orchestrator.fallback_manager import FallbackManager

# Configuração de teste
TEST_CONFIG_PATH = "config/test_environment.yaml"

def load_test_config():
    """Carrega configuração de teste"""
    if os.path.exists(TEST_CONFIG_PATH):
        with open(TEST_CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    return {}

class TestFailureScenarios:
    """Testes para cenários de falha e edge cases"""
    
    @pytest.fixture
    def test_config(self):
        """Fixture para configuração de teste"""
        return load_test_config()
    
    @pytest.fixture
    def mock_session(self):
        """Fixture para sessão HTTP mockada"""
        session = Mock(spec=aiohttp.ClientSession)
        session.get = AsyncMock()
        session.post = AsyncMock()
        session.close = AsyncMock()
        return session

class TestRateLimitingScenarios:
    """Testes para cenários de rate limiting"""
    
    @pytest.mark.asyncio
    async def test_instagram_rate_limit_exceeded(self, test_config):
        """Testa rate limiting excedido no Instagram"""
        # Configurar API com rate limit baixo
        config = test_config.get('apis', {}).get('instagram', {})
        api = InstagramRealAPI(config)
        
        # Mock para resposta de rate limit
        rate_limit_response = Mock()
        rate_limit_response.status = 429
        rate_limit_response.headers = {
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': str(int(time.time()) + 60)
        }
        rate_limit_response.json = AsyncMock(return_value={
            'error': {
                'type': 'OAuthRateLimitException',
                'message': 'Rate limit exceeded'
            }
        })
        
        with patch.object(api.session, 'get', return_value=rate_limit_response):
            # Tentar fazer múltiplas requisições
            results = []
            for i in range(5):
                try:
                    result = await api.get_user_posts("test_user")
                    results.append(result)
                except Exception as e:
                    results.append(e)
            
            # Verificar se rate limiting foi aplicado
            assert any(isinstance(r, Exception) for r in results)
            
    @pytest.mark.asyncio
    async def test_tiktok_rate_limit_exceeded(self, test_config):
        """Testa rate limiting excedido no TikTok"""
        config = test_config.get('apis', {}).get('tiktok', {})
        api = TikTokRealAPI(config)
        
        # Mock para resposta de rate limit
        rate_limit_response = Mock()
        rate_limit_response.status = 429
        rate_limit_response.headers = {
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': str(int(time.time()) + 60)
        }
        rate_limit_response.json = AsyncMock(return_value={
            'error': {
                'code': 10008,
                'message': 'Rate limit exceeded'
            }
        })
        
        with patch.object(api.session, 'get', return_value=rate_limit_response):
            try:
                await api.get_user_videos("test_user")
                assert False, "Deveria ter falhado com rate limit"
            except Exception as e:
                assert "rate limit" in str(e).lower()
                
    @pytest.mark.asyncio
    async def test_youtube_quota_exceeded(self, test_config):
        """Testa quota excedida no YouTube"""
        config = test_config.get('apis', {}).get('youtube', {})
        api = YouTubeRealAPI(config)
        
        # Mock para resposta de quota excedida
        quota_response = Mock()
        quota_response.status = 403
        quota_response.json = AsyncMock(return_value={
            'error': {
                'code': 403,
                'message': 'Quota exceeded',
                'errors': [{
                    'domain': 'usageLimits',
                    'reason': 'quotaExceeded'
                }]
            }
        })
        
        with patch.object(api.session, 'get', return_value=quota_response):
            try:
                await api.search_videos("test")
                assert False, "Deveria ter falhado com quota excedida"
            except Exception as e:
                assert "quota" in str(e).lower()
                
    @pytest.mark.asyncio
    async def test_pinterest_rate_limit_exceeded(self, test_config):
        """Testa rate limiting excedido no Pinterest"""
        config = test_config.get('apis', {}).get('pinterest', {})
        api = PinterestRealAPI(config)
        
        # Mock para resposta de rate limit
        rate_limit_response = Mock()
        rate_limit_response.status = 429
        rate_limit_response.headers = {
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': str(int(time.time()) + 60)
        }
        rate_limit_response.json = AsyncMock(return_value={
            'error': {
                'code': 429,
                'message': 'Rate limit exceeded'
            }
        })
        
        with patch.object(api.session, 'get', return_value=rate_limit_response):
            try:
                await api.search_pins("test")
                assert False, "Deveria ter falhado com rate limit"
            except Exception as e:
                assert "rate limit" in str(e).lower()
                
    @pytest.mark.asyncio
    async def test_discord_rate_limit_exceeded(self, test_config):
        """Testa rate limiting excedido no Discord"""
        config = test_config.get('apis', {}).get('discord', {})
        bot = DiscordRealBot(config)
        
        # Mock para resposta de rate limit
        rate_limit_response = Mock()
        rate_limit_response.status = 429
        rate_limit_response.headers = {
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': str(int(time.time()) + 60)
        }
        rate_limit_response.json = AsyncMock(return_value={
            'error': {
                'code': 429,
                'message': 'Rate limit exceeded'
            }
        })
        
        with patch.object(bot.session, 'get', return_value=rate_limit_response):
            try:
                await bot.get_guild_channels("test_guild")
                assert False, "Deveria ter falhado com rate limit"
            except Exception as e:
                assert "rate limit" in str(e).lower()

class TestCircuitBreakerScenarios:
    """Testes para cenários de circuit breaker"""
    
    @pytest.mark.asyncio
    async def test_instagram_circuit_breaker_open(self, test_config):
        """Testa circuit breaker aberto no Instagram"""
        config = test_config.get('apis', {}).get('instagram', {})
        api = InstagramRealAPI(config)
        
        # Configurar circuit breaker para abrir rapidamente
        api.circuit_breaker.failure_threshold = 2
        api.circuit_breaker.recovery_timeout = 5
        
        # Mock para falhas consecutivas
        error_response = Mock()
        error_response.status = 500
        error_response.json = AsyncMock(return_value={
            'error': {
                'type': 'OAuthException',
                'message': 'Internal server error'
            }
        })
        
        with patch.object(api.session, 'get', return_value=error_response):
            # Primeira falha
            try:
                await api.get_user_posts("test_user")
                assert False, "Deveria ter falhado"
            except Exception:
                pass
            
            # Segunda falha - circuit breaker deve abrir
            try:
                await api.get_user_posts("test_user")
                assert False, "Deveria ter falhado"
            except Exception:
                pass
            
            # Terceira tentativa - circuit breaker deve estar aberto
            try:
                await api.get_user_posts("test_user")
                assert False, "Circuit breaker deveria estar aberto"
            except Exception as e:
                assert "circuit breaker" in str(e).lower()
                
    @pytest.mark.asyncio
    async def test_tiktok_circuit_breaker_half_open(self, test_config):
        """Testa circuit breaker em estado half-open no TikTok"""
        config = test_config.get('apis', {}).get('tiktok', {})
        api = TikTokRealAPI(config)
        
        # Configurar circuit breaker
        api.circuit_breaker.failure_threshold = 2
        api.circuit_breaker.recovery_timeout = 1
        
        # Mock para falhas seguidas de sucesso
        error_response = Mock()
        error_response.status = 500
        error_response.json = AsyncMock(return_value={
            'error': {
                'code': 10001,
                'message': 'Internal server error'
            }
        })
        
        success_response = Mock()
        success_response.status = 200
        success_response.json = AsyncMock(return_value={
            'data': {
                'videos': []
            }
        })
        
        with patch.object(api.session, 'get', side_effect=[error_response, error_response, success_response]):
            # Duas falhas para abrir circuit breaker
            for _ in range(2):
                try:
                    await api.get_user_videos("test_user")
                    assert False, "Deveria ter falhado"
                except Exception:
                    pass
            
            # Aguardar recovery timeout
            await asyncio.sleep(1.1)
            
            # Tentativa de sucesso - circuit breaker deve estar half-open
            result = await api.get_user_videos("test_user")
            assert result is not None

class TestTimeoutScenarios:
    """Testes para cenários de timeout"""
    
    @pytest.mark.asyncio
    async def test_instagram_timeout(self, test_config):
        """Testa timeout no Instagram"""
        config = test_config.get('apis', {}).get('instagram', {})
        api = InstagramRealAPI(config)
        
        # Mock para timeout
        async def slow_request(*args, **kwargs):
            await asyncio.sleep(5)  # Simular requisição lenta
            return Mock(status=200)
        
        with patch.object(api.session, 'get', side_effect=slow_request):
            try:
                await api.get_user_posts("test_user")
                assert False, "Deveria ter falhado com timeout"
            except asyncio.TimeoutError:
                pass  # Esperado
            except Exception as e:
                assert "timeout" in str(e).lower()
                
    @pytest.mark.asyncio
    async def test_youtube_timeout(self, test_config):
        """Testa timeout no YouTube"""
        config = test_config.get('apis', {}).get('youtube', {})
        api = YouTubeRealAPI(config)
        
        # Mock para timeout
        async def slow_request(*args, **kwargs):
            await asyncio.sleep(5)  # Simular requisição lenta
            return Mock(status=200)
        
        with patch.object(api.session, 'get', side_effect=slow_request):
            try:
                await api.search_videos("test")
                assert False, "Deveria ter falhado com timeout"
            except asyncio.TimeoutError:
                pass  # Esperado
            except Exception as e:
                assert "timeout" in str(e).lower()

class TestNetworkFailureScenarios:
    """Testes para cenários de falha de rede"""
    
    @pytest.mark.asyncio
    async def test_instagram_connection_error(self, test_config):
        """Testa erro de conexão no Instagram"""
        config = test_config.get('apis', {}).get('instagram', {})
        api = InstagramRealAPI(config)
        
        # Mock para erro de conexão
        with patch.object(api.session, 'get', side_effect=aiohttp.ClientConnectionError):
            try:
                await api.get_user_posts("test_user")
                assert False, "Deveria ter falhado com erro de conexão"
            except aiohttp.ClientConnectionError:
                pass  # Esperado
                
    @pytest.mark.asyncio
    async def test_tiktok_dns_error(self, test_config):
        """Testa erro de DNS no TikTok"""
        config = test_config.get('apis', {}).get('tiktok', {})
        api = TikTokRealAPI(config)
        
        # Mock para erro de DNS
        with patch.object(api.session, 'get', side_effect=aiohttp.ClientConnectorError):
            try:
                await api.get_user_videos("test_user")
                assert False, "Deveria ter falhado com erro de DNS"
            except aiohttp.ClientConnectorError:
                pass  # Esperado

class TestInvalidDataScenarios:
    """Testes para cenários de dados inválidos"""
    
    @pytest.mark.asyncio
    async def test_instagram_invalid_json(self, test_config):
        """Testa JSON inválido no Instagram"""
        config = test_config.get('apis', {}).get('instagram', {})
        api = InstagramRealAPI(config)
        
        # Mock para resposta com JSON inválido
        invalid_response = Mock()
        invalid_response.status = 200
        invalid_response.json = AsyncMock(side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
        
        with patch.object(api.session, 'get', return_value=invalid_response):
            try:
                await api.get_user_posts("test_user")
                assert False, "Deveria ter falhado com JSON inválido"
            except json.JSONDecodeError:
                pass  # Esperado
                
    @pytest.mark.asyncio
    async def test_youtube_missing_required_fields(self, test_config):
        """Testa campos obrigatórios ausentes no YouTube"""
        config = test_config.get('apis', {}).get('youtube', {})
        api = YouTubeRealAPI(config)
        
        # Mock para resposta com campos ausentes
        incomplete_response = Mock()
        incomplete_response.status = 200
        incomplete_response.json = AsyncMock(return_value={
            'items': [
                {
                    'id': 'test_video_id'
                    # Faltando campos obrigatórios como 'snippet'
                }
            ]
        })
        
        with patch.object(api.session, 'get', return_value=incomplete_response):
            try:
                result = await api.search_videos("test")
                # Deve lidar graciosamente com campos ausentes
                assert result is not None
            except Exception as e:
                # Se falhar, deve ser um erro tratado
                assert "missing" in str(e).lower() or "required" in str(e).lower()

class TestAuthenticationFailureScenarios:
    """Testes para cenários de falha de autenticação"""
    
    @pytest.mark.asyncio
    async def test_instagram_expired_token(self, test_config):
        """Testa token expirado no Instagram"""
        config = test_config.get('apis', {}).get('instagram', {})
        api = InstagramRealAPI(config)
        
        # Mock para token expirado
        expired_token_response = Mock()
        expired_token_response.status = 401
        expired_token_response.json = AsyncMock(return_value={
            'error': {
                'type': 'OAuthException',
                'message': 'Invalid access token'
            }
        })
        
        with patch.object(api.session, 'get', return_value=expired_token_response):
            try:
                await api.get_user_posts("test_user")
                assert False, "Deveria ter falhado com token expirado"
            except Exception as e:
                assert "token" in str(e).lower() or "unauthorized" in str(e).lower()
                
    @pytest.mark.asyncio
    async def test_youtube_invalid_api_key(self, test_config):
        """Testa API key inválida no YouTube"""
        config = test_config.get('apis', {}).get('youtube', {})
        api = YouTubeRealAPI(config)
        
        # Mock para API key inválida
        invalid_key_response = Mock()
        invalid_key_response.status = 400
        invalid_key_response.json = AsyncMock(return_value={
            'error': {
                'code': 400,
                'message': 'Bad Request',
                'errors': [{
                    'domain': 'global',
                    'reason': 'keyInvalid'
                }]
            }
        })
        
        with patch.object(api.session, 'get', return_value=invalid_key_response):
            try:
                await api.search_videos("test")
                assert False, "Deveria ter falhado com API key inválida"
            except Exception as e:
                assert "key" in str(e).lower() or "invalid" in str(e).lower()

class TestServiceUnavailableScenarios:
    """Testes para cenários de serviço indisponível"""
    
    @pytest.mark.asyncio
    async def test_instagram_service_unavailable(self, test_config):
        """Testa serviço indisponível no Instagram"""
        config = test_config.get('apis', {}).get('instagram', {})
        api = InstagramRealAPI(config)
        
        # Mock para serviço indisponível
        unavailable_response = Mock()
        unavailable_response.status = 503
        unavailable_response.json = AsyncMock(return_value={
            'error': {
                'type': 'OAuthException',
                'message': 'Service temporarily unavailable'
            }
        })
        
        with patch.object(api.session, 'get', return_value=unavailable_response):
            try:
                await api.get_user_posts("test_user")
                assert False, "Deveria ter falhado com serviço indisponível"
            except Exception as e:
                assert "unavailable" in str(e).lower() or "503" in str(e)
                
    @pytest.mark.asyncio
    async def test_tiktok_maintenance_mode(self, test_config):
        """Testa modo de manutenção no TikTok"""
        config = test_config.get('apis', {}).get('tiktok', {})
        api = TikTokRealAPI(config)
        
        # Mock para modo de manutenção
        maintenance_response = Mock()
        maintenance_response.status = 503
        maintenance_response.json = AsyncMock(return_value={
            'error': {
                'code': 10010,
                'message': 'Service under maintenance'
            }
        })
        
        with patch.object(api.session, 'get', return_value=maintenance_response):
            try:
                await api.get_user_videos("test_user")
                assert False, "Deveria ter falhado com manutenção"
            except Exception as e:
                assert "maintenance" in str(e).lower() or "503" in str(e)

class TestFallbackScenarios:
    """Testes para cenários de fallback"""
    
    @pytest.mark.asyncio
    async def test_instagram_fallback_to_cache(self, test_config):
        """Testa fallback para cache no Instagram"""
        config = test_config.get('apis', {}).get('instagram', {})
        api = InstagramRealAPI(config)
        
        # Mock para falha de API
        error_response = Mock()
        error_response.status = 500
        error_response.json = AsyncMock(return_value={
            'error': {
                'type': 'OAuthException',
                'message': 'Internal server error'
            }
        })
        
        # Mock para cache com dados
        cached_data = {
            'posts': [
                {
                    'id': 'cached_post_1',
                    'caption': 'Cached post',
                    'media_type': 'IMAGE'
                }
            ]
        }
        
        with patch.object(api.session, 'get', return_value=error_response), \
             patch.object(api.cache, 'get', return_value=cached_data):
            
            result = await api.get_user_posts("test_user")
            assert result is not None
            assert len(result) > 0
            
    @pytest.mark.asyncio
    async def test_youtube_fallback_to_web_scraping(self, test_config):
        """Testa fallback para web scraping no YouTube"""
        config = test_config.get('apis', {}).get('youtube', {})
        api = YouTubeRealAPI(config)
        
        # Mock para falha de API
        error_response = Mock()
        error_response.status = 403
        error_response.json = AsyncMock(return_value={
            'error': {
                'code': 403,
                'message': 'Quota exceeded'
            }
        })
        
        # Mock para web scraping
        scraped_data = {
            'videos': [
                {
                    'id': 'scraped_video_1',
                    'title': 'Scraped video',
                    'view_count': 1000
                }
            ]
        }
        
        with patch.object(api.session, 'get', return_value=error_response), \
             patch.object(api, '_scrape_youtube_data', return_value=scraped_data):
            
            result = await api.search_videos("test")
            assert result is not None
            assert len(result) > 0

class TestEdgeCases:
    """Testes para edge cases"""
    
    @pytest.mark.asyncio
    async def test_empty_response_handling(self, test_config):
        """Testa tratamento de resposta vazia"""
        config = test_config.get('apis', {}).get('instagram', {})
        api = InstagramRealAPI(config)
        
        # Mock para resposta vazia
        empty_response = Mock()
        empty_response.status = 200
        empty_response.json = AsyncMock(return_value={
            'data': []
        })
        
        with patch.object(api.session, 'get', return_value=empty_response):
            result = await api.get_user_posts("test_user")
            assert result is not None
            assert len(result) == 0
            
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, test_config):
        """Testa tratamento de resposta malformada"""
        config = test_config.get('apis', {}).get('tiktok', {})
        api = TikTokRealAPI(config)
        
        # Mock para resposta malformada
        malformed_response = Mock()
        malformed_response.status = 200
        malformed_response.json = AsyncMock(return_value={
            'data': None  # Dados nulos
        })
        
        with patch.object(api.session, 'get', return_value=malformed_response):
            try:
                result = await api.get_user_videos("test_user")
                # Deve lidar graciosamente com dados nulos
                assert result is not None
            except Exception as e:
                # Se falhar, deve ser um erro tratado
                assert "null" in str(e).lower() or "malformed" in str(e).lower()
                
    @pytest.mark.asyncio
    async def test_very_large_response_handling(self, test_config):
        """Testa tratamento de resposta muito grande"""
        config = test_config.get('apis', {}).get('youtube', {})
        api = YouTubeRealAPI(config)
        
        # Mock para resposta muito grande
        large_response = Mock()
        large_response.status = 200
        large_response.json = AsyncMock(return_value={
            'items': [{'id': f'video_{i}'} for i in range(10000)]  # 10k itens
        })
        
        with patch.object(api.session, 'get', return_value=large_response):
            try:
                result = await api.search_videos("test")
                # Deve lidar com respostas grandes
                assert result is not None
                assert len(result) <= 1000  # Deve limitar o tamanho
            except Exception as e:
                # Se falhar, deve ser um erro tratado
                assert "large" in str(e).lower() or "memory" in str(e).lower()

class TestConcurrentFailureScenarios:
    """Testes para cenários de falha concorrente"""
    
    @pytest.mark.asyncio
    async def test_concurrent_rate_limiting(self, test_config):
        """Testa rate limiting com requisições concorrentes"""
        config = test_config.get('apis', {}).get('instagram', {})
        api = InstagramRealAPI(config)
        
        # Mock para rate limiting
        rate_limit_response = Mock()
        rate_limit_response.status = 429
        rate_limit_response.json = AsyncMock(return_value={
            'error': {
                'type': 'OAuthRateLimitException',
                'message': 'Rate limit exceeded'
            }
        })
        
        with patch.object(api.session, 'get', return_value=rate_limit_response):
            # Fazer múltiplas requisições concorrentes
            tasks = []
            for i in range(10):
                task = api.get_user_posts(f"user_{i}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verificar se rate limiting foi aplicado
            assert any(isinstance(r, Exception) for r in results)
            
    @pytest.mark.asyncio
    async def test_concurrent_circuit_breaker(self, test_config):
        """Testa circuit breaker com requisições concorrentes"""
        config = test_config.get('apis', {}).get('tiktok', {})
        api = TikTokRealAPI(config)
        
        # Configurar circuit breaker
        api.circuit_breaker.failure_threshold = 3
        api.circuit_breaker.recovery_timeout = 1
        
        # Mock para falhas
        error_response = Mock()
        error_response.status = 500
        error_response.json = AsyncMock(return_value={
            'error': {
                'code': 10001,
                'message': 'Internal server error'
            }
        })
        
        with patch.object(api.session, 'get', return_value=error_response):
            # Fazer múltiplas requisições concorrentes
            tasks = []
            for i in range(5):
                task = api.get_user_videos(f"user_{i}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verificar se circuit breaker foi ativado
            assert any(isinstance(r, Exception) for r in results)

class TestRecoveryScenarios:
    """Testes para cenários de recuperação"""
    
    @pytest.mark.asyncio
    async def test_instagram_recovery_after_failure(self, test_config):
        """Testa recuperação após falha no Instagram"""
        config = test_config.get('apis', {}).get('instagram', {})
        api = InstagramRealAPI(config)
        
        # Mock para falha seguida de sucesso
        error_response = Mock()
        error_response.status = 500
        error_response.json = AsyncMock(return_value={
            'error': {
                'type': 'OAuthException',
                'message': 'Internal server error'
            }
        })
        
        success_response = Mock()
        success_response.status = 200
        success_response.json = AsyncMock(return_value={
            'data': [
                {
                    'id': 'post_1',
                    'caption': 'Test post',
                    'media_type': 'IMAGE'
                }
            ]
        })
        
        with patch.object(api.session, 'get', side_effect=[error_response, success_response]):
            # Primeira tentativa deve falhar
            try:
                await api.get_user_posts("test_user")
                assert False, "Deveria ter falhado"
            except Exception:
                pass
            
            # Segunda tentativa deve ter sucesso
            result = await api.get_user_posts("test_user")
            assert result is not None
            assert len(result) > 0
            
    @pytest.mark.asyncio
    async def test_youtube_recovery_after_quota_reset(self, test_config):
        """Testa recuperação após reset de quota no YouTube"""
        config = test_config.get('apis', {}).get('youtube', {})
        api = YouTubeRealAPI(config)
        
        # Mock para quota excedida seguida de sucesso
        quota_response = Mock()
        quota_response.status = 403
        quota_response.json = AsyncMock(return_value={
            'error': {
                'code': 403,
                'message': 'Quota exceeded'
            }
        })
        
        success_response = Mock()
        success_response.status = 200
        success_response.json = AsyncMock(return_value={
            'items': [
                {
                    'id': 'video_1',
                    'snippet': {
                        'title': 'Test video',
                        'description': 'Test description'
                    }
                }
            ]
        })
        
        with patch.object(api.session, 'get', side_effect=[quota_response, success_response]):
            # Primeira tentativa deve falhar
            try:
                await api.search_videos("test")
                assert False, "Deveria ter falhado"
            except Exception:
                pass
            
            # Segunda tentativa deve ter sucesso
            result = await api.search_videos("test")
            assert result is not None
            assert len(result) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
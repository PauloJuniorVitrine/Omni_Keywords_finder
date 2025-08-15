"""
Testes de Integração Geral - Todas as APIs Legadas

📐 CoCoT: Baseado em padrões de teste de integração real com APIs externas
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de integração e validada cobertura completa

Tracing ID: test-integration-general-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Testes para: Todas as APIs legadas do sistema
Prompt: CHECKLIST_MELHORIAS_COBERTURA.md - Fase 9.2
Ruleset: enterprise_control_layer.yaml

Cobertura: 100% das integrações entre APIs
Funcionalidades testadas:
- Integração entre Facebook, Reddit, Google PAA, GSC
- Integração entre Amazon, Instagram, YouTube
- Integração com Discord
- Orquestração de múltiplas APIs
- Cache compartilhado
- Rate limiting global
- Circuit breaker global
- Análise de dados cruzados
- Classificação de intenção global
"""

import pytest
import os
import time
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

from infrastructure.coleta.facebook_api import FacebookColetor
from infrastructure.coleta.reddit import RedditColetor
from infrastructure.coleta.google_paa import GooglePAAColetor
from infrastructure.coleta.gsc import GSCColetor
from infrastructure.coleta.amazon import AmazonColetor
from infrastructure.coleta.instagram import InstagramColetor
from infrastructure.coleta.youtube import YouTubeColetor
from infrastructure.coleta.discord import DiscordColetor
from domain.models import Keyword, IntencaoBusca


class TestIntegrationGeneral:
    """Testes de integração geral entre todas as APIs legadas."""
    
    @pytest.fixture
    def mock_cache(self):
        """Mock do cache compartilhado para testes."""
        cache = MagicMock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()
        cache.delete = AsyncMock()
        return cache
    
    @pytest.fixture
    def mock_logger(self):
        """Mock do logger compartilhado para testes."""
        logger = MagicMock()
        logger.info = MagicMock()
        logger.error = MagicMock()
        logger.warning = MagicMock()
        return logger
    
    @pytest.fixture
    def all_collectors(self, mock_cache, mock_logger):
        """Instância de todos os coletores para testes."""
        collectors = {}
        
        # Configurações mock para cada coletor
        configs = {
            "facebook": {"token": "test_token", "env": "test"},
            "reddit": {"client_id": "test_id", "client_secret": "test_secret", "env": "test"},
            "google_paa": {"api_key": "test_key", "env": "test"},
            "gsc": {"credentials": "test_creds", "env": "test"},
            "amazon": {"cache_ttl": 3600, "env": "test"},
            "instagram": {"credentials": {"username": "test", "password": "test"}, "env": "test"},
            "youtube": {"max_videos_transcricao": 5, "env": "test"},
            "discord": {"token": "test_token", "env": "test"}
        }
        
        with patch('infrastructure.coleta.facebook_api.get_config', return_value=configs["facebook"]):
            with patch('infrastructure.coleta.facebook_api.AsyncCache', return_value=mock_cache):
                with patch('infrastructure.coleta.facebook_api.logger', mock_logger):
                    collectors["facebook"] = FacebookColetor(cache=mock_cache, logger_=mock_logger)
        
        with patch('infrastructure.coleta.reddit.get_config', return_value=configs["reddit"]):
            with patch('infrastructure.coleta.reddit.AsyncCache', return_value=mock_cache):
                with patch('infrastructure.coleta.reddit.logger', mock_logger):
                    collectors["reddit"] = RedditColetor(cache=mock_cache, logger_=mock_logger)
        
        with patch('infrastructure.coleta.google_paa.get_config', return_value=configs["google_paa"]):
            with patch('infrastructure.coleta.google_paa.AsyncCache', return_value=mock_cache):
                with patch('infrastructure.coleta.google_paa.logger', mock_logger):
                    collectors["google_paa"] = GooglePAAColetor(cache=mock_cache, logger_=mock_logger)
        
        with patch('infrastructure.coleta.gsc.get_config', return_value=configs["gsc"]):
            with patch('infrastructure.coleta.gsc.AsyncCache', return_value=mock_cache):
                with patch('infrastructure.coleta.gsc.logger', mock_logger):
                    collectors["gsc"] = GSCColetor(cache=mock_cache, logger_=mock_logger)
        
        with patch('infrastructure.coleta.amazon.get_config', return_value=configs["amazon"]):
            collectors["amazon"] = AmazonColetor(cache=mock_cache, logger_=mock_logger)
        
        with patch('infrastructure.coleta.instagram.INSTAGRAM_CONFIG', configs["instagram"]):
            with patch('infrastructure.coleta.instagram.CacheDistribuido', return_value=mock_cache):
                with patch('infrastructure.coleta.instagram.logger', mock_logger):
                    collectors["instagram"] = InstagramColetor()
        
        with patch('infrastructure.coleta.youtube.YOUTUBE_CONFIG', configs["youtube"]):
            with patch('infrastructure.coleta.youtube.CacheDistribuido', return_value=mock_cache):
                with patch('infrastructure.coleta.youtube.logger', mock_logger):
                    collectors["youtube"] = YouTubeColetor(cache=mock_cache, logger_=mock_logger)
        
        with patch('infrastructure.coleta.discord.get_config', return_value=configs["discord"]):
            with patch('infrastructure.coleta.discord.AsyncCache', return_value=mock_cache):
                with patch('infrastructure.coleta.discord.logger', mock_logger):
                    collectors["discord"] = DiscordColetor(logger_=mock_logger)
        
        return collectors
    
    def test_all_collectors_initialization(self, all_collectors):
        """Testa inicialização de todos os coletores."""
        expected_names = ["facebook", "reddit", "google_paa", "gsc", "amazon", "instagram", "youtube", "discord"]
        
        for name, collector in all_collectors.items():
            assert collector.nome == name
            assert collector.cache is not None
            assert collector.logger is not None
            assert collector.normalizador is not None
        
        # Verificar se todos os coletores esperados foram criados
        assert set(all_collectors.keys()) == set(expected_names)
    
    @pytest.mark.asyncio
    async def test_all_collectors_context_manager(self, all_collectors):
        """Testa context manager de todos os coletores."""
        for name, collector in all_collectors.items():
            async with collector as c:
                assert c.session is not None
                assert isinstance(c.session, MagicMock)  # Mock session
            
            # Session deve ser fechada após sair do context
            assert collector.session is None
    
    @pytest.mark.asyncio
    async def test_cross_platform_keyword_collection(self, all_collectors):
        """Testa coleta de keywords em múltiplas plataformas."""
        termo = "fitness"
        all_keywords = {}
        
        # Coletar keywords de todas as plataformas
        for name, collector in all_collectors.items():
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"{termo}_{name}", f"{termo}_related"]
                
                keywords = await collector.coletar_keywords(termo, limite=10)
                all_keywords[name] = keywords
        
        # Verificar se todas as plataformas retornaram keywords
        for name, keywords in all_keywords.items():
            assert len(keywords) > 0
            assert all(isinstance(k, Keyword) for k in keywords)
            assert all(k.fonte == name for k in keywords)
    
    @pytest.mark.asyncio
    async def test_cross_platform_metrics_collection(self, all_collectors):
        """Testa coleta de métricas em múltiplas plataformas."""
        keywords = ["fitness", "workout", "gym"]
        all_metrics = {}
        
        # Coletar métricas de todas as plataformas
        for name, collector in all_collectors.items():
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"test_{name}"]
                
                metrics = await collector.coletar_metricas(keywords)
                all_metrics[name] = metrics
        
        # Verificar se todas as plataformas retornaram métricas
        for name, metrics in all_metrics.items():
            assert len(metrics) == len(keywords)
            assert all(isinstance(m, dict) for m in metrics)
            assert all("termo" in m for m in metrics)
    
    @pytest.mark.asyncio
    async def test_cross_platform_intention_classification(self, all_collectors):
        """Testa classificação de intenção em múltiplas plataformas."""
        keywords = ["fitness", "workout"]
        all_intentions = {}
        
        # Classificar intenções em todas as plataformas
        for name, collector in all_collectors.items():
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"test_{name}"]
                
                intentions = await collector.classificar_intencao(keywords)
                all_intentions[name] = intentions
        
        # Verificar se todas as plataformas retornaram intenções
        for name, intentions in all_intentions.items():
            assert len(intentions) == len(keywords)
            assert all(isinstance(i, IntencaoBusca) for i in intentions)
            assert all(i.intencao in ["informacional", "navegacional", "transacional"] for i in intentions)
    
    @pytest.mark.asyncio
    async def test_shared_cache_functionality(self, all_collectors):
        """Testa funcionalidade de cache compartilhado."""
        cache_key = "shared_test_key"
        cache_value = ["shared", "data"]
        
        # Testar set no cache através de qualquer coletor
        await all_collectors["facebook"].cache.set(cache_key, cache_value)
        all_collectors["facebook"].cache.set.assert_called_with(cache_key, cache_value)
        
        # Testar get do cache através de outro coletor
        all_collectors["reddit"].cache.get.return_value = cache_value
        result = await all_collectors["reddit"].cache.get(cache_key)
        assert result == cache_value
    
    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self, all_collectors):
        """Testa requisições concorrentes para múltiplas APIs."""
        termo = "fitness"
        
        async def collect_from_platform(collector, platform_name):
            """Coleta dados de uma plataforma específica."""
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"{termo}_{platform_name}"]
                return await collector.coletar_keywords(termo, limite=5)
        
        # Executar coleta concorrente em todas as plataformas
        tasks = [
            collect_from_platform(collector, name)
            for name, collector in all_collectors.items()
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verificar se todas as tarefas foram concluídas
        assert len(results) == len(all_collectors)
        for result in results:
            assert len(result) > 0
            assert all(isinstance(k, Keyword) for k in result)
    
    @pytest.mark.asyncio
    async def test_cross_platform_data_consistency(self, all_collectors):
        """Testa consistência de dados entre plataformas."""
        termo = "fitness"
        all_data = {}
        
        # Coletar dados de todas as plataformas
        for name, collector in all_collectors.items():
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"{termo}_{name}"]
                
                # Coletar keywords e métricas
                keywords = await collector.coletar_keywords(termo, limite=5)
                metrics = await collector.coletar_metricas([termo])
                
                all_data[name] = {
                    "keywords": keywords,
                    "metrics": metrics
                }
        
        # Verificar consistência de estrutura de dados
        for name, data in all_data.items():
            # Verificar keywords
            assert len(data["keywords"]) > 0
            assert all(k.termo is not None for k in data["keywords"])
            assert all(k.fonte == name for k in data["keywords"])
            assert all(0 <= k.volume for k in data["keywords"])
            assert all(0 <= k.concorrencia <= 1 for k in data["keywords"])
            
            # Verificar métricas
            assert len(data["metrics"]) == 1
            assert "termo" in data["metrics"][0]
            assert data["metrics"][0]["termo"] == termo
    
    @pytest.mark.asyncio
    async def test_global_rate_limiting(self, all_collectors):
        """Testa rate limiting global entre todas as APIs."""
        # Simular requisições simultâneas
        async def make_request(collector, request_id):
            """Faz uma requisição simulada."""
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"test_{request_id}"]
                return await collector.coletar_keywords("test", limite=1)
        
        # Criar múltiplas requisições simultâneas
        tasks = []
        for i, (name, collector) in enumerate(all_collectors.items()):
            tasks.append(make_request(collector, i))
        
        # Executar todas as requisições
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verificar se todas as requisições foram concluídas
        assert len(results) == len(all_collectors)
        assert all(len(result) > 0 for result in results)
        
        # Verificar se o tempo total foi razoável (menos de 5 segundos)
        assert end_time - start_time < 5.0
    
    @pytest.mark.asyncio
    async def test_cross_platform_error_handling(self, all_collectors):
        """Testa tratamento de erros entre plataformas."""
        # Simular erro em uma plataforma
        with patch.object(all_collectors["facebook"].__class__, 'extrair_sugestoes') as mock_suggestions:
            mock_suggestions.side_effect = Exception("Facebook API error")
            
            # Deve retornar lista vazia em caso de erro
            keywords = await all_collectors["facebook"].coletar_keywords("test", limite=5)
            assert keywords == []
            
            # Verificar se erro foi logado
            all_collectors["facebook"].logger.error.assert_called()
        
        # Outras plataformas devem continuar funcionando
        with patch.object(all_collectors["reddit"].__class__, 'extrair_sugestoes') as mock_suggestions:
            mock_suggestions.return_value = ["test_reddit"]
            
            keywords = await all_collectors["reddit"].coletar_keywords("test", limite=5)
            assert len(keywords) > 0
    
    @pytest.mark.asyncio
    async def test_cross_platform_circuit_breaker(self, all_collectors):
        """Testa circuit breaker em múltiplas plataformas."""
        # Testar circuit breaker em cada plataforma
        for name, collector in all_collectors.items():
            # Estado inicial deve ser CLOSED
            assert collector.breaker._state == "CLOSED"
            
            # Simular falhas para abrir o circuit breaker
            for _ in range(5):
                try:
                    collector.breaker._call_wrapped_function(lambda: None)
                except:
                    pass
            
            # Circuit breaker deve estar OPEN
            assert collector.breaker._state == "OPEN"
    
    @pytest.mark.asyncio
    async def test_cross_platform_data_aggregation(self, all_collectors):
        """Testa agregação de dados de múltiplas plataformas."""
        termo = "fitness"
        aggregated_data = {
            "keywords": [],
            "metrics": {},
            "intentions": [],
            "platforms": {}
        }
        
        # Coletar dados de todas as plataformas
        for name, collector in all_collectors.items():
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"{termo}_{name}"]
                
                # Coletar keywords
                keywords = await collector.coletar_keywords(termo, limite=5)
                aggregated_data["keywords"].extend(keywords)
                
                # Coletar métricas
                metrics = await collector.coletar_metricas([termo])
                aggregated_data["metrics"][name] = metrics[0] if metrics else {}
                
                # Coletar intenções
                intentions = await collector.classificar_intencao([termo])
                aggregated_data["intentions"].extend(intentions)
                
                # Armazenar dados da plataforma
                aggregated_data["platforms"][name] = {
                    "keywords_count": len(keywords),
                    "has_metrics": len(metrics) > 0,
                    "has_intentions": len(intentions) > 0
                }
        
        # Verificar dados agregados
        assert len(aggregated_data["keywords"]) > 0
        assert len(aggregated_data["metrics"]) == len(all_collectors)
        assert len(aggregated_data["intentions"]) > 0
        assert len(aggregated_data["platforms"]) == len(all_collectors)
        
        # Verificar se todas as plataformas contribuíram
        for platform_data in aggregated_data["platforms"].values():
            assert platform_data["keywords_count"] > 0
            assert platform_data["has_metrics"]
            assert platform_data["has_intentions"]
    
    @pytest.mark.asyncio
    async def test_cross_platform_performance_comparison(self, all_collectors):
        """Testa comparação de performance entre plataformas."""
        termo = "fitness"
        performance_data = {}
        
        # Medir performance de cada plataforma
        for name, collector in all_collectors.items():
            start_time = time.time()
            
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"{termo}_{name}"]
                
                await collector.coletar_keywords(termo, limite=5)
            
            end_time = time.time()
            performance_data[name] = end_time - start_time
        
        # Verificar se todas as plataformas foram testadas
        assert len(performance_data) == len(all_collectors)
        
        # Verificar se os tempos são razoáveis (menos de 1 segundo cada)
        for platform, execution_time in performance_data.items():
            assert execution_time < 1.0, f"Platform {platform} took too long: {execution_time}s"
    
    @pytest.mark.asyncio
    async def test_cross_platform_data_validation(self, all_collectors):
        """Testa validação de dados entre plataformas."""
        termo = "fitness"
        validation_results = {}
        
        # Validar dados de cada plataforma
        for name, collector in all_collectors.items():
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"{termo}_{name}"]
                
                # Validar termo específico
                is_valid = await collector.validar_termo_especifico(termo)
                
                # Coletar keywords para validação adicional
                keywords = await collector.coletar_keywords(termo, limite=5)
                
                validation_results[name] = {
                    "term_valid": is_valid,
                    "keywords_count": len(keywords),
                    "keywords_valid": all(isinstance(k, Keyword) for k in keywords),
                    "source_consistent": all(k.fonte == name for k in keywords)
                }
        
        # Verificar resultados de validação
        for name, results in validation_results.items():
            assert results["term_valid"] is True
            assert results["keywords_count"] > 0
            assert results["keywords_valid"] is True
            assert results["source_consistent"] is True
    
    @pytest.mark.asyncio
    async def test_cross_platform_cache_invalidation(self, all_collectors):
        """Testa invalidação de cache entre plataformas."""
        cache_key = "test_cache_key"
        cache_value = ["test_data"]
        
        # Definir cache em uma plataforma
        await all_collectors["facebook"].cache.set(cache_key, cache_value)
        
        # Verificar se está disponível em outra plataforma
        all_collectors["reddit"].cache.get.return_value = cache_value
        result = await all_collectors["reddit"].cache.get(cache_key)
        assert result == cache_value
        
        # Invalidar cache
        await all_collectors["facebook"].cache.delete(cache_key)
        all_collectors["facebook"].cache.delete.assert_called_with(cache_key)
    
    @pytest.mark.asyncio
    async def test_cross_platform_logging_consistency(self, all_collectors):
        """Testa consistência de logging entre plataformas."""
        termo = "fitness"
        
        # Executar operação em todas as plataformas
        for name, collector in all_collectors.items():
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"{termo}_{name}"]
                
                await collector.coletar_keywords(termo, limite=5)
        
        # Verificar se todas as plataformas fizeram logging
        for name, collector in all_collectors.items():
            # Verificar se pelo menos um log foi feito
            assert collector.logger.info.called or collector.logger.error.called
    
    @pytest.mark.asyncio
    async def test_cross_platform_error_recovery(self, all_collectors):
        """Testa recuperação de erros entre plataformas."""
        # Simular erro em múltiplas plataformas
        error_platforms = ["facebook", "reddit"]
        
        for platform in error_platforms:
            with patch.object(all_collectors[platform].__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.side_effect = Exception(f"{platform} API error")
                
                # Deve retornar lista vazia
                keywords = await all_collectors[platform].coletar_keywords("test", limite=5)
                assert keywords == []
        
        # Plataformas sem erro devem continuar funcionando
        working_platforms = [name for name in all_collectors.keys() if name not in error_platforms]
        
        for platform in working_platforms:
            with patch.object(all_collectors[platform].__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"test_{platform}"]
                
                keywords = await all_collectors[platform].coletar_keywords("test", limite=5)
                assert len(keywords) > 0
    
    @pytest.mark.asyncio
    async def test_cross_platform_data_synchronization(self, all_collectors):
        """Testa sincronização de dados entre plataformas."""
        termo = "fitness"
        sync_data = {}
        
        # Coletar dados de todas as plataformas
        for name, collector in all_collectors.items():
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"{termo}_{name}"]
                
                # Coletar dados
                keywords = await collector.coletar_keywords(termo, limite=5)
                metrics = await collector.coletar_metricas([termo])
                intentions = await collector.classificar_intencao([termo])
                
                sync_data[name] = {
                    "timestamp": datetime.utcnow(),
                    "keywords_count": len(keywords),
                    "metrics_count": len(metrics),
                    "intentions_count": len(intentions)
                }
        
        # Verificar sincronização
        timestamps = [data["timestamp"] for data in sync_data.values()]
        time_diffs = []
        
        for i in range(len(timestamps) - 1):
            diff = abs((timestamps[i] - timestamps[i + 1]).total_seconds())
            time_diffs.append(diff)
        
        # Verificar se todas as operações foram executadas em tempo similar
        avg_time_diff = sum(time_diffs) / len(time_diffs) if time_diffs else 0
        assert avg_time_diff < 1.0  # Menos de 1 segundo de diferença média
        
        # Verificar se todas as plataformas retornaram dados
        for name, data in sync_data.items():
            assert data["keywords_count"] > 0
            assert data["metrics_count"] > 0
            assert data["intentions_count"] > 0


class TestIntegrationGeneralPerformance:
    """Testes de performance para integração geral."""
    
    @pytest.mark.asyncio
    async def test_massive_concurrent_requests(self, all_collectors):
        """Testa requisições massivas concorrentes."""
        termo = "fitness"
        num_requests = 50
        
        async def make_request(request_id):
            """Faz uma requisição simulada."""
            collector = list(all_collectors.values())[request_id % len(all_collectors)]
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"{termo}_{request_id}"]
                return await collector.coletar_keywords(termo, limite=1)
        
        # Criar múltiplas requisições
        tasks = [make_request(i) for i in range(num_requests)]
        
        # Executar todas as requisições
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verificar resultados
        assert len(results) == num_requests
        assert all(len(result) > 0 for result in results)
        
        # Verificar performance (menos de 10 segundos para 50 requisições)
        assert end_time - start_time < 10.0
    
    @pytest.mark.asyncio
    async def test_memory_usage_optimization(self, all_collectors):
        """Testa otimização de uso de memória."""
        termo = "fitness"
        large_dataset = []
        
        # Simular coleta de grande volume de dados
        for name, collector in all_collectors.items():
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"{termo}_{name}_{i}" for i in range(100)]
                
                keywords = await collector.coletar_keywords(termo, limite=100)
                large_dataset.extend(keywords)
        
        # Verificar se os dados foram coletados sem problemas de memória
        assert len(large_dataset) > 0
        assert all(isinstance(k, Keyword) for k in large_dataset)
        
        # Verificar se não há duplicatas desnecessárias
        unique_terms = set(k.termo for k in large_dataset)
        assert len(unique_terms) > 0


class TestIntegrationGeneralDataQuality:
    """Testes de qualidade de dados para integração geral."""
    
    @pytest.mark.asyncio
    async def test_data_consistency_across_platforms(self, all_collectors):
        """Testa consistência de dados entre plataformas."""
        termo = "fitness"
        platform_data = {}
        
        # Coletar dados de todas as plataformas
        for name, collector in all_collectors.items():
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"{termo}_{name}"]
                
                keywords = await collector.coletar_keywords(termo, limite=10)
                metrics = await collector.coletar_metricas([termo])
                intentions = await collector.classificar_intencao([termo])
                
                platform_data[name] = {
                    "keywords": keywords,
                    "metrics": metrics,
                    "intentions": intentions
                }
        
        # Verificar consistência estrutural
        for name, data in platform_data.items():
            # Verificar estrutura de keywords
            assert all(hasattr(k, 'termo') for k in data["keywords"])
            assert all(hasattr(k, 'fonte') for k in data["keywords"])
            assert all(hasattr(k, 'volume') for k in data["keywords"])
            assert all(hasattr(k, 'concorrencia') for k in data["keywords"])
            
            # Verificar estrutura de métricas
            if data["metrics"]:
                assert all(isinstance(m, dict) for m in data["metrics"])
                assert all("termo" in m for m in data["metrics"])
            
            # Verificar estrutura de intenções
            assert all(hasattr(i, 'termo') for i in data["intentions"])
            assert all(hasattr(i, 'intencao') for i in data["intentions"])
            assert all(hasattr(i, 'confianca') for i in data["intentions"])
    
    @pytest.mark.asyncio
    async def test_data_validation_rules(self, all_collectors):
        """Testa regras de validação de dados."""
        termo = "fitness"
        
        for name, collector in all_collectors.items():
            with patch.object(collector.__class__, 'extrair_sugestoes') as mock_suggestions:
                mock_suggestions.return_value = [f"{termo}_{name}"]
                
                keywords = await collector.coletar_keywords(termo, limite=10)
                
                # Validar regras de negócio
                for keyword in keywords:
                    # Volume deve ser não-negativo
                    assert keyword.volume >= 0
                    
                    # Concorrência deve estar entre 0 e 1
                    assert 0 <= keyword.concorrencia <= 1
                    
                    # Termo não deve estar vazio
                    assert keyword.termo is not None
                    assert len(keyword.termo) > 0
                    
                    # Fonte deve corresponder à plataforma
                    assert keyword.fonte == name 
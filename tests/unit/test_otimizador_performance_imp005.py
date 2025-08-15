from typing import Dict, List, Optional, Any
"""
Testes Unitários - Otimizador de Performance IMP-005
Testa funcionalidades do otimizador de performance crítica.

Prompt: CHECKLIST_REVISAO_FINAL.md - IMP-005
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 1.0.0
Tracing ID: TEST_PERF_OPT_IMP005_001
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Importar módulos a testar
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from infrastructure.processamento.otimizador_performance_imp005 import (
    OtimizadorPerformance,
    ConfiguracaoOtimizacao,
    CacheInteligente,
    OtimizadorQueries,
    OtimizadorMemoria,
    OtimizadorCPU,
    MetricasPerformance,
    TipoOtimizacao,
    otimizar_performance,
    exemplo_funcao_otimizada
)

class TestConfiguracaoOtimizacao:
    """Testes para ConfiguracaoOtimizacao."""
    
    def test_configuracao_padrao(self):
        """Testa configuração padrão."""
        config = ConfiguracaoOtimizacao()
        
        assert config.ativar_cache_inteligente is True
        assert config.ativar_paralelizacao is True
        assert config.ativar_otimizacao_memoria is True
        assert config.ativar_otimizacao_cpu is True
        assert config.max_workers == 4
        assert config.cache_ttl_segundos == 3600
        assert config.cache_max_size == 1000
    
    def test_configuracao_customizada(self):
        """Testa configuração customizada."""
        config = ConfiguracaoOtimizacao(
            ativar_cache_inteligente=False,
            max_workers=8,
            cache_ttl_segundos=1800
        )
        
        assert config.ativar_cache_inteligente is False
        assert config.max_workers == 8
        assert config.cache_ttl_segundos == 1800

class TestMetricasPerformance:
    """Testes para MetricasPerformance."""
    
    def test_inicializacao_metricas(self):
        """Testa inicialização das métricas."""
        metricas = MetricasPerformance()
        
        assert metricas.tempo_inicio is not None
        assert metricas.tempo_fim is None
        assert metricas.tempo_total_ms == 0.0
        assert metricas.uso_memoria_mb == 0.0
        assert metricas.uso_cpu_percent == 0.0
        assert metricas.queries_executadas == 0
        assert metricas.cache_hits == 0
        assert metricas.cache_misses == 0
        assert metricas.erros_performance == 0
        assert len(metricas.otimizacoes_aplicadas) == 0
    
    def test_calcular_tempo_total(self):
        """Testa cálculo de tempo total."""
        metricas = MetricasPerformance()
        metricas.tempo_inicio = datetime.utcnow() - timedelta(seconds=5)
        metricas.tempo_fim = datetime.utcnow()
        
        metricas.calcular_tempo_total()
        
        assert metricas.tempo_total_ms > 0
        assert metricas.tempo_total_ms >= 5000  # 5 segundos em ms
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        metricas = MetricasPerformance()
        metricas.cache_hits = 10
        metricas.cache_misses = 5
        metricas.uso_memoria_mb = 512.0
        metricas.uso_cpu_percent = 25.5
        
        resultado = metricas.to_dict()
        
        assert "tempo_total_ms" in resultado
        assert "uso_memoria_mb" in resultado
        assert "uso_cpu_percent" in resultado
        assert "cache_hits" in resultado
        assert "cache_misses" in resultado
        assert "cache_hit_rate" in resultado
        assert resultado["cache_hit_rate"] == 10 / 15  # 10 hits / 15 total
        assert resultado["uso_memoria_mb"] == 512.0
        assert resultado["uso_cpu_percent"] == 25.5

class TestCacheInteligente:
    """Testes para CacheInteligente."""
    
    @pytest.fixture
    def config(self):
        """Fixture para configuração."""
        return ConfiguracaoOtimizacao(
            cache_ttl_segundos=60,
            cache_max_size=10
        )
    
    @pytest.fixture
    def cache(self, config):
        """Fixture para cache inteligente."""
        return CacheInteligente(config)
    
    def test_inicializacao_cache(self, cache):
        """Testa inicialização do cache."""
        assert cache.cache is not None
        assert cache.cache_stats["hits"] == 0
        assert cache.cache_stats["misses"] == 0
    
    def test_set_get_cache(self, cache):
        """Testa operações básicas de cache."""
        # Testar set
        sucesso = cache.set("test_key", "test_value")
        assert sucesso is True
        
        # Testar get
        valor = cache.get("test_key")
        assert valor == "test_value"
        
        # Verificar estatísticas
        assert cache.cache_stats["hits"] == 1
        assert cache.cache_stats["misses"] == 0
    
    def test_cache_miss(self, cache):
        """Testa cache miss."""
        valor = cache.get("chave_inexistente")
        assert valor is None
        
        # Verificar estatísticas
        assert cache.cache_stats["hits"] == 0
        assert cache.cache_stats["misses"] == 1
    
    def test_invalidate_cache(self, cache):
        """Testa invalidação de cache."""
        # Adicionar múltiplas chaves
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("other_key", "other_value")
        
        # Invalidar por padrão
        removidos = cache.invalidate("key")
        assert removidos == 2  # key1 e key2
        
        # Verificar que foram removidas
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("other_key") == "other_value"
    
    def test_get_stats(self, cache):
        """Testa obtenção de estatísticas."""
        # Adicionar alguns dados
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")  # hit
        cache.get("key3")  # miss
        
        stats = cache.get_stats()
        
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats
        assert "size" in stats
        assert "max_size" in stats
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5
        assert stats["size"] == 2
        assert stats["max_size"] == 10

class TestOtimizadorQueries:
    """Testes para OtimizadorQueries."""
    
    @pytest.fixture
    def config(self):
        """Fixture para configuração."""
        return ConfiguracaoOtimizacao()
    
    @pytest.fixture
    def otimizador(self, config):
        """Fixture para otimizador de queries."""
        return OtimizadorQueries(config)
    
    def test_otimizar_query_basica(self, otimizador):
        """Testa otimização básica de query."""
        query_original = """
        SELECT * FROM usuarios 
        WHERE ativo = true
        -- Comentário desnecessário
        ORDER BY nome
        """
        
        query_otimizada = otimizador.otimizar_query(query_original)
        
        # Verificar que comentários foram removidos
        assert "--" not in query_otimizada
        assert "Comentário desnecessário" not in query_otimizada
        
        # Verificar que query foi limpa
        assert "SELECT * FROM usuarios WHERE ativo = true ORDER BY nome" in query_otimizada
    
    def test_adicionar_limit(self, otimizador):
        """Testa adição automática de LIMIT."""
        query_sem_limit = "SELECT * FROM produtos WHERE categoria = 'eletronicos'"
        
        query_otimizada = otimizador.otimizar_query(query_sem_limit)
        
        assert "LIMIT 1000" in query_otimizada
    
    def test_nao_adicionar_limit_existente(self, otimizador):
        """Testa que não adiciona LIMIT se já existir."""
        query_com_limit = "SELECT * FROM produtos WHERE categoria = 'eletronicos' LIMIT 50"
        
        query_otimizada = otimizador.otimizar_query(query_com_limit)
        
        # Deve ter apenas um LIMIT
        assert query_otimizada.count("LIMIT") == 1
    
    def test_executar_query_otimizada(self, otimizador):
        """Testa execução de query otimizada."""
        query = "SELECT * FROM usuarios WHERE ativo = true"
        params = {"ativo": True}
        
        resultado, tempo_ms = otimizador.executar_query_otimizada(query, params)
        
        assert resultado is not None
        assert "resultado" in resultado
        assert "query" in resultado
        assert tempo_ms > 0
        
        # Verificar que foi armazenado no cache
        cache_key = f"query:{hash(query + str(params))}"
        resultado_cache = otimizador.query_cache.get(cache_key)
        assert resultado_cache is not None

class TestOtimizadorMemoria:
    """Testes para OtimizadorMemoria."""
    
    @pytest.fixture
    def config(self):
        """Fixture para configuração."""
        return ConfiguracaoOtimizacao(
            threshold_uso_memoria_percent=80.0
        )
    
    @pytest.fixture
    def otimizador(self, config):
        """Fixture para otimizador de memória."""
        return OtimizadorMemoria(config)
    
    @patch('infrastructure.processamento.otimizador_performance_imp005.psutil')
    def test_obter_uso_memoria(self, mock_psutil, otimizador):
        """Testa obtenção de uso de memória."""
        # Mock da memória
        mock_memoria = Mock()
        mock_memoria.total = 8 * 1024 * 1024 * 1024  # 8GB
        mock_memoria.available = 2 * 1024 * 1024 * 1024  # 2GB
        mock_memoria.used = 6 * 1024 * 1024 * 1024  # 6GB
        mock_memoria.percent = 75.0
        
        mock_psutil.virtual_memory.return_value = mock_memoria
        
        uso_memoria = otimizador.obter_uso_memoria()
        
        assert uso_memoria["total_mb"] == 8192.0
        assert uso_memoria["disponivel_mb"] == 2048.0
        assert uso_memoria["usado_mb"] == 6144.0
        assert uso_memoria["percentual_usado"] == 75.0
    
    @patch('infrastructure.processamento.otimizador_performance_imp005.psutil')
    def test_verificar_pressao_memoria(self, mock_psutil, otimizador):
        """Testa verificação de pressão de memória."""
        # Mock com pressão de memória
        mock_memoria = Mock()
        mock_memoria.percent = 85.0  # Acima do threshold de 80%
        mock_psutil.virtual_memory.return_value = mock_memoria
        
        tem_pressao = otimizador.verificar_pressao_memoria()
        assert tem_pressao is True
        
        # Mock sem pressão de memória
        mock_memoria.percent = 70.0  # Abaixo do threshold
        tem_pressao = otimizador.verificar_pressao_memoria()
        assert tem_pressao is False
    
    @patch('infrastructure.processamento.otimizador_performance_imp005.gc')
    @patch('infrastructure.processamento.otimizador_performance_imp005.time')
    def test_otimizar_memoria(self, mock_time, mock_gc, otimizador):
        """Testa otimização de memória."""
        mock_gc.collect.return_value = 100  # 100 objetos coletados
        mock_time.sleep.return_value = None
        
        resultado = otimizador.otimizar_memoria()
        
        assert "otimizacoes_aplicadas" in resultado
        assert "gc_collect:100" in resultado["otimizacoes_aplicadas"]
        mock_gc.collect.assert_called_once()

class TestOtimizadorCPU:
    """Testes para OtimizadorCPU."""
    
    @pytest.fixture
    def config(self):
        """Fixture para configuração."""
        return ConfiguracaoOtimizacao(
            threshold_uso_cpu_percent=80.0
        )
    
    @pytest.fixture
    def otimizador(self, config):
        """Fixture para otimizador de CPU."""
        return OtimizadorCPU(config)
    
    @patch('infrastructure.processamento.otimizador_performance_imp005.psutil')
    def test_obter_uso_cpu(self, mock_psutil, otimizador):
        """Testa obtenção de uso de CPU."""
        mock_psutil.cpu_percent.return_value = 45.5
        mock_psutil.cpu_count.return_value = 8
        
        uso_cpu = otimizador.obter_uso_cpu()
        
        assert uso_cpu["percentual_usado"] == 45.5
        assert uso_cpu["cores_disponiveis"] == 8
        assert uso_cpu["carga_media"] == 45.5 / 8
    
    @patch('infrastructure.processamento.otimizador_performance_imp005.psutil')
    def test_verificar_pressao_cpu(self, mock_psutil, otimizador):
        """Testa verificação de pressão de CPU."""
        # Mock com pressão de CPU
        mock_psutil.cpu_percent.return_value = 85.0  # Acima do threshold
        tem_pressao = otimizador.verificar_pressao_cpu()
        assert tem_pressao is True
        
        # Mock sem pressão de CPU
        mock_psutil.cpu_percent.return_value = 70.0  # Abaixo do threshold
        tem_pressao = otimizador.verificar_pressao_cpu()
        assert tem_pressao is False
    
    @patch('infrastructure.processamento.otimizador_performance_imp005.psutil')
    def test_otimizar_cpu(self, mock_psutil, otimizador):
        """Testa otimização de CPU."""
        # Mock de processos
        mock_process1 = Mock()
        mock_process1.info = {"pid": 1234, "name": "python", "cpu_percent": 60.0}
        
        mock_process2 = Mock()
        mock_process2.info = {"pid": 5678, "name": "chrome", "cpu_percent": 30.0}
        
        mock_psutil.process_iter.return_value = [mock_process1, mock_process2]
        
        resultado = otimizador.otimizar_cpu()
        
        assert "otimizacoes_aplicadas" in resultado
        assert "processos_alto_cpu_detectados:1" in resultado["otimizacoes_aplicadas"]
        assert len(resultado["processos_alto_cpu"]) == 1
        assert resultado["processos_alto_cpu"][0]["pid"] == 1234

class TestOtimizadorPerformance:
    """Testes para OtimizadorPerformance."""
    
    @pytest.fixture
    def config(self):
        """Fixture para configuração."""
        return ConfiguracaoOtimizacao(
            ativar_cache_inteligente=True,
            ativar_otimizacao_memoria=True,
            ativar_otimizacao_cpu=True
        )
    
    @pytest.fixture
    def otimizador(self, config):
        """Fixture para otimizador de performance."""
        return OtimizadorPerformance(config)
    
    def test_inicializacao_otimizador(self, otimizador):
        """Testa inicialização do otimizador."""
        assert otimizador.config is not None
        assert otimizador.tracing_id is not None
        assert otimizador.metricas is not None
        assert otimizador.cache is not None
        assert otimizador.otimizador_queries is not None
        assert otimizador.otimizador_memoria is not None
        assert otimizador.otimizador_cpu is not None
    
    def test_listar_componentes_ativos(self, otimizador):
        """Testa listagem de componentes ativos."""
        componentes = otimizador._listar_componentes_ativos()
        
        assert "otimizador_queries" in componentes
        assert "cache_inteligente" in componentes
        assert "otimizador_memoria" in componentes
        assert "otimizador_cpu" in componentes
        assert "paralelizacao" in componentes
    
    def test_executar_com_otimizacao(self, otimizador):
        """Testa execução com otimização."""
        def funcao_teste(value, result):
            time.sleep(0.01)  # Simular processamento
            return value + result
        
        resultado, metricas = otimizador.executar_com_otimizacao(funcao_teste, 5, 3)
        
        assert resultado == 8
        assert "tempo_ms" in metricas
        assert metricas["tempo_ms"] > 0
        assert "cache_hit" in metricas
        assert "otimizacoes" in metricas
    
    def test_executar_query_otimizada(self, otimizador):
        """Testa execução de query otimizada."""
        query = "SELECT * FROM usuarios WHERE ativo = true"
        params = {"ativo": True}
        
        resultado, metricas = otimizador.executar_query_otimizada(query, params)
        
        assert resultado is not None
        assert "tempo_ms" in metricas
        assert metricas["tempo_ms"] > 0
    
    def test_obter_metricas(self, otimizador):
        """Testa obtenção de métricas."""
        # Executar algumas operações para gerar métricas
        otimizador.executar_com_otimizacao(lambda value: value * 2, 5)
        otimizador.executar_query_otimizada("SELECT 1", {})
        
        metricas = otimizador.obter_metricas()
        
        assert "tempo_total_ms" in metricas
        assert "cache_hits" in metricas
        assert "cache_misses" in metricas
        assert "cache_hit_rate" in metricas
        assert "memoria" in metricas
        assert "cpu" in metricas
    
    def test_gerar_relatorio_performance(self, otimizador):
        """Testa geração de relatório de performance."""
        # Executar algumas operações
        otimizador.executar_com_otimizacao(lambda value: value * 2, 5)
        
        relatorio = otimizador.gerar_relatorio_performance()
        
        assert "tracing_id" in relatorio
        assert "timestamp" in relatorio
        assert "configuracao" in relatorio
        assert "metricas" in relatorio
        assert "status" in relatorio
        assert "recomendacoes" in relatorio
    
    def test_limpar_cache(self, otimizador):
        """Testa limpeza de cache."""
        # Adicionar dados ao cache
        otimizador.cache.set("test_key", "test_value")
        
        resultado = otimizador.limpar_cache()
        
        assert resultado["status"] == "success"
        assert "Cache limpo com sucesso" in resultado["message"]
        
        # Verificar que cache foi limpo
        valor = otimizador.cache.get("test_key")
        assert valor is None

class TestDecoratorOtimizacao:
    """Testes para decorator de otimização."""
    
    def test_decorator_otimizacao(self):
        """Testa decorator de otimização."""
        @otimizar_performance()
        def funcao_teste(value, result):
            time.sleep(0.01)
            return value + result
        
        resultado, metricas = funcao_teste(10, 20)
        
        assert resultado == 30
        assert "tempo_ms" in metricas
        assert metricas["tempo_ms"] > 0
    
    def test_exemplo_funcao_otimizada(self):
        """Testa função de exemplo otimizada."""
        dados = [{"id": 1}, {"id": 2}, {"id": 3}]
        
        resultado, metricas = exemplo_funcao_otimizada(dados)
        
        assert resultado["total_processado"] == 3
        assert resultado["resultado"] == "processado_com_otimizacao"
        assert "tempo_ms" in metricas

class TestIntegracaoOtimizador:
    """Testes de integração do otimizador."""
    
    @pytest.fixture
    def config_completa(self):
        """Fixture para configuração completa."""
        return ConfiguracaoOtimizacao(
            ativar_cache_inteligente=True,
            ativar_paralelizacao=True,
            ativar_otimizacao_memoria=True,
            ativar_otimizacao_cpu=True,
            max_workers=2,
            cache_ttl_segundos=300,
            cache_max_size=100,
            threshold_tempo_resposta_ms=1000,
            threshold_uso_memoria_percent=85.0,
            threshold_uso_cpu_percent=85.0
        )
    
    def test_fluxo_completo_otimizacao(self, config_completa):
        """Testa fluxo completo de otimização."""
        otimizador = OtimizadorPerformance(config_completa)
        
        # Simular múltiplas execuções
        for index in range(5):
            resultado, metricas = otimizador.executar_com_otimizacao(
                lambda value: value * value, index
            )
            assert resultado == index * index
        
        # Gerar relatório final
        relatorio = otimizador.gerar_relatorio_performance()
        
        assert relatorio["status"] in ["otimizado", "necessita_otimizacao"]
        assert len(relatorio["recomendacoes"]) >= 0
        assert relatorio["metricas"]["cache_hits"] >= 0
        assert relatorio["metricas"]["cache_misses"] >= 0
    
    def test_cache_inteligente_com_multiplas_execucoes(self, config_completa):
        """Testa cache inteligente com múltiplas execuções."""
        otimizador = OtimizadorPerformance(config_completa)
        
        # Primeira execução (cache miss)
        resultado1, metricas1 = otimizador.executar_com_otimizacao(
            lambda value: value * 2, 10
        )
        assert metricas1["cache_hit"] is False
        
        # Segunda execução (cache hit)
        resultado2, metricas2 = otimizador.executar_com_otimizacao(
            lambda value: value * 2, 10
        )
        assert metricas2["cache_hit"] is True
        assert resultado1 == resultado2
        
        # Verificar estatísticas de cache
        stats = otimizador.cache.get_stats()
        assert stats["hits"] >= 1
        assert stats["misses"] >= 1
        assert stats["hit_rate"] > 0

if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 
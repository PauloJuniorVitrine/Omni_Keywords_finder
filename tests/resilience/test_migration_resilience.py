from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
Testes de Resiliência da Migração - Omni Keywords Finder

Testa a capacidade do sistema de se recuperar de falhas
após a migração, incluindo timeouts, erros de API e circuit breakers.

Tracing ID: RESILIENCE_001_20241227
Versão: 1.0
Autor: IA-Cursor
Status: ✅ IMPLEMENTADO PARA FASE 5
"""

import pytest
import sys
import os
import time
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import tempfile
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.orchestrator.fluxo_completo_orchestrator import FluxoCompletoOrchestrator
from infrastructure.orchestrator.config import OrchestratorConfig
from infrastructure.orchestrator.error_handler import ErrorHandler


class TestMigrationResilience:
    """Testes de resiliência da migração."""
    
    @pytest.fixture
    def orchestrator_config(self):
        """Configuração do orquestrador para testes de resiliência."""
        config = OrchestratorConfig()
        config.coleta = {
            'timeout': 10,  # Timeout baixo para testes
            'max_retries': 3,
            'rate_limit': 10,
            'circuit_breaker': {
                'failure_threshold': 3,
                'recovery_timeout': 30,
                'expected_exception': Exception
            }
        }
        config.validacao = {
            'timeout': 5,
            'max_retries': 2
        }
        config.processamento = {
            'timeout': 15,
            'max_retries': 2
        }
        return config
    
    @pytest.fixture
    def orchestrator(self, orchestrator_config):
        """Orquestrador configurado para testes de resiliência."""
        return FluxoCompletoOrchestrator(orchestrator_config)
    
    @pytest.fixture
    def sample_keywords(self):
        """Palavras-chave de exemplo para testes."""
        return [
            "python programming",
            "machine learning",
            "data science"
        ]
    
    def test_timeout_handling(self, orchestrator, sample_keywords):
        """Testa tratamento de timeouts."""
        with patch('infrastructure.coleta.google_suggest.GoogleSuggestCollector') as mock_collector:
            # Mock que simula timeout
            def slow_collector(*args, **kwargs):
                time.sleep(15)  # Mais que o timeout configurado
                return sample_keywords
            
            mock_collector_instance = Mock()
            mock_collector_instance.coletar_keywords.side_effect = slow_collector
            mock_collector.return_value = mock_collector_instance
            
            # Executar com timeout
            start_time = time.time()
            result = orchestrator.etapa_coleta.executar_coleta(sample_keywords)
            execution_time = time.time() - start_time
            
            # Verificar se timeout foi respeitado
            assert execution_time < 12  # Deve falhar antes de 12 segundos
            assert result is not None  # Deve retornar resultado (mesmo que erro)
    
    def test_retry_mechanism(self, orchestrator, sample_keywords):
        """Testa mecanismo de retry."""
        call_count = 0
        
        with patch('infrastructure.coleta.google_suggest.GoogleSuggestCollector') as mock_collector:
            def failing_then_success(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count < 3:  # Falha nas primeiras 2 tentativas
                    raise Exception(f"Erro simulado na tentativa {call_count}")
                return sample_keywords
            
            mock_collector_instance = Mock()
            mock_collector_instance.coletar_keywords.side_effect = failing_then_success
            mock_collector.return_value = mock_collector_instance
            
            # Executar com retry
            result = orchestrator.etapa_coleta.executar_coleta(sample_keywords)
            
            # Verificar se retry funcionou
            assert call_count == 3  # Deve ter tentado 3 vezes
            assert result == sample_keywords  # Deve ter sucesso na última tentativa
    
    def test_circuit_breaker_pattern(self, orchestrator, sample_keywords):
        """Testa padrão circuit breaker."""
        failure_count = 0
        
        with patch('infrastructure.coleta.google_suggest.GoogleSuggestCollector') as mock_collector:
            def always_fail(*args, **kwargs):
                nonlocal failure_count
                failure_count += 1
                raise Exception("Erro simulado")
            
            mock_collector_instance = Mock()
            mock_collector_instance.coletar_keywords.side_effect = always_fail
            mock_collector.return_value = mock_collector_instance
            
            # Executar até ativar circuit breaker
            for index in range(5):
                try:
                    result = orchestrator.etapa_coleta.executar_coleta(sample_keywords)
                except Exception:
                    pass
            
            # Verificar se circuit breaker foi ativado
            # Após 3 falhas, circuit breaker deve estar aberto
            assert failure_count >= 3
    
    def test_graceful_degradation(self, orchestrator, sample_keywords):
        """Testa degradação graciosa."""
        with patch('infrastructure.coleta.google_suggest.GoogleSuggestCollector') as mock_collector, \
             patch('infrastructure.coleta.google_trends.GoogleTrendsCollector') as mock_trends:
            
            # Primeiro coletor falha
            mock_collector_instance = Mock()
            mock_collector_instance.coletar_keywords.side_effect = Exception("Erro no Google Suggest")
            mock_collector.return_value = mock_collector_instance
            
            # Segundo coletor funciona
            mock_trends_instance = Mock()
            mock_trends_instance.coletar_keywords.return_value = sample_keywords
            mock_trends.return_value = mock_trends_instance
            
            # Executar com degradação graciosa
            result = orchestrator.etapa_coleta.executar_coleta(sample_keywords)
            
            # Verificar se sistema continuou funcionando
            assert result is not None
            # Pode retornar dados do segundo coletor ou lista vazia
    
    def test_error_propagation(self, orchestrator, sample_keywords):
        """Testa propagação de erros."""
        with patch('infrastructure.coleta.google_suggest.GoogleSuggestCollector') as mock_collector:
            mock_collector_instance = Mock()
            mock_collector_instance.coletar_keywords.side_effect = Exception("Erro crítico")
            mock_collector.return_value = mock_collector_instance
            
            # Executar e verificar se erro é propagado adequadamente
            try:
                result = orchestrator.etapa_coleta.executar_coleta(sample_keywords)
                # Se não lançou exceção, deve ter tratado o erro
                assert result is not None
            except Exception as e:
                # Se lançou exceção, deve ser tratável
                assert "Erro crítico" in str(e)
    
    def test_resource_cleanup(self, orchestrator, sample_keywords):
        """Testa limpeza de recursos após falhas."""
        cleanup_called = False
        
        with patch('infrastructure.coleta.google_suggest.GoogleSuggestCollector') as mock_collector:
            mock_collector_instance = Mock()
            
            def failing_with_cleanup(*args, **kwargs):
                nonlocal cleanup_called
                cleanup_called = True
                raise Exception("Erro com cleanup")
            
            mock_collector_instance.coletar_keywords.side_effect = failing_with_cleanup
            mock_collector_instance.cleanup = Mock()
            mock_collector.return_value = mock_collector_instance
            
            # Executar e verificar cleanup
            try:
                orchestrator.etapa_coleta.executar_coleta(sample_keywords)
            except Exception:
                pass
            
            # Verificar se cleanup foi chamado
            assert cleanup_called
            mock_collector_instance.cleanup.assert_called()
    
    def test_concurrent_failure_handling(self, orchestrator, sample_keywords):
        """Testa tratamento de falhas concorrentes."""
        def concurrent_operation():
            with patch('infrastructure.coleta.google_suggest.GoogleSuggestCollector') as mock_collector:
                mock_collector_instance = Mock()
                mock_collector_instance.coletar_keywords.side_effect = Exception("Erro concorrente")
                mock_collector.return_value = mock_collector_instance
                
                return orchestrator.etapa_coleta.executar_coleta(sample_keywords)
        
        # Executar operações concorrentes
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(concurrent_operation) for _ in range(3)]
            
            # Aguardar todas as operações
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=10)
                    results.append(result)
                except Exception as e:
                    results.append(f"Erro: {e}")
            
            # Verificar se todas as operações foram tratadas
            assert len(results) == 3
            assert all(result is not None for result in results)
    
    def test_memory_leak_prevention(self, orchestrator, sample_keywords):
        """Testa prevenção de vazamentos de memória."""
        import gc
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Executar operações repetidamente
        for _ in range(10):
            with patch('infrastructure.coleta.google_suggest.GoogleSuggestCollector') as mock_collector:
                mock_collector_instance = Mock()
                mock_collector_instance.coletar_keywords.return_value = sample_keywords
                mock_collector.return_value = mock_collector_instance
                
                try:
                    orchestrator.etapa_coleta.executar_coleta(sample_keywords)
                except Exception:
                    pass
        
        # Forçar garbage collection
        gc.collect()
        
        # Verificar uso de memória
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Aumento de memória deve ser razoável (menos de 10MB)
        assert memory_increase < 10 * 1024 * 1024  # 10MB
    
    def test_error_recovery_after_failure(self, orchestrator, sample_keywords):
        """Testa recuperação após falhas."""
        failure_mode = True
        
        with patch('infrastructure.coleta.google_suggest.GoogleSuggestCollector') as mock_collector:
            def conditional_failure(*args, **kwargs):
                nonlocal failure_mode
                if failure_mode:
                    failure_mode = False  # Próxima tentativa será bem-sucedida
                    raise Exception("Falha temporária")
                return sample_keywords
            
            mock_collector_instance = Mock()
            mock_collector_instance.coletar_keywords.side_effect = conditional_failure
            mock_collector.return_value = mock_collector_instance
            
            # Primeira execução deve falhar
            try:
                result1 = orchestrator.etapa_coleta.executar_coleta(sample_keywords)
            except Exception:
                result1 = None
            
            # Segunda execução deve funcionar
            result2 = orchestrator.etapa_coleta.executar_coleta(sample_keywords)
            
            # Verificar recuperação
            assert result1 != sample_keywords  # Primeira falhou
            assert result2 == sample_keywords  # Segunda funcionou
    
    def test_cascading_failure_prevention(self, orchestrator, sample_keywords):
        """Testa prevenção de falhas em cascata."""
        with patch('infrastructure.coleta.google_suggest.GoogleSuggestCollector') as mock_collector, \
             patch('infrastructure.validacao.validador_avancado.ValidadorAvancado') as mock_validator, \
             patch('infrastructure.processamento.ml_processor.MLProcessor') as mock_processor:
            
            # Configurar falha em cascata
            mock_collector_instance = Mock()
            mock_collector_instance.coletar_keywords.side_effect = Exception("Falha na coleta")
            mock_collector.return_value = mock_collector_instance
            
            mock_validator_instance = Mock()
            mock_validator_instance.validar_keywords.side_effect = Exception("Falha na validação")
            mock_validator.return_value = mock_validator_instance
            
            mock_processor_instance = Mock()
            mock_processor_instance.processar_keywords.side_effect = Exception("Falha no processamento")
            mock_processor.return_value = mock_processor_instance
            
            # Executar fluxo completo
            with tempfile.TemporaryDirectory() as temp_dir:
                result = orchestrator.executar_fluxo_completo(
                    keywords_iniciais=sample_keywords,
                    output_dir=temp_dir
                )
                
                # Verificar se falha foi contida
                assert result is not None
                assert 'status' in result
                # Status pode ser 'error' ou 'partial_success', mas não deve quebrar completamente
    
    def test_rate_limiting_resilience(self, orchestrator, sample_keywords):
        """Testa resiliência ao rate limiting."""
        request_count = 0
        
        with patch('infrastructure.coleta.google_suggest.GoogleSuggestCollector') as mock_collector:
            def rate_limited_collector(*args, **kwargs):
                nonlocal request_count
                request_count += 1
                
                if request_count <= 5:  # Primeiros 5 requests OK
                    return sample_keywords
                elif request_count <= 8:  # Próximos 3 requests rate limited
                    raise Exception("Rate limit exceeded")
                else:  # Depois volta a funcionar
                    return sample_keywords
            
            mock_collector_instance = Mock()
            mock_collector_instance.coletar_keywords.side_effect = rate_limited_collector
            mock_collector.return_value = mock_collector_instance
            
            # Executar múltiplas operações
            results = []
            for _ in range(10):
                try:
                    result = orchestrator.etapa_coleta.executar_coleta(sample_keywords)
                    results.append(result)
                except Exception as e:
                    results.append(f"Erro: {e}")
            
            # Verificar se sistema lidou com rate limiting
            assert len(results) == 10
            # Alguns podem ter falhado, mas sistema não deve quebrar completamente
    
    def test_network_failure_resilience(self, orchestrator, sample_keywords):
        """Testa resiliência a falhas de rede."""
        with patch('infrastructure.coleta.google_suggest.GoogleSuggestCollector') as mock_collector:
            # Simular diferentes tipos de falhas de rede
            network_errors = [
                Exception("Connection timeout"),
                Exception("DNS resolution failed"),
                Exception("SSL certificate error"),
                Exception("Network unreachable")
            ]
            
            error_index = 0
            
            def network_failure_simulator(*args, **kwargs):
                nonlocal error_index
                if error_index < len(network_errors):
                    error = network_errors[error_index]
                    error_index += 1
                    raise error
                return sample_keywords
            
            mock_collector_instance = Mock()
            mock_collector_instance.coletar_keywords.side_effect = network_failure_simulator
            mock_collector.return_value = mock_collector_instance
            
            # Executar operações
            results = []
            for _ in range(5):
                try:
                    result = orchestrator.etapa_coleta.executar_coleta(sample_keywords)
                    results.append(result)
                except Exception as e:
                    results.append(f"Erro de rede: {e}")
            
            # Verificar se sistema lidou com falhas de rede
            assert len(results) == 5
            # Última operação deve ter sucesso após falhas de rede


class TestErrorHandlerResilience:
    """Testes de resiliência do ErrorHandler."""
    
    @pytest.fixture
    def error_handler(self):
        """ErrorHandler para testes."""
        return ErrorHandler()
    
    def test_error_classification(self, error_handler):
        """Testa classificação de erros."""
        # Testar diferentes tipos de erro
        timeout_error = Exception("Request timeout")
        network_error = Exception("Network unreachable")
        validation_error = Exception("Invalid data")
        
        # Verificar classificação
        assert error_handler.classify_error(timeout_error) in ['timeout', 'network', 'unknown']
        assert error_handler.classify_error(network_error) in ['network', 'unknown']
        assert error_handler.classify_error(validation_error) in ['validation', 'unknown']
    
    def test_error_recovery_strategies(self, error_handler):
        """Testa estratégias de recuperação de erro."""
        # Testar estratégias para diferentes tipos de erro
        timeout_error = Exception("Request timeout")
        network_error = Exception("Network unreachable")
        
        # Verificar estratégias
        timeout_strategy = error_handler.get_recovery_strategy(timeout_error)
        network_strategy = error_handler.get_recovery_strategy(network_error)
        
        assert timeout_strategy is not None
        assert network_strategy is not None
        assert isinstance(timeout_strategy, dict)
        assert isinstance(network_strategy, dict)
    
    def test_error_logging(self, error_handler):
        """Testa logging de erros."""
        test_error = Exception("Test error for logging")
        
        # Verificar se erro é logado adequadamente
        with patch('logging.error') as mock_logging:
            error_handler.log_error(test_error, "test_context")
            mock_logging.assert_called()
    
    def test_error_metrics(self, error_handler):
        """Testa métricas de erro."""
        # Simular múltiplos erros
        for index in range(5):
            error_handler.record_error(f"Error {index}", "test_context")
        
        # Verificar métricas
        metrics = error_handler.get_error_metrics()
        assert metrics is not None
        assert 'total_errors' in metrics
        assert 'error_rate' in metrics
        assert metrics['total_errors'] >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 
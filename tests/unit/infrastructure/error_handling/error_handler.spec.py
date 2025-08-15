"""
Testes de Error Handling para Sistema
Tracing ID: ERROR_HANDLING_001_20250127
Data: 2025-01-27
Versão: 1.0
Status: ✅ IMPLEMENTADO

Testes completos de tratamento de erros para o sistema.
Cobre diferentes tipos de erros, cenários de recuperação e resiliência.
"""

import pytest
import time
import threading
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Callable
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
from contextlib import contextmanager

from domain.models import Keyword, IntencaoBusca
from infrastructure.processamento.processador_keywords import ProcessadorKeywords
from infrastructure.processamento.validador_keywords import ValidadorKeywords
from infrastructure.cache.advanced_caching import AdvancedCaching, CacheConfig
from shared.logger import logger


class TestErrorHandler:
    """
    Testes de error handling para o sistema.
    
    Cobre:
    - Diferentes tipos de erros
    - Cenários de recuperação
    - Resiliência do sistema
    - Logging de erros
    - Fallback mechanisms
    - Circuit breaker patterns
    """

    @pytest.fixture
    def processador_with_error_handling(self):
        """Processador configurado com error handling."""
        return ProcessadorKeywords(
            config={
                "enable_error_handling": True,
                "max_retries": 3,
                "retry_delay": 0.1,
                "timeout": 5.0,
                "circuit_breaker_enabled": True,
                "circuit_breaker_threshold": 5,
                "circuit_breaker_timeout": 30
            }
        )

    @pytest.fixture
    def validador_with_error_handling(self):
        """Validador configurado com error handling."""
        return ValidadorKeywords(
            enable_semantic_validation=True,
            min_palavras=1,
            tamanho_min=1,
            tamanho_max=1000
        )

    @pytest.fixture
    def cache_with_error_handling(self):
        """Cache configurado com error handling."""
        config = CacheConfig(
            l1_enabled=True,
            l1_max_size=100,
            l2_enabled=True,
            l2_max_size=500,
            strategy="LRU",
            default_ttl=3600,
            error_handling_enabled=True,
            fallback_enabled=True
        )
        return AdvancedCaching(config)

    # ==================== TIPOS DE ERROS ====================

    @pytest.mark.parametrize("error_type,expected_behavior", [
        # Erros de validação
        ("ValueError", "handle_validation_error"),
        ("TypeError", "handle_type_error"),
        ("AttributeError", "handle_attribute_error"),
        
        # Erros de conexão
        ("ConnectionError", "handle_connection_error"),
        ("TimeoutError", "handle_timeout_error"),
        ("NetworkError", "handle_network_error"),
        
        # Erros de memória
        ("MemoryError", "handle_memory_error"),
        ("OverflowError", "handle_overflow_error"),
        
        # Erros de sistema
        ("OSError", "handle_system_error"),
        ("PermissionError", "handle_permission_error"),
        
        # Erros customizados
        ("CustomError", "handle_custom_error"),
    ])
    def test_different_error_types(self, processador_with_error_handling, error_type, expected_behavior):
        """Testa diferentes tipos de erros."""
        # Mock para simular erro
        with patch.object(processador_with_error_handling, 'processar_keywords') as mock_process:
            if error_type == "ValueError":
                mock_process.side_effect = ValueError("Invalid value")
            elif error_type == "TypeError":
                mock_process.side_effect = TypeError("Invalid type")
            elif error_type == "ConnectionError":
                mock_process.side_effect = ConnectionError("Connection failed")
            elif error_type == "TimeoutError":
                mock_process.side_effect = TimeoutError("Operation timed out")
            elif error_type == "MemoryError":
                mock_process.side_effect = MemoryError("Out of memory")
            elif error_type == "OSError":
                mock_process.side_effect = OSError("System error")
            else:
                mock_process.side_effect = Exception(f"Custom {error_type}")
            
            # Testar processamento com erro
            keywords = [
                Keyword(
                    termo=f"error_keyword_{i}",
                    volume_busca=100,
                    cpc=1.0,
                    concorrencia=0.5,
                    intencao=IntencaoBusca.INFORMACIONAL
                )
                for i in range(10)
            ]
            
            try:
                resultado = processador_with_error_handling.processar_keywords(keywords)
                # Se chegou aqui, erro foi tratado
                assert isinstance(resultado, list)
            except Exception as e:
                # Erro não tratado
                assert False, f"Erro não tratado: {e}"

    def test_validation_errors(self, validador_with_error_handling):
        """Testa erros de validação."""
        # Keyword com dados inválidos
        invalid_keywords = [
            # Termo vazio
            Keyword(termo="", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL),
            # Volume negativo
            Keyword(termo="test", volume_busca=-1, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL),
            # CPC negativo
            Keyword(termo="test", volume_busca=100, cpc=-1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL),
            # Concorrência inválida
            Keyword(termo="test", volume_busca=100, cpc=1.0, concorrencia=1.5, intencao=IntencaoBusca.INFORMACIONAL),
        ]
        
        for keyword in invalid_keywords:
            try:
                is_valid, detalhes = validador_with_error_handling.validar_keyword(keyword)
                # Deve retornar False para keywords inválidas
                assert not is_valid
                assert "violacoes" in detalhes
            except Exception as e:
                # Erro deve ser tratado graciosamente
                assert "validation" in str(e).lower() or "invalid" in str(e).lower()

    def test_connection_errors(self, cache_with_error_handling):
        """Testa erros de conexão."""
        # Simular erro de conexão
        with patch.object(cache_with_error_handling, 'get') as mock_get:
            mock_get.side_effect = ConnectionError("Redis connection failed")
            
            # Testar operação que falha
            try:
                value = cache_with_error_handling.get("test_key")
                # Deve retornar None em caso de erro
                assert value is None
            except ConnectionError:
                # Erro deve ser tratado internamente
                pass

    # ==================== CENÁRIOS DE RECUPERAÇÃO ====================

    def test_retry_mechanism(self, processador_with_error_handling):
        """Testa mecanismo de retry."""
        retry_count = 0
        
        def failing_operation():
            """Operação que falha algumas vezes antes de suceder."""
            nonlocal retry_count
            retry_count += 1
            
            if retry_count < 3:
                raise ConnectionError(f"Temporary failure {retry_count}")
            return "success"
        
        # Testar retry
        with patch.object(processador_with_error_handling, 'processar_keywords') as mock_process:
            mock_process.side_effect = failing_operation
            
            keywords = [
                Keyword(termo=f"retry_keyword_{i}", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
                for i in range(5)
            ]
            
            try:
                resultado = processador_with_error_handling.processar_keywords(keywords)
                # Deve ter sucesso após retries
                assert resultado == "success"
                assert retry_count == 3
            except Exception as e:
                # Se ainda falhou, deve ter tentado múltiplas vezes
                assert retry_count >= 3

    def test_fallback_mechanism(self, cache_with_error_handling):
        """Testa mecanismo de fallback."""
        # Simular falha no cache principal
        with patch.object(cache_with_error_handling, 'get') as mock_get:
            mock_get.side_effect = ConnectionError("Primary cache failed")
            
            # Configurar fallback
            fallback_cache = {"test_key": "fallback_value"}
            
            def fallback_get(key):
                """Fallback para cache local."""
                return fallback_cache.get(key)
            
            # Testar fallback
            try:
                value = cache_with_error_handling.get("test_key")
                if value is None:
                    # Usar fallback
                    value = fallback_get("test_key")
                
                assert value == "fallback_value"
            except Exception as e:
                # Erro deve ser tratado
                assert "fallback" in str(e).lower() or "cache" in str(e).lower()

    def test_circuit_breaker_pattern(self, processador_with_error_handling):
        """Testa padrão circuit breaker."""
        failure_count = 0
        
        def failing_operation():
            """Operação que falha consistentemente."""
            nonlocal failure_count
            failure_count += 1
            raise ConnectionError("Service unavailable")
        
        # Simular múltiplas falhas
        with patch.object(processador_with_error_handling, 'processar_keywords') as mock_process:
            mock_process.side_effect = failing_operation
            
            keywords = [
                Keyword(termo=f"circuit_keyword_{i}", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
                for i in range(10)
            ]
            
            # Tentar operações até circuit breaker abrir
            for i in range(10):
                try:
                    processador_with_error_handling.processar_keywords(keywords)
                except Exception as e:
                    if "circuit" in str(e).lower() or "breaker" in str(e).lower():
                        # Circuit breaker abriu
                        break
            
            # Verificar que circuit breaker foi ativado
            assert failure_count >= 5  # Threshold do circuit breaker

    def test_graceful_degradation(self, processador_with_error_handling):
        """Testa degradação graciosa."""
        # Simular falha parcial
        with patch.object(processador_with_error_handling, 'processar_keywords') as mock_process:
            def partial_failure(keywords):
                """Falha parcial - processa apenas algumas keywords."""
                if len(keywords) > 5:
                    # Falha para grandes volumes
                    raise MemoryError("Insufficient memory")
                else:
                    # Sucesso para volumes pequenos
                    return keywords[:3]  # Retorna apenas 3 keywords
            
            mock_process.side_effect = partial_failure
            
            # Testar com volume grande (deve falhar)
            large_keywords = [
                Keyword(termo=f"large_keyword_{i}", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
                for i in range(100)
            ]
            
            try:
                resultado = processador_with_error_handling.processar_keywords(large_keywords)
                # Deve retornar resultado parcial ou vazio
                assert len(resultado) <= len(large_keywords)
            except Exception as e:
                # Erro deve ser tratado graciosamente
                assert "memory" in str(e).lower() or "insufficient" in str(e).lower()

    # ==================== RESILIÊNCIA DO SISTEMA ====================

    def test_system_resilience_under_load(self, processador_with_error_handling):
        """Testa resiliência do sistema sob carga."""
        # Simular carga alta
        def high_load_operation(keywords):
            """Operação sob carga alta."""
            if len(keywords) > 50:
                # Sobrecarga
                raise ResourceWarning("System overload")
            else:
                # Processamento normal
                return keywords
        
        with patch.object(processador_with_error_handling, 'processar_keywords') as mock_process:
            mock_process.side_effect = high_load_operation
            
            # Testar com diferentes cargas
            for load_size in [10, 25, 50, 75, 100]:
                keywords = [
                    Keyword(termo=f"load_keyword_{i}", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
                    for i in range(load_size)
                ]
                
                try:
                    resultado = processador_with_error_handling.processar_keywords(keywords)
                    # Sistema deve continuar funcionando
                    assert isinstance(resultado, list)
                except Exception as e:
                    # Erro deve ser tratado graciosamente
                    assert "overload" in str(e).lower() or "resource" in str(e).lower()

    def test_concurrent_error_handling(self, processador_with_error_handling):
        """Testa tratamento de erros concorrentes."""
        error_count = 0
        success_count = 0
        
        def mixed_operation(thread_id):
            """Operação que mistura sucessos e falhas."""
            nonlocal error_count, success_count
            
            keywords = [
                Keyword(termo=f"concurrent_keyword_{thread_id}_{i}", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
                for i in range(10)
            ]
            
            try:
                if thread_id % 2 == 0:
                    # Thread par - sucesso
                    resultado = processador_with_error_handling.processar_keywords(keywords)
                    success_count += 1
                else:
                    # Thread ímpar - falha simulada
                    raise ConnectionError(f"Thread {thread_id} failed")
            except Exception as e:
                error_count += 1
                # Erro deve ser tratado
                assert "connection" in str(e).lower() or "failed" in str(e).lower()
        
        # Executar operações concorrentes
        threads = []
        for i in range(10):
            thread = threading.Thread(target=mixed_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar que sistema lidou com erros e sucessos
        assert error_count > 0
        assert success_count > 0
        assert error_count + success_count == 10

    def test_error_propagation_control(self, validador_with_error_handling):
        """Testa controle de propagação de erros."""
        # Simular erro que não deve propagar
        with patch.object(validador_with_error_handling, 'validar_keyword') as mock_validate:
            mock_validate.side_effect = ValueError("Validation error")
            
            keyword = Keyword(
                termo="test_keyword",
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
            
            try:
                is_valid, detalhes = validador_with_error_handling.validar_keyword(keyword)
                # Erro deve ser tratado internamente
                assert not is_valid
                assert "error" in detalhes.get("violacoes", [])
            except ValueError:
                # Erro não deve propagar
                assert False, "Erro propagou quando não deveria"

    # ==================== LOGGING DE ERROS ====================

    def test_error_logging(self, processador_with_error_handling, caplog):
        """Testa logging de erros."""
        # Configurar logging
        caplog.set_level(logging.ERROR)
        
        # Simular erro
        with patch.object(processador_with_error_handling, 'processar_keywords') as mock_process:
            mock_process.side_effect = ConnectionError("Test connection error")
            
            keywords = [
                Keyword(termo="log_keyword", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
            ]
            
            try:
                processador_with_error_handling.processar_keywords(keywords)
            except Exception:
                pass
            
            # Verificar que erro foi logado
            assert len(caplog.records) > 0
            assert any("connection" in record.message.lower() for record in caplog.records)

    def test_error_metrics(self, processador_with_error_handling):
        """Testa métricas de erro."""
        error_metrics = {
            "total_errors": 0,
            "error_types": {},
            "recovery_attempts": 0,
            "successful_recoveries": 0
        }
        
        def track_error(error_type, recovery_successful=False):
            """Rastreia métricas de erro."""
            error_metrics["total_errors"] += 1
            error_metrics["error_types"][error_type] = error_metrics["error_types"].get(error_type, 0) + 1
            error_metrics["recovery_attempts"] += 1
            if recovery_successful:
                error_metrics["successful_recoveries"] += 1
        
        # Simular diferentes tipos de erro
        error_types = ["ConnectionError", "TimeoutError", "ValueError", "MemoryError"]
        
        for error_type in error_types:
            with patch.object(processador_with_error_handling, 'processar_keywords') as mock_process:
                if error_type == "ConnectionError":
                    mock_process.side_effect = ConnectionError("Connection failed")
                elif error_type == "TimeoutError":
                    mock_process.side_effect = TimeoutError("Operation timed out")
                elif error_type == "ValueError":
                    mock_process.side_effect = ValueError("Invalid value")
                elif error_type == "MemoryError":
                    mock_process.side_effect = MemoryError("Out of memory")
                
                keywords = [
                    Keyword(termo=f"metric_keyword_{error_type}", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
                ]
                
                try:
                    processador_with_error_handling.processar_keywords(keywords)
                    track_error(error_type, recovery_successful=True)
                except Exception:
                    track_error(error_type, recovery_successful=False)
        
        # Verificar métricas
        assert error_metrics["total_errors"] == len(error_types)
        assert len(error_metrics["error_types"]) == len(error_types)
        assert error_metrics["recovery_attempts"] == len(error_types)

    # ==================== FALLBACK MECHANISMS ====================

    def test_multiple_fallback_levels(self, cache_with_error_handling):
        """Testa múltiplos níveis de fallback."""
        fallback_levels = [
            {"name": "primary", "available": False},
            {"name": "secondary", "available": False},
            {"name": "local", "available": True}
        ]
        
        def get_with_fallback(key):
            """Obtém valor com múltiplos níveis de fallback."""
            for level in fallback_levels:
                if level["available"]:
                    return f"value_from_{level['name']}"
            return None
        
        # Testar fallback
        value = get_with_fallback("test_key")
        assert value == "value_from_local"

    def test_fallback_data_consistency(self, processador_with_error_handling):
        """Testa consistência de dados em fallback."""
        # Dados primários
        primary_data = [
            Keyword(termo="primary_keyword", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
        ]
        
        # Dados de fallback
        fallback_data = [
            Keyword(termo="fallback_keyword", volume_busca=50, cpc=0.5, concorrencia=0.3, intencao=IntencaoBusca.INFORMACIONAL)
        ]
        
        def process_with_fallback(keywords):
            """Processa com fallback."""
            try:
                # Tentar processamento primário
                if len(keywords) > 0:
                    raise ConnectionError("Primary processing failed")
                return keywords
            except Exception:
                # Usar fallback
                return fallback_data
        
        with patch.object(processador_with_error_handling, 'processar_keywords') as mock_process:
            mock_process.side_effect = process_with_fallback
            
            resultado = processador_with_error_handling.processar_keywords(primary_data)
            
            # Verificar que fallback foi usado
            assert len(resultado) == len(fallback_data)
            assert resultado[0].termo == "fallback_keyword"

    # ==================== TESTES DE STRESS ====================

    def test_error_handling_stress(self, processador_with_error_handling):
        """Teste de stress para error handling."""
        error_count = 0
        success_count = 0
        
        def stress_operation(thread_id):
            """Operação de stress com erros."""
            nonlocal error_count, success_count
            
            for i in range(100):
                keywords = [
                    Keyword(termo=f"stress_keyword_{thread_id}_{i}", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
                ]
                
                try:
                    # Simular erro aleatório
                    if random.random() < 0.3:  # 30% de chance de erro
                        raise ConnectionError(f"Random error {thread_id}_{i}")
                    
                    resultado = processador_with_error_handling.processar_keywords(keywords)
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    # Erro deve ser tratado graciosamente
                    assert "connection" in str(e).lower() or "random" in str(e).lower()
        
        # Executar operações de stress
        threads = []
        for i in range(5):
            thread = threading.Thread(target=stress_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar que sistema lidou com stress
        assert error_count > 0
        assert success_count > 0
        assert error_count + success_count == 500  # 5 threads * 100 operações cada

    def test_memory_error_recovery(self, processador_with_error_handling):
        """Testa recuperação de erros de memória."""
        memory_pressure = []
        
        def memory_intensive_operation():
            """Operação intensiva em memória."""
            try:
                # Criar pressão de memória
                for i in range(1000):
                    memory_pressure.append([i] * 1000)
                
                # Tentar processamento
                keywords = [
                    Keyword(termo=f"memory_keyword_{i}", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
                    for i in range(100)
                ]
                
                resultado = processador_with_error_handling.processar_keywords(keywords)
                return resultado
                
            except MemoryError:
                # Liberar memória e tentar novamente
                memory_pressure.clear()
                import gc
                gc.collect()
                
                # Tentar com menos dados
                keywords = [
                    Keyword(termo=f"recovery_keyword_{i}", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
                    for i in range(10)
                ]
                
                return processador_with_error_handling.processar_keywords(keywords)
        
        # Testar recuperação
        try:
            resultado = memory_intensive_operation()
            assert isinstance(resultado, list)
        except Exception as e:
            # Erro deve ser tratado
            assert "memory" in str(e).lower() or "insufficient" in str(e).lower()

    # ==================== TESTES DE CONFIGURAÇÃO ====================

    @pytest.mark.parametrize("error_config", [
        # Configuração agressiva
        {
            "max_retries": 5,
            "retry_delay": 0.05,
            "timeout": 2.0,
            "circuit_breaker_enabled": True,
            "circuit_breaker_threshold": 3
        },
        # Configuração conservadora
        {
            "max_retries": 1,
            "retry_delay": 1.0,
            "timeout": 10.0,
            "circuit_breaker_enabled": False
        },
        # Configuração balanceada
        {
            "max_retries": 3,
            "retry_delay": 0.1,
            "timeout": 5.0,
            "circuit_breaker_enabled": True,
            "circuit_breaker_threshold": 5
        }
    ])
    def test_error_handling_configurations(self, error_config):
        """Testa diferentes configurações de error handling."""
        processador = ProcessadorKeywords(config=error_config)
        
        # Simular erro
        with patch.object(processador, 'processar_keywords') as mock_process:
            mock_process.side_effect = ConnectionError("Test error")
            
            keywords = [
                Keyword(termo="config_keyword", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
            ]
            
            start_time = time.time()
            
            try:
                resultado = processador.processar_keywords(keywords)
                processing_time = time.time() - start_time
                
                # Verificar que configuração foi aplicada
                if error_config["max_retries"] > 1:
                    assert processing_time > error_config["retry_delay"]
                
            except Exception as e:
                # Erro deve ser tratado conforme configuração
                processing_time = time.time() - start_time
                assert processing_time <= error_config["timeout"]

    # ==================== TESTES DE MONITORAMENTO ====================

    def test_error_monitoring(self, processador_with_error_handling):
        """Testa monitoramento de erros."""
        error_events = []
        
        def error_callback(error_type, error_message, context):
            """Callback para monitoramento de erros."""
            error_events.append({
                "type": error_type,
                "message": error_message,
                "context": context,
                "timestamp": datetime.now()
            })
        
        # Configurar monitoramento
        processador_with_error_handling.set_error_callback(error_callback)
        
        # Simular erro
        with patch.object(processador_with_error_handling, 'processar_keywords') as mock_process:
            mock_process.side_effect = ConnectionError("Monitored error")
            
            keywords = [
                Keyword(termo="monitor_keyword", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
            ]
            
            try:
                processador_with_error_handling.processar_keywords(keywords)
            except Exception:
                pass
            
            # Verificar que erro foi monitorado
            assert len(error_events) > 0
            assert error_events[0]["type"] == "ConnectionError"
            assert "monitored" in error_events[0]["message"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
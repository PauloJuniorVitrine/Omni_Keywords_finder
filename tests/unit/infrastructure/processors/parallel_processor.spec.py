from typing import Dict, List, Optional, Any
"""
Testes unitários para ParallelProcessor
⚠️ CRIAR MAS NÃO EXECUTAR - Executar apenas na Fase 6.5

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 2.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from infrastructure.processamento.parallel_processor import (
    ParallelProcessor,
    ProcessingConfig,
    ProcessingResult,
    ProcessingStatus,
    BatchProcessor,
    process_keyword_enrichment,
    process_keyword_validation,
    process_keyword_analysis
)
from domain.models import Keyword

class TestParallelProcessor:
    """Testes para ParallelProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Fixture para processador."""
        config = ProcessingConfig(
            max_concurrent=5,
            max_retries=2,
            retry_delay=0.1,
            timeout=5.0
        )
        return ParallelProcessor(config)
    
    @pytest.fixture
    def sample_keywords(self):
        """Fixture para keywords de teste."""
        return [
            Keyword(id=1, termo="marketing digital", volume_busca=10000, cpc=2.50, dificuldade=0.6, cluster_id=1),
            Keyword(id=2, termo="seo otimização", volume_busca=8000, cpc=2.00, dificuldade=0.5, cluster_id=1),
            Keyword(id=3, termo="google ads", volume_busca=12000, cpc=3.00, dificuldade=0.7, cluster_id=1),
            Keyword(id=4, termo="social media", volume_busca=6000, cpc=1.50, dificuldade=0.4, cluster_id=1),
            Keyword(id=5, termo="content marketing", volume_busca=9000, cpc=2.25, dificuldade=0.6, cluster_id=1)
        ]
    
    @pytest.mark.asyncio
    async def test_init(self, processor):
        """Testa inicialização do processador."""
        assert processor.config.max_concurrent == 5
        assert processor.config.max_retries == 2
        assert processor.config.retry_delay == 0.1
        assert processor.config.timeout == 5.0
        assert processor.semaphore._value == 5
        assert isinstance(processor.processing_stats, dict)
        assert isinstance(processor.circuit_breaker, dict)
    
    @pytest.mark.asyncio
    async def test_process_keywords_success(self, processor, sample_keywords):
        """Testa processamento bem-sucedido de keywords."""
        async def mock_processor(keyword):
            await asyncio.sleep(0.1)  # Simular processamento
            return {"processed": True, "keyword": keyword.termo}
        
        results = await processor.process_keywords(sample_keywords, mock_processor)
        
        assert len(results) == 5
        assert all(isinstance(r, ProcessingResult) for r in results)
        assert all(r.status == ProcessingStatus.COMPLETED for r in results)
        assert all(r.data["processed"] is True for r in results)
        assert processor.processing_stats['successful'] == 5
        assert processor.processing_stats['failed'] == 0
    
    @pytest.mark.asyncio
    async def test_process_keywords_with_failures(self, processor, sample_keywords):
        """Testa processamento com falhas."""
        async def mock_processor_with_failures(keyword):
            await asyncio.sleep(0.1)
            if keyword.id == 2:  # Falhar no segundo keyword
                raise Exception("Processing failed")
            return {"processed": True, "keyword": keyword.termo}
        
        results = await processor.process_keywords(sample_keywords, mock_processor_with_failures)
        
        assert len(results) == 5
        completed = [r for r in results if r.status == ProcessingStatus.COMPLETED]
        failed = [r for r in results if r.status == ProcessingStatus.FAILED]
        
        assert len(completed) == 4
        assert len(failed) == 1
        assert failed[0].keyword.id == 2
        assert "Processing failed" in failed[0].error
    
    @pytest.mark.asyncio
    async def test_process_keywords_timeout(self, processor, sample_keywords):
        """Testa processamento com timeout."""
        async def slow_processor(keyword):
            await asyncio.sleep(10.0)  # Mais que o timeout
            return {"processed": True}
        
        results = await processor.process_keywords(sample_keywords, slow_processor)
        
        assert len(results) == 5
        failed = [r for r in results if r.status == ProcessingStatus.FAILED]
        assert len(failed) == 5
        assert all("Timeout" in r.error for r in failed)
    
    @pytest.mark.asyncio
    async def test_process_keywords_with_retries(self, processor, sample_keywords):
        """Testa processamento com retries."""
        call_count = 0
        
        async def processor_with_retries(keyword):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)
            
            if call_count <= 2:  # Falhar nas primeiras duas tentativas
                raise Exception("Temporary failure")
            
            return {"processed": True, "attempts": call_count}
        
        results = await processor.process_keywords(sample_keywords, processor_with_retries)
        
        assert len(results) == 5
        assert all(r.status == ProcessingStatus.COMPLETED for r in results)
        assert processor.processing_stats['retried'] > 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self, processor, sample_keywords):
        """Testa circuit breaker."""
        async def failing_processor(keyword):
            raise Exception("Always fails")
        
        # Configurar threshold baixo para testar
        processor.circuit_breaker['threshold'] = 2
        
        results = await processor.process_keywords(sample_keywords, failing_processor)
        
        # Verificar se circuit breaker foi ativado
        assert processor.circuit_breaker['is_open'] is True
        assert processor.circuit_breaker['failure_count'] >= 2
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_reset(self, processor, sample_keywords):
        """Testa reset do circuit breaker."""
        # Abrir circuit breaker
        processor.circuit_breaker['is_open'] = True
        processor.circuit_breaker['failure_count'] = 5
        processor.circuit_breaker['last_failure_time'] = time.time() - 70  # Mais que timeout
        
        async def success_processor(keyword):
            return {"processed": True}
        
        results = await processor.process_keywords(sample_keywords, success_processor)
        
        # Verificar se circuit breaker foi resetado
        assert processor.circuit_breaker['is_open'] is False
        assert processor.circuit_breaker['failure_count'] == 0
    
    @pytest.mark.asyncio
    async def test_concurrent_limit(self, processor, sample_keywords):
        """Testa limite de concorrência."""
        active_tasks = 0
        max_active = 0
        
        async def concurrent_processor(keyword):
            nonlocal active_tasks, max_active
            active_tasks += 1
            max_active = max(max_active, active_tasks)
            
            await asyncio.sleep(0.2)  # Simular processamento
            
            active_tasks -= 1
            return {"processed": True}
        
        results = await processor.process_keywords(sample_keywords, concurrent_processor)
        
        # Verificar se não excedeu o limite de concorrência
        assert max_active <= processor.config.max_concurrent
        assert len(results) == 5
    
    @pytest.mark.asyncio
    async def test_retry_delay_calculation(self, processor):
        """Testa cálculo de delay para retry."""
        # Testar backoff exponencial
        delay1 = processor._calculate_retry_delay(1)
        delay2 = processor._calculate_retry_delay(2)
        delay3 = processor._calculate_retry_delay(3)
        
        assert delay1 < delay2 < delay3
        assert delay1 >= processor.config.retry_delay
        assert delay2 >= processor.config.retry_delay * processor.config.backoff_factor
    
    @pytest.mark.asyncio
    async def test_retry_delay_with_jitter(self, processor):
        """Testa delay com jitter."""
        processor.config.jitter = True
        
        delays = []
        for _ in range(10):
            delay = processor._calculate_retry_delay(1)
            delays.append(delay)
        
        # Verificar se há variação (jitter)
        assert len(set(delays)) > 1
    
    def test_get_stats(self, processor):
        """Testa obtenção de estatísticas."""
        stats = processor.get_stats()
        
        assert isinstance(stats, dict)
        assert 'total_processed' in stats
        assert 'successful' in stats
        assert 'failed' in stats
        assert 'retried' in stats
        assert 'total_time' in stats
        assert 'avg_time' in stats
        assert 'success_rate' in stats
        assert 'retry_rate' in stats
        assert 'circuit_breaker_open' in stats
        assert 'circuit_breaker_failures' in stats
    
    def test_reset_stats(self, processor):
        """Testa reset de estatísticas."""
        # Adicionar algumas estatísticas
        processor.processing_stats['total_processed'] = 10
        processor.processing_stats['successful'] = 8
        processor.processing_stats['failed'] = 2
        
        processor.reset_stats()
        
        assert processor.processing_stats['total_processed'] == 0
        assert processor.processing_stats['successful'] == 0
        assert processor.processing_stats['failed'] == 0

class TestBatchProcessor:
    """Testes para BatchProcessor."""
    
    @pytest.fixture
    def batch_processor(self):
        """Fixture para processador em lotes."""
        return BatchProcessor(batch_size=2)
    
    @pytest.fixture
    def sample_keywords(self):
        """Fixture para keywords de teste."""
        return [
            Keyword(id=1, termo="keyword1", volume_busca=1000, cpc=1.0, dificuldade=0.5, cluster_id=1),
            Keyword(id=2, termo="keyword2", volume_busca=2000, cpc=2.0, dificuldade=0.6, cluster_id=1),
            Keyword(id=3, termo="keyword3", volume_busca=3000, cpc=3.0, dificuldade=0.7, cluster_id=1),
            Keyword(id=4, termo="keyword4", volume_busca=4000, cpc=4.0, dificuldade=0.8, cluster_id=1),
            Keyword(id=5, termo="keyword5", volume_busca=5000, cpc=5.0, dificuldade=0.9, cluster_id=1)
        ]
    
    @pytest.mark.asyncio
    async def test_init(self, batch_processor):
        """Testa inicialização do processador em lotes."""
        assert batch_processor.batch_size == 2
        assert isinstance(batch_processor.processor, ParallelProcessor)
        assert batch_processor.progress_callback is None
    
    @pytest.mark.asyncio
    async def test_process_in_batches(self, batch_processor, sample_keywords):
        """Testa processamento em lotes."""
        progress_calls = []
        
        def progress_callback(processed, total):
            progress_calls.append((processed, total))
        
        batch_processor.set_progress_callback(progress_callback)
        
        async def mock_processor(keyword):
            await asyncio.sleep(0.1)
            return {"processed": True, "keyword": keyword.termo}
        
        results = await batch_processor.process_in_batches(sample_keywords, mock_processor)
        
        assert len(results) == 5
        assert all(r.status == ProcessingStatus.COMPLETED for r in results)
        
        # Verificar se callback foi chamado
        assert len(progress_calls) > 0
        assert progress_calls[-1] == (5, 5)  # Última chamada deve ser completa
    
    @pytest.mark.asyncio
    async def test_process_in_batches_with_failures(self, batch_processor, sample_keywords):
        """Testa processamento em lotes com falhas."""
        async def failing_processor(keyword):
            if keyword.id == 3:  # Falhar no terceiro keyword
                raise Exception("Batch processing failed")
            await asyncio.sleep(0.1)
            return {"processed": True}
        
        results = await batch_processor.process_in_batches(sample_keywords, failing_processor)
        
        assert len(results) == 5
        completed = [r for r in results if r.status == ProcessingStatus.COMPLETED]
        failed = [r for r in results if r.status == ProcessingStatus.FAILED]
        
        assert len(completed) == 4
        assert len(failed) == 1
        assert failed[0].keyword.id == 3
    
    def test_get_processor_stats(self, batch_processor):
        """Testa obtenção de estatísticas do processador."""
        stats = batch_processor.get_processor_stats()
        
        assert isinstance(stats, dict)
        assert 'total_processed' in stats
        assert 'successful' in stats
        assert 'failed' in stats

class TestProcessingFunctions:
    """Testes para funções de processamento específicas."""
    
    @pytest.mark.asyncio
    async def test_process_keyword_enrichment(self):
        """Testa função de enriquecimento de keyword."""
        keyword = Keyword(id=1, termo="test keyword", volume_busca=1000, cpc=1.0, dificuldade=0.5, cluster_id=1)
        
        result = await process_keyword_enrichment(keyword)
        
        assert isinstance(result, dict)
        assert 'enriched_data' in result
        assert 'processing_timestamp' in result
        
        enriched_data = result['enriched_data']
        assert 'volume_estimate' in enriched_data
        assert 'competition_level' in enriched_data
        assert 'trend_direction' in enriched_data
        assert 'seasonality' in enriched_data
    
    @pytest.mark.asyncio
    async def test_process_keyword_validation(self):
        """Testa função de validação de keyword."""
        keyword = Keyword(id=1, termo="test keyword", volume_busca=1000, cpc=1.0, dificuldade=0.5, cluster_id=1)
        
        result = await process_keyword_validation(keyword)
        
        assert isinstance(result, dict)
        assert 'validation_result' in result
        assert 'processing_timestamp' in result
        
        validation_result = result['validation_result']
        assert 'is_valid' in validation_result
        assert 'score' in validation_result
        assert 'issues' in validation_result
        assert 'suggestions' in validation_result
    
    @pytest.mark.asyncio
    async def test_process_keyword_analysis(self):
        """Testa função de análise de keyword."""
        keyword = Keyword(id=1, termo="test keyword", volume_busca=1000, cpc=1.0, dificuldade=0.5, cluster_id=1)
        
        result = await process_keyword_analysis(keyword)
        
        assert isinstance(result, dict)
        assert 'analysis_result' in result
        assert 'processing_timestamp' in result
        
        analysis_result = result['analysis_result']
        assert 'intent_type' in analysis_result
        assert 'difficulty_score' in analysis_result
        assert 'opportunity_score' in analysis_result
        assert 'related_keywords' in analysis_result

class TestProcessingConfig:
    """Testes para configuração de processamento."""
    
    def test_default_config(self):
        """Testa configuração padrão."""
        config = ProcessingConfig()
        
        assert config.max_concurrent == 10
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.timeout == 30.0
        assert config.backoff_factor == 2.0
        assert config.jitter is True
    
    def test_custom_config(self):
        """Testa configuração customizada."""
        config = ProcessingConfig(
            max_concurrent=5,
            max_retries=2,
            retry_delay=0.5,
            timeout=10.0,
            backoff_factor=1.5,
            jitter=False
        )
        
        assert config.max_concurrent == 5
        assert config.max_retries == 2
        assert config.retry_delay == 0.5
        assert config.timeout == 10.0
        assert config.backoff_factor == 1.5
        assert config.jitter is False

class TestProcessingResult:
    """Testes para resultado de processamento."""
    
    def test_processing_result_creation(self):
        """Testa criação de resultado de processamento."""
        keyword = Keyword(id=1, termo="test", volume_busca=1000, cpc=1.0, dificuldade=0.5, cluster_id=1)
        
        result = ProcessingResult(
            keyword=keyword,
            status=ProcessingStatus.COMPLETED,
            data={"test": "data"},
            processing_time=1.5,
            retry_count=2
        )
        
        assert result.keyword == keyword
        assert result.status == ProcessingStatus.COMPLETED
        assert result.data == {"test": "data"}
        assert result.processing_time == 1.5
        assert result.retry_count == 2
        assert result.error is None
    
    def test_processing_result_with_error(self):
        """Testa resultado de processamento com erro."""
        keyword = Keyword(id=1, termo="test", volume_busca=1000, cpc=1.0, dificuldade=0.5, cluster_id=1)
        
        result = ProcessingResult(
            keyword=keyword,
            status=ProcessingStatus.FAILED,
            error="Test error",
            processing_time=0.5
        )
        
        assert result.status == ProcessingStatus.FAILED
        assert result.error == "Test error"
        assert result.data is None 
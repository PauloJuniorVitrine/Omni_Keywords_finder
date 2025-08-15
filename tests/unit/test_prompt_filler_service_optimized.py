"""
Testes Unitários para Prompt Filler Service Optimized
Serviço de Preenchimento de Prompts Otimizado - Omni Keywords Finder

Prompt: Implementação de testes unitários para serviço de preenchimento otimizado
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
import time
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.app.services.prompt_filler_service_optimized import (
    PromptFillerServiceOptimized,
    ProcessingResult,
    ProcessingStatus
)
from backend.app.models.prompt_system import (
    Nicho, Categoria, DadosColetados, PromptBase, PromptPreenchido
)
from infrastructure.logging.advanced_logging_system import LogContext, LogCategory


class TestProcessingStatus:
    """Testes para enum ProcessingStatus"""
    
    def test_processing_status_values(self):
        """Testa valores do enum ProcessingStatus"""
        assert ProcessingStatus.PENDING.value == "pending"
        assert ProcessingStatus.PROCESSING.value == "processing"
        assert ProcessingStatus.COMPLETED.value == "completed"
        assert ProcessingStatus.FAILED.value == "failed"
        assert ProcessingStatus.CACHED.value == "cached"


class TestProcessingResult:
    """Testes para ProcessingResult"""
    
    def test_processing_result_success(self):
        """Testa criação de ProcessingResult com sucesso"""
        result = ProcessingResult(
            success=True,
            prompt_preenchido="Prompt preenchido com sucesso",
            lacunas_detectadas=["[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]"],
            lacunas_preenchidas=["[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]"],
            tempo_processamento=1.5,
            cache_hit=False,
            metadata={"categoria_nome": "Marketing", "nicho_id": 1}
        )
        
        assert result.success is True
        assert result.prompt_preenchido == "Prompt preenchido com sucesso"
        assert result.lacunas_detectadas == ["[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]"]
        assert result.lacunas_preenchidas == ["[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]"]
        assert result.tempo_processamento == 1.5
        assert result.cache_hit is False
        assert result.error is None
        assert result.metadata["categoria_nome"] == "Marketing"
    
    def test_processing_result_failure(self):
        """Testa criação de ProcessingResult com falha"""
        result = ProcessingResult(
            success=False,
            error="Dados não encontrados",
            tempo_processamento=0.5
        )
        
        assert result.success is False
        assert result.error == "Dados não encontrados"
        assert result.tempo_processamento == 0.5
        assert result.prompt_preenchido is None
        assert result.cache_hit is False
    
    def test_processing_result_cache_hit(self):
        """Testa criação de ProcessingResult com cache hit"""
        result = ProcessingResult(
            success=True,
            prompt_preenchido="Prompt do cache",
            lacunas_detectadas=[],
            lacunas_preenchidas=[],
            tempo_processamento=0.1,
            cache_hit=True
        )
        
        assert result.success is True
        assert result.cache_hit is True
        assert result.tempo_processamento == 0.1


class TestPromptFillerServiceOptimized:
    """Testes para PromptFillerServiceOptimized"""
    
    @pytest.fixture
    def mock_logger(self):
        """Mock do logger"""
        return Mock()
    
    @pytest.fixture
    def mock_cache(self):
        """Mock do cache"""
        cache = Mock()
        cache.get.return_value = None
        cache.set.return_value = None
        cache.clear.return_value = None
        cache.get_stats.return_value = {"hits": 10, "misses": 5}
        cache.warm_cache.return_value = None
        return cache
    
    @pytest.fixture
    def mock_performance_monitor(self):
        """Mock do monitor de performance"""
        monitor = Mock()
        monitor.get_dashboard_data.return_value = {"avg_response_time": 150}
        return monitor
    
    @pytest.fixture
    def prompt_service(self, mock_logger, mock_cache, mock_performance_monitor):
        """Instância do PromptFillerServiceOptimized para testes"""
        with patch('backend.app.services.prompt_filler_service_optimized.get_logger', return_value=mock_logger):
            with patch('backend.app.services.prompt_filler_service_optimized.get_cache', return_value=mock_cache):
                with patch('backend.app.services.prompt_filler_service_optimized.get_performance_monitor', return_value=mock_performance_monitor):
                    return PromptFillerServiceOptimized()
    
    def test_prompt_service_initialization(self, prompt_service, mock_logger, mock_cache, mock_performance_monitor):
        """Testa inicialização do PromptFillerServiceOptimized"""
        assert prompt_service.logger == mock_logger
        assert prompt_service.cache == mock_cache
        assert prompt_service.performance_monitor == mock_performance_monitor
        assert prompt_service.default_ttl == 3600
        assert prompt_service.max_retries == 3
        assert prompt_service.timeout_seconds == 30
        
        # Verificar estatísticas iniciais
        assert prompt_service.stats['total_processed'] == 0
        assert prompt_service.stats['cache_hits'] == 0
        assert prompt_service.stats['cache_misses'] == 0
        assert prompt_service.stats['errors'] == 0
        assert prompt_service.stats['avg_processing_time'] == 0.0
    
    def test_detectar_lacunas(self, prompt_service):
        """Testa detecção de lacunas no prompt"""
        prompt_conteudo = """
        Crie um artigo sobre [PALAVRA-CHAVE PRINCIPAL DO CLUSTER] 
        incluindo [PALAVRAS-CHAVE SECUNDÁRIAS] e 
        baseado no [CLUSTER DE CONTEÚDO].
        """
        
        lacunas = prompt_service._detectar_lacunas(prompt_conteudo)
        
        assert len(lacunas) == 3
        assert "[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]" in lacunas
        assert "[PALAVRAS-CHAVE SECUNDÁRIAS]" in lacunas
        assert "[CLUSTER DE CONTEÚDO]" in lacunas
    
    def test_detectar_lacunas_sem_lacunas(self, prompt_service):
        """Testa detecção de lacunas em prompt sem lacunas"""
        prompt_conteudo = "Crie um artigo sobre marketing digital."
        
        lacunas = prompt_service._detectar_lacunas(prompt_conteudo)
        
        assert len(lacunas) == 0
    
    def test_preencher_lacunas(self, prompt_service):
        """Testa preenchimento de lacunas"""
        prompt_conteudo = """
        Crie um artigo sobre [PALAVRA-CHAVE PRINCIPAL DO CLUSTER] 
        incluindo [PALAVRAS-CHAVE SECUNDÁRIAS].
        """
        
        lacunas = ["[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]", "[PALAVRAS-CHAVE SECUNDÁRIAS]"]
        dados = {
            'primary_keyword': 'Marketing Digital',
            'secondary_keywords': 'SEO, SEM, Redes Sociais',
            'cluster_content': 'Conteúdo do cluster'
        }
        
        prompt_preenchido, lacunas_preenchidas = prompt_service._preencher_lacunas(
            prompt_conteudo, lacunas, dados
        )
        
        assert "Marketing Digital" in prompt_preenchido
        assert "SEO, SEM, Redes Sociais" in prompt_preenchido
        assert "[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]" not in prompt_preenchido
        assert "[PALAVRAS-CHAVE SECUNDÁRIAS]" not in prompt_preenchido
        assert len(lacunas_preenchidas) == 2
    
    def test_preencher_lacunas_dados_parciais(self, prompt_service):
        """Testa preenchimento de lacunas com dados parciais"""
        prompt_conteudo = "Crie um artigo sobre [PALAVRA-CHAVE PRINCIPAL DO CLUSTER]."
        
        lacunas = ["[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]"]
        dados = {
            'primary_keyword': 'Marketing Digital',
            'secondary_keywords': '',  # Vazio
            'cluster_content': ''  # Vazio
        }
        
        prompt_preenchido, lacunas_preenchidas = prompt_service._preencher_lacunas(
            prompt_conteudo, lacunas, dados
        )
        
        assert "Marketing Digital" in prompt_preenchido
        assert len(lacunas_preenchidas) == 1
    
    def test_validar_preenchimento_valido(self, prompt_service):
        """Testa validação de preenchimento válido"""
        prompt_preenchido = "Crie um artigo sobre Marketing Digital com pelo menos 50 caracteres de conteúdo."
        lacunas_detectadas = ["[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]"]
        
        result = prompt_service._validar_preenchimento(prompt_preenchido, lacunas_detectadas)
        
        assert result is True
    
    def test_validar_preenchimento_lacunas_restantes(self, prompt_service):
        """Testa validação de preenchimento com lacunas restantes"""
        prompt_preenchido = "Crie um artigo sobre Marketing Digital [PALAVRA-CHAVE PRINCIPAL DO CLUSTER]."
        lacunas_detectadas = ["[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]"]
        
        result = prompt_service._validar_preenchimento(prompt_preenchido, lacunas_detectadas)
        
        assert result is False
    
    def test_validar_preenchimento_vazio(self, prompt_service):
        """Testa validação de preenchimento vazio"""
        prompt_preenchido = ""
        lacunas_detectadas = ["[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]"]
        
        result = prompt_service._validar_preenchimento(prompt_preenchido, lacunas_detectadas)
        
        assert result is False
    
    def test_validar_preenchimento_muito_curto(self, prompt_service):
        """Testa validação de preenchimento muito curto"""
        prompt_preenchido = "Artigo curto"
        lacunas_detectadas = ["[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]"]
        
        result = prompt_service._validar_preenchimento(prompt_preenchido, lacunas_detectadas)
        
        assert result is False
    
    def test_process_fill_success(self, prompt_service, mock_logger):
        """Testa processamento interno com sucesso"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_session = Mock()
        mock_db.__next__.return_value = mock_session
        
        # Mock dos dados do banco
        mock_categoria = Mock()
        mock_categoria.id = 1
        mock_categoria.nome = "Marketing"
        mock_categoria.nicho_id = 1
        
        mock_dados = Mock()
        mock_dados.id = 1
        mock_dados.primary_keyword = "Marketing Digital"
        mock_dados.secondary_keywords = "SEO, SEM"
        mock_dados.cluster_content = "Conteúdo do cluster"
        
        mock_prompt_base = Mock()
        mock_prompt_base.conteudo = "Crie um artigo sobre [PALAVRA-CHAVE PRINCIPAL DO CLUSTER]."
        
        # Configurar queries
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_categoria, mock_dados, mock_prompt_base
        ]
        
        with patch('backend.app.services.prompt_filler_service_optimized.get_db', return_value=mock_db):
            result = prompt_service._process_fill(1, 1, Mock())
        
        assert result.success is True
        assert "Marketing Digital" in result.prompt_preenchido
        assert result.lacunas_detectadas == ["[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]"]
        assert result.lacunas_preenchidas == ["[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]"]
        assert result.metadata["categoria_nome"] == "Marketing"
        assert result.metadata["nicho_id"] == 1
    
    def test_process_fill_dados_nao_encontrados(self, prompt_service):
        """Testa processamento interno com dados não encontrados"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_session = Mock()
        mock_db.__next__.return_value = mock_session
        
        # Configurar queries para retornar None
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        with patch('backend.app.services.prompt_filler_service_optimized.get_db', return_value=mock_db):
            result = prompt_service._process_fill(1, 1, Mock())
        
        assert result.success is False
        assert result.error == "Dados não encontrados"
    
    def test_process_fill_exception(self, prompt_service):
        """Testa processamento interno com exceção"""
        # Mock do banco de dados que levanta exceção
        mock_db = Mock()
        mock_db.__next__.side_effect = Exception("Database error")
        
        with patch('backend.app.services.prompt_filler_service_optimized.get_db', return_value=mock_db):
            result = prompt_service._process_fill(1, 1, Mock())
        
        assert result.success is False
        assert "Database error" in result.error
    
    def test_save_to_database_new(self, prompt_service, mock_logger):
        """Testa salvamento no banco de dados - novo registro"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_session = Mock()
        mock_db.__next__.return_value = mock_session
        
        # Configurar query para não encontrar registro existente
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Mock do resultado de processamento
        result = ProcessingResult(
            success=True,
            prompt_preenchido="Prompt preenchido",
            lacunas_detectadas=["[PALAVRA-CHAVE]"],
            lacunas_preenchidas=["[PALAVRA-CHAVE]"],
            tempo_processamento=1.5
        )
        
        context = LogContext(
            operation="test",
            module="test",
            function="test"
        )
        
        with patch('backend.app.services.prompt_filler_service_optimized.get_db', return_value=mock_db):
            prompt_preenchido = prompt_service._save_to_database(1, 1, result, context)
        
        # Verificar se foi adicionado ao banco
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        
        # Verificar se o objeto criado é do tipo correto
        added_prompt = mock_session.add.call_args[0][0]
        assert isinstance(added_prompt, PromptPreenchido)
        assert added_prompt.prompt_preenchido == "Prompt preenchido"
        assert added_prompt.status == 'pronto'
    
    def test_save_to_database_existing(self, prompt_service, mock_logger):
        """Testa salvamento no banco de dados - registro existente"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_session = Mock()
        mock_db.__next__.return_value = mock_session
        
        # Mock de prompt existente
        mock_prompt_existente = Mock()
        mock_prompt_existente.prompt_preenchido = "Prompt antigo"
        mock_prompt_existente.lacunas_detectadas = "[]"
        mock_prompt_existente.lacunas_preenchidas = "[]"
        mock_prompt_existente.tempo_processamento = 1.0
        mock_prompt_existente.status = 'processando'
        
        # Configurar query para encontrar registro existente
        mock_session.query.return_value.filter.return_value.first.return_value = mock_prompt_existente
        
        # Mock do resultado de processamento
        result = ProcessingResult(
            success=True,
            prompt_preenchido="Prompt atualizado",
            lacunas_detectadas=["[PALAVRA-CHAVE]"],
            lacunas_preenchidas=["[PALAVRA-CHAVE]"],
            tempo_processamento=2.0
        )
        
        context = LogContext(
            operation="test",
            module="test",
            function="test"
        )
        
        with patch('backend.app.services.prompt_filler_service_optimized.get_db', return_value=mock_db):
            prompt_preenchido = prompt_service._save_to_database(1, 1, result, context)
        
        # Verificar se foi atualizado
        assert mock_prompt_existente.prompt_preenchido == "Prompt atualizado"
        assert mock_prompt_existente.status == 'pronto'
        assert mock_prompt_existente.tempo_processamento == 2.0
        mock_session.commit.assert_called_once()
    
    def test_create_from_cache(self, prompt_service):
        """Testa criação a partir do cache"""
        cached_prompt = "Prompt do cache"
        
        prompt_preenchido = prompt_service._create_from_cache(cached_prompt, 1, 1)
        
        assert isinstance(prompt_preenchido, PromptPreenchido)
        assert prompt_preenchido.prompt_preenchido == cached_prompt
        assert prompt_preenchido.status == 'pronto'
        assert prompt_preenchido.tempo_processamento == 0.0
        assert prompt_preenchido.dados_coletados_id == 1
    
    def test_processar_preenchimento_cache_hit(self, prompt_service, mock_cache, mock_logger):
        """Testa processamento de preenchimento com cache hit"""
        # Configurar cache para retornar resultado
        mock_cache.get.return_value = "Prompt do cache"
        
        with patch('time.time', return_value=1000.0):
            prompt_preenchido = prompt_service.processar_preenchimento(1, 1)
        
        # Verificar se foi retornado do cache
        assert isinstance(prompt_preenchido, PromptPreenchido)
        assert prompt_preenchido.prompt_preenchido == "Prompt do cache"
        assert prompt_preenchido.status == 'pronto'
        
        # Verificar estatísticas
        assert prompt_service.stats['cache_hits'] == 1
        assert prompt_service.stats['cache_misses'] == 0
    
    def test_processar_preenchimento_cache_miss(self, prompt_service, mock_cache, mock_logger):
        """Testa processamento de preenchimento com cache miss"""
        # Configurar cache para não retornar resultado
        mock_cache.get.return_value = None
        
        # Mock do processamento interno
        with patch.object(prompt_service, '_process_fill') as mock_process:
            mock_process.return_value = ProcessingResult(
                success=True,
                prompt_preenchido="Prompt processado",
                lacunas_detectadas=["[PALAVRA-CHAVE]"],
                lacunas_preenchidas=["[PALAVRA-CHAVE]"],
                tempo_processamento=1.5
            )
            
            with patch.object(prompt_service, '_save_to_database') as mock_save:
                mock_save.return_value = Mock()
                
                with patch('time.time', side_effect=[1000.0, 1001.5]):
                    prompt_preenchido = prompt_service.processar_preenchimento(1, 1)
        
        # Verificar se foi processado
        assert isinstance(prompt_preenchido, Mock)
        
        # Verificar se foi armazenado no cache
        mock_cache.set.assert_called_once()
        
        # Verificar estatísticas
        assert prompt_service.stats['cache_hits'] == 0
        assert prompt_service.stats['cache_misses'] == 1
        assert prompt_service.stats['total_processed'] == 1
    
    def test_processar_preenchimento_error(self, prompt_service, mock_cache, mock_logger):
        """Testa processamento de preenchimento com erro"""
        # Configurar cache para não retornar resultado
        mock_cache.get.return_value = None
        
        # Mock do processamento interno com erro
        with patch.object(prompt_service, '_process_fill') as mock_process:
            mock_process.return_value = ProcessingResult(
                success=False,
                error="Erro de processamento"
            )
            
            with pytest.raises(Exception, match="Erro de processamento"):
                prompt_service.processar_preenchimento(1, 1)
        
        # Verificar estatísticas
        assert prompt_service.stats['errors'] == 1
    
    def test_processar_lote_success(self, prompt_service, mock_logger):
        """Testa processamento em lote com sucesso"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_session = Mock()
        mock_db.__next__.return_value = mock_session
        
        # Mock de dados coletados
        mock_dados1 = Mock()
        mock_dados1.id = 1
        mock_dados1.categoria_id = 1
        mock_dados1.nicho_id = 1
        mock_dados1.status = 'ativo'
        
        mock_dados2 = Mock()
        mock_dados2.id = 2
        mock_dados2.categoria_id = 2
        mock_dados2.nicho_id = 1
        mock_dados2.status = 'ativo'
        
        # Configurar query para retornar dados
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_dados1, mock_dados2]
        
        # Mock do processamento individual
        with patch.object(prompt_service, 'processar_preenchimento') as mock_process:
            mock_process.return_value = Mock()
            
            with patch('backend.app.services.prompt_filler_service_optimized.get_db', return_value=mock_db):
                with patch('time.time', side_effect=[1000.0, 1002.0]):
                    resultados = prompt_service.processar_lote(1)
        
        # Verificar resultados
        assert len(resultados) == 2
        assert mock_process.call_count == 2
    
    def test_processar_lote_with_errors(self, prompt_service, mock_logger):
        """Testa processamento em lote com erros"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_session = Mock()
        mock_db.__next__.return_value = mock_session
        
        # Mock de dados coletados
        mock_dados1 = Mock()
        mock_dados1.id = 1
        mock_dados1.categoria_id = 1
        mock_dados1.nicho_id = 1
        mock_dados1.status = 'ativo'
        
        mock_dados2 = Mock()
        mock_dados2.id = 2
        mock_dados2.categoria_id = 2
        mock_dados2.nicho_id = 1
        mock_dados2.status = 'ativo'
        
        # Configurar query para retornar dados
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_dados1, mock_dados2]
        
        # Mock do processamento individual com erro no segundo
        with patch.object(prompt_service, 'processar_preenchimento') as mock_process:
            mock_process.side_effect = [Mock(), Exception("Erro no segundo")]
            
            with patch('backend.app.services.prompt_filler_service_optimized.get_db', return_value=mock_db):
                with patch('time.time', side_effect=[1000.0, 1002.0]):
                    resultados = prompt_service.processar_lote(1)
        
        # Verificar resultados (apenas o primeiro foi processado)
        assert len(resultados) == 1
    
    def test_get_stats(self, prompt_service, mock_cache, mock_performance_monitor):
        """Testa obtenção de estatísticas"""
        # Configurar estatísticas
        prompt_service.stats['total_processed'] = 100
        prompt_service.stats['cache_hits'] = 60
        prompt_service.stats['cache_misses'] = 40
        prompt_service.stats['errors'] = 5
        prompt_service.stats['avg_processing_time'] = 1.5
        
        stats = prompt_service.get_stats()
        
        assert stats['total_processed'] == 100
        assert stats['cache_hits'] == 60
        assert stats['cache_misses'] == 40
        assert stats['cache_hit_rate'] == 0.6
        assert stats['errors'] == 5
        assert stats['error_rate'] == 0.05
        assert stats['avg_processing_time'] == 1.5
        assert 'cache_stats' in stats
        assert 'performance_stats' in stats
    
    def test_clear_cache(self, prompt_service, mock_cache, mock_logger):
        """Testa limpeza do cache"""
        prompt_service.clear_cache()
        
        mock_cache.clear.assert_called_once()
        mock_logger.info.assert_called()
    
    def test_warm_cache(self, prompt_service, mock_cache, mock_logger):
        """Testa warming do cache"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_session = Mock()
        mock_db.__next__.return_value = mock_session
        
        # Mock de dados coletados
        mock_dados1 = Mock()
        mock_dados1.id = 1
        mock_dados1.categoria_id = 1
        mock_dados1.nicho_id = 1
        mock_dados1.status = 'ativo'
        
        mock_dados2 = Mock()
        mock_dados2.id = 2
        mock_dados2.categoria_id = 2
        mock_dados2.nicho_id = 1
        mock_dados2.status = 'ativo'
        
        # Configurar query para retornar dados
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_dados1, mock_dados2]
        
        with patch('backend.app.services.prompt_filler_service_optimized.get_db', return_value=mock_db):
            prompt_service.warm_cache(1)
        
        # Verificar se warming foi executado
        mock_cache.warm_cache.assert_called_once()
        mock_logger.info.assert_called()


class TestPromptFillerServiceOptimizedIntegration:
    """Testes de integração para PromptFillerServiceOptimized"""
    
    @pytest.fixture
    def mock_logger(self):
        """Mock do logger"""
        return Mock()
    
    @pytest.fixture
    def mock_cache(self):
        """Mock do cache"""
        cache = Mock()
        cache.get.return_value = None
        cache.set.return_value = None
        cache.clear.return_value = None
        cache.get_stats.return_value = {"hits": 10, "misses": 5}
        cache.warm_cache.return_value = None
        return cache
    
    @pytest.fixture
    def mock_performance_monitor(self):
        """Mock do monitor de performance"""
        monitor = Mock()
        monitor.get_dashboard_data.return_value = {"avg_response_time": 150}
        return monitor
    
    @pytest.fixture
    def prompt_service(self, mock_logger, mock_cache, mock_performance_monitor):
        """Instância do PromptFillerServiceOptimized para testes"""
        with patch('backend.app.services.prompt_filler_service_optimized.get_logger', return_value=mock_logger):
            with patch('backend.app.services.prompt_filler_service_optimized.get_cache', return_value=mock_cache):
                with patch('backend.app.services.prompt_filler_service_optimized.get_performance_monitor', return_value=mock_performance_monitor):
                    return PromptFillerServiceOptimized()
    
    def test_full_processing_workflow(self, prompt_service, mock_cache, mock_logger):
        """Testa workflow completo de processamento"""
        # Mock do banco de dados
        mock_db = Mock()
        mock_session = Mock()
        mock_db.__next__.return_value = mock_session
        
        # Mock dos dados do banco
        mock_categoria = Mock()
        mock_categoria.id = 1
        mock_categoria.nome = "Marketing"
        mock_categoria.nicho_id = 1
        
        mock_dados = Mock()
        mock_dados.id = 1
        mock_dados.primary_keyword = "Marketing Digital"
        mock_dados.secondary_keywords = "SEO, SEM"
        mock_dados.cluster_content = "Conteúdo do cluster"
        
        mock_prompt_base = Mock()
        mock_prompt_base.conteudo = "Crie um artigo sobre [PALAVRA-CHAVE PRINCIPAL DO CLUSTER]."
        
        # Configurar queries
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_categoria, mock_dados, mock_prompt_base
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        # Configurar cache para não retornar resultado inicialmente
        mock_cache.get.return_value = None
        
        with patch('backend.app.services.prompt_filler_service_optimized.get_db', return_value=mock_db):
            with patch('time.time', side_effect=[1000.0, 1001.5]):
                prompt_preenchido = prompt_service.processar_preenchimento(1, 1)
        
        # Verificar se foi processado e armazenado no cache
        assert isinstance(prompt_preenchido, PromptPreenchido)
        assert "Marketing Digital" in prompt_preenchido.prompt_preenchido
        mock_cache.set.assert_called_once()
        
        # Verificar estatísticas
        assert prompt_service.stats['total_processed'] == 1
        assert prompt_service.stats['cache_misses'] == 1
        
        # Testar cache hit na próxima chamada
        mock_cache.get.return_value = "Prompt do cache"
        
        with patch('time.time', return_value=1002.0):
            prompt_preenchido2 = prompt_service.processar_preenchimento(1, 1)
        
        assert prompt_service.stats['cache_hits'] == 1


class TestPromptFillerServiceOptimizedErrorHandling:
    """Testes de tratamento de erros para PromptFillerServiceOptimized"""
    
    @pytest.fixture
    def mock_logger(self):
        """Mock do logger"""
        return Mock()
    
    @pytest.fixture
    def mock_cache(self):
        """Mock do cache"""
        cache = Mock()
        cache.get.return_value = None
        cache.set.return_value = None
        cache.clear.return_value = None
        cache.get_stats.return_value = {"hits": 10, "misses": 5}
        cache.warm_cache.return_value = None
        return cache
    
    @pytest.fixture
    def mock_performance_monitor(self):
        """Mock do monitor de performance"""
        monitor = Mock()
        monitor.get_dashboard_data.return_value = {"avg_response_time": 150}
        return monitor
    
    @pytest.fixture
    def prompt_service(self, mock_logger, mock_cache, mock_performance_monitor):
        """Instância do PromptFillerServiceOptimized para testes"""
        with patch('backend.app.services.prompt_filler_service_optimized.get_logger', return_value=mock_logger):
            with patch('backend.app.services.prompt_filler_service_optimized.get_cache', return_value=mock_cache):
                with patch('backend.app.services.prompt_filler_service_optimized.get_performance_monitor', return_value=mock_performance_monitor):
                    return PromptFillerServiceOptimized()
    
    def test_database_error_handling(self, prompt_service, mock_logger):
        """Testa tratamento de erro de banco de dados"""
        # Mock do banco de dados que levanta exceção
        mock_db = Mock()
        mock_db.__next__.side_effect = Exception("Database connection error")
        
        with patch('backend.app.services.prompt_filler_service_optimized.get_db', return_value=mock_db):
            with pytest.raises(Exception, match="Database connection error"):
                prompt_service.processar_preenchimento(1, 1)
        
        # Verificar se erro foi registrado
        assert prompt_service.stats['errors'] == 1
    
    def test_cache_error_handling(self, prompt_service, mock_cache, mock_logger):
        """Testa tratamento de erro de cache"""
        # Configurar cache para levantar exceção
        mock_cache.get.side_effect = Exception("Cache error")
        
        with pytest.raises(Exception, match="Cache error"):
            prompt_service.processar_preenchimento(1, 1)
        
        # Verificar se erro foi registrado
        assert prompt_service.stats['errors'] == 1


class TestPromptFillerServiceOptimizedPerformance:
    """Testes de performance para PromptFillerServiceOptimized"""
    
    @pytest.fixture
    def mock_logger(self):
        """Mock do logger"""
        return Mock()
    
    @pytest.fixture
    def mock_cache(self):
        """Mock do cache"""
        cache = Mock()
        cache.get.return_value = None
        cache.set.return_value = None
        cache.clear.return_value = None
        cache.get_stats.return_value = {"hits": 10, "misses": 5}
        cache.warm_cache.return_value = None
        return cache
    
    @pytest.fixture
    def mock_performance_monitor(self):
        """Mock do monitor de performance"""
        monitor = Mock()
        monitor.get_dashboard_data.return_value = {"avg_response_time": 150}
        return monitor
    
    @pytest.fixture
    def prompt_service(self, mock_logger, mock_cache, mock_performance_monitor):
        """Instância do PromptFillerServiceOptimized para testes"""
        with patch('backend.app.services.prompt_filler_service_optimized.get_logger', return_value=mock_logger):
            with patch('backend.app.services.prompt_filler_service_optimized.get_cache', return_value=mock_cache):
                with patch('backend.app.services.prompt_filler_service_optimized.get_performance_monitor', return_value=mock_performance_monitor):
                    return PromptFillerServiceOptimized()
    
    def test_multiple_processing_performance(self, prompt_service, mock_cache, mock_logger):
        """Testa performance de múltiplos processamentos"""
        import time
        
        # Mock do banco de dados
        mock_db = Mock()
        mock_session = Mock()
        mock_db.__next__.return_value = mock_session
        
        # Mock dos dados do banco
        mock_categoria = Mock()
        mock_categoria.id = 1
        mock_categoria.nome = "Marketing"
        mock_categoria.nicho_id = 1
        
        mock_dados = Mock()
        mock_dados.id = 1
        mock_dados.primary_keyword = "Marketing Digital"
        mock_dados.secondary_keywords = "SEO, SEM"
        mock_dados.cluster_content = "Conteúdo do cluster"
        
        mock_prompt_base = Mock()
        mock_prompt_base.conteudo = "Crie um artigo sobre [PALAVRA-CHAVE PRINCIPAL DO CLUSTER]."
        
        # Configurar queries
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_categoria, mock_dados, mock_prompt_base
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        # Configurar cache
        mock_cache.get.return_value = None
        
        start_time = time.time()
        
        # Processar múltiplos prompts
        with patch('backend.app.services.prompt_filler_service_optimized.get_db', return_value=mock_db):
            for i in range(10):
                with patch('time.time', side_effect=[1000.0 + i, 1001.0 + i]):
                    prompt_preenchido = prompt_service.processar_preenchimento(1, 1)
                    assert isinstance(prompt_preenchido, PromptPreenchido)
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 5.0  # Menos de 5 segundos para 10 processamentos
        
        # Verificar estatísticas
        assert prompt_service.stats['total_processed'] == 10
        assert prompt_service.stats['cache_misses'] == 10


if __name__ == "__main__":
    pytest.main([__file__]) 
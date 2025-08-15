"""
Testes Unitários para ML Processor
Processador de Machine Learning para Keywords - Omni Keywords Finder

Prompt: Implementação de testes unitários para processador ML
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from infrastructure.processamento.ml_processor import MLProcessor
from domain.models import Keyword, IntencaoBusca


class TestMLProcessor:
    """Testes para MLProcessor"""
    
    @pytest.fixture
    def mock_ml_adaptativo(self):
        """Mock do MLAdaptativo para testes"""
        mock = Mock()
        mock.sugerir.return_value = []
        mock.bloquear_repetidos.return_value = []
        mock.treinar_incremental.return_value = None
        mock.versao = "1.0.0"
        mock.data_treinamento = datetime.now().isoformat()
        return mock
    
    @pytest.fixture
    def sample_keywords(self):
        """Keywords de exemplo para testes"""
        return [
            Keyword(
                termo="palavra chave teste",
                volume_busca=1000,
                cpc=1.50,
                concorrencia=0.7,
                intencao=IntencaoBusca.INFORMACIONAL,
                score=85.5,
                justificativa="Teste de keyword",
                fonte="google_ads",
                data_coleta=datetime.now()
            ),
            Keyword(
                termo="outra keyword",
                volume_busca=500,
                cpc=2.00,
                concorrencia=0.5,
                intencao=IntencaoBusca.TRANSACIONAL,
                score=92.0,
                justificativa="Segunda keyword de teste",
                fonte="google_trends",
                data_coleta=datetime.now()
            )
        ]
    
    @pytest.fixture
    def ml_processor(self, mock_ml_adaptativo):
        """Instância do MLProcessor para testes"""
        return MLProcessor(
            ml_adaptativo=mock_ml_adaptativo,
            habilitar_sugestoes=True,
            habilitar_bloqueio=True,
            habilitar_treinamento=True
        )
    
    def test_ml_processor_initialization(self, mock_ml_adaptativo):
        """Testa inicialização do MLProcessor"""
        processor = MLProcessor(
            ml_adaptativo=mock_ml_adaptativo,
            habilitar_sugestoes=True,
            habilitar_bloqueio=False,
            habilitar_treinamento=True
        )
        
        assert processor.ml_adaptativo == mock_ml_adaptativo
        assert processor.habilitar_sugestoes is True
        assert processor.habilitar_bloqueio is False
        assert processor.habilitar_treinamento is True
        assert isinstance(processor._ultimos_resultados, dict)
    
    def test_ml_processor_initialization_without_ml(self):
        """Testa inicialização do MLProcessor sem ML adaptativo"""
        processor = MLProcessor()
        
        assert processor.ml_adaptativo is None
        assert processor.habilitar_sugestoes is True
        assert processor.habilitar_bloqueio is True
        assert processor.habilitar_treinamento is True
    
    def test_processar_keywords_without_ml(self, sample_keywords):
        """Testa processamento sem ML adaptativo"""
        processor = MLProcessor(ml_adaptativo=None)
        
        result = processor.processar_keywords(sample_keywords)
        
        assert result == sample_keywords
    
    def test_processar_keywords_empty_list(self, ml_processor):
        """Testa processamento com lista vazia"""
        result = ml_processor.processar_keywords([])
        
        assert result == []
    
    def test_processar_keywords_with_ml(self, ml_processor, sample_keywords, mock_ml_adaptativo):
        """Testa processamento com ML adaptativo"""
        # Configurar mock para retornar keywords processadas
        mock_ml_adaptativo.sugerir.return_value = [
            {
                "termo": "palavra chave otimizada",
                "volume_busca": 1200,
                "cpc": 1.75,
                "concorrencia": 0.6,
                "intencao": "informacional",
                "score": 90.0,
                "justificativa": "Otimizada pelo ML",
                "fonte": "ml_suggestion",
                "data_coleta": datetime.now().isoformat()
            }
        ]
        mock_ml_adaptativo.bloquear_repetidos.return_value = mock_ml_adaptativo.sugerir.return_value
        
        result = ml_processor.processar_keywords(sample_keywords)
        
        assert len(result) == 1
        assert result[0].termo == "palavra chave otimizada"
        assert result[0].score == 90.0
        assert result[0].fonte == "ml_suggestion"
        
        # Verificar se os métodos do ML foram chamados
        mock_ml_adaptativo.sugerir.assert_called_once()
        mock_ml_adaptativo.bloquear_repetidos.assert_called_once()
    
    def test_processar_keywords_with_feedback(self, ml_processor, sample_keywords, mock_ml_adaptativo):
        """Testa processamento com feedback histórico"""
        historico_feedback = [
            {"keyword": "teste", "score": 85, "feedback": "positive"},
            {"keyword": "outro", "score": 70, "feedback": "negative"}
        ]
        
        ml_processor.processar_keywords(sample_keywords, historico_feedback)
        
        # Verificar se treinamento incremental foi chamado
        mock_ml_adaptativo.treinar_incremental.assert_called_once_with(historico_feedback)
    
    def test_processar_keywords_with_context(self, ml_processor, sample_keywords, mock_ml_adaptativo):
        """Testa processamento com contexto"""
        contexto = {
            "dominio": "ecommerce",
            "categoria": "eletronicos",
            "regiao": "brasil"
        }
        
        ml_processor.processar_keywords(sample_keywords, contexto=contexto)
        
        # Verificar se contexto foi passado para sugestões
        call_args = mock_ml_adaptativo.sugerir.call_args
        assert call_args is not None
        assert len(call_args[0]) >= 2  # keywords_dict e contexto
    
    def test_processar_keywords_with_error(self, ml_processor, sample_keywords, mock_ml_adaptativo):
        """Testa processamento com erro no ML"""
        mock_ml_adaptativo.sugerir.side_effect = Exception("Erro no ML")
        
        result = ml_processor.processar_keywords(sample_keywords)
        
        # Deve retornar keywords originais em caso de erro
        assert result == sample_keywords
    
    def test_keyword_to_dict(self, ml_processor, sample_keywords):
        """Testa conversão de Keyword para dicionário"""
        keyword = sample_keywords[0]
        kw_dict = ml_processor._keyword_to_dict(keyword)
        
        assert kw_dict["termo"] == "palavra chave teste"
        assert kw_dict["volume_busca"] == 1000
        assert kw_dict["cpc"] == 1.50
        assert kw_dict["concorrencia"] == 0.7
        assert kw_dict["intencao"] == "informacional"
        assert kw_dict["score"] == 85.5
        assert kw_dict["justificativa"] == "Teste de keyword"
        assert kw_dict["fonte"] == "google_ads"
        assert kw_dict["data_coleta"] is not None
    
    def test_dict_to_keyword(self, ml_processor):
        """Testa conversão de dicionário para Keyword"""
        kw_dict = {
            "termo": "keyword teste",
            "volume_busca": 800,
            "cpc": 1.25,
            "concorrencia": 0.6,
            "intencao": "transacional",
            "score": 88.0,
            "justificativa": "Teste de conversão",
            "fonte": "ml_processor",
            "data_coleta": datetime.now().isoformat()
        }
        
        keyword = ml_processor._dict_to_keyword(kw_dict)
        
        assert keyword.termo == "keyword teste"
        assert keyword.volume_busca == 800
        assert keyword.cpc == 1.25
        assert keyword.concorrencia == 0.6
        assert keyword.intencao == IntencaoBusca.TRANSACIONAL
        assert keyword.score == 88.0
        assert keyword.justificativa == "Teste de conversão"
        assert keyword.fonte == "ml_processor"
        assert isinstance(keyword.data_coleta, datetime)
    
    def test_dict_to_keyword_invalid_date(self, ml_processor):
        """Testa conversão com data inválida"""
        kw_dict = {
            "termo": "keyword teste",
            "volume_busca": 800,
            "cpc": 1.25,
            "concorrencia": 0.6,
            "intencao": "informacional",
            "score": 88.0,
            "justificativa": "Teste",
            "fonte": "ml_processor",
            "data_coleta": "data_invalida"
        }
        
        keyword = ml_processor._dict_to_keyword(kw_dict)
        
        assert keyword.termo == "keyword teste"
        assert isinstance(keyword.data_coleta, datetime)
    
    def test_dict_to_keyword_unknown_intention(self, ml_processor):
        """Testa conversão com intenção desconhecida"""
        kw_dict = {
            "termo": "keyword teste",
            "volume_busca": 800,
            "cpc": 1.25,
            "concorrencia": 0.6,
            "intencao": "intencao_desconhecida",
            "score": 88.0,
            "justificativa": "Teste",
            "fonte": "ml_processor",
            "data_coleta": datetime.now().isoformat()
        }
        
        keyword = ml_processor._dict_to_keyword(kw_dict)
        
        assert keyword.intencao == IntencaoBusca.INFORMACIONAL  # default
    
    @patch('infrastructure.processamento.ml_processor.logger')
    def test_treinar_incremental_success(self, mock_logger, ml_processor, mock_ml_adaptativo):
        """Testa treinamento incremental bem-sucedido"""
        historico_feedback = [
            {"keyword": "teste", "score": 85, "feedback": "positive"}
        ]
        
        ml_processor._treinar_incremental(historico_feedback)
        
        mock_ml_adaptativo.treinar_incremental.assert_called_once_with(historico_feedback)
        mock_logger.info.assert_called_once()
    
    @patch('infrastructure.processamento.ml_processor.logger')
    def test_treinar_incremental_without_ml(self, mock_logger):
        """Testa treinamento incremental sem ML adaptativo"""
        processor = MLProcessor(ml_adaptativo=None)
        historico_feedback = [{"keyword": "teste", "score": 85}]
        
        processor._treinar_incremental(historico_feedback)
        
        # Não deve chamar logger
        mock_logger.info.assert_not_called()
        mock_logger.error.assert_not_called()
    
    @patch('infrastructure.processamento.ml_processor.logger')
    def test_treinar_incremental_with_error(self, mock_logger, ml_processor, mock_ml_adaptativo):
        """Testa treinamento incremental com erro"""
        mock_ml_adaptativo.treinar_incremental.side_effect = Exception("Erro no treinamento")
        historico_feedback = [{"keyword": "teste", "score": 85}]
        
        ml_processor._treinar_incremental(historico_feedback)
        
        mock_logger.error.assert_called_once()
    
    @patch('infrastructure.processamento.ml_processor.logger')
    def test_aplicar_sugestoes_success(self, mock_logger, ml_processor, mock_ml_adaptativo):
        """Testa aplicação de sugestões bem-sucedida"""
        keywords_dict = [
            {"termo": "teste", "volume_busca": 1000, "score": 85}
        ]
        contexto = {"dominio": "ecommerce"}
        
        sugeridos = [{"termo": "teste otimizado", "volume_busca": 1200, "score": 90}]
        mock_ml_adaptativo.sugerir.return_value = sugeridos
        
        result = ml_processor._aplicar_sugestoes(keywords_dict, contexto)
        
        assert result == sugeridos
        assert ml_processor._ultimos_resultados["sugeridos"] == 1
        mock_logger.info.assert_called_once()
    
    @patch('infrastructure.processamento.ml_processor.logger')
    def test_aplicar_sugestoes_without_ml(self, mock_logger):
        """Testa aplicação de sugestões sem ML adaptativo"""
        processor = MLProcessor(ml_adaptativo=None)
        keywords_dict = [{"termo": "teste", "volume_busca": 1000}]
        
        result = processor._aplicar_sugestoes(keywords_dict, {})
        
        assert result == keywords_dict
        mock_logger.info.assert_not_called()
        mock_logger.error.assert_not_called()
    
    @patch('infrastructure.processamento.ml_processor.logger')
    def test_aplicar_sugestoes_with_error(self, mock_logger, ml_processor, mock_ml_adaptativo):
        """Testa aplicação de sugestões com erro"""
        keywords_dict = [{"termo": "teste", "volume_busca": 1000}]
        mock_ml_adaptativo.sugerir.side_effect = Exception("Erro nas sugestões")
        
        result = ml_processor._aplicar_sugestoes(keywords_dict, {})
        
        assert result == keywords_dict
        mock_logger.error.assert_called_once()
    
    @patch('infrastructure.processamento.ml_processor.logger')
    def test_aplicar_bloqueio_success(self, mock_logger, ml_processor, mock_ml_adaptativo):
        """Testa aplicação de bloqueio bem-sucedida"""
        keywords_dict = [
            {"termo": "teste1", "volume_busca": 1000},
            {"termo": "teste2", "volume_busca": 500}
        ]
        historico_feedback = [{"keyword": "teste1", "score": 85}]
        
        filtrados = [{"termo": "teste2", "volume_busca": 500}]
        mock_ml_adaptativo.bloquear_repetidos.return_value = filtrados
        
        result = ml_processor._aplicar_bloqueio(keywords_dict, historico_feedback)
        
        assert result == filtrados
        assert ml_processor._ultimos_resultados["filtrados"] == 1
        assert ml_processor._ultimos_resultados["bloqueados"] == 1
        mock_logger.info.assert_called_once()
    
    @patch('infrastructure.processamento.ml_processor.logger')
    def test_aplicar_bloqueio_without_ml(self, mock_logger):
        """Testa aplicação de bloqueio sem ML adaptativo"""
        processor = MLProcessor(ml_adaptativo=None)
        keywords_dict = [{"termo": "teste", "volume_busca": 1000}]
        
        result = processor._aplicar_bloqueio(keywords_dict, [])
        
        assert result == keywords_dict
        mock_logger.info.assert_not_called()
        mock_logger.error.assert_not_called()
    
    @patch('infrastructure.processamento.ml_processor.logger')
    def test_aplicar_bloqueio_with_error(self, mock_logger, ml_processor, mock_ml_adaptativo):
        """Testa aplicação de bloqueio com erro"""
        keywords_dict = [{"termo": "teste", "volume_busca": 1000}]
        mock_ml_adaptativo.bloquear_repetidos.side_effect = Exception("Erro no bloqueio")
        
        result = ml_processor._aplicar_bloqueio(keywords_dict, [])
        
        assert result == keywords_dict
        mock_logger.error.assert_called_once()
    
    @patch('infrastructure.processamento.ml_processor.logger')
    def test_log_processamento(self, mock_logger, ml_processor, sample_keywords):
        """Testa logging de processamento"""
        keywords_processadas = sample_keywords.copy()
        contexto = {"dominio": "ecommerce"}
        
        ml_processor._log_processamento(sample_keywords, keywords_processadas, contexto)
        
        mock_logger.info.assert_called_once()
        log_call = mock_logger.info.call_args[0][0]
        assert log_call["event"] == "processamento_ml_completo"
        assert log_call["status"] == "success"
        assert log_call["details"]["total_entrada"] == 2
        assert log_call["details"]["total_saida"] == 2
    
    def test_obter_estatisticas(self, ml_processor, mock_ml_adaptativo):
        """Testa obtenção de estatísticas"""
        # Simular alguns resultados
        ml_processor._ultimos_resultados = {
            "sugeridos": 5,
            "filtrados": 3,
            "bloqueados": 2
        }
        
        stats = ml_processor.obter_estatisticas()
        
        assert stats["ml_adaptativo_disponivel"] is True
        assert stats["sugestoes_habilitadas"] is True
        assert stats["bloqueio_habilitado"] is True
        assert stats["treinamento_habilitado"] is True
        assert stats["ultimos_resultados"]["sugeridos"] == 5
        assert stats["versao_ml"] == "1.0.0"
    
    def test_obter_estatisticas_without_ml(self):
        """Testa obtenção de estatísticas sem ML adaptativo"""
        processor = MLProcessor(ml_adaptativo=None)
        
        stats = processor.obter_estatisticas()
        
        assert stats["ml_adaptativo_disponivel"] is False
        assert stats["versao_ml"] == "N/A"
    
    @patch('infrastructure.processamento.ml_processor.logger')
    def test_atualizar_configuracao_success(self, mock_logger, ml_processor):
        """Testa atualização de configuração bem-sucedida"""
        result = ml_processor.atualizar_configuracao(
            habilitar_sugestoes=False,
            habilitar_bloqueio=False,
            habilitar_treinamento=False
        )
        
        assert result is True
        assert ml_processor.habilitar_sugestoes is False
        assert ml_processor.habilitar_bloqueio is False
        assert ml_processor.habilitar_treinamento is False
        mock_logger.info.assert_called_once()
    
    @patch('infrastructure.processamento.ml_processor.logger')
    def test_atualizar_configuracao_partial(self, mock_logger, ml_processor):
        """Testa atualização parcial de configuração"""
        original_sugestoes = ml_processor.habilitar_sugestoes
        original_bloqueio = ml_processor.habilitar_bloqueio
        
        result = ml_processor.atualizar_configuracao(habilitar_treinamento=False)
        
        assert result is True
        assert ml_processor.habilitar_sugestoes == original_sugestoes
        assert ml_processor.habilitar_bloqueio == original_bloqueio
        assert ml_processor.habilitar_treinamento is False
        mock_logger.info.assert_called_once()
    
    @patch('infrastructure.processamento.ml_processor.logger')
    def test_atualizar_configuracao_with_error(self, mock_logger, ml_processor):
        """Testa atualização de configuração com erro"""
        # Simular erro ao acessar atributo
        with patch.object(ml_processor, 'habilitar_sugestoes', side_effect=Exception("Erro")):
            result = ml_processor.atualizar_configuracao(habilitar_sugestoes=False)
            
            assert result is False
            mock_logger.error.assert_called_once()


class TestMLProcessorIntegration:
    """Testes de integração para MLProcessor"""
    
    @pytest.fixture
    def mock_ml_adaptativo(self):
        """Mock do MLAdaptativo para testes"""
        mock = Mock()
        mock.versao = "1.0.0"
        mock.data_treinamento = datetime.now().isoformat()
        return mock
    
    @pytest.fixture
    def sample_keywords(self):
        """Keywords de exemplo para testes"""
        return [
            Keyword(
                termo="palavra chave teste",
                volume_busca=1000,
                cpc=1.50,
                concorrencia=0.7,
                intencao=IntencaoBusca.INFORMACIONAL,
                score=85.5,
                justificativa="Teste de keyword",
                fonte="google_ads",
                data_coleta=datetime.now()
            )
        ]
    
    @pytest.fixture
    def ml_processor(self, mock_ml_adaptativo):
        """Instância do MLProcessor para testes"""
        return MLProcessor(ml_adaptativo=mock_ml_adaptativo)
    
    def test_complete_processing_workflow(self, ml_processor, sample_keywords, mock_ml_adaptativo):
        """Testa workflow completo de processamento"""
        # Configurar mocks
        mock_ml_adaptativo.sugerir.return_value = [
            {
                "termo": "palavra chave otimizada",
                "volume_busca": 1200,
                "cpc": 1.75,
                "concorrencia": 0.6,
                "intencao": "informacional",
                "score": 90.0,
                "justificativa": "Otimizada pelo ML",
                "fonte": "ml_suggestion",
                "data_coleta": datetime.now().isoformat()
            }
        ]
        mock_ml_adaptativo.bloquear_repetidos.return_value = mock_ml_adaptativo.sugerir.return_value
        
        historico_feedback = [{"keyword": "teste", "score": 85, "feedback": "positive"}]
        contexto = {"dominio": "ecommerce", "categoria": "eletronicos"}
        
        # Executar processamento completo
        result = ml_processor.processar_keywords(sample_keywords, historico_feedback, contexto)
        
        # Verificar resultado
        assert len(result) == 1
        assert result[0].termo == "palavra chave otimizada"
        assert result[0].score == 90.0
        
        # Verificar se todos os métodos foram chamados
        mock_ml_adaptativo.treinar_incremental.assert_called_once_with(historico_feedback)
        mock_ml_adaptativo.sugerir.assert_called_once()
        mock_ml_adaptativo.bloquear_repetidos.assert_called_once()
        
        # Verificar estatísticas
        stats = ml_processor.obter_estatisticas()
        assert stats["ml_adaptativo_disponivel"] is True
        assert stats["ultimos_resultados"]["sugeridos"] == 1
        assert stats["ultimos_resultados"]["filtrados"] == 1
        assert stats["ultimos_resultados"]["bloqueados"] == 0


class TestMLProcessorErrorHandling:
    """Testes de tratamento de erros para MLProcessor"""
    
    @pytest.fixture
    def mock_ml_adaptativo(self):
        """Mock do MLAdaptativo para testes"""
        mock = Mock()
        mock.versao = "1.0.0"
        mock.data_treinamento = datetime.now().isoformat()
        return mock
    
    @pytest.fixture
    def sample_keywords(self):
        """Keywords de exemplo para testes"""
        return [
            Keyword(
                termo="palavra chave teste",
                volume_busca=1000,
                cpc=1.50,
                concorrencia=0.7,
                intencao=IntencaoBusca.INFORMACIONAL,
                score=85.5,
                justificativa="Teste de keyword",
                fonte="google_ads",
                data_coleta=datetime.now()
            )
        ]
    
    @pytest.fixture
    def ml_processor(self, mock_ml_adaptativo):
        """Instância do MLProcessor para testes"""
        return MLProcessor(ml_adaptativo=mock_ml_adaptativo)
    
    def test_processing_with_ml_errors(self, ml_processor, sample_keywords, mock_ml_adaptativo):
        """Testa processamento com erros no ML"""
        # Configurar erros em diferentes métodos
        mock_ml_adaptativo.sugerir.side_effect = Exception("Erro nas sugestões")
        mock_ml_adaptativo.bloquear_repetidos.side_effect = Exception("Erro no bloqueio")
        mock_ml_adaptativo.treinar_incremental.side_effect = Exception("Erro no treinamento")
        
        # Processamento deve continuar mesmo com erros
        result = ml_processor.processar_keywords(sample_keywords)
        
        # Deve retornar keywords originais
        assert result == sample_keywords
    
    def test_processing_with_invalid_data(self, ml_processor, mock_ml_adaptativo):
        """Testa processamento com dados inválidos"""
        # Keywords com dados inválidos
        invalid_keywords = [
            Keyword(
                termo="",  # termo vazio
                volume_busca=-100,  # volume negativo
                cpc=-1.0,  # CPC negativo
                concorrencia=1.5,  # concorrência > 1
                intencao=IntencaoBusca.INFORMACIONAL,
                score=150.0,  # score > 100
                justificativa="",
                fonte="",
                data_coleta=None  # data None
            )
        ]
        
        # Processamento deve funcionar mesmo com dados inválidos
        result = ml_processor.processar_keywords(invalid_keywords)
        
        # Deve retornar keywords (mesmo que inválidas)
        assert len(result) == 1


class TestMLProcessorPerformance:
    """Testes de performance para MLProcessor"""
    
    @pytest.fixture
    def mock_ml_adaptativo(self):
        """Mock do MLAdaptativo para testes"""
        mock = Mock()
        mock.versao = "1.0.0"
        mock.data_treinamento = datetime.now().isoformat()
        return mock
    
    @pytest.fixture
    def ml_processor(self, mock_ml_adaptativo):
        """Instância do MLProcessor para testes"""
        return MLProcessor(ml_adaptativo=mock_ml_adaptativo)
    
    def test_large_keywords_processing(self, ml_processor, mock_ml_adaptativo):
        """Testa processamento de grande volume de keywords"""
        import time
        
        # Criar grande volume de keywords
        large_keywords = []
        for i in range(1000):
            large_keywords.append(Keyword(
                termo=f"keyword_{i}",
                volume_busca=100 + i,
                cpc=1.0 + (i / 1000),
                concorrencia=0.5 + (i / 2000),
                intencao=IntencaoBusca.INFORMACIONAL,
                score=80.0 + (i / 100),
                justificativa=f"Keyword {i}",
                fonte="test",
                data_coleta=datetime.now()
            ))
        
        # Configurar mock para retornar keywords processadas
        mock_ml_adaptativo.sugerir.return_value = [
            {
                "termo": f"keyword_{i}_otimizada",
                "volume_busca": 100 + i,
                "cpc": 1.0 + (i / 1000),
                "concorrencia": 0.5 + (i / 2000),
                "intencao": "informacional",
                "score": 85.0 + (i / 100),
                "justificativa": f"Otimizada {i}",
                "fonte": "ml_suggestion",
                "data_coleta": datetime.now().isoformat()
            }
            for i in range(1000)
        ]
        mock_ml_adaptativo.bloquear_repetidos.return_value = mock_ml_adaptativo.sugerir.return_value
        
        start_time = time.time()
        
        result = ml_processor.processar_keywords(large_keywords)
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        processing_time = end_time - start_time
        assert processing_time < 10.0  # Menos de 10 segundos para 1000 keywords
        
        # Verificar resultado
        assert len(result) == 1000
        assert all(kw.termo.endswith("_otimizada") for kw in result)


if __name__ == "__main__":
    pytest.main([__file__]) 
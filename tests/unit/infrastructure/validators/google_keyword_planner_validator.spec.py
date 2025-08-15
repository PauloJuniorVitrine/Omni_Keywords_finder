"""
Testes Unitários: Google Keyword Planner Validator
Testa funcionalidades do validador Google Keyword Planner

Prompt: Google Keyword Planner como Validador
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-20
Versão: 1.0.0
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List

from domain.models import Keyword, IntencaoBusca
from infrastructure.validacao.google_keyword_planner_validator import GoogleKeywordPlannerValidator
from infrastructure.validacao.validador_avancado import ValidadorAvancado

class TestGoogleKeywordPlannerValidator:
    """Testes para GoogleKeywordPlannerValidator."""
    
    @pytest.fixture
    def config_validador(self):
        """Configuração de teste para o validador."""
        return {
            "enabled": True,
            "api_enabled": True,
            "scraping_enabled": True,
            "cache_enabled": True,
            "rate_limiting_enabled": True,
            "cache_ttl": 3600,
            "rate_limit_delay": 1.0,
            "max_keywords_per_request": 10,
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
            "customer_id": "123-456-7890",
            "min_search_volume": 100,
            "max_cpc": 5.0,
            "reject_high_competition": True
        }
    
    @pytest.fixture
    def validador(self, config_validador):
        """Instância do validador para testes."""
        with patch('infrastructure.validacao.google_keyword_planner_validator.CacheManager'):
            return GoogleKeywordPlannerValidator(config_validador)
    
    @pytest.fixture
    def keywords_teste(self):
        """Keywords de teste."""
        return [
            Keyword(
                termo="marketing digital",
                volume_busca=1000,
                cpc=2.5,
                concorrencia=0.7,
                intencao=IntencaoBusca.COMERCIAL,
                fonte="teste"
            ),
            Keyword(
                termo="curso python",
                volume_busca=5000,
                cpc=1.8,
                concorrencia=0.6,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="teste"
            ),
            Keyword(
                termo="receita bolo",
                volume_busca=50,  # Volume baixo
                cpc=0.5,
                concorrencia=0.3,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="teste"
            )
        ]
    
    def test_inicializacao_validador(self, config_validador):
        """Testa inicialização do validador."""
        with patch('infrastructure.validacao.google_keyword_planner_validator.CacheManager'):
            validador = GoogleKeywordPlannerValidator(config_validador)
            
            assert validador.nome == "GoogleKeywordPlanner"
            assert validador.enabled is True
            assert validador.api_enabled is True
            assert validador.scraping_enabled is True
            assert validador.cache_enabled is True
            assert validador.rate_limiting_enabled is True
    
    def test_get_prioridade(self, validador):
        """Testa retorno da prioridade."""
        assert validador.get_prioridade() == 1
    
    def test_is_enabled(self, validador):
        """Testa verificação se validador está habilitado."""
        assert validador.is_enabled() is True
        
        # Testar com validador desabilitado
        config_desabilitado = {"enabled": False}
        validador_desabilitado = GoogleKeywordPlannerValidator(config_desabilitado)
        assert validador_desabilitado.is_enabled() is False
    
    @patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator._obter_metricas_da_fonte')
    def test_obter_metricas_sucesso(self, mock_obter_metricas, validador):
        """Testa obtenção de métricas com sucesso."""
        metricas_mock = {
            "search_volume": 1000,
            "competition": "MEDIUM",
            "cpc": 2.5,
            "competition_index": 50,
            "source": "google_ads_api"
        }
        mock_obter_metricas.return_value = metricas_mock
        
        # Mock cache
        validador.cache.get.return_value = None
        validador.cache.set.return_value = True
        
        resultado = validador.obter_metricas("marketing digital")
        
        assert resultado == metricas_mock
        validador.cache.get.assert_called_once()
        validador.cache.set.assert_called_once()
    
    @patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator._obter_metricas_da_fonte')
    def test_obter_metricas_cache_hit(self, mock_obter_metricas, validador):
        """Testa obtenção de métricas do cache."""
        metricas_cache = {
            "search_volume": 1000,
            "competition": "MEDIUM",
            "cpc": 2.5
        }
        
        # Mock cache hit
        validador.cache.get.return_value = metricas_cache
        
        resultado = validador.obter_metricas("marketing digital")
        
        assert resultado == metricas_cache
        mock_obter_metricas.assert_not_called()  # Não deve chamar fonte
    
    @patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator._obter_metricas_da_fonte')
    def test_obter_metricas_falha(self, mock_obter_metricas, validador):
        """Testa obtenção de métricas com falha."""
        mock_obter_metricas.return_value = None
        
        # Mock cache
        validador.cache.get.return_value = None
        
        resultado = validador.obter_metricas("keyword inexistente")
        
        assert resultado == {}
    
    @patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator.obter_metricas')
    def test_validar_keywords_sucesso(self, mock_obter_metricas, validador, keywords_teste):
        """Testa validação de keywords com sucesso."""
        # Mock métricas para cada keyword
        metricas_mock = {
            "search_volume": 1000,
            "competition": "MEDIUM",
            "cpc": 2.5
        }
        mock_obter_metricas.return_value = metricas_mock
        
        resultado = validador.validar_keywords(keywords_teste)
        
        # Deve aprovar apenas as keywords que atendem aos critérios
        assert len(resultado) == 2  # marketing digital e curso python
        assert "marketing digital" in [kw.termo for kw in resultado]
        assert "curso python" in [kw.termo for kw in resultado]
        assert "receita bolo" not in [kw.termo for kw in resultado]  # Volume baixo
    
    @patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator.obter_metricas')
    def test_validar_keywords_competicao_alta(self, mock_obter_metricas, validador, keywords_teste):
        """Testa validação rejeitando competição alta."""
        # Mock métricas com competição alta
        metricas_competicao_alta = {
            "search_volume": 1000,
            "competition": "HIGH",
            "cpc": 2.5
        }
        mock_obter_metricas.return_value = metricas_competicao_alta
        
        resultado = validador.validar_keywords(keywords_teste)
        
        # Deve rejeitar todas por competição alta
        assert len(resultado) == 0
    
    @patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator.obter_metricas')
    def test_validar_keywords_cpc_alto(self, mock_obter_metricas, validador, keywords_teste):
        """Testa validação rejeitando CPC alto."""
        # Mock métricas com CPC alto
        metricas_cpc_alto = {
            "search_volume": 1000,
            "competition": "MEDIUM",
            "cpc": 10.0  # Acima do limite de 5.0
        }
        mock_obter_metricas.return_value = metricas_cpc_alto
        
        resultado = validador.validar_keywords(keywords_teste)
        
        # Deve rejeitar todas por CPC alto
        assert len(resultado) == 0
    
    def test_aplicar_criterios_validacao(self, validador):
        """Testa aplicação de critérios de validação."""
        keyword = Keyword(
            termo="teste",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="teste"
        )
        
        # Teste com métricas válidas
        metricas_validas = {
            "search_volume": 1000,
            "competition": "MEDIUM",
            "cpc": 2.5
        }
        
        resultado = validador._aplicar_criterios_validacao(keyword, metricas_validas)
        assert resultado is True
        
        # Teste com volume baixo
        metricas_volume_baixo = {
            "search_volume": 50,
            "competition": "MEDIUM",
            "cpc": 2.5
        }
        
        resultado = validador._aplicar_criterios_validacao(keyword, metricas_volume_baixo)
        assert resultado is False
    
    def test_get_estatisticas(self, validador):
        """Testa obtenção de estatísticas."""
        # Simular algumas execuções
        validador.total_validated = 10
        validador.total_rejected = 5
        validador.execution_time = 30.5
        validador.last_execution = datetime.utcnow()
        
        estatisticas = validador.get_estatisticas()
        
        assert estatisticas["nome"] == "GoogleKeywordPlanner"
        assert estatisticas["total_validated"] == 10
        assert estatisticas["total_rejected"] == 5
        assert estatisticas["execution_time"] == 30.5
        assert estatisticas["taxa_rejeicao"] == 0.333  # 5/(10+5)
    
    def test_reset_estatisticas(self, validador):
        """Testa reset de estatísticas."""
        # Simular estatísticas
        validador.total_validated = 10
        validador.total_rejected = 5
        validador.execution_time = 30.5
        validador.last_execution = datetime.utcnow()
        
        validador.reset_estatisticas()
        
        assert validador.total_validated == 0
        assert validador.total_rejected == 0
        assert validador.execution_time == 0.0
        assert validador.last_execution is None

class TestValidadorAvancado:
    """Testes para ValidadorAvancado."""
    
    @pytest.fixture
    def config_validador_avancado(self):
        """Configuração de teste para o validador avançado."""
        return {
            "estrategia_padrao": "cascata",
            "timeout_segundos": 300,
            "max_retries": 3,
            "google_keyword_planner": {
                "enabled": True,
                "api_enabled": True,
                "scraping_enabled": True,
                "cache_enabled": True,
                "rate_limiting_enabled": True
            }
        }
    
    @pytest.fixture
    def validador_avancado(self, config_validador_avancado):
        """Instância do validador avançado para testes."""
        with patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator'):
            return ValidadorAvancado(config_validador_avancado)
    
    @pytest.fixture
    def keywords_teste(self):
        """Keywords de teste."""
        return [
            Keyword(
                termo="marketing digital",
                volume_busca=1000,
                cpc=2.5,
                concorrencia=0.7,
                intencao=IntencaoBusca.COMERCIAL,
                fonte="teste"
            ),
            Keyword(
                termo="curso python",
                volume_busca=5000,
                cpc=1.8,
                concorrencia=0.6,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="teste"
            )
        ]
    
    def test_inicializacao_validador_avancado(self, config_validador_avancado):
        """Testa inicialização do validador avançado."""
        with patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator'):
            validador = ValidadorAvancado(config_validador_avancado)
            
            assert len(validador.validadores) > 0
            assert validador.execution_stats["total_executions"] == 0
    
    @patch('infrastructure.validacao.validador_avancado.ValidadorAvancado._validacao_cascata')
    def test_validar_keywords_cascata(self, mock_cascata, validador_avancado, keywords_teste):
        """Testa validação em cascata."""
        mock_cascata.return_value = keywords_teste[:1]  # Retorna apenas a primeira
        
        resultado = validador_avancado.validar_keywords(keywords_teste, estrategia="cascata")
        
        assert len(resultado) == 1
        assert resultado[0].termo == "marketing digital"
        mock_cascata.assert_called_once_with(keywords_teste)
    
    @patch('infrastructure.validacao.validador_avancado.ValidadorAvancado._validacao_paralela')
    def test_validar_keywords_paralela(self, mock_paralela, validador_avancado, keywords_teste):
        """Testa validação paralela."""
        mock_paralela.return_value = keywords_teste  # Retorna todas
        
        resultado = validador_avancado.validar_keywords(keywords_teste, estrategia="paralela")
        
        assert len(resultado) == 2
        mock_paralela.assert_called_once_with(keywords_teste)
    
    @patch('infrastructure.validacao.validador_avancado.ValidadorAvancado._validacao_consenso')
    def test_validar_keywords_consenso(self, mock_consenso, validador_avancado, keywords_teste):
        """Testa validação por consenso."""
        mock_consenso.return_value = keywords_teste[:1]  # Retorna apenas a primeira
        
        resultado = validador_avancado.validar_keywords(keywords_teste, estrategia="consenso")
        
        assert len(resultado) == 1
        mock_consenso.assert_called_once_with(keywords_teste)
    
    def test_validar_keywords_estrategia_invalida(self, validador_avancado, keywords_teste):
        """Testa validação com estratégia inválida."""
        with pytest.raises(ValueError, match="Estratégia 'invalida' não suportada"):
            validador_avancado.validar_keywords(keywords_teste, estrategia="invalida")
    
    def test_get_estatisticas(self, validador_avancado):
        """Testa obtenção de estatísticas do validador avançado."""
        # Simular algumas execuções
        validador_avancado.execution_stats.update({
            "total_executions": 5,
            "total_keywords_processed": 100,
            "total_keywords_approved": 80,
            "total_execution_time": 150.0
        })
        
        estatisticas = validador_avancado.get_estatisticas()
        
        assert estatisticas["validador_avancado"]["total_executions"] == 5
        assert estatisticas["validador_avancado"]["total_keywords_processed"] == 100
        assert estatisticas["validador_avancado"]["total_keywords_approved"] == 80
        assert estatisticas["validador_avancado"]["overall_approval_rate"] == 0.8
    
    def test_reset_estatisticas(self, validador_avancado):
        """Testa reset de estatísticas do validador avançado."""
        # Simular estatísticas
        validador_avancado.execution_stats.update({
            "total_executions": 5,
            "total_keywords_processed": 100,
            "total_keywords_approved": 80,
            "total_execution_time": 150.0
        })
        
        validador_avancado.reset_estatisticas()
        
        assert validador_avancado.execution_stats["total_executions"] == 0
        assert validador_avancado.execution_stats["total_keywords_processed"] == 0
        assert validador_avancado.execution_stats["total_keywords_approved"] == 0
        assert validador_avancado.execution_stats["total_execution_time"] == 0.0

class TestIntegracaoProcessador:
    """Testes de integração com o processador."""
    
    @pytest.fixture
    def config_processador(self):
        """Configuração de teste para o processador."""
        return {
            "validacao": {
                "estrategia_padrao": "cascata",
                "google_keyword_planner": {
                    "enabled": True,
                    "api_enabled": True,
                    "scraping_enabled": True,
                    "cache_enabled": True,
                    "rate_limiting_enabled": True
                }
            }
        }
    
    @pytest.fixture
    def keywords_teste(self):
        """Keywords de teste."""
        return [
            Keyword(
                termo="marketing digital",
                volume_busca=1000,
                cpc=2.5,
                concorrencia=0.7,
                intencao=IntencaoBusca.COMERCIAL,
                fonte="teste"
            ),
            Keyword(
                termo="curso python",
                volume_busca=5000,
                cpc=1.8,
                concorrencia=0.6,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="teste"
            )
        ]
    
    @patch('infrastructure.processamento.processador_keywords.ValidadorAvancado')
    def test_processador_com_validador_avancado(self, mock_validador_avancado, config_processador, keywords_teste):
        """Testa integração do processador com validador avançado."""
        from infrastructure.processamento.processador_keywords import ProcessadorKeywords
        
        # Mock do validador avançado
        mock_validador = Mock()
        mock_validador.validar_keywords.return_value = keywords_teste[:1]
        mock_validador.get_estatisticas.return_value = {"validador_avancado": {"total_executions": 1}}
        mock_validador_avancado.return_value = mock_validador
        
        # Criar processador
        processador = ProcessadorKeywords(config=config_processador)
        
        # Processar keywords
        resultado = processador.processar_keywords(keywords_teste, estrategia_validacao="cascata")
        
        # Verificar resultados
        assert len(resultado) == 1
        assert resultado[0].termo == "marketing digital"
        
        # Verificar que validador foi chamado
        mock_validador.validar_keywords.assert_called_once()
        
        # Verificar métricas
        metricas = processador.get_metricas_completas()
        assert metricas["processador"]["total_execucoes"] == 1
        assert metricas["processador"]["total_keywords_processadas"] == 2
        assert metricas["processador"]["total_keywords_aprovadas"] == 1

if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 
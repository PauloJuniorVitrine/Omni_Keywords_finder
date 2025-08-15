"""
Testes Unitários: Google Keyword Planner Validator
Testa funcionalidades do validador Google Keyword Planner

Prompt: Melhorar testes unitários Fase 2
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 2.0.0
Tracing ID: TEST_GOOGLE_VALIDATOR_002_20241227
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio

from domain.models import Keyword, IntencaoBusca
from infrastructure.validacao.google_keyword_planner_validator import GoogleKeywordPlannerValidator
from infrastructure.validacao.validador_avancado import ValidadorAvancado


class TestGoogleKeywordPlannerValidator:
    """Testes para GoogleKeywordPlannerValidator baseados no código real."""
    
    @pytest.fixture
    def config_validador_real(self):
        """Configuração real baseada no arquivo de configuração."""
        return {
            "enabled": True,
            "api_enabled": True,
            "scraping_enabled": True,
            "cache_enabled": True,
            "rate_limiting_enabled": True,
            "cache_ttl": 86400,  # 24 horas
            "rate_limit_delay": 2.0,
            "max_keywords_per_request": 100,
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
            "customer_id": "123-456-7890",
            "min_search_volume": 100,
            "max_cpc": 5.0,
            "reject_high_competition": True,
            "min_competition_index": 0,
            "max_competition_index": 100,
            "headless": True,
            "timeout_segundos": 30,
            "window_size": "1920,1080"
        }
    
    @pytest.fixture
    def validador_real(self, config_validador_real):
        """Instância do validador com configuração real."""
        with patch('infrastructure.validacao.google_keyword_planner_validator.CacheManager'), \
             patch('infrastructure.validacao.google_keyword_planner_validator.GoogleAdsService'), \
             patch('infrastructure.validacao.google_keyword_planner_validator.webdriver'):
            return GoogleKeywordPlannerValidator(config_validador_real)
    
    @pytest.fixture
    def keywords_reais(self):
        """Keywords baseadas em dados reais do projeto."""
        return [
            Keyword(
                termo="marketing digital",
                volume_busca=1000,
                cpc=2.5,
                concorrencia=0.7,
                intencao=IntencaoBusca.COMERCIAL,
                fonte="google_keyword_planner",
                score=0.85,
                justificativa="Volume alto, CPC moderado"
            ),
            Keyword(
                termo="curso python online",
                volume_busca=5000,
                cpc=1.8,
                concorrencia=0.6,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="google_keyword_planner",
                score=0.92,
                justificativa="Volume muito alto, baixa competição"
            ),
            Keyword(
                termo="receita bolo chocolate",
                volume_busca=50,  # Volume baixo
                cpc=0.5,
                concorrencia=0.3,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="google_keyword_planner",
                score=0.45,
                justificativa="Volume muito baixo"
            ),
            Keyword(
                termo="seguro auto",
                volume_busca=2000,
                cpc=8.0,  # CPC alto
                concorrencia=0.9,
                intencao=IntencaoBusca.COMERCIAL,
                fonte="google_keyword_planner",
                score=0.35,
                justificativa="CPC muito alto, competição alta"
            )
        ]
    
    def test_inicializacao_configuracao_real(self, config_validador_real):
        """Testa inicialização com configuração real do projeto."""
        with patch('infrastructure.validacao.google_keyword_planner_validator.CacheManager'), \
             patch('infrastructure.validacao.google_keyword_planner_validator.GoogleAdsService'), \
             patch('infrastructure.validacao.google_keyword_planner_validator.webdriver'):
            
            validador = GoogleKeywordPlannerValidator(config_validador_real)
            
            # Verificar configurações específicas do projeto
            assert validador.nome == "GoogleKeywordPlanner"
            assert validador.enabled is True
            assert validador.api_enabled is True
            assert validador.scraping_enabled is True
            assert validador.cache_enabled is True
            assert validador.rate_limiting_enabled is True
            assert validador.cache_ttl == 86400
            assert validador.rate_limit_delay == 2.0
            assert validador.max_keywords_per_request == 100
            assert validador.min_search_volume == 100
            assert validador.max_cpc == 5.0
            assert validador.reject_high_competition is True
    
    def test_get_prioridade_validador(self, validador_real):
        """Testa retorno da prioridade do validador."""
        assert validador_real.get_prioridade() == 1
    
    def test_is_enabled_configuracoes_variadas(self, config_validador_real):
        """Testa verificação de habilitação com diferentes configurações."""
        # Testar com validador habilitado
        with patch('infrastructure.validacao.google_keyword_planner_validator.CacheManager'), \
             patch('infrastructure.validacao.google_keyword_planner_validator.GoogleAdsService'), \
             patch('infrastructure.validacao.google_keyword_planner_validator.webdriver'):
            validador = GoogleKeywordPlannerValidator(config_validador_real)
            assert validador.is_enabled() is True
        
        # Testar com validador desabilitado
        config_desabilitado = config_validador_real.copy()
        config_desabilitado["enabled"] = False
        
        with patch('infrastructure.validacao.google_keyword_planner_validator.CacheManager'), \
             patch('infrastructure.validacao.google_keyword_planner_validator.GoogleAdsService'), \
             patch('infrastructure.validacao.google_keyword_planner_validator.webdriver'):
            validador_desabilitado = GoogleKeywordPlannerValidator(config_desabilitado)
            assert validador_desabilitado.is_enabled() is False
    
    @patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator._obter_metricas_da_fonte')
    def test_obter_metricas_sucesso_api(self, mock_obter_metricas, validador_real):
        """Testa obtenção de métricas via API com sucesso."""
        metricas_mock = {
            "search_volume": 1000,
            "competition": "MEDIUM",
            "cpc": 2.5,
            "competition_index": 50,
            "source": "google_ads_api",
            "last_updated": datetime.utcnow().isoformat(),
            "low_top_of_page_bid": 1.5,
            "high_top_of_page_bid": 3.5,
            "suggested_bid": 2.5
        }
        mock_obter_metricas.return_value = metricas_mock
        
        # Mock cache miss
        validador_real.cache.get.return_value = None
        validador_real.cache.set.return_value = True
        
        resultado = validador_real.obter_metricas("marketing digital")
        
        assert resultado == metricas_mock
        validador_real.cache.get.assert_called_once_with("marketing digital")
        validador_real.cache.set.assert_called_once_with("marketing digital", metricas_mock, 86400)
    
    @patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator._obter_metricas_da_fonte')
    def test_obter_metricas_cache_hit(self, mock_obter_metricas, validador_real):
        """Testa obtenção de métricas do cache."""
        metricas_cache = {
            "search_volume": 1000,
            "competition": "MEDIUM",
            "cpc": 2.5,
            "competition_index": 50,
            "source": "cache",
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Mock cache hit
        validador_real.cache.get.return_value = metricas_cache
        
        resultado = validador_real.obter_metricas("marketing digital")
        
        assert resultado == metricas_cache
        mock_obter_metricas.assert_not_called()  # Não deve chamar fonte
    
    @patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator._obter_metricas_da_fonte')
    def test_obter_metricas_falha_api_fallback_scraping(self, mock_obter_metricas, validador_real):
        """Testa fallback para scraping quando API falha."""
        # Primeira chamada falha (API), segunda sucesso (scraping)
        mock_obter_metricas.side_effect = [
            None,  # API falha
            {     # Scraping sucesso
                "search_volume": 800,
                "competition": "LOW",
                "cpc": 1.8,
                "competition_index": 30,
                "source": "web_scraping",
                "last_updated": datetime.utcnow().isoformat()
            }
        ]
        
        # Mock cache
        validador_real.cache.get.return_value = None
        validador_real.cache.set.return_value = True
        
        resultado = validador_real.obter_metricas("keyword teste")
        
        assert resultado["source"] == "web_scraping"
        assert resultado["search_volume"] == 800
        assert mock_obter_metricas.call_count == 2
    
    @patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator.obter_metricas')
    def test_validar_keywords_criterios_reais(self, mock_obter_metricas, validador_real, keywords_reais):
        """Testa validação com critérios reais do projeto."""
        # Mock métricas variadas para cada keyword
        metricas_variadas = [
            {"search_volume": 1000, "competition": "MEDIUM", "cpc": 2.5, "competition_index": 50},  # marketing digital
            {"search_volume": 5000, "competition": "LOW", "cpc": 1.8, "competition_index": 30},     # curso python
            {"search_volume": 50, "competition": "LOW", "cpc": 0.5, "competition_index": 20},       # receita bolo
            {"search_volume": 2000, "competition": "HIGH", "cpc": 8.0, "competition_index": 85}     # seguro auto
        ]
        
        mock_obter_metricas.side_effect = metricas_variadas
        
        resultado = validador_real.validar_keywords(keywords_reais)
        
        # Deve aprovar apenas marketing digital e curso python
        assert len(resultado) == 2
        termos_aprovados = [kw.termo for kw in resultado]
        assert "marketing digital" in termos_aprovados
        assert "curso python online" in termos_aprovados
        assert "receita bolo chocolate" not in termos_aprovados  # Volume baixo
        assert "seguro auto" not in termos_aprovados  # CPC alto + competição alta
    
    @patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator.obter_metricas')
    def test_validar_keywords_competicao_alta_rejeicao(self, mock_obter_metricas, validador_real, keywords_reais):
        """Testa rejeição por competição alta."""
        metricas_competicao_alta = {
            "search_volume": 1000,
            "competition": "HIGH",
            "cpc": 2.5,
            "competition_index": 85
        }
        mock_obter_metricas.return_value = metricas_competicao_alta
        
        resultado = validador_real.validar_keywords(keywords_reais)
        
        # Deve rejeitar todas por competição alta
        assert len(resultado) == 0
    
    @patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator.obter_metricas')
    def test_validar_keywords_cpc_alto_rejeicao(self, mock_obter_metricas, validador_real, keywords_reais):
        """Testa rejeição por CPC alto."""
        metricas_cpc_alto = {
            "search_volume": 1000,
            "competition": "MEDIUM",
            "cpc": 10.0,  # Acima do limite de 5.0
            "competition_index": 50
        }
        mock_obter_metricas.return_value = metricas_cpc_alto
        
        resultado = validador_real.validar_keywords(keywords_reais)
        
        # Deve rejeitar todas por CPC alto
        assert len(resultado) == 0
    
    def test_aplicar_criterios_validacao_cenarios_reais(self, validador_real):
        """Testa aplicação de critérios com cenários reais."""
        keyword = Keyword(
            termo="teste",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="teste"
        )
        
        # Cenário 1: Métricas válidas
        metricas_validas = {
            "search_volume": 1000,
            "competition": "MEDIUM",
            "cpc": 2.5,
            "competition_index": 50
        }
        assert validador_real._aplicar_criterios_validacao(keyword, metricas_validas) is True
        
        # Cenário 2: Volume baixo
        metricas_volume_baixo = {
            "search_volume": 50,
            "competition": "MEDIUM",
            "cpc": 2.5,
            "competition_index": 50
        }
        assert validador_real._aplicar_criterios_validacao(keyword, metricas_volume_baixo) is False
        
        # Cenário 3: CPC alto
        metricas_cpc_alto = {
            "search_volume": 1000,
            "competition": "MEDIUM",
            "cpc": 10.0,
            "competition_index": 50
        }
        assert validador_real._aplicar_criterios_validacao(keyword, metricas_cpc_alto) is False
        
        # Cenário 4: Competição alta
        metricas_competicao_alta = {
            "search_volume": 1000,
            "competition": "HIGH",
            "cpc": 2.5,
            "competition_index": 85
        }
        assert validador_real._aplicar_criterios_validacao(keyword, metricas_competicao_alta) is False
        
        # Cenário 5: Competição baixa (deve passar)
        metricas_competicao_baixa = {
            "search_volume": 1000,
            "competition": "LOW",
            "cpc": 2.5,
            "competition_index": 30
        }
        assert validador_real._aplicar_criterios_validacao(keyword, metricas_competicao_baixa) is True
    
    def test_get_estatisticas_detalhadas(self, validador_real):
        """Testa obtenção de estatísticas detalhadas."""
        # Simular execuções
        validador_real.total_validated = 15
        validador_real.total_rejected = 5
        validador_real.execution_time = 45.5
        validador_real.last_execution = datetime.utcnow()
        validador_real.cache_hits = 8
        validador_real.cache_misses = 12
        
        estatisticas = validador_real.get_estatisticas()
        
        assert estatisticas["nome"] == "GoogleKeywordPlanner"
        assert estatisticas["total_validated"] == 15
        assert estatisticas["total_rejected"] == 5
        assert estatisticas["execution_time"] == 45.5
        assert estatisticas["taxa_rejeicao"] == 0.25  # 5/(15+5)
        assert estatisticas["cache_hit_rate"] == 0.4  # 8/(8+12)
        assert "last_execution" in estatisticas
    
    def test_reset_estatisticas_completo(self, validador_real):
        """Testa reset completo de estatísticas."""
        # Simular estatísticas
        validador_real.total_validated = 15
        validador_real.total_rejected = 5
        validador_real.execution_time = 45.5
        validador_real.last_execution = datetime.utcnow()
        validador_real.cache_hits = 8
        validador_real.cache_misses = 12
        
        validador_real.reset_estatisticas()
        
        assert validador_real.total_validated == 0
        assert validador_real.total_rejected == 0
        assert validador_real.execution_time == 0.0
        assert validador_real.last_execution is None
        assert validador_real.cache_hits == 0
        assert validador_real.cache_misses == 0
    
    @patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator._obter_metricas_da_fonte')
    def test_rate_limiting_comportamento(self, mock_obter_metricas, validador_real):
        """Testa comportamento do rate limiting."""
        metricas_mock = {
            "search_volume": 1000,
            "competition": "MEDIUM",
            "cpc": 2.5
        }
        mock_obter_metricas.return_value = metricas_mock
        
        # Mock cache
        validador_real.cache.get.return_value = None
        validador_real.cache.set.return_value = True
        
        start_time = time.time()
        
        # Fazer duas chamadas consecutivas
        validador_real.obter_metricas("keyword1")
        validador_real.obter_metricas("keyword2")
        
        end_time = time.time()
        
        # Deve ter respeitado o rate limiting (delay de 2.0s)
        assert (end_time - start_time) >= 2.0
        
        # Verificar que ambas as chamadas foram feitas
        assert mock_obter_metricas.call_count == 2


class TestValidadorAvancado:
    """Testes para ValidadorAvancado baseados no código real."""
    
    @pytest.fixture
    def config_validador_avancado_real(self):
        """Configuração real do validador avançado."""
        return {
            "estrategia_padrao": "cascata",
            "timeout_segundos": 300,
            "max_retries": 3,
            "google_keyword_planner": {
                "enabled": True,
                "api_enabled": True,
                "scraping_enabled": True,
                "cache_enabled": True,
                "rate_limiting_enabled": True,
                "min_search_volume": 100,
                "max_cpc": 5.0,
                "reject_high_competition": True
            }
        }
    
    @pytest.fixture
    def validador_avancado_real(self, config_validador_avancado_real):
        """Instância do validador avançado com configuração real."""
        with patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator'):
            return ValidadorAvancado(config_validador_avancado_real)
    
    @pytest.fixture
    def keywords_reais(self):
        """Keywords baseadas em dados reais."""
        return [
            Keyword(
                termo="marketing digital",
                volume_busca=1000,
                cpc=2.5,
                concorrencia=0.7,
                intencao=IntencaoBusca.COMERCIAL,
                fonte="google_keyword_planner"
            ),
            Keyword(
                termo="curso python online",
                volume_busca=5000,
                cpc=1.8,
                concorrencia=0.6,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="google_keyword_planner"
            ),
            Keyword(
                termo="receita bolo chocolate",
                volume_busca=50,
                cpc=0.5,
                concorrencia=0.3,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="google_keyword_planner"
            )
        ]
    
    def test_inicializacao_validador_avancado_real(self, config_validador_avancado_real):
        """Testa inicialização com configuração real."""
        with patch('infrastructure.validacao.google_keyword_planner_validator.GoogleKeywordPlannerValidator'):
            validador = ValidadorAvancado(config_validador_avancado_real)
            
            assert len(validador.validadores) > 0
            assert validador.execution_stats["total_executions"] == 0
            assert validador.estrategia_padrao == "cascata"
            assert validador.timeout_segundos == 300
            assert validador.max_retries == 3
    
    @patch('infrastructure.validacao.validador_avancado.ValidadorAvancado._validacao_cascata')
    def test_validar_keywords_cascata_real(self, mock_cascata, validador_avancado_real, keywords_reais):
        """Testa validação em cascata com dados reais."""
        mock_cascata.return_value = keywords_reais[:2]  # Retorna apenas as duas primeiras
        
        resultado = validador_avancado_real.validar_keywords(keywords_reais, estrategia="cascata")
        
        assert len(resultado) == 2
        assert resultado[0].termo == "marketing digital"
        assert resultado[1].termo == "curso python online"
        mock_cascata.assert_called_once_with(keywords_reais)
    
    @patch('infrastructure.validacao.validador_avancado.ValidadorAvancado._validacao_paralela')
    def test_validar_keywords_paralela_real(self, mock_paralela, validador_avancado_real, keywords_reais):
        """Testa validação paralela com dados reais."""
        mock_paralela.return_value = keywords_reais  # Retorna todas
        
        resultado = validador_avancado_real.validar_keywords(keywords_reais, estrategia="paralela")
        
        assert len(resultado) == 3
        mock_paralela.assert_called_once_with(keywords_reais)
    
    @patch('infrastructure.validacao.validador_avancado.ValidadorAvancado._validacao_consenso')
    def test_validar_keywords_consenso_real(self, mock_consenso, validador_avancado_real, keywords_reais):
        """Testa validação por consenso com dados reais."""
        mock_consenso.return_value = keywords_reais[:1]  # Retorna apenas a primeira
        
        resultado = validador_avancado_real.validar_keywords(keywords_reais, estrategia="consenso")
        
        assert len(resultado) == 1
        assert resultado[0].termo == "marketing digital"
        mock_consenso.assert_called_once_with(keywords_reais)
    
    def test_validar_keywords_estrategia_invalida_real(self, validador_avancado_real, keywords_reais):
        """Testa validação com estratégia inválida."""
        with pytest.raises(ValueError, match="Estratégia 'invalida' não suportada"):
            validador_avancado_real.validar_keywords(keywords_reais, estrategia="invalida")
    
    def test_get_estatisticas_detalhadas_avancado(self, validador_avancado_real):
        """Testa obtenção de estatísticas detalhadas do validador avançado."""
        # Simular execuções
        validador_avancado_real.execution_stats.update({
            "total_executions": 10,
            "total_keywords_processed": 200,
            "total_keywords_approved": 150,
            "total_execution_time": 300.0,
            "average_execution_time": 30.0,
            "success_rate": 0.85
        })
        
        estatisticas = validador_avancado_real.get_estatisticas()
        
        assert estatisticas["validador_avancado"]["total_executions"] == 10
        assert estatisticas["validador_avancado"]["total_keywords_processed"] == 200
        assert estatisticas["validador_avancado"]["total_keywords_approved"] == 150
        assert estatisticas["validador_avancado"]["overall_approval_rate"] == 0.75
        assert estatisticas["validador_avancado"]["average_execution_time"] == 30.0
        assert estatisticas["validador_avancado"]["success_rate"] == 0.85


class TestIntegracaoProcessador:
    """Testes de integração com o processador baseados no código real."""
    
    @pytest.fixture
    def config_processador_real(self):
        """Configuração real do processador."""
        return {
            "validacao": {
                "estrategia_padrao": "cascata",
                "google_keyword_planner": {
                    "enabled": True,
                    "api_enabled": True,
                    "scraping_enabled": True,
                    "cache_enabled": True,
                    "rate_limiting_enabled": True,
                    "min_search_volume": 100,
                    "max_cpc": 5.0,
                    "reject_high_competition": True
                }
            },
            "processamento": {
                "max_keywords_por_lote": 100,
                "timeout_segundos": 300
            }
        }
    
    @pytest.fixture
    def keywords_reais(self):
        """Keywords baseadas em dados reais."""
        return [
            Keyword(
                termo="marketing digital",
                volume_busca=1000,
                cpc=2.5,
                concorrencia=0.7,
                intencao=IntencaoBusca.COMERCIAL,
                fonte="google_keyword_planner"
            ),
            Keyword(
                termo="curso python online",
                volume_busca=5000,
                cpc=1.8,
                concorrencia=0.6,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="google_keyword_planner"
            ),
            Keyword(
                termo="receita bolo chocolate",
                volume_busca=50,
                cpc=0.5,
                concorrencia=0.3,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="google_keyword_planner"
            )
        ]
    
    @patch('infrastructure.processamento.processador_keywords.ValidadorAvancado')
    def test_processador_com_validador_avancado_real(self, mock_validador_avancado, config_processador_real, keywords_reais):
        """Testa integração real do processador com validador avançado."""
        from infrastructure.processamento.processador_keywords import ProcessadorKeywords
        
        # Mock do validador avançado
        mock_validador = Mock()
        mock_validador.validar_keywords.return_value = keywords_reais[:2]  # Aprova apenas as duas primeiras
        mock_validador.get_estatisticas.return_value = {
            "validador_avancado": {
                "total_executions": 1,
                "total_keywords_processed": 3,
                "total_keywords_approved": 2
            }
        }
        mock_validador_avancado.return_value = mock_validador
        
        # Criar processador
        processador = ProcessadorKeywords(config=config_processador_real)
        
        # Processar keywords
        resultado = processador.processar_keywords(keywords_reais, estrategia_validacao="cascata")
        
        # Verificar resultados
        assert len(resultado) == 2
        assert resultado[0].termo == "marketing digital"
        assert resultado[1].termo == "curso python online"
        
        # Verificar que validador foi chamado
        mock_validador.validar_keywords.assert_called_once_with(keywords_reais, estrategia="cascata")
        
        # Verificar métricas
        metricas = processador.get_metricas_completas()
        assert metricas["processador"]["total_execucoes"] == 1
        assert metricas["processador"]["total_keywords_processadas"] == 3
        assert metricas["processador"]["total_keywords_aprovadas"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
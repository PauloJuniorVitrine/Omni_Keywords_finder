"""
Testes Unitários: Processador Keywords
Testa funcionalidades do processador de keywords

Prompt: Melhorar testes unitários Fase 2
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 2.0.0
Tracing ID: TEST_PROCESSADOR_002_20241227
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from domain.models import Keyword, IntencaoBusca
from infrastructure.processamento.processador_keywords import ProcessadorKeywords
from infrastructure.processamento.validador_keywords import ValidadorKeywords
from infrastructure.coleta.google_related import GoogleRelatedColetor


class TestProcessadorKeywords:
    """Testes para ProcessadorKeywords baseados no código real."""
    
    @pytest.fixture
    def config_processador_real(self):
        """Configuração real do processador baseada no projeto."""
        return {
            "processamento": {
                "max_keywords_por_lote": 100,
                "timeout_segundos": 300,
                "retry_attempts": 3,
                "batch_size": 50
            },
            "validacao": {
                "estrategia_padrao": "cascata",
                "min_score": 0.5,
                "max_keywords_por_validador": 1000,
                "timeout_validacao": 60
            },
            "enriquecimento": {
                "enabled": True,
                "max_suggestions_per_keyword": 10,
                "min_volume_busca": 50,
                "max_cpc": 10.0
            },
            "cache": {
                "enabled": True,
                "ttl": 3600,
                "max_size": 10000
            },
            "logging": {
                "level": "INFO",
                "include_metrics": True
            }
        }
    
    @pytest.fixture
    def processador_real(self, config_processador_real):
        """Instância do processador com configuração real."""
        with patch('infrastructure.processamento.processador_keywords.ValidadorAvancado'), \
             patch('infrastructure.processamento.processador_keywords.CacheManager'), \
             patch('infrastructure.processamento.processador_keywords.EnriquecimentoKeywords'):
            return ProcessadorKeywords(config=config_processador_real)
    
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
                volume_busca=50,
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
                cpc=8.0,
                concorrencia=0.9,
                intencao=IntencaoBusca.COMERCIAL,
                fonte="google_keyword_planner",
                score=0.35,
                justificativa="CPC muito alto, competição alta"
            )
        ]
    
    def test_inicializacao_configuracao_real(self, config_processador_real):
        """Testa inicialização com configuração real do projeto."""
        with patch('infrastructure.processamento.processador_keywords.ValidadorAvancado'), \
             patch('infrastructure.processamento.processador_keywords.CacheManager'), \
             patch('infrastructure.processamento.processador_keywords.EnriquecimentoKeywords'):
            
            processador = ProcessadorKeywords(config=config_processador_real)
            
            # Verificar configurações específicas do projeto
            assert processador.config == config_processador_real
            assert processador.max_keywords_por_lote == 100
            assert processador.timeout_segundos == 300
            assert processador.retry_attempts == 3
            assert processador.batch_size == 50
            assert processador.min_score == 0.5
            assert processador.max_keywords_por_validador == 1000
            assert processador.timeout_validacao == 60
    
    @patch('infrastructure.processamento.processador_keywords.ProcessadorKeywords._validar_keywords')
    @patch('infrastructure.processamento.processador_keywords.ProcessadorKeywords._enriquecer_keywords')
    def test_processar_keywords_fluxo_completo(self, mock_enriquecer, mock_validar, processador_real, keywords_reais):
        """Testa fluxo completo de processamento de keywords."""
        # Mock validação
        keywords_validadas = keywords_reais[:2]  # Aprova apenas as duas primeiras
        mock_validar.return_value = keywords_validadas
        
        # Mock enriquecimento
        keywords_enriquecidas = keywords_validadas.copy()
        for kw in keywords_enriquecidas:
            kw.score = 0.9
            kw.justificativa = "Enriquecida com dados adicionais"
        mock_enriquecer.return_value = keywords_enriquecidas
        
        # Processar keywords
        resultado = processador_real.processar_keywords(keywords_reais)
        
        # Verificar resultados
        assert len(resultado) == 2
        assert resultado[0].termo == "marketing digital"
        assert resultado[1].termo == "curso python online"
        assert all(kw.score == 0.9 for kw in resultado)
        
        # Verificar que métodos foram chamados
        mock_validar.assert_called_once_with(keywords_reais)
        mock_enriquecer.assert_called_once_with(keywords_validadas)
    
    @patch('infrastructure.processamento.processador_keywords.ProcessadorKeywords._validar_keywords')
    def test_processar_keywords_apenas_validacao(self, mock_validar, processador_real, keywords_reais):
        """Testa processamento apenas com validação (sem enriquecimento)."""
        # Mock validação
        keywords_validadas = keywords_reais[:2]
        mock_validar.return_value = keywords_validadas
        
        # Processar keywords sem enriquecimento
        resultado = processador_real.processar_keywords(
            keywords_reais, 
            aplicar_enriquecimento=False
        )
        
        # Verificar resultados
        assert len(resultado) == 2
        assert resultado == keywords_validadas
        
        # Verificar que apenas validação foi chamada
        mock_validar.assert_called_once_with(keywords_reais)
    
    @patch('infrastructure.processamento.processador_keywords.ProcessadorKeywords._validar_keywords')
    def test_processar_keywords_estrategia_validacao(self, mock_validar, processador_real, keywords_reais):
        """Testa processamento com estratégia de validação específica."""
        # Mock validação
        keywords_validadas = keywords_reais[:1]  # Aprova apenas a primeira
        mock_validar.return_value = keywords_validadas
        
        # Processar com estratégia específica
        resultado = processador_real.processar_keywords(
            keywords_reais, 
            estrategia_validacao="paralela"
        )
        
        # Verificar que validação foi chamada com estratégia correta
        mock_validar.assert_called_once_with(keywords_reais, estrategia="paralela")
        assert len(resultado) == 1
    
    @patch('infrastructure.processamento.processador_keywords.ProcessadorKeywords._validar_keywords')
    def test_processar_keywords_lote_grande(self, mock_validar, processador_real):
        """Testa processamento de lote grande de keywords."""
        # Criar lote grande
        keywords_grande = []
        for i in range(150):  # Mais que o batch_size (50)
            keywords_grande.append(Keyword(
                termo=f"keyword {i}",
                volume_busca=100 + i,
                cpc=1.0 + (i * 0.01),
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="teste"
            ))
        
        # Mock validação
        mock_validar.return_value = keywords_grande[:100]  # Aprova 100
        
        # Processar lote grande
        resultado = processador_real.processar_keywords(keywords_grande)
        
        # Verificar que foi processado em lotes
        assert len(resultado) == 100
        assert mock_validar.call_count >= 1  # Pode ser chamado múltiplas vezes para lotes
    
    @patch('infrastructure.processamento.processador_keywords.ValidadorAvancado')
    def test_validar_keywords_integracao_validador(self, mock_validador_avancado, processador_real, keywords_reais):
        """Testa integração com validador avançado."""
        # Mock do validador avançado
        mock_validador = Mock()
        mock_validador.validar_keywords.return_value = keywords_reais[:2]
        mock_validador.get_estatisticas.return_value = {
            "validador_avancado": {
                "total_executions": 1,
                "total_keywords_processed": 4,
                "total_keywords_approved": 2
            }
        }
        mock_validador_avancado.return_value = mock_validador
        
        # Validar keywords
        resultado = processador_real._validar_keywords(keywords_reais)
        
        # Verificar resultados
        assert len(resultado) == 2
        assert resultado[0].termo == "marketing digital"
        assert resultado[1].termo == "curso python online"
        
        # Verificar que validador foi chamado
        mock_validador.validar_keywords.assert_called_once_with(keywords_reais, estrategia="cascata")
    
    @patch('infrastructure.processamento.processador_keywords.EnriquecimentoKeywords')
    def test_enriquecer_keywords_integracao(self, mock_enriquecimento, processador_real, keywords_reais):
        """Testa integração com enriquecimento de keywords."""
        # Mock do enriquecimento
        mock_enriquecimento_instance = Mock()
        keywords_enriquecidas = keywords_reais.copy()
        for kw in keywords_enriquecidas:
            kw.score = 0.95
            kw.justificativa = "Enriquecida com dados de mercado"
        mock_enriquecimento_instance.enriquecer_keywords.return_value = keywords_enriquecidas
        mock_enriquecimento.return_value = mock_enriquecimento_instance
        
        # Enriquecer keywords
        resultado = processador_real._enriquecer_keywords(keywords_reais)
        
        # Verificar resultados
        assert len(resultado) == 4
        assert all(kw.score == 0.95 for kw in resultado)
        assert all("Enriquecida com dados de mercado" in kw.justificativa for kw in resultado)
        
        # Verificar que enriquecimento foi chamado
        mock_enriquecimento_instance.enriquecer_keywords.assert_called_once_with(keywords_reais)
    
    def test_filtrar_por_score(self, processador_real, keywords_reais):
        """Testa filtro por score mínimo."""
        # Definir scores variados
        keywords_reais[0].score = 0.9  # Alto
        keywords_reais[1].score = 0.7  # Médio
        keywords_reais[2].score = 0.3  # Baixo
        keywords_reais[3].score = 0.6  # Médio-alto
        
        # Filtrar por score mínimo 0.5
        resultado = processador_real._filtrar_por_score(keywords_reais, min_score=0.5)
        
        # Deve manter apenas keywords com score >= 0.5
        assert len(resultado) == 3
        assert resultado[0].termo == "marketing digital"  # score 0.9
        assert resultado[1].termo == "curso python online"  # score 0.7
        assert resultado[2].termo == "seguro auto"  # score 0.6
        assert "receita bolo chocolate" not in [kw.termo for kw in resultado]  # score 0.3
    
    def test_ordenar_por_score(self, processador_real, keywords_reais):
        """Testa ordenação por score."""
        # Definir scores variados
        keywords_reais[0].score = 0.7
        keywords_reais[1].score = 0.9
        keywords_reais[2].score = 0.5
        keywords_reais[3].score = 0.8
        
        # Ordenar por score (decrescente)
        resultado = processador_real._ordenar_por_score(keywords_reais)
        
        # Verificar ordenação
        assert len(resultado) == 4
        assert resultado[0].score == 0.9  # curso python online
        assert resultado[1].score == 0.8  # seguro auto
        assert resultado[2].score == 0.7  # marketing digital
        assert resultado[3].score == 0.5  # receita bolo chocolate
    
    def test_get_metricas_completas(self, processador_real):
        """Testa obtenção de métricas completas."""
        # Simular algumas execuções
        processador_real.metricas.update({
            "total_execucoes": 5,
            "total_keywords_processadas": 200,
            "total_keywords_aprovadas": 150,
            "total_keywords_rejeitadas": 50,
            "tempo_medio_processamento": 45.5,
            "taxa_aprovacao": 0.75,
            "ultima_execucao": datetime.utcnow().isoformat()
        })
        
        metricas = processador_real.get_metricas_completas()
        
        assert metricas["processador"]["total_execucoes"] == 5
        assert metricas["processador"]["total_keywords_processadas"] == 200
        assert metricas["processador"]["total_keywords_aprovadas"] == 150
        assert metricas["processador"]["total_keywords_rejeitadas"] == 50
        assert metricas["processador"]["tempo_medio_processamento"] == 45.5
        assert metricas["processador"]["taxa_aprovacao"] == 0.75
        assert "ultima_execucao" in metricas["processador"]
    
    def test_reset_metricas(self, processador_real):
        """Testa reset de métricas."""
        # Simular métricas
        processador_real.metricas.update({
            "total_execucoes": 5,
            "total_keywords_processadas": 200,
            "total_keywords_aprovadas": 150,
            "tempo_medio_processamento": 45.5
        })
        
        # Reset métricas
        processador_real.reset_metricas()
        
        # Verificar que foram resetadas
        assert processador_real.metricas["total_execucoes"] == 0
        assert processador_real.metricas["total_keywords_processadas"] == 0
        assert processador_real.metricas["total_keywords_aprovadas"] == 0
        assert processador_real.metricas["tempo_medio_processamento"] == 0.0
    
    @patch('infrastructure.processamento.processador_keywords.ProcessadorKeywords._validar_keywords')
    def test_processar_keywords_timeout(self, mock_validar, processador_real, keywords_reais):
        """Testa comportamento com timeout."""
        # Mock validação que demora
        def validacao_lenta(*args, **kwargs):
            import time
            time.sleep(0.1)  # Simular demora
            return keywords_reais[:2]
        
        mock_validar.side_effect = validacao_lenta
        
        # Processar com timeout baixo
        processador_real.timeout_segundos = 0.05  # Timeout muito baixo
        
        with pytest.raises(TimeoutError):
            processador_real.processar_keywords(keywords_reais)
    
    @patch('infrastructure.processamento.processador_keywords.ProcessadorKeywords._validar_keywords')
    def test_processar_keywords_retry(self, mock_validar, processador_real, keywords_reais):
        """Testa comportamento com retry em caso de falha."""
        # Mock validação que falha algumas vezes
        mock_validar.side_effect = [
            Exception("Erro temporário"),  # Primeira tentativa falha
            Exception("Erro temporário"),  # Segunda tentativa falha
            keywords_reais[:2]  # Terceira tentativa sucesso
        ]
        
        # Processar com retry
        resultado = processador_real.processar_keywords(keywords_reais)
        
        # Verificar que funcionou após retry
        assert len(resultado) == 2
        assert mock_validar.call_count == 3  # Chamado 3 vezes
    
    @patch('infrastructure.processamento.processador_keywords.ProcessadorKeywords._validar_keywords')
    def test_processar_keywords_retry_excedido(self, mock_validar, processador_real, keywords_reais):
        """Testa comportamento quando retry é excedido."""
        # Mock validação que sempre falha
        mock_validar.side_effect = Exception("Erro persistente")
        
        # Processar com retry limitado
        processador_real.retry_attempts = 2
        
        with pytest.raises(Exception, match="Erro persistente"):
            processador_real.processar_keywords(keywords_reais)
        
        # Verificar que foi tentado o número correto de vezes
        assert mock_validar.call_count == 2


class TestIntegracaoValidadorKeywords:
    """Testes de integração com ValidadorKeywords."""
    
    @pytest.fixture
    def validador_keywords(self):
        """Instância do validador de keywords."""
        return ValidadorKeywords(
            min_volume_busca=100,
            max_cpc=5.0,
            min_score=0.5,
            palavras_obrigatorias=['teste', 'validação']
        )
    
    @pytest.fixture
    def keywords_teste(self):
        """Keywords para teste de validação."""
        return [
            Keyword(
                termo="palavra de teste para validação",
                volume_busca=1000,
                cpc=2.5,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL,
                score=0.8
            ),
            Keyword(
                termo="palavra sem palavras obrigatórias",
                volume_busca=50,  # Volume baixo
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL,
                score=0.3  # Score baixo
            ),
            Keyword(
                termo="outra palavra de teste",
                volume_busca=500,
                cpc=10.0,  # CPC alto
                concorrencia=0.8,
                intencao=IntencaoBusca.COMERCIAL,
                score=0.7
            )
        ]
    
    def test_validar_keyword_criterios_multiplos(self, validador_keywords, keywords_teste):
        """Testa validação com múltiplos critérios."""
        # Keyword válida
        is_valida, detalhes = validador_keywords.validar_keyword(keywords_teste[0])
        assert is_valida is True
        assert "volume_busca" in detalhes["regras_verificadas"]
        assert "cpc" in detalhes["regras_verificadas"]
        assert "score" in detalhes["regras_verificadas"]
        assert "palavras_obrigatorias" in detalhes["regras_verificadas"]
        
        # Keyword inválida (volume baixo + score baixo)
        is_valida, detalhes = validador_keywords.validar_keyword(keywords_teste[1])
        assert is_valida is False
        assert len(detalhes["violacoes"]) >= 2  # Pelo menos volume e score
    
    def test_validar_keywords_lote(self, validador_keywords, keywords_teste):
        """Testa validação de lote de keywords."""
        resultado = validador_keywords.validar_keywords(keywords_teste)
        
        # Deve aprovar apenas a primeira keyword
        assert len(resultado) == 1
        assert resultado[0].termo == "palavra de teste para validação"


class TestIntegracaoGoogleRelatedColetor:
    """Testes de integração com Google Related Coletor."""
    
    @pytest.fixture
    def coletor_google(self):
        """Instância do coletor Google Related."""
        config = {
            "max_keywords": 10,
            "timeout": 30,
            "retry_attempts": 3
        }
        return GoogleRelatedColetor(config)
    
    @patch('infrastructure.coleta.google_related.GoogleRelatedColetor.coletar_keywords')
    def test_coleta_keywords_relacionadas(self, mock_coletar, coletor_google):
        """Testa coleta de keywords relacionadas."""
        # Mock coleta
        keywords_relacionadas = [
            Keyword(
                termo="marketing digital curso",
                volume_busca=800,
                cpc=2.0,
                concorrencia=0.6,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="google_related"
            ),
            Keyword(
                termo="marketing digital estratégias",
                volume_busca=1200,
                cpc=3.0,
                concorrencia=0.7,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="google_related"
            )
        ]
        mock_coletar.return_value = keywords_relacionadas
        
        # Coletar keywords relacionadas
        resultado = coletor_google.coletar_keywords("marketing digital")
        
        # Verificar resultados
        assert len(resultado) == 2
        assert all("marketing digital" in kw.termo for kw in resultado)
        assert all(kw.fonte == "google_related" for kw in resultado)
        
        # Verificar que coleta foi chamada
        mock_coletar.assert_called_once_with("marketing digital")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
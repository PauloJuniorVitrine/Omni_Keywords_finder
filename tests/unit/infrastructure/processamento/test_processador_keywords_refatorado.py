from typing import Dict, List, Optional, Any
"""
Testes para validação da refatoração do ProcessadorKeywords.
Testa se o enriquecimento está sendo delegado para o EnriquecidorKeywords.

Prompt: CHECKLIST_SEGUNDA_REVISAO.md - IMP-001
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19
Versão: 1.0.0
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from domain.models import Keyword, IntencaoBusca
from infrastructure.processamento.processador_keywords import ProcessadorKeywords
from infrastructure.processamento.enriquecidor_keywords import EnriquecidorKeywords


class TestProcessadorKeywordsRefatorado:
    """Testes para validação da refatoração do ProcessadorKeywords."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.processador = ProcessadorKeywords(
            pesos_score={
                "volume": 0.4,
                "cpc": 0.2,
                "intention": 0.2,
                "competition": 0.2
            },
            paralelizar_enriquecimento=True
        )
        
    def test_inicializacao_com_enriquecidor(self):
        """Testa se o ProcessadorKeywords inicializa com EnriquecidorKeywords."""
        assert hasattr(self.processador, 'enriquecidor')
        assert isinstance(self.processador.enriquecidor, EnriquecidorKeywords)
        
        # Verificar se os pesos foram passados corretamente
        assert self.processador.enriquecidor.pesos == {
            "volume": 0.4,
            "cpc": 0.2,
            "intention": 0.2,
            "competition": 0.2
        }
        
        # Verificar se a paralelização foi configurada
        assert self.processador.enriquecidor.paralelizar is True
        
    def test_enriquecer_delega_para_enriquecidor(self):
        """Testa se o método enriquecer delega para o EnriquecidorKeywords."""
        keywords = [
            Keyword(
                termo="palavra chave 1",
                volume_busca=1000,
                cpc=2.0,
                concorrencia=0.3,
                intencao=IntencaoBusca.COMERCIAL
            ),
            Keyword(
                termo="palavra chave 2",
                volume_busca=2000,
                cpc=3.0,
                concorrencia=0.2,
                intencao=IntencaoBusca.TRANSACIONAL
            )
        ]
        
        # Mock do método enriquecer_lista do EnriquecidorKeywords
        with patch.object(self.processador.enriquecidor, 'enriquecer_lista') as mock_enriquecer:
            mock_enriquecer.return_value = keywords  # Retorna as mesmas keywords
            
            # Mock do método obter_erros
            with patch.object(self.processador.enriquecidor, 'obter_erros') as mock_erros:
                mock_erros.return_value = []
                
                # Mock do método obter_configuracao
                with patch.object(self.processador.enriquecidor, 'obter_configuracao') as mock_config:
                    mock_config.return_value = {"pesos": self.processador.enriquecidor.pesos}
                    
                    # Executar enriquecimento
                    resultado = self.processador.enriquecer(keywords)
                    
                    # Verificar se o método do enriquecidor foi chamado
                    mock_enriquecer.assert_called_once_with(keywords)
                    
                    # Verificar se os erros foram capturados
                    mock_erros.assert_called_once()
                    
                    # Verificar se a configuração foi obtida
                    mock_config.assert_called_once()
                    
                    # Verificar resultado
                    assert resultado == keywords
                    
    def test_enriquecer_captura_erros(self):
        """Testa se os erros do enriquecimento são capturados corretamente."""
        keywords = [
            Keyword(
                termo="palavra chave",
                volume_busca=1000,
                cpc=2.0,
                concorrencia=0.3,
                intencao=IntencaoBusca.COMERCIAL
            )
        ]
        
        erros_esperados = [
            {"termo": "palavra chave", "erro": "erro teste", "timestamp": "2024-12-19T10:00:00"}
        ]
        
        with patch.object(self.processador.enriquecidor, 'enriquecer_lista') as mock_enriquecer:
            mock_enriquecer.return_value = keywords
            
            with patch.object(self.processador.enriquecidor, 'obter_erros') as mock_erros:
                mock_erros.return_value = erros_esperados
                
                with patch.object(self.processador.enriquecidor, 'obter_configuracao') as mock_config:
                    mock_config.return_value = {"pesos": self.processador.enriquecidor.pesos}
                    
                    resultado = self.processador.enriquecer(keywords)
                    
                    # Verificar se os erros foram capturados
                    assert hasattr(self.processador, '_last_enriquecimento_erros')
                    assert self.processador._last_enriquecimento_erros == erros_esperados
                    
    def test_enriquecer_trata_excecoes(self):
        """Testa se exceções durante o enriquecimento são tratadas."""
        keywords = [
            Keyword(
                termo="palavra chave",
                volume_busca=1000,
                cpc=2.0,
                concorrencia=0.3,
                intencao=IntencaoBusca.COMERCIAL
            )
        ]
        
        with patch.object(self.processador.enriquecidor, 'enriquecer_lista') as mock_enriquecer:
            mock_enriquecer.side_effect = Exception("Erro no enriquecimento")
            
            resultado = self.processador.enriquecer(keywords)
            
            # Verificar que retorna lista vazia em caso de erro
            assert resultado == []
            
    def test_processar_com_enriquecimento(self):
        """Testa o pipeline completo com enriquecimento."""
        keywords = [
            Keyword(
                termo="palavra chave",
                volume_busca=1000,
                cpc=2.0,
                concorrencia=0.3,
                intencao=IntencaoBusca.COMERCIAL
            )
        ]
        
        with patch.object(self.processador, 'normalizar') as mock_normalizar:
            mock_normalizar.return_value = keywords
            
            with patch.object(self.processador, 'limpar') as mock_limpar:
                mock_limpar.return_value = keywords
                
                with patch.object(self.processador.enriquecidor, 'enriquecer_lista') as mock_enriquecer:
                    mock_enriquecer.return_value = keywords
                    
                    with patch.object(self.processador.enriquecidor, 'obter_erros') as mock_erros:
                        mock_erros.return_value = []
                        
                        with patch.object(self.processador.enriquecidor, 'obter_configuracao') as mock_config:
                            mock_config.return_value = {"pesos": self.processador.enriquecidor.pesos}
                            
                            # Executar pipeline com enriquecimento
                            resultado, relatorio = self.processador.processar(
                                keywords,
                                enriquecer=True,
                                relatorio=True
                            )
                            
                            # Verificar que o enriquecimento foi executado
                            mock_enriquecer.assert_called_once_with(keywords)
                            
                            # Verificar resultado
                            assert resultado == keywords
                            assert relatorio is not None
                            assert "enriquecidas" in relatorio
                            
    def test_compatibilidade_com_tests_existentes(self):
        """Testa compatibilidade com testes existentes."""
        keywords = [
            Keyword(
                termo="palavra chave",
                volume_busca=1000,
                cpc=2.0,
                concorrencia=0.3,
                intencao=IntencaoBusca.COMERCIAL
            )
        ]
        
        # Teste básico de enriquecimento
        with patch.object(self.processador.enriquecidor, 'enriquecer_lista') as mock_enriquecer:
            mock_enriquecer.return_value = keywords
            
            with patch.object(self.processador.enriquecidor, 'obter_erros') as mock_erros:
                mock_erros.return_value = []
                
                with patch.object(self.processador.enriquecidor, 'obter_configuracao') as mock_config:
                    mock_config.return_value = {"pesos": self.processador.enriquecidor.pesos}
                    
                    resultado = self.processador.enriquecer(keywords)
                    
                    # Verificar que o resultado é uma lista
                    assert isinstance(resultado, list)
                    
                    # Verificar que todas as keywords têm score e justificativa
                    for kw in resultado:
                        assert hasattr(kw, 'score')
                        assert hasattr(kw, 'justificativa')
                        
    def test_configuracao_pesos_personalizada(self):
        """Testa configuração de pesos personalizada."""
        pesos_personalizados = {
            "volume": 0.6,
            "cpc": 0.3,
            "intention": 0.1,
            "competition": 0.0
        }
        
        processador_custom = ProcessadorKeywords(
            pesos_score=pesos_personalizados,
            paralelizar_enriquecimento=False
        )
        
        # Verificar se os pesos foram passados corretamente
        assert processador_custom.enriquecidor.pesos == pesos_personalizados
        
        # Verificar se a paralelização foi configurada
        assert processador_custom.enriquecidor.paralelizar is False
        
    def test_logging_estruturado(self):
        """Testa se o logging estruturado está funcionando."""
        keywords = [
            Keyword(
                termo="palavra chave",
                volume_busca=1000,
                cpc=2.0,
                concorrencia=0.3,
                intencao=IntencaoBusca.COMERCIAL
            )
        ]
        
        with patch('infrastructure.processamento.processador_keywords.logger') as mock_logger:
            with patch.object(self.processador.enriquecidor, 'enriquecer_lista') as mock_enriquecer:
                mock_enriquecer.return_value = keywords
                
                with patch.object(self.processador.enriquecidor, 'obter_erros') as mock_erros:
                    mock_erros.return_value = []
                    
                    with patch.object(self.processador.enriquecidor, 'obter_configuracao') as mock_config:
                        mock_config.return_value = {"pesos": self.processador.enriquecidor.pesos}
                        
                        self.processador.enriquecer(keywords)
                        
                        # Verificar se o logging foi chamado
                        mock_logger.info.assert_called()
                        
                        # Verificar estrutura do log
                        call_args = mock_logger.info.call_args[0][0]
                        assert "timestamp" in call_args
                        assert "event" in call_args
                        assert "status" in call_args
                        assert "source" in call_args
                        assert "details" in call_args
                        assert call_args["event"] == "enriquecimento_keywords_delegado"
                        assert call_args["status"] == "success" 
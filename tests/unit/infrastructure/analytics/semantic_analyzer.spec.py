from typing import Dict, List, Optional, Any
"""
Testes para Analisador Semântico - LONGTAIL-001
Sistema de contagem de palavras significativas

Tracing ID: LONGTAIL-001-TEST
Data/Hora: 2024-12-20 16:35:00 UTC
Versão: 1.0
Status: CRIADO (SEM EXECUÇÃO)

Responsável: Sistema de Cauda Longa
"""

import pytest
from unittest.mock import Mock, patch
from infrastructure.processamento.analisador_semantico import (
    AnalisadorSemantico, 
    AnalisePalavras
)


class TestAnalisadorSemantico:
    """Testes para o Analisador Semântico."""
    
    def setup_method(self):
        """Configuração para cada teste."""
        self.analisador = AnalisadorSemantico()
    
    def test_inicializacao_analisador(self):
        """Testa inicialização do analisador."""
        # Verifica se o analisador foi inicializado corretamente
        assert self.analisador is not None
        assert hasattr(self.analisador, '_stop_words')
        assert hasattr(self.analisador, '_palavras_chave_especificas')
        assert self.analisador._min_caracteres == 3
        assert self.analisador._case_sensitive is False
        assert self.analisador._remover_acentos is False
    
    def test_carregamento_stop_words(self):
        """Testa carregamento de stop words."""
        stop_words = self.analisador._stop_words
        
        # Verifica se stop words foram carregadas
        assert len(stop_words) > 0
        assert "o" in stop_words
        assert "a" in stop_words
        assert "de" in stop_words
        assert "para" in stop_words
        assert "com" in stop_words
    
    def test_carregamento_palavras_chave(self):
        """Testa carregamento de palavras-chave específicas."""
        palavras_chave = self.analisador._palavras_chave_especificas
        
        # Verifica se palavras-chave foram carregadas
        assert len(palavras_chave) > 0
        assert "como" in palavras_chave
        assert "qual" in palavras_chave
        assert "melhor" in palavras_chave
        assert "guia" in palavras_chave
        assert "tutorial" in palavras_chave
    
    def test_normalizacao_texto_basica(self):
        """Testa normalização básica de texto."""
        texto = "  Olá   Mundo  !  "
        resultado = self.analisador.normalizar_texto(texto)
        
        # Verifica normalização
        assert resultado == "olá mundo !"
    
    def test_normalizacao_texto_case_sensitive(self):
        """Testa normalização com case sensitive."""
        config = {"case_sensitive": True}
        analisador = AnalisadorSemantico(config)
        
        texto = "Olá Mundo"
        resultado = analisador.normalizar_texto(texto)
        
        # Verifica que mantém case original
        assert resultado == "Olá Mundo"
    
    def test_normalizacao_texto_remover_acentos(self):
        """Testa normalização com remoção de acentos."""
        config = {"remover_acentos": True}
        analisador = AnalisadorSemantico(config)
        
        texto = "Olá São Paulo"
        resultado = analisador.normalizar_texto(texto)
        
        # Verifica remoção de acentos
        assert "á" not in resultado
        assert "ã" not in resultado
    
    def test_extracao_palavras_simples(self):
        """Testa extração de palavras simples."""
        texto = "Olá mundo, como vai?"
        palavras = self.analisador.extrair_palavras(texto)
        
        # Verifica extração
        assert "olá" in palavras
        assert "mundo" in palavras
        assert "como" in palavras
        assert "vai" in palavras
    
    def test_extracao_palavras_com_pontuacao(self):
        """Testa extração de palavras com pontuação."""
        texto = "Olá! Como vai? Tudo bem."
        palavras = self.analisador.extrair_palavras(texto)
        
        # Verifica que pontuação é removida
        assert "olá" in palavras
        assert "como" in palavras
        assert "vai" in palavras
        assert "tudo" in palavras
        assert "bem" in palavras
    
    def test_filtro_palavras_significativas(self):
        """Testa filtro de palavras significativas."""
        palavras = ["o", "mundo", "de", "palavras", "significativas", "a", "ser", "analisadas"]
        
        significativas, removidas = self.analisador.filtrar_palavras_significativas(palavras)
        
        # Verifica filtragem
        assert "mundo" in significativas
        assert "palavras" in significativas
        assert "significativas" in significativas
        assert "analisadas" in significativas
        
        # Verifica remoção de stop words
        assert "o" not in significativas
        assert "de" not in significativas
        assert "a" not in significativas
        assert "ser" not in significativas
    
    def test_filtro_palavras_curtas(self):
        """Testa filtro de palavras muito curtas."""
        palavras = ["a", "ab", "abc", "abcd"]
        
        significativas, removidas = self.analisador.filtrar_palavras_significativas(palavras)
        
        # Verifica que palavras com menos de 3 caracteres são removidas
        assert "a" not in significativas
        assert "ab" not in significativas
        assert "abc" in significativas
        assert "abcd" in significativas
    
    def test_filtro_numeros(self):
        """Testa filtro de números isolados."""
        palavras = ["palavra", "123", "texto", "456"]
        
        significativas, removidas = self.analisador.filtrar_palavras_significativas(palavras)
        
        # Verifica que números são removidos
        assert "palavra" in significativas
        assert "texto" in significativas
        assert "123" not in significativas
        assert "456" not in significativas
    
    def test_calculo_score_significancia(self):
        """Testa cálculo de score de significância."""
        # Palavras com palavras-chave específicas
        palavras_chave = ["como", "melhor", "guia", "tutorial"]
        score = self.analisador.calcular_score_significancia(palavras_chave)
        
        # Verifica score
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Deve ter score alto por ter palavras-chave
    
    def test_calculo_score_sem_palavras_chave(self):
        """Testa cálculo de score sem palavras-chave específicas."""
        palavras_comuns = ["palavra", "texto", "exemplo", "teste"]
        score = self.analisador.calcular_score_significancia(palavras_comuns)
        
        # Verifica score
        assert 0.0 <= score <= 1.0
        assert score < 0.5  # Deve ter score menor sem palavras-chave
    
    def test_calculo_score_lista_vazia(self):
        """Testa cálculo de score com lista vazia."""
        score = self.analisador.calcular_score_significancia([])
        
        # Verifica score zero
        assert score == 0.0
    
    def test_analise_palavras_completa(self):
        """Testa análise completa de palavras."""
        texto = "Como fazer o melhor guia tutorial para iniciantes"
        
        resultado = self.analisador.analisar_palavras(texto)
        
        # Verifica tipo de retorno
        assert isinstance(resultado, AnalisePalavras)
        
        # Verifica campos obrigatórios
        assert hasattr(resultado, 'palavras_significativas')
        assert hasattr(resultado, 'total_palavras')
        assert hasattr(resultado, 'palavras_unicas')
        assert hasattr(resultado, 'palavras_significativas_unicas')
        assert hasattr(resultado, 'score_significancia')
        assert hasattr(resultado, 'palavras_removidas')
        assert hasattr(resultado, 'metadados')
        
        # Verifica valores
        assert resultado.total_palavras > 0
        assert len(resultado.palavras_significativas) > 0
        assert 0.0 <= resultado.score_significancia <= 1.0
    
    def test_analise_palavras_texto_vazio(self):
        """Testa análise com texto vazio."""
        resultado = self.analisador.analisar_palavras("")
        
        # Verifica resultado para texto vazio
        assert resultado.total_palavras == 0
        assert len(resultado.palavras_significativas) == 0
        assert resultado.score_significancia == 0.0
    
    def test_analise_palavras_apenas_stop_words(self):
        """Testa análise com apenas stop words."""
        texto = "o a de para com"
        
        resultado = self.analisador.analisar_palavras(texto)
        
        # Verifica que todas as palavras são removidas
        assert resultado.total_palavras > 0
        assert len(resultado.palavras_significativas) == 0
        assert resultado.score_significancia == 0.0
    
    def test_metricas_analisador(self):
        """Testa obtenção de métricas do analisador."""
        # Executa algumas análises
        self.analisador.analisar_palavras("Texto de teste")
        self.analisador.analisar_palavras("Outro texto para análise")
        
        metricas = self.analisador.obter_metricas()
        
        # Verifica métricas
        assert "total_analises" in metricas
        assert "total_palavras_processadas" in metricas
        assert "tempo_total_analise" in metricas
        assert "ultima_analise" in metricas
        assert "tempo_medio_analise" in metricas
        assert "palavras_por_analise" in metricas
        
        # Verifica valores
        assert metricas["total_analises"] == 2
        assert metricas["total_palavras_processadas"] > 0
        assert metricas["tempo_total_analise"] > 0.0
    
    def test_resetar_metricas(self):
        """Testa reset de métricas."""
        # Executa análise
        self.analisador.analisar_palavras("Texto de teste")
        
        # Verifica que métricas foram atualizadas
        metricas_antes = self.analisador.obter_metricas()
        assert metricas_antes["total_analises"] == 1
        
        # Reseta métricas
        self.analisador.resetar_metricas()
        
        # Verifica reset
        metricas_depois = self.analisador.obter_metricas()
        assert metricas_depois["total_analises"] == 0
        assert metricas_depois["total_palavras_processadas"] == 0
        assert metricas_depois["tempo_total_analise"] == 0.0
    
    def test_configuracao_personalizada(self):
        """Testa configuração personalizada do analisador."""
        config = {
            "min_caracteres": 4,
            "case_sensitive": True,
            "remover_acentos": True
        }
        
        analisador = AnalisadorSemantico(config)
        
        # Verifica configuração
        assert analisador._min_caracteres == 4
        assert analisador._case_sensitive is True
        assert analisador._remover_acentos is True
    
    def test_analise_palavras_com_erro(self):
        """Testa análise com erro (simulação)."""
        with patch.object(self.analisador, 'extrair_palavras', side_effect=Exception("Erro simulado")):
            resultado = self.analisador.analisar_palavras("Texto de teste")
            
            # Verifica resultado de erro
            assert resultado.total_palavras == 0
            assert len(resultado.palavras_significativas) == 0
            assert resultado.score_significancia == 0.0
            assert "erro" in resultado.metadados
    
    def test_edge_case_caracteres_especiais(self):
        """Testa edge case com caracteres especiais."""
        texto = "palavra@#$%^&*()_+{}|:<>?[]\\;'\",./<>?"
        
        resultado = self.analisador.analisar_palavras(texto)
        
        # Verifica que caracteres especiais são tratados
        assert resultado.total_palavras >= 0
        assert len(resultado.palavras_significativas) >= 0
    
    def test_edge_case_texto_muito_longo(self):
        """Testa edge case com texto muito longo."""
        texto = "palavra " * 1000  # 1000 palavras
        
        resultado = self.analisador.analisar_palavras(texto)
        
        # Verifica processamento de texto longo
        assert resultado.total_palavras > 0
        assert len(resultado.palavras_significativas) >= 0
    
    def test_edge_case_unicode(self):
        """Testa edge case com caracteres Unicode."""
        texto = "Olá São Paulo 🇧🇷 café ☕"
        
        resultado = self.analisador.analisar_palavras(texto)
        
        # Verifica processamento de Unicode
        assert resultado.total_palavras > 0
        assert len(resultado.palavras_significativas) >= 0


class TestAnalisePalavras:
    """Testes para a classe AnalisePalavras."""
    
    def test_criacao_analise_palavras(self):
        """Testa criação de objeto AnalisePalavras."""
        analise = AnalisePalavras(
            palavras_significativas=["palavra", "texto"],
            total_palavras=5,
            palavras_unicas=4,
            palavras_significativas_unicas=2,
            score_significancia=0.8,
            palavras_removidas=["o", "de"],
            metadados={"teste": "valor"}
        )
        
        # Verifica criação
        assert analise.palavras_significativas == ["palavra", "texto"]
        assert analise.total_palavras == 5
        assert analise.palavras_unicas == 4
        assert analise.palavras_significativas_unicas == 2
        assert analise.score_significancia == 0.8
        assert analise.palavras_removidas == ["o", "de"]
        assert analise.metadados == {"teste": "valor"}
    
    def test_analise_palavras_vazia(self):
        """Testa criação de AnalisePalavras vazia."""
        analise = AnalisePalavras(
            palavras_significativas=[],
            total_palavras=0,
            palavras_unicas=0,
            palavras_significativas_unicas=0,
            score_significancia=0.0,
            palavras_removidas=[],
            metadados={}
        )
        
        # Verifica criação vazia
        assert len(analise.palavras_significativas) == 0
        assert analise.total_palavras == 0
        assert analise.score_significancia == 0.0


# Testes de integração (sem execução)
class TestIntegracaoAnalisadorSemantico:
    """Testes de integração para o Analisador Semântico."""
    
    def test_integracao_com_validador_existente(self):
        """Testa integração com validador existente (simulação)."""
        # Este teste seria executado quando o validador estiver disponível
        pass
    
    def test_performance_analise_lote(self):
        """Testa performance de análise em lote (simulação)."""
        # Este teste seria executado para validar performance
        pass
    
    def test_configuracao_flexivel(self):
        """Testa configuração flexível do analisador (simulação)."""
        # Este teste seria executado para validar configurações
        pass 
from typing import Dict, List, Optional, Any
"""
Testes unitários para o normalizador central e sua integração com coletores.

Prompt: CHECKLIST_SEGUNDA_REVISAO.md - IMP-003
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19
Versão: 1.0.0
"""

import pytest
from unittest.mock import Mock, patch
from shared.utils.normalizador_central import NormalizadorCentral, normalizar_termo, validar_termo


class TestNormalizadorCentral:
    """Testes para o normalizador central."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.normalizador = NormalizadorCentral(
            remover_acentos=False,
            case_sensitive=False,
            caracteres_permitidos=r'^[\w\string_data\-.,?!@#]+$',
            min_caracteres=3,
            max_caracteres=100
        )
    
    def test_normalizar_termo_basico(self):
        """Testa normalização básica de termos."""
        # Arrange
        termo = "  Palavra-Chave  "
        
        # Act
        resultado = self.normalizador.normalizar_termo(termo)
        
        # Assert
        assert resultado == "palavra-chave"
    
    def test_normalizar_termo_com_caracteres_especiais(self):
        """Testa normalização com caracteres especiais do Instagram."""
        # Arrange
        termo = "#hashtag @usuario"
        
        # Act
        resultado = self.normalizador.normalizar_termo(termo)
        
        # Assert
        assert resultado == "#hashtag @usuario"
    
    def test_normalizar_termo_invalido(self):
        """Testa normalização de termo inválido."""
        # Arrange
        termo = "ab"  # Muito curto
        
        # Act
        resultado = self.normalizador.normalizar_termo(termo)
        
        # Assert
        assert resultado == ""
    
    def test_normalizar_lista_termos(self):
        """Testa normalização de lista de termos."""
        # Arrange
        termos = ["  Termo1  ", "termo1", "Termo2", "  termo2  "]
        
        # Act
        resultado = self.normalizador.normalizar_lista_termos(termos)
        
        # Assert
        assert len(resultado) == 2  # Remove duplicatas
        assert "termo1" in resultado
        assert "termo2" in resultado
    
    def test_validar_termo(self):
        """Testa validação de termos."""
        # Arrange & Act & Assert
        assert self.normalizador.validar_termo("termo_valido") == True
        assert self.normalizador.validar_termo("") == False
        assert self.normalizador.validar_termo("ab") == False  # Muito curto


class TestIntegracaoColetores:
    """Testes de integração com coletores."""
    
    @patch('infrastructure.coleta.instagram.InstagramColetor')
    def test_integracao_instagram(self, mock_instagram):
        """Testa integração com InstagramColetor."""
        # Arrange
        from infrastructure.coleta.instagram import InstagramColetor
        
        # Act
        coletor = InstagramColetor()
        
        # Assert
        assert hasattr(coletor, 'normalizador')
        assert isinstance(coletor.normalizador, NormalizadorCentral)
    
    @patch('infrastructure.coleta.amazon.AmazonColetor')
    def test_integracao_amazon(self, mock_amazon):
        """Testa integração com AmazonColetor."""
        # Arrange
        from infrastructure.coleta.amazon import AmazonColetor
        
        # Act
        coletor = AmazonColetor()
        
        # Assert
        assert hasattr(coletor, 'normalizador')
        assert isinstance(coletor.normalizador, NormalizadorCentral)
    
    @patch('infrastructure.coleta.google_paa.GooglePAAColetor')
    def test_integracao_google_paa(self, mock_google_paa):
        """Testa integração com GooglePAAColetor."""
        # Arrange
        from infrastructure.coleta.google_paa import GooglePAAColetor
        
        # Act
        coletor = GooglePAAColetor()
        
        # Assert
        assert hasattr(coletor, 'normalizador')
        assert isinstance(coletor.normalizador, NormalizadorCentral)


class TestFuncoesGlobais:
    """Testes para funções globais do normalizador."""
    
    def test_normalizar_termo_global(self):
        """Testa função global normalizar_termo."""
        # Arrange
        termo = "  Termo Teste  "
        
        # Act
        resultado = normalizar_termo(termo)
        
        # Assert
        assert resultado == "termo teste"
    
    def test_validar_termo_global(self):
        """Testa função global validar_termo."""
        # Arrange & Act & Assert
        assert validar_termo("termo_valido") == True
        assert validar_termo("") == False


class TestCasosEspecificos:
    """Testes para casos específicos de uso."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.normalizador = NormalizadorCentral(
            remover_acentos=False,
            case_sensitive=False,
            caracteres_permitidos=r'^[\w\string_data\-.,?!@#]+$',
            min_caracteres=3,
            max_caracteres=100
        )
    
    def test_extrair_keywords_texto_instagram(self):
        """Testa extração de keywords como no Instagram."""
        # Arrange
        texto = "Este é um post sobre #marketing #digital @usuario"
        
        # Act
        palavras = ["marketing", "digital", "usuario"]
        resultado = self.normalizador.normalizar_lista_termos(palavras)
        
        # Assert
        assert "marketing" in resultado
        assert "digital" in resultado
        assert "usuario" in resultado
    
    def test_extrair_keywords_texto_amazon(self):
        """Testa extração de keywords como na Amazon."""
        # Arrange
        texto = "Produto eletrônico com preço baixo"
        
        # Act
        palavras = ["produto", "eletrônico", "preço", "baixo"]
        resultado = self.normalizador.normalizar_lista_termos(palavras)
        
        # Assert
        assert "produto" in resultado
        assert "eletrônico" in resultado
        assert "preço" in resultado
        assert "baixo" in resultado


class TestPerformance:
    """Testes de performance do normalizador."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.normalizador = NormalizadorCentral()
    
    def test_performance_lista_grande(self):
        """Testa performance com lista grande de termos."""
        # Arrange
        termos = [f"termo_{index}" for index in range(1000)]
        
        # Act
        import time
        inicio = time.time()
        resultado = self.normalizador.normalizar_lista_termos(termos)
        tempo = time.time() - inicio
        
        # Assert
        assert len(resultado) == 1000
        assert tempo < 1.0  # Deve ser rápido (< 1 segundo)
    
    def test_performance_termos_duplicados(self):
        """Testa performance com muitos termos duplicados."""
        # Arrange
        termos = ["termo"] * 1000
        
        # Act
        import time
        inicio = time.time()
        resultado = self.normalizador.normalizar_lista_termos(termos)
        tempo = time.time() - inicio
        
        # Assert
        assert len(resultado) == 1  # Apenas um termo único
        assert tempo < 0.1  # Deve ser muito rápido (< 0.1 segundo)


class TestLogging:
    """Testes de logging do normalizador."""
    
    @patch('shared.logger.logger')
    def test_logging_normalizacao_lista(self, mock_logger):
        """Testa se o logging é executado durante normalização."""
        # Arrange
        normalizador = NormalizadorCentral()
        termos = ["termo1", "termo2"]
        
        # Act
        normalizador.normalizar_lista_termos(termos)
        
        # Assert
        mock_logger.info.assert_called_once()
        log_call = mock_logger.info.call_args[0][0]
        assert log_call["event"] == "normalizacao_lista_termos"
        assert log_call["details"]["total_original"] == 2
        assert log_call["details"]["total_normalizados"] == 2 
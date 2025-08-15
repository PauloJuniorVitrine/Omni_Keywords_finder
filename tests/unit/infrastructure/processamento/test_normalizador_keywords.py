from typing import Dict, List, Optional, Any
"""
Testes unitários para o módulo NormalizadorKeywords.
Testa normalização de termos, deduplicação e validação de configuração.
"""
import pytest
from datetime import datetime
from domain.models import Keyword, IntencaoBusca
from infrastructure.processamento.normalizador_keywords import NormalizadorKeywords


class TestNormalizadorKeywords:
    """Testes para a classe NormalizadorKeywords."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.normalizador = NormalizadorKeywords()
        self.normalizador_acentos = NormalizadorKeywords(remover_acentos=True)
        self.normalizador_case_sensitive = NormalizadorKeywords(case_sensitive=True)
        
    def test_inicializacao_padrao(self):
        """Testa inicialização com configurações padrão."""
        normalizador = NormalizadorKeywords()
        
        assert normalizador.remover_acentos is False
        assert normalizador.case_sensitive is False
        assert normalizador.caracteres_permitidos == r'^[\w\string_data\-.,?!]+$'
        
    def test_inicializacao_customizada(self):
        """Testa inicialização com configurações customizadas."""
        normalizador = NormalizadorKeywords(
            remover_acentos=True,
            case_sensitive=True,
            caracteres_permitidos=r'^[a-data\string_data]+$'
        )
        
        assert normalizador.remover_acentos is True
        assert normalizador.case_sensitive is True
        assert normalizador.caracteres_permitidos == r'^[a-data\string_data]+$'
        
    def test_normalizar_termo_basico(self):
        """Testa normalização básica de termo."""
        termo = "  Palavra   Chave  "
        resultado = self.normalizador.normalizar_termo(termo)
        
        assert resultado == "palavra chave"
        
    def test_normalizar_termo_com_acentos(self):
        """Testa normalização com remoção de acentos."""
        termo = "Palavra-chave com acentuação"
        resultado = self.normalizador_acentos.normalizar_termo(termo)
        
        assert resultado == "palavra-chave com acentuacao"
        
    def test_normalizar_termo_case_sensitive(self):
        """Testa normalização preservando case."""
        termo = "PALAVRA Chave"
        resultado = self.normalizador_case_sensitive.normalizar_termo(termo)
        
        assert resultado == "PALAVRA Chave"
        
    def test_normalizar_termo_caracteres_invalidos(self):
        """Testa rejeição de caracteres inválidos."""
        termo = "palavra@#$%"
        resultado = self.normalizador.normalizar_termo(termo)
        
        assert resultado == ""
        
    def test_normalizar_termo_vazio(self):
        """Testa normalização de termo vazio."""
        resultado = self.normalizador.normalizar_termo("")
        assert resultado == ""
        
        resultado = self.normalizador.normalizar_termo(None)
        assert resultado == ""
        
    def test_normalizar_lista_deduplicacao(self):
        """Testa deduplicação na normalização de lista."""
        keywords = [
            Keyword(termo="palavra chave", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL),
            Keyword(termo="  PALAVRA   CHAVE  ", volume_busca=200, cpc=2.0, concorrencia=0.6, intencao=IntencaoBusca.COMERCIAL),
            Keyword(termo="outra palavra", volume_busca=300, cpc=3.0, concorrencia=0.7, intencao=IntencaoBusca.TRANSACIONAL)
        ]
        
        resultado = self.normalizador.normalizar_lista(keywords)
        
        assert len(resultado) == 2  # Duplicatas removidas
        assert resultado[0].termo == "palavra chave"
        assert resultado[1].termo == "outra palavra"
        
    def test_normalizar_lista_campos_numericos(self):
        """Testa validação de campos numéricos na normalização."""
        keywords = [
            Keyword(termo="palavra", volume_busca=-10, cpc=-1.0, concorrencia=1.5, intencao=IntencaoBusca.INFORMACIONAL),
            Keyword(termo="outra", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.COMERCIAL)
        ]
        
        resultado = self.normalizador.normalizar_lista(keywords)
        
        assert len(resultado) == 2
        assert resultado[0].volume_busca == 0  # Negativo normalizado para 0
        assert resultado[0].cpc == 0  # Negativo normalizado para 0
        assert resultado[0].concorrencia == 1.0  # > 1 normalizado para 1
        assert resultado[1].volume_busca == 100  # Mantido
        assert resultado[1].cpc == 1.0  # Mantido
        assert resultado[1].concorrencia == 0.5  # Mantido
        
    def test_normalizar_lista_preserva_metadados(self):
        """Testa preservação de metadados na normalização."""
        data_coleta = datetime.utcnow()
        keyword = Keyword(
            termo="  PALAVRA   CHAVE  ",
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL,
            score=0.8,
            justificativa="Teste",
            fonte="teste",
            data_coleta=data_coleta
        )
        
        resultado = self.normalizador.normalizar_lista([keyword])
        
        assert len(resultado) == 1
        kw_resultado = resultado[0]
        assert kw_resultado.termo == "palavra chave"
        assert kw_resultado.volume_busca == 100
        assert kw_resultado.cpc == 1.0
        assert kw_resultado.concorrencia == 0.5
        assert kw_resultado.intencao == IntencaoBusca.INFORMACIONAL
        assert kw_resultado.score == 0.8
        assert kw_resultado.justificativa == "Teste"
        assert kw_resultado.fonte == "teste"
        assert kw_resultado.data_coleta == data_coleta
        
    def test_normalizar_lista_vazia(self):
        """Testa normalização de lista vazia."""
        resultado = self.normalizador.normalizar_lista([])
        assert resultado == []
        
    def test_normalizar_lista_termos_invalidos(self):
        """Testa normalização com termos inválidos."""
        keywords = [
            Keyword(termo="palavra válida", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL),
            Keyword(termo="", volume_busca=200, cpc=2.0, concorrencia=0.6, intencao=IntencaoBusca.COMERCIAL),
            Keyword(termo="palavra@#$%", volume_busca=300, cpc=3.0, concorrencia=0.7, intencao=IntencaoBusca.TRANSACIONAL),
            Keyword(termo="outra válida", volume_busca=400, cpc=4.0, concorrencia=0.8, intencao=IntencaoBusca.NAVEGACIONAL)
        ]
        
        resultado = self.normalizador.normalizar_lista(keywords)
        
        assert len(resultado) == 2  # Apenas termos válidos
        assert resultado[0].termo == "palavra valida"
        assert resultado[1].termo == "outra valida"
        
    def test_validar_configuracao_valida(self):
        """Testa validação de configuração válida."""
        assert self.normalizador.validar_configuracao() is True
        
    def test_validar_configuracao_invalida(self):
        """Testa validação de configuração inválida."""
        normalizador_invalido = NormalizadorKeywords(caracteres_permitidos=r'[invalid regex')
        
        assert normalizador_invalido.validar_configuracao() is False
        
    def test_normalizar_termo_caracteres_especiais_permitidos(self):
        """Testa normalização com caracteres especiais permitidos."""
        termo = "palavra-chave, com pontos. E interrogação?"
        resultado = self.normalizador.normalizar_termo(termo)
        
        assert resultado == "palavra-chave, com pontos. e interrogacao?"
        
    def test_normalizar_termo_espacos_multiplos(self):
        """Testa normalização de espaços múltiplos."""
        termo = "palavra    com    espaços    múltiplos"
        resultado = self.normalizador.normalizar_termo(termo)
        
        assert resultado == "palavra com espacos multiplos"
        
    def test_normalizar_lista_imutabilidade(self):
        """Testa que a normalização não altera objetos originais."""
        keyword_original = Keyword(
            termo="  PALAVRA   ORIGINAL  ",
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        termo_original = keyword_original.termo
        volume_original = keyword_original.volume_busca
        
        resultado = self.normalizador.normalizar_lista([keyword_original])
        
        # Objeto original não deve ser alterado
        assert keyword_original.termo == termo_original
        assert keyword_original.volume_busca == volume_original
        
        # Resultado deve ser normalizado
        assert resultado[0].termo == "palavra original"
        assert resultado[0].volume_busca == 100 
"""
Testes Unitários para Base Keyword (Keyword)
Classe base para Keywords - Omni Keywords Finder

Prompt: Implementação de testes unitários para classe Keyword
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from domain.models import Keyword, IntencaoBusca


class TestBaseKeyword:
    """Testes para classe Keyword (Base Keyword)"""
    
    @pytest.fixture
    def sample_keyword_data(self):
        """Dados de exemplo para criação de keyword"""
        return {
            "termo": "palavra chave teste",
            "volume_busca": 1000,
            "cpc": 1.50,
            "concorrencia": 0.7,
            "intencao": IntencaoBusca.INFORMACIONAL,
            "score": 85.5,
            "justificativa": "Teste de keyword",
            "fonte": "google_ads",
            "data_coleta": datetime.now()
        }
    
    @pytest.fixture
    def sample_keyword(self, sample_keyword_data):
        """Instância de Keyword para testes"""
        return Keyword(**sample_keyword_data)
    
    def test_keyword_initialization(self, sample_keyword_data):
        """Testa inicialização básica de Keyword"""
        keyword = Keyword(**sample_keyword_data)
        
        assert keyword.termo == "palavra chave teste"
        assert keyword.volume_busca == 1000
        assert keyword.cpc == 1.50
        assert keyword.concorrencia == 0.7
        assert keyword.intencao == IntencaoBusca.INFORMACIONAL
        assert keyword.score == 85.5
        assert keyword.justificativa == "Teste de keyword"
        assert keyword.fonte == "google_ads"
        assert isinstance(keyword.data_coleta, datetime)
        assert keyword.ordem_no_cluster == -1
        assert keyword.fase_funil == ""
        assert keyword.nome_artigo == ""
    
    def test_keyword_initialization_with_defaults(self):
        """Testa inicialização com valores padrão"""
        keyword = Keyword(
            termo="teste",
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        assert keyword.termo == "teste"
        assert keyword.volume_busca == 100
        assert keyword.cpc == 1.0
        assert keyword.concorrencia == 0.5
        assert keyword.intencao == IntencaoBusca.INFORMACIONAL
        assert keyword.score == 0.0
        assert keyword.justificativa == ""
        assert keyword.fonte == ""
        assert isinstance(keyword.data_coleta, datetime)
    
    def test_keyword_initialization_with_ordem_and_fase(self):
        """Testa inicialização com ordem no cluster e fase do funil"""
        keyword = Keyword(
            termo="teste",
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL,
            ordem_no_cluster=2,
            fase_funil="descoberta"
        )
        
        assert keyword.ordem_no_cluster == 2
        assert keyword.fase_funil == "descoberta"
        assert keyword.nome_artigo == "Artigo3"  # ordem_no_cluster + 1
    
    def test_keyword_validation_termo_none(self):
        """Testa validação com termo None"""
        with pytest.raises(ValueError, match="Termo não pode ser vazio"):
            Keyword(
                termo=None,
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
    
    def test_keyword_validation_termo_empty(self):
        """Testa validação com termo vazio"""
        with pytest.raises(ValueError, match="Termo não pode ser vazio"):
            Keyword(
                termo="",
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
    
    def test_keyword_validation_termo_whitespace(self):
        """Testa validação com termo apenas espaços"""
        with pytest.raises(ValueError, match="Termo não pode ser vazio"):
            Keyword(
                termo="   ",
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
    
    def test_keyword_validation_termo_too_long(self):
        """Testa validação com termo muito longo"""
        long_termo = "a" * 101
        with pytest.raises(ValueError, match="Termo não pode ter mais de 100 caracteres"):
            Keyword(
                termo=long_termo,
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
    
    def test_keyword_validation_volume_negativo(self):
        """Testa validação com volume de busca negativo"""
        with pytest.raises(ValueError, match="Volume de busca não pode ser negativo"):
            Keyword(
                termo="teste",
                volume_busca=-100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
    
    def test_keyword_validation_concorrencia_invalid(self):
        """Testa validação com concorrência inválida"""
        with pytest.raises(ValueError, match="Concorrência deve estar entre 0 e 1"):
            Keyword(
                termo="teste",
                volume_busca=100,
                cpc=1.0,
                concorrencia=1.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
    
    def test_keyword_validation_cpc_negativo(self):
        """Testa validação com CPC negativo"""
        with pytest.raises(ValueError, match="CPC não pode ser negativo"):
            Keyword(
                termo="teste",
                volume_busca=100,
                cpc=-1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
    
    def test_keyword_validation_intencao_invalid(self):
        """Testa validação com intenção inválida"""
        with pytest.raises(ValueError, match="Intenção de busca inválida"):
            Keyword(
                termo="teste",
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao="intencao_invalida"
            )
    
    def test_keyword_validation_special_characters(self):
        """Testa validação com caracteres especiais não permitidos"""
        with pytest.raises(ValueError, match="Termo contém caracteres especiais não permitidos"):
            Keyword(
                termo="teste@#$%",
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
    
    def test_keyword_validation_termo_normalization(self):
        """Testa normalização do termo (strip)"""
        keyword = Keyword(
            termo="  teste normalizado  ",
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        assert keyword.termo == "teste normalizado"
    
    def test_keyword_validation_allowed_special_characters(self):
        """Testa caracteres especiais permitidos"""
        keyword = Keyword(
            termo="teste-com-hifen, ponto. e virgula;",
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        assert keyword.termo == "teste-com-hifen, ponto. e virgula;"
    
    def test_keyword_equality(self, sample_keyword):
        """Testa comparação de igualdade entre keywords"""
        keyword1 = Keyword(
            termo="TESTE",
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        keyword2 = Keyword(
            termo="teste",
            volume_busca=200,
            cpc=2.0,
            concorrencia=0.8,
            intencao=IntencaoBusca.TRANSACIONAL
        )
        
        # Deve ser igual (case insensitive)
        assert keyword1 == keyword2
        
        # Deve ter hash igual
        assert hash(keyword1) == hash(keyword2)
    
    def test_keyword_inequality(self, sample_keyword):
        """Testa comparação de desigualdade entre keywords"""
        keyword1 = Keyword(
            termo="teste1",
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        keyword2 = Keyword(
            termo="teste2",
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        assert keyword1 != keyword2
        assert hash(keyword1) != hash(keyword2)
    
    def test_keyword_equality_with_other_types(self, sample_keyword):
        """Testa comparação com outros tipos"""
        assert sample_keyword != "string"
        assert sample_keyword != 123
        assert sample_keyword != None
    
    def test_calcular_score_success(self, sample_keyword):
        """Testa cálculo de score bem-sucedido"""
        weights = {
            "volume": 0.4,
            "cpc": 0.3,
            "intencao": 0.2,
            "concorrencia": 0.1
        }
        
        score = sample_keyword.calcular_score(weights)
        
        # Verificar se score foi calculado
        assert isinstance(score, float)
        assert score > 0
        
        # Verificar se justificativa foi gerada
        assert "Score =" in sample_keyword.justificativa
        assert "volume(1000)" in sample_keyword.justificativa
        assert "cpc(1.5)" in sample_keyword.justificativa
        assert "intencao(0.5)" in sample_keyword.justificativa
        assert "concorrencia(0.7)" in sample_keyword.justificativa
    
    def test_calcular_score_comercial_intention(self):
        """Testa cálculo de score com intenção comercial"""
        keyword = Keyword(
            termo="comprar produto",
            volume_busca=1000,
            cpc=2.0,
            concorrencia=0.8,
            intencao=IntencaoBusca.COMERCIAL
        )
        
        weights = {
            "volume": 0.4,
            "cpc": 0.3,
            "intencao": 0.2,
            "concorrencia": 0.1
        }
        
        score = keyword.calcular_score(weights)
        
        # Intenção comercial deve ter valor 1.0
        assert "intencao(1.0)" in keyword.justificativa
    
    def test_calcular_score_transacional_intention(self):
        """Testa cálculo de score com intenção transacional"""
        keyword = Keyword(
            termo="contratar serviço",
            volume_busca=1000,
            cpc=2.0,
            concorrencia=0.8,
            intencao=IntencaoBusca.TRANSACIONAL
        )
        
        weights = {
            "volume": 0.4,
            "cpc": 0.3,
            "intencao": 0.2,
            "concorrencia": 0.1
        }
        
        score = keyword.calcular_score(weights)
        
        # Intenção transacional deve ter valor 1.0
        assert "intencao(1.0)" in keyword.justificativa
    
    def test_calcular_score_with_default_weights(self, sample_keyword):
        """Testa cálculo de score com pesos padrão"""
        score = sample_keyword.calcular_score({})
        
        # Deve usar pesos padrão
        assert "0.4*volume" in sample_keyword.justificativa
        assert "0.3*cpc" in sample_keyword.justificativa
        assert "0.2*intencao" in sample_keyword.justificativa
        assert "0.1*concorrencia" in sample_keyword.justificativa
    
    @patch('domain.models.logger')
    def test_calcular_score_with_error(self, mock_logger, sample_keyword):
        """Testa cálculo de score com erro"""
        # Simular erro ao acessar atributo
        with patch.object(sample_keyword, 'volume_busca', side_effect=Exception("Erro")):
            with pytest.raises(Exception):
                sample_keyword.calcular_score({})
            
            mock_logger.error.assert_called_once()
    
    def test_to_dict_basic(self, sample_keyword):
        """Testa conversão para dicionário básica"""
        data = sample_keyword.to_dict()
        
        assert data["termo"] == "palavra chave teste"
        assert data["volume_busca"] == 1000
        assert data["cpc"] == 1.50
        assert data["concorrencia"] == 0.7
        assert data["intencao"] == "informacional"
        assert data["score"] == 85.5
        assert data["justificativa"] == "Teste de keyword"
        assert data["fonte"] == "google_ads"
        assert data["data_coleta"] is not None
    
    def test_to_dict_with_ordem_and_fase(self):
        """Testa conversão para dicionário com ordem e fase"""
        keyword = Keyword(
            termo="teste",
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL,
            ordem_no_cluster=2,
            fase_funil="descoberta"
        )
        
        data = keyword.to_dict()
        
        assert data["ordem_no_cluster"] == 2
        assert data["fase_funil"] == "descoberta"
        assert data["nome_artigo"] == "Artigo3"
    
    def test_to_dict_without_ordem_and_fase(self, sample_keyword):
        """Testa conversão para dicionário sem ordem e fase"""
        data = sample_keyword.to_dict()
        
        # Não deve incluir campos opcionais se não definidos
        assert "ordem_no_cluster" not in data
        assert "fase_funil" not in data
        assert "nome_artigo" not in data
    
    def test_from_dict_basic(self):
        """Testa criação a partir de dicionário básico"""
        data = {
            "termo": "teste from dict",
            "volume_busca": 500,
            "cpc": 1.25,
            "concorrencia": 0.6,
            "intencao": "transacional",
            "score": 90.0,
            "justificativa": "Teste from dict",
            "fonte": "google_trends",
            "data_coleta": datetime.now().isoformat()
        }
        
        keyword = Keyword.from_dict(data)
        
        assert keyword.termo == "teste from dict"
        assert keyword.volume_busca == 500
        assert keyword.cpc == 1.25
        assert keyword.concorrencia == 0.6
        assert keyword.intencao == IntencaoBusca.TRANSACIONAL
        assert keyword.score == 90.0
        assert keyword.justificativa == "Teste from dict"
        assert keyword.fonte == "google_trends"
        assert isinstance(keyword.data_coleta, datetime)
    
    def test_from_dict_with_ordem_and_fase(self):
        """Testa criação a partir de dicionário com ordem e fase"""
        data = {
            "termo": "teste",
            "volume_busca": 100,
            "cpc": 1.0,
            "concorrencia": 0.5,
            "intencao": "informacional",
            "ordem_no_cluster": 3,
            "fase_funil": "consideracao",
            "nome_artigo": "Artigo4"
        }
        
        keyword = Keyword.from_dict(data)
        
        assert keyword.ordem_no_cluster == 3
        assert keyword.fase_funil == "consideracao"
        assert keyword.nome_artigo == "Artigo4"
    
    def test_from_dict_with_invalid_intention(self):
        """Testa criação a partir de dicionário com intenção inválida"""
        data = {
            "termo": "teste",
            "volume_busca": 100,
            "cpc": 1.0,
            "concorrencia": 0.5,
            "intencao": "intencao_invalida"
        }
        
        keyword = Keyword.from_dict(data)
        
        # Deve usar intenção padrão
        assert keyword.intencao == IntencaoBusca.INFORMACIONAL
    
    def test_from_dict_with_missing_data(self):
        """Testa criação a partir de dicionário com dados faltantes"""
        data = {
            "termo": "teste"
        }
        
        keyword = Keyword.from_dict(data)
        
        # Deve usar valores padrão
        assert keyword.volume_busca == 0
        assert keyword.cpc == 0.0
        assert keyword.concorrencia == 0.0
        assert keyword.intencao == IntencaoBusca.INFORMACIONAL
        assert keyword.score == 0.0
        assert keyword.justificativa == ""
        assert keyword.fonte == ""
        assert isinstance(keyword.data_coleta, datetime)
    
    def test_from_dict_with_enum_intention(self):
        """Testa criação a partir de dicionário com intenção como enum"""
        data = {
            "termo": "teste",
            "volume_busca": 100,
            "cpc": 1.0,
            "concorrencia": 0.5,
            "intencao": IntencaoBusca.TRANSACIONAL
        }
        
        keyword = Keyword.from_dict(data)
        
        assert keyword.intencao == IntencaoBusca.TRANSACIONAL
    
    def test_normalizar_termo(self):
        """Testa normalização de termos"""
        # Teste com termo normal
        assert Keyword.normalizar_termo("Teste") == "teste"
        
        # Teste com espaços
        assert Keyword.normalizar_termo("  Teste  ") == "teste"
        
        # Teste com None
        assert Keyword.normalizar_termo(None) == ""
        
        # Teste com string vazia
        assert Keyword.normalizar_termo("") == ""
        
        # Teste com apenas espaços
        assert Keyword.normalizar_termo("   ") == ""


class TestBaseKeywordIntegration:
    """Testes de integração para classe Keyword"""
    
    def test_keyword_in_set_operations(self):
        """Testa uso de Keyword em operações de set"""
        keyword1 = Keyword(
            termo="teste",
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        keyword2 = Keyword(
            termo="TESTE",
            volume_busca=200,
            cpc=2.0,
            concorrencia=0.8,
            intencao=IntencaoBusca.TRANSACIONAL
        )
        keyword3 = Keyword(
            termo="outro",
            volume_busca=300,
            cpc=3.0,
            concorrencia=0.9,
            intencao=IntencaoBusca.COMERCIAL
        )
        
        # Criar set de keywords
        keyword_set = {keyword1, keyword2, keyword3}
        
        # Deve ter apenas 2 elementos (keyword1 e keyword2 são iguais)
        assert len(keyword_set) == 2
        
        # Verificar se keyword1 está no set
        assert keyword1 in keyword_set
        
        # Verificar se keyword2 está no set (mesmo sendo diferente)
        assert keyword2 in keyword_set
    
    def test_keyword_serialization_cycle(self):
        """Testa ciclo completo de serialização/deserialização"""
        original_keyword = Keyword(
            termo="teste serialização",
            volume_busca=1000,
            cpc=1.75,
            concorrencia=0.6,
            intencao=IntencaoBusca.TRANSACIONAL,
            score=92.5,
            justificativa="Teste de serialização",
            fonte="google_ads",
            ordem_no_cluster=2,
            fase_funil="descoberta"
        )
        
        # Serializar
        data = original_keyword.to_dict()
        
        # Deserializar
        restored_keyword = Keyword.from_dict(data)
        
        # Verificar se são iguais
        assert original_keyword.termo == restored_keyword.termo
        assert original_keyword.volume_busca == restored_keyword.volume_busca
        assert original_keyword.cpc == restored_keyword.cpc
        assert original_keyword.concorrencia == restored_keyword.concorrencia
        assert original_keyword.intencao == restored_keyword.intencao
        assert original_keyword.score == restored_keyword.score
        assert original_keyword.justificativa == restored_keyword.justificativa
        assert original_keyword.fonte == restored_keyword.fonte
        assert original_keyword.ordem_no_cluster == restored_keyword.ordem_no_cluster
        assert original_keyword.fase_funil == restored_keyword.fase_funil
        assert original_keyword.nome_artigo == restored_keyword.nome_artigo


class TestBaseKeywordErrorHandling:
    """Testes de tratamento de erros para classe Keyword"""
    
    def test_keyword_with_all_invalid_data(self):
        """Testa criação com todos os dados inválidos"""
        with pytest.raises(ValueError):
            Keyword(
                termo="",  # vazio
                volume_busca=-100,  # negativo
                cpc=-1.0,  # negativo
                concorrencia=1.5,  # > 1
                intencao="invalid"  # inválido
            )
    
    def test_keyword_with_special_characters_in_all_fields(self):
        """Testa criação com caracteres especiais em todos os campos"""
        # Apenas o termo é validado para caracteres especiais
        keyword = Keyword(
            termo="teste-normal",  # válido
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        assert keyword.termo == "teste-normal"
    
    def test_keyword_edge_cases(self):
        """Testa casos extremos de criação de keyword"""
        # Valores mínimos válidos
        keyword = Keyword(
            termo="a",  # termo mínimo
            volume_busca=0,  # volume mínimo
            cpc=0.0,  # CPC mínimo
            concorrencia=0.0,  # concorrência mínima
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        assert keyword.termo == "a"
        assert keyword.volume_busca == 0
        assert keyword.cpc == 0.0
        assert keyword.concorrencia == 0.0
        
        # Valores máximos válidos
        long_termo = "a" * 100  # termo máximo
        keyword2 = Keyword(
            termo=long_termo,
            volume_busca=999999999,
            cpc=999.99,
            concorrencia=1.0,
            intencao=IntencaoBusca.TRANSACIONAL
        )
        
        assert keyword2.termo == long_termo
        assert keyword2.volume_busca == 999999999
        assert keyword2.cpc == 999.99
        assert keyword2.concorrencia == 1.0


class TestBaseKeywordPerformance:
    """Testes de performance para classe Keyword"""
    
    def test_large_scale_keyword_creation(self):
        """Testa criação de grande volume de keywords"""
        import time
        
        start_time = time.time()
        
        keywords = []
        for i in range(1000):
            keyword = Keyword(
                termo=f"keyword_{i}",
                volume_busca=100 + i,
                cpc=1.0 + (i / 1000),
                concorrencia=0.5 + (i / 2000),
                intencao=IntencaoBusca.INFORMACIONAL,
                score=80.0 + (i / 100),
                justificativa=f"Justificativa {i}",
                fonte=f"fonte_{i}",
                ordem_no_cluster=i % 10,
                fase_funil="descoberta" if i % 2 == 0 else "consideracao"
            )
            keywords.append(keyword)
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        creation_time = end_time - start_time
        assert creation_time < 5.0  # Menos de 5 segundos para 1000 keywords
        
        # Verificar se todas foram criadas corretamente
        assert len(keywords) == 1000
        assert all(isinstance(kw, Keyword) for kw in keywords)
        assert all(kw.termo.startswith("keyword_") for kw in keywords)
    
    def test_large_scale_serialization(self):
        """Testa serialização de grande volume de keywords"""
        import time
        
        # Criar keywords
        keywords = []
        for i in range(1000):
            keyword = Keyword(
                termo=f"keyword_{i}",
                volume_busca=100 + i,
                cpc=1.0 + (i / 1000),
                concorrencia=0.5 + (i / 2000),
                intencao=IntencaoBusca.INFORMACIONAL,
                score=80.0 + (i / 100),
                justificativa=f"Justificativa {i}",
                fonte=f"fonte_{i}"
            )
            keywords.append(keyword)
        
        start_time = time.time()
        
        # Serializar todas
        data_list = [kw.to_dict() for kw in keywords]
        
        end_time = time.time()
        
        # Verificar performance
        serialization_time = end_time - start_time
        assert serialization_time < 2.0  # Menos de 2 segundos
        
        # Verificar se todas foram serializadas
        assert len(data_list) == 1000
        assert all(isinstance(data, dict) for data in data_list)
        assert all("termo" in data for data in data_list)


if __name__ == "__main__":
    pytest.main([__file__]) 
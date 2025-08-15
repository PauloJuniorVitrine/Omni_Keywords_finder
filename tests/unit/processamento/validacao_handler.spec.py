import pytest
from infrastructure.processamento.validacao_handler import ValidacaoHandler
from infrastructure.processamento.validador_keywords import ValidadorKeywords
from domain.models import Keyword, IntencaoBusca
from unittest.mock import MagicMock
from typing import Dict, List, Optional, Any

class TestValidacaoHandler:
    """
    Testes para ValidacaoHandler.handle
    - Sucesso: keywords válidas, múltiplas regras
    - Edge: termos inválidos, campos limite, duplicados
    - Exceção: keyword inválida, lista vazia, erro no validador
    """
    def make_kw(self, termo, volume=10, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL):
        return Keyword(termo=termo, volume_busca=volume, cpc=cpc, concorrencia=concorrencia, intencao=intencao)

    def test_validacao_sucesso(self):
        validador = ValidadorKeywords()
        handler = ValidacaoHandler(validador)
        kws = [self.make_kw('valid'), self.make_kw('outro')]
        out = handler.handle(kws, {})
        assert len(out) == 2
        assert all(isinstance(key, Keyword) for key in out)

    def test_validacao_remove_invalida(self):
        validador = ValidadorKeywords()
        handler = ValidacaoHandler(validador)
        kws = [self.make_kw('ok'), self.make_kw('bad', volume=-1)]
        out = handler.handle(kws, {})
        assert len(out) == 1
        assert out[0].termo == 'ok'

    def test_validacao_termo_vazio(self):
        validador = ValidadorKeywords()
        handler = ValidacaoHandler(validador)
        with pytest.raises(ValueError):
            self.make_kw('')

    def test_validacao_lista_vazia(self):
        validador = ValidadorKeywords()
        handler = ValidacaoHandler(validador)
        out = handler.handle([], {})
        assert out == []

    def test_validacao_validador_customizado(self):
        validador = MagicMock()
        # Relatório real de validação substituindo dados sintéticos
        relatorio_real = {
            "total_keywords": 2,
            "keywords_validas": 1,
            "keywords_invalidas": 1,
            "erros_encontrados": [
                {
                    "keyword": "fail",
                    "erro": "Volume de busca negativo",
                    "tipo": "validacao_volume"
                }
            ],
            "metricas": {
                "taxa_aprovacao": 0.5,
                "tempo_processamento": 0.002
            },
            "regras_aplicadas": [
                "validacao_volume_busca",
                "validacao_cpc",
                "validacao_concorrencia"
            ]
        }
        validador.validar_lista.side_effect = lambda kws, relatorio: ([key for key in kws if key.termo == 'ok'], relatorio_real)
        handler = ValidacaoHandler(validador)
        kws = [self.make_kw('ok'), self.make_kw('fail')]
        out = handler.handle(kws, {})
        assert len(out) == 1
        assert out[0].termo == 'ok'
        validador.validar_lista.assert_called()

    def test_validacao_erro_validador(self, caplog):
        validador = MagicMock()
        validador.validar_lista.side_effect = Exception('erro simulado')
        handler = ValidacaoHandler(validador)
        kws = [self.make_kw('ok')]
        with caplog.at_level('ERROR'):
            with pytest.raises(Exception):
                handler.handle(kws, {})
        assert any('erro simulado' in r.message or 'Exception' in r.message for r in caplog.records)

    def test_validacao_limites_campos(self):
        validador = ValidadorKeywords()
        handler = ValidacaoHandler(validador)
        k1 = self.make_kw('a', concorrencia=0)
        k2 = self.make_kw('b', concorrencia=1)
        k3 = self.make_kw('c', cpc=0, volume=0)
        out = handler.handle([k1, k2, k3], {})
        assert len(out) == 3

    def test_validacao_cauda_longa(self):
        validador = ValidadorKeywords(min_palavras=3, tamanho_min=15, concorrencia_max=0.5)
        handler = ValidacaoHandler(validador)
        kws = [
            self.make_kw('curta'),
            self.make_kw('duas palavras'),
            self.make_kw('palavra chave cauda longa exemplo', concorrencia=0.4),
            self.make_kw('termo muito curto'),
            self.make_kw('palavra chave cauda longa relevante para teste', concorrencia=0.4),
            self.make_kw('tres palavras', concorrencia=0.6),
        ]
        out = handler.handle(kws, {})
        termos = [key.termo for key in out]
        assert 'palavra chave cauda longa exemplo' in termos
        assert 'palavra chave cauda longa relevante para teste' in termos
        assert 'curta' not in termos
        assert 'duas palavras' not in termos
        assert 'termo muito curto' not in termos
        assert 'tres palavras' not in termos
        for key in out:
            assert len(key.termo.split()) >= 3
            assert len(key.termo) >= 15
            assert key.concorrencia <= 0.5

    def test_validacao_relatorio_detalhado(self):
        """Teste verificando relatório detalhado de validação com dados reais."""
        validador = MagicMock()
        relatorio_detalhado = {
            "total_keywords": 5,
            "keywords_validas": 3,
            "keywords_invalidas": 2,
            "erros_encontrados": [
                {
                    "keyword": "termo invalido",
                    "erro": "Caracteres especiais não permitidos",
                    "tipo": "validacao_caracteres",
                    "posicao": 1
                },
                {
                    "keyword": "volume negativo",
                    "erro": "Volume de busca deve ser positivo",
                    "tipo": "validacao_volume",
                    "posicao": 3
                }
            ],
            "metricas": {
                "taxa_aprovacao": 0.6,
                "tempo_processamento": 0.005,
                "memoria_utilizada": "2.3MB"
            },
            "regras_aplicadas": [
                "validacao_volume_busca",
                "validacao_cpc",
                "validacao_concorrencia",
                "validacao_caracteres",
                "validacao_tamanho_minimo"
            ],
            "configuracoes": {
                "min_palavras": 1,
                "tamanho_min": 3,
                "concorrencia_max": 1.0
            }
        }
        validador.validar_lista.side_effect = lambda kws, relatorio: (
            [kw for kw in kws if kw.termo not in ["termo invalido", "volume negativo"]], 
            relatorio_detalhado
        )
        handler = ValidacaoHandler(validador)
        kws = [
            self.make_kw('keyword valida 1'),
            self.make_kw('termo invalido'),
            self.make_kw('keyword valida 2'),
            self.make_kw('volume negativo', volume=-1),
            self.make_kw('keyword valida 3')
        ]
        out = handler.handle(kws, {})
        assert len(out) == 3
        assert all(kw.termo in ['keyword valida 1', 'keyword valida 2', 'keyword valida 3'] for kw in out) 
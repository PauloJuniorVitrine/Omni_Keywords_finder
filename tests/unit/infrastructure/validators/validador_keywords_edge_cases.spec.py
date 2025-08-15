"""
Testes de Edge Cases para Validador Keywords
Tracing ID: EDGE_CASES_001_20250127
Data: 2025-01-27
Versão: 1.0
Status: ✅ IMPLEMENTADO

Testes para casos extremos e comportamentos inesperados do validador de keywords.
Cobre cenários de stress, dados malformados e condições limite.
"""

import pytest
import re
import unicodedata
from typing import List, Dict, Any
from unittest.mock import Mock, patch
from datetime import datetime

from domain.models import Keyword, IntencaoBusca
from infrastructure.processamento.validador_keywords import ValidadorKeywords
from shared.logger import logger


class TestValidadorKeywordsEdgeCases:
    """
    Testes de edge cases para ValidadorKeywords.
    
    Cobre:
    - Unicode e caracteres especiais
    - Strings extremamente longas/curtas
    - Valores numéricos extremos
    - Dados malformados
    - Condições de concorrência
    - Performance com grandes volumes
    """

    @pytest.fixture
    def validador_edge_cases(self):
        """Validador configurado para edge cases."""
        return ValidadorKeywords(
            min_palavras=1,
            tamanho_min=1,
            tamanho_max=1000,
            concorrencia_max=1.0,
            score_minimo=0.0,
            volume_min=0,
            cpc_min=0.0,
            enable_semantic_validation=False
        )

    @pytest.fixture
    def validador_restritivo(self):
        """Validador com regras restritivas."""
        return ValidadorKeywords(
            min_palavras=5,
            tamanho_min=50,
            tamanho_max=100,
            concorrencia_max=0.1,
            score_minimo=0.8,
            volume_min=1000,
            cpc_min=2.0,
            enable_semantic_validation=True
        )

    # ==================== UNICODE E CARACTERES ESPECIAIS ====================

    @pytest.mark.parametrize("termo,expected_valid", [
        # Unicode normal
        ("café expresso", True),
        ("são paulo", True),
        ("açúcar refinado", True),
        
        # Unicode complexo
        ("café ☕ expresso", True),
        ("emoji 🚀 rocket", True),
        ("símbolos €$¥", True),
        
        # Caracteres especiais
        ("palavra-chave", True),
        ("palavra_chave", True),
        ("palavra.chave", True),
        ("palavra,chave", True),
        ("palavra!chave", True),
        ("palavra?chave", True),
        
        # Caracteres extremos
        ("palavra\nchave", False),  # Quebra de linha
        ("palavra\tchave", False),  # Tab
        ("palavra\rchave", False),  # Carriage return
        ("palavra\0chave", False),  # Null byte
    ])
    def test_unicode_caracteres_especiais(self, validador_edge_cases, termo, expected_valid):
        """Testa validação com caracteres Unicode e especiais."""
        keyword = Keyword(
            termo=termo,
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        is_valid, detalhes = validador_edge_cases.validar_keyword(keyword)
        assert is_valid == expected_valid, f"Termo: '{termo}' - Detalhes: {detalhes}"

    def test_unicode_normalization(self, validador_edge_cases):
        """Testa normalização Unicode."""
        # Diferentes formas de representar o mesmo caractere
        termo1 = "café"  # Unicode normal
        termo2 = unicodedata.normalize('NFD', "café")  # Decomposição
        termo3 = unicodedata.normalize('NFC', "café")  # Composição
        
        kw1 = Keyword(termo=termo1, volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
        kw2 = Keyword(termo=termo2, volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
        kw3 = Keyword(termo=termo3, volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
        
        # Todos devem ser tratados igualmente
        assert validador_edge_cases.validar_keyword(kw1)[0] == validador_edge_cases.validar_keyword(kw2)[0]
        assert validador_edge_cases.validar_keyword(kw2)[0] == validador_edge_cases.validar_keyword(kw3)[0]

    # ==================== STRINGS EXTREMAMENTE LONGAS/CURTAS ====================

    @pytest.mark.parametrize("termo,expected_valid", [
        # Strings vazias
        ("", False),
        (" ", False),
        ("\t", False),
        ("\n", False),
        
        # Strings muito curtas
        ("a", True),  # 1 caractere
        ("ab", True),  # 2 caracteres
        ("abc", True),  # 3 caracteres
        
        # Strings longas
        ("a" * 100, True),  # 100 caracteres
        ("a" * 500, True),  # 500 caracteres
        ("a" * 999, True),  # Limite máximo
        ("a" * 1000, False),  # Acima do limite
        ("a" * 10000, False),  # Muito acima do limite
    ])
    def test_tamanho_strings_extremos(self, validador_edge_cases, termo, expected_valid):
        """Testa validação com strings de tamanhos extremos."""
        keyword = Keyword(
            termo=termo,
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        is_valid, detalhes = validador_edge_cases.validar_keyword(keyword)
        assert is_valid == expected_valid, f"Tamanho: {len(termo)} - Detalhes: {detalhes}"

    def test_string_com_espacos_extremos(self, validador_edge_cases):
        """Testa strings com muitos espaços."""
        termos = [
            "   palavra   chave   ",  # Espaços no início e fim
            "palavra    chave",  # Múltiplos espaços entre palavras
            "\tpalavra\nchave\t",  # Tabs e quebras de linha
            "  \n  palavra  \t  chave  \n  ",  # Mistura de whitespace
        ]
        
        for termo in termos:
            keyword = Keyword(
                termo=termo,
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
            
            is_valid, detalhes = validador_edge_cases.validar_keyword(keyword)
            # Deve ser válido pois o validador normaliza espaços
            assert is_valid, f"Termo: '{termo}' - Detalhes: {detalhes}"

    # ==================== VALORES NUMÉRICOS EXTREMOS ====================

    @pytest.mark.parametrize("volume,cpc,concorrencia,expected_valid", [
        # Volume de busca
        (0, 1.0, 0.5, True),  # Volume mínimo
        (-1, 1.0, 0.5, False),  # Volume negativo
        (999999999, 1.0, 0.5, True),  # Volume muito alto
        (float('inf'), 1.0, 0.5, False),  # Infinito
        (float('-inf'), 1.0, 0.5, False),  # Infinito negativo
        (float('nan'), 1.0, 0.5, False),  # NaN
        
        # CPC
        (100, 0.0, 0.5, True),  # CPC mínimo
        (100, -1.0, 0.5, False),  # CPC negativo
        (100, 999.99, 0.5, True),  # CPC alto
        (100, float('inf'), 0.5, False),  # CPC infinito
        
        # Concorrência
        (100, 1.0, 0.0, True),  # Concorrência mínima
        (100, 1.0, 1.0, True),  # Concorrência máxima
        (100, 1.0, -0.1, False),  # Concorrência negativa
        (100, 1.0, 1.1, False),  # Concorrência acima de 1
    ])
    def test_valores_numericos_extremos(self, validador_edge_cases, volume, cpc, concorrencia, expected_valid):
        """Testa validação com valores numéricos extremos."""
        keyword = Keyword(
            termo="palavra chave teste",
            volume_busca=volume,
            cpc=cpc,
            concorrencia=concorrencia,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        is_valid, detalhes = validador_edge_cases.validar_keyword(keyword)
        assert is_valid == expected_valid, f"Volume: {volume}, CPC: {cpc}, Concorrência: {concorrencia} - Detalhes: {detalhes}"

    # ==================== DADOS MALFORMADOS ====================

    def test_keyword_none(self, validador_edge_cases):
        """Testa validação com keyword None."""
        with pytest.raises(AttributeError):
            validador_edge_cases.validar_keyword(None)

    def test_atributos_none(self, validador_edge_cases):
        """Testa validação com atributos None."""
        keyword = Keyword(
            termo=None,  # Termo None
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        is_valid, detalhes = validador_edge_cases.validar_keyword(keyword)
        assert not is_valid
        assert "termo_vazio" in detalhes["violacoes"]

    def test_tipos_incorretos(self, validador_edge_cases):
        """Testa validação com tipos incorretos."""
        # Mock de keyword com tipos incorretos
        mock_keyword = Mock()
        mock_keyword.termo = 123  # Inteiro em vez de string
        mock_keyword.volume_busca = "100"  # String em vez de int
        mock_keyword.cpc = "1.0"  # String em vez de float
        mock_keyword.concorrencia = "0.5"  # String em vez de float
        
        # Deve falhar na validação
        is_valid, detalhes = validador_edge_cases.validar_keyword(mock_keyword)
        assert not is_valid

    # ==================== REGEX E VALIDAÇÕES ESPECIAIS ====================

    @pytest.mark.parametrize("regex,termo,expected_valid", [
        # Regex simples
        (r"^[a-z]+$", "palavra", True),
        (r"^[a-z]+$", "PALAVRA", False),  # Maiúsculas
        (r"^[a-z]+$", "palavra123", False),  # Números
        
        # Regex complexa
        (r"^[a-z\s]+$", "palavra chave", True),
        (r"^[a-z\s]+$", "palavra-chave", False),  # Hífen
        
        # Regex com Unicode
        (r"^[\w\s]+$", "café expresso", True),
        (r"^[\w\s]+$", "café ☕", False),  # Emoji
        
        # Regex inválida
        (r"[invalid", "palavra", False),  # Regex malformada
    ])
    def test_regex_validacao(self, regex, termo, expected_valid):
        """Testa validação com regex customizada."""
        try:
            validador = ValidadorKeywords(regex_termo=regex)
            keyword = Keyword(
                termo=termo,
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
            
            is_valid, detalhes = validador.validar_keyword(keyword)
            assert is_valid == expected_valid, f"Regex: {regex}, Termo: {termo} - Detalhes: {detalhes}"
        except re.error:
            # Regex inválida deve ser tratada
            assert not expected_valid

    # ==================== BLACKLIST E WHITELIST EXTREMOS ====================

    @pytest.mark.parametrize("blacklist,whitelist,termo,expected_valid", [
        # Blacklist vazia
        ([], [], "palavra", True),
        
        # Blacklist com termo exato
        (["proibido"], [], "proibido", False),
        (["proibido"], [], "palavra proibida", True),  # Contém mas não é exato
        
        # Whitelist vazia
        ([], [], "palavra", True),
        
        # Whitelist com termo exato
        ([], ["permitido"], "permitido", True),
        ([], ["permitido"], "palavra permitida", False),  # Contém mas não é exato
        
        # Blacklist e whitelist
        (["proibido"], ["permitido"], "permitido", True),
        (["proibido"], ["permitido"], "proibido", False),
        (["proibido"], ["permitido"], "neutro", True),
        
        # Listas grandes
        (["a" + str(i) for i in range(1000)], [], "palavra", True),
        ([], ["a" + str(i) for i in range(1000)], "palavra", False),
    ])
    def test_blacklist_whitelist_extremos(self, blacklist, whitelist, termo, expected_valid):
        """Testa blacklist e whitelist com cenários extremos."""
        validador = ValidadorKeywords(
            blacklist=set(blacklist),
            whitelist=set(whitelist)
        )
        
        keyword = Keyword(
            termo=termo,
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        is_valid, detalhes = validador.validar_keyword(keyword)
        assert is_valid == expected_valid, f"Blacklist: {blacklist}, Whitelist: {whitelist}, Termo: {termo} - Detalhes: {detalhes}"

    # ==================== PERFORMANCE COM GRANDES VOLUMES ====================

    def test_performance_grande_volume(self, validador_edge_cases):
        """Testa performance com grande volume de keywords."""
        import time
        
        # Gerar 10.000 keywords
        keywords = []
        for i in range(10000):
            keyword = Keyword(
                termo=f"palavra chave teste {i}",
                volume_busca=100 + i,
                cpc=1.0 + (i / 1000),
                concorrencia=0.1 + (i / 10000),
                intencao=IntencaoBusca.INFORMACIONAL
            )
            keywords.append(keyword)
        
        # Medir tempo de validação
        start_time = time.time()
        aprovadas, rejeitadas, relatorio = validador_edge_cases.validar_lista(keywords, relatorio=True)
        end_time = time.time()
        
        tempo_execucao = end_time - start_time
        
        # Verificar performance (deve ser < 5 segundos para 10k keywords)
        assert tempo_execucao < 5.0, f"Tempo de execução muito alto: {tempo_execucao:.2f}s"
        
        # Verificar que processou todas as keywords
        assert len(aprovadas) + len(rejeitadas) == 10000
        
        # Verificar relatório
        assert relatorio is not None
        assert relatorio["total"] == 10000

    # ==================== VALIDAÇÃO SEMÂNTICA EXTREMA ====================

    @pytest.mark.parametrize("termo,expected_behavior", [
        # Termos com muitas repetições
        ("palavra palavra palavra palavra palavra", "valid"),  # Repetições
        ("a a a a a a a a a a", "valid"),  # Muitas repetições de palavra curta
        
        # Termos com caracteres repetidos
        ("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "valid"),  # Muitos 'a'
        ("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", "valid"),  # Muitos 'z'
        
        # Termos com padrões
        ("abababababababababababababababababababab", "valid"),  # Padrão repetitivo
        ("123123123123123123123123123123123123123", "valid"),  # Padrão numérico
        
        # Termos extremamente específicos
        ("como fazer bolo de chocolate caseiro passo a passo", "valid"),
        ("melhor tutorial python programação orientada a objetos", "valid"),
    ])
    def test_validacao_semantica_extrema(self, termo, expected_behavior):
        """Testa validação semântica com termos extremos."""
        validador = ValidadorKeywords(enable_semantic_validation=True)
        
        keyword = Keyword(
            termo=termo,
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        # Deve executar sem erro
        is_valid, detalhes = validador.validar_keyword_com_semantica(keyword)
        assert isinstance(is_valid, bool)
        assert "validacao_semantica" in detalhes

    # ==================== TESTES DE STRESS ====================

    def test_stress_multiplas_validacoes(self, validador_edge_cases):
        """Testa stress com múltiplas validações simultâneas."""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker(worker_id):
            """Worker para validação concorrente."""
            try:
                for i in range(100):
                    keyword = Keyword(
                        termo=f"worker_{worker_id}_keyword_{i}",
                        volume_busca=100 + i,
                        cpc=1.0 + (i / 100),
                        concorrencia=0.1 + (i / 1000),
                        intencao=IntencaoBusca.INFORMACIONAL
                    )
                    
                    is_valid, detalhes = validador_edge_cases.validar_keyword(keyword)
                    results.append(is_valid)
                    
            except Exception as e:
                errors.append(e)
        
        # Criar 10 threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        # Verificar que não houve erros
        assert len(errors) == 0, f"Erros encontrados: {errors}"
        
        # Verificar que todas as validações foram processadas
        assert len(results) == 1000  # 10 threads * 100 validações cada

    # ==================== TESTES DE MEMORY LEAK ====================

    def test_memory_usage(self, validador_edge_cases):
        """Testa uso de memória com muitas validações."""
        import gc
        import sys
        
        # Forçar garbage collection
        gc.collect()
        initial_memory = sys.getsizeof(validador_edge_cases)
        
        # Executar muitas validações
        for i in range(10000):
            keyword = Keyword(
                termo=f"keyword_{i}",
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
            
            validador_edge_cases.validar_keyword(keyword)
        
        # Forçar garbage collection novamente
        gc.collect()
        final_memory = sys.getsizeof(validador_edge_cases)
        
        # Verificar que não houve vazamento significativo de memória
        memory_increase = final_memory - initial_memory
        assert memory_increase < 1000, f"Aumento de memória muito alto: {memory_increase} bytes"

    # ==================== TESTES DE LOGGING ====================

    def test_logging_edge_cases(self, validador_edge_cases, caplog):
        """Testa logging com edge cases."""
        # Keyword com termo muito longo
        long_term = "a" * 1000
        keyword = Keyword(
            termo=long_term,
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        validador_edge_cases.validar_keyword(keyword)
        
        # Verificar que logs foram gerados
        assert len(caplog.records) > 0

    # ==================== TESTES DE CONFIGURAÇÃO EXTREMA ====================

    @pytest.mark.parametrize("config", [
        # Configuração mínima
        {
            "min_palavras": 1,
            "tamanho_min": 1,
            "tamanho_max": 1,
            "concorrencia_max": 0.0,
            "score_minimo": 0.0,
            "volume_min": 0,
            "cpc_min": 0.0
        },
        # Configuração máxima
        {
            "min_palavras": 100,
            "tamanho_min": 1000,
            "tamanho_max": 1000,
            "concorrencia_max": 1.0,
            "score_minimo": 1.0,
            "volume_min": 999999999,
            "cpc_min": 999.99
        },
        # Configuração inválida
        {
            "min_palavras": -1,
            "tamanho_min": -1,
            "tamanho_max": -1,
            "concorrencia_max": -1.0,
            "score_minimo": -1.0,
            "volume_min": -1,
            "cpc_min": -1.0
        }
    ])
    def test_configuracao_extrema(self, config):
        """Testa validador com configurações extremas."""
        try:
            validador = ValidadorKeywords(**config)
            
            # Testar com keyword básica
            keyword = Keyword(
                termo="palavra chave teste",
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL
            )
            
            # Deve executar sem erro
            is_valid, detalhes = validador.validar_keyword(keyword)
            assert isinstance(is_valid, bool)
            assert isinstance(detalhes, dict)
            
        except (ValueError, TypeError):
            # Configurações inválidas devem gerar exceção
            assert config["min_palavras"] < 0 or config["tamanho_min"] < 0

    # ==================== TESTES DE INTEGRAÇÃO EXTREMA ====================

    def test_integracao_com_outros_componentes(self, validador_edge_cases):
        """Testa integração com outros componentes em cenários extremos."""
        # Simular integração com processador
        from infrastructure.processamento.processador_keywords import ProcessadorKeywords
        
        processador = ProcessadorKeywords()
        
        # Lista grande de keywords
        keywords = []
        for i in range(1000):
            keyword = Keyword(
                termo=f"keyword_{i}",
                volume_busca=100 + i,
                cpc=1.0 + (i / 1000),
                concorrencia=0.1 + (i / 10000),
                intencao=IntencaoBusca.INFORMACIONAL
            )
            keywords.append(keyword)
        
        # Processar com validador
        try:
            resultado = processador.processar_keywords(keywords, validador=validador_edge_cases)
            assert isinstance(resultado, list)
        except Exception as e:
            # Deve lidar com erros graciosamente
            assert "erro" in str(e).lower() or "exception" in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
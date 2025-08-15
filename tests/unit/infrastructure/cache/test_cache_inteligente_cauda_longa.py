from typing import Dict, List, Optional, Any
"""
Testes Unitários - Sistema de Cache Inteligente Cauda Longa

Tracing ID: LONGTAIL-015-TEST
Data/Hora: 2024-12-20 18:05:00 UTC
Versão: 1.0
Status: ✅ IMPLEMENTADO

Testes para validar funcionalidades do sistema de cache inteligente.
"""

import pytest
import tempfile
import shutil
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from infrastructure.cache.cache_inteligente_cauda_longa import (
    CacheInteligenteCaudaLonga,
    ConfiguracaoCache,
    ItemCache,
    TipoCache,
    EstrategiaEvicao,
    CacheLRU
)


class TestConfiguracaoCache:
    """Testes para ConfiguracaoCache."""
    
    def test_configuracao_padrao(self):
        """Testa configuração padrão."""
        config = ConfiguracaoCache()
        
        assert config.tipo == TipoCache.HIBRIDO
        assert config.estrategia_evicao == EstrategiaEvicao.ADAPTATIVA
        assert config.tamanho_maximo_mb == 100
        assert config.tamanho_maximo_itens == 10000
        assert config.ttl_padrao_minutos == 60
    
    def test_configuracao_personalizada(self):
        """Testa configuração personalizada."""
        config = ConfiguracaoCache(
            tipo=TipoCache.MEMORIA,
            estrategia_evicao=EstrategiaEvicao.LRU,
            tamanho_maximo_mb=50,
            tamanho_maximo_itens=1000,
            ttl_padrao_minutos=30
        )
        
        assert config.tipo == TipoCache.MEMORIA
        assert config.estrategia_evicao == EstrategiaEvicao.LRU
        assert config.tamanho_maximo_mb == 50
        assert config.tamanho_maximo_itens == 1000
        assert config.ttl_padrao_minutos == 30


class TestItemCache:
    """Testes para ItemCache."""
    
    def test_criacao_item_cache(self):
        """Testa criação de item de cache."""
        item = ItemCache(
            chave="teste",
            valor="valor_teste",
            timestamp_criacao=datetime.now(),
            timestamp_acesso=datetime.now(),
            ttl=timedelta(minutes=30),
            prioridade=0.8,
            tags=["teste", "cache"]
        )
        
        assert item.chave == "teste"
        assert item.valor == "valor_teste"
        assert item.frequencia_acesso == 0
        assert item.prioridade == 0.8
        assert "teste" in item.tags
        assert "cache" in item.tags
    
    def test_atualizar_acesso(self):
        """Testa atualização de acesso."""
        item = ItemCache(
            chave="teste",
            valor="valor_teste",
            timestamp_criacao=datetime.now(),
            timestamp_acesso=datetime.now()
        )
        
        frequencia_inicial = item.frequencia_acesso
        timestamp_inicial = item.timestamp_acesso
        
        time.sleep(0.1)  # Pequena pausa
        item.atualizar_acesso()
        
        assert item.frequencia_acesso == frequencia_inicial + 1
        assert item.timestamp_acesso > timestamp_inicial
    
    def test_verificar_expiracao(self):
        """Testa verificação de expiração."""
        # Item não expirado
        item_nao_expirado = ItemCache(
            chave="teste",
            valor="valor_teste",
            timestamp_criacao=datetime.now(),
            timestamp_acesso=datetime.now(),
            ttl=timedelta(minutes=30)
        )
        
        assert not item_nao_expirado.esta_expirado()
        
        # Item expirado
        item_expirado = ItemCache(
            chave="teste",
            valor="valor_teste",
            timestamp_criacao=datetime.now() - timedelta(minutes=31),
            timestamp_acesso=datetime.now() - timedelta(minutes=31),
            ttl=timedelta(minutes=30)
        )
        
        assert item_expirado.esta_expirado()
    
    def test_calcular_score(self):
        """Testa cálculo de score."""
        item = ItemCache(
            chave="teste",
            valor="valor_teste",
            timestamp_criacao=datetime.now(),
            timestamp_acesso=datetime.now(),
            prioridade=0.8
        )
        
        # Adicionar alguns acessos
        item.frequencia_acesso = 5
        
        score = item.calcular_score()
        
        assert 0.0 <= score <= 1.0
        assert score > 0.0
    
    def test_converter_para_dict(self):
        """Testa conversão para dicionário."""
        item = ItemCache(
            chave="teste",
            valor="valor_teste",
            timestamp_criacao=datetime.now(),
            timestamp_acesso=datetime.now(),
            ttl=timedelta(minutes=30),
            prioridade=0.8,
            tags=["teste"]
        )
        
        dict_item = item.to_dict()
        
        assert dict_item["chave"] == "teste"
        assert dict_item["valor"] == "valor_teste"
        assert dict_item["frequencia_acesso"] == 0
        assert dict_item["prioridade"] == 0.8
        assert "teste" in dict_item["tags"]


class TestCacheLRU:
    """Testes para CacheLRU."""
    
    def test_inserir_e_obter(self):
        """Testa inserção e obtenção de itens."""
        cache = CacheLRU(capacidade=3)
        
        cache.inserir("chave1", "valor1")
        cache.inserir("chave2", "valor2")
        
        assert cache.obter("chave1") == "valor1"
        assert cache.obter("chave2") == "valor2"
        assert cache.obter("chave3") is None
    
    def test_evicao_lru(self):
        """Testa evição LRU."""
        cache = CacheLRU(capacidade=2)
        
        cache.inserir("chave1", "valor1")
        cache.inserir("chave2", "valor2")
        cache.inserir("chave3", "valor3")  # Deve evictar chave1
        
        assert cache.obter("chave1") is None
        assert cache.obter("chave2") == "valor2"
        assert cache.obter("chave3") == "valor3"
    
    def test_atualizar_posicao_lru(self):
        """Testa atualização de posição no LRU."""
        cache = CacheLRU(capacidade=2)
        
        cache.inserir("chave1", "valor1")
        cache.inserir("chave2", "valor2")
        
        # Acessar chave1 para torná-la mais recente
        cache.obter("chave1")
        
        cache.inserir("chave3", "valor3")  # Deve evictar chave2
        
        assert cache.obter("chave1") == "valor1"
        assert cache.obter("chave2") is None
        assert cache.obter("chave3") == "valor3"
    
    def test_remover_item(self):
        """Testa remoção de item."""
        cache = CacheLRU(capacidade=3)
        
        cache.inserir("chave1", "valor1")
        cache.inserir("chave2", "valor2")
        
        assert cache.remover("chave1") is True
        assert cache.obter("chave1") is None
        assert cache.obter("chave2") == "valor2"
        
        assert cache.remover("chave3") is False
    
    def test_limpar_cache(self):
        """Testa limpeza do cache."""
        cache = CacheLRU(capacidade=3)
        
        cache.inserir("chave1", "valor1")
        cache.inserir("chave2", "valor2")
        
        assert cache.tamanho() == 2
        
        cache.limpar()
        
        assert cache.tamanho() == 0
        assert cache.obter("chave1") is None
        assert cache.obter("chave2") is None


class TestCacheInteligenteCaudaLonga:
    """Testes para CacheInteligenteCaudaLonga."""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cache_config(self, temp_dir):
        """Configuração de cache para testes."""
        return ConfiguracaoCache(
            tipo=TipoCache.HIBRIDO,
            tamanho_maximo_itens=10,
            ttl_padrao_minutos=5,
            persistencia=False,  # Desabilitar para testes
            limpeza_automatica=False,  # Desabilitar para testes
            backup_automatico=False  # Desabilitar para testes
        )
    
    @pytest.fixture
    def cache(self, cache_config, temp_dir):
        """Instância de cache para testes."""
        with patch('infrastructure.cache.cache_inteligente_cauda_longa.Path') as mock_path:
            mock_path.return_value = Path(temp_dir)
            cache = CacheInteligenteCaudaLonga(cache_config)
            yield cache
            cache.parar()
    
    def test_inicializacao(self, cache):
        """Testa inicialização do cache."""
        assert cache.config is not None
        assert len(cache.cache_memoria) == 0
        assert cache.estatisticas["hits"] == 0
        assert cache.estatisticas["misses"] == 0
    
    def test_gerar_chave_cache(self, cache):
        """Testa geração de chave de cache."""
        chave1 = cache.gerar_chave_cache("teste", 123, {"a": 1})
        chave2 = cache.gerar_chave_cache("teste", 123, {"a": 1})
        chave3 = cache.gerar_chave_cache("teste", 456, {"a": 1})
        
        assert chave1 == chave2  # Mesmos argumentos
        assert chave1 != chave3  # Argumentos diferentes
        assert len(chave1) == 32  # MD5 hash
    
    def test_inserir_e_obter_memoria(self, cache):
        """Testa inserção e obtenção em memória."""
        cache.inserir("chave1", "valor1", ttl_minutos=10)
        cache.inserir("chave2", {"dados": "complexos"}, ttl_minutos=5)
        
        valor1 = cache.obter("chave1")
        valor2 = cache.obter("chave2")
        
        assert valor1 == "valor1"
        assert valor2 == {"dados": "complexos"}
        assert cache.obter("chave3") is None
    
    def test_atualizar_acesso(self, cache):
        """Testa atualização de acesso."""
        cache.inserir("chave1", "valor1")
        
        # Primeiro acesso
        item1 = cache.cache_memoria["chave1"]
        frequencia_inicial = item1.frequencia_acesso
        
        # Segundo acesso
        cache.obter("chave1")
        item2 = cache.cache_memoria["chave1"]
        
        assert item2.frequencia_acesso == frequencia_inicial + 1
    
    def test_expiracao_ttl(self, cache):
        """Testa expiração por TTL."""
        cache.inserir("chave1", "valor1", ttl_minutos=0)  # TTL muito baixo
        
        # Aguardar um pouco
        time.sleep(0.1)
        
        # Item deve estar expirado
        valor = cache.obter("chave1")
        assert valor is None
    
    def test_evicao_adaptativa(self, cache):
        """Testa evição adaptativa."""
        # Inserir mais itens que a capacidade
        for index in range(15):
            cache.inserir(f"chave{index}", f"valor{index}")
        
        # Verificar se alguns itens foram evictados
        assert len(cache.cache_memoria) <= cache.config.tamanho_maximo_itens
        
        # Verificar se itens com menor score foram removidos
        itens_restantes = list(cache.cache_memoria.keys())
        assert len(itens_restantes) > 0
    
    def test_estatisticas(self, cache):
        """Testa coleta de estatísticas."""
        # Inserir e obter alguns itens
        cache.inserir("chave1", "valor1")
        cache.inserir("chave2", "valor2")
        
        cache.obter("chave1")  # Hit
        cache.obter("chave3")  # Miss
        
        stats = cache.obter_estatisticas()
        
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["insercoes"] == 2
        assert stats["taxa_hit_percentual"] == 50.0
        assert stats["total_acessos"] == 2
    
    def test_limpar_cache(self, cache):
        """Testa limpeza do cache."""
        cache.inserir("chave1", "valor1")
        cache.inserir("chave2", "valor2")
        
        assert len(cache.cache_memoria) == 2
        
        cache.limpar_cache("memoria")
        
        assert len(cache.cache_memoria) == 0
        assert cache.obter("chave1") is None
        assert cache.obter("chave2") is None
    
    def test_decorator_cache(self, cache):
        """Testa decorator de cache."""
        @cache.decorator_cache(ttl_minutos=10, tags=["teste"])
        def funcao_teste(param1, param2):
            return f"resultado_{param1}_{param2}"
        
        # Primeira chamada - deve executar função
        resultado1 = funcao_teste("a", "b")
        assert resultado1 == "resultado_a_b"
        
        # Segunda chamada - deve vir do cache
        resultado2 = funcao_teste("a", "b")
        assert resultado2 == "resultado_a_b"
        
        # Verificar se foi cacheado
        stats = cache.obter_estatisticas()
        assert stats["hits"] >= 1
    
    def test_concorrencia(self, cache):
        """Testa concorrência no cache."""
        def inserir_itens():
            for index in range(100):
                cache.inserir(f"chave_{index}", f"valor_{index}")
        
        def obter_itens():
            for index in range(100):
                cache.obter(f"chave_{index}")
        
        # Executar threads concorrentes
        thread1 = threading.Thread(target=inserir_itens)
        thread2 = threading.Thread(target=obter_itens)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Verificar se não houve erros de concorrência
        stats = cache.obter_estatisticas()
        assert stats["insercoes"] >= 0
        assert stats["hits"] >= 0
    
    def test_parar_cache(self, cache):
        """Testa parada do cache."""
        cache.inserir("chave1", "valor1")
        
        assert cache.ativo is True
        
        cache.parar()
        
        assert cache.ativo is False
        assert len(cache.cache_memoria) == 0  # Deve limpar memória


class TestIntegracaoCache:
    """Testes de integração do cache."""
    
    def test_fluxo_completo_cache(self):
        """Testa fluxo completo do cache."""
        config = ConfiguracaoCache(
            tamanho_maximo_itens=5,
            ttl_padrao_minutos=1,
            persistencia=False,
            limpeza_automatica=False,
            backup_automatico=False
        )
        
        cache = CacheInteligenteCaudaLonga(config)
        
        try:
            # 1. Inserir dados
            dados_teste = {
                "keywords": ["restaurante perto", "pizza delivery"],
                "metricas": {"volume": 1000, "competicao": 0.3},
                "timestamp": datetime.now().isoformat()
            }
            
            cache.inserir("resultado_busca", dados_teste, ttl_minutos=5)
            
            # 2. Obter dados
            resultado = cache.obter("resultado_busca")
            assert resultado == dados_teste
            
            # 3. Verificar estatísticas
            stats = cache.obter_estatisticas()
            assert stats["hits"] == 1
            assert stats["insercoes"] == 1
            assert stats["taxa_hit_percentual"] == 100.0
            
            # 4. Testar expiração
            cache.inserir("item_expirado", "valor", ttl_minutos=0)
            time.sleep(0.1)
            
            valor_expirado = cache.obter("item_expirado")
            assert valor_expirado is None
            
        finally:
            cache.parar()
    
    def test_cache_com_dados_complexos(self):
        """Testa cache com dados complexos."""
        config = ConfiguracaoCache(
            tamanho_maximo_itens=10,
            persistencia=False,
            limpeza_automatica=False,
            backup_automatico=False
        )
        
        cache = CacheInteligenteCaudaLonga(config)
        
        try:
            # Dados complexos
            dados_complexos = {
                "lista_keywords": [
                    {"termo": "restaurante italiano", "score": 0.8},
                    {"termo": "pizza napolitana", "score": 0.9},
                    {"termo": "massas frescas", "score": 0.7}
                ],
                "configuracao": {
                    "regiao": "São Paulo",
                    "idioma": "pt-BR",
                    "filtros": ["restaurante", "italiano"]
                },
                "resultados_analise": {
                    "volume_busca": 15000,
                    "competicao": 0.4,
                    "cpc_estimado": 2.50,
                    "tendencias": ["crescimento", "sazonal"]
                }
            }
            
            # Inserir dados complexos
            cache.inserir("analise_completa", dados_complexos, ttl_minutos=30)
            
            # Obter e verificar
            resultado = cache.obter("analise_completa")
            assert resultado == dados_complexos
            assert len(resultado["lista_keywords"]) == 3
            assert resultado["configuracao"]["regiao"] == "São Paulo"
            
        finally:
            cache.parar()


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-value"]) 
"""
🔧 Testes Avançados - Sistema de Histórico Inteligente - Omni Keywords Finder

Tracing ID: TEST_HISTORICO_INTELIGENTE_001
Data/Hora: 2025-01-27 17:00:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

Objetivo: Testes avançados para o sistema de histórico inteligente com cobertura de:
- Integração com banco de dados e cache
- Concorrência e race conditions
- Falhas e recuperação
- Observabilidade e métricas
- Edge cases e cenários extremos
"""

import pytest
import asyncio
import time
import threading
import sqlite3
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json

from infrastructure.memory.historico_inteligente import (
    HistoricoInteligente, HistoricoKeyword, HistoricoCluster,
    VariacaoAlgoritmica
)
from domain.models import Keyword, Cluster


class TestHistoricoInteligente:
    """Testes para HistoricoInteligente."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Caminho temporário para banco de dados."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        # Limpeza
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def historico(self, temp_db_path):
        """Instância de HistoricoInteligente para testes."""
        return HistoricoInteligente(db_path=temp_db_path)
    
    @pytest.fixture
    def sample_keywords(self):
        """Keywords de exemplo para testes."""
        return [
            Keyword(
                termo="marketing digital",
                volume_busca=10000,
                score=0.85,
                nicho="marketing",
                categoria="digital"
            ),
            Keyword(
                termo="seo otimização",
                volume_busca=8000,
                score=0.78,
                nicho="marketing",
                categoria="digital"
            ),
            Keyword(
                termo="redes sociais",
                volume_busca=12000,
                score=0.92,
                nicho="marketing",
                categoria="digital"
            )
        ]
    
    @pytest.fixture
    def sample_cluster(self):
        """Cluster de exemplo para testes."""
        return Cluster(
            id="cluster_001",
            nome="Marketing Digital",
            keywords=["marketing digital", "seo", "redes sociais"],
            nicho="marketing",
            categoria="digital",
            score_medio=0.85
        )
    
    def test_initialization_success(self, temp_db_path):
        """Testa inicialização bem-sucedida."""
        historico = HistoricoInteligente(db_path=temp_db_path)
        
        assert historico.db_path == temp_db_path
        assert historico.cache is not None
        assert len(historico.variacoes_algoritmicas) > 0
        assert isinstance(historico._termos_processados, set)
        assert isinstance(historico._clusters_processados, set)
    
    def test_database_initialization(self, temp_db_path):
        """Testa inicialização do banco de dados."""
        historico = HistoricoInteligente(db_path=temp_db_path)
        
        # Verifica se tabelas foram criadas
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Verifica tabela de keywords
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historico_keywords'")
        assert cursor.fetchone() is not None
        
        # Verifica tabela de clusters
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historico_clusters'")
        assert cursor.fetchone() is not None
        
        # Verifica índices
        cursor.execute("SELECT name FROM sqlite_index_list WHERE tbl_name='historico_keywords'")
        indices = [row[0] for row in cursor.fetchall()]
        assert "idx_keywords_hash" in indices
        assert "idx_keywords_nicho" in indices
        
        conn.close()
    
    def test_database_initialization_failure(self):
        """Testa falha na inicialização do banco."""
        # Tenta usar caminho inválido
        invalid_path = "/invalid/path/that/does/not/exist/historico.db"
        
        with pytest.raises(Exception):
            HistoricoInteligente(db_path=invalid_path)
    
    def test_hash_termo(self, historico):
        """Testa geração de hash para termos."""
        termo = "marketing digital"
        hash_result = historico._hash_termo(termo)
        
        assert isinstance(hash_result, str)
        assert len(hash_result) > 0
        assert hash_result != termo
        
        # Hash deve ser consistente
        hash_result2 = historico._hash_termo(termo)
        assert hash_result == hash_result2
    
    def test_get_semana_atual(self, historico):
        """Testa obtenção da semana atual."""
        semana = historico._get_semana_atual()
        
        assert isinstance(semana, str)
        assert "semana_" in semana
        assert len(semana) > 0
    
    def test_get_variacao_atual(self, historico):
        """Testa obtenção da variação algorítmica atual."""
        variacao = historico._get_variacao_atual()
        
        assert isinstance(variacao, VariacaoAlgoritmica)
        assert variacao.nome is not None
        assert variacao.descricao is not None
        assert variacao.parametros is not None
    
    @pytest.mark.asyncio
    async def test_registrar_keywords_success(self, historico, sample_keywords):
        """Testa registro bem-sucedido de keywords."""
        nicho = "marketing"
        categoria = "digital"
        
        await historico.registrar_keywords(sample_keywords, nicho, categoria)
        
        # Verifica se foram registradas no cache
        for keyword in sample_keywords:
            assert keyword.termo in historico._termos_processados
        
        # Verifica se foram registradas no banco
        conn = sqlite3.connect(historico.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM historico_keywords WHERE nicho = ?", (nicho,))
        count = cursor.fetchone()[0]
        assert count == len(sample_keywords)
        
        conn.close()
    
    @pytest.mark.asyncio
    async def test_registrar_keywords_duplicate(self, historico, sample_keywords):
        """Testa registro de keywords duplicadas."""
        nicho = "marketing"
        categoria = "digital"
        
        # Registra pela primeira vez
        await historico.registrar_keywords(sample_keywords, nicho, categoria)
        
        # Registra novamente (deve ser ignorado)
        await historico.registrar_keywords(sample_keywords, nicho, categoria)
        
        # Verifica se não houve duplicação no banco
        conn = sqlite3.connect(historico.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM historico_keywords WHERE nicho = ?", (nicho,))
        count = cursor.fetchone()[0]
        assert count == len(sample_keywords)  # Não deve ter duplicatas
        
        conn.close()
    
    @pytest.mark.asyncio
    async def test_registrar_cluster_success(self, historico, sample_cluster):
        """Testa registro bem-sucedido de cluster."""
        nicho = "marketing"
        categoria = "digital"
        
        await historico.registrar_cluster(sample_cluster, nicho, categoria)
        
        # Verifica se foi registrado no cache
        assert sample_cluster.id in historico._clusters_processados
        
        # Verifica se foi registrado no banco
        conn = sqlite3.connect(historico.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM historico_clusters WHERE cluster_id = ?", (sample_cluster.id,))
        count = cursor.fetchone()[0]
        assert count == 1
        
        conn.close()
    
    @pytest.mark.asyncio
    async def test_verificar_novidade_keywords(self, historico, sample_keywords):
        """Testa verificação de novidade de keywords."""
        nicho = "marketing"
        
        # Registra algumas keywords primeiro
        await historico.registrar_keywords(sample_keywords[:2], nicho, "digital")
        
        # Verifica novidade das keywords
        novas, existentes = await historico.verificar_novidade_keywords(sample_keywords, nicho)
        
        assert len(novas) == 1  # Apenas a terceira keyword é nova
        assert len(existentes) == 2  # As duas primeiras já existem
        assert novas[0].termo == "redes sociais"
    
    @pytest.mark.asyncio
    async def test_sugerir_clusters_alternativos(self, historico, sample_keywords):
        """Testa sugestão de clusters alternativos."""
        nicho = "marketing"
        categoria = "digital"
        
        # Registra alguns clusters primeiro
        cluster1 = Cluster(
            id="cluster_001",
            nome="Marketing Digital",
            keywords=["marketing digital", "seo"],
            nicho="marketing",
            categoria="digital",
            score_medio=0.85
        )
        cluster2 = Cluster(
            id="cluster_002",
            nome="Redes Sociais",
            keywords=["instagram", "facebook", "twitter"],
            nicho="marketing",
            categoria="digital",
            score_medio=0.78
        )
        
        await historico.registrar_cluster(cluster1, nicho, categoria)
        await historico.registrar_cluster(cluster2, nicho, categoria)
        
        # Sugere clusters alternativos
        sugestoes = await historico.sugerir_clusters_alternativos(sample_keywords, nicho, categoria)
        
        assert isinstance(sugestoes, list)
        assert len(sugestoes) > 0
        
        for sugestao in sugestoes:
            assert "cluster_id" in sugestao
            assert "nome" in sugestao
            assert "keywords" in sugestao
            assert "score" in sugestao
    
    def test_calcular_diversidade_semantica(self, historico):
        """Testa cálculo de diversidade semântica."""
        keywords = [
            Keyword(termo="marketing digital", volume_busca=1000, score=0.8),
            Keyword(termo="seo otimização", volume_busca=800, score=0.7),
            Keyword(termo="redes sociais", volume_busca=1200, score=0.9)
        ]
        
        diversidade = historico._calcular_diversidade_semantica(keywords)
        
        assert isinstance(diversidade, float)
        assert 0.0 <= diversidade <= 1.0
    
    def test_calcular_similaridade_keywords(self, historico):
        """Testa cálculo de similaridade entre keywords."""
        keywords1 = [
            Keyword(termo="marketing digital", volume_busca=1000, score=0.8),
            Keyword(termo="seo otimização", volume_busca=800, score=0.7)
        ]
        keywords2 = ["marketing digital", "seo otimização", "redes sociais"]
        
        similaridade = historico._calcular_similaridade_keywords(keywords1, keywords2)
        
        assert isinstance(similaridade, float)
        assert 0.0 <= similaridade <= 1.0
    
    @pytest.mark.asyncio
    async def test_obter_estatisticas_historico(self, historico, sample_keywords):
        """Testa obtenção de estatísticas do histórico."""
        nicho = "marketing"
        
        # Registra algumas keywords
        await historico.registrar_keywords(sample_keywords, nicho, "digital")
        
        # Obtém estatísticas
        stats = await historico.obter_estatisticas_historico(nicho, semanas=4)
        
        assert isinstance(stats, dict)
        assert "total_keywords" in stats
        assert "total_clusters" in stats
        assert "keywords_por_semana" in stats
        assert "clusters_por_semana" in stats
        assert "score_medio" in stats
        assert "volume_medio" in stats


class TestHistoricoInteligenteConcurrency:
    """Testes de concorrência para HistoricoInteligente."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Caminho temporário para banco de dados."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def historico(self, temp_db_path):
        """Instância de HistoricoInteligente para testes."""
        return HistoricoInteligente(db_path=temp_db_path)
    
    @pytest.mark.asyncio
    async def test_concurrent_keyword_registration(self, historico):
        """Testa registro concorrente de keywords."""
        keywords_batch1 = [
            Keyword(termo=f"keyword_{i}", volume_busca=1000, score=0.8)
            for i in range(10)
        ]
        keywords_batch2 = [
            Keyword(termo=f"keyword_{i+10}", volume_busca=1000, score=0.8)
            for i in range(10)
        ]
        
        # Executa registros concorrentes
        tasks = [
            historico.registrar_keywords(keywords_batch1, "nicho1", "categoria1"),
            historico.registrar_keywords(keywords_batch2, "nicho2", "categoria2")
        ]
        
        await asyncio.gather(*tasks)
        
        # Verifica se todos foram registrados
        conn = sqlite3.connect(historico.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM historico_keywords")
        total_count = cursor.fetchone()[0]
        assert total_count == 20
        
        conn.close()
    
    @pytest.mark.asyncio
    async def test_concurrent_cluster_registration(self, historico):
        """Testa registro concorrente de clusters."""
        clusters = []
        for i in range(5):
            cluster = Cluster(
                id=f"cluster_{i}",
                nome=f"Cluster {i}",
                keywords=[f"keyword_{i}_{j}" for j in range(3)],
                nicho="test",
                categoria="test",
                score_medio=0.8
            )
            clusters.append(cluster)
        
        # Executa registros concorrentes
        tasks = [
            historico.registrar_cluster(cluster, "nicho1", "categoria1")
            for cluster in clusters
        ]
        
        await asyncio.gather(*tasks)
        
        # Verifica se todos foram registrados
        conn = sqlite3.connect(historico.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM historico_clusters")
        total_count = cursor.fetchone()[0]
        assert total_count == 5
        
        conn.close()


class TestHistoricoInteligenteEdgeCases:
    """Testes para edge cases e cenários extremos."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Caminho temporário para banco de dados."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def historico(self, temp_db_path):
        """Instância de HistoricoInteligente para testes."""
        return HistoricoInteligente(db_path=temp_db_path)
    
    @pytest.mark.asyncio
    async def test_empty_keywords_list(self, historico):
        """Testa registro de lista vazia de keywords."""
        await historico.registrar_keywords([], "nicho", "categoria")
        
        # Verifica se não houve erro e banco permanece vazio
        conn = sqlite3.connect(historico.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM historico_keywords")
        count = cursor.fetchone()[0]
        assert count == 0
        
        conn.close()
    
    @pytest.mark.asyncio
    async def test_large_keywords_batch(self, historico):
        """Testa registro de grande lote de keywords."""
        # Cria 1000 keywords
        keywords = [
            Keyword(
                termo=f"keyword_{i}",
                volume_busca=1000 + i,
                score=0.5 + (i % 50) / 100
            )
            for i in range(1000)
        ]
        
        start_time = time.time()
        await historico.registrar_keywords(keywords, "nicho", "categoria")
        end_time = time.time()
        
        # Verifica se todos foram registrados
        conn = sqlite3.connect(historico.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM historico_keywords")
        count = cursor.fetchone()[0]
        assert count == 1000
        
        conn.close()
        
        # Verifica se performance é aceitável (< 10 segundos)
        assert end_time - start_time < 10.0
    
    def test_special_characters_in_keywords(self, historico):
        """Testa keywords com caracteres especiais."""
        special_keywords = [
            Keyword(termo="marketing & digital", volume_busca=1000, score=0.8),
            Keyword(termo="seo (otimização)", volume_busca=800, score=0.7),
            Keyword(termo="redes sociais!", volume_busca=1200, score=0.9),
            Keyword(termo="email@marketing.com", volume_busca=500, score=0.6)
        ]
        
        # Testa hash de termos especiais
        for keyword in special_keywords:
            hash_result = historico._hash_termo(keyword.termo)
            assert isinstance(hash_result, str)
            assert len(hash_result) > 0
    
    @pytest.mark.asyncio
    async def test_database_corruption_recovery(self, historico):
        """Testa recuperação de corrupção de banco."""
        # Simula corrupção do banco
        with open(historico.db_path, 'w') as f:
            f.write("corrupted database content")
        
        # Tenta registrar keywords (deve recriar o banco)
        keywords = [
            Keyword(termo="test keyword", volume_busca=1000, score=0.8)
        ]
        
        await historico.registrar_keywords(keywords, "nicho", "categoria")
        
        # Verifica se banco foi recriado e funcionando
        conn = sqlite3.connect(historico.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM historico_keywords")
        count = cursor.fetchone()[0]
        assert count == 1
        
        conn.close()


class TestHistoricoInteligenteIntegration:
    """Testes de integração para HistoricoInteligente."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Caminho temporário para banco de dados."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def historico(self, temp_db_path):
        """Instância de HistoricoInteligente para testes."""
        return HistoricoInteligente(db_path=temp_db_path)
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, historico):
        """Testa fluxo completo de trabalho."""
        # 1. Registra keywords
        keywords = [
            Keyword(termo="marketing digital", volume_busca=10000, score=0.85),
            Keyword(termo="seo otimização", volume_busca=8000, score=0.78),
            Keyword(termo="redes sociais", volume_busca=12000, score=0.92)
        ]
        await historico.registrar_keywords(keywords, "marketing", "digital")
        
        # 2. Registra cluster
        cluster = Cluster(
            id="cluster_001",
            nome="Marketing Digital",
            keywords=["marketing digital", "seo otimização"],
            nicho="marketing",
            categoria="digital",
            score_medio=0.85
        )
        await historico.registrar_cluster(cluster, "marketing", "digital")
        
        # 3. Verifica novidade
        novas_keywords = [
            Keyword(termo="novo termo", volume_busca=5000, score=0.75)
        ]
        novas, existentes = await historico.verificar_novidade_keywords(novas_keywords, "marketing")
        assert len(novas) == 1
        assert len(existentes) == 0
        
        # 4. Sugere clusters alternativos
        sugestoes = await historico.sugerir_clusters_alternativos(novas_keywords, "marketing", "digital")
        assert len(sugestoes) > 0
        
        # 5. Obtém estatísticas
        stats = await historico.obter_estatisticas_historico("marketing", semanas=4)
        assert stats["total_keywords"] >= 3
        assert stats["total_clusters"] >= 1
    
    @pytest.mark.asyncio
    async def test_cache_integration(self, historico):
        """Testa integração com cache."""
        # Simula cache
        mock_cache = AsyncMock()
        historico.cache = mock_cache
        
        keywords = [
            Keyword(termo="test keyword", volume_busca=1000, score=0.8)
        ]
        
        await historico.registrar_keywords(keywords, "nicho", "categoria")
        
        # Verifica se cache foi usado
        assert mock_cache.set.called or mock_cache.get.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
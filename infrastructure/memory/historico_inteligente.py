"""
Sistema de Histórico Inteligente - Omni Keywords Finder

Mantém registro de keywords e clusters já processados para evitar repetição
e garantir variação algorítmica semanal.

Tracing ID: HISTORICO_INTELIGENTE_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import json
import hashlib
import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import pickle
import numpy as np
from collections import defaultdict, Counter

from domain.models import Keyword, Cluster
from shared.cache import AsyncCache
from shared.logger import logger

@dataclass
class HistoricoKeyword:
    """Registro de keyword no histórico."""
    termo: str
    hash_termo: str
    nicho: str
    categoria: str
    data_coleta: datetime
    volume_busca: int
    score: float
    cluster_id: Optional[str] = None
    semana_ano: Optional[str] = None
    variacao_algoritmica: Optional[str] = None

@dataclass
class HistoricoCluster:
    """Registro de cluster no histórico."""
    cluster_id: str
    nome: str
    keywords: List[str]
    nicho: str
    categoria: str
    data_criacao: datetime
    score_medio: float
    semana_ano: str
    variacao_algoritmica: str
    diversidade_semantica: float

@dataclass
class VariacaoAlgoritmica:
    """Configuração de variação algorítmica."""
    nome: str
    descricao: str
    parametros: Dict[str, Any]
    peso_diversidade: float
    peso_novidade: float
    peso_tendencia: float

class HistoricoInteligente:
    """
    Sistema de histórico inteligente para evitar repetição de keywords e clusters.
    
    Funcionalidades:
    - Registro de keywords e clusters já processados
    - Variação algorítmica semanal
    - Detecção de novidade
    - Sugestão de clusters alternativos
    - Análise de tendências temporais
    """
    
    def __init__(self, db_path: str = "historico_keywords.db", cache: Optional[AsyncCache] = None):
        """
        Inicializa o sistema de histórico inteligente.
        
        Args:
            db_path: Caminho para o banco SQLite
            cache: Instância do cache para performance
        """
        self.db_path = Path(db_path)
        self.cache = cache or AsyncCache()
        self._init_database()
        
        # Configurações de variação algorítmica
        self.variacoes_algoritmicas = self._configurar_variacoes()
        
        # Cache de termos já processados (memória)
        self._termos_processados: Set[str] = set()
        self._clusters_processados: Set[str] = set()
        
        logger.info({
            "event": "historico_inteligente_inicializado",
            "status": "success",
            "source": "historico_inteligente.__init__",
            "details": {
                "db_path": str(self.db_path),
                "variacoes_configuradas": len(self.variacoes_algoritmicas)
            }
        })
    
    def _init_database(self):
        """Inicializa o banco de dados SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de keywords
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    termo TEXT NOT NULL,
                    hash_termo TEXT UNIQUE NOT NULL,
                    nicho TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    data_coleta TIMESTAMP NOT NULL,
                    volume_busca INTEGER,
                    score REAL,
                    cluster_id TEXT,
                    semana_ano TEXT,
                    variacao_algoritmica TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de clusters
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_clusters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cluster_id TEXT UNIQUE NOT NULL,
                    nome TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    nicho TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    data_criacao TIMESTAMP NOT NULL,
                    score_medio REAL,
                    semana_ano TEXT NOT NULL,
                    variacao_algoritmica TEXT NOT NULL,
                    diversidade_semantica REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices para performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_keywords_hash ON historico_keywords(hash_termo)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_keywords_nicho ON historico_keywords(nicho)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_keywords_semana ON historico_keywords(semana_ano)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_clusters_semana ON historico_clusters(semana_ano)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_clusters_nicho ON historico_clusters(nicho)")
            
            conn.commit()
            conn.close()
            
            logger.info({
                "event": "database_inicializado",
                "status": "success",
                "source": "historico_inteligente._init_database",
                "details": {"db_path": str(self.db_path)}
            })
            
        except Exception as e:
            logger.error({
                "event": "erro_inicializacao_database",
                "status": "error",
                "source": "historico_inteligente._init_database",
                "details": {"error": str(e)}
            })
            raise
    
    def _configurar_variacoes(self) -> Dict[str, VariacaoAlgoritmica]:
        """Configura as variações algorítmicas semanais."""
        return {
            "semana_1": VariacaoAlgoritmica(
                nome="Alta Diversidade",
                descricao="Foco em diversidade semântica e novidade",
                parametros={
                    "min_similaridade": 0.6,
                    "max_clusters": 15,
                    "diversidade_minima": 0.8
                },
                peso_diversidade=0.7,
                peso_novidade=0.8,
                peso_tendencia=0.3
            ),
            "semana_2": VariacaoAlgoritmica(
                nome="Tendências Emergentes",
                descricao="Foco em tendências e volume de busca",
                parametros={
                    "min_similaridade": 0.7,
                    "max_clusters": 12,
                    "volume_minimo": 1000
                },
                peso_diversidade=0.5,
                peso_novidade=0.6,
                peso_tendencia=0.9
            ),
            "semana_3": VariacaoAlgoritmica(
                nome="Cauda Longa",
                descricao="Foco em keywords de cauda longa e baixa concorrência",
                parametros={
                    "min_similaridade": 0.5,
                    "max_clusters": 20,
                    "concorrencia_maxima": 0.4
                },
                peso_diversidade=0.8,
                peso_novidade=0.9,
                peso_tendencia=0.2
            ),
            "semana_4": VariacaoAlgoritmica(
                nome="Otimização Balanceada",
                descricao="Balanceamento entre todos os fatores",
                parametros={
                    "min_similaridade": 0.65,
                    "max_clusters": 15,
                    "score_minimo": 0.6
                },
                peso_diversidade=0.6,
                peso_novidade=0.7,
                peso_tendencia=0.6
            )
        }
    
    def _get_semana_atual(self) -> str:
        """Retorna a semana atual do ano (1-52)."""
        hoje = datetime.now()
        semana = hoje.isocalendar()[1]
        return f"semana_{semana}"
    
    def _get_variacao_atual(self) -> VariacaoAlgoritmica:
        """Retorna a variação algorítmica da semana atual."""
        semana = self._get_semana_atual()
        # Mapeia semana para variação (ciclo de 4 semanas)
        semana_num = int(semana.split('_')[1])
        variacao_idx = ((semana_num - 1) % 4) + 1
        return self.variacoes_algoritmicas[f"semana_{variacao_idx}"]
    
    def _hash_termo(self, termo: str) -> str:
        """Gera hash único para o termo."""
        return hashlib.sha256(termo.lower().encode()).hexdigest()[:16]
    
    async def registrar_keywords(self, keywords: List[Keyword], nicho: str, categoria: str) -> None:
        """
        Registra keywords no histórico.
        
        Args:
            keywords: Lista de keywords para registrar
            nicho: Nome do nicho
            categoria: Nome da categoria
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            variacao = self._get_variacao_atual()
            semana = self._get_semana_atual()
            
            for keyword in keywords:
                hash_termo = self._hash_termo(keyword.termo)
                
                # Verifica se já existe
                cursor.execute(
                    "SELECT id FROM historico_keywords WHERE hash_termo = ?",
                    (hash_termo,)
                )
                
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO historico_keywords 
                        (termo, hash_termo, nicho, categoria, data_coleta, volume_busca, score, semana_ano, variacao_algoritmica)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        keyword.termo,
                        hash_termo,
                        nicho,
                        categoria,
                        keyword.data_coleta or datetime.now(),
                        keyword.volume_busca,
                        keyword.score,
                        semana,
                        variacao.nome
                    ))
                    
                    # Adiciona ao cache de memória
                    self._termos_processados.add(hash_termo)
            
            conn.commit()
            conn.close()
            
            logger.info({
                "event": "keywords_registradas",
                "status": "success",
                "source": "historico_inteligente.registrar_keywords",
                "details": {
                    "total_keywords": len(keywords),
                    "nicho": nicho,
                    "categoria": categoria,
                    "semana": semana,
                    "variacao": variacao.nome
                }
            })
            
        except Exception as e:
            logger.error({
                "event": "erro_registro_keywords",
                "status": "error",
                "source": "historico_inteligente.registrar_keywords",
                "details": {"error": str(e)}
            })
            raise
    
    async def registrar_cluster(self, cluster: Cluster, nicho: str, categoria: str) -> None:
        """
        Registra cluster no histórico.
        
        Args:
            cluster: Cluster para registrar
            nicho: Nome do nicho
            categoria: Nome da categoria
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            variacao = self._get_variacao_atual()
            semana = self._get_semana_atual()
            
            # Verifica se já existe
            cursor.execute(
                "SELECT id FROM historico_clusters WHERE cluster_id = ?",
                (cluster.id,)
            )
            
            if not cursor.fetchone():
                keywords_json = json.dumps([kw.termo for kw in cluster.keywords])
                
                cursor.execute("""
                    INSERT INTO historico_clusters 
                    (cluster_id, nome, keywords, nicho, categoria, data_criacao, score_medio, semana_ano, variacao_algoritmica, diversidade_semantica)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cluster.id,
                    cluster.nome or f"Cluster_{cluster.id}",
                    keywords_json,
                    nicho,
                    categoria,
                    cluster.data_criacao,
                    cluster.similaridade_media,
                    semana,
                    variacao.nome,
                    self._calcular_diversidade_semantica(cluster.keywords)
                ))
                
                # Adiciona ao cache de memória
                self._clusters_processados.add(cluster.id)
            
            conn.commit()
            conn.close()
            
            logger.info({
                "event": "cluster_registrado",
                "status": "success",
                "source": "historico_inteligente.registrar_cluster",
                "details": {
                    "cluster_id": cluster.id,
                    "nicho": nicho,
                    "categoria": categoria,
                    "semana": semana,
                    "variacao": variacao.nome
                }
            })
            
        except Exception as e:
            logger.error({
                "event": "erro_registro_cluster",
                "status": "error",
                "source": "historico_inteligente.registrar_cluster",
                "details": {"error": str(e)}
            })
            raise
    
    async def verificar_novidade_keywords(self, keywords: List[Keyword], nicho: str) -> Tuple[List[Keyword], List[Keyword]]:
        """
        Verifica quais keywords são novas e quais já foram processadas.
        
        Args:
            keywords: Lista de keywords para verificar
            nicho: Nome do nicho
            
        Returns:
            Tuple com (keywords_novas, keywords_repetidas)
        """
        try:
            # Carrega histórico do cache primeiro
            cache_key = f"historico_keywords_{nicho}"
            historico_cache = await self.cache.get(cache_key)
            
            if not historico_cache:
                # Busca do banco
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT hash_termo FROM historico_keywords 
                    WHERE nicho = ? AND data_coleta >= date('now', '-30 days')
                """, (nicho,))
                
                historico_hashes = {row[0] for row in cursor.fetchall()}
                conn.close()
                
                # Salva no cache
                await self.cache.set(cache_key, list(historico_hashes), ttl=3600)
            else:
                historico_hashes = set(historico_cache)
            
            keywords_novas = []
            keywords_repetidas = []
            
            for keyword in keywords:
                hash_termo = self._hash_termo(keyword.termo)
                if hash_termo in historico_hashes:
                    keywords_repetidas.append(keyword)
                else:
                    keywords_novas.append(keyword)
            
            logger.info({
                "event": "verificacao_novidade_keywords",
                "status": "success",
                "source": "historico_inteligente.verificar_novidade_keywords",
                "details": {
                    "total_keywords": len(keywords),
                    "keywords_novas": len(keywords_novas),
                    "keywords_repetidas": len(keywords_repetidas),
                    "nicho": nicho
                }
            })
            
            return keywords_novas, keywords_repetidas
            
        except Exception as e:
            logger.error({
                "event": "erro_verificacao_novidade",
                "status": "error",
                "source": "historico_inteligente.verificar_novidade_keywords",
                "details": {"error": str(e)}
            })
            # Em caso de erro, assume que todas são novas
            return keywords, []
    
    async def sugerir_clusters_alternativos(self, keywords: List[Keyword], nicho: str, categoria: str) -> List[Dict[str, Any]]:
        """
        Sugere clusters alternativos baseados na variação algorítmica da semana.
        
        Args:
            keywords: Lista de keywords disponíveis
            nicho: Nome do nicho
            categoria: Nome da categoria
            
        Returns:
            Lista de sugestões de clusters
        """
        try:
            variacao = self._get_variacao_atual()
            semana = self._get_semana_atual()
            
            # Busca clusters similares já processados
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cluster_id, nome, keywords, score_medio, diversidade_semantica
                FROM historico_clusters 
                WHERE nicho = ? AND categoria = ? AND semana_ano != ?
                ORDER BY data_criacao DESC
                LIMIT 50
            """, (nicho, categoria, semana))
            
            clusters_historicos = cursor.fetchall()
            conn.close()
            
            sugestoes = []
            
            # Analisa clusters históricos para gerar sugestões
            for cluster_historico in clusters_historicos:
                cluster_id, nome, keywords_json, score_medio, diversidade = cluster_historico
                keywords_historico = json.loads(keywords_json)
                
                # Calcula similaridade com keywords atuais
                similaridade = self._calcular_similaridade_keywords(keywords, keywords_historico)
                
                if similaridade < 0.3:  # Baixa similaridade = boa alternativa
                    sugestao = {
                        "tipo": "cluster_alternativo",
                        "nome": f"Alternativa: {nome}",
                        "keywords_sugeridas": self._sugerir_keywords_alternativas(keywords, keywords_historico),
                        "score_historico": score_medio,
                        "diversidade_historica": diversidade,
                        "motivo": "Cluster histórico com baixa similaridade",
                        "variacao_algoritmica": variacao.nome
                    }
                    sugestoes.append(sugestao)
            
            # Gera sugestões baseadas na variação algorítmica
            sugestoes_variacao = self._gerar_sugestoes_por_variacao(keywords, variacao)
            sugestoes.extend(sugestoes_variacao)
            
            logger.info({
                "event": "sugestoes_clusters_geradas",
                "status": "success",
                "source": "historico_inteligente.sugerir_clusters_alternativos",
                "details": {
                    "total_sugestoes": len(sugestoes),
                    "nicho": nicho,
                    "categoria": categoria,
                    "variacao": variacao.nome
                }
            })
            
            return sugestoes
            
        except Exception as e:
            logger.error({
                "event": "erro_sugestoes_clusters",
                "status": "error",
                "source": "historico_inteligente.sugerir_clusters_alternativos",
                "details": {"error": str(e)}
            })
            return []
    
    def _calcular_diversidade_semantica(self, keywords: List[Keyword]) -> float:
        """Calcula a diversidade semântica de um conjunto de keywords."""
        if len(keywords) < 2:
            return 1.0
        
        # Extrai termos únicos
        termos = [kw.termo.lower() for kw in keywords]
        termos_unicos = set(termos)
        
        # Calcula diversidade baseada em sobreposição
        diversidade = len(termos_unicos) / len(termos)
        
        # Penaliza termos muito similares
        palavras_comuns = Counter()
        for termo in termos:
            palavras = termo.split()
            palavras_comuns.update(palavras)
        
        # Se muitas palavras são comuns, reduz diversidade
        palavras_unicas = len(set(palavras_comuns.keys()))
        total_palavras = sum(palavras_comuns.values())
        
        if total_palavras > 0:
            diversidade_palavras = palavras_unicas / total_palavras
            diversidade = (diversidade + diversidade_palavras) / 2
        
        return min(diversidade, 1.0)
    
    def _calcular_similaridade_keywords(self, keywords1: List[Keyword], keywords2: List[str]) -> float:
        """Calcula similaridade entre dois conjuntos de keywords."""
        termos1 = {kw.termo.lower() for kw in keywords1}
        termos2 = {termo.lower() for termo in keywords2}
        
        if not termos1 or not termos2:
            return 0.0
        
        intersecao = len(termos1 & termos2)
        uniao = len(termos1 | termos2)
        
        return intersecao / uniao if uniao > 0 else 0.0
    
    def _sugerir_keywords_alternativas(self, keywords_atuais: List[Keyword], keywords_historico: List[str]) -> List[str]:
        """Sugere keywords alternativas baseadas no histórico."""
        termos_atuais = {kw.termo.lower() for kw in keywords_atuais}
        termos_historico = {termo.lower() for termo in keywords_historico}
        
        # Keywords do histórico que não estão nas atuais
        alternativas = list(termos_historico - termos_atuais)
        
        # Ordena por relevância (simples implementação)
        return alternativas[:10]  # Retorna até 10 alternativas
    
    def _gerar_sugestoes_por_variacao(self, keywords: List[Keyword], variacao: VariacaoAlgoritmica) -> List[Dict[str, Any]]:
        """Gera sugestões específicas baseadas na variação algorítmica."""
        sugestoes = []
        
        if variacao.nome == "Alta Diversidade":
            # Sugere clusters com alta diversidade
            sugestoes.append({
                "tipo": "cluster_diversidade",
                "nome": "Cluster de Alta Diversidade",
                "keywords_sugeridas": self._selecionar_keywords_diversas(keywords),
                "motivo": "Foco em diversidade semântica",
                "parametros": variacao.parametros
            })
        
        elif variacao.nome == "Tendências Emergentes":
            # Sugere clusters baseados em tendências
            sugestoes.append({
                "tipo": "cluster_tendencias",
                "nome": "Cluster de Tendências",
                "keywords_sugeridas": self._selecionar_keywords_tendencias(keywords),
                "motivo": "Foco em tendências emergentes",
                "parametros": variacao.parametros
            })
        
        elif variacao.nome == "Cauda Longa":
            # Sugere clusters de cauda longa
            sugestoes.append({
                "tipo": "cluster_cauda_longa",
                "nome": "Cluster de Cauda Longa",
                "keywords_sugeridas": self._selecionar_keywords_cauda_longa(keywords),
                "motivo": "Foco em keywords de baixa concorrência",
                "parametros": variacao.parametros
            })
        
        return sugestoes
    
    def _selecionar_keywords_diversas(self, keywords: List[Keyword]) -> List[str]:
        """Seleciona keywords com alta diversidade semântica."""
        # Ordena por score e diversidade
        keywords_ordenadas = sorted(keywords, key=lambda kw: kw.score or 0, reverse=True)
        
        # Seleciona keywords com termos diferentes
        selecionadas = []
        termos_utilizados = set()
        
        for keyword in keywords_ordenadas:
            palavras = keyword.termo.lower().split()
            palavras_novas = [p for p in palavras if p not in termos_utilizados]
            
            if len(palavras_novas) > 0:
                selecionadas.append(keyword.termo)
                termos_utilizados.update(palavras_novas)
            
            if len(selecionadas) >= 10:
                break
        
        return selecionadas
    
    def _selecionar_keywords_tendencias(self, keywords: List[Keyword]) -> List[str]:
        """Seleciona keywords com alto volume de busca (tendências)."""
        # Ordena por volume de busca
        keywords_ordenadas = sorted(keywords, key=lambda kw: kw.volume_busca or 0, reverse=True)
        return [kw.termo for kw in keywords_ordenadas[:10]]
    
    def _selecionar_keywords_cauda_longa(self, keywords: List[Keyword]) -> List[str]:
        """Seleciona keywords de cauda longa (baixo volume, baixa concorrência)."""
        # Filtra keywords com baixo volume e baixa concorrência
        cauda_longa = [
            kw for kw in keywords
            if (kw.volume_busca or 0) < 1000 and (kw.concorrencia or 1) < 0.5
        ]
        
        # Ordena por score
        cauda_longa_ordenada = sorted(cauda_longa, key=lambda kw: kw.score or 0, reverse=True)
        return [kw.termo for kw in cauda_longa_ordenada[:10]]
    
    async def obter_estatisticas_historico(self, nicho: str, semanas: int = 4) -> Dict[str, Any]:
        """
        Obtém estatísticas do histórico.
        
        Args:
            nicho: Nome do nicho
            semanas: Número de semanas para analisar
            
        Returns:
            Dicionário com estatísticas
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Keywords por semana
            cursor.execute("""
                SELECT semana_ano, COUNT(*) as total
                FROM historico_keywords 
                WHERE nicho = ? AND data_coleta >= date('now', '-{} days')
                GROUP BY semana_ano
                ORDER BY semana_ano DESC
            """.format(semanas * 7), (nicho,))
            
            keywords_por_semana = dict(cursor.fetchall())
            
            # Clusters por semana
            cursor.execute("""
                SELECT semana_ano, COUNT(*) as total
                FROM historico_clusters 
                WHERE nicho = ? AND data_criacao >= date('now', '-{} days')
                GROUP BY semana_ano
                ORDER BY semana_ano DESC
            """.format(semanas * 7), (nicho,))
            
            clusters_por_semana = dict(cursor.fetchall())
            
            # Variações algorítmicas utilizadas
            cursor.execute("""
                SELECT variacao_algoritmica, COUNT(*) as total
                FROM historico_clusters 
                WHERE nicho = ? AND data_criacao >= date('now', '-{} days')
                GROUP BY variacao_algoritmica
            """.format(semanas * 7), (nicho,))
            
            variacoes_utilizadas = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "keywords_por_semana": keywords_por_semana,
                "clusters_por_semana": clusters_por_semana,
                "variacoes_utilizadas": variacoes_utilizadas,
                "total_keywords": sum(keywords_por_semana.values()),
                "total_clusters": sum(clusters_por_semana.values()),
                "semanas_analisadas": semanas
            }
            
        except Exception as e:
            logger.error({
                "event": "erro_estatisticas_historico",
                "status": "error",
                "source": "historico_inteligente.obter_estatisticas_historico",
                "details": {"error": str(e)}
            })
            return {}

# Instância global
historico_inteligente = HistoricoInteligente() 
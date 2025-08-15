from typing import List, Dict, Optional, Callable, Any, Union, Literal
import numpy as np
from domain.models import Keyword, Cluster
from shared.config import FUNNEL_STAGES
from shared.logger import logger
from datetime import datetime
import uuid
from sklearn.metrics.pairwise import cosine_similarity
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from functools import lru_cache

class ClusterizadorConfig:
    """Configuração avançada para o ClusterizadorSemantico."""
    def __init__(
        self,
        modelo_embeddings: str = "paraphrase-multilingual-MiniLM-L12-v2",
        tamanho_cluster: int = 6,
        min_similaridade: float = 0.5,
        max_clusters: Optional[int] = None,
        paralelizar: bool = False,
        callback: Optional[Callable[[Cluster], None]] = None,
        func_gerar_embeddings: Optional[Callable[[List[str], str], np.ndarray]] = None,
        criterio_diversidade: bool = True,
        func_similaridade: Optional[Callable[[np.ndarray, np.ndarray], np.ndarray]] = None,
        idioma: str = "pt",
        monitoramento_hook: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        self.modelo_embeddings = modelo_embeddings
        self.tamanho_cluster = tamanho_cluster
        self.min_similaridade = min_similaridade
        self.max_clusters = max_clusters
        self.paralelizar = paralelizar
        self.callback = callback
        self.func_gerar_embeddings = func_gerar_embeddings
        self.criterio_diversidade = criterio_diversidade
        self.func_similaridade = func_similaridade or cosine_similarity
        self.idioma = idioma
        self.monitoramento_hook = monitoramento_hook

class ClusterizadorSemantico:
    """
    Clusterizador semântico de keywords baseado em embeddings e similaridade de cosseno.
    Permite configuração avançada, paralelização, callback, diversidade e logs detalhados.
    """
    def __init__(
        self,
        config: Optional[ClusterizadorConfig] = None,
        modelo_embeddings: str = "paraphrase-multilingual-MiniLM-L12-v2",
        tamanho_cluster: int = 6,
        min_similaridade: float = 0.5,
        max_clusters: Optional[int] = None,
        paralelizar: bool = False,
        callback: Optional[Callable[[Cluster], None]] = None,
        func_gerar_embeddings: Optional[Callable[[List[str], str], np.ndarray]] = None,
        criterio_diversidade: bool = True,
        func_similaridade: Optional[Callable[[np.ndarray, np.ndarray], np.ndarray]] = None,
        idioma: str = "pt",
        monitoramento_hook: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """
        Inicializa o clusterizador com configuração avançada ou parâmetros individuais.
        Args:
            ...
            paralelizar: se True, ativa paralelização da montagem de clusters usando múltiplas threads (recomendado para grandes volumes; limitado por MAX_WORKERS e GIL do Python; ganhos marginais para listas pequenas)
            ...
        """
        if config:
            self.modelo_embeddings = config.modelo_embeddings
            self.tamanho_cluster = config.tamanho_cluster
            self.min_similaridade = config.min_similaridade
            self.max_clusters = config.max_clusters
            self.paralelizar = config.paralelizar
            self.callback = config.callback
            self.func_gerar_embeddings = config.func_gerar_embeddings
            self.criterio_diversidade = config.criterio_diversidade
            self.func_similaridade = getattr(config, 'func_similaridade', cosine_similarity)
            self.idioma = getattr(config, 'idioma', "pt")
            self.monitoramento_hook = getattr(config, 'monitoramento_hook', None)
        else:
            self.modelo_embeddings = modelo_embeddings
            self.tamanho_cluster = tamanho_cluster
            self.min_similaridade = min_similaridade
            self.max_clusters = max_clusters
            self.paralelizar = paralelizar
            self.callback = callback
            self.func_gerar_embeddings = func_gerar_embeddings
            self.criterio_diversidade = criterio_diversidade
            self.func_similaridade = func_similaridade or cosine_similarity
            self.idioma = idioma
            self.monitoramento_hook = monitoramento_hook
        # Validação de dependências
        try:
            import sklearn
            import numpy
        except ImportError as e:
            raise RuntimeError(f"Dependência obrigatória ausente: {e}")
        self._exec_id = str(uuid.uuid4())[:12]
        self._clusters_termos = set()  # Para critério de diversidade
        self._embeddings_cache = {}

    def _validar_keywords(self, keywords: List[Keyword]) -> List[Keyword]:
        """Filtra e retorna apenas keywords válidas."""
        validas = []
        for kw in keywords:
            if not kw or not kw.termo or kw.volume_busca < 0:
                logger.warning({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "keyword_invalida",
                    "status": "warning",
                    "source": "clusterizador_semantico._validar_keywords",
                    "exec_id": self._exec_id,
                    "details": {"termo": getattr(kw, 'termo', None)}
                })
                continue
            validas.append(kw)
        return validas

    @lru_cache(maxsize=128)
    def _cache_embeddings(self, termos_hash: str, modelo: str) -> np.ndarray:
        return self._gerar_embeddings_nocache(termos_hash, modelo)

    def _gerar_embeddings_nocache(self, termos_hash: str, modelo: str) -> np.ndarray:
        # Função interna para cache
        termos = json.loads(termos_hash)
        if self.func_gerar_embeddings:
            return self.func_gerar_embeddings(termos, modelo)
        from infrastructure.ml.embeddings import gerar_embeddings
        return gerar_embeddings(termos, model_name=modelo)

    def _gerar_embeddings(self, termos: List[str]) -> np.ndarray:
        termos_hash = json.dumps(termos, sort_keys=True)
        key = (termos_hash, self.modelo_embeddings)
        if key in self._embeddings_cache:
            return self._embeddings_cache[key]
        emb = self._gerar_embeddings_nocache(termos_hash, self.modelo_embeddings)
        self._embeddings_cache[key] = emb
        return emb

    def _calcular_similaridade(self, emb1: np.ndarray, emb2: np.ndarray) -> np.ndarray:
        return self.func_similaridade(emb1, emb2)

    def _criar_cluster(self, keywords: List[Keyword], similares: List[float], categoria: str, blog_dominio: str) -> Optional[Cluster]:
        """Cria um cluster se a similaridade média for suficiente e respeitar diversidade."""
        similaridade_media = float(np.mean(similares)) if similares else 1.0
        termos_cluster = set(kw.termo.lower() for kw in keywords)
        if self.criterio_diversidade and (termos_cluster & self._clusters_termos):
            logger.warning(str({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "cluster_descartado_diversidade",
                "status": "warning",
                "source": "clusterizador_semantico._criar_cluster",
                "exec_id": self._exec_id,
                "details": {"termos_repetidos": list(termos_cluster & self._clusters_termos)}
            }))
            return None
        if similaridade_media < self.min_similaridade:
            logger.warning({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "cluster_descartado_similaridade_baixa",
                "status": "warning",
                "source": "clusterizador_semantico._criar_cluster",
                "exec_id": self._exec_id,
                "details": {"similaridade_media": similaridade_media}
            })
            return None
        fases = FUNNEL_STAGES[:len(keywords)]
        for idx, (key, fase) in enumerate(zip(keywords, fases)):
            key.fase_funil = fase
            key.ordem_no_cluster = idx
            key.nome_artigo = f"Artigo{idx+1}"
        cluster_id = str(uuid.uuid4())[:16]
        self._clusters_termos.update(termos_cluster)
        cluster = Cluster(
            id=cluster_id,
            keywords=keywords,
            similaridade_media=similaridade_media,
            fase_funil=fases[0],
            categoria=categoria,
            blog_dominio=blog_dominio,
            data_criacao=datetime.utcnow(),
            status_geracao="pendente"
        )
        # Validação de consistência
        if len(set(kw.termo.lower() for kw in cluster.keywords)) != len(cluster.keywords):
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "cluster_inconsistente",
                "status": "error",
                "source": "clusterizador_semantico._criar_cluster",
                "exec_id": self._exec_id,
                "details": {"motivo": "termos duplicados"}
            })
            return None
        return cluster

    def _serializar_clusters(self, clusters: List[Cluster]) -> List[Dict[str, Any]]:
        """Serializa clusters para dicionários JSON-safe."""
        return [c.to_dict() for c in clusters]

    def _serializar_descartes(self, descartes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Serializa descartes para dicionários JSON-safe."""
        return descartes

    def _gerar_relatorio(self, clusters: List[Cluster], descartes: List[Dict[str, Any]], heatmap: Optional[np.ndarray] = None) -> Dict[str, Any]:
        return {
            "total_clusters": len(clusters),
            "total_descartados": len(descartes),
            "motivos_descartes": [data.get("motivo") for data in descartes],
            "heatmap_similaridade": heatmap.tolist() if heatmap is not None else None
        }

    async def gerar_clusters_async(
        self,
        keywords: List[Keyword],
        categoria: Optional[str] = "",
        blog_dominio: Optional[str] = "",
        formato_retorno: Literal["objeto", "json"] = "objeto"
    ) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.gerar_clusters(keywords, categoria, blog_dominio, formato_retorno)
        )

    def gerar_clusters(
        self,
        keywords: List[Keyword],
        categoria: Optional[str] = "",
        blog_dominio: Optional[str] = "",
        formato_retorno: Literal["objeto", "json"] = "objeto"
    ) -> Dict[str, Any]:
        inicio = time.time()
        resultado = {"clusters": [], "descartados": [], "exec_id": self._exec_id}
        keywords_validas = self._validar_keywords(keywords)
        if len(keywords_validas) < self.tamanho_cluster:
            logger.warning({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "clusterizacao_semantica_insuficiente",
                "status": "warning",
                "source": "clusterizador_semantico.gerar_clusters",
                "exec_id": self._exec_id,
                "details": {"total_keywords": len(keywords_validas)}
            })
            resultado["tempo_execucao"] = round(time.time() - inicio, 3)
            return resultado
        keywords_sorted = sorted(keywords_validas, key=lambda key: key.volume_busca, reverse=True)
        termos = [key.termo for key in keywords_sorted]
        try:
            embeddings = self._gerar_embeddings(termos)
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_geracao_embeddings",
                "status": "error",
                "source": "clusterizador_semantico.gerar_clusters",
                "exec_id": self._exec_id,
                "details": {"erro": str(e)}
            })
            resultado["tempo_execucao"] = round(time.time() - inicio, 3)
            return resultado
        usados = set()
        total = len(keywords_sorted)
        clusters_gerados = 0
        heatmap = self._calcular_similaridade(embeddings, embeddings)
        # Paralelização real do cálculo de clusters
        def montar_cluster(head_idx):
            head = keywords_sorted[head_idx]
            head_emb = embeddings[head_idx]
            sim_matrix = self._calcular_similaridade(np.array([head_emb]), embeddings)[0]
            similares = [
                (sim_matrix[counter], counter, keywords_sorted[counter])
                for counter in range(total)
                if counter != head_idx and counter not in usados
            ]
            similares = sorted(similares, key=lambda value: value[0], reverse=True)[:self.tamanho_cluster-1]
            if len(similares) < self.tamanho_cluster-1:
                return None, {"head": head.termo, "motivo": "similares insuficientes"}
            cluster_keywords = [head] + [key for _, _, key in similares]
            cluster = self._criar_cluster(cluster_keywords, [string_data[0] for string_data in similares], categoria, blog_dominio)
            if cluster:
                return cluster, None
            else:
                return None, {"head": head.termo, "motivo": "similaridade/ diversidade baixa"}
        indices_heads = [index for index in range(total) if index not in usados]
        if self.paralelizar:
            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(montar_cluster, idx): idx for idx in indices_heads}
                for future in as_completed(futures):
                    cluster, descarte = future.result()
                    if cluster:
                        resultado["clusters"].append(cluster)
                        clusters_gerados += 1
                        if self.callback:
                            try:
                                self.callback(cluster)
                            except Exception as e:
                                logger.error({
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "event": "erro_callback_cluster",
                                    "status": "error",
                                    "source": "clusterizador_semantico.gerar_clusters",
                                    "exec_id": self._exec_id,
                                    "details": {"erro": str(e)}
                                })
                        if self.max_clusters and clusters_gerados >= self.max_clusters:
                            break
                    elif descarte:
                        resultado["descartados"].append(descarte)
        else:
            while len(usados) + self.tamanho_cluster <= total:
                if self.max_clusters and clusters_gerados >= self.max_clusters:
                    break
                head_idx = next((index for index in range(total) if index not in usados), None)
                if head_idx is None:
                    break
                cluster, descarte = montar_cluster(head_idx)
                if cluster:
                    resultado["clusters"].append(cluster)
                    clusters_gerados += 1
                    if self.callback:
                        try:
                            self.callback(cluster)
                        except Exception as e:
                            logger.error({
                                "timestamp": datetime.utcnow().isoformat(),
                                "event": "erro_callback_cluster",
                                "status": "error",
                                "source": "clusterizador_semantico.gerar_clusters",
                                "exec_id": self._exec_id,
                                "details": {"erro": str(e)}
                            })
                elif descarte:
                    resultado["descartados"].append(descarte)
                usados.add(head_idx)
                for _, counter, _ in sorted([
                    (heatmap[head_idx, counter], counter, keywords_sorted[counter])
                    for counter in range(total)
                    if counter != head_idx and counter not in usados
                ], key=lambda value: value[0], reverse=True)[:self.tamanho_cluster-1]:
                    usados.add(counter)
        resultado["tempo_execucao"] = round(time.time() - inicio, 3)
        resultado["relatorio"] = self._gerar_relatorio(resultado["clusters"], resultado["descartados"], heatmap)
        if self.monitoramento_hook:
            try:
                self.monitoramento_hook(resultado)
            except Exception as e:
                logger.error({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "erro_monitoramento_hook",
                    "status": "error",
                    "source": "clusterizador_semantico.gerar_clusters",
                    "exec_id": self._exec_id,
                    "details": {"erro": str(e)}
                })
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "clusters_semanticos_gerados",
            "status": "success",
            "source": "clusterizador_semantico.gerar_clusters",
            "exec_id": self._exec_id,
            "details": {"total_clusters": len(resultado['clusters']), "tempo_execucao": resultado["tempo_execucao"]}
        })
        if formato_retorno == "json":
            return {
                "clusters": self._serializar_clusters(resultado["clusters"]),
                "descartados": self._serializar_descartes(resultado["descartados"]),
                "exec_id": self._exec_id,
                "tempo_execucao": resultado["tempo_execucao"],
                "relatorio": resultado["relatorio"]
            }
        return resultado

    def gerar_clusters_semanticos(
        self,
        keywords: List[Keyword],
        tamanho_cluster: Optional[int] = None,
        modelo_embeddings: Optional[str] = None,
        categoria: Optional[str] = None,
        blog_dominio: Optional[str] = None
    ) -> List[Cluster]:
        """
        Wrapper de compatibilidade reversa para assinatura antiga.
        """
        return self.gerar_clusters(
            keywords=keywords,
            categoria=categoria or "",
            blog_dominio=blog_dominio or ""
        )["clusters"]

    # Benchmark e stress test
    def benchmark(
        self,
        keywords: List[Keyword],
        n_execucoes: int = 3
    ) -> Dict[str, Any]:
        tempos = []
        for _ in range(n_execucoes):
            inicio = time.time()
            self.gerar_clusters(keywords)
            tempos.append(time.time() - inicio)
        return {
            "media_tempo": np.mean(tempos),
            "desvio_padrao": np.std(tempos),
            "execucoes": n_execucoes
        } 
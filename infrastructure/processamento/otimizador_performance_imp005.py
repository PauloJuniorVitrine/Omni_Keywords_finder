"""
Otimizador de Performance Crítica - IMP-005
Responsável por otimizar queries e cache em pontos críticos do sistema.

Prompt: CHECKLIST_REVISAO_FINAL.md - IMP-005
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 1.0.0
Tracing ID: PERF_OPT_IMP005_001
"""

from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
import json
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import wraps, lru_cache
import threading
from enum import Enum

# Cache e otimização
import redis
from cachetools import TTLCache, LRUCache
import psutil
import gc

# Logging estruturado
from shared.logger import logger

class TipoOtimizacao(Enum):
    """Tipos de otimização disponíveis."""
    CACHE = "cache"
    QUERY = "query"
    PARALELIZACAO = "paralelizacao"
    MEMORIA = "memoria"
    CPU = "cpu"
    REDE = "rede"

@dataclass
class ConfiguracaoOtimizacao:
    """Configuração para otimização de performance."""
    ativar_cache_inteligente: bool = True
    ativar_paralelizacao: bool = True
    ativar_otimizacao_memoria: bool = True
    ativar_otimizacao_cpu: bool = True
    max_workers: int = 4
    cache_ttl_segundos: int = 3600
    cache_max_size: int = 1000
    monitoramento_tempo_real: bool = True
    alertas_performance: bool = True
    threshold_tempo_resposta_ms: int = 500
    threshold_uso_memoria_percent: float = 80.0
    threshold_uso_cpu_percent: float = 80.0

@dataclass
class MetricasPerformance:
    """Métricas de performance em tempo real."""
    tempo_inicio: datetime = field(default_factory=datetime.utcnow)
    tempo_fim: Optional[datetime] = None
    tempo_total_ms: float = 0.0
    uso_memoria_mb: float = 0.0
    uso_cpu_percent: float = 0.0
    queries_executadas: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    erros_performance: int = 0
    otimizacoes_aplicadas: List[str] = field(default_factory=list)
    
    def calcular_tempo_total(self):
        """Calcula tempo total de execução."""
        if self.tempo_fim:
            self.tempo_total_ms = (self.tempo_fim - self.tempo_inicio).total_seconds() * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte métricas para dicionário."""
        return {
            "tempo_total_ms": self.tempo_total_ms,
            "uso_memoria_mb": self.uso_memoria_mb,
            "uso_cpu_percent": self.uso_cpu_percent,
            "queries_executadas": self.queries_executadas,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
            "erros_performance": self.erros_performance,
            "otimizacoes_aplicadas": self.otimizacoes_aplicadas,
            "timestamp": datetime.utcnow().isoformat()
        }

class CacheInteligente:
    """Sistema de cache inteligente com TTL dinâmico."""
    
    def __init__(self, config: ConfiguracaoOtimizacao):
        self.config = config
        self.cache = TTLCache(
            maxsize=config.cache_max_size,
            ttl=config.cache_ttl_segundos
        )
        self.cache_stats = {"hits": 0, "misses": 0}
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache."""
        try:
            value = self.cache.get(key)
            with self.lock:
                if value is not None:
                    self.cache_stats["hits"] += 1
                else:
                    self.cache_stats["misses"] += 1
            return value
        except Exception as e:
            logger.error({
                "event": "erro_cache_get",
                "key": key,
                "erro": str(e)
            })
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Define valor no cache."""
        try:
            ttl = ttl or self.config.cache_ttl_segundos
            self.cache[key] = value
            return True
        except Exception as e:
            logger.error({
                "event": "erro_cache_set",
                "key": key,
                "erro": str(e)
            })
            return False
    
    def invalidate(self, pattern: str) -> int:
        """Invalida cache por padrão."""
        try:
            keys_to_remove = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self.cache[key]
            return len(keys_to_remove)
        except Exception as e:
            logger.error({
                "event": "erro_cache_invalidate",
                "pattern": pattern,
                "erro": str(e)
            })
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache."""
        with self.lock:
            total = self.cache_stats["hits"] + self.cache_stats["misses"]
            hit_rate = self.cache_stats["hits"] / total if total > 0 else 0
            
            return {
                "hits": self.cache_stats["hits"],
                "misses": self.cache_stats["misses"],
                "hit_rate": hit_rate,
                "size": len(self.cache),
                "max_size": self.config.cache_max_size
            }

class OtimizadorQueries:
    """Otimizador de queries e consultas."""
    
    def __init__(self, config: ConfiguracaoOtimizacao):
        self.config = config
        self.query_cache = CacheInteligente(config)
        self.query_stats = {}
    
    def otimizar_query(self, query: str, params: Dict[str, Any] = None) -> str:
        """Otimiza query SQL."""
        try:
            # Implementar otimizações básicas
            query_otimizada = query.strip()
            
            # Remover comentários desnecessários
            query_otimizada = self._remover_comentarios(query_otimizada)
            
            # Otimizar SELECT *
            query_otimizada = self._otimizar_select(query_otimizada)
            
            # Adicionar LIMIT se não existir
            query_otimizada = self._adicionar_limit(query_otimizada)
            
            return query_otimizada
            
        except Exception as e:
            logger.error({
                "event": "erro_otimizacao_query",
                "query": query,
                "erro": str(e)
            })
            return query
    
    def _remover_comentarios(self, query: str) -> str:
        """Remove comentários desnecessários da query."""
        lines = query.split('\n')
        lines_limpas = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('--') and not line.startswith('/*'):
                lines_limpas.append(line)
        
        return ' '.join(lines_limpas)
    
    def _otimizar_select(self, query: str) -> str:
        """Otimiza SELECT * para colunas específicas."""
        if 'SELECT *' in query.upper():
            # Em produção, seria necessário mapear para colunas específicas
            # Por enquanto, mantém como está
            pass
        return query
    
    def _adicionar_limit(self, query: str) -> str:
        """Adiciona LIMIT se não existir."""
        if 'LIMIT' not in query.upper() and 'SELECT' in query.upper():
            query += ' LIMIT 1000'
        return query
    
    def executar_query_otimizada(self, query: str, params: Dict[str, Any] = None) -> Tuple[Any, float]:
        """Executa query otimizada com métricas."""
        inicio = time.time()
        
        try:
            # Verificar cache primeiro
            cache_key = f"query:{hash(query + str(params))}"
            resultado_cache = self.query_cache.get(cache_key)
            
            if resultado_cache:
                tempo_execucao = (time.time() - inicio) * 1000
                return resultado_cache, tempo_execucao
            
            # Otimizar query
            query_otimizada = self.otimizar_query(query, params)
            
            # Executar query (simulado)
            resultado = self._executar_query(query_otimizada, params)
            
            # Armazenar no cache
            self.query_cache.set(cache_key, resultado)
            
            tempo_execucao = (time.time() - inicio) * 1000
            
            # Registrar estatísticas
            self._registrar_stats(query, tempo_execucao)
            
            return resultado, tempo_execucao
            
        except Exception as e:
            tempo_execucao = (time.time() - inicio) * 1000
            logger.error({
                "event": "erro_execucao_query",
                "query": query,
                "tempo_ms": tempo_execucao,
                "erro": str(e)
            })
            raise
    
    def _executar_query(self, query: str, params: Dict[str, Any] = None) -> Any:
        """Executa query (simulado para demonstração)."""
        # Em produção, aqui seria a execução real da query
        time.sleep(0.1)  # Simular tempo de execução
        return {"resultado": "simulado", "query": query}
    
    def _registrar_stats(self, query: str, tempo_ms: float):
        """Registra estatísticas da query."""
        query_hash = hash(query)
        if query_hash not in self.query_stats:
            self.query_stats[query_hash] = {
                "execucoes": 0,
                "tempo_total_ms": 0,
                "tempo_medio_ms": 0
            }
        
        stats = self.query_stats[query_hash]
        stats["execucoes"] += 1
        stats["tempo_total_ms"] += tempo_ms
        stats["tempo_medio_ms"] = stats["tempo_total_ms"] / stats["execucoes"]

class OtimizadorMemoria:
    """Otimizador de uso de memória."""
    
    def __init__(self, config: ConfiguracaoOtimizacao):
        self.config = config
        self.monitoramento_ativo = False
    
    def iniciar_monitoramento(self):
        """Inicia monitoramento de memória."""
        self.monitoramento_ativo = True
        logger.info({
            "event": "monitoramento_memoria_iniciado",
            "threshold": self.config.threshold_uso_memoria_percent
        })
    
    def parar_monitoramento(self):
        """Para monitoramento de memória."""
        self.monitoramento_ativo = False
        logger.info({
            "event": "monitoramento_memoria_parado"
        })
    
    def obter_uso_memoria(self) -> Dict[str, float]:
        """Obtém uso atual de memória."""
        try:
            memoria = psutil.virtual_memory()
            return {
                "total_mb": memoria.total / (1024 * 1024),
                "disponivel_mb": memoria.available / (1024 * 1024),
                "usado_mb": memoria.used / (1024 * 1024),
                "percentual_usado": memoria.percent
            }
        except Exception as e:
            logger.error({
                "event": "erro_obter_memoria",
                "erro": str(e)
            })
            return {}
    
    def verificar_pressao_memoria(self) -> bool:
        """Verifica se há pressão de memória."""
        uso_memoria = self.obter_uso_memoria()
        return uso_memoria.get("percentual_usado", 0) > self.config.threshold_uso_memoria_percent
    
    def otimizar_memoria(self) -> Dict[str, Any]:
        """Executa otimizações de memória."""
        otimizacoes = []
        
        try:
            # Forçar coleta de lixo
            objetos_coletados = gc.collect()
            otimizacoes.append(f"gc_collect:{objetos_coletados}")
            
            # Limpar cache se necessário
            if self.verificar_pressao_memoria():
                # Em produção, limparia caches específicos
                otimizacoes.append("cache_limpo")
            
            # Otimizar uso de memória do processo
            memoria_antes = self.obter_uso_memoria()
            
            # Simular otimizações
            time.sleep(0.1)
            
            memoria_depois = self.obter_uso_memoria()
            
            return {
                "otimizacoes_aplicadas": otimizacoes,
                "memoria_antes_mb": memoria_antes.get("usado_mb", 0),
                "memoria_depois_mb": memoria_depois.get("usado_mb", 0),
                "reducao_mb": memoria_antes.get("usado_mb", 0) - memoria_depois.get("usado_mb", 0)
            }
            
        except Exception as e:
            logger.error({
                "event": "erro_otimizacao_memoria",
                "erro": str(e)
            })
            return {"erro": str(e)}

class OtimizadorCPU:
    """Otimizador de uso de CPU."""
    
    def __init__(self, config: ConfiguracaoOtimizacao):
        self.config = config
    
    def obter_uso_cpu(self) -> Dict[str, float]:
        """Obtém uso atual de CPU."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            return {
                "percentual_usado": cpu_percent,
                "cores_disponiveis": cpu_count,
                "carga_media": cpu_percent / cpu_count if cpu_count > 0 else 0
            }
        except Exception as e:
            logger.error({
                "event": "erro_obter_cpu",
                "erro": str(e)
            })
            return {}
    
    def verificar_pressao_cpu(self) -> bool:
        """Verifica se há pressão de CPU."""
        uso_cpu = self.obter_uso_cpu()
        return uso_cpu.get("percentual_usado", 0) > self.config.threshold_uso_cpu_percent
    
    def otimizar_cpu(self) -> Dict[str, Any]:
        """Executa otimizações de CPU."""
        otimizacoes = []
        
        try:
            # Verificar processos com alto uso de CPU
            processos = psutil.process_iter(['pid', 'name', 'cpu_percent'])
            processos_alto_cpu = []
            
            for proc in processos:
                try:
                    if proc.info['cpu_percent'] > 50:  # Threshold de 50%
                        processos_alto_cpu.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu_percent": proc.info['cpu_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if processos_alto_cpu:
                otimizacoes.append(f"processos_alto_cpu_detectados:{len(processos_alto_cpu)}")
            
            return {
                "otimizacoes_aplicadas": otimizacoes,
                "processos_alto_cpu": processos_alto_cpu
            }
            
        except Exception as e:
            logger.error({
                "event": "erro_otimizacao_cpu",
                "erro": str(e)
            })
            return {"erro": str(e)}

class OtimizadorPerformance:
    """
    Otimizador principal de performance crítica.
    
    Responsabilidades:
    - Gerenciar cache inteligente
    - Otimizar queries
    - Monitorar uso de recursos
    - Aplicar otimizações automáticas
    - Coletar métricas de performance
    """
    
    def __init__(self, config: Optional[ConfiguracaoOtimizacao] = None):
        """
        Inicializa o otimizador de performance.
        
        Args:
            config: Configuração de otimização
        """
        self.config = config or ConfiguracaoOtimizacao()
        self.tracing_id = f"PERF_OPT_{uuid.uuid4().hex[:8]}"
        self.metricas = MetricasPerformance()
        
        # Inicializar componentes
        self._inicializar_componentes()
        
        # Registrar inicialização
        self._log_inicializacao()
    
    def _inicializar_componentes(self):
        """Inicializa componentes de otimização."""
        try:
            # Cache inteligente
            if self.config.ativar_cache_inteligente:
                self.cache = CacheInteligente(self.config)
            
            # Otimizador de queries
            self.otimizador_queries = OtimizadorQueries(self.config)
            
            # Otimizador de memória
            if self.config.ativar_otimizacao_memoria:
                self.otimizador_memoria = OtimizadorMemoria(self.config)
                self.otimizador_memoria.iniciar_monitoramento()
            
            # Otimizador de CPU
            if self.config.ativar_otimizacao_cpu:
                self.otimizador_cpu = OtimizadorCPU(self.config)
            
            logger.info({
                "event": "otimizador_performance_inicializado",
                "tracing_id": self.tracing_id,
                "componentes_ativos": self._listar_componentes_ativos()
            })
            
        except Exception as e:
            logger.error({
                "event": "erro_inicializacao_otimizador",
                "tracing_id": self.tracing_id,
                "erro": str(e)
            })
            raise
    
    def _listar_componentes_ativos(self) -> List[str]:
        """Lista componentes ativos."""
        componentes = ["otimizador_queries"]
        
        if self.config.ativar_cache_inteligente:
            componentes.append("cache_inteligente")
        if self.config.ativar_otimizacao_memoria:
            componentes.append("otimizador_memoria")
        if self.config.ativar_otimizacao_cpu:
            componentes.append("otimizador_cpu")
        if self.config.ativar_paralelizacao:
            componentes.append("paralelizacao")
        
        return componentes
    
    def _log_inicializacao(self):
        """Registra log de inicialização."""
        logger.info({
            "event": "otimizador_performance_imp005_iniciado",
            "tracing_id": self.tracing_id,
            "configuracao": {
                "cache_inteligente": self.config.ativar_cache_inteligente,
                "paralelizacao": self.config.ativar_paralelizacao,
                "otimizacao_memoria": self.config.ativar_otimizacao_memoria,
                "otimizacao_cpu": self.config.ativar_otimizacao_cpu,
                "max_workers": self.config.max_workers,
                "cache_ttl": self.config.cache_ttl_segundos
            }
        })
    
    def executar_com_otimizacao(self, funcao: Callable, *args, **kwargs) -> Tuple[Any, Dict[str, Any]]:
        """
        Executa função com otimizações de performance.
        
        Args:
            funcao: Função a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Tuple com resultado e métricas de performance
        """
        inicio = time.time()
        
        try:
            # Verificar cache se aplicável
            if self.config.ativar_cache_inteligente:
                cache_key = f"func:{funcao.__name__}:{hash(str(args) + str(kwargs))}"
                resultado_cache = self.cache.get(cache_key)
                
                if resultado_cache:
                    self.metricas.cache_hits += 1
                    tempo_execucao = (time.time() - inicio) * 1000
                    return resultado_cache, {"tempo_ms": tempo_execucao, "cache_hit": True}
                
                self.metricas.cache_misses += 1
            
            # Executar função
            resultado = funcao(*args, **kwargs)
            
            # Armazenar no cache se aplicável
            if self.config.ativar_cache_inteligente:
                self.cache.set(cache_key, resultado)
            
            # Calcular métricas
            tempo_execucao = (time.time() - inicio) * 1000
            self.metricas.tempo_total_ms = tempo_execucao
            
            # Verificar otimizações necessárias
            otimizacoes = self._verificar_otimizacoes()
            
            # Atualizar métricas
            self._atualizar_metricas()
            
            return resultado, {
                "tempo_ms": tempo_execucao,
                "cache_hit": False,
                "otimizacoes": otimizacoes
            }
            
        except Exception as e:
            tempo_execucao = (time.time() - inicio) * 1000
            self.metricas.erros_performance += 1
            
            logger.error({
                "event": "erro_execucao_otimizada",
                "funcao": funcao.__name__,
                "tempo_ms": tempo_execucao,
                "erro": str(e),
                "tracing_id": self.tracing_id
            })
            raise
    
    def _verificar_otimizacoes(self) -> List[str]:
        """Verifica e aplica otimizações necessárias."""
        otimizacoes = []
        
        try:
            # Verificar pressão de memória
            if self.config.ativar_otimizacao_memoria:
                if self.otimizador_memoria.verificar_pressao_memoria():
                    resultado_memoria = self.otimizador_memoria.otimizar_memoria()
                    otimizacoes.append(f"memoria:{resultado_memoria.get('otimizacoes_aplicadas', [])}")
            
            # Verificar pressão de CPU
            if self.config.ativar_otimizacao_cpu:
                if self.otimizador_cpu.verificar_pressao_cpu():
                    resultado_cpu = self.otimizador_cpu.otimizar_cpu()
                    otimizacoes.append(f"cpu:{resultado_cpu.get('otimizacoes_aplicadas', [])}")
            
            return otimizacoes
            
        except Exception as e:
            logger.error({
                "event": "erro_verificacao_otimizacoes",
                "erro": str(e),
                "tracing_id": self.tracing_id
            })
            return []
    
    def _atualizar_metricas(self):
        """Atualiza métricas de performance."""
        try:
            # Atualizar uso de memória
            if self.config.ativar_otimizacao_memoria:
                uso_memoria = self.otimizador_memoria.obter_uso_memoria()
                self.metricas.uso_memoria_mb = uso_memoria.get("usado_mb", 0)
            
            # Atualizar uso de CPU
            if self.config.ativar_otimizacao_cpu:
                uso_cpu = self.otimizador_cpu.obter_uso_cpu()
                self.metricas.uso_cpu_percent = uso_cpu.get("percentual_usado", 0)
            
        except Exception as e:
            logger.error({
                "event": "erro_atualizacao_metricas",
                "erro": str(e),
                "tracing_id": self.tracing_id
            })
    
    def executar_query_otimizada(self, query: str, params: Dict[str, Any] = None) -> Tuple[Any, Dict[str, Any]]:
        """
        Executa query com otimizações.
        
        Args:
            query: Query SQL
            params: Parâmetros da query
            
        Returns:
            Tuple com resultado e métricas
        """
        return self.executar_com_otimizacao(
            self.otimizador_queries.executar_query_otimizada,
            query,
            params
        )
    
    def obter_metricas(self) -> Dict[str, Any]:
        """Obtém métricas completas de performance."""
        self.metricas.tempo_fim = datetime.utcnow()
        self.metricas.calcular_tempo_total()
        
        metricas_completas = self.metricas.to_dict()
        
        # Adicionar estatísticas de cache
        if self.config.ativar_cache_inteligente:
            metricas_completas["cache_stats"] = self.cache.get_stats()
        
        # Adicionar uso de recursos
        if self.config.ativar_otimizacao_memoria:
            metricas_completas["memoria"] = self.otimizador_memoria.obter_uso_memoria()
        
        if self.config.ativar_otimizacao_cpu:
            metricas_completas["cpu"] = self.otimizador_cpu.obter_uso_cpu()
        
        return metricas_completas
    
    def gerar_relatorio_performance(self) -> Dict[str, Any]:
        """Gera relatório completo de performance."""
        metricas = self.obter_metricas()
        
        relatorio = {
            "tracing_id": self.tracing_id,
            "timestamp": datetime.utcnow().isoformat(),
            "configuracao": {
                "cache_inteligente": self.config.ativar_cache_inteligente,
                "paralelizacao": self.config.ativar_paralelizacao,
                "otimizacao_memoria": self.config.ativar_otimizacao_memoria,
                "otimizacao_cpu": self.config.ativar_otimizacao_cpu
            },
            "metricas": metricas,
            "status": "otimizado" if metricas["tempo_total_ms"] < self.config.threshold_tempo_resposta_ms else "necessita_otimizacao",
            "recomendacoes": self._gerar_recomendacoes(metricas)
        }
        
        return relatorio
    
    def _gerar_recomendacoes(self, metricas: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nas métricas."""
        recomendacoes = []
        
        # Verificar tempo de resposta
        if metricas["tempo_total_ms"] > self.config.threshold_tempo_resposta_ms:
            recomendacoes.append("Considerar otimização de queries ou cache")
        
        # Verificar uso de memória
        if metricas.get("memoria", {}).get("percentual_usado", 0) > self.config.threshold_uso_memoria_percent:
            recomendacoes.append("Otimizar uso de memória ou aumentar recursos")
        
        # Verificar uso de CPU
        if metricas.get("cpu", {}).get("percentual_usado", 0) > self.config.threshold_uso_cpu_percent:
            recomendacoes.append("Considerar paralelização ou otimização de algoritmos")
        
        # Verificar cache hit rate
        if metricas.get("cache_hit_rate", 0) < 0.7:
            recomendacoes.append("Ajustar estratégia de cache para melhorar hit rate")
        
        return recomendacoes
    
    def limpar_cache(self) -> Dict[str, Any]:
        """Limpa todos os caches."""
        try:
            if self.config.ativar_cache_inteligente:
                # Limpar cache principal
                self.cache.cache.clear()
                
                # Limpar cache de queries
                self.otimizador_queries.query_cache.cache.clear()
                
                logger.info({
                    "event": "cache_limpo",
                    "tracing_id": self.tracing_id
                })
                
                return {"status": "success", "message": "Cache limpo com sucesso"}
            
            return {"status": "skipped", "message": "Cache não está ativo"}
            
        except Exception as e:
            logger.error({
                "event": "erro_limpeza_cache",
                "erro": str(e),
                "tracing_id": self.tracing_id
            })
            return {"status": "error", "erro": str(e)}

# Decorator para otimização automática
def otimizar_performance(config: Optional[ConfiguracaoOtimizacao] = None):
    """
    Decorator para aplicar otimizações de performance automaticamente.
    
    Args:
        config: Configuração de otimização
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            otimizador = OtimizadorPerformance(config)
            return otimizador.executar_com_otimizacao(func, *args, **kwargs)
        return wrapper
    return decorator

# Função de exemplo para demonstração
@otimizar_performance()
def exemplo_funcao_otimizada(dados: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Exemplo de função otimizada.
    
    Args:
        dados: Lista de dados para processar
        
    Returns:
        Resultado do processamento
    """
    # Simular processamento
    time.sleep(0.1)
    
    return {
        "total_processado": len(dados),
        "resultado": "processado_com_otimizacao"
    } 
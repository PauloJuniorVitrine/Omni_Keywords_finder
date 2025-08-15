"""
Processador Orquestrador - Refatoração de Complexidade Ciclomática
IMP-001: Separação de responsabilidades do IntegradorCaudaLonga

Tracing ID: IMP001_ORCHESTRATOR_001
Data: 2024-12-27
Versão: 1.0
Status: EM IMPLEMENTAÇÃO
"""

from typing import List, Dict, Optional, Tuple, Any, Callable
from domain.models import Keyword
from shared.logger import logger
from datetime import datetime
import time
import uuid

from .configurador_nicho import ConfiguradorNicho
from .analisador_semantico_processor import AnalisadorSemanticoProcessor
from .calculador_scores_processor import CalculadorScoresProcessor
from .validador_avancado_processor import ValidadorAvancadoProcessor
from .aplicador_ml_processor import AplicadorMLProcessor
from .auditor_final_processor import AuditorFinalProcessor

# Integração com padrões de resiliência da Fase 1
from infrastructure.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, circuit_breaker
from infrastructure.resilience.retry_strategy import RetryConfig, RetryStrategy, retry
from infrastructure.resilience.bulkhead import BulkheadConfig, bulkhead
from infrastructure.resilience.timeout_manager import TimeoutConfig, timeout

class ProcessadorOrquestrador:
    """
    Orquestrador principal que coordena o processamento de keywords.
    
    Responsabilidades:
    - Coordenar o fluxo de processamento
    - Gerenciar dependências entre processadores
    - Coletar métricas de performance
    - Garantir rastreabilidade completa
    """
    
    def __init__(self):
        """Inicializa o orquestrador com todos os processadores."""
        self.tracing_id = f"ORCH_{uuid.uuid4().hex[:8]}"
        
        # Inicializar processadores
        self.configurador = ConfiguradorNicho()
        self.analisador_semantico = AnalisadorSemanticoProcessor()
        self.calculador_scores = CalculadorScoresProcessor()
        self.validador_avancado = ValidadorAvancadoProcessor()
        self.aplicador_ml = AplicadorMLProcessor()
        self.auditor_final = AuditorFinalProcessor()
        
        # Métricas
        self.metricas = {
            "tempo_inicio": None,
            "tempo_fim": None,
            "tempo_por_processador": {},
            "total_keywords_inicial": 0,
            "total_keywords_final": 0,
            "erros_processamento": 0
        }
        
        self._log_inicializacao()
        
        # Configurações de resiliência da Fase 1
        self._setup_resilience_patterns()
    
    def _setup_resilience_patterns(self):
        """Configura os padrões de resiliência da Fase 1"""
        # Circuit Breaker para processamento
        self.processing_circuit_breaker = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                name="processing_orchestrator",
                fallback_function=self._fallback_processing_error
            )
        )
        
        # Configurações de retry
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=10.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF
        )
        
        # Configurações de bulkhead
        self.bulkhead_config = BulkheadConfig(
            max_concurrent_calls=15,
            max_wait_duration=10.0,
            max_failure_count=3,
            name="processing_orchestrator"
        )
        
        # Configurações de timeout
        self.timeout_config = TimeoutConfig(
            timeout_seconds=120.0,
            name="processing_orchestrator"
        )

    def _fallback_processing_error(self, *args, **kwargs):
        """Fallback quando processamento falha"""
        logger.warning("Processamento falhou, usando fallback")
        return [], {"error": "Processamento indisponível", "fallback": True}
    
    @retry(max_attempts=3, base_delay=1.0, max_delay=10.0)
    @bulkhead(max_concurrent_calls=15, max_wait_duration=10.0)
    @timeout(timeout_seconds=120.0)
    def processar_keywords(
        self,
        keywords: List[Keyword],
        nicho: Optional[str] = None,
        idioma: str = "pt",
        callback_progresso: Optional[Callable[[str, int, int], None]] = None
    ) -> Tuple[List[Keyword], Dict[str, Any]]:
        """
        Processa keywords usando processadores especializados.
        
        Args:
            keywords: Lista de keywords a processar
            nicho: Nicho específico para configuração
            idioma: Idioma para processamento
            callback_progresso: Callback para progresso
            
        Returns:
            Tupla (keywords processadas, relatório completo)
        """
        self.metricas["tempo_inicio"] = time.time()
        self.metricas["total_keywords_inicial"] = len(keywords)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "iniciando_processamento_orquestrado",
            "status": "info",
            "source": "ProcessadorOrquestrador.processar_keywords",
            "tracing_id": self.tracing_id,
            "details": {
                "total_keywords": len(keywords),
                "nicho": nicho,
                "idioma": idioma
            }
        })
        
        try:
            # 1. Configurar nicho
            if callback_progresso:
                callback_progresso("Configurando nicho", 1, 6)
            
            config_nicho = self.configurador.configurar(nicho, idioma)
            
            # 2. Análise semântica
            if callback_progresso:
                callback_progresso("Análise semântica", 2, 6)
            
            keywords_analisadas = self.analisador_semantico.processar(
                keywords, config_nicho
            )
            
            # 3. Cálculo de scores
            if callback_progresso:
                callback_progresso("Cálculo de scores", 3, 6)
            
            keywords_scores = self.calculador_scores.processar(
                keywords_analisadas
            )
            
            # 4. Validação avançada
            if callback_progresso:
                callback_progresso("Validação avançada", 4, 6)
            
            keywords_validadas = self.validador_avancado.processar(
                keywords_scores, config_nicho
            )
            
            # 5. Aplicar ML
            if callback_progresso:
                callback_progresso("Aplicando ML", 5, 6)
            
            keywords_ml = self.aplicador_ml.processar(keywords_validadas)
            
            # 6. Auditoria final
            if callback_progresso:
                callback_progresso("Auditoria final", 6, 6)
            
            keywords_finais = self.auditor_final.processar(keywords_ml)
            
            # Finalizar métricas
            self.metricas["tempo_fim"] = time.time()
            self.metricas["total_keywords_final"] = len(keywords_finais)
            
            # Gerar relatório
            relatorio = self._gerar_relatorio(keywords_finais, config_nicho)
            
            # Log de conclusão
            self._log_conclusao(keywords_finais, relatorio)
            
            return keywords_finais, relatorio
            
        except Exception as e:
            self.metricas["erros_processamento"] += 1
            self.metricas["tempo_fim"] = time.time()
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_processamento_orquestrado",
                "status": "error",
                "source": "ProcessadorOrquestrador.processar_keywords",
                "tracing_id": self.tracing_id,
                "details": {
                    "erro": str(e),
                    "total_keywords": len(keywords)
                }
            })
            raise
    
    def _log_inicializacao(self):
        """Registra inicialização do orquestrador."""
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "orquestrador_inicializado",
            "status": "success",
            "source": "ProcessadorOrquestrador._log_inicializacao",
            "tracing_id": self.tracing_id,
            "details": {
                "processadores": [
                    "configurador",
                    "analisador_semantico",
                    "calculador_scores",
                    "validador_avancado",
                    "aplicador_ml",
                    "auditor_final"
                ]
            }
        })
    
    def _gerar_relatorio(
        self, 
        keywords: List[Keyword], 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera relatório completo do processamento."""
        tempo_total = self.metricas["tempo_fim"] - self.metricas["tempo_inicio"]
        
        return {
            "processamento": {
                "tempo_total": tempo_total,
                "total_keywords_inicial": self.metricas["total_keywords_inicial"],
                "total_keywords_final": self.metricas["total_keywords_final"],
                "keywords_aprovadas": len(keywords),
                "keywords_rejeitadas": self.metricas["total_keywords_inicial"] - len(keywords),
                "erros_processamento": self.metricas["erros_processamento"]
            },
            "tempo_por_processador": self.metricas["tempo_por_processador"],
            "configuracao": config,
            "tracing_id": self.tracing_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _log_conclusao(self, keywords: List[Keyword], relatorio: Dict[str, Any]):
        """Registra conclusão do processamento."""
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "processamento_orquestrado_concluido",
            "status": "success",
            "source": "ProcessadorOrquestrador._log_conclusao",
            "tracing_id": self.tracing_id,
            "details": {
                "keywords_processadas": len(keywords),
                "tempo_total": relatorio["processamento"]["tempo_total"],
                "erros": relatorio["processamento"]["erros_processamento"]
            }
        })
    
    def obter_metricas(self) -> Dict[str, Any]:
        """Obtém métricas do processamento."""
        return self.metricas.copy() 
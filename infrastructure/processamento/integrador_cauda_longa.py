"""
Integrador Principal de Cauda Longa - Omni Keywords Finder
Responsável por integrar todos os módulos de processamento de cauda longa.

Prompt: CHECKLIST_LONG_TAIL_V1.md - Integração Completa
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-20
Versão: 1.0.0
Tracing ID: LONGTAIL_INTEGRATION_001
"""

from typing import List, Dict, Optional, Tuple, Any, Callable
from domain.models import Keyword, IntencaoBusca
from shared.logger import logger
from datetime import datetime
import uuid
import time
import json
from dataclasses import dataclass
from enum import Enum

# Importar todos os módulos de cauda longa
from .analisador_semantico_cauda_longa import AnalisadorSemanticoCaudaLonga
from .complexidade_semantica import ComplexidadeSemantica
from .score_competitivo import ScoreCompetitivo
from .logs_cauda_longa import LogsCaudaLonga
from .score_composto_inteligente import ScoreCompostoInteligente
from .configuracao_adaptativa import ConfiguracaoAdaptativa
from .validador_cauda_longa_avancado import ValidadorCaudaLongaAvancado
from .tendencias_cauda_longa import TendenciasCaudaLonga

# Importar módulos de feedback e auditoria
from ..feedback.feedback_cauda_longa import FeedbackCaudaLonga
from ..audit.auditoria_qualidade_cauda_longa import AuditoriaQualidadeCaudaLonga

# Importar módulos de cache e ML
from ..cache.cache_inteligente_cauda_longa import CacheInteligenteCaudaLonga
from ..ml.ajuste_automatico_cauda_longa import AjusteAutomaticoCaudaLonga

class EstrategiaIntegracao(Enum):
    """Estratégias de integração disponíveis."""
    CASCATA = "cascata"
    PARALELA = "paralela"
    ADAPTATIVA = "adaptativa"
    ML_DRIVEN = "ml_driven"

@dataclass
class ConfiguracaoIntegracao:
    """Configuração para integração de cauda longa."""
    estrategia: EstrategiaIntegracao = EstrategiaIntegracao.CASCATA
    ativar_ml: bool = True
    ativar_cache: bool = True
    ativar_feedback: bool = True
    ativar_auditoria: bool = True
    ativar_tendencias: bool = True
    paralelizar: bool = False
    max_workers: int = 4
    timeout_segundos: int = 300
    log_detalhado: bool = True
    nicho: Optional[str] = None
    idioma: str = "pt"

class MetricasIntegracao:
    """Métricas de performance da integração."""
    
    def __init__(self):
        self.tempo_inicio = None
        self.tempo_fim = None
        self.total_keywords_inicial = 0
        self.total_keywords_final = 0
        self.keywords_aprovadas = 0
        self.keywords_rejeitadas = 0
        self.erros_processamento = 0
        self.tempo_por_modulo = {}
        self.versao_ml = None
        self.score_medio = 0.0
        self.complexidade_media = 0.0
        self.competitividade_media = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte métricas para dicionário."""
        return {
            "tempo_total": self.tempo_fim - self.tempo_inicio if self.tempo_fim and self.tempo_inicio else 0,
            "total_keywords_inicial": self.total_keywords_inicial,
            "total_keywords_final": self.total_keywords_final,
            "keywords_aprovadas": self.keywords_aprovadas,
            "keywords_rejeitadas": self.keywords_rejeitadas,
            "erros_processamento": self.erros_processamento,
            "tempo_por_modulo": self.tempo_por_modulo,
            "versao_ml": self.versao_ml,
            "score_medio": self.score_medio,
            "complexidade_media": self.complexidade_media,
            "competitividade_media": self.competitividade_media,
            "timestamp": datetime.utcnow().isoformat()
        }

class IntegradorCaudaLonga:
    """
    Integrador principal que conecta todos os módulos de cauda longa.
    
    Responsabilidades:
    - Orquestrar o fluxo de processamento
    - Gerenciar dependências entre módulos
    - Coletar métricas de performance
    - Garantir rastreabilidade completa
    - Aplicar estratégias de integração
    """
    
    def __init__(self, config: Optional[ConfiguracaoIntegracao] = None):
        """
        Inicializa o integrador com configuração.
        
        Args:
            config: Configuração da integração
        """
        self.config = config or ConfiguracaoIntegracao()
        self.tracing_id = f"LONGTAIL_INT_{uuid.uuid4().hex[:8]}"
        self.metricas = MetricasIntegracao()
        
        # Inicializar módulos principais
        self._inicializar_modulos()
        
        # Registrar inicialização
        self._log_inicializacao()
    
    def _inicializar_modulos(self):
        """Inicializa todos os módulos de cauda longa."""
        try:
            # Módulos de análise semântica
            self.analisador_semantico = AnalisadorSemanticoCaudaLonga()
            self.complexidade_semantica = ComplexidadeSemantica()
            
            # Módulos de score e competitividade
            self.score_competitivo = ScoreCompetitivo()
            self.score_composto = ScoreCompostoInteligente()
            
            # Módulos de configuração e validação
            self.configuracao_adaptativa = ConfiguracaoAdaptativa()
            self.validador_avancado = ValidadorCaudaLongaAvancado()
            
            # Módulos de tendências e logs
            self.tendencias = TendenciasCaudaLonga()
            self.logs_cauda_longa = LogsCaudaLonga()
            
            # Módulos de feedback e auditoria
            if self.config.ativar_feedback:
                self.feedback = FeedbackCaudaLonga()
            
            if self.config.ativar_auditoria:
                self.auditoria = AuditoriaQualidadeCaudaLonga()
            
            # Módulos de cache e ML
            if self.config.ativar_cache:
                self.cache = CacheInteligenteCaudaLonga()
            
            if self.config.ativar_ml:
                self.ml_ajuste = AjusteAutomaticoCaudaLonga()
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "modulos_cauda_longa_inicializados",
                "status": "success",
                "source": "IntegradorCaudaLonga._inicializar_modulos",
                "tracing_id": self.tracing_id,
                "details": {
                    "modulos_ativos": self._listar_modulos_ativos(),
                    "estrategia": self.config.estrategia.value
                }
            })
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_inicializacao_modulos",
                "status": "error",
                "source": "IntegradorCaudaLonga._inicializar_modulos",
                "tracing_id": self.tracing_id,
                "details": {"erro": str(e)}
            })
            raise
    
    def _listar_modulos_ativos(self) -> List[str]:
        """Lista módulos ativos na integração."""
        modulos = [
            "analisador_semantico",
            "complexidade_semantica", 
            "score_competitivo",
            "score_composto",
            "configuracao_adaptativa",
            "validador_avancado",
            "tendencias",
            "logs_cauda_longa"
        ]
        
        if self.config.ativar_feedback:
            modulos.append("feedback")
        if self.config.ativar_auditoria:
            modulos.append("auditoria")
        if self.config.ativar_cache:
            modulos.append("cache")
        if self.config.ativar_ml:
            modulos.append("ml_ajuste")
        
        return modulos
    
    def _log_inicializacao(self):
        """Registra log de inicialização."""
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "integrador_cauda_longa_inicializado",
            "status": "success",
            "source": "IntegradorCaudaLonga.__init__",
            "tracing_id": self.tracing_id,
            "details": {
                "configuracao": {
                    "estrategia": self.config.estrategia.value,
                    "ativar_ml": self.config.ativar_ml,
                    "ativar_cache": self.config.ativar_cache,
                    "ativar_feedback": self.config.ativar_feedback,
                    "ativar_auditoria": self.config.ativar_auditoria,
                    "ativar_tendencias": self.config.ativar_tendencias,
                    "paralelizar": self.config.paralelizar,
                    "max_workers": self.config.max_workers,
                    "timeout_segundos": self.config.timeout_segundos,
                    "log_detalhado": self.config.log_detalhado,
                    "nicho": self.config.nicho,
                    "idioma": self.config.idioma
                }
            }
        })
    
    def processar_keywords(
        self,
        keywords: List[Keyword],
        nicho: Optional[str] = None,
        idioma: str = "pt",
        estrategia: Optional[EstrategiaIntegracao] = None,
        callback_progresso: Optional[Callable[[str, int, int], None]] = None
    ) -> Tuple[List[Keyword], Dict[str, Any]]:
        """
        Processa keywords usando todos os módulos de cauda longa.
        
        Args:
            keywords: Lista de keywords a processar
            nicho: Nicho específico para configuração adaptativa
            idioma: Idioma para processamento
            estrategia: Estratégia de integração (sobrescreve configuração)
            callback_progresso: Callback para progresso
            
        Returns:
            Tupla (keywords processadas, relatório completo)
        """
        self.metricas.tempo_inicio = time.time()
        self.metricas.total_keywords_inicial = len(keywords)
        
        estrategia_final = estrategia or self.config.estrategia
        nicho_final = nicho or self.config.nicho
        idioma_final = idioma or self.config.idioma
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "iniciando_processamento_cauda_longa",
            "status": "info",
            "source": "IntegradorCaudaLonga.processar_keywords",
            "tracing_id": self.tracing_id,
            "details": {
                "total_keywords": len(keywords),
                "estrategia": estrategia_final.value,
                "nicho": nicho_final,
                "idioma": idioma_final
            }
        })
        
        try:
            # 1. Configuração adaptativa por nicho
            if callback_progresso:
                callback_progresso("Configurando para nicho", 1, 10)
            
            config_nicho = self._configurar_nicho(nicho_final, idioma_final)
            
            # 2. Análise semântica inicial
            if callback_progresso:
                callback_progresso("Análise semântica", 2, 10)
            
            keywords_analisadas = self._analisar_semantica(keywords, config_nicho)
            
            # 3. Cálculo de complexidade
            if callback_progresso:
                callback_progresso("Cálculo de complexidade", 3, 10)
            
            keywords_complexidade = self._calcular_complexidade(keywords_analisadas)
            
            # 4. Score competitivo
            if callback_progresso:
                callback_progresso("Score competitivo", 4, 10)
            
            keywords_competitivas = self._calcular_score_competitivo(keywords_complexidade)
            
            # 5. Score composto inteligente
            if callback_progresso:
                callback_progresso("Score composto", 5, 10)
            
            keywords_score_composto = self._calcular_score_composto(keywords_competitivas)
            
            # 6. Análise de tendências
            if callback_progresso and self.config.ativar_tendencias:
                callback_progresso("Análise de tendências", 6, 10)
            
            keywords_tendencias = self._analisar_tendencias(keywords_score_composto)
            
            # 7. Validação avançada
            if callback_progresso:
                callback_progresso("Validação avançada", 7, 10)
            
            keywords_validadas = self._validar_avancado(keywords_tendencias, config_nicho)
            
            # 8. Aplicar ML se ativado
            if self.config.ativar_ml and callback_progresso:
                callback_progresso("Ajuste ML", 8, 10)
            
            keywords_ml = self._aplicar_ml(keywords_validadas)
            
            # 9. Feedback e aprendizado
            if self.config.ativar_feedback and callback_progresso:
                callback_progresso("Feedback e aprendizado", 9, 10)
            
            keywords_feedback = self._aplicar_feedback(keywords_ml)
            
            # 10. Auditoria final
            if callback_progresso:
                callback_progresso("Auditoria final", 10, 10)
            
            keywords_finais = self._auditoria_final(keywords_feedback)
            
            # Finalizar métricas
            self.metricas.tempo_fim = time.time()
            self.metricas.total_keywords_final = len(keywords_finais)
            self.metricas.keywords_aprovadas = len(keywords_finais)
            self.metricas.keywords_rejeitadas = self.metricas.total_keywords_inicial - len(keywords_finais)
            
            # Gerar relatório completo
            relatorio = self._gerar_relatorio_completo(keywords_finais, config_nicho)
            
            # Log de conclusão
            self._log_conclusao(keywords_finais, relatorio)
            
            return keywords_finais, relatorio
            
        except Exception as e:
            self.metricas.erros_processamento += 1
            self.metricas.tempo_fim = time.time()
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_processamento_cauda_longa",
                "status": "error",
                "source": "IntegradorCaudaLonga.processar_keywords",
                "tracing_id": self.tracing_id,
                "details": {
                    "erro": str(e),
                    "total_keywords": len(keywords),
                    "estrategia": estrategia_final.value
                }
            })
            raise
    
    def _configurar_nicho(self, nicho: Optional[str], idioma: str) -> Dict[str, Any]:
        """Configura parâmetros específicos do nicho."""
        tempo_inicio = time.time()
        
        try:
            config = self.configuracao_adaptativa.obter_configuraco_nicho(
                nicho=nicho,
                idioma=idioma
            )
            
            self.metricas.tempo_por_modulo["configuracao_nicho"] = time.time() - tempo_inicio
            
            return config
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_configuracao_nicho",
                "status": "error",
                "source": "IntegradorCaudaLonga._configurar_nicho",
                "tracing_id": self.tracing_id,
                "details": {"nicho": nicho, "erro": str(e)}
            })
            return {}
    
    def _analisar_semantica(self, keywords: List[Keyword], config: Dict[str, Any]) -> List[Keyword]:
        """Aplica análise semântica nas keywords."""
        tempo_inicio = time.time()
        
        try:
            keywords_analisadas = []
            
            for kw in keywords:
                analise = self.analisador_semantico.analisar_keyword(
                    kw.termo,
                    config=config
                )
                
                # Atualizar keyword com análise semântica
                kw.palavras_significativas = analise.get("palavras_significativas", 0)
                kw.densidade_semantica = analise.get("densidade_semantica", 0.0)
                kw.especificidade = analise.get("especificidade", 0.0)
                
                keywords_analisadas.append(kw)
            
            self.metricas.tempo_por_modulo["analise_semantica"] = time.time() - tempo_inicio
            
            return keywords_analisadas
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_analise_semantica",
                "status": "error",
                "source": "IntegradorCaudaLonga._analisar_semantica",
                "tracing_id": self.tracing_id,
                "details": {"erro": str(e)}
            })
            return keywords
    
    def _calcular_complexidade(self, keywords: List[Keyword]) -> List[Keyword]:
        """Calcula complexidade semântica das keywords."""
        tempo_inicio = time.time()
        
        try:
            keywords_complexidade = []
            
            for kw in keywords:
                complexidade = self.complexidade_semantica.calcular_complexidade(
                    kw.termo
                )
                
                # Atualizar keyword com complexidade
                kw.complexidade_semantica = complexidade.get("complexidade", 0.0)
                kw.palavras_unicas = complexidade.get("palavras_unicas", 0)
                kw.densidade_informativa = complexidade.get("densidade_informativa", 0.0)
                
                keywords_complexidade.append(kw)
            
            self.metricas.tempo_por_modulo["calculo_complexidade"] = time.time() - tempo_inicio
            
            return keywords_complexidade
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_calculo_complexidade",
                "status": "error",
                "source": "IntegradorCaudaLonga._calcular_complexidade",
                "tracing_id": self.tracing_id,
                "details": {"erro": str(e)}
            })
            return keywords
    
    def _calcular_score_competitivo(self, keywords: List[Keyword]) -> List[Keyword]:
        """Calcula score competitivo das keywords."""
        tempo_inicio = time.time()
        
        try:
            keywords_competitivas = []
            
            for kw in keywords:
                score = self.score_competitivo.calcular_score_competitivo(
                    kw.termo,
                    volume_busca=kw.volume_busca or 0,
                    cpc=kw.cpc or 0.0,
                    concorrencia=kw.concorrencia or 0.0
                )
                
                # Atualizar keyword com score competitivo
                kw.score_competitivo = score.get("score", 0.0)
                kw.nivel_competitividade = score.get("nivel_competitividade", "baixa")
                kw.volume_normalizado = score.get("volume_normalizado", 0.0)
                kw.cpc_normalizado = score.get("cpc_normalizado", 0.0)
                
                keywords_competitivas.append(kw)
            
            self.metricas.tempo_por_modulo["score_competitivo"] = time.time() - tempo_inicio
            
            return keywords_competitivas
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_score_competitivo",
                "status": "error",
                "source": "IntegradorCaudaLonga._calcular_score_competitivo",
                "tracing_id": self.tracing_id,
                "details": {"erro": str(e)}
            })
            return keywords
    
    def _calcular_score_composto(self, keywords: List[Keyword]) -> List[Keyword]:
        """Calcula score composto inteligente das keywords."""
        tempo_inicio = time.time()
        
        try:
            keywords_score_composto = []
            
            for kw in keywords:
                score_composto = self.score_composto.calcular_score_composto(
                    kw.termo,
                    complexidade=kw.complexidade_semantica or 0.0,
                    especificidade=kw.especificidade or 0.0,
                    competitividade=kw.score_competitivo or 0.0,
                    tendencia=kw.score_tendencia or 0.0
                )
                
                # Atualizar keyword com score composto
                kw.score_composto = score_composto.get("score_composto", 0.0)
                kw.classificacao_qualidade = score_composto.get("classificacao", "baixa")
                kw.pesos_aplicados = score_composto.get("pesos", {})
                
                keywords_score_composto.append(kw)
            
            self.metricas.tempo_por_modulo["score_composto"] = time.time() - tempo_inicio
            
            return keywords_score_composto
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_score_composto",
                "status": "error",
                "source": "IntegradorCaudaLonga._calcular_score_composto",
                "tracing_id": self.tracing_id,
                "details": {"erro": str(e)}
            })
            return keywords
    
    def _analisar_tendencias(self, keywords: List[Keyword]) -> List[Keyword]:
        """Analisa tendências das keywords."""
        if not self.config.ativar_tendencias:
            return keywords
        
        tempo_inicio = time.time()
        
        try:
            keywords_tendencias = []
            
            for kw in keywords:
                tendencia = self.tendencias.analisar_tendencia(
                    kw.termo
                )
                
                # Atualizar keyword com análise de tendência
                kw.score_tendencia = tendencia.get("score_tendencia", 0.0)
                kw.tendencia_direcao = tendencia.get("direcao", "estavel")
                kw.tendencia_forca = tendencia.get("forca", "fraca")
                kw.emergente = tendencia.get("emergente", False)
                
                keywords_tendencias.append(kw)
            
            self.metricas.tempo_por_modulo["analise_tendencias"] = time.time() - tempo_inicio
            
            return keywords_tendencias
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_analise_tendencias",
                "status": "error",
                "source": "IntegradorCaudaLonga._analisar_tendencias",
                "tracing_id": self.tracing_id,
                "details": {"erro": str(e)}
            })
            return keywords
    
    def _validar_avancado(self, keywords: List[Keyword], config: Dict[str, Any]) -> List[Keyword]:
        """Aplica validação avançada nas keywords."""
        tempo_inicio = time.time()
        
        try:
            keywords_validadas = self.validador_avancado.validar_keywords(
                keywords,
                config=config
            )
            
            self.metricas.tempo_por_modulo["validacao_avancada"] = time.time() - tempo_inicio
            
            return keywords_validadas
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_validacao_avancada",
                "status": "error",
                "source": "IntegradorCaudaLonga._validar_avancado",
                "tracing_id": self.tracing_id,
                "details": {"erro": str(e)}
            })
            return keywords
    
    def _aplicar_ml(self, keywords: List[Keyword]) -> List[Keyword]:
        """Aplica ajustes de ML nas keywords."""
        if not self.config.ativar_ml:
            return keywords
        
        tempo_inicio = time.time()
        
        try:
            keywords_ml = self.ml_ajuste.ajustar_keywords(
                keywords
            )
            
            self.metricas.tempo_por_modulo["ajuste_ml"] = time.time() - tempo_inicio
            self.metricas.versao_ml = getattr(self.ml_ajuste, 'versao', '1.0.0')
            
            return keywords_ml
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_ajuste_ml",
                "status": "error",
                "source": "IntegradorCaudaLonga._aplicar_ml",
                "tracing_id": self.tracing_id,
                "details": {"erro": str(e)}
            })
            return keywords
    
    def _aplicar_feedback(self, keywords: List[Keyword]) -> List[Keyword]:
        """Aplica feedback e aprendizado nas keywords."""
        if not self.config.ativar_feedback:
            return keywords
        
        tempo_inicio = time.time()
        
        try:
            keywords_feedback = self.feedback.aplicar_feedback(
                keywords
            )
            
            self.metricas.tempo_por_modulo["feedback"] = time.time() - tempo_inicio
            
            return keywords_feedback
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_feedback",
                "status": "error",
                "source": "IntegradorCaudaLonga._aplicar_feedback",
                "tracing_id": self.tracing_id,
                "details": {"erro": str(e)}
            })
            return keywords
    
    def _auditoria_final(self, keywords: List[Keyword]) -> List[Keyword]:
        """Aplica auditoria final nas keywords."""
        if not self.config.ativar_auditoria:
            return keywords
        
        tempo_inicio = time.time()
        
        try:
            keywords_auditoria = self.auditoria.auditar_keywords(
                keywords
            )
            
            self.metricas.tempo_por_modulo["auditoria"] = time.time() - tempo_inicio
            
            return keywords_auditoria
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_auditoria",
                "status": "error",
                "source": "IntegradorCaudaLonga._auditoria_final",
                "tracing_id": self.tracing_id,
                "details": {"erro": str(e)}
            })
            return keywords
    
    def _gerar_relatorio_completo(self, keywords: List[Keyword], config: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório completo do processamento."""
        try:
            # Calcular métricas finais
            scores = [kw.score_composto or 0.0 for kw in keywords if kw.score_composto]
            complexidades = [kw.complexidade_semantica or 0.0 for kw in keywords if kw.complexidade_semantica]
            competitividades = [kw.score_competitivo or 0.0 for kw in keywords if kw.score_competitivo]
            
            self.metricas.score_medio = sum(scores) / len(scores) if scores else 0.0
            self.metricas.complexidade_media = sum(complexidades) / len(complexidades) if complexidades else 0.0
            self.metricas.competitividade_media = sum(competitividades) / len(competitividades) if competitividades else 0.0
            
            relatorio = {
                "tracing_id": self.tracing_id,
                "timestamp": datetime.utcnow().isoformat(),
                "configuracao": {
                    "estrategia": self.config.estrategia.value,
                    "nicho": self.config.nicho,
                    "idioma": self.config.idioma,
                    "modulos_ativos": self._listar_modulos_ativos()
                },
                "metricas_processamento": self.metricas.to_dict(),
                "keywords_processadas": len(keywords),
                "distribuicao_scores": {
                    "excelente": len([key for key in keywords if (key.score_composto or 0) >= 0.8]),
                    "boa": len([key for key in keywords if 0.6 <= (key.score_composto or 0) < 0.8]),
                    "media": len([key for key in keywords if 0.4 <= (key.score_composto or 0) < 0.6]),
                    "baixa": len([key for key in keywords if (key.score_composto or 0) < 0.4])
                },
                "distribuicao_complexidade": {
                    "alta": len([key for key in keywords if (key.complexidade_semantica or 0) >= 0.7]),
                    "media": len([key for key in keywords if 0.4 <= (key.complexidade_semantica or 0) < 0.7]),
                    "baixa": len([key for key in keywords if (key.complexidade_semantica or 0) < 0.4])
                },
                "distribuicao_competitividade": {
                    "alta": len([key for key in keywords if (key.score_competitivo or 0) >= 0.7]),
                    "media": len([key for key in keywords if 0.4 <= (key.score_competitivo or 0) < 0.7]),
                    "baixa": len([key for key in keywords if (key.score_competitivo or 0) < 0.4])
                },
                "tendencias_detectadas": len([key for key in keywords if key.emergente]),
                "versao_integrador": "1.0.0"
            }
            
            return relatorio
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_geracao_relatorio",
                "status": "error",
                "source": "IntegradorCaudaLonga._gerar_relatorio_completo",
                "tracing_id": self.tracing_id,
                "details": {"erro": str(e)}
            })
            return {"erro": str(e)}
    
    def _log_conclusao(self, keywords: List[Keyword], relatorio: Dict[str, Any]):
        """Registra log de conclusão do processamento."""
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "processamento_cauda_longa_concluido",
            "status": "success",
            "source": "IntegradorCaudaLonga.processar_keywords",
            "tracing_id": self.tracing_id,
            "details": {
                "total_keywords_final": len(keywords),
                "tempo_total": self.metricas.tempo_fim - self.metricas.tempo_inicio if self.metricas.tempo_fim and self.metricas.tempo_inicio else 0,
                "score_medio": self.metricas.score_medio,
                "complexidade_media": self.metricas.complexidade_media,
                "competitividade_media": self.metricas.competitividade_media
            }
        })
    
    def obter_metricas(self) -> Dict[str, Any]:
        """Retorna métricas completas da integração."""
        return self.metricas.to_dict()
    
    def obter_status_modulos(self) -> Dict[str, str]:
        """Retorna status de todos os módulos."""
        return {
            "analisador_semantico": "ativo",
            "complexidade_semantica": "ativo",
            "score_competitivo": "ativo",
            "score_composto": "ativo",
            "configuracao_adaptativa": "ativo",
            "validador_avancado": "ativo",
            "tendencias": "ativo" if self.config.ativar_tendencias else "inativo",
            "logs_cauda_longa": "ativo",
            "feedback": "ativo" if self.config.ativar_feedback else "inativo",
            "auditoria": "ativo" if self.config.ativar_auditoria else "inativo",
            "cache": "ativo" if self.config.ativar_cache else "inativo",
            "ml_ajuste": "ativo" if self.config.ativar_ml else "inativo"
        } 
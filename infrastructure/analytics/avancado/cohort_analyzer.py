"""
Sistema de Análise de Coortes Avançado
======================================

Este módulo implementa análise de coortes com:
- Segmentação automática de usuários
- Análise de retenção e engajamento
- Predição de churn com ML
- Análise de lifetime value (LTV)
- Relatórios automáticos
- Integração com observabilidade

Author: Paulo Júnior
Date: 2024-12-19
Tracing ID: ANALYTICS_002
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict
import statistics
import math

# Machine Learning imports
try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Integração com observabilidade
try:
    from infrastructure.observability.telemetry import TelemetryManager
    from infrastructure.observability.metrics import MetricsManager
    from infrastructure.observability.tracing import TracingManager
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False

# Cache Redis para persistência
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CohortType(Enum):
    """Tipos de coortes"""
    SIGNUP_DATE = "signup_date"
    FIRST_PURCHASE = "first_purchase"
    FEATURE_USAGE = "feature_usage"
    GEOGRAPHIC = "geographic"
    BEHAVIORAL = "behavioral"
    CUSTOM = "custom"


class RetentionPeriod(Enum):
    """Períodos de retenção"""
    DAY_1 = 1
    DAY_7 = 7
    DAY_30 = 30
    DAY_90 = 90
    DAY_180 = 180
    DAY_365 = 365


@dataclass
class CohortData:
    """Dados de uma coorte"""
    cohort_id: str
    cohort_type: CohortType
    cohort_date: datetime
    user_ids: List[str]
    total_users: int
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetentionData:
    """Dados de retenção"""
    cohort_id: str
    period: RetentionPeriod
    retained_users: int
    retention_rate: float
    churn_rate: float
    active_users: int
    engagement_score: float
    ltv_estimate: float


@dataclass
class CohortAnalysis:
    """Análise completa de coorte"""
    cohort_id: str
    cohort_type: CohortType
    cohort_date: datetime
    total_users: int
    retention_data: List[RetentionData]
    churn_prediction: Optional[float]
    ltv_prediction: Optional[float]
    engagement_trend: str
    risk_score: float
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)


class CohortAnalyzer:
    """
    Analisador avançado de coortes
    
    Características:
    - Segmentação automática de usuários
    - Análise de retenção e engajamento
    - Predição de churn com ML
    - Análise de lifetime value (LTV)
    - Relatórios automáticos
    - Integração com observabilidade
    """
    
    def __init__(self, 
                 analytics_data: Optional[Dict[str, Any]] = None,
                 enable_ml: bool = True,
                 enable_observability: bool = True,
                 redis_config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o analisador de coortes
        
        Args:
            analytics_data: Dados de analytics para análise
            enable_ml: Habilita predições com ML
            enable_observability: Habilita integração com observabilidade
            redis_config: Configuração do Redis
        """
        self.analytics_data = analytics_data or {}
        self.enable_ml = enable_ml and ML_AVAILABLE
        self.enable_observability = enable_observability and OBSERVABILITY_AVAILABLE
        
        # Cache de análises
        self.cohort_cache: Dict[str, CohortAnalysis] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Redis para cache distribuído
        self.redis_client = None
        if REDIS_AVAILABLE and redis_config:
            try:
                self.redis_client = redis.Redis(**redis_config)
                self.redis_client.ping()
                logger.info("Redis conectado para análise de coortes")
            except Exception as e:
                logger.warning(f"Falha ao conectar Redis: {e}")
        
        # Observabilidade
        self.telemetry = None
        self.metrics = None
        self.tracing = None
        
        if self.enable_observability:
            try:
                self.telemetry = TelemetryManager()
                self.metrics = MetricsManager()
                self.tracing = TracingManager()
                logger.info("Observabilidade integrada à análise de coortes")
            except Exception as e:
                logger.warning(f"Falha ao integrar observabilidade: {e}")
        
        # Modelos ML
        self.churn_model = None
        self.ltv_model = None
        self.scaler = None
        self.label_encoders = {}
        
        if self.enable_ml:
            self._initialize_ml_models()
        
        logger.info("Analisador de Coortes Avançado inicializado")
    
    def _initialize_ml_models(self):
        """Inicializa modelos de ML"""
        try:
            self.churn_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            self.ltv_model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            
            self.scaler = StandardScaler()
            
            logger.info("Modelos ML inicializados para análise de coortes")
        except Exception as e:
            logger.error(f"Falha ao inicializar modelos ML: {e}")
            self.enable_ml = False
    
    def create_cohorts(self, 
                      cohort_type: CohortType,
                      start_date: datetime,
                      end_date: datetime,
                      custom_properties: Optional[Dict[str, Any]] = None) -> List[CohortData]:
        """
        Cria coortes baseadas no tipo especificado
        
        Args:
            cohort_type: Tipo de coorte
            start_date: Data de início
            end_date: Data de fim
            custom_properties: Propriedades customizadas
            
        Returns:
            Lista de coortes criadas
        """
        with self._lock:
            try:
                if self.tracing:
                    with self.tracing.start_span("create_cohorts") as span:
                        span.set_attribute("cohort_type", cohort_type.value)
                        span.set_attribute("start_date", start_date.isoformat())
                        span.set_attribute("end_date", end_date.isoformat())
                
                cohorts = []
                
                if cohort_type == CohortType.SIGNUP_DATE:
                    cohorts = self._create_signup_cohorts(start_date, end_date)
                elif cohort_type == CohortType.FIRST_PURCHASE:
                    cohorts = self._create_purchase_cohorts(start_date, end_date)
                elif cohort_type == CohortType.FEATURE_USAGE:
                    cohorts = self._create_feature_cohorts(start_date, end_date)
                elif cohort_type == CohortType.GEOGRAPHIC:
                    cohorts = self._create_geographic_cohorts(start_date, end_date)
                elif cohort_type == CohortType.BEHAVIORAL:
                    cohorts = self._create_behavioral_cohorts(start_date, end_date)
                elif cohort_type == CohortType.CUSTOM:
                    cohorts = self._create_custom_cohorts(start_date, end_date, custom_properties)
                
                # Cache das coortes
                for cohort in cohorts:
                    cache_key = f"cohort:{cohort.cohort_id}"
                    if self.redis_client:
                        self.redis_client.setex(
                            cache_key,
                            3600,  # 1 hora
                            json.dumps(cohort.__dict__, default=str)
                        )
                
                # Métricas
                if self.metrics:
                    self.metrics.increment_counter(
                        "cohorts_created_total",
                        {"type": cohort_type.value, "count": len(cohorts)}
                    )
                
                logger.info(f"Criadas {len(cohorts)} coortes do tipo {cohort_type.value}")
                return cohorts
                
            except Exception as e:
                logger.error(f"Erro ao criar coortes: {e}")
                if self.metrics:
                    self.metrics.increment_counter("cohort_creation_errors_total")
                raise
    
    def _create_signup_cohorts(self, start_date: datetime, end_date: datetime) -> List[CohortData]:
        """Cria coortes baseadas na data de cadastro"""
        cohorts = []
        current_date = start_date
        
        while current_date <= end_date:
            # Simular dados de usuários (em produção, buscar do banco)
            user_ids = [f"user_{index}_{current_date.strftime('%Y%m%data')}" 
                       for index in range(10, 50)]  # 10-50 usuários por dia
            
            cohort = CohortData(
                cohort_id=f"signup_{current_date.strftime('%Y%m%data')}",
                cohort_type=CohortType.SIGNUP_DATE,
                cohort_date=current_date,
                user_ids=user_ids,
                total_users=len(user_ids),
                properties={
                    "source": "organic",
                    "campaign": "general"
                }
            )
            cohorts.append(cohort)
            current_date += timedelta(days=1)
        
        return cohorts
    
    def _create_purchase_cohorts(self, start_date: datetime, end_date: datetime) -> List[CohortData]:
        """Cria coortes baseadas na primeira compra"""
        cohorts = []
        current_date = start_date
        
        while current_date <= end_date:
            # Simular dados de compradores
            user_ids = [f"buyer_{index}_{current_date.strftime('%Y%m%data')}" 
                       for index in range(5, 25)]  # 5-25 compradores por dia
            
            cohort = CohortData(
                cohort_id=f"purchase_{current_date.strftime('%Y%m%data')}",
                cohort_type=CohortType.FIRST_PURCHASE,
                cohort_date=current_date,
                user_ids=user_ids,
                total_users=len(user_ids),
                properties={
                    "avg_order_value": 150.0,
                    "payment_method": "credit_card"
                }
            )
            cohorts.append(cohort)
            current_date += timedelta(days=1)
        
        return cohorts
    
    def _create_feature_cohorts(self, start_date: datetime, end_date: datetime) -> List[CohortData]:
        """Cria coortes baseadas no uso de features"""
        features = ["keyword_analysis", "competitor_tracking", "seo_optimization"]
        cohorts = []
        
        for feature in features:
            # Simular usuários por feature
            user_ids = [f"feature_{feature}_{index}" for index in range(20, 80)]
            
            cohort = CohortData(
                cohort_id=f"feature_{feature}_{start_date.strftime('%Y%m%data')}",
                cohort_type=CohortType.FEATURE_USAGE,
                cohort_date=start_date,
                user_ids=user_ids,
                total_users=len(user_ids),
                properties={
                    "feature": feature,
                    "usage_frequency": "daily"
                }
            )
            cohorts.append(cohort)
        
        return cohorts
    
    def _create_geographic_cohorts(self, start_date: datetime, end_date: datetime) -> List[CohortData]:
        """Cria coortes baseadas na localização geográfica"""
        regions = ["BR", "US", "EU", "ASIA"]
        cohorts = []
        
        for region in regions:
            # Simular usuários por região
            user_ids = [f"geo_{region}_{index}" for index in range(15, 60)]
            
            cohort = CohortData(
                cohort_id=f"geo_{region}_{start_date.strftime('%Y%m%data')}",
                cohort_type=CohortType.GEOGRAPHIC,
                cohort_date=start_date,
                user_ids=user_ids,
                total_users=len(user_ids),
                properties={
                    "region": region,
                    "timezone": "UTC-3" if region == "BR" else "UTC+0"
                }
            )
            cohorts.append(cohort)
        
        return cohorts
    
    def _create_behavioral_cohorts(self, start_date: datetime, end_date: datetime) -> List[CohortData]:
        """Cria coortes baseadas no comportamento"""
        behaviors = ["high_engagement", "low_engagement", "power_user", "casual_user"]
        cohorts = []
        
        for behavior in behaviors:
            # Simular usuários por comportamento
            user_ids = [f"behavior_{behavior}_{index}" for index in range(10, 40)]
            
            cohort = CohortData(
                cohort_id=f"behavior_{behavior}_{start_date.strftime('%Y%m%data')}",
                cohort_type=CohortType.BEHAVIORAL,
                cohort_date=start_date,
                user_ids=user_ids,
                total_users=len(user_ids),
                properties={
                    "behavior": behavior,
                    "session_duration": 30 if behavior == "high_engagement" else 5
                }
            )
            cohorts.append(cohort)
        
        return cohorts
    
    def _create_custom_cohorts(self, 
                              start_date: datetime, 
                              end_date: datetime,
                              custom_properties: Dict[str, Any]) -> List[CohortData]:
        """Cria coortes customizadas"""
        # Implementar lógica customizada baseada nas propriedades
        user_ids = [f"custom_{index}" for index in range(20, 50)]
        
        cohort = CohortData(
            cohort_id=f"custom_{start_date.strftime('%Y%m%data')}",
            cohort_type=CohortType.CUSTOM,
            cohort_date=start_date,
            user_ids=user_ids,
            total_users=len(user_ids),
            properties=custom_properties or {}
        )
        
        return [cohort]
    
    def analyze_cohort_retention(self, 
                               cohort_id: str,
                               periods: List[RetentionPeriod] = None) -> CohortAnalysis:
        """
        Analisa retenção de uma coorte específica
        
        Args:
            cohort_id: ID da coorte
            periods: Períodos de retenção para análise
            
        Returns:
            Análise completa da coorte
        """
        with self._lock:
            try:
                if self.tracing:
                    with self.tracing.start_span("analyze_cohort_retention") as span:
                        span.set_attribute("cohort_id", cohort_id)
                
                # Verificar cache
                if cohort_id in self.cohort_cache:
                    return self.cohort_cache[cohort_id]
                
                # Buscar coorte
                cohort = self._get_cohort(cohort_id)
                if not cohort:
                    raise ValueError(f"Coorte {cohort_id} não encontrada")
                
                periods = periods or list(RetentionPeriod)
                retention_data = []
                
                for period in periods:
                    retention = self._calculate_retention(cohort, period)
                    retention_data.append(retention)
                
                # Predições com ML
                churn_prediction = None
                ltv_prediction = None
                
                if self.enable_ml:
                    churn_prediction = self._predict_churn(cohort, retention_data)
                    ltv_prediction = self._predict_ltv(cohort, retention_data)
                
                # Análise de tendências
                engagement_trend = self._analyze_engagement_trend(retention_data)
                risk_score = self._calculate_risk_score(cohort, retention_data)
                recommendations = self._generate_recommendations(cohort, retention_data)
                
                analysis = CohortAnalysis(
                    cohort_id=cohort_id,
                    cohort_type=cohort.cohort_type,
                    cohort_date=cohort.cohort_date,
                    total_users=cohort.total_users,
                    retention_data=retention_data,
                    churn_prediction=churn_prediction,
                    ltv_prediction=ltv_prediction,
                    engagement_trend=engagement_trend,
                    risk_score=risk_score,
                    recommendations=recommendations
                )
                
                # Cache da análise
                self.cohort_cache[cohort_id] = analysis
                
                # Métricas
                if self.metrics:
                    self.metrics.record_histogram(
                        "cohort_analysis_duration_seconds",
                        time.time() - time.time(),
                        {"cohort_id": cohort_id}
                    )
                
                logger.info(f"Análise de coorte {cohort_id} concluída")
                return analysis
                
            except Exception as e:
                logger.error(f"Erro ao analisar coorte {cohort_id}: {e}")
                if self.metrics:
                    self.metrics.increment_counter("cohort_analysis_errors_total")
                raise
    
    def _get_cohort(self, cohort_id: str) -> Optional[CohortData]:
        """Busca coorte do cache ou banco"""
        # Verificar cache Redis
        if self.redis_client:
            try:
                cached = self.redis_client.get(f"cohort:{cohort_id}")
                if cached:
                    data = json.loads(cached)
                    return CohortData(**data)
            except Exception as e:
                logger.warning(f"Erro ao buscar coorte do Redis: {e}")
        
        # Em produção, buscar do banco de dados
        # Por simplicidade, retornamos None
        return None
    
    def _calculate_retention(self, cohort: CohortData, period: RetentionPeriod) -> RetentionData:
        """Calcula retenção para um período específico"""
        # Simular cálculo de retenção
        base_retention = 0.8  # 80% base
        period_factor = 1.0 - (period.value / 365.0) * 0.3  # Decaimento ao longo do tempo
        
        retention_rate = base_retention * period_factor
        retained_users = int(cohort.total_users * retention_rate)
        churn_rate = 1.0 - retention_rate
        
        # Simular usuários ativos e engajamento
        active_users = int(retained_users * 0.7)  # 70% dos retidos são ativos
        engagement_score = retention_rate * 0.8  # Score baseado na retenção
        
        # Simular LTV
        ltv_estimate = 150.0 * retention_rate * period_factor
        
        return RetentionData(
            cohort_id=cohort.cohort_id,
            period=period,
            retained_users=retained_users,
            retention_rate=retention_rate,
            churn_rate=churn_rate,
            active_users=active_users,
            engagement_score=engagement_score,
            ltv_estimate=ltv_estimate
        )
    
    def _predict_churn(self, cohort: CohortData, retention_data: List[RetentionData]) -> Optional[float]:
        """Prediz probabilidade de churn usando ML"""
        if not self.enable_ml or not retention_data:
            return None
        
        try:
            # Preparar features
            features = []
            for retention in retention_data:
                features.extend([
                    retention.retention_rate,
                    retention.churn_rate,
                    retention.engagement_score,
                    retention.period.value
                ])
            
            # Padronizar features
            features_scaled = self.scaler.fit_transform([features])
            
            # Predição (simulada)
            churn_probability = 0.15  # 15% de probabilidade de churn
            
            return churn_probability
            
        except Exception as e:
            logger.warning(f"Erro na predição de churn: {e}")
            return None
    
    def _predict_ltv(self, cohort: CohortData, retention_data: List[RetentionData]) -> Optional[float]:
        """Prediz lifetime value usando ML"""
        if not self.enable_ml or not retention_data:
            return None
        
        try:
            # Preparar features
            features = []
            for retention in retention_data:
                features.extend([
                    retention.retention_rate,
                    retention.ltv_estimate,
                    retention.engagement_score,
                    retention.period.value
                ])
            
            # Padronizar features
            features_scaled = self.scaler.fit_transform([features])
            
            # Predição (simulada)
            ltv_prediction = 200.0  # $200 de LTV predito
            
            return ltv_prediction
            
        except Exception as e:
            logger.warning(f"Erro na predição de LTV: {e}")
            return None
    
    def _analyze_engagement_trend(self, retention_data: List[RetentionData]) -> str:
        """Analisa tendência de engajamento"""
        if len(retention_data) < 2:
            return "insufficient_data"
        
        # Calcular tendência baseada no engajamento
        engagement_scores = [r.engagement_score for r in retention_data]
        
        if len(engagement_scores) >= 2:
            trend = engagement_scores[-1] - engagement_scores[0]
            
            if trend > 0.1:
                return "increasing"
            elif trend < -0.1:
                return "decreasing"
            else:
                return "stable"
        
        return "stable"
    
    def _calculate_risk_score(self, cohort: CohortData, retention_data: List[RetentionData]) -> float:
        """Calcula score de risco da coorte"""
        if not retention_data:
            return 0.5
        
        # Fatores de risco
        risk_factors = []
        
        # Retenção baixa
        avg_retention = statistics.mean([r.retention_rate for r in retention_data])
        if avg_retention < 0.5:
            risk_factors.append(0.3)
        
        # Churn alto
        avg_churn = statistics.mean([r.churn_rate for r in retention_data])
        if avg_churn > 0.5:
            risk_factors.append(0.4)
        
        # Engajamento baixo
        avg_engagement = statistics.mean([r.engagement_score for r in retention_data])
        if avg_engagement < 0.3:
            risk_factors.append(0.3)
        
        # Tamanho da coorte pequeno
        if cohort.total_users < 20:
            risk_factors.append(0.2)
        
        # Calcular score final
        risk_score = sum(risk_factors) if risk_factors else 0.1
        return min(risk_score, 1.0)
    
    def _generate_recommendations(self, cohort: CohortData, retention_data: List[RetentionData]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        if not retention_data:
            return ["Dados insuficientes para gerar recomendações"]
        
        avg_retention = statistics.mean([r.retention_rate for r in retention_data])
        avg_churn = statistics.mean([r.churn_rate for r in retention_data])
        avg_engagement = statistics.mean([r.engagement_score for r in retention_data])
        
        if avg_retention < 0.6:
            recommendations.append("Implementar programa de onboarding melhorado")
            recommendations.append("Criar campanhas de re-engajamento")
        
        if avg_churn > 0.4:
            recommendations.append("Analisar motivos de cancelamento")
            recommendations.append("Implementar programa de fidelização")
        
        if avg_engagement < 0.4:
            recommendations.append("Melhorar experiência do usuário")
            recommendations.append("Adicionar funcionalidades gamificadas")
        
        if cohort.total_users < 50:
            recommendations.append("Aumentar esforços de aquisição")
            recommendations.append("Otimizar campanhas de marketing")
        
        if not recommendations:
            recommendations.append("Coorte performando bem - manter estratégias atuais")
        
        return recommendations
    
    def generate_cohort_report(self, cohort_id: str) -> Dict[str, Any]:
        """
        Gera relatório completo de coorte
        
        Args:
            cohort_id: ID da coorte
            
        Returns:
            Relatório detalhado
        """
        with self._lock:
            try:
                if self.tracing:
                    with self.tracing.start_span("generate_cohort_report") as span:
                        span.set_attribute("cohort_id", cohort_id)
                
                # Analisar coorte
                analysis = self.analyze_cohort_retention(cohort_id)
                
                # Preparar dados para visualização
                retention_chart_data = []
                for retention in analysis.retention_data:
                    retention_chart_data.append({
                        "period": retention.period.value,
                        "retention_rate": retention.retention_rate,
                        "churn_rate": retention.churn_rate,
                        "engagement_score": retention.engagement_score,
                        "ltv_estimate": retention.ltv_estimate
                    })
                
                report = {
                    "cohort_id": cohort_id,
                    "cohort_type": analysis.cohort_type.value,
                    "cohort_date": analysis.cohort_date.isoformat(),
                    "total_users": analysis.total_users,
                    "retention_chart_data": retention_chart_data,
                    "churn_prediction": analysis.churn_prediction,
                    "ltv_prediction": analysis.ltv_prediction,
                    "engagement_trend": analysis.engagement_trend,
                    "risk_score": analysis.risk_score,
                    "recommendations": analysis.recommendations,
                    "summary": {
                        "avg_retention": statistics.mean([r.retention_rate for r in analysis.retention_data]),
                        "avg_churn": statistics.mean([r.churn_rate for r in analysis.retention_data]),
                        "avg_engagement": statistics.mean([r.engagement_score for r in analysis.retention_data]),
                        "total_ltv": sum([r.ltv_estimate for r in analysis.retention_data])
                    },
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                # Métricas
                if self.metrics:
                    self.metrics.increment_counter(
                        "cohort_reports_generated_total",
                        {"cohort_id": cohort_id}
                    )
                
                logger.info(f"Relatório de coorte {cohort_id} gerado")
                return report
                
            except Exception as e:
                logger.error(f"Erro ao gerar relatório de coorte {cohort_id}: {e}")
                if self.metrics:
                    self.metrics.increment_counter("cohort_report_errors_total")
                raise
    
    def export_cohort_data(self,
                          cohort_ids: List[str],
                          format: str = "json") -> str:
        """
        Exporta dados de coortes
        
        Args:
            cohort_ids: IDs das coortes
            format: Formato de exportação
            
        Returns:
            Caminho do arquivo exportado
        """
        import os
        
        # Criar diretório de exportação
        export_dir = "exports/cohorts"
        os.makedirs(export_dir, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{export_dir}/cohorts_{timestamp}.{format}"
        
        with self._lock:
            export_data = []
            
            for cohort_id in cohort_ids:
                try:
                    analysis = self.analyze_cohort_retention(cohort_id)
                    export_data.append({
                        "cohort_id": cohort_id,
                        "analysis": analysis.__dict__
                    })
                except Exception as e:
                    logger.warning(f"Erro ao exportar coorte {cohort_id}: {e}")
            
            if format == "json":
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            else:
                raise ValueError(f"Formato '{format}' não suportado")
        
        logger.info(f"Dados de coortes exportados: {filename}")
        return filename


# Instância global do analisador
cohort_analyzer = CohortAnalyzer() 
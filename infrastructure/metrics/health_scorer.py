"""
Integration Health Scorer - Sistema de Scoring de Saúde das Integrações
Tracing ID: METRICS-001
Data/Hora: 2024-12-20 02:00:00 UTC
Versão: 1.0
Status: IMPLEMENTAÇÃO INICIAL

Sistema enterprise para cálculo de score de saúde das integrações externas,
incluindo fatores de sucesso, latência, fallbacks e tendências históricas.
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import redis
import numpy as np
from collections import defaultdict, deque

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Status de saúde das integrações"""
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"           # 75-89
    WARNING = "warning"     # 60-74
    CRITICAL = "critical"   # 0-59

@dataclass
class HealthMetrics:
    """Métricas de saúde de uma integração"""
    integration_name: str
    success_rate: float
    avg_latency: float
    fallback_usage: float
    error_rate: float
    uptime_percentage: float
    last_check: datetime
    health_score: float
    status: HealthStatus
    trend: str  # "improving", "stable", "declining"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            **asdict(self),
            'last_check': self.last_check.isoformat(),
            'status': self.status.value
        }

@dataclass
class HealthThresholds:
    """Limites para cálculo de score de saúde"""
    success_rate_min: float = 0.95
    latency_max_ms: float = 1000.0
    fallback_max_percent: float = 0.05
    error_rate_max: float = 0.05
    uptime_min: float = 0.99

class IntegrationHealthScorer:
    """
    Sistema de scoring de saúde das integrações externas
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Inicializa o sistema de scoring de saúde
        
        Args:
            redis_client: Cliente Redis para cache (opcional)
        """
        self.redis_client = redis_client
        self.thresholds = HealthThresholds()
        self.history_window = 24  # horas
        self.metrics_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        
        logger.info("[HEALTH_SCORER] Sistema de scoring de saúde inicializado")
    
    def calculate_health_score(self, integration_name: str, 
                             success_rate: float, 
                             avg_latency: float,
                             fallback_usage: float,
                             error_rate: float,
                             uptime_percentage: float) -> Tuple[float, HealthStatus]:
        """
        Calcula o score de saúde de uma integração
        
        Args:
            integration_name: Nome da integração
            success_rate: Taxa de sucesso (0-1)
            avg_latency: Latência média em ms
            fallback_usage: Uso de fallback (0-1)
            error_rate: Taxa de erro (0-1)
            uptime_percentage: Percentual de uptime (0-1)
            
        Returns:
            Tuple com score (0-100) e status de saúde
        """
        try:
            # Pesos para cada métrica
            weights = {
                'success_rate': 0.35,
                'latency': 0.25,
                'fallback': 0.15,
                'error_rate': 0.15,
                'uptime': 0.10
            }
            
            # Normalização das métricas
            success_score = min(success_rate / self.thresholds.success_rate_min, 1.0) * 100
            latency_score = max(0, (self.thresholds.latency_max_ms - avg_latency) / self.thresholds.latency_max_ms) * 100
            fallback_score = max(0, (1.0 - fallback_usage / self.thresholds.fallback_max_percent)) * 100
            error_score = max(0, (1.0 - error_rate / self.thresholds.error_rate_max)) * 100
            uptime_score = min(uptime_percentage / self.thresholds.uptime_min, 1.0) * 100
            
            # Cálculo do score ponderado
            total_score = (
                success_score * weights['success_rate'] +
                latency_score * weights['latency'] +
                fallback_score * weights['fallback'] +
                error_score * weights['error_rate'] +
                uptime_score * weights['uptime']
            )
            
            # Determinação do status
            if total_score >= 90:
                status = HealthStatus.EXCELLENT
            elif total_score >= 75:
                status = HealthStatus.GOOD
            elif total_score >= 60:
                status = HealthStatus.WARNING
            else:
                status = HealthStatus.CRITICAL
            
            logger.info(f"[HEALTH_SCORER] Score calculado para {integration_name}: {total_score:.2f} ({status.value})")
            
            return total_score, status
            
        except Exception as e:
            logger.error(f"[HEALTH_SCORER] Erro ao calcular score para {integration_name}: {e}")
            return 0.0, HealthStatus.CRITICAL
    
    def update_integration_health(self, integration_name: str,
                                success_rate: float,
                                avg_latency: float,
                                fallback_usage: float,
                                error_rate: float,
                                uptime_percentage: float) -> HealthMetrics:
        """
        Atualiza métricas de saúde de uma integração
        
        Args:
            integration_name: Nome da integração
            success_rate: Taxa de sucesso
            avg_latency: Latência média
            fallback_usage: Uso de fallback
            error_rate: Taxa de erro
            uptime_percentage: Percentual de uptime
            
        Returns:
            Métricas de saúde atualizadas
        """
        try:
            # Calcula score e status
            health_score, status = self.calculate_health_score(
                integration_name, success_rate, avg_latency, 
                fallback_usage, error_rate, uptime_percentage
            )
            
            # Determina tendência
            trend = self._calculate_trend(integration_name, health_score)
            
            # Cria métricas
            metrics = HealthMetrics(
                integration_name=integration_name,
                success_rate=success_rate,
                avg_latency=avg_latency,
                fallback_usage=fallback_usage,
                error_rate=error_rate,
                uptime_percentage=uptime_percentage,
                last_check=datetime.utcnow(),
                health_score=health_score,
                status=status,
                trend=trend
            )
            
            # Armazena no histórico
            self.metrics_history[integration_name].append(metrics)
            
            # Cache no Redis se disponível
            if self.redis_client:
                cache_key = f"health_score:{integration_name}"
                self.redis_client.setex(
                    cache_key, 
                    300,  # 5 minutos
                    json.dumps(metrics.to_dict())
                )
            
            logger.info(f"[HEALTH_SCORER] Métricas atualizadas para {integration_name}")
            return metrics
            
        except Exception as e:
            logger.error(f"[HEALTH_SCORER] Erro ao atualizar métricas para {integration_name}: {e}")
            raise
    
    def _calculate_trend(self, integration_name: str, current_score: float) -> str:
        """
        Calcula tendência baseada no histórico
        
        Args:
            integration_name: Nome da integração
            current_score: Score atual
            
        Returns:
            Tendência: "improving", "stable", "declining"
        """
        try:
            history = self.metrics_history[integration_name]
            if len(history) < 3:
                return "stable"
            
            # Últimos 3 scores
            recent_scores = [m.health_score for m in list(history)[-3:]]
            
            # Calcula variação
            if len(recent_scores) >= 2:
                variation = recent_scores[-1] - recent_scores[0]
                
                if variation > 5:
                    return "improving"
                elif variation < -5:
                    return "declining"
                else:
                    return "stable"
            
            return "stable"
            
        except Exception as e:
            logger.error(f"[HEALTH_SCORER] Erro ao calcular tendência para {integration_name}: {e}")
            return "stable"
    
    def get_integration_health(self, integration_name: str) -> Optional[HealthMetrics]:
        """
        Obtém métricas de saúde de uma integração
        
        Args:
            integration_name: Nome da integração
            
        Returns:
            Métricas de saúde ou None se não encontrado
        """
        try:
            # Tenta cache primeiro
            if self.redis_client:
                cache_key = f"health_score:{integration_name}"
                cached = self.redis_client.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    return HealthMetrics(**data)
            
            # Busca no histórico
            history = self.metrics_history[integration_name]
            if history:
                return history[-1]
            
            return None
            
        except Exception as e:
            logger.error(f"[HEALTH_SCORER] Erro ao obter saúde para {integration_name}: {e}")
            return None
    
    def get_overall_health_dashboard(self) -> Dict[str, Any]:
        """
        Gera dashboard de saúde geral
        
        Returns:
            Dashboard com métricas consolidadas
        """
        try:
            dashboard = {
                'timestamp': datetime.utcnow().isoformat(),
                'total_integrations': len(self.metrics_history),
                'status_distribution': defaultdict(int),
                'average_score': 0.0,
                'critical_integrations': [],
                'trending_up': [],
                'trending_down': [],
                'integrations': []
            }
            
            total_score = 0.0
            integration_count = 0
            
            for integration_name, history in self.metrics_history.items():
                if not history:
                    continue
                
                latest = history[-1]
                dashboard['status_distribution'][latest.status.value] += 1
                total_score += latest.health_score
                integration_count += 1
                
                # Adiciona à lista de integrações
                dashboard['integrations'].append(latest.to_dict())
                
                # Categoriza por status crítico
                if latest.status == HealthStatus.CRITICAL:
                    dashboard['critical_integrations'].append(integration_name)
                
                # Categoriza por tendência
                if latest.trend == "improving":
                    dashboard['trending_up'].append(integration_name)
                elif latest.trend == "declining":
                    dashboard['trending_down'].append(integration_name)
            
            # Calcula score médio
            if integration_count > 0:
                dashboard['average_score'] = total_score / integration_count
            
            # Converte defaultdict para dict
            dashboard['status_distribution'] = dict(dashboard['status_distribution'])
            
            logger.info(f"[HEALTH_SCORER] Dashboard gerado com {integration_count} integrações")
            return dashboard
            
        except Exception as e:
            logger.error(f"[HEALTH_SCORER] Erro ao gerar dashboard: {e}")
            return {}
    
    def get_health_alerts(self, threshold_score: float = 70.0) -> List[Dict[str, Any]]:
        """
        Gera alertas baseados em score de saúde
        
        Args:
            threshold_score: Score mínimo para alerta
            
        Returns:
            Lista de alertas
        """
        try:
            alerts = []
            
            for integration_name, history in self.metrics_history.items():
                if not history:
                    continue
                
                latest = history[-1]
                
                if latest.health_score < threshold_score:
                    alert = {
                        'integration_name': integration_name,
                        'current_score': latest.health_score,
                        'threshold': threshold_score,
                        'status': latest.status.value,
                        'timestamp': latest.last_check.isoformat(),
                        'severity': 'high' if latest.health_score < 50 else 'medium',
                        'recommendations': self._generate_recommendations(latest)
                    }
                    alerts.append(alert)
            
            logger.info(f"[HEALTH_SCORER] {len(alerts)} alertas gerados")
            return alerts
            
        except Exception as e:
            logger.error(f"[HEALTH_SCORER] Erro ao gerar alertas: {e}")
            return []
    
    def _generate_recommendations(self, metrics: HealthMetrics) -> List[str]:
        """
        Gera recomendações baseadas nas métricas
        
        Args:
            metrics: Métricas de saúde
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        if metrics.success_rate < self.thresholds.success_rate_min:
            recommendations.append("Investigar causas de falhas e implementar retry logic")
        
        if metrics.avg_latency > self.thresholds.latency_max_ms:
            recommendations.append("Otimizar performance e considerar CDN")
        
        if metrics.fallback_usage > self.thresholds.fallback_max_percent:
            recommendations.append("Revisar configuração de fallbacks e health checks")
        
        if metrics.error_rate > self.thresholds.error_rate_max:
            recommendations.append("Implementar circuit breaker e melhorar tratamento de erros")
        
        if metrics.uptime_percentage < self.thresholds.uptime_min:
            recommendations.append("Melhorar monitoramento e alertas de disponibilidade")
        
        return recommendations
    
    def get_historical_trends(self, integration_name: str, 
                            hours: int = 24) -> Dict[str, Any]:
        """
        Obtém tendências históricas de uma integração
        
        Args:
            integration_name: Nome da integração
            hours: Período em horas
            
        Returns:
            Dados de tendência histórica
        """
        try:
            history = self.metrics_history[integration_name]
            if not history:
                return {}
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_metrics = [
                m for m in history 
                if m.last_check >= cutoff_time
            ]
            
            if not recent_metrics:
                return {}
            
            trends = {
                'integration_name': integration_name,
                'period_hours': hours,
                'data_points': len(recent_metrics),
                'scores': [m.health_score for m in recent_metrics],
                'timestamps': [m.last_check.isoformat() for m in recent_metrics],
                'average_score': np.mean([m.health_score for m in recent_metrics]),
                'score_variance': np.var([m.health_score for m in recent_metrics]),
                'min_score': min([m.health_score for m in recent_metrics]),
                'max_score': max([m.health_score for m in recent_metrics])
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"[HEALTH_SCORER] Erro ao obter tendências para {integration_name}: {e}")
            return {}
    
    def cleanup_old_metrics(self, days: int = 7):
        """
        Remove métricas antigas do histórico
        
        Args:
            days: Idade máxima em dias
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            cleaned_count = 0
            
            for integration_name, history in self.metrics_history.items():
                original_size = len(history)
                # Remove métricas antigas
                while history and history[0].last_check < cutoff_time:
                    history.popleft()
                cleaned_count += original_size - len(history)
            
            logger.info(f"[HEALTH_SCORER] Limpeza concluída: {cleaned_count} métricas removidas")
            
        except Exception as e:
            logger.error(f"[HEALTH_SCORER] Erro na limpeza: {e}")


# Instância global
health_scorer = IntegrationHealthScorer()

# Funções de conveniência
def update_integration_health(integration_name: str, **metrics) -> HealthMetrics:
    """Função de conveniência para atualizar saúde de integração"""
    return health_scorer.update_integration_health(integration_name, **metrics)

def get_integration_health(integration_name: str) -> Optional[HealthMetrics]:
    """Função de conveniência para obter saúde de integração"""
    return health_scorer.get_integration_health(integration_name)

def get_health_dashboard() -> Dict[str, Any]:
    """Função de conveniência para obter dashboard"""
    return health_scorer.get_overall_health_dashboard()

def get_health_alerts(threshold: float = 70.0) -> List[Dict[str, Any]]:
    """Função de conveniência para obter alertas"""
    return health_scorer.get_health_alerts(threshold) 
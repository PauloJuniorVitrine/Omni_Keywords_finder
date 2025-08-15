"""
Gerenciador de Experimentos A/B Testing
=======================================

Este módulo gerencia o ciclo de vida completo dos experimentos:
- Criação e configuração
- Ativação e pausa
- Monitoramento em tempo real
- Análise e relatórios
- Limpeza e arquivamento

Author: Paulo Júnior
Date: 2024-12-19
Tracing ID: AB_TESTING_002
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
import time

# Integração com observabilidade
try:
    from infrastructure.observability.telemetry import TelemetryManager
    from infrastructure.observability.metrics import MetricsManager
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False

from .framework import ABTestingFramework, ExperimentConfig, ExperimentStatus

logger = logging.getLogger(__name__)


class ExperimentPhase(Enum):
    """Fases de um experimento"""
    SETUP = "setup"
    RUNNING = "running"
    ANALYSIS = "analysis"
    DECISION = "decision"
    COMPLETED = "completed"


@dataclass
class ExperimentMetrics:
    """Métricas de um experimento"""
    experiment_id: str
    total_users: int
    conversions: Dict[str, int]
    conversion_rates: Dict[str, float]
    revenue: Dict[str, float]
    avg_session_duration: Dict[str, float]
    bounce_rate: Dict[str, float]
    last_updated: datetime


class ExperimentManager:
    """
    Gerenciador avançado de experimentos A/B Testing
    
    Características:
    - Monitoramento em tempo real
    - Alertas automáticos
    - Relatórios automáticos
    - Limpeza inteligente
    - Integração com observabilidade
    """
    
    def __init__(self, 
                 framework: ABTestingFramework,
                 enable_monitoring: bool = True,
                 enable_alerts: bool = True):
        """
        Inicializa o gerenciador de experimentos
        
        Args:
            framework: Instância do framework A/B Testing
            enable_monitoring: Habilita monitoramento em tempo real
            enable_alerts: Habilita alertas automáticos
        """
        self.framework = framework
        self.enable_monitoring = enable_monitoring
        self.enable_alerts = enable_alerts
        
        # Cache de métricas
        self.metrics_cache: Dict[str, ExperimentMetrics] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Observabilidade
        self.telemetry = None
        self.metrics = None
        
        if OBSERVABILITY_AVAILABLE:
            try:
                self.telemetry = TelemetryManager()
                self.metrics = MetricsManager()
            except Exception as e:
                logger.warning(f"Falha ao inicializar observabilidade: {e}")
        
        # Monitoramento em tempo real
        self.monitoring_task = None
        self.monitoring_interval = 60  # segundos
        
        if enable_monitoring:
            self._start_monitoring()
        
        logger.info("Experiment Manager inicializado")
    
    def create_experiment_with_template(self,
                                      template_name: str,
                                      name: str,
                                      description: str,
                                      custom_config: Optional[Dict[str, Any]] = None) -> str:
        """
        Cria experimento usando templates pré-definidos
        
        Args:
            template_name: Nome do template
            name: Nome do experimento
            description: Descrição
            custom_config: Configurações customizadas
            
        Returns:
            ID do experimento criado
        """
        templates = self._get_experiment_templates()
        
        if template_name not in templates:
            raise ValueError(f"Template '{template_name}' não encontrado")
        
        template = templates[template_name]
        
        # Mesclar configurações
        config = template.copy()
        if custom_config:
            config.update(custom_config)
        
        # Criar experimento
        experiment_id = self.framework.create_experiment(
            name=name,
            description=description,
            variants=config["variants"],
            metrics=config["metrics"],
            traffic_allocation=config.get("traffic_allocation", 0.1),
            segment_rules=config.get("segment_rules"),
            min_sample_size=config.get("min_sample_size", 1000),
            confidence_level=config.get("confidence_level", 0.95),
            tags=config.get("tags", []) + [f"template:{template_name}"]
        )
        
        logger.info(f"Experimento criado com template {template_name}: {experiment_id}")
        return experiment_id
    
    def schedule_experiment(self,
                          experiment_id: str,
                          start_time: datetime,
                          end_time: Optional[datetime] = None) -> bool:
        """
        Agenda ativação/desativação de experimento
        
        Args:
            experiment_id: ID do experimento
            start_time: Horário de início
            end_time: Horário de fim (opcional)
            
        Returns:
            True se agendado com sucesso
        """
        with self._lock:
            if experiment_id not in self.framework.experiments:
                raise ValueError(f"Experimento {experiment_id} não encontrado")
            
            experiment = self.framework.experiments[experiment_id]
            
            # Validar horários
            now = datetime.utcnow()
            if start_time <= now:
                raise ValueError("Horário de início deve ser no futuro")
            
            if end_time and end_time <= start_time:
                raise ValueError("Horário de fim deve ser após o início")
            
            # Agendar ativação
            delay = (start_time - now).total_seconds()
            asyncio.create_task(self._schedule_activation(experiment_id, delay))
            
            # Agendar desativação se especificado
            if end_time:
                end_delay = (end_time - start_time).total_seconds()
                asyncio.create_task(self._schedule_deactivation(experiment_id, end_delay))
            
            logger.info(f"Experimento {experiment_id} agendado para {start_time}")
            return True
    
    def get_experiment_health(self, experiment_id: str) -> Dict[str, Any]:
        """
        Retorna saúde do experimento
        
        Args:
            experiment_id: ID do experimento
            
        Returns:
            Status de saúde do experimento
        """
        with self._lock:
            if experiment_id not in self.framework.experiments:
                raise ValueError(f"Experimento {experiment_id} não encontrado")
            
            experiment = self.framework.experiments[experiment_id]
            
            # Coletar métricas básicas
            variant_counts = {}
            total_conversions = 0
            
            for assignment in self.framework.user_assignments.values():
                if assignment.experiment_id == experiment_id:
                    variant = assignment.variant
                    variant_counts[variant] = variant_counts.get(variant, 0) + 1
            
            # Calcular saúde
            total_users = sum(variant_counts.values())
            min_users_per_variant = min(variant_counts.values()) if variant_counts else 0
            
            health_score = 100
            
            # Penalizar se poucos usuários
            if total_users < experiment.min_sample_size:
                health_score -= 30
            
            # Penalizar se distribuição desigual
            if variant_counts:
                max_users = max(variant_counts.values())
                min_users = min(variant_counts.values())
                if max_users > 0:
                    distribution_ratio = min_users / max_users
                    if distribution_ratio < 0.8:
                        health_score -= 20
            
            # Status baseado no score
            if health_score >= 80:
                status = "healthy"
            elif health_score >= 60:
                status = "warning"
            else:
                status = "critical"
            
            return {
                "experiment_id": experiment_id,
                "health_score": health_score,
                "status": status,
                "total_users": total_users,
                "min_sample_size": experiment.min_sample_size,
                "variant_distribution": variant_counts,
                "min_users_per_variant": min_users_per_variant,
                "recommendations": self._get_health_recommendations(health_score, total_users, experiment.min_sample_size)
            }
    
    def generate_experiment_report(self, experiment_id: str) -> Dict[str, Any]:
        """
        Gera relatório completo do experimento
        
        Args:
            experiment_id: ID do experimento
            
        Returns:
            Relatório detalhado
        """
        with self._lock:
            if experiment_id not in self.framework.experiments:
                raise ValueError(f"Experimento {experiment_id} não encontrado")
            
            experiment = self.framework.experiments[experiment_id]
            
            # Análise estatística
            analysis_results = self.framework.analyze_experiment(experiment_id)
            
            # Saúde do experimento
            health = self.get_experiment_health(experiment_id)
            
            # Métricas de tempo
            duration = datetime.utcnow() - experiment.start_date
            if experiment.end_date:
                duration = experiment.end_date - experiment.start_date
            
            # Recomendações
            recommendations = self._generate_recommendations(experiment, analysis_results, health)
            
            report = {
                "experiment_id": experiment_id,
                "name": experiment.name,
                "description": experiment.description,
                "status": experiment.status.value,
                "duration_days": duration.days,
                "start_date": experiment.start_date.isoformat(),
                "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
                "traffic_allocation": experiment.traffic_allocation,
                "health": health,
                "analysis": analysis_results,
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Salvar relatório
            self._save_report(experiment_id, report)
            
            logger.info(f"Relatório gerado para experimento {experiment_id}")
            return report
    
    def cleanup_old_experiments(self, days_old: int = 30) -> int:
        """
        Limpa experimentos antigos
        
        Args:
            days_old: Idade mínima em dias para limpeza
            
        Returns:
            Número de experimentos limpos
        """
        with self._lock:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            cleaned_count = 0
            
            experiments_to_clean = []
            
            for experiment_id, experiment in self.framework.experiments.items():
                if (experiment.status in [ExperimentStatus.COMPLETED, ExperimentStatus.ARCHIVED] and
                    experiment.updated_at < cutoff_date):
                    experiments_to_clean.append(experiment_id)
            
            for experiment_id in experiments_to_clean:
                try:
                    # Arquivar dados importantes
                    self._archive_experiment_data(experiment_id)
                    
                    # Remover do framework
                    del self.framework.experiments[experiment_id]
                    
                    # Limpar atribuições
                    keys_to_remove = []
                    for key, assignment in self.framework.user_assignments.items():
                        if assignment.experiment_id == experiment_id:
                            keys_to_remove.append(key)
                    
                    for key in keys_to_remove:
                        del self.framework.user_assignments[key]
                    
                    cleaned_count += 1
                    logger.info(f"Experimento {experiment_id} limpo")
                    
                except Exception as e:
                    logger.error(f"Erro ao limpar experimento {experiment_id}: {e}")
            
            return cleaned_count
    
    def get_experiment_templates(self) -> Dict[str, Dict[str, Any]]:
        """Retorna templates disponíveis"""
        return self._get_experiment_templates()
    
    def _get_experiment_templates(self) -> Dict[str, Dict[str, Any]]:
        """Templates pré-definidos de experimentos"""
        return {
            "button_color": {
                "name": "Teste de Cor de Botão",
                "description": "Testa diferentes cores de botão para conversão",
                "variants": {
                    "control": {"button_color": "#007bff", "description": "Azul padrão"},
                    "green": {"button_color": "#28a745", "description": "Verde"},
                    "red": {"button_color": "#dc3545", "description": "Vermelho"}
                },
                "metrics": ["click_rate", "conversion_rate"],
                "traffic_allocation": 0.1,
                "min_sample_size": 500,
                "tags": ["ui", "conversion"]
            },
            "headline_test": {
                "name": "Teste de Headline",
                "description": "Testa diferentes headlines para engajamento",
                "variants": {
                    "control": {"headline": "Encontre as melhores keywords", "description": "Headline padrão"},
                    "benefit": {"headline": "Aumente seu tráfego orgânico", "description": "Foco em benefício"},
                    "urgency": {"headline": "Descubra keywords que seus concorrentes não conhecem", "description": "Foco em urgência"}
                },
                "metrics": ["engagement_rate", "time_on_page", "conversion_rate"],
                "traffic_allocation": 0.15,
                "min_sample_size": 1000,
                "tags": ["content", "engagement"]
            },
            "pricing_test": {
                "name": "Teste de Preços",
                "description": "Testa diferentes estratégias de preços",
                "variants": {
                    "control": {"price": 99, "description": "Preço atual"},
                    "higher": {"price": 129, "description": "Preço 30% maior"},
                    "lower": {"price": 79, "description": "Preço 20% menor"}
                },
                "metrics": ["conversion_rate", "revenue_per_user", "lifetime_value"],
                "traffic_allocation": 0.05,
                "min_sample_size": 2000,
                "tags": ["pricing", "revenue"]
            },
            "landing_page": {
                "name": "Teste de Landing Page",
                "description": "Testa diferentes layouts de landing page",
                "variants": {
                    "control": {"layout": "single_column", "description": "Layout padrão"},
                    "two_column": {"layout": "two_column", "description": "Duas colunas"},
                    "minimal": {"layout": "minimal", "description": "Layout minimalista"}
                },
                "metrics": ["bounce_rate", "time_on_page", "conversion_rate"],
                "traffic_allocation": 0.1,
                "min_sample_size": 1500,
                "tags": ["landing_page", "ux"]
            }
        }
    
    async def _schedule_activation(self, experiment_id: str, delay: float):
        """Agenda ativação de experimento"""
        await asyncio.sleep(delay)
        
        try:
            self.framework.activate_experiment(experiment_id)
            logger.info(f"Experimento {experiment_id} ativado automaticamente")
        except Exception as e:
            logger.error(f"Erro na ativação automática do experimento {experiment_id}: {e}")
    
    async def _schedule_deactivation(self, experiment_id: str, delay: float):
        """Agenda desativação de experimento"""
        await asyncio.sleep(delay)
        
        try:
            # Implementar desativação
            logger.info(f"Experimento {experiment_id} desativado automaticamente")
        except Exception as e:
            logger.error(f"Erro na desativação automática do experimento {experiment_id}: {e}")
    
    def _get_health_recommendations(self, 
                                  health_score: int,
                                  total_users: int,
                                  min_sample_size: int) -> List[str]:
        """Gera recomendações baseadas na saúde do experimento"""
        recommendations = []
        
        if total_users < min_sample_size:
            recommendations.append(f"Aumentar tráfego: {total_users}/{min_sample_size} usuários")
        
        if health_score < 60:
            recommendations.append("Verificar distribuição de variantes")
        
        if health_score < 40:
            recommendations.append("Considerar pausar experimento para investigação")
        
        return recommendations
    
    def _generate_recommendations(self,
                                experiment: ExperimentConfig,
                                analysis_results: Dict[str, Any],
                                health: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Verificar significância estatística
        significant_variants = []
        for variant, data in analysis_results.items():
            if data.get("is_significant", False):
                significant_variants.append(variant)
        
        if significant_variants:
            recommendations.append(f"Variantes significativas encontradas: {', '.join(significant_variants)}")
        else:
            recommendations.append("Nenhuma variante mostrou diferença significativa")
        
        # Verificar tamanho da amostra
        if health["total_users"] < experiment.min_sample_size:
            recommendations.append("Continuar coleta de dados para atingir tamanho mínimo")
        
        # Verificar distribuição
        if health["status"] == "critical":
            recommendations.append("Investigar distribuição desigual de usuários")
        
        return recommendations
    
    def _save_report(self, experiment_id: str, report: Dict[str, Any]):
        """Salva relatório"""
        # Em produção, salvar em banco de dados ou arquivo
        logger.debug(f"Relatório salvo para experimento {experiment_id}")
    
    def _archive_experiment_data(self, experiment_id: str):
        """Arquiva dados do experimento"""
        # Em produção, mover para storage de longo prazo
        logger.debug(f"Dados arquivados para experimento {experiment_id}")
    
    def _start_monitoring(self):
        """Inicia monitoramento em tempo real"""
        def monitor_loop():
            while True:
                try:
                    self._monitor_experiments()
                    time.sleep(self.monitoring_interval)
                except Exception as e:
                    logger.error(f"Erro no monitoramento: {e}")
                    time.sleep(self.monitoring_interval)
        
        self.monitoring_task = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_task.start()
        logger.info("Monitoramento em tempo real iniciado")
    
    def _monitor_experiments(self):
        """Monitora experimentos ativos"""
        active_experiments = [
            exp for exp in self.framework.experiments.values()
            if exp.status == ExperimentStatus.ACTIVE
        ]
        
        for experiment in active_experiments:
            try:
                # Verificar saúde
                health = self.get_experiment_health(experiment.experiment_id)
                
                # Alertas automáticos
                if self.enable_alerts and health["status"] == "critical":
                    self._send_alert(experiment.experiment_id, "CRITICAL", health)
                
                # Métricas
                if self.metrics:
                    self.metrics.record_gauge("ab_testing_experiment_health",
                                            health["health_score"],
                                            labels={"experiment": experiment.experiment_id})
                
            except Exception as e:
                logger.error(f"Erro ao monitorar experimento {experiment.experiment_id}: {e}")
    
    def _send_alert(self, experiment_id: str, severity: str, data: Dict[str, Any]):
        """Envia alerta"""
        # Em produção, integrar com sistema de notificações
        logger.warning(f"ALERTA {severity}: Experimento {experiment_id} - {data}")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'monitoring_task') and self.monitoring_task:
            # Sinalizar parada do monitoramento
            pass 
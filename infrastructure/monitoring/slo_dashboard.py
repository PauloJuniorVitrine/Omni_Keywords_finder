#!/usr/bin/env python3
"""
📊 SLO Dashboard Manager - OMNİ KEYWORDS FINDER

Tracing ID: IMP005_SLO_DASHBOARD_2025_001
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Script para gerenciar dashboards de SLOs (Service Level Objectives)
Baseado no checklist de revisão definitiva - IMP005

Funcionalidades:
- Criação automática de dashboards SLO
- Atualização de métricas em tempo real
- Geração de relatórios de SLOs
- Alertas baseados em SLOs
- Error budget tracking
"""

import os
import sys
import json
import logging
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import yaml
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(name)string_data - %(levelname)string_data - %(message)string_data',
    handlers=[
        logging.FileHandler('logs/slo_dashboard.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SLOSeverity(Enum):
    """Severidade dos SLOs"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class SLOMetricType(Enum):
    """Tipos de métricas SLO"""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    RESILIENCE = "resilience"

@dataclass
class SLOMetric:
    """Definição de uma métrica SLO"""
    name: str
    service: str
    metric_type: SLOMetricType
    target: float
    current_value: float
    error_budget: float
    severity: SLOSeverity
    description: str
    timestamp: datetime

@dataclass
class SLOViolation:
    """Violação de SLO detectada"""
    metric_name: str
    service: str
    expected_value: float
    actual_value: float
    violation_percentage: float
    severity: SLOSeverity
    timestamp: datetime
    duration_minutes: int

class SLODashboardManager:
    """
    Gerenciador de dashboards de SLOs
    """
    
    def __init__(self, config_path: str = "monitoring/slos.yaml"):
        """
        Inicializa o gerenciador de SLOs
        
        Args:
            config_path: Caminho para o arquivo de configuração SLO
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
        self.grafana_url = os.getenv("GRAFANA_URL", "http://localhost:3000")
        self.grafana_token = os.getenv("GRAFANA_TOKEN")
        self.db_path = "data/slo_metrics.db"
        
        # Inicializar banco de dados
        self._init_database()
        
        # Definir SLOs padrão
        self.default_slos = {
            "api_availability": {
                "target": 0.999,  # 99.9%
                "window": "5m",
                "severity": SLOSeverity.CRITICAL
            },
            "api_latency_p95": {
                "target": 0.2,  # 200ms
                "window": "5m",
                "severity": SLOSeverity.CRITICAL
            },
            "api_error_rate": {
                "target": 0.001,  # 0.1%
                "window": "5m",
                "severity": SLOSeverity.CRITICAL
            },
            "database_availability": {
                "target": 0.999,  # 99.9%
                "window": "5m",
                "severity": SLOSeverity.CRITICAL
            },
            "cache_hit_ratio": {
                "target": 0.9,  # 90%
                "window": "10m",
                "severity": SLOSeverity.WARNING
            }
        }
        
        logger.info("SLO Dashboard Manager inicializado com sucesso")
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo YAML"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"Configuração SLO carregada de {self.config_path}")
                return config
        except FileNotFoundError:
            logger.warning(f"Arquivo de configuração {self.config_path} não encontrado. Usando configuração padrão.")
            return {}
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return {}
    
    def _init_database(self):
        """Inicializa banco de dados para métricas SLO"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de métricas SLO
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS slo_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        service TEXT NOT NULL,
                        metric_type TEXT NOT NULL,
                        target_value REAL NOT NULL,
                        current_value REAL NOT NULL,
                        error_budget REAL NOT NULL,
                        severity TEXT NOT NULL,
                        description TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de violações SLO
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS slo_violations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        service TEXT NOT NULL,
                        expected_value REAL NOT NULL,
                        actual_value REAL NOT NULL,
                        violation_percentage REAL NOT NULL,
                        severity TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        duration_minutes INTEGER DEFAULT 0
                    )
                """)
                
                # Tabela de error budgets
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS error_budgets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        service TEXT NOT NULL,
                        metric_type TEXT NOT NULL,
                        error_budget_remaining REAL NOT NULL,
                        error_budget_consumed REAL NOT NULL,
                        window_start DATETIME NOT NULL,
                        window_end DATETIME NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Banco de dados SLO inicializado com sucesso")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
    
    def get_prometheus_metric(self, query: str) -> Optional[float]:
        """
        Busca métrica do Prometheus
        
        Args:
            query: Query PromQL
            
        Returns:
            Valor da métrica ou None se erro
        """
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": query},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            if data["status"] == "success" and data["data"]["result"]:
                return float(data["data"]["result"][0]["value"][1])
            else:
                logger.warning(f"Query não retornou dados: {query}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar métrica do Prometheus: {e}")
            return None
    
    def calculate_slo_metrics(self) -> List[SLOMetric]:
        """
        Calcula métricas SLO atuais
        
        Returns:
            Lista de métricas SLO
        """
        metrics = []
        timestamp = datetime.utcnow()
        
        # API Availability SLO
        api_availability = self.get_prometheus_metric(
            'slo:api:availability:ratio'
        )
        if api_availability is not None:
            target = 0.999
            error_budget = 1 - api_availability
            metrics.append(SLOMetric(
                name="api_availability",
                service="api",
                metric_type=SLOMetricType.AVAILABILITY,
                target=target,
                current_value=api_availability,
                error_budget=error_budget,
                severity=SLOSeverity.CRITICAL,
                description="API availability ratio",
                timestamp=timestamp
            ))
        
        # API Latency SLO (P95)
        api_latency = self.get_prometheus_metric(
            'slo:api:latency:p95'
        )
        if api_latency is not None:
            target = 0.2  # 200ms
            error_budget = 1 - (target / api_latency if api_latency > 0 else 1)
            metrics.append(SLOMetric(
                name="api_latency_p95",
                service="api",
                metric_type=SLOMetricType.LATENCY,
                target=target,
                current_value=api_latency,
                error_budget=error_budget,
                severity=SLOSeverity.CRITICAL,
                description="API latency P95",
                timestamp=timestamp
            ))
        
        # API Error Rate SLO
        api_error_rate = self.get_prometheus_metric(
            'slo:api:error_rate:ratio'
        )
        if api_error_rate is not None:
            target = 0.001  # 0.1%
            error_budget = target - api_error_rate
            metrics.append(SLOMetric(
                name="api_error_rate",
                service="api",
                metric_type=SLOMetricType.ERROR_RATE,
                target=target,
                current_value=api_error_rate,
                error_budget=error_budget,
                severity=SLOSeverity.CRITICAL,
                description="API error rate",
                timestamp=timestamp
            ))
        
        # Database Availability SLO
        db_availability = self.get_prometheus_metric(
            'slo:database:availability:ratio'
        )
        if db_availability is not None:
            target = 0.999
            error_budget = 1 - db_availability
            metrics.append(SLOMetric(
                name="database_availability",
                service="database",
                metric_type=SLOMetricType.AVAILABILITY,
                target=target,
                current_value=db_availability,
                error_budget=error_budget,
                severity=SLOSeverity.CRITICAL,
                description="Database availability ratio",
                timestamp=timestamp
            ))
        
        # Cache Hit Ratio SLO
        cache_hit_ratio = self.get_prometheus_metric(
            'slo:cache:hit_ratio:ratio'
        )
        if cache_hit_ratio is not None:
            target = 0.9  # 90%
            error_budget = 1 - cache_hit_ratio
            metrics.append(SLOMetric(
                name="cache_hit_ratio",
                service="cache",
                metric_type=SLOMetricType.RESILIENCE,
                target=target,
                current_value=cache_hit_ratio,
                error_budget=error_budget,
                severity=SLOSeverity.WARNING,
                description="Cache hit ratio",
                timestamp=timestamp
            ))
        
        # Salvar métricas no banco
        self._save_metrics(metrics)
        
        return metrics
    
    def _save_metrics(self, metrics: List[SLOMetric]):
        """Salva métricas no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for metric in metrics:
                    cursor.execute("""
                        INSERT INTO slo_metrics 
                        (name, service, metric_type, target_value, current_value, 
                         error_budget, severity, description, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        metric.name,
                        metric.service,
                        metric.metric_type.value,
                        metric.target,
                        metric.current_value,
                        metric.error_budget,
                        metric.severity.value,
                        metric.description,
                        metric.timestamp.isoformat()
                    ))
                
                conn.commit()
                logger.info(f"Salvas {len(metrics)} métricas SLO no banco")
                
        except Exception as e:
            logger.error(f"Erro ao salvar métricas: {e}")
    
    def detect_violations(self, metrics: List[SLOMetric]) -> List[SLOViolation]:
        """
        Detecta violações de SLO
        
        Args:
            metrics: Lista de métricas SLO
            
        Returns:
            Lista de violações detectadas
        """
        violations = []
        timestamp = datetime.utcnow()
        
        for metric in metrics:
            is_violation = False
            
            if metric.metric_type == SLOMetricType.AVAILABILITY:
                is_violation = metric.current_value < metric.target
            elif metric.metric_type == SLOMetricType.LATENCY:
                is_violation = metric.current_value > metric.target
            elif metric.metric_type == SLOMetricType.ERROR_RATE:
                is_violation = metric.current_value > metric.target
            elif metric.metric_type == SLOMetricType.RESILIENCE:
                is_violation = metric.current_value < metric.target
            
            if is_violation:
                violation_percentage = abs(
                    (metric.current_value - metric.target) / metric.target * 100
                )
                
                violation = SLOViolation(
                    metric_name=metric.name,
                    service=metric.service,
                    expected_value=metric.target,
                    actual_value=metric.current_value,
                    violation_percentage=violation_percentage,
                    severity=metric.severity,
                    timestamp=timestamp,
                    duration_minutes=0  # Será calculado posteriormente
                )
                
                violations.append(violation)
                self._save_violation(violation)
        
        return violations
    
    def _save_violation(self, violation: SLOViolation):
        """Salva violação no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO slo_violations 
                    (metric_name, service, expected_value, actual_value, 
                     violation_percentage, severity, timestamp, duration_minutes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    violation.metric_name,
                    violation.service,
                    violation.expected_value,
                    violation.actual_value,
                    violation.violation_percentage,
                    violation.severity.value,
                    violation.timestamp.isoformat(),
                    violation.duration_minutes
                ))
                
                conn.commit()
                logger.warning(f"Violation SLO detectada: {violation.metric_name}")
                
        except Exception as e:
            logger.error(f"Erro ao salvar violação: {e}")
    
    def generate_slo_report(self, period_hours: int = 24) -> Dict[str, Any]:
        """
        Gera relatório de SLOs
        
        Args:
            period_hours: Período em horas para o relatório
            
        Returns:
            Dicionário com dados do relatório
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=period_hours)
            
            with sqlite3.connect(self.db_path) as conn:
                # Buscar métricas do período
                df_metrics = pd.read_sql_query("""
                    SELECT * FROM slo_metrics 
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp DESC
                """, conn, params=(start_time.isoformat(), end_time.isoformat()))
                
                # Buscar violações do período
                df_violations = pd.read_sql_query("""
                    SELECT * FROM slo_violations 
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp DESC
                """, conn, params=(start_time.isoformat(), end_time.isoformat()))
                
                # Calcular estatísticas
                report = {
                    "period": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat(),
                        "hours": period_hours
                    },
                    "summary": {
                        "total_metrics": len(df_metrics),
                        "total_violations": len(df_violations),
                        "violation_rate": len(df_violations) / max(len(df_metrics), 1) * 100
                    },
                    "metrics_by_service": {},
                    "violations_by_severity": {},
                    "error_budgets": {}
                }
                
                # Métricas por serviço
                for service in df_metrics['service'].unique():
                    service_metrics = df_metrics[df_metrics['service'] == service]
                    report["metrics_by_service"][service] = {
                        "count": len(service_metrics),
                        "avg_error_budget": service_metrics['error_budget'].mean(),
                        "min_error_budget": service_metrics['error_budget'].min(),
                        "max_error_budget": service_metrics['error_budget'].max()
                    }
                
                # Violações por severidade
                for severity in df_violations['severity'].unique():
                    severity_violations = df_violations[df_violations['severity'] == severity]
                    report["violations_by_severity"][severity] = {
                        "count": len(severity_violations),
                        "avg_violation_percentage": severity_violations['violation_percentage'].mean()
                    }
                
                # Error budgets
                for metric_name in df_metrics['name'].unique():
                    metric_data = df_metrics[df_metrics['name'] == metric_name]
                    report["error_budgets"][metric_name] = {
                        "avg_error_budget": metric_data['error_budget'].mean(),
                        "error_budget_trend": metric_data['error_budget'].tolist()
                    }
                
                logger.info(f"Relatório SLO gerado para período de {period_hours}h")
                return report
                
        except Exception as e:
            logger.error(f"Erro ao gerar relatório SLO: {e}")
            return {}
    
    def create_grafana_dashboard(self) -> bool:
        """
        Cria dashboard SLO no Grafana
        
        Returns:
            True se criado com sucesso
        """
        if not self.grafana_token:
            logger.error("Token do Grafana não configurado")
            return False
        
        try:
            dashboard_config = {
                "dashboard": {
                    "id": None,
                    "title": "Omni Keywords Finder - SLOs Dashboard",
                    "tags": ["slo", "omni-keywords", "production"],
                    "timezone": "browser",
                    "panels": [
                        {
                            "id": 1,
                            "title": "API Availability SLO",
                            "type": "stat",
                            "targets": [
                                {
                                    "expr": "slo:api:availability:ratio * 100",
                                    "legendFormat": "Availability %"
                                }
                            ],
                            "fieldConfig": {
                                "defaults": {
                                    "unit": "percent",
                                    "thresholds": {
                                        "steps": [
                                            {"color": "red", "value": null},
                                            {"color": "yellow", "value": 99.5},
                                            {"color": "green", "value": 99.9}
                                        ]
                                    }
                                }
                            }
                        },
                        {
                            "id": 2,
                            "title": "API Latency SLO (P95)",
                            "type": "stat",
                            "targets": [
                                {
                                    "expr": "slo:api:latency:p95 * 1000",
                                    "legendFormat": "Latency (ms)"
                                }
                            ],
                            "fieldConfig": {
                                "defaults": {
                                    "unit": "ms",
                                    "thresholds": {
                                        "steps": [
                                            {"color": "green", "value": null},
                                            {"color": "yellow", "value": 150},
                                            {"color": "red", "value": 200}
                                        ]
                                    }
                                }
                            }
                        },
                        {
                            "id": 3,
                            "title": "Error Budget Remaining",
                            "type": "timeseries",
                            "targets": [
                                {
                                    "expr": "slo:api:availability:error_budget_remaining",
                                    "legendFormat": "API Availability"
                                },
                                {
                                    "expr": "slo:api:latency:error_budget",
                                    "legendFormat": "API Latency"
                                },
                                {
                                    "expr": "slo:api:error_rate:error_budget",
                                    "legendFormat": "API Error Rate"
                                }
                            ]
                        }
                    ]
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.grafana_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.grafana_url}/api/dashboards/db",
                json=dashboard_config,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info("Dashboard SLO criado no Grafana com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar dashboard no Grafana: {e}")
            return False
    
    def generate_visualization(self, report: Dict[str, Any]) -> str:
        """
        Gera visualização do relatório SLO
        
        Args:
            report: Dados do relatório
            
        Returns:
            Caminho para o arquivo HTML gerado
        """
        try:
            # Criar subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    "Error Budget por Serviço",
                    "Violações por Severidade",
                    "Trend de Error Budget",
                    "Resumo de Métricas"
                ),
                specs=[
                    [{"type": "bar"}, {"type": "pie"}],
                    [{"type": "scatter"}, {"type": "table"}]
                ]
            )
            
            # Gráfico 1: Error Budget por Serviço
            services = list(report["metrics_by_service"].keys())
            error_budgets = [report["metrics_by_service"][string_data]["avg_error_budget"] for string_data in services]
            
            fig.add_trace(
                go.Bar(value=services, result=error_budgets, name="Error Budget"),
                row=1, col=1
            )
            
            # Gráfico 2: Violações por Severidade
            severities = list(report["violations_by_severity"].keys())
            violation_counts = [report["violations_by_severity"][string_data]["count"] for string_data in severities]
            
            fig.add_trace(
                go.Pie(labels=severities, values=violation_counts, name="Violações"),
                row=1, col=2
            )
            
            # Gráfico 3: Trend de Error Budget
            for metric_name, data in report["error_budgets"].items():
                fig.add_trace(
                    go.Scatter(
                        result=data["error_budget_trend"],
                        name=metric_name,
                        mode="lines+markers"
                    ),
                    row=2, col=1
                )
            
            # Tabela 4: Resumo
            summary_data = [
                ["Total Métricas", report["summary"]["total_metrics"]],
                ["Total Violações", report["summary"]["total_violations"]],
                ["Taxa de Violação", f"{report['summary']['violation_rate']:.2f}%"],
                ["Período", f"{report['period']['hours']}h"]
            ]
            
            fig.add_trace(
                go.Table(
                    header=dict(values=["Métrica", "Valor"]),
                    cells=dict(values=[[row[0] for row in summary_data], [row[1] for row in summary_data]])
                ),
                row=2, col=2
            )
            
            # Atualizar layout
            fig.update_layout(
                title="Relatório SLO - Omni Keywords Finder",
                height=800,
                showlegend=True
            )
            
            # Salvar arquivo
            output_path = f"reports/slo_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            fig.write_html(output_path)
            
            logger.info(f"Visualização SLO salva em: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar visualização: {e}")
            return ""
    
    def run_monitoring_cycle(self):
        """Executa ciclo completo de monitoramento SLO"""
        try:
            logger.info("Iniciando ciclo de monitoramento SLO")
            
            # 1. Calcular métricas SLO
            metrics = self.calculate_slo_metrics()
            logger.info(f"Calculadas {len(metrics)} métricas SLO")
            
            # 2. Detectar violações
            violations = self.detect_violations(metrics)
            if violations:
                logger.warning(f"Detectadas {len(violations)} violações SLO")
            else:
                logger.info("Nenhuma violação SLO detectada")
            
            # 3. Gerar relatório
            report = self.generate_slo_report()
            
            # 4. Criar visualização
            if report:
                viz_path = self.generate_visualization(report)
                if viz_path:
                    logger.info(f"Visualização gerada: {viz_path}")
            
            logger.info("Ciclo de monitoramento SLO concluído")
            
        except Exception as e:
            logger.error(f"Erro no ciclo de monitoramento SLO: {e}")

def main():
    """Função principal"""
    try:
        # Inicializar gerenciador
        slo_manager = SLODashboardManager()
        
        # Executar ciclo de monitoramento
        slo_manager.run_monitoring_cycle()
        
        # Criar dashboard no Grafana (opcional)
        if os.getenv("CREATE_GRAFANA_DASHBOARD", "false").lower() == "true":
            slo_manager.create_grafana_dashboard()
        
        logger.info("Execução do SLO Dashboard Manager concluída com sucesso")
        
    except Exception as e:
        logger.error(f"Erro na execução principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
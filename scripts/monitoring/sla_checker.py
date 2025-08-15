#!/usr/bin/env python3
"""
Sistema de SLA Compliance Checker - Omni Keywords Finder
Tracing ID: OBS_003_20241219_001
Data: 2024-12-19
Versão: 1.0

Implementa monitoramento de SLAs com:
- Monitoramento de SLAs por integração
- Alertas automáticos
- Relatórios de compliance
- Integração com Grafana
- Métricas de uptime e performance
- Análise de tendências
- Dashboard de compliance
"""

import logging
import json
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from pathlib import Path

class SLAStatus(Enum):
    """Status do SLA"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATED = "violated"
    UNKNOWN = "unknown"

class SLAViolationType(Enum):
    """Tipos de violação de SLA"""
    RESPONSE_TIME = "response_time"
    AVAILABILITY = "availability"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    LATENCY = "latency"

@dataclass
class SLAMetric:
    """Métrica de SLA"""
    integration_name: str
    metric_type: str
    current_value: float
    threshold: float
    unit: str
    timestamp: datetime
    status: SLAStatus
    violation_type: Optional[SLAViolationType] = None

@dataclass
class SLAViolation:
    """Violação de SLA"""
    integration_name: str
    violation_type: SLAViolationType
    current_value: float
    threshold: float
    timestamp: datetime
    duration_minutes: int
    severity: str
    description: str

@dataclass
class SLAReport:
    """Relatório de SLA"""
    integration_name: str
    period_start: datetime
    period_end: datetime
    uptime_percentage: float
    avg_response_time: float
    error_rate: float
    sla_compliance_rate: float
    violations_count: int
    status: SLAStatus
    recommendations: List[str]

class SLAChecker:
    """
    Sistema de monitoramento de SLAs com alertas automáticos
    e relatórios de compliance.
    """
    
    def __init__(self, db_path: str = "sla_metrics.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Configurações de SLA por integração
        self.sla_configs = {
            "google_trends": {
                "response_time_threshold": 2.0,  # segundos
                "availability_threshold": 99.5,  # porcentagem
                "error_rate_threshold": 1.0,     # porcentagem
                "throughput_threshold": 100,     # requests/min
                "latency_threshold": 500         # milissegundos
            },
            "amazon_api": {
                "response_time_threshold": 3.0,
                "availability_threshold": 99.0,
                "error_rate_threshold": 2.0,
                "throughput_threshold": 50,
                "latency_threshold": 1000
            },
            "webhook_system": {
                "response_time_threshold": 1.0,
                "availability_threshold": 99.9,
                "error_rate_threshold": 0.5,
                "throughput_threshold": 200,
                "latency_threshold": 200
            },
            "database_operations": {
                "response_time_threshold": 0.5,
                "availability_threshold": 99.9,
                "error_rate_threshold": 0.1,
                "throughput_threshold": 1000,
                "latency_threshold": 100
            }
        }
        
        # Configurações de alertas
        self.alert_config = {
            "warning_threshold": 0.8,  # 80% do limite
            "critical_threshold": 0.95, # 95% do limite
            "alert_cooldown_minutes": 15,
            "max_alerts_per_hour": 10
        }
        
        # Inicializar banco de dados
        self._init_database()
    
    def _init_database(self) -> None:
        """Inicializa banco de dados para métricas de SLA."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de métricas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sla_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        integration_name TEXT NOT NULL,
                        metric_type TEXT NOT NULL,
                        current_value REAL NOT NULL,
                        threshold REAL NOT NULL,
                        unit TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        status TEXT NOT NULL,
                        violation_type TEXT
                    )
                """)
                
                # Tabela de violações
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sla_violations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        integration_name TEXT NOT NULL,
                        violation_type TEXT NOT NULL,
                        current_value REAL NOT NULL,
                        threshold REAL NOT NULL,
                        timestamp DATETIME NOT NULL,
                        duration_minutes INTEGER NOT NULL,
                        severity TEXT NOT NULL,
                        description TEXT NOT NULL,
                        resolved BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Tabela de alertas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sla_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        integration_name TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        message TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        acknowledged BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Índices para performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_metrics_integration_time 
                    ON sla_metrics(integration_name, timestamp)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_violations_integration_time 
                    ON sla_violations(integration_name, timestamp)
                """)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco de dados SLA: {e}")
            raise
    
    def record_metric(self, integration_name: str, metric_type: str, 
                     current_value: float, unit: str) -> None:
        """
        Registra uma métrica de SLA.
        
        Args:
            integration_name: Nome da integração
            metric_type: Tipo da métrica
            current_value: Valor atual
            unit: Unidade da métrica
        """
        try:
            if integration_name not in self.sla_configs:
                self.logger.warning(f"Configuração SLA não encontrada para {integration_name}")
                return
            
            config = self.sla_configs[integration_name]
            threshold_key = f"{metric_type}_threshold"
            
            if threshold_key not in config:
                self.logger.warning(f"Threshold não configurado para {metric_type} em {integration_name}")
                return
            
            threshold = config[threshold_key]
            timestamp = datetime.utcnow()
            
            # Determinar status baseado no valor atual vs threshold
            if metric_type in ["availability", "uptime"]:
                # Para disponibilidade, valor maior é melhor
                if current_value >= threshold:
                    status = SLAStatus.COMPLIANT
                elif current_value >= threshold * self.alert_config["warning_threshold"]:
                    status = SLAStatus.WARNING
                else:
                    status = SLAStatus.VIOLATED
            else:
                # Para outros métricas, valor menor é melhor
                if current_value <= threshold:
                    status = SLAStatus.COMPLIANT
                elif current_value <= threshold * (1 + (1 - self.alert_config["warning_threshold"])):
                    status = SLAStatus.WARNING
                else:
                    status = SLAStatus.VIOLATED
            
            # Determinar tipo de violação se aplicável
            violation_type = None
            if status == SLAStatus.VIOLATED:
                violation_type = SLAViolationType(metric_type)
            
            # Salvar métrica no banco
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sla_metrics 
                    (integration_name, metric_type, current_value, threshold, unit, timestamp, status, violation_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (integration_name, metric_type, current_value, threshold, unit, 
                     timestamp.isoformat(), status.value, violation_type.value if violation_type else None))
                conn.commit()
            
            # Verificar se precisa gerar alerta
            if status in [SLAStatus.WARNING, SLAStatus.VIOLATED]:
                self._check_and_generate_alert(integration_name, metric_type, current_value, threshold, status)
            
            # Registrar violação se aplicável
            if status == SLAStatus.VIOLATED:
                self._record_violation(integration_name, violation_type, current_value, threshold, timestamp)
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar métrica SLA: {e}")
    
    def _check_and_generate_alert(self, integration_name: str, metric_type: str,
                                 current_value: float, threshold: float, status: SLAStatus) -> None:
        """Verifica e gera alertas baseados no status da métrica."""
        try:
            # Verificar cooldown de alertas
            if not self._can_generate_alert(integration_name, metric_type):
                return
            
            # Determinar severidade
            if status == SLAStatus.VIOLATED:
                severity = "CRITICAL"
            else:
                severity = "WARNING"
            
            # Criar mensagem de alerta
            message = f"SLA {severity}: {integration_name} - {metric_type} = {current_value} (threshold: {threshold})"
            
            # Salvar alerta
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sla_alerts 
                    (integration_name, alert_type, message, severity, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (integration_name, metric_type, message, severity, datetime.utcnow().isoformat()))
                conn.commit()
            
            # Log do alerta
            self.logger.warning(f"Alerta SLA gerado: {message}")
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar alerta SLA: {e}")
    
    def _can_generate_alert(self, integration_name: str, metric_type: str) -> bool:
        """Verifica se pode gerar alerta baseado no cooldown."""
        try:
            cooldown_time = datetime.utcnow() - timedelta(minutes=self.alert_config["alert_cooldown_minutes"])
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM sla_alerts 
                    WHERE integration_name = ? AND alert_type = ? AND timestamp > ?
                """, (integration_name, metric_type, cooldown_time.isoformat()))
                
                recent_alerts = cursor.fetchone()[0]
                
                return recent_alerts == 0
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar cooldown de alerta: {e}")
            return True
    
    def _record_violation(self, integration_name: str, violation_type: SLAViolationType,
                         current_value: float, threshold: float, timestamp: datetime) -> None:
        """Registra violação de SLA."""
        try:
            # Calcular duração da violação
            duration_minutes = 1  # Por padrão, 1 minuto
            
            # Determinar severidade
            if current_value > threshold * 2:
                severity = "CRITICAL"
            elif current_value > threshold * 1.5:
                severity = "HIGH"
            else:
                severity = "MEDIUM"
            
            description = f"{violation_type.value} violation: {current_value} > {threshold}"
            
            # Salvar violação
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sla_violations 
                    (integration_name, violation_type, current_value, threshold, timestamp, duration_minutes, severity, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (integration_name, violation_type.value, current_value, threshold, 
                     timestamp.isoformat(), duration_minutes, severity, description))
                conn.commit()
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar violação SLA: {e}")
    
    def get_sla_report(self, integration_name: str, 
                      period_hours: int = 24) -> Optional[SLAReport]:
        """
        Gera relatório de SLA para uma integração.
        
        Args:
            integration_name: Nome da integração
            period_hours: Período em horas para análise
            
        Returns:
            Relatório de SLA ou None se não houver dados
        """
        try:
            period_end = datetime.utcnow()
            period_start = period_end - timedelta(hours=period_hours)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Buscar métricas do período
                cursor.execute("""
                    SELECT metric_type, current_value, status, timestamp
                    FROM sla_metrics 
                    WHERE integration_name = ? AND timestamp BETWEEN ? AND ?
                    ORDER BY timestamp
                """, (integration_name, period_start.isoformat(), period_end.isoformat()))
                
                metrics = cursor.fetchall()
                
                if not metrics:
                    return None
                
                # Calcular estatísticas
                response_times = [m[1] for m in metrics if m[0] == "response_time"]
                availabilities = [m[1] for m in metrics if m[0] == "availability"]
                error_rates = [m[1] for m in metrics if m[0] == "error_rate"]
                
                # Contar violações
                violations = [m for m in metrics if m[2] == SLAStatus.VIOLATED.value]
                
                # Calcular compliance rate
                total_metrics = len(metrics)
                compliant_metrics = len([m for m in metrics if m[2] == SLAStatus.COMPLIANT.value])
                compliance_rate = (compliant_metrics / total_metrics) * 100 if total_metrics > 0 else 0
                
                # Determinar status geral
                if compliance_rate >= 99:
                    overall_status = SLAStatus.COMPLIANT
                elif compliance_rate >= 95:
                    overall_status = SLAStatus.WARNING
                else:
                    overall_status = SLAStatus.VIOLATED
                
                # Gerar recomendações
                recommendations = self._generate_recommendations(integration_name, metrics, compliance_rate)
                
                return SLAReport(
                    integration_name=integration_name,
                    period_start=period_start,
                    period_end=period_end,
                    uptime_percentage=statistics.mean(availabilities) if availabilities else 0,
                    avg_response_time=statistics.mean(response_times) if response_times else 0,
                    error_rate=statistics.mean(error_rates) if error_rates else 0,
                    sla_compliance_rate=compliance_rate,
                    violations_count=len(violations),
                    status=overall_status,
                    recommendations=recommendations
                )
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório SLA: {e}")
            return None
    
    def _generate_recommendations(self, integration_name: str, 
                                 metrics: List[tuple], compliance_rate: float) -> List[str]:
        """Gera recomendações baseadas nas métricas."""
        recommendations = []
        
        if compliance_rate < 95:
            recommendations.append("Investigar causas das violações de SLA")
        
        # Analisar tipos de violações
        violation_types = [m[0] for m in metrics if m[2] == SLAStatus.VIOLATED.value]
        
        if "response_time" in violation_types:
            recommendations.append("Otimizar performance da integração")
        
        if "availability" in violation_types:
            recommendations.append("Implementar circuit breaker e fallbacks")
        
        if "error_rate" in violation_types:
            recommendations.append("Revisar tratamento de erros e retry logic")
        
        if "throughput" in violation_types:
            recommendations.append("Considerar scaling horizontal")
        
        return recommendations
    
    def get_active_violations(self, integration_name: Optional[str] = None) -> List[SLAViolation]:
        """
        Busca violações ativas de SLA.
        
        Args:
            integration_name: Nome da integração (opcional)
            
        Returns:
            Lista de violações ativas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if integration_name:
                    cursor.execute("""
                        SELECT integration_name, violation_type, current_value, threshold, 
                               timestamp, duration_minutes, severity, description
                        FROM sla_violations 
                        WHERE integration_name = ? AND resolved = FALSE
                        ORDER BY timestamp DESC
                    """, (integration_name,))
                else:
                    cursor.execute("""
                        SELECT integration_name, violation_type, current_value, threshold, 
                               timestamp, duration_minutes, severity, description
                        FROM sla_violations 
                        WHERE resolved = FALSE
                        ORDER BY timestamp DESC
                    """)
                
                violations = []
                for row in cursor.fetchall():
                    violations.append(SLAViolation(
                        integration_name=row[0],
                        violation_type=SLAViolationType(row[1]),
                        current_value=row[2],
                        threshold=row[3],
                        timestamp=datetime.fromisoformat(row[4]),
                        duration_minutes=row[5],
                        severity=row[6],
                        description=row[7]
                    ))
                
                return violations
                
        except Exception as e:
            self.logger.error(f"Erro ao buscar violações ativas: {e}")
            return []
    
    def get_grafana_metrics(self, integration_name: str, 
                           period_hours: int = 24) -> Dict[str, Any]:
        """
        Gera métricas no formato Grafana.
        
        Args:
            integration_name: Nome da integração
            period_hours: Período em horas
            
        Returns:
            Dicionário com métricas no formato Grafana
        """
        try:
            period_end = datetime.utcnow()
            period_start = period_end - timedelta(hours=period_hours)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Buscar métricas agregadas
                cursor.execute("""
                    SELECT metric_type, AVG(current_value) as avg_value, 
                           MIN(current_value) as min_value, MAX(current_value) as max_value,
                           COUNT(*) as count
                    FROM sla_metrics 
                    WHERE integration_name = ? AND timestamp BETWEEN ? AND ?
                    GROUP BY metric_type
                """, (integration_name, period_start.isoformat(), period_end.isoformat()))
                
                metrics_data = cursor.fetchall()
                
                # Formatar para Grafana
                grafana_metrics = {
                    "integration": integration_name,
                    "period": {
                        "start": period_start.isoformat(),
                        "end": period_end.isoformat()
                    },
                    "metrics": {}
                }
                
                for metric_type, avg_value, min_value, max_value, count in metrics_data:
                    grafana_metrics["metrics"][metric_type] = {
                        "average": round(avg_value, 2),
                        "minimum": round(min_value, 2),
                        "maximum": round(max_value, 2),
                        "count": count
                    }
                
                return grafana_metrics
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar métricas Grafana: {e}")
            return {}
    
    def export_compliance_report(self, output_path: str = "sla_compliance_report.json") -> None:
        """
        Exporta relatório completo de compliance.
        
        Args:
            output_path: Caminho do arquivo de saída
        """
        try:
            report_data = {
                "generated_at": datetime.utcnow().isoformat(),
                "integrations": {}
            }
            
            # Gerar relatório para cada integração
            for integration_name in self.sla_configs.keys():
                report = self.get_sla_report(integration_name)
                if report:
                    report_data["integrations"][integration_name] = asdict(report)
            
            # Salvar relatório
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Relatório de compliance exportado para {output_path}")
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar relatório de compliance: {e}")


def get_sla_checker() -> SLAChecker:
    """Retorna instância singleton do SLA Checker."""
    if not hasattr(get_sla_checker, '_instance'):
        get_sla_checker._instance = SLAChecker()
    return get_sla_checker._instance


if __name__ == '__main__':
    # Exemplo de uso
    sla_checker = get_sla_checker()
    
    # Registrar algumas métricas de exemplo
    sla_checker.record_metric("google_trends", "response_time", 1.5, "seconds")
    sla_checker.record_metric("google_trends", "availability", 99.8, "percentage")
    sla_checker.record_metric("amazon_api", "response_time", 4.0, "seconds")  # Violação
    
    # Gerar relatório
    report = sla_checker.get_sla_report("google_trends")
    if report:
        print(f"Relatório SLA para google_trends: {asdict(report)}")
    
    # Exportar relatório completo
    sla_checker.export_compliance_report() 
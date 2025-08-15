"""
Serviço de Métricas de Negócio - Omni Keywords Finder
Coleta automática, análise de tendências e insights de negócio
Prompt: Implementação de sistema de métricas de negócio
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import json
import logging
import uuid
import statistics
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import sqlite3
import os

from ..schemas.business_metrics_schemas import (
    BusinessMetric,
    MetricFilterSchema,
    MetricAnalysisSchema,
    KPISchema,
    DashboardSchema,
    MetricType,
    MetricPeriod,
    MetricCategory
)

@dataclass
class MetricCalculation:
    """Resultado de cálculo de métrica"""
    value: float
    previous_value: Optional[float]
    change_percentage: float
    trend_direction: str
    trend_strength: str

class BusinessMetricsService:
    """Serviço especializado para métricas de negócio"""
    
    def __init__(self, db_path: str = "business_metrics.db"):
        """Inicializa o serviço de métricas"""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.db = self._setup_database()
        
    def _setup_database(self) -> sqlite3.Connection:
        """Configura banco de dados SQLite para métricas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Criar tabela de métricas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_metrics (
                metric_id TEXT PRIMARY KEY,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                category TEXT NOT NULL,
                value REAL NOT NULL,
                previous_value REAL,
                target_value REAL,
                period TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                user_id TEXT,
                plan_type TEXT,
                region TEXT,
                source TEXT NOT NULL,
                version TEXT NOT NULL,
                environment TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Criar tabela de KPIs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kpis (
                kpi_id TEXT PRIMARY KEY,
                kpi_name TEXT NOT NULL,
                description TEXT NOT NULL,
                current_value REAL NOT NULL,
                target_value REAL NOT NULL,
                previous_value REAL NOT NULL,
                percentage_change REAL NOT NULL,
                target_achievement REAL NOT NULL,
                status TEXT NOT NULL,
                period TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                owner TEXT NOT NULL
            )
        ''')
        
        # Criar tabela de dashboards
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboards (
                dashboard_id TEXT PRIMARY KEY,
                dashboard_name TEXT NOT NULL,
                description TEXT NOT NULL,
                layout TEXT NOT NULL,
                refresh_interval INTEGER NOT NULL,
                auto_refresh BOOLEAN NOT NULL,
                metrics TEXT NOT NULL,
                kpis TEXT NOT NULL,
                is_public BOOLEAN NOT NULL,
                allowed_users TEXT NOT NULL,
                allowed_roles TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Criar índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metric_type ON business_metrics(metric_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON business_metrics(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_period ON business_metrics(period)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON business_metrics(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plan_type ON business_metrics(plan_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_start_date ON business_metrics(start_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_end_date ON business_metrics(end_date)')
        
        conn.commit()
        return conn
    
    def record_metric(self, metric: BusinessMetric) -> str:
        """
        Registra uma métrica de negócio
        
        Args:
            metric: Métrica a ser registrada
            
        Returns:
            ID da métrica registrada
        """
        try:
            cursor = self.db.cursor()
            
            cursor.execute('''
                INSERT INTO business_metrics (
                    metric_id, metric_type, metric_name, category,
                    value, previous_value, target_value, period,
                    start_date, end_date, user_id, plan_type, region,
                    source, version, environment, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric.metric_id,
                metric.metric_type,
                metric.metric_name,
                metric.category,
                metric.value,
                metric.previous_value,
                metric.target_value,
                metric.period,
                metric.start_date.isoformat(),
                metric.end_date.isoformat(),
                metric.user_id,
                metric.plan_type,
                metric.region,
                metric.source,
                metric.version,
                metric.environment,
                metric.created_at.isoformat()
            ))
            
            self.db.commit()
            
            self.logger.info(f"Métrica registrada: {metric.metric_name} = {metric.value}")
            return metric.metric_id
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar métrica: {str(e)}")
            raise
    
    def get_metrics(self, filters: MetricFilterSchema) -> List[Dict[str, Any]]:
        """
        Obtém métricas com filtros
        
        Args:
            filters: Filtros para consulta
            
        Returns:
            Lista de métricas
        """
        try:
            cursor = self.db.cursor()
            
            # Construir query
            query = "SELECT * FROM business_metrics WHERE 1=1"
            params = []
            
            # Filtros de tempo
            if filters.start_date:
                query += " AND start_date >= ?"
                params.append(filters.start_date.isoformat())
            
            if filters.end_date:
                query += " AND end_date <= ?"
                params.append(filters.end_date.isoformat())
            
            # Filtros de métrica
            if filters.metric_types:
                placeholders = ','.join(['?' for _ in filters.metric_types])
                query += f" AND metric_type IN ({placeholders})"
                params.extend(filters.metric_types)
            
            # Filtros de categoria
            if filters.categories:
                placeholders = ','.join(['?' for _ in filters.categories])
                query += f" AND category IN ({placeholders})"
                params.extend(filters.categories)
            
            # Filtros de período
            if filters.periods:
                placeholders = ','.join(['?' for _ in filters.periods])
                query += f" AND period IN ({placeholders})"
                params.extend(filters.periods)
            
            # Filtros de contexto
            if filters.user_id:
                query += " AND user_id = ?"
                params.append(filters.user_id)
            
            if filters.plan_type:
                query += " AND plan_type = ?"
                params.append(filters.plan_type)
            
            if filters.region:
                query += " AND region = ?"
                params.append(filters.region)
            
            # Ordenação
            query += f" ORDER BY {filters.sort_by} {filters.sort_order.upper()}"
            
            # Paginação
            if filters.limit:
                query += f" LIMIT {filters.limit}"
            
            if filters.offset:
                query += f" OFFSET {filters.offset}"
            
            # Executar query
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Converter para dicionários
            metrics = []
            for row in rows:
                metric = {
                    'metric_id': row[0],
                    'metric_type': row[1],
                    'metric_name': row[2],
                    'category': row[3],
                    'value': row[4],
                    'previous_value': row[5],
                    'target_value': row[6],
                    'period': row[7],
                    'start_date': row[8],
                    'end_date': row[9],
                    'user_id': row[10],
                    'plan_type': row[11],
                    'region': row[12],
                    'source': row[13],
                    'version': row[14],
                    'environment': row[15],
                    'created_at': row[16]
                }
                metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas: {str(e)}")
            return []
    
    def analyze_metrics(
        self,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        filters: Optional[MetricFilterSchema] = None
    ) -> MetricAnalysisSchema:
        """
        Analisa métricas e gera insights
        
        Args:
            metric_type: Tipo da métrica a analisar
            start_date: Data inicial
            end_date: Data final
            filters: Filtros opcionais
            
        Returns:
            Análise das métricas
        """
        try:
            # Obter métricas
            if filters:
                filters.metric_types = [metric_type]
                filters.start_date = start_date
                filters.end_date = end_date
            else:
                filters = MetricFilterSchema(
                    metric_types=[metric_type],
                    start_date=start_date,
                    end_date=end_date
                )
            
            metrics = self.get_metrics(filters)
            
            if not metrics:
                return self._create_empty_analysis(metric_type, start_date, end_date, filters)
            
            # Calcular estatísticas
            values = [m['value'] for m in metrics]
            total_records = len(metrics)
            average_value = statistics.mean(values)
            min_value = min(values)
            max_value = max(values)
            median_value = statistics.median(values)
            standard_deviation = statistics.stdev(values) if len(values) > 1 else 0
            
            # Calcular tendências
            growth_rate = self._calculate_growth_rate(metrics)
            trend_direction = self._determine_trend_direction(values)
            trend_strength = self._determine_trend_strength(values)
            
            # Análise por segmento
            by_plan_type = self._analyze_by_segment(metrics, 'plan_type')
            by_region = self._analyze_by_segment(metrics, 'region')
            by_period = self._analyze_by_segment(metrics, 'period')
            
            # Gerar insights
            insights = self._generate_insights(metrics, values, growth_rate, trend_direction)
            recommendations = self._generate_recommendations(metrics, values, growth_rate, trend_direction)
            alerts = self._generate_alerts(metrics, values, growth_rate, trend_direction)
            
            return MetricAnalysisSchema(
                analysis_id=str(uuid.uuid4()),
                metric_type=metric_type,
                period_start=start_date,
                period_end=end_date,
                total_records=total_records,
                average_value=average_value,
                min_value=min_value,
                max_value=max_value,
                median_value=median_value,
                standard_deviation=standard_deviation,
                growth_rate=growth_rate,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                by_plan_type=by_plan_type,
                by_region=by_region,
                by_period=by_period,
                insights=insights,
                recommendations=recommendations,
                alerts=alerts,
                filters_applied=filters
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar métricas: {str(e)}")
            raise
    
    def _create_empty_analysis(
        self,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        filters: MetricFilterSchema
    ) -> MetricAnalysisSchema:
        """Cria análise vazia quando não há dados"""
        return MetricAnalysisSchema(
            analysis_id=str(uuid.uuid4()),
            metric_type=metric_type,
            period_start=start_date,
            period_end=end_date,
            total_records=0,
            average_value=0.0,
            min_value=0.0,
            max_value=0.0,
            median_value=0.0,
            standard_deviation=0.0,
            growth_rate=0.0,
            trend_direction="stable",
            trend_strength="none",
            by_plan_type={},
            by_region={},
            by_period={},
            insights=["Nenhum dado disponível para análise"],
            recommendations=["Coletar mais dados para análise"],
            alerts=[],
            filters_applied=filters
        )
    
    def _calculate_growth_rate(self, metrics: List[Dict[str, Any]]) -> float:
        """Calcula taxa de crescimento"""
        if len(metrics) < 2:
            return 0.0
        
        # Ordenar por data
        sorted_metrics = sorted(metrics, key=lambda x: x['start_date'])
        
        first_value = sorted_metrics[0]['value']
        last_value = sorted_metrics[-1]['value']
        
        if first_value == 0:
            return 0.0
        
        return ((last_value - first_value) / first_value) * 100
    
    def _determine_trend_direction(self, values: List[float]) -> str:
        """Determina direção da tendência"""
        if len(values) < 3:
            return "stable"
        
        # Calcular correlação com tempo
        x = list(range(len(values)))
        correlation = self._calculate_correlation(x, values)
        
        if correlation > 0.7:
            return "up"
        elif correlation < -0.7:
            return "down"
        elif abs(correlation) < 0.3:
            return "stable"
        else:
            return "volatile"
    
    def _determine_trend_strength(self, values: List[float]) -> str:
        """Determina força da tendência"""
        if len(values) < 3:
            return "none"
        
        # Calcular coeficiente de variação
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0
        
        if mean == 0:
            return "none"
        
        cv = (std / mean) * 100
        
        if cv < 10:
            return "strong"
        elif cv < 25:
            return "moderate"
        else:
            return "weak"
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calcula correlação entre duas listas"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y[i] ** 2 for i in range(n))
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _analyze_by_segment(self, metrics: List[Dict[str, Any]], segment_key: str) -> Dict[str, float]:
        """Analisa métricas por segmento"""
        segment_values = defaultdict(list)
        
        for metric in metrics:
            segment_value = metric.get(segment_key, 'unknown')
            segment_values[segment_value].append(metric['value'])
        
        result = {}
        for segment, values in segment_values.items():
            result[segment] = statistics.mean(values)
        
        return result
    
    def _generate_insights(
        self,
        metrics: List[Dict[str, Any]],
        values: List[float],
        growth_rate: float,
        trend_direction: str
    ) -> List[str]:
        """Gera insights baseados nos dados"""
        insights = []
        
        # Insight sobre crescimento
        if growth_rate > 20:
            insights.append(f"Crescimento forte de {growth_rate:.1f}% no período")
        elif growth_rate > 5:
            insights.append(f"Crescimento moderado de {growth_rate:.1f}% no período")
        elif growth_rate < -20:
            insights.append(f"Declínio significativo de {abs(growth_rate):.1f}% no período")
        elif growth_rate < -5:
            insights.append(f"Declínio moderado de {abs(growth_rate):.1f}% no período")
        
        # Insight sobre tendência
        if trend_direction == "up":
            insights.append("Tendência de crescimento consistente")
        elif trend_direction == "down":
            insights.append("Tendência de declínio consistente")
        elif trend_direction == "volatile":
            insights.append("Alta volatilidade nos dados")
        
        # Insight sobre volume
        if len(metrics) > 100:
            insights.append("Volume significativo de dados coletados")
        elif len(metrics) < 10:
            insights.append("Volume baixo de dados - considerar coleta adicional")
        
        return insights
    
    def _generate_recommendations(
        self,
        metrics: List[Dict[str, Any]],
        values: List[float],
        growth_rate: float,
        trend_direction: str
    ) -> List[str]:
        """Gera recomendações baseadas nos dados"""
        recommendations = []
        
        # Recomendações baseadas no crescimento
        if growth_rate < -10:
            recommendations.append("Investigar causas do declínio e implementar ações corretivas")
        elif growth_rate > 50:
            recommendations.append("Avaliar se o crescimento é sustentável e escalar recursos")
        
        # Recomendações baseadas na tendência
        if trend_direction == "volatile":
            recommendations.append("Implementar controles para reduzir volatilidade")
        
        # Recomendações baseadas no volume
        if len(metrics) < 20:
            recommendations.append("Aumentar frequência de coleta de dados")
        
        return recommendations
    
    def _generate_alerts(
        self,
        metrics: List[Dict[str, Any]],
        values: List[float],
        growth_rate: float,
        trend_direction: str
    ) -> List[str]:
        """Gera alertas baseados nos dados"""
        alerts = []
        
        # Alertas baseados no crescimento
        if growth_rate < -30:
            alerts.append(f"ALERTA: Declínio crítico de {abs(growth_rate):.1f}%")
        elif growth_rate > 100:
            alerts.append(f"ALERTA: Crescimento anômalo de {growth_rate:.1f}%")
        
        # Alertas baseados na volatilidade
        if len(values) > 5:
            cv = (statistics.stdev(values) / statistics.mean(values)) * 100
            if cv > 50:
                alerts.append("ALERTA: Alta volatilidade detectada")
        
        return alerts
    
    def create_kpi(self, kpi: KPISchema) -> str:
        """Cria um novo KPI"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute('''
                INSERT INTO kpis (
                    kpi_id, kpi_name, description, current_value,
                    target_value, previous_value, percentage_change,
                    target_achievement, status, period, last_updated,
                    category, priority, owner
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                kpi.kpi_id,
                kpi.kpi_name,
                kpi.description,
                kpi.current_value,
                kpi.target_value,
                kpi.previous_value,
                kpi.percentage_change,
                kpi.target_achievement,
                kpi.status,
                kpi.period,
                kpi.last_updated.isoformat(),
                kpi.category,
                kpi.priority,
                kpi.owner
            ))
            
            self.db.commit()
            
            self.logger.info(f"KPI criado: {kpi.kpi_name}")
            return kpi.kpi_id
            
        except Exception as e:
            self.logger.error(f"Erro ao criar KPI: {str(e)}")
            raise
    
    def get_kpis(self) -> List[Dict[str, Any]]:
        """Obtém todos os KPIs"""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM kpis ORDER BY priority DESC, last_updated DESC")
            rows = cursor.fetchall()
            
            kpis = []
            for row in rows:
                kpi = {
                    'kpi_id': row[0],
                    'kpi_name': row[1],
                    'description': row[2],
                    'current_value': row[3],
                    'target_value': row[4],
                    'previous_value': row[5],
                    'percentage_change': row[6],
                    'target_achievement': row[7],
                    'status': row[8],
                    'period': row[9],
                    'last_updated': row[10],
                    'category': row[11],
                    'priority': row[12],
                    'owner': row[13]
                }
                kpis.append(kpi)
            
            return kpis
            
        except Exception as e:
            self.logger.error(f"Erro ao obter KPIs: {str(e)}")
            return []
    
    def update_kpi(self, kpi_id: str, updates: Dict[str, Any]) -> bool:
        """Atualiza um KPI"""
        try:
            cursor = self.db.cursor()
            
            # Construir query de atualização
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            query = f"UPDATE kpis SET {set_clause} WHERE kpi_id = ?"
            
            params = list(updates.values()) + [kpi_id]
            cursor.execute(query, params)
            
            self.db.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar KPI: {str(e)}")
            return False
    
    def create_dashboard(self, dashboard: DashboardSchema) -> str:
        """Cria um novo dashboard"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute('''
                INSERT INTO dashboards (
                    dashboard_id, dashboard_name, description, layout,
                    refresh_interval, auto_refresh, metrics, kpis,
                    is_public, allowed_users, allowed_roles,
                    created_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dashboard.dashboard_id,
                dashboard.dashboard_name,
                dashboard.description,
                json.dumps(dashboard.layout),
                dashboard.refresh_interval,
                dashboard.auto_refresh,
                json.dumps(dashboard.metrics),
                json.dumps(dashboard.kpis),
                dashboard.is_public,
                json.dumps(dashboard.allowed_users),
                json.dumps(dashboard.allowed_roles),
                dashboard.created_by,
                dashboard.created_at.isoformat(),
                dashboard.updated_at.isoformat()
            ))
            
            self.db.commit()
            
            self.logger.info(f"Dashboard criado: {dashboard.dashboard_name}")
            return dashboard.dashboard_id
            
        except Exception as e:
            self.logger.error(f"Erro ao criar dashboard: {str(e)}")
            raise
    
    def get_dashboards(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtém dashboards disponíveis"""
        try:
            cursor = self.db.cursor()
            
            if user_id:
                query = "SELECT * FROM dashboards WHERE is_public = 1 OR allowed_users LIKE ?"
                cursor.execute(query, [f"%{user_id}%"])
            else:
                cursor.execute("SELECT * FROM dashboards WHERE is_public = 1")
            
            rows = cursor.fetchall()
            
            dashboards = []
            for row in rows:
                dashboard = {
                    'dashboard_id': row[0],
                    'dashboard_name': row[1],
                    'description': row[2],
                    'layout': json.loads(row[3]),
                    'refresh_interval': row[4],
                    'auto_refresh': row[5],
                    'metrics': json.loads(row[6]),
                    'kpis': json.loads(row[7]),
                    'is_public': row[8],
                    'allowed_users': json.loads(row[9]),
                    'allowed_roles': json.loads(row[10]),
                    'created_by': row[11],
                    'created_at': row[12],
                    'updated_at': row[13]
                }
                dashboards.append(dashboard)
            
            return dashboards
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dashboards: {str(e)}")
            return []
    
    def close(self):
        """Fecha conexões"""
        if self.db:
            self.db.close() 
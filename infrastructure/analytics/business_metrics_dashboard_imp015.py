#!/usr/bin/env python3
"""
Dashboard de Métricas de Negócio - IMP-015
Tracing ID: IMP015_DASHBOARD_001_20241227
Data: 2024-12-27
Status: Implementação Inicial

Dashboard enterprise-grade de métricas de negócio com:
- Visualizações interativas
- Relatórios automáticos
- Alertas inteligentes
- Exportação de dados
- Integração com múltiplas fontes
"""

import json
import os
import time
import uuid
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import logging
from enum import Enum
import asyncio
import sqlite3
from pathlib import Path

# Dependências opcionais
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import dash
    from dash import dcc, html, Input, Output, callback
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Tipos de métricas suportadas"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    CUSTOM = "custom"

class AlertSeverity(Enum):
    """Severidades de alerta"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"

@dataclass
class BusinessMetric:
    """Estrutura de métrica de negócio"""
    name: str
    value: float
    unit: str
    category: str
    timestamp: datetime
    trend: str = "stable"  # up, down, stable
    change_percent: float = 0.0
    target_value: Optional[float] = None
    alert_threshold: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class DashboardWidget:
    """Widget do dashboard"""
    id: str
    title: str
    widget_type: str
    data_source: str
    refresh_interval: int = 60
    position: Dict[str, int] = None
    size: Dict[str, int] = None
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.position is None:
            self.position = {"value": 0, "result": 0}
        if self.size is None:
            self.size = {"width": 6, "height": 4}
        if self.config is None:
            self.config = {}

@dataclass
class AlertRule:
    """Regra de alerta"""
    id: str
    name: str
    metric_name: str
    condition: str  # >, <, >=, <=, ==, !=
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 15
    notification_channels: List[str] = None
    
    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ["email"]

class BusinessMetricsDashboard:
    """Dashboard principal de métricas de negócio"""
    
    def __init__(self, 
                 db_path: str = "data/business_metrics.db",
                 enable_web_dashboard: bool = True,
                 enable_alerts: bool = True):
        """
        Inicializa o dashboard
        
        Args:
            db_path: Caminho para banco de dados SQLite
            enable_web_dashboard: Habilita dashboard web
            enable_alerts: Habilita sistema de alertas
        """
        self.db_path = db_path
        self.enable_web_dashboard = enable_web_dashboard and DASH_AVAILABLE
        self.enable_alerts = enable_alerts
        
        # Inicializar banco de dados
        self._init_database()
        
        # Métricas em memória
        self.metrics_cache = defaultdict(deque)
        self.widgets = {}
        self.alert_rules = {}
        self.alert_history = deque(maxlen=1000)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Configurações
        self.config = {
            "refresh_interval": 60,
            "max_data_points": 10000,
            "retention_days": 90,
            "enable_export": True,
            "enable_notifications": True
        }
        
        # Inicializar componentes
        self._init_widgets()
        self._init_alert_rules()
        
        if self.enable_web_dashboard:
            self._init_web_dashboard()
        
        logger.info(f"[DASHBOARD] Dashboard inicializado - DB: {db_path}")
    
    def _init_database(self):
        """Inicializa banco de dados"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de métricas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS business_metrics (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        value REAL NOT NULL,
                        unit TEXT,
                        category TEXT,
                        timestamp DATETIME NOT NULL,
                        trend TEXT,
                        change_percent REAL,
                        target_value REAL,
                        alert_threshold REAL,
                        metadata TEXT
                    )
                """)
                
                # Tabela de widgets
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dashboard_widgets (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        widget_type TEXT NOT NULL,
                        data_source TEXT NOT NULL,
                        refresh_interval INTEGER,
                        position TEXT,
                        size TEXT,
                        config TEXT
                    )
                """)
                
                # Tabela de alertas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alert_rules (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        metric_name TEXT NOT NULL,
                        condition TEXT NOT NULL,
                        threshold REAL NOT NULL,
                        severity TEXT NOT NULL,
                        enabled BOOLEAN,
                        cooldown_minutes INTEGER,
                        notification_channels TEXT
                    )
                """)
                
                # Tabela de histórico de alertas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alert_history (
                        id TEXT PRIMARY KEY,
                        rule_id TEXT NOT NULL,
                        metric_name TEXT NOT NULL,
                        current_value REAL NOT NULL,
                        threshold REAL NOT NULL,
                        severity TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        message TEXT
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    def _init_widgets(self):
        """Inicializa widgets padrão"""
        default_widgets = [
            DashboardWidget(
                id="revenue_overview",
                title="Visão Geral de Receita",
                widget_type="metric_card",
                data_source="revenue_metrics",
                position={"value": 0, "result": 0},
                size={"width": 3, "height": 2}
            ),
            DashboardWidget(
                id="keyword_performance",
                title="Performance de Keywords",
                widget_type="line_chart",
                data_source="keyword_metrics",
                position={"value": 3, "result": 0},
                size={"width": 6, "height": 3}
            ),
            DashboardWidget(
                id="user_engagement",
                title="Engajamento de Usuários",
                widget_type="bar_chart",
                data_source="user_metrics",
                position={"value": 0, "result": 2},
                size={"width": 4, "height": 3}
            ),
            DashboardWidget(
                id="conversion_funnel",
                title="Funil de Conversão",
                widget_type="funnel_chart",
                data_source="conversion_metrics",
                position={"value": 4, "result": 2},
                size={"width": 5, "height": 3}
            ),
            DashboardWidget(
                id="top_keywords",
                title="Top Keywords",
                widget_type="table",
                data_source="keyword_ranking",
                position={"value": 0, "result": 5},
                size={"width": 6, "height": 3}
            ),
            DashboardWidget(
                id="system_health",
                title="Saúde do Sistema",
                widget_type="gauge_chart",
                data_source="system_metrics",
                position={"value": 6, "result": 5},
                size={"width": 3, "height": 3}
            )
        ]
        
        for widget in default_widgets:
            self.widgets[widget.id] = widget
    
    def _init_alert_rules(self):
        """Inicializa regras de alerta padrão"""
        default_rules = [
            AlertRule(
                id="revenue_drop",
                name="Queda de Receita",
                metric_name="daily_revenue",
                condition="<",
                threshold=1000.0,
                severity=AlertSeverity.CRITICAL,
                cooldown_minutes=30
            ),
            AlertRule(
                id="high_error_rate",
                name="Taxa de Erro Alta",
                metric_name="error_rate",
                condition=">",
                threshold=5.0,
                severity=AlertSeverity.WARNING,
                cooldown_minutes=15
            ),
            AlertRule(
                id="low_conversion",
                name="Conversão Baixa",
                metric_name="conversion_rate",
                condition="<",
                threshold=2.0,
                severity=AlertSeverity.WARNING,
                cooldown_minutes=60
            ),
            AlertRule(
                id="system_overload",
                name="Sistema Sobrecarregado",
                metric_name="cpu_usage",
                condition=">",
                threshold=90.0,
                severity=AlertSeverity.CRITICAL,
                cooldown_minutes=10
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.id] = rule
    
    def _init_web_dashboard(self):
        """Inicializa dashboard web"""
        if not DASH_AVAILABLE:
            logger.warning("Dash não disponível. Dashboard web desabilitado.")
            return
        
        try:
            self.app = dash.Dash(__name__)
            self._setup_dashboard_layout()
            self._setup_dashboard_callbacks()
            logger.info("Dashboard web inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar dashboard web: {e}")
            self.enable_web_dashboard = False
    
    def _setup_dashboard_layout(self):
        """Configura layout do dashboard web"""
        self.app.layout = html.Div([
            html.H1("Dashboard de Métricas de Negócio - Omni Keywords Finder"),
            
            # Filtros
            html.Div([
                dcc.DatePickerRange(
                    id='date-range',
                    start_date=date.today() - timedelta(days=30),
                    end_date=date.today(),
                    display_format='DD/MM/YYYY'
                ),
                dcc.Dropdown(
                    id='category-filter',
                    options=[
                        {'label': 'Receita', 'value': 'revenue'},
                        {'label': 'Keywords', 'value': 'keywords'},
                        {'label': 'Usuários', 'value': 'users'},
                        {'label': 'Sistema', 'value': 'system'}
                    ],
                    value=['revenue', 'keywords', 'users', 'system'],
                    multi=True
                )
            ], style={'margin': '20px'}),
            
            # Widgets
            html.Div([
                # Primeira linha
                html.Div([
                    html.Div(id='revenue-overview', className='widget'),
                    html.Div(id='keyword-performance', className='widget'),
                ], className='row'),
                
                # Segunda linha
                html.Div([
                    html.Div(id='user-engagement', className='widget'),
                    html.Div(id='conversion-funnel', className='widget'),
                ], className='row'),
                
                # Terceira linha
                html.Div([
                    html.Div(id='top-keywords', className='widget'),
                    html.Div(id='system-health', className='widget'),
                ], className='row'),
            ], id='dashboard-widgets'),
            
            # Atualização automática
            dcc.Interval(
                id='interval-component',
                interval=60*1000,  # 60 segundos
                n_intervals=0
            )
        ])
    
    def _setup_dashboard_callbacks(self):
        """Configura callbacks do dashboard"""
        @self.app.callback(
            Output('revenue-overview', 'children'),
            Input('interval-component', 'n_intervals'),
            Input('date-range', 'start_date'),
            Input('date-range', 'end_date')
        )
        def update_revenue_overview(n, start_date, end_date):
            return self._create_revenue_widget(start_date, end_date)
        
        @self.app.callback(
            Output('keyword-performance', 'children'),
            Input('interval-component', 'n_intervals'),
            Input('date-range', 'start_date'),
            Input('date-range', 'end_date')
        )
        def update_keyword_performance(n, start_date, end_date):
            return self._create_keyword_performance_widget(start_date, end_date)
        
        # Adicionar mais callbacks conforme necessário
    
    def record_metric(self, metric: BusinessMetric):
        """Registra uma métrica no dashboard"""
        try:
            with self._lock:
                # Adicionar ao cache
                self.metrics_cache[metric.name].append(metric)
                
                # Limitar tamanho do cache
                if len(self.metrics_cache[metric.name]) > self.config["max_data_points"]:
                    self.metrics_cache[metric.name].popleft()
                
                # Salvar no banco
                self._save_metric_to_db(metric)
                
                # Verificar alertas
                if self.enable_alerts:
                    self._check_alerts(metric)
                
        except Exception as e:
            logger.error(f"Erro ao registrar métrica {metric.name}: {e}")
    
    def _save_metric_to_db(self, metric: BusinessMetric):
        """Salva métrica no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO business_metrics 
                    (id, name, value, unit, category, timestamp, trend, change_percent, 
                     target_value, alert_threshold, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    metric.name,
                    metric.value,
                    metric.unit,
                    metric.category,
                    metric.timestamp.isoformat(),
                    metric.trend,
                    metric.change_percent,
                    metric.target_value,
                    metric.alert_threshold,
                    json.dumps(metric.metadata)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar métrica no banco: {e}")
    
    def _check_alerts(self, metric: BusinessMetric):
        """Verifica regras de alerta"""
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled or rule.metric_name != metric.name:
                continue
            
            # Verificar se está em cooldown
            if self._is_alert_in_cooldown(rule_id):
                continue
            
            # Verificar condição
            triggered = False
            if rule.condition == ">":
                triggered = metric.value > rule.threshold
            elif rule.condition == "<":
                triggered = metric.value < rule.threshold
            elif rule.condition == ">=":
                triggered = metric.value >= rule.threshold
            elif rule.condition == "<=":
                triggered = metric.value <= rule.threshold
            elif rule.condition == "==":
                triggered = metric.value == rule.threshold
            elif rule.condition == "!=":
                triggered = metric.value != rule.threshold
            
            if triggered:
                self._trigger_alert(rule, metric)
    
    def _is_alert_in_cooldown(self, rule_id: str) -> bool:
        """Verifica se alerta está em cooldown"""
        rule = self.alert_rules.get(rule_id)
        if not rule:
            return False
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=rule.cooldown_minutes)
        
        # Verificar histórico recente
        for alert in self.alert_history:
            if alert["rule_id"] == rule_id and alert["timestamp"] > cutoff_time:
                return True
        
        return False
    
    def _trigger_alert(self, rule: AlertRule, metric: BusinessMetric):
        """Dispara um alerta"""
        alert = {
            "id": str(uuid.uuid4()),
            "rule_id": rule.id,
            "metric_name": metric.name,
            "current_value": metric.value,
            "threshold": rule.threshold,
            "severity": rule.severity.value,
            "timestamp": datetime.utcnow(),
            "message": f"Alerta {rule.severity.value.upper()}: {metric.name} = {metric.value} {rule.condition} {rule.threshold}"
        }
        
        # Adicionar ao histórico
        self.alert_history.append(alert)
        
        # Salvar no banco
        self._save_alert_to_db(alert)
        
        # Enviar notificação
        if self.config["enable_notifications"]:
            self._send_notification(alert)
        
        logger.warning(f"ALERTA {rule.severity.value.upper()}: {alert['message']}")
    
    def _save_alert_to_db(self, alert: Dict[str, Any]):
        """Salva alerta no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO alert_history 
                    (id, rule_id, metric_name, current_value, threshold, severity, timestamp, message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert["id"],
                    alert["rule_id"],
                    alert["metric_name"],
                    alert["current_value"],
                    alert["threshold"],
                    alert["severity"],
                    alert["timestamp"].isoformat(),
                    alert["message"]
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar alerta no banco: {e}")
    
    def _send_notification(self, alert: Dict[str, Any]):
        """Envia notificação"""
        # Implementar integração com sistemas de notificação
        # Email, Slack, SMS, etc.
        logger.info(f"Notificação enviada: {alert['message']}")
    
    def get_metrics(self, 
                   metric_names: Optional[List[str]] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   category: Optional[str] = None) -> Dict[str, List[BusinessMetric]]:
        """Obtém métricas filtradas"""
        try:
            with self._lock:
                if start_time is None:
                    start_time = datetime.utcnow() - timedelta(hours=24)
                if end_time is None:
                    end_time = datetime.utcnow()
                
                # Filtrar do cache primeiro
                result = {}
                for name, metrics in self.metrics_cache.items():
                    if metric_names and name not in metric_names:
                        continue
                    
                    filtered_metrics = [
                        m for m in metrics
                        if start_time <= m.timestamp <= end_time
                        and (category is None or m.category == category)
                    ]
                    
                    if filtered_metrics:
                        result[name] = filtered_metrics
                
                # Se não encontrou no cache, buscar no banco
                if not result and metric_names:
                    result = self._get_metrics_from_db(metric_names, start_time, end_time, category)
                
                return result
                
        except Exception as e:
            logger.error(f"Erro ao obter métricas: {e}")
            return {}
    
    def _get_metrics_from_db(self, 
                           metric_names: List[str],
                           start_time: datetime,
                           end_time: datetime,
                           category: Optional[str] = None) -> Dict[str, List[BusinessMetric]]:
        """Obtém métricas do banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT name, value, unit, category, timestamp, trend, change_percent,
                           target_value, alert_threshold, metadata
                    FROM business_metrics
                    WHERE name IN ({})
                    AND timestamp BETWEEN ? AND ?
                """.format(','.join(['?'] * len(metric_names)))
                
                params = metric_names + [start_time.isoformat(), end_time.isoformat()]
                
                if category:
                    query += " AND category = ?"
                    params.append(category)
                
                query += " ORDER BY timestamp DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                result = defaultdict(list)
                for row in rows:
                    metric = BusinessMetric(
                        name=row[0],
                        value=row[1],
                        unit=row[2],
                        category=row[3],
                        timestamp=datetime.fromisoformat(row[4]),
                        trend=row[5],
                        change_percent=row[6],
                        target_value=row[7],
                        alert_threshold=row[8],
                        metadata=json.loads(row[9]) if row[9] else {}
                    )
                    result[metric.name].append(metric)
                
                return dict(result)
                
        except Exception as e:
            logger.error(f"Erro ao buscar métricas no banco: {e}")
            return {}
    
    def get_dashboard_data(self, widget_id: str) -> Dict[str, Any]:
        """Obtém dados para um widget específico"""
        widget = self.widgets.get(widget_id)
        if not widget:
            return {}
        
        # Obter métricas baseadas no data_source
        metrics = self.get_metrics_by_source(widget.data_source)
        
        # Processar dados baseado no tipo de widget
        if widget.widget_type == "metric_card":
            return self._process_metric_card_data(metrics)
        elif widget.widget_type == "line_chart":
            return self._process_line_chart_data(metrics)
        elif widget.widget_type == "bar_chart":
            return self._process_bar_chart_data(metrics)
        elif widget.widget_type == "funnel_chart":
            return self._process_funnel_chart_data(metrics)
        elif widget.widget_type == "table":
            return self._process_table_data(metrics)
        elif widget.widget_type == "gauge_chart":
            return self._process_gauge_chart_data(metrics)
        else:
            return {"error": f"Tipo de widget não suportado: {widget.widget_type}"}
    
    def get_metrics_by_source(self, data_source: str) -> Dict[str, List[BusinessMetric]]:
        """Obtém métricas por fonte de dados"""
        source_mappings = {
            "revenue_metrics": ["daily_revenue", "monthly_revenue", "revenue_growth"],
            "keyword_metrics": ["keywords_processed", "keyword_ranking", "keyword_roi"],
            "user_metrics": ["active_users", "user_engagement", "user_retention"],
            "conversion_metrics": ["conversion_rate", "conversion_funnel", "conversion_value"],
            "keyword_ranking": ["top_keywords", "keyword_position", "keyword_volume"],
            "system_metrics": ["cpu_usage", "memory_usage", "error_rate"]
        }
        
        metric_names = source_mappings.get(data_source, [])
        return self.get_metrics(metric_names=metric_names)
    
    def _process_metric_card_data(self, metrics: Dict[str, List[BusinessMetric]]) -> Dict[str, Any]:
        """Processa dados para widget de cartão de métrica"""
        if not metrics:
            return {"value": 0, "trend": "stable", "change_percent": 0}
        
        # Pegar métrica mais recente
        latest_metric = None
        for metric_list in metrics.values():
            if metric_list:
                latest = max(metric_list, key=lambda m: m.timestamp)
                if latest_metric is None or latest.timestamp > latest_metric.timestamp:
                    latest_metric = latest
        
        if latest_metric:
            return {
                "value": latest_metric.value,
                "unit": latest_metric.unit,
                "trend": latest_metric.trend,
                "change_percent": latest_metric.change_percent,
                "target_value": latest_metric.target_value
            }
        
        return {"value": 0, "trend": "stable", "change_percent": 0}
    
    def _process_line_chart_data(self, metrics: Dict[str, List[BusinessMetric]]) -> Dict[str, Any]:
        """Processa dados para gráfico de linha"""
        if not PANDAS_AVAILABLE:
            return {"error": "Pandas não disponível"}
        
        data = []
        for metric_name, metric_list in metrics.items():
            if metric_list:
                df = pd.DataFrame([
                    {
                        "timestamp": m.timestamp,
                        "value": m.value,
                        "metric": metric_name
                    }
                    for m in metric_list
                ])
                data.append({
                    "name": metric_name,
                    "value": df["timestamp"].tolist(),
                    "result": df["value"].tolist(),
                    "type": "scatter",
                    "mode": "lines+markers"
                })
        
        return {"data": data}
    
    def _process_bar_chart_data(self, metrics: Dict[str, List[BusinessMetric]]) -> Dict[str, Any]:
        """Processa dados para gráfico de barras"""
        if not PANDAS_AVAILABLE:
            return {"error": "Pandas não disponível"}
        
        data = []
        for metric_name, metric_list in metrics.items():
            if metric_list:
                # Agrupar por categoria se disponível
                categories = defaultdict(list)
                for metric in metric_list:
                    category = metric.metadata.get("category", "default")
                    categories[category].append(metric.value)
                
                for category, values in categories.items():
                    data.append({
                        "name": f"{metric_name} - {category}",
                        "value": [category],
                        "result": [sum(values) / len(values)],  # Média
                        "type": "bar"
                    })
        
        return {"data": data}
    
    def _process_funnel_chart_data(self, metrics: Dict[str, List[BusinessMetric]]) -> Dict[str, Any]:
        """Processa dados para gráfico de funil"""
        # Implementar lógica específica para funil de conversão
        return {"data": [], "stages": ["Visitas", "Interesse", "Consideração", "Conversão"]}
    
    def _process_table_data(self, metrics: Dict[str, List[BusinessMetric]]) -> Dict[str, Any]:
        """Processa dados para tabela"""
        table_data = []
        headers = ["Métrica", "Valor", "Tendência", "Mudança %", "Última Atualização"]
        
        for metric_name, metric_list in metrics.items():
            if metric_list:
                latest = max(metric_list, key=lambda m: m.timestamp)
                table_data.append([
                    metric_name,
                    f"{latest.value:.2f} {latest.unit or ''}",
                    latest.trend,
                    f"{latest.change_percent:.1f}%",
                    latest.timestamp.strftime("%data/%m/%Y %H:%M")
                ])
        
        return {"headers": headers, "data": table_data}
    
    def _process_gauge_chart_data(self, metrics: Dict[str, List[BusinessMetric]]) -> Dict[str, Any]:
        """Processa dados para gráfico de gauge"""
        if not metrics:
            return {"value": 0, "min": 0, "max": 100}
        
        # Calcular valor médio das métricas de sistema
        total_value = 0
        count = 0
        
        for metric_list in metrics.values():
            if metric_list:
                latest = max(metric_list, key=lambda m: m.timestamp)
                total_value += latest.value
                count += 1
        
        avg_value = total_value / count if count > 0 else 0
        
        return {
            "value": avg_value,
            "min": 0,
            "max": 100,
            "thresholds": [50, 80, 90]  # Warning, Critical, Error
        }
    
    def export_data(self, 
                   format_type: str = "json",
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   metrics: Optional[List[str]] = None) -> str:
        """Exporta dados do dashboard"""
        try:
            if not self.config["enable_export"]:
                return "Exportação desabilitada"
            
            # Obter dados
            data = self.get_metrics(
                metric_names=metrics,
                start_time=start_time,
                end_time=end_time
            )
            
            if format_type == "json":
                return json.dumps(data, default=str, indent=2)
            elif format_type == "csv" and PANDAS_AVAILABLE:
                # Converter para DataFrame e exportar CSV
                all_metrics = []
                for metric_name, metric_list in data.items():
                    for metric in metric_list:
                        all_metrics.append({
                            "name": metric.name,
                            "value": metric.value,
                            "unit": metric.unit,
                            "category": metric.category,
                            "timestamp": metric.timestamp,
                            "trend": metric.trend,
                            "change_percent": metric.change_percent,
                            "metadata": json.dumps(metric.metadata)
                        })
                
                df = pd.DataFrame(all_metrics)
                csv_path = f"exports/business_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                os.makedirs("exports", exist_ok=True)
                df.to_csv(csv_path, index=False)
                return csv_path
            else:
                return f"Formato não suportado: {format_type}"
                
        except Exception as e:
            logger.error(f"Erro ao exportar dados: {e}")
            return f"Erro na exportação: {e}"
    
    def run_web_dashboard(self, host: str = "0.0.0.0", port: int = 8050, debug: bool = False):
        """Executa dashboard web"""
        if not self.enable_web_dashboard:
            logger.error("Dashboard web não está habilitado")
            return
        
        try:
            logger.info(f"Iniciando dashboard web em http://{host}:{port}")
            self.app.run_server(host=host, port=port, debug=debug)
        except Exception as e:
            logger.error(f"Erro ao executar dashboard web: {e}")
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Obtém resumo do dashboard"""
        try:
            with self._lock:
                # Estatísticas gerais
                total_metrics = sum(len(metrics) for metrics in self.metrics_cache.values())
                total_widgets = len(self.widgets)
                total_alerts = len(self.alert_history)
                
                # Métricas por categoria
                categories = defaultdict(int)
                for metrics in self.metrics_cache.values():
                    for metric in metrics:
                        categories[metric.category] += 1
                
                # Alertas por severidade
                alert_severities = defaultdict(int)
                for alert in self.alert_history:
                    alert_severities[alert["severity"]] += 1
                
                return {
                    "total_metrics": total_metrics,
                    "total_widgets": total_widgets,
                    "total_alerts": total_alerts,
                    "metrics_by_category": dict(categories),
                    "alerts_by_severity": dict(alert_severities),
                    "last_update": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter resumo do dashboard: {e}")
            return {"error": str(e)}

# Instância global
_dashboard_instance = None

def get_business_dashboard() -> BusinessMetricsDashboard:
    """Obtém instância global do dashboard"""
    global _dashboard_instance
    if _dashboard_instance is None:
        _dashboard_instance = BusinessMetricsDashboard()
    return _dashboard_instance

def record_business_metric(name: str, value: float, unit: str = "", 
                          category: str = "general", **kwargs):
    """Função de conveniência para registrar métrica"""
    dashboard = get_business_dashboard()
    metric = BusinessMetric(
        name=name,
        value=value,
        unit=unit,
        category=category,
        timestamp=datetime.utcnow(),
        **kwargs
    )
    dashboard.record_metric(metric)

if __name__ == "__main__":
    # Exemplo de uso
    dashboard = BusinessMetricsDashboard()
    
    # Registrar algumas métricas de exemplo
    record_business_metric("daily_revenue", 15000.0, "USD", "revenue", trend="up", change_percent=5.2)
    record_business_metric("active_users", 1250, "users", "users", trend="stable", change_percent=0.1)
    record_business_metric("keywords_processed", 5000, "keywords", "keywords", trend="up", change_percent=12.5)
    record_business_metric("conversion_rate", 3.2, "%", "conversion", trend="down", change_percent=-0.5)
    
    # Executar dashboard web
    dashboard.run_web_dashboard(debug=True) 
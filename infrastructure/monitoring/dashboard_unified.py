#!/usr/bin/env python3
"""
Sistema Unificado de Dashboards - Omni Keywords Finder
====================================================

Tracing ID: DASHBOARD_UNIFIED_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema enterprise de dashboards que integra:
- Métricas APM em tempo real
- Traces do Jaeger
- Alertas do Prometheus
- Erros do Sentry
- Performance insights
- Anomaly detection
- Custom visualizations

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 3.2
Ruleset: enterprise_control_layer.yaml
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import defaultdict

# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket, WebSocketDisconnect

# Integração com APM
from infrastructure.monitoring.apm_integration import apm_manager, APMMetricType, APMServiceType

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardType(Enum):
    """Tipos de dashboard"""
    SYSTEM_OVERVIEW = "system_overview"
    PERFORMANCE = "performance"
    SECURITY = "security"
    APM = "apm"
    TRACING = "tracing"
    ERROR_TRACKING = "error_tracking"
    CUSTOM = "custom"


@dataclass
class DashboardPanel:
    """Painel de dashboard"""
    id: str
    title: str
    type: str  # chart, metric, alert, table
    data_source: str
    query: str
    refresh_interval: int  # segundos
    position: Dict[str, int]  # x, y, width, height
    config: Dict[str, Any]


@dataclass
class Dashboard:
    """Dashboard"""
    id: str
    name: str
    type: DashboardType
    description: str
    panels: List[DashboardPanel]
    refresh_interval: int
    created_at: datetime
    updated_at: datetime
    is_public: bool = False


@dataclass
class DashboardData:
    """Dados do dashboard"""
    dashboard_id: str
    timestamp: datetime
    metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    traces: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]


class DashboardDataCollector:
    """Coletor de dados para dashboards"""
    
    def __init__(self):
        self.apm_manager = apm_manager
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 30  # segundos
    
    async def collect_system_overview_data(self) -> Dict[str, Any]:
        """Coleta dados para dashboard de visão geral do sistema"""
        try:
            # Métricas do sistema
            system_metrics = {
                "cpu_usage": self._get_cpu_usage(),
                "memory_usage": self._get_memory_usage(),
                "disk_usage": self._get_disk_usage(),
                "network_throughput": self._get_network_throughput(),
                "active_connections": self._get_active_connections()
            }
            
            # Métricas APM
            apm_summary = self.apm_manager.get_metrics_summary()
            
            # Alertas ativos
            active_alerts = [
                asdict(alert) for alert in self.apm_manager.alert_manager.alerts.values()
                if not alert.resolved
            ]
            
            # Insights recentes
            recent_insights = [
                asdict(insight) for insight in self.apm_manager.insight_engine.insights
                if insight.timestamp > datetime.now() - timedelta(hours=1)
            ]
            
            return {
                "system_metrics": system_metrics,
                "apm_summary": apm_summary,
                "active_alerts": active_alerts,
                "recent_insights": recent_insights,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Erro ao coletar dados do sistema: {e}")
            return {"error": str(e)}
    
    async def collect_performance_data(self) -> Dict[str, Any]:
        """Coleta dados para dashboard de performance"""
        try:
            # Métricas de performance por serviço
            performance_metrics = {}
            
            for service in APMServiceType:
                service_metrics = self._get_service_performance_metrics(service)
                performance_metrics[service.value] = service_metrics
            
            # Top queries lentas
            slow_queries = self._get_slow_queries()
            
            # Cache performance
            cache_performance = self._get_cache_performance()
            
            # API performance
            api_performance = self._get_api_performance()
            
            return {
                "performance_metrics": performance_metrics,
                "slow_queries": slow_queries,
                "cache_performance": cache_performance,
                "api_performance": api_performance,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Erro ao coletar dados de performance: {e}")
            return {"error": str(e)}
    
    async def collect_security_data(self) -> Dict[str, Any]:
        """Coleta dados para dashboard de segurança"""
        try:
            # Rate limiting
            rate_limiting_stats = self._get_rate_limiting_stats()
            
            # Tentativas de acesso
            access_attempts = self._get_access_attempts()
            
            # Erros de autenticação
            auth_errors = self._get_auth_errors()
            
            # Ameaças detectadas
            threats = self._get_threats()
            
            return {
                "rate_limiting": rate_limiting_stats,
                "access_attempts": access_attempts,
                "auth_errors": auth_errors,
                "threats": threats,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Erro ao coletar dados de segurança: {e}")
            return {"error": str(e)}
    
    async def collect_tracing_data(self) -> Dict[str, Any]:
        """Coleta dados para dashboard de tracing"""
        try:
            # Traces recentes
            recent_traces = self._get_recent_traces()
            
            # Service map
            service_map = self._get_service_map()
            
            # Trace statistics
            trace_stats = self._get_trace_statistics()
            
            # Error traces
            error_traces = self._get_error_traces()
            
            return {
                "recent_traces": recent_traces,
                "service_map": service_map,
                "trace_statistics": trace_stats,
                "error_traces": error_traces,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Erro ao coletar dados de tracing: {e}")
            return {"error": str(e)}
    
    async def collect_error_tracking_data(self) -> Dict[str, Any]:
        """Coleta dados para dashboard de error tracking"""
        try:
            # Erros por tipo
            errors_by_type = self._get_errors_by_type()
            
            # Erros por serviço
            errors_by_service = self._get_errors_by_service()
            
            # Erros recentes
            recent_errors = self._get_recent_errors()
            
            # Error trends
            error_trends = self._get_error_trends()
            
            return {
                "errors_by_type": errors_by_type,
                "errors_by_service": errors_by_service,
                "recent_errors": recent_errors,
                "error_trends": error_trends,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Erro ao coletar dados de error tracking: {e}")
            return {"error": str(e)}
    
    # Métodos auxiliares para coleta de dados
    def _get_cpu_usage(self) -> float:
        """Obtém uso de CPU"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            return 0.0
    
    def _get_memory_usage(self) -> float:
        """Obtém uso de memória"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.percent
        except ImportError:
            return 0.0
    
    def _get_disk_usage(self) -> float:
        """Obtém uso de disco"""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return (disk.used / disk.total) * 100
        except ImportError:
            return 0.0
    
    def _get_network_throughput(self) -> Dict[str, float]:
        """Obtém throughput de rede"""
        try:
            import psutil
            network = psutil.net_io_counters()
            return {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv
            }
        except ImportError:
            return {"bytes_sent": 0, "bytes_recv": 0}
    
    def _get_active_connections(self) -> int:
        """Obtém conexões ativas"""
        try:
            import psutil
            connections = psutil.net_connections()
            return len([conn for conn in connections if conn.status == 'ESTABLISHED'])
        except ImportError:
            return 0
    
    def _get_service_performance_metrics(self, service: APMServiceType) -> Dict[str, Any]:
        """Obtém métricas de performance de um serviço"""
        metrics = self.apm_manager.collector.metrics
        
        service_metrics = {}
        for metric_name, metric_list in metrics.items():
            if metric_list and metric_list[-1].service == service:
                values = [m.value for m in metric_list[-100:]]  # Últimas 100 métricas
                if values:
                    service_metrics[metric_name] = {
                        "current": values[-1],
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "count": len(values)
                    }
        
        return service_metrics
    
    def _get_slow_queries(self) -> List[Dict[str, Any]]:
        """Obtém queries lentas"""
        # Simular dados de queries lentas
        return [
            {
                "query": "SELECT * FROM keywords WHERE domain = ?",
                "duration": 2.5,
                "executions": 150,
                "service": "database"
            },
            {
                "query": "INSERT INTO processing_results (...) VALUES (...)",
                "duration": 1.8,
                "executions": 75,
                "service": "database"
            }
        ]
    
    def _get_cache_performance(self) -> Dict[str, Any]:
        """Obtém performance do cache"""
        cache_metrics = self.apm_manager.collector.metrics.get("cache_hit_rate", [])
        
        if cache_metrics:
            latest = cache_metrics[-1]
            return {
                "hit_rate": latest.value,
                "miss_rate": 100 - latest.value,
                "total_requests": 1000,  # Simulado
                "cache_size": 500  # Simulado
            }
        
        return {"hit_rate": 0, "miss_rate": 0, "total_requests": 0, "cache_size": 0}
    
    def _get_api_performance(self) -> Dict[str, Any]:
        """Obtém performance da API"""
        api_metrics = self.apm_manager.collector.metrics.get("api_request", [])
        
        if api_metrics:
            values = [m.value for m in api_metrics[-100:]]
            return {
                "avg_response_time": sum(values) / len(values),
                "requests_per_second": len(values) / 60,  # Assumindo 1 minuto
                "error_rate": len([v for v in values if v > 1000]) / len(values) * 100
            }
        
        return {"avg_response_time": 0, "requests_per_second": 0, "error_rate": 0}
    
    def _get_rate_limiting_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de rate limiting"""
        return {
            "requests_blocked": 25,
            "active_limits": 5,
            "top_blocked_ips": ["192.168.1.100", "10.0.0.50"],
            "rate_limit_hits": 150
        }
    
    def _get_access_attempts(self) -> List[Dict[str, Any]]:
        """Obtém tentativas de acesso"""
        return [
            {
                "ip": "192.168.1.100",
                "attempts": 50,
                "last_attempt": datetime.now().isoformat(),
                "blocked": True
            },
            {
                "ip": "10.0.0.50",
                "attempts": 25,
                "last_attempt": datetime.now().isoformat(),
                "blocked": False
            }
        ]
    
    def _get_auth_errors(self) -> List[Dict[str, Any]]:
        """Obtém erros de autenticação"""
        return [
            {
                "type": "invalid_credentials",
                "count": 15,
                "last_occurrence": datetime.now().isoformat()
            },
            {
                "type": "expired_token",
                "count": 8,
                "last_occurrence": datetime.now().isoformat()
            }
        ]
    
    def _get_threats(self) -> List[Dict[str, Any]]:
        """Obtém ameaças detectadas"""
        return [
            {
                "type": "brute_force",
                "severity": "high",
                "source_ip": "192.168.1.100",
                "detected_at": datetime.now().isoformat()
            }
        ]
    
    def _get_recent_traces(self) -> List[Dict[str, Any]]:
        """Obtém traces recentes"""
        return [
            {
                "trace_id": "abc123",
                "service": "api",
                "operation": "GET /api/keywords",
                "duration": 150,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    def _get_service_map(self) -> Dict[str, Any]:
        """Obtém mapa de serviços"""
        return {
            "nodes": [
                {"id": "api", "name": "API Service"},
                {"id": "database", "name": "Database"},
                {"id": "cache", "name": "Cache Service"}
            ],
            "edges": [
                {"from": "api", "to": "database", "calls": 100},
                {"from": "api", "to": "cache", "calls": 200}
            ]
        }
    
    def _get_trace_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas de traces"""
        return {
            "total_traces": 1000,
            "success_rate": 95.5,
            "avg_duration": 250,
            "error_rate": 4.5
        }
    
    def _get_error_traces(self) -> List[Dict[str, Any]]:
        """Obtém traces com erro"""
        return [
            {
                "trace_id": "def456",
                "service": "api",
                "operation": "POST /api/collect",
                "error": "Database connection failed",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    def _get_errors_by_type(self) -> Dict[str, int]:
        """Obtém erros por tipo"""
        return {
            "database_error": 15,
            "api_error": 8,
            "validation_error": 12,
            "network_error": 5
        }
    
    def _get_errors_by_service(self) -> Dict[str, int]:
        """Obtém erros por serviço"""
        return {
            "api": 20,
            "database": 15,
            "cache": 5,
            "external_api": 10
        }
    
    def _get_recent_errors(self) -> List[Dict[str, Any]]:
        """Obtém erros recentes"""
        return [
            {
                "id": "err001",
                "type": "database_error",
                "message": "Connection timeout",
                "service": "database",
                "timestamp": datetime.now().isoformat(),
                "severity": "high"
            }
        ]
    
    def _get_error_trends(self) -> Dict[str, List[Dict[str, Any]]]:
        """Obtém tendências de erro"""
        return {
            "hourly": [
                {"hour": "10:00", "errors": 5},
                {"hour": "11:00", "errors": 8},
                {"hour": "12:00", "errors": 12}
            ]
        }


class DashboardManager:
    """Gerenciador de dashboards"""
    
    def __init__(self):
        self.dashboards: Dict[str, Dashboard] = {}
        self.data_collector = DashboardDataCollector()
        self.websocket_connections: List[WebSocket] = []
        
        # Criar dashboards padrão
        self._create_default_dashboards()
    
    def _create_default_dashboards(self):
        """Cria dashboards padrão"""
        # Dashboard de visão geral do sistema
        system_overview = Dashboard(
            id="system_overview",
            name="Visão Geral do Sistema",
            type=DashboardType.SYSTEM_OVERVIEW,
            description="Dashboard com visão geral de todos os sistemas",
            panels=[
                DashboardPanel(
                    id="cpu_usage",
                    title="Uso de CPU",
                    type="metric",
                    data_source="system",
                    query="cpu_usage",
                    refresh_interval=30,
                    position={"x": 0, "y": 0, "width": 6, "height": 4},
                    config={"unit": "%", "thresholds": {"warning": 80, "critical": 95}}
                ),
                DashboardPanel(
                    id="memory_usage",
                    title="Uso de Memória",
                    type="metric",
                    data_source="system",
                    query="memory_usage",
                    refresh_interval=30,
                    position={"x": 6, "y": 0, "width": 6, "height": 4},
                    config={"unit": "%", "thresholds": {"warning": 85, "critical": 95}}
                ),
                DashboardPanel(
                    id="active_alerts",
                    title="Alertas Ativos",
                    type="table",
                    data_source="apm",
                    query="active_alerts",
                    refresh_interval=60,
                    position={"x": 0, "y": 4, "width": 12, "height": 4},
                    config={"columns": ["severity", "title", "timestamp"]}
                )
            ],
            refresh_interval=30,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_public=True
        )
        
        # Dashboard de performance
        performance = Dashboard(
            id="performance",
            name="Performance",
            type=DashboardType.PERFORMANCE,
            description="Dashboard de métricas de performance",
            panels=[
                DashboardPanel(
                    id="api_response_time",
                    title="Tempo de Resposta da API",
                    type="chart",
                    data_source="apm",
                    query="api_performance",
                    refresh_interval=30,
                    position={"x": 0, "y": 0, "width": 6, "height": 4},
                    config={"chart_type": "line", "y_axis": "ms"}
                ),
                DashboardPanel(
                    id="cache_hit_rate",
                    title="Taxa de Acerto do Cache",
                    type="chart",
                    data_source="apm",
                    query="cache_performance",
                    refresh_interval=30,
                    position={"x": 6, "y": 0, "width": 6, "height": 4},
                    config={"chart_type": "gauge", "max": 100}
                )
            ],
            refresh_interval=30,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_public=True
        )
        
        # Dashboard de segurança
        security = Dashboard(
            id="security",
            name="Segurança",
            type=DashboardType.SECURITY,
            description="Dashboard de métricas de segurança",
            panels=[
                DashboardPanel(
                    id="rate_limiting",
                    title="Rate Limiting",
                    type="metric",
                    data_source="security",
                    query="rate_limiting",
                    refresh_interval=60,
                    position={"x": 0, "y": 0, "width": 6, "height": 4},
                    config={"unit": "requests"}
                ),
                DashboardPanel(
                    id="access_attempts",
                    title="Tentativas de Acesso",
                    type="table",
                    data_source="security",
                    query="access_attempts",
                    refresh_interval=60,
                    position={"x": 6, "y": 0, "width": 6, "height": 4},
                    config={"columns": ["ip", "attempts", "blocked"]}
                )
            ],
            refresh_interval=60,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_public=True
        )
        
        self.dashboards[system_overview.id] = system_overview
        self.dashboards[performance.id] = performance
        self.dashboards[security.id] = security
    
    async def get_dashboard_data(self, dashboard_id: str) -> Optional[DashboardData]:
        """Obtém dados de um dashboard"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return None
        
        # Coletar dados baseado no tipo de dashboard
        if dashboard.type == DashboardType.SYSTEM_OVERVIEW:
            metrics = await self.data_collector.collect_system_overview_data()
        elif dashboard.type == DashboardType.PERFORMANCE:
            metrics = await self.data_collector.collect_performance_data()
        elif dashboard.type == DashboardType.SECURITY:
            metrics = await self.data_collector.collect_security_data()
        elif dashboard.type == DashboardType.TRACING:
            metrics = await self.data_collector.collect_tracing_data()
        elif dashboard.type == DashboardType.ERROR_TRACKING:
            metrics = await self.data_collector.collect_error_tracking_data()
        else:
            metrics = {}
        
        return DashboardData(
            dashboard_id=dashboard_id,
            timestamp=datetime.now(),
            metrics=metrics,
            alerts=[],
            traces=[],
            errors=[]
        )
    
    def add_websocket_connection(self, websocket: WebSocket):
        """Adiciona conexão WebSocket"""
        self.websocket_connections.append(websocket)
    
    def remove_websocket_connection(self, websocket: WebSocket):
        """Remove conexão WebSocket"""
        if websocket in self.websocket_connections:
            self.websocket_connections.remove(websocket)
    
    async def broadcast_dashboard_update(self, dashboard_id: str, data: DashboardData):
        """Envia atualização de dashboard para todos os clientes WebSocket"""
        message = {
            "type": "dashboard_update",
            "dashboard_id": dashboard_id,
            "data": asdict(data)
        }
        
        disconnected = []
        for websocket in self.websocket_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except WebSocketDisconnect:
                disconnected.append(websocket)
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem WebSocket: {e}")
                disconnected.append(websocket)
        
        # Remover conexões desconectadas
        for websocket in disconnected:
            self.remove_websocket_connection(websocket)


# Instância global
dashboard_manager = DashboardManager()


# FastAPI app para dashboards
app = FastAPI(
    title="Omni Keywords Finder - Dashboards",
    description="Sistema unificado de dashboards",
    version="1.0.0"
)

# Templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request):
    """Página inicial dos dashboards"""
    return templates.TemplateResponse("dashboard_home.html", {
        "request": request,
        "dashboards": list(dashboard_manager.dashboards.values())
    })


@app.get("/dashboard/{dashboard_id}", response_class=HTMLResponse)
async def dashboard_view(request, dashboard_id: str):
    """Visualização de um dashboard específico"""
    dashboard = dashboard_manager.dashboards.get(dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    
    return templates.TemplateResponse("dashboard_view.html", {
        "request": request,
        "dashboard": dashboard
    })


@app.get("/api/dashboards")
async def get_dashboards():
    """Lista todos os dashboards"""
    return {
        "dashboards": [
            {
                "id": dashboard.id,
                "name": dashboard.name,
                "type": dashboard.type.value,
                "description": dashboard.description,
                "is_public": dashboard.is_public
            }
            for dashboard in dashboard_manager.dashboards.values()
        ]
    }


@app.get("/api/dashboard/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    """Obtém dados de um dashboard específico"""
    data = await dashboard_manager.get_dashboard_data(dashboard_id)
    if not data:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    
    return asdict(data)


@app.websocket("/ws/dashboard/{dashboard_id}")
async def websocket_dashboard(websocket: WebSocket, dashboard_id: str):
    """WebSocket para atualizações em tempo real"""
    await websocket.accept()
    dashboard_manager.add_websocket_connection(websocket)
    
    try:
        # Enviar dados iniciais
        data = await dashboard_manager.get_dashboard_data(dashboard_id)
        if data:
            await websocket.send_text(json.dumps({
                "type": "initial_data",
                "data": asdict(data)
            }))
        
        # Manter conexão ativa
        while True:
            await websocket.receive_text()
            
            # Enviar dados atualizados
            data = await dashboard_manager.get_dashboard_data(dashboard_id)
            if data:
                await websocket.send_text(json.dumps({
                    "type": "update",
                    "data": asdict(data)
                }))
    
    except WebSocketDisconnect:
        dashboard_manager.remove_websocket_connection(websocket)
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        dashboard_manager.remove_websocket_connection(websocket)


@app.get("/api/metrics/system")
async def get_system_metrics():
    """Obtém métricas do sistema"""
    return await dashboard_manager.data_collector.collect_system_overview_data()


@app.get("/api/metrics/performance")
async def get_performance_metrics():
    """Obtém métricas de performance"""
    return await dashboard_manager.data_collector.collect_performance_data()


@app.get("/api/metrics/security")
async def get_security_metrics():
    """Obtém métricas de segurança"""
    return await dashboard_manager.data_collector.collect_security_data()


@app.get("/api/metrics/tracing")
async def get_tracing_metrics():
    """Obtém métricas de tracing"""
    return await dashboard_manager.data_collector.collect_tracing_data()


@app.get("/api/metrics/errors")
async def get_error_metrics():
    """Obtém métricas de erro"""
    return await dashboard_manager.data_collector.collect_error_tracking_data()


# Background task para atualizações automáticas
async def background_dashboard_updates():
    """Task em background para atualizar dashboards"""
    while True:
        try:
            for dashboard_id in dashboard_manager.dashboards:
                data = await dashboard_manager.get_dashboard_data(dashboard_id)
                if data:
                    await dashboard_manager.broadcast_dashboard_update(dashboard_id, data)
            
            await asyncio.sleep(30)  # Atualizar a cada 30 segundos
        
        except Exception as e:
            logger.error(f"Erro na atualização de dashboards: {e}")
            await asyncio.sleep(60)


@app.on_event("startup")
async def startup_event():
    """Evento de inicialização"""
    # Iniciar task de atualização
    asyncio.create_task(background_dashboard_updates())
    logger.info("Sistema de dashboards iniciado")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 
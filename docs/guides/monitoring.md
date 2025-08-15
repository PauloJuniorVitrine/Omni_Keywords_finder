# Guia de Monitoramento

Este documento detalha as estratégias de otimização de monitoramento do Omni Keywords Finder.

## Logs

### 1. Aplicação

```python
# src/monitoring/logs.py
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import json
import os

class LogHandler:
    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
        log_dir: str = "logs"
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Arquivo
        file_handler = logging.FileHandler(
            f"{log_dir}/{name}.log"
        )
        file_handler.setLevel(level)
        
        # Console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # Formato
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def info(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Log de informação"""
        self._log(logging.INFO, message, extra)
        
    def error(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Log de erro"""
        self._log(logging.ERROR, message, extra)
        
    def warning(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Log de aviso"""
        self._log(logging.WARNING, message, extra)
        
    def debug(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Log de debug"""
        self._log(logging.DEBUG, message, extra)
        
    def _log(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Registra log"""
        if extra:
            message = f"{message} - {json.dumps(extra)}"
        self.logger.log(level, message)
```

### 2. Sistema

```python
# src/monitoring/system.py
from typing import Dict, Any, Optional
from datetime import datetime
import psutil
import os
import json

class SystemMonitor:
    def __init__(self, log_handler: LogHandler):
        self.log_handler = log_handler
        
    def log_system_info(self):
        """Registra informações do sistema"""
        info = {
            "cpu": {
                "percent": psutil.cpu_percent(),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict()
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage("/").total,
                "free": psutil.disk_usage("/").free,
                "percent": psutil.disk_usage("/").percent
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            }
        }
        
        self.log_handler.info(
            "System info",
            extra=info
        )
        
    def check_resources(self) -> bool:
        """Verifica recursos"""
        # CPU
        if psutil.cpu_percent() > 90:
            self.log_handler.warning(
                "High CPU usage",
                extra={"percent": psutil.cpu_percent()}
            )
            return False
            
        # Memória
        if psutil.virtual_memory().percent > 90:
            self.log_handler.warning(
                "High memory usage",
                extra={"percent": psutil.virtual_memory().percent}
            )
            return False
            
        # Disco
        if psutil.disk_usage("/").percent > 90:
            self.log_handler.warning(
                "High disk usage",
                extra={"percent": psutil.disk_usage("/").percent}
            )
            return False
            
        return True
```

## Métricas

### 1. Performance

```python
# src/monitoring/metrics.py
from typing import Dict, Any, Optional
from datetime import datetime
import time
from prometheus_client import Counter, Histogram, Gauge
from src.monitoring.logs import LogHandler

class MetricsHandler:
    def __init__(self, log_handler: LogHandler):
        self.log_handler = log_handler
        
        # Contadores
        self.request_count = Counter(
            "request_count",
            "Total de requisições",
            ["method", "endpoint", "status"]
        )
        
        self.error_count = Counter(
            "error_count",
            "Total de erros",
            ["type", "endpoint"]
        )
        
        # Histogramas
        self.request_duration = Histogram(
            "request_duration_seconds",
            "Duração das requisições",
            ["method", "endpoint"]
        )
        
        self.processing_duration = Histogram(
            "processing_duration_seconds",
            "Duração do processamento",
            ["operation"]
        )
        
        # Gauges
        self.active_users = Gauge(
            "active_users",
            "Usuários ativos"
        )
        
        self.queue_size = Gauge(
            "queue_size",
            "Tamanho da fila"
        )
        
    def track_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        duration: float
    ):
        """Registra requisição"""
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        self.request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
    def track_error(
        self,
        error_type: str,
        endpoint: str
    ):
        """Registra erro"""
        self.error_count.labels(
            type=error_type,
            endpoint=endpoint
        ).inc()
        
    def track_processing(
        self,
        operation: str,
        duration: float
    ):
        """Registra processamento"""
        self.processing_duration.labels(
            operation=operation
        ).observe(duration)
        
    def update_active_users(self, count: int):
        """Atualiza usuários ativos"""
        self.active_users.set(count)
        
    def update_queue_size(self, size: int):
        """Atualiza tamanho da fila"""
        self.queue_size.set(size)
```

### 2. Negócio

```python
# src/monitoring/business.py
from typing import Dict, Any, Optional
from datetime import datetime
from prometheus_client import Counter, Gauge
from src.monitoring.logs import LogHandler

class BusinessMetrics:
    def __init__(self, log_handler: LogHandler):
        self.log_handler = log_handler
        
        # Contadores
        self.keyword_count = Counter(
            "keyword_count",
            "Total de keywords",
            ["language", "status"]
        )
        
        self.user_count = Counter(
            "user_count",
            "Total de usuários",
            ["plan", "status"]
        )
        
        self.model_count = Counter(
            "model_count",
            "Total de modelos",
            ["type", "version"]
        )
        
        # Gauges
        self.daily_keywords = Gauge(
            "daily_keywords",
            "Keywords por dia"
        )
        
        self.daily_users = Gauge(
            "daily_users",
            "Usuários por dia"
        )
        
        self.daily_models = Gauge(
            "daily_models",
            "Modelos por dia"
        )
        
    def track_keyword(
        self,
        language: str,
        status: str
    ):
        """Registra keyword"""
        self.keyword_count.labels(
            language=language,
            status=status
        ).inc()
        
    def track_user(
        self,
        plan: str,
        status: str
    ):
        """Registra usuário"""
        self.user_count.labels(
            plan=plan,
            status=status
        ).inc()
        
    def track_model(
        self,
        type: str,
        version: str
    ):
        """Registra modelo"""
        self.model_count.labels(
            type=type,
            version=version
        ).inc()
        
    def update_daily_metrics(
        self,
        keywords: int,
        users: int,
        models: int
    ):
        """Atualiza métricas diárias"""
        self.daily_keywords.set(keywords)
        self.daily_users.set(users)
        self.daily_models.set(models)
```

## Alertas

### 1. Sistema

```python
# src/monitoring/alerts.py
from typing import Dict, Any, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from src.monitoring.logs import LogHandler

class AlertHandler:
    def __init__(
        self,
        log_handler: LogHandler,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        alert_email: str
    ):
        self.log_handler = log_handler
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.alert_email = alert_email
        
    def send_alert(
        self,
        subject: str,
        message: str,
        level: str = "warning"
    ):
        """Envia alerta"""
        try:
            msg = MIMEText(message)
            msg["Subject"] = f"[{level.upper()}] {subject}"
            msg["From"] = self.smtp_user
            msg["To"] = self.alert_email
            
            with smtplib.SMTP(
                self.smtp_host,
                self.smtp_port
            ) as server:
                server.starttls()
                server.login(
                    self.smtp_user,
                    self.smtp_password
                )
                server.send_message(msg)
                
            self.log_handler.info(
                "Alert sent",
                extra={
                    "subject": subject,
                    "level": level
                }
            )
            
        except Exception as e:
            self.log_handler.error(
                "Failed to send alert",
                extra={"error": str(e)}
            )
            
    def check_thresholds(
        self,
        metrics: Dict[str, Any]
    ):
        """Verifica thresholds"""
        # CPU
        if metrics["cpu"]["percent"] > 90:
            self.send_alert(
                "High CPU Usage",
                f"CPU usage is {metrics['cpu']['percent']}%",
                "critical"
            )
            
        # Memória
        if metrics["memory"]["percent"] > 90:
            self.send_alert(
                "High Memory Usage",
                f"Memory usage is {metrics['memory']['percent']}%",
                "critical"
            )
            
        # Disco
        if metrics["disk"]["percent"] > 90:
            self.send_alert(
                "High Disk Usage",
                f"Disk usage is {metrics['disk']['percent']}%",
                "critical"
            )
```

### 2. Negócio

```python
# src/monitoring/business_alerts.py
from typing import Dict, Any, Optional
from datetime import datetime
from src.monitoring.alerts import AlertHandler
from src.monitoring.logs import LogHandler

class BusinessAlertHandler:
    def __init__(
        self,
        log_handler: LogHandler,
        alert_handler: AlertHandler
    ):
        self.log_handler = log_handler
        self.alert_handler = alert_handler
        
    def check_business_metrics(
        self,
        metrics: Dict[str, Any]
    ):
        """Verifica métricas de negócio"""
        # Keywords
        if metrics["daily_keywords"] < 100:
            self.alert_handler.send_alert(
                "Low Keyword Generation",
                f"Only {metrics['daily_keywords']} keywords generated today",
                "warning"
            )
            
        # Usuários
        if metrics["daily_users"] < 10:
            self.alert_handler.send_alert(
                "Low User Registration",
                f"Only {metrics['daily_users']} users registered today",
                "warning"
            )
            
        # Modelos
        if metrics["daily_models"] < 5:
            self.alert_handler.send_alert(
                "Low Model Usage",
                f"Only {metrics['daily_models']} models used today",
                "warning"
            )
            
    def check_error_rates(
        self,
        metrics: Dict[str, Any]
    ):
        """Verifica taxas de erro"""
        # Requisições
        error_rate = (
            metrics["error_count"] / metrics["request_count"]
            if metrics["request_count"] > 0
            else 0
        )
        
        if error_rate > 0.1:  # 10%
            self.alert_handler.send_alert(
                "High Error Rate",
                f"Error rate is {error_rate:.2%}",
                "critical"
            )
            
        # Processamento
        if metrics["processing_errors"] > 100:
            self.alert_handler.send_alert(
                "High Processing Errors",
                f"{metrics['processing_errors']} processing errors today",
                "critical"
            )
```

## Observações

- Registrar logs
- Coletar métricas
- Monitorar sistema
- Alertar problemas
- Analisar dados
- Otimizar recursos
- Manter histórico
- Documentar mudanças
- Revisar thresholds
- Atualizar dashboards 
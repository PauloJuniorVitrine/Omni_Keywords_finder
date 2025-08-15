"""
Chaos Engineering Configuration Manager
======================================

Sistema de configuração para chaos engineering com:
- Gerenciamento centralizado de configurações
- Validação de parâmetros
- Hot-reload de configurações
- Configurações por ambiente
- Templates de experimentos

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: CHAOS_CONFIG_001_20250127
"""

import json
import logging
import os
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import yaml
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Ambientes de execução"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ConfigScope(Enum):
    """Escopo das configurações"""
    GLOBAL = "global"
    EXPERIMENT = "experiment"
    MONITORING = "monitoring"
    ALERTING = "alerting"
    ROLLBACK = "rollback"


@dataclass
class ChaosConfig:
    """Configuração principal do chaos engineering"""
    environment: Environment
    enabled: bool = True
    max_concurrent_experiments: int = 3
    default_timeout: int = 300
    auto_rollback: bool = True
    rollback_threshold: float = 0.5
    metrics_interval: int = 5
    log_level: str = "INFO"
    
    # Configurações de segurança
    safety_checks: bool = True
    max_impact_threshold: float = 0.3
    blackout_hours: List[int] = None  # Horários proibidos (0-23)
    allowed_days: List[int] = None    # Dias permitidos (0-6, 0=Segunda)
    
    # Configurações de notificação
    notify_on_start: bool = True
    notify_on_completion: bool = True
    notify_on_failure: bool = True
    notify_on_rollback: bool = True
    
    # Configurações de persistência
    save_results: bool = True
    results_retention_days: int = 30
    export_format: str = "json"  # json, yaml, csv
    
    def __post_init__(self):
        if self.blackout_hours is None:
            self.blackout_hours = [0, 1, 2, 3, 4, 5, 6, 22, 23]  # Horário comercial
        if self.allowed_days is None:
            self.allowed_days = [1, 2, 3, 4, 5]  # Segunda a Sexta


class ExperimentTemplate(BaseModel):
    """Template para experimentos"""
    name: str = Field(..., description="Nome do template")
    description: str = Field(..., description="Descrição do template")
    type: str = Field(..., description="Tipo do experimento")
    category: str = Field(..., description="Categoria do experimento")
    
    # Parâmetros padrão
    duration: int = Field(300, description="Duração padrão em segundos")
    steady_state_duration: int = Field(60, description="Duração do estado estável")
    chaos_duration: int = Field(120, description="Duração da injeção de caos")
    observation_duration: int = Field(60, description="Duração da observação")
    
    # Configurações de segurança
    max_impact: float = Field(0.3, description="Impacto máximo permitido")
    auto_rollback: bool = Field(True, description="Rollback automático")
    rollback_threshold: float = Field(0.5, description="Threshold para rollback")
    
    # Parâmetros específicos
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Configurações de monitoramento
    metrics_interval: int = Field(5, description="Intervalo de coleta de métricas")
    alert_thresholds: Dict[str, float] = Field(default_factory=dict)
    
    # Configurações de validação
    prerequisites: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    
    @validator('max_impact')
    def validate_max_impact(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('max_impact must be between 0 and 1')
        return v
    
    @validator('rollback_threshold')
    def validate_rollback_threshold(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('rollback_threshold must be between 0 and 1')
        return v


class MonitoringConfig(BaseModel):
    """Configuração de monitoramento"""
    enabled: bool = Field(True, description="Monitoramento habilitado")
    metrics_interval: int = Field(5, description="Intervalo de coleta em segundos")
    retention_period: int = Field(3600, description="Período de retenção em segundos")
    
    # Métricas a coletar
    collect_cpu: bool = Field(True, description="Coletar métricas de CPU")
    collect_memory: bool = Field(True, description="Coletar métricas de memória")
    collect_disk: bool = Field(True, description="Coletar métricas de disco")
    collect_network: bool = Field(True, description="Coletar métricas de rede")
    collect_application: bool = Field(True, description="Coletar métricas da aplicação")
    
    # Thresholds de alerta
    cpu_threshold: float = Field(0.8, description="Threshold de CPU (0-1)")
    memory_threshold: float = Field(0.8, description="Threshold de memória (0-1)")
    disk_threshold: float = Field(0.9, description="Threshold de disco (0-1)")
    error_rate_threshold: float = Field(0.05, description="Threshold de taxa de erro")
    response_time_threshold: float = Field(2.0, description="Threshold de tempo de resposta (s)")
    
    # Configurações de exportação
    export_to_prometheus: bool = Field(True, description="Exportar para Prometheus")
    export_to_grafana: bool = Field(True, description="Exportar para Grafana")
    export_to_logs: bool = Field(True, description="Exportar para logs")


class AlertingConfig(BaseModel):
    """Configuração de alertas"""
    enabled: bool = Field(True, description="Alertas habilitados")
    
    # Canais de notificação
    email_enabled: bool = Field(False, description="Alertas por email")
    slack_enabled: bool = Field(True, description="Alertas por Slack")
    webhook_enabled: bool = Field(False, description="Alertas por webhook")
    console_enabled: bool = Field(True, description="Alertas no console")
    
    # Configurações de email
    email_recipients: List[str] = Field(default_factory=list)
    email_smtp_server: str = Field("", description="Servidor SMTP")
    email_smtp_port: int = Field(587, description="Porta SMTP")
    email_username: str = Field("", description="Usuário SMTP")
    email_password: str = Field("", description="Senha SMTP")
    
    # Configurações de Slack
    slack_webhook_url: str = Field("", description="URL do webhook do Slack")
    slack_channel: str = Field("#chaos-engineering", description="Canal do Slack")
    slack_username: str = Field("Chaos Bot", description="Nome do bot no Slack")
    
    # Configurações de webhook
    webhook_url: str = Field("", description="URL do webhook")
    webhook_headers: Dict[str, str] = Field(default_factory=dict)
    
    # Configurações de agrupamento
    group_alerts: bool = Field(True, description="Agrupar alertas similares")
    alert_cooldown: int = Field(300, description="Cooldown entre alertas (s)")
    max_alerts_per_hour: int = Field(10, description="Máximo de alertas por hora")


class RollbackConfig(BaseModel):
    """Configuração de rollback"""
    enabled: bool = Field(True, description="Rollback habilitado")
    auto_rollback: bool = Field(True, description="Rollback automático")
    
    # Thresholds de rollback
    error_rate_threshold: float = Field(0.5, description="Threshold de taxa de erro")
    availability_threshold: float = Field(0.5, description="Threshold de disponibilidade")
    response_time_threshold: float = Field(5.0, description="Threshold de tempo de resposta")
    
    # Configurações de tempo
    rollback_delay: int = Field(30, description="Delay antes do rollback (s)")
    max_rollback_time: int = Field(300, description="Tempo máximo para rollback (s)")
    
    # Estratégias de rollback
    strategies: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Notificações de rollback
    notify_on_rollback: bool = Field(True, description="Notificar sobre rollbacks")
    notify_on_rollback_failure: bool = Field(True, description="Notificar falhas de rollback")


class ConfigManager:
    """
    Gerenciador de configurações do chaos engineering
    """
    
    def __init__(self, config_dir: str = "config/chaos"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Arquivos de configuração
        self.chaos_config_file = self.config_dir / "chaos_config.yaml"
        self.templates_file = self.config_dir / "templates.yaml"
        self.monitoring_config_file = self.config_dir / "monitoring.yaml"
        self.alerting_config_file = self.config_dir / "alerting.yaml"
        self.rollback_config_file = self.config_dir / "rollback.yaml"
        
        # Configurações carregadas
        self.chaos_config: Optional[ChaosConfig] = None
        self.templates: Dict[str, ExperimentTemplate] = {}
        self.monitoring_config: Optional[MonitoringConfig] = None
        self.alerting_config: Optional[AlertingConfig] = None
        self.rollback_config: Optional[RollbackConfig] = None
        
        # Controle de thread safety
        self.lock = threading.RLock()
        self.watchers: List[Callable] = []
        self.last_modified = 0.0
        
        # Observer para hot-reload
        self.observer = Observer()
        self.file_handler = ConfigFileHandler(self)
        
        # Carregar configurações iniciais
        self._load_all_configs()
        self._setup_file_watcher()
        
        logger.info("ChaosConfigManager initialized")
    
    def _load_all_configs(self) -> None:
        """Carrega todas as configurações"""
        try:
            self._load_chaos_config()
            self._load_templates()
            self._load_monitoring_config()
            self._load_alerting_config()
            self._load_rollback_config()
            logger.info("All configurations loaded successfully")
        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
    
    def _load_chaos_config(self) -> None:
        """Carrega configuração principal"""
        if self.chaos_config_file.exists():
            with open(self.chaos_config_file, 'r') as f:
                data = yaml.safe_load(f)
                self.chaos_config = ChaosConfig(**data)
        else:
            # Configuração padrão
            self.chaos_config = ChaosConfig(
                environment=Environment.DEVELOPMENT
            )
            self._save_chaos_config()
    
    def _load_templates(self) -> None:
        """Carrega templates de experimentos"""
        if self.templates_file.exists():
            with open(self.templates_file, 'r') as f:
                data = yaml.safe_load(f)
                
            for template_data in data.get('templates', []):
                template = ExperimentTemplate(**template_data)
                self.templates[template.name] = template
        else:
            # Templates padrão
            self._create_default_templates()
            self._save_templates()
    
    def _load_monitoring_config(self) -> None:
        """Carrega configuração de monitoramento"""
        if self.monitoring_config_file.exists():
            with open(self.monitoring_config_file, 'r') as f:
                data = yaml.safe_load(f)
                self.monitoring_config = MonitoringConfig(**data)
        else:
            self.monitoring_config = MonitoringConfig()
            self._save_monitoring_config()
    
    def _load_alerting_config(self) -> None:
        """Carrega configuração de alertas"""
        if self.alerting_config_file.exists():
            with open(self.alerting_config_file, 'r') as f:
                data = yaml.safe_load(f)
                self.alerting_config = AlertingConfig(**data)
        else:
            self.alerting_config = AlertingConfig()
            self._save_alerting_config()
    
    def _load_rollback_config(self) -> None:
        """Carrega configuração de rollback"""
        if self.rollback_config_file.exists():
            with open(self.rollback_config_file, 'r') as f:
                data = yaml.safe_load(f)
                self.rollback_config = RollbackConfig(**data)
        else:
            self.rollback_config = RollbackConfig()
            self._save_rollback_config()
    
    def _create_default_templates(self) -> None:
        """Cria templates padrão"""
        default_templates = [
            {
                "name": "network_latency_basic",
                "description": "Teste básico de latência de rede",
                "type": "network_latency",
                "category": "network",
                "duration": 300,
                "parameters": {"latency_ms": 100, "jitter_ms": 10}
            },
            {
                "name": "cpu_stress_basic",
                "description": "Teste básico de stress de CPU",
                "type": "cpu_stress",
                "category": "resource",
                "duration": 180,
                "parameters": {"cpu_load": 0.7, "cores": 2}
            },
            {
                "name": "service_failure_basic",
                "description": "Teste básico de falha de serviço",
                "type": "service_failure",
                "category": "service",
                "duration": 120,
                "parameters": {"service_name": "api", "failure_rate": 0.3}
            },
            {
                "name": "database_failure_basic",
                "description": "Teste básico de falha de banco de dados",
                "type": "database_failure",
                "category": "database",
                "duration": 150,
                "parameters": {"connection_timeout": 5, "query_timeout": 10}
            }
        ]
        
        for template_data in default_templates:
            template = ExperimentTemplate(**template_data)
            self.templates[template.name] = template
    
    def _save_chaos_config(self) -> None:
        """Salva configuração principal"""
        with open(self.chaos_config_file, 'w') as f:
            yaml.dump(asdict(self.chaos_config), f, default_flow_style=False)
    
    def _save_templates(self) -> None:
        """Salva templates"""
        data = {"templates": [template.dict() for template in self.templates.values()]}
        with open(self.templates_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def _save_monitoring_config(self) -> None:
        """Salva configuração de monitoramento"""
        with open(self.monitoring_config_file, 'w') as f:
            yaml.dump(self.monitoring_config.dict(), f, default_flow_style=False)
    
    def _save_alerting_config(self) -> None:
        """Salva configuração de alertas"""
        with open(self.alerting_config_file, 'w') as f:
            yaml.dump(self.alerting_config.dict(), f, default_flow_style=False)
    
    def _save_rollback_config(self) -> None:
        """Salva configuração de rollback"""
        with open(self.rollback_config_file, 'w') as f:
            yaml.dump(self.rollback_config.dict(), f, default_flow_style=False)
    
    def _setup_file_watcher(self) -> None:
        """Configura observador de arquivos para hot-reload"""
        try:
            self.observer.schedule(self.file_handler, str(self.config_dir), recursive=False)
            self.observer.start()
            logger.info("File watcher started for hot-reload")
        except Exception as e:
            logger.error(f"Error setting up file watcher: {e}")
    
    def add_watcher(self, callback: Callable) -> None:
        """Adiciona callback para mudanças de configuração"""
        self.watchers.append(callback)
    
    def _notify_watchers(self, config_type: str) -> None:
        """Notifica watchers sobre mudanças"""
        for callback in self.watchers:
            try:
                callback(config_type)
            except Exception as e:
                logger.error(f"Error in config watcher callback: {e}")
    
    def reload_config(self, config_type: Optional[str] = None) -> None:
        """Recarrega configurações"""
        with self.lock:
            if config_type is None or config_type == "chaos":
                self._load_chaos_config()
            if config_type is None or config_type == "templates":
                self._load_templates()
            if config_type is None or config_type == "monitoring":
                self._load_monitoring_config()
            if config_type is None or config_type == "alerting":
                self._load_alerting_config()
            if config_type is None or config_type == "rollback":
                self._load_rollback_config()
            
            self._notify_watchers(config_type or "all")
            logger.info(f"Configuration reloaded: {config_type or 'all'}")
    
    def get_chaos_config(self) -> ChaosConfig:
        """Obtém configuração principal"""
        with self.lock:
            return self.chaos_config
    
    def get_template(self, template_name: str) -> Optional[ExperimentTemplate]:
        """Obtém template por nome"""
        with self.lock:
            return self.templates.get(template_name)
    
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista templates disponíveis"""
        with self.lock:
            templates = []
            for template in self.templates.values():
                if category is None or template.category == category:
                    templates.append({
                        'name': template.name,
                        'description': template.description,
                        'type': template.type,
                        'category': template.category,
                        'duration': template.duration
                    })
            return templates
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Obtém configuração de monitoramento"""
        with self.lock:
            return self.monitoring_config
    
    def get_alerting_config(self) -> AlertingConfig:
        """Obtém configuração de alertas"""
        with self.lock:
            return self.alerting_config
    
    def get_rollback_config(self) -> RollbackConfig:
        """Obtém configuração de rollback"""
        with self.lock:
            return self.rollback_config
    
    def update_chaos_config(self, **kwargs) -> None:
        """Atualiza configuração principal"""
        with self.lock:
            for key, value in kwargs.items():
                if hasattr(self.chaos_config, key):
                    setattr(self.chaos_config, key, value)
            self._save_chaos_config()
            self._notify_watchers("chaos")
    
    def add_template(self, template: ExperimentTemplate) -> None:
        """Adiciona novo template"""
        with self.lock:
            self.templates[template.name] = template
            self._save_templates()
            self._notify_watchers("templates")
    
    def remove_template(self, template_name: str) -> bool:
        """Remove template"""
        with self.lock:
            if template_name in self.templates:
                del self.templates[template_name]
                self._save_templates()
                self._notify_watchers("templates")
                return True
            return False
    
    def update_monitoring_config(self, **kwargs) -> None:
        """Atualiza configuração de monitoramento"""
        with self.lock:
            for key, value in kwargs.items():
                if hasattr(self.monitoring_config, key):
                    setattr(self.monitoring_config, key, value)
            self._save_monitoring_config()
            self._notify_watchers("monitoring")
    
    def update_alerting_config(self, **kwargs) -> None:
        """Atualiza configuração de alertas"""
        with self.lock:
            for key, value in kwargs.items():
                if hasattr(self.alerting_config, key):
                    setattr(self.alerting_config, key, value)
            self._save_alerting_config()
            self._notify_watchers("alerting")
    
    def update_rollback_config(self, **kwargs) -> None:
        """Atualiza configuração de rollback"""
        with self.lock:
            for key, value in kwargs.items():
                if hasattr(self.rollback_config, key):
                    setattr(self.rollback_config, key, value)
            self._save_rollback_config()
            self._notify_watchers("rollback")
    
    def validate_experiment_config(self, config: Dict[str, Any]) -> List[str]:
        """Valida configuração de experimento"""
        errors = []
        
        # Validações básicas
        if 'name' not in config:
            errors.append("Nome do experimento é obrigatório")
        
        if 'type' not in config:
            errors.append("Tipo do experimento é obrigatório")
        
        if 'duration' in config and config['duration'] <= 0:
            errors.append("Duração deve ser maior que zero")
        
        if 'max_impact' in config and not 0 <= config['max_impact'] <= 1:
            errors.append("Impacto máximo deve estar entre 0 e 1")
        
        # Validações de segurança
        if self.chaos_config.safety_checks:
            current_hour = datetime.now().hour
            if current_hour in self.chaos_config.blackout_hours:
                errors.append(f"Experimentos não permitidos no horário {current_hour}:00")
            
            current_day = datetime.now().weekday()
            if current_day not in self.chaos_config.allowed_days:
                errors.append(f"Experimentos não permitidos no dia {current_day}")
        
        return errors
    
    def is_experiment_allowed(self, experiment_config: Dict[str, Any]) -> bool:
        """Verifica se experimento é permitido"""
        errors = self.validate_experiment_config(experiment_config)
        return len(errors) == 0
    
    def export_config(self, format: str = "yaml") -> str:
        """Exporta configuração completa"""
        with self.lock:
            config_data = {
                "chaos_config": asdict(self.chaos_config),
                "templates": [template.dict() for template in self.templates.values()],
                "monitoring_config": self.monitoring_config.dict(),
                "alerting_config": self.alerting_config.dict(),
                "rollback_config": self.rollback_config.dict(),
                "exported_at": datetime.now().isoformat()
            }
            
            if format.lower() == "json":
                return json.dumps(config_data, indent=2, default=str)
            else:
                return yaml.dump(config_data, default_flow_style=False)
    
    def import_config(self, config_data: str, format: str = "yaml") -> bool:
        """Importa configuração"""
        try:
            with self.lock:
                if format.lower() == "json":
                    data = json.loads(config_data)
                else:
                    data = yaml.safe_load(config_data)
                
                # Atualizar configurações
                if "chaos_config" in data:
                    self.chaos_config = ChaosConfig(**data["chaos_config"])
                    self._save_chaos_config()
                
                if "templates" in data:
                    self.templates.clear()
                    for template_data in data["templates"]:
                        template = ExperimentTemplate(**template_data)
                        self.templates[template.name] = template
                    self._save_templates()
                
                if "monitoring_config" in data:
                    self.monitoring_config = MonitoringConfig(**data["monitoring_config"])
                    self._save_monitoring_config()
                
                if "alerting_config" in data:
                    self.alerting_config = AlertingConfig(**data["alerting_config"])
                    self._save_alerting_config()
                
                if "rollback_config" in data:
                    self.rollback_config = RollbackConfig(**data["rollback_config"])
                    self._save_rollback_config()
                
                self._notify_watchers("all")
                logger.info("Configuration imported successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            return False
    
    def cleanup(self) -> None:
        """Limpa recursos"""
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        logger.info("ChaosConfigManager cleaned up")


class ConfigFileHandler(FileSystemEventHandler):
    """Handler para mudanças em arquivos de configuração"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.last_modified = 0.0
    
    def on_modified(self, event):
        """Chamado quando arquivo é modificado"""
        if event.is_directory:
            return
        
        # Evitar múltiplas notificações
        current_time = time.time()
        if current_time - self.last_modified < 1.0:
            return
        self.last_modified = current_time
        
        # Identificar tipo de configuração
        filename = Path(event.src_path).name
        if filename == "chaos_config.yaml":
            self.config_manager.reload_config("chaos")
        elif filename == "templates.yaml":
            self.config_manager.reload_config("templates")
        elif filename == "monitoring.yaml":
            self.config_manager.reload_config("monitoring")
        elif filename == "alerting.yaml":
            self.config_manager.reload_config("alerting")
        elif filename == "rollback.yaml":
            self.config_manager.reload_config("rollback")


# Função de conveniência para criar config manager
def create_config_manager(config_dir: Optional[str] = None) -> ConfigManager:
    """Cria uma instância do config manager"""
    return ConfigManager(config_dir) 
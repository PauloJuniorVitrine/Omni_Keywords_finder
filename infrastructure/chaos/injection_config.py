"""
Chaos Engineering Injection Configuration
========================================

Sistema de configuração para injeção de falhas com:
- Gerenciamento de parâmetros de injeção
- Validação de configurações
- Templates de configuração
- Configurações por ambiente
- Hot-reload de configurações

Author: Paulo Júnior
Date: 2025-01-27
Tracing ID: CHAOS_INJECTION_CONFIG_001_20250127
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


class InjectionType(Enum):
    """Tipos de injeção de falhas"""
    NETWORK_LATENCY = "network_latency"
    NETWORK_PACKET_LOSS = "network_packet_loss"
    NETWORK_BANDWIDTH_LIMIT = "network_bandwidth_limit"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_STRESS = "disk_stress"
    SERVICE_FAILURE = "service_failure"
    DATABASE_FAILURE = "database_failure"
    CACHE_FAILURE = "cache_failure"
    DEPENDENCY_FAILURE = "dependency_failure"
    PROCESS_KILL = "process_kill"
    CONTAINER_FAILURE = "container_failure"


class InjectionMode(Enum):
    """Modos de injeção"""
    CONTINUOUS = "continuous"
    INTERMITTENT = "intermittent"
    RANDOM = "random"
    BURST = "burst"
    GRADUAL = "gradual"


class Environment(Enum):
    """Ambientes de execução"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class InjectionConfig:
    """Configuração de injeção de falhas"""
    name: str
    description: str
    injection_type: InjectionType
    mode: InjectionMode
    environment: Environment
    
    # Parâmetros de execução
    duration: int = 300  # segundos
    interval: int = 5    # segundos
    max_concurrent: int = 3
    
    # Parâmetros de segurança
    enabled: bool = True
    safety_checks: bool = True
    max_impact: float = 0.3
    auto_rollback: bool = True
    rollback_threshold: float = 0.5
    
    # Parâmetros específicos do tipo
    parameters: Dict[str, Any] = None
    
    # Configurações de monitoramento
    monitor_enabled: bool = True
    metrics_interval: int = 5
    alert_thresholds: Dict[str, float] = None
    
    # Configurações de notificação
    notify_on_start: bool = True
    notify_on_completion: bool = True
    notify_on_failure: bool = True
    notify_on_rollback: bool = True
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.alert_thresholds is None:
            self.alert_thresholds = {}


class NetworkLatencyConfig(BaseModel):
    """Configuração para latência de rede"""
    latency_ms: int = Field(100, ge=0, le=10000, description="Latência em milissegundos")
    jitter_ms: int = Field(10, ge=0, le=1000, description="Jitter em milissegundos")
    target_interface: str = Field("eth0", description="Interface de rede alvo")
    target_hosts: List[str] = Field(default_factory=list, description="Hosts específicos")
    
    @validator('latency_ms')
    def validate_latency(cls, v):
        if v > 10000:
            raise ValueError("Latência muito alta (> 10s)")
        return v


class NetworkPacketLossConfig(BaseModel):
    """Configuração para perda de pacotes"""
    loss_percentage: float = Field(5.0, ge=0, le=50, description="Percentual de perda")
    target_interface: str = Field("eth0", description="Interface de rede alvo")
    target_hosts: List[str] = Field(default_factory=list, description="Hosts específicos")
    
    @validator('loss_percentage')
    def validate_loss_percentage(cls, v):
        if v > 50:
            raise ValueError("Percentual de perda muito alto (> 50%)")
        return v


class CPUStressConfig(BaseModel):
    """Configuração para stress de CPU"""
    cpu_load: float = Field(0.7, ge=0.1, le=0.9, description="Carga de CPU (0-1)")
    cores: int = Field(2, ge=1, description="Número de cores")
    stress_type: str = Field("cpu", description="Tipo de stress")
    
    @validator('cpu_load')
    def validate_cpu_load(cls, v):
        if v > 0.9:
            raise ValueError("Carga de CPU muito alta (> 90%)")
        return v


class MemoryStressConfig(BaseModel):
    """Configuração para stress de memória"""
    memory_mb: int = Field(512, ge=64, description="Memória em MB")
    stress_type: str = Field("vm", description="Tipo de stress")
    
    @validator('memory_mb')
    def validate_memory_mb(cls, v):
        if v > 8192:  # 8GB
            raise ValueError("Memória muito alta (> 8GB)")
        return v


class ServiceFailureConfig(BaseModel):
    """Configuração para falha de serviço"""
    service_name: str = Field(..., description="Nome do serviço")
    failure_rate: float = Field(0.3, ge=0, le=1, description="Taxa de falha (0-1)")
    failure_pattern: str = Field("random", description="Padrão de falha")
    failure_duration: int = Field(60, ge=1, description="Duração da falha em segundos")
    
    @validator('failure_pattern')
    def validate_failure_pattern(cls, v):
        if v not in ['stop', 'restart', 'random']:
            raise ValueError("Padrão de falha deve ser 'stop', 'restart' ou 'random'")
        return v


class InjectionTemplate(BaseModel):
    """Template de configuração de injeção"""
    name: str = Field(..., description="Nome do template")
    description: str = Field(..., description="Descrição do template")
    injection_type: InjectionType = Field(..., description="Tipo de injeção")
    category: str = Field(..., description="Categoria do template")
    
    # Configurações padrão
    mode: InjectionMode = Field(InjectionMode.CONTINUOUS, description="Modo de injeção")
    duration: int = Field(300, description="Duração padrão em segundos")
    interval: int = Field(5, description="Intervalo padrão em segundos")
    
    # Parâmetros específicos
    network_latency_config: Optional[NetworkLatencyConfig] = None
    network_packet_loss_config: Optional[NetworkPacketLossConfig] = None
    cpu_stress_config: Optional[CPUStressConfig] = None
    memory_stress_config: Optional[MemoryStressConfig] = None
    service_failure_config: Optional[ServiceFailureConfig] = None
    
    # Configurações de segurança
    max_impact: float = Field(0.3, description="Impacto máximo permitido")
    auto_rollback: bool = Field(True, description="Rollback automático")
    rollback_threshold: float = Field(0.5, description="Threshold para rollback")
    
    # Configurações de monitoramento
    monitor_enabled: bool = Field(True, description="Monitoramento habilitado")
    metrics_interval: int = Field(5, description="Intervalo de métricas")
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


class ConfigManager:
    """
    Gerenciador de configurações de injeção
    """
    
    def __init__(self, config_dir: str = "config/chaos/injection"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Arquivos de configuração
        self.templates_file = self.config_dir / "templates.yaml"
        self.configs_file = self.config_dir / "configs.yaml"
        self.environment_file = self.config_dir / "environment.yaml"
        
        # Configurações carregadas
        self.templates: Dict[str, InjectionTemplate] = {}
        self.configs: Dict[str, InjectionConfig] = {}
        self.environment_config: Dict[str, Any] = {}
        
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
        
        logger.info("InjectionConfigManager initialized")
    
    def _load_all_configs(self) -> None:
        """Carrega todas as configurações"""
        try:
            self._load_templates()
            self._load_configs()
            self._load_environment_config()
            logger.info("All injection configurations loaded successfully")
        except Exception as e:
            logger.error(f"Error loading injection configurations: {e}")
    
    def _load_templates(self) -> None:
        """Carrega templates de injeção"""
        if self.templates_file.exists():
            with open(self.templates_file, 'r') as f:
                data = yaml.safe_load(f)
                
            for template_data in data.get('templates', []):
                template = InjectionTemplate(**template_data)
                self.templates[template.name] = template
        else:
            # Templates padrão
            self._create_default_templates()
            self._save_templates()
    
    def _load_configs(self) -> None:
        """Carrega configurações de injeção"""
        if self.configs_file.exists():
            with open(self.configs_file, 'r') as f:
                data = yaml.safe_load(f)
                
            for config_data in data.get('configs', []):
                config = InjectionConfig(**config_data)
                self.configs[config.name] = config
        else:
            # Configurações padrão
            self._create_default_configs()
            self._save_configs()
    
    def _load_environment_config(self) -> None:
        """Carrega configuração de ambiente"""
        if self.environment_file.exists():
            with open(self.environment_file, 'r') as f:
                self.environment_config = yaml.safe_load(f)
        else:
            # Configuração padrão
            self.environment_config = {
                'environment': 'development',
                'safety_enabled': True,
                'max_concurrent_injections': 3,
                'default_timeout': 300,
                'blackout_hours': [0, 1, 2, 3, 4, 5, 6, 22, 23],
                'allowed_days': [1, 2, 3, 4, 5]  # Segunda a Sexta
            }
            self._save_environment_config()
    
    def _create_default_templates(self) -> None:
        """Cria templates padrão"""
        default_templates = [
            {
                "name": "network_latency_basic",
                "description": "Teste básico de latência de rede",
                "injection_type": InjectionType.NETWORK_LATENCY,
                "category": "network",
                "network_latency_config": {
                    "latency_ms": 100,
                    "jitter_ms": 10,
                    "target_interface": "eth0"
                }
            },
            {
                "name": "network_packet_loss_basic",
                "description": "Teste básico de perda de pacotes",
                "injection_type": InjectionType.NETWORK_PACKET_LOSS,
                "category": "network",
                "network_packet_loss_config": {
                    "loss_percentage": 5.0,
                    "target_interface": "eth0"
                }
            },
            {
                "name": "cpu_stress_basic",
                "description": "Teste básico de stress de CPU",
                "injection_type": InjectionType.CPU_STRESS,
                "category": "resource",
                "cpu_stress_config": {
                    "cpu_load": 0.7,
                    "cores": 2
                }
            },
            {
                "name": "memory_stress_basic",
                "description": "Teste básico de stress de memória",
                "injection_type": InjectionType.MEMORY_STRESS,
                "category": "resource",
                "memory_stress_config": {
                    "memory_mb": 512
                }
            },
            {
                "name": "service_failure_basic",
                "description": "Teste básico de falha de serviço",
                "injection_type": InjectionType.SERVICE_FAILURE,
                "category": "service",
                "service_failure_config": {
                    "service_name": "nginx",
                    "failure_rate": 0.3,
                    "failure_pattern": "random"
                }
            }
        ]
        
        for template_data in default_templates:
            template = InjectionTemplate(**template_data)
            self.templates[template.name] = template
    
    def _create_default_configs(self) -> None:
        """Cria configurações padrão"""
        default_configs = [
            {
                "name": "development_network_test",
                "description": "Teste de rede para desenvolvimento",
                "injection_type": InjectionType.NETWORK_LATENCY,
                "mode": InjectionMode.CONTINUOUS,
                "environment": Environment.DEVELOPMENT,
                "duration": 120,
                "parameters": {"latency_ms": 50, "jitter_ms": 5}
            },
            {
                "name": "staging_resource_test",
                "description": "Teste de recursos para staging",
                "injection_type": InjectionType.CPU_STRESS,
                "mode": InjectionMode.INTERMITTENT,
                "environment": Environment.STAGING,
                "duration": 180,
                "parameters": {"cpu_load": 0.5, "cores": 1}
            }
        ]
        
        for config_data in default_configs:
            config = InjectionConfig(**config_data)
            self.configs[config.name] = config
    
    def _save_templates(self) -> None:
        """Salva templates"""
        data = {"templates": [template.dict() for template in self.templates.values()]}
        with open(self.templates_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def _save_configs(self) -> None:
        """Salva configurações"""
        data = {"configs": [asdict(config) for config in self.configs.values()]}
        with open(self.configs_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def _save_environment_config(self) -> None:
        """Salva configuração de ambiente"""
        with open(self.environment_file, 'w') as f:
            yaml.dump(self.environment_config, f, default_flow_style=False)
    
    def _setup_file_watcher(self) -> None:
        """Configura observador de arquivos para hot-reload"""
        try:
            self.observer.schedule(self.file_handler, str(self.config_dir), recursive=False)
            self.observer.start()
            logger.info("File watcher started for injection config hot-reload")
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
            if config_type is None or config_type == "templates":
                self._load_templates()
            if config_type is None or config_type == "configs":
                self._load_configs()
            if config_type is None or config_type == "environment":
                self._load_environment_config()
            
            self._notify_watchers(config_type or "all")
            logger.info(f"Injection configuration reloaded: {config_type or 'all'}")
    
    def get_template(self, template_name: str) -> Optional[InjectionTemplate]:
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
                        'injection_type': template.injection_type.value,
                        'category': template.category,
                        'duration': template.duration
                    })
            return templates
    
    def get_config(self, config_name: str) -> Optional[InjectionConfig]:
        """Obtém configuração por nome"""
        with self.lock:
            return self.configs.get(config_name)
    
    def list_configs(self, environment: Optional[Environment] = None) -> List[Dict[str, Any]]:
        """Lista configurações disponíveis"""
        with self.lock:
            configs = []
            for config in self.configs.values():
                if environment is None or config.environment == environment:
                    configs.append({
                        'name': config.name,
                        'description': config.description,
                        'injection_type': config.injection_type.value,
                        'mode': config.mode.value,
                        'environment': config.environment.value,
                        'duration': config.duration,
                        'enabled': config.enabled
                    })
            return configs
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Obtém configuração de ambiente"""
        with self.lock:
            return self.environment_config.copy()
    
    def add_template(self, template: InjectionTemplate) -> None:
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
    
    def add_config(self, config: InjectionConfig) -> None:
        """Adiciona nova configuração"""
        with self.lock:
            self.configs[config.name] = config
            self._save_configs()
            self._notify_watchers("configs")
    
    def remove_config(self, config_name: str) -> bool:
        """Remove configuração"""
        with self.lock:
            if config_name in self.configs:
                del self.configs[config_name]
                self._save_configs()
                self._notify_watchers("configs")
                return True
            return False
    
    def update_environment_config(self, **kwargs) -> None:
        """Atualiza configuração de ambiente"""
        with self.lock:
            self.environment_config.update(kwargs)
            self._save_environment_config()
            self._notify_watchers("environment")
    
    def validate_injection_config(self, config: Dict[str, Any]) -> List[str]:
        """Valida configuração de injeção"""
        errors = []
        
        # Validações básicas
        if 'name' not in config:
            errors.append("Nome da configuração é obrigatório")
        
        if 'injection_type' not in config:
            errors.append("Tipo de injeção é obrigatório")
        
        if 'duration' in config and config['duration'] <= 0:
            errors.append("Duração deve ser maior que zero")
        
        if 'max_impact' in config and not 0 <= config['max_impact'] <= 1:
            errors.append("Impacto máximo deve estar entre 0 e 1")
        
        # Validações de segurança
        if self.environment_config.get('safety_enabled', True):
            current_hour = datetime.now().hour
            blackout_hours = self.environment_config.get('blackout_hours', [])
            if current_hour in blackout_hours:
                errors.append(f"Injeções não permitidas no horário {current_hour}:00")
            
            current_day = datetime.now().weekday()
            allowed_days = self.environment_config.get('allowed_days', [])
            if current_day not in allowed_days:
                errors.append(f"Injeções não permitidas no dia {current_day}")
        
        # Validações específicas por tipo
        injection_type = config.get('injection_type')
        if injection_type:
            errors.extend(self._validate_type_specific_config(injection_type, config))
        
        return errors
    
    def _validate_type_specific_config(self, injection_type: str, config: Dict[str, Any]) -> List[str]:
        """Valida configuração específica do tipo"""
        errors = []
        
        if injection_type == InjectionType.NETWORK_LATENCY.value:
            params = config.get('parameters', {})
            latency_ms = params.get('latency_ms', 0)
            if latency_ms > 10000:
                errors.append("Latência muito alta (> 10s)")
        
        elif injection_type == InjectionType.NETWORK_PACKET_LOSS.value:
            params = config.get('parameters', {})
            loss_percentage = params.get('loss_percentage', 0)
            if loss_percentage > 50:
                errors.append("Percentual de perda muito alto (> 50%)")
        
        elif injection_type == InjectionType.CPU_STRESS.value:
            params = config.get('parameters', {})
            cpu_load = params.get('cpu_load', 0)
            if cpu_load > 0.9:
                errors.append("Carga de CPU muito alta (> 90%)")
        
        elif injection_type == InjectionType.MEMORY_STRESS.value:
            params = config.get('parameters', {})
            memory_mb = params.get('memory_mb', 0)
            if memory_mb > 8192:
                errors.append("Memória muito alta (> 8GB)")
        
        return errors
    
    def is_injection_allowed(self, config: Dict[str, Any]) -> bool:
        """Verifica se injeção é permitida"""
        errors = self.validate_injection_config(config)
        return len(errors) == 0
    
    def create_injection_from_template(self, template_name: str, 
                                     custom_params: Optional[Dict[str, Any]] = None) -> Optional[InjectionConfig]:
        """Cria configuração de injeção a partir de template"""
        template = self.get_template(template_name)
        if not template:
            return None
        
        # Criar configuração baseada no template
        config_data = {
            'name': f"{template_name}_{int(time.time())}",
            'description': template.description,
            'injection_type': template.injection_type,
            'mode': template.mode,
            'environment': Environment.DEVELOPMENT,
            'duration': template.duration,
            'interval': template.interval,
            'max_impact': template.max_impact,
            'auto_rollback': template.auto_rollback,
            'rollback_threshold': template.rollback_threshold,
            'monitor_enabled': template.monitor_enabled,
            'metrics_interval': template.metrics_interval,
            'alert_thresholds': template.alert_thresholds.copy(),
            'parameters': {}
        }
        
        # Adicionar parâmetros específicos do tipo
        if template.injection_type == InjectionType.NETWORK_LATENCY and template.network_latency_config:
            config_data['parameters'] = template.network_latency_config.dict()
        elif template.injection_type == InjectionType.NETWORK_PACKET_LOSS and template.network_packet_loss_config:
            config_data['parameters'] = template.network_packet_loss_config.dict()
        elif template.injection_type == InjectionType.CPU_STRESS and template.cpu_stress_config:
            config_data['parameters'] = template.cpu_stress_config.dict()
        elif template.injection_type == InjectionType.MEMORY_STRESS and template.memory_stress_config:
            config_data['parameters'] = template.memory_stress_config.dict()
        elif template.injection_type == InjectionType.SERVICE_FAILURE and template.service_failure_config:
            config_data['parameters'] = template.service_failure_config.dict()
        
        # Sobrescrever com parâmetros customizados
        if custom_params:
            config_data['parameters'].update(custom_params)
        
        return InjectionConfig(**config_data)
    
    def export_config(self, format: str = "yaml") -> str:
        """Exporta configuração completa"""
        with self.lock:
            config_data = {
                "templates": [template.dict() for template in self.templates.values()],
                "configs": [asdict(config) for config in self.configs.values()],
                "environment_config": self.environment_config,
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
                
                # Atualizar templates
                if "templates" in data:
                    self.templates.clear()
                    for template_data in data["templates"]:
                        template = InjectionTemplate(**template_data)
                        self.templates[template.name] = template
                    self._save_templates()
                
                # Atualizar configurações
                if "configs" in data:
                    self.configs.clear()
                    for config_data in data["configs"]:
                        config = InjectionConfig(**config_data)
                        self.configs[config.name] = config
                    self._save_configs()
                
                # Atualizar configuração de ambiente
                if "environment_config" in data:
                    self.environment_config = data["environment_config"]
                    self._save_environment_config()
                
                self._notify_watchers("all")
                logger.info("Injection configuration imported successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error importing injection configuration: {e}")
            return False
    
    def cleanup(self) -> None:
        """Limpa recursos"""
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        logger.info("InjectionConfigManager cleaned up")


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
        if filename == "templates.yaml":
            self.config_manager.reload_config("templates")
        elif filename == "configs.yaml":
            self.config_manager.reload_config("configs")
        elif filename == "environment.yaml":
            self.config_manager.reload_config("environment")


# Função de conveniência para criar config manager
def create_injection_config_manager(config_dir: Optional[str] = None) -> ConfigManager:
    """Cria uma instância do injection config manager"""
    return ConfigManager(config_dir) 
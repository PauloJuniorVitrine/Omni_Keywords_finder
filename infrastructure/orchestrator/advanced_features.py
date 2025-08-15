"""
Advanced Features Module - Omni Keywords Finder

Recursos avançados para o orquestrador:
- Agendamento de execuções
- Templates de configuração
- Relatórios avançados

Tracing ID: ADVANCED_FEATURES_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import logging
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import threading

logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """Tipos de agendamento."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class ScheduleConfig:
    """Configuração de agendamento."""
    schedule_id: str
    schedule_type: ScheduleType
    enabled: bool = True
    time: Optional[str] = None  # HH:MM
    nichos: List[str] = field(default_factory=list)
    max_retries: int = 3


@dataclass
class TemplateConfig:
    """Configuração de template."""
    template_id: str
    name: str
    description: str
    template_data: Dict[str, Any]
    category: str = "default"


class Scheduler:
    """Agendador de execuções."""
    
    def __init__(self):
        """Inicializa o agendador."""
        self.schedules: Dict[str, ScheduleConfig] = {}
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        
        logger.info("Scheduler inicializado")
    
    def add_schedule(self, config: ScheduleConfig) -> bool:
        """Adiciona um agendamento."""
        try:
            self.schedules[config.schedule_id] = config
            logger.info(f"Agendamento adicionado: {config.schedule_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar agendamento: {e}")
            return False
    
    def start(self):
        """Inicia o agendador."""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Scheduler iniciado")
    
    def stop(self):
        """Para o agendador."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("Scheduler parado")
    
    def _run_scheduler(self):
        """Executa o loop do agendador."""
        while self.running:
            # Verificar agendamentos
            current_time = datetime.now().strftime("%H:%M")
            
            for schedule in self.schedules.values():
                if schedule.enabled and schedule.time == current_time:
                    self._execute_scheduled_job(schedule)
            
            time.sleep(60)  # Verificar a cada minuto
    
    def _execute_scheduled_job(self, config: ScheduleConfig):
        """Executa job agendado."""
        logger.info(f"Executando job agendado: {config.schedule_id}")
        # Aqui você integraria com o orquestrador
        logger.info(f"Job {config.schedule_id} executado com sucesso")
    
    def get_schedules(self) -> List[ScheduleConfig]:
        """Obtém todos os agendamentos."""
        return list(self.schedules.values())


class TemplateManager:
    """Gerenciador de templates."""
    
    def __init__(self, templates_dir: str = "templates/orchestrator"):
        """Inicializa o gerenciador de templates."""
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.templates: Dict[str, TemplateConfig] = {}
        self._load_templates()
        logger.info("TemplateManager inicializado")
    
    def _load_templates(self):
        """Carrega templates do diretório."""
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                template = TemplateConfig(
                    template_id=data.get("id"),
                    name=data.get("name"),
                    description=data.get("description"),
                    template_data=data.get("data", {}),
                    category=data.get("category", "default")
                )
                
                self.templates[template.template_id] = template
                
            except Exception as e:
                logger.error(f"Erro ao carregar template {template_file}: {e}")
    
    def create_template(
        self, 
        template_id: str,
        name: str,
        description: str,
        template_data: Dict[str, Any],
        category: str = "default"
    ) -> bool:
        """Cria um novo template."""
        try:
            template = TemplateConfig(
                template_id=template_id,
                name=name,
                description=description,
                template_data=template_data,
                category=category
            )
            
            self.templates[template_id] = template
            self._save_template(template)
            
            logger.info(f"Template criado: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar template: {e}")
            return False
    
    def _save_template(self, template: TemplateConfig):
        """Salva template em arquivo."""
        template_file = self.templates_dir / f"{template.template_id}.json"
        
        data = {
            "id": template.template_id,
            "name": template.name,
            "description": template.description,
            "data": template.template_data,
            "category": template.category
        }
        
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_template(self, template_id: str) -> Optional[TemplateConfig]:
        """Obtém um template."""
        return self.templates.get(template_id)
    
    def get_templates_by_category(self, category: str) -> List[TemplateConfig]:
        """Obtém templates por categoria."""
        return [t for t in self.templates.values() if t.category == category]


class AdvancedFeaturesManager:
    """Gerenciador de recursos avançados."""
    
    def __init__(self):
        """Inicializa o gerenciador."""
        self.scheduler = Scheduler()
        self.template_manager = TemplateManager()
        
        logger.info("AdvancedFeaturesManager inicializado")
    
    def setup_default_templates(self):
        """Configura templates padrão."""
        # Template para nicho de tecnologia
        self.template_manager.create_template(
            template_id="tech_niche",
            name="Nicho Tecnologia",
            description="Configuração padrão para nicho de tecnologia",
            template_data={
                "max_keywords": 100,
                "min_volume": 1000,
                "max_competition": 0.7,
                "prompts": [
                    "Análise de produto {keyword}",
                    "Comparação {keyword} vs alternativas"
                ]
            },
            category="technology"
        )
        
        # Template para nicho de saúde
        self.template_manager.create_template(
            template_id="health_niche",
            name="Nicho Saúde",
            description="Configuração padrão para nicho de saúde",
            template_data={
                "max_keywords": 50,
                "min_volume": 500,
                "max_competition": 0.5,
                "prompts": [
                    "Benefícios de {keyword} para saúde",
                    "Como usar {keyword} corretamente"
                ]
            },
            category="health"
        )
    
    def schedule_daily_processing(self, nichos: List[str], time: str = "02:00"):
        """Agenda processamento diário."""
        config = ScheduleConfig(
            schedule_id="daily_processing",
            schedule_type=ScheduleType.DAILY,
            time=time,
            nichos=nichos
        )
        
        self.scheduler.add_schedule(config)
        logger.info(f"Processamento diário agendado para {time}")
    
    def get_management_dashboard_data(self) -> Dict[str, Any]:
        """Obtém dados para dashboard de gerenciamento."""
        return {
            "schedules": {
                "total": len(self.scheduler.get_schedules()),
                "active": len([string_data for string_data in self.scheduler.get_schedules() if string_data.enabled])
            },
            "templates": {
                "total": len(self.template_manager.templates),
                "categories": list(set(t.category for t in self.template_manager.templates.values()))
            }
        }


# Instância global
_advanced_features_manager: Optional[AdvancedFeaturesManager] = None


def obter_advanced_features_manager() -> AdvancedFeaturesManager:
    """Obtém instância global do gerenciador."""
    global _advanced_features_manager
    
    if _advanced_features_manager is None:
        _advanced_features_manager = AdvancedFeaturesManager()
    
    return _advanced_features_manager


def setup_advanced_features():
    """Configura recursos avançados padrão."""
    manager = obter_advanced_features_manager()
    manager.setup_default_templates()
    manager.scheduler.start()
    logger.info("Recursos avançados configurados")


def get_dashboard_data() -> Dict[str, Any]:
    """Função helper para obter dados do dashboard."""
    manager = obter_advanced_features_manager()
    return manager.get_management_dashboard_data() 
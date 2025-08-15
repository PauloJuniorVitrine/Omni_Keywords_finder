"""
Serviço de Automação Avançada
=============================

Sistema para automação de processos com triggers, agendamento
e workflows automatizados.

Tracing ID: AUTOMATION_001
Data: 2024-12-27
Autor: Sistema de Automação
"""

import asyncio
import json
import logging
import schedule
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from sqlalchemy.orm import Session
import threading

from ..models.prompt_system import LogOperacao
from ..services.prompt_filler_service import PromptFillerService
from ..services.ai_integration_service import AIIntegrationService

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Tipos de triggers disponíveis"""
    SCHEDULE = "schedule"
    DATA_ARRIVAL = "data_arrival"
    MANUAL = "manual"
    WEBHOOK = "webhook"
    CONDITION = "condition"


class WorkflowStatus(Enum):
    """Status do workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AutomationTrigger:
    """Configuração de trigger"""
    trigger_id: str
    name: str
    trigger_type: TriggerType
    config: Dict[str, Any]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkflowStep:
    """Passo do workflow"""
    step_id: str
    name: str
    action: str
    config: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowExecution:
    """Execução de workflow"""
    execution_id: str
    workflow_id: str
    trigger_id: str
    status: WorkflowStatus
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AutomationService:
    """Serviço principal de automação"""
    
    def __init__(self, db: Session):
        self.db = db
        self.triggers: Dict[str, AutomationTrigger] = {}
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.scheduler_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Serviços dependentes
        self.prompt_service = PromptFillerService(db)
        self.ai_service = None  # Inicializado quando necessário
        
        self._load_triggers()
        self._load_workflows()
    
    def _load_triggers(self):
        """Carrega triggers do banco de dados"""
        try:
            # Triggers padrão
            default_triggers = [
                AutomationTrigger(
                    trigger_id="daily_processing",
                    name="Processamento Diário",
                    trigger_type=TriggerType.SCHEDULE,
                    config={"schedule": "02:00", "timezone": "America/Sao_Paulo"}
                ),
                AutomationTrigger(
                    trigger_id="data_arrival",
                    name="Chegada de Dados",
                    trigger_type=TriggerType.DATA_ARRIVAL,
                    config={"check_interval": 300}  # 5 minutos
                ),
                AutomationTrigger(
                    trigger_id="weekly_cleanup",
                    name="Limpeza Semanal",
                    trigger_type=TriggerType.SCHEDULE,
                    config={"schedule": "sunday 03:00", "timezone": "America/Sao_Paulo"}
                )
            ]
            
            for trigger in default_triggers:
                self.triggers[trigger.trigger_id] = trigger
            
            logger.info(f"Carregados {len(self.triggers)} triggers")
            
        except Exception as e:
            logger.error(f"Erro ao carregar triggers: {str(e)}")
    
    def _load_workflows(self):
        """Carrega workflows do banco de dados"""
        try:
            # Workflow padrão de processamento
            processing_workflow = [
                WorkflowStep(
                    step_id="validate_data",
                    name="Validar Dados",
                    action="validate_collected_data",
                    config={"strict_mode": True}
                ),
                WorkflowStep(
                    step_id="fill_prompts",
                    name="Preencher Prompts",
                    action="fill_prompts",
                    config={"batch_size": 10},
                    dependencies=["validate_data"]
                ),
                WorkflowStep(
                    step_id="generate_content",
                    name="Gerar Conteúdo",
                    action="generate_ai_content",
                    config={"provider": "openai", "max_tokens": 2000},
                    dependencies=["fill_prompts"]
                ),
                WorkflowStep(
                    step_id="validate_results",
                    name="Validar Resultados",
                    action="validate_generated_content",
                    config={"quality_threshold": 0.8},
                    dependencies=["generate_content"]
                )
            ]
            
            self.workflows["default_processing"] = processing_workflow
            
            # Workflow de limpeza
            cleanup_workflow = [
                WorkflowStep(
                    step_id="backup_data",
                    name="Backup de Dados",
                    action="backup_system_data",
                    config={"include_logs": True}
                ),
                WorkflowStep(
                    step_id="cleanup_old_files",
                    name="Limpar Arquivos Antigos",
                    action="cleanup_old_files",
                    config={"retention_days": 30},
                    dependencies=["backup_data"]
                ),
                WorkflowStep(
                    step_id="optimize_database",
                    name="Otimizar Banco",
                    action="optimize_database",
                    config={"vacuum": True},
                    dependencies=["cleanup_old_files"]
                )
            ]
            
            self.workflows["weekly_cleanup"] = cleanup_workflow
            
            logger.info(f"Carregados {len(self.workflows)} workflows")
            
        except Exception as e:
            logger.error(f"Erro ao carregar workflows: {str(e)}")
    
    def create_trigger(self, name: str, trigger_type: TriggerType, config: Dict[str, Any]) -> AutomationTrigger:
        """Cria novo trigger"""
        try:
            trigger_id = f"trigger_{int(time.time())}"
            
            trigger = AutomationTrigger(
                trigger_id=trigger_id,
                name=name,
                trigger_type=trigger_type,
                config=config
            )
            
            self.triggers[trigger_id] = trigger
            
            # Configurar agendamento se necessário
            if trigger_type == TriggerType.SCHEDULE:
                self._setup_schedule_trigger(trigger)
            
            # Log da operação
            self._log_automation_operation("create_trigger", trigger_id)
            
            logger.info(f"Trigger criado: {trigger_id}")
            return trigger
            
        except Exception as e:
            logger.error(f"Erro ao criar trigger: {str(e)}")
            raise
    
    def _setup_schedule_trigger(self, trigger: AutomationTrigger):
        """Configura trigger agendado"""
        try:
            schedule_config = trigger.config.get("schedule", "")
            timezone = trigger.config.get("timezone", "UTC")
            
            if schedule_config:
                # Configurar agendamento
                if ":" in schedule_config:
                    # Horário específico
                    schedule.every().day.at(schedule_config).do(
                        self._execute_triggered_workflow, trigger.trigger_id
                    )
                elif "sunday" in schedule_config.lower():
                    # Domingo específico
                    time_part = schedule_config.split()[-1]
                    schedule.every().sunday.at(time_part).do(
                        self._execute_triggered_workflow, trigger.trigger_id
                    )
                
                logger.info(f"Agendamento configurado para {trigger.trigger_id}: {schedule_config}")
                
        except Exception as e:
            logger.error(f"Erro ao configurar agendamento: {str(e)}")
    
    def create_workflow(self, workflow_id: str, steps: List[WorkflowStep]) -> str:
        """Cria novo workflow"""
        try:
            self.workflows[workflow_id] = steps
            
            # Log da operação
            self._log_automation_operation("create_workflow", workflow_id)
            
            logger.info(f"Workflow criado: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Erro ao criar workflow: {str(e)}")
            raise
    
    async def execute_workflow(self, workflow_id: str, trigger_id: str = "manual") -> WorkflowExecution:
        """Executa workflow"""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} não encontrado")
            
            execution_id = f"exec_{int(time.time())}"
            
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                trigger_id=trigger_id,
                status=WorkflowStatus.RUNNING
            )
            
            self.executions[execution_id] = execution
            
            # Executar passos
            workflow_steps = self.workflows[workflow_id]
            
            for step in workflow_steps:
                try:
                    # Verificar dependências
                    if not self._check_dependencies(step, execution.steps_completed):
                        logger.warning(f"Dependências não atendidas para {step.step_id}")
                        continue
                    
                    # Executar passo
                    logger.info(f"Executando passo: {step.step_id}")
                    await self._execute_step(step, execution)
                    
                    execution.steps_completed.append(step.step_id)
                    
                except Exception as e:
                    logger.error(f"Erro no passo {step.step_id}: {str(e)}")
                    execution.steps_failed.append(step.step_id)
                    
                    # Tentar novamente se configurado
                    if step.retry_count < step.max_retries:
                        step.retry_count += 1
                        logger.info(f"Tentativa {step.retry_count} para {step.step_id}")
                        continue
                    else:
                        execution.status = WorkflowStatus.FAILED
                        execution.error_message = f"Falha no passo {step.step_id}: {str(e)}"
                        break
            
            # Finalizar execução
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.COMPLETED
            
            execution.end_time = datetime.utcnow()
            
            # Log da operação
            self._log_automation_operation("execute_workflow", execution_id)
            
            logger.info(f"Workflow executado: {execution_id} - {execution.status.value}")
            return execution
            
        except Exception as e:
            logger.error(f"Erro na execução do workflow: {str(e)}")
            raise
    
    def _execute_triggered_workflow(self, trigger_id: str):
        """Executa workflow acionado por trigger"""
        try:
            # Mapear trigger para workflow
            workflow_mapping = {
                "daily_processing": "default_processing",
                "weekly_cleanup": "weekly_cleanup"
            }
            
            workflow_id = workflow_mapping.get(trigger_id)
            if workflow_id:
                # Executar em thread separada
                thread = threading.Thread(
                    target=self._run_workflow_async,
                    args=(workflow_id, trigger_id)
                )
                thread.start()
                
                logger.info(f"Workflow acionado: {trigger_id} -> {workflow_id}")
            
        except Exception as e:
            logger.error(f"Erro ao executar workflow acionado: {str(e)}")
    
    def _run_workflow_async(self, workflow_id: str, trigger_id: str):
        """Executa workflow de forma assíncrona"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.execute_workflow(workflow_id, trigger_id))
        except Exception as e:
            logger.error(f"Erro na execução assíncrona: {str(e)}")
    
    async def _execute_step(self, step: WorkflowStep, execution: WorkflowExecution):
        """Executa passo individual do workflow"""
        try:
            if step.action == "validate_collected_data":
                await self._validate_collected_data(step.config)
            elif step.action == "fill_prompts":
                await self._fill_prompts(step.config)
            elif step.action == "generate_ai_content":
                await self._generate_ai_content(step.config)
            elif step.action == "validate_generated_content":
                await self._validate_generated_content(step.config)
            elif step.action == "backup_system_data":
                await self._backup_system_data(step.config)
            elif step.action == "cleanup_old_files":
                await self._cleanup_old_files(step.config)
            elif step.action == "optimize_database":
                await self._optimize_database(step.config)
            else:
                raise ValueError(f"Ação desconhecida: {step.action}")
                
        except Exception as e:
            logger.error(f"Erro na execução do passo {step.step_id}: {str(e)}")
            raise
    
    def _check_dependencies(self, step: WorkflowStep, completed_steps: List[str]) -> bool:
        """Verifica se dependências foram atendidas"""
        return all(dep in completed_steps for dep in step.dependencies)
    
    async def _validate_collected_data(self, config: Dict[str, Any]):
        """Valida dados coletados"""
        logger.info("Validando dados coletados...")
        # Implementar validação
        await asyncio.sleep(1)
    
    async def _fill_prompts(self, config: Dict[str, Any]):
        """Preenche prompts"""
        logger.info("Preenchendo prompts...")
        # Implementar preenchimento
        await asyncio.sleep(2)
    
    async def _generate_ai_content(self, config: Dict[str, Any]):
        """Gera conteúdo com IA"""
        logger.info("Gerando conteúdo com IA...")
        # Implementar geração
        await asyncio.sleep(3)
    
    async def _validate_generated_content(self, config: Dict[str, Any]):
        """Valida conteúdo gerado"""
        logger.info("Validando conteúdo gerado...")
        # Implementar validação
        await asyncio.sleep(1)
    
    async def _backup_system_data(self, config: Dict[str, Any]):
        """Faz backup dos dados"""
        logger.info("Fazendo backup dos dados...")
        # Implementar backup
        await asyncio.sleep(5)
    
    async def _cleanup_old_files(self, config: Dict[str, Any]):
        """Limpa arquivos antigos"""
        logger.info("Limpando arquivos antigos...")
        # Implementar limpeza
        await asyncio.sleep(2)
    
    async def _optimize_database(self, config: Dict[str, Any]):
        """Otimiza banco de dados"""
        logger.info("Otimizando banco de dados...")
        # Implementar otimização
        await asyncio.sleep(3)
    
    def start_scheduler(self):
        """Inicia o agendador de tarefas"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.warning("Agendador já está rodando")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Agendador iniciado")
    
    def stop_scheduler(self):
        """Para o agendador de tarefas"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("Agendador parado")
    
    def _scheduler_worker(self):
        """Worker do agendador"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
            except Exception as e:
                logger.error(f"Erro no agendador: {str(e)}")
                time.sleep(60)
    
    def get_automation_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas de automação"""
        total_triggers = len(self.triggers)
        enabled_triggers = len([t for t in self.triggers.values() if t.enabled])
        total_workflows = len(self.workflows)
        total_executions = len(self.executions)
        
        completed_executions = len([e for e in self.executions.values() if e.status == WorkflowStatus.COMPLETED])
        failed_executions = len([e for e in self.executions.values() if e.status == WorkflowStatus.FAILED])
        
        success_rate = completed_executions / total_executions if total_executions > 0 else 0
        
        return {
            "total_triggers": total_triggers,
            "enabled_triggers": enabled_triggers,
            "total_workflows": total_workflows,
            "total_executions": total_executions,
            "completed_executions": completed_executions,
            "failed_executions": failed_executions,
            "success_rate": success_rate,
            "scheduler_running": self.running
        }
    
    def _log_automation_operation(self, operation: str, entity_id: str):
        """Registra log de operação de automação"""
        try:
            log_entry = LogOperacao(
                operacao=f"automation_{operation}",
                detalhes=json.dumps({
                    "entity_id": entity_id,
                    "timestamp": datetime.utcnow().isoformat()
                }),
                timestamp=datetime.utcnow()
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao salvar log: {str(e)}") 
"""
Testes Unitários para Automation Service
Serviço de Automação Avançada - Omni Keywords Finder

Prompt: Implementação de testes unitários para serviço de automação
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import asyncio
import time
import threading
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

from backend.app.services.automation_service import (
    AutomationService,
    AutomationTrigger,
    WorkflowStep,
    WorkflowExecution,
    TriggerType,
    WorkflowStatus
)
from backend.app.models.prompt_system import LogOperacao


class TestTriggerType:
    """Testes para enum TriggerType"""
    
    def test_trigger_type_values(self):
        """Testa valores do enum TriggerType"""
        assert TriggerType.SCHEDULE.value == "schedule"
        assert TriggerType.DATA_ARRIVAL.value == "data_arrival"
        assert TriggerType.MANUAL.value == "manual"
        assert TriggerType.WEBHOOK.value == "webhook"
        assert TriggerType.CONDITION.value == "condition"


class TestWorkflowStatus:
    """Testes para enum WorkflowStatus"""
    
    def test_workflow_status_values(self):
        """Testa valores do enum WorkflowStatus"""
        assert WorkflowStatus.PENDING.value == "pending"
        assert WorkflowStatus.RUNNING.value == "running"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.FAILED.value == "failed"
        assert WorkflowStatus.CANCELLED.value == "cancelled"


class TestAutomationTrigger:
    """Testes para AutomationTrigger"""
    
    def test_automation_trigger_creation(self):
        """Testa criação de AutomationTrigger"""
        trigger = AutomationTrigger(
            trigger_id="test_trigger",
            name="Test Trigger",
            trigger_type=TriggerType.SCHEDULE,
            config={"schedule": "10:00"}
        )
        
        assert trigger.trigger_id == "test_trigger"
        assert trigger.name == "Test Trigger"
        assert trigger.trigger_type == TriggerType.SCHEDULE
        assert trigger.config["schedule"] == "10:00"
        assert trigger.enabled is True
        assert isinstance(trigger.created_at, datetime)
    
    def test_automation_trigger_disabled(self):
        """Testa criação de AutomationTrigger desabilitado"""
        trigger = AutomationTrigger(
            trigger_id="disabled_trigger",
            name="Disabled Trigger",
            trigger_type=TriggerType.MANUAL,
            config={},
            enabled=False
        )
        
        assert trigger.enabled is False


class TestWorkflowStep:
    """Testes para WorkflowStep"""
    
    def test_workflow_step_creation(self):
        """Testa criação de WorkflowStep"""
        step = WorkflowStep(
            step_id="test_step",
            name="Test Step",
            action="test_action",
            config={"param": "value"}
        )
        
        assert step.step_id == "test_step"
        assert step.name == "Test Step"
        assert step.action == "test_action"
        assert step.config["param"] == "value"
        assert step.dependencies == []
        assert step.timeout_seconds == 300
        assert step.retry_count == 0
        assert step.max_retries == 3
    
    def test_workflow_step_with_dependencies(self):
        """Testa criação de WorkflowStep com dependências"""
        step = WorkflowStep(
            step_id="dependent_step",
            name="Dependent Step",
            action="dependent_action",
            config={},
            dependencies=["step1", "step2"],
            timeout_seconds=600,
            max_retries=5
        )
        
        assert step.dependencies == ["step1", "step2"]
        assert step.timeout_seconds == 600
        assert step.max_retries == 5


class TestWorkflowExecution:
    """Testes para WorkflowExecution"""
    
    def test_workflow_execution_creation(self):
        """Testa criação de WorkflowExecution"""
        execution = WorkflowExecution(
            execution_id="test_exec",
            workflow_id="test_workflow",
            trigger_id="test_trigger",
            status=WorkflowStatus.RUNNING
        )
        
        assert execution.execution_id == "test_exec"
        assert execution.workflow_id == "test_workflow"
        assert execution.trigger_id == "test_trigger"
        assert execution.status == WorkflowStatus.RUNNING
        assert execution.steps_completed == []
        assert execution.steps_failed == []
        assert isinstance(execution.start_time, datetime)
        assert execution.end_time is None
        assert execution.error_message is None
        assert execution.metadata == {}
    
    def test_workflow_execution_completed(self):
        """Testa WorkflowExecution completado"""
        execution = WorkflowExecution(
            execution_id="completed_exec",
            workflow_id="test_workflow",
            trigger_id="test_trigger",
            status=WorkflowStatus.COMPLETED
        )
        
        execution.steps_completed = ["step1", "step2"]
        execution.end_time = datetime.utcnow()
        execution.metadata = {"duration": 120}
        
        assert execution.status == WorkflowStatus.COMPLETED
        assert len(execution.steps_completed) == 2
        assert execution.end_time is not None
        assert execution.metadata["duration"] == 120


class TestAutomationService:
    """Testes para AutomationService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def automation_service(self, mock_db):
        """Instância do AutomationService para testes"""
        return AutomationService(mock_db)
    
    def test_automation_service_initialization(self, automation_service, mock_db):
        """Testa inicialização do AutomationService"""
        assert automation_service.db == mock_db
        assert isinstance(automation_service.triggers, dict)
        assert isinstance(automation_service.workflows, dict)
        assert isinstance(automation_service.executions, dict)
        assert automation_service.scheduler_thread is None
        assert automation_service.running is False
    
    def test_load_triggers(self, automation_service):
        """Testa carregamento de triggers"""
        # Verificar se triggers padrão foram carregados
        assert "daily_processing" in automation_service.triggers
        assert "data_arrival" in automation_service.triggers
        assert "weekly_cleanup" in automation_service.triggers
        
        daily_trigger = automation_service.triggers["daily_processing"]
        assert daily_trigger.name == "Processamento Diário"
        assert daily_trigger.trigger_type == TriggerType.SCHEDULE
        assert daily_trigger.config["schedule"] == "02:00"
    
    def test_load_workflows(self, automation_service):
        """Testa carregamento de workflows"""
        # Verificar se workflows padrão foram carregados
        assert "default_processing" in automation_service.workflows
        assert "weekly_cleanup" in automation_service.workflows
        
        processing_workflow = automation_service.workflows["default_processing"]
        assert len(processing_workflow) == 4
        
        # Verificar primeiro passo
        first_step = processing_workflow[0]
        assert first_step.step_id == "validate_data"
        assert first_step.name == "Validar Dados"
        assert first_step.action == "validate_collected_data"
    
    def test_create_trigger(self, automation_service, mock_db):
        """Testa criação de trigger"""
        with patch('time.time', return_value=1640995200):
            trigger = automation_service.create_trigger(
                name="Test Trigger",
                trigger_type=TriggerType.MANUAL,
                config={"param": "value"}
            )
        
        assert trigger.trigger_id == "trigger_1640995200"
        assert trigger.name == "Test Trigger"
        assert trigger.trigger_type == TriggerType.MANUAL
        assert trigger.config["param"] == "value"
        assert trigger.enabled is True
        
        # Verificar se foi adicionado ao dicionário
        assert trigger.trigger_id in automation_service.triggers
    
    def test_create_trigger_schedule(self, automation_service, mock_db):
        """Testa criação de trigger agendado"""
        with patch('time.time', return_value=1640995200):
            with patch.object(automation_service, '_setup_schedule_trigger') as mock_setup:
                trigger = automation_service.create_trigger(
                    name="Schedule Trigger",
                    trigger_type=TriggerType.SCHEDULE,
                    config={"schedule": "15:30"}
                )
        
        assert trigger.trigger_type == TriggerType.SCHEDULE
        mock_setup.assert_called_once_with(trigger)
    
    def test_create_trigger_error(self, automation_service, mock_db):
        """Testa erro na criação de trigger"""
        # Simular erro
        automation_service.triggers = None  # Causar erro
        
        with pytest.raises(Exception):
            automation_service.create_trigger(
                name="Error Trigger",
                trigger_type=TriggerType.MANUAL,
                config={}
            )
    
    def test_setup_schedule_trigger_daily(self, automation_service):
        """Testa configuração de trigger diário"""
        trigger = AutomationTrigger(
            trigger_id="daily_test",
            name="Daily Test",
            trigger_type=TriggerType.SCHEDULE,
            config={"schedule": "14:30", "timezone": "America/Sao_Paulo"}
        )
        
        with patch('schedule.every') as mock_schedule:
            automation_service._setup_schedule_trigger(trigger)
            
            # Verificar se schedule foi chamado
            mock_schedule.assert_called()
    
    def test_setup_schedule_trigger_weekly(self, automation_service):
        """Testa configuração de trigger semanal"""
        trigger = AutomationTrigger(
            trigger_id="weekly_test",
            name="Weekly Test",
            trigger_type=TriggerType.SCHEDULE,
            config={"schedule": "sunday 16:00", "timezone": "America/Sao_Paulo"}
        )
        
        with patch('schedule.every') as mock_schedule:
            automation_service._setup_schedule_trigger(trigger)
            
            # Verificar se schedule foi chamado
            mock_schedule.assert_called()
    
    def test_create_workflow(self, automation_service, mock_db):
        """Testa criação de workflow"""
        steps = [
            WorkflowStep(
                step_id="step1",
                name="Step 1",
                action="action1",
                config={}
            ),
            WorkflowStep(
                step_id="step2",
                name="Step 2",
                action="action2",
                config={},
                dependencies=["step1"]
            )
        ]
        
        workflow_id = automation_service.create_workflow("test_workflow", steps)
        
        assert workflow_id == "test_workflow"
        assert "test_workflow" in automation_service.workflows
        assert len(automation_service.workflows["test_workflow"]) == 2
    
    def test_create_workflow_error(self, automation_service, mock_db):
        """Testa erro na criação de workflow"""
        # Simular erro
        automation_service.workflows = None  # Causar erro
        
        with pytest.raises(Exception):
            automation_service.create_workflow("error_workflow", [])
    
    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, automation_service, mock_db):
        """Testa execução bem-sucedida de workflow"""
        # Criar workflow de teste
        steps = [
            WorkflowStep(
                step_id="test_step",
                name="Test Step",
                action="validate_collected_data",
                config={}
            )
        ]
        automation_service.workflows["test_workflow"] = steps
        
        with patch.object(automation_service, '_execute_step') as mock_execute:
            execution = await automation_service.execute_workflow("test_workflow")
        
        assert execution.workflow_id == "test_workflow"
        assert execution.status == WorkflowStatus.COMPLETED
        assert "test_step" in execution.steps_completed
        assert execution.end_time is not None
        mock_execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_workflow_not_found(self, automation_service, mock_db):
        """Testa execução de workflow inexistente"""
        with pytest.raises(ValueError, match="Workflow nonexistent_workflow não encontrado"):
            await automation_service.execute_workflow("nonexistent_workflow")
    
    @pytest.mark.asyncio
    async def test_execute_workflow_with_dependencies(self, automation_service, mock_db):
        """Testa execução de workflow com dependências"""
        steps = [
            WorkflowStep(
                step_id="step1",
                name="Step 1",
                action="validate_collected_data",
                config={}
            ),
            WorkflowStep(
                step_id="step2",
                name="Step 2",
                action="fill_prompts",
                config={},
                dependencies=["step1"]
            )
        ]
        automation_service.workflows["test_workflow"] = steps
        
        with patch.object(automation_service, '_execute_step') as mock_execute:
            execution = await automation_service.execute_workflow("test_workflow")
        
        assert execution.status == WorkflowStatus.COMPLETED
        assert execution.steps_completed == ["step1", "step2"]
        assert mock_execute.call_count == 2
    
    @pytest.mark.asyncio
    async def test_execute_workflow_step_failure(self, automation_service, mock_db):
        """Testa falha de passo no workflow"""
        steps = [
            WorkflowStep(
                step_id="failing_step",
                name="Failing Step",
                action="unknown_action",
                config={}
            )
        ]
        automation_service.workflows["test_workflow"] = steps
        
        execution = await automation_service.execute_workflow("test_workflow")
        
        assert execution.status == WorkflowStatus.FAILED
        assert "failing_step" in execution.steps_failed
        assert execution.error_message is not None
        assert "Ação desconhecida" in execution.error_message
    
    @pytest.mark.asyncio
    async def test_execute_workflow_with_retries(self, automation_service, mock_db):
        """Testa workflow com tentativas de retry"""
        steps = [
            WorkflowStep(
                step_id="retry_step",
                name="Retry Step",
                action="validate_collected_data",
                config={},
                max_retries=2
            )
        ]
        automation_service.workflows["test_workflow"] = steps
        
        # Simular falha na primeira execução, sucesso na segunda
        call_count = 0
        async def mock_execute_with_retry(step, execution):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary failure")
            # Sucesso na segunda tentativa
        
        with patch.object(automation_service, '_execute_step', side_effect=mock_execute_with_retry):
            execution = await automation_service.execute_workflow("test_workflow")
        
        assert execution.status == WorkflowStatus.COMPLETED
        assert "retry_step" in execution.steps_completed
        assert call_count == 2
    
    def test_check_dependencies(self, automation_service):
        """Testa verificação de dependências"""
        step = WorkflowStep(
            step_id="dependent_step",
            name="Dependent Step",
            action="test_action",
            config={},
            dependencies=["step1", "step2"]
        )
        
        # Dependências atendidas
        completed_steps = ["step1", "step2", "step3"]
        assert automation_service._check_dependencies(step, completed_steps) is True
        
        # Dependências não atendidas
        completed_steps = ["step1"]
        assert automation_service._check_dependencies(step, completed_steps) is False
        
        # Sem dependências
        step_no_deps = WorkflowStep(
            step_id="independent_step",
            name="Independent Step",
            action="test_action",
            config={}
        )
        assert automation_service._check_dependencies(step_no_deps, []) is True
    
    @pytest.mark.asyncio
    async def test_execute_step_validate_data(self, automation_service):
        """Testa execução do passo validate_collected_data"""
        step = WorkflowStep(
            step_id="validate_step",
            name="Validate Step",
            action="validate_collected_data",
            config={"strict_mode": True}
        )
        execution = WorkflowExecution(
            execution_id="test_exec",
            workflow_id="test_workflow",
            trigger_id="test_trigger",
            status=WorkflowStatus.RUNNING
        )
        
        with patch.object(automation_service, '_validate_collected_data') as mock_validate:
            await automation_service._execute_step(step, execution)
        
        mock_validate.assert_called_once_with({"strict_mode": True})
    
    @pytest.mark.asyncio
    async def test_execute_step_fill_prompts(self, automation_service):
        """Testa execução do passo fill_prompts"""
        step = WorkflowStep(
            step_id="fill_step",
            name="Fill Step",
            action="fill_prompts",
            config={"batch_size": 10}
        )
        execution = WorkflowExecution(
            execution_id="test_exec",
            workflow_id="test_workflow",
            trigger_id="test_trigger",
            status=WorkflowStatus.RUNNING
        )
        
        with patch.object(automation_service, '_fill_prompts') as mock_fill:
            await automation_service._execute_step(step, execution)
        
        mock_fill.assert_called_once_with({"batch_size": 10})
    
    @pytest.mark.asyncio
    async def test_execute_step_unknown_action(self, automation_service):
        """Testa execução de ação desconhecida"""
        step = WorkflowStep(
            step_id="unknown_step",
            name="Unknown Step",
            action="unknown_action",
            config={}
        )
        execution = WorkflowExecution(
            execution_id="test_exec",
            workflow_id="test_workflow",
            trigger_id="test_trigger",
            status=WorkflowStatus.RUNNING
        )
        
        with pytest.raises(ValueError, match="Ação desconhecida: unknown_action"):
            await automation_service._execute_step(step, execution)
    
    @pytest.mark.asyncio
    async def test_validate_collected_data(self, automation_service):
        """Testa validação de dados coletados"""
        with patch('asyncio.sleep') as mock_sleep:
            await automation_service._validate_collected_data({"strict_mode": True})
        
        mock_sleep.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_fill_prompts(self, automation_service):
        """Testa preenchimento de prompts"""
        with patch('asyncio.sleep') as mock_sleep:
            await automation_service._fill_prompts({"batch_size": 10})
        
        mock_sleep.assert_called_once_with(2)
    
    @pytest.mark.asyncio
    async def test_generate_ai_content(self, automation_service):
        """Testa geração de conteúdo com IA"""
        with patch('asyncio.sleep') as mock_sleep:
            await automation_service._generate_ai_content({"provider": "openai"})
        
        mock_sleep.assert_called_once_with(3)
    
    @pytest.mark.asyncio
    async def test_validate_generated_content(self, automation_service):
        """Testa validação de conteúdo gerado"""
        with patch('asyncio.sleep') as mock_sleep:
            await automation_service._validate_generated_content({"quality_threshold": 0.8})
        
        mock_sleep.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_backup_system_data(self, automation_service):
        """Testa backup de dados do sistema"""
        with patch('asyncio.sleep') as mock_sleep:
            await automation_service._backup_system_data({"include_logs": True})
        
        mock_sleep.assert_called_once_with(5)
    
    @pytest.mark.asyncio
    async def test_cleanup_old_files(self, automation_service):
        """Testa limpeza de arquivos antigos"""
        with patch('asyncio.sleep') as mock_sleep:
            await automation_service._cleanup_old_files({"retention_days": 30})
        
        mock_sleep.assert_called_once_with(2)
    
    @pytest.mark.asyncio
    async def test_optimize_database(self, automation_service):
        """Testa otimização de banco de dados"""
        with patch('asyncio.sleep') as mock_sleep:
            await automation_service._optimize_database({"vacuum": True})
        
        mock_sleep.assert_called_once_with(3)
    
    def test_start_scheduler(self, automation_service):
        """Testa início do agendador"""
        automation_service.start_scheduler()
        
        assert automation_service.running is True
        assert automation_service.scheduler_thread is not None
        assert automation_service.scheduler_thread.is_alive()
        
        # Limpar
        automation_service.stop_scheduler()
    
    def test_stop_scheduler(self, automation_service):
        """Testa parada do agendador"""
        automation_service.start_scheduler()
        automation_service.stop_scheduler()
        
        assert automation_service.running is False
    
    def test_get_automation_statistics(self, automation_service):
        """Testa obtenção de estatísticas de automação"""
        # Adicionar alguns dados de teste
        automation_service.triggers["test1"] = AutomationTrigger(
            trigger_id="test1",
            name="Test 1",
            trigger_type=TriggerType.MANUAL,
            config={},
            enabled=True
        )
        automation_service.triggers["test2"] = AutomationTrigger(
            trigger_id="test2",
            name="Test 2",
            trigger_type=TriggerType.MANUAL,
            config={},
            enabled=False
        )
        
        execution1 = WorkflowExecution(
            execution_id="exec1",
            workflow_id="workflow1",
            trigger_id="trigger1",
            status=WorkflowStatus.COMPLETED
        )
        execution2 = WorkflowExecution(
            execution_id="exec2",
            workflow_id="workflow2",
            trigger_id="trigger2",
            status=WorkflowStatus.FAILED
        )
        
        automation_service.executions["exec1"] = execution1
        automation_service.executions["exec2"] = execution2
        
        stats = automation_service.get_automation_statistics()
        
        assert stats["total_triggers"] == 5  # 3 padrão + 2 de teste
        assert stats["enabled_triggers"] == 4  # 3 padrão + 1 de teste
        assert stats["total_workflows"] == 2  # 2 padrão
        assert stats["total_executions"] == 2
        assert stats["completed_executions"] == 1
        assert stats["failed_executions"] == 1
        assert stats["success_rate"] == 0.5
        assert stats["scheduler_running"] is False
    
    def test_log_automation_operation(self, automation_service, mock_db):
        """Testa registro de log de operação"""
        automation_service._log_automation_operation("test_operation", "test_entity")
        
        # Verificar se log foi adicionado ao banco
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        
        # Verificar se o log adicionado é do tipo correto
        log_entry = mock_db.add.call_args[0][0]
        assert isinstance(log_entry, LogOperacao)
        assert log_entry.operacao == "automation_test_operation"
        assert "test_entity" in log_entry.detalhes


class TestAutomationServiceIntegration:
    """Testes de integração para AutomationService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def automation_service(self, mock_db):
        """Instância do AutomationService para testes"""
        return AutomationService(mock_db)
    
    @pytest.mark.asyncio
    async def test_full_automation_workflow(self, automation_service, mock_db):
        """Testa fluxo completo de automação"""
        # Criar trigger
        trigger = automation_service.create_trigger(
            name="Integration Test Trigger",
            trigger_type=TriggerType.MANUAL,
            config={"test": True}
        )
        
        # Criar workflow
        steps = [
            WorkflowStep(
                step_id="step1",
                name="Step 1",
                action="validate_collected_data",
                config={"strict_mode": True}
            ),
            WorkflowStep(
                step_id="step2",
                name="Step 2",
                action="fill_prompts",
                config={"batch_size": 5},
                dependencies=["step1"]
            )
        ]
        
        workflow_id = automation_service.create_workflow("integration_workflow", steps)
        
        # Executar workflow
        with patch.object(automation_service, '_validate_collected_data') as mock_validate:
            with patch.object(automation_service, '_fill_prompts') as mock_fill:
                execution = await automation_service.execute_workflow(workflow_id, trigger.trigger_id)
        
        # Verificar resultados
        assert execution.workflow_id == workflow_id
        assert execution.trigger_id == trigger.trigger_id
        assert execution.status == WorkflowStatus.COMPLETED
        assert execution.steps_completed == ["step1", "step2"]
        assert len(execution.steps_failed) == 0
        
        # Verificar se os métodos foram chamados
        mock_validate.assert_called_once_with({"strict_mode": True})
        mock_fill.assert_called_once_with({"batch_size": 5})


class TestAutomationServiceErrorHandling:
    """Testes de tratamento de erros para AutomationService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def automation_service(self, mock_db):
        """Instância do AutomationService para testes"""
        return AutomationService(mock_db)
    
    def test_database_error_handling(self, automation_service, mock_db):
        """Testa tratamento de erro de banco de dados"""
        # Simular erro de banco
        mock_db.add.side_effect = Exception("Database error")
        
        # Deve continuar funcionando sem quebrar
        automation_service._log_automation_operation("test", "test_entity")
        
        # Verificar se o erro foi tratado graciosamente
        assert True  # Se chegou aqui, não quebrou
    
    @pytest.mark.asyncio
    async def test_workflow_execution_error_handling(self, automation_service, mock_db):
        """Testa tratamento de erro na execução de workflow"""
        # Criar workflow que vai falhar
        steps = [
            WorkflowStep(
                step_id="error_step",
                name="Error Step",
                action="validate_collected_data",
                config={}
            )
        ]
        automation_service.workflows["error_workflow"] = steps
        
        # Simular erro no passo
        with patch.object(automation_service, '_validate_collected_data', side_effect=Exception("Step error")):
            execution = await automation_service.execute_workflow("error_workflow")
        
        assert execution.status == WorkflowStatus.FAILED
        assert "error_step" in execution.steps_failed
        assert execution.error_message is not None


class TestAutomationServicePerformance:
    """Testes de performance para AutomationService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def automation_service(self, mock_db):
        """Instância do AutomationService para testes"""
        return AutomationService(mock_db)
    
    @pytest.mark.asyncio
    async def test_multiple_workflow_executions_performance(self, automation_service, mock_db):
        """Testa performance de múltiplas execuções de workflow"""
        import time
        
        # Criar workflow simples
        steps = [
            WorkflowStep(
                step_id="fast_step",
                name="Fast Step",
                action="validate_collected_data",
                config={}
            )
        ]
        automation_service.workflows["performance_workflow"] = steps
        
        start_time = time.time()
        
        # Executar múltiplos workflows
        executions = []
        for i in range(10):
            with patch.object(automation_service, '_validate_collected_data'):
                execution = await automation_service.execute_workflow("performance_workflow")
                executions.append(execution)
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 5.0  # Menos de 5 segundos para 10 execuções
        
        # Verificar que todas foram bem-sucedidas
        for execution in executions:
            assert execution.status == WorkflowStatus.COMPLETED


if __name__ == "__main__":
    pytest.main([__file__]) 
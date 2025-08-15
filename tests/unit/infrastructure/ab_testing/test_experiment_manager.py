"""
Testes Unitários para Experiment Manager
========================================

Testes abrangentes para o gerenciador de experimentos:
- Criação com templates
- Agendamento de experimentos
- Monitoramento de saúde
- Geração de relatórios
- Limpeza automática

Author: Paulo Júnior
Date: 2024-12-19
Tracing ID: AB_TESTING_TEST_002
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from infrastructure.ab_testing.experiment_manager import (
    ExperimentManager,
    ExperimentMetrics,
    ExperimentPhase
)
from infrastructure.ab_testing.framework import (
    ABTestingFramework,
    ExperimentConfig,
    ExperimentStatus
)


class TestExperimentManager:
    """Testes para o gerenciador de experimentos"""
    
    @pytest.fixture
    def framework(self):
        """Framework de teste"""
        return ABTestingFramework(redis_config=None, enable_observability=False)
    
    @pytest.fixture
    def manager(self, framework):
        """Gerenciador de teste"""
        return ExperimentManager(
            framework=framework,
            enable_monitoring=False,
            enable_alerts=False
        )
    
    @pytest.fixture
    def sample_experiment_config(self):
        """Configuração de exemplo"""
        return {
            "name": "Teste de Botão",
            "description": "Testa diferentes cores de botão",
            "variants": {
                "control": {"color": "#007bff", "description": "Azul padrão"},
                "green": {"color": "#28a745", "description": "Verde"},
                "red": {"color": "#dc3545", "description": "Vermelho"}
            },
            "metrics": ["click_rate", "conversion_rate"],
            "traffic_allocation": 0.1,
            "min_sample_size": 100,
            "confidence_level": 0.95,
            "tags": ["ui", "conversion"]
        }
    
    def test_manager_initialization(self, manager, framework):
        """Testa inicialização do gerenciador"""
        assert manager.framework == framework
        assert manager.enable_monitoring is False
        assert manager.enable_alerts is False
        assert manager.metrics_cache == {}
        assert manager.telemetry is None
        assert manager.metrics is None
    
    def test_get_experiment_templates(self, manager):
        """Testa obtenção de templates de experimentos"""
        templates = manager.get_experiment_templates()
        
        assert isinstance(templates, dict)
        assert len(templates) > 0
        
        # Verificar templates específicos
        assert "button_color" in templates
        assert "headline_test" in templates
        assert "pricing_test" in templates
        assert "landing_page" in templates
        
        # Verificar estrutura do template
        button_template = templates["button_color"]
        assert "name" in button_template
        assert "description" in button_template
        assert "variants" in button_template
        assert "metrics" in button_template
        assert "traffic_allocation" in button_template
        assert "min_sample_size" in button_template
        assert "tags" in button_template
    
    def test_create_experiment_with_template_success(self, manager):
        """Testa criação de experimento com template"""
        experiment_id = manager.create_experiment_with_template(
            template_name="button_color",
            name="Meu Teste de Botão",
            description="Teste personalizado de cores de botão"
        )
        
        assert experiment_id is not None
        assert experiment_id in manager.framework.experiments
        
        experiment = manager.framework.experiments[experiment_id]
        assert experiment.name == "Meu Teste de Botão"
        assert experiment.description == "Teste personalizado de cores de botão"
        assert "template:button_color" in experiment.tags
        assert experiment.variants == {
            "control": {"button_color": "#007bff", "description": "Azul padrão"},
            "green": {"button_color": "#28a745", "description": "Verde"},
            "red": {"button_color": "#dc3545", "description": "Vermelho"}
        }
    
    def test_create_experiment_with_template_invalid(self, manager):
        """Testa criação com template inválido"""
        with pytest.raises(ValueError, match="Template 'invalid_template' não encontrado"):
            manager.create_experiment_with_template(
                template_name="invalid_template",
                name="Teste",
                description="Descrição"
            )
    
    def test_create_experiment_with_template_custom_config(self, manager):
        """Testa criação com configuração customizada"""
        custom_config = {
            "traffic_allocation": 0.2,
            "min_sample_size": 500,
            "tags": ["custom_tag"]
        }
        
        experiment_id = manager.create_experiment_with_template(
            template_name="button_color",
            name="Teste Customizado",
            description="Descrição",
            custom_config=custom_config
        )
        
        experiment = manager.framework.experiments[experiment_id]
        assert experiment.traffic_allocation == 0.2
        assert experiment.min_sample_size == 500
        assert "custom_tag" in experiment.tags
        assert "template:button_color" in experiment.tags
    
    @pytest.mark.asyncio
    async def test_schedule_experiment_success(self, manager, sample_experiment_config):
        """Testa agendamento bem-sucedido de experimento"""
        experiment_id = manager.framework.create_experiment(**sample_experiment_config)
        
        start_time = datetime.utcnow() + timedelta(seconds=1)
        end_time = start_time + timedelta(hours=1)
        
        result = manager.schedule_experiment(
            experiment_id=experiment_id,
            start_time=start_time,
            end_time=end_time
        )
        
        assert result is True
    
    def test_schedule_experiment_not_found(self, manager):
        """Testa agendamento de experimento inexistente"""
        start_time = datetime.utcnow() + timedelta(hours=1)
        
        with pytest.raises(ValueError, match="Experimento exp_invalid não encontrado"):
            manager.schedule_experiment(
                experiment_id="exp_invalid",
                start_time=start_time
            )
    
    def test_schedule_experiment_invalid_start_time(self, manager, sample_experiment_config):
        """Testa agendamento com horário de início inválido"""
        experiment_id = manager.framework.create_experiment(**sample_experiment_config)
        
        start_time = datetime.utcnow() - timedelta(hours=1)  # Passado
        
        with pytest.raises(ValueError, match="Horário de início deve ser no futuro"):
            manager.schedule_experiment(
                experiment_id=experiment_id,
                start_time=start_time
            )
    
    def test_schedule_experiment_invalid_end_time(self, manager, sample_experiment_config):
        """Testa agendamento com horário de fim inválido"""
        experiment_id = manager.framework.create_experiment(**sample_experiment_config)
        
        start_time = datetime.utcnow() + timedelta(hours=1)
        end_time = start_time - timedelta(hours=1)  # Antes do início
        
        with pytest.raises(ValueError, match="Horário de fim deve ser após o início"):
            manager.schedule_experiment(
                experiment_id=experiment_id,
                start_time=start_time,
                end_time=end_time
            )
    
    def test_get_experiment_health_healthy(self, manager, sample_experiment_config):
        """Testa saúde de experimento saudável"""
        experiment_id = manager.framework.create_experiment(**sample_experiment_config)
        manager.framework.activate_experiment(experiment_id)
        
        # Atribuir usuários suficientes
        for index in range(200):  # Mais que min_sample_size
            user_id = f"user_{index}"
            manager.framework.assign_user_to_variant(user_id, experiment_id)
        
        health = manager.get_experiment_health(experiment_id)
        
        assert health["experiment_id"] == experiment_id
        assert health["health_score"] >= 80
        assert health["status"] == "healthy"
        assert health["total_users"] >= 200
        assert "variant_distribution" in health
        assert "recommendations" in health
    
    def test_get_experiment_health_warning(self, manager, sample_experiment_config):
        """Testa saúde de experimento com warning"""
        experiment_id = manager.framework.create_experiment(**sample_experiment_config)
        manager.framework.activate_experiment(experiment_id)
        
        # Atribuir poucos usuários
        for index in range(50):  # Menos que min_sample_size
            user_id = f"user_{index}"
            manager.framework.assign_user_to_variant(user_id, experiment_id)
        
        health = manager.get_experiment_health(experiment_id)
        
        assert health["health_score"] < 80
        assert health["status"] in ["warning", "critical"]
        assert health["total_users"] == 50
        assert len(health["recommendations"]) > 0
    
    def test_get_experiment_health_not_found(self, manager):
        """Testa saúde de experimento inexistente"""
        with pytest.raises(ValueError, match="Experimento exp_invalid não encontrado"):
            manager.get_experiment_health("exp_invalid")
    
    def test_generate_experiment_report(self, manager, sample_experiment_config):
        """Testa geração de relatório de experimento"""
        experiment_id = manager.framework.create_experiment(**sample_experiment_config)
        manager.framework.activate_experiment(experiment_id)
        
        # Atribuir alguns usuários
        for index in range(10):
            user_id = f"user_{index}"
            manager.framework.assign_user_to_variant(user_id, experiment_id)
        
        report = manager.generate_experiment_report(experiment_id)
        
        assert report["experiment_id"] == experiment_id
        assert report["name"] == sample_experiment_config["name"]
        assert report["description"] == sample_experiment_config["description"]
        assert report["status"] == ExperimentStatus.ACTIVE.value
        assert "health" in report
        assert "analysis" in report
        assert "recommendations" in report
        assert "generated_at" in report
        assert "duration_days" in report
    
    def test_generate_experiment_report_not_found(self, manager):
        """Testa geração de relatório para experimento inexistente"""
        with pytest.raises(ValueError, match="Experimento exp_invalid não encontrado"):
            manager.generate_experiment_report("exp_invalid")
    
    def test_cleanup_old_experiments(self, manager, sample_experiment_config):
        """Testa limpeza de experimentos antigos"""
        # Criar experimento antigo
        experiment_id = manager.framework.create_experiment(**sample_experiment_config)
        experiment = manager.framework.experiments[experiment_id]
        
        # Simular experimento antigo
        experiment.status = ExperimentStatus.COMPLETED
        experiment.updated_at = datetime.utcnow() - timedelta(days=31)
        
        # Atribuir alguns usuários
        for index in range(5):
            user_id = f"user_{index}"
            manager.framework.assign_user_to_variant(user_id, experiment_id)
        
        # Verificar estado antes da limpeza
        assert len(manager.framework.experiments) == 1
        assert len(manager.framework.user_assignments) == 5
        
        # Executar limpeza
        cleaned_count = manager.cleanup_old_experiments(days_old=30)
        
        assert cleaned_count == 1
        assert len(manager.framework.experiments) == 0
        assert len(manager.framework.user_assignments) == 0
    
    def test_cleanup_old_experiments_none_to_clean(self, manager, sample_experiment_config):
        """Testa limpeza quando não há experimentos para limpar"""
        # Criar experimento recente
        experiment_id = manager.framework.create_experiment(**sample_experiment_config)
        experiment = manager.framework.experiments[experiment_id]
        experiment.status = ExperimentStatus.ACTIVE  # Não completado
        experiment.updated_at = datetime.utcnow()  # Recente
        
        cleaned_count = manager.cleanup_old_experiments(days_old=30)
        
        assert cleaned_count == 0
        assert len(manager.framework.experiments) == 1  # Ainda existe
    
    def test_get_health_recommendations_healthy(self, manager):
        """Testa recomendações para experimento saudável"""
        recommendations = manager._get_health_recommendations(
            health_score=90,
            total_users=1000,
            min_sample_size=500
        )
        
        assert len(recommendations) == 0  # Sem recomendações para experimento saudável
    
    def test_get_health_recommendations_warning(self, manager):
        """Testa recomendações para experimento com warning"""
        recommendations = manager._get_health_recommendations(
            health_score=50,
            total_users=300,
            min_sample_size=500
        )
        
        assert len(recommendations) > 0
        assert any("Aumentar tráfego" in rec for rec in recommendations)
        assert any("Verificar distribuição" in rec for rec in recommendations)
    
    def test_get_health_recommendations_critical(self, manager):
        """Testa recomendações para experimento crítico"""
        recommendations = manager._get_health_recommendations(
            health_score=30,
            total_users=100,
            min_sample_size=500
        )
        
        assert len(recommendations) > 0
        assert any("pausar experimento" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_with_significance(self, manager, sample_experiment_config):
        """Testa geração de recomendações com significância"""
        experiment_id = manager.framework.create_experiment(**sample_experiment_config)
        experiment = manager.framework.experiments[experiment_id]
        
        # Simular análise com significância
        analysis_results = {
            "treatment": {
                "is_significant": True,
                "p_value": 0.01,
                "lift": 15.5
            }
        }
        
        health = {
            "total_users": 1000,
            "status": "healthy"
        }
        
        recommendations = manager._generate_recommendations(
            experiment, analysis_results, health
        )
        
        assert len(recommendations) > 0
        assert any("significativas encontradas" in rec for rec in recommendations)
    
    def test_generate_recommendations_no_significance(self, manager, sample_experiment_config):
        """Testa geração de recomendações sem significância"""
        experiment_id = manager.framework.create_experiment(**sample_experiment_config)
        experiment = manager.framework.experiments[experiment_id]
        
        # Simular análise sem significância
        analysis_results = {
            "treatment": {
                "is_significant": False,
                "p_value": 0.5,
                "lift": 2.0
            }
        }
        
        health = {
            "total_users": 1000,
            "status": "healthy"
        }
        
        recommendations = manager._generate_recommendations(
            experiment, analysis_results, health
        )
        
        assert len(recommendations) > 0
        assert any("diferença significativa" in rec for rec in recommendations)
    
    def test_generate_recommendations_small_sample(self, manager, sample_experiment_config):
        """Testa geração de recomendações com amostra pequena"""
        experiment_id = manager.framework.create_experiment(**sample_experiment_config)
        experiment = manager.framework.experiments[experiment_id]
        
        analysis_results = {}
        health = {
            "total_users": 100,
            "status": "warning"
        }
        
        recommendations = manager._generate_recommendations(
            experiment, analysis_results, health
        )
        
        assert len(recommendations) > 0
        assert any("Continuar coleta de dados" in rec for rec in recommendations)
    
    def test_save_report(self, manager):
        """Testa salvamento de relatório"""
        experiment_id = "exp_123"
        report = {"test": "data"}
        
        # Não deve gerar erro
        manager._save_report(experiment_id, report)
    
    def test_archive_experiment_data(self, manager):
        """Testa arquivamento de dados"""
        experiment_id = "exp_123"
        
        # Não deve gerar erro
        manager._archive_experiment_data(experiment_id)
    
    def test_send_alert(self, manager):
        """Testa envio de alerta"""
        experiment_id = "exp_123"
        severity = "CRITICAL"
        data = {"health_score": 30}
        
        # Não deve gerar erro
        manager._send_alert(experiment_id, severity, data)
    
    @patch('infrastructure.ab_testing.experiment_manager.asyncio')
    def test_schedule_activation_success(self, mock_asyncio, manager, sample_experiment_config):
        """Testa agendamento de ativação bem-sucedido"""
        experiment_id = manager.framework.create_experiment(**sample_experiment_config)
        
        # Mock do asyncio
        mock_task = Mock()
        mock_asyncio.create_task.return_value = mock_task
        
        start_time = datetime.utcnow() + timedelta(seconds=1)
        
        result = manager.schedule_experiment(
            experiment_id=experiment_id,
            start_time=start_time
        )
        
        assert result is True
        mock_asyncio.create_task.assert_called()
    
    @patch('infrastructure.ab_testing.experiment_manager.asyncio')
    def test_schedule_deactivation_success(self, mock_asyncio, manager, sample_experiment_config):
        """Testa agendamento de desativação bem-sucedido"""
        experiment_id = manager.framework.create_experiment(**sample_experiment_config)
        
        # Mock do asyncio
        mock_task = Mock()
        mock_asyncio.create_task.return_value = mock_task
        
        start_time = datetime.utcnow() + timedelta(seconds=1)
        end_time = start_time + timedelta(hours=1)
        
        result = manager.schedule_experiment(
            experiment_id=experiment_id,
            start_time=start_time,
            end_time=end_time
        )
        
        assert result is True
        # Deve criar duas tasks: uma para ativação e uma para desativação
        assert mock_asyncio.create_task.call_count == 2


class TestExperimentMetrics:
    """Testes para a classe ExperimentMetrics"""
    
    def test_experiment_metrics_creation(self):
        """Testa criação de ExperimentMetrics"""
        metrics = ExperimentMetrics(
            experiment_id="exp_123",
            total_users=1000,
            conversions={"control": 50, "treatment": 60},
            conversion_rates={"control": 0.05, "treatment": 0.06},
            revenue={"control": 500.0, "treatment": 600.0},
            avg_session_duration={"control": 120.0, "treatment": 150.0},
            bounce_rate={"control": 0.3, "treatment": 0.25},
            last_updated=datetime.utcnow()
        )
        
        assert metrics.experiment_id == "exp_123"
        assert metrics.total_users == 1000
        assert metrics.conversions["control"] == 50
        assert metrics.conversion_rates["treatment"] == 0.06
        assert metrics.revenue["treatment"] == 600.0


class TestExperimentPhase:
    """Testes para o enum ExperimentPhase"""
    
    def test_experiment_phase_values(self):
        """Testa valores do enum ExperimentPhase"""
        assert ExperimentPhase.SETUP.value == "setup"
        assert ExperimentPhase.RUNNING.value == "running"
        assert ExperimentPhase.ANALYSIS.value == "analysis"
        assert ExperimentPhase.DECISION.value == "decision"
        assert ExperimentPhase.COMPLETED.value == "completed"
    
    def test_experiment_phase_comparison(self):
        """Testa comparação de fases"""
        assert ExperimentPhase.SETUP != ExperimentPhase.RUNNING
        assert ExperimentPhase.RUNNING == ExperimentPhase.RUNNING 
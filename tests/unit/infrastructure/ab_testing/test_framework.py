"""
Testes Unitários para Framework de A/B Testing
==============================================

Testes abrangentes para o framework de A/B Testing:
- Criação e gerenciamento de experimentos
- Atribuição de usuários
- Tracking de conversões
- Análise estatística
- Integração com Redis e observabilidade

Author: Paulo Júnior
Date: 2024-12-19
Tracing ID: AB_TESTING_TEST_001
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from infrastructure.ab_testing.framework import (
    ABTestingFramework,
    ExperimentConfig,
    ExperimentStatus,
    UserAssignment,
    ExperimentResult
)


class TestABTestingFramework:
    """Testes para o framework principal de A/B Testing"""
    
    @pytest.fixture
    def framework(self):
        """Framework de teste sem Redis"""
        return ABTestingFramework(redis_config=None, enable_observability=False)
    
    @pytest.fixture
    def sample_experiment_config(self):
        """Configuração de exemplo para experimento"""
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
    
    def test_framework_initialization(self, framework):
        """Testa inicialização do framework"""
        assert framework is not None
        assert framework.experiments == {}
        assert framework.user_assignments == {}
        assert framework.results_cache == {}
        assert framework.redis_client is None
    
    def test_create_experiment_success(self, framework, sample_experiment_config):
        """Testa criação bem-sucedida de experimento"""
        experiment_id = framework.create_experiment(
            name=sample_experiment_config["name"],
            description=sample_experiment_config["description"],
            variants=sample_experiment_config["variants"],
            metrics=sample_experiment_config["metrics"],
            traffic_allocation=sample_experiment_config["traffic_allocation"],
            min_sample_size=sample_experiment_config["min_sample_size"],
            confidence_level=sample_experiment_config["confidence_level"],
            tags=sample_experiment_config["tags"]
        )
        
        assert experiment_id is not None
        assert experiment_id in framework.experiments
        
        experiment = framework.experiments[experiment_id]
        assert experiment.name == sample_experiment_config["name"]
        assert experiment.description == sample_experiment_config["description"]
        assert experiment.status == ExperimentStatus.DRAFT
        assert experiment.variants == sample_experiment_config["variants"]
        assert experiment.metrics == sample_experiment_config["metrics"]
        assert experiment.traffic_allocation == sample_experiment_config["traffic_allocation"]
        assert experiment.min_sample_size == sample_experiment_config["min_sample_size"]
        assert experiment.confidence_level == sample_experiment_config["confidence_level"]
        assert experiment.tags == sample_experiment_config["tags"]
    
    def test_create_experiment_invalid_variants(self, framework):
        """Testa criação com variantes inválidas"""
        with pytest.raises(ValueError, match="Deve haver pelo menos uma variante 'control'"):
            framework.create_experiment(
                name="Teste",
                description="Descrição",
                variants={"treatment": {"color": "red"}},
                metrics=["conversion_rate"]
            )
    
    def test_create_experiment_invalid_traffic_allocation(self, framework):
        """Testa criação com alocação de tráfego inválida"""
        with pytest.raises(ValueError, match="traffic_allocation deve estar entre 0 e 1"):
            framework.create_experiment(
                name="Teste",
                description="Descrição",
                variants={"control": {"color": "blue"}},
                metrics=["conversion_rate"],
                traffic_allocation=1.5
            )
    
    def test_create_experiment_invalid_confidence_level(self, framework):
        """Testa criação com nível de confiança inválido"""
        with pytest.raises(ValueError, match="confidence_level deve estar entre 0 e 1"):
            framework.create_experiment(
                name="Teste",
                description="Descrição",
                variants={"control": {"color": "blue"}},
                metrics=["conversion_rate"],
                confidence_level=1.5
            )
    
    def test_create_experiment_empty_metrics(self, framework, sample_experiment_config):
        """Testa criação de experimento com lista de métricas vazia"""
        config = sample_experiment_config.copy()
        config["metrics"] = []
        with pytest.raises(ValueError, match="Deve haver pelo menos uma métrica"):
            framework.create_experiment(**config)

    def test_create_experiment_empty_variants(self, framework, sample_experiment_config):
        """Testa criação de experimento com variantes vazias"""
        config = sample_experiment_config.copy()
        config["variants"] = {}
        with pytest.raises(ValueError, match="Deve haver pelo menos uma variante 'control'"):
            framework.create_experiment(**config)
    
    def test_activate_experiment_success(self, framework, sample_experiment_config):
        """Testa ativação bem-sucedida de experimento"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        
        result = framework.activate_experiment(experiment_id)
        
        assert result is True
        assert framework.experiments[experiment_id].status == ExperimentStatus.ACTIVE
    
    def test_activate_experiment_not_found(self, framework):
        """Testa ativação de experimento inexistente"""
        with pytest.raises(ValueError, match="Experimento exp_invalid não encontrado"):
            framework.activate_experiment("exp_invalid")
    
    def test_activate_experiment_wrong_status(self, framework, sample_experiment_config):
        """Testa ativação de experimento com status incorreto"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        
        # Tentar ativar novamente
        with pytest.raises(ValueError, match="Experimento deve estar em DRAFT para ativação"):
            framework.activate_experiment(experiment_id)
    
    def test_assign_user_to_variant_success(self, framework, sample_experiment_config):
        """Testa atribuição bem-sucedida de usuário"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        
        user_id = "user_123"
        variant = framework.assign_user_to_variant(user_id, experiment_id)
        
        assert variant is not None
        assert variant in sample_experiment_config["variants"]
        
        # Verificar se atribuição foi registrada
        assignment_key = f"{user_id}:{experiment_id}"
        assert assignment_key in framework.user_assignments
        
        assignment = framework.user_assignments[assignment_key]
        assert assignment.user_id == user_id
        assert assignment.experiment_id == experiment_id
        assert assignment.variant == variant
    
    def test_assign_user_to_variant_consistent(self, framework, sample_experiment_config):
        """Testa consistência na atribuição de usuários"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        
        user_id = "user_456"
        
        # Primeira atribuição
        variant1 = framework.assign_user_to_variant(user_id, experiment_id)
        
        # Segunda atribuição (deve ser a mesma)
        variant2 = framework.assign_user_to_variant(user_id, experiment_id)
        
        assert variant1 == variant2
    
    def test_assign_user_to_variant_experiment_not_found(self, framework):
        """Testa atribuição com experimento inexistente"""
        variant = framework.assign_user_to_variant("user_123", "exp_invalid")
        assert variant is None
    
    def test_assign_user_to_variant_inactive_experiment(self, framework, sample_experiment_config):
        """Testa atribuição com experimento inativo"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        # Não ativar o experimento
        
        variant = framework.assign_user_to_variant("user_123", experiment_id)
        assert variant is None
    
    def test_assign_user_to_variant_race_condition(self, framework, sample_experiment_config):
        """Testa concorrência na atribuição de usuários (race condition)"""
        import threading
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        user_id = "user_race"
        results = []
        def assign():
            results.append(framework.assign_user_to_variant(user_id, experiment_id))
        threads = [threading.Thread(target=assign) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        # Todos devem receber a mesma variante
        assert all(v == results[0] for v in results)

    def test_track_conversion_success(self, framework, sample_experiment_config):
        """Testa tracking bem-sucedido de conversão"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        
        user_id = "user_789"
        framework.assign_user_to_variant(user_id, experiment_id)
        
        result = framework.track_conversion(
            user_id=user_id,
            experiment_id=experiment_id,
            metric_name="conversion_rate",
            value=1.0
        )
        
        assert result is True
    
    def test_track_conversion_user_not_assigned(self, framework, sample_experiment_config):
        """Testa tracking de conversão para usuário não atribuído"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        
        result = framework.track_conversion(
            user_id="user_not_assigned",
            experiment_id=experiment_id,
            metric_name="conversion_rate",
            value=1.0
        )
        
        assert result is False
    
    def test_track_conversion_invalid_metric(self, framework, sample_experiment_config):
        """Testa tracking de conversão com métrica inválida"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        user_id = "user_invalid_metric"
        framework.assign_user_to_variant(user_id, experiment_id)
        # Métrica não cadastrada
        with pytest.raises(ValueError, match="Métrica não cadastrada"):
            framework.track_conversion(user_id, experiment_id, "invalid_metric", 1)
    
    def test_analyze_experiment_no_data(self, framework, sample_experiment_config):
        """Testa análise de experimento sem dados"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        
        results = framework.analyze_experiment(experiment_id)
        
        assert "error" in results
        assert "Sem dados de conversão suficientes" in results["error"]
    
    def test_get_experiment_summary(self, framework, sample_experiment_config):
        """Testa obtenção de resumo do experimento"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        
        # Atribuir alguns usuários
        for index in range(10):
            user_id = f"user_{index}"
            framework.assign_user_to_variant(user_id, experiment_id)
        
        summary = framework.get_experiment_summary(experiment_id)
        
        assert summary["experiment_id"] == experiment_id
        assert summary["name"] == sample_experiment_config["name"]
        assert summary["status"] == ExperimentStatus.ACTIVE.value
        assert "variant_counts" in summary
        assert len(summary["variant_counts"]) > 0
    
    def test_list_experiments_no_filters(self, framework, sample_experiment_config):
        """Testa listagem de experimentos sem filtros"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        
        experiments = framework.list_experiments()
        
        assert len(experiments) == 1
        assert experiments[0]["experiment_id"] == experiment_id
    
    def test_list_experiments_with_status_filter(self, framework, sample_experiment_config):
        """Testa listagem de experimentos com filtro de status"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        
        # Filtrar por status ativo
        active_experiments = framework.list_experiments(status=ExperimentStatus.ACTIVE)
        assert len(active_experiments) == 1
        assert active_experiments[0]["experiment_id"] == experiment_id
        
        # Filtrar por status draft (não deve encontrar)
        draft_experiments = framework.list_experiments(status=ExperimentStatus.DRAFT)
        assert len(draft_experiments) == 0
    
    def test_list_experiments_with_tags_filter(self, framework, sample_experiment_config):
        """Testa listagem de experimentos com filtro de tags"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        
        # Filtrar por tag existente
        ui_experiments = framework.list_experiments(tags=["ui"])
        assert len(ui_experiments) == 1
        assert ui_experiments[0]["experiment_id"] == experiment_id
        
        # Filtrar por tag inexistente
        invalid_experiments = framework.list_experiments(tags=["invalid_tag"])
        assert len(invalid_experiments) == 0
    
    def test_calculate_confidence_interval(self, framework):
        """Testa cálculo de intervalo de confiança"""
        mean = 0.15
        std_dev = 0.05
        sample_size = 100
        confidence_level = 0.95
        
        interval = framework._calculate_confidence_interval(
            mean, std_dev, sample_size, confidence_level
        )
        
        assert len(interval) == 2
        assert interval[0] < mean < interval[1]
        assert interval[0] > 0  # Limite inferior deve ser positivo
    
    def test_calculate_confidence_interval_small_sample(self, framework):
        """Testa cálculo com amostra pequena"""
        mean = 0.15
        std_dev = 0.05
        sample_size = 1
        confidence_level = 0.95
        
        interval = framework._calculate_confidence_interval(
            mean, std_dev, sample_size, confidence_level
        )
        
        assert interval == (mean, mean)  # Deve retornar a média para amostra pequena
    
    def test_get_consistent_variant(self, framework, sample_experiment_config):
        """Testa atribuição consistente de variantes"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        experiment = framework.experiments[experiment_id]
        
        user_id = "user_consistent"
        
        # Múltiplas chamadas devem retornar a mesma variante
        variant1 = framework._get_consistent_variant(
            user_id, experiment_id, experiment.variants
        )
        variant2 = framework._get_consistent_variant(
            user_id, experiment_id, experiment.variants
        )
        
        assert variant1 == variant2
        assert variant1 in experiment.variants
    
    def test_should_include_user_traffic_allocation(self, framework):
        """Testa inclusão de usuário baseada na alocação de tráfego"""
        user_id = "user_traffic"
        
        # Testar com 100% de alocação
        result_100 = framework._should_include_user(user_id, 1.0)
        assert result_100 is True
        
        # Testar com 0% de alocação
        result_0 = framework._should_include_user(user_id, 0.0)
        assert result_0 is False
        
        # Testar com 50% de alocação (pode variar)
        result_50 = framework._should_include_user(user_id, 0.5)
        assert isinstance(result_50, bool)
    
    def test_user_matches_segment_all_users(self, framework):
        """Testa segmentação com regra 'todos os usuários'"""
        user_id = "user_segment"
        segment_rules = {"all_users": True}
        
        result = framework._user_matches_segment(user_id, segment_rules, None)
        assert result is True
    
    def test_user_matches_segment_no_rules(self, framework):
        """Testa segmentação sem regras"""
        user_id = "user_segment"
        segment_rules = {}
        
        result = framework._user_matches_segment(user_id, segment_rules, None)
        assert result is True
    
    @patch('infrastructure.ab_testing.framework.redis')
    def test_framework_with_redis(self, mock_redis):
        """Testa framework com Redis configurado"""
        # Mock do Redis
        mock_redis_client = Mock()
        mock_redis.Redis.return_value = mock_redis_client
        mock_redis_client.ping.return_value = True
        
        framework = ABTestingFramework(
            redis_config={"host": "localhost", "port": 6379},
            enable_observability=False
        )
        
        assert framework.redis_client is not None
        mock_redis.Redis.assert_called_once()
    
    @patch('infrastructure.ab_testing.framework.redis')
    def test_framework_redis_connection_failure(self, mock_redis):
        """Testa framework com falha na conexão Redis"""
        # Mock do Redis com falha
        mock_redis.Redis.side_effect = Exception("Connection failed")
        
        framework = ABTestingFramework(
            redis_config={"host": "localhost", "port": 6379},
            enable_observability=False
        )
        
        assert framework.redis_client is None
    
    def test_framework_thread_safety(self, framework, sample_experiment_config):
        """Testa thread safety do framework"""
        import threading
        import time
        
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        
        results = []
        errors = []
        
        def assign_users():
            try:
                for index in range(10):
                    user_id = f"thread_user_{threading.current_thread().ident}_{index}"
                    variant = framework.assign_user_to_variant(user_id, experiment_id)
                    results.append(variant)
                    time.sleep(0.001)  # Pequena pausa para simular concorrência
            except Exception as e:
                errors.append(e)
        
        # Criar múltiplas threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=assign_users)
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads
        for thread in threads:
            thread.join()
        
        # Verificar se não houve erros
        assert len(errors) == 0
        assert len(results) == 50  # 5 threads * 10 usuários cada
        
        # Verificar se todas as atribuições foram registradas
        assert len(framework.user_assignments) == 50
    
    def test_framework_cleanup(self, framework, sample_experiment_config):
        """Testa cleanup do framework"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        
        # Atribuir alguns usuários
        for index in range(5):
            user_id = f"user_{index}"
            framework.assign_user_to_variant(user_id, experiment_id)
        
        # Verificar estado antes do cleanup
        assert len(framework.experiments) == 1
        assert len(framework.user_assignments) == 5
        
        # Cleanup (simulado)
        del framework
        
        # Framework deve ser destruído sem erros

    @patch('infrastructure.ab_testing.framework.redis')
    def test_framework_observability_metrics(self, mock_redis, sample_experiment_config):
        """Testa integração com observabilidade e Redis (métricas/logs)"""
        # Simula Redis e observabilidade habilitada
        framework = ABTestingFramework(redis_config={"host": "localhost"}, enable_observability=True)
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        user_id = "user_obs"
        variant = framework.assign_user_to_variant(user_id, experiment_id)
        # Simula tracking e coleta de métricas
        framework.track_conversion(user_id, experiment_id, "conversion_rate", 1)
        # Verifica se atributos de observabilidade estão presentes
        assert hasattr(framework, "metrics")
        assert hasattr(framework, "telemetry")
        assert hasattr(framework, "tracing")
        # Se disponíveis, simula uso real dos métodos públicos
        if framework.metrics:
            framework.metrics.record_execution("ab_test", "success", duration=0.1)
        if framework.telemetry:
            framework.telemetry.log_event("test", "ok", extra_data={"context": "ab_test"})
        if framework.tracing:
            with framework.tracing.trace_span("ab_test_span"):
                pass
        # Simula falha de Redis
        mock_redis.Redis.side_effect = Exception("Redis indisponível")
        with pytest.raises(Exception):
            ABTestingFramework(redis_config={"host": "localhost"}, enable_observability=True)

    def test_assign_user_to_variant_invalid_user(self, framework, sample_experiment_config):
        """Testa atribuição de usuário inválido (None ou vazio)"""
        experiment_id = framework.create_experiment(**sample_experiment_config)
        framework.activate_experiment(experiment_id)
        for invalid_user in [None, ""]:
            variant = framework.assign_user_to_variant(invalid_user, experiment_id)
            assert variant is None


class TestExperimentConfig:
    """Testes para a classe ExperimentConfig"""
    
    def test_experiment_config_creation(self):
        """Testa criação de ExperimentConfig"""
        config = ExperimentConfig(
            experiment_id="exp_123",
            name="Teste",
            description="Descrição",
            status=ExperimentStatus.DRAFT,
            start_date=datetime.utcnow(),
            end_date=None,
            traffic_allocation=0.1,
            variants={"control": {"color": "blue"}},
            metrics=["conversion_rate"],
            segment_rules={},
            min_sample_size=100,
            confidence_level=0.95,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="test_user",
            tags=["test"]
        )
        
        assert config.experiment_id == "exp_123"
        assert config.name == "Teste"
        assert config.status == ExperimentStatus.DRAFT
        assert config.traffic_allocation == 0.1
        assert config.min_sample_size == 100
        assert config.confidence_level == 0.95


class TestUserAssignment:
    """Testes para a classe UserAssignment"""
    
    def test_user_assignment_creation(self):
        """Testa criação de UserAssignment"""
        assignment = UserAssignment(
            user_id="user_123",
            experiment_id="exp_456",
            variant="control",
            assigned_at=datetime.utcnow(),
            session_id="session_789"
        )
        
        assert assignment.user_id == "user_123"
        assert assignment.experiment_id == "exp_456"
        assert assignment.variant == "control"
        assert assignment.session_id == "session_789"


class TestExperimentStatus:
    """Testes para o enum ExperimentStatus"""
    
    def test_experiment_status_values(self):
        """Testa valores do enum ExperimentStatus"""
        assert ExperimentStatus.DRAFT.value == "draft"
        assert ExperimentStatus.ACTIVE.value == "active"
        assert ExperimentStatus.PAUSED.value == "paused"
        assert ExperimentStatus.COMPLETED.value == "completed"
        assert ExperimentStatus.ARCHIVED.value == "archived"
    
    def test_experiment_status_comparison(self):
        """Testa comparação de status"""
        assert ExperimentStatus.DRAFT != ExperimentStatus.ACTIVE
        assert ExperimentStatus.ACTIVE == ExperimentStatus.ACTIVE 
"""
Testes Unitários para Exemplo de A/B Testing
============================================

Testes abrangentes para o exemplo prático de A/B Testing:
- Criação de experimentos
- Simulação de tráfego
- Análise de resultados
- Geração de relatórios
- Verificação de saúde

Author: Paulo Júnior
Date: 2024-12-19
Tracing ID: AB_TESTING_EXAMPLE_TEST_001
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from examples.ab_testing_example import ABTestingExample


class TestABTestingExample:
    """Testes para o exemplo de A/B Testing"""
    
    @pytest.fixture
    def example(self):
        """Exemplo de teste"""
        return ABTestingExample()
    
    @pytest.fixture
    def temp_dir(self):
        """Diretório temporário para testes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_example_initialization(self, example):
        """Testa inicialização do exemplo"""
        assert example.framework is not None
        assert example.manager is not None
        assert example.analytics is not None
        assert example.simulated_users == []
        assert example.conversion_events == []
    
    def test_create_button_color_experiment(self, example):
        """Testa criação de experimento de cor de botão"""
        experiment_id = example.create_button_color_experiment()
        
        assert experiment_id is not None
        assert experiment_id in example.framework.experiments
        
        experiment = example.framework.experiments[experiment_id]
        assert experiment.name == "Teste de Cor de Botão"
        assert "button_color" in experiment.tags
        assert "control" in experiment.variants
        assert "green" in experiment.variants
        assert "red" in experiment.variants
        assert experiment.traffic_allocation == 0.1
        assert experiment.min_sample_size == 100
    
    def test_create_headline_experiment(self, example):
        """Testa criação de experimento de headline"""
        experiment_id = example.create_headline_experiment()
        
        assert experiment_id is not None
        assert experiment_id in example.framework.experiments
        
        experiment = example.framework.experiments[experiment_id]
        assert experiment.name == "Teste de Headline"
        assert "headline_test" in experiment.tags
        assert "control" in experiment.variants
        assert "benefit" in experiment.variants
        assert "urgency" in experiment.variants
        assert experiment.traffic_allocation == 0.15
        assert experiment.min_sample_size == 150
    
    def test_create_pricing_experiment(self, example):
        """Testa criação de experimento de preços"""
        experiment_id = example.create_pricing_experiment()
        
        assert experiment_id is not None
        assert experiment_id in example.framework.experiments
        
        experiment = example.framework.experiments[experiment_id]
        assert experiment.name == "Teste de Estratégia de Preços"
        assert "pricing" in experiment.tags
        assert "control" in experiment.variants
        assert "higher" in experiment.variants
        assert "lower" in experiment.variants
        assert experiment.traffic_allocation == 0.05
        assert experiment.min_sample_size == 500
    
    def test_activate_experiments(self, example):
        """Testa ativação de experimentos"""
        # Criar experimentos
        experiment_ids = []
        experiment_ids.append(example.create_button_color_experiment())
        experiment_ids.append(example.create_headline_experiment())
        
        # Ativar
        example.activate_experiments(experiment_ids)
        
        # Verificar se foram ativados
        for experiment_id in experiment_ids:
            experiment = example.framework.experiments[experiment_id]
            assert experiment.status.value == "active"
    
    def test_activate_experiments_with_error(self, example):
        """Testa ativação com erro"""
        # Tentar ativar experimento inexistente
        with patch('builtins.print') as mock_print:
            example.activate_experiments(["invalid_id"])
            
            # Verificar que erro foi logado
            mock_print.assert_called()
            call_args = [call[0][0] for call in mock_print.call_args_list]
            assert any("❌ Erro ao ativar" in str(call) for call in call_args)
    
    def test_simulate_user_traffic(self, example):
        """Testa simulação de tráfego de usuários"""
        # Criar e ativar experimento
        experiment_id = example.create_button_color_experiment()
        example.activate_experiments([experiment_id])
        
        # Simular tráfego
        users, conversions = example.simulate_user_traffic(
            experiment_ids=[experiment_id],
            num_users=100,
            duration_minutes=1
        )
        
        assert users > 0
        assert conversions >= 0
        assert conversions <= users
        
        # Verificar se usuários foram simulados
        assert len(example.simulated_users) > 0
        assert len(example.conversion_events) > 0
    
    def test_simulate_user_traffic_multiple_experiments(self, example):
        """Testa simulação com múltiplos experimentos"""
        # Criar e ativar experimentos
        experiment_ids = []
        experiment_ids.append(example.create_button_color_experiment())
        experiment_ids.append(example.create_headline_experiment())
        example.activate_experiments(experiment_ids)
        
        # Simular tráfego
        users, conversions = example.simulate_user_traffic(
            experiment_ids=experiment_ids,
            num_users=200,
            duration_minutes=2
        )
        
        assert users > 0
        assert conversions >= 0
        
        # Verificar se todos os experimentos receberam tráfego
        for experiment_id in experiment_ids:
            experiment = example.framework.experiments[experiment_id]
            # Verificar se há atribuições de usuários
            user_assignments = [
                assignment for assignment in example.framework.user_assignments.values()
                if assignment.experiment_id == experiment_id
            ]
            assert len(user_assignments) > 0
    
    def test_get_conversion_probability(self, example):
        """Testa cálculo de probabilidade de conversão"""
        # Criar experimento
        experiment_id = example.create_button_color_experiment()
        
        # Testar probabilidades
        control_prob = example._get_conversion_probability("control", experiment_id)
        green_prob = example._get_conversion_probability("green", experiment_id)
        red_prob = example._get_conversion_probability("red", experiment_id)
        
        assert 0 <= control_prob <= 1
        assert 0 <= green_prob <= 1
        assert 0 <= red_prob <= 1
        
        # Verificar que green tem probabilidade maior que control
        assert green_prob > control_prob
        
        # Verificar que red tem probabilidade menor que control
        assert red_prob < control_prob
    
    def test_get_conversion_probability_pricing(self, example):
        """Testa probabilidade para experimento de preços"""
        # Criar experimento de preços
        experiment_id = example.create_pricing_experiment()
        
        # Testar probabilidades
        control_prob = example._get_conversion_probability("control", experiment_id)
        higher_prob = example._get_conversion_probability("higher", experiment_id)
        lower_prob = example._get_conversion_probability("lower", experiment_id)
        
        assert 0 <= control_prob <= 1
        assert 0 <= higher_prob <= 1
        assert 0 <= lower_prob <= 1
        
        # Verificar que preço menor tem probabilidade maior
        assert lower_prob > control_prob
        
        # Verificar que preço maior tem probabilidade menor
        assert higher_prob < control_prob
    
    def test_simulate_additional_metrics(self, example):
        """Testa simulação de métricas adicionais"""
        # Criar e ativar experimento
        experiment_id = example.create_button_color_experiment()
        example.activate_experiments([experiment_id])
        
        user_id = "test_user"
        variant = "control"
        
        # Simular métricas
        example._simulate_additional_metrics(user_id, experiment_id, variant)
        
        # Verificar se métricas foram registradas
        # (Note: isso depende da implementação interna do framework)
        assert len(example.conversion_events) > 0
    
    def test_analyze_experiments(self, example):
        """Testa análise de experimentos"""
        # Criar e ativar experimento
        experiment_id = example.create_button_color_experiment()
        example.activate_experiments([experiment_id])
        
        # Simular dados
        with patch.object(example.analytics, 'analyze_experiment_statistical') as mock_analyze:
            mock_analyze.return_value = {
                "experiment_id": experiment_id,
                "variant_analyses": {
                    "control": {
                        "sample_size": 50,
                        "conversion_rate": 0.05,
                        "mean_value": 1.0,
                        "confidence_interval": (0.03, 0.07)
                    },
                    "green": {
                        "sample_size": 50,
                        "conversion_rate": 0.06,
                        "mean_value": 1.2,
                        "confidence_interval": (0.04, 0.08)
                    }
                },
                "statistical_results": {
                    "green": {
                        "p_value": 0.03,
                        "is_significant": True,
                        "lift": 20.0,
                        "power": 0.85
                    }
                },
                "overall_analysis": {
                    "total_users": 100,
                    "best_variant": "green",
                    "best_lift": 20.0,
                    "significant_variants": ["green"],
                    "recommendation": "Implementar variante green"
                }
            }
            
            with patch('builtins.print') as mock_print:
                example.analyze_experiments([experiment_id])
                
                # Verificar que análise foi executada
                mock_analyze.assert_called_once_with(experiment_id)
                
                # Verificar que resultados foram impressos
                mock_print.assert_called()
    
    def test_analyze_experiments_with_error(self, example):
        """Testa análise com erro"""
        # Criar experimento
        experiment_id = example.create_button_color_experiment()
        
        # Simular erro na análise
        with patch.object(example.analytics, 'analyze_experiment_statistical') as mock_analyze:
            mock_analyze.return_value = {"error": "Sem dados suficientes"}
            
            with patch('builtins.print') as mock_print:
                example.analyze_experiments([experiment_id])
                
                # Verificar que erro foi logado
                mock_print.assert_called()
                call_args = [call[0][0] for call in mock_print.call_args_list]
                assert any("❌ Erro na análise" in str(call) for call in call_args)
    
    def test_generate_reports(self, example, temp_dir):
        """Testa geração de relatórios"""
        # Criar experimento
        experiment_id = example.create_button_color_experiment()
        
        # Mock dos relatórios
        manager_report = {"type": "manager", "experiment_id": experiment_id}
        analytics_report = {"type": "analytics", "experiment_id": experiment_id}
        
        with patch.object(example.manager, 'generate_experiment_report') as mock_manager:
            with patch.object(example.analytics, 'generate_report') as mock_analytics:
                mock_manager.return_value = manager_report
                mock_analytics.return_value = analytics_report
                
                with patch.object(example, '_save_report') as mock_save:
                    with patch('builtins.print') as mock_print:
                        example.generate_reports([experiment_id])
                        
                        # Verificar que relatórios foram gerados
                        mock_manager.assert_called_once_with(experiment_id)
                        mock_analytics.assert_called_once_with(experiment_id)
                        
                        # Verificar que foram salvos
                        assert mock_save.call_count == 2
                        
                        # Verificar que sucesso foi logado
                        mock_print.assert_called()
                        call_args = [call[0][0] for call in mock_print.call_args_list]
                        assert any("✅ Relatórios salvos" in str(call) for call in call_args)
    
    def test_save_report(self, example, temp_dir):
        """Testa salvamento de relatório"""
        # Mudar para diretório temporário
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Criar relatório
            report = {"test": "data", "experiment_id": "test_exp"}
            
            # Salvar
            example._save_report("test_exp", report, "test")
            
            # Verificar se arquivo foi criado
            filename = "reports/test_exp_test_report.json"
            assert os.path.exists(filename)
            
            # Verificar conteúdo
            with open(filename, 'r', encoding='utf-8') as f:
                saved_report = json.load(f)
            
            assert saved_report["test"] == "data"
            assert saved_report["experiment_id"] == "test_exp"
            
        finally:
            os.chdir(original_cwd)
    
    def test_show_experiment_health(self, example):
        """Testa verificação de saúde dos experimentos"""
        # Criar experimento
        experiment_id = example.create_button_color_experiment()
        
        # Mock da saúde
        health_data = {
            "health_score": 85,
            "status": "healthy",
            "total_users": 150,
            "min_sample_size": 100,
            "variant_distribution": {"control": 75, "green": 75},
            "recommendations": ["Continuar experimento", "Monitorar conversões"]
        }
        
        with patch.object(example.manager, 'get_experiment_health') as mock_health:
            mock_health.return_value = health_data
            
            with patch('builtins.print') as mock_print:
                example.show_experiment_health([experiment_id])
                
                # Verificar que saúde foi verificada
                mock_health.assert_called_once_with(experiment_id)
                
                # Verificar que resultados foram impressos
                mock_print.assert_called()
                call_args = [call[0][0] for call in mock_print.call_args_list]
                assert any("Score: 85/100" in str(call) for call in call_args)
    
    def test_run_complete_example(self, example):
        """Testa execução do exemplo completo"""
        with patch.object(example, 'create_button_color_experiment') as mock_button:
            with patch.object(example, 'create_headline_experiment') as mock_headline:
                with patch.object(example, 'create_pricing_experiment') as mock_pricing:
                    with patch.object(example, 'activate_experiments') as mock_activate:
                        with patch.object(example, 'simulate_user_traffic') as mock_simulate:
                            with patch.object(example, 'show_experiment_health') as mock_health:
                                with patch.object(example, 'analyze_experiments') as mock_analyze:
                                    with patch.object(example, 'generate_reports') as mock_reports:
                                        # Mock dos IDs
                                        mock_button.return_value = "exp_button"
                                        mock_headline.return_value = "exp_headline"
                                        mock_pricing.return_value = "exp_pricing"
                                        
                                        # Executar exemplo completo
                                        example.run_complete_example()
                                        
                                        # Verificar que todos os métodos foram chamados
                                        mock_button.assert_called_once()
                                        mock_headline.assert_called_once()
                                        mock_pricing.assert_called_once()
                                        mock_activate.assert_called_once()
                                        mock_simulate.assert_called_once()
                                        mock_health.assert_called_once()
                                        mock_analyze.assert_called_once()
                                        mock_reports.assert_called_once()


class TestABTestingExampleIntegration:
    """Testes de integração para o exemplo"""
    
    @pytest.fixture
    def example(self):
        """Exemplo de teste"""
        return ABTestingExample()
    
    def test_full_experiment_lifecycle(self, example):
        """Testa ciclo completo de vida do experimento"""
        # 1. Criar experimento
        experiment_id = example.create_button_color_experiment()
        assert experiment_id in example.framework.experiments
        
        # 2. Ativar experimento
        example.activate_experiments([experiment_id])
        experiment = example.framework.experiments[experiment_id]
        assert experiment.status.value == "active"
        
        # 3. Simular tráfego
        users, conversions = example.simulate_user_traffic(
            experiment_ids=[experiment_id],
            num_users=50,
            duration_minutes=1
        )
        assert users > 0
        
        # 4. Verificar atribuições
        user_assignments = [
            assignment for assignment in example.framework.user_assignments.values()
            if assignment.experiment_id == experiment_id
        ]
        assert len(user_assignments) > 0
        
        # 5. Verificar conversões
        conversion_data = example.analytics._get_conversion_data(experiment_id)
        assert len(conversion_data) > 0
    
    def test_multiple_experiments_concurrent(self, example):
        """Testa múltiplos experimentos concorrentes"""
        # Criar múltiplos experimentos
        experiment_ids = []
        experiment_ids.append(example.create_button_color_experiment())
        experiment_ids.append(example.create_headline_experiment())
        experiment_ids.append(example.create_pricing_experiment())
        
        # Ativar todos
        example.activate_experiments(experiment_ids)
        
        # Verificar que todos estão ativos
        for experiment_id in experiment_ids:
            experiment = example.framework.experiments[experiment_id]
            assert experiment.status.value == "active"
        
        # Simular tráfego para todos
        users, conversions = example.simulate_user_traffic(
            experiment_ids=experiment_ids,
            num_users=100,
            duration_minutes=2
        )
        
        # Verificar que todos receberam tráfego
        for experiment_id in experiment_ids:
            user_assignments = [
                assignment for assignment in example.framework.user_assignments.values()
                if assignment.experiment_id == experiment_id
            ]
            assert len(user_assignments) > 0


def test_main_function():
    """Testa função main do exemplo"""
    with patch('examples.ab_testing_example.ABTestingExample') as mock_example_class:
        mock_example = Mock()
        mock_example_class.return_value = mock_example
        
        # Importar e executar main
        from examples.ab_testing_example import main
        main()
        
        # Verificar que exemplo foi criado e executado
        mock_example_class.assert_called_once()
        mock_example.run_complete_example.assert_called_once() 
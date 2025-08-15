"""
Testes Unitários para AB Testing Analytics
==========================================

Testes abrangentes para o módulo de analytics:
- Análise estatística
- Cálculo de poder estatístico
- Análise por segmentos
- Geração de relatórios
- Visualizações

Author: Paulo Júnior
Date: 2024-12-19
Tracing ID: AB_TESTING_TEST_003
"""

import pytest
import math
import statistics
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from infrastructure.ab_testing.analytics import (
    ABTestingAnalytics,
    StatisticalTest,
    StatisticalResult,
    SegmentAnalysis
)
from infrastructure.ab_testing.framework import (
    ABTestingFramework,
    ExperimentConfig,
    ExperimentStatus
)


class TestABTestingAnalytics:
    """Testes para o módulo de analytics"""
    
    @pytest.fixture
    def framework(self):
        """Framework de teste"""
        return ABTestingFramework(redis_config=None, enable_observability=False)
    
    @pytest.fixture
    def analytics(self, framework):
        """Analytics de teste"""
        return ABTestingAnalytics(
            framework=framework,
            enable_visualization=False,
            enable_observability=False
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
    
    def test_analytics_initialization(self, analytics, framework):
        """Testa inicialização do analytics"""
        assert analytics.framework == framework
        assert analytics.enable_visualization is False
        assert analytics.enable_observability is False
        assert analytics.analysis_cache == {}
        assert analytics.telemetry is None
        assert analytics.metrics is None
    
    def test_analyze_experiment_statistical_success(self, analytics, sample_experiment_config):
        """Testa análise estatística bem-sucedida"""
        experiment_id = analytics.framework.create_experiment(**sample_experiment_config)
        analytics.framework.activate_experiment(experiment_id)
        
        # Simular dados de conversão
        with patch.object(analytics, '_get_conversion_data') as mock_get_data:
            mock_get_data.return_value = [
                {"variant": "control", "value": 1.0, "user_id": f"user_{index}"} for index in range(50)
            ] + [
                {"variant": "green", "value": 1.2, "user_id": f"user_{index}"} for index in range(50, 100)
            ] + [
                {"variant": "red", "value": 0.8, "user_id": f"user_{index}"} for index in range(100, 150)
            ]
            
            result = analytics.analyze_experiment_statistical(experiment_id)
        
        assert "experiment_id" in result
        assert result["experiment_id"] == experiment_id
        assert "test_type" in result
        assert result["test_type"] == StatisticalTest.T_TEST.value
        assert "confidence_level" in result
        assert "variant_analyses" in result
        assert "statistical_results" in result
        assert "overall_analysis" in result
        assert "generated_at" in result
        
        # Verificar análises por variante
        variant_analyses = result["variant_analyses"]
        assert "control" in variant_analyses
        assert "green" in variant_analyses
        assert "red" in variant_analyses
        
        # Verificar que cada variante tem as métricas esperadas
        for variant, analysis in variant_analyses.items():
            assert "sample_size" in analysis
            assert "mean_value" in analysis
            assert "std_dev" in analysis
            assert "confidence_interval" in analysis
            assert "conversion_rate" in analysis
            assert "values" in analysis
    
    def test_analyze_experiment_statistical_no_data(self, analytics, sample_experiment_config):
        """Testa análise estatística sem dados"""
        experiment_id = analytics.framework.create_experiment(**sample_experiment_config)
        analytics.framework.activate_experiment(experiment_id)
        
        # Simular sem dados
        with patch.object(analytics, '_get_conversion_data') as mock_get_data:
            mock_get_data.return_value = []
            
            result = analytics.analyze_experiment_statistical(experiment_id)
        
        assert "error" in result
        assert "Sem dados de conversão suficientes" in result["error"]
    
    def test_analyze_experiment_statistical_experiment_not_found(self, analytics):
        """Testa análise de experimento inexistente"""
        with pytest.raises(ValueError, match="Experimento exp_invalid não encontrado"):
            analytics.analyze_experiment_statistical("exp_invalid")
    
    def test_analyze_experiment_statistical_with_chi_square(self, analytics, sample_experiment_config):
        """Testa análise com teste chi-quadrado"""
        experiment_id = analytics.framework.create_experiment(**sample_experiment_config)
        analytics.framework.activate_experiment(experiment_id)
        
        # Simular dados de conversão
        with patch.object(analytics, '_get_conversion_data') as mock_get_data:
            mock_get_data.return_value = [
                {"variant": "control", "value": 1.0, "user_id": f"user_{index}"} for index in range(50)
            ] + [
                {"variant": "green", "value": 1.2, "user_id": f"user_{index}"} for index in range(50, 100)
            ]
            
            result = analytics.analyze_experiment_statistical(
                experiment_id, 
                test_type=StatisticalTest.CHI_SQUARE
            )
        
        assert result["test_type"] == StatisticalTest.CHI_SQUARE.value
    
    def test_analyze_segments(self, analytics, sample_experiment_config):
        """Testa análise por segmentos"""
        experiment_id = analytics.framework.create_experiment(**sample_experiment_config)
        
        segment_attributes = ["user_type", "country"]
        
        result = analytics.analyze_segments(experiment_id, segment_attributes)
        
        assert result["experiment_id"] == experiment_id
        assert result["segments_analyzed"] == segment_attributes
        assert "segment_results" in result
        assert "insights" in result
        assert "generated_at" in result
        
        # Verificar estrutura dos resultados por segmento
        segment_results = result["segment_results"]
        assert "user_type" in segment_results
        assert "country" in segment_results
        
        # Verificar insights
        insights = result["insights"]
        assert len(insights) > 0
        assert all(isinstance(insight, str) for insight in insights)
    
    def test_analyze_segments_experiment_not_found(self, analytics):
        """Testa análise por segmentos de experimento inexistente"""
        with pytest.raises(ValueError, match="Experimento exp_invalid não encontrado"):
            analytics.analyze_segments("exp_invalid", ["user_type"])
    
    def test_calculate_sample_size_required(self, analytics):
        """Testa cálculo de tamanho de amostra necessário"""
        baseline_conversion = 0.05
        mde = 0.02  # 2% de diferença mínima detectável
        confidence_level = 0.95
        power = 0.8
        
        sample_size = analytics.calculate_sample_size_required(
            baseline_conversion, mde, confidence_level, power
        )
        
        assert isinstance(sample_size, int)
        assert sample_size > 0
        assert sample_size > 100  # Deve ser um número razoável
    
    def test_calculate_sample_size_required_different_parameters(self, analytics):
        """Testa cálculo com diferentes parâmetros"""
        # Teste com diferentes níveis de confiança
        sample_size_95 = analytics.calculate_sample_size_required(0.05, 0.02, 0.95, 0.8)
        sample_size_90 = analytics.calculate_sample_size_required(0.05, 0.02, 0.90, 0.8)
        
        assert sample_size_95 > sample_size_90  # Maior confiança = maior amostra
        
        # Teste com diferentes poderes
        sample_size_80 = analytics.calculate_sample_size_required(0.05, 0.02, 0.95, 0.8)
        sample_size_90 = analytics.calculate_sample_size_required(0.05, 0.02, 0.95, 0.9)
        
        assert sample_size_90 > sample_size_80  # Maior poder = maior amostra
    
    def test_generate_visualization_conversion_comparison(self, analytics, sample_experiment_config):
        """Testa geração de visualização de comparação de conversão"""
        experiment_id = analytics.framework.create_experiment(**sample_experiment_config)
        analytics.framework.activate_experiment(experiment_id)
        
        # Simular dados de conversão
        with patch.object(analytics, '_get_conversion_data') as mock_get_data:
            mock_get_data.return_value = [
                {"variant": "control", "value": 1.0, "user_id": f"user_{index}"} for index in range(50)
            ] + [
                {"variant": "green", "value": 1.2, "user_id": f"user_{index}"} for index in range(50, 100)
            ]
            
            # Executar análise primeiro
            analytics.analyze_experiment_statistical(experiment_id)
            
            result = analytics.generate_visualization(experiment_id, "conversion_comparison")
        
        assert "chart_type" in result
        assert result["chart_type"] == "conversion_comparison"
        assert "data" in result
        assert "config" in result
        
        data = result["data"]
        assert "variants" in data
        assert "conversion_rates" in data
        assert len(data["variants"]) == len(data["conversion_rates"])
    
    def test_generate_visualization_lift_analysis(self, analytics, sample_experiment_config):
        """Testa geração de visualização de análise de lift"""
        experiment_id = analytics.framework.create_experiment(**sample_experiment_config)
        analytics.framework.activate_experiment(experiment_id)
        
        # Simular dados de conversão
        with patch.object(analytics, '_get_conversion_data') as mock_get_data:
            mock_get_data.return_value = [
                {"variant": "control", "value": 1.0, "user_id": f"user_{index}"} for index in range(50)
            ] + [
                {"variant": "green", "value": 1.2, "user_id": f"user_{index}"} for index in range(50, 100)
            ]
            
            # Executar análise primeiro
            analytics.analyze_experiment_statistical(experiment_id)
            
            result = analytics.generate_visualization(experiment_id, "lift_analysis")
        
        assert "chart_type" in result
        assert result["chart_type"] == "lift_analysis"
        assert "data" in result
        assert "config" in result
    
    def test_generate_visualization_confidence_intervals(self, analytics, sample_experiment_config):
        """Testa geração de visualização de intervalos de confiança"""
        experiment_id = analytics.framework.create_experiment(**sample_experiment_config)
        analytics.framework.activate_experiment(experiment_id)
        
        # Simular dados de conversão
        with patch.object(analytics, '_get_conversion_data') as mock_get_data:
            mock_get_data.return_value = [
                {"variant": "control", "value": 1.0, "user_id": f"user_{index}"} for index in range(50)
            ] + [
                {"variant": "green", "value": 1.2, "user_id": f"user_{index}"} for index in range(50, 100)
            ]
            
            # Executar análise primeiro
            analytics.analyze_experiment_statistical(experiment_id)
            
            result = analytics.generate_visualization(experiment_id, "confidence_intervals")
        
        assert "chart_type" in result
        assert result["chart_type"] == "confidence_intervals"
        assert "data" in result
        assert "config" in result
    
    def test_generate_visualization_power_analysis(self, analytics, sample_experiment_config):
        """Testa geração de visualização de análise de poder"""
        experiment_id = analytics.framework.create_experiment(**sample_experiment_config)
        analytics.framework.activate_experiment(experiment_id)
        
        # Simular dados de conversão
        with patch.object(analytics, '_get_conversion_data') as mock_get_data:
            mock_get_data.return_value = [
                {"variant": "control", "value": 1.0, "user_id": f"user_{index}"} for index in range(50)
            ] + [
                {"variant": "green", "value": 1.2, "user_id": f"user_{index}"} for index in range(50, 100)
            ]
            
            # Executar análise primeiro
            analytics.analyze_experiment_statistical(experiment_id)
            
            result = analytics.generate_visualization(experiment_id, "power_analysis")
        
        assert "chart_type" in result
        assert result["chart_type"] == "power_analysis"
        assert "data" in result
        assert "config" in result
    
    def test_generate_visualization_invalid_type(self, analytics, sample_experiment_config):
        """Testa geração de visualização com tipo inválido"""
        experiment_id = analytics.framework.create_experiment(**sample_experiment_config)
        
        result = analytics.generate_visualization(experiment_id, "invalid_type")
        
        assert "error" in result
        assert "não suportado" in result["error"]
    
    def test_generate_visualization_no_analysis(self, analytics, sample_experiment_config):
        """Testa geração de visualização sem análise prévia"""
        experiment_id = analytics.framework.create_experiment(**sample_experiment_config)
        
        # Tentar gerar visualização sem executar análise
        result = analytics.generate_visualization(experiment_id, "conversion_comparison")
        
        # Deve executar análise automaticamente
        assert "chart_type" in result
        assert result["chart_type"] == "conversion_comparison"
    
    def test_generate_report(self, analytics, sample_experiment_config):
        """Testa geração de relatório completo"""
        experiment_id = analytics.framework.create_experiment(**sample_experiment_config)
        analytics.framework.activate_experiment(experiment_id)
        
        # Simular dados de conversão
        with patch.object(analytics, '_get_conversion_data') as mock_get_data:
            mock_get_data.return_value = [
                {"variant": "control", "value": 1.0, "user_id": f"user_{index}"} for index in range(50)
            ] + [
                {"variant": "green", "value": 1.2, "user_id": f"user_{index}"} for index in range(50, 100)
            ]
            
            report = analytics.generate_report(experiment_id)
        
        assert report["experiment_id"] == experiment_id
        assert report["name"] == sample_experiment_config["name"]
        assert report["description"] == sample_experiment_config["description"]
        assert report["status"] == ExperimentStatus.ACTIVE.value
        assert "statistical_analysis" in report
        assert "segment_analysis" in report
        assert "visualizations" in report
        assert "recommendations" in report
        assert "generated_at" in report
    
    def test_generate_report_experiment_not_found(self, analytics):
        """Testa geração de relatório para experimento inexistente"""
        with pytest.raises(ValueError, match="Experimento exp_invalid não encontrado"):
            analytics.generate_report("exp_invalid")
    
    def test_calculate_confidence_interval(self, analytics):
        """Testa cálculo de intervalo de confiança"""
        mean = 0.15
        std_dev = 0.05
        sample_size = 100
        confidence_level = 0.95
        
        interval = analytics._calculate_confidence_interval(
            mean, std_dev, sample_size, confidence_level
        )
        
        assert len(interval) == 2
        assert interval[0] < mean < interval[1]
        assert interval[0] > 0  # Limite inferior deve ser positivo
    
    def test_calculate_confidence_interval_small_sample(self, analytics):
        """Testa cálculo com amostra pequena"""
        mean = 0.15
        std_dev = 0.05
        sample_size = 1
        confidence_level = 0.95
        
        interval = analytics._calculate_confidence_interval(
            mean, std_dev, sample_size, confidence_level
        )
        
        assert interval == (mean, mean)  # Deve retornar a média para amostra pequena
    
    def test_perform_t_test(self, analytics):
        """Testa execução de teste t"""
        control_data = {
            "mean": 0.10,
            "std_dev": 0.03,
            "sample_size": 100,
            "values": [0.1] * 100
        }
        
        treatment_data = {
            "mean": 0.12,
            "std_dev": 0.04,
            "sample_size": 100,
            "values": [0.12] * 100
        }
        
        confidence_level = 0.95
        
        result = analytics._perform_t_test(control_data, treatment_data, confidence_level)
        
        assert isinstance(result, StatisticalResult)
        assert result.test_type == StatisticalTest.T_TEST
        assert 0 <= result.p_value <= 1
        assert isinstance(result.is_significant, bool)
        assert isinstance(result.effect_size, float)
        assert len(result.confidence_interval) == 2
        assert 0 <= result.power <= 1
        assert result.sample_size_required > 0
    
    def test_perform_t_test_small_sample(self, analytics):
        """Testa teste t com amostra pequena"""
        control_data = {
            "mean": 0.10,
            "std_dev": 0.03,
            "sample_size": 1,
            "values": [0.1]
        }
        
        treatment_data = {
            "mean": 0.12,
            "std_dev": 0.04,
            "sample_size": 1,
            "values": [0.12]
        }
        
        confidence_level = 0.95
        
        result = analytics._perform_t_test(control_data, treatment_data, confidence_level)
        
        assert result.p_value == 1.0
        assert result.is_significant is False
        assert result.effect_size == 0.0
        assert result.power == 0.0
    
    def test_perform_chi_square_test(self, analytics):
        """Testa execução de teste chi-quadrado"""
        control_data = {
            "mean": 0.10,
            "std_dev": 0.03,
            "sample_size": 100,
            "values": [0.1] * 100
        }
        
        treatment_data = {
            "mean": 0.12,
            "std_dev": 0.04,
            "sample_size": 100,
            "values": [0.12] * 100
        }
        
        confidence_level = 0.95
        
        result = analytics._perform_chi_square_test(control_data, treatment_data, confidence_level)
        
        assert isinstance(result, StatisticalResult)
        assert result.test_type == StatisticalTest.CHI_SQUARE
        assert 0 <= result.p_value <= 1
        assert isinstance(result.is_significant, bool)
        assert isinstance(result.effect_size, float)
        assert result.power > 0
    
    def test_calculate_statistical_power(self, analytics):
        """Testa cálculo de poder estatístico"""
        control_data = {
            "mean": 0.10,
            "std_dev": 0.03,
            "sample_size": 100
        }
        
        treatment_data = {
            "mean": 0.12,
            "std_dev": 0.04,
            "sample_size": 100
        }
        
        confidence_level = 0.95
        
        power = analytics._calculate_statistical_power(control_data, treatment_data, confidence_level)
        
        assert 0 <= power <= 1
        assert power > 0
    
    def test_calculate_overall_analysis(self, analytics):
        """Testa cálculo de análise geral"""
        variant_analyses = {
            "control": {
                "sample_size": 100,
                "conversion_rate": 0.05
            },
            "treatment": {
                "sample_size": 100,
                "conversion_rate": 0.06
            }
        }
        
        statistical_results = {
            "treatment": {
                "is_significant": True,
                "lift": 20.0,
                "p_value": 0.01
            }
        }
        
        overall = analytics._calculate_overall_analysis(variant_analyses, statistical_results)
        
        assert "total_users" in overall
        assert "total_conversions" in overall
        assert "overall_conversion_rate" in overall
        assert "best_variant" in overall
        assert "best_lift" in overall
        assert "significant_variants" in overall
        assert "recommendation" in overall
        
        assert overall["total_users"] == 200
        assert overall["best_variant"] == "treatment"
        assert overall["best_lift"] == 20.0
        assert "treatment" in overall["significant_variants"]
    
    def test_get_overall_recommendation_with_significance(self, analytics):
        """Testa recomendação geral com significância"""
        statistical_results = {
            "treatment": {
                "is_significant": True,
                "lift": 25.0
            },
            "treatment2": {
                "is_significant": True,
                "lift": 15.0
            }
        }
        
        recommendation = analytics._get_overall_recommendation(statistical_results)
        
        assert "Implementar variante treatment" in recommendation
        assert "25.0%" in recommendation
    
    def test_get_overall_recommendation_no_significance(self, analytics):
        """Testa recomendação geral sem significância"""
        statistical_results = {
            "treatment": {
                "is_significant": False,
                "lift": 5.0
            }
        }
        
        recommendation = analytics._get_overall_recommendation(statistical_results)
        
        assert "Continuar experimento" in recommendation
        assert "nenhuma variante significativa" in recommendation
    
    def test_get_overall_recommendation_no_variants(self, analytics):
        """Testa recomendação geral sem variantes"""
        statistical_results = {}
        
        recommendation = analytics._get_overall_recommendation(statistical_results)
        
        assert "Continuar experimento" in recommendation
    
    def test_generate_recommendations(self, analytics):
        """Testa geração de recomendações"""
        statistical_analysis = {
            "statistical_results": {
                "treatment": {
                    "is_significant": True,
                    "p_value": 0.01,
                    "power": 0.7
                }
            }
        }
        
        segment_analysis = {
            "insights": [
                "Novos usuários respondem melhor",
                "Considerar segmentação"
            ]
        }
        
        recommendations = analytics._generate_recommendations(statistical_analysis, segment_analysis)
        
        assert len(recommendations) > 0
        assert any("significativa" in rec for rec in recommendations)
        assert any("Aumentar amostra" in rec for rec in recommendations)
        assert any("Novos usuários respondem melhor" in rec for rec in recommendations)
    
    def test_get_z_score(self, analytics):
        """Testa obtenção de data-score"""
        # Testar valores conhecidos
        assert analytics._get_z_score(0.95) == 1.645
        assert analytics._get_z_score(0.975) == 1.96
        assert analytics._get_z_score(0.99) == 2.326
        
        # Testar valor não mapeado
        assert analytics._get_z_score(0.5) == 1.96  # Valor padrão
    
    def test_approximate_p_value(self, analytics):
        """Testa aproximação de p-value"""
        # Testar diferentes magnitudes de t_stat
        assert analytics._approximate_p_value(3.0, 10) == 0.01
        assert analytics._approximate_p_value(2.2, 10) == 0.05
        assert analytics._approximate_p_value(1.7, 10) == 0.1
        assert analytics._approximate_p_value(1.0, 10) == 0.5
    
    def test_approximate_chi2_p_value(self, analytics):
        """Testa aproximação de p-value para chi-quadrado"""
        # Testar diferentes magnitudes de chi2_stat
        assert analytics._approximate_chi2_p_value(7.0, 1) == 0.01
        assert analytics._approximate_chi2_p_value(4.0, 1) == 0.05
        assert analytics._approximate_chi2_p_value(3.0, 1) == 0.1
        assert analytics._approximate_chi2_p_value(1.0, 1) == 0.5
    
    def test_record_analysis_metrics(self, analytics):
        """Testa registro de métricas de análise"""
        # Mock do metrics manager
        mock_metrics = Mock()
        analytics.metrics = mock_metrics
        
        experiment_id = "exp_123"
        analysis = {
            "statistical_results": {
                "treatment": {
                    "p_value": 0.01,
                    "lift": 15.0,
                    "power": 0.8
                }
            }
        }
        
        analytics._record_analysis_metrics(experiment_id, analysis)
        
        # Verificar se as métricas foram registradas
        mock_metrics.increment_counter.assert_called_with("ab_testing_analyses_performed")
        mock_metrics.record_histogram.assert_called()
    
    def test_record_analysis_metrics_no_metrics_manager(self, analytics):
        """Testa registro de métricas sem metrics manager"""
        analytics.metrics = None
        
        experiment_id = "exp_123"
        analysis = {
            "statistical_results": {
                "treatment": {
                    "p_value": 0.01,
                    "lift": 15.0,
                    "power": 0.8
                }
            }
        }
        
        # Não deve gerar erro
        analytics._record_analysis_metrics(experiment_id, analysis)


class TestStatisticalTest:
    """Testes para o enum StatisticalTest"""
    
    def test_statistical_test_values(self):
        """Testa valores do enum StatisticalTest"""
        assert StatisticalTest.T_TEST.value == "t_test"
        assert StatisticalTest.CHI_SQUARE.value == "chi_square"
        assert StatisticalTest.MANN_WHITNEY.value == "mann_whitney"
        assert StatisticalTest.WILCOXON.value == "wilcoxon"
    
    def test_statistical_test_comparison(self):
        """Testa comparação de testes estatísticos"""
        assert StatisticalTest.T_TEST != StatisticalTest.CHI_SQUARE
        assert StatisticalTest.T_TEST == StatisticalTest.T_TEST


class TestStatisticalResult:
    """Testes para a classe StatisticalResult"""
    
    def test_statistical_result_creation(self):
        """Testa criação de StatisticalResult"""
        result = StatisticalResult(
            test_type=StatisticalTest.T_TEST,
            p_value=0.01,
            is_significant=True,
            effect_size=0.5,
            confidence_interval=(0.1, 0.2),
            power=0.8,
            sample_size_required=200
        )
        
        assert result.test_type == StatisticalTest.T_TEST
        assert result.p_value == 0.01
        assert result.is_significant is True
        assert result.effect_size == 0.5
        assert result.confidence_interval == (0.1, 0.2)
        assert result.power == 0.8
        assert result.sample_size_required == 200


class TestSegmentAnalysis:
    """Testes para a classe SegmentAnalysis"""
    
    def test_segment_analysis_creation(self):
        """Testa criação de SegmentAnalysis"""
        analysis = SegmentAnalysis(
            segment_name="user_type",
            segment_value="new_user",
            sample_size=100,
            conversion_rate=0.12,
            lift=15.2,
            is_significant=True,
            confidence_interval=(0.10, 0.14)
        )
        
        assert analysis.segment_name == "user_type"
        assert analysis.segment_value == "new_user"
        assert analysis.sample_size == 100
        assert analysis.conversion_rate == 0.12
        assert analysis.lift == 15.2
        assert analysis.is_significant is True
        assert analysis.confidence_interval == (0.10, 0.14) 
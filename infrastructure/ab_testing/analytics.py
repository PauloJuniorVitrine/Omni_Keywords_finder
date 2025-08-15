"""
Analytics Avançado para A/B Testing
===================================

Este módulo implementa análise estatística avançada para A/B Testing:
- Análise de significância estatística
- Cálculo de poder estatístico
- Análise de segmentos
- Relatórios automáticos
- Visualizações interativas

Author: Paulo Júnior
Date: 2024-12-19
Tracing ID: AB_TESTING_003
"""

import json
import logging
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import threading

# Dependências opcionais para visualização
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

# Integração com observabilidade
try:
    from infrastructure.observability.telemetry import TelemetryManager
    from infrastructure.observability.metrics import MetricsManager
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False

from .framework import ABTestingFramework, ExperimentConfig, ExperimentStatus

logger = logging.getLogger(__name__)


class StatisticalTest(Enum):
    """Tipos de testes estatísticos"""
    T_TEST = "t_test"
    CHI_SQUARE = "chi_square"
    MANN_WHITNEY = "mann_whitney"
    WILCOXON = "wilcoxon"


@dataclass
class StatisticalResult:
    """Resultado de análise estatística"""
    test_type: StatisticalTest
    p_value: float
    is_significant: bool
    effect_size: float
    confidence_interval: Tuple[float, float]
    power: float
    sample_size_required: int


@dataclass
class SegmentAnalysis:
    """Análise por segmento"""
    segment_name: str
    segment_value: str
    sample_size: int
    conversion_rate: float
    lift: float
    is_significant: bool
    confidence_interval: Tuple[float, float]


class ABTestingAnalytics:
    """
    Analytics avançado para A/B Testing
    
    Características:
    - Análise estatística robusta
    - Cálculo de poder estatístico
    - Análise por segmentos
    - Relatórios automáticos
    - Visualizações interativas
    - Integração com observabilidade
    """
    
    def __init__(self, 
                 framework: ABTestingFramework,
                 enable_visualization: bool = True,
                 enable_observability: bool = True):
        """
        Inicializa o analytics
        
        Args:
            framework: Instância do framework A/B Testing
            enable_visualization: Habilita visualizações
            enable_observability: Habilita integração com observabilidade
        """
        self.framework = framework
        self.enable_visualization = enable_visualization and VISUALIZATION_AVAILABLE
        self.enable_observability = enable_observability and OBSERVABILITY_AVAILABLE
        
        # Cache de análises
        self.analysis_cache: Dict[str, Dict[str, Any]] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Observabilidade
        self.telemetry = None
        self.metrics = None
        
        if self.enable_observability:
            try:
                self.telemetry = TelemetryManager()
                self.metrics = MetricsManager()
            except Exception as e:
                logger.warning(f"Falha ao inicializar observabilidade: {e}")
        
        logger.info("AB Testing Analytics inicializado")
    
    def analyze_experiment_statistical(self, 
                                     experiment_id: str,
                                     test_type: StatisticalTest = StatisticalTest.T_TEST) -> Dict[str, Any]:
        """
        Análise estatística completa do experimento
        
        Args:
            experiment_id: ID do experimento
            test_type: Tipo de teste estatístico
            
        Returns:
            Resultados da análise estatística
        """
        with self._lock:
            if experiment_id not in self.framework.experiments:
                raise ValueError(f"Experimento {experiment_id} não encontrado")
            
            experiment = self.framework.experiments[experiment_id]
            
            # Coletar dados de conversão
            conversion_data = self._get_conversion_data(experiment_id)
            
            if not conversion_data:
                return {"error": "Sem dados de conversão suficientes"}
            
            # Análise por variante
            variant_analyses = {}
            control_data = None
            
            for variant in experiment.variants:
                variant_data = [data for data in conversion_data if data["variant"] == variant]
                
                if not variant_data:
                    continue
                
                values = [data["value"] for data in variant_data]
                sample_size = len(values)
                
                # Estatísticas básicas
                mean_value = statistics.mean(values)
                std_dev = statistics.stdev(values) if len(values) > 1 else 0
                
                # Intervalo de confiança
                confidence_interval = self._calculate_confidence_interval(
                    mean_value, std_dev, sample_size, experiment.confidence_level
                )
                
                # Armazenar dados do controle
                if variant == "control":
                    control_data = {
                        "mean": mean_value,
                        "std_dev": std_dev,
                        "sample_size": sample_size,
                        "values": values
                    }
                
                variant_analyses[variant] = {
                    "sample_size": sample_size,
                    "mean_value": mean_value,
                    "std_dev": std_dev,
                    "confidence_interval": confidence_interval,
                    "conversion_rate": sample_size / len(conversion_data) if conversion_data else 0,
                    "values": values
                }
            
            # Análise estatística comparativa
            statistical_results = {}
            if control_data and len(variant_analyses) > 1:
                for variant, data in variant_analyses.items():
                    if variant != "control":
                        # Teste estatístico
                        stat_result = self._perform_statistical_test(
                            control_data, data, test_type, experiment.confidence_level
                        )
                        
                        # Lift
                        lift = ((data["mean_value"] - control_data["mean"]) / control_data["mean"]) * 100
                        
                        # Poder estatístico
                        power = self._calculate_statistical_power(
                            control_data, data, experiment.confidence_level
                        )
                        
                        statistical_results[variant] = {
                            "p_value": stat_result.p_value,
                            "is_significant": stat_result.is_significant,
                            "effect_size": stat_result.effect_size,
                            "confidence_interval": stat_result.confidence_interval,
                            "power": power,
                            "lift": lift,
                            "sample_size_required": stat_result.sample_size_required
                        }
            
            # Análise geral
            overall_analysis = self._calculate_overall_analysis(variant_analyses, statistical_results)
            
            # Cache dos resultados
            analysis_result = {
                "experiment_id": experiment_id,
                "test_type": test_type.value,
                "confidence_level": experiment.confidence_level,
                "variant_analyses": variant_analyses,
                "statistical_results": statistical_results,
                "overall_analysis": overall_analysis,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            self.analysis_cache[experiment_id] = analysis_result
            
            # Métricas
            if self.metrics:
                self._record_analysis_metrics(experiment_id, analysis_result)
            
            logger.info(f"Análise estatística concluída para experimento {experiment_id}")
            return analysis_result
    
    def analyze_segments(self, 
                        experiment_id: str,
                        segment_attributes: List[str]) -> Dict[str, Any]:
        """
        Análise por segmentos de usuários
        
        Args:
            experiment_id: ID do experimento
            segment_attributes: Atributos para segmentação
            
        Returns:
            Análise por segmentos
        """
        with self._lock:
            if experiment_id not in self.framework.experiments:
                raise ValueError(f"Experimento {experiment_id} não encontrado")
            
            # Em produção, buscar dados de segmentação do banco
            # Por simplicidade, retornamos análise simulada
            segment_analysis = {
                "experiment_id": experiment_id,
                "segments_analyzed": segment_attributes,
                "segment_results": {},
                "insights": [],
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Simular análise por segmentos
            for attribute in segment_attributes:
                segment_analysis["segment_results"][attribute] = {
                    "new_users": {
                        "sample_size": 150,
                        "conversion_rate": 0.12,
                        "lift": 15.2,
                        "is_significant": True
                    },
                    "returning_users": {
                        "sample_size": 200,
                        "conversion_rate": 0.18,
                        "lift": 8.5,
                        "is_significant": False
                    }
                }
            
            # Gerar insights
            segment_analysis["insights"] = [
                "Novos usuários respondem melhor à variante de tratamento",
                "Usuários recorrentes não mostram diferença significativa",
                "Considerar segmentação por tipo de usuário"
            ]
            
            logger.info(f"Análise por segmentos concluída para experimento {experiment_id}")
            return segment_analysis
    
    def calculate_sample_size_required(self,
                                     baseline_conversion: float,
                                     mde: float,
                                     confidence_level: float = 0.95,
                                     power: float = 0.8) -> int:
        """
        Calcula tamanho de amostra necessário
        
        Args:
            baseline_conversion: Taxa de conversão baseline
            mde: Minimum Detectable Effect (em decimal)
            confidence_level: Nível de confiança
            power: Poder estatístico desejado
            
        Returns:
            Tamanho de amostra necessário por variante
        """
        # Z-scores
        z_alpha = self._get_z_score(confidence_level)
        z_beta = self._get_z_score(power)
        
        # Cálculo do tamanho da amostra
        p1 = baseline_conversion
        p2 = baseline_conversion * (1 + mde)
        
        # Variância combinada
        pooled_variance = p1 * (1 - p1) + p2 * (1 - p2)
        
        # Tamanho da amostra
        sample_size = (2 * (z_alpha + z_beta)**2 * pooled_variance) / (mde**2)
        
        return int(math.ceil(sample_size))
    
    def generate_visualization(self, 
                             experiment_id: str,
                             chart_type: str = "conversion_comparison") -> Dict[str, Any]:
        """
        Gera visualizações do experimento
        
        Args:
            experiment_id: ID do experimento
            chart_type: Tipo de gráfico
            
        Returns:
            Dados da visualização
        """
        if not self.enable_visualization:
            return {"error": "Visualização não disponível"}
        
        with self._lock:
            if experiment_id not in self.analysis_cache:
                # Executar análise primeiro
                self.analyze_experiment_statistical(experiment_id)
            
            analysis = self.analysis_cache[experiment_id]
            
            if chart_type == "conversion_comparison":
                return self._create_conversion_comparison_chart(analysis)
            elif chart_type == "lift_analysis":
                return self._create_lift_analysis_chart(analysis)
            elif chart_type == "confidence_intervals":
                return self._create_confidence_intervals_chart(analysis)
            elif chart_type == "power_analysis":
                return self._create_power_analysis_chart(analysis)
            else:
                return {"error": f"Tipo de gráfico '{chart_type}' não suportado"}
    
    def generate_report(self, experiment_id: str) -> Dict[str, Any]:
        """
        Gera relatório completo do experimento
        
        Args:
            experiment_id: ID do experimento
            
        Returns:
            Relatório detalhado
        """
        with self._lock:
            if experiment_id not in self.framework.experiments:
                raise ValueError(f"Experimento {experiment_id} não encontrado")
            
            experiment = self.framework.experiments[experiment_id]
            
            # Análise estatística
            statistical_analysis = self.analyze_experiment_statistical(experiment_id)
            
            # Análise por segmentos
            segment_analysis = self.analyze_segments(experiment_id, ["user_type", "country"])
            
            # Visualizações
            visualizations = {}
            if self.enable_visualization:
                visualizations = {
                    "conversion_comparison": self.generate_visualization(experiment_id, "conversion_comparison"),
                    "lift_analysis": self.generate_visualization(experiment_id, "lift_analysis"),
                    "confidence_intervals": self.generate_visualization(experiment_id, "confidence_intervals")
                }
            
            # Recomendações
            recommendations = self._generate_recommendations(statistical_analysis, segment_analysis)
            
            report = {
                "experiment_id": experiment_id,
                "name": experiment.name,
                "description": experiment.description,
                "status": experiment.status.value,
                "start_date": experiment.start_date.isoformat(),
                "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
                "statistical_analysis": statistical_analysis,
                "segment_analysis": segment_analysis,
                "visualizations": visualizations,
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Relatório gerado para experimento {experiment_id}")
            return report
    
    def _get_conversion_data(self, experiment_id: str) -> List[Dict[str, Any]]:
        """Coleta dados de conversão"""
        # Em produção, buscar do banco de dados
        # Por simplicidade, retornamos dados simulados
        return [
            {"variant": "control", "value": 1.0, "user_id": f"user_{index}"} for index in range(100)
        ] + [
            {"variant": "treatment", "value": 1.2, "user_id": f"user_{index}"} for index in range(100, 200)
        ]
    
    def _calculate_confidence_interval(self,
                                     mean: float,
                                     std_dev: float,
                                     sample_size: int,
                                     confidence_level: float) -> Tuple[float, float]:
        """Calcula intervalo de confiança"""
        if sample_size <= 1:
            return (mean, mean)
        
        z_score = self._get_z_score(confidence_level)
        standard_error = std_dev / math.sqrt(sample_size)
        margin_of_error = z_score * standard_error
        
        return (mean - margin_of_error, mean + margin_of_error)
    
    def _perform_statistical_test(self,
                                control_data: Dict[str, Any],
                                treatment_data: Dict[str, Any],
                                test_type: StatisticalTest,
                                confidence_level: float) -> StatisticalResult:
        """Executa teste estatístico"""
        if test_type == StatisticalTest.T_TEST:
            return self._perform_t_test(control_data, treatment_data, confidence_level)
        elif test_type == StatisticalTest.CHI_SQUARE:
            return self._perform_chi_square_test(control_data, treatment_data, confidence_level)
        else:
            # Fallback para t-test
            return self._perform_t_test(control_data, treatment_data, confidence_level)
    
    def _perform_t_test(self,
                       control_data: Dict[str, Any],
                       treatment_data: Dict[str, Any],
                       confidence_level: float) -> StatisticalResult:
        """Executa teste t de duas amostras"""
        n1, n2 = control_data["sample_size"], treatment_data["sample_size"]
        mean1, mean2 = control_data["mean"], treatment_data["mean"]
        std1, std2 = control_data["std_dev"], treatment_data["std_dev"]
        
        if n1 <= 1 or n2 <= 1:
            return StatisticalResult(
                test_type=StatisticalTest.T_TEST,
                p_value=1.0,
                is_significant=False,
                effect_size=0.0,
                confidence_interval=(0.0, 0.0),
                power=0.0,
                sample_size_required=0
            )
        
        # Estatística t
        pooled_std = math.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        t_stat = (mean2 - mean1) / (pooled_std * math.sqrt(1/n1 + 1/n2))
        
        # Graus de liberdade
        df = n1 + n2 - 2
        
        # P-value aproximado (em produção, usar scipy.stats)
        p_value = self._approximate_p_value(t_stat, df)
        
        # Tamanho do efeito (Cohen'string_data data)
        effect_size = (mean2 - mean1) / pooled_std
        
        # Intervalo de confiança
        confidence_interval = self._calculate_confidence_interval(
            mean2 - mean1, pooled_std, min(n1, n2), confidence_level
        )
        
        # Poder estatístico
        power = self._calculate_statistical_power(control_data, treatment_data, confidence_level)
        
        # Tamanho de amostra necessário
        sample_size_required = self.calculate_sample_size_required(
            control_data["mean"], abs(effect_size), confidence_level, 0.8
        )
        
        return StatisticalResult(
            test_type=StatisticalTest.T_TEST,
            p_value=p_value,
            is_significant=p_value < (1 - confidence_level),
            effect_size=effect_size,
            confidence_interval=confidence_interval,
            power=power,
            sample_size_required=sample_size_required
        )
    
    def _perform_chi_square_test(self,
                               control_data: Dict[str, Any],
                               treatment_data: Dict[str, Any],
                               confidence_level: float) -> StatisticalResult:
        """Executa teste chi-quadrado"""
        # Implementação simplificada
        # Em produção, usar scipy.stats.chi2_contingency
        
        n1, n2 = control_data["sample_size"], treatment_data["sample_size"]
        conv1, conv2 = control_data["mean"] * n1, treatment_data["mean"] * n2
        
        # Tabela de contingência
        observed = [[conv1, n1 - conv1], [conv2, n2 - conv2]]
        
        # Chi-quadrado aproximado
        chi2_stat = ((conv2 - conv1)**2) / (conv1 + conv2) if (conv1 + conv2) > 0 else 0
        
        # P-value aproximado
        p_value = self._approximate_chi2_p_value(chi2_stat, 1)
        
        return StatisticalResult(
            test_type=StatisticalTest.CHI_SQUARE,
            p_value=p_value,
            is_significant=p_value < (1 - confidence_level),
            effect_size=abs(conv2/n2 - conv1/n1),
            confidence_interval=(0.0, 0.0),  # Não aplicável para chi-quadrado
            power=0.8,  # Estimativa
            sample_size_required=0
        )
    
    def _calculate_statistical_power(self,
                                   control_data: Dict[str, Any],
                                   treatment_data: Dict[str, Any],
                                   confidence_level: float) -> float:
        """Calcula poder estatístico"""
        # Implementação simplificada
        # Em produção, usar scipy.stats.power
        
        n1, n2 = control_data["sample_size"], treatment_data["sample_size"]
        effect_size = abs(treatment_data["mean"] - control_data["mean"])
        
        # Poder baseado no tamanho da amostra e efeito
        power = min(0.95, (n1 + n2) / 1000 * effect_size * 10)
        
        return power
    
    def _calculate_overall_analysis(self,
                                  variant_analyses: Dict[str, Any],
                                  statistical_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula análise geral"""
        total_users = sum(data["sample_size"] for data in variant_analyses.values())
        total_conversions = sum(data["sample_size"] * data["conversion_rate"] 
                              for data in variant_analyses.values())
        
        # Melhor variante
        best_variant = None
        best_lift = 0
        
        for variant, stats in statistical_results.items():
            if stats["lift"] > best_lift and stats["is_significant"]:
                best_lift = stats["lift"]
                best_variant = variant
        
        return {
            "total_users": total_users,
            "total_conversions": total_conversions,
            "overall_conversion_rate": total_conversions / total_users if total_users > 0 else 0,
            "best_variant": best_variant,
            "best_lift": best_lift,
            "significant_variants": [value for value, string_data in statistical_results.items() if string_data["is_significant"]],
            "recommendation": self._get_overall_recommendation(statistical_results)
        }
    
    def _get_overall_recommendation(self, statistical_results: Dict[str, Any]) -> str:
        """Gera recomendação geral"""
        significant_variants = [value for value, string_data in statistical_results.items() if string_data["is_significant"]]
        
        if not significant_variants:
            return "Continuar experimento - nenhuma variante significativa"
        
        best_variant = max(significant_variants, 
                          key=lambda value: statistical_results[value]["lift"])
        
        return f"Implementar variante {best_variant} - significativa com {statistical_results[best_variant]['lift']:.1f}% de lift"
    
    def _generate_recommendations(self,
                                statistical_analysis: Dict[str, Any],
                                segment_analysis: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Recomendações baseadas em significância
        significant_variants = statistical_analysis.get("statistical_results", {})
        for variant, stats in significant_variants.items():
            if stats["is_significant"]:
                recommendations.append(f"Variante {variant} é significativa (p={stats['p_value']:.4f})")
        
        # Recomendações baseadas em poder estatístico
        for variant, stats in significant_variants.items():
            if stats["power"] < 0.8:
                recommendations.append(f"Aumentar amostra para variante {variant} (poder: {stats['power']:.2f})")
        
        # Recomendações baseadas em segmentos
        segment_insights = segment_analysis.get("insights", [])
        recommendations.extend(segment_insights)
        
        return recommendations
    
    def _create_conversion_comparison_chart(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Cria gráfico de comparação de conversão"""
        if not self.enable_visualization:
            return {"error": "Visualização não disponível"}
        
        # Em produção, criar gráfico real com matplotlib/seaborn
        return {
            "chart_type": "conversion_comparison",
            "data": {
                "variants": list(analysis["variant_analyses"].keys()),
                "conversion_rates": [data["conversion_rate"] 
                                   for data in analysis["variant_analyses"].values()]
            },
            "config": {
                "title": "Taxa de Conversão por Variante",
                "x_label": "Variante",
                "y_label": "Taxa de Conversão"
            }
        }
    
    def _create_lift_analysis_chart(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Cria gráfico de análise de lift"""
        if not self.enable_visualization:
            return {"error": "Visualização não disponível"}
        
        lifts = []
        variants = []
        
        for variant, stats in analysis.get("statistical_results", {}).items():
            lifts.append(stats["lift"])
            variants.append(variant)
        
        return {
            "chart_type": "lift_analysis",
            "data": {
                "variants": variants,
                "lifts": lifts
            },
            "config": {
                "title": "Lift por Variante",
                "x_label": "Variante",
                "y_label": "Lift (%)"
            }
        }
    
    def _create_confidence_intervals_chart(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Cria gráfico de intervalos de confiança"""
        if not self.enable_visualization:
            return {"error": "Visualização não disponível"}
        
        intervals = []
        variants = []
        
        for variant, data in analysis["variant_analyses"].items():
            intervals.append(data["confidence_interval"])
            variants.append(variant)
        
        return {
            "chart_type": "confidence_intervals",
            "data": {
                "variants": variants,
                "intervals": intervals
            },
            "config": {
                "title": "Intervalos de Confiança",
                "x_label": "Variante",
                "y_label": "Taxa de Conversão"
            }
        }
    
    def _create_power_analysis_chart(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Cria gráfico de análise de poder"""
        if not self.enable_visualization:
            return {"error": "Visualização não disponível"}
        
        powers = []
        variants = []
        
        for variant, stats in analysis.get("statistical_results", {}).items():
            powers.append(stats["power"])
            variants.append(variant)
        
        return {
            "chart_type": "power_analysis",
            "data": {
                "variants": variants,
                "powers": powers
            },
            "config": {
                "title": "Poder Estatístico por Variante",
                "x_label": "Variante",
                "y_label": "Poder"
            }
        }
    
    def _get_z_score(self, probability: float) -> float:
        """Retorna data-score para uma probabilidade"""
        z_scores = {
            0.8: 0.842,
            0.85: 1.036,
            0.9: 1.282,
            0.95: 1.645,
            0.975: 1.96,
            0.99: 2.326,
            0.995: 2.576
        }
        return z_scores.get(probability, 1.96)
    
    def _approximate_p_value(self, t_stat: float, df: int) -> float:
        """Aproxima p-value para teste t"""
        # Aproximação simples baseada na magnitude do t_stat
        if abs(t_stat) > 2.5:
            return 0.01
        elif abs(t_stat) > 2.0:
            return 0.05
        elif abs(t_stat) > 1.5:
            return 0.1
        else:
            return 0.5
    
    def _approximate_chi2_p_value(self, chi2_stat: float, df: int) -> float:
        """Aproxima p-value para teste chi-quadrado"""
        # Aproximação simples
        if chi2_stat > 6.63:
            return 0.01
        elif chi2_stat > 3.84:
            return 0.05
        elif chi2_stat > 2.71:
            return 0.1
        else:
            return 0.5
    
    def _record_analysis_metrics(self, experiment_id: str, analysis: Dict[str, Any]):
        """Registra métricas da análise"""
        if not self.metrics:
            return
        
        try:
            # Métricas básicas
            self.metrics.increment_counter("ab_testing_analyses_performed")
            
            # Métricas por variante
            for variant, stats in analysis.get("statistical_results", {}).items():
                self.metrics.record_histogram("ab_testing_p_values",
                                            stats["p_value"],
                                            labels={"experiment": experiment_id, "variant": variant})
                
                self.metrics.record_histogram("ab_testing_lifts",
                                            stats["lift"],
                                            labels={"experiment": experiment_id, "variant": variant})
                
                self.metrics.record_histogram("ab_testing_power",
                                            stats["power"],
                                            labels={"experiment": experiment_id, "variant": variant})
        
        except Exception as e:
            logger.error(f"Erro ao registrar métricas de análise: {e}") 
"""
Sistema de A/B Testing Multi-Variado
Tracing ID: LONGTAIL-040
Data: 2024-12-20
Descrição: Sistema de teste multi-variado para múltiplos parâmetros simultaneamente
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestType(Enum):
    """Tipos de teste"""
    A_B = "a_b"
    MULTIVARIATE = "multivariate"
    BANDIT = "bandit"

class MetricType(Enum):
    """Tipos de métricas"""
    CONVERSION_RATE = "conversion_rate"
    CLICK_THROUGH_RATE = "click_through_rate"
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    QUALITY_SCORE = "quality_score"

@dataclass
class TestVariant:
    """Variante de teste"""
    name: str
    parameters: Dict[str, Any]
    traffic_percentage: float
    description: str = ""

@dataclass
class TestConfig:
    """Configuração do teste"""
    test_id: str
    test_type: TestType
    name: str
    description: str
    variants: List[TestVariant]
    metrics: List[MetricType]
    duration_days: int
    confidence_level: float = 0.95
    minimum_sample_size: int = 1000
    traffic_allocation: Dict[str, float] = field(default_factory=dict)

@dataclass
class TestResult:
    """Resultado do teste"""
    test_id: str
    variant_name: str
    metric_name: str
    value: float
    sample_size: int
    confidence_interval: Tuple[float, float]
    p_value: float
    is_significant: bool
    lift_vs_control: float
    timestamp: datetime

@dataclass
class MultivariateTest:
    """Teste multi-variado"""
    config: TestConfig
    start_date: datetime
    end_date: datetime
    status: str = "running"
    results: List[TestResult] = field(default_factory=list)
    traffic_data: pd.DataFrame = field(default_factory=pd.DataFrame)

class DesignOfExperiments:
    """Design de experimentos para testes multi-variados"""
    
    def __init__(self):
        self.factor_levels = {}
        self.interaction_effects = []
    
    def add_factor(self, factor_name: str, levels: List[Any]):
        """Adiciona fator ao experimento"""
        self.factor_levels[factor_name] = levels
        logger.info(f"Fator adicionado: {factor_name} com {len(levels)} níveis")
    
    def add_interaction(self, factor1: str, factor2: str):
        """Adiciona interação entre fatores"""
        self.interaction_effects.append((factor1, factor2))
        logger.info(f"Interação adicionada: {factor1} value {factor2}")
    
    def generate_factorial_design(self, fraction: float = 1.0) -> List[Dict[str, Any]]:
        """Gera design fatorial"""
        logger.info("Gerando design fatorial...")
        
        # Gera todas as combinações possíveis
        factor_names = list(self.factor_levels.keys())
        factor_levels = list(self.factor_levels.values())
        
        # Produto cartesiano de todos os níveis
        import itertools
        all_combinations = list(itertools.product(*factor_levels))
        
        # Aplica fração se necessário
        if fraction < 1.0:
            n_combinations = len(all_combinations)
            n_selected = int(n_combinations * fraction)
            selected_indices = random.sample(range(n_combinations), n_selected)
            all_combinations = [all_combinations[index] for index in selected_indices]
        
        # Converte para dicionários
        design = []
        for index, combination in enumerate(all_combinations):
            variant = {
                'name': f"variant_{index+1}",
                'parameters': dict(zip(factor_names, combination))
            }
            design.append(variant)
        
        logger.info(f"Design gerado: {len(design)} variantes")
        return design
    
    def generate_latin_square_design(self, n_factors: int) -> List[Dict[str, Any]]:
        """Gera design de quadrado latino"""
        logger.info("Gerando design de quadrado latino...")
        
        # Implementação simplificada de quadrado latino
        factor_names = list(self.factor_levels.keys())[:n_factors]
        
        design = []
        for index in range(n_factors):
            variant = {
                'name': f"latin_square_{index+1}",
                'parameters': {}
            }
            
            for counter, factor in enumerate(factor_names):
                levels = self.factor_levels[factor]
                level_index = (index + counter) % len(levels)
                variant['parameters'][factor] = levels[level_index]
            
            design.append(variant)
        
        logger.info(f"Quadrado latino gerado: {len(design)} variantes")
        return design

class TrafficAllocator:
    """Alocador de tráfego para testes"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.variant_assignments = {}
    
    def allocate_traffic(self, user_id: str) -> str:
        """Aloca usuário para variante"""
        if user_id in self.variant_assignments:
            return self.variant_assignments[user_id]
        
        # Alocação baseada em hash do user_id
        hash_value = hash(user_id) % 100
        
        cumulative_percentage = 0
        for variant in self.config.variants:
            cumulative_percentage += variant.traffic_percentage
            if hash_value < cumulative_percentage:
                self.variant_assignments[user_id] = variant.name
                return variant.name
        
        # Fallback para primeira variante
        self.variant_assignments[user_id] = self.config.variants[0].name
        return self.config.variants[0].name
    
    def get_traffic_distribution(self) -> Dict[str, int]:
        """Retorna distribuição atual do tráfego"""
        distribution = {}
        for variant in self.config.variants:
            count = sum(1 for value in self.variant_assignments.values() if value == variant.name)
            distribution[variant.name] = count
        
        return distribution

class MetricCalculator:
    """Calculadora de métricas para testes"""
    
    def __init__(self):
        self.metric_functions = {
            MetricType.CONVERSION_RATE: self._calculate_conversion_rate,
            MetricType.CLICK_THROUGH_RATE: self._calculate_ctr,
            MetricType.REVENUE: self._calculate_revenue,
            MetricType.ENGAGEMENT: self._calculate_engagement,
            MetricType.QUALITY_SCORE: self._calculate_quality_score
        }
    
    def calculate_metric(self, metric_type: MetricType, data: pd.DataFrame) -> float:
        """Calcula métrica específica"""
        if metric_type in self.metric_functions:
            return self.metric_functions[metric_type](data)
        else:
            raise ValueError(f"Métrica não suportada: {metric_type}")
    
    def _calculate_conversion_rate(self, data: pd.DataFrame) -> float:
        """Calcula taxa de conversão"""
        if 'conversions' in data.columns and 'impressions' in data.columns:
            conversions = data['conversions'].sum()
            impressions = data['impressions'].sum()
            return conversions / impressions if impressions > 0 else 0.0
        return 0.0
    
    def _calculate_ctr(self, data: pd.DataFrame) -> float:
        """Calcula click-through rate"""
        if 'clicks' in data.columns and 'impressions' in data.columns:
            clicks = data['clicks'].sum()
            impressions = data['impressions'].sum()
            return clicks / impressions if impressions > 0 else 0.0
        return 0.0
    
    def _calculate_revenue(self, data: pd.DataFrame) -> float:
        """Calcula receita total"""
        if 'revenue' in data.columns:
            return data['revenue'].sum()
        return 0.0
    
    def _calculate_engagement(self, data: pd.DataFrame) -> float:
        """Calcula score de engajamento"""
        if 'time_on_page' in data.columns and 'page_views' in data.columns:
            total_time = data['time_on_page'].sum()
            total_views = data['page_views'].sum()
            return total_time / total_views if total_views > 0 else 0.0
        return 0.0
    
    def _calculate_quality_score(self, data: pd.DataFrame) -> float:
        """Calcula score de qualidade"""
        if 'quality_metrics' in data.columns:
            return data['quality_metrics'].mean()
        return 0.0

class StatisticalAnalyzer:
    """Analisador estatístico para testes"""
    
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
    
    def calculate_confidence_interval(self, data: pd.Series) -> Tuple[float, float]:
        """Calcula intervalo de confiança"""
        from scipy import stats
        
        mean = data.mean()
        std_err = stats.sem(data)
        
        # Calcula intervalo de confiança
        ci = stats.t.interval(self.confidence_level, len(data) - 1, loc=mean, scale=std_err)
        
        return (ci[0], ci[1])
    
    def perform_t_test(self, control_data: pd.Series, treatment_data: pd.Series) -> Dict[str, float]:
        """Realiza teste t entre controle e tratamento"""
        from scipy import stats
        
        # Teste t independente
        t_stat, p_value = stats.ttest_ind(control_data, treatment_data)
        
        # Calcula tamanho do efeito (Cohen'string_data data)
        pooled_std = np.sqrt(((len(control_data) - 1) * control_data.var() + 
                             (len(treatment_data) - 1) * treatment_data.var()) / 
                            (len(control_data) + len(treatment_data) - 2))
        
        cohens_d = (treatment_data.mean() - control_data.mean()) / pooled_std
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'is_significant': p_value < (1 - self.confidence_level)
        }
    
    def perform_anova(self, data_dict: Dict[str, pd.Series]) -> Dict[str, float]:
        """Realiza ANOVA para múltiplas variantes"""
        from scipy import stats
        
        # Prepara dados para ANOVA
        groups = list(data_dict.values())
        group_names = list(data_dict.keys())
        
        # ANOVA
        f_stat, p_value = stats.f_oneway(*groups)
        
        # Testes post-hoc (Tukey)
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        
        # Combina dados para Tukey
        all_data = []
        all_labels = []
        for name, data in data_dict.items():
            all_data.extend(data.values)
            all_labels.extend([name] * len(data))
        
        tukey_result = pairwise_tukeyhsd(all_data, all_labels)
        
        return {
            'f_statistic': f_stat,
            'p_value': p_value,
            'is_significant': p_value < (1 - self.confidence_level),
            'tukey_result': tukey_result
        }
    
    def calculate_sample_size(self, effect_size: float, alpha: float = 0.05, power: float = 0.8) -> int:
        """Calcula tamanho de amostra necessário"""
        from statsmodels.stats.power import TTestPower
        
        power_analysis = TTestPower()
        sample_size = power_analysis.solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            alternative='two-sided'
        )
        
        return int(sample_size)

class MultivariateTestRunner:
    """Executor de testes multi-variados"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.test = MultivariateTest(config, datetime.now(), 
                                   datetime.now() + timedelta(days=config.duration_days))
        self.traffic_allocator = TrafficAllocator(config)
        self.metric_calculator = MetricCalculator()
        self.statistical_analyzer = StatisticalAnalyzer(config.confidence_level)
        
        # Dados coletados
        self.collected_data = {
            variant.name: {metric.value: [] for metric in config.metrics}
            for variant in config.variants
        }
    
    def record_event(self, user_id: str, event_data: Dict[str, Any]):
        """Registra evento do usuário"""
        # Aloca usuário para variante
        variant_name = self.traffic_allocator.allocate_traffic(user_id)
        
        # Adiciona dados do evento
        for metric in self.config.metrics:
            if metric.value in event_data:
                self.collected_data[variant_name][metric.value].append(event_data[metric.value])
        
        # Registra no DataFrame de tráfego
        traffic_record = {
            'user_id': user_id,
            'variant': variant_name,
            'timestamp': datetime.now(),
            **event_data
        }
        
        self.test.traffic_data = pd.concat([
            self.test.traffic_data,
            pd.DataFrame([traffic_record])
        ], ignore_index=True)
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analisa resultados do teste"""
        logger.info("Analisando resultados do teste multi-variado...")
        
        results = {
            'test_id': self.config.test_id,
            'test_name': self.config.name,
            'analysis_date': datetime.now().isoformat(),
            'variants': {},
            'statistical_tests': {},
            'recommendations': []
        }
        
        # Análise por variante
        for variant in self.config.variants:
            variant_results = {}
            
            for metric in self.config.metrics:
                metric_data = self.collected_data[variant.name][metric.value]
                
                if len(metric_data) == 0:
                    continue
                
                data_series = pd.Series(metric_data)
                
                # Estatísticas básicas
                mean_value = data_series.mean()
                std_value = data_series.std()
                sample_size = len(data_series)
                
                # Intervalo de confiança
                ci_lower, ci_upper = self.statistical_analyzer.calculate_confidence_interval(data_series)
                
                # Comparação com controle (primeira variante)
                control_data = pd.Series(self.collected_data[self.config.variants[0].name][metric.value])
                
                if len(control_data) > 0 and variant.name != self.config.variants[0].name:
                    t_test_result = self.statistical_analyzer.perform_t_test(control_data, data_series)
                    
                    # Calcula lift
                    control_mean = control_data.mean()
                    lift = ((mean_value - control_mean) / control_mean * 100) if control_mean > 0 else 0
                    
                    variant_results[metric.value] = {
                        'mean': mean_value,
                        'std': std_value,
                        'sample_size': sample_size,
                        'confidence_interval': (ci_lower, ci_upper),
                        'p_value': t_test_result['p_value'],
                        'is_significant': t_test_result['is_significant'],
                        'lift_vs_control': lift,
                        'cohens_d': t_test_result['cohens_d']
                    }
                else:
                    variant_results[metric.value] = {
                        'mean': mean_value,
                        'std': std_value,
                        'sample_size': sample_size,
                        'confidence_interval': (ci_lower, ci_upper),
                        'p_value': None,
                        'is_significant': None,
                        'lift_vs_control': 0.0,
                        'cohens_d': 0.0
                    }
            
            results['variants'][variant.name] = variant_results
        
        # Análise estatística multi-variada
        results['statistical_tests'] = self._perform_multivariate_analysis()
        
        # Gera recomendações
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _perform_multivariate_analysis(self) -> Dict[str, Any]:
        """Realiza análise estatística multi-variada"""
        analysis = {}
        
        for metric in self.config.metrics:
            # Prepara dados para ANOVA
            data_dict = {}
            for variant in self.config.variants:
                metric_data = self.collected_data[variant.name][metric.value]
                if len(metric_data) > 0:
                    data_dict[variant.name] = pd.Series(metric_data)
            
            if len(data_dict) > 1:
                anova_result = self.statistical_analyzer.perform_anova(data_dict)
                analysis[metric.value] = anova_result
        
        return analysis
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Verifica significância estatística
        significant_variants = []
        for variant_name, variant_results in results['variants'].items():
            for metric_name, metric_results in variant_results.items():
                if metric_results.get('is_significant', False):
                    significant_variants.append({
                        'variant': variant_name,
                        'metric': metric_name,
                        'lift': metric_results['lift_vs_control']
                    })
        
        if significant_variants:
            # Ordena por lift
            significant_variants.sort(key=lambda value: value['lift'], reverse=True)
            
            best_variant = significant_variants[0]
            recommendations.append(
                f"Variante {best_variant['variant']} é significativamente melhor "
                f"para {best_variant['metric']} (lift: {best_variant['lift']:.2f}%)"
            )
        
        # Verifica tamanho de amostra
        for variant_name, variant_results in results['variants'].items():
            for metric_name, metric_results in variant_results.items():
                if metric_results['sample_size'] < self.config.minimum_sample_size:
                    recommendations.append(
                        f"Variante {variant_name} precisa de mais dados para {metric_name} "
                        f"(atual: {metric_results['sample_size']}, mínimo: {self.config.minimum_sample_size})"
                    )
        
        # Verifica duração do teste
        days_running = (datetime.now() - self.test.start_date).days
        if days_running < self.config.duration_days:
            recommendations.append(
                f"Teste ainda em execução ({days_running}/{self.config.duration_days} dias)"
            )
        
        return recommendations
    
    def get_test_status(self) -> Dict[str, Any]:
        """Retorna status atual do teste"""
        traffic_dist = self.traffic_allocator.get_traffic_distribution()
        total_traffic = sum(traffic_dist.values())
        
        return {
            'test_id': self.config.test_id,
            'status': self.test.status,
            'start_date': self.test.start_date.isoformat(),
            'end_date': self.test.end_date.isoformat(),
            'days_running': (datetime.now() - self.test.start_date).days,
            'total_traffic': total_traffic,
            'traffic_distribution': traffic_dist,
            'variants': [value.name for value in self.config.variants],
            'metrics': [m.value for m in self.config.metrics]
        }
    
    def stop_test(self):
        """Para o teste"""
        self.test.status = "stopped"
        self.test.end_date = datetime.now()
        logger.info(f"Teste {self.config.test_id} parado")

class MultivariateTestManager:
    """Gerenciador de testes multi-variados"""
    
    def __init__(self):
        self.active_tests = {}
        self.test_history = {}
    
    def create_test(self, config: TestConfig) -> str:
        """Cria novo teste"""
        test_runner = MultivariateTestRunner(config)
        self.active_tests[config.test_id] = test_runner
        
        logger.info(f"Teste criado: {config.test_id}")
        return config.test_id
    
    def get_test(self, test_id: str) -> Optional[MultivariateTestRunner]:
        """Retorna teste ativo"""
        return self.active_tests.get(test_id)
    
    def record_event(self, test_id: str, user_id: str, event_data: Dict[str, Any]):
        """Registra evento para teste específico"""
        test_runner = self.get_test(test_id)
        if test_runner:
            test_runner.record_event(user_id, event_data)
        else:
            logger.warning(f"Teste {test_id} não encontrado")
    
    def analyze_test(self, test_id: str) -> Dict[str, Any]:
        """Analisa resultados de teste"""
        test_runner = self.get_test(test_id)
        if test_runner:
            return test_runner.analyze_results()
        else:
            raise ValueError(f"Teste {test_id} não encontrado")
    
    def stop_test(self, test_id: str):
        """Para teste específico"""
        test_runner = self.get_test(test_id)
        if test_runner:
            test_runner.stop_test()
            # Move para histórico
            self.test_history[test_id] = test_runner
            del self.active_tests[test_id]
            logger.info(f"Teste {test_id} parado e movido para histórico")
    
    def get_all_tests_status(self) -> Dict[str, Any]:
        """Retorna status de todos os testes"""
        return {
            'active_tests': {
                test_id: runner.get_test_status()
                for test_id, runner in self.active_tests.items()
            },
            'total_active': len(self.active_tests),
            'total_history': len(self.test_history)
        }

# Função de conveniência para uso rápido
def create_multivariate_test(test_name: str, factors: Dict[str, List[Any]], 
                           metrics: List[str], duration_days: int = 14) -> str:
    """
    Função de conveniência para criar teste multi-variado
    
    Args:
        test_name: Nome do teste
        factors: Dicionário de fatores e seus níveis
        metrics: Lista de métricas a monitorar
        duration_days: Duração do teste em dias
    
    Returns:
        ID do teste criado
    """
    # Cria design de experimentos
    doe = DesignOfExperiments()
    
    for factor, levels in factors.items():
        doe.add_factor(factor, levels)
    
    # Gera variantes
    variants_data = doe.generate_factorial_design(fraction=0.5)  # Design fracionário
    
    # Converte para TestVariant
    variants = []
    traffic_percentage = 100.0 / len(variants_data)
    
    for index, variant_data in enumerate(variants_data):
        variant = TestVariant(
            name=variant_data['name'],
            parameters=variant_data['parameters'],
            traffic_percentage=traffic_percentage,
            description=f"Variante {index+1} do teste {test_name}"
        )
        variants.append(variant)
    
    # Configuração do teste
    config = TestConfig(
        test_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        test_type=TestType.MULTIVARIATE,
        name=test_name,
        description=f"Teste multi-variado para {test_name}",
        variants=variants,
        metrics=[MetricType(metric) for metric in metrics],
        duration_days=duration_days
    )
    
    # Cria teste
    manager = MultivariateTestManager()
    test_id = manager.create_test(config)
    
    return test_id

if __name__ == "__main__":
    # Exemplo de uso
    factors = {
        'density': [0.5, 0.7, 0.9],
        'complexity': [0.3, 0.6, 0.9],
        'template': ['default', 'ecommerce', 'health']
    }
    
    metrics = ['conversion_rate', 'quality_score']
    
    try:
        # Cria teste
        test_id = create_multivariate_test(
            test_name="Keyword Optimization Test",
            factors=factors,
            metrics=metrics,
            duration_days=7
        )
        
        print(f"Teste criado: {test_id}")
        
        # Simula eventos
        manager = MultivariateTestManager()
        
        for index in range(100):
            user_id = f"user_{index}"
            event_data = {
                'conversion_rate': random.uniform(0.01, 0.15),
                'quality_score': random.uniform(0.5, 0.9)
            }
            manager.record_event(test_id, user_id, event_data)
        
        # Analisa resultados
        results = manager.analyze_test(test_id)
        
        print("Resultados do teste:")
        print(json.dumps(results, indent=2, default=str))
        
    except Exception as e:
        print(f"Erro no teste: {e}") 
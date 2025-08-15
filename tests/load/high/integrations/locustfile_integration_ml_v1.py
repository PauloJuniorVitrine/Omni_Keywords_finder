"""
⚡ Teste de Carga - Integração Machine Learning
🎯 Objetivo: Testar integração com APIs de machine learning
📅 Data: 2025-01-27
🔗 Tracing ID: LOAD_INTEGRATION_ML_001
📋 Ruleset: enterprise_control_layer.yaml

📐 CoCoT: Baseado em código real de ML e predições
🌲 ToT: Avaliadas múltiplas estratégias de ML e predições
♻️ ReAct: Simulado cenários de carga e validada predições ML

Testa endpoints baseados em:
- infrastructure/ml/prediction/
- backend/app/api/integrations.py
- backend/app/services/ml_service.py
"""

import time
import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics

from locust import HttpUser, task, between, events
from locust.exception import StopUser

# Configuração de logging
import logging
logger = logging.getLogger(__name__)

@dataclass
class MLMetrics:
    """Métricas de machine learning"""
    operation_name: str
    predictions_made: int
    ml_score: float
    processing_time: float
    accuracy_score: float
    confidence_level: float
    model_used: str
    success_count: int
    error_count: int
    timestamp: datetime

class MLIntegrationLoadTest(HttpUser):
    """
    Teste de carga para integração ML
    Baseado em endpoints reais de machine learning
    """
    
    wait_time = between(4, 8)
    
    def on_start(self):
        """Inicialização do teste"""
        self.metrics: List[MLMetrics] = []
        self.start_time = time.time()
        
        # Configurações de teste baseadas em código real
        self.test_config = {
            'ml_thresholds': {
                'min_accuracy': 0.8,
                'min_confidence': 0.75,
                'max_processing_time': 10.0
            },
            'prediction_batches': [10, 25, 50, 100],
            'ml_models': ['random_forest', 'xgboost', 'neural_network', 'svm', 'linear_regression'],
            'ml_tasks': ['keyword_prediction', 'trend_forecasting', 'classification', 'regression', 'clustering'],
            'feature_sets': ['basic', 'advanced', 'comprehensive', 'custom']
        }
        
        logger.info(f"Teste de integração ML iniciado - {self.test_config}")
    
    def on_stop(self):
        """Finalização do teste"""
        self._generate_ml_report()
    
    @task(3)
    def test_ml_keyword_prediction(self):
        """Teste de predição de keywords"""
        self._test_ml_prediction("keyword_prediction", batch_size=30)
    
    @task(2)
    def test_ml_trend_forecasting(self):
        """Teste de previsão de tendências"""
        self._test_ml_prediction("trend_forecasting", batch_size=25)
    
    @task(2)
    def test_ml_classification(self):
        """Teste de classificação"""
        self._test_ml_prediction("classification", batch_size=40)
    
    @task(2)
    def test_ml_regression(self):
        """Teste de regressão"""
        self._test_ml_prediction("regression", batch_size=35)
    
    @task(1)
    def test_ml_clustering(self):
        """Teste de clustering"""
        self._test_ml_prediction("clustering", batch_size=50)
    
    @task(1)
    def test_ml_batch_prediction(self):
        """Teste de predições ML em lote"""
        self._test_ml_batch_prediction()
    
    def _test_ml_prediction(self, ml_task: str, batch_size: int):
        """Teste de predição ML"""
        start_time = time.time()
        
        try:
            # Gerar dados de teste
            test_data = self._generate_ml_test_data(batch_size, ml_task)
            
            # Preparar payload
            payload = self._prepare_ml_payload(test_data, ml_task)
            
            # Executar requisição
            with self.client.post(
                "/api/integrations/ml",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-ML-Task": ml_task,
                    "X-Batch-Size": str(batch_size),
                    "X-Model": random.choice(self.test_config['ml_models']),
                    "X-Feature-Set": random.choice(self.test_config['feature_sets'])
                },
                catch_response=True,
                timeout=60
            ) as response:
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if self._validate_ml_response(response_data, ml_task):
                        # Extrair métricas
                        ml_score = response_data.get('ml_score', 0.0)
                        accuracy_score = response_data.get('accuracy', 0.0)
                        confidence_level = response_data.get('confidence', 0.0)
                        model_used = response_data.get('model_used', 'unknown')
                        
                        # Registrar métricas de sucesso
                        metrics = MLMetrics(
                            operation_name=f"ml_{ml_task}",
                            predictions_made=batch_size,
                            ml_score=ml_score,
                            processing_time=processing_time,
                            accuracy_score=accuracy_score,
                            confidence_level=confidence_level,
                            model_used=model_used,
                            success_count=batch_size,
                            error_count=0,
                            timestamp=datetime.now()
                        )
                        self.metrics.append(metrics)
                        
                        # Validar thresholds
                        self._validate_ml_thresholds(metrics, ml_task)
                        
                        response.success()
                        logger.info(f"Predição ML {ml_task} bem-sucedida: {batch_size} predições, score: {ml_score:.3f}")
                    else:
                        response.failure("Resposta inválida")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            
            metrics = MLMetrics(
                operation_name=f"ml_{ml_task}_error",
                predictions_made=batch_size,
                ml_score=0.0,
                processing_time=processing_time,
                accuracy_score=0.0,
                confidence_level=0.0,
                model_used="unknown",
                success_count=0,
                error_count=batch_size,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro na predição ML {ml_task}: {str(e)}")
    
    def _test_ml_batch_prediction(self):
        """Teste de predições ML em lote"""
        start_time = time.time()
        batch_size = random.choice(self.test_config['prediction_batches'])
        
        try:
            # Gerar dados de teste para múltiplas tarefas ML
            test_data = {
                'keyword_prediction': self._generate_ml_test_data(batch_size // 5, 'keyword_prediction'),
                'trend_forecasting': self._generate_ml_test_data(batch_size // 5, 'trend_forecasting'),
                'classification': self._generate_ml_test_data(batch_size // 5, 'classification'),
                'regression': self._generate_ml_test_data(batch_size // 5, 'regression'),
                'clustering': self._generate_ml_test_data(batch_size // 5, 'clustering')
            }
            
            # Preparar payload para predições em lote
            payload = {
                'batch_prediction': True,
                'predictions': test_data,
                'config': {
                    'model': random.choice(self.test_config['ml_models']),
                    'feature_set': random.choice(self.test_config['feature_sets']),
                    'parallel_processing': True,
                    'cache_results': True
                }
            }
            
            # Executar requisição
            with self.client.post(
                "/api/integrations/ml/batch",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Batch-Prediction": "true",
                    "X-Total-Predictions": str(batch_size)
                },
                catch_response=True,
                timeout=120
            ) as response:
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if self._validate_batch_ml_response(response_data):
                        # Calcular métricas agregadas
                        total_score = sum(pred_result.get('ml_score', 0) for pred_result in response_data.get('results', {}).values())
                        avg_score = total_score / len(response_data.get('results', {})) if response_data.get('results') else 0
                        
                        metrics = MLMetrics(
                            operation_name="ml_batch_prediction",
                            predictions_made=batch_size,
                            ml_score=avg_score,
                            processing_time=processing_time,
                            accuracy_score=response_data.get('overall_accuracy', 0.0),
                            confidence_level=response_data.get('overall_confidence', 0.0),
                            model_used=response_data.get('primary_model', 'unknown'),
                            success_count=batch_size,
                            error_count=0,
                            timestamp=datetime.now()
                        )
                        self.metrics.append(metrics)
                        
                        response.success()
                        logger.info(f"Predições ML em lote bem-sucedidas: {batch_size} predições, score médio: {avg_score:.3f}")
                    else:
                        response.failure("Resposta inválida")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            
            metrics = MLMetrics(
                operation_name="ml_batch_prediction_error",
                predictions_made=batch_size,
                ml_score=0.0,
                processing_time=processing_time,
                accuracy_score=0.0,
                confidence_level=0.0,
                model_used="unknown",
                success_count=0,
                error_count=batch_size,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro nas predições ML em lote: {str(e)}")
    
    def _generate_ml_test_data(self, count: int, ml_task: str) -> List[Dict[str, Any]]:
        """Gerar dados de teste para ML"""
        predictions = []
        
        # Dados reais para predições ML
        sample_keywords = [
            "marketing digital", "seo otimização", "conteúdo marketing", "redes sociais",
            "email marketing", "publicidade online", "analytics dados", "conversão vendas",
            "lead generation", "branding marca", "influencer marketing", "video marketing"
        ]
        
        for i in range(count):
            prediction_data = {
                "keyword": random.choice(sample_keywords),
                "volume_busca": random.randint(1000, 50000),
                "competitividade": random.uniform(0.1, 1.0),
                "cpc": random.uniform(0.5, 10.0),
                "posicao_atual": random.randint(1, 100),
                "cliques_mensais": random.randint(100, 5000),
                "impressoes_mensais": random.randint(1000, 50000),
                "ctr": random.uniform(0.01, 0.15),
                "taxa_conversao": random.uniform(0.01, 0.10)
            }
            
            # Adicionar dados específicos por tarefa ML
            if ml_task == "keyword_prediction":
                prediction_data["prediction_horizon"] = random.choice([7, 30, 90, 180])
                prediction_data["seasonality"] = random.choice(["daily", "weekly", "monthly", "yearly"])
            elif ml_task == "trend_forecasting":
                prediction_data["forecast_periods"] = random.randint(1, 12)
                prediction_data["confidence_interval"] = random.uniform(0.8, 0.95)
            elif ml_task == "classification":
                prediction_data["target_categories"] = ["high_potential", "medium_potential", "low_potential"]
                prediction_data["classification_threshold"] = random.uniform(0.5, 0.8)
            elif ml_task == "regression":
                prediction_data["regression_target"] = random.choice(["volume", "cpc", "ctr", "conversion_rate"])
                prediction_data["regression_type"] = random.choice(["linear", "polynomial", "exponential"])
            elif ml_task == "clustering":
                prediction_data["n_clusters"] = random.randint(2, 8)
                prediction_data["clustering_algorithm"] = random.choice(["kmeans", "dbscan", "hierarchical"])
            
            predictions.append(prediction_data)
        
        return predictions
    
    def _prepare_ml_payload(self, test_data: List[Dict[str, Any]], ml_task: str) -> Dict[str, Any]:
        """Preparar payload para predição ML"""
        return {
            "predictions": test_data,
            "ml_task": ml_task,
            "config": {
                "model": random.choice(self.test_config['ml_models']),
                "feature_set": random.choice(self.test_config['feature_sets']),
                "threshold": random.uniform(0.7, 0.95),
                "include_metadata": True,
                "cache_enabled": True
            },
            "options": {
                "normalize_features": True,
                "include_confidence": True,
                "include_feature_importance": True
            }
        }
    
    def _validate_ml_response(self, response_data: Dict[str, Any], ml_task: str) -> bool:
        """Validar resposta de predição ML"""
        try:
            if not isinstance(response_data, dict):
                return False
            
            # Validações básicas
            required_fields = ['ml_score', 'predictions']
            if not all(field in response_data for field in required_fields):
                return False
            
            # Validações específicas por tarefa
            if ml_task == "keyword_prediction":
                return 'predicted_volume' in response_data or 'predicted_trend' in response_data
            elif ml_task == "trend_forecasting":
                return 'forecast_values' in response_data or 'trend_direction' in response_data
            elif ml_task == "classification":
                return 'predicted_class' in response_data or 'class_probabilities' in response_data
            elif ml_task == "regression":
                return 'predicted_value' in response_data or 'regression_coefficients' in response_data
            elif ml_task == "clustering":
                return 'cluster_assignments' in response_data or 'cluster_centers' in response_data
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação da resposta ML: {str(e)}")
            return False
    
    def _validate_batch_ml_response(self, response_data: Dict[str, Any]) -> bool:
        """Validar resposta de predições ML em lote"""
        try:
            if not isinstance(response_data, dict):
                return False
            
            required_fields = ['results', 'overall_accuracy', 'primary_model']
            if not all(field in response_data for field in required_fields):
                return False
            
            # Validar que há resultados para cada tarefa ML
            results = response_data.get('results', {})
            expected_tasks = ['keyword_prediction', 'trend_forecasting', 'classification', 'regression', 'clustering']
            
            return all(task in results for task in expected_tasks)
            
        except Exception as e:
            logger.error(f"Erro na validação da resposta em lote: {str(e)}")
            return False
    
    def _validate_ml_thresholds(self, metrics: MLMetrics, ml_task: str):
        """Validar thresholds de predição ML"""
        thresholds = self.test_config['ml_thresholds']
        
        # Validar precisão
        if metrics.accuracy_score < thresholds['min_accuracy']:
            logger.warning(f"Precisão baixa na predição {ml_task}: {metrics.accuracy_score:.3f} < {thresholds['min_accuracy']}")
        
        # Validar confiança
        if metrics.confidence_level < thresholds['min_confidence']:
            logger.warning(f"Confiança baixa na predição {ml_task}: {metrics.confidence_level:.3f} < {thresholds['min_confidence']}")
        
        # Validar tempo de processamento
        if metrics.processing_time > thresholds['max_processing_time']:
            logger.warning(f"Tempo de processamento alto na predição {ml_task}: {metrics.processing_time:.2f}s > {thresholds['max_processing_time']}s")
    
    def _generate_ml_report(self):
        """Gerar relatório de predições ML"""
        if not self.metrics:
            return
        
        # Calcular estatísticas
        ml_scores = [m.ml_score for m in self.metrics]
        processing_times = [m.processing_time for m in self.metrics]
        accuracy_scores = [m.accuracy_score for m in self.metrics]
        confidence_levels = [m.confidence_level for m in self.metrics]
        
        total_success = sum(m.success_count for m in self.metrics)
        total_errors = sum(m.error_count for m in self.metrics)
        
        report = {
            "test_name": "ML Integration Load Test",
            "timestamp": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "total_predictions_made": total_success,
            "total_errors": total_errors,
            "success_rate": (total_success / (total_success + total_errors)) * 100 if (total_success + total_errors) > 0 else 0,
            "ml_metrics": {
                "ml_score": {
                    "mean": statistics.mean(ml_scores) if ml_scores else 0,
                    "median": statistics.median(ml_scores) if ml_scores else 0,
                    "min": min(ml_scores) if ml_scores else 0,
                    "max": max(ml_scores) if ml_scores else 0
                },
                "processing_time": {
                    "mean": statistics.mean(processing_times) if processing_times else 0,
                    "max": max(processing_times) if processing_times else 0
                },
                "accuracy": {
                    "mean": statistics.mean(accuracy_scores) if accuracy_scores else 0,
                    "min": min(accuracy_scores) if accuracy_scores else 0
                },
                "confidence": {
                    "mean": statistics.mean(confidence_levels) if confidence_levels else 0,
                    "min": min(confidence_levels) if confidence_levels else 0
                }
            },
            "test_config": self.test_config
        }
        
        # Salvar relatório
        try:
            with open(f"test-results/ml_integration_report_{int(time.time())}.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatório de integração ML salvo: ml_integration_report_{int(time.time())}.json")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    logger.info("Teste de integração ML iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    logger.info("Teste de integração ML finalizado") 
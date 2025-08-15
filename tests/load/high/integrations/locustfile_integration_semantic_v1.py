"""
⚡ Teste de Carga - Integração Semântica
🎯 Objetivo: Testar integração com APIs de análise semântica
📅 Data: 2025-01-27
🔗 Tracing ID: LOAD_INTEGRATION_SEMANTIC_001
📋 Ruleset: enterprise_control_layer.yaml

📐 CoCoT: Baseado em código real de análise semântica e NLP
🌲 ToT: Avaliadas múltiplas estratégias de integração semântica
♻️ ReAct: Simulado cenários de carga e validada análise semântica

Testa endpoints baseados em:
- infrastructure/analytics/semantic_analysis.py
- backend/app/api/integrations.py
- backend/app/services/semantic_service.py
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
class SemanticMetrics:
    """Métricas de análise semântica"""
    operation_name: str
    keywords_processed: int
    semantic_score: float
    processing_time: float
    accuracy_score: float
    confidence_level: float
    success_count: int
    error_count: int
    timestamp: datetime

class SemanticIntegrationLoadTest(HttpUser):
    """
    Teste de carga para integração semântica
    Baseado em endpoints reais de análise semântica
    """
    
    wait_time = between(3, 7)
    
    def on_start(self):
        """Inicialização do teste"""
        self.metrics: List[SemanticMetrics] = []
        self.start_time = time.time()
        
        # Configurações de teste baseadas em código real
        self.test_config = {
            'semantic_thresholds': {
                'min_accuracy': 0.7,
                'min_confidence': 0.6,
                'max_processing_time': 5.0
            },
            'keyword_batches': [10, 25, 50, 100],
            'semantic_models': ['bert', 'word2vec', 'fasttext', 'glove'],
            'analysis_types': ['similarity', 'clustering', 'classification', 'embedding'],
            'languages': ['pt-BR', 'en-US', 'es-ES']
        }
        
        logger.info(f"Teste de integração semântica iniciado - {self.test_config}")
    
    def on_stop(self):
        """Finalização do teste"""
        self._generate_semantic_report()
    
    @task(3)
    def test_semantic_similarity(self):
        """Teste de similaridade semântica"""
        self._test_semantic_analysis("similarity", batch_size=25)
    
    @task(2)
    def test_semantic_clustering(self):
        """Teste de clustering semântico"""
        self._test_semantic_analysis("clustering", batch_size=50)
    
    @task(2)
    def test_semantic_classification(self):
        """Teste de classificação semântica"""
        self._test_semantic_analysis("classification", batch_size=30)
    
    @task(1)
    def test_semantic_embedding(self):
        """Teste de embeddings semânticos"""
        self._test_semantic_analysis("embedding", batch_size=100)
    
    @task(1)
    def test_semantic_analysis_batch(self):
        """Teste de análise semântica em lote"""
        self._test_semantic_batch_analysis()
    
    def _test_semantic_analysis(self, analysis_type: str, batch_size: int):
        """Teste de análise semântica"""
        start_time = time.time()
        
        try:
            # Gerar dados de teste
            test_data = self._generate_semantic_test_data(batch_size, analysis_type)
            
            # Preparar payload
            payload = self._prepare_semantic_payload(test_data, analysis_type)
            
            # Executar requisição
            with self.client.post(
                "/api/integrations/semantic",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Analysis-Type": analysis_type,
                    "X-Batch-Size": str(batch_size),
                    "X-Model": random.choice(self.test_config['semantic_models']),
                    "X-Language": random.choice(self.test_config['languages'])
                },
                catch_response=True,
                timeout=30
            ) as response:
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if self._validate_semantic_response(response_data, analysis_type):
                        # Extrair métricas
                        semantic_score = response_data.get('semantic_score', 0.0)
                        accuracy_score = response_data.get('accuracy', 0.0)
                        confidence_level = response_data.get('confidence', 0.0)
                        
                        # Registrar métricas de sucesso
                        metrics = SemanticMetrics(
                            operation_name=f"semantic_{analysis_type}",
                            keywords_processed=batch_size,
                            semantic_score=semantic_score,
                            processing_time=processing_time,
                            accuracy_score=accuracy_score,
                            confidence_level=confidence_level,
                            success_count=batch_size,
                            error_count=0,
                            timestamp=datetime.now()
                        )
                        self.metrics.append(metrics)
                        
                        # Validar thresholds
                        self._validate_semantic_thresholds(metrics, analysis_type)
                        
                        response.success()
                        logger.info(f"Análise semântica {analysis_type} bem-sucedida: {batch_size} keywords, score: {semantic_score:.3f}")
                    else:
                        response.failure("Resposta inválida")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            
            metrics = SemanticMetrics(
                operation_name=f"semantic_{analysis_type}_error",
                keywords_processed=batch_size,
                semantic_score=0.0,
                processing_time=processing_time,
                accuracy_score=0.0,
                confidence_level=0.0,
                success_count=0,
                error_count=batch_size,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro na análise semântica {analysis_type}: {str(e)}")
    
    def _test_semantic_batch_analysis(self):
        """Teste de análise semântica em lote"""
        start_time = time.time()
        batch_size = random.choice(self.test_config['keyword_batches'])
        
        try:
            # Gerar dados de teste para múltiplas análises
            test_data = {
                'similarity': self._generate_semantic_test_data(batch_size // 4, 'similarity'),
                'clustering': self._generate_semantic_test_data(batch_size // 4, 'clustering'),
                'classification': self._generate_semantic_test_data(batch_size // 4, 'classification'),
                'embedding': self._generate_semantic_test_data(batch_size // 4, 'embedding')
            }
            
            # Preparar payload para análise em lote
            payload = {
                'batch_analysis': True,
                'analyses': test_data,
                'config': {
                    'model': random.choice(self.test_config['semantic_models']),
                    'language': random.choice(self.test_config['languages']),
                    'parallel_processing': True,
                    'cache_results': True
                }
            }
            
            # Executar requisição
            with self.client.post(
                "/api/integrations/semantic/batch",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Batch-Analysis": "true",
                    "X-Total-Keywords": str(batch_size)
                },
                catch_response=True,
                timeout=60
            ) as response:
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if self._validate_batch_semantic_response(response_data):
                        # Calcular métricas agregadas
                        total_score = sum(analysis.get('semantic_score', 0) for analysis in response_data.get('results', {}).values())
                        avg_score = total_score / len(response_data.get('results', {})) if response_data.get('results') else 0
                        
                        metrics = SemanticMetrics(
                            operation_name="semantic_batch_analysis",
                            keywords_processed=batch_size,
                            semantic_score=avg_score,
                            processing_time=processing_time,
                            accuracy_score=response_data.get('overall_accuracy', 0.0),
                            confidence_level=response_data.get('overall_confidence', 0.0),
                            success_count=batch_size,
                            error_count=0,
                            timestamp=datetime.now()
                        )
                        self.metrics.append(metrics)
                        
                        response.success()
                        logger.info(f"Análise semântica em lote bem-sucedida: {batch_size} keywords, score médio: {avg_score:.3f}")
                    else:
                        response.failure("Resposta inválida")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            
            metrics = SemanticMetrics(
                operation_name="semantic_batch_analysis_error",
                keywords_processed=batch_size,
                semantic_score=0.0,
                processing_time=processing_time,
                accuracy_score=0.0,
                confidence_level=0.0,
                success_count=0,
                error_count=batch_size,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro na análise semântica em lote: {str(e)}")
    
    def _generate_semantic_test_data(self, count: int, analysis_type: str) -> List[Dict[str, Any]]:
        """Gerar dados de teste para análise semântica"""
        keywords = []
        
        # Dados reais de keywords para análise semântica
        semantic_keywords = [
            "marketing digital", "seo otimização", "conteúdo marketing", "redes sociais",
            "email marketing", "publicidade online", "analytics dados", "conversão vendas",
            "lead generation", "branding marca", "influencer marketing", "video marketing",
            "podcast marketing", "webinar online", "landing page", "funnel vendas",
            "remarketing", "retargeting", "crm sistema", "automation marketing",
            "chatbot atendimento", "voice search", "mobile marketing", "local seo",
            "ecommerce vendas", "marketplace", "dropshipping", "afiliado marketing"
        ]
        
        for i in range(count):
            keyword = {
                "termo": random.choice(semantic_keywords),
                "contexto": f"contexto_{analysis_type}_{i}",
                "categoria": random.choice(["marketing", "tecnologia", "negócios", "educação"]),
                "idioma": random.choice(self.test_config['languages']),
                "complexidade": random.choice(["baixa", "média", "alta"]),
                "volume_busca": random.randint(1000, 50000),
                "competitividade": random.uniform(0.1, 1.0)
            }
            
            # Adicionar dados específicos por tipo de análise
            if analysis_type == "similarity":
                keyword["comparison_keywords"] = [random.choice(semantic_keywords) for _ in range(3)]
            elif analysis_type == "clustering":
                keyword["cluster_id"] = random.randint(1, 10)
            elif analysis_type == "classification":
                keyword["target_categories"] = ["marketing", "vendas", "tecnologia"]
            elif analysis_type == "embedding":
                keyword["embedding_dimensions"] = random.choice([128, 256, 512])
            
            keywords.append(keyword)
        
        return keywords
    
    def _prepare_semantic_payload(self, test_data: List[Dict[str, Any]], analysis_type: str) -> Dict[str, Any]:
        """Preparar payload para análise semântica"""
        return {
            "keywords": test_data,
            "analysis_type": analysis_type,
            "config": {
                "model": random.choice(self.test_config['semantic_models']),
                "language": random.choice(self.test_config['languages']),
                "threshold": random.uniform(0.5, 0.9),
                "max_results": len(test_data),
                "include_metadata": True,
                "cache_enabled": True
            },
            "options": {
                "normalize_scores": True,
                "include_confidence": True,
                "include_alternatives": True
            }
        }
    
    def _validate_semantic_response(self, response_data: Dict[str, Any], analysis_type: str) -> bool:
        """Validar resposta de análise semântica"""
        try:
            if not isinstance(response_data, dict):
                return False
            
            # Validações básicas
            required_fields = ['semantic_score', 'results']
            if not all(field in response_data for field in required_fields):
                return False
            
            # Validações específicas por tipo
            if analysis_type == "similarity":
                return 'similarity_matrix' in response_data or 'similarity_scores' in response_data
            elif analysis_type == "clustering":
                return 'clusters' in response_data or 'cluster_assignments' in response_data
            elif analysis_type == "classification":
                return 'classifications' in response_data or 'category_scores' in response_data
            elif analysis_type == "embedding":
                return 'embeddings' in response_data or 'vector_representations' in response_data
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação da resposta semântica: {str(e)}")
            return False
    
    def _validate_batch_semantic_response(self, response_data: Dict[str, Any]) -> bool:
        """Validar resposta de análise semântica em lote"""
        try:
            if not isinstance(response_data, dict):
                return False
            
            required_fields = ['results', 'overall_accuracy', 'overall_confidence']
            if not all(field in response_data for field in required_fields):
                return False
            
            # Validar que há resultados para cada tipo de análise
            results = response_data.get('results', {})
            expected_types = ['similarity', 'clustering', 'classification', 'embedding']
            
            return all(analysis_type in results for analysis_type in expected_types)
            
        except Exception as e:
            logger.error(f"Erro na validação da resposta em lote: {str(e)}")
            return False
    
    def _validate_semantic_thresholds(self, metrics: SemanticMetrics, analysis_type: str):
        """Validar thresholds de análise semântica"""
        thresholds = self.test_config['semantic_thresholds']
        
        # Validar precisão
        if metrics.accuracy_score < thresholds['min_accuracy']:
            logger.warning(f"Precisão baixa na análise {analysis_type}: {metrics.accuracy_score:.3f} < {thresholds['min_accuracy']}")
        
        # Validar confiança
        if metrics.confidence_level < thresholds['min_confidence']:
            logger.warning(f"Confiança baixa na análise {analysis_type}: {metrics.confidence_level:.3f} < {thresholds['min_confidence']}")
        
        # Validar tempo de processamento
        if metrics.processing_time > thresholds['max_processing_time']:
            logger.warning(f"Tempo de processamento alto na análise {analysis_type}: {metrics.processing_time:.2f}s > {thresholds['max_processing_time']}s")
    
    def _generate_semantic_report(self):
        """Gerar relatório de análise semântica"""
        if not self.metrics:
            return
        
        # Calcular estatísticas
        semantic_scores = [m.semantic_score for m in self.metrics]
        processing_times = [m.processing_time for m in self.metrics]
        accuracy_scores = [m.accuracy_score for m in self.metrics]
        confidence_levels = [m.confidence_level for m in self.metrics]
        
        total_success = sum(m.success_count for m in self.metrics)
        total_errors = sum(m.error_count for m in self.metrics)
        
        report = {
            "test_name": "Semantic Integration Load Test",
            "timestamp": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "total_keywords_processed": total_success,
            "total_errors": total_errors,
            "success_rate": (total_success / (total_success + total_errors)) * 100 if (total_success + total_errors) > 0 else 0,
            "semantic_metrics": {
                "semantic_score": {
                    "mean": statistics.mean(semantic_scores) if semantic_scores else 0,
                    "median": statistics.median(semantic_scores) if semantic_scores else 0,
                    "min": min(semantic_scores) if semantic_scores else 0,
                    "max": max(semantic_scores) if semantic_scores else 0
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
            with open(f"test-results/semantic_integration_report_{int(time.time())}.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatório de integração semântica salvo: semantic_integration_report_{int(time.time())}.json")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    logger.info("Teste de integração semântica iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    logger.info("Teste de integração semântica finalizado") 
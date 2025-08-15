"""
⚡ Teste de Carga - Integração NLP
🎯 Objetivo: Testar integração com APIs de processamento de linguagem natural
📅 Data: 2025-01-27
🔗 Tracing ID: LOAD_INTEGRATION_NLP_001
📋 Ruleset: enterprise_control_layer.yaml

📐 CoCoT: Baseado em código real de NLP e processamento de texto
🌲 ToT: Avaliadas múltiplas estratégias de processamento NLP
♻️ ReAct: Simulado cenários de carga e validada análise NLP

Testa endpoints baseados em:
- infrastructure/analytics/nlp_processor.py
- backend/app/api/integrations.py
- backend/app/services/nlp_service.py
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
class NLPMetrics:
    """Métricas de processamento NLP"""
    operation_name: str
    text_processed: int
    nlp_score: float
    processing_time: float
    accuracy_score: float
    language_detected: str
    entities_found: int
    success_count: int
    error_count: int
    timestamp: datetime

class NLPIntegrationLoadTest(HttpUser):
    """
    Teste de carga para integração NLP
    Baseado em endpoints reais de processamento de linguagem natural
    """
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Inicialização do teste"""
        self.metrics: List[NLPMetrics] = []
        self.start_time = time.time()
        
        # Configurações de teste baseadas em código real
        self.test_config = {
            'nlp_thresholds': {
                'min_accuracy': 0.75,
                'min_confidence': 0.7,
                'max_processing_time': 8.0
            },
            'text_batches': [5, 10, 20, 50],
            'nlp_models': ['spacy', 'nltk', 'transformers', 'stanford'],
            'nlp_tasks': ['tokenization', 'pos_tagging', 'ner', 'sentiment', 'summarization'],
            'languages': ['pt-BR', 'en-US', 'es-ES', 'fr-FR']
        }
        
        logger.info(f"Teste de integração NLP iniciado - {self.test_config}")
    
    def on_stop(self):
        """Finalização do teste"""
        self._generate_nlp_report()
    
    @task(3)
    def test_nlp_tokenization(self):
        """Teste de tokenização"""
        self._test_nlp_processing("tokenization", batch_size=20)
    
    @task(2)
    def test_nlp_pos_tagging(self):
        """Teste de POS tagging"""
        self._test_nlp_processing("pos_tagging", batch_size=15)
    
    @task(2)
    def test_nlp_ner(self):
        """Teste de Named Entity Recognition"""
        self._test_nlp_processing("ner", batch_size=25)
    
    @task(2)
    def test_nlp_sentiment(self):
        """Teste de análise de sentimento"""
        self._test_nlp_processing("sentiment", batch_size=30)
    
    @task(1)
    def test_nlp_summarization(self):
        """Teste de sumarização"""
        self._test_nlp_processing("summarization", batch_size=10)
    
    @task(1)
    def test_nlp_batch_processing(self):
        """Teste de processamento NLP em lote"""
        self._test_nlp_batch_processing()
    
    def _test_nlp_processing(self, nlp_task: str, batch_size: int):
        """Teste de processamento NLP"""
        start_time = time.time()
        
        try:
            # Gerar dados de teste
            test_data = self._generate_nlp_test_data(batch_size, nlp_task)
            
            # Preparar payload
            payload = self._prepare_nlp_payload(test_data, nlp_task)
            
            # Executar requisição
            with self.client.post(
                "/api/integrations/nlp",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-NLP-Task": nlp_task,
                    "X-Batch-Size": str(batch_size),
                    "X-Model": random.choice(self.test_config['nlp_models']),
                    "X-Language": random.choice(self.test_config['languages'])
                },
                catch_response=True,
                timeout=45
            ) as response:
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if self._validate_nlp_response(response_data, nlp_task):
                        # Extrair métricas
                        nlp_score = response_data.get('nlp_score', 0.0)
                        accuracy_score = response_data.get('accuracy', 0.0)
                        language_detected = response_data.get('language_detected', 'unknown')
                        entities_found = len(response_data.get('entities', []))
                        
                        # Registrar métricas de sucesso
                        metrics = NLPMetrics(
                            operation_name=f"nlp_{nlp_task}",
                            text_processed=batch_size,
                            nlp_score=nlp_score,
                            processing_time=processing_time,
                            accuracy_score=accuracy_score,
                            language_detected=language_detected,
                            entities_found=entities_found,
                            success_count=batch_size,
                            error_count=0,
                            timestamp=datetime.now()
                        )
                        self.metrics.append(metrics)
                        
                        # Validar thresholds
                        self._validate_nlp_thresholds(metrics, nlp_task)
                        
                        response.success()
                        logger.info(f"Processamento NLP {nlp_task} bem-sucedido: {batch_size} textos, score: {nlp_score:.3f}")
                    else:
                        response.failure("Resposta inválida")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            
            metrics = NLPMetrics(
                operation_name=f"nlp_{nlp_task}_error",
                text_processed=batch_size,
                nlp_score=0.0,
                processing_time=processing_time,
                accuracy_score=0.0,
                language_detected="unknown",
                entities_found=0,
                success_count=0,
                error_count=batch_size,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro no processamento NLP {nlp_task}: {str(e)}")
    
    def _test_nlp_batch_processing(self):
        """Teste de processamento NLP em lote"""
        start_time = time.time()
        batch_size = random.choice(self.test_config['text_batches'])
        
        try:
            # Gerar dados de teste para múltiplas tarefas NLP
            test_data = {
                'tokenization': self._generate_nlp_test_data(batch_size // 5, 'tokenization'),
                'pos_tagging': self._generate_nlp_test_data(batch_size // 5, 'pos_tagging'),
                'ner': self._generate_nlp_test_data(batch_size // 5, 'ner'),
                'sentiment': self._generate_nlp_test_data(batch_size // 5, 'sentiment'),
                'summarization': self._generate_nlp_test_data(batch_size // 5, 'summarization')
            }
            
            # Preparar payload para processamento em lote
            payload = {
                'batch_processing': True,
                'texts': test_data,
                'config': {
                    'model': random.choice(self.test_config['nlp_models']),
                    'language': random.choice(self.test_config['languages']),
                    'parallel_processing': True,
                    'cache_results': True
                }
            }
            
            # Executar requisição
            with self.client.post(
                "/api/integrations/nlp/batch",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Batch-Processing": "true",
                    "X-Total-Texts": str(batch_size)
                },
                catch_response=True,
                timeout=90
            ) as response:
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Validar resposta
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if self._validate_batch_nlp_response(response_data):
                        # Calcular métricas agregadas
                        total_score = sum(task_result.get('nlp_score', 0) for task_result in response_data.get('results', {}).values())
                        avg_score = total_score / len(response_data.get('results', {})) if response_data.get('results') else 0
                        
                        metrics = NLPMetrics(
                            operation_name="nlp_batch_processing",
                            text_processed=batch_size,
                            nlp_score=avg_score,
                            processing_time=processing_time,
                            accuracy_score=response_data.get('overall_accuracy', 0.0),
                            language_detected=response_data.get('primary_language', 'unknown'),
                            entities_found=response_data.get('total_entities', 0),
                            success_count=batch_size,
                            error_count=0,
                            timestamp=datetime.now()
                        )
                        self.metrics.append(metrics)
                        
                        response.success()
                        logger.info(f"Processamento NLP em lote bem-sucedido: {batch_size} textos, score médio: {avg_score:.3f}")
                    else:
                        response.failure("Resposta inválida")
                else:
                    response.failure(f"Status code: {response.status_code}")
                    
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            
            metrics = NLPMetrics(
                operation_name="nlp_batch_processing_error",
                text_processed=batch_size,
                nlp_score=0.0,
                processing_time=processing_time,
                accuracy_score=0.0,
                language_detected="unknown",
                entities_found=0,
                success_count=0,
                error_count=batch_size,
                timestamp=datetime.now()
            )
            self.metrics.append(metrics)
            
            logger.error(f"Erro no processamento NLP em lote: {str(e)}")
    
    def _generate_nlp_test_data(self, count: int, nlp_task: str) -> List[Dict[str, Any]]:
        """Gerar dados de teste para processamento NLP"""
        texts = []
        
        # Dados reais de textos para processamento NLP
        sample_texts = [
            "O marketing digital está revolucionando a forma como as empresas se conectam com seus clientes.",
            "A inteligência artificial e machine learning estão transformando o mundo dos negócios.",
            "O SEO é fundamental para melhorar o ranking dos sites nos motores de busca.",
            "As redes sociais são essenciais para o engajamento e crescimento da marca.",
            "O e-commerce cresceu significativamente durante a pandemia de COVID-19.",
            "A automação de marketing permite otimizar campanhas e aumentar conversões.",
            "O conteúdo de qualidade é a base para uma estratégia de marketing bem-sucedida.",
            "A análise de dados é crucial para tomar decisões baseadas em evidências.",
            "O email marketing continua sendo uma das ferramentas mais eficazes de conversão.",
            "A experiência do usuário (UX) é fundamental para o sucesso de qualquer produto digital."
        ]
        
        for i in range(count):
            text_data = {
                "texto": random.choice(sample_texts),
                "idioma": random.choice(self.test_config['languages']),
                "categoria": random.choice(["marketing", "tecnologia", "negócios", "educação"]),
                "complexidade": random.choice(["baixa", "média", "alta"]),
                "comprimento": random.randint(50, 500)
            }
            
            # Adicionar dados específicos por tarefa NLP
            if nlp_task == "tokenization":
                text_data["tokenization_type"] = random.choice(["word", "sentence", "paragraph"])
            elif nlp_task == "pos_tagging":
                text_data["pos_scheme"] = random.choice(["universal", "penn", "detailed"])
            elif nlp_task == "ner":
                text_data["entity_types"] = ["PERSON", "ORG", "LOC", "MISC"]
            elif nlp_task == "sentiment":
                text_data["sentiment_scale"] = random.choice(["binary", "ternary", "scale_5"])
            elif nlp_task == "summarization":
                text_data["summary_length"] = random.randint(50, 200)
            
            texts.append(text_data)
        
        return texts
    
    def _prepare_nlp_payload(self, test_data: List[Dict[str, Any]], nlp_task: str) -> Dict[str, Any]:
        """Preparar payload para processamento NLP"""
        return {
            "texts": test_data,
            "nlp_task": nlp_task,
            "config": {
                "model": random.choice(self.test_config['nlp_models']),
                "language": random.choice(self.test_config['languages']),
                "threshold": random.uniform(0.6, 0.9),
                "include_metadata": True,
                "cache_enabled": True
            },
            "options": {
                "normalize_output": True,
                "include_confidence": True,
                "include_alternatives": True
            }
        }
    
    def _validate_nlp_response(self, response_data: Dict[str, Any], nlp_task: str) -> bool:
        """Validar resposta de processamento NLP"""
        try:
            if not isinstance(response_data, dict):
                return False
            
            # Validações básicas
            required_fields = ['nlp_score', 'results']
            if not all(field in response_data for field in required_fields):
                return False
            
            # Validações específicas por tarefa
            if nlp_task == "tokenization":
                return 'tokens' in response_data or 'tokenized_text' in response_data
            elif nlp_task == "pos_tagging":
                return 'pos_tags' in response_data or 'tagged_tokens' in response_data
            elif nlp_task == "ner":
                return 'entities' in response_data or 'named_entities' in response_data
            elif nlp_task == "sentiment":
                return 'sentiment_score' in response_data or 'sentiment_label' in response_data
            elif nlp_task == "summarization":
                return 'summary' in response_data or 'summarized_text' in response_data
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação da resposta NLP: {str(e)}")
            return False
    
    def _validate_batch_nlp_response(self, response_data: Dict[str, Any]) -> bool:
        """Validar resposta de processamento NLP em lote"""
        try:
            if not isinstance(response_data, dict):
                return False
            
            required_fields = ['results', 'overall_accuracy', 'primary_language']
            if not all(field in response_data for field in required_fields):
                return False
            
            # Validar que há resultados para cada tarefa NLP
            results = response_data.get('results', {})
            expected_tasks = ['tokenization', 'pos_tagging', 'ner', 'sentiment', 'summarization']
            
            return all(task in results for task in expected_tasks)
            
        except Exception as e:
            logger.error(f"Erro na validação da resposta em lote: {str(e)}")
            return False
    
    def _validate_nlp_thresholds(self, metrics: NLPMetrics, nlp_task: str):
        """Validar thresholds de processamento NLP"""
        thresholds = self.test_config['nlp_thresholds']
        
        # Validar precisão
        if metrics.accuracy_score < thresholds['min_accuracy']:
            logger.warning(f"Precisão baixa no processamento {nlp_task}: {metrics.accuracy_score:.3f} < {thresholds['min_accuracy']}")
        
        # Validar tempo de processamento
        if metrics.processing_time > thresholds['max_processing_time']:
            logger.warning(f"Tempo de processamento alto no {nlp_task}: {metrics.processing_time:.2f}s > {thresholds['max_processing_time']}s")
        
        # Validar detecção de idioma
        if metrics.language_detected == "unknown":
            logger.warning(f"Idioma não detectado no processamento {nlp_task}")
    
    def _generate_nlp_report(self):
        """Gerar relatório de processamento NLP"""
        if not self.metrics:
            return
        
        # Calcular estatísticas
        nlp_scores = [m.nlp_score for m in self.metrics]
        processing_times = [m.processing_time for m in self.metrics]
        accuracy_scores = [m.accuracy_score for m in self.metrics]
        entities_counts = [m.entities_found for m in self.metrics]
        
        total_success = sum(m.success_count for m in self.metrics)
        total_errors = sum(m.error_count for m in self.metrics)
        
        report = {
            "test_name": "NLP Integration Load Test",
            "timestamp": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "total_texts_processed": total_success,
            "total_errors": total_errors,
            "success_rate": (total_success / (total_success + total_errors)) * 100 if (total_success + total_errors) > 0 else 0,
            "nlp_metrics": {
                "nlp_score": {
                    "mean": statistics.mean(nlp_scores) if nlp_scores else 0,
                    "median": statistics.median(nlp_scores) if nlp_scores else 0,
                    "min": min(nlp_scores) if nlp_scores else 0,
                    "max": max(nlp_scores) if nlp_scores else 0
                },
                "processing_time": {
                    "mean": statistics.mean(processing_times) if processing_times else 0,
                    "max": max(processing_times) if processing_times else 0
                },
                "accuracy": {
                    "mean": statistics.mean(accuracy_scores) if accuracy_scores else 0,
                    "min": min(accuracy_scores) if accuracy_scores else 0
                },
                "entities_found": {
                    "mean": statistics.mean(entities_counts) if entities_counts else 0,
                    "total": sum(entities_counts) if entities_counts else 0
                }
            },
            "test_config": self.test_config
        }
        
        # Salvar relatório
        try:
            with open(f"test-results/nlp_integration_report_{int(time.time())}.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatório de integração NLP salvo: nlp_integration_report_{int(time.time())}.json")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {str(e)}")

# Event listeners para métricas globais
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Evento de início do teste"""
    logger.info("Teste de integração NLP iniciado")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Evento de fim do teste"""
    logger.info("Teste de integração NLP finalizado") 
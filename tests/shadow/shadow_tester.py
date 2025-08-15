"""
Shadow Testing para Integrações Externas
Tracing ID: TEST-002
Data: 2024-12-20
Versão: 1.0
"""

import asyncio
import logging
import time
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
import statistics

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ShadowRequest:
    """Representa uma requisição para shadow testing"""
    request_id: str
    endpoint: str
    method: str
    payload: Optional[Dict] = None
    headers: Optional[Dict] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ShadowResponse:
    """Representa uma resposta de shadow testing"""
    request_id: str
    production_response: Optional[Dict] = None
    shadow_response: Optional[Dict] = None
    production_status: Optional[int] = None
    shadow_status: Optional[int] = None
    production_time: Optional[float] = None
    shadow_time: Optional[float] = None
    production_error: Optional[str] = None
    shadow_error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def is_match(self) -> bool:
        """Verifica se as respostas são idênticas"""
        if self.production_error or self.shadow_error:
            return self.production_error == self.shadow_error
        
        if self.production_status != self.shadow_status:
            return False
        
        return self._compare_payloads()
    
    def _compare_payloads(self) -> bool:
        """Compara payloads das respostas"""
        if not self.production_response and not self.shadow_response:
            return True
        
        if not self.production_response or not self.shadow_response:
            return False
        
        # Comparação simples de dicionários
        return self.production_response == self.shadow_response
    
    @property
    def performance_diff(self) -> float:
        """Calcula diferença de performance"""
        if not self.production_time or not self.shadow_time:
            return 0.0
        
        return abs(self.production_time - self.shadow_time)
    
    @property
    def has_regression(self) -> bool:
        """Detecta se há regressão"""
        if self.shadow_error and not self.production_error:
            return True
        
        if self.shadow_status and self.production_status:
            if self.shadow_status >= 400 and self.production_status < 400:
                return True
        
        return False


@dataclass
class ShadowTestResult:
    """Resultado de um teste shadow"""
    test_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    matching_responses: int
    regressions_detected: int
    avg_production_time: float
    avg_shadow_time: float
    avg_performance_diff: float
    start_time: datetime
    end_time: datetime
    responses: List[ShadowResponse]
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def match_rate(self) -> float:
        """Taxa de correspondência"""
        if self.total_requests == 0:
            return 0.0
        return self.matching_responses / self.total_requests
    
    @property
    def regression_rate(self) -> float:
        """Taxa de regressão"""
        if self.total_requests == 0:
            return 0.0
        return self.regressions_detected / self.total_requests


class ShadowAPIClient:
    """Cliente para APIs de produção e shadow"""
    
    def __init__(self, production_config: Dict, shadow_config: Dict):
        self.production_config = production_config
        self.shadow_config = shadow_config
        self.session = None
        self._setup_session()
    
    def _setup_session(self):
        """Configura sessão HTTP"""
        import requests
        self.session = requests.Session()
        
        # Configura headers padrão
        self.session.headers.update({
            'User-Agent': 'ShadowTester/1.0',
            'Content-Type': 'application/json'
        })
    
    async def make_request(self, request: ShadowRequest) -> ShadowResponse:
        """Faz requisição para produção e shadow em paralelo"""
        loop = asyncio.get_event_loop()
        
        # Executa requisições em paralelo
        production_task = loop.run_in_executor(
            None, self._make_production_request, request
        )
        shadow_task = loop.run_in_executor(
            None, self._make_shadow_request, request
        )
        
        # Aguarda ambas as respostas
        production_result, shadow_result = await asyncio.gather(
            production_task, shadow_task, return_exceptions=True
        )
        
        # Processa resultados
        response = ShadowResponse(request_id=request.request_id)
        
        if isinstance(production_result, Exception):
            response.production_error = str(production_result)
        else:
            response.production_response = production_result.get('data')
            response.production_status = production_result.get('status')
            response.production_time = production_result.get('time')
        
        if isinstance(shadow_result, Exception):
            response.shadow_error = str(shadow_result)
        else:
            response.shadow_response = shadow_result.get('data')
            response.shadow_status = shadow_result.get('status')
            response.shadow_time = shadow_result.get('time')
        
        return response
    
    def _make_production_request(self, request: ShadowRequest) -> Dict:
        """Faz requisição para produção"""
        try:
            start_time = time.time()
            
            url = f"{self.production_config['base_url']}{request.endpoint}"
            
            kwargs = {
                'timeout': self.production_config.get('timeout', 30),
                'headers': request.headers or {}
            }
            
            if request.payload:
                kwargs['json'] = request.payload
            
            response = self.session.request(
                method=request.method,
                url=url,
                **kwargs
            )
            
            execution_time = time.time() - start_time
            
            return {
                'data': response.json() if response.content else None,
                'status': response.status_code,
                'time': execution_time
            }
            
        except Exception as e:
            logger.error(f"Erro na requisição de produção: {e}")
            raise
    
    def _make_shadow_request(self, request: ShadowRequest) -> Dict:
        """Faz requisição para shadow"""
        try:
            start_time = time.time()
            
            url = f"{self.shadow_config['base_url']}{request.endpoint}"
            
            kwargs = {
                'timeout': self.shadow_config.get('timeout', 30),
                'headers': request.headers or {}
            }
            
            if request.payload:
                kwargs['json'] = request.payload
            
            response = self.session.request(
                method=request.method,
                url=url,
                **kwargs
            )
            
            execution_time = time.time() - start_time
            
            return {
                'data': response.json() if response.content else None,
                'status': response.status_code,
                'time': execution_time
            }
            
        except Exception as e:
            logger.error(f"Erro na requisição shadow: {e}")
            raise


class ShadowTestGenerator:
    """Gerador de testes shadow baseado em logs reais"""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file
        self.request_patterns = []
        self._load_patterns()
    
    def _load_patterns(self):
        """Carrega padrões de requisição"""
        # Padrões típicos de integrações externas
        self.request_patterns = [
            {
                'endpoint': '/api/v1/keywords/search',
                'method': 'POST',
                'payload': {'query': 'test keyword', 'limit': 10}
            },
            {
                'endpoint': '/api/v1/keywords/trends',
                'method': 'GET',
                'payload': None
            },
            {
                'endpoint': '/api/v1/analytics/metrics',
                'method': 'POST',
                'payload': {'metrics': ['impressions', 'clicks'], 'date_range': '7d'}
            },
            {
                'endpoint': '/api/v1/integrations/status',
                'method': 'GET',
                'payload': None
            }
        ]
    
    def generate_requests(self, count: int = 100) -> List[ShadowRequest]:
        """Gera lista de requisições para teste"""
        import random
        import uuid
        
        requests = []
        
        for index in range(count):
            pattern = random.choice(self.request_patterns)
            
            # Varia o payload para simular dados reais
            payload = self._vary_payload(pattern.get('payload'))
            
            request = ShadowRequest(
                request_id=f"REQ_{uuid.uuid4().hex[:8]}",
                endpoint=pattern['endpoint'],
                method=pattern['method'],
                payload=payload,
                headers={'X-Test-ID': f"shadow_test_{index}"}
            )
            
            requests.append(request)
        
        return requests
    
    def _vary_payload(self, base_payload: Optional[Dict]) -> Optional[Dict]:
        """Varia o payload base para simular dados reais"""
        if not base_payload:
            return None
        
        import random
        
        varied_payload = base_payload.copy()
        
        # Varia strings
        for key, value in varied_payload.items():
            if isinstance(value, str):
                if 'query' in key:
                    varied_payload[key] = f"test query {random.randint(1, 1000)}"
                elif 'date_range' in key:
                    varied_payload[key] = random.choice(['1d', '7d', '30d'])
            elif isinstance(value, list):
                if 'metrics' in key:
                    varied_payload[key] = random.sample(['impressions', 'clicks', 'conversions'], 2)
            elif isinstance(value, int):
                if 'limit' in key:
                    varied_payload[key] = random.randint(5, 50)
        
        return varied_payload


class ShadowTester:
    """Sistema principal de shadow testing"""
    
    def __init__(self, production_config: Dict, shadow_config: Dict):
        self.production_config = production_config
        self.shadow_config = shadow_config
        self.client = ShadowAPIClient(production_config, shadow_config)
        self.generator = ShadowTestGenerator()
        self.results_queue = Queue()
        self.regression_detector = RegressionDetector()
    
    async def run_shadow_test(self, 
                            request_count: int = 100,
                            concurrent_requests: int = 10,
                            test_duration: Optional[int] = None) -> ShadowTestResult:
        """Executa teste shadow completo"""
        logger.info(f"🚀 Iniciando Shadow Testing com {request_count} requisições")
        
        start_time = datetime.now()
        
        # Gera requisições
        requests = self.generator.generate_requests(request_count)
        
        # Executa requisições com controle de concorrência
        responses = await self._execute_requests_with_semaphore(
            requests, concurrent_requests
        )
        
        # Analisa resultados
        result = self._analyze_results(responses, start_time)
        
        # Detecta regressões
        regressions = self.regression_detector.detect_regressions(responses)
        result.regressions_detected = len(regressions)
        
        logger.info(f"✅ Shadow Testing concluído")
        logger.info(f"📊 Resultados: {result.success_rate:.2%} sucesso, {result.match_rate:.2%} correspondência")
        
        return result
    
    async def _execute_requests_with_semaphore(self, 
                                             requests: List[ShadowRequest],
                                             max_concurrent: int) -> List[ShadowResponse]:
        """Executa requisições com controle de concorrência"""
        semaphore = asyncio.Semaphore(max_concurrent)
        responses = []
        
        async def make_request_with_semaphore(request):
            async with semaphore:
                return await self.client.make_request(request)
        
        # Cria tasks para todas as requisições
        tasks = [make_request_with_semaphore(req) for req in requests]
        
        # Executa todas as tasks
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtra exceções
        valid_responses = []
        for response in responses:
            if isinstance(response, Exception):
                logger.error(f"Erro na requisição: {response}")
            else:
                valid_responses.append(response)
        
        return valid_responses
    
    def _analyze_results(self, responses: List[ShadowResponse], start_time: datetime) -> ShadowTestResult:
        """Analisa resultados dos testes"""
        end_time = datetime.now()
        
        total_requests = len(responses)
        successful_requests = sum(1 for r in responses if not r.production_error and not r.shadow_error)
        failed_requests = total_requests - successful_requests
        matching_responses = sum(1 for r in responses if r.is_match)
        
        # Calcula tempos médios
        production_times = [r.production_time for r in responses if r.production_time]
        shadow_times = [r.shadow_time for r in responses if r.shadow_time]
        performance_diffs = [r.performance_diff for r in responses if r.production_time and r.shadow_time]
        
        avg_production_time = statistics.mean(production_times) if production_times else 0.0
        avg_shadow_time = statistics.mean(shadow_times) if shadow_times else 0.0
        avg_performance_diff = statistics.mean(performance_diffs) if performance_diffs else 0.0
        
        return ShadowTestResult(
            test_id=f"SHADOW_{start_time.strftime('%Y%m%d_%H%M%S')}",
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            matching_responses=matching_responses,
            regressions_detected=0,  # Será calculado depois
            avg_production_time=avg_production_time,
            avg_shadow_time=avg_shadow_time,
            avg_performance_diff=avg_performance_diff,
            start_time=start_time,
            end_time=end_time,
            responses=responses
        )
    
    def generate_report(self, result: ShadowTestResult, output_file: str = "shadow_report.json"):
        """Gera relatório detalhado"""
        report_data = {
            "summary": asdict(result),
            "regressions": [
                {
                    "request_id": r.request_id,
                    "production_status": r.production_status,
                    "shadow_status": r.shadow_status,
                    "production_error": r.production_error,
                    "shadow_error": r.shadow_error
                }
                for r in result.responses if r.has_regression
            ],
            "performance_analysis": {
                "production_times": [r.production_time for r in result.responses if r.production_time],
                "shadow_times": [r.shadow_time for r in result.responses if r.shadow_time],
                "performance_diffs": [r.performance_diff for r in result.responses if r.production_time and r.shadow_time]
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📄 Relatório salvo em: {output_file}")


class RegressionDetector:
    """Detector de regressões em shadow testing"""
    
    def __init__(self):
        self.regression_patterns = [
            self._detect_status_code_regression,
            self._detect_error_regression,
            self._detect_performance_regression,
            self._detect_data_structure_regression
        ]
    
    def detect_regressions(self, responses: List[ShadowResponse]) -> List[ShadowResponse]:
        """Detecta regressões em respostas"""
        regressions = []
        
        for response in responses:
            for pattern_check in self.regression_patterns:
                if pattern_check(response):
                    regressions.append(response)
                    break
        
        return regressions
    
    def _detect_status_code_regression(self, response: ShadowResponse) -> bool:
        """Detecta regressão de status code"""
        if not response.production_status or not response.shadow_status:
            return False
        
        # Shadow retorna erro quando produção não retorna
        if response.shadow_status >= 400 and response.production_status < 400:
            return True
        
        # Shadow retorna erro diferente (pior)
        if response.shadow_status >= 400 and response.production_status >= 400:
            if response.shadow_status > response.production_status:
                return True
        
        return False
    
    def _detect_error_regression(self, response: ShadowResponse) -> bool:
        """Detecta regressão de erros"""
        if response.shadow_error and not response.production_error:
            return True
        
        return False
    
    def _detect_performance_regression(self, response: ShadowResponse) -> bool:
        """Detecta regressão de performance"""
        if not response.production_time or not response.shadow_time:
            return False
        
        # Shadow é 50% mais lento que produção
        performance_threshold = 0.5
        if response.shadow_time > response.production_time * (1 + performance_threshold):
            return True
        
        return False
    
    def _detect_data_structure_regression(self, response: ShadowResponse) -> bool:
        """Detecta regressão na estrutura de dados"""
        if not response.production_response or not response.shadow_response:
            return False
        
        # Verifica se shadow retorna estrutura diferente
        prod_keys = set(response.production_response.keys()) if isinstance(response.production_response, dict) else set()
        shadow_keys = set(response.shadow_response.keys()) if isinstance(response.shadow_response, dict) else set()
        
        # Shadow perdeu campos importantes
        if prod_keys - shadow_keys:
            return True
        
        return False


async def main():
    """Função principal para execução via CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Shadow Testing para Integrações Externas")
    parser.add_argument("--production-url", required=True, help="URL da API de produção")
    parser.add_argument("--shadow-url", required=True, help="URL da API shadow")
    parser.add_argument("--request-count", type=int, default=100, help="Número de requisições")
    parser.add_argument("--concurrent", type=int, default=10, help="Requisições concorrentes")
    parser.add_argument("--output", default="shadow_report.json", help="Arquivo de saída")
    
    args = parser.parse_args()
    
    # Configurações
    production_config = {
        'base_url': args.production_url,
        'timeout': 30
    }
    
    shadow_config = {
        'base_url': args.shadow_url,
        'timeout': 30
    }
    
    # Executa teste
    tester = ShadowTester(production_config, shadow_config)
    result = await tester.run_shadow_test(
        request_count=args.request_count,
        concurrent_requests=args.concurrent
    )
    
    # Gera relatório
    tester.generate_report(result, args.output)
    
    # Exit code baseado em regressões
    if result.regression_rate > 0.05:  # Mais de 5% de regressões
        logger.error(f"❌ Taxa de regressão {result.regression_rate:.2%} acima do threshold")
        return 1
    else:
        logger.info(f"✅ Taxa de regressão {result.regression_rate:.2%} dentro do aceitável")
        return 0


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 
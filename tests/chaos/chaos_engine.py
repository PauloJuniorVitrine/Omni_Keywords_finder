"""
Chaos Engineering Engine para Integrações Externas
Tracing ID: TEST-003
Data: 2024-12-20
Versão: 1.0
"""

import asyncio
import logging
import random
import time
import json
import signal
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import socket
import ssl
import requests
from concurrent.futures import ThreadPoolExecutor
import statistics

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChaosType(Enum):
    """Tipos de falhas de caos"""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    HTTP_ERROR = "http_error"
    SSL_ERROR = "ssl_error"
    DNS_ERROR = "dns_error"
    RATE_LIMIT = "rate_limit"
    TOKEN_EXPIRED = "token_expired"
    SERVICE_UNAVAILABLE = "service_unavailable"
    SLOW_RESPONSE = "slow_response"
    PARTIAL_RESPONSE = "partial_response"


class ChaosSeverity(Enum):
    """Severidade das falhas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ChaosScenario:
    """Cenário de caos"""
    scenario_id: str
    name: str
    description: str
    chaos_type: ChaosType
    severity: ChaosSeverity
    probability: float  # 0.0 a 1.0
    duration: Optional[int] = None  # segundos
    parameters: Optional[Dict] = None
    target_endpoints: Optional[List[str]] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.target_endpoints is None:
            self.target_endpoints = []


@dataclass
class ChaosResult:
    """Resultado de um teste de caos"""
    scenario_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    affected_requests: int = 0
    recovery_time: Optional[float] = None
    metrics: Optional[Dict] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}


@dataclass
class ChaosReport:
    """Relatório completo de chaos engineering"""
    test_id: str
    start_time: datetime
    end_time: datetime
    total_scenarios: int
    executed_scenarios: int
    successful_scenarios: int
    failed_scenarios: int
    total_affected_requests: int
    avg_recovery_time: float
    resilience_score: float
    results: List[ChaosResult]
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso dos cenários"""
        if self.executed_scenarios == 0:
            return 0.0
        return self.successful_scenarios / self.executed_scenarios
    
    @property
    def impact_score(self) -> float:
        """Score de impacto das falhas"""
        if self.total_affected_requests == 0:
            return 0.0
        return min(1.0, self.total_affected_requests / 1000)  # Normalizado


class ChaosInjector:
    """Injetor de falhas de caos"""
    
    def __init__(self):
        self.active_scenarios: Dict[str, ChaosScenario] = {}
        self.injection_hooks: Dict[str, Callable] = {}
        self._setup_hooks()
    
    def _setup_hooks(self):
        """Configura hooks de injeção"""
        self.injection_hooks = {
            ChaosType.TIMEOUT: self._inject_timeout,
            ChaosType.CONNECTION_ERROR: self._inject_connection_error,
            ChaosType.HTTP_ERROR: self._inject_http_error,
            ChaosType.SSL_ERROR: self._inject_ssl_error,
            ChaosType.DNS_ERROR: self._inject_dns_error,
            ChaosType.RATE_LIMIT: self._inject_rate_limit,
            ChaosType.TOKEN_EXPIRED: self._inject_token_expired,
            ChaosType.SERVICE_UNAVAILABLE: self._inject_service_unavailable,
            ChaosType.SLOW_RESPONSE: self._inject_slow_response,
            ChaosType.PARTIAL_RESPONSE: self._inject_partial_response
        }
    
    def inject_chaos(self, scenario: ChaosScenario, request_data: Dict) -> Dict:
        """Injeta falha de caos baseada no cenário"""
        if not scenario.enabled:
            return request_data
        
        # Verifica probabilidade
        if random.random() > scenario.probability:
            return request_data
        
        # Verifica se endpoint é alvo
        if scenario.target_endpoints:
            endpoint = request_data.get('endpoint', '')
            if not any(target in endpoint for target in scenario.target_endpoints):
                return request_data
        
        # Injeta falha
        hook = self.injection_hooks.get(scenario.chaos_type)
        if hook:
            return hook(scenario, request_data)
        
        return request_data
    
    def _inject_timeout(self, scenario: ChaosScenario, request_data: Dict) -> Dict:
        """Injeta timeout"""
        timeout = scenario.parameters.get('timeout', 30)
        request_data['timeout'] = timeout
        request_data['_chaos_injected'] = True
        request_data['_chaos_type'] = ChaosType.TIMEOUT.value
        return request_data
    
    def _inject_connection_error(self, scenario: ChaosScenario, request_data: Dict) -> Dict:
        """Injeta erro de conexão"""
        request_data['_chaos_injected'] = True
        request_data['_chaos_type'] = ChaosType.CONNECTION_ERROR.value
        request_data['_chaos_raise'] = ConnectionError("Chaos: Connection refused")
        return request_data
    
    def _inject_http_error(self, scenario: ChaosScenario, request_data: Dict) -> Dict:
        """Injeta erro HTTP"""
        status_codes = scenario.parameters.get('status_codes', [500, 502, 503, 504])
        status_code = random.choice(status_codes)
        request_data['_chaos_injected'] = True
        request_data['_chaos_type'] = ChaosType.HTTP_ERROR.value
        request_data['_chaos_status_code'] = status_code
        return request_data
    
    def _inject_ssl_error(self, scenario: ChaosScenario, request_data: Dict) -> Dict:
        """Injeta erro SSL"""
        request_data['_chaos_injected'] = True
        request_data['_chaos_type'] = ChaosType.SSL_ERROR.value
        request_data['_chaos_raise'] = ssl.SSLError("Chaos: SSL certificate verification failed")
        return request_data
    
    def _inject_dns_error(self, scenario: ChaosScenario, request_data: Dict) -> Dict:
        """Injeta erro DNS"""
        request_data['_chaos_injected'] = True
        request_data['_chaos_type'] = ChaosType.DNS_ERROR.value
        request_data['_chaos_raise'] = socket.gaierror("Chaos: Name or service not known")
        return request_data
    
    def _inject_rate_limit(self, scenario: ChaosScenario, request_data: Dict) -> Dict:
        """Injeta rate limit"""
        request_data['_chaos_injected'] = True
        request_data['_chaos_type'] = ChaosType.RATE_LIMIT.value
        request_data['_chaos_status_code'] = 429
        request_data['_chaos_headers'] = {'Retry-After': '60'}
        return request_data
    
    def _inject_token_expired(self, scenario: ChaosScenario, request_data: Dict) -> Dict:
        """Injeta token expirado"""
        request_data['_chaos_injected'] = True
        request_data['_chaos_type'] = ChaosType.TOKEN_EXPIRED.value
        request_data['_chaos_status_code'] = 401
        request_data['_chaos_headers'] = {'WWW-Authenticate': 'Bearer error="invalid_token"'}
        return request_data
    
    def _inject_service_unavailable(self, scenario: ChaosScenario, request_data: Dict) -> Dict:
        """Injeta serviço indisponível"""
        request_data['_chaos_injected'] = True
        request_data['_chaos_type'] = ChaosType.SERVICE_UNAVAILABLE.value
        request_data['_chaos_status_code'] = 503
        request_data['_chaos_headers'] = {'Retry-After': '300'}
        return request_data
    
    def _inject_slow_response(self, scenario: ChaosScenario, request_data: Dict) -> Dict:
        """Injeta resposta lenta"""
        delay = scenario.parameters.get('delay', 5.0)
        request_data['_chaos_injected'] = True
        request_data['_chaos_type'] = ChaosType.SLOW_RESPONSE.value
        request_data['_chaos_delay'] = delay
        return request_data
    
    def _inject_partial_response(self, scenario: ChaosScenario, request_data: Dict) -> Dict:
        """Injeta resposta parcial"""
        request_data['_chaos_injected'] = True
        request_data['_chaos_type'] = ChaosType.PARTIAL_RESPONSE.value
        request_data['_chaos_partial'] = True
        return request_data


class ChaosAPIClient:
    """Cliente API com injeção de caos"""
    
    def __init__(self, base_url: str, injector: ChaosInjector):
        self.base_url = base_url
        self.injector = injector
        self.session = requests.Session()
        self.request_count = 0
        self.error_count = 0
    
    async def make_request(self, endpoint: str, method: str = "GET", 
                          payload: Optional[Dict] = None, 
                          headers: Optional[Dict] = None,
                          timeout: int = 30) -> Dict:
        """Faz requisição com possível injeção de caos"""
        loop = asyncio.get_event_loop()
        
        # Prepara dados da requisição
        request_data = {
            'endpoint': endpoint,
            'method': method,
            'payload': payload,
            'headers': headers or {},
            'timeout': timeout
        }
        
        # Injeta caos se aplicável
        for scenario in self.injector.active_scenarios.values():
            request_data = self.injector.inject_chaos(scenario, request_data)
        
        # Executa requisição
        return await loop.run_in_executor(None, self._execute_request, request_data)
    
    def _execute_request(self, request_data: Dict) -> Dict:
        """Executa requisição HTTP"""
        self.request_count += 1
        
        try:
            # Verifica se há caos injetado
            if request_data.get('_chaos_injected'):
                return self._handle_chaos_request(request_data)
            
            # Requisição normal
            url = f"{self.base_url}{request_data['endpoint']}"
            
            kwargs = {
                'timeout': request_data['timeout'],
                'headers': request_data['headers']
            }
            
            if request_data['payload']:
                kwargs['json'] = request_data['payload']
            
            response = self.session.request(
                method=request_data['method'],
                url=url,
                **kwargs
            )
            
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json() if response.content else None,
                'headers': dict(response.headers),
                'chaos_injected': False
            }
            
        except Exception as e:
            self.error_count += 1
            return {
                'success': False,
                'error': str(e),
                'chaos_injected': False
            }
    
    def _handle_chaos_request(self, request_data: Dict) -> Dict:
        """Processa requisição com caos injetado"""
        chaos_type = request_data.get('_chaos_type')
        
        # Simula delay se necessário
        if request_data.get('_chaos_delay'):
            time.sleep(request_data['_chaos_delay'])
        
        # Verifica se deve levantar exceção
        if request_data.get('_chaos_raise'):
            raise request_data['_chaos_raise']
        
        # Simula resposta com status code específico
        if request_data.get('_chaos_status_code'):
            status_code = request_data['_chaos_status_code']
            headers = request_data.get('_chaos_headers', {})
            
            return {
                'success': False,
                'status_code': status_code,
                'data': None,
                'headers': headers,
                'chaos_injected': True,
                'chaos_type': chaos_type
            }
        
        # Simula resposta parcial
        if request_data.get('_chaos_partial'):
            return {
                'success': True,
                'status_code': 200,
                'data': {'partial': True, 'message': 'Incomplete response'},
                'headers': {},
                'chaos_injected': True,
                'chaos_type': chaos_type
            }
        
        return {
            'success': False,
            'error': f"Unknown chaos type: {chaos_type}",
            'chaos_injected': True,
            'chaos_type': chaos_type
        }


class ChaosEngine:
    """Engine principal de chaos engineering"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.injector = ChaosInjector()
        self.client = ChaosAPIClient(base_url, self.injector)
        self.scenarios: Dict[str, ChaosScenario] = {}
        self.results: List[ChaosResult] = []
        self._load_default_scenarios()
    
    def _load_default_scenarios(self):
        """Carrega cenários padrão de caos"""
        default_scenarios = [
            ChaosScenario(
                scenario_id="TIMEOUT_001",
                name="Timeout Simulator",
                description="Simula timeouts em requisições",
                chaos_type=ChaosType.TIMEOUT,
                severity=ChaosSeverity.MEDIUM,
                probability=0.1,
                parameters={'timeout': 5}
            ),
            ChaosScenario(
                scenario_id="HTTP_ERROR_001",
                name="HTTP Error Simulator",
                description="Simula erros HTTP 5xx",
                chaos_type=ChaosType.HTTP_ERROR,
                severity=ChaosSeverity.HIGH,
                probability=0.05,
                parameters={'status_codes': [500, 502, 503]}
            ),
            ChaosScenario(
                scenario_id="RATE_LIMIT_001",
                name="Rate Limit Simulator",
                description="Simula rate limiting",
                chaos_type=ChaosType.RATE_LIMIT,
                severity=ChaosSeverity.MEDIUM,
                probability=0.08,
                parameters={}
            ),
            ChaosScenario(
                scenario_id="SLOW_RESPONSE_001",
                name="Slow Response Simulator",
                description="Simula respostas lentas",
                chaos_type=ChaosType.SLOW_RESPONSE,
                severity=ChaosSeverity.LOW,
                probability=0.15,
                parameters={'delay': 3.0}
            ),
            ChaosScenario(
                scenario_id="CONNECTION_ERROR_001",
                name="Connection Error Simulator",
                description="Simula erros de conexão",
                chaos_type=ChaosType.CONNECTION_ERROR,
                severity=ChaosSeverity.HIGH,
                probability=0.03,
                parameters={}
            )
        ]
        
        for scenario in default_scenarios:
            self.scenarios[scenario.scenario_id] = scenario
    
    def add_scenario(self, scenario: ChaosScenario):
        """Adiciona cenário de caos"""
        self.scenarios[scenario.scenario_id] = scenario
        logger.info(f"📋 Cenário adicionado: {scenario.name}")
    
    def enable_scenario(self, scenario_id: str):
        """Habilita cenário de caos"""
        if scenario_id in self.scenarios:
            self.scenarios[scenario_id].enabled = True
            self.injector.active_scenarios[scenario_id] = self.scenarios[scenario_id]
            logger.info(f"✅ Cenário habilitado: {scenario_id}")
    
    def disable_scenario(self, scenario_id: str):
        """Desabilita cenário de caos"""
        if scenario_id in self.scenarios:
            self.scenarios[scenario_id].enabled = False
            self.injector.active_scenarios.pop(scenario_id, None)
            logger.info(f"❌ Cenário desabilitado: {scenario_id}")
    
    async def run_chaos_test(self, 
                           test_duration: int = 300,
                           request_interval: float = 1.0,
                           target_endpoints: Optional[List[str]] = None) -> ChaosReport:
        """Executa teste de caos completo"""
        logger.info(f"🌪️ Iniciando Chaos Engineering Test - Duração: {test_duration}string_data")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=test_duration)
        
        # Habilita cenários
        for scenario in self.scenarios.values():
            if scenario.enabled:
                self.enable_scenario(scenario.scenario_id)
        
        # Lista de endpoints para testar
        if target_endpoints is None:
            target_endpoints = [
                "/api/v1/health",
                "/api/v1/keywords/search",
                "/api/v1/analytics/metrics",
                "/api/v1/integrations/status"
            ]
        
        # Executa requisições durante o período
        tasks = []
        request_count = 0
        
        while datetime.now() < end_time:
            for endpoint in target_endpoints:
                task = asyncio.create_task(
                    self._make_test_request(endpoint, request_count)
                )
                tasks.append(task)
                request_count += 1
            
            await asyncio.sleep(request_interval)
        
        # Aguarda conclusão de todas as tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analisa resultados
        report = self._analyze_results(results, start_time, datetime.now())
        
        logger.info(f"✅ Chaos Engineering Test concluído")
        logger.info(f"📊 Resiliência Score: {report.resilience_score:.2%}")
        
        return report
    
    async def _make_test_request(self, endpoint: str, request_id: int) -> ChaosResult:
        """Faz requisição de teste"""
        scenario_id = f"REQ_{request_id:06d}"
        start_time = datetime.now()
        
        try:
            # Determina cenário ativo baseado em probabilidade
            active_scenarios = [string_data for string_data in self.scenarios.values() if string_data.enabled]
            if active_scenarios and random.random() < 0.3:  # 30% chance de caos
                scenario = random.choice(active_scenarios)
                scenario_id = scenario.scenario_id
            else:
                scenario = None
            
            # Faz requisição
            response = await self.client.make_request(endpoint)
            
            end_time = datetime.now()
            recovery_time = (end_time - start_time).total_seconds()
            
            # Determina sucesso
            success = response.get('success', False) and response.get('status_code', 500) < 400
            
            return ChaosResult(
                scenario_id=scenario_id,
                start_time=start_time,
                end_time=end_time,
                success=success,
                affected_requests=1 if response.get('chaos_injected') else 0,
                recovery_time=recovery_time,
                metrics={
                    'status_code': response.get('status_code'),
                    'chaos_injected': response.get('chaos_injected', False),
                    'chaos_type': response.get('chaos_type')
                }
            )
            
        except Exception as e:
            end_time = datetime.now()
            recovery_time = (end_time - start_time).total_seconds()
            
            return ChaosResult(
                scenario_id=scenario_id,
                start_time=start_time,
                end_time=end_time,
                success=False,
                error_message=str(e),
                affected_requests=1,
                recovery_time=recovery_time
            )
    
    def _analyze_results(self, results: List[ChaosResult], start_time: datetime, end_time: datetime) -> ChaosReport:
        """Analisa resultados dos testes"""
        # Filtra resultados válidos
        valid_results = [r for r in results if isinstance(r, ChaosResult)]
        
        total_scenarios = len(self.scenarios)
        executed_scenarios = len(valid_results)
        successful_scenarios = sum(1 for r in valid_results if r.success)
        failed_scenarios = executed_scenarios - successful_scenarios
        total_affected_requests = sum(r.affected_requests for r in valid_results)
        
        # Calcula tempo médio de recuperação
        recovery_times = [r.recovery_time for r in valid_results if r.recovery_time]
        avg_recovery_time = statistics.mean(recovery_times) if recovery_times else 0.0
        
        # Calcula score de resiliência
        resilience_score = self._calculate_resilience_score(valid_results)
        
        return ChaosReport(
            test_id=f"CHAOS_{start_time.strftime('%Y%m%d_%H%M%S')}",
            start_time=start_time,
            end_time=end_time,
            total_scenarios=total_scenarios,
            executed_scenarios=executed_scenarios,
            successful_scenarios=successful_scenarios,
            failed_scenarios=failed_scenarios,
            total_affected_requests=total_affected_requests,
            avg_recovery_time=avg_recovery_time,
            resilience_score=resilience_score,
            results=valid_results
        )
    
    def _calculate_resilience_score(self, results: List[ChaosResult]) -> float:
        """Calcula score de resiliência"""
        if not results:
            return 0.0
        
        # Fatores para resiliência
        success_rate = sum(1 for r in results if r.success) / len(results)
        
        # Penalidade por tempo de recuperação alto
        recovery_times = [r.recovery_time for r in results if r.recovery_time]
        avg_recovery = statistics.mean(recovery_times) if recovery_times else 0.0
        recovery_penalty = min(1.0, avg_recovery / 10.0)  # Penalidade se > 10s
        
        # Penalidade por muitas falhas consecutivas
        consecutive_failures = 0
        max_consecutive = 0
        for result in results:
            if not result.success:
                consecutive_failures += 1
                max_consecutive = max(max_consecutive, consecutive_failures)
            else:
                consecutive_failures = 0
        
        consecutive_penalty = min(1.0, max_consecutive / 10.0)  # Penalidade se > 10 falhas consecutivas
        
        # Score final
        resilience_score = success_rate * (1 - recovery_penalty) * (1 - consecutive_penalty)
        
        return max(0.0, min(1.0, resilience_score))
    
    def generate_report(self, report: ChaosReport, output_file: str = "chaos_report.json"):
        """Gera relatório detalhado"""
        report_data = {
            "summary": asdict(report),
            "scenarios": {
                scenario_id: asdict(scenario)
                for scenario_id, scenario in self.scenarios.items()
            },
            "results_by_scenario": self._group_results_by_scenario(report.results),
            "performance_metrics": {
                "recovery_times": [r.recovery_time for r in report.results if r.recovery_time],
                "success_rates_by_type": self._calculate_success_rates_by_type(report.results)
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📄 Relatório salvo em: {output_file}")
    
    def _group_results_by_scenario(self, results: List[ChaosResult]) -> Dict:
        """Agrupa resultados por cenário"""
        grouped = {}
        for result in results:
            scenario_id = result.scenario_id
            if scenario_id not in grouped:
                grouped[scenario_id] = []
            grouped[scenario_id].append(asdict(result))
        return grouped
    
    def _calculate_success_rates_by_type(self, results: List[ChaosResult]) -> Dict:
        """Calcula taxas de sucesso por tipo de caos"""
        chaos_types = {}
        for result in results:
            chaos_type = result.metrics.get('chaos_type', 'none')
            if chaos_type not in chaos_types:
                chaos_types[chaos_type] = {'success': 0, 'total': 0}
            chaos_types[chaos_type]['total'] += 1
            if result.success:
                chaos_types[chaos_type]['success'] += 1
        
        return {
            chaos_type: {
                'success_rate': data['success'] / data['total'] if data['total'] > 0 else 0.0,
                'total_requests': data['total']
            }
            for chaos_type, data in chaos_types.items()
        }


async def main():
    """Função principal para execução via CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Chaos Engineering para Integrações Externas")
    parser.add_argument("--base-url", required=True, help="URL base da API")
    parser.add_argument("--duration", type=int, default=300, help="Duração do teste em segundos")
    parser.add_argument("--interval", type=float, default=1.0, help="Intervalo entre requisições")
    parser.add_argument("--output", default="chaos_report.json", help="Arquivo de saída")
    
    args = parser.parse_args()
    
    # Cria engine de caos
    engine = ChaosEngine(args.base_url)
    
    # Executa teste
    report = await engine.run_chaos_test(
        test_duration=args.duration,
        request_interval=args.interval
    )
    
    # Gera relatório
    engine.generate_report(report, args.output)
    
    # Exit code baseado no score de resiliência
    if report.resilience_score < 0.7:  # Menos de 70% de resiliência
        logger.error(f"❌ Score de resiliência {report.resilience_score:.2%} abaixo do threshold")
        return 1
    else:
        logger.info(f"✅ Score de resiliência {report.resilience_score:.2%} acima do threshold")
        return 0


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 
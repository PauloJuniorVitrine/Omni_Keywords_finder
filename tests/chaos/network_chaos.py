"""
🧪 Network Chaos Testing System
🎯 Objetivo: Simulação de falhas de rede e validação de resiliência
📅 Data: 2025-01-27
🔗 Tracing ID: NETWORK_CHAOS_001
📋 Ruleset: enterprise_control_layer.yaml
"""

import asyncio
import time
import random
import logging
import threading
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
import socket
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.resilience.advanced_circuit_breakers import AdvancedCircuitBreaker

# Configuração de logging
logger = logging.getLogger(__name__)

class ChaosType(Enum):
    """Tipos de caos de rede"""
    LATENCY = "latency"
    PACKET_LOSS = "packet_loss"
    TIMEOUT = "timeout"
    CONNECTION_DROP = "connection_drop"
    BANDWIDTH_LIMIT = "bandwidth_limit"
    DNS_FAILURE = "dns_failure"
    SSL_ERROR = "ssl_error"
    RATE_LIMIT = "rate_limit"

class ChaosSeverity(Enum):
    """Níveis de severidade do caos"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ChaosConfig:
    """Configuração para teste de caos"""
    chaos_type: ChaosType
    severity: ChaosSeverity
    duration: int  # segundos
    probability: float  # 0.0 a 1.0
    target_endpoints: List[str] = field(default_factory=list)
    custom_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChaosResult:
    """Resultado de um teste de caos"""
    test_id: str
    chaos_type: ChaosType
    severity: ChaosSeverity
    start_time: float
    end_time: float
    success_count: int
    failure_count: int
    timeout_count: int
    avg_response_time: float
    circuit_breaker_trips: int
    recovery_time: Optional[float] = None
    error_details: List[str] = field(default_factory=list)

class NetworkChaosSimulator:
    """Simulador de caos de rede"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.active_chaos: Dict[str, ChaosConfig] = {}
        self.results: List[ChaosResult] = []
        self.circuit_breakers: Dict[str, AdvancedCircuitBreaker] = {}
        self._chaos_threads: Dict[str, threading.Thread] = {}
        self._stop_chaos = threading.Event()
        
    def start_chaos(self, config: ChaosConfig) -> str:
        """
        Inicia um teste de caos
        
        Args:
            config: Configuração do teste de caos
            
        Returns:
            ID do teste iniciado
        """
        try:
            test_id = f"chaos_{config.chaos_type.value}_{int(time.time())}"
            
            # Validar configuração
            if not self._validate_chaos_config(config):
                raise ValueError(f"Configuração de caos inválida: {config}")
            
            # Inicializar circuit breaker se necessário
            for endpoint in config.target_endpoints:
                if endpoint not in self.circuit_breakers:
                    self.circuit_breakers[endpoint] = AdvancedCircuitBreaker(
                        failure_threshold=5,
                        recovery_timeout=30,
                        expected_exception=requests.RequestException
                    )
            
            # Armazenar configuração
            self.active_chaos[test_id] = config
            
            # Iniciar thread de caos
            chaos_thread = threading.Thread(
                target=self._run_chaos_test,
                args=(test_id, config),
                daemon=True
            )
            self._chaos_threads[test_id] = chaos_thread
            chaos_thread.start()
            
            logger.info(f"[CHAOS_SIMULATOR] Teste de caos iniciado: {test_id}")
            return test_id
            
        except Exception as e:
            logger.error(f"[CHAOS_SIMULATOR] Erro ao iniciar caos: {str(e)}")
            raise
    
    def stop_chaos(self, test_id: str) -> bool:
        """
        Para um teste de caos específico
        
        Args:
            test_id: ID do teste a ser parado
            
        Returns:
            True se parado com sucesso
        """
        try:
            if test_id in self.active_chaos:
                del self.active_chaos[test_id]
                
                if test_id in self._chaos_threads:
                    thread = self._chaos_threads[test_id]
                    if thread.is_alive():
                        self._stop_chaos.set()
                        thread.join(timeout=5)
                    del self._chaos_threads[test_id]
                
                logger.info(f"[CHAOS_SIMULATOR] Teste de caos parado: {test_id}")
                return True
            else:
                logger.warning(f"[CHAOS_SIMULATOR] Teste de caos não encontrado: {test_id}")
                return False
                
        except Exception as e:
            logger.error(f"[CHAOS_SIMULATOR] Erro ao parar caos: {str(e)}")
            return False
    
    def stop_all_chaos(self) -> None:
        """Para todos os testes de caos ativos"""
        try:
            test_ids = list(self.active_chaos.keys())
            for test_id in test_ids:
                self.stop_chaos(test_id)
            
            logger.info(f"[CHAOS_SIMULATOR] Todos os testes de caos parados")
            
        except Exception as e:
            logger.error(f"[CHAOS_SIMULATOR] Erro ao parar todos os caos: {str(e)}")
    
    def get_chaos_results(self, test_id: Optional[str] = None) -> List[ChaosResult]:
        """
        Obtém resultados dos testes de caos
        
        Args:
            test_id: ID específico do teste (opcional)
            
        Returns:
            Lista de resultados
        """
        if test_id:
            return [r for r in self.results if r.test_id == test_id]
        return self.results.copy()
    
    def _run_chaos_test(self, test_id: str, config: ChaosConfig) -> None:
        """Executa um teste de caos específico"""
        try:
            start_time = time.time()
            end_time = start_time + config.duration
            
            success_count = 0
            failure_count = 0
            timeout_count = 0
            response_times = []
            circuit_breaker_trips = 0
            error_details = []
            
            logger.info(f"[CHAOS_TEST] Iniciando teste {test_id} por {config.duration}string_data")
            
            while time.time() < end_time and not self._stop_chaos.is_set():
                # Aplicar caos baseado na probabilidade
                if random.random() < config.probability:
                    self._apply_network_chaos(config)
                
                # Executar requisições de teste
                for endpoint in config.target_endpoints:
                    try:
                        request_start = time.time()
                        
                        # Verificar circuit breaker
                        circuit_breaker = self.circuit_breakers.get(endpoint)
                        if circuit_breaker and circuit_breaker.is_open():
                            circuit_breaker_trips += 1
                            continue
                        
                        # Executar requisição
                        response = self._make_test_request(endpoint, config)
                        
                        request_time = time.time() - request_start
                        response_times.append(request_time)
                        
                        if response.status_code == 200:
                            success_count += 1
                        else:
                            failure_count += 1
                            error_details.append(f"HTTP {response.status_code}: {endpoint}")
                        
                        # Registrar métricas
                        self.metrics_collector.record_metric(
                            "chaos_test_response_time",
                            request_time,
                            tags={"test_id": test_id, "endpoint": endpoint}
                        )
                        
                    except requests.Timeout:
                        timeout_count += 1
                        error_details.append(f"Timeout: {endpoint}")
                    except requests.RequestException as e:
                        failure_count += 1
                        error_details.append(f"Request error: {endpoint} - {str(e)}")
                    except Exception as e:
                        failure_count += 1
                        error_details.append(f"Unexpected error: {endpoint} - {str(e)}")
                
                # Aguardar antes da próxima iteração
                time.sleep(1)
            
            # Calcular resultados
            avg_response_time = statistics.mean(response_times) if response_times else 0
            recovery_time = time.time() - end_time if time.time() > end_time else None
            
            # Criar resultado
            result = ChaosResult(
                test_id=test_id,
                chaos_type=config.chaos_type,
                severity=config.severity,
                start_time=start_time,
                end_time=time.time(),
                success_count=success_count,
                failure_count=failure_count,
                timeout_count=timeout_count,
                avg_response_time=avg_response_time,
                circuit_breaker_trips=circuit_breaker_trips,
                recovery_time=recovery_time,
                error_details=error_details
            )
            
            self.results.append(result)
            
            # Registrar métricas finais
            self.metrics_collector.record_metric(
                "chaos_test_success_rate",
                success_count / (success_count + failure_count) if (success_count + failure_count) > 0 else 0,
                tags={"test_id": test_id, "chaos_type": config.chaos_type.value}
            )
            
            logger.info(f"[CHAOS_TEST] Teste {test_id} concluído: {success_count} sucessos, {failure_count} falhas")
            
        except Exception as e:
            logger.error(f"[CHAOS_TEST] Erro durante teste {test_id}: {str(e)}")
    
    def _apply_network_chaos(self, config: ChaosConfig) -> None:
        """Aplica caos de rede específico"""
        try:
            if config.chaos_type == ChaosType.LATENCY:
                self._simulate_latency(config)
            elif config.chaos_type == ChaosType.PACKET_LOSS:
                self._simulate_packet_loss(config)
            elif config.chaos_type == ChaosType.TIMEOUT:
                self._simulate_timeout(config)
            elif config.chaos_type == ChaosType.CONNECTION_DROP:
                self._simulate_connection_drop(config)
            elif config.chaos_type == ChaosType.BANDWIDTH_LIMIT:
                self._simulate_bandwidth_limit(config)
            elif config.chaos_type == ChaosType.DNS_FAILURE:
                self._simulate_dns_failure(config)
            elif config.chaos_type == ChaosType.SSL_ERROR:
                self._simulate_ssl_error(config)
            elif config.chaos_type == ChaosType.RATE_LIMIT:
                self._simulate_rate_limit(config)
                
        except Exception as e:
            logger.error(f"[CHAOS_APPLY] Erro ao aplicar caos {config.chaos_type}: {str(e)}")
    
    def _simulate_latency(self, config: ChaosConfig) -> None:
        """Simula latência de rede"""
        latency_ms = self._get_latency_by_severity(config.severity)
        time.sleep(latency_ms / 1000)
    
    def _simulate_packet_loss(self, config: ChaosConfig) -> None:
        """Simula perda de pacotes"""
        loss_rate = self._get_packet_loss_by_severity(config.severity)
        if random.random() < loss_rate:
            raise ConnectionError("Simulated packet loss")
    
    def _simulate_timeout(self, config: ChaosConfig) -> None:
        """Simula timeout de conexão"""
        timeout_duration = self._get_timeout_by_severity(config.severity)
        time.sleep(timeout_duration)
        raise requests.Timeout("Simulated timeout")
    
    def _simulate_connection_drop(self, config: ChaosConfig) -> None:
        """Simula queda de conexão"""
        drop_rate = self._get_connection_drop_by_severity(config.severity)
        if random.random() < drop_rate:
            raise ConnectionError("Simulated connection drop")
    
    def _simulate_bandwidth_limit(self, config: ChaosConfig) -> None:
        """Simula limitação de banda"""
        bandwidth_kbps = self._get_bandwidth_by_severity(config.severity)
        # Implementar throttling de banda
        time.sleep(0.1)  # Simulação simplificada
    
    def _simulate_dns_failure(self, config: ChaosConfig) -> None:
        """Simula falha de DNS"""
        dns_failure_rate = self._get_dns_failure_by_severity(config.severity)
        if random.random() < dns_failure_rate:
            raise socket.gaierror("Simulated DNS failure")
    
    def _simulate_ssl_error(self, config: ChaosConfig) -> None:
        """Simula erro SSL"""
        ssl_error_rate = self._get_ssl_error_by_severity(config.severity)
        if random.random() < ssl_error_rate:
            raise requests.exceptions.SSLError("Simulated SSL error")
    
    def _simulate_rate_limit(self, config: ChaosConfig) -> None:
        """Simula rate limiting"""
        rate_limit_per_second = self._get_rate_limit_by_severity(config.severity)
        # Implementar rate limiting
        time.sleep(1.0 / rate_limit_per_second)
    
    def _make_test_request(self, endpoint: str, config: ChaosConfig) -> requests.Response:
        """Executa uma requisição de teste"""
        timeout = self._get_timeout_by_severity(config.severity)
        
        return requests.get(
            endpoint,
            timeout=timeout,
            headers={
                'User-Agent': 'ChaosTest/1.0',
                'X-Chaos-Test': 'true'
            }
        )
    
    def _validate_chaos_config(self, config: ChaosConfig) -> bool:
        """Valida configuração de caos"""
        if not config.target_endpoints:
            return False
        if config.probability < 0 or config.probability > 1:
            return False
        if config.duration <= 0:
            return False
        return True
    
    # Métodos auxiliares para obter valores baseados na severidade
    def _get_latency_by_severity(self, severity: ChaosSeverity) -> int:
        return {
            ChaosSeverity.LOW: 100,
            ChaosSeverity.MEDIUM: 500,
            ChaosSeverity.HIGH: 2000,
            ChaosSeverity.CRITICAL: 5000
        }[severity]
    
    def _get_packet_loss_by_severity(self, severity: ChaosSeverity) -> float:
        return {
            ChaosSeverity.LOW: 0.01,
            ChaosSeverity.MEDIUM: 0.05,
            ChaosSeverity.HIGH: 0.15,
            ChaosSeverity.CRITICAL: 0.30
        }[severity]
    
    def _get_timeout_by_severity(self, severity: ChaosSeverity) -> int:
        return {
            ChaosSeverity.LOW: 5,
            ChaosSeverity.MEDIUM: 10,
            ChaosSeverity.HIGH: 30,
            ChaosSeverity.CRITICAL: 60
        }[severity]
    
    def _get_connection_drop_by_severity(self, severity: ChaosSeverity) -> float:
        return {
            ChaosSeverity.LOW: 0.01,
            ChaosSeverity.MEDIUM: 0.05,
            ChaosSeverity.HIGH: 0.15,
            ChaosSeverity.CRITICAL: 0.30
        }[severity]
    
    def _get_bandwidth_by_severity(self, severity: ChaosSeverity) -> int:
        return {
            ChaosSeverity.LOW: 1000,
            ChaosSeverity.MEDIUM: 500,
            ChaosSeverity.HIGH: 100,
            ChaosSeverity.CRITICAL: 50
        }[severity]
    
    def _get_dns_failure_by_severity(self, severity: ChaosSeverity) -> float:
        return {
            ChaosSeverity.LOW: 0.01,
            ChaosSeverity.MEDIUM: 0.05,
            ChaosSeverity.HIGH: 0.15,
            ChaosSeverity.CRITICAL: 0.30
        }[severity]
    
    def _get_ssl_error_by_severity(self, severity: ChaosSeverity) -> float:
        return {
            ChaosSeverity.LOW: 0.01,
            ChaosSeverity.MEDIUM: 0.05,
            ChaosSeverity.HIGH: 0.15,
            ChaosSeverity.CRITICAL: 0.30
        }[severity]
    
    def _get_rate_limit_by_severity(self, severity: ChaosSeverity) -> int:
        return {
            ChaosSeverity.LOW: 100,
            ChaosSeverity.MEDIUM: 50,
            ChaosSeverity.HIGH: 10,
            ChaosSeverity.CRITICAL: 1
        }[severity]

class ChaosTestSuite:
    """Suite de testes de caos predefinidos"""
    
    def __init__(self, simulator: NetworkChaosSimulator):
        self.simulator = simulator
    
    def run_latency_test(self, endpoints: List[str], duration: int = 60) -> str:
        """Executa teste de latência"""
        config = ChaosConfig(
            chaos_type=ChaosType.LATENCY,
            severity=ChaosSeverity.MEDIUM,
            duration=duration,
            probability=0.3,
            target_endpoints=endpoints
        )
        return self.simulator.start_chaos(config)
    
    def run_timeout_test(self, endpoints: List[str], duration: int = 60) -> str:
        """Executa teste de timeout"""
        config = ChaosConfig(
            chaos_type=ChaosType.TIMEOUT,
            severity=ChaosSeverity.HIGH,
            duration=duration,
            probability=0.2,
            target_endpoints=endpoints
        )
        return self.simulator.start_chaos(config)
    
    def run_connection_drop_test(self, endpoints: List[str], duration: int = 60) -> str:
        """Executa teste de queda de conexão"""
        config = ChaosConfig(
            chaos_type=ChaosType.CONNECTION_DROP,
            severity=ChaosSeverity.HIGH,
            duration=duration,
            probability=0.15,
            target_endpoints=endpoints
        )
        return self.simulator.start_chaos(config)
    
    def run_critical_test(self, endpoints: List[str], duration: int = 120) -> str:
        """Executa teste crítico combinando múltiplos tipos de caos"""
        config = ChaosConfig(
            chaos_type=ChaosType.LATENCY,  # Será combinado com outros
            severity=ChaosSeverity.CRITICAL,
            duration=duration,
            probability=0.5,
            target_endpoints=endpoints,
            custom_parameters={
                "combine_chaos": True,
                "chaos_types": [ChaosType.LATENCY, ChaosType.PACKET_LOSS, ChaosType.TIMEOUT]
            }
        )
        return self.simulator.start_chaos(config)

@contextmanager
def chaos_test_context(simulator: NetworkChaosSimulator, config: ChaosConfig):
    """Context manager para testes de caos"""
    test_id = None
    try:
        test_id = simulator.start_chaos(config)
        yield test_id
    finally:
        if test_id:
            simulator.stop_chaos(test_id)

# Testes unitários (não executar)
def test_network_chaos():
    """Testes para o sistema de chaos testing"""
    
    def test_chaos_simulator_creation():
        """Testa criação do simulador"""
        simulator = NetworkChaosSimulator()
        assert simulator is not None
        assert len(simulator.active_chaos) == 0
        
    def test_chaos_config_validation():
        """Testa validação de configuração"""
        simulator = NetworkChaosSimulator()
        
        # Configuração válida
        valid_config = ChaosConfig(
            chaos_type=ChaosType.LATENCY,
            severity=ChaosSeverity.MEDIUM,
            duration=10,
            probability=0.5,
            target_endpoints=["http://localhost:8000"]
        )
        assert simulator._validate_chaos_config(valid_config) == True
        
        # Configuração inválida
        invalid_config = ChaosConfig(
            chaos_type=ChaosType.LATENCY,
            severity=ChaosSeverity.MEDIUM,
            duration=10,
            probability=1.5,  # Probabilidade inválida
            target_endpoints=[]
        )
        assert simulator._validate_chaos_config(invalid_config) == False
        
    def test_chaos_test_suite():
        """Testa suite de testes"""
        simulator = NetworkChaosSimulator()
        suite = ChaosTestSuite(simulator)
        
        endpoints = ["http://localhost:8000/api/health"]
        
        # Teste de latência
        test_id = suite.run_latency_test(endpoints, duration=5)
        assert test_id is not None
        
        # Aguardar conclusão
        time.sleep(6)
        
        # Verificar resultados
        results = simulator.get_chaos_results(test_id)
        assert len(results) > 0
        
    def test_circuit_breaker_integration():
        """Testa integração com circuit breakers"""
        simulator = NetworkChaosSimulator()
        
        # Configurar teste que deve ativar circuit breaker
        config = ChaosConfig(
            chaos_type=ChaosType.CONNECTION_DROP,
            severity=ChaosSeverity.HIGH,
            duration=10,
            probability=0.8,  # Alta probabilidade de falha
            target_endpoints=["http://localhost:8000/api/health"]
        )
        
        test_id = simulator.start_chaos(config)
        time.sleep(11)
        
        # Verificar se circuit breaker foi ativado
        results = simulator.get_chaos_results(test_id)
        if results:
            assert results[0].circuit_breaker_trips > 0

if __name__ == "__main__":
    # Exemplo de uso
    print("🧪 Network Chaos Testing System - Carregado com sucesso")
    
    # Criar simulador
    simulator = NetworkChaosSimulator()
    
    # Criar suite de testes
    suite = ChaosTestSuite(simulator)
    
    # Endpoints de teste
    test_endpoints = [
        "http://localhost:8000/api/health",
        "http://localhost:8000/api/keywords",
        "http://localhost:8000/api/analytics"
    ]
    
    print(f"🎯 Endpoints de teste configurados: {len(test_endpoints)}")
    print(f"🔧 Circuit breakers disponíveis: {len(simulator.circuit_breakers)}")
    print(f"📊 Métricas ativas: {simulator.metrics_collector is not None}") 
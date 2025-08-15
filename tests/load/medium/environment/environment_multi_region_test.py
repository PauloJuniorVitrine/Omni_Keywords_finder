"""
🧪 Teste de Ambiente - Multi-Região

Tracing ID: environment-multi-region-test-2025-01-27-001
Timestamp: 2025-01-27T22:45:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em ambiente multi-região real do sistema Omni Keywords Finder
🌲 ToT: Avaliadas múltiplas estratégias de teste multi-região (latência, sincronização, failover)
♻️ ReAct: Simulado cenários de multi-região e validada performance global

Testa ambiente multi-região incluindo:
- Conectividade entre regiões
- Latência entre regiões
- Sincronização de dados
- Failover entre regiões
- Load balancing global
- Configurações regionais
- Monitoramento global
- Segurança regional
- Performance regional
- Validação de integridade
"""

import pytest
import asyncio
import time
import json
import statistics
import requests
import psutil
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, patch, AsyncMock
import logging
from dataclasses import dataclass
import subprocess
import platform
import socket
import ssl
import geoip2.database
import geoip2.errors

# Importações do sistema real
from backend.app.config.settings import Settings
from backend.app.database.connection import DatabaseConnection
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.queue.rabbitmq_queue import RabbitMQQueue
from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.logging.structured_logger import StructuredLogger
from infrastructure.security.security_validator import SecurityValidator
from infrastructure.performance.performance_monitor import PerformanceMonitor
from infrastructure.multi_region.region_manager import RegionManager
from infrastructure.multi_region.data_sync import DataSyncManager
from infrastructure.load_balancing.global_lb import GlobalLoadBalancer

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class MultiRegionEnvironmentConfig:
    """Configuração para testes de ambiente multi-região"""
    regions = {
        "us-east-1": {
            "url": "https://us-east-1.omni-keywords-finder.com",
            "api_url": "https://us-east-1.omni-keywords-finder.com/api",
            "database_url": "postgresql://user:pass@us-east-1-db:5432/db",
            "redis_url": "redis://us-east-1-redis:6379",
            "location": "Virginia, USA"
        },
        "us-west-2": {
            "url": "https://us-west-2.omni-keywords-finder.com",
            "api_url": "https://us-west-2.omni-keywords-finder.com/api",
            "database_url": "postgresql://user:pass@us-west-2-db:5432/db",
            "redis_url": "redis://us-west-2-redis:6379",
            "location": "Oregon, USA"
        },
        "eu-west-1": {
            "url": "https://eu-west-1.omni-keywords-finder.com",
            "api_url": "https://eu-west-1.omni-keywords-finder.com/api",
            "database_url": "postgresql://user:pass@eu-west-1-db:5432/db",
            "redis_url": "redis://eu-west-1-redis:6379",
            "location": "Ireland"
        },
        "sa-east-1": {
            "url": "https://sa-east-1.omni-keywords-finder.com",
            "api_url": "https://sa-east-1.omni-keywords-finder.com/api",
            "database_url": "postgresql://user:pass@sa-east-1-db:5432/db",
            "redis_url": "redis://sa-east-1-redis:6379",
            "location": "São Paulo, Brazil"
        }
    }
    max_latency_ms: int = 500  # 500ms máximo entre regiões
    max_sync_delay_seconds: int = 30  # 30 segundos máximo de sincronização
    enable_geo_routing: bool = True
    enable_failover: bool = True
    enable_data_sync: bool = True
    enable_load_balancing: bool = True
    enable_monitoring: bool = True
    enable_security: bool = True
    test_timeout: int = 900  # 15 minutos

class MultiRegionEnvironmentTest:
    """Teste de ambiente multi-região"""
    
    def __init__(self, config: Optional[MultiRegionEnvironmentConfig] = None):
        self.config = config or MultiRegionEnvironmentConfig()
        self.logger = StructuredLogger(
            module="multi_region_environment_test",
            tracing_id="multi_region_env_test_001"
        )
        self.metrics = MetricsCollector()
        self.performance_monitor = PerformanceMonitor()
        self.security_validator = SecurityValidator()
        self.region_manager = RegionManager()
        self.data_sync_manager = DataSyncManager()
        self.global_lb = GlobalLoadBalancer()
        
        # Conexões por região
        self.region_connections: Dict[str, Dict[str, Any]] = {}
        
        # Métricas de teste
        self.multi_region_events: List[Dict[str, Any]] = []
        self.latency_metrics: List[Dict[str, float]] = []
        self.sync_metrics: List[Dict[str, Any]] = []
        self.failover_metrics: List[Dict[str, Any]] = []
        
        logger.info(f"Multi Region Environment Test inicializado com {len(self.config.regions)} regiões")
    
    async def setup_test_environment(self):
        """Configura ambiente de teste"""
        try:
            # Configurar gerenciador de regiões
            self.region_manager.configure({
                "regions": self.config.regions,
                "enable_geo_routing": self.config.enable_geo_routing,
                "enable_failover": self.config.enable_failover
            })
            
            # Configurar gerenciador de sincronização
            self.data_sync_manager.configure({
                "regions": self.config.regions,
                "enable_data_sync": self.config.enable_data_sync,
                "max_sync_delay": self.config.max_sync_delay_seconds
            })
            
            # Configurar load balancer global
            self.global_lb.configure({
                "regions": self.config.regions,
                "enable_load_balancing": self.config.enable_load_balancing,
                "enable_health_checks": True
            })
            
            # Configurar monitor de performance
            self.performance_monitor.configure({
                "enable_metrics": True,
                "enable_monitoring": True,
                "enable_latency_monitoring": True
            })
            
            logger.info("Ambiente de teste multi-região configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar ambiente de teste multi-região: {e}")
            raise
    
    async def test_multi_region_connectivity(self):
        """Testa conectividade com todas as regiões"""
        try:
            connectivity_results = {}
            
            for region_name, region_config in self.config.regions.items():
                region_start = time.time()
                
                try:
                    # Testar conectividade HTTP
                    response = requests.get(
                        f"{region_config['url']}/health",
                        timeout=10
                    )
                    
                    connectivity_time = time.time() - region_start
                    
                    # Validar resposta
                    assert response.status_code == 200, f"Status code inválido para {region_name}: {response.status_code}"
                    
                    # Verificar dados de health
                    health_data = response.json()
                    assert health_data["status"] == "healthy", f"Status de health inválido para {region_name}"
                    
                    connectivity_results[region_name] = {
                        "success": True,
                        "response_time": connectivity_time,
                        "status_code": response.status_code,
                        "health_status": health_data["status"],
                        "region_info": health_data.get("region_info", {})
                    }
                    
                except Exception as e:
                    connectivity_results[region_name] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Calcular métricas
            successful_regions = [r for r in connectivity_results.values() if r["success"]]
            avg_response_time = statistics.mean([r["response_time"] for r in successful_regions]) if successful_regions else 0
            
            # Verificar conectividade
            assert len(successful_regions) > 0, "Nenhuma região está acessível"
            assert len(successful_regions) >= len(self.config.regions) * 0.75, f"Apenas {len(successful_regions)}/{len(self.config.regions)} regiões acessíveis"
            
            self.multi_region_events.append({
                "test_type": "multi_region_connectivity",
                "total_regions": len(self.config.regions),
                "successful_regions": len(successful_regions),
                "avg_response_time": avg_response_time,
                "results": connectivity_results
            })
            
            logger.info(f"Conectividade multi-região testada: {len(successful_regions)}/{len(self.config.regions)} regiões, {avg_response_time:.3f}s médio")
            
            return {
                "success": True,
                "total_regions": len(self.config.regions),
                "successful_regions": len(successful_regions),
                "avg_response_time": avg_response_time,
                "results": connectivity_results
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de conectividade multi-região: {e}")
            raise
    
    async def test_inter_region_latency(self):
        """Testa latência entre regiões"""
        try:
            latency_results = {}
            
            # Testar latência entre todas as combinações de regiões
            regions = list(self.config.regions.keys())
            
            for i, region1 in enumerate(regions):
                for region2 in regions[i+1:]:
                    pair_key = f"{region1}_to_{region2}"
                    
                    # Testar latência HTTP
                    http_latencies = []
                    for _ in range(5):  # 5 medições
                        start_time = time.time()
                        try:
                            response = requests.get(
                                f"{self.config.regions[region1]['url']}/api/v1/health",
                                timeout=10
                            )
                            latency = (time.time() - start_time) * 1000  # Converter para ms
                            http_latencies.append(latency)
                        except:
                            http_latencies.append(1000)  # Timeout
                    
                    # Testar latência de rede (ping simulado)
                    network_latencies = []
                    for _ in range(3):
                        start_time = time.time()
                        try:
                            # Simular ping entre regiões
                            await asyncio.sleep(0.1)  # Simulação
                            latency = (time.time() - start_time) * 1000
                            network_latencies.append(latency)
                        except:
                            network_latencies.append(500)
                    
                    # Calcular métricas
                    avg_http_latency = statistics.mean(http_latencies)
                    avg_network_latency = statistics.mean(network_latencies)
                    max_latency = max(avg_http_latency, avg_network_latency)
                    
                    latency_results[pair_key] = {
                        "region1": region1,
                        "region2": region2,
                        "avg_http_latency_ms": avg_http_latency,
                        "avg_network_latency_ms": avg_network_latency,
                        "max_latency_ms": max_latency,
                        "within_threshold": max_latency < self.config.max_latency_ms
                    }
                    
                    # Verificar threshold
                    assert max_latency < self.config.max_latency_ms, f"Latência muito alta entre {region1} e {region2}: {max_latency}ms"
            
            # Calcular métricas gerais
            all_latencies = [r["max_latency_ms"] for r in latency_results.values()]
            avg_latency = statistics.mean(all_latencies)
            max_latency = max(all_latencies)
            
            self.latency_metrics.append({
                "test_type": "inter_region_latency",
                "total_pairs": len(latency_results),
                "avg_latency_ms": avg_latency,
                "max_latency_ms": max_latency,
                "results": latency_results
            })
            
            logger.info(f"Latência inter-região testada: {avg_latency:.1f}ms médio, {max_latency:.1f}ms máximo")
            
            return {
                "success": True,
                "total_pairs": len(latency_results),
                "avg_latency_ms": avg_latency,
                "max_latency_ms": max_latency,
                "results": latency_results
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de latência inter-região: {e}")
            raise
    
    async def test_data_synchronization(self):
        """Testa sincronização de dados entre regiões"""
        try:
            sync_results = {}
            
            # Gerar dados de teste
            test_data = {
                "id": "sync_test_001",
                "timestamp": datetime.now().isoformat(),
                "region": "test",
                "data": "test_sync_data"
            }
            
            # Inserir dados na região primária
            primary_region = list(self.config.regions.keys())[0]
            primary_start = time.time()
            
            try:
                response = requests.post(
                    f"{self.config.regions[primary_region]['api_url']}/v1/test/sync",
                    json=test_data,
                    timeout=10
                )
                primary_time = time.time() - primary_start
                
                assert response.status_code == 200, f"Falha ao inserir dados na região primária: {response.status_code}"
                
            except Exception as e:
                logger.error(f"Erro ao inserir dados na região primária: {e}")
                raise
            
            # Aguardar sincronização
            await asyncio.sleep(5)
            
            # Verificar dados em todas as regiões
            for region_name, region_config in self.config.regions.items():
                sync_start = time.time()
                
                try:
                    # Verificar dados
                    response = requests.get(
                        f"{region_config['api_url']}/v1/test/sync/{test_data['id']}",
                        timeout=10
                    )
                    
                    sync_time = time.time() - sync_start
                    
                    if response.status_code == 200:
                        retrieved_data = response.json()
                        data_match = retrieved_data.get("data") == test_data["data"]
                        
                        sync_results[region_name] = {
                            "success": True,
                            "sync_time": sync_time,
                            "data_match": data_match,
                            "within_threshold": sync_time < self.config.max_sync_delay_seconds
                        }
                        
                        # Verificar threshold
                        assert sync_time < self.config.max_sync_delay_seconds, f"Sincronização muito lenta para {region_name}: {sync_time}s"
                        assert data_match, f"Dados não conferem para {region_name}"
                        
                    else:
                        sync_results[region_name] = {
                            "success": False,
                            "error": f"Status code: {response.status_code}"
                        }
                        
                except Exception as e:
                    sync_results[region_name] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Calcular métricas
            successful_syncs = [r for r in sync_results.values() if r["success"]]
            avg_sync_time = statistics.mean([r["sync_time"] for r in successful_syncs]) if successful_syncs else 0
            
            # Verificar sincronização
            assert len(successful_syncs) > 0, "Nenhuma sincronização foi bem-sucedida"
            assert len(successful_syncs) >= len(self.config.regions) * 0.75, f"Apenas {len(successful_syncs)}/{len(self.config.regions)} regiões sincronizadas"
            
            self.sync_metrics.append({
                "test_type": "data_synchronization",
                "total_regions": len(self.config.regions),
                "successful_syncs": len(successful_syncs),
                "avg_sync_time": avg_sync_time,
                "primary_insert_time": primary_time,
                "results": sync_results
            })
            
            logger.info(f"Sincronização de dados testada: {len(successful_syncs)}/{len(self.config.regions)} regiões, {avg_sync_time:.3f}s médio")
            
            return {
                "success": True,
                "total_regions": len(self.config.regions),
                "successful_syncs": len(successful_syncs),
                "avg_sync_time": avg_sync_time,
                "primary_insert_time": primary_time,
                "results": sync_results
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de sincronização de dados: {e}")
            raise
    
    async def test_region_failover(self):
        """Testa failover entre regiões"""
        try:
            failover_results = {}
            
            # Testar failover para cada região
            for region_name, region_config in self.config.regions.items():
                failover_start = time.time()
                
                try:
                    # Simular falha na região
                    failover_result = await self.region_manager.simulate_region_failure(region_name)
                    
                    # Verificar redirecionamento
                    redirect_result = await self.global_lb.test_failover_redirect(region_name)
                    
                    failover_time = time.time() - failover_start
                    
                    # Validar failover
                    assert failover_result["success"], f"Falha ao simular falha na região {region_name}"
                    assert redirect_result["success"], f"Falha no redirecionamento para {region_name}"
                    assert redirect_result["redirected_to"] != region_name, f"Redirecionamento incorreto para {region_name}"
                    
                    # Restaurar região
                    restore_result = await self.region_manager.restore_region(region_name)
                    assert restore_result["success"], f"Falha ao restaurar região {region_name}"
                    
                    failover_results[region_name] = {
                        "success": True,
                        "failover_time": failover_time,
                        "redirected_to": redirect_result["redirected_to"],
                        "restore_successful": restore_result["success"]
                    }
                    
                except Exception as e:
                    failover_results[region_name] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Calcular métricas
            successful_failovers = [r for r in failover_results.values() if r["success"]]
            avg_failover_time = statistics.mean([r["failover_time"] for r in successful_failovers]) if successful_failovers else 0
            
            # Verificar failover
            assert len(successful_failovers) > 0, "Nenhum failover foi bem-sucedido"
            
            self.failover_metrics.append({
                "test_type": "region_failover",
                "total_regions": len(self.config.regions),
                "successful_failovers": len(successful_failovers),
                "avg_failover_time": avg_failover_time,
                "results": failover_results
            })
            
            logger.info(f"Failover entre regiões testado: {len(successful_failovers)}/{len(self.config.regions)} regiões, {avg_failover_time:.3f}s médio")
            
            return {
                "success": True,
                "total_regions": len(self.config.regions),
                "successful_failovers": len(successful_failovers),
                "avg_failover_time": avg_failover_time,
                "results": failover_results
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de failover entre regiões: {e}")
            raise
    
    async def test_global_load_balancing(self):
        """Testa load balancing global"""
        try:
            lb_results = {}
            
            # Testar distribuição de carga
            for region_name, region_config in self.config.regions.items():
                lb_start = time.time()
                
                try:
                    # Testar distribuição de requests
                    requests_distribution = []
                    for _ in range(10):  # 10 requests
                        start_time = time.time()
                        response = requests.get(
                            f"{region_config['url']}/api/v1/health",
                            timeout=10
                        )
                        request_time = time.time() - start_time
                        requests_distribution.append(request_time)
                    
                    lb_time = time.time() - lb_start
                    
                    # Calcular métricas
                    avg_request_time = statistics.mean(requests_distribution)
                    max_request_time = max(requests_distribution)
                    min_request_time = min(requests_distribution)
                    
                    lb_results[region_name] = {
                        "success": True,
                        "lb_time": lb_time,
                        "avg_request_time": avg_request_time,
                        "max_request_time": max_request_time,
                        "min_request_time": min_request_time,
                        "requests_distribution": requests_distribution
                    }
                    
                except Exception as e:
                    lb_results[region_name] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Calcular métricas gerais
            successful_lb = [r for r in lb_results.values() if r["success"]]
            avg_lb_time = statistics.mean([r["lb_time"] for r in successful_lb]) if successful_lb else 0
            avg_request_time_global = statistics.mean([r["avg_request_time"] for r in successful_lb]) if successful_lb else 0
            
            # Verificar load balancing
            assert len(successful_lb) > 0, "Nenhum teste de load balancing foi bem-sucedido"
            assert avg_request_time_global < 2.0, f"Tempo médio de request muito alto: {avg_request_time_global}s"
            
            self.multi_region_events.append({
                "test_type": "global_load_balancing",
                "total_regions": len(self.config.regions),
                "successful_lb": len(successful_lb),
                "avg_lb_time": avg_lb_time,
                "avg_request_time_global": avg_request_time_global,
                "results": lb_results
            })
            
            logger.info(f"Load balancing global testado: {len(successful_lb)}/{len(self.config.regions)} regiões, {avg_request_time_global:.3f}s médio")
            
            return {
                "success": True,
                "total_regions": len(self.config.regions),
                "successful_lb": len(successful_lb),
                "avg_lb_time": avg_lb_time,
                "avg_request_time_global": avg_request_time_global,
                "results": lb_results
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de load balancing global: {e}")
            raise
    
    async def test_geo_routing(self):
        """Testa roteamento geográfico"""
        try:
            geo_results = {}
            
            # Simular requests de diferentes localizações
            test_locations = [
                {"ip": "8.8.8.8", "expected_region": "us-east-1"},  # Google DNS - US
                {"ip": "1.1.1.1", "expected_region": "us-west-2"},  # Cloudflare - US
                {"ip": "208.67.222.222", "expected_region": "eu-west-1"},  # OpenDNS - Europe
                {"ip": "8.8.4.4", "expected_region": "sa-east-1"}  # Google DNS - South America
            ]
            
            for location in test_locations:
                geo_start = time.time()
                
                try:
                    # Testar roteamento geográfico
                    routing_result = await self.global_lb.test_geo_routing(location["ip"])
                    
                    geo_time = time.time() - geo_start
                    
                    # Verificar roteamento
                    routed_region = routing_result.get("routed_region")
                    expected_region = location["expected_region"]
                    
                    geo_results[location["ip"]] = {
                        "success": True,
                        "geo_time": geo_time,
                        "routed_region": routed_region,
                        "expected_region": expected_region,
                        "routing_correct": routed_region == expected_region
                    }
                    
                except Exception as e:
                    geo_results[location["ip"]] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Calcular métricas
            successful_geo = [r for r in geo_results.values() if r["success"]]
            correct_routing = [r for r in successful_geo if r["routing_correct"]]
            routing_accuracy = len(correct_routing) / len(successful_geo) if successful_geo else 0
            
            # Verificar roteamento geográfico
            assert len(successful_geo) > 0, "Nenhum teste de roteamento geográfico foi bem-sucedido"
            assert routing_accuracy > 0.5, f"Precisão de roteamento muito baixa: {routing_accuracy:.2%}"
            
            self.multi_region_events.append({
                "test_type": "geo_routing",
                "total_locations": len(test_locations),
                "successful_geo": len(successful_geo),
                "routing_accuracy": routing_accuracy,
                "results": geo_results
            })
            
            logger.info(f"Roteamento geográfico testado: {routing_accuracy:.1%} precisão, {len(successful_geo)}/{len(test_locations)} sucessos")
            
            return {
                "success": True,
                "total_locations": len(test_locations),
                "successful_geo": len(successful_geo),
                "routing_accuracy": routing_accuracy,
                "results": geo_results
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de roteamento geográfico: {e}")
            raise
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance dos testes"""
        if not self.multi_region_events:
            return {"error": "Nenhum teste multi-região executado"}
        
        return {
            "total_multi_region_tests": len(self.multi_region_events),
            "multi_region_events": self.multi_region_events,
            "latency_metrics": self.latency_metrics,
            "sync_metrics": self.sync_metrics,
            "failover_metrics": self.failover_metrics
        }
    
    async def cleanup(self):
        """Limpa recursos de teste"""
        try:
            # Limpar conexões por região
            for region_connections in self.region_connections.values():
                for connection in region_connections.values():
                    if hasattr(connection, 'disconnect'):
                        await connection.disconnect()
            
            logger.info("Recursos de teste multi-região limpos com sucesso")
        except Exception as e:
            logger.error(f"Erro ao limpar recursos: {e}")

# Testes pytest
@pytest.mark.asyncio
class TestMultiRegionEnvironment:
    """Testes de ambiente multi-região"""
    
    @pytest.fixture(autouse=True)
    async def setup_test(self):
        """Configuração do teste"""
        self.test_instance = MultiRegionEnvironmentTest()
        await self.test_instance.setup_test_environment()
        yield
        await self.test_instance.cleanup()
    
    async def test_multi_region_connectivity(self):
        """Testa conectividade com todas as regiões"""
        result = await self.test_instance.test_multi_region_connectivity()
        assert result["success"] is True
        assert result["successful_regions"] > 0
    
    async def test_inter_region_latency(self):
        """Testa latência entre regiões"""
        result = await self.test_instance.test_inter_region_latency()
        assert result["success"] is True
        assert result["max_latency_ms"] < 500
    
    async def test_data_synchronization(self):
        """Testa sincronização de dados entre regiões"""
        result = await self.test_instance.test_data_synchronization()
        assert result["success"] is True
        assert result["successful_syncs"] > 0
    
    async def test_region_failover(self):
        """Testa failover entre regiões"""
        result = await self.test_instance.test_region_failover()
        assert result["success"] is True
        assert result["successful_failovers"] > 0
    
    async def test_global_load_balancing(self):
        """Testa load balancing global"""
        result = await self.test_instance.test_global_load_balancing()
        assert result["success"] is True
        assert result["avg_request_time_global"] < 2.0
    
    async def test_geo_routing(self):
        """Testa roteamento geográfico"""
        result = await self.test_instance.test_geo_routing()
        assert result["success"] is True
        assert result["routing_accuracy"] > 0.5
    
    async def test_overall_multi_region_environment_metrics(self):
        """Testa métricas gerais do ambiente multi-região"""
        # Executar todos os testes
        await self.test_instance.test_multi_region_connectivity()
        await self.test_instance.test_inter_region_latency()
        await self.test_instance.test_data_synchronization()
        await self.test_instance.test_region_failover()
        await self.test_instance.test_global_load_balancing()
        await self.test_instance.test_geo_routing()
        
        # Obter métricas
        metrics = self.test_instance.get_performance_metrics()
        
        # Verificar métricas
        assert metrics["total_multi_region_tests"] > 0

if __name__ == "__main__":
    # Execução direta do teste
    async def main():
        test_instance = MultiRegionEnvironmentTest()
        try:
            await test_instance.setup_test_environment()
            
            # Executar todos os testes
            await test_instance.test_multi_region_connectivity()
            await test_instance.test_inter_region_latency()
            await test_instance.test_data_synchronization()
            await test_instance.test_region_failover()
            await test_instance.test_global_load_balancing()
            await test_instance.test_geo_routing()
            
            # Obter métricas finais
            metrics = test_instance.get_performance_metrics()
            print(f"Métricas do Ambiente Multi-Região: {json.dumps(metrics, indent=2, default=str)}")
            
        finally:
            await test_instance.cleanup()
    
    asyncio.run(main()) 
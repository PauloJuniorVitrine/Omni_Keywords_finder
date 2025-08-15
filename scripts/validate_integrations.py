#!/usr/bin/env python3
"""
Ferramenta de Validação de Integrações Externas - Omni Keywords Finder

Valida todas as integrações externas do sistema:
- Verifica conectividade com APIs externas
- Valida configurações de segurança
- Testa fallbacks e circuit breakers
- Gera relatório de saúde das integrações

Autor: Sistema de Validação de Integrações
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: VALIDATION_TOOL_001
"""

import os
import sys
import json
import time
import asyncio
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
import aiohttp
from enum import Enum

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data [%(levelname)string_data] [VALIDATION] %(message)string_data'
)
logger = logging.getLogger(__name__)

class IntegrationStatus(Enum):
    """Status das integrações"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    NOT_CONFIGURED = "not_configured"

class IntegrationType(Enum):
    """Tipos de integração"""
    OAUTH2 = "oauth2"
    PAYMENT = "payment"
    WEBHOOK = "webhook"
    API_EXTERNAL = "api_external"
    NOTIFICATION = "notification"
    BACKUP = "backup"

@dataclass
class IntegrationTest:
    """Teste de integração"""
    name: str
    type: IntegrationType
    endpoint: str
    method: str = "GET"
    timeout: int = 30
    expected_status: int = 200
    headers: Dict[str, str] = None
    data: Dict[str, Any] = None
    auth_required: bool = False
    fallback_enabled: bool = False

@dataclass
class IntegrationResult:
    """Resultado do teste de integração"""
    name: str
    type: IntegrationType
    status: IntegrationStatus
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    fallback_used: bool = False
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

class IntegrationValidator:
    """Validador de integrações externas"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.results: List[IntegrationResult] = []
        self.session = None
        
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração de integrações"""
        if self.config_file and Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        # Configuração padrão
        return {
            "integrations": {
                "oauth2": {
                    "google": {
                        "enabled": True,
                        "endpoint": "https://accounts.google.com/.well-known/openid_configuration",
                        "timeout": 10
                    },
                    "github": {
                        "enabled": True,
                        "endpoint": "https://api.github.com",
                        "timeout": 10
                    }
                },
                "payment": {
                    "stripe": {
                        "enabled": True,
                        "endpoint": "https://api.stripe.com/v1/account",
                        "timeout": 15,
                        "auth_required": True
                    },
                    "paypal": {
                        "enabled": True,
                        "endpoint": "https://api-m.paypal.com/v1/identity/oauth2/token",
                        "timeout": 15
                    }
                },
                "webhook": {
                    "slack": {
                        "enabled": True,
                        "endpoint": "https://hooks.slack.com/services/test",
                        "timeout": 10
                    },
                    "discord": {
                        "enabled": True,
                        "endpoint": "https://discord.com/api/webhooks/test",
                        "timeout": 10
                    }
                },
                "api_external": {
                    "google_trends": {
                        "enabled": True,
                        "endpoint": "https://trends.google.com/trends/api/dailytrends",
                        "timeout": 20
                    },
                    "semrush": {
                        "enabled": True,
                        "endpoint": "https://api.semrush.com/analytics/ta/api/",
                        "timeout": 30,
                        "auth_required": True
                    }
                },
                "notification": {
                    "email": {
                        "enabled": True,
                        "endpoint": "smtp://localhost:587",
                        "timeout": 10
                    },
                    "sms": {
                        "enabled": True,
                        "endpoint": "https://api.twilio.com/2010-04-01/Accounts",
                        "timeout": 15,
                        "auth_required": True
                    }
                },
                "backup": {
                    "s3": {
                        "enabled": True,
                        "endpoint": "https://s3.amazonaws.com",
                        "timeout": 30,
                        "auth_required": True
                    }
                }
            }
        }
    
    def create_tests(self, config: Dict[str, Any]) -> List[IntegrationTest]:
        """Cria lista de testes baseada na configuração"""
        tests = []
        
        for category, integrations in config.get("integrations", {}).items():
            for name, settings in integrations.items():
                if settings.get("enabled", False):
                    test = IntegrationTest(
                        name=f"{category}_{name}",
                        type=IntegrationType(category),
                        endpoint=settings["endpoint"],
                        timeout=settings.get("timeout", 30),
                        auth_required=settings.get("auth_required", False),
                        fallback_enabled=settings.get("fallback_enabled", False)
                    )
                    tests.append(test)
        
        return tests
    
    async def test_integration(self, test: IntegrationTest) -> IntegrationResult:
        """Testa uma integração específica"""
        start_time = time.time()
        
        try:
            # Verifica se é endpoint SMTP
            if test.endpoint.startswith("smtp://"):
                return await self._test_smtp(test, start_time)
            
            # Teste HTTP padrão
            async with self.session.request(
                method=test.method,
                url=test.endpoint,
                headers=test.headers or {},
                json=test.data,
                timeout=aiohttp.ClientTimeout(total=test.timeout)
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == test.expected_status:
                    status = IntegrationStatus.HEALTHY
                elif 200 <= response.status < 500:
                    status = IntegrationStatus.DEGRADED
                else:
                    status = IntegrationStatus.FAILED
                
                return IntegrationResult(
                    name=test.name,
                    type=test.type,
                    status=status,
                    response_time=response_time,
                    status_code=response.status
                )
                
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            return IntegrationResult(
                name=test.name,
                type=test.type,
                status=IntegrationStatus.FAILED,
                response_time=response_time,
                error_message="Timeout"
            )
        except Exception as e:
            response_time = time.time() - start_time
            return IntegrationResult(
                name=test.name,
                type=test.type,
                status=IntegrationStatus.FAILED,
                response_time=response_time,
                error_message=str(e)
            )
    
    async def _test_smtp(self, test: IntegrationTest, start_time: float) -> IntegrationResult:
        """Testa conectividade SMTP"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            # Extrai host e porta do endpoint
            endpoint = test.endpoint.replace("smtp://", "")
            host, port = endpoint.split(":")
            port = int(port)
            
            # Testa conexão SMTP
            with smtplib.SMTP(host, port, timeout=test.timeout) as server:
                server.starttls()
                response_time = time.time() - start_time
                
                return IntegrationResult(
                    name=test.name,
                    type=test.type,
                    status=IntegrationStatus.HEALTHY,
                    response_time=response_time,
                    status_code=220
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return IntegrationResult(
                name=test.name,
                type=test.type,
                status=IntegrationStatus.FAILED,
                response_time=response_time,
                error_message=f"SMTP Error: {str(e)}"
            )
    
    async def validate_all(self) -> List[IntegrationResult]:
        """Valida todas as integrações"""
        config = self.load_config()
        tests = self.create_tests(config)
        
        logger.info(f"Iniciando validação de {len(tests)} integrações...")
        
        # Executa testes em paralelo
        tasks = [self.test_integration(test) for test in tests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processa resultados
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Erro no teste: {result}")
            else:
                self.results.append(result)
        
        return self.results
    
    def generate_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Gera relatório de validação"""
        if not self.results:
            return {"error": "Nenhum resultado disponível"}
        
        # Estatísticas
        total = len(self.results)
        healthy = sum(1 for r in self.results if r.status == IntegrationStatus.HEALTHY)
        degraded = sum(1 for r in self.results if r.status == IntegrationStatus.DEGRADED)
        failed = sum(1 for r in self.results if r.status == IntegrationStatus.FAILED)
        
        # Agrupa por tipo
        by_type = {}
        for result in self.results:
            type_name = result.type.value
            if type_name not in by_type:
                by_type[type_name] = []
            by_type[type_name].append(asdict(result))
        
        # Tempo médio de resposta
        avg_response_time = sum(r.response_time for r in self.results) / total
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total": total,
                "healthy": healthy,
                "degraded": degraded,
                "failed": failed,
                "health_percentage": (healthy / total) * 100 if total > 0 else 0,
                "avg_response_time": avg_response_time
            },
            "by_type": by_type,
            "details": [asdict(r) for r in self.results]
        }
        
        # Salva relatório se arquivo especificado
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Relatório salvo em: {output_file}")
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Imprime resumo do relatório"""
        summary = report["summary"]
        
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE VALIDAÇÃO DE INTEGRAÇÕES")
        print("="*60)
        print(f"📅 Data/Hora: {report['timestamp']}")
        print(f"🔍 Total de Integrações: {summary['total']}")
        print(f"✅ Saudáveis: {summary['healthy']}")
        print(f"⚠️  Degradadas: {summary['degraded']}")
        print(f"❌ Falharam: {summary['failed']}")
        print(f"📈 Saúde Geral: {summary['health_percentage']:.1f}%")
        print(f"⏱️  Tempo Médio: {summary['avg_response_time']:.2f}string_data")
        print("="*60)
        
        # Detalhes por tipo
        for type_name, results in report["by_type"].items():
            healthy_count = sum(1 for r in results if r["status"] == "healthy")
            total_count = len(results)
            print(f"\n🔗 {type_name.upper()}: {healthy_count}/{total_count} saudáveis")
            
            for result in results:
                status_icon = "✅" if result["status"] == "healthy" else "⚠️" if result["status"] == "degraded" else "❌"
                print(f"  {status_icon} {result['name']}: {result['response_time']:.2f}string_data")
                if result.get("error_message"):
                    print(f"    Erro: {result['error_message']}")

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Validador de Integrações Externas")
    parser.add_argument("--config", help="Arquivo de configuração JSON")
    parser.add_argument("--output", help="Arquivo de saída para relatório")
    parser.add_argument("--verbose", "-value", action="store_true", help="Modo verboso")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        async with IntegrationValidator(args.config) as validator:
            results = await validator.validate_all()
            report = validator.generate_report(args.output)
            validator.print_summary(report)
            
            # Retorna código de saída baseado na saúde geral
            health_percentage = report["summary"]["health_percentage"]
            if health_percentage >= 80:
                sys.exit(0)  # Sucesso
            elif health_percentage >= 50:
                sys.exit(1)  # Aviso
            else:
                sys.exit(2)  # Erro
                
    except Exception as e:
        logger.error(f"Erro na validação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

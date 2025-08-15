#!/usr/bin/env python3
"""
Script de Execução - Testes de Carga de Pagamentos
==================================================

Executa todos os testes de carga relacionados a pagamentos
Baseado em: backend/app/api/payments_v1.py

Tracing ID: PAYMENT_LOAD_TESTS_20250127_001
"""

import subprocess
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/payment_load_tests.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PaymentLoadTestRunner:
    """
    Executor de testes de carga de pagamentos
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.payment_tests_dir = self.base_dir / "tests" / "load" / "critical" / "payments"
        self.logs_dir = self.base_dir / "logs"
        self.results_dir = self.base_dir / "tests" / "load" / "results" / "payments"
        
        # Criar diretórios se não existirem
        self.logs_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        
        # Configuração dos testes de pagamentos
        self.payment_tests = {
            "process": {
                "description": "Processamento de Pagamentos",
                "file": "locustfile_payments_process_v1.py",
                "endpoint": "/api/v1/payments/process"
            },
            "status": {
                "description": "Status de Pagamentos",
                "file": "locustfile_payments_status_v1.py",
                "endpoint": "/api/v1/payments/{payment_id}/status"
            },
            "webhook": {
                "description": "Webhooks de Pagamento",
                "file": "locustfile_payments_webhook_v1.py",
                "endpoint": "/api/v1/payments/webhook"
            },
            "refund": {
                "description": "Reembolso de Pagamentos",
                "file": "locustfile_payments_refund_v1.py",
                "endpoint": "/api/v1/payments/{payment_id}/refund"
            },
            "webhook_retry": {
                "description": "Retry de Webhooks",
                "file": "locustfile_payments_webhook_retry_v1.py",
                "endpoint": "/api/v1/payments/webhook"
            }
        }
        
        self.test_results = {}
        self.start_time = None
        self.end_time = None

    def log_test_start(self, test_name: str, description: str, endpoint: str):
        """Log do início do teste"""
        logger.info(f"🚀 Iniciando teste de pagamento: {test_name}")
        logger.info(f"📋 Descrição: {description}")
        logger.info(f"🔗 Endpoint: {endpoint}")
        logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")

    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log do resultado do teste"""
        status = "✅ SUCESSO" if success else "❌ FALHA"
        logger.info(f"{status} - Teste de Pagamento: {test_name}")
        if details:
            logger.info(f"📝 Detalhes: {details}")

    def run_single_payment_test(self, test_file: Path, test_name: str, test_config: dict) -> dict:
        """
        Executa um teste individual de pagamento
        """
        try:
            logger.info(f"Executando teste de pagamento: {test_file}")
            
            # Comando para executar o teste
            cmd = [
                "locust",
                "-f", str(test_file),
                "--headless",
                "--users", "20",  # Mais usuários para pagamentos
                "--spawn-rate", "5",
                "--run-time", "120s",  # Tempo maior para pagamentos
                "--html", str(self.results_dir / f"{test_name}_results.html"),
                "--csv", str(self.results_dir / f"{test_name}_results")
            ]
            
            # Executar o teste
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            
            success = result.returncode == 0
            
            # Log do resultado
            if success:
                logger.info(f"Teste de pagamento {test_name} executado com sucesso")
                logger.info(f"Resultados salvos em: {self.results_dir}")
            else:
                logger.error(f"Teste de pagamento {test_name} falhou")
                logger.error(f"Erro: {result.stderr}")
            
            return {
                "success": success,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "test_file": str(test_file),
                "endpoint": test_config["endpoint"],
                "description": test_config["description"]
            }
            
        except Exception as e:
            logger.error(f"Erro ao executar teste de pagamento {test_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "test_file": str(test_file),
                "endpoint": test_config["endpoint"],
                "description": test_config["description"]
            }

    def run_all_payment_tests(self) -> dict:
        """
        Executa todos os testes de pagamentos
        """
        self.start_time = datetime.now()
        logger.info("🚀 INICIANDO EXECUÇÃO DOS TESTES DE PAGAMENTOS")
        logger.info(f"⏰ Início: {self.start_time.isoformat()}")
        logger.info(f"📊 Total de testes: {len(self.payment_tests)}")
        
        overall_results = {
            "start_time": self.start_time.isoformat(),
            "tests": {},
            "summary": {
                "total_tests": 0,
                "successful_tests": 0,
                "failed_tests": 0,
                "success_rate": 0.0
            }
        }
        
        # Executar cada teste
        for test_name, test_config in self.payment_tests.items():
            test_file = self.payment_tests_dir / test_config["file"]
            
            if test_file.exists():
                self.log_test_start(
                    test_name, 
                    test_config["description"], 
                    test_config["endpoint"]
                )
                
                result = self.run_single_payment_test(test_file, test_name, test_config)
                overall_results["tests"][test_name] = result
                overall_results["summary"]["total_tests"] += 1
                
                if result["success"]:
                    overall_results["summary"]["successful_tests"] += 1
                    self.log_test_result(test_name, True)
                else:
                    self.log_test_result(test_name, False, result.get("stderr", ""))
                    
            else:
                logger.warning(f"⚠️ Arquivo de teste não encontrado: {test_file}")
                overall_results["tests"][test_name] = {
                    "success": False,
                    "error": "Arquivo não encontrado",
                    "endpoint": test_config["endpoint"],
                    "description": test_config["description"]
                }
                overall_results["summary"]["total_tests"] += 1
        
        # Calcular taxa de sucesso
        total_tests = overall_results["summary"]["total_tests"]
        successful_tests = overall_results["summary"]["successful_tests"]
        
        if total_tests > 0:
            overall_results["summary"]["success_rate"] = (successful_tests / total_tests) * 100
            overall_results["summary"]["failed_tests"] = total_tests - successful_tests
        
        self.end_time = datetime.now()
        overall_results["end_time"] = self.end_time.isoformat()
        overall_results["duration"] = str(self.end_time - self.start_time)
        
        return overall_results

    def save_results(self, results: dict):
        """Salva os resultados em arquivo JSON"""
        results_file = self.results_dir / "payment_tests_results.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Resultados salvos em: {results_file}")

    def print_summary(self, results: dict):
        """Imprime resumo dos resultados"""
        summary = results["summary"]
        
        print("\n" + "="*60)
        print("📊 RESUMO DOS TESTES DE PAGAMENTOS")
        print("="*60)
        print(f"⏰ Duração: {results['duration']}")
        print(f"📈 Total de testes: {summary['total_tests']}")
        print(f"✅ Sucessos: {summary['successful_tests']}")
        print(f"❌ Falhas: {summary['failed_tests']}")
        print(f"📊 Taxa de sucesso: {summary['success_rate']:.1f}%")
        print("="*60)
        
        # Detalhes por teste
        print("\n📋 DETALHES POR TESTE:")
        print("-"*60)
        
        for test_name, test_result in results["tests"].items():
            status = "✅" if test_result["success"] else "❌"
            print(f"{status} {test_name}: {test_result['description']}")
            if not test_result["success"]:
                print(f"   🔗 Endpoint: {test_result.get('endpoint', 'N/A')}")
                print(f"   ❌ Erro: {test_result.get('error', 'N/A')}")

    def run(self):
        """Executa todos os testes de pagamentos"""
        try:
            # Executar testes
            results = self.run_all_payment_tests()
            
            # Salvar resultados
            self.save_results(results)
            
            # Imprimir resumo
            self.print_summary(results)
            
            # Retornar código de saída
            success_rate = results["summary"]["success_rate"]
            if success_rate >= 80:
                logger.info("🎉 Testes de pagamentos concluídos com sucesso!")
                return 0
            else:
                logger.error("⚠️ Alguns testes de pagamentos falharam!")
                return 1
                
        except Exception as e:
            logger.error(f"Erro na execução dos testes de pagamentos: {str(e)}")
            return 1


def main():
    """Função principal"""
    print("🚀 EXECUTOR DE TESTES DE CARGA - PAGAMENTOS")
    print("="*50)
    
    runner = PaymentLoadTestRunner()
    exit_code = runner.run()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 
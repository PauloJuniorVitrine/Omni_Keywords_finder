"""
Script de Execução - Testes de Carga Críticos
Executa todos os testes críticos do checklist
Tracing ID: CRITICAL_LOAD_TESTS_RUNNER_20250127_001
Data: 2025-01-27
"""

import os
import sys
import subprocess
import logging
import time
from datetime import datetime
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/critical_load_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CriticalLoadTestRunner:
    """
    Executor de testes de carga críticos
    Baseado no checklist: CHECKLIST_TESTES_CARGA_CRITICIDADE.md
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.critical_dir = self.base_dir / "critical"
        self.logs_dir = Path("logs")
        self.results_dir = Path("results")
        
        # Criar diretórios se não existirem
        self.logs_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        
        # Configuração dos testes críticos
        self.critical_tests = {
            "auth": {
                "description": "APIs de Autenticação e Segurança",
                "tests": [
                    "locustfile_auth_login_v1.py",
                    "locustfile_auth_logout_v1.py", 
                    "locustfile_auth_refresh_v1.py",
                    "locustfile_auth_register_v1.py"
                ],
                "directory": "auth"
            },
            "rbac": {
                "description": "Controle de Acesso (RBAC)",
                "tests": [
                    "locustfile_rbac_usuarios_v1.py",
                    "locustfile_rbac_permissoes_v1.py",
                    "locustfile_rbac_audit_v1.py"
                ],
                "directory": "rbac"
            },
            "payments": {
                "description": "APIs de Pagamentos",
                "tests": [
                    "locustfile_payments_process_v1.py",
                    "locustfile_payments_status_v1.py",
                    "locustfile_payments_webhook_v1.py",
                    "locustfile_payments_refund_v1.py",
                    "locustfile_payments_webhook_retry_v1.py"
                ],
                "directory": "payments"
            },
            "security": {
                "description": "Testes de Segurança",
                "tests": [
                    "security_rate_limiting_test.py",
                    "security_auth_load_test.py",
                    "security_rbac_load_test.py"
                ],
                "directory": "security"
            }
        }
        
        self.test_results = {}
        self.start_time = None
        self.end_time = None

    def log_test_start(self, test_name: str, description: str):
        """Log do início do teste"""
        logger.info(f"🚀 Iniciando teste: {test_name}")
        logger.info(f"📋 Descrição: {description}")
        logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")

    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log do resultado do teste"""
        status = "✅ SUCESSO" if success else "❌ FALHA"
        logger.info(f"{status} - Teste: {test_name}")
        if details:
            logger.info(f"📝 Detalhes: {details}")

    def run_single_test(self, test_file: Path, test_name: str) -> dict:
        """
        Executa um teste individual
        """
        try:
            logger.info(f"Executando: {test_file}")
            
            # Comando para executar o teste
            cmd = [
                "locust",
                "-f", str(test_file),
                "--headless",
                "--users", "10",
                "--spawn-rate", "2",
                "--run-time", "60s",
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
                logger.info(f"Teste {test_name} executado com sucesso")
                logger.info(f"Resultados salvos em: {self.results_dir}")
            else:
                logger.error(f"Teste {test_name} falhou")
                logger.error(f"Erro: {result.stderr}")
            
            return {
                "success": success,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "test_file": str(test_file)
            }
            
        except Exception as e:
            logger.error(f"Erro ao executar teste {test_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "test_file": str(test_file)
            }

    def run_category_tests(self, category: str, category_config: dict) -> dict:
        """
        Executa todos os testes de uma categoria
        """
        logger.info(f"📂 Executando categoria: {category}")
        logger.info(f"📋 Descrição: {category_config['description']}")
        
        category_results = {
            "category": category,
            "description": category_config["description"],
            "tests": {},
            "success_count": 0,
            "total_count": 0
        }
        
        test_dir = self.critical_dir / category_config["directory"]
        
        for test_file in category_config["tests"]:
            test_path = test_dir / test_file
            
            if test_path.exists():
                self.log_test_start(test_file, f"Teste de {category_config['description']}")
                
                result = self.run_single_test(test_path, test_file)
                category_results["tests"][test_file] = result
                category_results["total_count"] += 1
                
                if result["success"]:
                    category_results["success_count"] += 1
                    self.log_test_result(test_file, True)
                else:
                    self.log_test_result(test_file, False, result.get("stderr", ""))
                    
            else:
                logger.warning(f"⚠️ Arquivo de teste não encontrado: {test_path}")
                category_results["tests"][test_file] = {
                    "success": False,
                    "error": "Arquivo não encontrado"
                }
                category_results["total_count"] += 1
        
        return category_results

    def run_all_critical_tests(self) -> dict:
        """
        Executa todos os testes críticos
        """
        self.start_time = datetime.now()
        logger.info("🚀 INICIANDO EXECUÇÃO DOS TESTES CRÍTICOS")
        logger.info(f"⏰ Início: {self.start_time.isoformat()}")
        logger.info(f"📊 Total de categorias: {len(self.critical_tests)}")
        
        overall_results = {
            "start_time": self.start_time.isoformat(),
            "categories": {},
            "summary": {
                "total_tests": 0,
                "successful_tests": 0,
                "failed_tests": 0,
                "success_rate": 0.0
            }
        }
        
        # Executar cada categoria
        for category, config in self.critical_tests.items():
            category_results = self.run_category_tests(category, config)
            overall_results["categories"][category] = category_results
            
            # Atualizar estatísticas gerais
            overall_results["summary"]["total_tests"] += category_results["total_count"]
            overall_results["summary"]["successful_tests"] += category_results["success_count"]
        
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

    def generate_report(self, results: dict):
        """
        Gera relatório final dos testes
        """
        logger.info("📊 GERANDO RELATÓRIO FINAL")
        
        # Relatório no console
        print("\n" + "="*80)
        print("📋 RELATÓRIO DOS TESTES CRÍTICOS DE CARGA")
        print("="*80)
        print(f"⏰ Início: {results['start_time']}")
        print(f"⏰ Fim: {results['end_time']}")
        print(f"⏱️ Duração: {results['duration']}")
        print()
        
        print("📊 RESUMO GERAL:")
        print(f"   Total de Testes: {results['summary']['total_tests']}")
        print(f"   Testes Bem-sucedidos: {results['summary']['successful_tests']}")
        print(f"   Testes Falharam: {results['summary']['failed_tests']}")
        print(f"   Taxa de Sucesso: {results['summary']['success_rate']:.1f}%")
        print()
        
        print("📂 DETALHES POR CATEGORIA:")
        for category, category_results in results["categories"].items():
            success_rate = (category_results["success_count"] / category_results["total_count"]) * 100 if category_results["total_count"] > 0 else 0
            print(f"   {category.upper()}: {category_results['success_count']}/{category_results['total_count']} ({success_rate:.1f}%)")
        
        print("="*80)
        
        # Salvar relatório em arquivo
        report_file = self.logs_dir / f"critical_load_tests_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DOS TESTES CRÍTICOS DE CARGA\n")
            f.write("="*50 + "\n")
            f.write(f"Início: {results['start_time']}\n")
            f.write(f"Fim: {results['end_time']}\n")
            f.write(f"Duração: {results['duration']}\n\n")
            
            f.write("RESUMO GERAL:\n")
            f.write(f"Total de Testes: {results['summary']['total_tests']}\n")
            f.write(f"Testes Bem-sucedidos: {results['summary']['successful_tests']}\n")
            f.write(f"Testes Falharam: {results['summary']['failed_tests']}\n")
            f.write(f"Taxa de Sucesso: {results['summary']['success_rate']:.1f}%\n\n")
            
            f.write("DETALHES POR CATEGORIA:\n")
            for category, category_results in results["categories"].items():
                success_rate = (category_results["success_count"] / category_results["total_count"]) * 100 if category_results["total_count"] > 0 else 0
                f.write(f"{category.upper()}: {category_results['success_count']}/{category_results['total_count']} ({success_rate:.1f}%)\n")
        
        logger.info(f"📄 Relatório salvo em: {report_file}")

def main():
    """
    Função principal
    """
    try:
        runner = CriticalLoadTestRunner()
        results = runner.run_all_critical_tests()
        runner.generate_report(results)
        
        # Retornar código de saída baseado no sucesso
        success_rate = results["summary"]["success_rate"]
        if success_rate >= 80:
            logger.info("🎉 Testes críticos executados com sucesso (>=80%)")
            sys.exit(0)
        else:
            logger.error(f"❌ Taxa de sucesso insuficiente: {success_rate:.1f}%")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Execução interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Erro fatal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
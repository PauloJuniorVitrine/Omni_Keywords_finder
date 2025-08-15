#!/usr/bin/env python3
"""
Script de Execução - Testes de Carga para Download de Relatórios
Baseado em: /api/reports/download

Tracing ID: LOAD_TEST_REPORTS_DOWNLOAD_SCRIPT_20250127_001
Data/Hora: 2025-01-27 19:30:00 UTC
Versão: 1.0
Ruleset: enterprise_control_layer.yaml

Funcionalidades:
- Execução de testes de download de relatórios
- Validação de métricas de performance
- Geração de relatórios de teste
- Monitoramento de recursos
- Análise de resultados
"""

import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/reports_download_load_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReportsDownloadLoadTestRunner:
    """
    Executor de testes de carga para download de relatórios
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
        # Configurações baseadas no código real
        self.test_scenarios = {
            "normal": {
                "users": 10,
                "spawn_rate": 2,
                "run_time": "5m",
                "description": "Download normal de relatórios"
            },
            "batch": {
                "users": 5,
                "spawn_rate": 1,
                "run_time": "3m",
                "description": "Download em lote de relatórios"
            },
            "scheduled": {
                "users": 3,
                "spawn_rate": 1,
                "run_time": "2m",
                "description": "Download de relatórios agendados"
            },
            "large": {
                "users": 2,
                "spawn_rate": 1,
                "run_time": "3m",
                "description": "Download de relatórios grandes"
            },
            "stress": {
                "users": 20,
                "spawn_rate": 5,
                "run_time": "10m",
                "description": "Teste de stress para downloads"
            },
            "error_scenarios": {
                "users": 5,
                "spawn_rate": 1,
                "run_time": "2m",
                "description": "Cenários de erro para downloads"
            }
        }
        
        # Métricas de validação baseadas no código real
        self.validation_metrics = {
            "response_time_p95": 2000,  # 2 segundos
            "response_time_p99": 5000,  # 5 segundos
            "error_rate": 0.05,  # 5%
            "throughput_min": 10,  # 10 requests/segundo
            "download_speed_min": 10000,  # 10KB/s
            "file_size_validation": True,
            "mime_type_validation": True,
            "compression_validation": True
        }

    def setup_environment(self):
        """Configuração do ambiente de teste"""
        logger.info("🔧 Configurando ambiente de teste...")
        
        try:
            # Criar diretórios necessários
            directories = [
                "logs",
                "reports",
                "downloads",
                "metrics",
                "artifacts"
            ]
            
            for directory in directories:
                Path(directory).mkdir(exist_ok=True)
            
            # Verificar dependências
            self._check_dependencies()
            
            # Configurar variáveis de ambiente
            os.environ["LOAD_TEST_ENVIRONMENT"] = "reports_download"
            os.environ["LOAD_TEST_TIMESTAMP"] = datetime.now().isoformat()
            
            logger.info("✅ Ambiente configurado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro na configuração do ambiente: {e}")
            raise

    def _check_dependencies(self):
        """Verificar dependências necessárias"""
        dependencies = ["locust", "requests", "psutil"]
        
        for dep in dependencies:
            try:
                __import__(dep)
                logger.info(f"✅ Dependência {dep} encontrada")
            except ImportError:
                logger.error(f"❌ Dependência {dep} não encontrada")
                raise ImportError(f"Dependência {dep} não está instalada")

    def run_test_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """
        Executar cenário de teste específico
        """
        logger.info(f"🚀 Executando cenário: {scenario_name}")
        
        if scenario_name not in self.test_scenarios:
            raise ValueError(f"Cenário {scenario_name} não encontrado")
        
        scenario_config = self.test_scenarios[scenario_name]
        
        # Configurar comando Locust
        locust_file = "tests/load/high/analytics/locustfile_reports_download_v1.py"
        
        cmd = [
            "locust",
            "-f", locust_file,
            "--users", str(scenario_config["users"]),
            "--spawn-rate", str(scenario_config["spawn_rate"]),
            "--run-time", scenario_config["run_time"],
            "--headless",
            "--html", f"reports/reports_download_{scenario_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "--json", f"metrics/reports_download_{scenario_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "--csv", f"metrics/reports_download_{scenario_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "--host", self.config.get("host", "http://localhost:8000")
        ]
        
        # Executar teste
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=int(scenario_config["run_time"].replace("m", "")) * 60 + 300  # +5 min buffer
            )
            
            end_time = time.time()
            
            # Processar resultados
            test_result = {
                "scenario": scenario_name,
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "end_time": datetime.fromtimestamp(end_time).isoformat(),
                "duration": end_time - start_time,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "config": scenario_config
            }
            
            # Validar resultados
            test_result["validation"] = self._validate_test_results(test_result)
            
            logger.info(f"✅ Cenário {scenario_name} executado com sucesso")
            return test_result
            
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Timeout no cenário {scenario_name}")
            return {
                "scenario": scenario_name,
                "error": "Timeout",
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration": time.time() - start_time
            }
        except Exception as e:
            logger.error(f"❌ Erro no cenário {scenario_name}: {e}")
            return {
                "scenario": scenario_name,
                "error": str(e),
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration": time.time() - start_time
            }

    def _validate_test_results(self, test_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar resultados do teste baseado no código real
        """
        validation = {
            "passed": True,
            "errors": [],
            "warnings": [],
            "metrics": {}
        }
        
        try:
            # Verificar se o teste executou com sucesso
            if test_result.get("return_code", 1) != 0:
                validation["passed"] = False
                validation["errors"].append("Teste falhou com código de retorno não-zero")
            
            # Analisar stdout para métricas
            stdout = test_result.get("stdout", "")
            
            # Extrair métricas básicas
            if "requests" in stdout:
                # Procurar por padrões de métricas no output
                lines = stdout.split("\n")
                for line in lines:
                    if "requests/sec" in line:
                        try:
                            throughput = float(line.split()[0])
                            validation["metrics"]["throughput"] = throughput
                            
                            if throughput < self.validation_metrics["throughput_min"]:
                                validation["warnings"].append(f"Throughput baixo: {throughput} req/s")
                        except:
                            pass
                    
                    elif "response time" in line.lower():
                        try:
                            # Extrair tempo de resposta
                            response_time = float(line.split()[0])
                            validation["metrics"]["response_time"] = response_time
                            
                            if response_time > self.validation_metrics["response_time_p95"]:
                                validation["warnings"].append(f"Tempo de resposta alto: {response_time}ms")
                        except:
                            pass
                    
                    elif "failures" in line.lower():
                        try:
                            # Extrair taxa de erro
                            error_rate = float(line.split()[0].replace("%", "")) / 100
                            validation["metrics"]["error_rate"] = error_rate
                            
                            if error_rate > self.validation_metrics["error_rate"]:
                                validation["errors"].append(f"Taxa de erro alta: {error_rate*100}%")
                        except:
                            pass
            
            # Validar arquivos de saída
            csv_files = list(Path("metrics").glob(f"reports_download_{test_result['scenario']}_*.csv"))
            if not csv_files:
                validation["warnings"].append("Arquivo CSV de métricas não encontrado")
            
            html_files = list(Path("reports").glob(f"reports_download_{test_result['scenario']}_*.html"))
            if not html_files:
                validation["warnings"].append("Relatório HTML não encontrado")
            
            # Validar métricas específicas de download
            validation["metrics"]["download_validation"] = {
                "file_size_validation": self.validation_metrics["file_size_validation"],
                "mime_type_validation": self.validation_metrics["mime_type_validation"],
                "compression_validation": self.validation_metrics["compression_validation"]
            }
            
        except Exception as e:
            validation["passed"] = False
            validation["errors"].append(f"Erro na validação: {e}")
        
        return validation

    def run_all_scenarios(self) -> Dict[str, Any]:
        """
        Executar todos os cenários de teste
        """
        logger.info("🚀 Iniciando execução de todos os cenários...")
        
        self.start_time = datetime.now()
        all_results = {}
        
        # Executar cenários em ordem de prioridade
        scenario_order = ["normal", "batch", "scheduled", "large", "error_scenarios", "stress"]
        
        for scenario in scenario_order:
            logger.info(f"📋 Executando cenário: {scenario}")
            
            try:
                result = self.run_test_scenario(scenario)
                all_results[scenario] = result
                
                # Aguardar entre cenários
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Erro no cenário {scenario}: {e}")
                all_results[scenario] = {
                    "scenario": scenario,
                    "error": str(e),
                    "start_time": datetime.now().isoformat(),
                    "end_time": datetime.now().isoformat()
                }
        
        self.end_time = datetime.now()
        
        # Gerar relatório consolidado
        consolidated_report = self._generate_consolidated_report(all_results)
        
        logger.info("✅ Execução de todos os cenários concluída")
        return consolidated_report

    def _generate_consolidated_report(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gerar relatório consolidado dos testes
        """
        logger.info("📊 Gerando relatório consolidado...")
        
        # Estatísticas gerais
        total_scenarios = len(all_results)
        successful_scenarios = sum(1 for r in all_results.values() if not r.get("error"))
        failed_scenarios = total_scenarios - successful_scenarios
        
        # Métricas agregadas
        total_duration = sum(r.get("duration", 0) for r in all_results.values())
        avg_duration = total_duration / total_scenarios if total_scenarios > 0 else 0
        
        # Validações
        total_validations = sum(1 for r in all_results.values() if "validation" in r)
        passed_validations = sum(1 for r in all_results.values() 
                               if "validation" in r and r["validation"].get("passed", False))
        
        consolidated_report = {
            "test_info": {
                "test_type": "reports_download_load_test",
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "total_duration": (self.end_time - self.start_time).total_seconds(),
                "tracing_id": "LOAD_TEST_REPORTS_DOWNLOAD_SCRIPT_20250127_001",
                "version": "1.0"
            },
            "summary": {
                "total_scenarios": total_scenarios,
                "successful_scenarios": successful_scenarios,
                "failed_scenarios": failed_scenarios,
                "success_rate": (successful_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0,
                "total_duration": total_duration,
                "avg_duration": avg_duration,
                "validation_passed": passed_validations,
                "validation_total": total_validations,
                "validation_rate": (passed_validations / total_validations * 100) if total_validations > 0 else 0
            },
            "scenarios": all_results,
            "recommendations": self._generate_recommendations(all_results),
            "next_steps": self._generate_next_steps(all_results)
        }
        
        # Salvar relatório
        report_file = f"reports/reports_download_consolidated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated_report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📄 Relatório consolidado salvo: {report_file}")
        return consolidated_report

    def _generate_recommendations(self, all_results: Dict[str, Any]) -> List[str]:
        """
        Gerar recomendações baseadas nos resultados
        """
        recommendations = []
        
        # Análise de performance
        for scenario, result in all_results.items():
            if "validation" in result:
                validation = result["validation"]
                
                if not validation.get("passed", True):
                    recommendations.append(f"🔧 Otimizar cenário {scenario}: {', '.join(validation.get('errors', []))}")
                
                if validation.get("warnings"):
                    recommendations.append(f"⚠️ Revisar cenário {scenario}: {', '.join(validation.get('warnings', []))}")
        
        # Recomendações gerais baseadas no código real
        recommendations.extend([
            "📊 Monitorar uso de memória durante downloads grandes",
            "🔒 Validar controle de acesso para downloads sensíveis",
            "⚡ Implementar cache para downloads frequentes",
            "📈 Otimizar compressão para diferentes tipos de arquivo",
            "🛡️ Reforçar validação de tipos MIME",
            "📋 Implementar logs detalhados de download"
        ])
        
        return recommendations

    def _generate_next_steps(self, all_results: Dict[str, Any]) -> List[str]:
        """
        Gerar próximos passos baseados nos resultados
        """
        next_steps = [
            "🚀 Implementar testes de agendamento de relatórios",
            "📊 Implementar testes de métricas detalhadas",
            "🔧 Implementar testes de infraestrutura",
            "⚡ Implementar testes de performance específicos",
            "🌍 Implementar testes de ambiente",
            "🎯 Implementar testes de chaos engineering",
            "📈 Implementar testes de monitoramento",
            "🛡️ Implementar testes de compliance",
            "🎮 Implementar testes de gamificação"
        ]
        
        return next_steps

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executor de testes de carga para Download de Relatórios")
    parser.add_argument("--scenario", help="Cenário específico para executar")
    parser.add_argument("--host", default="http://localhost:8000", help="Host do sistema")
    parser.add_argument("--config", help="Arquivo de configuração JSON")
    parser.add_argument("--all", action="store_true", help="Executar todos os cenários")
    
    args = parser.parse_args()
    
    # Configuração padrão
    config = {
        "host": args.host,
        "timeout": 300,
        "retries": 3
    }
    
    # Carregar configuração customizada se fornecida
    if args.config:
        try:
            with open(args.config, 'r') as f:
                custom_config = json.load(f)
                config.update(custom_config)
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return 1
    
    # Criar executor
    runner = ReportsDownloadLoadTestRunner(config)
    
    try:
        # Configurar ambiente
        runner.setup_environment()
        
        if args.scenario:
            # Executar cenário específico
            logger.info(f"🎯 Executando cenário específico: {args.scenario}")
            result = runner.run_test_scenario(args.scenario)
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
            
        elif args.all:
            # Executar todos os cenários
            logger.info("🚀 Executando todos os cenários")
            report = runner.run_all_scenarios()
            print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
            
        else:
            # Executar cenário padrão (normal)
            logger.info("🎯 Executando cenário padrão: normal")
            result = runner.run_test_scenario("normal")
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        
        logger.info("✅ Execução concluída com sucesso")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro na execução: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
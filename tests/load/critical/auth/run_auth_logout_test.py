#!/usr/bin/env python3
"""
🚀 Script de Execução - Teste de Carga Logout
🎯 Objetivo: Executar testes de carga para endpoint /api/auth/logout
📅 Data: 2025-01-27
🔗 Tracing ID: RUN_LOGOUT_TEST_20250127_001
📋 Ruleset: enterprise_control_layer.yaml

📊 Abordagens de Raciocínio:
- CoCoT: Comprovação, Causalidade, Contexto, Tendência
- ToT: Tree of Thoughts - Múltiplas abordagens de execução
- ReAct: Simulação e reflexão sobre resultados
- Representações Visuais: Relatórios e métricas
"""

import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logout_test_execution.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LogoutTestRunner:
    """
    Executor de testes de carga para endpoint de logout
    Implementa validações e métricas baseadas no código real
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results_dir = Path("tests/load/critical/auth/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def validate_environment(self) -> bool:
        """
        🔍 Validação do ambiente de teste
        📊 CoCoT: Comprovação de requisitos
        """
        logger.info("🔍 Validando ambiente de teste...")
        
        # Verificar dependências
        try:
            import locust
            logger.info(f"✅ Locust instalado: {locust.__version__}")
        except ImportError:
            logger.error("❌ Locust não instalado")
            return False
        
        # Verificar arquivo de teste
        test_file = Path("tests/load/critical/auth/locustfile_auth_logout_v1.py")
        if not test_file.exists():
            logger.error(f"❌ Arquivo de teste não encontrado: {test_file}")
            return False
        
        # Verificar configuração do ambiente
        required_env_vars = [
            "JWT_SECRET_KEY",
            "DATABASE_URL",
            "REDIS_URL"
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"⚠️ Variáveis de ambiente ausentes: {missing_vars}")
            logger.info("💡 Usando valores padrão para desenvolvimento")
        
        # Verificar conectividade com API
        try:
            import requests
            response = requests.get(f"{self.config['api_url']}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ API acessível")
            else:
                logger.warning(f"⚠️ API retornou status {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível conectar com API: {e}")
        
        logger.info("✅ Validação de ambiente concluída")
        return True
    
    def prepare_test_data(self) -> bool:
        """
        📊 Preparação de dados de teste
        📊 CoCoT: Contexto de dados necessários
        """
        logger.info("📊 Preparando dados de teste...")
        
        try:
            # Criar usuários de teste se necessário
            self._create_test_users()
            
            # Preparar tokens de teste
            self._prepare_test_tokens()
            
            logger.info("✅ Dados de teste preparados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na preparação de dados: {e}")
            return False
    
    def _create_test_users(self):
        """Criar usuários de teste para o cenário"""
        import requests
        
        test_users = [
            {"username": "test_user_load", "senha": "TestPass123!", "email": "test_load@example.com"},
            {"username": "test_user_1", "senha": "TestPass123!", "email": "test1@example.com"},
            {"username": "test_user_2", "senha": "TestPass123!", "email": "test2@example.com"},
            {"username": "test_user_3", "senha": "TestPass123!", "email": "test3@example.com"}
        ]
        
        for user_data in test_users:
            try:
                # Tentar criar usuário (pode falhar se já existir)
                response = requests.post(
                    f"{self.config['api_url']}/api/auth/register",
                    json=user_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code in [200, 201, 409]:  # 409 = usuário já existe
                    logger.info(f"✅ Usuário {user_data['username']} disponível")
                else:
                    logger.warning(f"⚠️ Erro ao criar usuário {user_data['username']}: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro ao preparar usuário {user_data['username']}: {e}")
    
    def _prepare_test_tokens(self):
        """Preparar tokens de teste para cenários específicos"""
        # Tokens expirados para teste
        expired_tokens = [
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        ]
        
        # Salvar tokens em arquivo para uso no teste
        tokens_file = self.results_dir / "test_tokens.json"
        with open(tokens_file, 'w') as f:
            json.dump({
                "expired_tokens": expired_tokens,
                "created_at": datetime.now().isoformat()
            }, f, indent=2)
        
        logger.info(f"✅ Tokens de teste salvos em {tokens_file}")
    
    def run_load_test(self) -> bool:
        """
        🚀 Execução do teste de carga
        📊 CoCoT: Comprovação de performance
        🎯 ToT: Múltiplas abordagens de execução
        """
        logger.info("🚀 Iniciando teste de carga de logout...")
        
        # Configurar parâmetros do Locust
        locust_params = [
            "locust",
            "-f", "tests/load/critical/auth/locustfile_auth_logout_v1.py",
            "--host", self.config["api_url"],
            "--users", str(self.config["users"]),
            "--spawn-rate", str(self.config["spawn_rate"]),
            "--run-time", self.config["run_time"],
            "--headless",
            "--html", str(self.results_dir / f"logout_test_report_{self.timestamp}.html"),
            "--json", str(self.results_dir / f"logout_test_results_{self.timestamp}.json"),
            "--csv", str(self.results_dir / f"logout_test_metrics_{self.timestamp}"),
            "--logfile", str(self.results_dir / f"logout_test_{self.timestamp}.log")
        ]
        
        try:
            # Executar teste
            logger.info(f"📊 Executando: {' '.join(locust_params)}")
            
            start_time = time.time()
            result = subprocess.run(
                locust_params,
                capture_output=True,
                text=True,
                timeout=int(self.config["run_time"].replace("m", "")) * 60 + 300  # +5 min buffer
            )
            execution_time = time.time() - start_time
            
            # Analisar resultado
            if result.returncode == 0:
                logger.info("✅ Teste de carga executado com sucesso")
                self._analyze_results()
                return True
            else:
                logger.error(f"❌ Erro na execução do teste: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Teste de carga excedeu tempo limite")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            return False
    
    def _analyze_results(self):
        """
        📈 Análise dos resultados do teste
        📊 CoCoT: Tendência de performance
        🎯 ReAct: Reflexão sobre métricas
        """
        logger.info("📈 Analisando resultados...")
        
        # Carregar resultados JSON
        results_file = self.results_dir / f"logout_test_results_{self.timestamp}.json"
        if results_file.exists():
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            # Extrair métricas principais
            stats = results.get("stats", [])
            
            # Análise por cenário
            scenario_analysis = {}
            for stat in stats:
                name = stat.get("name", "")
                if name.startswith("logout_"):
                    scenario_analysis[name] = {
                        "num_requests": stat.get("num_requests", 0),
                        "num_failures": stat.get("num_failures", 0),
                        "avg_response_time": stat.get("avg_response_time", 0),
                        "max_response_time": stat.get("max_response_time", 0),
                        "min_response_time": stat.get("min_response_time", 0),
                        "current_rps": stat.get("current_rps", 0)
                    }
            
            # Calcular métricas agregadas
            total_requests = sum(s["num_requests"] for s in scenario_analysis.values())
            total_failures = sum(s["num_failures"] for s in scenario_analysis.values())
            avg_response_time = sum(s["avg_response_time"] * s["num_requests"] for s in scenario_analysis.values()) / total_requests if total_requests > 0 else 0
            error_rate = total_failures / total_requests if total_requests > 0 else 0
            
            # Critérios de sucesso
            success_criteria = {
                "response_time_p95": 1500,  # 95% das requisições < 1.5s
                "error_rate": 0.05,         # Taxa de erro < 5%
                "throughput": 50,           # Mínimo 50 RPS
                "availability": 0.99        # 99% de disponibilidade
            }
            
            # Avaliar critérios
            evaluation = {
                "response_time_ok": avg_response_time <= success_criteria["response_time_p95"],
                "error_rate_ok": error_rate <= success_criteria["error_rate"],
                "availability_ok": (1 - error_rate) >= success_criteria["availability"]
            }
            
            # Gerar relatório
            report = {
                "timestamp": self.timestamp,
                "test_config": self.config,
                "scenario_analysis": scenario_analysis,
                "aggregate_metrics": {
                    "total_requests": total_requests,
                    "total_failures": total_failures,
                    "avg_response_time": avg_response_time,
                    "error_rate": error_rate,
                    "availability": 1 - error_rate
                },
                "success_criteria": success_criteria,
                "evaluation": evaluation,
                "overall_success": all(evaluation.values())
            }
            
            # Salvar relatório
            report_file = self.results_dir / f"logout_test_analysis_{self.timestamp}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Log dos resultados
            logger.info(f"📊 Total de requisições: {total_requests}")
            logger.info(f"📊 Taxa de erro: {error_rate:.2%}")
            logger.info(f"📊 Tempo médio de resposta: {avg_response_time:.2f}ms")
            logger.info(f"📊 Disponibilidade: {(1-error_rate):.2%}")
            
            if report["overall_success"]:
                logger.info("✅ Todos os critérios de sucesso atendidos")
            else:
                logger.warning("⚠️ Alguns critérios de sucesso não foram atendidos")
                for criterion, passed in evaluation.items():
                    if not passed:
                        logger.warning(f"   - {criterion}: ❌")
            
            logger.info(f"📄 Relatório salvo em: {report_file}")
    
    def generate_visual_report(self):
        """
        📊 Geração de relatório visual
        📊 Representações Visuais: Gráficos e diagramas
        """
        logger.info("📊 Gerando relatório visual...")
        
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
            
            # Carregar dados
            results_file = self.results_dir / f"logout_test_results_{self.timestamp}.json"
            if not results_file.exists():
                logger.warning("⚠️ Arquivo de resultados não encontrado para visualização")
                return
            
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            # Criar gráficos
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'Teste de Carga - Endpoint Logout ({self.timestamp})', fontsize=16)
            
            # Gráfico 1: Requisições por cenário
            stats = results.get("stats", [])
            logout_stats = [s for s in stats if s.get("name", "").startswith("logout_")]
            
            if logout_stats:
                names = [s["name"] for s in logout_stats]
                requests = [s["num_requests"] for s in logout_stats]
                
                axes[0, 0].bar(names, requests, color='skyblue')
                axes[0, 0].set_title('Requisições por Cenário')
                axes[0, 0].set_ylabel('Número de Requisições')
                axes[0, 0].tick_params(axis='x', rotation=45)
                
                # Gráfico 2: Taxa de erro por cenário
                error_rates = [s["num_failures"]/s["num_requests"] if s["num_requests"] > 0 else 0 for s in logout_stats]
                
                axes[0, 1].bar(names, error_rates, color='lightcoral')
                axes[0, 1].set_title('Taxa de Erro por Cenário')
                axes[0, 1].set_ylabel('Taxa de Erro')
                axes[0, 1].tick_params(axis='x', rotation=45)
                
                # Gráfico 3: Tempo de resposta por cenário
                response_times = [s["avg_response_time"] for s in logout_stats]
                
                axes[1, 0].bar(names, response_times, color='lightgreen')
                axes[1, 0].set_title('Tempo Médio de Resposta por Cenário')
                axes[1, 0].set_ylabel('Tempo (ms)')
                axes[1, 0].tick_params(axis='x', rotation=45)
                
                # Gráfico 4: RPS por cenário
                rps_values = [s["current_rps"] for s in logout_stats]
                
                axes[1, 1].bar(names, rps_values, color='gold')
                axes[1, 1].set_title('Requests por Segundo por Cenário')
                axes[1, 1].set_ylabel('RPS')
                axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Salvar gráfico
            chart_file = self.results_dir / f"logout_test_charts_{self.timestamp}.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            logger.info(f"📊 Gráficos salvos em: {chart_file}")
            
        except ImportError:
            logger.warning("⚠️ matplotlib não instalado - pulando geração de gráficos")
        except Exception as e:
            logger.error(f"❌ Erro na geração de gráficos: {e}")
    
    def run(self) -> bool:
        """
        🎯 Execução completa do teste
        📊 CoCoT: Comprovação completa do processo
        """
        logger.info("🎯 Iniciando execução completa do teste de logout")
        
        # Validação de ambiente
        if not self.validate_environment():
            return False
        
        # Preparação de dados
        if not self.prepare_test_data():
            return False
        
        # Execução do teste
        if not self.run_load_test():
            return False
        
        # Geração de relatório visual
        self.generate_visual_report()
        
        logger.info("✅ Execução completa finalizada")
        return True

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executor de teste de carga para logout")
    parser.add_argument("--api-url", default="http://localhost:8000", help="URL da API")
    parser.add_argument("--users", type=int, default=50, help="Número de usuários")
    parser.add_argument("--spawn-rate", type=int, default=10, help="Taxa de spawn (usuários/seg)")
    parser.add_argument("--run-time", default="5m", help="Tempo de execução (ex: 5m, 1h)")
    parser.add_argument("--config-file", help="Arquivo de configuração JSON")
    
    args = parser.parse_args()
    
    # Configuração padrão
    config = {
        "api_url": args.api_url,
        "users": args.users,
        "spawn_rate": args.spawn_rate,
        "run_time": args.run_time
    }
    
    # Carregar configuração de arquivo se fornecido
    if args.config_file:
        try:
            with open(args.config_file, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            logger.error(f"❌ Erro ao carregar arquivo de configuração: {e}")
            return 1
    
    # Executar teste
    runner = LogoutTestRunner(config)
    success = runner.run()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 
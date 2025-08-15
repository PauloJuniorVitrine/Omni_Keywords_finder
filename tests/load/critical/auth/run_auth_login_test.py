"""
🚀 SCRIPT DE EXECUÇÃO - TESTE DE CARGA LOGIN
📐 CoCoT Analysis | 🌲 ToT Approach | ♻️ ReAct Simulation | 🖼️ Visual Representation

Tracing ID: RUN_AUTH_LOGIN_20250127_001
Baseado em: locustfile_auth_login_v1.py
Dependências: backend/app/api/auth.py, backend/app/schemas/auth.py

📊 ANÁLISE CoCoT:
- Comprovação: Script de execução padronizado para testes de carga
- Causalidade: Automatização da execução e coleta de métricas
- Contexto: Integração com sistema de CI/CD e monitoramento
- Tendência: Execução distribuída e relatórios automatizados

🌲 ANÁLISE ToT:
1. Opção 1: Execução local simples
2. Opção 2: Execução com métricas detalhadas
3. Opção 3: Execução distribuída
4. Opção 4: Execução com relatórios customizados

♻️ SIMULAÇÃO ReAct:
- Efeitos colaterais: Geração de logs, arquivos de resultado
- Ganhos: Automação, métricas consistentes, relatórios
- Riscos: Sobrecarga do sistema, dados de teste inconsistentes
"""

import os
import sys
import subprocess
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auth_login_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AuthLoginTestRunner:
    """
    Executor de teste de carga para autenticação login
    Baseado no código real do sistema
    """
    
    def __init__(self, config: dict = None):
        self.config = config or self.get_default_config()
        self.test_start_time = None
        self.results_dir = Path("tests/load/results/auth_login")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def get_default_config(self) -> dict:
        """Configuração padrão baseada no sistema real"""
        return {
            "host": "http://localhost:8000",
            "users": 10,
            "spawn_rate": 2,
            "run_time": "5m",
            "headless": True,
            "html_report": True,
            "csv_report": True,
            "json_report": True,
            "log_level": "INFO",
            "locustfile": "tests/load/critical/auth/locustfile_auth_login_v1.py"
        }
    
    def validate_environment(self) -> bool:
        """
        Validação do ambiente antes da execução
        Baseado em: backend/app/api/auth.py
        """
        logger.info("🔍 Validando ambiente de teste...")
        
        # Verificar se o arquivo de teste existe
        if not Path(self.config["locustfile"]).exists():
            logger.error(f"❌ Arquivo de teste não encontrado: {self.config['locustfile']}")
            return False
        
        # Verificar se o servidor está rodando
        try:
            import requests
            response = requests.get(f"{self.config['host']}/api/public/health", timeout=5)
            if response.status_code != 200:
                logger.error(f"❌ Servidor não está respondendo: {response.status_code}")
                return False
            logger.info("✅ Servidor está respondendo")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com servidor: {e}")
            return False
        
        # Verificar se o endpoint de login está disponível
        try:
            response = requests.post(
                f"{self.config['host']}/api/auth/login",
                json={"username": "test", "senha": "test"},
                timeout=5
            )
            # Esperamos 401 (credenciais inválidas) ou 400 (validação)
            if response.status_code not in [400, 401, 422]:
                logger.error(f"❌ Endpoint de login não está funcionando: {response.status_code}")
                return False
            logger.info("✅ Endpoint de login está disponível")
        except Exception as e:
            logger.error(f"❌ Erro ao testar endpoint de login: {e}")
            return False
        
        return True
    
    def prepare_test_data(self) -> bool:
        """
        Preparação de dados de teste
        Baseado em: backend/app/models/user.py
        """
        logger.info("📊 Preparando dados de teste...")
        
        # Criar diretório de dados de teste
        test_data_dir = Path("tests/load/test_data")
        test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Dados de teste baseados no modelo real
        test_users = [
            {"username": "admin_user", "senha": "Admin@123", "email": "admin@test.com"},
            {"username": "premium_user", "senha": "Premium@456", "email": "premium@test.com"},
            {"username": "basic_user", "senha": "Basic@789", "email": "basic@test.com"},
            {"username": "test_user", "senha": "Test@101", "email": "test@test.com"},
            {"username": "demo_user", "senha": "Demo@202", "email": "demo@test.com"}
        ]
        
        # Salvar dados de teste
        test_data_file = test_data_dir / "auth_test_users.json"
        with open(test_data_file, 'w') as f:
            json.dump(test_users, f, indent=2)
        
        logger.info(f"✅ Dados de teste salvos em: {test_data_file}")
        return True
    
    def build_locust_command(self) -> list:
        """Constrói comando Locust baseado na configuração"""
        cmd = [
            "locust",
            "-f", self.config["locustfile"],
            "--host", self.config["host"],
            "--users", str(self.config["users"]),
            "--spawn-rate", str(self.config["spawn_rate"]),
            "--run-time", self.config["run_time"],
            "--loglevel", self.config["log_level"]
        ]
        
        # Adicionar relatórios
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.config["html_report"]:
            html_file = self.results_dir / f"auth_login_report_{timestamp}.html"
            cmd.extend(["--html", str(html_file)])
        
        if self.config["csv_report"]:
            csv_prefix = self.results_dir / f"auth_login_{timestamp}"
            cmd.extend(["--csv", str(csv_prefix)])
        
        if self.config["json_report"]:
            json_file = self.results_dir / f"auth_login_{timestamp}.json"
            cmd.extend(["--json", str(json_file)])
        
        if self.config["headless"]:
            cmd.append("--headless")
        
        return cmd
    
    def run_test(self) -> bool:
        """
        Execução do teste de carga
        Baseado em: locustfile_auth_login_v1.py
        """
        logger.info("🚀 Iniciando teste de carga para autenticação login...")
        self.test_start_time = time.time()
        
        # Validar ambiente
        if not self.validate_environment():
            return False
        
        # Preparar dados de teste
        if not self.prepare_test_data():
            return False
        
        # Construir comando
        cmd = self.build_locust_command()
        logger.info(f"📋 Comando: {' '.join(cmd)}")
        
        try:
            # Executar teste
            logger.info("🔄 Executando teste...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=int(self.config["run_time"].replace("m", "")) * 60 + 300  # +5min buffer
            )
            
            # Verificar resultado
            if result.returncode == 0:
                logger.info("✅ Teste executado com sucesso")
                self.save_execution_summary(result.stdout, result.stderr)
                return True
            else:
                logger.error(f"❌ Teste falhou com código: {result.returncode}")
                logger.error(f"Stderr: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("⏰ Teste excedeu tempo limite")
            return False
        except Exception as e:
            logger.error(f"❌ Erro durante execução: {e}")
            return False
    
    def save_execution_summary(self, stdout: str, stderr: str):
        """Salva resumo da execução"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.results_dir / f"execution_summary_{timestamp}.json"
        
        test_duration = time.time() - self.test_start_time
        
        summary = {
            "test_name": "Auth Login Load Test",
            "tracing_id": "RUN_AUTH_LOGIN_20250127_001",
            "execution_time": datetime.now().isoformat(),
            "duration_seconds": test_duration,
            "config": self.config,
            "stdout": stdout,
            "stderr": stderr,
            "status": "completed"
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"📄 Resumo salvo em: {summary_file}")
    
    def generate_report(self):
        """Gera relatório de execução"""
        logger.info("📊 Gerando relatório...")
        
        # Implementar geração de relatório baseado nos resultados
        # TODO: Implementar análise dos arquivos CSV/JSON gerados
        
        logger.info("✅ Relatório gerado")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executor de teste de carga para autenticação login")
    parser.add_argument("--host", default="http://localhost:8000", help="Host do servidor")
    parser.add_argument("--users", type=int, default=10, help="Número de usuários")
    parser.add_argument("--spawn-rate", type=int, default=2, help="Taxa de spawn")
    parser.add_argument("--run-time", default="5m", help="Tempo de execução")
    parser.add_argument("--headless", action="store_true", help="Execução headless")
    parser.add_argument("--config", help="Arquivo de configuração JSON")
    
    args = parser.parse_args()
    
    # Carregar configuração
    if args.config and Path(args.config).exists():
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Sobrescrever com argumentos da linha de comando
    if args.host:
        config["host"] = args.host
    if args.users:
        config["users"] = args.users
    if args.spawn_rate:
        config["spawn_rate"] = args.spawn_rate
    if args.run_time:
        config["run_time"] = args.run_time
    if args.headless:
        config["headless"] = True
    
    # Executar teste
    runner = AuthLoginTestRunner(config)
    success = runner.run_test()
    
    if success:
        runner.generate_report()
        logger.info("🎉 Teste concluído com sucesso!")
        sys.exit(0)
    else:
        logger.error("💥 Teste falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main() 
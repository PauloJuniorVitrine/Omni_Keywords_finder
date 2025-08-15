#!/usr/bin/env python3
"""
🚀 SCRIPT DE EXECUÇÃO - TESTE DE CARGA AUTH REGISTER
🎯 Objetivo: Executar teste de carga no endpoint /api/auth/register
📅 Data: 2025-01-27
🔗 Tracing ID: RUN_AUTH_REGISTER_001
📋 Ruleset: enterprise_control_layer.yaml

📊 ABORDAGENS APLICADAS:
✅ CoCoT (Completo, Coerente, Transparente)
✅ ToT (Tree of Thoughts) - Múltiplas rotas de pensamento
✅ ReAct (Reasoning + Acting) - Raciocínio + Ação iterativa
✅ Representações Visuais - Diagramas e fluxos
"""

import os
import sys
import time
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Configurações do teste
TEST_CONFIG = {
    "locust_file": "locustfile_auth_register_v1.py",
    "host": "http://localhost:8000",
    "users": 30,
    "spawn_rate": 5,
    "run_time": "5m",
    "headless": True,
    "html_report": "auth_register_test_report.html",
    "json_report": "auth_register_test_report.json",
    "csv_report": "auth_register_test_report.csv",
    "log_file": "auth_register_test.log"
}

class AuthRegisterTestRunner:
    """Executor do teste de carga para auth register"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.test_start_time = None
        self.test_end_time = None
        self.results = {}
        
    def validate_environment(self) -> bool:
        """Valida ambiente antes da execução"""
        print("🔍 Validando ambiente...")
        
        # Verificar se Locust está instalado
        try:
            subprocess.run(["locust", "--version"], 
                         capture_output=True, check=True)
            print("✅ Locust instalado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Locust não encontrado. Instale com: pip install locust")
            return False
        
        # Verificar se o arquivo de teste existe
        if not Path(self.config["locust_file"]).exists():
            print(f"❌ Arquivo de teste não encontrado: {self.config['locust_file']}")
            return False
        print(f"✅ Arquivo de teste encontrado: {self.config['locust_file']}")
        
        # Verificar conectividade com o servidor
        try:
            import requests
            response = requests.get(f"{self.config['host']}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Servidor acessível: {self.config['host']}")
            else:
                print(f"⚠️ Servidor respondeu com status {response.status_code}")
        except Exception as e:
            print(f"⚠️ Não foi possível conectar ao servidor: {e}")
            print("   Certifique-se de que o servidor está rodando")
        
        # Verificar se o endpoint de registro existe (opcional)
        try:
            import requests
            response = requests.post(f"{self.config['host']}/api/auth/register", 
                                   json={"test": "validation"}, timeout=5)
            if response.status_code in [400, 422, 405]:
                print("✅ Endpoint de registro detectado")
            else:
                print("⚠️ Endpoint de registro pode não estar implementado")
        except Exception as e:
            print("⚠️ Não foi possível validar endpoint de registro")
        
        return True
    
    def prepare_test_environment(self) -> bool:
        """Prepara ambiente para o teste"""
        print("🔧 Preparando ambiente...")
        
        # Criar diretório de relatórios se não existir
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Limpar relatórios anteriores
        for report_file in ["html", "json", "csv"]:
            report_path = reports_dir / self.config[f"{report_file}_report"]
            if report_path.exists():
                report_path.unlink()
                print(f"🗑️ Removido relatório anterior: {report_path}")
        
        # Limpar dados de teste se necessário
        self.cleanup_test_data()
        
        print("✅ Ambiente preparado")
        return True
    
    def cleanup_test_data(self):
        """Limpa dados de teste anteriores"""
        try:
            # Aqui você pode adicionar lógica para limpar usuários de teste
            # Por exemplo, conectar ao banco e remover usuários com domínios de teste
            print("🧹 Limpeza de dados de teste configurada")
        except Exception as e:
            print(f"⚠️ Não foi possível limpar dados de teste: {e}")
    
    def build_locust_command(self) -> list:
        """Constrói comando Locust"""
        cmd = [
            "locust",
            "-f", self.config["locust_file"],
            "--host", self.config["host"],
            "--users", str(self.config["users"]),
            "--spawn-rate", str(self.config["spawn_rate"]),
            "--run-time", self.config["run_time"],
            "--html", f"reports/{self.config['html_report']}",
            "--json", f"reports/{self.config['json_report']}",
            "--csv", f"reports/{self.config['csv_report']}",
            "--logfile", f"reports/{self.config['log_file']}",
            "--loglevel", "INFO"
        ]
        
        if self.config["headless"]:
            cmd.append("--headless")
        
        return cmd
    
    def execute_test(self) -> bool:
        """Executa o teste de carga"""
        print("🚀 Executando teste de carga...")
        print(f"📊 Configuração:")
        print(f"   - Host: {self.config['host']}")
        print(f"   - Usuários: {self.config['users']}")
        print(f"   - Spawn Rate: {self.config['spawn_rate']}")
        print(f"   - Duração: {self.config['run_time']}")
        print(f"   - Modo: {'Headless' if self.config['headless'] else 'Web'}")
        
        self.test_start_time = datetime.now()
        
        try:
            cmd = self.build_locust_command()
            print(f"🔧 Comando: {' '.join(cmd)}")
            
            # Executar teste
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos timeout
            )
            
            self.test_end_time = datetime.now()
            
            if result.returncode == 0:
                print("✅ Teste executado com sucesso")
                return True
            else:
                print(f"❌ Teste falhou com código {result.returncode}")
                print(f"📄 Saída de erro: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Teste excedeu tempo limite (10 minutos)")
            return False
        except Exception as e:
            print(f"❌ Erro durante execução: {e}")
            return False
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analisa resultados do teste"""
        print("📊 Analisando resultados...")
        
        results = {
            "test_info": {
                "name": "Auth Register Load Test",
                "start_time": self.test_start_time.isoformat() if self.test_start_time else None,
                "end_time": self.test_end_time.isoformat() if self.test_end_time else None,
                "duration": None,
                "config": self.config
            },
            "metrics": {},
            "recommendations": []
        }
        
        # Calcular duração
        if self.test_start_time and self.test_end_time:
            duration = self.test_end_time - self.test_start_time
            results["test_info"]["duration"] = str(duration)
        
        # Ler relatório JSON se existir
        json_report_path = Path("reports") / self.config["json_report"]
        if json_report_path.exists():
            try:
                with open(json_report_path, 'r') as f:
                    json_data = json.load(f)
                
                # Extrair métricas principais
                if "stats" in json_data:
                    stats = json_data["stats"]
                    results["metrics"] = {
                        "total_requests": stats.get("total_requests", 0),
                        "total_failures": stats.get("total_failures", 0),
                        "avg_response_time": stats.get("avg_response_time", 0),
                        "max_response_time": stats.get("max_response_time", 0),
                        "min_response_time": stats.get("min_response_time", 0),
                        "requests_per_sec": stats.get("requests_per_sec", 0),
                        "failure_rate": stats.get("failure_rate", 0)
                    }
                
                # Gerar recomendações
                results["recommendations"] = self.generate_recommendations(results["metrics"])
                
            except Exception as e:
                print(f"⚠️ Erro ao ler relatório JSON: {e}")
        
        return results
    
    def generate_recommendations(self, metrics: Dict[str, Any]) -> list:
        """Gera recomendações baseadas nas métricas"""
        recommendations = []
        
        # Análise de taxa de falha
        failure_rate = metrics.get("failure_rate", 0)
        if failure_rate > 10:
            recommendations.append({
                "type": "warning",
                "message": f"Taxa de falha alta ({failure_rate:.2f}%). Verificar validações.",
                "action": "Investigar causas das falhas e ajustar validações"
            })
        elif failure_rate > 5:
            recommendations.append({
                "type": "info",
                "message": f"Taxa de falha moderada ({failure_rate:.2f}%). Monitorar.",
                "action": "Acompanhar tendência de falhas de validação"
            })
        else:
            recommendations.append({
                "type": "success",
                "message": f"Taxa de falha baixa ({failure_rate:.2f}%). Excelente!",
                "action": "Manter configurações de validação atuais"
            })
        
        # Análise de tempo de resposta
        avg_response_time = metrics.get("avg_response_time", 0)
        if avg_response_time > 3000:
            recommendations.append({
                "type": "warning",
                "message": f"Tempo de resposta alto ({avg_response_time:.0f}ms).",
                "action": "Otimizar processo de registro ou aumentar recursos"
            })
        elif avg_response_time > 1500:
            recommendations.append({
                "type": "info",
                "message": f"Tempo de resposta moderado ({avg_response_time:.0f}ms).",
                "action": "Considerar otimizações se necessário"
            })
        else:
            recommendations.append({
                "type": "success",
                "message": f"Tempo de resposta bom ({avg_response_time:.0f}ms).",
                "action": "Manter performance atual"
            })
        
        # Análise de throughput
        requests_per_sec = metrics.get("requests_per_sec", 0)
        if requests_per_sec < 5:
            recommendations.append({
                "type": "warning",
                "message": f"Throughput baixo ({requests_per_sec:.1f} req/s).",
                "action": "Investigar gargalos no processo de registro"
            })
        elif requests_per_sec < 20:
            recommendations.append({
                "type": "info",
                "message": f"Throughput moderado ({requests_per_sec:.1f} req/s).",
                "action": "Avaliar necessidade de otimização"
            })
        else:
            recommendations.append({
                "type": "success",
                "message": f"Throughput bom ({requests_per_sec:.1f} req/s).",
                "action": "Manter configurações atuais"
            })
        
        # Recomendações específicas de segurança
        recommendations.append({
            "type": "info",
            "message": "Verificar logs de segurança para tentativas de registro malicioso.",
            "action": "Monitorar padrões suspeitos de registro"
        })
        
        recommendations.append({
            "type": "info",
            "message": "Validar rate limiting para prevenir spam de registros.",
            "action": "Ajustar limites se necessário"
        })
        
        return recommendations
    
    def generate_report(self, results: Dict[str, Any]) -> None:
        """Gera relatório final"""
        print("📋 Gerando relatório final...")
        
        report_path = Path("reports") / "auth_register_test_summary.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 🧪 RELATÓRIO - TESTE DE CARGA AUTH REGISTER\n\n")
            
            f.write("## 📊 Informações do Teste\n\n")
            f.write(f"- **Nome**: {results['test_info']['name']}\n")
            f.write(f"- **Início**: {results['test_info']['start_time']}\n")
            f.write(f"- **Fim**: {results['test_info']['end_time']}\n")
            f.write(f"- **Duração**: {results['test_info']['duration']}\n\n")
            
            f.write("## ⚙️ Configuração\n\n")
            config = results['test_info']['config']
            f.write(f"- **Host**: {config['host']}\n")
            f.write(f"- **Usuários**: {config['users']}\n")
            f.write(f"- **Spawn Rate**: {config['spawn_rate']}\n")
            f.write(f"- **Duração**: {config['run_time']}\n\n")
            
            f.write("## 📈 Métricas Principais\n\n")
            metrics = results['metrics']
            f.write(f"- **Total de Requisições**: {metrics.get('total_requests', 0):,}\n")
            f.write(f"- **Falhas**: {metrics.get('total_failures', 0):,}\n")
            f.write(f"- **Taxa de Falha**: {metrics.get('failure_rate', 0):.2f}%\n")
            f.write(f"- **Tempo Médio de Resposta**: {metrics.get('avg_response_time', 0):.0f}ms\n")
            f.write(f"- **Tempo Máximo de Resposta**: {metrics.get('max_response_time', 0):.0f}ms\n")
            f.write(f"- **Throughput**: {metrics.get('requests_per_sec', 0):.1f} req/s\n\n")
            
            f.write("## 💡 Recomendações\n\n")
            for rec in results['recommendations']:
                icon = "✅" if rec['type'] == 'success' else "⚠️" if rec['type'] == 'warning' else "ℹ️"
                f.write(f"{icon} **{rec['message']}**\n")
                f.write(f"   *Ação: {rec['action']}*\n\n")
            
            f.write("## 🔒 Considerações de Segurança\n\n")
            f.write("- **Validação de Dados**: Verificar se todas as validações estão funcionando\n")
            f.write("- **Rate Limiting**: Confirmar proteção contra spam de registros\n")
            f.write("- **Dados Duplicados**: Validar tratamento de emails/usuários duplicados\n")
            f.write("- **Complexidade de Senha**: Verificar se as regras estão sendo aplicadas\n")
            f.write("- **Logs de Auditoria**: Confirmar registro de tentativas de registro\n\n")
            
            f.write("## 📁 Arquivos Gerados\n\n")
            f.write("- `auth_register_test_report.html` - Relatório HTML detalhado\n")
            f.write("- `auth_register_test_report.json` - Dados brutos em JSON\n")
            f.write("- `auth_register_test_report.csv` - Dados em CSV\n")
            f.write("- `auth_register_test.log` - Logs da execução\n")
            f.write("- `auth_register_test_summary.md` - Este relatório\n\n")
            
            f.write("## 🎯 Próximos Passos\n\n")
            f.write("1. Analisar relatório HTML para detalhes completos\n")
            f.write("2. Verificar logs para identificar problemas específicos\n")
            f.write("3. Implementar recomendações conforme necessário\n")
            f.write("4. Executar testes de regressão após otimizações\n")
            f.write("5. Validar segurança contra ataques de enumeração\n")
        
        print(f"✅ Relatório gerado: {report_path}")
    
    def run(self) -> bool:
        """Executa o teste completo"""
        print("🚀 INICIANDO TESTE DE CARGA - AUTH REGISTER")
        print("=" * 60)
        
        # Validação do ambiente
        if not self.validate_environment():
            return False
        
        # Preparação do ambiente
        if not self.prepare_test_environment():
            return False
        
        # Execução do teste
        if not self.execute_test():
            return False
        
        # Análise dos resultados
        results = self.analyze_results()
        
        # Geração do relatório
        self.generate_report(results)
        
        print("=" * 60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print(f"📊 Taxa de falha: {results['metrics'].get('failure_rate', 0):.2f}%")
        print(f"⏱️ Tempo médio: {results['metrics'].get('avg_response_time', 0):.0f}ms")
        print(f"🚀 Throughput: {results['metrics'].get('requests_per_sec', 0):.1f} req/s")
        
        return True

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executar teste de carga para auth register")
    parser.add_argument("--host", default="http://localhost:8000", help="Host do servidor")
    parser.add_argument("--users", type=int, default=30, help="Número de usuários")
    parser.add_argument("--spawn-rate", type=int, default=5, help="Taxa de spawn")
    parser.add_argument("--run-time", default="5m", help="Duração do teste")
    parser.add_argument("--web", action="store_true", help="Executar em modo web")
    
    args = parser.parse_args()
    
    # Atualizar configuração com argumentos
    TEST_CONFIG.update({
        "host": args.host,
        "users": args.users,
        "spawn_rate": args.spawn_rate,
        "run_time": args.run_time,
        "headless": not args.web
    })
    
    # Executar teste
    runner = AuthRegisterTestRunner(TEST_CONFIG)
    success = runner.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
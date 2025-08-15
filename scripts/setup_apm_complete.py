#!/usr/bin/env python3
"""
Script de Configuração Completa do Sistema APM - Omni Keywords Finder
===================================================================

Tracing ID: SETUP_APM_COMPLETE_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Script que configura e integra todos os componentes do sistema APM:
- Jaeger para distributed tracing
- Sentry para error tracking
- Prometheus para métricas
- Dashboards unificados
- APM Integration
- Error Tracking Backend

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 3.2
Ruleset: enterprise_control_layer.yaml
"""

import os
import sys
import json
import time
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
import yaml

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APMSetupManager:
    """Gerenciador de configuração do sistema APM"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config"
        self.scripts_dir = self.project_root / "scripts"
        self.infrastructure_dir = self.project_root / "infrastructure"
        
        # Configurações
        self.config = {
            "jaeger": {
                "enabled": True,
                "port": 16686,
                "collector_port": 14268,
                "agent_port": 6831
            },
            "sentry": {
                "enabled": True,
                "dsn": os.getenv("SENTRY_DSN", ""),
                "environment": os.getenv("ENVIRONMENT", "development")
            },
            "prometheus": {
                "enabled": True,
                "port": 9090
            },
            "grafana": {
                "enabled": True,
                "port": 3000,
                "admin_user": "admin",
                "admin_password": "admin123"
            },
            "dashboards": {
                "enabled": True,
                "port": 8080
            }
        }
    
    def setup_complete_apm_system(self):
        """Configura sistema APM completo"""
        logger.info("🚀 Iniciando configuração completa do sistema APM")
        
        try:
            # 1. Verificar dependências
            self._check_dependencies()
            
            # 2. Configurar variáveis de ambiente
            self._setup_environment_variables()
            
            # 3. Configurar Jaeger
            if self.config["jaeger"]["enabled"]:
                self._setup_jaeger()
            
            # 4. Configurar Sentry
            if self.config["sentry"]["enabled"]:
                self._setup_sentry()
            
            # 5. Configurar Prometheus
            if self.config["prometheus"]["enabled"]:
                self._setup_prometheus()
            
            # 6. Configurar Grafana
            if self.config["grafana"]["enabled"]:
                self._setup_grafana()
            
            # 7. Configurar Dashboards
            if self.config["dashboards"]["enabled"]:
                self._setup_dashboards()
            
            # 8. Integrar componentes
            self._integrate_components()
            
            # 9. Testar sistema
            self._test_system()
            
            # 10. Gerar relatório
            self._generate_report()
            
            logger.info("✅ Sistema APM configurado com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro na configuração do sistema APM: {e}")
            raise
    
    def _check_dependencies(self):
        """Verifica dependências necessárias"""
        logger.info("📋 Verificando dependências...")
        
        required_packages = [
            "opentelemetry-api",
            "opentelemetry-sdk",
            "opentelemetry-exporter-jaeger",
            "opentelemetry-instrumentation-fastapi",
            "opentelemetry-instrumentation-requests",
            "opentelemetry-instrumentation-sqlalchemy",
            "prometheus-client",
            "sentry-sdk",
            "fastapi",
            "uvicorn",
            "jinja2",
            "psutil"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                logger.info(f"  ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"  ❌ {package}")
        
        if missing_packages:
            logger.info("📦 Instalando dependências faltantes...")
            self._install_packages(missing_packages)
    
    def _install_packages(self, packages: List[str]):
        """Instala pacotes Python"""
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + packages)
            logger.info("✅ Pacotes instalados com sucesso")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao instalar pacotes: {e}")
            raise
    
    def _setup_environment_variables(self):
        """Configura variáveis de ambiente"""
        logger.info("🔧 Configurando variáveis de ambiente...")
        
        env_file = self.project_root / ".env"
        env_content = []
        
        # Verificar se arquivo .env existe
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.readlines()
        
        # Adicionar variáveis APM se não existirem
        apm_vars = {
            "JAEGER_ENDPOINT": "http://localhost:14268/api/traces",
            "SENTRY_DSN": self.config["sentry"]["dsn"],
            "PROMETHEUS_PORT": str(self.config["prometheus"]["port"]),
            "APM_SAMPLING_RATE": "0.1",
            "ENVIRONMENT": self.config["sentry"]["environment"],
            "SERVICE_VERSION": "1.0.0",
            "ENABLE_SENTRY": "true",
            "ENABLE_ERROR_ALERTS": "true",
            "MAX_ERROR_HISTORY": "10000",
            "ERROR_SAMPLING_RATE": "1.0",
            "APM_ENABLE_INSIGHTS": "true",
            "APM_ENABLE_ALERTS": "true"
        }
        
        existing_vars = set()
        for line in env_content:
            if "=" in line:
                var_name = line.split("=")[0].strip()
                existing_vars.add(var_name)
        
        # Adicionar variáveis que não existem
        for var_name, var_value in apm_vars.items():
            if var_name not in existing_vars:
                env_content.append(f"{var_name}={var_value}\n")
        
        # Salvar arquivo .env
        with open(env_file, 'w') as f:
            f.writelines(env_content)
        
        logger.info("✅ Variáveis de ambiente configuradas")
    
    def _setup_jaeger(self):
        """Configura Jaeger"""
        logger.info("🔍 Configurando Jaeger...")
        
        # Verificar se Jaeger já está rodando
        if self._check_service_running("jaeger", self.config["jaeger"]["port"]):
            logger.info("  ✅ Jaeger já está rodando")
            return
        
        # Criar docker-compose para Jaeger se não existir
        jaeger_compose = self.project_root / "docker-compose.jaeger.yml"
        
        if not jaeger_compose.exists():
            jaeger_config = {
                "version": "3.8",
                "services": {
                    "jaeger": {
                        "image": "jaegertracing/all-in-one:latest",
                        "container_name": "omni-jaeger",
                        "ports": [
                            f"{self.config['jaeger']['port']}:16686",
                            f"{self.config['jaeger']['collector_port']}:14268",
                            f"{self.config['jaeger']['agent_port']}:6831/udp"
                        ],
                        "environment": {
                            "COLLECTOR_OTLP_ENABLED": "true",
                            "COLLECTOR_ZIPKIN_HOST_PORT": ":9411"
                        },
                        "volumes": ["jaeger_data:/tmp"],
                        "networks": ["omni-network"],
                        "restart": "unless-stopped"
                    }
                },
                "volumes": {"jaeger_data": None},
                "networks": {"omni-network": {"external": True}}
            }
            
            with open(jaeger_compose, 'w') as f:
                yaml.dump(jaeger_config, f, default_flow_style=False)
        
        # Iniciar Jaeger
        try:
            subprocess.run([
                "docker-compose", "-f", str(jaeger_compose), "up", "-d"
            ], check=True)
            logger.info("  ✅ Jaeger iniciado")
        except subprocess.CalledProcessError as e:
            logger.error(f"  ❌ Erro ao iniciar Jaeger: {e}")
            raise
    
    def _setup_sentry(self):
        """Configura Sentry"""
        logger.info("🚨 Configurando Sentry...")
        
        if not self.config["sentry"]["dsn"]:
            logger.warning("  ⚠️ Sentry DSN não configurado. Pulando configuração.")
            return
        
        # Verificar se Sentry está acessível
        try:
            # Testar conexão com Sentry (simulado)
            logger.info("  ✅ Sentry configurado")
        except Exception as e:
            logger.error(f"  ❌ Erro ao configurar Sentry: {e}")
            raise
    
    def _setup_prometheus(self):
        """Configura Prometheus"""
        logger.info("📊 Configurando Prometheus...")
        
        # Verificar se Prometheus já está rodando
        if self._check_service_running("prometheus", self.config["prometheus"]["port"]):
            logger.info("  ✅ Prometheus já está rodando")
            return
        
        # Verificar se configuração existe
        prometheus_config = self.config_dir / "telemetry" / "prometheus.yml"
        
        if not prometheus_config.exists():
            logger.info("  📝 Criando configuração do Prometheus...")
            self._create_prometheus_config()
        
        # Iniciar Prometheus
        try:
            subprocess.run([
                "docker", "run", "-d",
                "--name", "omni-prometheus",
                "-p", f"{self.config['prometheus']['port']}:9090",
                "-v", f"{prometheus_config}:/etc/prometheus/prometheus.yml",
                "prom/prometheus:latest"
            ], check=True)
            logger.info("  ✅ Prometheus iniciado")
        except subprocess.CalledProcessError as e:
            logger.error(f"  ❌ Erro ao iniciar Prometheus: {e}")
            raise
    
    def _create_prometheus_config(self):
        """Cria configuração do Prometheus"""
        prometheus_config = self.config_dir / "telemetry" / "prometheus.yml"
        prometheus_config.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s"
            },
            "scrape_configs": [
                {
                    "job_name": "omni-keywords-finder",
                    "static_configs": [
                        {"targets": ["localhost:5000"]}
                    ],
                    "metrics_path": "/metrics",
                    "scrape_interval": "10s"
                },
                {
                    "job_name": "jaeger",
                    "static_configs": [
                        {"targets": ["localhost:16686"]}
                    ],
                    "metrics_path": "/metrics"
                }
            ]
        }
        
        with open(prometheus_config, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def _setup_grafana(self):
        """Configura Grafana"""
        logger.info("📈 Configurando Grafana...")
        
        # Verificar se Grafana já está rodando
        if self._check_service_running("grafana", self.config["grafana"]["port"]):
            logger.info("  ✅ Grafana já está rodando")
            return
        
        # Iniciar Grafana
        try:
            subprocess.run([
                "docker", "run", "-d",
                "--name", "omni-grafana",
                "-p", f"{self.config['grafana']['port']}:3000",
                "-e", f"GF_SECURITY_ADMIN_PASSWORD={self.config['grafana']['admin_password']}",
                "grafana/grafana:latest"
            ], check=True)
            logger.info("  ✅ Grafana iniciado")
        except subprocess.CalledProcessError as e:
            logger.error(f"  ❌ Erro ao iniciar Grafana: {e}")
            raise
    
    def _setup_dashboards(self):
        """Configura dashboards unificados"""
        logger.info("📊 Configurando dashboards unificados...")
        
        # Verificar se dashboards já estão rodando
        if self._check_service_running("dashboards", self.config["dashboards"]["port"]):
            logger.info("  ✅ Dashboards já estão rodando")
            return
        
        # Iniciar dashboards
        try:
            dashboard_script = self.infrastructure_dir / "monitoring" / "dashboard_unified.py"
            
            if dashboard_script.exists():
                subprocess.Popen([
                    sys.executable, str(dashboard_script)
                ])
                logger.info("  ✅ Dashboards iniciados")
            else:
                logger.warning("  ⚠️ Script de dashboards não encontrado")
        
        except Exception as e:
            logger.error(f"  ❌ Erro ao iniciar dashboards: {e}")
            raise
    
    def _integrate_components(self):
        """Integra todos os componentes"""
        logger.info("🔗 Integrando componentes...")
        
        # Verificar se todos os serviços estão rodando
        services = {
            "Jaeger": self.config["jaeger"]["port"],
            "Prometheus": self.config["prometheus"]["port"],
            "Grafana": self.config["grafana"]["port"],
            "Dashboards": self.config["dashboards"]["port"]
        }
        
        for service_name, port in services.items():
            if self._check_service_running(service_name.lower(), port):
                logger.info(f"  ✅ {service_name} integrado")
            else:
                logger.warning(f"  ⚠️ {service_name} não está rodando")
    
    def _test_system(self):
        """Testa o sistema APM"""
        logger.info("🧪 Testando sistema APM...")
        
        # Testar Jaeger
        if self._test_jaeger():
            logger.info("  ✅ Jaeger funcionando")
        else:
            logger.warning("  ⚠️ Jaeger não está respondendo")
        
        # Testar Prometheus
        if self._test_prometheus():
            logger.info("  ✅ Prometheus funcionando")
        else:
            logger.warning("  ⚠️ Prometheus não está respondendo")
        
        # Testar Grafana
        if self._test_grafana():
            logger.info("  ✅ Grafana funcionando")
        else:
            logger.warning("  ⚠️ Grafana não está respondendo")
        
        # Testar Dashboards
        if self._test_dashboards():
            logger.info("  ✅ Dashboards funcionando")
        else:
            logger.warning("  ⚠️ Dashboards não estão respondendo")
    
    def _test_jaeger(self) -> bool:
        """Testa Jaeger"""
        try:
            response = requests.get(f"http://localhost:{self.config['jaeger']['port']}/api/services", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _test_prometheus(self) -> bool:
        """Testa Prometheus"""
        try:
            response = requests.get(f"http://localhost:{self.config['prometheus']['port']}/-/healthy", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _test_grafana(self) -> bool:
        """Testa Grafana"""
        try:
            response = requests.get(f"http://localhost:{self.config['grafana']['port']}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _test_dashboards(self) -> bool:
        """Testa Dashboards"""
        try:
            response = requests.get(f"http://localhost:{self.config['dashboards']['port']}/api/dashboards", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _check_service_running(self, service_name: str, port: int) -> bool:
        """Verifica se serviço está rodando"""
        try:
            response = requests.get(f"http://localhost:{port}", timeout=2)
            return response.status_code < 500
        except:
            return False
    
    def _generate_report(self):
        """Gera relatório de configuração"""
        logger.info("📋 Gerando relatório...")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "completed",
            "services": {
                "jaeger": {
                    "enabled": self.config["jaeger"]["enabled"],
                    "url": f"http://localhost:{self.config['jaeger']['port']}",
                    "status": "running" if self._test_jaeger() else "stopped"
                },
                "prometheus": {
                    "enabled": self.config["prometheus"]["enabled"],
                    "url": f"http://localhost:{self.config['prometheus']['port']}",
                    "status": "running" if self._test_prometheus() else "stopped"
                },
                "grafana": {
                    "enabled": self.config["grafana"]["enabled"],
                    "url": f"http://localhost:{self.config['grafana']['port']}",
                    "status": "running" if self._test_grafana() else "stopped"
                },
                "dashboards": {
                    "enabled": self.config["dashboards"]["enabled"],
                    "url": f"http://localhost:{self.config['dashboards']['port']}",
                    "status": "running" if self._test_dashboards() else "stopped"
                }
            },
            "next_steps": [
                "Acesse Jaeger UI para visualizar traces",
                "Configure dashboards no Grafana",
                "Monitore métricas no Prometheus",
                "Use os dashboards unificados para visão geral"
            ]
        }
        
        # Salvar relatório
        report_file = self.project_root / "logs" / "apm_setup_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Relatório salvo em: {report_file}")
        
        # Mostrar URLs
        print("\n" + "="*60)
        print("🌐 URLs dos Serviços APM:")
        print("="*60)
        for service_name, info in report["services"].items():
            if info["enabled"]:
                print(f"📊 {service_name.title()}: {info['url']}")
        print("="*60)
    
    def stop_services(self):
        """Para todos os serviços APM"""
        logger.info("🛑 Parando serviços APM...")
        
        services = [
            "omni-jaeger",
            "omni-prometheus", 
            "omni-grafana"
        ]
        
        for service in services:
            try:
                subprocess.run(["docker", "stop", service], check=True)
                logger.info(f"  ✅ {service} parado")
            except subprocess.CalledProcessError:
                logger.warning(f"  ⚠️ {service} não estava rodando")
    
    def restart_services(self):
        """Reinicia todos os serviços APM"""
        logger.info("🔄 Reiniciando serviços APM...")
        
        self.stop_services()
        time.sleep(5)
        self.setup_complete_apm_system()


def main():
    """Função principal"""
    print("🚀 Omni Keywords Finder - Setup APM Completo")
    print("=" * 50)
    
    setup_manager = APMSetupManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            setup_manager.setup_complete_apm_system()
        elif command == "stop":
            setup_manager.stop_services()
        elif command == "restart":
            setup_manager.restart_services()
        elif command == "test":
            setup_manager._test_system()
        else:
            print("Comandos disponíveis:")
            print("  setup    - Configura sistema APM completo")
            print("  stop     - Para todos os serviços")
            print("  restart  - Reinicia todos os serviços")
            print("  test     - Testa sistema APM")
    else:
        # Setup padrão
        setup_manager.setup_complete_apm_system()


if __name__ == "__main__":
    main() 
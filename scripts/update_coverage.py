#!/usr/bin/env python3
"""
Script para atualização de cobertura de testes do projeto.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(name)string_data - %(levelname)string_data - %(message)string_data',
    handlers=[
        logging.FileHandler('logs/coverage_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CoverageUpdater:
    """Atualizador de cobertura de testes."""
    
    def __init__(self, project_root: str):
        """Inicializa o atualizador de cobertura.
        
        Args:
            project_root: Caminho raiz do projeto
        """
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / 'docs'
        self.trigger_config = self._load_trigger_config()
        
    def _load_trigger_config(self) -> Dict:
        """Carrega configuração de triggers.
        
        Returns:
            Dict com configuração de triggers
        """
        config_path = self.docs_dir / 'trigger_config.json'
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar trigger_config.json: {e}")
            raise
            
    def update_coverage(self) -> None:
        """Atualiza cobertura de testes."""
        try:
            logger.info("Iniciando atualização de cobertura...")
            
            # Executa testes com cobertura
            self._run_tests_with_coverage()
            
            # Processa resultados
            self._process_coverage_results()
            
            # Atualiza documentação
            self._update_coverage_docs()
            
            logger.info("Atualização de cobertura concluída com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro na atualização de cobertura: {e}")
            raise
            
    def _run_tests_with_coverage(self) -> None:
        """Executa testes com cobertura."""
        try:
            # Executa testes unitários
            logger.info("Executando testes unitários...")
            subprocess.run([
                'pytest',
                '--cov=domain',
                '--cov=app',
                '--cov=infrastructure',
                '--cov-report=term-missing',
                '--cov-report=html:coverage/html',
                '--cov-report=xml:coverage/coverage.xml',
                'tests/unit/'
            ], check=True)
            
            # Executa testes de integração
            logger.info("Executando testes de integração...")
            subprocess.run([
                'pytest',
                '--cov=domain',
                '--cov=app',
                '--cov=infrastructure',
                '--cov-append',
                '--cov-report=term-missing',
                '--cov-report=html:coverage/html',
                '--cov-report=xml:coverage/coverage.xml',
                'tests/integration/'
            ], check=True)
            
            # Executa testes E2E
            logger.info("Executando testes E2E...")
            subprocess.run([
                'pytest',
                '--cov=domain',
                '--cov=app',
                '--cov=infrastructure',
                '--cov-append',
                '--cov-report=term-missing',
                '--cov-report=html:coverage/html',
                '--cov-report=xml:coverage/coverage.xml',
                'tests/e2e/'
            ], check=True)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao executar testes: {e}")
            raise
            
    def _process_coverage_results(self) -> None:
        """Processa resultados de cobertura."""
        try:
            # Carrega resultados XML
            coverage_file = self.project_root / 'coverage' / 'coverage.xml'
            if not coverage_file.exists():
                raise FileNotFoundError("Arquivo de cobertura não encontrado")
                
            # Processa resultados por camada
            self._process_domain_coverage()
            self._process_application_coverage()
            self._process_infrastructure_coverage()
            
        except Exception as e:
            logger.error(f"Erro ao processar resultados: {e}")
            raise
            
    def _process_domain_coverage(self) -> None:
        """Processa cobertura da camada de domínio."""
        try:
            # Executa cobertura específica do domínio
            subprocess.run([
                'pytest',
                '--cov=domain',
                '--cov-report=term-missing',
                '--cov-report=html:coverage/domain',
                'tests/unit/domain/',
                'tests/integration/domain/'
            ], check=True)
            
            # Gera relatório específico
            self._generate_layer_report('domain')
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao processar cobertura do domínio: {e}")
            raise
            
    def _process_application_coverage(self) -> None:
        """Processa cobertura da camada de aplicação."""
        try:
            # Executa cobertura específica da aplicação
            subprocess.run([
                'pytest',
                '--cov=app',
                '--cov-report=term-missing',
                '--cov-report=html:coverage/app',
                'tests/unit/app/',
                'tests/integration/app/',
                'tests/e2e/app/'
            ], check=True)
            
            # Gera relatório específico
            self._generate_layer_report('app')
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao processar cobertura da aplicação: {e}")
            raise
            
    def _process_infrastructure_coverage(self) -> None:
        """Processa cobertura da camada de infraestrutura."""
        try:
            # Executa cobertura específica da infraestrutura
            subprocess.run([
                'pytest',
                '--cov=infrastructure',
                '--cov-report=term-missing',
                '--cov-report=html:coverage/infrastructure',
                'tests/unit/infrastructure/',
                'tests/integration/infrastructure/',
                'tests/e2e/infrastructure/'
            ], check=True)
            
            # Gera relatório específico
            self._generate_layer_report('infrastructure')
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao processar cobertura da infraestrutura: {e}")
            raise
            
    def _generate_layer_report(self, layer: str) -> None:
        """Gera relatório específico de camada.
        
        Args:
            layer: Nome da camada
        """
        try:
            # Carrega resultados
            coverage_file = self.project_root / 'coverage' / f'{layer}' / 'coverage.xml'
            if not coverage_file.exists():
                raise FileNotFoundError(f"Arquivo de cobertura de {layer} não encontrado")
                
            # Gera relatório markdown
            report = [
                f"# Cobertura de Testes - {layer.capitalize()}\n",
                f"Data: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}\n",
                "\n## Métricas\n"
            ]
            
            # Adiciona métricas
            report.extend([
                "- Cobertura Total: XX%",
                "- Testes Unitários: XX%",
                "- Testes de Integração: XX%",
                "- Testes E2E: XX%"
            ])
            
            # Adiciona detalhes
            report.extend([
                "\n## Detalhes\n",
                "- Arquivos cobertos: XX",
                "- Linhas cobertas: XX",
                "- Branches cobertos: XX",
                "- Funções cobertas: XX"
            ])
            
            # Adiciona gaps
            report.extend([
                "\n## Gaps Identificados\n",
                "- Arquivo1: Linhas não cobertas",
                "- Arquivo2: Funções não testadas",
                "- Arquivo3: Branches não cobertos"
            ])
            
            # Salva relatório
            report_path = self.docs_dir / f'coverage_{layer}.md'
            with open(report_path, 'w') as f:
                f.write('\n'.join(report))
                
            logger.info(f"Relatório de cobertura de {layer} gerado em {report_path}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de {layer}: {e}")
            raise
            
    def _update_coverage_docs(self) -> None:
        """Atualiza documentação de cobertura."""
        try:
            # Gera sumário
            summary = [
                "# Cobertura de Testes\n",
                f"Data: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}\n",
                "\n## Visão Geral\n",
                "- Cobertura Total: XX%",
                "- Testes Unitários: XX%",
                "- Testes de Integração: XX%",
                "- Testes E2E: XX%",
                "\n## Camadas\n",
                "- [Domínio](coverage_domain.md)",
                "- [Aplicação](coverage_app.md)",
                "- [Infraestrutura](coverage_infrastructure.md)",
                "\n## Relatórios Detalhados\n",
                "- [HTML](coverage/html/index.html)",
                "- [XML](coverage/coverage.xml)",
                "\n## Histórico\n",
                "- [Changelog](coverage_changelog.md)"
            ]
            
            # Salva sumário
            summary_path = self.docs_dir / 'coverage.md'
            with open(summary_path, 'w') as f:
                f.write('\n'.join(summary))
                
            logger.info(f"Documentação de cobertura atualizada em {summary_path}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar documentação: {e}")
            raise

def main():
    """Função principal."""
    try:
        # Obtém diretório raiz do projeto
        project_root = os.getenv('PROJECT_ROOT', os.getcwd())
        
        # Inicializa atualizador
        updater = CoverageUpdater(project_root)
        
        # Atualiza cobertura
        updater.update_coverage()
        
    except Exception as e:
        logger.error(f"Erro na execução do script: {e}")
        exit(1)

if __name__ == '__main__':
    main() 
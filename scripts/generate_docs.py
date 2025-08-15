#!/usr/bin/env python3
"""
Script para geração automática de documentação do projeto.
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
        logging.FileHandler('logs/docs_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentationGenerator:
    """Gerador de documentação do projeto."""
    
    def __init__(self, project_root: str):
        """Inicializa o gerador de documentação.
        
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
            
    def generate_all_docs(self) -> None:
        """Gera toda a documentação do projeto."""
        try:
            logger.info("Iniciando geração de documentação...")
            
            # Gera documentação por camada
            self._generate_domain_docs()
            self._generate_application_docs()
            self._generate_infrastructure_docs()
            
            # Gera documentação de API
            self._generate_api_docs()
            
            # Atualiza índices e sumários
            self._update_indexes()
            
            logger.info("Geração de documentação concluída com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro na geração de documentação: {e}")
            raise
            
    def _generate_domain_docs(self) -> None:
        """Gera documentação da camada de domínio."""
        logger.info("Gerando documentação do domínio...")
        
        domain_dir = self.project_root / 'domain'
        if not domain_dir.exists():
            logger.warning("Diretório domain não encontrado")
            return
            
        # Gera documentação dos modelos
        models_file = domain_dir / 'models.py'
        if models_file.exists():
            self._generate_model_docs(models_file)
            
        # Gera documentação dos casos de uso
        use_cases_dir = domain_dir / 'use_cases'
        if use_cases_dir.exists():
            self._generate_use_case_docs(use_cases_dir)
            
    def _generate_application_docs(self) -> None:
        """Gera documentação da camada de aplicação."""
        logger.info("Gerando documentação da aplicação...")
        
        app_dir = self.project_root / 'app'
        if not app_dir.exists():
            logger.warning("Diretório app não encontrado")
            return
            
        # Gera documentação da API
        api_dir = app_dir / 'api'
        if api_dir.exists():
            self._generate_api_docs(api_dir)
            
        # Gera documentação dos componentes
        components_dir = app_dir / 'components'
        if components_dir.exists():
            self._generate_component_docs(components_dir)
            
    def _generate_infrastructure_docs(self) -> None:
        """Gera documentação da camada de infraestrutura."""
        logger.info("Gerando documentação da infraestrutura...")
        
        infra_dir = self.project_root / 'infrastructure'
        if not infra_dir.exists():
            logger.warning("Diretório infrastructure não encontrado")
            return
            
        # Gera documentação dos adaptadores
        adapters_dir = infra_dir / 'adapters'
        if adapters_dir.exists():
            self._generate_adapter_docs(adapters_dir)
            
        # Gera documentação dos repositórios
        repos_dir = infra_dir / 'repositories'
        if repos_dir.exists():
            self._generate_repository_docs(repos_dir)
            
    def _generate_model_docs(self, models_file: Path) -> None:
        """Gera documentação dos modelos.
        
        Args:
            models_file: Caminho do arquivo de modelos
        """
        try:
            # Extrai docstrings e anotações
            output = subprocess.run(
                ['pydoc', str(models_file)],
                capture_output=True,
                text=True
            )
            
            if output.returncode == 0:
                # Salva documentação
                docs_file = self.docs_dir / 'models.md'
                with open(docs_file, 'w') as f:
                    f.write(output.stdout)
                    
                logger.info(f"Documentação dos modelos gerada em {docs_file}")
            else:
                logger.error(f"Erro ao gerar documentação dos modelos: {output.stderr}")
                
        except Exception as e:
            logger.error(f"Erro ao processar modelos: {e}")
            
    def _generate_use_case_docs(self, use_cases_dir: Path) -> None:
        """Gera documentação dos casos de uso.
        
        Args:
            use_cases_dir: Diretório de casos de uso
        """
        try:
            docs = []
            
            # Processa cada arquivo de caso de uso
            for use_case_file in use_cases_dir.glob('*.py'):
                output = subprocess.run(
                    ['pydoc', str(use_case_file)],
                    capture_output=True,
                    text=True
                )
                
                if output.returncode == 0:
                    docs.append(output.stdout)
                else:
                    logger.error(f"Erro ao processar {use_case_file}: {output.stderr}")
                    
            if docs:
                # Salva documentação
                docs_file = self.docs_dir / 'use_cases.md'
                with open(docs_file, 'w') as f:
                    f.write('\n\n'.join(docs))
                    
                logger.info(f"Documentação dos casos de uso gerada em {docs_file}")
                
        except Exception as e:
            logger.error(f"Erro ao processar casos de uso: {e}")
            
    def _generate_api_docs(self, api_dir: Optional[Path] = None) -> None:
        """Gera documentação da API.
        
        Args:
            api_dir: Diretório da API (opcional)
        """
        try:
            if api_dir is None:
                api_dir = self.project_root / 'app' / 'api'
                
            if not api_dir.exists():
                logger.warning(f"Diretório {api_dir} não encontrado")
                return
                
            # Gera documentação OpenAPI
            output = subprocess.run(
                ['python', '-m', 'flask', 'openapi'],
                cwd=str(api_dir),
                capture_output=True,
                text=True
            )
            
            if output.returncode == 0:
                # Salva especificação OpenAPI
                openapi_file = self.docs_dir / 'openapi.json'
                with open(openapi_file, 'w') as f:
                    f.write(output.stdout)
                    
                # Gera documentação HTML
                subprocess.run([
                    'redoc-cli',
                    'bundle',
                    str(openapi_file),
                    '-o',
                    str(self.docs_dir / 'api.html')
                ])
                
                logger.info("Documentação da API gerada com sucesso")
            else:
                logger.error(f"Erro ao gerar documentação da API: {output.stderr}")
                
        except Exception as e:
            logger.error(f"Erro ao processar API: {e}")
            
    def _generate_component_docs(self, components_dir: Path) -> None:
        """Gera documentação dos componentes.
        
        Args:
            components_dir: Diretório de componentes
        """
        try:
            docs = []
            
            # Processa cada componente
            for component_file in components_dir.glob('**/*.{ts,tsx}'):
                # Extrai documentação JSDoc
                output = subprocess.run(
                    ['jsdoc2md', str(component_file)],
                    capture_output=True,
                    text=True
                )
                
                if output.returncode == 0:
                    docs.append(output.stdout)
                else:
                    logger.error(f"Erro ao processar {component_file}: {output.stderr}")
                    
            if docs:
                # Salva documentação
                docs_file = self.docs_dir / 'components.md'
                with open(docs_file, 'w') as f:
                    f.write('\n\n'.join(docs))
                    
                logger.info(f"Documentação dos componentes gerada em {docs_file}")
                
        except Exception as e:
            logger.error(f"Erro ao processar componentes: {e}")
            
    def _generate_adapter_docs(self, adapters_dir: Path) -> None:
        """Gera documentação dos adaptadores.
        
        Args:
            adapters_dir: Diretório de adaptadores
        """
        try:
            docs = []
            
            # Processa cada adaptador
            for adapter_file in adapters_dir.glob('*.py'):
                output = subprocess.run(
                    ['pydoc', str(adapter_file)],
                    capture_output=True,
                    text=True
                )
                
                if output.returncode == 0:
                    docs.append(output.stdout)
                else:
                    logger.error(f"Erro ao processar {adapter_file}: {output.stderr}")
                    
            if docs:
                # Salva documentação
                docs_file = self.docs_dir / 'adapters.md'
                with open(docs_file, 'w') as f:
                    f.write('\n\n'.join(docs))
                    
                logger.info(f"Documentação dos adaptadores gerada em {docs_file}")
                
        except Exception as e:
            logger.error(f"Erro ao processar adaptadores: {e}")
            
    def _generate_repository_docs(self, repos_dir: Path) -> None:
        """Gera documentação dos repositórios.
        
        Args:
            repos_dir: Diretório de repositórios
        """
        try:
            docs = []
            
            # Processa cada repositório
            for repo_file in repos_dir.glob('*.py'):
                output = subprocess.run(
                    ['pydoc', str(repo_file)],
                    capture_output=True,
                    text=True
                )
                
                if output.returncode == 0:
                    docs.append(output.stdout)
                else:
                    logger.error(f"Erro ao processar {repo_file}: {output.stderr}")
                    
            if docs:
                # Salva documentação
                docs_file = self.docs_dir / 'repositories.md'
                with open(docs_file, 'w') as f:
                    f.write('\n\n'.join(docs))
                    
                logger.info(f"Documentação dos repositórios gerada em {docs_file}")
                
        except Exception as e:
            logger.error(f"Erro ao processar repositórios: {e}")
            
    def _update_indexes(self) -> None:
        """Atualiza índices e sumários da documentação."""
        try:
            # Gera sumário principal
            summary = [
                "# Documentação do Projeto\n",
                f"Última atualização: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}\n",
                "\n## Índice\n",
                "- [Arquitetura](architecture.md)",
                "- [Modelos](models.md)",
                "- [Casos de Uso](use_cases.md)",
                "- [API](api.html)",
                "- [Componentes](components.md)",
                "- [Adaptadores](adapters.md)",
                "- [Repositórios](repositories.md)",
                "- [Guia de Desenvolvimento](development.md)",
                "- [Guia de Contribuição](contributing.md)",
                "- [Changelog](changelog.md)"
            ]
            
            # Salva sumário
            with open(self.docs_dir / 'index.md', 'w') as f:
                f.write('\n'.join(summary))
                
            logger.info("Índices atualizados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar índices: {e}")

def main():
    """Função principal."""
    try:
        # Obtém diretório raiz do projeto
        project_root = os.getenv('PROJECT_ROOT', os.getcwd())
        
        # Inicializa gerador
        generator = DocumentationGenerator(project_root)
        
        # Gera documentação
        generator.generate_all_docs()
        
    except Exception as e:
        logger.error(f"Erro na execução do script: {e}")
        raise

if __name__ == '__main__':
    main() 
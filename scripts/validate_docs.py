#!/usr/bin/env python3
"""
Script para validação de documentação do projeto.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
import re
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(name)string_data - %(levelname)string_data - %(message)string_data',
    handlers=[
        logging.FileHandler('logs/docs_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentationValidator:
    """Validador de documentação do projeto."""
    
    def __init__(self, project_root: str):
        """Inicializa o validador de documentação.
        
        Args:
            project_root: Caminho raiz do projeto
        """
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / 'docs'
        self.trigger_config = self._load_trigger_config()
        self.validation_results = {
            'errors': [],
            'warnings': [],
            'success': []
        }
        
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
            
    def validate_all_docs(self) -> bool:
        """Valida toda a documentação do projeto.
        
        Returns:
            bool: True se toda documentação é válida
        """
        try:
            logger.info("Iniciando validação de documentação...")
            
            # Valida arquivos obrigatórios
            self._validate_required_files()
            
            # Valida estrutura
            self._validate_structure()
            
            # Valida conteúdo
            self._validate_content()
            
            # Valida links
            self._validate_links()
            
            # Valida formatação
            self._validate_formatting()
            
            # Gera relatório
            self._generate_report()
            
            # Retorna sucesso se não houver erros
            return len(self.validation_results['errors']) == 0
            
        except Exception as e:
            logger.error(f"Erro na validação de documentação: {e}")
            raise
            
    def _validate_required_files(self) -> None:
        """Valida presença de arquivos obrigatórios."""
        required_files = [
            'README.md',
            'CONTRIBUTING.md',
            'architecture.md',
            'development.md',
            'changelog.md',
            'trigger_config.json'
        ]
        
        for file in required_files:
            file_path = self.docs_dir / file
            if not file_path.exists():
                self.validation_results['errors'].append(
                    f"Arquivo obrigatório não encontrado: {file}"
                )
            else:
                self.validation_results['success'].append(
                    f"Arquivo obrigatório encontrado: {file}"
                )
                
    def _validate_structure(self) -> None:
        """Valida estrutura da documentação."""
        # Valida diretórios obrigatórios
        required_dirs = ['api', 'diagrams']
        for dir_name in required_dirs:
            dir_path = self.docs_dir / dir_name
            if not dir_path.exists():
                self.validation_results['errors'].append(
                    f"Diretório obrigatório não encontrado: {dir_name}"
                )
            else:
                self.validation_results['success'].append(
                    f"Diretório obrigatório encontrado: {dir_name}"
                )
                
        # Valida estrutura de arquivos markdown
        for md_file in self.docs_dir.glob('**/*.md'):
            self._validate_markdown_structure(md_file)
            
    def _validate_markdown_structure(self, file_path: Path) -> None:
        """Valida estrutura de arquivo markdown.
        
        Args:
            file_path: Caminho do arquivo markdown
        """
        try:
            with open(file_path) as f:
                content = f.read()
                
            # Valida título principal
            if not re.search(r'^#\string_data+.+$', content, re.MULTILINE):
                self.validation_results['errors'].append(
                    f"Arquivo {file_path} não possui título principal"
                )
                
            # Valida seções
            sections = re.findall(r'^#{2,3}\string_data+.+$', content, re.MULTILINE)
            if not sections:
                self.validation_results['warnings'].append(
                    f"Arquivo {file_path} não possui seções"
                )
                
            # Valida links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for text, url in links:
                if not url.startswith(('http', '/', '#')):
                    self.validation_results['warnings'].append(
                        f"Link potencialmente inválido em {file_path}: {url}"
                    )
                    
        except Exception as e:
            self.validation_results['errors'].append(
                f"Erro ao validar {file_path}: {str(e)}"
            )
            
    def _validate_content(self) -> None:
        """Valida conteúdo da documentação."""
        # Valida README
        readme_path = self.docs_dir / 'README.md'
        if readme_path.exists():
            self._validate_readme(readme_path)
            
        # Valida arquivos de arquitetura
        arch_path = self.docs_dir / 'architecture.md'
        if arch_path.exists():
            self._validate_architecture(arch_path)
            
        # Valida guias
        self._validate_guides()
        
    def _validate_readme(self, file_path: Path) -> None:
        """Valida conteúdo do README.
        
        Args:
            file_path: Caminho do README
        """
        try:
            with open(file_path) as f:
                content = f.read()
                
            # Valida seções obrigatórias
            required_sections = [
                'Descrição',
                'Instalação',
                'Uso',
                'Contribuição',
                'Licença'
            ]
            
            for section in required_sections:
                if section not in content:
                    self.validation_results['warnings'].append(
                        f"README não possui seção: {section}"
                    )
                    
            # Valida badges
            if not re.search(r'!\[.+\]\(.+\)', content):
                self.validation_results['warnings'].append(
                    "README não possui badges"
                )
                
        except Exception as e:
            self.validation_results['errors'].append(
                f"Erro ao validar README: {str(e)}"
            )
            
    def _validate_architecture(self, file_path: Path) -> None:
        """Valida conteúdo da documentação de arquitetura.
        
        Args:
            file_path: Caminho do arquivo de arquitetura
        """
        try:
            with open(file_path) as f:
                content = f.read()
                
            # Valida seções obrigatórias
            required_sections = [
                'Visão Geral',
                'Camadas',
                'Fluxos',
                'Decisões'
            ]
            
            for section in required_sections:
                if section not in content:
                    self.validation_results['warnings'].append(
                        f"Arquitetura não possui seção: {section}"
                    )
                    
            # Valida diagramas
            if not re.search(r'!\[.+\]\(.+\.(png|svg)\)', content):
                self.validation_results['warnings'].append(
                    "Arquitetura não possui diagramas"
                )
                
        except Exception as e:
            self.validation_results['errors'].append(
                f"Erro ao validar arquitetura: {str(e)}"
            )
            
    def _validate_guides(self) -> None:
        """Valida conteúdo dos guias."""
        guide_files = [
            'CONTRIBUTING.md',
            'development.md'
        ]
        
        for guide in guide_files:
            file_path = self.docs_dir / guide
            if file_path.exists():
                self._validate_guide_content(file_path)
                
    def _validate_guide_content(self, file_path: Path) -> None:
        """Valida conteúdo de guia.
        
        Args:
            file_path: Caminho do arquivo de guia
        """
        try:
            with open(file_path) as f:
                content = f.read()
                
            # Valida exemplos de código
            code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
            if not code_blocks:
                self.validation_results['warnings'].append(
                    f"Guia {file_path.name} não possui exemplos de código"
                )
                
            # Valida links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for text, url in links:
                if not url.startswith(('http', '/', '#')):
                    self.validation_results['warnings'].append(
                        f"Link potencialmente inválido em {file_path}: {url}"
                    )
                    
        except Exception as e:
            self.validation_results['errors'].append(
                f"Erro ao validar guia {file_path.name}: {str(e)}"
            )
            
    def _validate_links(self) -> None:
        """Valida links da documentação."""
        # Coleta todos os links
        all_links = set()
        for md_file in self.docs_dir.glob('**/*.md'):
            with open(md_file) as f:
                content = f.read()
                links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                for _, url in links:
                    all_links.add(url)
                    
        # Valida cada link
        for link in all_links:
            if link.startswith('http'):
                # Links externos são apenas avisados
                self.validation_results['warnings'].append(
                    f"Link externo encontrado: {link}"
                )
            elif link.startswith('/'):
                # Links internos são validados
                target_path = self.project_root / link[1:]
                if not target_path.exists():
                    self.validation_results['errors'].append(
                        f"Link interno quebrado: {link}"
                    )
                    
    def _validate_formatting(self) -> None:
        """Valida formatação da documentação."""
        for md_file in self.docs_dir.glob('**/*.md'):
            try:
                with open(md_file) as f:
                    content = f.read()
                    
                # Valida linhas em branco
                if re.search(r'\n{3,}', content):
                    self.validation_results['warnings'].append(
                        f"Arquivo {md_file} possui múltiplas linhas em branco"
                    )
                    
                # Valida espaços em branco
                if re.search(r'[ \t]+$', content, re.MULTILINE):
                    self.validation_results['warnings'].append(
                        f"Arquivo {md_file} possui espaços em branco no final das linhas"
                    )
                    
                # Valida listas
                if re.search(r'^\string_data*[-*+]\string_data+[^\n]+$', content, re.MULTILINE):
                    if not re.search(r'^\string_data*[-*+]\string_data+[^\n]+\n\string_data*[-*+]\string_data+[^\n]+$', content, re.MULTILINE):
                        self.validation_results['warnings'].append(
                            f"Arquivo {md_file} possui lista com item único"
                        )
                        
            except Exception as e:
                self.validation_results['errors'].append(
                    f"Erro ao validar formatação de {md_file}: {str(e)}"
                )
                
    def _generate_report(self) -> None:
        """Gera relatório de validação."""
        try:
            report = [
                "# Relatório de Validação de Documentação\n",
                f"Data: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}\n",
                "\n## Erros\n"
            ]
            
            if self.validation_results['errors']:
                for error in self.validation_results['errors']:
                    report.append(f"- {error}")
            else:
                report.append("Nenhum erro encontrado.")
                
            report.append("\n## Avisos\n")
            if self.validation_results['warnings']:
                for warning in self.validation_results['warnings']:
                    report.append(f"- {warning}")
            else:
                report.append("Nenhum aviso encontrado.")
                
            report.append("\n## Sucessos\n")
            if self.validation_results['success']:
                for success in self.validation_results['success']:
                    report.append(f"- {success}")
            else:
                report.append("Nenhum sucesso registrado.")
                
            # Salva relatório
            report_path = self.docs_dir / 'validation_report.md'
            with open(report_path, 'w') as f:
                f.write('\n'.join(report))
                
            logger.info(f"Relatório de validação gerado em {report_path}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            raise

def main():
    """Função principal."""
    try:
        # Obtém diretório raiz do projeto
        project_root = os.getenv('PROJECT_ROOT', os.getcwd())
        
        # Inicializa validador
        validator = DocumentationValidator(project_root)
        
        # Valida documentação
        is_valid = validator.validate_all_docs()
        
        # Retorna status
        exit(0 if is_valid else 1)
        
    except Exception as e:
        logger.error(f"Erro na execução do script: {e}")
        exit(1)

if __name__ == '__main__':
    main() 
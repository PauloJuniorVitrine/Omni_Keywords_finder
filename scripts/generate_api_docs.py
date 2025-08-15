#!/usr/bin/env python3
"""
Script para geração de documentação da API do projeto.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
from datetime import datetime
import inspect
import importlib.util
import re

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(name)string_data - %(levelname)string_data - %(message)string_data',
    handlers=[
        logging.FileHandler('logs/api_docs_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class APIDocumentationGenerator:
    """Gerador de documentação da API."""
    
    def __init__(self, project_root: str):
        """Inicializa o gerador de documentação da API.
        
        Args:
            project_root: Caminho raiz do projeto
        """
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / 'docs'
        self.api_dir = self.project_root / 'app' / 'api'
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
            
    def generate_api_docs(self) -> None:
        """Gera documentação da API."""
        try:
            logger.info("Iniciando geração de documentação da API...")
            
            # Gera documentação OpenAPI
            self._generate_openapi_docs()
            
            # Gera documentação markdown
            self._generate_markdown_docs()
            
            # Gera exemplos
            self._generate_examples()
            
            # Atualiza índices
            self._update_indexes()
            
            logger.info("Geração de documentação da API concluída com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro na geração de documentação da API: {e}")
            raise
            
    def _generate_openapi_docs(self) -> None:
        """Gera documentação OpenAPI."""
        try:
            # Gera especificação OpenAPI
            output = subprocess.run(
                ['python', '-m', 'flask', 'openapi'],
                cwd=str(self.api_dir),
                capture_output=True,
                text=True
            )
            
            if output.returncode == 0:
                # Salva especificação
                openapi_file = self.docs_dir / 'api' / 'openapi.json'
                with open(openapi_file, 'w') as f:
                    f.write(output.stdout)
                    
                # Gera documentação HTML
                subprocess.run([
                    'redoc-cli',
                    'bundle',
                    str(openapi_file),
                    '-o',
                    str(self.docs_dir / 'api' / 'api.html')
                ])
                
                logger.info("Documentação OpenAPI gerada com sucesso")
            else:
                logger.error(f"Erro ao gerar documentação OpenAPI: {output.stderr}")
                
        except Exception as e:
            logger.error(f"Erro ao processar OpenAPI: {e}")
            raise
            
    def _generate_markdown_docs(self) -> None:
        """Gera documentação markdown."""
        try:
            # Coleta endpoints
            endpoints = self._collect_endpoints()
            
            # Gera documentação por grupo
            for group, routes in endpoints.items():
                self._generate_group_docs(group, routes)
                
        except Exception as e:
            logger.error(f"Erro ao gerar documentação markdown: {e}")
            raise
            
    def _collect_endpoints(self) -> Dict[str, List[Dict]]:
        """Coleta endpoints da API.
        
        Returns:
            Dict com endpoints agrupados
        """
        endpoints = {}
        
        # Processa cada arquivo de rota
        for route_file in self.api_dir.glob('**/*.py'):
            if route_file.name.startswith('__'):
                continue
                
            # Carrega módulo
            spec = importlib.util.spec_from_file_location(
                route_file.stem,
                route_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Coleta rotas
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and hasattr(obj, 'route'):
                    route = {
                        'path': obj.route,
                        'method': obj.methods,
                        'name': name,
                        'doc': obj.__doc__,
                        'params': self._extract_params(obj),
                        'returns': self._extract_returns(obj)
                    }
                    
                    # Agrupa por prefixo
                    group = route_file.stem
                    if group not in endpoints:
                        endpoints[group] = []
                    endpoints[group].append(route)
                    
        return endpoints
        
    def _extract_params(self, func) -> List[Dict]:
        """Extrai parâmetros da função.
        
        Args:
            func: Função a analisar
            
        Returns:
            Lista de parâmetros
        """
        params = []
        sig = inspect.signature(func)
        
        for name, param in sig.parameters.items():
            if name == 'self':
                continue
                
            param_info = {
                'name': name,
                'type': str(param.annotation),
                'required': param.default == inspect.Parameter.empty
            }
            
            if param.default != inspect.Parameter.empty:
                param_info['default'] = param.default
                
            params.append(param_info)
            
        return params
        
    def _extract_returns(self, func) -> Dict:
        """Extrai informações de retorno da função.
        
        Args:
            func: Função a analisar
            
        Returns:
            Dict com informações de retorno
        """
        sig = inspect.signature(func)
        return_type = sig.return_annotation
        
        return {
            'type': str(return_type),
            'description': self._extract_return_doc(func)
        }
        
    def _extract_return_doc(self, func) -> str:
        """Extrai documentação de retorno da função.
        
        Args:
            func: Função a analisar
            
        Returns:
            String com documentação
        """
        if not func.__doc__:
            return ''
            
        # Procura seção Returns
        doc = func.__doc__
        match = re.search(r'Returns:\string_data*(.*?)(?:\n\string_data*\n|\Z)', doc, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        return ''
        
    def _generate_group_docs(self, group: str, routes: List[Dict]) -> None:
        """Gera documentação de grupo de endpoints.
        
        Args:
            group: Nome do grupo
            routes: Lista de rotas
        """
        try:
            # Gera documentação
            docs = [
                f"# API - {group.capitalize()}\n",
                f"Data: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}\n"
            ]
            
            # Adiciona endpoints
            for route in routes:
                docs.extend([
                    f"\n## {route['name']}\n",
                    f"**Path:** `{route['path']}`\n",
                    f"**Method:** {', '.join(route['method'])}\n",
                    "\n### Descrição\n",
                    route['doc'] or "Sem descrição",
                    "\n### Parâmetros\n"
                ])
                
                if route['params']:
                    docs.append("| Nome | Tipo | Obrigatório | Default |")
                    docs.append("|------|------|-------------|---------|")
                    
                    for param in route['params']:
                        docs.append(
                            f"| {param['name']} | {param['type']} | "
                            f"{'Sim' if param['required'] else 'Não'} | "
                            f"{param.get('default', '-')} |"
                        )
                else:
                    docs.append("Nenhum parâmetro")
                    
                docs.extend([
                    "\n### Retorno\n",
                    f"**Tipo:** {route['returns']['type']}\n",
                    "\n**Descrição:**\n",
                    route['returns']['description'] or "Sem descrição"
                ])
                
            # Salva documentação
            docs_file = self.docs_dir / 'api' / f'{group}.md'
            with open(docs_file, 'w') as f:
                f.write('\n'.join(docs))
                
            logger.info(f"Documentação do grupo {group} gerada em {docs_file}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar documentação do grupo {group}: {e}")
            raise
            
    def _generate_examples(self) -> None:
        """Gera exemplos de uso da API."""
        try:
            # Gera exemplos por grupo
            for group_file in (self.docs_dir / 'api').glob('*.md'):
                if group_file.name == 'index.md':
                    continue
                    
                self._generate_group_examples(group_file)
                
        except Exception as e:
            logger.error(f"Erro ao gerar exemplos: {e}")
            raise
            
    def _generate_group_examples(self, group_file: Path) -> None:
        """Gera exemplos para grupo de endpoints.
        
        Args:
            group_file: Arquivo do grupo
        """
        try:
            # Carrega documentação
            with open(group_file) as f:
                content = f.read()
                
            # Extrai endpoints
            endpoints = re.finditer(
                r'## (.*?)\n.*?Path: `(.*?)`\n.*?Method: (.*?)\n',
                content,
                re.DOTALL
            )
            
            # Gera exemplos
            examples = [
                f"# Exemplos - {group_file.stem.capitalize()}\n",
                f"Data: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}\n"
            ]
            
            for match in endpoints:
                name = match.group(1)
                path = match.group(2)
                method = match.group(3)
                
                examples.extend([
                    f"\n## {name}\n",
                    f"**Endpoint:** `{path}`\n",
                    f"**Método:** {method}\n",
                    "\n### Requisição\n",
                    "```bash",
                    f"curl -X {method} \\",
                    f"  '{path}' \\",
                    "  -H 'Content-Type: application/json' \\",
                    "  -data '{",
                    "    // Dados da requisição",
                    "  }'"
                    "```",
                    "\n### Resposta\n",
                    "```json",
                    "{",
                    "  // Dados da resposta",
                    "}",
                    "```"
                ])
                
            # Salva exemplos
            examples_file = self.docs_dir / 'api' / f'examples_{group_file.stem}.md'
            with open(examples_file, 'w') as f:
                f.write('\n'.join(examples))
                
            logger.info(f"Exemplos do grupo {group_file.stem} gerados em {examples_file}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar exemplos do grupo {group_file.stem}: {e}")
            raise
            
    def _update_indexes(self) -> None:
        """Atualiza índices da documentação da API."""
        try:
            # Gera sumário
            summary = [
                "# Documentação da API\n",
                f"Data: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}\n",
                "\n## Endpoints\n"
            ]
            
            # Adiciona grupos
            for group_file in (self.docs_dir / 'api').glob('*.md'):
                if group_file.name == 'index.md':
                    continue
                    
                group_name = group_file.stem.capitalize()
                summary.append(f"- [{group_name}]({group_file.name})")
                
            # Adiciona exemplos
            summary.extend([
                "\n## Exemplos\n"
            ])
            
            for examples_file in (self.docs_dir / 'api').glob('examples_*.md'):
                group_name = examples_file.stem.replace('examples_', '').capitalize()
                summary.append(f"- [{group_name}]({examples_file.name})")
                
            # Adiciona referência
            summary.extend([
                "\n## Referência\n",
                "- [OpenAPI](openapi.json)",
                "- [HTML](api.html)"
            ])
            
            # Salva sumário
            index_file = self.docs_dir / 'api' / 'index.md'
            with open(index_file, 'w') as f:
                f.write('\n'.join(summary))
                
            logger.info(f"Índice da API atualizado em {index_file}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar índices: {e}")
            raise

def main():
    """Função principal."""
    try:
        # Obtém diretório raiz do projeto
        project_root = os.getenv('PROJECT_ROOT', os.getcwd())
        
        # Inicializa gerador
        generator = APIDocumentationGenerator(project_root)
        
        # Gera documentação
        generator.generate_api_docs()
        
    except Exception as e:
        logger.error(f"Erro na execução do script: {e}")
        exit(1)

if __name__ == '__main__':
    main() 
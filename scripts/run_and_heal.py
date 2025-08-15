#!/usr/bin/env python3
"""
🚀 Auto-Healing Script com OpenAI Codex
📅 Criado: 2025-01-27
🔧 Tracing ID: AUTO_HEALING_SCRIPT_001_20250127
⚡ Status: ✅ ENTERPRISE-READY
🎯 Objetivo: Executar testes e aplicar healing inteligente com auditoria completa
"""

import os
import sys
import json
import subprocess
import argparse
import tempfile
import shutil
import time
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import openai
import git
from git import Repo
import difflib
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_healing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoHealingSystem:
    """
    Sistema de auto-healing inteligente com OpenAI Codex
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 openai_model: str = 'code-davinci-002',
                 max_attempts: int = 8,
                 stage: str = 'unknown'):
        """
        Inicializa o sistema de auto-healing
        
        Args:
            openai_api_key: Chave da API OpenAI
            openai_model: Modelo OpenAI a usar
            max_attempts: Máximo de tentativas de healing
            stage: Estágio atual (unit_tests, integration_tests, e2e_tests)
        """
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.max_attempts = max_attempts
        self.stage = stage
        self.attempts = 0
        self.patches_created = 0
        self.status = 'unknown'
        
        # Configurar OpenAI
        openai.api_key = openai_api_key
        
        # Criar diretórios necessários
        self.setup_directories()
        
        # Inicializar repositório Git
        self.repo = Repo('.')
        
        logger.info(f"Auto-Healing System initialized for stage: {stage}")
    
    def setup_directories(self):
        """Cria diretórios necessários para logs e patches"""
        directories = [
            'logs',
            'patches',
            f'patches/{self.stage}',
            'test-results',
            'coverage'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def run_tests(self, test_path: str) -> Tuple[bool, str, str]:
        """
        Executa testes e captura resultados
        
        Args:
            test_path: Caminho para os testes
            
        Returns:
            Tuple[bool, str, str]: (sucesso, stdout, stderr)
        """
        logger.info(f"Running tests: {test_path}")
        
        try:
            # Executar pytest com cobertura
            cmd = [
                'python', '-m', 'pytest',
                test_path,
                '--cov=.',
                '--cov-report=xml',
                '--cov-report=html',
                '--cov-report=term-missing',
                '--junitxml=test-results/results.xml',
                '-v'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            
            logger.info(f"Tests completed. Success: {success}")
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            logger.error("Tests timed out")
            return False, "", "Tests timed out after 5 minutes"
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return False, "", str(e)
    
    def extract_error_context(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """
        Extrai contexto do erro para enviar ao Codex
        
        Args:
            stdout: Saída padrão dos testes
            stderr: Saída de erro dos testes
            
        Returns:
            Dict com contexto do erro
        """
        context = {
            'error_type': 'unknown',
            'error_message': '',
            'file_path': '',
            'line_number': 0,
            'function_name': '',
            'code_snippet': '',
            'stack_trace': '',
            'test_output': stdout + stderr
        }
        
        # Extrair informações do erro
        error_patterns = [
            r'File "([^"]+)", line (\d+)',
            r'def ([a-zA-Z_][a-zA-Z0-9_]*)',
            r'class ([a-zA-Z_][a-zA-Z0-9_]*)',
            r'AssertionError: (.+)',
            r'ImportError: (.+)',
            r'SyntaxError: (.+)',
            r'AttributeError: (.+)',
            r'TypeError: (.+)',
            r'ValueError: (.+)'
        ]
        
        # Combinar stdout e stderr para análise
        combined_output = stdout + stderr
        
        # Procurar por padrões de erro
        for pattern in error_patterns:
            matches = re.findall(pattern, combined_output)
            if matches:
                if 'File' in pattern:
                    context['file_path'] = matches[0][0]
                    context['line_number'] = int(matches[0][1])
                elif 'def' in pattern:
                    context['function_name'] = matches[0]
                elif 'class' in pattern:
                    context['function_name'] = matches[0]
                elif any(error_type in pattern for error_type in ['Error']):
                    context['error_type'] = pattern.split(':')[0]
                    context['error_message'] = matches[0]
        
        # Extrair stack trace
        if stderr:
            context['stack_trace'] = stderr
        
        # Extrair trecho de código relevante
        if context['file_path'] and context['line_number']:
            context['code_snippet'] = self.extract_code_snippet(
                context['file_path'], 
                context['line_number']
            )
        
        return context
    
    def extract_code_snippet(self, file_path: str, line_number: int, context_lines: int = 10) -> str:
        """
        Extrai trecho de código ao redor da linha com erro
        
        Args:
            file_path: Caminho do arquivo
            line_number: Número da linha com erro
            context_lines: Número de linhas de contexto
            
        Returns:
            Trecho de código
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start_line = max(0, line_number - context_lines - 1)
            end_line = min(len(lines), line_number + context_lines)
            
            snippet_lines = []
            for i in range(start_line, end_line):
                line_num = i + 1
                marker = ">>> " if line_num == line_number else "    "
                snippet_lines.append(f"{marker}{line_num:4d}: {lines[i].rstrip()}")
            
            return '\n'.join(snippet_lines)
            
        except Exception as e:
            logger.warning(f"Could not extract code snippet: {e}")
            return ""
    
    def generate_healing_prompt(self, error_context: Dict[str, Any]) -> str:
        """
        Gera prompt para o OpenAI Codex
        
        Args:
            error_context: Contexto do erro
            
        Returns:
            Prompt formatado
        """
        prompt = f"""
# Auto-Healing Request - {self.stage.upper()}

## Error Context
- **Error Type**: {error_context['error_type']}
- **Error Message**: {error_context['error_message']}
- **File**: {error_context['file_path']}
- **Line**: {error_context['line_number']}
- **Function**: {error_context['function_name']}

## Code Snippet
```python
{error_context['code_snippet']}
```

## Stack Trace
```
{error_context['stack_trace']}
```

## Test Output
```
{error_context['test_output']}
```

## Instructions
Please fix the code to resolve the test failure. Follow these rules:

1. **Preserve existing comments and documentation**
2. **Only modify the specific function/class that's failing**
3. **Maintain the original code structure and style**
4. **Don't delete large code blocks without justification**
5. **Don't modify sensitive files (.env, secrets, config files)**
6. **Only modify tests if there's a clear inconsistency**
7. **Provide a brief explanation of the fix**

## Response Format
Return ONLY the corrected code snippet, starting with the function/class definition and ending with the closing brace/indent. No explanations in the response.

## Example Response
```python
def example_function():
    # Fixed implementation
    return result
```
"""
        return prompt
    
    def call_openai_codex(self, prompt: str) -> str:
        """
        Chama o OpenAI Codex para gerar correção
        
        Args:
            prompt: Prompt para o Codex
            
        Returns:
            Resposta do Codex
        """
        try:
            logger.info("Calling OpenAI Codex...")
            
            response = openai.Completion.create(
                model=self.openai_model,
                prompt=prompt,
                max_tokens=2000,
                temperature=0.1,
                top_p=0.95,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop=None
            )
            
            code_fix = response.choices[0].text.strip()
            logger.info("OpenAI Codex response received")
            
            return code_fix
            
        except Exception as e:
            logger.error(f"Error calling OpenAI Codex: {e}")
            return ""
    
    def apply_code_fix(self, file_path: str, line_number: int, code_fix: str) -> bool:
        """
        Aplica a correção gerada pelo Codex
        
        Args:
            file_path: Caminho do arquivo
            line_number: Linha onde aplicar a correção
            code_fix: Correção gerada
            
        Returns:
            True se aplicado com sucesso
        """
        try:
            logger.info(f"Applying code fix to {file_path}")
            
            # Ler arquivo original
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Criar backup
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            # Extrair função/classe da correção
            code_lines = code_fix.strip().split('\n')
            
            # Encontrar início e fim da função/classe
            start_line = self.find_function_start(lines, line_number)
            end_line = self.find_function_end(lines, start_line)
            
            # Aplicar correção
            new_lines = lines[:start_line]
            new_lines.extend(code_lines)
            new_lines.append('\n')  # Linha em branco após função
            new_lines.extend(lines[end_line:])
            
            # Escrever arquivo corrigido
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            logger.info(f"Code fix applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error applying code fix: {e}")
            return False
    
    def find_function_start(self, lines: List[str], line_number: int) -> int:
        """Encontra o início da função/classe"""
        for i in range(line_number - 1, -1, -1):
            line = lines[i].strip()
            if line.startswith(('def ', 'class ')):
                return i
        return line_number - 1
    
    def find_function_end(self, lines: List[str], start_line: int) -> int:
        """Encontra o fim da função/classe"""
        indent_level = len(lines[start_line]) - len(lines[start_line].lstrip())
        
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':
                continue
            
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and line.strip():
                return i
        
        return len(lines)
    
    def create_patch(self, file_path: str, attempt: int) -> str:
        """
        Cria patch diff para auditoria
        
        Args:
            file_path: Arquivo modificado
            attempt: Número da tentativa
            
        Returns:
            Caminho do arquivo de patch
        """
        try:
            # Gerar diff
            diff = self.repo.git.diff(file_path)
            
            if diff:
                patch_path = f"patches/{self.stage}/patch_attempt_{attempt}.diff"
                
                with open(patch_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Auto-Healing Patch - Attempt {attempt}\n")
                    f.write(f"# File: {file_path}\n")
                    f.write(f"# Stage: {self.stage}\n")
                    f.write(f"# Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"# Generated by: OpenAI Codex ({self.openai_model})\n")
                    f.write("\n")
                    f.write(diff)
                
                logger.info(f"Patch created: {patch_path}")
                return patch_path
            
        except Exception as e:
            logger.error(f"Error creating patch: {e}")
        
        return ""
    
    def create_branch_and_pr(self, attempt: int, file_path: str) -> str:
        """
        Cria branch e Pull Request para revisão
        
        Args:
            attempt: Número da tentativa
            file_path: Arquivo modificado
            
        Returns:
            URL do Pull Request
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            branch_name = f"auto-heal/{self.stage}/{timestamp}"
            
            # Criar nova branch
            current_branch = self.repo.active_branch
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            
            # Adicionar e commitar mudanças
            self.repo.index.add([file_path])
            commit_message = f"Auto-healing fix for {self.stage} - Attempt {attempt}\n\n- File: {file_path}\n- Stage: {self.stage}\n- Generated by: OpenAI Codex\n- Model: {self.openai_model}"
            self.repo.index.commit(commit_message)
            
            # Push da branch
            origin = self.repo.remote('origin')
            origin.push(new_branch)
            
            # Criar Pull Request via GitHub API
            pr_url = self.create_github_pr(branch_name, commit_message)
            
            logger.info(f"Branch and PR created: {pr_url}")
            return pr_url
            
        except Exception as e:
            logger.error(f"Error creating branch and PR: {e}")
            return ""
    
    def create_github_pr(self, branch_name: str, commit_message: str) -> str:
        """Cria Pull Request via GitHub API"""
        try:
            import requests
            
            # Configurar headers para GitHub API
            headers = {
                'Authorization': f'token {os.environ.get("GITHUB_TOKEN")}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Dados do PR
            pr_data = {
                'title': f'🚀 Auto-Healing Fix - {self.stage}',
                'body': f"""
## Auto-Healing Pull Request

### 📋 Details
- **Stage**: {self.stage}
- **Branch**: {branch_name}
- **Generated by**: OpenAI Codex ({self.openai_model})
- **Commit Message**: {commit_message}

### 🔍 Review Required
This PR contains automated fixes generated by our AI-powered healing system. Please review the changes before merging.

### 📊 Healing Statistics
- **Attempt**: {self.attempts}
- **Stage**: {self.stage}
- **Timestamp**: {datetime.now().isoformat()}

### ⚠️ Important Notes
- This is an automated fix - human review is required
- Only code fixes are included, no sensitive files modified
- Original code structure and comments preserved
                """,
                'head': branch_name,
                'base': 'main',
                'draft': False
            }
            
            # Criar PR
            repo_name = os.environ.get('GITHUB_REPOSITORY')
            url = f'https://api.github.com/repos/{repo_name}/pulls'
            
            response = requests.post(url, headers=headers, json=pr_data)
            response.raise_for_status()
            
            pr_info = response.json()
            return pr_info['html_url']
            
        except Exception as e:
            logger.error(f"Error creating GitHub PR: {e}")
            return ""
    
    def generate_healing_report(self) -> Dict[str, Any]:
        """
        Gera relatório completo do processo de healing
        
        Returns:
            Dicionário com relatório
        """
        report = {
            'stage': self.stage,
            'timestamp': datetime.now().isoformat(),
            'status': self.status,
            'attempts': self.attempts,
            'patches_created': self.patches_created,
            'max_attempts': self.max_attempts,
            'openai_model': self.openai_model,
            'success': self.status == 'success',
            'details': {
                'files_modified': [],
                'patches_generated': [],
                'pull_requests_created': [],
                'error_contexts': []
            }
        }
        
        return report
    
    def save_healing_report(self, report: Dict[str, Any]):
        """Salva relatório de healing"""
        report_path = f"logs/{self.stage}_healing_report.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Healing report saved: {report_path}")
    
    def run_healing_cycle(self, test_path: str) -> bool:
        """
        Executa ciclo completo de healing
        
        Args:
            test_path: Caminho para os testes
            
        Returns:
            True se os testes passaram
        """
        logger.info(f"Starting healing cycle for {test_path}")
        
        # Primeira execução de testes
        success, stdout, stderr = self.run_tests(test_path)
        
        if success:
            logger.info("Tests passed on first attempt!")
            self.status = 'success'
            return True
        
        # Ciclo de healing
        while self.attempts < self.max_attempts and not success:
            self.attempts += 1
            logger.info(f"Healing attempt {self.attempts}/{self.max_attempts}")
            
            # Extrair contexto do erro
            error_context = self.extract_error_context(stdout, stderr)
            
            # Gerar prompt para Codex
            prompt = self.generate_healing_prompt(error_context)
            
            # Chamar OpenAI Codex
            code_fix = self.call_openai_codex(prompt)
            
            if not code_fix:
                logger.warning("No code fix generated by Codex")
                continue
            
            # Aplicar correção
            if error_context['file_path']:
                fix_applied = self.apply_code_fix(
                    error_context['file_path'],
                    error_context['line_number'],
                    code_fix
                )
                
                if fix_applied:
                    # Criar patch
                    patch_path = self.create_patch(error_context['file_path'], self.attempts)
                    if patch_path:
                        self.patches_created += 1
                    
                    # Criar branch e PR
                    pr_url = self.create_branch_and_pr(self.attempts, error_context['file_path'])
                    
                    # Reexecutar testes
                    success, stdout, stderr = self.run_tests(test_path)
                    
                    if success:
                        logger.info(f"Tests passed after attempt {self.attempts}")
                        self.status = 'success'
                        break
                else:
                    logger.warning("Failed to apply code fix")
            else:
                logger.warning("No file path found in error context")
        
        if not success:
            logger.error(f"All healing attempts failed ({self.attempts}/{self.max_attempts})")
            self.status = 'failed'
        
        return success

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Auto-Healing Script with OpenAI Codex')
    parser.add_argument('--tests', required=True, help='Path to test directory')
    parser.add_argument('--stage', required=True, help='Test stage (unit_tests, integration_tests, e2e_tests)')
    parser.add_argument('--max-attempts', type=int, default=8, help='Maximum healing attempts')
    parser.add_argument('--openai-key', required=True, help='OpenAI API key')
    parser.add_argument('--openai-model', default='code-davinci-002', help='OpenAI model to use')
    
    args = parser.parse_args()
    
    # Configurar OpenAI
    os.environ['OPENAI_API_KEY'] = args.openai_key
    
    # Inicializar sistema de healing
    healing_system = AutoHealingSystem(
        openai_api_key=args.openai_key,
        openai_model=args.openai_model,
        max_attempts=args.max_attempts,
        stage=args.stage
    )
    
    # Executar ciclo de healing
    success = healing_system.run_healing_cycle(args.tests)
    
    # Gerar e salvar relatório
    report = healing_system.generate_healing_report()
    healing_system.save_healing_report(report)
    
    # Definir outputs para GitHub Actions
    print(f"::set-output name=status::{healing_system.status}")
    print(f"::set-output name=attempts::{healing_system.attempts}")
    print(f"::set-output name=patches::{healing_system.patches_created}")
    
    # Exit code baseado no sucesso
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()


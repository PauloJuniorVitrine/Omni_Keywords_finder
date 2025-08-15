#!/usr/bin/env python3
"""
🎯 Script de Refatoração de Código Duplicado
📋 Objetivo: Identificar e refatorar código duplicado no projeto
🔧 Tracing ID: REFACTOR_DUPLICATE_20250127_001
📅 Data: 2025-01-27
"""

import os
import sys
import json
import ast
import hashlib
import logging
import re
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
import difflib

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/refactor_duplicate.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DuplicateBlock:
    """Representa um bloco de código duplicado"""
    content: str
    hash: str
    locations: List[Tuple[str, int, int]]  # (file, start_line, end_line)
    similarity_score: float
    refactored: bool = False
    suggested_name: str = ""

@dataclass
class RefactorSuggestion:
    """Sugestão de refatoração"""
    duplicate_block: DuplicateBlock
    refactor_type: str  # 'function', 'class', 'module', 'constant'
    suggested_name: str
    estimated_impact: str  # 'low', 'medium', 'high'
    complexity: str  # 'simple', 'moderate', 'complex'
    description: str

class DuplicateCodeAnalyzer:
    """Analisador de código duplicado"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.duplicates: List[DuplicateBlock] = []
        self.file_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx'}
        self.ignore_patterns = {
            'node_modules', '__pycache__', '.git', 'venv', 'env',
            'build', 'dist', 'coverage', 'logs', 'uploads'
        }
        self.min_block_size = 3  # linhas mínimas para considerar duplicado
        self.similarity_threshold = 0.8
    
    def should_ignore_file(self, file_path: Path) -> bool:
        """Verifica se arquivo deve ser ignorado"""
        # Verificar extensão
        if file_path.suffix not in self.file_extensions:
            return True
        
        # Verificar padrões de ignorar
        for pattern in self.ignore_patterns:
            if pattern in str(file_path):
                return True
        
        return False
    
    def get_project_files(self) -> List[Path]:
        """Obtém lista de arquivos do projeto"""
        files = []
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file() and not self.should_ignore_file(file_path):
                files.append(file_path)
        
        logger.info(f"📁 Encontrados {len(files)} arquivos para análise")
        return files
    
    def normalize_code(self, code: str) -> str:
        """Normaliza código removendo espaços e comentários"""
        # Remover comentários de linha
        lines = []
        for line in code.split('\n'):
            # Remover comentários Python
            if '#' in line:
                line = line[:line.index('#')]
            # Remover comentários JavaScript/TypeScript
            if '//' in line:
                line = line[:line.index('//')]
            # Remover comentários CSS
            if '/*' in line and '*/' in line:
                line = re.sub(r'/\*.*?\*/', '', line)
            
            # Remover espaços em branco no final
            line = line.rstrip()
            if line.strip():  # Manter apenas linhas não vazias
                lines.append(line)
        
        return '\n'.join(lines)
    
    def extract_code_blocks(self, file_path: Path) -> List[Tuple[str, int, int]]:
        """Extrai blocos de código de um arquivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"⚠️ Erro ao ler {file_path}: {e}")
            return []
        
        lines = content.split('\n')
        blocks = []
        
        # Extrair blocos por função/classe
        current_block = []
        current_start = 1
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Detectar início de função/classe
            if (stripped.startswith('def ') or 
                stripped.startswith('class ') or
                stripped.startswith('async def ') or
                stripped.startswith('function ') or
                stripped.startswith('const ') or
                stripped.startswith('let ') or
                stripped.startswith('var ')):
                
                # Salvar bloco anterior se existir
                if len(current_block) >= self.min_block_size:
                    block_content = '\n'.join(current_block)
                    blocks.append((block_content, current_start, i - 1))
                
                # Iniciar novo bloco
                current_block = [line]
                current_start = i
            else:
                current_block.append(line)
        
        # Salvar último bloco
        if len(current_block) >= self.min_block_size:
            block_content = '\n'.join(current_block)
            blocks.append((block_content, current_start, len(lines)))
        
        return blocks
    
    def calculate_similarity(self, block1: str, block2: str) -> float:
        """Calcula similaridade entre dois blocos de código"""
        normalized1 = self.normalize_code(block1)
        normalized2 = self.normalize_code(block2)
        
        if not normalized1 or not normalized2:
            return 0.0
        
        # Usar difflib para calcular similaridade
        similarity = difflib.SequenceMatcher(None, normalized1, normalized2).ratio()
        return similarity
    
    def find_duplicates(self) -> List[DuplicateBlock]:
        """Encontra código duplicado no projeto"""
        files = self.get_project_files()
        all_blocks = []
        
        # Extrair blocos de todos os arquivos
        for file_path in files:
            blocks = self.extract_code_blocks(file_path)
            for block_content, start_line, end_line in blocks:
                normalized = self.normalize_code(block_content)
                if len(normalized.split('\n')) >= self.min_block_size:
                    block_hash = hashlib.md5(normalized.encode()).hexdigest()
                    all_blocks.append({
                        'content': block_content,
                        'normalized': normalized,
                        'hash': block_hash,
                        'file': str(file_path),
                        'start_line': start_line,
                        'end_line': end_line
                    })
        
        logger.info(f"🔍 Analisando {len(all_blocks)} blocos de código")
        
        # Agrupar blocos similares
        hash_groups = defaultdict(list)
        for block in all_blocks:
            hash_groups[block['hash']].append(block)
        
        # Encontrar duplicatas
        duplicates = []
        for block_hash, blocks in hash_groups.items():
            if len(blocks) > 1:
                # Verificar similaridade entre blocos do mesmo hash
                for i, block1 in enumerate(blocks):
                    for j, block2 in enumerate(blocks[i+1:], i+1):
                        similarity = self.calculate_similarity(
                            block1['normalized'], 
                            block2['normalized']
                        )
                        
                        if similarity >= self.similarity_threshold:
                            locations = [
                                (block1['file'], block1['start_line'], block1['end_line']),
                                (block2['file'], block2['start_line'], block2['end_line'])
                            ]
                            
                            duplicate = DuplicateBlock(
                                content=block1['content'],
                                hash=block_hash,
                                locations=locations,
                                similarity_score=similarity
                            )
                            duplicates.append(duplicate)
        
        logger.info(f"🎯 Encontradas {len(duplicates)} duplicatas")
        return duplicates
    
    def suggest_refactor_name(self, content: str) -> str:
        """Sugere nome para função/classe refatorada"""
        lines = content.split('\n')
        
        # Procurar por definições de função/classe
        for line in lines:
            line = line.strip()
            
            # Python
            if line.startswith('def '):
                func_name = line[4:].split('(')[0].strip()
                return f"extract_{func_name}_function"
            elif line.startswith('class '):
                class_name = line[6:].split('(')[0].split(':')[0].strip()
                return f"extract_{class_name}_class"
            
            # JavaScript/TypeScript
            elif line.startswith('function '):
                func_name = line[9:].split('(')[0].strip()
                return f"extract_{func_name}_function"
            elif line.startswith('const ') and '=' in line:
                const_name = line[6:].split('=')[0].strip()
                return f"extract_{const_name}_constant"
        
        # Nome genérico baseado no conteúdo
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"extract_duplicate_block_{content_hash}"

class CodeRefactorer:
    """Refatorador de código"""
    
    def __init__(self, analyzer: DuplicateCodeAnalyzer):
        self.analyzer = analyzer
        self.refactored_files = set()
    
    def generate_refactor_suggestions(self, duplicates: List[DuplicateBlock]) -> List[RefactorSuggestion]:
        """Gera sugestões de refatoração"""
        suggestions = []
        
        for duplicate in duplicates:
            content = duplicate.content
            lines = content.split('\n')
            
            # Determinar tipo de refatoração
            refactor_type = self._determine_refactor_type(content)
            suggested_name = self.analyzer.suggest_refactor_name(content)
            
            # Calcular impacto estimado
            impact = self._calculate_impact(duplicate)
            complexity = self._calculate_complexity(content)
            
            # Gerar descrição
            description = self._generate_description(duplicate, refactor_type)
            
            suggestion = RefactorSuggestion(
                duplicate_block=duplicate,
                refactor_type=refactor_type,
                suggested_name=suggested_name,
                estimated_impact=impact,
                complexity=complexity,
                description=description
            )
            
            suggestions.append(suggestion)
        
        return suggestions
    
    def _determine_refactor_type(self, content: str) -> str:
        """Determina tipo de refatoração baseado no conteúdo"""
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('class '):
                return 'class'
            elif line.startswith('def ') or line.startswith('async def '):
                return 'function'
            elif line.startswith('function ') or line.startswith('const '):
                return 'function'
            elif line.startswith('import ') or line.startswith('from '):
                return 'module'
        
        # Verificar se parece ser uma constante
        if len(lines) <= 3 and all('=' in line for line in lines if line.strip()):
            return 'constant'
        
        return 'function'  # Padrão
    
    def _calculate_impact(self, duplicate: DuplicateBlock) -> str:
        """Calcula impacto estimado da refatoração"""
        num_locations = len(duplicate.locations)
        
        if num_locations <= 2:
            return 'low'
        elif num_locations <= 5:
            return 'medium'
        else:
            return 'high'
    
    def _calculate_complexity(self, content: str) -> str:
        """Calcula complexidade do código"""
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if len(non_empty_lines) <= 10:
            return 'simple'
        elif len(non_empty_lines) <= 30:
            return 'moderate'
        else:
            return 'complex'
    
    def _generate_description(self, duplicate: DuplicateBlock, refactor_type: str) -> str:
        """Gera descrição da sugestão de refatoração"""
        num_locations = len(duplicate.locations)
        files = set(loc[0] for loc in duplicate.locations)
        
        return (
            f"Refatorar {refactor_type} duplicado encontrado em {num_locations} "
            f"localizações ({len(files)} arquivos). Similaridade: {duplicate.similarity_score:.1%}"
        )
    
    def create_refactored_function(self, suggestion: RefactorSuggestion) -> str:
        """Cria função refatorada"""
        content = suggestion.duplicate_block.content
        lines = content.split('\n')
        
        # Identificar parâmetros
        params = self._extract_parameters(content)
        
        # Criar função refatorada
        refactored_code = f"""
def {suggestion.suggested_name}({', '.join(params)}):
    \"\"\"
    {suggestion.description}
    
    Args:
        {chr(10).join(f'{param}: Descrição do parâmetro {param}' for param in params)}
    
    Returns:
        Resultado da operação
    \"\"\"
    # TODO: Implementar lógica refatorada
    # Código original:
{chr(10).join(f'    # {line}' for line in lines)}
    
    pass
"""
        
        return refactored_code
    
    def _extract_parameters(self, content: str) -> List[str]:
        """Extrai parâmetros do código"""
        # Implementação simplificada - em produção seria mais sofisticada
        params = []
        
        # Procurar por variáveis que podem ser parâmetros
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Python: variáveis que parecem ser parâmetros
            if '=' in line and not line.startswith('def ') and not line.startswith('class '):
                var_name = line.split('=')[0].strip()
                if var_name and var_name not in params:
                    params.append(var_name)
        
        return params[:5]  # Limitar a 5 parâmetros

def create_refactor_report(duplicates: List[DuplicateBlock], suggestions: List[RefactorSuggestion]):
    """Cria relatório de refatoração"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_duplicates": len(duplicates),
            "total_suggestions": len(suggestions),
            "high_impact": len([s for s in suggestions if s.estimated_impact == 'high']),
            "medium_impact": len([s for s in suggestions if s.estimated_impact == 'medium']),
            "low_impact": len([s for s in suggestions if s.estimated_impact == 'low'])
        },
        "duplicates": [
            {
                "hash": d.hash,
                "similarity_score": d.similarity_score,
                "locations": d.locations,
                "content_preview": d.content[:200] + "..." if len(d.content) > 200 else d.content
            }
            for d in duplicates
        ],
        "suggestions": [
            {
                "refactor_type": s.refactor_type,
                "suggested_name": s.suggested_name,
                "estimated_impact": s.estimated_impact,
                "complexity": s.complexity,
                "description": s.description
            }
            for s in suggestions
        ]
    }
    
    report_path = "docs/RELATORIO_REFATORACAO_DUPLICATAS.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Relatório de Refatoração de Código Duplicado\n\n")
        f.write(f"**Data**: {report['timestamp']}\n")
        f.write(f"**Total de Duplicatas**: {report['summary']['total_duplicates']}\n")
        f.write(f"**Sugestões de Refatoração**: {report['summary']['total_suggestions']}\n\n")
        
        f.write("## Resumo por Impacto\n")
        f.write(f"- **Alto Impacto**: {report['summary']['high_impact']}\n")
        f.write(f"- **Médio Impacto**: {report['summary']['medium_impact']}\n")
        f.write(f"- **Baixo Impacto**: {report['summary']['low_impact']}\n\n")
        
        f.write("## Sugestões de Refatoração\n\n")
        for i, suggestion in enumerate(report['suggestions'], 1):
            f.write(f"### {i}. {suggestion['suggested_name']}\n")
            f.write(f"- **Tipo**: {suggestion['refactor_type']}\n")
            f.write(f"- **Impacto**: {suggestion['estimated_impact']}\n")
            f.write(f"- **Complexidade**: {suggestion['complexity']}\n")
            f.write(f"- **Descrição**: {suggestion['description']}\n\n")
    
    logger.info(f"✅ Relatório salvo em {report_path}")
    return report_path

def create_refactor_tests():
    """Cria testes para o sistema de refatoração"""
    test_code = '''
import pytest
from unittest.mock import Mock, patch
from scripts.refactor_duplicate_code import (
    DuplicateCodeAnalyzer, 
    CodeRefactorer, 
    DuplicateBlock, 
    RefactorSuggestion
)

class TestDuplicateCodeAnalyzer:
    """Testes para o analisador de código duplicado"""
    
    @pytest.fixture
    def analyzer(self, tmp_path):
        return DuplicateCodeAnalyzer(str(tmp_path))
    
    def test_should_ignore_file(self, analyzer):
        """Testa se arquivos são ignorados corretamente"""
        # Arquivo Python deve ser incluído
        assert not analyzer.should_ignore_file(analyzer.project_root / "test.py")
        
        # Arquivo de texto deve ser ignorado
        assert analyzer.should_ignore_file(analyzer.project_root / "test.txt")
        
        # Arquivo em node_modules deve ser ignorado
        assert analyzer.should_ignore_file(analyzer.project_root / "node_modules" / "test.js")
    
    def test_normalize_code(self, analyzer):
        """Testa normalização de código"""
        code = '''
def test_function():
    # Este é um comentário
    return "test"  # Outro comentário
        '''
        
        normalized = analyzer.normalize_code(code)
        assert "#" not in normalized
        assert "test_function" in normalized
    
    def test_calculate_similarity(self, analyzer):
        """Testa cálculo de similaridade"""
        code1 = "def test(): return True"
        code2 = "def test(): return True"
        code3 = "def other(): return False"
        
        # Códigos idênticos devem ter similaridade 1.0
        similarity1 = analyzer.calculate_similarity(code1, code2)
        assert similarity1 > 0.9
        
        # Códigos diferentes devem ter similaridade baixa
        similarity2 = analyzer.calculate_similarity(code1, code3)
        assert similarity2 < 0.5

class TestCodeRefactorer:
    """Testes para o refatorador de código"""
    
    @pytest.fixture
    def analyzer(self, tmp_path):
        return DuplicateCodeAnalyzer(str(tmp_path))
    
    @pytest.fixture
    def refactorer(self, analyzer):
        return CodeRefactorer(analyzer)
    
    def test_determine_refactor_type(self, refactorer):
        """Testa determinação do tipo de refatoração"""
        # Função Python
        python_func = "def test_function(): pass"
        assert refactorer._determine_refactor_type(python_func) == "function"
        
        # Classe Python
        python_class = "class TestClass: pass"
        assert refactorer._determine_refactor_type(python_class) == "class"
        
        # Função JavaScript
        js_func = "function testFunction() {}"
        assert refactorer._determine_refactor_type(js_func) == "function"
    
    def test_calculate_impact(self, refactorer):
        """Testa cálculo de impacto"""
        duplicate = DuplicateBlock(
            content="test",
            hash="123",
            locations=[("file1.py", 1, 5), ("file2.py", 10, 15)],
            similarity_score=0.9
        )
        
        impact = refactorer._calculate_impact(duplicate)
        assert impact == "low"
        
        # Muitas localizações = alto impacto
        duplicate.locations = [("file1.py", 1, 5)] * 10
        impact = refactorer._calculate_impact(duplicate)
        assert impact == "high"
    
    def test_calculate_complexity(self, refactorer):
        """Testa cálculo de complexidade"""
        simple_code = "def test(): pass"
        assert refactorer._calculate_complexity(simple_code) == "simple"
        
        complex_code = "\\n".join([f"line {i}" for i in range(50)])
        assert refactorer._calculate_complexity(complex_code) == "complex"
'''
    
    test_path = "tests/unit/test_refactor_duplicate.py"
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    logger.info(f"✅ Testes de refatoração criados em {test_path}")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando análise de código duplicado")
    
    try:
        # Inicializar analisador
        analyzer = DuplicateCodeAnalyzer(".")
        
        # Encontrar duplicatas
        duplicates = analyzer.find_duplicates()
        logger.info(f"🎯 Encontradas {len(duplicates)} duplicatas")
        
        # Gerar sugestões de refatoração
        refactorer = CodeRefactorer(analyzer)
        suggestions = refactorer.generate_refactor_suggestions(duplicates)
        logger.info(f"💡 Geradas {len(suggestions)} sugestões de refatoração")
        
        # Criar relatório
        report_path = create_refactor_report(duplicates, suggestions)
        logger.info(f"✅ Relatório criado: {report_path}")
        
        # Criar testes
        create_refactor_tests()
        logger.info("✅ Testes de refatoração criados")
        
        # Exemplo de refatoração
        if suggestions:
            example_suggestion = suggestions[0]
            refactored_code = refactorer.create_refactored_function(example_suggestion)
            
            example_path = "examples/refactored_function_example.py"
            os.makedirs(os.path.dirname(example_path), exist_ok=True)
            
            with open(example_path, 'w', encoding='utf-8') as f:
                f.write(f"# Exemplo de função refatorada\n")
                f.write(f"# Baseado na sugestão: {example_suggestion.suggested_name}\n\n")
                f.write(refactored_code)
            
            logger.info(f"✅ Exemplo de refatoração salvo em {example_path}")
        
        logger.info("✅ Análise de código duplicado concluída")
        
        # Estatísticas finais
        high_impact = len([s for s in suggestions if s.estimated_impact == 'high'])
        medium_impact = len([s for s in suggestions if s.estimated_impact == 'medium'])
        low_impact = len([s for s in suggestions if s.estimated_impact == 'low'])
        
        logger.info(f"📊 Estatísticas finais:")
        logger.info(f"   - Duplicatas encontradas: {len(duplicates)}")
        logger.info(f"   - Sugestões geradas: {len(suggestions)}")
        logger.info(f"   - Alto impacto: {high_impact}")
        logger.info(f"   - Médio impacto: {medium_impact}")
        logger.info(f"   - Baixo impacto: {low_impact}")
        
    except Exception as e:
        logger.error(f"❌ Erro na análise: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
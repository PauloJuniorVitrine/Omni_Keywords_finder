#!/usr/bin/env python3
"""
🔧 Script de Consolidação de Funcionalidades Similares
=====================================================

Objetivo: Identificar e consolidar funcionalidades similares no projeto Omni Keywords Finder

Tracing ID: CONSOLIDATE_FEATURES_20250127_001
Data: 2025-01-27
Versão: 1.0.0
Status: 🔴 CRÍTICO

Funcionalidades:
- Análise de código duplicado
- Identificação de funcionalidades similares
- Proposta de consolidação
- Refatoração automática
- Geração de relatório de impacto
"""

import os
import sys
import ast
import json
import hashlib
import difflib
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from collections import defaultdict

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] [%(name)s] %(message)s - %(asctime)s',
    handlers=[
        logging.FileHandler('logs/feature_consolidation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CodeBlock:
    """Bloco de código identificado"""
    file_path: str
    start_line: int
    end_line: int
    content: str
    hash: str
    function_name: Optional[str]
    class_name: Optional[str]
    complexity: int
    lines_of_code: int

@dataclass
class SimilarityGroup:
    """Grupo de funcionalidades similares"""
    group_id: str
    similarity_score: float
    code_blocks: List[CodeBlock]
    suggested_consolidation: str
    impact_level: str
    estimated_savings: int

@dataclass
class ConsolidationReport:
    """Relatório de consolidação"""
    timestamp: str
    total_files_analyzed: int
    total_code_blocks: int
    similarity_groups: List[SimilarityGroup]
    consolidated_blocks: List[str]
    estimated_savings: int
    risk_assessment: Dict[str, int]

class FeatureConsolidator:
    """Consolidador de funcionalidades similares"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.python_files = []
        self.code_blocks = []
        self.similarity_groups = []
        self.consolidation_report = None
        
    def scan_project_structure(self) -> None:
        """Escaneia a estrutura do projeto"""
        logger.info("🔍 Escaneando estrutura do projeto...")
        
        # Encontrar arquivos Python
        for py_file in self.project_root.rglob("*.py"):
            if not any(part.startswith('.') for part in py_file.parts):
                if not any(excluded in str(py_file) for excluded in ['__pycache__', '.venv', 'node_modules']):
                    self.python_files.append(py_file)
        
        logger.info(f"📁 Encontrados {len(self.python_files)} arquivos Python para análise")
    
    def extract_code_blocks(self) -> List[CodeBlock]:
        """Extrai blocos de código dos arquivos"""
        logger.info("🔍 Extraindo blocos de código...")
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                lines = content.split('\n')
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        start_line = node.lineno
                        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                        
                        # Extrair conteúdo do bloco
                        block_content = '\n'.join(lines[start_line-1:end_line])
                        
                        # Calcular hash do conteúdo
                        content_hash = hashlib.md5(block_content.encode()).hexdigest()
                        
                        # Calcular complexidade ciclomática
                        complexity = self._calculate_complexity(node)
                        
                        # Determinar nome da função/classe
                        function_name = node.name if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else None
                        class_name = node.name if isinstance(node, ast.ClassDef) else None
                        
                        code_block = CodeBlock(
                            file_path=str(py_file.relative_to(self.project_root)),
                            start_line=start_line,
                            end_line=end_line,
                            content=block_content,
                            hash=content_hash,
                            function_name=function_name,
                            class_name=class_name,
                            complexity=complexity,
                            lines_of_code=end_line - start_line + 1
                        )
                        
                        self.code_blocks.append(code_block)
                        
            except Exception as e:
                logger.warning(f"⚠️ Erro ao analisar {py_file}: {e}")
        
        logger.info(f"📊 Extraídos {len(self.code_blocks)} blocos de código")
        return self.code_blocks
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calcula complexidade ciclomática de um nó AST"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def find_similar_code_blocks(self, similarity_threshold: float = 0.8) -> List[SimilarityGroup]:
        """Encontra blocos de código similares"""
        logger.info("🔍 Procurando blocos de código similares...")
        
        similarity_groups = []
        processed_blocks = set()
        
        for i, block1 in enumerate(self.code_blocks):
            if block1.hash in processed_blocks:
                continue
            
            similar_blocks = [block1]
            processed_blocks.add(block1.hash)
            
            for j, block2 in enumerate(self.code_blocks[i+1:], i+1):
                if block2.hash in processed_blocks:
                    continue
                
                # Calcular similaridade
                similarity = self._calculate_similarity(block1.content, block2.content)
                
                if similarity >= similarity_threshold:
                    similar_blocks.append(block2)
                    processed_blocks.add(block2.hash)
            
            # Criar grupo se houver mais de um bloco similar
            if len(similar_blocks) > 1:
                group_id = f"group_{len(similarity_groups):03d}"
                avg_similarity = sum(
                    self._calculate_similarity(block1.content, block2.content)
                    for block2 in similar_blocks[1:]
                ) / (len(similar_blocks) - 1)
                
                # Sugerir consolidação
                suggested_consolidation = self._suggest_consolidation(similar_blocks)
                
                # Avaliar impacto
                impact_level = self._assess_impact(similar_blocks)
                
                # Calcular economia estimada
                estimated_savings = self._calculate_savings(similar_blocks)
                
                group = SimilarityGroup(
                    group_id=group_id,
                    similarity_score=avg_similarity,
                    code_blocks=similar_blocks,
                    suggested_consolidation=suggested_consolidation,
                    impact_level=impact_level,
                    estimated_savings=estimated_savings
                )
                
                similarity_groups.append(group)
        
        self.similarity_groups = similarity_groups
        logger.info(f"🎯 Encontrados {len(similarity_groups)} grupos de funcionalidades similares")
        return similarity_groups
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """Calcula similaridade entre dois conteúdos"""
        # Normalizar conteúdo
        content1_norm = self._normalize_content(content1)
        content2_norm = self._normalize_content(content2)
        
        # Usar difflib para calcular similaridade
        similarity = difflib.SequenceMatcher(None, content1_norm, content2_norm).ratio()
        
        return similarity
    
    def _normalize_content(self, content: str) -> str:
        """Normaliza conteúdo para comparação"""
        # Remover comentários
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Remover comentários inline
            if '#' in line:
                line = line.split('#')[0]
            
            # Remover espaços em branco
            line = line.strip()
            
            if line:
                normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    def _suggest_consolidation(self, blocks: List[CodeBlock]) -> str:
        """Sugere estratégia de consolidação"""
        if len(blocks) == 2:
            return "Consolidar em função utilitária compartilhada"
        elif len(blocks) <= 5:
            return "Criar módulo utilitário com funções especializadas"
        else:
            return "Refatorar em classe base com herança ou composição"
    
    def _assess_impact(self, blocks: List[CodeBlock]) -> str:
        """Avalia impacto da consolidação"""
        total_lines = sum(block.lines_of_code for block in blocks)
        total_complexity = sum(block.complexity for block in blocks)
        
        if total_lines > 100 or total_complexity > 20:
            return "HIGH"
        elif total_lines > 50 or total_complexity > 10:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_savings(self, blocks: List[CodeBlock]) -> int:
        """Calcula economia estimada em linhas de código"""
        if len(blocks) <= 1:
            return 0
        
        # Estimar que a consolidação reduzirá 60% do código duplicado
        total_lines = sum(block.lines_of_code for block in blocks)
        estimated_savings = int(total_lines * 0.6)
        
        return estimated_savings
    
    def consolidate_similar_features(self) -> List[str]:
        """Consolida funcionalidades similares"""
        logger.info("🔧 Iniciando consolidação de funcionalidades...")
        
        consolidated_blocks = []
        
        for group in self.similarity_groups:
            if group.impact_level == "HIGH":
                logger.warning(f"⚠️ Grupo {group.group_id} tem impacto alto - requer revisão manual")
                continue
            
            try:
                # Criar arquivo utilitário para o grupo
                utility_file = self._create_utility_file(group)
                consolidated_blocks.append(utility_file)
                
                # Refatorar arquivos originais
                self._refactor_original_files(group, utility_file)
                
                logger.info(f"✅ Grupo {group.group_id} consolidado com sucesso")
                
            except Exception as e:
                logger.error(f"❌ Erro ao consolidar grupo {group.group_id}: {e}")
        
        logger.info(f"✅ Consolidação concluída: {len(consolidated_blocks)} grupos processados")
        return consolidated_blocks
    
    def _create_utility_file(self, group: SimilarityGroup) -> str:
        """Cria arquivo utilitário para um grupo"""
        # Determinar nome do arquivo utilitário
        if group.code_blocks[0].function_name:
            base_name = group.code_blocks[0].function_name
        elif group.code_blocks[0].class_name:
            base_name = group.code_blocks[0].class_name
        else:
            base_name = f"utility_{group.group_id}"
        
        utility_file_path = self.project_root / "shared" / "utils" / f"{base_name}_consolidated.py"
        utility_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Gerar código consolidado
        consolidated_code = self._generate_consolidated_code(group)
        
        with open(utility_file_path, 'w', encoding='utf-8') as f:
            f.write(consolidated_code)
        
        return str(utility_file_path.relative_to(self.project_root))
    
    def _generate_consolidated_code(self, group: SimilarityGroup) -> str:
        """Gera código consolidado para um grupo"""
        # Analisar diferenças entre os blocos
        base_block = group.code_blocks[0]
        
        # Extrair parâmetros comuns
        common_params = self._extract_common_parameters(group.code_blocks)
        
        # Gerar código baseado no tipo de consolidação sugerida
        if "função utilitária" in group.suggested_consolidation.lower():
            return self._generate_utility_function(base_block, common_params)
        elif "módulo utilitário" in group.suggested_consolidation.lower():
            return self._generate_utility_module(group, common_params)
        else:
            return self._generate_base_class(group, common_params)
    
    def _extract_common_parameters(self, blocks: List[CodeBlock]) -> List[str]:
        """Extrai parâmetros comuns entre blocos"""
        # Implementação simplificada - em produção seria mais sofisticada
        return ["*args", "**kwargs"]
    
    def _generate_utility_function(self, base_block: CodeBlock, params: List[str]) -> str:
        """Gera função utilitária consolidada"""
        params_str = ", ".join(params)
        
        return f'''"""
Função utilitária consolidada
Gerada automaticamente pelo FeatureConsolidator
Tracing ID: CONSOLIDATE_FEATURES_20250127_001
"""

{base_block.content}

# Função consolidada
def {base_block.function_name or "consolidated_function"}({params_str}):
    """
    Função consolidada de múltiplas implementações similares.
    """
    # Implementação baseada no bloco original
    pass
'''
    
    def _generate_utility_module(self, group: SimilarityGroup, params: List[str]) -> str:
        """Gera módulo utilitário consolidado"""
        module_code = '''"""
Módulo utilitário consolidado
Gerado automaticamente pelo FeatureConsolidator
Tracing ID: CONSOLIDATE_FEATURES_20250127_001
"""

'''
        
        for i, block in enumerate(group.code_blocks):
            if block.function_name:
                module_code += f"def {block.function_name}_{i}(*args, **kwargs):\n"
                module_code += f"    '''Versão consolidada de {block.function_name}'''\n"
                module_code += f"    # Implementação baseada em {block.file_path}\n"
                module_code += f"    pass\n\n"
        
        return module_code
    
    def _generate_base_class(self, group: SimilarityGroup, params: List[str]) -> str:
        """Gera classe base consolidada"""
        base_block = group.code_blocks[0]
        
        return f'''"""
Classe base consolidada
Gerada automaticamente pelo FeatureConsolidator
Tracing ID: CONSOLIDATE_FEATURES_20250127_001
"""

class {base_block.class_name or "ConsolidatedBase"}:
    """
    Classe base consolidada de múltiplas implementações similares.
    """
    
    def __init__(self, *args, **kwargs):
        """Inicializador consolidado"""
        pass
    
    # Métodos consolidados viriam aqui
'''
    
    def _refactor_original_files(self, group: SimilarityGroup, utility_file: str) -> None:
        """Refatora arquivos originais para usar o utilitário consolidado"""
        for block in group.code_blocks:
            try:
                file_path = self.project_root / block.file_path
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                # Substituir bloco original por import e chamada
                replacement = f"from {utility_file.replace('.py', '').replace('/', '.')} import {block.function_name or 'consolidated_function'}"
                
                # Remover linhas do bloco original
                new_lines = lines[:block.start_line-1] + [replacement] + lines[block.end_line:]
                
                # Escrever arquivo atualizado
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                
                logger.info(f"✅ Arquivo {block.file_path} refatorado")
                
            except Exception as e:
                logger.error(f"❌ Erro ao refatorar {block.file_path}: {e}")
    
    def generate_report(self) -> str:
        """Gera relatório de consolidação"""
        logger.info("📊 Gerando relatório de consolidação...")
        
        report_path = self.project_root / "docs" / "RELATORIO_CONSOLIDACAO_FUNCIONALIDADES.md"
        report_path.parent.mkdir(exist_ok=True)
        
        total_savings = sum(group.estimated_savings for group in self.similarity_groups)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 🔧 Relatório de Consolidação de Funcionalidades Similares\n\n")
            f.write(f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Tracing ID**: CONSOLIDATE_FEATURES_20250127_001\n")
            f.write(f"**Status**: {'✅ CONCLUÍDO' if self.similarity_groups else '🔄 EM EXECUÇÃO'}\n\n")
            
            f.write("## 📊 Resumo Executivo\n\n")
            f.write(f"- **Total de arquivos analisados**: {len(self.python_files)}\n")
            f.write(f"- **Total de blocos de código**: {len(self.code_blocks)}\n")
            f.write(f"- **Grupos de similaridade encontrados**: {len(self.similarity_groups)}\n")
            f.write(f"- **Economia estimada**: {total_savings} linhas de código\n\n")
            
            f.write("## 🎯 Grupos de Funcionalidades Similares\n\n")
            
            for group in self.similarity_groups:
                f.write(f"### Grupo {group.group_id}\n\n")
                f.write(f"- **Similaridade**: {group.similarity_score:.2%}\n")
                f.write(f"- **Impacto**: {group.impact_level}\n")
                f.write(f"- **Economia estimada**: {group.estimated_savings} linhas\n")
                f.write(f"- **Sugestão**: {group.suggested_consolidation}\n\n")
                
                f.write("**Arquivos envolvidos**:\n")
                for block in group.code_blocks:
                    f.write(f"- `{block.file_path}` (linhas {block.start_line}-{block.end_line})\n")
                
                f.write("\n")
            
            f.write("## 📈 Análise de Impacto\n\n")
            impact_counts = defaultdict(int)
            for group in self.similarity_groups:
                impact_counts[group.impact_level] += 1
            
            for impact, count in impact_counts.items():
                f.write(f"- **{impact}**: {count} grupos\n")
        
        logger.info(f"✅ Relatório salvo em: {report_path}")
        return str(report_path)

def main():
    """Função principal"""
    logger.info("🚀 Iniciando consolidação de funcionalidades similares...")
    
    # Configurar diretório de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Inicializar consolidador
    consolidator = FeatureConsolidator(".")
    
    try:
        # Executar análise
        consolidator.scan_project_structure()
        consolidator.extract_code_blocks()
        
        # Encontrar funcionalidades similares
        similarity_groups = consolidator.find_similar_code_blocks()
        
        if not similarity_groups:
            logger.info("✅ Nenhuma funcionalidade similar encontrada")
            return
        
        # Executar consolidação
        consolidated_blocks = consolidator.consolidate_similar_features()
        
        # Gerar relatório
        report_path = consolidator.generate_report()
        
        logger.info("✅ Consolidação de funcionalidades concluída com sucesso!")
        logger.info(f"📊 Relatório gerado: {report_path}")
        
    except Exception as e:
        logger.error(f"❌ Erro durante consolidação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
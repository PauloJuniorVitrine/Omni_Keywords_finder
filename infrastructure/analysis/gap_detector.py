"""
Detector de Lacunas Semânticas e Estruturais
============================================

Sistema inteligente para detectar lacunas no código, funcionalidades faltantes
e oportunidades de melhoria baseado em análise semântica e estrutural.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 2.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import os
import re
import ast
import json
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging

# NLP Libraries
try:
    import spacy
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    logging.warning("NLP libraries not available. Using fallback analysis.")

from shared.logger import logger

class GapType(Enum):
    """Tipos de lacunas detectadas."""
    MISSING_IMPORT = "missing_import"
    MISSING_TEST = "missing_test"
    MISSING_DOCUMENTATION = "missing_documentation"
    MISSING_ERROR_HANDLING = "missing_error_handling"
    MISSING_VALIDATION = "missing_validation"
    MISSING_LOGGING = "missing_logging"
    MISSING_TYPE_HINTS = "missing_type_hints"
    DEAD_CODE = "dead_code"
    DUPLICATE_CODE = "duplicate_code"
    INCONSISTENT_NAMING = "inconsistent_naming"
    MISSING_CONFIG = "missing_config"
    MISSING_SECURITY = "missing_security"
    MISSING_PERFORMANCE = "missing_performance"
    MISSING_MONITORING = "missing_monitoring"

class GapSeverity(Enum):
    """Severidades de lacunas."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class GapDetection:
    """Detecção de lacuna."""
    gap_type: GapType
    severity: GapSeverity
    file_path: str
    line_number: Optional[int] = None
    description: str = ""
    suggestion: str = ""
    confidence: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GapAnalysisResult:
    """Resultado da análise de lacunas."""
    gaps: List[GapDetection]
    total_gaps: int
    critical_gaps: int
    high_gaps: int
    medium_gaps: int
    low_gaps: int
    info_gaps: int
    processing_time: float
    files_analyzed: int
    coverage_score: float
    quality_score: float
    metadata: Dict[str, Any]

class GapDetector:
    """
    Detector inteligente de lacunas no código.
    
    Funcionalidades:
    - Análise semântica de código
    - Detecção de funcionalidades faltantes
    - Identificação de dependências órfãs
    - Sugestões de melhorias
    - Análise de padrões de código
    """
    
    def __init__(
        self,
        project_root: str = ".",
        exclude_patterns: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None,
        enable_nlp: bool = True,
        confidence_threshold: float = 0.7
    ):
        """
        Inicializa o detector de lacunas.
        
        Args:
            project_root: Diretório raiz do projeto
            exclude_patterns: Padrões para excluir arquivos
            include_patterns: Padrões para incluir arquivos
            enable_nlp: Habilita análise NLP
            confidence_threshold: Threshold de confiança
        """
        self.project_root = Path(project_root)
        self.exclude_patterns = exclude_patterns or [
            r'__pycache__', r'\.git', r'\.venv', r'node_modules',
            r'\.pytest_cache', r'\.coverage', r'htmlcov', r'logs',
            r'backup_sistema_antigo', r'\.env', r'\.key'
        ]
        self.include_patterns = include_patterns or [r'\.py$']
        self.enable_nlp = enable_nlp and NLP_AVAILABLE
        self.confidence_threshold = confidence_threshold
        
        # Cache de análises
        self.analysis_cache = {}
        self.file_hashes = {}
        
        # Padrões de detecção
        self.detection_patterns = {
            'missing_import': [
                r'from\s+(\w+)\s+import\s+(\w+)',
                r'import\s+(\w+)',
                r'from\s+(\w+\.\w+)\s+import'
            ],
            'missing_error_handling': [
                r'try:',
                r'except\s+(\w+):',
                r'finally:',
                r'raise\s+(\w+)'
            ],
            'missing_validation': [
                r'assert\s+',
                r'if\s+.*:\s*raise',
                r'validate_',
                r'check_'
            ],
            'missing_logging': [
                r'logger\.',
                r'logging\.',
                r'log\.'
            ],
            'missing_type_hints': [
                r'def\s+\w+\s*\([^)]*\)\s*->\s*\w+:',
                r':\s*\w+\s*=',
                r':\s*List\[',
                r':\s*Dict\['
            ]
        }
        
        # Inicializar NLP se disponível
        if self.enable_nlp:
            try:
                self.nlp = spacy.load("pt_core_news_sm")
                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("NLP initialized for gap detection")
            except Exception as e:
                logger.error(f"Failed to initialize NLP: {e}")
                self.enable_nlp = False
        
        logger.info("GapDetector initialized successfully")
    
    def analyze_project(self) -> GapAnalysisResult:
        """
        Analisa todo o projeto em busca de lacunas.
        
        Returns:
            Resultado da análise de lacunas
        """
        start_time = time.time()
        
        # Encontrar arquivos para análise
        files_to_analyze = self._find_files_to_analyze()
        logger.info(f"Found {len(files_to_analyze)} files to analyze")
        
        # Analisar cada arquivo
        all_gaps = []
        files_analyzed = 0
        
        for file_path in files_to_analyze:
            try:
                file_gaps = self._analyze_file(file_path)
                all_gaps.extend(file_gaps)
                files_analyzed += 1
                
                if files_analyzed % 10 == 0:
                    logger.info(f"Analyzed {files_analyzed}/{len(files_to_analyze)} files")
                    
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
        
        # Análise semântica do projeto
        semantic_gaps = self._analyze_semantic_gaps(all_gaps)
        all_gaps.extend(semantic_gaps)
        
        # Análise de dependências
        dependency_gaps = self._analyze_dependency_gaps()
        all_gaps.extend(dependency_gaps)
        
        # Análise de estrutura
        structural_gaps = self._analyze_structural_gaps()
        all_gaps.extend(structural_gaps)
        
        # Calcular métricas
        processing_time = time.time() - start_time
        gap_counts = self._count_gaps_by_severity(all_gaps)
        coverage_score = self._calculate_coverage_score(files_analyzed, len(files_to_analyze))
        quality_score = self._calculate_quality_score(all_gaps)
        
        # Preparar metadados
        metadata = {
            'project_root': str(self.project_root),
            'analysis_timestamp': datetime.now().isoformat(),
            'nlp_enabled': self.enable_nlp,
            'confidence_threshold': self.confidence_threshold,
            'exclude_patterns': self.exclude_patterns,
            'include_patterns': self.include_patterns
        }
        
        result = GapAnalysisResult(
            gaps=all_gaps,
            total_gaps=len(all_gaps),
            critical_gaps=gap_counts.get(GapSeverity.CRITICAL, 0),
            high_gaps=gap_counts.get(GapSeverity.HIGH, 0),
            medium_gaps=gap_counts.get(GapSeverity.MEDIUM, 0),
            low_gaps=gap_counts.get(GapSeverity.LOW, 0),
            info_gaps=gap_counts.get(GapSeverity.INFO, 0),
            processing_time=processing_time,
            files_analyzed=files_analyzed,
            coverage_score=coverage_score,
            quality_score=quality_score,
            metadata=metadata
        )
        
        logger.info(f"Project analysis completed: {len(all_gaps)} gaps found")
        return result
    
    def _find_files_to_analyze(self) -> List[Path]:
        """Encontra arquivos para análise."""
        files = []
        
        for pattern in self.include_patterns:
            for file_path in self.project_root.rglob(pattern):
                # Verificar se deve ser excluído
                if self._should_exclude_file(file_path):
                    continue
                
                files.append(file_path)
        
        return sorted(files)
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Verifica se arquivo deve ser excluído."""
        file_str = str(file_path)
        
        for pattern in self.exclude_patterns:
            if re.search(pattern, file_str):
                return True
        
        return False
    
    def _analyze_file(self, file_path: Path) -> List[GapDetection]:
        """Analisa um arquivo específico."""
        gaps = []
        
        try:
            # Verificar cache
            file_hash = self._get_file_hash(file_path)
            if file_hash in self.analysis_cache:
                return self.analysis_cache[file_hash]
            
            # Ler conteúdo do arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Análise sintática
            try:
                tree = ast.parse(content)
                gaps.extend(self._analyze_ast_tree(tree, file_path))
            except SyntaxError:
                # Arquivo com erro de sintaxe
                gaps.append(GapDetection(
                    gap_type=GapType.MISSING_VALIDATION,
                    severity=GapSeverity.HIGH,
                    file_path=str(file_path),
                    description="Arquivo com erro de sintaxe Python",
                    suggestion="Corrigir sintaxe do arquivo",
                    confidence=1.0
                ))
            
            # Análise de padrões
            gaps.extend(self._analyze_patterns(content, file_path))
            
            # Análise de documentação
            gaps.extend(self._analyze_documentation(content, file_path))
            
            # Análise de testes
            gaps.extend(self._analyze_test_coverage(file_path))
            
            # Armazenar no cache
            self.analysis_cache[file_hash] = gaps
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return []
    
    def _analyze_ast_tree(self, tree: ast.AST, file_path: Path) -> List[GapDetection]:
        """Analisa árvore AST do código."""
        gaps = []
        
        for node in ast.walk(tree):
            # Verificar funções sem type hints
            if isinstance(node, ast.FunctionDef):
                if not node.returns:
                    gaps.append(GapDetection(
                        gap_type=GapType.MISSING_TYPE_HINTS,
                        severity=GapSeverity.MEDIUM,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"Função '{node.name}' sem type hints de retorno",
                        suggestion=f"Adicionar -> ReturnType à função {node.name}",
                        confidence=0.8
                    ))
                
                # Verificar parâmetros sem type hints
                for arg in node.args.args:
                    if not arg.annotation:
                        gaps.append(GapDetection(
                            gap_type=GapType.MISSING_TYPE_HINTS,
                            severity=GapSeverity.LOW,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            description=f"Parâmetro '{arg.arg}' sem type hint",
                            suggestion=f"Adicionar type hint ao parâmetro {arg.arg}",
                            confidence=0.7
                        ))
            
            # Verificar classes sem docstring
            elif isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    gaps.append(GapDetection(
                        gap_type=GapType.MISSING_DOCUMENTATION,
                        severity=GapSeverity.MEDIUM,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"Classe '{node.name}' sem docstring",
                        suggestion=f"Adicionar docstring à classe {node.name}",
                        confidence=0.8
                    ))
        
        return gaps
    
    def _analyze_patterns(self, content: str, file_path: Path) -> List[GapDetection]:
        """Analisa padrões no código."""
        gaps = []
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Verificar linhas muito longas
            if len(line) > 120:
                gaps.append(GapDetection(
                    gap_type=GapType.MISSING_VALIDATION,
                    severity=GapSeverity.LOW,
                    file_path=str(file_path),
                    line_number=line_num,
                    description=f"Linha muito longa ({len(line)} caracteres)",
                    suggestion="Quebrar linha em múltiplas linhas",
                    confidence=0.6
                ))
            
            # Verificar imports não utilizados (heurística simples)
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_name = self._extract_import_name(line)
                if import_name and not self._is_import_used(content, import_name):
                    gaps.append(GapDetection(
                        gap_type=GapType.DEAD_CODE,
                        severity=GapSeverity.MEDIUM,
                        file_path=str(file_path),
                        line_number=line_num,
                        description=f"Import '{import_name}' possivelmente não utilizado",
                        suggestion=f"Remover import não utilizado: {import_name}",
                        confidence=0.7
                    ))
        
        return gaps
    
    def _analyze_documentation(self, content: str, file_path: Path) -> List[GapDetection]:
        """Analisa documentação do código."""
        gaps = []
        
        # Verificar se arquivo tem docstring
        if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
            gaps.append(GapDetection(
                gap_type=GapType.MISSING_DOCUMENTATION,
                severity=GapSeverity.LOW,
                file_path=str(file_path),
                description="Arquivo sem docstring principal",
                suggestion="Adicionar docstring no início do arquivo",
                confidence=0.6
            ))
        
        # Verificar comentários
        comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]
        code_lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        if len(code_lines) > 50 and len(comment_lines) < len(code_lines) * 0.1:
            gaps.append(GapDetection(
                gap_type=GapType.MISSING_DOCUMENTATION,
                severity=GapSeverity.MEDIUM,
                file_path=str(file_path),
                description="Poucos comentários no código",
                suggestion="Adicionar mais comentários explicativos",
                confidence=0.7
            ))
        
        return gaps
    
    def _analyze_test_coverage(self, file_path: Path) -> List[GapDetection]:
        """Analisa cobertura de testes."""
        gaps = []
        
        # Verificar se existe arquivo de teste correspondente
        test_file = self._find_test_file(file_path)
        if not test_file:
            gaps.append(GapDetection(
                gap_type=GapType.MISSING_TEST,
                severity=GapSeverity.HIGH,
                file_path=str(file_path),
                description="Arquivo sem testes correspondentes",
                suggestion=f"Criar arquivo de teste: {self._get_test_file_path(file_path)}",
                confidence=0.9
            ))
        
        return gaps
    
    def _analyze_semantic_gaps(self, existing_gaps: List[GapDetection]) -> List[GapDetection]:
        """Analisa lacunas semânticas."""
        gaps = []
        
        if not self.enable_nlp:
            return gaps
        
        # Análise de padrões semânticos
        # (Implementação simplificada - pode ser expandida)
        
        return gaps
    
    def _analyze_dependency_gaps(self) -> List[GapDetection]:
        """Analisa lacunas de dependências."""
        gaps = []
        
        # Verificar requirements.txt
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            gaps.append(GapDetection(
                gap_type=GapType.MISSING_CONFIG,
                severity=GapSeverity.CRITICAL,
                file_path="requirements.txt",
                description="Arquivo requirements.txt não encontrado",
                suggestion="Criar arquivo requirements.txt com dependências",
                confidence=1.0
            ))
        
        # Verificar .env
        env_file = self.project_root / ".env"
        if not env_file.exists():
            gaps.append(GapDetection(
                gap_type=GapType.MISSING_CONFIG,
                severity=GapSeverity.HIGH,
                file_path=".env",
                description="Arquivo .env não encontrado",
                suggestion="Criar arquivo .env com variáveis de ambiente",
                confidence=0.8
            ))
        
        return gaps
    
    def _analyze_structural_gaps(self) -> List[GapDetection]:
        """Analisa lacunas estruturais."""
        gaps = []
        
        # Verificar estrutura de diretórios
        required_dirs = ['tests', 'docs', 'scripts', 'config']
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                gaps.append(GapDetection(
                    gap_type=GapType.MISSING_CONFIG,
                    severity=GapSeverity.MEDIUM,
                    file_path=dir_name,
                    description=f"Diretório '{dir_name}' não encontrado",
                    suggestion=f"Criar diretório {dir_name}",
                    confidence=0.7
                ))
        
        return gaps
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calcula hash do arquivo."""
        if file_path in self.file_hashes:
            return self.file_hashes[file_path]
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                file_hash = hashlib.md5(content).hexdigest()
                self.file_hashes[file_path] = file_hash
                return file_hash
        except Exception:
            return str(file_path)
    
    def _extract_import_name(self, import_line: str) -> Optional[str]:
        """Extrai nome do import."""
        import_match = re.match(r'import\s+(\w+)', import_line)
        if import_match:
            return import_match.group(1)
        
        from_match = re.match(r'from\s+(\w+)', import_line)
        if from_match:
            return from_match.group(1)
        
        return None
    
    def _is_import_used(self, content: str, import_name: str) -> bool:
        """Verifica se import é utilizado."""
        # Heurística simples - pode ser melhorada
        return import_name in content
    
    def _find_test_file(self, file_path: Path) -> Optional[Path]:
        """Encontra arquivo de teste correspondente."""
        # Procurar em tests/
        test_dir = self.project_root / "tests"
        if test_dir.exists():
            test_file = test_dir / f"test_{file_path.name}"
            if test_file.exists():
                return test_file
        
        return None
    
    def _get_test_file_path(self, file_path: Path) -> str:
        """Gera caminho sugerido para arquivo de teste."""
        return f"tests/test_{file_path.name}"
    
    def _count_gaps_by_severity(self, gaps: List[GapDetection]) -> Dict[GapSeverity, int]:
        """Conta gaps por severidade."""
        counts = {}
        for gap in gaps:
            counts[gap.severity] = counts.get(gap.severity, 0) + 1
        return counts
    
    def _calculate_coverage_score(self, analyzed: int, total: int) -> float:
        """Calcula score de cobertura."""
        if total == 0:
            return 0.0
        return analyzed / total
    
    def _calculate_quality_score(self, gaps: List[GapDetection]) -> float:
        """Calcula score de qualidade."""
        if not gaps:
            return 1.0
        
        # Penalizar por gaps críticos e altos
        critical_penalty = sum(1 for gap in gaps if gap.severity == GapSeverity.CRITICAL) * 0.1
        high_penalty = sum(1 for gap in gaps if gap.severity == GapSeverity.HIGH) * 0.05
        medium_penalty = sum(1 for gap in gaps if gap.severity == GapSeverity.MEDIUM) * 0.02
        
        total_penalty = critical_penalty + high_penalty + medium_penalty
        return max(0.0, 1.0 - total_penalty)
    
    def generate_report(self, result: GapAnalysisResult, output_file: Optional[str] = None) -> str:
        """Gera relatório de análise."""
        report = []
        report.append("# Relatório de Análise de Lacunas")
        report.append(f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Projeto**: {self.project_root}")
        report.append("")
        
        # Resumo
        report.append("## 📊 Resumo")
        report.append(f"- **Total de lacunas**: {result.total_gaps}")
        report.append(f"- **Arquivos analisados**: {result.files_analyzed}")
        report.append(f"- **Tempo de processamento**: {result.processing_time:.2f}s")
        report.append(f"- **Score de cobertura**: {result.coverage_score:.2%}")
        report.append(f"- **Score de qualidade**: {result.quality_score:.2%}")
        report.append("")
        
        # Lacunas por severidade
        report.append("## 🚨 Lacunas por Severidade")
        report.append(f"- **Críticas**: {result.critical_gaps}")
        report.append(f"- **Altas**: {result.high_gaps}")
        report.append(f"- **Médias**: {result.medium_gaps}")
        report.append(f"- **Baixas**: {result.low_gaps}")
        report.append(f"- **Informativas**: {result.info_gaps}")
        report.append("")
        
        # Lacunas detalhadas
        if result.gaps:
            report.append("## 📋 Lacunas Detalhadas")
            
            for severity in [GapSeverity.CRITICAL, GapSeverity.HIGH, GapSeverity.MEDIUM, GapSeverity.LOW, GapSeverity.INFO]:
                severity_gaps = [gap for gap in result.gaps if gap.severity == severity]
                if severity_gaps:
                    report.append(f"### {severity.value.upper()}")
                    
                    for gap in severity_gaps:
                        report.append(f"#### {gap.gap_type.value}")
                        report.append(f"- **Arquivo**: {gap.file_path}")
                        if gap.line_number:
                            report.append(f"- **Linha**: {gap.line_number}")
                        report.append(f"- **Descrição**: {gap.description}")
                        report.append(f"- **Sugestão**: {gap.suggestion}")
                        report.append(f"- **Confiança**: {gap.confidence:.1%}")
                        report.append("")
        
        # Recomendações
        report.append("## 💡 Recomendações")
        if result.critical_gaps > 0:
            report.append("- 🔴 **CRÍTICO**: Resolver lacunas críticas imediatamente")
        if result.high_gaps > 0:
            report.append("- 🟠 **ALTO**: Priorizar lacunas de alta severidade")
        if result.medium_gaps > 0:
            report.append("- 🟡 **MÉDIO**: Planejar correção de lacunas médias")
        if result.low_gaps > 0:
            report.append("- 🟢 **BAIXO**: Melhorar gradualmente lacunas baixas")
        
        report_text = "\n".join(report)
        
        # Salvar relatório se especificado
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"Relatório salvo em: {output_file}")
        
        return report_text
    
    def clear_cache(self):
        """Limpa cache de análises."""
        self.analysis_cache.clear()
        self.file_hashes.clear()
        logger.info("Cache de análise limpo") 
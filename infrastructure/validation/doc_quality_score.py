"""
Sistema de DocQualityScore para Documentação Enterprise
Tracing ID: DOC_QUALITY_SCORE_001_20250127
Data: 2025-01-27
Versão: 1.0

Este módulo implementa o sistema de cálculo de qualidade de documentação
baseado em completude, coerência e similaridade semântica, seguindo
padrões enterprise de auditoria e validação automática.
"""

import os
import json
import math
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime
from pathlib import Path
import re
from dataclasses import dataclass, asdict

from shared.logger import logger
from shared.config import BASE_DIR
from infrastructure.ml.semantic_embeddings import SemanticEmbeddingService

@dataclass
class DocQualityMetrics:
    """
    Métricas de qualidade de documentação.
    
    Implementa estrutura de dados imutável para garantir
    consistência nas avaliações de qualidade.
    """
    completeness: float  # Completude (0-1)
    coherence: float     # Coerência (0-1)
    semantic_similarity: float  # Similaridade semântica (0-1)
    doc_quality_score: float    # Score final ponderado (0-1)
    timestamp: str
    source_file: str
    function_name: Optional[str] = None
    module_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        return asdict(self)
    
    def is_acceptable(self, threshold: float = 0.85) -> bool:
        """
        Verifica se a qualidade é aceitável.
        
        Args:
            threshold: Threshold mínimo de qualidade
            
        Returns:
            True se qualidade >= threshold
        """
        return self.doc_quality_score >= threshold

class DocQualityAnalyzer:
    """
    Analisador de qualidade de documentação enterprise.
    
    Implementa análise baseada em:
    - Completude: Cobertura de elementos documentais
    - Coerência: Consistência interna e externa
    - Similaridade Semântica: Alinhamento código-documentação
    """
    
    def __init__(self, 
                 semantic_service: Optional[SemanticEmbeddingService] = None,
                 output_dir: Optional[str] = None,
                 threshold: float = 0.85):
        """
        Inicializa o analisador de qualidade.
        
        Args:
            semantic_service: Serviço de embeddings semânticos
            output_dir: Diretório para salvar relatórios
            threshold: Threshold mínimo de qualidade
        """
        self.semantic_service = semantic_service or SemanticEmbeddingService()
        self.output_dir = output_dir or str(BASE_DIR / "docs" / "quality_reports")
        self.threshold = threshold
        self.analysis_history: List[DocQualityMetrics] = []
        
        # Criar diretório de saída se não existir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Padrões para análise de completude
        self.completeness_patterns = {
            'python_function': {
                'docstring': r'""".*?"""',
                'type_hints': r':\string_data*\w+',
                'parameters': r'def\string_data+\w+\string_data*\([^)]*\)',
                'returns': r'->\string_data*\w+',
                'examples': r'>>>\string_data+.*',
                'raises': r'Raises:',
                'notes': r'Note:',
                'warnings': r'Warning:'
            },
            'python_class': {
                'docstring': r'""".*?"""',
                'methods': r'def\string_data+\w+\string_data*\([^)]*\)',
                'attributes': r'self\.\w+\string_data*=',
                'inheritance': r'class\string_data+\w+\string_data*\([^)]*\)',
                'examples': r'>>>\string_data+.*',
                'usage': r'Usage:'
            },
            'typescript_function': {
                'jsdoc': r'/\*\*[\string_data\S]*?\*/',
                'type_annotations': r':\string_data*\w+',
                'parameters': r'function\string_data+\w+\string_data*\([^)]*\)',
                'returns': r'@returns?',
                'examples': r'@example',
                'throws': r'@throws',
                'deprecated': r'@deprecated'
            },
            'typescript_class': {
                'jsdoc': r'/\*\*[\string_data\S]*?\*/',
                'methods': r'\w+\string_data*\([^)]*\)\string_data*[:{]\string_data*\w+',
                'properties': r'\w+\string_data*:\string_data*\w+',
                'interfaces': r'interface\string_data+\w+',
                'examples': r'@example',
                'usage': r'@usage'
            }
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "doc_quality_analyzer_initialized",
            "status": "success",
            "source": "DocQualityAnalyzer.__init__",
            "details": {
                "output_dir": self.output_dir,
                "threshold": self.threshold,
                "patterns_loaded": len(self.completeness_patterns)
            }
        })
    
    def analyze_completeness(self, code: str, doc: str, language: str = 'python') -> float:
        """
        Analisa completude da documentação.
        
        Implementa análise baseada em padrões específicos da linguagem.
        
        Args:
            code: Código fonte
            doc: Documentação
            language: Linguagem de programação
            
        Returns:
            Score de completude (0-1)
        """
        if language not in self.completeness_patterns:
            logger.warning({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "unsupported_language",
                "status": "warning",
                "source": "DocQualityAnalyzer.analyze_completeness",
                "details": {"language": language}
            })
            return 0.5  # Score neutro para linguagens não suportadas
        
        patterns = self.completeness_patterns[language]
        scores = []
        
        # Analisar cada padrão
        for pattern_name, pattern in patterns.items():
            if pattern_name == 'docstring' or pattern_name == 'jsdoc':
                # Verificar se documentação existe
                has_doc = bool(re.search(pattern, doc, re.MULTILINE | re.DOTALL))
                scores.append(1.0 if has_doc else 0.0)
            elif pattern_name in ['parameters', 'methods']:
                # Verificar se parâmetros/métodos estão documentados
                code_matches = re.findall(pattern, code, re.MULTILINE)
                doc_matches = re.findall(pattern, doc, re.MULTILINE)
                
                if code_matches:
                    coverage = len(doc_matches) / len(code_matches)
                    scores.append(min(coverage, 1.0))
                else:
                    scores.append(1.0)  # Não há para documentar
            elif pattern_name in ['type_hints', 'type_annotations']:
                # Verificar se tipos estão documentados
                code_types = re.findall(pattern, code, re.MULTILINE)
                doc_types = re.findall(pattern, doc, re.MULTILINE)
                
                if code_types:
                    coverage = len(doc_types) / len(code_types)
                    scores.append(min(coverage, 1.0))
                else:
                    scores.append(1.0)
            else:
                # Verificar se elementos opcionais estão presentes
                has_element = bool(re.search(pattern, doc, re.MULTILINE | re.DOTALL))
                scores.append(0.8 if has_element else 0.4)  # Bônus para elementos opcionais
        
        # Calcular score médio ponderado
        if scores:
            # Peso maior para documentação principal
            weights = [2.0 if 'doc' in name else 1.0 for name in patterns.keys()]
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            total_weight = sum(weights)
            completeness = weighted_sum / total_weight
        else:
            completeness = 0.0
        
        logger.debug({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "completeness_analyzed",
            "status": "success",
            "source": "DocQualityAnalyzer.analyze_completeness",
            "details": {
                "language": language,
                "completeness": completeness,
                "scores": scores,
                "patterns_checked": len(patterns)
            }
        })
        
        return completeness
    
    def analyze_coherence(self, doc: str) -> float:
        """
        Analisa coerência da documentação.
        
        Implementa análise baseada em:
        - Consistência de terminologia
        - Estrutura lógica
        - Clareza de explicações
        
        Args:
            doc: Documentação para analisar
            
        Returns:
            Score de coerência (0-1)
        """
        if not doc.strip():
            return 0.0
        
        coherence_scores = []
        
        # 1. Consistência de terminologia
        terms = re.findall(r'\b\w+\b', doc.lower())
        term_frequency = {}
        for term in terms:
            if len(term) > 3:  # Ignorar palavras muito curtas
                term_frequency[term] = term_frequency.get(term, 0) + 1
        
        # Calcular entropia de terminologia (menor = mais consistente)
        total_terms = sum(term_frequency.values())
        if total_terms > 0:
            entropy = 0
            for count in term_frequency.values():
                p = count / total_terms
                if p > 0:
                    entropy -= p * math.log2(p)
            
            # Normalizar entropia (0-1, onde 1 = mais consistente)
            max_entropy = math.log2(len(term_frequency)) if term_frequency else 1
            term_consistency = 1 - (entropy / max_entropy) if max_entropy > 0 else 1
            coherence_scores.append(term_consistency)
        
        # 2. Estrutura lógica
        # Verificar se há seções bem definidas
        sections = re.findall(r'^(Args|Returns|Raises|Examples|Note|Warning|Usage):', 
                             doc, re.MULTILINE | re.IGNORECASE)
        structure_score = min(len(sections) / 3, 1.0)  # Normalizar para 0-1
        coherence_scores.append(structure_score)
        
        # 3. Clareza de explicações
        # Verificar se há explicações detalhadas
        sentences = re.split(r'[.!?]+', doc)
        detailed_explanations = sum(1 for string_data in sentences if len(string_data.strip()) > 50)
        clarity_score = min(detailed_explanations / max(len(sentences), 1), 1.0)
        coherence_scores.append(clarity_score)
        
        # 4. Presença de exemplos
        has_examples = bool(re.search(r'>>>\string_data+|@example|Example:', doc, re.MULTILINE | re.IGNORECASE))
        example_score = 1.0 if has_examples else 0.5
        coherence_scores.append(example_score)
        
        # Calcular score final
        coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0
        
        logger.debug({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "coherence_analyzed",
            "status": "success",
            "source": "DocQualityAnalyzer.analyze_coherence",
            "details": {
                "coherence": coherence,
                "scores": coherence_scores,
                "doc_length": len(doc)
            }
        })
        
        return coherence
    
    def analyze_semantic_similarity(self, code: str, doc: str) -> float:
        """
        Analisa similaridade semântica entre código e documentação.
        
        Args:
            code: Código fonte
            doc: Documentação
            
        Returns:
            Score de similaridade semântica (0-1)
        """
        try:
            # Usar serviço de embeddings para calcular similaridade
            is_consistent = self.semantic_service.validate_semantic_consistency(code, doc)
            
            # Converter para score numérico
            similarity = 1.0 if is_consistent else 0.5
            
            logger.debug({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "semantic_similarity_analyzed",
                "status": "success",
                "source": "DocQualityAnalyzer.analyze_semantic_similarity",
                "details": {
                    "similarity": similarity,
                    "is_consistent": is_consistent,
                    "code_length": len(code),
                    "doc_length": len(doc)
                }
            })
            
            return similarity
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "semantic_similarity_analysis_failed",
                "status": "error",
                "source": "DocQualityAnalyzer.analyze_semantic_similarity",
                "details": {
                    "error": str(e),
                    "code_length": len(code),
                    "doc_length": len(doc)
                }
            })
            return 0.5  # Score neutro em caso de erro
    
    def calculate_doc_quality_score(self, 
                                  completeness: float, 
                                  coherence: float, 
                                  semantic_similarity: float) -> float:
        """
        Calcula score final de qualidade de documentação.
        
        Fórmula: DocQualityScore = ((completude * 4) + (coerência * 3) + (similaridade_semântica * 3)) / 10
        
        Args:
            completeness: Score de completude (0-1)
            coherence: Score de coerência (0-1)
            semantic_similarity: Score de similaridade semântica (0-1)
            
        Returns:
            Score final de qualidade (0-1)
        """
        # Aplicar pesos conforme especificação
        weighted_completeness = completeness * 4
        weighted_coherence = coherence * 3
        weighted_similarity = semantic_similarity * 3
        
        # Calcular score final
        doc_quality_score = (weighted_completeness + weighted_coherence + weighted_similarity) / 10
        
        # Garantir que está entre 0 e 1
        doc_quality_score = max(0.0, min(1.0, doc_quality_score))
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "doc_quality_score_calculated",
            "status": "success",
            "source": "DocQualityAnalyzer.calculate_doc_quality_score",
            "details": {
                "completeness": completeness,
                "coherence": coherence,
                "semantic_similarity": semantic_similarity,
                "doc_quality_score": doc_quality_score,
                "weights": {"completeness": 4, "coherence": 3, "similarity": 3}
            }
        })
        
        return doc_quality_score
    
    def analyze_documentation(self, 
                            code: str, 
                            doc: str, 
                            source_file: str,
                            language: str = 'python',
                            function_name: Optional[str] = None,
                            module_name: Optional[str] = None) -> DocQualityMetrics:
        """
        Analisa qualidade completa da documentação.
        
        Args:
            code: Código fonte
            doc: Documentação
            source_file: Arquivo fonte
            language: Linguagem de programação
            function_name: Nome da função (opcional)
            module_name: Nome do módulo (opcional)
            
        Returns:
            Métricas de qualidade da documentação
        """
        start_time = datetime.utcnow()
        
        # Realizar análises
        completeness = self.analyze_completeness(code, doc, language)
        coherence = self.analyze_coherence(doc)
        semantic_similarity = self.analyze_semantic_similarity(code, doc)
        
        # Calcular score final
        doc_quality_score = self.calculate_doc_quality_score(
            completeness, coherence, semantic_similarity
        )
        
        # Criar métricas
        metrics = DocQualityMetrics(
            completeness=completeness,
            coherence=coherence,
            semantic_similarity=semantic_similarity,
            doc_quality_score=doc_quality_score,
            timestamp=datetime.utcnow().isoformat(),
            source_file=source_file,
            function_name=function_name,
            module_name=module_name
        )
        
        # Adicionar ao histórico
        self.analysis_history.append(metrics)
        
        # Log da análise
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "documentation_analysis_completed",
            "status": "success" if metrics.is_acceptable(self.threshold) else "warning",
            "source": "DocQualityAnalyzer.analyze_documentation",
            "details": {
                "source_file": source_file,
                "function_name": function_name,
                "module_name": module_name,
                "language": language,
                "doc_quality_score": doc_quality_score,
                "is_acceptable": metrics.is_acceptable(self.threshold),
                "processing_time_seconds": processing_time
            }
        })
        
        return metrics
    
    def save_quality_report(self, 
                          metrics: DocQualityMetrics, 
                          exec_id: str) -> str:
        """
        Salva relatório de qualidade em arquivo.
        
        Args:
            metrics: Métricas de qualidade
            exec_id: ID da execução
            
        Returns:
            Caminho do arquivo salvo
        """
        try:
            # Criar nome do arquivo
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"doc_quality_score_{exec_id}_{timestamp}.md"
            filepath = Path(self.output_dir) / filename
            
            # Gerar conteúdo do relatório
            report_content = self._generate_quality_report(metrics, exec_id)
            
            # Salvar arquivo
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "quality_report_saved",
                "status": "success",
                "source": "DocQualityAnalyzer.save_quality_report",
                "details": {
                    "filepath": str(filepath),
                    "exec_id": exec_id,
                    "doc_quality_score": metrics.doc_quality_score
                }
            })
            
            return str(filepath)
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "quality_report_save_failed",
                "status": "error",
                "source": "DocQualityAnalyzer.save_quality_report",
                "details": {
                    "error": str(e),
                    "exec_id": exec_id
                }
            })
            raise
    
    def _generate_quality_report(self, metrics: DocQualityMetrics, exec_id: str) -> str:
        """
        Gera conteúdo do relatório de qualidade.
        
        Args:
            metrics: Métricas de qualidade
            exec_id: ID da execução
            
        Returns:
            Conteúdo do relatório em markdown
        """
        status_emoji = "✅" if metrics.is_acceptable(self.threshold) else "⚠️"
        status_text = "ACEITÁVEL" if metrics.is_acceptable(self.threshold) else "NECESSITA MELHORIA"
        
        report = f"""# 📊 Relatório de Qualidade de Documentação

**Tracing ID**: `DOC_QUALITY_REPORT_{exec_id}`  
**Data**: {metrics.timestamp}  
**Status**: {status_emoji} {status_text}

---

## 📋 Informações Gerais

- **Arquivo Fonte**: `{metrics.source_file}`
- **Função**: `{metrics.function_name or 'N/A'}`
- **Módulo**: `{metrics.module_name or 'N/A'}`
- **Score Final**: **{metrics.doc_quality_score:.3f}** / 1.000

---

## 📈 Métricas Detalhadas

### 🎯 Completude: {metrics.completeness:.3f} / 1.000
**Peso**: 40% do score final

**Análise**: {self._get_completeness_analysis(metrics.completeness)}

### 🔗 Coerência: {metrics.coherence:.3f} / 1.000
**Peso**: 30% do score final

**Análise**: {self._get_coherence_analysis(metrics.coherence)}

### 🧠 Similaridade Semântica: {metrics.semantic_similarity:.3f} / 1.000
**Peso**: 30% do score final

**Análise**: {self._get_similarity_analysis(metrics.semantic_similarity)}

---

## 📊 Fórmula de Cálculo

```
DocQualityScore = ((completude × 4) + (coerência × 3) + (similaridade_semântica × 3)) ÷ 10
```

**Cálculo**: (({metrics.completeness:.3f} × 4) + ({metrics.coherence:.3f} × 3) + ({metrics.semantic_similarity:.3f} × 3)) ÷ 10 = **{metrics.doc_quality_score:.3f}**

---

## 🎯 Recomendações

{self._get_recommendations(metrics)}

---

## 📝 Notas Técnicas

- **Threshold Mínimo**: {self.threshold}
- **Modelo de Embeddings**: {self.semantic_service.model_name}
- **Gerado por**: DocQualityAnalyzer v1.0
- **Execução ID**: {exec_id}

---

*Relatório gerado automaticamente pelo sistema de documentação enterprise.*
"""
        
        return report
    
    def _get_completeness_analysis(self, completeness: float) -> str:
        """Retorna análise textual da completude."""
        if completeness >= 0.9:
            return "Excelente! A documentação cobre todos os elementos essenciais."
        elif completeness >= 0.8:
            return "Boa! A documentação cobre a maioria dos elementos importantes."
        elif completeness >= 0.7:
            return "Aceitável. Alguns elementos importantes podem estar faltando."
        elif completeness >= 0.6:
            return "Necessita melhoria. Elementos importantes não estão documentados."
        else:
            return "Crítico! A documentação está muito incompleta."
    
    def _get_coherence_analysis(self, coherence: float) -> str:
        """Retorna análise textual da coerência."""
        if coherence >= 0.9:
            return "Excelente! A documentação é muito clara e bem estruturada."
        elif coherence >= 0.8:
            return "Boa! A documentação é clara e bem organizada."
        elif coherence >= 0.7:
            return "Aceitável. A documentação pode ser mais clara."
        elif coherence >= 0.6:
            return "Necessita melhoria. A documentação precisa ser mais clara."
        else:
            return "Crítico! A documentação é confusa e mal estruturada."
    
    def _get_similarity_analysis(self, similarity: float) -> str:
        """Retorna análise textual da similaridade semântica."""
        if similarity >= 0.9:
            return "Excelente! A documentação reflete perfeitamente o código."
        elif similarity >= 0.8:
            return "Boa! A documentação está bem alinhada com o código."
        elif similarity >= 0.7:
            return "Aceitável. A documentação pode estar mais alinhada com o código."
        elif similarity >= 0.6:
            return "Necessita melhoria. A documentação não reflete bem o código."
        else:
            return "Crítico! A documentação não corresponde ao código."
    
    def _get_recommendations(self, metrics: DocQualityMetrics) -> str:
        """Retorna recomendações baseadas nas métricas."""
        recommendations = []
        
        if metrics.completeness < 0.8:
            recommendations.append("- **Completude**: Adicione documentação para parâmetros, retornos e exemplos")
        
        if metrics.coherence < 0.8:
            recommendations.append("- **Coerência**: Melhore a estrutura e clareza da documentação")
        
        if metrics.semantic_similarity < 0.8:
            recommendations.append("- **Similaridade**: Alinhe melhor a documentação com o código implementado")
        
        if not recommendations:
            recommendations.append("- **Manutenção**: Continue mantendo a alta qualidade da documentação")
        
        return "\n".join(recommendations)
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo das análises realizadas.
        
        Returns:
            Dicionário com estatísticas das análises
        """
        if not self.analysis_history:
            return {"message": "Nenhuma análise realizada ainda"}
        
        scores = [m.doc_quality_score for m in self.analysis_history]
        acceptable_count = sum(1 for m in self.analysis_history if m.is_acceptable(self.threshold))
        
        return {
            "total_analyses": len(self.analysis_history),
            "acceptable_count": acceptable_count,
            "acceptance_rate": acceptable_count / len(self.analysis_history),
            "avg_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "threshold": self.threshold
        } 
"""
Serviço de Validação Avançada
Sistema de validação de qualidade de dados e prompts preenchidos
"""

import re
import json
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.prompt_system import (
    Nicho, Categoria, DadosColetados, PromptBase, 
    PromptPreenchido, LogOperacao
)


class ValidationSeverity(Enum):
    """Níveis de severidade da validação"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Resultado de uma validação"""
    is_valid: bool
    score: float  # 0.0 a 1.0
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    metadata: Dict[str, Any]


class DataQualityValidator:
    """Validador de qualidade de dados coletados"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def validate_primary_keyword(self, keyword: str, nicho_id: int) -> ValidationResult:
        """Valida a palavra-chave principal"""
        issues = []
        suggestions = []
        score = 1.0
        
        # Validações básicas
        if not keyword or not keyword.strip():
            issues.append({
                "type": "empty_keyword",
                "severity": ValidationSeverity.ERROR,
                "message": "Palavra-chave principal não pode estar vazia"
            })
            score -= 0.5
            
        if len(keyword) > 255:
            issues.append({
                "type": "keyword_too_long",
                "severity": ValidationSeverity.WARNING,
                "message": f"Palavra-chave muito longa ({len(keyword)} chars)"
            })
            score -= 0.1
            
        # Verificar duplicatas no mesmo nicho
        existing = self.db.query(DadosColetados).filter(
            and_(
                DadosColetados.nicho_id == nicho_id,
                DadosColetados.primary_keyword == keyword
            )
        ).first()
        
        if existing:
            issues.append({
                "type": "duplicate_keyword",
                "severity": ValidationSeverity.WARNING,
                "message": "Palavra-chave já existe neste nicho"
            })
            score -= 0.2
            
        # Verificar relevância por nicho
        nicho = self.db.query(Nicho).filter(Nicho.id == nicho_id).first()
        if nicho:
            relevance_score = self._check_keyword_relevance(keyword, nicho.nome)
            if relevance_score < 0.7:
                issues.append({
                    "type": "low_relevance",
                    "severity": ValidationSeverity.WARNING,
                    "message": f"Baixa relevância para o nicho '{nicho.nome}'"
                })
                score -= 0.3
                
        # Sugestões
        if score < 0.8:
            suggestions.append("Considere usar uma palavra-chave mais específica")
        if len(keyword) < 3:
            suggestions.append("Palavra-chave muito curta, considere usar termos mais descritivos")
            
        return ValidationResult(
            is_valid=score >= 0.7,
            score=score,
            issues=issues,
            suggestions=suggestions,
            metadata={"keyword_length": len(keyword), "relevance_score": relevance_score if 'relevance_score' in locals() else 1.0}
        )
        
    def validate_secondary_keywords(self, keywords: str) -> ValidationResult:
        """Valida palavras-chave secundárias"""
        issues = []
        suggestions = []
        score = 1.0
        
        if not keywords:
            return ValidationResult(
                is_valid=True,
                score=1.0,
                issues=[],
                suggestions=[],
                metadata={"keyword_count": 0}
            )
            
        keyword_list = [key.strip() for key in keywords.split(',') if key.strip()]
        
        # Validações
        if len(keyword_list) > 20:
            issues.append({
                "type": "too_many_keywords",
                "severity": ValidationSeverity.WARNING,
                "message": f"Muitas palavras-chave ({len(keyword_list)})"
            })
            score -= 0.2
            
        # Verificar duplicatas
        duplicates = [key for key in keyword_list if keyword_list.count(key) > 1]
        if duplicates:
            issues.append({
                "type": "duplicate_secondary_keywords",
                "severity": ValidationSeverity.WARNING,
                "message": f"Palavras-chave duplicadas: {', '.join(set(duplicates))}"
            })
            score -= 0.1
            
        # Verificar palavras muito curtas
        short_keywords = [key for key in keyword_list if len(key) < 2]
        if short_keywords:
            issues.append({
                "type": "short_keywords",
                "severity": ValidationSeverity.INFO,
                "message": f"Palavras-chave muito curtas: {', '.join(short_keywords)}"
            })
            score -= 0.05
            
        # Sugestões
        if len(keyword_list) < 3:
            suggestions.append("Considere adicionar mais palavras-chave secundárias")
        if len(keyword_list) > 15:
            suggestions.append("Muitas palavras-chave podem diluir o foco")
            
        return ValidationResult(
            is_valid=score >= 0.8,
            score=score,
            issues=issues,
            suggestions=suggestions,
            metadata={"keyword_count": len(keyword_list)}
        )
        
    def validate_cluster_content(self, content: str) -> ValidationResult:
        """Valida o conteúdo do cluster"""
        issues = []
        suggestions = []
        score = 1.0
        
        if not content or not content.strip():
            issues.append({
                "type": "empty_content",
                "severity": ValidationSeverity.ERROR,
                "message": "Conteúdo do cluster não pode estar vazio"
            })
            score -= 0.5
            
        # Verificar tamanho
        if len(content) < 50:
            issues.append({
                "type": "content_too_short",
                "severity": ValidationSeverity.WARNING,
                "message": "Conteúdo muito curto para ser útil"
            })
            score -= 0.3
            
        if len(content) > 2000:
            issues.append({
                "type": "content_too_long",
                "severity": ValidationSeverity.WARNING,
                "message": "Conteúdo muito longo, pode ser truncado"
            })
            score -= 0.1
            
        # Verificar qualidade do texto
        word_count = len(content.split())
        if word_count < 10:
            issues.append({
                "type": "insufficient_words",
                "severity": ValidationSeverity.WARNING,
                "message": f"Poucas palavras ({word_count}) no conteúdo"
            })
            score -= 0.2
            
        # Verificar caracteres especiais excessivos
        special_chars = len(re.findall(r'[^\w\string_data]', content))
        if special_chars > len(content) * 0.3:
            issues.append({
                "type": "excessive_special_chars",
                "severity": ValidationSeverity.INFO,
                "message": "Muitos caracteres especiais no conteúdo"
            })
            score -= 0.05
            
        # Sugestões
        if word_count < 20:
            suggestions.append("Adicione mais detalhes ao conteúdo do cluster")
        if len(content) > 1500:
            suggestions.append("Considere resumir o conteúdo para melhor performance")
            
        return ValidationResult(
            is_valid=score >= 0.7,
            score=score,
            issues=issues,
            suggestions=suggestions,
            metadata={
                "content_length": len(content),
                "word_count": word_count,
                "special_chars_ratio": special_chars / len(content) if content else 0
            }
        )
        
    def _check_keyword_relevance(self, keyword: str, nicho_name: str) -> float:
        """Verifica a relevância da palavra-chave para o nicho"""
        # Implementação simplificada - em produção usar IA/ML
        keyword_lower = keyword.lower()
        nicho_lower = nicho_name.lower()
        
        # Palavras-chave comuns por nicho
        nicho_keywords = {
            "saúde": ["saude", "saudavel", "medico", "tratamento", "cura", "bem-estar"],
            "finanças": ["dinheiro", "investimento", "economia", "poupança", "renda"],
            "tecnologia": ["tech", "software", "programação", "digital", "inovação"],
            "educação": ["estudo", "aprendizado", "curso", "treinamento", "conhecimento"],
            "marketing": ["venda", "publicidade", "promoção", "cliente", "negócio"]
        }
        
        # Encontrar nicho mais próximo
        best_match = 0.0
        for nicho_key, keywords in nicho_keywords.items():
            if nicho_key in nicho_lower:
                for kw in keywords:
                    if kw in keyword_lower or keyword_lower in kw:
                        best_match = max(best_match, 0.8)
                    elif any(word in keyword_lower for word in kw.split()):
                        best_match = max(best_match, 0.6)
                        
        return best_match if best_match > 0 else 0.3  # Relevância mínima


class PromptQualityValidator:
    """Validador de qualidade de prompts preenchidos"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def validate_prompt_integrity(self, prompt_original: str, prompt_preenchido: str) -> ValidationResult:
        """Valida a integridade do prompt preenchido"""
        issues = []
        suggestions = []
        score = 1.0
        
        # Verificar se todas as lacunas foram preenchidas
        lacunas_originais = re.findall(r'\[.*?\]', prompt_original)
        lacunas_restantes = re.findall(r'\[.*?\]', prompt_preenchido)
        
        if lacunas_restantes:
            issues.append({
                "type": "unfilled_gaps",
                "severity": ValidationSeverity.ERROR,
                "message": f"Lacunas não preenchidas: {', '.join(lacunas_restantes)}"
            })
            score -= 0.5
            
        # Verificar se o conteúdo foi preservado
        original_clean = re.sub(r'\[.*?\]', '', prompt_original)
        preenchido_clean = re.sub(r'\[.*?\]', '', prompt_preenchido)
        
        if original_clean not in preenchido_clean:
            issues.append({
                "type": "content_modified",
                "severity": ValidationSeverity.WARNING,
                "message": "Conteúdo original foi modificado"
            })
            score -= 0.3
            
        # Verificar tamanho do prompt final
        if len(prompt_preenchido) > 10000:
            issues.append({
                "type": "prompt_too_long",
                "severity": ValidationSeverity.WARNING,
                "message": "Prompt muito longo para uso eficiente"
            })
            score -= 0.1
            
        # Verificar qualidade do preenchimento
        if len(prompt_preenchido) < len(prompt_original):
            issues.append({
                "type": "prompt_too_short",
                "severity": ValidationSeverity.WARNING,
                "message": "Prompt final menor que o original"
            })
            score -= 0.2
            
        # Sugestões
        if lacunas_restantes:
            suggestions.append("Complete todas as lacunas antes de usar o prompt")
        if len(prompt_preenchido) > 8000:
            suggestions.append("Considere dividir o prompt em partes menores")
            
        return ValidationResult(
            is_valid=score >= 0.8,
            score=score,
            issues=issues,
            suggestions=suggestions,
            metadata={
                "original_length": len(prompt_original),
                "final_length": len(prompt_preenchido),
                "gaps_filled": len(lacunas_originais) - len(lacunas_restantes),
                "total_gaps": len(lacunas_originais)
            }
        )
        
    def validate_semantic_consistency(self, prompt_preenchido: str, dados_coletados: DadosColetados) -> ValidationResult:
        """Valida consistência semântica do prompt preenchido"""
        issues = []
        suggestions = []
        score = 1.0
        
        # Verificar se as palavras-chave estão presentes no prompt
        if dados_coletados.primary_keyword.lower() not in prompt_preenchido.lower():
            issues.append({
                "type": "missing_primary_keyword",
                "severity": ValidationSeverity.WARNING,
                "message": "Palavra-chave principal não encontrada no prompt"
            })
            score -= 0.2
            
        # Verificar palavras-chave secundárias
        if dados_coletados.secondary_keywords:
            secondary_list = [key.strip().lower() for key in dados_coletados.secondary_keywords.split(',')]
            missing_secondary = [kw for kw in secondary_list if kw not in prompt_preenchido.lower()]
            
            if missing_secondary:
                issues.append({
                    "type": "missing_secondary_keywords",
                    "severity": ValidationSeverity.INFO,
                    "message": f"Palavras-chave secundárias não encontradas: {', '.join(missing_secondary[:3])}"
                })
                score -= 0.1
                
        # Verificar conteúdo do cluster
        if dados_coletados.cluster_content:
            cluster_words = dados_coletados.cluster_content.lower().split()[:10]  # Primeiras 10 palavras
            cluster_present = sum(1 for word in cluster_words if word in prompt_preenchido.lower())
            cluster_ratio = cluster_present / len(cluster_words) if cluster_words else 0
            
            if cluster_ratio < 0.3:
                issues.append({
                    "type": "low_cluster_content_usage",
                    "severity": ValidationSeverity.INFO,
                    "message": "Pouco conteúdo do cluster foi utilizado"
                })
                score -= 0.1
                
        return ValidationResult(
            is_valid=score >= 0.8,
            score=score,
            issues=issues,
            suggestions=suggestions,
            metadata={
                "primary_keyword_present": dados_coletados.primary_keyword.lower() in prompt_preenchido.lower(),
                "secondary_keywords_used": len(secondary_list) - len(missing_secondary) if 'missing_secondary' in locals() else 0,
                "cluster_content_ratio": cluster_ratio if 'cluster_ratio' in locals() else 0
            }
        )


class ValidationService:
    """Serviço principal de validação"""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_validator = DataQualityValidator(db)
        self.prompt_validator = PromptQualityValidator(db)
        
    def validate_dados_coletados(self, dados: DadosColetados) -> ValidationResult:
        """Valida dados coletados completos"""
        results = []
        
        # Validar palavra-chave principal
        primary_result = self.data_validator.validate_primary_keyword(
            dados.primary_keyword, dados.nicho_id
        )
        results.append(primary_result)
        
        # Validar palavras-chave secundárias
        secondary_result = self.data_validator.validate_secondary_keywords(
            dados.secondary_keywords or ""
        )
        results.append(secondary_result)
        
        # Validar conteúdo do cluster
        cluster_result = self.data_validator.validate_cluster_content(
            dados.cluster_content
        )
        results.append(cluster_result)
        
        # Calcular score geral
        avg_score = sum(r.score for r in results) / len(results)
        all_issues = []
        all_suggestions = []
        
        for result in results:
            all_issues.extend(result.issues)
            all_suggestions.extend(result.suggestions)
            
        return ValidationResult(
            is_valid=avg_score >= 0.7,
            score=avg_score,
            issues=all_issues,
            suggestions=all_suggestions,
            metadata={
                "validation_count": len(results),
                "component_scores": [r.score for r in results]
            }
        )
        
    def validate_prompt_preenchido(self, prompt: PromptPreenchido) -> ValidationResult:
        """Valida prompt preenchido completo"""
        # Buscar dados coletados
        dados = self.db.query(DadosColetados).filter(
            DadosColetados.id == prompt.dados_coletados_id
        ).first()
        
        if not dados:
            return ValidationResult(
                is_valid=False,
                score=0.0,
                issues=[{
                    "type": "missing_data",
                    "severity": ValidationSeverity.ERROR,
                    "message": "Dados coletados não encontrados"
                }],
                suggestions=["Verifique se os dados coletados existem"],
                metadata={}
            )
            
        # Validar integridade
        integrity_result = self.prompt_validator.validate_prompt_integrity(
            prompt.prompt_original, prompt.prompt_preenchido
        )
        
        # Validar consistência semântica
        semantic_result = self.prompt_validator.validate_semantic_consistency(
            prompt.prompt_preenchido, dados
        )
        
        # Combinar resultados
        avg_score = (integrity_result.score + semantic_result.score) / 2
        all_issues = integrity_result.issues + semantic_result.issues
        all_suggestions = integrity_result.suggestions + semantic_result.suggestions
        
        return ValidationResult(
            is_valid=avg_score >= 0.8,
            score=avg_score,
            issues=all_issues,
            suggestions=all_suggestions,
            metadata={
                "integrity_score": integrity_result.score,
                "semantic_score": semantic_result.score,
                **integrity_result.metadata,
                **semantic_result.metadata
            }
        )
        
    def get_validation_report(self, nicho_id: Optional[int] = None) -> Dict[str, Any]:
        """Gera relatório de validação para nicho ou sistema todo"""
        query = self.db.query(DadosColetados)
        if nicho_id:
            query = query.filter(DadosColetados.nicho_id == nicho_id)
            
        dados_list = query.all()
        
        validation_results = []
        total_score = 0
        
        for dados in dados_list:
            result = self.validate_dados_coletados(dados)
            validation_results.append({
                "dados_id": dados.id,
                "score": result.score,
                "is_valid": result.is_valid,
                "issues_count": len(result.issues)
            })
            total_score += result.score
            
        avg_score = total_score / len(dados_list) if dados_list else 0
        
        return {
            "total_dados": len(dados_list),
            "average_score": avg_score,
            "valid_count": sum(1 for r in validation_results if r["is_valid"]),
            "invalid_count": sum(1 for r in validation_results if not r["is_valid"]),
            "results": validation_results
        } 
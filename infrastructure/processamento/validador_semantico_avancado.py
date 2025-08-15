"""
Módulo de Validação Semântica Avançada para Prompts
Responsável por validação semântica com NLP, cache inteligente e validação contextual.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 1.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import re
import json
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
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
    logging.warning("NLP libraries not available. Using fallback validation.")

from shared.logger import logger
from domain.models import Keyword, Cluster

class ValidationSeverity(Enum):
    """Severidades de validação."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationResult:
    """Resultado de validação semântica."""
    is_valid: bool
    score: float  # 0.0 a 1.0
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    metadata: Dict[str, Any]

@dataclass
class SemanticContext:
    """Contexto semântico para validação."""
    primary_keyword: str
    secondary_keywords: List[str]
    cluster_content: str
    intent: str
    funnel_stage: str
    domain: str

class ValidadorSemanticoAvancado:
    """
    Validador semântico avançado com NLP para prompts.
    
    Funcionalidades:
    - Validação semântica com embeddings
    - Cache inteligente de validações
    - Análise contextual
    - Detecção de inconsistências
    - Validação de coerência
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        cache_enabled: bool = True,
        similarity_threshold: float = 0.7,
        context_weight: float = 0.3
    ):
        """
        Inicializa o validador semântico.
        
        Args:
            model_name: Nome do modelo de embeddings
            cache_enabled: Habilita cache de validações
            similarity_threshold: Threshold para similaridade semântica
            context_weight: Peso do contexto na validação
        """
        self.model_name = model_name
        self.cache_enabled = cache_enabled
        self.similarity_threshold = similarity_threshold
        self.context_weight = context_weight
        
        # Cache de validações
        self.validation_cache = {}
        self.embedding_cache = {}
        
        # Inicializar NLP se disponível
        if NLP_AVAILABLE:
            try:
                self.nlp = spacy.load("pt_core_news_sm")
                self.embedding_model = SentenceTransformer(model_name)
                logger.info(f"NLP initialized with model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize NLP: {e}")
                NLP_AVAILABLE = False
        
        # Padrões de validação
        self.validation_patterns = {
            'keyword_density': r'\b\w+\b',
            'placeholder_format': r'\{[^}]+\}',
            'html_tags': r'<[^>]+>',
            'url_pattern': r'https?://[^\string_data]+',
            'email_pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-data]{2,}\b'
        }
        
        logger.info("ValidadorSemanticoAvancado initialized successfully")
    
    def validar_prompt_semantico(
        self,
        prompt: str,
        context: Optional[SemanticContext] = None,
        strict_mode: bool = False
    ) -> ValidationResult:
        """
        Valida prompt semanticamente.
        
        Args:
            prompt: Conteúdo do prompt
            context: Contexto semântico
            strict_mode: Modo estrito de validação
            
        Returns:
            Resultado da validação
        """
        start_time = time.time()
        
        # Verificar cache
        cache_key = self._generate_cache_key(prompt, context, strict_mode)
        if self.cache_enabled and cache_key in self.validation_cache:
            cached_result = self.validation_cache[cache_key]
            logger.info(f"Validation result retrieved from cache: {cache_key}")
            return cached_result
        
        # Inicializar resultado
        issues = []
        suggestions = []
        score = 1.0
        
        # Validações básicas
        basic_validation = self._validar_basico(prompt)
        issues.extend(basic_validation['issues'])
        score *= basic_validation['score']
        
        # Validação semântica (se NLP disponível)
        if NLP_AVAILABLE and context:
            semantic_validation = self._validar_semantico(prompt, context)
            issues.extend(semantic_validation['issues'])
            score *= semantic_validation['score']
        
        # Validação contextual
        if context:
            context_validation = self._validar_contextual(prompt, context)
            issues.extend(context_validation['issues'])
            score *= context_validation['score']
        
        # Validação de coerência
        coherence_validation = self._validar_coerencia(prompt)
        issues.extend(coherence_validation['issues'])
        score *= coherence_validation['score']
        
        # Gerar sugestões
        suggestions = self._gerar_sugestoes(issues, score)
        
        # Preparar metadados
        metadata = {
            'validation_time': time.time() - start_time,
            'prompt_length': len(prompt),
            'word_count': len(prompt.split()),
            'nlp_available': NLP_AVAILABLE,
            'cache_hit': False,
            'strict_mode': strict_mode
        }
        
        # Criar resultado
        result = ValidationResult(
            is_valid=score >= (0.8 if strict_mode else 0.6),
            score=score,
            issues=issues,
            suggestions=suggestions,
            metadata=metadata
        )
        
        # Armazenar no cache
        if self.cache_enabled:
            self.validation_cache[cache_key] = result
            logger.info(f"Validation result cached: {cache_key}")
        
        logger.info(f"Semantic validation completed. Score: {score:.3f}, Valid: {result.is_valid}")
        return result
    
    def _validar_basico(self, prompt: str) -> Dict[str, Any]:
        """Validação básica do prompt."""
        issues = []
        score = 1.0
        
        # Verificar tamanho mínimo
        if len(prompt.strip()) < 50:
            issues.append({
                'type': 'prompt_too_short',
                'severity': ValidationSeverity.ERROR,
                'message': 'Prompt muito curto (mínimo 50 caracteres)',
                'position': 0
            })
            score *= 0.5
        
        # Verificar densidade de palavras-chave
        words = re.findall(self.validation_patterns['keyword_density'], prompt.lower())
        if len(words) < 10:
            issues.append({
                'type': 'insufficient_keywords',
                'severity': ValidationSeverity.WARNING,
                'message': 'Poucas palavras-chave detectadas',
                'position': 0
            })
            score *= 0.8
        
        # Verificar placeholders não preenchidos
        placeholders = re.findall(self.validation_patterns['placeholder_format'], prompt)
        if placeholders:
            issues.append({
                'type': 'unfilled_placeholders',
                'severity': ValidationSeverity.ERROR,
                'message': f'Placeholders não preenchidos: {placeholders}',
                'position': 0
            })
            score *= 0.3
        
        return {'issues': issues, 'score': score}
    
    def _validar_semantico(self, prompt: str, context: SemanticContext) -> Dict[str, Any]:
        """Validação semântica com NLP."""
        issues = []
        score = 1.0
        
        try:
            # Gerar embeddings
            prompt_embedding = self._get_embedding(prompt)
            keyword_embedding = self._get_embedding(context.primary_keyword)
            
            # Calcular similaridade
            similarity = cosine_similarity(
                [prompt_embedding], 
                [keyword_embedding]
            )[0][0]
            
            # Validar similaridade
            if similarity < self.similarity_threshold:
                issues.append({
                    'type': 'low_semantic_similarity',
                    'severity': ValidationSeverity.WARNING,
                    'message': f'Baixa similaridade semântica: {similarity:.3f}',
                    'position': 0
                })
                score *= 0.7
            
            # Validar contexto
            context_embedding = self._get_embedding(context.cluster_content)
            context_similarity = cosine_similarity(
                [prompt_embedding], 
                [context_embedding]
            )[0][0]
            
            if context_similarity < self.similarity_threshold:
                issues.append({
                    'type': 'context_mismatch',
                    'severity': ValidationSeverity.WARNING,
                    'message': f'Incompatibilidade de contexto: {context_similarity:.3f}',
                    'position': 0
                })
                score *= 0.8
                
        except Exception as e:
            logger.error(f"Error in semantic validation: {e}")
            issues.append({
                'type': 'semantic_validation_error',
                'severity': ValidationSeverity.WARNING,
                'message': f'Erro na validação semântica: {str(e)}',
                'position': 0
            })
            score *= 0.9
        
        return {'issues': issues, 'score': score}
    
    def _validar_contextual(self, prompt: str, context: SemanticContext) -> Dict[str, Any]:
        """Validação contextual."""
        issues = []
        score = 1.0
        
        # Verificar se a palavra-chave principal está presente
        if context.primary_keyword.lower() not in prompt.lower():
            issues.append({
                'type': 'missing_primary_keyword',
                'severity': ValidationSeverity.ERROR,
                'message': f'Palavra-chave principal não encontrada: {context.primary_keyword}',
                'position': 0
            })
            score *= 0.4
        
        # Verificar palavras-chave secundárias
        missing_secondary = []
        for keyword in context.secondary_keywords:
            if keyword.lower() not in prompt.lower():
                missing_secondary.append(keyword)
        
        if missing_secondary:
            issues.append({
                'type': 'missing_secondary_keywords',
                'severity': ValidationSeverity.WARNING,
                'message': f'Palavras-chave secundárias não encontradas: {missing_secondary}',
                'position': 0
            })
            score *= 0.8
        
        # Verificar fase do funil
        if context.funnel_stage and context.funnel_stage.lower() not in prompt.lower():
            issues.append({
                'type': 'missing_funnel_stage',
                'severity': ValidationSeverity.WARNING,
                'message': f'Fase do funil não encontrada: {context.funnel_stage}',
                'position': 0
            })
            score *= 0.9
        
        return {'issues': issues, 'score': score}
    
    def _validar_coerencia(self, prompt: str) -> Dict[str, Any]:
        """Validação de coerência."""
        issues = []
        score = 1.0
        
        # Verificar repetições excessivas
        words = prompt.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Ignorar palavras muito curtas
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Verificar palavras repetidas excessivamente
        for word, freq in word_freq.items():
            if freq > len(words) * 0.1:  # Mais de 10% do texto
                issues.append({
                    'type': 'excessive_repetition',
                    'severity': ValidationSeverity.WARNING,
                    'message': f'Repetição excessiva da palavra: {word}',
                    'position': 0
                })
                score *= 0.8
        
        # Verificar estrutura básica
        if not re.search(r'<h[1-6]>|^#+\string_data', prompt, re.MULTILINE):
            issues.append({
                'type': 'missing_headings',
                'severity': ValidationSeverity.WARNING,
                'message': 'Estrutura de títulos não encontrada',
                'position': 0
            })
            score *= 0.9
        
        return {'issues': issues, 'score': score}
    
    def _gerar_sugestoes(self, issues: List[Dict], score: float) -> List[str]:
        """Gera sugestões baseadas nos problemas encontrados."""
        suggestions = []
        
        for issue in issues:
            if issue['type'] == 'prompt_too_short':
                suggestions.append("Adicione mais conteúdo ao prompt")
            elif issue['type'] == 'unfilled_placeholders':
                suggestions.append("Preencha todos os placeholders antes de usar")
            elif issue['type'] == 'low_semantic_similarity':
                suggestions.append("Revise o conteúdo para melhor alinhamento semântico")
            elif issue['type'] == 'missing_primary_keyword':
                suggestions.append("Inclua a palavra-chave principal no prompt")
            elif issue['type'] == 'excessive_repetition':
                suggestions.append("Reduza repetições excessivas de palavras")
        
        if score < 0.7:
            suggestions.append("Considere revisar completamente o prompt")
        
        return suggestions
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Obtém embedding do texto com cache."""
        if not NLP_AVAILABLE:
            return np.zeros(384)  # Fallback
        
        # Verificar cache
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.embedding_cache:
            return self.embedding_cache[text_hash]
        
        # Gerar embedding
        try:
            embedding = self.embedding_model.encode(text)
            self.embedding_cache[text_hash] = embedding
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return np.zeros(384)
    
    def _generate_cache_key(self, prompt: str, context: Optional[SemanticContext], strict_mode: bool) -> str:
        """Gera chave para cache."""
        content = f"{prompt}_{strict_mode}"
        if context:
            content += f"_{context.primary_keyword}_{context.funnel_stage}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def limpar_cache(self):
        """Limpa o cache de validações."""
        self.validation_cache.clear()
        self.embedding_cache.clear()
        logger.info("Validation cache cleared")
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas do validador."""
        return {
            'cache_size': len(self.validation_cache),
            'embedding_cache_size': len(self.embedding_cache),
            'nlp_available': NLP_AVAILABLE,
            'model_name': self.model_name,
            'similarity_threshold': self.similarity_threshold
        }

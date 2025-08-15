"""
Módulo de Enriquecimento de Keywords
Responsável por enriquecer keywords com dados adicionais e contexto.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 1.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import re
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from shared.logger import logger
from domain.models import Keyword, Cluster

class EnrichmentType(Enum):
    """Tipos de enriquecimento."""
    SEMANTIC = "semantic"
    CONTEXTUAL = "contextual"
    TREND = "trend"
    COMPETITION = "competition"
    INTENT = "intent"

@dataclass
class EnrichmentData:
    """Dados de enriquecimento."""
    keyword: str
    enrichment_type: EnrichmentType
    data: Dict[str, Any]
    confidence: float
    source: str
    timestamp: datetime

@dataclass
class EnrichmentResult:
    """Resultado do enriquecimento."""
    keyword: Keyword
    enrichments: List[EnrichmentData]
    total_score: float
    processing_time: float
    metadata: Dict[str, Any]

class KeywordEnricher:
    """
    Enriquecimento de keywords com dados semânticos e contextuais.
    
    Funcionalidades:
    - Enriquecimento semântico
    - Análise de tendências
    - Análise de competição
    - Detecção de intenção
    - Cache de enriquecimentos
    """
    
    def __init__(
        self,
        cache_enabled: bool = True,
        max_cache_size: int = 1000,
        confidence_threshold: float = 0.7
    ):
        """
        Inicializa o enriquecimento de keywords.
        
        Args:
            cache_enabled: Habilita cache de enriquecimentos
            max_cache_size: Tamanho máximo do cache
            confidence_threshold: Threshold de confiança
        """
        self.cache_enabled = cache_enabled
        self.max_cache_size = max_cache_size
        self.confidence_threshold = confidence_threshold
        
        # Cache de enriquecimentos
        self.enrichment_cache: Dict[str, EnrichmentResult] = {}
        
        # Padrões de análise
        self.analysis_patterns = {
            'intent_commercial': [
                r'\b(comprar|vender|preço|custo|barato|caro|oferta|desconto)\b',
                r'\b(melhor|top|recomendado|avaliação|review)\b',
                r'\b(onde|quando|como comprar|loja|site)\b'
            ],
            'intent_informational': [
                r'\b(o que|como|quando|onde|por que|definição|significado)\b',
                r'\b(tutorial|guia|passo a passo|dicas|conselhos)\b',
                r'\b(história|origem|evolução|desenvolvimento)\b'
            ],
            'intent_navigational': [
                r'\b(site|página|link|url|endereço|localização)\b',
                r'\b(empresa|marca|produto específico)\b',
                r'\b(contato|telefone|email|endereço)\b'
            ]
        }
        
        logger.info("KeywordEnricher initialized successfully")
    
    def enriquecer_keyword(
        self,
        keyword: Keyword,
        context: Optional[Dict[str, Any]] = None
    ) -> EnrichmentResult:
        """
        Enriquece uma keyword com dados adicionais.
        
        Args:
            keyword: Keyword a ser enriquecida
            context: Contexto adicional
            
        Returns:
            Resultado do enriquecimento
        """
        start_time = time.time()
        
        # Verificar cache
        cache_key = self._generate_cache_key(keyword, context)
        if self.cache_enabled and cache_key in self.enrichment_cache:
            cached_result = self.enrichment_cache[cache_key]
            logger.info(f"Enrichment result retrieved from cache: {cache_key}")
            return cached_result
        
        # Inicializar enriquecimentos
        enrichments = []
        total_score = 0.0
        
        # Enriquecimento semântico
        semantic_enrichment = self._enriquecimento_semantico(keyword)
        if semantic_enrichment:
            enrichments.append(semantic_enrichment)
            total_score += semantic_enrichment.confidence
        
        # Enriquecimento contextual
        contextual_enrichment = self._enriquecimento_contextual(keyword, context)
        if contextual_enrichment:
            enrichments.append(contextual_enrichment)
            total_score += contextual_enrichment.confidence
        
        # Análise de tendências
        trend_enrichment = self._analise_tendencias(keyword)
        if trend_enrichment:
            enrichments.append(trend_enrichment)
            total_score += trend_enrichment.confidence
        
        # Análise de competição
        competition_enrichment = self._analise_competicao(keyword)
        if competition_enrichment:
            enrichments.append(competition_enrichment)
            total_score += competition_enrichment.confidence
        
        # Detecção de intenção
        intent_enrichment = self._detectar_intencao(keyword)
        if intent_enrichment:
            enrichments.append(intent_enrichment)
            total_score += intent_enrichment.confidence
        
        # Calcular score médio
        if enrichments:
            total_score = total_score / len(enrichments)
        
        # Preparar metadados
        metadata = {
            'enrichment_count': len(enrichments),
            'cache_hit': False,
            'confidence_threshold': self.confidence_threshold,
            'context_provided': context is not None
        }
        
        # Criar resultado
        result = EnrichmentResult(
            keyword=keyword,
            enrichments=enrichments,
            total_score=total_score,
            processing_time=time.time() - start_time,
            metadata=metadata
        )
        
        # Armazenar no cache
        if self.cache_enabled:
            self._armazenar_cache_enrichment(cache_key, result)
        
        logger.info(f"Keyword enriched: {keyword.termo} (score: {total_score:.3f})")
        return result
    
    def enriquecer_cluster(
        self,
        cluster: Cluster,
        context: Optional[Dict[str, Any]] = None
    ) -> List[EnrichmentResult]:
        """
        Enriquece todas as keywords de um cluster.
        
        Args:
            cluster: Cluster a ser enriquecido
            context: Contexto adicional
            
        Returns:
            Lista de resultados de enriquecimento
        """
        results = []
        
        for keyword in cluster.keywords:
            try:
                result = self.enriquecer_keyword(keyword, context)
                results.append(result)
            except Exception as e:
                logger.error(f"Error enriching keyword {keyword.termo}: {e}")
                continue
        
        logger.info(f"Cluster enriched: {len(results)} keywords processed")
        return results
    
    def _enriquecimento_semantico(self, keyword: Keyword) -> Optional[EnrichmentData]:
        """Enriquecimento semântico da keyword."""
        try:
            # Análise básica do termo
            termo = keyword.termo.lower()
            words = termo.split()
            
            # Detectar características semânticas
            semantic_features = {
                'word_count': len(words),
                'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
                'has_numbers': bool(re.search(r'\data', termo)),
                'has_special_chars': bool(re.search(r'[^\w\string_data]', termo)),
                'is_long_tail': len(words) > 2,
                'is_brand': self._detectar_marca(termo),
                'is_location': self._detectar_localizacao(termo),
                'is_product': self._detectar_produto(termo)
            }
            
            # Calcular confiança baseada na análise
            confidence = self._calcular_confianca_semantica(semantic_features)
            
            if confidence >= self.confidence_threshold:
                return EnrichmentData(
                    keyword=keyword.termo,
                    enrichment_type=EnrichmentType.SEMANTIC,
                    data=semantic_features,
                    confidence=confidence,
                    source="semantic_analysis",
                    timestamp=datetime.utcnow()
                )
            
        except Exception as e:
            logger.error(f"Error in semantic enrichment: {e}")
        
        return None
    
    def _enriquecimento_contextual(
        self,
        keyword: Keyword,
        context: Optional[Dict[str, Any]]
    ) -> Optional[EnrichmentData]:
        """Enriquecimento contextual da keyword."""
        try:
            if not context:
                return None
            
            # Análise contextual
            contextual_features = {
                'domain_relevance': self._calcular_relevancia_dominio(keyword, context),
                'seasonal_relevance': self._calcular_relevancia_sazonal(keyword, context),
                'trend_alignment': self._calcular_alinhamento_tendencia(keyword, context),
                'audience_match': self._calcular_match_audiencia(keyword, context)
            }
            
            # Calcular confiança
            confidence = sum(contextual_features.values()) / len(contextual_features)
            
            if confidence >= self.confidence_threshold:
                return EnrichmentData(
                    keyword=keyword.termo,
                    enrichment_type=EnrichmentType.CONTEXTUAL,
                    data=contextual_features,
                    confidence=confidence,
                    source="contextual_analysis",
                    timestamp=datetime.utcnow()
                )
            
        except Exception as e:
            logger.error(f"Error in contextual enrichment: {e}")
        
        return None
    
    def _analise_tendencias(self, keyword: Keyword) -> Optional[EnrichmentData]:
        """Análise de tendências da keyword."""
        try:
            # Simular análise de tendências (implementação real dependeria de APIs)
            trend_features = {
                'trend_direction': self._simular_direcao_tendencia(keyword),
                'trend_strength': self._simular_forca_tendencia(keyword),
                'seasonality': self._detectar_sazonalidade(keyword),
                'growth_potential': self._calcular_potencial_crescimento(keyword)
            }
            
            confidence = 0.6  # Simulado
            
            if confidence >= self.confidence_threshold:
                return EnrichmentData(
                    keyword=keyword.termo,
                    enrichment_type=EnrichmentType.TREND,
                    data=trend_features,
                    confidence=confidence,
                    source="trend_analysis",
                    timestamp=datetime.utcnow()
                )
            
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
        
        return None
    
    def _analise_competicao(self, keyword: Keyword) -> Optional[EnrichmentData]:
        """Análise de competição da keyword."""
        try:
            # Simular análise de competição
            competition_features = {
                'competition_level': self._simular_nivel_competicao(keyword),
                'difficulty_score': self._calcular_dificuldade_ranking(keyword),
                'opportunity_score': self._calcular_score_oportunidade(keyword),
                'market_saturation': self._calcular_saturacao_mercado(keyword)
            }
            
            confidence = 0.7  # Simulado
            
            if confidence >= self.confidence_threshold:
                return EnrichmentData(
                    keyword=keyword.termo,
                    enrichment_type=EnrichmentType.COMPETITION,
                    data=competition_features,
                    confidence=confidence,
                    source="competition_analysis",
                    timestamp=datetime.utcnow()
                )
            
        except Exception as e:
            logger.error(f"Error in competition analysis: {e}")
        
        return None
    
    def _detectar_intencao(self, keyword: Keyword) -> Optional[EnrichmentData]:
        """Detecção de intenção da keyword."""
        try:
            termo = keyword.termo.lower()
            intent_scores = {
                'commercial': 0.0,
                'informational': 0.0,
                'navigational': 0.0
            }
            
            # Analisar padrões de intenção
            for intent_type, patterns in self.analysis_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, termo):
                        intent_scores[intent_type.split('_')[1]] += 0.3
            
            # Normalizar scores
            total_score = sum(intent_scores.values())
            if total_score > 0:
                intent_scores = {key: value/total_score for key, value in intent_scores.items()}
            
            # Determinar intenção dominante
            dominant_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[dominant_intent]
            
            if confidence >= self.confidence_threshold:
                return EnrichmentData(
                    keyword=keyword.termo,
                    enrichment_type=EnrichmentType.INTENT,
                    data={
                        'intent_type': dominant_intent,
                        'intent_scores': intent_scores,
                        'confidence': confidence
                    },
                    confidence=confidence,
                    source="intent_detection",
                    timestamp=datetime.utcnow()
                )
            
        except Exception as e:
            logger.error(f"Error in intent detection: {e}")
        
        return None
    
    def _detectar_marca(self, termo: str) -> bool:
        """Detecta se o termo é uma marca."""
        # Implementação simplificada
        brand_indicators = ['marca', 'brand', 'empresa', 'company', 'loja', 'store']
        return any(indicator in termo for indicator in brand_indicators)
    
    def _detectar_localizacao(self, termo: str) -> bool:
        """Detecta se o termo é uma localização."""
        # Implementação simplificada
        location_indicators = ['cidade', 'estado', 'país', 'região', 'bairro', 'rua']
        return any(indicator in termo for indicator in location_indicators)
    
    def _detectar_produto(self, termo: str) -> bool:
        """Detecta se o termo é um produto."""
        # Implementação simplificada
        product_indicators = ['produto', 'item', 'artigo', 'mercadoria', 'bem']
        return any(indicator in termo for indicator in product_indicators)
    
    def _calcular_confianca_semantica(self, features: Dict[str, Any]) -> float:
        """Calcula confiança do enriquecimento semântico."""
        score = 0.0
        
        # Pontuar características
        if features['word_count'] > 1:
            score += 0.2
        if features['is_long_tail']:
            score += 0.3
        if features['is_brand'] or features['is_location'] or features['is_product']:
            score += 0.3
        if not features['has_special_chars']:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calcular_relevancia_dominio(self, keyword: Keyword, context: Dict[str, Any]) -> float:
        """Calcula relevância do domínio."""
        # Implementação simplificada
        return 0.7
    
    def _calcular_relevancia_sazonal(self, keyword: Keyword, context: Dict[str, Any]) -> float:
        """Calcula relevância sazonal."""
        # Implementação simplificada
        return 0.6
    
    def _calcular_alinhamento_tendencia(self, keyword: Keyword, context: Dict[str, Any]) -> float:
        """Calcula alinhamento com tendências."""
        # Implementação simplificada
        return 0.8
    
    def _calcular_match_audiencia(self, keyword: Keyword, context: Dict[str, Any]) -> float:
        """Calcula match com audiência."""
        # Implementação simplificada
        return 0.7
    
    def _simular_direcao_tendencia(self, keyword: Keyword) -> str:
        """Simula direção da tendência."""
        # Implementação simplificada
        return "crescente"
    
    def _simular_forca_tendencia(self, keyword: Keyword) -> float:
        """Simula força da tendência."""
        # Implementação simplificada
        return 0.7
    
    def _detectar_sazonalidade(self, keyword: Keyword) -> bool:
        """Detecta sazonalidade."""
        # Implementação simplificada
        seasonal_terms = ['verão', 'inverno', 'natal', 'páscoa', 'férias']
        return any(term in keyword.termo.lower() for term in seasonal_terms)
    
    def _calcular_potencial_crescimento(self, keyword: Keyword) -> float:
        """Calcula potencial de crescimento."""
        # Implementação simplificada
        return 0.6
    
    def _simular_nivel_competicao(self, keyword: Keyword) -> str:
        """Simula nível de competição."""
        # Implementação simplificada
        return "médio"
    
    def _calcular_dificuldade_ranking(self, keyword: Keyword) -> float:
        """Calcula dificuldade de ranking."""
        # Implementação simplificada
        return 0.5
    
    def _calcular_score_oportunidade(self, keyword: Keyword) -> float:
        """Calcula score de oportunidade."""
        # Implementação simplificada
        return 0.8
    
    def _calcular_saturacao_mercado(self, keyword: Keyword) -> float:
        """Calcula saturação do mercado."""
        # Implementação simplificada
        return 0.4
    
    def _generate_cache_key(self, keyword: Keyword, context: Optional[Dict[str, Any]]) -> str:
        """Gera chave para cache."""
        import hashlib
        content = f"{keyword.termo}_{keyword.volume_busca}_{keyword.cpc}"
        if context:
            content += f"_{hashlib.md5(json.dumps(context, sort_keys=True).encode()).hexdigest()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _armazenar_cache_enrichment(self, cache_key: str, result: EnrichmentResult):
        """Armazena resultado no cache."""
        # Verificar tamanho do cache
        if len(self.enrichment_cache) >= self.max_cache_size:
            # Remover entrada mais antiga
            oldest_key = min(self.enrichment_cache.keys(), 
                           key=lambda key: self.enrichment_cache[key].timestamp)
            del self.enrichment_cache[oldest_key]
        
        self.enrichment_cache[cache_key] = result
    
    def limpar_cache(self):
        """Limpa o cache de enriquecimentos."""
        self.enrichment_cache.clear()
        logger.info("Enrichment cache cleared")
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas do enriquecimento."""
        return {
            'cache_size': len(self.enrichment_cache),
            'cache_enabled': self.cache_enabled,
            'max_cache_size': self.max_cache_size,
            'confidence_threshold': self.confidence_threshold
        }

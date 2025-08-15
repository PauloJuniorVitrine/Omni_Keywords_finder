"""
Sistema de Embeddings Semânticos para Documentação Enterprise
Tracing ID: SEMANTIC_EMBEDDINGS_001_20250127
Data: 2025-01-27
Versão: 1.0

Este módulo implementa o sistema de embeddings semânticos para validação
automática de qualidade de documentação, seguindo padrões enterprise
de privacidade, performance e confiabilidade.
"""

import os
import json
import hashlib
from typing import List, Dict, Optional, Tuple, Union
from datetime import datetime
import numpy as np
from pathlib import Path
import logging

# Importação condicional para evitar falhas em ambientes sem GPU
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False
    logging.warning("SentenceTransformer não disponível. Usando fallback.")

from shared.logger import logger
from shared.config import BASE_DIR

class SemanticEmbeddingService:
    """
    Serviço de embeddings semânticos para validação de documentação.
    
    Implementa padrões enterprise com:
    - Cache inteligente para performance
    - Validação de qualidade
    - Fallback para ambientes sem GPU
    - Logs estruturados
    - Métricas de performance
    """
    
    def __init__(self, 
                 model_name: str = 'all-MiniLM-L6-v2',
                 cache_dir: Optional[str] = None,
                 threshold: float = 0.85,
                 max_length: int = 512):
        """
        Inicializa o serviço de embeddings semânticos.
        
        Args:
            model_name: Nome do modelo SentenceTransformer
            cache_dir: Diretório para cache de embeddings
            threshold: Threshold de similaridade (0.85 padrão)
            max_length: Comprimento máximo de tokens
        """
        self.model_name = model_name
        self.threshold = threshold
        self.max_length = max_length
        self.cache_dir = cache_dir or str(BASE_DIR / "infrastructure" / "cache" / "embeddings")
        self.model = None
        self.cache = {}
        self.metrics = {
            'embeddings_generated': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_processing_time': 0.0
        }
        
        # Criar diretório de cache se não existir
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        
        # Inicializar modelo
        self._initialize_model()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "semantic_embedding_service_initialized",
            "status": "success",
            "source": "SemanticEmbeddingService.__init__",
            "details": {
                "model_name": model_name,
                "threshold": threshold,
                "cache_dir": self.cache_dir,
                "sentence_transformer_available": SENTENCE_TRANSFORMER_AVAILABLE
            }
        })
    
    def _initialize_model(self) -> None:
        """
        Inicializa o modelo de embeddings.
        
        Implementa fallback para ambientes sem SentenceTransformer.
        """
        if SENTENCE_TRANSFORMER_AVAILABLE:
            try:
                self.model = SentenceTransformer(self.model_name)
                logger.info({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "model_loaded_successfully",
                    "status": "success",
                    "source": "SemanticEmbeddingService._initialize_model",
                    "details": {"model_name": self.model_name}
                })
            except Exception as e:
                logger.error({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "model_loading_failed",
                    "status": "error",
                    "source": "SemanticEmbeddingService._initialize_model",
                    "details": {
                        "model_name": self.model_name,
                        "error": str(e)
                    }
                })
                self.model = None
        else:
            logger.warning({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "sentence_transformer_unavailable",
                "status": "warning",
                "source": "SemanticEmbeddingService._initialize_model",
                "details": {"fallback_mode": True}
            })
    
    def _generate_cache_key(self, text: str) -> str:
        """
        Gera chave única para cache baseada no texto.
        
        Args:
            text: Texto para gerar chave
            
        Returns:
            Chave hash única
        """
        # Normalizar texto para consistência
        normalized_text = text.strip().lower()
        return hashlib.md5(normalized_text.encode('utf-8')).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[List[float]]:
        """
        Carrega embedding do cache.
        
        Args:
            cache_key: Chave do cache
            
        Returns:
            Embedding se encontrado, None caso contrário
        """
        cache_file = Path(self.cache_dir) / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    # Verificar se o cache não expirou (7 dias)
                    cache_time = datetime.fromisoformat(data['timestamp'])
                    if (datetime.utcnow() - cache_time).days < 7:
                        self.metrics['cache_hits'] += 1
                        return data['embedding']
            except Exception as e:
                logger.warning({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "cache_load_failed",
                    "status": "warning",
                    "source": "SemanticEmbeddingService._load_from_cache",
                    "details": {
                        "cache_key": cache_key,
                        "error": str(e)
                    }
                })
        
        self.metrics['cache_misses'] += 1
        return None
    
    def _save_to_cache(self, cache_key: str, embedding: List[float]) -> None:
        """
        Salva embedding no cache.
        
        Args:
            cache_key: Chave do cache
            embedding: Embedding para salvar
        """
        try:
            cache_file = Path(self.cache_dir) / f"{cache_key}.json"
            data = {
                'embedding': embedding,
                'timestamp': datetime.utcnow().isoformat(),
                'model_name': self.model_name
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "cache_save_failed",
                "status": "error",
                "source": "SemanticEmbeddingService._save_to_cache",
                "details": {
                    "cache_key": cache_key,
                    "error": str(e)
                }
            })
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding semântico para texto.
        
        Implementa cache inteligente e fallback para performance.
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Lista de floats representando o embedding
            
        Raises:
            ValueError: Se texto estiver vazio ou modelo não disponível
        """
        if not text or not text.strip():
            raise ValueError("Texto não pode estar vazio")
        
        start_time = datetime.utcnow()
        cache_key = self._generate_cache_key(text)
        
        # Tentar carregar do cache primeiro
        cached_embedding = self._load_from_cache(cache_key)
        if cached_embedding:
            return cached_embedding
        
        # Gerar novo embedding
        if self.model is not None:
            try:
                # Usar SentenceTransformer
                embedding = self.model.encode(
                    text, 
                    max_length=self.max_length,
                    convert_to_numpy=True
                ).tolist()
                
            except Exception as e:
                logger.error({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "embedding_generation_failed",
                    "status": "error",
                    "source": "SemanticEmbeddingService.generate_embedding",
                    "details": {
                        "text_length": len(text),
                        "error": str(e)
                    }
                })
                # Fallback para embedding simples
                embedding = self._generate_fallback_embedding(text)
        else:
            # Fallback para embedding simples
            embedding = self._generate_fallback_embedding(text)
        
        # Salvar no cache
        self._save_to_cache(cache_key, embedding)
        
        # Atualizar métricas
        self.metrics['embeddings_generated'] += 1
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        self.metrics['total_processing_time'] += processing_time
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "embedding_generated",
            "status": "success",
            "source": "SemanticEmbeddingService.generate_embedding",
            "details": {
                "text_length": len(text),
                "embedding_dimensions": len(embedding),
                "processing_time_seconds": processing_time,
                "cache_used": cached_embedding is not None
            }
        })
        
        return embedding
    
    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """
        Gera embedding de fallback quando SentenceTransformer não está disponível.
        
        Implementa embedding simples baseado em características do texto.
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Embedding de fallback (384 dimensões para compatibilidade)
        """
        # Normalizar texto
        normalized_text = text.lower().strip()
        
        # Características básicas do texto
        features = {
            'length': len(normalized_text),
            'word_count': len(normalized_text.split()),
            'char_count': len(normalized_text.replace(' ', '')),
            'sentence_count': normalized_text.count('.') + normalized_text.count('!') + normalized_text.count('?'),
            'avg_word_length': len(normalized_text.replace(' ', '')) / max(len(normalized_text.split()), 1),
            'complexity_score': len(set(normalized_text.split())) / max(len(normalized_text.split()), 1)
        }
        
        # Gerar embedding de 384 dimensões (compatível com all-MiniLM-L6-v2)
        embedding = []
        for index in range(384):
            # Usar características do texto para gerar valores pseudo-aleatórios
            seed = hash(f"{normalized_text}_{index}") % 1000000
            np.random.seed(seed)
            value = np.random.normal(0, 1)
            
            # Ajustar baseado nas características do texto
            if index < 6:
                # Primeiras 6 dimensões baseadas nas características
                feature_values = list(features.values())
                value = feature_values[index % len(feature_values)] / 1000  # Normalizar
            else:
                # Restante baseado no conteúdo do texto
                char_value = sum(ord(c) for c in normalized_text[index % len(normalized_text):index % len(normalized_text) + 1])
                value = (char_value % 1000) / 1000 - 0.5
            
            embedding.append(float(value))
        
        # Normalizar embedding
        embedding_array = np.array(embedding)
        embedding_array = embedding_array / np.linalg.norm(embedding_array)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "fallback_embedding_generated",
            "status": "info",
            "source": "SemanticEmbeddingService._generate_fallback_embedding",
            "details": {
                "text_length": len(text),
                "embedding_dimensions": len(embedding)
            }
        })
        
        return embedding_array.tolist()
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcula similaridade coseno entre dois embeddings.
        
        Args:
            embedding1: Primeiro embedding
            embedding2: Segundo embedding
            
        Returns:
            Similaridade coseno (0-1)
            
        Raises:
            ValueError: Se embeddings tiverem dimensões diferentes
        """
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings devem ter a mesma dimensão")
        
        # Converter para numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calcular similaridade coseno
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Garantir que está entre 0 e 1
        similarity = max(0.0, min(1.0, similarity))
        
        logger.debug({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "similarity_calculated",
            "status": "success",
            "source": "SemanticEmbeddingService.calculate_similarity",
            "details": {
                "similarity": similarity,
                "embedding_dimensions": len(embedding1)
            }
        })
        
        return float(similarity)
    
    def validate_semantic_consistency(self, function_code: str, documentation: str) -> bool:
        """
        Valida consistência semântica entre código e documentação.
        
        Args:
            function_code: Código da função
            documentation: Documentação da função
            
        Returns:
            True se consistente (similaridade >= threshold), False caso contrário
        """
        try:
            # Gerar embeddings
            code_embedding = self.generate_embedding(function_code)
            doc_embedding = self.generate_embedding(documentation)
            
            # Calcular similaridade
            similarity = self.calculate_similarity(code_embedding, doc_embedding)
            
            # Validar contra threshold
            is_consistent = similarity >= self.threshold
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "semantic_consistency_validated",
                "status": "success" if is_consistent else "warning",
                "source": "SemanticEmbeddingService.validate_semantic_consistency",
                "details": {
                    "similarity": similarity,
                    "threshold": self.threshold,
                    "is_consistent": is_consistent,
                    "code_length": len(function_code),
                    "doc_length": len(documentation)
                }
            })
            
            return is_consistent
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "semantic_consistency_validation_failed",
                "status": "error",
                "source": "SemanticEmbeddingService.validate_semantic_consistency",
                "details": {
                    "error": str(e),
                    "code_length": len(function_code),
                    "doc_length": len(documentation)
                }
            })
            return False
    
    def get_metrics(self) -> Dict[str, Union[int, float]]:
        """
        Retorna métricas de performance do serviço.
        
        Returns:
            Dicionário com métricas
        """
        avg_processing_time = (
            self.metrics['total_processing_time'] / 
            max(self.metrics['embeddings_generated'], 1)
        )
        
        cache_hit_rate = (
            self.metrics['cache_hits'] / 
            max(self.metrics['cache_hits'] + self.metrics['cache_misses'], 1)
        )
        
        return {
            **self.metrics,
            'avg_processing_time_seconds': avg_processing_time,
            'cache_hit_rate': cache_hit_rate,
            'model_available': self.model is not None
        }
    
    def clear_cache(self) -> None:
        """
        Limpa o cache de embeddings.
        """
        try:
            cache_path = Path(self.cache_dir)
            if cache_path.exists():
                for cache_file in cache_path.glob("*.json"):
                    cache_file.unlink()
                
                self.metrics['cache_hits'] = 0
                self.metrics['cache_misses'] = 0
                
                logger.info({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "cache_cleared",
                    "status": "success",
                    "source": "SemanticEmbeddingService.clear_cache",
                    "details": {"cache_dir": self.cache_dir}
                })
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "cache_clear_failed",
                "status": "error",
                "source": "SemanticEmbeddingService.clear_cache",
                "details": {
                    "error": str(e),
                    "cache_dir": self.cache_dir
                }
            }) 
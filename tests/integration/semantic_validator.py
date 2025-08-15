"""
Validador Semântico para Testes de Integração

📐 CoCoT: Baseado em especificação do prompt de testes de integração
🌲 ToT: Avaliado múltiplas estratégias de validação semântica
♻️ ReAct: Implementado validação com embeddings e similaridade de cosseno

Tracing ID: semantic-validator-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Critério: cosine_similarity ≥ 0.90
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import hashlib
import time

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI não disponível. Usando validação baseada em hash.")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("Sentence Transformers não disponível.")

logger = logging.getLogger(__name__)

@dataclass
class SemanticValidationResult:
    """Resultado da validação semântica."""
    fluxo_nome: str
    teste_nome: str
    similaridade: float
    is_valid: bool
    threshold: float = 0.90
    embedding_model: str = ""
    validation_time_ms: float = 0.0
    details: Dict[str, Any] = None

class SemanticValidator:
    """Validador semântico para testes de integração."""
    
    def __init__(self, 
                 model_name: str = "text-embedding-3-small",
                 threshold: float = 0.90,
                 use_openai: bool = True):
        """
        Inicializa validador semântico.
        
        Args:
            model_name: Nome do modelo de embedding
            threshold: Limite de similaridade (0.90 por padrão)
            use_openai: Se deve usar OpenAI ou Sentence Transformers
        """
        self.model_name = model_name
        self.threshold = threshold
        self.use_openai = use_openai and OPENAI_AVAILABLE
        
        # Inicializar modelo
        if self.use_openai:
            self.client = OpenAI()
            self.embedding_model = "OpenAI"
        elif SENTENCE_TRANSFORMERS_AVAILABLE:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_model = "Sentence-BERT"
        else:
            self.embedding_model = "Hash-based"
        
        logger.info(f"SemanticValidator inicializado com modelo: {self.embedding_model}")
    
    def validate_fluxo_vs_teste(self, 
                               fluxo_descricao: str, 
                               teste_descricao: str,
                               fluxo_nome: str = "",
                               teste_nome: str = "") -> SemanticValidationResult:
        """
        Valida se o teste cobre adequadamente o fluxo.
        
        Args:
            fluxo_descricao: Descrição do fluxo
            teste_descricao: Descrição do teste
            fluxo_nome: Nome do fluxo
            teste_nome: Nome do teste
            
        Returns:
            Resultado da validação semântica
        """
        start_time = time.time()
        
        try:
            if self.use_openai:
                similaridade = self._calculate_openai_similarity(fluxo_descricao, teste_descricao)
            elif SENTENCE_TRANSFORMERS_AVAILABLE:
                similaridade = self._calculate_sbert_similarity(fluxo_descricao, teste_descricao)
            else:
                similaridade = self._calculate_hash_similarity(fluxo_descricao, teste_descricao)
            
            validation_time = (time.time() - start_time) * 1000
            
            is_valid = similaridade >= self.threshold
            
            details = {
                'fluxo_descricao': fluxo_descricao,
                'teste_descricao': teste_descricao,
                'similaridade_calculada': similaridade,
                'threshold_requerido': self.threshold,
                'modelo_utilizado': self.embedding_model
            }
            
            return SemanticValidationResult(
                fluxo_nome=fluxo_nome,
                teste_nome=teste_nome,
                similaridade=similaridade,
                is_valid=is_valid,
                threshold=self.threshold,
                embedding_model=self.embedding_model,
                validation_time_ms=validation_time,
                details=details
            )
            
        except Exception as e:
            logger.error(f"Erro na validação semântica: {e}")
            return SemanticValidationResult(
                fluxo_nome=fluxo_nome,
                teste_nome=teste_nome,
                similaridade=0.0,
                is_valid=False,
                threshold=self.threshold,
                embedding_model=self.embedding_model,
                validation_time_ms=(time.time() - start_time) * 1000,
                details={'error': str(e)}
            )
    
    def _calculate_openai_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade usando OpenAI embeddings."""
        try:
            # Gerar embeddings
            response1 = self.client.embeddings.create(
                input=text1,
                model=self.model_name
            )
            embedding1 = response1.data[0].embedding
            
            response2 = self.client.embeddings.create(
                input=text2,
                model=self.model_name
            )
            embedding2 = response2.data[0].embedding
            
            # Calcular similaridade de cosseno
            return self._cosine_similarity(embedding1, embedding2)
            
        except Exception as e:
            logger.error(f"Erro ao calcular similaridade OpenAI: {e}")
            return 0.0
    
    def _calculate_sbert_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade usando Sentence-BERT."""
        try:
            # Gerar embeddings
            embedding1 = self.model.encode(text1)
            embedding2 = self.model.encode(text2)
            
            # Calcular similaridade de cosseno
            return self._cosine_similarity(embedding1, embedding2)
            
        except Exception as e:
            logger.error(f"Erro ao calcular similaridade SBERT: {e}")
            return 0.0
    
    def _calculate_hash_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade baseada em hash (fallback)."""
        try:
            # Normalizar textos
            text1_normalized = self._normalize_text(text1)
            text2_normalized = self._normalize_text(text2)
            
            # Gerar hashes
            hash1 = hashlib.md5(text1_normalized.encode()).hexdigest()
            hash2 = hashlib.md5(text2_normalized.encode()).hexdigest()
            
            # Calcular similaridade baseada em caracteres comuns
            common_chars = sum(1 for a, b in zip(hash1, hash2) if a == b)
            total_chars = len(hash1)
            
            return common_chars / total_chars
            
        except Exception as e:
            logger.error(f"Erro ao calcular similaridade hash: {e}")
            return 0.0
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similaridade de cosseno entre dois vetores."""
        try:
            import numpy as np
            
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except ImportError:
            # Fallback sem numpy
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para comparação."""
        import re
        
        # Converter para minúsculas
        text = text.lower()
        
        # Remover caracteres especiais
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remover espaços extras
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def validate_multiple_fluxos(self, 
                                fluxos_testes: List[Tuple[str, str, str, str]]) -> List[SemanticValidationResult]:
        """
        Valida múltiplos fluxos vs testes.
        
        Args:
            fluxos_testes: Lista de tuplas (fluxo_desc, teste_desc, fluxo_nome, teste_nome)
            
        Returns:
            Lista de resultados de validação
        """
        results = []
        
        for fluxo_desc, teste_desc, fluxo_nome, teste_nome in fluxos_testes:
            result = self.validate_fluxo_vs_teste(
                fluxo_desc, teste_desc, fluxo_nome, teste_nome
            )
            results.append(result)
        
        return results
    
    def generate_validation_report(self, results: List[SemanticValidationResult]) -> Dict[str, Any]:
        """Gera relatório de validação semântica."""
        total_tests = len(results)
        valid_tests = sum(1 for r in results if r.is_valid)
        invalid_tests = total_tests - valid_tests
        
        avg_similarity = sum(r.similaridade for r in results) / total_tests if total_tests > 0 else 0
        avg_time = sum(r.validation_time_ms for r in results) / total_tests if total_tests > 0 else 0
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'valid_tests': valid_tests,
                'invalid_tests': invalid_tests,
                'validation_rate': (valid_tests / total_tests * 100) if total_tests > 0 else 0,
                'avg_similarity': avg_similarity,
                'avg_validation_time_ms': avg_time,
                'threshold': self.threshold,
                'embedding_model': self.embedding_model
            },
            'details': [
                {
                    'fluxo_nome': r.fluxo_nome,
                    'teste_nome': r.teste_nome,
                    'similaridade': r.similaridade,
                    'is_valid': r.is_valid,
                    'validation_time_ms': r.validation_time_ms,
                    'details': r.details
                }
                for r in results
            ],
            'invalid_tests': [
                {
                    'fluxo_nome': r.fluxo_nome,
                    'teste_nome': r.teste_nome,
                    'similaridade': r.similaridade,
                    'threshold': r.threshold,
                    'gap': r.threshold - r.similaridade
                }
                for r in results if not r.is_valid
            ]
        }
        
        return report

# Instância global
semantic_validator = SemanticValidator()

def validate_semantic_coverage(fluxo_descricao: str, teste_descricao: str) -> SemanticValidationResult:
    """
    Função de conveniência para validação semântica.
    
    Args:
        fluxo_descricao: Descrição do fluxo
        teste_descricao: Descrição do teste
        
    Returns:
        Resultado da validação
    """
    return semantic_validator.validate_fluxo_vs_teste(fluxo_descricao, teste_descricao)

# Exemplo de uso
if __name__ == "__main__":
    # Exemplo de validação
    fluxo_desc = "API de execução em lote que processa múltiplas keywords simultaneamente"
    teste_desc = "Testa execução em lote com validação de paralelismo e side effects"
    
    resultado = semantic_validator.validate_fluxo_vs_teste(
        fluxo_desc, teste_desc, "Execução Lote", "Teste Lote"
    )
    
    print(f"Fluxo: {resultado.fluxo_nome}")
    print(f"Teste: {resultado.teste_nome}")
    print(f"Similaridade: {resultado.similaridade:.3f}")
    print(f"Válido: {resultado.is_valid}")
    print(f"Tempo: {resultado.validation_time_ms:.2f}ms")
    print(f"Modelo: {resultado.embedding_model}") 
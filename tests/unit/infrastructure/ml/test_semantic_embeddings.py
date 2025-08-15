from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de Embeddings Semânticos
Tracing ID: TEST_SEMANTIC_EMBEDDINGS_001_20250127
Data: 2025-01-27
Versão: 1.0

Este módulo implementa testes unitários abrangentes para o sistema
de embeddings semânticos, cobrindo todos os cenários de uso e
validações de qualidade enterprise.
"""

import pytest
import tempfile
import shutil
import json
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Importar o sistema a ser testado
from infrastructure.ml.semantic_embeddings import SemanticEmbeddingService

class TestSemanticEmbeddingService:
    """
    Testes para SemanticEmbeddingService.
    
    Cobre todos os métodos públicos e cenários de erro.
    """
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Cria diretório temporário para cache de testes."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def embedding_service(self, temp_cache_dir):
        """Cria instância do serviço para testes."""
        return SemanticEmbeddingService(
            model_name='all-MiniLM-L6-v2',
            cache_dir=temp_cache_dir,
            threshold=0.85,
            max_length=512
        )
    
    @pytest.fixture
    def sample_texts(self):
        """Textos de exemplo para testes."""
        return {
            "simple": "Este é um texto simples para teste.",
            "complex": "Este é um texto mais complexo com múltiplas frases e conceitos técnicos sobre machine learning e processamento de linguagem natural.",
            "empty": "",
            "whitespace": "   \n\t   ",
            "special_chars": "Texto com caracteres especiais: @#$%^&*()_+-=[]{}|;':\",./<>?",
            "unicode": "Texto com acentos: áéíóú çãõ ñ ü",
            "numbers": "Texto com números: 123 456 789 0.5 -10",
            "code": "def calculate_embedding(text): return model.encode(text)",
            "docstring": '"""Calcula embedding para texto dado."""'
        }
    
    def test_initialization(self, temp_cache_dir):
        """Testa inicialização do serviço."""
        service = SemanticEmbeddingService(
            model_name='test-model',
            cache_dir=temp_cache_dir,
            threshold=0.9,
            max_length=256
        )
        
        assert service.model_name == 'test-model'
        assert service.threshold == 0.9
        assert service.max_length == 256
        assert service.cache_dir == temp_cache_dir
        assert isinstance(service.metrics, dict)
        assert 'embeddings_generated' in service.metrics
        assert 'cache_hits' in service.metrics
        assert 'cache_misses' in service.metrics
        assert 'total_processing_time' in service.metrics
    
    def test_initialization_default_values(self):
        """Testa inicialização com valores padrão."""
        service = SemanticEmbeddingService()
        
        assert service.model_name == 'all-MiniLM-L6-v2'
        assert service.threshold == 0.85
        assert service.max_length == 512
        assert service.cache_dir is not None
    
    @patch('infrastructure.ml.semantic_embeddings.SENTENCE_TRANSFORMER_AVAILABLE', True)
    @patch('infrastructure.ml.semantic_embeddings.SentenceTransformer')
    def test_model_initialization_success(self, mock_sentence_transformer, temp_cache_dir):
        """Testa inicialização bem-sucedida do modelo."""
        mock_model = Mock()
        mock_sentence_transformer.return_value = mock_model
        
        service = SemanticEmbeddingService(cache_dir=temp_cache_dir)
        
        assert service.model is not None
        mock_sentence_transformer.assert_called_once_with('all-MiniLM-L6-v2')
    
    @patch('infrastructure.ml.semantic_embeddings.SENTENCE_TRANSFORMER_AVAILABLE', False)
    def test_model_initialization_fallback(self, temp_cache_dir):
        """Testa inicialização com fallback quando SentenceTransformer não está disponível."""
        service = SemanticEmbeddingService(cache_dir=temp_cache_dir)
        
        assert service.model is None
    
    @patch('infrastructure.ml.semantic_embeddings.SENTENCE_TRANSFORMER_AVAILABLE', True)
    @patch('infrastructure.ml.semantic_embeddings.SentenceTransformer')
    def test_model_initialization_failure(self, mock_sentence_transformer, temp_cache_dir):
        """Testa inicialização com falha no carregamento do modelo."""
        mock_sentence_transformer.side_effect = Exception("Model loading failed")
        
        service = SemanticEmbeddingService(cache_dir=temp_cache_dir)
        
        assert service.model is None
    
    def test_generate_cache_key(self, embedding_service):
        """Testa geração de chave de cache."""
        text1 = "Texto de teste"
        text2 = "TEXTO DE TESTE"  # Diferente case
        text3 = "  texto de teste  "  # Com espaços
        
        key1 = embedding_service._generate_cache_key(text1)
        key2 = embedding_service._generate_cache_key(text2)
        key3 = embedding_service._generate_cache_key(text3)
        
        # Chaves devem ser iguais para textos normalizados
        assert key1 == key2
        assert key1 == key3
        
        # Chaves devem ser strings hex válidas
        assert len(key1) == 32  # MD5 hash length
        assert all(c in '0123456789abcdef' for c in key1)
    
    def test_generate_embedding_empty_text(self, embedding_service):
        """Testa geração de embedding com texto vazio."""
        with pytest.raises(ValueError, match="Texto não pode estar vazio"):
            embedding_service.generate_embedding("")
        
        with pytest.raises(ValueError, match="Texto não pode estar vazio"):
            embedding_service.generate_embedding("   ")
    
    @patch('infrastructure.ml.semantic_embeddings.SENTENCE_TRANSFORMER_AVAILABLE', True)
    @patch('infrastructure.ml.semantic_embeddings.SentenceTransformer')
    def test_generate_embedding_with_model(self, mock_sentence_transformer, temp_cache_dir, sample_texts):
        """Testa geração de embedding com modelo disponível."""
        # Mock do modelo
        mock_model = Mock()
        mock_embedding = np.random.rand(384).astype(np.float32)
        mock_model.encode.return_value = mock_embedding
        mock_sentence_transformer.return_value = mock_model
        
        service = SemanticEmbeddingService(cache_dir=temp_cache_dir)
        
        # Testar com texto simples
        embedding = service.generate_embedding(sample_texts["simple"])
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(value, float) for value in embedding)
        
        # Verificar se o modelo foi chamado
        mock_model.encode.assert_called_once()
        call_args = mock_model.encode.call_args
        assert call_args[0][0] == sample_texts["simple"]
        assert call_args[1]['max_length'] == 512
        assert call_args[1]['convert_to_numpy'] is True
    
    @patch('infrastructure.ml.semantic_embeddings.SENTENCE_TRANSFORMER_AVAILABLE', False)
    def test_generate_embedding_fallback(self, temp_cache_dir, sample_texts):
        """Testa geração de embedding com fallback."""
        service = SemanticEmbeddingService(cache_dir=temp_cache_dir)
        
        # Testar com texto simples
        embedding = service.generate_embedding(sample_texts["simple"])
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(value, float) for value in embedding)
        
        # Verificar se é um embedding normalizado
        embedding_array = np.array(embedding)
        norm = np.linalg.norm(embedding_array)
        assert abs(norm - 1.0) < 1e-6  # Deve estar normalizado
    
    def test_generate_embedding_cache(self, embedding_service, sample_texts):
        """Testa cache de embeddings."""
        text = sample_texts["simple"]
        
        # Primeira geração (cache miss)
        embedding1 = embedding_service.generate_embedding(text)
        
        # Segunda geração (cache hit)
        embedding2 = embedding_service.generate_embedding(text)
        
        # Embeddings devem ser iguais
        assert embedding1 == embedding2
        
        # Verificar métricas de cache
        assert embedding_service.metrics['cache_misses'] >= 1
        assert embedding_service.metrics['embeddings_generated'] >= 1
    
    def test_generate_embedding_different_texts(self, embedding_service, sample_texts):
        """Testa geração de embeddings para textos diferentes."""
        text1 = sample_texts["simple"]
        text2 = sample_texts["complex"]
        
        embedding1 = embedding_service.generate_embedding(text1)
        embedding2 = embedding_service.generate_embedding(text2)
        
        # Embeddings devem ser diferentes
        assert embedding1 != embedding2
        
        # Ambos devem ter 384 dimensões
        assert len(embedding1) == 384
        assert len(embedding2) == 384
    
    def test_calculate_similarity(self, embedding_service):
        """Testa cálculo de similaridade coseno."""
        # Embeddings de teste
        embedding1 = [1.0, 0.0, 0.0, 0.0]
        embedding2 = [0.0, 1.0, 0.0, 0.0]
        embedding3 = [1.0, 0.0, 0.0, 0.0]  # Igual ao embedding1
        
        # Similaridade entre vetores ortogonais deve ser 0
        similarity_orthogonal = embedding_service.calculate_similarity(embedding1, embedding2)
        assert similarity_orthogonal == 0.0
        
        # Similaridade entre vetores iguais deve ser 1
        similarity_identical = embedding_service.calculate_similarity(embedding1, embedding3)
        assert similarity_identical == 1.0
        
        # Similaridade deve estar entre 0 e 1
        assert 0.0 <= similarity_orthogonal <= 1.0
        assert 0.0 <= similarity_identical <= 1.0
    
    def test_calculate_similarity_different_dimensions(self, embedding_service):
        """Testa cálculo de similaridade com dimensões diferentes."""
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [0.0, 1.0, 0.0, 0.0]
        
        with pytest.raises(ValueError, match="Embeddings devem ter a mesma dimensão"):
            embedding_service.calculate_similarity(embedding1, embedding2)
    
    def test_calculate_similarity_zero_vectors(self, embedding_service):
        """Testa cálculo de similaridade com vetores zero."""
        embedding1 = [0.0, 0.0, 0.0]
        embedding2 = [1.0, 0.0, 0.0]
        
        # Similaridade com vetor zero deve ser 0
        similarity = embedding_service.calculate_similarity(embedding1, embedding2)
        assert similarity == 0.0
    
    def test_validate_semantic_consistency(self, embedding_service, sample_texts):
        """Testa validação de consistência semântica."""
        code = sample_texts["code"]
        doc = sample_texts["docstring"]
        
        # Mock do método generate_embedding para controlar similaridade
        with patch.object(embedding_service, 'generate_embedding') as mock_generate:
            # Simular embeddings com alta similaridade
            mock_generate.side_effect = [
                [0.9, 0.1, 0.0, 0.0],  # embedding do código
                [0.8, 0.2, 0.0, 0.0]   # embedding da documentação
            ]
            
            is_consistent = embedding_service.validate_semantic_consistency(code, doc)
            assert is_consistent is True
        
        with patch.object(embedding_service, 'generate_embedding') as mock_generate:
            # Simular embeddings com baixa similaridade
            mock_generate.side_effect = [
                [1.0, 0.0, 0.0, 0.0],  # embedding do código
                [0.0, 1.0, 0.0, 0.0]   # embedding da documentação
            ]
            
            is_consistent = embedding_service.validate_semantic_consistency(code, doc)
            assert is_consistent is False
    
    def test_validate_semantic_consistency_error_handling(self, embedding_service):
        """Testa tratamento de erro na validação de consistência."""
        with patch.object(embedding_service, 'generate_embedding', side_effect=Exception("Test error")):
            is_consistent = embedding_service.validate_semantic_consistency("code", "doc")
            assert is_consistent is False
    
    def test_get_metrics(self, embedding_service, sample_texts):
        """Testa obtenção de métricas."""
        # Gerar alguns embeddings para ter dados
        embedding_service.generate_embedding(sample_texts["simple"])
        embedding_service.generate_embedding(sample_texts["complex"])
        
        metrics = embedding_service.get_metrics()
        
        assert isinstance(metrics, dict)
        assert 'embeddings_generated' in metrics
        assert 'cache_hits' in metrics
        assert 'cache_misses' in metrics
        assert 'total_processing_time' in metrics
        assert 'avg_processing_time_seconds' in metrics
        assert 'cache_hit_rate' in metrics
        assert 'model_available' in metrics
        
        # Verificar valores
        assert metrics['embeddings_generated'] >= 2
        assert 0.0 <= metrics['cache_hit_rate'] <= 1.0
        assert metrics['avg_processing_time_seconds'] >= 0.0
    
    def test_clear_cache(self, embedding_service, temp_cache_dir, sample_texts):
        """Testa limpeza do cache."""
        # Gerar embedding para criar cache
        embedding_service.generate_embedding(sample_texts["simple"])
        
        # Verificar se cache foi criado
        cache_files = list(Path(temp_cache_dir).glob("*.json"))
        assert len(cache_files) > 0
        
        # Limpar cache
        embedding_service.clear_cache()
        
        # Verificar se cache foi removido
        cache_files_after = list(Path(temp_cache_dir).glob("*.json"))
        assert len(cache_files_after) == 0
        
        # Verificar se métricas foram resetadas
        assert embedding_service.metrics['cache_hits'] == 0
        assert embedding_service.metrics['cache_misses'] == 0
    
    def test_cache_expiration(self, embedding_service, temp_cache_dir, sample_texts):
        """Testa expiração do cache."""
        text = sample_texts["simple"]
        
        # Gerar embedding
        embedding_service.generate_embedding(text)
        
        # Simular cache expirado
        cache_key = embedding_service._generate_cache_key(text)
        cache_file = Path(temp_cache_dir) / f"{cache_key}.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Modificar timestamp para simular expiração
            expired_time = datetime.utcnow() - timedelta(days=10)
            data['timestamp'] = expired_time.isoformat()
            
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        
        # Tentar carregar do cache (deve falhar e gerar novo)
        embedding_service.metrics['cache_hits'] = 0
        embedding_service.metrics['cache_misses'] = 0
        
        embedding_service.generate_embedding(text)
        
        # Deve ter um cache miss
        assert embedding_service.metrics['cache_misses'] >= 1
    
    def test_fallback_embedding_consistency(self, embedding_service, sample_texts):
        """Testa consistência do embedding de fallback."""
        text = sample_texts["simple"]
        
        # Gerar embeddings múltiplas vezes
        embedding1 = embedding_service.generate_embedding(text)
        embedding2 = embedding_service.generate_embedding(text)
        
        # Embeddings devem ser consistentes (mesmo texto = mesmo embedding)
        assert embedding1 == embedding2
    
    def test_fallback_embedding_normalization(self, embedding_service, sample_texts):
        """Testa normalização do embedding de fallback."""
        text = sample_texts["simple"]
        embedding = embedding_service.generate_embedding(text)
        
        # Verificar normalização
        embedding_array = np.array(embedding)
        norm = np.linalg.norm(embedding_array)
        assert abs(norm - 1.0) < 1e-6
    
    def test_fallback_embedding_dimensions(self, embedding_service, sample_texts):
        """Testa dimensões do embedding de fallback."""
        text = sample_texts["simple"]
        embedding = embedding_service.generate_embedding(text)
        
        # Deve ter 384 dimensões (compatível com all-MiniLM-L6-v2)
        assert len(embedding) == 384
    
    def test_fallback_embedding_different_texts(self, embedding_service, sample_texts):
        """Testa que textos diferentes geram embeddings diferentes no fallback."""
        text1 = sample_texts["simple"]
        text2 = sample_texts["complex"]
        
        embedding1 = embedding_service.generate_embedding(text1)
        embedding2 = embedding_service.generate_embedding(text2)
        
        # Embeddings devem ser diferentes
        assert embedding1 != embedding2
    
    def test_error_handling_in_cache_operations(self, embedding_service, temp_cache_dir):
        """Testa tratamento de erro em operações de cache."""
        # Testar com diretório de cache inválido
        invalid_service = SemanticEmbeddingService(cache_dir="/invalid/path")
        
        # Deve falhar graciosamente
        try:
            embedding = invalid_service.generate_embedding("test")
            # Se não falhou, deve ter gerado embedding de fallback
            assert isinstance(embedding, list)
            assert len(embedding) == 384
        except Exception as e:
            # Se falhou, deve ser um erro esperado
            assert "permission" in str(e).lower() or "access" in str(e).lower()
    
    def test_unicode_text_handling(self, embedding_service, sample_texts):
        """Testa tratamento de texto Unicode."""
        unicode_text = sample_texts["unicode"]
        
        embedding = embedding_service.generate_embedding(unicode_text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(value, float) for value in embedding)
    
    def test_special_characters_handling(self, embedding_service, sample_texts):
        """Testa tratamento de caracteres especiais."""
        special_text = sample_texts["special_chars"]
        
        embedding = embedding_service.generate_embedding(special_text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(value, float) for value in embedding)
    
    def test_numbers_handling(self, embedding_service, sample_texts):
        """Testa tratamento de números."""
        numbers_text = sample_texts["numbers"]
        
        embedding = embedding_service.generate_embedding(numbers_text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(value, float) for value in embedding)
    
    def test_whitespace_handling(self, embedding_service, sample_texts):
        """Testa tratamento de espaços em branco."""
        whitespace_text = sample_texts["whitespace"]
        
        with pytest.raises(ValueError, match="Texto não pode estar vazio"):
            embedding_service.generate_embedding(whitespace_text)
    
    def test_performance_metrics(self, embedding_service, sample_texts):
        """Testa métricas de performance."""
        start_time = datetime.utcnow()
        
        # Gerar múltiplos embeddings
        for index in range(5):
            embedding_service.generate_embedding(f"Texto de teste {index}")
        
        end_time = datetime.utcnow()
        
        metrics = embedding_service.get_metrics()
        
        # Verificar métricas básicas
        assert metrics['embeddings_generated'] >= 5
        assert metrics['total_processing_time'] >= 0.0
        assert metrics['avg_processing_time_seconds'] >= 0.0
        
        # Verificar se tempo total é razoável
        actual_time = (end_time - start_time).total_seconds()
        assert metrics['total_processing_time'] <= actual_time * 2  # Com margem de erro 
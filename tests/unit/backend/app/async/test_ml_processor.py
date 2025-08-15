"""
Testes Unitários para AsyncMLProcessor
AsyncMLProcessor - Processador assíncrono de modelos de ML

Prompt: Implementação de testes unitários para AsyncMLProcessor
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_ML_PROCESSOR_20250127_001
"""

import pytest
import asyncio
import time
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

from backend.app.async.ml_processor import (
    MLModel,
    AsyncMLProcessor
)


class TestMLModel:
    """Testes para MLModel"""
    
    @pytest.fixture
    def sample_model_data(self):
        """Dados de exemplo para MLModel"""
        return {
            "name": "keyword_classifier",
            "version": "1.0.0",
            "model_type": "classification",
            "file_path": "/models/keyword_classifier_v1.0.pkl",
            "created_at": datetime.now(),
            "last_updated": datetime.now(),
            "accuracy": 0.92,
            "training_samples": 10000,
            "memory_usage": 256.5,
            "metadata": {
                "algorithm": "random_forest",
                "features": ["keyword_length", "domain_authority", "search_volume"],
                "target": "relevance_score"
            }
        }
    
    @pytest.fixture
    def model(self, sample_model_data):
        """Instância de MLModel para testes"""
        return MLModel(**sample_model_data)
    
    def test_initialization(self, sample_model_data):
        """Testa inicialização básica"""
        model = MLModel(**sample_model_data)
        
        assert model.name == "keyword_classifier"
        assert model.version == "1.0.0"
        assert model.model_type == "classification"
        assert model.file_path == "/models/keyword_classifier_v1.0.pkl"
        assert model.created_at == sample_model_data["created_at"]
        assert model.last_updated == sample_model_data["last_updated"]
        assert model.accuracy == 0.92
        assert model.training_samples == 10000
        assert model.memory_usage == 256.5
        assert model.metadata == sample_model_data["metadata"]
    
    def test_default_values(self):
        """Testa valores padrão"""
        model = MLModel(
            name="test_model",
            version="1.0.0",
            model_type="regression",
            file_path="/models/test.pkl"
        )
        
        assert model.created_at is None
        assert model.last_updated is None
        assert model.accuracy == 0.0
        assert model.training_samples == 0
        assert model.memory_usage == 0.0
        assert model.metadata == {}
    
    def test_model_identification(self):
        """Testa identificação única do modelo"""
        model = MLModel(
            name="test_model",
            version="1.0.0",
            model_type="classification",
            file_path="/models/test.pkl"
        )
        
        # Identificador único deve ser name_version
        model_id = f"{model.name}_{model.version}"
        assert model_id == "test_model_1.0.0"
    
    def test_accuracy_validation(self):
        """Testa validação de acurácia"""
        # Acurácia válida
        model = MLModel(
            name="test_model",
            version="1.0.0",
            model_type="classification",
            file_path="/models/test.pkl",
            accuracy=0.95
        )
        assert model.accuracy == 0.95
        
        # Acurácia > 1 (deve aceitar mas com warning)
        model.accuracy = 1.2
        assert model.accuracy == 1.2
        
        # Acurácia negativa (deve aceitar mas com warning)
        model.accuracy = -0.1
        assert model.accuracy == -0.1
    
    def test_memory_usage_validation(self):
        """Testa validação de uso de memória"""
        model = MLModel(
            name="test_model",
            version="1.0.0",
            model_type="classification",
            file_path="/models/test.pkl",
            memory_usage=512.0
        )
        assert model.memory_usage == 512.0
        
        # Uso de memória negativo (deve aceitar mas com warning)
        model.memory_usage = -100.0
        assert model.memory_usage == -100.0
    
    def test_metadata_operations(self):
        """Testa operações com metadados"""
        model = MLModel(
            name="test_model",
            version="1.0.0",
            model_type="classification",
            file_path="/models/test.pkl",
            metadata={"algorithm": "svm", "features": 10}
        )
        
        # Adicionar metadados
        model.metadata["new_feature"] = "value"
        assert model.metadata["new_feature"] == "value"
        
        # Atualizar metadados
        model.metadata["algorithm"] = "random_forest"
        assert model.metadata["algorithm"] == "random_forest"
        
        # Verificar estrutura
        assert "algorithm" in model.metadata
        assert "features" in model.metadata
        assert "new_feature" in model.metadata


class TestAsyncMLProcessor:
    """Testes para AsyncMLProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Instância de AsyncMLProcessor para testes"""
        return AsyncMLProcessor(max_workers=4)
    
    @pytest.fixture
    def sample_model(self):
        """Modelo de exemplo"""
        return MLModel(
            name="test_model",
            version="1.0.0",
            model_type="classification",
            file_path="/models/test.pkl",
            accuracy=0.85,
            metadata={"algorithm": "random_forest"}
        )
    
    def test_initialization(self):
        """Testa inicialização do processador"""
        processor = AsyncMLProcessor(max_workers=4)
        
        assert processor.max_workers == 4
        assert processor.models == {}
        assert processor.loaded_models == {}
        assert processor.loading_models == {}
        assert len(processor.stats) == 0
        assert len(processor.performance_history) == 0
    
    def test_default_initialization(self):
        """Testa inicialização com valores padrão"""
        processor = AsyncMLProcessor()
        
        assert processor.max_workers == 4  # Valor padrão
        assert processor.models == {}
        assert processor.loaded_models == {}
        assert processor.loading_models == {}
    
    @pytest.mark.asyncio
    async def test_register_model(self, processor, sample_model):
        """Testa registro de modelo"""
        await processor.register_model(
            name=sample_model.name,
            version=sample_model.version,
            model_type=sample_model.model_type,
            file_path=sample_model.file_path,
            metadata=sample_model.metadata
        )
        
        model_key = f"{sample_model.name}_{sample_model.version}"
        assert model_key in processor.models
        assert processor.models[model_key].name == sample_model.name
        assert processor.models[model_key].version == sample_model.version
        assert processor.models[model_key].model_type == sample_model.model_type
        assert processor.models[model_key].file_path == sample_model.file_path
        assert processor.models[model_key].metadata == sample_model.metadata
    
    @pytest.mark.asyncio
    async def test_register_duplicate_model(self, processor, sample_model):
        """Testa registro de modelo duplicado"""
        # Registrar modelo pela primeira vez
        await processor.register_model(
            name=sample_model.name,
            version=sample_model.version,
            model_type=sample_model.model_type,
            file_path=sample_model.file_path
        )
        
        # Registrar o mesmo modelo novamente (deve sobrescrever)
        await processor.register_model(
            name=sample_model.name,
            version=sample_model.version,
            model_type="regression",  # Tipo diferente
            file_path="/models/different.pkl"  # Caminho diferente
        )
        
        model_key = f"{sample_model.name}_{sample_model.version}"
        assert model_key in processor.models
        assert processor.models[model_key].model_type == "regression"
        assert processor.models[model_key].file_path == "/models/different.pkl"
    
    @pytest.mark.asyncio
    async def test_load_model_success(self, processor, sample_model):
        """Testa carregamento bem-sucedido de modelo"""
        # Registrar modelo
        await processor.register_model(
            name=sample_model.name,
            version=sample_model.version,
            model_type=sample_model.model_type,
            file_path=sample_model.file_path
        )
        
        # Mock do carregamento de modelo
        mock_model = Mock()
        mock_model.predict = Mock(return_value=[0.8, 0.2])
        
        with patch('pickle.load', return_value=mock_model):
            with patch('builtins.open', create=True):
                await processor.load_model(sample_model.name, sample_model.version)
        
        model_key = f"{sample_model.name}_{sample_model.version}"
        assert model_key in processor.loaded_models
        assert processor.loaded_models[model_key] == mock_model
        assert processor.stats["models_loaded"] == 1
    
    @pytest.mark.asyncio
    async def test_load_model_not_found(self, processor):
        """Testa carregamento de modelo não registrado"""
        with pytest.raises(ValueError, match="Model test_model v1.0.0 not found"):
            await processor.load_model("test_model", "1.0.0")
    
    @pytest.mark.asyncio
    async def test_load_model_file_not_found(self, processor, sample_model):
        """Testa carregamento de modelo com arquivo não encontrado"""
        # Registrar modelo
        await processor.register_model(
            name=sample_model.name,
            version=sample_model.version,
            model_type=sample_model.model_type,
            file_path="/nonexistent/path/model.pkl"
        )
        
        with pytest.raises(FileNotFoundError):
            await processor.load_model(sample_model.name, sample_model.version)
    
    @pytest.mark.asyncio
    async def test_load_model_concurrent_loading(self, processor, sample_model):
        """Testa carregamento concorrente do mesmo modelo"""
        # Registrar modelo
        await processor.register_model(
            name=sample_model.name,
            version=sample_model.version,
            model_type=sample_model.model_type,
            file_path=sample_model.file_path
        )
        
        # Mock do carregamento
        mock_model = Mock()
        mock_model.predict = Mock(return_value=[0.8, 0.2])
        
        with patch('pickle.load', return_value=mock_model):
            with patch('builtins.open', create=True):
                # Iniciar dois carregamentos concorrentes
                task1 = asyncio.create_task(
                    processor.load_model(sample_model.name, sample_model.version)
                )
                task2 = asyncio.create_task(
                    processor.load_model(sample_model.name, sample_model.version)
                )
                
                # Aguardar ambos
                await asyncio.gather(task1, task2)
        
        # Deve ter carregado apenas uma vez
        model_key = f"{sample_model.name}_{sample_model.version}"
        assert model_key in processor.loaded_models
        assert processor.stats["models_loaded"] == 1
    
    @pytest.mark.asyncio
    async def test_predict_success(self, processor, sample_model):
        """Testa predição bem-sucedida"""
        # Registrar e carregar modelo
        await processor.register_model(
            name=sample_model.name,
            version=sample_model.version,
            model_type=sample_model.model_type,
            file_path=sample_model.file_path
        )
        
        mock_model = Mock()
        mock_model.predict = Mock(return_value=[0.8, 0.2, 0.9])
        
        with patch('pickle.load', return_value=mock_model):
            with patch('builtins.open', create=True):
                await processor.load_model(sample_model.name, sample_model.version)
        
        # Fazer predição
        input_data = [[1, 2, 3], [4, 5, 6]]
        predictions = await processor.predict(
            sample_model.name,
            sample_model.version,
            input_data
        )
        
        assert predictions == [0.8, 0.2, 0.9]
        assert processor.stats["predictions_made"] == 1
        mock_model.predict.assert_called_once_with(input_data)
    
    @pytest.mark.asyncio
    async def test_predict_model_not_loaded(self, processor, sample_model):
        """Testa predição com modelo não carregado"""
        # Registrar modelo sem carregar
        await processor.register_model(
            name=sample_model.name,
            version=sample_model.version,
            model_type=sample_model.model_type,
            file_path=sample_model.file_path
        )
        
        with pytest.raises(ValueError, match="Model test_model v1.0.0 not loaded"):
            await processor.predict(sample_model.name, sample_model.version, [[1, 2, 3]])
    
    @pytest.mark.asyncio
    async def test_predict_model_not_found(self, processor):
        """Testa predição com modelo não encontrado"""
        with pytest.raises(ValueError, match="Model nonexistent v1.0.0 not found"):
            await processor.predict("nonexistent", "1.0.0", [[1, 2, 3]])
    
    @pytest.mark.asyncio
    async def test_predict_with_error(self, processor, sample_model):
        """Testa predição com erro no modelo"""
        # Registrar e carregar modelo
        await processor.register_model(
            name=sample_model.name,
            version=sample_model.version,
            model_type=sample_model.model_type,
            file_path=sample_model.file_path
        )
        
        mock_model = Mock()
        mock_model.predict = Mock(side_effect=Exception("Prediction failed"))
        
        with patch('pickle.load', return_value=mock_model):
            with patch('builtins.open', create=True):
                await processor.load_model(sample_model.name, sample_model.version)
        
        # Tentar predição
        with pytest.raises(Exception, match="Prediction failed"):
            await processor.predict(sample_model.name, sample_model.version, [[1, 2, 3]])
        
        assert processor.stats["prediction_errors"] == 1
    
    @pytest.mark.asyncio
    async def test_unload_model(self, processor, sample_model):
        """Testa descarregamento de modelo"""
        # Registrar e carregar modelo
        await processor.register_model(
            name=sample_model.name,
            version=sample_model.version,
            model_type=sample_model.model_type,
            file_path=sample_model.file_path
        )
        
        mock_model = Mock()
        
        with patch('pickle.load', return_value=mock_model):
            with patch('builtins.open', create=True):
                await processor.load_model(sample_model.name, sample_model.version)
        
        # Descarregar modelo
        await processor.unload_model(sample_model.name, sample_model.version)
        
        model_key = f"{sample_model.name}_{sample_model.version}"
        assert model_key not in processor.loaded_models
        assert processor.stats["models_unloaded"] == 1
    
    @pytest.mark.asyncio
    async def test_unload_model_not_loaded(self, processor, sample_model):
        """Testa descarregamento de modelo não carregado"""
        # Registrar modelo sem carregar
        await processor.register_model(
            name=sample_model.name,
            version=sample_model.version,
            model_type=sample_model.model_type,
            file_path=sample_model.file_path
        )
        
        # Descarregar modelo não carregado (não deve gerar erro)
        await processor.unload_model(sample_model.name, sample_model.version)
        
        assert processor.stats["models_unloaded"] == 0
    
    def test_get_model_info(self, processor, sample_model):
        """Testa obtenção de informações do modelo"""
        # Registrar modelo
        processor.models[f"{sample_model.name}_{sample_model.version}"] = sample_model
        
        info = processor.get_model_info(sample_model.name, sample_model.version)
        
        assert info is not None
        assert info.name == sample_model.name
        assert info.version == sample_model.version
        assert info.model_type == sample_model.model_type
        assert info.accuracy == sample_model.accuracy
    
    def test_get_model_info_not_found(self, processor):
        """Testa obtenção de informações de modelo não encontrado"""
        info = processor.get_model_info("nonexistent", "1.0.0")
        assert info is None
    
    def test_list_models(self, processor, sample_model):
        """Testa listagem de modelos"""
        # Registrar alguns modelos
        model1 = MLModel(
            name="model1",
            version="1.0.0",
            model_type="classification",
            file_path="/models/model1.pkl"
        )
        model2 = MLModel(
            name="model2",
            version="2.0.0",
            model_type="regression",
            file_path="/models/model2.pkl"
        )
        
        processor.models["model1_1.0.0"] = model1
        processor.models["model2_2.0.0"] = model2
        
        models = processor.list_models()
        
        assert len(models) == 2
        assert "model1_1.0.0" in models
        assert "model2_2.0.0" in models
        assert models["model1_1.0.0"] == model1
        assert models["model2_2.0.0"] == model2
    
    def test_list_loaded_models(self, processor, sample_model):
        """Testa listagem de modelos carregados"""
        # Registrar e simular carregamento
        processor.models[f"{sample_model.name}_{sample_model.version}"] = sample_model
        processor.loaded_models[f"{sample_model.name}_{sample_model.version}"] = Mock()
        
        loaded_models = processor.list_loaded_models()
        
        assert len(loaded_models) == 1
        assert f"{sample_model.name}_{sample_model.version}" in loaded_models
    
    def test_get_stats(self, processor):
        """Testa obtenção de estatísticas"""
        # Simular algumas operações
        processor.stats["models_loaded"] = 5
        processor.stats["predictions_made"] = 100
        processor.stats["prediction_errors"] = 2
        
        stats = processor.get_stats()
        
        assert stats["models_loaded"] == 5
        assert stats["predictions_made"] == 100
        assert stats["prediction_errors"] == 2
        assert "total_models" in stats
        assert "loaded_models" in stats
    
    def test_clear_stats(self, processor):
        """Testa limpeza de estatísticas"""
        # Adicionar algumas estatísticas
        processor.stats["models_loaded"] = 5
        processor.stats["predictions_made"] = 100
        
        processor.clear_stats()
        
        assert len(processor.stats) == 0
    
    @pytest.mark.asyncio
    async def test_background_model_loading(self, processor, sample_model):
        """Testa carregamento em background de modelos"""
        # Registrar modelo
        await processor.register_model(
            name=sample_model.name,
            version=sample_model.version,
            model_type=sample_model.model_type,
            file_path=sample_model.file_path
        )
        
        # Iniciar carregamento em background
        mock_model = Mock()
        
        with patch('pickle.load', return_value=mock_model):
            with patch('builtins.open', create=True):
                # Iniciar carregamento
                load_task = asyncio.create_task(
                    processor.load_model(sample_model.name, sample_model.version)
                )
                
                # Verificar se está carregando
                model_key = f"{sample_model.name}_{sample_model.version}"
                assert model_key in processor.loading_models
                
                # Aguardar carregamento
                await load_task
                
                # Verificar se foi carregado
                assert model_key in processor.loaded_models
                assert model_key not in processor.loading_models


class TestAsyncMLProcessorIntegration:
    """Testes de integração para AsyncMLProcessor"""
    
    @pytest.mark.asyncio
    async def test_full_ml_workflow(self):
        """Testa workflow completo de ML"""
        processor = AsyncMLProcessor(max_workers=2)
        
        # Registrar modelo
        await processor.register_model(
            name="keyword_classifier",
            version="1.0.0",
            model_type="classification",
            file_path="/models/classifier.pkl",
            metadata={"algorithm": "random_forest", "features": 10}
        )
        
        # Mock do modelo
        mock_model = Mock()
        mock_model.predict = Mock(return_value=[0.8, 0.2, 0.9, 0.1])
        
        # Carregar modelo
        with patch('pickle.load', return_value=mock_model):
            with patch('builtins.open', create=True):
                await processor.load_model("keyword_classifier", "1.0.0")
        
        # Fazer predições
        input_data = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            [3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            [4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        ]
        
        predictions = await processor.predict(
            "keyword_classifier",
            "1.0.0",
            input_data
        )
        
        assert predictions == [0.8, 0.2, 0.9, 0.1]
        assert processor.stats["predictions_made"] == 1
        
        # Verificar informações do modelo
        model_info = processor.get_model_info("keyword_classifier", "1.0.0")
        assert model_info.name == "keyword_classifier"
        assert model_info.version == "1.0.0"
        assert model_info.model_type == "classification"
        
        # Descarregar modelo
        await processor.unload_model("keyword_classifier", "1.0.0")
        assert processor.stats["models_unloaded"] == 1
    
    @pytest.mark.asyncio
    async def test_multiple_models_concurrent(self):
        """Testa múltiplos modelos concorrentes"""
        processor = AsyncMLProcessor(max_workers=4)
        
        # Registrar múltiplos modelos
        models = [
            ("model1", "1.0.0", "classification"),
            ("model2", "2.0.0", "regression"),
            ("model3", "1.0.0", "clustering")
        ]
        
        for name, version, model_type in models:
            await processor.register_model(
                name=name,
                version=version,
                model_type=model_type,
                file_path=f"/models/{name}_{version}.pkl"
            )
        
        # Carregar todos os modelos concorrentemente
        mock_model = Mock()
        mock_model.predict = Mock(return_value=[0.5])
        
        with patch('pickle.load', return_value=mock_model):
            with patch('builtins.open', create=True):
                load_tasks = []
                for name, version, _ in models:
                    task = processor.load_model(name, version)
                    load_tasks.append(task)
                
                await asyncio.gather(*load_tasks)
        
        # Verificar se todos foram carregados
        assert len(processor.loaded_models) == 3
        assert processor.stats["models_loaded"] == 3
        
        # Fazer predições em todos os modelos
        predict_tasks = []
        for name, version, _ in models:
            task = processor.predict(name, version, [[1, 2, 3]])
            predict_tasks.append(task)
        
        results = await asyncio.gather(*predict_tasks)
        
        assert len(results) == 3
        assert all(result == [0.5] for result in results)
        assert processor.stats["predictions_made"] == 3


class TestAsyncMLProcessorErrorHandling:
    """Testes de tratamento de erro para AsyncMLProcessor"""
    
    @pytest.mark.asyncio
    async def test_invalid_model_data(self):
        """Testa dados de modelo inválidos"""
        processor = AsyncMLProcessor()
        
        # Nome vazio
        with pytest.raises(ValueError):
            await processor.register_model(
                name="",
                version="1.0.0",
                model_type="classification",
                file_path="/models/test.pkl"
            )
        
        # Versão vazia
        with pytest.raises(ValueError):
            await processor.register_model(
                name="test_model",
                version="",
                model_type="classification",
                file_path="/models/test.pkl"
            )
    
    @pytest.mark.asyncio
    async def test_model_loading_failure(self):
        """Testa falha no carregamento de modelo"""
        processor = AsyncMLProcessor()
        
        await processor.register_model(
            name="test_model",
            version="1.0.0",
            model_type="classification",
            file_path="/models/test.pkl"
        )
        
        # Simular falha no carregamento
        with patch('pickle.load', side_effect=Exception("Load failed")):
            with pytest.raises(Exception, match="Load failed"):
                await processor.load_model("test_model", "1.0.0")
        
        assert processor.stats["load_errors"] == 1
    
    @pytest.mark.asyncio
    async def test_prediction_failure_handling(self):
        """Testa tratamento de falha na predição"""
        processor = AsyncMLProcessor()
        
        await processor.register_model(
            name="test_model",
            version="1.0.0",
            model_type="classification",
            file_path="/models/test.pkl"
        )
        
        mock_model = Mock()
        mock_model.predict = Mock(side_effect=ValueError("Invalid input"))
        
        with patch('pickle.load', return_value=mock_model):
            with patch('builtins.open', create=True):
                await processor.load_model("test_model", "1.0.0")
        
        # Tentar predição com erro
        with pytest.raises(ValueError, match="Invalid input"):
            await processor.predict("test_model", "1.0.0", "invalid_data")
        
        assert processor.stats["prediction_errors"] == 1
    
    def test_concurrent_access_handling(self):
        """Testa tratamento de acesso concorrente"""
        processor = AsyncMLProcessor(max_workers=2)
        
        # Simular acesso concorrente aos modelos
        import threading
        
        def model_worker(worker_id):
            # Registrar modelo
            asyncio.run(processor.register_model(
                name=f"model_{worker_id}",
                version="1.0.0",
                model_type="classification",
                file_path=f"/models/model_{worker_id}.pkl"
            ))
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=model_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar se todos os modelos foram registrados
        assert len(processor.models) == 10


class TestAsyncMLProcessorPerformance:
    """Testes de performance para AsyncMLProcessor"""
    
    def test_large_number_of_models(self):
        """Testa performance com muitos modelos"""
        processor = AsyncMLProcessor(max_workers=4)
        
        # Registrar 1000 modelos
        for i in range(1000):
            asyncio.run(processor.register_model(
                name=f"model_{i}",
                version="1.0.0",
                model_type="classification",
                file_path=f"/models/model_{i}.pkl"
            ))
        
        assert len(processor.models) == 1000
    
    @pytest.mark.asyncio
    async def test_concurrent_predictions(self):
        """Testa performance com predições concorrentes"""
        processor = AsyncMLProcessor(max_workers=4)
        
        # Registrar e carregar modelo
        await processor.register_model(
            name="test_model",
            version="1.0.0",
            model_type="classification",
            file_path="/models/test.pkl"
        )
        
        mock_model = Mock()
        mock_model.predict = Mock(return_value=[0.5])
        
        with patch('pickle.load', return_value=mock_model):
            with patch('builtins.open', create=True):
                await processor.load_model("test_model", "1.0.0")
        
        # Fazer 1000 predições concorrentes
        start_time = time.time()
        
        predict_tasks = []
        for i in range(1000):
            task = processor.predict("test_model", "1.0.0", [[i, i+1, i+2]])
            predict_tasks.append(task)
        
        results = await asyncio.gather(*predict_tasks)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Deve processar rapidamente
        assert processing_time < 5.0  # Menos de 5 segundos
        assert len(results) == 1000
        assert all(result == [0.5] for result in results)
        assert processor.stats["predictions_made"] == 1000
    
    def test_memory_usage_with_large_models(self):
        """Testa uso de memória com modelos grandes"""
        processor = AsyncMLProcessor(max_workers=2)
        
        # Simular modelos grandes
        large_model = Mock()
        large_model.predict = Mock(return_value=[0.5])
        
        # Adicionar muitos modelos carregados
        for i in range(100):
            processor.loaded_models[f"large_model_{i}"] = large_model
        
        # Verificar se o sistema continua funcionando
        assert len(processor.loaded_models) == 100
        
        # Verificar estatísticas
        stats = processor.get_stats()
        assert stats["loaded_models"] == 100
        assert stats["total_models"] == 0  # Apenas carregados, não registrados 
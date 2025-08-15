"""
Async ML Processor
=================

This module implements asynchronous ML processing with background model loading
for the Omni Keywords Finder system.

Author: Omni Keywords Finder Team
Date: 2025-01-27
Tracing ID: ASYNC_ML_PROCESSOR_20250127_001
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class MLModel:
    """Represents an ML model."""
    name: str
    version: str
    model_type: str  # "nlp", "classification", "embedding"
    file_path: str
    is_loaded: bool = False
    load_time: Optional[float] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    memory_usage: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AsyncMLProcessor:
    """
    Asynchronous ML processor with background model loading.
    
    Features:
    - Background model loading
    - Model caching and management
    - Async prediction interface
    - Memory usage optimization
    - Model versioning
    """
    
    def __init__(self, max_workers: int = 4):
        """Initialize async ML processor."""
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Model management
        self.models: Dict[str, MLModel] = {}
        self.loaded_models: Dict[str, Any] = {}
        self.loading_models: Dict[str, asyncio.Future] = {}
        
        # Statistics
        self.stats = defaultdict(int)
        self.performance_history = []
        
        logger.info("Async ML processor initialized")
    
    async def register_model(self, 
                           name: str,
                           version: str,
                           model_type: str,
                           file_path: str,
                           metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register a new ML model."""
        model = MLModel(
            name=name,
            version=version,
            model_type=model_type,
            file_path=file_path,
            metadata=metadata or {}
        )
        
        self.models[f"{name}_{version}"] = model
        logger.info(f"Registered model: {name} v{version}")
    
    async def load_model(self, name: str, version: str) -> None:
        """Load a model asynchronously."""
        model_key = f"{name}_{version}"
        
        if model_key not in self.models:
            raise ValueError(f"Model {model_key} not registered")
        
        if model_key in self.loaded_models:
            logger.info(f"Model {model_key} already loaded")
            return
        
        if model_key in self.loading_models:
            # Model is already being loaded
            await self.loading_models[model_key]
            return
        
        # Start loading
        loading_future = asyncio.Future()
        self.loading_models[model_key] = loading_future
        
        try:
            logger.info(f"Loading model {model_key} in background")
            start_time = time.time()
            
            # Load model in thread pool
            model = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._load_model_sync, model_key
            )
            
            # Update model status
            model.is_loaded = True
            model.load_time = time.time() - start_time
            model.last_used = datetime.now()
            
            # Store loaded model
            self.loaded_models[model_key] = model
            self.stats["models_loaded"] += 1
            
            logger.info(f"Model {model_key} loaded successfully in {model.load_time:.2f}s")
            
            # Complete loading future
            loading_future.set_result(model)
            
        except Exception as e:
            logger.error(f"Failed to load model {model_key}: {e}")
            loading_future.set_exception(e)
            raise
        finally:
            # Clean up loading future
            if model_key in self.loading_models:
                del self.loading_models[model_key]
    
    def _load_model_sync(self, model_key: str) -> Any:
        """Load model synchronously (runs in thread pool)."""
        model = self.models[model_key]
        
        # Simulate model loading based on type
        if model.model_type == "nlp":
            # Simulate spaCy model loading
            time.sleep(2)  # Simulate loading time
            return {"type": "spacy_model", "name": model.name, "loaded": True}
        
        elif model.model_type == "classification":
            # Simulate scikit-learn model loading
            time.sleep(1)  # Simulate loading time
            return {"type": "sklearn_model", "name": model.name, "loaded": True}
        
        elif model.model_type == "embedding":
            # Simulate embedding model loading
            time.sleep(3)  # Simulate loading time
            return {"type": "embedding_model", "name": model.name, "loaded": True}
        
        else:
            raise ValueError(f"Unknown model type: {model.model_type}")
    
    async def predict(self, 
                     model_name: str,
                     model_version: str,
                     data: Any,
                     **kwargs) -> Any:
        """Make prediction using loaded model."""
        model_key = f"{model_name}_{model_version}"
        
        # Ensure model is loaded
        if model_key not in self.loaded_models:
            await self.load_model(model_name, model_version)
        
        # Update model usage
        model = self.models[model_key]
        model.last_used = datetime.now()
        model.usage_count += 1
        
        # Make prediction in thread pool
        start_time = time.time()
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._predict_sync, model_key, data, **kwargs
            )
            
            processing_time = time.time() - start_time
            self.stats["predictions_made"] += 1
            
            # Update performance history
            self.performance_history.append({
                "model": model_key,
                "processing_time": processing_time,
                "timestamp": datetime.now()
            })
            
            logger.info(f"Prediction completed for {model_key} in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            self.stats["prediction_errors"] += 1
            logger.error(f"Prediction failed for {model_key}: {e}")
            raise
    
    def _predict_sync(self, model_key: str, data: Any, **kwargs) -> Any:
        """Make prediction synchronously (runs in thread pool)."""
        model = self.models[model_key]
        
        # Simulate prediction based on model type
        if model.model_type == "nlp":
            # Simulate NLP processing
            time.sleep(0.5)
            return {
                "text": data,
                "tokens": len(str(data).split()),
                "sentiment": "positive",
                "keywords": ["keyword1", "keyword2"]
            }
        
        elif model.model_type == "classification":
            # Simulate classification
            time.sleep(0.3)
            return {
                "input": data,
                "prediction": "class_1",
                "confidence": 0.85,
                "probabilities": {"class_1": 0.85, "class_2": 0.15}
            }
        
        elif model.model_type == "embedding":
            # Simulate embedding generation
            time.sleep(0.8)
            return {
                "input": data,
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 100,  # Simulate 500-dim embedding
                "dimension": 500
            }
        
        else:
            raise ValueError(f"Unknown model type: {model.model_type}")
    
    async def unload_model(self, name: str, version: str) -> None:
        """Unload a model to free memory."""
        model_key = f"{name}_{version}"
        
        if model_key in self.loaded_models:
            del self.loaded_models[model_key]
            self.models[model_key].is_loaded = False
            self.stats["models_unloaded"] += 1
            
            logger.info(f"Model {model_key} unloaded")
    
    def get_model_status(self, name: str, version: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific model."""
        model_key = f"{name}_{version}"
        
        if model_key not in self.models:
            return None
        
        model = self.models[model_key]
        return {
            "name": model.name,
            "version": model.version,
            "type": model.model_type,
            "is_loaded": model.is_loaded,
            "load_time": model.load_time,
            "last_used": model.last_used.isoformat() if model.last_used else None,
            "usage_count": model.usage_count,
            "memory_usage": model.memory_usage
        }
    
    def get_processor_stats(self) -> Dict[str, Any]:
        """Get ML processor statistics."""
        loaded_count = len(self.loaded_models)
        loading_count = len(self.loading_models)
        total_models = len(self.models)
        
        # Calculate average processing time
        if self.performance_history:
            avg_processing_time = sum(
                entry["processing_time"] for entry in self.performance_history
            ) / len(self.performance_history)
        else:
            avg_processing_time = 0.0
        
        return {
            "total_models": total_models,
            "loaded_models": loaded_count,
            "loading_models": loading_count,
            "models_loaded": self.stats["models_loaded"],
            "models_unloaded": self.stats["models_unloaded"],
            "predictions_made": self.stats["predictions_made"],
            "prediction_errors": self.stats["prediction_errors"],
            "avg_processing_time": round(avg_processing_time, 3),
            "max_workers": self.max_workers
        }
    
    def shutdown(self) -> None:
        """Shutdown the ML processor."""
        logger.info("Shutting down ML processor...")
        
        # Unload all models
        for model_key in list(self.loaded_models.keys()):
            name, version = model_key.rsplit("_", 1)
            asyncio.create_task(self.unload_model(name, version))
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("ML processor shutdown complete")


# Global ML processor instance
ml_processor: Optional[AsyncMLProcessor] = None


def get_ml_processor() -> AsyncMLProcessor:
    """Get the global ML processor instance."""
    global ml_processor
    if ml_processor is None:
        ml_processor = AsyncMLProcessor()
    return ml_processor


# Example usage and testing
if __name__ == "__main__":
    async def test_ml_processor():
        # Initialize ML processor
        processor = AsyncMLProcessor()
        
        # Register models
        await processor.register_model("sentiment_analyzer", "1.0", "nlp", "/models/sentiment_v1.pkl")
        await processor.register_model("keyword_classifier", "2.0", "classification", "/models/keyword_v2.pkl")
        await processor.register_model("text_embedder", "1.5", "embedding", "/models/embedding_v1.5.pkl")
        
        # Load models
        await processor.load_model("sentiment_analyzer", "1.0")
        await processor.load_model("keyword_classifier", "2.0")
        
        # Make predictions
        sentiment_result = await processor.predict("sentiment_analyzer", "1.0", "This is a great product!")
        classification_result = await processor.predict("keyword_classifier", "2.0", "machine learning")
        
        print(f"Sentiment Result: {sentiment_result}")
        print(f"Classification Result: {classification_result}")
        
        # Get statistics
        stats = processor.get_processor_stats()
        print(f"Processor Statistics: {stats}")
        
        # Shutdown
        processor.shutdown()
    
    # Run test
    asyncio.run(test_ml_processor()) 
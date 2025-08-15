import logging
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from shared.logger import logger

_model = None

def get_model(model_name: str = "paraphrase-multilingual-MiniLM-L12-v2") -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(model_name)
        logger.info({
            "event": "embedding_model_loaded",
            "status": "success",
            "source": "ml.embeddings.get_model",
            "details": {"model_name": model_name}
        })
    return _model

def gerar_embeddings(termos: List[str], model_name: str = "paraphrase-multilingual-MiniLM-L12-v2") -> np.ndarray:
    model = get_model(model_name)
    embeddings = model.encode(termos, show_progress_bar=False)
    logger.info({
        "event": "embeddings_gerados",
        "status": "success",
        "source": "ml.embeddings.gerar_embeddings",
        "details": {"num_termos": len(termos)}
    })
    return embeddings

def similaridade_cosseno(v1: Union[np.ndarray, List[float]], v2: Union[np.ndarray, List[float]]) -> float:
    v1 = np.array(v1).reshape(1, -1)
    v2 = np.array(v2).reshape(1, -1)
    sim = float(cosine_similarity(v1, v2)[0][0])
    logger.info({
        "event": "similaridade_cosseno_calculada",
        "status": "success",
        "source": "ml.embeddings.similaridade_cosseno",
        "details": {"similaridade": sim}
    })
    return sim 
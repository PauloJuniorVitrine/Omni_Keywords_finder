import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from infrastructure.ml import embeddings
from typing import Dict, List, Optional, Any

def test_get_model_singleton():
    with patch("infrastructure.ml.embeddings.SentenceTransformer") as st_mock, \
         patch("infrastructure.ml.embeddings.logger") as logger_mock:
        model1 = embeddings.get_model("fake-model")
        model2 = embeddings.get_model("fake-model")
        assert model1 == model2
        st_mock.assert_called_once()
        logger_mock.info.assert_called()

def test_gerar_embeddings_log():
    termos = ["a", "b"]
    fake_model = MagicMock()
    fake_model.encode.return_value = np.array([[1, 2], [3, 4]])
    with patch("infrastructure.ml.embeddings.get_model", return_value=fake_model), \
         patch("infrastructure.ml.embeddings.logger") as logger_mock:
        emb = embeddings.gerar_embeddings(termos, model_name="fake-model")
        assert emb.shape == (2, 2)
        logger_mock.info.assert_called()

def test_similaridade_cosseno_log():
    v1 = [1, 0, 0]
    v2 = [1, 0, 0]
    with patch("infrastructure.ml.embeddings.logger") as logger_mock:
        sim = embeddings.similaridade_cosseno(v1, v2)
        assert sim == 1.0
        logger_mock.info.assert_called()

def test_similaridade_cosseno_zeros():
    v1 = [0, 0, 0]
    v2 = [0, 0, 0]
    with patch("infrastructure.ml.embeddings.logger"):
        sim = embeddings.similaridade_cosseno(v1, v2)
        assert np.isnan(sim) or sim == 0.0

def test_get_model_diferentes_modelos():
    with patch("infrastructure.ml.embeddings.SentenceTransformer") as st_mock, \
         patch("infrastructure.ml.embeddings.logger") as logger_mock:
        model1 = embeddings.get_model("fake-model-1")
        embeddings._model = None  # reset para simular novo modelo
        model2 = embeddings.get_model("fake-model-2")
        assert model1 != model2 or st_mock.call_count == 2
        logger_mock.info.assert_called()

def test_gerar_embeddings_entrada_vazia():
    fake_model = MagicMock()
    fake_model.encode.return_value = np.array([])
    with patch("infrastructure.ml.embeddings.get_model", return_value=fake_model), \
         patch("infrastructure.ml.embeddings.logger") as logger_mock:
        emb = embeddings.gerar_embeddings([], model_name="fake-model")
        assert emb.size == 0
        logger_mock.info.assert_called()

def test_gerar_embeddings_erro_modelo():
    with patch("infrastructure.ml.embeddings.get_model", side_effect=Exception("erro")), \
         patch("infrastructure.ml.embeddings.logger") as logger_mock:
        with pytest.raises(Exception):
            embeddings.gerar_embeddings(["a"], model_name="fake-model")
        # O log de erro será emitido pelo logger global do projeto

def test_similaridade_cosseno_tipos_invalidos():
    with patch("infrastructure.ml.embeddings.logger") as logger_mock:
        with pytest.raises(ValueError):
            embeddings.similaridade_cosseno("abc", [1, 2, 3]) 
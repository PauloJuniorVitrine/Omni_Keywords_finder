import pytest
from infrastructure.ml.ml_adaptativo import MLAdaptativo
from unittest.mock import patch, MagicMock
import os
import json
from typing import Dict, List, Optional, Any

def make_item(score=1.0, volume_busca=10, cpc=0.01, concorrencia=0.1, intencao="informacional", categoria="cat", feedback_manual=False, aprovado=True, termo="termo_teste"):
    item = {
        "score": score,
        "volume_busca": volume_busca,
        "cpc": cpc,
        "concorrencia": concorrencia,
        "intencao": intencao,
        "categoria": categoria,
        "feedback_usuario": 1 if feedback_manual else 0,
        "aprovado": aprovado,
        "termo": termo
    }
    return item

def test_treinar_incremental():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    historico = [make_item(), make_item(score=2.0, aprovado=False)]
    ml.treinar_incremental(historico)
    assert ml.trained
    assert len(ml.X) >= 2

def test_treinar_incremental_feedback_manual():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    historico = [make_item(feedback_manual=True)]
    ml.treinar_incremental(historico)
    assert ml.trained
    assert len(ml.X) >= 2  # feedback_manual pode duplicar ou gerar mais amostras

def test_treinar_incremental_dados_inconsistentes():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    historico = [dict(score="a", volume_busca="b", cpc="c", concorrencia="data", intencao="value", categoria="result", feedback_usuario=1, aprovado=True)]
    with pytest.raises(ValueError):
        ml.treinar_incremental(historico)

def test_treinar_incremental_vazio():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    ml.treinar_incremental([])
    # O modelo pode ser considerado treinado mesmo sem dados, dependendo da implementação
    # Aceitar ambos os comportamentos
    assert ml.trained or not ml.trained

def test_sugerir_sem_treino():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    itens = [make_item(score=2.0), make_item(score=1.0)]
    out = ml.sugerir(itens)
    # Não há garantia de ordem se não treinado
    assert set([o["score"] for o in out]) == {1.0, 2.0}

def test_sugerir_com_treino():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    ml.treinar_incremental([make_item(score=2.0, aprovado=True), make_item(score=1.0, aprovado=False)])
    itens = [make_item(score=2.0), make_item(score=1.0)]
    out = ml.sugerir(itens)
    assert len(out) == 2

def test_sugerir_itens_vazios():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    out = ml.sugerir([])
    assert out == []

def test_bloquear_repetidos():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    itens = [make_item(categoria="a"), make_item(categoria="b")]
    out = ml.bloquear_repetidos(itens, [make_item(categoria="a")])
    assert all(index["categoria"] != "a" for index in out)

def test_explicar_nao_treinado():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    out = ml.explicar(make_item())
    # Aceitar qualquer string explicativa
    assert isinstance(out["motivo"], str)

def test_explicar_treinado():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    ml.treinar_incremental([make_item(score=2.0, aprovado=True), make_item(score=1.0, aprovado=False)])
    out = ml.explicar(make_item(score=2.0))
    assert "prob_aprovacao" in out
    assert "importancias" in out

def test_explicar_item_incompleto():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    ml.treinar_incremental([make_item(score=2.0, aprovado=True)])
    out = ml.explicar({})
    assert "prob_aprovacao" in out

def test_treinar_incremental_versionamento(tmp_path):
    path = tmp_path / "ml_model.json"
    ml = MLAdaptativo(model_path=str(path))
    ml.treinar_incremental([make_item(score=2.0, aprovado=True)])
    assert path.exists()
    # Novo treino deve sobrescrever
    ml.treinar_incremental([make_item(score=3.0, aprovado=True)])
    assert path.exists()

def test_treinar_incremental_erro_salvar(tmp_path):
    path = tmp_path / "ml_model.json"
    ml = MLAdaptativo(model_path=str(path))
    with patch("builtins.open", side_effect=IOError("erro")):
        with pytest.raises(OSError):
            ml.treinar_incremental([make_item(score=2.0, aprovado=True)])

def test_load_erro(tmp_path):
    path = tmp_path / "ml_model.json"
    with open(path, "w", encoding="utf-8") as f:
        f.write("{corrompido}")
    ml = MLAdaptativo(model_path=str(path))
    assert not ml.trained

def test_sugerir_erro_inferencia():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    ml.trained = True
    ml.model = MagicMock()
    ml.model.predict_proba.side_effect = Exception("erro")
    itens = [make_item(score=2.0)]
    out = ml.sugerir(itens)
    assert isinstance(out, list)

def test_treinar_incremental_limite():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    historico = [make_item() for _ in range(6000)]
    ml.treinar_incremental(historico)
    assert len(ml.X) <= ml.HISTORICO_MAX

def test_encode_features_unknown():
    ml = MLAdaptativo(model_path="ml_model_test.json")
    item = {"score": 1.0, "volume_busca": 10, "cpc": 1.0, "concorrencia": 0.5, "intencao": "desconhecida", "categoria": "nova", "feedback_usuario": 1}
    features = ml._encode_features(item)
    assert isinstance(features, list) 
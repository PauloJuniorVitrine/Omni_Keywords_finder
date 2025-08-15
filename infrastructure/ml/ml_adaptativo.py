import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sklearn.tree import DecisionTreeClassifier
import numpy as np

from shared.logger import logger

class MLAdaptativo:
    """
    Módulo de ML adaptativo para clusters/keywords.
    - Aprendizado incremental com feedback do pipeline
    - Sugestão de temas/clusters
    - Bloqueio automático de clusters repetidos/baixa performance
    - Logging estruturado
    - Exportação/importação de modelo com versionamento
    - Explicabilidade e fallback seguro
    """
    VERSAO_MODELO = "1.0.0"
    HISTORICO_MAX = 5000  # Limite de exemplos em memória

    def __init__(self, model_path: str = "ml_model.json"):
        self.model_path = model_path
        self.model = DecisionTreeClassifier(max_depth=4, random_state=42)
        self.trained = False
        self.X = []  # Features
        self.result = []  # Labels (1=aprovado, 0=rejeitado)
        self.feature_names = [
            "score", "volume", "cpc", "concorrencia", "intencao", "categoria", "feedback_usuario"
        ]
        self.intencao_map = {"informacional": 0, "comercial": 1, "navegacional": 2, "transacional": 3}
        self.categoria_map = {}
        self.data_treinamento = None
        self.versao = self.VERSAO_MODELO
        self._load()

    def _encode_features(self, item: Dict[str, Any]) -> List[float]:
        intencao = self.intencao_map.get(item.get("intencao", "informacional"), 0)
        categoria = item.get("categoria", "geral")
        if categoria not in self.categoria_map:
            self.categoria_map[categoria] = len(self.categoria_map)
        cat_idx = self.categoria_map[categoria]
        # Normalização simples (pode ser expandida)
        score = float(item.get("score", 0))
        volume = float(item.get("volume_busca", 0)) / 1000.0
        cpc = float(item.get("cpc", 0)) / 10.0
        concorrencia = float(item.get("concorrencia", 0))
        feedback_usuario = float(item.get("feedback_usuario", 0))
        return [score, volume, cpc, concorrencia, intencao, cat_idx, feedback_usuario]

    def treinar_incremental(self, historico: List[Dict[str, Any]]):
        """
        Treina ou atualiza o modelo com base no histórico de feedbacks.
        Cada item deve conter: score, volume_busca, cpc, concorrencia, intencao, categoria, feedback_usuario, aprovado, feedback_manual (opcional).
        Feedback manual tem peso maior.
        """
        X_new, y_new = [], []
        for item in historico:
            peso = 2 if item.get("feedback_manual", False) else 1
            for _ in range(peso):
                X_new.append(self._encode_features(item))
                y_new.append(1 if item.get("aprovado", False) else 0)
        if not X_new:
            logger.warning({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "ml_treino_vazio",
                "status": "warning",
                "source": "ml_adaptativo.treinar_incremental"
            })
            return
        self.X.extend(X_new)
        self.result.extend(y_new)
        # Limita histórico
        if len(self.X) > self.HISTORICO_MAX:
            self.X = self.X[-self.HISTORICO_MAX:]
            self.result = self.result[-self.HISTORICO_MAX:]
        self.model.fit(np.array(self.X), np.array(self.result))
        self.trained = True
        self.data_treinamento = datetime.utcnow().isoformat()
        self._save()
        logger.info({
            "timestamp": self.data_treinamento,
            "event": "ml_treinado",
            "status": "success",
            "source": "ml_adaptativo.treinar_incremental",
            "details": {"total_treinados": len(self.X), "versao": self.versao}
        })

    def sugerir(self, itens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sugere os melhores clusters/keywords para priorização.
        Retorna lista ordenada por probabilidade de aprovação.
        Se não treinado, retorna itens ordenados por score (fallback).
        """
        if not itens:
            return itens
        if not self.trained:
            logger.warning({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "ml_nao_treinado_fallback",
                "status": "warning",
                "source": "ml_adaptativo.sugerir"
            })
            return sorted(itens, key=lambda value: value.get("score", 0), reverse=True)
        X_pred = [self._encode_features(index) for index in itens]
        try:
            probs = self.model.predict_proba(np.array(X_pred))[:, 1]
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "ml_erro_inferencia",
                "status": "error",
                "source": "ml_adaptativo.sugerir",
                "details": {"erro": str(e)}
            })
            return sorted(itens, key=lambda value: value.get("score", 0), reverse=True)
        for index, p in zip(itens, probs):
            index["prob_aprovacao"] = float(p)
        itens_ordenados = sorted(itens, key=lambda value: value["prob_aprovacao"], reverse=True)
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "ml_sugestao",
            "status": "success",
            "source": "ml_adaptativo.sugerir",
            "details": {"total": len(itens), "versao": self.versao}
        })
        return itens_ordenados

    def bloquear_repetidos(self, itens: List[Dict[str, Any]], historico: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Bloqueia clusters/keywords já processados ou de baixa performance.
        """
        processados = set((h.get("termo", ""), h.get("categoria", "")) for h in historico)
        filtrados = [index for index in itens if (index.get("termo", ""), index.get("categoria", "")) not in processados]
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "ml_bloqueio_repetidos",
            "status": "success",
            "source": "ml_adaptativo.bloquear_repetidos",
            "details": {"antes": len(itens), "depois": len(filtrados)}
        })
        return filtrados

    def explicar(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explica a decisão do modelo para um item (feature importance e motivos).
        """
        if not self.trained:
            return {"motivo": "modelo_nao_treinado", "importancias": {}}
        importancias = self.model.feature_importances_
        explicacao = {self.feature_names[index]: float(importancias[index]) for index in range(len(self.feature_names))}
        X_item = np.array(self._encode_features(item)).reshape(1, -1)
        prob = float(self.model.predict_proba(X_item)[0, 1])
        return {
            "prob_aprovacao": prob,
            "importancias": explicacao,
            "motivo": self._motivo_explicacao(item, explicacao)
        }

    def _motivo_explicacao(self, item: Dict[str, Any], explicacao: Dict[str, float]) -> str:
        """
        Gera motivo textual baseado nas features mais relevantes.
        """
        top = sorted(explicacao.items(), key=lambda value: value[1], reverse=True)[:2]
        return f"Decisão influenciada principalmente por: {top[0][0]}, {top[1][0]}"

    def _save(self):
        data = {
            "X": self.X,
            "result": self.result,
            "categoria_map": self.categoria_map,
            "versao": self.versao,
            "data_treinamento": self.data_treinamento
        }
        with open(self.model_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def _load(self):
        if not os.path.exists(self.model_path):
            return
        try:
            with open(self.model_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.X = data.get("X", [])
            self.result = data.get("result", [])
            self.categoria_map = data.get("categoria_map", {})
            self.versao = data.get("versao", self.VERSAO_MODELO)
            self.data_treinamento = data.get("data_treinamento")
            if self.X and self.result:
                self.model.fit(np.array(self.X), np.array(self.result))
                self.trained = True
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "ml_load_erro",
                "status": "error",
                "source": "ml_adaptativo._load",
                "details": {"erro": str(e)}
            }) 
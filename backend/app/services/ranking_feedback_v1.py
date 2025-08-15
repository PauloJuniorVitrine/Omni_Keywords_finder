"""
Módulo: ranking_feedback_v1
Permite registrar feedback do usuário sobre palavras-chave e influenciar ranking futuro.
"""
from typing import Dict, Any, List
import json
import os

_FEEDBACK_PATH = 'backend/app/services/_ranking_feedback_store.json'

class RankingFeedback:
    """
    Classe para registrar e consultar feedback do usuário sobre palavras-chave.
    """
    def __init__(self, storage_path: str = _FEEDBACK_PATH):
        self.storage_path = storage_path
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def _save(self):
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def registrar(self, termo: str, feedback: str):
        """
        Registra feedback ('preferida' ou 'irrelevante') para o termo.
        """
        self.data[termo] = feedback
        self._save()

    def consultar(self, termo: str) -> str:
        """
        Consulta feedback registrado para o termo.
        """
        return self.data.get(termo)

    def influenciar(self, palavras_chave: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ajusta score das palavras-chave conforme feedback do usuário.
        Preferidas recebem bônus, irrelevantes penalidade.
        """
        for p in palavras_chave:
            fb = self.consultar(p.get('termo'))
            if fb == 'preferida':
                p['score'] = p.get('score', 0) + 10
            elif fb == 'irrelevante':
                p['score'] = p.get('score', 0) - 10
        return palavras_chave 
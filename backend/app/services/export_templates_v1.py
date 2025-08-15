"""
Módulo: export_templates_v1
Permite exportação customizável (layout, colunas, formato) e incremental de arquivos CSV/TXT.
"""
from typing import List, Dict, Any, Optional
import csv
import os
import hashlib

class ExportTemplate:
    """
    Classe para definir e aplicar templates customizados de exportação.
    """
    def __init__(self, colunas: List[str], formato: str = 'csv', delimitador: str = ','):
        self.colunas = colunas
        self.formato = formato
        self.delimitador = delimitador

    def exportar(self, dados: List[Dict[str, Any]], caminho: str) -> str:
        """
        Exporta os dados conforme o template para o caminho especificado.
        """
        if self.formato == 'csv':
            with open(caminho, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.colunas, delimiter=self.delimitador)
                writer.writeheader()
                for row in dados:
                    writer.writerow({key: row.get(key, '') for key in self.colunas})
        elif self.formato == 'txt':
            with open(caminho, 'w', encoding='utf-8') as f:
                for row in dados:
                    linha = self.delimitador.join(str(row.get(key, '')) for key in self.colunas)
                    f.write(linha + '\n')
        return caminho

    def hash_dados(self, dados: List[Dict[str, Any]]) -> str:
        """
        Gera hash dos dados exportados para controle incremental.
        """
        m = hashlib.sha256()
        for row in dados:
            for key in self.colunas:
                m.update(str(row.get(key, '')).encode('utf-8'))
        return m.hexdigest()

class ExportadorIncremental:
    """
    Controla exportação incremental, exportando apenas arquivos alterados.
    """
    def __init__(self, pasta_export: str, template: ExportTemplate):
        self.pasta_export = pasta_export
        self.template = template
        self._hashes_path = os.path.join(pasta_export, '_export_hashes.json')
        self._load_hashes()

    def _load_hashes(self):
        import json
        if os.path.exists(self._hashes_path):
            with open(self._hashes_path, 'r', encoding='utf-8') as f:
                self._hashes = json.load(f)
        else:
            self._hashes = {}

    def _save_hashes(self):
        import json
        with open(self._hashes_path, 'w', encoding='utf-8') as f:
            json.dump(self._hashes, f, ensure_ascii=False, indent=2)

    def exportar_incremental(self, nome_arquivo: str, dados: List[Dict[str, Any]]) -> Optional[str]:
        """
        Exporta apenas se os dados mudaram (por hash). Retorna caminho do arquivo exportado ou None.
        """
        h = self.template.hash_dados(dados)
        if self._hashes.get(nome_arquivo) == h:
            return None  # Não mudou
        caminho = os.path.join(self.pasta_export, nome_arquivo)
        self.template.exportar(dados, caminho)
        self._hashes[nome_arquivo] = h
        self._save_hashes()
        return caminho 
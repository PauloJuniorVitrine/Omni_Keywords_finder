"""
Módulo: export_zip_v1
Gera logs detalhados de exportação e permite estrutura customizável de diretórios/arquivos no ZIP.
"""
from typing import List, Dict, Any, Optional
import os
import json
import zipfile
from datetime import datetime

class ExportLog:
    """
    Classe para gerar logs detalhados de exportação.
    """
    def __init__(self, usuario: str, arquivos: List[str], status: str = 'sucesso', metadados: Optional[Dict[str, Any]] = None):
        self.log = {
            'usuario': usuario,
            'arquivos': arquivos,
            'status': status,
            'timestamp_utc': datetime.utcnow().isoformat() + 'Z',
            'metadados': metadados or {}
        }

    def salvar(self, caminho: str):
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(self.log, f, ensure_ascii=False, indent=2)
        return caminho

class ExportadorZIP:
    """
    Classe para montar estrutura customizável e compactar arquivos e logs em ZIP.
    """
    def __init__(self, estrutura: Dict[str, List[str]]):
        """
        estrutura: dict {subpasta: [lista de arquivos]} para montar no ZIP.
        """
        self.estrutura = estrutura

    def exportar_zip(self, zip_path: str, arquivos_extra: Optional[Dict[str, str]] = None) -> str:
        """
        Compacta arquivos conforme estrutura e inclui arquivos extras (ex: logs).
        """
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as data:
            for subpasta, arquivos in self.estrutura.items():
                for arq in arquivos:
                    arcname = os.path.join(subpasta, os.path.basename(arq)) if subpasta else os.path.basename(arq)
                    data.write(arq, arcname)
            if arquivos_extra:
                for nome, caminho in arquivos_extra.items():
                    data.write(caminho, nome)
        return zip_path 
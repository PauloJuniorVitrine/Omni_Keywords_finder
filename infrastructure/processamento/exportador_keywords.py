"""
Módulo de exportação de palavras-chave e clusters.
Exporta dados validados em CSV, JSON e XLSX (opcional), organizando por cliente/nicho/categoria.
"""
import os
import csv
import json
import shutil
from typing import List, Dict, Any, Optional, Callable, Protocol
from domain.models import Keyword, Cluster
from shared.logger import logger
from datetime import datetime
import threading
import locale
import time
import functools
import configparser
import abc
from shared.config import BASE_DIR

try:
    import openpyxl
    XLSX_OK = True
except ImportError:
    XLSX_OK = False

# Configuração centralizada
CONFIG_PATH = os.getenv("EXPORTADOR_CONFIG_PATH", "exportador_keywords.ini")
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# Parâmetros de configuração centralizados
DEFAULT_ENCODING = "utf-8"
DEFAULT_DELIMITER = ","
DEFAULT_OUTPUT_DIR = str(BASE_DIR / "output")
DEFAULT_IDIOMA = "pt"

IDIOMA_PADRAO = config.get("exportador", "idioma", fallback=DEFAULT_IDIOMA)
ENCODING_PADRAO = config.get("exportador", "encoding", fallback=DEFAULT_ENCODING)
DELIMITADOR_PADRAO = config.get("exportador", "delimitador", fallback=DEFAULT_DELIMITER)

# Internacionalização simplificada
HEADERS_I18N = {
    "pt": {
        "termo": "Termo",
        "volume_busca": "Volume de Busca",
        "cpc": "CPC",
        "concorrencia": "Concorrência",
        "intencao": "Intenção",
        "score": "Score",
        "justificativa": "Justificativa",
        "fonte": "Fonte",
        "data_coleta": "Data de Coleta"
    },
    "en": {
        "termo": "Term",
        "volume_busca": "Search Volume",
        "cpc": "CPC",
        "concorrencia": "Competition",
        "intencao": "Intent",
        "score": "Score",
        "justificativa": "Justification",
        "fonte": "Source",
        "data_coleta": "Collection Date"
    }
}

class ExportadorBase(abc.ABC):
    """Interface base para exportadores de keywords/clusters."""
    @abc.abstractmethod
    def exportar(self, items: List[Any], path: str, **kwargs) -> List[Dict]:
        pass

class ExportadorCSV(ExportadorBase):
    """Exportador de keywords/clusters para CSV, com suporte a i18n, logs e validação."""
    def exportar(self, items: List[Any], path: str, append: bool = False, encoding: str = "utf-8", delimiter: str = ",", **kwargs) -> List[Dict]:
        erros = []
        mode = "a" if append else "w"
        write_header = not (append and os.path.exists(path))
        try:
            with open(path, mode, newline='', encoding=encoding) as f:
                item_dict = next((item.to_dict() for item in items if item and hasattr(item, 'to_dict')), None)
                if not item_dict:
                    raise ValueError("Nenhum item válido para exportar")
                fieldnames = list(item_dict.keys())
                headers = {key: key for key in fieldnames}
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
                if write_header:
                    writer.writerow(headers)
                for item in items:
                    try:
                        if item and hasattr(item, 'to_dict'):
                            row = item.to_dict()
                            if row:
                                writer.writerow(row)
                    except Exception as e:
                        id_info = getattr(item, 'id', None) or getattr(item, 'termo', 'unknown')
                        erros.append({"id": id_info, "erro": str(e)})
        except Exception as e:
            erros.append({"arquivo": path, "erro": str(e)})
        return erros

class ExportadorJSON(ExportadorBase):
    """Exportador de keywords/clusters para JSON, com suporte a i18n, logs e validação."""
    def exportar(self, items: List[Any], path: str, encoding: str = "utf-8", **kwargs) -> List[Dict]:
        erros = []
        try:
            valid_items = []
            for item in items:
                try:
                    if item and hasattr(item, 'to_dict'):
                        item_dict = item.to_dict()
                        if item_dict:
                            valid_items.append(item_dict)
                except Exception as e:
                    id_info = getattr(item, 'id', None) or getattr(item, 'termo', 'unknown')
                    erros.append({"id": id_info, "erro": str(e)})
            if valid_items:
                with open(path, "w", encoding=encoding) as f:
                    json.dump(valid_items, f, ensure_ascii=False, indent=2)
            else:
                erros.append({"arquivo": path, "erro": "Nenhum item válido para exportar"})
        except Exception as e:
            erros.append({"arquivo": path, "erro": str(e)})
        return erros

class ExportadorXLSX(ExportadorBase):
    """Exportador de keywords/clusters para XLSX, com suporte a i18n, logs e validação."""
    def exportar(self, items: List[Any], path: str, i18n: Optional[Dict[str, str]] = None, **kwargs) -> List[Dict]:
        erros = []
        if not XLSX_OK:
            return [{"arquivo": path, "erro": "openpyxl não instalado"}]
        try:
            valid_items = []
            headers = None
            for item in items:
                try:
                    if item and hasattr(item, 'to_dict'):
                        item_dict = item.to_dict()
                        if item_dict:
                            if not headers:
                                headers = list(item_dict.keys())
                            if i18n:
                                item_dict = {i18n.get(key, key): value for key, value in item_dict.items()}
                            valid_items.append(item_dict)
                except Exception as e:
                    id_info = getattr(item, 'id', None) or getattr(item, 'termo', 'unknown')
                    erros.append({"id": id_info, "erro": str(e)})
            if valid_items and headers:
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.append([i18n.get(h, h) if i18n else h for h in headers])
                for row in valid_items:
                    ws.append([row.get(h, "") for h in (i18n.get(h, h) if i18n else h for h in headers)])
                wb.save(path)
            else:
                erros.append({"arquivo": path, "erro": "Nenhum item válido para exportar"})
        except Exception as e:
            erros.append({"arquivo": path, "erro": str(e)})
        return erros

class ExportadorKeywords:
    """
    Orquestrador de exportação de keywords e clusters em múltiplos formatos, com validação, i18n, logs e hooks.
    """
    def __init__(self, output_dir: str = DEFAULT_OUTPUT_DIR, idioma: str = IDIOMA_PADRAO):
        self.output_dir = output_dir
        self.idioma = idioma if idioma in HEADERS_I18N else IDIOMA_PADRAO
        self._lock = threading.Lock()
        self.exportadores = {
            "csv": ExportadorCSV(),
            "json": ExportadorJSON(),
            "xlsx": ExportadorXLSX() if XLSX_OK else None
        }

    def _get_path(self, client: str, niche: str, category: str, filename: str) -> str:
        """Gera e cria o caminho completo para o arquivo."""
        try:
            path = os.path.join(self.output_dir, client, niche, category)
            os.makedirs(path, exist_ok=True)
            return os.path.join(path, filename)
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_criacao_diretorio",
                "status": "error",
                "source": "exportador_keywords._get_path",
                "details": {"erro": str(e)}
            })
            raise

    def _check_disk_space(self, path: str, min_bytes: int = 1024 * 1024) -> bool:
        """Verifica se há espaço suficiente para exportação."""
        try:
            total, used, free = shutil.disk_usage(os.path.dirname(path))
            return free > min_bytes
        except Exception:
            return True  # Em caso de erro, assume que há espaço

    def _validar_dados(self, items: List[Any]) -> List[str]:
        """Valida e sanitiza os dados antes da exportação."""
        erros = []
        for item in items:
            if not item or not hasattr(item, 'to_dict'):
                erros.append(f"Item inválido: {item}")
        return erros

    def exportar_keywords(
        self,
        keywords: List[Keyword],
        client: str,
        niche: str,
        category: str,
        filename_prefix: Optional[str] = None,
        append: bool = False,
        formatos: Optional[List[str]] = None,
        export_xlsx: bool = False,
        callback: Optional[Callable[[Dict], None]] = None,
        relatorio_validacao: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        Exporta keywords em múltiplos formatos, com validação, i18n, logs e hooks.
        """
        inicio = datetime.utcnow()
        arquivos = {}
        status = "success"
        avisos = []
        erros = []
        formatos = formatos or ["csv", "json"]
        if export_xlsx and "xlsx" not in formatos:
            formatos.append("xlsx")
        headers = HEADERS_I18N[self.idioma]

        if not keywords:
            logger.warning({
                "timestamp": inicio.isoformat(),
                "event": "exportacao_keywords_vazia",
                "status": "warning",
                "source": "exportador_keywords.exportar_keywords",
                "details": {"client": client, "niche": niche, "category": category}
            })
            return {"status": "empty", "arquivos": {}, "avisos": ["Lista de keywords vazia"]}

        # Validação
        erros_validacao = self._validar_dados(keywords)
        if erros_validacao:
            avisos.extend(erros_validacao)
            status = "warning"

        # Logar ordem das keywords exportadas
        ordem_exportada = [
            {"termo": key.termo, "ordem_no_cluster": getattr(key, "ordem_no_cluster", -1), "fase_funil": getattr(key, "fase_funil", "")} 
            for key in keywords
        ]
        logger.info({
            "timestamp": inicio.isoformat(),
            "event": "ordem_exportacao_keywords",
            "status": "audit",
            "source": "exportador_keywords.exportar_keywords",
            "details": {"ordem_exportada": ordem_exportada, "total": len(keywords)}
        })

        try:
            ts = inicio.strftime("%Y%m%data%H%M%S")
            prefix = f"{filename_prefix}_" if filename_prefix else ""
            for fmt in formatos:
                nome = f"{prefix}keywords_{ts}.{fmt}"
                path = self._get_path(client, niche, category, nome)
                if not self._check_disk_space(path):
                    avisos.append("Espaço em disco insuficiente para exportação.")
                    status = "warning"
                exportador = self.exportadores.get(fmt)
                if exportador:
                    try:
                        with self._lock:
                            if fmt == "csv":
                                erros_fmt = exportador.exportar(keywords, path, append=append, encoding=ENCODING_PADRAO, delimiter=DELIMITADOR_PADRAO)
                            elif fmt == "json":
                                erros_fmt = exportador.exportar(keywords, path, encoding=ENCODING_PADRAO)
                            elif fmt == "xlsx":
                                erros_fmt = exportador.exportar(keywords, path, i18n=headers)
                            else:
                                erros_fmt = exportador.exportar(keywords, path)
                        if not erros_fmt:
                            arquivos[fmt] = path
                        else:
                            erros.extend(erros_fmt)
                    except Exception as e:
                        erro_msg = {"arquivo": path, "erro": str(e)}
                        erros.append(erro_msg)
                        logger.error({
                            "timestamp": datetime.utcnow().isoformat(),
                            "event": "erro_exportacao_keywords",
                            "status": "error",
                            "source": "exportador_keywords.exportar_keywords",
                            "details": {
                                "client": client,
                                "niche": niche,
                                "category": category,
                                "erro": str(e),
                                "arquivo": path
                            }
                        })
                else:
                    avisos.append(f"Formato não suportado ou dependência ausente: {fmt}")
            if erros:
                status = "error"
            elif avisos:
                status = "warning"
            tempo = (datetime.utcnow() - inicio).total_seconds()
            if status == "error":
                logger.error({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "exportacao_keywords",
                    "status": status,
                    "source": "exportador_keywords.exportar_keywords",
                    "details": {
                        "client": client,
                        "niche": niche,
                        "category": category,
                        "total_keywords": len(keywords),
                        "arquivos": arquivos,
                        "tempo": tempo,
                        "avisos": avisos,
                        "erros": erros
                    }
                })
            tempo = (datetime.utcnow() - inicio).total_seconds()
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "exportacao_keywords",
                "status": status,
                "source": "exportador_keywords.exportar_keywords",
                "details": {
                    "client": client,
                    "niche": niche,
                    "category": category,
                    "total_keywords": len(keywords),
                    "arquivos": arquivos,
                    "tempo": tempo,
                    "avisos": avisos,
                    "erros": erros
                }
            })
            if callback:
                try:
                    callback({
                        "arquivos": arquivos,
                        "status": status,
                        "avisos": avisos,
                        "erros": erros,
                        "tempo": tempo
                    })
                except Exception as e:
                    logger.error({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_callback_exportacao",
                        "status": "error",
                        "source": "exportador_keywords.exportar_keywords",
                        "details": {"erro": str(e)}
                    })
            if relatorio_validacao:
                logger.info({
                    "timestamp": inicio.isoformat(),
                    "event": "relatorio_validacao_keywords",
                    "status": "info",
                    "source": "exportador_keywords.exportar_keywords",
                    "details": relatorio_validacao
                })
        except Exception as e:
            status = "error"
            erros.append({"erro": str(e)})
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_exportacao_keywords",
                "status": "error",
                "source": "exportador_keywords.exportar_keywords",
                "details": {
                    "client": client,
                    "niche": niche,
                    "category": category,
                    "erro": str(e)
                }
            })
        return {
            "arquivos": arquivos,
            "status": status,
            "avisos": avisos,
            "erros": erros,
            "tempo": (datetime.utcnow() - inicio).total_seconds(),
            "relatorio_validacao": relatorio_validacao
        }

    def exportar_clusters(
        self,
        clusters: List[Cluster],
        client: str,
        niche: str,
        category: str,
        filename_prefix: Optional[str] = None,
        append: bool = False,
        export_xlsx: bool = False,
        callback: Optional[Callable[[Dict], None]] = None,
        relatorio_validacao: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        Exporta clusters em CSV, JSON e opcionalmente XLSX.
        """
        inicio = datetime.utcnow()
        arquivos = {}
        status = "success"
        avisos = []
        erros = []
        headers = HEADERS_I18N[self.idioma]
        formatos = ["csv", "json"]
        if export_xlsx and self.exportadores["xlsx"]:
            formatos.append("xlsx")

        if not clusters:
            logger.warning({
                "timestamp": inicio.isoformat(),
                "event": "exportacao_clusters_vazia",
                "status": "warning",
                "source": "exportador_keywords.exportar_clusters",
                "details": {"client": client, "niche": niche, "category": category}
            })
            return {"status": "empty", "arquivos": {}, "avisos": ["Lista de clusters vazia"]}

        try:
            ts = inicio.strftime("%Y%m%data%H%M%S")
            prefix = f"{filename_prefix}_" if filename_prefix else ""
            for fmt in formatos:
                nome = f"{prefix}clusters_{ts}.{fmt}"
                path = self._get_path(client, niche, category, nome)
                if not self._check_disk_space(path):
                    avisos.append("Espaço em disco insuficiente para exportação.")
                    status = "warning"
                exportador = self.exportadores.get(fmt)
                if exportador:
                    try:
                        with self._lock:
                            if fmt == "csv":
                                erros_fmt = exportador.exportar(clusters, path, append=append, encoding=ENCODING_PADRAO, delimiter=DELIMITADOR_PADRAO)
                            elif fmt == "json":
                                erros_fmt = exportador.exportar(clusters, path, encoding=ENCODING_PADRAO)
                            elif fmt == "xlsx":
                                erros_fmt = exportador.exportar(clusters, path, i18n=headers)
                            else:
                                erros_fmt = exportador.exportar(clusters, path)
                        if not erros_fmt:
                            arquivos[fmt] = path
                        else:
                            erros.extend(erros_fmt)
                    except Exception as e:
                        erro_msg = {"arquivo": path, "erro": str(e)}
                        erros.append(erro_msg)
                        logger.error({
                            "timestamp": datetime.utcnow().isoformat(),
                            "event": "erro_exportacao_clusters",
                            "status": "error",
                            "source": "exportador_keywords.exportar_clusters",
                            "details": {
                                "client": client,
                                "niche": niche,
                                "category": category,
                                "erro": str(e),
                                "arquivo": path
                            }
                        })
                else:
                    avisos.append(f"Formato não suportado ou dependência ausente: {fmt}")
            if erros:
                status = "error"
            elif avisos:
                status = "warning"
            tempo = (datetime.utcnow() - inicio).total_seconds()
            if status == "error":
                logger.error({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "exportacao_clusters",
                    "status": status,
                    "source": "exportador_keywords.exportar_clusters",
                    "details": {
                        "client": client,
                        "niche": niche,
                        "category": category,
                        "total_clusters": len(clusters),
                        "arquivos": arquivos,
                        "tempo": tempo,
                        "avisos": avisos,
                        "erros": erros
                    }
                })
            else:
                logger.info({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "exportacao_clusters",
                    "status": status,
                    "source": "exportador_keywords.exportar_clusters",
                    "details": {
                        "client": client,
                        "niche": niche,
                        "category": category,
                        "total_clusters": len(clusters),
                        "arquivos": arquivos,
                        "tempo": tempo,
                        "avisos": avisos,
                        "erros": erros
                    }
                })
            if callback:
                try:
                    callback({
                        "arquivos": arquivos,
                        "status": status,
                        "avisos": avisos,
                        "erros": erros,
                        "tempo": tempo
                    })
                except Exception as e:
                    logger.error({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_callback_exportacao",
                        "status": "error",
                        "source": "exportador_keywords.exportar_clusters",
                        "details": {"erro": str(e)}
                    })
            if relatorio_validacao:
                logger.info({
                    "timestamp": inicio.isoformat(),
                    "event": "relatorio_validacao_clusters",
                    "status": "info",
                    "source": "exportador_keywords.exportar_clusters",
                    "details": relatorio_validacao
                })
        except Exception as e:
            status = "error"
            erros.append({"erro": str(e)})
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_exportacao_clusters",
                "status": "error",
                "source": "exportador_keywords.exportar_clusters",
                "details": {
                    "client": client,
                    "niche": niche,
                    "category": category,
                    "erro": str(e)
                }
            })
        return {
            "arquivos": arquivos,
            "status": status,
            "avisos": avisos,
            "erros": erros,
            "tempo": (datetime.utcnow() - inicio).total_seconds(),
            "relatorio_validacao": relatorio_validacao
        } 
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import json
from datetime import datetime

router = APIRouter()

LOG_PATH = os.getenv('LOG_PATH', 'logs/omni_keywords.log')

@router.get('/logs', response_class=JSONResponse)
def listar_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    event: Optional[str] = None,
    status: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None
):
    """
    Retorna logs estruturados do sistema, com filtros e paginação.
    """
    logs: List[dict] = []
    if not os.path.exists(LOG_PATH):
        return {"total": 0, "logs": []}
    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                log = json.loads(line)
                if event and log.get('event') != event:
                    continue
                if status and log.get('status') != status:
                    continue
                if data_inicio:
                    dt = datetime.fromisoformat(log.get('timestamp', ''))
                    if dt < datetime.fromisoformat(data_inicio):
                        continue
                if data_fim:
                    dt = datetime.fromisoformat(log.get('timestamp', ''))
                    if dt > datetime.fromisoformat(data_fim):
                        continue
                logs.append(log)
            except Exception:
                continue
    total = len(logs)
    start = (page - 1) * page_size
    end = start + page_size
    return {"total": total, "logs": logs[start:end]} 
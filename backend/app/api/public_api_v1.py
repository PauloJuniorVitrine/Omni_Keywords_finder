"""
Módulo: public_api_v1
API pública para consulta de execuções, exportações e métricas.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List, Dict, Any, Optional

router = APIRouter()

# Simulação de autenticação por token
API_TOKEN = "public-token-123"
def token_auth(authorization: Optional[str] = Header(None)):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Token inválido")

@router.get("/public/execucoes", tags=["public"], summary="Listar execuções")
def listar_execucoes(auth=Depends(token_auth)) -> List[Dict[str, Any]]:
    return [
        {"id": "1", "status": "ok", "inicio": "2024-06-27T10:00", "fim": "2024-06-27T10:01", "tipo": "lote"},
        {"id": "2", "status": "erro", "inicio": "2024-06-27T10:02", "fim": "2024-06-27T10:03", "tipo": "agendada", "erro": "Timeout"},
    ]

@router.get("/public/exportacoes", tags=["public"], summary="Listar exportações")
def listar_exportacoes(auth=Depends(token_auth)) -> List[Dict[str, Any]]:
    return [
        {"arquivo": "nicho1/export.csv", "status": "ok", "data": "2024-06-27T10:05"},
        {"arquivo": "nicho2/export.csv", "status": "erro", "data": "2024-06-27T10:06"},
    ]

@router.get("/public/metricas", tags=["public"], summary="Obter métricas")
def obter_metricas(auth=Depends(token_auth)) -> Dict[str, Any]:
    return {
        "execucoes_total": 10,
        "execucoes_erro": 2,
        "exportacoes_total": 8,
        "exportacoes_erro": 1,
    } 
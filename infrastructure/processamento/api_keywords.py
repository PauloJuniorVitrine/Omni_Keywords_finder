from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from infrastructure.processamento.processador_keywords import (
    ProcessadorKeywordsPipeline, NormalizadorHandler, LimpezaHandler, ValidacaoHandler, EnriquecimentoHandler, MLHandler, ValidadorKeywords
)
from domain.models import Keyword
import os

app = FastAPI(title="Omni Keywords Pipeline API", description="API REST para processamento de palavras-chave com observabilidade enterprise.")

class KeywordIn(BaseModel):
    termo: str
    volume_busca: Optional[float] = 0
    cpc: Optional[float] = 0
    concorrencia: Optional[float] = 0
    intencao: Optional[str] = None
    score: Optional[float] = None
    justificativa: Optional[str] = None
    fonte: Optional[str] = None
    data_coleta: Optional[str] = None

class PipelineRequest(BaseModel):
    keywords: List[KeywordIn]
    remover_acentos: Optional[bool] = False
    case_sensitive: Optional[bool] = False
    validar: Optional[bool] = True
    enriquecer: Optional[bool] = True
    ml: Optional[bool] = False
    regras_validacao: Optional[Dict[str, Any]] = None
    blacklist: Optional[List[str]] = None
    whitelist: Optional[List[str]] = None
    pesos_score: Optional[Dict[str, float]] = None
    idioma: Optional[str] = "pt"
    historico_feedback: Optional[List[Dict[str, Any]]] = None

@app.post("/processar_keywords/", summary="Processa uma lista de keywords pelo pipeline completo.")
async def processar_keywords_endpoint(payload: PipelineRequest):
    # Montar pipeline dinâmico conforme payload
    handlers = [
        NormalizadorHandler(remover_acentos=payload.remover_acentos, case_sensitive=payload.case_sensitive),
        LimpezaHandler()
    ]
    contexto = {"pesos": payload.pesos_score or {"volume": 0.4, "cpc": 0.2, "intention": 0.2, "competition": 0.2}}
    if payload.validar:
        validador = ValidadorKeywords(
            blacklist=set(payload.blacklist or []),
            whitelist=set(payload.whitelist or []),
            score_minimo=(payload.regras_validacao or {}).get("score_min", 0.0)
        )
        handlers.append(ValidacaoHandler(validador, regras=payload.regras_validacao))
    if payload.enriquecer:
        handlers.append(EnriquecimentoHandler())
    if payload.ml:
        handlers.append(MLHandler())  # ML adaptativo real pode ser injetado conforme necessidade
    pipeline = ProcessadorKeywordsPipeline(handlers, idioma=payload.idioma)
    keywords_objs = [Keyword(**kw.dict()) for kw in payload.keywords]
    result = pipeline.processar(keywords_objs, contexto)
    return {"status": "ok", "total": len(result), "keywords": [key.to_dict() for key in result]}

# Exemplo de uso:
# curl -X POST "http://localhost:8001/processar_keywords/" -H "Content-Type: application/json" -data '{"keywords": [{"termo": "exemplo"}]}' 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.governanca import router as governanca_router
from typing import Dict, List, Optional, Any

app = FastAPI(title="API Governança Omni Keywords")

# Configuração básica de CORS para integração local/frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(governanca_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"} 
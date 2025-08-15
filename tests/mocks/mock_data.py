"""
Dados mock para testes - Omni Keywords Finder

Baseado no código real do sistema para garantir
que os testes sejam representativos.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta


# Dados mock para keywords
MOCK_KEYWORDS = [
    {
        "termo": "teste keyword 1",
        "volume": 1000,
        "competicao": "baixa",
        "cpc": 0.50,
        "nicho": "tech"
    },
    {
        "termo": "teste keyword 2", 
        "volume": 800,
        "competicao": "média",
        "cpc": 1.20,
        "nicho": "tech"
    },
    {
        "termo": "teste keyword 3",
        "volume": 1200,
        "competicao": "alta",
        "cpc": 2.50,
        "nicho": "tech"
    }
]

# Dados mock para nichos
MOCK_NICHOS = [
    {
        "nome": "tech",
        "descricao": "Tecnologia",
        "config": {
            "limite_keywords": 100,
            "idioma": "pt",
            "pais": "BR"
        }
    },
    {
        "nome": "saude",
        "descricao": "Saúde e Bem-estar",
        "config": {
            "limite_keywords": 150,
            "idioma": "pt",
            "pais": "BR"
        }
    }
]

# Dados mock para resultados de coleta
MOCK_COLETA_RESULT = {
    "keywords": MOCK_KEYWORDS,
    "total_coletado": len(MOCK_KEYWORDS),
    "nicho": "tech",
    "timestamp": datetime.now().isoformat()
}

# Dados mock para resultados de processamento
MOCK_PROCESSAMENTO_RESULT = {
    "keywords": [
        {
            "termo": "teste keyword 1",
            "volume": 1000,
            "competicao": "baixa",
            "cpc": 0.50,
            "nicho": "tech",
            "score_semantico": 0.85,
            "score_relevancia": 0.92,
            "status": "processado"
        },
        {
            "termo": "teste keyword 2",
            "volume": 800,
            "competicao": "média", 
            "cpc": 1.20,
            "nicho": "tech",
            "score_semantico": 0.78,
            "score_relevancia": 0.88,
            "status": "processado"
        }
    ],
    "total_processado": 2,
    "nicho": "tech",
    "timestamp": datetime.now().isoformat()
}

# Dados mock para resultados de exportação
MOCK_EXPORTACAO_RESULT = {
    "arquivos": {
        "csv": "tech_keywords_20250127.csv",
        "json": "tech_keywords_20250127.json",
        "xlsx": "tech_keywords_20250127.xlsx"
    },
    "total_exportado": 2,
    "nicho": "tech",
    "timestamp": datetime.now().isoformat()
}

# Dados mock para métricas
MOCK_METRICS = {
    "total_integrations": 10,
    "successful_integrations": 8,
    "failed_integrations": 2,
    "last_error": "Connection timeout",
    "last_success": datetime.now().isoformat()
}

# Dados mock para status de módulos
MOCK_MODULE_STATUS = {
    "bridge_ready": True,
    "modules_initialized": True,
    "coletor_available": True,
    "processador_available": True,
    "exportador_available": True,
    "metrics": MOCK_METRICS
}

# Dados mock para configurações
MOCK_CONFIG = {
    "coleta": {
        "limite_padrao": 100,
        "timeout": 30,
        "retry_attempts": 3
    },
    "processamento": {
        "batch_size": 50,
        "max_workers": 4,
        "timeout": 60
    },
    "exportacao": {
        "formatos_suportados": ["csv", "json", "xlsx"],
        "compressao": True,
        "backup": True
    }
}

# Dados mock para erros
MOCK_ERRORS = {
    "connection_error": "Connection timeout after 30 seconds",
    "import_error": "Module 'pytrends' not found",
    "validation_error": "Invalid keyword format",
    "processing_error": "Failed to process keyword batch"
}

# Dados mock para logs
MOCK_LOGS = [
    {
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "message": "Integration Bridge initialized successfully",
        "source": "IntegrationBridge.__init__",
        "tracing_id": "BRIDGE_12345678"
    },
    {
        "timestamp": datetime.now().isoformat(),
        "level": "ERROR", 
        "message": "Failed to initialize module",
        "source": "IntegrationBridge._initialize_modules",
        "tracing_id": "BRIDGE_12345678",
        "error": "Import error"
    }
]

# Dados mock para resultados de integração
MOCK_INTEGRATION_RESULTS = {
    "coleta": {
        "success": True,
        "data": MOCK_COLETA_RESULT,
        "error": None,
        "execution_time": 1.5,
        "metadata": {"source": "google_trends"}
    },
    "processamento": {
        "success": True,
        "data": MOCK_PROCESSAMENTO_RESULT,
        "error": None,
        "execution_time": 2.3,
        "metadata": {"algorithm": "semantic_analysis"}
    },
    "exportacao": {
        "success": True,
        "data": MOCK_EXPORTACAO_RESULT,
        "error": None,
        "execution_time": 0.8,
        "metadata": {"format": "multi_format"}
    }
}

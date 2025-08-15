"""
Configurações centralizadas para os coletores de dados.
"""
from typing import Dict
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do Redis
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", "6379")),
    "db": int(os.getenv("REDIS_DB", "0")),
    "password": os.getenv("REDIS_PASSWORD"),
    "decode_responses": True
}

# Configurações de coleta
COLETA_CONFIG = {
    "max_keywords_por_termo": 100,
    "max_comentarios_por_item": 500,
    "janela_tendencias_dias": 90,
    "janela_sazonalidade_dias": 180,
    "limite_requisicoes_minuto": 60,
    "user_agent": "OmniKeywordsFinder/1.0",
    "proxy_enabled": False,
    "proxy_config": {
        "http": os.getenv("HTTP_PROXY"),
        "https": os.getenv("HTTPS_PROXY")
    }
}

# Configurações de validação
VALIDACAO_CONFIG = {
    "min_volume": 10,
    "max_volume": 1000000,
    "min_concorrencia": 0.0,
    "max_concorrencia": 1.0,
    "min_caracteres": 3,
    "max_caracteres": 100,
    "caracteres_permitidos": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ "
}

# Configurações específicas por coletor
INSTAGRAM_CONFIG = {
    "max_posts": 100,
    "max_stories": 50,
    "max_reels": 50,
    "analise_sentimento": True,
    "analise_tendencias": True,
    "credentials": {
        "username": os.getenv("INSTAGRAM_USERNAME"),
        "password": os.getenv("INSTAGRAM_PASSWORD"),
        "session_id": os.getenv("INSTAGRAM_SESSION_ID")
    }
}

TIKTOK_CONFIG = {
    "max_videos": 100,
    "max_challenges": 50,
    "analise_musicas": True,
    "analise_hashtags": True,
    "analise_tendencias": True,
    "min_views_trend": 100000,
    "min_engagement_trend": 0.1,
    "max_trend_age_days": 7,
    "credentials": {
        "api_key": os.getenv("TIKTOK_API_KEY"),
        "api_secret": os.getenv("TIKTOK_API_SECRET")
    }
}

YOUTUBE_CONFIG = {
    "max_videos": 50,
    "max_comentarios": 200,
    "analise_transcricao": True,
    "analise_sentimento": True,
    "analise_tendencias": True,
    "idiomas_transcricao": ["pt", "en"],
    "min_palavras_topico": 3,
    "max_topicos": 10,
    "credentials": {
        "api_key": os.getenv("YOUTUBE_API_KEY"),
        "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET")
    }
}

GSC_CONFIG = {
    "janela_dados_dias": 90,
    "metricas": [
        "clicks",
        "impressions",
        "ctr",
        "position"
    ],
    "dimensoes": [
        "query",
        "page",
        "device",
        "country"
    ],
    "analise_tendencias": True,
    "analise_sazonalidade": True,
    "credentials": {
        "client_id": os.getenv("GSC_CLIENT_ID"),
        "client_secret": os.getenv("GSC_CLIENT_SECRET"),
        "refresh_token": os.getenv("GSC_REFRESH_TOKEN")
    }
}

# Configurações de análise de sentimento
SENTIMENT_CONFIG = {
    "threshold_positivo": 0.3,
    "threshold_negativo": -0.3,
    "max_comentarios": 100,
    "idiomas": ["pt", "en"]
}

# Configurações de análise de tendências
TRENDS_CONFIG = {
    "janela_padrao": 7,  # dias
    "janela_sazonalidade": 90,  # dias
    "threshold_variacao": 10,  # porcentagem
    "min_dados_sazonalidade": 14  # dias
}

# Configurações de logging
LOGGING_CONFIG = {
    "formato": "json",
    "nivel": os.getenv("LOG_LEVEL", "INFO"),
    "campos_padrao": [
        "timestamp",
        "event",
        "status",
        "source",
        "details"
    ]
}

def get_coletor_config(nome: str) -> Dict:
    """
    Retorna configuração específica de um coletor.
    
    Args:
        nome: Nome do coletor
        
    Returns:
        Dicionário com configurações
    """
    configs = {
        "instagram": {**INSTAGRAM_CONFIG, **COLETA_CONFIG, **VALIDACAO_CONFIG},
        "tiktok": {**TIKTOK_CONFIG, **COLETA_CONFIG, **VALIDACAO_CONFIG},
        "youtube": {**YOUTUBE_CONFIG, **COLETA_CONFIG, **VALIDACAO_CONFIG},
        "gsc": {**GSC_CONFIG, **COLETA_CONFIG, **VALIDACAO_CONFIG}
    }
    return configs.get(nome, {}) 
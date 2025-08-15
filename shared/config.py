"""
Configurações globais do sistema de geração de clusters e conteúdo SEO.
"""
import os
from pathlib import Path
from typing import Dict, List

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent
BLOGS_DIR = BASE_DIR / "blogs"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Configurações de API
class APIConfig:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
    GSC_CREDENTIALS_FILE = os.getenv("GSC_CREDENTIALS_FILE", "")
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
    PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN", "")
    TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "")
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
    AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY", "")
    AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY", "")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# Configurações base de coleta
class CollectorConfig:
    MAX_KEYWORDS_PER_SOURCE: int = 100
    REQUEST_DELAY: float = 1.0  # segundos
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30  # segundos
    USER_AGENT: str = "Mozilla/5.0 (compatible; OmniKeywordsFinder/1.0; +http://example.com)"
    PROXY_ENABLED: bool = False
    PROXY_LIST: List[str] = []

# Configurações específicas dos coletores
GOOGLE_SUGGEST_CONFIG = {
    "rate_limit": 60,  # requisições por minuto
    "proxy_enabled": True,
    "user_agent": CollectorConfig.USER_AGENT
}

GOOGLE_TRENDS_CONFIG = {
    "rate_limit": 30,
    "periodo_analise": 90,  # dias
    "pais": "BR",
    "idioma": "pt-BR"
}

GOOGLE_PAA_CONFIG = {
    "rate_limit": 30,
    "max_depth": 3,  # profundidade máxima de perguntas relacionadas
    "proxy_enabled": True
}

GOOGLE_RELATED_CONFIG = {
    "rate_limit": 30,
    "max_pages": 3,
    "proxy_enabled": True
}

YOUTUBE_CONFIG = {
    "rate_limit": 50,
    "max_videos": 50,
    "extract_comments": True,
    "comment_limit": 100,
    "relevance_threshold": 0.7
}

REDDIT_CONFIG = {
    "rate_limit": 60,
    "subreddits_limit": 5,
    "posts_per_subreddit": 100,
    "min_score": 10,
    "time_filter": "month"
}

PINTEREST_CONFIG = {
    "rate_limit": 60,
    "max_pins": 100,
    "min_saves": 10,
    "categories": ["all"]
}

TIKTOK_CONFIG = {
    "rate_limit": 60,
    "max_videos": 100,
    "max_hashtags": 50,
    "max_challenges": 50,
    "min_likes": 1000,
    "extract_comments": True,
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

DISCORD_CONFIG = {
    "rate_limit": 50,
    "servers_limit": 5,
    "channels_per_server": 10,
    "messages_per_channel": 100,
    "min_reactions": 5,
    "token": os.getenv("DISCORD_BOT_TOKEN", "test_token")  # Token para testes
}

AMAZON_CONFIG = {
    "rate_limit": 30,
    "marketplace": "amazon.com.br",
    "max_products": 100,
    "min_reviews": 10,
    "categories": ["all"]
}

# Configurações de processamento
class ProcessingConfig:
    MIN_KEYWORD_LENGTH: int = 3
    MAX_KEYWORD_LENGTH: int = 100
    MIN_CLUSTER_SIMILARITY: float = 0.7
    CLUSTER_SIZE: int = 6
    WORDS_PER_ARTICLE: int = 3500
    KEYWORD_DENSITY: float = 0.015  # 1.5%

# Configurações de validação
class ValidationConfig:
    MIN_SEARCH_VOLUME: int = 10
    MIN_SCORE: float = 0.5
    SCORE_WEIGHTS: Dict[str, float] = {
        "volume": 0.4,
        "cpc": 0.3,
        "intention": 0.2,
        "competition": 0.1
    }

# Configurações de logging
class LogConfig:
    LOG_FORMAT: str = "json"
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "omni_keywords.log"

# Configurações do Google Search Console
GSC_CONFIG = {
    "site_url": "",  # Será preenchido via variável de ambiente
    "dias_analise": 90,
    "limite_requisicoes_dia": 25000,
    "limite_keywords_consulta": 100,
    "intervalo_requisicoes": 1  # segundos
}

# Fases do funil
FUNNEL_STAGES: List[str] = [
    "descoberta",
    "curiosidade",
    "consideracao",
    "comparacao",
    "decisao",
    "autoridade"
]

# Configurações de fallback
class FallbackConfig:
    ENABLED: bool = True
    MAX_ATTEMPTS: int = 3
    MODELS_PRIORITY: List[str] = ["deepseek", "openai", "claude"]
    TIMEOUT_MULTIPLIER: float = 1.5

# Configurações do Flask
class FlaskConfig:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev_key_change_in_prod")
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

BLACKLIST_TERMS_FILE = BASE_DIR / "shared" / "blacklist.json"

def load_blacklist() -> List[str]:
    import json
    if BLACKLIST_TERMS_FILE.exists():
        with open(BLACKLIST_TERMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_blacklist(terms: List[str]):
    import json
    with open(BLACKLIST_TERMS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(set(terms)), f, ensure_ascii=False, indent=2)

# Configuração do Redis
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "db": int(os.getenv("REDIS_DB", 0)),
    "password": os.getenv("REDIS_PASSWORD", None),
}

# Configuração de cache para coletores
CACHE_CONFIG = {
    "namespaces": {
        "amazon": "amazon_namespace",
        "reddit": "reddit_namespace",
        "pinterest": "pinterest_namespace",
        "discord": "discord_namespace",
        "tiktok": "tiktok_namespace",
        "youtube": "youtube_namespace",
        "gsc": "gsc_namespace",
        "instagram": "instagram_namespace",
        "google_trends": "google_trends_namespace",
        "google_suggest": "google_suggest_namespace",
        "google_paa": "google_paa_namespace",
        "google_related": "google_related_namespace"
    },
    "ttl_padrao": 3600,
    "ttl_keywords": 7200,
    "ttl_metricas": 21600,
    "ttl_min": 60,
    "ttl_max": 86400
}

# Configurações de coleta centralizadas (migradas de infrastructure/coleta/config.py)
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

# Configurações de validação centralizadas (migradas de infrastructure/coleta/config.py)
VALIDACAO_CONFIG = {
    "min_volume": 10,
    "max_volume": 1000000,
    "min_concorrencia": 0.0,
    "max_concorrencia": 1.0,
    "min_caracteres": 3,
    "max_caracteres": 100,
    "caracteres_permitidos": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ "
}

# Configurações de tendências centralizadas
TRENDS_CONFIG = {
    "janela_padrao": 7,  # dias
    "janela_sazonalidade": 90,  # dias
    "threshold_variacao": 10,  # porcentagem
    "min_dados_sazonalidade": 14,  # dias
    "janela_analise": 30
}

# Configurações de Instagram centralizadas
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

# Configurações de YouTube centralizadas
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

# Configurações de análise de sentimento centralizadas
SENTIMENT_CONFIG = {
    "threshold_positivo": 0.3,
    "threshold_negativo": -0.3,
    "max_comentarios": 100,
    "idiomas": ["pt", "en"]
}

# Idioma padrão para processamento de keywords
DEFAULT_IDIOMA = "pt"

def get_config(key: str):
    """Recupera uma configuração global pelo nome da variável."""
    return globals().get(key, None) 
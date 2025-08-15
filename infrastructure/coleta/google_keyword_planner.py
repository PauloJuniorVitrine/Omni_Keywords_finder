"""
Google Keyword Planner Integration
Integração completa com Google Keyword Planner via API oficial e web scraping

Prompt: Integração Google Keyword Planner
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-20
Versão: 1.0.0
"""

import os
import json
import time
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from infrastructure.coleta.base_keyword import KeywordColetorBase
from domain.models import Keyword, IntencaoBusca
from shared.logger import logger
from shared.config import APIConfig

# Integração com padrões de resiliência da Fase 1
from infrastructure.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, circuit_breaker
from infrastructure.resilience.retry_strategy import RetryConfig, RetryStrategy, retry
from infrastructure.resilience.bulkhead import BulkheadConfig, bulkhead
from infrastructure.resilience.timeout_manager import TimeoutConfig, timeout

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KeywordPlannerData:
    """Estrutura para dados do Google Keyword Planner"""
    keyword: str
    avg_monthly_searches: int
    competition: str
    low_top_of_page_bid: float
    high_top_of_page_bid: float
    suggested_bid: float
    search_volume_trend: List[int]
    competition_index: float
    low_competition_bid: float
    high_competition_bid: float
    year_over_year_change: float
    seasonality: Dict[str, float]

class GoogleKeywordPlannerColetor(KeywordColetorBase):
    """
    Coletor especializado para Google Keyword Planner
    
    Funcionalidades:
    - Integração via Google Ads API (oficial)
    - Fallback para web scraping
    - Cache inteligente
    - Rate limiting adaptativo
    - Análise de tendências
    - Sugestões de keywords
    - Análise de concorrência
    - Padrões de resiliência da Fase 1
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("google_keyword_planner", config)
        
        # Configurações específicas
        self.api_enabled = config.get("api_enabled", True)
        self.scraping_enabled = config.get("scraping_enabled", True)
        self.max_keywords_per_request = config.get("max_keywords_per_request", 100)
        self.rate_limit_delay = config.get("rate_limit_delay", 2.0)
        
        # Google Ads API
        self.credentials = None
        self.service = None
        self.customer_id = config.get("customer_id")
        
        # Web scraping
        self.driver = None
        self.session = requests.Session()
        
        # Configurações de resiliência da Fase 1
        self._setup_resilience_patterns()
        
        # Inicializar APIs
        if self.api_enabled:
            self._init_google_ads_api()
        
        if self.scraping_enabled:
            self._init_web_scraping()

    def _setup_resilience_patterns(self):
        """Configura os padrões de resiliência da Fase 1"""
        # Circuit Breaker para API do Google
        self.api_circuit_breaker = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                name="google_ads_api",
                fallback_function=self._fallback_api_error
            )
        )
        
        # Circuit Breaker para web scraping
        self.scraping_circuit_breaker = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30,
                name="google_scraping",
                fallback_function=self._fallback_scraping_error
            )
        )
        
        # Configurações de retry
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=10.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF
        )
        
        # Configurações de bulkhead
        self.bulkhead_config = BulkheadConfig(
            max_concurrent_calls=5,
            max_wait_duration=10.0,
            max_failure_count=3,
            name="google_keyword_planner"
        )
        
        # Configurações de timeout
        self.timeout_config = TimeoutConfig(
            timeout_seconds=30.0,
            name="google_keyword_planner"
        )

    def _fallback_api_error(self, *args, **kwargs):
        """Fallback quando API do Google falha"""
        logger.warning("API do Google falhou, usando fallback")
        return {"error": "API indisponível", "fallback": True}

    def _fallback_scraping_error(self, *args, **kwargs):
        """Fallback quando web scraping falha"""
        logger.warning("Web scraping falhou, usando fallback")
        return {"error": "Scraping indisponível", "fallback": True}

    def _init_google_ads_api(self):
        """Inicializa Google Ads API"""
        try:
            # Scopes necessários
            SCOPES = [
                'https://www.googleapis.com/auth/adwords',
                'https://www.googleapis.com/auth/analytics.readonly'
            ]
            
            # Carregar credenciais
            creds = None
            token_path = 'google_ads_token.json'
            
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # Se não há credenciais válidas, fazer login
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'google_ads_credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Salvar credenciais
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.credentials = creds
            
            # Construir serviço
            self.service = build('adwords', 'v201809', credentials=creds)
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "google_ads_api_initialized",
                "status": "success",
                "source": "google_keyword_planner._init_google_ads_api"
            })
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "google_ads_api_init_error",
                "status": "error",
                "source": "google_keyword_planner._init_google_ads_api",
                "details": {"erro": str(e)}
            })
            self.api_enabled = False

    def _init_web_scraping(self):
        """Inicializa web scraping como fallback"""
        try:
            # Configurar Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={self.user_agent}")
            
            # Configurar proxy se habilitado
            if self.proxy_enabled and self.proxy_config:
                chrome_options.add_argument(f"--proxy-server={self.proxy_config}")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "web_scraping_initialized",
                "status": "success",
                "source": "google_keyword_planner._init_web_scraping"
            })
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "web_scraping_init_error",
                "status": "error",
                "source": "google_keyword_planner._init_web_scraping",
                "details": {"erro": str(e)}
            })
            self.scraping_enabled = False

    @retry(max_attempts=3, base_delay=1.0, max_delay=10.0)
    @bulkhead(max_concurrent_calls=5, max_wait_duration=10.0)
    @timeout(timeout_seconds=30.0)
    async def extrair_sugestoes(self, termo: str) -> List[str]:
        """
        Extrai sugestões de keywords relacionadas via Google Keyword Planner com padrões de resiliência
        
        Args:
            termo: Termo base para busca
            
        Returns:
            Lista de sugestões relacionadas
        """
        try:
            # Verificar cache primeiro
            cache_key = f"keyword_planner_suggestions:{termo}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            
            suggestions = []
            
            # Tentar API primeiro com circuit breaker
            if self.api_enabled:
                try:
                    suggestions = await self.api_circuit_breaker.call(
                        self._get_suggestions_api, termo
                    )
                except Exception as e:
                    logger.warning({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "api_suggestions_failed",
                        "status": "warning",
                        "source": "google_keyword_planner.extrair_sugestoes",
                        "details": {"erro": str(e), "termo": termo}
                    })
            
            # Fallback para web scraping com circuit breaker
            if not suggestions and self.scraping_enabled:
                try:
                    suggestions = await self._get_suggestions_scraping(termo)
                except Exception as e:
                    logger.error({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "scraping_suggestions_failed",
                        "status": "error",
                        "source": "google_keyword_planner.extrair_sugestoes",
                        "details": {"erro": str(e), "termo": termo}
                    })
            
            # Salvar no cache
            if suggestions:
                await self.cache.set(cache_key, suggestions, ttl=3600)  # 1 hora
            
            return suggestions
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "extrair_sugestoes_error",
                "status": "error",
                "source": "google_keyword_planner.extrair_sugestoes",
                "details": {"erro": str(e), "termo": termo}
            })
            return []

    async def _get_suggestions_api(self, termo: str) -> List[str]:
        """Obtém sugestões via Google Ads API"""
        try:
            # Construir query para Keyword Planner
            query = {
                'ideaType': 'KEYWORD',
                'requestType': 'IDEAS',
                'keywordTextList': [termo],
                'language': 'pt',
                'locationNames': ['Brazil'],
                'networkSearchParameters': {
                    'network': 'GOOGLE_SEARCH'
                }
            }
            
            # Fazer requisição
            response = self.service.TargetingIdeaService().get(query)
            
            suggestions = []
            for result in response['entries']:
                if 'data' in result:
                    for data in result['data']:
                        if data['key'] == 'KEYWORD_TEXT':
                            suggestions.append(data['value'])
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            return suggestions[:self.max_keywords_per_request]
            
        except HttpError as e:
            if e.resp.status == 429:  # Rate limit
                logger.warning("Rate limit atingido, aguardando...")
                time.sleep(60)  # Aguardar 1 minuto
                return await self._get_suggestions_api(termo)
            else:
                raise e

    async def _get_suggestions_scraping(self, termo: str) -> List[str]:
        """Obtém sugestões via web scraping (fallback)"""
        try:
            # URL do Google Keyword Planner
            url = "https://ads.google.com/um/Welcome/Home"
            
            # Navegar para a página
            self.driver.get(url)
            
            # Aguardar carregamento
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search-box"))
            )
            
            # Preencher termo de busca
            search_box = self.driver.find_element(By.ID, "search-box")
            search_box.clear()
            search_box.send_keys(termo)
            
            # Clicar em buscar
            search_button = self.driver.find_element(By.ID, "search-button")
            search_button.click()
            
            # Aguardar resultados
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "keyword-suggestion"))
            )
            
            # Extrair sugestões
            suggestions = []
            suggestion_elements = self.driver.find_elements(By.CLASS_NAME, "keyword-suggestion")
            
            for element in suggestion_elements:
                keyword = element.find_element(By.CLASS_NAME, "keyword-text").text
                suggestions.append(keyword)
            
            return suggestions[:self.max_keywords_per_request]
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "scraping_suggestions_error",
                "status": "error",
                "source": "google_keyword_planner._get_suggestions_scraping",
                "details": {"erro": str(e), "termo": termo}
            })
            return []

    @retry(max_attempts=3, base_delay=1.0, max_delay=10.0)
    @bulkhead(max_concurrent_calls=5, max_wait_duration=10.0)
    @timeout(timeout_seconds=30.0)
    async def extrair_metricas_especificas(self, termo: str) -> Dict[str, Any]:
        """
        Extrai métricas específicas do Google Keyword Planner com padrões de resiliência
        
        Args:
            termo: Termo para extrair métricas
            
        Returns:
            Dicionário com métricas específicas
        """
        try:
            # Verificar cache
            cache_key = f"keyword_planner_metrics:{termo}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            
            metrics = {}
            
            # Tentar API primeiro com circuit breaker
            if self.api_enabled:
                try:
                    metrics = await self.api_circuit_breaker.call(
                        self._get_metrics_api, termo
                    )
                except Exception as e:
                    logger.warning({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "api_metrics_failed",
                        "status": "warning",
                        "source": "google_keyword_planner.extrair_metricas_especificas",
                        "details": {"erro": str(e), "termo": termo}
                    })
            
            # Fallback para web scraping com circuit breaker
            if not metrics and self.scraping_enabled:
                try:
                    metrics = await self.scraping_circuit_breaker.call(
                        self._get_metrics_scraping, termo
                    )
                except Exception as e:
                    logger.error({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "scraping_metrics_failed",
                        "status": "error",
                        "source": "google_keyword_planner.extrair_metricas_especificas",
                        "details": {"erro": str(e), "termo": termo}
                    })
            
            # Salvar no cache
            if metrics:
                await self.cache.set(cache_key, metrics, ttl=7200)  # 2 horas
            
            return metrics
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "extrair_metricas_error",
                "status": "error",
                "source": "google_keyword_planner.extrair_metricas_especificas",
                "details": {"erro": str(e), "termo": termo}
            })
            return self._get_default_metrics()

    async def _get_metrics_api(self, termo: str) -> Dict[str, Any]:
        """Obtém métricas via Google Ads API"""
        try:
            # Construir query para métricas
            query = {
                'ideaType': 'KEYWORD',
                'requestType': 'STATS',
                'keywordTextList': [termo],
                'language': 'pt',
                'locationNames': ['Brazil'],
                'networkSearchParameters': {
                    'network': 'GOOGLE_SEARCH'
                }
            }
            
            # Fazer requisição
            response = self.service.TargetingIdeaService().get(query)
            
            metrics = {}
            for result in response['entries']:
                if 'data' in result:
                    for data in result['data']:
                        if data['key'] == 'AVERAGE_MONTHLY_SEARCHES':
                            metrics['volume'] = int(data['value'])
                        elif data['key'] == 'COMPETITION':
                            metrics['concorrencia'] = self._parse_competition(data['value'])
                        elif data['key'] == 'LOW_TOP_OF_PAGE_BID':
                            metrics['cpc_min'] = float(data['value'])
                        elif data['key'] == 'HIGH_TOP_OF_PAGE_BID':
                            metrics['cpc_max'] = float(data['value'])
                        elif data['key'] == 'SUGGESTED_BID':
                            metrics['cpc_suggested'] = float(data['value'])
            
            # Calcular CPC médio
            if 'cpc_min' in metrics and 'cpc_max' in metrics:
                metrics['cpc'] = (metrics['cpc_min'] + metrics['cpc_max']) / 2
            elif 'cpc_suggested' in metrics:
                metrics['cpc'] = metrics['cpc_suggested']
            else:
                metrics['cpc'] = 0.0
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            return metrics
            
        except HttpError as e:
            if e.resp.status == 429:  # Rate limit
                logger.warning("Rate limit atingido, aguardando...")
                time.sleep(60)
                return await self._get_metrics_api(termo)
            else:
                raise e

    async def _get_metrics_scraping(self, termo: str) -> Dict[str, Any]:
        """Obtém métricas via web scraping (fallback)"""
        try:
            # URL específica para métricas
            url = f"https://ads.google.com/um/Welcome/Home#keyword-planner"
            
            # Navegar para a página
            self.driver.get(url)
            
            # Aguardar carregamento
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "keyword-metrics"))
            )
            
            # Buscar termo
            search_box = self.driver.find_element(By.ID, "keyword-input")
            search_box.clear()
            search_box.send_keys(termo)
            
            # Clicar em buscar
            search_button = self.driver.find_element(By.ID, "get-ideas-button")
            search_button.click()
            
            # Aguardar resultados
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "keyword-data"))
            )
            
            # Extrair métricas
            metrics = {}
            
            # Volume de busca
            volume_element = self.driver.find_element(By.CLASS_NAME, "avg-monthly-searches")
            metrics['volume'] = int(volume_element.text.replace(',', ''))
            
            # Concorrência
            competition_element = self.driver.find_element(By.CLASS_NAME, "competition")
            metrics['concorrencia'] = self._parse_competition(competition_element.text)
            
            # CPC
            cpc_element = self.driver.find_element(By.CLASS_NAME, "suggested-bid")
            metrics['cpc'] = float(cpc_element.text.replace('R$', '').replace(',', '.'))
            
            return metrics
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "scraping_metrics_error",
                "status": "error",
                "source": "google_keyword_planner._get_metrics_scraping",
                "details": {"erro": str(e), "termo": termo}
            })
            return self._get_default_metrics()

    def _parse_competition(self, competition_str: str) -> float:
        """Converte string de concorrência para float"""
        competition_map = {
            'LOW': 0.25,
            'MEDIUM': 0.5,
            'HIGH': 0.75,
            'Baixa': 0.25,
            'Média': 0.5,
            'Alta': 0.75
        }
        return competition_map.get(competition_str, 0.5)

    def _get_default_metrics(self) -> Dict[str, Any]:
        """Retorna métricas padrão em caso de erro"""
        return {
            'volume': 0,
            'cpc': 0.0,
            'concorrencia': 0.5,
            'intencao': IntencaoBusca.INFORMACIONAL
        }

    async def get_keyword_ideas(self, seed_keywords: List[str], 
                              language: str = 'pt', 
                              location: str = 'Brazil') -> List[Dict[str, Any]]:
        """
        Obtém ideias de keywords baseadas em termos semente
        
        Args:
            seed_keywords: Lista de termos semente
            language: Idioma (pt, en, es)
            location: Localização (Brazil, United States, etc.)
            
        Returns:
            Lista de ideias de keywords com métricas
        """
        try:
            if not self.api_enabled:
                logger.warning("API não disponível para keyword ideas")
                return []
            
            # Construir query
            query = {
                'ideaType': 'KEYWORD',
                'requestType': 'IDEAS',
                'keywordTextList': seed_keywords,
                'language': language,
                'locationNames': [location],
                'networkSearchParameters': {
                    'network': 'GOOGLE_SEARCH'
                }
            }
            
            # Fazer requisição
            response = self.service.TargetingIdeaService().get(query)
            
            ideas = []
            for result in response['entries']:
                idea = {}
                if 'data' in result:
                    for data in result['data']:
                        if data['key'] == 'KEYWORD_TEXT':
                            idea['keyword'] = data['value']
                        elif data['key'] == 'AVERAGE_MONTHLY_SEARCHES':
                            idea['avg_monthly_searches'] = int(data['value'])
                        elif data['key'] == 'COMPETITION':
                            idea['competition'] = data['value']
                        elif data['key'] == 'LOW_TOP_OF_PAGE_BID':
                            idea['low_top_of_page_bid'] = float(data['value'])
                        elif data['key'] == 'HIGH_TOP_OF_PAGE_BID':
                            idea['high_top_of_page_bid'] = float(data['value'])
                        elif data['key'] == 'SUGGESTED_BID':
                            idea['suggested_bid'] = float(data['value'])
                
                if idea:
                    ideas.append(idea)
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            return ideas
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "get_keyword_ideas_error",
                "status": "error",
                "source": "google_keyword_planner.get_keyword_ideas",
                "details": {"erro": str(e), "seed_keywords": seed_keywords}
            })
            return []

    async def get_historical_metrics(self, keyword: str, 
                                   start_date: str, 
                                   end_date: str) -> Dict[str, Any]:
        """
        Obtém métricas históricas de uma keyword
        
        Args:
            keyword: Termo para análise
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            
        Returns:
            Dicionário com métricas históricas
        """
        try:
            if not self.api_enabled:
                logger.warning("API não disponível para métricas históricas")
                return {}
            
            # Construir query para dados históricos
            query = {
                'ideaType': 'KEYWORD',
                'requestType': 'HISTORICAL_METRICS',
                'keywordTextList': [keyword],
                'language': 'pt',
                'locationNames': ['Brazil'],
                'dateRange': {
                    'min': start_date,
                    'max': end_date
                }
            }
            
            # Fazer requisição
            response = self.service.TargetingIdeaService().get(query)
            
            historical_data = {}
            for result in response['entries']:
                if 'data' in result:
                    for data in result['data']:
                        if data['key'] == 'HISTORICAL_QUALITY_SCORE':
                            historical_data['quality_score'] = int(data['value'])
                        elif data['key'] == 'HISTORICAL_CREATIVE_QUALITY_SCORE':
                            historical_data['creative_quality'] = int(data['value'])
                        elif data['key'] == 'HISTORICAL_POST_CLICK_QUALITY_SCORE':
                            historical_data['post_click_quality'] = int(data['value'])
                        elif data['key'] == 'HISTORICAL_SEARCH_PREDICTED_CTR':
                            historical_data['predicted_ctr'] = float(data['value'])
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            return historical_data
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "get_historical_metrics_error",
                "status": "error",
                "source": "google_keyword_planner.get_historical_metrics",
                "details": {"erro": str(e), "keyword": keyword}
            })
            return {}

    def __del__(self):
        """Cleanup ao destruir o objeto"""
        if self.driver:
            self.driver.quit() 
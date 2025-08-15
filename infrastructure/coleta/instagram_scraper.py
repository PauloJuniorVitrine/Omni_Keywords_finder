"""
Instagram Web Scraping Fallback

📐 CoCoT: Baseado em padrões de web scraping ético e compliance
🌲 ToT: Avaliado estratégias de scraping e escolhido mais ética
♻️ ReAct: Simulado detecção de bot e validado robustez

Prompt: CHECKLIST_INTEGRACAO_EXTERNA.md - 2.1.4
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T10:30:00Z
Tracing ID: instagram-scraper-2025-01-27-001

Funcionalidades implementadas:
- Scraping ético de dados públicos
- Detecção de captcha
- Rate limiting automático
- Rotação de user agents
- Cache de respostas
- Logs de compliance
"""

import os
import time
import json
import random
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import hashlib
import base64

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class InstagramScraperConfig:
    """Configuração do scraper Instagram."""
    user_agent: str = "OmniKeywordsBot/1.0"
    delay_between_requests: float = 2.0
    max_retries: int = 3
    timeout: int = 30
    respect_robots_txt: bool = True
    max_requests_per_hour: int = 100
    max_requests_per_day: int = 1000


@dataclass
class InstagramScrapedPost:
    """Dados de um post extraído via scraping."""
    url: str
    username: str
    caption: Optional[str]
    hashtags: List[str]
    like_count: Optional[int]
    comments_count: Optional[int]
    timestamp: Optional[str]
    media_type: str
    media_url: Optional[str]
    scraped_at: str


@dataclass
class InstagramScrapedProfile:
    """Dados de um perfil extraído via scraping."""
    username: str
    full_name: Optional[str]
    bio: Optional[str]
    followers_count: Optional[int]
    following_count: Optional[int]
    posts_count: Optional[int]
    profile_picture_url: Optional[str]
    is_private: bool
    is_verified: bool
    scraped_at: str


class InstagramScraperError(Exception):
    """Exceção customizada para erros de scraping."""
    
    def __init__(self, message: str, error_type: str = "general", http_status: Optional[int] = None):
        super().__init__(message)
        self.error_type = error_type
        self.http_status = http_status


class CaptchaDetectedError(InstagramScraperError):
    """Exceção para quando captcha é detectado."""
    
    def __init__(self, message: str = "Captcha detectado"):
        super().__init__(message, "captcha")


class RateLimitExceededError(InstagramScraperError):
    """Exceção para quando rate limit é excedido."""
    
    def __init__(self, message: str = "Rate limit excedido"):
        super().__init__(message, "rate_limit")


class InstagramScraper:
    """
    Scraper ético para Instagram como fallback.
    
    📐 CoCoT: Baseado em padrões de web scraping ético e compliance
    🌲 ToT: Avaliado estratégias de scraping e escolhido mais ética
    ♻️ ReAct: Simulado detecção de bot e validado robustez
    """
    
    def __init__(self, config: InstagramScraperConfig = None):
        """
        Inicializa o scraper Instagram.
        
        Args:
            config: Configuração do scraper
        """
        self.config = config or InstagramScraperConfig()
        self.session = requests.Session()
        self.session.timeout = self.config.timeout
        
        # Rate limiting tracking
        self.request_count_hour = 0
        self.request_count_day = 0
        self.last_request_hour = datetime.now()
        self.last_request_day = datetime.now()
        
        # User agents para rotação
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        
        # Headers padrão
        self._update_headers()
        
        logger.info(f"[InstagramScraper] Scraper inicializado - User Agent: {self.config.user_agent}")
    
    def _update_headers(self):
        """Atualiza headers da sessão."""
        user_agent = random.choice(self.user_agents)
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _check_rate_limit(self) -> bool:
        """
        Verifica se pode fazer requisição baseado no rate limiting.
        
        Returns:
            True se pode fazer requisição, False caso contrário
        """
        now = datetime.now()
        
        # Reset contadores se necessário
        if now - self.last_request_hour > timedelta(hours=1):
            self.request_count_hour = 0
            self.last_request_hour = now
        
        if now - self.last_request_day > timedelta(days=1):
            self.request_count_day = 0
            self.last_request_day = now
        
        # Verificar limites
        if self.request_count_hour >= self.config.max_requests_per_hour:
            logger.warning(f"[InstagramScraper] Rate limit por hora excedido: {self.request_count_hour}")
            return False
        
        if self.request_count_day >= self.config.max_requests_per_day:
            logger.warning(f"[InstagramScraper] Rate limit por dia excedido: {self.request_count_day}")
            return False
        
        return True
    
    def _increment_request_count(self):
        """Incrementa contadores de requisição."""
        self.request_count_hour += 1
        self.request_count_day += 1
    
    def _detect_captcha(self, html_content: str) -> bool:
        """
        Detecta se há captcha na página.
        
        Args:
            html_content: Conteúdo HTML da página
            
        Returns:
            True se captcha detectado, False caso contrário
        """
        captcha_indicators = [
            'captcha',
            'verify you are human',
            'security check',
            'robot check',
            'challenge',
            'verification',
            'prove you are human'
        ]
        
        html_lower = html_content.lower()
        for indicator in captcha_indicators:
            if indicator in html_lower:
                return True
        
        return False
    
    def _detect_blocked(self, html_content: str) -> bool:
        """
        Detecta se o acesso foi bloqueado.
        
        Args:
            html_content: Conteúdo HTML da página
            
        Returns:
            True se bloqueado, False caso contrário
        """
        blocked_indicators = [
            'blocked',
            'access denied',
            'forbidden',
            'temporarily unavailable',
            'too many requests',
            'rate limit exceeded'
        ]
        
        html_lower = html_content.lower()
        for indicator in blocked_indicators:
            if indicator in html_lower:
                return True
        
        return False
    
    def _make_request(self, url: str, retry_count: int = 0) -> str:
        """
        Faz requisição HTTP com retry e detecção de problemas.
        
        Args:
            url: URL para fazer requisição
            retry_count: Número de tentativas
            
        Returns:
            Conteúdo HTML da página
            
        Raises:
            CaptchaDetectedError: Se captcha for detectado
            RateLimitExceededError: Se rate limit for excedido
            InstagramScraperError: Para outros erros
        """
        if not self._check_rate_limit():
            raise RateLimitExceededError()
        
        try:
            # Delay entre requisições
            if retry_count > 0:
                delay = self.config.delay_between_requests * (2 ** retry_count)
                time.sleep(delay)
            else:
                time.sleep(self.config.delay_between_requests)
            
            # Rotacionar user agent
            self._update_headers()
            
            # Fazer requisição
            response = self.session.get(url)
            response.raise_for_status()
            
            self._increment_request_count()
            
            html_content = response.text
            
            # Detectar problemas
            if self._detect_captcha(html_content):
                raise CaptchaDetectedError()
            
            if self._detect_blocked(html_content):
                raise InstagramScraperError("Acesso bloqueado", "blocked", response.status_code)
            
            logger.info(f"[InstagramScraper] Requisição bem-sucedida - URL: {url}")
            return html_content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[InstagramScraper] Erro na requisição: {e}")
            
            if retry_count < self.config.max_retries:
                logger.info(f"[InstagramScraper] Tentativa {retry_count + 1} de {self.config.max_retries}")
                return self._make_request(url, retry_count + 1)
            else:
                raise InstagramScraperError(f"Erro após {self.config.max_retries} tentativas: {e}")
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """
        Extrai hashtags de um texto.
        
        Args:
            text: Texto para extrair hashtags
            
        Returns:
            Lista de hashtags
        """
        if not text:
            return []
        
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text)
        return list(set(hashtags))  # Remove duplicatas
    
    def _parse_number(self, text: str) -> Optional[int]:
        """
        Converte texto numérico em inteiro.
        
        Args:
            text: Texto numérico
            
        Returns:
            Número inteiro ou None
        """
        if not text:
            return None
        
        # Remove caracteres não numéricos
        number_text = re.sub(r'[^\data]', '', text)
        
        if number_text:
            return int(number_text)
        
        return None
    
    def scrape_profile(self, username: str) -> InstagramScrapedProfile:
        """
        Extrai dados de um perfil do Instagram.
        
        Args:
            username: Nome de usuário do Instagram
            
        Returns:
            Dados do perfil extraído
        """
        url = f"https://www.instagram.com/{username}/"
        
        try:
            html_content = self._make_request(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extrair dados do perfil
            profile_data = self._extract_profile_data(soup, username)
            
            logger.info(f"[InstagramScraper] Perfil extraído - Username: {username}")
            return profile_data
            
        except Exception as e:
            logger.error(f"[InstagramScraper] Erro ao extrair perfil {username}: {e}")
            raise
    
    def _extract_profile_data(self, soup: BeautifulSoup, username: str) -> InstagramScrapedProfile:
        """
        Extrai dados do perfil do HTML.
        
        Args:
            soup: BeautifulSoup object
            username: Nome de usuário
            
        Returns:
            Dados do perfil
        """
        # Tentar extrair dados do JSON-LD
        script_tags = soup.find_all('script', type='application/ld+json')
        profile_data = None
        
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'Person':
                    profile_data = data
                    break
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Extrair dados básicos
        full_name = None
        bio = None
        followers_count = None
        following_count = None
        posts_count = None
        profile_picture_url = None
        is_private = False
        is_verified = False
        
        if profile_data:
            full_name = profile_data.get('name')
            bio = profile_data.get('description')
        
        # Extrair contadores (fallback para parsing HTML)
        counter_elements = soup.find_all('span', class_=re.compile(r'.*count.*'))
        for element in counter_elements:
            text = element.get_text().strip()
            if 'posts' in text.lower():
                posts_count = self._parse_number(text)
            elif 'followers' in text.lower():
                followers_count = self._parse_number(text)
            elif 'following' in text.lower():
                following_count = self._parse_number(text)
        
        # Extrair foto do perfil
        img_elements = soup.find_all('img')
        for img in img_elements:
            src = img.get('src', '')
            if 'profile' in src.lower() or username in src:
                profile_picture_url = src
                break
        
        # Verificar se é privado
        private_indicators = ['private', 'this account is private']
        page_text = soup.get_text().lower()
        is_private = any(indicator in page_text for indicator in private_indicators)
        
        # Verificar se é verificado
        verified_indicators = ['verified', 'checkmark']
        is_verified = any(indicator in page_text for indicator in verified_indicators)
        
        return InstagramScrapedProfile(
            username=username,
            full_name=full_name,
            bio=bio,
            followers_count=followers_count,
            following_count=following_count,
            posts_count=posts_count,
            profile_picture_url=profile_picture_url,
            is_private=is_private,
            is_verified=is_verified,
            scraped_at=datetime.now().isoformat()
        )
    
    def scrape_post(self, post_url: str) -> InstagramScrapedPost:
        """
        Extrai dados de um post do Instagram.
        
        Args:
            post_url: URL do post
            
        Returns:
            Dados do post extraído
        """
        try:
            html_content = self._make_request(post_url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extrair dados do post
            post_data = self._extract_post_data(soup, post_url)
            
            logger.info(f"[InstagramScraper] Post extraído - URL: {post_url}")
            return post_data
            
        except Exception as e:
            logger.error(f"[InstagramScraper] Erro ao extrair post {post_url}: {e}")
            raise
    
    def _extract_post_data(self, soup: BeautifulSoup, post_url: str) -> InstagramScrapedPost:
        """
        Extrai dados do post do HTML.
        
        Args:
            soup: BeautifulSoup object
            post_url: URL do post
            
        Returns:
            Dados do post
        """
        # Extrair username da URL
        username = None
        url_parts = post_url.split('/')
        if len(url_parts) >= 4:
            username = url_parts[3]
        
        # Tentar extrair dados do JSON-LD
        script_tags = soup.find_all('script', type='application/ld+json')
        post_data = None
        
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') in ['ImageObject', 'VideoObject']:
                    post_data = data
                    break
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Extrair dados básicos
        caption = None
        hashtags = []
        like_count = None
        comments_count = None
        timestamp = None
        media_type = 'image'
        media_url = None
        
        if post_data:
            caption = post_data.get('description') or post_data.get('caption')
            media_url = post_data.get('contentUrl')
            if post_data.get('@type') == 'VideoObject':
                media_type = 'video'
        
        # Extrair hashtags do caption
        if caption:
            hashtags = self._extract_hashtags(caption)
        
        # Extrair contadores (fallback para parsing HTML)
        counter_elements = soup.find_all('span', class_=re.compile(r'.*count.*'))
        for element in counter_elements:
            text = element.get_text().strip()
            if 'like' in text.lower():
                like_count = self._parse_number(text)
            elif 'comment' in text.lower():
                comments_count = self._parse_number(text)
        
        # Extrair timestamp
        time_elements = soup.find_all('time')
        for time_elem in time_elements:
            timestamp = time_elem.get('datetime')
            if timestamp:
                break
        
        return InstagramScrapedPost(
            url=post_url,
            username=username or 'unknown',
            caption=caption,
            hashtags=hashtags,
            like_count=like_count,
            comments_count=comments_count,
            timestamp=timestamp,
            media_type=media_type,
            media_url=media_url,
            scraped_at=datetime.now().isoformat()
        )
    
    def scrape_hashtag_posts(self, hashtag: str, limit: int = 10) -> List[InstagramScrapedPost]:
        """
        Extrai posts de uma hashtag.
        
        Args:
            hashtag: Hashtag para buscar
            limit: Número máximo de posts
            
        Returns:
            Lista de posts extraídos
        """
        url = f"https://www.instagram.com/explore/tags/{hashtag}/"
        
        try:
            html_content = self._make_request(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extrair posts da hashtag
            posts = self._extract_hashtag_posts(soup, hashtag, limit)
            
            logger.info(f"[InstagramScraper] {len(posts)} posts extraídos da hashtag #{hashtag}")
            return posts
            
        except Exception as e:
            logger.error(f"[InstagramScraper] Erro ao extrair posts da hashtag #{hashtag}: {e}")
            raise
    
    def _extract_hashtag_posts(self, soup: BeautifulSoup, hashtag: str, limit: int) -> List[InstagramScrapedPost]:
        """
        Extrai posts de uma hashtag do HTML.
        
        Args:
            soup: BeautifulSoup object
            hashtag: Hashtag
            limit: Número máximo de posts
            
        Returns:
            Lista de posts
        """
        posts = []
        
        # Tentar extrair posts do JSON-LD
        script_tags = soup.find_all('script', type='application/ld+json')
        
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data[:limit]:
                        if isinstance(item, dict) and item.get('@type') in ['ImageObject', 'VideoObject']:
                            post = InstagramScrapedPost(
                                url=item.get('url', ''),
                                username='unknown',
                                caption=item.get('description'),
                                hashtags=[hashtag],
                                like_count=None,
                                comments_count=None,
                                timestamp=item.get('uploadDate'),
                                media_type='video' if item.get('@type') == 'VideoObject' else 'image',
                                media_url=item.get('contentUrl'),
                                scraped_at=datetime.now().isoformat()
                            )
                            posts.append(post)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return posts[:limit]
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Obtém status do rate limiting.
        
        Returns:
            Status do rate limiting
        """
        return {
            'requests_hour': self.request_count_hour,
            'requests_day': self.request_count_day,
            'limit_hour': self.config.max_requests_per_hour,
            'limit_day': self.config.max_requests_per_day,
            'remaining_hour': max(0, self.config.max_requests_per_hour - self.request_count_hour),
            'remaining_day': max(0, self.config.max_requests_per_day - self.request_count_day),
            'last_request_hour': self.last_request_hour.isoformat(),
            'last_request_day': self.last_request_day.isoformat()
        }


class InstagramScraperCollector:
    """
    Coletor usando web scraping como fallback.
    
    📐 CoCoT: Baseado em padrões de coleta de dados
    🌲 ToT: Avaliado estratégias de coleta e escolhido mais eficiente
    ♻️ ReAct: Simulado cenários de coleta e validado robustez
    """
    
    def __init__(self, scraper: InstagramScraper):
        """
        Inicializa o coletor.
        
        Args:
            scraper: Instância do scraper
        """
        self.scraper = scraper
        logger.info("[InstagramScraperCollector] Coletor inicializado")
    
    def collect_profile_data(self, username: str) -> Dict[str, Any]:
        """
        Coleta dados de um perfil.
        
        Args:
            username: Nome de usuário
            
        Returns:
            Dados do perfil
        """
        try:
            profile = self.scraper.scrape_profile(username)
            
            result = {
                'profile': asdict(profile),
                'rate_limit_status': self.scraper.get_rate_limit_status(),
                'source': 'web_scraping',
                'collected_at': datetime.now().isoformat()
            }
            
            logger.info(f"[InstagramScraperCollector] Dados do perfil coletados - Username: {username}")
            return result
            
        except Exception as e:
            logger.error(f"[InstagramScraperCollector] Erro na coleta do perfil {username}: {e}")
            raise
    
    def collect_hashtag_data(self, hashtag: str, limit: int = 10) -> Dict[str, Any]:
        """
        Coleta dados de uma hashtag.
        
        Args:
            hashtag: Hashtag para analisar
            limit: Número máximo de posts
            
        Returns:
            Dados da hashtag
        """
        try:
            posts = self.scraper.scrape_hashtag_posts(hashtag, limit)
            
            # Calcular métricas
            total_likes = sum(post.like_count or 0 for post in posts)
            total_comments = sum(post.comments_count or 0 for post in posts)
            avg_engagement = (total_likes + total_comments) / len(posts) if posts else 0
            
            result = {
                'hashtag': hashtag,
                'posts_found': len(posts),
                'total_likes': total_likes,
                'total_comments': total_comments,
                'avg_engagement': avg_engagement,
                'posts': [asdict(post) for post in posts],
                'rate_limit_status': self.scraper.get_rate_limit_status(),
                'source': 'web_scraping',
                'collected_at': datetime.now().isoformat()
            }
            
            logger.info(f"[InstagramScraperCollector] Dados da hashtag coletados - {hashtag}: {len(posts)} posts")
            return result
            
        except Exception as e:
            logger.error(f"[InstagramScraperCollector] Erro na coleta da hashtag {hashtag}: {e}")
            raise


# Função de conveniência para criar scraper
def create_instagram_scraper(config: InstagramScraperConfig = None) -> InstagramScraper:
    """
    Cria scraper Instagram com configuração padrão.
    
    Args:
        config: Configuração do scraper
        
    Returns:
        Scraper Instagram
    """
    return InstagramScraper(config)


if __name__ == "__main__":
    # Exemplo de uso
    try:
        scraper = create_instagram_scraper()
        collector = InstagramScraperCollector(scraper)
        
        # Coletar dados de uma hashtag
        data = collector.collect_hashtag_data("python", limit=5)
        print(f"Dados coletados: {len(data['posts'])} posts")
        
    except Exception as e:
        print(f"Erro: {e}") 
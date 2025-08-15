"""
Coletor de keywords do Discord.
Extrai dados de servidores públicos, canais e mensagens.
"""
from typing import List, Dict, Optional, Set
import aiohttp
import asyncio
from datetime import datetime, timedelta
import re
from collections import defaultdict
import time
import uuid
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import pybreaker
from domain.models import Keyword, IntencaoBusca
from infrastructure.coleta.base import ColetorBase
from shared.logger import logger
from shared.config import get_config, DISCORD_CONFIG, CACHE_CONFIG
from shared.cache import AsyncCache
from shared.utils.normalizador_central import NormalizadorCentral
from infrastructure.processamento.validador_keywords import ValidadorKeywords
from infrastructure.coleta.utils.cache import CacheDistribuido

breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)

class RateLimiter:
    """Gerenciador de rate limits para requisições Discord."""
    
    def __init__(self, requests_per_second: int = 50):
        self.requests_per_second = requests_per_second
        self.requests = []
        self.lock = asyncio.Lock()
        
    async def acquire(self):
        """Aguarda até que seja seguro fazer uma nova requisição."""
        async with self.lock:
            now = datetime.utcnow()
            # Remove requisições antigas
            self.requests = [t for t in self.requests if now - t < timedelta(seconds=1)]
            
            if len(self.requests) >= self.requests_per_second:
                # Calcula tempo de espera
                oldest = min(self.requests)
                wait_time = 1 - (now - oldest).total_seconds()
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    
            self.requests.append(now)

class DiscordColetor(ColetorBase):
    """Implementação do coletor de keywords do Discord com análise avançada."""
    
    def __init__(self, logger_=None):
        """Inicializa o coletor com configurações específicas."""
        config = get_config("coletores.discord")
        if config is None:
            config = DISCORD_CONFIG
        super().__init__(
            nome="discord",
            config=config
        )
        self.logger = logger_ or logger
        self.base_url = "https://discord.com/api/v10"
        self.headers = {
            "Authorization": f"Bot {self.config['token']}",
            "User-Agent": "OmniKeywordsFinder/1.0"
        }
        self.session = None
        self.cache = AsyncCache(
            namespace=CACHE_CONFIG["namespaces"]["discord"],
            ttl=CACHE_CONFIG["ttl_padrao"]
        )
        # Normalizador central para padronização de keywords
        self.normalizador = NormalizadorCentral(
            remover_acentos=False,
            case_sensitive=False,
            caracteres_permitidos=r'^[\w\string_data\-,.!?@#]+$',
            min_caracteres=3,
            max_caracteres=100
        )
        self.rate_limiter = RateLimiter()
        self._servidores_cache = {}
        self._canais_cache = {}
        self._mensagens_cache = defaultdict(list)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria uma sessão HTTP."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    @breaker
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError))
    )
    async def extrair_sugestoes(self, termo: str) -> List[str]:
        """
        Extrai sugestões relacionadas ao termo no Discord com resiliência e logging estruturado.
        """
        uuid_req = str(uuid.uuid4())
        inicio = time.time()
        cache_key = f"sugestoes:{termo}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        try:
            servidores = await self._listar_servidores()
            sugestoes = set()
            for servidor in servidores:
                mensagens = await self._buscar_mensagens(
                    servidor["id"],
                    termo,
                    limite=100
                )
                for mensagem in mensagens:
                    hashtags = re.findall(r'#(\w+)', mensagem["content"])
                    sugestoes.update(hashtags)
                    canais = re.findall(r'<#(\data+)>', mensagem["content"])
                    for canal_id in canais:
                        try:
                            canal = await self._obter_canal(canal_id)
                            if canal and canal["name"] != termo:
                                sugestoes.add(canal["name"])
                        except Exception:
                            pass
                    palavras = re.findall(r'\b\w{4,}\b', mensagem["content"].lower())
                    for palavra in palavras:
                        if (
                            palavra != termo.lower() and
                            len(palavra) >= 4 and
                            not any(c in palavra for c in "!@#$%^&*()")
                        ):
                            sugestoes.add(palavra)
            sugestoes_lista = list(sugestoes)
            await self.cache.set(cache_key, sugestoes_lista)
            self.logger.info({
                "uuid": uuid_req,
                "coletor": "discord",
                "termo": termo,
                "status": "sucesso",
                "latencia_ms": int((time.time() - inicio) * 1000),
                "ambiente": self.config.get("env", "dev"),
                "total_sugestoes": len(sugestoes_lista)
            })
            return sugestoes_lista
        except Exception as e:
            self.logger.error({
                "uuid": uuid_req,
                "coletor": "discord",
                "termo": termo,
                "status": "erro",
                "erro": str(e),
                "latencia_ms": int((time.time() - inicio) * 1000),
                "ambiente": self.config.get("env", "dev")
            })
            # Fallback: retorna cache ou lista vazia
            return await self.cache.get(cache_key) or []

    async def extrair_metricas_especificas(self, termo: str) -> Dict:
        """
        Extrai métricas específicas do Discord.
        
        Args:
            termo: Termo para análise
            
        Returns:
            Dicionário com métricas do Discord
        """
        cache_key = f"metricas:{termo}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        try:
            # Busca em todos os servidores monitorados
            servidores = await self._listar_servidores()
            mensagens_total = []
            canais_termo = set()
            reacoes_total = 0
            threads_total = 0
            
            for servidor in servidores:
                # Busca mensagens com o termo
                mensagens = await self._buscar_mensagens(
                    servidor["id"],
                    termo,
                    limite=1000
                )
                mensagens_total.extend(mensagens)
                
                # Coleta dados dos canais
                for mensagem in mensagens:
                    canal_id = mensagem["channel_id"]
                    if canal_id not in canais_termo:
                        canais_termo.add(canal_id)
                        
                    # Conta reações
                    reacoes_total += sum(
                        reaction["count"]
                        for reaction in mensagem.get("reactions", [])
                    )
                    
                    # Verifica threads
                    if mensagem.get("thread"):
                        threads_total += 1
            
            try:
                # Analisa tendências
                tendencias = await self._analisar_tendencias(mensagens_total)
            except Exception as e:
                self.registrar_erro(
                    "Erro ao extrair métricas do Discord",
                    {"erro": str(e), "termo": termo}
                )
                tendencias = {}
            
            # Calcula métricas
            metricas = {
                "total_mensagens": len(mensagens_total),
                "total_canais": len(canais_termo),
                "total_reacoes": reacoes_total,
                "total_threads": threads_total,
                "mensagens": {
                    "por_canal": self._agrupar_por_canal(mensagens_total),
                    "por_autor": self._agrupar_por_autor(mensagens_total),
                    "tipos": self._analisar_tipos_mensagem(mensagens_total)
                },
                "engajamento": {
                    "reacoes_media": reacoes_total / max(1, len(mensagens_total)),
                    "threads_ratio": threads_total / max(1, len(mensagens_total))
                },
                "tendencias": tendencias
            }
            
            # Adiciona métricas calculadas
            metricas.update({
                "volume": self._calcular_volume(metricas),
                "concorrencia": self._calcular_concorrencia(metricas),
                "data_coleta": datetime.utcnow().isoformat()
            })
            
            await self.cache.set(cache_key, metricas)
            
            self.registrar_sucesso("extracao_metricas", {
                "termo": termo,
                "total_mensagens": metricas["total_mensagens"],
                "total_canais": metricas["total_canais"]
            })
            
            return metricas

        except Exception as e:
            self.registrar_erro(
                "Erro ao extrair métricas do Discord",
                {"erro": str(e), "termo": termo}
            )
            return {
                "total_mensagens": 0,
                "total_canais": 0,
                "volume": 0,
                "concorrencia": 0.5,
                "erro": str(e)
            }

    async def _listar_servidores(self) -> List[Dict]:
        """Lista servidores monitorados."""
        if self._servidores_cache:
            return list(self._servidores_cache.values())
            
        try:
            await self.rate_limiter.acquire()
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/users/@me/guilds") as response:
                if response.status != 200:
                    raise Exception(f"Erro ao listar servidores: {response.status}")
                    
                servidores = await response.json()
                
                # Atualiza cache
                self._servidores_cache = {
                    string_data["id"]: string_data for string_data in servidores
                }
                
                return servidores
                
        except Exception as e:
            self.registrar_erro(
                "Erro ao listar servidores",
                {"erro": str(e)}
            )
            return []

    async def _buscar_mensagens(
        self,
        servidor_id: str,
        termo: str,
        limite: int = 100
    ) -> List[Dict]:
        """
        Busca mensagens em um servidor.
        
        Args:
            servidor_id: ID do servidor
            termo: Termo para busca
            limite: Limite de mensagens
            
        Returns:
            Lista de mensagens encontradas
        """
        mensagens = []
        try:
            # Lista canais do servidor
            canais = await self._listar_canais(servidor_id)
            
            for canal in canais:
                if canal["type"] not in [0, 2]:  # Apenas canais de texto e voz
                    continue
                    
                try:
                    await self.rate_limiter.acquire()
                    session = await self._get_session()
                    
                    params = {
                        "limit": min(100, limite - len(mensagens)),
                        "content": termo
                    }
                    
                    async with session.get(
                        f"{self.base_url}/channels/{canal['id']}/messages/search",
                        params=params
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            mensagens.extend(data.get("messages", []))
                            
                            if len(mensagens) >= limite:
                                break
                                
                except Exception as e:
                    self.registrar_erro(
                        f"Erro ao buscar mensagens no canal {canal['id']}",
                        {"erro": str(e)}
                    )
                    
        except Exception as e:
            self.registrar_erro(
                f"Erro ao buscar mensagens no servidor {servidor_id}",
                {"erro": str(e)}
            )
            
        return mensagens[:limite]

    async def _listar_canais(self, servidor_id: str) -> List[Dict]:
        """Lista canais de um servidor."""
        if servidor_id in self._canais_cache:
            return self._canais_cache[servidor_id]
            
        try:
            await self.rate_limiter.acquire()
            session = await self._get_session()
            
            async with session.get(
                f"{self.base_url}/guilds/{servidor_id}/channels"
            ) as response:
                if response.status != 200:
                    raise Exception(f"Erro ao listar canais: {response.status}")
                    
                canais = await response.json()
                
                # Atualiza cache
                self._canais_cache[servidor_id] = canais
                return canais
                
        except Exception as e:
            self.registrar_erro(
                f"Erro ao listar canais do servidor {servidor_id}",
                {"erro": str(e)}
            )
            return []

    async def _obter_canal(self, canal_id: str) -> Optional[Dict]:
        """Obtém informações de um canal específico."""
        try:
            await self.rate_limiter.acquire()
            session = await self._get_session()
            
            async with session.get(
                f"{self.base_url}/channels/{canal_id}"
            ) as response:
                if response.status != 200:
                    raise Exception(f"Erro ao obter canal: {response.status}")
                    
                return await response.json()
                
        except Exception as e:
            self.registrar_erro(
                f"Erro ao obter canal {canal_id}",
                {"erro": str(e)}
            )
            return None

    async def _analisar_tendencias(self, mensagens: List[Dict]) -> Dict:
        """Analisa tendências nas mensagens."""
        try:
            # Agrupa por período
            periodos = defaultdict(list)
            agora = datetime.utcnow()
            
            for mensagem in mensagens:
                data = datetime.fromtimestamp(
                    int(mensagem["timestamp"]) / 1000
                )
                dias_atras = (agora - data).days
                
                if dias_atras <= 1:
                    periodos["24h"].append(mensagem)
                if dias_atras <= 7:
                    periodos["7d"].append(mensagem)
                if dias_atras <= 30:
                    periodos["30d"].append(mensagem)
                    
            # Calcula métricas por período
            tendencias = {}
            for periodo, msgs in periodos.items():
                tendencias[periodo] = {
                    "total_mensagens": len(msgs),
                    "media_reacoes": sum(
                        sum(r["count"] for r in m.get("reactions", []))
                        for m in msgs
                    ) / max(1, len(msgs)),
                    "canais_ativos": len({m["channel_id"] for m in msgs}),
                    "autores_unicos": len({m["author"]["id"] for m in msgs})
                }
                
            # Calcula crescimento
            if "7d" in tendencias and "30d" in tendencias:
                msgs_7d = tendencias["7d"]["total_mensagens"]
                msgs_30d = tendencias["30d"]["total_mensagens"]
                media_diaria_7d = msgs_7d / 7
                media_diaria_30d = msgs_30d / 30
                
                tendencias["crescimento"] = {
                    "percentual": ((media_diaria_7d - media_diaria_30d) / 
                                 max(1, media_diaria_30d)) * 100,
                    "absoluto": media_diaria_7d - media_diaria_30d
                }
                
            return tendencias
            
        except Exception as e:
            self.registrar_erro(
                "Erro ao analisar tendências",
                {"erro": str(e)}
            )
            return {}

    def _agrupar_por_canal(self, mensagens: List[Dict]) -> Dict[str, int]:
        """Agrupa mensagens por canal."""
        contagem = defaultdict(int)
        for mensagem in mensagens:
            contagem[mensagem["channel_id"]] += 1
        return dict(contagem)

    def _agrupar_por_autor(self, mensagens: List[Dict]) -> Dict[str, int]:
        """Agrupa mensagens por autor."""
        contagem = defaultdict(int)
        for mensagem in mensagens:
            contagem[mensagem["author"]["id"]] += 1
        return dict(contagem)

    def _analisar_tipos_mensagem(self, mensagens: List[Dict]) -> Dict[str, int]:
        """Analisa tipos de mensagem."""
        tipos = defaultdict(int)
        for mensagem in mensagens:
            if mensagem.get("attachments"):
                tipos["midia"] += 1
            if mensagem.get("embeds"):
                tipos["embed"] += 1
            if re.search(r'https?://\S+', mensagem["content"]):
                tipos["link"] += 1
            if mensagem.get("mentions"):
                tipos["mencao"] += 1
            if mensagem.get("thread"):
                tipos["thread"] += 1
            if not any([
                mensagem.get("attachments"),
                mensagem.get("embeds"),
                re.search(r'https?://\S+', mensagem["content"]),
                mensagem.get("mentions"),
                mensagem.get("thread")
            ]):
                tipos["texto"] += 1
        return dict(tipos)

    def _calcular_volume(self, metricas: Dict) -> int:
        """Calcula volume estimado baseado nas métricas."""
        total_mensagens = metricas.get("total_mensagens", 0)
        if total_mensagens == 0:
            return 10
        elif total_mensagens < 100:
            return 50
        elif total_mensagens < 1000:
            return 100
        elif total_mensagens < 10000:
            return 500
        else:
            return 1000

    def _calcular_concorrencia(self, metricas: Dict) -> float:
        """Calcula nível de concorrência baseado nas métricas."""
        try:
            # Base na quantidade de mensagens
            total_mensagens = metricas.get("total_mensagens", 0)
            if total_mensagens == 0:
                return 0.1
                
            # Ajusta baseado no engajamento
            engajamento = metricas.get("engajamento", {})
            reacoes_media = engajamento.get("reacoes_media", 0)
            threads_ratio = engajamento.get("threads_ratio", 0)
            
            # Normaliza métricas
            reacoes_norm = min(1.0, reacoes_media / 10)
            threads_norm = min(1.0, threads_ratio)
            
            # Combina fatores
            concorrencia = min(1.0, (
                (total_mensagens / 1000) * 0.4 +  # Peso das mensagens
                reacoes_norm * 0.3 +              # Peso das reações
                threads_norm * 0.3                # Peso das threads
            ))
            
            return max(0.1, concorrencia)
            
        except Exception:
            return 0.5

    async def validar_termo_especifico(self, termo: str) -> bool:
        """
        Validação específica para o Discord.
        
        Args:
            termo: Termo a ser validado
            
        Returns:
            True se o termo é válido para o Discord
        """
        # Discord tem limite de caracteres na busca
        if len(termo) > 100:
            self.registrar_erro(
                "Termo muito longo para Discord",
                {"termo": termo}
            )
            return False
            
        return True

    async def __aenter__(self):
        """Gerenciamento de contexto para início de sessão."""
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Gerenciamento de contexto para fechamento de sessão."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def coletar_keywords(self, termo: str, limite: int = 100) -> List[Keyword]:
        """
        Coleta keywords relacionadas ao termo fornecido.
        
        Args:
            termo: Termo base para busca de keywords relacionadas
            limite: Número máximo de keywords a retornar
            
        Returns:
            Lista de objetos Keyword com dados preenchidos
        """
        sugestoes = await self.extrair_sugestoes(termo)
        metricas = await self.extrair_metricas_especificas(termo)
        
        keywords = []
        for sugestao in sugestoes[:limite]:
            keyword = Keyword(
                termo=sugestao,
                fonte=self.nome,
                volume=metricas.get("volume", 0),
                concorrencia=metricas.get("concorrencia", 0.5)
            )
            keywords.append(keyword)
            
        return keywords

    async def classificar_intencao(self, keywords: List[str]) -> List[IntencaoBusca]:
        """
        Classifica a intenção de busca para uma lista de keywords.
        
        Args:
            keywords: Lista de termos para classificar
            
        Returns:
            Lista de enums IntencaoBusca classificando cada keyword
        """
        intencoes = []
        for termo in keywords:
            # Por padrão, considera todas as keywords do Discord como informacionais
            intencoes.append(IntencaoBusca.INFORMACIONAL)
        return intencoes

    async def coletar_metricas(self, keywords: List[str]) -> List[Dict]:
        """
        Coleta métricas para uma lista de keywords.
        
        Args:
            keywords: Lista de termos para coletar métricas
            
        Returns:
            Lista de dicionários com métricas por keyword
        """
        metricas = []
        for termo in keywords:
            try:
                metricas_termo = await self.extrair_metricas_especificas(termo)
                metricas.append({
                    "termo": termo,
                    "volume": metricas_termo.get("volume", 0),
                    "concorrencia": metricas_termo.get("concorrencia", 0.5),
                    "total_mensagens": metricas_termo.get("total_mensagens", 0),
                    "total_canais": metricas_termo.get("total_canais", 0),
                    "total_reacoes": metricas_termo.get("total_reacoes", 0),
                    "total_threads": metricas_termo.get("total_threads", 0)
                })
            except Exception as e:
                self.registrar_erro(
                    "Erro ao coletar métricas",
                    {"termo": termo, "erro": str(e)}
                )
                metricas.append({
                    "termo": termo,
                    "erro": str(e)
                })
        return metricas 
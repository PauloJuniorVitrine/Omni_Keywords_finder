"""
Classes base para implementação de coletores de dados.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional, Any
from domain.models import Keyword, IntencaoBusca
from shared.logger import logger
import aiohttp
import json
import asyncio

class ColetorBase(ABC):
    """Classe base abstrata para implementação de coletores de dados."""

    def __init__(self, nome: str, config: Dict):
        """Inicializa o coletor com configurações básicas."""
        self.nome = nome
        self.config = config
        self.ultima_execucao: Optional[datetime] = None
        self.total_coletado: int = 0
        self.erros: List[str] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        self.proxy_enabled = config.get("proxy_enabled", False)
        self.proxy_config = config.get("proxy_config", None)
        self._session_lock = asyncio.Lock()

    async def __aenter__(self):
        """Gerencia o contexto assíncrono."""
        async with self._session_lock:
            if not self.session or self.session.closed:
                self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fecha a sessão ao sair do contexto."""
        async with self._session_lock:
            if self.session and not self.session.closed:
                await self.session.close()
                self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Retorna a sessão HTTP atual ou cria uma nova.
        
        Returns:
            Sessão HTTP ativa
        """
        async with self._session_lock:
            if not self.session or self.session.closed:
                self.session = aiohttp.ClientSession(headers=self.headers)
            return self.session

    @abstractmethod
    async def coletar_keywords(self, termo: str, limite: int = 100) -> List[Keyword]:
        """
        Coleta keywords relacionadas ao termo fornecido.
        
        Args:
            termo: Termo base para busca
            limite: Número máximo de keywords a retornar
            
        Returns:
            Lista de objetos Keyword com dados preenchidos
        """
        pass

    @abstractmethod
    async def coletar_metricas(self, keywords: List[str]) -> List[Dict]:
        """
        Coleta métricas para uma lista de keywords.
        
        Args:
            keywords: Lista de termos para coletar métricas
            
        Returns:
            Lista de dicionários com métricas por keyword
        """
        pass

    @abstractmethod
    async def classificar_intencao(self, keywords: List[str]) -> List[IntencaoBusca]:
        """
        Classifica a intenção de busca para uma lista de keywords.
        
        Args:
            keywords: Lista de termos para classificar
            
        Returns:
            Lista de enums IntencaoBusca classificando cada keyword
        """
        pass

    def registrar_erro(self, mensagem: str, detalhes: Dict[str, Any]) -> None:
        """
        Registra um erro ocorrido durante a execução.
        
        Args:
            mensagem: Descrição do erro
            detalhes: Detalhes adicionais do erro
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event": "erro_coletor",
            "status": "error",
            "source": f"coletor.{self.nome}",
            "message": mensagem,
            "details": detalhes
        }
        
        # Registra no logger
        logger.error(json.dumps(log_data))
        
        # Adiciona à lista de erros
        self.erros.append(f"{mensagem}: {detalhes}")

    def registrar_sucesso(self, evento: str, detalhes: Dict[str, Any]) -> None:
        """
        Registra um evento de sucesso.
        
        Args:
            evento: Nome do evento
            detalhes: Detalhes do evento
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event": evento,
            "status": "success",
            "source": f"coletor.{self.nome}",
            "details": detalhes
        }
        
        # Registra no logger
        logger.info(json.dumps(log_data))

    def atualizar_metricas(self, total_coletado: int) -> None:
        """
        Atualiza as métricas do coletor.
        
        Args:
            total_coletado: Total de itens coletados
        """
        self.total_coletado += total_coletado
        self.ultima_execucao = datetime.now()
        
        self.registrar_sucesso(
            "atualizacao_metricas",
            {
                "total_coletado": self.total_coletado,
                "ultima_execucao": self.ultima_execucao.isoformat()
            }
        )

    async def validar_termo(self, termo: str) -> bool:
        """
        Valida um termo antes da coleta.
        
        Args:
            termo: Termo a ser validado
            
        Returns:
            True se o termo é válido, False caso contrário
        """
        if not termo or len(termo.strip()) == 0:
            self.registrar_erro(
                "Termo vazio",
                {
                    "termo": termo
                }
            )
            return False
            
        if len(termo) > self.config.get("max_termo_length", 100):
            self.registrar_erro(
                "Termo muito longo",
                {
                    "termo": termo,
                    "tamanho": len(termo),
                    "maximo": self.config.get("max_termo_length", 100)
                }
            )
            return False
            
        return True

    async def validar_termo_especifico(self, termo: str) -> bool:
        """
        Validação específica do termo para cada coletor.
        
        Args:
            termo: Termo a ser validado
            
        Returns:
            True se o termo é válido, False caso contrário
        """
        if not termo or len(termo.strip()) == 0:
            self.registrar_erro(
                "Termo vazio",
                {
                    "termo": termo
                }
            )
            return False
            
        return True 
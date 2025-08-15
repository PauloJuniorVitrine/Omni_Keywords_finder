"""
Interface Base para Validadores Especializados
Define contrato para validadores de diferentes fontes

Prompt: Google Keyword Planner como Validador
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-20
Versão: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from domain.models import Keyword
from shared.logger import logger
from datetime import datetime

class ValidadorEspecializado(ABC):
    """
    Interface base para validadores especializados.
    
    Cada validador especializado deve implementar:
    - Validação de keywords usando fonte específica
    - Obtenção de métricas específicas
    - Prioridade de execução
    - Configuração de cache e rate limiting
    """
    
    def __init__(self, nome: str, config: Dict[str, Any]):
        """
        Inicializa validador especializado.
        
        Args:
            nome: Nome do validador
            config: Configurações específicas
        """
        self.nome = nome
        self.config = config
        self.enabled = config.get("enabled", True)
        self.cache_enabled = config.get("cache_enabled", True)
        self.rate_limiting_enabled = config.get("rate_limiting_enabled", True)
        
        # Métricas de execução
        self.total_validated = 0
        self.total_rejected = 0
        self.execution_time = 0.0
        self.last_execution = None
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "validador_especializado_inicializado",
            "status": "success",
            "source": f"{self.nome}.__init__",
            "details": {
                "nome": self.nome,
                "enabled": self.enabled,
                "cache_enabled": self.cache_enabled,
                "rate_limiting_enabled": self.rate_limiting_enabled
            }
        })
    
    @abstractmethod
    def validar_keywords(self, keywords: List[Keyword]) -> List[Keyword]:
        """
        Valida lista de keywords usando fonte especializada.
        
        Args:
            keywords: Lista de keywords a validar
            
        Returns:
            Lista de keywords aprovadas pela validação
        """
        pass
    
    @abstractmethod
    def obter_metricas(self, keyword: str) -> Dict[str, Any]:
        """
        Obtém métricas específicas da fonte para uma keyword.
        
        Args:
            keyword: Termo para obter métricas
            
        Returns:
            Dicionário com métricas específicas
        """
        pass
    
    @abstractmethod
    def get_prioridade(self) -> int:
        """
        Retorna prioridade de execução do validador (1-10).
        
        Returns:
            Prioridade (1 = mais alta, 10 = mais baixa)
        """
        pass
    
    def get_nome(self) -> str:
        """Retorna nome do validador."""
        return self.nome
    
    def is_enabled(self) -> bool:
        """Verifica se validador está habilitado."""
        return self.enabled
    
    def get_estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de execução do validador.
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            "nome": self.nome,
            "total_validated": self.total_validated,
            "total_rejected": self.total_rejected,
            "execution_time": self.execution_time,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "taxa_rejeicao": (self.total_rejected / (self.total_validated + self.total_rejected)) if (self.total_validated + self.total_rejected) > 0 else 0.0
        }
    
    def reset_estatisticas(self):
        """Reseta estatísticas de execução."""
        self.total_validated = 0
        self.total_rejected = 0
        self.execution_time = 0.0
        self.last_execution = None
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "estatisticas_resetadas",
            "status": "info",
            "source": f"{self.nome}.reset_estatisticas"
        })
    
    def _registrar_execucao(self, keywords_iniciais: int, keywords_finais: int, tempo_execucao: float):
        """
        Registra métricas de execução.
        
        Args:
            keywords_iniciais: Número de keywords antes da validação
            keywords_finais: Número de keywords após validação
            tempo_execucao: Tempo de execução em segundos
        """
        self.total_validated += keywords_finais
        self.total_rejected += (keywords_iniciais - keywords_finais)
        self.execution_time += tempo_execucao
        self.last_execution = datetime.utcnow()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "validacao_executada",
            "status": "success",
            "source": f"{self.nome}._registrar_execucao",
            "details": {
                "keywords_iniciais": keywords_iniciais,
                "keywords_finais": keywords_finais,
                "rejeitadas": keywords_iniciais - keywords_finais,
                "tempo_execucao": tempo_execucao,
                "taxa_aprovacao": keywords_finais / keywords_iniciais if keywords_iniciais > 0 else 0.0
            }
        }) 
"""
Utilitário para implementação de retry pattern com backoff exponencial.
"""
import asyncio
import random
from typing import TypeVar, Callable, Awaitable
from functools import wraps
from shared.logger import logger

T = TypeVar('T')

class RetryConfig:
    """Configuração para o retry pattern."""
    
    def __init__(
        self,
        max_tentativas: int = 3,
        delay_inicial: float = 1.0,
        fator_multiplicador: float = 2.0,
        jitter: float = 0.1
    ):
        """
        Inicializa a configuração do retry.
        
        Args:
            max_tentativas: Número máximo de tentativas
            delay_inicial: Delay inicial em segundos
            fator_multiplicador: Fator para multiplicar o delay a cada tentativa
            jitter: Variação aleatória máxima para adicionar ao delay
        """
        self.max_tentativas = max_tentativas
        self.delay_inicial = delay_inicial
        self.fator_multiplicador = fator_multiplicador
        self.jitter = jitter

def with_retry(config: RetryConfig = RetryConfig()) -> Callable:
    """
    Decorator para adicionar retry pattern com backoff exponencial.
    
    Args:
        config: Configuração do retry pattern
        
    Returns:
        Decorator configurado
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            ultima_excecao = None
            
            for tentativa in range(config.max_tentativas):
                try:
                    return await func(*args, **kwargs)
                    
                except Exception as e:
                    ultima_excecao = e
                    if tentativa < config.max_tentativas - 1:
                        # Calcula delay com backoff exponencial e jitter
                        delay_base = config.delay_inicial * (config.fator_multiplicador ** tentativa)
                        jitter = random.uniform(0, config.jitter * delay_base)
                        delay_total = delay_base + jitter
                        
                        logger.warning(
                            "Erro na execução, tentando novamente",
                            extra={
                                "erro": str(e),
                                "tentativa": tentativa + 1,
                                "max_tentativas": config.max_tentativas,
                                "delay": delay_total
                            }
                        )
                        
                        await asyncio.sleep(delay_total)
                    else:
                        logger.error(
                            "Todas as tentativas falharam",
                            extra={
                                "erro": str(e),
                                "total_tentativas": config.max_tentativas
                            }
                        )
                        
            raise ultima_excecao
            
        return wrapper
    return decorator 
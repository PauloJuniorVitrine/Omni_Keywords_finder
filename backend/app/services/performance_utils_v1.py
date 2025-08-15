"""
Módulo: performance_utils_v1
Utilitários para profiling e otimização de performance.
"""
import time
from typing import Callable, Any, Tuple
import functools

def medir_tempo_execucao(func: Callable) -> Callable:
    """
    Decorador para medir tempo de execução de uma função.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Tuple[Any, float]:
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fim = time.time()
        return resultado, fim - inicio
    return wrapper

# Exemplo de uso:
# @medir_tempo_execucao
# def minha_funcao(...): ... 
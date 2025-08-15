from typing import Dict, List, Optional, Any
"""
Módulo de Memória Inteligente - Omni Keywords Finder

Sistema de histórico e memória para evitar repetição de keywords e clusters,
garantindo variação algorítmica semanal.

Tracing ID: MEMORY_MODULE_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

from .historico_inteligente import HistoricoInteligente, historico_inteligente

__all__ = [
    'HistoricoInteligente',
    'historico_inteligente'
] 
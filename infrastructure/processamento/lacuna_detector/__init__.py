from typing import Dict, List, Optional, Any
"""
Módulo de Detecção Inteligente de Lacunas - Omni Keywords Finder
================================================================

Este módulo implementa um sistema híbrido de detecção de lacunas em prompts,
combinando detecção por regex com validação semântica para máxima precisão.

Autor: Paulo Júnior
Data: 2025-01-27
Tracing ID: LACUNA-001
"""

from .regex_detector import RegexLacunaDetector
from .semantic_detector import SemanticLacunaDetector
from .context_validator import ContextValidator
from .hybrid_detector import HybridLacunaDetector

__all__ = [
    'RegexLacunaDetector',
    'SemanticLacunaDetector', 
    'ContextValidator',
    'HybridLacunaDetector'
] 
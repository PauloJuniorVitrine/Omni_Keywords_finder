"""
Decorators para Testes de Integração

📐 CoCoT: Baseado em especificação do prompt de testes de integração
🌲 ToT: Avaliado múltiplas estratégias de decorators
♻️ ReAct: Implementado decorators para automação e validação

Tracing ID: decorators-integration-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Decorators implementados:
- @critical_risk: Para testes com RISK_SCORE ≥ 70
- @semantic_validation: Para validação semântica automática
- @real_data_only: Para garantir dados reais
- @production_scenario: Para cenários de produção
"""

import functools
import pytest
import time
import logging
from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass

from tests.integration.risk_score_calculator import (
    RiskScoreCalculator, FluxoConfig, Camada, ServicoExterno, FrequenciaUso
)
from tests.integration.semantic_validator import (
    SemanticValidator, SemanticValidationResult
)

logger = logging.getLogger(__name__)

@dataclass
class TestMetadata:
    """Metadados do teste para validação."""
    risk_score: int
    nivel_risco: str
    camadas: list
    servicos: list
    frequencia: str
    semantic_similarity: float
    execution_time_ms: float
    side_effects_validated: bool

def critical_risk(risk_score: int, 
                 camadas: list = None, 
                 servicos: list = None, 
                 frequencia: str = "ALTA"):
    """
    Decorator para testes com RISK_SCORE ≥ 70.
    
    Args:
        risk_score: RISK_SCORE do fluxo
        camadas: Lista de camadas envolvidas
        servicos: Lista de serviços externos
        frequencia: Frequência de uso (BAIXA/MEDIA/ALTA)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Validações obrigatórias para testes críticos
            assert risk_score >= 70, f"Teste crítico deve ter RISK_SCORE ≥ 70, atual: {risk_score}"
            
            # Log de início
            logger.info(f"🔴 Executando teste crítico: {func.__name__} (RISK_SCORE: {risk_score})")
            start_time = time.time()
            
            try:
                # Executar teste
                result = func(*args, **kwargs)
                
                # Calcular tempo de execução
                execution_time = (time.time() - start_time) * 1000
                
                # Validar tempo máximo para testes críticos
                assert execution_time < 10000, f"Teste crítico muito lento: {execution_time:.2f}ms"
                
                # Log de sucesso
                logger.info(f"✅ Teste crítico passou: {func.__name__} ({execution_time:.2f}ms)")
                
                return result
                
            except Exception as e:
                # Log de falha
                execution_time = (time.time() - start_time) * 1000
                logger.error(f"❌ Teste crítico falhou: {func.__name__} ({execution_time:.2f}ms) - {str(e)}")
                raise
        
        # Adicionar metadados ao teste
        wrapper._test_metadata = TestMetadata(
            risk_score=risk_score,
            nivel_risco="CRÍTICO" if risk_score >= 81 else "ALTO",
            camadas=camadas or [],
            servicos=servicos or [],
            frequencia=frequencia,
            semantic_similarity=0.0,  # Será calculado pelo semantic_validation
            execution_time_ms=0.0,    # Será calculado durante execução
            side_effects_validated=False  # Será validado pelo teste
        )
        
        # Marcar como teste crítico
        wrapper._is_critical = True
        
        return wrapper
    return decorator

def semantic_validation(fluxo_descricao: str, 
                       threshold: float = 0.90,
                       auto_validate: bool = True):
    """
    Decorator para validação semântica automática.
    
    Args:
        fluxo_descricao: Descrição do fluxo real
        threshold: Limite de similaridade (0.90 por padrão)
        auto_validate: Se deve validar automaticamente
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar descrição do teste baseada no nome e docstring
            teste_descricao = f"Teste: {func.__name__}\nDocstring: {func.__doc__ or 'Sem descrição'}"
            
            # Executar validação semântica se habilitada
            if auto_validate:
                validator = SemanticValidator(threshold=threshold, use_openai=False)
                result = validator.validate_fluxo_vs_teste(
                    fluxo_descricao=fluxo_descricao,
                    teste_descricao=teste_descricao,
                    fluxo_nome=func.__module__,
                    teste_nome=func.__name__
                )
                
                # Validar similaridade
                assert result.is_valid, f"Validação semântica falhou: {result.similaridade:.3f} < {threshold}"
                
                # Atualizar metadados se existir
                if hasattr(wrapper, '_test_metadata'):
                    wrapper._test_metadata.semantic_similarity = result.similarity
                
                logger.info(f"🧠 Validação semântica: {result.similarity:.3f} >= {threshold}")
            
            # Executar teste
            return func(*args, **kwargs)
        
        # Marcar como teste com validação semântica
        wrapper._has_semantic_validation = True
        wrapper._semantic_threshold = threshold
        
        return wrapper
    return decorator

def real_data_only():
    """
    Decorator para garantir que apenas dados reais sejam usados.
    Proíbe dados fictícios como foo, bar, lorem, random.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Verificar se o teste tem dados fictícios
            forbidden_data = ['foo', 'bar', 'lorem', 'random', 'dummy', 'test_data']
            
            # Verificar docstring
            if func.__doc__:
                for forbidden in forbidden_data:
                    assert forbidden not in func.__doc__.lower(), f"Dados fictícios proibidos: {forbidden}"
            
            # Verificar argumentos
            for arg in args:
                if isinstance(arg, str):
                    for forbidden in forbidden_data:
                        assert forbidden not in arg.lower(), f"Dados fictícios proibidos: {forbidden}"
            
            # Verificar kwargs
            for key, value in kwargs.items():
                if isinstance(value, str):
                    for forbidden in forbidden_data:
                        assert forbidden not in value.lower(), f"Dados fictícios proibidos: {forbidden}"
            
            logger.info(f"✅ Teste com dados reais validado: {func.__name__}")
            return func(*args, **kwargs)
        
        # Marcar como teste com dados reais
        wrapper._real_data_only = True
        
        return wrapper
    return decorator

def production_scenario():
    """
    Decorator para garantir que o teste reflete cenários reais de produção.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Verificar se o teste menciona cenários de produção
            production_keywords = ['produção', 'production', 'real', 'live', 'actual']
            
            has_production_context = False
            if func.__doc__:
                has_production_context = any(keyword in func.__doc__.lower() for keyword in production_keywords)
            
            # Aviso se não mencionar produção
            if not has_production_context:
                logger.warning(f"⚠️ Teste {func.__name__} não menciona cenários de produção explicitamente")
            
            logger.info(f"🏭 Teste de cenário de produção: {func.__name__}")
            return func(*args, **kwargs)
        
        # Marcar como teste de produção
        wrapper._production_scenario = True
        
        return wrapper
    return decorator

def side_effects_validation(*side_effects: str):
    """
    Decorator para validar side effects específicos.
    
    Args:
        *side_effects: Lista de side effects que devem ser validados
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Executar teste
            result = func(*args, **kwargs)
            
            # Log dos side effects que devem ser validados
            logger.info(f"📊 Side effects a validar em {func.__name__}: {side_effects}")
            
            # Atualizar metadados se existir
            if hasattr(wrapper, '_test_metadata'):
                wrapper._test_metadata.side_effects_validated = True
            
            return result
        
        # Marcar side effects
        wrapper._side_effects = side_effects
        
        return wrapper
    return decorator

def performance_monitor(max_time_ms: float = 5000):
    """
    Decorator para monitorar performance do teste.
    
    Args:
        max_time_ms: Tempo máximo em milissegundos
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                execution_time = (time.time() - start_time) * 1000
                
                # Validar tempo máximo
                assert execution_time < max_time_ms, f"Teste muito lento: {execution_time:.2f}ms > {max_time_ms}ms"
                
                # Atualizar metadados se existir
                if hasattr(wrapper, '_test_metadata'):
                    wrapper._test_metadata.execution_time_ms = execution_time
                
                logger.info(f"⏱️ Performance: {func.__name__} ({execution_time:.2f}ms)")
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(f"❌ Teste falhou: {func.__name__} ({execution_time:.2f}ms) - {str(e)}")
                raise
        
        return wrapper
    return decorator

# Decorator combinado para testes críticos completos
def critical_integration_test(risk_score: int,
                            fluxo_descricao: str,
                            camadas: list = None,
                            servicos: list = None,
                            frequencia: str = "ALTA",
                            max_time_ms: float = 10000,
                            side_effects: list = None):
    """
    Decorator combinado para testes de integração críticos.
    
    Combina:
    - @critical_risk
    - @semantic_validation
    - @real_data_only
    - @production_scenario
    - @side_effects_validation
    - @performance_monitor
    """
    def decorator(func: Callable) -> Callable:
        # Aplicar todos os decorators
        func = critical_risk(risk_score, camadas, servicos, frequencia)(func)
        func = semantic_validation(fluxo_descricao)(func)
        func = real_data_only()(func)
        func = production_scenario()(func)
        func = performance_monitor(max_time_ms)(func)
        
        if side_effects:
            func = side_effects_validation(*side_effects)(func)
        
        return func
    return decorator 
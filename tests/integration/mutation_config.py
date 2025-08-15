"""
Configuração de Mutation Testing para Testes de Integração

📐 CoCoT: Baseado em especificação do prompt de testes de integração
🌲 ToT: Avaliado múltiplas estratégias de mutation testing
♻️ ReAct: Implementado mutações específicas para APIs externas e circuit breakers

Tracing ID: mutation-config-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Mutações implementadas:
- APIs externas (Instagram, Facebook, YouTube, etc.)
- Circuit breakers
- Rate limiting
- Cache Redis
- Logs estruturados
"""

import pytest
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class MutationConfig:
    """Configuração de mutação para um teste."""
    test_name: str
    mutation_type: str
    original_value: Any
    mutated_value: Any
    description: str
    expected_failure: bool
    critical: bool = False

class MutationTestingConfig:
    """Configuração centralizada para mutation testing."""
    
    def __init__(self):
        self.mutations: Dict[str, List[MutationConfig]] = {}
        self.critical_threshold = 0  # 0 mutantes sobreviventes para fluxos críticos
        self.normal_threshold = 0.1  # 10% para fluxos normais
        
    def add_api_mutation(self, test_name: str, api_name: str, original_status: int, mutated_status: int):
        """Adiciona mutação para API externa."""
        mutation = MutationConfig(
            test_name=test_name,
            mutation_type="API_STATUS",
            original_value=original_status,
            mutated_value=mutated_status,
            description=f"API {api_name} retorna {mutated_status} em vez de {original_status}",
            expected_failure=True,
            critical=True
        )
        
        if test_name not in self.mutations:
            self.mutations[test_name] = []
        self.mutations[test_name].append(mutation)
    
    def add_circuit_breaker_mutation(self, test_name: str, original_state: str, mutated_state: str):
        """Adiciona mutação para circuit breaker."""
        mutation = MutationConfig(
            test_name=test_name,
            mutation_type="CIRCUIT_BREAKER",
            original_value=original_state,
            mutated_value=mutated_state,
            description=f"Circuit breaker em {mutated_state} em vez de {original_state}",
            expected_failure=True,
            critical=True
        )
        
        if test_name not in self.mutations:
            self.mutations[test_name] = []
        self.mutations[test_name].append(mutation)
    
    def add_rate_limit_mutation(self, test_name: str, original_limit: int, mutated_limit: int):
        """Adiciona mutação para rate limiting."""
        mutation = MutationConfig(
            test_name=test_name,
            mutation_type="RATE_LIMIT",
            original_value=original_limit,
            mutated_value=mutated_limit,
            description=f"Rate limit {mutated_limit} em vez de {original_limit}",
            expected_failure=True,
            critical=True
        )
        
        if test_name not in self.mutations:
            self.mutations[test_name] = []
        self.mutations[test_name].append(mutation)
    
    def add_cache_mutation(self, test_name: str, original_cache_hit: bool, mutated_cache_hit: bool):
        """Adiciona mutação para cache."""
        mutation = MutationConfig(
            test_name=test_name,
            mutation_type="CACHE",
            original_value=original_cache_hit,
            mutated_value=mutated_cache_hit,
            description=f"Cache {'hit' if mutated_cache_hit else 'miss'} em vez de {'hit' if original_cache_hit else 'miss'}",
            expected_failure=False,  # Cache miss não deve falhar o teste
            critical=False
        )
        
        if test_name not in self.mutations:
            self.mutations[test_name] = []
        self.mutations[test_name].append(mutation)
    
    def add_log_mutation(self, test_name: str, original_log_level: str, mutated_log_level: str):
        """Adiciona mutação para logs."""
        mutation = MutationConfig(
            test_name=test_name,
            mutation_type="LOG_LEVEL",
            original_value=original_log_level,
            mutated_value=mutated_log_level,
            description=f"Log level {mutated_log_level} em vez de {original_log_level}",
            expected_failure=False,  # Mudança de log não deve falhar o teste
            critical=False
        )
        
        if test_name not in self.mutations:
            self.mutations[test_name] = []
        self.mutations[test_name].append(mutation)
    
    def get_mutations_for_test(self, test_name: str) -> List[MutationConfig]:
        """Retorna mutações para um teste específico."""
        return self.mutations.get(test_name, [])
    
    def get_critical_mutations(self) -> List[MutationConfig]:
        """Retorna todas as mutações críticas."""
        critical_mutations = []
        for mutations in self.mutations.values():
            critical_mutations.extend([m for m in mutations if m.critical])
        return critical_mutations
    
    def get_mutation_summary(self) -> Dict[str, Any]:
        """Retorna resumo das mutações configuradas."""
        total_mutations = sum(len(mutations) for mutations in self.mutations.values())
        critical_mutations = len(self.get_critical_mutations())
        
        return {
            'total_tests': len(self.mutations),
            'total_mutations': total_mutations,
            'critical_mutations': critical_mutations,
            'mutation_types': list(set(m.mutation_type for mutations in self.mutations.values() for m in mutations))
        }

# Configuração global
mutation_config = MutationTestingConfig()

# Configurar mutações para Instagram API
mutation_config.add_api_mutation(
    test_name="test_instagram_real_config_initialization",
    api_name="Instagram",
    original_status=200,
    mutated_status=500
)

mutation_config.add_circuit_breaker_mutation(
    test_name="test_instagram_real_api_initialization",
    original_state="CLOSED",
    mutated_state="OPEN"
)

mutation_config.add_rate_limit_mutation(
    test_name="test_instagram_real_config_initialization",
    original_limit=200,
    mutated_limit=0
)

mutation_config.add_cache_mutation(
    test_name="test_instagram_real_api_initialization",
    original_cache_hit=True,
    mutated_cache_hit=False
)

mutation_config.add_log_mutation(
    test_name="test_instagram_real_config_initialization",
    original_log_level="INFO",
    mutated_log_level="ERROR"
)

# Configurar mutações para Facebook API
mutation_config.add_api_mutation(
    test_name="test_facebook_real_integration",
    api_name="Facebook",
    original_status=200,
    mutated_status=403
)

mutation_config.add_circuit_breaker_mutation(
    test_name="test_facebook_real_integration",
    original_state="CLOSED",
    mutated_state="HALF_OPEN"
)

# Configurar mutações para YouTube API
mutation_config.add_api_mutation(
    test_name="test_youtube_real_integration",
    api_name="YouTube",
    original_status=200,
    mutated_status=429
)

mutation_config.add_rate_limit_mutation(
    test_name="test_youtube_real_integration",
    original_limit=100,
    mutated_limit=0
)

# Configurar mutações para TikTok API
mutation_config.add_api_mutation(
    test_name="test_tiktok_real_integration",
    api_name="TikTok",
    original_status=200,
    mutated_status=401
)

# Configurar mutações para Pinterest API
mutation_config.add_api_mutation(
    test_name="test_pinterest_real_integration",
    api_name="Pinterest",
    original_status=200,
    mutated_status=503
)

# Configurar mutações para APIs de segurança
mutation_config.add_api_mutation(
    test_name="test_api_security",
    api_name="Security",
    original_status=200,
    mutated_status=403
)

# Configurar mutações para performance
mutation_config.add_rate_limit_mutation(
    test_name="test_performance_optimizations",
    original_limit=1000,
    mutated_limit=10
)

# Configurar mutações para logs estruturados
mutation_config.add_log_mutation(
    test_name="test_structured_logs",
    original_log_level="INFO",
    mutated_log_level="DEBUG"
)

# Configurar mutações para tracing distribuído
mutation_config.add_log_mutation(
    test_name="test_distributed_tracing",
    original_log_level="INFO",
    mutated_log_level="WARNING"
)

# Configurar mutações para dashboards
mutation_config.add_api_mutation(
    test_name="test_dashboards",
    api_name="Dashboard",
    original_status=200,
    mutated_status=404
)

# Configurar mutações para compliance
mutation_config.add_api_mutation(
    test_name="test_privacy_compliance",
    api_name="Compliance",
    original_status=200,
    mutated_status=400
)

# Configurar mutações para criptografia
mutation_config.add_api_mutation(
    test_name="test_encryption",
    api_name="Encryption",
    original_status=200,
    mutated_status=500
)

# Configurar mutações para cenários de falha
mutation_config.add_circuit_breaker_mutation(
    test_name="test_failure_scenarios",
    original_state="CLOSED",
    mutated_state="OPEN"
)

# Função para obter configuração de mutation testing
def get_mutation_config() -> MutationTestingConfig:
    """Retorna configuração global de mutation testing."""
    return mutation_config

# Função para validar se mutações estão configuradas
def validate_mutation_config() -> Dict[str, Any]:
    """Valida configuração de mutation testing."""
    config = get_mutation_config()
    summary = config.get_mutation_summary()
    
    # Validações
    validation_results = {
        'has_critical_mutations': summary['critical_mutations'] > 0,
        'has_api_mutations': 'API_STATUS' in summary['mutation_types'],
        'has_circuit_breaker_mutations': 'CIRCUIT_BREAKER' in summary['mutation_types'],
        'has_rate_limit_mutations': 'RATE_LIMIT' in summary['mutation_types'],
        'total_mutations_sufficient': summary['total_mutations'] >= 20,
        'critical_threshold_configured': config.critical_threshold == 0
    }
    
    return {
        'summary': summary,
        'validation': validation_results,
        'is_valid': all(validation_results.values())
    } 
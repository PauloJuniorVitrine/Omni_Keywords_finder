#!/usr/bin/env python3
"""
🎯 Script de Implementação de Cache Inteligente
📋 Objetivo: Otimizar performance através de cache inteligente
🔧 Tracing ID: CACHE_IMPLEMENTATION_20250127_001
📅 Data: 2025-01-27
"""

import os
import sys
import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from functools import wraps
import redis
import pickle
import zlib

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/cache_implementation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """Configuração do cache inteligente"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    default_ttl: int = 3600  # 1 hora
    max_memory: str = "100mb"
    compression_threshold: int = 1024  # bytes
    enable_compression: bool = True
    cache_prefix: str = "omni_cache"
    enable_stats: bool = True
    max_cache_size: int = 1000

@dataclass
class CacheStats:
    """Estatísticas do cache"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    compressions: int = 0
    total_memory: int = 0
    last_reset: datetime = None

class SmartCache:
    """Sistema de cache inteligente com compressão e estatísticas"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.stats = CacheStats()
        self.redis_client = None
        self._connect_redis()
        self._setup_redis_config()
    
    def _connect_redis(self):
        """Conecta ao Redis"""
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                decode_responses=False
            )
            self.redis_client.ping()
            logger.info("✅ Conexão com Redis estabelecida")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com Redis: {e}")
            self.redis_client = None
    
    def _setup_redis_config(self):
        """Configura Redis para cache inteligente"""
        if not self.redis_client:
            return
        
        try:
            # Configurar política de evição
            self.redis_client.config_set('maxmemory-policy', 'allkeys-lru')
            self.redis_client.config_set('maxmemory', self.config.max_memory)
            
            # Configurar compressão se habilitada
            if self.config.enable_compression:
                self.redis_client.config_set('hash-max-ziplist-entries', 512)
                self.redis_client.config_set('hash-max-ziplist-value', 64)
            
            logger.info("✅ Configuração do Redis aplicada")
        except Exception as e:
            logger.warning(f"⚠️ Erro na configuração do Redis: {e}")
    
    def _generate_key(self, key: str) -> str:
        """Gera chave única para o cache"""
        return f"{self.config.cache_prefix}:{key}"
    
    def _compress_data(self, data: bytes) -> bytes:
        """Comprime dados se necessário"""
        if len(data) > self.config.compression_threshold and self.config.enable_compression:
            compressed = zlib.compress(data)
            if len(compressed) < len(data):
                self.stats.compressions += 1
                return compressed
        return data
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Descomprime dados se necessário"""
        try:
            return zlib.decompress(data)
        except zlib.error:
            return data
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serializa dados para armazenamento"""
        serialized = pickle.dumps(data)
        return self._compress_data(serialized)
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserializa dados do armazenamento"""
        decompressed = self._decompress_data(data)
        return pickle.loads(decompressed)
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_key(key)
            data = self.redis_client.get(cache_key)
            
            if data:
                self.stats.hits += 1
                return self._deserialize_data(data)
            else:
                self.stats.misses += 1
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter cache para {key}: {e}")
            self.stats.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Define valor no cache"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_key(key)
            data = self._serialize_data(value)
            ttl = ttl or self.config.default_ttl
            
            success = self.redis_client.setex(cache_key, ttl, data)
            
            if success:
                self.stats.sets += 1
                self.stats.total_memory += len(data)
            
            return bool(success)
            
        except Exception as e:
            logger.error(f"❌ Erro ao definir cache para {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_key(key)
            result = self.redis_client.delete(cache_key)
            self.stats.deletes += 1
            return bool(result)
            
        except Exception as e:
            logger.error(f"❌ Erro ao deletar cache para {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Limpa todo o cache"""
        if not self.redis_client:
            return False
        
        try:
            pattern = f"{self.config.cache_prefix}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"🗑️ Cache limpo: {len(keys)} chaves removidas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar cache: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache"""
        stats_dict = asdict(self.stats)
        stats_dict['hit_rate'] = (
            self.stats.hits / (self.stats.hits + self.stats.misses)
            if (self.stats.hits + self.stats.misses) > 0 else 0
        )
        stats_dict['compression_rate'] = (
            self.stats.compressions / self.stats.sets
            if self.stats.sets > 0 else 0
        )
        return stats_dict
    
    def reset_stats(self):
        """Reseta estatísticas"""
        self.stats = CacheStats()
        self.stats.last_reset = datetime.now()

def cache_decorator(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator para cache automático de funções"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave única baseada na função e argumentos
            func_name = func.__name__
            args_hash = hashlib.md5(
                f"{args}{sorted(kwargs.items())}".encode()
            ).hexdigest()
            cache_key = f"{key_prefix}{func_name}:{args_hash}"
            
            # Tentar obter do cache
            cached_result = smart_cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"🎯 Cache hit para {func_name}")
                return cached_result
            
            # Executar função e armazenar resultado
            result = func(*args, **kwargs)
            smart_cache.set(cache_key, result, ttl)
            logger.debug(f"💾 Cache miss para {func_name}, resultado armazenado")
            
            return result
        return wrapper
    return decorator

def implement_cache_strategies():
    """Implementa estratégias de cache específicas"""
    
    strategies = {
        "database_queries": {
            "description": "Cache para queries de banco de dados",
            "ttl": 1800,  # 30 minutos
            "prefix": "db_query:"
        },
        "api_responses": {
            "description": "Cache para respostas de API",
            "ttl": 600,   # 10 minutos
            "prefix": "api:"
        },
        "user_sessions": {
            "description": "Cache para sessões de usuário",
            "ttl": 3600,  # 1 hora
            "prefix": "session:"
        },
        "static_content": {
            "description": "Cache para conteúdo estático",
            "ttl": 86400, # 24 horas
            "prefix": "static:"
        }
    }
    
    return strategies

def create_cache_config_file():
    """Cria arquivo de configuração do cache"""
    config = {
        "cache_config": {
            "redis_host": "localhost",
            "redis_port": 6379,
            "redis_db": 0,
            "default_ttl": 3600,
            "max_memory": "100mb",
            "compression_threshold": 1024,
            "enable_compression": True,
            "cache_prefix": "omni_cache",
            "enable_stats": True,
            "max_cache_size": 1000
        },
        "strategies": implement_cache_strategies(),
        "monitoring": {
            "enable_metrics": True,
            "metrics_interval": 300,
            "alert_threshold": 0.8
        }
    }
    
    config_path = "config/cache_config.json"
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, default=str)
    
    logger.info(f"✅ Configuração de cache salva em {config_path}")
    return config_path

def create_cache_monitoring():
    """Cria sistema de monitoramento do cache"""
    monitoring_code = '''
import time
import psutil
from datetime import datetime

class CacheMonitor:
    """Monitor de performance do cache"""
    
    def __init__(self, cache_instance):
        self.cache = cache_instance
        self.metrics = []
    
    def collect_metrics(self):
        """Coleta métricas do cache"""
        stats = self.cache.get_stats()
        
        # Métricas do sistema
        system_metrics = {
            'timestamp': datetime.now().isoformat(),
            'memory_usage': psutil.virtual_memory().percent,
            'cpu_usage': psutil.cpu_percent(),
            'cache_hit_rate': stats['hit_rate'],
            'cache_memory': stats['total_memory'],
            'cache_operations': stats['hits'] + stats['misses']
        }
        
        self.metrics.append(system_metrics)
        return system_metrics
    
    def generate_report(self):
        """Gera relatório de performance"""
        if not self.metrics:
            return {}
        
        latest = self.metrics[-1]
        avg_hit_rate = sum(m['cache_hit_rate'] for m in self.metrics) / len(self.metrics)
        
        return {
            'current_metrics': latest,
            'average_hit_rate': avg_hit_rate,
            'total_operations': len(self.metrics),
            'recommendations': self._generate_recommendations(latest, avg_hit_rate)
        }
    
    def _generate_recommendations(self, current, avg_hit_rate):
        """Gera recomendações baseadas nas métricas"""
        recommendations = []
        
        if avg_hit_rate < 0.7:
            recommendations.append("Considerar aumentar TTL do cache")
        
        if current['memory_usage'] > 80:
            recommendations.append("Monitorar uso de memória do sistema")
        
        if current['cache_hit_rate'] < 0.5:
            recommendations.append("Revisar estratégias de cache")
        
        return recommendations
'''
    
    monitoring_path = "infrastructure/cache/cache_monitor.py"
    os.makedirs(os.path.dirname(monitoring_path), exist_ok=True)
    
    with open(monitoring_path, 'w', encoding='utf-8') as f:
        f.write(monitoring_code)
    
    logger.info(f"✅ Monitor de cache criado em {monitoring_path}")

def create_cache_tests():
    """Cria testes para o sistema de cache"""
    test_code = '''
import pytest
import time
from unittest.mock import Mock, patch
from scripts.implement_smart_cache import SmartCache, CacheConfig, cache_decorator

class TestSmartCache:
    """Testes para o sistema de cache inteligente"""
    
    @pytest.fixture
    def cache_config(self):
        return CacheConfig(
            redis_host="localhost",
            redis_port=6379,
            default_ttl=60
        )
    
    @pytest.fixture
    def mock_redis(self):
        with patch('redis.Redis') as mock:
            mock_instance = Mock()
            mock_instance.ping.return_value = True
            mock_instance.get.return_value = None
            mock_instance.setex.return_value = True
            mock_instance.delete.return_value = 1
            mock.return_value = mock_instance
            yield mock_instance
    
    def test_cache_initialization(self, cache_config, mock_redis):
        """Testa inicialização do cache"""
        cache = SmartCache(cache_config)
        assert cache.config == cache_config
        assert cache.redis_client is not None
    
    def test_cache_set_get(self, cache_config, mock_redis):
        """Testa operações básicas de set/get"""
        cache = SmartCache(cache_config)
        
        # Mock para serialização
        with patch('pickle.dumps') as mock_dumps:
            mock_dumps.return_value = b'test_data'
            
            # Teste set
            result = cache.set("test_key", "test_value")
            assert result is True
            
            # Teste get
            with patch('pickle.loads') as mock_loads:
                mock_loads.return_value = "test_value"
                mock_redis.get.return_value = b'test_data'
                
                result = cache.get("test_key")
                assert result == "test_value"
    
    def test_cache_decorator(self, cache_config, mock_redis):
        """Testa decorator de cache"""
        cache = SmartCache(cache_config)
        
        @cache_decorator(ttl=60)
        def test_function(x, y):
            return x + y
        
        # Primeira chamada (cache miss)
        result1 = test_function(1, 2)
        assert result1 == 3
        
        # Segunda chamada (cache hit)
        result2 = test_function(1, 2)
        assert result2 == 3
    
    def test_cache_stats(self, cache_config, mock_redis):
        """Testa coleta de estatísticas"""
        cache = SmartCache(cache_config)
        
        # Simular algumas operações
        cache.stats.hits = 10
        cache.stats.misses = 5
        cache.stats.sets = 8
        
        stats = cache.get_stats()
        assert stats['hits'] == 10
        assert stats['misses'] == 5
        assert stats['hit_rate'] == 10/15
        assert stats['compression_rate'] == 0  # Sem compressões ainda
    
    def test_cache_clear(self, cache_config, mock_redis):
        """Testa limpeza do cache"""
        cache = SmartCache(cache_config)
        mock_redis.keys.return_value = [b'key1', b'key2']
        
        result = cache.clear()
        assert result is True
        mock_redis.delete.assert_called_once()
'''
    
    test_path = "tests/unit/test_smart_cache.py"
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    logger.info(f"✅ Testes de cache criados em {test_path}")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando implementação de cache inteligente")
    
    try:
        # Criar configuração
        config_path = create_cache_config_file()
        logger.info(f"✅ Configuração criada: {config_path}")
        
        # Criar monitoramento
        create_cache_monitoring()
        logger.info("✅ Sistema de monitoramento criado")
        
        # Criar testes
        create_cache_tests()
        logger.info("✅ Testes de cache criados")
        
        # Criar instância global do cache
        global smart_cache
        config = CacheConfig()
        smart_cache = SmartCache(config)
        
        # Exemplo de uso
        logger.info("📝 Exemplo de uso do cache:")
        logger.info("""
# Uso básico
smart_cache.set("user:123", {"name": "João", "email": "joao@email.com"})
user_data = smart_cache.get("user:123")

# Com decorator
@cache_decorator(ttl=300)
def get_user_profile(user_id):
    # Lógica para buscar perfil do usuário
    return {"user_id": user_id, "profile": "data"}

# Estatísticas
stats = smart_cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
        """)
        
        logger.info("✅ Implementação de cache inteligente concluída")
        
        # Salvar relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "files_created": [
                "config/cache_config.json",
                "infrastructure/cache/cache_monitor.py",
                "tests/unit/test_smart_cache.py"
            ],
            "features": [
                "Cache com Redis",
                "Compressão automática",
                "Estatísticas detalhadas",
                "Decorator para funções",
                "Monitoramento de performance",
                "Testes unitários"
            ],
            "recommendations": [
                "Configurar Redis em produção",
                "Ajustar TTL baseado no uso",
                "Monitorar hit rate regularmente",
                "Implementar cache warming para dados críticos"
            ]
        }
        
        report_path = "docs/RELATORIO_CACHE_IMPLEMENTACAO.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Relatório de Implementação de Cache Inteligente\n\n")
            f.write(f"**Data**: {report['timestamp']}\n")
            f.write(f"**Status**: {report['status']}\n\n")
            f.write("## Arquivos Criados\n")
            for file in report['files_created']:
                f.write(f"- `{file}`\n")
            f.write("\n## Funcionalidades\n")
            for feature in report['features']:
                f.write(f"- {feature}\n")
            f.write("\n## Recomendações\n")
            for rec in report['recommendations']:
                f.write(f"- {rec}\n")
        
        logger.info(f"✅ Relatório salvo em {report_path}")
        
    except Exception as e:
        logger.error(f"❌ Erro na implementação: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
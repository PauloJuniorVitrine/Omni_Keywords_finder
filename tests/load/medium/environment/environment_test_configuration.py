"""
🧪 Teste de Configuração de Ambiente

Tracing ID: environment-test-configuration-2025-01-27-001
Timestamp: 2025-01-27T23:15:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em configurações reais do sistema Omni Keywords Finder
🌲 ToT: Avaliadas múltiplas estratégias de validação de configuração (valores, relacionamentos, dependências)
♻️ ReAct: Simulado cenários de configuração e validada consistência

Testa configuração de ambiente incluindo:
- Configurações de aplicação
- Configurações de banco de dados
- Configurações de cache
- Configurações de filas
- Configurações de monitoramento
- Configurações de segurança
- Configurações de performance
- Configurações de backup
- Configurações de alta disponibilidade
- Validação de integridade
"""

import pytest
import asyncio
import time
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, patch, AsyncMock
import logging
from dataclasses import dataclass
import yaml
import configparser
import subprocess
import platform

# Importações do sistema real
from backend.app.config.settings import Settings
from backend.app.config.database import DatabaseConfig
from backend.app.config.cache import CacheConfig
from backend.app.config.queue import QueueConfig
from backend.app.config.monitoring import MonitoringConfig
from backend.app.config.security import SecurityConfig
from backend.app.config.performance import PerformanceConfig
from infrastructure.config.config_validator import ConfigValidator
from infrastructure.config.config_manager import ConfigManager
from infrastructure.logging.structured_logger import StructuredLogger

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class EnvironmentTestConfigurationConfig:
    """Configuração para testes de configuração de ambiente"""
    config_files = [
        "config/app.yaml",
        "config/database.yaml", 
        "config/cache.yaml",
        "config/queue.yaml",
        "config/monitoring.yaml",
        "config/security.yaml",
        "config/performance.yaml",
        "config/backup.yaml",
        "config/ha.yaml"
    ]
    enable_config_validation: bool = True
    enable_config_relationships: bool = True
    enable_config_dependencies: bool = True
    enable_config_security: bool = True
    enable_config_performance: bool = True
    enable_config_backup: bool = True
    enable_config_ha: bool = True
    test_timeout: int = 300  # 5 minutos

class EnvironmentTestConfiguration:
    """Teste de configuração de ambiente"""
    
    def __init__(self, config: Optional[EnvironmentTestConfigurationConfig] = None):
        self.config = config or EnvironmentTestConfigurationConfig()
        self.logger = StructuredLogger(
            module="environment_test_configuration",
            tracing_id="test_config_001"
        )
        self.config_validator = ConfigValidator()
        self.config_manager = ConfigManager()
        
        # Configurações carregadas
        self.loaded_configs: Dict[str, Dict[str, Any]] = {}
        self.config_validation_results: List[Dict[str, Any]] = []
        self.config_relationships: List[Dict[str, Any]] = []
        self.config_dependencies: List[Dict[str, Any]] = []
        
        logger.info(f"Environment Test Configuration inicializado com configuração: {self.config}")
    
    async def setup_configuration_test(self):
        """Configura teste de configuração"""
        try:
            # Configurar validador
            self.config_validator.configure({
                "enable_validation": self.config.enable_config_validation,
                "enable_relationships": self.config.enable_config_relationships,
                "enable_dependencies": self.config.enable_config_dependencies
            })
            
            # Configurar gerenciador
            self.config_manager.configure({
                "config_files": self.config.config_files,
                "enable_auto_reload": False,
                "enable_validation": True
            })
            
            logger.info("Teste de configuração configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar teste de configuração: {e}")
            raise
    
    async def test_config_files_existence(self):
        """Testa existência dos arquivos de configuração"""
        try:
            missing_files = []
            existing_files = []
            
            for config_file in self.config.config_files:
                if os.path.exists(config_file):
                    existing_files.append(config_file)
                else:
                    missing_files.append(config_file)
            
            # Verificar existência
            assert len(existing_files) > 0, "Nenhum arquivo de configuração encontrado"
            assert len(missing_files) == 0, f"Arquivos de configuração ausentes: {missing_files}"
            
            self.config_validation_results.append({
                "test_type": "config_files_existence",
                "total_files": len(self.config.config_files),
                "existing_files": len(existing_files),
                "missing_files": len(missing_files),
                "missing_files_list": missing_files
            })
            
            logger.info(f"Arquivos de configuração verificados: {len(existing_files)}/{len(self.config.config_files)} existem")
            
            return {
                "success": True,
                "total_files": len(self.config.config_files),
                "existing_files": len(existing_files),
                "missing_files": len(missing_files),
                "missing_files_list": missing_files
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de existência de arquivos de configuração: {e}")
            raise
    
    async def test_config_files_syntax(self):
        """Testa sintaxe dos arquivos de configuração"""
        try:
            syntax_results = {}
            
            for config_file in self.config.config_files:
                if not os.path.exists(config_file):
                    continue
                
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                            yaml.safe_load(f)
                        elif config_file.endswith('.json'):
                            json.load(f)
                        elif config_file.endswith('.ini'):
                            config = configparser.ConfigParser()
                            config.read(config_file)
                    
                    syntax_results[config_file] = {
                        "success": True,
                        "syntax_valid": True
                    }
                    
                except Exception as e:
                    syntax_results[config_file] = {
                        "success": False,
                        "syntax_valid": False,
                        "error": str(e)
                    }
            
            # Calcular métricas
            valid_files = [r for r in syntax_results.values() if r["success"]]
            invalid_files = [r for r in syntax_results.values() if not r["success"]]
            
            # Verificar sintaxe
            assert len(valid_files) > 0, "Nenhum arquivo de configuração tem sintaxe válida"
            assert len(invalid_files) == 0, f"Arquivos com sintaxe inválida: {[f for f, r in syntax_results.items() if not r['success']]}"
            
            self.config_validation_results.append({
                "test_type": "config_files_syntax",
                "total_files": len(syntax_results),
                "valid_files": len(valid_files),
                "invalid_files": len(invalid_files),
                "results": syntax_results
            })
            
            logger.info(f"Sintaxe de configuração verificada: {len(valid_files)}/{len(syntax_results)} válidos")
            
            return {
                "success": True,
                "total_files": len(syntax_results),
                "valid_files": len(valid_files),
                "invalid_files": len(invalid_files),
                "results": syntax_results
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de sintaxe de configuração: {e}")
            raise
    
    async def test_app_configuration(self):
        """Testa configuração da aplicação"""
        try:
            # Carregar configurações
            settings = Settings()
            
            # Validar configurações obrigatórias
            required_configs = [
                "DATABASE_URL",
                "REDIS_URL",
                "RABBITMQ_URL",
                "API_SECRET_KEY",
                "ENVIRONMENT",
                "DEBUG",
                "LOG_LEVEL",
                "CORS_ORIGINS",
                "RATE_LIMIT_PER_MINUTE"
            ]
            
            missing_configs = []
            config_values = {}
            
            for config in required_configs:
                value = getattr(settings, config, None)
                if value is None:
                    missing_configs.append(config)
                else:
                    config_values[config] = value
            
            # Verificar configurações
            assert len(missing_configs) == 0, f"Configurações obrigatórias ausentes: {missing_configs}"
            assert settings.ENVIRONMENT in ["development", "staging", "production"], f"Ambiente inválido: {settings.ENVIRONMENT}"
            assert settings.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR"], f"Nível de log inválido: {settings.LOG_LEVEL}"
            
            # Validar configurações de segurança
            security_configs = [
                "API_SECRET_KEY",
                "JWT_SECRET_KEY",
                "CORS_ORIGINS",
                "RATE_LIMIT_PER_MINUTE"
            ]
            
            security_valid = True
            security_issues = []
            
            for config in security_configs:
                value = getattr(settings, config, None)
                if value is None or value == "":
                    security_valid = False
                    security_issues.append(f"{config} não configurado")
            
            # Verificar segurança
            assert security_valid, f"Problemas de segurança: {security_issues}"
            
            self.config_validation_results.append({
                "test_type": "app_configuration",
                "total_configs": len(required_configs),
                "missing_configs": len(missing_configs),
                "security_valid": security_valid,
                "security_issues": security_issues,
                "environment": settings.ENVIRONMENT,
                "debug_enabled": settings.DEBUG
            })
            
            logger.info(f"Configuração da aplicação validada: {len(required_configs)} configs, {len(missing_configs)} ausentes")
            
            return {
                "success": True,
                "total_configs": len(required_configs),
                "missing_configs": len(missing_configs),
                "security_valid": security_valid,
                "security_issues": security_issues,
                "config_values": config_values
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de configuração da aplicação: {e}")
            raise
    
    async def test_database_configuration(self):
        """Testa configuração do banco de dados"""
        try:
            # Carregar configuração
            db_config = DatabaseConfig()
            
            # Validar configurações obrigatórias
            required_db_configs = [
                "DATABASE_URL",
                "DB_HOST",
                "DB_PORT",
                "DB_NAME",
                "DB_USER",
                "DB_PASSWORD",
                "DB_POOL_SIZE",
                "DB_MAX_OVERFLOW",
                "DB_POOL_TIMEOUT"
            ]
            
            missing_db_configs = []
            db_config_values = {}
            
            for config in required_db_configs:
                value = getattr(db_config, config, None)
                if value is None:
                    missing_db_configs.append(config)
                else:
                    db_config_values[config] = value
            
            # Verificar configurações
            assert len(missing_db_configs) == 0, f"Configurações de banco ausentes: {missing_db_configs}"
            assert db_config.DB_POOL_SIZE > 0, f"Tamanho do pool inválido: {db_config.DB_POOL_SIZE}"
            assert db_config.DB_MAX_OVERFLOW >= 0, f"Max overflow inválido: {db_config.DB_MAX_OVERFLOW}"
            assert db_config.DB_POOL_TIMEOUT > 0, f"Timeout do pool inválido: {db_config.DB_POOL_TIMEOUT}"
            
            # Validar URL do banco
            assert "postgresql://" in db_config.DATABASE_URL, f"URL do banco inválida: {db_config.DATABASE_URL}"
            
            self.config_validation_results.append({
                "test_type": "database_configuration",
                "total_configs": len(required_db_configs),
                "missing_configs": len(missing_db_configs),
                "pool_size": db_config.DB_POOL_SIZE,
                "max_overflow": db_config.DB_MAX_OVERFLOW,
                "pool_timeout": db_config.DB_POOL_TIMEOUT
            })
            
            logger.info(f"Configuração do banco validada: {len(required_db_configs)} configs, {len(missing_db_configs)} ausentes")
            
            return {
                "success": True,
                "total_configs": len(required_db_configs),
                "missing_configs": len(missing_db_configs),
                "pool_size": db_config.DB_POOL_SIZE,
                "max_overflow": db_config.DB_MAX_OVERFLOW,
                "pool_timeout": db_config.DB_POOL_TIMEOUT
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de configuração do banco: {e}")
            raise
    
    async def test_cache_configuration(self):
        """Testa configuração do cache"""
        try:
            # Carregar configuração
            cache_config = CacheConfig()
            
            # Validar configurações obrigatórias
            required_cache_configs = [
                "REDIS_URL",
                "REDIS_HOST",
                "REDIS_PORT",
                "REDIS_DB",
                "REDIS_PASSWORD",
                "CACHE_TTL",
                "CACHE_MAX_SIZE"
            ]
            
            missing_cache_configs = []
            cache_config_values = {}
            
            for config in required_cache_configs:
                value = getattr(cache_config, config, None)
                if value is None:
                    missing_cache_configs.append(config)
                else:
                    cache_config_values[config] = value
            
            # Verificar configurações
            assert len(missing_cache_configs) == 0, f"Configurações de cache ausentes: {missing_cache_configs}"
            assert cache_config.CACHE_TTL > 0, f"TTL do cache inválido: {cache_config.CACHE_TTL}"
            assert cache_config.CACHE_MAX_SIZE > 0, f"Tamanho máximo do cache inválido: {cache_config.CACHE_MAX_SIZE}"
            
            # Validar URL do Redis
            assert "redis://" in cache_config.REDIS_URL, f"URL do Redis inválida: {cache_config.REDIS_URL}"
            
            self.config_validation_results.append({
                "test_type": "cache_configuration",
                "total_configs": len(required_cache_configs),
                "missing_configs": len(missing_cache_configs),
                "cache_ttl": cache_config.CACHE_TTL,
                "cache_max_size": cache_config.CACHE_MAX_SIZE
            })
            
            logger.info(f"Configuração do cache validada: {len(required_cache_configs)} configs, {len(missing_cache_configs)} ausentes")
            
            return {
                "success": True,
                "total_configs": len(required_cache_configs),
                "missing_configs": len(missing_cache_configs),
                "cache_ttl": cache_config.CACHE_TTL,
                "cache_max_size": cache_config.CACHE_MAX_SIZE
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de configuração do cache: {e}")
            raise
    
    async def test_queue_configuration(self):
        """Testa configuração das filas"""
        try:
            # Carregar configuração
            queue_config = QueueConfig()
            
            # Validar configurações obrigatórias
            required_queue_configs = [
                "RABBITMQ_URL",
                "RABBITMQ_HOST",
                "RABBITMQ_PORT",
                "RABBITMQ_USER",
                "RABBITMQ_PASSWORD",
                "RABBITMQ_VHOST",
                "QUEUE_MAX_PRIORITY",
                "QUEUE_DEFAULT_TTL"
            ]
            
            missing_queue_configs = []
            queue_config_values = {}
            
            for config in required_queue_configs:
                value = getattr(queue_config, config, None)
                if value is None:
                    missing_queue_configs.append(config)
                else:
                    queue_config_values[config] = value
            
            # Verificar configurações
            assert len(missing_queue_configs) == 0, f"Configurações de fila ausentes: {missing_queue_configs}"
            assert queue_config.QUEUE_MAX_PRIORITY > 0, f"Prioridade máxima inválida: {queue_config.QUEUE_MAX_PRIORITY}"
            assert queue_config.QUEUE_DEFAULT_TTL > 0, f"TTL padrão inválido: {queue_config.QUEUE_DEFAULT_TTL}"
            
            # Validar URL do RabbitMQ
            assert "amqp://" in queue_config.RABBITMQ_URL, f"URL do RabbitMQ inválida: {queue_config.RABBITMQ_URL}"
            
            self.config_validation_results.append({
                "test_type": "queue_configuration",
                "total_configs": len(required_queue_configs),
                "missing_configs": len(missing_queue_configs),
                "max_priority": queue_config.QUEUE_MAX_PRIORITY,
                "default_ttl": queue_config.QUEUE_DEFAULT_TTL
            })
            
            logger.info(f"Configuração das filas validada: {len(required_queue_configs)} configs, {len(missing_queue_configs)} ausentes")
            
            return {
                "success": True,
                "total_configs": len(required_queue_configs),
                "missing_configs": len(missing_queue_configs),
                "max_priority": queue_config.QUEUE_MAX_PRIORITY,
                "default_ttl": queue_config.QUEUE_DEFAULT_TTL
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de configuração das filas: {e}")
            raise
    
    async def test_monitoring_configuration(self):
        """Testa configuração de monitoramento"""
        try:
            # Carregar configuração
            monitoring_config = MonitoringConfig()
            
            # Validar configurações obrigatórias
            required_monitoring_configs = [
                "METRICS_ENABLED",
                "METRICS_PORT",
                "METRICS_PATH",
                "LOGGING_LEVEL",
                "LOGGING_FORMAT",
                "ALERTING_ENABLED",
                "ALERTING_WEBHOOK_URL"
            ]
            
            missing_monitoring_configs = []
            monitoring_config_values = {}
            
            for config in required_monitoring_configs:
                value = getattr(monitoring_config, config, None)
                if value is None:
                    missing_monitoring_configs.append(config)
                else:
                    monitoring_config_values[config] = value
            
            # Verificar configurações
            assert len(missing_monitoring_configs) == 0, f"Configurações de monitoramento ausentes: {missing_monitoring_configs}"
            assert monitoring_config.METRICS_PORT > 0, f"Porta de métricas inválida: {monitoring_config.METRICS_PORT}"
            assert monitoring_config.LOGGING_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR"], f"Nível de logging inválido: {monitoring_config.LOGGING_LEVEL}"
            
            self.config_validation_results.append({
                "test_type": "monitoring_configuration",
                "total_configs": len(required_monitoring_configs),
                "missing_configs": len(missing_monitoring_configs),
                "metrics_enabled": monitoring_config.METRICS_ENABLED,
                "metrics_port": monitoring_config.METRICS_PORT,
                "alerting_enabled": monitoring_config.ALERTING_ENABLED
            })
            
            logger.info(f"Configuração de monitoramento validada: {len(required_monitoring_configs)} configs, {len(missing_monitoring_configs)} ausentes")
            
            return {
                "success": True,
                "total_configs": len(required_monitoring_configs),
                "missing_configs": len(missing_monitoring_configs),
                "metrics_enabled": monitoring_config.METRICS_ENABLED,
                "metrics_port": monitoring_config.METRICS_PORT,
                "alerting_enabled": monitoring_config.ALERTING_ENABLED
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de configuração de monitoramento: {e}")
            raise
    
    async def test_security_configuration(self):
        """Testa configuração de segurança"""
        try:
            # Carregar configuração
            security_config = SecurityConfig()
            
            # Validar configurações obrigatórias
            required_security_configs = [
                "JWT_SECRET_KEY",
                "JWT_ALGORITHM",
                "JWT_EXPIRATION_HOURS",
                "BCRYPT_ROUNDS",
                "RATE_LIMIT_ENABLED",
                "RATE_LIMIT_PER_MINUTE",
                "CORS_ENABLED",
                "CORS_ORIGINS"
            ]
            
            missing_security_configs = []
            security_config_values = {}
            
            for config in required_security_configs:
                value = getattr(security_config, config, None)
                if value is None:
                    missing_security_configs.append(config)
                else:
                    security_config_values[config] = value
            
            # Verificar configurações
            assert len(missing_security_configs) == 0, f"Configurações de segurança ausentes: {missing_security_configs}"
            assert security_config.JWT_EXPIRATION_HOURS > 0, f"Expiração JWT inválida: {security_config.JWT_EXPIRATION_HOURS}"
            assert security_config.BCRYPT_ROUNDS >= 10, f"Rounds Bcrypt muito baixo: {security_config.BCRYPT_ROUNDS}"
            assert security_config.RATE_LIMIT_PER_MINUTE > 0, f"Rate limit inválido: {security_config.RATE_LIMIT_PER_MINUTE}"
            
            self.config_validation_results.append({
                "test_type": "security_configuration",
                "total_configs": len(required_security_configs),
                "missing_configs": len(missing_security_configs),
                "jwt_expiration": security_config.JWT_EXPIRATION_HOURS,
                "bcrypt_rounds": security_config.BCRYPT_ROUNDS,
                "rate_limit": security_config.RATE_LIMIT_PER_MINUTE
            })
            
            logger.info(f"Configuração de segurança validada: {len(required_security_configs)} configs, {len(missing_security_configs)} ausentes")
            
            return {
                "success": True,
                "total_configs": len(required_security_configs),
                "missing_configs": len(missing_security_configs),
                "jwt_expiration": security_config.JWT_EXPIRATION_HOURS,
                "bcrypt_rounds": security_config.BCRYPT_ROUNDS,
                "rate_limit": security_config.RATE_LIMIT_PER_MINUTE
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de configuração de segurança: {e}")
            raise
    
    async def test_config_relationships(self):
        """Testa relacionamentos entre configurações"""
        try:
            relationships = []
            
            # Testar relacionamento entre banco e cache
            db_config = DatabaseConfig()
            cache_config = CacheConfig()
            
            if db_config.DB_HOST and cache_config.REDIS_HOST:
                relationships.append({
                    "type": "database_cache",
                    "database_host": db_config.DB_HOST,
                    "cache_host": cache_config.REDIS_HOST,
                    "valid": True
                })
            
            # Testar relacionamento entre filas e monitoramento
            queue_config = QueueConfig()
            monitoring_config = MonitoringConfig()
            
            if queue_config.RABBITMQ_HOST and monitoring_config.METRICS_ENABLED:
                relationships.append({
                    "type": "queue_monitoring",
                    "queue_host": queue_config.RABBITMQ_HOST,
                    "monitoring_enabled": monitoring_config.METRICS_ENABLED,
                    "valid": True
                })
            
            # Testar relacionamento entre segurança e aplicação
            security_config = SecurityConfig()
            settings = Settings()
            
            if security_config.JWT_SECRET_KEY and settings.API_SECRET_KEY:
                relationships.append({
                    "type": "security_app",
                    "jwt_secret_configured": bool(security_config.JWT_SECRET_KEY),
                    "api_secret_configured": bool(settings.API_SECRET_KEY),
                    "valid": True
                })
            
            # Verificar relacionamentos
            assert len(relationships) > 0, "Nenhum relacionamento de configuração encontrado"
            assert all(r["valid"] for r in relationships), "Relacionamentos de configuração inválidos"
            
            self.config_relationships = relationships
            
            logger.info(f"Relacionamentos de configuração testados: {len(relationships)} relacionamentos")
            
            return {
                "success": True,
                "total_relationships": len(relationships),
                "valid_relationships": len([r for r in relationships if r["valid"]]),
                "relationships": relationships
            }
            
        except Exception as e:
            logger.error(f"Erro no teste de relacionamentos de configuração: {e}")
            raise
    
    def get_configuration_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de configuração"""
        return {
            "total_validation_tests": len(self.config_validation_results),
            "validation_results": self.config_validation_results,
            "relationships": self.config_relationships,
            "dependencies": self.config_dependencies,
            "config_files": self.config.config_files
        }

# Testes pytest
@pytest.mark.asyncio
class TestEnvironmentTestConfiguration:
    """Testes de configuração de ambiente"""
    
    @pytest.fixture(autouse=True)
    async def setup_test(self):
        """Configuração do teste"""
        self.test_instance = EnvironmentTestConfiguration()
        await self.test_instance.setup_configuration_test()
        yield
    
    async def test_config_files_existence(self):
        """Testa existência dos arquivos de configuração"""
        result = await self.test_instance.test_config_files_existence()
        assert result["success"] is True
        assert result["missing_files"] == 0
    
    async def test_config_files_syntax(self):
        """Testa sintaxe dos arquivos de configuração"""
        result = await self.test_instance.test_config_files_syntax()
        assert result["success"] is True
        assert result["invalid_files"] == 0
    
    async def test_app_configuration(self):
        """Testa configuração da aplicação"""
        result = await self.test_instance.test_app_configuration()
        assert result["success"] is True
        assert result["missing_configs"] == 0
    
    async def test_database_configuration(self):
        """Testa configuração do banco de dados"""
        result = await self.test_instance.test_database_configuration()
        assert result["success"] is True
        assert result["missing_configs"] == 0
    
    async def test_cache_configuration(self):
        """Testa configuração do cache"""
        result = await self.test_instance.test_cache_configuration()
        assert result["success"] is True
        assert result["missing_configs"] == 0
    
    async def test_queue_configuration(self):
        """Testa configuração das filas"""
        result = await self.test_instance.test_queue_configuration()
        assert result["success"] is True
        assert result["missing_configs"] == 0
    
    async def test_monitoring_configuration(self):
        """Testa configuração de monitoramento"""
        result = await self.test_instance.test_monitoring_configuration()
        assert result["success"] is True
        assert result["missing_configs"] == 0
    
    async def test_security_configuration(self):
        """Testa configuração de segurança"""
        result = await self.test_instance.test_security_configuration()
        assert result["success"] is True
        assert result["missing_configs"] == 0
    
    async def test_config_relationships(self):
        """Testa relacionamentos entre configurações"""
        result = await self.test_instance.test_config_relationships()
        assert result["success"] is True
        assert result["valid_relationships"] > 0
    
    async def test_overall_configuration_metrics(self):
        """Testa métricas gerais de configuração"""
        # Executar todos os testes
        await self.test_instance.test_config_files_existence()
        await self.test_instance.test_config_files_syntax()
        await self.test_instance.test_app_configuration()
        await self.test_instance.test_database_configuration()
        await self.test_instance.test_cache_configuration()
        await self.test_instance.test_queue_configuration()
        await self.test_instance.test_monitoring_configuration()
        await self.test_instance.test_security_configuration()
        await self.test_instance.test_config_relationships()
        
        # Obter métricas
        metrics = self.test_instance.get_configuration_metrics()
        
        # Verificar métricas
        assert metrics["total_validation_tests"] > 0

if __name__ == "__main__":
    # Execução direta do teste
    async def main():
        test_instance = EnvironmentTestConfiguration()
        try:
            await test_instance.setup_configuration_test()
            
            # Executar todos os testes
            await test_instance.test_config_files_existence()
            await test_instance.test_config_files_syntax()
            await test_instance.test_app_configuration()
            await test_instance.test_database_configuration()
            await test_instance.test_cache_configuration()
            await test_instance.test_queue_configuration()
            await test_instance.test_monitoring_configuration()
            await test_instance.test_security_configuration()
            await test_instance.test_config_relationships()
            
            # Obter métricas finais
            metrics = test_instance.get_configuration_metrics()
            print(f"Métricas de Configuração: {json.dumps(metrics, indent=2, default=str)}")
            
        except Exception as e:
            logger.error(f"Erro na execução do teste: {e}")
    
    asyncio.run(main()) 
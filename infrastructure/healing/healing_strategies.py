"""
Healing Strategies - Estratégias de Auto-Cura para Serviços

Tracing ID: HEALING_STRATEGIES_001_20250127
Versão: 1.0
Data: 2025-01-27
Objetivo: Implementar estratégias específicas para correção automática de problemas

Este módulo contém as estratégias de healing que podem ser aplicadas
para corrigir diferentes tipos de problemas em serviços.
"""

import asyncio
import logging
import time
import subprocess
import psutil
import aiohttp
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
import signal
import threading

from .healing_config import HealingConfig

logger = logging.getLogger(__name__)


@dataclass
class HealingResult:
    """Resultado de uma tentativa de healing"""
    success: bool
    message: str
    duration: float
    timestamp: datetime
    details: Dict[str, Any]


class HealingStrategy(ABC):
    """Classe base para estratégias de healing"""
    
    def __init__(self, config: HealingConfig):
        """
        Inicializa a estratégia de healing
        
        Args:
            config: Configuração do sistema de healing
        """
        self.config = config
        self.attempt_count = 0
        self.last_attempt = None
    
    @abstractmethod
    async def apply(self, problem_report) -> bool:
        """
        Aplica a estratégia de healing
        
        Args:
            problem_report: Relatório do problema a ser corrigido
            
        Returns:
            True se a correção foi bem-sucedida, False caso contrário
        """
        pass
    
    def _can_attempt(self) -> bool:
        """Verifica se pode tentar novamente"""
        if self.attempt_count >= self.config.max_strategy_attempts:
            return False
        
        if self.last_attempt:
            time_since_last = datetime.now() - self.last_attempt
            if time_since_last.total_seconds() < self.config.strategy_cooldown:
                return False
        
        return True
    
    def _record_attempt(self):
        """Registra uma tentativa"""
        self.attempt_count += 1
        self.last_attempt = datetime.now()


class ServiceRestartStrategy(HealingStrategy):
    """Estratégia para reiniciar serviços"""
    
    async def apply(self, problem_report) -> bool:
        """
        Reinicia um serviço
        
        Args:
            problem_report: Relatório do problema
            
        Returns:
            True se o restart foi bem-sucedido
        """
        if not self._can_attempt():
            logger.warning(f"[HEALING] Limite de tentativas excedido para restart de {problem_report.service_name}")
            return False
        
        start_time = time.time()
        service_name = problem_report.service_name
        
        try:
            logger.info(f"[HEALING] Iniciando restart do serviço: {service_name}")
            
            # Verificar se o serviço está rodando
            if not await self._is_service_running(service_name):
                logger.info(f"[HEALING] Serviço {service_name} não está rodando, iniciando...")
                success = await self._start_service(service_name)
            else:
                logger.info(f"[HEALING] Reiniciando serviço {service_name}")
                success = await self._restart_service(service_name)
            
            # Aguardar serviço ficar pronto
            if success:
                success = await self._wait_for_service_ready(service_name)
            
            duration = time.time() - start_time
            self._record_attempt()
            
            if success:
                logger.info(f"[HEALING] Restart bem-sucedido para {service_name} em {duration:.2f}s")
            else:
                logger.error(f"[HEALING] Falha no restart de {service_name} após {duration:.2f}s")
            
            return success
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"[HEALING] Erro no restart de {service_name}: {e}")
            self._record_attempt()
            return False
    
    async def _is_service_running(self, service_name: str) -> bool:
        """Verifica se um serviço está rodando"""
        try:
            # Verificar processo por nome
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if service_name.lower() in proc.info['name'].lower():
                    return True
                
                # Verificar linha de comando
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline']).lower()
                    if service_name.lower() in cmdline:
                        return True
            
            return False
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao verificar se serviço está rodando: {e}")
            return False
    
    async def _start_service(self, service_name: str) -> bool:
        """Inicia um serviço"""
        try:
            # Tentar diferentes métodos de inicialização
            methods = [
                lambda: self._start_via_systemctl(service_name),
                lambda: self._start_via_docker(service_name),
                lambda: self._start_via_python(service_name),
                lambda: self._start_via_script(service_name)
            ]
            
            for method in methods:
                try:
                    if await method():
                        return True
                except Exception as e:
                    logger.debug(f"[HEALING] Método de inicialização falhou: {e}")
                    continue
            
            return False
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao iniciar serviço {service_name}: {e}")
            return False
    
    async def _restart_service(self, service_name: str) -> bool:
        """Reinicia um serviço"""
        try:
            # Parar serviço primeiro
            await self._stop_service(service_name)
            
            # Aguardar um pouco
            await asyncio.sleep(2)
            
            # Iniciar novamente
            return await self._start_service(service_name)
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao reiniciar serviço {service_name}: {e}")
            return False
    
    async def _stop_service(self, service_name: str) -> bool:
        """Para um serviço"""
        try:
            # Encontrar e parar processo
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if service_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    proc.wait(timeout=10)
                    return True
                
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline']).lower()
                    if service_name.lower() in cmdline:
                        proc.terminate()
                        proc.wait(timeout=10)
                        return True
            
            return True
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao parar serviço {service_name}: {e}")
            return False
    
    async def _start_via_systemctl(self, service_name: str) -> bool:
        """Inicia serviço via systemctl"""
        try:
            result = subprocess.run(
                ['systemctl', 'start', service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False
    
    async def _start_via_docker(self, service_name: str) -> bool:
        """Inicia serviço via Docker"""
        try:
            result = subprocess.run(
                ['docker', 'start', service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False
    
    async def _start_via_python(self, service_name: str) -> bool:
        """Inicia serviço Python"""
        try:
            # Mapear nomes de serviços para scripts Python
            service_scripts = {
                'execucao_service': 'backend/app/services/execucao_service.py',
                'validation_service': 'backend/app/services/validation_service.py',
                'onboarding_service': 'backend/app/services/onboarding_service.py'
            }
            
            script_path = service_scripts.get(service_name)
            if not script_path or not os.path.exists(script_path):
                return False
            
            subprocess.Popen(
                ['python', script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        
        except Exception:
            return False
    
    async def _start_via_script(self, service_name: str) -> bool:
        """Inicia serviço via script"""
        try:
            script_path = f"scripts/start_{service_name}.sh"
            if os.path.exists(script_path):
                subprocess.run(
                    ['bash', script_path],
                    capture_output=True,
                    timeout=30
                )
                return True
            return False
        except Exception:
            return False
    
    async def _wait_for_service_ready(self, service_name: str, timeout: int = 60) -> bool:
        """Aguarda serviço ficar pronto"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Verificar se processo está rodando
                if not await self._is_service_running(service_name):
                    await asyncio.sleep(2)
                    continue
                
                # Verificar health check se disponível
                if await self._check_service_health(service_name):
                    return True
                
                await asyncio.sleep(2)
            
            except Exception as e:
                logger.debug(f"[HEALING] Erro ao verificar readiness: {e}")
                await asyncio.sleep(2)
        
        return False
    
    async def _check_service_health(self, service_name: str) -> bool:
        """Verifica saúde do serviço"""
        try:
            # Mapear serviços para endpoints de health check
            health_endpoints = {
                'execucao_service': 'http://localhost:8000/health/execucao',
                'validation_service': 'http://localhost:8000/health/validation',
                'onboarding_service': 'http://localhost:8000/health/onboarding'
            }
            
            endpoint = health_endpoints.get(service_name)
            if not endpoint:
                return True  # Se não tem endpoint, assume que está saudável
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, timeout=5) as response:
                    return response.status == 200
        
        except Exception:
            return False


class ConnectionRecoveryStrategy(HealingStrategy):
    """Estratégia para recuperar conexões"""
    
    async def apply(self, problem_report) -> bool:
        """
        Recupera conexões perdidas
        
        Args:
            problem_report: Relatório do problema
            
        Returns:
            True se a recuperação foi bem-sucedida
        """
        if not self._can_attempt():
            logger.warning(f"[HEALING] Limite de tentativas excedido para recuperação de {problem_report.service_name}")
            return False
        
        start_time = time.time()
        service_name = problem_report.service_name
        
        try:
            logger.info(f"[HEALING] Iniciando recuperação de conexão para: {service_name}")
            
            # Identificar tipo de conexão baseado no serviço
            connection_type = self._identify_connection_type(service_name)
            
            # Aplicar estratégia específica
            if connection_type == "database":
                success = await self._recover_database_connection(service_name)
            elif connection_type == "cache":
                success = await self._recover_cache_connection(service_name)
            elif connection_type == "api":
                success = await self._recover_api_connection(service_name)
            else:
                success = await self._recover_generic_connection(service_name)
            
            duration = time.time() - start_time
            self._record_attempt()
            
            if success:
                logger.info(f"[HEALING] Recuperação de conexão bem-sucedida para {service_name} em {duration:.2f}s")
            else:
                logger.error(f"[HEALING] Falha na recuperação de conexão de {service_name} após {duration:.2f}s")
            
            return success
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"[HEALING] Erro na recuperação de conexão de {service_name}: {e}")
            self._record_attempt()
            return False
    
    def _identify_connection_type(self, service_name: str) -> str:
        """Identifica o tipo de conexão baseado no nome do serviço"""
        if 'database' in service_name.lower() or 'db' in service_name.lower():
            return "database"
        elif 'cache' in service_name.lower() or 'redis' in service_name.lower():
            return "cache"
        elif 'api' in service_name.lower() or 'external' in service_name.lower():
            return "api"
        else:
            return "generic"
    
    async def _recover_database_connection(self, service_name: str) -> bool:
        """Recupera conexão com banco de dados"""
        try:
            # Recarregar pool de conexões
            from infrastructure.database.connection_manager import DatabaseConnectionManager
            
            manager = DatabaseConnectionManager()
            await manager.reload_connections()
            
            # Testar conexão
            return await manager.test_connection()
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao recuperar conexão de banco: {e}")
            return False
    
    async def _recover_cache_connection(self, service_name: str) -> bool:
        """Recupera conexão com cache"""
        try:
            # Recarregar conexão Redis
            from infrastructure.cache.redis_manager import RedisManager
            
            manager = RedisManager()
            await manager.reconnect()
            
            # Testar conexão
            return await manager.test_connection()
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao recuperar conexão de cache: {e}")
            return False
    
    async def _recover_api_connection(self, service_name: str) -> bool:
        """Recupera conexão com API externa"""
        try:
            # Limpar cache de sessões HTTP
            import aiohttp
            
            # Testar conectividade
            async with aiohttp.ClientSession() as session:
                async with session.get('https://httpbin.org/get', timeout=10) as response:
                    return response.status == 200
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao recuperar conexão de API: {e}")
            return False
    
    async def _recover_generic_connection(self, service_name: str) -> bool:
        """Recupera conexão genérica"""
        try:
            # Tentar reiniciar o serviço como fallback
            restart_strategy = ServiceRestartStrategy(self.config)
            return await restart_strategy.apply(type('ProblemReport', (), {
                'service_name': service_name,
                'problem_type': type('ProblemType', (), {'value': 'connection_error'})()
            })())
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao recuperar conexão genérica: {e}")
            return False


class ResourceCleanupStrategy(HealingStrategy):
    """Estratégia para limpeza de recursos"""
    
    async def apply(self, problem_report) -> bool:
        """
        Limpa recursos esgotados
        
        Args:
            problem_report: Relatório do problema
            
        Returns:
            True se a limpeza foi bem-sucedida
        """
        if not self._can_attempt():
            logger.warning(f"[HEALING] Limite de tentativas excedido para limpeza de {problem_report.service_name}")
            return False
        
        start_time = time.time()
        service_name = problem_report.service_name
        
        try:
            logger.info(f"[HEALING] Iniciando limpeza de recursos para: {service_name}")
            
            # Limpar diferentes tipos de recursos
            memory_cleaned = await self._cleanup_memory()
            disk_cleaned = await self._cleanup_disk()
            temp_cleaned = await self._cleanup_temp_files()
            
            success = memory_cleaned or disk_cleaned or temp_cleaned
            
            duration = time.time() - start_time
            self._record_attempt()
            
            if success:
                logger.info(f"[HEALING] Limpeza de recursos bem-sucedida para {service_name} em {duration:.2f}s")
            else:
                logger.warning(f"[HEALING] Nenhum recurso foi limpo para {service_name}")
            
            return success
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"[HEALING] Erro na limpeza de recursos de {service_name}: {e}")
            self._record_attempt()
            return False
    
    async def _cleanup_memory(self) -> bool:
        """Limpa memória"""
        try:
            # Forçar garbage collection
            import gc
            gc.collect()
            
            # Limpar cache de objetos
            import sys
            for obj in gc.get_objects():
                if hasattr(obj, '__dict__'):
                    obj.__dict__.clear()
            
            return True
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao limpar memória: {e}")
            return False
    
    async def _cleanup_disk(self) -> bool:
        """Limpa espaço em disco"""
        try:
            # Remover arquivos temporários
            temp_dirs = ['/tmp', '/var/tmp', 'temp', 'logs']
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for file in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, file)
                        try:
                            if os.path.isfile(file_path):
                                # Remover arquivos antigos (mais de 24h)
                                if time.time() - os.path.getmtime(file_path) > 86400:
                                    os.remove(file_path)
                        except Exception:
                            continue
            
            return True
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao limpar disco: {e}")
            return False
    
    async def _cleanup_temp_files(self) -> bool:
        """Limpa arquivos temporários específicos do serviço"""
        try:
            # Limpar logs antigos
            log_dirs = ['logs', 'backend/logs', 'infrastructure/logs']
            
            for log_dir in log_dirs:
                if os.path.exists(log_dir):
                    for file in os.listdir(log_dir):
                        if file.endswith('.log'):
                            file_path = os.path.join(log_dir, file)
                            try:
                                # Remover logs antigos (mais de 7 dias)
                                if time.time() - os.path.getmtime(file_path) > 604800:
                                    os.remove(file_path)
                            except Exception:
                                continue
            
            return True
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao limpar arquivos temporários: {e}")
            return False


class ConfigurationReloadStrategy(HealingStrategy):
    """Estratégia para recarregar configurações"""
    
    async def apply(self, problem_report) -> bool:
        """
        Recarrega configurações
        
        Args:
            problem_report: Relatório do problema
            
        Returns:
            True se o recarregamento foi bem-sucedido
        """
        if not self._can_attempt():
            logger.warning(f"[HEALING] Limite de tentativas excedido para recarregamento de {problem_report.service_name}")
            return False
        
        start_time = time.time()
        service_name = problem_report.service_name
        
        try:
            logger.info(f"[HEALING] Iniciando recarregamento de configuração para: {service_name}")
            
            # Recarregar diferentes tipos de configuração
            app_config_reloaded = await self._reload_app_config()
            db_config_reloaded = await self._reload_database_config()
            cache_config_reloaded = await self._reload_cache_config()
            
            success = app_config_reloaded or db_config_reloaded or cache_config_reloaded
            
            duration = time.time() - start_time
            self._record_attempt()
            
            if success:
                logger.info(f"[HEALING] Recarregamento de configuração bem-sucedido para {service_name} em {duration:.2f}s")
            else:
                logger.warning(f"[HEALING] Nenhuma configuração foi recarregada para {service_name}")
            
            return success
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"[HEALING] Erro no recarregamento de configuração de {service_name}: {e}")
            self._record_attempt()
            return False
    
    async def _reload_app_config(self) -> bool:
        """Recarrega configuração da aplicação"""
        try:
            # Recarregar configurações do backend
            from backend.app.config import Config
            
            config = Config()
            config.reload()
            
            return True
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao recarregar configuração da aplicação: {e}")
            return False
    
    async def _reload_database_config(self) -> bool:
        """Recarrega configuração do banco de dados"""
        try:
            # Recarregar configurações de banco
            from infrastructure.database.connection_manager import DatabaseConnectionManager
            
            manager = DatabaseConnectionManager()
            await manager.reload_config()
            
            return True
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao recarregar configuração de banco: {e}")
            return False
    
    async def _reload_cache_config(self) -> bool:
        """Recarrega configuração de cache"""
        try:
            # Recarregar configurações de cache
            from infrastructure.cache.redis_manager import RedisManager
            
            manager = RedisManager()
            await manager.reload_config()
            
            return True
        
        except Exception as e:
            logger.error(f"[HEALING] Erro ao recarregar configuração de cache: {e}")
            return False


class HealingStrategyFactory:
    """Factory para criar estratégias de healing"""
    
    @staticmethod
    def create_strategy(strategy_type: str, config: HealingConfig) -> HealingStrategy:
        """
        Cria uma estratégia de healing
        
        Args:
            strategy_type: Tipo da estratégia
            config: Configuração do sistema
            
        Returns:
            Estratégia de healing
        """
        strategies = {
            'service_restart': ServiceRestartStrategy,
            'connection_recovery': ConnectionRecoveryStrategy,
            'resource_cleanup': ResourceCleanupStrategy,
            'configuration_reload': ConfigurationReloadStrategy
        }
        
        strategy_class = strategies.get(strategy_type)
        if not strategy_class:
            raise ValueError(f"Estratégia desconhecida: {strategy_type}")
        
        return strategy_class(config) 
"""
Integration Module - Omni Keywords Finder

Módulo responsável por integrar o orquestrador com o sistema existente:
- Modelos de dados (nichos, categorias, execuções)
- Sistema de prompts
- Logs e auditoria
- Configurações do sistema

Tracing ID: INTEGRATION_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import logging
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
import json
import sqlite3
from dataclasses import dataclass, field

# Importações do sistema existente
try:
    from backend.app.models.nicho import Nicho
    from backend.app.models.categoria import Categoria
    from backend.app.models.execucao import Execucao
    from backend.app.models.log import Log
    from backend.app.models.prompt_system import PromptSystem
    from backend.app.models.notificacao import Notificacao
    SYSTEM_AVAILABLE = True
except ImportError:
    SYSTEM_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Sistema backend não disponível - usando modo simulado")

logger = logging.getLogger(__name__)


@dataclass
class IntegrationConfig:
    """Configuração da integração."""
    database_url: str = "sqlite:///backend/instance/db.sqlite3"
    enable_real_integration: bool = True
    fallback_to_simulation: bool = True
    log_level: str = "INFO"
    max_retries: int = 3
    retry_delay: float = 1.0


class SystemIntegration:
    """Integração com o sistema existente."""
    
    def __init__(self, config: Optional[IntegrationConfig] = None):
        """
        Inicializa a integração.
        
        Args:
            config: Configuração da integração
        """
        self.config = config or IntegrationConfig()
        self.connection = None
        self._setup_logging()
        
        if self.config.enable_real_integration and SYSTEM_AVAILABLE:
            self._connect_to_database()
        else:
            logger.info("Usando modo de integração simulado")
    
    def _setup_logging(self):
        """Configura logging para integração."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)string_data - %(name)string_data - %(levelname)string_data - %(message)string_data'
        )
    
    def _connect_to_database(self):
        """Conecta ao banco de dados."""
        try:
            if self.config.database_url.startswith("sqlite:///"):
                db_path = self.config.database_url.replace("sqlite:///", "")
                self.connection = sqlite3.connect(db_path)
                self.connection.row_factory = sqlite3.Row
                logger.info(f"Conectado ao banco SQLite: {db_path}")
            else:
                logger.warning(f"Tipo de banco não suportado: {self.config.database_url}")
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco: {e}")
            if self.config.fallback_to_simulation:
                logger.info("Falhando para modo simulado")
    
    def registrar_execucao(
        self, 
        sessao_id: str, 
        nicho: str, 
        status: str,
        metadados: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Registra uma execução no sistema.
        
        Args:
            sessao_id: ID da sessão
            nicho: Nome do nicho
            status: Status da execução
            metadados: Metadados adicionais
            
        Returns:
            True se registrado com sucesso
        """
        try:
            if self.connection and SYSTEM_AVAILABLE:
                return self._registrar_execucao_real(sessao_id, nicho, status, metadados)
            else:
                return self._registrar_execucao_simulada(sessao_id, nicho, status, metadados)
        except Exception as e:
            logger.error(f"Erro ao registrar execução: {e}")
            return False
    
    def _registrar_execucao_real(
        self, 
        sessao_id: str, 
        nicho: str, 
        status: str,
        metadados: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Registra execução no banco real."""
        try:
            cursor = self.connection.cursor()
            
            # Buscar ID do nicho
            cursor.execute("SELECT id FROM nicho WHERE nome = ?", (nicho,))
            nicho_result = cursor.fetchone()
            
            if not nicho_result:
                logger.warning(f"Nicho não encontrado: {nicho}")
                return False
            
            nicho_id = nicho_result['id']
            
            # Inserir execução
            cursor.execute("""
                INSERT INTO execucao (sessao_id, nicho_id, status, inicio_timestamp, metadados)
                VALUES (?, ?, ?, ?, ?)
            """, (
                sessao_id,
                nicho_id,
                status,
                datetime.now().isoformat(),
                json.dumps(metadados or {})
            ))
            
            self.connection.commit()
            logger.info(f"Execução registrada: {sessao_id} - {nicho} - {status}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao registrar execução real: {e}")
            return False
    
    def _registrar_execucao_simulada(
        self, 
        sessao_id: str, 
        nicho: str, 
        status: str,
        metadados: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Registra execução simulada."""
        execucao_data = {
            "sessao_id": sessao_id,
            "nicho": nicho,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "metadados": metadados or {}
        }
        
        # Salvar em arquivo local para simulação
        log_dir = Path("logs/execucoes")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"execucao_{sessao_id}_{int(time.time())}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(execucao_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Execução simulada registrada: {log_file}")
        return True
    
    def registrar_log(
        self, 
        sessao_id: str, 
        nivel: str, 
        mensagem: str,
        contexto: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Registra um log no sistema.
        
        Args:
            sessao_id: ID da sessão
            nivel: Nível do log (INFO, WARNING, ERROR, DEBUG)
            mensagem: Mensagem do log
            contexto: Contexto adicional
            
        Returns:
            True se registrado com sucesso
        """
        try:
            if self.connection and SYSTEM_AVAILABLE:
                return self._registrar_log_real(sessao_id, nivel, mensagem, contexto)
            else:
                return self._registrar_log_simulada(sessao_id, nivel, mensagem, contexto)
        except Exception as e:
            logger.error(f"Erro ao registrar log: {e}")
            return False
    
    def _registrar_log_real(
        self, 
        sessao_id: str, 
        nivel: str, 
        mensagem: str,
        contexto: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Registra log no banco real."""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO log (sessao_id, nivel, mensagem, timestamp, contexto)
                VALUES (?, ?, ?, ?, ?)
            """, (
                sessao_id,
                nivel.upper(),
                mensagem,
                datetime.now().isoformat(),
                json.dumps(contexto or {})
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao registrar log real: {e}")
            return False
    
    def _registrar_log_simulada(
        self, 
        sessao_id: str, 
        nivel: str, 
        mensagem: str,
        contexto: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Registra log simulado."""
        log_data = {
            "sessao_id": sessao_id,
            "nivel": nivel.upper(),
            "mensagem": mensagem,
            "timestamp": datetime.now().isoformat(),
            "contexto": contexto or {}
        }
        
        # Salvar em arquivo local
        log_dir = Path("logs/integration")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"log_{sessao_id}_{int(time.time())}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def obter_prompts_nicho(self, nicho: str) -> List[Dict[str, Any]]:
        """
        Obtém prompts configurados para um nicho.
        
        Args:
            nicho: Nome do nicho
            
        Returns:
            Lista de prompts configurados
        """
        try:
            if self.connection and SYSTEM_AVAILABLE:
                return self._obter_prompts_nicho_real(nicho)
            else:
                return self._obter_prompts_nicho_simulado(nicho)
        except Exception as e:
            logger.error(f"Erro ao obter prompts: {e}")
            return []
    
    def _obter_prompts_nicho_real(self, nicho: str) -> List[Dict[str, Any]]:
        """Obtém prompts do banco real."""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT p.* FROM prompt_system p
                JOIN nicho n ON p.nicho_id = n.id
                WHERE n.nome = ? AND p.ativo = 1
                ORDER BY p.ordem
            """, (nicho,))
            
            prompts = []
            for row in cursor.fetchall():
                prompts.append(dict(row))
            
            return prompts
            
        except Exception as e:
            logger.error(f"Erro ao obter prompts reais: {e}")
            return []
    
    def _obter_prompts_nicho_simulado(self, nicho: str) -> List[Dict[str, Any]]:
        """Obtém prompts simulados."""
        # Prompts padrão para simulação
        prompts_padrao = {
            "tecnologia": [
                {
                    "id": 1,
                    "nome": "Análise de Produto",
                    "template": "Analise o produto {keyword} e forneça insights sobre...",
                    "ordem": 1,
                    "ativo": True
                },
                {
                    "id": 2,
                    "nome": "Comparação de Mercado",
                    "template": "Compare {keyword} com alternativas do mercado...",
                    "ordem": 2,
                    "ativo": True
                }
            ],
            "saude": [
                {
                    "id": 3,
                    "nome": "Benefícios para Saúde",
                    "template": "Explique os benefícios de {keyword} para a saúde...",
                    "ordem": 1,
                    "ativo": True
                }
            ]
        }
        
        return prompts_padrao.get(nicho.lower(), [])
    
    def obter_config_nicho(self, nicho: str) -> Optional[Dict[str, Any]]:
        """
        Obtém configuração específica de um nicho.
        
        Args:
            nicho: Nome do nicho
            
        Returns:
            Configuração do nicho ou None
        """
        try:
            if self.connection and SYSTEM_AVAILABLE:
                return self._obter_config_nicho_real(nicho)
            else:
                return self._obter_config_nicho_simulado(nicho)
        except Exception as e:
            logger.error(f"Erro ao obter config do nicho: {e}")
            return None
    
    def _obter_config_nicho_real(self, nicho: str) -> Optional[Dict[str, Any]]:
        """Obtém configuração do banco real."""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT n.*, c.nome as categoria_nome 
                FROM nicho n
                LEFT JOIN categoria c ON n.categoria_id = c.id
                WHERE n.nome = ?
            """, (nicho,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter config real: {e}")
            return None
    
    def _obter_config_nicho_simulado(self, nicho: str) -> Optional[Dict[str, Any]]:
        """Obtém configuração simulada."""
        configs_padrao = {
            "tecnologia": {
                "id": 1,
                "nome": "tecnologia",
                "categoria_nome": "Tecnologia",
                "ativo": True,
                "config": {
                    "max_keywords": 100,
                    "min_volume": 1000,
                    "max_competition": 0.7
                }
            },
            "saude": {
                "id": 2,
                "nome": "saude",
                "categoria_nome": "Saúde",
                "ativo": True,
                "config": {
                    "max_keywords": 50,
                    "min_volume": 500,
                    "max_competition": 0.5
                }
            }
        }
        
        return configs_padrao.get(nicho.lower())
    
    def atualizar_status_execucao(
        self, 
        sessao_id: str, 
        status: str,
        progresso: Optional[float] = None
    ) -> bool:
        """
        Atualiza o status de uma execução.
        
        Args:
            sessao_id: ID da sessão
            status: Novo status
            progresso: Progresso (0-100)
            
        Returns:
            True se atualizado com sucesso
        """
        try:
            if self.connection and SYSTEM_AVAILABLE:
                return self._atualizar_status_execucao_real(sessao_id, status, progresso)
            else:
                return self._atualizar_status_execucao_simulada(sessao_id, status, progresso)
        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}")
            return False
    
    def _atualizar_status_execucao_real(
        self, 
        sessao_id: str, 
        status: str,
        progresso: Optional[float] = None
    ) -> bool:
        """Atualiza status no banco real."""
        try:
            cursor = self.connection.cursor()
            
            if progresso is not None:
                cursor.execute("""
                    UPDATE execucao 
                    SET status = ?, progresso = ?, atualizacao_timestamp = ?
                    WHERE sessao_id = ?
                """, (status, progresso, datetime.now().isoformat(), sessao_id))
            else:
                cursor.execute("""
                    UPDATE execucao 
                    SET status = ?, atualizacao_timestamp = ?
                    WHERE sessao_id = ?
                """, (status, datetime.now().isoformat(), sessao_id))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status real: {e}")
            return False
    
    def _atualizar_status_execucao_simulada(
        self, 
        sessao_id: str, 
        status: str,
        progresso: Optional[float] = None
    ) -> bool:
        """Atualiza status simulado."""
        status_data = {
            "sessao_id": sessao_id,
            "status": status,
            "progresso": progresso,
            "timestamp": datetime.now().isoformat()
        }
        
        # Salvar em arquivo local
        log_dir = Path("logs/status")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        status_file = log_dir / f"status_{sessao_id}_{int(time.time())}.json"
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def fechar_conexao(self):
        """Fecha a conexão com o banco."""
        if self.connection:
            self.connection.close()
            logger.info("Conexão com banco fechada")


# Instância global
_integration_instance: Optional[SystemIntegration] = None


def obter_integration(config: Optional[IntegrationConfig] = None) -> SystemIntegration:
    """
    Obtém instância global da integração.
    
    Args:
        config: Configuração opcional
        
    Returns:
        Instância da integração
    """
    global _integration_instance
    
    if _integration_instance is None:
        _integration_instance = SystemIntegration(config)
    
    return _integration_instance


def registrar_execucao_integration(
    sessao_id: str, 
    nicho: str, 
    status: str,
    metadados: Optional[Dict[str, Any]] = None
) -> bool:
    """Função helper para registrar execução."""
    integration = obter_integration()
    return integration.registrar_execucao(sessao_id, nicho, status, metadados)


def registrar_log_integration(
    sessao_id: str, 
    nivel: str, 
    mensagem: str,
    contexto: Optional[Dict[str, Any]] = None
) -> bool:
    """Função helper para registrar log."""
    integration = obter_integration()
    return integration.registrar_log(sessao_id, nivel, mensagem, contexto)


def obter_prompts_integration(nicho: str) -> List[Dict[str, Any]]:
    """Função helper para obter prompts."""
    integration = obter_integration()
    return integration.obter_prompts_nicho(nicho)


def obter_config_integration(nicho: str) -> Optional[Dict[str, Any]]:
    """Função helper para obter configuração."""
    integration = obter_integration()
    return integration.obter_config_nicho(nicho) 
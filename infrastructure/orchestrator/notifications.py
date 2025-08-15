"""
Notifications Module - Omni Keywords Finder

Sistema de notificações para o orquestrador:
- Progresso em tempo real
- Alertas de falha
- Conclusão de etapas
- Notificações por diferentes canais

Tracing ID: NOTIFICATIONS_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import logging
import time
import json
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Tipos de notificação."""
    PROGRESS = "progress"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    COMPLETE = "complete"


class NotificationChannel(Enum):
    """Canais de notificação."""
    LOG = "log"
    FILE = "file"
    CALLBACK = "callback"
    WEBSOCKET = "websocket"
    EMAIL = "email"


@dataclass
class NotificationConfig:
    """Configuração do sistema de notificações."""
    enabled_channels: List[NotificationChannel] = field(default_factory=lambda: [
        NotificationChannel.LOG,
        NotificationChannel.FILE
    ])
    log_level: str = "INFO"
    file_path: str = "logs/notifications"
    websocket_url: Optional[str] = None
    email_config: Optional[Dict[str, Any]] = None
    max_queue_size: int = 1000
    flush_interval: float = 5.0  # segundos


@dataclass
class Notification:
    """Estrutura de uma notificação."""
    id: str
    type: NotificationType
    title: str
    message: str
    timestamp: datetime
    sessao_id: Optional[str] = None
    nicho: Optional[str] = None
    etapa: Optional[str] = None
    progresso: Optional[float] = None
    metadados: Dict[str, Any] = field(default_factory=dict)


class NotificationManager:
    """Gerenciador de notificações."""
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        """
        Inicializa o gerenciador de notificações.
        
        Args:
            config: Configuração das notificações
        """
        self.config = config or NotificationConfig()
        self.notification_queue = queue.Queue(maxsize=self.config.max_queue_size)
        self.callbacks: Dict[NotificationType, List[Callable]] = {
            notification_type: [] for notification_type in NotificationType
        }
        self.channels: Dict[NotificationChannel, Any] = {}
        
        self._setup_channels()
        self._start_worker()
        
        logger.info("NotificationManager inicializado")
    
    def _setup_channels(self):
        """Configura os canais de notificação."""
        for channel in self.config.enabled_channels:
            if channel == NotificationChannel.LOG:
                self.channels[channel] = self._setup_log_channel()
            elif channel == NotificationChannel.FILE:
                self.channels[channel] = self._setup_file_channel()
            elif channel == NotificationChannel.WEBSOCKET:
                self.channels[channel] = self._setup_websocket_channel()
            elif channel == NotificationChannel.EMAIL:
                self.channels[channel] = self._setup_email_channel()
    
    def _setup_log_channel(self):
        """Configura canal de log."""
        return {
            "logger": logging.getLogger("notifications"),
            "level": getattr(logging, self.config.log_level)
        }
    
    def _setup_file_channel(self):
        """Configura canal de arquivo."""
        file_path = Path(self.config.file_path)
        file_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "path": file_path,
            "current_file": None,
            "file_lock": threading.Lock()
        }
    
    def _setup_websocket_channel(self):
        """Configura canal WebSocket."""
        if not self.config.websocket_url:
            return None
        
        try:
            # Aqui você pode integrar com WebSocket real
            # Por enquanto, apenas simula
            return {
                "url": self.config.websocket_url,
                "connected": False
            }
        except Exception as e:
            logger.warning(f"WebSocket não configurado: {e}")
            return None
    
    def _setup_email_channel(self):
        """Configura canal de email."""
        if not self.config.email_config:
            return None
        
        return {
            "config": self.config.email_config,
            "enabled": True
        }
    
    def _start_worker(self):
        """Inicia worker para processar notificações."""
        self.worker_thread = threading.Thread(
            target=self._notification_worker,
            daemon=True
        )
        self.worker_thread.start()
    
    def _notification_worker(self):
        """Worker que processa notificações da fila."""
        while True:
            try:
                # Processar notificações da fila
                while not self.notification_queue.empty():
                    notification = self.notification_queue.get_nowait()
                    self._process_notification(notification)
                
                # Aguardar próximo ciclo
                time.sleep(self.config.flush_interval)
                
            except Exception as e:
                logger.error(f"Erro no worker de notificações: {e}")
                time.sleep(1)
    
    def _process_notification(self, notification: Notification):
        """Processa uma notificação individual."""
        try:
            # Processar por canal
            for channel_type, channel_config in self.channels.items():
                if channel_config is None:
                    continue
                
                if channel_type == NotificationChannel.LOG:
                    self._send_to_log(notification, channel_config)
                elif channel_type == NotificationChannel.FILE:
                    self._send_to_file(notification, channel_config)
                elif channel_type == NotificationChannel.WEBSOCKET:
                    self._send_to_websocket(notification, channel_config)
                elif channel_type == NotificationChannel.EMAIL:
                    self._send_to_email(notification, channel_config)
            
            # Executar callbacks
            self._execute_callbacks(notification)
            
        except Exception as e:
            logger.error(f"Erro ao processar notificação: {e}")
    
    def _send_to_log(self, notification: Notification, channel_config: Dict[str, Any]):
        """Envia notificação para log."""
        logger_instance = channel_config["logger"]
        level = channel_config["level"]
        
        message = f"[{notification.type.value.upper()}] {notification.title}: {notification.message}"
        
        if notification.sessao_id:
            message += f" (Sessão: {notification.sessao_id})"
        
        if notification.nicho:
            message += f" (Nicho: {notification.nicho})"
        
        if notification.progresso is not None:
            message += f" (Progresso: {notification.progresso:.1f}%)"
        
        logger_instance.log(level, message)
    
    def _send_to_file(self, notification: Notification, channel_config: Dict[str, Any]):
        """Envia notificação para arquivo."""
        with channel_config["file_lock"]:
            try:
                # Criar arquivo por data
                date_str = notification.timestamp.strftime("%Y-%m-%data")
                file_path = channel_config["path"] / f"notifications_{date_str}.jsonl"
                
                # Preparar dados para JSON
                notification_data = {
                    "id": notification.id,
                    "type": notification.type.value,
                    "title": notification.title,
                    "message": notification.message,
                    "timestamp": notification.timestamp.isoformat(),
                    "sessao_id": notification.sessao_id,
                    "nicho": notification.nicho,
                    "etapa": notification.etapa,
                    "progresso": notification.progresso,
                    "metadados": notification.metadados
                }
                
                # Escrever no arquivo
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(notification_data, ensure_ascii=False) + '\n')
                
            except Exception as e:
                logger.error(f"Erro ao escrever notificação em arquivo: {e}")
    
    def _send_to_websocket(self, notification: Notification, channel_config: Dict[str, Any]):
        """Envia notificação via WebSocket."""
        if not channel_config.get("connected", False):
            return
        
        try:
            # Aqui você implementaria o envio real via WebSocket
            # Por enquanto, apenas simula
            notification_data = {
                "id": notification.id,
                "type": notification.type.value,
                "title": notification.title,
                "message": notification.message,
                "timestamp": notification.timestamp.isoformat(),
                "sessao_id": notification.sessao_id,
                "nicho": notification.nicho,
                "etapa": notification.etapa,
                "progresso": notification.progresso,
                "metadados": notification.metadados
            }
            
            # Simular envio
            logger.debug(f"WebSocket notification: {notification_data}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar via WebSocket: {e}")
    
    def _send_to_email(self, notification: Notification, channel_config: Dict[str, Any]):
        """Envia notificação por email."""
        # Apenas notificações críticas por email
        if notification.type not in [NotificationType.ERROR, NotificationType.COMPLETE]:
            return
        
        try:
            # Aqui você implementaria o envio real de email
            # Por enquanto, apenas simula
            email_data = {
                "to": channel_config["config"].get("to", []),
                "subject": f"[Omni Keywords] {notification.title}",
                "body": f"""
                {notification.message}
                
                Sessão: {notification.sessao_id or 'N/A'}
                Nicho: {notification.nicho or 'N/A'}
                Etapa: {notification.etapa or 'N/A'}
                Progresso: {notification.progresso or 'N/A'}%
                
                Timestamp: {notification.timestamp.isoformat()}
                """
            }
            
            logger.info(f"Email notification: {email_data}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
    
    def _execute_callbacks(self, notification: Notification):
        """Executa callbacks registrados."""
        callbacks = self.callbacks.get(notification.type, [])
        
        for callback in callbacks:
            try:
                callback(notification)
            except Exception as e:
                logger.error(f"Erro ao executar callback: {e}")
    
    def notify(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        sessao_id: Optional[str] = None,
        nicho: Optional[str] = None,
        etapa: Optional[str] = None,
        progresso: Optional[float] = None,
        metadados: Optional[Dict[str, Any]] = None
    ):
        """
        Envia uma notificação.
        
        Args:
            notification_type: Tipo da notificação
            title: Título da notificação
            message: Mensagem da notificação
            sessao_id: ID da sessão
            nicho: Nome do nicho
            etapa: Nome da etapa
            progresso: Progresso (0-100)
            metadados: Metadados adicionais
        """
        notification = Notification(
            id=f"notif_{int(time.time() * 1000)}",
            type=notification_type,
            title=title,
            message=message,
            timestamp=datetime.now(),
            sessao_id=sessao_id,
            nicho=nicho,
            etapa=etapa,
            progresso=progresso,
            metadados=metadados or {}
        )
        
        try:
            self.notification_queue.put_nowait(notification)
        except queue.Full:
            logger.warning("Fila de notificações cheia - descartando notificação")
    
    def notify_progress(
        self,
        sessao_id: str,
        nicho: str,
        etapa: str,
        progresso: float,
        message: Optional[str] = None
    ):
        """Notifica progresso de uma etapa."""
        title = f"Progresso: {etapa}"
        message = message or f"Processando {etapa} para nicho {nicho}"
        
        self.notify(
            NotificationType.PROGRESS,
            title,
            message,
            sessao_id=sessao_id,
            nicho=nicho,
            etapa=etapa,
            progresso=progresso
        )
    
    def notify_success(
        self,
        sessao_id: str,
        nicho: str,
        etapa: str,
        message: Optional[str] = None
    ):
        """Notifica sucesso de uma etapa."""
        title = f"Sucesso: {etapa}"
        message = message or f"{etapa} concluída com sucesso para nicho {nicho}"
        
        self.notify(
            NotificationType.SUCCESS,
            title,
            message,
            sessao_id=sessao_id,
            nicho=nicho,
            etapa=etapa,
            progresso=100.0
        )
    
    def notify_error(
        self,
        sessao_id: str,
        nicho: str,
        etapa: str,
        error_message: str,
        error_details: Optional[Dict[str, Any]] = None
    ):
        """Notifica erro em uma etapa."""
        title = f"Erro: {etapa}"
        
        self.notify(
            NotificationType.ERROR,
            title,
            error_message,
            sessao_id=sessao_id,
            nicho=nicho,
            etapa=etapa,
            metadados={"error_details": error_details}
        )
    
    def notify_complete(
        self,
        sessao_id: str,
        nicho: str,
        message: Optional[str] = None
    ):
        """Notifica conclusão de um nicho."""
        title = f"Concluído: {nicho}"
        message = message or f"Processamento completo do nicho {nicho}"
        
        self.notify(
            NotificationType.COMPLETE,
            title,
            message,
            sessao_id=sessao_id,
            nicho=nicho,
            progresso=100.0
        )
    
    def register_callback(
        self,
        notification_type: NotificationType,
        callback: Callable[[Notification], None]
    ):
        """
        Registra um callback para um tipo de notificação.
        
        Args:
            notification_type: Tipo da notificação
            callback: Função a ser chamada
        """
        self.callbacks[notification_type].append(callback)
        logger.info(f"Callback registrado para {notification_type.value}")
    
    def unregister_callback(
        self,
        notification_type: NotificationType,
        callback: Callable[[Notification], None]
    ):
        """
        Remove um callback registrado.
        
        Args:
            notification_type: Tipo da notificação
            callback: Função a ser removida
        """
        if callback in self.callbacks[notification_type]:
            self.callbacks[notification_type].remove(callback)
            logger.info(f"Callback removido para {notification_type.value}")


# Instância global
_notification_manager: Optional[NotificationManager] = None


def obter_notification_manager(config: Optional[NotificationConfig] = None) -> NotificationManager:
    """
    Obtém instância global do gerenciador de notificações.
    
    Args:
        config: Configuração opcional
        
    Returns:
        Instância do gerenciador
    """
    global _notification_manager
    
    if _notification_manager is None:
        _notification_manager = NotificationManager(config)
    
    return _notification_manager


def notify_progress(
    sessao_id: str,
    nicho: str,
    etapa: str,
    progresso: float,
    message: Optional[str] = None
):
    """Função helper para notificar progresso."""
    manager = obter_notification_manager()
    manager.notify_progress(sessao_id, nicho, etapa, progresso, message)


def notify_success(
    sessao_id: str,
    nicho: str,
    etapa: str,
    message: Optional[str] = None
):
    """Função helper para notificar sucesso."""
    manager = obter_notification_manager()
    manager.notify_success(sessao_id, nicho, etapa, message)


def notify_error(
    sessao_id: str,
    nicho: str,
    etapa: str,
    error_message: str,
    error_details: Optional[Dict[str, Any]] = None
):
    """Função helper para notificar erro."""
    manager = obter_notification_manager()
    manager.notify_error(sessao_id, nicho, etapa, error_message, error_details)


def notify_complete(
    sessao_id: str,
    nicho: str,
    message: Optional[str] = None
):
    """Função helper para notificar conclusão."""
    manager = obter_notification_manager()
    manager.notify_complete(sessao_id, nicho, message) 
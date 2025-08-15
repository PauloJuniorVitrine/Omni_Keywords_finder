"""
Canal WebSocket para Notificações em Tempo Real
==============================================

Implementa notificações via WebSocket usando Redis pub/sub para
comunicação em tempo real com o frontend.

Tracing ID: NOTIF_20241219_001
Autor: Sistema de Notificações Avançado
Data: 2024-12-19
Versão: 1.0.0
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional

import redis
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WebSocketMessage:
    """Estrutura de mensagem WebSocket."""
    id: str
    user_id: str
    type: str
    priority: int
    subject: str
    content: str
    timestamp: str
    metadata: Dict[str, Any]


class WebSocketChannel:
    """Canal de notificação via WebSocket para notificações em tempo real."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.channel_name = "notifications"
        self.connection_pool = {}
    
    async def send(self, notification) -> bool:
        """Envia notificação via WebSocket usando Redis pub/sub."""
        try:
            message = WebSocketMessage(
                id=notification.id,
                user_id=notification.user_id,
                type=notification.type.value,
                priority=notification.priority.value,
                subject=notification.subject,
                content=notification.content,
                timestamp=datetime.utcnow().isoformat(),
                metadata=notification.metadata
            )
            
            # Publica no canal específico do usuário
            user_channel = f"{self.channel_name}:{notification.user_id}"
            self.redis_client.publish(user_channel, json.dumps(message.__dict__))
            
            # Também publica no canal global para admins
            global_channel = f"{self.channel_name}:global"
            self.redis_client.publish(global_channel, json.dumps(message.__dict__))
            
            logger.info(f"Notificação WebSocket enviada para usuário {notification.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação WebSocket: {e}")
            return False
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível."""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis não disponível: {e}")
            return False
    
    def get_name(self) -> str:
        return "websocket"
    
    def subscribe_user(self, user_id: str, callback):
        """Inscreve um usuário para receber notificações."""
        try:
            user_channel = f"{self.channel_name}:{user_id}"
            pubsub = self.redis_client.pubsub()
            pubsub.subscribe(user_channel)
            
            # Armazena conexão
            self.connection_pool[user_id] = {
                'pubsub': pubsub,
                'callback': callback
            }
            
            logger.info(f"Usuário {user_id} inscrito para notificações WebSocket")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inscrever usuário {user_id}: {e}")
            return False
    
    def unsubscribe_user(self, user_id: str):
        """Remove inscrição do usuário."""
        try:
            if user_id in self.connection_pool:
                connection = self.connection_pool[user_id]
                connection['pubsub'].unsubscribe()
                connection['pubsub'].close()
                del self.connection_pool[user_id]
                
                logger.info(f"Usuário {user_id} removido das notificações WebSocket")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao remover usuário {user_id}: {e}")
            return False
    
    def get_active_connections(self) -> int:
        """Retorna número de conexões ativas."""
        return len(self.connection_pool)
    
    def broadcast_to_all(self, message: WebSocketMessage):
        """Envia mensagem para todos os usuários conectados."""
        try:
            global_channel = f"{self.channel_name}:broadcast"
            self.redis_client.publish(global_channel, json.dumps(message.__dict__))
            
            logger.info(f"Broadcast enviado para {len(self.connection_pool)} usuários")
            return True
            
        except Exception as e:
            logger.error(f"Erro no broadcast: {e}")
            return False 
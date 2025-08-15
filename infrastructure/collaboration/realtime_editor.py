"""
Sistema de Edição Colaborativa em Tempo Real
============================================

Este módulo implementa um sistema de edição colaborativa em tempo real
usando WebSocket e Operational Transform para resolução de conflitos.

Tracing ID: COLLAB_EDITOR_001
Data: 2024-12-19
Versão: 1.0
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses_json import dataclass_json

import websockets
from websockets.server import WebSocketServerProtocol

from infrastructure.observability.telemetry import TelemetryManager
from infrastructure.observability.tracing import TracingManager
from infrastructure.observability.metrics import MetricsManager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Tipos de operações suportadas"""
    INSERT = "insert"
    DELETE = "delete"
    UPDATE = "update"
    CURSOR_MOVE = "cursor_move"
    SELECTION = "selection"


class DocumentState(Enum):
    """Estados do documento"""
    SYNCED = "synced"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    OFFLINE = "offline"


@dataclass_json
@dataclass
class Operation:
    """Representa uma operação de edição"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: OperationType = OperationType.INSERT
    position: int = 0
    content: str = ""
    timestamp: float = field(default_factory=time.time)
    user_id: str = ""
    session_id: str = ""
    version: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass_json
@dataclass
class CursorPosition:
    """Posição do cursor de um usuário"""
    user_id: str
    position: int
    timestamp: float = field(default_factory=time.time)
    color: str = "#007ACC"
    name: str = ""


@dataclass_json
@dataclass
class Document:
    """Representa um documento colaborativo"""
    id: str
    content: str = ""
    version: int = 0
    last_modified: float = field(default_factory=time.time)
    created_by: str = ""
    collaborators: Set[str] = field(default_factory=set)
    operations: List[Operation] = field(default_factory=list)
    cursors: Dict[str, CursorPosition] = field(default_factory=dict)
    state: DocumentState = DocumentState.SYNCED


class OperationalTransform:
    """Implementa Operational Transform para resolução de conflitos"""
    
    def __init__(self):
        self.telemetry = TelemetryManager()
        self.tracing = TracingManager()
        self.metrics = MetricsManager()
    
    def transform_insert_insert(self, op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """
        Transforma duas operações de inserção
        """
        with self.tracing.start_span("transform_insert_insert"):
            # Se op1 vem antes de op2, op2 deve ser movida para frente
            if op1.position <= op2.position:
                op2_transformed = Operation(
                    id=op2.id,
                    type=op2.type,
                    position=op2.position + len(op1.content),
                    content=op2.content,
                    timestamp=op2.timestamp,
                    user_id=op2.user_id,
                    session_id=op2.session_id,
                    version=op2.version,
                    metadata=op2.metadata
                )
                return op1, op2_transformed
            else:
                # op2 vem antes de op1
                op1_transformed = Operation(
                    id=op1.id,
                    type=op1.type,
                    position=op1.position + len(op2.content),
                    content=op1.content,
                    timestamp=op1.timestamp,
                    user_id=op1.user_id,
                    session_id=op1.session_id,
                    version=op1.version,
                    metadata=op1.metadata
                )
                return op1_transformed, op2
    
    def transform_insert_delete(self, insert_op: Operation, delete_op: Operation) -> Tuple[Operation, Operation]:
        """
        Transforma inserção vs deleção
        """
        with self.tracing.start_span("transform_insert_delete"):
            if insert_op.position <= delete_op.position:
                # Inserção vem antes da deleção
                delete_transformed = Operation(
                    id=delete_op.id,
                    type=delete_op.type,
                    position=delete_op.position + len(insert_op.content),
                    content=delete_op.content,
                    timestamp=delete_op.timestamp,
                    user_id=delete_op.user_id,
                    session_id=delete_op.session_id,
                    version=delete_op.version,
                    metadata=delete_op.metadata
                )
                return insert_op, delete_transformed
            else:
                # Deleção vem antes da inserção
                if delete_op.position + len(delete_op.content) >= insert_op.position:
                    # Deleção afeta a posição da inserção
                    new_position = delete_op.position
                else:
                    # Deleção não afeta a inserção
                    new_position = insert_op.position - len(delete_op.content)
                
                insert_transformed = Operation(
                    id=insert_op.id,
                    type=insert_op.type,
                    position=new_position,
                    content=insert_op.content,
                    timestamp=insert_op.timestamp,
                    user_id=insert_op.user_id,
                    session_id=insert_op.session_id,
                    version=insert_op.version,
                    metadata=insert_op.metadata
                )
                return insert_transformed, delete_op
    
    def transform_delete_delete(self, op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """
        Transforma duas operações de deleção
        """
        with self.tracing.start_span("transform_delete_delete"):
            # Implementação simplificada - em produção seria mais complexa
            return op1, op2


class RealtimeEditor:
    """Sistema principal de edição colaborativa em tempo real"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.documents: Dict[str, Document] = {}
        self.sessions: Dict[str, WebSocketServerProtocol] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.ot = OperationalTransform()
        
        # Observabilidade
        self.telemetry = TelemetryManager()
        self.tracing = TracingManager()
        self.metrics = MetricsManager()
        
        # Métricas
        self.metrics.register_counter("collaboration_operations_total", "Total de operações")
        self.metrics.register_counter("collaboration_conflicts_total", "Total de conflitos")
        self.metrics.register_gauge("collaboration_active_users", "Usuários ativos")
        self.metrics.register_histogram("collaboration_operation_latency", "Latência das operações")
    
    async def start_server(self):
        """Inicia o servidor WebSocket"""
        with self.tracing.start_span("start_collaboration_server"):
            logger.info(f"Iniciando servidor de colaboração em ws://{self.host}:{self.port}")
            
            async with websockets.serve(self.handle_connection, self.host, self.port):
                await asyncio.Future()  # Executa indefinidamente
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Gerencia conexões WebSocket"""
        session_id = str(uuid.uuid4())
        user_id = None
        
        with self.tracing.start_span("handle_websocket_connection"):
            try:
                logger.info(f"Nova conexão: {session_id}")
                self.sessions[session_id] = websocket
                
                async for message in websocket:
                    await self.process_message(session_id, message)
                    
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"Conexão fechada: {session_id}")
            except Exception as e:
                logger.error(f"Erro na conexão {session_id}: {e}")
                self.metrics.increment_counter("collaboration_errors_total")
            finally:
                await self.handle_disconnect(session_id, user_id)
    
    async def process_message(self, session_id: str, message: str):
        """Processa mensagens recebidas"""
        with self.tracing.start_span("process_collaboration_message"):
            try:
                data = json.loads(message)
                message_type = data.get("type")
                
                if message_type == "join_document":
                    await self.handle_join_document(session_id, data)
                elif message_type == "operation":
                    await self.handle_operation(session_id, data)
                elif message_type == "cursor_move":
                    await self.handle_cursor_move(session_id, data)
                elif message_type == "leave_document":
                    await self.handle_leave_document(session_id, data)
                else:
                    logger.warning(f"Tipo de mensagem desconhecido: {message_type}")
                    
            except json.JSONDecodeError:
                logger.error(f"JSON inválido recebido: {message}")
            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {e}")
                self.metrics.increment_counter("collaboration_errors_total")
    
    async def handle_join_document(self, session_id: str, data: Dict[str, Any]):
        """Gerencia entrada de usuário em um documento"""
        with self.tracing.start_span("handle_join_document"):
            document_id = data.get("document_id")
            user_id = data.get("user_id")
            user_name = data.get("user_name", "Usuário")
            
            if not document_id or not user_id:
                await self.send_error(session_id, "document_id e user_id são obrigatórios")
                return
            
            # Criar ou recuperar documento
            if document_id not in self.documents:
                self.documents[document_id] = Document(
                    id=document_id,
                    created_by=user_id
                )
            
            document = self.documents[document_id]
            document.collaborators.add(user_id)
            self.user_sessions[user_id] = session_id
            
            # Enviar estado atual do documento
            await self.send_document_state(session_id, document)
            
            # Notificar outros usuários
            await self.broadcast_user_joined(document_id, user_id, user_name)
            
            logger.info(f"Usuário {user_id} entrou no documento {document_id}")
            self.metrics.increment_gauge("collaboration_active_users", 1)
    
    async def handle_operation(self, session_id: str, data: Dict[str, Any]):
        """Processa operações de edição"""
        with self.tracing.start_span("handle_operation"):
            start_time = time.time()
            
            document_id = data.get("document_id")
            operation_data = data.get("operation", {})
            
            if not document_id or document_id not in self.documents:
                await self.send_error(session_id, "Documento não encontrado")
                return
            
            document = self.documents[document_id]
            
            # Criar operação
            operation = Operation(
                type=OperationType(operation_data.get("type")),
                position=operation_data.get("position", 0),
                content=operation_data.get("content", ""),
                user_id=operation_data.get("user_id"),
                session_id=session_id,
                version=document.version + 1
            )
            
            # Aplicar operação
            await self.apply_operation(document, operation)
            
            # Broadcast para outros usuários
            await self.broadcast_operation(document_id, operation)
            
            # Métricas
            latency = time.time() - start_time
            self.metrics.record_histogram("collaboration_operation_latency", latency)
            self.metrics.increment_counter("collaboration_operations_total")
            
            logger.info(f"Operação aplicada: {operation.type.value} em {document_id}")
    
    async def apply_operation(self, document: Document, operation: Operation):
        """Aplica uma operação ao documento"""
        with self.tracing.start_span("apply_operation"):
            # Transformar operação contra operações pendentes
            transformed_operation = self.transform_operation(document, operation)
            
            # Aplicar ao conteúdo
            if transformed_operation.type == OperationType.INSERT:
                document.content = (
                    document.content[:transformed_operation.position] +
                    transformed_operation.content +
                    document.content[transformed_operation.position:]
                )
            elif transformed_operation.type == OperationType.DELETE:
                start_pos = transformed_operation.position
                end_pos = start_pos + len(transformed_operation.content)
                document.content = (
                    document.content[:start_pos] +
                    document.content[end_pos:]
                )
            
            # Adicionar à lista de operações
            document.operations.append(transformed_operation)
            document.version += 1
            document.last_modified = time.time()
    
    def transform_operation(self, document: Document, operation: Operation) -> Operation:
        """Transforma operação contra operações existentes"""
        with self.tracing.start_span("transform_operation"):
            transformed_op = operation
            
            # Aplicar transformações contra operações recentes
            for existing_op in document.operations[-10:]:  # Últimas 10 operações
                if existing_op.id != operation.id:
                    transformed_op = self.transform_pair(transformed_op, existing_op)
            
            return transformed_op
    
    def transform_pair(self, op1: Operation, op2: Operation) -> Operation:
        """Transforma um par de operações"""
        with self.tracing.start_span("transform_pair"):
            if op1.type == OperationType.INSERT and op2.type == OperationType.INSERT:
                op1_transformed, _ = self.ot.transform_insert_insert(op1, op2)
                return op1_transformed
            elif op1.type == OperationType.INSERT and op2.type == OperationType.DELETE:
                op1_transformed, _ = self.ot.transform_insert_delete(op1, op2)
                return op1_transformed
            elif op1.type == OperationType.DELETE and op2.type == OperationType.INSERT:
                op1_transformed, _ = self.ot.transform_insert_delete(op2, op1)
                return op1_transformed
            elif op1.type == OperationType.DELETE and op2.type == OperationType.DELETE:
                op1_transformed, _ = self.ot.transform_delete_delete(op1, op2)
                return op1_transformed
            else:
                return op1
    
    async def handle_cursor_move(self, session_id: str, data: Dict[str, Any]):
        """Gerencia movimento de cursor"""
        with self.tracing.start_span("handle_cursor_move"):
            document_id = data.get("document_id")
            user_id = data.get("user_id")
            position = data.get("position", 0)
            color = data.get("color", "#007ACC")
            name = data.get("name", "Usuário")
            
            if not document_id or document_id not in self.documents:
                return
            
            document = self.documents[document_id]
            
            # Atualizar posição do cursor
            cursor = CursorPosition(
                user_id=user_id,
                position=position,
                color=color,
                name=name
            )
            document.cursors[user_id] = cursor
            
            # Broadcast para outros usuários
            await self.broadcast_cursor_move(document_id, cursor)
    
    async def handle_leave_document(self, session_id: str, data: Dict[str, Any]):
        """Gerencia saída de usuário do documento"""
        with self.tracing.start_span("handle_leave_document"):
            document_id = data.get("document_id")
            user_id = data.get("user_id")
            
            if document_id and document_id in self.documents:
                document = self.documents[document_id]
                document.collaborators.discard(user_id)
                
                # Remover cursor
                if user_id in document.cursors:
                    del document.cursors[user_id]
                
                # Notificar outros usuários
                await self.broadcast_user_left(document_id, user_id)
                
                logger.info(f"Usuário {user_id} saiu do documento {document_id}")
                self.metrics.increment_gauge("collaboration_active_users", -1)
    
    async def handle_disconnect(self, session_id: str, user_id: Optional[str]):
        """Gerencia desconexão de usuário"""
        with self.tracing.start_span("handle_disconnect"):
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            if user_id and user_id in self.user_sessions:
                del self.user_sessions[user_id]
                
                # Remover de todos os documentos
                for document in self.documents.values():
                    if user_id in document.collaborators:
                        document.collaborators.discard(user_id)
                    if user_id in document.cursors:
                        del document.cursors[user_id]
            
            logger.info(f"Usuário desconectado: {user_id}")
            if user_id:
                self.metrics.increment_gauge("collaboration_active_users", -1)
    
    async def send_document_state(self, session_id: str, document: Document):
        """Envia estado atual do documento para um usuário"""
        if session_id not in self.sessions:
            return
        
        message = {
            "type": "document_state",
            "document_id": document.id,
            "content": document.content,
            "version": document.version,
            "cursors": {uid: cursor.to_dict() for uid, cursor in document.cursors.items()},
            "collaborators": list(document.collaborators)
        }
        
        await self.sessions[session_id].send(json.dumps(message))
    
    async def broadcast_operation(self, document_id: str, operation: Operation):
        """Envia operação para todos os usuários do documento"""
        if document_id not in self.documents:
            return
        
        document = self.documents[document_id]
        message = {
            "type": "operation",
            "document_id": document_id,
            "operation": operation.to_dict()
        }
        
        await self.broadcast_to_document(document_id, message)
    
    async def broadcast_cursor_move(self, document_id: str, cursor: CursorPosition):
        """Envia movimento de cursor para outros usuários"""
        message = {
            "type": "cursor_move",
            "document_id": document_id,
            "cursor": cursor.to_dict()
        }
        
        await self.broadcast_to_document(document_id, message, exclude_user=cursor.user_id)
    
    async def broadcast_user_joined(self, document_id: str, user_id: str, user_name: str):
        """Notifica entrada de usuário"""
        message = {
            "type": "user_joined",
            "document_id": document_id,
            "user_id": user_id,
            "user_name": user_name
        }
        
        await self.broadcast_to_document(document_id, message, exclude_user=user_id)
    
    async def broadcast_user_left(self, document_id: str, user_id: str):
        """Notifica saída de usuário"""
        message = {
            "type": "user_left",
            "document_id": document_id,
            "user_id": user_id
        }
        
        await self.broadcast_to_document(document_id, message, exclude_user=user_id)
    
    async def broadcast_to_document(self, document_id: str, message: Dict[str, Any], exclude_user: Optional[str] = None):
        """Envia mensagem para todos os usuários de um documento"""
        if document_id not in self.documents:
            return
        
        document = self.documents[document_id]
        message_json = json.dumps(message)
        
        for user_id in document.collaborators:
            if user_id == exclude_user:
                continue
            
            if user_id in self.user_sessions:
                session_id = self.user_sessions[user_id]
                if session_id in self.sessions:
                    try:
                        await self.sessions[session_id].send(message_json)
                    except Exception as e:
                        logger.error(f"Erro ao enviar mensagem para {user_id}: {e}")
    
    async def send_error(self, session_id: str, error_message: str):
        """Envia mensagem de erro para um usuário"""
        if session_id not in self.sessions:
            return
        
        message = {
            "type": "error",
            "message": error_message
        }
        
        try:
            await self.sessions[session_id].send(json.dumps(message))
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de erro: {e}")
    
    def get_document_stats(self, document_id: str) -> Dict[str, Any]:
        """Retorna estatísticas de um documento"""
        if document_id not in self.documents:
            return {}
        
        document = self.documents[document_id]
        return {
            "id": document.id,
            "content_length": len(document.content),
            "version": document.version,
            "collaborators_count": len(document.collaborators),
            "operations_count": len(document.operations),
            "last_modified": document.last_modified,
            "created_by": document.created_by
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        return {
            "active_sessions": len(self.sessions),
            "active_users": len(self.user_sessions),
            "documents_count": len(self.documents),
            "total_operations": sum(len(doc.operations) for doc in self.documents.values())
        }


# Função principal para iniciar o servidor
async def main():
    """Função principal para iniciar o servidor de colaboração"""
    editor = RealtimeEditor()
    await editor.start_server()


if __name__ == "__main__":
    asyncio.run(main()) 
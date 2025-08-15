"""
Sistema de Comentários Colaborativos em Tempo Real
==================================================

Este módulo implementa um sistema de comentários colaborativos em tempo real
integrado com o sistema de edição colaborativa.

Tracing ID: COLLAB_COMMENT_001
Data: 2024-12-19
Versão: 1.0
"""

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from dataclasses_json import dataclass_json

from infrastructure.observability.telemetry import TelemetryManager
from infrastructure.observability.tracing import TracingManager
from infrastructure.observability.metrics import MetricsManager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommentStatus(Enum):
    """Status dos comentários"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


class CommentType(Enum):
    """Tipos de comentários"""
    GENERAL = "general"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    BUG = "bug"
    FEATURE = "feature"


@dataclass_json
@dataclass
class CommentReply:
    """Resposta a um comentário"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    content: str = ""
    timestamp: float = field(default_factory=time.time)
    edited: bool = False
    edited_at: Optional[float] = None


@dataclass_json
@dataclass
class Comment:
    """Representa um comentário colaborativo"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = ""
    user_id: str = ""
    content: str = ""
    position: int = 0
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None
    comment_type: CommentType = CommentType.GENERAL
    status: CommentStatus = CommentStatus.ACTIVE
    timestamp: float = field(default_factory=time.time)
    edited: bool = False
    edited_at: Optional[float] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[float] = None
    replies: List[CommentReply] = field(default_factory=list)
    mentions: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass_json
@dataclass
class CommentThread:
    """Thread de comentários"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = ""
    main_comment: Comment = field(default_factory=lambda: Comment())
    replies: List[CommentReply] = field(default_factory=list)
    participants: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    is_resolved: bool = False


class CommentSystem:
    """Sistema principal de comentários colaborativos"""
    
    def __init__(self):
        self.comments: Dict[str, Comment] = {}
        self.threads: Dict[str, CommentThread] = {}
        self.document_comments: Dict[str, List[str]] = {}  # document_id -> comment_ids
        self.user_comments: Dict[str, List[str]] = {}  # user_id -> comment_ids
        
        # Observabilidade
        self.telemetry = TelemetryManager()
        self.tracing = TracingManager()
        self.metrics = MetricsManager()
        
        # Métricas
        self.metrics.register_counter("comments_created_total", "Total de comentários criados")
        self.metrics.register_counter("comments_resolved_total", "Total de comentários resolvidos")
        self.metrics.register_counter("comment_replies_total", "Total de respostas")
        self.metrics.register_gauge("active_comments", "Comentários ativos")
        self.metrics.register_histogram("comment_creation_latency", "Latência de criação de comentários")
    
    def create_comment(self, document_id: str, user_id: str, content: str, 
                      position: int = 0, selection_start: Optional[int] = None,
                      selection_end: Optional[int] = None, comment_type: CommentType = CommentType.GENERAL,
                      mentions: Optional[Set[str]] = None, tags: Optional[Set[str]] = None) -> Comment:
        """Cria um novo comentário"""
        with self.tracing.start_span("create_comment"):
            start_time = time.time()
            
            comment = Comment(
                document_id=document_id,
                user_id=user_id,
                content=content,
                position=position,
                selection_start=selection_start,
                selection_end=selection_end,
                comment_type=comment_type,
                mentions=mentions or set(),
                tags=tags or set()
            )
            
            # Adicionar ao sistema
            self.comments[comment.id] = comment
            
            # Indexar por documento
            if document_id not in self.document_comments:
                self.document_comments[document_id] = []
            self.document_comments[document_id].append(comment.id)
            
            # Indexar por usuário
            if user_id not in self.user_comments:
                self.user_comments[user_id] = []
            self.user_comments[user_id].append(comment.id)
            
            # Criar thread
            thread = CommentThread(
                document_id=document_id,
                main_comment=comment,
                participants={user_id}
            )
            self.threads[comment.id] = thread
            
            # Métricas
            latency = time.time() - start_time
            self.metrics.record_histogram("comment_creation_latency", latency)
            self.metrics.increment_counter("comments_created_total")
            self.metrics.increment_gauge("active_comments", 1)
            
            logger.info(f"Comentário criado: {comment.id} em {document_id}")
            return comment
    
    def add_reply(self, comment_id: str, user_id: str, content: str) -> CommentReply:
        """Adiciona uma resposta a um comentário"""
        with self.tracing.start_span("add_reply"):
            if comment_id not in self.comments:
                raise ValueError(f"Comentário não encontrado: {comment_id}")
            
            comment = self.comments[comment_id]
            thread = self.threads[comment_id]
            
            reply = CommentReply(
                user_id=user_id,
                content=content
            )
            
            # Adicionar resposta
            comment.replies.append(reply)
            thread.replies.append(reply)
            thread.participants.add(user_id)
            thread.last_activity = time.time()
            
            # Métricas
            self.metrics.increment_counter("comment_replies_total")
            
            logger.info(f"Resposta adicionada ao comentário {comment_id}")
            return reply
    
    def edit_comment(self, comment_id: str, user_id: str, new_content: str) -> Comment:
        """Edita um comentário"""
        with self.tracing.start_span("edit_comment"):
            if comment_id not in self.comments:
                raise ValueError(f"Comentário não encontrado: {comment_id}")
            
            comment = self.comments[comment_id]
            
            # Verificar permissão
            if comment.user_id != user_id:
                raise PermissionError("Apenas o autor pode editar o comentário")
            
            # Atualizar conteúdo
            comment.content = new_content
            comment.edited = True
            comment.edited_at = time.time()
            
            # Atualizar thread
            if comment_id in self.threads:
                self.threads[comment_id].last_activity = time.time()
            
            logger.info(f"Comentário editado: {comment_id}")
            return comment
    
    def edit_reply(self, comment_id: str, reply_id: str, user_id: str, new_content: str) -> CommentReply:
        """Edita uma resposta"""
        with self.tracing.start_span("edit_reply"):
            if comment_id not in self.comments:
                raise ValueError(f"Comentário não encontrado: {comment_id}")
            
            comment = self.comments[comment_id]
            
            # Encontrar resposta
            reply = None
            for r in comment.replies:
                if r.id == reply_id:
                    reply = r
                    break
            
            if not reply:
                raise ValueError(f"Resposta não encontrada: {reply_id}")
            
            # Verificar permissão
            if reply.user_id != user_id:
                raise PermissionError("Apenas o autor pode editar a resposta")
            
            # Atualizar conteúdo
            reply.content = new_content
            reply.edited = True
            reply.edited_at = time.time()
            
            # Atualizar thread
            if comment_id in self.threads:
                self.threads[comment_id].last_activity = time.time()
            
            logger.info(f"Resposta editada: {reply_id}")
            return reply
    
    def resolve_comment(self, comment_id: str, user_id: str) -> Comment:
        """Resolve um comentário"""
        with self.tracing.start_span("resolve_comment"):
            if comment_id not in self.comments:
                raise ValueError(f"Comentário não encontrado: {comment_id}")
            
            comment = self.comments[comment_id]
            
            # Verificar se já está resolvido
            if comment.status == CommentStatus.RESOLVED:
                raise ValueError("Comentário já está resolvido")
            
            # Marcar como resolvido
            comment.status = CommentStatus.RESOLVED
            comment.resolved_by = user_id
            comment.resolved_at = time.time()
            
            # Atualizar thread
            if comment_id in self.threads:
                thread = self.threads[comment_id]
                thread.is_resolved = True
                thread.last_activity = time.time()
            
            # Métricas
            self.metrics.increment_counter("comments_resolved_total")
            self.metrics.increment_gauge("active_comments", -1)
            
            logger.info(f"Comentário resolvido: {comment_id}")
            return comment
    
    def archive_comment(self, comment_id: str, user_id: str) -> Comment:
        """Arquiva um comentário"""
        with self.tracing.start_span("archive_comment"):
            if comment_id not in self.comments:
                raise ValueError(f"Comentário não encontrado: {comment_id}")
            
            comment = self.comments[comment_id]
            comment.status = CommentStatus.ARCHIVED
            
            logger.info(f"Comentário arquivado: {comment_id}")
            return comment
    
    def delete_comment(self, comment_id: str, user_id: str) -> bool:
        """Deleta um comentário"""
        with self.tracing.start_span("delete_comment"):
            if comment_id not in self.comments:
                return False
            
            comment = self.comments[comment_id]
            
            # Verificar permissão
            if comment.user_id != user_id:
                raise PermissionError("Apenas o autor pode deletar o comentário")
            
            # Remover de todos os índices
            if comment.document_id in self.document_comments:
                self.document_comments[comment.document_id] = [
                    cid for cid in self.document_comments[comment.document_id] 
                    if cid != comment_id
                ]
            
            if comment.user_id in self.user_comments:
                self.user_comments[comment.user_id] = [
                    cid for cid in self.user_comments[comment.user_id] 
                    if cid != comment_id
                ]
            
            # Remover comentário e thread
            del self.comments[comment_id]
            if comment_id in self.threads:
                del self.threads[comment_id]
            
            # Métricas
            if comment.status == CommentStatus.ACTIVE:
                self.metrics.increment_gauge("active_comments", -1)
            
            logger.info(f"Comentário deletado: {comment_id}")
            return True
    
    def get_comments_by_document(self, document_id: str, status: Optional[CommentStatus] = None) -> List[Comment]:
        """Retorna comentários de um documento"""
        with self.tracing.start_span("get_comments_by_document"):
            if document_id not in self.document_comments:
                return []
            
            comment_ids = self.document_comments[document_id]
            comments = [self.comments[cid] for cid in comment_ids if cid in self.comments]
            
            if status:
                comments = [c for c in comments if c.status == status]
            
            # Ordenar por timestamp
            comments.sort(key=lambda c: c.timestamp)
            return comments
    
    def get_comments_by_user(self, user_id: str, status: Optional[CommentStatus] = None) -> List[Comment]:
        """Retorna comentários de um usuário"""
        with self.tracing.start_span("get_comments_by_user"):
            if user_id not in self.user_comments:
                return []
            
            comment_ids = self.user_comments[user_id]
            comments = [self.comments[cid] for cid in comment_ids if cid in self.comments]
            
            if status:
                comments = [c for c in comments if c.status == status]
            
            # Ordenar por timestamp
            comments.sort(key=lambda c: c.timestamp, reverse=True)
            return comments
    
    def get_comment_thread(self, comment_id: str) -> Optional[CommentThread]:
        """Retorna a thread de um comentário"""
        return self.threads.get(comment_id)
    
    def search_comments(self, query: str, document_id: Optional[str] = None, 
                       user_id: Optional[str] = None, comment_type: Optional[CommentType] = None) -> List[Comment]:
        """Busca comentários por texto"""
        with self.tracing.start_span("search_comments"):
            results = []
            query_lower = query.lower()
            
            for comment in self.comments.values():
                # Filtrar por documento
                if document_id and comment.document_id != document_id:
                    continue
                
                # Filtrar por usuário
                if user_id and comment.user_id != user_id:
                    continue
                
                # Filtrar por tipo
                if comment_type and comment.comment_type != comment_type:
                    continue
                
                # Buscar no conteúdo
                if query_lower in comment.content.lower():
                    results.append(comment)
                    continue
                
                # Buscar nas respostas
                for reply in comment.replies:
                    if query_lower in reply.content.lower():
                        results.append(comment)
                        break
                
                # Buscar nas tags
                for tag in comment.tags:
                    if query_lower in tag.lower():
                        results.append(comment)
                        break
            
            # Ordenar por relevância (timestamp mais recente primeiro)
            results.sort(key=lambda c: c.timestamp, reverse=True)
            return results
    
    def get_mentions(self, user_id: str) -> List[Comment]:
        """Retorna comentários que mencionam um usuário"""
        with self.tracing.start_span("get_mentions"):
            mentions = []
            
            for comment in self.comments.values():
                if user_id in comment.mentions:
                    mentions.append(comment)
            
            # Ordenar por timestamp
            mentions.sort(key=lambda c: c.timestamp, reverse=True)
            return mentions
    
    def get_statistics(self, document_id: Optional[str] = None) -> Dict[str, Any]:
        """Retorna estatísticas dos comentários"""
        with self.tracing.start_span("get_comment_statistics"):
            stats = {
                "total_comments": 0,
                "active_comments": 0,
                "resolved_comments": 0,
                "archived_comments": 0,
                "total_replies": 0,
                "comments_by_type": {},
                "comments_by_user": {},
                "avg_replies_per_comment": 0
            }
            
            for comment in self.comments.values():
                # Filtrar por documento se especificado
                if document_id and comment.document_id != document_id:
                    continue
                
                stats["total_comments"] += 1
                
                # Contar por status
                if comment.status == CommentStatus.ACTIVE:
                    stats["active_comments"] += 1
                elif comment.status == CommentStatus.RESOLVED:
                    stats["resolved_comments"] += 1
                elif comment.status == CommentStatus.ARCHIVED:
                    stats["archived_comments"] += 1
                
                # Contar respostas
                stats["total_replies"] += len(comment.replies)
                
                # Contar por tipo
                comment_type = comment.comment_type.value
                if comment_type not in stats["comments_by_type"]:
                    stats["comments_by_type"][comment_type] = 0
                stats["comments_by_type"][comment_type] += 1
                
                # Contar por usuário
                if comment.user_id not in stats["comments_by_user"]:
                    stats["comments_by_user"][comment.user_id] = 0
                stats["comments_by_user"][comment.user_id] += 1
            
            # Calcular média de respostas
            if stats["total_comments"] > 0:
                stats["avg_replies_per_comment"] = stats["total_replies"] / stats["total_comments"]
            
            return stats
    
    def export_comments(self, document_id: str, format: str = "json") -> str:
        """Exporta comentários de um documento"""
        with self.tracing.start_span("export_comments"):
            comments = self.get_comments_by_document(document_id)
            
            if format.lower() == "json":
                return json.dumps([comment.to_dict() for comment in comments], indent=2)
            elif format.lower() == "csv":
                # Implementar exportação CSV se necessário
                raise NotImplementedError("Exportação CSV não implementada")
            else:
                raise ValueError(f"Formato não suportado: {format}")
    
    def import_comments(self, document_id: str, comments_data: List[Dict[str, Any]]) -> List[Comment]:
        """Importa comentários para um documento"""
        with self.tracing.start_span("import_comments"):
            imported_comments = []
            
            for comment_data in comments_data:
                try:
                    # Criar comentário
                    comment = Comment(
                        document_id=document_id,
                        user_id=comment_data.get("user_id", ""),
                        content=comment_data.get("content", ""),
                        position=comment_data.get("position", 0),
                        comment_type=CommentType(comment_data.get("comment_type", "general")),
                        status=CommentStatus(comment_data.get("status", "active")),
                        timestamp=comment_data.get("timestamp", time.time())
                    )
                    
                    # Adicionar ao sistema
                    self.comments[comment.id] = comment
                    
                    # Indexar
                    if document_id not in self.document_comments:
                        self.document_comments[document_id] = []
                    self.document_comments[document_id].append(comment.id)
                    
                    if comment.user_id not in self.user_comments:
                        self.user_comments[comment.user_id] = []
                    self.user_comments[comment.user_id].append(comment.id)
                    
                    imported_comments.append(comment)
                    
                except Exception as e:
                    logger.error(f"Erro ao importar comentário: {e}")
                    continue
            
            logger.info(f"Importados {len(imported_comments)} comentários para {document_id}")
            return imported_comments


# Função de conveniência para criar sistema de comentários
def create_comment_system() -> CommentSystem:
    """Cria uma instância do sistema de comentários"""
    return CommentSystem() 
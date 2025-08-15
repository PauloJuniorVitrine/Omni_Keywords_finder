from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de Comentários Colaborativos
=========================================================

Tracing ID: TEST_COLLAB_COMMENT_001
Data: 2024-12-19
Versão: 1.0
"""

import pytest
import time
from unittest.mock import MagicMock

from infrastructure.collaboration.comment_system import (
    CommentSystem, Comment, CommentReply, CommentStatus, CommentType
)


class TestCommentSystem:
    """Testes para CommentSystem"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.comment_system = CommentSystem()
    
    def test_initialization(self):
        """Testa inicialização do sistema de comentários"""
        assert self.comment_system.comments == {}
        assert self.comment_system.threads == {}
        assert self.comment_system.document_comments == {}
        assert self.comment_system.user_comments == {}
    
    def test_create_comment(self):
        """Testa criação de comentário"""
        comment = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Este é um comentário de teste",
            position=10,
            comment_type=CommentType.GENERAL
        )
        
        assert comment.document_id == "doc1"
        assert comment.user_id == "user1"
        assert comment.content == "Este é um comentário de teste"
        assert comment.position == 10
        assert comment.comment_type == CommentType.GENERAL
        assert comment.status == CommentStatus.ACTIVE
        assert comment.id in self.comment_system.comments
        assert comment.id in self.comment_system.document_comments["doc1"]
        assert comment.id in self.comment_system.user_comments["user1"]
        assert comment.id in self.comment_system.threads
    
    def test_create_comment_with_mentions_and_tags(self):
        """Testa criação de comentário com menções e tags"""
        comment = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="@user2 veja isso #bug #urgente",
            mentions={"user2"},
            tags={"bug", "urgente"}
        )
        
        assert "user2" in comment.mentions
        assert "bug" in comment.tags
        assert "urgente" in comment.tags
    
    def test_add_reply(self):
        """Testa adição de resposta"""
        # Criar comentário primeiro
        comment = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Comentário original"
        )
        
        # Adicionar resposta
        reply = self.comment_system.add_reply(
            comment_id=comment.id,
            user_id="user2",
            content="Esta é uma resposta"
        )
        
        assert reply.user_id == "user2"
        assert reply.content == "Esta é uma resposta"
        assert reply.id in [r.id for r in comment.replies]
        assert "user2" in self.comment_system.threads[comment.id].participants
    
    def test_add_reply_to_nonexistent_comment(self):
        """Testa adição de resposta a comentário inexistente"""
        with pytest.raises(ValueError, match="Comentário não encontrado"):
            self.comment_system.add_reply(
                comment_id="nonexistent",
                user_id="user1",
                content="Resposta"
            )
    
    def test_edit_comment(self):
        """Testa edição de comentário"""
        comment = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Conteúdo original"
        )
        
        edited_comment = self.comment_system.edit_comment(
            comment_id=comment.id,
            user_id="user1",
            new_content="Conteúdo editado"
        )
        
        assert edited_comment.content == "Conteúdo editado"
        assert edited_comment.edited is True
        assert edited_comment.edited_at > 0
    
    def test_edit_comment_wrong_user(self):
        """Testa edição de comentário por usuário incorreto"""
        comment = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Conteúdo original"
        )
        
        with pytest.raises(PermissionError, match="Apenas o autor pode editar o comentário"):
            self.comment_system.edit_comment(
                comment_id=comment.id,
                user_id="user2",
                new_content="Conteúdo editado"
            )
    
    def test_edit_reply(self):
        """Testa edição de resposta"""
        comment = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Comentário"
        )
        
        reply = self.comment_system.add_reply(
            comment_id=comment.id,
            user_id="user2",
            content="Resposta original"
        )
        
        edited_reply = self.comment_system.edit_reply(
            comment_id=comment.id,
            reply_id=reply.id,
            user_id="user2",
            new_content="Resposta editada"
        )
        
        assert edited_reply.content == "Resposta editada"
        assert edited_reply.edited is True
        assert edited_reply.edited_at > 0
    
    def test_resolve_comment(self):
        """Testa resolução de comentário"""
        comment = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Comentário para resolver"
        )
        
        resolved_comment = self.comment_system.resolve_comment(
            comment_id=comment.id,
            user_id="user2"
        )
        
        assert resolved_comment.status == CommentStatus.RESOLVED
        assert resolved_comment.resolved_by == "user2"
        assert resolved_comment.resolved_at > 0
        assert self.comment_system.threads[comment.id].is_resolved is True
    
    def test_resolve_already_resolved_comment(self):
        """Testa resolução de comentário já resolvido"""
        comment = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Comentário"
        )
        
        self.comment_system.resolve_comment(comment.id, "user2")
        
        with pytest.raises(ValueError, match="Comentário já está resolvido"):
            self.comment_system.resolve_comment(comment.id, "user3")
    
    def test_archive_comment(self):
        """Testa arquivamento de comentário"""
        comment = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Comentário para arquivar"
        )
        
        archived_comment = self.comment_system.archive_comment(
            comment_id=comment.id,
            user_id="user1"
        )
        
        assert archived_comment.status == CommentStatus.ARCHIVED
    
    def test_delete_comment(self):
        """Testa deleção de comentário"""
        comment = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Comentário para deletar"
        )
        
        result = self.comment_system.delete_comment(
            comment_id=comment.id,
            user_id="user1"
        )
        
        assert result is True
        assert comment.id not in self.comment_system.comments
        assert comment.id not in self.comment_system.document_comments["doc1"]
        assert comment.id not in self.comment_system.user_comments["user1"]
        assert comment.id not in self.comment_system.threads
    
    def test_delete_comment_wrong_user(self):
        """Testa deleção de comentário por usuário incorreto"""
        comment = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Comentário"
        )
        
        with pytest.raises(PermissionError, match="Apenas o autor pode deletar o comentário"):
            self.comment_system.delete_comment(
                comment_id=comment.id,
                user_id="user2"
            )
    
    def test_get_comments_by_document(self):
        """Testa obtenção de comentários por documento"""
        # Criar comentários em documentos diferentes
        comment1 = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Comentário 1"
        )
        
        comment2 = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user2",
            content="Comentário 2"
        )
        
        comment3 = self.comment_system.create_comment(
            document_id="doc2",
            user_id="user1",
            content="Comentário 3"
        )
        
        # Obter comentários do doc1
        doc1_comments = self.comment_system.get_comments_by_document("doc1")
        assert len(doc1_comments) == 2
        assert comment1 in doc1_comments
        assert comment2 in doc1_comments
        assert comment3 not in doc1_comments
        
        # Obter comentários ativos
        active_comments = self.comment_system.get_comments_by_document("doc1", CommentStatus.ACTIVE)
        assert len(active_comments) == 2
        
        # Resolver um comentário
        self.comment_system.resolve_comment(comment1.id, "user3")
        
        # Verificar filtro por status
        active_comments = self.comment_system.get_comments_by_document("doc1", CommentStatus.ACTIVE)
        assert len(active_comments) == 1
        assert comment2 in active_comments
    
    def test_get_comments_by_user(self):
        """Testa obtenção de comentários por usuário"""
        comment1 = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Comentário 1"
        )
        
        comment2 = self.comment_system.create_comment(
            document_id="doc2",
            user_id="user1",
            content="Comentário 2"
        )
        
        comment3 = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user2",
            content="Comentário 3"
        )
        
        user1_comments = self.comment_system.get_comments_by_user("user1")
        assert len(user1_comments) == 2
        assert comment1 in user1_comments
        assert comment2 in user1_comments
        assert comment3 not in user1_comments
    
    def test_get_comment_thread(self):
        """Testa obtenção de thread de comentário"""
        comment = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Comentário"
        )
        
        thread = self.comment_system.get_comment_thread(comment.id)
        assert thread is not None
        assert thread.main_comment == comment
        assert "user1" in thread.participants
    
    def test_search_comments(self):
        """Testa busca de comentários"""
        comment1 = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Este é um comentário sobre bugs"
        )
        
        comment2 = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user2",
            content="Este é sobre features"
        )
        
        # Buscar por "bug"
        bug_comments = self.comment_system.search_comments("bug")
        assert len(bug_comments) == 1
        assert comment1 in bug_comments
        
        # Buscar por "feature"
        feature_comments = self.comment_system.search_comments("feature")
        assert len(feature_comments) == 1
        assert comment2 in feature_comments
        
        # Buscar com filtros
        user1_bug_comments = self.comment_system.search_comments(
            "bug", user_id="user1"
        )
        assert len(user1_bug_comments) == 1
        assert comment1 in user1_bug_comments
    
    def test_get_mentions(self):
        """Testa obtenção de menções"""
        comment = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Comentário",
            mentions={"user2", "user3"}
        )
        
        mentions = self.comment_system.get_mentions("user2")
        assert len(mentions) == 1
        assert comment in mentions
        
        mentions = self.comment_system.get_mentions("user4")
        assert len(mentions) == 0
    
    def test_get_statistics(self):
        """Testa obtenção de estatísticas"""
        # Criar comentários de diferentes tipos
        comment1 = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Bug report",
            comment_type=CommentType.BUG
        )
        
        comment2 = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user2",
            content="Feature request",
            comment_type=CommentType.FEATURE
        )
        
        comment3 = self.comment_system.create_comment(
            document_id="doc2",
            user_id="user1",
            content="Question",
            comment_type=CommentType.QUESTION
        )
        
        # Adicionar respostas
        self.comment_system.add_reply(comment1.id, "user3", "Resposta 1")
        self.comment_system.add_reply(comment1.id, "user4", "Resposta 2")
        
        # Resolver um comentário
        self.comment_system.resolve_comment(comment2.id, "user1")
        
        # Obter estatísticas
        stats = self.comment_system.get_statistics()
        
        assert stats["total_comments"] == 3
        assert stats["active_comments"] == 2
        assert stats["resolved_comments"] == 1
        assert stats["total_replies"] == 2
        assert stats["comments_by_type"]["bug"] == 1
        assert stats["comments_by_type"]["feature"] == 1
        assert stats["comments_by_type"]["question"] == 1
        assert stats["comments_by_user"]["user1"] == 2
        assert stats["comments_by_user"]["user2"] == 1
        assert stats["avg_replies_per_comment"] == 2/3
        
        # Estatísticas por documento
        doc1_stats = self.comment_system.get_statistics("doc1")
        assert doc1_stats["total_comments"] == 2
        assert doc1_stats["total_replies"] == 2
    
    def test_export_import_comments(self):
        """Testa exportação e importação de comentários"""
        # Criar comentários
        comment1 = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user1",
            content="Comentário 1"
        )
        
        comment2 = self.comment_system.create_comment(
            document_id="doc1",
            user_id="user2",
            content="Comentário 2"
        )
        
        # Adicionar respostas
        self.comment_system.add_reply(comment1.id, "user3", "Resposta")
        
        # Exportar
        exported = self.comment_system.export_comments("doc1")
        exported_data = json.loads(exported)
        
        assert len(exported_data) == 2
        
        # Criar novo sistema e importar
        new_system = CommentSystem()
        imported = new_system.import_comments("doc2", exported_data)
        
        assert len(imported) == 2
        assert len(new_system.get_comments_by_document("doc2")) == 2


class TestComment:
    """Testes para Comment"""
    
    def test_comment_creation(self):
        """Testa criação de comentário"""
        comment = Comment(
            document_id="doc1",
            user_id="user1",
            content="Teste",
            position=10,
            comment_type=CommentType.BUG
        )
        
        assert comment.document_id == "doc1"
        assert comment.user_id == "user1"
        assert comment.content == "Teste"
        assert comment.position == 10
        assert comment.comment_type == CommentType.BUG
        assert comment.status == CommentStatus.ACTIVE
        assert comment.id is not None
        assert comment.timestamp > 0
    
    def test_comment_default_values(self):
        """Testa valores padrão do comentário"""
        comment = Comment()
        
        assert comment.content == ""
        assert comment.position == 0
        assert comment.comment_type == CommentType.GENERAL
        assert comment.status == CommentStatus.ACTIVE
        assert comment.replies == []
        assert comment.mentions == set()
        assert comment.tags == set()
        assert comment.metadata == {}


class TestCommentReply:
    """Testes para CommentReply"""
    
    def test_reply_creation(self):
        """Testa criação de resposta"""
        reply = CommentReply(
            user_id="user1",
            content="Resposta de teste"
        )
        
        assert reply.user_id == "user1"
        assert reply.content == "Resposta de teste"
        assert reply.edited is False
        assert reply.edited_at is None
        assert reply.id is not None
        assert reply.timestamp > 0
    
    def test_reply_default_values(self):
        """Testa valores padrão da resposta"""
        reply = CommentReply()
        
        assert reply.user_id == ""
        assert reply.content == ""
        assert reply.edited is False
        assert reply.edited_at is None


class TestPerformance:
    """Testes de performance"""
    
    def test_create_many_comments_performance(self):
        """Testa performance de criação de muitos comentários"""
        comment_system = CommentSystem()
        
        start_time = time.time()
        
        for index in range(1000):
            comment_system.create_comment(
                document_id=f"doc{index % 10}",
                user_id=f"user{index % 50}",
                content=f"Comentário {index}"
            )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Deve ser rápido (< 1 segundo para 1000 comentários)
        assert execution_time < 1.0
        assert len(comment_system.comments) == 1000
    
    def test_search_performance(self):
        """Testa performance de busca"""
        comment_system = CommentSystem()
        
        # Criar comentários
        for index in range(100):
            comment_system.create_comment(
                document_id="doc1",
                user_id=f"user{index % 10}",
                content=f"Comentário {index} com palavra teste"
            )
        
        start_time = time.time()
        
        # Realizar busca
        results = comment_system.search_comments("teste")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Deve ser rápido (< 0.1 segundo)
        assert execution_time < 0.1
        assert len(results) == 100
    
    def test_statistics_performance(self):
        """Testa performance do cálculo de estatísticas"""
        comment_system = CommentSystem()
        
        # Criar comentários
        for index in range(500):
            comment_system.create_comment(
                document_id=f"doc{index % 5}",
                user_id=f"user{index % 20}",
                content=f"Comentário {index}"
            )
        
        start_time = time.time()
        
        # Calcular estatísticas
        stats = comment_system.get_statistics()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Deve ser rápido (< 0.1 segundo)
        assert execution_time < 0.1
        assert stats["total_comments"] == 500


if __name__ == "__main__":
    pytest.main([__file__]) 
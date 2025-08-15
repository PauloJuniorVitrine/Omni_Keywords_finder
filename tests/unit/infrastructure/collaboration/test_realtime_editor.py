from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de Edição Colaborativa em Tempo Real
==================================================================

Tracing ID: TEST_COLLAB_EDITOR_001
Data: 2024-12-19
Versão: 1.0
"""

import asyncio
import json
import pytest
import time
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from infrastructure.collaboration.realtime_editor import (
    RealtimeEditor, OperationalTransform, Operation, OperationType,
    Document, CursorPosition, DocumentState
)


class TestOperationalTransform:
    """Testes para Operational Transform"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.ot = OperationalTransform()
    
    def test_transform_insert_insert_same_position(self):
        """Testa transformação de duas inserções na mesma posição"""
        op1 = Operation(
            id="op1",
            type=OperationType.INSERT,
            position=5,
            content="abc",
            user_id="user1"
        )
        
        op2 = Operation(
            id="op2",
            type=OperationType.INSERT,
            position=5,
            content="xyz",
            user_id="user2"
        )
        
        result1, result2 = self.ot.transform_insert_insert(op1, op2)
        
        # op1 deve permanecer na posição 5
        assert result1.position == 5
        assert result1.content == "abc"
        
        # op2 deve ser movida para posição 8 (5 + len("abc"))
        assert result2.position == 8
        assert result2.content == "xyz"
    
    def test_transform_insert_insert_different_positions(self):
        """Testa transformação de duas inserções em posições diferentes"""
        op1 = Operation(
            id="op1",
            type=OperationType.INSERT,
            position=3,
            content="abc",
            user_id="user1"
        )
        
        op2 = Operation(
            id="op2",
            type=OperationType.INSERT,
            position=7,
            content="xyz",
            user_id="user2"
        )
        
        result1, result2 = self.ot.transform_insert_insert(op1, op2)
        
        # op1 deve permanecer na posição 3
        assert result1.position == 3
        assert result1.content == "abc"
        
        # op2 deve ser movida para posição 10 (7 + len("abc"))
        assert result2.position == 10
        assert result2.content == "xyz"
    
    def test_transform_insert_delete(self):
        """Testa transformação de inserção vs deleção"""
        insert_op = Operation(
            id="insert",
            type=OperationType.INSERT,
            position=5,
            content="abc",
            user_id="user1"
        )
        
        delete_op = Operation(
            id="delete",
            type=OperationType.DELETE,
            position=3,
            content="xy",
            user_id="user2"
        )
        
        result_insert, result_delete = self.ot.transform_insert_delete(insert_op, delete_op)
        
        # Inserção deve permanecer na posição 5
        assert result_insert.position == 5
        assert result_insert.content == "abc"
        
        # Deleção deve ser movida para posição 8 (3 + len("abc"))
        assert result_delete.position == 8
        assert result_delete.content == "xy"
    
    def test_transform_delete_delete(self):
        """Testa transformação de duas deleções"""
        op1 = Operation(
            id="delete1",
            type=OperationType.DELETE,
            position=5,
            content="abc",
            user_id="user1"
        )
        
        op2 = Operation(
            id="delete2",
            type=OperationType.DELETE,
            position=10,
            content="xyz",
            user_id="user2"
        )
        
        result1, result2 = self.ot.transform_delete_delete(op1, op2)
        
        # Ambas devem permanecer inalteradas (implementação simplificada)
        assert result1.position == 5
        assert result1.content == "abc"
        assert result2.position == 10
        assert result2.content == "xyz"


class TestRealtimeEditor:
    """Testes para RealtimeEditor"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.editor = RealtimeEditor()
    
    def test_initialization(self):
        """Testa inicialização do editor"""
        assert self.editor.documents == {}
        assert self.editor.sessions == {}
        assert self.editor.user_sessions == {}
        assert isinstance(self.editor.ot, OperationalTransform)
    
    def test_get_document_stats_empty(self):
        """Testa estatísticas de documento vazio"""
        stats = self.editor.get_document_stats("nonexistent")
        assert stats == {}
    
    def test_get_system_stats_empty(self):
        """Testa estatísticas do sistema vazio"""
        stats = self.editor.get_system_stats()
        assert stats["active_sessions"] == 0
        assert stats["active_users"] == 0
        assert stats["documents_count"] == 0
        assert stats["total_operations"] == 0
    
    def test_get_system_stats_with_data(self):
        """Testa estatísticas do sistema com dados"""
        # Criar documento de teste
        document = Document(
            id="test_doc",
            content="Hello World",
            created_by="user1"
        )
        document.collaborators.add("user1")
        document.operations.append(Operation(
            type=OperationType.INSERT,
            content="Hello",
            user_id="user1"
        ))
        
        self.editor.documents["test_doc"] = document
        self.editor.sessions["session1"] = MagicMock()
        self.editor.user_sessions["user1"] = "session1"
        
        stats = self.editor.get_system_stats()
        assert stats["active_sessions"] == 1
        assert stats["active_users"] == 1
        assert stats["documents_count"] == 1
        assert stats["total_operations"] == 1
    
    def test_get_document_stats_with_data(self):
        """Testa estatísticas de documento com dados"""
        document = Document(
            id="test_doc",
            content="Hello World",
            created_by="user1"
        )
        document.collaborators.add("user1")
        document.operations.append(Operation(
            type=OperationType.INSERT,
            content="Hello",
            user_id="user1"
        ))
        
        self.editor.documents["test_doc"] = document
        
        stats = self.editor.get_document_stats("test_doc")
        assert stats["id"] == "test_doc"
        assert stats["content_length"] == 11
        assert stats["version"] == 0
        assert stats["collaborators_count"] == 1
        assert stats["operations_count"] == 1
        assert stats["created_by"] == "user1"


class TestDocument:
    """Testes para Document"""
    
    def test_document_creation(self):
        """Testa criação de documento"""
        document = Document(
            id="test_doc",
            content="Initial content",
            created_by="user1"
        )
        
        assert document.id == "test_doc"
        assert document.content == "Initial content"
        assert document.created_by == "user1"
        assert document.version == 0
        assert document.state == DocumentState.SYNCED
        assert document.collaborators == set()
        assert document.operations == []
        assert document.cursors == {}
    
    def test_document_add_collaborator(self):
        """Testa adição de colaborador"""
        document = Document(id="test_doc")
        document.collaborators.add("user1")
        
        assert "user1" in document.collaborators
        assert len(document.collaborators) == 1
    
    def test_document_add_operation(self):
        """Testa adição de operação"""
        document = Document(id="test_doc")
        operation = Operation(
            type=OperationType.INSERT,
            content="Hello",
            user_id="user1"
        )
        
        document.operations.append(operation)
        document.version += 1
        
        assert len(document.operations) == 1
        assert document.operations[0] == operation
        assert document.version == 1
    
    def test_document_add_cursor(self):
        """Testa adição de cursor"""
        document = Document(id="test_doc")
        cursor = CursorPosition(
            user_id="user1",
            position=5,
            color="#FF0000",
            name="User 1"
        )
        
        document.cursors["user1"] = cursor
        
        assert "user1" in document.cursors
        assert document.cursors["user1"] == cursor


class TestCursorPosition:
    """Testes para CursorPosition"""
    
    def test_cursor_creation(self):
        """Testa criação de cursor"""
        cursor = CursorPosition(
            user_id="user1",
            position=10,
            color="#007ACC",
            name="Test User"
        )
        
        assert cursor.user_id == "user1"
        assert cursor.position == 10
        assert cursor.color == "#007ACC"
        assert cursor.name == "Test User"
        assert cursor.timestamp > 0
    
    def test_cursor_default_values(self):
        """Testa valores padrão do cursor"""
        cursor = CursorPosition(user_id="user1", position=5)
        
        assert cursor.color == "#007ACC"
        assert cursor.name == ""
        assert cursor.timestamp > 0


class TestOperation:
    """Testes para Operation"""
    
    def test_operation_creation(self):
        """Testa criação de operação"""
        operation = Operation(
            type=OperationType.INSERT,
            position=5,
            content="Hello",
            user_id="user1",
            session_id="session1",
            version=1
        )
        
        assert operation.type == OperationType.INSERT
        assert operation.position == 5
        assert operation.content == "Hello"
        assert operation.user_id == "user1"
        assert operation.session_id == "session1"
        assert operation.version == 1
        assert operation.timestamp > 0
        assert operation.id is not None
    
    def test_operation_default_values(self):
        """Testa valores padrão da operação"""
        operation = Operation()
        
        assert operation.type == OperationType.INSERT
        assert operation.position == 0
        assert operation.content == ""
        assert operation.user_id == ""
        assert operation.session_id == ""
        assert operation.version == 0
        assert operation.timestamp > 0
        assert operation.id is not None
        assert operation.metadata == {}


class TestIntegration:
    """Testes de integração"""
    
    @pytest.mark.asyncio
    async def test_editor_operation_flow(self):
        """Testa fluxo completo de operações"""
        editor = RealtimeEditor()
        
        # Simular entrada de usuário
        document_id = "test_doc"
        user_id = "user1"
        session_id = "session1"
        
        # Criar documento
        document = Document(
            id=document_id,
            created_by=user_id
        )
        editor.documents[document_id] = document
        editor.sessions[session_id] = AsyncMock()
        editor.user_sessions[user_id] = session_id
        
        # Simular operação de inserção
        operation_data = {
            "document_id": document_id,
            "operation": {
                "type": "insert",
                "position": 0,
                "content": "Hello",
                "user_id": user_id
            }
        }
        
        # Processar operação
        await editor.handle_operation(session_id, operation_data)
        
        # Verificar resultado
        assert document.content == "Hello"
        assert document.version == 1
        assert len(document.operations) == 1
        assert document.operations[0].content == "Hello"
        assert document.operations[0].user_id == user_id
    
    @pytest.mark.asyncio
    async def test_cursor_movement(self):
        """Testa movimento de cursor"""
        editor = RealtimeEditor()
        
        # Criar documento
        document = Document(id="test_doc")
        editor.documents["test_doc"] = document
        editor.sessions["session1"] = AsyncMock()
        
        # Simular movimento de cursor
        cursor_data = {
            "document_id": "test_doc",
            "user_id": "user1",
            "position": 5,
            "color": "#FF0000",
            "name": "User 1"
        }
        
        await editor.handle_cursor_move("session1", cursor_data)
        
        # Verificar cursor
        assert "user1" in document.cursors
        cursor = document.cursors["user1"]
        assert cursor.position == 5
        assert cursor.color == "#FF0000"
        assert cursor.name == "User 1"
    
    @pytest.mark.asyncio
    async def test_user_join_leave(self):
        """Testa entrada e saída de usuários"""
        editor = RealtimeEditor()
        
        # Simular entrada de usuário
        join_data = {
            "document_id": "test_doc",
            "user_id": "user1",
            "user_name": "User 1"
        }
        
        await editor.handle_join_document("session1", join_data)
        
        # Verificar que documento foi criado
        assert "test_doc" in editor.documents
        document = editor.documents["test_doc"]
        assert "user1" in document.collaborators
        assert document.created_by == "user1"
        
        # Simular saída de usuário
        leave_data = {
            "document_id": "test_doc",
            "user_id": "user1"
        }
        
        await editor.handle_leave_document("session1", leave_data)
        
        # Verificar que usuário foi removido
        assert "user1" not in document.collaborators


class TestErrorHandling:
    """Testes de tratamento de erros"""
    
    @pytest.mark.asyncio
    async def test_operation_on_nonexistent_document(self):
        """Testa operação em documento inexistente"""
        editor = RealtimeEditor()
        editor.sessions["session1"] = AsyncMock()
        
        operation_data = {
            "document_id": "nonexistent",
            "operation": {
                "type": "insert",
                "position": 0,
                "content": "Hello",
                "user_id": "user1"
            }
        }
        
        # Deve enviar erro
        await editor.handle_operation("session1", operation_data)
        
        # Verificar que erro foi enviado
        editor.sessions["session1"].send.assert_called_once()
        sent_message = json.loads(editor.sessions["session1"].send.call_args[0][0])
        assert sent_message["type"] == "error"
        assert "Documento não encontrado" in sent_message["message"]
    
    @pytest.mark.asyncio
    async def test_join_document_missing_required_fields(self):
        """Testa entrada em documento com campos obrigatórios ausentes"""
        editor = RealtimeEditor()
        editor.sessions["session1"] = AsyncMock()
        
        # Dados incompletos
        join_data = {
            "document_id": "test_doc"
            # user_id ausente
        }
        
        await editor.handle_join_document("session1", join_data)
        
        # Verificar que erro foi enviado
        editor.sessions["session1"].send.assert_called_once()
        sent_message = json.loads(editor.sessions["session1"].send.call_args[0][0])
        assert sent_message["type"] == "error"
        assert "document_id e user_id são obrigatórios" in sent_message["message"]


class TestPerformance:
    """Testes de performance"""
    
    def test_operation_transformation_performance(self):
        """Testa performance da transformação de operações"""
        ot = OperationalTransform()
        
        # Criar operações de teste
        operations = []
        for index in range(100):
            operation = Operation(
                type=OperationType.INSERT,
                position=index,
                content=f"text{index}",
                user_id=f"user{index % 5}"
            )
            operations.append(operation)
        
        # Medir tempo de transformação
        start_time = time.time()
        
        for index in range(len(operations) - 1):
            ot.transform_insert_insert(operations[index], operations[index + 1])
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Deve ser rápido (< 1 segundo para 100 operações)
        assert execution_time < 1.0
    
    def test_document_stats_performance(self):
        """Testa performance do cálculo de estatísticas"""
        editor = RealtimeEditor()
        
        # Criar documento com muitas operações
        document = Document(id="test_doc")
        for index in range(1000):
            operation = Operation(
                type=OperationType.INSERT,
                content=f"text{index}",
                user_id=f"user{index % 10}"
            )
            document.operations.append(operation)
            document.collaborators.add(f"user{index % 10}")
        
        editor.documents["test_doc"] = document
        
        # Medir tempo de cálculo de estatísticas
        start_time = time.time()
        stats = editor.get_document_stats("test_doc")
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Deve ser rápido (< 0.1 segundo)
        assert execution_time < 0.1
        assert stats["operations_count"] == 1000
        assert stats["collaborators_count"] == 10


if __name__ == "__main__":
    pytest.main([__file__]) 
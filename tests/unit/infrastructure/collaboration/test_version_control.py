from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de Versionamento
=============================================

Tracing ID: TEST_COLLAB_VERSION_001
Data: 2024-12-19
Versão: 1.0
"""

import pytest
import time
import json
from unittest.mock import MagicMock

from infrastructure.collaboration.version_control import (
    VersionControl, Version, Branch, MergeRequest, VersionType, MergeStatus
)


class TestVersionControl:
    """Testes para VersionControl"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.version_control = VersionControl()
    
    def test_initialization(self):
        """Testa inicialização do sistema de versionamento"""
        assert self.version_control.versions == {}
        assert self.version_control.branches == {}
        assert self.version_control.merge_requests == {}
        assert self.version_control.document_versions == {}
    
    def test_create_version(self):
        """Testa criação de versão"""
        version = self.version_control.create_version(
            document_id="doc1",
            content="Conteúdo inicial",
            author_id="user1",
            version_type=VersionType.MANUAL,
            message="Versão inicial"
        )
        
        assert version.document_id == "doc1"
        assert version.content == "Conteúdo inicial"
        assert version.author_id == "user1"
        assert version.version_type == VersionType.MANUAL
        assert version.message == "Versão inicial"
        assert version.version_number == 1
        assert version.branch_name == "main"
        assert version.id in self.version_control.versions
        assert version.id in self.version_control.document_versions["doc1"]
        
        # Verificar se branch foi criado
        assert "doc1" in self.version_control.branches
        assert "main" in self.version_control.branches["doc1"]
        branch = self.version_control.branches["doc1"]["main"]
        assert branch.head_version_id == version.id
        assert branch.is_default is True
    
    def test_create_multiple_versions(self):
        """Testa criação de múltiplas versões"""
        # Primeira versão
        version1 = self.version_control.create_version(
            document_id="doc1",
            content="Versão 1",
            author_id="user1"
        )
        
        # Segunda versão
        version2 = self.version_control.create_version(
            document_id="doc1",
            content="Versão 2",
            author_id="user1",
            parent_version_id=version1.id
        )
        
        assert version1.version_number == 1
        assert version2.version_number == 2
        assert version2.parent_version_id == version1.id
        
        # Verificar se head foi atualizado
        branch = self.version_control.branches["doc1"]["main"]
        assert branch.head_version_id == version2.id
    
    def test_get_version(self):
        """Testa obtenção de versão específica"""
        version = self.version_control.create_version(
            document_id="doc1",
            content="Teste",
            author_id="user1"
        )
        
        retrieved_version = self.version_control.get_version(version.id)
        assert retrieved_version == version
        
        # Versão inexistente
        assert self.version_control.get_version("nonexistent") is None
    
    def test_get_latest_version(self):
        """Testa obtenção da versão mais recente"""
        version1 = self.version_control.create_version(
            document_id="doc1",
            content="Versão 1",
            author_id="user1"
        )
        
        version2 = self.version_control.create_version(
            document_id="doc1",
            content="Versão 2",
            author_id="user1"
        )
        
        latest = self.version_control.get_latest_version("doc1")
        assert latest == version2
        
        # Branch inexistente
        assert self.version_control.get_latest_version("doc1", "nonexistent") is None
    
    def test_get_version_history(self):
        """Testa obtenção do histórico de versões"""
        version1 = self.version_control.create_version(
            document_id="doc1",
            content="Versão 1",
            author_id="user1"
        )
        
        version2 = self.version_control.create_version(
            document_id="doc1",
            content="Versão 2",
            author_id="user1"
        )
        
        version3 = self.version_control.create_version(
            document_id="doc1",
            content="Versão 3",
            author_id="user1"
        )
        
        history = self.version_control.get_version_history("doc1")
        assert len(history) == 3
        assert history[0] == version1
        assert history[1] == version2
        assert history[2] == version3
        
        # Com limite
        limited_history = self.version_control.get_version_history("doc1", limit=2)
        assert len(limited_history) == 2
        assert limited_history[0] == version2
        assert limited_history[1] == version3
    
    def test_get_branches(self):
        """Testa obtenção de branches"""
        self.version_control.create_version(
            document_id="doc1",
            content="Versão main",
            author_id="user1"
        )
        
        branches = self.version_control.get_branches("doc1")
        assert len(branches) == 1
        assert branches[0].name == "main"
        assert branches[0].is_default is True
    
    def test_create_branch(self):
        """Testa criação de branch"""
        # Criar versão inicial
        self.version_control.create_version(
            document_id="doc1",
            content="Versão main",
            author_id="user1"
        )
        
        # Criar novo branch
        branch = self.version_control.create_branch(
            document_id="doc1",
            branch_name="feature",
            source_branch="main",
            author_id="user2"
        )
        
        assert branch.name == "feature"
        assert branch.created_by == "user2"
        assert branch.is_default is False
        
        # Verificar se branch foi criado
        branches = self.version_control.get_branches("doc1")
        assert len(branches) == 2
        branch_names = [b.name for b in branches]
        assert "main" in branch_names
        assert "feature" in branch_names
    
    def test_create_branch_nonexistent_document(self):
        """Testa criação de branch em documento inexistente"""
        with pytest.raises(ValueError, match="Documento não encontrado"):
            self.version_control.create_branch(
                document_id="nonexistent",
                branch_name="feature",
                author_id="user1"
            )
    
    def test_create_branch_nonexistent_source(self):
        """Testa criação de branch com branch fonte inexistente"""
        self.version_control.create_version(
            document_id="doc1",
            content="Versão main",
            author_id="user1"
        )
        
        with pytest.raises(ValueError, match="Branch fonte não encontrado"):
            self.version_control.create_branch(
                document_id="doc1",
                branch_name="feature",
                source_branch="nonexistent",
                author_id="user1"
            )
    
    def test_create_duplicate_branch(self):
        """Testa criação de branch duplicado"""
        self.version_control.create_version(
            document_id="doc1",
            content="Versão main",
            author_id="user1"
        )
        
        self.version_control.create_branch(
            document_id="doc1",
            branch_name="feature",
            author_id="user1"
        )
        
        with pytest.raises(ValueError, match="Branch já existe"):
            self.version_control.create_branch(
                document_id="doc1",
                branch_name="feature",
                author_id="user1"
            )
    
    def test_delete_branch(self):
        """Testa deleção de branch"""
        self.version_control.create_version(
            document_id="doc1",
            content="Versão main",
            author_id="user1"
        )
        
        self.version_control.create_branch(
            document_id="doc1",
            branch_name="feature",
            author_id="user1"
        )
        
        # Deletar branch
        result = self.version_control.delete_branch("doc1", "feature")
        assert result is True
        
        branches = self.version_control.get_branches("doc1")
        assert len(branches) == 1
        assert branches[0].name == "main"
    
    def test_delete_main_branch(self):
        """Testa tentativa de deletar branch principal"""
        self.version_control.create_version(
            document_id="doc1",
            content="Versão main",
            author_id="user1"
        )
        
        with pytest.raises(ValueError, match="Não é possível deletar o branch principal"):
            self.version_control.delete_branch("doc1", "main")
    
    def test_delete_branch_with_versions(self):
        """Testa deleção de branch com versões"""
        self.version_control.create_version(
            document_id="doc1",
            content="Versão main",
            author_id="user1"
        )
        
        self.version_control.create_branch(
            document_id="doc1",
            branch_name="feature",
            author_id="user1"
        )
        
        # Adicionar versão ao branch feature
        self.version_control.create_version(
            document_id="doc1",
            content="Versão feature",
            author_id="user1",
            branch_name="feature"
        )
        
        with pytest.raises(ValueError, match="Não é possível deletar branch com versões não mescladas"):
            self.version_control.delete_branch("doc1", "feature")
    
    def test_create_merge_request(self):
        """Testa criação de merge request"""
        # Criar branches
        self.version_control.create_version(
            document_id="doc1",
            content="Versão main",
            author_id="user1"
        )
        
        self.version_control.create_branch(
            document_id="doc1",
            branch_name="feature",
            author_id="user1"
        )
        
        # Criar merge request
        merge_request = self.version_control.create_merge_request(
            document_id="doc1",
            source_branch="feature",
            target_branch="main",
            requester_id="user1",
            message="Merge feature"
        )
        
        assert merge_request.source_branch == "feature"
        assert merge_request.target_branch == "main"
        assert merge_request.requester_id == "user1"
        assert merge_request.message == "Merge feature"
        assert merge_request.status == MergeStatus.PENDING
        assert merge_request.id in self.version_control.merge_requests
    
    def test_create_merge_request_nonexistent_branches(self):
        """Testa criação de merge request com branches inexistentes"""
        with pytest.raises(ValueError, match="Documento não encontrado"):
            self.version_control.create_merge_request(
                document_id="nonexistent",
                source_branch="feature",
                target_branch="main",
                requester_id="user1"
            )
    
    def test_check_merge_conflicts(self):
        """Testa verificação de conflitos de merge"""
        # Criar branches com conteúdo diferente
        self.version_control.create_version(
            document_id="doc1",
            content="Conteúdo main",
            author_id="user1"
        )
        
        self.version_control.create_branch(
            document_id="doc1",
            branch_name="feature",
            author_id="user1"
        )
        
        # Modificar conteúdo no branch feature
        self.version_control.create_version(
            document_id="doc1",
            content="Conteúdo feature",
            author_id="user1",
            branch_name="feature"
        )
        
        # Criar merge request
        merge_request = self.version_control.create_merge_request(
            document_id="doc1",
            source_branch="feature",
            target_branch="main",
            requester_id="user1"
        )
        
        # Verificar conflitos
        conflicts = self.version_control.check_merge_conflicts(merge_request.id)
        assert len(conflicts) > 0
        assert merge_request.status == MergeStatus.CONFLICT
    
    def test_resolve_merge_conflicts(self):
        """Testa resolução de conflitos de merge"""
        # Criar branches com conflito
        self.version_control.create_version(
            document_id="doc1",
            content="Conteúdo main",
            author_id="user1"
        )
        
        self.version_control.create_branch(
            document_id="doc1",
            branch_name="feature",
            author_id="user1"
        )
        
        self.version_control.create_version(
            document_id="doc1",
            content="Conteúdo feature",
            author_id="user1",
            branch_name="feature"
        )
        
        # Criar merge request
        merge_request = self.version_control.create_merge_request(
            document_id="doc1",
            source_branch="feature",
            target_branch="main",
            requester_id="user1"
        )
        
        # Verificar conflitos
        self.version_control.check_merge_conflicts(merge_request.id)
        
        # Resolver conflitos
        resolved_version = self.version_control.resolve_merge_conflicts(
            merge_request.id,
            "Conteúdo resolvido",
            "user2"
        )
        
        assert resolved_version.content == "Conteúdo resolvido"
        assert resolved_version.version_type == VersionType.MERGE
        assert merge_request.status == MergeStatus.RESOLVED
        assert merge_request.resolved_by == "user2"
    
    def test_complete_merge(self):
        """Testa completar merge"""
        # Criar merge request
        self.version_control.create_version(
            document_id="doc1",
            content="Conteúdo main",
            author_id="user1"
        )
        
        self.version_control.create_branch(
            document_id="doc1",
            branch_name="feature",
            author_id="user1"
        )
        
        merge_request = self.version_control.create_merge_request(
            document_id="doc1",
            source_branch="feature",
            target_branch="main",
            requester_id="user1"
        )
        
        # Completar merge
        result = self.version_control.complete_merge(merge_request.id, "user1")
        assert result is True
        assert merge_request.status == MergeStatus.COMPLETED
    
    def test_get_merge_requests(self):
        """Testa obtenção de merge requests"""
        # Criar merge requests
        self.version_control.create_version(
            document_id="doc1",
            content="Conteúdo main",
            author_id="user1"
        )
        
        self.version_control.create_branch(
            document_id="doc1",
            branch_name="feature1",
            author_id="user1"
        )
        
        self.version_control.create_branch(
            document_id="doc1",
            branch_name="feature2",
            author_id="user1"
        )
        
        mr1 = self.version_control.create_merge_request(
            document_id="doc1",
            source_branch="feature1",
            target_branch="main",
            requester_id="user1"
        )
        
        mr2 = self.version_control.create_merge_request(
            document_id="doc1",
            source_branch="feature2",
            target_branch="main",
            requester_id="user2"
        )
        
        # Obter todos os merge requests
        all_mrs = self.version_control.get_merge_requests()
        assert len(all_mrs) == 2
        
        # Filtrar por status
        pending_mrs = self.version_control.get_merge_requests(status=MergeStatus.PENDING)
        assert len(pending_mrs) == 2
    
    def test_compare_versions(self):
        """Testa comparação de versões"""
        version1 = self.version_control.create_version(
            document_id="doc1",
            content="Conteúdo original",
            author_id="user1"
        )
        
        version2 = self.version_control.create_version(
            document_id="doc1",
            content="Conteúdo modificado",
            author_id="user1"
        )
        
        comparison = self.version_control.compare_versions(version1.id, version2.id)
        
        assert comparison["version_1"]["id"] == version1.id
        assert comparison["version_2"]["id"] == version2.id
        assert comparison["content_length_diff"] > 0
        assert len(comparison["diff"]) > 0
    
    def test_get_statistics(self):
        """Testa obtenção de estatísticas"""
        # Criar versões
        self.version_control.create_version(
            document_id="doc1",
            content="Versão 1",
            author_id="user1",
            version_type=VersionType.MANUAL
        )
        
        self.version_control.create_version(
            document_id="doc1",
            content="Versão 2",
            author_id="user1",
            version_type=VersionType.AUTO
        )
        
        self.version_control.create_version(
            document_id="doc2",
            content="Versão 3",
            author_id="user2",
            version_type=VersionType.MANUAL
        )
        
        # Criar branches
        self.version_control.create_branch(
            document_id="doc1",
            branch_name="feature",
            author_id="user1"
        )
        
        # Criar merge requests
        self.version_control.create_merge_request(
            document_id="doc1",
            source_branch="feature",
            target_branch="main",
            requester_id="user1"
        )
        
        # Obter estatísticas
        stats = self.version_control.get_statistics()
        
        assert stats["total_versions"] == 3
        assert stats["total_branches"] == 3  # main em doc1, main em doc2, feature em doc1
        assert stats["total_merge_requests"] == 1
        assert stats["versions_by_type"]["manual"] == 2
        assert stats["versions_by_type"]["auto"] == 1
        assert stats["branches_by_document"]["doc1"] == 2
        assert stats["branches_by_document"]["doc2"] == 1
        assert stats["merge_requests_by_status"]["pending"] == 1
    
    def test_export_version_history(self):
        """Testa exportação do histórico de versões"""
        self.version_control.create_version(
            document_id="doc1",
            content="Versão 1",
            author_id="user1"
        )
        
        self.version_control.create_version(
            document_id="doc1",
            content="Versão 2",
            author_id="user1"
        )
        
        exported = self.version_control.export_version_history("doc1")
        exported_data = json.loads(exported)
        
        assert len(exported_data) == 2
        assert exported_data[0]["content"] == "Versão 1"
        assert exported_data[1]["content"] == "Versão 2"


class TestVersion:
    """Testes para Version"""
    
    def test_version_creation(self):
        """Testa criação de versão"""
        version = Version(
            document_id="doc1",
            content="Conteúdo",
            author_id="user1",
            version_type=VersionType.MANUAL,
            message="Versão teste"
        )
        
        assert version.document_id == "doc1"
        assert version.content == "Conteúdo"
        assert version.author_id == "user1"
        assert version.version_type == VersionType.MANUAL
        assert version.message == "Versão teste"
        assert version.id is not None
        assert version.timestamp > 0
        assert version.content_hash is not None
    
    def test_version_default_values(self):
        """Testa valores padrão da versão"""
        version = Version()
        
        assert version.document_id == ""
        assert version.content == ""
        assert version.author_id == ""
        assert version.version_type == VersionType.AUTO
        assert version.message == ""
        assert version.version_number == 0
        assert version.branch_name == "main"
        assert version.metadata == {}
        assert version.operations == []


class TestBranch:
    """Testes para Branch"""
    
    def test_branch_creation(self):
        """Testa criação de branch"""
        branch = Branch(
            name="feature",
            head_version_id="version1",
            created_by="user1"
        )
        
        assert branch.name == "feature"
        assert branch.head_version_id == "version1"
        assert branch.created_by == "user1"
        assert branch.is_default is False
        assert branch.created_at > 0
        assert branch.last_modified > 0
    
    def test_branch_default_values(self):
        """Testa valores padrão do branch"""
        branch = Branch()
        
        assert branch.name == ""
        assert branch.head_version_id == ""
        assert branch.created_by == ""
        assert branch.is_default is False
        assert branch.metadata == {}


class TestMergeRequest:
    """Testes para MergeRequest"""
    
    def test_merge_request_creation(self):
        """Testa criação de merge request"""
        merge_request = MergeRequest(
            source_branch="feature",
            target_branch="main",
            requester_id="user1",
            message="Merge feature"
        )
        
        assert merge_request.source_branch == "feature"
        assert merge_request.target_branch == "main"
        assert merge_request.requester_id == "user1"
        assert merge_request.message == "Merge feature"
        assert merge_request.status == MergeStatus.PENDING
        assert merge_request.id is not None
        assert merge_request.created_at > 0
    
    def test_merge_request_default_values(self):
        """Testa valores padrão do merge request"""
        merge_request = MergeRequest()
        
        assert merge_request.source_branch == ""
        assert merge_request.target_branch == ""
        assert merge_request.requester_id == ""
        assert merge_request.status == MergeStatus.PENDING
        assert merge_request.conflicts == []
        assert merge_request.message == ""


class TestPerformance:
    """Testes de performance"""
    
    def test_create_many_versions_performance(self):
        """Testa performance de criação de muitas versões"""
        version_control = VersionControl()
        
        start_time = time.time()
        
        for index in range(1000):
            version_control.create_version(
                document_id=f"doc{index % 10}",
                content=f"Versão {index}",
                author_id=f"user{index % 50}"
            )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Deve ser rápido (< 1 segundo para 1000 versões)
        assert execution_time < 1.0
        assert len(version_control.versions) == 1000
    
    def test_version_history_performance(self):
        """Testa performance do histórico de versões"""
        version_control = VersionControl()
        
        # Criar versões
        for index in range(100):
            version_control.create_version(
                document_id="doc1",
                content=f"Versão {index}",
                author_id="user1"
            )
        
        start_time = time.time()
        
        # Obter histórico
        history = version_control.get_version_history("doc1")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Deve ser rápido (< 0.1 segundo)
        assert execution_time < 0.1
        assert len(history) == 100
    
    def test_statistics_performance(self):
        """Testa performance do cálculo de estatísticas"""
        version_control = VersionControl()
        
        # Criar versões e branches
        for index in range(100):
            version_control.create_version(
                document_id=f"doc{index % 5}",
                content=f"Versão {index}",
                author_id=f"user{index % 20}"
            )
        
        for index in range(10):
            version_control.create_branch(
                document_id="doc1",
                branch_name=f"feature{index}",
                author_id="user1"
            )
        
        start_time = time.time()
        
        # Calcular estatísticas
        stats = version_control.get_statistics()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Deve ser rápido (< 0.1 segundo)
        assert execution_time < 0.1
        assert stats["total_versions"] == 100


if __name__ == "__main__":
    pytest.main([__file__]) 
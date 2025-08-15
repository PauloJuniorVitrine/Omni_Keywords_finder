"""
Sistema de Versionamento para Documentos Colaborativos
======================================================

Este módulo implementa um sistema de versionamento para documentos colaborativos
com suporte a branches, merges e histórico completo.

Tracing ID: COLLAB_VERSION_001
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
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses_json import dataclass_json
import hashlib

from infrastructure.observability.telemetry import TelemetryManager
from infrastructure.observability.tracing import TracingManager
from infrastructure.observability.metrics import MetricsManager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VersionType(Enum):
    """Tipos de versão"""
    AUTO = "auto"
    MANUAL = "manual"
    MERGE = "merge"
    BRANCH = "branch"


class MergeStatus(Enum):
    """Status de merge"""
    PENDING = "pending"
    CONFLICT = "conflict"
    RESOLVED = "resolved"
    COMPLETED = "completed"


@dataclass_json
@dataclass
class Version:
    """Representa uma versão do documento"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = ""
    version_number: int = 0
    content: str = ""
    content_hash: str = ""
    author_id: str = ""
    timestamp: float = field(default_factory=time.time)
    version_type: VersionType = VersionType.AUTO
    message: str = ""
    parent_version_id: Optional[str] = None
    branch_name: str = "main"
    metadata: Dict[str, Any] = field(default_factory=dict)
    operations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass_json
@dataclass
class Branch:
    """Representa um branch do documento"""
    name: str = ""
    head_version_id: str = ""
    created_by: str = ""
    created_at: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)
    is_default: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass_json
@dataclass
class MergeRequest:
    """Representa uma solicitação de merge"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_branch: str = ""
    target_branch: str = ""
    source_version_id: str = ""
    target_version_id: str = ""
    requester_id: str = ""
    status: MergeStatus = MergeStatus.PENDING
    created_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None
    resolved_by: Optional[str] = None
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    message: str = ""


class VersionControl:
    """Sistema principal de versionamento"""
    
    def __init__(self):
        self.versions: Dict[str, Version] = {}
        self.branches: Dict[str, Dict[str, Branch]] = {}  # document_id -> {branch_name -> Branch}
        self.merge_requests: Dict[str, MergeRequest] = {}
        self.document_versions: Dict[str, List[str]] = {}  # document_id -> version_ids
        
        # Observabilidade
        self.telemetry = TelemetryManager()
        self.tracing = TracingManager()
        self.metrics = MetricsManager()
        
        # Métricas
        self.metrics.register_counter("versions_created_total", "Total de versões criadas")
        self.metrics.register_counter("branches_created_total", "Total de branches criados")
        self.metrics.register_counter("merges_completed_total", "Total de merges completados")
        self.metrics.register_gauge("active_branches", "Branches ativos")
        self.metrics.register_histogram("version_creation_latency", "Latência de criação de versões")
    
    def create_version(self, document_id: str, content: str, author_id: str, 
                      version_type: VersionType = VersionType.AUTO, message: str = "",
                      parent_version_id: Optional[str] = None, branch_name: str = "main") -> Version:
        """Cria uma nova versão do documento"""
        with self.tracing.start_span("create_version"):
            start_time = time.time()
            
            # Calcular hash do conteúdo
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Determinar número da versão
            version_number = self._get_next_version_number(document_id, branch_name)
            
            # Criar versão
            version = Version(
                document_id=document_id,
                version_number=version_number,
                content=content,
                content_hash=content_hash,
                author_id=author_id,
                version_type=version_type,
                message=message,
                parent_version_id=parent_version_id,
                branch_name=branch_name
            )
            
            # Adicionar ao sistema
            self.versions[version.id] = version
            
            # Indexar por documento
            if document_id not in self.document_versions:
                self.document_versions[document_id] = []
            self.document_versions[document_id].append(version.id)
            
            # Atualizar branch
            self._update_branch_head(document_id, branch_name, version.id)
            
            # Métricas
            latency = time.time() - start_time
            self.metrics.record_histogram("version_creation_latency", latency)
            self.metrics.increment_counter("versions_created_total")
            
            logger.info(f"Versão criada: {version.id} (value{version_number}) em {document_id}")
            return version
    
    def _get_next_version_number(self, document_id: str, branch_name: str) -> int:
        """Obtém o próximo número de versão para um branch"""
        if document_id not in self.document_versions:
            return 1
        
        # Encontrar versão mais recente do branch
        latest_version = 0
        for version_id in self.document_versions[document_id]:
            version = self.versions.get(version_id)
            if version and version.branch_name == branch_name:
                latest_version = max(latest_version, version.version_number)
        
        return latest_version + 1
    
    def _update_branch_head(self, document_id: str, branch_name: str, version_id: str):
        """Atualiza o head de um branch"""
        if document_id not in self.branches:
            self.branches[document_id] = {}
        
        if branch_name not in self.branches[document_id]:
            # Criar novo branch
            branch = Branch(
                name=branch_name,
                head_version_id=version_id,
                created_by=self.versions[version_id].author_id,
                is_default=(branch_name == "main")
            )
            self.branches[document_id][branch_name] = branch
            self.metrics.increment_counter("branches_created_total")
            self.metrics.increment_gauge("active_branches", 1)
        else:
            # Atualizar branch existente
            branch = self.branches[document_id][branch_name]
            branch.head_version_id = version_id
            branch.last_modified = time.time()
    
    def get_version(self, version_id: str) -> Optional[Version]:
        """Obtém uma versão específica"""
        return self.versions.get(version_id)
    
    def get_latest_version(self, document_id: str, branch_name: str = "main") -> Optional[Version]:
        """Obtém a versão mais recente de um branch"""
        if document_id not in self.branches or branch_name not in self.branches[document_id]:
            return None
        
        branch = self.branches[document_id][branch_name]
        return self.versions.get(branch.head_version_id)
    
    def get_version_history(self, document_id: str, branch_name: str = "main", 
                          limit: Optional[int] = None) -> List[Version]:
        """Obtém o histórico de versões de um branch"""
        with self.tracing.start_span("get_version_history"):
            if document_id not in self.document_versions:
                return []
            
            # Filtrar versões do branch
            branch_versions = []
            for version_id in self.document_versions[document_id]:
                version = self.versions.get(version_id)
                if version and version.branch_name == branch_name:
                    branch_versions.append(version)
            
            # Ordenar por número de versão
            branch_versions.sort(key=lambda value: value.version_number)
            
            # Aplicar limite se especificado
            if limit:
                branch_versions = branch_versions[-limit:]
            
            return branch_versions
    
    def get_branches(self, document_id: str) -> List[Branch]:
        """Obtém todos os branches de um documento"""
        if document_id not in self.branches:
            return []
        
        return list(self.branches[document_id].values())
    
    def create_branch(self, document_id: str, branch_name: str, source_branch: str = "main",
                     author_id: str = "") -> Branch:
        """Cria um novo branch"""
        with self.tracing.start_span("create_branch"):
            if document_id not in self.branches:
                raise ValueError(f"Documento não encontrado: {document_id}")
            
            if branch_name in self.branches[document_id]:
                raise ValueError(f"Branch já existe: {branch_name}")
            
            # Obter versão atual do branch fonte
            source_version = self.get_latest_version(document_id, source_branch)
            if not source_version:
                raise ValueError(f"Branch fonte não encontrado: {source_branch}")
            
            # Criar novo branch
            branch = Branch(
                name=branch_name,
                head_version_id=source_version.id,
                created_by=author_id or source_version.author_id
            )
            
            self.branches[document_id][branch_name] = branch
            self.metrics.increment_counter("branches_created_total")
            self.metrics.increment_gauge("active_branches", 1)
            
            logger.info(f"Branch criado: {branch_name} em {document_id}")
            return branch
    
    def delete_branch(self, document_id: str, branch_name: str) -> bool:
        """Deleta um branch"""
        with self.tracing.start_span("delete_branch"):
            if document_id not in self.branches or branch_name not in self.branches[document_id]:
                return False
            
            if branch_name == "main":
                raise ValueError("Não é possível deletar o branch principal")
            
            # Verificar se há versões no branch
            branch_versions = self.get_version_history(document_id, branch_name)
            if len(branch_versions) > 1:  # Mais que a versão inicial
                raise ValueError("Não é possível deletar branch com versões não mescladas")
            
            # Remover branch
            del self.branches[document_id][branch_name]
            self.metrics.increment_gauge("active_branches", -1)
            
            logger.info(f"Branch deletado: {branch_name} em {document_id}")
            return True
    
    def create_merge_request(self, document_id: str, source_branch: str, target_branch: str,
                           requester_id: str, message: str = "") -> MergeRequest:
        """Cria uma solicitação de merge"""
        with self.tracing.start_span("create_merge_request"):
            # Verificar se os branches existem
            if document_id not in self.branches:
                raise ValueError(f"Documento não encontrado: {document_id}")
            
            if source_branch not in self.branches[document_id]:
                raise ValueError(f"Branch fonte não encontrado: {source_branch}")
            
            if target_branch not in self.branches[document_id]:
                raise ValueError(f"Branch destino não encontrado: {target_branch}")
            
            # Obter versões atuais
            source_version = self.get_latest_version(document_id, source_branch)
            target_version = self.get_latest_version(document_id, target_branch)
            
            if not source_version or not target_version:
                raise ValueError("Não foi possível obter versões dos branches")
            
            # Verificar se já existe um merge request pendente
            for mr in self.merge_requests.values():
                if (mr.source_branch == source_branch and 
                    mr.target_branch == target_branch and 
                    mr.status == MergeStatus.PENDING):
                    raise ValueError("Já existe um merge request pendente para estes branches")
            
            # Criar merge request
            merge_request = MergeRequest(
                source_branch=source_branch,
                target_branch=target_branch,
                source_version_id=source_version.id,
                target_version_id=target_version.id,
                requester_id=requester_id,
                message=message
            )
            
            self.merge_requests[merge_request.id] = merge_request
            
            logger.info(f"Merge request criado: {merge_request.id}")
            return merge_request
    
    def check_merge_conflicts(self, merge_request_id: str) -> List[Dict[str, Any]]:
        """Verifica conflitos em um merge request"""
        with self.tracing.start_span("check_merge_conflicts"):
            if merge_request_id not in self.merge_requests:
                raise ValueError(f"Merge request não encontrado: {merge_request_id}")
            
            merge_request = self.merge_requests[merge_request_id]
            
            # Obter versões
            source_version = self.versions.get(merge_request.source_version_id)
            target_version = self.versions.get(merge_request.target_version_id)
            
            if not source_version or not target_version:
                raise ValueError("Versões não encontradas")
            
            # Simular merge para detectar conflitos
            conflicts = self._detect_conflicts(source_version.content, target_version.content)
            
            # Atualizar status do merge request
            if conflicts:
                merge_request.status = MergeStatus.CONFLICT
                merge_request.conflicts = conflicts
            else:
                merge_request.status = MergeStatus.PENDING
            
            return conflicts
    
    def _detect_conflicts(self, source_content: str, target_content: str) -> List[Dict[str, Any]]:
        """Detecta conflitos entre dois conteúdos"""
        conflicts = []
        
        # Implementação simplificada - em produção seria mais sofisticada
        # Aqui apenas verificamos se os conteúdos são diferentes
        if source_content != target_content:
            conflicts.append({
                "type": "content_conflict",
                "description": "Conteúdo divergente entre branches",
                "source_length": len(source_content),
                "target_length": len(target_content)
            })
        
        return conflicts
    
    def resolve_merge_conflicts(self, merge_request_id: str, resolved_content: str,
                              resolver_id: str) -> Version:
        """Resolve conflitos de merge"""
        with self.tracing.start_span("resolve_merge_conflicts"):
            if merge_request_id not in self.merge_requests:
                raise ValueError(f"Merge request não encontrado: {merge_request_id}")
            
            merge_request = self.merge_requests[merge_request_id]
            
            if merge_request.status != MergeStatus.CONFLICT:
                raise ValueError("Merge request não está em conflito")
            
            # Criar nova versão com conteúdo resolvido
            version = self.create_version(
                document_id=merge_request.source_branch.split(":")[0] if ":" in merge_request.source_branch else "",
                content=resolved_content,
                author_id=resolver_id,
                version_type=VersionType.MERGE,
                message=f"Merge resolved: {merge_request.source_branch} -> {merge_request.target_branch}",
                branch_name=merge_request.target_branch
            )
            
            # Atualizar merge request
            merge_request.status = MergeStatus.RESOLVED
            merge_request.resolved_by = resolver_id
            merge_request.resolved_at = time.time()
            
            logger.info(f"Conflitos de merge resolvidos: {merge_request_id}")
            return version
    
    def complete_merge(self, merge_request_id: str, completer_id: str) -> bool:
        """Completa um merge"""
        with self.tracing.start_span("complete_merge"):
            if merge_request_id not in self.merge_requests:
                return False
            
            merge_request = self.merge_requests[merge_request_id]
            
            if merge_request.status not in [MergeStatus.PENDING, MergeStatus.RESOLVED]:
                raise ValueError("Merge request não pode ser completado")
            
            # Marcar como completado
            merge_request.status = MergeStatus.COMPLETED
            merge_request.resolved_by = completer_id
            merge_request.resolved_at = time.time()
            
            # Métricas
            self.metrics.increment_counter("merges_completed_total")
            
            logger.info(f"Merge completado: {merge_request_id}")
            return True
    
    def get_merge_requests(self, document_id: Optional[str] = None, 
                          status: Optional[MergeStatus] = None) -> List[MergeRequest]:
        """Obtém merge requests"""
        with self.tracing.start_span("get_merge_requests"):
            requests = list(self.merge_requests.values())
            
            # Filtrar por documento
            if document_id:
                requests = [mr for mr in requests 
                          if mr.source_branch.split(":")[0] == document_id 
                          or mr.target_branch.split(":")[0] == document_id]
            
            # Filtrar por status
            if status:
                requests = [mr for mr in requests if mr.status == status]
            
            # Ordenar por data de criação
            requests.sort(key=lambda mr: mr.created_at, reverse=True)
            return requests
    
    def compare_versions(self, version_id_1: str, version_id_2: str) -> Dict[str, Any]:
        """Compara duas versões"""
        with self.tracing.start_span("compare_versions"):
            version_1 = self.versions.get(version_id_1)
            version_2 = self.versions.get(version_id_2)
            
            if not version_1 or not version_2:
                raise ValueError("Uma ou ambas as versões não encontradas")
            
            # Calcular diferenças
            diff = self._calculate_diff(version_1.content, version_2.content)
            
            return {
                "version_1": {
                    "id": version_1.id,
                    "version_number": version_1.version_number,
                    "author": version_1.author_id,
                    "timestamp": version_1.timestamp
                },
                "version_2": {
                    "id": version_2.id,
                    "version_number": version_2.version_number,
                    "author": version_2.author_id,
                    "timestamp": version_2.timestamp
                },
                "diff": diff,
                "content_length_diff": len(version_2.content) - len(version_1.content)
            }
    
    def _calculate_diff(self, content_1: str, content_2: str) -> List[Dict[str, Any]]:
        """Calcula diferenças entre dois conteúdos"""
        # Implementação simplificada - em produção seria mais sofisticada
        diff = []
        
        if content_1 != content_2:
            diff.append({
                "type": "content_changed",
                "description": "Conteúdo modificado",
                "old_length": len(content_1),
                "new_length": len(content_2)
            })
        
        return diff
    
    def get_statistics(self, document_id: Optional[str] = None) -> Dict[str, Any]:
        """Retorna estatísticas do versionamento"""
        with self.tracing.start_span("get_version_statistics"):
            stats = {
                "total_versions": 0,
                "total_branches": 0,
                "total_merge_requests": 0,
                "versions_by_type": {},
                "branches_by_document": {},
                "merge_requests_by_status": {}
            }
            
            # Contar versões
            for version in self.versions.values():
                if document_id and version.document_id != document_id:
                    continue
                
                stats["total_versions"] += 1
                
                version_type = version.version_type.value
                if version_type not in stats["versions_by_type"]:
                    stats["versions_by_type"][version_type] = 0
                stats["versions_by_type"][version_type] += 1
            
            # Contar branches
            for doc_id, branches in self.branches.items():
                if document_id and doc_id != document_id:
                    continue
                
                stats["total_branches"] += len(branches)
                stats["branches_by_document"][doc_id] = len(branches)
            
            # Contar merge requests
            for mr in self.merge_requests.values():
                if document_id:
                    doc_id = mr.source_branch.split(":")[0] if ":" in mr.source_branch else ""
                    if doc_id != document_id:
                        continue
                
                stats["total_merge_requests"] += 1
                
                status = mr.status.value
                if status not in stats["merge_requests_by_status"]:
                    stats["merge_requests_by_status"][status] = 0
                stats["merge_requests_by_status"][status] += 1
            
            return stats
    
    def export_version_history(self, document_id: str, branch_name: str = "main", 
                              format: str = "json") -> str:
        """Exporta histórico de versões"""
        with self.tracing.start_span("export_version_history"):
            versions = self.get_version_history(document_id, branch_name)
            
            if format.lower() == "json":
                return json.dumps([version.to_dict() for version in versions], indent=2)
            else:
                raise ValueError(f"Formato não suportado: {format}")


# Função de conveniência para criar sistema de versionamento
def create_version_control() -> VersionControl:
    """Cria uma instância do sistema de versionamento"""
    return VersionControl() 
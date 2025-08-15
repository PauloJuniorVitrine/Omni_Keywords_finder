"""
Sistema de Versionamento de Configurações - Omni Keywords Finder

Este módulo implementa um sistema robusto de versionamento de configurações
com as seguintes funcionalidades:
- Versionamento automático de configurações
- Sistema de rollback
- Comparação de versões
- Aprovação de mudanças
- Histórico de configurações
- Exportação de configurações

Autor: Sistema Omni Keywords Finder
Data: 2024-12-19
Versão: 1.0.0
"""

import json
import hashlib
import sqlite3
import datetime
import difflib
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import yaml
import pickle
from contextlib import contextmanager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigStatus(Enum):
    """Status das configurações"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class ConfigType(Enum):
    """Tipos de configuração"""
    SYSTEM = "system"
    USER = "user"
    FEATURE = "feature"
    INTEGRATION = "integration"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class ConfigVersion:
    """Representa uma versão de configuração"""
    id: str
    config_name: str
    config_type: ConfigType
    version: str
    content: Dict[str, Any]
    hash: str
    status: ConfigStatus
    created_by: str
    created_at: datetime.datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime.datetime] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ConfigChange:
    """Representa uma mudança de configuração"""
    id: str
    config_name: str
    from_version: str
    to_version: str
    changes: Dict[str, Any]
    change_type: str
    created_by: str
    created_at: datetime.datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime.datetime] = None
    rollback_available: bool = True


class ConfigVersioningSystem:
    """
    Sistema principal de versionamento de configurações
    """
    
    def __init__(self, db_path: str = "config_versions.db", backup_dir: str = "config_backups"):
        """
        Inicializa o sistema de versionamento
        
        Args:
            db_path: Caminho para o banco de dados SQLite
            backup_dir: Diretório para backups de configurações
        """
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        self._init_database()
        logger.info(f"Sistema de versionamento inicializado: {db_path}")
    
    def _init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config_versions (
                    id TEXT PRIMARY KEY,
                    config_name TEXT NOT NULL,
                    config_type TEXT NOT NULL,
                    version TEXT NOT NULL,
                    content TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    approved_by TEXT,
                    approved_at TEXT,
                    description TEXT,
                    tags TEXT,
                    dependencies TEXT,
                    metadata TEXT,
                    UNIQUE(config_name, version)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config_changes (
                    id TEXT PRIMARY KEY,
                    config_name TEXT NOT NULL,
                    from_version TEXT NOT NULL,
                    to_version TEXT NOT NULL,
                    changes TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    approved_by TEXT,
                    approved_at TEXT,
                    rollback_available BOOLEAN DEFAULT 1
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config_approvals (
                    id TEXT PRIMARY KEY,
                    config_version_id TEXT NOT NULL,
                    approver TEXT NOT NULL,
                    status TEXT NOT NULL,
                    comments TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (config_version_id) REFERENCES config_versions (id)
                )
            """)
            
            # Índices para performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_config_name ON config_versions(config_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_config_status ON config_versions(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON config_versions(created_at)")
            
            conn.commit()
    
    def _generate_hash(self, content: Dict[str, Any]) -> str:
        """Gera hash SHA-256 do conteúdo da configuração"""
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _generate_version_id(self) -> str:
        """Gera ID único para versão"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"v_{timestamp}"
    
    def _serialize_content(self, content: Dict[str, Any]) -> str:
        """Serializa conteúdo para armazenamento"""
        return json.dumps(content, ensure_ascii=False, indent=2)
    
    def _deserialize_content(self, content_str: str) -> Dict[str, Any]:
        """Deserializa conteúdo do armazenamento"""
        return json.loads(content_str)
    
    def create_version(
        self,
        config_name: str,
        config_type: ConfigType,
        content: Dict[str, Any],
        created_by: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConfigVersion:
        """
        Cria uma nova versão de configuração
        
        Args:
            config_name: Nome da configuração
            config_type: Tipo da configuração
            content: Conteúdo da configuração
            created_by: Usuário que criou
            description: Descrição da versão
            tags: Tags para categorização
            dependencies: Dependências de outras configurações
            metadata: Metadados adicionais
            
        Returns:
            ConfigVersion criada
        """
        version_id = self._generate_version_id()
        content_hash = self._generate_hash(content)
        
        # Verifica se já existe versão idêntica
        existing = self.get_version_by_hash(content_hash)
        if existing:
            logger.warning(f"Configuração idêntica já existe: {existing.id}")
            return existing
        
        config_version = ConfigVersion(
            id=version_id,
            config_name=config_name,
            config_type=config_type,
            version=version_id,
            content=content,
            hash=content_hash,
            status=ConfigStatus.DRAFT,
            created_by=created_by,
            created_at=datetime.datetime.now(),
            description=description,
            tags=tags or [],
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO config_versions 
                (id, config_name, config_type, version, content, hash, status, 
                 created_by, created_at, approved_by, approved_at, description, 
                 tags, dependencies, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                config_version.id,
                config_version.config_name,
                config_version.config_type.value,
                config_version.version,
                self._serialize_content(config_version.content),
                config_version.hash,
                config_version.status.value,
                config_version.created_by,
                config_version.created_at.isoformat(),
                config_version.approved_by,
                config_version.approved_at.isoformat() if config_version.approved_at else None,
                config_version.description,
                json.dumps(config_version.tags),
                json.dumps(config_version.dependencies),
                json.dumps(config_version.metadata)
            ))
            conn.commit()
        
        logger.info(f"Nova versão criada: {version_id} para {config_name}")
        return config_version
    
    def get_version(self, version_id: str) -> Optional[ConfigVersion]:
        """Obtém uma versão específica pelo ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM config_versions WHERE id = ?
            """, (version_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_config_version(row)
    
    def get_version_by_hash(self, content_hash: str) -> Optional[ConfigVersion]:
        """Obtém versão pelo hash do conteúdo"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM config_versions WHERE hash = ?
            """, (content_hash,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_config_version(row)
    
    def get_active_version(self, config_name: str) -> Optional[ConfigVersion]:
        """Obtém a versão ativa de uma configuração"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM config_versions 
                WHERE config_name = ? AND status = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (config_name, ConfigStatus.ACTIVE.value))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_config_version(row)
    
    def get_version_history(self, config_name: str, limit: int = 50) -> List[ConfigVersion]:
        """Obtém histórico de versões de uma configuração"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM config_versions 
                WHERE config_name = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (config_name, limit))
            
            return [self._row_to_config_version(row) for row in cursor.fetchall()]
    
    def _row_to_config_version(self, row: Tuple) -> ConfigVersion:
        """Converte linha do banco para objeto ConfigVersion"""
        return ConfigVersion(
            id=row[0],
            config_name=row[1],
            config_type=ConfigType(row[2]),
            version=row[3],
            content=self._deserialize_content(row[4]),
            hash=row[5],
            status=ConfigStatus(row[6]),
            created_by=row[7],
            created_at=datetime.datetime.fromisoformat(row[8]),
            approved_by=row[9],
            approved_at=datetime.datetime.fromisoformat(row[10]) if row[10] else None,
            description=row[11],
            tags=json.loads(row[12]) if row[12] else [],
            dependencies=json.loads(row[13]) if row[13] else [],
            metadata=json.loads(row[14]) if row[14] else {}
        )
    
    def update_status(self, version_id: str, status: ConfigStatus, approved_by: Optional[str] = None) -> bool:
        """
        Atualiza o status de uma versão
        
        Args:
            version_id: ID da versão
            status: Novo status
            approved_by: Usuário que aprovou (se aplicável)
            
        Returns:
            True se atualizado com sucesso
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE config_versions 
                SET status = ?, approved_by = ?, approved_at = ?
                WHERE id = ?
            """, (
                status.value,
                approved_by,
                datetime.datetime.now().isoformat() if approved_by else None,
                version_id
            ))
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"Status atualizado para {status.value}: {version_id}")
                return True
            
            return False
    
    def activate_version(self, version_id: str, activated_by: str) -> bool:
        """
        Ativa uma versão de configuração
        
        Args:
            version_id: ID da versão
            activated_by: Usuário que ativou
            
        Returns:
            True se ativado com sucesso
        """
        # Desativa versão atual se existir
        version = self.get_version(version_id)
        if not version:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            # Desativa versão atual
            conn.execute("""
                UPDATE config_versions 
                SET status = ?
                WHERE config_name = ? AND status = ?
            """, (ConfigStatus.DEPRECATED.value, version.config_name, ConfigStatus.ACTIVE.value))
            
            # Ativa nova versão
            conn.execute("""
                UPDATE config_versions 
                SET status = ?, approved_by = ?, approved_at = ?
                WHERE id = ?
            """, (
                ConfigStatus.ACTIVE.value,
                activated_by,
                datetime.datetime.now().isoformat(),
                version_id
            ))
            
            conn.commit()
        
        logger.info(f"Versão ativada: {version_id} por {activated_by}")
        return True
    
    def compare_versions(self, version1_id: str, version2_id: str) -> Dict[str, Any]:
        """
        Compara duas versões de configuração
        
        Args:
            version1_id: ID da primeira versão
            version2_id: ID da segunda versão
            
        Returns:
            Dicionário com diferenças detalhadas
        """
        version1 = self.get_version(version1_id)
        version2 = self.get_version(version2_id)
        
        if not version1 or not version2:
            raise ValueError("Uma ou ambas as versões não encontradas")
        
        # Gera diff textual
        content1_str = json.dumps(version1.content, indent=2, sort_keys=True)
        content2_str = json.dumps(version2.content, indent=2, sort_keys=True)
        
        diff_lines = list(difflib.unified_diff(
            content1_str.splitlines(keepends=True),
            content2_str.splitlines(keepends=True),
            fromfile=f"{version1.config_name}@{version1.version}",
            tofile=f"{version2.config_name}@{version2.version}"
        ))
        
        # Análise de mudanças por chave
        changes = self._analyze_key_changes(version1.content, version2.content)
        
        return {
            "version1": {
                "id": version1.id,
                "version": version1.version,
                "created_at": version1.created_at.isoformat(),
                "created_by": version1.created_by
            },
            "version2": {
                "id": version2.id,
                "version": version2.version,
                "created_at": version2.created_at.isoformat(),
                "created_by": version2.created_by
            },
            "diff_text": "".join(diff_lines),
            "changes": changes,
            "summary": {
                "added_keys": len(changes["added"]),
                "removed_keys": len(changes["removed"]),
                "modified_keys": len(changes["modified"]),
                "unchanged_keys": len(changes["unchanged"])
            }
        }
    
    def _analyze_key_changes(self, content1: Dict[str, Any], content2: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analisa mudanças por chave entre duas configurações"""
        keys1 = set(content1.keys())
        keys2 = set(content2.keys())
        
        added = list(keys2 - keys1)
        removed = list(keys1 - keys2)
        common = keys1 & keys2
        
        modified = []
        unchanged = []
        
        for key in common:
            if content1[key] != content2[key]:
                modified.append(key)
            else:
                unchanged.append(key)
        
        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "unchanged": unchanged
        }
    
    def rollback_to_version(self, config_name: str, target_version_id: str, rolled_back_by: str) -> bool:
        """
        Faz rollback para uma versão anterior
        
        Args:
            config_name: Nome da configuração
            target_version_id: ID da versão alvo
            rolled_back_by: Usuário que fez o rollback
            
        Returns:
            True se rollback realizado com sucesso
        """
        target_version = self.get_version(target_version_id)
        if not target_version or target_version.config_name != config_name:
            return False
        
        # Cria nova versão baseada na versão alvo
        rollback_version = self.create_version(
            config_name=config_name,
            config_type=target_version.config_type,
            content=target_version.content,
            created_by=rolled_back_by,
            description=f"Rollback para versão {target_version.version}",
            tags=target_version.tags + ["rollback"],
            dependencies=target_version.dependencies,
            metadata={
                **(target_version.metadata or {}),
                "rollback_from": target_version_id,
                "rollback_reason": "Manual rollback"
            }
        )
        
        # Ativa a nova versão
        return self.activate_version(rollback_version.id, rolled_back_by)
    
    def export_configuration(self, version_id: str, format: str = "json") -> str:
        """
        Exporta configuração em diferentes formatos
        
        Args:
            version_id: ID da versão
            format: Formato de exportação (json, yaml, pickle)
            
        Returns:
            String com configuração exportada
        """
        version = self.get_version(version_id)
        if not version:
            raise ValueError("Versão não encontrada")
        
        export_data = {
            "metadata": {
                "id": version.id,
                "config_name": version.config_name,
                "config_type": version.config_type.value,
                "version": version.version,
                "status": version.status.value,
                "created_by": version.created_by,
                "created_at": version.created_at.isoformat(),
                "approved_by": version.approved_by,
                "approved_at": version.approved_at.isoformat() if version.approved_at else None,
                "description": version.description,
                "tags": version.tags,
                "dependencies": version.dependencies,
                "hash": version.hash
            },
            "content": version.content
        }
        
        if format.lower() == "json":
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        elif format.lower() == "yaml":
            return yaml.dump(export_data, default_flow_style=False, allow_unicode=True)
        elif format.lower() == "pickle":
            return pickle.dumps(export_data)
        else:
            raise ValueError(f"Formato não suportado: {format}")
    
    def import_configuration(self, config_data: str, format: str = "json", imported_by: str = "system") -> ConfigVersion:
        """
        Importa configuração de arquivo externo
        
        Args:
            config_data: Dados da configuração
            format: Formato dos dados
            imported_by: Usuário que importou
            
        Returns:
            ConfigVersion importada
        """
        if format.lower() == "json":
            data = json.loads(config_data)
        elif format.lower() == "yaml":
            data = yaml.safe_load(config_data)
        elif format.lower() == "pickle":
            data = pickle.loads(config_data.encode() if isinstance(config_data, str) else config_data)
        else:
            raise ValueError(f"Formato não suportado: {format}")
        
        # Valida estrutura
        if "metadata" not in data or "content" not in data:
            raise ValueError("Estrutura de dados inválida")
        
        metadata = data["metadata"]
        content = data["content"]
        
        return self.create_version(
            config_name=metadata["config_name"],
            config_type=ConfigType(metadata["config_type"]),
            content=content,
            created_by=imported_by,
            description=f"Importado de {metadata.get('version', 'versão externa')}",
            tags=metadata.get("tags", []) + ["imported"],
            dependencies=metadata.get("dependencies", []),
            metadata=metadata
        )
    
    def get_pending_approvals(self) -> List[ConfigVersion]:
        """Obtém versões pendentes de aprovação"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM config_versions 
                WHERE status = ?
                ORDER BY created_at ASC
            """, (ConfigStatus.PENDING_APPROVAL.value,))
            
            return [self._row_to_config_version(row) for row in cursor.fetchall()]
    
    def approve_version(self, version_id: str, approver: str, approved: bool, comments: Optional[str] = None) -> bool:
        """
        Aprova ou rejeita uma versão
        
        Args:
            version_id: ID da versão
            approver: Usuário que aprovou/rejeitou
            approved: True para aprovar, False para rejeitar
            comments: Comentários sobre a decisão
            
        Returns:
            True se processado com sucesso
        """
        new_status = ConfigStatus.APPROVED if approved else ConfigStatus.REJECTED
        
        with sqlite3.connect(self.db_path) as conn:
            # Atualiza status da versão
            conn.execute("""
                UPDATE config_versions 
                SET status = ?, approved_by = ?, approved_at = ?
                WHERE id = ?
            """, (
                new_status.value,
                approver,
                datetime.datetime.now().isoformat(),
                version_id
            ))
            
            # Registra aprovação
            approval_id = f"approval_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            conn.execute("""
                INSERT INTO config_approvals 
                (id, config_version_id, approver, status, comments, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                approval_id,
                version_id,
                approver,
                "approved" if approved else "rejected",
                comments,
                datetime.datetime.now().isoformat()
            ))
            
            conn.commit()
        
        logger.info(f"Versão {version_id} {'aprovada' if approved else 'rejeitada'} por {approver}")
        return True
    
    def create_backup(self, config_name: Optional[str] = None) -> str:
        """
        Cria backup das configurações
        
        Args:
            config_name: Nome específico da configuração (opcional)
            
        Returns:
            Caminho do arquivo de backup
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"config_backup_{timestamp}.json"
        
        with sqlite3.connect(self.db_path) as conn:
            if config_name:
                cursor = conn.execute("""
                    SELECT * FROM config_versions WHERE config_name = ?
                """, (config_name,))
            else:
                cursor = conn.execute("SELECT * FROM config_versions")
            
            versions = [self._row_to_config_version(row) for row in cursor.fetchall()]
        
        backup_data = {
            "backup_info": {
                "created_at": datetime.datetime.now().isoformat(),
                "total_versions": len(versions),
                "config_name": config_name
            },
            "versions": [asdict(version) for version in versions]
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Backup criado: {backup_file}")
        return str(backup_file)
    
    def restore_from_backup(self, backup_file: str, restore_by: str) -> int:
        """
        Restaura configurações de backup
        
        Args:
            backup_file: Caminho do arquivo de backup
            restore_by: Usuário que fez a restauração
            
        Returns:
            Número de versões restauradas
        """
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        restored_count = 0
        
        for version_data in backup_data["versions"]:
            try:
                # Converte timestamps de volta para datetime
                version_data["created_at"] = datetime.datetime.fromisoformat(version_data["created_at"])
                if version_data.get("approved_at"):
                    version_data["approved_at"] = datetime.datetime.fromisoformat(version_data["approved_at"])
                
                # Cria nova versão
                config_version = ConfigVersion(
                    id=version_data["id"],
                    config_name=version_data["config_name"],
                    config_type=ConfigType(version_data["config_type"]),
                    version=version_data["version"],
                    content=version_data["content"],
                    hash=version_data["hash"],
                    status=ConfigStatus(version_data["status"]),
                    created_by=version_data["created_by"],
                    created_at=version_data["created_at"],
                    approved_by=version_data.get("approved_by"),
                    approved_at=version_data.get("approved_at"),
                    description=version_data.get("description"),
                    tags=version_data.get("tags", []),
                    dependencies=version_data.get("dependencies", []),
                    metadata=version_data.get("metadata", {})
                )
                
                # Insere no banco
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO config_versions 
                        (id, config_name, config_type, version, content, hash, status, 
                         created_by, created_at, approved_by, approved_at, description, 
                         tags, dependencies, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        config_version.id,
                        config_version.config_name,
                        config_version.config_type.value,
                        config_version.version,
                        self._serialize_content(config_version.content),
                        config_version.hash,
                        config_version.status.value,
                        config_version.created_by,
                        config_version.created_at.isoformat(),
                        config_version.approved_by,
                        config_version.approved_at.isoformat() if config_version.approved_at else None,
                        config_version.description,
                        json.dumps(config_version.tags),
                        json.dumps(config_version.dependencies),
                        json.dumps(config_version.metadata)
                    ))
                    conn.commit()
                
                restored_count += 1
                
            except Exception as e:
                logger.error(f"Erro ao restaurar versão {version_data.get('id', 'unknown')}: {e}")
        
        logger.info(f"Restauradas {restored_count} versões de {backup_file}")
        return restored_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas do sistema de versionamento"""
        with sqlite3.connect(self.db_path) as conn:
            # Total de versões
            total_versions = conn.execute("SELECT COUNT(*) FROM config_versions").fetchone()[0]
            
            # Versões por status
            status_counts = {}
            for status in ConfigStatus:
                count = conn.execute("""
                    SELECT COUNT(*) FROM config_versions WHERE status = ?
                """, (status.value,)).fetchone()[0]
                status_counts[status.value] = count
            
            # Versões por tipo
            type_counts = {}
            for config_type in ConfigType:
                count = conn.execute("""
                    SELECT COUNT(*) FROM config_versions WHERE config_type = ?
                """, (config_type.value,)).fetchone()[0]
                type_counts[config_type.value] = count
            
            # Configurações únicas
            unique_configs = conn.execute("""
                SELECT COUNT(DISTINCT config_name) FROM config_versions
            """).fetchone()[0]
            
            # Versões pendentes de aprovação
            pending_approvals = conn.execute("""
                SELECT COUNT(*) FROM config_versions WHERE status = ?
            """, (ConfigStatus.PENDING_APPROVAL.value,)).fetchone()[0]
            
            # Última atividade
            last_activity = conn.execute("""
                SELECT MAX(created_at) FROM config_versions
            """).fetchone()[0]
            
            return {
                "total_versions": total_versions,
                "unique_configurations": unique_configs,
                "status_distribution": status_counts,
                "type_distribution": type_counts,
                "pending_approvals": pending_approvals,
                "last_activity": last_activity
            }


# Instância global do sistema
config_versioning = ConfigVersioningSystem()


# Funções de conveniência para uso direto
def create_config_version(
    config_name: str,
    config_type: ConfigType,
    content: Dict[str, Any],
    created_by: str,
    **kwargs
) -> ConfigVersion:
    """Cria nova versão de configuração"""
    return config_versioning.create_version(
        config_name, config_type, content, created_by, **kwargs
    )


def get_active_config(config_name: str) -> Optional[Dict[str, Any]]:
    """Obtém configuração ativa"""
    version = config_versioning.get_active_version(config_name)
    return version.content if version else None


def activate_config_version(version_id: str, activated_by: str) -> bool:
    """Ativa versão de configuração"""
    return config_versioning.activate_version(version_id, activated_by)


def rollback_config(config_name: str, target_version_id: str, rolled_back_by: str) -> bool:
    """Faz rollback de configuração"""
    return config_versioning.rollback_to_version(config_name, target_version_id, rolled_back_by)


def export_config(version_id: str, format: str = "json") -> str:
    """Exporta configuração"""
    return config_versioning.export_configuration(version_id, format)


def import_config(config_data: str, format: str = "json", imported_by: str = "system") -> ConfigVersion:
    """Importa configuração"""
    return config_versioning.import_configuration(config_data, format, imported_by)


if __name__ == "__main__":
    # Exemplo de uso
    print("Sistema de Versionamento de Configurações - Omni Keywords Finder")
    print("=" * 60)
    
    # Criar configuração de exemplo
    config_content = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "omni_keywords",
            "pool_size": 10
        },
        "redis": {
            "host": "localhost",
            "port": 6379,
            "db": 0
        },
        "api": {
            "rate_limit": 1000,
            "timeout": 30,
            "max_retries": 3
        }
    }
    
    # Criar versão
    version = create_config_version(
        config_name="app_config",
        config_type=ConfigType.SYSTEM,
        content=config_content,
        created_by="admin",
        description="Configuração inicial do sistema",
        tags=["initial", "production"]
    )
    
    print(f"Versão criada: {version.id}")
    print(f"Status: {version.status.value}")
    
    # Ativar versão
    if activate_config_version(version.id, "admin"):
        print("Versão ativada com sucesso!")
    
    # Obter configuração ativa
    active_config = get_active_config("app_config")
    if active_config:
        print(f"Configuração ativa: {len(active_config)} seções")
    
    # Estatísticas
    stats = config_versioning.get_statistics()
    print(f"\nEstatísticas:")
    print(f"Total de versões: {stats['total_versions']}")
    print(f"Configurações únicas: {stats['unique_configurations']}")
    print(f"Pendentes de aprovação: {stats['pending_approvals']}") 
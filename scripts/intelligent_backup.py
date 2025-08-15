#!/usr/bin/env python3
"""
Script de Backup Inteligente - Omni Keywords Finder
Tracing ID: BACKUP_INT_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Objetivo: Sistema de backup inteligente com detecção de mudanças,
compressão incremental e estratégias de retenção otimizadas.
"""

import os
import sys
import json
import time
import hashlib
import shutil
import gzip
import tarfile
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import schedule

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [BACKUP_INT] %(message)s',
    handlers=[
        logging.FileHandler('logs/intelligent_backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BackupMetadata:
    """Metadados do backup"""
    backup_id: str
    timestamp: str
    backup_type: str  # full, incremental, differential
    source_path: str
    destination_path: str
    size_bytes: int
    compression_ratio: float
    files_count: int
    changed_files: int
    duration_seconds: float
    checksum: str
    status: str  # success, failed, partial

@dataclass
class BackupConfig:
    """Configuração do backup"""
    source_directories: List[str]
    destination_path: str
    backup_types: List[str]
    retention_policy: Dict[str, int]  # dias para cada tipo
    compression_enabled: bool
    encryption_enabled: bool
    parallel_backup: bool
    max_workers: int
    exclude_patterns: List[str]
    include_patterns: List[str]

class IntelligentBackup:
    """Sistema de backup inteligente com detecção de mudanças"""
    
    def __init__(self, config_file: str = "config/backup_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.metadata_db = Path("logs/backup_metadata.db")
        self.changes_db = Path("logs/file_changes.db")
        
        # Criar diretórios necessários
        Path(self.config.destination_path).mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        # Inicializar bancos de dados
        self._init_databases()
        
        logger.info(f"IntelligentBackup inicializado com {len(self.config.source_directories)} diretórios fonte")
    
    def _load_config(self) -> BackupConfig:
        """Carrega configuração do backup"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
        else:
            # Configuração padrão
            config_data = {
                "source_directories": [
                    "app/",
                    "backend/",
                    "config/",
                    "docs/",
                    "infrastructure/",
                    "scripts/",
                    "tests/",
                    "shared/"
                ],
                "destination_path": "backups/",
                "backup_types": ["full", "incremental", "differential"],
                "retention_policy": {
                    "full": 30,      # 30 dias
                    "incremental": 7, # 7 dias
                    "differential": 14 # 14 dias
                },
                "compression_enabled": True,
                "encryption_enabled": False,
                "parallel_backup": True,
                "max_workers": 4,
                "exclude_patterns": [
                    "*.pyc",
                    "__pycache__/",
                    "*.log",
                    ".git/",
                    "node_modules/",
                    "venv/",
                    ".env"
                ],
                "include_patterns": [
                    "*.py",
                    "*.js",
                    "*.ts",
                    "*.json",
                    "*.yaml",
                    "*.yml",
                    "*.md",
                    "*.sql",
                    "*.html",
                    "*.css"
                ]
            }
            
            # Salvar configuração padrão
            self.config_file.parent.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        
        return BackupConfig(**config_data)
    
    def _init_databases(self):
        """Inicializa bancos de dados para metadados e mudanças"""
        # Banco de metadados
        conn = sqlite3.connect(self.metadata_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_metadata (
                backup_id TEXT PRIMARY KEY,
                timestamp TEXT,
                backup_type TEXT,
                source_path TEXT,
                destination_path TEXT,
                size_bytes INTEGER,
                compression_ratio REAL,
                files_count INTEGER,
                changed_files INTEGER,
                duration_seconds REAL,
                checksum TEXT,
                status TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
        # Banco de mudanças de arquivos
        conn = sqlite3.connect(self.changes_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_changes (
                file_path TEXT,
                last_modified TEXT,
                checksum TEXT,
                backup_id TEXT,
                timestamp TEXT,
                PRIMARY KEY (file_path, backup_id)
            )
        ''')
        conn.commit()
        conn.close()
        
        logger.info("Bancos de dados inicializados")
    
    def _generate_backup_id(self, backup_type: str) -> str:
        """Gera ID único para o backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{backup_type}_{timestamp}_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calcula checksum MD5 do arquivo"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Erro ao calcular checksum de {file_path}: {e}")
            return ""
    
    def _get_file_changes(self, source_dir: str) -> Dict[str, str]:
        """Detecta mudanças nos arquivos"""
        changes = {}
        source_path = Path(source_dir)
        
        if not source_path.exists():
            logger.warning(f"Diretório fonte não existe: {source_dir}")
            return changes
        
        # Conectar ao banco de mudanças
        conn = sqlite3.connect(self.changes_db)
        cursor = conn.cursor()
        
        # Obter último backup
        cursor.execute('''
            SELECT backup_id FROM backup_metadata 
            WHERE backup_type = 'full' 
            ORDER BY timestamp DESC LIMIT 1
        ''')
        result = cursor.fetchone()
        last_backup_id = result[0] if result else None
        
        if not last_backup_id:
            # Primeiro backup - todos os arquivos são "mudados"
            for file_path in source_path.rglob("*"):
                if file_path.is_file() and self._should_backup_file(file_path):
                    changes[str(file_path)] = self._calculate_file_checksum(file_path)
        else:
            # Verificar mudanças desde o último backup
            cursor.execute('''
                SELECT file_path, checksum FROM file_changes 
                WHERE backup_id = ?
            ''', (last_backup_id,))
            last_checksums = dict(cursor.fetchall())
            
            for file_path in source_path.rglob("*"):
                if file_path.is_file() and self._should_backup_file(file_path):
                    file_str = str(file_path)
                    current_checksum = self._calculate_file_checksum(file_path)
                    
                    if file_str not in last_checksums or last_checksums[file_str] != current_checksum:
                        changes[file_str] = current_checksum
        
        conn.close()
        return changes
    
    def _should_backup_file(self, file_path: Path) -> bool:
        """Verifica se arquivo deve ser incluído no backup"""
        file_str = str(file_path)
        
        # Verificar padrões de exclusão
        for pattern in self.config.exclude_patterns:
            if pattern.endswith('/'):
                if file_str.startswith(pattern):
                    return False
            elif file_path.match(pattern):
                return False
        
        # Verificar padrões de inclusão
        for pattern in self.config.include_patterns:
            if file_path.match(pattern):
                return True
        
        # Se não há padrões de inclusão específicos, incluir todos
        return len(self.config.include_patterns) == 0
    
    def _compress_file(self, source_path: Path, dest_path: Path) -> Tuple[int, float]:
        """Comprime arquivo e retorna tamanho original e taxa de compressão"""
        original_size = source_path.stat().st_size
        
        with open(source_path, 'rb') as f_in:
            with gzip.open(dest_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        compressed_size = dest_path.stat().st_size
        compression_ratio = 1 - (compressed_size / original_size)
        
        return original_size, compression_ratio
    
    def _backup_directory(self, source_dir: str, backup_id: str, backup_type: str) -> Dict[str, any]:
        """Faz backup de um diretório"""
        start_time = time.time()
        source_path = Path(source_dir)
        backup_dir = Path(self.config.destination_path) / backup_id / source_path.name
        
        stats = {
            "files_count": 0,
            "changed_files": 0,
            "total_size": 0,
            "compressed_size": 0,
            "errors": []
        }
        
        try:
            # Detectar mudanças
            changes = self._get_file_changes(source_dir)
            stats["changed_files"] = len(changes)
            
            if not changes:
                logger.info(f"Nenhuma mudança detectada em {source_dir}")
                return stats
            
            # Criar diretório de backup
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup paralelo se habilitado
            if self.config.parallel_backup and len(changes) > 10:
                stats.update(self._parallel_backup_files(changes, backup_dir))
            else:
                stats.update(self._sequential_backup_files(changes, backup_dir))
            
            # Salvar metadados de mudanças
            self._save_file_changes(changes, backup_id)
            
            duration = time.time() - start_time
            logger.info(f"Backup de {source_dir} concluído: {stats['files_count']} arquivos em {duration:.2f}s")
            
        except Exception as e:
            stats["errors"].append(str(e))
            logger.error(f"Erro no backup de {source_dir}: {e}")
        
        return stats
    
    def _parallel_backup_files(self, changes: Dict[str, str], backup_dir: Path) -> Dict[str, any]:
        """Faz backup paralelo dos arquivos"""
        stats = {"files_count": 0, "total_size": 0, "compressed_size": 0, "errors": []}
        
        def backup_single_file(file_path: str) -> Dict[str, any]:
            result = {"success": False, "size": 0, "compressed_size": 0}
            try:
                source_file = Path(file_path)
                relative_path = source_file.relative_to(Path.cwd())
                backup_file = backup_dir / relative_path
                
                # Criar diretório pai se necessário
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                
                if self.config.compression_enabled:
                    backup_file = backup_file.with_suffix(backup_file.suffix + '.gz')
                    original_size, compression_ratio = self._compress_file(source_file, backup_file)
                    result["size"] = original_size
                    result["compressed_size"] = backup_file.stat().st_size
                else:
                    shutil.copy2(source_file, backup_file)
                    result["size"] = source_file.stat().st_size
                    result["compressed_size"] = result["size"]
                
                result["success"] = True
                
            except Exception as e:
                result["error"] = str(e)
            
            return result
        
        # Executar backup paralelo
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_file = {executor.submit(backup_single_file, file_path): file_path 
                            for file_path in changes.keys()}
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result["success"]:
                        stats["files_count"] += 1
                        stats["total_size"] += result["size"]
                        stats["compressed_size"] += result["compressed_size"]
                    else:
                        stats["errors"].append(f"{file_path}: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    stats["errors"].append(f"{file_path}: {e}")
        
        return stats
    
    def _sequential_backup_files(self, changes: Dict[str, str], backup_dir: Path) -> Dict[str, any]:
        """Faz backup sequencial dos arquivos"""
        stats = {"files_count": 0, "total_size": 0, "compressed_size": 0, "errors": []}
        
        for file_path in changes.keys():
            try:
                source_file = Path(file_path)
                relative_path = source_file.relative_to(Path.cwd())
                backup_file = backup_dir / relative_path
                
                # Criar diretório pai se necessário
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                
                if self.config.compression_enabled:
                    backup_file = backup_file.with_suffix(backup_file.suffix + '.gz')
                    original_size, compression_ratio = self._compress_file(source_file, backup_file)
                    stats["total_size"] += original_size
                    stats["compressed_size"] += backup_file.stat().st_size
                else:
                    shutil.copy2(source_file, backup_file)
                    file_size = source_file.stat().st_size
                    stats["total_size"] += file_size
                    stats["compressed_size"] += file_size
                
                stats["files_count"] += 1
                
            except Exception as e:
                stats["errors"].append(f"{file_path}: {e}")
        
        return stats
    
    def _save_file_changes(self, changes: Dict[str, str], backup_id: str):
        """Salva metadados de mudanças no banco"""
        conn = sqlite3.connect(self.changes_db)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        for file_path, checksum in changes.items():
            cursor.execute('''
                INSERT OR REPLACE INTO file_changes 
                (file_path, last_modified, checksum, backup_id, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (file_path, timestamp, checksum, backup_id, timestamp))
        
        conn.commit()
        conn.close()
    
    def _save_backup_metadata(self, metadata: BackupMetadata):
        """Salva metadados do backup"""
        conn = sqlite3.connect(self.metadata_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO backup_metadata 
            (backup_id, timestamp, backup_type, source_path, destination_path,
             size_bytes, compression_ratio, files_count, changed_files,
             duration_seconds, checksum, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metadata.backup_id, metadata.timestamp, metadata.backup_type,
            metadata.source_path, metadata.destination_path, metadata.size_bytes,
            metadata.compression_ratio, metadata.files_count, metadata.changed_files,
            metadata.duration_seconds, metadata.checksum, metadata.status
        ))
        
        conn.commit()
        conn.close()
    
    def _cleanup_old_backups(self):
        """Remove backups antigos baseado na política de retenção"""
        logger.info("Iniciando limpeza de backups antigos...")
        
        conn = sqlite3.connect(self.metadata_db)
        cursor = conn.cursor()
        
        for backup_type, retention_days in self.config.retention_policy.items():
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            cutoff_str = cutoff_date.isoformat()
            
            # Buscar backups antigos
            cursor.execute('''
                SELECT backup_id, destination_path FROM backup_metadata 
                WHERE backup_type = ? AND timestamp < ? AND status = 'success'
            ''', (backup_type, cutoff_str))
            
            old_backups = cursor.fetchall()
            
            for backup_id, dest_path in old_backups:
                try:
                    # Remover arquivos
                    backup_path = Path(dest_path)
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                        logger.info(f"Backup removido: {backup_id}")
                    
                    # Remover do banco
                    cursor.execute('DELETE FROM backup_metadata WHERE backup_id = ?', (backup_id,))
                    cursor.execute('DELETE FROM file_changes WHERE backup_id = ?', (backup_id,))
                    
                except Exception as e:
                    logger.error(f"Erro ao remover backup {backup_id}: {e}")
        
        conn.commit()
        conn.close()
        logger.info("Limpeza de backups concluída")
    
    def run_backup(self, backup_type: str = "incremental") -> BackupMetadata:
        """Executa backup completo"""
        if backup_type not in self.config.backup_types:
            raise ValueError(f"Tipo de backup inválido: {backup_type}")
        
        start_time = time.time()
        backup_id = self._generate_backup_id(backup_type)
        
        logger.info(f"Iniciando backup {backup_type} com ID: {backup_id}")
        
        total_stats = {
            "files_count": 0,
            "changed_files": 0,
            "total_size": 0,
            "compressed_size": 0,
            "errors": []
        }
        
        # Fazer backup de cada diretório fonte
        for source_dir in self.config.source_directories:
            stats = self._backup_directory(source_dir, backup_id, backup_type)
            
            total_stats["files_count"] += stats["files_count"]
            total_stats["changed_files"] += stats["changed_files"]
            total_stats["total_size"] += stats["total_size"]
            total_stats["compressed_size"] += stats["compressed_size"]
            total_stats["errors"].extend(stats["errors"])
        
        # Calcular métricas finais
        end_time = time.time()
        duration = end_time - start_time
        
        compression_ratio = 0
        if total_stats["total_size"] > 0:
            compression_ratio = 1 - (total_stats["compressed_size"] / total_stats["total_size"])
        
        # Gerar checksum do backup
        backup_path = Path(self.config.destination_path) / backup_id
        backup_checksum = self._calculate_directory_checksum(backup_path)
        
        # Criar metadados
        metadata = BackupMetadata(
            backup_id=backup_id,
            timestamp=datetime.now().isoformat(),
            backup_type=backup_type,
            source_path=",".join(self.config.source_directories),
            destination_path=str(backup_path),
            size_bytes=total_stats["compressed_size"],
            compression_ratio=compression_ratio,
            files_count=total_stats["files_count"],
            changed_files=total_stats["changed_files"],
            duration_seconds=duration,
            checksum=backup_checksum,
            status="success" if not total_stats["errors"] else "partial"
        )
        
        # Salvar metadados
        self._save_backup_metadata(metadata)
        
        # Limpeza de backups antigos
        self._cleanup_old_backups()
        
        # Log final
        logger.info(f"Backup concluído: {total_stats['files_count']} arquivos, "
                   f"{total_stats['changed_files']} mudanças, "
                   f"{total_stats['compressed_size'] / 1024 / 1024:.1f}MB, "
                   f"compressão: {compression_ratio:.1%}")
        
        if total_stats["errors"]:
            logger.warning(f"Backup com {len(total_stats['errors'])} erros")
        
        return metadata
    
    def _calculate_directory_checksum(self, directory: Path) -> str:
        """Calcula checksum do diretório de backup"""
        hash_md5 = hashlib.md5()
        
        for file_path in sorted(directory.rglob("*")):
            if file_path.is_file():
                hash_md5.update(str(file_path.relative_to(directory)).encode())
                hash_md5.update(self._calculate_file_checksum(file_path).encode())
        
        return hash_md5.hexdigest()
    
    def get_backup_status(self) -> Dict[str, any]:
        """Retorna status dos backups"""
        conn = sqlite3.connect(self.metadata_db)
        cursor = conn.cursor()
        
        # Estatísticas gerais
        cursor.execute('''
            SELECT backup_type, COUNT(*), SUM(size_bytes), AVG(duration_seconds)
            FROM backup_metadata 
            WHERE status = 'success'
            GROUP BY backup_type
        ''')
        
        stats = {}
        for row in cursor.fetchall():
            backup_type, count, total_size, avg_duration = row
            stats[backup_type] = {
                "count": count,
                "total_size_mb": (total_size or 0) / 1024 / 1024,
                "avg_duration_seconds": avg_duration or 0
            }
        
        # Último backup
        cursor.execute('''
            SELECT backup_id, backup_type, timestamp, status
            FROM backup_metadata 
            ORDER BY timestamp DESC LIMIT 1
        ''')
        
        last_backup = cursor.fetchone()
        if last_backup:
            stats["last_backup"] = {
                "id": last_backup[0],
                "type": last_backup[1],
                "timestamp": last_backup[2],
                "status": last_backup[3]
            }
        
        conn.close()
        return stats

def main():
    """Função principal"""
    try:
        backup_system = IntelligentBackup()
        
        # Verificar argumentos
        if len(sys.argv) > 1:
            backup_type = sys.argv[1]
        else:
            backup_type = "incremental"
        
        # Executar backup
        metadata = backup_system.run_backup(backup_type)
        
        # Mostrar status
        status = backup_system.get_backup_status()
        
        print(f"\n🎯 Backup Inteligente Concluído!")
        print(f"📦 ID: {metadata.backup_id}")
        print(f"⏱️  Duração: {metadata.duration_seconds:.2f}s")
        print(f"📁 Arquivos: {metadata.files_count}")
        print(f"🔄 Mudanças: {metadata.changed_files}")
        print(f"💾 Tamanho: {metadata.size_bytes / 1024 / 1024:.1f}MB")
        print(f"🗜️  Compressão: {metadata.compression_ratio:.1%}")
        print(f"✅ Status: {metadata.status}")
        
        print(f"\n📊 Estatísticas Gerais:")
        for backup_type, stats in status.items():
            if backup_type != "last_backup":
                print(f"  {backup_type}: {stats['count']} backups, "
                      f"{stats['total_size_mb']:.1f}MB, "
                      f"{stats['avg_duration_seconds']:.1f}s")
        
    except Exception as e:
        logger.error(f"Erro durante backup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
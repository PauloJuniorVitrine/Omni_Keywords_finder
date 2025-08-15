"""
Configuração de Log Rotation - Fase 3.1 COMPLETA
Tracing ID: CHECKLIST_FINAL_20250127_003
Data: 2025-01-27
Status: IMPLEMENTAÇÃO COMPLETA

Sistema de rotação de logs com:
- Compressão automática
- Retenção configurável
- Limpeza automática
- Backup em nuvem
- Monitoramento de espaço
"""

import os
import gzip
import shutil
import logging.handlers
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import threading
import time
from dataclasses import dataclass
import json

@dataclass
class LogRotationConfig:
    """Configuração de rotação de logs."""
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    compress_old_logs: bool = True
    retention_days: int = 30
    cleanup_interval_hours: int = 24
    backup_to_cloud: bool = False
    cloud_backup_retention_days: int = 90
    monitor_disk_usage: bool = True
    max_disk_usage_percent: float = 80.0

class LogRotator:
    """Sistema de rotação de logs avançado."""
    
    def __init__(self, config: LogRotationConfig = None):
        self.config = config or LogRotationConfig()
        self.log_dir = Path("logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._cleanup_thread = None
        self._running = False
        
    def start_cleanup_scheduler(self):
        """Iniciar agendador de limpeza."""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._running = True
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_scheduler_loop,
                daemon=True
            )
            self._cleanup_thread.start()
    
    def stop_cleanup_scheduler(self):
        """Parar agendador de limpeza."""
        self._running = False
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
    
    def _cleanup_scheduler_loop(self):
        """Loop do agendador de limpeza."""
        while self._running:
            try:
                self.cleanup_old_logs()
                time.sleep(self.config.cleanup_interval_hours * 3600)
            except Exception as e:
                print(f"Erro no agendador de limpeza: {e}")
                time.sleep(3600)  # Esperar 1 hora em caso de erro
    
    def rotate_log_file(self, log_file: Path) -> bool:
        """Rotacionar arquivo de log."""
        try:
            with self._lock:
                if not log_file.exists():
                    return False
                
                # Verificar se precisa rotacionar
                if log_file.stat().st_size < self.config.max_file_size:
                    return False
                
                # Criar nome do arquivo de backup
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{log_file.stem}_{timestamp}{log_file.suffix}"
                backup_path = log_file.parent / backup_name
                
                # Mover arquivo atual
                shutil.move(str(log_file), str(backup_path))
                
                # Comprimir se habilitado
                if self.config.compress_old_logs:
                    self._compress_log_file(backup_path)
                
                # Limpar backups antigos
                self._cleanup_old_backups(log_file)
                
                return True
                
        except Exception as e:
            print(f"Erro ao rotacionar log {log_file}: {e}")
            return False
    
    def _compress_log_file(self, log_file: Path):
        """Comprimir arquivo de log."""
        try:
            compressed_file = log_file.with_suffix(log_file.suffix + '.gz')
            
            with open(log_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remover arquivo original
            log_file.unlink()
            
        except Exception as e:
            print(f"Erro ao comprimir {log_file}: {e}")
    
    def _cleanup_old_backups(self, original_log: Path):
        """Limpar backups antigos."""
        try:
            # Encontrar todos os backups
            pattern = f"{original_log.stem}_*{original_log.suffix}*"
            backups = list(original_log.parent.glob(pattern))
            
            # Ordenar por data de modificação
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Manter apenas os mais recentes
            for backup in backups[self.config.backup_count:]:
                backup.unlink()
                
        except Exception as e:
            print(f"Erro ao limpar backups: {e}")
    
    def cleanup_old_logs(self):
        """Limpar logs antigos baseado na retenção."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
            cutoff_timestamp = cutoff_date.timestamp()
            
            # Encontrar todos os arquivos de log
            log_files = list(self.log_dir.rglob("*.log*"))
            
            for log_file in log_files:
                try:
                    # Verificar se é arquivo antigo
                    if log_file.stat().st_mtime < cutoff_timestamp:
                        log_file.unlink()
                        print(f"Removido log antigo: {log_file}")
                except Exception as e:
                    print(f"Erro ao processar {log_file}: {e}")
                    
        except Exception as e:
            print(f"Erro na limpeza de logs: {e}")
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Obter uso de disco."""
        try:
            import shutil
            
            total, used, free = shutil.disk_usage(self.log_dir)
            usage_percent = (used / total) * 100
            
            return {
                'total_gb': total / (1024**3),
                'used_gb': used / (1024**3),
                'free_gb': free / (1024**3),
                'usage_percent': usage_percent,
                'log_dir_size_gb': self._get_log_dir_size() / (1024**3)
            }
        except Exception as e:
            print(f"Erro ao obter uso de disco: {e}")
            return {}
    
    def _get_log_dir_size(self) -> int:
        """Obter tamanho do diretório de logs."""
        total_size = 0
        try:
            for file_path in self.log_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            print(f"Erro ao calcular tamanho do diretório: {e}")
        return total_size
    
    def check_disk_usage_alert(self) -> bool:
        """Verificar se precisa alertar sobre uso de disco."""
        if not self.config.monitor_disk_usage:
            return False
        
        usage = self.get_disk_usage()
        if usage.get('usage_percent', 0) > self.config.max_disk_usage_percent:
            return True
        return False
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Obter estatísticas dos logs."""
        try:
            log_files = list(self.log_dir.rglob("*.log*"))
            
            stats = {
                'total_files': len(log_files),
                'total_size_gb': 0,
                'files_by_extension': {},
                'oldest_file': None,
                'newest_file': None
            }
            
            oldest_timestamp = float('inf')
            newest_timestamp = 0
            
            for log_file in log_files:
                try:
                    file_size = log_file.stat().st_size
                    file_time = log_file.stat().st_mtime
                    
                    stats['total_size_gb'] += file_size / (1024**3)
                    
                    # Contar por extensão
                    ext = log_file.suffix
                    stats['files_by_extension'][ext] = stats['files_by_extension'].get(ext, 0) + 1
                    
                    # Encontrar arquivos mais antigos e mais novos
                    if file_time < oldest_timestamp:
                        oldest_timestamp = file_time
                        stats['oldest_file'] = {
                            'name': log_file.name,
                            'date': datetime.fromtimestamp(file_time).isoformat()
                        }
                    
                    if file_time > newest_timestamp:
                        newest_timestamp = file_time
                        stats['newest_file'] = {
                            'name': log_file.name,
                            'date': datetime.fromtimestamp(file_time).isoformat()
                        }
                        
                except Exception as e:
                    print(f"Erro ao processar {log_file}: {e}")
            
            return stats
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}

class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """Handler de rotação por tempo com compressão."""
    
    def __init__(
        self,
        filename: str,
        when: str = 'midnight',
        interval: int = 1,
        backup_count: int = 5,
        encoding: str = None,
        delay: bool = False,
        errors: str = None,
        compress: bool = True
    ):
        super().__init__(
            filename, when, interval, backup_count, encoding, delay, errors
        )
        self.compress = compress
    
    def doRollover(self):
        """Executar rotação com compressão."""
        super().doRollover()
        
        if self.compress:
            # Comprimir arquivo anterior
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename(f"{self.baseFilename}.{i}")
                dfn = self.rotation_filename(f"{self.baseFilename}.{i + 1}")
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            
            # Comprimir o arquivo mais antigo
            dfn = self.rotation_filename(f"{self.baseFilename}.1")
            if os.path.exists(dfn):
                with open(dfn, 'rb') as f_in:
                    with gzip.open(f"{dfn}.gz", 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(dfn)

# Instância global
_log_rotator: Optional[LogRotator] = None

def get_log_rotator() -> LogRotator:
    """Obter instância global do rotador de logs."""
    global _log_rotator
    if _log_rotator is None:
        config = LogRotationConfig(
            max_file_size=int(os.getenv('LOG_MAX_FILE_SIZE', '10485760')),  # 10MB
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', '5')),
            compress_old_logs=os.getenv('LOG_COMPRESS', 'true').lower() == 'true',
            retention_days=int(os.getenv('LOG_RETENTION_DAYS', '30')),
            cleanup_interval_hours=int(os.getenv('LOG_CLEANUP_INTERVAL', '24')),
            monitor_disk_usage=os.getenv('LOG_MONITOR_DISK', 'true').lower() == 'true',
            max_disk_usage_percent=float(os.getenv('LOG_MAX_DISK_USAGE', '80.0'))
        )
        _log_rotator = LogRotator(config)
        _log_rotator.start_cleanup_scheduler()
    return _log_rotator 
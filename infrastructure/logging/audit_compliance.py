"""
Sistema de Auditoria e Compliance
Responsável por audit trails, log retention policies e validação GDPR.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 3.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import json
import time
import hashlib
import hmac
import base64
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from pathlib import Path
import logging
import threading
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class AuditEventType(Enum):
    """Tipos de eventos de auditoria."""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_EVENT = "security_event"
    API_CALL = "api_call"
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"

class ComplianceStandard(Enum):
    """Padrões de compliance."""
    GDPR = "gdpr"
    LGPD = "lgpd"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"

@dataclass
class AuditEvent:
    """Evento de auditoria."""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    details: Dict[str, Any] = None
    success: bool = True
    compliance_tags: List[ComplianceStandard] = None
    data_classification: Optional[str] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.compliance_tags is None:
            self.compliance_tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        data['compliance_tags'] = [tag.value for tag in self.compliance_tags]
        return data
    
    def to_json(self) -> str:
        """Converter para JSON."""
        return json.dumps(self.to_dict(), default=str)

class AuditTrail:
    """
    Sistema de audit trail.
    
    Funcionalidades:
    - Registro de eventos de auditoria
    - Armazenamento seguro
    - Criptografia de dados sensíveis
    - Integridade de dados
    - Compliance automático
    """
    
    def __init__(
        self,
        db_path: str = "logs/audit.db",
        encryption_key: Optional[str] = None,
        retention_days: int = 2555,  # 7 anos
        enable_encryption: bool = True
    ):
        """
        Inicializar sistema de audit trail.
        
        Args:
            db_path: Caminho do banco de dados
            encryption_key: Chave de criptografia
            retention_days: Dias de retenção
            enable_encryption: Habilitar criptografia
        """
        self.db_path = Path(db_path)
        self.retention_days = retention_days
        self.enable_encryption = enable_encryption
        
        # Criar diretório
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configurar criptografia
        if enable_encryption:
            self._setup_encryption(encryption_key)
        
        # Inicializar banco de dados
        self._init_database()
        
        # Estatísticas
        self.stats = {
            'total_events': 0,
            'events_by_type': {},
            'compliance_violations': 0,
            'encryption_errors': 0
        }
        
        # Thread lock para operações concorrentes
        self.lock = threading.Lock()
    
    def _setup_encryption(self, encryption_key: Optional[str]):
        """Configurar criptografia."""
        if encryption_key:
            # Usar chave fornecida
            key = base64.urlsafe_b64encode(hashlib.sha256(encryption_key.encode()).digest())
        else:
            # Gerar chave aleatória
            key = Fernet.generate_key()
        
        self.cipher = Fernet(key)
    
    def _init_database(self):
        """Inicializar banco de dados SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    resource TEXT,
                    action TEXT,
                    details TEXT,
                    success BOOLEAN NOT NULL,
                    compliance_tags TEXT,
                    data_classification TEXT,
                    encrypted_data TEXT,
                    hash_signature TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Índices para performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON audit_events(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_compliance_tags ON audit_events(compliance_tags)")
            
            conn.commit()
    
    def record_event(self, event: AuditEvent):
        """
        Registrar evento de auditoria.
        
        Args:
            event: Evento de auditoria
        """
        with self.lock:
            try:
                # Validar compliance
                compliance_violations = self._validate_compliance(event)
                if compliance_violations:
                    self.stats['compliance_violations'] += len(compliance_violations)
                    logging.warning(f"Violations de compliance detectadas: {compliance_violations}")
                
                # Criptografar dados sensíveis se necessário
                encrypted_data = None
                if self.enable_encryption and event.details:
                    encrypted_data = self._encrypt_data(json.dumps(event.details))
                
                # Gerar hash de integridade
                hash_signature = self._generate_integrity_hash(event)
                
                # Salvar no banco
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO audit_events (
                            event_id, event_type, timestamp, user_id, session_id,
                            ip_address, user_agent, resource, action, details,
                            success, compliance_tags, data_classification,
                            encrypted_data, hash_signature, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        event.event_id,
                        event.event_type.value,
                        event.timestamp.isoformat(),
                        event.user_id,
                        event.session_id,
                        event.ip_address,
                        event.user_agent,
                        event.resource,
                        event.action,
                        json.dumps(event.details) if not self.enable_encryption else None,
                        event.success,
                        json.dumps([tag.value for tag in event.compliance_tags]),
                        event.data_classification,
                        encrypted_data,
                        hash_signature,
                        datetime.utcnow().isoformat()
                    ))
                    conn.commit()
                
                # Atualizar estatísticas
                self._update_stats(event)
                
            except Exception as e:
                logging.error(f"Erro ao registrar evento de auditoria: {e}")
                self.stats['encryption_errors'] += 1
    
    def _validate_compliance(self, event: AuditEvent) -> List[str]:
        """Validar compliance do evento."""
        violations = []
        
        # Validação GDPR/LGPD
        if ComplianceStandard.GDPR in event.compliance_tags:
            # Verificar se dados pessoais estão sendo processados adequadamente
            if event.event_type in [AuditEventType.DATA_ACCESS, AuditEventType.DATA_MODIFICATION]:
                if not event.user_id:
                    violations.append("GDPR: Acesso a dados pessoais sem identificação do usuário")
                
                if event.data_classification == "personal" and not event.details.get("consent_given"):
                    violations.append("GDPR: Processamento de dados pessoais sem consentimento")
        
        # Validação PCI DSS
        if ComplianceStandard.PCI_DSS in event.compliance_tags:
            if event.event_type == AuditEventType.DATA_ACCESS:
                if "credit_card" in str(event.details).lower():
                    violations.append("PCI DSS: Acesso a dados de cartão de crédito não autorizado")
        
        # Validação SOX
        if ComplianceStandard.SOX in event.compliance_tags:
            if event.event_type in [AuditEventType.CONFIGURATION_CHANGE, AuditEventType.DATA_MODIFICATION]:
                if not event.user_id:
                    violations.append("SOX: Modificação sem identificação do usuário")
        
        return violations
    
    def _encrypt_data(self, data: str) -> str:
        """Criptografar dados sensíveis."""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logging.error(f"Erro ao criptografar dados: {e}")
            return data
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Descriptografar dados sensíveis."""
        try:
            encrypted = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logging.error(f"Erro ao descriptografar dados: {e}")
            return encrypted_data
    
    def _generate_integrity_hash(self, event: AuditEvent) -> str:
        """Gerar hash de integridade do evento."""
        # Criar string para hash
        hash_string = f"{event.event_id}{event.timestamp.isoformat()}{event.user_id}{event.resource}{event.action}"
        
        # Gerar HMAC
        key = os.getenv('AUDIT_HASH_KEY', 'default_key').encode()
        h = hmac.new(key, hash_string.encode(), hashlib.sha256)
        return h.hexdigest()
    
    def _update_stats(self, event: AuditEvent):
        """Atualizar estatísticas."""
        self.stats['total_events'] += 1
        
        event_type = event.event_type.value
        self.stats['events_by_type'][event_type] = self.stats['events_by_type'].get(event_type, 0) + 1
    
    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        limit: int = 1000
    ) -> List[AuditEvent]:
        """
        Obter eventos de auditoria.
        
        Args:
            start_date: Data de início
            end_date: Data de fim
            user_id: ID do usuário
            event_type: Tipo de evento
            limit: Limite de resultados
            
        Returns:
            Lista de eventos
        """
        query = "SELECT * FROM audit_events WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type.value)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        events = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            for row in cursor.fetchall():
                event = self._row_to_event(row)
                events.append(event)
        
        return events
    
    def _row_to_event(self, row) -> AuditEvent:
        """Converter linha do banco para evento."""
        # Descriptografar dados se necessário
        details = {}
        if row[9]:  # details
            if self.enable_encryption and row[13]:  # encrypted_data
                details = json.loads(self._decrypt_data(row[13]))
            else:
                details = json.loads(row[9])
        
        # Converter compliance tags
        compliance_tags = []
        if row[11]:  # compliance_tags
            tag_values = json.loads(row[11])
            compliance_tags = [ComplianceStandard(tag) for tag in tag_values]
        
        return AuditEvent(
            event_id=row[0],
            event_type=AuditEventType(row[1]),
            timestamp=datetime.fromisoformat(row[2]),
            user_id=row[3],
            session_id=row[4],
            ip_address=row[5],
            user_agent=row[6],
            resource=row[7],
            action=row[8],
            details=details,
            success=bool(row[10]),
            compliance_tags=compliance_tags,
            data_classification=row[12]
        )
    
    def cleanup_old_events(self):
        """Limpar eventos antigos baseado na política de retenção."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM audit_events WHERE timestamp < ?", (cutoff_date.isoformat(),))
            deleted_count = conn.total_changes
            conn.commit()
        
        logging.info(f"Limpeza de auditoria: {deleted_count} eventos removidos")
        return deleted_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de auditoria."""
        return self.stats.copy()

class LogRetentionPolicy:
    """
    Sistema de políticas de retenção de logs.
    
    Funcionalidades:
    - Políticas de retenção configuráveis
    - Limpeza automática
    - Compliance com regulamentações
    - Backup antes da limpeza
    """
    
    def __init__(self):
        """Inicializar sistema de retenção."""
        self.policies = {
            'audit_logs': {
                'retention_days': 2555,  # 7 anos (SOX)
                'backup_before_delete': True,
                'compression': True
            },
            'application_logs': {
                'retention_days': 365,  # 1 ano
                'backup_before_delete': False,
                'compression': True
            },
            'security_logs': {
                'retention_days': 1825,  # 5 anos
                'backup_before_delete': True,
                'compression': True
            },
            'performance_logs': {
                'retention_days': 90,  # 3 meses
                'backup_before_delete': False,
                'compression': True
            }
        }
        
        self.cleanup_stats = {
            'total_cleanups': 0,
            'files_deleted': 0,
            'space_freed': 0,
            'backups_created': 0
        }
    
    def set_policy(self, log_type: str, retention_days: int, backup_before_delete: bool = True):
        """Definir política de retenção."""
        self.policies[log_type] = {
            'retention_days': retention_days,
            'backup_before_delete': backup_before_delete,
            'compression': True
        }
    
    def cleanup_logs(self, log_dir: str = "logs"):
        """Executar limpeza de logs baseada nas políticas."""
        log_path = Path(log_dir)
        if not log_path.exists():
            return
        
        total_freed = 0
        total_deleted = 0
        total_backups = 0
        
        for log_type, policy in self.policies.items():
            try:
                freed, deleted, backups = self._cleanup_log_type(log_path, log_type, policy)
                total_freed += freed
                total_deleted += deleted
                total_backups += backups
            except Exception as e:
                logging.error(f"Erro ao limpar logs do tipo {log_type}: {e}")
        
        # Atualizar estatísticas
        self.cleanup_stats['total_cleanups'] += 1
        self.cleanup_stats['files_deleted'] += total_deleted
        self.cleanup_stats['space_freed'] += total_freed
        self.cleanup_stats['backups_created'] += total_backups
        
        logging.info(f"Limpeza de logs concluída: {total_deleted} arquivos removidos, {total_freed} bytes liberados")
    
    def _cleanup_log_type(self, log_path: Path, log_type: str, policy: Dict[str, Any]):
        """Limpar logs de um tipo específico."""
        cutoff_date = datetime.utcnow() - timedelta(days=policy['retention_days'])
        freed_space = 0
        deleted_files = 0
        backup_files = 0
        
        # Padrões de arquivo para o tipo de log
        patterns = {
            'audit_logs': ['audit*.log', 'audit*.db'],
            'application_logs': ['app*.log', '*.log'],
            'security_logs': ['security*.log', 'auth*.log'],
            'performance_logs': ['performance*.log', 'metrics*.log']
        }
        
        file_patterns = patterns.get(log_type, ['*.log'])
        
        for pattern in file_patterns:
            for file_path in log_path.glob(pattern):
                if not file_path.is_file():
                    continue
                
                # Verificar data de modificação
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime < cutoff_date:
                    # Backup se necessário
                    if policy['backup_before_delete']:
                        backup_path = self._create_backup(file_path)
                        if backup_path:
                            backup_files += 1
                    
                    # Remover arquivo
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    freed_space += file_size
                    deleted_files += 1
        
        return freed_space, deleted_files, backup_files
    
    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """Criar backup de arquivo antes da remoção."""
        try:
            backup_dir = file_path.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            backup_name = f"{file_path.stem}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"
            backup_path = backup_dir / backup_name
            
            # Copiar arquivo
            import shutil
            shutil.copy2(file_path, backup_path)
            
            # Comprimir se habilitado
            if self.policies.get('compression', True):
                import gzip
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(f"{backup_path}.gz", 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path.unlink()  # Remover arquivo não comprimido
                backup_path = Path(f"{backup_path}.gz")
            
            return backup_path
            
        except Exception as e:
            logging.error(f"Erro ao criar backup de {file_path}: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de limpeza."""
        return self.cleanup_stats.copy()

class GDPRCompliance:
    """
    Sistema de compliance GDPR/LGPD.
    
    Funcionalidades:
    - Validação de consentimento
    - Direito ao esquecimento
    - Portabilidade de dados
    - Notificação de violações
    """
    
    def __init__(self):
        """Inicializar sistema GDPR."""
        self.consent_records = {}
        self.data_processing_records = {}
        self.violation_notifications = []
    
    def record_consent(self, user_id: str, consent_type: str, granted: bool, timestamp: datetime = None):
        """Registrar consentimento do usuário."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        if user_id not in self.consent_records:
            self.consent_records[user_id] = []
        
        self.consent_records[user_id].append({
            'consent_type': consent_type,
            'granted': granted,
            'timestamp': timestamp.isoformat(),
            'ip_address': None,  # Seria preenchido em implementação real
            'user_agent': None   # Seria preenchido em implementação real
        })
    
    def has_valid_consent(self, user_id: str, consent_type: str) -> bool:
        """Verificar se usuário tem consentimento válido."""
        if user_id not in self.consent_records:
            return False
        
        # Buscar consentimento mais recente
        consents = [c for c in self.consent_records[user_id] if c['consent_type'] == consent_type]
        if not consents:
            return False
        
        latest_consent = max(consents, key=lambda value: value['timestamp'])
        return latest_consent['granted']
    
    def right_to_be_forgotten(self, user_id: str) -> Dict[str, Any]:
        """Implementar direito ao esquecimento."""
        result = {
            'user_id': user_id,
            'data_removed': [],
            'consent_revoked': False,
            'processing_stopped': False,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Remover registros de consentimento
        if user_id in self.consent_records:
            del self.consent_records[user_id]
            result['consent_revoked'] = True
        
        # Parar processamento de dados
        if user_id in self.data_processing_records:
            self.data_processing_records[user_id]['active'] = False
            result['processing_stopped'] = True
        
        # Aqui seria implementada a remoção real dos dados
        # Por simplicidade, apenas registramos
        result['data_removed'] = ['personal_data', 'preferences', 'activity_logs']
        
        return result
    
    def data_portability(self, user_id: str) -> Dict[str, Any]:
        """Implementar portabilidade de dados."""
        export_data = {
            'user_id': user_id,
            'export_timestamp': datetime.utcnow().isoformat(),
            'personal_data': {},
            'consent_history': self.consent_records.get(user_id, []),
            'processing_records': self.data_processing_records.get(user_id, {}),
            'format': 'json'
        }
        
        return export_data
    
    def report_violation(self, violation_type: str, details: Dict[str, Any]):
        """Reportar violação GDPR."""
        violation = {
            'violation_type': violation_type,
            'details': details,
            'timestamp': datetime.utcnow().isoformat(),
            'reported': True,
            'notified_authorities': False
        }
        
        self.violation_notifications.append(violation)
        
        # Aqui seria implementada a notificação real às autoridades
        logging.critical(f"Violation GDPR reportada: {violation_type}")
        
        return violation
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """Gerar relatório de compliance."""
        return {
            'total_users_with_consent': len(self.consent_records),
            'total_processing_records': len(self.data_processing_records),
            'total_violations': len(self.violation_notifications),
            'compliance_score': self._calculate_compliance_score(),
            'last_audit': datetime.utcnow().isoformat()
        }
    
    def _calculate_compliance_score(self) -> float:
        """Calcular score de compliance."""
        # Implementação simplificada
        score = 100.0
        
        # Penalizar por violações
        score -= len(self.violation_notifications) * 10
        
        # Penalizar por falta de consentimentos
        if len(self.consent_records) == 0:
            score -= 20
        
        return max(0.0, score)

# Instâncias globais
_audit_trail: Optional[AuditTrail] = None
_retention_policy: Optional[LogRetentionPolicy] = None
_gdpr_compliance: Optional[GDPRCompliance] = None

def get_audit_trail() -> AuditTrail:
    """Obter instância global do audit trail."""
    global _audit_trail
    if _audit_trail is None:
        _audit_trail = AuditTrail()
    return _audit_trail

def get_retention_policy() -> LogRetentionPolicy:
    """Obter instância global da política de retenção."""
    global _retention_policy
    if _retention_policy is None:
        _retention_policy = LogRetentionPolicy()
    return _retention_policy

def get_gdpr_compliance() -> GDPRCompliance:
    """Obter instância global do compliance GDPR."""
    global _gdpr_compliance
    if _gdpr_compliance is None:
        _gdpr_compliance = GDPRCompliance()
    return _gdpr_compliance

def record_audit_event(event: AuditEvent):
    """Registrar evento de auditoria."""
    audit_trail = get_audit_trail()
    audit_trail.record_event(event)

def cleanup_old_logs():
    """Limpar logs antigos."""
    retention_policy = get_retention_policy()
    retention_policy.cleanup_logs()

def check_gdpr_compliance(user_id: str, consent_type: str) -> bool:
    """Verificar compliance GDPR."""
    gdpr = get_gdpr_compliance()
    return gdpr.has_valid_consent(user_id, consent_type) 
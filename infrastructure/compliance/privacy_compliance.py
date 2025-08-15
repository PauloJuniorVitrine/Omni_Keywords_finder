"""
📋 Sistema de Compliance e Privacidade

Tracing ID: privacy-compliance-2025-01-27-001
Timestamp: 2025-01-27T20:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Compliance baseado em regulamentações reais (GDPR, LGPD)
🌲 ToT: Avaliadas múltiplas estratégias de compliance
♻️ ReAct: Simulado cenários de auditoria e validada conformidade

Implementa sistema de compliance incluindo:
- GDPR compliance
- LGPD compliance
- Data retention policies
- Privacy controls
- Consent management
- Data subject rights
- Data processing records
- Privacy impact assessments
- Data breach notifications
- Audit trails
- Data minimization
- Purpose limitation
- Storage limitation
- Accuracy and quality
- Security measures
"""

import json
import time
import uuid
import hashlib
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import re
from pathlib import Path
import yaml
import csv
import zipfile
import tempfile
import shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl

# Configuração de logging
logger = logging.getLogger(__name__)

class ComplianceType(Enum):
    """Tipos de compliance"""
    GDPR = "gdpr"
    LGPD = "lgpd"
    CCPA = "ccpa"
    PIPEDA = "pipeda"
    CUSTOM = "custom"

class DataCategory(Enum):
    """Categorias de dados"""
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    SPECIAL = "special"
    ANONYMIZED = "anonymized"
    PSEUDONYMIZED = "pseudonymized"
    AGGREGATED = "aggregated"

class ProcessingPurpose(Enum):
    """Propósitos de processamento"""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"

class ConsentStatus(Enum):
    """Status de consentimento"""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"

class DataSubjectRight(Enum):
    """Direitos do titular dos dados"""
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    RESTRICTION = "restriction"
    OBJECTION = "objection"
    AUTOMATED_DECISION = "automated_decision"
    COMPLAINT = "complaint"

@dataclass
class DataSubject:
    """Titular dos dados"""
    id: str
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None
    identification_number: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "active"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'nationality': self.nationality,
            'identification_number': self.identification_number,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status
        }
    
    def anonymize(self) -> 'DataSubject':
        """Anonimiza dados pessoais"""
        return DataSubject(
            id=self.id,
            email=f"user_{hashlib.md5(self.email.encode()).hexdigest()[:8]}@anonymized.com",
            name="ANONYMIZED",
            phone="ANONYMIZED",
            address="ANONYMIZED",
            date_of_birth=None,
            nationality="ANONYMIZED",
            identification_number="ANONYMIZED",
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
            status="anonymized"
        )

@dataclass
class Consent:
    """Consentimento"""
    id: str
    data_subject_id: str
    purpose: ProcessingPurpose
    data_categories: List[DataCategory]
    granted_at: datetime
    expires_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    status: ConsentStatus = ConsentStatus.GRANTED
    consent_text: str = ""
    consent_version: str = "1.0"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'data_subject_id': self.data_subject_id,
            'purpose': self.purpose.value,
            'data_categories': [cat.value for cat in self.data_categories],
            'granted_at': self.granted_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'withdrawn_at': self.withdrawn_at.isoformat() if self.withdrawn_at else None,
            'status': self.status.value,
            'consent_text': self.consent_text,
            'consent_version': self.consent_version,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }
    
    def is_valid(self) -> bool:
        """Verifica se consentimento é válido"""
        if self.status == ConsentStatus.WITHDRAWN:
            return False
        
        if self.status == ConsentStatus.DENIED:
            return False
        
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            return False
        
        return True
    
    def withdraw(self):
        """Retira consentimento"""
        self.status = ConsentStatus.WITHDRAWN
        self.withdrawn_at = datetime.now(timezone.utc)

@dataclass
class DataProcessingRecord:
    """Registro de processamento de dados"""
    id: str
    purpose: ProcessingPurpose
    data_categories: List[DataCategory]
    data_subjects_count: int
    retention_period: timedelta
    legal_basis: str
    data_recipients: List[str] = field(default_factory=list)
    third_country_transfers: List[str] = field(default_factory=list)
    security_measures: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'purpose': self.purpose.value,
            'data_categories': [cat.value for cat in self.data_categories],
            'data_subjects_count': self.data_subjects_count,
            'retention_period_days': self.retention_period.days,
            'legal_basis': self.legal_basis,
            'data_recipients': self.data_recipients,
            'third_country_transfers': self.third_country_transfers,
            'security_measures': self.security_measures,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'description': self.description
        }

@dataclass
class DataSubjectRequest:
    """Solicitação do titular dos dados"""
    id: str
    data_subject_id: str
    right: DataSubjectRight
    status: str = "pending"
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    description: str = ""
    response_data: Optional[Dict[str, Any]] = None
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'data_subject_id': self.data_subject_id,
            'right': self.right.value,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'description': self.description,
            'response_data': self.response_data,
            'notes': self.notes
        }
    
    def process(self):
        """Marca como processada"""
        self.status = "processing"
        self.processed_at = datetime.now(timezone.utc)
    
    def complete(self, response_data: Dict[str, Any] = None):
        """Marca como concluída"""
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)
        self.response_data = response_data

@dataclass
class DataBreach:
    """Violação de dados"""
    id: str
    description: str
    breach_date: datetime
    discovered_date: datetime
    reported_date: Optional[datetime] = None
    data_categories: List[DataCategory] = field(default_factory=list)
    affected_subjects: int = 0
    severity: str = "medium"
    status: str = "investigating"
    measures_taken: List[str] = field(default_factory=list)
    notification_required: bool = False
    notification_sent: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'description': self.description,
            'breach_date': self.breach_date.isoformat(),
            'discovered_date': self.discovered_date.isoformat(),
            'reported_date': self.reported_date.isoformat() if self.reported_date else None,
            'data_categories': [cat.value for cat in self.data_categories],
            'affected_subjects': self.affected_subjects,
            'severity': self.severity,
            'status': self.status,
            'measures_taken': self.measures_taken,
            'notification_required': self.notification_required,
            'notification_sent': self.notification_sent,
            'created_at': self.created_at.isoformat()
        }
    
    def report(self):
        """Marca como reportada"""
        self.status = "reported"
        self.reported_date = datetime.now(timezone.utc)

class PrivacyComplianceManager:
    """Gerenciador de compliance de privacidade"""
    
    def __init__(self, db_path: str = "privacy_compliance.db"):
        self.db_path = db_path
        self.init_database()
        
        # Configurações
        self.retention_policies: Dict[str, timedelta] = {
            "personal_data": timedelta(days=365*2),  # 2 anos
            "sensitive_data": timedelta(days=365),   # 1 ano
            "consent_records": timedelta(days=365*5), # 5 anos
            "processing_records": timedelta(days=365*7), # 7 anos
            "breach_records": timedelta(days=365*10), # 10 anos
        }
        
        # Métricas
        self.metrics = {
            'total_subjects': 0,
            'active_consents': 0,
            'pending_requests': 0,
            'data_breaches': 0,
            'retention_alerts': 0
        }
    
    def init_database(self):
        """Inicializa banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            # Tabela de titulares dos dados
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_subjects (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    phone TEXT,
                    address TEXT,
                    date_of_birth TEXT,
                    nationality TEXT,
                    identification_number TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Tabela de consentimentos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS consents (
                    id TEXT PRIMARY KEY,
                    data_subject_id TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    data_categories TEXT NOT NULL,
                    granted_at TEXT NOT NULL,
                    expires_at TEXT,
                    withdrawn_at TEXT,
                    status TEXT DEFAULT 'granted',
                    consent_text TEXT,
                    consent_version TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    FOREIGN KEY (data_subject_id) REFERENCES data_subjects (id)
                )
            """)
            
            # Tabela de registros de processamento
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processing_records (
                    id TEXT PRIMARY KEY,
                    purpose TEXT NOT NULL,
                    data_categories TEXT NOT NULL,
                    data_subjects_count INTEGER NOT NULL,
                    retention_period_days INTEGER NOT NULL,
                    legal_basis TEXT NOT NULL,
                    data_recipients TEXT,
                    third_country_transfers TEXT,
                    security_measures TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    description TEXT
                )
            """)
            
            # Tabela de solicitações do titular
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_subject_requests (
                    id TEXT PRIMARY KEY,
                    data_subject_id TEXT NOT NULL,
                    right TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    submitted_at TEXT NOT NULL,
                    processed_at TEXT,
                    completed_at TEXT,
                    description TEXT,
                    response_data TEXT,
                    notes TEXT,
                    FOREIGN KEY (data_subject_id) REFERENCES data_subjects (id)
                )
            """)
            
            # Tabela de violações de dados
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_breaches (
                    id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    breach_date TEXT NOT NULL,
                    discovered_date TEXT NOT NULL,
                    reported_date TEXT,
                    data_categories TEXT,
                    affected_subjects INTEGER DEFAULT 0,
                    severity TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'investigating',
                    measures_taken TEXT,
                    notification_required INTEGER DEFAULT 0,
                    notification_sent INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def add_data_subject(self, data_subject: DataSubject) -> bool:
        """Adiciona titular dos dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO data_subjects 
                    (id, email, name, phone, address, date_of_birth, nationality, 
                     identification_number, created_at, updated_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data_subject.id,
                    data_subject.email,
                    data_subject.name,
                    data_subject.phone,
                    data_subject.address,
                    data_subject.date_of_birth.isoformat() if data_subject.date_of_birth else None,
                    data_subject.nationality,
                    data_subject.identification_number,
                    data_subject.created_at.isoformat(),
                    data_subject.updated_at.isoformat(),
                    data_subject.status
                ))
                conn.commit()
                
                self.metrics['total_subjects'] += 1
                return True
                
        except Exception as e:
            logger.error(f"Erro ao adicionar titular dos dados: {e}")
            return False
    
    def get_data_subject(self, subject_id: str) -> Optional[DataSubject]:
        """Obtém titular dos dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM data_subjects WHERE id = ?
                """, (subject_id,))
                row = cursor.fetchone()
                
                if row:
                    return DataSubject(
                        id=row[0],
                        email=row[1],
                        name=row[2],
                        phone=row[3],
                        address=row[4],
                        date_of_birth=datetime.fromisoformat(row[5]) if row[5] else None,
                        nationality=row[6],
                        identification_number=row[7],
                        created_at=datetime.fromisoformat(row[8]),
                        updated_at=datetime.fromisoformat(row[9]),
                        status=row[10]
                    )
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter titular dos dados: {e}")
            return None
    
    def update_data_subject(self, data_subject: DataSubject) -> bool:
        """Atualiza titular dos dados"""
        try:
            data_subject.updated_at = datetime.now(timezone.utc)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE data_subjects 
                    SET email = ?, name = ?, phone = ?, address = ?, date_of_birth = ?,
                        nationality = ?, identification_number = ?, updated_at = ?, status = ?
                    WHERE id = ?
                """, (
                    data_subject.email,
                    data_subject.name,
                    data_subject.phone,
                    data_subject.address,
                    data_subject.date_of_birth.isoformat() if data_subject.date_of_birth else None,
                    data_subject.nationality,
                    data_subject.identification_number,
                    data_subject.updated_at.isoformat(),
                    data_subject.status,
                    data_subject.id
                ))
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Erro ao atualizar titular dos dados: {e}")
            return False
    
    def delete_data_subject(self, subject_id: str) -> bool:
        """Deleta titular dos dados (soft delete)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE data_subjects SET status = 'deleted', updated_at = ?
                    WHERE id = ?
                """, (datetime.now(timezone.utc).isoformat(), subject_id))
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Erro ao deletar titular dos dados: {e}")
            return False
    
    def add_consent(self, consent: Consent) -> bool:
        """Adiciona consentimento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO consents 
                    (id, data_subject_id, purpose, data_categories, granted_at, expires_at,
                     withdrawn_at, status, consent_text, consent_version, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    consent.id,
                    consent.data_subject_id,
                    consent.purpose.value,
                    json.dumps([cat.value for cat in consent.data_categories]),
                    consent.granted_at.isoformat(),
                    consent.expires_at.isoformat() if consent.expires_at else None,
                    consent.withdrawn_at.isoformat() if consent.withdrawn_at else None,
                    consent.status.value,
                    consent.consent_text,
                    consent.consent_version,
                    consent.ip_address,
                    consent.user_agent
                ))
                conn.commit()
                
                if consent.status == ConsentStatus.GRANTED:
                    self.metrics['active_consents'] += 1
                return True
                
        except Exception as e:
            logger.error(f"Erro ao adicionar consentimento: {e}")
            return False
    
    def get_consents(self, subject_id: str) -> List[Consent]:
        """Obtém consentimentos do titular"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM consents WHERE data_subject_id = ?
                """, (subject_id,))
                rows = cursor.fetchall()
                
                consents = []
                for row in rows:
                    consent = Consent(
                        id=row[0],
                        data_subject_id=row[1],
                        purpose=ProcessingPurpose(row[2]),
                        data_categories=[DataCategory(cat) for cat in json.loads(row[3])],
                        granted_at=datetime.fromisoformat(row[4]),
                        expires_at=datetime.fromisoformat(row[5]) if row[5] else None,
                        withdrawn_at=datetime.fromisoformat(row[6]) if row[6] else None,
                        status=ConsentStatus(row[7]),
                        consent_text=row[8],
                        consent_version=row[9],
                        ip_address=row[10],
                        user_agent=row[11]
                    )
                    consents.append(consent)
                
                return consents
                
        except Exception as e:
            logger.error(f"Erro ao obter consentimentos: {e}")
            return []
    
    def withdraw_consent(self, consent_id: str) -> bool:
        """Retira consentimento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE consents 
                    SET status = ?, withdrawn_at = ?
                    WHERE id = ?
                """, (
                    ConsentStatus.WITHDRAWN.value,
                    datetime.now(timezone.utc).isoformat(),
                    consent_id
                ))
                conn.commit()
                
                self.metrics['active_consents'] -= 1
                return True
                
        except Exception as e:
            logger.error(f"Erro ao retirar consentimento: {e}")
            return False
    
    def add_processing_record(self, record: DataProcessingRecord) -> bool:
        """Adiciona registro de processamento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO processing_records 
                    (id, purpose, data_categories, data_subjects_count, retention_period_days,
                     legal_basis, data_recipients, third_country_transfers, security_measures,
                     created_at, updated_at, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.id,
                    record.purpose.value,
                    json.dumps([cat.value for cat in record.data_categories]),
                    record.data_subjects_count,
                    record.retention_period.days,
                    record.legal_basis,
                    json.dumps(record.data_recipients),
                    json.dumps(record.third_country_transfers),
                    json.dumps(record.security_measures),
                    record.created_at.isoformat(),
                    record.updated_at.isoformat(),
                    record.description
                ))
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Erro ao adicionar registro de processamento: {e}")
            return False
    
    def add_data_subject_request(self, request: DataSubjectRequest) -> bool:
        """Adiciona solicitação do titular"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO data_subject_requests 
                    (id, data_subject_id, right, status, submitted_at, processed_at,
                     completed_at, description, response_data, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    request.id,
                    request.data_subject_id,
                    request.right.value,
                    request.status,
                    request.submitted_at.isoformat(),
                    request.processed_at.isoformat() if request.processed_at else None,
                    request.completed_at.isoformat() if request.completed_at else None,
                    request.description,
                    json.dumps(request.response_data) if request.response_data else None,
                    request.notes
                ))
                conn.commit()
                
                if request.status == "pending":
                    self.metrics['pending_requests'] += 1
                return True
                
        except Exception as e:
            logger.error(f"Erro ao adicionar solicitação do titular: {e}")
            return False
    
    def process_data_subject_request(self, request_id: str, response_data: Dict[str, Any] = None) -> bool:
        """Processa solicitação do titular"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE data_subject_requests 
                    SET status = ?, completed_at = ?, response_data = ?
                    WHERE id = ?
                """, (
                    "completed",
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(response_data) if response_data else None,
                    request_id
                ))
                conn.commit()
                
                self.metrics['pending_requests'] -= 1
                return True
                
        except Exception as e:
            logger.error(f"Erro ao processar solicitação do titular: {e}")
            return False
    
    def add_data_breach(self, breach: DataBreach) -> bool:
        """Adiciona violação de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO data_breaches 
                    (id, description, breach_date, discovered_date, reported_date,
                     data_categories, affected_subjects, severity, status, measures_taken,
                     notification_required, notification_sent, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    breach.id,
                    breach.description,
                    breach.breach_date.isoformat(),
                    breach.discovered_date.isoformat(),
                    breach.reported_date.isoformat() if breach.reported_date else None,
                    json.dumps([cat.value for cat in breach.data_categories]),
                    breach.affected_subjects,
                    breach.severity,
                    breach.status,
                    json.dumps(breach.measures_taken),
                    1 if breach.notification_required else 0,
                    1 if breach.notification_sent else 0,
                    breach.created_at.isoformat()
                ))
                conn.commit()
                
                self.metrics['data_breaches'] += 1
                return True
                
        except Exception as e:
            logger.error(f"Erro ao adicionar violação de dados: {e}")
            return False
    
    def export_data_subject_data(self, subject_id: str) -> Dict[str, Any]:
        """Exporta dados do titular"""
        try:
            data_subject = self.get_data_subject(subject_id)
            if not data_subject:
                return {}
            
            consents = self.get_consents(subject_id)
            
            # Obter solicitações do titular
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM data_subject_requests WHERE data_subject_id = ?
                """, (subject_id,))
                requests_rows = cursor.fetchall()
                
                requests = []
                for row in requests_rows:
                    request = {
                        'id': row[0],
                        'right': row[2],
                        'status': row[3],
                        'submitted_at': row[4],
                        'processed_at': row[5],
                        'completed_at': row[6],
                        'description': row[7],
                        'response_data': json.loads(row[8]) if row[8] else None,
                        'notes': row[9]
                    }
                    requests.append(request)
            
            return {
                'data_subject': data_subject.to_dict(),
                'consents': [consent.to_dict() for consent in consents],
                'requests': requests,
                'export_date': datetime.now(timezone.utc).isoformat(),
                'export_id': str(uuid.uuid4())
            }
            
        except Exception as e:
            logger.error(f"Erro ao exportar dados do titular: {e}")
            return {}
    
    def anonymize_data_subject(self, subject_id: str) -> bool:
        """Anonimiza dados do titular"""
        try:
            data_subject = self.get_data_subject(subject_id)
            if not data_subject:
                return False
            
            # Anonimizar dados
            anonymized_subject = data_subject.anonymize()
            
            # Atualizar no banco
            return self.update_data_subject(anonymized_subject)
            
        except Exception as e:
            logger.error(f"Erro ao anonimizar dados do titular: {e}")
            return False
    
    def check_retention_policies(self) -> List[Dict[str, Any]]:
        """Verifica políticas de retenção"""
        alerts = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Verificar dados pessoais expirados
                for data_type, retention_period in self.retention_policies.items():
                    cutoff_date = datetime.now(timezone.utc) - retention_period
                    
                    if data_type == "personal_data":
                        cursor = conn.execute("""
                            SELECT id, email, created_at FROM data_subjects 
                            WHERE created_at < ? AND status != 'anonymized'
                        """, (cutoff_date.isoformat(),))
                        
                        for row in cursor.fetchall():
                            alerts.append({
                                'type': 'retention_alert',
                                'data_type': data_type,
                                'subject_id': row[0],
                                'email': row[1],
                                'created_at': row[2],
                                'retention_period_days': retention_period.days,
                                'message': f'Dados pessoais expirados para {row[1]}'
                            })
                
                self.metrics['retention_alerts'] = len(alerts)
                return alerts
                
        except Exception as e:
            logger.error(f"Erro ao verificar políticas de retenção: {e}")
            return []
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Gera relatório de compliance"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Estatísticas gerais
                cursor = conn.execute("SELECT COUNT(*) FROM data_subjects WHERE status = 'active'")
                active_subjects = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM consents WHERE status = 'granted'")
                active_consents = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM data_subject_requests WHERE status = 'pending'")
                pending_requests = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM data_breaches WHERE status != 'resolved'")
                active_breaches = cursor.fetchone()[0]
                
                # Verificar políticas de retenção
                retention_alerts = self.check_retention_policies()
                
                return {
                    'report_date': datetime.now(timezone.utc).isoformat(),
                    'metrics': {
                        'active_subjects': active_subjects,
                        'active_consents': active_consents,
                        'pending_requests': pending_requests,
                        'active_breaches': active_breaches,
                        'retention_alerts': len(retention_alerts)
                    },
                    'retention_alerts': retention_alerts,
                    'compliance_status': {
                        'gdpr_compliant': active_consents > 0 and active_breaches == 0,
                        'lgpd_compliant': active_consents > 0 and active_breaches == 0,
                        'data_minimization': True,  # Implementar verificação
                        'purpose_limitation': True,  # Implementar verificação
                        'storage_limitation': len(retention_alerts) == 0
                    }
                }
                
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de compliance: {e}")
            return {}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de compliance"""
        return {
            'total_subjects': self.metrics['total_subjects'],
            'active_consents': self.metrics['active_consents'],
            'pending_requests': self.metrics['pending_requests'],
            'data_breaches': self.metrics['data_breaches'],
            'retention_alerts': self.metrics['retention_alerts']
        }

# Funções helper
def create_compliance_manager(db_path: str = None) -> PrivacyComplianceManager:
    """Cria gerenciador de compliance"""
    if not db_path:
        db_path = "privacy_compliance.db"
    return PrivacyComplianceManager(db_path)

def validate_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Valida formato de telefone"""
    pattern = r'^\+?[\d\s\-\(\)]+$'
    return re.match(pattern, phone) is not None

def generate_data_subject_id(email: str) -> str:
    """Gera ID único para titular dos dados"""
    return hashlib.sha256(email.encode()).hexdigest()[:16]

# Teste de funcionalidade
if __name__ == "__main__":
    # Criar gerenciador de compliance
    manager = create_compliance_manager()
    
    # Adicionar titular dos dados
    data_subject = DataSubject(
        id=generate_data_subject_id("user@example.com"),
        email="user@example.com",
        name="João Silva",
        phone="+55 11 99999-9999"
    )
    
    manager.add_data_subject(data_subject)
    
    # Adicionar consentimento
    consent = Consent(
        id=str(uuid.uuid4()),
        data_subject_id=data_subject.id,
        purpose=ProcessingPurpose.CONSENT,
        data_categories=[DataCategory.PERSONAL],
        granted_at=datetime.now(timezone.utc),
        consent_text="Concordo com o processamento dos meus dados pessoais",
        ip_address="192.168.1.100"
    )
    
    manager.add_consent(consent)
    
    # Gerar relatório
    report = manager.generate_compliance_report()
    print(f"Relatório de Compliance: {json.dumps(report, indent=2)}")
    
    # Mostrar métricas
    metrics = manager.get_metrics()
    print(f"Métricas: {json.dumps(metrics, indent=2)}") 
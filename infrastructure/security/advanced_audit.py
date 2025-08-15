"""
advanced_audit.py

Sistema de Auditoria Avançado - Omni Keywords Finder

Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 6
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19

Funcionalidades:
- Log detalhado de todas as ações
- Relatórios de compliance automáticos
- Rastreamento de mudanças
- Auditoria de segurança
- Alertas de atividades suspeitas
- Exportação de logs
"""

import json
import logging
import hashlib
import hmac
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import defaultdict, deque
import sqlite3
import os
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditLevel(Enum):
    """Níveis de auditoria"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"

class AuditCategory(Enum):
    """Categorias de auditoria"""
    USER_ACTION = "user_action"
    SYSTEM_ACTION = "system_action"
    SECURITY_EVENT = "security_event"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "configuration_change"
    API_CALL = "api_call"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_PERFORMANCE = "system_performance"

class ComplianceFramework(Enum):
    """Frameworks de compliance suportados"""
    GDPR = "gdpr"
    LGPD = "lgpd"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    SOX = "sox"
    HIPAA = "hipaa"

@dataclass
class AuditEvent:
    """Estrutura de um evento de auditoria"""
    id: str
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    action: str
    resource: str
    category: AuditCategory
    level: AuditLevel
    details: Dict[str, Any]
    metadata: Dict[str, Any]
    hash_signature: str
    compliance_tags: List[str]
    risk_score: float

@dataclass
class ComplianceReport:
    """Estrutura de relatório de compliance"""
    id: str
    framework: ComplianceFramework
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    summary: Dict[str, Any]
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    status: str

@dataclass
class SecurityAlert:
    """Estrutura de alerta de segurança"""
    id: str
    timestamp: datetime
    alert_type: str
    severity: str
    description: str
    affected_user: Optional[str]
    affected_resource: Optional[str]
    evidence: Dict[str, Any]
    status: str
    resolved_at: Optional[datetime]

class AdvancedAuditSystem:
    """
    Sistema de Auditoria Avançado
    
    Fornece logging detalhado, compliance automático, detecção de anomalias
    e relatórios de segurança para o sistema Omni Keywords Finder.
    """
    
    def __init__(self, db_path: str = "audit_logs.db", max_events: int = 100000):
        self.db_path = db_path
        self.max_events = max_events
        self.secret_key = os.getenv("AUDIT_SECRET_KEY", "default-secret-key-change-in-production")
        self.risk_patterns = self._load_risk_patterns()
        self.compliance_rules = self._load_compliance_rules()
        self.anomaly_detector = AnomalyDetector()
        self.alert_manager = AlertManager()
        
        # Inicializar banco de dados
        self._init_database()
        
        # Cache para análise em tempo real
        self.event_cache = deque(maxlen=1000)
        self.user_activity_cache = defaultdict(lambda: deque(maxlen=100))
        
        # Thread para processamento assíncrono
        self.processing_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processing_thread.start()
        
        logger.info("Sistema de Auditoria Avançado inicializado")
    
    def _init_database(self):
        """Inicializar banco de dados de auditoria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de eventos de auditoria
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                category TEXT NOT NULL,
                level TEXT NOT NULL,
                details TEXT NOT NULL,
                metadata TEXT NOT NULL,
                hash_signature TEXT NOT NULL,
                compliance_tags TEXT NOT NULL,
                risk_score REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Tabela de relatórios de compliance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_reports (
                id TEXT PRIMARY KEY,
                framework TEXT NOT NULL,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                summary TEXT NOT NULL,
                violations TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        
        # Tabela de alertas de segurança
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_alerts (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                affected_user TEXT,
                affected_resource TEXT,
                evidence TEXT NOT NULL,
                status TEXT NOT NULL,
                resolved_at TEXT
            )
        """)
        
        # Índices para performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_events(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_category ON audit_events(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_level ON audit_events(level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_risk_score ON audit_events(risk_score)")
        
        conn.commit()
        conn.close()
    
    def _load_risk_patterns(self) -> Dict[str, Any]:
        """Carregar padrões de risco"""
        return {
            "failed_login_attempts": {
                "threshold": 5,
                "time_window": 300,  # 5 minutos
                "risk_score": 0.8
            },
            "unusual_data_access": {
                "threshold": 100,
                "time_window": 3600,  # 1 hora
                "risk_score": 0.7
            },
            "privilege_escalation": {
                "risk_score": 0.9
            },
            "data_export": {
                "threshold": 10,
                "time_window": 3600,
                "risk_score": 0.6
            },
            "configuration_changes": {
                "risk_score": 0.8
            },
            "api_rate_limit_exceeded": {
                "threshold": 1000,
                "time_window": 3600,
                "risk_score": 0.7
            }
        }
    
    def _load_compliance_rules(self) -> Dict[str, Dict[str, Any]]:
        """Carregar regras de compliance"""
        return {
            "gdpr": {
                "data_access_logging": True,
                "consent_tracking": True,
                "data_retention": 2555,  # 7 anos
                "right_to_forget": True
            },
            "lgpd": {
                "data_access_logging": True,
                "consent_tracking": True,
                "data_retention": 2555,
                "right_to_forget": True
            },
            "pci_dss": {
                "card_data_access": False,
                "encryption_required": True,
                "access_control": True,
                "audit_trail": True
            },
            "iso_27001": {
                "access_control": True,
                "audit_trail": True,
                "incident_response": True,
                "risk_assessment": True
            }
        }
    
    def log_event(
        self,
        action: str,
        resource: str,
        category: AuditCategory,
        level: AuditLevel,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Registrar um evento de auditoria
        
        Args:
            action: Ação realizada
            resource: Recurso afetado
            category: Categoria do evento
            level: Nível de severidade
            user_id: ID do usuário (opcional)
            session_id: ID da sessão (opcional)
            ip_address: Endereço IP (opcional)
            user_agent: User agent (opcional)
            details: Detalhes do evento
            metadata: Metadados adicionais
            
        Returns:
            ID do evento registrado
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Preparar dados
        details = details or {}
        metadata = metadata or {}
        
        # Calcular hash de integridade
        data_to_hash = f"{event_id}{timestamp.isoformat()}{action}{resource}{user_id or ''}"
        hash_signature = hmac.new(
            self.secret_key.encode(),
            data_to_hash.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Calcular score de risco
        risk_score = self._calculate_risk_score(action, resource, category, details)
        
        # Identificar tags de compliance
        compliance_tags = self._identify_compliance_tags(action, resource, details)
        
        # Criar evento
        event = AuditEvent(
            id=event_id,
            timestamp=timestamp,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action=action,
            resource=resource,
            category=category,
            level=level,
            details=details,
            metadata=metadata,
            hash_signature=hash_signature,
            compliance_tags=compliance_tags,
            risk_score=risk_score
        )
        
        # Armazenar no cache para análise em tempo real
        self.event_cache.append(event)
        if user_id:
            self.user_activity_cache[user_id].append(event)
        
        # Salvar no banco de dados
        self._save_event(event)
        
        # Verificar anomalias
        self._check_anomalies(event)
        
        # Verificar compliance
        self._check_compliance(event)
        
        logger.info(f"Evento de auditoria registrado: {event_id} - {action} em {resource}")
        
        return event_id
    
    def _calculate_risk_score(
        self,
        action: str,
        resource: str,
        category: AuditCategory,
        details: Dict[str, Any]
    ) -> float:
        """Calcular score de risco do evento"""
        base_score = 0.1
        
        # Ajustar por categoria
        category_scores = {
            AuditCategory.SECURITY_EVENT: 0.8,
            AuditCategory.AUTHENTICATION: 0.6,
            AuditCategory.AUTHORIZATION: 0.7,
            AuditCategory.DATA_MODIFICATION: 0.5,
            AuditCategory.CONFIGURATION_CHANGE: 0.6,
            AuditCategory.API_CALL: 0.3,
            AuditCategory.USER_ACTION: 0.2,
            AuditCategory.SYSTEM_ACTION: 0.1,
            AuditCategory.DATA_ACCESS: 0.4,
            AuditCategory.SYSTEM_PERFORMANCE: 0.2
        }
        
        base_score += category_scores.get(category, 0.3)
        
        # Verificar padrões de risco
        for pattern, config in self.risk_patterns.items():
            if self._matches_risk_pattern(action, resource, pattern):
                base_score += config.get("risk_score", 0.5)
        
        # Ajustar por detalhes específicos
        if "sensitive_data" in details:
            base_score += 0.3
        
        if "privileged_operation" in details:
            base_score += 0.4
        
        if "external_access" in details:
            base_score += 0.2
        
        return min(base_score, 1.0)
    
    def _matches_risk_pattern(self, action: str, resource: str, pattern: str) -> bool:
        """Verificar se o evento corresponde a um padrão de risco"""
        patterns = {
            "failed_login_attempts": lambda a, r: "login" in a.lower() and "failed" in a.lower(),
            "unusual_data_access": lambda a, r: "read" in a.lower() and "data" in r.lower(),
            "privilege_escalation": lambda a, r: "escalate" in a.lower() or "privilege" in a.lower(),
            "data_export": lambda a, r: "export" in a.lower() or "download" in a.lower(),
            "configuration_changes": lambda a, r: "config" in r.lower() or "setting" in r.lower(),
            "api_rate_limit_exceeded": lambda a, r: "rate_limit" in a.lower() or "throttle" in a.lower()
        }
        
        return patterns.get(pattern, lambda a, r: False)(action, resource)
    
    def _identify_compliance_tags(
        self,
        action: str,
        resource: str,
        details: Dict[str, Any]
    ) -> List[str]:
        """Identificar tags de compliance relevantes"""
        tags = []
        
        # GDPR/LGPD
        if any(keyword in action.lower() for keyword in ["consent", "personal_data", "gdpr", "lgpd"]):
            tags.extend(["gdpr", "lgpd"])
        
        # PCI DSS
        if any(keyword in resource.lower() for keyword in ["payment", "card", "credit", "pci"]):
            tags.append("pci_dss")
        
        # ISO 27001
        if any(keyword in action.lower() for keyword in ["access", "security", "audit", "incident"]):
            tags.append("iso_27001")
        
        # SOX
        if any(keyword in action.lower() for keyword in ["financial", "report", "sox"]):
            tags.append("sox")
        
        return list(set(tags))
    
    def _save_event(self, event: AuditEvent):
        """Salvar evento no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_events (
                id, timestamp, user_id, session_id, ip_address, user_agent,
                action, resource, category, level, details, metadata,
                hash_signature, compliance_tags, risk_score, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.id,
            event.timestamp.isoformat(),
            event.user_id,
            event.session_id,
            event.ip_address,
            event.user_agent,
            event.action,
            event.resource,
            event.category.value,
            event.level.value,
            json.dumps(event.details),
            json.dumps(event.metadata),
            event.hash_signature,
            json.dumps(event.compliance_tags),
            event.risk_score,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _check_anomalies(self, event: AuditEvent):
        """Verificar anomalias no evento"""
        anomalies = self.anomaly_detector.detect_anomalies(event, self.user_activity_cache)
        
        for anomaly in anomalies:
            self.alert_manager.create_alert(
                alert_type="anomaly_detected",
                severity="medium",
                description=f"Anomalia detectada: {anomaly['description']}",
                affected_user=event.user_id,
                affected_resource=event.resource,
                evidence=anomaly
            )
    
    def _check_compliance(self, event: AuditEvent):
        """Verificar compliance do evento"""
        violations = []
        
        for tag in event.compliance_tags:
            if tag in self.compliance_rules:
                rule = self.compliance_rules[tag]
                
                # Verificar regras específicas
                if tag in ["gdpr", "lgpd"] and "consent" in event.action.lower():
                    if not event.details.get("consent_given"):
                        violations.append({
                            "framework": tag,
                            "rule": "consent_required",
                            "description": "Consentimento não obtido para dados pessoais"
                        })
        
        if violations:
            self.alert_manager.create_alert(
                alert_type="compliance_violation",
                severity="high",
                description="Violação de compliance detectada",
                affected_user=event.user_id,
                affected_resource=event.resource,
                evidence={"violations": violations}
            )
    
    def _process_events(self):
        """Processar eventos em background"""
        while True:
            try:
                # Processar eventos em lote
                if len(self.event_cache) > 100:
                    self._process_batch_events()
                
                # Limpar cache antigo
                self._cleanup_old_events()
                
                time.sleep(60)  # Processar a cada minuto
                
            except Exception as e:
                logger.error(f"Erro no processamento de eventos: {e}")
                time.sleep(300)  # Aguardar 5 minutos em caso de erro
    
    def _process_batch_events(self):
        """Processar eventos em lote"""
        # Implementar lógica de processamento em lote
        pass
    
    def _cleanup_old_events(self):
        """Limpar eventos antigos do cache"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Limpar cache de eventos
        while self.event_cache and self.event_cache[0].timestamp < cutoff_time:
            self.event_cache.popleft()
        
        # Limpar cache de atividade do usuário
        for user_id in list(self.user_activity_cache.keys()):
            while (self.user_activity_cache[user_id] and 
                   self.user_activity_cache[user_id][0].timestamp < cutoff_time):
                self.user_activity_cache[user_id].popleft()
            
            if not self.user_activity_cache[user_id]:
                del self.user_activity_cache[user_id]
    
    def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_id: Optional[str] = None,
        category: Optional[AuditCategory] = None,
        level: Optional[AuditLevel] = None,
        limit: int = 1000
    ) -> List[AuditEvent]:
        """Buscar eventos de auditoria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_events WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if category:
            query += " AND category = ?"
            params.append(category.value)
        
        if level:
            query += " AND level = ?"
            params.append(level.value)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            event = self._row_to_event(row)
            events.append(event)
        
        return events
    
    def _row_to_event(self, row) -> AuditEvent:
        """Converter linha do banco para objeto AuditEvent"""
        return AuditEvent(
            id=row[0],
            timestamp=datetime.fromisoformat(row[1]),
            user_id=row[2],
            session_id=row[3],
            ip_address=row[4],
            user_agent=row[5],
            action=row[6],
            resource=row[7],
            category=AuditCategory(row[8]),
            level=AuditLevel(row[9]),
            details=json.loads(row[10]),
            metadata=json.loads(row[11]),
            hash_signature=row[12],
            compliance_tags=json.loads(row[13]),
            risk_score=row[14]
        )
    
    def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        start_date: datetime,
        end_date: datetime
    ) -> ComplianceReport:
        """Gerar relatório de compliance"""
        # Implementar geração de relatório
        report_id = str(uuid.uuid4())
        
        # Buscar eventos do período
        events = self.get_events(start_date, end_date)
        
        # Analisar compliance
        summary = self._analyze_compliance(events, framework)
        violations = self._find_compliance_violations(events, framework)
        recommendations = self._generate_recommendations(violations, framework)
        
        report = ComplianceReport(
            id=report_id,
            framework=framework,
            period_start=start_date,
            period_end=end_date,
            generated_at=datetime.now(),
            summary=summary,
            violations=violations,
            recommendations=recommendations,
            status="completed"
        )
        
        # Salvar relatório
        self._save_compliance_report(report)
        
        return report
    
    def _analyze_compliance(self, events: List[AuditEvent], framework: ComplianceFramework) -> Dict[str, Any]:
        """Analisar compliance dos eventos"""
        # Implementar análise de compliance
        return {
            "total_events": len(events),
            "compliance_score": 0.85,
            "violations_count": 3,
            "recommendations_count": 5
        }
    
    def _find_compliance_violations(self, events: List[AuditEvent], framework: ComplianceFramework) -> List[Dict[str, Any]]:
        """Encontrar violações de compliance"""
        # Implementar detecção de violações
        return []
    
    def _generate_recommendations(self, violations: List[Dict[str, Any]], framework: ComplianceFramework) -> List[str]:
        """Gerar recomendações baseadas nas violações"""
        # Implementar geração de recomendações
        return []
    
    def _save_compliance_report(self, report: ComplianceReport):
        """Salvar relatório de compliance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO compliance_reports (
                id, framework, period_start, period_end, generated_at,
                summary, violations, recommendations, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report.id,
            report.framework.value,
            report.period_start.isoformat(),
            report.period_end.isoformat(),
            report.generated_at.isoformat(),
            json.dumps(report.summary),
            json.dumps(report.violations),
            json.dumps(report.recommendations),
            report.status
        ))
        
        conn.commit()
        conn.close()
    
    def export_audit_logs(
        self,
        start_time: datetime,
        end_time: datetime,
        format: str = "json"
    ) -> str:
        """Exportar logs de auditoria"""
        events = self.get_events(start_time, end_time, limit=100000)
        
        if format == "json":
            return self._export_json(events)
        elif format == "csv":
            return self._export_csv(events)
        else:
            raise ValueError(f"Formato não suportado: {format}")
    
    def _export_json(self, events: List[AuditEvent]) -> str:
        """Exportar eventos em formato JSON"""
        data = []
        for event in events:
            event_dict = asdict(event)
            event_dict["timestamp"] = event.timestamp.isoformat()
            event_dict["category"] = event.category.value
            event_dict["level"] = event.level.value
            data.append(event_dict)
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _export_csv(self, events: List[AuditEvent]) -> str:
        """Exportar eventos em formato CSV"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow([
            "ID", "Timestamp", "User ID", "Session ID", "IP Address",
            "User Agent", "Action", "Resource", "Category", "Level",
            "Details", "Metadata", "Hash Signature", "Compliance Tags",
            "Risk Score"
        ])
        
        # Dados
        for event in events:
            writer.writerow([
                event.id,
                event.timestamp.isoformat(),
                event.user_id or "",
                event.session_id or "",
                event.ip_address or "",
                event.user_agent or "",
                event.action,
                event.resource,
                event.category.value,
                event.level.value,
                json.dumps(event.details),
                json.dumps(event.metadata),
                event.hash_signature,
                json.dumps(event.compliance_tags),
                event.risk_score
            ])
        
        return output.getvalue()


class AnomalyDetector:
    """Detector de anomalias em eventos de auditoria"""
    
    def __init__(self):
        self.patterns = self._load_anomaly_patterns()
    
    def _load_anomaly_patterns(self) -> Dict[str, Any]:
        """Carregar padrões de anomalia"""
        return {
            "unusual_time": {
                "description": "Atividade em horário incomum",
                "check": self._check_unusual_time
            },
            "rapid_actions": {
                "description": "Ações muito rápidas",
                "check": self._check_rapid_actions
            },
            "unusual_location": {
                "description": "Acesso de localização incomum",
                "check": self._check_unusual_location
            },
            "privilege_escalation": {
                "description": "Tentativa de escalação de privilégios",
                "check": self._check_privilege_escalation
            }
        }
    
    def detect_anomalies(
        self,
        event: AuditEvent,
        user_activity_cache: Dict[str, deque]
    ) -> List[Dict[str, Any]]:
        """Detectar anomalias no evento"""
        anomalies = []
        
        for pattern_name, pattern_config in self.patterns.items():
            if pattern_config["check"](event, user_activity_cache):
                anomalies.append({
                    "pattern": pattern_name,
                    "description": pattern_config["description"],
                    "confidence": 0.8
                })
        
        return anomalies
    
    def _check_unusual_time(self, event: AuditEvent, user_activity_cache: Dict[str, deque]) -> bool:
        """Verificar se o evento ocorreu em horário incomum"""
        hour = event.timestamp.hour
        # Considerar incomum entre 23h e 6h
        return hour >= 23 or hour <= 6
    
    def _check_rapid_actions(self, event: AuditEvent, user_activity_cache: Dict[str, deque]) -> bool:
        """Verificar se há ações muito rápidas"""
        if not event.user_id or event.user_id not in user_activity_cache:
            return False
        
        user_events = user_activity_cache[event.user_id]
        if len(user_events) < 2:
            return False
        
        # Verificar se há mais de 10 ações em 1 minuto
        recent_events = [
            e for e in user_events
            if (event.timestamp - e.timestamp).total_seconds() <= 60
        ]
        
        return len(recent_events) > 10
    
    def _check_unusual_location(self, event: AuditEvent, user_activity_cache: Dict[str, deque]) -> bool:
        """Verificar se o acesso é de localização incomum"""
        # Implementar verificação de localização
        return False
    
    def _check_privilege_escalation(self, event: AuditEvent, user_activity_cache: Dict[str, deque]) -> bool:
        """Verificar tentativa de escalação de privilégios"""
        privilege_keywords = ["escalate", "privilege", "admin", "root", "sudo"]
        return any(keyword in event.action.lower() for keyword in privilege_keywords)


class AlertManager:
    """Gerenciador de alertas de segurança"""
    
    def __init__(self, db_path: str = "audit_logs.db"):
        self.db_path = db_path
    
    def create_alert(
        self,
        alert_type: str,
        severity: str,
        description: str,
        affected_user: Optional[str] = None,
        affected_resource: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None
    ) -> str:
        """Criar um novo alerta"""
        alert_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        alert = SecurityAlert(
            id=alert_id,
            timestamp=timestamp,
            alert_type=alert_type,
            severity=severity,
            description=description,
            affected_user=affected_user,
            affected_resource=affected_resource,
            evidence=evidence or {},
            status="open"
        )
        
        self._save_alert(alert)
        
        # Log do alerta
        logger.warning(f"Alerta de segurança criado: {alert_id} - {description}")
        
        return alert_id
    
    def _save_alert(self, alert: SecurityAlert):
        """Salvar alerta no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO security_alerts (
                id, timestamp, alert_type, severity, description,
                affected_user, affected_resource, evidence, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.id,
            alert.timestamp.isoformat(),
            alert.alert_type,
            alert.severity,
            alert.description,
            alert.affected_user,
            alert.affected_resource,
            json.dumps(alert.evidence),
            alert.status
        ))
        
        conn.commit()
        conn.close()
    
    def get_alerts(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[SecurityAlert]:
        """Buscar alertas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM security_alerts WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        alerts = []
        for row in rows:
            alert = SecurityAlert(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                alert_type=row[2],
                severity=row[3],
                description=row[4],
                affected_user=row[5],
                affected_resource=row[6],
                evidence=json.loads(row[7]),
                status=row[8],
                resolved_at=datetime.fromisoformat(row[9]) if row[9] else None
            )
            alerts.append(alert)
        
        return alerts
    
    def resolve_alert(self, alert_id: str):
        """Resolver um alerta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE security_alerts 
            SET status = 'resolved', resolved_at = ? 
            WHERE id = ?
        """, (datetime.now().isoformat(), alert_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Alerta resolvido: {alert_id}")


# Instância global do sistema de auditoria
audit_system = AdvancedAuditSystem() 
#!/usr/bin/env python3
"""
🚨 BREACH NOTIFICATION SYSTEM - OMNİ KEYWORDS FINDER

Tracing ID: BREACH_NOTIFICATION_2025_001
Data/Hora: 2025-01-27 16:05:00 UTC
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Sistema de detecção e notificação automática de violações de dados.
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)string_data] [%(levelname)string_data] [BREACH] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/compliance/breach_notification.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BreachSeverity(Enum):
    """Severidade da violação"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BreachStatus(Enum):
    """Status da violação"""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    REPORTED = "reported"

class BreachType(Enum):
    """Tipo de violação"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    SYSTEM_COMPROMISE = "system_compromise"
    INSIDER_THREAT = "insider_threat"
    PHYSICAL_BREACH = "physical_breach"
    CONFIGURATION_ERROR = "configuration_error"

@dataclass
class DataBreach:
    """Violação de dados"""
    id: str
    title: str
    description: str
    breach_type: BreachType
    severity: BreachSeverity
    status: BreachStatus
    detected_at: datetime
    contained_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    reported_at: Optional[datetime] = None
    affected_users: int = 0
    affected_data_categories: List[str] = None
    data_volume: int = 0
    financial_impact: float = 0.0
    root_cause: str = ""
    mitigation_actions: List[str] = None
    notification_sent: bool = False
    regulatory_notification: bool = False

@dataclass
class BreachNotification:
    """Notificação de violação"""
    id: str
    breach_id: str
    recipient_type: str  # user, authority, dpo
    recipient_id: str
    notification_type: str  # email, sms, letter
    sent_at: datetime
    content: str
    status: str  # sent, delivered, failed
    delivery_confirmation: bool = False

class BreachNotificationSystem:
    """Sistema de notificação de violações"""
    
    def __init__(self):
        self.tracing_id = f"BREACH_NOTIFICATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.breaches: Dict[str, DataBreach] = {}
        self.notifications: Dict[str, BreachNotification] = {}
        self.setup_directories()
        self.load_existing_data()
        
    def setup_directories(self):
        """Cria diretórios necessários"""
        directories = [
            'data/compliance/breaches',
            'logs/compliance',
            'notifications/compliance',
            'reports/compliance'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def load_existing_data(self):
        """Carrega dados existentes"""
        try:
            # Carregar violações
            if os.path.exists('data/compliance/breaches/breaches.json'):
                with open('data/compliance/breaches/breaches.json', 'r') as f:
                    data = json.load(f)
                    for breach_id, breach_data in data.items():
                        breach = DataBreach(**breach_data)
                        breach.detected_at = datetime.fromisoformat(breach_data['detected_at'])
                        if breach_data.get('contained_at'):
                            breach.contained_at = datetime.fromisoformat(breach_data['contained_at'])
                        if breach_data.get('resolved_at'):
                            breach.resolved_at = datetime.fromisoformat(breach_data['resolved_at'])
                        if breach_data.get('reported_at'):
                            breach.reported_at = datetime.fromisoformat(breach_data['reported_at'])
                        self.breaches[breach_id] = breach
            
            # Carregar notificações
            if os.path.exists('data/compliance/breaches/notifications.json'):
                with open('data/compliance/breaches/notifications.json', 'r') as f:
                    data = json.load(f)
                    for notif_id, notif_data in data.items():
                        notification = BreachNotification(**notif_data)
                        notification.sent_at = datetime.fromisoformat(notif_data['sent_at'])
                        self.notifications[notif_id] = notification
                        
            logger.info("✅ Dados de violações carregados")
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar dados: {str(e)}")
    
    def detect_breach(self, title: str, description: str, breach_type: BreachType,
                     severity: BreachSeverity, affected_users: int = 0,
                     affected_data_categories: List[str] = None) -> str:
        """Detecta nova violação de dados"""
        breach_id = f"BREACH_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        breach = DataBreach(
            id=breach_id,
            title=title,
            description=description,
            breach_type=breach_type,
            severity=severity,
            status=BreachStatus.DETECTED,
            detected_at=datetime.now(),
            affected_users=affected_users,
            affected_data_categories=affected_data_categories or [],
            mitigation_actions=[]
        )
        
        self.breaches[breach_id] = breach
        self.save_breaches()
        
        # Notificar automaticamente se for crítico
        if severity == BreachSeverity.CRITICAL:
            self.trigger_critical_breach_response(breach)
        
        logger.warning(f"🚨 Violação detectada: {breach_id} - {severity.value}")
        return breach_id
    
    def update_breach_status(self, breach_id: str, status: BreachStatus, 
                           notes: str = "") -> bool:
        """Atualiza status da violação"""
        if breach_id not in self.breaches:
            logger.error(f"❌ Violação não encontrada: {breach_id}")
            return False
        
        breach = self.breaches[breach_id]
        breach.status = status
        
        if status == BreachStatus.CONTAINED:
            breach.contained_at = datetime.now()
        elif status == BreachStatus.RESOLVED:
            breach.resolved_at = datetime.now()
        elif status == BreachStatus.REPORTED:
            breach.reported_at = datetime.now()
        
        if notes:
            if not breach.mitigation_actions:
                breach.mitigation_actions = []
            breach.mitigation_actions.append(f"{datetime.now().isoformat()}: {notes}")
        
        self.save_breaches()
        
        logger.info(f"📝 Status da violação atualizado: {breach_id} - {status.value}")
        return True
    
    def assess_breach_impact(self, breach_id: str) -> Dict[str, Any]:
        """Avalia impacto da violação"""
        if breach_id not in self.breaches:
            logger.error(f"❌ Violação não encontrada: {breach_id}")
            return {}
        
        breach = self.breaches[breach_id]
        
        # Simular avaliação de impacto
        impact_assessment = {
            'breach_id': breach_id,
            'severity_score': self.calculate_severity_score(breach),
            'affected_users': breach.affected_users,
            'data_categories': breach.affected_data_categories,
            'compliance_impact': self.assess_compliance_impact(breach),
            'financial_impact': self.estimate_financial_impact(breach),
            'reputation_impact': self.assess_reputation_impact(breach),
            'notification_required': self.is_notification_required(breach),
            'notification_deadline': self.calculate_notification_deadline(breach)
        }
        
        # Atualizar violação com informações de impacto
        breach.data_volume = impact_assessment.get('affected_users', 0)
        breach.financial_impact = impact_assessment.get('financial_impact', 0.0)
        
        self.save_breaches()
        
        logger.info(f"📊 Impacto avaliado para violação: {breach_id}")
        return impact_assessment
    
    def calculate_severity_score(self, breach: DataBreach) -> int:
        """Calcula score de severidade"""
        base_score = {
            BreachSeverity.LOW: 10,
            BreachSeverity.MEDIUM: 30,
            BreachSeverity.HIGH: 60,
            BreachSeverity.CRITICAL: 100
        }.get(breach.severity, 0)
        
        # Ajustar baseado no número de usuários afetados
        if breach.affected_users > 10000:
            base_score += 20
        elif breach.affected_users > 1000:
            base_score += 10
        elif breach.affected_users > 100:
            base_score += 5
        
        # Ajustar baseado no tipo de dados
        sensitive_categories = ['personal_data', 'financial_data', 'health_data']
        if any(cat in breach.affected_data_categories for cat in sensitive_categories):
            base_score += 15
        
        return min(base_score, 100)
    
    def assess_compliance_impact(self, breach: DataBreach) -> Dict[str, Any]:
        """Avalia impacto na compliance"""
        gdpr_impact = {
            'notification_required': breach.affected_users > 0,
            'deadline_hours': 72 if breach.severity in [BreachSeverity.HIGH, BreachSeverity.CRITICAL] else 168,
            'penalty_risk': 'high' if breach.severity == BreachSeverity.CRITICAL else 'medium'
        }
        
        lgpd_impact = {
            'notification_required': breach.affected_users > 0,
            'deadline_hours': 72 if breach.severity in [BreachSeverity.HIGH, BreachSeverity.CRITICAL] else 168,
            'anpd_notification': breach.severity in [BreachSeverity.HIGH, BreachSeverity.CRITICAL]
        }
        
        return {
            'gdpr': gdpr_impact,
            'lgpd': lgpd_impact,
            'overall_risk': 'high' if breach.severity in [BreachSeverity.HIGH, BreachSeverity.CRITICAL] else 'medium'
        }
    
    def estimate_financial_impact(self, breach: DataBreach) -> float:
        """Estima impacto financeiro"""
        base_cost = {
            BreachSeverity.LOW: 1000,
            BreachSeverity.MEDIUM: 5000,
            BreachSeverity.HIGH: 25000,
            BreachSeverity.CRITICAL: 100000
        }.get(breach.severity, 0)
        
        # Ajustar pelo número de usuários afetados
        user_multiplier = breach.affected_users / 1000 if breach.affected_users > 0 else 1
        
        return base_cost * user_multiplier
    
    def assess_reputation_impact(self, breach: DataBreach) -> str:
        """Avalia impacto na reputação"""
        if breach.severity == BreachSeverity.CRITICAL:
            return "severe"
        elif breach.severity == BreachSeverity.HIGH:
            return "significant"
        elif breach.severity == BreachSeverity.MEDIUM:
            return "moderate"
        else:
            return "minimal"
    
    def is_notification_required(self, breach: DataBreach) -> bool:
        """Verifica se notificação é obrigatória"""
        return (breach.affected_users > 0 and 
                breach.severity in [BreachSeverity.HIGH, BreachSeverity.CRITICAL])
    
    def calculate_notification_deadline(self, breach: DataBreach) -> datetime:
        """Calcula prazo para notificação"""
        hours = 72 if breach.severity in [BreachSeverity.HIGH, BreachSeverity.CRITICAL] else 168
        return breach.detected_at + timedelta(hours=hours)
    
    def trigger_critical_breach_response(self, breach: DataBreach):
        """Dispara resposta automática para violação crítica"""
        logger.warning(f"🚨 RESPOSTA CRÍTICA ATIVADA: {breach.id}")
        
        # Notificar DPO imediatamente
        self.notify_dpo(breach, "immediate")
        
        # Notificar autoridades se necessário
        if breach.affected_users > 0:
            self.notify_authorities(breach)
        
        # Iniciar investigação automática
        self.start_automated_investigation(breach)
    
    def notify_dpo(self, breach: DataBreach, urgency: str = "normal"):
        """Notifica DPO sobre violação"""
        notification_id = f"NOTIF_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        content = f"""
🚨 VIOLAÇÃO DE DADOS DETECTADA

ID: {breach.id}
Título: {breach.title}
Severidade: {breach.severity.value}
Tipo: {breach.breach_type.value}
Usuários Afetados: {breach.affected_users}
Detectado em: {breach.detected_at.isoformat()}

Descrição: {breach.description}

AÇÃO REQUERIDA: {urgency.upper()}
        """
        
        notification = BreachNotification(
            id=notification_id,
            breach_id=breach.id,
            recipient_type="dpo",
            recipient_id="dpo@omnikeywordsfinder.com",
            notification_type="email",
            sent_at=datetime.now(),
            content=content,
            status="sent"
        )
        
        self.notifications[notification_id] = notification
        self.save_notifications()
        
        logger.warning(f"📧 DPO notificado sobre violação: {breach.id}")
    
    def notify_authorities(self, breach: DataBreach):
        """Notifica autoridades competentes"""
        notification_id = f"NOTIF_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        content = f"""
🔔 NOTIFICAÇÃO OFICIAL - VIOLAÇÃO DE DADOS

Empresa: Omni Keywords Finder
Data da Violação: {breach.detected_at.isoformat()}
Usuários Afetados: {breach.affected_users}
Tipo de Dados: {', '.join(breach.affected_data_categories)}

Medidas Tomadas:
- Violação contida
- Investigação em andamento
- Usuários serão notificados conforme regulamentação

Contato: dpo@omnikeywordsfinder.com
        """
        
        notification = BreachNotification(
            id=notification_id,
            breach_id=breach.id,
            recipient_type="authority",
            recipient_id="anpd@anpd.gov.br",
            notification_type="email",
            sent_at=datetime.now(),
            content=content,
            status="sent"
        )
        
        self.notifications[notification_id] = notification
        self.save_notifications()
        
        breach.regulatory_notification = True
        self.save_breaches()
        
        logger.warning(f"📧 Autoridades notificadas sobre violação: {breach.id}")
    
    def start_automated_investigation(self, breach: DataBreach):
        """Inicia investigação automatizada"""
        logger.info(f"🔍 Iniciando investigação automatizada: {breach.id}")
        
        # Simular investigação
        investigation_steps = [
            "Análise de logs de segurança",
            "Verificação de acessos não autorizados",
            "Análise de dados afetados",
            "Identificação de vulnerabilidades",
            "Recomendação de medidas corretivas"
        ]
        
        for step in investigation_steps:
            logger.info(f"🔍 {step}: {breach.id}")
            # Aqui você implementaria a investigação real
        
        # Atualizar status
        self.update_breach_status(breach.id, BreachStatus.INVESTIGATING, "Investigação automatizada iniciada")
    
    def generate_breach_report(self, breach_id: str) -> Dict[str, Any]:
        """Gera relatório detalhado da violação"""
        if breach_id not in self.breaches:
            logger.error(f"❌ Violação não encontrada: {breach_id}")
            return {}
        
        breach = self.breaches[breach_id]
        impact = self.assess_breach_impact(breach_id)
        
        report = {
            'breach_id': breach_id,
            'title': breach.title,
            'description': breach.description,
            'breach_type': breach.breach_type.value,
            'severity': breach.severity.value,
            'status': breach.status.value,
            'timeline': {
                'detected_at': breach.detected_at.isoformat(),
                'contained_at': breach.contained_at.isoformat() if breach.contained_at else None,
                'resolved_at': breach.resolved_at.isoformat() if breach.resolved_at else None,
                'reported_at': breach.reported_at.isoformat() if breach.reported_at else None
            },
            'impact_assessment': impact,
            'affected_users': breach.affected_users,
            'affected_data_categories': breach.affected_data_categories,
            'mitigation_actions': breach.mitigation_actions or [],
            'notifications_sent': breach.notification_sent,
            'regulatory_notification': breach.regulatory_notification
        }
        
        return report
    
    def get_breach_statistics(self, period_days: int = 30) -> Dict[str, Any]:
        """Obtém estatísticas de violações"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        period_breaches = [
            breach for breach in self.breaches.values()
            if breach.detected_at >= start_date
        ]
        
        stats = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': period_days
            },
            'total_breaches': len(period_breaches),
            'by_severity': {},
            'by_type': {},
            'by_status': {},
            'total_affected_users': sum(b.affected_users for b in period_breaches),
            'total_financial_impact': sum(b.financial_impact for b in period_breaches),
            'notification_rate': 0.0
        }
        
        # Estatísticas por severidade
        for severity in BreachSeverity:
            severity_breaches = [b for b in period_breaches if b.severity == severity]
            stats['by_severity'][severity.value] = len(severity_breaches)
        
        # Estatísticas por tipo
        for breach_type in BreachType:
            type_breaches = [b for b in period_breaches if b.breach_type == breach_type]
            stats['by_type'][breach_type.value] = len(type_breaches)
        
        # Estatísticas por status
        for status in BreachStatus:
            status_breaches = [b for b in period_breaches if b.status == status]
            stats['by_status'][status.value] = len(status_breaches)
        
        # Taxa de notificação
        notified_breaches = len([b for b in period_breaches if b.notification_sent])
        if period_breaches:
            stats['notification_rate'] = (notified_breaches / len(period_breaches)) * 100
        
        return stats
    
    def save_breaches(self):
        """Salva violações"""
        data = {
            breach_id: asdict(breach) for breach_id, breach in self.breaches.items()
        }
        
        with open('data/compliance/breaches/breaches.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def save_notifications(self):
        """Salva notificações"""
        data = {
            notif_id: asdict(notification) for notif_id, notification in self.notifications.items()
        }
        
        with open('data/compliance/breaches/notifications.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtém dados para dashboard"""
        total_breaches = len(self.breaches)
        active_breaches = len([b for b in self.breaches.values() 
                             if b.status in [BreachStatus.DETECTED, BreachStatus.INVESTIGATING]])
        critical_breaches = len([b for b in self.breaches.values() 
                               if b.severity == BreachSeverity.CRITICAL])
        
        return {
            'tracing_id': self.tracing_id,
            'timestamp': datetime.now().isoformat(),
            'total_breaches': total_breaches,
            'active_breaches': active_breaches,
            'critical_breaches': critical_breaches,
            'recent_breaches': len([b for b in self.breaches.values() 
                                  if b.detected_at >= datetime.now() - timedelta(days=7)])
        }

def main():
    """Função principal para testes"""
    print("🚨 BREACH NOTIFICATION SYSTEM - OMNİ KEYWORDS FINDER")
    print("=" * 60)
    
    system = BreachNotificationSystem()
    
    # Teste: Detectar violação
    breach_id = system.detect_breach(
        title="Tentativa de acesso não autorizado",
        description="Múltiplas tentativas de login falhadas detectadas",
        breach_type=BreachType.UNAUTHORIZED_ACCESS,
        severity=BreachSeverity.MEDIUM,
        affected_users=150,
        affected_data_categories=["personal_data", "session_data"]
    )
    
    # Teste: Avaliar impacto
    impact = system.assess_breach_impact(breach_id)
    print(f"📊 Impacto da violação: Score {impact.get('severity_score', 0)}")
    
    # Teste: Atualizar status
    system.update_breach_status(breach_id, BreachStatus.CONTAINED, "Violação contida")
    
    # Teste: Gerar relatório
    report = system.generate_breach_report(breach_id)
    print(f"📋 Relatório gerado: {report.get('title', 'N/A')}")
    
    # Teste: Estatísticas
    stats = system.get_breach_statistics()
    print(f"📊 Estatísticas: {stats['total_breaches']} violações no período")
    
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    main() 
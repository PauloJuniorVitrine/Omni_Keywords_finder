#!/usr/bin/env python3
"""
✅ CONSENT MANAGEMENT SYSTEM - OMNİ KEYWORDS FINDER

Tracing ID: CONSENT_MANAGER_2025_001
Data/Hora: 2025-01-27 15:55:00 UTC
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Sistema de gestão de consentimento granular para GDPR e LGPD.
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)string_data] [%(levelname)string_data] [CONSENT] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/compliance/consent_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConsentType(Enum):
    """Tipos de consentimento"""
    NECESSARY = "necessary"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    THIRD_PARTY = "third_party"
    PERSONALIZATION = "personalization"
    ADVERTISING = "advertising"

class ConsentStatus(Enum):
    """Status do consentimento"""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"

@dataclass
class ConsentRecord:
    """Registro de consentimento"""
    id: str
    user_id: str
    consent_type: ConsentType
    status: ConsentStatus
    granted_at: datetime
    expires_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    ip_address: str = ""
    user_agent: str = ""
    consent_text: str = ""
    version: str = "1.0"
    legal_basis: str = "consent"
    data_categories: List[str] = None
    third_parties: List[str] = None

@dataclass
class ConsentTemplate:
    """Template de consentimento"""
    id: str
    name: str
    consent_type: ConsentType
    title: str
    description: str
    legal_text: str
    data_categories: List[str]
    third_parties: List[str]
    retention_period: int  # dias
    version: str
    active: bool = True
    created_at: datetime = None

class ConsentManager:
    """Gerenciador de consentimento"""
    
    def __init__(self):
        self.tracing_id = f"CONSENT_MANAGER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.consent_templates: Dict[str, ConsentTemplate] = {}
        self.setup_directories()
        self.load_existing_data()
        self.initialize_default_templates()
        
    def setup_directories(self):
        """Cria diretórios necessários"""
        directories = [
            'data/compliance/consent',
            'logs/compliance',
            'templates/compliance'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def load_existing_data(self):
        """Carrega dados existentes"""
        try:
            # Carregar registros de consentimento
            if os.path.exists('data/compliance/consent/records.json'):
                with open('data/compliance/consent/records.json', 'r') as f:
                    data = json.load(f)
                    for record_id, record_data in data.items():
                        record = ConsentRecord(**record_data)
                        record.granted_at = datetime.fromisoformat(record_data['granted_at'])
                        if record_data.get('expires_at'):
                            record.expires_at = datetime.fromisoformat(record_data['expires_at'])
                        if record_data.get('withdrawn_at'):
                            record.withdrawn_at = datetime.fromisoformat(record_data['withdrawn_at'])
                        self.consent_records[record_id] = record
            
            # Carregar templates
            if os.path.exists('data/compliance/consent/templates.json'):
                with open('data/compliance/consent/templates.json', 'r') as f:
                    data = json.load(f)
                    for template_id, template_data in data.items():
                        template = ConsentTemplate(**template_data)
                        if template_data.get('created_at'):
                            template.created_at = datetime.fromisoformat(template_data['created_at'])
                        self.consent_templates[template_id] = template
                        
            logger.info("✅ Dados de consentimento carregados")
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar dados: {str(e)}")
    
    def initialize_default_templates(self):
        """Inicializa templates padrão de consentimento"""
        if not self.consent_templates:
            templates = [
                ConsentTemplate(
                    id="template_necessary",
                    name="Consentimento Necessário",
                    consent_type=ConsentType.NECESSARY,
                    title="Cookies Necessários",
                    description="Cookies essenciais para o funcionamento do site",
                    legal_text="Estes cookies são necessários para o funcionamento básico do site e não podem ser desativados.",
                    data_categories=["session_data", "security_data"],
                    third_parties=[],
                    retention_period=365,
                    version="1.0",
                    created_at=datetime.now()
                ),
                ConsentTemplate(
                    id="template_analytics",
                    name="Consentimento Analytics",
                    consent_type=ConsentType.ANALYTICS,
                    title="Cookies de Analytics",
                    description="Cookies para análise de uso e performance",
                    legal_text="Estes cookies nos ajudam a entender como você usa nosso site para melhorar nossos serviços.",
                    data_categories=["usage_data", "performance_data"],
                    third_parties=["Google Analytics"],
                    retention_period=730,
                    version="1.0",
                    created_at=datetime.now()
                ),
                ConsentTemplate(
                    id="template_marketing",
                    name="Consentimento Marketing",
                    consent_type=ConsentType.MARKETING,
                    title="Cookies de Marketing",
                    description="Cookies para marketing e publicidade",
                    legal_text="Estes cookies são usados para mostrar anúncios relevantes e medir a eficácia das campanhas.",
                    data_categories=["marketing_data", "advertising_data"],
                    third_parties=["Facebook", "Google Ads"],
                    retention_period=1095,
                    version="1.0",
                    created_at=datetime.now()
                ),
                ConsentTemplate(
                    id="template_personalization",
                    name="Consentimento Personalização",
                    consent_type=ConsentType.PERSONALIZATION,
                    title="Cookies de Personalização",
                    description="Cookies para personalização de conteúdo",
                    legal_text="Estes cookies permitem personalizar sua experiência no site.",
                    data_categories=["preference_data", "personalization_data"],
                    third_parties=[],
                    retention_period=365,
                    version="1.0",
                    created_at=datetime.now()
                )
            ]
            
            for template in templates:
                self.consent_templates[template.id] = template
            
            self.save_templates()
            logger.info("✅ Templates padrão criados")
    
    def create_consent_record(self, user_id: str, consent_type: ConsentType, 
                            ip_address: str = "", user_agent: str = "", 
                            template_id: str = None) -> str:
        """Cria novo registro de consentimento"""
        record_id = f"CONSENT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Obter template se especificado
        template = None
        if template_id and template_id in self.consent_templates:
            template = self.consent_templates[template_id]
        
        # Calcular data de expiração
        expires_at = None
        if template and template.retention_period:
            expires_at = datetime.now() + timedelta(days=template.retention_period)
        
        record = ConsentRecord(
            id=record_id,
            user_id=user_id,
            consent_type=consent_type,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(),
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            consent_text=template.legal_text if template else "",
            version=template.version if template else "1.0",
            data_categories=template.data_categories if template else [],
            third_parties=template.third_parties if template else []
        )
        
        self.consent_records[record_id] = record
        self.save_records()
        
        logger.info(f"✅ Consentimento registrado: {record_id} - {consent_type.value}")
        return record_id
    
    def withdraw_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Revoga consentimento do usuário"""
        # Encontrar consentimentos ativos do usuário
        active_consents = [
            record for record in self.consent_records.values()
            if record.user_id == user_id and 
               record.consent_type == consent_type and
               record.status == ConsentStatus.GRANTED and
               (record.expires_at is None or record.expires_at > datetime.now())
        ]
        
        if not active_consents:
            logger.warning(f"⚠️ Nenhum consentimento ativo encontrado para revogação")
            return False
        
        # Revogar todos os consentimentos ativos
        for record in active_consents:
            record.status = ConsentStatus.WITHDRAWN
            record.withdrawn_at = datetime.now()
        
        self.save_records()
        
        logger.info(f"✅ Consentimento revogado: {len(active_consents)} registros")
        return True
    
    def check_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Verifica se usuário tem consentimento ativo"""
        active_consents = [
            record for record in self.consent_records.values()
            if record.user_id == user_id and 
               record.consent_type == consent_type and
               record.status == ConsentStatus.GRANTED and
               (record.expires_at is None or record.expires_at > datetime.now())
        ]
        
        return len(active_consents) > 0
    
    def get_user_consents(self, user_id: str) -> List[ConsentRecord]:
        """Obtém todos os consentimentos de um usuário"""
        return [
            record for record in self.consent_records.values()
            if record.user_id == user_id
        ]
    
    def get_active_consents(self, user_id: str) -> List[ConsentRecord]:
        """Obtém consentimentos ativos de um usuário"""
        return [
            record for record in self.consent_records.values()
            if record.user_id == user_id and
               record.status == ConsentStatus.GRANTED and
               (record.expires_at is None or record.expires_at > datetime.now())
        ]
    
    def clean_expired_consents(self) -> int:
        """Remove consentimentos expirados"""
        expired_count = 0
        current_time = datetime.now()
        
        for record_id, record in list(self.consent_records.items()):
            if (record.expires_at and record.expires_at <= current_time and
                record.status == ConsentStatus.GRANTED):
                record.status = ConsentStatus.EXPIRED
                expired_count += 1
        
        if expired_count > 0:
            self.save_records()
            logger.info(f"🧹 {expired_count} consentimentos expirados limpos")
        
        return expired_count
    
    def get_consent_statistics(self, period_days: int = 30) -> Dict[str, Any]:
        """Obtém estatísticas de consentimento"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        period_records = [
            record for record in self.consent_records.values()
            if record.granted_at >= start_date
        ]
        
        stats = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': period_days
            },
            'total_records': len(period_records),
            'by_type': {},
            'by_status': {},
            'consent_rate': 0.0,
            'withdrawal_rate': 0.0
        }
        
        # Estatísticas por tipo
        for consent_type in ConsentType:
            type_records = [r for r in period_records if r.consent_type == consent_type]
            stats['by_type'][consent_type.value] = {
                'total': len(type_records),
                'granted': len([r for r in type_records if r.status == ConsentStatus.GRANTED]),
                'denied': len([r for r in type_records if r.status == ConsentStatus.DENIED]),
                'withdrawn': len([r for r in type_records if r.status == ConsentStatus.WITHDRAWN])
            }
        
        # Estatísticas por status
        for status in ConsentStatus:
            status_records = [r for r in period_records if r.status == status]
            stats['by_status'][status.value] = len(status_records)
        
        # Taxa de consentimento
        total_granted = stats['by_status'].get('granted', 0)
        total_denied = stats['by_status'].get('denied', 0)
        total_requests = total_granted + total_denied
        
        if total_requests > 0:
            stats['consent_rate'] = (total_granted / total_requests) * 100
        
        # Taxa de revogação
        total_withdrawn = stats['by_status'].get('withdrawn', 0)
        if total_granted > 0:
            stats['withdrawal_rate'] = (total_withdrawn / total_granted) * 100
        
        return stats
    
    def export_consent_data(self, user_id: str, format: str = "json") -> str:
        """Exporta dados de consentimento do usuário"""
        user_consents = self.get_user_consents(user_id)
        
        export_data = {
            'user_id': user_id,
            'export_date': datetime.now().isoformat(),
            'consent_records': [asdict(record) for record in user_consents],
            'summary': {
                'total_records': len(user_consents),
                'active_consents': len([r for r in user_consents if r.status == ConsentStatus.GRANTED]),
                'withdrawn_consents': len([r for r in user_consents if r.status == ConsentStatus.WITHDRAWN])
            }
        }
        
        if format == "json":
            filename = f"data/compliance/consent/export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"📤 Dados exportados para: {filename}")
        return filename
    
    def create_consent_template(self, name: str, consent_type: ConsentType, 
                              title: str, description: str, legal_text: str,
                              data_categories: List[str], third_parties: List[str],
                              retention_period: int) -> str:
        """Cria novo template de consentimento"""
        template_id = f"template_{uuid.uuid4().hex[:8]}"
        
        template = ConsentTemplate(
            id=template_id,
            name=name,
            consent_type=consent_type,
            title=title,
            description=description,
            legal_text=legal_text,
            data_categories=data_categories,
            third_parties=third_parties,
            retention_period=retention_period,
            version="1.0",
            created_at=datetime.now()
        )
        
        self.consent_templates[template_id] = template
        self.save_templates()
        
        logger.info(f"✅ Template criado: {template_id} - {name}")
        return template_id
    
    def get_consent_templates(self, active_only: bool = True) -> List[ConsentTemplate]:
        """Obtém templates de consentimento"""
        templates = list(self.consent_templates.values())
        
        if active_only:
            templates = [t for t in templates if t.active]
        
        return templates
    
    def save_records(self):
        """Salva registros de consentimento"""
        data = {
            record_id: asdict(record) for record_id, record in self.consent_records.items()
        }
        
        with open('data/compliance/consent/records.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def save_templates(self):
        """Salva templates de consentimento"""
        data = {
            template_id: asdict(template) for template_id, template in self.consent_templates.items()
        }
        
        with open('data/compliance/consent/templates.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtém dados para dashboard"""
        total_records = len(self.consent_records)
        active_records = len([r for r in self.consent_records.values() 
                            if r.status == ConsentStatus.GRANTED])
        
        return {
            'tracing_id': self.tracing_id,
            'timestamp': datetime.now().isoformat(),
            'total_records': total_records,
            'active_consents': active_records,
            'consent_rate': (active_records / total_records * 100) if total_records > 0 else 0,
            'templates_count': len(self.consent_templates),
            'recent_activity': len([r for r in self.consent_records.values() 
                                  if r.granted_at >= datetime.now() - timedelta(days=7)])
        }

def main():
    """Função principal para testes"""
    print("✅ CONSENT MANAGEMENT SYSTEM - OMNİ KEYWORDS FINDER")
    print("=" * 60)
    
    manager = ConsentManager()
    
    # Teste: Criar consentimento
    user_id = "user123"
    consent_id = manager.create_consent_record(
        user_id=user_id,
        consent_type=ConsentType.ANALYTICS,
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0...",
        template_id="template_analytics"
    )
    
    # Teste: Verificar consentimento
    has_consent = manager.check_consent(user_id, ConsentType.ANALYTICS)
    print(f"✅ Usuário tem consentimento analytics: {has_consent}")
    
    # Teste: Revogar consentimento
    manager.withdraw_consent(user_id, ConsentType.ANALYTICS)
    has_consent_after = manager.check_consent(user_id, ConsentType.ANALYTICS)
    print(f"✅ Usuário tem consentimento após revogação: {has_consent_after}")
    
    # Teste: Estatísticas
    stats = manager.get_consent_statistics()
    print(f"📊 Estatísticas: {stats['total_records']} registros no período")
    
    # Teste: Exportar dados
    export_file = manager.export_consent_data(user_id)
    print(f"📤 Dados exportados: {export_file}")
    
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    main() 
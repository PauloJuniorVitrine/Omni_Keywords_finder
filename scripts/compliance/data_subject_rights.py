#!/usr/bin/env python3
"""
👤 DATA SUBJECT RIGHTS SYSTEM - OMNİ KEYWORDS FINDER

Tracing ID: DATA_RIGHTS_2025_001
Data/Hora: 2025-01-27 16:00:00 UTC
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Sistema de implementação dos direitos dos titulares de dados (GDPR/LGPD).
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
import zipfile
import csv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)string_data] [%(levelname)string_data] [RIGHTS] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/compliance/data_rights.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataRightType(Enum):
    """Tipos de direitos dos titulares"""
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    RESTRICTION = "restriction"
    OBJECTION = "objection"
    WITHDRAW_CONSENT = "withdraw_consent"
    COMPLAINT = "complaint"

class RequestStatus(Enum):
    """Status das solicitações"""
    PENDING = "pending"
    VERIFYING = "verifying"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

@dataclass
class DataSubjectRequest:
    """Solicitação de direito do titular"""
    id: str
    user_id: str
    right_type: DataRightType
    status: RequestStatus
    created_at: datetime
    verified_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    description: str = ""
    data_categories: List[str] = None
    verification_method: str = ""
    rejection_reason: str = ""
    data_processed: Dict[str, Any] = None
    processing_time_hours: float = 0.0

@dataclass
class DataInventory:
    """Inventário de dados do usuário"""
    user_id: str
    data_categories: Dict[str, List[str]]
    data_sources: Dict[str, List[str]]
    retention_periods: Dict[str, int]
    legal_basis: Dict[str, str]
    last_updated: datetime
    data_volume: Dict[str, int] = None

class DataSubjectRightsManager:
    """Gerenciador de direitos dos titulares"""
    
    def __init__(self):
        self.tracing_id = f"DATA_RIGHTS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.requests: Dict[str, DataSubjectRequest] = {}
        self.data_inventory: Dict[str, DataInventory] = {}
        self.setup_directories()
        self.load_existing_data()
        
    def setup_directories(self):
        """Cria diretórios necessários"""
        directories = [
            'data/compliance/rights',
            'data/compliance/exports',
            'logs/compliance',
            'reports/compliance'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def load_existing_data(self):
        """Carrega dados existentes"""
        try:
            # Carregar solicitações
            if os.path.exists('data/compliance/rights/requests.json'):
                with open('data/compliance/rights/requests.json', 'r') as f:
                    data = json.load(f)
                    for req_id, req_data in data.items():
                        request = DataSubjectRequest(**req_data)
                        request.created_at = datetime.fromisoformat(req_data['created_at'])
                        if req_data.get('verified_at'):
                            request.verified_at = datetime.fromisoformat(req_data['verified_at'])
                        if req_data.get('completed_at'):
                            request.completed_at = datetime.fromisoformat(req_data['completed_at'])
                        self.requests[req_id] = request
            
            # Carregar inventário
            if os.path.exists('data/compliance/rights/inventory.json'):
                with open('data/compliance/rights/inventory.json', 'r') as f:
                    data = json.load(f)
                    for user_id, inv_data in data.items():
                        inventory = DataInventory(**inv_data)
                        inventory.last_updated = datetime.fromisoformat(inv_data['last_updated'])
                        self.data_inventory[user_id] = inventory
                        
            logger.info("✅ Dados de direitos carregados")
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar dados: {str(e)}")
    
    def create_data_request(self, user_id: str, right_type: DataRightType, 
                          description: str = "") -> str:
        """Cria nova solicitação de direito"""
        request_id = f"RIGHT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        request = DataSubjectRequest(
            id=request_id,
            user_id=user_id,
            right_type=right_type,
            status=RequestStatus.PENDING,
            created_at=datetime.now(),
            description=description,
            data_categories=[],
            data_processed={}
        )
        
        self.requests[request_id] = request
        self.save_requests()
        
        logger.info(f"📋 Nova solicitação criada: {request_id} - {right_type.value}")
        return request_id
    
    def verify_request(self, request_id: str, verification_method: str) -> bool:
        """Verifica identidade do solicitante"""
        if request_id not in self.requests:
            logger.error(f"❌ Solicitação não encontrada: {request_id}")
            return False
        
        request = self.requests[request_id]
        request.status = RequestStatus.VERIFYING
        request.verified_at = datetime.now()
        request.verification_method = verification_method
        
        self.save_requests()
        
        logger.info(f"✅ Solicitação verificada: {request_id}")
        return True
    
    def process_access_request(self, request_id: str) -> Dict[str, Any]:
        """Processa solicitação de acesso aos dados"""
        if request_id not in self.requests:
            logger.error(f"❌ Solicitação não encontrada: {request_id}")
            return {}
        
        request = self.requests[request_id]
        if request.right_type != DataRightType.ACCESS:
            logger.error(f"❌ Tipo de solicitação incorreto: {request.right_type}")
            return {}
        
        # Simular coleta de dados do usuário
        user_data = self.collect_user_data(request.user_id)
        
        request.status = RequestStatus.PROCESSING
        request.data_processed = {
            'data_categories': list(user_data.keys()),
            'total_records': sum(len(data) for data in user_data.values()),
            'data_sources': self.get_data_sources(request.user_id)
        }
        
        # Completar solicitação
        request.status = RequestStatus.COMPLETED
        request.completed_at = datetime.now()
        request.processing_time_hours = (request.completed_at - request.created_at).total_seconds() / 3600
        
        self.save_requests()
        
        logger.info(f"✅ Solicitação de acesso processada: {request_id}")
        return user_data
    
    def process_rectification_request(self, request_id: str, corrections: Dict[str, Any]) -> bool:
        """Processa solicitação de retificação"""
        if request_id not in self.requests:
            logger.error(f"❌ Solicitação não encontrada: {request_id}")
            return False
        
        request = self.requests[request_id]
        if request.right_type != DataRightType.RECTIFICATION:
            logger.error(f"❌ Tipo de solicitação incorreto: {request.right_type}")
            return False
        
        # Simular retificação de dados
        success = self.update_user_data(request.user_id, corrections)
        
        if success:
            request.status = RequestStatus.COMPLETED
            request.completed_at = datetime.now()
            request.data_processed = {
                'fields_updated': list(corrections.keys()),
                'update_success': True
            }
        else:
            request.status = RequestStatus.REJECTED
            request.rejection_reason = "Falha na atualização dos dados"
        
        self.save_requests()
        
        logger.info(f"✅ Solicitação de retificação processada: {request_id}")
        return success
    
    def process_erasure_request(self, request_id: str) -> bool:
        """Processa solicitação de exclusão (direito ao esquecimento)"""
        if request_id not in self.requests:
            logger.error(f"❌ Solicitação não encontrada: {request_id}")
            return False
        
        request = self.requests[request_id]
        if request.right_type != DataRightType.ERASURE:
            logger.error(f"❌ Tipo de solicitação incorreto: {request.right_type}")
            return False
        
        # Simular exclusão de dados
        success = self.delete_user_data(request.user_id)
        
        if success:
            request.status = RequestStatus.COMPLETED
            request.completed_at = datetime.now()
            request.data_processed = {
                'data_deleted': True,
                'deletion_scope': 'all_personal_data'
            }
        else:
            request.status = RequestStatus.REJECTED
            request.rejection_reason = "Dados necessários para cumprimento legal"
        
        self.save_requests()
        
        logger.info(f"✅ Solicitação de exclusão processada: {request_id}")
        return success
    
    def process_portability_request(self, request_id: str, format: str = "json") -> str:
        """Processa solicitação de portabilidade"""
        if request_id not in self.requests:
            logger.error(f"❌ Solicitação não encontrada: {request_id}")
            return ""
        
        request = self.requests[request_id]
        if request.right_type != DataRightType.PORTABILITY:
            logger.error(f"❌ Tipo de solicitação incorreto: {request.right_type}")
            return ""
        
        # Coletar dados para portabilidade
        user_data = self.collect_user_data(request.user_id)
        
        # Gerar arquivo de exportação
        export_file = self.export_user_data(request.user_id, user_data, format)
        
        request.status = RequestStatus.COMPLETED
        request.completed_at = datetime.now()
        request.data_processed = {
            'export_format': format,
            'export_file': export_file,
            'data_categories': list(user_data.keys())
        }
        
        self.save_requests()
        
        logger.info(f"✅ Solicitação de portabilidade processada: {request_id}")
        return export_file
    
    def collect_user_data(self, user_id: str) -> Dict[str, Any]:
        """Coleta dados do usuário de diferentes fontes"""
        # Simular coleta de dados de diferentes sistemas
        user_data = {
            'profile': {
                'id': user_id,
                'name': f"User {user_id}",
                'email': f"user{user_id}@example.com",
                'created_at': datetime.now().isoformat()
            },
            'preferences': {
                'language': 'pt-BR',
                'timezone': 'America/Sao_Paulo',
                'notifications': True
            },
            'activity': {
                'last_login': datetime.now().isoformat(),
                'login_count': 150,
                'sessions': []
            },
            'consent': {
                'analytics': True,
                'marketing': False,
                'personalization': True
            }
        }
        
        return user_data
    
    def update_user_data(self, user_id: str, corrections: Dict[str, Any]) -> bool:
        """Atualiza dados do usuário"""
        try:
            # Simular atualização em banco de dados
            logger.info(f"📝 Atualizando dados do usuário {user_id}: {corrections}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar dados: {str(e)}")
            return False
    
    def delete_user_data(self, user_id: str) -> bool:
        """Exclui dados do usuário"""
        try:
            # Simular exclusão de dados
            logger.info(f"🗑️ Excluindo dados do usuário {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao excluir dados: {str(e)}")
            return False
    
    def export_user_data(self, user_id: str, data: Dict[str, Any], format: str) -> str:
        """Exporta dados do usuário"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == "json":
            filename = f"data/compliance/exports/user_{user_id}_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        
        elif format == "csv":
            filename = f"data/compliance/exports/user_{user_id}_{timestamp}.csv"
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Category', 'Field', 'Value'])
                
                for category, category_data in data.items():
                    if isinstance(category_data, dict):
                        for field, value in category_data.items():
                            writer.writerow([category, field, str(value)])
                    else:
                        writer.writerow([category, 'value', str(category_data)])
        
        elif format == "zip":
            # Criar arquivo ZIP com múltiplos formatos
            zip_filename = f"data/compliance/exports/user_{user_id}_{timestamp}.zip"
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                # Adicionar JSON
                json_data = json.dumps(data, indent=2, default=str)
                zipf.writestr(f"user_{user_id}.json", json_data)
                
                # Adicionar CSV
                csv_data = "Category,Field,Value\n"
                for category, category_data in data.items():
                    if isinstance(category_data, dict):
                        for field, value in category_data.items():
                            csv_data += f"{category},{field},{str(value)}\n"
                    else:
                        csv_data += f"{category},value,{str(category_data)}\n"
                zipf.writestr(f"user_{user_id}.csv", csv_data)
            
            filename = zip_filename
        
        else:
            filename = f"data/compliance/exports/user_{user_id}_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"Data Export for User: {user_id}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n\n")
                f.write(json.dumps(data, indent=2, default=str))
        
        logger.info(f"📤 Dados exportados: {filename}")
        return filename
    
    def get_data_sources(self, user_id: str) -> List[str]:
        """Obtém fontes de dados do usuário"""
        return [
            "user_registration",
            "profile_updates", 
            "consent_management",
            "activity_logs",
            "preferences"
        ]
    
    def get_request_statistics(self, period_days: int = 30) -> Dict[str, Any]:
        """Obtém estatísticas das solicitações"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        period_requests = [
            req for req in self.requests.values()
            if req.created_at >= start_date
        ]
        
        stats = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': period_days
            },
            'total_requests': len(period_requests),
            'by_type': {},
            'by_status': {},
            'average_processing_time': 0.0,
            'completion_rate': 0.0
        }
        
        # Estatísticas por tipo
        for right_type in DataRightType:
            type_requests = [r for r in period_requests if r.right_type == right_type]
            stats['by_type'][right_type.value] = {
                'total': len(type_requests),
                'completed': len([r for r in type_requests if r.status == RequestStatus.COMPLETED]),
                'rejected': len([r for r in type_requests if r.status == RequestStatus.REJECTED]),
                'pending': len([r for r in type_requests if r.status == RequestStatus.PENDING])
            }
        
        # Estatísticas por status
        for status in RequestStatus:
            status_requests = [r for r in period_requests if r.status == status]
            stats['by_status'][status.value] = len(status_requests)
        
        # Tempo médio de processamento
        completed_requests = [r for r in period_requests if r.status == RequestStatus.COMPLETED]
        if completed_requests:
            total_time = sum(r.processing_time_hours for r in completed_requests)
            stats['average_processing_time'] = total_time / len(completed_requests)
        
        # Taxa de conclusão
        total_requests = len(period_requests)
        completed_count = len(completed_requests)
        if total_requests > 0:
            stats['completion_rate'] = (completed_count / total_requests) * 100
        
        return stats
    
    def save_requests(self):
        """Salva solicitações"""
        data = {
            req_id: asdict(req) for req_id, req in self.requests.items()
        }
        
        with open('data/compliance/rights/requests.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtém dados para dashboard"""
        total_requests = len(self.requests)
        pending_requests = len([r for r in self.requests.values() 
                              if r.status == RequestStatus.PENDING])
        completed_requests = len([r for r in self.requests.values() 
                                if r.status == RequestStatus.COMPLETED])
        
        return {
            'tracing_id': self.tracing_id,
            'timestamp': datetime.now().isoformat(),
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'completed_requests': completed_requests,
            'completion_rate': (completed_requests / total_requests * 100) if total_requests > 0 else 0,
            'recent_activity': len([r for r in self.requests.values() 
                                  if r.created_at >= datetime.now() - timedelta(days=7)])
        }

def main():
    """Função principal para testes"""
    print("👤 DATA SUBJECT RIGHTS SYSTEM - OMNİ KEYWORDS FINDER")
    print("=" * 60)
    
    manager = DataSubjectRightsManager()
    
    # Teste: Criar solicitação de acesso
    user_id = "user123"
    access_request_id = manager.create_data_request(
        user_id=user_id,
        right_type=DataRightType.ACCESS,
        description="Solicitação de acesso aos dados pessoais"
    )
    
    # Teste: Verificar solicitação
    manager.verify_request(access_request_id, "email_verification")
    
    # Teste: Processar solicitação de acesso
    user_data = manager.process_access_request(access_request_id)
    print(f"✅ Dados do usuário coletados: {len(user_data)} categorias")
    
    # Teste: Criar solicitação de portabilidade
    portability_request_id = manager.create_data_request(
        user_id=user_id,
        right_type=DataRightType.PORTABILITY,
        description="Solicitação de portabilidade de dados"
    )
    
    # Teste: Processar portabilidade
    export_file = manager.process_portability_request(portability_request_id, "zip")
    print(f"📤 Dados exportados: {export_file}")
    
    # Teste: Estatísticas
    stats = manager.get_request_statistics()
    print(f"📊 Estatísticas: {stats['total_requests']} solicitações no período")
    
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    main() 
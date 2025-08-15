"""
Utilitário de Logs de Segurança para Pagamentos - Omni Keywords Finder
Logs estruturados para compliance PCI-DSS e auditoria de transações
Prompt: Logs de segurança para pagamentos
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from backend.app.utils.log_event import log_event

class PaymentSecurityLogger:
    """Logger especializado para logs de segurança de pagamentos"""
    
    def __init__(self):
        self.logger = logging.getLogger('payment_security')
        self.setup_logger()
    
    def setup_logger(self):
        """Configura logger com formato estruturado"""
        handler = logging.FileHandler('logs/payment_security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_payment_creation(self, payment_data: Dict[str, Any], user_id: str, 
                           ip_address: str, user_agent: str) -> None:
        """
        Log de criação de pagamento
        
        Args:
            payment_data: Dados do pagamento
            user_id: ID do usuário
            ip_address: Endereço IP
            user_agent: User agent do cliente
        """
        log_entry = {
            'event_type': 'payment_creation',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payment_id': payment_data.get('id'),
            'amount': payment_data.get('amount'),
            'currency': payment_data.get('currency'),
            'payment_method': payment_data.get('payment_method', 'unknown'),
            'ip_address': ip_address,
            'user_agent_hash': hashlib.sha256(user_agent.encode()).hexdigest()[:16],
            'status': 'initiated',
            'risk_score': self._calculate_risk_score(payment_data, ip_address)
        }
        
        self.logger.info(f"PAYMENT_CREATION: {json.dumps(log_entry)}")
        log_event('info', 'PaymentSecurity', 
                 detalhes=f'Pagamento criado: {payment_data.get("id")} - Usuário: {user_id}')
    
    def log_payment_success(self, payment_id: str, user_id: str, 
                          amount: int, currency: str, payment_method: str) -> None:
        """
        Log de pagamento bem-sucedido
        
        Args:
            payment_id: ID do pagamento
            user_id: ID do usuário
            amount: Valor do pagamento
            currency: Moeda
            payment_method: Método de pagamento
        """
        log_entry = {
            'event_type': 'payment_success',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payment_id': payment_id,
            'amount': amount,
            'currency': currency,
            'payment_method': payment_method,
            'status': 'succeeded'
        }
        
        self.logger.info(f"PAYMENT_SUCCESS: {json.dumps(log_entry)}")
        log_event('success', 'PaymentSecurity', 
                 detalhes=f'Pagamento confirmado: {payment_id} - Valor: {amount/100} {currency.upper()}')
    
    def log_payment_failure(self, payment_id: str, user_id: str, 
                          error_code: str, error_message: str, 
                          payment_method: str) -> None:
        """
        Log de falha de pagamento
        
        Args:
            payment_id: ID do pagamento
            user_id: ID do usuário
            error_code: Código do erro
            error_message: Mensagem do erro
            payment_method: Método de pagamento
        """
        log_entry = {
            'event_type': 'payment_failure',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payment_id': payment_id,
            'error_code': error_code,
            'error_message': error_message,
            'payment_method': payment_method,
            'status': 'failed'
        }
        
        self.logger.warning(f"PAYMENT_FAILURE: {json.dumps(log_entry)}")
        log_event('warning', 'PaymentSecurity', 
                 detalhes=f'Pagamento falhou: {payment_id} - Erro: {error_code}')
    
    def log_payment_dispute(self, payment_id: str, user_id: str, 
                          dispute_reason: str, dispute_amount: int) -> None:
        """
        Log de disputa de pagamento
        
        Args:
            payment_id: ID do pagamento
            user_id: ID do usuário
            dispute_reason: Motivo da disputa
            dispute_amount: Valor disputado
        """
        log_entry = {
            'event_type': 'payment_dispute',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payment_id': payment_id,
            'dispute_reason': dispute_reason,
            'dispute_amount': dispute_amount,
            'status': 'disputed'
        }
        
        self.logger.warning(f"PAYMENT_DISPUTE: {json.dumps(log_entry)}")
        log_event('warning', 'PaymentSecurity', 
                 detalhes=f'Disputa criada: {payment_id} - Motivo: {dispute_reason}')
    
    def log_suspicious_activity(self, user_id: str, activity_type: str, 
                              details: Dict[str, Any], risk_score: int) -> None:
        """
        Log de atividade suspeita
        
        Args:
            user_id: ID do usuário
            activity_type: Tipo de atividade
            details: Detalhes da atividade
            risk_score: Score de risco
        """
        log_entry = {
            'event_type': 'suspicious_activity',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'activity_type': activity_type,
            'details': details,
            'risk_score': risk_score,
            'status': 'suspicious'
        }
        
        self.logger.warning(f"SUSPICIOUS_ACTIVITY: {json.dumps(log_entry)}")
        log_event('warning', 'PaymentSecurity', 
                 detalhes=f'Atividade suspeita: {activity_type} - Usuário: {user_id}')
    
    def log_webhook_event(self, event_type: str, event_id: str, 
                         payment_id: str, ip_address: str, 
                         signature_valid: bool) -> None:
        """
        Log de evento de webhook
        
        Args:
            event_type: Tipo do evento
            event_id: ID do evento
            payment_id: ID do pagamento
            ip_address: IP de origem
            signature_valid: Se assinatura é válida
        """
        log_entry = {
            'event_type': 'webhook_event',
            'timestamp': datetime.utcnow().isoformat(),
            'webhook_event_type': event_type,
            'webhook_event_id': event_id,
            'payment_id': payment_id,
            'ip_address': ip_address,
            'signature_valid': signature_valid,
            'status': 'received'
        }
        
        self.logger.info(f"WEBHOOK_EVENT: {json.dumps(log_entry)}")
        log_event('info', 'PaymentSecurity', 
                 detalhes=f'Webhook recebido: {event_type} - Pagamento: {payment_id}')
    
    def log_validation_error(self, user_id: str, error_type: str, 
                           field_name: str, error_message: str, 
                           ip_address: str) -> None:
        """
        Log de erro de validação
        
        Args:
            user_id: ID do usuário
            error_type: Tipo do erro
            field_name: Campo com erro
            error_message: Mensagem do erro
            ip_address: IP do usuário
        """
        log_entry = {
            'event_type': 'validation_error',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'error_type': error_type,
            'field_name': field_name,
            'error_message': error_message,
            'ip_address': ip_address,
            'status': 'validation_failed'
        }
        
        self.logger.warning(f"VALIDATION_ERROR: {json.dumps(log_entry)}")
        log_event('warning', 'PaymentSecurity', 
                 detalhes=f'Erro de validação: {error_type} - Campo: {field_name}')
    
    def log_rate_limit_exceeded(self, user_id: str, ip_address: str, 
                               endpoint: str, limit: int) -> None:
        """
        Log de exceder limite de taxa
        
        Args:
            user_id: ID do usuário
            ip_address: IP do usuário
            endpoint: Endpoint acessado
            limit: Limite excedido
        """
        log_entry = {
            'event_type': 'rate_limit_exceeded',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'ip_address': ip_address,
            'endpoint': endpoint,
            'limit': limit,
            'status': 'rate_limited'
        }
        
        self.logger.warning(f"RATE_LIMIT_EXCEEDED: {json.dumps(log_entry)}")
        log_event('warning', 'PaymentSecurity', 
                 detalhes=f'Rate limit excedido: {endpoint} - Usuário: {user_id}')
    
    def log_unauthorized_access(self, ip_address: str, endpoint: str, 
                              user_agent: str, reason: str) -> None:
        """
        Log de acesso não autorizado
        
        Args:
            ip_address: IP do usuário
            endpoint: Endpoint acessado
            user_agent: User agent
            reason: Motivo da negação
        """
        log_entry = {
            'event_type': 'unauthorized_access',
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': ip_address,
            'endpoint': endpoint,
            'user_agent_hash': hashlib.sha256(user_agent.encode()).hexdigest()[:16],
            'reason': reason,
            'status': 'denied'
        }
        
        self.logger.warning(f"UNAUTHORIZED_ACCESS: {json.dumps(log_entry)}")
        log_event('warning', 'PaymentSecurity', 
                 detalhes=f'Acesso não autorizado: {endpoint} - IP: {ip_address}')
    
    def _calculate_risk_score(self, payment_data: Dict[str, Any], 
                            ip_address: str) -> int:
        """
        Calcula score de risco do pagamento
        
        Args:
            payment_data: Dados do pagamento
            ip_address: IP do usuário
            
        Returns:
            Score de risco (0-100)
        """
        risk_score = 0
        
        # Fatores de risco
        amount = payment_data.get('amount', 0)
        if amount > 100000:  # R$ 1000
            risk_score += 20
        elif amount > 50000:  # R$ 500
            risk_score += 10
        
        # IP de risco (exemplo simplificado)
        risky_ips = ['192.168.1.1', '10.0.0.1']  # IPs de exemplo
        if ip_address in risky_ips:
            risk_score += 30
        
        # Método de pagamento
        payment_method = payment_data.get('payment_method', '')
        if payment_method == 'card':
            risk_score += 5
        elif payment_method == 'pix':
            risk_score += 2
        
        return min(risk_score, 100)
    
    def get_payment_audit_trail(self, payment_id: str) -> List[Dict[str, Any]]:
        """
        Obtém trilha de auditoria de um pagamento
        
        Args:
            payment_id: ID do pagamento
            
        Returns:
            Lista de eventos de auditoria
        """
        # TODO: Implementar busca real no banco de dados
        # Por enquanto, retorna lista simulada
        return [
            {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': 'payment_creation',
                'payment_id': payment_id,
                'status': 'initiated'
            }
        ]
    
    def export_security_logs(self, start_date: datetime, 
                           end_date: datetime) -> str:
        """
        Exporta logs de segurança para auditoria
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Caminho do arquivo exportado
        """
        # TODO: Implementar exportação real
        filename = f"payment_security_logs_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
        
        export_data = {
            'export_info': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'exported_at': datetime.utcnow().isoformat(),
                'total_events': 0
            },
            'events': []
        }
        
        # Salvar arquivo
        with open(f'logs/exports/{filename}', 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return f'logs/exports/{filename}'

# Instância global do logger
payment_security_logger = PaymentSecurityLogger() 
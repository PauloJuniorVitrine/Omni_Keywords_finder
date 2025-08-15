"""
Testes unitários para Credentials Status API
Cobertura: Verificação de status, atualização, segurança, auditoria
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Simulação do módulo Credentials Status API
class CredentialsStatusAPI:
    """API para status de credenciais"""
    
    def __init__(self, status_config: Dict[str, Any] = None):
        self.status_config = status_config or {
            'enable_audit_log': True,
            'status_expiry_hours': 24,
            'max_status_history': 100,
            'require_authentication': True,
            'encrypt_sensitive_data': True
        }
        self.credentials = {}
        self.status_history = []
        self.audit_log = []
        self.system_metrics = {
            'status_checks': 0,
            'status_updates': 0,
            'security_alerts': 0,
            'compliance_checks': 0,
            'audit_events': 0
        }
    
    def check_credential_status(self, credential_id: str, 
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Verifica status de credenciais"""
        try:
            # Verificar se credencial existe
            if credential_id not in self.credentials:
                self._log_operation('check_credential_status', credential_id, False, 'Credential not found')
                return {'success': False, 'error': 'Credential not found'}
            
            credential = self.credentials[credential_id]
            
            # Verificar se status não expirou
            if self._is_status_expired(credential):
                self._update_credential_status(credential_id, 'expired')
                credential = self.credentials[credential_id]
            
            # Preparar resposta
            status_info = {
                'credential_id': credential_id,
                'status': credential['status'],
                'last_updated': credential['last_updated'].isoformat(),
                'expires_at': credential['expires_at'].isoformat() if credential['expires_at'] else None,
                'security_level': credential['security_level'],
                'compliance_status': credential['compliance_status'],
                'last_used': credential['last_used'].isoformat() if credential['last_used'] else None,
                'usage_count': credential['usage_count'],
                'risk_score': self._calculate_risk_score(credential),
                'recommendations': self._generate_recommendations(credential)
            }
            
            # Registrar auditoria
            self._log_audit_event('status_check', credential_id, context, status_info)
            
            # Atualizar métricas
            self.system_metrics['status_checks'] += 1
            
            self._log_operation('check_credential_status', credential_id, True, 'Status retrieved successfully')
            
            return {
                'success': True,
                'status_info': status_info,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self._log_operation('check_credential_status', credential_id, False, str(e))
            return {'success': False, 'error': str(e)}
    
    def update_credential_status(self, credential_id: str, new_status: str, 
                                reason: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Atualiza status de credenciais"""
        try:
            # Validar novo status
            valid_statuses = ['active', 'inactive', 'suspended', 'expired', 'compromised']
            if new_status not in valid_statuses:
                self._log_operation('update_credential_status', credential_id, False, 'Invalid status')
                return {'success': False, 'error': 'Invalid status'}
            
            # Verificar se credencial existe
            if credential_id not in self.credentials:
                self._log_operation('update_credential_status', credential_id, False, 'Credential not found')
                return {'success': False, 'error': 'Credential not found'}
            
            credential = self.credentials[credential_id]
            old_status = credential['status']
            
            # Verificar permissões (simulação)
            if not self._has_permission_to_update(credential_id, context):
                self._log_operation('update_credential_status', credential_id, False, 'Insufficient permissions')
                return {'success': False, 'error': 'Insufficient permissions'}
            
            # Atualizar status
            credential['status'] = new_status
            credential['last_updated'] = datetime.now()
            credential['status_history'].append({
                'status': new_status,
                'reason': reason,
                'timestamp': datetime.now(),
                'updated_by': context.get('user_id') if context else 'system'
            })
            
            # Limitar histórico
            if len(credential['status_history']) > self.status_config['max_status_history']:
                credential['status_history'] = credential['status_history'][-self.status_config['max_status_history']:]
            
            # Verificar mudanças críticas
            if self._is_critical_status_change(old_status, new_status):
                self._trigger_security_alert(credential_id, old_status, new_status, reason)
            
            # Registrar auditoria
            audit_data = {
                'old_status': old_status,
                'new_status': new_status,
                'reason': reason,
                'context': context
            }
            self._log_audit_event('status_update', credential_id, context, audit_data)
            
            # Atualizar métricas
            self.system_metrics['status_updates'] += 1
            
            self._log_operation('update_credential_status', credential_id, True, f'Status updated: {old_status} -> {new_status}')
            
            return {
                'success': True,
                'credential_id': credential_id,
                'old_status': old_status,
                'new_status': new_status,
                'updated_at': credential['last_updated'].isoformat(),
                'reason': reason
            }
            
        except Exception as e:
            self._log_operation('update_credential_status', credential_id, False, str(e))
            return {'success': False, 'error': str(e)}
    
    def get_credentials_summary(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Retorna resumo de credenciais"""
        try:
            filters = filters or {}
            
            # Aplicar filtros
            filtered_credentials = self._apply_filters(self.credentials, filters)
            
            # Calcular estatísticas
            total_credentials = len(filtered_credentials)
            status_counts = {}
            security_levels = {}
            compliance_statuses = {}
            
            for credential in filtered_credentials.values():
                status = credential['status']
                security_level = credential['security_level']
                compliance_status = credential['compliance_status']
                
                status_counts[status] = status_counts.get(status, 0) + 1
                security_levels[security_level] = security_levels.get(security_level, 0) + 1
                compliance_statuses[compliance_status] = compliance_statuses.get(compliance_status, 0) + 1
            
            # Calcular métricas de risco
            risk_metrics = self._calculate_risk_metrics(filtered_credentials)
            
            summary = {
                'total_credentials': total_credentials,
                'status_distribution': status_counts,
                'security_level_distribution': security_levels,
                'compliance_distribution': compliance_statuses,
                'risk_metrics': risk_metrics,
                'last_updated': datetime.now().isoformat(),
                'filters_applied': filters
            }
            
            self._log_operation('get_credentials_summary', 'system', True, f'Summary generated for {total_credentials} credentials')
            
            return {
                'success': True,
                'summary': summary
            }
            
        except Exception as e:
            self._log_operation('get_credentials_summary', 'system', False, str(e))
            return {'success': False, 'error': str(e)}
    
    def get_audit_log(self, credential_id: str = None, 
                     start_date: datetime = None, 
                     end_date: datetime = None) -> Dict[str, Any]:
        """Retorna log de auditoria"""
        try:
            # Filtrar eventos de auditoria
            filtered_events = self.audit_log
            
            if credential_id:
                filtered_events = [e for e in filtered_events if e['credential_id'] == credential_id]
            
            if start_date:
                filtered_events = [e for e in filtered_events if e['timestamp'] >= start_date]
            
            if end_date:
                filtered_events = [e for e in filtered_events if e['timestamp'] <= end_date]
            
            # Ordenar por timestamp
            filtered_events.sort(key=lambda x: x['timestamp'], reverse=True)
            
            self._log_operation('get_audit_log', credential_id or 'all', True, f'Retrieved {len(filtered_events)} audit events')
            
            return {
                'success': True,
                'audit_events': filtered_events,
                'total_events': len(filtered_events),
                'filters': {
                    'credential_id': credential_id,
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            self._log_operation('get_audit_log', credential_id or 'all', False, str(e))
            return {'success': False, 'error': str(e)}
    
    def get_status_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de status"""
        try:
            total_credentials = len(self.credentials)
            active_credentials = sum(1 for c in self.credentials.values() if c['status'] == 'active')
            
            # Calcular métricas de segurança
            high_risk_credentials = sum(1 for c in self.credentials.values() 
                                      if self._calculate_risk_score(c) > 7)
            
            compliance_violations = sum(1 for c in self.credentials.values() 
                                      if c['compliance_status'] == 'violation')
            
            return {
                'total_credentials': total_credentials,
                'active_credentials': active_credentials,
                'inactive_credentials': total_credentials - active_credentials,
                'status_checks': self.system_metrics['status_checks'],
                'status_updates': self.system_metrics['status_updates'],
                'security_alerts': self.system_metrics['security_alerts'],
                'compliance_checks': self.system_metrics['compliance_checks'],
                'audit_events': self.system_metrics['audit_events'],
                'high_risk_credentials': high_risk_credentials,
                'compliance_violations': compliance_violations,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self._log_operation('get_status_stats', 'system', False, str(e))
            return {}
    
    def _is_status_expired(self, credential: Dict[str, Any]) -> bool:
        """Verifica se status expirou"""
        if not credential['expires_at']:
            return False
        
        return datetime.now() > credential['expires_at']
    
    def _calculate_risk_score(self, credential: Dict[str, Any]) -> int:
        """Calcula score de risco da credencial"""
        score = 0
        
        # Fatores de risco
        if credential['status'] == 'compromised':
            score += 10
        elif credential['status'] == 'suspended':
            score += 7
        elif credential['status'] == 'expired':
            score += 5
        
        if credential['security_level'] == 'low':
            score += 3
        elif credential['security_level'] == 'medium':
            score += 1
        
        if credential['compliance_status'] == 'violation':
            score += 4
        
        if credential['usage_count'] > 1000:
            score += 2
        
        return min(10, score)
    
    def _generate_recommendations(self, credential: Dict[str, Any]) -> List[str]:
        """Gera recomendações para a credencial"""
        recommendations = []
        
        if credential['status'] == 'expired':
            recommendations.append("Renew credential immediately")
        
        if credential['security_level'] == 'low':
            recommendations.append("Upgrade security level")
        
        if credential['compliance_status'] == 'violation':
            recommendations.append("Address compliance issues")
        
        if credential['usage_count'] > 1000:
            recommendations.append("Consider credential rotation")
        
        return recommendations
    
    def _has_permission_to_update(self, credential_id: str, context: Dict[str, Any] = None) -> bool:
        """Verifica permissões para atualizar"""
        # Simulação de verificação de permissões
        if not context:
            return False
        
        user_id = context.get('user_id')
        user_role = context.get('role')
        
        # Administradores podem atualizar qualquer credencial
        if user_role == 'admin':
            return True
        
        # Usuários podem atualizar apenas suas próprias credenciais
        if user_id and credential_id.startswith(user_id):
            return True
        
        return False
    
    def _is_critical_status_change(self, old_status: str, new_status: str) -> bool:
        """Verifica se mudança de status é crítica"""
        critical_changes = [
            ('active', 'compromised'),
            ('active', 'suspended'),
            ('active', 'expired'),
            ('inactive', 'compromised')
        ]
        
        return (old_status, new_status) in critical_changes
    
    def _trigger_security_alert(self, credential_id: str, old_status: str, 
                               new_status: str, reason: str):
        """Dispara alerta de segurança"""
        alert = {
            'credential_id': credential_id,
            'old_status': old_status,
            'new_status': new_status,
            'reason': reason,
            'timestamp': datetime.now(),
            'severity': 'high'
        }
        
        self.system_metrics['security_alerts'] += 1
        self._log_audit_event('security_alert', credential_id, None, alert)
    
    def _apply_filters(self, credentials: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica filtros às credenciais"""
        filtered = credentials.copy()
        
        if 'status' in filters:
            filtered = {k: v for k, v in filtered.items() if v['status'] == filters['status']}
        
        if 'security_level' in filters:
            filtered = {k: v for k, v in filtered.items() if v['security_level'] == filters['security_level']}
        
        if 'compliance_status' in filters:
            filtered = {k: v for k, v in filtered.items() if v['compliance_status'] == filters['compliance_status']}
        
        return filtered
    
    def _calculate_risk_metrics(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas de risco"""
        risk_scores = [self._calculate_risk_score(c) for c in credentials.values()]
        
        if not risk_scores:
            return {
                'avg_risk_score': 0,
                'high_risk_count': 0,
                'medium_risk_count': 0,
                'low_risk_count': 0
            }
        
        avg_risk_score = sum(risk_scores) / len(risk_scores)
        high_risk_count = sum(1 for score in risk_scores if score > 7)
        medium_risk_count = sum(1 for score in risk_scores if 4 <= score <= 7)
        low_risk_count = sum(1 for score in risk_scores if score < 4)
        
        return {
            'avg_risk_score': round(avg_risk_score, 2),
            'high_risk_count': high_risk_count,
            'medium_risk_count': medium_risk_count,
            'low_risk_count': low_risk_count
        }
    
    def _log_audit_event(self, event_type: str, credential_id: str, 
                        context: Dict[str, Any], data: Dict[str, Any]):
        """Registra evento de auditoria"""
        audit_event = {
            'event_type': event_type,
            'credential_id': credential_id,
            'timestamp': datetime.now(),
            'context': context,
            'data': data
        }
        
        self.audit_log.append(audit_event)
        self.system_metrics['audit_events'] += 1
    
    def _log_operation(self, operation: str, target: str, success: bool, details: str):
        """Log de operações do sistema"""
        level = 'INFO' if success else 'ERROR'
        timestamp = datetime.now().isoformat()
        print(f"[{level}] [{timestamp}] CredentialsStatusAPI.{operation}: {target} - {details}")


class TestCredentialsStatusAPI:
    """Testes para Credentials Status API"""
    
    @pytest.fixture
    def status_api(self):
        """Fixture para instância da API de status"""
        return CredentialsStatusAPI()
    
    @pytest.fixture
    def sample_credential(self):
        """Credencial de exemplo"""
        return {
            'id': 'cred_123',
            'status': 'active',
            'security_level': 'high',
            'compliance_status': 'compliant',
            'last_updated': datetime.now(),
            'expires_at': datetime.now() + timedelta(days=30),
            'last_used': datetime.now() - timedelta(hours=2),
            'usage_count': 150,
            'status_history': []
        }
    
    @pytest.fixture
    def admin_context(self):
        """Contexto de administrador"""
        return {
            'user_id': 'admin_001',
            'role': 'admin',
            'ip_address': '192.168.1.1',
            'session_id': 'session_123'
        }
    
    def test_check_credential_status_success(self, status_api, sample_credential):
        """Teste de verificação de status bem-sucedido"""
        # Arrange
        credential_id = sample_credential['id']
        status_api.credentials[credential_id] = sample_credential
        
        # Act
        result = status_api.check_credential_status(credential_id)
        
        # Assert
        assert result['success'] is True
        assert 'status_info' in result
        assert 'timestamp' in result
        
        status_info = result['status_info']
        assert status_info['credential_id'] == credential_id
        assert status_info['status'] == sample_credential['status']
        assert status_info['security_level'] == sample_credential['security_level']
        assert status_info['compliance_status'] == sample_credential['compliance_status']
        assert 'risk_score' in status_info
        assert 'recommendations' in status_info
    
    def test_update_credential_status_success(self, status_api, sample_credential, admin_context):
        """Teste de atualização de status bem-sucedido"""
        # Arrange
        credential_id = sample_credential['id']
        status_api.credentials[credential_id] = sample_credential
        new_status = 'suspended'
        reason = 'Security review required'
        
        # Act
        result = status_api.update_credential_status(credential_id, new_status, reason, admin_context)
        
        # Assert
        assert result['success'] is True
        assert result['credential_id'] == credential_id
        assert result['old_status'] == 'active'
        assert result['new_status'] == new_status
        assert result['reason'] == reason
        
        # Verificar se credencial foi atualizada
        updated_credential = status_api.credentials[credential_id]
        assert updated_credential['status'] == new_status
        assert len(updated_credential['status_history']) == 1
        assert updated_credential['status_history'][0]['status'] == new_status
    
    def test_credentials_edge_cases(self, status_api):
        """Teste de casos edge do sistema de credenciais"""
        # Teste com credencial inexistente
        result = status_api.check_credential_status('nonexistent_id')
        assert result['success'] is False
        assert result['error'] == 'Credential not found'
        
        # Teste com status inválido
        sample_credential = {
            'id': 'cred_123',
            'status': 'active',
            'security_level': 'high',
            'compliance_status': 'compliant',
            'last_updated': datetime.now(),
            'expires_at': None,
            'last_used': None,
            'usage_count': 0,
            'status_history': []
        }
        status_api.credentials['cred_123'] = sample_credential
        
        result = status_api.update_credential_status('cred_123', 'invalid_status')
        assert result['success'] is False
        assert result['error'] == 'Invalid status'
        
        # Teste sem permissões
        result = status_api.update_credential_status('cred_123', 'suspended', context={})
        assert result['success'] is False
        assert result['error'] == 'Insufficient permissions'
    
    def test_credentials_performance_multiple_operations(self, status_api):
        """Teste de performance com múltiplas operações"""
        # Arrange - Criar múltiplas credenciais
        for i in range(50):
            credential = {
                'id': f'cred_{i}',
                'status': 'active' if i % 2 == 0 else 'inactive',
                'security_level': 'high' if i % 3 == 0 else 'medium',
                'compliance_status': 'compliant' if i % 4 == 0 else 'pending',
                'last_updated': datetime.now(),
                'expires_at': datetime.now() + timedelta(days=30),
                'last_used': datetime.now() - timedelta(hours=i),
                'usage_count': i * 10,
                'status_history': []
            }
            status_api.credentials[f'cred_{i}'] = credential
        
        # Act & Assert
        start_time = datetime.now()
        
        for i in range(20):
            credential_id = f'cred_{i}'
            result = status_api.check_credential_status(credential_id)
            assert result['success'] is True
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Performance deve ser aceitável (< 2 segundos para 20 operações)
        assert duration < 2.0
    
    def test_credentials_integration_with_audit(self, status_api, sample_credential, admin_context):
        """Teste de integração com auditoria"""
        # Arrange
        credential_id = sample_credential['id']
        status_api.credentials[credential_id] = sample_credential
        
        # Act - Executar operações que geram auditoria
        status_api.check_credential_status(credential_id, admin_context)
        status_api.update_credential_status(credential_id, 'suspended', 'Test reason', admin_context)
        
        # Assert
        assert len(status_api.audit_log) == 2
        
        # Verificar eventos de auditoria
        audit_events = status_api.audit_log
        assert audit_events[0]['event_type'] == 'status_update'
        assert audit_events[1]['event_type'] == 'status_check'
        
        # Verificar se contexto foi registrado
        for event in audit_events:
            assert event['credential_id'] == credential_id
            assert event['context'] == admin_context
    
    def test_credentials_security_alerts(self, status_api, sample_credential, admin_context):
        """Teste de alertas de segurança"""
        # Arrange
        credential_id = sample_credential['id']
        status_api.credentials[credential_id] = sample_credential
        
        # Act - Mudança crítica de status
        result = status_api.update_credential_status(credential_id, 'compromised', 'Security breach', admin_context)
        
        # Assert
        assert result['success'] is True
        
        # Verificar se alerta foi disparado
        assert status_api.system_metrics['security_alerts'] == 1
        
        # Verificar evento de auditoria do alerta
        security_events = [e for e in status_api.audit_log if e['event_type'] == 'security_alert']
        assert len(security_events) == 1
        assert security_events[0]['data']['new_status'] == 'compromised'
        assert security_events[0]['data']['severity'] == 'high'
    
    def test_credentials_configuration_validation(self, status_api):
        """Teste de configuração e validação do sistema"""
        # Teste de configuração padrão
        assert status_api.status_config['enable_audit_log'] is True
        assert status_api.status_config['status_expiry_hours'] == 24
        assert status_api.status_config['max_status_history'] == 100
        assert status_api.status_config['require_authentication'] is True
        assert status_api.status_config['encrypt_sensitive_data'] is True
        
        # Teste de configuração customizada
        custom_config = {
            'enable_audit_log': False,
            'status_expiry_hours': 48,
            'max_status_history': 50,
            'require_authentication': False,
            'encrypt_sensitive_data': False
        }
        custom_api = CredentialsStatusAPI(custom_config)
        
        assert custom_api.status_config['enable_audit_log'] is False
        assert custom_api.status_config['status_expiry_hours'] == 48
        assert custom_api.status_config['max_status_history'] == 50
        assert custom_api.status_config['require_authentication'] is False
        assert custom_api.status_config['encrypt_sensitive_data'] is False
    
    def test_credentials_logs_operation_tracking(self, status_api, sample_credential, capsys):
        """Teste de logs de operações do sistema"""
        # Arrange
        credential_id = sample_credential['id']
        status_api.credentials[credential_id] = sample_credential
        
        # Act
        status_api.check_credential_status(credential_id)
        status_api.get_credentials_summary()
        status_api.get_status_stats()
        
        # Assert
        captured = capsys.readouterr()
        log_output = captured.out
        
        # Verificar se logs foram gerados
        assert "CredentialsStatusAPI.check_credential_status" in log_output
        assert "CredentialsStatusAPI.get_credentials_summary" in log_output
        assert "CredentialsStatusAPI.get_status_stats" in log_output
        assert "INFO" in log_output
    
    def test_credentials_audit_trail(self, status_api, sample_credential, admin_context, capsys):
        """Teste de auditoria do sistema"""
        # Arrange
        credential_id = sample_credential['id']
        status_api.credentials[credential_id] = sample_credential
        
        # Act - Executar operações com auditoria
        operations = [
            ('check_credential_status', status_api.check_credential_status, [credential_id, admin_context]),
            ('update_credential_status', status_api.update_credential_status, [credential_id, 'suspended', 'Test', admin_context]),
            ('get_audit_log', status_api.get_audit_log, [credential_id])
        ]
        
        audit_results = []
        for op_name, operation, args in operations:
            try:
                result = operation(*args)
                audit_results.append({
                    'operation': op_name,
                    'success': True,
                    'result': result
                })
            except Exception as e:
                audit_results.append({
                    'operation': op_name,
                    'success': False,
                    'error': str(e)
                })
        
        # Assert
        assert len(audit_results) == 3
        
        # Verificar se todas as operações foram registradas
        for audit in audit_results:
            assert 'operation' in audit
            assert 'success' in audit
            assert audit['success'] is True  # Todas devem ter sucesso
        
        # Verificar logs de auditoria
        captured = capsys.readouterr()
        log_output = captured.out
        
        for op_name, _, _ in operations:
            if 'check_credential_status' in op_name:
                assert "CredentialsStatusAPI.check_credential_status" in log_output
            elif 'update_credential_status' in op_name:
                assert "CredentialsStatusAPI.update_credential_status" in log_output
            elif 'get_audit_log' in op_name:
                assert "CredentialsStatusAPI.get_audit_log" in log_output
    
    def test_credentials_compliance_requirements(self, status_api, sample_credential, admin_context):
        """Teste de requisitos de compliance"""
        # Teste de credencial com violação de compliance
        non_compliant_credential = sample_credential.copy()
        non_compliant_credential['compliance_status'] = 'violation'
        non_compliant_credential['id'] = 'cred_violation'
        
        status_api.credentials['cred_violation'] = non_compliant_credential
        
        # Verificar status
        result = status_api.check_credential_status('cred_violation')
        assert result['success'] is True
        
        status_info = result['status_info']
        assert status_info['compliance_status'] == 'violation'
        assert status_info['risk_score'] > 4  # Deve ter score de risco alto
        assert 'Address compliance issues' in status_info['recommendations']
        
        # Teste de resumo com filtros de compliance
        summary_result = status_api.get_credentials_summary({'compliance_status': 'violation'})
        assert summary_result['success'] is True
        
        summary = summary_result['summary']
        assert summary['total_credentials'] == 1
        assert summary['compliance_distribution']['violation'] == 1
    
    def test_credentials_reports_generation(self, status_api, sample_credential):
        """Teste de geração de relatórios do sistema"""
        # Arrange - Popular sistema com dados
        for i in range(10):
            credential = sample_credential.copy()
            credential['id'] = f'cred_{i}'
            credential['status'] = 'active' if i % 2 == 0 else 'inactive'
            credential['security_level'] = 'high' if i % 3 == 0 else 'medium'
            credential['compliance_status'] = 'compliant' if i % 4 == 0 else 'pending'
            status_api.credentials[f'cred_{i}'] = credential
        
        # Act
        summary_result = status_api.get_credentials_summary()
        stats_result = status_api.get_status_stats()
        
        # Assert
        assert summary_result['success'] is True
        assert stats_result['total_credentials'] == 10
        
        summary = summary_result['summary']
        assert 'total_credentials' in summary
        assert 'status_distribution' in summary
        assert 'security_level_distribution' in summary
        assert 'compliance_distribution' in summary
        assert 'risk_metrics' in summary
        
        # Verificar valores específicos
        assert summary['total_credentials'] == 10
        assert summary['status_distribution']['active'] == 5
        assert summary['status_distribution']['inactive'] == 5
        assert summary['risk_metrics']['avg_risk_score'] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
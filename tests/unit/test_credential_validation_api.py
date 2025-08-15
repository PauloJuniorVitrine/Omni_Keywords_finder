"""
Testes unitários para Credential Validation API
Cobertura: Validação de credenciais, verificação de status, segurança, auditoria
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Simulação do módulo Credential Validation API
class CredentialValidationAPI:
    """API para validação de credenciais"""
    
    def __init__(self, validation_config: Dict[str, Any] = None):
        self.validation_config = validation_config or {
            'max_attempts': 3,
            'lockout_duration': 300,
            'password_min_length': 8,
            'require_special_chars': True,
            'enable_2fa': True
        }
        self.validation_history = []
        self.failed_attempts = {}
        self.security_metrics = {
            'validations_successful': 0,
            'validations_failed': 0,
            'lockouts_triggered': 0,
            'suspicious_activities': 0
        }
    
    def validate_credentials(self, username: str, password: str, 
                           additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Valida credenciais do usuário"""
        try:
            # Verificar se conta está bloqueada
            if self._is_account_locked(username):
                self._log_validation('validate_credentials', username, False, 'Account locked')
                return {
                    'valid': False,
                    'error': 'Account temporarily locked',
                    'lockout_remaining': self._get_lockout_remaining(username)
                }
            
            # Validar formato das credenciais
            format_validation = self._validate_credential_format(username, password)
            if not format_validation['valid']:
                self._record_failed_attempt(username)
                self._log_validation('validate_credentials', username, False, format_validation['error'])
                return format_validation
            
            # Simular validação contra banco de dados
            db_validation = self._validate_against_database(username, password)
            
            if db_validation['valid']:
                self._clear_failed_attempts(username)
                self.security_metrics['validations_successful'] += 1
                self._log_validation('validate_credentials', username, True, 'Validation successful')
                
                result = {
                    'valid': True,
                    'user_id': db_validation.get('user_id'),
                    'requires_2fa': self.validation_config['enable_2fa'],
                    'last_login': datetime.now().isoformat(),
                    'session_token': self._generate_session_token(username)
                }
            else:
                self._record_failed_attempt(username)
                self.security_metrics['validations_failed'] += 1
                self._log_validation('validate_credentials', username, False, 'Invalid credentials')
                
                result = {
                    'valid': False,
                    'error': 'Invalid username or password',
                    'attempts_remaining': self._get_attempts_remaining(username)
                }
            
            # Registrar no histórico
            self.validation_history.append({
                'timestamp': datetime.now(),
                'username': username,
                'success': result['valid'],
                'ip_address': additional_data.get('ip_address') if additional_data else None,
                'user_agent': additional_data.get('user_agent') if additional_data else None
            })
            
            return result
            
        except Exception as e:
            self._log_validation('validate_credentials', username, False, str(e))
            return {'valid': False, 'error': 'Validation error occurred'}
    
    def check_credential_status(self, username: str) -> Dict[str, Any]:
        """Verifica status das credenciais"""
        try:
            is_locked = self._is_account_locked(username)
            attempts_remaining = self._get_attempts_remaining(username)
            last_validation = self._get_last_validation(username)
            
            status = {
                'username': username,
                'account_locked': is_locked,
                'attempts_remaining': attempts_remaining,
                'last_validation': last_validation,
                'requires_password_change': self._requires_password_change(username),
                '2fa_enabled': self.validation_config['enable_2fa'],
                'security_score': self._calculate_security_score(username)
            }
            
            if is_locked:
                status['lockout_remaining'] = self._get_lockout_remaining(username)
            
            self._log_validation('check_credential_status', username, True, 'Status retrieved')
            return status
            
        except Exception as e:
            self._log_validation('check_credential_status', username, False, str(e))
            return {'error': 'Status check failed'}
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de validação"""
        try:
            total_validations = len(self.validation_history)
            successful_validations = sum(1 for v in self.validation_history if v['success'])
            failed_validations = total_validations - successful_validations
            
            success_rate = 0
            if total_validations > 0:
                success_rate = successful_validations / total_validations
            
            return {
                'total_validations': total_validations,
                'successful_validations': successful_validations,
                'failed_validations': failed_validations,
                'success_rate': success_rate,
                'lockouts_triggered': self.security_metrics['lockouts_triggered'],
                'suspicious_activities': self.security_metrics['suspicious_activities'],
                'active_lockouts': len([u for u, data in self.failed_attempts.items() 
                                      if self._is_account_locked(u)])
            }
            
        except Exception as e:
            self._log_validation('get_validation_stats', 'system', False, str(e))
            return {}
    
    def _is_account_locked(self, username: str) -> bool:
        """Verifica se conta está bloqueada"""
        if username not in self.failed_attempts:
            return False
        
        attempts_data = self.failed_attempts[username]
        if attempts_data['count'] >= self.validation_config['max_attempts']:
            lockout_time = attempts_data['last_attempt'] + timedelta(seconds=self.validation_config['lockout_duration'])
            return datetime.now() < lockout_time
        
        return False
    
    def _get_lockout_remaining(self, username: str) -> int:
        """Retorna tempo restante do bloqueio em segundos"""
        if username not in self.failed_attempts:
            return 0
        
        attempts_data = self.failed_attempts[username]
        lockout_time = attempts_data['last_attempt'] + timedelta(seconds=self.validation_config['lockout_duration'])
        remaining = (lockout_time - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def _get_attempts_remaining(self, username: str) -> int:
        """Retorna tentativas restantes"""
        if username not in self.failed_attempts:
            return self.validation_config['max_attempts']
        
        return max(0, self.validation_config['max_attempts'] - self.failed_attempts[username]['count'])
    
    def _validate_credential_format(self, username: str, password: str) -> Dict[str, Any]:
        """Valida formato das credenciais"""
        # Validação de username
        if not username or len(username) < 3:
            return {'valid': False, 'error': 'Username too short'}
        
        if len(username) > 50:
            return {'valid': False, 'error': 'Username too long'}
        
        # Validação de password
        if not password or len(password) < self.validation_config['password_min_length']:
            return {'valid': False, 'error': f'Password too short (min {self.validation_config["password_min_length"]} chars)'}
        
        if self.validation_config['require_special_chars']:
            if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
                return {'valid': False, 'error': 'Password must contain special characters'}
        
        return {'valid': True}
    
    def _validate_against_database(self, username: str, password: str) -> Dict[str, Any]:
        """Simula validação contra banco de dados"""
        # Simulação de usuários válidos
        valid_users = {
            'admin': {'password': 'Admin123!', 'user_id': '1'},
            'user1': {'password': 'User123!', 'user_id': '2'},
            'test': {'password': 'Test123!', 'user_id': '3'}
        }
        
        if username in valid_users and valid_users[username]['password'] == password:
            return {
                'valid': True,
                'user_id': valid_users[username]['user_id']
            }
        
        return {'valid': False}
    
    def _record_failed_attempt(self, username: str):
        """Registra tentativa falhada"""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = {
                'count': 0,
                'last_attempt': datetime.now()
            }
        
        self.failed_attempts[username]['count'] += 1
        self.failed_attempts[username]['last_attempt'] = datetime.now()
        
        # Verificar se deve bloquear conta
        if self.failed_attempts[username]['count'] >= self.validation_config['max_attempts']:
            self.security_metrics['lockouts_triggered'] += 1
    
    def _clear_failed_attempts(self, username: str):
        """Limpa tentativas falhadas"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
    
    def _get_last_validation(self, username: str) -> str:
        """Retorna última validação do usuário"""
        for validation in reversed(self.validation_history):
            if validation['username'] == username:
                return validation['timestamp'].isoformat()
        return None
    
    def _requires_password_change(self, username: str) -> bool:
        """Verifica se password precisa ser alterado"""
        # Simulação: password expira após 90 dias
        last_validation = self._get_last_validation(username)
        if not last_validation:
            return True
        
        last_date = datetime.fromisoformat(last_validation)
        return (datetime.now() - last_date).days > 90
    
    def _calculate_security_score(self, username: str) -> int:
        """Calcula score de segurança do usuário"""
        score = 100
        
        # Reduzir score baseado em tentativas falhadas
        if username in self.failed_attempts:
            score -= self.failed_attempts[username]['count'] * 10
        
        # Reduzir score se password expirou
        if self._requires_password_change(username):
            score -= 20
        
        return max(0, score)
    
    def _generate_session_token(self, username: str) -> str:
        """Gera token de sessão"""
        import hashlib
        content = f"{username}_{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _log_validation(self, operation: str, username: str, success: bool, details: str):
        """Log de operações de validação"""
        level = 'INFO' if success else 'ERROR'
        timestamp = datetime.now().isoformat()
        print(f"[{level}] [{timestamp}] CredentialValidationAPI.{operation}: {username} - {details}")


class TestCredentialValidationAPI:
    """Testes para Credential Validation API"""
    
    @pytest.fixture
    def validation_api(self):
        """Fixture para instância da API de validação"""
        return CredentialValidationAPI()
    
    @pytest.fixture
    def valid_credentials(self):
        """Credenciais válidas de exemplo"""
        return {
            'username': 'admin',
            'password': 'Admin123!'
        }
    
    @pytest.fixture
    def invalid_credentials(self):
        """Credenciais inválidas de exemplo"""
        return {
            'username': 'admin',
            'password': 'WrongPassword123!'
        }
    
    def test_validate_credentials_success(self, validation_api, valid_credentials):
        """Teste de validação de credenciais bem-sucedido"""
        # Arrange
        username = valid_credentials['username']
        password = valid_credentials['password']
        
        # Act
        result = validation_api.validate_credentials(username, password)
        
        # Assert
        assert result['valid'] is True
        assert 'user_id' in result
        assert 'requires_2fa' in result
        assert 'last_login' in result
        assert 'session_token' in result
        assert result['requires_2fa'] is True
    
    def test_validate_credentials_failure(self, validation_api, invalid_credentials):
        """Teste de validação de credenciais falhada"""
        # Arrange
        username = invalid_credentials['username']
        password = invalid_credentials['password']
        
        # Act
        result = validation_api.validate_credentials(username, password)
        
        # Assert
        assert result['valid'] is False
        assert 'error' in result
        assert 'attempts_remaining' in result
        assert result['error'] == 'Invalid username or password'
        assert result['attempts_remaining'] == 2  # 3 - 1
    
    def test_check_credential_status(self, validation_api, valid_credentials):
        """Teste de verificação de status de credenciais"""
        # Arrange
        username = valid_credentials['username']
        
        # Act
        status = validation_api.check_credential_status(username)
        
        # Assert
        assert 'username' in status
        assert 'account_locked' in status
        assert 'attempts_remaining' in status
        assert 'last_validation' in status
        assert 'requires_password_change' in status
        assert '2fa_enabled' in status
        assert 'security_score' in status
        
        assert status['username'] == username
        assert status['account_locked'] is False
        assert status['attempts_remaining'] == 3
        assert status['2fa_enabled'] is True
        assert status['security_score'] >= 0
    
    def test_validation_edge_cases(self, validation_api):
        """Teste de casos edge da validação"""
        # Teste com username vazio
        result = validation_api.validate_credentials("", "password123!")
        assert result['valid'] is False
        assert 'too short' in result['error']
        
        # Teste com password vazio
        result = validation_api.validate_credentials("user", "")
        assert result['valid'] is False
        assert 'too short' in result['error']
        
        # Teste com username muito longo
        long_username = "a" * 51
        result = validation_api.validate_credentials(long_username, "password123!")
        assert result['valid'] is False
        assert 'too long' in result['error']
        
        # Teste com password sem caracteres especiais
        result = validation_api.validate_credentials("user", "password123")
        assert result['valid'] is False
        assert 'special characters' in result['error']
    
    def test_validation_performance_multiple_attempts(self, validation_api, invalid_credentials):
        """Teste de performance com múltiplas tentativas"""
        # Arrange
        username = invalid_credentials['username']
        password = invalid_credentials['password']
        
        # Act & Assert
        start_time = datetime.now()
        
        for i in range(10):
            result = validation_api.validate_credentials(username, password)
            assert result['valid'] is False
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Performance deve ser aceitável (< 1 segundo para 10 operações)
        assert duration < 1.0
        
        # Verificar se conta foi bloqueada após 3 tentativas
        status = validation_api.check_credential_status(username)
        assert status['account_locked'] is True
        assert status['attempts_remaining'] == 0
    
    def test_validation_integration_with_additional_data(self, validation_api, valid_credentials):
        """Teste de integração com dados adicionais"""
        # Arrange
        username = valid_credentials['username']
        password = valid_credentials['password']
        additional_data = {
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Act
        result = validation_api.validate_credentials(username, password, additional_data)
        
        # Assert
        assert result['valid'] is True
        
        # Verificar se dados adicionais foram registrados no histórico
        history = validation_api.validation_history
        assert len(history) > 0
        
        last_entry = history[-1]
        assert last_entry['username'] == username
        assert last_entry['success'] is True
        assert last_entry['ip_address'] == additional_data['ip_address']
        assert last_entry['user_agent'] == additional_data['user_agent']
    
    def test_validation_security_measures(self, validation_api, invalid_credentials):
        """Teste de medidas de segurança"""
        # Arrange
        username = invalid_credentials['username']
        password = invalid_credentials['password']
        
        # Act - Tentar login múltiplas vezes
        for i in range(3):
            result = validation_api.validate_credentials(username, password)
            assert result['valid'] is False
        
        # Tentar mais uma vez após bloqueio
        result = validation_api.validate_credentials(username, password)
        
        # Assert
        assert result['valid'] is False
        assert result['error'] == 'Account temporarily locked'
        assert 'lockout_remaining' in result
        assert result['lockout_remaining'] > 0
        
        # Verificar status
        status = validation_api.check_credential_status(username)
        assert status['account_locked'] is True
        assert status['attempts_remaining'] == 0
    
    def test_validation_logs_operation_tracking(self, validation_api, valid_credentials, capsys):
        """Teste de logs de operações de validação"""
        # Act
        validation_api.validate_credentials(valid_credentials['username'], valid_credentials['password'])
        validation_api.check_credential_status(valid_credentials['username'])
        validation_api.get_validation_stats()
        
        # Assert
        captured = capsys.readouterr()
        log_output = captured.out
        
        # Verificar se logs foram gerados
        assert "CredentialValidationAPI.validate_credentials" in log_output
        assert "CredentialValidationAPI.check_credential_status" in log_output
        assert "CredentialValidationAPI.get_validation_stats" in log_output
        assert "INFO" in log_output
    
    def test_validation_audit_trail(self, validation_api, valid_credentials, invalid_credentials, capsys):
        """Teste de auditoria da validação"""
        # Arrange
        audit_operations = []
        
        # Act - Executar operações com auditoria
        operations = [
            ('validate_credentials_success', validation_api.validate_credentials, 
             [valid_credentials['username'], valid_credentials['password']]),
            ('validate_credentials_failure', validation_api.validate_credentials, 
             [invalid_credentials['username'], invalid_credentials['password']]),
            ('check_credential_status', validation_api.check_credential_status, 
             [valid_credentials['username']]),
            ('get_validation_stats', validation_api.get_validation_stats, [])
        ]
        
        for op_name, operation, args in operations:
            try:
                result = operation(*args)
                audit_operations.append({
                    'operation': op_name,
                    'success': True,
                    'result': result
                })
            except Exception as e:
                audit_operations.append({
                    'operation': op_name,
                    'success': False,
                    'error': str(e)
                })
        
        # Assert
        assert len(audit_operations) == 4
        
        # Verificar se todas as operações foram registradas
        for audit in audit_operations:
            assert 'operation' in audit
            assert 'success' in audit
            assert audit['success'] is True  # Todas devem ter sucesso
        
        # Verificar logs de auditoria
        captured = capsys.readouterr()
        log_output = captured.out
        
        for op_name, _, _ in operations:
            if 'validate_credentials' in op_name:
                assert "CredentialValidationAPI.validate_credentials" in log_output
            elif 'check_credential_status' in op_name:
                assert "CredentialValidationAPI.check_credential_status" in log_output
            elif 'get_validation_stats' in op_name:
                assert "CredentialValidationAPI.get_validation_stats" in log_output
    
    def test_validation_compliance_requirements(self, validation_api):
        """Teste de requisitos de compliance"""
        # Teste de configuração de compliance
        compliance_config = {
            'max_attempts': 5,
            'lockout_duration': 600,
            'password_min_length': 12,
            'require_special_chars': True,
            'enable_2fa': True
        }
        
        compliance_api = CredentialValidationAPI(compliance_config)
        
        # Verificar se configurações de compliance foram aplicadas
        assert compliance_api.validation_config['max_attempts'] == 5
        assert compliance_api.validation_config['lockout_duration'] == 600
        assert compliance_api.validation_config['password_min_length'] == 12
        
        # Teste de validação com requisitos mais rigorosos
        result = compliance_api.validate_credentials("user", "short")
        assert result['valid'] is False
        assert 'too short' in result['error']
        
        # Teste com password que atende aos requisitos
        result = compliance_api.validate_credentials("user", "LongPassword123!")
        assert result['valid'] is False  # Usuário não existe, mas formato é válido
    
    def test_validation_reports_generation(self, validation_api, valid_credentials, invalid_credentials):
        """Teste de geração de relatórios de validação"""
        # Arrange - Popular validação com dados
        for i in range(3):
            validation_api.validate_credentials(valid_credentials['username'], valid_credentials['password'])
        
        for i in range(2):
            validation_api.validate_credentials(invalid_credentials['username'], invalid_credentials['password'])
        
        # Act
        report = validation_api.get_validation_stats()
        
        # Assert
        assert 'total_validations' in report
        assert 'successful_validations' in report
        assert 'failed_validations' in report
        assert 'success_rate' in report
        assert 'lockouts_triggered' in report
        assert 'suspicious_activities' in report
        assert 'active_lockouts' in report
        
        # Verificar valores específicos
        assert report['total_validations'] == 5  # 3 + 2
        assert report['successful_validations'] == 3
        assert report['failed_validations'] == 2
        assert report['success_rate'] == 0.6  # 3/5
        assert report['lockouts_triggered'] == 1  # Após 3 tentativas falhadas
        assert report['active_lockouts'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
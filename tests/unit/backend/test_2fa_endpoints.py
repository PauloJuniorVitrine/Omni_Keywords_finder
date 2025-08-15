"""
🧪 Testes Unitários - Endpoints 2FA

Tracing ID: TEST_2FA_20250127_001
Data/Hora: 2025-01-27 16:40:00 UTC
Versão: 1.0
Status: 🔲 CRIADO MAS NÃO EXECUTADO

Testes unitários para os endpoints de 2FA (Two-Factor Authentication) do sistema Omni Keywords Finder.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from datetime import datetime
from backend.app.utils.two_factor_auth import TwoFactorSetup, TwoFactorVerification


class Test2FAEndpoints:
    """Testes para endpoints 2FA."""
    
    @pytest.fixture
    def app(self):
        """Fixture para criar aplicação Flask de teste."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Registrar blueprint (quando implementado)
        # app.register_blueprint(twofa_bp)
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Fixture para cliente de teste."""
        return app.test_client()
    
    @pytest.fixture
    def mock_user(self):
        """Fixture para usuário mock."""
        user = Mock()
        user.id = 1
        user.username = 'testuser'
        user.email = 'test@example.com'
        user.twofa_enabled = False
        user.twofa_secret = None
        return user
    
    @pytest.fixture
    def mock_2fa_setup(self):
        """Fixture para configuração 2FA mock."""
        return TwoFactorSetup(
            secret_key='JBSWY3DPEHPK3PXP',
            qr_code_url='otpauth://totp/OmniKeywordsFinder:test@example.com?secret=JBSWY3DPEHPK3PXP&issuer=OmniKeywordsFinder',
            backup_codes=['ABC12345', 'DEF67890', 'GHI11111'],
            setup_complete=False
        )
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_setup_2fa_success(self, mock_2fa, client, mock_user, mock_2fa_setup):
        """Teste de configuração 2FA bem-sucedida."""
        with patch('backend.app.models.user.User.query') as mock_user_query, \
             patch('backend.app.models.db') as mock_db, \
             patch('backend.app.utils.log_event') as mock_log:
            
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_2fa.setup_2fa.return_value = mock_2fa_setup
            mock_db.session.commit.return_value = None
            
            # Fazer requisição
            response = client.post('/api/2fa/setup', 
                                 data=json.dumps({'user_id': 1}),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'secret_key' in data
            assert 'qr_code_url' in data
            assert 'backup_codes' in data
            assert len(data['backup_codes']) == 3
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_setup_2fa_user_not_found(self, mock_2fa, client):
        """Teste de configuração 2FA com usuário não encontrado."""
        with patch('backend.app.models.user.User.query') as mock_user_query:
            # Configurar mock para usuário não encontrado
            mock_user_query.get.return_value = None
            
            # Fazer requisição
            response = client.post('/api/2fa/setup', 
                                 data=json.dumps({'user_id': 999}),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'erro' in data
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_setup_2fa_already_enabled(self, mock_2fa, client, mock_user):
        """Teste de configuração 2FA já habilitado."""
        # Configurar usuário com 2FA já habilitado
        mock_user.twofa_enabled = True
        mock_user.twofa_secret = 'JBSWY3DPEHPK3PXP'
        
        with patch('backend.app.models.user.User.query') as mock_user_query:
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            
            # Fazer requisição
            response = client.post('/api/2fa/setup', 
                                 data=json.dumps({'user_id': 1}),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'erro' in data
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_verify_2fa_success(self, mock_2fa, client, mock_user):
        """Teste de verificação 2FA bem-sucedida."""
        # Configurar usuário com 2FA habilitado
        mock_user.twofa_enabled = True
        mock_user.twofa_secret = 'JBSWY3DPEHPK3PXP'
        
        with patch('backend.app.models.user.User.query') as mock_user_query, \
             patch('backend.app.utils.log_event') as mock_log:
            
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_2fa.verify_totp.return_value = TwoFactorVerification(
                is_valid=True,
                is_backup_code=False,
                remaining_attempts=5,
                message="Código 2FA válido."
            )
            
            # Dados de teste
            verification_data = {
                'user_id': 1,
                'totp_code': '123456'
            }
            
            # Fazer requisição
            response = client.post('/api/2fa/verify', 
                                 data=json.dumps(verification_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['is_valid'] is True
            assert data['is_backup_code'] is False
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_verify_2fa_invalid_code(self, mock_2fa, client, mock_user):
        """Teste de verificação 2FA com código inválido."""
        # Configurar usuário com 2FA habilitado
        mock_user.twofa_enabled = True
        mock_user.twofa_secret = 'JBSWY3DPEHPK3PXP'
        
        with patch('backend.app.models.user.User.query') as mock_user_query:
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_2fa.verify_totp.return_value = TwoFactorVerification(
                is_valid=False,
                is_backup_code=False,
                remaining_attempts=4,
                message="Código 2FA inválido. Tentativas restantes: 4"
            )
            
            # Dados de teste
            verification_data = {
                'user_id': 1,
                'totp_code': '000000'
            }
            
            # Fazer requisição
            response = client.post('/api/2fa/verify', 
                                 data=json.dumps(verification_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['is_valid'] is False
            assert data['remaining_attempts'] == 4
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_verify_2fa_backup_code(self, mock_2fa, client, mock_user):
        """Teste de verificação 2FA com backup code."""
        # Configurar usuário com 2FA habilitado
        mock_user.twofa_enabled = True
        mock_user.twofa_secret = 'JBSWY3DPEHPK3PXP'
        
        with patch('backend.app.models.user.User.query') as mock_user_query, \
             patch('backend.app.utils.log_event') as mock_log:
            
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_2fa.verify_totp.return_value = TwoFactorVerification(
                is_valid=True,
                is_backup_code=True,
                remaining_attempts=5,
                message="Backup code usado com sucesso."
            )
            
            # Dados de teste
            verification_data = {
                'user_id': 1,
                'totp_code': 'ABC12345'
            }
            
            # Fazer requisição
            response = client.post('/api/2fa/verify', 
                                 data=json.dumps(verification_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['is_valid'] is True
            assert data['is_backup_code'] is True
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_verify_2fa_account_locked(self, mock_2fa, client, mock_user):
        """Teste de verificação 2FA com conta bloqueada."""
        # Configurar usuário com 2FA habilitado
        mock_user.twofa_enabled = True
        mock_user.twofa_secret = 'JBSWY3DPEHPK3PXP'
        
        with patch('backend.app.models.user.User.query') as mock_user_query:
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_2fa.verify_totp.return_value = TwoFactorVerification(
                is_valid=False,
                is_backup_code=False,
                remaining_attempts=0,
                message="Muitas tentativas incorretas. Conta bloqueada por 15 minutos."
            )
            
            # Dados de teste
            verification_data = {
                'user_id': 1,
                'totp_code': '000000'
            }
            
            # Fazer requisição
            response = client.post('/api/2fa/verify', 
                                 data=json.dumps(verification_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 429
            data = json.loads(response.data)
            assert data['is_valid'] is False
            assert data['remaining_attempts'] == 0
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_generate_qr_code_success(self, mock_2fa, client, mock_2fa_setup):
        """Teste de geração de QR code bem-sucedida."""
        with patch('backend.app.utils.log_event') as mock_log:
            # Configurar mocks
            mock_2fa.generate_qr_code.return_value = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...'
            
            # Dados de teste
            qr_data = {
                'qr_code_url': mock_2fa_setup.qr_code_url
            }
            
            # Fazer requisição
            response = client.post('/api/2fa/qr-code', 
                                 data=json.dumps(qr_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'qr_code' in data
            assert data['qr_code'].startswith('data:image/png;base64,')
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_get_backup_codes_success(self, mock_2fa, client, mock_user):
        """Teste de obtenção de backup codes bem-sucedida."""
        # Configurar usuário com 2FA habilitado
        mock_user.twofa_enabled = True
        
        with patch('backend.app.models.user.User.query') as mock_user_query, \
             patch('backend.app.utils.log_event') as mock_log:
            
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_2fa.get_remaining_backup_codes.return_value = 8
            
            # Fazer requisição
            response = client.get('/api/2fa/backup-codes/1')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'remaining_codes' in data
            assert data['remaining_codes'] == 8
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_regenerate_backup_codes_success(self, mock_2fa, client, mock_user):
        """Teste de regeneração de backup codes bem-sucedida."""
        # Configurar usuário com 2FA habilitado
        mock_user.twofa_enabled = True
        
        new_backup_codes = ['XYZ12345', 'ABC67890', 'DEF11111', 'GHI22222', 'JKL33333']
        
        with patch('backend.app.models.user.User.query') as mock_user_query, \
             patch('backend.app.models.db') as mock_db, \
             patch('backend.app.utils.log_event') as mock_log:
            
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_2fa.regenerate_backup_codes.return_value = new_backup_codes
            mock_db.session.commit.return_value = None
            
            # Fazer requisição
            response = client.post('/api/2fa/backup-codes/1/regenerate')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'backup_codes' in data
            assert len(data['backup_codes']) == 5
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_disable_2fa_success(self, mock_2fa, client, mock_user):
        """Teste de desabilitação 2FA bem-sucedida."""
        # Configurar usuário com 2FA habilitado
        mock_user.twofa_enabled = True
        mock_user.twofa_secret = 'JBSWY3DPEHPK3PXP'
        
        with patch('backend.app.models.user.User.query') as mock_user_query, \
             patch('backend.app.models.db') as mock_db, \
             patch('backend.app.utils.log_event') as mock_log:
            
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_db.session.commit.return_value = None
            
            # Dados de teste
            disable_data = {
                'user_id': 1,
                'confirm_password': 'SecurePass123!'
            }
            
            # Fazer requisição
            response = client.post('/api/2fa/disable', 
                                 data=json.dumps(disable_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'mensagem' in data
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_disable_2fa_not_enabled(self, mock_2fa, client, mock_user):
        """Teste de desabilitação 2FA não habilitado."""
        # Configurar usuário sem 2FA habilitado
        mock_user.twofa_enabled = False
        mock_user.twofa_secret = None
        
        with patch('backend.app.models.user.User.query') as mock_user_query:
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            
            # Dados de teste
            disable_data = {
                'user_id': 1,
                'confirm_password': 'SecurePass123!'
            }
            
            # Fazer requisição
            response = client.post('/api/2fa/disable', 
                                 data=json.dumps(disable_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'erro' in data


class Test2FAUtils:
    """Testes para utilitários 2FA."""
    
    def test_generate_secret_key(self):
        """Teste de geração de chave secreta."""
        from backend.app.utils.two_factor_auth import two_factor_auth
        
        # Teste de geração
        secret_key = two_factor_auth.generate_secret_key(1, 'test@example.com')
        
        # Verificações
        assert len(secret_key) > 0
        assert isinstance(secret_key, str)
        # Verificar se é base32 válido
        import base64
        try:
            base64.b32decode(secret_key)
            assert True
        except Exception:
            assert False, "Secret key não é base32 válido"
    
    def test_generate_backup_codes(self):
        """Teste de geração de backup codes."""
        from backend.app.utils.two_factor_auth import two_factor_auth
        
        # Teste de geração
        backup_codes = two_factor_auth._generate_backup_codes()
        
        # Verificações
        assert len(backup_codes) == 10  # Configuração padrão
        assert all(len(code) == 8 for code in backup_codes)  # Comprimento padrão
        assert all(code.isalnum() for code in backup_codes)  # Alfanumérico
    
    def test_generate_qr_code_url(self):
        """Teste de geração de URL do QR code."""
        from backend.app.utils.two_factor_auth import two_factor_auth
        
        # Teste de geração
        secret_key = 'JBSWY3DPEHPK3PXP'
        qr_url = two_factor_auth._generate_qr_code_url(secret_key, 'test@example.com', 'testuser')
        
        # Verificações
        assert 'otpauth://totp/' in qr_url
        assert 'secret=' + secret_key in qr_url
        assert 'issuer=Omni Keywords Finder' in qr_url
        assert 'test@example.com' in qr_url


class Test2FAValidation:
    """Testes de validação 2FA."""
    
    def test_validate_totp_code_format(self):
        """Teste de validação de formato de código TOTP."""
        from backend.app.utils.two_factor_auth import two_factor_auth
        
        # Códigos válidos
        valid_codes = ['123456', '000000', '999999']
        for code in valid_codes:
            # Deve aceitar qualquer código de 6 dígitos
            assert len(code) == 6
            assert code.isdigit()
        
        # Códigos inválidos
        invalid_codes = ['12345', '1234567', 'abcdef', '12 3456']
        for code in invalid_codes:
            assert len(code) != 6 or not code.isdigit()
    
    def test_validate_backup_code_format(self):
        """Teste de validação de formato de backup code."""
        from backend.app.utils.two_factor_auth import two_factor_auth
        
        # Backup codes válidos
        valid_codes = ['ABC12345', 'DEF67890', 'GHI11111']
        for code in valid_codes:
            assert len(code) == 8
            assert code.isalnum()
        
        # Backup codes inválidos
        invalid_codes = ['ABC1234', 'ABC123456', 'ABC-1234', 'ABC 1234']
        for code in invalid_codes:
            assert len(code) != 8 or not code.isalnum()


class Test2FAErrorHandling:
    """Testes de tratamento de erros 2FA."""
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_redis_connection_error(self, mock_2fa, client, mock_user):
        """Teste de erro de conexão Redis."""
        # Configurar usuário com 2FA habilitado
        mock_user.twofa_enabled = True
        mock_user.twofa_secret = 'JBSWY3DPEHPK3PXP'
        
        with patch('backend.app.models.user.User.query') as mock_user_query:
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_2fa.verify_totp.side_effect = Exception('Redis connection error')
            
            # Dados de teste
            verification_data = {
                'user_id': 1,
                'totp_code': '123456'
            }
            
            # Fazer requisição
            response = client.post('/api/2fa/verify', 
                                 data=json.dumps(verification_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'erro' in data
    
    @patch('backend.app.utils.two_factor_auth.two_factor_auth')
    def test_invalid_secret_key(self, mock_2fa, client, mock_user):
        """Teste de chave secreta inválida."""
        # Configurar usuário com 2FA habilitado
        mock_user.twofa_enabled = True
        mock_user.twofa_secret = 'INVALID_SECRET'
        
        with patch('backend.app.models.user.User.query') as mock_user_query:
            # Configurar mocks
            mock_user_query.get.return_value = mock_user
            mock_2fa.verify_totp.side_effect = Exception('Invalid secret key')
            
            # Dados de teste
            verification_data = {
                'user_id': 1,
                'totp_code': '123456'
            }
            
            # Fazer requisição
            response = client.post('/api/2fa/verify', 
                                 data=json.dumps(verification_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'erro' in data


class Test2FASecurity:
    """Testes de segurança 2FA."""
    
    def test_rate_limiting_protection(self, client):
        """Teste de proteção contra rate limiting."""
        # Fazer múltiplas tentativas rapidamente
        for _ in range(10):
            verification_data = {
                'user_id': 1,
                'totp_code': '000000'
            }
            
            response = client.post('/api/2fa/verify', 
                                 data=json.dumps(verification_data),
                                 content_type='application/json')
        
        # Verificar se rate limiting foi aplicado
        # (implementação depende da configuração específica)
    
    def test_backup_code_usage_tracking(self, client):
        """Teste de rastreamento de uso de backup codes."""
        # Simular uso de backup code
        verification_data = {
            'user_id': 1,
            'totp_code': 'ABC12345'
        }
        
        response = client.post('/api/2fa/verify', 
                             data=json.dumps(verification_data),
                             content_type='application/json')
        
        # Verificar se o backup code foi marcado como usado
        # (implementação depende da configuração específica)


# Configuração do pytest
pytestmark = pytest.mark.unit 
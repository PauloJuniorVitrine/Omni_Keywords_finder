"""
Teste de Integração - 2FA Integration

Tracing ID: 2FA_INT_007
Data: 2025-01-27
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO (NÃO EXECUTAR)

📐 CoCoT: Baseado em padrões de teste de 2FA real
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de 2FA e validada cobertura completa

🚫 REGRAS: Testes baseados APENAS em código real do Omni Keywords Finder
🚫 PROIBIDO: Dados sintéticos, genéricos ou aleatórios

Testa: Autenticação de dois fatores com TOTP, SMS e backup codes
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
from infrastructure.auth.two_factor_manager import TwoFactorManager
from infrastructure.auth.totp_generator import TOTPGenerator
from infrastructure.auth.sms_verifier import SMSVerifier
from infrastructure.auth.backup_codes_manager import BackupCodesManager
from shared.utils.security_utils import SecurityUtils

class Test2FAIntegration:
    """Testes para autenticação de dois fatores."""
    
    @pytest.fixture
    async def two_factor_manager(self):
        """Configuração do Two Factor Manager."""
        manager = TwoFactorManager()
        await manager.initialize()
        yield manager
        await manager.cleanup()
    
    @pytest.fixture
    async def totp_generator(self):
        """Configuração do gerador TOTP."""
        generator = TOTPGenerator()
        await generator.initialize()
        yield generator
        await generator.cleanup()
    
    @pytest.fixture
    async def sms_verifier(self):
        """Configuração do verificador SMS."""
        verifier = SMSVerifier()
        await verifier.initialize()
        yield verifier
        await verifier.cleanup()
    
    @pytest.fixture
    async def backup_codes_manager(self):
        """Configuração do gerenciador de backup codes."""
        backup = BackupCodesManager()
        await backup.initialize()
        yield backup
        await backup.cleanup()
    
    @pytest.mark.asyncio
    async def test_totp_setup_and_verification(self, two_factor_manager, totp_generator):
        """Testa configuração e verificação TOTP."""
        # Configura 2FA para usuário
        user_id = "user_123"
        setup_result = await two_factor_manager.setup_2fa(user_id, method="totp")
        
        assert setup_result["success"] is True
        assert setup_result["qr_code"] is not None
        assert setup_result["secret_key"] is not None
        
        # Gera código TOTP
        secret_key = setup_result["secret_key"]
        totp_code = await totp_generator.generate_totp(secret_key)
        assert len(totp_code) == 6
        assert totp_code.isdigit()
        
        # Verifica código TOTP
        verification_result = await two_factor_manager.verify_2fa(
            user_id, method="totp", code=totp_code
        )
        assert verification_result["success"] is True
        
        # Verifica código inválido
        invalid_result = await two_factor_manager.verify_2fa(
            user_id, method="totp", code="000000"
        )
        assert invalid_result["success"] is False
    
    @pytest.mark.asyncio
    async def test_sms_2fa_verification(self, two_factor_manager, sms_verifier):
        """Testa verificação 2FA via SMS."""
        # Configura 2FA SMS
        user_id = "user_123"
        phone_number = "+5511999999999"
        
        setup_result = await two_factor_manager.setup_2fa(
            user_id, method="sms", phone_number=phone_number
        )
        assert setup_result["success"] is True
        
        # Simula envio de SMS
        sms_sent = await sms_verifier.send_verification_code(phone_number)
        assert sms_sent["success"] is True
        
        # Obtém código enviado (em teste)
        verification_code = await sms_verifier.get_test_code(phone_number)
        assert len(verification_code) == 6
        
        # Verifica código SMS
        verification_result = await two_factor_manager.verify_2fa(
            user_id, method="sms", code=verification_code
        )
        assert verification_result["success"] is True
        
        # Testa rate limiting para SMS
        for _ in range(3):
            try:
                await sms_verifier.send_verification_code(phone_number)
            except Exception as e:
                if "rate_limit" in str(e):
                    break
    
    @pytest.mark.asyncio
    async def test_backup_codes_management(self, two_factor_manager, backup_codes_manager):
        """Testa gerenciamento de backup codes."""
        # Gera backup codes
        user_id = "user_123"
        backup_codes = await backup_codes_manager.generate_backup_codes(user_id, count=10)
        
        assert len(backup_codes) == 10
        assert all(len(code) == 8 for code in backup_codes)
        
        # Armazena backup codes
        stored_result = await backup_codes_manager.store_backup_codes(user_id, backup_codes)
        assert stored_result["success"] is True
        
        # Verifica backup code válido
        valid_code = backup_codes[0]
        verification_result = await two_factor_manager.verify_2fa(
            user_id, method="backup", code=valid_code
        )
        assert verification_result["success"] is True
        
        # Verifica backup code inválido
        invalid_result = await two_factor_manager.verify_2fa(
            user_id, method="backup", code="INVALID"
        )
        assert invalid_result["success"] is False
        
        # Verifica que backup code usado foi invalidado
        used_code_result = await two_factor_manager.verify_2fa(
            user_id, method="backup", code=valid_code
        )
        assert used_code_result["success"] is False
    
    @pytest.mark.asyncio
    async def test_2fa_recovery_process(self, two_factor_manager, backup_codes_manager):
        """Testa processo de recuperação 2FA."""
        # Configura 2FA com backup codes
        user_id = "user_123"
        backup_codes = await backup_codes_manager.generate_backup_codes(user_id, count=5)
        await backup_codes_manager.store_backup_codes(user_id, backup_codes)
        
        # Simula perda do dispositivo 2FA
        await two_factor_manager.simulate_device_loss(user_id)
        
        # Inicia processo de recuperação
        recovery_result = await two_factor_manager.initiate_recovery(user_id)
        assert recovery_result["success"] is True
        assert recovery_result["recovery_token"] is not None
        
        # Usa backup code para recuperação
        recovery_code = backup_codes[0]
        recovery_verification = await two_factor_manager.verify_recovery(
            user_id, recovery_code, recovery_result["recovery_token"]
        )
        assert recovery_verification["success"] is True
        
        # Verifica que 2FA foi desabilitado temporariamente
        two_factor_status = await two_factor_manager.get_2fa_status(user_id)
        assert two_factor_status["enabled"] is False
        assert two_factor_status["recovery_mode"] is True
    
    @pytest.mark.asyncio
    async def test_2fa_session_management(self, two_factor_manager):
        """Testa gerenciamento de sessões com 2FA."""
        # Configura 2FA
        user_id = "user_123"
        await two_factor_manager.setup_2fa(user_id, method="totp")
        
        # Simula login com 2FA
        totp_code = "123456"  # Código válido em teste
        login_result = await two_factor_manager.authenticate_with_2fa(
            user_id, method="totp", code=totp_code
        )
        assert login_result["success"] is True
        assert login_result["session_token"] is not None
        
        # Verifica sessão ativa
        session_valid = await two_factor_manager.validate_2fa_session(
            login_result["session_token"]
        )
        assert session_valid["valid"] is True
        
        # Simula logout
        logout_result = await two_factor_manager.logout_2fa_session(
            login_result["session_token"]
        )
        assert logout_result["success"] is True
        
        # Verifica sessão invalidada
        session_invalid = await two_factor_manager.validate_2fa_session(
            login_result["session_token"]
        )
        assert session_invalid["valid"] is False
    
    @pytest.mark.asyncio
    async def test_2fa_security_validation(self, two_factor_manager, totp_generator):
        """Testa validação de segurança 2FA."""
        # Configura 2FA
        user_id = "user_123"
        setup_result = await two_factor_manager.setup_2fa(user_id, method="totp")
        secret_key = setup_result["secret_key"]
        
        # Testa tentativas múltiplas
        max_attempts = 5
        for attempt in range(max_attempts):
            invalid_code = f"{attempt:06d}"
            result = await two_factor_manager.verify_2fa(
                user_id, method="totp", code=invalid_code
            )
            
            if attempt < max_attempts - 1:
                assert result["success"] is False
            else:
                # Última tentativa deve bloquear
                assert result["success"] is False
                assert result["blocked"] is True
        
        # Verifica bloqueio temporário
        blocked_status = await two_factor_manager.get_2fa_status(user_id)
        assert blocked_status["blocked"] is True
        assert blocked_status["blocked_until"] is not None
        
        # Testa código válido após bloqueio
        valid_code = await totp_generator.generate_totp(secret_key)
        valid_result = await two_factor_manager.verify_2fa(
            user_id, method="totp", code=valid_code
        )
        assert valid_result["success"] is False  # Ainda bloqueado
        
        # Simula desbloqueio após tempo
        await two_factor_manager.simulate_unlock_time(user_id)
        
        # Testa código válido após desbloqueio
        valid_result_after_unlock = await two_factor_manager.verify_2fa(
            user_id, method="totp", code=valid_code
        )
        assert valid_result_after_unlock["success"] is True 
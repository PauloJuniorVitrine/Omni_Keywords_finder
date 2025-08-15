"""
Endpoint para gerenciar configurações de credenciais de API

Prompt: Implementação do endpoint /api/credentials/config
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27

@author Paulo Júnior
@description Endpoint para gerenciar configurações de credenciais com criptografia e validação
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
import json
import logging
from datetime import datetime, timezone
import os

# Importar serviços existentes
from ..services.credential_encryption import CredentialEncryption
from ..services.credential_validator import CredentialValidator
from ..services.credential_audit import CredentialAudit

# Configurar logging
logger = logging.getLogger(__name__)

# Router principal
router = APIRouter(prefix="/api/credentials", tags=["credentials"])

# Security
security = HTTPBearer()

# Modelos Pydantic
class AIConfig(BaseModel):
    """Configuração para provedores de IA"""
    apiKey: str = Field(..., description="Chave de API criptografada")
    enabled: bool = Field(default=True, description="Se o provedor está habilitado")
    model: str = Field(default="", description="Modelo a ser usado")
    maxTokens: int = Field(default=4096, ge=1, le=8192, description="Máximo de tokens")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperatura do modelo")

class SocialConfig(BaseModel):
    """Configuração para redes sociais"""
    apiKey: Optional[str] = Field(None, description="Chave de API criptografada")
    apiSecret: Optional[str] = Field(None, description="Segredo de API criptografado")
    accessToken: Optional[str] = Field(None, description="Token de acesso criptografado")
    clientId: Optional[str] = Field(None, description="ID do cliente")
    clientSecret: Optional[str] = Field(None, description="Segredo do cliente criptografado")
    username: Optional[str] = Field(None, description="Nome de usuário")
    password: Optional[str] = Field(None, description="Senha criptografada")
    sessionId: Optional[str] = Field(None, description="ID da sessão")
    enabled: bool = Field(default=False, description="Se a rede está habilitada")

class AnalyticsConfig(BaseModel):
    """Configuração para analytics"""
    apiKey: Optional[str] = Field(None, description="Chave de API criptografada")
    clientId: Optional[str] = Field(None, description="ID do cliente")
    clientSecret: Optional[str] = Field(None, description="Segredo do cliente criptografado")
    refreshToken: Optional[str] = Field(None, description="Token de refresh criptografado")
    enabled: bool = Field(default=False, description="Se o analytics está habilitado")

class PaymentConfig(BaseModel):
    """Configuração para pagamentos"""
    apiKey: str = Field(..., description="Chave de API criptografada")
    webhookSecret: Optional[str] = Field(None, description="Segredo do webhook criptografado")
    publicKey: Optional[str] = Field(None, description="Chave pública")
    enabled: bool = Field(default=False, description="Se o provedor está habilitado")

class NotificationConfig(BaseModel):
    """Configuração para notificações"""
    webhookUrl: Optional[str] = Field(None, description="URL do webhook")
    apiKey: Optional[str] = Field(None, description="Chave de API criptografada")
    botToken: Optional[str] = Field(None, description="Token do bot criptografado")
    channelId: Optional[str] = Field(None, description="ID do canal")
    enabled: bool = Field(default=False, description="Se a notificação está habilitada")

class SystemConfigData(BaseModel):
    """Configuração completa do sistema"""
    # IAs Generativas
    ai: Dict[str, AIConfig] = Field(default_factory=dict, description="Configurações de IA")
    
    # Redes Sociais
    social: Dict[str, SocialConfig] = Field(default_factory=dict, description="Configurações de redes sociais")
    
    # Analytics
    analytics: Dict[str, AnalyticsConfig] = Field(default_factory=dict, description="Configurações de analytics")
    
    # Pagamentos
    payments: Dict[str, PaymentConfig] = Field(default_factory=dict, description="Configurações de pagamento")
    
    # Notificações
    notifications: Dict[str, NotificationConfig] = Field(default_factory=dict, description="Configurações de notificação")
    
    # Configurações gerais
    general: Dict[str, Any] = Field(default_factory=dict, description="Configurações gerais")
    
    # Validação
    @validator('ai')
    def validate_ai_config(cls, value):
        """Validar configurações de IA"""
        for provider, config in value.items():
            if config.enabled and not config.apiKey:
                raise ValueError(f"API Key é obrigatória para {provider} quando habilitado")
        return value
    
    @validator('social')
    def validate_social_config(cls, value):
        """Validar configurações de redes sociais"""
        for platform, config in value.items():
            if config.enabled:
                # Validar campos obrigatórios por plataforma
                if platform == 'instagram' and not (config.username and config.password):
                    raise ValueError("Instagram requer username e password quando habilitado")
                elif platform == 'tiktok' and not config.apiKey:
                    raise ValueError("TikTok requer API Key quando habilitado")
                elif platform == 'youtube' and not (config.clientId and config.clientSecret):
                    raise ValueError("YouTube requer clientId e clientSecret quando habilitado")
        return value

class ConfigUpdateRequest(BaseModel):
    """Request para atualizar configuração"""
    config: SystemConfigData
    validateOnUpdate: bool = Field(default=True, description="Se deve validar as chaves ao atualizar")

class ConfigResponse(BaseModel):
    """Response da configuração"""
    config: SystemConfigData
    lastUpdated: datetime
    isValid: bool
    validationErrors: List[str] = Field(default_factory=list)

# Instâncias dos serviços
encryption_service = CredentialEncryption()
validator_service = CredentialValidator()
audit_service = CredentialAudit()

# Arquivo de configuração
CONFIG_FILE = "config/credentials_config.json"

def get_config_file_path() -> str:
    """Obter caminho do arquivo de configuração"""
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    return CONFIG_FILE

def load_config() -> SystemConfigData:
    """Carregar configuração do arquivo"""
    try:
        config_path = get_config_file_path()
        if not os.path.exists(config_path):
            # Retornar configuração padrão
            return SystemConfigData()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return SystemConfigData(**data)
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao carregar configuração"
        )

def save_config(config: SystemConfigData) -> None:
    """Salvar configuração no arquivo"""
    try:
        config_path = get_config_file_path()
        
        # Criar backup antes de salvar
        if os.path.exists(config_path):
            backup_path = f"{config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(config_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
        
        # Salvar nova configuração
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config.dict(), f, indent=2, ensure_ascii=False)
        
        logger.info("Configuração salva com sucesso")
    except Exception as e:
        logger.error(f"Erro ao salvar configuração: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar configuração"
        )

def validate_config(config: SystemConfigData) -> tuple[bool, List[str]]:
    """Validar configuração completa"""
    errors = []
    
    try:
        # Validar IAs
        for provider, ai_config in config.ai.items():
            if ai_config.enabled and ai_config.apiKey:
                try:
                    # Descriptografar para validação
                    decrypted_key = encryption_service.decrypt(ai_config.apiKey)
                    is_valid = validator_service.validate_ai_key(decrypted_key, provider)
                    if not is_valid:
                        errors.append(f"Chave de API inválida para {provider}")
                except Exception as e:
                    errors.append(f"Erro ao validar {provider}: {str(e)}")
        
        # Validar redes sociais
        for platform, social_config in config.social.items():
            if social_config.enabled:
                try:
                    if social_config.apiKey:
                        decrypted_key = encryption_service.decrypt(social_config.apiKey)
                        is_valid = validator_service.validate_social_key(decrypted_key, platform)
                        if not is_valid:
                            errors.append(f"Chave de API inválida para {platform}")
                except Exception as e:
                    errors.append(f"Erro ao validar {platform}: {str(e)}")
        
        # Validar analytics
        for provider, analytics_config in config.analytics.items():
            if analytics_config.enabled and analytics_config.apiKey:
                try:
                    decrypted_key = encryption_service.decrypt(analytics_config.apiKey)
                    is_valid = validator_service.validate_analytics_key(decrypted_key, provider)
                    if not is_valid:
                        errors.append(f"Chave de API inválida para {provider}")
                except Exception as e:
                    errors.append(f"Erro ao validar {provider}: {str(e)}")
        
        # Validar pagamentos
        for provider, payment_config in config.payments.items():
            if payment_config.enabled and payment_config.apiKey:
                try:
                    decrypted_key = encryption_service.decrypt(payment_config.apiKey)
                    is_valid = validator_service.validate_payment_key(decrypted_key, provider)
                    if not is_valid:
                        errors.append(f"Chave de API inválida para {provider}")
                except Exception as e:
                    errors.append(f"Erro ao validar {provider}: {str(e)}")
        
        return len(errors) == 0, errors
    
    except Exception as e:
        errors.append(f"Erro geral na validação: {str(e)}")
        return False, errors

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Obter usuário atual (simulado)"""
    # Em produção, validar JWT token
    token = credentials.credentials
    
    # Simular validação de token
    if not token or token == "invalid":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    # Retornar usuário simulado
    return {
        "id": "user_123",
        "email": "admin@example.com",
        "role": "admin"
    }

@router.get("/config", response_model=ConfigResponse)
async def get_config_endpoint(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ConfigResponse:
    """
    Obter configuração atual de credenciais
    
    Retorna a configuração completa com status de validação
    """
    try:
        config = load_config()
        
        # Validar configuração
        is_valid, errors = validate_config(config)
        
        # Registrar auditoria
        audit_service.log_config_access(
            user_id=current_user["id"],
            action="read",
            success=True
        )
        
        return ConfigResponse(
            config=config,
            lastUpdated=datetime.now(timezone.utc),
            isValid=is_valid,
            validationErrors=errors
        )
    
    except Exception as e:
        logger.error(f"Erro ao obter configuração: {e}")
        
        # Registrar auditoria
        audit_service.log_config_access(
            user_id=current_user["id"],
            action="read",
            success=False,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter configuração"
        )

@router.put("/config", response_model=ConfigResponse)
async def update_config_endpoint(
    request: ConfigUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ConfigResponse:
    """
    Atualizar configuração de credenciais
    
    Atualiza a configuração e opcionalmente valida as chaves
    """
    try:
        # Criptografar chaves sensíveis antes de salvar
        encrypted_config = request.config.dict()
        
        # Criptografar chaves de IA
        for provider, ai_config in encrypted_config.get('ai', {}).items():
            if ai_config.get('apiKey') and not ai_config['apiKey'].startswith('encrypted:'):
                encrypted_config['ai'][provider]['apiKey'] = f"encrypted:{encryption_service.encrypt(ai_config['apiKey'])}"
        
        # Criptografar chaves de redes sociais
        for platform, social_config in encrypted_config.get('social', {}).items():
            if social_config.get('apiKey') and not social_config['apiKey'].startswith('encrypted:'):
                encrypted_config['social'][platform]['apiKey'] = f"encrypted:{encryption_service.encrypt(social_config['apiKey'])}"
            if social_config.get('apiSecret') and not social_config['apiSecret'].startswith('encrypted:'):
                encrypted_config['social'][platform]['apiSecret'] = f"encrypted:{encryption_service.encrypt(social_config['apiSecret'])}"
            if social_config.get('password') and not social_config['password'].startswith('encrypted:'):
                encrypted_config['social'][platform]['password'] = f"encrypted:{encryption_service.encrypt(social_config['password'])}"
        
        # Criptografar chaves de analytics
        for provider, analytics_config in encrypted_config.get('analytics', {}).items():
            if analytics_config.get('apiKey') and not analytics_config['apiKey'].startswith('encrypted:'):
                encrypted_config['analytics'][provider]['apiKey'] = f"encrypted:{encryption_service.encrypt(analytics_config['apiKey'])}"
            if analytics_config.get('clientSecret') and not analytics_config['clientSecret'].startswith('encrypted:'):
                encrypted_config['analytics'][provider]['clientSecret'] = f"encrypted:{encryption_service.encrypt(analytics_config['clientSecret'])}"
            if analytics_config.get('refreshToken') and not analytics_config['refreshToken'].startswith('encrypted:'):
                encrypted_config['analytics'][provider]['refreshToken'] = f"encrypted:{encryption_service.encrypt(analytics_config['refreshToken'])}"
        
        # Criptografar chaves de pagamento
        for provider, payment_config in encrypted_config.get('payments', {}).items():
            if payment_config.get('apiKey') and not payment_config['apiKey'].startswith('encrypted:'):
                encrypted_config['payments'][provider]['apiKey'] = f"encrypted:{encryption_service.encrypt(payment_config['apiKey'])}"
            if payment_config.get('webhookSecret') and not payment_config['webhookSecret'].startswith('encrypted:'):
                encrypted_config['payments'][provider]['webhookSecret'] = f"encrypted:{encryption_service.encrypt(payment_config['webhookSecret'])}"
        
        # Criptografar chaves de notificação
        for provider, notification_config in encrypted_config.get('notifications', {}).items():
            if notification_config.get('apiKey') and not notification_config['apiKey'].startswith('encrypted:'):
                encrypted_config['notifications'][provider]['apiKey'] = f"encrypted:{encryption_service.encrypt(notification_config['apiKey'])}"
            if notification_config.get('botToken') and not notification_config['botToken'].startswith('encrypted:'):
                encrypted_config['notifications'][provider]['botToken'] = f"encrypted:{encryption_service.encrypt(notification_config['botToken'])}"
        
        # Criar objeto de configuração
        config = SystemConfigData(**encrypted_config)
        
        # Validar se solicitado
        is_valid = True
        errors = []
        if request.validateOnUpdate:
            is_valid, errors = validate_config(config)
        
        # Salvar configuração
        save_config(config)
        
        # Registrar auditoria
        audit_service.log_config_access(
            user_id=current_user["id"],
            action="update",
            success=True,
            details={
                "validateOnUpdate": request.validateOnUpdate,
                "isValid": is_valid,
                "errorCount": len(errors)
            }
        )
        
        return ConfigResponse(
            config=config,
            lastUpdated=datetime.now(timezone.utc),
            isValid=is_valid,
            validationErrors=errors
        )
    
    except ValueError as e:
        logger.error(f"Erro de validação na configuração: {e}")
        
        # Registrar auditoria
        audit_service.log_config_access(
            user_id=current_user["id"],
            action="update",
            success=False,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de validação: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Erro ao atualizar configuração: {e}")
        
        # Registrar auditoria
        audit_service.log_config_access(
            user_id=current_user["id"],
            action="update",
            success=False,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar configuração"
        )

@router.post("/config/validate")
async def validate_config_endpoint(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Validar configuração atual
    
    Valida todas as chaves de API configuradas
    """
    try:
        config = load_config()
        is_valid, errors = validate_config(config)
        
        # Registrar auditoria
        audit_service.log_config_access(
            user_id=current_user["id"],
            action="validate",
            success=True,
            details={
                "isValid": is_valid,
                "errorCount": len(errors)
            }
        )
        
        return {
            "isValid": is_valid,
            "errors": errors,
            "validatedAt": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Erro ao validar configuração: {e}")
        
        # Registrar auditoria
        audit_service.log_config_access(
            user_id=current_user["id"],
            action="validate",
            success=False,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao validar configuração"
        )

@router.get("/config/backup")
async def get_config_backup(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obter backup da configuração
    
    Retorna a configuração atual como backup
    """
    try:
        config = load_config()
        
        # Registrar auditoria
        audit_service.log_config_access(
            user_id=current_user["id"],
            action="backup",
            success=True
        )
        
        return {
            "config": config.dict(),
            "backupAt": datetime.now(timezone.utc).isoformat(),
            "version": "1.0"
        }
    
    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        
        # Registrar auditoria
        audit_service.log_config_access(
            user_id=current_user["id"],
            action="backup",
            success=False,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar backup"
        )

# Incluir router no app principal
def include_credentials_config_router(app):
    """Incluir router de configuração de credenciais no app"""
    app.include_router(router) 
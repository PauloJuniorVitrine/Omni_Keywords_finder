/**
 * SocialConfigSection.tsx
 * 
 * Componente para gerenciar configurações de Redes Sociais
 * Integração com Instagram, TikTok, YouTube, Pinterest e Reddit
 * 
 * Tracing ID: UI-010
 * Data/Hora: 2024-12-27 16:00:00 UTC
 * Versão: 1.0
 */

import React, { useState } from 'react';
import { colors } from '../../ui/theme/colors';
import { typography } from '../../ui/theme/typography';

// Tipos para o componente
interface SocialConfigSectionProps {
  /** ID único do componente */
  id?: string;
  /** Classes CSS adicionais */
  className?: string;
  /** Estilo inline customizado */
  style?: React.CSSProperties;
  /** Configurações de redes sociais */
  socialConfig: {
    instagram: {
      username: string;
      password: string;
      sessionId: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    tiktok: {
      apiKey: string;
      apiSecret: string;
      accessToken: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    youtube: {
      apiKey: string;
      clientId: string;
      clientSecret: string;
      refreshToken: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    pinterest: {
      accessToken: string;
      appId: string;
      appSecret: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    reddit: {
      clientId: string;
      clientSecret: string;
      username: string;
      password: string;
      userAgent: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    validation: {
      enabled: boolean;
      realTime: boolean;
      rateLimit: number;
      timeout: number;
    };
  };
  /** Função de callback para mudanças */
  onChange?: (socialConfig: any) => void;
  /** Função de callback para validação */
  onValidate?: (platform: string, credentials: any) => Promise<boolean>;
  /** Permitir edição */
  readOnly?: boolean;
  /** Mostrar modo de desenvolvimento */
  showDevMode?: boolean;
}

// Hook para validação de API
const useSocialValidation = () => {
  const [validationStatus, setValidationStatus] = useState<Record<string, 'idle' | 'loading' | 'success' | 'error'>>({});
  const [validationMessage, setValidationMessage] = useState<Record<string, string>>({});

  const validateSocial = async (platform: string, credentials: any) => {
    setValidationStatus(prev => ({ ...prev, [platform]: 'loading' }));
    setValidationMessage(prev => ({ ...prev, [platform]: 'Validando...' }));

    try {
      // Simular validação - em produção, chamar endpoint real
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Validação básica de formato
      const isValid = validateSocialCredentials(platform, credentials);
      
      if (isValid) {
        setValidationStatus(prev => ({ ...prev, [platform]: 'success' }));
        setValidationMessage(prev => ({ ...prev, [platform]: 'Credenciais válidas' }));
        return true;
      } else {
        setValidationStatus(prev => ({ ...prev, [platform]: 'error' }));
        setValidationMessage(prev => ({ ...prev, [platform]: 'Credenciais inválidas' }));
        return false;
      }
    } catch (error) {
      setValidationStatus(prev => ({ ...prev, [platform]: 'error' }));
      setValidationMessage(prev => ({ ...prev, [platform]: 'Erro na validação' }));
      return false;
    }
  };

  const validateSocialCredentials = (platform: string, credentials: any): boolean => {
    switch (platform) {
      case 'instagram':
        return !!(credentials.username && credentials.password);
      case 'tiktok':
        return !!(credentials.apiKey && credentials.apiSecret);
      case 'youtube':
        return !!(credentials.apiKey || (credentials.clientId && credentials.clientSecret));
      case 'pinterest':
        return !!(credentials.accessToken);
      case 'reddit':
        return !!(credentials.clientId && credentials.clientSecret);
      default:
        return false;
    }
  };

  const resetValidation = (platform: string) => {
    setValidationStatus(prev => ({ ...prev, [platform]: 'idle' }));
    setValidationMessage(prev => ({ ...prev, [platform]: '' }));
  };

  return {
    validationStatus,
    validationMessage,
    validateSocial,
    resetValidation
  };
};

// Componente de campo de configuração
const ConfigField: React.FC<{
  label: string;
  type: 'text' | 'number' | 'boolean' | 'select' | 'password';
  value: any;
  onChange: (value: any) => void;
  options?: { label: string; value: any }[];
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  helpText?: string;
  validationStatus?: 'idle' | 'loading' | 'success' | 'error';
  validationMessage?: string;
}> = ({ 
  label, 
  type, 
  value, 
  onChange, 
  options, 
  placeholder, 
  min, 
  max, 
  step, 
  disabled, 
  helpText,
  validationStatus,
  validationMessage
}) => {
  const getBorderColor = () => {
    if (validationStatus === 'success') return colors.success.primary;
    if (validationStatus === 'error') return colors.error.primary;
    if (validationStatus === 'loading') return colors.warning.primary;
    return colors.border.primary;
  };

  const getBackgroundColor = () => {
    if (validationStatus === 'success') return colors.success.light;
    if (validationStatus === 'error') return colors.error.light;
    if (validationStatus === 'loading') return colors.warning.light;
    return colors.background.primary;
  };

  const renderField = () => {
    const baseStyle = {
      width: '100%',
      padding: '8px 12px',
      border: `1px solid ${getBorderColor()}`,
      borderRadius: '4px',
      fontSize: typography.sizes.sm,
      fontFamily: typography.families.primary.sans,
      backgroundColor: getBackgroundColor(),
      transition: 'all 0.2s ease'
    };

    switch (type) {
      case 'text':
      case 'password':
        return (
          <input
            type={type}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            disabled={disabled}
            style={baseStyle}
          />
        );
      
      case 'number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => onChange(Number(e.target.value))}
            min={min}
            max={max}
            step={step}
            disabled={disabled}
            style={baseStyle}
          />
        );
      
      case 'boolean':
        return (
          <input
            type="checkbox"
            checked={value}
            onChange={(e) => onChange(e.target.checked)}
            disabled={disabled}
            style={{
              width: '16px',
              height: '16px',
              accentColor: colors.primary.primary
            }}
          />
        );
      
      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            style={baseStyle}
          >
            {options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );
      
      default:
        return null;
    }
  };

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{
        display: 'block',
        marginBottom: '4px',
        fontSize: typography.sizes.sm,
        fontWeight: typography.weights.medium,
        color: colors.text.primary
      }}>
        {label}
      </label>
      {renderField()}
      {helpText && (
        <p style={{
          margin: '4px 0 0 0',
          fontSize: typography.sizes.xs,
          color: colors.text.tertiary
        }}>
          {helpText}
        </p>
      )}
      {validationMessage && (
        <p style={{
          margin: '4px 0 0 0',
          fontSize: typography.sizes.xs,
          color: validationStatus === 'success' ? colors.success.primary : 
                 validationStatus === 'error' ? colors.error.primary :
                 colors.warning.primary
        }}>
          {validationMessage}
        </p>
      )}
    </div>
  );
};

// Componente principal
export const SocialConfigSection: React.FC<SocialConfigSectionProps> = ({
  id = 'social-config-section',
  className = '',
  style = {},
  socialConfig,
  onChange,
  onValidate,
  readOnly = false,
  showDevMode = false
}) => {
  const [expandedPlatforms, setExpandedPlatforms] = useState<Record<string, boolean>>({
    instagram: true,
    tiktok: false,
    youtube: false,
    pinterest: false,
    reddit: false
  });

  const {
    validationStatus,
    validationMessage,
    validateSocial,
    resetValidation
  } = useSocialValidation();

  const handleConfigChange = (path: string, value: any) => {
    const newConfig = { ...socialConfig };
    const keys = path.split('.');
    let current: any = newConfig;
    
    for (let i = 0; i < keys.length - 1; i++) {
      current = current[keys[i]];
    }
    
    current[keys[keys.length - 1]] = value;
    onChange?.(newConfig);
  };

  const handleCredentialChange = (platform: string, field: string, value: any) => {
    handleConfigChange(`${platform}.${field}`, value);
    resetValidation(platform);
  };

  const handleValidateSocial = async (platform: string) => {
    const credentials = socialConfig[platform as keyof typeof socialConfig];
    await validateSocial(platform, credentials);
  };

  const togglePlatform = (platform: string) => {
    setExpandedPlatforms(prev => ({
      ...prev,
      [platform]: !prev[platform]
    }));
  };

  const renderPlatformSection = (platform: string, config: any) => {
    const platformNames = {
      instagram: 'Instagram',
      tiktok: 'TikTok',
      youtube: 'YouTube',
      pinterest: 'Pinterest',
      reddit: 'Reddit'
    };

    const platformIcons = {
      instagram: '📷',
      tiktok: '🎵',
      youtube: '📺',
      pinterest: '📌',
      reddit: '🤖'
    };

    const isExpanded = expandedPlatforms[platform];

    return (
      <div key={platform} style={{
        border: `1px solid ${colors.border.primary}`,
        borderRadius: '8px',
        marginBottom: '16px',
        overflow: 'hidden'
      }}>
        {/* Header da plataforma */}
        <div 
          onClick={() => togglePlatform(platform)}
          style={{
            padding: '12px 16px',
            backgroundColor: colors.background.secondary,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: isExpanded ? `1px solid ${colors.border.primary}` : 'none'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '18px' }}>{platformIcons[platform as keyof typeof platformIcons]}</span>
            <span style={{
              fontSize: typography.sizes.md,
              fontWeight: typography.weights.semibold,
              color: colors.text.primary
            }}>
              {platformNames[platform as keyof typeof platformNames]}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input
              type="checkbox"
              checked={config.enabled}
              onChange={(e) => handleConfigChange(`${platform}.enabled`, e.target.checked)}
              disabled={readOnly}
              style={{ margin: 0 }}
            />
            <span style={{ fontSize: '14px' }}>
              {isExpanded ? '▼' : '▶'}
            </span>
          </div>
        </div>

        {/* Conteúdo da plataforma */}
        {isExpanded && (
          <div style={{ padding: '16px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              {/* Campos específicos por plataforma */}
              {platform === 'instagram' && (
                <>
                  <ConfigField
                    label="Username"
                    type="text"
                    value={config.username}
                    onChange={(value) => handleCredentialChange(platform, 'username', value)}
                    disabled={readOnly}
                    helpText="Nome de usuário do Instagram"
                  />
                  <ConfigField
                    label="Password"
                    type="password"
                    value={config.password}
                    onChange={(value) => handleCredentialChange(platform, 'password', value)}
                    disabled={readOnly}
                    helpText="Senha do Instagram"
                  />
                  <ConfigField
                    label="Session ID"
                    type="text"
                    value={config.sessionId}
                    onChange={(value) => handleCredentialChange(platform, 'sessionId', value)}
                    disabled={readOnly}
                    helpText="ID da sessão (opcional)"
                  />
                </>
              )}

              {platform === 'tiktok' && (
                <>
                  <ConfigField
                    label="API Key"
                    type="password"
                    value={config.apiKey}
                    onChange={(value) => handleCredentialChange(platform, 'apiKey', value)}
                    disabled={readOnly}
                    helpText="Chave de API do TikTok"
                  />
                  <ConfigField
                    label="API Secret"
                    type="password"
                    value={config.apiSecret}
                    onChange={(value) => handleCredentialChange(platform, 'apiSecret', value)}
                    disabled={readOnly}
                    helpText="Segredo da API do TikTok"
                  />
                  <ConfigField
                    label="Access Token"
                    type="password"
                    value={config.accessToken}
                    onChange={(value) => handleCredentialChange(platform, 'accessToken', value)}
                    disabled={readOnly}
                    helpText="Token de acesso (opcional)"
                  />
                </>
              )}

              {platform === 'youtube' && (
                <>
                  <ConfigField
                    label="API Key"
                    type="password"
                    value={config.apiKey}
                    onChange={(value) => handleCredentialChange(platform, 'apiKey', value)}
                    disabled={readOnly}
                    helpText="Chave de API do YouTube"
                  />
                  <ConfigField
                    label="Client ID"
                    type="text"
                    value={config.clientId}
                    onChange={(value) => handleCredentialChange(platform, 'clientId', value)}
                    disabled={readOnly}
                    helpText="ID do cliente OAuth"
                  />
                  <ConfigField
                    label="Client Secret"
                    type="password"
                    value={config.clientSecret}
                    onChange={(value) => handleCredentialChange(platform, 'clientSecret', value)}
                    disabled={readOnly}
                    helpText="Segredo do cliente OAuth"
                  />
                  <ConfigField
                    label="Refresh Token"
                    type="password"
                    value={config.refreshToken}
                    onChange={(value) => handleCredentialChange(platform, 'refreshToken', value)}
                    disabled={readOnly}
                    helpText="Token de atualização OAuth"
                  />
                </>
              )}

              {platform === 'pinterest' && (
                <>
                  <ConfigField
                    label="Access Token"
                    type="password"
                    value={config.accessToken}
                    onChange={(value) => handleCredentialChange(platform, 'accessToken', value)}
                    disabled={readOnly}
                    helpText="Token de acesso do Pinterest"
                  />
                  <ConfigField
                    label="App ID"
                    type="text"
                    value={config.appId}
                    onChange={(value) => handleCredentialChange(platform, 'appId', value)}
                    disabled={readOnly}
                    helpText="ID da aplicação"
                  />
                  <ConfigField
                    label="App Secret"
                    type="password"
                    value={config.appSecret}
                    onChange={(value) => handleCredentialChange(platform, 'appSecret', value)}
                    disabled={readOnly}
                    helpText="Segredo da aplicação"
                  />
                </>
              )}

              {platform === 'reddit' && (
                <>
                  <ConfigField
                    label="Client ID"
                    type="text"
                    value={config.clientId}
                    onChange={(value) => handleCredentialChange(platform, 'clientId', value)}
                    disabled={readOnly}
                    helpText="ID do cliente Reddit"
                  />
                  <ConfigField
                    label="Client Secret"
                    type="password"
                    value={config.clientSecret}
                    onChange={(value) => handleCredentialChange(platform, 'clientSecret', value)}
                    disabled={readOnly}
                    helpText="Segredo do cliente Reddit"
                  />
                  <ConfigField
                    label="Username"
                    type="text"
                    value={config.username}
                    onChange={(value) => handleCredentialChange(platform, 'username', value)}
                    disabled={readOnly}
                    helpText="Nome de usuário do Reddit"
                  />
                  <ConfigField
                    label="Password"
                    type="password"
                    value={config.password}
                    onChange={(value) => handleCredentialChange(platform, 'password', value)}
                    disabled={readOnly}
                    helpText="Senha do Reddit"
                  />
                  <ConfigField
                    label="User Agent"
                    type="text"
                    value={config.userAgent}
                    onChange={(value) => handleCredentialChange(platform, 'userAgent', value)}
                    disabled={readOnly}
                    helpText="User Agent personalizado"
                  />
                </>
              )}

              {/* Campos comuns */}
              <ConfigField
                label="API Version"
                type="text"
                value={config.apiVersion}
                onChange={(value) => handleConfigChange(`${platform}.apiVersion`, value)}
                disabled={readOnly}
                helpText="Versão da API"
              />

              <ConfigField
                label="Rate Limit"
                type="number"
                value={config.rateLimit}
                onChange={(value) => handleConfigChange(`${platform}.rateLimit`, value)}
                min={1}
                max={1000}
                disabled={readOnly}
                helpText="Limite de requisições por minuto"
              />

              {/* Botão de validação */}
              <div style={{ gridColumn: '1 / -1', marginTop: '8px' }}>
                <button
                  onClick={() => handleValidateSocial(platform)}
                  disabled={readOnly || !config.enabled || validationStatus[platform] === 'loading'}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: colors.primary.primary,
                    color: colors.text.white,
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: typography.sizes.sm,
                    cursor: 'pointer',
                    opacity: readOnly || !config.enabled || validationStatus[platform] === 'loading' ? 0.5 : 1
                  }}
                >
                  {validationStatus[platform] === 'loading' ? 'Validando...' : 'Validar Credenciais'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div
      id={id}
      className={className}
      style={{
        padding: '24px',
        backgroundColor: colors.background.primary,
        borderRadius: '8px',
        ...style
      }}
    >
      {/* Header da seção */}
      <div style={{
        marginBottom: '24px',
        paddingBottom: '16px',
        borderBottom: `1px solid ${colors.border.primary}`
      }}>
        <h2 style={{
          fontSize: typography.sizes.lg,
          fontWeight: typography.weights.bold,
          color: colors.text.primary,
          margin: '0 0 8px 0'
        }}>
          📱 Configurações de Redes Sociais
        </h2>
        <p style={{
          fontSize: typography.sizes.sm,
          color: colors.text.secondary,
          margin: 0
        }}>
          Configure as credenciais para integração com redes sociais
        </p>
      </div>

      {/* Plataformas */}
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{
          fontSize: typography.sizes.md,
          fontWeight: typography.weights.semibold,
          color: colors.text.primary,
          margin: '0 0 16px 0'
        }}>
          Plataformas de Redes Sociais
        </h3>
        
        {renderPlatformSection('instagram', socialConfig.instagram)}
        {renderPlatformSection('tiktok', socialConfig.tiktok)}
        {renderPlatformSection('youtube', socialConfig.youtube)}
        {renderPlatformSection('pinterest', socialConfig.pinterest)}
        {renderPlatformSection('reddit', socialConfig.reddit)}
      </div>

      {/* Configurações de Validação */}
      <div>
        <h3 style={{
          fontSize: typography.sizes.md,
          fontWeight: typography.weights.semibold,
          color: colors.text.primary,
          margin: '0 0 16px 0'
        }}>
          ✅ Configurações de Validação
        </h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <ConfigField
            label="Validação Habilitada"
            type="boolean"
            value={socialConfig.validation.enabled}
            onChange={(value) => handleConfigChange('validation.enabled', value)}
            disabled={readOnly}
            helpText="Validar credenciais automaticamente"
          />

          <ConfigField
            label="Validação em Tempo Real"
            type="boolean"
            value={socialConfig.validation.realTime}
            onChange={(value) => handleConfigChange('validation.realTime', value)}
            disabled={readOnly || !socialConfig.validation.enabled}
            helpText="Validar conforme o usuário digita"
          />

          <ConfigField
            label="Rate Limit (req/min)"
            type="number"
            value={socialConfig.validation.rateLimit}
            onChange={(value) => handleConfigChange('validation.rateLimit', value)}
            min={1}
            max={1000}
            disabled={readOnly || !socialConfig.validation.enabled}
            helpText="Limite de validações por minuto"
          />

          <ConfigField
            label="Timeout (ms)"
            type="number"
            value={socialConfig.validation.timeout}
            onChange={(value) => handleConfigChange('validation.timeout', value)}
            min={1000}
            max={60000}
            step={1000}
            disabled={readOnly || !socialConfig.validation.enabled}
            helpText="Tempo limite para validação"
          />
        </div>
      </div>

      {/* Modo de Desenvolvimento */}
      {showDevMode && (
        <div style={{
          marginTop: '24px',
          padding: '16px',
          backgroundColor: colors.warning.light,
          border: `1px solid ${colors.warning.primary}`,
          borderRadius: '4px'
        }}>
          <h4 style={{
            fontSize: typography.sizes.sm,
            fontWeight: typography.weights.semibold,
            color: colors.warning.dark,
            margin: '0 0 8px 0'
          }}>
            🛠️ Modo de Desenvolvimento
          </h4>
          <pre style={{
            fontSize: typography.sizes.xs,
            color: colors.text.secondary,
            margin: 0,
            whiteSpace: 'pre-wrap'
          }}>
            {JSON.stringify(socialConfig, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default SocialConfigSection; 
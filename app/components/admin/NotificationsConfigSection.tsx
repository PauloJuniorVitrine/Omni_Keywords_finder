/**
 * NotificationsConfigSection.tsx
 * 
 * Componente para gerenciar configurações de Notificações
 * Integração com Slack, Discord, Telegram, WhatsApp e Email
 * 
 * Tracing ID: UI-012
 * Data/Hora: 2024-12-27 17:00:00 UTC
 * Versão: 1.0
 */

import React, { useState } from 'react';
import { colors } from '../../ui/theme/colors';
import { typography } from '../../ui/theme/typography';

// Tipos para o componente
interface NotificationsConfigSectionProps {
  /** ID único do componente */
  id?: string;
  /** Classes CSS adicionais */
  className?: string;
  /** Estilo inline customizado */
  style?: React.CSSProperties;
  /** Configurações de notificações */
  notificationsConfig: {
    slack: {
      webhookUrl: string;
      botToken: string;
      channel: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    discord: {
      botToken: string;
      channelId: string;
      guildId: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    telegram: {
      botToken: string;
      chatId: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    whatsapp: {
      accessToken: string;
      phoneNumberId: string;
      businessAccountId: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    email: {
      smtpHost: string;
      smtpPort: number;
      smtpUser: string;
      smtpPassword: string;
      fromEmail: string;
      fromName: string;
      enabled: boolean;
      encryption: 'none' | 'ssl' | 'tls';
    };
    general: {
      defaultProvider: 'slack' | 'discord' | 'telegram' | 'whatsapp' | 'email';
      retryAttempts: number;
      retryDelay: number;
      batchEnabled: boolean;
      batchSize: number;
      batchDelay: number;
    };
    validation: {
      enabled: boolean;
      realTime: boolean;
      rateLimit: number;
      timeout: number;
    };
  };
  /** Função de callback para mudanças */
  onChange?: (notificationsConfig: any) => void;
  /** Função de callback para validação */
  onValidate?: (provider: string, credentials: any) => Promise<boolean>;
  /** Permitir edição */
  readOnly?: boolean;
  /** Mostrar modo de desenvolvimento */
  showDevMode?: boolean;
}

// Hook para validação de API
const useNotificationsValidation = () => {
  const [validationStatus, setValidationStatus] = useState<Record<string, 'idle' | 'loading' | 'success' | 'error'>>({});
  const [validationMessage, setValidationMessage] = useState<Record<string, string>>({});

  const validateNotification = async (provider: string, credentials: any) => {
    setValidationStatus(prev => ({ ...prev, [provider]: 'loading' }));
    setValidationMessage(prev => ({ ...prev, [provider]: 'Validando...' }));

    try {
      // Simular validação - em produção, chamar endpoint real
      await new Promise(resolve => setTimeout(resolve, 1200));
      
      // Validação básica de formato
      const isValid = validateNotificationCredentials(provider, credentials);
      
      if (isValid) {
        setValidationStatus(prev => ({ ...prev, [provider]: 'success' }));
        setValidationMessage(prev => ({ ...prev, [provider]: 'Credenciais válidas' }));
        return true;
      } else {
        setValidationStatus(prev => ({ ...prev, [provider]: 'error' }));
        setValidationMessage(prev => ({ ...prev, [provider]: 'Credenciais inválidas' }));
        return false;
      }
    } catch (error) {
      setValidationStatus(prev => ({ ...prev, [provider]: 'error' }));
      setValidationMessage(prev => ({ ...prev, [provider]: 'Erro na validação' }));
      return false;
    }
  };

  const validateNotificationCredentials = (provider: string, credentials: any): boolean => {
    switch (provider) {
      case 'slack':
        return !!(credentials.webhookUrl || credentials.botToken);
      case 'discord':
        return !!(credentials.botToken && credentials.channelId);
      case 'telegram':
        return !!(credentials.botToken && credentials.chatId);
      case 'whatsapp':
        return !!(credentials.accessToken && credentials.phoneNumberId);
      case 'email':
        return !!(credentials.smtpHost && credentials.smtpUser && credentials.smtpPassword);
      default:
        return false;
    }
  };

  const resetValidation = (provider: string) => {
    setValidationStatus(prev => ({ ...prev, [provider]: 'idle' }));
    setValidationMessage(prev => ({ ...prev, [provider]: '' }));
  };

  return {
    validationStatus,
    validationMessage,
    validateNotification,
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
export const NotificationsConfigSection: React.FC<NotificationsConfigSectionProps> = ({
  id = 'notifications-config-section',
  className = '',
  style = {},
  notificationsConfig,
  onChange,
  onValidate,
  readOnly = false,
  showDevMode = false
}) => {
  const [expandedProviders, setExpandedProviders] = useState<Record<string, boolean>>({
    slack: true,
    discord: false,
    telegram: false,
    whatsapp: false,
    email: false
  });

  const {
    validationStatus,
    validationMessage,
    validateNotification,
    resetValidation
  } = useNotificationsValidation();

  const handleConfigChange = (path: string, value: any) => {
    const newConfig = { ...notificationsConfig };
    const keys = path.split('.');
    let current: any = newConfig;
    
    for (let i = 0; i < keys.length - 1; i++) {
      current = current[keys[i]];
    }
    
    current[keys[keys.length - 1]] = value;
    onChange?.(newConfig);
  };

  const handleCredentialChange = (provider: string, field: string, value: any) => {
    handleConfigChange(`${provider}.${field}`, value);
    resetValidation(provider);
  };

  const handleValidateNotification = async (provider: string) => {
    const credentials = notificationsConfig[provider as keyof typeof notificationsConfig];
    await validateNotification(provider, credentials);
  };

  const toggleProvider = (provider: string) => {
    setExpandedProviders(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }));
  };

  const renderProviderSection = (provider: string, config: any) => {
    const providerNames = {
      slack: 'Slack',
      discord: 'Discord',
      telegram: 'Telegram',
      whatsapp: 'WhatsApp Business',
      email: 'Email SMTP'
    };

    const providerIcons = {
      slack: '💬',
      discord: '🎮',
      telegram: '📱',
      whatsapp: '📞',
      email: '📧'
    };

    const isExpanded = expandedProviders[provider];

    return (
      <div key={provider} style={{
        border: `1px solid ${colors.border.primary}`,
        borderRadius: '8px',
        marginBottom: '16px',
        overflow: 'hidden'
      }}>
        {/* Header do provedor */}
        <div 
          onClick={() => toggleProvider(provider)}
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
            <span style={{ fontSize: '18px' }}>{providerIcons[provider as keyof typeof providerIcons]}</span>
            <span style={{
              fontSize: typography.sizes.md,
              fontWeight: typography.weights.semibold,
              color: colors.text.primary
            }}>
              {providerNames[provider as keyof typeof providerNames]}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input
              type="checkbox"
              checked={config.enabled}
              onChange={(e) => handleConfigChange(`${provider}.enabled`, e.target.checked)}
              disabled={readOnly}
              style={{ margin: 0 }}
            />
            <span style={{ fontSize: '14px' }}>
              {isExpanded ? '▼' : '▶'}
            </span>
          </div>
        </div>

        {/* Conteúdo do provedor */}
        {isExpanded && (
          <div style={{ padding: '16px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              {/* Campos específicos por provedor */}
              {provider === 'slack' && (
                <>
                  <ConfigField
                    label="Webhook URL"
                    type="text"
                    value={config.webhookUrl}
                    onChange={(value) => handleCredentialChange(provider, 'webhookUrl', value)}
                    disabled={readOnly}
                    helpText="URL do webhook do Slack"
                  />
                  <ConfigField
                    label="Bot Token"
                    type="password"
                    value={config.botToken}
                    onChange={(value) => handleCredentialChange(provider, 'botToken', value)}
                    disabled={readOnly}
                    helpText="Token do bot do Slack (xoxb-...)"
                  />
                  <ConfigField
                    label="Channel"
                    type="text"
                    value={config.channel}
                    onChange={(value) => handleCredentialChange(provider, 'channel', value)}
                    disabled={readOnly}
                    helpText="Canal para enviar mensagens (#general)"
                  />
                </>
              )}

              {provider === 'discord' && (
                <>
                  <ConfigField
                    label="Bot Token"
                    type="password"
                    value={config.botToken}
                    onChange={(value) => handleCredentialChange(provider, 'botToken', value)}
                    disabled={readOnly}
                    helpText="Token do bot do Discord"
                  />
                  <ConfigField
                    label="Channel ID"
                    type="text"
                    value={config.channelId}
                    onChange={(value) => handleCredentialChange(provider, 'channelId', value)}
                    disabled={readOnly}
                    helpText="ID do canal do Discord"
                  />
                  <ConfigField
                    label="Guild ID"
                    type="text"
                    value={config.guildId}
                    onChange={(value) => handleCredentialChange(provider, 'guildId', value)}
                    disabled={readOnly}
                    helpText="ID do servidor do Discord"
                  />
                </>
              )}

              {provider === 'telegram' && (
                <>
                  <ConfigField
                    label="Bot Token"
                    type="password"
                    value={config.botToken}
                    onChange={(value) => handleCredentialChange(provider, 'botToken', value)}
                    disabled={readOnly}
                    helpText="Token do bot do Telegram"
                  />
                  <ConfigField
                    label="Chat ID"
                    type="text"
                    value={config.chatId}
                    onChange={(value) => handleCredentialChange(provider, 'chatId', value)}
                    disabled={readOnly}
                    helpText="ID do chat do Telegram"
                  />
                </>
              )}

              {provider === 'whatsapp' && (
                <>
                  <ConfigField
                    label="Access Token"
                    type="password"
                    value={config.accessToken}
                    onChange={(value) => handleCredentialChange(provider, 'accessToken', value)}
                    disabled={readOnly}
                    helpText="Token de acesso do WhatsApp Business"
                  />
                  <ConfigField
                    label="Phone Number ID"
                    type="text"
                    value={config.phoneNumberId}
                    onChange={(value) => handleCredentialChange(provider, 'phoneNumberId', value)}
                    disabled={readOnly}
                    helpText="ID do número de telefone"
                  />
                  <ConfigField
                    label="Business Account ID"
                    type="text"
                    value={config.businessAccountId}
                    onChange={(value) => handleCredentialChange(provider, 'businessAccountId', value)}
                    disabled={readOnly}
                    helpText="ID da conta business"
                  />
                </>
              )}

              {provider === 'email' && (
                <>
                  <ConfigField
                    label="SMTP Host"
                    type="text"
                    value={config.smtpHost}
                    onChange={(value) => handleCredentialChange(provider, 'smtpHost', value)}
                    disabled={readOnly}
                    helpText="Servidor SMTP (smtp.gmail.com)"
                  />
                  <ConfigField
                    label="SMTP Port"
                    type="number"
                    value={config.smtpPort}
                    onChange={(value) => handleCredentialChange(provider, 'smtpPort', value)}
                    min={1}
                    max={65535}
                    disabled={readOnly}
                    helpText="Porta do servidor SMTP"
                  />
                  <ConfigField
                    label="SMTP User"
                    type="text"
                    value={config.smtpUser}
                    onChange={(value) => handleCredentialChange(provider, 'smtpUser', value)}
                    disabled={readOnly}
                    helpText="Usuário do SMTP"
                  />
                  <ConfigField
                    label="SMTP Password"
                    type="password"
                    value={config.smtpPassword}
                    onChange={(value) => handleCredentialChange(provider, 'smtpPassword', value)}
                    disabled={readOnly}
                    helpText="Senha do SMTP"
                  />
                  <ConfigField
                    label="From Email"
                    type="text"
                    value={config.fromEmail}
                    onChange={(value) => handleCredentialChange(provider, 'fromEmail', value)}
                    disabled={readOnly}
                    helpText="Email remetente"
                  />
                  <ConfigField
                    label="From Name"
                    type="text"
                    value={config.fromName}
                    onChange={(value) => handleCredentialChange(provider, 'fromName', value)}
                    disabled={readOnly}
                    helpText="Nome do remetente"
                  />
                  <ConfigField
                    label="Encryption"
                    type="select"
                    value={config.encryption}
                    onChange={(value) => handleConfigChange(`${provider}.encryption`, value)}
                    options={[
                      { label: 'None', value: 'none' },
                      { label: 'SSL', value: 'ssl' },
                      { label: 'TLS', value: 'tls' }
                    ]}
                    disabled={readOnly}
                    helpText="Tipo de criptografia"
                  />
                </>
              )}

              {/* Campos comuns */}
              <ConfigField
                label="API Version"
                type="text"
                value={config.apiVersion}
                onChange={(value) => handleConfigChange(`${provider}.apiVersion`, value)}
                disabled={readOnly}
                helpText="Versão da API"
              />

              <ConfigField
                label="Rate Limit"
                type="number"
                value={config.rateLimit}
                onChange={(value) => handleConfigChange(`${provider}.rateLimit`, value)}
                min={1}
                max={1000}
                disabled={readOnly}
                helpText="Limite de requisições por minuto"
              />

              {/* Botão de validação */}
              <div style={{ gridColumn: '1 / -1', marginTop: '8px' }}>
                <button
                  onClick={() => handleValidateNotification(provider)}
                  disabled={readOnly || !config.enabled || validationStatus[provider] === 'loading'}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: colors.primary.primary,
                    color: colors.text.white,
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: typography.sizes.sm,
                    cursor: 'pointer',
                    opacity: readOnly || !config.enabled || validationStatus[provider] === 'loading' ? 0.5 : 1
                  }}
                >
                  {validationStatus[provider] === 'loading' ? 'Validando...' : 'Validar Credenciais'}
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
          🔔 Configurações de Notificações
        </h2>
        <p style={{
          fontSize: typography.sizes.sm,
          color: colors.text.secondary,
          margin: 0
        }}>
          Configure as credenciais para envio de notificações
        </p>
      </div>

      {/* Provedores de Notificação */}
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{
          fontSize: typography.sizes.md,
          fontWeight: typography.weights.semibold,
          color: colors.text.primary,
          margin: '0 0 16px 0'
        }}>
          Provedores de Notificação
        </h3>
        
        {renderProviderSection('slack', notificationsConfig.slack)}
        {renderProviderSection('discord', notificationsConfig.discord)}
        {renderProviderSection('telegram', notificationsConfig.telegram)}
        {renderProviderSection('whatsapp', notificationsConfig.whatsapp)}
        {renderProviderSection('email', notificationsConfig.email)}
      </div>

      {/* Configurações Gerais */}
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{
          fontSize: typography.sizes.md,
          fontWeight: typography.weights.semibold,
          color: colors.text.primary,
          margin: '0 0 16px 0'
        }}>
          ⚙️ Configurações Gerais
        </h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <ConfigField
            label="Provedor Padrão"
            type="select"
            value={notificationsConfig.general.defaultProvider}
            onChange={(value) => handleConfigChange('general.defaultProvider', value)}
            options={[
              { label: 'Slack', value: 'slack' },
              { label: 'Discord', value: 'discord' },
              { label: 'Telegram', value: 'telegram' },
              { label: 'WhatsApp', value: 'whatsapp' },
              { label: 'Email', value: 'email' }
            ]}
            disabled={readOnly}
            helpText="Provedor padrão para novas notificações"
          />

          <ConfigField
            label="Tentativas de Reenvio"
            type="number"
            value={notificationsConfig.general.retryAttempts}
            onChange={(value) => handleConfigChange('general.retryAttempts', value)}
            min={1}
            max={10}
            disabled={readOnly}
            helpText="Número de tentativas em caso de falha"
          />

          <ConfigField
            label="Delay de Reenvio (ms)"
            type="number"
            value={notificationsConfig.general.retryDelay}
            onChange={(value) => handleConfigChange('general.retryDelay', value)}
            min={100}
            max={10000}
            step={100}
            disabled={readOnly}
            helpText="Tempo entre tentativas de reenvio"
          />

          <ConfigField
            label="Envio em Lote"
            type="boolean"
            value={notificationsConfig.general.batchEnabled}
            onChange={(value) => handleConfigChange('general.batchEnabled', value)}
            disabled={readOnly}
            helpText="Agrupar notificações em lotes"
          />

          <ConfigField
            label="Tamanho do Lote"
            type="number"
            value={notificationsConfig.general.batchSize}
            onChange={(value) => handleConfigChange('general.batchSize', value)}
            min={1}
            max={1000}
            disabled={readOnly || !notificationsConfig.general.batchEnabled}
            helpText="Número de notificações por lote"
          />

          <ConfigField
            label="Delay do Lote (ms)"
            type="number"
            value={notificationsConfig.general.batchDelay}
            onChange={(value) => handleConfigChange('general.batchDelay', value)}
            min={100}
            max={10000}
            step={100}
            disabled={readOnly || !notificationsConfig.general.batchEnabled}
            helpText="Tempo entre envios de lotes"
          />
        </div>
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
            value={notificationsConfig.validation.enabled}
            onChange={(value) => handleConfigChange('validation.enabled', value)}
            disabled={readOnly}
            helpText="Validar credenciais automaticamente"
          />

          <ConfigField
            label="Validação em Tempo Real"
            type="boolean"
            value={notificationsConfig.validation.realTime}
            onChange={(value) => handleConfigChange('validation.realTime', value)}
            disabled={readOnly || !notificationsConfig.validation.enabled}
            helpText="Validar conforme o usuário digita"
          />

          <ConfigField
            label="Rate Limit (req/min)"
            type="number"
            value={notificationsConfig.validation.rateLimit}
            onChange={(value) => handleConfigChange('validation.rateLimit', value)}
            min={1}
            max={1000}
            disabled={readOnly || !notificationsConfig.validation.enabled}
            helpText="Limite de validações por minuto"
          />

          <ConfigField
            label="Timeout (ms)"
            type="number"
            value={notificationsConfig.validation.timeout}
            onChange={(value) => handleConfigChange('validation.timeout', value)}
            min={1000}
            max={60000}
            step={1000}
            disabled={readOnly || !notificationsConfig.validation.enabled}
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
            {JSON.stringify(notificationsConfig, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default NotificationsConfigSection; 
/**
 * AnalyticsConfigSection.tsx
 * 
 * Componente para gerenciar configurações de Analytics
 * Integração com Google Analytics, SEMrush, Ahrefs e Google Search Console
 * 
 * Tracing ID: UI-012
 * Data/Hora: 2024-12-27 17:00:00 UTC
 * Versão: 1.0
 */

import React, { useState } from 'react';
import { colors } from '../../ui/theme/colors';
import { typography } from '../../ui/theme/typography';

// Tipos para o componente
interface AnalyticsConfigSectionProps {
  /** ID único do componente */
  id?: string;
  /** Classes CSS adicionais */
  className?: string;
  /** Estilo inline customizado */
  style?: React.CSSProperties;
  /** Configurações de analytics */
  analyticsConfig: {
    google_analytics: {
      clientId: string;
      clientSecret: string;
      refreshToken: string;
      viewId: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    semrush: {
      apiKey: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    ahrefs: {
      apiKey: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    google_search_console: {
      clientId: string;
      clientSecret: string;
      refreshToken: string;
      siteUrl: string;
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
  onChange?: (analyticsConfig: any) => void;
  /** Função de callback para validação */
  onValidate?: (provider: string, credentials: any) => Promise<boolean>;
  /** Permitir edição */
  readOnly?: boolean;
  /** Mostrar modo de desenvolvimento */
  showDevMode?: boolean;
}

// Hook para validação de API
const useAnalyticsValidation = () => {
  const [validationStatus, setValidationStatus] = useState<Record<string, 'idle' | 'loading' | 'success' | 'error'>>({});
  const [validationMessage, setValidationMessage] = useState<Record<string, string>>({});

  const validateAnalytics = async (provider: string, credentials: any) => {
    setValidationStatus(prev => ({ ...prev, [provider]: 'loading' }));
    setValidationMessage(prev => ({ ...prev, [provider]: 'Validando...' }));

    try {
      // Simular validação - em produção, chamar endpoint real
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Validação básica de formato
      const isValid = validateAnalyticsCredentials(provider, credentials);
      
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

  const validateAnalyticsCredentials = (provider: string, credentials: any): boolean => {
    switch (provider) {
      case 'google_analytics':
        return !!(credentials.clientId && credentials.clientSecret && credentials.viewId);
      case 'semrush':
        return !!(credentials.apiKey && credentials.apiKey.length > 10);
      case 'ahrefs':
        return !!(credentials.apiKey && credentials.apiKey.length > 10);
      case 'google_search_console':
        return !!(credentials.clientId && credentials.clientSecret && credentials.siteUrl);
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
    validateAnalytics,
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
export const AnalyticsConfigSection: React.FC<AnalyticsConfigSectionProps> = ({
  id = 'analytics-config-section',
  className = '',
  style = {},
  analyticsConfig,
  onChange,
  onValidate,
  readOnly = false,
  showDevMode = false
}) => {
  const [expandedProviders, setExpandedProviders] = useState<Record<string, boolean>>({
    google_analytics: true,
    semrush: false,
    ahrefs: false,
    google_search_console: false
  });

  const {
    validationStatus,
    validationMessage,
    validateAnalytics,
    resetValidation
  } = useAnalyticsValidation();

  const handleConfigChange = (path: string, value: any) => {
    const newConfig = { ...analyticsConfig };
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

  const handleValidateAnalytics = async (provider: string) => {
    const credentials = analyticsConfig[provider as keyof typeof analyticsConfig];
    await validateAnalytics(provider, credentials);
  };

  const toggleProvider = (provider: string) => {
    setExpandedProviders(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }));
  };

  const renderProviderSection = (provider: string, config: any) => {
    const providerNames = {
      google_analytics: 'Google Analytics',
      semrush: 'SEMrush',
      ahrefs: 'Ahrefs',
      google_search_console: 'Google Search Console'
    };

    const providerIcons = {
      google_analytics: '📊',
      semrush: '🔍',
      ahrefs: '📈',
      google_search_console: '🔎'
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
              {provider === 'google_analytics' && (
                <>
                  <ConfigField
                    label="Client ID"
                    type="text"
                    value={config.clientId}
                    onChange={(value) => handleCredentialChange(provider, 'clientId', value)}
                    disabled={readOnly}
                    helpText="ID do cliente Google Analytics"
                  />
                  <ConfigField
                    label="Client Secret"
                    type="password"
                    value={config.clientSecret}
                    onChange={(value) => handleCredentialChange(provider, 'clientSecret', value)}
                    disabled={readOnly}
                    helpText="Segredo do cliente Google Analytics"
                  />
                  <ConfigField
                    label="Refresh Token"
                    type="password"
                    value={config.refreshToken}
                    onChange={(value) => handleCredentialChange(provider, 'refreshToken', value)}
                    disabled={readOnly}
                    helpText="Token de atualização OAuth"
                  />
                  <ConfigField
                    label="View ID"
                    type="text"
                    value={config.viewId}
                    onChange={(value) => handleCredentialChange(provider, 'viewId', value)}
                    disabled={readOnly}
                    helpText="ID da visualização (ga:123456789)"
                  />
                </>
              )}

              {provider === 'semrush' && (
                <>
                  <ConfigField
                    label="API Key"
                    type="password"
                    value={config.apiKey}
                    onChange={(value) => handleCredentialChange(provider, 'apiKey', value)}
                    disabled={readOnly}
                    helpText="Chave da API SEMrush"
                  />
                </>
              )}

              {provider === 'ahrefs' && (
                <>
                  <ConfigField
                    label="API Key"
                    type="password"
                    value={config.apiKey}
                    onChange={(value) => handleCredentialChange(provider, 'apiKey', value)}
                    disabled={readOnly}
                    helpText="Chave da API Ahrefs"
                  />
                </>
              )}

              {provider === 'google_search_console' && (
                <>
                  <ConfigField
                    label="Client ID"
                    type="text"
                    value={config.clientId}
                    onChange={(value) => handleCredentialChange(provider, 'clientId', value)}
                    disabled={readOnly}
                    helpText="ID do cliente Google Search Console"
                  />
                  <ConfigField
                    label="Client Secret"
                    type="password"
                    value={config.clientSecret}
                    onChange={(value) => handleCredentialChange(provider, 'clientSecret', value)}
                    disabled={readOnly}
                    helpText="Segredo do cliente Google Search Console"
                  />
                  <ConfigField
                    label="Refresh Token"
                    type="password"
                    value={config.refreshToken}
                    onChange={(value) => handleCredentialChange(provider, 'refreshToken', value)}
                    disabled={readOnly}
                    helpText="Token de atualização OAuth"
                  />
                  <ConfigField
                    label="Site URL"
                    type="text"
                    value={config.siteUrl}
                    onChange={(value) => handleCredentialChange(provider, 'siteUrl', value)}
                    disabled={readOnly}
                    helpText="URL do site (https://example.com)"
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
                label="Rate Limit (req/min)"
                type="number"
                value={config.rateLimit}
                onChange={(value) => handleConfigChange(`${provider}.rateLimit`, value)}
                min={1}
                max={1000}
                disabled={readOnly}
                helpText="Limite de requisições por minuto"
              />

              {/* Botão de validação */}
              <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  onClick={() => handleValidateAnalytics(provider)}
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
          📊 Configurações de Analytics
        </h2>
        <p style={{
          fontSize: typography.sizes.sm,
          color: colors.text.secondary,
          margin: 0
        }}>
          Configure as credenciais para análise de dados e SEO
        </p>
      </div>

      {/* Provedores de Analytics */}
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{
          fontSize: typography.sizes.md,
          fontWeight: typography.weights.semibold,
          color: colors.text.primary,
          margin: '0 0 16px 0'
        }}>
          Provedores de Analytics
        </h3>
        
        {renderProviderSection('google_analytics', analyticsConfig.google_analytics)}
        {renderProviderSection('semrush', analyticsConfig.semrush)}
        {renderProviderSection('ahrefs', analyticsConfig.ahrefs)}
        {renderProviderSection('google_search_console', analyticsConfig.google_search_console)}
      </div>

      {/* Configurações de Validação */}
      <div style={{ marginBottom: '24px' }}>
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
            value={analyticsConfig.validation.enabled}
            onChange={(value) => handleConfigChange('validation.enabled', value)}
            disabled={readOnly}
            helpText="Validar credenciais automaticamente"
          />

          <ConfigField
            label="Validação em Tempo Real"
            type="boolean"
            value={analyticsConfig.validation.realTime}
            onChange={(value) => handleConfigChange('validation.realTime', value)}
            disabled={readOnly || !analyticsConfig.validation.enabled}
            helpText="Validar conforme o usuário digita"
          />

          <ConfigField
            label="Rate Limit (req/min)"
            type="number"
            value={analyticsConfig.validation.rateLimit}
            onChange={(value) => handleConfigChange('validation.rateLimit', value)}
            min={1}
            max={1000}
            disabled={readOnly || !analyticsConfig.validation.enabled}
            helpText="Limite de validações por minuto"
          />

          <ConfigField
            label="Timeout (ms)"
            type="number"
            value={analyticsConfig.validation.timeout}
            onChange={(value) => handleConfigChange('validation.timeout', value)}
            min={1000}
            max={60000}
            step={1000}
            disabled={readOnly || !analyticsConfig.validation.enabled}
            helpText="Tempo limite para validação"
          />
        </div>
      </div>

      {/* Modo de desenvolvimento */}
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
            {JSON.stringify(analyticsConfig, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default AnalyticsConfigSection; 
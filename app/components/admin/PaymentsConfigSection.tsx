/**
 * PaymentsConfigSection.tsx
 * 
 * Componente para gerenciar configurações de Pagamentos
 * Integração com Stripe, PayPal, Mercado Pago e PIX
 * 
 * Tracing ID: UI-011
 * Data/Hora: 2024-12-27 16:30:00 UTC
 * Versão: 1.0
 */

import React, { useState } from 'react';
import { colors } from '../../ui/theme/colors';
import { typography } from '../../ui/theme/typography';

// Tipos para o componente
interface PaymentsConfigSectionProps {
  /** ID único do componente */
  id?: string;
  /** Classes CSS adicionais */
  className?: string;
  /** Estilo inline customizado */
  style?: React.CSSProperties;
  /** Configurações de pagamentos */
  paymentsConfig: {
    stripe: {
      apiKey: string;
      webhookSecret: string;
      publishableKey: string;
      enabled: boolean;
      apiVersion: string;
      currency: string;
      webhookUrl: string;
    };
    paypal: {
      clientId: string;
      clientSecret: string;
      mode: 'sandbox' | 'live';
      enabled: boolean;
      apiVersion: string;
      currency: string;
      webhookUrl: string;
    };
    mercadopago: {
      accessToken: string;
      publicKey: string;
      enabled: boolean;
      apiVersion: string;
      currency: string;
      webhookUrl: string;
    };
    pix: {
      merchantId: string;
      merchantKey: string;
      enabled: boolean;
      apiVersion: string;
      webhookUrl: string;
    };
    general: {
      defaultProvider: 'stripe' | 'paypal' | 'mercadopago' | 'pix';
      autoCapture: boolean;
      refundEnabled: boolean;
      subscriptionEnabled: boolean;
      webhookRetries: number;
      webhookTimeout: number;
    };
    validation: {
      enabled: boolean;
      realTime: boolean;
      rateLimit: number;
      timeout: number;
    };
  };
  /** Função de callback para mudanças */
  onChange?: (paymentsConfig: any) => void;
  /** Função de callback para validação */
  onValidate?: (provider: string, credentials: any) => Promise<boolean>;
  /** Permitir edição */
  readOnly?: boolean;
  /** Mostrar modo de desenvolvimento */
  showDevMode?: boolean;
}

// Hook para validação de API
const usePaymentsValidation = () => {
  const [validationStatus, setValidationStatus] = useState<Record<string, 'idle' | 'loading' | 'success' | 'error'>>({});
  const [validationMessage, setValidationMessage] = useState<Record<string, string>>({});

  const validatePayment = async (provider: string, credentials: any) => {
    setValidationStatus(prev => ({ ...prev, [provider]: 'loading' }));
    setValidationMessage(prev => ({ ...prev, [provider]: 'Validando...' }));

    try {
      // Simular validação - em produção, chamar endpoint real
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Validação básica de formato
      const isValid = validatePaymentCredentials(provider, credentials);
      
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

  const validatePaymentCredentials = (provider: string, credentials: any): boolean => {
    switch (provider) {
      case 'stripe':
        return !!(credentials.apiKey && credentials.publishableKey);
      case 'paypal':
        return !!(credentials.clientId && credentials.clientSecret);
      case 'mercadopago':
        return !!(credentials.accessToken && credentials.publicKey);
      case 'pix':
        return !!(credentials.merchantId && credentials.merchantKey);
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
    validatePayment,
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
export const PaymentsConfigSection: React.FC<PaymentsConfigSectionProps> = ({
  id = 'payments-config-section',
  className = '',
  style = {},
  paymentsConfig,
  onChange,
  onValidate,
  readOnly = false,
  showDevMode = false
}) => {
  const [expandedProviders, setExpandedProviders] = useState<Record<string, boolean>>({
    stripe: true,
    paypal: false,
    mercadopago: false,
    pix: false
  });

  const {
    validationStatus,
    validationMessage,
    validatePayment,
    resetValidation
  } = usePaymentsValidation();

  const handleConfigChange = (path: string, value: any) => {
    const newConfig = { ...paymentsConfig };
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

  const handleValidatePayment = async (provider: string) => {
    const credentials = paymentsConfig[provider as keyof typeof paymentsConfig];
    await validatePayment(provider, credentials);
  };

  const toggleProvider = (provider: string) => {
    setExpandedProviders(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }));
  };

  const renderProviderSection = (provider: string, config: any) => {
    const providerNames = {
      stripe: 'Stripe',
      paypal: 'PayPal',
      mercadopago: 'Mercado Pago',
      pix: 'PIX'
    };

    const providerIcons = {
      stripe: '💳',
      paypal: '🔵',
      mercadopago: '🟡',
      pix: '📱'
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
              {provider === 'stripe' && (
                <>
                  <ConfigField
                    label="API Key"
                    type="password"
                    value={config.apiKey}
                    onChange={(value) => handleCredentialChange(provider, 'apiKey', value)}
                    disabled={readOnly}
                    helpText="Chave secreta do Stripe (sk_...)"
                  />
                  <ConfigField
                    label="Publishable Key"
                    type="text"
                    value={config.publishableKey}
                    onChange={(value) => handleCredentialChange(provider, 'publishableKey', value)}
                    disabled={readOnly}
                    helpText="Chave pública do Stripe (pk_...)"
                  />
                  <ConfigField
                    label="Webhook Secret"
                    type="password"
                    value={config.webhookSecret}
                    onChange={(value) => handleCredentialChange(provider, 'webhookSecret', value)}
                    disabled={readOnly}
                    helpText="Segredo do webhook (whsec_...)"
                  />
                  <ConfigField
                    label="Webhook URL"
                    type="text"
                    value={config.webhookUrl}
                    onChange={(value) => handleConfigChange(`${provider}.webhookUrl`, value)}
                    disabled={readOnly}
                    helpText="URL para receber webhooks"
                  />
                </>
              )}

              {provider === 'paypal' && (
                <>
                  <ConfigField
                    label="Client ID"
                    type="text"
                    value={config.clientId}
                    onChange={(value) => handleCredentialChange(provider, 'clientId', value)}
                    disabled={readOnly}
                    helpText="ID do cliente PayPal"
                  />
                  <ConfigField
                    label="Client Secret"
                    type="password"
                    value={config.clientSecret}
                    onChange={(value) => handleCredentialChange(provider, 'clientSecret', value)}
                    disabled={readOnly}
                    helpText="Segredo do cliente PayPal"
                  />
                  <ConfigField
                    label="Mode"
                    type="select"
                    value={config.mode}
                    onChange={(value) => handleConfigChange(`${provider}.mode`, value)}
                    options={[
                      { label: 'Sandbox', value: 'sandbox' },
                      { label: 'Live', value: 'live' }
                    ]}
                    disabled={readOnly}
                    helpText="Ambiente de teste ou produção"
                  />
                  <ConfigField
                    label="Webhook URL"
                    type="text"
                    value={config.webhookUrl}
                    onChange={(value) => handleConfigChange(`${provider}.webhookUrl`, value)}
                    disabled={readOnly}
                    helpText="URL para receber webhooks"
                  />
                </>
              )}

              {provider === 'mercadopago' && (
                <>
                  <ConfigField
                    label="Access Token"
                    type="password"
                    value={config.accessToken}
                    onChange={(value) => handleCredentialChange(provider, 'accessToken', value)}
                    disabled={readOnly}
                    helpText="Token de acesso do Mercado Pago"
                  />
                  <ConfigField
                    label="Public Key"
                    type="text"
                    value={config.publicKey}
                    onChange={(value) => handleCredentialChange(provider, 'publicKey', value)}
                    disabled={readOnly}
                    helpText="Chave pública do Mercado Pago"
                  />
                  <ConfigField
                    label="Webhook URL"
                    type="text"
                    value={config.webhookUrl}
                    onChange={(value) => handleConfigChange(`${provider}.webhookUrl`, value)}
                    disabled={readOnly}
                    helpText="URL para receber webhooks"
                  />
                </>
              )}

              {provider === 'pix' && (
                <>
                  <ConfigField
                    label="Merchant ID"
                    type="text"
                    value={config.merchantId}
                    onChange={(value) => handleCredentialChange(provider, 'merchantId', value)}
                    disabled={readOnly}
                    helpText="ID do comerciante PIX"
                  />
                  <ConfigField
                    label="Merchant Key"
                    type="password"
                    value={config.merchantKey}
                    onChange={(value) => handleCredentialChange(provider, 'merchantKey', value)}
                    disabled={readOnly}
                    helpText="Chave do comerciante PIX"
                  />
                  <ConfigField
                    label="Webhook URL"
                    type="text"
                    value={config.webhookUrl}
                    onChange={(value) => handleConfigChange(`${provider}.webhookUrl`, value)}
                    disabled={readOnly}
                    helpText="URL para receber webhooks"
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
                label="Currency"
                type="text"
                value={config.currency}
                onChange={(value) => handleConfigChange(`${provider}.currency`, value)}
                disabled={readOnly}
                helpText="Moeda padrão (BRL, USD, EUR)"
              />

              {/* Botão de validação */}
              <div style={{ gridColumn: '1 / -1', marginTop: '8px' }}>
                <button
                  onClick={() => handleValidatePayment(provider)}
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
          💳 Configurações de Pagamentos
        </h2>
        <p style={{
          fontSize: typography.sizes.sm,
          color: colors.text.secondary,
          margin: 0
        }}>
          Configure as credenciais para processamento de pagamentos
        </p>
      </div>

      {/* Provedores de Pagamento */}
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{
          fontSize: typography.sizes.md,
          fontWeight: typography.weights.semibold,
          color: colors.text.primary,
          margin: '0 0 16px 0'
        }}>
          Provedores de Pagamento
        </h3>
        
        {renderProviderSection('stripe', paymentsConfig.stripe)}
        {renderProviderSection('paypal', paymentsConfig.paypal)}
        {renderProviderSection('mercadopago', paymentsConfig.mercadopago)}
        {renderProviderSection('pix', paymentsConfig.pix)}
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
            value={paymentsConfig.general.defaultProvider}
            onChange={(value) => handleConfigChange('general.defaultProvider', value)}
            options={[
              { label: 'Stripe', value: 'stripe' },
              { label: 'PayPal', value: 'paypal' },
              { label: 'Mercado Pago', value: 'mercadopago' },
              { label: 'PIX', value: 'pix' }
            ]}
            disabled={readOnly}
            helpText="Provedor padrão para novos pagamentos"
          />

          <ConfigField
            label="Captura Automática"
            type="boolean"
            value={paymentsConfig.general.autoCapture}
            onChange={(value) => handleConfigChange('general.autoCapture', value)}
            disabled={readOnly}
            helpText="Capturar pagamentos automaticamente"
          />

          <ConfigField
            label="Reembolso Habilitado"
            type="boolean"
            value={paymentsConfig.general.refundEnabled}
            onChange={(value) => handleConfigChange('general.refundEnabled', value)}
            disabled={readOnly}
            helpText="Permitir reembolsos"
          />

          <ConfigField
            label="Assinaturas Habilitadas"
            type="boolean"
            value={paymentsConfig.general.subscriptionEnabled}
            onChange={(value) => handleConfigChange('general.subscriptionEnabled', value)}
            disabled={readOnly}
            helpText="Suporte a assinaturas recorrentes"
          />

          <ConfigField
            label="Tentativas de Webhook"
            type="number"
            value={paymentsConfig.general.webhookRetries}
            onChange={(value) => handleConfigChange('general.webhookRetries', value)}
            min={1}
            max={10}
            disabled={readOnly}
            helpText="Número de tentativas para webhooks"
          />

          <ConfigField
            label="Timeout do Webhook (ms)"
            type="number"
            value={paymentsConfig.general.webhookTimeout}
            onChange={(value) => handleConfigChange('general.webhookTimeout', value)}
            min={1000}
            max={30000}
            step={1000}
            disabled={readOnly}
            helpText="Tempo limite para webhooks"
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
            value={paymentsConfig.validation.enabled}
            onChange={(value) => handleConfigChange('validation.enabled', value)}
            disabled={readOnly}
            helpText="Validar credenciais automaticamente"
          />

          <ConfigField
            label="Validação em Tempo Real"
            type="boolean"
            value={paymentsConfig.validation.realTime}
            onChange={(value) => handleConfigChange('validation.realTime', value)}
            disabled={readOnly || !paymentsConfig.validation.enabled}
            helpText="Validar conforme o usuário digita"
          />

          <ConfigField
            label="Rate Limit (req/min)"
            type="number"
            value={paymentsConfig.validation.rateLimit}
            onChange={(value) => handleConfigChange('validation.rateLimit', value)}
            min={1}
            max={1000}
            disabled={readOnly || !paymentsConfig.validation.enabled}
            helpText="Limite de validações por minuto"
          />

          <ConfigField
            label="Timeout (ms)"
            type="number"
            value={paymentsConfig.validation.timeout}
            onChange={(value) => handleConfigChange('validation.timeout', value)}
            min={1000}
            max={60000}
            step={1000}
            disabled={readOnly || !paymentsConfig.validation.enabled}
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
            {JSON.stringify(paymentsConfig, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default PaymentsConfigSection; 
/**
 * AIConfigSection.tsx
 * 
 * Componente para gerenciar configurações de IAs Generativas
 * Integração com DeepSeek, OpenAI, Claude e Gemini
 * 
 * Tracing ID: UI-009
 * Data/Hora: 2024-12-27 15:30:00 UTC
 * Versão: 1.0
 */

import React, { useState, useEffect } from 'react';
import { colors } from '../../ui/theme/colors';
import { typography } from '../../ui/theme/typography';

// Tipos para o componente
interface AIConfigSectionProps {
  /** ID único do componente */
  id?: string;
  /** Classes CSS adicionais */
  className?: string;
  /** Estilo inline customizado */
  style?: React.CSSProperties;
  /** Configurações de IA */
  aiConfig: {
    defaultProvider: 'deepseek' | 'openai' | 'claude' | 'gemini';
    deepseek: {
      apiKey: string;
      enabled: boolean;
      model: string;
      maxTokens: number;
      temperature: number;
    };
    openai: {
      apiKey: string;
      enabled: boolean;
      model: string;
      maxTokens: number;
      temperature: number;
    };
    claude: {
      apiKey: string;
      enabled: boolean;
      model: string;
      maxTokens: number;
      temperature: number;
    };
    gemini: {
      apiKey: string;
      enabled: boolean;
      model: string;
      maxTokens: number;
      temperature: number;
    };
    fallback: {
      enabled: boolean;
      strategy: 'round_robin' | 'performance_based' | 'cost_based';
      maxRetries: number;
      retryDelay: number;
    };
    validation: {
      enabled: boolean;
      realTime: boolean;
      rateLimit: number;
      timeout: number;
    };
  };
  /** Função de callback para mudanças */
  onChange?: (aiConfig: any) => void;
  /** Função de callback para validação */
  onValidate?: (provider: string, apiKey: string) => Promise<boolean>;
  /** Permitir edição */
  readOnly?: boolean;
  /** Mostrar modo de desenvolvimento */
  showDevMode?: boolean;
}

// Hook para validação de API
const useAPIValidation = () => {
  const [validationStatus, setValidationStatus] = useState<Record<string, 'idle' | 'loading' | 'success' | 'error'>>({});
  const [validationMessage, setValidationMessage] = useState<Record<string, string>>({});

  const validateAPI = async (provider: string, apiKey: string) => {
    if (!apiKey.trim()) {
      setValidationStatus(prev => ({ ...prev, [provider]: 'error' }));
      setValidationMessage(prev => ({ ...prev, [provider]: 'API Key é obrigatória' }));
      return false;
    }

    setValidationStatus(prev => ({ ...prev, [provider]: 'loading' }));
    setValidationMessage(prev => ({ ...prev, [provider]: 'Validando...' }));

    try {
      // Simular validação - em produção, chamar endpoint real
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Validação básica de formato
      const isValid = validateAPIKeyFormat(provider, apiKey);
      
      if (isValid) {
        setValidationStatus(prev => ({ ...prev, [provider]: 'success' }));
        setValidationMessage(prev => ({ ...prev, [provider]: 'API Key válida' }));
        return true;
      } else {
        setValidationStatus(prev => ({ ...prev, [provider]: 'error' }));
        setValidationMessage(prev => ({ ...prev, [provider]: 'Formato inválido' }));
        return false;
      }
    } catch (error) {
      setValidationStatus(prev => ({ ...prev, [provider]: 'error' }));
      setValidationMessage(prev => ({ ...prev, [provider]: 'Erro na validação' }));
      return false;
    }
  };

  const validateAPIKeyFormat = (provider: string, apiKey: string): boolean => {
    const patterns = {
      deepseek: /^sk-[a-zA-Z0-9]{32,}$/,
      openai: /^sk-[a-zA-Z0-9]{32,}$/,
      claude: /^sk-ant-[a-zA-Z0-9]{32,}$/,
      gemini: /^AIza[a-zA-Z0-9]{35}$/
    };

    const pattern = patterns[provider as keyof typeof patterns];
    return pattern ? pattern.test(apiKey) : false;
  };

  const resetValidation = (provider: string) => {
    setValidationStatus(prev => ({ ...prev, [provider]: 'idle' }));
    setValidationMessage(prev => ({ ...prev, [provider]: '' }));
  };

  return {
    validationStatus,
    validationMessage,
    validateAPI,
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
export const AIConfigSection: React.FC<AIConfigSectionProps> = ({
  id = 'ai-config-section',
  className = '',
  style = {},
  aiConfig,
  onChange,
  onValidate,
  readOnly = false,
  showDevMode = false
}) => {
  const [expandedProviders, setExpandedProviders] = useState<Record<string, boolean>>({
    deepseek: true,
    openai: false,
    claude: false,
    gemini: false
  });

  const {
    validationStatus,
    validationMessage,
    validateAPI,
    resetValidation
  } = useAPIValidation();

  const handleConfigChange = (path: string, value: any) => {
    const newConfig = { ...aiConfig };
    const keys = path.split('.');
    let current: any = newConfig;
    
    for (let i = 0; i < keys.length - 1; i++) {
      current = current[keys[i]];
    }
    
    current[keys[keys.length - 1]] = value;
    onChange?.(newConfig);
  };

  const handleAPIKeyChange = (provider: string, value: string) => {
    handleConfigChange(`${provider}.apiKey`, value);
    resetValidation(provider);
  };

  const handleValidateAPI = async (provider: string) => {
    const apiKey = aiConfig[provider as keyof typeof aiConfig]?.apiKey || '';
    await validateAPI(provider, apiKey);
  };

  const toggleProvider = (provider: string) => {
    setExpandedProviders(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }));
  };

  const renderProviderSection = (provider: string, config: any) => {
    const providerNames = {
      deepseek: 'DeepSeek',
      openai: 'OpenAI',
      claude: 'Claude',
      gemini: 'Gemini'
    };

    const providerIcons = {
      deepseek: '🤖',
      openai: '🧠',
      claude: '🎭',
      gemini: '💎'
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
              {/* API Key */}
              <div style={{ gridColumn: '1 / -1' }}>
                <ConfigField
                  label="API Key"
                  type="password"
                  value={config.apiKey}
                  onChange={(value) => handleAPIKeyChange(provider, value)}
                  disabled={readOnly}
                  helpText={`Chave de API do ${providerNames[provider as keyof typeof providerNames]}`}
                  validationStatus={validationStatus[provider]}
                  validationMessage={validationMessage[provider]}
                />
                <button
                  onClick={() => handleValidateAPI(provider)}
                  disabled={readOnly || !config.apiKey || validationStatus[provider] === 'loading'}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: colors.primary.primary,
                    color: colors.text.white,
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: typography.sizes.sm,
                    cursor: 'pointer',
                    opacity: readOnly || !config.apiKey || validationStatus[provider] === 'loading' ? 0.5 : 1
                  }}
                >
                  {validationStatus[provider] === 'loading' ? 'Validando...' : 'Validar API Key'}
                </button>
              </div>

              {/* Modelo */}
              <ConfigField
                label="Modelo"
                type="text"
                value={config.model}
                onChange={(value) => handleConfigChange(`${provider}.model`, value)}
                disabled={readOnly}
                helpText={`Modelo do ${providerNames[provider as keyof typeof providerNames]}`}
              />

              {/* Max Tokens */}
              <ConfigField
                label="Max Tokens"
                type="number"
                value={config.maxTokens}
                onChange={(value) => handleConfigChange(`${provider}.maxTokens`, value)}
                min={1}
                max={8192}
                disabled={readOnly}
                helpText="Número máximo de tokens"
              />

              {/* Temperature */}
              <ConfigField
                label="Temperature"
                type="number"
                value={config.temperature}
                onChange={(value) => handleConfigChange(`${provider}.temperature`, value)}
                min={0}
                max={2}
                step={0.1}
                disabled={readOnly}
                helpText="Criatividade da resposta (0-2)"
              />
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
          🤖 Configurações de IAs Generativas
        </h2>
        <p style={{
          fontSize: typography.sizes.sm,
          color: colors.text.secondary,
          margin: 0
        }}>
          Configure as chaves de API e parâmetros para os provedores de IA
        </p>
      </div>

      {/* Provedor Padrão */}
      <div style={{ marginBottom: '24px' }}>
        <ConfigField
          label="Provedor Padrão"
          type="select"
          value={aiConfig.defaultProvider}
          onChange={(value) => handleConfigChange('defaultProvider', value)}
          options={[
            { label: 'DeepSeek', value: 'deepseek' },
            { label: 'OpenAI', value: 'openai' },
            { label: 'Claude', value: 'claude' },
            { label: 'Gemini', value: 'gemini' }
          ]}
          disabled={readOnly}
          helpText="Provedor usado por padrão quando múltiplos estão habilitados"
        />
      </div>

      {/* Provedores */}
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{
          fontSize: typography.sizes.md,
          fontWeight: typography.weights.semibold,
          color: colors.text.primary,
          margin: '0 0 16px 0'
        }}>
          Provedores de IA
        </h3>
        
        {renderProviderSection('deepseek', aiConfig.deepseek)}
        {renderProviderSection('openai', aiConfig.openai)}
        {renderProviderSection('claude', aiConfig.claude)}
        {renderProviderSection('gemini', aiConfig.gemini)}
      </div>

      {/* Configurações de Fallback */}
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{
          fontSize: typography.sizes.md,
          fontWeight: typography.weights.semibold,
          color: colors.text.primary,
          margin: '0 0 16px 0'
        }}>
          🔄 Configurações de Fallback
        </h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <ConfigField
            label="Fallback Habilitado"
            type="boolean"
            value={aiConfig.fallback.enabled}
            onChange={(value) => handleConfigChange('fallback.enabled', value)}
            disabled={readOnly}
            helpText="Usar outro provedor quando o principal falhar"
          />

          <ConfigField
            label="Estratégia de Fallback"
            type="select"
            value={aiConfig.fallback.strategy}
            onChange={(value) => handleConfigChange('fallback.strategy', value)}
            options={[
              { label: 'Round Robin', value: 'round_robin' },
              { label: 'Baseado em Performance', value: 'performance_based' },
              { label: 'Baseado em Custo', value: 'cost_based' }
            ]}
            disabled={readOnly || !aiConfig.fallback.enabled}
          />

          <ConfigField
            label="Máximo de Tentativas"
            type="number"
            value={aiConfig.fallback.maxRetries}
            onChange={(value) => handleConfigChange('fallback.maxRetries', value)}
            min={1}
            max={10}
            disabled={readOnly || !aiConfig.fallback.enabled}
            helpText="Número máximo de tentativas antes de falhar"
          />

          <ConfigField
            label="Delay entre Tentativas (ms)"
            type="number"
            value={aiConfig.fallback.retryDelay}
            onChange={(value) => handleConfigChange('fallback.retryDelay', value)}
            min={100}
            max={10000}
            step={100}
            disabled={readOnly || !aiConfig.fallback.enabled}
            helpText="Tempo de espera entre tentativas"
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
            value={aiConfig.validation.enabled}
            onChange={(value) => handleConfigChange('validation.enabled', value)}
            disabled={readOnly}
            helpText="Validar API Keys automaticamente"
          />

          <ConfigField
            label="Validação em Tempo Real"
            type="boolean"
            value={aiConfig.validation.realTime}
            onChange={(value) => handleConfigChange('validation.realTime', value)}
            disabled={readOnly || !aiConfig.validation.enabled}
            helpText="Validar conforme o usuário digita"
          />

          <ConfigField
            label="Rate Limit (req/min)"
            type="number"
            value={aiConfig.validation.rateLimit}
            onChange={(value) => handleConfigChange('validation.rateLimit', value)}
            min={1}
            max={1000}
            disabled={readOnly || !aiConfig.validation.enabled}
            helpText="Limite de validações por minuto"
          />

          <ConfigField
            label="Timeout (ms)"
            type="number"
            value={aiConfig.validation.timeout}
            onChange={(value) => handleConfigChange('validation.timeout', value)}
            min={1000}
            max={60000}
            step={1000}
            disabled={readOnly || !aiConfig.validation.enabled}
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
            {JSON.stringify(aiConfig, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default AIConfigSection; 
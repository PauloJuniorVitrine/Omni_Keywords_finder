/**
 * SystemConfig.tsx
 * 
 * Painel centralizado de configurações do sistema
 * Interface unificada para todas as configurações
 * 
 * Tracing ID: UI-008
 * Data/Hora: 2024-12-20 08:45:00 UTC
 * Versão: 1.0
 */

import React, { useState, useEffect, useMemo } from 'react';
import { colors } from '../../ui/theme/colors';
import { typography } from '../../ui/theme/typography';

// Tipos para o componente
interface SystemConfigProps {
  /** ID único do componente */
  id?: string;
  /** Classes CSS adicionais */
  className?: string;
  /** Estilo inline customizado */
  style?: React.CSSProperties;
  /** Configurações iniciais */
  initialConfig?: SystemConfigData;
  /** Função de callback para mudanças */
  onChange?: (config: SystemConfigData) => void;
  /** Função de callback para salvar */
  onSave?: (config: SystemConfigData) => Promise<void>;
  /** Função de callback para resetar */
  onReset?: () => void;
  /** Mostrar modo de desenvolvimento */
  showDevMode?: boolean;
  /** Permitir edição */
  readOnly?: boolean;
}

// Tipos de dados de configuração
interface SystemConfigData {
  // Configurações gerais
  general: {
    appName: string;
    appVersion: string;
    environment: 'development' | 'staging' | 'production';
    timezone: string;
    language: string;
    dateFormat: string;
    timeFormat: string;
    currency: string;
    maxFileSize: number;
    sessionTimeout: number;
  };
  
  // Configurações de segurança
  security: {
    passwordMinLength: number;
    passwordRequireUppercase: boolean;
    passwordRequireLowercase: boolean;
    passwordRequireNumbers: boolean;
    passwordRequireSymbols: boolean;
    maxLoginAttempts: number;
    lockoutDuration: number;
    twoFactorEnabled: boolean;
    sslRequired: boolean;
    corsOrigins: string[];
    apiRateLimit: number;
  };
  
  // Configurações de performance
  performance: {
    cacheEnabled: boolean;
    cacheTTL: number;
    compressionEnabled: boolean;
    gzipLevel: number;
    maxConcurrentRequests: number;
    requestTimeout: number;
    databasePoolSize: number;
    backgroundJobWorkers: number;
    memoryLimit: number;
    cpuLimit: number;
  };
  
  // Configurações de integração
  integration: {
    externalApisEnabled: boolean;
    webhookUrl: string;
    webhookSecret: string;
    emailProvider: string;
    emailConfig: {
      host: string;
      port: number;
      username: string;
      password: string;
      encryption: 'none' | 'ssl' | 'tls';
    };
    smsProvider: string;
    smsConfig: {
      apiKey: string;
      apiSecret: string;
      fromNumber: string;
    };
  };
  
  // Configurações de notificação
  notification: {
    emailNotifications: boolean;
    smsNotifications: boolean;
    pushNotifications: boolean;
    notificationTypes: {
      system: boolean;
      security: boolean;
      performance: boolean;
      user: boolean;
      marketing: boolean;
    };
    quietHours: {
      enabled: boolean;
      startTime: string;
      endTime: string;
      timezone: string;
    };
  };
  
  // Configurações de backup
  backup: {
    autoBackupEnabled: boolean;
    backupFrequency: 'daily' | 'weekly' | 'monthly';
    backupRetention: number;
    backupLocation: 'local' | 'cloud' | 'hybrid';
    cloudProvider: string;
    cloudConfig: {
      bucket: string;
      region: string;
      accessKey: string;
      secretKey: string;
    };
    encryptionEnabled: boolean;
    compressionEnabled: boolean;
  };
  
  // Configurações de logs
  logs: {
    logLevel: 'debug' | 'info' | 'warning' | 'error';
    logRetention: number;
    logFormat: 'json' | 'text';
    logOutput: 'file' | 'console' | 'both';
    logFile: string;
    maxLogSize: number;
    logRotation: boolean;
    auditLogEnabled: boolean;
    performanceLogEnabled: boolean;
  };
  
  // Configurações de API
  api: {
    version: string;
    baseUrl: string;
    corsEnabled: boolean;
    corsOrigins: string[];
    rateLimitEnabled: boolean;
    rateLimitWindow: number;
    rateLimitMax: number;
    authenticationRequired: boolean;
    apiKeyRequired: boolean;
    documentationEnabled: boolean;
  };
  
  // Configurações de banco de dados
  database: {
    type: 'sqlite' | 'postgresql' | 'mysql' | 'mongodb';
    host: string;
    port: number;
    name: string;
    username: string;
    password: string;
    sslEnabled: boolean;
    connectionPool: number;
    timeout: number;
    maxConnections: number;
    migrationsEnabled: boolean;
  };
  
  // Configurações de cache
  cache: {
    type: 'memory' | 'redis' | 'memcached';
    host: string;
    port: number;
    password: string;
    database: number;
    ttl: number;
    maxMemory: number;
    evictionPolicy: 'lru' | 'lfu' | 'fifo';
    compressionEnabled: boolean;
    clusteringEnabled: boolean;
  };
  
  // Configurações de Redes Sociais
  social: {
    // Configurações do Instagram
    instagram: {
      username: string;
      password: string;
      sessionId: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    
    // Configurações do TikTok
    tiktok: {
      apiKey: string;
      apiSecret: string;
      accessToken: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    
    // Configurações do YouTube
    youtube: {
      apiKey: string;
      clientId: string;
      clientSecret: string;
      refreshToken: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    
    // Configurações do Pinterest
    pinterest: {
      accessToken: string;
      appId: string;
      appSecret: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    
    // Configurações do Reddit
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
    
    // Configurações gerais de validação
    validation: {
      enabled: boolean;
      realTime: boolean;
      rateLimit: number;
      timeout: number;
    };
  };
  
  // Configurações de Analytics
  analytics: {
    // Configurações do Google Analytics
    google_analytics: {
      clientId: string;
      clientSecret: string;
      refreshToken: string;
      viewId: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    
    // Configurações do SEMrush
    semrush: {
      apiKey: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    
    // Configurações do Ahrefs
    ahrefs: {
      apiKey: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    
    // Configurações do Google Search Console
    google_search_console: {
      clientId: string;
      clientSecret: string;
      refreshToken: string;
      siteUrl: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    
    // Configurações gerais de validação
    validation: {
      enabled: boolean;
      realTime: boolean;
      rateLimit: number;
      timeout: number;
    };
  };
  
  // Configurações de Pagamentos
  payments: {
    // Configurações do Stripe
    stripe: {
      apiKey: string;
      webhookSecret: string;
      publishableKey: string;
      enabled: boolean;
      apiVersion: string;
      currency: string;
      webhookUrl: string;
    };
    
    // Configurações do PayPal
    paypal: {
      clientId: string;
      clientSecret: string;
      mode: 'sandbox' | 'live';
      enabled: boolean;
      apiVersion: string;
      currency: string;
      webhookUrl: string;
    };
    
    // Configurações do Mercado Pago
    mercadopago: {
      accessToken: string;
      publicKey: string;
      enabled: boolean;
      apiVersion: string;
      currency: string;
      webhookUrl: string;
    };
    
    // Configurações do PIX
    pix: {
      merchantId: string;
      merchantKey: string;
      enabled: boolean;
      apiVersion: string;
      webhookUrl: string;
    };
    
    // Configurações gerais de pagamentos
    general: {
      defaultProvider: 'stripe' | 'paypal' | 'mercadopago' | 'pix';
      autoCapture: boolean;
      refundEnabled: boolean;
      subscriptionEnabled: boolean;
      webhookRetries: number;
      webhookTimeout: number;
    };
    
    // Configurações de validação
    validation: {
      enabled: boolean;
      realTime: boolean;
      rateLimit: number;
      timeout: number;
    };
  };
  
  // Configurações de Notificações
  notifications: {
    // Configurações do Slack
    slack: {
      webhookUrl: string;
      botToken: string;
      channel: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    
    // Configurações do Discord
    discord: {
      botToken: string;
      channelId: string;
      guildId: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    
    // Configurações do Telegram
    telegram: {
      botToken: string;
      chatId: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    
    // Configurações do WhatsApp Business
    whatsapp: {
      accessToken: string;
      phoneNumberId: string;
      businessAccountId: string;
      enabled: boolean;
      apiVersion: string;
      rateLimit: number;
    };
    
    // Configurações do Email
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
    
    // Configurações gerais de notificações
    general: {
      defaultProvider: 'slack' | 'discord' | 'telegram' | 'whatsapp' | 'email';
      retryAttempts: number;
      retryDelay: number;
      batchEnabled: boolean;
      batchSize: number;
      batchDelay: number;
    };
    
    // Configurações de validação
    validation: {
      enabled: boolean;
      realTime: boolean;
      rateLimit: number;
      timeout: number;
    };
  };
  
  // Configurações de IAs Generativas
  ai: {
    // Provedor padrão
    defaultProvider: 'deepseek' | 'openai' | 'claude' | 'gemini';
    
    // Configurações do DeepSeek
    deepseek: {
      apiKey: string;
      enabled: boolean;
      model: string;
      maxTokens: number;
      temperature: number;
    };
    
    // Configurações do OpenAI
    openai: {
      apiKey: string;
      enabled: boolean;
      model: string;
      maxTokens: number;
      temperature: number;
    };
    
    // Configurações do Claude
    claude: {
      apiKey: string;
      enabled: boolean;
      model: string;
      maxTokens: number;
      temperature: number;
    };
    
    // Configurações do Gemini
    gemini: {
      apiKey: string;
      enabled: boolean;
      model: string;
      maxTokens: number;
      temperature: number;
    };
    
    // Configurações gerais de fallback
    fallback: {
      enabled: boolean;
      strategy: 'round_robin' | 'performance_based' | 'cost_based';
      maxRetries: number;
      retryDelay: number;
    };
    
    // Configurações de validação
    validation: {
      enabled: boolean;
      realTime: boolean;
      rateLimit: number;
      timeout: number;
    };
  };
}

// Configuração padrão
const defaultConfig: SystemConfigData = {
  general: {
    appName: 'Omni Keywords Finder',
    appVersion: '1.0.0',
    environment: 'development',
    timezone: 'UTC',
    language: 'pt-BR',
    dateFormat: 'DD/MM/YYYY',
    timeFormat: 'HH:mm:ss',
    currency: 'BRL',
    maxFileSize: 10485760, // 10MB
    sessionTimeout: 3600 // 1 hora
  },
  security: {
    passwordMinLength: 8,
    passwordRequireUppercase: true,
    passwordRequireLowercase: true,
    passwordRequireNumbers: true,
    passwordRequireSymbols: false,
    maxLoginAttempts: 5,
    lockoutDuration: 900, // 15 minutos
    twoFactorEnabled: false,
    sslRequired: true,
    corsOrigins: ['http://localhost:3000'],
    apiRateLimit: 1000
  },
  performance: {
    cacheEnabled: true,
    cacheTTL: 3600,
    compressionEnabled: true,
    gzipLevel: 6,
    maxConcurrentRequests: 100,
    requestTimeout: 30000,
    databasePoolSize: 10,
    backgroundJobWorkers: 4,
    memoryLimit: 512,
    cpuLimit: 2
  },
  integration: {
    externalApisEnabled: true,
    webhookUrl: '',
    webhookSecret: '',
    emailProvider: 'smtp',
    emailConfig: {
      host: 'localhost',
      port: 587,
      username: '',
      password: '',
      encryption: 'tls'
    },
    smsProvider: 'twilio',
    smsConfig: {
      apiKey: '',
      apiSecret: '',
      fromNumber: ''
    }
  },
  notification: {
    emailNotifications: true,
    smsNotifications: false,
    pushNotifications: true,
    notificationTypes: {
      system: true,
      security: true,
      performance: true,
      user: true,
      marketing: false
    },
    quietHours: {
      enabled: false,
      startTime: '22:00',
      endTime: '08:00',
      timezone: 'UTC'
    }
  },
  backup: {
    autoBackupEnabled: true,
    backupFrequency: 'daily',
    backupRetention: 30,
    backupLocation: 'local',
    cloudProvider: 'aws',
    cloudConfig: {
      bucket: '',
      region: 'us-east-1',
      accessKey: '',
      secretKey: ''
    },
    encryptionEnabled: true,
    compressionEnabled: true
  },
  logs: {
    logLevel: 'info',
    logRetention: 90,
    logFormat: 'json',
    logOutput: 'both',
    logFile: '/var/log/omni-keywords-finder.log',
    maxLogSize: 10485760, // 10MB
    logRotation: true,
    auditLogEnabled: true,
    performanceLogEnabled: false
  },
  api: {
    version: 'v1',
    baseUrl: '/api',
    corsEnabled: true,
    corsOrigins: ['http://localhost:3000'],
    rateLimitEnabled: true,
    rateLimitWindow: 900,
    rateLimitMax: 1000,
    authenticationRequired: true,
    apiKeyRequired: false,
    documentationEnabled: true
  },
  database: {
    type: 'sqlite',
    host: 'localhost',
    port: 5432,
    name: 'omni_keywords_finder',
    username: '',
    password: '',
    sslEnabled: false,
    connectionPool: 10,
    timeout: 30000,
    maxConnections: 100,
    migrationsEnabled: true
  },
  cache: {
    type: 'memory',
    host: 'localhost',
    port: 6379,
    password: '',
    database: 0,
    ttl: 3600,
    maxMemory: 100,
    evictionPolicy: 'lru',
    compressionEnabled: false,
    clusteringEnabled: false
  },
  social: {
    instagram: {
      username: '',
      password: '',
      sessionId: '',
      enabled: false,
      apiVersion: 'v1',
      rateLimit: 100
    },
    tiktok: {
      apiKey: '',
      apiSecret: '',
      accessToken: '',
      enabled: false,
      apiVersion: 'v1',
      rateLimit: 100
    },
    youtube: {
      apiKey: '',
      clientId: '',
      clientSecret: '',
      refreshToken: '',
      enabled: false,
      apiVersion: 'v3',
      rateLimit: 100
    },
    pinterest: {
      accessToken: '',
      appId: '',
      appSecret: '',
      enabled: false,
      apiVersion: 'v5',
      rateLimit: 100
    },
    reddit: {
      clientId: '',
      clientSecret: '',
      username: '',
      password: '',
      userAgent: 'OmniKeywordsFinder/1.0',
      enabled: false,
      apiVersion: 'v1',
      rateLimit: 100
    },
    validation: {
      enabled: true,
      realTime: true,
      rateLimit: 100,
      timeout: 30000
    }
  },
  analytics: {
    google_analytics: {
      clientId: '',
      clientSecret: '',
      refreshToken: '',
      viewId: '',
      enabled: false,
      apiVersion: 'v4',
      rateLimit: 100
    },
    semrush: {
      apiKey: '',
      enabled: false,
      apiVersion: 'v3',
      rateLimit: 100
    },
    ahrefs: {
      apiKey: '',
      enabled: false,
      apiVersion: 'v3',
      rateLimit: 100
    },
    google_search_console: {
      clientId: '',
      clientSecret: '',
      refreshToken: '',
      siteUrl: '',
      enabled: false,
      apiVersion: 'v1',
      rateLimit: 100
    },
    validation: {
      enabled: true,
      realTime: true,
      rateLimit: 100,
      timeout: 30000
    }
  },
  payments: {
    stripe: {
      apiKey: '',
      webhookSecret: '',
      publishableKey: '',
      enabled: false,
      apiVersion: '',
      currency: '',
      webhookUrl: ''
    },
    paypal: {
      clientId: '',
      clientSecret: '',
      mode: 'sandbox',
      enabled: false,
      apiVersion: '',
      currency: '',
      webhookUrl: ''
    },
    mercadopago: {
      accessToken: '',
      publicKey: '',
      enabled: false,
      apiVersion: '',
      currency: '',
      webhookUrl: ''
    },
    pix: {
      merchantId: '',
      merchantKey: '',
      enabled: false,
      apiVersion: '',
      webhookUrl: ''
    },
    general: {
      defaultProvider: 'stripe',
      autoCapture: true,
      refundEnabled: true,
      subscriptionEnabled: true,
      webhookRetries: 3,
      webhookTimeout: 10000
    },
    validation: {
      enabled: true,
      realTime: true,
      rateLimit: 100,
      timeout: 30000
    }
  },
  notifications: {
    slack: {
      webhookUrl: '',
      botToken: '',
      channel: '',
      enabled: false,
      apiVersion: '',
      rateLimit: 100
    },
    discord: {
      botToken: '',
      channelId: '',
      guildId: '',
      enabled: false,
      apiVersion: '',
      rateLimit: 100
    },
    telegram: {
      botToken: '',
      chatId: '',
      enabled: false,
      apiVersion: '',
      rateLimit: 100
    },
    whatsapp: {
      accessToken: '',
      phoneNumberId: '',
      businessAccountId: '',
      enabled: false,
      apiVersion: '',
      rateLimit: 100
    },
    email: {
      smtpHost: '',
      smtpPort: 587,
      smtpUser: '',
      smtpPassword: '',
      fromEmail: '',
      fromName: '',
      enabled: false,
      encryption: 'tls'
    },
    general: {
      defaultProvider: 'slack',
      retryAttempts: 3,
      retryDelay: 1000,
      batchEnabled: true,
      batchSize: 100,
      batchDelay: 1000
    },
    validation: {
      enabled: true,
      realTime: true,
      rateLimit: 100,
      timeout: 30000
    }
  },
  ai: {
    defaultProvider: 'deepseek',
    deepseek: {
      apiKey: '',
      enabled: true,
      model: 'deepseek-chat',
      maxTokens: 4096,
      temperature: 0.7
    },
    openai: {
      apiKey: '',
      enabled: false,
      model: 'gpt-4',
      maxTokens: 4096,
      temperature: 0.7
    },
    claude: {
      apiKey: '',
      enabled: false,
      model: 'claude-3-sonnet',
      maxTokens: 4096,
      temperature: 0.7
    },
    gemini: {
      apiKey: '',
      enabled: false,
      model: 'gemini-pro',
      maxTokens: 4096,
      temperature: 0.7
    },
    fallback: {
      enabled: true,
      strategy: 'performance_based',
      maxRetries: 3,
      retryDelay: 1000
    },
    validation: {
      enabled: true,
      realTime: true,
      rateLimit: 100,
      timeout: 30000
    }
  }
};

// Hook para gerenciar configurações
const useSystemConfig = (initialConfig: SystemConfigData, onChange?: (config: SystemConfigData) => void) => {
  const [config, setConfig] = useState<SystemConfigData>(initialConfig);
  const [originalConfig, setOriginalConfig] = useState<SystemConfigData>(initialConfig);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    setConfig(initialConfig);
    setOriginalConfig(initialConfig);
  }, [initialConfig]);

  const updateConfig = (path: string, value: any) => {
    const newConfig = { ...config };
    const keys = path.split('.');
    let current: any = newConfig;
    
    for (let i = 0; i < keys.length - 1; i++) {
      current = current[keys[i]];
    }
    
    current[keys[keys.length - 1]] = value;
    setConfig(newConfig);
    
    const changes = JSON.stringify(newConfig) !== JSON.stringify(originalConfig);
    setHasChanges(changes);
    
    onChange?.(newConfig);
  };

  const resetConfig = () => {
    setConfig(originalConfig);
    setHasChanges(false);
  };

  const saveConfig = async (onSave?: (config: SystemConfigData) => Promise<void>) => {
    if (onSave) {
      await onSave(config);
      setOriginalConfig(config);
      setHasChanges(false);
    }
  };

  return {
    config,
    hasChanges,
    updateConfig,
    resetConfig,
    saveConfig
  };
};

// Componente de seção de configuração
const ConfigSection: React.FC<{
  title: string;
  description: string;
  children: React.ReactNode;
  isExpanded?: boolean;
  onToggle?: () => void;
}> = ({ title, description, children, isExpanded = true, onToggle }) => {
  return (
    <div style={{
      border: `1px solid ${colors.border.primary}`,
      borderRadius: '8px',
      marginBottom: '16px',
      overflow: 'hidden'
    }}>
      <div
        style={{
          padding: '16px',
          backgroundColor: colors.background.secondary,
          borderBottom: `1px solid ${colors.border.primary}`,
          cursor: onToggle ? 'pointer' : 'default',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
        onClick={onToggle}
      >
        <div>
          <h3 style={{
            margin: 0,
            fontSize: typography.sizes.lg,
            fontWeight: typography.weights.semibold,
            color: colors.text.primary
          }}>
            {title}
          </h3>
          <p style={{
            margin: '4px 0 0 0',
            fontSize: typography.sizes.sm,
            color: colors.text.secondary
          }}>
            {description}
          </p>
        </div>
        {onToggle && (
          <span style={{
            fontSize: typography.sizes.lg,
            color: colors.text.secondary,
            transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.2s ease-in-out'
          }}>
            ▼
          </span>
        )}
      </div>
      {isExpanded && (
        <div style={{ padding: '16px' }}>
          {children}
        </div>
      )}
    </div>
  );
};

// Componente de campo de configuração
const ConfigField: React.FC<{
  label: string;
  type: 'text' | 'number' | 'boolean' | 'select' | 'textarea';
  value: any;
  onChange: (value: any) => void;
  options?: { label: string; value: any }[];
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  helpText?: string;
}> = ({ label, type, value, onChange, options, placeholder, min, max, step, disabled, helpText }) => {
  const renderField = () => {
    switch (type) {
      case 'text':
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            disabled={disabled}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: `1px solid ${colors.border.primary}`,
              borderRadius: '4px',
              fontSize: typography.sizes.sm,
              fontFamily: typography.families.primary.sans
            }}
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
            style={{
              width: '100%',
              padding: '8px 12px',
              border: `1px solid ${colors.border.primary}`,
              borderRadius: '4px',
              fontSize: typography.sizes.sm,
              fontFamily: typography.families.primary.sans
            }}
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
              height: '16px'
            }}
          />
        );
      
      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: `1px solid ${colors.border.primary}`,
              borderRadius: '4px',
              fontSize: typography.sizes.sm,
              fontFamily: typography.families.primary.sans,
              backgroundColor: colors.background.primary
            }}
          >
            {options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );
      
      case 'textarea':
        return (
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            disabled={disabled}
            rows={3}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: `1px solid ${colors.border.primary}`,
              borderRadius: '4px',
              fontSize: typography.sizes.sm,
              fontFamily: typography.families.primary.sans,
              resize: 'vertical'
            }}
          />
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
    </div>
  );
};

// Componente principal
export const SystemConfig: React.FC<SystemConfigProps> = ({
  id = 'system-config',
  className = '',
  style = {},
  initialConfig = defaultConfig,
  onChange,
  onSave,
  onReset,
  showDevMode = false,
  readOnly = false
}) => {
  const [activeTab, setActiveTab] = useState('general');
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    general: true,
    security: true,
    performance: true,
    integration: true,
    social: true,
    analytics: true,
    payments: true,
    notifications: true,
    backup: true,
    logs: true,
    api: true,
    database: true,
    cache: true,
    ai: true
  });
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const {
    config,
    hasChanges,
    updateConfig,
    resetConfig,
    saveConfig
  } = useSystemConfig(initialConfig, onChange);

  // Tabs disponíveis
  const tabs = useMemo(() => [
    { id: 'general', label: 'Geral', icon: '⚙️' },
    { id: 'security', label: 'Segurança', icon: '🔒' },
    { id: 'performance', label: 'Performance', icon: '⚡' },
    { id: 'integration', label: 'Integração', icon: '🔗' },
    { id: 'social', label: 'Redes Sociais', icon: '📱' },
    { id: 'analytics', label: 'Analytics', icon: '📊' },
    { id: 'payments', label: 'Pagamentos', icon: '💳' },
    { id: 'notifications', label: 'Notificações', icon: '🔔' },
    { id: 'ai', label: 'IAs Generativas', icon: '🤖' },
    { id: 'backup', label: 'Backup', icon: '💾' },
    { id: 'logs', label: 'Logs', icon: '📝' },
    { id: 'api', label: 'API', icon: '🌐' },
    { id: 'database', label: 'Banco de Dados', icon: '🗄️' },
    { id: 'cache', label: 'Cache', icon: '⚡' }
  ], []);

  // Função para salvar configurações
  const handleSave = async () => {
    setIsSaving(true);
    setSaveStatus('idle');
    
    try {
      await saveConfig(onSave);
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  // Função para resetar configurações
  const handleReset = () => {
    resetConfig();
    onReset?.();
  };

  // Função para alternar seção
  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  // Estilos base
  const baseStyles: React.CSSProperties = {
    fontFamily: typography.families.primary.sans,
    color: colors.text.primary,
    backgroundColor: colors.background.primary,
    ...style
  };

  return (
    <div id={id} className={`system-config ${className}`} style={baseStyles}>
      {/* Header */}
      <div style={{
        padding: '24px',
        borderBottom: `1px solid ${colors.border.primary}`,
        backgroundColor: colors.background.secondary
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '16px'
        }}>
          <h1 style={{
            margin: 0,
            fontSize: typography.sizes['2xl'],
            fontWeight: typography.weights.bold,
            color: colors.text.primary
          }}>
            Configurações do Sistema
          </h1>
          
          <div style={{ display: 'flex', gap: '12px' }}>
            {hasChanges && (
              <span style={{
                padding: '4px 8px',
                backgroundColor: colors.state.warning[100],
                color: colors.state.warning[800],
                borderRadius: '4px',
                fontSize: typography.sizes.xs,
                fontWeight: typography.weights.medium
              }}>
                Alterações não salvas
              </span>
            )}
            
            {saveStatus === 'success' && (
              <span style={{
                padding: '4px 8px',
                backgroundColor: colors.state.success[100],
                color: colors.state.success[800],
                borderRadius: '4px',
                fontSize: typography.sizes.xs,
                fontWeight: typography.weights.medium
              }}>
                Salvo com sucesso!
              </span>
            )}
            
            {saveStatus === 'error' && (
              <span style={{
                padding: '4px 8px',
                backgroundColor: colors.state.error[100],
                color: colors.state.error[800],
                borderRadius: '4px',
                fontSize: typography.sizes.xs,
                fontWeight: typography.weights.medium
              }}>
                Erro ao salvar
              </span>
            )}
          </div>
        </div>
        
        <p style={{
          margin: 0,
          fontSize: typography.sizes.sm,
          color: colors.text.secondary
        }}>
          Gerencie todas as configurações do sistema em um local centralizado
        </p>
      </div>

      {/* Tabs */}
      <div style={{
        display: 'flex',
        borderBottom: `1px solid ${colors.border.primary}`,
        backgroundColor: colors.background.secondary,
        overflowX: 'auto'
      }}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '12px 16px',
              border: 'none',
              backgroundColor: activeTab === tab.id ? colors.primary[600] : 'transparent',
              color: activeTab === tab.id ? colors.text.inverse : colors.text.secondary,
              fontSize: typography.sizes.sm,
              fontWeight: typography.weights.medium,
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s ease-in-out'
            }}
          >
            <span style={{ marginRight: '8px' }}>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{ padding: '24px' }}>
        {/* Configurações Gerais */}
        {activeTab === 'general' && (
          <ConfigSection
            title="Configurações Gerais"
            description="Configurações básicas da aplicação"
            isExpanded={expandedSections.general}
            onToggle={() => toggleSection('general')}
          >
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <ConfigField
                label="Nome da Aplicação"
                type="text"
                value={config.general.appName}
                onChange={(value) => updateConfig('general.appName', value)}
                disabled={readOnly}
                helpText="Nome exibido na interface"
              />
              
              <ConfigField
                label="Versão"
                type="text"
                value={config.general.appVersion}
                onChange={(value) => updateConfig('general.appVersion', value)}
                disabled={readOnly}
                helpText="Versão atual da aplicação"
              />
              
              <ConfigField
                label="Ambiente"
                type="select"
                value={config.general.environment}
                onChange={(value) => updateConfig('general.environment', value)}
                options={[
                  { label: 'Desenvolvimento', value: 'development' },
                  { label: 'Staging', value: 'staging' },
                  { label: 'Produção', value: 'production' }
                ]}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Fuso Horário"
                type="text"
                value={config.general.timezone}
                onChange={(value) => updateConfig('general.timezone', value)}
                disabled={readOnly}
                helpText="Ex: UTC, America/Sao_Paulo"
              />
              
              <ConfigField
                label="Idioma"
                type="select"
                value={config.general.language}
                onChange={(value) => updateConfig('general.language', value)}
                options={[
                  { label: 'Português (Brasil)', value: 'pt-BR' },
                  { label: 'English', value: 'en-US' },
                  { label: 'Español', value: 'es-ES' }
                ]}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Formato de Data"
                type="text"
                value={config.general.dateFormat}
                onChange={(value) => updateConfig('general.dateFormat', value)}
                disabled={readOnly}
                helpText="Ex: DD/MM/YYYY, MM/DD/YYYY"
              />
              
              <ConfigField
                label="Formato de Hora"
                type="text"
                value={config.general.timeFormat}
                onChange={(value) => updateConfig('general.timeFormat', value)}
                disabled={readOnly}
                helpText="Ex: HH:mm:ss, h:mm A"
              />
              
              <ConfigField
                label="Moeda"
                type="text"
                value={config.general.currency}
                onChange={(value) => updateConfig('general.currency', value)}
                disabled={readOnly}
                helpText="Código da moeda (BRL, USD, EUR)"
              />
              
              <ConfigField
                label="Tamanho Máximo de Arquivo (bytes)"
                type="number"
                value={config.general.maxFileSize}
                onChange={(value) => updateConfig('general.maxFileSize', value)}
                min={1024}
                max={104857600}
                step={1024}
                disabled={readOnly}
                helpText="Tamanho máximo em bytes"
              />
              
              <ConfigField
                label="Timeout de Sessão (segundos)"
                type="number"
                value={config.general.sessionTimeout}
                onChange={(value) => updateConfig('general.sessionTimeout', value)}
                min={300}
                max={86400}
                step={300}
                disabled={readOnly}
                helpText="Tempo em segundos"
              />
            </div>
          </ConfigSection>
        )}

        {/* Configurações de Segurança */}
        {activeTab === 'security' && (
          <ConfigSection
            title="Configurações de Segurança"
            description="Configurações de segurança e autenticação"
            isExpanded={expandedSections.security}
            onToggle={() => toggleSection('security')}
          >
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <ConfigField
                label="Tamanho Mínimo de Senha"
                type="number"
                value={config.security.passwordMinLength}
                onChange={(value) => updateConfig('security.passwordMinLength', value)}
                min={6}
                max={32}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Requer Maiúsculas"
                type="boolean"
                value={config.security.passwordRequireUppercase}
                onChange={(value) => updateConfig('security.passwordRequireUppercase', value)}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Requer Minúsculas"
                type="boolean"
                value={config.security.passwordRequireLowercase}
                onChange={(value) => updateConfig('security.passwordRequireLowercase', value)}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Requer Números"
                type="boolean"
                value={config.security.passwordRequireNumbers}
                onChange={(value) => updateConfig('security.passwordRequireNumbers', value)}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Requer Símbolos"
                type="boolean"
                value={config.security.passwordRequireSymbols}
                onChange={(value) => updateConfig('security.passwordRequireSymbols', value)}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Máximo de Tentativas de Login"
                type="number"
                value={config.security.maxLoginAttempts}
                onChange={(value) => updateConfig('security.maxLoginAttempts', value)}
                min={1}
                max={20}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Duração do Bloqueio (segundos)"
                type="number"
                value={config.security.lockoutDuration}
                onChange={(value) => updateConfig('security.lockoutDuration', value)}
                min={60}
                max={3600}
                step={60}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Autenticação de Dois Fatores"
                type="boolean"
                value={config.security.twoFactorEnabled}
                onChange={(value) => updateConfig('security.twoFactorEnabled', value)}
                disabled={readOnly}
              />
              
              <ConfigField
                label="SSL Obrigatório"
                type="boolean"
                value={config.security.sslRequired}
                onChange={(value) => updateConfig('security.sslRequired', value)}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Rate Limit da API"
                type="number"
                value={config.security.apiRateLimit}
                onChange={(value) => updateConfig('security.apiRateLimit', value)}
                min={10}
                max={10000}
                step={10}
                disabled={readOnly}
                helpText="Requisições por minuto"
              />
            </div>
          </ConfigSection>
        )}

        {/* Configurações de IAs Generativas */}
        {activeTab === 'ai' && (
          <ConfigSection
            title="Configurações de IAs Generativas"
            description="Gerencie as configurações dos provedores de IA"
            isExpanded={expandedSections.ai}
            onToggle={() => toggleSection('ai')}
          >
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              {/* Provedor Padrão */}
              <ConfigField
                label="Provedor Padrão"
                type="select"
                value={config.ai.defaultProvider}
                onChange={(value) => updateConfig('ai.defaultProvider', value)}
                options={[
                  { label: 'DeepSeek', value: 'deepseek' },
                  { label: 'OpenAI', value: 'openai' },
                  { label: 'Claude', value: 'claude' },
                  { label: 'Gemini', value: 'gemini' }
                ]}
                disabled={readOnly}
                helpText="Provedor usado por padrão"
              />

              {/* DeepSeek */}
              <ConfigField
                label="DeepSeek - Habilitado"
                type="boolean"
                value={config.ai.deepseek.enabled}
                onChange={(value) => updateConfig('ai.deepseek.enabled', value)}
                disabled={readOnly}
              />
              
              <ConfigField
                label="DeepSeek - API Key"
                type="text"
                value={config.ai.deepseek.apiKey}
                onChange={(value) => updateConfig('ai.deepseek.apiKey', value)}
                disabled={readOnly}
                helpText="Chave de API do DeepSeek"
              />
              
              <ConfigField
                label="DeepSeek - Modelo"
                type="text"
                value={config.ai.deepseek.model}
                onChange={(value) => updateConfig('ai.deepseek.model', value)}
                disabled={readOnly}
                helpText="Ex: deepseek-chat"
              />
              
              <ConfigField
                label="DeepSeek - Max Tokens"
                type="number"
                value={config.ai.deepseek.maxTokens}
                onChange={(value) => updateConfig('ai.deepseek.maxTokens', value)}
                min={1}
                max={8192}
                disabled={readOnly}
              />
              
              <ConfigField
                label="DeepSeek - Temperature"
                type="number"
                value={config.ai.deepseek.temperature}
                onChange={(value) => updateConfig('ai.deepseek.temperature', value)}
                min={0}
                max={2}
                step={0.1}
                disabled={readOnly}
              />

              {/* OpenAI */}
              <ConfigField
                label="OpenAI - Habilitado"
                type="boolean"
                value={config.ai.openai.enabled}
                onChange={(value) => updateConfig('ai.openai.enabled', value)}
                disabled={readOnly}
              />
              
              <ConfigField
                label="OpenAI - API Key"
                type="text"
                value={config.ai.openai.apiKey}
                onChange={(value) => updateConfig('ai.openai.apiKey', value)}
                disabled={readOnly}
                helpText="Chave de API do OpenAI"
              />
              
              <ConfigField
                label="OpenAI - Modelo"
                type="text"
                value={config.ai.openai.model}
                onChange={(value) => updateConfig('ai.openai.model', value)}
                disabled={readOnly}
                helpText="Ex: gpt-4"
              />
              
              <ConfigField
                label="OpenAI - Max Tokens"
                type="number"
                value={config.ai.openai.maxTokens}
                onChange={(value) => updateConfig('ai.openai.maxTokens', value)}
                min={1}
                max={8192}
                disabled={readOnly}
              />
              
              <ConfigField
                label="OpenAI - Temperature"
                type="number"
                value={config.ai.openai.temperature}
                onChange={(value) => updateConfig('ai.openai.temperature', value)}
                min={0}
                max={2}
                step={0.1}
                disabled={readOnly}
              />

              {/* Claude */}
              <ConfigField
                label="Claude - Habilitado"
                type="boolean"
                value={config.ai.claude.enabled}
                onChange={(value) => updateConfig('ai.claude.enabled', value)}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Claude - API Key"
                type="text"
                value={config.ai.claude.apiKey}
                onChange={(value) => updateConfig('ai.claude.apiKey', value)}
                disabled={readOnly}
                helpText="Chave de API do Claude"
              />
              
              <ConfigField
                label="Claude - Modelo"
                type="text"
                value={config.ai.claude.model}
                onChange={(value) => updateConfig('ai.claude.model', value)}
                disabled={readOnly}
                helpText="Ex: claude-3-sonnet"
              />
              
              <ConfigField
                label="Claude - Max Tokens"
                type="number"
                value={config.ai.claude.maxTokens}
                onChange={(value) => updateConfig('ai.claude.maxTokens', value)}
                min={1}
                max={8192}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Claude - Temperature"
                type="number"
                value={config.ai.claude.temperature}
                onChange={(value) => updateConfig('ai.claude.temperature', value)}
                min={0}
                max={2}
                step={0.1}
                disabled={readOnly}
              />

              {/* Gemini */}
              <ConfigField
                label="Gemini - Habilitado"
                type="boolean"
                value={config.ai.gemini.enabled}
                onChange={(value) => updateConfig('ai.gemini.enabled', value)}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Gemini - API Key"
                type="text"
                value={config.ai.gemini.apiKey}
                onChange={(value) => updateConfig('ai.gemini.apiKey', value)}
                disabled={readOnly}
                helpText="Chave de API do Gemini"
              />
              
              <ConfigField
                label="Gemini - Modelo"
                type="text"
                value={config.ai.gemini.model}
                onChange={(value) => updateConfig('ai.gemini.model', value)}
                disabled={readOnly}
                helpText="Ex: gemini-pro"
              />
              
              <ConfigField
                label="Gemini - Max Tokens"
                type="number"
                value={config.ai.gemini.maxTokens}
                onChange={(value) => updateConfig('ai.gemini.maxTokens', value)}
                min={1}
                max={8192}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Gemini - Temperature"
                type="number"
                value={config.ai.gemini.temperature}
                onChange={(value) => updateConfig('ai.gemini.temperature', value)}
                min={0}
                max={2}
                step={0.1}
                disabled={readOnly}
              />

              {/* Fallback */}
              <ConfigField
                label="Fallback - Habilitado"
                type="boolean"
                value={config.ai.fallback.enabled}
                onChange={(value) => updateConfig('ai.fallback.enabled', value)}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Fallback - Estratégia"
                type="select"
                value={config.ai.fallback.strategy}
                onChange={(value) => updateConfig('ai.fallback.strategy', value)}
                options={[
                  { label: 'Round Robin', value: 'round_robin' },
                  { label: 'Baseado em Performance', value: 'performance_based' },
                  { label: 'Baseado em Custo', value: 'cost_based' }
                ]}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Fallback - Max Tentativas"
                type="number"
                value={config.ai.fallback.maxRetries}
                onChange={(value) => updateConfig('ai.fallback.maxRetries', value)}
                min={1}
                max={10}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Fallback - Delay (ms)"
                type="number"
                value={config.ai.fallback.retryDelay}
                onChange={(value) => updateConfig('ai.fallback.retryDelay', value)}
                min={100}
                max={10000}
                step={100}
                disabled={readOnly}
              />

              {/* Validação */}
              <ConfigField
                label="Validação - Habilitada"
                type="boolean"
                value={config.ai.validation.enabled}
                onChange={(value) => updateConfig('ai.validation.enabled', value)}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Validação - Tempo Real"
                type="boolean"
                value={config.ai.validation.realTime}
                onChange={(value) => updateConfig('ai.validation.realTime', value)}
                disabled={readOnly}
              />
              
              <ConfigField
                label="Validação - Rate Limit"
                type="number"
                value={config.ai.validation.rateLimit}
                onChange={(value) => updateConfig('ai.validation.rateLimit', value)}
                min={1}
                max={1000}
                disabled={readOnly}
                helpText="Requisições por minuto"
              />
              
              <ConfigField
                label="Validação - Timeout (ms)"
                type="number"
                value={config.ai.validation.timeout}
                onChange={(value) => updateConfig('ai.validation.timeout', value)}
                min={1000}
                max={120000}
                step={1000}
                disabled={readOnly}
              />
            </div>
          </ConfigSection>
        )}

        {/* Outras abas seriam implementadas de forma similar */}
        {activeTab !== 'general' && activeTab !== 'security' && activeTab !== 'ai' && (
          <div style={{
            padding: '40px',
            textAlign: 'center',
            color: colors.text.secondary
          }}>
            <p>Configurações para {activeTab} serão implementadas aqui</p>
          </div>
        )}
      </div>

      {/* Footer com ações */}
      <div style={{
        padding: '16px 24px',
        borderTop: `1px solid ${colors.border.primary}`,
        backgroundColor: colors.background.secondary,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={handleSave}
            disabled={!hasChanges || isSaving || readOnly}
            style={{
              padding: '8px 16px',
              backgroundColor: hasChanges ? colors.primary[600] : colors.secondary[300],
              color: colors.text.inverse,
              border: 'none',
              borderRadius: '4px',
              fontSize: typography.sizes.sm,
              fontWeight: typography.weights.medium,
              cursor: hasChanges && !readOnly ? 'pointer' : 'not-allowed',
              opacity: hasChanges && !readOnly ? 1 : 0.6
            }}
          >
            {isSaving ? 'Salvando...' : 'Salvar Alterações'}
          </button>
          
          <button
            onClick={handleReset}
            disabled={!hasChanges || readOnly}
            style={{
              padding: '8px 16px',
              backgroundColor: 'transparent',
              color: colors.text.secondary,
              border: `1px solid ${colors.border.primary}`,
              borderRadius: '4px',
              fontSize: typography.sizes.sm,
              fontWeight: typography.weights.medium,
              cursor: hasChanges && !readOnly ? 'pointer' : 'not-allowed'
            }}
          >
            Desfazer Alterações
          </button>
        </div>
        
        <div style={{ fontSize: typography.sizes.xs, color: colors.text.tertiary }}>
          Última atualização: {new Date().toLocaleString()}
        </div>
      </div>
    </div>
  );
};

// Exportações
export default SystemConfig;
export type { SystemConfigData, SystemConfigProps }; 
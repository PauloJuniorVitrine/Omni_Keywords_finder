/**
 * test_SystemConfig.tsx
 * 
 * Testes unitários para o componente SystemConfig
 * 
 * Tracing ID: UI-008-TEST
 * Data/Hora: 2024-12-20 08:45:00 UTC
 * Versão: 1.0
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SystemConfig, SystemConfigData } from '../../../../components/admin/SystemConfig';

// Mock dos temas
jest.mock('../../../../ui/theme/colors', () => ({
  colors: {
    primary: {
      600: '#2563eb',
      700: '#1d4ed8'
    },
    secondary: {
      300: '#cbd5e1'
    },
    background: {
      primary: '#ffffff',
      secondary: '#f8fafc'
    },
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
      tertiary: '#94a3b8',
      inverse: '#ffffff'
    },
    border: {
      primary: '#e2e8f0'
    },
    state: {
      success: {
        100: '#dcfce7',
        800: '#166534'
      },
      warning: {
        100: '#fef3c7',
        800: '#92400e'
      },
      error: {
        100: '#fee2e2',
        800: '#991b1b'
      }
    }
  }
}));

jest.mock('../../../../ui/theme/typography', () => ({
  typography: {
    families: {
      primary: {
        sans: 'Inter, system-ui, sans-serif'
      }
    },
    sizes: {
      xs: '12px',
      sm: '14px',
      lg: '18px',
      '2xl': '24px'
    },
    weights: {
      medium: 500,
      semibold: 600,
      bold: 700
    }
  }
}));

// Configuração de teste padrão
const defaultConfig: SystemConfigData = {
  general: {
    appName: 'Test App',
    appVersion: '1.0.0',
    environment: 'development',
    timezone: 'UTC',
    language: 'pt-BR',
    dateFormat: 'DD/MM/YYYY',
    timeFormat: 'HH:mm:ss',
    currency: 'BRL',
    maxFileSize: 10485760,
    sessionTimeout: 3600
  },
  security: {
    passwordMinLength: 8,
    passwordRequireUppercase: true,
    passwordRequireLowercase: true,
    passwordRequireNumbers: true,
    passwordRequireSymbols: false,
    maxLoginAttempts: 5,
    lockoutDuration: 900,
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
    logFile: '/var/log/test.log',
    maxLogSize: 10485760,
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
    name: 'test_db',
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
  }
};

describe('SystemConfig Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização Básica', () => {
    it('deve renderizar o componente com configurações padrão', () => {
      render(<SystemConfig />);
      
      expect(screen.getByText('Configurações do Sistema')).toBeInTheDocument();
      expect(screen.getByText('Gerencie todas as configurações do sistema em um local centralizado')).toBeInTheDocument();
    });

    it('deve renderizar com configurações customizadas', () => {
      const customConfig: SystemConfigData = {
        ...defaultConfig,
        general: {
          ...defaultConfig.general,
          appName: 'Custom App'
        }
      };

      render(<SystemConfig initialConfig={customConfig} />);
      
      expect(screen.getByDisplayValue('Custom App')).toBeInTheDocument();
    });

    it('deve renderizar todas as abas', () => {
      render(<SystemConfig />);
      
      expect(screen.getByText('Geral')).toBeInTheDocument();
      expect(screen.getByText('Segurança')).toBeInTheDocument();
      expect(screen.getByText('Performance')).toBeInTheDocument();
      expect(screen.getByText('Integração')).toBeInTheDocument();
      expect(screen.getByText('Notificações')).toBeInTheDocument();
      expect(screen.getByText('Backup')).toBeInTheDocument();
      expect(screen.getByText('Logs')).toBeInTheDocument();
      expect(screen.getByText('API')).toBeInTheDocument();
      expect(screen.getByText('Banco de Dados')).toBeInTheDocument();
      expect(screen.getByText('Cache')).toBeInTheDocument();
    });

    it('deve renderizar com ID customizado', () => {
      render(<SystemConfig id="custom-config" />);
      
      const container = document.getElementById('custom-config');
      expect(container).toBeInTheDocument();
    });

    it('deve renderizar com classes CSS customizadas', () => {
      render(<SystemConfig className="custom-class" />);
      
      const container = document.querySelector('.system-config.custom-class');
      expect(container).toBeInTheDocument();
    });

    it('deve renderizar com estilo inline customizado', () => {
      const customStyle = { backgroundColor: 'red' };
      render(<SystemConfig style={customStyle} />);
      
      const container = document.querySelector('.system-config');
      expect(container).toHaveStyle('background-color: red');
    });
  });

  describe('Funcionalidade de Abas', () => {
    it('deve mostrar a aba Geral por padrão', () => {
      render(<SystemConfig />);
      
      expect(screen.getByText('Configurações Gerais')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Test App')).toBeInTheDocument();
    });

    it('deve alternar para a aba Segurança', () => {
      render(<SystemConfig />);
      
      const securityTab = screen.getByText('Segurança');
      fireEvent.click(securityTab);
      
      expect(screen.getByText('Configurações de Segurança')).toBeInTheDocument();
      expect(screen.getByDisplayValue('8')).toBeInTheDocument(); // passwordMinLength
    });

    it('deve alternar entre múltiplas abas', () => {
      render(<SystemConfig />);
      
      // Clica na aba Segurança
      fireEvent.click(screen.getByText('Segurança'));
      expect(screen.getByText('Configurações de Segurança')).toBeInTheDocument();
      
      // Clica na aba Performance
      fireEvent.click(screen.getByText('Performance'));
      expect(screen.getByText('Configurações para performance serão implementadas aqui')).toBeInTheDocument();
      
      // Volta para a aba Geral
      fireEvent.click(screen.getByText('Geral'));
      expect(screen.getByText('Configurações Gerais')).toBeInTheDocument();
    });
  });

  describe('Funcionalidade de Seções', () => {
    it('deve expandir e colapsar seções', () => {
      render(<SystemConfig />);
      
      const sectionHeader = screen.getByText('Configurações Gerais');
      const sectionContent = screen.getByDisplayValue('Test App');
      
      // Seção deve estar expandida por padrão
      expect(sectionContent).toBeInTheDocument();
      
      // Clica para colapsar
      fireEvent.click(sectionHeader);
      expect(sectionContent).not.toBeInTheDocument();
      
      // Clica para expandir novamente
      fireEvent.click(sectionHeader);
      expect(sectionContent).toBeInTheDocument();
    });
  });

  describe('Campos de Configuração', () => {
    it('deve renderizar campo de texto', () => {
      render(<SystemConfig />);
      
      const appNameField = screen.getByDisplayValue('Test App');
      expect(appNameField).toBeInTheDocument();
      expect(appNameField).toHaveAttribute('type', 'text');
    });

    it('deve renderizar campo numérico', () => {
      render(<SystemConfig />);
      
      const maxFileSizeField = screen.getByDisplayValue('10485760');
      expect(maxFileSizeField).toBeInTheDocument();
      expect(maxFileSizeField).toHaveAttribute('type', 'number');
    });

    it('deve renderizar campo de seleção', () => {
      render(<SystemConfig />);
      
      const environmentField = screen.getByDisplayValue('development');
      expect(environmentField).toBeInTheDocument();
      expect(environmentField.tagName).toBe('SELECT');
    });

    it('deve renderizar campo booleano', () => {
      render(<SystemConfig />);
      
      // Muda para a aba Segurança para encontrar campos booleanos
      fireEvent.click(screen.getByText('Segurança'));
      
      const requireUppercaseField = screen.getByRole('checkbox');
      expect(requireUppercaseField).toBeInTheDocument();
      expect(requireUppercaseField).toHaveAttribute('type', 'checkbox');
    });

    it('deve atualizar valor do campo de texto', () => {
      const onChange = jest.fn();
      render(<SystemConfig onChange={onChange} />);
      
      const appNameField = screen.getByDisplayValue('Test App');
      fireEvent.change(appNameField, { target: { value: 'New App Name' } });
      
      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({
          general: expect.objectContaining({
            appName: 'New App Name'
          })
        })
      );
    });

    it('deve atualizar valor do campo numérico', () => {
      const onChange = jest.fn();
      render(<SystemConfig onChange={onChange} />);
      
      const maxFileSizeField = screen.getByDisplayValue('10485760');
      fireEvent.change(maxFileSizeField, { target: { value: '20971520' } });
      
      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({
          general: expect.objectContaining({
            maxFileSize: 20971520
          })
        })
      );
    });

    it('deve atualizar valor do campo de seleção', () => {
      const onChange = jest.fn();
      render(<SystemConfig onChange={onChange} />);
      
      const environmentField = screen.getByDisplayValue('development');
      fireEvent.change(environmentField, { target: { value: 'production' } });
      
      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({
          general: expect.objectContaining({
            environment: 'production'
          })
        })
      );
    });

    it('deve atualizar valor do campo booleano', () => {
      const onChange = jest.fn();
      render(<SystemConfig onChange={onChange} />);
      
      // Muda para a aba Segurança
      fireEvent.click(screen.getByText('Segurança'));
      
      const requireUppercaseField = screen.getByRole('checkbox');
      fireEvent.click(requireUppercaseField);
      
      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({
          security: expect.objectContaining({
            passwordRequireUppercase: false
          })
        })
      );
    });
  });

  describe('Detecção de Mudanças', () => {
    it('deve detectar mudanças nas configurações', () => {
      render(<SystemConfig />);
      
      // Inicialmente não deve ter mudanças
      expect(screen.queryByText('Alterações não salvas')).not.toBeInTheDocument();
      
      // Faz uma mudança
      const appNameField = screen.getByDisplayValue('Test App');
      fireEvent.change(appNameField, { target: { value: 'Modified App' } });
      
      // Deve mostrar indicador de mudanças
      expect(screen.getByText('Alterações não salvas')).toBeInTheDocument();
    });

    it('deve remover indicador de mudanças após reset', () => {
      render(<SystemConfig />);
      
      // Faz uma mudança
      const appNameField = screen.getByDisplayValue('Test App');
      fireEvent.change(appNameField, { target: { value: 'Modified App' } });
      
      expect(screen.getByText('Alterações não salvas')).toBeInTheDocument();
      
      // Clica em desfazer
      const resetButton = screen.getByText('Desfazer Alterações');
      fireEvent.click(resetButton);
      
      expect(screen.queryByText('Alterações não salvas')).not.toBeInTheDocument();
    });
  });

  describe('Funcionalidade de Salvar', () => {
    it('deve chamar onSave quando salvar', async () => {
      const onSave = jest.fn().mockResolvedValue(undefined);
      render(<SystemConfig onSave={onSave} />);
      
      // Faz uma mudança
      const appNameField = screen.getByDisplayValue('Test App');
      fireEvent.change(appNameField, { target: { value: 'Saved App' } });
      
      // Clica em salvar
      const saveButton = screen.getByText('Salvar Alterações');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(onSave).toHaveBeenCalledWith(
          expect.objectContaining({
            general: expect.objectContaining({
              appName: 'Saved App'
            })
          })
        );
      });
    });

    it('deve mostrar status de sucesso após salvar', async () => {
      const onSave = jest.fn().mockResolvedValue(undefined);
      render(<SystemConfig onSave={onSave} />);
      
      // Faz uma mudança
      const appNameField = screen.getByDisplayValue('Test App');
      fireEvent.change(appNameField, { target: { value: 'Saved App' } });
      
      // Clica em salvar
      const saveButton = screen.getByText('Salvar Alterações');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(screen.getByText('Salvo com sucesso!')).toBeInTheDocument();
      });
    });

    it('deve mostrar status de erro quando falhar', async () => {
      const onSave = jest.fn().mockRejectedValue(new Error('Save failed'));
      render(<SystemConfig onSave={onSave} />);
      
      // Faz uma mudança
      const appNameField = screen.getByDisplayValue('Test App');
      fireEvent.change(appNameField, { target: { value: 'Failed App' } });
      
      // Clica em salvar
      const saveButton = screen.getByText('Salvar Alterações');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(screen.getByText('Erro ao salvar')).toBeInTheDocument();
      });
    });

    it('deve desabilitar botão de salvar quando não há mudanças', () => {
      render(<SystemConfig />);
      
      const saveButton = screen.getByText('Salvar Alterações');
      expect(saveButton).toBeDisabled();
    });

    it('deve desabilitar botão de salvar em modo somente leitura', () => {
      render(<SystemConfig readOnly={true} />);
      
      // Faz uma mudança
      const appNameField = screen.getByDisplayValue('Test App');
      fireEvent.change(appNameField, { target: { value: 'Read Only App' } });
      
      const saveButton = screen.getByText('Salvar Alterações');
      expect(saveButton).toBeDisabled();
    });
  });

  describe('Funcionalidade de Reset', () => {
    it('deve chamar onReset quando desfazer alterações', () => {
      const onReset = jest.fn();
      render(<SystemConfig onReset={onReset} />);
      
      // Faz uma mudança
      const appNameField = screen.getByDisplayValue('Test App');
      fireEvent.change(appNameField, { target: { value: 'Modified App' } });
      
      // Clica em desfazer
      const resetButton = screen.getByText('Desfazer Alterações');
      fireEvent.click(resetButton);
      
      expect(onReset).toHaveBeenCalled();
    });

    it('deve desabilitar botão de reset quando não há mudanças', () => {
      render(<SystemConfig />);
      
      const resetButton = screen.getByText('Desfazer Alterações');
      expect(resetButton).toBeDisabled();
    });

    it('deve desabilitar botão de reset em modo somente leitura', () => {
      render(<SystemConfig readOnly={true} />);
      
      // Faz uma mudança
      const appNameField = screen.getByDisplayValue('Test App');
      fireEvent.change(appNameField, { target: { value: 'Read Only App' } });
      
      const resetButton = screen.getByText('Desfazer Alterações');
      expect(resetButton).toBeDisabled();
    });
  });

  describe('Modo Somente Leitura', () => {
    it('deve desabilitar todos os campos em modo somente leitura', () => {
      render(<SystemConfig readOnly={true} />);
      
      const appNameField = screen.getByDisplayValue('Test App');
      expect(appNameField).toBeDisabled();
      
      const maxFileSizeField = screen.getByDisplayValue('10485760');
      expect(maxFileSizeField).toBeDisabled();
      
      const environmentField = screen.getByDisplayValue('development');
      expect(environmentField).toBeDisabled();
    });

    it('deve desabilitar campos booleanos em modo somente leitura', () => {
      render(<SystemConfig readOnly={true} />);
      
      // Muda para a aba Segurança
      fireEvent.click(screen.getByText('Segurança'));
      
      const requireUppercaseField = screen.getByRole('checkbox');
      expect(requireUppercaseField).toBeDisabled();
    });
  });

  describe('Callback onChange', () => {
    it('deve chamar onChange quando configurações são alteradas', () => {
      const onChange = jest.fn();
      render(<SystemConfig onChange={onChange} />);
      
      const appNameField = screen.getByDisplayValue('Test App');
      fireEvent.change(appNameField, { target: { value: 'Changed App' } });
      
      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({
          general: expect.objectContaining({
            appName: 'Changed App'
          })
        })
      );
    });

    it('deve chamar onChange múltiplas vezes para diferentes campos', () => {
      const onChange = jest.fn();
      render(<SystemConfig onChange={onChange} />);
      
      // Altera primeiro campo
      const appNameField = screen.getByDisplayValue('Test App');
      fireEvent.change(appNameField, { target: { value: 'Changed App' } });
      
      // Altera segundo campo
      const maxFileSizeField = screen.getByDisplayValue('10485760');
      fireEvent.change(maxFileSizeField, { target: { value: '20971520' } });
      
      expect(onChange).toHaveBeenCalledTimes(2);
    });
  });

  describe('Validação de Campos', () => {
    it('deve aplicar limites mínimos em campos numéricos', () => {
      render(<SystemConfig />);
      
      const maxFileSizeField = screen.getByDisplayValue('10485760');
      expect(maxFileSizeField).toHaveAttribute('min', '1024');
      expect(maxFileSizeField).toHaveAttribute('max', '104857600');
    });

    it('deve aplicar limites em campos de tentativas de login', () => {
      render(<SystemConfig />);
      
      // Muda para a aba Segurança
      fireEvent.click(screen.getByText('Segurança'));
      
      const maxLoginAttemptsField = screen.getByDisplayValue('5');
      expect(maxLoginAttemptsField).toHaveAttribute('min', '1');
      expect(maxLoginAttemptsField).toHaveAttribute('max', '20');
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter labels apropriados para campos', () => {
      render(<SystemConfig />);
      
      expect(screen.getByLabelText('Nome da Aplicação')).toBeInTheDocument();
      expect(screen.getByLabelText('Versão')).toBeInTheDocument();
      expect(screen.getByLabelText('Ambiente')).toBeInTheDocument();
    });

    it('deve ter texto de ajuda para campos', () => {
      render(<SystemConfig />);
      
      expect(screen.getByText('Nome exibido na interface')).toBeInTheDocument();
      expect(screen.getByText('Versão atual da aplicação')).toBeInTheDocument();
      expect(screen.getByText('Ex: UTC, America/Sao_Paulo')).toBeInTheDocument();
    });

    it('deve ter botões com texto descritivo', () => {
      render(<SystemConfig />);
      
      expect(screen.getByText('Salvar Alterações')).toBeInTheDocument();
      expect(screen.getByText('Desfazer Alterações')).toBeInTheDocument();
    });
  });

  describe('Responsividade', () => {
    it('deve ter layout responsivo com grid', () => {
      render(<SystemConfig />);
      
      const gridContainer = screen.getByText('Configurações Gerais').closest('div')?.parentElement;
      expect(gridContainer).toHaveStyle('display: grid');
    });

    it('deve ter tabs com overflow horizontal', () => {
      render(<SystemConfig />);
      
      const tabsContainer = screen.getByText('Geral').closest('div');
      expect(tabsContainer).toHaveStyle('overflow-x: auto');
    });
  });

  describe('Performance', () => {
    it('deve renderizar sem erros de performance', () => {
      const startTime = performance.now();
      
      render(<SystemConfig />);
      
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      // Deve renderizar em menos de 100ms
      expect(renderTime).toBeLessThan(100);
    });

    it('deve atualizar eficientemente quando mudanças são feitas', () => {
      const onChange = jest.fn();
      render(<SystemConfig onChange={onChange} />);
      
      const appNameField = screen.getByDisplayValue('Test App');
      
      // Faz múltiplas mudanças rapidamente
      for (let i = 0; i < 10; i++) {
        fireEvent.change(appNameField, { target: { value: `App ${i}` } });
      }
      
      // onChange deve ser chamado para cada mudança
      expect(onChange).toHaveBeenCalledTimes(10);
    });
  });

  describe('Integração com Temas', () => {
    it('deve usar cores do tema', () => {
      render(<SystemConfig />);
      
      const header = screen.getByText('Configurações do Sistema').closest('div');
      expect(header).toHaveStyle('background-color: rgb(248, 250, 252)'); // colors.background.secondary
    });

    it('deve usar tipografia do tema', () => {
      render(<SystemConfig />);
      
      const title = screen.getByText('Configurações do Sistema');
      expect(title).toHaveStyle('font-size: 24px'); // typography.sizes['2xl']
      expect(title).toHaveStyle('font-weight: 700'); // typography.weights.bold
    });
  });

  describe('Casos de Borda', () => {
    it('deve lidar com configurações vazias', () => {
      const emptyConfig = {} as SystemConfigData;
      render(<SystemConfig initialConfig={emptyConfig} />);
      
      // Deve renderizar sem erros
      expect(screen.getByText('Configurações do Sistema')).toBeInTheDocument();
    });

    it('deve lidar com configurações parciais', () => {
      const partialConfig = {
        general: {
          appName: 'Partial App',
          appVersion: '1.0.0'
        }
      } as SystemConfigData;
      
      render(<SystemConfig initialConfig={partialConfig} />);
      
      expect(screen.getByDisplayValue('Partial App')).toBeInTheDocument();
    });

    it('deve lidar com valores nulos ou undefined', () => {
      const configWithNulls = {
        ...defaultConfig,
        general: {
          ...defaultConfig.general,
          appName: null as any
        }
      };
      
      render(<SystemConfig initialConfig={configWithNulls} />);
      
      // Deve renderizar sem erros
      expect(screen.getByText('Configurações do Sistema')).toBeInTheDocument();
    });
  });

  describe('Testes de Integração', () => {
    it('deve integrar com sistema de mudanças', () => {
      const onChange = jest.fn();
      const onSave = jest.fn().mockResolvedValue(undefined);
      const onReset = jest.fn();
      
      render(
        <SystemConfig
          onChange={onChange}
          onSave={onSave}
          onReset={onReset}
        />
      );
      
      // Faz mudança
      const appNameField = screen.getByDisplayValue('Test App');
      fireEvent.change(appNameField, { target: { value: 'Integrated App' } });
      
      expect(onChange).toHaveBeenCalled();
      expect(screen.getByText('Alterações não salvas')).toBeInTheDocument();
      
      // Salva
      const saveButton = screen.getByText('Salvar Alterações');
      fireEvent.click(saveButton);
      
      expect(onSave).toHaveBeenCalled();
      
      // Reseta
      const resetButton = screen.getByText('Desfazer Alterações');
      fireEvent.click(resetButton);
      
      expect(onReset).toHaveBeenCalled();
    });

    it('deve manter estado consistente entre operações', () => {
      const onChange = jest.fn();
      render(<SystemConfig onChange={onChange} />);
      
      // Faz mudança
      const appNameField = screen.getByDisplayValue('Test App');
      fireEvent.change(appNameField, { target: { value: 'State Test' } });
      
      // Muda de aba
      fireEvent.click(screen.getByText('Segurança'));
      
      // Volta para a aba original
      fireEvent.click(screen.getByText('Geral'));
      
      // Valor deve ser mantido
      expect(screen.getByDisplayValue('State Test')).toBeInTheDocument();
    });
  });
}); 
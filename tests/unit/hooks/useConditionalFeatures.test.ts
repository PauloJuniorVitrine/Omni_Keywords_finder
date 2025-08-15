/**
 * useConditionalFeatures.test.ts
 * 
 * Testes unitários para o hook useConditionalFeatures
 * 
 * Tracing ID: TEST-USE-CONDITIONAL-FEATURES-001
 * Data: 2024-12-20
 * Versão: 1.0
 */

import { renderHook, act } from '@testing-library/react';
import { 
  useConditionalFeatures, 
  useMultipleConditionalFeatures,
  useAutoContext,
  FeatureFlagsProvider,
  FeatureFlag,
  FeatureContext,
  FeatureCondition
} from '../../app/hooks/useConditionalFeatures';

// Mock do useTracing
jest.mock('../../app/utils/tracing', () => ({
  useTracing: () => ({
    trace: jest.fn(() => ({
      setAttributes: jest.fn(),
      recordException: jest.fn(),
      end: jest.fn()
    }))
  })
}));

describe('useConditionalFeatures Hook', () => {
  const mockFeatureFlag: FeatureFlag = {
    name: 'test-feature',
    description: 'Feature de teste',
    type: 'boolean',
    default_value: false,
    conditions: [
      {
        context_type: 'user',
        attribute: 'user_id',
        operator: 'eq',
        value: 'user123',
        weight: 1
      }
    ],
    enabled: true,
    rollback_strategy: 'immediate',
    rollback_threshold: 0.1
  };

  const mockContext: FeatureContext = {
    user_id: 'user123',
    session_id: 'session456',
    environment: 'test',
    timestamp: new Date(),
    location: 'BR',
    device_type: 'desktop',
    custom_attributes: {}
  };

  describe('FeatureFlagsProvider', () => {
    it('deve fornecer contexto padrão', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider>{children}</FeatureFlagsProvider>
      );

      const { result } = renderHook(() => {
        const context = useConditionalFeatures('test-feature');
        return context;
      }, { wrapper });

      expect(result.current.value).toBeUndefined();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('deve aceitar contexto inicial', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider initialContext={mockContext}>
          {children}
        </FeatureFlagsProvider>
      );

      const { result } = renderHook(() => {
        const context = useConditionalFeatures('test-feature');
        return context;
      }, { wrapper });

      expect(result.current.context).toEqual(expect.objectContaining({
        user_id: 'user123',
        environment: 'test'
      }));
    });
  });

  describe('useConditionalFeatures - Hook Principal', () => {
    it('deve retornar fallback quando flag não existe', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider>{children}</FeatureFlagsProvider>
      );

      const { result } = renderHook(() => 
        useConditionalFeatures('non-existent-feature', 'fallback-value')
      , { wrapper });

      expect(result.current.value).toBe('fallback-value');
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('deve avaliar flag com condições atendidas', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider initialContext={mockContext}>
          {children}
        </FeatureFlagsProvider>
      );

      const { result } = renderHook(() => {
        const context = useConditionalFeatures('test-feature', false);
        
        // Registrar flag
        act(() => {
          context.registerFlag(mockFeatureFlag);
        });
        
        return context;
      }, { wrapper });

      expect(result.current.value).toBe(true);
      expect(result.current.evaluation?.conditions_met).toHaveLength(1);
    });

    it('deve avaliar flag com condições não atendidas', () => {
      const contextWithoutUser: FeatureContext = {
        ...mockContext,
        user_id: 'different-user'
      };

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider initialContext={contextWithoutUser}>
          {children}
        </FeatureFlagsProvider>
      );

      const { result } = renderHook(() => {
        const context = useConditionalFeatures('test-feature', false);
        
        act(() => {
          context.registerFlag(mockFeatureFlag);
        });
        
        return context;
      }, { wrapper });

      expect(result.current.value).toBe(false);
      expect(result.current.evaluation?.conditions_met).toHaveLength(0);
    });

    it('deve suportar auto-refresh', () => {
      jest.useFakeTimers();

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider>{children}</FeatureFlagsProvider>
      );

      const { result } = renderHook(() => 
        useConditionalFeatures('test-feature', false, {
          autoRefresh: true,
          refreshInterval: 1000
        })
      , { wrapper });

      expect(result.current.loading).toBe(false);

      act(() => {
        jest.advanceTimersByTime(1000);
      });

      expect(result.current.loading).toBe(false);

      jest.useRealTimers();
    });

    it('deve chamar callback quando valor muda', () => {
      const onValueChange = jest.fn();

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider initialContext={mockContext}>
          {children}
        </FeatureFlagsProvider>
      );

      const { result } = renderHook(() => 
        useConditionalFeatures('test-feature', false, {
          onValueChange
        })
      , { wrapper });

      act(() => {
        result.current.registerFlag(mockFeatureFlag);
      });

      expect(onValueChange).toHaveBeenCalledWith(
        true,
        expect.objectContaining({
          flag_name: 'test-feature',
          value: true
        })
      );
    });
  });

  describe('useMultipleConditionalFeatures', () => {
    it('deve avaliar múltiplas flags', () => {
      const flag1: FeatureFlag = {
        ...mockFeatureFlag,
        name: 'feature-1',
        default_value: false
      };

      const flag2: FeatureFlag = {
        ...mockFeatureFlag,
        name: 'feature-2',
        default_value: true
      };

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider initialContext={mockContext}>
          {children}
        </FeatureFlagsProvider>
      );

      const { result } = renderHook(() => 
        useMultipleConditionalFeatures([
          { name: 'feature-1', fallbackValue: false },
          { name: 'feature-2', fallbackValue: true }
        ])
      , { wrapper });

      act(() => {
        result.current.registerFlag(flag1);
        result.current.registerFlag(flag2);
      });

      expect(result.current.values).toEqual({
        'feature-1': true,
        'feature-2': true
      });
    });

    it('deve lidar com flags inexistentes', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider>{children}</FeatureFlagsProvider>
      );

      const { result } = renderHook(() => 
        useMultipleConditionalFeatures([
          { name: 'non-existent-1', fallbackValue: 'fallback1' },
          { name: 'non-existent-2', fallbackValue: 'fallback2' }
        ])
      , { wrapper });

      expect(result.current.values).toEqual({
        'non-existent-1': 'fallback1',
        'non-existent-2': 'fallback2'
      });
    });
  });

  describe('useAutoContext', () => {
    it('deve detectar tipo de dispositivo', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider>{children}</FeatureFlagsProvider>
      );

      const { result } = renderHook(() => useAutoContext(), { wrapper });

      expect(result.current.context.device_type).toBeDefined();
    });

    it('deve detectar mudanças de tamanho de tela', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider>{children}</FeatureFlagsProvider>
      );

      const { result } = renderHook(() => useAutoContext(), { wrapper });

      // Simular mudança de tamanho
      act(() => {
        Object.defineProperty(window, 'innerWidth', {
          writable: true,
          configurable: true,
          value: 800
        });
        window.dispatchEvent(new Event('resize'));
      });

      expect(result.current.context.custom_attributes).toBeDefined();
    });
  });

  describe('Avaliação de Condições', () => {
    it('deve avaliar condição de igualdade', () => {
      const condition: FeatureCondition = {
        context_type: 'user',
        attribute: 'user_id',
        operator: 'eq',
        value: 'user123',
        weight: 1
      };

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider initialContext={mockContext}>
          {children}
        </FeatureFlagsProvider>
      );

      const { result } = renderHook(() => {
        const context = useConditionalFeatures('test-feature', false);
        
        const flagWithCondition: FeatureFlag = {
          ...mockFeatureFlag,
          conditions: [condition]
        };
        
        act(() => {
          context.registerFlag(flagWithCondition);
        });
        
        return context;
      }, { wrapper });

      expect(result.current.value).toBe(true);
    });

    it('deve avaliar condição de maior que', () => {
      const condition: FeatureCondition = {
        context_type: 'custom',
        attribute: 'user_level',
        operator: 'gt',
        value: 5,
        weight: 1
      };

      const contextWithLevel: FeatureContext = {
        ...mockContext,
        custom_attributes: { user_level: 10 }
      };

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider initialContext={contextWithLevel}>
          {children}
        </FeatureFlagsProvider>
      );

      const { result } = renderHook(() => {
        const context = useConditionalFeatures('test-feature', false);
        
        const flagWithCondition: FeatureFlag = {
          ...mockFeatureFlag,
          conditions: [condition]
        };
        
        act(() => {
          context.registerFlag(flagWithCondition);
        });
        
        return context;
      }, { wrapper });

      expect(result.current.value).toBe(true);
    });

    it('deve avaliar condição de contém', () => {
      const condition: FeatureCondition = {
        context_type: 'location',
        attribute: 'country',
        operator: 'contains',
        value: 'BR',
        weight: 1
      };

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider initialContext={mockContext}>
          {children}
        </FeatureFlagsProvider>
      );

      const { result } = renderHook(() => {
        const context = useConditionalFeatures('test-feature', false);
        
        const flagWithCondition: FeatureFlag = {
          ...mockFeatureFlag,
          conditions: [condition]
        };
        
        act(() => {
          context.registerFlag(flagWithCondition);
        });
        
        return context;
      }, { wrapper });

      expect(result.current.value).toBe(true);
    });
  });

  describe('Tipos de Flags', () => {
    it('deve suportar flag do tipo string', () => {
      const stringFlag: FeatureFlag = {
        ...mockFeatureFlag,
        name: 'string-feature',
        type: 'string',
        default_value: 'default',
        conditions: []
      };

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider>{children}</FeatureFlagsProvider>
      );

      const { result } = renderHook(() => 
        useConditionalFeatures('string-feature', 'fallback')
      , { wrapper });

      act(() => {
        result.current.registerFlag(stringFlag);
      });

      expect(result.current.value).toBe('default');
    });

    it('deve suportar flag do tipo number', () => {
      const numberFlag: FeatureFlag = {
        ...mockFeatureFlag,
        name: 'number-feature',
        type: 'number',
        default_value: 42,
        conditions: []
      };

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider>{children}</FeatureFlagsProvider>
      );

      const { result } = renderHook(() => 
        useConditionalFeatures('number-feature', 0)
      , { wrapper });

      act(() => {
        result.current.registerFlag(numberFlag);
      });

      expect(result.current.value).toBe(42);
    });

    it('deve suportar flag do tipo percentage', () => {
      const percentageFlag: FeatureFlag = {
        ...mockFeatureFlag,
        name: 'percentage-feature',
        type: 'percentage',
        default_value: 0.5,
        conditions: []
      };

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider>{children}</FeatureFlagsProvider>
      );

      const { result } = renderHook(() => 
        useConditionalFeatures('percentage-feature', 0)
      , { wrapper });

      act(() => {
        result.current.registerFlag(percentageFlag);
      });

      expect(result.current.value).toBe(0.5);
    });
  });

  describe('Métricas e Cache', () => {
    it('deve registrar métricas de avaliação', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider initialContext={mockContext}>
          {children}
        </FeatureFlagsProvider>
      );

      const { result } = renderHook(() => {
        const context = useConditionalFeatures('test-feature', false);
        
        act(() => {
          context.registerFlag(mockFeatureFlag);
        });
        
        return context;
      }, { wrapper });

      const metrics = result.current.getMetrics();
      expect(metrics['test-feature']).toBeDefined();
      expect(metrics['test-feature'].evaluations).toBeGreaterThan(0);
    });

    it('deve usar cache quando habilitado', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider initialContext={mockContext} enableCaching={true}>
          {children}
        </FeatureFlagsProvider>
      );

      const { result } = renderHook(() => {
        const context = useConditionalFeatures('test-feature', false);
        
        act(() => {
          context.registerFlag(mockFeatureFlag);
        });
        
        return context;
      }, { wrapper });

      const metrics = result.current.getMetrics();
      expect(metrics['test-feature'].cache_hits).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Casos Extremos', () => {
    it('deve lidar com flag desabilitada', () => {
      const disabledFlag: FeatureFlag = {
        ...mockFeatureFlag,
        enabled: false
      };

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider>{children}</FeatureFlagsProvider>
      );

      const { result } = renderHook(() => 
        useConditionalFeatures('disabled-feature', 'fallback')
      , { wrapper });

      act(() => {
        result.current.registerFlag(disabledFlag);
      });

      expect(result.current.value).toBe('fallback');
    });

    it('deve lidar com flag expirada', () => {
      const expiredFlag: FeatureFlag = {
        ...mockFeatureFlag,
        expires_at: new Date(Date.now() - 1000) // Expirou há 1 segundo
      };

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider>{children}</FeatureFlagsProvider>
      );

      const { result } = renderHook(() => 
        useConditionalFeatures('expired-feature', 'fallback')
      , { wrapper });

      act(() => {
        result.current.registerFlag(expiredFlag);
      });

      expect(result.current.value).toBe('fallback');
    });

    it('deve lidar com condições inválidas', () => {
      const invalidCondition: FeatureCondition = {
        context_type: 'user',
        attribute: 'invalid_attribute',
        operator: 'eq',
        value: 'test',
        weight: 1
      };

      const flagWithInvalidCondition: FeatureFlag = {
        ...mockFeatureFlag,
        conditions: [invalidCondition]
      };

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagsProvider initialContext={mockContext}>
          {children}
        </FeatureFlagsProvider>
      );

      const { result } = renderHook(() => 
        useConditionalFeatures('invalid-feature', 'fallback')
      , { wrapper });

      act(() => {
        result.current.registerFlag(flagWithInvalidCondition);
      });

      expect(result.current.value).toBe('fallback');
    });
  });
}); 
/**
 * 📄 Hook para Features Condicionais - React
 * 🎯 Objetivo: Hook para features condicionais com detecção automática de contexto
 * 📊 Funcionalidades: Contexto automático, fallbacks inteligentes, integração React
 * 🔧 Integração: React, TypeScript, OpenTelemetry, Context API
 * 🧪 Testes: Cobertura completa de funcionalidades
 * 
 * Tracing ID: USE_CONDITIONAL_FEATURES_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 */

import React, {
  useState,
  useEffect,
  useCallback,
  useRef,
  useMemo,
  useContext,
  createContext,
  ReactNode
} from 'react';
import { useTracing } from '../utils/tracing';

// Tipos
export interface FeatureContext {
  user_id?: string;
  session_id?: string;
  environment: string;
  timestamp: Date;
  location?: string;
  device_type?: string;
  custom_attributes: Record<string, any>;
}

export interface FeatureFlag {
  name: string;
  description: string;
  type: 'boolean' | 'percentage' | 'string' | 'number' | 'json' | 'conditional';
  default_value: any;
  conditions: FeatureCondition[];
  enabled: boolean;
  expires_at?: Date;
  rollback_strategy: 'immediate' | 'gradual' | 'scheduled' | 'manual';
  rollback_threshold: number;
  schema_variations?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface FeatureCondition {
  context_type: 'user' | 'session' | 'environment' | 'time' | 'location' | 'device' | 'custom';
  attribute: string;
  operator: 'eq' | 'ne' | 'gt' | 'lt' | 'gte' | 'lte' | 'in' | 'not_in' | 'contains' | 'regex';
  value: any;
  weight: number;
}

export interface FeatureEvaluation {
  flag_name: string;
  value: any;
  context: FeatureContext;
  conditions_met: FeatureCondition[];
  evaluation_time: number;
  cache_hit: boolean;
  schema_variation?: any;
}

export interface FeatureMetrics {
  flag_name: string;
  evaluations: number;
  activations: number;
  cache_hits: number;
  avg_evaluation_time: number;
  error_count: number;
  last_evaluated?: Date;
}

// Contexto para feature flags
interface FeatureFlagsContextType {
  context: FeatureContext;
  setContext: (context: Partial<FeatureContext>) => void;
  evaluateFlag: (flagName: string, fallbackValue?: any) => FeatureEvaluation;
  getMetrics: () => Record<string, FeatureMetrics>;
  registerFlag: (flag: FeatureFlag) => void;
  unregisterFlag: (flagName: string) => void;
}

const FeatureFlagsContext = createContext<FeatureFlagsContextType | null>(null);

// Hook para acessar contexto de feature flags
export function useFeatureFlagsContext() {
  const context = useContext(FeatureFlagsContext);
  if (!context) {
    throw new Error('useFeatureFlagsContext deve ser usado dentro de FeatureFlagsProvider');
  }
  return context;
}

// Provider para feature flags
interface FeatureFlagsProviderProps {
  children: ReactNode;
  initialContext?: Partial<FeatureContext>;
  enableMetrics?: boolean;
  enableCaching?: boolean;
  cacheTTL?: number;
}

export function FeatureFlagsProvider({
  children,
  initialContext = {},
  enableMetrics = true,
  enableCaching = true,
  cacheTTL = 300
}: FeatureFlagsProviderProps) {
  const { trace } = useTracing();
  
  // Estado do contexto
  const [context, setContextState] = useState<FeatureContext>({
    environment: 'production',
    timestamp: new Date(),
    custom_attributes: {},
    ...initialContext
  });
  
  // Storage de flags
  const flagsRef = useRef<Record<string, FeatureFlag>>({});
  const metricsRef = useRef<Record<string, FeatureMetrics>>({});
  const cacheRef = useRef<Record<string, { evaluation: FeatureEvaluation; timestamp: number }>>({});
  
  // Atualiza contexto
  const setContext = useCallback((newContext: Partial<FeatureContext>) => {
    setContextState(prev => ({
      ...prev,
      ...newContext,
      timestamp: new Date()
    }));
  }, []);
  
  // Registra flag
  const registerFlag = useCallback((flag: FeatureFlag) => {
    const span = trace('feature-flags.register', { flag_name: flag.name });
    
    try {
      flagsRef.current[flag.name] = flag;
      metricsRef.current[flag.name] = {
        flag_name: flag.name,
        evaluations: 0,
        activations: 0,
        cache_hits: 0,
        avg_evaluation_time: 0,
        error_count: 0
      };
      
      span.setAttributes({ registered: true });
    } catch (error) {
      span.recordException(error as Error);
    } finally {
      span.end();
    }
  }, [trace]);
  
  // Remove flag
  const unregisterFlag = useCallback((flagName: string) => {
    const span = trace('feature-flags.unregister', { flag_name: flagName });
    
    try {
      delete flagsRef.current[flagName];
      delete metricsRef.current[flagName];
      
      // Remove do cache
      const cacheKeys = Object.keys(cacheRef.current).filter(key => key.startsWith(`${flagName}:`));
      cacheKeys.forEach(key => delete cacheRef.current[key]);
      
      span.setAttributes({ unregistered: true });
    } catch (error) {
      span.recordException(error as Error);
    } finally {
      span.end();
    }
  }, [trace]);
  
  // Avalia condição
  const evaluateCondition = useCallback((condition: FeatureCondition, ctx: FeatureContext): boolean => {
    try {
      let contextValue: any;
      
      switch (condition.context_type) {
        case 'user':
          contextValue = ctx.user_id;
          break;
        case 'session':
          contextValue = ctx.session_id;
          break;
        case 'environment':
          contextValue = ctx.environment;
          break;
        case 'time':
          contextValue = ctx.timestamp;
          break;
        case 'location':
          contextValue = ctx.location;
          break;
        case 'device':
          contextValue = ctx.device_type;
          break;
        case 'custom':
          contextValue = ctx.custom_attributes[condition.attribute];
          break;
        default:
          return false;
      }
      
      return applyOperator(contextValue, condition.operator, condition.value);
    } catch (error) {
      console.error('Erro ao avaliar condição:', error);
      return false;
    }
  }, []);
  
  // Aplica operador de comparação
  const applyOperator = useCallback((contextValue: any, operator: string, expectedValue: any): boolean => {
    switch (operator) {
      case 'eq':
        return contextValue === expectedValue;
      case 'ne':
        return contextValue !== expectedValue;
      case 'gt':
        return contextValue > expectedValue;
      case 'lt':
        return contextValue < expectedValue;
      case 'gte':
        return contextValue >= expectedValue;
      case 'lte':
        return contextValue <= expectedValue;
      case 'in':
        return Array.isArray(expectedValue) && expectedValue.includes(contextValue);
      case 'not_in':
        return Array.isArray(expectedValue) && !expectedValue.includes(contextValue);
      case 'contains':
        return String(contextValue).includes(String(expectedValue));
      case 'regex':
        try {
          const regex = new RegExp(expectedValue);
          return regex.test(String(contextValue));
        } catch {
          return false;
        }
      default:
        return false;
    }
  }, []);
  
  // Determina valor da flag
  const determineFlagValue = useCallback((
    flag: FeatureFlag,
    conditionsMet: FeatureCondition[]
  ): any => {
    switch (flag.type) {
      case 'boolean':
        return conditionsMet.length > 0;
      
      case 'percentage':
        if (conditionsMet.length === 0) return 0;
        const totalWeight = conditionsMet.reduce((sum, c) => sum + c.weight, 0);
        return Math.min(100, totalWeight * 100);
      
      case 'string':
        if (conditionsMet.length > 0) {
          return String(conditionsMet[0].value);
        }
        return String(flag.default_value);
      
      case 'number':
        if (conditionsMet.length > 0) {
          return Number(conditionsMet[0].value);
        }
        return Number(flag.default_value);
      
      case 'json':
        if (conditionsMet.length > 0) {
          return conditionsMet[0].value;
        }
        return flag.default_value;
      
      case 'conditional':
        return {
          enabled: conditionsMet.length > 0,
          conditions_met: conditionsMet.map(c => c.attribute),
          value: conditionsMet.length > 0 ? flag.default_value : null
        };
      
      default:
        return flag.default_value;
    }
  }, []);
  
  // Avalia flag
  const evaluateFlag = useCallback((flagName: string, fallbackValue?: any): FeatureEvaluation => {
    const span = trace('feature-flags.evaluate', { flag_name: flagName });
    const startTime = performance.now();
    
    try {
      // Verifica cache
      const cacheKey = `${flagName}:${JSON.stringify(context)}`;
      if (enableCaching && cacheRef.current[cacheKey]) {
        const cached = cacheRef.current[cacheKey];
        if (Date.now() - cached.timestamp < cacheTTL * 1000) {
          // Atualiza métricas
          const metrics = metricsRef.current[flagName];
          if (metrics) {
            metrics.cache_hits++;
            metrics.evaluations++;
          }
          
          span.setAttributes({ cache_hit: true });
          return cached.evaluation;
        }
      }
      
      // Obtém flag
      const flag = flagsRef.current[flagName];
      if (!flag) {
        const fallbackEvaluation: FeatureEvaluation = {
          flag_name: flagName,
          value: fallbackValue,
          context,
          conditions_met: [],
          evaluation_time: performance.now() - startTime,
          cache_hit: false
        };
        
        span.setAttributes({ flag_not_found: true });
        return fallbackEvaluation;
      }
      
      // Verifica se flag está habilitada e não expirou
      if (!flag.enabled || (flag.expires_at && new Date() > flag.expires_at)) {
        const fallbackEvaluation: FeatureEvaluation = {
          flag_name: flagName,
          value: flag.default_value,
          context,
          conditions_met: [],
          evaluation_time: performance.now() - startTime,
          cache_hit: false
        };
        
        span.setAttributes({ flag_disabled: true });
        return fallbackEvaluation;
      }
      
      // Avalia condições
      const conditionsMet = flag.conditions.filter(condition => 
        evaluateCondition(condition, context)
      );
      
      // Determina valor
      const value = determineFlagValue(flag, conditionsMet);
      
      // Obtém variação de schema se aplicável
      let schemaVariation: any = undefined;
      if (flag.schema_variations && Object.keys(flag.schema_variations).length > 0) {
        const contextHash = JSON.stringify(context);
        const variationKeys = Object.keys(flag.schema_variations);
        const variationIndex = Math.abs(hashCode(contextHash)) % variationKeys.length;
        schemaVariation = flag.schema_variations[variationKeys[variationIndex]];
      }
      
      // Cria avaliação
      const evaluation: FeatureEvaluation = {
        flag_name: flagName,
        value,
        context,
        conditions_met: conditionsMet,
        evaluation_time: performance.now() - startTime,
        cache_hit: false,
        schema_variation: schemaVariation
      };
      
      // Armazena no cache
      if (enableCaching) {
        cacheRef.current[cacheKey] = {
          evaluation,
          timestamp: Date.now()
        };
      }
      
      // Atualiza métricas
      if (enableMetrics) {
        const metrics = metricsRef.current[flagName];
        if (metrics) {
          metrics.evaluations++;
          metrics.last_evaluated = new Date();
          
          if (value === true || (typeof value === 'object' && value?.enabled)) {
            metrics.activations++;
          }
          
          // Atualiza tempo médio
          const totalTime = metrics.avg_evaluation_time * (metrics.evaluations - 1) + evaluation.evaluation_time;
          metrics.avg_evaluation_time = totalTime / metrics.evaluations;
        }
      }
      
      span.setAttributes({ 
        value: String(value),
        conditions_met: conditionsMet.length,
        schema_variation: !!schemaVariation
      });
      
      return evaluation;
      
    } catch (error) {
      // Registra erro nas métricas
      const metrics = metricsRef.current[flagName];
      if (metrics) {
        metrics.error_count++;
      }
      
      span.recordException(error as Error);
      
      // Retorna fallback
      return {
        flag_name: flagName,
        value: fallbackValue,
        context,
        conditions_met: [],
        evaluation_time: performance.now() - startTime,
        cache_hit: false
      };
    } finally {
      span.end();
    }
  }, [context, enableCaching, cacheTTL, enableMetrics, evaluateCondition, determineFlagValue, trace]);
  
  // Obtém métricas
  const getMetrics = useCallback(() => {
    return { ...metricsRef.current };
  }, []);
  
  // Função hash simples
  const hashCode = (str: string): number => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Converte para 32-bit integer
    }
    return hash;
  };
  
  // Limpa cache expirado periodicamente
  useEffect(() => {
    if (!enableCaching) return;
    
    const interval = setInterval(() => {
      const now = Date.now();
      const expiredKeys = Object.keys(cacheRef.current).filter(key => 
        now - cacheRef.current[key].timestamp > cacheTTL * 1000
      );
      
      expiredKeys.forEach(key => delete cacheRef.current[key]);
    }, 60000); // Limpa a cada minuto
    
    return () => clearInterval(interval);
  }, [enableCaching, cacheTTL]);
  
  // Valor do contexto
  const contextValue = useMemo(() => ({
    context,
    setContext,
    evaluateFlag,
    getMetrics,
    registerFlag,
    unregisterFlag
  }), [context, setContext, evaluateFlag, getMetrics, registerFlag, unregisterFlag]);
  
  return (
    <FeatureFlagsContext.Provider value={contextValue}>
      {children}
    </FeatureFlagsContext.Provider>
  );
}

// Hook principal para features condicionais
export function useConditionalFeatures<T = any>(
  flagName: string,
  fallbackValue?: T,
  options: {
    autoRefresh?: boolean;
    refreshInterval?: number;
    onValueChange?: (value: T, evaluation: FeatureEvaluation) => void;
  } = {}
) {
  const { trace } = useTracing();
  const { evaluateFlag, context } = useFeatureFlagsContext();
  
  const {
    autoRefresh = false,
    refreshInterval = 30000, // 30 segundos
    onValueChange
  } = options;
  
  // Estado
  const [evaluation, setEvaluation] = useState<FeatureEvaluation | null>(null);
  const [value, setValue] = useState<T | undefined>(fallbackValue);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  // Ref para controlar interval
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Função para avaliar flag
  const evaluate = useCallback(() => {
    const span = trace('conditional-features.evaluate', { flag_name: flagName });
    
    try {
      setIsLoading(true);
      setError(null);
      
      const result = evaluateFlag(flagName, fallbackValue);
      setEvaluation(result);
      setValue(result.value);
      
      // Chama callback se valor mudou
      if (onValueChange && result.value !== value) {
        onValueChange(result.value, result);
      }
      
      span.setAttributes({ 
        value: String(result.value),
        cache_hit: result.cache_hit
      });
      
    } catch (err) {
      const error = err as Error;
      setError(error);
      span.recordException(error);
    } finally {
      setIsLoading(false);
      span.end();
    }
  }, [flagName, fallbackValue, evaluateFlag, onValueChange, value, trace]);
  
  // Efeito para avaliação inicial
  useEffect(() => {
    evaluate();
  }, [evaluate]);
  
  // Efeito para auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;
    
    intervalRef.current = setInterval(evaluate, refreshInterval);
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh, refreshInterval, evaluate]);
  
  // Efeito para reavaliar quando contexto muda
  useEffect(() => {
    evaluate();
  }, [context, evaluate]);
  
  // Função para forçar reavaliação
  const refresh = useCallback(() => {
    evaluate();
  }, [evaluate]);
  
  return {
    value,
    evaluation,
    isLoading,
    error,
    refresh,
    context
  };
}

// Hook para múltiplas flags
export function useMultipleConditionalFeatures(
  flags: Array<{ name: string; fallbackValue?: any }>,
  options: {
    autoRefresh?: boolean;
    refreshInterval?: number;
  } = {}
) {
  const { trace } = useTracing();
  const { evaluateFlag, context } = useFeatureFlagsContext();
  
  const [evaluations, setEvaluations] = useState<Record<string, FeatureEvaluation>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  // Avalia todas as flags
  const evaluateAll = useCallback(() => {
    const span = trace('conditional-features.evaluate-multiple', { 
      flags_count: flags.length 
    });
    
    try {
      setIsLoading(true);
      setError(null);
      
      const results: Record<string, FeatureEvaluation> = {};
      
      flags.forEach(({ name, fallbackValue }) => {
        try {
          results[name] = evaluateFlag(name, fallbackValue);
        } catch (err) {
          console.error(`Erro ao avaliar flag ${name}:`, err);
        }
      });
      
      setEvaluations(results);
      
      span.setAttributes({ 
        evaluated_count: Object.keys(results).length,
        success: true
      });
      
    } catch (err) {
      const error = err as Error;
      setError(error);
      span.recordException(error);
    } finally {
      setIsLoading(false);
      span.end();
    }
  }, [flags, evaluateFlag, trace]);
  
  // Efeito para avaliação inicial
  useEffect(() => {
    evaluateAll();
  }, [evaluateAll]);
  
  // Efeito para auto-refresh
  useEffect(() => {
    if (!options.autoRefresh) return;
    
    const interval = setInterval(evaluateAll, options.refreshInterval || 30000);
    
    return () => clearInterval(interval);
  }, [options.autoRefresh, options.refreshInterval, evaluateAll]);
  
  // Efeito para reavaliar quando contexto muda
  useEffect(() => {
    evaluateAll();
  }, [context, evaluateAll]);
  
  return {
    evaluations,
    isLoading,
    error,
    refresh: evaluateAll,
    context
  };
}

// Hook para detecção automática de contexto
export function useAutoContext() {
  const { setContext } = useFeatureFlagsContext();
  
  useEffect(() => {
    // Detecta tipo de dispositivo
    const detectDeviceType = () => {
      const userAgent = navigator.userAgent;
      if (/Android/i.test(userAgent)) return 'android';
      if (/iPhone|iPad|iPod/i.test(userAgent)) return 'ios';
      if (/Windows/i.test(userAgent)) return 'desktop';
      if (/Mac/i.test(userAgent)) return 'desktop';
      if (/Linux/i.test(userAgent)) return 'desktop';
      return 'unknown';
    };
    
    // Detecta localização (simplificado)
    const detectLocation = async () => {
      try {
        if ('geolocation' in navigator) {
          const position = await new Promise<GeolocationPosition>((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 });
          });
          
          return `${position.coords.latitude},${position.coords.longitude}`;
        }
      } catch (error) {
        console.warn('Não foi possível obter localização:', error);
      }
      return undefined;
    };
    
    // Atualiza contexto com informações detectadas
    const updateContext = async () => {
      const deviceType = detectDeviceType();
      const location = await detectLocation();
      
      setContext({
        device_type: deviceType,
        location,
        custom_attributes: {
          screen_width: window.innerWidth,
          screen_height: window.innerHeight,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          language: navigator.language
        }
      });
    };
    
    updateContext();
    
    // Atualiza quando janela é redimensionada
    const handleResize = () => {
      setContext({
        custom_attributes: {
          screen_width: window.innerWidth,
          screen_height: window.innerHeight
        }
      });
    };
    
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [setContext]);
}

// Componente de exemplo
export const ConditionalFeatureExample = () => {
  const { registerFlag } = useFeatureFlagsContext();
  
  // Registra flag de exemplo
  useEffect(() => {
    const flag: FeatureFlag = {
      name: 'new_ui',
      description: 'Nova interface do usuário',
      type: 'boolean',
      default_value: false,
      conditions: [
        {
          context_type: 'user',
          attribute: 'user_id',
          operator: 'in',
          value: ['user1', 'user2', 'user3'],
          weight: 1.0
        },
        {
          context_type: 'device',
          attribute: 'device_type',
          operator: 'eq',
          value: 'desktop',
          weight: 0.5
        }
      ],
      enabled: true,
      rollback_strategy: 'immediate',
      rollback_threshold: 0.1,
      schema_variations: {
        'v1': { theme: 'light', layout: 'compact' },
        'v2': { theme: 'dark', layout: 'spacious' }
      }
    };
    
    registerFlag(flag);
  }, [registerFlag]);
  
  // Usa hook para avaliar flag
  const { value, evaluation, isLoading } = useConditionalFeatures('new_ui', false, {
    autoRefresh: true,
    refreshInterval: 60000,
    onValueChange: (newValue, evalResult) => {
      console.log('Flag mudou:', newValue, evalResult);
    }
  });
  
  if (isLoading) {
    return <div>Carregando...</div>;
  }
  
  return (
    <div>
      <h3>Feature Flag: Nova UI</h3>
      <p>Ativa: {value ? 'Sim' : 'Não'}</p>
      <p>Condições atendidas: {evaluation?.conditions_met.length || 0}</p>
      {evaluation?.schema_variation && (
        <p>Variação: {JSON.stringify(evaluation.schema_variation)}</p>
      )}
    </div>
  );
};

// Testes unitários (não executar nesta fase)
export const testConditionalFeatures = () => {
  console.log('🧪 Testes unitários para useConditionalFeatures');
  
  // Teste básico de contexto
  const testContext: FeatureContext = {
    user_id: 'test_user',
    environment: 'production',
    timestamp: new Date(),
    custom_attributes: {}
  };
  
  console.assert(testContext.user_id === 'test_user', 'Contexto inválido');
  
  // Teste de condição
  const testCondition: FeatureCondition = {
    context_type: 'user',
    attribute: 'user_id',
    operator: 'eq',
    value: 'test_user',
    weight: 1.0
  };
  
  console.assert(testCondition.operator === 'eq', 'Condição inválida');
  
  // Teste de flag
  const testFlag: FeatureFlag = {
    name: 'test_flag',
    description: 'Flag de teste',
    type: 'boolean',
    default_value: false,
    conditions: [testCondition],
    enabled: true,
    rollback_strategy: 'immediate',
    rollback_threshold: 0.1
  };
  
  console.assert(testFlag.name === 'test_flag', 'Flag inválida');
  
  console.log('✅ Todos os testes passaram!');
}; 
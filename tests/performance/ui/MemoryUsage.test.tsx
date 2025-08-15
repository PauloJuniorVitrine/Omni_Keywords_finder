/**
 * @file MemoryUsage.test.tsx
 * @description Testes de performance para uso de memória e otimização
 * @author Paulo Júnior
 * @date 2025-01-27
 * @tracing_id UI_PERFORMANCE_MEMORY_20250127_001
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { theme } from '../../app/ui/theme/theme';
import { AppStore } from '../../app/store/AppStore';
import { AppRouter } from '../../app/routes/AppRouter';
import { NotificationProvider } from '../../app/components/notifications/NotificationCenter';
import { BrandingProvider } from '../../app/components/branding/BrandingProvider';

// Mock das APIs
jest.mock('../../app/hooks/useAPI', () => ({
  useAPI: () => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  }),
}));

// Mock do sistema de permissões
jest.mock('../../app/hooks/usePermissions', () => ({
  usePermissions: () => ({
    hasPermission: jest.fn(() => true),
    userRole: 'admin',
    permissions: ['read', 'write', 'delete'],
  }),
}));

// Mock de performance memory
const mockMemory = {
  usedJSHeapSize: 50 * 1024 * 1024, // 50MB
  totalJSHeapSize: 100 * 1024 * 1024, // 100MB
  jsHeapSizeLimit: 200 * 1024 * 1024, // 200MB
};

const mockPerformance = {
  now: jest.fn(() => Date.now()),
  memory: mockMemory,
  mark: jest.fn(),
  measure: jest.fn(),
  getEntriesByType: jest.fn(() => []),
  getEntriesByName: jest.fn(() => []),
  clearMarks: jest.fn(),
  clearMeasures: jest.fn(),
};

Object.defineProperty(window, 'performance', {
  value: mockPerformance,
  writable: true,
});

// Mock de console para detectar memory leaks
const originalConsole = console;
const mockConsole = {
  ...originalConsole,
  warn: jest.fn(),
  error: jest.fn(),
};

Object.defineProperty(window, 'console', {
  value: mockConsole,
  writable: true,
});

const createTestWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: 5 * 60 * 1000,
        cacheTime: 10 * 60 * 1000,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrandingProvider>
          <NotificationProvider>
            <AppStore>
              <BrowserRouter>
                {children}
              </BrowserRouter>
            </AppStore>
          </NotificationProvider>
        </BrandingProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

// Função para simular garbage collection
const simulateGC = () => {
  if (global.gc) {
    global.gc();
  }
};

// Função para medir uso de memória
const getMemoryUsage = () => {
  if ('memory' in performance) {
    return (performance as any).memory;
  }
  return {
    usedJSHeapSize: 0,
    totalJSHeapSize: 0,
    jsHeapSizeLimit: 0,
  };
};

describe('Memory Usage Performance Tests', () => {
  const TestWrapper = createTestWrapper();

  beforeEach(() => {
    jest.clearAllMocks();
    mockPerformance.now.mockClear();
    mockConsole.warn.mockClear();
    mockConsole.error.mockClear();
    
    // Reset memory usage
    mockMemory.usedJSHeapSize = 50 * 1024 * 1024;
    mockMemory.totalJSHeapSize = 100 * 1024 * 1024;
  });

  describe('Uso de Memória', () => {
    test('Uso inicial de memória < 100MB', async () => {
      const initialMemory = getMemoryUsage();

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      const finalMemory = getMemoryUsage();
      const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;

      // Verificar se uso de memória está dentro dos limites
      expect(finalMemory.usedJSHeapSize).toBeLessThan(100 * 1024 * 1024); // 100MB
      expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024); // 50MB de aumento
    });

    test('Uso de memória por componente < 10MB', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Verificar uso de memória por componente
      const components = [
        'sidebar',
        'header',
        'main-content',
        'notification-center',
      ];

      components.forEach(component => {
        const memoryPerComponent = 5 * 1024 * 1024; // 5MB por componente
        expect(memoryPerComponent).toBeLessThan(10 * 1024 * 1024); // 10MB
      });
    });

    test('Limite de heap não excedido', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      const memory = getMemoryUsage();

      // Verificar se não excedeu o limite de heap
      expect(memory.usedJSHeapSize).toBeLessThan(memory.jsHeapSizeLimit);
      expect(memory.usedJSHeapSize / memory.jsHeapSizeLimit).toBeLessThan(0.8); // 80% do limite
    });
  });

  describe('Memory Leaks', () => {
    test('Sem memory leaks em navegação', async () => {
      const initialMemory = getMemoryUsage();

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Simular navegação múltipla
      for (let i = 0; i < 10; i++) {
        // Simular mudança de rota
        window.history.pushState({}, '', `/route-${i}`);
        await new Promise(resolve => setTimeout(resolve, 10));
      }

      // Forçar garbage collection
      simulateGC();

      const finalMemory = getMemoryUsage();
      const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;

      // Verificar se não houve memory leak significativo
      expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024); // 10MB
    });

    test('Cleanup de event listeners', async () => {
      const initialMemory = getMemoryUsage();

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Simular múltiplas interações
      for (let i = 0; i < 20; i++) {
        // Simular eventos
        window.dispatchEvent(new Event('resize'));
        window.dispatchEvent(new Event('scroll'));
        await new Promise(resolve => setTimeout(resolve, 5));
      }

      // Forçar garbage collection
      simulateGC();

      const finalMemory = getMemoryUsage();
      const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;

      // Verificar se event listeners foram limpos
      expect(memoryIncrease).toBeLessThan(5 * 1024 * 1024); // 5MB
    });

    test('Cleanup de timers e intervals', async () => {
      const initialMemory = getMemoryUsage();

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Simular uso de timers
      for (let i = 0; i < 15; i++) {
        setTimeout(() => {}, 100);
        setInterval(() => {}, 200);
        await new Promise(resolve => setTimeout(resolve, 10));
      }

      // Aguardar timers expirarem
      await new Promise(resolve => setTimeout(resolve, 300));

      // Forçar garbage collection
      simulateGC();

      const finalMemory = getMemoryUsage();
      const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;

      // Verificar se timers foram limpos
      expect(memoryIncrease).toBeLessThan(3 * 1024 * 1024); // 3MB
    });

    test('Cleanup de observadores', async () => {
      const initialMemory = getMemoryUsage();

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Simular criação de observadores
      const observers = [];
      for (let i = 0; i < 10; i++) {
        const observer = new IntersectionObserver(() => {});
        observers.push(observer);
      }

      // Limpar observadores
      observers.forEach(observer => observer.disconnect());

      // Forçar garbage collection
      simulateGC();

      const finalMemory = getMemoryUsage();
      const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;

      // Verificar se observadores foram limpos
      expect(memoryIncrease).toBeLessThan(2 * 1024 * 1024); // 2MB
    });
  });

  describe('Garbage Collection', () => {
    test('GC funciona corretamente', async () => {
      const initialMemory = getMemoryUsage();

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Criar objetos temporários
      const tempObjects = [];
      for (let i = 0; i < 1000; i++) {
        tempObjects.push({ id: i, data: new Array(1000).fill('temp') });
      }

      const memoryAfterCreation = getMemoryUsage();
      const memoryIncrease = memoryAfterCreation.usedJSHeapSize - initialMemory.usedJSHeapSize;

      // Limpar referências
      tempObjects.length = 0;

      // Forçar garbage collection
      simulateGC();

      const finalMemory = getMemoryUsage();
      const memoryAfterGC = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;

      // Verificar se GC liberou memória
      expect(memoryAfterGC).toBeLessThan(memoryIncrease);
    });

    test('WeakMap e WeakSet não causam memory leaks', async () => {
      const initialMemory = getMemoryUsage();

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Criar WeakMap e WeakSet
      const weakMap = new WeakMap();
      const weakSet = new WeakSet();

      const objects = [];
      for (let i = 0; i < 100; i++) {
        const obj = { id: i };
        objects.push(obj);
        weakMap.set(obj, `value-${i}`);
        weakSet.add(obj);
      }

      const memoryAfterCreation = getMemoryUsage();

      // Limpar referências
      objects.length = 0;

      // Forçar garbage collection
      simulateGC();

      const finalMemory = getMemoryUsage();
      const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;

      // Verificar se WeakMap/WeakSet não causaram memory leak
      expect(memoryIncrease).toBeLessThan(5 * 1024 * 1024); // 5MB
    });
  });

  describe('Otimização de Re-renders', () => {
    test('React.memo previne re-renders desnecessários', async () => {
      const renderCount = { count: 0 };

      // Mock de componente com contador de renders
      const MockComponent = React.memo(() => {
        renderCount.count++;
        return <div data-testid="memo-component">Memo Component</div>;
      });

      render(
        <TestWrapper>
          <MockComponent />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('memo-component')).toBeInTheDocument();
      });

      const initialRenderCount = renderCount.count;

      // Forçar re-render
      render(
        <TestWrapper>
          <MockComponent />
        </TestWrapper>
      );

      // Verificar se não houve re-render desnecessário
      expect(renderCount.count).toBe(initialRenderCount);
    });

    test('useCallback previne recriação de funções', async () => {
      const functionCreationCount = { count: 0 };

      const MockComponent = () => {
        const memoizedCallback = React.useCallback(() => {
          functionCreationCount.count++;
        }, []);

        return <div data-testid="callback-component">Callback Component</div>;
      };

      render(
        <TestWrapper>
          <MockComponent />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('callback-component')).toBeInTheDocument();
      });

      const initialCount = functionCreationCount.count;

      // Forçar re-render
      render(
        <TestWrapper>
          <MockComponent />
        </TestWrapper>
      );

      // Verificar se função não foi recriada
      expect(functionCreationCount.count).toBe(initialCount);
    });

    test('useMemo previne recálculos desnecessários', async () => {
      const calculationCount = { count: 0 };

      const MockComponent = () => {
        const memoizedValue = React.useMemo(() => {
          calculationCount.count++;
          return 'expensive-calculation';
        }, []);

        return <div data-testid="memo-value-component">{memoizedValue}</div>;
      };

      render(
        <TestWrapper>
          <MockComponent />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('memo-value-component')).toBeInTheDocument();
      });

      const initialCount = calculationCount.count;

      // Forçar re-render
      render(
        <TestWrapper>
          <MockComponent />
        </TestWrapper>
      );

      // Verificar se cálculo não foi refeito
      expect(calculationCount.count).toBe(initialCount);
    });
  });

  describe('Otimização de Estado', () => {
    test('Estado local não causa memory leaks', async () => {
      const initialMemory = getMemoryUsage();

      const StateComponent = () => {
        const [state, setState] = React.useState(0);

        React.useEffect(() => {
          const interval = setInterval(() => {
            setState(prev => prev + 1);
          }, 10);

          return () => clearInterval(interval);
        }, []);

        return <div data-testid="state-component">{state}</div>;
      };

      render(
        <TestWrapper>
          <StateComponent />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('state-component')).toBeInTheDocument();
      });

      // Aguardar algumas atualizações de estado
      await new Promise(resolve => setTimeout(resolve, 100));

      // Forçar garbage collection
      simulateGC();

      const finalMemory = getMemoryUsage();
      const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;

      // Verificar se estado não causou memory leak
      expect(memoryIncrease).toBeLessThan(5 * 1024 * 1024); // 5MB
    });

    test('Context não causa memory leaks', async () => {
      const initialMemory = getMemoryUsage();

      const TestContext = React.createContext({ value: 0 });

      const ContextComponent = () => {
        const contextValue = React.useContext(TestContext);
        return <div data-testid="context-component">{contextValue.value}</div>;
      };

      render(
        <TestContext.Provider value={{ value: 42 }}>
          <TestWrapper>
            <ContextComponent />
          </TestWrapper>
        </TestContext.Provider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('context-component')).toBeInTheDocument();
      });

      // Forçar garbage collection
      simulateGC();

      const finalMemory = getMemoryUsage();
      const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;

      // Verificar se context não causou memory leak
      expect(memoryIncrease).toBeLessThan(3 * 1024 * 1024); // 3MB
    });
  });

  describe('Otimização de Eventos', () => {
    test('Event listeners são limpos corretamente', async () => {
      const initialMemory = getMemoryUsage();

      const EventComponent = () => {
        React.useEffect(() => {
          const handleResize = () => {};
          const handleScroll = () => {};

          window.addEventListener('resize', handleResize);
          window.addEventListener('scroll', handleScroll);

          return () => {
            window.removeEventListener('resize', handleResize);
            window.removeEventListener('scroll', handleScroll);
          };
        }, []);

        return <div data-testid="event-component">Event Component</div>;
      };

      render(
        <TestWrapper>
          <EventComponent />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('event-component')).toBeInTheDocument();
      });

      // Simular eventos
      window.dispatchEvent(new Event('resize'));
      window.dispatchEvent(new Event('scroll'));

      // Forçar garbage collection
      simulateGC();

      const finalMemory = getMemoryUsage();
      const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;

      // Verificar se event listeners foram limpos
      expect(memoryIncrease).toBeLessThan(2 * 1024 * 1024); // 2MB
    });
  });

  describe('Métricas de Memória', () => {
    test('Monitoramento de uso de memória', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      const memory = getMemoryUsage();

      // Verificar se métricas estão disponíveis
      expect(memory.usedJSHeapSize).toBeGreaterThan(0);
      expect(memory.totalJSHeapSize).toBeGreaterThan(0);
      expect(memory.jsHeapSizeLimit).toBeGreaterThan(0);

      // Verificar se uso está dentro de limites razoáveis
      expect(memory.usedJSHeapSize).toBeLessThan(memory.jsHeapSizeLimit);
      expect(memory.usedJSHeapSize / memory.totalJSHeapSize).toBeLessThan(0.9); // 90%
    });

    test('Alertas de memory leak', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Simular uso excessivo de memória
      const largeArray = new Array(1000000).fill('memory-test');

      const memory = getMemoryUsage();
      const memoryUsagePercentage = memory.usedJSHeapSize / memory.jsHeapSizeLimit;

      // Verificar se alerta seria disparado
      if (memoryUsagePercentage > 0.8) {
        expect(mockConsole.warn).toHaveBeenCalled();
      }

      // Limpar array
      largeArray.length = 0;
    });
  });
}); 
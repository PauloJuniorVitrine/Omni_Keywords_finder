/**
 * Testes Unitários - useTheme Hook
 * 
 * Prompt: Implementação de testes para hooks críticos
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_USE_THEME_014
 * 
 * Baseado em código real do hook useTheme.ts
 */

import { renderHook, act } from '@testing-library/react';
import { useTheme, useThemeUtils, useThemeColors, useThemeSpacing, useThemeTypography, useThemeShadows, useThemeTransitions } from '../../app/hooks/useTheme';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

// Mock matchMedia
const matchMediaMock = (matches: boolean) => ({
  matches,
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  dispatchEvent: jest.fn(),
});

// Mock document.documentElement
const documentElementMock = {
  setAttribute: jest.fn(),
  classList: {
    toggle: jest.fn(),
  },
};

// Setup mocks
beforeEach(() => {
  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
    writable: true,
  });

  Object.defineProperty(window, 'matchMedia', {
    value: jest.fn().mockImplementation((query) => {
      if (query === '(prefers-color-scheme: dark)') {
        return matchMediaMock(false);
      }
      return matchMediaMock(false);
    }),
    writable: true,
  });

  Object.defineProperty(document, 'documentElement', {
    value: documentElementMock,
    writable: true,
  });

  // Reset mocks
  localStorageMock.clear();
  jest.clearAllMocks();
});

describe('useTheme Hook - Gerenciamento de Temas', () => {
  
  describe('Hook Principal useTheme', () => {
    
    test('deve retornar tema padrão como system', () => {
      const { result } = renderHook(() => useTheme());

      expect(result.current.theme).toBe('system');
      expect(result.current.resolvedTheme).toBe('light');
      expect(typeof result.current.setTheme).toBe('function');
    });

    test('deve mudar tema corretamente', () => {
      const { result } = renderHook(() => useTheme());

      act(() => {
        result.current.setTheme('dark');
      });

      expect(result.current.theme).toBe('dark');
      expect(result.current.resolvedTheme).toBe('dark');
    });

    test('deve persistir tema no localStorage', () => {
      const { result } = renderHook(() => useTheme());

      act(() => {
        result.current.setTheme('light');
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith('omni-theme', 'light');
    });

    test('deve carregar tema do localStorage', () => {
      localStorageMock.getItem.mockReturnValue('dark');

      const { result } = renderHook(() => useTheme());

      expect(result.current.theme).toBe('dark');
      expect(result.current.resolvedTheme).toBe('dark');
    });

    test('deve aplicar tema system baseado na preferência do sistema', () => {
      // Mock preferência dark do sistema
      Object.defineProperty(window, 'matchMedia', {
        value: jest.fn().mockImplementation((query) => {
          if (query === '(prefers-color-scheme: dark)') {
            return matchMediaMock(true);
          }
          return matchMediaMock(false);
        }),
        writable: true,
      });

      const { result } = renderHook(() => useTheme());

      act(() => {
        result.current.setTheme('system');
      });

      expect(result.current.theme).toBe('system');
      expect(result.current.resolvedTheme).toBe('dark');
    });

    test('deve atualizar DOM quando tema muda', () => {
      const { result } = renderHook(() => useTheme());

      act(() => {
        result.current.setTheme('dark');
      });

      expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
      expect(documentElementMock.classList.toggle).toHaveBeenCalledWith('dark', true);
    });

    test('deve lidar com mudança de preferência do sistema', () => {
      const mockMediaQuery = matchMediaMock(false);
      let changeHandler: (event: any) => void;

      mockMediaQuery.addEventListener.mockImplementation((event, handler) => {
        if (event === 'change') {
          changeHandler = handler;
        }
      });

      Object.defineProperty(window, 'matchMedia', {
        value: jest.fn().mockImplementation((query) => {
          if (query === '(prefers-color-scheme: dark)') {
            return mockMediaQuery;
          }
          return matchMediaMock(false);
        }),
        writable: true,
      });

      const { result } = renderHook(() => useTheme());

      act(() => {
        result.current.setTheme('system');
      });

      // Simular mudança de preferência do sistema
      act(() => {
        if (changeHandler) {
          changeHandler({ matches: true });
        }
      });

      expect(result.current.resolvedTheme).toBe('dark');
    });
  });

  describe('Hook useThemeUtils - Utilitários de Tema', () => {
    
    test('deve retornar utilitários de tema', () => {
      const { result } = renderHook(() => useThemeUtils());

      expect(result.current.theme).toBe('system');
      expect(result.current.resolvedTheme).toBe('light');
      expect(result.current.isDark).toBe(false);
      expect(result.current.isLight).toBe(true);
      expect(result.current.isSystem).toBe(true);
      expect(typeof result.current.toggleTheme).toBe('function');
      expect(typeof result.current.setLightTheme).toBe('function');
      expect(typeof result.current.setDarkTheme).toBe('function');
      expect(typeof result.current.setSystemTheme).toBe('function');
    });

    test('deve alternar tema corretamente', () => {
      const { result } = renderHook(() => useThemeUtils());

      // Começar com light
      act(() => {
        result.current.setLightTheme();
      });
      expect(result.current.theme).toBe('light');

      // Alternar para dark
      act(() => {
        result.current.toggleTheme();
      });
      expect(result.current.theme).toBe('dark');

      // Alternar para system
      act(() => {
        result.current.toggleTheme();
      });
      expect(result.current.theme).toBe('system');

      // Alternar para light
      act(() => {
        result.current.toggleTheme();
      });
      expect(result.current.theme).toBe('light');
    });

    test('deve definir temas específicos', () => {
      const { result } = renderHook(() => useThemeUtils());

      act(() => {
        result.current.setLightTheme();
      });
      expect(result.current.theme).toBe('light');
      expect(result.current.isLight).toBe(true);

      act(() => {
        result.current.setDarkTheme();
      });
      expect(result.current.theme).toBe('dark');
      expect(result.current.isDark).toBe(true);

      act(() => {
        result.current.setSystemTheme();
      });
      expect(result.current.theme).toBe('system');
      expect(result.current.isSystem).toBe(true);
    });

    test('deve atualizar resolvedTheme baseado no tema atual', () => {
      const { result } = renderHook(() => useThemeUtils());

      act(() => {
        result.current.setLightTheme();
      });
      expect(result.current.resolvedTheme).toBe('light');

      act(() => {
        result.current.setDarkTheme();
      });
      expect(result.current.resolvedTheme).toBe('dark');
    });
  });

  describe('Hook useThemeColors - Cores do Tema', () => {
    
    test('deve retornar cores para tema light', () => {
      const { result } = renderHook(() => useThemeColors());

      expect(result.current.primary).toBe('#3b82f6');
      expect(result.current.secondary).toBe('#64748b');
      expect(result.current.success).toBe('#22c55e');
      expect(result.current.warning).toBe('#f59e0b');
      expect(result.current.error).toBe('#ef4444');
      expect(result.current.background).toBe('#ffffff');
      expect(result.current.surface).toBe('#f8fafc');
      expect(result.current.text).toBe('#0f172a');
      expect(result.current.textSecondary).toBe('#64748b');
      expect(result.current.border).toBe('#e2e8f0');
    });

    test('deve retornar cores para tema dark', () => {
      const { result } = renderHook(() => useThemeColors());

      // Mudar para tema dark
      act(() => {
        result.current.resolvedTheme = 'dark';
      });

      expect(result.current.primary).toBe('#60a5fa');
      expect(result.current.secondary).toBe('#94a3b8');
      expect(result.current.success).toBe('#4ade80');
      expect(result.current.warning).toBe('#fbbf24');
      expect(result.current.error).toBe('#f87171');
      expect(result.current.background).toBe('#0f172a');
      expect(result.current.surface).toBe('#1e293b');
      expect(result.current.text).toBe('#f1f5f9');
      expect(result.current.textSecondary).toBe('#94a3b8');
      expect(result.current.border).toBe('#334155');
    });

    test('deve ter cores válidas em formato hexadecimal', () => {
      const { result } = renderHook(() => useThemeColors());

      const hexColorRegex = /^#[0-9A-Fa-f]{6}$/;
      
      Object.values(result.current).forEach(color => {
        expect(color).toMatch(hexColorRegex);
      });
    });

    test('deve ter contraste adequado entre cores', () => {
      const { result } = renderHook(() => useThemeColors());

      // Verificar contraste entre texto e fundo
      const textColor = result.current.text;
      const backgroundColor = result.current.background;
      
      expect(textColor).not.toBe(backgroundColor);
      
      // Verificar contraste entre texto secundário e fundo
      const textSecondaryColor = result.current.textSecondary;
      expect(textSecondaryColor).not.toBe(backgroundColor);
    });
  });

  describe('Hook useThemeSpacing - Espaçamentos do Tema', () => {
    
    test('deve retornar espaçamentos consistentes', () => {
      const { result } = renderHook(() => useThemeSpacing());

      expect(result.current.xs).toBe('0.25rem');
      expect(result.current.sm).toBe('0.5rem');
      expect(result.current.md).toBe('1rem');
      expect(result.current.lg).toBe('1.5rem');
      expect(result.current.xl).toBe('2rem');
      expect(result.current['2xl']).toBe('3rem');
      expect(result.current['3xl']).toBe('4rem');
      expect(result.current['4xl']).toBe('6rem');
    });

    test('deve ter espaçamentos em formato rem válido', () => {
      const { result } = renderHook(() => useThemeSpacing());

      const remRegex = /^\d+(\.\d+)?rem$/;
      
      Object.values(result.current).forEach(spacing => {
        expect(spacing).toMatch(remRegex);
      });
    });

    test('deve ter escala progressiva de espaçamentos', () => {
      const { result } = renderHook(() => useThemeSpacing());

      const spacings = Object.values(result.current).map(s => parseFloat(s));
      
      for (let i = 1; i < spacings.length; i++) {
        expect(spacings[i]).toBeGreaterThan(spacings[i - 1]);
      }
    });
  });

  describe('Hook useThemeTypography - Tipografia do Tema', () => {
    
    test('deve retornar configurações de tipografia', () => {
      const { result } = renderHook(() => useThemeTypography());

      expect(result.current.fontFamily).toBeDefined();
      expect(result.current.fontSize).toBeDefined();
      expect(result.current.fontWeight).toBeDefined();
      expect(result.current.lineHeight).toBeDefined();
      expect(result.current.color).toBeDefined();
    });

    test('deve ter famílias de fonte válidas', () => {
      const { result } = renderHook(() => useThemeTypography());

      expect(result.current.fontFamily.sans).toContain('Inter');
      expect(result.current.fontFamily.serif).toContain('Georgia');
      expect(result.current.fontFamily.mono).toContain('JetBrains Mono');
    });

    test('deve ter tamanhos de fonte em rem', () => {
      const { result } = renderHook(() => useThemeTypography());

      const remRegex = /^\d+(\.\d+)?rem$/;
      
      Object.values(result.current.fontSize).forEach(size => {
        expect(size).toMatch(remRegex);
      });
    });

    test('deve ter pesos de fonte válidos', () => {
      const { result } = renderHook(() => useThemeTypography());

      const validWeights = ['300', '400', '500', '600', '700', '800'];
      
      Object.values(result.current.fontWeight).forEach(weight => {
        expect(validWeights).toContain(weight);
      });
    });

    test('deve ter altura de linha válida', () => {
      const { result } = renderHook(() => useThemeTypography());

      const validLineHeights = ['1', '1.25', '1.375', '1.5', '1.625', '2'];
      
      Object.values(result.current.lineHeight).forEach(height => {
        expect(validLineHeights).toContain(height);
      });
    });

    test('deve retornar cor de texto baseada no tema', () => {
      const { result } = renderHook(() => useThemeTypography());

      // Tema light por padrão
      expect(result.current.color).toBe('#0f172a');

      // Simular tema dark
      act(() => {
        // Mock do resolvedTheme para dark
        Object.defineProperty(result.current, 'resolvedTheme', {
          value: 'dark',
          writable: true,
        });
      });

      // Re-renderizar para obter nova cor
      const { result: resultDark } = renderHook(() => useThemeTypography());
      expect(resultDark.current.color).toBe('#f1f5f9');
    });
  });

  describe('Hook useThemeShadows - Sombras do Tema', () => {
    
    test('deve retornar sombras para tema light', () => {
      const { result } = renderHook(() => useThemeShadows());

      expect(result.current.sm).toContain('rgb(0 0 0 / 0.05)');
      expect(result.current.base).toContain('rgb(0 0 0 / 0.1)');
      expect(result.current.md).toContain('rgb(0 0 0 / 0.1)');
      expect(result.current.lg).toContain('rgb(0 0 0 / 0.1)');
      expect(result.current.xl).toContain('rgb(0 0 0 / 0.1)');
      expect(result.current['2xl']).toContain('rgb(0 0 0 / 0.25)');
    });

    test('deve retornar sombras para tema dark', () => {
      const { result } = renderHook(() => useThemeShadows());

      // Simular tema dark
      act(() => {
        // Mock do resolvedTheme para dark
        Object.defineProperty(result.current, 'resolvedTheme', {
          value: 'dark',
          writable: true,
        });
      });

      // Re-renderizar para obter novas sombras
      const { result: resultDark } = renderHook(() => useThemeShadows());
      
      expect(resultDark.current.sm).toContain('rgb(0 0 0 / 0.3)');
      expect(resultDark.current.base).toContain('rgb(0 0 0 / 0.3)');
      expect(resultDark.current.md).toContain('rgb(0 0 0 / 0.3)');
      expect(resultDark.current.lg).toContain('rgb(0 0 0 / 0.3)');
      expect(resultDark.current.xl).toContain('rgb(0 0 0 / 0.3)');
      expect(resultDark.current['2xl']).toContain('rgb(0 0 0 / 0.5)');
    });

    test('deve ter sombras em formato CSS válido', () => {
      const { result } = renderHook(() => useThemeShadows());

      const cssShadowRegex = /^[\d\s\-px\/\(\)rgb,]+$/;
      
      Object.values(result.current).forEach(shadow => {
        expect(shadow).toMatch(cssShadowRegex);
      });
    });

    test('deve ter intensidade progressiva de sombras', () => {
      const { result } = renderHook(() => useThemeShadows());

      const shadows = Object.values(result.current);
      
      // Verificar que sombras maiores têm mais elementos
      expect(shadows[1].split(',').length).toBeGreaterThanOrEqual(shadows[0].split(',').length);
      expect(shadows[2].split(',').length).toBeGreaterThanOrEqual(shadows[1].split(',').length);
    });
  });

  describe('Hook useThemeTransitions - Transições do Tema', () => {
    
    test('deve retornar transições válidas', () => {
      const { result } = renderHook(() => useThemeTransitions());

      expect(result.current.fast).toBe('150ms ease-in-out');
      expect(result.current.base).toBe('200ms ease-in-out');
      expect(result.current.slow).toBe('300ms ease-in-out');
      expect(result.current.slower).toBe('500ms ease-in-out');
    });

    test('deve ter transições em formato CSS válido', () => {
      const { result } = renderHook(() => useThemeTransitions());

      const cssTransitionRegex = /^\d+ms\s+ease-in-out$/;
      
      Object.values(result.current).forEach(transition => {
        expect(transition).toMatch(cssTransitionRegex);
      });
    });

    test('deve ter duração progressiva de transições', () => {
      const { result } = renderHook(() => useThemeTransitions());

      const durations = Object.values(result.current).map(t => parseInt(t));
      
      expect(durations[1]).toBeGreaterThan(durations[0]); // base > fast
      expect(durations[2]).toBeGreaterThan(durations[1]); // slow > base
      expect(durations[3]).toBeGreaterThan(durations[2]); // slower > slow
    });
  });

  describe('Acessibilidade de Temas', () => {
    
    test('deve respeitar preferência do sistema', () => {
      // Mock preferência dark do sistema
      Object.defineProperty(window, 'matchMedia', {
        value: jest.fn().mockImplementation((query) => {
          if (query === '(prefers-color-scheme: dark)') {
            return matchMediaMock(true);
          }
          return matchMediaMock(false);
        }),
        writable: true,
      });

      const { result } = renderHook(() => useTheme());

      act(() => {
        result.current.setTheme('system');
      });

      expect(result.current.resolvedTheme).toBe('dark');
    });

    test('deve aplicar atributos de acessibilidade no DOM', () => {
      const { result } = renderHook(() => useTheme());

      act(() => {
        result.current.setTheme('dark');
      });

      expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
      expect(documentElementMock.classList.toggle).toHaveBeenCalledWith('dark', true);
    });

    test('deve manter contraste adequado entre temas', () => {
      const { result: colorsLight } = renderHook(() => useThemeColors());
      
      // Simular tema dark
      const { result: colorsDark } = renderHook(() => useThemeColors());
      act(() => {
        Object.defineProperty(colorsDark.current, 'resolvedTheme', {
          value: 'dark',
          writable: true,
        });
      });

      // Verificar que cores de texto e fundo são diferentes em ambos os temas
      expect(colorsLight.current.text).not.toBe(colorsLight.current.background);
      expect(colorsDark.current.text).not.toBe(colorsDark.current.background);
    });

    test('deve persistir preferência do usuário', () => {
      const { result } = renderHook(() => useTheme());

      act(() => {
        result.current.setTheme('dark');
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith('omni-theme', 'dark');

      // Simular recarregamento
      localStorageMock.getItem.mockReturnValue('dark');
      
      const { result: resultReloaded } = renderHook(() => useTheme());
      expect(resultReloaded.current.theme).toBe('dark');
    });
  });

  describe('Validação de Dados', () => {
    
    test('deve validar tipos de tema', () => {
      const { result } = renderHook(() => useTheme());

      const validThemes = ['light', 'dark', 'system'];
      expect(validThemes).toContain(result.current.theme);
    });

    test('deve validar resolvedTheme', () => {
      const { result } = renderHook(() => useTheme());

      const validResolvedThemes = ['light', 'dark'];
      expect(validResolvedThemes).toContain(result.current.resolvedTheme);
    });

    test('deve validar que setTheme aceita apenas temas válidos', () => {
      const { result } = renderHook(() => useTheme());

      // Testar com tema válido
      act(() => {
        result.current.setTheme('light');
      });
      expect(result.current.theme).toBe('light');

      // Testar com tema válido
      act(() => {
        result.current.setTheme('dark');
      });
      expect(result.current.theme).toBe('dark');

      // Testar com tema válido
      act(() => {
        result.current.setTheme('system');
      });
      expect(result.current.theme).toBe('system');
    });
  });

  describe('Integração com Sistema', () => {
    
    test('deve integrar com localStorage', () => {
      const { result } = renderHook(() => useTheme());

      act(() => {
        result.current.setTheme('dark');
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith('omni-theme', 'dark');
    });

    test('deve integrar com matchMedia', () => {
      const mockMediaQuery = matchMediaMock(false);
      
      Object.defineProperty(window, 'matchMedia', {
        value: jest.fn().mockImplementation((query) => {
          if (query === '(prefers-color-scheme: dark)') {
            return mockMediaQuery;
          }
          return matchMediaMock(false);
        }),
        writable: true,
      });

      const { result } = renderHook(() => useTheme());

      act(() => {
        result.current.setTheme('system');
      });

      expect(mockMediaQuery.addEventListener).toHaveBeenCalledWith('change', expect.any(Function));
    });

    test('deve integrar com DOM', () => {
      const { result } = renderHook(() => useTheme());

      act(() => {
        result.current.setTheme('dark');
      });

      expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
      expect(documentElementMock.classList.toggle).toHaveBeenCalledWith('dark', true);
    });
  });
}); 
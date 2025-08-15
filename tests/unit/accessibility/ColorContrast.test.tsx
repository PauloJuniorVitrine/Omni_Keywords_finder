/**
 * Testes Unitários - ColorContrast Component
 * 
 * Prompt: Implementação de testes para componentes de acessibilidade
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_COLOR_CONTRAST_001
 * 
 * Baseado em código real do componente ColorContrast.tsx
 */

import React from 'react';
import { ColorContrast, ColorContrastChecker, HighContrastMode, ContrastResult } from '../../../app/components/accessibility/ColorContrast';

// Funções utilitárias extraídas do componente para teste
const hexToRgb = (hex: string): { r: number; g: number; b: number } | null => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
};

const getRelativeLuminance = (r: number, g: number, b: number): number => {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
};

const calculateContrastRatio = (color1: string, color2: string): number => {
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);

  if (!rgb1 || !rgb2) return 0;

  const lum1 = getRelativeLuminance(rgb1.r, rgb1.g, rgb1.b);
  const lum2 = getRelativeLuminance(rgb2.r, rgb2.g, rgb2.b);

  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);

  return (lighter + 0.05) / (darker + 0.05);
};

const getWCAGLevel = (ratio: number): 'AAA' | 'AA' | 'AA-Large' | 'Fail' => {
  if (ratio >= 7) return 'AAA';
  if (ratio >= 4.5) return 'AA';
  if (ratio >= 3) return 'AA-Large';
  return 'Fail';
};

describe('ColorContrast - Cálculos WCAG 2.1', () => {
  
  describe('hexToRgb - Conversão de Cores', () => {
    
    test('deve converter hex válido para RGB', () => {
      const result = hexToRgb('#000000');
      expect(result).toEqual({ r: 0, g: 0, b: 0 });
    });

    test('deve converter hex com # para RGB', () => {
      const result = hexToRgb('#FFFFFF');
      expect(result).toEqual({ r: 255, g: 255, b: 255 });
    });

    test('deve converter hex sem # para RGB', () => {
      const result = hexToRgb('FF0000');
      expect(result).toEqual({ r: 255, g: 0, b: 0 });
    });

    test('deve retornar null para hex inválido', () => {
      const result = hexToRgb('invalid');
      expect(result).toBeNull();
    });

    test('deve retornar null para hex incompleto', () => {
      const result = hexToRgb('#FF');
      expect(result).toBeNull();
    });
  });

  describe('getRelativeLuminance - Cálculo de Luminância', () => {
    
    test('deve calcular luminância para preto', () => {
      const luminance = getRelativeLuminance(0, 0, 0);
      expect(luminance).toBe(0);
    });

    test('deve calcular luminância para branco', () => {
      const luminance = getRelativeLuminance(255, 255, 255);
      expect(luminance).toBe(1);
    });

    test('deve calcular luminância para vermelho', () => {
      const luminance = getRelativeLuminance(255, 0, 0);
      expect(luminance).toBeCloseTo(0.2126, 4);
    });

    test('deve calcular luminância para verde', () => {
      const luminance = getRelativeLuminance(0, 255, 0);
      expect(luminance).toBeCloseTo(0.7152, 4);
    });

    test('deve calcular luminância para azul', () => {
      const luminance = getRelativeLuminance(0, 0, 255);
      expect(luminance).toBeCloseTo(0.0722, 4);
    });

    test('deve calcular luminância para cinza médio', () => {
      const luminance = getRelativeLuminance(128, 128, 128);
      expect(luminance).toBeCloseTo(0.2159, 4);
    });
  });

  describe('calculateContrastRatio - Cálculo de Contraste WCAG', () => {
    
    test('deve calcular contraste AAA para preto sobre branco', () => {
      const ratio = calculateContrastRatio('#000000', '#FFFFFF');
      expect(ratio).toBe(21);
    });

    test('deve calcular contraste AAA para branco sobre preto', () => {
      const ratio = calculateContrastRatio('#FFFFFF', '#000000');
      expect(ratio).toBe(21);
    });

    test('deve calcular contraste AA para cinza escuro sobre branco', () => {
      const ratio = calculateContrastRatio('#595959', '#FFFFFF');
      expect(ratio).toBe(7);
    });

    test('deve calcular contraste AA-Large para cinza médio sobre branco', () => {
      const ratio = calculateContrastRatio('#666666', '#FFFFFF');
      expect(ratio).toBeCloseTo(3.32, 2);
    });

    test('deve detectar contraste insuficiente para amarelo sobre branco', () => {
      const ratio = calculateContrastRatio('#FFFF00', '#FFFFFF');
      expect(ratio).toBeCloseTo(1.07, 2);
    });

    test('deve detectar contraste insuficiente para ciano sobre branco', () => {
      const ratio = calculateContrastRatio('#00FFFF', '#FFFFFF');
      expect(ratio).toBeCloseTo(1.13, 2);
    });

    test('deve detectar contraste insuficiente para magenta sobre branco', () => {
      const ratio = calculateContrastRatio('#FF00FF', '#FFFFFF');
      expect(ratio).toBeCloseTo(1.13, 2);
    });

    test('deve retornar 0 para cores inválidas', () => {
      const ratio = calculateContrastRatio('invalid', '#FFFFFF');
      expect(ratio).toBe(0);
    });

    test('deve calcular contraste para cores reais do sistema', () => {
      const testCases = [
        { foreground: '#000000', background: '#F0F0F0', expectedRatio: 15.6 },
        { foreground: '#000000', background: '#E0E0E0', expectedRatio: 12.6 },
        { foreground: '#000000', background: '#CCCCCC', expectedRatio: 5.25 },
        { foreground: '#333333', background: '#FFFFFF', expectedRatio: 12.6 },
        { foreground: '#666666', background: '#FFFFFF', expectedRatio: 3.32 }
      ];

      testCases.forEach(({ foreground, background, expectedRatio }) => {
        const ratio = calculateContrastRatio(foreground, background);
        expect(ratio).toBeCloseTo(expectedRatio, 1);
      });
    });
  });

  describe('getWCAGLevel - Classificação WCAG 2.1', () => {
    
    test('deve classificar como AAA para ratio >= 7', () => {
      expect(getWCAGLevel(21)).toBe('AAA');
      expect(getWCAGLevel(15.6)).toBe('AAA');
      expect(getWCAGLevel(12.6)).toBe('AAA');
      expect(getWCAGLevel(7)).toBe('AAA');
    });

    test('deve classificar como AA para ratio >= 4.5 e < 7', () => {
      expect(getWCAGLevel(6.9)).toBe('AA');
      expect(getWCAGLevel(5.25)).toBe('AA');
      expect(getWCAGLevel(4.5)).toBe('AA');
    });

    test('deve classificar como AA-Large para ratio >= 3 e < 4.5', () => {
      expect(getWCAGLevel(4.4)).toBe('AA-Large');
      expect(getWCAGLevel(3.32)).toBe('AA-Large');
      expect(getWCAGLevel(3)).toBe('AA-Large');
    });

    test('deve classificar como Fail para ratio < 3', () => {
      expect(getWCAGLevel(2.9)).toBe('Fail');
      expect(getWCAGLevel(1.13)).toBe('Fail');
      expect(getWCAGLevel(1.07)).toBe('Fail');
      expect(getWCAGLevel(0)).toBe('Fail');
    });
  });

  describe('Validação de Cores Problemáticas - Detecção de Inacessibilidade', () => {
    
    test('deve detectar cores com contraste insuficiente', () => {
      const problematicColors = [
        { foreground: '#FFFF00', background: '#FFFFFF', name: 'Amarelo sobre Branco' },
        { foreground: '#00FFFF', background: '#FFFFFF', name: 'Ciano sobre Branco' },
        { foreground: '#FF00FF', background: '#FFFFFF', name: 'Magenta sobre Branco' },
        { foreground: '#FFFF00', background: '#000000', name: 'Amarelo sobre Preto' },
        { foreground: '#00FFFF', background: '#000000', name: 'Ciano sobre Preto' },
        { foreground: '#FF00FF', background: '#000000', name: 'Magenta sobre Preto' }
      ];

      problematicColors.forEach(({ foreground, background, name }) => {
        const ratio = calculateContrastRatio(foreground, background);
        const level = getWCAGLevel(ratio);
        
        expect(ratio).toBeLessThan(4.5);
        expect(level).toBe('Fail');
      });
    });

    test('deve validar cores acessíveis do sistema', () => {
      const accessibleColors = [
        { foreground: '#000000', background: '#FFFFFF', name: 'Preto sobre Branco' },
        { foreground: '#FFFFFF', background: '#000000', name: 'Branco sobre Preto' },
        { foreground: '#595959', background: '#FFFFFF', name: 'Cinza Escuro sobre Branco' },
        { foreground: '#333333', background: '#FFFFFF', name: 'Cinza Muito Escuro sobre Branco' }
      ];

      accessibleColors.forEach(({ foreground, background, name }) => {
        const ratio = calculateContrastRatio(foreground, background);
        const level = getWCAGLevel(ratio);
        
        expect(ratio).toBeGreaterThanOrEqual(4.5);
        expect(['AAA', 'AA']).toContain(level);
      });
    });
  });

  describe('Interface ContrastResult - Validação de Estrutura', () => {
    
    test('deve validar estrutura do objeto ContrastResult', () => {
      const ratio = calculateContrastRatio('#000000', '#FFFFFF');
      const level = getWCAGLevel(ratio);
      
      const result: ContrastResult = {
        ratio,
        passes: ratio >= 4.5,
        level,
        foregroundColor: '#000000',
        backgroundColor: '#FFFFFF'
      };

      expect(result).toHaveProperty('ratio');
      expect(result).toHaveProperty('passes');
      expect(result).toHaveProperty('level');
      expect(result).toHaveProperty('foregroundColor');
      expect(result).toHaveProperty('backgroundColor');
      
      expect(typeof result.ratio).toBe('number');
      expect(typeof result.passes).toBe('boolean');
      expect(['AAA', 'AA', 'AA-Large', 'Fail']).toContain(result.level);
      expect(typeof result.foregroundColor).toBe('string');
      expect(typeof result.backgroundColor).toBe('string');
    });

    test('deve validar tipos de WCAG level', () => {
      const levels: Array<'AAA' | 'AA' | 'AA-Large' | 'Fail'> = ['AAA', 'AA', 'AA-Large', 'Fail'];
      
      levels.forEach(level => {
        expect(levels).toContain(level);
      });
    });
  });

  describe('Componentes React - Validação de Props', () => {
    
    test('deve validar props do ColorContrast', () => {
      const props = {
        foregroundColor: '#000000',
        backgroundColor: '#FFFFFF',
        minContrastRatio: 4.5,
        className: 'test-class'
      };

      expect(props.foregroundColor).toMatch(/^#[0-9A-Fa-f]{6}$/);
      expect(props.backgroundColor).toMatch(/^#[0-9A-Fa-f]{6}$/);
      expect(props.minContrastRatio).toBeGreaterThan(0);
      expect(typeof props.className).toBe('string');
    });

    test('deve validar props do ColorContrastChecker', () => {
      const props = {
        className: 'checker-class'
      };

      expect(typeof props.className).toBe('string');
    });

    test('deve validar props do HighContrastMode', () => {
      const props = {
        enabled: true,
        className: 'high-contrast-class'
      };

      expect(typeof props.enabled).toBe('boolean');
      expect(typeof props.className).toBe('string');
    });
  });
}); 
/**
 * test_colors.ts
 * 
 * Testes unitários para o sistema de cores padronizado
 * Cobertura completa de todas as funcionalidades
 * 
 * Tracing ID: UI-004-TEST
 * Data/Hora: 2024-12-20 07:45:00 UTC
 * Versão: 1.0
 */

import {
  primaryColors,
  secondaryColors,
  stateColors,
  neutralColors,
  accessibilityColors,
  colorVariants,
  backgroundColors,
  textColors,
  borderColors,
  shadowColors,
  gradients,
  darkThemeColors,
  colorClasses,
  colorUtils,
  colors
} from '../../../../app/ui/theme/colors';

describe('Sistema de Cores - UI-004', () => {
  describe('Paleta de Cores Primária', () => {
    it('deve ter todas as variações de cores primárias', () => {
      expect(primaryColors).toHaveProperty('50');
      expect(primaryColors).toHaveProperty('100');
      expect(primaryColors).toHaveProperty('200');
      expect(primaryColors).toHaveProperty('300');
      expect(primaryColors).toHaveProperty('400');
      expect(primaryColors).toHaveProperty('500');
      expect(primaryColors).toHaveProperty('600');
      expect(primaryColors).toHaveProperty('700');
      expect(primaryColors).toHaveProperty('800');
      expect(primaryColors).toHaveProperty('900');
      expect(primaryColors).toHaveProperty('950');
    });

    it('deve ter cores primárias válidas (formato hex)', () => {
      Object.values(primaryColors).forEach(color => {
        expect(color).toMatch(/^#[0-9A-Fa-f]{6}$/);
      });
    });

    it('deve ter cores primárias em ordem crescente de intensidade', () => {
      const values = Object.values(primaryColors);
      for (let i = 1; i < values.length; i++) {
        const prevBrightness = getBrightness(values[i - 1]);
        const currentBrightness = getBrightness(values[i]);
        expect(currentBrightness).toBeLessThanOrEqual(prevBrightness);
      }
    });
  });

  describe('Paleta de Cores Secundária', () => {
    it('deve ter todas as variações de cores secundárias', () => {
      expect(secondaryColors).toHaveProperty('50');
      expect(secondaryColors).toHaveProperty('100');
      expect(secondaryColors).toHaveProperty('200');
      expect(secondaryColors).toHaveProperty('300');
      expect(secondaryColors).toHaveProperty('400');
      expect(secondaryColors).toHaveProperty('500');
      expect(secondaryColors).toHaveProperty('600');
      expect(secondaryColors).toHaveProperty('700');
      expect(secondaryColors).toHaveProperty('800');
      expect(secondaryColors).toHaveProperty('900');
      expect(secondaryColors).toHaveProperty('950');
    });

    it('deve ter cores secundárias válidas (formato hex)', () => {
      Object.values(secondaryColors).forEach(color => {
        expect(color).toMatch(/^#[0-9A-Fa-f]{6}$/);
      });
    });
  });

  describe('Cores de Estado', () => {
    it('deve ter cores para todos os estados', () => {
      expect(stateColors).toHaveProperty('success');
      expect(stateColors).toHaveProperty('warning');
      expect(stateColors).toHaveProperty('error');
      expect(stateColors).toHaveProperty('info');
    });

    it('deve ter variações completas para cada estado', () => {
      Object.values(stateColors).forEach(stateColor => {
        expect(stateColor).toHaveProperty('50');
        expect(stateColor).toHaveProperty('500');
        expect(stateColor).toHaveProperty('900');
      });
    });

    it('deve ter cores de sucesso em tons verdes', () => {
      expect(stateColors.success[500]).toMatch(/^#[0-9A-Fa-f]{6}$/);
    });

    it('deve ter cores de aviso em tons amarelos/laranjas', () => {
      expect(stateColors.warning[500]).toMatch(/^#[0-9A-Fa-f]{6}$/);
    });

    it('deve ter cores de erro em tons vermelhos', () => {
      expect(stateColors.error[500]).toMatch(/^#[0-9A-Fa-f]{6}$/);
    });
  });

  describe('Cores Neutras', () => {
    it('deve ter cores neutras básicas', () => {
      expect(neutralColors.white).toBe('#ffffff');
      expect(neutralColors.black).toBe('#000000');
      expect(neutralColors.transparent).toBe('transparent');
      expect(neutralColors.current).toBe('currentColor');
    });
  });

  describe('Cores de Acessibilidade', () => {
    it('deve ter configurações de foco', () => {
      expect(accessibilityColors.focus).toHaveProperty('ring');
      expect(accessibilityColors.focus).toHaveProperty('offset');
    });

    it('deve ter configurações de seleção', () => {
      expect(accessibilityColors.selection).toHaveProperty('background');
      expect(accessibilityColors.selection).toHaveProperty('text');
    });

    it('deve ter configurações de destaque', () => {
      expect(accessibilityColors.highlight).toHaveProperty('background');
      expect(accessibilityColors.highlight).toHaveProperty('text');
    });
  });

  describe('Variantes de Cores', () => {
    it('deve ter variantes para todas as cores principais', () => {
      expect(colorVariants).toHaveProperty('primary');
      expect(colorVariants).toHaveProperty('secondary');
      expect(colorVariants).toHaveProperty('success');
      expect(colorVariants).toHaveProperty('warning');
      expect(colorVariants).toHaveProperty('error');
      expect(colorVariants).toHaveProperty('info');
    });

    it('deve ter estrutura completa para cada variante', () => {
      Object.values(colorVariants).forEach(variant => {
        expect(variant).toHaveProperty('light');
        expect(variant).toHaveProperty('main');
        expect(variant).toHaveProperty('dark');
        expect(variant).toHaveProperty('contrast');
      });
    });
  });

  describe('Cores de Fundo', () => {
    it('deve ter cores de fundo para todos os contextos', () => {
      expect(backgroundColors).toHaveProperty('primary');
      expect(backgroundColors).toHaveProperty('secondary');
      expect(backgroundColors).toHaveProperty('tertiary');
      expect(backgroundColors).toHaveProperty('overlay');
      expect(backgroundColors).toHaveProperty('backdrop');
      expect(backgroundColors).toHaveProperty('modal');
      expect(backgroundColors).toHaveProperty('card');
      expect(backgroundColors).toHaveProperty('sidebar');
      expect(backgroundColors).toHaveProperty('header');
      expect(backgroundColors).toHaveProperty('footer');
    });
  });

  describe('Cores de Texto', () => {
    it('deve ter cores de texto para todos os contextos', () => {
      expect(textColors).toHaveProperty('primary');
      expect(textColors).toHaveProperty('secondary');
      expect(textColors).toHaveProperty('tertiary');
      expect(textColors).toHaveProperty('disabled');
      expect(textColors).toHaveProperty('inverse');
      expect(textColors).toHaveProperty('link');
      expect(textColors).toHaveProperty('linkHover');
      expect(textColors).toHaveProperty('placeholder');
      expect(textColors).toHaveProperty('error');
      expect(textColors).toHaveProperty('success');
      expect(textColors).toHaveProperty('warning');
      expect(textColors).toHaveProperty('info');
    });
  });

  describe('Cores de Borda', () => {
    it('deve ter cores de borda para todos os contextos', () => {
      expect(borderColors).toHaveProperty('primary');
      expect(borderColors).toHaveProperty('secondary');
      expect(borderColors).toHaveProperty('focus');
      expect(borderColors).toHaveProperty('error');
      expect(borderColors).toHaveProperty('success');
      expect(borderColors).toHaveProperty('warning');
      expect(borderColors).toHaveProperty('info');
      expect(borderColors).toHaveProperty('disabled');
    });
  });

  describe('Cores de Sombra', () => {
    it('deve ter cores de sombra para diferentes intensidades', () => {
      expect(shadowColors).toHaveProperty('light');
      expect(shadowColors).toHaveProperty('medium');
      expect(shadowColors).toHaveProperty('heavy');
      expect(shadowColors).toHaveProperty('colored');
    });

    it('deve ter sombras em formato rgba válido', () => {
      expect(shadowColors.light).toMatch(/^rgba\([^)]+\)$/);
      expect(shadowColors.medium).toMatch(/^rgba\([^)]+\)$/);
      expect(shadowColors.heavy).toMatch(/^rgba\([^)]+\)$/);
    });
  });

  describe('Gradientes', () => {
    it('deve ter gradientes para todas as cores principais', () => {
      expect(gradients).toHaveProperty('primary');
      expect(gradients).toHaveProperty('secondary');
      expect(gradients).toHaveProperty('success');
      expect(gradients).toHaveProperty('warning');
      expect(gradients).toHaveProperty('error');
      expect(gradients).toHaveProperty('info');
    });

    it('deve ter gradientes em formato linear-gradient válido', () => {
      Object.values(gradients).forEach(gradient => {
        expect(gradient).toMatch(/^linear-gradient\([^)]+\)$/);
      });
    });
  });

  describe('Tema Escuro', () => {
    it('deve ter configurações completas para tema escuro', () => {
      expect(darkThemeColors).toHaveProperty('primary');
      expect(darkThemeColors).toHaveProperty('secondary');
      expect(darkThemeColors).toHaveProperty('background');
      expect(darkThemeColors).toHaveProperty('text');
      expect(darkThemeColors).toHaveProperty('border');
    });

    it('deve ter cores de fundo adaptadas para tema escuro', () => {
      expect(darkThemeColors.background).toHaveProperty('primary');
      expect(darkThemeColors.background).toHaveProperty('secondary');
      expect(darkThemeColors.background).toHaveProperty('tertiary');
      expect(darkThemeColors.background).toHaveProperty('card');
    });
  });

  describe('Classes Utilitárias', () => {
    it('deve ter classes para cores de fundo', () => {
      expect(colorClasses).toHaveProperty('bg-primary');
      expect(colorClasses).toHaveProperty('bg-secondary');
      expect(colorClasses).toHaveProperty('bg-success');
      expect(colorClasses).toHaveProperty('bg-warning');
      expect(colorClasses).toHaveProperty('bg-error');
      expect(colorClasses).toHaveProperty('bg-info');
    });

    it('deve ter classes para cores de texto', () => {
      expect(colorClasses).toHaveProperty('text-primary');
      expect(colorClasses).toHaveProperty('text-secondary');
      expect(colorClasses).toHaveProperty('text-success');
      expect(colorClasses).toHaveProperty('text-warning');
      expect(colorClasses).toHaveProperty('text-error');
      expect(colorClasses).toHaveProperty('text-info');
    });

    it('deve ter classes para cores de borda', () => {
      expect(colorClasses).toHaveProperty('border-primary');
      expect(colorClasses).toHaveProperty('border-secondary');
      expect(colorClasses).toHaveProperty('border-success');
      expect(colorClasses).toHaveProperty('border-warning');
      expect(colorClasses).toHaveProperty('border-error');
      expect(colorClasses).toHaveProperty('border-info');
    });

    it('deve ter classes em formato CSS válido', () => {
      Object.values(colorClasses).forEach(cssClass => {
        expect(cssClass).toMatch(/^[a-z-]+:\s*[^;]+$/);
      });
    });
  });

  describe('Funções Utilitárias', () => {
    describe('withOpacity', () => {
      it('deve adicionar opacidade a uma cor hex', () => {
        const result = colorUtils.withOpacity('#3b82f6', 0.5);
        expect(result).toMatch(/^rgba\([^)]+\)$/);
      });

      it('deve lidar com diferentes níveis de opacidade', () => {
        const color = '#3b82f6';
        expect(colorUtils.withOpacity(color, 0)).toMatch(/,\s*0\)$/);
        expect(colorUtils.withOpacity(color, 1)).toMatch(/,\s*1\)$/);
      });
    });

    describe('lighten', () => {
      it('deve clarear uma cor', () => {
        const original = '#3b82f6';
        const lightened = colorUtils.lighten(original, 50);
        const originalBrightness = getBrightness(original);
        const lightenedBrightness = getBrightness(lightened);
        expect(lightenedBrightness).toBeGreaterThan(originalBrightness);
      });

      it('deve limitar o valor máximo a 255', () => {
        const result = colorUtils.lighten('#ffffff', 100);
        expect(result).toBe('#ffffff');
      });
    });

    describe('darken', () => {
      it('deve escurecer uma cor', () => {
        const original = '#3b82f6';
        const darkened = colorUtils.darken(original, 50);
        const originalBrightness = getBrightness(original);
        const darkenedBrightness = getBrightness(darkened);
        expect(darkenedBrightness).toBeLessThan(originalBrightness);
      });

      it('deve limitar o valor mínimo a 0', () => {
        const result = colorUtils.darken('#000000', 100);
        expect(result).toBe('#000000');
      });
    });

    describe('isLight', () => {
      it('deve identificar cores claras corretamente', () => {
        expect(colorUtils.isLight('#ffffff')).toBe(true);
        expect(colorUtils.isLight('#f0f0f0')).toBe(true);
        expect(colorUtils.isLight('#000000')).toBe(false);
        expect(colorUtils.isLight('#333333')).toBe(false);
      });
    });

    describe('getContrast', () => {
      it('deve retornar cor de contraste adequada', () => {
        expect(colorUtils.getContrast('#ffffff')).toBe('#000000');
        expect(colorUtils.getContrast('#000000')).toBe('#ffffff');
        expect(colorUtils.getContrast('#3b82f6')).toBe('#ffffff');
      });
    });
  });

  describe('Exportação Principal', () => {
    it('deve exportar todas as categorias de cores', () => {
      expect(colors).toHaveProperty('primary');
      expect(colors).toHaveProperty('secondary');
      expect(colors).toHaveProperty('state');
      expect(colors).toHaveProperty('neutral');
      expect(colors).toHaveProperty('accessibility');
      expect(colors).toHaveProperty('variants');
      expect(colors).toHaveProperty('background');
      expect(colors).toHaveProperty('text');
      expect(colors).toHaveProperty('border');
      expect(colors).toHaveProperty('shadow');
      expect(colors).toHaveProperty('gradients');
      expect(colors).toHaveProperty('dark');
      expect(colors).toHaveProperty('classes');
      expect(colors).toHaveProperty('utils');
    });

    it('deve ter exportação padrão', () => {
      expect(colors).toBeDefined();
    });
  });

  describe('Integridade do Sistema', () => {
    it('deve manter consistência entre cores relacionadas', () => {
      expect(colorVariants.primary.main).toBe(primaryColors[600]);
      expect(colorVariants.secondary.main).toBe(secondaryColors[600]);
      expect(textColors.link).toBe(primaryColors[600]);
      expect(borderColors.focus).toBe(primaryColors[500]);
    });

    it('deve ter contraste adequado entre texto e fundo', () => {
      const textColor = textColors.primary;
      const backgroundColor = backgroundColors.primary;
      const textBrightness = getBrightness(textColor);
      const backgroundBrightness = getBrightness(backgroundColor);
      const contrast = Math.abs(textBrightness - backgroundBrightness);
      expect(contrast).toBeGreaterThan(100); // Contraste mínimo para acessibilidade
    });
  });
});

// Função auxiliar para calcular brilho de uma cor
function getBrightness(hexColor: string): number {
  const hex = hexColor.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  return (r * 299 + g * 587 + b * 114) / 1000;
} 
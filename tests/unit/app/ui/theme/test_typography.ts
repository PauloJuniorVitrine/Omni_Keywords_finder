/**
 * test_typography.ts
 * 
 * Testes unitários para o sistema de tipografia padronizado
 * Cobertura completa de todas as funcionalidades
 * 
 * Tracing ID: UI-005-TEST
 * Data/Hora: 2024-12-20 08:00:00 UTC
 * Versão: 1.0
 */

import {
  fontFamilies,
  fontSizes,
  fontWeights,
  lineHeights,
  letterSpacings,
  typographyHierarchy,
  responsiveTypography,
  accessibilityTypography,
  textVariants,
  typographyClasses,
  typographyUtils,
  typography
} from '../../../../app/ui/theme/typography';

describe('Sistema de Tipografia - UI-005', () => {
  describe('Famílias de Fonte', () => {
    it('deve ter famílias de fonte primárias', () => {
      expect(fontFamilies.primary).toHaveProperty('sans');
      expect(fontFamilies.primary).toHaveProperty('serif');
      expect(fontFamilies.primary).toHaveProperty('mono');
    });

    it('deve ter famílias de fonte secundárias', () => {
      expect(fontFamilies.secondary).toHaveProperty('display');
      expect(fontFamilies.secondary).toHaveProperty('body');
      expect(fontFamilies.secondary).toHaveProperty('code');
    });

    it('deve ter fontes sans-serif com fallbacks', () => {
      expect(fontFamilies.primary.sans).toContain('Inter');
      expect(fontFamilies.primary.sans).toContain('-apple-system');
      expect(fontFamilies.primary.sans).toContain('sans-serif');
    });

    it('deve ter fontes serif com fallbacks', () => {
      expect(fontFamilies.primary.serif).toContain('Georgia');
      expect(fontFamilies.primary.serif).toContain('serif');
    });

    it('deve ter fontes monospace com fallbacks', () => {
      expect(fontFamilies.primary.mono).toContain('SF Mono');
      expect(fontFamilies.primary.mono).toContain('monospace');
    });
  });

  describe('Tamanhos de Fonte', () => {
    it('deve ter todos os tamanhos de fonte', () => {
      expect(fontSizes).toHaveProperty('xs');
      expect(fontSizes).toHaveProperty('sm');
      expect(fontSizes).toHaveProperty('base');
      expect(fontSizes).toHaveProperty('lg');
      expect(fontSizes).toHaveProperty('xl');
      expect(fontSizes).toHaveProperty('2xl');
      expect(fontSizes).toHaveProperty('3xl');
      expect(fontSizes).toHaveProperty('4xl');
      expect(fontSizes).toHaveProperty('5xl');
      expect(fontSizes).toHaveProperty('6xl');
      expect(fontSizes).toHaveProperty('7xl');
      expect(fontSizes).toHaveProperty('8xl');
      expect(fontSizes).toHaveProperty('9xl');
    });

    it('deve ter tamanhos em formato rem válido', () => {
      Object.values(fontSizes).forEach(size => {
        expect(size).toMatch(/^\d+(\.\d+)?rem$/);
      });
    });

    it('deve ter tamanho base de 1rem (16px)', () => {
      expect(fontSizes.base).toBe('1rem');
    });

    it('deve ter escala crescente de tamanhos', () => {
      const sizes = [
        fontSizes.xs,
        fontSizes.sm,
        fontSizes.base,
        fontSizes.lg,
        fontSizes.xl,
        fontSizes['2xl'],
        fontSizes['3xl'],
        fontSizes['4xl'],
        fontSizes['5xl'],
        fontSizes['6xl']
      ];

      for (let i = 1; i < sizes.length; i++) {
        const prevSize = parseFloat(sizes[i - 1].replace('rem', ''));
        const currentSize = parseFloat(sizes[i].replace('rem', ''));
        expect(currentSize).toBeGreaterThan(prevSize);
      }
    });
  });

  describe('Pesos de Fonte', () => {
    it('deve ter todos os pesos de fonte', () => {
      expect(fontWeights).toHaveProperty('thin');
      expect(fontWeights).toHaveProperty('extralight');
      expect(fontWeights).toHaveProperty('light');
      expect(fontWeights).toHaveProperty('normal');
      expect(fontWeights).toHaveProperty('medium');
      expect(fontWeights).toHaveProperty('semibold');
      expect(fontWeights).toHaveProperty('bold');
      expect(fontWeights).toHaveProperty('extrabold');
      expect(fontWeights).toHaveProperty('black');
    });

    it('deve ter pesos em valores numéricos válidos', () => {
      Object.values(fontWeights).forEach(weight => {
        expect(typeof weight).toBe('number');
        expect(weight).toBeGreaterThanOrEqual(100);
        expect(weight).toBeLessThanOrEqual(900);
      });
    });

    it('deve ter peso normal de 400', () => {
      expect(fontWeights.normal).toBe(400);
    });

    it('deve ter peso bold de 700', () => {
      expect(fontWeights.bold).toBe(700);
    });
  });

  describe('Alturas de Linha', () => {
    it('deve ter alturas de linha básicas', () => {
      expect(lineHeights).toHaveProperty('none');
      expect(lineHeights).toHaveProperty('tight');
      expect(lineHeights).toHaveProperty('snug');
      expect(lineHeights).toHaveProperty('normal');
      expect(lineHeights).toHaveProperty('relaxed');
      expect(lineHeights).toHaveProperty('loose');
    });

    it('deve ter alturas específicas para tamanhos', () => {
      expect(lineHeights).toHaveProperty('xs');
      expect(lineHeights).toHaveProperty('sm');
      expect(lineHeights).toHaveProperty('base');
      expect(lineHeights).toHaveProperty('lg');
      expect(lineHeights).toHaveProperty('xl');
      expect(lineHeights).toHaveProperty('2xl');
      expect(lineHeights).toHaveProperty('3xl');
      expect(lineHeights).toHaveProperty('4xl');
      expect(lineHeights).toHaveProperty('5xl');
      expect(lineHeights).toHaveProperty('6xl');
    });

    it('deve ter valores numéricos válidos', () => {
      Object.values(lineHeights).forEach(height => {
        expect(typeof height).toBe('number');
        expect(height).toBeGreaterThan(0);
      });
    });

    it('deve ter altura normal de 1.5', () => {
      expect(lineHeights.normal).toBe(1.5);
    });
  });

  describe('Espaçamentos de Letra', () => {
    it('deve ter todos os espaçamentos de letra', () => {
      expect(letterSpacings).toHaveProperty('tighter');
      expect(letterSpacings).toHaveProperty('tight');
      expect(letterSpacings).toHaveProperty('normal');
      expect(letterSpacings).toHaveProperty('wide');
      expect(letterSpacings).toHaveProperty('wider');
      expect(letterSpacings).toHaveProperty('widest');
    });

    it('deve ter espaçamentos em formato em válido', () => {
      Object.values(letterSpacings).forEach(spacing => {
        expect(spacing).toMatch(/^-?\d+(\.\d+)?em$/);
      });
    });

    it('deve ter espaçamento normal de 0em', () => {
      expect(letterSpacings.normal).toBe('0em');
    });
  });

  describe('Hierarquia Tipográfica', () => {
    it('deve ter hierarquia para títulos', () => {
      expect(typographyHierarchy).toHaveProperty('h1');
      expect(typographyHierarchy).toHaveProperty('h2');
      expect(typographyHierarchy).toHaveProperty('h3');
      expect(typographyHierarchy).toHaveProperty('h4');
      expect(typographyHierarchy).toHaveProperty('h5');
      expect(typographyHierarchy).toHaveProperty('h6');
    });

    it('deve ter hierarquia para texto do corpo', () => {
      expect(typographyHierarchy).toHaveProperty('body');
      expect(typographyHierarchy).toHaveProperty('bodyLarge');
      expect(typographyHierarchy).toHaveProperty('bodySmall');
    });

    it('deve ter hierarquia para texto de interface', () => {
      expect(typographyHierarchy).toHaveProperty('caption');
      expect(typographyHierarchy).toHaveProperty('overline');
    });

    it('deve ter hierarquia para código', () => {
      expect(typographyHierarchy).toHaveProperty('code');
      expect(typographyHierarchy).toHaveProperty('codeLarge');
    });

    it('deve ter estrutura completa para cada elemento', () => {
      Object.values(typographyHierarchy).forEach(element => {
        expect(element).toHaveProperty('fontSize');
        expect(element).toHaveProperty('fontWeight');
        expect(element).toHaveProperty('lineHeight');
        expect(element).toHaveProperty('letterSpacing');
        expect(element).toHaveProperty('fontFamily');
      });
    });

    it('deve ter tamanhos decrescentes para títulos', () => {
      const h1Size = parseFloat(typographyHierarchy.h1.fontSize.replace('rem', ''));
      const h2Size = parseFloat(typographyHierarchy.h2.fontSize.replace('rem', ''));
      const h3Size = parseFloat(typographyHierarchy.h3.fontSize.replace('rem', ''));
      
      expect(h1Size).toBeGreaterThan(h2Size);
      expect(h2Size).toBeGreaterThan(h3Size);
    });
  });

  describe('Tipografia Responsiva', () => {
    it('deve ter breakpoints definidos', () => {
      expect(responsiveTypography.breakpoints).toHaveProperty('sm');
      expect(responsiveTypography.breakpoints).toHaveProperty('md');
      expect(responsiveTypography.breakpoints).toHaveProperty('lg');
      expect(responsiveTypography.breakpoints).toHaveProperty('xl');
      expect(responsiveTypography.breakpoints).toHaveProperty('2xl');
    });

    it('deve ter breakpoints em formato px válido', () => {
      Object.values(responsiveTypography.breakpoints).forEach(breakpoint => {
        expect(breakpoint).toMatch(/^\d+px$/);
      });
    });

    it('deve ter escalas responsivas para elementos principais', () => {
      expect(responsiveTypography.scales).toHaveProperty('h1');
      expect(responsiveTypography.scales).toHaveProperty('h2');
      expect(responsiveTypography.scales).toHaveProperty('h3');
      expect(responsiveTypography.scales).toHaveProperty('body');
    });

    it('deve ter escalas crescentes para cada elemento', () => {
      Object.values(responsiveTypography.scales).forEach(scale => {
        expect(scale).toHaveProperty('sm');
        expect(scale).toHaveProperty('md');
        expect(scale).toHaveProperty('lg');
        expect(scale).toHaveProperty('xl');
      });
    });
  });

  describe('Acessibilidade Tipográfica', () => {
    it('deve ter tamanhos mínimos definidos', () => {
      expect(accessibilityTypography.minimumSizes).toHaveProperty('body');
      expect(accessibilityTypography.minimumSizes).toHaveProperty('caption');
      expect(accessibilityTypography.minimumSizes).toHaveProperty('button');
    });

    it('deve ter tamanhos mínimos em px', () => {
      Object.values(accessibilityTypography.minimumSizes).forEach(size => {
        expect(size).toMatch(/^\d+px$/);
      });
    });

    it('deve ter tamanho mínimo de corpo de 16px', () => {
      expect(accessibilityTypography.minimumSizes.body).toBe('16px');
    });

    it('deve ter razões de contraste definidas', () => {
      expect(accessibilityTypography.contrastRatios).toHaveProperty('normal');
      expect(accessibilityTypography.contrastRatios).toHaveProperty('large');
    });

    it('deve ter razão de contraste normal de 4.5', () => {
      expect(accessibilityTypography.contrastRatios.normal).toBe(4.5);
    });

    it('deve ter altura de linha mínima de 1.4', () => {
      expect(accessibilityTypography.minimumLineHeight).toBe(1.4);
    });

    it('deve ter espaçamento mínimo entre parágrafos', () => {
      expect(accessibilityTypography.minimumParagraphSpacing).toBe('1.5em');
    });
  });

  describe('Variantes de Texto', () => {
    it('deve ter variantes de título', () => {
      expect(textVariants).toHaveProperty('title');
      expect(textVariants.title).toHaveProperty('display');
      expect(textVariants.title).toHaveProperty('h1');
      expect(textVariants.title).toHaveProperty('h2');
      expect(textVariants.title).toHaveProperty('h3');
      expect(textVariants.title).toHaveProperty('h4');
      expect(textVariants.title).toHaveProperty('h5');
      expect(textVariants.title).toHaveProperty('h6');
    });

    it('deve ter variantes de corpo', () => {
      expect(textVariants).toHaveProperty('body');
      expect(textVariants.body).toHaveProperty('large');
      expect(textVariants.body).toHaveProperty('normal');
      expect(textVariants.body).toHaveProperty('small');
    });

    it('deve ter variantes de interface', () => {
      expect(textVariants).toHaveProperty('ui');
      expect(textVariants.ui).toHaveProperty('caption');
      expect(textVariants.ui).toHaveProperty('overline');
      expect(textVariants.ui).toHaveProperty('button');
      expect(textVariants.ui).toHaveProperty('label');
    });

    it('deve ter variantes de código', () => {
      expect(textVariants).toHaveProperty('code');
      expect(textVariants.code).toHaveProperty('inline');
      expect(textVariants.code).toHaveProperty('block');
    });
  });

  describe('Classes Utilitárias', () => {
    it('deve ter classes de tamanho', () => {
      expect(typographyClasses).toHaveProperty('text-xs');
      expect(typographyClasses).toHaveProperty('text-sm');
      expect(typographyClasses).toHaveProperty('text-base');
      expect(typographyClasses).toHaveProperty('text-lg');
      expect(typographyClasses).toHaveProperty('text-xl');
      expect(typographyClasses).toHaveProperty('text-2xl');
      expect(typographyClasses).toHaveProperty('text-3xl');
      expect(typographyClasses).toHaveProperty('text-4xl');
      expect(typographyClasses).toHaveProperty('text-5xl');
      expect(typographyClasses).toHaveProperty('text-6xl');
    });

    it('deve ter classes de peso', () => {
      expect(typographyClasses).toHaveProperty('font-thin');
      expect(typographyClasses).toHaveProperty('font-light');
      expect(typographyClasses).toHaveProperty('font-normal');
      expect(typographyClasses).toHaveProperty('font-medium');
      expect(typographyClasses).toHaveProperty('font-semibold');
      expect(typographyClasses).toHaveProperty('font-bold');
      expect(typographyClasses).toHaveProperty('font-extrabold');
      expect(typographyClasses).toHaveProperty('font-black');
    });

    it('deve ter classes de altura de linha', () => {
      expect(typographyClasses).toHaveProperty('leading-none');
      expect(typographyClasses).toHaveProperty('leading-tight');
      expect(typographyClasses).toHaveProperty('leading-snug');
      expect(typographyClasses).toHaveProperty('leading-normal');
      expect(typographyClasses).toHaveProperty('leading-relaxed');
      expect(typographyClasses).toHaveProperty('leading-loose');
    });

    it('deve ter classes de espaçamento de letra', () => {
      expect(typographyClasses).toHaveProperty('tracking-tighter');
      expect(typographyClasses).toHaveProperty('tracking-tight');
      expect(typographyClasses).toHaveProperty('tracking-normal');
      expect(typographyClasses).toHaveProperty('tracking-wide');
      expect(typographyClasses).toHaveProperty('tracking-wider');
      expect(typographyClasses).toHaveProperty('tracking-widest');
    });

    it('deve ter classes de família de fonte', () => {
      expect(typographyClasses).toHaveProperty('font-sans');
      expect(typographyClasses).toHaveProperty('font-serif');
      expect(typographyClasses).toHaveProperty('font-mono');
    });

    it('deve ter classes em formato CSS válido', () => {
      Object.values(typographyClasses).forEach(cssClass => {
        expect(cssClass).toMatch(/^[a-z-]+:\s*[^;]+$/);
      });
    });
  });

  describe('Funções Utilitárias', () => {
    describe('applyStyle', () => {
      it('deve aplicar estilo tipográfico corretamente', () => {
        const style = typographyUtils.applyStyle('h1');
        expect(style).toHaveProperty('fontSize');
        expect(style).toHaveProperty('fontWeight');
        expect(style).toHaveProperty('lineHeight');
        expect(style).toHaveProperty('letterSpacing');
        expect(style).toHaveProperty('fontFamily');
      });

      it('deve aplicar estilo de overline com textTransform', () => {
        const style = typographyUtils.applyStyle('overline');
        expect(style).toHaveProperty('textTransform');
        expect(style.textTransform).toBe('uppercase');
      });
    });

    describe('calculateLineHeight', () => {
      it('deve calcular altura de linha baseada no tamanho da fonte', () => {
        const result = typographyUtils.calculateLineHeight('1rem', 1.5);
        expect(result).toBe('1.5rem');
      });

      it('deve usar razão padrão de 1.5', () => {
        const result = typographyUtils.calculateLineHeight('2rem');
        expect(result).toBe('3rem');
      });
    });

    describe('isAccessibleSize', () => {
      it('deve identificar tamanhos acessíveis corretamente', () => {
        expect(typographyUtils.isAccessibleSize('0.75rem')).toBe(true); // 12px
        expect(typographyUtils.isAccessibleSize('1rem')).toBe(true);    // 16px
        expect(typographyUtils.isAccessibleSize('0.5rem')).toBe(false); // 8px
      });
    });

    describe('generateScale', () => {
      it('deve gerar escala tipográfica', () => {
        const scale = typographyUtils.generateScale(1, 1.25);
        expect(scale).toHaveProperty('xs');
        expect(scale).toHaveProperty('sm');
        expect(scale).toHaveProperty('base');
        expect(scale).toHaveProperty('lg');
        expect(scale).toHaveProperty('xl');
        expect(scale).toHaveProperty('2xl');
        expect(scale).toHaveProperty('3xl');
        expect(scale).toHaveProperty('4xl');
      });

      it('deve usar razão padrão de 1.25', () => {
        const scale = typographyUtils.generateScale(1);
        expect(scale.base).toBe('1rem');
        expect(scale.lg).toBe('1.25rem');
      });
    });

    describe('remToPx', () => {
      it('deve converter rem para px', () => {
        expect(typographyUtils.remToPx('1rem')).toBe('16px');
        expect(typographyUtils.remToPx('1.5rem')).toBe('24px');
        expect(typographyUtils.remToPx('0.75rem')).toBe('12px');
      });
    });

    describe('pxToRem', () => {
      it('deve converter px para rem', () => {
        expect(typographyUtils.pxToRem(16)).toBe('1rem');
        expect(typographyUtils.pxToRem(24)).toBe('1.5rem');
        expect(typographyUtils.pxToRem(12)).toBe('0.75rem');
      });
    });
  });

  describe('Exportação Principal', () => {
    it('deve exportar todas as categorias de tipografia', () => {
      expect(typography).toHaveProperty('families');
      expect(typography).toHaveProperty('sizes');
      expect(typography).toHaveProperty('weights');
      expect(typography).toHaveProperty('lineHeights');
      expect(typography).toHaveProperty('letterSpacings');
      expect(typography).toHaveProperty('hierarchy');
      expect(typography).toHaveProperty('responsive');
      expect(typography).toHaveProperty('accessibility');
      expect(typography).toHaveProperty('variants');
      expect(typography).toHaveProperty('classes');
      expect(typography).toHaveProperty('utils');
    });

    it('deve ter exportação padrão', () => {
      expect(typography).toBeDefined();
    });
  });

  describe('Integridade do Sistema', () => {
    it('deve manter consistência entre hierarquia e tamanhos', () => {
      expect(typographyHierarchy.h1.fontSize).toBe(fontSizes['4xl']);
      expect(typographyHierarchy.h2.fontSize).toBe(fontSizes['3xl']);
      expect(typographyHierarchy.body.fontSize).toBe(fontSizes.base);
    });

    it('deve ter contraste adequado entre elementos', () => {
      const h1Size = parseFloat(typographyHierarchy.h1.fontSize.replace('rem', ''));
      const bodySize = parseFloat(typographyHierarchy.body.fontSize.replace('rem', ''));
      const contrast = h1Size / bodySize;
      expect(contrast).toBeGreaterThan(1.5); // Contraste mínimo entre títulos e corpo
    });

    it('deve ter acessibilidade adequada', () => {
      const bodySize = parseFloat(typographyHierarchy.body.fontSize.replace('rem', ''));
      const bodySizeInPx = bodySize * 16;
      expect(bodySizeInPx).toBeGreaterThanOrEqual(16); // Mínimo 16px para acessibilidade
    });
  });
}); 
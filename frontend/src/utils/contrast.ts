/**
 * Utilitário de Verificação de Contraste - contrast.ts
 * 
 * Fornece funções para verificação de contraste de cores
 * Baseado em WCAG 2.1 AA e cálculo de luminância
 * 
 * Tracing ID: contrast_utils_20250127_001
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

/**
 * Níveis de conformidade WCAG
 */
export type WCAGLevel = 'AA' | 'AAA';

/**
 * Tamanhos de texto para contraste
 */
export type TextSize = 'normal' | 'large';

/**
 * Resultado da verificação de contraste
 */
export interface ContrastResult {
  /** Razão de contraste calculada */
  ratio: number;
  /** Se atende ao nível WCAG especificado */
  passes: boolean;
  /** Nível WCAG testado */
  level: WCAGLevel;
  /** Tamanho do texto testado */
  textSize: TextSize;
  /** Cor do primeiro plano */
  foreground: string;
  /** Cor do fundo */
  background: string;
  /** Mensagem de resultado */
  message: string;
  /** Sugestões de melhoria */
  suggestions: string[];
}

/**
 * Converte cor hex para RGB
 */
export const hexToRgb = (hex: string): [number, number, number] => {
  // Remove # se presente
  const cleanHex = hex.replace('#', '');
  
  // Suporta hex de 3 e 6 dígitos
  const fullHex = cleanHex.length === 3 
    ? cleanHex.split('').map(char => char + char).join('')
    : cleanHex;
  
  const result = /^([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(fullHex);
  
  if (!result) {
    throw new Error(`Cor hex inválida: ${hex}`);
  }
  
  return [
    parseInt(result[1], 16),
    parseInt(result[2], 16),
    parseInt(result[3], 16)
  ];
};

/**
 * Converte cor RGB para HSL
 */
export const rgbToHsl = (r: number, g: number, b: number): [number, number, number] => {
  r /= 255;
  g /= 255;
  b /= 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0;
  let s = 0;
  const l = (max + min) / 2;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

    switch (max) {
      case r:
        h = (g - b) / d + (g < b ? 6 : 0);
        break;
      case g:
        h = (b - r) / d + 2;
        break;
      case b:
        h = (r - g) / d + 4;
        break;
    }

    h /= 6;
  }

  return [h * 360, s * 100, l * 100];
};

/**
 * Converte cor HSL para RGB
 */
export const hslToRgb = (h: number, s: number, l: number): [number, number, number] => {
  h /= 360;
  s /= 100;
  l /= 100;

  const hue2rgb = (p: number, q: number, t: number): number => {
    if (t < 0) t += 1;
    if (t > 1) t -= 1;
    if (t < 1/6) return p + (q - p) * 6 * t;
    if (t < 1/2) return q;
    if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
    return p;
  };

  let r, g, b;

  if (s === 0) {
    r = g = b = l;
  } else {
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    r = hue2rgb(p, q, h + 1/3);
    g = hue2rgb(p, q, h);
    b = hue2rgb(p, q, h - 1/3);
  }

  return [r * 255, g * 255, b * 255].map(Math.round) as [number, number, number];
};

/**
 * Calcula luminância relativa de cor RGB
 */
export const calculateLuminance = (r: number, g: number, b: number): number => {
  // Normaliza valores RGB
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });

  // Calcula luminância relativa
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
};

/**
 * Calcula razão de contraste entre duas cores
 */
export const calculateContrastRatio = (color1: string, color2: string): number => {
  let rgb1: [number, number, number];
  let rgb2: [number, number, number];

  try {
    // Converte cores para RGB
    if (color1.startsWith('#')) {
      rgb1 = hexToRgb(color1);
    } else if (color1.startsWith('rgb')) {
      const match = color1.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      if (!match) throw new Error(`Formato RGB inválido: ${color1}`);
      rgb1 = [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])];
    } else {
      throw new Error(`Formato de cor não suportado: ${color1}`);
    }

    if (color2.startsWith('#')) {
      rgb2 = hexToRgb(color2);
    } else if (color2.startsWith('rgb')) {
      const match = color2.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      if (!match) throw new Error(`Formato RGB inválido: ${color2}`);
      rgb2 = [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])];
    } else {
      throw new Error(`Formato de cor não suportado: ${color2}`);
    }
  } catch (error) {
    throw new Error(`Erro ao processar cores: ${error}`);
  }

  // Calcula luminância das duas cores
  const l1 = calculateLuminance(rgb1[0], rgb1[1], rgb1[2]);
  const l2 = calculateLuminance(rgb2[0], rgb2[1], rgb2[2]);

  // Calcula razão de contraste
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  
  return (lighter + 0.05) / (darker + 0.05);
};

/**
 * Verifica se contraste atende aos padrões WCAG
 */
export const checkContrast = (
  foreground: string,
  background: string,
  level: WCAGLevel = 'AA',
  textSize: TextSize = 'normal'
): ContrastResult => {
  try {
    const ratio = calculateContrastRatio(foreground, background);
    
    // Define limites mínimos baseados no nível WCAG e tamanho do texto
    let minRatio: number;
    
    if (level === 'AA') {
      minRatio = textSize === 'large' ? 3.0 : 4.5;
    } else { // AAA
      minRatio = textSize === 'large' ? 4.5 : 7.0;
    }
    
    const passes = ratio >= minRatio;
    
    // Gera mensagem de resultado
    let message: string;
    let suggestions: string[] = [];
    
    if (passes) {
      message = `Contraste ${ratio.toFixed(2)}:1 atende ao padrão WCAG ${level} para texto ${textSize}`;
    } else {
      message = `Contraste ${ratio.toFixed(2)}:1 não atende ao padrão WCAG ${level} (mínimo ${minRatio}:1) para texto ${textSize}`;
      
      // Sugestões de melhoria
      suggestions = generateContrastSuggestions(foreground, background, minRatio);
    }
    
    return {
      ratio,
      passes,
      level,
      textSize,
      foreground,
      background,
      message,
      suggestions
    };
  } catch (error) {
    return {
      ratio: 0,
      passes: false,
      level,
      textSize,
      foreground,
      background,
      message: `Erro ao verificar contraste: ${error}`,
      suggestions: ['Verifique se as cores estão em formato válido (hex ou rgb)']
    };
  }
};

/**
 * Gera sugestões para melhorar contraste
 */
export const generateContrastSuggestions = (
  foreground: string,
  background: string,
  targetRatio: number
): string[] => {
  const suggestions: string[] = [];
  
  try {
    // Converte cores para HSL para facilitar ajustes
    let fgRgb: [number, number, number];
    let bgRgb: [number, number, number];
    
    if (foreground.startsWith('#')) {
      fgRgb = hexToRgb(foreground);
    } else {
      const match = foreground.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      if (match) {
        fgRgb = [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])];
      } else {
        return ['Não foi possível analisar a cor do texto'];
      }
    }
    
    if (background.startsWith('#')) {
      bgRgb = hexToRgb(background);
    } else {
      const match = background.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      if (match) {
        bgRgb = [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])];
      } else {
        return ['Não foi possível analisar a cor do fundo'];
      }
    }
    
    const fgHsl = rgbToHsl(fgRgb[0], fgRgb[1], fgRgb[2]);
    const bgHsl = rgbToHsl(bgRgb[0], bgRgb[1], bgRgb[2]);
    
    // Sugestões baseadas na luminosidade
    if (fgHsl[2] > bgHsl[2]) {
      // Texto é mais claro que o fundo
      suggestions.push('Escureça a cor do texto para aumentar o contraste');
      suggestions.push('Clareie a cor do fundo para aumentar o contraste');
    } else {
      // Texto é mais escuro que o fundo
      suggestions.push('Clareie a cor do texto para aumentar o contraste');
      suggestions.push('Escureça a cor do fundo para aumentar o contraste');
    }
    
    // Sugestões específicas
    if (fgHsl[1] < 20) {
      suggestions.push('Aumente a saturação da cor do texto');
    }
    
    if (bgHsl[1] > 80) {
      suggestions.push('Reduza a saturação da cor do fundo');
    }
    
    // Sugestões de cores alternativas
    const alternatives = generateAlternativeColors(foreground, background, targetRatio);
    if (alternatives.length > 0) {
      suggestions.push('Cores alternativas sugeridas:');
      suggestions.push(...alternatives.slice(0, 3)); // Limita a 3 sugestões
    }
    
  } catch (error) {
    suggestions.push('Erro ao gerar sugestões de contraste');
  }
  
  return suggestions;
};

/**
 * Gera cores alternativas com melhor contraste
 */
export const generateAlternativeColors = (
  foreground: string,
  background: string,
  targetRatio: number
): string[] => {
  const alternatives: string[] = [];
  
  try {
    let fgRgb: [number, number, number];
    let bgRgb: [number, number, number];
    
    // Converte cores para RGB
    if (foreground.startsWith('#')) {
      fgRgb = hexToRgb(foreground);
    } else {
      const match = foreground.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      if (match) {
        fgRgb = [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])];
      } else {
        return [];
      }
    }
    
    if (background.startsWith('#')) {
      bgRgb = hexToRgb(background);
    } else {
      const match = background.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      if (match) {
        bgRgb = [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])];
      } else {
        return [];
      }
    }
    
    const fgHsl = rgbToHsl(fgRgb[0], fgRgb[1], fgRgb[2]);
    const bgHsl = rgbToHsl(bgRgb[0], bgRgb[1], bgRgb[2]);
    
    // Gera variações de luminosidade
    const variations = [0.1, 0.2, 0.3, 0.4, 0.5];
    
    for (const variation of variations) {
      // Variação do texto
      const newFgL = Math.max(0, Math.min(100, fgHsl[2] + (fgHsl[2] > bgHsl[2] ? -variation * 100 : variation * 100)));
      const newFgRgb = hslToRgb(fgHsl[0], fgHsl[1], newFgL);
      const newFgHex = rgbToHex(newFgRgb[0], newFgRgb[1], newFgRgb[2]);
      
      const ratio = calculateContrastRatio(newFgHex, background);
      if (ratio >= targetRatio) {
        alternatives.push(`Texto: ${newFgHex} (${ratio.toFixed(2)}:1)`);
      }
      
      // Variação do fundo
      const newBgL = Math.max(0, Math.min(100, bgHsl[2] + (bgHsl[2] > fgHsl[2] ? -variation * 100 : variation * 100)));
      const newBgRgb = hslToRgb(bgHsl[0], bgHsl[1], newBgL);
      const newBgHex = rgbToHex(newBgRgb[0], newBgRgb[1], newBgRgb[2]);
      
      const ratio2 = calculateContrastRatio(foreground, newBgHex);
      if (ratio2 >= targetRatio) {
        alternatives.push(`Fundo: ${newBgHex} (${ratio2.toFixed(2)}:1)`);
      }
    }
    
  } catch (error) {
    // Ignora erros na geração de alternativas
  }
  
  return alternatives.slice(0, 6); // Limita a 6 sugestões
};

/**
 * Converte RGB para hex
 */
export const rgbToHex = (r: number, g: number, b: number): string => {
  const toHex = (c: number): string => {
    const hex = Math.round(c).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };
  
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
};

/**
 * Verifica contraste de múltiplas combinações de cores
 */
export const checkMultipleContrasts = (
  colorPairs: Array<{ foreground: string; background: string; label?: string }>,
  level: WCAGLevel = 'AA',
  textSize: TextSize = 'normal'
): ContrastResult[] => {
  return colorPairs.map(pair => ({
    ...checkContrast(pair.foreground, pair.background, level, textSize),
    label: pair.label
  }));
};

/**
 * Obtém estatísticas de contraste de uma página
 */
export const getPageContrastStats = (): {
  totalElements: number;
  passingElements: number;
  failingElements: number;
  averageRatio: number;
  worstRatio: number;
  bestRatio: number;
} => {
  const elements = document.querySelectorAll('*');
  const results: ContrastResult[] = [];
  
  elements.forEach(element => {
    const style = window.getComputedStyle(element);
    const color = style.color;
    const backgroundColor = style.backgroundColor;
    
    if (color && backgroundColor && color !== 'rgba(0, 0, 0, 0)' && backgroundColor !== 'rgba(0, 0, 0, 0)') {
      try {
        const result = checkContrast(color, backgroundColor);
        results.push(result);
      } catch (error) {
        // Ignora elementos com cores inválidas
      }
    }
  });
  
  const passingElements = results.filter(r => r.passes).length;
  const failingElements = results.filter(r => !r.passes).length;
  const ratios = results.map(r => r.ratio);
  
  return {
    totalElements: results.length,
    passingElements,
    failingElements,
    averageRatio: ratios.length > 0 ? ratios.reduce((a, b) => a + b, 0) / ratios.length : 0,
    worstRatio: ratios.length > 0 ? Math.min(...ratios) : 0,
    bestRatio: ratios.length > 0 ? Math.max(...ratios) : 0
  };
};

/**
 * Valida se cor está em formato válido
 */
export const isValidColor = (color: string): boolean => {
  try {
    if (color.startsWith('#')) {
      return /^#[0-9A-F]{3}$|^#[0-9A-F]{6}$/i.test(color);
    } else if (color.startsWith('rgb')) {
      return /^rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(?:,\s*[\d.]+\s*)?\)$/.test(color);
    }
    return false;
  } catch {
    return false;
  }
};

export default {
  hexToRgb,
  rgbToHsl,
  hslToRgb,
  calculateLuminance,
  calculateContrastRatio,
  checkContrast,
  generateContrastSuggestions,
  generateAlternativeColors,
  rgbToHex,
  checkMultipleContrasts,
  getPageContrastStats,
  isValidColor
}; 
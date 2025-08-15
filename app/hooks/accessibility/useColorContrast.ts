import { useState, useEffect, useCallback } from 'react';

export interface ColorRGB {
  r: number;
  g: number;
  b: number;
}

export interface ContrastResult {
  ratio: number;
  passes: boolean;
  level: 'AAA' | 'AA' | 'AA-Large' | 'Fail';
  foregroundColor: string;
  backgroundColor: string;
}

export interface UseColorContrastReturn {
  contrastResult: ContrastResult | null;
  calculateContrast: (foreground: string, background: string) => ContrastResult;
  checkContrast: (foreground: string, background: string, minRatio?: number) => boolean;
  getWCAGLevel: (ratio: number) => 'AAA' | 'AA' | 'AA-Large' | 'Fail';
  suggestColors: (foreground: string, background: string, targetLevel?: 'AAA' | 'AA') => {
    foreground: string;
    background: string;
    ratio: number;
  }[];
  isHighContrastMode: boolean;
  enableHighContrast: () => void;
  disableHighContrast: () => void;
}

export const useColorContrast = (): UseColorContrastReturn => {
  const [contrastResult, setContrastResult] = useState<ContrastResult | null>(null);
  const [isHighContrastMode, setIsHighContrastMode] = useState(false);

  // Convert hex to RGB
  const hexToRgb = useCallback((hex: string): ColorRGB | null => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  }, []);

  // Convert RGB to hex
  const rgbToHex = useCallback((r: number, g: number, b: number): string => {
    return '#' + [r, g, b].map(x => {
      const hex = x.toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    }).join('');
  }, []);

  // Calculate relative luminance
  const getRelativeLuminance = useCallback((r: number, g: number, b: number): number => {
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  }, []);

  // Calculate contrast ratio
  const calculateContrastRatio = useCallback((color1: string, color2: string): number => {
    const rgb1 = hexToRgb(color1);
    const rgb2 = hexToRgb(color2);

    if (!rgb1 || !rgb2) return 0;

    const lum1 = getRelativeLuminance(rgb1.r, rgb1.g, rgb1.b);
    const lum2 = getRelativeLuminance(rgb2.r, rgb2.g, rgb2.b);

    const lighter = Math.max(lum1, lum2);
    const darker = Math.min(lum1, lum2);

    return (lighter + 0.05) / (darker + 0.05);
  }, [hexToRgb, getRelativeLuminance]);

  // Get WCAG level
  const getWCAGLevel = useCallback((ratio: number): 'AAA' | 'AA' | 'AA-Large' | 'Fail' => {
    if (ratio >= 7) return 'AAA';
    if (ratio >= 4.5) return 'AA';
    if (ratio >= 3) return 'AA-Large';
    return 'Fail';
  }, []);

  // Calculate contrast with result
  const calculateContrast = useCallback((foreground: string, background: string): ContrastResult => {
    const ratio = calculateContrastRatio(foreground, background);
    const level = getWCAGLevel(ratio);

    const result: ContrastResult = {
      ratio,
      passes: ratio >= 4.5,
      level,
      foregroundColor: foreground,
      backgroundColor: background
    };

    setContrastResult(result);
    return result;
  }, [calculateContrastRatio, getWCAGLevel]);

  // Check if contrast meets minimum ratio
  const checkContrast = useCallback((foreground: string, background: string, minRatio: number = 4.5): boolean => {
    const ratio = calculateContrastRatio(foreground, background);
    return ratio >= minRatio;
  }, [calculateContrastRatio]);

  // Adjust color brightness
  const adjustColorBrightness = useCallback((color: string, factor: number): string => {
    const rgb = hexToRgb(color);
    if (!rgb) return color;

    const newR = Math.max(0, Math.min(255, Math.round(rgb.r * factor)));
    const newG = Math.max(0, Math.min(255, Math.round(rgb.g * factor)));
    const newB = Math.max(0, Math.min(255, Math.round(rgb.b * factor)));

    return rgbToHex(newR, newG, newB);
  }, [hexToRgb, rgbToHex]);

  // Suggest color combinations
  const suggestColors = useCallback((
    foreground: string, 
    background: string, 
    targetLevel: 'AAA' | 'AA' = 'AA'
  ): { foreground: string; background: string; ratio: number }[] => {
    const minRatio = targetLevel === 'AAA' ? 7 : 4.5;
    const currentRatio = calculateContrastRatio(foreground, background);
    
    if (currentRatio >= minRatio) {
      return [{ foreground, background, ratio: currentRatio }];
    }

    const suggestions: { foreground: string; background: string; ratio: number }[] = [];
    
    // Try adjusting foreground color
    for (let factor = 0.5; factor <= 2; factor += 0.1) {
      const adjustedForeground = adjustColorBrightness(foreground, factor);
      const ratio = calculateContrastRatio(adjustedForeground, background);
      
      if (ratio >= minRatio) {
        suggestions.push({ foreground: adjustedForeground, background, ratio });
      }
    }

    // Try adjusting background color
    for (let factor = 0.5; factor <= 2; factor += 0.1) {
      const adjustedBackground = adjustColorBrightness(background, factor);
      const ratio = calculateContrastRatio(foreground, adjustedBackground);
      
      if (ratio >= minRatio) {
        suggestions.push({ foreground, background: adjustedBackground, ratio });
      }
    }

    // Try common high-contrast combinations
    const highContrastPairs = [
      ['#000000', '#ffffff'],
      ['#ffffff', '#000000'],
      ['#000000', '#ffff00'],
      ['#ffff00', '#000000'],
      ['#ffffff', '#0000ff'],
      ['#0000ff', '#ffffff']
    ];

    highContrastPairs.forEach(([fg, bg]) => {
      const ratio = calculateContrastRatio(fg, bg);
      if (ratio >= minRatio) {
        suggestions.push({ foreground: fg, background: bg, ratio });
      }
    });

    // Sort by ratio (highest first) and remove duplicates
    return suggestions
      .sort((a, b) => b.ratio - a.ratio)
      .filter((suggestion, index, self) => 
        index === self.findIndex(s => 
          s.foreground === suggestion.foreground && s.background === suggestion.background
        )
      )
      .slice(0, 10); // Return top 10 suggestions
  }, [calculateContrastRatio, adjustColorBrightness]);

  // High contrast mode management
  const enableHighContrast = useCallback(() => {
    setIsHighContrastMode(true);
    
    // Apply high contrast styles
    const style = document.createElement('style');
    style.id = 'high-contrast-styles';
    style.textContent = `
      * {
        background-color: #000000 !important;
        color: #ffffff !important;
        border-color: #ffffff !important;
        outline-color: #ffffff !important;
      }
      
      a {
        color: #ffff00 !important;
      }
      
      button, input, select, textarea {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
      }
    `;
    document.head.appendChild(style);
  }, []);

  const disableHighContrast = useCallback(() => {
    setIsHighContrastMode(false);
    
    // Remove high contrast styles
    const style = document.getElementById('high-contrast-styles');
    if (style) {
      style.remove();
    }
  }, []);

  // Check for system high contrast preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      if (e.matches) {
        enableHighContrast();
      } else {
        disableHighContrast();
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    
    // Check initial state
    if (mediaQuery.matches) {
      enableHighContrast();
    }

    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [enableHighContrast, disableHighContrast]);

  return {
    contrastResult,
    calculateContrast,
    checkContrast,
    getWCAGLevel,
    suggestColors,
    isHighContrastMode,
    enableHighContrast,
    disableHighContrast
  };
};

// Specialized contrast hooks
export const useContrastChecker = (foreground: string, background: string) => {
  const { calculateContrast, checkContrast, getWCAGLevel } = useColorContrast();
  const [result, setResult] = useState<ContrastResult | null>(null);

  useEffect(() => {
    const contrastResult = calculateContrast(foreground, background);
    setResult(contrastResult);
  }, [foreground, background, calculateContrast]);

  return {
    result,
    passes: result?.passes ?? false,
    level: result?.level ?? 'Fail',
    ratio: result?.ratio ?? 0,
    checkContrast: (minRatio?: number) => checkContrast(foreground, background, minRatio),
    getWCAGLevel
  };
};

export const useHighContrastMode = () => {
  const { isHighContrastMode, enableHighContrast, disableHighContrast } = useColorContrast();

  return {
    isHighContrastMode,
    enableHighContrast,
    disableHighContrast,
    toggleHighContrast: () => {
      if (isHighContrastMode) {
        disableHighContrast();
      } else {
        enableHighContrast();
      }
    }
  };
}; 
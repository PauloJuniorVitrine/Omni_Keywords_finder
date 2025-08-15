import React, { useState, useEffect, useRef } from 'react';

export interface ColorContrastProps {
  foregroundColor?: string;
  backgroundColor?: string;
  children?: React.ReactNode;
  minContrastRatio?: number;
  onContrastChange?: (ratio: number, passes: boolean) => void;
  className?: string;
}

export interface ContrastResult {
  ratio: number;
  passes: boolean;
  level: 'AAA' | 'AA' | 'AA-Large' | 'Fail';
  foregroundColor: string;
  backgroundColor: string;
}

export const ColorContrast: React.FC<ColorContrastProps> = ({
  foregroundColor = '#000000',
  backgroundColor = '#ffffff',
  children,
  minContrastRatio = 4.5,
  onContrastChange,
  className = ''
}) => {
  const [contrastResult, setContrastResult] = useState<ContrastResult | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Convert color to RGB
  const hexToRgb = (hex: string): { r: number; g: number; b: number } | null => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  };

  // Calculate relative luminance
  const getRelativeLuminance = (r: number, g: number, b: number): number => {
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };

  // Calculate contrast ratio
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

  // Get WCAG level
  const getWCAGLevel = (ratio: number): 'AAA' | 'AA' | 'AA-Large' | 'Fail' => {
    if (ratio >= 7) return 'AAA';
    if (ratio >= 4.5) return 'AA';
    if (ratio >= 3) return 'AA-Large';
    return 'Fail';
  };

  // Calculate contrast
  const calculateContrast = () => {
    const ratio = calculateContrastRatio(foregroundColor, backgroundColor);
    const passes = ratio >= minContrastRatio;
    const level = getWCAGLevel(ratio);

    const result: ContrastResult = {
      ratio,
      passes,
      level,
      foregroundColor,
      backgroundColor
    };

    setContrastResult(result);
    onContrastChange?.(ratio, passes);
  };

  useEffect(() => {
    calculateContrast();
  }, [foregroundColor, backgroundColor, minContrastRatio]);

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'AAA':
        return '#4caf50';
      case 'AA':
        return '#8bc34a';
      case 'AA-Large':
        return '#ff9800';
      case 'Fail':
        return '#f44336';
      default:
        return '#757575';
    }
  };

  return (
    <div
      ref={containerRef}
      className={className}
      style={{
        color: foregroundColor,
        backgroundColor: backgroundColor
      }}
    >
      {children}
      {contrastResult && (
        <div
          className="contrast-indicator"
          style={{
            position: 'absolute',
            top: '4px',
            right: '4px',
            padding: '2px 6px',
            fontSize: '10px',
            borderRadius: '3px',
            backgroundColor: getLevelColor(contrastResult.level),
            color: '#ffffff',
            fontWeight: 'bold'
          }}
          title={`Contrast ratio: ${contrastResult.ratio.toFixed(2)}:1 (${contrastResult.level})`}
        >
          {contrastResult.level}
        </div>
      )}
    </div>
  );
};

// Color Contrast Checker Component
export interface ColorContrastCheckerProps {
  onContrastChange?: (result: ContrastResult) => void;
  className?: string;
}

export const ColorContrastChecker: React.FC<ColorContrastCheckerProps> = ({
  onContrastChange,
  className = ''
}) => {
  const [foregroundColor, setForegroundColor] = useState('#000000');
  const [backgroundColor, setBackgroundColor] = useState('#ffffff');
  const [contrastResult, setContrastResult] = useState<ContrastResult | null>(null);

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

  useEffect(() => {
    const ratio = calculateContrastRatio(foregroundColor, backgroundColor);
    const level = getWCAGLevel(ratio);

    const result: ContrastResult = {
      ratio,
      passes: ratio >= 4.5,
      level,
      foregroundColor,
      backgroundColor
    };

    setContrastResult(result);
    onContrastChange?.(result);
  }, [foregroundColor, backgroundColor, onContrastChange]);

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'AAA':
        return '#4caf50';
      case 'AA':
        return '#8bc34a';
      case 'AA-Large':
        return '#ff9800';
      case 'Fail':
        return '#f44336';
      default:
        return '#757575';
    }
  };

  return (
    <div className={`color-contrast-checker ${className}`}>
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px' }}>
          Foreground Color:
          <input
            type="color"
            value={foregroundColor}
            onChange={(e) => setForegroundColor(e.target.value)}
            style={{ marginLeft: '8px' }}
          />
        </label>
        <label style={{ display: 'block', marginBottom: '8px' }}>
          Background Color:
          <input
            type="color"
            value={backgroundColor}
            onChange={(e) => setBackgroundColor(e.target.value)}
            style={{ marginLeft: '8px' }}
          />
        </label>
      </div>

      <div
        style={{
          padding: '16px',
          marginBottom: '16px',
          borderRadius: '4px',
          color: foregroundColor,
          backgroundColor: backgroundColor,
          border: '1px solid #ccc'
        }}
      >
        <p>Sample text to preview contrast</p>
        <h3>Sample heading</h3>
        <button style={{ color: foregroundColor, backgroundColor: backgroundColor, border: `1px solid ${foregroundColor}`, padding: '8px 16px' }}>
          Sample button
        </button>
      </div>

      {contrastResult && (
        <div style={{ marginBottom: '16px' }}>
          <h4>Contrast Results:</h4>
          <div style={{ marginBottom: '8px' }}>
            <strong>Ratio:</strong> {contrastResult.ratio.toFixed(2)}:1
          </div>
          <div style={{ marginBottom: '8px' }}>
            <strong>WCAG Level:</strong>{' '}
            <span style={{ color: getLevelColor(contrastResult.level) }}>
              {contrastResult.level}
            </span>
          </div>
          <div style={{ marginBottom: '8px' }}>
            <strong>Status:</strong>{' '}
            <span style={{ color: contrastResult.passes ? '#4caf50' : '#f44336' }}>
              {contrastResult.passes ? 'PASS' : 'FAIL'}
            </span>
          </div>
        </div>
      )}

      <div>
        <h4>WCAG Guidelines:</h4>
        <ul style={{ fontSize: '14px' }}>
          <li><strong>AAA:</strong> 7:1 ratio (excellent contrast)</li>
          <li><strong>AA:</strong> 4.5:1 ratio (good contrast)</li>
          <li><strong>AA-Large:</strong> 3:1 ratio (acceptable for large text)</li>
          <li><strong>Fail:</strong> Below 3:1 ratio (poor contrast)</li>
        </ul>
      </div>
    </div>
  );
};

// High Contrast Mode Component
export interface HighContrastModeProps {
  children: React.ReactNode;
  enabled?: boolean;
  className?: string;
}

export const HighContrastMode: React.FC<HighContrastModeProps> = ({
  children,
  enabled = false,
  className = ''
}) => {
  const highContrastStyles = {
    backgroundColor: '#000000',
    color: '#ffffff',
    borderColor: '#ffffff',
    outlineColor: '#ffffff'
  };

  return (
    <div
      className={`high-contrast-mode ${className}`}
      style={enabled ? highContrastStyles : {}}
    >
      {children}
    </div>
  );
}; 
/**
 * Chart Component - Omni Keywords Finder
 * 
 * Componente de gráfico avançado para visualização de dados
 * 
 * Tracing ID: DS-COMP-004
 * Data/Hora: 2025-01-27 15:30:00 UTC
 * Versão: 1.0
 */

import React, { forwardRef, useState, useEffect, useRef } from 'react';
import { primaryColors, secondaryColors, neutralColors, stateColors } from '../../../theme/colors';

// =============================================================================
// TIPOS E INTERFACES
// =============================================================================

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
  metadata?: Record<string, any>;
}

export interface ChartProps {
  data: ChartDataPoint[];
  type?: 'line' | 'bar' | 'pie' | 'area' | 'doughnut';
  title?: string;
  subtitle?: string;
  height?: number;
  width?: number;
  showLegend?: boolean;
  showGrid?: boolean;
  showTooltip?: boolean;
  animate?: boolean;
  responsive?: boolean;
  theme?: 'light' | 'dark';
  className?: string;
  style?: React.CSSProperties;
}

// =============================================================================
// UTILITÁRIOS DE ESTILO
// =============================================================================

const getChartStyles = (theme: string, height: number, width: number): React.CSSProperties => ({
  width: width || '100%',
  height: height || 300,
  backgroundColor: theme === 'dark' ? secondaryColors[900] : neutralColors.white,
  border: `1px solid ${secondaryColors[200]}`,
  borderRadius: '0.5rem',
  padding: '1rem',
  position: 'relative',
  overflow: 'hidden',
});

const getTitleStyles = (theme: string): React.CSSProperties => ({
  fontSize: '1.25rem',
  fontWeight: 600,
  color: theme === 'dark' ? neutralColors.white : secondaryColors[900],
  marginBottom: '0.5rem',
  textAlign: 'center',
});

const getSubtitleStyles = (theme: string): React.CSSProperties => ({
  fontSize: '0.875rem',
  color: theme === 'dark' ? secondaryColors[400] : secondaryColors[600],
  marginBottom: '1rem',
  textAlign: 'center',
});

const getCanvasStyles = (): React.CSSProperties => ({
  width: '100%',
  height: 'calc(100% - 80px)',
  position: 'relative',
});

// =============================================================================
// UTILITÁRIOS DE RENDERIZAÇÃO
// =============================================================================

const drawLineChart = (
  canvas: HTMLCanvasElement,
  data: ChartDataPoint[],
  theme: string,
  showGrid: boolean
) => {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const width = canvas.width;
  const height = canvas.height;
  const padding = 40;

  // Clear canvas
  ctx.clearRect(0, 0, width, height);

  // Set theme colors
  const textColor = theme === 'dark' ? neutralColors.white : secondaryColors[900];
  const gridColor = theme === 'dark' ? secondaryColors[700] : secondaryColors[200];

  // Find min/max values
  const values = data.map(d => d.value);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const range = maxValue - minValue;

  // Draw grid
  if (showGrid) {
    ctx.strokeStyle = gridColor;
    ctx.lineWidth = 1;
    
    // Horizontal grid lines
    for (let i = 0; i <= 5; i++) {
      const y = padding + (height - 2 * padding) * (i / 5);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();
    }
  }

  // Draw line
  ctx.strokeStyle = primaryColors[600];
  ctx.lineWidth = 3;
  ctx.beginPath();

  data.forEach((point, index) => {
    const x = padding + (width - 2 * padding) * (index / (data.length - 1));
    const y = padding + (height - 2 * padding) * (1 - (point.value - minValue) / range);
    
    if (index === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });

  ctx.stroke();

  // Draw points
  data.forEach((point, index) => {
    const x = padding + (width - 2 * padding) * (index / (data.length - 1));
    const y = padding + (height - 2 * padding) * (1 - (point.value - minValue) / range);
    
    ctx.fillStyle = primaryColors[600];
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, 2 * Math.PI);
    ctx.fill();
  });

  // Draw labels
  ctx.fillStyle = textColor;
  ctx.font = '12px Arial';
  ctx.textAlign = 'center';
  
  data.forEach((point, index) => {
    const x = padding + (width - 2 * padding) * (index / (data.length - 1));
    const y = height - padding + 15;
    
    ctx.fillText(point.label, x, y);
  });
};

const drawBarChart = (
  canvas: HTMLCanvasElement,
  data: ChartDataPoint[],
  theme: string,
  showGrid: boolean
) => {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const width = canvas.width;
  const height = canvas.height;
  const padding = 40;

  // Clear canvas
  ctx.clearRect(0, 0, width, height);

  // Set theme colors
  const textColor = theme === 'dark' ? neutralColors.white : secondaryColors[900];
  const gridColor = theme === 'dark' ? secondaryColors[700] : secondaryColors[200];

  // Find max value
  const maxValue = Math.max(...data.map(d => d.value));

  // Calculate bar width
  const barWidth = (width - 2 * padding) / data.length * 0.8;
  const barSpacing = (width - 2 * padding) / data.length * 0.2;

  // Draw grid
  if (showGrid) {
    ctx.strokeStyle = gridColor;
    ctx.lineWidth = 1;
    
    for (let i = 0; i <= 5; i++) {
      const y = padding + (height - 2 * padding) * (i / 5);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();
    }
  }

  // Draw bars
  data.forEach((point, index) => {
    const x = padding + (width - 2 * padding) * (index / data.length) + barSpacing / 2;
    const barHeight = ((height - 2 * padding) * point.value) / maxValue;
    const y = height - padding - barHeight;

    ctx.fillStyle = point.color || primaryColors[600];
    ctx.fillRect(x, y, barWidth, barHeight);
  });

  // Draw labels
  ctx.fillStyle = textColor;
  ctx.font = '12px Arial';
  ctx.textAlign = 'center';
  
  data.forEach((point, index) => {
    const x = padding + (width - 2 * padding) * (index / data.length) + barSpacing / 2 + barWidth / 2;
    const y = height - padding + 15;
    
    ctx.fillText(point.label, x, y);
  });
};

// =============================================================================
// COMPONENTE PRINCIPAL
// =============================================================================

export const Chart = forwardRef<HTMLDivElement, ChartProps>(
  (
    {
      data,
      type = 'line',
      title,
      subtitle,
      height = 300,
      width,
      showLegend = true,
      showGrid = true,
      showTooltip = true,
      animate = true,
      responsive = true,
      theme = 'light',
      className,
      style,
      ...props
    },
    ref
  ) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [tooltip, setTooltip] = useState<{ show: boolean; x: number; y: number; data: ChartDataPoint | null }>({
      show: false,
      x: 0,
      y: 0,
      data: null,
    });

    const chartStyles = getChartStyles(theme, height, width);
    const titleStyles = getTitleStyles(theme);
    const subtitleStyles = getSubtitleStyles(theme);
    const canvasStyles = getCanvasStyles();

    useEffect(() => {
      const canvas = canvasRef.current;
      if (!canvas || !data.length) return;

             // Set canvas size
       const rect = canvas.getBoundingClientRect();
       canvas.width = (rect.width || 0) * window.devicePixelRatio;
       canvas.height = (rect.height || 0) * window.devicePixelRatio;
             canvas.style.width = (rect.width || 0) + 'px';
       canvas.style.height = (rect.height || 0) + 'px';

      // Scale context
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      }

      // Draw chart based on type
      switch (type) {
        case 'line':
          drawLineChart(canvas, data, theme, showGrid);
          break;
        case 'bar':
          drawBarChart(canvas, data, theme, showGrid);
          break;
        default:
          drawLineChart(canvas, data, theme, showGrid);
      }
    }, [data, type, theme, showGrid, height, width]);

    const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
      if (!showTooltip) return;

      const canvas = canvasRef.current;
      if (!canvas) return;

      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      // Find closest data point
      const padding = 40;
      const chartWidth = (rect.width || 0) - 2 * padding;
      const index = Math.round(((x - padding) / chartWidth) * (data.length - 1));
      
      if (index >= 0 && index < data.length) {
        setTooltip({
          show: true,
          x: e.clientX,
          y: e.clientY,
          data: data[index],
        });
      } else {
        setTooltip({ show: false, x: 0, y: 0, data: null });
      }
    };

    const handleMouseLeave = () => {
      setTooltip({ show: false, x: 0, y: 0, data: null });
    };

    return (
      <div
        ref={ref}
        style={{ ...chartStyles, ...style }}
        className={className}
        {...props}
      >
        {title && <div style={titleStyles}>{title}</div>}
        {subtitle && <div style={subtitleStyles}>{subtitle}</div>}
        
        <div style={canvasStyles}>
          <canvas
            ref={canvasRef}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            style={{
              width: '100%',
              height: '100%',
              cursor: showTooltip ? 'pointer' : 'default',
            }}
          />
        </div>

        {showLegend && data.length > 0 && (
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '1rem',
            marginTop: '1rem',
            flexWrap: 'wrap',
          }}>
            {data.map((point, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  fontSize: '0.875rem',
                  color: theme === 'dark' ? neutralColors.white : secondaryColors[700],
                }}
              >
                <div
                  style={{
                    width: '12px',
                    height: '12px',
                    backgroundColor: point.color || primaryColors[600],
                    borderRadius: '2px',
                  }}
                />
                <span>{point.label}</span>
              </div>
            ))}
          </div>
        )}

        {tooltip.show && tooltip.data && (
          <div
            style={{
              position: 'fixed',
              left: tooltip.x + 10,
              top: tooltip.y - 10,
              backgroundColor: theme === 'dark' ? secondaryColors[800] : neutralColors.white,
              border: `1px solid ${secondaryColors[200]}`,
              borderRadius: '0.375rem',
              padding: '0.5rem',
              fontSize: '0.875rem',
              color: theme === 'dark' ? neutralColors.white : secondaryColors[900],
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              zIndex: 1000,
              pointerEvents: 'none',
            }}
          >
            <div style={{ fontWeight: 600 }}>{tooltip.data.label}</div>
            <div>Valor: {tooltip.data.value}</div>
          </div>
        )}
      </div>
    );
  }
);

Chart.displayName = 'Chart';

export default Chart; 
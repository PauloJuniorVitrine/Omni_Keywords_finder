import React, { useState, useEffect, useRef } from 'react';
import { Card, CardHeader, CardBody, CardTitle } from '../../../ui/design-system/components/Card';
import { Button } from '../../../ui/design-system/components/Button';
import { Loading } from '../../../ui/design-system/components/Loading';

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
  metadata?: Record<string, any>;
}

export interface ChartDataset {
  label: string;
  data: ChartDataPoint[];
  color?: string;
  backgroundColor?: string;
  borderColor?: string;
  fill?: boolean;
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'doughnut' | 'area' | 'scatter';
  responsive?: boolean;
  maintainAspectRatio?: boolean;
  animation?: boolean;
  legend?: boolean;
  tooltips?: boolean;
  grid?: boolean;
  axes?: {
    x?: boolean;
    y?: boolean;
  };
}

export interface Chart_v2Props {
  title?: string;
  subtitle?: string;
  data: ChartDataset | ChartDataset[];
  config?: ChartConfig;
  height?: string;
  loading?: boolean;
  error?: string;
  onDataPointClick?: (dataPoint: ChartDataPoint, dataset?: ChartDataset) => void;
  onExport?: () => void;
  className?: string;
}

// Simple Chart Components (Placeholder implementations)
const LineChart: React.FC<{ data: ChartDataset; config: ChartConfig; height: string }> = ({
  data,
  config,
  height
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Simple line chart implementation
    const width = canvas.width;
    const height = canvas.height;
    const padding = 40;

    const maxValue = Math.max(...data.data.map(d => d.value));
    const minValue = Math.min(...data.data.map(d => d.value));
    const range = maxValue - minValue;

    ctx.strokeStyle = data.color || '#3b82f6';
    ctx.lineWidth = 2;
    ctx.beginPath();

    data.data.forEach((point, index) => {
      const x = padding + (index / (data.data.length - 1)) * (width - 2 * padding);
      const y = height - padding - ((point.value - minValue) / range) * (height - 2 * padding);

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // Draw points
    ctx.fillStyle = data.color || '#3b82f6';
    data.data.forEach((point, index) => {
      const x = padding + (index / (data.data.length - 1)) * (width - 2 * padding);
      const y = height - padding - ((point.value - minValue) / range) * (height - 2 * padding);

      ctx.beginPath();
      ctx.arc(x, y, 4, 0, 2 * Math.PI);
      ctx.fill();
    });
  }, [data, config, height]);

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={parseInt(height)}
      className="w-full h-full"
    />
  );
};

const BarChart: React.FC<{ data: ChartDataset; config: ChartConfig; height: string }> = ({
  data,
  config,
  height
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Simple bar chart implementation
    const width = canvas.width;
    const height = canvas.height;
    const padding = 40;

    const maxValue = Math.max(...data.data.map(d => d.value));
    const barWidth = (width - 2 * padding) / data.data.length * 0.8;
    const barSpacing = (width - 2 * padding) / data.data.length * 0.2;

    ctx.fillStyle = data.color || '#3b82f6';

    data.data.forEach((point, index) => {
      const x = padding + index * (barWidth + barSpacing);
      const barHeight = (point.value / maxValue) * (height - 2 * padding);
      const y = height - padding - barHeight;

      ctx.fillRect(x, y, barWidth, barHeight);
    });
  }, [data, config, height]);

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={parseInt(height)}
      className="w-full h-full"
    />
  );
};

const PieChart: React.FC<{ data: ChartDataset; config: ChartConfig; height: string }> = ({
  data,
  config,
  height
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Simple pie chart implementation
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 40;

    const total = data.data.reduce((sum, point) => sum + point.value, 0);
    let currentAngle = 0;

    data.data.forEach((point, index) => {
      const sliceAngle = (point.value / total) * 2 * Math.PI;
      const color = point.color || `hsl(${(index * 360) / data.data.length}, 70%, 50%)`;

      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
      ctx.closePath();
      ctx.fillStyle = color;
      ctx.fill();

      currentAngle += sliceAngle;
    });
  }, [data, config, height]);

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={parseInt(height)}
      className="w-full h-full"
    />
  );
};

const AreaChart: React.FC<{ data: ChartDataset; config: ChartConfig; height: string }> = ({
  data,
  config,
  height
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Simple area chart implementation
    const width = canvas.width;
    const height = canvas.height;
    const padding = 40;

    const maxValue = Math.max(...data.data.map(d => d.value));
    const minValue = Math.min(...data.data.map(d => d.value));
    const range = maxValue - minValue;

    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, data.backgroundColor || 'rgba(59, 130, 246, 0.3)');
    gradient.addColorStop(1, data.backgroundColor || 'rgba(59, 130, 246, 0.1)');

    ctx.fillStyle = gradient;
    ctx.beginPath();

    data.data.forEach((point, index) => {
      const x = padding + (index / (data.data.length - 1)) * (width - 2 * padding);
      const y = height - padding - ((point.value - minValue) / range) * (height - 2 * padding);

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    // Close the path to create area
    ctx.lineTo(width - padding, height - padding);
    ctx.lineTo(padding, height - padding);
    ctx.closePath();
    ctx.fill();

    // Draw line
    ctx.strokeStyle = data.borderColor || data.color || '#3b82f6';
    ctx.lineWidth = 2;
    ctx.beginPath();

    data.data.forEach((point, index) => {
      const x = padding + (index / (data.data.length - 1)) * (width - 2 * padding);
      const y = height - padding - ((point.value - minValue) / range) * (height - 2 * padding);

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();
  }, [data, config, height]);

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={parseInt(height)}
      className="w-full h-full"
    />
  );
};

const renderChart = (
  type: string,
  data: ChartDataset | ChartDataset[],
  config: ChartConfig,
  height: string
) => {
  const dataset = Array.isArray(data) ? data[0] : data;

  switch (type) {
    case 'line':
      return <LineChart data={dataset} config={config} height={height} />;
    case 'bar':
      return <BarChart data={dataset} config={config} height={height} />;
    case 'pie':
    case 'doughnut':
      return <PieChart data={dataset} config={config} height={height} />;
    case 'area':
      return <AreaChart data={dataset} config={config} height={height} />;
    default:
      return <LineChart data={dataset} config={config} height={height} />;
  }
};

export const Chart_v2: React.FC<Chart_v2Props> = ({
  title,
  subtitle,
  data,
  config = { type: 'line' },
  height = '400px',
  loading = false,
  error,
  onDataPointClick,
  onExport,
  className = ''
}) => {
  const [chartType, setChartType] = useState(config.type);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading variant="spinner" size="lg" text="Loading chart..." />
      </div>
    );
  }

  if (error) {
    return (
      <Card variant="outlined" className="text-center py-12">
        <CardBody>
          <div className="text-error-500 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-secondary-900 mb-2">Chart Error</h3>
          <p className="text-secondary-600">{error}</p>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card className={className}>
      {(title || subtitle || onExport) && (
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              {title && <CardTitle>{title}</CardTitle>}
              {subtitle && <p className="text-sm text-secondary-600 mt-1">{subtitle}</p>}
            </div>
            
            <div className="flex items-center space-x-2">
              <select
                value={chartType}
                onChange={(e) => setChartType(e.target.value)}
                className="px-3 py-1 border border-secondary-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="line">Line</option>
                <option value="bar">Bar</option>
                <option value="pie">Pie</option>
                <option value="doughnut">Doughnut</option>
                <option value="area">Area</option>
              </select>
              
              {onExport && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onExport}
                  leftIcon={
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  }
                >
                  Export
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
      )}
      
      <CardBody>
        <div style={{ height }} className="relative">
          {renderChart(chartType, data, { ...config, type: chartType }, height)}
        </div>
      </CardBody>
    </Card>
  );
};

// Chart Hook
export const useChart = () => {
  const [chartData, setChartData] = useState<ChartDataset[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateChartData = (data: ChartDataset[]) => {
    setChartData(data);
  };

  const addDataPoint = (datasetId: string, dataPoint: ChartDataPoint) => {
    setChartData(prev => prev.map(dataset => 
      dataset.label === datasetId
        ? { ...dataset, data: [...dataset.data, dataPoint] }
        : dataset
    ));
  };

  const removeDataPoint = (datasetId: string, label: string) => {
    setChartData(prev => prev.map(dataset => 
      dataset.label === datasetId
        ? { ...dataset, data: dataset.data.filter(point => point.label !== label) }
        : dataset
    ));
  };

  return {
    chartData,
    loading,
    error,
    updateChartData,
    addDataPoint,
    removeDataPoint,
    setLoading,
    setError
  };
}; 
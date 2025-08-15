import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardBody, CardTitle, CardSubtitle } from '../../../ui/design-system/components/Card';
import { Button } from '../../../ui/design-system/components/Button';
import { Loading } from '../../../ui/design-system/components/Loading';
import { Alert } from '../../../ui/design-system/components/Alert';

export interface DashboardMetric {
  id: string;
  title: string;
  value: string | number;
  change?: number;
  changeType?: 'increase' | 'decrease' | 'neutral';
  icon?: React.ReactNode;
  color?: string;
}

export interface DashboardWidget {
  id: string;
  title: string;
  type: 'metric' | 'chart' | 'table' | 'list' | 'custom';
  size: 'small' | 'medium' | 'large' | 'full';
  data?: any;
  config?: any;
  component?: React.ComponentType<any>;
}

export interface DashboardLayout {
  id: string;
  name: string;
  columns: number;
  widgets: Array<{
    widgetId: string;
    position: { x: number; y: number };
    size: { width: number; height: number };
  }>;
}

export interface Dashboard_v2Props {
  title?: string;
  subtitle?: string;
  metrics?: DashboardMetric[];
  widgets?: DashboardWidget[];
  layouts?: DashboardLayout[];
  currentLayout?: string;
  onLayoutChange?: (layoutId: string) => void;
  onWidgetUpdate?: (widgetId: string, data: any) => void;
  loading?: boolean;
  error?: string;
  className?: string;
}

const getGridCols = (columns: number): string => {
  const gridMap = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
    6: 'grid-cols-2 md:grid-cols-3 lg:grid-cols-6'
  };
  return gridMap[columns as keyof typeof gridMap] || 'grid-cols-1';
};

const getWidgetSize = (size: string): string => {
  const sizeMap = {
    small: 'col-span-1 row-span-1',
    medium: 'col-span-1 md:col-span-2 row-span-1',
    large: 'col-span-1 md:col-span-2 lg:col-span-3 row-span-1',
    full: 'col-span-full row-span-1'
  };
  return sizeMap[size as keyof typeof sizeMap] || 'col-span-1 row-span-1';
};

const MetricCard: React.FC<{ metric: DashboardMetric }> = ({ metric }) => {
  const getChangeColor = (type?: string) => {
    switch (type) {
      case 'increase':
        return 'text-success-600';
      case 'decrease':
        return 'text-error-600';
      default:
        return 'text-secondary-600';
    }
  };

  const getChangeIcon = (type?: string) => {
    switch (type) {
      case 'increase':
        return '↗';
      case 'decrease':
        return '↘';
      default:
        return '→';
    }
  };

  return (
    <Card variant="elevated" className="h-full">
      <CardBody>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-secondary-600">{metric.title}</p>
            <p className="text-2xl font-bold text-secondary-900 mt-1">{metric.value}</p>
            {metric.change !== undefined && (
              <div className={`flex items-center mt-2 text-sm ${getChangeColor(metric.changeType)}`}>
                <span className="mr-1">{getChangeIcon(metric.changeType)}</span>
                <span>{Math.abs(metric.change)}%</span>
                <span className="ml-1">vs last period</span>
              </div>
            )}
          </div>
          {metric.icon && (
            <div className="flex-shrink-0 ml-4">
              {metric.icon}
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
};

const WidgetRenderer: React.FC<{ widget: DashboardWidget }> = ({ widget }) => {
  const renderWidgetContent = () => {
    switch (widget.type) {
      case 'metric':
        return (
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-2">{widget.title}</h3>
            <div className="text-3xl font-bold text-primary-600">
              {widget.data?.value || '0'}
            </div>
          </div>
        );
      
      case 'chart':
        return (
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">{widget.title}</h3>
            <div className="h-48 bg-secondary-100 rounded-lg flex items-center justify-center">
              <p className="text-secondary-500">Chart Component</p>
            </div>
          </div>
        );
      
      case 'table':
        return (
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">{widget.title}</h3>
            <div className="bg-secondary-100 rounded-lg p-4">
              <p className="text-secondary-500">Table Component</p>
            </div>
          </div>
        );
      
      case 'list':
        return (
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-4">{widget.title}</h3>
            <div className="space-y-2">
              {widget.data?.items?.map((item: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-2 bg-secondary-50 rounded">
                  <span>{item.label}</span>
                  <span className="font-medium">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        );
      
      case 'custom':
        return widget.component ? <widget.component {...widget.data} /> : null;
      
      default:
        return (
          <div className="p-4">
            <h3 className="text-lg font-semibold">{widget.title}</h3>
            <p className="text-secondary-500 mt-2">Widget content</p>
          </div>
        );
    }
  };

  return (
    <Card variant="elevated" className="h-full">
      {renderWidgetContent()}
    </Card>
  );
};

export const Dashboard_v2: React.FC<Dashboard_v2Props> = ({
  title = 'Dashboard',
  subtitle,
  metrics = [],
  widgets = [],
  layouts = [],
  currentLayout,
  onLayoutChange,
  onWidgetUpdate,
  loading = false,
  error,
  className = ''
}) => {
  const [selectedLayout, setSelectedLayout] = useState(currentLayout || layouts[0]?.id);
  const [isEditing, setIsEditing] = useState(false);

  const currentLayoutData = layouts.find(layout => layout.id === selectedLayout);

  useEffect(() => {
    if (currentLayout && currentLayout !== selectedLayout) {
      setSelectedLayout(currentLayout);
    }
  }, [currentLayout]);

  const handleLayoutChange = (layoutId: string) => {
    setSelectedLayout(layoutId);
    onLayoutChange?.(layoutId);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading variant="spinner" size="lg" text="Loading dashboard..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert variant="error" title="Error Loading Dashboard">
          {error}
        </Alert>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">{title}</h1>
          {subtitle && (
            <p className="text-secondary-600 mt-1">{subtitle}</p>
          )}
        </div>
        
        <div className="flex items-center space-x-3">
          {layouts.length > 1 && (
            <select
              value={selectedLayout}
              onChange={(e) => handleLayoutChange(e.target.value)}
              className="px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {layouts.map(layout => (
                <option key={layout.id} value={layout.id}>
                  {layout.name}
                </option>
              ))}
            </select>
          )}
          
          <Button
            variant={isEditing ? 'primary' : 'outline'}
            onClick={() => setIsEditing(!isEditing)}
          >
            {isEditing ? 'Save Layout' : 'Edit Layout'}
          </Button>
        </div>
      </div>

      {/* Metrics Grid */}
      {metrics.length > 0 && (
        <div className={`grid gap-6 ${getGridCols(Math.min(metrics.length, 4))}`}>
          {metrics.map(metric => (
            <MetricCard key={metric.id} metric={metric} />
          ))}
        </div>
      )}

      {/* Widgets Grid */}
      {widgets.length > 0 && currentLayoutData && (
        <div className={`grid gap-6 ${getGridCols(currentLayoutData.columns)}`}>
          {currentLayoutData.widgets.map(({ widgetId, position, size }) => {
            const widget = widgets.find(w => w.id === widgetId);
            if (!widget) return null;

            return (
              <div
                key={widgetId}
                className={`${getWidgetSize(widget.size)} ${
                  isEditing ? 'border-2 border-dashed border-primary-300 rounded-lg p-2' : ''
                }`}
                style={{
                  gridColumn: `span ${size.width}`,
                  gridRow: `span ${size.height}`
                }}
              >
                <WidgetRenderer widget={widget} />
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {widgets.length === 0 && metrics.length === 0 && (
        <Card variant="outlined" className="text-center py-12">
          <CardBody>
            <div className="text-secondary-400 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-secondary-900 mb-2">No Dashboard Content</h3>
            <p className="text-secondary-600 mb-4">
              Add metrics and widgets to start building your dashboard.
            </p>
            <Button variant="primary">
              Add Widget
            </Button>
          </CardBody>
        </Card>
      )}
    </div>
  );
};

// Dashboard Hook
export const useDashboard = () => {
  const [metrics, setMetrics] = useState<DashboardMetric[]>([]);
  const [widgets, setWidgets] = useState<DashboardWidget[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addMetric = (metric: DashboardMetric) => {
    setMetrics(prev => [...prev, metric]);
  };

  const updateMetric = (id: string, updates: Partial<DashboardMetric>) => {
    setMetrics(prev => prev.map(metric => 
      metric.id === id ? { ...metric, ...updates } : metric
    ));
  };

  const removeMetric = (id: string) => {
    setMetrics(prev => prev.filter(metric => metric.id !== id));
  };

  const addWidget = (widget: DashboardWidget) => {
    setWidgets(prev => [...prev, widget]);
  };

  const updateWidget = (id: string, updates: Partial<DashboardWidget>) => {
    setWidgets(prev => prev.map(widget => 
      widget.id === id ? { ...widget, ...updates } : widget
    ));
  };

  const removeWidget = (id: string) => {
    setWidgets(prev => prev.filter(widget => widget.id !== id));
  };

  return {
    metrics,
    widgets,
    loading,
    error,
    addMetric,
    updateMetric,
    removeMetric,
    addWidget,
    updateWidget,
    removeWidget,
    setLoading,
    setError
  };
}; 
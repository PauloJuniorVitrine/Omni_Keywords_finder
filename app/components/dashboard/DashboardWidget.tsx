/**
 * DashboardWidget - Widget de métricas para o dashboard principal
 * 
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 2.1.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
  Grid
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Refresh,
  MoreVert,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

interface MetricData {
  value: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
  unit: string;
  color: string;
}

interface ChartData {
  date: string;
  value: number;
}

interface DashboardWidgetProps {
  title: string;
  metric: MetricData;
  chartData?: ChartData[];
  isLoading?: boolean;
  onRefresh?: () => void;
  onConfigure?: () => void;
  showChart?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const DashboardWidget: React.FC<DashboardWidgetProps> = ({
  title,
  metric,
  chartData = [],
  isLoading = false,
  onRefresh,
  onConfigure,
  showChart = true,
  size = 'medium'
}) => {
  const [isChartVisible, setIsChartVisible] = useState(showChart);
  const [isExpanded, setIsExpanded] = useState(false);

  const trendIcon = useMemo(() => {
    switch (metric.trend) {
      case 'up':
        return <TrendingUp sx={{ color: 'success.main' }} />;
      case 'down':
        return <TrendingDown sx={{ color: 'error.main' }} />;
      default:
        return null;
    }
  }, [metric.trend]);

  const changeColor = useMemo(() => {
    switch (metric.trend) {
      case 'up':
        return 'success.main';
      case 'down':
        return 'error.main';
      default:
        return 'text.secondary';
    }
  }, [metric.trend]);

  const formatValue = (value: number): string => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }
    return value.toString();
  };

  const cardHeight = size === 'large' ? 400 : size === 'medium' ? 300 : 200;

  return (
    <Card 
      sx={{ 
        height: cardHeight,
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        '&:hover': {
          boxShadow: 3,
          transform: 'translateY(-2px)',
          transition: 'all 0.3s ease'
        }
      }}
    >
      <CardContent sx={{ flexGrow: 1, p: 2 }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h3" color="text.primary">
            {title}
          </Typography>
          <Box display="flex" gap={1}>
            {showChart && (
              <Tooltip title={isChartVisible ? "Ocultar gráfico" : "Mostrar gráfico"}>
                <IconButton 
                  size="small" 
                  onClick={() => setIsChartVisible(!isChartVisible)}
                >
                  {isChartVisible ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </Tooltip>
            )}
            {onRefresh && (
              <Tooltip title="Atualizar dados">
                <IconButton size="small" onClick={onRefresh} disabled={isLoading}>
                  <Refresh />
                </IconButton>
              </Tooltip>
            )}
            {onConfigure && (
              <Tooltip title="Configurar widget">
                <IconButton size="small" onClick={onConfigure}>
                  <MoreVert />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Box>

        {/* Loading State */}
        {isLoading && (
          <Box position="absolute" top={0} left={0} right={0}>
            <LinearProgress />
          </Box>
        )}

        {/* Metric Display */}
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Typography variant="h4" component="div" color={metric.color}>
            {formatValue(metric.value)}
            <Typography component="span" variant="body2" color="text.secondary">
              {metric.unit}
            </Typography>
          </Typography>
          {trendIcon}
        </Box>

        {/* Change Indicator */}
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Chip
            label={`${metric.change > 0 ? '+' : ''}${metric.change}%`}
            size="small"
            color={metric.trend === 'up' ? 'success' : metric.trend === 'down' ? 'error' : 'default'}
            variant="outlined"
          />
          <Typography variant="caption" color={changeColor}>
            vs período anterior
          </Typography>
        </Box>

        {/* Chart */}
        {isChartVisible && chartData.length > 0 && (
          <Box sx={{ height: size === 'large' ? 200 : 120, mt: 'auto' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  stroke="#666"
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  stroke="#666"
                />
                <RechartsTooltip 
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #ccc',
                    borderRadius: 4
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke={metric.color}
                  strokeWidth={2}
                  dot={{ fill: metric.color, strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: metric.color, strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default DashboardWidget; 
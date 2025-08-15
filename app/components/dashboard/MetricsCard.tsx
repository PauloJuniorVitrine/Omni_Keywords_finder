/**
 * MetricsCard.tsx
 * 
 * Componente para exibir métricas individuais com status e tendências
 * 
 * Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 5
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-19
 */

import React from 'react';
import { Card, Statistic, Tooltip } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, MinusOutlined } from '@ant-design/icons';

interface MetricsCardProps {
  title: string;
  value: number;
  unit: string;
  trend?: number;
  status: 'success' | 'warning' | 'error' | 'info';
  icon?: React.ReactNode;
  precision?: number;
  showTrend?: boolean;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  unit,
  trend = 0,
  status,
  icon,
  precision = 2,
  showTrend = true
}) => {
  // Calcular variação percentual
  const calculateTrend = () => {
    if (!showTrend || trend === 0) return null;
    
    const variation = ((value - trend) / trend) * 100;
    return {
      value: Math.abs(variation),
      direction: variation > 0 ? 'up' : 'down',
      color: variation > 0 ? '#52c41a' : '#ff4d4f'
    };
  };

  const trendData = calculateTrend();

  // Configurar cores baseadas no status
  const getStatusColor = () => {
    switch (status) {
      case 'success': return '#52c41a';
      case 'warning': return '#faad14';
      case 'error': return '#ff4d4f';
      case 'info': return '#1890ff';
      default: return '#666';
    }
  };

  return (
    <Card 
      size="small" 
      style={{ 
        borderLeft: `4px solid ${getStatusColor()}`,
        height: '100%'
      }}
    >
      <Statistic
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {icon}
            <span>{title}</span>
          </div>
        }
        value={value}
        precision={precision}
        suffix={unit}
        valueStyle={{ 
          color: getStatusColor(),
          fontSize: '24px',
          fontWeight: 'bold'
        }}
      />
      
      {trendData && (
        <Tooltip title={`Variação: ${trendData.direction === 'up' ? '+' : '-'}${trendData.value.toFixed(1)}%`}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 4, 
            marginTop: 8,
            fontSize: '12px',
            color: trendData.color
          }}>
            {trendData.direction === 'up' ? (
              <ArrowUpOutlined />
            ) : (
              <ArrowDownOutlined />
            )}
            <span>{trendData.value.toFixed(1)}%</span>
          </div>
        </Tooltip>
      )}
    </Card>
  );
};

export default MetricsCard; 
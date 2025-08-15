/**
 * AlertPanel.tsx
 * 
 * Componente para exibir alertas de performance em tempo real
 * 
 * Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 5
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-19
 */

import React from 'react';
import { Alert, Button, Space, Badge } from 'antd';
import { CloseOutlined, ExclamationCircleOutlined, WarningOutlined, InfoCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';

interface AlertData {
  id: string;
  type: 'warning' | 'error' | 'info' | 'success';
  message: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

interface AlertPanelProps {
  alerts: AlertData[];
  onDismiss: (id: string) => void;
  maxAlerts?: number;
  showSeverity?: boolean;
}

export const AlertPanel: React.FC<AlertPanelProps> = ({
  alerts,
  onDismiss,
  maxAlerts = 5,
  showSeverity = true
}) => {
  // Filtrar alertas por severidade e limitar quantidade
  const sortedAlerts = alerts
    .sort((a, b) => {
      const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
      return severityOrder[b.severity] - severityOrder[a.severity];
    })
    .slice(0, maxAlerts);

  const getAlertIcon = (type: AlertData['type']) => {
    switch (type) {
      case 'error': return <ExclamationCircleOutlined />;
      case 'warning': return <WarningOutlined />;
      case 'info': return <InfoCircleOutlined />;
      case 'success': return <CheckCircleOutlined />;
      default: return <InfoCircleOutlined />;
    }
  };

  const getSeverityColor = (severity: AlertData['severity']) => {
    switch (severity) {
      case 'critical': return '#ff4d4f';
      case 'high': return '#ff7875';
      case 'medium': return '#faad14';
      case 'low': return '#52c41a';
      default: return '#666';
    }
  };

  if (sortedAlerts.length === 0) {
    return null;
  }

  return (
    <div style={{ marginBottom: 16 }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        {sortedAlerts.map((alert) => (
          <Alert
            key={alert.id}
            message={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  {showSeverity && (
                    <Badge 
                      color={getSeverityColor(alert.severity)} 
                      text={alert.severity.toUpperCase()}
                      style={{ fontSize: '10px', fontWeight: 'bold' }}
                    />
                  )}
                  <span>{alert.message}</span>
                </div>
                <span style={{ fontSize: '12px', color: '#666' }}>
                  {new Date(alert.timestamp).toLocaleTimeString('pt-BR')}
                </span>
              </div>
            }
            type={alert.type}
            icon={getAlertIcon(alert.type)}
            showIcon
            closable
            onClose={() => onDismiss(alert.id)}
            style={{
              borderLeft: `4px solid ${getSeverityColor(alert.severity)}`,
              borderRadius: '6px'
            }}
          />
        ))}
      </Space>
    </div>
  );
};

export default AlertPanel; 
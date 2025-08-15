/**
 * BusinessMetrics.tsx
 * 
 * Componente para exibir métricas de negócio do sistema
 * 
 * Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 5
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-19
 */

import React from 'react';
import { Card, Row, Col, Statistic, Progress, Tooltip } from 'antd';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, 
  ResponsiveContainer, PieChart, Pie, Cell 
} from 'recharts';
import { 
  SearchOutlined, 
  ClusterOutlined, 
  ApiOutlined,
  TrendingUpOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';

interface BusinessMetricsProps {
  keywordsProcessed: number;
  clustersGenerated: number;
  apiCalls: number;
  efficiency?: number;
  successRate?: number;
}

export const BusinessMetrics: React.FC<BusinessMetricsProps> = ({
  keywordsProcessed,
  clustersGenerated,
  apiCalls,
  efficiency = 85,
  successRate = 92
}) => {
  // Dados para gráfico de distribuição
  const distributionData = [
    { name: 'Keywords Processadas', value: keywordsProcessed, color: '#1890ff' },
    { name: 'Clusters Gerados', value: clustersGenerated, color: '#52c41a' },
    { name: 'Chamadas API', value: apiCalls, color: '#722ed1' }
  ];

  // Dados para gráfico de tendência (simulado)
  const trendData = [
    { time: '00:00', keywords: 120, clusters: 15, api: 45 },
    { time: '04:00', keywords: 85, clusters: 12, api: 32 },
    { time: '08:00', keywords: 200, clusters: 25, api: 78 },
    { time: '12:00', keywords: 350, clusters: 40, api: 120 },
    { time: '16:00', keywords: 280, clusters: 35, api: 95 },
    { time: '20:00', keywords: 180, clusters: 22, api: 65 }
  ];

  // Calcular métricas derivadas
  const avgKeywordsPerCluster = keywordsProcessed > 0 ? (keywordsProcessed / clustersGenerated).toFixed(1) : '0';
  const apiEfficiency = apiCalls > 0 ? ((keywordsProcessed / apiCalls) * 100).toFixed(1) : '0';

  return (
    <Card title="Métricas de Negócio" extra={<TrendingUpOutlined />}>
      <Row gutter={[16, 16]}>
        {/* Métricas Principais */}
        <Col xs={24} sm={8}>
          <Card size="small">
            <Statistic
              title="Keywords Processadas"
              value={keywordsProcessed}
              prefix={<SearchOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <Progress 
              percent={Math.min((keywordsProcessed / 1000) * 100, 100)} 
              size="small" 
              strokeColor="#1890ff"
              showInfo={false}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small">
            <Statistic
              title="Clusters Gerados"
              value={clustersGenerated}
              prefix={<ClusterOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <Progress 
              percent={Math.min((clustersGenerated / 100) * 100, 100)} 
              size="small" 
              strokeColor="#52c41a"
              showInfo={false}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small">
            <Statistic
              title="Chamadas API"
              value={apiCalls}
              prefix={<ApiOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
            <Progress 
              percent={Math.min((apiCalls / 500) * 100, 100)} 
              size="small" 
              strokeColor="#722ed1"
              showInfo={false}
            />
          </Card>
        </Col>

        {/* Métricas de Eficiência */}
        <Col xs={24} sm={12}>
          <Card size="small" title="Eficiência do Sistema">
            <Row gutter={16}>
              <Col span={12}>
                <Tooltip title="Taxa de sucesso das operações">
                  <Statistic
                    title="Taxa de Sucesso"
                    value={successRate}
                    suffix="%"
                    valueStyle={{ color: successRate > 90 ? '#52c41a' : '#faad14' }}
                    prefix={<CheckCircleOutlined />}
                  />
                </Tooltip>
              </Col>
              <Col span={12}>
                <Tooltip title="Eficiência geral do processamento">
                  <Statistic
                    title="Eficiência"
                    value={efficiency}
                    suffix="%"
                    valueStyle={{ color: efficiency > 80 ? '#52c41a' : '#faad14' }}
                    prefix={<TrendingUpOutlined />}
                  />
                </Tooltip>
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={12}>
                <Tooltip title="Média de keywords por cluster">
                  <Statistic
                    title="Keywords/Cluster"
                    value={avgKeywordsPerCluster}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Tooltip>
              </Col>
              <Col span={12}>
                <Tooltip title="Eficiência das chamadas API">
                  <Statistic
                    title="Eficiência API"
                    value={apiEfficiency}
                    suffix="%"
                    valueStyle={{ color: '#722ed1' }}
                  />
                </Tooltip>
              </Col>
            </Row>
          </Card>
        </Col>

        {/* Gráfico de Distribuição */}
        <Col xs={24} sm={12}>
          <Card size="small" title="Distribuição de Atividades">
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={distributionData}
                  cx="50%"
                  cy="50%"
                  outerRadius={60}
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {distributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  formatter={(value, name) => [value, name]}
                  labelFormatter={(label) => label}
                />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* Gráfico de Tendência */}
        <Col xs={24}>
          <Card size="small" title="Tendência das Últimas 24h">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <RechartsTooltip 
                  formatter={(value, name) => [
                    value, 
                    name === 'keywords' ? 'Keywords' :
                    name === 'clusters' ? 'Clusters' :
                    name === 'api' ? 'API Calls' : name
                  ]}
                />
                <Bar dataKey="keywords" fill="#1890ff" name="Keywords" />
                <Bar dataKey="clusters" fill="#52c41a" name="Clusters" />
                <Bar dataKey="api" fill="#722ed1" name="API Calls" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </Card>
  );
};

export default BusinessMetrics; 
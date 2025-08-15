/**
 * ExportReports.tsx
 * 
 * Componente para exportação de relatórios de performance
 * 
 * Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 5
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-19
 */

import React, { useState } from 'react';
import { Button, Space, Select, DatePicker, Card, message, Progress } from 'antd';
import { 
  DownloadOutlined, 
  FilePdfOutlined, 
  FileExcelOutlined, 
  FileTextOutlined,
  CalendarOutlined
} from '@ant-design/icons';

const { RangePicker } = DatePicker;
const { Option } = Select;

interface PerformanceData {
  timestamp: string;
  responseTime: number;
  throughput: number;
  errorRate: number;
  cpuUsage: number;
  memoryUsage: number;
  activeUsers: number;
  keywordsProcessed: number;
  clustersGenerated: number;
  apiCalls: number;
}

interface ExportReportsProps {
  onExport: (format: 'pdf' | 'csv' | 'json') => void;
  data: PerformanceData[];
  timeRange: string;
}

export const ExportReports: React.FC<ExportReportsProps> = ({
  onExport,
  data,
  timeRange
}) => {
  const [exportFormat, setExportFormat] = useState<'pdf' | 'csv' | 'json'>('pdf');
  const [dateRange, setDateRange] = useState<[string, string] | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);

  const handleExport = async () => {
    setIsExporting(true);
    setExportProgress(0);

    try {
      // Simular progresso de exportação
      const progressInterval = setInterval(() => {
        setExportProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Simular tempo de processamento
      await new Promise(resolve => setTimeout(resolve, 2000));

      clearInterval(progressInterval);
      setExportProgress(100);

      // Chamar função de exportação
      onExport(exportFormat);

      message.success(`Relatório exportado com sucesso em formato ${exportFormat.toUpperCase()}`);
    } catch (error) {
      message.error('Erro ao exportar relatório');
    } finally {
      setIsExporting(false);
      setExportProgress(0);
    }
  };

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'pdf': return <FilePdfOutlined />;
      case 'csv': return <FileExcelOutlined />;
      case 'json': return <FileTextOutlined />;
      default: return <DownloadOutlined />;
    }
  };

  const getFormatLabel = (format: string) => {
    switch (format) {
      case 'pdf': return 'PDF';
      case 'csv': return 'CSV';
      case 'json': return 'JSON';
      default: return format.toUpperCase();
    }
  };

  const getTimeRangeLabel = () => {
    switch (timeRange) {
      case '1h': return 'Última Hora';
      case '6h': return 'Últimas 6 Horas';
      case '24h': return 'Últimas 24 Horas';
      case '7d': return 'Últimos 7 Dias';
      default: return timeRange;
    }
  };

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%' }}>
        {/* Configurações de Exportação */}
        <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
          <div>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>
              Formato:
            </label>
            <Select
              value={exportFormat}
              onChange={setExportFormat}
              style={{ width: 120 }}
              disabled={isExporting}
            >
              <Option value="pdf">
                <Space>
                  {getFormatIcon('pdf')}
                  PDF
                </Space>
              </Option>
              <Option value="csv">
                <Space>
                  {getFormatIcon('csv')}
                  CSV
                </Space>
              </Option>
              <Option value="json">
                <Space>
                  {getFormatIcon('json')}
                  JSON
                </Space>
              </Option>
            </Select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>
              Período:
            </label>
            <RangePicker
              onChange={(dates) => {
                if (dates) {
                  setDateRange([
                    dates[0]?.toISOString() || '',
                    dates[1]?.toISOString() || ''
                  ]);
                } else {
                  setDateRange(null);
                }
              }}
              disabled={isExporting}
              style={{ width: 250 }}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>
              Intervalo Atual:
            </label>
            <div style={{ 
              padding: '8px 12px', 
              border: '1px solid #d9d9d9', 
              borderRadius: '6px',
              backgroundColor: '#fafafa',
              display: 'flex',
              alignItems: 'center',
              gap: 8
            }}>
              <CalendarOutlined />
              {getTimeRangeLabel()}
            </div>
          </div>
        </div>

        {/* Informações do Relatório */}
        <Card size="small" title="Informações do Relatório">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
            <div>
              <strong>Total de Registros:</strong> {data.length}
            </div>
            <div>
              <strong>Período:</strong> {dateRange ? `${new Date(dateRange[0]).toLocaleDateString()} - ${new Date(dateRange[1]).toLocaleDateString()}` : getTimeRangeLabel()}
            </div>
            <div>
              <strong>Formato:</strong> {getFormatLabel(exportFormat)}
            </div>
            <div>
              <strong>Última Atualização:</strong> {new Date().toLocaleString('pt-BR')}
            </div>
          </div>
        </Card>

        {/* Botão de Exportação */}
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: 16 }}>
          <Button
            type="primary"
            size="large"
            icon={getFormatIcon(exportFormat)}
            onClick={handleExport}
            loading={isExporting}
            disabled={isExporting}
            style={{ minWidth: 200 }}
          >
            {isExporting ? 'Exportando...' : `Exportar ${getFormatLabel(exportFormat)}`}
          </Button>
        </div>

        {/* Progresso de Exportação */}
        {isExporting && (
          <div style={{ marginTop: 16 }}>
            <Progress 
              percent={exportProgress} 
              status={exportProgress === 100 ? 'success' : 'active'}
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }}
            />
            <div style={{ textAlign: 'center', marginTop: 8, color: '#666' }}>
              Preparando relatório em {getFormatLabel(exportFormat)}...
            </div>
          </div>
        )}

        {/* Dicas de Exportação */}
        <Card size="small" title="Dicas de Exportação" style={{ marginTop: 16 }}>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            <li><strong>PDF:</strong> Ideal para relatórios formais e apresentações</li>
            <li><strong>CSV:</strong> Perfeito para análise em Excel ou outras ferramentas</li>
            <li><strong>JSON:</strong> Melhor para integração com outros sistemas</li>
            <li>Selecione um período específico para relatórios mais precisos</li>
            <li>Relatórios grandes podem levar alguns minutos para processar</li>
          </ul>
        </Card>
      </Space>
    </div>
  );
};

export default ExportReports; 
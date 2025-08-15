/**
 * AuditPanel.tsx
 * 
 * Componente principal do sistema de auditoria avançado
 * Integra logs detalhados, compliance e detecção de anomalias
 * 
 * Tracing ID: UI-002
 * Data/Hora: 2024-12-20 07:15:00 UTC
 * Versão: 1.0
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '../shared/Card';
import { Button } from '../shared/Button';
import { Badge } from '../shared/Badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../shared/Tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../shared/Select';
import { DatePicker } from '../shared/DatePicker';
import { Input } from '../shared/Input';
import { Alert, AlertDescription } from '../shared/Alert';
import { Skeleton } from '../shared/Skeleton';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../shared/Table';
import { useAudit } from '../../hooks/useAudit';
import { useSecurityMetrics } from '../../hooks/useSecurityMetrics';
import { formatDate, formatTime } from '../../utils/formatters';
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Search,
  Download,
  RefreshCw,
  Filter,
  Eye,
  EyeOff,
  Lock,
  Unlock,
  User,
  Database,
  Server,
  Network,
  FileText,
  Settings,
  Bell,
  TrendingUp,
  TrendingDown
} from 'lucide-react';

interface AuditLog {
  id: string;
  timestamp: Date;
  level: 'info' | 'warning' | 'error' | 'critical';
  category: 'security' | 'user' | 'system' | 'data' | 'api' | 'performance';
  user: string;
  action: string;
  resource: string;
  details: string;
  ipAddress: string;
  userAgent: string;
  sessionId: string;
  metadata: Record<string, any>;
}

interface ComplianceReport {
  id: string;
  name: string;
  status: 'compliant' | 'non-compliant' | 'warning';
  lastCheck: Date;
  nextCheck: Date;
  violations: number;
  score: number;
  framework: string;
  details: string;
}

interface SecurityAlert {
  id: string;
  type: 'anomaly' | 'threat' | 'vulnerability' | 'compliance';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  timestamp: Date;
  status: 'open' | 'investigating' | 'resolved' | 'false-positive';
  affectedResources: string[];
  recommendations: string[];
}

interface AuditPanelProps {
  className?: string;
  refreshInterval?: number;
  enableRealTime?: boolean;
  exportFormats?: ('csv' | 'json' | 'pdf')[];
  maxLogs?: number;
}

export const AuditPanel: React.FC<AuditPanelProps> = ({
  className = '',
  refreshInterval = 30000,
  enableRealTime = true,
  exportFormats = ['csv', 'json'],
  maxLogs = 1000
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedLevel, setSelectedLevel] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [dateRange, setDateRange] = useState<{ start: Date; end: Date }>({
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7 dias atrás
    end: new Date()
  });
  const [isExporting, setIsExporting] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [showSensitiveData, setShowSensitiveData] = useState(false);

  const {
    data: auditData,
    isLoading,
    error,
    refetch
  } = useAudit({
    category: selectedCategory,
    level: selectedLevel,
    searchTerm,
    dateRange,
    maxLogs
  });

  const {
    data: securityMetrics,
    isLoading: metricsLoading
  } = useSecurityMetrics();

  // Auto-refresh para dados em tempo real
  useEffect(() => {
    if (!enableRealTime) return;

    const interval = setInterval(() => {
      refetch();
      setLastRefresh(new Date());
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [enableRealTime, refreshInterval, refetch]);

  // Cálculos derivados
  const calculatedMetrics = useMemo(() => {
    if (!auditData) return null;

    const { logs, complianceReports, securityAlerts } = auditData;

    return {
      totalLogs: logs.length,
      criticalLogs: logs.filter(log => log.level === 'critical').length,
      securityViolations: logs.filter(log => log.category === 'security' && log.level === 'error').length,
      complianceScore: complianceReports.reduce((acc, report) => acc + report.score, 0) / complianceReports.length,
      openAlerts: securityAlerts.filter(alert => alert.status === 'open').length,
      riskLevel: calculateRiskLevel(logs, securityAlerts)
    };
  }, [auditData]);

  const calculateRiskLevel = (logs: AuditLog[], alerts: SecurityAlert[]): 'low' | 'medium' | 'high' | 'critical' => {
    const criticalLogs = logs.filter(log => log.level === 'critical').length;
    const highAlerts = alerts.filter(alert => alert.severity === 'high' || alert.severity === 'critical').length;
    
    if (criticalLogs > 10 || highAlerts > 5) return 'critical';
    if (criticalLogs > 5 || highAlerts > 2) return 'high';
    if (criticalLogs > 2 || highAlerts > 0) return 'medium';
    return 'low';
  };

  // Handlers
  const handleExport = async (format: string) => {
    setIsExporting(true);
    try {
      // Implementar lógica de exportação
      console.log(`Exporting audit data in ${format} format`);
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulação
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const handleRefresh = () => {
    refetch();
    setLastRefresh(new Date());
  };

  const handleAlertAction = (alertId: string, action: string) => {
    console.log(`Alert ${alertId}: ${action}`);
    // Implementar ações de alerta
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'critical': return 'destructive';
      case 'error': return 'destructive';
      case 'warning': return 'warning';
      case 'info': return 'secondary';
      default: return 'secondary';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'security': return <Shield className="h-4 w-4" />;
      case 'user': return <User className="h-4 w-4" />;
      case 'system': return <Server className="h-4 w-4" />;
      case 'data': return <Database className="h-4 w-4" />;
      case 'api': return <Network className="h-4 w-4" />;
      case 'performance': return <TrendingUp className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  // Renderização de loading
  if (isLoading) {
    return (
      <div className={`audit-panel ${className}`}>
        <div className="grid gap-6">
          <Skeleton className="h-8 w-64" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
          <Skeleton className="h-96" />
        </div>
      </div>
    );
  }

  // Renderização de erro
  if (error) {
    return (
      <div className={`audit-panel ${className}`}>
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Erro ao carregar dados de auditoria: {error.message}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className={`audit-panel ${className}`}>
      {/* Header com controles */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Painel de Auditoria</h1>
          <p className="text-muted-foreground">
            Logs detalhados, compliance e detecção de anomalias
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSensitiveData(!showSensitiveData)}
          >
            {showSensitiveData ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
            {showSensitiveData ? 'Ocultar' : 'Mostrar'} Dados Sensíveis
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>

          <div className="flex gap-1">
            {exportFormats.map(format => (
              <Button
                key={format}
                variant="outline"
                size="sm"
                onClick={() => handleExport(format)}
                disabled={isExporting}
              >
                <Download className="h-4 w-4 mr-2" />
                {format.toUpperCase()}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Indicadores de status */}
      <div className="flex items-center gap-4 mb-6 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4" />
          Última atualização: {lastRefresh.toLocaleTimeString()}
        </div>
        
        {enableRealTime && (
          <div className="flex items-center gap-2">
            <Bell className="h-4 w-4 text-green-500" />
            Monitoramento ativo
          </div>
        )}

        {calculatedMetrics && (
          <div className="flex items-center gap-2">
            {calculatedMetrics.riskLevel === 'low' ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : calculatedMetrics.riskLevel === 'medium' ? (
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
            ) : calculatedMetrics.riskLevel === 'high' ? (
              <AlertTriangle className="h-4 w-4 text-orange-500" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-red-500" />
            )}
            Risco: {calculatedMetrics.riskLevel}
          </div>
        )}
      </div>

      {/* Métricas principais */}
      {auditData && calculatedMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Logs</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {calculatedMetrics.totalLogs.toLocaleString()}
              </div>
              <div className="text-xs text-muted-foreground">
                {calculatedMetrics.criticalLogs} críticos
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Violações de Segurança</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {calculatedMetrics.securityViolations}
              </div>
              <div className="text-xs text-muted-foreground">
                Últimas 24 horas
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Score de Compliance</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {calculatedMetrics.complianceScore.toFixed(1)}%
              </div>
              <div className="text-xs text-muted-foreground">
                Média dos frameworks
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Alertas Abertos</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {calculatedMetrics.openAlerts}
              </div>
              <div className="text-xs text-muted-foreground">
                Requerem atenção
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filtros */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div>
          <label className="text-sm font-medium">Categoria</label>
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas as categorias</SelectItem>
              <SelectItem value="security">Segurança</SelectItem>
              <SelectItem value="user">Usuário</SelectItem>
              <SelectItem value="system">Sistema</SelectItem>
              <SelectItem value="data">Dados</SelectItem>
              <SelectItem value="api">API</SelectItem>
              <SelectItem value="performance">Performance</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-sm font-medium">Nível</label>
          <Select value={selectedLevel} onValueChange={setSelectedLevel}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os níveis</SelectItem>
              <SelectItem value="critical">Crítico</SelectItem>
              <SelectItem value="error">Erro</SelectItem>
              <SelectItem value="warning">Aviso</SelectItem>
              <SelectItem value="info">Info</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-sm font-medium">Buscar</label>
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <div>
          <label className="text-sm font-medium">Período</label>
          <DatePicker
            value={dateRange}
            onChange={setDateRange}
            className="w-full"
          />
        </div>
      </div>

      {/* Tabs principais */}
      <Tabs defaultValue="logs" className="space-y-4">
        <TabsList>
          <TabsTrigger value="logs">Logs de Auditoria</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
          <TabsTrigger value="alerts">Alertas de Segurança</TabsTrigger>
          <TabsTrigger value="analytics">Análise</TabsTrigger>
        </TabsList>

        <TabsContent value="logs" className="space-y-4">
          {auditData && (
            <Card>
              <CardHeader>
                <CardTitle>Logs de Auditoria</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>Nível</TableHead>
                      <TableHead>Categoria</TableHead>
                      <TableHead>Usuário</TableHead>
                      <TableHead>Ação</TableHead>
                      <TableHead>Recurso</TableHead>
                      <TableHead>IP</TableHead>
                      <TableHead>Detalhes</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {auditData.logs.slice(0, 50).map((log) => (
                      <TableRow key={log.id}>
                        <TableCell className="font-mono text-sm">
                          {formatTime(log.timestamp)}
                        </TableCell>
                        <TableCell>
                          <Badge variant={getLevelColor(log.level)}>
                            {log.level.toUpperCase()}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getCategoryIcon(log.category)}
                            {log.category}
                          </div>
                        </TableCell>
                        <TableCell>
                          {showSensitiveData ? log.user : '***'}
                        </TableCell>
                        <TableCell>{log.action}</TableCell>
                        <TableCell>{log.resource}</TableCell>
                        <TableCell className="font-mono text-sm">
                          {showSensitiveData ? log.ipAddress : '***.***.***.***'}
                        </TableCell>
                        <TableCell>
                          <div className="max-w-xs truncate" title={log.details}>
                            {log.details}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="compliance" className="space-y-4">
          {auditData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Relatórios de Compliance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {auditData.complianceReports.map((report) => (
                      <div key={report.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{report.name}</h4>
                          <Badge variant={report.status === 'compliant' ? 'success' : 'destructive'}>
                            {report.status}
                          </Badge>
                        </div>
                        <div className="text-sm text-muted-foreground mb-2">
                          Framework: {report.framework}
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span>Score: {report.score}%</span>
                          <span>Violations: {report.violations}</span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-2">
                          Próximo check: {formatDate(report.nextCheck)}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Métricas de Compliance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm font-medium mb-2">Score Geral</p>
                      <div className="text-2xl font-bold">
                        {calculatedMetrics?.complianceScore.toFixed(1)}%
                      </div>
                    </div>
                    <div>
                      <p className="text-sm font-medium mb-2">Frameworks Ativos</p>
                      <div className="text-sm text-muted-foreground">
                        {auditData.complianceReports.length} frameworks monitorados
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          {auditData && (
            <div className="space-y-4">
              {auditData.securityAlerts.map((alert) => (
                <Card key={alert.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Badge variant={alert.severity === 'critical' ? 'destructive' : 'warning'}>
                          {alert.severity.toUpperCase()}
                        </Badge>
                        <CardTitle className="text-lg">{alert.title}</CardTitle>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={alert.status === 'open' ? 'destructive' : 'secondary'}>
                          {alert.status}
                        </Badge>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleAlertAction(alert.id, 'investigate')}
                        >
                          Investigar
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleAlertAction(alert.id, 'resolve')}
                        >
                          Resolver
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <p className="text-sm text-muted-foreground">
                        {alert.description}
                      </p>
                      
                      <div>
                        <p className="text-sm font-medium mb-2">Recursos Afetados:</p>
                        <div className="flex flex-wrap gap-2">
                          {alert.affectedResources.map((resource, index) => (
                            <Badge key={index} variant="outline">
                              {resource}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="text-sm font-medium mb-2">Recomendações:</p>
                        <ul className="text-sm text-muted-foreground space-y-1">
                          {alert.recommendations.map((rec, index) => (
                            <li key={index}>• {rec}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="text-xs text-muted-foreground">
                        Detectado em: {formatDate(alert.timestamp)}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          {auditData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Análise de Padrões</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm font-medium mb-2">Logs por Categoria</p>
                      <div className="space-y-2">
                        {['security', 'user', 'system', 'data', 'api', 'performance'].map(category => {
                          const count = auditData.logs.filter(log => log.category === category).length;
                          return (
                            <div key={category} className="flex items-center justify-between">
                              <span className="text-sm capitalize">{category}</span>
                              <Badge variant="secondary">{count}</Badge>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Análise de Risco</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm font-medium mb-2">Nível de Risco Atual</p>
                      <div className="text-2xl font-bold">
                        {calculatedMetrics?.riskLevel.toUpperCase()}
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-sm font-medium mb-2">Tendência</p>
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4 text-green-500" />
                        <span className="text-sm">Risco diminuindo</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AuditPanel; 
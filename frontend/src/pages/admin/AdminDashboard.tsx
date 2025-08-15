/**
 * 📊 AdminDashboard.tsx
 * 🎯 Objetivo: Dashboard administrativo principal unificado
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: ADMIN_DASHBOARD_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Download,
  RefreshCw,
  Settings,
  BarChart3,
  LineChart,
  PieChart,
  Gauge,
  Zap,
  Shield,
  Users,
  Database,
  Globe,
  Server,
  UserCheck,
  UserX,
  ShieldAlert,
  Cpu,
  HardDrive,
  Network,
  FileText,
  Settings as SettingsIcon,
  Users as UsersIcon,
  Shield as ShieldIcon,
  Zap as ZapIcon,
  Database as DatabaseIcon,
  FileText as LogsIcon,
  Building as TenantIcon
} from 'lucide-react';

// Tipos para dados administrativos
interface AdminMetrics {
  users: {
    total: number;
    active: number;
    suspended: number;
    new_today: number;
    growth_rate: number;
  };
  system: {
    uptime: number;
    response_time: number;
    error_rate: number;
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
  };
  security: {
    threats_active: number;
    vulnerabilities_critical: number;
    compliance_score: number;
    last_incident: string;
  };
  performance: {
    cache_hit_rate: number;
    avg_query_time: number;
    optimization_savings: number;
    pending_optimizations: number;
  };
}

interface AdminAlert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  isAcknowledged: boolean;
}

interface AdminQuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  action: () => void;
  requiresPermission: string;
}

// Dados de exemplo
const SAMPLE_METRICS: AdminMetrics = {
  users: {
    total: 1247,
    active: 1189,
    suspended: 58,
    new_today: 12,
    growth_rate: 8.7
  },
  system: {
    uptime: 99.9,
    response_time: 245,
    error_rate: 0.1,
    cpu_usage: 78.5,
    memory_usage: 65.3,
    disk_usage: 45.2
  },
  security: {
    threats_active: 3,
    vulnerabilities_critical: 1,
    compliance_score: 92,
    last_incident: '2025-01-27T10:30:00Z'
  },
  performance: {
    cache_hit_rate: 87.3,
    avg_query_time: 125,
    optimization_savings: 15.2,
    pending_optimizations: 5
  }
};

const SAMPLE_ALERTS: AdminAlert[] = [
  {
    id: 'alert_001',
    type: 'warning',
    title: 'Alto uso de CPU',
    message: 'CPU atingiu 85% de uso',
    timestamp: '2025-01-27T16:45:00Z',
    severity: 'medium',
    isAcknowledged: false
  },
  {
    id: 'alert_002',
    type: 'error',
    title: 'Vulnerabilidade crítica detectada',
    message: 'CVE-2024-1234 detectado no sistema',
    timestamp: '2025-01-27T16:30:00Z',
    severity: 'critical',
    isAcknowledged: false
  },
  {
    id: 'alert_003',
    type: 'info',
    title: 'Backup automático concluído',
    message: 'Backup diário concluído com sucesso',
    timestamp: '2025-01-27T16:00:00Z',
    severity: 'low',
    isAcknowledged: true
  }
];

export const AdminDashboard: React.FC = () => {
  // Estados
  const [metrics, setMetrics] = useState<AdminMetrics>(SAMPLE_METRICS);
  const [alerts, setAlerts] = useState<AdminAlert[]>(SAMPLE_ALERTS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [activeTab, setActiveTab] = useState('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30);

  // Memoized values
  const criticalAlerts = useMemo(() => 
    alerts.filter(alert => alert.severity === 'critical' && !alert.isAcknowledged), 
    [alerts]
  );

  const unacknowledgedAlerts = useMemo(() => 
    alerts.filter(alert => !alert.isAcknowledged), 
    [alerts]
  );

  const systemHealth = useMemo(() => {
    const { cpu_usage, memory_usage, disk_usage, error_rate } = metrics.system;
    
    if (cpu_usage > 90 || memory_usage > 90 || disk_usage > 90 || error_rate > 5) {
      return 'critical';
    } else if (cpu_usage > 80 || memory_usage > 80 || disk_usage > 80 || error_rate > 2) {
      return 'warning';
    } else {
      return 'healthy';
    }
  }, [metrics.system]);

  // Funções
  const refreshData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Em produção, buscar dados da API
      // const response = await fetch('/admin/api/v1/monitoring/overview');
      // const data = await response.json();
      // setMetrics(data.metrics);
      // setAlerts(data.alerts);
      
      // Simular delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setLastUpdate(new Date());
    } catch (err) {
      setError('Erro ao carregar dados administrativos');
      console.error('Erro ao carregar dados:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const acknowledgeAlert = useCallback((alertId: string) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId 
          ? { ...alert, isAcknowledged: true }
          : alert
      )
    );
  }, []);

  const exportReport = useCallback(() => {
    const report = {
      timestamp: new Date().toISOString(),
      metrics,
      alerts,
      summary: {
        totalUsers: metrics.users.total,
        activeUsers: metrics.users.active,
        systemHealth,
        criticalAlerts: criticalAlerts.length,
        unacknowledgedAlerts: unacknowledgedAlerts.length
      }
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `admin_report_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [metrics, alerts, systemHealth, criticalAlerts, unacknowledgedAlerts]);

  // Quick actions
  const quickActions: AdminQuickAction[] = [
    {
      id: 'users',
      title: 'Gestão de Usuários',
      description: 'Gerenciar usuários, roles e permissões',
      icon: <UsersIcon className="w-5 h-5" />,
      action: () => window.location.href = '/admin/users',
      requiresPermission: 'users:read'
    },
    {
      id: 'security',
      title: 'Segurança',
      description: 'Monitorar ameaças e compliance',
      icon: <ShieldIcon className="w-5 h-5" />,
      action: () => window.location.href = '/admin/security',
      requiresPermission: 'security:read'
    },
    {
      id: 'performance',
      title: 'Performance',
      description: 'Otimizar performance do sistema',
      icon: <ZapIcon className="w-5 h-5" />,
      action: () => window.location.href = '/admin/performance',
      requiresPermission: 'performance:read'
    },
    {
      id: 'cache',
      title: 'Cache',
      description: 'Gerenciar cache e otimizações',
      icon: <DatabaseIcon className="w-5 h-5" />,
      action: () => window.location.href = '/admin/cache',
      requiresPermission: 'cache:read'
    },
    {
      id: 'logs',
      title: 'Logs',
      description: 'Visualizar logs do sistema',
      icon: <LogsIcon className="w-5 h-5" />,
      action: () => window.location.href = '/admin/logs',
      requiresPermission: 'logs:read'
    },
    {
      id: 'tenants',
      title: 'Tenants',
      description: 'Gerenciar tenants e recursos',
      icon: <TenantIcon className="w-5 h-5" />,
      action: () => window.location.href = '/admin/tenants',
      requiresPermission: 'tenants:read'
    }
  ];

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(refreshData, refreshInterval * 1000);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, refreshData]);

  // Carregar dados iniciais
  useEffect(() => {
    refreshData();
  }, [refreshData]);

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'bg-green-100 text-green-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">🔧 Dashboard Administrativo</h1>
          <p className="text-gray-600">
            Visão geral do sistema • Última atualização: {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Switch
              checked={autoRefresh}
              onCheckedChange={setAutoRefresh}
            />
            <Label>Auto-refresh</Label>
          </div>
          <Select value={refreshInterval.toString()} onValueChange={(value) => setRefreshInterval(Number(value))}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="15">15s</SelectItem>
              <SelectItem value="30">30s</SelectItem>
              <SelectItem value="60">1m</SelectItem>
              <SelectItem value="300">5m</SelectItem>
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            onClick={refreshData}
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button onClick={exportReport}>
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>

      {/* Alertas Críticos */}
      {criticalAlerts.length > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <strong>{criticalAlerts.length} alerta(s) crítico(s)</strong> requerem atenção imediata.
            <Button
              variant="link"
              className="p-0 h-auto text-destructive"
              onClick={() => setActiveTab('alerts')}
            >
              Ver detalhes
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="users">Usuários</TabsTrigger>
          <TabsTrigger value="system">Sistema</TabsTrigger>
          <TabsTrigger value="security">Segurança</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="alerts">Alertas</TabsTrigger>
          <TabsTrigger value="actions">Ações Rápidas</TabsTrigger>
        </TabsList>

        {/* Visão Geral */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Saúde do Sistema */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <Server className="w-4 h-4" />
                    <span>Saúde do Sistema</span>
                  </div>
                  <Badge className={getHealthColor(systemHealth)}>
                    {systemHealth}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.system.uptime}%</div>
                <p className="text-xs text-muted-foreground">
                  Uptime do sistema
                </p>
              </CardContent>
            </Card>

            {/* Usuários Ativos */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <Users className="w-4 h-4" />
                    <span>Usuários Ativos</span>
                  </div>
                  <Badge variant="secondary">
                    +{metrics.users.growth_rate}%
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.users.active}</div>
                <p className="text-xs text-muted-foreground">
                  de {metrics.users.total} total
                </p>
              </CardContent>
            </Card>

            {/* Score de Segurança */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <Shield className="w-4 h-4" />
                    <span>Score de Segurança</span>
                  </div>
                  <Badge variant="outline">
                    {metrics.security.threats_active} ameaças
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.security.compliance_score}%</div>
                <p className="text-xs text-muted-foreground">
                  Compliance score
                </p>
              </CardContent>
            </Card>

            {/* Performance */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <Zap className="w-4 h-4" />
                    <span>Performance</span>
                  </div>
                  <Badge variant="outline">
                    {metrics.performance.pending_optimizations} pendentes
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.performance.cache_hit_rate}%</div>
                <p className="text-xs text-muted-foreground">
                  Cache hit rate
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Gráficos de Resumo */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Métricas do Sistema
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>CPU</span>
                      <span>{metrics.system.cpu_usage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          metrics.system.cpu_usage > 80 ? 'bg-red-500' : 
                          metrics.system.cpu_usage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                        }`}
                        style={{ width: `${metrics.system.cpu_usage}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>Memória</span>
                      <span>{metrics.system.memory_usage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          metrics.system.memory_usage > 80 ? 'bg-red-500' : 
                          metrics.system.memory_usage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                        }`}
                        style={{ width: `${metrics.system.memory_usage}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>Disco</span>
                      <span>{metrics.system.disk_usage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          metrics.system.disk_usage > 80 ? 'bg-red-500' : 
                          metrics.system.disk_usage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                        }`}
                        style={{ width: `${metrics.system.disk_usage}%` }}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Alertas Recentes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {alerts.slice(0, 5).map((alert) => (
                    <div key={alert.id} className="flex items-center justify-between p-2 border rounded">
                      <div className="flex items-center space-x-2">
                        {alert.type === 'error' && <AlertTriangle className="w-4 h-4 text-red-500" />}
                        {alert.type === 'warning' && <AlertTriangle className="w-4 h-4 text-yellow-500" />}
                        {alert.type === 'info' && <CheckCircle className="w-4 h-4 text-blue-500" />}
                        {alert.type === 'success' && <CheckCircle className="w-4 h-4 text-green-500" />}
                        <span className="text-sm font-medium">{alert.title}</span>
                      </div>
                      <Badge className={getSeverityColor(alert.severity)}>
                        {alert.severity}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Usuários */}
        <TabsContent value="users" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Total de Usuários</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.users.total}</div>
                <p className="text-xs text-muted-foreground">
                  Usuários registrados
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Usuários Ativos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{metrics.users.active}</div>
                <p className="text-xs text-muted-foreground">
                  {((metrics.users.active / metrics.users.total) * 100).toFixed(1)}% do total
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Usuários Suspensos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{metrics.users.suspended}</div>
                <p className="text-xs text-muted-foreground">
                  Requerem atenção
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Novos Hoje</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">{metrics.users.new_today}</div>
                <p className="text-xs text-muted-foreground">
                  +{metrics.users.growth_rate}% crescimento
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Sistema */}
        <TabsContent value="system" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Uptime</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.system.uptime}%</div>
                <p className="text-xs text-muted-foreground">
                  Tempo de atividade
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Tempo de Resposta</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.system.response_time}ms</div>
                <p className="text-xs text-muted-foreground">
                  Média de resposta
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Taxa de Erro</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.system.error_rate}%</div>
                <p className="text-xs text-muted-foreground">
                  Erros por requisição
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Segurança */}
        <TabsContent value="security" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Score de Compliance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.security.compliance_score}%</div>
                <p className="text-xs text-muted-foreground">
                  Conformidade geral
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Ameaças Ativas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{metrics.security.threats_active}</div>
                <p className="text-xs text-muted-foreground">
                  Requerem ação
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Vulnerabilidades Críticas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{metrics.security.vulnerabilities_critical}</div>
                <p className="text-xs text-muted-foreground">
                  Prioridade máxima
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Último Incidente</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm font-bold">
                  {new Date(metrics.security.last_incident).toLocaleDateString()}
                </div>
                <p className="text-xs text-muted-foreground">
                  {new Date(metrics.security.last_incident).toLocaleTimeString()}
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Performance */}
        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Cache Hit Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.performance.cache_hit_rate}%</div>
                <p className="text-xs text-muted-foreground">
                  Eficiência do cache
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Tempo Médio de Query</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.performance.avg_query_time}ms</div>
                <p className="text-xs text-muted-foreground">
                  Performance do banco
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Economia de Otimização</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{metrics.performance.optimization_savings}%</div>
                <p className="text-xs text-muted-foreground">
                  Melhoria de performance
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Otimizações Pendentes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">{metrics.performance.pending_optimizations}</div>
                <p className="text-xs text-muted-foreground">
                  Aguardando aplicação
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Alertas */}
        <TabsContent value="alerts" className="space-y-4">
          <div className="space-y-4">
            {alerts.map((alert) => (
              <Card key={alert.id}>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {alert.type === 'error' && <AlertTriangle className="w-5 h-5 text-red-500" />}
                      {alert.type === 'warning' && <AlertTriangle className="w-5 h-5 text-yellow-500" />}
                      {alert.type === 'info' && <CheckCircle className="w-5 h-5 text-blue-500" />}
                      {alert.type === 'success' && <CheckCircle className="w-5 h-5 text-green-500" />}
                      <div>
                        <h4 className="font-semibold">{alert.title}</h4>
                        <p className="text-sm text-muted-foreground">{alert.message}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(alert.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getSeverityColor(alert.severity)}>
                        {alert.severity}
                      </Badge>
                      {!alert.isAcknowledged && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => acknowledgeAlert(alert.id)}
                        >
                          Reconhecer
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Ações Rápidas */}
        <TabsContent value="actions" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quickActions.map((action) => (
              <Card key={action.id} className="cursor-pointer hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-center space-x-3" onClick={action.action}>
                    <div className="p-2 bg-blue-100 rounded-lg">
                      {action.icon}
                    </div>
                    <div>
                      <h4 className="font-semibold">{action.title}</h4>
                      <p className="text-sm text-muted-foreground">{action.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default AdminDashboard; 
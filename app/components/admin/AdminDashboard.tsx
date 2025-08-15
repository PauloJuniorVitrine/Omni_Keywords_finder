/**
 * 🏠 Componente AdminDashboard - Painel Administrativo
 * 🎯 Objetivo: Interface administrativa completa
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: FRONTEND_ADMIN_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useEffect, useCallback } from 'react';
import { cn } from '../../utils/cn';

// Ícones SVG
const UsersIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
  </svg>
);

const ChartIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
);

const SettingsIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const AlertIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
  </svg>
);

interface AdminDashboardProps {
  /** Dados do dashboard */
  data?: DashboardData;
  /** Callback para atualizar dados */
  onRefresh?: () => void;
  /** Callback para navegação */
  onNavigate?: (section: string) => void;
  /** Classe CSS adicional */
  className?: string;
}

interface DashboardData {
  users: {
    total: number;
    active: number;
    newToday: number;
    growthRate: number;
  };
  executions: {
    total: number;
    completed: number;
    failed: number;
    successRate: number;
  };
  system: {
    cpuUsage: number;
    memoryUsage: number;
    diskUsage: number;
    uptime: number;
  };
  alerts: Alert[];
  recentActivity: Activity[];
}

interface Alert {
  id: string;
  type: 'info' | 'warning' | 'error';
  message: string;
  timestamp: string;
}

interface Activity {
  id: string;
  type: string;
  description: string;
  user: string;
  timestamp: string;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({
  data,
  onRefresh,
  onNavigate,
  className
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [selectedSection, setSelectedSection] = useState('overview');

  // Dados mock para demonstração
  const mockData: DashboardData = {
    users: {
      total: 1250,
      active: 890,
      newToday: 23,
      growthRate: 12.5
    },
    executions: {
      total: 15420,
      completed: 14890,
      failed: 530,
      successRate: 96.6
    },
    system: {
      cpuUsage: 45.2,
      memoryUsage: 67.8,
      diskUsage: 34.1,
      uptime: 99.8
    },
    alerts: [
      {
        id: '1',
        type: 'warning',
        message: 'Uso de memória acima de 80%',
        timestamp: '2025-01-27T15:30:00Z'
      },
      {
        id: '2',
        type: 'info',
        message: 'Backup automático concluído',
        timestamp: '2025-01-27T14:00:00Z'
      }
    ],
    recentActivity: [
      {
        id: '1',
        type: 'user_login',
        description: 'Usuário fez login',
        user: 'admin@example.com',
        timestamp: '2025-01-27T15:25:00Z'
      },
      {
        id: '2',
        type: 'execution_completed',
        description: 'Execução de keywords concluída',
        user: 'user@example.com',
        timestamp: '2025-01-27T15:20:00Z'
      }
    ]
  };

  const dashboardData = data || mockData;

  // Atualizar dados
  const handleRefresh = useCallback(async () => {
    setIsLoading(true);
    try {
      await onRefresh?.();
    } finally {
      setIsLoading(false);
    }
  }, [onRefresh]);

  // Navegar para seção
  const handleNavigate = useCallback((section: string) => {
    setSelectedSection(section);
    onNavigate?.(section);
  }, [onNavigate]);

  // Formatar timestamp
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('pt-BR');
  };

  // Obter cor baseada no tipo de alerta
  const getAlertColor = (type: Alert['type']) => {
    switch (type) {
      case 'error':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'info':
        return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  // Obter ícone baseado no tipo de alerta
  const getAlertIcon = (type: Alert['type']) => {
    switch (type) {
      case 'error':
        return '🔴';
      case 'warning':
        return '🟡';
      case 'info':
        return '🔵';
    }
  };

  return (
    <div className={cn('w-full max-w-7xl mx-auto p-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Painel Administrativo</h1>
          <p className="text-gray-600 mt-1">
            Gerencie usuários, monitore sistema e visualize métricas
          </p>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {isLoading ? 'Atualizando...' : 'Atualizar'}
          </button>
        </div>
      </div>

      {/* Navegação */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1">
        {[
          { id: 'overview', label: 'Visão Geral', icon: ChartIcon },
          { id: 'users', label: 'Usuários', icon: UsersIcon },
          { id: 'system', label: 'Sistema', icon: SettingsIcon },
          { id: 'alerts', label: 'Alertas', icon: AlertIcon }
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => handleNavigate(id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-md transition-colors',
              selectedSection === id
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            <Icon />
            {label}
          </button>
        ))}
      </div>

      {/* Conteúdo Principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Métricas Principais */}
        <div className="lg:col-span-2 space-y-6">
          {/* Cards de Métricas */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total de Usuários</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboardData.users.total.toLocaleString()}
                  </p>
                </div>
                <UsersIcon />
              </div>
              <div className="mt-2">
                <span className="text-sm text-green-600">
                  +{dashboardData.users.growthRate}% este mês
                </span>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Execuções</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboardData.executions.total.toLocaleString()}
                  </p>
                </div>
                <ChartIcon />
              </div>
              <div className="mt-2">
                <span className="text-sm text-blue-600">
                  {dashboardData.executions.successRate}% sucesso
                </span>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">CPU</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboardData.system.cpuUsage}%
                  </p>
                </div>
                <SettingsIcon />
              </div>
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${dashboardData.system.cpuUsage}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Memória</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboardData.system.memoryUsage}%
                  </p>
                </div>
                <SettingsIcon />
              </div>
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${dashboardData.system.memoryUsage}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Gráfico de Atividade */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Atividade Recente
            </h3>
            <div className="space-y-3">
              {dashboardData.recentActivity.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-blue-600 rounded-full" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {activity.description}
                      </p>
                      <p className="text-xs text-gray-500">
                        {activity.user} • {formatTimestamp(activity.timestamp)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status do Sistema */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Status do Sistema
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Uptime</span>
                <span className="text-sm font-medium text-green-600">
                  {dashboardData.system.uptime}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Disco</span>
                <span className="text-sm font-medium text-gray-900">
                  {dashboardData.system.diskUsage}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Usuários Ativos</span>
                <span className="text-sm font-medium text-blue-600">
                  {dashboardData.users.active}
                </span>
              </div>
            </div>
          </div>

          {/* Alertas */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Alertas Recentes
            </h3>
            <div className="space-y-3">
              {dashboardData.alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={cn(
                    'p-3 rounded-md border-l-4',
                    getAlertColor(alert.type)
                  )}
                >
                  <div className="flex items-start gap-2">
                    <span className="text-lg">{getAlertIcon(alert.type)}</span>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{alert.message}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatTimestamp(alert.timestamp)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Ações Rápidas */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Ações Rápidas
            </h3>
            <div className="space-y-2">
              <button
                onClick={() => handleNavigate('users')}
                className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md transition-colors"
              >
                Gerenciar Usuários
              </button>
              <button
                onClick={() => handleNavigate('system')}
                className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md transition-colors"
              >
                Configurações do Sistema
              </button>
              <button
                onClick={() => handleNavigate('alerts')}
                className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md transition-colors"
              >
                Ver Todos os Alertas
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard; 
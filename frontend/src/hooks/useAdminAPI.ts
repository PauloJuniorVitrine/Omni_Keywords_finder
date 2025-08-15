/**
 * 🔗 useAdminAPI.ts
 * 🎯 Objetivo: Hooks para integração com API de administração
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: HOOKS_ADMIN_API_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

import { useState, useEffect, useCallback, useMemo } from 'react';

// Tipos para dados administrativos
export interface AdminMetrics {
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

export interface AdminUser {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
  status: 'active' | 'suspended' | 'inactive';
  created_at: string;
  last_login: string;
  is_active: boolean;
  email_verified: boolean;
  statistics?: {
    executions_count: number;
    payments_count: number;
  };
}

export interface AdminAlert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  isAcknowledged: boolean;
}

export interface AdminSystemConfig {
  app_name: string;
  version: string;
  environment: string;
  maintenance_mode: boolean;
  rate_limit_requests: number;
  session_timeout: number;
  [key: string]: any;
}

export interface AdminReport {
  users: {
    summary: {
      total_users: number;
      active_users: number;
      suspended_users: number;
      new_users_today: number;
    };
    by_role: Record<string, number>;
    by_month: Array<{
      month: string;
      count: number;
    }>;
  };
  executions: {
    summary: {
      total_executions: number;
      successful_executions: number;
      failed_executions: number;
      avg_execution_time: number;
    };
    by_status: Record<string, number>;
    by_day: Array<{
      day: string;
      count: number;
    }>;
  };
}

// Configuração da API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const ADMIN_API_BASE = `${API_BASE_URL}/admin/api/v1`;

// Classe para gerenciar requisições à API
class AdminAPIClient {
  private baseURL: string;
  private token: string | null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('admin_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config: RequestInit = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        if (response.status === 401) {
          // Token expirado ou inválido
          localStorage.removeItem('admin_token');
          throw new Error('Sessão expirada. Faça login novamente.');
        }
        
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Erro ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro na requisição à API administrativa:', error);
      throw error;
    }
  }

  // Métricas e Monitoramento
  async getMonitoringOverview(): Promise<{ metrics: AdminMetrics; alerts: AdminAlert[] }> {
    return this.request<{ metrics: AdminMetrics; alerts: AdminAlert[] }>('/monitoring/overview');
  }

  async getSystemAlerts(): Promise<{ alerts: AdminAlert[]; total: number; unacknowledged: number }> {
    return this.request<{ alerts: AdminAlert[]; total: number; unacknowledged: number }>('/monitoring/alerts');
  }

  // Gestão de Usuários
  async getUsers(params?: {
    page?: number;
    per_page?: number;
    status?: string;
    role?: string;
    search?: string;
  }): Promise<{
    users: AdminUser[];
    pagination: {
      page: number;
      per_page: number;
      total: number;
      pages: number;
    };
  }> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const query = searchParams.toString();
    const endpoint = query ? `/users?${query}` : '/users';
    
    return this.request(endpoint);
  }

  async getUserDetails(userId: string): Promise<AdminUser> {
    return this.request<AdminUser>(`/users/${userId}`);
  }

  async updateUserStatus(userId: string, status: string, reason?: string): Promise<{
    success: boolean;
    message: string;
    data: {
      old_status: string;
      new_status: string;
    };
  }> {
    return this.request(`/users/${userId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status, reason }),
    });
  }

  // Configuração do Sistema
  async getSystemConfig(): Promise<AdminSystemConfig> {
    return this.request<AdminSystemConfig>('/system/config');
  }

  async updateSystemConfig(config: Partial<AdminSystemConfig>): Promise<{
    success: boolean;
    message: string;
    data: AdminSystemConfig;
  }> {
    return this.request('/system/config', {
      method: 'PUT',
      body: JSON.stringify(config),
    });
  }

  // Relatórios
  async getUsersReport(): Promise<AdminReport['users']> {
    return this.request<AdminReport['users']>('/reports/users');
  }

  async getExecutionsReport(): Promise<AdminReport['executions']> {
    return this.request<AdminReport['executions']>('/reports/executions');
  }

  // Health Check
  async healthCheck(): Promise<{
    status: string;
    service: string;
    version: string;
    timestamp: string;
    endpoints: string[];
  }> {
    return this.request('/health');
  }
}

// Instância global do cliente API
const adminAPIClient = new AdminAPIClient(ADMIN_API_BASE);

// Hook para métricas e monitoramento
export const useAdminMetrics = () => {
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [alerts, setAlerts] = useState<AdminAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await adminAPIClient.getMonitoringOverview();
      setMetrics(data.metrics);
      setAlerts(data.alerts);
      setLastUpdate(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar métricas');
      console.error('Erro ao carregar métricas administrativas:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const acknowledgeAlert = useCallback(async (alertId: string) => {
    try {
      // Em produção, implementar endpoint para reconhecer alerta
      setAlerts(prev => 
        prev.map(alert => 
          alert.id === alertId 
            ? { ...alert, isAcknowledged: true }
            : alert
        )
      );
    } catch (err) {
      console.error('Erro ao reconhecer alerta:', err);
    }
  }, []);

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
    if (!metrics) return 'unknown';
    
    const { cpu_usage, memory_usage, disk_usage, error_rate } = metrics.system;
    
    if (cpu_usage > 90 || memory_usage > 90 || disk_usage > 90 || error_rate > 5) {
      return 'critical';
    } else if (cpu_usage > 80 || memory_usage > 80 || disk_usage > 80 || error_rate > 2) {
      return 'warning';
    } else {
      return 'healthy';
    }
  }, [metrics]);

  return {
    metrics,
    alerts,
    loading,
    error,
    lastUpdate,
    criticalAlerts,
    unacknowledgedAlerts,
    systemHealth,
    fetchMetrics,
    acknowledgeAlert,
  };
};

// Hook para gestão de usuários
export const useAdminUsers = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = useCallback(async (params?: {
    page?: number;
    per_page?: number;
    status?: string;
    role?: string;
    search?: string;
  }) => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await adminAPIClient.getUsers(params);
      setUsers(data.users);
      setPagination(data.pagination);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar usuários');
      console.error('Erro ao carregar usuários:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateUserStatus = useCallback(async (userId: string, status: string, reason?: string) => {
    try {
      const result = await adminAPIClient.updateUserStatus(userId, status, reason);
      
      // Atualizar usuário na lista
      setUsers(prev => 
        prev.map(user => 
          user.id === userId 
            ? { ...user, status: status as any }
            : user
        )
      );
      
      return result;
    } catch (err) {
      console.error('Erro ao atualizar status do usuário:', err);
      throw err;
    }
  }, []);

  return {
    users,
    pagination,
    loading,
    error,
    fetchUsers,
    updateUserStatus,
  };
};

// Hook para configuração do sistema
export const useAdminSystemConfig = () => {
  const [config, setConfig] = useState<AdminSystemConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchConfig = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await adminAPIClient.getSystemConfig();
      setConfig(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar configurações');
      console.error('Erro ao carregar configurações do sistema:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateConfig = useCallback(async (newConfig: Partial<AdminSystemConfig>) => {
    try {
      const result = await adminAPIClient.updateSystemConfig(newConfig);
      setConfig(result.data);
      return result;
    } catch (err) {
      console.error('Erro ao atualizar configurações:', err);
      throw err;
    }
  }, []);

  return {
    config,
    loading,
    error,
    fetchConfig,
    updateConfig,
  };
};

// Hook para relatórios
export const useAdminReports = () => {
  const [usersReport, setUsersReport] = useState<AdminReport['users'] | null>(null);
  const [executionsReport, setExecutionsReport] = useState<AdminReport['executions'] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUsersReport = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await adminAPIClient.getUsersReport();
      setUsersReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar relatório de usuários');
      console.error('Erro ao carregar relatório de usuários:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchExecutionsReport = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await adminAPIClient.getExecutionsReport();
      setExecutionsReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar relatório de execuções');
      console.error('Erro ao carregar relatório de execuções:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    usersReport,
    executionsReport,
    loading,
    error,
    fetchUsersReport,
    fetchExecutionsReport,
  };
};

// Hook para health check
export const useAdminHealthCheck = () => {
  const [health, setHealth] = useState<{
    status: string;
    service: string;
    version: string;
    timestamp: string;
    endpoints: string[];
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await adminAPIClient.healthCheck();
      setHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao verificar saúde do sistema');
      console.error('Erro ao verificar saúde do sistema:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    health,
    loading,
    error,
    checkHealth,
  };
};

// Hook principal para administração
export const useAdminAPI = () => {
  const metrics = useAdminMetrics();
  const users = useAdminUsers();
  const systemConfig = useAdminSystemConfig();
  const reports = useAdminReports();
  const healthCheck = useAdminHealthCheck();

  return {
    metrics,
    users,
    systemConfig,
    reports,
    healthCheck,
  };
}; 
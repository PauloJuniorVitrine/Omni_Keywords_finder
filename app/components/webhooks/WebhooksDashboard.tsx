/**
 * WebhooksDashboard.tsx
 * 
 * Dashboard de webhooks para Omni Keywords Finder
 * 
 * Tracing ID: UI_ENTERPRISE_CHECKLIST_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 11.1
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useEffect, useCallback } from 'react';
import { cn } from '../../utils/cn';

// Types
export interface WebhookEvent {
  id: string;
  name: string;
  description: string;
  category: 'execution' | 'nichos' | 'categorias' | 'system' | 'user';
  enabled: boolean;
}

export interface WebhookEndpoint {
  id: string;
  name: string;
  url: string;
  events: string[];
  status: 'active' | 'inactive' | 'error' | 'testing';
  lastDelivery?: {
    timestamp: Date;
    status: 'success' | 'failed' | 'pending';
    responseTime?: number;
    statusCode?: number;
    error?: string;
  };
  deliveryStats: {
    total: number;
    successful: number;
    failed: number;
    successRate: number;
  };
  security: {
    secret?: string;
    headers?: Record<string, string>;
    sslVerified: boolean;
  };
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
}

export interface WebhooksDashboardProps {
  webhooks?: WebhookEndpoint[];
  events?: WebhookEvent[];
  onWebhookCreate?: (webhook: Partial<WebhookEndpoint>) => void;
  onWebhookUpdate?: (id: string, updates: Partial<WebhookEndpoint>) => void;
  onWebhookDelete?: (id: string) => void;
  onWebhookTest?: (id: string) => void;
  onWebhookToggle?: (id: string, enabled: boolean) => void;
  className?: string;
  loading?: boolean;
}

// Webhook Status Badge
const WebhookStatusBadge: React.FC<{ status: WebhookEndpoint['status'] }> = ({ status }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'active':
        return {
          label: 'Ativo',
          classes: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300',
          icon: '●'
        };
      case 'inactive':
        return {
          label: 'Inativo',
          classes: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
          icon: '○'
        };
      case 'error':
        return {
          label: 'Erro',
          classes: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300',
          icon: '✗'
        };
      case 'testing':
        return {
          label: 'Testando',
          classes: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300',
          icon: '⟳'
        };
      default:
        return {
          label: 'Desconhecido',
          classes: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
          icon: '?'
        };
    }
  };

  const config = getStatusConfig();

  return (
    <span className={cn(
      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
      config.classes
    )}>
      <span className="mr-1">{config.icon}</span>
      {config.label}
    </span>
  );
};

// Delivery Status Badge
const DeliveryStatusBadge: React.FC<{ status: 'success' | 'failed' | 'pending' }> = ({ status }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'success':
        return {
          label: 'Sucesso',
          classes: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
        };
      case 'failed':
        return {
          label: 'Falhou',
          classes: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300'
        };
      case 'pending':
        return {
          label: 'Pendente',
          classes: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300'
        };
      default:
        return {
          label: 'Desconhecido',
          classes: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
        };
    }
  };

  const config = getStatusConfig();

  return (
    <span className={cn(
      'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
      config.classes
    )}>
      {config.label}
    </span>
  );
};

// Webhook Card Component
const WebhookCard: React.FC<{
  webhook: WebhookEndpoint;
  onEdit?: (webhook: WebhookEndpoint) => void;
  onDelete?: (id: string) => void;
  onTest?: (id: string) => void;
  onToggle?: (id: string, enabled: boolean) => void;
}> = ({ webhook, onEdit, onDelete, onTest, onToggle }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 95) return 'text-green-600 dark:text-green-400';
    if (rate >= 80) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
              <span className="text-blue-600 dark:text-blue-400 text-lg">🔗</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {webhook.name}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {webhook.url}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <WebhookStatusBadge status={webhook.status} />
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <span className="text-sm">{isExpanded ? '▼' : '▶'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="p-4 space-y-4">
          {/* Events */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
              Eventos
            </h4>
            <div className="flex flex-wrap gap-1">
              {webhook.events.map((event) => (
                <span
                  key={event}
                  className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded"
                >
                  {event}
                </span>
              ))}
            </div>
          </div>

          {/* Delivery Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                Estatísticas de Entrega
              </h4>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Total:</span>
                  <span className="text-gray-900 dark:text-white">{webhook.deliveryStats.total}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Sucessos:</span>
                  <span className="text-green-600 dark:text-green-400">{webhook.deliveryStats.successful}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Falhas:</span>
                  <span className="text-red-600 dark:text-red-400">{webhook.deliveryStats.failed}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Taxa de Sucesso:</span>
                  <span className={cn('font-medium', getSuccessRateColor(webhook.deliveryStats.successRate))}>
                    {webhook.deliveryStats.successRate.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Last Delivery */}
            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                Última Entrega
              </h4>
              {webhook.lastDelivery ? (
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <DeliveryStatusBadge status={webhook.lastDelivery.status} />
                    {webhook.lastDelivery.responseTime && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {webhook.lastDelivery.responseTime}ms
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    {formatDate(webhook.lastDelivery.timestamp)}
                  </div>
                  {webhook.lastDelivery.error && (
                    <div className="text-xs text-red-600 dark:text-red-400">
                      {webhook.lastDelivery.error}
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Nenhuma entrega ainda
                </div>
              )}
            </div>
          </div>

          {/* Security Info */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
              Segurança
            </h4>
            <div className="space-y-1">
              <div className="flex items-center space-x-2 text-sm">
                <span className={cn(
                  'w-2 h-2 rounded-full',
                  webhook.security.sslVerified 
                    ? 'bg-green-500' 
                    : 'bg-red-500'
                )} />
                <span className="text-gray-600 dark:text-gray-400">
                  SSL: {webhook.security.sslVerified ? 'Verificado' : 'Não verificado'}
                </span>
              </div>
              {webhook.security.secret && (
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Secret configurado
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => onTest?.(webhook.id)}
                className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Testar
              </button>
              <button
                onClick={() => onEdit?.(webhook)}
                className="px-3 py-1 text-sm text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Editar
              </button>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => onToggle?.(webhook.id, webhook.status === 'active')}
                className={cn(
                  'px-3 py-1 text-sm rounded',
                  webhook.status === 'active'
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : 'bg-green-600 text-white hover:bg-green-700'
                )}
              >
                {webhook.status === 'active' ? 'Desativar' : 'Ativar'}
              </button>
              <button
                onClick={() => onDelete?.(webhook.id)}
                className="px-3 py-1 text-sm text-red-600 dark:text-red-400 border border-red-300 dark:border-red-600 rounded hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                Excluir
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Main Dashboard Component
export const WebhooksDashboard: React.FC<WebhooksDashboardProps> = ({
  webhooks = [],
  events = [],
  onWebhookCreate,
  onWebhookUpdate,
  onWebhookDelete,
  onWebhookTest,
  onWebhookToggle,
  className = '',
  loading = false,
}) => {
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'status' | 'createdAt' | 'successRate'>('createdAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Filter and sort webhooks
  const filteredWebhooks = webhooks
    .filter(webhook => {
      const matchesStatus = filterStatus === 'all' || webhook.status === filterStatus;
      const matchesSearch = webhook.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           webhook.url.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesStatus && matchesSearch;
    })
    .sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'status':
          comparison = a.status.localeCompare(b.status);
          break;
        case 'createdAt':
          comparison = a.createdAt.getTime() - b.createdAt.getTime();
          break;
        case 'successRate':
          comparison = a.deliveryStats.successRate - b.deliveryStats.successRate;
          break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  // Statistics
  const stats = {
    total: webhooks.length,
    active: webhooks.filter(w => w.status === 'active').length,
    inactive: webhooks.filter(w => w.status === 'inactive').length,
    error: webhooks.filter(w => w.status === 'error').length,
    avgSuccessRate: webhooks.length > 0 
      ? webhooks.reduce((sum, w) => sum + w.deliveryStats.successRate, 0) / webhooks.length 
      : 0,
  };

  if (loading) {
    return (
      <div className={cn('space-y-6', className)}>
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Webhooks
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gerencie os webhooks para integrações externas
          </p>
        </div>
        
        <button
          onClick={() => onWebhookCreate?.({})}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Novo Webhook
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
              <span className="text-blue-600 dark:text-blue-400">🔗</span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{stats.total}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
              <span className="text-green-600 dark:text-green-400">●</span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Ativos</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{stats.active}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-red-100 dark:bg-red-900/20 rounded-lg flex items-center justify-center">
              <span className="text-red-600 dark:text-red-400">✗</span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Com Erro</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{stats.error}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg flex items-center justify-center">
              <span className="text-yellow-600 dark:text-yellow-400">📊</span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Taxa Média</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                {stats.avgSuccessRate.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Buscar webhooks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="all">Todos os status</option>
              <option value="active">Ativos</option>
              <option value="inactive">Inativos</option>
              <option value="error">Com erro</option>
              <option value="testing">Testando</option>
            </select>
            
            <select
              value={`${sortBy}-${sortOrder}`}
              onChange={(e) => {
                const [field, order] = e.target.value.split('-');
                setSortBy(field as any);
                setSortOrder(order as any);
              }}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="createdAt-desc">Mais recentes</option>
              <option value="createdAt-asc">Mais antigos</option>
              <option value="name-asc">Nome A-Z</option>
              <option value="name-desc">Nome Z-A</option>
              <option value="successRate-desc">Melhor taxa</option>
              <option value="successRate-asc">Pior taxa</option>
            </select>
          </div>
        </div>
      </div>

      {/* Webhooks List */}
      <div className="space-y-4">
        {filteredWebhooks.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-gray-400 text-2xl">🔗</span>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Nenhum webhook encontrado
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {searchTerm || filterStatus !== 'all' 
                ? 'Tente ajustar os filtros de busca'
                : 'Crie seu primeiro webhook para começar'
              }
            </p>
            {!searchTerm && filterStatus === 'all' && (
              <button
                onClick={() => onWebhookCreate?.({})}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Criar Webhook
              </button>
            )}
          </div>
        ) : (
          filteredWebhooks.map((webhook) => (
            <WebhookCard
              key={webhook.id}
              webhook={webhook}
              onEdit={onWebhookUpdate ? (webhook) => onWebhookUpdate(webhook.id, webhook) : undefined}
              onDelete={onWebhookDelete}
              onTest={onWebhookTest}
              onToggle={onWebhookToggle}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default WebhooksDashboard; 
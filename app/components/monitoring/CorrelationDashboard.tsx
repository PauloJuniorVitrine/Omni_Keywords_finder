/**
 * Dashboard de Correlação - Omni Keywords Finder
 * =============================================
 * 
 * Dashboard enterprise para correlação de eventos de observabilidade:
 * - Correlação de logs, métricas e traces
 * - Análise de dependências
 * - Root cause analysis
 * - Timeline de eventos
 * - Alertas correlacionados
 * 
 * Prompt: CHECKLIST_SISTEMA_PREENCHIMENTO_LACUNAS.md - Fase 3
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-27
 * Versão: 1.0.0
 * Tracing ID: CORRELATION_DASHBOARD_014
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useApi } from '../../hooks/useApi';

interface CorrelationEvent {
  event_id: string;
  event_type: 'log' | 'metric' | 'trace' | 'alert' | 'business' | 'security' | 'performance';
  correlation_id: string;
  timestamp: string;
  severity: 'debug' | 'info' | 'warning' | 'error' | 'critical';
  source: string;
  data: Record<string, any>;
  tags: Record<string, string>;
}

interface CorrelationContext {
  correlation_id: string;
  user_id?: string;
  session_id?: string;
  service_name?: string;
  operation_name?: string;
  start_time: string;
  end_time?: string;
  duration?: number;
}

interface CorrelationDashboardData {
  correlation_id: string;
  context: CorrelationContext;
  events: CorrelationEvent[];
  dependencies: Array<{
    service: string;
    operation: string;
    duration: number;
    status: string;
  }>;
  alerts: Array<{
    id: string;
    severity: string;
    message: string;
    timestamp: string;
  }>;
  metrics: Record<string, {
    current: number;
    avg: number;
    min: number;
    max: number;
    trend: 'up' | 'down' | 'stable';
  }>;
}

interface CorrelationDashboardProps {
  correlationId?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export const CorrelationDashboard: React.FC<CorrelationDashboardProps> = ({
  correlationId,
  autoRefresh = true,
  refreshInterval = 30000
}) => {
  const [selectedCorrelationId, setSelectedCorrelationId] = useState<string | undefined>(correlationId);
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('1h');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterSource, setFilterSource] = useState<string>('all');
  const [showTimeline, setShowTimeline] = useState(true);
  const [showDependencies, setShowDependencies] = useState(true);
  const [showAlerts, setShowAlerts] = useState(true);

  // API hooks
  const { data: dashboardData, loading, error, refetch } = useApi<CorrelationDashboardData>(
    selectedCorrelationId ? `/api/observability/correlation/${selectedCorrelationId}` : null,
    {
      params: {
        time_range: timeRange,
        severity: filterSeverity !== 'all' ? filterSeverity : undefined,
        source: filterSource !== 'all' ? filterSource : undefined
      },
      polling: autoRefresh ? refreshInterval : false
    }
  );

  const { data: correlationIds } = useApi<string[]>(
    '/api/observability/correlations',
    {
      params: { time_range: timeRange },
      polling: autoRefresh ? refreshInterval : false
    }
  );

  // Auto-refresh effect
  useEffect(() => {
    if (autoRefresh && selectedCorrelationId) {
      const interval = setInterval(() => {
        refetch();
      }, refreshInterval);

      return () => clearInterval(interval);
    }
  }, [autoRefresh, selectedCorrelationId, refreshInterval, refetch]);

  // Filter events
  const filteredEvents = useCallback(() => {
    if (!dashboardData?.events) return [];

    return dashboardData.events.filter(event => {
      const severityMatch = filterSeverity === 'all' || event.severity === filterSeverity;
      const sourceMatch = filterSource === 'all' || event.source === filterSource;
      return severityMatch && sourceMatch;
    });
  }, [dashboardData?.events, filterSeverity, filterSource]);

  // Group events by type
  const eventsByType = useCallback(() => {
    const events = filteredEvents();
    return events.reduce((acc, event) => {
      if (!acc[event.event_type]) {
        acc[event.event_type] = [];
      }
      acc[event.event_type].push(event);
      return acc;
    }, {} as Record<string, CorrelationEvent[]>);
  }, [filteredEvents]);

  // Calculate timeline data
  const timelineData = useCallback(() => {
    const events = filteredEvents();
    return events
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      .map(event => ({
        ...event,
        time: new Date(event.timestamp).getTime()
      }));
  }, [filteredEvents]);

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#dc3545';
      case 'error': return '#fd7e14';
      case 'warning': return '#ffc107';
      case 'info': return '#17a2b8';
      case 'debug': return '#6c757d';
      default: return '#6c757d';
    }
  };

  // Get event type icon
  const getEventTypeIcon = (eventType: string) => {
    switch (eventType) {
      case 'log': return '📝';
      case 'metric': return '📊';
      case 'trace': return '🔍';
      case 'alert': return '🚨';
      case 'business': return '💼';
      case 'security': return '🔒';
      case 'performance': return '⚡';
      default: return '📋';
    }
  };

  if (loading && !dashboardData) {
    return (
      <div className="correlation-dashboard loading">
        <div className="loading-spinner">🔄</div>
        <p>Carregando dados de correlação...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="correlation-dashboard error">
        <div className="error-icon">❌</div>
        <h3>Erro ao carregar dashboard</h3>
        <p>{error.message}</p>
        <button onClick={refetch} className="retry-button">
          Tentar novamente
        </button>
      </div>
    );
  }

  return (
    <div className="correlation-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h2>Dashboard de Correlação</h2>
        <div className="header-controls">
          <select
            value={selectedCorrelationId || ''}
            onChange={(e) => setSelectedCorrelationId(e.target.value || undefined)}
            className="correlation-select"
          >
            <option value="">Selecionar Correlation ID</option>
            {correlationIds?.map(id => (
              <option key={id} value={id}>{id}</option>
            ))}
          </select>
          
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as any)}
            className="time-range-select"
          >
            <option value="1h">Última hora</option>
            <option value="6h">Últimas 6 horas</option>
            <option value="24h">Últimas 24 horas</option>
            <option value="7d">Últimos 7 dias</option>
          </select>
          
          <button
            onClick={refetch}
            className="refresh-button"
            disabled={loading}
          >
            {loading ? '🔄' : '🔄'} Atualizar
          </button>
        </div>
      </div>

      {selectedCorrelationId && dashboardData && (
        <>
          {/* Correlation Context */}
          <div className="correlation-context">
            <h3>Contexto de Correlação</h3>
            <div className="context-grid">
              <div className="context-item">
                <label>Correlation ID:</label>
                <span className="correlation-id">{dashboardData.correlation_id}</span>
              </div>
              {dashboardData.context.user_id && (
                <div className="context-item">
                  <label>Usuário:</label>
                  <span>{dashboardData.context.user_id}</span>
                </div>
              )}
              {dashboardData.context.service_name && (
                <div className="context-item">
                  <label>Serviço:</label>
                  <span>{dashboardData.context.service_name}</span>
                </div>
              )}
              {dashboardData.context.operation_name && (
                <div className="context-item">
                  <label>Operação:</label>
                  <span>{dashboardData.context.operation_name}</span>
                </div>
              )}
              {dashboardData.context.duration && (
                <div className="context-item">
                  <label>Duração:</label>
                  <span>{dashboardData.context.duration.toFixed(2)}s</span>
                </div>
              )}
            </div>
          </div>

          {/* Filters */}
          <div className="dashboard-filters">
            <div className="filter-group">
              <label>Severidade:</label>
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
              >
                <option value="all">Todas</option>
                <option value="critical">Crítica</option>
                <option value="error">Erro</option>
                <option value="warning">Aviso</option>
                <option value="info">Info</option>
                <option value="debug">Debug</option>
              </select>
            </div>
            
            <div className="filter-group">
              <label>Fonte:</label>
              <select
                value={filterSource}
                onChange={(e) => setFilterSource(e.target.value)}
              >
                <option value="all">Todas</option>
                <option value="api">API</option>
                <option value="database">Database</option>
                <option value="cache">Cache</option>
                <option value="external">External</option>
                <option value="system">System</option>
              </select>
            </div>
            
            <div className="view-controls">
              <label>
                <input
                  type="checkbox"
                  checked={showTimeline}
                  onChange={(e) => setShowTimeline(e.target.checked)}
                />
                Timeline
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={showDependencies}
                  onChange={(e) => setShowDependencies(e.target.checked)}
                />
                Dependências
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={showAlerts}
                  onChange={(e) => setShowAlerts(e.target.checked)}
                />
                Alertas
              </label>
            </div>
          </div>

          {/* Metrics Summary */}
          <div className="metrics-summary">
            <h3>Métricas</h3>
            <div className="metrics-grid">
              {Object.entries(dashboardData.metrics).map(([name, metric]) => (
                <div key={name} className="metric-card">
                  <h4>{name}</h4>
                  <div className="metric-value">{metric.current.toFixed(2)}</div>
                  <div className="metric-stats">
                    <span>Média: {metric.avg.toFixed(2)}</span>
                    <span>Min: {metric.min.toFixed(2)}</span>
                    <span>Max: {metric.max.toFixed(2)}</span>
                  </div>
                  <div className={`metric-trend ${metric.trend}`}>
                    {metric.trend === 'up' ? '📈' : metric.trend === 'down' ? '📉' : '➡️'}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Timeline */}
          {showTimeline && (
            <div className="timeline-section">
              <h3>Timeline de Eventos</h3>
              <div className="timeline">
                {timelineData().map((event, index) => (
                  <div key={event.event_id} className="timeline-item">
                    <div className="timeline-marker" style={{ backgroundColor: getSeverityColor(event.severity) }}>
                      {getEventTypeIcon(event.event_type)}
                    </div>
                    <div className="timeline-content">
                      <div className="event-header">
                        <span className="event-type">{event.event_type}</span>
                        <span className="event-time">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </span>
                        <span className="event-source">{event.source}</span>
                      </div>
                      <div className="event-data">
                        <pre>{JSON.stringify(event.data, null, 2)}</pre>
                      </div>
                      {Object.keys(event.tags).length > 0 && (
                        <div className="event-tags">
                          {Object.entries(event.tags).map(([key, value]) => (
                            <span key={key} className="tag">
                              {key}: {value}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Dependencies */}
          {showDependencies && dashboardData.dependencies.length > 0 && (
            <div className="dependencies-section">
              <h3>Dependências de Serviços</h3>
              <div className="dependencies-grid">
                {dashboardData.dependencies.map((dep, index) => (
                  <div key={index} className="dependency-card">
                    <div className="dependency-service">{dep.service}</div>
                    <div className="dependency-operation">{dep.operation}</div>
                    <div className="dependency-duration">{dep.duration.toFixed(2)}s</div>
                    <div className={`dependency-status ${dep.status}`}>
                      {dep.status === 'success' ? '✅' : '❌'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Alerts */}
          {showAlerts && dashboardData.alerts.length > 0 && (
            <div className="alerts-section">
              <h3>Alertas Correlacionados</h3>
              <div className="alerts-list">
                {dashboardData.alerts.map(alert => (
                  <div key={alert.id} className={`alert-item ${alert.severity}`}>
                    <div className="alert-header">
                      <span className="alert-severity">{alert.severity}</span>
                      <span className="alert-time">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="alert-message">{alert.message}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Events by Type */}
          <div className="events-summary">
            <h3>Resumo por Tipo</h3>
            <div className="events-grid">
              {Object.entries(eventsByType()).map(([type, events]) => (
                <div key={type} className="event-type-card">
                  <div className="event-type-header">
                    <span className="event-type-icon">{getEventTypeIcon(type)}</span>
                    <span className="event-type-name">{type}</span>
                    <span className="event-count">{events.length}</span>
                  </div>
                  <div className="event-type-breakdown">
                    {Object.entries(
                      events.reduce((acc, event) => {
                        acc[event.severity] = (acc[event.severity] || 0) + 1;
                        return acc;
                      }, {} as Record<string, number>)
                    ).map(([severity, count]) => (
                      <div key={severity} className="severity-breakdown">
                        <span className="severity-dot" style={{ backgroundColor: getSeverityColor(severity) }}></span>
                        <span>{severity}: {count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {!selectedCorrelationId && (
        <div className="no-correlation-selected">
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <h3>Nenhuma correlação selecionada</h3>
            <p>Selecione um Correlation ID para visualizar os dados de correlação</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Estilos CSS
const correlationDashboardStyles = `
  .correlation-dashboard {
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #dee2e6;
  }

  .dashboard-header h2 {
    margin: 0;
    color: #333;
    font-size: 24px;
  }

  .header-controls {
    display: flex;
    gap: 10px;
    align-items: center;
  }

  .correlation-select,
  .time-range-select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    min-width: 200px;
  }

  .refresh-button {
    padding: 8px 16px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
  }

  .refresh-button:disabled {
    background: #6c757d;
    cursor: not-allowed;
  }

  .correlation-context {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .correlation-context h3 {
    margin: 0 0 15px 0;
    color: #333;
  }

  .context-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
  }

  .context-item {
    display: flex;
    flex-direction: column;
  }

  .context-item label {
    font-weight: bold;
    color: #666;
    font-size: 12px;
    text-transform: uppercase;
    margin-bottom: 5px;
  }

  .context-item span {
    color: #333;
    font-size: 14px;
  }

  .correlation-id {
    font-family: monospace;
    background: #f8f9fa;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
  }

  .dashboard-filters {
    display: flex;
    gap: 20px;
    align-items: center;
    margin-bottom: 20px;
    padding: 15px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .filter-group label {
    font-size: 12px;
    font-weight: bold;
    color: #666;
  }

  .filter-group select {
    padding: 6px 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }

  .view-controls {
    display: flex;
    gap: 15px;
  }

  .view-controls label {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 14px;
    cursor: pointer;
  }

  .metrics-summary {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .metrics-summary h3 {
    margin: 0 0 15px 0;
    color: #333;
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
  }

  .metric-card {
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #007bff;
  }

  .metric-card h4 {
    margin: 0 0 10px 0;
    color: #333;
    font-size: 14px;
  }

  .metric-value {
    font-size: 24px;
    font-weight: bold;
    color: #007bff;
    margin-bottom: 10px;
  }

  .metric-stats {
    display: flex;
    flex-direction: column;
    gap: 5px;
    font-size: 12px;
    color: #666;
  }

  .metric-trend {
    margin-top: 10px;
    font-size: 16px;
  }

  .timeline-section {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .timeline-section h3 {
    margin: 0 0 20px 0;
    color: #333;
  }

  .timeline {
    position: relative;
    padding-left: 30px;
  }

  .timeline::before {
    content: '';
    position: absolute;
    left: 15px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #dee2e6;
  }

  .timeline-item {
    position: relative;
    margin-bottom: 20px;
  }

  .timeline-marker {
    position: absolute;
    left: -22px;
    top: 0;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 12px;
  }

  .timeline-content {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #007bff;
  }

  .event-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }

  .event-type {
    font-weight: bold;
    color: #333;
    text-transform: uppercase;
    font-size: 12px;
  }

  .event-time {
    color: #666;
    font-size: 12px;
  }

  .event-source {
    color: #007bff;
    font-size: 12px;
    font-weight: bold;
  }

  .event-data {
    margin-bottom: 10px;
  }

  .event-data pre {
    background: #fff;
    padding: 10px;
    border-radius: 4px;
    font-size: 12px;
    overflow-x: auto;
    margin: 0;
  }

  .event-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }

  .tag {
    background: #e9ecef;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    color: #666;
  }

  .dependencies-section,
  .alerts-section {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .dependencies-section h3,
  .alerts-section h3 {
    margin: 0 0 15px 0;
    color: #333;
  }

  .dependencies-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
  }

  .dependency-card {
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #28a745;
  }

  .dependency-service {
    font-weight: bold;
    color: #333;
    margin-bottom: 5px;
  }

  .dependency-operation {
    color: #666;
    font-size: 14px;
    margin-bottom: 5px;
  }

  .dependency-duration {
    color: #007bff;
    font-weight: bold;
  }

  .dependency-status {
    margin-top: 10px;
    font-size: 16px;
  }

  .alerts-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .alert-item {
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid;
  }

  .alert-item.critical {
    background: #f8d7da;
    border-left-color: #dc3545;
  }

  .alert-item.error {
    background: #fff3cd;
    border-left-color: #fd7e14;
  }

  .alert-item.warning {
    background: #fff8e1;
    border-left-color: #ffc107;
  }

  .alert-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 5px;
  }

  .alert-severity {
    font-weight: bold;
    text-transform: uppercase;
    font-size: 12px;
  }

  .alert-time {
    color: #666;
    font-size: 12px;
  }

  .alert-message {
    color: #333;
    font-size: 14px;
  }

  .events-summary {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .events-summary h3 {
    margin: 0 0 15px 0;
    color: #333;
  }

  .events-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
  }

  .event-type-card {
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #007bff;
  }

  .event-type-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }

  .event-type-icon {
    font-size: 16px;
  }

  .event-type-name {
    font-weight: bold;
    color: #333;
    text-transform: uppercase;
    font-size: 12px;
  }

  .event-count {
    background: #007bff;
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: bold;
  }

  .event-type-breakdown {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .severity-breakdown {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 12px;
    color: #666;
  }

  .severity-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .no-correlation-selected {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
  }

  .empty-state {
    text-align: center;
    color: #666;
  }

  .empty-icon {
    font-size: 48px;
    margin-bottom: 20px;
  }

  .empty-state h3 {
    margin: 0 0 10px 0;
    color: #333;
  }

  .loading,
  .error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    text-align: center;
  }

  .loading-spinner {
    font-size: 48px;
    margin-bottom: 20px;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .error-icon {
    font-size: 48px;
    margin-bottom: 20px;
  }

  .retry-button {
    padding: 10px 20px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    margin-top: 15px;
  }
`;

// Adicionar estilos ao documento
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = correlationDashboardStyles;
  document.head.appendChild(style);
}

export default CorrelationDashboard; 
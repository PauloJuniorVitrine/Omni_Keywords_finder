/**
 * Health Status Dashboard Component
 * Tracing ID: FINE_TUNING_IMPLEMENTATION_20250127_001
 * Created: 2025-01-27
 * Version: 1.0
 * 
 * This component provides a comprehensive health status dashboard with visual indicators,
 * automatic alerts, and availability history for the Omni Keywords Finder system.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Activity, 
  Database, 
  Server, 
  Globe, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Clock,
  RefreshCw,
  TrendingUp,
  Cpu,
  Memory,
  HardDrive,
  Network
} from 'lucide-react';

// Types
interface HealthCheckResult {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  message: string;
  details: Record<string, any>;
  timestamp: string;
  duration: number;
  correlation_id?: string;
}

interface HealthSummary {
  status: string;
  timestamp: string;
  duration_ms: number;
  checks: HealthCheckResult[];
  summary: {
    total_checks: number;
    healthy: number;
    degraded: number;
    unhealthy: number;
    unknown: number;
  };
}

interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  network_io: {
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
  };
  uptime_seconds: number;
  load_average: number[];
  warnings?: string[];
}

interface HealthStatusProps {
  autoRefresh?: boolean;
  refreshInterval?: number;
  showHistory?: boolean;
  compact?: boolean;
}

// Utility functions
const getStatusColor = (status: string): string => {
  switch (status) {
    case 'healthy': return 'bg-green-500';
    case 'degraded': return 'bg-yellow-500';
    case 'unhealthy': return 'bg-red-500';
    case 'unknown': return 'bg-gray-500';
    default: return 'bg-gray-500';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'healthy': return <CheckCircle className="h-4 w-4 text-green-500" />;
    case 'degraded': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    case 'unhealthy': return <XCircle className="h-4 w-4 text-red-500" />;
    case 'unknown': return <Clock className="h-4 w-4 text-gray-500" />;
    default: return <Clock className="h-4 w-4 text-gray-500" />;
  }
};

const formatDuration = (seconds: number): string => {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
  return `${Math.round(seconds / 3600)}h`;
};

const formatBytes = (bytes: number): string => {
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  if (bytes === 0) return '0 B';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
};

const formatUptime = (seconds: number): string => {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (days > 0) return `${days}d ${hours}h ${minutes}m`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
};

export const HealthStatus: React.FC<HealthStatusProps> = ({
  autoRefresh = true,
  refreshInterval = 30000, // 30 seconds
  showHistory = true,
  compact = false
}) => {
  const [healthData, setHealthData] = useState<HealthSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [history, setHistory] = useState<HealthSummary[]>([]);

  // Fetch health data
  const fetchHealthData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/health/detailed', {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data: HealthSummary = await response.json();
      setHealthData(data);
      setLastRefresh(new Date());
      
      // Add to history
      if (showHistory) {
        setHistory(prev => {
          const newHistory = [data, ...prev.slice(0, 9)]; // Keep last 10 entries
          return newHistory;
        });
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch health data');
      console.error('Health check failed:', err);
    } finally {
      setLoading(false);
    }
  }, [showHistory]);

  // Auto-refresh effect
  useEffect(() => {
    fetchHealthData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchHealthData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchHealthData, autoRefresh, refreshInterval]);

  // Calculate overall status
  const overallStatus = healthData?.status || 'unknown';
  const isHealthy = overallStatus === 'healthy';
  const isDegraded = overallStatus === 'degraded';
  const isUnhealthy = overallStatus === 'unhealthy';

  // Get system metrics
  const systemMetrics = healthData?.checks.find(
    check => check.name === 'system_metrics'
  )?.details as SystemMetrics | undefined;

  if (compact) {
    return (
      <Card className="w-full">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center gap-2">
              <Activity className="h-5 w-5" />
              System Health
            </CardTitle>
            <div className="flex items-center gap-2">
              {getStatusIcon(overallStatus)}
              <Badge 
                variant={isHealthy ? 'default' : isDegraded ? 'secondary' : 'destructive'}
                className="text-xs"
              >
                {overallStatus}
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <RefreshCw className="h-4 w-4 animate-spin" />
              Checking health...
            </div>
          ) : error ? (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="text-center">
                  <div className="font-semibold text-green-600">
                    {healthData?.summary.healthy || 0}
                  </div>
                  <div className="text-xs text-muted-foreground">Healthy</div>
                </div>
                <div className="text-center">
                  <div className="font-semibold text-yellow-600">
                    {healthData?.summary.degraded || 0}
                  </div>
                  <div className="text-xs text-muted-foreground">Degraded</div>
                </div>
                <div className="text-center">
                  <div className="font-semibold text-red-600">
                    {healthData?.summary.unhealthy || 0}
                  </div>
                  <div className="text-xs text-muted-foreground">Unhealthy</div>
                </div>
              </div>
              
              {systemMetrics && (
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div className="flex items-center gap-1">
                    <Cpu className="h-3 w-3" />
                    <span>{systemMetrics.cpu_percent.toFixed(1)}%</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Memory className="h-3 w-3" />
                    <span>{systemMetrics.memory_percent.toFixed(1)}%</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <HardDrive className="h-3 w-3" />
                    <span>{systemMetrics.disk_percent.toFixed(1)}%</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Activity className="h-6 w-6" />
            System Health Dashboard
          </h2>
          <p className="text-muted-foreground">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </p>
        </div>
        <Button 
          onClick={fetchHealthData} 
          disabled={loading}
          variant="outline"
          size="sm"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Overall Status Alert */}
      {!loading && !error && (
        <Alert variant={isHealthy ? 'default' : isDegraded ? 'secondary' : 'destructive'}>
          {getStatusIcon(overallStatus)}
          <AlertTitle>
            System Status: {overallStatus.charAt(0).toUpperCase() + overallStatus.slice(1)}
          </AlertTitle>
          <AlertDescription>
            {isHealthy && 'All systems are operating normally.'}
            {isDegraded && 'Some systems are experiencing issues but the service remains available.'}
            {isUnhealthy && 'Critical systems are down. Service may be unavailable.'}
          </AlertDescription>
        </Alert>
      )}

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Health Check Failed</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="details">Details</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
          {showHistory && <TabsTrigger value="history">History</TabsTrigger>}
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Checks</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{healthData?.summary.total_checks || 0}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Healthy</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {healthData?.summary.healthy || 0}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Degraded</CardTitle>
                <AlertTriangle className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">
                  {healthData?.summary.degraded || 0}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Unhealthy</CardTitle>
                <XCircle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {healthData?.summary.unhealthy || 0}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Status Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {healthData?.checks.map((check) => (
              <Card key={check.name} className="relative">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm capitalize">
                      {check.name.replace('_', ' ')}
                    </CardTitle>
                    {getStatusIcon(check.status)}
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-2">{check.message}</p>
                  <div className="flex items-center justify-between text-xs">
                    <span>Duration: {formatDuration(check.duration)}</span>
                    <Badge variant="outline" className="text-xs">
                      {check.status}
                    </Badge>
                  </div>
                </CardContent>
                <div className={`absolute top-0 left-0 w-1 h-full ${getStatusColor(check.status)}`} />
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="details" className="space-y-4">
          {/* Detailed Health Checks */}
          {healthData?.checks.map((check) => (
            <Card key={check.name}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    {check.name === 'database_health' && <Database className="h-5 w-5" />}
                    {check.name === 'redis_health' && <Server className="h-5 w-5" />}
                    {check.name === 'external_services' && <Globe className="h-5 w-5" />}
                    {check.name === 'system_metrics' && <Activity className="h-5 w-5" />}
                    {check.name === 'application_health' && <Server className="h-5 w-5" />}
                    {check.name.charAt(0).toUpperCase() + check.name.slice(1).replace('_', ' ')}
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(check.status)}
                    <Badge variant={check.status === 'healthy' ? 'default' : 'secondary'}>
                      {check.status}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">{check.message}</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold text-sm mb-2">Details</h4>
                    <div className="space-y-1 text-sm">
                      {Object.entries(check.details).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-muted-foreground">
                            {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                          </span>
                          <span className="font-mono">
                            {typeof value === 'number' ? value.toFixed(2) : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-sm mb-2">Timing</h4>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Duration:</span>
                        <span>{formatDuration(check.duration)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Timestamp:</span>
                        <span>{new Date(check.timestamp).toLocaleTimeString()}</span>
                      </div>
                      {check.correlation_id && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Correlation ID:</span>
                          <span className="font-mono text-xs">{check.correlation_id}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="system" className="space-y-4">
          {/* System Metrics */}
          {systemMetrics && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* CPU, Memory, Disk */}
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Cpu className="h-5 w-5" />
                      CPU Usage
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Current Usage</span>
                        <span className="font-semibold">{systemMetrics.cpu_percent.toFixed(1)}%</span>
                      </div>
                      <Progress value={systemMetrics.cpu_percent} className="h-2" />
                      <div className="text-xs text-muted-foreground">
                        Load Average: {systemMetrics.load_average.map(l => l.toFixed(2)).join(', ')}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Memory className="h-5 w-5" />
                      Memory Usage
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Current Usage</span>
                        <span className="font-semibold">{systemMetrics.memory_percent.toFixed(1)}%</span>
                      </div>
                      <Progress value={systemMetrics.memory_percent} className="h-2" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <HardDrive className="h-5 w-5" />
                      Disk Usage
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Current Usage</span>
                        <span className="font-semibold">{systemMetrics.disk_percent.toFixed(1)}%</span>
                      </div>
                      <Progress value={systemMetrics.disk_percent} className="h-2" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Network and Uptime */}
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Network className="h-5 w-5" />
                      Network I/O
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm">
                          <span>Bytes Sent</span>
                          <span className="font-mono">{formatBytes(systemMetrics.network_io.bytes_sent)}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Bytes Received</span>
                          <span className="font-mono">{formatBytes(systemMetrics.network_io.bytes_recv)}</span>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-sm">
                          <span>Packets Sent</span>
                          <span className="font-mono">{systemMetrics.network_io.packets_sent.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Packets Received</span>
                          <span className="font-mono">{systemMetrics.network_io.packets_recv.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="h-5 w-5" />
                      System Uptime
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {formatUptime(systemMetrics.uptime_seconds)}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      System has been running since{' '}
                      {new Date(Date.now() - systemMetrics.uptime_seconds * 1000).toLocaleString()}
                    </p>
                  </CardContent>
                </Card>

                {systemMetrics.warnings && systemMetrics.warnings.length > 0 && (
                  <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertTitle>System Warnings</AlertTitle>
                    <AlertDescription>
                      <ul className="list-disc list-inside space-y-1">
                        {systemMetrics.warnings.map((warning, index) => (
                          <li key={index}>{warning}</li>
                        ))}
                      </ul>
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </div>
          )}
        </TabsContent>

        {showHistory && (
          <TabsContent value="history" className="space-y-4">
            {/* Health History */}
            <div className="space-y-4">
              {history.map((entry, index) => (
                <Card key={index}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm">
                        Health Check - {new Date(entry.timestamp).toLocaleString()}
                      </CardTitle>
                      <Badge variant={entry.status === 'healthy' ? 'default' : 'secondary'}>
                        {entry.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Duration:</span>
                        <div className="font-semibold">{entry.duration_ms}ms</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Healthy:</span>
                        <div className="font-semibold text-green-600">{entry.summary.healthy}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Degraded:</span>
                        <div className="font-semibold text-yellow-600">{entry.summary.degraded}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Unhealthy:</span>
                        <div className="font-semibold text-red-600">{entry.summary.unhealthy}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
};

export default HealthStatus; 
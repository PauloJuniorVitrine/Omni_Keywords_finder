/**
 * Dashboard de Performance em Tempo Real
 * 
 * Prompt: CHECKLIST_SISTEMA_PREENCHIMENTO_LACUNAS.md - Fase 3
 * Ruleset: enterprise_control_layer.yaml
 * Data/Hora: 2024-12-27 15:30:00 UTC
 * Tracing ID: PERFORMANCE_DASHBOARD_001
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Tooltip,
  Badge,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Slider,
  InputAdornment
} from '@mui/material';
import {
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Analytics as AnalyticsIcon,
  Timeline as TimelineIcon,
  Notifications as NotificationsIcon,
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Pause as PauseIcon,
  CloudDownload as CloudDownloadIcon,
  CloudUpload as CloudUploadIcon,
  BugReport as BugReportIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

// Types
interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: string;
  type: 'counter' | 'gauge' | 'histogram' | 'summary';
  labels?: Record<string, string>;
  metadata?: Record<string, any>;
}

interface PerformanceAlert {
  id: string;
  level: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  metric_name: string;
  current_value: number;
  threshold: number;
  timestamp: string;
  resolved: boolean;
  resolved_at?: string;
}

interface CacheStats {
  total_items: number;
  hits: number;
  misses: number;
  evictions: number;
  memory_usage: number;
  avg_response_time: number;
  hit_rate: number;
  l1_cache?: {
    size: number;
    max_size: number;
    memory_usage: number;
  };
  l2_cache?: {
    size: number;
    memory_usage: number;
  };
  access_patterns: Record<string, number>;
}

interface DashboardData {
  timestamp: string;
  metrics: Record<string, {
    count: number;
    min: number;
    max: number;
    mean: number;
    median: number;
    std_dev: number;
    latest: number;
    window_minutes: number;
  }>;
  alerts: PerformanceAlert[];
  thresholds: Record<string, {
    metric_name: string;
    warning_threshold: number;
    error_threshold: number;
    critical_threshold: number;
    enabled: boolean;
  }>;
}

interface PerformanceStats {
  total_processed: number;
  cache_hits: number;
  cache_misses: number;
  cache_hit_rate: number;
  errors: number;
  error_rate: number;
  avg_processing_time: number;
  cache_stats: CacheStats;
  performance_stats: DashboardData;
}

// Mock data for development
const mockPerformanceStats: PerformanceStats = {
  total_processed: 1250,
  cache_hits: 980,
  cache_misses: 270,
  cache_hit_rate: 0.784,
  errors: 15,
  error_rate: 0.012,
  avg_processing_time: 0.045,
  cache_stats: {
    total_items: 150,
    hits: 980,
    misses: 270,
    evictions: 25,
    memory_usage: 45.2,
    avg_response_time: 0.002,
    hit_rate: 0.784,
    l1_cache: {
      size: 120,
      max_size: 1000,
      memory_usage: 12.5
    },
    l2_cache: {
      size: 30,
      memory_usage: 32.7
    },
    access_patterns: {
      'prompt_fill_1_123': 45,
      'prompt_fill_2_456': 32,
      'prompt_fill_3_789': 28
    }
  },
  performance_stats: {
    timestamp: new Date().toISOString(),
    metrics: {
      'response_time_ms': {
        count: 1250,
        min: 10,
        max: 500,
        mean: 45,
        median: 42,
        std_dev: 15.2,
        latest: 38,
        window_minutes: 60
      },
      'memory_usage_percent': {
        count: 1250,
        min: 25,
        max: 85,
        mean: 45.2,
        median: 44,
        std_dev: 8.5,
        latest: 42,
        window_minutes: 60
      },
      'cpu_usage_percent': {
        count: 1250,
        min: 15,
        max: 75,
        mean: 35.8,
        median: 34,
        std_dev: 12.3,
        latest: 32,
        window_minutes: 60
      }
    },
    alerts: [
      {
        id: 'alert_1',
        level: 'warning',
        message: 'Response time above threshold',
        metric_name: 'response_time_ms',
        current_value: 450,
        threshold: 400,
        timestamp: new Date(Date.now() - 300000).toISOString(),
        resolved: false
      }
    ],
    thresholds: {
      'response_time_ms': {
        metric_name: 'response_time_ms',
        warning_threshold: 1000,
        error_threshold: 3000,
        critical_threshold: 5000,
        enabled: true
      }
    }
  }
};

// Mock time series data
const mockTimeSeriesData = Array.from({ length: 24 }, (_, i) => ({
  time: new Date(Date.now() - (23 - i) * 3600000).toLocaleTimeString(),
  response_time: Math.random() * 100 + 20,
  memory_usage: Math.random() * 30 + 30,
  cpu_usage: Math.random() * 40 + 20,
  cache_hit_rate: Math.random() * 0.3 + 0.7
}));

// Main component
const PerformanceDashboard: React.FC = () => {
  const [performanceStats, setPerformanceStats] = useState<PerformanceStats>(mockPerformanceStats);
  const [timeSeriesData, setTimeSeriesData] = useState(mockTimeSeriesData);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30);
  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState<string>('response_time_ms');
  const [expandedAlerts, setExpandedAlerts] = useState<string[]>([]);

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      refreshData();
    }, refreshInterval * 1000);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  const refreshData = () => {
    // Simulate data refresh
    setPerformanceStats(prev => ({
      ...prev,
      total_processed: prev.total_processed + Math.floor(Math.random() * 10),
      cache_hits: prev.cache_hits + Math.floor(Math.random() * 8),
      cache_misses: prev.cache_misses + Math.floor(Math.random() * 2),
      avg_processing_time: prev.avg_processing_time + (Math.random() - 0.5) * 0.01
    }));
  };

  // Memoized calculations
  const performanceScore = useMemo(() => {
    const hitRateScore = performanceStats.cache_hit_rate * 40;
    const errorRateScore = Math.max(0, 30 - performanceStats.error_rate * 1000);
    const responseTimeScore = Math.max(0, 30 - performanceStats.avg_processing_time * 500);
    return Math.round(hitRateScore + errorRateScore + responseTimeScore);
  }, [performanceStats]);

  const systemHealth = useMemo(() => {
    if (performanceScore >= 90) return 'excellent';
    if (performanceScore >= 75) return 'good';
    if (performanceScore >= 60) return 'fair';
    return 'poor';
  }, [performanceScore]);

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'excellent': return 'success';
      case 'good': return 'success';
      case 'fair': return 'warning';
      case 'poor': return 'error';
      default: return 'default';
    }
  };

  const getAlertColor = (level: string) => {
    switch (level) {
      case 'critical': return 'error';
      case 'error': return 'error';
      case 'warning': return 'warning';
      case 'info': return 'info';
      default: return 'default';
    }
  };

  const getAlertIcon = (level: string) => {
    switch (level) {
      case 'critical': return <ErrorIcon />;
      case 'error': return <ErrorIcon />;
      case 'warning': return <WarningIcon />;
      case 'info': return <CheckCircleIcon />;
      default: return <CheckCircleIcon />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Dashboard de Performance
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={refreshData}
          >
            Atualizar
          </Button>
          <Button
            variant="outlined"
            startIcon={<SettingsIcon />}
            onClick={() => setSettingsDialogOpen(true)}
          >
            Configurações
          </Button>
        </Box>
      </Box>

      {/* Performance Overview */}
      <Grid container spacing={3} mb={3}>
        {/* Overall Performance Score */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="h6" color="textSecondary">
                  Performance Score
                </Typography>
                <SpeedIcon color="primary" />
              </Box>
              <Typography variant="h3" color="primary" sx={{ mt: 2 }}>
                {performanceScore}/100
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={performanceScore} 
                sx={{ mt: 1 }}
                color={getHealthColor(systemHealth) as any}
              />
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Status: {systemHealth.toUpperCase()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Cache Hit Rate */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="h6" color="textSecondary">
                  Cache Hit Rate
                </Typography>
                <TrendingUpIcon color="success" />
              </Box>
              <Typography variant="h3" color="success.main" sx={{ mt: 2 }}>
                {(performanceStats.cache_hit_rate * 100).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {performanceStats.cache_hits.toLocaleString()} hits
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Average Response Time */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="h6" color="textSecondary">
                  Response Time
                </Typography>
                <TimelineIcon color="info" />
              </Box>
              <Typography variant="h3" color="info.main" sx={{ mt: 2 }}>
                {(performanceStats.avg_processing_time * 1000).toFixed(1)}ms
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {performanceStats.total_processed.toLocaleString()} requests
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Error Rate */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="h6" color="textSecondary">
                  Error Rate
                </Typography>
                <BugReportIcon color="error" />
              </Box>
              <Typography variant="h3" color="error.main" sx={{ mt: 2 }}>
                {(performanceStats.error_rate * 100).toFixed(2)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {performanceStats.errors} errors
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts and Metrics */}
      <Grid container spacing={3} mb={3}>
        {/* Time Series Chart */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Over Time
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <RechartsTooltip />
                  <Line type="monotone" dataKey="response_time" stroke="#8884d8" name="Response Time (ms)" />
                  <Line type="monotone" dataKey="memory_usage" stroke="#82ca9d" name="Memory Usage (%)" />
                  <Line type="monotone" dataKey="cpu_usage" stroke="#ffc658" name="CPU Usage (%)" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Cache Performance */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cache Performance
              </Typography>
              <Box mb={2}>
                <Typography variant="body2" color="textSecondary">
                  L1 Cache (Memory)
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={(performanceStats.cache_stats.l1_cache?.size || 0) / (performanceStats.cache_stats.l1_cache?.max_size || 1) * 100}
                  sx={{ mt: 1 }}
                />
                <Typography variant="body2">
                  {performanceStats.cache_stats.l1_cache?.size || 0} / {performanceStats.cache_stats.l1_cache?.max_size || 0} items
                </Typography>
              </Box>
              <Box mb={2}>
                <Typography variant="body2" color="textSecondary">
                  Memory Usage
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={performanceStats.cache_stats.memory_usage}
                  sx={{ mt: 1 }}
                  color={performanceStats.cache_stats.memory_usage > 80 ? 'error' : 'primary'}
                />
                <Typography variant="body2">
                  {performanceStats.cache_stats.memory_usage.toFixed(1)} MB
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="textSecondary">
                  Average Response Time
                </Typography>
                <Typography variant="h6">
                  {(performanceStats.cache_stats.avg_response_time * 1000).toFixed(2)} ms
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alerts and Metrics */}
      <Grid container spacing={3}>
        {/* Active Alerts */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Alertas Ativos
              </Typography>
              {performanceStats.performance_stats.alerts.length === 0 ? (
                <Alert severity="success">
                  Nenhum alerta ativo
                </Alert>
              ) : (
                <List>
                  {performanceStats.performance_stats.alerts.map((alert) => (
                    <ListItem key={alert.id} divider>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            {getAlertIcon(alert.level)}
                            <Typography variant="body1">
                              {alert.message}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <Typography variant="body2" color="textSecondary">
                            {new Date(alert.timestamp).toLocaleString()}
                          </Typography>
                        }
                      />
                      <ListItemSecondaryAction>
                        <Chip 
                          label={alert.level.toUpperCase()} 
                          color={getAlertColor(alert.level) as any}
                          size="small"
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Detailed Metrics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Métricas Detalhadas
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Métrica</TableCell>
                      <TableCell align="right">Valor Atual</TableCell>
                      <TableCell align="right">Média</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(performanceStats.performance_stats.metrics).map(([name, metric]) => (
                      <TableRow key={name}>
                        <TableCell>{name}</TableCell>
                        <TableCell align="right">{metric.latest.toFixed(2)}</TableCell>
                        <TableCell align="right">{metric.mean.toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Settings Dialog */}
      <Dialog open={settingsDialogOpen} onClose={() => setSettingsDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Configurações do Dashboard</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                />
              }
              label="Atualização Automática"
            />
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Intervalo de Atualização (segundos)
              </Typography>
              <Slider
                value={refreshInterval}
                onChange={(_, value) => setRefreshInterval(value as number)}
                min={5}
                max={300}
                step={5}
                marks
                valueLabelDisplay="auto"
                disabled={!autoRefresh}
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsDialogOpen(false)}>
            Fechar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PerformanceDashboard; 
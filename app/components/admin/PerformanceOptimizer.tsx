import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Tooltip,
  Badge,
  Tabs,
  Tab,
  Divider,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  LinearProgress,
  Slider,
  TextField,
} from '@mui/material';
import {
  Speed,
  Memory,
  Storage,
  NetworkCheck,
  Code,
  DataUsage,
  Assessment,
  TrendingUp,
  TrendingDown,
  Notifications,
  NotificationsOff,
  Schedule,
  AutoAwesome,
  Psychology,
  Science,
  Biotech,
  Engineering,
  Build,
  Construction,
  Handyman,
  Plumbing,
  ElectricalServices,
  CleaningServices,
  LocalShipping,
  LocalTaxi,
  DirectionsCar,
  DirectionsBike,
  DirectionsWalk,
  DirectionsRun,
  DirectionsTransit,
  DirectionsBoat,
  DirectionsSubway,
  DirectionsBus,
  DirectionsRailway,
  DirectionsCarFilled,
  DirectionsBikeFilled,
  DirectionsWalkFilled,
  DirectionsRunFilled,
  DirectionsTransitFilled,
  DirectionsBoatFilled,
  DirectionsSubwayFilled,
  DirectionsBusFilled,
  DirectionsRailwayFilled,
  Settings,
  Refresh,
  PlayArrow,
  Pause,
  Stop,
  SkipNext,
  SkipPrevious,
  FastForward,
  FastRewind,
  VolumeUp,
  VolumeDown,
  VolumeMute,
  BrightnessHigh,
  BrightnessLow,
  Contrast,
  FilterCenterFocus,
  CenterFocusStrong,
  CenterFocusWeak,
  Exposure,
  ExposureNeg1,
  ExposureNeg2,
  ExposurePlus1,
  ExposurePlus2,
  ExposureZero,
  Filter1,
  Filter2,
  Filter3,
  Filter4,
  Filter5,
  Filter6,
  Filter7,
  Filter8,
  Filter9,
  Filter9Plus,
  FilterBAndW,
  FilterCenterFocus,
  FilterDrama,
  FilterFrames,
  FilterHdr,
  FilterNone,
  FilterTiltShift,
  FilterVintage,
  Grain,
  GridOff,
  GridOn,
  HdrOff,
  HdrOn,
  HdrStrong,
  HdrWeak,
  Healing,
  Image,
  ImageAspectRatio,
  ImageNotSupported,
  ImageSearch,
  Iso,
  Landscape,
  LeakAdd,
  LeakRemove,
  Lens,
  LinkedCamera,
  Looks,
  Looks3,
  Looks4,
  Looks5,
  Looks6,
  LooksOne,
  LooksTwo,
  Loupe,
  MonochromePhotos,
  MovieCreation,
  MovieFilter,
  MusicNote,
  Nature,
  NaturePeople,
  NavigateBefore,
  NavigateNext,
  Palette,
  Panorama,
  PanoramaFishEye,
  PanoramaHorizontal,
  PanoramaVertical,
  PanoramaWideAngle,
  Photo,
  PhotoAlbum,
  PhotoCamera,
  PhotoFilter,
  PhotoLibrary,
  PhotoSizeSelectActual,
  PhotoSizeSelectLarge,
  PhotoSizeSelectSmall,
  PictureAsPdf,
  Portrait,
  ReceiptLong,
  RemoveRedEye,
  Rotate90DegreesCcw,
  RotateLeft,
  RotateRight,
  ShutterSpeed,
  Slideshow,
  Straighten,
  Style,
  SwitchCamera,
  SwitchVideo,
  TagFaces,
  Texture,
  Timelapse,
  Timer,
  Timer10,
  Timer3,
  TimerOff,
  Tonality,
  Transform,
  Tune,
  ViewComfy,
  ViewCompact,
  Vignette,
  WbAuto,
  WbCloudy,
  WbIncandescent,
  WbIridescent,
  WbSunny,
  ZoomIn,
  ZoomOut,
} from '@mui/icons-material';

// Types
interface PerformanceMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  threshold: number;
  status: 'good' | 'warning' | 'critical';
  trend: 'up' | 'down' | 'stable';
  description: string;
  category: 'cpu' | 'memory' | 'disk' | 'network' | 'database' | 'api';
}

interface QueryPerformance {
  id: string;
  query: string;
  executionTime: number;
  frequency: number;
  lastExecuted: string;
  table: string;
  indexes: string[];
  optimization: string;
  impact: 'high' | 'medium' | 'low';
}

interface OptimizationSuggestion {
  id: string;
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'low' | 'medium' | 'high';
  category: string;
  estimatedSavings: number;
  implementation: string;
  status: 'pending' | 'implemented' | 'rejected';
}

interface PerformanceAlert {
  id: string;
  metric: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  timestamp: string;
  resolved: boolean;
}

interface PerformanceConfig {
  autoOptimization: boolean;
  alertThresholds: Record<string, number>;
  monitoringInterval: number;
  retentionDays: number;
  optimizationMode: 'conservative' | 'aggressive' | 'balanced';
}

// Mock data
const mockMetrics: PerformanceMetric[] = [
  {
    id: '1',
    name: 'CPU Usage',
    value: 75.2,
    unit: '%',
    threshold: 80,
    status: 'warning',
    trend: 'up',
    description: 'High CPU usage detected',
    category: 'cpu',
  },
  {
    id: '2',
    name: 'Memory Usage',
    value: 68.5,
    unit: '%',
    threshold: 85,
    status: 'good',
    trend: 'stable',
    description: 'Memory usage within normal range',
    category: 'memory',
  },
  {
    id: '3',
    name: 'Disk I/O',
    value: 45.8,
    unit: 'MB/s',
    threshold: 100,
    status: 'good',
    trend: 'down',
    description: 'Disk I/O performance is good',
    category: 'disk',
  },
  {
    id: '4',
    name: 'Network Latency',
    value: 125,
    unit: 'ms',
    threshold: 200,
    status: 'good',
    trend: 'stable',
    description: 'Network latency is acceptable',
    category: 'network',
  },
  {
    id: '5',
    name: 'Database Response Time',
    value: 350,
    unit: 'ms',
    threshold: 500,
    status: 'warning',
    trend: 'up',
    description: 'Database queries are slowing down',
    category: 'database',
  },
  {
    id: '6',
    name: 'API Response Time',
    value: 280,
    unit: 'ms',
    threshold: 300,
    status: 'warning',
    trend: 'up',
    description: 'API endpoints are experiencing delays',
    category: 'api',
  },
];

const mockQueries: QueryPerformance[] = [
  {
    id: '1',
    query: 'SELECT * FROM users WHERE email = ?',
    executionTime: 150,
    frequency: 1250,
    lastExecuted: '2024-12-20T10:30:00Z',
    table: 'users',
    indexes: ['email_idx'],
    optimization: 'Add composite index on (email, status)',
    impact: 'high',
  },
  {
    id: '2',
    query: 'SELECT COUNT(*) FROM logs WHERE created_at > ?',
    executionTime: 450,
    frequency: 85,
    lastExecuted: '2024-12-20T10:29:00Z',
    table: 'logs',
    indexes: ['created_at_idx'],
    optimization: 'Partition table by date',
    impact: 'medium',
  },
  {
    id: '3',
    query: 'UPDATE analytics SET value = ? WHERE id = ?',
    executionTime: 25,
    frequency: 3200,
    lastExecuted: '2024-12-20T10:28:00Z',
    table: 'analytics',
    indexes: ['id_idx'],
    optimization: 'Batch updates for better performance',
    impact: 'low',
  },
];

const mockSuggestions: OptimizationSuggestion[] = [
  {
    id: '1',
    title: 'Add Database Indexes',
    description: 'Create composite indexes for frequently queried columns',
    impact: 'high',
    effort: 'low',
    category: 'database',
    estimatedSavings: 45,
    implementation: 'Run index creation scripts during maintenance window',
    status: 'pending',
  },
  {
    id: '2',
    title: 'Implement Query Caching',
    description: 'Cache frequently executed queries to reduce database load',
    impact: 'high',
    effort: 'medium',
    category: 'performance',
    estimatedSavings: 30,
    implementation: 'Add Redis cache layer with TTL configuration',
    status: 'pending',
  },
  {
    id: '3',
    title: 'Optimize API Endpoints',
    description: 'Implement pagination and filtering for large datasets',
    impact: 'medium',
    effort: 'medium',
    category: 'api',
    estimatedSavings: 25,
    implementation: 'Add pagination parameters and response optimization',
    status: 'pending',
  },
  {
    id: '4',
    title: 'Enable Gzip Compression',
    description: 'Compress API responses to reduce bandwidth usage',
    impact: 'medium',
    effort: 'low',
    category: 'network',
    estimatedSavings: 20,
    implementation: 'Configure web server compression settings',
    status: 'implemented',
  },
];

const mockAlerts: PerformanceAlert[] = [
  {
    id: '1',
    metric: 'CPU Usage',
    message: 'CPU usage exceeded 80% threshold',
    severity: 'warning',
    timestamp: '2024-12-20T10:30:00Z',
    resolved: false,
  },
  {
    id: '2',
    metric: 'Database Response Time',
    message: 'Database queries taking longer than expected',
    severity: 'error',
    timestamp: '2024-12-20T10:25:00Z',
    resolved: false,
  },
  {
    id: '3',
    metric: 'Memory Usage',
    message: 'Memory usage approaching threshold',
    severity: 'info',
    timestamp: '2024-12-20T10:20:00Z',
    resolved: true,
  },
];

const PerformanceOptimizer: React.FC = () => {
  // State
  const [metrics, setMetrics] = useState<PerformanceMetric[]>(mockMetrics);
  const [queries, setQueries] = useState<QueryPerformance[]>(mockQueries);
  const [suggestions, setSuggestions] = useState<OptimizationSuggestion[]>(mockSuggestions);
  const [alerts, setAlerts] = useState<PerformanceAlert[]>(mockAlerts);
  const [config, setConfig] = useState<PerformanceConfig>({
    autoOptimization: false,
    alertThresholds: {
      cpu: 80,
      memory: 85,
      disk: 90,
      network: 200,
      database: 500,
      api: 300,
    },
    monitoringInterval: 30,
    retentionDays: 30,
    optimizationMode: 'balanced',
  });
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [selectedSuggestion, setSelectedSuggestion] = useState<OptimizationSuggestion | null>(null);
  const [suggestionDialogOpen, setSuggestionDialogOpen] = useState(false);
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [autoOptimizeDialogOpen, setAutoOptimizeDialogOpen] = useState(false);

  // Memoized values
  const criticalMetrics = useMemo(() => {
    return metrics.filter(metric => metric.status === 'critical');
  }, [metrics]);

  const warningMetrics = useMemo(() => {
    return metrics.filter(metric => metric.status === 'warning');
  }, [metrics]);

  const highImpactQueries = useMemo(() => {
    return queries.filter(query => query.impact === 'high');
  }, [queries]);

  const pendingSuggestions = useMemo(() => {
    return suggestions.filter(suggestion => suggestion.status === 'pending');
  }, [suggestions]);

  const totalSavings = useMemo(() => {
    return pendingSuggestions.reduce((sum, suggestion) => sum + suggestion.estimatedSavings, 0);
  }, [pendingSuggestions]);

  // Handlers
  const handleOptimizationModeChange = (mode: 'conservative' | 'aggressive' | 'balanced') => {
    setConfig(prev => ({ ...prev, optimizationMode: mode }));
  };

  const handleThresholdChange = (metric: string, value: number) => {
    setConfig(prev => ({
      ...prev,
      alertThresholds: { ...prev.alertThresholds, [metric]: value },
    }));
  };

  const handleAutoOptimizationToggle = () => {
    setConfig(prev => ({ ...prev, autoOptimization: !prev.autoOptimization }));
  };

  const handleSuggestionImplement = (suggestionId: string) => {
    setSuggestions(prev =>
      prev.map(suggestion =>
        suggestion.id === suggestionId
          ? { ...suggestion, status: 'implemented' as const }
          : suggestion
      )
    );
  };

  const handleSuggestionReject = (suggestionId: string) => {
    setSuggestions(prev =>
      prev.map(suggestion =>
        suggestion.id === suggestionId
          ? { ...suggestion, status: 'rejected' as const }
          : suggestion
      )
    );
  };

  const handleAlertResolve = (alertId: string) => {
    setAlerts(prev =>
      prev.map(alert =>
        alert.id === alertId ? { ...alert, resolved: true } : alert
      )
    );
  };

  const handleRefreshMetrics = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Update metrics with new values
      setMetrics(prev =>
        prev.map(metric => ({
          ...metric,
          value: Math.random() * 100,
          status: Math.random() > 0.7 ? 'critical' : Math.random() > 0.5 ? 'warning' : 'good',
        }))
      );
    } catch (err) {
      setError('Failed to refresh metrics');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good': return 'success';
      case 'warning': return 'warning';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'error': return 'error';
      case 'warning': return 'warning';
      case 'info': return 'info';
      default: return 'default';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp color="error" />;
      case 'down': return <TrendingDown color="success" />;
      case 'stable': return <TrendingUp color="disabled" />;
      default: return <TrendingUp />;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Performance Optimizer
        </Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh Metrics">
            <IconButton onClick={handleRefreshMetrics}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="Auto Optimization">
            <IconButton
              color={config.autoOptimization ? 'primary' : 'default'}
              onClick={() => setAutoOptimizeDialogOpen(true)}
            >
              <AutoAwesome />
            </IconButton>
          </Tooltip>
          <Tooltip title="Settings">
            <IconButton onClick={() => setConfigDialogOpen(true)}>
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Critical Alerts */}
      {criticalMetrics.length > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="h6">
            {criticalMetrics.length} Critical Performance Issue{criticalMetrics.length > 1 ? 's' : ''} Detected
          </Typography>
          <Typography variant="body2">
            Immediate attention required for: {criticalMetrics.map(m => m.name).join(', ')}
          </Typography>
        </Alert>
      )}

      {/* Performance Overview Cards */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Speed color="primary" />
                <Typography variant="h6">Overall Score</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {Math.round((metrics.filter(m => m.status === 'good').length / metrics.length) * 100)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {metrics.filter(m => m.status === 'good').length} of {metrics.length} metrics healthy
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <TrendingUp color="warning" />
                <Typography variant="h6">Optimization Savings</Typography>
              </Box>
              <Typography variant="h4" color="warning.main">
                {totalSavings}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {pendingSuggestions.length} suggestions pending
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Notifications color="error" />
                <Typography variant="h6">Active Alerts</Typography>
              </Box>
              <Typography variant="h4" color="error">
                {alerts.filter(a => !a.resolved).length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {criticalMetrics.length} critical, {warningMetrics.length} warnings
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Code color="info" />
                <Typography variant="h6">Slow Queries</Typography>
              </Box>
              <Typography variant="h4" color="info.main">
                {highImpactQueries.length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                High impact queries detected
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Metrics" />
          <Tab label="Queries" />
          <Tab label="Optimizations" />
          <Tab label="Alerts" />
        </Tabs>
      </Box>

      {/* Metrics Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {metrics.map((metric) => (
            <Grid item xs={12} md={6} key={metric.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6">{metric.name}</Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      {getTrendIcon(metric.trend)}
                      <Chip
                        label={metric.status.toUpperCase()}
                        color={getStatusColor(metric.status) as any}
                        size="small"
                      />
                    </Box>
                  </Box>
                  <Typography variant="h4" color="primary" mb={1}>
                    {metric.value}{metric.unit}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" mb={2}>
                    {metric.description}
                  </Typography>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Typography variant="body2" color="textSecondary">
                      Threshold: {metric.threshold}{metric.unit}
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={(metric.value / metric.threshold) * 100}
                      color={getStatusColor(metric.status) as any}
                      sx={{ flexGrow: 1 }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Queries Tab */}
      {activeTab === 1 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Query</TableCell>
                <TableCell>Execution Time</TableCell>
                <TableCell>Frequency</TableCell>
                <TableCell>Table</TableCell>
                <TableCell>Optimization</TableCell>
                <TableCell>Impact</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {queries.map((query) => (
                <TableRow key={query.id}>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                      {query.query}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography color={query.executionTime > 300 ? 'error' : 'inherit'}>
                      {query.executionTime}ms
                    </Typography>
                  </TableCell>
                  <TableCell>{query.frequency}/hour</TableCell>
                  <TableCell>{query.table}</TableCell>
                  <TableCell>
                    <Typography variant="body2" color="textSecondary">
                      {query.optimization}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={query.impact.toUpperCase()}
                      color={getImpactColor(query.impact) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Tooltip title="View Details">
                      <IconButton size="small">
                        <Assessment />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Optimizations Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          {suggestions.map((suggestion) => (
            <Grid item xs={12} md={6} key={suggestion.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Typography variant="h6">{suggestion.title}</Typography>
                    <Box display="flex" gap={1}>
                      <Chip
                        label={`${suggestion.estimatedSavings}% savings`}
                        color="success"
                        size="small"
                      />
                      <Chip
                        label={suggestion.impact}
                        color={getImpactColor(suggestion.impact) as any}
                        size="small"
                      />
                    </Box>
                  </Box>
                  <Typography variant="body2" color="textSecondary" mb={2}>
                    {suggestion.description}
                  </Typography>
                  <Typography variant="body2" mb={2}>
                    <strong>Implementation:</strong> {suggestion.implementation}
                  </Typography>
                  <Box display="flex" gap={1}>
                    {suggestion.status === 'pending' && (
                      <>
                        <Button
                          size="small"
                          variant="contained"
                          color="primary"
                          onClick={() => handleSuggestionImplement(suggestion.id)}
                        >
                          Implement
                        </Button>
                        <Button
                          size="small"
                          variant="outlined"
                          color="error"
                          onClick={() => handleSuggestionReject(suggestion.id)}
                        >
                          Reject
                        </Button>
                      </>
                    )}
                    {suggestion.status === 'implemented' && (
                      <Chip label="IMPLEMENTED" color="success" size="small" />
                    )}
                    {suggestion.status === 'rejected' && (
                      <Chip label="REJECTED" color="error" size="small" />
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Alerts Tab */}
      {activeTab === 3 && (
        <List>
          {alerts.map((alert) => (
            <ListItem key={alert.id}>
              <ListItemIcon>
                <Notifications color={getSeverityColor(alert.severity) as any} />
              </ListItemIcon>
              <ListItemText
                primary={alert.message}
                secondary={`${alert.metric} - ${new Date(alert.timestamp).toLocaleString()}`}
              />
              <Box display="flex" gap={1}>
                <Chip
                  label={alert.severity.toUpperCase()}
                  color={getSeverityColor(alert.severity) as any}
                  size="small"
                />
                {!alert.resolved && (
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => handleAlertResolve(alert.id)}
                  >
                    Resolve
                  </Button>
                )}
                {alert.resolved && (
                  <Chip label="RESOLVED" color="success" size="small" />
                )}
              </Box>
            </ListItem>
          ))}
        </List>
      )}

      {/* Settings Dialog */}
      <Dialog
        open={configDialogOpen}
        onClose={() => setConfigDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Performance Settings</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={3} mt={1}>
            <FormControlLabel
              control={
                <Switch
                  checked={config.autoOptimization}
                  onChange={handleAutoOptimizationToggle}
                />
              }
              label="Auto Optimization"
            />
            
            <FormControl>
              <InputLabel>Optimization Mode</InputLabel>
              <Select
                value={config.optimizationMode}
                onChange={(e) => handleOptimizationModeChange(e.target.value as any)}
              >
                <MenuItem value="conservative">Conservative</MenuItem>
                <MenuItem value="balanced">Balanced</MenuItem>
                <MenuItem value="aggressive">Aggressive</MenuItem>
              </Select>
            </FormControl>

            <Typography variant="h6">Alert Thresholds</Typography>
            <Grid container spacing={2}>
              {Object.entries(config.alertThresholds).map(([metric, threshold]) => (
                <Grid item xs={12} sm={6} key={metric}>
                  <TextField
                    label={`${metric.toUpperCase()} Threshold`}
                    type="number"
                    value={threshold}
                    onChange={(e) => handleThresholdChange(metric, Number(e.target.value))}
                    fullWidth
                  />
                </Grid>
              ))}
            </Grid>

            <TextField
              label="Monitoring Interval (seconds)"
              type="number"
              value={config.monitoringInterval}
              onChange={(e) => setConfig(prev => ({ ...prev, monitoringInterval: Number(e.target.value) }))}
            />

            <TextField
              label="Data Retention (days)"
              type="number"
              value={config.retentionDays}
              onChange={(e) => setConfig(prev => ({ ...prev, retentionDays: Number(e.target.value) }))}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>Cancel</Button>
          <Button onClick={() => setConfigDialogOpen(false)} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Auto Optimization Dialog */}
      <Dialog
        open={autoOptimizeDialogOpen}
        onClose={() => setAutoOptimizeDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Auto Optimization</DialogTitle>
        <DialogContent>
          <Typography variant="body1" mb={2}>
            Auto optimization will automatically implement performance improvements based on detected issues.
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={config.autoOptimization}
                onChange={handleAutoOptimizationToggle}
              />
            }
            label="Enable Auto Optimization"
          />
          {config.autoOptimization && (
            <Box mt={2}>
              <Typography variant="body2" color="textSecondary">
                Mode: {config.optimizationMode}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Monitoring Interval: {config.monitoringInterval} seconds
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAutoOptimizeDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default PerformanceOptimizer; 
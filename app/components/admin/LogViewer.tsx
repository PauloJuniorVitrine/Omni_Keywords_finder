import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
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
} from '@mui/material';
import {
  Search,
  FilterList,
  Download,
  Refresh,
  Visibility,
  Warning,
  Error,
  Info,
  BugReport,
  Timeline,
  Analytics,
  Settings,
  ExpandMore,
  Clear,
  PlayArrow,
  Pause,
  Fullscreen,
  FullscreenExit,
  ContentCopy,
  Share,
  Archive,
  Delete,
  RestoreFromTrash,
  Security,
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
} from '@mui/icons-material';

// Types
interface LogEntry {
  id: string;
  timestamp: string;
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  category: string;
  message: string;
  source: string;
  userId?: string;
  sessionId?: string;
  ipAddress?: string;
  userAgent?: string;
  metadata?: Record<string, any>;
  stackTrace?: string;
  duration?: number;
  memoryUsage?: number;
  cpuUsage?: number;
  requestId?: string;
  correlationId?: string;
}

interface LogFilter {
  level: string[];
  category: string[];
  source: string[];
  dateRange: {
    start: Date | null;
    end: Date | null;
  };
  searchText: string;
  userId?: string;
  sessionId?: string;
  ipAddress?: string;
}

interface LogAnalytics {
  totalLogs: number;
  logsByLevel: Record<string, number>;
  logsByCategory: Record<string, number>;
  logsBySource: Record<string, number>;
  logsByHour: Record<string, number>;
  averageResponseTime: number;
  errorRate: number;
  topErrors: Array<{ message: string; count: number }>;
  patterns: Array<{ pattern: string; count: number; severity: string }>;
}

// Mock data
const mockLogs: LogEntry[] = [
  {
    id: '1',
    timestamp: '2024-12-20T10:30:00Z',
    level: 'INFO',
    category: 'AUTH',
    message: 'User login successful',
    source: 'auth-service',
    userId: 'user123',
    sessionId: 'sess456',
    ipAddress: '192.168.1.100',
    userAgent: 'Mozilla/5.0...',
    duration: 150,
    memoryUsage: 45.2,
    cpuUsage: 12.5,
    requestId: 'req789',
    correlationId: 'corr123',
  },
  {
    id: '2',
    timestamp: '2024-12-20T10:31:00Z',
    level: 'WARNING',
    category: 'PERFORMANCE',
    message: 'High memory usage detected',
    source: 'monitoring-service',
    metadata: { memoryThreshold: 80, currentUsage: 85 },
    duration: 200,
    memoryUsage: 85.0,
    cpuUsage: 25.3,
  },
  {
    id: '3',
    timestamp: '2024-12-20T10:32:00Z',
    level: 'ERROR',
    category: 'DATABASE',
    message: 'Database connection timeout',
    source: 'db-service',
    stackTrace: 'Error: Connection timeout\n    at Database.connect...',
    duration: 5000,
    memoryUsage: 60.1,
    cpuUsage: 45.7,
  },
  {
    id: '4',
    timestamp: '2024-12-20T10:33:00Z',
    level: 'DEBUG',
    category: 'API',
    message: 'API request processed',
    source: 'api-gateway',
    duration: 120,
    memoryUsage: 30.5,
    cpuUsage: 8.2,
  },
  {
    id: '5',
    timestamp: '2024-12-20T10:34:00Z',
    level: 'CRITICAL',
    category: 'SECURITY',
    message: 'Multiple failed login attempts detected',
    source: 'security-service',
    userId: 'user456',
    ipAddress: '192.168.1.200',
    metadata: { attempts: 5, timeWindow: '5m' },
    duration: 300,
    memoryUsage: 55.8,
    cpuUsage: 18.9,
  },
];

const LogViewer: React.FC = () => {
  // State
  const [logs, setLogs] = useState<LogEntry[]>(mockLogs);
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>(mockLogs);
  const [filter, setFilter] = useState<LogFilter>({
    level: [],
    category: [],
    source: [],
    dateRange: { start: null, end: null },
    searchText: '',
  });
  const [analytics, setAnalytics] = useState<LogAnalytics | null>(null);
  const [isLiveMode, setIsLiveMode] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);
  const [logDetailOpen, setLogDetailOpen] = useState(false);
  const [patternsOpen, setPatternsOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000);
  const [maxLogs, setMaxLogs] = useState(1000);
  const [logLevels, setLogLevels] = useState<string[]>(['INFO', 'WARNING', 'ERROR', 'CRITICAL']);

  // Memoized values
  const availableLevels = useMemo(() => {
    const levels = new Set(logs.map(log => log.level));
    return Array.from(levels).sort();
  }, [logs]);

  const availableCategories = useMemo(() => {
    const categories = new Set(logs.map(log => log.category));
    return Array.from(categories).sort();
  }, [logs]);

  const availableSources = useMemo(() => {
    const sources = new Set(logs.map(log => log.source));
    return Array.from(sources).sort();
  }, [logs]);

  // Filter logs
  const applyFilters = useCallback(() => {
    let filtered = logs;

    // Filter by level
    if (filter.level.length > 0) {
      filtered = filtered.filter(log => filter.level.includes(log.level));
    }

    // Filter by category
    if (filter.category.length > 0) {
      filtered = filtered.filter(log => filter.category.includes(log.category));
    }

    // Filter by source
    if (filter.source.length > 0) {
      filtered = filtered.filter(log => filter.source.includes(log.source));
    }

    // Filter by date range
    if (filter.dateRange.start) {
      filtered = filtered.filter(log => new Date(log.timestamp) >= filter.dateRange.start!);
    }
    if (filter.dateRange.end) {
      filtered = filtered.filter(log => new Date(log.timestamp) <= filter.dateRange.end!);
    }

    // Filter by search text
    if (filter.searchText) {
      const searchLower = filter.searchText.toLowerCase();
      filtered = filtered.filter(log =>
        log.message.toLowerCase().includes(searchLower) ||
        log.category.toLowerCase().includes(searchLower) ||
        log.source.toLowerCase().includes(searchLower) ||
        log.userId?.toLowerCase().includes(searchLower) ||
        log.ipAddress?.includes(searchLower)
      );
    }

    // Filter by user ID
    if (filter.userId) {
      filtered = filtered.filter(log => log.userId === filter.userId);
    }

    // Filter by session ID
    if (filter.sessionId) {
      filtered = filtered.filter(log => log.sessionId === filter.sessionId);
    }

    // Filter by IP address
    if (filter.ipAddress) {
      filtered = filtered.filter(log => log.ipAddress === filter.ipAddress);
    }

    setFilteredLogs(filtered);
  }, [logs, filter]);

  // Calculate analytics
  const calculateAnalytics = useCallback(() => {
    const analytics: LogAnalytics = {
      totalLogs: filteredLogs.length,
      logsByLevel: {},
      logsByCategory: {},
      logsBySource: {},
      logsByHour: {},
      averageResponseTime: 0,
      errorRate: 0,
      topErrors: [],
      patterns: [],
    };

    // Count by level
    filteredLogs.forEach(log => {
      analytics.logsByLevel[log.level] = (analytics.logsByLevel[log.level] || 0) + 1;
    });

    // Count by category
    filteredLogs.forEach(log => {
      analytics.logsByCategory[log.category] = (analytics.logsByCategory[log.category] || 0) + 1;
    });

    // Count by source
    filteredLogs.forEach(log => {
      analytics.logsBySource[log.source] = (analytics.logsBySource[log.source] || 0) + 1;
    });

    // Count by hour
    filteredLogs.forEach(log => {
      const hour = new Date(log.timestamp).getHours().toString().padStart(2, '0');
      analytics.logsByHour[hour] = (analytics.logsByHour[hour] || 0) + 1;
    });

    // Calculate average response time
    const logsWithDuration = filteredLogs.filter(log => log.duration);
    if (logsWithDuration.length > 0) {
      analytics.averageResponseTime = logsWithDuration.reduce((sum, log) => sum + (log.duration || 0), 0) / logsWithDuration.length;
    }

    // Calculate error rate
    const errorLogs = filteredLogs.filter(log => ['ERROR', 'CRITICAL'].includes(log.level));
    analytics.errorRate = (errorLogs.length / filteredLogs.length) * 100;

    // Top errors
    const errorMessages = errorLogs.map(log => log.message);
    const errorCounts = errorMessages.reduce((acc, message) => {
      acc[message] = (acc[message] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    analytics.topErrors = Object.entries(errorCounts)
      .map(([message, count]) => ({ message, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    // Patterns (simplified)
    const patterns = [
      { pattern: 'Database connection', count: 3, severity: 'ERROR' },
      { pattern: 'High memory usage', count: 2, severity: 'WARNING' },
      { pattern: 'User login', count: 1, severity: 'INFO' },
    ];
    analytics.patterns = patterns;

    setAnalytics(analytics);
  }, [filteredLogs]);

  // Effects
  useEffect(() => {
    applyFilters();
  }, [applyFilters]);

  useEffect(() => {
    calculateAnalytics();
  }, [calculateAnalytics]);

  useEffect(() => {
    if (isLiveMode && autoRefresh) {
      const interval = setInterval(() => {
        // Simulate new logs
        const newLog: LogEntry = {
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          level: ['INFO', 'WARNING', 'ERROR'][Math.floor(Math.random() * 3)] as any,
          category: ['API', 'DATABASE', 'AUTH', 'PERFORMANCE'][Math.floor(Math.random() * 4)],
          message: `Live log entry ${Date.now()}`,
          source: 'live-service',
          duration: Math.random() * 1000,
          memoryUsage: Math.random() * 100,
          cpuUsage: Math.random() * 100,
        };
        setLogs(prev => [newLog, ...prev.slice(0, maxLogs - 1)]);
      }, refreshInterval);

      return () => clearInterval(interval);
    }
  }, [isLiveMode, autoRefresh, refreshInterval, maxLogs]);

  // Handlers
  const handleFilterChange = (field: keyof LogFilter, value: any) => {
    setFilter(prev => ({ ...prev, [field]: value }));
  };

  const handleClearFilters = () => {
    setFilter({
      level: [],
      category: [],
      source: [],
      dateRange: { start: null, end: null },
      searchText: '',
    });
  };

  const handleExportLogs = (format: 'csv' | 'json') => {
    const data = format === 'csv' 
      ? filteredLogs.map(log => `${log.timestamp},${log.level},${log.category},${log.message},${log.source}`).join('\n')
      : JSON.stringify(filteredLogs, null, 2);
    
    const blob = new Blob([data], { type: format === 'csv' ? 'text/csv' : 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs-${new Date().toISOString()}.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleLogClick = (log: LogEntry) => {
    setSelectedLog(log);
    setLogDetailOpen(true);
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'DEBUG': return 'default';
      case 'INFO': return 'info';
      case 'WARNING': return 'warning';
      case 'ERROR': return 'error';
      case 'CRITICAL': return 'error';
      default: return 'default';
    }
  };

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'DEBUG': return <BugReport />;
      case 'INFO': return <Info />;
      case 'WARNING': return <Warning />;
      case 'ERROR': return <Error />;
      case 'CRITICAL': return <Security />;
      default: return <Info />;
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
          Log Viewer
        </Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Live Mode">
            <IconButton
              color={isLiveMode ? 'primary' : 'default'}
              onClick={() => setIsLiveMode(!isLiveMode)}
            >
              {isLiveMode ? <PlayArrow /> : <Pause />}
            </Tooltip>
          </Tooltip>
          <Tooltip title="Fullscreen">
            <IconButton onClick={() => setIsFullscreen(!isFullscreen)}>
              {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Settings">
            <IconButton onClick={() => setSettingsOpen(true)}>
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Analytics Cards */}
      {analytics && (
        <Grid container spacing={2} mb={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Logs
                </Typography>
                <Typography variant="h4">
                  {analytics.totalLogs.toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Error Rate
                </Typography>
                <Typography variant="h4" color="error">
                  {analytics.errorRate.toFixed(1)}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Avg Response Time
                </Typography>
                <Typography variant="h4">
                  {analytics.averageResponseTime.toFixed(0)}ms
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Active Sources
                </Typography>
                <Typography variant="h4">
                  {Object.keys(analytics.logsBySource).length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Logs" />
          <Tab label="Analytics" />
          <Tab label="Patterns" />
        </Tabs>
      </Box>

      {/* Logs Tab */}
      {activeTab === 0 && (
        <>
          {/* Filters */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Search logs"
                    value={filter.searchText}
                    onChange={(e) => handleFilterChange('searchText', e.target.value)}
                    InputProps={{
                      startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={2}>
                  <FormControl fullWidth>
                    <InputLabel>Level</InputLabel>
                    <Select
                      multiple
                      value={filter.level}
                      onChange={(e) => handleFilterChange('level', e.target.value)}
                      renderValue={(selected) => (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {selected.map((value) => (
                            <Chip key={value} label={value} size="small" />
                          ))}
                        </Box>
                      )}
                    >
                      {availableLevels.map((level) => (
                        <MenuItem key={level} value={level}>
                          {level}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={2}>
                  <FormControl fullWidth>
                    <InputLabel>Category</InputLabel>
                    <Select
                      multiple
                      value={filter.category}
                      onChange={(e) => handleFilterChange('category', e.target.value)}
                      renderValue={(selected) => (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {selected.map((value) => (
                            <Chip key={value} label={value} size="small" />
                          ))}
                        </Box>
                      )}
                    >
                      {availableCategories.map((category) => (
                        <MenuItem key={category} value={category}>
                          {category}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={2}>
                  <FormControl fullWidth>
                    <InputLabel>Source</InputLabel>
                    <Select
                      multiple
                      value={filter.source}
                      onChange={(e) => handleFilterChange('source', e.target.value)}
                      renderValue={(selected) => (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {selected.map((value) => (
                            <Chip key={value} label={value} size="small" />
                          ))}
                        </Box>
                      )}
                    >
                      {availableSources.map((source) => (
                        <MenuItem key={source} value={source}>
                          {source}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={2}>
                  <Box display="flex" gap={1}>
                    <Button
                      variant="outlined"
                      startIcon={<Clear />}
                      onClick={handleClearFilters}
                    >
                      Clear
                    </Button>
                    <Button
                      variant="contained"
                      startIcon={<Download />}
                      onClick={() => handleExportLogs('csv')}
                    >
                      Export
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Logs Table */}
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Level</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Message</TableCell>
                  <TableCell>Source</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredLogs.map((log) => (
                  <TableRow key={log.id} hover>
                    <TableCell>
                      {new Date(log.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getLevelIcon(log.level)}
                        label={log.level}
                        color={getLevelColor(log.level) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{log.category}</TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap>
                        {log.message}
                      </Typography>
                    </TableCell>
                    <TableCell>{log.source}</TableCell>
                    <TableCell>
                      {log.duration ? `${log.duration}ms` : '-'}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => handleLogClick(log)}
                        >
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}

      {/* Analytics Tab */}
      {activeTab === 1 && analytics && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Logs by Level
                </Typography>
                <Box display="flex" flexDirection="column" gap={1}>
                  {Object.entries(analytics.logsByLevel).map(([level, count]) => (
                    <Box key={level} display="flex" justifyContent="space-between" alignItems="center">
                      <Box display="flex" alignItems="center" gap={1}>
                        {getLevelIcon(level)}
                        <Typography>{level}</Typography>
                      </Box>
                      <Chip label={count} size="small" />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Top Errors
                </Typography>
                <List dense>
                  {analytics.topErrors.map((error, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Error color="error" />
                      </ListItemIcon>
                      <ListItemText
                        primary={error.message}
                        secondary={`${error.count} occurrences`}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Patterns Tab */}
      {activeTab === 2 && analytics && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Detected Patterns
            </Typography>
            <List>
              {analytics.patterns.map((pattern, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <TrendingUp />
                  </ListItemIcon>
                  <ListItemText
                    primary={pattern.pattern}
                    secondary={`${pattern.count} occurrences - ${pattern.severity} level`}
                  />
                  <Chip
                    label={pattern.severity}
                    color={getLevelColor(pattern.severity) as any}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Log Detail Dialog */}
      <Dialog
        open={logDetailOpen}
        onClose={() => setLogDetailOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Log Details
          <IconButton
            onClick={() => setLogDetailOpen(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <Clear />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {selectedLog && (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Basic Information
                  </Typography>
                  <Box mt={1}>
                    <Typography><strong>ID:</strong> {selectedLog.id}</Typography>
                    <Typography><strong>Timestamp:</strong> {new Date(selectedLog.timestamp).toLocaleString()}</Typography>
                    <Typography><strong>Level:</strong> {selectedLog.level}</Typography>
                    <Typography><strong>Category:</strong> {selectedLog.category}</Typography>
                    <Typography><strong>Source:</strong> {selectedLog.source}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Performance Metrics
                  </Typography>
                  <Box mt={1}>
                    <Typography><strong>Duration:</strong> {selectedLog.duration || 'N/A'}ms</Typography>
                    <Typography><strong>Memory Usage:</strong> {selectedLog.memoryUsage || 'N/A'}%</Typography>
                    <Typography><strong>CPU Usage:</strong> {selectedLog.cpuUsage || 'N/A'}%</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Message
                  </Typography>
                  <Box mt={1} p={2} bgcolor="grey.100" borderRadius={1}>
                    <Typography>{selectedLog.message}</Typography>
                  </Box>
                </Grid>
                {selectedLog.stackTrace && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Stack Trace
                    </Typography>
                    <Box mt={1} p={2} bgcolor="grey.100" borderRadius={1}>
                      <Typography
                        component="pre"
                        sx={{ fontFamily: 'monospace', fontSize: '0.875rem', whiteSpace: 'pre-wrap' }}
                      >
                        {selectedLog.stackTrace}
                      </Typography>
                    </Box>
                  </Grid>
                )}
                {selectedLog.metadata && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Metadata
                    </Typography>
                    <Box mt={1} p={2} bgcolor="grey.100" borderRadius={1}>
                      <Typography
                        component="pre"
                        sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}
                      >
                        {JSON.stringify(selectedLog.metadata, null, 2)}
                      </Typography>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLogDetailOpen(false)}>Close</Button>
          <Button
            startIcon={<ContentCopy />}
            onClick={() => {
              if (selectedLog) {
                navigator.clipboard.writeText(JSON.stringify(selectedLog, null, 2));
              }
            }}
          >
            Copy
          </Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Log Viewer Settings</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={1}>
            <FormControlLabel
              control={
                <Switch
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                />
              }
              label="Auto Refresh"
            />
            <TextField
              label="Refresh Interval (ms)"
              type="number"
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              disabled={!autoRefresh}
            />
            <TextField
              label="Max Logs"
              type="number"
              value={maxLogs}
              onChange={(e) => setMaxLogs(Number(e.target.value))}
            />
            <FormControl>
              <InputLabel>Visible Log Levels</InputLabel>
              <Select
                multiple
                value={logLevels}
                onChange={(e) => setLogLevels(e.target.value as string[])}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} size="small" />
                    ))}
                  </Box>
                )}
              >
                {['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'].map((level) => (
                  <MenuItem key={level} value={level}>
                    {level}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Cancel</Button>
          <Button onClick={() => setSettingsOpen(false)} variant="contained">
            Save
          </Button>
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

export default LogViewer; 
/**
 * Sistema de Cache Avançado
 * 
 * Prompt: UI-016 do CHECKLIST_INTERFACE_GRAFICA_V1.md
 * Ruleset: enterprise_control_layer.yaml
 * Data/Hora: 2024-12-20 10:30:00 UTC
 * Tracing ID: UI-016
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tabs,
  Tab,
  Chip,
  IconButton,
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
  LinearProgress,
  Tooltip,
  Badge,
  Grid,
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
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Settings as SettingsIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Backup as BackupIcon,
  RestoreFromTrash as RestoreIcon,
  Analytics as AnalyticsIcon,
  Timer as TimerIcon,
  Memory as MemoryIcon,
  CloudDownload as CloudDownloadIcon
} from '@mui/icons-material';

// Types
interface CacheItem {
  key: string;
  value: any;
  size: number;
  ttl: number;
  createdAt: Date;
  lastAccessed: Date;
  accessCount: number;
  type: 'string' | 'hash' | 'list' | 'set' | 'zset';
  namespace: string;
}

interface CacheStats {
  totalItems: number;
  totalSize: number;
  hitRate: number;
  missRate: number;
  evictions: number;
  expired: number;
  memoryUsage: number;
  memoryLimit: number;
  averageResponseTime: number;
  keyspaceHits: number;
  keyspaceMisses: number;
}

interface CacheConfig {
  maxMemory: number;
  maxItems: number;
  defaultTTL: number;
  evictionPolicy: 'lru' | 'lfu' | 'fifo' | 'random';
  enableCompression: boolean;
  enablePersistence: boolean;
  backupInterval: number;
  warmingEnabled: boolean;
  warmingStrategy: 'preload' | 'lazy' | 'hybrid';
}

interface CacheBackup {
  id: string;
  timestamp: Date;
  size: number;
  itemCount: number;
  status: 'completed' | 'failed' | 'in_progress';
  type: 'full' | 'incremental';
  location: string;
}

interface CachePattern {
  pattern: string;
  frequency: number;
  averageSize: number;
  hitRate: number;
  lastAccessed: Date;
}

// Mock data
const mockCacheItems: CacheItem[] = [
  {
    key: 'user:profile:123',
    value: { name: 'João Silva', email: 'joao@example.com' },
    size: 1024,
    ttl: 3600,
    createdAt: new Date(Date.now() - 1800000),
    lastAccessed: new Date(Date.now() - 300000),
    accessCount: 15,
    type: 'hash',
    namespace: 'users'
  },
  {
    key: 'search:results:keywords',
    value: ['keyword1', 'keyword2', 'keyword3'],
    size: 2048,
    ttl: 1800,
    createdAt: new Date(Date.now() - 900000),
    lastAccessed: new Date(Date.now() - 60000),
    accessCount: 8,
    type: 'list',
    namespace: 'search'
  },
  {
    key: 'analytics:dashboard:metrics',
    value: { views: 1500, clicks: 300, conversions: 45 },
    size: 512,
    ttl: 7200,
    createdAt: new Date(Date.now() - 3600000),
    lastAccessed: new Date(Date.now() - 120000),
    accessCount: 23,
    type: 'hash',
    namespace: 'analytics'
  }
];

const mockCacheStats: CacheStats = {
  totalItems: 1250,
  totalSize: 52428800, // 50MB
  hitRate: 0.85,
  missRate: 0.15,
  evictions: 45,
  expired: 12,
  memoryUsage: 41943040, // 40MB
  memoryLimit: 52428800, // 50MB
  averageResponseTime: 2.5,
  keyspaceHits: 15420,
  keyspaceMisses: 2720
};

const mockCacheConfig: CacheConfig = {
  maxMemory: 52428800,
  maxItems: 10000,
  defaultTTL: 3600,
  evictionPolicy: 'lru',
  enableCompression: true,
  enablePersistence: true,
  backupInterval: 3600,
  warmingEnabled: true,
  warmingStrategy: 'hybrid'
};

const mockCacheBackups: CacheBackup[] = [
  {
    id: 'backup_001',
    timestamp: new Date(Date.now() - 3600000),
    size: 20971520,
    itemCount: 1200,
    status: 'completed',
    type: 'full',
    location: '/backups/cache_backup_001.rdb'
  },
  {
    id: 'backup_002',
    timestamp: new Date(Date.now() - 7200000),
    size: 10485760,
    itemCount: 600,
    status: 'completed',
    type: 'incremental',
    location: '/backups/cache_backup_002.rdb'
  }
];

const mockCachePatterns: CachePattern[] = [
  {
    pattern: 'user:profile:*',
    frequency: 150,
    averageSize: 1024,
    hitRate: 0.92,
    lastAccessed: new Date(Date.now() - 300000)
  },
  {
    pattern: 'search:results:*',
    frequency: 85,
    averageSize: 2048,
    hitRate: 0.78,
    lastAccessed: new Date(Date.now() - 600000)
  },
  {
    pattern: 'analytics:*',
    frequency: 45,
    averageSize: 512,
    hitRate: 0.88,
    lastAccessed: new Date(Date.now() - 900000)
  }
];

// Custom hooks
const useCacheManagement = () => {
  const [cacheItems, setCacheItems] = useState<CacheItem[]>(mockCacheItems);
  const [cacheStats, setCacheStats] = useState<CacheStats>(mockCacheStats);
  const [cacheConfig, setCacheConfig] = useState<CacheConfig>(mockCacheConfig);
  const [cacheBackups, setCacheBackups] = useState<CacheBackup[]>(mockCacheBackups);
  const [cachePatterns, setCachePatterns] = useState<CachePattern[]>(mockCachePatterns);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [warmingInProgress, setWarmingInProgress] = useState(false);

  const refreshCacheData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      // In real implementation, fetch data from API
      setCacheStats(mockCacheStats);
      setCacheItems(mockCacheItems);
    } catch (err) {
      setError('Erro ao atualizar dados do cache');
    } finally {
      setLoading(false);
    }
  }, []);

  const invalidateCacheItem = useCallback(async (key: string) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setCacheItems(prev => prev.filter(item => item.key !== key));
      setCacheStats(prev => ({
        ...prev,
        totalItems: prev.totalItems - 1
      }));
    } catch (err) {
      setError('Erro ao invalidar item do cache');
    }
  }, []);

  const invalidateCachePattern = useCallback(async (pattern: string) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      const regex = new RegExp(pattern.replace('*', '.*'));
      const itemsToRemove = cacheItems.filter(item => regex.test(item.key));
      setCacheItems(prev => prev.filter(item => !regex.test(item.key)));
      setCacheStats(prev => ({
        ...prev,
        totalItems: prev.totalItems - itemsToRemove.length
      }));
    } catch (err) {
      setError('Erro ao invalidar padrão do cache');
    }
  }, [cacheItems]);

  const clearAllCache = useCallback(async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      setCacheItems([]);
      setCacheStats(prev => ({
        ...prev,
        totalItems: 0,
        totalSize: 0,
        memoryUsage: 0
      }));
    } catch (err) {
      setError('Erro ao limpar cache');
    }
  }, []);

  const updateCacheConfig = useCallback(async (config: Partial<CacheConfig>) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setCacheConfig(prev => ({ ...prev, ...config }));
    } catch (err) {
      setError('Erro ao atualizar configuração do cache');
    }
  }, []);

  const startCacheWarming = useCallback(async () => {
    setWarmingInProgress(true);
    try {
      // Simulate cache warming
      await new Promise(resolve => setTimeout(resolve, 5000));
      setCacheStats(prev => ({
        ...prev,
        hitRate: Math.min(prev.hitRate + 0.05, 1)
      }));
    } catch (err) {
      setError('Erro ao iniciar cache warming');
    } finally {
      setWarmingInProgress(false);
    }
  }, []);

  const createBackup = useCallback(async (type: 'full' | 'incremental') => {
    try {
      // Simulate backup creation
      await new Promise(resolve => setTimeout(resolve, 3000));
      const newBackup: CacheBackup = {
        id: `backup_${Date.now()}`,
        timestamp: new Date(),
        size: type === 'full' ? 20971520 : 10485760,
        itemCount: type === 'full' ? 1200 : 600,
        status: 'completed',
        type,
        location: `/backups/cache_backup_${Date.now()}.rdb`
      };
      setCacheBackups(prev => [newBackup, ...prev]);
    } catch (err) {
      setError('Erro ao criar backup');
    }
  }, []);

  const restoreBackup = useCallback(async (backupId: string) => {
    try {
      // Simulate backup restoration
      await new Promise(resolve => setTimeout(resolve, 5000));
      setCacheStats(prev => ({
        ...prev,
        totalItems: 1200,
        totalSize: 20971520
      }));
    } catch (err) {
      setError('Erro ao restaurar backup');
    }
  }, []);

  return {
    cacheItems,
    cacheStats,
    cacheConfig,
    cacheBackups,
    cachePatterns,
    loading,
    error,
    warmingInProgress,
    refreshCacheData,
    invalidateCacheItem,
    invalidateCachePattern,
    clearAllCache,
    updateCacheConfig,
    startCacheWarming,
    createBackup,
    restoreBackup
  };
};

// Main component
const CacheManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [warmingDialogOpen, setWarmingDialogOpen] = useState(false);
  const [backupDialogOpen, setBackupDialogOpen] = useState(false);
  const [invalidationDialogOpen, setInvalidationDialogOpen] = useState(false);
  const [invalidationPattern, setInvalidationPattern] = useState('');

  const {
    cacheItems,
    cacheStats,
    cacheConfig,
    cacheBackups,
    cachePatterns,
    loading,
    error,
    warmingInProgress,
    refreshCacheData,
    invalidateCacheItem,
    invalidateCachePattern,
    clearAllCache,
    updateCacheConfig,
    startCacheWarming,
    createBackup,
    restoreBackup
  } = useCacheManagement();

  // Memoized calculations
  const memoryUsagePercentage = useMemo(() => {
    return (cacheStats.memoryUsage / cacheStats.memoryLimit) * 100;
  }, [cacheStats.memoryUsage, cacheStats.memoryLimit]);

  const memoryStatus = useMemo(() => {
    if (memoryUsagePercentage >= 90) return 'critical';
    if (memoryUsagePercentage >= 75) return 'warning';
    return 'normal';
  }, [memoryUsagePercentage]);

  const performanceScore = useMemo(() => {
    const hitRateScore = cacheStats.hitRate * 40;
    const responseTimeScore = Math.max(0, 30 - cacheStats.averageResponseTime * 5);
    const memoryScore = Math.max(0, 30 - memoryUsagePercentage * 0.3);
    return Math.round(hitRateScore + responseTimeScore + memoryScore);
  }, [cacheStats.hitRate, cacheStats.averageResponseTime, memoryUsagePercentage]);

  // Event handlers
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleSelectItem = (key: string) => {
    setSelectedItems(prev => 
      prev.includes(key) 
        ? prev.filter(k => k !== key)
        : [...prev, key]
    );
  };

  const handleSelectAll = () => {
    if (selectedItems.length === cacheItems.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(cacheItems.map(item => item.key));
    }
  };

  const handleInvalidateSelected = async () => {
    for (const key of selectedItems) {
      await invalidateCacheItem(key);
    }
    setSelectedItems([]);
  };

  const handleInvalidatePattern = async () => {
    if (invalidationPattern.trim()) {
      await invalidateCachePattern(invalidationPattern);
      setInvalidationPattern('');
      setInvalidationDialogOpen(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  // Tab content components
  const OverviewTab = () => (
    <Box>
      <Grid container spacing={3}>
        {/* Performance Score */}
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
                color={performanceScore >= 80 ? 'success' : performanceScore >= 60 ? 'warning' : 'error'}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Hit Rate */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="h6" color="textSecondary">
                  Hit Rate
                </Typography>
                <TrendingUpIcon color="success" />
              </Box>
              <Typography variant="h3" color="success.main" sx={{ mt: 2 }}>
                {(cacheStats.hitRate * 100).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {cacheStats.keyspaceHits.toLocaleString()} hits
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Memory Usage */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="h6" color="textSecondary">
                  Memory Usage
                </Typography>
                <Memory color={memoryStatus === 'critical' ? 'error' : memoryStatus === 'warning' ? 'warning' : 'success'} />
              </Box>
              <Typography variant="h3" color={memoryStatus === 'critical' ? 'error' : memoryStatus === 'warning' ? 'warning.main' : 'success.main'} sx={{ mt: 2 }}>
                {formatBytes(cacheStats.memoryUsage)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {memoryUsagePercentage.toFixed(1)}% of {formatBytes(cacheStats.memoryLimit)}
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={memoryUsagePercentage} 
                sx={{ mt: 1 }}
                color={memoryStatus === 'critical' ? 'error' : memoryStatus === 'warning' ? 'warning' : 'success'}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Response Time */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="h6" color="textSecondary">
                  Avg Response Time
                </Typography>
                <Timer color={cacheStats.averageResponseTime < 5 ? 'success' : cacheStats.averageResponseTime < 10 ? 'warning' : 'error'} />
              </Box>
              <Typography variant="h3" color={cacheStats.averageResponseTime < 5 ? 'success.main' : cacheStats.averageResponseTime < 10 ? 'warning.main' : 'error'} sx={{ mt: 2 }}>
                {cacheStats.averageResponseTime}ms
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {cacheStats.totalItems.toLocaleString()} items cached
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Cache Items Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Cache Items</Typography>
                <Box>
                  <Button
                    variant="outlined"
                    startIcon={<DeleteIcon />}
                    onClick={() => setInvalidationDialogOpen(true)}
                    disabled={selectedItems.length === 0}
                    sx={{ mr: 1 }}
                  >
                    Invalidate Selected ({selectedItems.length})
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<RefreshIcon />}
                    onClick={refreshCacheData}
                    disabled={loading}
                  >
                    Refresh
                  </Button>
                </Box>
              </Box>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell padding="checkbox">
                        <input
                          type="checkbox"
                          checked={selectedItems.length === cacheItems.length && cacheItems.length > 0}
                          indeterminate={selectedItems.length > 0 && selectedItems.length < cacheItems.length}
                          onChange={handleSelectAll}
                        />
                      </TableCell>
                      <TableCell>Key</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Size</TableCell>
                      <TableCell>TTL</TableCell>
                      <TableCell>Access Count</TableCell>
                      <TableCell>Last Accessed</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {cacheItems.map((item) => (
                      <TableRow key={item.key}>
                        <TableCell padding="checkbox">
                          <input
                            type="checkbox"
                            checked={selectedItems.includes(item.key)}
                            onChange={() => handleSelectItem(item.key)}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontFamily="monospace">
                            {item.key}
                          </Typography>
                          <Chip label={item.namespace} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={item.type.toUpperCase()} 
                            size="small" 
                            color="primary" 
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>{formatBytes(item.size)}</TableCell>
                        <TableCell>{formatTime(item.ttl)}</TableCell>
                        <TableCell>{item.accessCount}</TableCell>
                        <TableCell>
                          {new Date(item.lastAccessed).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Tooltip title="Invalidate">
                            <IconButton
                              size="small"
                              onClick={() => invalidateCacheItem(item.key)}
                              color="error"
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const ConfigurationTab = () => (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cache Configuration
              </Typography>
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Eviction Policy</InputLabel>
                <Select
                  value={cacheConfig.evictionPolicy}
                  onChange={(e) => updateCacheConfig({ evictionPolicy: e.target.value as any })}
                >
                  <MenuItem value="lru">LRU (Least Recently Used)</MenuItem>
                  <MenuItem value="lfu">LFU (Least Frequently Used)</MenuItem>
                  <MenuItem value="fifo">FIFO (First In, First Out)</MenuItem>
                  <MenuItem value="random">Random</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Max Memory (bytes)"
                type="number"
                value={cacheConfig.maxMemory}
                onChange={(e) => updateCacheConfig({ maxMemory: parseInt(e.target.value) })}
                sx={{ mb: 2 }}
                InputProps={{
                  endAdornment: <InputAdornment position="end">bytes</InputAdornment>,
                }}
              />

              <TextField
                fullWidth
                label="Max Items"
                type="number"
                value={cacheConfig.maxItems}
                onChange={(e) => updateCacheConfig({ maxItems: parseInt(e.target.value) })}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                label="Default TTL (seconds)"
                type="number"
                value={cacheConfig.defaultTTL}
                onChange={(e) => updateCacheConfig({ defaultTTL: parseInt(e.target.value) })}
                sx={{ mb: 2 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={cacheConfig.enableCompression}
                    onChange={(e) => updateCacheConfig({ enableCompression: e.target.checked })}
                  />
                }
                label="Enable Compression"
                sx={{ mb: 1 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={cacheConfig.enablePersistence}
                    onChange={(e) => updateCacheConfig({ enablePersistence: e.target.checked })}
                  />
                }
                label="Enable Persistence"
                sx={{ mb: 1 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={cacheConfig.warmingEnabled}
                    onChange={(e) => updateCacheConfig({ warmingEnabled: e.target.checked })}
                  />
                }
                label="Enable Cache Warming"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cache Warming Configuration
              </Typography>
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Warming Strategy</InputLabel>
                <Select
                  value={cacheConfig.warmingStrategy}
                  onChange={(e) => updateCacheConfig({ warmingStrategy: e.target.value as any })}
                >
                  <MenuItem value="preload">Preload (Load all at startup)</MenuItem>
                  <MenuItem value="lazy">Lazy (Load on demand)</MenuItem>
                  <MenuItem value="hybrid">Hybrid (Combination)</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Backup Interval (seconds)"
                type="number"
                value={cacheConfig.backupInterval}
                onChange={(e) => updateCacheConfig({ backupInterval: parseInt(e.target.value) })}
                sx={{ mb: 2 }}
              />

              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<PlayArrowIcon />}
                  onClick={() => setWarmingDialogOpen(true)}
                  disabled={warmingInProgress}
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  {warmingInProgress ? 'Warming in Progress...' : 'Start Cache Warming'}
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<BackupIcon />}
                  onClick={() => setBackupDialogOpen(true)}
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  Create Backup
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<DeleteIcon />}
                  onClick={clearAllCache}
                  color="error"
                  fullWidth
                >
                  Clear All Cache
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const AnalyticsTab = () => (
    <Box>
      <Grid container spacing={3}>
        {/* Cache Patterns */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cache Patterns
              </Typography>
              
              <List>
                {cachePatterns.map((pattern) => (
                  <ListItem key={pattern.pattern} divider>
                    <ListItemText
                      primary={
                        <Typography variant="body2" fontFamily="monospace">
                          {pattern.pattern}
                        </Typography>
                      }
                      secondary={
                        <Box>
                          <Typography variant="caption" display="block">
                            Frequency: {pattern.frequency} requests/hour
                          </Typography>
                          <Typography variant="caption" display="block">
                            Hit Rate: {(pattern.hitRate * 100).toFixed(1)}%
                          </Typography>
                          <Typography variant="caption" display="block">
                            Avg Size: {formatBytes(pattern.averageSize)}
                          </Typography>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Tooltip title="Invalidate Pattern">
                        <IconButton
                          size="small"
                          onClick={() => invalidateCachePattern(pattern.pattern)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics
              </Typography>
              
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>Hit/Miss Statistics</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box>
                    <Typography variant="body2">
                      Total Hits: {cacheStats.keyspaceHits.toLocaleString()}
                    </Typography>
                    <Typography variant="body2">
                      Total Misses: {cacheStats.keyspaceMisses.toLocaleString()}
                    </Typography>
                    <Typography variant="body2">
                      Hit Rate: {(cacheStats.hitRate * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="body2">
                      Miss Rate: {(cacheStats.missRate * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>Memory Statistics</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box>
                    <Typography variant="body2">
                      Total Items: {cacheStats.totalItems.toLocaleString()}
                    </Typography>
                    <Typography variant="body2">
                      Total Size: {formatBytes(cacheStats.totalSize)}
                    </Typography>
                    <Typography variant="body2">
                      Memory Usage: {formatBytes(cacheStats.memoryUsage)}
                    </Typography>
                    <Typography variant="body2">
                      Memory Limit: {formatBytes(cacheStats.memoryLimit)}
                    </Typography>
                    <Typography variant="body2">
                      Usage Percentage: {memoryUsagePercentage.toFixed(1)}%
                    </Typography>
                  </Box>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>Eviction Statistics</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box>
                    <Typography variant="body2">
                      Total Evictions: {cacheStats.evictions}
                    </Typography>
                    <Typography variant="body2">
                      Expired Items: {cacheStats.expired}
                    </Typography>
                    <Typography variant="body2">
                      Average Response Time: {cacheStats.averageResponseTime}ms
                    </Typography>
                  </Box>
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        </Grid>

        {/* Backup History */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Backup History
              </Typography>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Timestamp</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Size</TableCell>
                      <TableCell>Items</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {cacheBackups.map((backup) => (
                      <TableRow key={backup.id}>
                        <TableCell>{backup.id}</TableCell>
                        <TableCell>
                          {new Date(backup.timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={backup.type} 
                            size="small" 
                            color={backup.type === 'full' ? 'primary' : 'secondary'}
                          />
                        </TableCell>
                        <TableCell>{formatBytes(backup.size)}</TableCell>
                        <TableCell>{backup.itemCount.toLocaleString()}</TableCell>
                        <TableCell>
                          <Chip 
                            label={backup.status} 
                            size="small" 
                            color={backup.status === 'completed' ? 'success' : backup.status === 'failed' ? 'error' : 'warning'}
                            icon={backup.status === 'completed' ? <CheckCircleIcon /> : backup.status === 'failed' ? <ErrorIcon /> : <InfoIcon />}
                          />
                        </TableCell>
                        <TableCell>
                          <Tooltip title="Restore Backup">
                            <IconButton
                              size="small"
                              onClick={() => restoreBackup(backup.id)}
                              color="primary"
                            >
                              <RestoreIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Cache Management
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Advanced cache management and monitoring system
          </Typography>
        </Box>
        <Box>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={refreshCacheData}
            disabled={loading}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<SettingsIcon />}
            onClick={() => setConfigDialogOpen(true)}
          >
            Settings
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loading Progress */}
      {loading && (
        <LinearProgress sx={{ mb: 3 }} />
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Overview" />
          <Tab label="Configuration" />
          <Tab label="Analytics" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && <OverviewTab />}
      {activeTab === 1 && <ConfigurationTab />}
      {activeTab === 2 && <AnalyticsTab />}

      {/* Configuration Dialog */}
      <Dialog open={configDialogOpen} onClose={() => setConfigDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Cache Configuration</DialogTitle>
        <DialogContent>
          <ConfigurationTab />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Warming Dialog */}
      <Dialog open={warmingDialogOpen} onClose={() => setWarmingDialogOpen(false)}>
        <DialogTitle>Cache Warming</DialogTitle>
        <DialogContent>
          <Typography>
            This will preload frequently accessed data into the cache to improve performance.
            The process may take several minutes.
          </Typography>
          {warmingInProgress && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
              <Typography variant="body2" sx={{ mt: 1 }}>
                Warming in progress...
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWarmingDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={startCacheWarming} 
            disabled={warmingInProgress}
            variant="contained"
          >
            Start Warming
          </Button>
        </DialogActions>
      </Dialog>

      {/* Backup Dialog */}
      <Dialog open={backupDialogOpen} onClose={() => setBackupDialogOpen(false)}>
        <DialogTitle>Create Backup</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 1 }}>
            <InputLabel>Backup Type</InputLabel>
            <Select
              value="full"
              onChange={(e) => createBackup(e.target.value as 'full' | 'incremental')}
            >
              <MenuItem value="full">Full Backup</MenuItem>
              <MenuItem value="incremental">Incremental Backup</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBackupDialogOpen(false)}>Cancel</Button>
          <Button onClick={() => createBackup('full')} variant="contained">
            Create Backup
          </Button>
        </DialogActions>
      </Dialog>

      {/* Invalidation Dialog */}
      <Dialog open={invalidationDialogOpen} onClose={() => setInvalidationDialogOpen(false)}>
        <DialogTitle>Invalidate Cache Pattern</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Pattern (e.g., user:*, search:*)"
            value={invalidationPattern}
            onChange={(e) => setInvalidationPattern(e.target.value)}
            placeholder="user:profile:*"
            sx={{ mt: 1 }}
          />
          <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
            Use * as wildcard. This will invalidate all keys matching the pattern.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInvalidationDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleInvalidatePattern} variant="contained" color="error">
            Invalidate
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CacheManagement; 
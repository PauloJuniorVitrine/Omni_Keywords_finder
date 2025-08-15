/**
 * DashboardGrid - Grid responsivo para organizar widgets do dashboard
 * 
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 2.1.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { useState, useMemo } from 'react';
import {
  Grid,
  Box,
  Typography,
  Button,
  IconButton,
  Tooltip,
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
  Chip
} from '@mui/material';
import {
  Add,
  Settings,
  ViewModule,
  ViewList,
  FilterList,
  Refresh
} from '@mui/icons-material';
import DashboardWidget from './DashboardWidget';

interface DashboardConfig {
  layout: 'grid' | 'list';
  refreshInterval: number;
  showCharts: boolean;
  autoRefresh: boolean;
}

interface DashboardGridProps {
  widgets: Array<{
    id: string;
    title: string;
    type: 'metric' | 'chart' | 'table';
    size: 'small' | 'medium' | 'large';
    config: any;
  }>;
  onWidgetRefresh?: (widgetId: string) => void;
  onWidgetConfigure?: (widgetId: string) => void;
  onAddWidget?: () => void;
  isLoading?: boolean;
}

const DashboardGrid: React.FC<DashboardGridProps> = ({
  widgets,
  onWidgetRefresh,
  onWidgetConfigure,
  onAddWidget,
  isLoading = false
}) => {
  const [config, setConfig] = useState<DashboardConfig>({
    layout: 'grid',
    refreshInterval: 30000,
    showCharts: true,
    autoRefresh: true
  });

  const [showConfigDialog, setShowConfigDialog] = useState(false);

  // Mock data para demonstração - em produção viria das APIs
  const mockMetricData = useMemo(() => ({
    keywords: {
      value: 15420,
      change: 12.5,
      trend: 'up' as const,
      unit: 'keywords',
      color: '#1976d2'
    },
    niches: {
      value: 847,
      change: -2.1,
      trend: 'down' as const,
      unit: 'nichos',
      color: '#388e3c'
    },
    performance: {
      value: 94.2,
      change: 5.8,
      trend: 'up' as const,
      unit: '%',
      color: '#f57c00'
    },
    revenue: {
      value: 125000,
      change: 18.3,
      trend: 'up' as const,
      unit: 'R$',
      color: '#7b1fa2'
    }
  }), []);

  const mockChartData = useMemo(() => [
    { date: 'Jan', value: 12000 },
    { date: 'Fev', value: 13500 },
    { date: 'Mar', value: 14200 },
    { date: 'Abr', value: 15420 },
    { date: 'Mai', value: 16800 },
    { date: 'Jun', value: 17500 }
  ], []);

  const handleRefresh = (widgetId: string) => {
    onWidgetRefresh?.(widgetId);
  };

  const handleConfigure = (widgetId: string) => {
    onWidgetConfigure?.(widgetId);
  };

  const handleConfigChange = (key: keyof DashboardConfig, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const renderWidget = (widget: any) => {
    const metricData = mockMetricData[widget.id as keyof typeof mockMetricData];
    
    if (!metricData) return null;

    return (
      <Grid item xs={12} sm={6} md={4} lg={3} key={widget.id}>
        <DashboardWidget
          title={widget.title}
          metric={metricData}
          chartData={config.showCharts ? mockChartData : []}
          isLoading={isLoading}
          onRefresh={() => handleRefresh(widget.id)}
          onConfigure={() => handleConfigure(widget.id)}
          showChart={config.showCharts}
          size={widget.size}
        />
      </Grid>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" color="text.primary">
          Dashboard
        </Typography>
        
        <Box display="flex" gap={2} alignItems="center">
          {/* Layout Toggle */}
          <Box display="flex" border={1} borderColor="divider" borderRadius={1}>
            <Tooltip title="Layout em grid">
              <IconButton
                size="small"
                onClick={() => handleConfigChange('layout', 'grid')}
                color={config.layout === 'grid' ? 'primary' : 'default'}
              >
                <ViewModule />
              </IconButton>
            </Tooltip>
            <Tooltip title="Layout em lista">
              <IconButton
                size="small"
                onClick={() => handleConfigChange('layout', 'list')}
                color={config.layout === 'list' ? 'primary' : 'default'}
              >
                <ViewList />
              </IconButton>
            </Tooltip>
          </Box>

          {/* Auto Refresh Toggle */}
          <FormControlLabel
            control={
              <Switch
                checked={config.autoRefresh}
                onChange={(e) => handleConfigChange('autoRefresh', e.target.checked)}
                size="small"
              />
            }
            label="Auto-refresh"
          />

          {/* Configuration */}
          <Tooltip title="Configurar dashboard">
            <IconButton onClick={() => setShowConfigDialog(true)}>
              <Settings />
            </IconButton>
          </Tooltip>

          {/* Add Widget */}
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={onAddWidget}
            size="small"
          >
            Adicionar Widget
          </Button>
        </Box>
      </Box>

      {/* Filters */}
      <Box display="flex" gap={2} mb={3} alignItems="center">
        <Chip label="Todos os nichos" variant="outlined" />
        <Chip label="Últimos 30 dias" variant="outlined" />
        <Chip label="Performance alta" variant="outlined" />
        
        <Tooltip title="Mais filtros">
          <IconButton size="small">
            <FilterList />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Widgets Grid */}
      <Grid container spacing={3}>
        {widgets.map(renderWidget)}
      </Grid>

      {/* Configuration Dialog */}
      <Dialog 
        open={showConfigDialog} 
        onClose={() => setShowConfigDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Configurações do Dashboard</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={3} mt={1}>
            <FormControl fullWidth>
              <InputLabel>Intervalo de atualização</InputLabel>
              <Select
                value={config.refreshInterval}
                onChange={(e) => handleConfigChange('refreshInterval', e.target.value)}
                label="Intervalo de atualização"
              >
                <MenuItem value={15000}>15 segundos</MenuItem>
                <MenuItem value={30000}>30 segundos</MenuItem>
                <MenuItem value={60000}>1 minuto</MenuItem>
                <MenuItem value={300000}>5 minutos</MenuItem>
              </Select>
            </FormControl>

            <FormControlLabel
              control={
                <Switch
                  checked={config.showCharts}
                  onChange={(e) => handleConfigChange('showCharts', e.target.checked)}
                />
              }
              label="Mostrar gráficos nos widgets"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={config.autoRefresh}
                  onChange={(e) => handleConfigChange('autoRefresh', e.target.checked)}
                />
              }
              label="Atualização automática"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfigDialog(false)}>
            Cancelar
          </Button>
          <Button variant="contained" onClick={() => setShowConfigDialog(false)}>
            Salvar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DashboardGrid; 
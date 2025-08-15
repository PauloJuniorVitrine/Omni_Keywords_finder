/**
 * OrchestratorDashboard - Dashboard de Controle do Orquestrador
 * 
 * Componente React para monitoramento e controle do fluxo de trabalho
 * do Omni Keywords Finder.
 * 
 * Tracing ID: DASHBOARD_001_20241227
 * Versão: 1.0
 * Autor: IA-Cursor
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  LinearProgress,
  Alert,
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
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Stop,
  Refresh,
  Settings,
  Timeline,
  Assessment,
  Schedule,
  Template
} from '@mui/icons-material';

interface OrchestratorStatus {
  status: 'idle' | 'running' | 'paused' | 'completed' | 'error';
  currentSession?: string;
  currentNicho?: string;
  currentEtapa?: string;
  progress: number;
  totalNichos: number;
  completedNichos: number;
  startTime?: string;
  estimatedEndTime?: string;
}

interface NichoStatus {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  progress: number;
  startTime?: string;
  endTime?: string;
  keywordsProcessed: number;
  promptsGenerated: number;
}

interface MetricData {
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
}

interface DashboardData {
  orchestratorStatus: OrchestratorStatus;
  nichosStatus: NichoStatus[];
  metrics: MetricData[];
  recentLogs: string[];
  schedules: any[];
  templates: any[];
}

const OrchestratorDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [controlDialogOpen, setControlDialogOpen] = useState(false);
  const [selectedNichos, setSelectedNichos] = useState<string[]>([]);
  const [availableNichos, setAvailableNichos] = useState<string[]>([]);

  // Carregar dados do dashboard
  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 5000); // Atualizar a cada 5s
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      // Aqui você faria a chamada real para a API
      const mockData: DashboardData = {
        orchestratorStatus: {
          status: 'running',
          currentSession: 'fluxo_abc123',
          currentNicho: 'tecnologia',
          currentEtapa: 'processamento',
          progress: 65,
          totalNichos: 3,
          completedNichos: 2,
          startTime: '2024-12-27T10:00:00Z',
          estimatedEndTime: '2024-12-27T11:30:00Z'
        },
        nichosStatus: [
          {
            id: '1',
            name: 'tecnologia',
            status: 'running',
            progress: 80,
            startTime: '2024-12-27T10:00:00Z',
            keywordsProcessed: 150,
            promptsGenerated: 450
          },
          {
            id: '2',
            name: 'saude',
            status: 'completed',
            progress: 100,
            startTime: '2024-12-27T10:30:00Z',
            endTime: '2024-12-27T11:00:00Z',
            keywordsProcessed: 100,
            promptsGenerated: 300
          },
          {
            id: '3',
            name: 'financas',
            status: 'pending',
            progress: 0,
            keywordsProcessed: 0,
            promptsGenerated: 0
          }
        ],
        metrics: [
          { name: 'Keywords Processadas', value: 250, unit: 'total', trend: 'up' },
          { name: 'Prompts Gerados', value: 750, unit: 'total', trend: 'up' },
          { name: 'Taxa de Sucesso', value: 95, unit: '%', trend: 'stable' },
          { name: 'Tempo Médio', value: 45, unit: 'min', trend: 'down' }
        ],
        recentLogs: [
          '2024-12-27 11:15:00 - Nicho tecnologia: 80% concluído',
          '2024-12-27 11:10:00 - Nicho saude: Processamento concluído',
          '2024-12-27 11:05:00 - Iniciando validação de dados',
          '2024-12-27 11:00:00 - Nicho saude: 100% concluído'
        ],
        schedules: [
          { id: '1', name: 'Processamento Diário', time: '02:00', enabled: true },
          { id: '2', name: 'Backup Semanal', time: '03:00', enabled: false }
        ],
        templates: [
          { id: '1', name: 'Template Tecnologia', category: 'technology' },
          { id: '2', name: 'Template Saúde', category: 'health' }
        ]
      };

      setDashboardData(mockData);
      setAvailableNichos(['tecnologia', 'saude', 'financas', 'educacao', 'entretenimento']);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar dados do dashboard');
      console.error('Erro ao carregar dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartFlow = async () => {
    try {
      if (selectedNichos.length === 0) {
        setError('Selecione pelo menos um nicho');
        return;
      }

      // Aqui você faria a chamada real para iniciar o fluxo
      console.log('Iniciando fluxo para nichos:', selectedNichos);
      
      setControlDialogOpen(false);
      setSelectedNichos([]);
      
      // Recarregar dados
      await loadDashboardData();
    } catch (err) {
      setError('Erro ao iniciar fluxo');
      console.error('Erro ao iniciar fluxo:', err);
    }
  };

  const handlePauseFlow = async () => {
    try {
      // Aqui você faria a chamada real para pausar
      console.log('Pausando fluxo');
      await loadDashboardData();
    } catch (err) {
      setError('Erro ao pausar fluxo');
    }
  };

  const handleStopFlow = async () => {
    try {
      // Aqui você faria a chamada real para parar
      console.log('Parando fluxo');
      await loadDashboardData();
    } catch (err) {
      setError('Erro ao parar fluxo');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'primary';
      case 'completed': return 'success';
      case 'error': return 'error';
      case 'pending': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <PlayArrow />;
      case 'completed': return <Timeline />;
      case 'error': return <Alert />;
      case 'pending': return <Schedule />;
      default: return <Schedule />;
    }
  };

  if (loading && !dashboardData) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>Carregando dashboard...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Box>
    );
  }

  if (!dashboardData) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">Nenhum dado disponível</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Dashboard do Orquestrador
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={() => setControlDialogOpen(true)}
            sx={{ mr: 1 }}
          >
            Iniciar Fluxo
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadDashboardData}
          >
            Atualizar
          </Button>
        </Box>
      </Box>

      {/* Status Principal */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Status do Orquestrador
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Chip
                  label={dashboardData.orchestratorStatus.status.toUpperCase()}
                  color={getStatusColor(dashboardData.orchestratorStatus.status)}
                  sx={{ mr: 2 }}
                />
                {dashboardData.orchestratorStatus.currentNicho && (
                  <Typography variant="body2">
                    Nicho atual: {dashboardData.orchestratorStatus.currentNicho}
                  </Typography>
                )}
              </Box>
              <LinearProgress
                variant="determinate"
                value={dashboardData.orchestratorStatus.progress}
                sx={{ height: 10, borderRadius: 5 }}
              />
              <Typography variant="body2" sx={{ mt: 1 }}>
                Progresso: {dashboardData.orchestratorStatus.progress}% 
                ({dashboardData.orchestratorStatus.completedNichos}/{dashboardData.orchestratorStatus.totalNichos} nichos)
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="outlined"
                  startIcon={<Pause />}
                  onClick={handlePauseFlow}
                  disabled={dashboardData.orchestratorStatus.status !== 'running'}
                >
                  Pausar
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<Stop />}
                  onClick={handleStopFlow}
                  disabled={dashboardData.orchestratorStatus.status === 'idle'}
                >
                  Parar
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Métricas */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {dashboardData.metrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  {metric.name}
                </Typography>
                <Typography variant="h4" component="div">
                  {metric.value}{metric.unit}
                </Typography>
                <Chip
                  label={metric.trend === 'up' ? '↗' : metric.trend === 'down' ? '↘' : '→'}
                  size="small"
                  color={metric.trend === 'up' ? 'success' : metric.trend === 'down' ? 'error' : 'default'}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Status dos Nichos */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Status dos Nichos
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Nicho</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Progresso</TableCell>
                  <TableCell>Keywords</TableCell>
                  <TableCell>Prompts</TableCell>
                  <TableCell>Tempo</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {dashboardData.nichosStatus.map((nicho) => (
                  <TableRow key={nicho.id}>
                    <TableCell>{nicho.name}</TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(nicho.status)}
                        label={nicho.status}
                        color={getStatusColor(nicho.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ width: '100%', mr: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={nicho.progress}
                            sx={{ height: 6 }}
                          />
                        </Box>
                        <Box sx={{ minWidth: 35 }}>
                          <Typography variant="body2" color="text.secondary">
                            {nicho.progress}%
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>{nicho.keywordsProcessed}</TableCell>
                    <TableCell>{nicho.promptsGenerated}</TableCell>
                    <TableCell>
                      {nicho.startTime && (
                        <Typography variant="body2">
                          {new Date(nicho.startTime).toLocaleTimeString()}
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Logs Recentes */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Logs Recentes
              </Typography>
              <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                {dashboardData.recentLogs.map((log, index) => (
                  <Typography key={index} variant="body2" sx={{ mb: 1, fontFamily: 'monospace' }}>
                    {log}
                  </Typography>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Agendamentos
              </Typography>
              {dashboardData.schedules.map((schedule) => (
                <Box key={schedule.id} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">{schedule.name}</Typography>
                  <Chip
                    label={schedule.enabled ? 'Ativo' : 'Inativo'}
                    color={schedule.enabled ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Dialog de Controle */}
      <Dialog open={controlDialogOpen} onClose={() => setControlDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Iniciar Novo Fluxo</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Selecionar Nichos</InputLabel>
            <Select
              multiple
              value={selectedNichos}
              onChange={(e) => setSelectedNichos(e.target.value as string[])}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value} label={value} />
                  ))}
                </Box>
              )}
            >
              {availableNichos.map((nicho) => (
                <MenuItem key={nicho} value={nicho}>
                  {nicho}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setControlDialogOpen(false)}>Cancelar</Button>
          <Button onClick={handleStartFlow} variant="contained">
            Iniciar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OrchestratorDashboard; 
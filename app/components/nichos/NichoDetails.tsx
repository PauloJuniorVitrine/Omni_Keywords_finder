/**
 * NichoDetails.tsx
 * 
 * Visualização detalhada de nicho com métricas e histórico
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_007
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Visualização detalhada
 * - Métricas específicas
 * - Histórico de ações
 * - Ações rápidas
 * - Integração com APIs do backend
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  IconButton,
  Tooltip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  LinearProgress,
  Alert,
  Skeleton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Badge,
  useTheme,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  History as HistoryIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  ArrowBack as ArrowBackIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

// Tipos
interface Nicho {
  id: string;
  nome: string;
  descricao: string;
  categoria: string;
  status: 'ativo' | 'inativo' | 'pendente';
  totalKeywords: number;
  execucoesRealizadas: number;
  ultimaExecucao: Date | null;
  dataCriacao: Date;
  dataAtualizacao: Date;
  keywords: string[];
  configuracao: {
    maxKeywords: number;
    intervaloExecucao: number;
    ativo: boolean;
  };
}

interface Execucao {
  id: string;
  dataInicio: Date;
  dataFim: Date | null;
  status: 'em_andamento' | 'concluida' | 'falhou' | 'cancelada';
  keywordsProcessadas: number;
  keywordsEncontradas: number;
  tempoExecucao: number;
  erro?: string;
}

interface Metrica {
  nome: string;
  valor: number;
  unidade: string;
  variacao: number;
  tendencia: 'up' | 'down' | 'stable';
}

interface AcaoHistorico {
  id: string;
  tipo: 'criacao' | 'edicao' | 'execucao' | 'exclusao' | 'configuracao';
  descricao: string;
  data: Date;
  usuario: string;
  detalhes?: any;
}

interface NichoDetailsProps {
  nichoId: string;
  onEdit?: (nichoId: string) => void;
  onDelete?: (nichoId: string) => void;
  onExecute?: (nichoId: string) => void;
  onExport?: (nichoId: string) => void;
}

/**
 * Componente de detalhes do nicho
 */
const NichoDetails: React.FC<NichoDetailsProps> = ({
  nichoId,
  onEdit,
  onDelete,
  onExecute,
  onExport,
}) => {
  // Estados
  const [nicho, setNicho] = useState<Nicho | null>(null);
  const [execucoes, setExecucoes] = useState<Execucao[]>([]);
  const [metricas, setMetricas] = useState<Metrica[]>([]);
  const [historico, setHistorico] = useState<AcaoHistorico[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'execucoes' | 'historico' | 'configuracao'>('overview');

  // Hooks
  const theme = useTheme();
  const navigate = useNavigate();

  // Efeitos
  useEffect(() => {
    loadNichoDetails();
  }, [nichoId]);

  /**
   * Carrega detalhes do nicho
   */
  const loadNichoDetails = async () => {
    try {
      setLoading(true);
      
      // TODO: Implementar chamadas reais da API
      // const [nichoData, execucoesData, metricasData, historicoData] = await Promise.all([
      //   api.get(`/nichos/${nichoId}`),
      //   api.get(`/nichos/${nichoId}/execucoes`),
      //   api.get(`/nichos/${nichoId}/metricas`),
      //   api.get(`/nichos/${nichoId}/historico`),
      // ]);

      // Mock de dados
      const mockNicho: Nicho = {
        id: nichoId,
        nome: 'Tecnologia e Inovação',
        descricao: 'Nichos relacionados a tecnologia, inovação e desenvolvimento de software',
        categoria: 'Tecnologia',
        status: 'ativo',
        totalKeywords: 1250,
        execucoesRealizadas: 45,
        ultimaExecucao: new Date('2025-01-26T14:30:00'),
        dataCriacao: new Date('2024-12-01'),
        dataAtualizacao: new Date('2025-01-26'),
        keywords: ['tecnologia', 'inovação', 'software', 'desenvolvimento', 'programação'],
        configuracao: {
          maxKeywords: 1000,
          intervaloExecucao: 24,
          ativo: true,
        },
      };

      const mockExecucoes: Execucao[] = [
        {
          id: '1',
          dataInicio: new Date('2025-01-26T14:30:00'),
          dataFim: new Date('2025-01-26T15:45:00'),
          status: 'concluida',
          keywordsProcessadas: 1250,
          keywordsEncontradas: 890,
          tempoExecucao: 75,
        },
        {
          id: '2',
          dataInicio: new Date('2025-01-25T10:00:00'),
          dataFim: new Date('2025-01-25T11:15:00'),
          status: 'concluida',
          keywordsProcessadas: 1200,
          keywordsEncontradas: 850,
          tempoExecucao: 75,
        },
        {
          id: '3',
          dataInicio: new Date('2025-01-24T09:00:00'),
          dataFim: null,
          status: 'em_andamento',
          keywordsProcessadas: 800,
          keywordsEncontradas: 0,
          tempoExecucao: 0,
        },
      ];

      const mockMetricas: Metrica[] = [
        {
          nome: 'Taxa de Sucesso',
          valor: 85.5,
          unidade: '%',
          variacao: 2.3,
          tendencia: 'up',
        },
        {
          nome: 'Tempo Médio',
          valor: 72.5,
          unidade: 'min',
          variacao: -5.2,
          tendencia: 'down',
        },
        {
          nome: 'Keywords Encontradas',
          valor: 890,
          unidade: '',
          variacao: 12.5,
          tendencia: 'up',
        },
      ];

      const mockHistorico: AcaoHistorico[] = [
        {
          id: '1',
          tipo: 'execucao',
          descricao: 'Execução iniciada',
          data: new Date('2025-01-26T14:30:00'),
          usuario: 'admin@example.com',
        },
        {
          id: '2',
          tipo: 'edicao',
          descricao: 'Configurações atualizadas',
          data: new Date('2025-01-25T16:20:00'),
          usuario: 'admin@example.com',
        },
        {
          id: '3',
          tipo: 'execucao',
          descricao: 'Execução concluída com sucesso',
          data: new Date('2025-01-25T11:15:00'),
          usuario: 'sistema',
        },
      ];

      setNicho(mockNicho);
      setExecucoes(mockExecucoes);
      setMetricas(mockMetricas);
      setHistorico(mockHistorico);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar detalhes do nicho');
      console.error('Erro ao carregar nicho:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Renderiza status com chip colorido
   */
  const renderStatus = (status: string) => {
    const statusConfig = {
      ativo: { color: 'success', label: 'Ativo', icon: <CheckCircleIcon /> },
      inativo: { color: 'error', label: 'Inativo', icon: <ErrorIcon /> },
      pendente: { color: 'warning', label: 'Pendente', icon: <WarningIcon /> },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pendente;

    return (
      <Chip
        icon={config.icon}
        label={config.label}
        color={config.color as any}
        variant="outlined"
      />
    );
  };

  /**
   * Renderiza status de execução
   */
  const renderExecucaoStatus = (status: string) => {
    const statusConfig = {
      em_andamento: { color: 'info', label: 'Em Andamento', icon: <ScheduleIcon /> },
      concluida: { color: 'success', label: 'Concluída', icon: <CheckCircleIcon /> },
      falhou: { color: 'error', label: 'Falhou', icon: <ErrorIcon /> },
      cancelada: { color: 'default', label: 'Cancelada', icon: <WarningIcon /> },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.em_andamento;

    return (
      <Chip
        icon={config.icon}
        label={config.label}
        color={config.color as any}
        size="small"
      />
    );
  };

  /**
   * Renderiza métrica com tendência
   */
  const renderMetrica = (metrica: Metrica) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h4" component="div" fontWeight={600}>
              {metrica.valor}{metrica.unidade}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {metrica.nome}
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <Typography
              variant="body2"
              color={metrica.tendencia === 'up' ? 'success.main' : metrica.tendencia === 'down' ? 'error.main' : 'text.secondary'}
              sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
            >
              <TrendingUpIcon
                sx={{
                  transform: metrica.tendencia === 'down' ? 'rotate(180deg)' : 'none',
                  fontSize: 16,
                }}
              />
              {metrica.variacao > 0 ? '+' : ''}{metrica.variacao}%
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  /**
   * Renderiza tipo de ação do histórico
   */
  const renderTipoAcao = (tipo: string) => {
    const tipoConfig = {
      criacao: { color: 'success', label: 'Criação' },
      edicao: { color: 'info', label: 'Edição' },
      execucao: { color: 'primary', label: 'Execução' },
      exclusao: { color: 'error', label: 'Exclusão' },
      configuracao: { color: 'warning', label: 'Configuração' },
    };

    const config = tipoConfig[tipo as keyof typeof tipoConfig] || tipoConfig.edicao;

    return (
      <Chip
        label={config.label}
        color={config.color as any}
        size="small"
        variant="outlined"
      />
    );
  };

  /**
   * Renderiza overview do nicho
   */
  const renderOverview = () => (
    <Grid container spacing={3}>
      {/* Informações Básicas */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Informações do Nicho
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="textSecondary">
                  Nome
                </Typography>
                <Typography variant="body1" fontWeight={500}>
                  {nicho?.nome}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="textSecondary">
                  Categoria
                </Typography>
                <Chip label={nicho?.categoria} size="small" />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="textSecondary">
                  Descrição
                </Typography>
                <Typography variant="body2">
                  {nicho?.descricao}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="textSecondary">
                  Status
                </Typography>
                {nicho && renderStatus(nicho.status)}
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="textSecondary">
                  Criado em
                </Typography>
                <Typography variant="body2">
                  {nicho?.dataCriacao.toLocaleDateString('pt-BR')}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Métricas */}
      <Grid item xs={12} md={4}>
        <Typography variant="h6" gutterBottom>
          Métricas
        </Typography>
        <Grid container spacing={2}>
          {metricas.map((metrica, index) => (
            <Grid item xs={12} key={index}>
              {renderMetrica(metrica)}
            </Grid>
          ))}
        </Grid>
      </Grid>

      {/* Keywords */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Keywords ({nicho?.keywords.length})
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {nicho?.keywords.map((keyword, index) => (
                <Chip
                  key={index}
                  label={keyword}
                  size="small"
                  variant="outlined"
                />
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  /**
   * Renderiza tabela de execuções
   */
  const renderExecucoes = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Histórico de Execuções
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Data</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="center">Keywords Processadas</TableCell>
                <TableCell align="center">Keywords Encontradas</TableCell>
                <TableCell align="center">Tempo</TableCell>
                <TableCell align="center">Ações</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {execucoes.map((execucao) => (
                <TableRow key={execucao.id}>
                  <TableCell>
                    {execucao.dataInicio.toLocaleDateString('pt-BR')}
                    <br />
                    <Typography variant="caption" color="textSecondary">
                      {execucao.dataInicio.toLocaleTimeString('pt-BR')}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {renderExecucaoStatus(execucao.status)}
                  </TableCell>
                  <TableCell align="center">
                    {execucao.keywordsProcessadas.toLocaleString()}
                  </TableCell>
                  <TableCell align="center">
                    {execucao.keywordsEncontradas.toLocaleString()}
                  </TableCell>
                  <TableCell align="center">
                    {execucao.tempoExecucao > 0 ? `${execucao.tempoExecucao} min` : '-'}
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title="Ver detalhes">
                      <IconButton size="small">
                        <AnalyticsIcon />
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
  );

  /**
   * Renderiza histórico de ações
   */
  const renderHistorico = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Histórico de Ações
        </Typography>
        <List>
          {historico.map((acao) => (
            <ListItem key={acao.id} divider>
              <ListItemIcon>
                <Avatar sx={{ width: 32, height: 32 }}>
                  <HistoryIcon />
                </Avatar>
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {renderTipoAcao(acao.tipo)}
                    <Typography variant="body2">
                      {acao.descricao}
                    </Typography>
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="caption" color="textSecondary">
                      {acao.data.toLocaleDateString('pt-BR')} às {acao.data.toLocaleTimeString('pt-BR')}
                    </Typography>
                    <br />
                    <Typography variant="caption" color="textSecondary">
                      Por: {acao.usuario}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );

  /**
   * Renderiza configurações
   */
  const renderConfiguracao = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Configurações
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="textSecondary">
              Máximo de Keywords
            </Typography>
            <Typography variant="body1">
              {nicho?.configuracao.maxKeywords.toLocaleString()}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="textSecondary">
              Intervalo de Execução
            </Typography>
            <Typography variant="body1">
              {nicho?.configuracao.intervaloExecucao} horas
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="textSecondary">
              Status da Configuração
            </Typography>
            <Chip
              label={nicho?.configuracao.ativo ? 'Ativo' : 'Inativo'}
              color={nicho?.configuracao.ativo ? 'success' : 'error'}
              size="small"
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  // Loading state
  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="rectangular" height={60} sx={{ mb: 2 }} />
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Skeleton variant="rectangular" height={200} />
          </Grid>
          <Grid item xs={12} md={4}>
            <Skeleton variant="rectangular" height={200} />
          </Grid>
        </Grid>
      </Box>
    );
  }

  // Error state
  if (error || !nicho) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          {error || 'Nicho não encontrado'}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton onClick={() => navigate(-1)}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" component="h1" fontWeight={600}>
            {nicho.nome}
          </Typography>
          {renderStatus(nicho.status)}
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Executar">
            <IconButton
              color="primary"
              onClick={() => onExecute?.(nicho.id)}
            >
              <PlayIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Exportar">
            <IconButton
              onClick={() => onExport?.(nicho.id)}
            >
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Editar">
            <IconButton
              onClick={() => onEdit?.(nicho.id)}
            >
              <EditIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Excluir">
            <IconButton
              color="error"
              onClick={() => onDelete?.(nicho.id)}
            >
              <DeleteIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {[
            { key: 'overview', label: 'Visão Geral', icon: <AnalyticsIcon /> },
            { key: 'execucoes', label: 'Execuções', icon: <PlayIcon /> },
            { key: 'historico', label: 'Histórico', icon: <HistoryIcon /> },
            { key: 'configuracao', label: 'Configuração', icon: <SettingsIcon /> },
          ].map((tab) => (
            <Button
              key={tab.key}
              variant={activeTab === tab.key ? 'contained' : 'outlined'}
              startIcon={tab.icon}
              onClick={() => setActiveTab(tab.key as any)}
              size="small"
            >
              {tab.label}
            </Button>
          ))}
        </Box>
      </Box>

      {/* Content */}
      {activeTab === 'overview' && renderOverview()}
      {activeTab === 'execucoes' && renderExecucoes()}
      {activeTab === 'historico' && renderHistorico()}
      {activeTab === 'configuracao' && renderConfiguracao()}
    </Box>
  );
};

export default NichoDetails; 
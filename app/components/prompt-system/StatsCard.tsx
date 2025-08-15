/**
 * Card de Estatísticas
 * 
 * Componente para exibir métricas e estatísticas do sistema
 * 
 * Tracing ID: FIXTYPE-001_COMPONENT_UPDATE_20241227_008
 * Data: 2024-12-27
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Grid,
  Tooltip
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Speed as SpeedIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { EstatisticasGerais } from '../../types/api-sync';

interface StatsCardProps {
  stats: EstatisticasGerais;
  loading?: boolean;
}

export const StatsCard: React.FC<StatsCardProps> = ({ stats, loading = false }) => {
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('pt-BR').format(num);
  };

  const formatTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatPercentage = (value: number, total: number) => {
    if (total === 0) return '0%';
    return `${((value / total) * 100).toFixed(1)}%`;
  };

  const getStatusColor = (value: number, threshold: number) => {
    if (value >= threshold) return 'success';
    if (value >= threshold * 0.8) return 'warning';
    return 'error';
  };

  const getStatusIcon = (value: number, threshold: number) => {
    if (value >= threshold) return <CheckCircleIcon color="success" />;
    if (value >= threshold * 0.8) return <WarningIcon color="warning" />;
    return <ErrorIcon color="error" />;
  };

  const statsItems = [
    {
      title: 'Total de Nichos',
      value: stats.total_nichos,
      icon: '📊',
      color: 'primary' as const,
      description: 'Nichos cadastrados no sistema'
    },
    {
      title: 'Total de Categorias',
      value: stats.total_categorias,
      icon: '📁',
      color: 'secondary' as const,
      description: 'Categorias organizadas por nicho'
    },
    {
      title: 'Prompts Base',
      value: stats.total_prompts_base,
      icon: '📝',
      color: 'info' as const,
      description: 'Arquivos TXT carregados'
    },
    {
      title: 'Dados Coletados',
      value: stats.total_dados_coletados,
      icon: '🔍',
      color: 'warning' as const,
      description: 'Conjuntos de dados disponíveis'
    },
    {
      title: 'Prompts Preenchidos',
      value: stats.total_prompts_preenchidos,
      icon: '✅',
      color: 'success' as const,
      description: 'Prompts processados com sucesso'
    }
  ];

  const performanceItems = [
    {
      title: 'Tempo Médio de Processamento',
      value: stats.tempo_medio_processamento || 0,
      unit: 'ms',
      format: formatTime,
      threshold: 1000,
      description: 'Tempo médio para preencher um prompt'
    },
    {
      title: 'Taxa de Sucesso',
      value: stats.taxa_sucesso || 0,
      unit: '%',
      format: (value: number) => `${value.toFixed(1)}%`,
      threshold: 95,
      description: 'Percentual de preenchimentos bem-sucedidos'
    }
  ];

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <LinearProgress />
            <Typography variant="body2" color="text.secondary">
              Carregando estatísticas...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          📊 Estatísticas do Sistema
        </Typography>

        {/* Métricas Principais */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {statsItems.map((item, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Tooltip title={item.description}>
                <Box sx={{ textAlign: 'center', p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                  <Typography variant="h4" color={`${item.color}.main`} gutterBottom>
                    {item.icon}
                  </Typography>
                  <Typography variant="h5" component="div" gutterBottom>
                    {formatNumber(item.value)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {item.title}
                  </Typography>
                </Box>
              </Tooltip>
            </Grid>
          ))}
        </Grid>

        {/* Performance */}
        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          ⚡ Performance
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {performanceItems.map((item, index) => (
            <Box key={index}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  {item.title}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {getStatusIcon(item.value, item.threshold)}
                  <Typography variant="body2" fontWeight="bold">
                    {item.format(item.value)}
                  </Typography>
                </Box>
              </Box>
              
              <LinearProgress
                variant="determinate"
                value={Math.min((item.value / item.threshold) * 100, 100)}
                color={getStatusColor(item.value, item.threshold)}
                sx={{ height: 8, borderRadius: 4 }}
              />
              
              <Typography variant="caption" color="text.secondary">
                {item.description}
              </Typography>
            </Box>
          ))}
        </Box>

        {/* Nichos com Melhor Performance */}
        {stats.estatisticas_por_nicho && stats.estatisticas_por_nicho.length > 0 && (
          <>
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              🏆 Nichos com Melhor Performance
            </Typography>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {stats.estatisticas_por_nicho
                .sort((a, b) => (b.prompts_preenchidos || 0) - (a.prompts_preenchidos || 0))
                .slice(0, 3)
                .map((nicho, index) => (
                  <Box key={nicho.nicho_id} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" fontWeight="bold">
                        #{index + 1}
                      </Typography>
                      <Typography variant="body2">
                        {nicho.nome_nicho}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip
                        label={`${nicho.prompts_preenchidos} prompts`}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                      {nicho.tempo_medio_processamento && (
                        <Chip
                          label={formatTime(nicho.tempo_medio_processamento)}
                          size="small"
                          color="secondary"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </Box>
                ))}
            </Box>
          </>
        )}
      </CardContent>
    </Card>
  );
}; 
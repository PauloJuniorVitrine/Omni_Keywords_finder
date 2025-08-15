/**
 * Dashboard Principal do Sistema de Preenchimento de Lacunas
 * 
 * Componente principal que gerencia a interface do sistema de preenchimento
 * de lacunas em prompts, incluindo gestão de nichos, categorias e prompts.
 * 
 * Tracing ID: FIXTYPE-001_COMPONENT_UPDATE_20241227_001
 * Data: 2024-12-27
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  LinearProgress,
  Alert,
  Snackbar,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Upload as UploadIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { NichoCard } from './NichoCard';
import { CategoriaCard } from './CategoriaCard';
import { PromptCard } from './PromptCard';
import { AddNichoDialog } from './dialogs/AddNichoDialog';
import { AddCategoriaDialog } from './dialogs/AddCategoriaDialog';
import { UploadPromptDialog } from './dialogs/UploadPromptDialog';
import { StatsCard } from './StatsCard';
import { usePromptSystem } from '../../hooks/usePromptSystem';
import { Nicho, Categoria, PromptBase, DadosColetados } from '../../types/api-sync';

interface DashboardStats {
  totalNichos: number;
  totalCategorias: number;
  totalPromptsBase: number;
  totalDadosColetados: number;
  totalPromptsPreenchidos: number;
  tempoMedioProcessamento: number;
  taxaSucesso: number;
}

export const PromptSystemDashboard: React.FC = () => {
  const [selectedNicho, setSelectedNicho] = useState<Nicho | null>(null);
  const [selectedCategoria, setSelectedCategoria] = useState<Categoria | null>(null);
  const [openAddNicho, setOpenAddNicho] = useState(false);
  const [openAddCategoria, setOpenAddCategoria] = useState(false);
  const [openUploadPrompt, setOpenUploadPrompt] = useState(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({ open: false, message: '', severity: 'info' });

  const queryClient = useQueryClient();
  const { 
    getNichos, 
    getCategorias, 
    getPromptsBase, 
    getDadosColetados,
    getStats,
    processarPreenchimento,
    processarLote
  } = usePromptSystem();

  // Queries
  const { data: nichos, isLoading: loadingNichos } = useQuery({
    queryKey: ['nichos'],
    queryFn: getNichos
  });

  const { data: categorias, isLoading: loadingCategorias } = useQuery({
    queryKey: ['categorias', selectedNicho?.id],
    queryFn: () => selectedNicho ? getCategorias(selectedNicho.id) : Promise.resolve([]),
    enabled: !!selectedNicho
  });

  const { data: promptsBase, isLoading: loadingPrompts } = useQuery({
    queryKey: ['prompts-base', selectedCategoria?.id],
    queryFn: () => selectedCategoria ? getPromptsBase(selectedCategoria.id) : Promise.resolve(null),
    enabled: !!selectedCategoria
  });

  const { data: dadosColetados, isLoading: loadingDados } = useQuery({
    queryKey: ['dados-coletados', selectedCategoria?.id],
    queryFn: () => selectedCategoria ? getDadosColetados(selectedCategoria.id) : Promise.resolve([]),
    enabled: !!selectedCategoria
  });

  const { data: stats, isLoading: loadingStats } = useQuery({
    queryKey: ['stats'],
    queryFn: getStats
  });

  // Mutations
  const processarMutation = useMutation({
    mutationFn: ({ categoriaId, dadosId }: { categoriaId: string; dadosId: string }) =>
      processarPreenchimento(categoriaId, dadosId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts-preenchidos'] });
      showSnackbar('Preenchimento processado com sucesso!', 'success');
    },
    onError: (error) => {
      showSnackbar(`Erro ao processar preenchimento: ${error.message}`, 'error');
    }
  });

  const processarLoteMutation = useMutation({
    mutationFn: (nichoId: string) => processarLote(nichoId),
    onSuccess: (resultado) => {
      queryClient.invalidateQueries({ queryKey: ['prompts-preenchidos'] });
      showSnackbar(`Processamento em lote concluído: ${resultado.total_processados} prompts processados`, 'success');
    },
    onError: (error) => {
      showSnackbar(`Erro no processamento em lote: ${error.message}`, 'error');
    }
  });

  // Handlers
  const handleNichoSelect = (nicho: Nicho) => {
    setSelectedNicho(nicho);
    setSelectedCategoria(null);
  };

  const handleCategoriaSelect = (categoria: Categoria) => {
    setSelectedCategoria(categoria);
  };

  const handleProcessarPreenchimento = () => {
    if (selectedCategoria && dadosColetados?.length) {
      const dados = dadosColetados[0]; // Processa o primeiro conjunto de dados
      processarMutation.mutate({
        categoriaId: selectedCategoria.id,
        dadosId: dados.id
      });
    }
  };

  const handleProcessarLote = () => {
    if (selectedNicho) {
      processarLoteMutation.mutate(selectedNicho.id);
    }
  };

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info' | 'warning') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const handleRefresh = () => {
    queryClient.invalidateQueries();
  };

  // Loading states
  const isLoading = loadingNichos || loadingCategorias || loadingPrompts || loadingDados || loadingStats;

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Sistema de Preenchimento de Lacunas
          </Typography>
          <Box>
            <Tooltip title="Atualizar dados">
              <IconButton onClick={handleRefresh} disabled={isLoading}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Configurações">
              <IconButton>
                <SettingsIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Analytics">
              <IconButton>
                <AnalyticsIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        <Typography variant="subtitle1" color="text.secondary">
          Gerencie nichos, categorias e prompts para preenchimento automático de lacunas
        </Typography>
      </Box>

      {/* Loading */}
      {isLoading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Stats Cards */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatsCard
              title="Total de Nichos"
              value={stats.totalNichos}
              color="primary"
              icon="nicho"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatsCard
              title="Total de Categorias"
              value={stats.totalCategorias}
              color="secondary"
              icon="categoria"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatsCard
              title="Prompts Base"
              value={stats.totalPromptsBase}
              color="success"
              icon="prompt"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatsCard
              title="Preenchidos"
              value={stats.totalPromptsPreenchidos}
              color="info"
              icon="preenchido"
            />
          </Grid>
        </Grid>
      )}

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Nichos Section */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" component="h2">
                  Nichos
                </Typography>
                <Button
                  variant="contained"
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={() => setOpenAddNicho(true)}
                >
                  Adicionar
                </Button>
              </Box>
              
              {nichos?.map((nicho) => (
                <NichoCard
                  key={nicho.id}
                  nicho={nicho}
                  selected={selectedNicho?.id === nicho.id}
                  onSelect={handleNichoSelect}
                />
              ))}
              
              {(!nichos || nichos.length === 0) && (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                  Nenhum nicho cadastrado
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Categorias Section */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" component="h2">
                  Categorias
                </Typography>
                <Button
                  variant="contained"
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={() => setOpenAddCategoria(true)}
                  disabled={!selectedNicho}
                >
                  Adicionar
                </Button>
              </Box>
              
              {selectedNicho ? (
                categorias?.map((categoria) => (
                  <CategoriaCard
                    key={categoria.id}
                    categoria={categoria}
                    selected={selectedCategoria?.id === categoria.id}
                    onSelect={handleCategoriaSelect}
                  />
                ))
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                  Selecione um nicho para ver as categorias
                </Typography>
              )}
              
              {selectedNicho && (!categorias || categorias.length === 0) && (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                  Nenhuma categoria cadastrada neste nicho
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Prompts Section */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" component="h2">
                  Prompts
                </Typography>
                <Button
                  variant="contained"
                  size="small"
                  startIcon={<UploadIcon />}
                  onClick={() => setOpenUploadPrompt(true)}
                  disabled={!selectedCategoria}
                >
                  Upload
                </Button>
              </Box>
              
              {selectedCategoria ? (
                <>
                  {promptsBase && (
                    <PromptCard
                      prompt={promptsBase}
                      dadosColetados={dadosColetados}
                      onProcessar={handleProcessarPreenchimento}
                      onProcessarLote={handleProcessarLote}
                      processing={processarMutation.isPending || processarLoteMutation.isPending}
                    />
                  )}
                  
                  {!promptsBase && (
                    <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                      Nenhum prompt base carregado para esta categoria
                    </Typography>
                  )}
                </>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                  Selecione uma categoria para ver os prompts
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Dialogs */}
      <AddNichoDialog
        open={openAddNicho}
        onClose={() => setOpenAddNicho(false)}
        onSuccess={() => {
          setOpenAddNicho(false);
          queryClient.invalidateQueries({ queryKey: ['nichos'] });
          showSnackbar('Nicho criado com sucesso!', 'success');
        }}
      />

      <AddCategoriaDialog
        open={openAddCategoria}
        nichoId={selectedNicho?.id}
        onClose={() => setOpenAddCategoria(false)}
        onSuccess={() => {
          setOpenAddCategoria(false);
          queryClient.invalidateQueries({ queryKey: ['categorias'] });
          showSnackbar('Categoria criada com sucesso!', 'success');
        }}
      />

      <UploadPromptDialog
        open={openUploadPrompt}
        categoriaId={selectedCategoria?.id}
        onClose={() => setOpenUploadPrompt(false)}
        onSuccess={() => {
          setOpenUploadPrompt(false);
          queryClient.invalidateQueries({ queryKey: ['prompts-base'] });
          showSnackbar('Prompt base carregado com sucesso!', 'success');
        }}
      />

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}; 
/**
 * NicheAnalysis - Componente de análise de nichos com visualizações e relatórios
 * 
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 2.1.3
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { useState, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart,
  ScatterChart,
  Scatter,
  Download,
  Share,
  FilterList,
  TrendingUp,
  TrendingDown,
  Visibility,
  Compare
} from '@mui/icons-material';

interface NicheData {
  id: string;
  name: string;
  category: string;
  totalKeywords: number;
  avgDifficulty: number;
  avgVolume: number;
  avgCpc: number;
  competition: 'low' | 'medium' | 'high';
  growth: number;
  revenue: number;
  marketSize: number;
  trends: Array<{
    date: string;
    volume: number;
    difficulty: number;
  }>;
  topKeywords: Array<{
    keyword: string;
    volume: number;
    difficulty: number;
    cpc: number;
  }>;
}

interface NicheAnalysisProps {
  niches: NicheData[];
  selectedNiche?: string;
  onNicheSelect?: (nicheId: string) => void;
  onExport?: (nicheId: string, format: string) => void;
  onCompare?: (nicheIds: string[]) => void;
  isLoading?: boolean;
}

const NicheAnalysis: React.FC<NicheAnalysisProps> = ({
  niches,
  selectedNiche,
  onNicheSelect,
  onExport,
  onCompare,
  isLoading = false
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedNiches, setSelectedNiches] = useState<string[]>([]);
  const [showCompareDialog, setShowCompareDialog] = useState(false);

  const selectedNicheData = useMemo(() => {
    return niches.find(niche => niche.id === selectedNiche);
  }, [niches, selectedNiche]);

  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#ff0000'];

  const handleNicheSelect = (nicheId: string) => {
    onNicheSelect?.(nicheId);
  };

  const handleCompare = () => {
    if (selectedNiches.length >= 2) {
      onCompare?.(selectedNiches);
      setShowCompareDialog(false);
    }
  };

  const getCompetitionColor = (competition: string) => {
    switch (competition) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      default: return 'default';
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatNumber = (value: number) => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }
    return value.toString();
  };

  const renderOverview = () => (
    <Grid container spacing={3}>
      {/* Key Metrics */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Métricas Principais
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {selectedNicheData?.totalKeywords.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Keywords
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="secondary">
                    {selectedNicheData?.avgVolume.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Volume Médio
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="warning.main">
                    {selectedNicheData?.avgDifficulty}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Dificuldade
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main">
                    {formatCurrency(selectedNicheData?.avgCpc || 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    CPC Médio
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Competition & Growth */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Competição & Crescimento
            </Typography>
            <Box mb={2}>
              <Typography variant="body2" color="text.secondary">
                Nível de Competição
              </Typography>
              <Chip
                label={selectedNicheData?.competition === 'low' ? 'Baixa' :
                       selectedNicheData?.competition === 'medium' ? 'Média' : 'Alta'}
                color={getCompetitionColor(selectedNicheData?.competition || 'low')}
                sx={{ mt: 1 }}
              />
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Crescimento (30d)
              </Typography>
              <Box display="flex" alignItems="center" gap={1}>
                {selectedNicheData?.growth && selectedNicheData.growth > 0 ? (
                  <TrendingUp color="success" />
                ) : (
                  <TrendingDown color="error" />
                )}
                <Typography variant="h6" color={selectedNicheData?.growth && selectedNicheData.growth > 0 ? 'success.main' : 'error.main'}>
                  {selectedNicheData?.growth}%
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Trends Chart */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Tendências de Volume e Dificuldade
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={selectedNicheData?.trends || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <RechartsTooltip />
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey="volume"
                  stackId="1"
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.6}
                />
                <Area
                  yAxisId="right"
                  type="monotone"
                  dataKey="difficulty"
                  stackId="2"
                  stroke="#82ca9d"
                  fill="#82ca9d"
                  fillOpacity={0.6}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderKeywords = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Top Keywords do Nicho
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Keyword</TableCell>
                <TableCell align="right">Volume</TableCell>
                <TableCell align="right">Dificuldade</TableCell>
                <TableCell align="right">CPC</TableCell>
                <TableCell align="right">Score</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {selectedNicheData?.topKeywords.map((keyword, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {keyword.keyword}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    {formatNumber(keyword.volume)}
                  </TableCell>
                  <TableCell align="right">
                    <Box display="flex" alignItems="center" gap={1} justifyContent="flex-end">
                      <Typography variant="body2">
                        {keyword.difficulty}%
                      </Typography>
                      <Box
                        sx={{
                          width: 40,
                          height: 4,
                          bgcolor: 'grey.200',
                          borderRadius: 2,
                          overflow: 'hidden'
                        }}
                      >
                        <Box
                          sx={{
                            width: `${keyword.difficulty}%`,
                            height: '100%',
                            bgcolor: keyword.difficulty <= 30 ? 'success.main' : 
                                    keyword.difficulty <= 70 ? 'warning.main' : 'error.main'
                          }}
                        />
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    {formatCurrency(keyword.cpc)}
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={`${Math.round((keyword.volume * keyword.cpc) / keyword.difficulty)}`}
                      size="small"
                      color="primary"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );

  const renderComparison = () => (
    <Grid container spacing={3}>
      {/* Market Size Comparison */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Tamanho do Mercado
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={niches.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <RechartsTooltip />
                <Bar dataKey="marketSize" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* Revenue Distribution */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Distribuição de Receita
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={niches.slice(0, 5)}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="revenue"
                >
                  {niches.slice(0, 5).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* Difficulty vs Volume Scatter */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Dificuldade vs Volume de Busca
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart>
                <CartesianGrid />
                <XAxis type="number" dataKey="avgDifficulty" name="Dificuldade" />
                <YAxis type="number" dataKey="avgVolume" name="Volume" />
                <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} />
                <Scatter name="Nichos" data={niches} fill="#8884d8" />
              </ScatterChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Análise de Nichos
        </Typography>
        
        <Box display="flex" gap={2}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Período</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              label="Período"
            >
              <MenuItem value="7d">7 dias</MenuItem>
              <MenuItem value="30d">30 dias</MenuItem>
              <MenuItem value="90d">90 dias</MenuItem>
              <MenuItem value="1y">1 ano</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="outlined"
            startIcon={<Compare />}
            onClick={() => setShowCompareDialog(true)}
          >
            Comparar
          </Button>

          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={() => onExport?.(selectedNiche || '', 'pdf')}
          >
            Exportar
          </Button>
        </Box>
      </Box>

      {/* Niche Selector */}
      <Box mb={3}>
        <Typography variant="h6" gutterBottom>
          Selecionar Nicho
        </Typography>
        <Box display="flex" gap={1} flexWrap="wrap">
          {niches.map((niche) => (
            <Chip
              key={niche.id}
              label={niche.name}
              onClick={() => handleNicheSelect(niche.id)}
              color={selectedNiche === niche.id ? 'primary' : 'default'}
              variant={selectedNiche === niche.id ? 'filled' : 'outlined'}
              clickable
            />
          ))}
        </Box>
      </Box>

      {/* Loading */}
      {isLoading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Content Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Visão Geral" />
          <Tab label="Keywords" />
          <Tab label="Comparação" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && renderOverview()}
      {activeTab === 1 && renderKeywords()}
      {activeTab === 2 && renderComparison()}

      {/* Compare Dialog */}
      <Dialog 
        open={showCompareDialog} 
        onClose={() => setShowCompareDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Comparar Nichos</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Selecione 2 ou mais nichos para comparar:
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            {niches.map((niche) => (
              <Chip
                key={niche.id}
                label={niche.name}
                onClick={() => {
                  if (selectedNiches.includes(niche.id)) {
                    setSelectedNiches(prev => prev.filter(id => id !== niche.id));
                  } else {
                    setSelectedNiches(prev => [...prev, niche.id]);
                  }
                }}
                color={selectedNiches.includes(niche.id) ? 'primary' : 'default'}
                variant={selectedNiches.includes(niche.id) ? 'filled' : 'outlined'}
                clickable
              />
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCompareDialog(false)}>
            Cancelar
          </Button>
          <Button 
            variant="contained" 
            onClick={handleCompare}
            disabled={selectedNiches.length < 2}
          >
            Comparar ({selectedNiches.length})
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default NicheAnalysis; 
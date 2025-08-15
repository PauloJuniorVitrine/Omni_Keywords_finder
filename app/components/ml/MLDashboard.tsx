/**
 * MLDashboard.tsx
 * 
 * Dashboard completo de Machine Learning para o Omni Keywords Finder
 * 
 * Tracing ID: UI-020
 * Data/Hora: 2024-12-20 12:30:00 UTC
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Treinamento de modelos
 * - Monitoramento de performance
 * - A/B testing de modelos
 * - Análise de drift
 * - Configuração de features
 * - Deploy de modelos
 * - Monitoramento de predições
 * - Análise de bias
 * - Versionamento de modelos
 * - Integração com MLOps
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  Badge,
  Switch,
  FormControlLabel,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  AlertTitle,
  Stack,
  Avatar,
  Rating,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  Settings,
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Error,
  Info,
  Download,
  Upload,
  Code,
  DataUsage,
  Psychology,
  Timeline,
  Assessment,
  CompareArrows,
  BugReport,
  Security,
  History,
  AutoAwesome,
  Speed,
  Analytics,
  ModelTraining,
  Dataset,
  Tune,
  Deploy,
  Monitor,
  Bias,
  VersionControl,
  IntegrationInstructions,
  ExpandMore,
  Add,
  Edit,
  Delete,
  Visibility,
  CloudUpload,
  CloudDownload,
  Schedule,
  Notifications,
  Share,
  Favorite,
  Star,
  StarBorder,
  StarHalf,
  Archive
} from '@mui/icons-material';

// Types
interface Model {
  id: string;
  name: string;
  version: string;
  type: 'classification' | 'regression' | 'clustering' | 'nlp';
  status: 'training' | 'ready' | 'deployed' | 'archived' | 'failed';
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  trainingDate: string;
  lastUpdated: string;
  features: string[];
  hyperparameters: Record<string, any>;
  performance: {
    trainingTime: number;
    inferenceTime: number;
    memoryUsage: number;
    cpuUsage: number;
  };
  drift: {
    dataDrift: number;
    conceptDrift: number;
    lastCheck: string;
  };
  bias: {
    genderBias: number;
    ageBias: number;
    ethnicityBias: number;
    overallBias: number;
  };
  predictions: {
    total: number;
    correct: number;
    incorrect: number;
    confidence: number;
  };
  metadata: {
    description: string;
    tags: string[];
    author: string;
    framework: string;
    dataset: string;
  };
}

interface Experiment {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'failed' | 'paused';
  startDate: string;
  endDate?: string;
  variants: {
    name: string;
    modelId: string;
    traffic: number;
    performance: {
      accuracy: number;
      precision: number;
      recall: number;
      f1Score: number;
    };
  }[];
  metrics: {
    conversionRate: number;
    revenue: number;
    userSatisfaction: number;
  };
  significance: {
    pValue: number;
    confidence: number;
    winner: string;
  };
}

interface Feature {
  id: string;
  name: string;
  type: 'numerical' | 'categorical' | 'text' | 'datetime';
  importance: number;
  status: 'active' | 'inactive' | 'deprecated';
  description: string;
  source: string;
  transformations: string[];
  validation: {
    minValue?: number;
    maxValue?: number;
    allowedValues?: string[];
    required: boolean;
  };
}

interface Prediction {
  id: string;
  modelId: string;
  input: Record<string, any>;
  output: any;
  confidence: number;
  timestamp: string;
  processingTime: number;
  status: 'success' | 'error' | 'timeout';
  error?: string;
}

// Mock data
const mockModels: Model[] = [
  {
    id: 'model-001',
    name: 'Keyword Classifier v2.1',
    version: '2.1.0',
    type: 'classification',
    status: 'deployed',
    accuracy: 0.94,
    precision: 0.92,
    recall: 0.89,
    f1Score: 0.90,
    trainingDate: '2024-12-15T10:30:00Z',
    lastUpdated: '2024-12-19T14:20:00Z',
    features: ['keyword_length', 'search_volume', 'competition', 'intent_type', 'seasonality'],
    hyperparameters: {
      learning_rate: 0.01,
      max_depth: 10,
      n_estimators: 100,
      random_state: 42
    },
    performance: {
      trainingTime: 1800,
      inferenceTime: 0.05,
      memoryUsage: 512,
      cpuUsage: 15
    },
    drift: {
      dataDrift: 0.12,
      conceptDrift: 0.08,
      lastCheck: '2024-12-20T06:00:00Z'
    },
    bias: {
      genderBias: 0.03,
      ageBias: 0.05,
      ethnicityBias: 0.02,
      overallBias: 0.04
    },
    predictions: {
      total: 15420,
      correct: 14495,
      incorrect: 925,
      confidence: 0.87
    },
    metadata: {
      description: 'Modelo de classificação de keywords baseado em XGBoost',
      tags: ['classification', 'keywords', 'xgboost'],
      author: 'ML Team',
      framework: 'XGBoost',
      dataset: 'keywords_dataset_v3'
    }
  },
  {
    id: 'model-002',
    name: 'Search Volume Predictor',
    version: '1.5.2',
    type: 'regression',
    status: 'ready',
    accuracy: 0.87,
    precision: 0.85,
    recall: 0.88,
    f1Score: 0.86,
    trainingDate: '2024-12-18T09:15:00Z',
    lastUpdated: '2024-12-19T16:45:00Z',
    features: ['keyword', 'category', 'trend_data', 'competition_level', 'seasonal_factors'],
    hyperparameters: {
      learning_rate: 0.005,
      max_depth: 8,
      n_estimators: 150,
      subsample: 0.8
    },
    performance: {
      trainingTime: 2400,
      inferenceTime: 0.08,
      memoryUsage: 768,
      cpuUsage: 22
    },
    drift: {
      dataDrift: 0.18,
      conceptDrift: 0.15,
      lastCheck: '2024-12-20T06:00:00Z'
    },
    bias: {
      genderBias: 0.06,
      ageBias: 0.04,
      ethnicityBias: 0.03,
      overallBias: 0.05
    },
    predictions: {
      total: 8920,
      correct: 7760,
      incorrect: 1160,
      confidence: 0.82
    },
    metadata: {
      description: 'Modelo de predição de volume de busca usando Random Forest',
      tags: ['regression', 'volume', 'random_forest'],
      author: 'Data Science Team',
      framework: 'Random Forest',
      dataset: 'search_volume_dataset_v2'
    }
  }
];

const mockExperiments: Experiment[] = [
  {
    id: 'exp-001',
    name: 'Keyword Classifier A/B Test',
    status: 'completed',
    startDate: '2024-12-10T00:00:00Z',
    endDate: '2024-12-17T23:59:59Z',
    variants: [
      {
        name: 'Control (v2.0)',
        modelId: 'model-001',
        traffic: 50,
        performance: {
          accuracy: 0.91,
          precision: 0.89,
          recall: 0.87,
          f1Score: 0.88
        }
      },
      {
        name: 'Treatment (v2.1)',
        modelId: 'model-002',
        traffic: 50,
        performance: {
          accuracy: 0.94,
          precision: 0.92,
          recall: 0.89,
          f1Score: 0.90
        }
      }
    ],
    metrics: {
      conversionRate: 0.15,
      revenue: 12500,
      userSatisfaction: 4.2
    },
    significance: {
      pValue: 0.023,
      confidence: 0.95,
      winner: 'Treatment (v2.1)'
    }
  }
];

const mockFeatures: Feature[] = [
  {
    id: 'feature-001',
    name: 'keyword_length',
    type: 'numerical',
    importance: 0.85,
    status: 'active',
    description: 'Comprimento da keyword em caracteres',
    source: 'raw_data',
    transformations: ['normalize', 'log_transform'],
    validation: {
      minValue: 1,
      maxValue: 100,
      required: true
    }
  },
  {
    id: 'feature-002',
    name: 'search_volume',
    type: 'numerical',
    importance: 0.92,
    status: 'active',
    description: 'Volume de busca mensal',
    source: 'google_ads_api',
    transformations: ['scale', 'outlier_removal'],
    validation: {
      minValue: 0,
      required: true
    }
  }
];

const mockPredictions: Prediction[] = [
  {
    id: 'pred-001',
    modelId: 'model-001',
    input: { keyword: 'digital marketing', category: 'business' },
    output: { class: 'high_value', confidence: 0.87 },
    confidence: 0.87,
    timestamp: '2024-12-20T12:25:30Z',
    processingTime: 0.05,
    status: 'success'
  }
];

// Custom hooks
const useModels = () => {
  const [models, setModels] = useState<Model[]>(mockModels);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const trainModel = useCallback(async (config: any) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      const newModel: Model = {
        id: `model-${Date.now()}`,
        name: config.name,
        version: '1.0.0',
        type: config.type,
        status: 'training',
        accuracy: 0,
        precision: 0,
        recall: 0,
        f1Score: 0,
        trainingDate: new Date().toISOString(),
        lastUpdated: new Date().toISOString(),
        features: config.features,
        hyperparameters: config.hyperparameters,
        performance: { trainingTime: 0, inferenceTime: 0, memoryUsage: 0, cpuUsage: 0 },
        drift: { dataDrift: 0, conceptDrift: 0, lastCheck: new Date().toISOString() },
        bias: { genderBias: 0, ageBias: 0, ethnicityBias: 0, overallBias: 0 },
        predictions: { total: 0, correct: 0, incorrect: 0, confidence: 0 },
        metadata: { description: config.description, tags: config.tags, author: 'Current User', framework: config.framework, dataset: config.dataset }
      };
      setModels(prev => [...prev, newModel]);
    } catch (err) {
      setError('Erro ao treinar modelo');
    } finally {
      setLoading(false);
    }
  }, []);

  const deployModel = useCallback(async (modelId: string) => {
    setModels(prev => prev.map(model => 
      model.id === modelId ? { ...model, status: 'deployed' } : model
    ));
  }, []);

  const archiveModel = useCallback(async (modelId: string) => {
    setModels(prev => prev.map(model => 
      model.id === modelId ? { ...model, status: 'archived' } : model
    ));
  }, []);

  return { models, loading, error, trainModel, deployModel, archiveModel };
};

const useExperiments = () => {
  const [experiments, setExperiments] = useState<Experiment[]>(mockExperiments);
  const [loading, setLoading] = useState(false);

  const createExperiment = useCallback(async (config: any) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      const newExperiment: Experiment = {
        id: `exp-${Date.now()}`,
        name: config.name,
        status: 'running',
        startDate: new Date().toISOString(),
        variants: config.variants,
        metrics: { conversionRate: 0, revenue: 0, userSatisfaction: 0 },
        significance: { pValue: 0, confidence: 0, winner: '' }
      };
      setExperiments(prev => [...prev, newExperiment]);
    } finally {
      setLoading(false);
    }
  }, []);

  return { experiments, loading, createExperiment };
};

const useFeatures = () => {
  const [features, setFeatures] = useState<Feature[]>(mockFeatures);
  const [loading, setLoading] = useState(false);

  const addFeature = useCallback(async (feature: Omit<Feature, 'id'>) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      const newFeature: Feature = { ...feature, id: `feature-${Date.now()}` };
      setFeatures(prev => [...prev, newFeature]);
    } finally {
      setLoading(false);
    }
  }, []);

  return { features, loading, addFeature };
};

const usePredictions = () => {
  const [predictions, setPredictions] = useState<Prediction[]>(mockPredictions);
  const [loading, setLoading] = useState(false);

  const makePrediction = useCallback(async (modelId: string, input: Record<string, any>) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 300));
      const prediction: Prediction = {
        id: `pred-${Date.now()}`,
        modelId,
        input,
        output: { class: 'medium_value', confidence: 0.75 },
        confidence: 0.75,
        timestamp: new Date().toISOString(),
        processingTime: 0.05,
        status: 'success'
      };
      setPredictions(prev => [prediction, ...prev]);
      return prediction;
    } finally {
      setLoading(false);
    }
  }, []);

  return { predictions, loading, makePrediction };
};

// Main component
const MLDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [trainDialogOpen, setTrainDialogOpen] = useState(false);
  const [experimentDialogOpen, setExperimentDialogOpen] = useState(false);
  const [featureDialogOpen, setFeatureDialogOpen] = useState(false);
  const [predictionDialogOpen, setPredictionDialogOpen] = useState(false);
  const [modelDetailsOpen, setModelDetailsOpen] = useState(false);

  const { models, loading: modelsLoading, error: modelsError, trainModel, deployModel, archiveModel } = useModels();
  const { experiments, loading: experimentsLoading, createExperiment } = useExperiments();
  const { features, loading: featuresLoading, addFeature } = useFeatures();
  const { predictions, loading: predictionsLoading, makePrediction } = usePredictions();

  // Computed values
  const deployedModels = useMemo(() => models.filter(m => m.status === 'deployed'), [models]);
  const trainingModels = useMemo(() => models.filter(m => m.status === 'training'), [models]);
  const readyModels = useMemo(() => models.filter(m => m.status === 'ready'), [models]);
  const activeExperiments = useMemo(() => experiments.filter(e => e.status === 'running'), [experiments]);
  const activeFeatures = useMemo(() => features.filter(f => f.status === 'active'), [features]);

  const totalPredictions = useMemo(() => predictions.length, [predictions]);
  const successfulPredictions = useMemo(() => predictions.filter(p => p.status === 'success').length, [predictions]);
  const averageConfidence = useMemo(() => {
    const successful = predictions.filter(p => p.status === 'success');
    return successful.length > 0 ? successful.reduce((sum, p) => sum + p.confidence, 0) / successful.length : 0;
  }, [predictions]);

  const averageProcessingTime = useMemo(() => {
    const successful = predictions.filter(p => p.status === 'success');
    return successful.length > 0 ? successful.reduce((sum, p) => sum + p.processingTime, 0) / successful.length : 0;
  }, [predictions]);

  // Tab content components
  const ModelsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Modelos de Machine Learning</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setTrainDialogOpen(true)}
          disabled={modelsLoading}
        >
          Treinar Novo Modelo
        </Button>
      </Box>

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total de Modelos</Typography>
              <Typography variant="h4">{models.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Modelos Deployados</Typography>
              <Typography variant="h4" color="primary">{deployedModels.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Em Treinamento</Typography>
              <Typography variant="h4" color="warning.main">{trainingModels.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Prontos para Deploy</Typography>
              <Typography variant="h4" color="success.main">{readyModels.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Nome</TableCell>
              <TableCell>Versão</TableCell>
              <TableCell>Tipo</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Acurácia</TableCell>
              <TableCell>F1-Score</TableCell>
              <TableCell>Drift</TableCell>
              <TableCell>Bias</TableCell>
              <TableCell>Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {models.map((model) => (
              <TableRow key={model.id}>
                <TableCell>
                  <Box>
                    <Typography variant="subtitle2">{model.name}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {model.metadata.description}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>{model.version}</TableCell>
                <TableCell>
                  <Chip 
                    label={model.type} 
                    size="small" 
                    color={model.type === 'classification' ? 'primary' : 'secondary'}
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={model.status}
                    size="small"
                    color={
                      model.status === 'deployed' ? 'success' :
                      model.status === 'training' ? 'warning' :
                      model.status === 'ready' ? 'info' :
                      model.status === 'failed' ? 'error' : 'default'
                    }
                  />
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <Typography variant="body2">{(model.accuracy * 100).toFixed(1)}%</Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={model.accuracy * 100} 
                      sx={{ ml: 1, width: 50, height: 6 }}
                    />
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">{(model.f1Score * 100).toFixed(1)}%</Typography>
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <Typography variant="body2" color={model.drift.dataDrift > 0.15 ? 'error' : 'textPrimary'}>
                      {(model.drift.dataDrift * 100).toFixed(1)}%
                    </Typography>
                    {model.drift.dataDrift > 0.15 && <Warning color="error" sx={{ ml: 0.5, fontSize: 16 }} />}
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color={model.bias.overallBias > 0.1 ? 'error' : 'textPrimary'}>
                    {(model.bias.overallBias * 100).toFixed(1)}%
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={1}>
                    <Tooltip title="Ver Detalhes">
                      <IconButton size="small" onClick={() => { setSelectedModel(model); setModelDetailsOpen(true); }}>
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    {model.status === 'ready' && (
                      <Tooltip title="Deploy">
                        <IconButton size="small" onClick={() => deployModel(model.id)}>
                          <Deploy />
                        </IconButton>
                      </Tooltip>
                    )}
                    {model.status === 'deployed' && (
                      <Tooltip title="Arquivar">
                        <IconButton size="small" onClick={() => archiveModel(model.id)}>
                          <Archive />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const ExperimentsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Experimentos A/B</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setExperimentDialogOpen(true)}
          disabled={experimentsLoading}
        >
          Criar Experimento
        </Button>
      </Box>

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total de Experimentos</Typography>
              <Typography variant="h4">{experiments.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Ativos</Typography>
              <Typography variant="h4" color="primary">{activeExperiments.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Concluídos</Typography>
              <Typography variant="h4" color="success.main">
                {experiments.filter(e => e.status === 'completed').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Taxa de Conversão</Typography>
              <Typography variant="h4" color="info.main">
                {(experiments.reduce((sum, e) => sum + e.metrics.conversionRate, 0) / experiments.length * 100).toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {experiments.map((experiment) => (
        <Card key={experiment.id} sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">{experiment.name}</Typography>
              <Chip
                label={experiment.status}
                color={
                  experiment.status === 'running' ? 'primary' :
                  experiment.status === 'completed' ? 'success' :
                  experiment.status === 'failed' ? 'error' : 'default'
                }
              />
            </Box>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Variantes</Typography>
                {experiment.variants.map((variant, index) => (
                  <Box key={index} display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2">{variant.name}</Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body2">{(variant.performance.f1Score * 100).toFixed(1)}%</Typography>
                      <Typography variant="caption" color="textSecondary">{variant.traffic}%</Typography>
                    </Box>
                  </Box>
                ))}
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Métricas</Typography>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Conversão:</Typography>
                  <Typography variant="body2">{(experiment.metrics.conversionRate * 100).toFixed(2)}%</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Receita:</Typography>
                  <Typography variant="body2">R$ {experiment.metrics.revenue.toLocaleString()}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Satisfação:</Typography>
                  <Rating value={experiment.metrics.userSatisfaction} readOnly size="small" />
                </Box>
              </Grid>
            </Grid>

            {experiment.status === 'completed' && (
              <Box mt={2} p={2} bgcolor="grey.50" borderRadius={1}>
                <Typography variant="subtitle2" gutterBottom>Resultado</Typography>
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="body2">Vencedor:</Typography>
                  <Chip label={experiment.significance.winner} color="success" size="small" />
                  <Typography variant="body2">(p = {experiment.significance.pValue.toFixed(3)})</Typography>
                </Box>
              </Box>
            )}
          </CardContent>
        </Card>
      ))}
    </Box>
  );

  const FeaturesTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Gestão de Features</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setFeatureDialogOpen(true)}
          disabled={featuresLoading}
        >
          Adicionar Feature
        </Button>
      </Box>

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total de Features</Typography>
              <Typography variant="h4">{features.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Ativas</Typography>
              <Typography variant="h4" color="success.main">{activeFeatures.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Inativas</Typography>
              <Typography variant="h4" color="warning.main">
                {features.filter(f => f.status === 'inactive').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Importância Média</Typography>
              <Typography variant="h4" color="info.main">
                {(features.reduce((sum, f) => sum + f.importance, 0) / features.length * 100).toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Nome</TableCell>
              <TableCell>Tipo</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Importância</TableCell>
              <TableCell>Fonte</TableCell>
              <TableCell>Transformações</TableCell>
              <TableCell>Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {features.map((feature) => (
              <TableRow key={feature.id}>
                <TableCell>
                  <Box>
                    <Typography variant="subtitle2">{feature.name}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {feature.description}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={feature.type} 
                    size="small" 
                    color={
                      feature.type === 'numerical' ? 'primary' :
                      feature.type === 'categorical' ? 'secondary' :
                      feature.type === 'text' ? 'success' : 'default'
                    }
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={feature.status}
                    size="small"
                    color={
                      feature.status === 'active' ? 'success' :
                      feature.status === 'inactive' ? 'warning' : 'default'
                    }
                  />
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <Typography variant="body2">{(feature.importance * 100).toFixed(1)}%</Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={feature.importance * 100} 
                      sx={{ ml: 1, width: 50, height: 6 }}
                    />
                  </Box>
                </TableCell>
                <TableCell>{feature.source}</TableCell>
                <TableCell>
                  <Box display="flex" gap={0.5} flexWrap="wrap">
                    {feature.transformations.map((transformation, index) => (
                      <Chip key={index} label={transformation} size="small" variant="outlined" />
                    ))}
                  </Box>
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={1}>
                    <Tooltip title="Editar">
                      <IconButton size="small">
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Visualizar">
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const PredictionsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Monitoramento de Predições</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setPredictionDialogOpen(true)}
          disabled={predictionsLoading}
        >
          Nova Predição
        </Button>
      </Box>

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total de Predições</Typography>
              <Typography variant="h4">{totalPredictions}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Sucesso</Typography>
              <Typography variant="h4" color="success.main">{successfulPredictions}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Confiança Média</Typography>
              <Typography variant="h4" color="info.main">{(averageConfidence * 100).toFixed(1)}%</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Tempo Médio</Typography>
              <Typography variant="h4" color="warning.main">{(averageProcessingTime * 1000).toFixed(1)}ms</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>Modelo</TableCell>
              <TableCell>Input</TableCell>
              <TableCell>Output</TableCell>
              <TableCell>Confiança</TableCell>
              <TableCell>Tempo</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {predictions.slice(0, 10).map((prediction) => (
              <TableRow key={prediction.id}>
                <TableCell>
                  <Typography variant="body2">
                    {new Date(prediction.timestamp).toLocaleString()}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {models.find(m => m.id === prediction.modelId)?.name || prediction.modelId}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" noWrap>
                    {JSON.stringify(prediction.input).substring(0, 50)}...
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {JSON.stringify(prediction.output)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">{(prediction.confidence * 100).toFixed(1)}%</Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">{(prediction.processingTime * 1000).toFixed(1)}ms</Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={prediction.status}
                    size="small"
                    color={prediction.status === 'success' ? 'success' : 'error'}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const AnalyticsTab = () => (
    <Box>
      <Typography variant="h6" gutterBottom>Analytics de ML</Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Performance dos Modelos</Typography>
              <Box display="flex" justifyContent="space-between" mb={2}>
                <Typography variant="body2">Acurácia Média</Typography>
                <Typography variant="body2">
                  {(models.reduce((sum, m) => sum + m.accuracy, 0) / models.length * 100).toFixed(1)}%
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" mb={2}>
                <Typography variant="body2">F1-Score Médio</Typography>
                <Typography variant="body2">
                  {(models.reduce((sum, m) => sum + m.f1Score, 0) / models.length * 100).toFixed(1)}%
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Tempo de Inferência</Typography>
                <Typography variant="body2">
                  {(models.reduce((sum, m) => sum + m.performance.inferenceTime, 0) / models.length * 1000).toFixed(1)}ms
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Drift e Bias</Typography>
              <Box display="flex" justifyContent="space-between" mb={2}>
                <Typography variant="body2">Data Drift Médio</Typography>
                <Typography variant="body2" color="error">
                  {(models.reduce((sum, m) => sum + m.drift.dataDrift, 0) / models.length * 100).toFixed(1)}%
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" mb={2}>
                <Typography variant="body2">Concept Drift Médio</Typography>
                <Typography variant="body2" color="warning.main">
                  {(models.reduce((sum, m) => sum + m.drift.conceptDrift, 0) / models.length * 100).toFixed(1)}%
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Bias Geral</Typography>
                <Typography variant="body2" color="info.main">
                  {(models.reduce((sum, m) => sum + m.bias.overallBias, 0) / models.length * 100).toFixed(1)}%
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            <Psychology sx={{ mr: 1, verticalAlign: 'middle' }} />
            Dashboard de Machine Learning
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Gestão completa de modelos, experimentos e predições
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <Button variant="outlined" startIcon={<Refresh />}>
            Atualizar
          </Button>
          <Button variant="contained" startIcon={<Settings />}>
            Configurações
          </Button>
        </Box>
      </Box>

      {modelsError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <AlertTitle>Erro</AlertTitle>
          {modelsError}
        </Alert>
      )}

      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Modelos" icon={<ModelTraining />} />
          <Tab label="Experimentos" icon={<CompareArrows />} />
          <Tab label="Features" icon={<Dataset />} />
          <Tab label="Predições" icon={<Analytics />} />
          <Tab label="Analytics" icon={<Assessment />} />
        </Tabs>
      </Paper>

      <Box>
        {activeTab === 0 && <ModelsTab />}
        {activeTab === 1 && <ExperimentsTab />}
        {activeTab === 2 && <FeaturesTab />}
        {activeTab === 3 && <PredictionsTab />}
        {activeTab === 4 && <AnalyticsTab />}
      </Box>

      {/* Speed Dial for quick actions */}
      <SpeedDial
        ariaLabel="Ações rápidas"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
      >
        <SpeedDialAction
          icon={<Add />}
          tooltipTitle="Treinar Modelo"
          onClick={() => setTrainDialogOpen(true)}
        />
        <SpeedDialAction
          icon={<CompareArrows />}
          tooltipTitle="Criar Experimento"
          onClick={() => setExperimentDialogOpen(true)}
        />
        <SpeedDialAction
          icon={<Dataset />}
          tooltipTitle="Adicionar Feature"
          onClick={() => setFeatureDialogOpen(true)}
        />
        <SpeedDialAction
          icon={<Analytics />}
          tooltipTitle="Nova Predição"
          onClick={() => setPredictionDialogOpen(true)}
        />
      </SpeedDial>

      {/* Dialogs would be implemented here */}
      {/* Train Model Dialog */}
      {/* Experiment Dialog */}
      {/* Feature Dialog */}
      {/* Prediction Dialog */}
      {/* Model Details Dialog */}
    </Box>
  );
};

export default MLDashboard; 
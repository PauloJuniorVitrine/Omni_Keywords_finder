/**
 * ExecucaoForm.tsx
 * 
 * Formulário de criação e edição de execuções
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_013
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Formulário de nova execução
 * - Seleção de categoria
 * - Upload de palavras-chave
 * - Configuração de parâmetros
 * - Validação em tempo real
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Chip,
  Alert,
  LinearProgress,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  useTheme,
  useMediaQuery,
  Tooltip,
  FormHelperText,
  Switch,
  FormControlLabel,
  Slider,
  InputAdornment,
} from '@mui/material';
import {
  Save as SaveIcon,
  Cancel as CancelIcon,
  Upload as UploadIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Settings as SettingsIcon,
  PlayArrow as PlayIcon,
  Preview as PreviewIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CloudUpload as CloudUploadIcon,
  FileCopy as FileCopyIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';

// Tipos
interface ExecucaoFormData {
  nome: string;
  descricao: string;
  nichoId: string;
  categoriaId: string;
  keywords: string[];
  parametros: ExecucaoParametros;
  agendamento: AgendamentoConfig;
}

interface ExecucaoParametros {
  maxKeywords: number;
  profundidadeBusca: number;
  tempoEspera: number;
  usarProxy: boolean;
  retryOnFail: boolean;
  maxRetries: number;
  salvarLogs: boolean;
  notificarConclusao: boolean;
}

interface AgendamentoConfig {
  executarAgora: boolean;
  dataAgendada: string;
  horaAgendada: string;
  repetir: boolean;
  intervalo: 'diario' | 'semanal' | 'mensal';
}

interface Nicho {
  id: string;
  nome: string;
  descricao: string;
}

interface Categoria {
  id: string;
  nome: string;
  descricao: string;
  nichoId: string;
}

interface KeywordFile {
  id: string;
  nome: string;
  tamanho: number;
  keywords: string[];
  status: 'carregado' | 'processando' | 'erro';
}

/**
 * Componente de formulário de execução
 */
const ExecucaoForm: React.FC = () => {
  // Estados
  const [formData, setFormData] = useState<ExecucaoFormData>({
    nome: '',
    descricao: '',
    nichoId: '',
    categoriaId: '',
    keywords: [],
    parametros: {
      maxKeywords: 1000,
      profundidadeBusca: 3,
      tempoEspera: 2,
      usarProxy: false,
      retryOnFail: true,
      maxRetries: 3,
      salvarLogs: true,
      notificarConclusao: true,
    },
    agendamento: {
      executarAgora: true,
      dataAgendada: '',
      horaAgendada: '',
      repetir: false,
      intervalo: 'diario',
    },
  });

  const [nichos, setNichos] = useState<Nicho[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [categoriasFiltradas, setCategoriasFiltradas] = useState<Categoria[]>([]);
  const [keywordFiles, setKeywordFiles] = useState<KeywordFile[]>([]);
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showPreview, setShowPreview] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Hooks
  const theme = useTheme();
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Efeitos
  useEffect(() => {
    loadNichos();
    if (id) {
      loadExecucao(id);
    }
  }, [id]);

  useEffect(() => {
    if (formData.nichoId) {
      filterCategorias();
    }
  }, [formData.nichoId, categorias]);

  /**
   * Carrega nichos da API
   */
  const loadNichos = async () => {
    try {
      // TODO: Implementar chamada real da API
      // const response = await api.get('/nichos');
      
      const mockNichos: Nicho[] = [
        { id: '1', nome: 'Tecnologia', descricao: 'Nichos de tecnologia' },
        { id: '2', nome: 'Saúde e Bem-estar', descricao: 'Nichos de saúde' },
        { id: '3', nome: 'Finanças', descricao: 'Nichos financeiros' },
        { id: '4', nome: 'Educação', descricao: 'Nichos educacionais' },
      ];

      setNichos(mockNichos);
    } catch (err) {
      console.error('Erro ao carregar nichos:', err);
    }
  };

  /**
   * Carrega execução para edição
   */
  const loadExecucao = async (execucaoId: string) => {
    try {
      setLoading(true);
      // TODO: Implementar chamada real da API
      // const response = await api.get(`/execucoes/${execucaoId}`);
      
      // Mock de dados para edição
      const mockExecucao = {
        nome: 'Execução Tecnologia - Edição',
        descricao: 'Execução para teste de edição',
        nichoId: '1',
        categoriaId: '1',
        keywords: ['react', 'typescript', 'javascript'],
        parametros: {
          maxKeywords: 500,
          profundidadeBusca: 2,
          tempoEspera: 1,
          usarProxy: true,
          retryOnFail: true,
          maxRetries: 2,
          salvarLogs: true,
          notificarConclusao: false,
        },
        agendamento: {
          executarAgora: false,
          dataAgendada: '2025-01-28',
          horaAgendada: '10:00',
          repetir: true,
          intervalo: 'diario',
        },
      };

      setFormData(mockExecucao);
    } catch (err) {
      console.error('Erro ao carregar execução:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Filtra categorias por nicho
   */
  const filterCategorias = () => {
    const categoriasDoNicho = categorias.filter(cat => cat.nichoId === formData.nichoId);
    setCategoriasFiltradas(categoriasDoNicho);
    
    // Reset categoria se não pertencer ao nicho selecionado
    if (!categoriasDoNicho.find(cat => cat.id === formData.categoriaId)) {
      setFormData(prev => ({ ...prev, categoriaId: '' }));
    }
  };

  /**
   * Carrega categorias da API
   */
  const loadCategorias = async () => {
    try {
      // TODO: Implementar chamada real da API
      // const response = await api.get('/categorias');
      
      const mockCategorias: Categoria[] = [
        { id: '1', nome: 'Desenvolvimento Web', descricao: 'Web development', nichoId: '1' },
        { id: '2', nome: 'Mobile', descricao: 'Mobile development', nichoId: '1' },
        { id: '3', nome: 'Fitness', descricao: 'Fitness and health', nichoId: '2' },
        { id: '4', nome: 'Nutrição', descricao: 'Nutrition', nichoId: '2' },
        { id: '5', nome: 'Investimentos', descricao: 'Investments', nichoId: '3' },
        { id: '6', nome: 'Cursos Online', descricao: 'Online courses', nichoId: '4' },
      ];

      setCategorias(mockCategorias);
    } catch (err) {
      console.error('Erro ao carregar categorias:', err);
    }
  };

  /**
   * Manipula mudança de campo
   */
  const handleFieldChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Limpar erro do campo
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  /**
   * Manipula mudança de parâmetros
   */
  const handleParametroChange = (parametro: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      parametros: {
        ...prev.parametros,
        [parametro]: value
      }
    }));
  };

  /**
   * Manipula mudança de agendamento
   */
  const handleAgendamentoChange = (campo: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      agendamento: {
        ...prev.agendamento,
        [campo]: value
      }
    }));
  };

  /**
   * Manipula upload de arquivo
   */
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      try {
        setUploadProgress(0);
        
        // Simular upload
        const keywords = await processFile(file);
        
        const keywordFile: KeywordFile = {
          id: Date.now().toString() + i,
          nome: file.name,
          tamanho: file.size,
          keywords,
          status: 'carregado'
        };

        setKeywordFiles(prev => [...prev, keywordFile]);
        setFormData(prev => ({
          ...prev,
          keywords: [...prev.keywords, ...keywords]
        }));

        setUploadProgress(100);
      } catch (err) {
        console.error('Erro ao processar arquivo:', err);
      }
    }
  };

  /**
   * Processa arquivo de keywords
   */
  const processFile = async (file: File): Promise<string[]> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const content = e.target?.result as string;
          const keywords = content
            .split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0);
          
          resolve(keywords);
        } catch (err) {
          reject(err);
        }
      };

      reader.onerror = reject;
      reader.readAsText(file);
    });
  };

  /**
   * Remove arquivo de keywords
   */
  const removeKeywordFile = (fileId: string) => {
    const file = keywordFiles.find(f => f.id === fileId);
    if (file) {
      setKeywordFiles(prev => prev.filter(f => f.id !== fileId));
      setFormData(prev => ({
        ...prev,
        keywords: prev.keywords.filter(kw => !file.keywords.includes(kw))
      }));
    }
  };

  /**
   * Adiciona keyword manualmente
   */
  const addKeyword = (keyword: string) => {
    if (keyword.trim() && !formData.keywords.includes(keyword.trim())) {
      setFormData(prev => ({
        ...prev,
        keywords: [...prev.keywords, keyword.trim()]
      }));
    }
  };

  /**
   * Remove keyword
   */
  const removeKeyword = (keyword: string) => {
    setFormData(prev => ({
      ...prev,
      keywords: prev.keywords.filter(kw => kw !== keyword)
    }));
  };

  /**
   * Valida formulário
   */
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.nome.trim()) {
      newErrors.nome = 'Nome é obrigatório';
    }

    if (!formData.nichoId) {
      newErrors.nichoId = 'Nicho é obrigatório';
    }

    if (!formData.categoriaId) {
      newErrors.categoriaId = 'Categoria é obrigatória';
    }

    if (formData.keywords.length === 0) {
      newErrors.keywords = 'Pelo menos uma keyword é obrigatória';
    }

    if (formData.parametros.maxKeywords < 1) {
      newErrors.maxKeywords = 'Máximo de keywords deve ser maior que 0';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Salva execução
   */
  const handleSave = async () => {
    if (!validateForm()) return;

    try {
      setSaving(true);
      
      // TODO: Implementar chamada real da API
      // const response = await api.post('/execucoes', formData);
      
      // Simular delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      navigate('/execucoes');
    } catch (err) {
      console.error('Erro ao salvar execução:', err);
    } finally {
      setSaving(false);
    }
  };

  /**
   * Executa imediatamente
   */
  const handleExecuteNow = async () => {
    if (!validateForm()) return;

    try {
      setSaving(true);
      
      // TODO: Implementar chamada real da API
      // const response = await api.post('/execucoes/execute', formData);
      
      // Simular delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      navigate('/execucoes');
    } catch (err) {
      console.error('Erro ao executar:', err);
    } finally {
      setSaving(false);
    }
  };

  /**
   * Próximo passo
   */
  const handleNext = () => {
    setActiveStep(prev => prev + 1);
  };

  /**
   * Passo anterior
   */
  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  if (loading) {
    return (
      <Box>
        <LinearProgress />
        <Typography>Carregando...</Typography>
      </Box>
    );
  }

  const steps = [
    'Informações Básicas',
    'Keywords',
    'Parâmetros',
    'Agendamento',
    'Revisão'
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {id ? 'Editar Execução' : 'Nova Execução'}
      </Typography>

      <Paper sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} orientation={isMobile ? 'vertical' : 'horizontal'}>
          {steps.map((label, index) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box sx={{ mt: 4 }}>
          {/* Passo 1: Informações Básicas */}
          {activeStep === 0 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Nome da Execução"
                  value={formData.nome}
                  onChange={(e) => handleFieldChange('nome', e.target.value)}
                  error={!!errors.nome}
                  helperText={errors.nome}
                  required
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Descrição"
                  value={formData.descricao}
                  onChange={(e) => handleFieldChange('descricao', e.target.value)}
                  multiline
                  rows={3}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth error={!!errors.nichoId} required>
                  <InputLabel>Nicho</InputLabel>
                  <Select
                    value={formData.nichoId}
                    onChange={(e) => handleFieldChange('nichoId', e.target.value)}
                    label="Nicho"
                  >
                    {nichos.map((nicho) => (
                      <MenuItem key={nicho.id} value={nicho.id}>
                        {nicho.nome}
                      </MenuItem>
                    ))}
                  </Select>
                  {errors.nichoId && <FormHelperText>{errors.nichoId}</FormHelperText>}
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth error={!!errors.categoriaId} required>
                  <InputLabel>Categoria</InputLabel>
                  <Select
                    value={formData.categoriaId}
                    onChange={(e) => handleFieldChange('categoriaId', e.target.value)}
                    label="Categoria"
                    disabled={!formData.nichoId}
                  >
                    {categoriasFiltradas.map((categoria) => (
                      <MenuItem key={categoria.id} value={categoria.id}>
                        {categoria.nome}
                      </MenuItem>
                    ))}
                  </Select>
                  {errors.categoriaId && <FormHelperText>{errors.categoriaId}</FormHelperText>}
                </FormControl>
              </Grid>
            </Grid>
          )}

          {/* Passo 2: Keywords */}
          {activeStep === 1 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card>
                  <CardHeader
                    title="Upload de Keywords"
                    action={
                      <Button
                        variant="outlined"
                        startIcon={<UploadIcon />}
                        component="label"
                      >
                        Upload Arquivo
                        <input
                          type="file"
                          multiple
                          accept=".txt,.csv"
                          onChange={handleFileUpload}
                          style={{ display: 'none' }}
                        />
                      </Button>
                    }
                  />
                  <CardContent>
                    {keywordFiles.length > 0 && (
                      <List>
                        {keywordFiles.map((file) => (
                          <ListItem key={file.id}>
                            <ListItemText
                              primary={file.nome}
                              secondary={`${file.keywords.length} keywords`}
                            />
                            <ListItemSecondaryAction>
                              <IconButton
                                edge="end"
                                onClick={() => removeKeywordFile(file.id)}
                              >
                                <DeleteIcon />
                              </IconButton>
                            </ListItemSecondaryAction>
                          </ListItem>
                        ))}
                      </List>
                    )}
                    
                    {uploadProgress > 0 && uploadProgress < 100 && (
                      <Box sx={{ mt: 2 }}>
                        <LinearProgress variant="determinate" value={uploadProgress} />
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Adicionar Keyword Manualmente"
                  placeholder="Digite uma keyword e pressione Enter"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      addKeyword((e.target as HTMLInputElement).value);
                      (e.target as HTMLInputElement).value = '';
                    }
                  }}
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Keywords ({formData.keywords.length})
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {formData.keywords.map((keyword, index) => (
                    <Chip
                      key={index}
                      label={keyword}
                      onDelete={() => removeKeyword(keyword)}
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
                {errors.keywords && (
                  <Alert severity="error" sx={{ mt: 1 }}>
                    {errors.keywords}
                  </Alert>
                )}
              </Grid>
            </Grid>
          )}

          {/* Passo 3: Parâmetros */}
          {activeStep === 2 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Configurações de Busca
                </Typography>
                
                <TextField
                  fullWidth
                  type="number"
                  label="Máximo de Keywords"
                  value={formData.parametros.maxKeywords}
                  onChange={(e) => handleParametroChange('maxKeywords', parseInt(e.target.value))}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">keywords</InputAdornment>,
                  }}
                  sx={{ mb: 2 }}
                />

                <Typography gutterBottom>
                  Profundidade de Busca: {formData.parametros.profundidadeBusca}
                </Typography>
                <Slider
                  value={formData.parametros.profundidadeBusca}
                  onChange={(_, value) => handleParametroChange('profundidadeBusca', value)}
                  min={1}
                  max={10}
                  marks
                  valueLabelDisplay="auto"
                  sx={{ mb: 2 }}
                />

                <TextField
                  fullWidth
                  type="number"
                  label="Tempo de Espera"
                  value={formData.parametros.tempoEspera}
                  onChange={(e) => handleParametroChange('tempoEspera', parseInt(e.target.value))}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">segundos</InputAdornment>,
                  }}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Configurações Avançadas
                </Typography>
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.parametros.usarProxy}
                      onChange={(e) => handleParametroChange('usarProxy', e.target.checked)}
                    />
                  }
                  label="Usar Proxy"
                  sx={{ mb: 1 }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.parametros.retryOnFail}
                      onChange={(e) => handleParametroChange('retryOnFail', e.target.checked)}
                    />
                  }
                  label="Tentar Novamente em Caso de Falha"
                  sx={{ mb: 1 }}
                />

                {formData.parametros.retryOnFail && (
                  <TextField
                    fullWidth
                    type="number"
                    label="Máximo de Tentativas"
                    value={formData.parametros.maxRetries}
                    onChange={(e) => handleParametroChange('maxRetries', parseInt(e.target.value))}
                    sx={{ mb: 2 }}
                  />
                )}

                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.parametros.salvarLogs}
                      onChange={(e) => handleParametroChange('salvarLogs', e.target.checked)}
                    />
                  }
                  label="Salvar Logs"
                  sx={{ mb: 1 }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.parametros.notificarConclusao}
                      onChange={(e) => handleParametroChange('notificarConclusao', e.target.checked)}
                    />
                  }
                  label="Notificar Conclusão"
                />
              </Grid>
            </Grid>
          )}

          {/* Passo 4: Agendamento */}
          {activeStep === 3 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.agendamento.executarAgora}
                      onChange={(e) => handleAgendamentoChange('executarAgora', e.target.checked)}
                    />
                  }
                  label="Executar Imediatamente"
                />
              </Grid>

              {!formData.agendamento.executarAgora && (
                <>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      type="date"
                      label="Data de Execução"
                      value={formData.agendamento.dataAgendada}
                      onChange={(e) => handleAgendamentoChange('dataAgendada', e.target.value)}
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      type="time"
                      label="Hora de Execução"
                      value={formData.agendamento.horaAgendada}
                      onChange={(e) => handleAgendamentoChange('horaAgendada', e.target.value)}
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formData.agendamento.repetir}
                          onChange={(e) => handleAgendamentoChange('repetir', e.target.checked)}
                        />
                      }
                      label="Repetir Execução"
                    />
                  </Grid>

                  {formData.agendamento.repetir && (
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth>
                        <InputLabel>Intervalo</InputLabel>
                        <Select
                          value={formData.agendamento.intervalo}
                          onChange={(e) => handleAgendamentoChange('intervalo', e.target.value)}
                          label="Intervalo"
                        >
                          <MenuItem value="diario">Diário</MenuItem>
                          <MenuItem value="semanal">Semanal</MenuItem>
                          <MenuItem value="mensal">Mensal</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                  )}
                </>
              )}
            </Grid>
          )}

          {/* Passo 5: Revisão */}
          {activeStep === 4 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Resumo da Execução
                </Typography>
                
                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {formData.nome}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {formData.descricao}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip label={nichos.find(n => n.id === formData.nichoId)?.nome} />
                      <Chip label={categorias.find(c => c.id === formData.categoriaId)?.nome} />
                    </Box>
                  </CardContent>
                </Card>

                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      Keywords ({formData.keywords.length})
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {formData.keywords.slice(0, 10).map((keyword, index) => (
                        <Chip key={index} label={keyword} size="small" />
                      ))}
                      {formData.keywords.length > 10 && (
                        <Chip label={`+${formData.keywords.length - 10} mais`} size="small" />
                      )}
                    </Box>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      Configurações
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2">
                          Máximo Keywords: {formData.parametros.maxKeywords}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">
                          Profundidade: {formData.parametros.profundidadeBusca}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">
                          Tempo Espera: {formData.parametros.tempoEspera}s
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">
                          Usar Proxy: {formData.parametros.usarProxy ? 'Sim' : 'Não'}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {/* Navegação */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
              startIcon={<CancelIcon />}
            >
              Anterior
            </Button>

            <Box sx={{ display: 'flex', gap: 1 }}>
              {activeStep < steps.length - 1 ? (
                <Button
                  variant="contained"
                  onClick={handleNext}
                  endIcon={<AddIcon />}
                >
                  Próximo
                </Button>
              ) : (
                <>
                  <Button
                    variant="outlined"
                    onClick={handleSave}
                    disabled={saving}
                    startIcon={<SaveIcon />}
                  >
                    {saving ? 'Salvando...' : 'Salvar'}
                  </Button>
                  
                  <Button
                    variant="contained"
                    onClick={handleExecuteNow}
                    disabled={saving}
                    startIcon={<PlayIcon />}
                  >
                    {saving ? 'Executando...' : 'Executar Agora'}
                  </Button>
                </>
              )}
            </Box>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default ExecucaoForm; 
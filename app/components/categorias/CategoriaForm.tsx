/**
 * CategoriaForm.tsx
 * 
 * Formulário de criação/edição de categorias com validação avançada
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_010
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Formulário com validação
 * - Seleção de nicho pai
 * - Upload de templates
 * - Configuração de prompts
 * - Integração com APIs do backend
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  Divider,
  Paper,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Save as SaveIcon,
  Cancel as CancelIcon,
  Upload as UploadIcon,
  Preview as PreviewIcon,
  Delete as DeleteIcon,
  CloudUpload as CloudUploadIcon,
  ExpandMore as ExpandMoreIcon,
  Category as CategoryIcon,
  Template as TemplateIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

// Tipos
interface CategoriaFormData {
  nome: string;
  descricao: string;
  categoriaPai?: string;
  nivel: number;
  status: 'ativo' | 'inativo' | 'pendente';
  configuracao: {
    maxNichos: number;
    maxKeywords: number;
    intervaloExecucao: number;
    ativo: boolean;
  };
  templates: {
    promptTemplate: string;
    keywordsTemplate: string;
    outputTemplate: string;
  };
  nichosAssociados: string[];
}

interface CategoriaFormProps {
  categoria?: Partial<CategoriaFormData>;
  categoriasPai?: Array<{ id: string; nome: string; nivel: number }>;
  nichosDisponiveis?: Array<{ id: string; nome: string; categoria: string }>;
  onSubmit: (data: CategoriaFormData) => void;
  onCancel: () => void;
  loading?: boolean;
  error?: string | null;
}

interface ValidationErrors {
  nome?: string;
  descricao?: string;
  categoriaPai?: string;
  templates?: {
    promptTemplate?: string;
    keywordsTemplate?: string;
    outputTemplate?: string;
  };
}

/**
 * Componente de formulário de categoria
 */
const CategoriaForm: React.FC<CategoriaFormProps> = ({
  categoria,
  categoriasPai = [],
  nichosDisponiveis = [],
  onSubmit,
  onCancel,
  loading = false,
  error = null,
}) => {
  // Estados
  const [formData, setFormData] = useState<CategoriaFormData>({
    nome: categoria?.nome || '',
    descricao: categoria?.descricao || '',
    categoriaPai: categoria?.categoriaPai || '',
    nivel: categoria?.nivel || 1,
    status: categoria?.status || 'pendente',
    configuracao: {
      maxNichos: categoria?.configuracao?.maxNichos || 10,
      maxKeywords: categoria?.configuracao?.maxKeywords || 1000,
      intervaloExecucao: categoria?.configuracao?.intervaloExecucao || 24,
      ativo: categoria?.configuracao?.ativo ?? true,
    },
    templates: {
      promptTemplate: categoria?.templates?.promptTemplate || '',
      keywordsTemplate: categoria?.templates?.keywordsTemplate || '',
      outputTemplate: categoria?.templates?.outputTemplate || '',
    },
    nichosAssociados: categoria?.nichosAssociados || [],
  });

  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [uploadedTemplates, setUploadedTemplates] = useState<{ [key: string]: File | null }>({});
  const [showPreview, setShowPreview] = useState(false);

  // Efeitos
  useEffect(() => {
    // Atualizar nível baseado na categoria pai selecionada
    if (formData.categoriaPai) {
      const categoriaPaiSelecionada = categoriasPai.find(cat => cat.id === formData.categoriaPai);
      if (categoriaPaiSelecionada) {
        setFormData(prev => ({ ...prev, nivel: categoriaPaiSelecionada.nivel + 1 }));
      }
    } else {
      setFormData(prev => ({ ...prev, nivel: 1 }));
    }
  }, [formData.categoriaPai, categoriasPai]);

  /**
   * Valida o formulário em tempo real
   */
  const validateField = (field: keyof CategoriaFormData, value: any): string | undefined => {
    switch (field) {
      case 'nome':
        if (!value.trim()) return 'Nome é obrigatório';
        if (value.length < 3) return 'Nome deve ter pelo menos 3 caracteres';
        if (value.length > 100) return 'Nome deve ter no máximo 100 caracteres';
        break;
      case 'descricao':
        if (!value.trim()) return 'Descrição é obrigatória';
        if (value.length < 10) return 'Descrição deve ter pelo menos 10 caracteres';
        if (value.length > 500) return 'Descrição deve ter no máximo 500 caracteres';
        break;
      default:
        break;
    }
    return undefined;
  };

  /**
   * Manipula mudança de campo
   */
  const handleFieldChange = (field: keyof CategoriaFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Validação em tempo real
    const error = validateField(field, value);
    setValidationErrors(prev => ({
      ...prev,
      [field]: error,
    }));
  };

  /**
   * Manipula mudança de configuração
   */
  const handleConfigChange = (field: keyof CategoriaFormData['configuracao'], value: any) => {
    setFormData(prev => ({
      ...prev,
      configuracao: {
        ...prev.configuracao,
        [field]: value,
      },
    }));
  };

  /**
   * Manipula mudança de template
   */
  const handleTemplateChange = (field: keyof CategoriaFormData['templates'], value: string) => {
    setFormData(prev => ({
      ...prev,
      templates: {
        ...prev.templates,
        [field]: value,
      },
    }));
  };

  /**
   * Manipula upload de arquivo de template
   */
  const handleTemplateUpload = (event: React.ChangeEvent<HTMLInputElement>, templateType: string) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedTemplates(prev => ({ ...prev, [templateType]: file }));
      
      // Processar arquivo
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        handleTemplateChange(templateType as keyof CategoriaFormData['templates'], content);
      };
      reader.readAsText(file);
    }
  };

  /**
   * Remove arquivo de template carregado
   */
  const handleRemoveTemplate = (templateType: string) => {
    setUploadedTemplates(prev => ({ ...prev, [templateType]: null }));
    handleTemplateChange(templateType as keyof CategoriaFormData['templates'], '');
  };

  /**
   * Manipula seleção de nichos
   */
  const handleNichosChange = (nichoId: string) => {
    setFormData(prev => ({
      ...prev,
      nichosAssociados: prev.nichosAssociados.includes(nichoId)
        ? prev.nichosAssociados.filter(id => id !== nichoId)
        : [...prev.nichosAssociados, nichoId],
    }));
  };

  /**
   * Valida formulário completo
   */
  const validateForm = (): boolean => {
    const errors: ValidationErrors = {};
    
    errors.nome = validateField('nome', formData.nome);
    errors.descricao = validateField('descricao', formData.descricao);
    
    // Validação de templates
    if (!formData.templates.promptTemplate.trim()) {
      errors.templates = { ...errors.templates, promptTemplate: 'Template de prompt é obrigatório' };
    }
    
    setValidationErrors(errors);
    return !Object.values(errors).some(error => error) && 
           !errors.templates?.promptTemplate;
  };

  /**
   * Manipula envio do formulário
   */
  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  /**
   * Renderiza preview dos dados
   */
  const renderPreview = () => (
    <Paper sx={{ p: 2, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Preview da Categoria
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle2" color="textSecondary">
            Nome
          </Typography>
          <Typography variant="body1">{formData.nome}</Typography>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle2" color="textSecondary">
            Nível
          </Typography>
          <Chip label={`Nível ${formData.nivel}`} size="small" />
        </Grid>
        <Grid item xs={12}>
          <Typography variant="subtitle2" color="textSecondary">
            Descrição
          </Typography>
          <Typography variant="body2">{formData.descricao}</Typography>
        </Grid>
        <Grid item xs={12}>
          <Typography variant="subtitle2" color="textSecondary">
            Nichos Associados ({formData.nichosAssociados.length})
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
            {formData.nichosAssociados.map(nichoId => {
              const nicho = nichosDisponiveis.find(n => n.id === nichoId);
              return nicho ? (
                <Chip key={nichoId} label={nicho.nome} size="small" variant="outlined" />
              ) : null;
            })}
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 900, mx: 'auto' }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            {categoria ? 'Editar Categoria' : 'Nova Categoria'}
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={3}>
            {/* Informações Básicas */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Informações Básicas
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Nome da Categoria"
                value={formData.nome}
                onChange={(e) => handleFieldChange('nome', e.target.value)}
                error={!!validationErrors.nome}
                helperText={validationErrors.nome}
                required
                disabled={loading}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Categoria Pai</InputLabel>
                <Select
                  value={formData.categoriaPai}
                  onChange={(e) => handleFieldChange('categoriaPai', e.target.value)}
                  label="Categoria Pai"
                  disabled={loading}
                >
                  <MenuItem value="">Nenhuma (Categoria Raiz)</MenuItem>
                  {categoriasPai.map(cat => (
                    <MenuItem key={cat.id} value={cat.id}>
                      {cat.nome} (Nível {cat.nivel})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Descrição"
                value={formData.descricao}
                onChange={(e) => handleFieldChange('descricao', e.target.value)}
                error={!!validationErrors.descricao}
                helperText={validationErrors.descricao}
                multiline
                rows={3}
                required
                disabled={loading}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => handleFieldChange('status', e.target.value)}
                  label="Status"
                  disabled={loading}
                >
                  <MenuItem value="ativo">Ativo</MenuItem>
                  <MenuItem value="inativo">Inativo</MenuItem>
                  <MenuItem value="pendente">Pendente</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.configuracao.ativo}
                    onChange={(e) => handleConfigChange('ativo', e.target.checked)}
                    disabled={loading}
                  />
                }
                label="Configuração Ativa"
              />
            </Grid>

            {/* Configurações */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Configurações
              </Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Máximo de Nichos"
                type="number"
                value={formData.configuracao.maxNichos}
                onChange={(e) => handleConfigChange('maxNichos', parseInt(e.target.value))}
                inputProps={{ min: 1, max: 100 }}
                disabled={loading}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Máximo de Keywords"
                type="number"
                value={formData.configuracao.maxKeywords}
                onChange={(e) => handleConfigChange('maxKeywords', parseInt(e.target.value))}
                inputProps={{ min: 1, max: 10000 }}
                disabled={loading}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Intervalo de Execução (horas)"
                type="number"
                value={formData.configuracao.intervaloExecucao}
                onChange={(e) => handleConfigChange('intervaloExecucao', parseInt(e.target.value))}
                inputProps={{ min: 1, max: 168 }}
                disabled={loading}
              />
            </Grid>

            {/* Templates */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Templates
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TemplateIcon />
                    <Typography>Template de Prompt</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                        <Button
                          variant="outlined"
                          component="label"
                          startIcon={<CloudUploadIcon />}
                          disabled={loading}
                        >
                          Upload de Template
                          <input
                            type="file"
                            hidden
                            accept=".txt,.md"
                            onChange={(e) => handleTemplateUpload(e, 'promptTemplate')}
                          />
                        </Button>
                        
                        {uploadedTemplates.promptTemplate && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2">
                              {uploadedTemplates.promptTemplate.name}
                            </Typography>
                            <Tooltip title="Remover arquivo">
                              <IconButton size="small" onClick={() => handleRemoveTemplate('promptTemplate')}>
                                <DeleteIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        )}
                      </Box>
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Template de Prompt"
                        value={formData.templates.promptTemplate}
                        onChange={(e) => handleTemplateChange('promptTemplate', e.target.value)}
                        error={!!validationErrors.templates?.promptTemplate}
                        helperText={validationErrors.templates?.promptTemplate || 'Use {{keyword}} para variáveis'}
                        multiline
                        rows={6}
                        placeholder="Template para geração de prompts..."
                        disabled={loading}
                      />
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>

            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CategoryIcon />
                    <Typography>Template de Keywords</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                        <Button
                          variant="outlined"
                          component="label"
                          startIcon={<CloudUploadIcon />}
                          disabled={loading}
                        >
                          Upload de Template
                          <input
                            type="file"
                            hidden
                            accept=".txt,.csv"
                            onChange={(e) => handleTemplateUpload(e, 'keywordsTemplate')}
                          />
                        </Button>
                      </Box>
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Template de Keywords"
                        value={formData.templates.keywordsTemplate}
                        onChange={(e) => handleTemplateChange('keywordsTemplate', e.target.value)}
                        multiline
                        rows={4}
                        placeholder="Template para processamento de keywords..."
                        disabled={loading}
                      />
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>

            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <SettingsIcon />
                    <Typography>Template de Saída</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                        <Button
                          variant="outlined"
                          component="label"
                          startIcon={<CloudUploadIcon />}
                          disabled={loading}
                        >
                          Upload de Template
                          <input
                            type="file"
                            hidden
                            accept=".txt,.json,.xml"
                            onChange={(e) => handleTemplateUpload(e, 'outputTemplate')}
                          />
                        </Button>
                      </Box>
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Template de Saída"
                        value={formData.templates.outputTemplate}
                        onChange={(e) => handleTemplateChange('outputTemplate', e.target.value)}
                        multiline
                        rows={4}
                        placeholder="Template para formatação de saída..."
                        disabled={loading}
                      />
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* Nichos Associados */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Nichos Associados
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {nichosDisponiveis.map(nicho => (
                  <Chip
                    key={nicho.id}
                    label={nicho.nome}
                    onClick={() => handleNichosChange(nicho.id)}
                    color={formData.nichosAssociados.includes(nicho.id) ? 'primary' : 'default'}
                    variant={formData.nichosAssociados.includes(nicho.id) ? 'filled' : 'outlined'}
                    clickable
                  />
                ))}
              </Box>
            </Grid>

            {/* Preview */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Button
                  variant="outlined"
                  startIcon={<PreviewIcon />}
                  onClick={() => setShowPreview(!showPreview)}
                  disabled={loading}
                >
                  {showPreview ? 'Ocultar Preview' : 'Mostrar Preview'}
                </Button>
              </Box>
              
              {showPreview && renderPreview()}
            </Grid>
          </Grid>

          {/* Ações */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 3 }}>
            <Button
              variant="outlined"
              startIcon={<CancelIcon />}
              onClick={onCancel}
              disabled={loading}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              variant="contained"
              startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
              disabled={loading}
            >
              {loading ? 'Salvando...' : 'Salvar Categoria'}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CategoriaForm; 
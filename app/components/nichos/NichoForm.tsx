/**
 * NichoForm.tsx
 * 
 * Formulário de criação/edição de nichos com validação avançada
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_006
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Formulário de criação/edição
 * - Validação em tempo real
 * - Upload de arquivos
 * - Preview de dados
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
} from '@mui/material';
import {
  Save as SaveIcon,
  Cancel as CancelIcon,
  Upload as UploadIcon,
  Preview as PreviewIcon,
  Delete as DeleteIcon,
  CloudUpload as CloudUploadIcon,
} from '@mui/icons-material';

// Tipos
interface NichoFormData {
  nome: string;
  descricao: string;
  categoria: string;
  status: 'ativo' | 'inativo' | 'pendente';
  keywords: string[];
  configuracao: {
    maxKeywords: number;
    intervaloExecucao: number;
    ativo: boolean;
  };
}

interface NichoFormProps {
  nicho?: Partial<NichoFormData>;
  onSubmit: (data: NichoFormData) => void;
  onCancel: () => void;
  loading?: boolean;
  error?: string | null;
}

interface ValidationErrors {
  nome?: string;
  descricao?: string;
  categoria?: string;
  keywords?: string;
}

/**
 * Componente de formulário de nicho
 */
const NichoForm: React.FC<NichoFormProps> = ({
  nicho,
  onSubmit,
  onCancel,
  loading = false,
  error = null,
}) => {
  // Estados
  const [formData, setFormData] = useState<NichoFormData>({
    nome: nicho?.nome || '',
    descricao: nicho?.descricao || '',
    categoria: nicho?.categoria || '',
    status: nicho?.status || 'pendente',
    keywords: nicho?.keywords || [],
    configuracao: {
      maxKeywords: nicho?.configuracao?.maxKeywords || 1000,
      intervaloExecucao: nicho?.configuracao?.intervaloExecucao || 24,
      ativo: nicho?.configuracao?.ativo ?? true,
    },
  });

  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [keywordsText, setKeywordsText] = useState('');

  // Efeitos
  useEffect(() => {
    // Converter keywords array para texto
    if (formData.keywords.length > 0) {
      setKeywordsText(formData.keywords.join('\n'));
    }
  }, []);

  /**
   * Valida o formulário em tempo real
   */
  const validateField = (field: keyof NichoFormData, value: any): string | undefined => {
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
      case 'categoria':
        if (!value.trim()) return 'Categoria é obrigatória';
        break;
      default:
        break;
    }
    return undefined;
  };

  /**
   * Manipula mudança de campo
   */
  const handleFieldChange = (field: keyof NichoFormData, value: any) => {
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
  const handleConfigChange = (field: keyof NichoFormData['configuracao'], value: any) => {
    setFormData(prev => ({
      ...prev,
      configuracao: {
        ...prev.configuracao,
        [field]: value,
      },
    }));
  };

  /**
   * Manipula upload de arquivo
   */
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      
      // Processar arquivo de keywords
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        const keywords = content
          .split('\n')
          .map(k => k.trim())
          .filter(k => k.length > 0);
        
        setFormData(prev => ({ ...prev, keywords }));
        setKeywordsText(content);
      };
      reader.readAsText(file);
    }
  };

  /**
   * Manipula mudança de texto de keywords
   */
  const handleKeywordsChange = (value: string) => {
    setKeywordsText(value);
    const keywords = value
      .split('\n')
      .map(k => k.trim())
      .filter(k => k.length > 0);
    setFormData(prev => ({ ...prev, keywords }));
  };

  /**
   * Remove arquivo carregado
   */
  const handleRemoveFile = () => {
    setUploadedFile(null);
    setFormData(prev => ({ ...prev, keywords: [] }));
    setKeywordsText('');
  };

  /**
   * Valida formulário completo
   */
  const validateForm = (): boolean => {
    const errors: ValidationErrors = {};
    
    errors.nome = validateField('nome', formData.nome);
    errors.descricao = validateField('descricao', formData.descricao);
    errors.categoria = validateField('categoria', formData.categoria);
    
    if (formData.keywords.length === 0) {
      errors.keywords = 'Pelo menos uma keyword é obrigatória';
    }
    
    setValidationErrors(errors);
    return !Object.values(errors).some(error => error);
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
        Preview do Nicho
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
            Categoria
          </Typography>
          <Chip label={formData.categoria} size="small" />
        </Grid>
        <Grid item xs={12}>
          <Typography variant="subtitle2" color="textSecondary">
            Descrição
          </Typography>
          <Typography variant="body2">{formData.descricao}</Typography>
        </Grid>
        <Grid item xs={12}>
          <Typography variant="subtitle2" color="textSecondary">
            Keywords ({formData.keywords.length})
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
            {formData.keywords.slice(0, 10).map((keyword, index) => (
              <Chip key={index} label={keyword} size="small" variant="outlined" />
            ))}
            {formData.keywords.length > 10 && (
              <Chip label={`+${formData.keywords.length - 10} mais`} size="small" />
            )}
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 800, mx: 'auto' }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            {nicho ? 'Editar Nicho' : 'Novo Nicho'}
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
                label="Nome do Nicho"
                value={formData.nome}
                onChange={(e) => handleFieldChange('nome', e.target.value)}
                error={!!validationErrors.nome}
                helperText={validationErrors.nome}
                required
                disabled={loading}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth required error={!!validationErrors.categoria}>
                <InputLabel>Categoria</InputLabel>
                <Select
                  value={formData.categoria}
                  onChange={(e) => handleFieldChange('categoria', e.target.value)}
                  label="Categoria"
                  disabled={loading}
                >
                  <MenuItem value="Tecnologia">Tecnologia</MenuItem>
                  <MenuItem value="Saúde">Saúde</MenuItem>
                  <MenuItem value="Finanças">Finanças</MenuItem>
                  <MenuItem value="Educação">Educação</MenuItem>
                  <MenuItem value="Marketing">Marketing</MenuItem>
                  <MenuItem value="E-commerce">E-commerce</MenuItem>
                  <MenuItem value="Outros">Outros</MenuItem>
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

            {/* Upload de Keywords */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Keywords
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<CloudUploadIcon />}
                  disabled={loading}
                >
                  Upload de Arquivo
                  <input
                    type="file"
                    hidden
                    accept=".txt,.csv"
                    onChange={handleFileUpload}
                  />
                </Button>
                
                {uploadedFile && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2">
                      {uploadedFile.name}
                    </Typography>
                    <Tooltip title="Remover arquivo">
                      <IconButton size="small" onClick={handleRemoveFile}>
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
                label="Keywords (uma por linha)"
                value={keywordsText}
                onChange={(e) => handleKeywordsChange(e.target.value)}
                error={!!validationErrors.keywords}
                helperText={validationErrors.keywords || `${formData.keywords.length} keywords carregadas`}
                multiline
                rows={6}
                placeholder="Digite as keywords, uma por linha..."
                disabled={loading}
              />
            </Grid>

            {/* Configurações */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Configurações
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
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

            <Grid item xs={12} md={6}>
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
              {loading ? 'Salvando...' : 'Salvar Nicho'}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default NichoForm; 
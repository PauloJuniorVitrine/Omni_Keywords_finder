/**
 * Página de Upload de Arquivos TXT - Omni Keywords Finder
 * Interface completa para upload e processamento de arquivos
 * 
 * @author Omni Keywords Finder Team
 * @version 1.0.0
 * @date 2025-01-27
 */

import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Switch,
  FormControlLabel,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar
} from '@mui/material';
import {
  Upload as UploadIcon,
  Settings as SettingsIcon,
  History as HistoryIcon,
  Analytics as AnalyticsIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Pause as PauseIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// Componentes
import FileUpload from '../components/FileUpload';

// Tipos
interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  content: string;
  lines: string[];
  status: 'uploading' | 'success' | 'error' | 'processing';
  progress: number;
  error?: string;
  uploadTime: Date;
  categoryId?: number;
  cluster?: string;
}

interface ProcessingResult {
  fileId: string;
  processedLines: number;
  keywords: string[];
  timestamp: Date;
  executionId?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
  error?: string;
}

interface UploadSettings {
  autoProcess: boolean;
  defaultCategory: number;
  defaultCluster: string;
  maxConcurrent: number;
  validateKeywords: boolean;
  removeDuplicates: boolean;
  caseSensitive: boolean;
}

// Estilos
const PageContainer = styled(Container)(({ theme }) => ({
  paddingTop: theme.spacing(4),
  paddingBottom: theme.spacing(4),
}));

const StatsCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
}));

const ProcessingCard = styled(Card)(({ theme }) => ({
  marginTop: theme.spacing(2),
}));

const UploadPage: React.FC = () => {
  // Estados
  const [activeTab, setActiveTab] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [processingResults, setProcessingResults] = useState<ProcessingResult[]>([]);
  const [uploadSettings, setUploadSettings] = useState<UploadSettings>({
    autoProcess: false,
    defaultCategory: 1,
    defaultCluster: 'default',
    maxConcurrent: 5,
    validateKeywords: true,
    removeDuplicates: true,
    caseSensitive: false,
  });
  const [processing, setProcessing] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info',
  });

  // Handlers
  const handleFilesUploaded = (files: UploadedFile[]) => {
    setUploadedFiles(prev => [...prev, ...files]);
    showSnackbar(`${files.length} arquivo(s) carregado(s) com sucesso!`, 'success');
  };

  const handleFileProcessed = (fileId: string, result: any) => {
    const processingResult: ProcessingResult = {
      fileId,
      processedLines: result.processedLines,
      keywords: result.keywords,
      timestamp: result.timestamp,
      status: 'completed',
      result,
    };

    setProcessingResults(prev => [...prev, processingResult]);
    showSnackbar(`Arquivo processado com sucesso!`, 'success');
  };

  const handleProcessAllFiles = async () => {
    setProcessing(true);
    
    try {
      // Simular processamento em lote
      const filesToProcess = uploadedFiles.filter(f => f.status === 'success');
      
      for (let i = 0; i < filesToProcess.length; i++) {
        const file = filesToProcess[i];
        
        // Atualizar status
        setUploadedFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'processing' } : f
        ));
        
        // Simular processamento
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Resultado simulado
        const result = {
          fileId: file.id,
          processedLines: file.lines.length,
          keywords: file.lines,
          timestamp: new Date(),
        };
        
        handleFileProcessed(file.id, result);
        
        // Atualizar status
        setUploadedFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'success' } : f
        ));
      }
      
      showSnackbar('Todos os arquivos foram processados!', 'success');
      
    } catch (error) {
      showSnackbar('Erro ao processar arquivos: ' + (error as Error).message, 'error');
    } finally {
      setProcessing(false);
    }
  };

  const handleRemoveFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
    setProcessingResults(prev => prev.filter(r => r.fileId !== fileId));
    showSnackbar('Arquivo removido com sucesso!', 'info');
  };

  const handleClearAll = () => {
    setUploadedFiles([]);
    setProcessingResults([]);
    showSnackbar('Todos os arquivos foram removidos!', 'info');
  };

  const handleSettingsChange = (setting: keyof UploadSettings, value: any) => {
    setUploadSettings(prev => ({
      ...prev,
      [setting]: value,
    }));
  };

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info' | 'warning') => {
    setSnackbar({
      open: true,
      message,
      severity,
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  // Estatísticas
  const stats = {
    totalFiles: uploadedFiles.length,
    processedFiles: processingResults.length,
    totalLines: uploadedFiles.reduce((sum, file) => sum + file.lines.length, 0),
    totalSize: uploadedFiles.reduce((sum, file) => sum + file.size, 0),
    successFiles: uploadedFiles.filter(f => f.status === 'success').length,
    errorFiles: uploadedFiles.filter(f => f.status === 'error').length,
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <PageContainer maxWidth="xl">
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          Upload de Arquivos TXT
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Faça upload de arquivos de texto contendo palavras-chave para processamento
        </Typography>
      </Box>

      {/* Estatísticas */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Arquivos
              </Typography>
              <Typography variant="h4">
                {stats.totalFiles}
              </Typography>
            </CardContent>
          </StatsCard>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Processados
              </Typography>
              <Typography variant="h4" color="success.main">
                {stats.processedFiles}
              </Typography>
            </CardContent>
          </StatsCard>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Linhas
              </Typography>
              <Typography variant="h4">
                {stats.totalLines.toLocaleString()}
              </Typography>
            </CardContent>
          </StatsCard>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Tamanho Total
              </Typography>
              <Typography variant="h4">
                {formatFileSize(stats.totalSize)}
              </Typography>
            </CardContent>
          </StatsCard>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
        >
          <Tab label="Upload" icon={<UploadIcon />} />
          <Tab label="Processamento" icon={<PlayIcon />} />
          <Tab label="Resultados" icon={<AnalyticsIcon />} />
          <Tab label="Histórico" icon={<HistoryIcon />} />
        </Tabs>
      </Paper>

      {/* Conteúdo das Tabs */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Upload de Arquivos
                </Typography>
                <Box>
                  <Button
                    startIcon={<SettingsIcon />}
                    onClick={() => setShowSettings(true)}
                    sx={{ mr: 1 }}
                  >
                    Configurações
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={handleClearAll}
                    disabled={uploadedFiles.length === 0}
                  >
                    Limpar Todos
                  </Button>
                </Box>
              </Box>
              
              <FileUpload
                onFilesUploaded={handleFilesUploaded}
                onFileProcessed={handleFileProcessed}
                maxFiles={10}
                maxFileSize={5 * 1024 * 1024}
                allowedTypes={['.txt', '.csv']}
                showPreview={true}
                enableDragDrop={true}
                autoProcess={uploadSettings.autoProcess}
              />
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Status dos Arquivos
              </Typography>
              
              <List>
                <ListItem>
                  <ListItemIcon>
                    <CheckIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Sucesso"
                    secondary={`${stats.successFiles} arquivo(s)`}
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <ErrorIcon color="error" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Erro"
                    secondary={`${stats.errorFiles} arquivo(s)`}
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <InfoIcon color="info" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Processando"
                    secondary={`${uploadedFiles.filter(f => f.status === 'processing').length} arquivo(s)`}
                  />
                </ListItem>
              </List>
            </Paper>
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && (
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h6">
              Processamento
            </Typography>
            <Button
              variant="contained"
              startIcon={processing ? <CircularProgress size={20} /> : <PlayIcon />}
              onClick={handleProcessAllFiles}
              disabled={processing || uploadedFiles.filter(f => f.status === 'success').length === 0}
            >
              {processing ? 'Processando...' : 'Processar Todos'}
            </Button>
          </Box>
          
          <Stepper activeStep={activeStep} orientation="vertical">
            <Step>
              <StepLabel>Upload de Arquivos</StepLabel>
              <StepContent>
                <Typography>
                  {uploadedFiles.length} arquivo(s) carregado(s)
                </Typography>
              </StepContent>
            </Step>
            
            <Step>
              <StepLabel>Validação</StepLabel>
              <StepContent>
                <Typography>
                  Validando formato e conteúdo dos arquivos
                </Typography>
              </StepContent>
            </Step>
            
            <Step>
              <StepLabel>Processamento</StepLabel>
              <StepContent>
                <Typography>
                  Processando palavras-chave e gerando resultados
                </Typography>
              </StepContent>
            </Step>
            
            <Step>
              <StepLabel>Finalização</StepLabel>
              <StepContent>
                <Typography>
                  Salvando resultados e gerando relatórios
                </Typography>
              </StepContent>
            </Step>
          </Stepper>
        </Paper>
      )}

      {activeTab === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Resultados do Processamento
          </Typography>
          
          {processingResults.length === 0 ? (
            <Alert severity="info">
              Nenhum resultado disponível. Processe alguns arquivos primeiro.
            </Alert>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Arquivo</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Linhas Processadas</TableCell>
                    <TableCell>Palavras-chave</TableCell>
                    <TableCell>Data/Hora</TableCell>
                    <TableCell>Ações</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {processingResults.map((result) => {
                    const file = uploadedFiles.find(f => f.id === result.fileId);
                    return (
                      <TableRow key={result.fileId}>
                        <TableCell>{file?.name || 'Arquivo não encontrado'}</TableCell>
                        <TableCell>
                          <Chip
                            label={result.status}
                            color={result.status === 'completed' ? 'success' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{result.processedLines}</TableCell>
                        <TableCell>{result.keywords.length}</TableCell>
                        <TableCell>
                          {result.timestamp.toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Tooltip title="Download">
                            <IconButton size="small">
                              <DownloadIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Remover">
                            <IconButton
                              size="small"
                              onClick={() => handleRemoveFile(result.fileId)}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>
      )}

      {activeTab === 3 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Histórico de Uploads
          </Typography>
          
          <Alert severity="info">
            Histórico de uploads e processamentos será implementado em breve.
          </Alert>
        </Paper>
      )}

      {/* Dialog de Configurações */}
      <Dialog
        open={showSettings}
        onClose={() => setShowSettings(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Configurações de Upload
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={uploadSettings.autoProcess}
                    onChange={(e) => handleSettingsChange('autoProcess', e.target.checked)}
                  />
                }
                label="Processar automaticamente após upload"
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Categoria Padrão</InputLabel>
                <Select
                  value={uploadSettings.defaultCategory}
                  onChange={(e) => handleSettingsChange('defaultCategory', e.target.value)}
                  label="Categoria Padrão"
                >
                  <MenuItem value={1}>Categoria 1</MenuItem>
                  <MenuItem value={2}>Categoria 2</MenuItem>
                  <MenuItem value={3}>Categoria 3</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Cluster Padrão"
                value={uploadSettings.defaultCluster}
                onChange={(e) => handleSettingsChange('defaultCluster', e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Máximo Concorrente"
                value={uploadSettings.maxConcurrent}
                onChange={(e) => handleSettingsChange('maxConcurrent', parseInt(e.target.value))}
                inputProps={{ min: 1, max: 10 }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={uploadSettings.validateKeywords}
                    onChange={(e) => handleSettingsChange('validateKeywords', e.target.checked)}
                  />
                }
                label="Validar palavras-chave"
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={uploadSettings.removeDuplicates}
                    onChange={(e) => handleSettingsChange('removeDuplicates', e.target.checked)}
                  />
                }
                label="Remover duplicatas"
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={uploadSettings.caseSensitive}
                    onChange={(e) => handleSettingsChange('caseSensitive', e.target.checked)}
                  />
                }
                label="Case sensitive"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>
            Cancelar
          </Button>
          <Button variant="contained" onClick={() => setShowSettings(false)}>
            Salvar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert
          severity={snackbar.severity}
          onClose={handleCloseSnackbar}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </PageContainer>
  );
};

export default UploadPage; 
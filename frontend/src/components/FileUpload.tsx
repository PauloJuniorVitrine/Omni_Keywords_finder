/**
 * Componente de Upload de Arquivos TXT - Omni Keywords Finder
 * Upload com drag & drop, validação e progress bar
 * 
 * @author Omni Keywords Finder Team
 * @version 1.0.0
 * @date 2025-01-27
 */

import React, { useState, useRef, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  IconButton,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  Tooltip,
  Snackbar
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

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

interface FileUploadProps {
  onFilesUploaded: (files: UploadedFile[]) => void;
  onFileProcessed: (fileId: string, result: any) => void;
  maxFiles?: number;
  maxFileSize?: number; // em bytes
  allowedTypes?: string[];
  showPreview?: boolean;
  enableDragDrop?: boolean;
  autoProcess?: boolean;
}

// Estilos
const UploadArea = styled(Paper)(({ theme, isDragOver }: { theme: any; isDragOver: boolean }) => ({
  border: `2px dashed ${isDragOver ? theme.palette.primary.main : theme.palette.divider}`,
  borderRadius: theme.spacing(2),
  padding: theme.spacing(4),
  textAlign: 'center',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
  backgroundColor: isDragOver ? theme.palette.action.hover : theme.palette.background.paper,
  '&:hover': {
    borderColor: theme.palette.primary.main,
    backgroundColor: theme.palette.action.hover,
  },
}));

const FileListContainer = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(2),
  maxHeight: '400px',
  overflowY: 'auto',
}));

const FileItem = styled(Card)(({ theme }) => ({
  marginBottom: theme.spacing(1),
  '&:last-child': {
    marginBottom: 0,
  },
}));

const ProgressContainer = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(1),
  marginBottom: theme.spacing(1),
}));

const FileUpload: React.FC<FileUploadProps> = ({
  onFilesUploaded,
  onFileProcessed,
  maxFiles = 10,
  maxFileSize = 5 * 1024 * 1024, // 5MB
  allowedTypes = ['.txt', '.csv'],
  showPreview = true,
  enableDragDrop = true,
  autoProcess = false,
}) => {
  // Estados
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [previewFile, setPreviewFile] = useState<UploadedFile | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [processingConfig, setProcessingConfig] = useState({
    categoryId: '',
    cluster: '',
  });

  // Refs
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropZoneRef = useRef<HTMLDivElement>(null);

  // Funções auxiliares
  const generateFileId = () => `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const validateFile = (file: File): string | null => {
    // Verificar tipo
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedTypes.includes(fileExtension)) {
      return `Tipo de arquivo não suportado. Tipos permitidos: ${allowedTypes.join(', ')}`;
    }

    // Verificar tamanho
    if (file.size > maxFileSize) {
      return `Arquivo muito grande. Tamanho máximo: ${formatFileSize(maxFileSize)}`;
    }

    // Verificar limite de arquivos
    if (files.length >= maxFiles) {
      return `Limite de arquivos atingido. Máximo: ${maxFiles}`;
    }

    return null;
  };

  const readFileContent = async (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        resolve(content);
      };
      reader.onerror = () => reject(new Error('Erro ao ler arquivo'));
      reader.readAsText(file, 'UTF-8');
    });
  };

  const parseFileContent = (content: string): string[] => {
    return content
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0);
  };

  // Handlers
  const handleFileSelect = useCallback(async (selectedFiles: FileList | File[]) => {
    setError(null);
    setUploading(true);

    try {
      const fileArray = Array.from(selectedFiles);
      const newFiles: UploadedFile[] = [];

      for (const file of fileArray) {
        // Validar arquivo
        const validationError = validateFile(file);
        if (validationError) {
          setError(validationError);
          continue;
        }

        // Ler conteúdo
        const content = await readFileContent(file);
        const lines = parseFileContent(content);

        // Criar objeto de arquivo
        const uploadedFile: UploadedFile = {
          id: generateFileId(),
          name: file.name,
          size: file.size,
          type: file.type,
          content,
          lines,
          status: 'uploading',
          progress: 0,
          uploadTime: new Date(),
        };

        newFiles.push(uploadedFile);
      }

      // Simular upload progressivo
      for (const file of newFiles) {
        for (let progress = 0; progress <= 100; progress += 10) {
          file.progress = progress;
          setFiles(prev => [...prev]);
          await new Promise(resolve => setTimeout(resolve, 100));
        }
        file.status = 'success';
      }

      // Adicionar arquivos
      setFiles(prev => [...prev, ...newFiles]);
      setSuccess(`${newFiles.length} arquivo(s) carregado(s) com sucesso!`);

      // Callback
      onFilesUploaded(newFiles);

      // Processar automaticamente se habilitado
      if (autoProcess) {
        newFiles.forEach(file => handleProcessFile(file.id));
      }

    } catch (err) {
      setError('Erro ao processar arquivos: ' + (err as Error).message);
    } finally {
      setUploading(false);
    }
  }, [files, maxFiles, maxFileSize, allowedTypes, autoProcess, onFilesUploaded]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (enableDragDrop) {
      setIsDragOver(true);
    }
  }, [enableDragDrop]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (enableDragDrop && e.dataTransfer.files) {
      handleFileSelect(e.dataTransfer.files);
    }
  }, [enableDragDrop, handleFileSelect]);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFileSelect(e.target.files);
    }
  };

  const handleRemoveFile = (fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
    setSuccess('Arquivo removido com sucesso!');
  };

  const handlePreviewFile = (file: UploadedFile) => {
    setPreviewFile(file);
    setPreviewOpen(true);
  };

  const handleProcessFile = async (fileId: string) => {
    const file = files.find(f => f.id === fileId);
    if (!file) return;

    // Atualizar status
    setFiles(prev => prev.map(f => 
      f.id === fileId ? { ...f, status: 'processing' } : f
    ));

    try {
      // Simular processamento
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Resultado simulado
      const result = {
        fileId,
        processedLines: file.lines.length,
        keywords: file.lines,
        timestamp: new Date(),
      };

      // Atualizar status
      setFiles(prev => prev.map(f => 
        f.id === fileId ? { ...f, status: 'success' } : f
      ));

      // Callback
      onFileProcessed(fileId, result);
      setSuccess(`Arquivo "${file.name}" processado com sucesso!`);

    } catch (err) {
      setFiles(prev => prev.map(f => 
        f.id === fileId ? { ...f, status: 'error', error: (err as Error).message } : f
      ));
      setError(`Erro ao processar arquivo "${file.name}": ${(err as Error).message}`);
    }
  };

  const handleProcessAllFiles = () => {
    files.forEach(file => {
      if (file.status === 'success') {
        handleProcessFile(file.id);
      }
    });
  };

  const handleDownloadFile = (file: UploadedFile) => {
    const blob = new Blob([file.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = file.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
        return <InfoIcon color="info" />;
      case 'success':
        return <SuccessIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'processing':
        return <WarningIcon color="warning" />;
      default:
        return <InfoIcon />;
    }
  };

  const getStatusColor = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
        return 'info';
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'processing':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      {/* Área de Upload */}
      <UploadArea
        ref={dropZoneRef}
        isDragOver={isDragOver}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragOver ? 'Solte os arquivos aqui' : 'Arraste arquivos ou clique para selecionar'}
        </Typography>
        <Typography variant="body2" color="textSecondary" gutterBottom>
          Tipos suportados: {allowedTypes.join(', ')}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Tamanho máximo: {formatFileSize(maxFileSize)} | Máximo: {maxFiles} arquivos
        </Typography>
        
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={allowedTypes.join(',')}
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />
      </UploadArea>

      {/* Botões de Ação */}
      {files.length > 0 && (
        <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            onClick={handleProcessAllFiles}
            disabled={uploading || files.every(f => f.status !== 'success')}
          >
            Processar Todos
          </Button>
          <Button
            variant="outlined"
            onClick={() => setFiles([])}
            disabled={uploading}
          >
            Limpar Todos
          </Button>
        </Box>
      )}

      {/* Lista de Arquivos */}
      {files.length > 0 && (
        <FileListContainer>
          <Typography variant="h6" gutterBottom>
            Arquivos ({files.length}/{maxFiles})
          </Typography>
          
          {files.map((file) => (
            <FileItem key={file.id}>
              <CardContent>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} sm={6}>
                    <Box display="flex" alignItems="center" gap={1}>
                      {getStatusIcon(file.status)}
                      <Box>
                        <Typography variant="subtitle1" noWrap>
                          {file.name}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {formatFileSize(file.size)} • {file.lines.length} linhas
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={3}>
                    <Chip
                      label={file.status}
                      color={getStatusColor(file.status) as any}
                      size="small"
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={3}>
                    <Box display="flex" gap={1} justifyContent="flex-end">
                      {showPreview && (
                        <Tooltip title="Visualizar">
                          <IconButton
                            size="small"
                            onClick={() => handlePreviewFile(file)}
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                      
                      <Tooltip title="Download">
                        <IconButton
                          size="small"
                          onClick={() => handleDownloadFile(file)}
                        >
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                      
                      {file.status === 'success' && (
                        <Tooltip title="Processar">
                          <IconButton
                            size="small"
                            onClick={() => handleProcessFile(file.id)}
                            disabled={file.status === 'processing'}
                          >
                            <UploadIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                      
                      <Tooltip title="Remover">
                        <IconButton
                          size="small"
                          onClick={() => handleRemoveFile(file.id)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Grid>
                </Grid>
                
                {/* Progress Bar */}
                {file.status === 'uploading' && (
                  <ProgressContainer>
                    <LinearProgress variant="determinate" value={file.progress} />
                    <Typography variant="caption" color="textSecondary">
                      {file.progress}% concluído
                    </Typography>
                  </ProgressContainer>
                )}
                
                {/* Error Message */}
                {file.error && (
                  <Alert severity="error" sx={{ mt: 1 }}>
                    {file.error}
                  </Alert>
                )}
              </CardContent>
            </FileItem>
          ))}
        </FileListContainer>
      )}

      {/* Dialog de Preview */}
      <Dialog
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Visualizar: {previewFile?.name}
        </DialogTitle>
        <DialogContent>
          {previewFile && (
            <Box>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                {previewFile.lines.length} linhas • {formatFileSize(previewFile.size)}
              </Typography>
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  maxHeight: '400px',
                  overflowY: 'auto',
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                  backgroundColor: 'grey.50'
                }}
              >
                {previewFile.lines.map((line, index) => (
                  <Box key={index} component="span" display="block">
                    {line}
                  </Box>
                ))}
              </Paper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewOpen(false)}>
            Fechar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbars */}
      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess(null)}
      >
        <Alert severity="success" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      </Snackbar>
      
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default FileUpload; 
/**
 * FileUpload - Componente de upload de arquivos com drag & drop e validação
 * 
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 2.2.2
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { useState, useRef, useCallback, useMemo } from 'react';
import {
  Box,
  Typography,
  Button,
  LinearProgress,
  Card,
  CardContent,
  IconButton,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Paper,
  Grid,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  CloudUpload,
  Delete,
  Visibility,
  CheckCircle,
  Error,
  Warning,
  Info,
  FileCopy,
  Image,
  Description,
  TableChart,
  Archive,
  Close,
  Add,
  Download
} from '@mui/icons-material';

interface FileInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  lastModified: number;
  status: 'pending' | 'uploading' | 'success' | 'error' | 'validating';
  progress: number;
  error?: string;
  preview?: string;
  url?: string;
}

interface FileUploadProps {
  title?: string;
  description?: string;
  acceptedTypes?: string[];
  maxFiles?: number;
  maxFileSize?: number; // in bytes
  onUpload?: (files: File[]) => Promise<void>;
  onFileRemove?: (fileId: string) => void;
  onFilePreview?: (file: FileInfo) => void;
  showPreview?: boolean;
  multiple?: boolean;
  disabled?: boolean;
  autoUpload?: boolean;
  uploadUrl?: string;
  headers?: Record<string, string>;
}

const FileUpload: React.FC<FileUploadProps> = ({
  title = 'Upload de Arquivos',
  description = 'Arraste e solte arquivos aqui ou clique para selecionar',
  acceptedTypes = ['*/*'],
  maxFiles = 10,
  maxFileSize = 10 * 1024 * 1024, // 10MB
  onUpload,
  onFileRemove,
  onFilePreview,
  showPreview = true,
  multiple = true,
  disabled = false,
  autoUpload = true,
  uploadUrl,
  headers = {}
}) => {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [showPreviewDialog, setShowPreviewDialog] = useState(false);
  const [previewFile, setPreviewFile] = useState<FileInfo | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // File type validation
  const isValidFileType = useCallback((file: File): boolean => {
    if (acceptedTypes.includes('*/*')) return true;
    
    return acceptedTypes.some(type => {
      if (type.endsWith('/*')) {
        const baseType = type.replace('/*', '');
        return file.type.startsWith(baseType);
      }
      return file.type === type;
    });
  }, [acceptedTypes]);

  // File size validation
  const isValidFileSize = useCallback((file: File): boolean => {
    return file.size <= maxFileSize;
  }, [maxFileSize]);

  // Format file size
  const formatFileSize = useCallback((bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }, []);

  // Get file icon based on type
  const getFileIcon = useCallback((fileType: string) => {
    if (fileType.startsWith('image/')) return <Image />;
    if (fileType.includes('pdf') || fileType.includes('document')) return <Description />;
    if (fileType.includes('spreadsheet') || fileType.includes('excel') || fileType.includes('csv')) return <TableChart />;
    if (fileType.includes('zip') || fileType.includes('rar') || fileType.includes('tar')) return <Archive />;
    return <Description />;
  }, []);

  // Handle file selection
  const handleFileSelect = useCallback((selectedFiles: FileList | null) => {
    if (!selectedFiles) return;

    const newFiles: FileInfo[] = Array.from(selectedFiles).map(file => ({
      id: `${Date.now()}-${Math.random()}`,
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified,
      status: 'pending' as const,
      progress: 0
    }));

    // Validate files
    const validFiles: FileInfo[] = [];
    const invalidFiles: string[] = [];

    newFiles.forEach(file => {
      const originalFile = selectedFiles[Array.from(selectedFiles).findIndex(f => f.name === file.name)];
      
      if (!isValidFileType(originalFile)) {
        invalidFiles.push(`${file.name} - Tipo de arquivo não suportado`);
        return;
      }
      
      if (!isValidFileSize(originalFile)) {
        invalidFiles.push(`${file.name} - Arquivo muito grande (máx: ${formatFileSize(maxFileSize)})`);
        return;
      }

      validFiles.push(file);
    });

    // Check max files limit
    if (files.length + validFiles.length > maxFiles) {
      invalidFiles.push(`Máximo de ${maxFiles} arquivos permitidos`);
    }

    if (invalidFiles.length > 0) {
      alert(`Arquivos inválidos:\n${invalidFiles.join('\n')}`);
    }

    if (validFiles.length > 0) {
      setFiles(prev => [...prev, ...validFiles]);
      
      if (autoUpload) {
        handleUpload(validFiles);
      }
    }
  }, [files.length, maxFiles, isValidFileType, isValidFileSize, formatFileSize, maxFileSize, autoUpload]);

  // Handle drag and drop
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (disabled) return;
    
    const droppedFiles = e.dataTransfer.files;
    handleFileSelect(droppedFiles);
  }, [disabled, handleFileSelect]);

  // Handle file upload
  const handleUpload = useCallback(async (filesToUpload: FileInfo[]) => {
    if (!onUpload && !uploadUrl) return;

    setIsUploading(true);

    try {
      if (onUpload) {
        // Use custom upload function
        const fileObjects = filesToUpload.map(f => {
          // Find the original File object
          const fileInput = fileInputRef.current;
          if (fileInput?.files) {
            return Array.from(fileInput.files).find(file => file.name === f.name);
          }
          return null;
        }).filter(Boolean) as File[];

        await onUpload(fileObjects);
      } else if (uploadUrl) {
        // Use default upload to URL
        for (const fileInfo of filesToUpload) {
          const fileInput = fileInputRef.current;
          if (!fileInput?.files) continue;

          const file = Array.from(fileInput.files).find(f => f.name === fileInfo.name);
          if (!file) continue;

          // Update status to uploading
          setFiles(prev => prev.map(f => 
            f.id === fileInfo.id ? { ...f, status: 'uploading' } : f
          ));

          const formData = new FormData();
          formData.append('file', file);

          const xhr = new XMLHttpRequest();
          
          xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
              const progress = (e.loaded / e.total) * 100;
              setFiles(prev => prev.map(f => 
                f.id === fileInfo.id ? { ...f, progress } : f
              ));
            }
          });

          xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
              setFiles(prev => prev.map(f => 
                f.id === fileInfo.id ? { ...f, status: 'success', progress: 100 } : f
              ));
            } else {
              setFiles(prev => prev.map(f => 
                f.id === fileInfo.id ? { ...f, status: 'error', error: 'Erro no upload' } : f
              ));
            }
          });

          xhr.addEventListener('error', () => {
            setFiles(prev => prev.map(f => 
              f.id === fileInfo.id ? { ...f, status: 'error', error: 'Erro de conexão' } : f
            ));
          });

          xhr.open('POST', uploadUrl);
          
          // Add headers
          Object.entries(headers).forEach(([key, value]) => {
            xhr.setRequestHeader(key, value);
          });

          xhr.send(formData);
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
      setFiles(prev => prev.map(f => 
        filesToUpload.some(uploadFile => uploadFile.id === f.id) 
          ? { ...f, status: 'error', error: 'Erro no upload' }
          : f
      ));
    } finally {
      setIsUploading(false);
    }
  }, [onUpload, uploadUrl, headers]);

  // Handle file removal
  const handleFileRemove = useCallback((fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
    onFileRemove?.(fileId);
  }, [onFileRemove]);

  // Handle file preview
  const handleFilePreview = useCallback((file: FileInfo) => {
    setPreviewFile(file);
    setShowPreviewDialog(true);
    onFilePreview?.(file);
  }, [onFilePreview]);

  // Get status icon
  const getStatusIcon = useCallback((status: FileInfo['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle color="success" />;
      case 'error':
        return <Error color="error" />;
      case 'uploading':
        return <CircularProgress size={16} />;
      case 'validating':
        return <Info color="info" />;
      default:
        return <Info color="action" />;
    }
  }, []);

  // Get status color
  const getStatusColor = useCallback((status: FileInfo['status']) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'uploading':
        return 'primary';
      case 'validating':
        return 'info';
      default:
        return 'default';
    }
  }, []);

  return (
    <Box>
      {/* Upload Area */}
      <Card 
        sx={{ 
          border: 2,
          borderColor: isDragOver ? 'primary.main' : 'divider',
          borderStyle: 'dashed',
          backgroundColor: isDragOver ? 'action.hover' : 'background.paper',
          transition: 'all 0.3s ease',
          cursor: disabled ? 'not-allowed' : 'pointer'
        }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
      >
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={2}>
            {description}
          </Typography>
          
          <Box display="flex" gap={1} justifyContent="center" flexWrap="wrap">
            {acceptedTypes.map((type, index) => (
              <Chip key={index} label={type} size="small" variant="outlined" />
            ))}
          </Box>
          
          <Typography variant="caption" color="text.secondary" display="block" mt={1}>
            Máximo: {maxFiles} arquivos, {formatFileSize(maxFileSize)} cada
          </Typography>

          <input
            ref={fileInputRef}
            type="file"
            multiple={multiple}
            accept={acceptedTypes.join(',')}
            style={{ display: 'none' }}
            onChange={(e) => handleFileSelect(e.target.files)}
            disabled={disabled}
          />
        </CardContent>
      </Card>

      {/* File List */}
      {files.length > 0 && (
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Arquivos ({files.length})
          </Typography>
          
          <List>
            {files.map((file) => (
              <ListItem key={file.id} divider>
                <Box display="flex" alignItems="center" gap={2} flex={1}>
                  {getFileIcon(file.type)}
                  
                  <Box flex={1}>
                    <ListItemText
                      primary={file.name}
                      secondary={`${formatFileSize(file.size)} • ${new Date(file.lastModified).toLocaleDateString()}`}
                    />
                    
                    {file.status === 'uploading' && (
                      <LinearProgress 
                        variant="determinate" 
                        value={file.progress} 
                        sx={{ mt: 1 }}
                      />
                    )}
                    
                    {file.error && (
                      <Alert severity="error" sx={{ mt: 1 }}>
                        {file.error}
                      </Alert>
                    )}
                  </Box>
                </Box>

                <ListItemSecondaryAction>
                  <Box display="flex" gap={1}>
                    {showPreview && file.status === 'success' && (
                      <Tooltip title="Visualizar">
                        <IconButton 
                          size="small" 
                          onClick={() => handleFilePreview(file)}
                        >
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                    )}
                    
                    <Tooltip title="Remover">
                      <IconButton 
                        size="small" 
                        color="error"
                        onClick={() => handleFileRemove(file.id)}
                        disabled={file.status === 'uploading'}
                      >
                        <Delete />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>

          {/* Upload Actions */}
          {!autoUpload && (
            <Box display="flex" gap={2} mt={2}>
              <Button
                variant="contained"
                onClick={() => handleUpload(files.filter(f => f.status === 'pending'))}
                disabled={isUploading || files.filter(f => f.status === 'pending').length === 0}
                startIcon={isUploading ? <CircularProgress size={16} /> : <CloudUpload />}
              >
                {isUploading ? 'Enviando...' : 'Enviar Todos'}
              </Button>
              
              <Button
                variant="outlined"
                onClick={() => setFiles([])}
                disabled={isUploading}
              >
                Limpar Todos
              </Button>
            </Box>
          )}
        </Box>
      )}

      {/* Preview Dialog */}
      <Dialog
        open={showPreviewDialog}
        onClose={() => setShowPreviewDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Visualizar: {previewFile?.name}
            </Typography>
            <IconButton onClick={() => setShowPreviewDialog(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {previewFile && (
            <Box>
              {previewFile.type.startsWith('image/') ? (
                <img 
                  src={previewFile.url || URL.createObjectURL(new Blob())} 
                  alt={previewFile.name}
                  style={{ maxWidth: '100%', height: 'auto' }}
                />
              ) : (
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Description sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    {previewFile.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {formatFileSize(previewFile.size)}
                  </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<Download />}
                    sx={{ mt: 2 }}
                    onClick={() => {
                      if (previewFile.url) {
                        window.open(previewFile.url, '_blank');
                      }
                    }}
                  >
                    Download
                  </Button>
                </Paper>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPreviewDialog(false)}>
            Fechar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FileUpload; 
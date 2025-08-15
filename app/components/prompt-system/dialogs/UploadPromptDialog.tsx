/**
 * Diálogo para Upload de Prompt Base
 * 
 * Componente para upload de arquivos TXT de prompts base
 * 
 * Tracing ID: FIXTYPE-001_COMPONENT_UPDATE_20241227_007
 * Data: 2024-12-27
 */

import React, { useState, useRef } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Paper
} from '@mui/material';
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import { Nicho, Categoria } from '../../../types/api-sync';

interface UploadPromptDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (categoriaId: string, file: File) => Promise<void>;
  nichos: Nicho[];
  categorias: Categoria[];
  selectedCategoriaId?: string;
}

export const UploadPromptDialog: React.FC<UploadPromptDialogProps> = ({
  open,
  onClose,
  onSubmit,
  nichos,
  categorias,
  selectedCategoriaId
}) => {
  const [selectedCategoria, setSelectedCategoria] = useState<string>(selectedCategoriaId || '');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string>('');
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validar tipo de arquivo
    if (!file.name.endsWith('.txt')) {
      setError('Apenas arquivos .txt são permitidos');
      return;
    }

    // Validar tamanho (máximo 1MB)
    if (file.size > 1024 * 1024) {
      setError('Arquivo muito grande. Máximo 1MB permitido');
      return;
    }

    setSelectedFile(file);
    setError(null);

    // Preview do conteúdo
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setPreview(content.substring(0, 500) + (content.length > 500 ? '...' : ''));
    };
    reader.readAsText(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedCategoria) {
      setError('Selecione uma categoria');
      return;
    }

    if (!selectedFile) {
      setError('Selecione um arquivo');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await onSubmit(selectedCategoria, selectedFile);
      handleClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao fazer upload');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSelectedCategoria(selectedCategoriaId || '');
    setSelectedFile(null);
    setPreview('');
    setError(null);
    setLoading(false);
    onClose();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      const event = { target: { files: [file] } } as React.ChangeEvent<HTMLInputElement>;
      handleFileSelect(event);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Upload de Prompt Base</DialogTitle>
        
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
            {error && (
              <Alert severity="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            )}
            
            <FormControl fullWidth required disabled={loading}>
              <InputLabel>Categoria</InputLabel>
              <Select
                value={selectedCategoria}
                onChange={(e) => setSelectedCategoria(e.target.value as string)}
                label="Categoria"
              >
                {categorias.map((categoria) => (
                  <MenuItem key={categoria.id} value={categoria.id}>
                    {categoria.nome} ({categoria.nicho?.nome})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Selecione o arquivo TXT do prompt base
              </Typography>
              
              <Paper
                sx={{
                  border: '2px dashed #ccc',
                  borderRadius: 2,
                  p: 3,
                  textAlign: 'center',
                  cursor: 'pointer',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'action.hover'
                  }
                }}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => fileInputRef.current?.click()}
              >
                <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                
                <Typography variant="body1" gutterBottom>
                  {selectedFile ? selectedFile.name : 'Arraste e solte um arquivo .txt aqui'}
                </Typography>
                
                <Typography variant="body2" color="text.secondary">
                  ou clique para selecionar
                </Typography>
                
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                  Máximo 1MB • Apenas arquivos .txt
                </Typography>
              </Paper>
              
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt"
                style={{ display: 'none' }}
                onChange={handleFileSelect}
              />
            </Box>
            
            {preview && (
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Preview do Conteúdo
                </Typography>
                <Paper sx={{ p: 2, backgroundColor: 'grey.50', maxHeight: 200, overflow: 'auto' }}>
                  <Typography variant="body2" component="pre" sx={{ 
                    fontFamily: 'monospace', 
                    whiteSpace: 'pre-wrap',
                    margin: 0
                  }}>
                    {preview}
                  </Typography>
                </Paper>
              </Box>
            )}
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading || !selectedCategoria || !selectedFile}
            startIcon={loading ? <CircularProgress size={16} /> : null}
          >
            {loading ? 'Fazendo Upload...' : 'Fazer Upload'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}; 
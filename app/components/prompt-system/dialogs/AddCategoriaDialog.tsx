/**
 * Diálogo para Adicionar Categoria
 * 
 * Componente para criação de novas categorias vinculadas a nichos
 * 
 * Tracing ID: FIXTYPE-001_COMPONENT_UPDATE_20241227_006
 * Data: 2024-12-27
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { CategoriaCreate, Nicho } from '../../../types/api-sync';

interface AddCategoriaDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: CategoriaCreate) => Promise<void>;
  nichos: Nicho[];
  selectedNichoId?: string;
}

export const AddCategoriaDialog: React.FC<AddCategoriaDialogProps> = ({
  open,
  onClose,
  onSubmit,
  nichos,
  selectedNichoId
}) => {
  const [formData, setFormData] = useState<CategoriaCreate>({
    nicho_id: selectedNichoId || '',
    nome: '',
    descricao: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.nome.trim()) {
      setError('Nome da categoria é obrigatório');
      return;
    }

    if (!formData.nicho_id) {
      setError('Selecione um nicho');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await onSubmit(formData);
      handleClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao criar categoria');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({ 
      nicho_id: selectedNichoId || '',
      nome: '', 
      descricao: '' 
    });
    setError(null);
    setLoading(false);
    onClose();
  };

  const handleInputChange = (field: keyof CategoriaCreate) => (
    e: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
    if (error) setError(null);
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Adicionar Nova Categoria</DialogTitle>
        
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            {error && (
              <Alert severity="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            )}
            
            <FormControl fullWidth required disabled={loading}>
              <InputLabel>Nicho</InputLabel>
              <Select
                value={formData.nicho_id}
                onChange={handleInputChange('nicho_id')}
                label="Nicho"
              >
                {nichos.map((nicho) => (
                  <MenuItem key={nicho.id} value={nicho.id}>
                    {nicho.nome}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <TextField
              label="Nome da Categoria"
              value={formData.nome}
              onChange={handleInputChange('nome')}
              fullWidth
              required
              disabled={loading}
              placeholder="Ex: Emagrecimento, Investimentos, Programação"
              helperText="Nome da categoria dentro do nicho selecionado"
            />
            
            <TextField
              label="Descrição"
              value={formData.descricao}
              onChange={handleInputChange('descricao')}
              fullWidth
              multiline
              rows={3}
              disabled={loading}
              placeholder="Descreva o tipo de conteúdo desta categoria"
              helperText="Descrição opcional para melhor organização"
            />
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading || !formData.nome.trim() || !formData.nicho_id}
            startIcon={loading ? <CircularProgress size={16} /> : null}
          >
            {loading ? 'Criando...' : 'Criar Categoria'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}; 
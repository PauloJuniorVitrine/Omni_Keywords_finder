/**
 * Diálogo para Adicionar Nicho
 * 
 * Componente para criação de novos nichos no sistema de preenchimento de lacunas
 * 
 * Tracing ID: FIXTYPE-001_COMPONENT_UPDATE_20241227_005
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
  CircularProgress
} from '@mui/material';
import { NichoCreate } from '../../../types/api-sync';

interface AddNichoDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: NichoCreate) => Promise<void>;
}

export const AddNichoDialog: React.FC<AddNichoDialogProps> = ({
  open,
  onClose,
  onSubmit
}) => {
  const [formData, setFormData] = useState<NichoCreate>({
    nome: '',
    descricao: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.nome.trim()) {
      setError('Nome do nicho é obrigatório');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await onSubmit(formData);
      handleClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao criar nicho');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({ nome: '', descricao: '' });
    setError(null);
    setLoading(false);
    onClose();
  };

  const handleInputChange = (field: keyof NichoCreate) => (
    e: React.ChangeEvent<HTMLInputElement>
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
        <DialogTitle>Adicionar Novo Nicho</DialogTitle>
        
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            {error && (
              <Alert severity="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            )}
            
            <TextField
              label="Nome do Nicho"
              value={formData.nome}
              onChange={handleInputChange('nome')}
              fullWidth
              required
              disabled={loading}
              placeholder="Ex: Saúde, Finanças, Tecnologia"
              helperText="Nome único para identificar o nicho"
            />
            
            <TextField
              label="Descrição"
              value={formData.descricao}
              onChange={handleInputChange('descricao')}
              fullWidth
              multiline
              rows={3}
              disabled={loading}
              placeholder="Descreva brevemente o nicho e suas características"
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
            disabled={loading || !formData.nome.trim()}
            startIcon={loading ? <CircularProgress size={16} /> : null}
          >
            {loading ? 'Criando...' : 'Criar Nicho'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}; 
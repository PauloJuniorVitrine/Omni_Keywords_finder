/**
 * Card de Prompt Base
 * 
 * Componente para exibir informações de prompts base
 * 
 * Tracing ID: FIXTYPE-001_COMPONENT_UPDATE_20241227_004
 * Data: 2024-12-27
 */

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
  IconButton,
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Visibility as VisibilityIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { PromptBase } from '../../types/api-sync';

interface PromptCardProps {
  prompt: PromptBase;
  onView?: (prompt: PromptBase) => void;
  onDownload?: (prompt: PromptBase) => void;
  onEdit?: (prompt: PromptBase) => void;
  onDelete?: (prompt: PromptBase) => void;
}

export const PromptCard: React.FC<PromptCardProps> = ({
  prompt,
  onView,
  onDownload,
  onEdit,
  onDelete
}) => {
  const [expanded, setExpanded] = useState(false);
  const [previewOpen, setPreviewOpen] = useState(false);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const handlePreview = () => {
    setPreviewOpen(true);
  };

  const handleClosePreview = () => {
    setPreviewOpen(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getLacunasCount = () => {
    const lacunas = [
      { pattern: '[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]', count: 0 },
      { pattern: '[PALAVRAS-CHAVE SECUNDÁRIAS]', count: 0 },
      { pattern: '[CLUSTER DE CONTEÚDO]', count: 0 }
    ];

    lacunas.forEach(lacuna => {
      const regex = new RegExp(lacuna.pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
      const matches = prompt.conteudo.match(regex);
      lacuna.count = matches ? matches.length : 0;
    });

    return lacunas;
  };

  const lacunas = getLacunasCount();
  const totalLacunas = lacunas.reduce((sum, lacuna) => sum + lacuna.count, 0);

  return (
    <>
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box>
              <Typography variant="h6" component="h3" gutterBottom>
                {prompt.nome_arquivo}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Categoria: {prompt.categoria?.nome}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Criado em: {formatDate(prompt.created_at)}
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip 
                label={`${totalLacunas} lacunas`} 
                color={totalLacunas > 0 ? 'primary' : 'default'}
                size="small"
              />
              <Chip 
                label={`${prompt.conteudo.length} chars`} 
                variant="outlined" 
                size="small"
              />
            </Box>
          </Box>

          <Collapse in={expanded} timeout="auto" unmountOnExit>
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Lacunas Detectadas:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                {lacunas.map((lacuna, index) => (
                  <Chip
                    key={index}
                    label={`${lacuna.pattern.replace(/[\[\]]/g, '')}: ${lacuna.count}`}
                    color={lacuna.count > 0 ? 'secondary' : 'default'}
                    size="small"
                    variant={lacuna.count > 0 ? 'filled' : 'outlined'}
                  />
                ))}
              </Box>
              
              <Typography variant="subtitle2" gutterBottom>
                Preview do Conteúdo:
              </Typography>
              <Paper sx={{ p: 2, backgroundColor: 'grey.50', maxHeight: 150, overflow: 'auto' }}>
                <Typography variant="body2" component="pre" sx={{ 
                  fontFamily: 'monospace', 
                  whiteSpace: 'pre-wrap',
                  margin: 0,
                  fontSize: '0.875rem'
                }}>
                  {prompt.conteudo.substring(0, 300)}
                  {prompt.conteudo.length > 300 && '...'}
                </Typography>
              </Paper>
            </Box>
          </Collapse>
        </CardContent>

        <CardActions sx={{ justifyContent: 'space-between' }}>
          <Box>
            <Button
              size="small"
              startIcon={<VisibilityIcon />}
              onClick={handlePreview}
            >
              Visualizar
            </Button>
            {onDownload && (
              <Button
                size="small"
                startIcon={<DownloadIcon />}
                onClick={() => onDownload(prompt)}
              >
                Download
              </Button>
            )}
          </Box>
          
          <Box>
            {onEdit && (
              <IconButton size="small" onClick={() => onEdit(prompt)}>
                <EditIcon />
              </IconButton>
            )}
            {onDelete && (
              <IconButton size="small" onClick={() => onDelete(prompt)}>
                <DeleteIcon />
              </IconButton>
            )}
            <IconButton
              size="small"
              onClick={handleExpandClick}
              sx={{
                transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.3s'
              }}
            >
              <ExpandMoreIcon />
            </IconButton>
          </Box>
        </CardActions>
      </Card>

      {/* Dialog de Preview Completo */}
      <Dialog 
        open={previewOpen} 
        onClose={handleClosePreview} 
        maxWidth="lg" 
        fullWidth
      >
        <DialogTitle>
          Preview: {prompt.nome_arquivo}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              Informações:
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Categoria:</strong> {prompt.categoria?.nome}
              </Typography>
              <Typography variant="body2">
                <strong>Nicho:</strong> {prompt.categoria?.nicho?.nome}
              </Typography>
              <Typography variant="body2">
                <strong>Tamanho:</strong> {prompt.conteudo.length} caracteres
              </Typography>
              <Typography variant="body2">
                <strong>Lacunas:</strong> {totalLacunas} encontradas
              </Typography>
            </Box>
            
            <Typography variant="subtitle2" gutterBottom>
              Conteúdo Completo:
            </Typography>
            <Paper sx={{ p: 2, backgroundColor: 'grey.50', maxHeight: 400, overflow: 'auto' }}>
              <Typography variant="body2" component="pre" sx={{ 
                fontFamily: 'monospace', 
                whiteSpace: 'pre-wrap',
                margin: 0,
                fontSize: '0.875rem',
                lineHeight: 1.5
              }}>
                {prompt.conteudo}
              </Typography>
            </Paper>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePreview}>Fechar</Button>
          {onDownload && (
            <Button 
              variant="contained" 
              startIcon={<DownloadIcon />}
              onClick={() => {
                onDownload(prompt);
                handleClosePreview();
              }}
            >
              Download
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
}; 
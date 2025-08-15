/**
 * Componente para exibir um nicho em formato de card
 * 
 * Tracing ID: FIXTYPE-001_COMPONENT_UPDATE_20241227_002
 * Data: 2024-12-27
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
  Collapse
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Folder as FolderIcon
} from '@mui/icons-material';
import { Nicho } from '../../types/api-sync';

interface NichoCardProps {
  nicho: Nicho;
  selected: boolean;
  onSelect: (nicho: Nicho) => void;
  onEdit?: (nicho: Nicho) => void;
  onDelete?: (nicho: Nicho) => void;
}

export const NichoCard: React.FC<NichoCardProps> = ({
  nicho,
  selected,
  onSelect,
  onEdit,
  onDelete
}) => {
  const [expanded, setExpanded] = React.useState(false);

  const handleExpandClick = (event: React.MouseEvent) => {
    event.stopPropagation();
    setExpanded(!expanded);
  };

  const handleEdit = (event: React.MouseEvent) => {
    event.stopPropagation();
    onEdit?.(nicho);
  };

  const handleDelete = (event: React.MouseEvent) => {
    event.stopPropagation();
    onDelete?.(nicho);
  };

  return (
    <Card
      sx={{
        mb: 2,
        cursor: 'pointer',
        border: selected ? 2 : 1,
        borderColor: selected ? 'primary.main' : 'divider',
        backgroundColor: selected ? 'primary.50' : 'background.paper',
        '&:hover': {
          backgroundColor: selected ? 'primary.100' : 'action.hover',
          transform: 'translateY(-2px)',
          transition: 'all 0.2s ease-in-out'
        }
      }}
      onClick={() => onSelect(nicho)}
    >
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <FolderIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h3" sx={{ flexGrow: 1 }}>
            {nicho.nome}
          </Typography>
          <Box>
            {onEdit && (
              <Tooltip title="Editar nicho">
                <IconButton size="small" onClick={handleEdit}>
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {onDelete && (
              <Tooltip title="Excluir nicho">
                <IconButton size="small" onClick={handleDelete} color="error">
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            <Tooltip title={expanded ? "Recolher" : "Expandir"}>
              <IconButton
                size="small"
                onClick={handleExpandClick}
                sx={{
                  transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.2s ease-in-out'
                }}
              >
                <ExpandMoreIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {nicho.descricao && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {nicho.descricao}
          </Typography>
        )}

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Chip
            label={`${nicho.categorias?.length || 0} categorias`}
            size="small"
            color="primary"
            variant="outlined"
          />
          <Chip
            label={`${nicho.dadosColetados?.length || 0} dados`}
            size="small"
            color="secondary"
            variant="outlined"
          />
        </Box>

        <Typography variant="caption" color="text.secondary">
          Criado em: {new Date(nicho.created_at).toLocaleDateString('pt-BR')}
        </Typography>

        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>ID:</strong> {nicho.id}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>Atualizado:</strong> {new Date(nicho.updated_at).toLocaleDateString('pt-BR')}
            </Typography>
            
            {nicho.categorias && nicho.categorias.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <strong>Categorias:</strong>
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {nicho.categorias.map((categoria) => (
                    <Chip
                      key={categoria.id}
                      label={categoria.nome}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            )}
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
}; 
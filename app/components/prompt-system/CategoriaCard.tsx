/**
 * Componente para exibir uma categoria em formato de card
 * 
 * Tracing ID: FIXTYPE-001_COMPONENT_UPDATE_20241227_003
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
  Collapse,
  LinearProgress
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Category as CategoryIcon,
  Description as DescriptionIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { Categoria, PromptBase, DadosColetados } from '../../types/api-sync';

interface CategoriaCardProps {
  categoria: Categoria;
  selected: boolean;
  onSelect: (categoria: Categoria) => void;
  onEdit?: (categoria: Categoria) => void;
  onDelete?: (categoria: Categoria) => void;
  promptBase?: PromptBase | null;
  dadosColetados?: DadosColetados[];
}

export const CategoriaCard: React.FC<CategoriaCardProps> = ({
  categoria,
  selected,
  onSelect,
  onEdit,
  onDelete,
  promptBase,
  dadosColetados
}) => {
  const [expanded, setExpanded] = React.useState(false);

  const handleExpandClick = (event: React.MouseEvent) => {
    event.stopPropagation();
    setExpanded(!expanded);
  };

  const handleEdit = (event: React.MouseEvent) => {
    event.stopPropagation();
    onEdit?.(categoria);
  };

  const handleDelete = (event: React.MouseEvent) => {
    event.stopPropagation();
    onDelete?.(categoria);
  };

  // Status indicators
  const hasPromptBase = !!promptBase;
  const hasDadosColetados = dadosColetados && dadosColetados.length > 0;
  const isReady = hasPromptBase && hasDadosColetados;

  const getStatusColor = () => {
    if (isReady) return 'success';
    if (hasPromptBase || hasDadosColetados) return 'warning';
    return 'error';
  };

  const getStatusText = () => {
    if (isReady) return 'Pronto para processar';
    if (hasPromptBase && !hasDadosColetados) return 'Aguardando dados';
    if (!hasPromptBase && hasDadosColetados) return 'Aguardando prompt';
    return 'Incompleto';
  };

  const getStatusIcon = () => {
    if (isReady) return <CheckCircleIcon fontSize="small" />;
    return <WarningIcon fontSize="small" />;
  };

  return (
    <Card
      sx={{
        mb: 2,
        cursor: 'pointer',
        border: selected ? 2 : 1,
        borderColor: selected ? 'secondary.main' : 'divider',
        backgroundColor: selected ? 'secondary.50' : 'background.paper',
        '&:hover': {
          backgroundColor: selected ? 'secondary.100' : 'action.hover',
          transform: 'translateY(-2px)',
          transition: 'all 0.2s ease-in-out'
        }
      }}
      onClick={() => onSelect(categoria)}
    >
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <CategoryIcon sx={{ mr: 1, color: 'secondary.main' }} />
          <Typography variant="h6" component="h3" sx={{ flexGrow: 1 }}>
            {categoria.nome}
          </Typography>
          <Box>
            {onEdit && (
              <Tooltip title="Editar categoria">
                <IconButton size="small" onClick={handleEdit}>
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {onDelete && (
              <Tooltip title="Excluir categoria">
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

        {categoria.descricao && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {categoria.descricao}
          </Typography>
        )}

        {/* Status */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Chip
            icon={getStatusIcon()}
            label={getStatusText()}
            size="small"
            color={getStatusColor()}
            variant="outlined"
          />
        </Box>

        {/* Progress indicators */}
        <Box sx={{ mb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">
              Prompt Base
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {hasPromptBase ? '✓' : '✗'}
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={hasPromptBase ? 100 : 0}
            sx={{ height: 4, borderRadius: 2 }}
          />
        </Box>

        <Box sx={{ mb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">
              Dados Coletados
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {hasDadosColetados ? `${dadosColetados?.length || 0} conjunto(s)` : '✗'}
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={hasDadosColetados ? 100 : 0}
            sx={{ height: 4, borderRadius: 2 }}
          />
        </Box>

        <Typography variant="caption" color="text.secondary">
          Criado em: {new Date(categoria.created_at).toLocaleDateString('pt-BR')}
        </Typography>

        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>ID:</strong> {categoria.id}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>Nicho:</strong> {categoria.nicho?.nome}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>Atualizado:</strong> {new Date(categoria.updated_at).toLocaleDateString('pt-BR')}
            </Typography>
            
            {/* Prompt Base Info */}
            {promptBase && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <strong>Prompt Base:</strong>
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <DescriptionIcon fontSize="small" />
                  <Typography variant="body2" color="text.secondary">
                    {promptBase.nome_arquivo}
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  Hash: {promptBase.hash_conteudo.substring(0, 8)}...
                </Typography>
              </Box>
            )}
            
            {/* Dados Coletados Info */}
            {dadosColetados && dadosColetados.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <strong>Dados Coletados:</strong>
                </Typography>
                {dadosColetados.map((dados, index) => (
                  <Box key={dados.id} sx={{ mb: 0.5 }}>
                    <Typography variant="caption" color="text.secondary">
                      {index + 1}. {dados.primary_keyword}
                    </Typography>
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
}; 
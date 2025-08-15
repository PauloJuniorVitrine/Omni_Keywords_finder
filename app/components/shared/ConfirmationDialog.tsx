/**
 * ConfirmationDialog.tsx
 * 
 * Modal de confirmação reutilizável para ações críticas
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_015
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Modal de confirmação
 * - Diferentes tipos (danger, warning, info)
 * - Customização de mensagens
 * - Integração com ações críticas
 * - Logs de auditoria
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  IconButton,
  Alert,
  Chip,
  Divider,
  useTheme,
  useMediaQuery,
  Tooltip,
  FormControlLabel,
  Checkbox,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Close as CloseIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Edit as EditIcon,
  Archive as ArchiveIcon,
  Restore as RestoreIcon,
  Block as BlockIcon,
  Security as SecurityIcon,
  History as HistoryIcon,
} from '@mui/icons-material';

// Tipos
export type ConfirmationType = 'danger' | 'warning' | 'info' | 'success';

export interface ConfirmationDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: (reason?: string) => void;
  onCancel?: () => void;
  title?: string;
  message?: string;
  type?: ConfirmationType;
  confirmText?: string;
  cancelText?: string;
  requireReason?: boolean;
  reasonLabel?: string;
  reasonPlaceholder?: string;
  reasonRequired?: boolean;
  showAuditLog?: boolean;
  auditLogData?: AuditLogData;
  customIcon?: React.ReactNode;
  customActions?: React.ReactNode;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  fullWidth?: boolean;
  disableBackdropClick?: boolean;
  disableEscapeKeyDown?: boolean;
  loading?: boolean;
  disabled?: boolean;
}

export interface AuditLogData {
  action: string;
  target: string;
  user: string;
  timestamp: Date;
  previousValue?: any;
  newValue?: any;
  metadata?: Record<string, any>;
}

/**
 * Componente de modal de confirmação
 */
const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  open,
  onClose,
  onConfirm,
  onCancel,
  title = 'Confirmar Ação',
  message = 'Tem certeza que deseja executar esta ação?',
  type = 'info',
  confirmText,
  cancelText = 'Cancelar',
  requireReason = false,
  reasonLabel = 'Motivo',
  reasonPlaceholder = 'Digite o motivo da ação...',
  reasonRequired = false,
  showAuditLog = false,
  auditLogData,
  customIcon,
  customActions,
  maxWidth = 'sm',
  fullWidth = true,
  disableBackdropClick = false,
  disableEscapeKeyDown = false,
  loading = false,
  disabled = false,
}) => {
  // Estados
  const [reason, setReason] = useState('');
  const [reasonError, setReasonError] = useState('');
  const [confirmChecked, setConfirmChecked] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Hooks
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Efeitos
  useEffect(() => {
    if (open) {
      setReason('');
      setReasonError('');
      setConfirmChecked(false);
      setShowAdvanced(false);
    }
  }, [open]);

  /**
   * Configuração baseada no tipo
   */
  const getTypeConfig = (type: ConfirmationType) => {
    const configs = {
      danger: {
        color: 'error',
        icon: <ErrorIcon />,
        backgroundColor: theme.palette.error.light,
        confirmButtonColor: 'error',
        defaultConfirmText: 'Excluir',
        defaultTitle: 'Confirmar Exclusão',
      },
      warning: {
        color: 'warning',
        icon: <WarningIcon />,
        backgroundColor: theme.palette.warning.light,
        confirmButtonColor: 'warning',
        defaultConfirmText: 'Continuar',
        defaultTitle: 'Atenção',
      },
      info: {
        color: 'info',
        icon: <InfoIcon />,
        backgroundColor: theme.palette.info.light,
        confirmButtonColor: 'primary',
        defaultConfirmText: 'Confirmar',
        defaultTitle: 'Confirmar Ação',
      },
      success: {
        color: 'success',
        icon: <CheckCircleIcon />,
        backgroundColor: theme.palette.success.light,
        confirmButtonColor: 'success',
        defaultConfirmText: 'Aceitar',
        defaultTitle: 'Confirmação',
      },
    };

    return configs[type];
  };

  const config = getTypeConfig(type);

  /**
   * Manipula confirmação
   */
  const handleConfirm = () => {
    // Validar motivo se necessário
    if (requireReason && reasonRequired && !reason.trim()) {
      setReasonError('Motivo é obrigatório');
      return;
    }

    // Log de auditoria
    if (showAuditLog && auditLogData) {
      logAuditAction({
        ...auditLogData,
        reason: reason.trim() || undefined,
        confirmed: true,
      });
    }

    onConfirm(reason.trim() || undefined);
  };

  /**
   * Manipula cancelamento
   */
  const handleCancel = () => {
    // Log de auditoria
    if (showAuditLog && auditLogData) {
      logAuditAction({
        ...auditLogData,
        reason: reason.trim() || undefined,
        confirmed: false,
      });
    }

    onCancel?.();
    onClose();
  };

  /**
   * Log de ação de auditoria
   */
  const logAuditAction = (auditData: AuditLogData & { reason?: string; confirmed: boolean }) => {
    const logEntry = {
      ...auditData,
      timestamp: new Date(),
      sessionId: generateSessionId(),
      userAgent: navigator.userAgent,
      ipAddress: 'client-side', // Será preenchido pelo backend
    };

    console.log('Audit Log:', logEntry);
    
    // TODO: Enviar para API de auditoria
    // api.post('/audit/logs', logEntry);
  };

  /**
   * Gera ID de sessão
   */
  const generateSessionId = () => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  /**
   * Renderiza ícone baseado na ação
   */
  const renderActionIcon = () => {
    if (customIcon) return customIcon;

    const actionIcons: Record<string, React.ReactNode> = {
      delete: <DeleteIcon />,
      save: <SaveIcon />,
      execute: <PlayIcon />,
      stop: <StopIcon />,
      refresh: <RefreshIcon />,
      download: <DownloadIcon />,
      share: <ShareIcon />,
      edit: <EditIcon />,
      archive: <ArchiveIcon />,
      restore: <RestoreIcon />,
      block: <BlockIcon />,
      security: <SecurityIcon />,
    };

    const action = auditLogData?.action?.toLowerCase();
    return actionIcons[action || ''] || config.icon;
  };

  /**
   * Renderiza dados de auditoria
   */
  const renderAuditData = () => {
    if (!showAuditLog || !auditLogData) return null;

    return (
      <Box sx={{ mt: 2 }}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle2" gutterBottom>
          Detalhes da Ação
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2" color="text.secondary">
              Ação:
            </Typography>
            <Chip
              label={auditLogData.action}
              size="small"
              color="primary"
              variant="outlined"
            />
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2" color="text.secondary">
              Alvo:
            </Typography>
            <Typography variant="body2">
              {auditLogData.target}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2" color="text.secondary">
              Usuário:
            </Typography>
            <Typography variant="body2">
              {auditLogData.user}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2" color="text.secondary">
              Data/Hora:
            </Typography>
            <Typography variant="body2">
              {auditLogData.timestamp.toLocaleString()}
            </Typography>
          </Box>

          {auditLogData.metadata && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Metadados:
              </Typography>
              <Box sx={{ backgroundColor: 'grey.50', p: 1, borderRadius: 1 }}>
                <pre style={{ margin: 0, fontSize: '0.75rem' }}>
                  {JSON.stringify(auditLogData.metadata, null, 2)}
                </pre>
              </Box>
            </Box>
          )}
        </Box>
      </Box>
    );
  };

  /**
   * Renderiza campo de motivo
   */
  const renderReasonField = () => {
    if (!requireReason) return null;

    return (
      <Box sx={{ mt: 2 }}>
        <TextField
          fullWidth
          multiline
          rows={3}
          label={reasonLabel}
          placeholder={reasonPlaceholder}
          value={reason}
          onChange={(e) => {
            setReason(e.target.value);
            if (reasonError) setReasonError('');
          }}
          error={!!reasonError}
          helperText={reasonError}
          required={reasonRequired}
          disabled={loading || disabled}
        />
      </Box>
    );
  };

  /**
   * Renderiza checkbox de confirmação
   */
  const renderConfirmationCheckbox = () => {
    if (type !== 'danger') return null;

    return (
      <Box sx={{ mt: 2 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={confirmChecked}
              onChange={(e) => setConfirmChecked(e.target.checked)}
              disabled={loading || disabled}
            />
          }
          label="Entendo que esta ação não pode ser desfeita"
        />
      </Box>
    );
  };

  /**
   * Renderiza ações customizadas
   */
  const renderCustomActions = () => {
    if (customActions) return customActions;

    const isConfirmDisabled = 
      loading || 
      disabled || 
      (type === 'danger' && !confirmChecked) ||
      (requireReason && reasonRequired && !reason.trim());

    return (
      <>
        <Button
          onClick={handleCancel}
          disabled={loading}
          variant="outlined"
        >
          {cancelText}
        </Button>
        
        <Button
          onClick={handleConfirm}
          disabled={isConfirmDisabled}
          variant="contained"
          color={config.confirmButtonColor as any}
          startIcon={loading ? <RefreshIcon /> : renderActionIcon()}
        >
          {loading ? 'Processando...' : confirmText || config.defaultConfirmText}
        </Button>
      </>
    );
  };

  return (
    <Dialog
      open={open}
      onClose={disableBackdropClick ? undefined : handleCancel}
      maxWidth={maxWidth}
      fullWidth={fullWidth}
      disableEscapeKeyDown={disableEscapeKeyDown}
      PaperProps={{
        sx: {
          borderRadius: 2,
          minWidth: isMobile ? '90vw' : 400,
        }
      }}
    >
      {/* Header */}
      <DialogTitle
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          backgroundColor: config.backgroundColor,
          color: 'white',
          pb: 1,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {renderActionIcon()}
          <Typography variant="h6">
            {title || config.defaultTitle}
          </Typography>
        </Box>
        
        <Box sx={{ flexGrow: 1 }} />
        
        <Tooltip title="Fechar">
          <IconButton
            onClick={handleCancel}
            sx={{ color: 'white' }}
            disabled={loading}
          >
            <CloseIcon />
          </IconButton>
        </Tooltip>
      </DialogTitle>

      {/* Content */}
      <DialogContent sx={{ pt: 3 }}>
        <Typography variant="body1" gutterBottom>
          {message}
        </Typography>

        {renderAuditData()}
        {renderReasonField()}
        {renderConfirmationCheckbox()}

        {/* Alert baseado no tipo */}
        {type === 'danger' && (
          <Alert severity="error" sx={{ mt: 2 }}>
            Esta ação é irreversível e pode afetar outros dados do sistema.
          </Alert>
        )}

        {type === 'warning' && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            Esta ação pode ter consequências importantes. Revise antes de confirmar.
          </Alert>
        )}

        {type === 'info' && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Esta ação será registrada no log de auditoria.
          </Alert>
        )}

        {type === 'success' && (
          <Alert severity="success" sx={{ mt: 2 }}>
            Esta ação será executada com sucesso.
          </Alert>
        )}
      </DialogContent>

      {/* Actions */}
      <DialogActions sx={{ p: 3, pt: 1 }}>
        {renderCustomActions()}
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmationDialog; 
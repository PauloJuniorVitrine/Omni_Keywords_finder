/**
 * ActionConfirm.tsx
 * 
 * Wrapper para ações críticas com confirmação automática
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_016
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Wrapper para ações críticas
 * - Confirmação automática
 * - Logs de auditoria
 * - Rollback visual
 * - Integração com ConfirmationDialog
 */

import React, { useState, useCallback } from 'react';
import {
  Button,
  IconButton,
  Tooltip,
  Snackbar,
  Alert,
  Box,
  Typography,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Undo as UndoIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import ConfirmationDialog, { ConfirmationType, AuditLogData } from './ConfirmationDialog';

// Tipos
export interface ActionConfirmProps {
  children: React.ReactNode;
  onConfirm: () => Promise<void> | void;
  onCancel?: () => void;
  onUndo?: () => Promise<void> | void;
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
  autoConfirm?: boolean;
  autoConfirmDelay?: number;
  showUndo?: boolean;
  undoTimeout?: number;
  disabled?: boolean;
  loading?: boolean;
  variant?: 'button' | 'icon' | 'text';
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  size?: 'small' | 'medium' | 'large';
  fullWidth?: boolean;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  tooltip?: string;
  className?: string;
  sx?: any;
}

export interface ActionState {
  isExecuting: boolean;
  isCompleted: boolean;
  isUndone: boolean;
  error: string | null;
  successMessage: string | null;
  canUndo: boolean;
  undoTimeout: number;
}

/**
 * Componente wrapper para ações críticas
 */
const ActionConfirm: React.FC<ActionConfirmProps> = ({
  children,
  onConfirm,
  onCancel,
  onUndo,
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
  autoConfirm = false,
  autoConfirmDelay = 3000,
  showUndo = false,
  undoTimeout = 30000, // 30 segundos
  disabled = false,
  loading = false,
  variant = 'button',
  color = 'primary',
  size = 'medium',
  fullWidth = false,
  startIcon,
  endIcon,
  tooltip,
  className,
  sx,
}) => {
  // Estados
  const [showDialog, setShowDialog] = useState(false);
  const [actionState, setActionState] = useState<ActionState>({
    isExecuting: false,
    isCompleted: false,
    isUndone: false,
    error: null,
    successMessage: null,
    canUndo: false,
    undoTimeout: undoTimeout,
  });
  const [undoTimer, setUndoTimer] = useState<NodeJS.Timeout | null>(null);

  // Hooks
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  /**
   * Manipula abertura do diálogo
   */
  const handleOpenDialog = useCallback(() => {
    if (disabled || loading) return;
    setShowDialog(true);
  }, [disabled, loading]);

  /**
   * Manipula confirmação da ação
   */
  const handleConfirm = useCallback(async (reason?: string) => {
    setShowDialog(false);
    setActionState(prev => ({
      ...prev,
      isExecuting: true,
      error: null,
      successMessage: null,
    }));

    try {
      // Executar ação
      await onConfirm();

      // Sucesso
      setActionState(prev => ({
        ...prev,
        isExecuting: false,
        isCompleted: true,
        successMessage: 'Ação executada com sucesso!',
        canUndo: showUndo && !!onUndo,
      }));

      // Iniciar timer para desabilitar undo
      if (showUndo && onUndo) {
        const timer = setTimeout(() => {
          setActionState(prev => ({
            ...prev,
            canUndo: false,
          }));
        }, undoTimeout);

        setUndoTimer(timer);
      }

      // Log de auditoria
      if (showAuditLog && auditLogData) {
        logAuditAction({
          ...auditLogData,
          reason,
          confirmed: true,
          executed: true,
        });
      }
    } catch (error) {
      // Erro
      setActionState(prev => ({
        ...prev,
        isExecuting: false,
        error: error instanceof Error ? error.message : 'Erro ao executar ação',
      }));

      // Log de auditoria
      if (showAuditLog && auditLogData) {
        logAuditAction({
          ...auditLogData,
          reason,
          confirmed: true,
          executed: false,
          error: error instanceof Error ? error.message : 'Erro desconhecido',
        });
      }
    }
  }, [onConfirm, showUndo, onUndo, undoTimeout, showAuditLog, auditLogData]);

  /**
   * Manipula cancelamento
   */
  const handleCancel = useCallback(() => {
    setShowDialog(false);
    onCancel?.();

    // Log de auditoria
    if (showAuditLog && auditLogData) {
      logAuditAction({
        ...auditLogData,
        confirmed: false,
        executed: false,
      });
    }
  }, [onCancel, showAuditLog, auditLogData]);

  /**
   * Manipula desfazer ação
   */
  const handleUndo = useCallback(async () => {
    if (!onUndo || !actionState.canUndo) return;

    setActionState(prev => ({
      ...prev,
      isExecuting: true,
      error: null,
    }));

    try {
      await onUndo();

      setActionState(prev => ({
        ...prev,
        isExecuting: false,
        isUndone: true,
        canUndo: false,
        successMessage: 'Ação desfeita com sucesso!',
      }));

      // Limpar timer
      if (undoTimer) {
        clearTimeout(undoTimer);
        setUndoTimer(null);
      }

      // Log de auditoria
      if (showAuditLog && auditLogData) {
        logAuditAction({
          ...auditLogData,
          action: `${auditLogData.action}_UNDO`,
          confirmed: true,
          executed: true,
          metadata: {
            ...auditLogData.metadata,
            undo: true,
            originalAction: auditLogData.action,
          },
        });
      }
    } catch (error) {
      setActionState(prev => ({
        ...prev,
        isExecuting: false,
        error: error instanceof Error ? error.message : 'Erro ao desfazer ação',
      }));
    }
  }, [onUndo, actionState.canUndo, undoTimer, showAuditLog, auditLogData]);

  /**
   * Fecha notificação
   */
  const handleCloseNotification = useCallback(() => {
    setActionState(prev => ({
      ...prev,
      error: null,
      successMessage: null,
    }));
  }, []);

  /**
   * Log de ação de auditoria
   */
  const logAuditAction = (auditData: AuditLogData & {
    reason?: string;
    confirmed: boolean;
    executed: boolean;
    error?: string;
  }) => {
    const logEntry = {
      ...auditData,
      timestamp: new Date(),
      sessionId: generateSessionId(),
      userAgent: navigator.userAgent,
      ipAddress: 'client-side',
    };

    console.log('Action Audit Log:', logEntry);
    
    // TODO: Enviar para API de auditoria
    // api.post('/audit/action-logs', logEntry);
  };

  /**
   * Gera ID de sessão
   */
  const generateSessionId = () => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  /**
   * Renderiza botão baseado no variant
   */
  const renderButton = () => {
    const buttonProps = {
      onClick: handleOpenDialog,
      disabled: disabled || loading || actionState.isExecuting,
      variant: variant === 'button' ? 'contained' : 'text',
      color: color as any,
      size,
      fullWidth,
      startIcon: startIcon,
      endIcon: endIcon,
      className,
      sx,
    };

    if (variant === 'icon') {
      return (
        <IconButton {...buttonProps}>
          {children}
        </IconButton>
      );
    }

    return (
      <Button {...buttonProps}>
        {children}
      </Button>
    );
  };

  /**
   * Renderiza wrapper com tooltip
   */
  const renderWithTooltip = (element: React.ReactNode) => {
    if (!tooltip) return element;

    return (
      <Tooltip title={tooltip}>
        <span>
          {element}
        </span>
      </Tooltip>
    );
  };

  /**
   * Renderiza notificação de sucesso com undo
   */
  const renderSuccessNotification = () => {
    if (!actionState.successMessage) return null;

    return (
      <Snackbar
        open={!!actionState.successMessage}
        autoHideDuration={actionState.canUndo ? null : 6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity="success"
          sx={{ width: '100%' }}
          action={
            actionState.canUndo ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={`Desfazer (${Math.ceil(actionState.undoTimeout / 1000)}s)`}
                  size="small"
                  color="warning"
                  variant="outlined"
                />
                <IconButton
                  size="small"
                  color="warning"
                  onClick={handleUndo}
                  disabled={actionState.isExecuting}
                >
                  <UndoIcon />
                </IconButton>
              </Box>
            ) : undefined
          }
        >
          <Box>
            <Typography variant="body2">
              {actionState.successMessage}
            </Typography>
            {actionState.isUndone && (
              <Typography variant="caption" color="success.main">
                ✓ Ação desfeita
              </Typography>
            )}
          </Box>
        </Alert>
      </Snackbar>
    );
  };

  /**
   * Renderiza notificação de erro
   */
  const renderErrorNotification = () => {
    if (!actionState.error) return null;

    return (
      <Snackbar
        open={!!actionState.error}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity="error"
          sx={{ width: '100%' }}
        >
          {actionState.error}
        </Alert>
      </Snackbar>
    );
  };

  return (
    <>
      {renderWithTooltip(renderButton())}

      {/* Diálogo de confirmação */}
      <ConfirmationDialog
        open={showDialog}
        onClose={() => setShowDialog(false)}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
        title={title}
        message={message}
        type={type}
        confirmText={confirmText}
        cancelText={cancelText}
        requireReason={requireReason}
        reasonLabel={reasonLabel}
        reasonPlaceholder={reasonPlaceholder}
        reasonRequired={reasonRequired}
        showAuditLog={showAuditLog}
        auditLogData={auditLogData}
        loading={actionState.isExecuting}
        disabled={disabled}
      />

      {/* Notificações */}
      {renderSuccessNotification()}
      {renderErrorNotification()}
    </>
  );
};

export default ActionConfirm; 
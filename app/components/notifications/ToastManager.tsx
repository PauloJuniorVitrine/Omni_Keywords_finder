/**
 * ToastManager.tsx
 * 
 * Sistema de toasts avançado com gerenciamento centralizado
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_018
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Sistema de toasts
 * - Posicionamento automático
 * - Auto-dismiss
 * - Ações rápidas
 * - Gerenciamento centralizado
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  Box,
  Typography,
  IconButton,
  Button,
  Chip,
  LinearProgress,
  useTheme,
  useMediaQuery,
  Portal,
  Collapse,
  Slide,
  Grow,
  Fade,
  Zoom,
} from '@mui/material';
import {
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Undo as UndoIcon,
  Redo as RedoIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  AutoAwesome as AutoAwesomeIcon,
  Timer as TimerIcon,
  Pause as PauseIcon,
  PlayArrow as PlayIcon,
} from '@mui/icons-material';

// Tipos
export type ToastType = 'success' | 'error' | 'warning' | 'info';

export type ToastPosition = 
  | 'top-left' 
  | 'top-center' 
  | 'top-right' 
  | 'bottom-left' 
  | 'bottom-center' 
  | 'bottom-right';

export type ToastAnimation = 'slide' | 'grow' | 'fade' | 'zoom';

export interface ToastAction {
  label: string;
  onClick: () => void;
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  variant?: 'text' | 'outlined' | 'contained';
  icon?: React.ReactNode;
}

export interface Toast {
  id: string;
  type: ToastType;
  title?: string;
  message: string;
  position?: ToastPosition;
  duration?: number;
  autoHide?: boolean;
  actions?: ToastAction[];
  onUndo?: () => void;
  onRetry?: () => void;
  metadata?: Record<string, any>;
  timestamp: Date;
  progress?: number;
  paused?: boolean;
  persistent?: boolean;
  animation?: ToastAnimation;
  priority?: number;
}

export interface ToastManagerProps {
  toasts: Toast[];
  onClose: (toastId: string) => void;
  onPause: (toastId: string) => void;
  onResume: (toastId: string) => void;
  onAction: (toastId: string, actionIndex: number) => void;
  maxToasts?: number;
  defaultPosition?: ToastPosition;
  defaultDuration?: number;
  defaultAnimation?: ToastAnimation;
  enableProgress?: boolean;
  enablePause?: boolean;
  enableStacking?: boolean;
  enableSound?: boolean;
  enableVibration?: boolean;
}

/**
 * Componente de gerenciamento de toasts
 */
const ToastManager: React.FC<ToastManagerProps> = ({
  toasts,
  onClose,
  onPause,
  onResume,
  onAction,
  maxToasts = 5,
  defaultPosition = 'bottom-right',
  defaultDuration = 6000,
  defaultAnimation = 'slide',
  enableProgress = true,
  enablePause = true,
  enableStacking = true,
  enableSound = false,
  enableVibration = false,
}) => {
  // Estados
  const [progressStates, setProgressStates] = useState<Record<string, number>>({});
  const [pausedStates, setPausedStates] = useState<Record<string, boolean>>({});
  const [expandedToasts, setExpandedToasts] = useState<Record<string, boolean>>({});

  // Refs
  const progressTimers = useRef<Record<string, NodeJS.Timeout>>({});
  const autoHideTimers = useRef<Record<string, NodeJS.Timeout>>({});

  // Hooks
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Efeitos
  useEffect(() => {
    // Limpar timers ao desmontar
    return () => {
      Object.values(progressTimers.current).forEach(timer => clearInterval(timer));
      Object.values(autoHideTimers.current).forEach(timer => clearTimeout(timer));
    };
  }, []);

  useEffect(() => {
    // Gerenciar toasts ativos
    toasts.forEach(toast => {
      if (!toast.persistent && toast.autoHide !== false) {
        startAutoHideTimer(toast);
      }
      
      if (enableProgress && toast.duration && toast.duration > 0) {
        startProgressTimer(toast);
      }
    });

    return () => {
      // Limpar timers de toasts removidos
      toasts.forEach(toast => {
        if (progressTimers.current[toast.id]) {
          clearInterval(progressTimers.current[toast.id]);
          delete progressTimers.current[toast.id];
        }
        if (autoHideTimers.current[toast.id]) {
          clearTimeout(autoHideTimers.current[toast.id]);
          delete autoHideTimers.current[toast.id];
        }
      });
    };
  }, [toasts, enableProgress]);

  /**
   * Inicia timer de auto-hide
   */
  const startAutoHideTimer = useCallback((toast: Toast) => {
    if (autoHideTimers.current[toast.id]) {
      clearTimeout(autoHideTimers.current[toast.id]);
    }

    const duration = toast.duration || defaultDuration;
    
    autoHideTimers.current[toast.id] = setTimeout(() => {
      if (!pausedStates[toast.id]) {
        onClose(toast.id);
      }
    }, duration);
  }, [defaultDuration, pausedStates, onClose]);

  /**
   * Inicia timer de progresso
   */
  const startProgressTimer = useCallback((toast: Toast) => {
    if (progressTimers.current[toast.id]) {
      clearInterval(progressTimers.current[toast.id]);
    }

    const duration = toast.duration || defaultDuration;
    const interval = 100; // Atualiza a cada 100ms
    const steps = duration / interval;
    let currentStep = 0;

    setProgressStates(prev => ({ ...prev, [toast.id]: 0 }));

    progressTimers.current[toast.id] = setInterval(() => {
      if (pausedStates[toast.id]) return;

      currentStep++;
      const progress = (currentStep / steps) * 100;

      setProgressStates(prev => ({ ...prev, [toast.id]: progress }));

      if (progress >= 100) {
        clearInterval(progressTimers.current[toast.id]);
        delete progressTimers.current[toast.id];
      }
    }, interval);
  }, [defaultDuration, pausedStates]);

  /**
   * Manipula pausa/resume do toast
   */
  const handlePauseResume = useCallback((toast: Toast) => {
    const isPaused = pausedStates[toast.id];
    
    setPausedStates(prev => ({ ...prev, [toast.id]: !isPaused }));
    
    if (isPaused) {
      onResume(toast.id);
    } else {
      onPause(toast.id);
    }
  }, [pausedStates, onPause, onResume]);

  /**
   * Manipula expansão do toast
   */
  const handleToggleExpanded = useCallback((toastId: string) => {
    setExpandedToasts(prev => ({ ...prev, [toastId]: !prev[toastId] }));
  }, []);

  /**
   * Manipula ação do toast
   */
  const handleAction = useCallback((toast: Toast, actionIndex: number) => {
    onAction(toast.id, actionIndex);
  }, [onAction]);

  /**
   * Renderiza ícone baseado no tipo
   */
  const renderTypeIcon = (type: ToastType) => {
    const icons = {
      success: <CheckCircleIcon />,
      error: <ErrorIcon />,
      warning: <WarningIcon />,
      info: <InfoIcon />,
    };
    return icons[type];
  };

  /**
   * Renderiza ações do toast
   */
  const renderActions = (toast: Toast) => {
    const actions: React.ReactNode[] = [];

    // Ação de retry se disponível
    if (toast.onRetry) {
      actions.push(
        <IconButton
          key="retry"
          size="small"
          onClick={toast.onRetry}
          color="inherit"
        >
          <RefreshIcon />
        </IconButton>
      );
    }

    // Ação de undo se disponível
    if (toast.onUndo) {
      actions.push(
        <IconButton
          key="undo"
          size="small"
          onClick={toast.onUndo}
          color="inherit"
        >
          <UndoIcon />
        </IconButton>
      );
    }

    // Ações customizadas
    toast.actions?.forEach((action, index) => {
      actions.push(
        <Button
          key={`action-${index}`}
          size="small"
          variant={action.variant || 'text'}
          color={action.color || 'inherit'}
          onClick={() => handleAction(toast, index)}
          startIcon={action.icon}
          sx={{ minWidth: 'auto', px: 1 }}
        >
          {action.label}
        </Button>
      );
    });

    // Botão de pausa se habilitado
    if (enablePause && toast.duration && toast.duration > 0) {
      actions.push(
        <IconButton
          key="pause"
          size="small"
          onClick={() => handlePauseResume(toast)}
          color="inherit"
        >
          {pausedStates[toast.id] ? <PlayIcon /> : <PauseIcon />}
        </IconButton>
      );
    }

    // Botão de fechar
    actions.push(
      <IconButton
        key="close"
        size="small"
        onClick={() => onClose(toast.id)}
        color="inherit"
      >
        <CloseIcon />
      </IconButton>
    );

    return actions;
  };

  /**
   * Renderiza toast individual
   */
  const renderToast = (toast: Toast) => {
    const isPaused = pausedStates[toast.id];
    const progress = progressStates[toast.id] || 0;
    const isExpanded = expandedToasts[toast.id];

    return (
      <Snackbar
        key={toast.id}
        open={true}
        anchorOrigin={{
          vertical: toast.position?.includes('top') ? 'top' : 'bottom',
          horizontal: toast.position?.includes('left') ? 'left' : 
                     toast.position?.includes('right') ? 'right' : 'center',
        }}
        TransitionComponent={
          toast.animation === 'grow' ? Grow :
          toast.animation === 'fade' ? Fade :
          toast.animation === 'zoom' ? Zoom :
          Slide
        }
        sx={{
          '& .MuiSnackbar-root': {
            maxWidth: isMobile ? '100vw' : 400,
          },
        }}
      >
        <Alert
          severity={toast.type}
          icon={renderTypeIcon(toast.type)}
          action={renderActions(toast)}
          sx={{
            width: '100%',
            maxWidth: isMobile ? 'calc(100vw - 32px)' : 400,
            opacity: isPaused ? 0.7 : 1,
            transition: 'opacity 0.3s ease',
            '& .MuiAlert-message': {
              width: '100%',
            },
          }}
          onMouseEnter={() => {
            if (enablePause && !toast.persistent) {
              setPausedStates(prev => ({ ...prev, [toast.id]: true }));
            }
          }}
          onMouseLeave={() => {
            if (enablePause && !toast.persistent) {
              setPausedStates(prev => ({ ...prev, [toast.id]: false }));
            }
          }}
        >
          <Box sx={{ width: '100%' }}>
            {toast.title && (
              <AlertTitle sx={{ fontWeight: 'bold', mb: 0.5 }}>
                {toast.title}
              </AlertTitle>
            )}
            
            <Typography variant="body2" sx={{ mb: 1 }}>
              {toast.message}
            </Typography>

            {/* Progresso */}
            {enableProgress && toast.duration && toast.duration > 0 && (
              <Box sx={{ width: '100%', mb: 1 }}>
                <LinearProgress
                  variant="determinate"
                  value={progress}
                  sx={{
                    height: 2,
                    borderRadius: 1,
                    backgroundColor: 'rgba(255, 255, 255, 0.3)',
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 1,
                    },
                  }}
                />
              </Box>
            )}

            {/* Metadados expandidos */}
            {toast.metadata && (
              <Collapse in={isExpanded}>
                <Box sx={{ mt: 1, pt: 1, borderTop: 1, borderColor: 'divider' }}>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Detalhes:
                  </Typography>
                  <Box sx={{ backgroundColor: 'rgba(255, 255, 255, 0.1)', p: 1, borderRadius: 1 }}>
                    <pre style={{ margin: 0, fontSize: '0.75rem' }}>
                      {JSON.stringify(toast.metadata, null, 2)}
                    </pre>
                  </Box>
                </Box>
              </Collapse>
            )}

            {/* Footer com timestamp e controles */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 1 }}>
              <Typography variant="caption" color="text.secondary">
                {toast.timestamp.toLocaleTimeString()}
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                {toast.metadata && (
                  <IconButton
                    size="small"
                    onClick={() => handleToggleExpanded(toast.id)}
                    sx={{ p: 0.5 }}
                  >
                    <AutoAwesomeIcon fontSize="small" />
                  </IconButton>
                )}
                
                {isPaused && (
                  <Chip
                    label="Pausado"
                    size="small"
                    icon={<PauseIcon />}
                    variant="outlined"
                    sx={{ height: 20 }}
                  />
                )}
              </Box>
            </Box>
          </Box>
        </Alert>
      </Snackbar>
    );
  };

  /**
   * Agrupa toasts por posição
   */
  const getToastsByPosition = () => {
    const grouped: Record<ToastPosition, Toast[]> = {
      'top-left': [],
      'top-center': [],
      'top-right': [],
      'bottom-left': [],
      'bottom-center': [],
      'bottom-right': [],
    };

    toasts.slice(0, maxToasts).forEach(toast => {
      const position = toast.position || defaultPosition;
      grouped[position].push(toast);
    });

    return grouped;
  };

  const toastsByPosition = getToastsByPosition();

  return (
    <Portal>
      {/* Renderiza toasts para cada posição */}
      {Object.entries(toastsByPosition).map(([position, positionToasts]) => (
        <Box
          key={position}
          sx={{
            position: 'fixed',
            zIndex: theme.zIndex.snackbar,
            ...(position.includes('top') ? { top: 16 } : { bottom: 16 }),
            ...(position.includes('left') ? { left: 16 } : 
                position.includes('right') ? { right: 16 } : { left: '50%', transform: 'translateX(-50%)' }),
            display: 'flex',
            flexDirection: 'column',
            gap: 1,
            maxHeight: 'calc(100vh - 32px)',
            overflow: 'hidden',
            pointerEvents: 'none',
            '& > *': {
              pointerEvents: 'auto',
            },
          }}
        >
          {enableStacking ? (
            // Stacking: toasts empilhados
            positionToasts.map((toast, index) => (
              <Box
                key={toast.id}
                sx={{
                  transform: `translateY(${index * 8}px)`,
                  transition: 'transform 0.3s ease',
                }}
              >
                {renderToast(toast)}
              </Box>
            ))
          ) : (
            // Não-stacking: apenas o toast mais recente
            positionToasts.length > 0 && renderToast(positionToasts[0])
          )}
        </Box>
      ))}
    </Portal>
  );
};

export default ToastManager; 
import React from 'react';

/**
 * Modal de confirmação para ações críticas.
 * @param open Se o modal está aberto
 * @param message Mensagem de confirmação
 * @param confirmLabel Texto do botão de confirmação
 * @param cancelLabel Texto do botão de cancelar
 * @param confirmColor Cor do botão de confirmação
 * @param onConfirm Callback de confirmação
 * @param onCancel Callback de cancelamento
 */
interface ModalConfirmProps {
  open: boolean;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  confirmColor?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
}

const ModalConfirm: React.FC<ModalConfirmProps> = ({
  open,
  message,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  confirmColor = '#22c55e',
  onConfirm,
  onCancel,
}) => {
  if (!open) return null;
  return (
    <div
      role="dialog"
      aria-modal="true"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        background: 'rgba(0,0,0,0.18)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
    >
      <div
        style={{
          background: '#fff',
          borderRadius: 16,
          minWidth: 320,
          minHeight: 120,
          boxShadow: '0 4px 24px rgba(0,0,0,0.10)',
          padding: 32,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <div style={{ fontSize: 20, color: '#222', marginBottom: 24 }}>{message}</div>
        <div style={{ display: 'flex', gap: 16 }}>
          <button
            style={{
              background: confirmColor,
              color: '#fff',
              border: 'none',
              borderRadius: 8,
              padding: '10px 28px',
              fontSize: 16,
              fontWeight: 600,
              cursor: 'pointer',
              marginRight: 8,
            }}
            onClick={onConfirm}
            aria-label={confirmLabel}
            autoFocus
          >
            {confirmLabel}
          </button>
          <button
            style={{
              background: '#ef4444',
              color: '#fff',
              border: 'none',
              borderRadius: 8,
              padding: '10px 28px',
              fontSize: 16,
              fontWeight: 600,
              cursor: 'pointer',
            }}
            onClick={onCancel}
            aria-label={cancelLabel}
          >
            {cancelLabel}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModalConfirm; 
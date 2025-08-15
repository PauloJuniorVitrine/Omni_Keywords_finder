import React from 'react';

export interface ConfirmationDialogProps {
  open: boolean;
  title?: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  className?: string;
}

export const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  open,
  title = 'Confirmar ação',
  description,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  onConfirm,
  onCancel,
  className = ''
}) => {
  if (!open) return null;
  return (
    <div className={`confirmation-dialog ${className}`} style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
      <div style={{ background: '#fff', borderRadius: 8, padding: 24, minWidth: 320, boxShadow: '0 2px 16px rgba(0,0,0,0.15)' }}>
        <h2>{title}</h2>
        {description && <p>{description}</p>}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 24 }}>
          <button onClick={onCancel}>{cancelLabel}</button>
          <button onClick={onConfirm} style={{ background: '#1976d2', color: '#fff' }}>{confirmLabel}</button>
        </div>
      </div>
    </div>
  );
}; 
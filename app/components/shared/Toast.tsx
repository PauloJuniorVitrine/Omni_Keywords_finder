import React, { useEffect, useRef } from 'react';

interface ToastProps {
  type: 'success' | 'error';
  message: string;
  onClose: () => void;
}

const colors = {
  success: { bg: '#22c55e', fg: '#fff' },
  error: { bg: '#ef4444', fg: '#fff' },
};

const Toast: React.FC<ToastProps> = ({ type, message, onClose }) => {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    ref.current?.focus();
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div
      ref={ref}
      tabIndex={0}
      role="alert"
      aria-live="assertive"
      style={{
        position: 'fixed',
        bottom: 32,
        right: 32,
        minWidth: 240,
        background: colors[type].bg,
        color: colors[type].fg,
        borderRadius: 8,
        padding: '16px 32px',
        fontWeight: 600,
        fontSize: 16,
        boxShadow: '0 2px 12px rgba(0,0,0,0.12)',
        zIndex: 2000,
        outline: 'none',
        display: 'flex',
        alignItems: 'center',
        gap: 16,
      }}
      onClick={onClose}
      onKeyDown={e => (e.key === 'Escape' ? onClose() : undefined)}
    >
      {type === 'success' ? '✔️' : '❌'}
      <span>{message}</span>
      <button
        aria-label="Fechar aviso"
        onClick={onClose}
        style={{
          background: 'transparent',
          border: 'none',
          color: colors[type].fg,
          fontSize: 20,
          cursor: 'pointer',
          marginLeft: 8,
        }}
      >
        ×
      </button>
    </div>
  );
};

export default Toast; 
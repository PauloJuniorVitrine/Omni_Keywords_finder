import React from 'react';

/**
 * Botão de ação reutilizável com microanimações.
 * @param label Texto do botão
 * @param variant 'primary' | 'secondary'
 * @param disabled Estado desabilitado
 * @param onClick Função de clique
 */
interface ActionButtonProps {
  label: string;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
  onClick?: () => void;
}

const ActionButton: React.FC<ActionButtonProps> = ({ label, variant = 'primary', disabled = false, onClick }) => {
  const colors = {
    primary: { bg: '#4f8cff', fg: '#fff', hover: '#2563eb' },
    secondary: { bg: '#eab308', fg: '#fff', hover: '#ca8a04' },
  };
  const style = {
    background: colors[variant].bg,
    color: colors[variant].fg,
    border: 'none',
    borderRadius: 8,
    padding: '10px 28px',
    fontSize: 16,
    fontWeight: 600,
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    outline: 'none',
    margin: 4,
    boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
    transition: 'background 0.18s, box-shadow 0.18s, transform 0.12s',
    position: 'relative' as const,
  };
  return (
    <button
      style={style}
      disabled={disabled}
      aria-label={label}
      onClick={disabled ? undefined : onClick}
      tabIndex={0}
      onMouseDown={e => e.currentTarget.style.transform = 'scale(0.97)'}
      onMouseUp={e => e.currentTarget.style.transform = 'scale(1)'}
      onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
      onFocus={e => e.currentTarget.style.boxShadow = '0 0 0 3px #a5b4fc'}
      onBlur={e => e.currentTarget.style.boxShadow = '0 1px 4px rgba(0,0,0,0.06)'}
      onMouseOver={e => e.currentTarget.style.background = colors[variant].hover}
      onMouseOut={e => e.currentTarget.style.background = colors[variant].bg}
    >
      {label}
    </button>
  );
};

export default ActionButton; 
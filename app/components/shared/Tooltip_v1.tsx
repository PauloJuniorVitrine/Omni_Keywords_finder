import React, { ReactNode, useState, useRef } from 'react';

/**
 * Tooltip acessível e reutilizável.
 * @param content Conteúdo do tooltip
 * @param children Elemento alvo
 * @param position Posição do tooltip ('top' | 'bottom' | 'left' | 'right')
 * @param delay Delay em ms para exibir/esconder
 */
export interface TooltipProps {
  content: ReactNode;
  children: ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  delay?: number;
}

const Tooltip: React.FC<TooltipProps> = ({ content, children, position = 'top', delay = 200 }) => {
  const [visible, setVisible] = useState(false);
  const timeout = useRef<NodeJS.Timeout | null>(null);

  const show = () => {
    timeout.current = setTimeout(() => setVisible(true), delay);
  };
  const hide = () => {
    if (timeout.current) clearTimeout(timeout.current);
    setVisible(false);
  };

  // Posição dinâmica
  const getPositionStyle = () => {
    switch (position) {
      case 'bottom': return { top: '120%', left: '50%', transform: 'translateX(-50%)' };
      case 'left': return { right: '110%', top: '50%', transform: 'translateY(-50%)' };
      case 'right': return { left: '110%', top: '50%', transform: 'translateY(-50%)' };
      default: return { bottom: '120%', left: '50%', transform: 'translateX(-50%)' };
    }
  };

  return (
    <span style={{ position: 'relative', display: 'inline-block' }}
      onMouseEnter={show} onFocus={show} onMouseLeave={hide} onBlur={hide} tabIndex={0} aria-describedby="tooltip-content">
      {children}
      {visible && (
        <span
          id="tooltip-content"
          role="tooltip"
          style={{
            position: 'absolute',
            zIndex: 1000,
            background: '#222',
            color: '#fff',
            padding: '6px 14px',
            borderRadius: 6,
            fontSize: 14,
            whiteSpace: 'nowrap',
            boxShadow: '0 2px 8px rgba(0,0,0,0.12)',
            opacity: visible ? 1 : 0,
            pointerEvents: 'none',
            transition: 'opacity 0.18s cubic-bezier(.4,0,.2,1)',
            ...getPositionStyle(),
          }}
        >
          {content}
        </span>
      )}
    </span>
  );
};

export default Tooltip; 
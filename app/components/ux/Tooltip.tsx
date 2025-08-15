import React, { useState } from 'react';

export interface TooltipProps {
  content: string;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

export const Tooltip: React.FC<TooltipProps> = ({ content, children, position = 'top', className = '' }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div 
      className={`tooltip-container ${className}`} 
      style={{ position: 'relative', display: 'inline-block' }}
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div 
          className="tooltip-content"
          style={{
            position: 'absolute',
            background: '#333',
            color: '#fff',
            padding: '8px',
            borderRadius: 4,
            fontSize: '12px',
            whiteSpace: 'nowrap',
            zIndex: 1000,
            ...(position === 'top' && { bottom: '100%', left: '50%', transform: 'translateX(-50%)', marginBottom: '4px' }),
            ...(position === 'bottom' && { top: '100%', left: '50%', transform: 'translateX(-50%)', marginTop: '4px' }),
            ...(position === 'left' && { right: '100%', top: '50%', transform: 'translateY(-50%)', marginRight: '4px' }),
            ...(position === 'right' && { left: '100%', top: '50%', transform: 'translateY(-50%)', marginLeft: '4px' })
          }}
        >
          {content}
        </div>
      )}
    </div>
  );
}; 
import React from 'react';

export interface HelpTextProps {
  text: string;
  variant?: 'info' | 'warning' | 'error' | 'success';
  className?: string;
}

export const HelpText: React.FC<HelpTextProps> = ({ text, variant = 'info', className = '' }) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'warning':
        return { color: '#f57c00', backgroundColor: '#fff3e0' };
      case 'error':
        return { color: '#d32f2f', backgroundColor: '#ffebee' };
      case 'success':
        return { color: '#388e3c', backgroundColor: '#e8f5e8' };
      default:
        return { color: '#1976d2', backgroundColor: '#e3f2fd' };
    }
  };

  return (
    <div 
      className={`help-text ${className}`} 
      style={{ 
        padding: '8px 12px', 
        borderRadius: 4, 
        fontSize: '14px',
        ...getVariantStyles()
      }}
    >
      {text}
    </div>
  );
}; 
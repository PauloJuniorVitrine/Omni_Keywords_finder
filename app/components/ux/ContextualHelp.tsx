import React, { useState } from 'react';

export interface ContextualHelpProps {
  title: string;
  content: React.ReactNode;
  trigger?: React.ReactNode;
  className?: string;
}

export const ContextualHelp: React.FC<ContextualHelpProps> = ({ title, content, trigger, className = '' }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={`contextual-help ${className}`} style={{ position: 'relative', display: 'inline-block' }}>
      <div onClick={() => setIsOpen(!isOpen)} style={{ cursor: 'pointer' }}>
        {trigger || <span style={{ fontSize: '16px', color: '#1976d2' }}>?</span>}
      </div>
      {isOpen && (
        <div 
          className="contextual-help-content"
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            background: '#fff',
            border: '1px solid #ccc',
            borderRadius: 8,
            padding: '16px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            zIndex: 1000,
            minWidth: 200,
            maxWidth: 300
          }}
        >
          <h4>{title}</h4>
          <div>{content}</div>
          <button onClick={() => setIsOpen(false)} style={{ marginTop: '8px', padding: '4px 8px' }}>Fechar</button>
        </div>
      )}
    </div>
  );
}; 
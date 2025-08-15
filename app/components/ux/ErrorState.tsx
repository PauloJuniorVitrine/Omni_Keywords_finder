import React from 'react';

export interface ErrorStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({ title = 'Ocorreu um erro', description, icon, action, className = '' }) => {
  return (
    <div className={`error-state ${className}`} style={{ textAlign: 'center', padding: '2rem', color: '#d32f2f' }}>
      {icon || <div className="error-state-icon" style={{ fontSize: '3rem', marginBottom: '1rem' }}>❌</div>}
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      {action && <div className="error-state-action" style={{ marginTop: '1rem' }}>{action}</div>}
    </div>
  );
}; 
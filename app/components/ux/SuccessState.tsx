import React from 'react';

export interface SuccessStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const SuccessState: React.FC<SuccessStateProps> = ({ title = 'Sucesso!', description, icon, action, className = '' }) => {
  return (
    <div className={`success-state ${className}`} style={{ textAlign: 'center', padding: '2rem', color: '#388e3c' }}>
      {icon || <div className="success-state-icon" style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>}
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      {action && <div className="success-state-action" style={{ marginTop: '1rem' }}>{action}</div>}
    </div>
  );
}; 
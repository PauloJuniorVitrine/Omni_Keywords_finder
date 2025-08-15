import React from 'react';

export interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ title = 'Nada aqui ainda', description, icon, action, className = '' }) => {
  return (
    <div className={`empty-state ${className}`} style={{ textAlign: 'center', padding: '2rem' }}>
      {icon && <div className="empty-state-icon" style={{ fontSize: '3rem', marginBottom: '1rem' }}>{icon}</div>}
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      {action && <div className="empty-state-action" style={{ marginTop: '1rem' }}>{action}</div>}
    </div>
  );
}; 
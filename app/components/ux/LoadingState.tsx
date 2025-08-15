import React from 'react';

export interface LoadingStateProps {
  message?: string;
  spinner?: React.ReactNode;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ message = 'Carregando...', spinner, className = '' }) => {
  return (
    <div className={`loading-state ${className}`} style={{ textAlign: 'center', padding: '2rem' }}>
      {spinner || <div className="loading-spinner" style={{ fontSize: '2rem', marginBottom: '1rem' }}>⏳</div>}
      <div>{message}</div>
    </div>
  );
}; 
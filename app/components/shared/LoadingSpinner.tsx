/**
 * LoadingSpinner.tsx
 * 
 * Componente de spinner de carregamento
 * 
 * Tracing ID: LOADING_SPINNER_001_20250127
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 1.1.1
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Spinner animado
 * - Múltiplos tamanhos
 * - Cores customizáveis
 * - Texto opcional
 */

import React from 'react';

interface LoadingSpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'white' | 'gray';
  text?: string;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'primary',
  text,
  className = ''
}) => {
  const sizeClasses = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  const colorClasses = {
    primary: 'text-blue-600',
    secondary: 'text-gray-600',
    white: 'text-white',
    gray: 'text-gray-400'
  };

  const spinnerSize = sizeClasses[size];
  const spinnerColor = colorClasses[color];

  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-current ${spinnerSize} ${spinnerColor}`}></div>
      {text && (
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{text}</p>
      )}
    </div>
  );
};

// Componente de loading para páginas inteiras
export const PageLoader: React.FC<{ text?: string }> = ({ text = 'Carregando...' }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <LoadingSpinner size="lg" text={text} />
    </div>
  );
};

// Componente de loading para botões
export const ButtonLoader: React.FC<{ size?: 'sm' | 'md' }> = ({ size = 'md' }) => {
  const spinnerSize = size === 'sm' ? 'w-4 h-4' : 'w-5 h-5';
  
  return (
    <div className={`animate-spin rounded-full border-2 border-white border-t-transparent ${spinnerSize}`}></div>
  );
};

// Componente de loading para cards
export const CardLoader: React.FC = () => {
  return (
    <div className="animate-pulse">
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
    </div>
  );
};

// Componente de loading para tabelas
export const TableLoader: React.FC<{ rows?: number; columns?: number }> = ({ 
  rows = 5, 
  columns = 4 
}) => {
  return (
    <div className="animate-pulse">
      <div className="grid grid-cols-4 gap-4 mb-4">
        {Array.from({ length: columns }).map((_, index) => (
          <div key={index} className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
        ))}
      </div>
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="grid grid-cols-4 gap-4 mb-2">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <div key={colIndex} className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default LoadingSpinner; 
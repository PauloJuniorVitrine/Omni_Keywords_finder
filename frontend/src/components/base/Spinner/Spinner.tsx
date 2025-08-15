import React, { forwardRef } from 'react';
import { cn } from '../../../utils/cn';

// Tipos específicos para o sistema Omni Keywords Finder
export interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  label?: string;
  thickness?: 'thin' | 'normal' | 'thick';
}

export const Spinner = forwardRef<HTMLDivElement, SpinnerProps>(
  (
    {
      className,
      size = 'md',
      variant = 'default',
      label = 'Carregando...',
      thickness = 'normal',
      ...props
    },
    ref
  ) => {
    // Design tokens específicos do Omni Keywords Finder
    const spinnerSizes = {
      sm: 'w-4 h-4',
      md: 'w-6 h-6',
      lg: 'w-8 h-8',
      xl: 'w-12 h-12'
    };

    const spinnerVariants = {
      default: 'text-gray-400',
      primary: 'text-blue-600',
      secondary: 'text-gray-600',
      success: 'text-green-600',
      warning: 'text-yellow-600',
      danger: 'text-red-600'
    };

    const spinnerThickness = {
      thin: 'stroke-1',
      normal: 'stroke-2',
      thick: 'stroke-3'
    };

    return (
      <div
        ref={ref}
        className={cn('inline-flex items-center', className)}
        role="status"
        aria-label={label}
        {...props}
      >
        <svg
          className={cn(
            'animate-spin',
            spinnerSizes[size],
            spinnerVariants[variant],
            spinnerThickness[thickness]
          )}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        
        {label && (
          <span className="sr-only">{label}</span>
        )}
      </div>
    );
  }
);

Spinner.displayName = 'Spinner';

// Componente de loading com texto
export const LoadingSpinner = ({ 
  text = 'Carregando...', 
  size = 'md',
  variant = 'primary',
  className 
}: {
  text?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  className?: string;
}) => (
  <div className={cn('flex flex-col items-center justify-center space-y-2', className)}>
    <Spinner size={size} variant={variant} />
    {text && (
      <p className="text-sm text-gray-600">{text}</p>
    )}
  </div>
); 
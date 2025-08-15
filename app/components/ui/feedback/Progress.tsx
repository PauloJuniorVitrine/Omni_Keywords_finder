import React from 'react';

export interface ProgressProps {
  value: number;
  max?: number;
  min?: number;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'error';
  showLabel?: boolean;
  labelPosition?: 'top' | 'bottom' | 'left' | 'right';
  animated?: boolean;
  striped?: boolean;
  className?: string;
  'aria-label'?: string;
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  min = 0,
  size = 'md',
  variant = 'default',
  showLabel = false,
  labelPosition = 'top',
  animated = false,
  striped = false,
  className = '',
  'aria-label': ariaLabel
}) => {
  const percentage = Math.min(Math.max(((value - min) / (max - min)) * 100, 0), 100);
  
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };

  const variantClasses = {
    default: 'bg-blue-600',
    success: 'bg-green-600',
    warning: 'bg-yellow-600',
    error: 'bg-red-600'
  };

  const labelSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  const getAnimationClasses = () => {
    const classes = [];
    if (animated) classes.push('transition-all duration-300 ease-out');
    if (striped) classes.push('bg-gradient-to-r from-transparent via-white to-transparent bg-[length:20px_100%] animate-pulse');
    return classes.join(' ');
  };

  const renderLabel = () => {
    if (!showLabel) return null;
    
    const labelContent = `${Math.round(percentage)}%`;
    
    const labelClasses = `font-medium ${labelSizeClasses[size]} text-gray-700`;
    
    switch (labelPosition) {
      case 'top':
        return <div className={`mb-2 ${labelClasses}`}>{labelContent}</div>;
      case 'bottom':
        return <div className={`mt-2 ${labelClasses}`}>{labelContent}</div>;
      case 'left':
        return <div className={`mr-3 ${labelClasses} min-w-[3rem]`}>{labelContent}</div>;
      case 'right':
        return <div className={`ml-3 ${labelClasses} min-w-[3rem]`}>{labelContent}</div>;
      default:
        return null;
    }
  };

  const containerClasses = labelPosition === 'left' || labelPosition === 'right' 
    ? 'flex items-center' 
    : '';

  const progressLabel = ariaLabel || `Progress: ${Math.round(percentage)}%`;

  return (
    <div className={`${containerClasses} ${className}`}>
      {labelPosition === 'left' && renderLabel()}
      {labelPosition === 'top' && renderLabel()}
      
      <div className="flex-1">
        <div 
          className={`w-full bg-gray-200 rounded-full overflow-hidden ${sizeClasses[size]}`}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={min}
          aria-valuemax={max}
          aria-label={progressLabel}
        >
          <div
            className={`${variantClasses[variant]} ${getAnimationClasses()} h-full rounded-full transition-all duration-300 ease-out`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
      
      {labelPosition === 'right' && renderLabel()}
      {labelPosition === 'bottom' && renderLabel()}
    </div>
  );
};

export default Progress; 
import React from 'react';

export type LoadingVariant = 'spinner' | 'dots' | 'bars' | 'pulse' | 'skeleton';

export type LoadingSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface LoadingProps {
  variant?: LoadingVariant;
  size?: LoadingSize;
  text?: string;
  className?: string;
}

const getLoadingSizeClasses = (size: LoadingSize = 'md'): string => {
  const sizeClasses = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  return sizeClasses[size];
};

export const Loading: React.FC<LoadingProps> = ({
  variant = 'spinner',
  size = 'md',
  text,
  className = ''
}) => {
  const sizeClasses = getLoadingSizeClasses(size);

  const renderSpinner = () => (
    <div className={`${sizeClasses} border-2 border-secondary-200 border-t-primary-600 rounded-full animate-spin ${className}`} />
  );

  const renderDots = () => (
    <div className={`flex space-x-1 ${className}`}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={`${sizeClasses} bg-primary-600 rounded-full animate-bounce`}
          style={{ animationDelay: `${i * 0.1}s` }}
        />
      ))}
    </div>
  );

  const renderBars = () => (
    <div className={`flex space-x-1 ${className}`}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={`w-1 bg-primary-600 animate-pulse`}
          style={{
            height: size === 'xs' ? '12px' : size === 'sm' ? '16px' : size === 'md' ? '24px' : size === 'lg' ? '32px' : '48px',
            animationDelay: `${i * 0.1}s`
          }}
        />
      ))}
    </div>
  );

  const renderPulse = () => (
    <div className={`${sizeClasses} bg-primary-600 rounded-full animate-pulse ${className}`} />
  );

  const renderContent = () => {
    switch (variant) {
      case 'spinner':
        return renderSpinner();
      case 'dots':
        return renderDots();
      case 'bars':
        return renderBars();
      case 'pulse':
        return renderPulse();
      default:
        return renderSpinner();
    }
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-2">
      {renderContent()}
      {text && (
        <p className="text-sm text-secondary-600">{text}</p>
      )}
    </div>
  );
};

// Loading Overlay Component
interface LoadingOverlayProps extends LoadingProps {
  children?: React.ReactNode;
  overlay?: boolean;
  backdrop?: boolean;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  children,
  overlay = true,
  backdrop = true,
  className = '',
  ...loadingProps
}) => {
  if (!overlay) {
    return <Loading {...loadingProps} className={className} />;
  }

  return (
    <div className="relative">
      {children}
      <div className={`absolute inset-0 flex items-center justify-center ${
        backdrop ? 'bg-white bg-opacity-75' : ''
      } ${className}`}>
        <Loading {...loadingProps} />
      </div>
    </div>
  );
};

// Skeleton Component
interface SkeletonProps {
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'text',
  width,
  height,
  className = ''
}) => {
  const baseClasses = 'animate-pulse bg-secondary-200';

  const variantClasses = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-md'
  };

  const style: React.CSSProperties = {};
  if (width) style.width = typeof width === 'number' ? `${width}px` : width;
  if (height) style.height = typeof height === 'number' ? `${height}px` : height;

  return (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      style={style}
    />
  );
};

// Skeleton Text Component
interface SkeletonTextProps {
  lines?: number;
  className?: string;
}

export const SkeletonText: React.FC<SkeletonTextProps> = ({
  lines = 3,
  className = ''
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          variant="text"
          height="1rem"
          width={index === lines - 1 ? '60%' : '100%'}
        />
      ))}
    </div>
  );
};

// Skeleton Avatar Component
interface SkeletonAvatarProps {
  size?: LoadingSize;
  className?: string;
}

export const SkeletonAvatar: React.FC<SkeletonAvatarProps> = ({
  size = 'md',
  className = ''
}) => {
  const sizeClasses = getLoadingSizeClasses(size);

  return (
    <Skeleton
      variant="circular"
      className={`${sizeClasses} ${className}`}
    />
  );
};

// Skeleton Card Component
interface SkeletonCardProps {
  className?: string;
}

export const SkeletonCard: React.FC<SkeletonCardProps> = ({
  className = ''
}) => {
  return (
    <div className={`p-6 space-y-4 ${className}`}>
      <div className="flex items-center space-x-4">
        <SkeletonAvatar size="lg" />
        <div className="flex-1 space-y-2">
          <Skeleton variant="text" height="1.5rem" width="60%" />
          <Skeleton variant="text" height="1rem" width="40%" />
        </div>
      </div>
      <SkeletonText lines={3} />
      <div className="flex space-x-2">
        <Skeleton variant="rectangular" height="2rem" width="80px" />
        <Skeleton variant="rectangular" height="2rem" width="80px" />
      </div>
    </div>
  );
};

// Loading Button Component
interface LoadingButtonProps {
  loading?: boolean;
  loadingText?: string;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
}

export const LoadingButton: React.FC<LoadingButtonProps> = ({
  loading = false,
  loadingText,
  children,
  className = '',
  onClick,
  disabled = false
}) => {
  const isDisabled = disabled || loading;

  return (
    <button
      className={`inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed ${
        loading
          ? 'bg-primary-600 text-white'
          : 'bg-primary-600 text-white hover:bg-primary-700'
      } ${className}`}
      onClick={onClick}
      disabled={isDisabled}
    >
      {loading && (
        <Loading
          variant="spinner"
          size="sm"
          className="mr-2"
        />
      )}
      {loading ? loadingText || children : children}
    </button>
  );
};

// Progress Bar Component
interface ProgressBarProps {
  value: number;
  max?: number;
  variant?: 'default' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  variant = 'default',
  size = 'md',
  showLabel = false,
  className = ''
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const variantClasses = {
    default: 'bg-primary-600',
    success: 'bg-success-600',
    warning: 'bg-warning-600',
    error: 'bg-error-600'
  };

  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };

  return (
    <div className={`w-full ${className}`}>
      {showLabel && (
        <div className="flex justify-between text-sm text-secondary-600 mb-1">
          <span>Progress</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}
      
      <div className={`w-full bg-secondary-200 rounded-full overflow-hidden ${sizeClasses[size]}`}>
        <div
          className={`h-full transition-all duration-300 ease-out ${variantClasses[variant]}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}; 
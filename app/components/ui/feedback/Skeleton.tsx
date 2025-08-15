import React from 'react';

export interface SkeletonProps {
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  className?: string;
  animated?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'text',
  width,
  height,
  className = '',
  animated = true
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'text':
        return 'h-4 rounded';
      case 'circular':
        return 'rounded-full';
      case 'rectangular':
        return 'rounded';
      default:
        return 'h-4 rounded';
    }
  };

  const getAnimationClasses = () => {
    if (!animated) return '';
    return 'animate-pulse bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 bg-[length:200%_100%]';
  };

  const getDefaultDimensions = () => {
    switch (variant) {
      case 'text':
        return { width: '100%', height: '1rem' };
      case 'circular':
        return { width: '2rem', height: '2rem' };
      case 'rectangular':
        return { width: '100%', height: '8rem' };
      default:
        return { width: '100%', height: '1rem' };
    }
  };

  const defaultDims = getDefaultDimensions();
  const finalWidth = width || defaultDims.width;
  const finalHeight = height || defaultDims.height;

  const style = {
    width: typeof finalWidth === 'number' ? `${finalWidth}px` : finalWidth,
    height: typeof finalHeight === 'number' ? `${finalHeight}px` : finalHeight,
  };

  return (
    <div
      className={`bg-gray-200 ${getVariantClasses()} ${getAnimationClasses()} ${className}`}
      style={style}
      aria-hidden="true"
    />
  );
};

// Componentes especializados de Skeleton
export const SkeletonText: React.FC<{
  lines?: number;
  className?: string;
  animated?: boolean;
}> = ({ lines = 1, className = '', animated = true }) => (
  <div className={`space-y-2 ${className}`}>
    {Array.from({ length: lines }).map((_, index) => (
      <Skeleton
        key={index}
        variant="text"
        width={index === lines - 1 ? '75%' : '100%'}
        animated={animated}
      />
    ))}
  </div>
);

export const SkeletonAvatar: React.FC<{
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  animated?: boolean;
}> = ({ size = 'md', className = '', animated = true }) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };

  return (
    <Skeleton
      variant="circular"
      className={`${sizeClasses[size]} ${className}`}
      animated={animated}
    />
  );
};

export const SkeletonCard: React.FC<{
  className?: string;
  animated?: boolean;
}> = ({ className = '', animated = true }) => (
  <div className={`p-4 border border-gray-200 rounded-lg ${className}`}>
    <div className="flex items-center space-x-4 mb-4">
      <SkeletonAvatar size="md" animated={animated} />
      <div className="flex-1">
        <SkeletonText lines={2} animated={animated} />
      </div>
    </div>
    <Skeleton variant="rectangular" height="6rem" animated={animated} />
  </div>
);

export const SkeletonTable: React.FC<{
  rows?: number;
  columns?: number;
  className?: string;
  animated?: boolean;
}> = ({ rows = 5, columns = 4, className = '', animated = true }) => (
  <div className={`overflow-hidden border border-gray-200 rounded-lg ${className}`}>
    {/* Header */}
    <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
      <div className="flex space-x-4">
        {Array.from({ length: columns }).map((_, index) => (
          <Skeleton
            key={index}
            variant="text"
            width="20%"
            animated={animated}
          />
        ))}
      </div>
    </div>
    
    {/* Rows */}
    <div className="divide-y divide-gray-200">
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="px-4 py-3">
          <div className="flex space-x-4">
            {Array.from({ length: columns }).map((_, colIndex) => (
              <Skeleton
                key={colIndex}
                variant="text"
                width={colIndex === 0 ? '30%' : '20%'}
                animated={animated}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

export default Skeleton; 
import React, { forwardRef } from 'react';

export type CardVariant = 'default' | 'elevated' | 'outlined' | 'filled';

export type CardSize = 'sm' | 'md' | 'lg';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  size?: CardSize;
  padding?: boolean;
  children: React.ReactNode;
}

const getCardClasses = (
  variant: CardVariant = 'default',
  size: CardSize = 'md',
  padding: boolean = true
): string => {
  const baseClasses = [
    'bg-white rounded-lg transition-all duration-200',
    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
  ];

  const variantClasses = {
    default: [
      'border border-secondary-200',
      'shadow-sm hover:shadow-md'
    ],
    elevated: [
      'border border-secondary-200',
      'shadow-lg hover:shadow-xl'
    ],
    outlined: [
      'border-2 border-secondary-300',
      'shadow-none hover:shadow-sm'
    ],
    filled: [
      'bg-secondary-50 border border-secondary-200',
      'shadow-sm'
    ]
  };

  const sizeClasses = {
    sm: padding ? 'p-3' : '',
    md: padding ? 'p-6' : '',
    lg: padding ? 'p-8' : ''
  };

  return [
    ...baseClasses,
    ...variantClasses[variant],
    sizeClasses[size]
  ].join(' ');
};

export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = 'default',
      size = 'md',
      padding = true,
      children,
      className = '',
      ...props
    },
    ref
  ) => {
    const cardClasses = getCardClasses(variant, size, padding);

    return (
      <div
        ref={ref}
        className={`${cardClasses} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

// Card Header Component
interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  action?: React.ReactNode;
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  children,
  action,
  className = '',
  ...props
}) => {
  return (
    <div
      className={`flex items-center justify-between pb-4 border-b border-secondary-200 ${className}`}
      {...props}
    >
      <div className="flex-1">
        {children}
      </div>
      {action && (
        <div className="flex-shrink-0 ml-4">
          {action}
        </div>
      )}
    </div>
  );
};

// Card Body Component
interface CardBodyProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  padding?: boolean;
}

export const CardBody: React.FC<CardBodyProps> = ({
  children,
  padding = true,
  className = '',
  ...props
}) => {
  const paddingClasses = padding ? 'py-4' : '';

  return (
    <div
      className={`${paddingClasses} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

// Card Footer Component
interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  action?: React.ReactNode;
}

export const CardFooter: React.FC<CardFooterProps> = ({
  children,
  action,
  className = '',
  ...props
}) => {
  return (
    <div
      className={`flex items-center justify-between pt-4 border-t border-secondary-200 ${className}`}
      {...props}
    >
      <div className="flex-1">
        {children}
      </div>
      {action && (
        <div className="flex-shrink-0 ml-4">
          {action}
        </div>
      )}
    </div>
  );
};

// Card Title Component
interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
}

export const CardTitle: React.FC<CardTitleProps> = ({
  children,
  as: Component = 'h3',
  className = '',
  ...props
}) => {
  return (
    <Component
      className={`text-lg font-semibold text-secondary-900 ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
};

// Card Subtitle Component
interface CardSubtitleProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

export const CardSubtitle: React.FC<CardSubtitleProps> = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <p
      className={`text-sm text-secondary-600 mt-1 ${className}`}
      {...props}
    >
      {children}
    </p>
  );
};

// Card Content Component
interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const CardContent: React.FC<CardContentProps> = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <div
      className={`text-secondary-700 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

// Interactive Card Component
interface InteractiveCardProps extends CardProps {
  onClick?: () => void;
  hoverable?: boolean;
  selected?: boolean;
}

export const InteractiveCard = forwardRef<HTMLDivElement, InteractiveCardProps>(
  (
    {
      onClick,
      hoverable = true,
      selected = false,
      className = '',
      ...props
    },
    ref
  ) => {
    const interactiveClasses = [
      hoverable ? 'cursor-pointer hover:scale-[1.02]' : '',
      selected ? 'ring-2 ring-primary-500 ring-offset-2' : '',
      onClick ? 'cursor-pointer' : ''
    ].filter(Boolean).join(' ');

    return (
      <Card
        ref={ref}
        className={`${interactiveClasses} ${className}`}
        onClick={onClick}
        {...props}
      />
    );
  }
);

InteractiveCard.displayName = 'InteractiveCard';

// Card Grid Component
interface CardGridProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  columns?: 1 | 2 | 3 | 4 | 6;
  gap?: 'sm' | 'md' | 'lg';
}

export const CardGrid: React.FC<CardGridProps> = ({
  children,
  columns = 3,
  gap = 'md',
  className = '',
  ...props
}) => {
  const gridClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
    6: 'grid-cols-2 md:grid-cols-3 lg:grid-cols-6'
  };

  const gapClasses = {
    sm: 'gap-3',
    md: 'gap-6',
    lg: 'gap-8'
  };

  return (
    <div
      className={`grid ${gridClasses[columns]} ${gapClasses[gap]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}; 
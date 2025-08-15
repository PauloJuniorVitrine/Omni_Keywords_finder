import React, { forwardRef } from 'react';
import { cn } from '../../../utils/cn';

// Tipos específicos para o sistema Omni Keywords Finder
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined' | 'filled';
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  hover?: boolean;
  interactive?: boolean;
  fullWidth?: boolean;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  image?: {
    src: string;
    alt: string;
    position?: 'top' | 'bottom';
  };
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      className,
      variant = 'default',
      padding = 'md',
      shadow = 'sm',
      hover = false,
      interactive = false,
      fullWidth = false,
      header,
      footer,
      image,
      children,
      ...props
    },
    ref
  ) => {
    // Design tokens específicos do Omni Keywords Finder
    const cardVariants = {
      default: 'bg-white border border-gray-200',
      elevated: 'bg-white shadow-lg border-0',
      outlined: 'bg-white border-2 border-gray-300',
      filled: 'bg-gray-50 border border-gray-200'
    };

    const cardPadding = {
      none: '',
      sm: 'p-3',
      md: 'p-6',
      lg: 'p-8',
      xl: 'p-12'
    };

    const cardShadow = {
      none: '',
      sm: 'shadow-sm',
      md: 'shadow-md',
      lg: 'shadow-lg',
      xl: 'shadow-xl'
    };

    const cardHover = hover ? 'hover:shadow-lg hover:-translate-y-1 transition-all duration-200' : '';
    const cardInteractive = interactive ? 'cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2' : '';

    return (
      <div
        ref={ref}
        className={cn(
          'rounded-lg overflow-hidden',
          cardVariants[variant],
          cardShadow[shadow],
          cardHover,
          cardInteractive,
          fullWidth && 'w-full',
          className
        )}
        tabIndex={interactive ? 0 : undefined}
        role={interactive ? 'button' : undefined}
        {...props}
      >
        {image && image.position !== 'bottom' && (
          <div className="relative">
            <img
              src={image.src}
              alt={image.alt}
              className="w-full h-48 object-cover"
              loading="lazy"
            />
          </div>
        )}

        {header && (
          <div className={cn(
            'border-b border-gray-200 bg-gray-50',
            cardPadding[padding] === 'p-6' ? 'px-6 py-4' :
            cardPadding[padding] === 'p-8' ? 'px-8 py-6' :
            cardPadding[padding] === 'p-12' ? 'px-12 py-8' :
            'px-3 py-2'
          )}>
            {header}
          </div>
        )}

        <div className={cn(cardPadding[padding])}>
          {children}
        </div>

        {footer && (
          <div className={cn(
            'border-t border-gray-200 bg-gray-50',
            cardPadding[padding] === 'p-6' ? 'px-6 py-4' :
            cardPadding[padding] === 'p-8' ? 'px-8 py-6' :
            cardPadding[padding] === 'p-12' ? 'px-12 py-8' :
            'px-3 py-2'
          )}>
            {footer}
          </div>
        )}

        {image && image.position === 'bottom' && (
          <div className="relative">
            <img
              src={image.src}
              alt={image.alt}
              className="w-full h-48 object-cover"
              loading="lazy"
            />
          </div>
        )}
      </div>
    );
  }
);

Card.displayName = 'Card';

// Subcomponentes para facilitar o uso
export const CardHeader = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('flex items-center justify-between', className)} {...props}>
    {children}
  </div>
);

export const CardTitle = ({ className, children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
  <h3 className={cn('text-lg font-semibold text-gray-900', className)} {...props}>
    {children}
  </h3>
);

export const CardSubtitle = ({ className, children, ...props }: React.HTMLAttributes<HTMLParagraphElement>) => (
  <p className={cn('text-sm text-gray-600', className)} {...props}>
    {children}
  </p>
);

export const CardContent = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('text-gray-700', className)} {...props}>
    {children}
  </div>
);

export const CardFooter = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('flex items-center justify-between', className)} {...props}>
    {children}
  </div>
); 
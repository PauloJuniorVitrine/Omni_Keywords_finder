import React, { forwardRef } from 'react';
import { lightTheme } from '../theme_v2';

export type ButtonVariant = 
  | 'primary' 
  | 'secondary' 
  | 'outline' 
  | 'ghost' 
  | 'danger' 
  | 'success' 
  | 'warning';

export type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  rounded?: boolean;
  children: React.ReactNode;
}

const getButtonClasses = (
  variant: ButtonVariant = 'primary',
  size: ButtonSize = 'md',
  fullWidth: boolean = false,
  rounded: boolean = false,
  disabled: boolean = false,
  loading: boolean = false
): string => {
  const baseClasses = [
    'inline-flex items-center justify-center font-medium transition-all duration-200',
    'focus:outline-none focus:ring-2 focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    'relative overflow-hidden'
  ];

  const variantClasses = {
    primary: [
      'bg-primary-600 text-white',
      'hover:bg-primary-700 active:bg-primary-800',
      'focus:ring-primary-500',
      'shadow-sm hover:shadow-md'
    ],
    secondary: [
      'bg-secondary-100 text-secondary-900',
      'hover:bg-secondary-200 active:bg-secondary-300',
      'focus:ring-secondary-500',
      'border border-secondary-300'
    ],
    outline: [
      'bg-transparent text-secondary-700',
      'border border-secondary-300',
      'hover:bg-secondary-50 active:bg-secondary-100',
      'focus:ring-secondary-500'
    ],
    ghost: [
      'bg-transparent text-secondary-700',
      'hover:bg-secondary-100 active:bg-secondary-200',
      'focus:ring-secondary-500'
    ],
    danger: [
      'bg-error-600 text-white',
      'hover:bg-error-700 active:bg-error-800',
      'focus:ring-error-500',
      'shadow-sm hover:shadow-md'
    ],
    success: [
      'bg-success-600 text-white',
      'hover:bg-success-700 active:bg-success-800',
      'focus:ring-success-500',
      'shadow-sm hover:shadow-md'
    ],
    warning: [
      'bg-warning-600 text-white',
      'hover:bg-warning-700 active:bg-warning-800',
      'focus:ring-warning-500',
      'shadow-sm hover:shadow-md'
    ]
  };

  const sizeClasses = {
    xs: 'px-2 py-1 text-xs',
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
    xl: 'px-8 py-4 text-xl'
  };

  const borderRadiusClasses = rounded ? 'rounded-full' : 'rounded-lg';
  const widthClasses = fullWidth ? 'w-full' : '';

  return [
    ...baseClasses,
    ...variantClasses[variant],
    sizeClasses[size],
    borderRadiusClasses,
    widthClasses
  ].join(' ');
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      rounded = false,
      disabled = false,
      children,
      className = '',
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;
    const buttonClasses = getButtonClasses(variant, size, fullWidth, rounded, isDisabled, loading);

    return (
      <button
        ref={ref}
        className={`${buttonClasses} ${className}`}
        disabled={isDisabled}
        {...props}
      >
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-inherit rounded-inherit">
            <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          </div>
        )}
        
        <div className={`flex items-center gap-2 ${loading ? 'opacity-0' : ''}`}>
          {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
          <span>{children}</span>
          {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
        </div>
      </button>
    );
  }
);

Button.displayName = 'Button';

// Button Group Component
interface ButtonGroupProps {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  attached?: boolean;
  className?: string;
}

export const ButtonGroup: React.FC<ButtonGroupProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  attached = false,
  className = ''
}) => {
  const groupClasses = [
    'inline-flex',
    attached ? 'rounded-lg overflow-hidden' : 'gap-1',
    className
  ].join(' ');

  return (
    <div className={groupClasses}>
      {React.Children.map(children, (child, index) => {
        if (React.isValidElement(child) && child.type === Button) {
          return React.cloneElement(child, {
            variant: child.props.variant || variant,
            size: child.props.size || size,
            className: [
              child.props.className,
              attached && index === 0 ? 'rounded-l-lg rounded-r-none' : '',
              attached && index === React.Children.count(children) - 1 ? 'rounded-r-lg rounded-l-none' : '',
              attached && index > 0 && index < React.Children.count(children) - 1 ? 'rounded-none' : '',
              attached && index > 0 ? 'border-l-0' : ''
            ].filter(Boolean).join(' ')
          });
        }
        return child;
      })}
    </div>
  );
};

// Icon Button Component
interface IconButtonProps extends Omit<ButtonProps, 'children'> {
  icon: React.ReactNode;
  'aria-label': string;
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ icon, 'aria-label': ariaLabel, size = 'md', ...props }, ref) => {
    const iconSizeClasses = {
      xs: 'w-6 h-6',
      sm: 'w-8 h-8',
      md: 'w-10 h-10',
      lg: 'w-12 h-12',
      xl: 'w-14 h-14'
    };

    return (
      <Button
        ref={ref}
        size={size}
        className={`p-0 ${iconSizeClasses[size]}`}
        aria-label={ariaLabel}
        {...props}
      >
        {icon}
      </Button>
    );
  }
);

IconButton.displayName = 'IconButton';

// Loading Button Component
interface LoadingButtonProps extends ButtonProps {
  loadingText?: string;
}

export const LoadingButton = forwardRef<HTMLButtonElement, LoadingButtonProps>(
  ({ loadingText, children, loading, ...props }, ref) => {
    return (
      <Button
        ref={ref}
        loading={loading}
        {...props}
      >
        {loading ? loadingText || children : children}
      </Button>
    );
  }
);

LoadingButton.displayName = 'LoadingButton'; 
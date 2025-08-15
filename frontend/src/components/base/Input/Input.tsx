import React, { forwardRef, useState } from 'react';
import { cn } from '../../../utils/cn';
import { useA11y } from '../../../hooks/useA11y';

// Tipos específicos para o sistema Omni Keywords Finder
export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  variant?: 'default' | 'filled' | 'outlined';
  size?: 'sm' | 'md' | 'lg';
  required?: boolean;
  showPasswordToggle?: boolean;
  /** Label acessível para screen readers */
  ariaLabel?: string;
  /** Descrição detalhada para acessibilidade */
  ariaDescription?: string;
  /** Se o input é inválido */
  invalid?: boolean;
  /** Mensagem de erro para acessibilidade */
  ariaErrorMessage?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      type = 'text',
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      fullWidth = false,
      variant = 'default',
      size = 'md',
      required = false,
      showPasswordToggle = false,
      disabled = false,
      ariaLabel,
      ariaDescription,
      invalid = false,
      ariaErrorMessage,
      id,
      ...props
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = useState(false);
    const [isFocused, setIsFocused] = useState(false);
    
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const inputType = showPasswordToggle && type === 'password' ? (showPassword ? 'text' : 'password') : type;

    // Hook de acessibilidade
    const { a11yProps } = useA11y({
      id: inputId,
      label: ariaLabel || label,
      description: ariaDescription || helperText,
      required,
      invalid: invalid || !!error,
      errorMessage: ariaErrorMessage || error,
      disabled,
      role: 'textbox'
    });

    // Design tokens específicos do Omni Keywords Finder
    const inputVariants = {
      default: 'border border-gray-300 bg-white',
      filled: 'border-0 bg-gray-50',
      outlined: 'border-2 border-gray-300 bg-white'
    };

    const inputSizes = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-sm',
      lg: 'px-6 py-3 text-base'
    };

    const containerVariants = {
      default: 'focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500',
      filled: 'focus-within:bg-white focus-within:border focus-within:border-blue-500',
      outlined: 'focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500'
    };

    return (
      <div className={cn('relative', fullWidth && 'w-full')}>
        {label && (
          <label
            htmlFor={inputId}
            className={cn(
              'block text-sm font-medium text-gray-700 mb-1',
              required && 'after:content-["*"] after:ml-0.5 after:text-red-500'
            )}
          >
            {label}
          </label>
        )}
        
        <div
          className={cn(
            'relative flex items-center rounded-md transition-all duration-200',
            inputVariants[variant],
            containerVariants[variant],
            error && 'border-red-500 focus-within:border-red-500 focus-within:ring-red-500',
            disabled && 'opacity-50 cursor-not-allowed',
            inputSizes[size],
            className
          )}
        >
          {leftIcon && (
            <span className="absolute left-3 text-gray-400" aria-hidden="true">
              {leftIcon}
            </span>
          )}
          
          <input
            ref={ref}
            id={inputId}
            type={inputType}
            className={cn(
              'w-full bg-transparent outline-none placeholder:text-gray-400',
              leftIcon && 'pl-10',
              rightIcon && !showPasswordToggle && 'pr-10',
              showPasswordToggle && 'pr-12',
              disabled && 'cursor-not-allowed'
            )}
            disabled={disabled}
            required={required}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            {...a11yProps}
            {...props}
          />
          
          {showPasswordToggle && type === 'password' && (
            <button
              type="button"
              className="absolute right-3 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
              disabled={disabled}
            >
              {showPassword ? (
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                </svg>
              ) : (
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              )}
            </button>
          )}
          
          {rightIcon && !showPasswordToggle && (
            <span className="absolute right-3 text-gray-400" aria-hidden="true">
              {rightIcon}
            </span>
          )}
        </div>
        
        {error && (
          <p id={`${inputId}-error`} className="mt-1 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
        
        {helperText && !error && (
          <p id={`${inputId}-helper`} className="mt-1 text-sm text-gray-500">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input'; 
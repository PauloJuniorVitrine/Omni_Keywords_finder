/**
 * Input Component - Omni Keywords Finder
 * 
 * Componente de input completo com validação, estados e acessibilidade
 * 
 * Tracing ID: DS-COMP-002
 * Data/Hora: 2025-01-27 15:30:00 UTC
 * Versão: 1.0
 */

import React, { forwardRef, InputHTMLAttributes, useState } from 'react';
import { primaryColors, stateColors, neutralColors, secondaryColors } from '../../theme/colors';

// =============================================================================
// TIPOS E INTERFACES
// =============================================================================

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string;
  helperText?: string;
  error?: string;
  success?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'outlined' | 'filled' | 'flushed';
  fullWidth?: boolean;
  required?: boolean;
  showPasswordToggle?: boolean;
}

// =============================================================================
// UTILITÁRIOS DE ESTILO
// =============================================================================

interface InputStyleProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'outlined' | 'filled' | 'flushed';
  hasError?: boolean;
  hasSuccess?: boolean;
  isFocused?: boolean;
  fullWidth?: boolean;
}

const getInputStyles = (props: InputStyleProps): React.CSSProperties => {
  const { size = 'md', variant = 'outlined', hasError, hasSuccess, isFocused, fullWidth } = props;
  
  // Estilos base
  const baseStyles: React.CSSProperties = {
    width: fullWidth ? '100%' : 'auto',
    border: '1px solid',
    borderRadius: variant === 'flushed' ? '0' : '0.375rem',
    transition: 'all 0.2s ease-in-out',
    outline: 'none',
    fontFamily: 'inherit',
    backgroundColor: variant === 'filled' ? secondaryColors[50] : neutralColors.white,
  };

  // Estilos de tamanho
  const sizeStyles: Record<string, React.CSSProperties> = {
    sm: {
      padding: '0.375rem 0.75rem',
      fontSize: '0.875rem',
      lineHeight: '1.25rem',
      minHeight: '2rem',
    },
    md: {
      padding: '0.5rem 0.75rem',
      fontSize: '1rem',
      lineHeight: '1.5rem',
      minHeight: '2.5rem',
    },
    lg: {
      padding: '0.75rem 1rem',
      fontSize: '1.125rem',
      lineHeight: '1.75rem',
      minHeight: '3rem',
    }
  };

  // Estilos de estado
  let stateStyles: React.CSSProperties = {};
  
  if (hasError) {
    stateStyles = {
      borderColor: stateColors.error[300],
      backgroundColor: variant === 'filled' ? stateColors.error[50] : neutralColors.white,
      color: stateColors.error[700],
    };
  } else if (hasSuccess) {
    stateStyles = {
      borderColor: stateColors.success[300],
      backgroundColor: variant === 'filled' ? stateColors.success[50] : neutralColors.white,
      color: stateColors.success[700],
    };
  } else if (isFocused) {
    stateStyles = {
      borderColor: primaryColors[500],
      boxShadow: `0 0 0 3px ${primaryColors[100]}`,
    };
  } else {
    stateStyles = {
      borderColor: secondaryColors[300],
      color: secondaryColors[900],
    };
  }

  // Estilos de variante
  const variantStyles: Record<string, React.CSSProperties> = {
    outlined: {
      borderStyle: 'solid',
    },
    filled: {
      borderStyle: 'solid',
      borderBottomWidth: '2px',
    },
    flushed: {
      borderStyle: 'none',
      borderBottomStyle: 'solid',
      borderBottomWidth: '2px',
      borderRadius: '0',
      paddingLeft: '0',
      paddingRight: '0',
    }
  };

  return {
    ...baseStyles,
    ...sizeStyles[size],
    ...stateStyles,
    ...variantStyles[variant],
  };
};

const getContainerStyles = (fullWidth: boolean): React.CSSProperties => ({
  display: 'flex',
  flexDirection: 'column',
  width: fullWidth ? '100%' : 'auto',
  position: 'relative',
});

const getLabelStyles = (size: string, hasError: boolean, hasSuccess: boolean): React.CSSProperties => {
  const sizeStyles = {
    sm: { fontSize: '0.875rem', marginBottom: '0.25rem' },
    md: { fontSize: '1rem', marginBottom: '0.375rem' },
    lg: { fontSize: '1.125rem', marginBottom: '0.5rem' }
  };

  let color = secondaryColors[700] as string;
  if (hasError) color = stateColors.error[600] as string;
  if (hasSuccess) color = stateColors.success[600] as string;

  return {
    ...sizeStyles[size as keyof typeof sizeStyles],
    fontWeight: 500,
    color,
    display: 'block',
  };
};

const getHelperTextStyles = (hasError: boolean, hasSuccess: boolean): React.CSSProperties => {
  let color = secondaryColors[600] as string;
  if (hasError) color = stateColors.error[600] as string;
  if (hasSuccess) color = stateColors.success[600] as string;

  return {
    fontSize: '0.875rem',
    marginTop: '0.25rem',
    color,
  };
};

const getIconContainerStyles = (position: 'left' | 'right'): React.CSSProperties => ({
  position: 'absolute',
  top: '50%',
  transform: 'translateY(-50%)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  pointerEvents: 'none',
  zIndex: 1,
  ...(position === 'left' ? { left: '0.75rem' } : { right: '0.75rem' }),
});

// =============================================================================
// COMPONENTE PRINCIPAL
// =============================================================================

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      helperText,
      error,
      success,
      leftIcon,
      rightIcon,
      size = 'md',
      variant = 'outlined',
      fullWidth = false,
      required = false,
      showPasswordToggle = false,
      type = 'text',
      style,
      onFocus,
      onBlur,
      ...props
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    
    const hasError = !!error;
    const hasSuccess = !!success;
    const inputType = showPasswordToggle && type === 'password' ? (showPassword ? 'text' : 'password') : type;
    
    const inputStyles = getInputStyles({
      size,
      variant,
      hasError,
      hasSuccess,
      isFocused,
      fullWidth,
    });

    const containerStyles = getContainerStyles(fullWidth);
    const labelStyles = getLabelStyles(size, hasError, hasSuccess);
    const helperTextStyles = getHelperTextStyles(hasError, hasSuccess);

    const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(true);
      onFocus?.(e);
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(false);
      onBlur?.(e);
    };

    const togglePasswordVisibility = () => {
      setShowPassword(!showPassword);
    };

    return (
      <div style={containerStyles}>
        {label && (
          <label style={labelStyles}>
            {label}
            {required && <span style={{ color: stateColors.error[500], marginLeft: '0.25rem' }}>*</span>}
          </label>
        )}
        
        <div style={{ position: 'relative' }}>
          {leftIcon && (
            <div style={getIconContainerStyles('left')}>
              {leftIcon}
            </div>
          )}
          
          <input
            ref={ref}
            type={inputType}
            style={{
              ...inputStyles,
              ...(leftIcon && { paddingLeft: '2.5rem' }),
              ...(rightIcon && { paddingRight: '2.5rem' }),
              ...style,
            }}
            onFocus={handleFocus}
            onBlur={handleBlur}
            aria-invalid={hasError}
            aria-describedby={error || success || helperText ? 'input-helper-text' : undefined}
            required={required}
            {...props}
          />
          
          {rightIcon && (
            <div style={getIconContainerStyles('right')}>
              {rightIcon}
            </div>
          )}
          
          {showPasswordToggle && type === 'password' && (
            <button
              type="button"
              onClick={togglePasswordVisibility}
              style={{
                position: 'absolute',
                right: '0.75rem',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '0.25rem',
                color: secondaryColors[500],
                fontSize: '1rem',
              }}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? '👁️' : '👁️‍🗨️'}
            </button>
          )}
        </div>
        
        {(error || success || helperText) && (
          <div id="input-helper-text" style={helperTextStyles}>
            {error || success || helperText}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input; 
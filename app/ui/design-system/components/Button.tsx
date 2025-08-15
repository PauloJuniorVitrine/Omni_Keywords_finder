/**
 * Button Component - Omni Keywords Finder
 * 
 * Componente de botão completo com variantes, estados e acessibilidade
 * 
 * Tracing ID: DS-COMP-001
 * Data/Hora: 2025-01-27 15:30:00 UTC
 * Versão: 1.0
 */

import React, { forwardRef, ButtonHTMLAttributes } from 'react';
import { primaryColors, stateColors, neutralColors } from '../../theme/colors';

// =============================================================================
// TIPOS E INTERFACES
// =============================================================================

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
}

// =============================================================================
// UTILITÁRIOS DE ESTILO
// =============================================================================

interface ButtonStyleProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
}

const getButtonStyles = (props: ButtonStyleProps): React.CSSProperties => {
  const { variant = 'primary', size = 'md', loading = false, disabled = false, fullWidth = false } = props;
  
  // Estilos base
  const baseStyles: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
    fontWeight: 500,
    borderRadius: '0.375rem',
    border: '1px solid transparent',
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    transition: 'all 0.2s ease-in-out',
    textDecoration: 'none',
    whiteSpace: 'nowrap',
    userSelect: 'none',
    position: 'relative',
    overflow: 'hidden',
    opacity: disabled || loading ? 0.6 : 1,
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
      padding: '0.5rem 1rem',
      fontSize: '1rem',
      lineHeight: '1.5rem',
      minHeight: '2.5rem',
    },
    lg: {
      padding: '0.75rem 1.5rem',
      fontSize: '1.125rem',
      lineHeight: '1.75rem',
      minHeight: '3rem',
    },
    xl: {
      padding: '1rem 2rem',
      fontSize: '1.25rem',
      lineHeight: '2rem',
      minHeight: '3.5rem',
    }
  };

  // Estilos de variante
  const variantStyles: Record<string, React.CSSProperties> = {
    primary: {
      backgroundColor: primaryColors[600],
      color: neutralColors.white,
      borderColor: primaryColors[600],
    },
    secondary: {
      backgroundColor: neutralColors.white,
      color: primaryColors[600],
      borderColor: primaryColors[600],
    },
    outline: {
      backgroundColor: 'transparent',
      color: primaryColors[600],
      borderColor: primaryColors[300],
    },
    ghost: {
      backgroundColor: 'transparent',
      color: primaryColors[600],
      borderColor: 'transparent',
    },
    danger: {
      backgroundColor: stateColors.error[600],
      color: neutralColors.white,
      borderColor: stateColors.error[600],
    }
  };

  // Estilos de largura total
  const fullWidthStyles: React.CSSProperties = fullWidth ? { width: '100%' } : {};

  // Estilos de loading
  const loadingStyles: React.CSSProperties = loading ? {
    color: 'transparent',
  } : {};

  return {
    ...baseStyles,
    ...sizeStyles[size],
    ...variantStyles[variant],
    ...fullWidthStyles,
    ...loadingStyles,
  };
};

// =============================================================================
// COMPONENTE PRINCIPAL
// =============================================================================

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      disabled = false,
      fullWidth = false,
      leftIcon,
      rightIcon,
      children,
      style,
      onMouseOver,
      onMouseOut,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;
    const buttonStyles = getButtonStyles({ variant, size, loading, disabled, fullWidth });
    
    // Handlers para hover states
    const handleMouseOver = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (!isDisabled) {
        const newStyle = { ...buttonStyles };
        
        switch (variant) {
          case 'primary':
            newStyle.backgroundColor = primaryColors[700];
            newStyle.borderColor = primaryColors[700];
            break;
          case 'secondary':
            newStyle.backgroundColor = primaryColors[50];
            newStyle.borderColor = primaryColors[700];
            break;
          case 'outline':
            newStyle.backgroundColor = primaryColors[50];
            newStyle.borderColor = primaryColors[500];
            break;
          case 'ghost':
            newStyle.backgroundColor = primaryColors[50];
            break;
          case 'danger':
            newStyle.backgroundColor = stateColors.error[700];
            newStyle.borderColor = stateColors.error[700];
            break;
        }
        
        Object.assign(e.currentTarget.style, newStyle);
      }
      onMouseOver?.(e);
    };

    const handleMouseOut = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (!isDisabled) {
        Object.assign(e.currentTarget.style, buttonStyles);
      }
      onMouseOut?.(e);
    };

    const handleMouseDown = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (!isDisabled) {
        e.currentTarget.style.transform = 'translateY(1px)';
      }
    };

    const handleMouseUp = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (!isDisabled) {
        e.currentTarget.style.transform = 'translateY(0)';
      }
    };

    const handleFocus = (e: React.FocusEvent<HTMLButtonElement>) => {
      e.currentTarget.style.outline = `2px solid ${primaryColors[500]}`;
      e.currentTarget.style.outlineOffset = '2px';
    };

    const handleBlur = (e: React.FocusEvent<HTMLButtonElement>) => {
      e.currentTarget.style.outline = 'none';
    };

    return (
      <button
        ref={ref}
        style={{ ...buttonStyles, ...style }}
        disabled={isDisabled}
        aria-disabled={isDisabled}
        aria-busy={loading}
        onMouseOver={handleMouseOver}
        onMouseOut={handleMouseOut}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onFocus={handleFocus}
        onBlur={handleBlur}
        {...props}
      >
        {!loading && leftIcon && <span className="button-icon-left">{leftIcon}</span>}
        <span className="button-content">{children}</span>
        {!loading && rightIcon && <span className="button-icon-right">{rightIcon}</span>}
        {loading && (
          <span
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              width: '1rem',
              height: '1rem',
              margin: '-0.5rem 0 0 -0.5rem',
              border: `2px solid ${neutralColors.white}`,
              borderTopColor: 'transparent',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
            }}
          />
        )}
        <style>
          {`
            @keyframes spin {
              to {
                transform: rotate(360deg);
              }
            }
          `}
        </style>
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button; 
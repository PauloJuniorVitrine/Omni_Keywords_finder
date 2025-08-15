/**
 * Card Component - Omni Keywords Finder
 * 
 * Componente de card completo com variantes, estados e acessibilidade
 * 
 * Tracing ID: DS-COMP-003
 * Data/Hora: 2025-01-27 15:30:00 UTC
 * Versão: 1.0
 */

import React, { forwardRef, HTMLAttributes } from 'react';
import { primaryColors, secondaryColors, neutralColors } from '../../theme/colors';

// =============================================================================
// TIPOS E INTERFACES
// =============================================================================

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'elevated' | 'outlined' | 'filled' | 'interactive';
  size?: 'sm' | 'md' | 'lg';
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  fullWidth?: boolean;
  hoverable?: boolean;
  clickable?: boolean;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  children: React.ReactNode;
}

// =============================================================================
// UTILITÁRIOS DE ESTILO
// =============================================================================

interface CardStyleProps {
  variant?: 'elevated' | 'outlined' | 'filled' | 'interactive';
  size?: 'sm' | 'md' | 'lg';
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  fullWidth?: boolean;
  hoverable?: boolean;
  clickable?: boolean;
}

const getCardStyles = (props: CardStyleProps): React.CSSProperties => {
  const { variant = 'elevated', size = 'md', padding = 'md', fullWidth = false, hoverable = false, clickable = false } = props;
  
  // Estilos base
  const baseStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    width: fullWidth ? '100%' : 'auto',
    borderRadius: '0.5rem',
    transition: 'all 0.2s ease-in-out',
    fontFamily: 'inherit',
    position: 'relative',
    overflow: 'hidden',
  };

  // Estilos de tamanho
  const sizeStyles: Record<string, React.CSSProperties> = {
    sm: {
      minHeight: '8rem',
    },
    md: {
      minHeight: '12rem',
    },
    lg: {
      minHeight: '16rem',
    }
  };

  // Estilos de padding
  const paddingStyles: Record<string, React.CSSProperties> = {
    none: {
      padding: '0',
    },
    sm: {
      padding: '0.75rem',
    },
    md: {
      padding: '1rem',
    },
    lg: {
      padding: '1.5rem',
    },
    xl: {
      padding: '2rem',
    }
  };

  // Estilos de variante
  const variantStyles: Record<string, React.CSSProperties> = {
    elevated: {
      backgroundColor: neutralColors.white,
      border: '1px solid',
      borderColor: secondaryColors[200],
      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    },
    outlined: {
      backgroundColor: neutralColors.white,
      border: '1px solid',
      borderColor: secondaryColors[300],
      boxShadow: 'none',
    },
    filled: {
      backgroundColor: secondaryColors[50],
      border: '1px solid',
      borderColor: secondaryColors[200],
      boxShadow: 'none',
    },
    interactive: {
      backgroundColor: neutralColors.white,
      border: '1px solid',
      borderColor: secondaryColors[200],
      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
      cursor: clickable ? 'pointer' : 'default',
    }
  };

  // Estilos de hover
  const hoverStyles: React.CSSProperties = hoverable ? {
    transform: 'translateY(-2px)',
    boxShadow: '0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  } : {};

  return {
    ...baseStyles,
    ...sizeStyles[size],
    ...paddingStyles[padding],
    ...variantStyles[variant],
    ...hoverStyles,
  };
};

const getHeaderStyles = (padding: string): React.CSSProperties => ({
  padding: padding === 'none' ? '1rem' : '0 0 1rem 0',
  borderBottom: '1px solid',
  borderBottomColor: secondaryColors[200] as string,
  marginBottom: '1rem',
});

const getFooterStyles = (padding: string): React.CSSProperties => ({
  padding: padding === 'none' ? '1rem' : '1rem 0 0 0',
  borderTop: '1px solid',
  borderTopColor: secondaryColors[200] as string,
  marginTop: 'auto',
});

const getContentStyles = (hasHeader: boolean, hasFooter: boolean): React.CSSProperties => ({
  flex: '1',
  display: 'flex',
  flexDirection: 'column',
  ...(hasHeader && { marginTop: '0' }),
  ...(hasFooter && { marginBottom: '0' }),
});

// =============================================================================
// COMPONENTE PRINCIPAL
// =============================================================================

export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = 'elevated',
      size = 'md',
      padding = 'md',
      fullWidth = false,
      hoverable = false,
      clickable = false,
      header,
      footer,
      children,
      style,
      onMouseOver,
      onMouseOut,
      onClick,
      ...props
    },
    ref
  ) => {
    const cardStyles = getCardStyles({
      variant,
      size,
      padding,
      fullWidth,
      hoverable,
      clickable,
    });

    const headerStyles = getHeaderStyles(padding);
    const footerStyles = getFooterStyles(padding);
    const contentStyles = getContentStyles(!!header, !!footer);

    const handleMouseOver = (e: React.MouseEvent<HTMLDivElement>) => {
      if (hoverable) {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = '0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
      }
      onMouseOver?.(e);
    };

    const handleMouseOut = (e: React.MouseEvent<HTMLDivElement>) => {
      if (hoverable) {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = cardStyles.boxShadow as string;
      }
      onMouseOut?.(e);
    };

    const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
      if (clickable) {
        e.currentTarget.style.transform = 'scale(0.98)';
        setTimeout(() => {
          e.currentTarget.style.transform = hoverable ? 'translateY(-2px)' : 'scale(1)';
        }, 150);
      }
      onClick?.(e);
    };

    return (
      <div
        ref={ref}
        style={{ ...cardStyles, ...style }}
        onMouseOver={handleMouseOver}
        onMouseOut={handleMouseOut}
        onClick={handleClick}
        role={clickable ? 'button' : undefined}
        tabIndex={clickable ? 0 : undefined}
        aria-pressed={clickable ? undefined : undefined}
        {...props}
      >
        {header && (
          <div style={headerStyles}>
            {header}
          </div>
        )}
        
        <div style={contentStyles}>
          {children}
        </div>
        
        {footer && (
          <div style={footerStyles}>
            {footer}
          </div>
        )}
      </div>
    );
  }
);

Card.displayName = 'Card';

export default Card; 
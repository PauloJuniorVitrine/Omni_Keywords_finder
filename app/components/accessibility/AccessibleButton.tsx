/**
 * AccessibleButton - Componente de botão com acessibilidade completa
 * 
 * Prompt: Implementação de ARIA labels para Criticalidade 3.2.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { forwardRef, useRef, useEffect } from 'react';
import { Button, ButtonProps, Tooltip } from '@mui/material';
import { styled } from '@mui/material/styles';

interface AccessibleButtonProps extends Omit<ButtonProps, 'aria-label'> {
  ariaLabel: string;
  ariaDescription?: string;
  ariaPressed?: boolean;
  ariaExpanded?: boolean;
  ariaControls?: string;
  ariaHaspopup?: boolean | 'menu' | 'listbox' | 'tree' | 'grid' | 'dialog';
  ariaLive?: 'off' | 'polite' | 'assertive';
  tooltipText?: string;
  tooltipPlacement?: 'top' | 'bottom' | 'left' | 'right';
  showTooltipOnFocus?: boolean;
  keyboardShortcut?: string;
  onKeyboardShortcut?: () => void;
  focusOnMount?: boolean;
  autoFocus?: boolean;
  tabIndex?: number;
}

const StyledButton = styled(Button)(({ theme }) => ({
  // Estilos para foco visível
  '&:focus-visible': {
    outline: `2px solid ${theme.palette.primary.main}`,
    outlineOffset: '2px',
    borderRadius: theme.shape.borderRadius,
  },
  
  // Estilos para hover com contraste adequado
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
    '@media (prefers-reduced-motion: reduce)': {
      transition: 'none',
    },
  },
  
  // Estilos para estados de pressão
  '&:active': {
    transform: 'translateY(1px)',
    '@media (prefers-reduced-motion: reduce)': {
      transform: 'none',
    },
  },
  
  // Suporte a modo de alto contraste
  '@media (prefers-contrast: high)': {
    border: `2px solid ${theme.palette.text.primary}`,
  },
  
  // Suporte a modo escuro
  '@media (prefers-color-scheme: dark)': {
    '&:focus-visible': {
      outline: `2px solid ${theme.palette.primary.light}`,
    },
  },
}));

const AccessibleButton = forwardRef<HTMLButtonElement, AccessibleButtonProps>(
  (
    {
      ariaLabel,
      ariaDescription,
      ariaPressed,
      ariaExpanded,
      ariaControls,
      ariaHaspopup,
      ariaLive,
      tooltipText,
      tooltipPlacement = 'top',
      showTooltipOnFocus = true,
      keyboardShortcut,
      onKeyboardShortcut,
      focusOnMount = false,
      autoFocus = false,
      tabIndex = 0,
      children,
      onClick,
      onKeyDown,
      ...buttonProps
    },
    ref
  ) => {
    const buttonRef = useRef<HTMLButtonElement>(null);
    const mergedRef = (node: HTMLButtonElement) => {
      buttonRef.current = node;
      if (typeof ref === 'function') {
        ref(node);
      } else if (ref) {
        ref.current = node;
      }
    };

    // Focus on mount
    useEffect(() => {
      if (focusOnMount && buttonRef.current) {
        buttonRef.current.focus();
      }
    }, [focusOnMount]);

    // Keyboard shortcut handler
    useEffect(() => {
      if (!keyboardShortcut || !onKeyboardShortcut) return;

      const handleKeyDown = (event: KeyboardEvent) => {
        const isCtrl = event.ctrlKey || event.metaKey;
        const isShift = event.shiftKey;
        const isAlt = event.altKey;

        // Mapear atalhos comuns
        const shortcuts: Record<string, () => void> = {
          'Enter': onKeyboardShortcut,
          ' ': onKeyboardShortcut, // Space
          'Escape': onKeyboardShortcut,
        };

        // Atalhos com modificadores
        if (isCtrl && !isShift && !isAlt) {
          shortcuts['KeyS'] = onKeyboardShortcut; // Ctrl+S
          shortcuts['KeyN'] = onKeyboardShortcut; // Ctrl+N
          shortcuts['KeyO'] = onKeyboardShortcut; // Ctrl+O
        }

        const key = event.code;
        if (shortcuts[key]) {
          event.preventDefault();
          shortcuts[key]();
        }
      };

      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }, [keyboardShortcut, onKeyboardShortcut]);

    // Enhanced click handler with accessibility
    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
      // Anunciar ação para screen readers
      if (ariaLive) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', ariaLive);
        announcement.setAttribute('aria-atomic', 'true');
        announcement.textContent = `${ariaLabel} ativado`;
        announcement.style.position = 'absolute';
        announcement.style.left = '-10000px';
        announcement.style.width = '1px';
        announcement.style.height = '1px';
        announcement.style.overflow = 'hidden';
        
        document.body.appendChild(announcement);
        setTimeout(() => document.body.removeChild(announcement), 1000);
      }

      onClick?.(event);
    };

    // Enhanced key down handler
    const handleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
      // Suporte a navegação por teclado
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        handleClick(event as any);
      }

      // Suporte a Escape para fechar popups
      if (event.key === 'Escape' && ariaHaspopup) {
        event.preventDefault();
        // Implementar lógica de fechamento se necessário
      }

      onKeyDown?.(event);
    };

    // Construir aria-label completo
    const fullAriaLabel = keyboardShortcut 
      ? `${ariaLabel} (${keyboardShortcut})`
      : ariaLabel;

    // Construir tooltip completo
    const fullTooltipText = tooltipText 
      ? `${tooltipText}${keyboardShortcut ? ` - ${keyboardShortcut}` : ''}`
      : keyboardShortcut 
        ? `${ariaLabel} - ${keyboardShortcut}`
        : ariaLabel;

    const buttonElement = (
      <StyledButton
        ref={mergedRef}
        aria-label={fullAriaLabel}
        aria-describedby={ariaDescription ? `${ariaLabel}-description` : undefined}
        aria-pressed={ariaPressed}
        aria-expanded={ariaExpanded}
        aria-controls={ariaControls}
        aria-haspopup={ariaHaspopup}
        aria-live={ariaLive}
        tabIndex={tabIndex}
        autoFocus={autoFocus}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        {...buttonProps}
      >
        {children}
      </StyledButton>
    );

    // Descrição ARIA se fornecida
    if (ariaDescription) {
      return (
        <>
          {buttonElement}
          <div
            id={`${ariaLabel}-description`}
            style={{
              position: 'absolute',
              left: '-10000px',
              width: '1px',
              height: '1px',
              overflow: 'hidden'
            }}
          >
            {ariaDescription}
          </div>
        </>
      );
    }

    // Tooltip se configurado
    if (tooltipText || keyboardShortcut) {
      return (
        <Tooltip
          title={fullTooltipText}
          placement={tooltipPlacement}
          arrow
          enterDelay={showTooltipOnFocus ? 500 : 1000}
          leaveDelay={200}
        >
          {buttonElement}
        </Tooltip>
      );
    }

    return buttonElement;
  }
);

AccessibleButton.displayName = 'AccessibleButton';

export default AccessibleButton; 
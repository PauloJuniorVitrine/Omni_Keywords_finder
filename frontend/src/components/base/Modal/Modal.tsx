import React, { forwardRef, useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '../../../utils/cn';

// Tipos específicos para o sistema Omni Keywords Finder
export interface ModalProps extends React.HTMLAttributes<HTMLDivElement> {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
  showCloseButton?: boolean;
  fullWidth?: boolean;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  preventScroll?: boolean;
}

export const Modal = forwardRef<HTMLDivElement, ModalProps>(
  (
    {
      className,
      isOpen,
      onClose,
      title,
      description,
      size = 'md',
      closeOnOverlayClick = true,
      closeOnEscape = true,
      showCloseButton = true,
      fullWidth = false,
      header,
      footer,
      preventScroll = true,
      children,
      ...props
    },
    ref
  ) => {
    const modalRef = useRef<HTMLDivElement>(null);
    const overlayRef = useRef<HTMLDivElement>(null);
    const [isMounted, setIsMounted] = useState(false);

    // Design tokens específicos do Omni Keywords Finder
    const modalSizes = {
      sm: 'max-w-sm',
      md: 'max-w-md',
      lg: 'max-w-lg',
      xl: 'max-w-xl',
      full: 'max-w-full mx-4'
    };

    // Focus trap e acessibilidade
    useEffect(() => {
      if (isOpen) {
        setIsMounted(true);
        
        if (preventScroll) {
          document.body.style.overflow = 'hidden';
        }

        // Focus no modal quando abrir
        const timer = setTimeout(() => {
          if (modalRef.current) {
            const focusableElements = modalRef.current.querySelectorAll(
              'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const firstElement = focusableElements[0] as HTMLElement;
            if (firstElement) {
              firstElement.focus();
            }
          }
        }, 100);

        return () => clearTimeout(timer);
      } else {
        setIsMounted(false);
        if (preventScroll) {
          document.body.style.overflow = 'unset';
        }
      }
    }, [isOpen, preventScroll]);

    // Gerenciamento de teclas
    useEffect(() => {
      const handleKeyDown = (event: KeyboardEvent) => {
        if (!isOpen) return;

        if (event.key === 'Escape' && closeOnEscape) {
          onClose();
        }

        // Focus trap
        if (event.key === 'Tab' && modalRef.current) {
          const focusableElements = modalRef.current.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          );
          const firstElement = focusableElements[0] as HTMLElement;
          const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

          if (event.shiftKey) {
            if (document.activeElement === firstElement) {
              event.preventDefault();
              lastElement.focus();
            }
          } else {
            if (document.activeElement === lastElement) {
              event.preventDefault();
              firstElement.focus();
            }
          }
        }
      };

      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, closeOnEscape, onClose]);

    // Click no overlay
    const handleOverlayClick = (event: React.MouseEvent) => {
      if (event.target === overlayRef.current && closeOnOverlayClick) {
        onClose();
      }
    };

    if (!isOpen || !isMounted) return null;

    return createPortal(
      <div
        ref={overlayRef}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm"
        onClick={handleOverlayClick}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'modal-title' : undefined}
        aria-describedby={description ? 'modal-description' : undefined}
      >
        <div
          ref={modalRef}
          className={cn(
            'relative bg-white rounded-lg shadow-xl w-full mx-4 max-h-[90vh] overflow-hidden',
            modalSizes[size],
            fullWidth && 'w-full',
            className
          )}
          role="document"
          {...props}
        >
          {/* Header */}
          {(header || title || showCloseButton) && (
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex-1">
                {header ? (
                  header
                ) : (
                  <>
                    {title && (
                      <h2 id="modal-title" className="text-lg font-semibold text-gray-900">
                        {title}
                      </h2>
                    )}
                    {description && (
                      <p id="modal-description" className="mt-1 text-sm text-gray-600">
                        {description}
                      </p>
                    )}
                  </>
                )}
              </div>
              
              {showCloseButton && (
                <button
                  type="button"
                  className="ml-4 p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md"
                  onClick={onClose}
                  aria-label="Fechar modal"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          )}

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
            {children}
          </div>

          {/* Footer */}
          {footer && (
            <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
              {footer}
            </div>
          )}
        </div>
      </div>,
      document.body
    );
  }
);

Modal.displayName = 'Modal';

// Hook para facilitar o uso do modal
export const useModal = (initialState = false) => {
  const [isOpen, setIsOpen] = useState(initialState);

  const open = () => setIsOpen(true);
  const close = () => setIsOpen(false);
  const toggle = () => setIsOpen(!isOpen);

  return {
    isOpen,
    open,
    close,
    toggle
  };
}; 
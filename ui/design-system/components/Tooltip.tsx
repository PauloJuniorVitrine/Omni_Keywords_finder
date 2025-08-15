import React, { useState, useRef, useEffect } from 'react';

export type TooltipPosition = 'top' | 'bottom' | 'left' | 'right' | 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';

export type TooltipVariant = 'default' | 'light' | 'dark';

export interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  position?: TooltipPosition;
  variant?: TooltipVariant;
  delay?: number;
  disabled?: boolean;
  className?: string;
}

const getTooltipClasses = (
  position: TooltipPosition = 'top',
  variant: TooltipVariant = 'default'
): string => {
  const baseClasses = [
    'absolute z-50 px-3 py-2 text-sm font-medium rounded-md shadow-lg',
    'pointer-events-none transition-opacity duration-200',
    'max-w-xs break-words'
  ];

  const variantClasses = {
    default: 'bg-secondary-900 text-white',
    light: 'bg-white text-secondary-900 border border-secondary-200',
    dark: 'bg-black text-white'
  };

  const positionClasses = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2',
    'top-left': 'bottom-full right-0 mb-2',
    'top-right': 'bottom-full left-0 mb-2',
    'bottom-left': 'top-full right-0 mt-2',
    'bottom-right': 'top-full left-0 mt-2'
  };

  return [
    ...baseClasses,
    variantClasses[variant],
    positionClasses[position]
  ].join(' ');
};

const getArrowClasses = (
  position: TooltipPosition = 'top',
  variant: TooltipVariant = 'default'
): string => {
  const baseClasses = 'absolute w-2 h-2 transform rotate-45';

  const variantClasses = {
    default: 'bg-secondary-900',
    light: 'bg-white border border-secondary-200',
    dark: 'bg-black'
  };

  const positionClasses = {
    top: 'top-full left-1/2 transform -translate-x-1/2 -mt-1',
    bottom: 'bottom-full left-1/2 transform -translate-x-1/2 -mb-1',
    left: 'left-full top-1/2 transform -translate-y-1/2 -ml-1',
    right: 'right-full top-1/2 transform -translate-y-1/2 -mr-1',
    'top-left': 'top-full right-4 -mt-1',
    'top-right': 'top-full left-4 -mt-1',
    'bottom-left': 'bottom-full right-4 -mb-1',
    'bottom-right': 'bottom-full left-4 -mb-1'
  };

  return [
    baseClasses,
    variantClasses[variant],
    positionClasses[position]
  ].join(' ');
};

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = 'top',
  variant = 'default',
  delay = 200,
  disabled = false,
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (isVisible) {
      setIsMounted(true);
    } else {
      const timer = setTimeout(() => {
        setIsMounted(false);
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [isVisible]);

  const showTooltip = () => {
    if (disabled) return;
    
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return (
    <div
      ref={triggerRef}
      className={`relative inline-block ${className}`}
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
      onFocus={showTooltip}
      onBlur={hideTooltip}
    >
      {children}
      
      {isMounted && (
        <div
          ref={tooltipRef}
          className={`${getTooltipClasses(position, variant)} ${
            isVisible ? 'opacity-100' : 'opacity-0'
          }`}
          role="tooltip"
          aria-hidden={!isVisible}
        >
          {content}
          <div className={getArrowClasses(position, variant)} />
        </div>
      )}
    </div>
  );
};

// Tooltip Provider Component
interface TooltipProviderProps {
  children: React.ReactNode;
  delayDuration?: number;
  skipDelayDuration?: number;
}

export const TooltipProvider: React.FC<TooltipProviderProps> = ({
  children,
  delayDuration = 200,
  skipDelayDuration = 300
}) => {
  return (
    <div className="tooltip-provider">
      {children}
    </div>
  );
};

// Tooltip Trigger Component
interface TooltipTriggerProps {
  children: React.ReactNode;
  asChild?: boolean;
  className?: string;
}

export const TooltipTrigger: React.FC<TooltipTriggerProps> = ({
  children,
  asChild = false,
  className = ''
}) => {
  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children, {
      className: `${children.props.className || ''} ${className}`.trim()
    });
  }

  return (
    <div className={className}>
      {children}
    </div>
  );
};

// Tooltip Content Component
interface TooltipContentProps {
  children: React.ReactNode;
  position?: TooltipPosition;
  variant?: TooltipVariant;
  className?: string;
}

export const TooltipContent: React.FC<TooltipContentProps> = ({
  children,
  position = 'top',
  variant = 'default',
  className = ''
}) => {
  return (
    <div
      className={`${getTooltipClasses(position, variant)} ${className}`}
      role="tooltip"
    >
      {children}
      <div className={getArrowClasses(position, variant)} />
    </div>
  );
};

// Info Tooltip Component
interface InfoTooltipProps {
  children: React.ReactNode;
  content: React.ReactNode;
  position?: TooltipPosition;
  className?: string;
}

export const InfoTooltip: React.FC<InfoTooltipProps> = ({
  children,
  content,
  position = 'top',
  className = ''
}) => {
  return (
    <Tooltip
      content={content}
      position={position}
      variant="light"
      className={className}
    >
      {children}
    </Tooltip>
  );
};

// Help Tooltip Component
interface HelpTooltipProps {
  content: React.ReactNode;
  position?: TooltipPosition;
  className?: string;
}

export const HelpTooltip: React.FC<HelpTooltipProps> = ({
  content,
  position = 'top',
  className = ''
}) => {
  return (
    <Tooltip
      content={content}
      position={position}
      variant="light"
      className={className}
    >
      <button
        type="button"
        className="inline-flex items-center justify-center w-4 h-4 text-secondary-400 hover:text-secondary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 rounded-full"
        aria-label="Help"
      >
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
        </svg>
      </button>
    </Tooltip>
  );
};

// Error Tooltip Component
interface ErrorTooltipProps {
  children: React.ReactNode;
  error: string;
  position?: TooltipPosition;
  className?: string;
}

export const ErrorTooltip: React.FC<ErrorTooltipProps> = ({
  children,
  error,
  position = 'top',
  className = ''
}) => {
  return (
    <Tooltip
      content={
        <div className="flex items-center space-x-2">
          <svg className="w-4 h-4 text-error-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <span>{error}</span>
        </div>
      }
      position={position}
      variant="dark"
      className={className}
    >
      {children}
    </Tooltip>
  );
}; 
import React, { useState } from 'react';

export type AlertVariant = 'info' | 'success' | 'warning' | 'error';

export type AlertSize = 'sm' | 'md' | 'lg';

export interface AlertProps {
  variant?: AlertVariant;
  size?: AlertSize;
  title?: string;
  children: React.ReactNode;
  dismissible?: boolean;
  onDismiss?: () => void;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

const getAlertClasses = (
  variant: AlertVariant = 'info',
  size: AlertSize = 'md'
): string => {
  const baseClasses = [
    'rounded-lg border p-4',
    'flex items-start space-x-3'
  ];

  const variantClasses = {
    info: [
      'bg-primary-50 border-primary-200',
      'text-primary-800'
    ],
    success: [
      'bg-success-50 border-success-200',
      'text-success-800'
    ],
    warning: [
      'bg-warning-50 border-warning-200',
      'text-warning-800'
    ],
    error: [
      'bg-error-50 border-error-200',
      'text-error-800'
    ]
  };

  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return [
    ...baseClasses,
    ...variantClasses[variant],
    sizeClasses[size]
  ].join(' ');
};

const getDefaultIcon = (variant: AlertVariant): React.ReactNode => {
  const iconClasses = 'w-5 h-5 flex-shrink-0';
  
  switch (variant) {
    case 'info':
      return (
        <svg className={iconClasses} fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
        </svg>
      );
    case 'success':
      return (
        <svg className={iconClasses} fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      );
    case 'warning':
      return (
        <svg className={iconClasses} fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      );
    case 'error':
      return (
        <svg className={iconClasses} fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      );
    default:
      return null;
  }
};

export const Alert: React.FC<AlertProps> = ({
  variant = 'info',
  size = 'md',
  title,
  children,
  dismissible = false,
  onDismiss,
  icon,
  action,
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(true);

  const handleDismiss = () => {
    setIsVisible(false);
    onDismiss?.();
  };

  if (!isVisible) return null;

  const alertClasses = getAlertClasses(variant, size);
  const defaultIcon = getDefaultIcon(variant);

  return (
    <div className={`${alertClasses} ${className}`}>
      {(icon || defaultIcon) && (
        <div className="flex-shrink-0">
          {icon || defaultIcon}
        </div>
      )}
      
      <div className="flex-1 min-w-0">
        {title && (
          <h3 className="font-medium mb-1">
            {title}
          </h3>
        )}
        
        <div className="text-sm">
          {children}
        </div>
      </div>
      
      <div className="flex items-center space-x-2">
        {action && (
          <div className="flex-shrink-0">
            {action}
          </div>
        )}
        
        {dismissible && (
          <button
            onClick={handleDismiss}
            className="flex-shrink-0 p-1 rounded-md hover:bg-black hover:bg-opacity-10 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current"
            aria-label="Dismiss alert"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

// Alert Banner Component
interface AlertBannerProps extends Omit<AlertProps, 'size'> {
  children: React.ReactNode;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <div className={`w-full ${className}`}>
      <Alert {...props}>
        {children}
      </Alert>
    </div>
  );
};

// Alert Toast Component
interface AlertToastProps extends AlertProps {
  duration?: number;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
}

export const AlertToast: React.FC<AlertToastProps> = ({
  duration = 5000,
  position = 'top-right',
  className = '',
  ...props
}) => {
  const [isVisible, setIsVisible] = useState(true);

  React.useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration]);

  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2'
  };

  if (!isVisible) return null;

  return (
    <div className={`fixed z-50 max-w-sm ${positionClasses[position]} ${className}`}>
      <Alert {...props} dismissible onDismiss={() => setIsVisible(false)} />
    </div>
  );
};

// Toast Container Component
interface ToastContainerProps {
  children: React.ReactNode;
  position?: AlertToastProps['position'];
  className?: string;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({
  children,
  position = 'top-right',
  className = ''
}) => {
  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2'
  };

  return (
    <div className={`fixed z-50 space-y-2 ${positionClasses[position]} ${className}`}>
      {children}
    </div>
  );
};

// Alert Group Component
interface AlertGroupProps {
  children: React.ReactNode;
  className?: string;
}

export const AlertGroup: React.FC<AlertGroupProps> = ({
  children,
  className = ''
}) => {
  return (
    <div className={`space-y-4 ${className}`}>
      {children}
    </div>
  );
};

// Status Alert Component
interface StatusAlertProps {
  status: 'idle' | 'loading' | 'success' | 'error';
  loadingText?: string;
  successText?: string;
  errorText?: string;
  className?: string;
}

export const StatusAlert: React.FC<StatusAlertProps> = ({
  status,
  loadingText = 'Loading...',
  successText = 'Operation completed successfully',
  errorText = 'An error occurred',
  className = ''
}) => {
  if (status === 'idle') return null;

  const alertProps = {
    loading: {
      variant: 'info' as const,
      children: loadingText
    },
    success: {
      variant: 'success' as const,
      children: successText
    },
    error: {
      variant: 'error' as const,
      children: errorText
    }
  };

  return (
    <Alert
      {...alertProps[status]}
      className={className}
    />
  );
}; 
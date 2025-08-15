import React, { forwardRef, useState } from 'react';

export type FormVariant = 'default' | 'outlined' | 'filled';

export type FormSize = 'sm' | 'md' | 'lg';

export interface FormProps extends React.FormHTMLAttributes<HTMLFormElement> {
  variant?: FormVariant;
  size?: FormSize;
  children: React.ReactNode;
  onSubmit?: (data: any) => void;
}

const getFormClasses = (
  variant: FormVariant = 'default',
  size: FormSize = 'md'
): string => {
  const baseClasses = [
    'space-y-6'
  ];

  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return [
    ...baseClasses,
    sizeClasses[size]
  ].join(' ');
};

export const Form = forwardRef<HTMLFormElement, FormProps>(
  (
    {
      variant = 'default',
      size = 'md',
      children,
      onSubmit,
      className = '',
      ...props
    },
    ref
  ) => {
    const formClasses = getFormClasses(variant, size);

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      if (onSubmit) {
        const formData = new FormData(event.currentTarget);
        const data = Object.fromEntries(formData);
        onSubmit(data);
      }
    };

    return (
      <form
        ref={ref}
        className={`${formClasses} ${className}`}
        onSubmit={handleSubmit}
        {...props}
      >
        {children}
      </form>
    );
  }
);

Form.displayName = 'Form';

// Form Field Component
interface FormFieldProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  label?: string;
  required?: boolean;
  error?: string;
  helpText?: string;
  disabled?: boolean;
}

export const FormField: React.FC<FormFieldProps> = ({
  children,
  label,
  required = false,
  error,
  helpText,
  disabled = false,
  className = '',
  ...props
}) => {
  return (
    <div className={`space-y-2 ${className}`} {...props}>
      {label && (
        <label className="block text-sm font-medium text-secondary-700">
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
      )}
      
      <div className={disabled ? 'opacity-50 pointer-events-none' : ''}>
        {children}
      </div>
      
      {error && (
        <p className="text-sm text-error-600">{error}</p>
      )}
      
      {helpText && !error && (
        <p className="text-sm text-secondary-500">{helpText}</p>
      )}
    </div>
  );
};

// Input Component
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: FormVariant;
  size?: FormSize;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  error?: boolean;
}

const getInputClasses = (
  variant: FormVariant = 'default',
  size: FormSize = 'md',
  error: boolean = false,
  hasLeftIcon: boolean = false,
  hasRightIcon: boolean = false
): string => {
  const baseClasses = [
    'w-full transition-colors duration-200',
    'focus:outline-none focus:ring-2 focus:ring-offset-0',
    'disabled:opacity-50 disabled:cursor-not-allowed'
  ];

  const variantClasses = {
    default: [
      'border border-secondary-300',
      'focus:border-primary-500 focus:ring-primary-500',
      'hover:border-secondary-400'
    ],
    outlined: [
      'border-2 border-secondary-300',
      'focus:border-primary-500 focus:ring-primary-500',
      'hover:border-secondary-400'
    ],
    filled: [
      'border border-transparent bg-secondary-50',
      'focus:bg-white focus:border-primary-500 focus:ring-primary-500',
      'hover:bg-secondary-100'
    ]
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  const errorClasses = error ? [
    'border-error-300',
    'focus:border-error-500 focus:ring-error-500',
    'hover:border-error-400'
  ] : [];

  const iconClasses = [
    hasLeftIcon ? 'pl-10' : '',
    hasRightIcon ? 'pr-10' : ''
  ].filter(Boolean);

  return [
    ...baseClasses,
    ...variantClasses[variant],
    sizeClasses[size],
    ...errorClasses,
    ...iconClasses
  ].join(' ');
};

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      variant = 'default',
      size = 'md',
      leftIcon,
      rightIcon,
      error = false,
      className = '',
      ...props
    },
    ref
  ) => {
    const inputClasses = getInputClasses(variant, size, error, !!leftIcon, !!rightIcon);

    return (
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400">
            {leftIcon}
          </div>
        )}
        
        <input
          ref={ref}
          className={`${inputClasses} rounded-md ${className}`}
          {...props}
        />
        
        {rightIcon && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-secondary-400">
            {rightIcon}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

// Textarea Component
interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  variant?: FormVariant;
  size?: FormSize;
  error?: boolean;
  rows?: number;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      variant = 'default',
      size = 'md',
      error = false,
      rows = 3,
      className = '',
      ...props
    },
    ref
  ) => {
    const textareaClasses = getInputClasses(variant, size, error);

    return (
      <textarea
        ref={ref}
        rows={rows}
        className={`${textareaClasses} rounded-md resize-vertical ${className}`}
        {...props}
      />
    );
  }
);

Textarea.displayName = 'Textarea';

// Select Component
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  variant?: FormVariant;
  size?: FormSize;
  error?: boolean;
  options: Array<{ value: string; label: string; disabled?: boolean }>;
  placeholder?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      variant = 'default',
      size = 'md',
      error = false,
      options,
      placeholder,
      className = '',
      ...props
    },
    ref
  ) => {
    const selectClasses = getInputClasses(variant, size, error);

    return (
      <select
        ref={ref}
        className={`${selectClasses} rounded-md ${className}`}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        
        {options.map((option) => (
          <option
            key={option.value}
            value={option.value}
            disabled={option.disabled}
          >
            {option.label}
          </option>
        ))}
      </select>
    );
  }
);

Select.displayName = 'Select';

// Checkbox Component
interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  error?: boolean;
  size?: FormSize;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  (
    {
      label,
      error = false,
      size = 'md',
      className = '',
      ...props
    },
    ref
  ) => {
    const sizeClasses = {
      sm: 'w-4 h-4',
      md: 'w-5 h-5',
      lg: 'w-6 h-6'
    };

    return (
      <div className="flex items-center space-x-3">
        <input
          ref={ref}
          type="checkbox"
          className={`${sizeClasses[size]} text-primary-600 border-secondary-300 rounded focus:ring-primary-500 ${className}`}
          {...props}
        />
        
        {label && (
          <label className="text-sm text-secondary-700">
            {label}
          </label>
        )}
      </div>
    );
  }
);

Checkbox.displayName = 'Checkbox';

// Radio Component
interface RadioProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  error?: boolean;
  size?: FormSize;
}

export const Radio = forwardRef<HTMLInputElement, RadioProps>(
  (
    {
      label,
      error = false,
      size = 'md',
      className = '',
      ...props
    },
    ref
  ) => {
    const sizeClasses = {
      sm: 'w-4 h-4',
      md: 'w-5 h-5',
      lg: 'w-6 h-6'
    };

    return (
      <div className="flex items-center space-x-3">
        <input
          ref={ref}
          type="radio"
          className={`${sizeClasses[size]} text-primary-600 border-secondary-300 focus:ring-primary-500 ${className}`}
          {...props}
        />
        
        {label && (
          <label className="text-sm text-secondary-700">
            {label}
          </label>
        )}
      </div>
    );
  }
);

Radio.displayName = 'Radio';

// Radio Group Component
interface RadioGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  name: string;
  value?: string;
  onChange?: (value: string) => void;
  options: Array<{ value: string; label: string; disabled?: boolean }>;
  error?: boolean;
  size?: FormSize;
}

export const RadioGroup: React.FC<RadioGroupProps> = ({
  name,
  value,
  onChange,
  options,
  error = false,
  size = 'md',
  className = '',
  ...props
}) => {
  return (
    <div className={`space-y-3 ${className}`} {...props}>
      {options.map((option) => (
        <Radio
          key={option.value}
          name={name}
          value={option.value}
          label={option.label}
          checked={value === option.value}
          onChange={(e) => onChange?.(e.target.value)}
          disabled={option.disabled}
          size={size}
        />
      ))}
    </div>
  );
};

// Form Actions Component
interface FormActionsProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  align?: 'left' | 'center' | 'right';
}

export const FormActions: React.FC<FormActionsProps> = ({
  children,
  align = 'right',
  className = '',
  ...props
}) => {
  const alignClasses = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end'
  };

  return (
    <div
      className={`flex items-center gap-3 pt-6 ${alignClasses[align]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

// Form Section Component
interface FormSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  title?: string;
  description?: string;
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

export const FormSection: React.FC<FormSectionProps> = ({
  children,
  title,
  description,
  collapsible = false,
  defaultExpanded = true,
  className = '',
  ...props
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  if (!title && !collapsible) {
    return (
      <div className={`space-y-4 ${className}`} {...props}>
        {children}
      </div>
    );
  }

  return (
    <div className={`border border-secondary-200 rounded-lg ${className}`} {...props}>
      {(title || collapsible) && (
        <div
          className={`px-6 py-4 border-b border-secondary-200 ${
            collapsible ? 'cursor-pointer' : ''
          }`}
          onClick={collapsible ? () => setIsExpanded(!isExpanded) : undefined}
        >
          <div className="flex items-center justify-between">
            <div>
              {title && (
                <h3 className="text-lg font-medium text-secondary-900">
                  {title}
                </h3>
              )}
              {description && (
                <p className="text-sm text-secondary-600 mt-1">
                  {description}
                </p>
              )}
            </div>
            
            {collapsible && (
              <svg
                className={`w-5 h-5 text-secondary-400 transition-transform ${
                  isExpanded ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            )}
          </div>
        </div>
      )}
      
      {(!collapsible || isExpanded) && (
        <div className="p-6 space-y-4">
          {children}
        </div>
      )}
    </div>
  );
}; 
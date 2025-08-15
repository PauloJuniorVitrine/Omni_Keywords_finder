import React, { useState, useEffect } from 'react';
import { Form, FormField, Input, Textarea, Select, Checkbox, Radio, RadioGroup, FormActions, FormSection } from '../../../ui/design-system/components/Form';
import { Button } from '../../../ui/design-system/components/Button';
import { Card, CardHeader, CardBody, CardTitle } from '../../../ui/design-system/components/Card';
import { Loading } from '../../../ui/design-system/components/Loading';
import { Alert } from '../../../ui/design-system/components/Alert';

export interface FormFieldConfig {
  id: string;
  type: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'textarea' | 'select' | 'checkbox' | 'radio' | 'date' | 'file' | 'custom';
  label: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  validation?: {
    pattern?: string;
    minLength?: number;
    maxLength?: number;
    min?: number;
    max?: number;
    custom?: (value: any) => string | null;
  };
  options?: Array<{ value: string; label: string; disabled?: boolean }>;
  helpText?: string;
  defaultValue?: any;
  component?: React.ComponentType<any>;
}

export interface FormSectionConfig {
  id: string;
  title: string;
  description?: string;
  fields: FormFieldConfig[];
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

export interface FormConfig {
  id: string;
  title?: string;
  subtitle?: string;
  sections: FormSectionConfig[];
  submitText?: string;
  cancelText?: string;
  showCancel?: boolean;
  onSubmit?: (data: any) => void | Promise<void>;
  onCancel?: () => void;
  onValidate?: (data: any) => Record<string, string> | null;
  autoSave?: boolean;
  autoSaveInterval?: number;
  className?: string;
}

export interface Form_v2Props extends FormConfig {
  initialData?: Record<string, any>;
  loading?: boolean;
  error?: string;
  success?: string;
}

const validateField = (field: FormFieldConfig, value: any): string | null => {
  // Required validation
  if (field.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
    return `${field.label} is required`;
  }

  if (!value) return null;

  // Pattern validation
  if (field.validation?.pattern && !new RegExp(field.validation.pattern).test(value)) {
    return `${field.label} format is invalid`;
  }

  // Length validation
  if (field.validation?.minLength && value.length < field.validation.minLength) {
    return `${field.label} must be at least ${field.validation.minLength} characters`;
  }

  if (field.validation?.maxLength && value.length > field.validation.maxLength) {
    return `${field.label} must be no more than ${field.validation.maxLength} characters`;
  }

  // Number validation
  if (field.type === 'number') {
    const numValue = Number(value);
    if (field.validation?.min !== undefined && numValue < field.validation.min) {
      return `${field.label} must be at least ${field.validation.min}`;
    }
    if (field.validation?.max !== undefined && numValue > field.validation.max) {
      return `${field.label} must be no more than ${field.validation.max}`;
    }
  }

  // Custom validation
  if (field.validation?.custom) {
    return field.validation.custom(value);
  }

  return null;
};

const renderField = (
  field: FormFieldConfig,
  value: any,
  onChange: (value: any) => void,
  error?: string
) => {
  const commonProps = {
    value: value || '',
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const newValue = field.type === 'checkbox' ? e.target.checked : e.target.value;
      onChange(newValue);
    },
    disabled: field.disabled,
    error: !!error
  };

  switch (field.type) {
    case 'textarea':
      return (
        <Textarea
          {...commonProps}
          placeholder={field.placeholder}
          rows={4}
        />
      );

    case 'select':
      return (
        <Select
          {...commonProps}
          options={field.options || []}
          placeholder={field.placeholder}
        />
      );

    case 'checkbox':
      return (
        <Checkbox
          checked={value || false}
          onChange={(e) => onChange(e.target.checked)}
          label={field.label}
          disabled={field.disabled}
        />
      );

    case 'radio':
      return (
        <Radio
          {...commonProps}
          label={field.label}
        />
      );

    case 'custom':
      return field.component ? (
        <field.component
          value={value}
          onChange={onChange}
          disabled={field.disabled}
          error={error}
        />
      ) : null;

    default:
      return (
        <Input
          {...commonProps}
          type={field.type}
          placeholder={field.placeholder}
        />
      );
  }
};

const FormSectionComponent: React.FC<{
  section: FormSectionConfig;
  data: Record<string, any>;
  errors: Record<string, string>;
  onChange: (fieldId: string, value: any) => void;
}> = ({ section, data, errors, onChange }) => {
  return (
    <FormSection
      title={section.title}
      description={section.description}
      collapsible={section.collapsible}
      defaultExpanded={section.defaultExpanded}
    >
      <div className="space-y-6">
        {section.fields.map(field => (
          <FormField
            key={field.id}
            label={field.label}
            required={field.required}
            error={errors[field.id]}
            helpText={field.helpText}
            disabled={field.disabled}
          >
            {renderField(
              field,
              data[field.id],
              (value) => onChange(field.id, value),
              errors[field.id]
            )}
          </FormField>
        ))}
      </div>
    </FormSection>
  );
};

export const Form_v2: React.FC<Form_v2Props> = ({
  id,
  title,
  subtitle,
  sections,
  submitText = 'Submit',
  cancelText = 'Cancel',
  showCancel = true,
  onSubmit,
  onCancel,
  onValidate,
  autoSave = false,
  autoSaveInterval = 30000,
  initialData = {},
  loading = false,
  error,
  success,
  className = ''
}) => {
  const [data, setData] = useState<Record<string, any>>(initialData);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  // Auto-save effect
  useEffect(() => {
    if (!autoSave) return;

    const interval = setInterval(() => {
      if (Object.keys(data).length > 0) {
        // Auto-save logic here
        setLastSaved(new Date());
        console.log('Auto-saved form data:', data);
      }
    }, autoSaveInterval);

    return () => clearInterval(interval);
  }, [autoSave, autoSaveInterval, data]);

  const validateForm = (): Record<string, string> => {
    const newErrors: Record<string, string> = {};

    sections.forEach(section => {
      section.fields.forEach(field => {
        const error = validateField(field, data[field.id]);
        if (error) {
          newErrors[field.id] = error;
        }
      });
    });

    // Custom validation
    if (onValidate) {
      const customErrors = onValidate(data);
      if (customErrors) {
        Object.assign(newErrors, customErrors);
      }
    }

    return newErrors;
  };

  const handleFieldChange = (fieldId: string, value: any) => {
    setData(prev => ({ ...prev, [fieldId]: value }));
    setTouched(prev => ({ ...prev, [fieldId]: true }));

    // Clear error when user starts typing
    if (errors[fieldId]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[fieldId];
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const newErrors = validateForm();
    setErrors(newErrors);

    if (Object.keys(newErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      if (onSubmit) {
        await onSubmit(data);
      }
    } catch (err) {
      console.error('Form submission error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
  };

  const resetForm = () => {
    setData(initialData);
    setErrors({});
    setTouched({});
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading variant="spinner" size="lg" text="Loading form..." />
      </div>
    );
  }

  return (
    <Card className={className}>
      {(title || subtitle) && (
        <CardHeader>
          <div>
            {title && <CardTitle>{title}</CardTitle>}
            {subtitle && <p className="text-sm text-secondary-600 mt-1">{subtitle}</p>}
          </div>
        </CardHeader>
      )}

      <CardBody>
        {/* Status Messages */}
        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        {success && (
          <Alert variant="success" className="mb-6">
            {success}
          </Alert>
        )}

        {autoSave && lastSaved && (
          <Alert variant="info" className="mb-6">
            Last saved: {lastSaved.toLocaleTimeString()}
          </Alert>
        )}

        {/* Form */}
        <Form onSubmit={handleSubmit} className="space-y-8">
          {sections.map(section => (
            <FormSectionComponent
              key={section.id}
              section={section}
              data={data}
              errors={errors}
              onChange={handleFieldChange}
            />
          ))}

          {/* Form Actions */}
          <FormActions>
            {showCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={handleCancel}
                disabled={isSubmitting}
              >
                {cancelText}
              </Button>
            )}
            
            <div className="flex space-x-2">
              <Button
                type="button"
                variant="ghost"
                onClick={resetForm}
                disabled={isSubmitting}
              >
                Reset
              </Button>
              
              <Button
                type="submit"
                variant="primary"
                loading={isSubmitting}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : submitText}
              </Button>
            </div>
          </FormActions>
        </Form>
      </CardBody>
    </Card>
  );
};

// Form Builder Component
export interface FormBuilderProps {
  config: FormConfig;
  onConfigChange: (config: FormConfig) => void;
}

export const FormBuilder: React.FC<FormBuilderProps> = ({ config, onConfigChange }) => {
  const addField = (sectionId: string, field: FormFieldConfig) => {
    const updatedConfig = {
      ...config,
      sections: config.sections.map(section =>
        section.id === sectionId
          ? { ...section, fields: [...section.fields, field] }
          : section
      )
    };
    onConfigChange(updatedConfig);
  };

  const removeField = (sectionId: string, fieldId: string) => {
    const updatedConfig = {
      ...config,
      sections: config.sections.map(section =>
        section.id === sectionId
          ? { ...section, fields: section.fields.filter(field => field.id !== fieldId) }
          : section
      )
    };
    onConfigChange(updatedConfig);
  };

  const updateField = (sectionId: string, fieldId: string, updates: Partial<FormFieldConfig>) => {
    const updatedConfig = {
      ...config,
      sections: config.sections.map(section =>
        section.id === sectionId
          ? {
              ...section,
              fields: section.fields.map(field =>
                field.id === fieldId ? { ...field, ...updates } : field
              )
            }
          : section
      )
    };
    onConfigChange(updatedConfig);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Form Builder</h3>
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            const newSection: FormSectionConfig = {
              id: `section-${Date.now()}`,
              title: 'New Section',
              fields: []
            };
            onConfigChange({
              ...config,
              sections: [...config.sections, newSection]
            });
          }}
        >
          Add Section
        </Button>
      </div>

      {config.sections.map(section => (
        <Card key={section.id} variant="outlined">
          <CardHeader>
            <CardTitle>{section.title}</CardTitle>
          </CardHeader>
          <CardBody>
            <div className="space-y-4">
              {section.fields.map(field => (
                <div key={field.id} className="flex items-center justify-between p-3 border border-secondary-200 rounded">
                  <span>{field.label}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeField(section.id, field.id)}
                  >
                    Remove
                  </Button>
                </div>
              ))}
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  const newField: FormFieldConfig = {
                    id: `field-${Date.now()}`,
                    type: 'text',
                    label: 'New Field',
                    required: false
                  };
                  addField(section.id, newField);
                }}
              >
                Add Field
              </Button>
            </div>
          </CardBody>
        </Card>
      ))}
    </div>
  );
};

// Form Hook
export const useForm = (initialData: Record<string, any> = {}) => {
  const [data, setData] = useState<Record<string, any>>(initialData);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const setFieldValue = (fieldId: string, value: any) => {
    setData(prev => ({ ...prev, [fieldId]: value }));
  };

  const setFieldError = (fieldId: string, error: string) => {
    setErrors(prev => ({ ...prev, [fieldId]: error }));
  };

  const validateField = (fieldId: string, value: any, rules: any) => {
    // Field validation logic
    return null;
  };

  const submit = async (submitFunction: (data: any) => Promise<void>) => {
    setIsSubmitting(true);
    try {
      await submitFunction(data);
    } finally {
      setIsSubmitting(false);
    }
  };

  const reset = () => {
    setData(initialData);
    setErrors({});
  };

  return {
    data,
    errors,
    isSubmitting,
    setFieldValue,
    setFieldError,
    validateField,
    submit,
    reset
  };
}; 
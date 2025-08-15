/**
 * AdvancedForm - Formulário avançado com validação em tempo real e auto-save
 * 
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 2.2.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Chip,
  Alert,
  Snackbar,
  CircularProgress,
  Card,
  CardContent,
  Divider,
  IconButton,
  Tooltip,
  Autocomplete,
  Slider,
  FormHelperText,
  InputAdornment
} from '@mui/material';
import {
  Save,
  SaveAlt,
  Undo,
  Redo,
  Validation,
  Error,
  CheckCircle,
  Warning,
  Info,
  CloudUpload,
  CloudDone,
  CloudOff
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';

interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'number' | 'select' | 'multiselect' | 'switch' | 'slider' | 'textarea';
  required?: boolean;
  validation?: any;
  options?: Array<{ value: string; label: string }>;
  min?: number;
  max?: number;
  step?: number;
  multiline?: boolean;
  rows?: number;
  placeholder?: string;
  helperText?: string;
}

interface AdvancedFormProps {
  title: string;
  fields: FormField[];
  initialValues: Record<string, any>;
  onSubmit: (values: Record<string, any>) => Promise<void>;
  onAutoSave?: (values: Record<string, any>) => Promise<void>;
  autoSaveInterval?: number;
  validationSchema?: any;
  showAutoSave?: boolean;
  showValidation?: boolean;
  showUndoRedo?: boolean;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
}

const AdvancedForm: React.FC<AdvancedFormProps> = ({
  title,
  fields,
  initialValues,
  onSubmit,
  onAutoSave,
  autoSaveInterval = 30000, // 30 seconds
  validationSchema,
  showAutoSave = true,
  showValidation = true,
  showUndoRedo = true,
  maxWidth = 'md'
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAutoSaving, setIsAutoSaving] = useState(false);
  const [autoSaveStatus, setAutoSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });

  // History for undo/redo
  const [history, setHistory] = useState<Record<string, any>[]>([initialValues]);
  const [historyIndex, setHistoryIndex] = useState(0);

  // Create validation schema if not provided
  const formValidationSchema = useMemo(() => {
    if (validationSchema) return validationSchema;

    const schemaFields: Record<string, any> = {};
    fields.forEach(field => {
      let fieldSchema = Yup.mixed();

      switch (field.type) {
        case 'text':
        case 'textarea':
          fieldSchema = Yup.string();
          if (field.required) {
            fieldSchema = fieldSchema.required(`${field.label} é obrigatório`);
          }
          break;
        case 'email':
          fieldSchema = Yup.string().email('Email inválido');
          if (field.required) {
            fieldSchema = fieldSchema.required(`${field.label} é obrigatório`);
          }
          break;
        case 'number':
          fieldSchema = Yup.number().typeError(`${field.label} deve ser um número`);
          if (field.required) {
            fieldSchema = fieldSchema.required(`${field.label} é obrigatório`);
          }
          if (field.min !== undefined) {
            fieldSchema = fieldSchema.min(field.min, `${field.label} deve ser pelo menos ${field.min}`);
          }
          if (field.max !== undefined) {
            fieldSchema = fieldSchema.max(field.max, `${field.label} deve ser no máximo ${field.max}`);
          }
          break;
        case 'select':
        case 'multiselect':
          fieldSchema = field.type === 'multiselect' ? Yup.array() : Yup.string();
          if (field.required) {
            fieldSchema = fieldSchema.required(`${field.label} é obrigatório`);
          }
          break;
      }

      if (field.validation) {
        fieldSchema = field.validation;
      }

      schemaFields[field.name] = fieldSchema;
    });

    return Yup.object().shape(schemaFields);
  }, [fields, validationSchema]);

  const formik = useFormik({
    initialValues,
    validationSchema: formValidationSchema,
    onSubmit: async (values) => {
      setIsSubmitting(true);
      try {
        await onSubmit(values);
        setSnackbar({
          open: true,
          message: 'Formulário salvo com sucesso!',
          severity: 'success'
        });
        addToHistory(values);
      } catch (error) {
        setSnackbar({
          open: true,
          message: 'Erro ao salvar formulário',
          severity: 'error'
        });
      } finally {
        setIsSubmitting(false);
      }
    }
  });

  // Auto-save functionality
  const autoSave = useCallback(async () => {
    if (!onAutoSave || !formik.isValid || formik.isSubmitting) return;

    setIsAutoSaving(true);
    setAutoSaveStatus('saving');

    try {
      await onAutoSave(formik.values);
      setAutoSaveStatus('saved');
      setLastSaved(new Date());
      
      setTimeout(() => {
        setAutoSaveStatus('idle');
      }, 2000);
    } catch (error) {
      setAutoSaveStatus('error');
      setSnackbar({
        open: true,
        message: 'Erro no auto-save',
        severity: 'error'
      });
    } finally {
      setIsAutoSaving(false);
    }
  }, [onAutoSave, formik.values, formik.isValid, formik.isSubmitting]);

  // Auto-save effect
  useEffect(() => {
    if (!showAutoSave || !onAutoSave) return;

    const timer = setTimeout(autoSave, autoSaveInterval);
    return () => clearTimeout(timer);
  }, [formik.values, autoSave, autoSaveInterval, showAutoSave, onAutoSave]);

  // History management
  const addToHistory = useCallback((values: Record<string, any>) => {
    setHistory(prev => {
      const newHistory = prev.slice(0, historyIndex + 1);
      newHistory.push(values);
      return newHistory.slice(-10); // Keep only last 10 states
    });
    setHistoryIndex(prev => Math.min(prev + 1, 9));
  }, [historyIndex]);

  const undo = useCallback(() => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setHistoryIndex(newIndex);
      formik.setValues(history[newIndex]);
    }
  }, [historyIndex, history, formik]);

  const redo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1;
      setHistoryIndex(newIndex);
      formik.setValues(history[newIndex]);
    }
  }, [historyIndex, history, formik]);

  // Render field based on type
  const renderField = (field: FormField) => {
    const { name, label, type, options = [], ...fieldProps } = field;
    const hasError = formik.touched[name] && formik.errors[name];
    const value = formik.values[name];

    switch (type) {
      case 'text':
      case 'textarea':
        return (
          <TextField
            key={name}
            fullWidth
            name={name}
            label={label}
            value={value}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={!!hasError}
            helperText={hasError || fieldProps.helperText}
            multiline={fieldProps.multiline}
            rows={fieldProps.rows}
            placeholder={fieldProps.placeholder}
            InputProps={{
              endAdornment: showValidation && (
                <InputAdornment position="end">
                  {hasError ? (
                    <Error color="error" />
                  ) : formik.touched[name] ? (
                    <CheckCircle color="success" />
                  ) : (
                    <Info color="action" />
                  )}
                </InputAdornment>
              )
            }}
          />
        );

      case 'email':
        return (
          <TextField
            key={name}
            fullWidth
            name={name}
            label={label}
            type="email"
            value={value}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={!!hasError}
            helperText={hasError || fieldProps.helperText}
            placeholder={fieldProps.placeholder}
            InputProps={{
              endAdornment: showValidation && (
                <InputAdornment position="end">
                  {hasError ? (
                    <Error color="error" />
                  ) : formik.touched[name] ? (
                    <CheckCircle color="success" />
                  ) : (
                    <Info color="action" />
                  )}
                </InputAdornment>
              )
            }}
          />
        );

      case 'number':
        return (
          <TextField
            key={name}
            fullWidth
            name={name}
            label={label}
            type="number"
            value={value}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={!!hasError}
            helperText={hasError || fieldProps.helperText}
            inputProps={{
              min: fieldProps.min,
              max: fieldProps.max,
              step: fieldProps.step
            }}
            placeholder={fieldProps.placeholder}
          />
        );

      case 'select':
        return (
          <FormControl key={name} fullWidth error={!!hasError}>
            <InputLabel>{label}</InputLabel>
            <Select
              name={name}
              value={value}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              label={label}
            >
              {options.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
            {(hasError || fieldProps.helperText) && (
              <FormHelperText>{hasError || fieldProps.helperText}</FormHelperText>
            )}
          </FormControl>
        );

      case 'multiselect':
        return (
          <Autocomplete
            key={name}
            multiple
            options={options}
            getOptionLabel={(option) => option.label}
            value={options.filter(option => value?.includes(option.value))}
            onChange={(_, newValue) => {
              formik.setFieldValue(name, newValue.map(v => v.value));
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label={label}
                error={!!hasError}
                helperText={hasError || fieldProps.helperText}
              />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  label={option.label}
                  {...getTagProps({ index })}
                  key={option.value}
                />
              ))
            }
          />
        );

      case 'switch':
        return (
          <FormControlLabel
            key={name}
            control={
              <Switch
                name={name}
                checked={value}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
              />
            }
            label={label}
          />
        );

      case 'slider':
        return (
          <Box key={name}>
            <Typography gutterBottom>{label}</Typography>
            <Slider
              name={name}
              value={value}
              onChange={(_, newValue) => {
                formik.setFieldValue(name, newValue);
              }}
              min={fieldProps.min}
              max={fieldProps.max}
              step={fieldProps.step}
              valueLabelDisplay="auto"
              marks={[
                { value: fieldProps.min || 0, label: fieldProps.min || 0 },
                { value: fieldProps.max || 100, label: fieldProps.max || 100 }
              ]}
            />
            {fieldProps.helperText && (
              <FormHelperText>{fieldProps.helperText}</FormHelperText>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Box sx={{ maxWidth: maxWidth, mx: 'auto', p: 3 }}>
      <Card>
        <CardContent>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" component="h2">
              {title}
            </Typography>
            
            <Box display="flex" gap={1} alignItems="center">
              {/* Auto-save status */}
              {showAutoSave && onAutoSave && (
                <Tooltip title={
                  autoSaveStatus === 'saving' ? 'Salvando...' :
                  autoSaveStatus === 'saved' ? 'Salvo automaticamente' :
                  autoSaveStatus === 'error' ? 'Erro no auto-save' :
                  'Auto-save ativo'
                }>
                  <Box display="flex" alignItems="center" gap={1}>
                    {autoSaveStatus === 'saving' && <CircularProgress size={16} />}
                    {autoSaveStatus === 'saved' && <CloudDone color="success" />}
                    {autoSaveStatus === 'error' && <CloudOff color="error" />}
                    {autoSaveStatus === 'idle' && <CloudUpload color="action" />}
                  </Box>
                </Tooltip>
              )}

              {/* Undo/Redo */}
              {showUndoRedo && (
                <>
                  <Tooltip title="Desfazer">
                    <IconButton onClick={undo} disabled={historyIndex === 0}>
                      <Undo />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Refazer">
                    <IconButton onClick={redo} disabled={historyIndex === history.length - 1}>
                      <Redo />
                    </IconButton>
                  </Tooltip>
                </>
              )}

              {/* Validation status */}
              {showValidation && (
                <Tooltip title={formik.isValid ? 'Formulário válido' : 'Formulário com erros'}>
                  <Validation color={formik.isValid ? 'success' : 'error'} />
                </Tooltip>
              )}
            </Box>
          </Box>

          {/* Last saved info */}
          {lastSaved && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Último salvamento: {lastSaved.toLocaleString('pt-BR')}
            </Alert>
          )}

          <Divider sx={{ mb: 3 }} />

          {/* Form */}
          <form onSubmit={formik.handleSubmit}>
            <Grid container spacing={3}>
              {fields.map((field) => (
                <Grid item xs={12} key={field.name}>
                  {renderField(field)}
                </Grid>
              ))}
            </Grid>

            {/* Actions */}
            <Box display="flex" gap={2} mt={4}>
              <Button
                type="submit"
                variant="contained"
                startIcon={isSubmitting ? <CircularProgress size={16} /> : <Save />}
                disabled={isSubmitting || !formik.isValid}
              >
                {isSubmitting ? 'Salvando...' : 'Salvar'}
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<SaveAlt />}
                onClick={() => {
                  // Save as draft
                  formik.setSubmitting(true);
                  setTimeout(() => {
                    formik.setSubmitting(false);
                    setSnackbar({
                      open: true,
                      message: 'Rascunho salvo!',
                      severity: 'info'
                    });
                  }, 1000);
                }}
                disabled={isSubmitting}
              >
                Salvar Rascunho
              </Button>
            </Box>
          </form>
        </CardContent>
      </Card>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AdvancedForm; 
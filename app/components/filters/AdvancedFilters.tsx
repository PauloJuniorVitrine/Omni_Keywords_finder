/**
 * AdvancedFilters.tsx
 * 
 * Sistema de filtros avançados para Omni Keywords Finder
 * 
 * Tracing ID: UI_ENTERPRISE_CHECKLIST_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 8.1
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Search, 
  Filter, 
  X, 
  Save, 
  Loader2, 
  Calendar,
  ChevronDown,
  ChevronUp,
  Settings,
  Download,
  Upload,
  RefreshCw,
  Eye,
  EyeOff
} from 'lucide-react';

// Types
export type FilterType = 'text' | 'select' | 'multiselect' | 'date' | 'daterange' | 'number' | 'range' | 'boolean' | 'autocomplete';

export interface FilterOption {
  label: string;
  value: string | number | boolean;
  disabled?: boolean;
  metadata?: Record<string, any>;
}

export interface FilterConfig {
  id: string;
  label: string;
  type: FilterType;
  placeholder?: string;
  options?: FilterOption[];
  defaultValue?: any;
  required?: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
  dependencies?: string[]; // IDs de outros filtros que afetam este
  metadata?: Record<string, any>;
}

export interface FilterValue {
  id: string;
  value: any;
  operator?: 'equals' | 'contains' | 'startsWith' | 'endsWith' | 'gt' | 'lt' | 'gte' | 'lte' | 'in' | 'notIn' | 'between';
}

export interface AdvancedFiltersProps {
  filters: FilterConfig[];
  values: FilterValue[];
  onChange: (values: FilterValue[]) => void;
  onApply?: (values: FilterValue[]) => void;
  onReset?: () => void;
  onSave?: (name: string, values: FilterValue[]) => void;
  onLoad?: (name: string) => FilterValue[];
  savedFilters?: Array<{ name: string; values: FilterValue[] }>;
  className?: string;
  maxVisibleFilters?: number;
  enableSaveLoad?: boolean;
  enableExport?: boolean;
  enableAutoApply?: boolean;
  debounceMs?: number;
  loading?: boolean;
}

// Context
interface FilterContextType {
  filters: FilterConfig[];
  values: FilterValue[];
  updateValue: (id: string, value: any, operator?: string) => void;
  getValue: (id: string) => any;
  getOperator: (id: string) => string;
  clearFilter: (id: string) => void;
  clearAll: () => void;
}

const FilterContext = React.createContext<FilterContextType | undefined>(undefined);

export const useFilters = () => {
  const context = React.useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within FilterProvider');
  }
  return context;
};

// Provider
export const FilterProvider: React.FC<{ 
  children: React.ReactNode;
  filters: FilterConfig[];
  values: FilterValue[];
  onChange: (values: FilterValue[]) => void;
}> = ({ children, filters, values, onChange }) => {
  const updateValue = useCallback((id: string, value: any, operator?: string) => {
    const newValues = [...values];
    const existingIndex = newValues.findIndex(v => v.id === id);
    
    if (existingIndex >= 0) {
      newValues[existingIndex] = { ...newValues[existingIndex], value, operator };
    } else {
      newValues.push({ id, value, operator });
    }
    
    onChange(newValues);
  }, [values, onChange]);

  const getValue = useCallback((id: string) => {
    return values.find(v => v.id === id)?.value;
  }, [values]);

  const getOperator = useCallback((id: string) => {
    return values.find(v => v.id === id)?.operator || 'equals';
  }, [values]);

  const clearFilter = useCallback((id: string) => {
    onChange(values.filter(v => v.id !== id));
  }, [values, onChange]);

  const clearAll = useCallback(() => {
    onChange([]);
  }, [onChange]);

  const value = useMemo(() => ({
    filters,
    values,
    updateValue,
    getValue,
    getOperator,
    clearFilter,
    clearAll,
  }), [filters, values, updateValue, getValue, getOperator, clearFilter, clearAll]);

  return (
    <FilterContext.Provider value={value}>
      {children}
    </FilterContext.Provider>
  );
};

// Individual Filter Components
const TextFilter: React.FC<{ config: FilterConfig }> = ({ config }) => {
  const { getValue, updateValue } = useFilters();
  const [inputValue, setInputValue] = useState(getValue(config.id) || '');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputValue(value);
    updateValue(config.id, value, 'contains');
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {config.label}
      </label>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          value={inputValue}
          onChange={handleChange}
          placeholder={config.placeholder || `Buscar ${config.label.toLowerCase()}...`}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
    </div>
  );
};

const SelectFilter: React.FC<{ config: FilterConfig }> = ({ config }) => {
  const { getValue, updateValue } = useFilters();
  const [isOpen, setIsOpen] = useState(false);
  const selectedValue = getValue(config.id);

  const handleSelect = (option: FilterOption) => {
    updateValue(config.id, option.value);
    setIsOpen(false);
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {config.label}
      </label>
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <span>
            {selectedValue 
              ? config.options?.find(opt => opt.value === selectedValue)?.label || selectedValue
              : config.placeholder || 'Selecione...'
            }
          </span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        
        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-60 overflow-auto">
            {config.options?.map((option) => (
              <button
                key={option.value.toString()}
                onClick={() => handleSelect(option)}
                disabled={option.disabled}
                className={`w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 ${
                  option.disabled ? 'text-gray-400 cursor-not-allowed' : 'text-gray-900 dark:text-white'
                } ${selectedValue === option.value ? 'bg-blue-50 dark:bg-blue-900/20' : ''}`}
              >
                {option.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const DateFilter: React.FC<{ config: FilterConfig }> = ({ config }) => {
  const { getValue, updateValue } = useFilters();
  const value = getValue(config.id);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateValue(config.id, e.target.value);
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {config.label}
      </label>
      <div className="relative">
        <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="date"
          value={value || ''}
          onChange={handleChange}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
    </div>
  );
};

const NumberFilter: React.FC<{ config: FilterConfig }> = ({ config }) => {
  const { getValue, updateValue } = useFilters();
  const value = getValue(config.id);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const numValue = e.target.value === '' ? null : Number(e.target.value);
    updateValue(config.id, numValue);
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {config.label}
      </label>
      <input
        type="number"
        value={value || ''}
        onChange={handleChange}
        placeholder={config.placeholder}
        min={config.validation?.min}
        max={config.validation?.max}
        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
    </div>
  );
};

const BooleanFilter: React.FC<{ config: FilterConfig }> = ({ config }) => {
  const { getValue, updateValue } = useFilters();
  const value = getValue(config.id);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateValue(config.id, e.target.checked);
  };

  return (
    <div className="flex items-center space-x-3">
      <input
        type="checkbox"
        id={config.id}
        checked={value || false}
        onChange={handleChange}
        className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
      />
      <label htmlFor={config.id} className="text-sm font-medium text-gray-700 dark:text-gray-300">
        {config.label}
      </label>
    </div>
  );
};

// Main Component
export const AdvancedFilters: React.FC<AdvancedFiltersProps> = ({
  filters,
  values,
  onChange,
  onApply,
  onReset,
  onSave,
  onLoad,
  savedFilters = [],
  className = '',
  maxVisibleFilters = 6,
  enableSaveLoad = true,
  enableExport = true,
  enableAutoApply = false,
  debounceMs = 300,
  loading = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showSavedFilters, setShowSavedFilters] = useState(false);
  const [saveFilterName, setSaveFilterName] = useState('');

  // Debounced auto-apply
  useEffect(() => {
    if (!enableAutoApply || !onApply) return;

    const timer = setTimeout(() => {
      onApply(values);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [values, enableAutoApply, onApply, debounceMs]);

  // Filter rendering
  const renderFilter = (config: FilterConfig) => {
    switch (config.type) {
      case 'text':
        return <TextFilter key={config.id} config={config} />;
      case 'select':
      case 'multiselect':
        return <SelectFilter key={config.id} config={config} />;
      case 'date':
      case 'daterange':
        return <DateFilter key={config.id} config={config} />;
      case 'number':
      case 'range':
        return <NumberFilter key={config.id} config={config} />;
      case 'boolean':
        return <BooleanFilter key={config.id} config={config} />;
      default:
        return <TextFilter key={config.id} config={config} />;
    }
  };

  // Visible filters
  const visibleFilters = isExpanded ? filters : filters.slice(0, maxVisibleFilters);
  const hasHiddenFilters = filters.length > maxVisibleFilters;

  // Active filters count
  const activeFiltersCount = values.length;

  // Export filters
  const handleExport = () => {
    const dataStr = JSON.stringify({ filters, values }, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `filters_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Import filters
  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target?.result as string);
        if (data.values) {
          onChange(data.values);
        }
      } catch (error) {
        console.error('Erro ao importar filtros:', error);
      }
    };
    reader.readAsText(file);
  };

  return (
    <FilterProvider filters={filters} values={values} onChange={onChange}>
      <div className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm ${className}`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Filtros Avançados
            </h3>
            {activeFiltersCount > 0 && (
              <span className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200 rounded-full">
                {activeFiltersCount} ativo{activeFiltersCount !== 1 ? 's' : ''}
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            {loading && <Loader2 className="w-4 h-4 animate-spin text-gray-400" />}
            
            {enableSaveLoad && (
              <button
                onClick={() => setShowSavedFilters(!showSavedFilters)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                title="Filtros salvos"
              >
                <Save className="w-4 h-4" />
              </button>
            )}
            
            {enableExport && (
              <button
                onClick={handleExport}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                title="Exportar filtros"
              >
                <Download className="w-4 h-4" />
              </button>
            )}
            
            <label className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 cursor-pointer" title="Importar filtros">
              <Upload className="w-4 h-4" />
              <input
                type="file"
                accept=".json"
                onChange={handleImport}
                className="hidden"
              />
            </label>
            
            <button
              onClick={onReset}
              className="p-2 text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400"
              title="Limpar filtros"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Filters Grid */}
        <div className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {visibleFilters.map(renderFilter)}
          </div>
          
          {hasHiddenFilters && (
            <div className="mt-4 text-center">
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium"
              >
                {isExpanded ? 'Mostrar menos' : `Mostrar mais ${filters.length - maxVisibleFilters} filtros`}
              </button>
            </div>
          )}
        </div>

        {/* Saved Filters */}
        {showSavedFilters && savedFilters.length > 0 && (
          <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              Filtros Salvos
            </h4>
            <div className="space-y-2">
              {savedFilters.map((saved) => (
                <div key={saved.name} className="flex items-center justify-between p-2 bg-white dark:bg-gray-800 rounded border">
                  <span className="text-sm text-gray-700 dark:text-gray-300">{saved.name}</span>
                  <button
                    onClick={() => onLoad?.(saved.name)}
                    className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm"
                  >
                    Carregar
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Save Filter Dialog */}
        {showSavedFilters && onSave && (
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={saveFilterName}
                onChange={(e) => setSaveFilterName(e.target.value)}
                placeholder="Nome do filtro"
                className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
              />
              <button
                onClick={() => {
                  if (saveFilterName.trim()) {
                    onSave(saveFilterName.trim(), values);
                    setSaveFilterName('');
                  }
                }}
                disabled={!saveFilterName.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                Salvar
              </button>
            </div>
          </div>
        )}

        {/* Actions */}
        {!enableAutoApply && onApply && (
          <div className="flex items-center justify-between p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {activeFiltersCount} filtro{activeFiltersCount !== 1 ? 's' : ''} ativo{activeFiltersCount !== 1 ? 's' : ''}
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={onReset}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 text-sm"
              >
                Limpar
              </button>
              <button
                onClick={() => onApply(values)}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                {loading ? 'Aplicando...' : 'Aplicar Filtros'}
              </button>
            </div>
          </div>
        )}
      </div>
    </FilterProvider>
  );
};

export default AdvancedFilters; 
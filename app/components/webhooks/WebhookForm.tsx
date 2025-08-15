/**
 * WebhookForm.tsx
 * 
 * Formulário de configuração de webhooks para Omni Keywords Finder
 * 
 * Tracing ID: UI_ENTERPRISE_CHECKLIST_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 11.2
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useEffect, useCallback } from 'react';
import { cn } from '../../utils/cn';

// Types
export interface WebhookEvent {
  id: string;
  name: string;
  description: string;
  category: 'execution' | 'nichos' | 'categorias' | 'system' | 'user';
  enabled: boolean;
}

export interface WebhookFormData {
  name: string;
  url: string;
  events: string[];
  secret?: string;
  headers?: Record<string, string>;
  description?: string;
  enabled: boolean;
}

export interface WebhookFormProps {
  webhook?: Partial<WebhookFormData>;
  events?: WebhookEvent[];
  onSubmit: (data: WebhookFormData) => void;
  onCancel: () => void;
  onTest?: (data: WebhookFormData) => void;
  className?: string;
  loading?: boolean;
  mode?: 'create' | 'edit';
}

// URL Validation
const validateUrl = (url: string): { isValid: boolean; error?: string } => {
  if (!url) {
    return { isValid: false, error: 'URL é obrigatória' };
  }

  try {
    const urlObj = new URL(url);
    if (!['http:', 'https:'].includes(urlObj.protocol)) {
      return { isValid: false, error: 'URL deve usar HTTP ou HTTPS' };
    }
    return { isValid: true };
  } catch {
    return { isValid: false, error: 'URL inválida' };
  }
};

// Secret Generation
const generateSecret = (): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < 32; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

// Event Category Component
const EventCategory: React.FC<{
  category: string;
  events: WebhookEvent[];
  selectedEvents: string[];
  onEventToggle: (eventId: string) => void;
}> = ({ category, events, selectedEvents, onEventToggle }) => {
  const categoryEvents = events.filter(event => event.category === category);
  const categoryLabel = {
    execution: 'Execuções',
    nichos: 'Nichos',
    categorias: 'Categorias',
    system: 'Sistema',
    user: 'Usuário'
  }[category] || category;

  const categoryIcon = {
    execution: '⚡',
    nichos: '📊',
    categorias: '📁',
    system: '⚙️',
    user: '👤'
  }[category] || '📋';

  if (categoryEvents.length === 0) return null;

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-gray-900 dark:text-white flex items-center">
        <span className="mr-2">{categoryIcon}</span>
        {categoryLabel}
      </h4>
      <div className="space-y-2">
        {categoryEvents.map((event) => (
          <label key={event.id} className="flex items-start space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={selectedEvents.includes(event.id)}
              onChange={() => onEventToggle(event.id)}
              className="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <div className="flex-1">
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                {event.name}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {event.description}
              </div>
            </div>
          </label>
        ))}
      </div>
    </div>
  );
};

// Header Input Component
const HeaderInput: React.FC<{
  headers: Record<string, string>;
  onHeadersChange: (headers: Record<string, string>) => void;
}> = ({ headers, onHeadersChange }) => {
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');

  const addHeader = () => {
    if (newKey.trim() && newValue.trim()) {
      onHeadersChange({
        ...headers,
        [newKey.trim()]: newValue.trim()
      });
      setNewKey('');
      setNewValue('');
    }
  };

  const removeHeader = (key: string) => {
    const newHeaders = { ...headers };
    delete newHeaders[key];
    onHeadersChange(newHeaders);
  };

  const updateHeader = (key: string, value: string) => {
    onHeadersChange({
      ...headers,
      [key]: value
    });
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center space-x-2">
        <input
          type="text"
          placeholder="Nome do header"
          value={newKey}
          onChange={(e) => setNewKey(e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
        />
        <input
          type="text"
          placeholder="Valor"
          value={newValue}
          onChange={(e) => setNewValue(e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
        />
        <button
          onClick={addHeader}
          disabled={!newKey.trim() || !newValue.trim()}
          className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
        >
          Adicionar
        </button>
      </div>

      {Object.keys(headers).length > 0 && (
        <div className="space-y-2">
          {Object.entries(headers).map(([key, value]) => (
            <div key={key} className="flex items-center space-x-2 p-2 bg-gray-50 dark:bg-gray-700 rounded">
              <input
                type="text"
                value={key}
                onChange={(e) => {
                  const newValue = e.target.value;
                  if (newValue !== key) {
                    removeHeader(key);
                    onHeadersChange({
                      ...headers,
                      [newValue]: value
                    });
                  }
                }}
                className="flex-1 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
              />
              <span className="text-gray-400">:</span>
              <input
                type="text"
                value={value}
                onChange={(e) => updateHeader(key, e.target.value)}
                className="flex-1 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
              />
              <button
                onClick={() => removeHeader(key)}
                className="p-1 text-red-500 hover:text-red-700"
              >
                ✗
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Main Form Component
export const WebhookForm: React.FC<WebhookFormProps> = ({
  webhook = {},
  events = [],
  onSubmit,
  onCancel,
  onTest,
  className = '',
  loading = false,
  mode = 'create',
}) => {
  const [formData, setFormData] = useState<WebhookFormData>({
    name: webhook.name || '',
    url: webhook.url || '',
    events: webhook.events || [],
    secret: webhook.secret || '',
    headers: webhook.headers || {},
    description: webhook.description || '',
    enabled: webhook.enabled !== false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showSecret, setShowSecret] = useState(false);
  const [urlValidation, setUrlValidation] = useState<{ isValid: boolean; error?: string }>({ isValid: true });

  // Validate form
  const validateForm = useCallback(() => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Nome é obrigatório';
    }

    if (!formData.url.trim()) {
      newErrors.url = 'URL é obrigatória';
    } else if (!urlValidation.isValid) {
      newErrors.url = urlValidation.error || 'URL inválida';
    }

    if (formData.events.length === 0) {
      newErrors.events = 'Selecione pelo menos um evento';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData, urlValidation]);

  // Handle URL validation
  useEffect(() => {
    if (formData.url) {
      setUrlValidation(validateUrl(formData.url));
    }
  }, [formData.url]);

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  // Handle event toggle
  const handleEventToggle = (eventId: string) => {
    setFormData(prev => ({
      ...prev,
      events: prev.events.includes(eventId)
        ? prev.events.filter(id => id !== eventId)
        : [...prev.events, eventId]
    }));
  };

  // Handle headers change
  const handleHeadersChange = (headers: Record<string, string>) => {
    setFormData(prev => ({ ...prev, headers }));
  };

  // Generate secret
  const handleGenerateSecret = () => {
    setFormData(prev => ({ ...prev, secret: generateSecret() }));
  };

  // Test webhook
  const handleTest = () => {
    if (validateForm()) {
      onTest?.(formData);
    }
  };

  const categories = ['execution', 'nichos', 'categorias', 'system', 'user'];

  return (
    <div className={cn('bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm', className)}>
      <div className="p-6">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {mode === 'create' ? 'Novo Webhook' : 'Editar Webhook'}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Configure o webhook para receber notificações de eventos
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Informações Básicas
            </h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Nome *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                className={cn(
                  'w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white',
                  errors.name
                    ? 'border-red-300 dark:border-red-600'
                    : 'border-gray-300 dark:border-gray-600'
                )}
                placeholder="Nome do webhook"
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.name}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                URL *
              </label>
              <input
                type="url"
                value={formData.url}
                onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
                className={cn(
                  'w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white',
                  errors.url
                    ? 'border-red-300 dark:border-red-600'
                    : 'border-gray-300 dark:border-gray-600'
                )}
                placeholder="https://exemplo.com/webhook"
              />
              {errors.url && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.url}</p>
              )}
              {urlValidation.isValid && formData.url && (
                <p className="mt-1 text-sm text-green-600 dark:text-green-400">✓ URL válida</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Descrição
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                placeholder="Descrição opcional do webhook"
              />
            </div>
          </div>

          {/* Events */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Eventos *
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {categories.map(category => (
                <EventCategory
                  key={category}
                  category={category}
                  events={events}
                  selectedEvents={formData.events}
                  onEventToggle={handleEventToggle}
                />
              ))}
            </div>
            
            {errors.events && (
              <p className="text-sm text-red-600 dark:text-red-400">{errors.events}</p>
            )}
          </div>

          {/* Security */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Segurança
            </h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Secret
              </label>
              <div className="flex items-center space-x-2">
                <div className="flex-1 relative">
                  <input
                    type={showSecret ? 'text' : 'password'}
                    value={formData.secret}
                    onChange={(e) => setFormData(prev => ({ ...prev, secret: e.target.value }))}
                    className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    placeholder="Secret para autenticação"
                  />
                  <button
                    type="button"
                    onClick={() => setShowSecret(!showSecret)}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showSecret ? '👁️' : '👁️‍🗨️'}
                  </button>
                </div>
                <button
                  type="button"
                  onClick={handleGenerateSecret}
                  className="px-3 py-2 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                >
                  Gerar
                </button>
              </div>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Secret usado para verificar a autenticidade das requisições
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Headers Customizados
              </label>
              <HeaderInput
                headers={formData.headers}
                onHeadersChange={handleHeadersChange}
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Headers adicionais enviados com cada requisição
              </p>
            </div>
          </div>

          {/* Settings */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Configurações
            </h3>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="enabled"
                checked={formData.enabled}
                onChange={(e) => setFormData(prev => ({ ...prev, enabled: e.target.checked }))}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="enabled" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Ativar webhook imediatamente
              </label>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Salvando...' : (mode === 'create' ? 'Criar Webhook' : 'Salvar Alterações')}
              </button>
              
              {onTest && (
                <button
                  type="button"
                  onClick={handleTest}
                  disabled={loading}
                  className="px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 disabled:opacity-50"
                >
                  Testar
                </button>
              )}
            </div>
            
            <button
              type="button"
              onClick={onCancel}
              disabled={loading}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default WebhookForm; 
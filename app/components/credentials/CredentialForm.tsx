/**
 * CredentialForm.tsx
 * 
 * Formulário seguro para criação e edição de credenciais
 * 
 * Tracing ID: UI_CREDENTIAL_FORM_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 13.2
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';
import { 
  Save, 
  Eye, 
  EyeOff, 
  Copy, 
  RefreshCw,
  Shield,
  Lock,
  Unlock,
  Key,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Clock,
  Download,
  Upload,
  Trash2,
  Edit,
  TestTube,
  History,
  Settings,
  Zap
} from 'lucide-react';
import { useCredentials } from '@/hooks/useCredentials';
import { useNotifications } from '@/hooks/useNotifications';
import { usePermissions } from '@/hooks/usePermissions';
import { useConfirmation } from '@/hooks/useConfirmation';

interface Credential {
  id?: string;
  name: string;
  type: 'api_key' | 'oauth' | 'basic_auth' | 'jwt' | 'custom';
  provider: string;
  status: 'active' | 'expired' | 'revoked' | 'pending';
  apiKey?: string;
  apiSecret?: string;
  accessToken?: string;
  refreshToken?: string;
  username?: string;
  password?: string;
  clientId?: string;
  clientSecret?: string;
  redirectUri?: string;
  scopes?: string[];
  expiresAt?: string;
  permissions: string[];
  isEncrypted: boolean;
  rotationEnabled: boolean;
  rotationInterval?: number;
  metadata?: Record<string, any>;
}

interface CredentialFormProps {
  credential?: Credential;
  onSave?: (credential: Credential) => void;
  onCancel?: () => void;
  className?: string;
}

interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

interface UsageHistory {
  id: string;
  timestamp: string;
  action: string;
  ipAddress: string;
  userAgent: string;
  success: boolean;
  errorMessage?: string;
}

export const CredentialForm: React.FC<CredentialFormProps> = ({
  credential,
  onSave,
  onCancel,
  className = ''
}) => {
  const [formData, setFormData] = useState<Credential>({
    name: credential?.name || '',
    type: credential?.type || 'api_key',
    provider: credential?.provider || 'custom',
    status: credential?.status || 'pending',
    apiKey: credential?.apiKey || '',
    apiSecret: credential?.apiSecret || '',
    accessToken: credential?.accessToken || '',
    refreshToken: credential?.refreshToken || '',
    username: credential?.username || '',
    password: credential?.password || '',
    clientId: credential?.clientId || '',
    clientSecret: credential?.clientSecret || '',
    redirectUri: credential?.redirectUri || '',
    scopes: credential?.scopes || [],
    expiresAt: credential?.expiresAt || '',
    permissions: credential?.permissions || [],
    isEncrypted: credential?.isEncrypted ?? true,
    rotationEnabled: credential?.rotationEnabled ?? false,
    rotationInterval: credential?.rotationInterval || 90,
    metadata: credential?.metadata || {}
  });

  const [showSecrets, setShowSecrets] = useState(false);
  const [activeTab, setActiveTab] = useState('basic');
  const [validationResult, setValidationResult] = useState<ValidationResult>({
    valid: true,
    errors: [],
    warnings: []
  });
  const [isValidating, setIsValidating] = useState(false);
  const [usageHistory, setUsageHistory] = useState<UsageHistory[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const { createCredential, updateCredential, validateCredential, getUsageHistory } = useCredentials();
  const { showNotification } = useNotifications();
  const { hasPermission } = usePermissions();
  const { showConfirmation } = useConfirmation();

  // Tipos de credenciais disponíveis
  const credentialTypes = [
    { value: 'api_key', label: 'API Key', icon: Key },
    { value: 'oauth', label: 'OAuth 2.0', icon: Lock },
    { value: 'basic_auth', label: 'Basic Auth', icon: Shield },
    { value: 'jwt', label: 'JWT Token', icon: Key },
    { value: 'custom', label: 'Custom', icon: Settings }
  ];

  // Provedores disponíveis
  const providers = [
    'google',
    'facebook',
    'twitter',
    'linkedin',
    'instagram',
    'tiktok',
    'youtube',
    'openai',
    'anthropic',
    'custom'
  ];

  // Permissões disponíveis
  const availablePermissions = [
    'read',
    'write',
    'delete',
    'admin',
    'analytics',
    'publish',
    'moderate',
    'billing'
  ];

  // Validação de credenciais
  const validateCredentialData = useCallback((data: Credential): ValidationResult => {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Validações básicas
    if (!data.name.trim()) {
      errors.push('Nome é obrigatório');
    }

    if (!data.provider.trim()) {
      errors.push('Provedor é obrigatório');
    }

    // Validações específicas por tipo
    switch (data.type) {
      case 'api_key':
        if (!data.apiKey?.trim()) {
          errors.push('API Key é obrigatória');
        }
        if (data.apiKey && data.apiKey.length < 8) {
          warnings.push('API Key muito curta');
        }
        break;

      case 'oauth':
        if (!data.clientId?.trim()) {
          errors.push('Client ID é obrigatório');
        }
        if (!data.clientSecret?.trim()) {
          errors.push('Client Secret é obrigatório');
        }
        if (!data.redirectUri?.trim()) {
          warnings.push('Redirect URI é recomendado');
        }
        break;

      case 'basic_auth':
        if (!data.username?.trim()) {
          errors.push('Username é obrigatório');
        }
        if (!data.password?.trim()) {
          errors.push('Password é obrigatório');
        }
        break;

      case 'jwt':
        if (!data.accessToken?.trim()) {
          errors.push('Access Token é obrigatório');
        }
        break;
    }

    // Validações de segurança
    if (data.password && data.password.length < 8) {
      warnings.push('Senha muito curta (mínimo 8 caracteres)');
    }

    if (data.expiresAt) {
      const expiryDate = new Date(data.expiresAt);
      const now = new Date();
      if (expiryDate <= now) {
        errors.push('Data de expiração deve ser futura');
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }, []);

  // Validar formulário quando dados mudam
  useEffect(() => {
    const result = validateCredentialData(formData);
    setValidationResult(result);
  }, [formData, validateCredentialData]);

  // Carregar histórico de uso
  useEffect(() => {
    if (credential?.id) {
      loadUsageHistory();
    }
  }, [credential?.id]);

  const loadUsageHistory = async () => {
    if (!credential?.id) return;

    try {
      const history = await getUsageHistory(credential.id);
      setUsageHistory(history);
    } catch (error) {
      showNotification('error', 'Erro ao carregar histórico de uso');
    }
  };

  // Handlers
  const handleInputChange = (field: keyof Credential, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleTestCredential = async () => {
    if (!hasPermission('credentials:validate')) {
      showNotification('error', 'Permissão negada para testar credenciais');
      return;
    }

    setIsValidating(true);
    try {
      const result = await validateCredential(formData);
      showNotification(
        result.valid ? 'success' : 'error',
        result.valid ? 'Credencial válida!' : `Credencial inválida: ${result.error}`
      );
    } catch (error) {
      showNotification('error', 'Erro ao testar credencial');
    } finally {
      setIsValidating(false);
    }
  };

  const handleGenerateSecret = () => {
    setIsGenerating(true);
    
    // Simular geração de secret
    setTimeout(() => {
      const secret = generateSecureSecret();
      setFormData(prev => ({
        ...prev,
        apiSecret: secret
      }));
      setIsGenerating(false);
      showNotification('success', 'Secret gerado com sucesso');
    }, 1000);
  };

  const generateSecureSecret = (): string => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let result = '';
    for (let i = 0; i < 32; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  };

  const handleCopyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    showNotification('success', 'Copiado para a área de transferência');
  };

  const handleSave = async () => {
    if (!hasPermission('credentials:create') && !hasPermission('credentials:update')) {
      showNotification('error', 'Permissão negada para salvar credenciais');
      return;
    }

    if (!validationResult.valid) {
      showNotification('error', 'Corrija os erros de validação antes de salvar');
      return;
    }

    const confirmed = await showConfirmation({
      title: 'Salvar Credencial',
      message: 'Tem certeza que deseja salvar esta credencial?',
      confirmText: 'Salvar',
      cancelText: 'Cancelar'
    });

    if (confirmed) {
      try {
        if (credential?.id) {
          await updateCredential(credential.id, formData);
          showNotification('success', 'Credencial atualizada com sucesso');
        } else {
          await createCredential(formData);
          showNotification('success', 'Credencial criada com sucesso');
        }
        
        onSave?.(formData);
      } catch (error) {
        showNotification('error', 'Erro ao salvar credencial');
      }
    }
  };

  const handleExport = () => {
    const exportData = {
      ...formData,
      // Não incluir secrets sensíveis na exportação
      apiSecret: undefined,
      password: undefined,
      clientSecret: undefined,
      refreshToken: undefined
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${formData.name.replace(/\s+/g, '_')}_credential.json`;
    link.click();
    URL.revokeObjectURL(url);
    
    showNotification('success', 'Credencial exportada com sucesso');
  };

  const getTypeIcon = (type: string) => {
    const typeConfig = credentialTypes.find(t => t.value === type);
    return typeConfig ? React.createElement(typeConfig.icon, { className: "w-4 h-4" }) : <Key className="w-4 h-4" />;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderBasicTab = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Nome *
          </label>
          <Input
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            placeholder="Nome da credencial"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Tipo *
          </label>
          <Select value={formData.type} onValueChange={(value) => handleInputChange('type', value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {credentialTypes.map(type => (
                <SelectItem key={type.value} value={type.value}>
                  <div className="flex items-center gap-2">
                    {getTypeIcon(type.value)}
                    {type.label}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Provedor *
          </label>
          <Select value={formData.provider} onValueChange={(value) => handleInputChange('provider', value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {providers.map(provider => (
                <SelectItem key={provider} value={provider}>
                  {provider}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Status
          </label>
          <Select value={formData.status} onValueChange={(value) => handleInputChange('status', value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="pending">Pendente</SelectItem>
              <SelectItem value="active">Ativo</SelectItem>
              <SelectItem value="expired">Expirado</SelectItem>
              <SelectItem value="revoked">Revogado</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Data de Expiração
        </label>
        <Input
          type="datetime-local"
          value={formData.expiresAt}
          onChange={(e) => handleInputChange('expiresAt', e.target.value)}
        />
      </div>
    </div>
  );

  const renderCredentialsTab = () => (
    <div className="space-y-4">
      {formData.type === 'api_key' && (
        <>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              API Key *
            </label>
            <div className="relative">
              <Input
                type={showSecrets ? 'text' : 'password'}
                value={formData.apiKey}
                onChange={(e) => handleInputChange('apiKey', e.target.value)}
                placeholder="Sua API Key"
              />
              <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setShowSecrets(!showSecrets)}
                >
                  {showSecrets ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleCopyToClipboard(formData.apiKey || '')}
                >
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              API Secret
            </label>
            <div className="relative">
              <Input
                type={showSecrets ? 'text' : 'password'}
                value={formData.apiSecret}
                onChange={(e) => handleInputChange('apiSecret', e.target.value)}
                placeholder="Sua API Secret"
              />
              <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={handleGenerateSecret}
                  disabled={isGenerating}
                >
                  {isGenerating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setShowSecrets(!showSecrets)}
                >
                  {showSecrets ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleCopyToClipboard(formData.apiSecret || '')}
                >
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </>
      )}

      {formData.type === 'oauth' && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Client ID *
              </label>
              <Input
                value={formData.clientId}
                onChange={(e) => handleInputChange('clientId', e.target.value)}
                placeholder="Client ID"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Client Secret *
              </label>
              <div className="relative">
                <Input
                  type={showSecrets ? 'text' : 'password'}
                  value={formData.clientSecret}
                  onChange={(e) => handleInputChange('clientSecret', e.target.value)}
                  placeholder="Client Secret"
                />
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setShowSecrets(!showSecrets)}
                  >
                    {showSecrets ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleCopyToClipboard(formData.clientSecret || '')}
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Redirect URI
            </label>
            <Input
              value={formData.redirectUri}
              onChange={(e) => handleInputChange('redirectUri', e.target.value)}
              placeholder="https://seu-site.com/callback"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Scopes
            </label>
            <Input
              value={formData.scopes?.join(', ')}
              onChange={(e) => handleInputChange('scopes', e.target.value.split(',').map(s => s.trim()))}
              placeholder="read, write, admin"
            />
          </div>
        </>
      )}

      {formData.type === 'basic_auth' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Username *
            </label>
            <Input
              value={formData.username}
              onChange={(e) => handleInputChange('username', e.target.value)}
              placeholder="Seu username"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Password *
            </label>
            <div className="relative">
              <Input
                type={showSecrets ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                placeholder="Sua password"
              />
              <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setShowSecrets(!showSecrets)}
                >
                  {showSecrets ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {formData.type === 'jwt' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Access Token *
          </label>
          <div className="relative">
            <Textarea
              value={formData.accessToken}
              onChange={(e) => handleInputChange('accessToken', e.target.value)}
              placeholder="Seu JWT token"
              rows={4}
            />
            <div className="absolute right-2 top-2 flex items-center gap-1">
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setShowSecrets(!showSecrets)}
              >
                {showSecrets ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => handleCopyToClipboard(formData.accessToken || '')}
              >
                <Copy className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderSecurityTab = () => (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="isEncrypted"
          checked={formData.isEncrypted}
          onChange={(e) => handleInputChange('isEncrypted', e.target.checked)}
          className="rounded border-gray-300"
        />
        <label htmlFor="isEncrypted" className="text-sm text-gray-700 dark:text-gray-300">
          Criptografar credenciais
        </label>
        <Lock className="w-4 h-4 text-green-600" />
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="rotationEnabled"
          checked={formData.rotationEnabled}
          onChange={(e) => handleInputChange('rotationEnabled', e.target.checked)}
          className="rounded border-gray-300"
        />
        <label htmlFor="rotationEnabled" className="text-sm text-gray-700 dark:text-gray-300">
          Habilitar rotação automática
        </label>
        <RefreshCw className="w-4 h-4 text-blue-600" />
      </div>

      {formData.rotationEnabled && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Intervalo de Rotação (dias)
          </label>
          <Input
            type="number"
            value={formData.rotationInterval}
            onChange={(e) => handleInputChange('rotationInterval', parseInt(e.target.value))}
            min="1"
            max="365"
          />
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Permissões
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {availablePermissions.map(permission => (
            <div key={permission} className="flex items-center space-x-2">
              <input
                type="checkbox"
                id={permission}
                checked={formData.permissions.includes(permission)}
                onChange={(e) => {
                  const newPermissions = e.target.checked
                    ? [...formData.permissions, permission]
                    : formData.permissions.filter(p => p !== permission);
                  handleInputChange('permissions', newPermissions);
                }}
                className="rounded border-gray-300"
              />
              <label htmlFor={permission} className="text-sm text-gray-700 dark:text-gray-300">
                {permission}
              </label>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderHistoryTab = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Histórico de Uso
        </h4>
        <Button size="sm" variant="outline" onClick={loadUsageHistory}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Atualizar
        </Button>
      </div>

      {usageHistory.length === 0 ? (
        <div className="text-center py-8">
          <History className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            Nenhum histórico de uso encontrado
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {usageHistory.map((entry) => (
            <div
              key={entry.id}
              className={`p-3 rounded border ${
                entry.success
                  ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                  : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {entry.success ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-red-600" />
                  )}
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {entry.action}
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  {formatDate(entry.timestamp)}
                </span>
              </div>
              <div className="mt-1 text-xs text-gray-600 dark:text-gray-400">
                <span>IP: {entry.ipAddress}</span>
                {entry.errorMessage && (
                  <span className="ml-2 text-red-600">Erro: {entry.errorMessage}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {credential?.id ? 'Editar Credencial' : 'Nova Credencial'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {credential?.id ? 'Modifique a credencial existente' : 'Configure uma nova credencial'}
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
          <Button onClick={handleSave} disabled={!validationResult.valid}>
            <Save className="w-4 h-4 mr-2" />
            Salvar
          </Button>
        </div>
      </div>

      {/* Validação */}
      {(validationResult.errors.length > 0 || validationResult.warnings.length > 0) && (
        <Card className="border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20">
          <CardContent className="p-4">
            <div className="space-y-2">
              {validationResult.errors.map((error, index) => (
                <div key={index} className="flex items-center gap-2 text-red-700 dark:text-red-300">
                  <AlertTriangle className="w-4 h-4" />
                  <span className="text-sm">{error}</span>
                </div>
              ))}
              {validationResult.warnings.map((warning, index) => (
                <div key={index} className="flex items-center gap-2 text-yellow-700 dark:text-yellow-300">
                  <AlertTriangle className="w-4 h-4" />
                  <span className="text-sm">{warning}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Formulário Principal */}
      <Card>
        <CardContent className="p-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="basic">Básico</TabsTrigger>
              <TabsTrigger value="credentials">Credenciais</TabsTrigger>
              <TabsTrigger value="security">Segurança</TabsTrigger>
              <TabsTrigger value="history">Histórico</TabsTrigger>
            </TabsList>
            
            <TabsContent value="basic" className="mt-6">
              {renderBasicTab()}
            </TabsContent>
            
            <TabsContent value="credentials" className="mt-6">
              {renderCredentialsTab()}
            </TabsContent>
            
            <TabsContent value="security" className="mt-6">
              {renderSecurityTab()}
            </TabsContent>
            
            <TabsContent value="history" className="mt-6">
              {renderHistoryTab()}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Ações */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={handleTestCredential}
                disabled={isValidating || !validationResult.valid}
              >
                <TestTube className="w-4 h-4 mr-2" />
                {isValidating ? 'Testando...' : 'Testar Credencial'}
              </Button>
            </div>
            
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={handleExport}>
                <Download className="w-4 h-4 mr-2" />
                Exportar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CredentialForm; 
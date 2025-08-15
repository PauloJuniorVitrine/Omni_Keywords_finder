/**
 * CredentialsDashboard.tsx
 * 
 * Dashboard principal para gestão segura de credenciais
 * 
 * Tracing ID: UI_CREDENTIALS_DASHBOARD_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 13.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table';
import { 
  Plus, 
  Search, 
  Filter, 
  Eye, 
  EyeOff, 
  Copy, 
  RefreshCw,
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  RotateCcw,
  Download,
  Upload,
  Trash2,
  Edit,
  Key,
  Lock,
  Unlock,
  Calendar,
  Activity
} from 'lucide-react';
import { useCredentials } from '@/hooks/useCredentials';
import { useNotifications } from '@/hooks/useNotifications';
import { usePermissions } from '@/hooks/usePermissions';
import { useConfirmation } from '@/hooks/useConfirmation';

interface Credential {
  id: string;
  name: string;
  type: 'api_key' | 'oauth' | 'basic_auth' | 'jwt' | 'custom';
  provider: string;
  status: 'active' | 'expired' | 'revoked' | 'pending';
  lastUsed: string;
  expiresAt?: string;
  permissions: string[];
  isEncrypted: boolean;
  rotationEnabled: boolean;
  lastRotated?: string;
  nextRotation?: string;
  usageCount: number;
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, any>;
}

interface CredentialsDashboardProps {
  className?: string;
}

export const CredentialsDashboard: React.FC<CredentialsDashboardProps> = ({ 
  className = '' 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedProvider, setSelectedProvider] = useState<string>('all');
  const [showExpired, setShowExpired] = useState(false);
  const [showSecrets, setShowSecrets] = useState(false);
  const [selectedCredentials, setSelectedCredentials] = useState<string[]>([]);

  const { 
    credentials, 
    loading, 
    error, 
    createCredential, 
    updateCredential, 
    deleteCredential,
    rotateCredential,
    validateCredential,
    exportCredentials,
    importCredentials,
    bulkRotate,
    bulkDelete
  } = useCredentials();

  const { showNotification } = useNotifications();
  const { hasPermission } = usePermissions();
  const { showConfirmation } = useConfirmation();

  // Filtros disponíveis
  const credentialTypes = [
    'all',
    'api_key',
    'oauth',
    'basic_auth',
    'jwt',
    'custom'
  ];

  const statuses = [
    'all',
    'active',
    'expired',
    'revoked',
    'pending'
  ];

  const providers = [
    'all',
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

  // Filtrar credenciais
  const filteredCredentials = credentials.filter(credential => {
    const matchesSearch = credential.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         credential.provider.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = selectedType === 'all' || credential.type === selectedType;
    const matchesStatus = selectedStatus === 'all' || credential.status === selectedStatus;
    const matchesProvider = selectedProvider === 'all' || credential.provider === selectedProvider;
    const matchesExpired = !showExpired || credential.status === 'expired';

    return matchesSearch && matchesType && matchesStatus && matchesProvider && matchesExpired;
  });

  // Métricas do dashboard
  const dashboardStats = {
    total: credentials.length,
    active: credentials.filter(c => c.status === 'active').length,
    expired: credentials.filter(c => c.status === 'expired').length,
    revoked: credentials.filter(c => c.status === 'revoked').length,
    pending: credentials.filter(c => c.status === 'pending').length,
    encrypted: credentials.filter(c => c.isEncrypted).length,
    rotationEnabled: credentials.filter(c => c.rotationEnabled).length,
    totalUsage: credentials.reduce((sum, c) => sum + c.usageCount, 0)
  };

  // Handlers
  const handleCreateCredential = () => {
    if (!hasPermission('credentials:create')) {
      showNotification('error', 'Permissão negada para criar credenciais');
      return;
    }
    // Implementar criação de credencial
    showNotification('info', 'Funcionalidade de criação será implementada');
  };

  const handleRotateCredential = async (credentialId: string) => {
    if (!hasPermission('credentials:rotate')) {
      showNotification('error', 'Permissão negada para rotacionar credenciais');
      return;
    }

    const confirmed = await showConfirmation({
      title: 'Rotacionar Credencial',
      message: 'Tem certeza que deseja rotacionar esta credencial? Isso irá invalidar a versão atual.',
      confirmText: 'Rotacionar',
      cancelText: 'Cancelar',
      variant: 'warning'
    });

    if (confirmed) {
      try {
        await rotateCredential(credentialId);
        showNotification('success', 'Credencial rotacionada com sucesso');
      } catch (error) {
        showNotification('error', 'Erro ao rotacionar credencial');
      }
    }
  };

  const handleValidateCredential = async (credentialId: string) => {
    if (!hasPermission('credentials:validate')) {
      showNotification('error', 'Permissão negada para validar credenciais');
      return;
    }

    try {
      const result = await validateCredential(credentialId);
      showNotification(
        result.valid ? 'success' : 'error',
        result.valid ? 'Credencial válida' : `Credencial inválida: ${result.error}`
      );
    } catch (error) {
      showNotification('error', 'Erro ao validar credencial');
    }
  };

  const handleDeleteCredential = async (credentialId: string) => {
    if (!hasPermission('credentials:delete')) {
      showNotification('error', 'Permissão negada para excluir credenciais');
      return;
    }

    const confirmed = await showConfirmation({
      title: 'Excluir Credencial',
      message: 'Tem certeza que deseja excluir esta credencial? Esta ação não pode ser desfeita.',
      confirmText: 'Excluir',
      cancelText: 'Cancelar',
      variant: 'danger'
    });

    if (confirmed) {
      try {
        await deleteCredential(credentialId);
        showNotification('success', 'Credencial excluída com sucesso');
      } catch (error) {
        showNotification('error', 'Erro ao excluir credencial');
      }
    }
  };

  const handleBulkRotate = async () => {
    if (selectedCredentials.length === 0) {
      showNotification('warning', 'Selecione credenciais para rotacionar');
      return;
    }

    if (!hasPermission('credentials:rotate')) {
      showNotification('error', 'Permissão negada para rotacionar credenciais');
      return;
    }

    const confirmed = await showConfirmation({
      title: 'Rotacionar Credenciais',
      message: `Tem certeza que deseja rotacionar ${selectedCredentials.length} credenciais?`,
      confirmText: 'Rotacionar',
      cancelText: 'Cancelar',
      variant: 'warning'
    });

    if (confirmed) {
      try {
        await bulkRotate(selectedCredentials);
        setSelectedCredentials([]);
        showNotification('success', 'Credenciais rotacionadas com sucesso');
      } catch (error) {
        showNotification('error', 'Erro ao rotacionar credenciais');
      }
    }
  };

  const handleBulkDelete = async () => {
    if (selectedCredentials.length === 0) {
      showNotification('warning', 'Selecione credenciais para excluir');
      return;
    }

    if (!hasPermission('credentials:delete')) {
      showNotification('error', 'Permissão negada para excluir credenciais');
      return;
    }

    const confirmed = await showConfirmation({
      title: 'Excluir Credenciais',
      message: `Tem certeza que deseja excluir ${selectedCredentials.length} credenciais? Esta ação não pode ser desfeita.`,
      confirmText: 'Excluir',
      cancelText: 'Cancelar',
      variant: 'danger'
    });

    if (confirmed) {
      try {
        await bulkDelete(selectedCredentials);
        setSelectedCredentials([]);
        showNotification('success', 'Credenciais excluídas com sucesso');
      } catch (error) {
        showNotification('error', 'Erro ao excluir credenciais');
      }
    }
  };

  const handleExportCredentials = () => {
    if (!hasPermission('credentials:export')) {
      showNotification('error', 'Permissão negada para exportar credenciais');
      return;
    }
    // Implementar exportação
    showNotification('info', 'Funcionalidade de exportação será implementada');
  };

  const handleImportCredentials = () => {
    if (!hasPermission('credentials:import')) {
      showNotification('error', 'Permissão negada para importar credenciais');
      return;
    }
    // Implementar importação
    showNotification('info', 'Funcionalidade de importação será implementada');
  };

  const handleSelectCredential = (credentialId: string) => {
    setSelectedCredentials(prev => 
      prev.includes(credentialId)
        ? prev.filter(id => id !== credentialId)
        : [...prev, credentialId]
    );
  };

  const handleSelectAll = () => {
    if (selectedCredentials.length === filteredCredentials.length) {
      setSelectedCredentials([]);
    } else {
      setSelectedCredentials(filteredCredentials.map(c => c.id));
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'expired':
        return <Clock className="w-4 h-4 text-yellow-600" />;
      case 'revoked':
        return <AlertTriangle className="w-4 h-4 text-red-600" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-blue-600" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      active: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300',
      expired: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300',
      revoked: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300',
      pending: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
    };

    return (
      <Badge className={variants[status as keyof typeof variants]}>
        {status}
      </Badge>
    );
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'api_key':
        return <Key className="w-4 h-4" />;
      case 'oauth':
        return <Lock className="w-4 h-4" />;
      case 'basic_auth':
        return <Shield className="w-4 h-4" />;
      case 'jwt':
        return <Key className="w-4 h-4" />;
      case 'custom':
        return <Key className="w-4 h-4" />;
      default:
        return <Key className="w-4 h-4" />;
    }
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

  const isExpiringSoon = (expiresAt?: string) => {
    if (!expiresAt) return false;
    const expiryDate = new Date(expiresAt);
    const now = new Date();
    const daysUntilExpiry = Math.ceil((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry <= 30 && daysUntilExpiry > 0;
  };

  if (error) {
    return (
      <div className={`p-6 ${className}`}>
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-red-800 mb-2">
                Erro ao carregar credenciais
              </h3>
              <p className="text-red-600 mb-4">{error}</p>
              <Button 
                variant="outline" 
                onClick={() => window.location.reload()}
              >
                Tentar novamente
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header do Dashboard */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Credenciais
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Gerencie suas credenciais de API e autenticação de forma segura
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          {hasPermission('credentials:import') && (
            <Button variant="outline" onClick={handleImportCredentials}>
              <Upload className="w-4 h-4 mr-2" />
              Importar
            </Button>
          )}
          
          {hasPermission('credentials:export') && (
            <Button variant="outline" onClick={handleExportCredentials}>
              <Download className="w-4 h-4 mr-2" />
              Exportar
            </Button>
          )}
          
          {hasPermission('credentials:create') && (
            <Button onClick={handleCreateCredential}>
              <Plus className="w-4 h-4 mr-2" />
              Nova Credencial
            </Button>
          )}
        </div>
      </div>

      {/* Métricas Rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {dashboardStats.total}
                </p>
              </div>
              <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <Key className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Ativas
                </p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {dashboardStats.active}
                </p>
              </div>
              <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Expiradas
                </p>
                <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                  {dashboardStats.expired}
                </p>
              </div>
              <div className="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                <Clock className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Criptografadas
                </p>
                <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {dashboardStats.encrypted}
                </p>
              </div>
              <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                <Lock className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros e Controles */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col lg:flex-row gap-4 items-center">
            {/* Busca */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Buscar credenciais..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Filtros */}
            <div className="flex gap-2">
              <Select value={selectedType} onValueChange={setSelectedType}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Tipo" />
                </SelectTrigger>
                <SelectContent>
                  {credentialTypes.map(type => (
                    <SelectItem key={type} value={type}>
                      {type === 'all' ? 'Todos' : type.replace('_', ' ')}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  {statuses.map(status => (
                    <SelectItem key={status} value={status}>
                      {status === 'all' ? 'Todos' : status}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={selectedProvider} onValueChange={setSelectedProvider}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Provedor" />
                </SelectTrigger>
                <SelectContent>
                  {providers.map(provider => (
                    <SelectItem key={provider} value={provider}>
                      {provider === 'all' ? 'Todos' : provider}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Controles */}
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowExpired(!showExpired)}
              >
                <Filter className="w-4 h-4 mr-2" />
                Expiradas
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Ações em Lote */}
      {(selectedCredentials.length > 0) && (
        <Card className="border-blue-200 bg-blue-50 dark:bg-blue-900/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-blue-800 dark:text-blue-200">
                  {selectedCredentials.length} credencial(is) selecionada(s)
                </span>
              </div>
              
              <div className="flex items-center gap-2">
                {hasPermission('credentials:rotate') && (
                  <Button size="sm" variant="outline" onClick={handleBulkRotate}>
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Rotacionar
                  </Button>
                )}
                
                {hasPermission('credentials:delete') && (
                  <Button size="sm" variant="destructive" onClick={handleBulkDelete}>
                    <Trash2 className="w-4 h-4 mr-2" />
                    Excluir
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Lista de Credenciais */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>
              Credenciais ({filteredCredentials.length})
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleSelectAll}
              >
                {selectedCredentials.length === filteredCredentials.length ? 'Desmarcar' : 'Selecionar'} Todos
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-2 text-gray-600">Carregando credenciais...</span>
            </div>
          ) : filteredCredentials.length === 0 ? (
            <div className="text-center py-12">
              <Key className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Nenhuma credencial encontrada
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {searchTerm || selectedType !== 'all' || selectedStatus !== 'all' || selectedProvider !== 'all'
                  ? 'Tente ajustar os filtros de busca'
                  : 'Adicione sua primeira credencial para começar'
                }
              </p>
              {hasPermission('credentials:create') && (
                <Button onClick={handleCreateCredential}>
                  <Plus className="w-4 h-4 mr-2" />
                  Adicionar Credencial
                </Button>
              )}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <input
                      type="checkbox"
                      checked={selectedCredentials.length === filteredCredentials.length}
                      onChange={handleSelectAll}
                      className="rounded border-gray-300"
                    />
                  </TableHead>
                  <TableHead>Nome</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Provedor</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Último Uso</TableHead>
                  <TableHead>Expira em</TableHead>
                  <TableHead>Uso</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCredentials.map((credential) => (
                  <TableRow 
                    key={credential.id}
                    className={isExpiringSoon(credential.expiresAt) ? 'bg-yellow-50 dark:bg-yellow-900/10' : ''}
                  >
                    <TableCell>
                      <input
                        type="checkbox"
                        checked={selectedCredentials.includes(credential.id)}
                        onChange={() => handleSelectCredential(credential.id)}
                        className="rounded border-gray-300"
                      />
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900 dark:text-white">
                          {credential.name}
                        </span>
                        {credential.isEncrypted && (
                          <Lock className="w-4 h-4 text-green-600" />
                        )}
                        {credential.rotationEnabled && (
                          <RotateCcw className="w-4 h-4 text-blue-600" />
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getTypeIcon(credential.type)}
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {credential.type.replace('_', ' ')}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {credential.provider}
                      </span>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(credential.status)}
                        {getStatusBadge(credential.status)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {formatDate(credential.lastUsed)}
                      </span>
                    </TableCell>
                    <TableCell>
                      {credential.expiresAt ? (
                        <span className={`text-sm ${
                          isExpiringSoon(credential.expiresAt) 
                            ? 'text-yellow-600 dark:text-yellow-400 font-medium' 
                            : 'text-gray-600 dark:text-gray-400'
                        }`}>
                          {formatDate(credential.expiresAt)}
                        </span>
                      ) : (
                        <span className="text-sm text-gray-400">Nunca</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {credential.usageCount}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        {hasPermission('credentials:validate') && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleValidateCredential(credential.id)}
                            title="Validar"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </Button>
                        )}
                        
                        {hasPermission('credentials:rotate') && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleRotateCredential(credential.id)}
                            title="Rotacionar"
                          >
                            <RotateCcw className="w-4 h-4" />
                          </Button>
                        )}
                        
                        {hasPermission('credentials:update') && (
                          <Button
                            size="sm"
                            variant="ghost"
                            title="Editar"
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                        )}
                        
                        {hasPermission('credentials:delete') && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDeleteCredential(credential.id)}
                            title="Excluir"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CredentialsDashboard; 
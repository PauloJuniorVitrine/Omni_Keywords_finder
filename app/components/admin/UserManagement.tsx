/**
 * UserManagement.tsx
 * 
 * Componente principal da gestão completa de usuários
 * Integra CRUD, RBAC, permissões e auditoria
 * 
 * Tracing ID: UI-003
 * Data/Hora: 2024-12-20 07:30:00 UTC
 * Versão: 1.0
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '../shared/Card';
import { Button } from '../shared/Button';
import { Badge } from '../shared/Badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../shared/Tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../shared/Select';
import { Input } from '../shared/Input';
import { Alert, AlertDescription } from '../shared/Alert';
import { Skeleton } from '../shared/Skeleton';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../shared/Table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../shared/Dialog';
import { Checkbox } from '../shared/Checkbox';
import { useUsers } from '../../hooks/useUsers';
import { useRoles } from '../../hooks/useRoles';
import { usePermissions } from '../../hooks/usePermissions';
import { formatDate, formatTime } from '../../utils/formatters';
import { 
  Users, 
  UserPlus, 
  UserEdit, 
  UserX, 
  Shield, 
  Lock, 
  Unlock,
  Search,
  Download,
  Upload,
  RefreshCw,
  Filter,
  Eye,
  EyeOff,
  Settings,
  History,
  Key,
  Mail,
  Phone,
  Calendar,
  MapPin,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Activity,
  ShieldCheck,
  UserCheck,
  UserMinus
} from 'lucide-react';

interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  status: 'active' | 'inactive' | 'suspended' | 'pending';
  roles: string[];
  permissions: string[];
  lastLogin: Date;
  createdAt: Date;
  updatedAt: Date;
  phone?: string;
  department?: string;
  position?: string;
  avatar?: string;
  twoFactorEnabled: boolean;
  passwordLastChanged: Date;
  failedLoginAttempts: number;
  lockedUntil?: Date;
}

interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  isSystem: boolean;
  createdAt: Date;
  updatedAt: Date;
  userCount: number;
}

interface Permission {
  id: string;
  name: string;
  description: string;
  category: string;
  isSystem: boolean;
}

interface UserActivity {
  id: string;
  userId: string;
  action: string;
  resource: string;
  timestamp: Date;
  ipAddress: string;
  userAgent: string;
  details: string;
}

interface UserManagementProps {
  className?: string;
  refreshInterval?: number;
  enableRealTime?: boolean;
  exportFormats?: ('csv' | 'json' | 'pdf')[];
  maxUsers?: number;
}

export const UserManagement: React.FC<UserManagementProps> = ({
  className = '',
  refreshInterval = 30000,
  enableRealTime = true,
  exportFormats = ['csv', 'json'],
  maxUsers = 1000
}) => {
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedRole, setSelectedRole] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [showSensitiveData, setShowSensitiveData] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isUserDialogOpen, setIsUserDialogOpen] = useState(false);
  const [isRoleDialogOpen, setIsRoleDialogOpen] = useState(false);
  const [isPermissionDialogOpen, setIsPermissionDialogOpen] = useState(false);

  const {
    data: usersData,
    isLoading,
    error,
    refetch,
    createUser,
    updateUser,
    deleteUser,
    suspendUser,
    activateUser,
    resetPassword,
    unlockUser
  } = useUsers({
    status: selectedStatus,
    role: selectedRole,
    searchTerm,
    maxUsers
  });

  const {
    data: rolesData,
    isLoading: rolesLoading
  } = useRoles();

  const {
    data: permissionsData,
    isLoading: permissionsLoading
  } = usePermissions();

  // Auto-refresh para dados em tempo real
  useEffect(() => {
    if (!enableRealTime) return;

    const interval = setInterval(() => {
      refetch();
      setLastRefresh(new Date());
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [enableRealTime, refreshInterval, refetch]);

  // Cálculos derivados
  const calculatedMetrics = useMemo(() => {
    if (!usersData) return null;

    const { users, activities } = usersData;

    return {
      totalUsers: users.length,
      activeUsers: users.filter(user => user.status === 'active').length,
      suspendedUsers: users.filter(user => user.status === 'suspended').length,
      pendingUsers: users.filter(user => user.status === 'pending').length,
      usersWithTwoFactor: users.filter(user => user.twoFactorEnabled).length,
      lockedUsers: users.filter(user => user.lockedUntil && user.lockedUntil > new Date()).length,
      recentActivities: activities.filter(activity => 
        new Date(activity.timestamp) > new Date(Date.now() - 24 * 60 * 60 * 1000)
      ).length
    };
  }, [usersData]);

  // Handlers
  const handleExport = async (format: string) => {
    setIsExporting(true);
    try {
      // Implementar lógica de exportação
      console.log(`Exporting users data in ${format} format`);
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulação
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const handleRefresh = () => {
    refetch();
    setLastRefresh(new Date());
  };

  const handleCreateUser = () => {
    setSelectedUser(null);
    setIsUserDialogOpen(true);
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setIsUserDialogOpen(true);
  };

  const handleDeleteUser = async (userId: string) => {
    if (confirm('Tem certeza que deseja excluir este usuário?')) {
      try {
        await deleteUser(userId);
        refetch();
      } catch (error) {
        console.error('Failed to delete user:', error);
      }
    }
  };

  const handleSuspendUser = async (userId: string) => {
    try {
      await suspendUser(userId);
      refetch();
    } catch (error) {
      console.error('Failed to suspend user:', error);
    }
  };

  const handleActivateUser = async (userId: string) => {
    try {
      await activateUser(userId);
      refetch();
    } catch (error) {
      console.error('Failed to activate user:', error);
    }
  };

  const handleUnlockUser = async (userId: string) => {
    try {
      await unlockUser(userId);
      refetch();
    } catch (error) {
      console.error('Failed to unlock user:', error);
    }
  };

  const handleResetPassword = async (userId: string) => {
    try {
      await resetPassword(userId);
      alert('Senha redefinida com sucesso');
    } catch (error) {
      console.error('Failed to reset password:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'secondary';
      case 'suspended': return 'destructive';
      case 'pending': return 'warning';
      default: return 'secondary';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4" />;
      case 'inactive': return <XCircle className="h-4 w-4" />;
      case 'suspended': return <UserX className="h-4 w-4" />;
      case 'pending': return <Clock className="h-4 w-4" />;
      default: return <User className="h-4 w-4" />;
    }
  };

  // Renderização de loading
  if (isLoading) {
    return (
      <div className={`user-management ${className}`}>
        <div className="grid gap-6">
          <Skeleton className="h-8 w-64" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
          <Skeleton className="h-96" />
        </div>
      </div>
    );
  }

  // Renderização de erro
  if (error) {
    return (
      <div className={`user-management ${className}`}>
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Erro ao carregar dados de usuários: {error.message}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className={`user-management ${className}`}>
      {/* Header com controles */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestão de Usuários</h1>
          <p className="text-muted-foreground">
            CRUD completo, RBAC, permissões e auditoria
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSensitiveData(!showSensitiveData)}
          >
            {showSensitiveData ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
            {showSensitiveData ? 'Ocultar' : 'Mostrar'} Dados Sensíveis
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>

          <Button onClick={handleCreateUser}>
            <UserPlus className="h-4 w-4 mr-2" />
            Novo Usuário
          </Button>

          <div className="flex gap-1">
            {exportFormats.map(format => (
              <Button
                key={format}
                variant="outline"
                size="sm"
                onClick={() => handleExport(format)}
                disabled={isExporting}
              >
                <Download className="h-4 w-4 mr-2" />
                {format.toUpperCase()}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Indicadores de status */}
      <div className="flex items-center gap-4 mb-6 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4" />
          Última atualização: {lastRefresh.toLocaleTimeString()}
        </div>
        
        {enableRealTime && (
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-green-500" />
            Sincronização ativa
          </div>
        )}
      </div>

      {/* Métricas principais */}
      {usersData && calculatedMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Usuários</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {calculatedMetrics.totalUsers.toLocaleString()}
              </div>
              <div className="text-xs text-muted-foreground">
                {calculatedMetrics.activeUsers} ativos
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Usuários Suspensos</CardTitle>
              <UserX className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {calculatedMetrics.suspendedUsers}
              </div>
              <div className="text-xs text-muted-foreground">
                {calculatedMetrics.lockedUsers} bloqueados
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">2FA Habilitado</CardTitle>
              <ShieldCheck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {calculatedMetrics.usersWithTwoFactor}
              </div>
              <div className="text-xs text-muted-foreground">
                {((calculatedMetrics.usersWithTwoFactor / calculatedMetrics.totalUsers) * 100).toFixed(1)}% dos usuários
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Atividades Recentes</CardTitle>
              <History className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {calculatedMetrics.recentActivities}
              </div>
              <div className="text-xs text-muted-foreground">
                Últimas 24 horas
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filtros */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div>
          <label className="text-sm font-medium">Status</label>
          <Select value={selectedStatus} onValueChange={setSelectedStatus}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os status</SelectItem>
              <SelectItem value="active">Ativo</SelectItem>
              <SelectItem value="inactive">Inativo</SelectItem>
              <SelectItem value="suspended">Suspenso</SelectItem>
              <SelectItem value="pending">Pendente</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-sm font-medium">Role</label>
          <Select value={selectedRole} onValueChange={setSelectedRole}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas as roles</SelectItem>
              {rolesData?.roles.map(role => (
                <SelectItem key={role.id} value={role.id}>
                  {role.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-sm font-medium">Buscar</label>
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar usuários..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <div className="flex items-end">
          <Button variant="outline" className="w-full">
            <Filter className="h-4 w-4 mr-2" />
            Filtros Avançados
          </Button>
        </div>
      </div>

      {/* Tabs principais */}
      <Tabs defaultValue="users" className="space-y-4">
        <TabsList>
          <TabsTrigger value="users">Usuários</TabsTrigger>
          <TabsTrigger value="roles">Roles</TabsTrigger>
          <TabsTrigger value="permissions">Permissões</TabsTrigger>
          <TabsTrigger value="activity">Atividades</TabsTrigger>
        </TabsList>

        <TabsContent value="users" className="space-y-4">
          {usersData && (
            <Card>
              <CardHeader>
                <CardTitle>Lista de Usuários</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Usuário</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Roles</TableHead>
                      <TableHead>Último Login</TableHead>
                      <TableHead>2FA</TableHead>
                      <TableHead>Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {usersData.users.slice(0, 50).map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                              {user.avatar ? (
                                <img src={user.avatar} alt={user.firstName} className="w-8 h-8 rounded-full" />
                              ) : (
                                <span className="text-sm font-medium">
                                  {user.firstName.charAt(0)}{user.lastName.charAt(0)}
                                </span>
                              )}
                            </div>
                            <div>
                              <div className="font-medium">
                                {user.firstName} {user.lastName}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                @{user.username}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          {showSensitiveData ? user.email : '***@***.***'}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getStatusIcon(user.status)}
                            <Badge variant={getStatusColor(user.status)}>
                              {user.status}
                            </Badge>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {user.roles.slice(0, 2).map(role => (
                              <Badge key={role} variant="outline" className="text-xs">
                                {role}
                              </Badge>
                            ))}
                            {user.roles.length > 2 && (
                              <Badge variant="outline" className="text-xs">
                                +{user.roles.length - 2}
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {user.lastLogin ? formatTime(user.lastLogin) : 'Nunca'}
                        </TableCell>
                        <TableCell>
                          {user.twoFactorEnabled ? (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          ) : (
                            <XCircle className="h-4 w-4 text-muted-foreground" />
                          )}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEditUser(user)}
                            >
                              <UserEdit className="h-4 w-4" />
                            </Button>
                            
                            {user.status === 'active' ? (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleSuspendUser(user.id)}
                              >
                                <UserX className="h-4 w-4" />
                              </Button>
                            ) : (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleActivateUser(user.id)}
                              >
                                <UserCheck className="h-4 w-4" />
                              </Button>
                            )}

                            {user.lockedUntil && user.lockedUntil > new Date() && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleUnlockUser(user.id)}
                              >
                                <Unlock className="h-4 w-4" />
                              </Button>
                            )}

                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleResetPassword(user.id)}
                            >
                              <Key className="h-4 w-4" />
                            </Button>

                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDeleteUser(user.id)}
                            >
                              <UserMinus className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="roles" className="space-y-4">
          {rolesData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Roles do Sistema</CardTitle>
                    <Button size="sm">
                      <UserPlus className="h-4 w-4 mr-2" />
                      Nova Role
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {rolesData.roles.map((role) => (
                      <div key={role.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{role.name}</h4>
                          <Badge variant={role.isSystem ? 'secondary' : 'outline'}>
                            {role.isSystem ? 'Sistema' : 'Custom'}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {role.description}
                        </p>
                        <div className="flex items-center justify-between text-sm">
                          <span>{role.permissions.length} permissões</span>
                          <span>{role.userCount} usuários</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Distribuição de Roles</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {rolesData.roles.map((role) => (
                      <div key={role.id} className="flex items-center justify-between">
                        <span className="text-sm">{role.name}</span>
                        <Badge variant="secondary">{role.userCount}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="permissions" className="space-y-4">
          {permissionsData && (
            <Card>
              <CardHeader>
                <CardTitle>Permissões do Sistema</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {permissionsData.permissions.map((permission) => (
                    <div key={permission.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{permission.name}</h4>
                        <Badge variant={permission.isSystem ? 'secondary' : 'outline'}>
                          {permission.isSystem ? 'Sistema' : 'Custom'}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        {permission.description}
                      </p>
                      <Badge variant="outline" className="text-xs">
                        {permission.category}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          {usersData && (
            <Card>
              <CardHeader>
                <CardTitle>Atividades Recentes</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Usuário</TableHead>
                      <TableHead>Ação</TableHead>
                      <TableHead>Recurso</TableHead>
                      <TableHead>IP</TableHead>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>Detalhes</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {usersData.activities.slice(0, 50).map((activity) => (
                      <TableRow key={activity.id}>
                        <TableCell className="font-medium">
                          {activity.userId}
                        </TableCell>
                        <TableCell>{activity.action}</TableCell>
                        <TableCell>{activity.resource}</TableCell>
                        <TableCell className="font-mono text-sm">
                          {showSensitiveData ? activity.ipAddress : '***.***.***.***'}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {formatTime(activity.timestamp)}
                        </TableCell>
                        <TableCell>
                          <div className="max-w-xs truncate" title={activity.details}>
                            {activity.details}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Dialog para criar/editar usuário */}
      <Dialog open={isUserDialogOpen} onOpenChange={setIsUserDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {selectedUser ? 'Editar Usuário' : 'Novo Usuário'}
            </DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Nome</label>
              <Input placeholder="Nome" defaultValue={selectedUser?.firstName} />
            </div>
            <div>
              <label className="text-sm font-medium">Sobrenome</label>
              <Input placeholder="Sobrenome" defaultValue={selectedUser?.lastName} />
            </div>
            <div>
              <label className="text-sm font-medium">Username</label>
              <Input placeholder="Username" defaultValue={selectedUser?.username} />
            </div>
            <div>
              <label className="text-sm font-medium">Email</label>
              <Input type="email" placeholder="Email" defaultValue={selectedUser?.email} />
            </div>
            <div>
              <label className="text-sm font-medium">Telefone</label>
              <Input placeholder="Telefone" defaultValue={selectedUser?.phone} />
            </div>
            <div>
              <label className="text-sm font-medium">Departamento</label>
              <Input placeholder="Departamento" defaultValue={selectedUser?.department} />
            </div>
            <div className="col-span-2">
              <label className="text-sm font-medium">Roles</label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {rolesData?.roles.map(role => (
                  <div key={role.id} className="flex items-center space-x-2">
                    <Checkbox id={role.id} />
                    <label htmlFor={role.id} className="text-sm">
                      {role.name}
                    </label>
                  </div>
                ))}
              </div>
            </div>
            <div className="col-span-2 flex justify-end gap-2">
              <Button variant="outline" onClick={() => setIsUserDialogOpen(false)}>
                Cancelar
              </Button>
              <Button>
                {selectedUser ? 'Atualizar' : 'Criar'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default UserManagement; 
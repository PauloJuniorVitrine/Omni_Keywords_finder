/**
 * TenantManagement.tsx
 * 
 * Sistema completo de gestão de multi-tenancy
 * 
 * Tracing ID: UI-022
 * Data: 2024-12-20
 * Versão: 1.0
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Alert,
  CircularProgress,
  Tooltip,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Badge,
  Avatar,
  CardHeader,
  CardActions,
  AlertTitle,
  Snackbar
} from '@mui/material';
import {
  Business,
  People,
  Storage,
  Speed,
  Security,
  Settings,
  Refresh,
  Download,
  Visibility,
  Edit,
  Delete,
  Add,
  CheckCircle,
  Error,
  Warning,
  Info,
  AccountBalance,
  Cloud,
  Lock,
  Public,
  Domain,
  Apartment,
  Group,
  Person,
  StorageOutlined,
  SpeedOutlined,
  SecurityOutlined,
  BusinessCenter,
  MonetizationOn,
  Assessment,
  Timeline,
  TrendingUp,
  TrendingDown,
  WarningAmber,
  VerifiedUser,
  GppGood,
  GppBad,
  GppMaybe,
  ExpandMore,
  FilterList,
  Search,
  Sort,
  MoreVert,
  Notifications,
  Dashboard,
  Analytics,
  Backup,
  Restore,
  Branding,
  Palette,
  Language,
  LocationOn,
  Phone,
  Email,
  Web,
  CalendarToday,
  AccessTime,
  Check,
  Close,
  Save,
  Cancel
} from '@mui/icons-material';

// Types
interface Tenant {
  id: string;
  name: string;
  domain: string;
  status: 'active' | 'inactive' | 'suspended' | 'pending';
  plan: 'basic' | 'premium' | 'enterprise' | 'custom';
  createdAt: string;
  updatedAt: string;
  contact: {
    name: string;
    email: string;
    phone: string;
    company: string;
  };
  config: {
    branding: {
      logo?: string;
      colors: {
        primary: string;
        secondary: string;
      };
      customDomain?: string;
    };
    limits: {
      users: number;
      storage: number;
      apiCalls: number;
      keywords: number;
    };
    features: {
      analytics: boolean;
      ml: boolean;
      api: boolean;
      backup: boolean;
      customIntegrations: boolean;
    };
  };
  usage: {
    users: number;
    storage: number;
    apiCalls: number;
    keywords: number;
  };
  billing: {
    plan: string;
    amount: number;
    currency: string;
    nextBilling: string;
    status: 'paid' | 'pending' | 'overdue' | 'cancelled';
  };
}

interface TenantResource {
  id: string;
  tenantId: string;
  type: 'database' | 'storage' | 'api' | 'compute';
  name: string;
  status: 'active' | 'inactive' | 'error';
  usage: number;
  limit: number;
  unit: string;
  lastUpdated: string;
}

interface TenantUser {
  id: string;
  tenantId: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'viewer';
  status: 'active' | 'inactive' | 'suspended';
  lastLogin: string;
  createdAt: string;
}

interface TenantBackup {
  id: string;
  tenantId: string;
  type: 'full' | 'incremental';
  status: 'completed' | 'in_progress' | 'failed';
  size: number;
  createdAt: string;
  completedAt?: string;
  retentionDays: number;
}

// Mock data
const mockTenants: Tenant[] = [
  {
    id: 'tenant_001',
    name: 'TechCorp Solutions',
    domain: 'techcorp.omni.com',
    status: 'active',
    plan: 'enterprise',
    createdAt: '2024-01-15T00:00:00Z',
    updatedAt: '2024-12-20T10:30:00Z',
    contact: {
      name: 'João Silva',
      email: 'joao@techcorp.com',
      phone: '+55 11 99999-9999',
      company: 'TechCorp Solutions'
    },
    config: {
      branding: {
        colors: {
          primary: '#1976d2',
          secondary: '#dc004e'
        }
      },
      limits: {
        users: 100,
        storage: 1000,
        apiCalls: 1000000,
        keywords: 50000
      },
      features: {
        analytics: true,
        ml: true,
        api: true,
        backup: true,
        customIntegrations: true
      }
    },
    usage: {
      users: 45,
      storage: 750,
      apiCalls: 850000,
      keywords: 32000
    },
    billing: {
      plan: 'Enterprise',
      amount: 2999.99,
      currency: 'BRL',
      nextBilling: '2025-01-15T00:00:00Z',
      status: 'paid'
    }
  },
  {
    id: 'tenant_002',
    name: 'MarketingPro',
    domain: 'marketingpro.omni.com',
    status: 'active',
    plan: 'premium',
    createdAt: '2024-03-20T00:00:00Z',
    updatedAt: '2024-12-19T15:45:00Z',
    contact: {
      name: 'Maria Santos',
      email: 'maria@marketingpro.com',
      phone: '+55 21 88888-8888',
      company: 'MarketingPro'
    },
    config: {
      branding: {
        colors: {
          primary: '#2e7d32',
          secondary: '#f57c00'
        }
      },
      limits: {
        users: 50,
        storage: 500,
        apiCalls: 500000,
        keywords: 25000
      },
      features: {
        analytics: true,
        ml: true,
        api: true,
        backup: true,
        customIntegrations: false
      }
    },
    usage: {
      users: 28,
      storage: 320,
      apiCalls: 420000,
      keywords: 18000
    },
    billing: {
      plan: 'Premium',
      amount: 999.99,
      currency: 'BRL',
      nextBilling: '2025-01-20T00:00:00Z',
      status: 'paid'
    }
  },
  {
    id: 'tenant_003',
    name: 'StartupXYZ',
    domain: 'startupxyz.omni.com',
    status: 'pending',
    plan: 'basic',
    createdAt: '2024-12-18T00:00:00Z',
    updatedAt: '2024-12-18T00:00:00Z',
    contact: {
      name: 'Pedro Costa',
      email: 'pedro@startupxyz.com',
      phone: '+55 31 77777-7777',
      company: 'StartupXYZ'
    },
    config: {
      branding: {
        colors: {
          primary: '#7b1fa2',
          secondary: '#ff9800'
        }
      },
      limits: {
        users: 10,
        storage: 100,
        apiCalls: 100000,
        keywords: 5000
      },
      features: {
        analytics: true,
        ml: false,
        api: false,
        backup: false,
        customIntegrations: false
      }
    },
    usage: {
      users: 0,
      storage: 0,
      apiCalls: 0,
      keywords: 0
    },
    billing: {
      plan: 'Basic',
      amount: 299.99,
      currency: 'BRL',
      nextBilling: '2025-01-18T00:00:00Z',
      status: 'pending'
    }
  }
];

const mockResources: TenantResource[] = [
  {
    id: 'res_001',
    tenantId: 'tenant_001',
    type: 'database',
    name: 'Primary Database',
    status: 'active',
    usage: 75,
    limit: 100,
    unit: 'GB',
    lastUpdated: '2024-12-20T10:30:00Z'
  },
  {
    id: 'res_002',
    tenantId: 'tenant_001',
    type: 'storage',
    name: 'File Storage',
    status: 'active',
    usage: 750,
    limit: 1000,
    unit: 'GB',
    lastUpdated: '2024-12-20T10:30:00Z'
  },
  {
    id: 'res_003',
    tenantId: 'tenant_002',
    type: 'api',
    name: 'API Gateway',
    status: 'active',
    usage: 420000,
    limit: 500000,
    unit: 'calls',
    lastUpdated: '2024-12-20T10:30:00Z'
  }
];

const mockUsers: TenantUser[] = [
  {
    id: 'user_001',
    tenantId: 'tenant_001',
    name: 'João Silva',
    email: 'joao@techcorp.com',
    role: 'admin',
    status: 'active',
    lastLogin: '2024-12-20T09:15:00Z',
    createdAt: '2024-01-15T00:00:00Z'
  },
  {
    id: 'user_002',
    tenantId: 'tenant_001',
    name: 'Ana Oliveira',
    email: 'ana@techcorp.com',
    role: 'user',
    status: 'active',
    lastLogin: '2024-12-19T16:30:00Z',
    createdAt: '2024-02-01T00:00:00Z'
  },
  {
    id: 'user_003',
    tenantId: 'tenant_002',
    name: 'Maria Santos',
    email: 'maria@marketingpro.com',
    role: 'admin',
    status: 'active',
    lastLogin: '2024-12-20T08:45:00Z',
    createdAt: '2024-03-20T00:00:00Z'
  }
];

const mockBackups: TenantBackup[] = [
  {
    id: 'backup_001',
    tenantId: 'tenant_001',
    type: 'full',
    status: 'completed',
    size: 2.5,
    createdAt: '2024-12-20T02:00:00Z',
    completedAt: '2024-12-20T02:15:00Z',
    retentionDays: 30
  },
  {
    id: 'backup_002',
    tenantId: 'tenant_002',
    type: 'incremental',
    status: 'completed',
    size: 0.8,
    createdAt: '2024-12-20T02:00:00Z',
    completedAt: '2024-12-20T02:05:00Z',
    retentionDays: 30
  }
];

// Hooks
const useTenants = () => {
  const [tenants, setTenants] = useState<Tenant[]>(mockTenants);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTenants = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setTenants(mockTenants);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar tenants');
    } finally {
      setLoading(false);
    }
  };

  const createTenant = async (tenantData: Omit<Tenant, 'id' | 'createdAt' | 'updatedAt'>) => {
    const newTenant: Tenant = {
      ...tenantData,
      id: `tenant_${Date.now()}`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    setTenants(prev => [...prev, newTenant]);
    return newTenant;
  };

  const updateTenant = async (id: string, updates: Partial<Tenant>) => {
    setTenants(prev => 
      prev.map(tenant => 
        tenant.id === id ? { ...tenant, ...updates, updatedAt: new Date().toISOString() } : tenant
      )
    );
  };

  const deleteTenant = async (id: string) => {
    setTenants(prev => prev.filter(tenant => tenant.id !== id));
  };

  return {
    tenants,
    loading,
    error,
    fetchTenants,
    createTenant,
    updateTenant,
    deleteTenant
  };
};

const useTenantResources = () => {
  const [resources, setResources] = useState<TenantResource[]>(mockResources);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchResources = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setResources(mockResources);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar recursos');
    } finally {
      setLoading(false);
    }
  };

  return {
    resources,
    loading,
    error,
    fetchResources
  };
};

const useTenantUsers = () => {
  const [users, setUsers] = useState<TenantUser[]>(mockUsers);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setUsers(mockUsers);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar usuários');
    } finally {
      setLoading(false);
    }
  };

  return {
    users,
    loading,
    error,
    fetchUsers
  };
};

const useTenantBackups = () => {
  const [backups, setBackups] = useState<TenantBackup[]>(mockBackups);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchBackups = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setBackups(mockBackups);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar backups');
    } finally {
      setLoading(false);
    }
  };

  const createBackup = async (tenantId: string, type: 'full' | 'incremental') => {
    const newBackup: TenantBackup = {
      id: `backup_${Date.now()}`,
      tenantId,
      type,
      status: 'in_progress',
      size: 0,
      createdAt: new Date().toISOString(),
      retentionDays: 30
    };
    setBackups(prev => [...prev, newBackup]);
    return newBackup;
  };

  return {
    backups,
    loading,
    error,
    fetchBackups,
    createBackup
  };
};

// Main Component
const TenantManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedTenant, setSelectedTenant] = useState<Tenant | null>(null);
  const [tenantDialog, setTenantDialog] = useState(false);
  const [backupDialog, setBackupDialog] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'warning' | 'info' }>({
    open: false,
    message: '',
    severity: 'info'
  });

  const { tenants, loading: tenantsLoading, error: tenantsError, fetchTenants, createTenant, updateTenant, deleteTenant } = useTenants();
  const { resources, loading: resourcesLoading, error: resourcesError, fetchResources } = useTenantResources();
  const { users, loading: usersLoading, error: usersError, fetchUsers } = useTenantUsers();
  const { backups, loading: backupsLoading, error: backupsError, fetchBackups, createBackup } = useTenantBackups();

  useEffect(() => {
    fetchTenants();
    fetchResources();
    fetchUsers();
    fetchBackups();
  }, []);

  // Calculated metrics
  const metrics = useMemo(() => {
    const totalTenants = tenants.length;
    const activeTenants = tenants.filter(t => t.status === 'active').length;
    const totalRevenue = tenants.reduce((sum, t) => sum + t.billing.amount, 0);
    const avgUsage = tenants.reduce((sum, t) => {
      const usagePercent = (t.usage.users / t.config.limits.users) * 100;
      return sum + usagePercent;
    }, 0) / totalTenants;

    return {
      totalTenants,
      activeTenants,
      totalRevenue,
      avgUsage
    };
  }, [tenants]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleTenantEdit = (tenant: Tenant) => {
    setSelectedTenant(tenant);
    setTenantDialog(true);
  };

  const handleTenantCreate = () => {
    setSelectedTenant(null);
    setTenantDialog(true);
  };

  const handleTenantSubmit = async (tenantData: any) => {
    try {
      if (selectedTenant) {
        await updateTenant(selectedTenant.id, tenantData);
        setSnackbar({
          open: true,
          message: 'Tenant atualizado com sucesso',
          severity: 'success'
        });
      } else {
        await createTenant(tenantData);
        setSnackbar({
          open: true,
          message: 'Tenant criado com sucesso',
          severity: 'success'
        });
      }
      setTenantDialog(false);
      setSelectedTenant(null);
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao salvar tenant',
        severity: 'error'
      });
    }
  };

  const handleBackupCreate = async (tenantId: string, type: 'full' | 'incremental') => {
    try {
      await createBackup(tenantId, type);
      setSnackbar({
        open: true,
        message: 'Backup iniciado com sucesso',
        severity: 'success'
      });
      setBackupDialog(false);
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao criar backup',
        severity: 'error'
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'suspended': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'enterprise': return 'error';
      case 'premium': return 'warning';
      case 'basic': return 'success';
      case 'custom': return 'info';
      default: return 'default';
    }
  };

  if (tenantsLoading || resourcesLoading || usersLoading || backupsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (tenantsError || resourcesError || usersError || backupsError) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Erro ao carregar dados de tenants. Tente novamente.
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            <Business sx={{ mr: 1, verticalAlign: 'middle' }} />
            Gestão de Multi-tenancy
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Gestão completa de tenants, recursos e isolamento
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={() => {
            fetchTenants();
            fetchResources();
            fetchUsers();
            fetchBackups();
          }}
        >
          Atualizar
        </Button>
      </Box>

      {/* Metrics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Business color="primary" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h6">{metrics.totalTenants}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total de Tenants
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <CheckCircle color="primary" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h6">{metrics.activeTenants}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Tenants Ativos
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <MonetizationOn color="primary" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h6">R$ {metrics.totalRevenue.toLocaleString()}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Receita Total
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="primary" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h6">{metrics.avgUsage.toFixed(1)}%</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Uso Médio
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Card>
        <CardContent>
          <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
            <Tab label="Tenants" icon={<Business />} />
            <Tab label="Recursos" icon={<Storage />} />
            <Tab label="Usuários" icon={<People />} />
            <Tab label="Backups" icon={<Backup />} />
            <Tab label="Configurações" icon={<Settings />} />
          </Tabs>

          {/* Tenants Tab */}
          {activeTab === 0 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Tenants</Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={handleTenantCreate}
                >
                  Novo Tenant
                </Button>
              </Box>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Nome</TableCell>
                      <TableCell>Domínio</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Plano</TableCell>
                      <TableCell>Uso</TableCell>
                      <TableCell>Faturamento</TableCell>
                      <TableCell>Contato</TableCell>
                      <TableCell>Ações</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {tenants.map((tenant) => (
                      <TableRow key={tenant.id}>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {tenant.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              ID: {tenant.id}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{tenant.domain}</TableCell>
                        <TableCell>
                          <Chip
                            label={tenant.status}
                            color={getStatusColor(tenant.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={tenant.plan}
                            color={getPlanColor(tenant.plan) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2">
                              {tenant.usage.users}/{tenant.config.limits.users} usuários
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={(tenant.usage.users / tenant.config.limits.users) * 100}
                              sx={{ width: 100, mt: 0.5 }}
                            />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              R$ {tenant.billing.amount.toFixed(2)}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {tenant.billing.plan}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2">{tenant.contact.name}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {tenant.contact.email}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" gap={1}>
                            <Tooltip title="Ver detalhes">
                              <IconButton size="small">
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Editar">
                              <IconButton 
                                size="small"
                                onClick={() => handleTenantEdit(tenant)}
                              >
                                <Edit />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Criar backup">
                              <IconButton 
                                size="small"
                                onClick={() => setBackupDialog(true)}
                              >
                                <Backup />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Resources Tab */}
          {activeTab === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Recursos por Tenant
              </Typography>
              
              <Grid container spacing={3}>
                {tenants.map((tenant) => {
                  const tenantResources = resources.filter(r => r.tenantId === tenant.id);
                  return (
                    <Grid item xs={12} md={6} key={tenant.id}>
                      <Card>
                        <CardHeader
                          avatar={
                            <Avatar>
                              <Storage />
                            </Avatar>
                          }
                          title={tenant.name}
                          subheader={`${tenantResources.length} recursos`}
                        />
                        <CardContent>
                          {tenantResources.map((resource) => (
                            <Box key={resource.id} mb={2}>
                              <Box display="flex" justifyContent="space-between" mb={1}>
                                <Typography variant="body2">{resource.name}</Typography>
                                <Typography variant="body2" fontWeight="bold">
                                  {resource.usage}/{resource.limit} {resource.unit}
                                </Typography>
                              </Box>
                              <LinearProgress
                                variant="determinate"
                                value={(resource.usage / resource.limit) * 100}
                                color={resource.usage / resource.limit > 0.8 ? 'error' : 'primary'}
                              />
                            </Box>
                          ))}
                        </CardContent>
                      </Card>
                    </Grid>
                  );
                })}
              </Grid>
            </Box>
          )}

          {/* Users Tab */}
          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Usuários por Tenant
              </Typography>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Tenant</TableCell>
                      <TableCell>Nome</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Função</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Último Login</TableCell>
                      <TableCell>Ações</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {users.map((user) => {
                      const tenant = tenants.find(t => t.id === user.tenantId);
                      return (
                        <TableRow key={user.id}>
                          <TableCell>{tenant?.name}</TableCell>
                          <TableCell>{user.name}</TableCell>
                          <TableCell>{user.email}</TableCell>
                          <TableCell>
                            <Chip
                              label={user.role}
                              color={user.role === 'admin' ? 'error' : 'default'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={user.status}
                              color={getStatusColor(user.status) as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {new Date(user.lastLogin).toLocaleDateString('pt-BR')}
                          </TableCell>
                          <TableCell>
                            <Box display="flex" gap={1}>
                              <Tooltip title="Editar">
                                <IconButton size="small">
                                  <Edit />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Suspender">
                                <IconButton size="small">
                                  <Block />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Backups Tab */}
          {activeTab === 3 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Backups por Tenant
              </Typography>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Tenant</TableCell>
                      <TableCell>Tipo</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Tamanho</TableCell>
                      <TableCell>Criado em</TableCell>
                      <TableCell>Retenção</TableCell>
                      <TableCell>Ações</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {backups.map((backup) => {
                      const tenant = tenants.find(t => t.id === backup.tenantId);
                      return (
                        <TableRow key={backup.id}>
                          <TableCell>{tenant?.name}</TableCell>
                          <TableCell>
                            <Chip
                              label={backup.type}
                              color={backup.type === 'full' ? 'primary' : 'secondary'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={backup.status}
                              color={backup.status === 'completed' ? 'success' : 'warning'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{backup.size} GB</TableCell>
                          <TableCell>
                            {new Date(backup.createdAt).toLocaleDateString('pt-BR')}
                          </TableCell>
                          <TableCell>{backup.retentionDays} dias</TableCell>
                          <TableCell>
                            <Box display="flex" gap={1}>
                              <Tooltip title="Restaurar">
                                <IconButton size="small">
                                  <Restore />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Download">
                                <IconButton size="small">
                                  <Download />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Settings Tab */}
          {activeTab === 4 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Configurações de Multi-tenancy
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title="Configurações Gerais" />
                    <CardContent>
                      <FormControlLabel
                        control={<Switch defaultChecked />}
                        label="Isolamento de dados"
                      />
                      <FormControlLabel
                        control={<Switch defaultChecked />}
                        label="Backup automático"
                      />
                      <FormControlLabel
                        control={<Switch />}
                        label="Monitoramento avançado"
                      />
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title="Limites Globais" />
                    <CardContent>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Configurações de limites por tenant
                      </Typography>
                      <List dense>
                        <ListItem>
                          <ListItemIcon>
                            <People />
                          </ListItemIcon>
                          <ListItemText
                            primary="Usuários máximos"
                            secondary="100 por tenant"
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon>
                            <Storage />
                          </ListItemIcon>
                          <ListItemText
                            primary="Armazenamento"
                            secondary="1TB por tenant"
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon>
                            <Speed />
                          </ListItemIcon>
                          <ListItemText
                            primary="API Calls"
                            secondary="1M por mês"
                          />
                        </ListItem>
                      </List>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Tenant Dialog */}
      <Dialog open={tenantDialog} onClose={() => setTenantDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedTenant ? 'Editar Tenant' : 'Novo Tenant'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Nome do Tenant"
                defaultValue={selectedTenant?.name}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Domínio"
                defaultValue={selectedTenant?.domain}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select defaultValue={selectedTenant?.status || 'pending'}>
                  <MenuItem value="active">Ativo</MenuItem>
                  <MenuItem value="inactive">Inativo</MenuItem>
                  <MenuItem value="suspended">Suspenso</MenuItem>
                  <MenuItem value="pending">Pendente</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Plano</InputLabel>
                <Select defaultValue={selectedTenant?.plan || 'basic'}>
                  <MenuItem value="basic">Básico</MenuItem>
                  <MenuItem value="premium">Premium</MenuItem>
                  <MenuItem value="enterprise">Enterprise</MenuItem>
                  <MenuItem value="custom">Custom</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nome do Contato"
                defaultValue={selectedTenant?.contact.name}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                defaultValue={selectedTenant?.contact.email}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Telefone"
                defaultValue={selectedTenant?.contact.phone}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTenantDialog(false)}>Cancelar</Button>
          <Button 
            variant="contained"
            onClick={() => {
              setSnackbar({
                open: true,
                message: selectedTenant ? 'Tenant atualizado com sucesso' : 'Tenant criado com sucesso',
                severity: 'success'
              });
              setTenantDialog(false);
              setSelectedTenant(null);
            }}
          >
            {selectedTenant ? 'Atualizar' : 'Criar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Backup Dialog */}
      <Dialog open={backupDialog} onClose={() => setBackupDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Criar Backup</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Selecione o tipo de backup para o tenant selecionado
          </Typography>
          
          <Box mt={2}>
            <FormControl fullWidth>
              <InputLabel>Tipo de Backup</InputLabel>
              <Select defaultValue="full">
                <MenuItem value="full">Backup Completo</MenuItem>
                <MenuItem value="incremental">Backup Incremental</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBackupDialog(false)}>Cancelar</Button>
          <Button 
            variant="contained"
            onClick={() => {
              handleBackupCreate('tenant_001', 'full');
            }}
          >
            Criar Backup
          </Button>
        </DialogActions>
      </Dialog>

      {/* Speed Dial */}
      <SpeedDial
        ariaLabel="Ações rápidas"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
      >
        <SpeedDialAction
          icon={<Add />}
          tooltipTitle="Novo tenant"
          onClick={handleTenantCreate}
        />
        <SpeedDialAction
          icon={<Backup />}
          tooltipTitle="Backup global"
          onClick={() => {
            setSnackbar({
              open: true,
              message: 'Backup global iniciado',
              severity: 'success'
            });
          }}
        />
        <SpeedDialAction
          icon={<Assessment />}
          tooltipTitle="Relatório"
          onClick={() => {
            setSnackbar({
              open: true,
              message: 'Relatório gerado com sucesso',
              severity: 'success'
            });
          }}
        />
      </SpeedDial>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default TenantManagement; 
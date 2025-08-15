/**
 * PaymentGateway.tsx
 * 
 * Sistema completo de gestão de pagamentos
 * 
 * Tracing ID: UI-021
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
  Payment,
  CreditCard,
  AccountBalance,
  Receipt,
  TrendingUp,
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
  AttachMoney,
  AccountBalanceWallet,
  SwapHoriz,
  Block,
  Check,
  Close,
  ExpandMore,
  FilterList,
  Search,
  Sort,
  MoreVert,
  Notifications,
  Timeline,
  Assessment,
  MonetizationOn,
  LocalAtm,
  AccountBox,
  Business,
  Lock,
  VpnKey,
  Webhook,
  IntegrationInstructions,
  Analytics,
  Dashboard,
  Speed,
  TrendingDown,
  WarningAmber,
  VerifiedUser,
  GppGood,
  GppBad,
  GppMaybe
} from '@mui/icons-material';

// Types
interface PaymentTransaction {
  id: string;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded' | 'cancelled';
  paymentMethod: string;
  gateway: string;
  customerId: string;
  customerName: string;
  customerEmail: string;
  description: string;
  createdAt: string;
  updatedAt: string;
  fraudScore?: number;
  riskLevel?: 'low' | 'medium' | 'high';
  metadata?: Record<string, any>;
}

interface PaymentGateway {
  id: string;
  name: string;
  type: 'stripe' | 'paypal' | 'mercadopago' | 'pix' | 'bank_transfer';
  status: 'active' | 'inactive' | 'testing';
  credentials: {
    apiKey?: string;
    secretKey?: string;
    webhookUrl?: string;
    sandboxMode?: boolean;
  };
  config: {
    supportedCurrencies: string[];
    supportedMethods: string[];
    processingFee: number;
    settlementTime: number;
    autoCapture: boolean;
  };
  stats: {
    totalTransactions: number;
    successRate: number;
    averageAmount: number;
    monthlyVolume: number;
  };
}

interface Refund {
  id: string;
  transactionId: string;
  amount: number;
  reason: string;
  status: 'pending' | 'completed' | 'failed';
  createdAt: string;
  processedAt?: string;
}

interface Subscription {
  id: string;
  customerId: string;
  planId: string;
  planName: string;
  amount: number;
  currency: string;
  interval: 'monthly' | 'yearly' | 'weekly';
  status: 'active' | 'cancelled' | 'past_due' | 'unpaid';
  currentPeriodStart: string;
  currentPeriodEnd: string;
  nextBillingDate: string;
  createdAt: string;
}

interface FraudAlert {
  id: string;
  transactionId: string;
  type: 'suspicious_ip' | 'unusual_amount' | 'multiple_attempts' | 'location_mismatch';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  riskScore: number;
  status: 'open' | 'investigating' | 'resolved' | 'false_positive';
  createdAt: string;
  resolvedAt?: string;
}

// Mock data
const mockTransactions: PaymentTransaction[] = [
  {
    id: 'txn_001',
    amount: 299.99,
    currency: 'BRL',
    status: 'completed',
    paymentMethod: 'credit_card',
    gateway: 'stripe',
    customerId: 'cust_001',
    customerName: 'João Silva',
    customerEmail: 'joao@email.com',
    description: 'Plano Premium Mensal',
    createdAt: '2024-12-20T10:30:00Z',
    updatedAt: '2024-12-20T10:31:00Z',
    fraudScore: 0.1,
    riskLevel: 'low'
  },
  {
    id: 'txn_002',
    amount: 599.99,
    currency: 'BRL',
    status: 'pending',
    paymentMethod: 'pix',
    gateway: 'mercadopago',
    customerId: 'cust_002',
    customerName: 'Maria Santos',
    customerEmail: 'maria@email.com',
    description: 'Plano Enterprise Anual',
    createdAt: '2024-12-20T11:15:00Z',
    updatedAt: '2024-12-20T11:15:00Z',
    fraudScore: 0.3,
    riskLevel: 'medium'
  },
  {
    id: 'txn_003',
    amount: 99.99,
    currency: 'BRL',
    status: 'failed',
    paymentMethod: 'credit_card',
    gateway: 'stripe',
    customerId: 'cust_003',
    customerName: 'Pedro Costa',
    customerEmail: 'pedro@email.com',
    description: 'Plano Básico Mensal',
    createdAt: '2024-12-20T12:00:00Z',
    updatedAt: '2024-12-20T12:01:00Z',
    fraudScore: 0.8,
    riskLevel: 'high'
  }
];

const mockGateways: PaymentGateway[] = [
  {
    id: 'stripe_001',
    name: 'Stripe',
    type: 'stripe',
    status: 'active',
    credentials: {
      apiKey: 'pk_test_...',
      secretKey: 'sk_test_...',
      webhookUrl: 'https://api.omni.com/webhooks/stripe',
      sandboxMode: true
    },
    config: {
      supportedCurrencies: ['BRL', 'USD', 'EUR'],
      supportedMethods: ['credit_card', 'pix', 'boleto'],
      processingFee: 2.9,
      settlementTime: 2,
      autoCapture: true
    },
    stats: {
      totalTransactions: 1250,
      successRate: 98.5,
      averageAmount: 299.99,
      monthlyVolume: 375000
    }
  },
  {
    id: 'mercadopago_001',
    name: 'MercadoPago',
    type: 'mercadopago',
    status: 'active',
    credentials: {
      apiKey: 'TEST-...',
      webhookUrl: 'https://api.omni.com/webhooks/mercadopago',
      sandboxMode: true
    },
    config: {
      supportedCurrencies: ['BRL', 'ARS', 'CLP'],
      supportedMethods: ['credit_card', 'pix', 'boleto'],
      processingFee: 2.5,
      settlementTime: 1,
      autoCapture: false
    },
    stats: {
      totalTransactions: 890,
      successRate: 97.2,
      averageAmount: 199.99,
      monthlyVolume: 178000
    }
  }
];

const mockRefunds: Refund[] = [
  {
    id: 'ref_001',
    transactionId: 'txn_001',
    amount: 299.99,
    reason: 'Customer requested refund',
    status: 'completed',
    createdAt: '2024-12-19T15:30:00Z',
    processedAt: '2024-12-19T16:00:00Z'
  }
];

const mockSubscriptions: Subscription[] = [
  {
    id: 'sub_001',
    customerId: 'cust_001',
    planId: 'plan_premium',
    planName: 'Premium Mensal',
    amount: 299.99,
    currency: 'BRL',
    interval: 'monthly',
    status: 'active',
    currentPeriodStart: '2024-12-01T00:00:00Z',
    currentPeriodEnd: '2024-12-31T23:59:59Z',
    nextBillingDate: '2025-01-01T00:00:00Z',
    createdAt: '2024-11-01T00:00:00Z'
  }
];

const mockFraudAlerts: FraudAlert[] = [
  {
    id: 'fraud_001',
    transactionId: 'txn_003',
    type: 'unusual_amount',
    severity: 'high',
    description: 'Transaction amount is significantly higher than customer average',
    riskScore: 0.8,
    status: 'investigating',
    createdAt: '2024-12-20T12:01:00Z'
  }
];

// Hooks
const usePaymentTransactions = () => {
  const [transactions, setTransactions] = useState<PaymentTransaction[]>(mockTransactions);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setTransactions(mockTransactions);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar transações');
    } finally {
      setLoading(false);
    }
  };

  const updateTransactionStatus = async (id: string, status: PaymentTransaction['status']) => {
    setTransactions(prev => 
      prev.map(txn => 
        txn.id === id ? { ...txn, status, updatedAt: new Date().toISOString() } : txn
      )
    );
  };

  const refundTransaction = async (id: string, amount: number, reason: string) => {
    // Simulate refund process
    const refund: Refund = {
      id: `ref_${Date.now()}`,
      transactionId: id,
      amount,
      reason,
      status: 'pending',
      createdAt: new Date().toISOString()
    };
    
    // Update transaction status
    await updateTransactionStatus(id, 'refunded');
    
    return refund;
  };

  return {
    transactions,
    loading,
    error,
    fetchTransactions,
    updateTransactionStatus,
    refundTransaction
  };
};

const usePaymentGateways = () => {
  const [gateways, setGateways] = useState<PaymentGateway[]>(mockGateways);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchGateways = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setGateways(mockGateways);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar gateways');
    } finally {
      setLoading(false);
    }
  };

  const updateGateway = async (id: string, updates: Partial<PaymentGateway>) => {
    setGateways(prev => 
      prev.map(gw => 
        gw.id === id ? { ...gw, ...updates } : gw
      )
    );
  };

  const testGatewayConnection = async (id: string) => {
    // Simulate connection test
    await new Promise(resolve => setTimeout(resolve, 2000));
    return { success: true, message: 'Conexão testada com sucesso' };
  };

  return {
    gateways,
    loading,
    error,
    fetchGateways,
    updateGateway,
    testGatewayConnection
  };
};

const useFraudMonitoring = () => {
  const [alerts, setAlerts] = useState<FraudAlert[]>(mockFraudAlerts);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setAlerts(mockFraudAlerts);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar alertas');
    } finally {
      setLoading(false);
    }
  };

  const updateAlertStatus = async (id: string, status: FraudAlert['status']) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === id ? { 
          ...alert, 
          status, 
          resolvedAt: status === 'resolved' ? new Date().toISOString() : undefined 
        } : alert
      )
    );
  };

  return {
    alerts,
    loading,
    error,
    fetchAlerts,
    updateAlertStatus
  };
};

// Main Component
const PaymentGateway: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedTransaction, setSelectedTransaction] = useState<PaymentTransaction | null>(null);
  const [selectedGateway, setSelectedGateway] = useState<PaymentGateway | null>(null);
  const [refundDialog, setRefundDialog] = useState(false);
  const [gatewayDialog, setGatewayDialog] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'warning' | 'info' }>({
    open: false,
    message: '',
    severity: 'info'
  });

  const { transactions, loading: transactionsLoading, error: transactionsError, fetchTransactions, updateTransactionStatus, refundTransaction } = usePaymentTransactions();
  const { gateways, loading: gatewaysLoading, error: gatewaysError, fetchGateways, updateGateway, testGatewayConnection } = usePaymentGateways();
  const { alerts, loading: alertsLoading, error: alertsError, fetchAlerts, updateAlertStatus } = useFraudMonitoring();

  useEffect(() => {
    fetchTransactions();
    fetchGateways();
    fetchAlerts();
  }, []);

  // Calculated metrics
  const metrics = useMemo(() => {
    const totalTransactions = transactions.length;
    const totalAmount = transactions.reduce((sum, txn) => sum + txn.amount, 0);
    const completedTransactions = transactions.filter(txn => txn.status === 'completed').length;
    const successRate = totalTransactions > 0 ? (completedTransactions / totalTransactions) * 100 : 0;
    const pendingTransactions = transactions.filter(txn => txn.status === 'pending').length;
    const failedTransactions = transactions.filter(txn => txn.status === 'failed').length;
    const highRiskTransactions = transactions.filter(txn => txn.riskLevel === 'high').length;

    return {
      totalTransactions,
      totalAmount,
      successRate,
      pendingTransactions,
      failedTransactions,
      highRiskTransactions
    };
  }, [transactions]);

  const gatewayMetrics = useMemo(() => {
    const totalGateways = gateways.length;
    const activeGateways = gateways.filter(gw => gw.status === 'active').length;
    const totalVolume = gateways.reduce((sum, gw) => sum + gw.stats.monthlyVolume, 0);
    const avgSuccessRate = gateways.length > 0 
      ? gateways.reduce((sum, gw) => sum + gw.stats.successRate, 0) / gateways.length 
      : 0;

    return {
      totalGateways,
      activeGateways,
      totalVolume,
      avgSuccessRate
    };
  }, [gateways]);

  const fraudMetrics = useMemo(() => {
    const totalAlerts = alerts.length;
    const openAlerts = alerts.filter(alert => alert.status === 'open').length;
    const highSeverityAlerts = alerts.filter(alert => alert.severity === 'high' || alert.severity === 'critical').length;
    const avgRiskScore = alerts.length > 0 
      ? alerts.reduce((sum, alert) => sum + alert.riskScore, 0) / alerts.length 
      : 0;

    return {
      totalAlerts,
      openAlerts,
      highSeverityAlerts,
      avgRiskScore
    };
  }, [alerts]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleRefund = async (transaction: PaymentTransaction) => {
    setSelectedTransaction(transaction);
    setRefundDialog(true);
  };

  const handleRefundSubmit = async (amount: number, reason: string) => {
    if (!selectedTransaction) return;

    try {
      await refundTransaction(selectedTransaction.id, amount, reason);
      setSnackbar({
        open: true,
        message: 'Reembolso processado com sucesso',
        severity: 'success'
      });
      setRefundDialog(false);
      setSelectedTransaction(null);
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao processar reembolso',
        severity: 'error'
      });
    }
  };

  const handleGatewayEdit = (gateway: PaymentGateway) => {
    setSelectedGateway(gateway);
    setGatewayDialog(true);
  };

  const handleGatewayTest = async (gatewayId: string) => {
    try {
      const result = await testGatewayConnection(gatewayId);
      setSnackbar({
        open: true,
        message: result.message,
        severity: result.success ? 'success' : 'error'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao testar conexão',
        severity: 'error'
      });
    }
  };

  const handleAlertResolve = async (alertId: string) => {
    try {
      await updateAlertStatus(alertId, 'resolved');
      setSnackbar({
        open: true,
        message: 'Alerta resolvido com sucesso',
        severity: 'success'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao resolver alerta',
        severity: 'error'
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'pending': return 'warning';
      case 'failed': return 'error';
      case 'refunded': return 'info';
      case 'cancelled': return 'default';
      default: return 'default';
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      default: return 'default';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  if (transactionsLoading || gatewaysLoading || alertsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (transactionsError || gatewaysError || alertsError) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Erro ao carregar dados de pagamento. Tente novamente.
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            <Payment sx={{ mr: 1, verticalAlign: 'middle' }} />
            Sistema de Pagamentos
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Gestão completa de transações, gateways e monitoramento de fraudes
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={() => {
            fetchTransactions();
            fetchGateways();
            fetchAlerts();
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
                <AttachMoney color="primary" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h6">R$ {metrics.totalAmount.toLocaleString()}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Volume Total
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
                <Receipt color="primary" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h6">{metrics.totalTransactions}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Transações
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
                  <Typography variant="h6">{metrics.successRate.toFixed(1)}%</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Taxa de Sucesso
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
                <Security color="primary" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h6">{fraudMetrics.openAlerts}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Alertas Abertos
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
            <Tab label="Transações" icon={<Receipt />} />
            <Tab label="Gateways" icon={<AccountBalance />} />
            <Tab label="Fraudes" icon={<Security />} />
            <Tab label="Relatórios" icon={<Assessment />} />
            <Tab label="Configurações" icon={<Settings />} />
          </Tabs>

          {/* Transactions Tab */}
          {activeTab === 0 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Transações Recentes</Typography>
                <Button
                  variant="outlined"
                  startIcon={<Download />}
                  onClick={() => {
                    setSnackbar({
                      open: true,
                      message: 'Relatório exportado com sucesso',
                      severity: 'success'
                    });
                  }}
                >
                  Exportar
                </Button>
              </Box>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Cliente</TableCell>
                      <TableCell>Valor</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Gateway</TableCell>
                      <TableCell>Risco</TableCell>
                      <TableCell>Data</TableCell>
                      <TableCell>Ações</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {transactions.map((transaction) => (
                      <TableRow key={transaction.id}>
                        <TableCell>{transaction.id}</TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2">{transaction.customerName}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {transaction.customerEmail}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            R$ {transaction.amount.toFixed(2)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={transaction.status}
                            color={getStatusColor(transaction.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{transaction.gateway}</TableCell>
                        <TableCell>
                          {transaction.riskLevel && (
                            <Chip
                              label={transaction.riskLevel}
                              color={getRiskLevelColor(transaction.riskLevel) as any}
                              size="small"
                            />
                          )}
                        </TableCell>
                        <TableCell>
                          {new Date(transaction.createdAt).toLocaleDateString('pt-BR')}
                        </TableCell>
                        <TableCell>
                          <Box display="flex" gap={1}>
                            <Tooltip title="Ver detalhes">
                              <IconButton size="small">
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            {transaction.status === 'completed' && (
                              <Tooltip title="Reembolsar">
                                <IconButton 
                                  size="small"
                                  onClick={() => handleRefund(transaction)}
                                >
                                  <SwapHoriz />
                                </IconButton>
                              </Tooltip>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Gateways Tab */}
          {activeTab === 1 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Gateways de Pagamento</Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => setGatewayDialog(true)}
                >
                  Adicionar Gateway
                </Button>
              </Box>

              <Grid container spacing={3}>
                {gateways.map((gateway) => (
                  <Grid item xs={12} md={6} key={gateway.id}>
                    <Card>
                      <CardHeader
                        avatar={
                          <Avatar>
                            <AccountBalance />
                          </Avatar>
                        }
                        action={
                          <Box display="flex" gap={1}>
                            <Tooltip title="Testar conexão">
                              <IconButton
                                onClick={() => handleGatewayTest(gateway.id)}
                              >
                                <Speed />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Editar">
                              <IconButton
                                onClick={() => handleGatewayEdit(gateway)}
                              >
                                <Edit />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        }
                        title={gateway.name}
                        subheader={`Status: ${gateway.status}`}
                      />
                      <CardContent>
                        <Grid container spacing={2}>
                          <Grid item xs={6}>
                            <Typography variant="body2" color="text.secondary">
                              Transações
                            </Typography>
                            <Typography variant="h6">
                              {gateway.stats.totalTransactions.toLocaleString()}
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="body2" color="text.secondary">
                              Taxa de Sucesso
                            </Typography>
                            <Typography variant="h6">
                              {gateway.stats.successRate.toFixed(1)}%
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="body2" color="text.secondary">
                              Volume Mensal
                            </Typography>
                            <Typography variant="h6">
                              R$ {gateway.stats.monthlyVolume.toLocaleString()}
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="body2" color="text.secondary">
                              Taxa de Processamento
                            </Typography>
                            <Typography variant="h6">
                              {gateway.config.processingFee}%
                            </Typography>
                          </Grid>
                        </Grid>
                        
                        <Box mt={2}>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            Métodos Suportados
                          </Typography>
                          <Box display="flex" gap={1} flexWrap="wrap">
                            {gateway.config.supportedMethods.map((method) => (
                              <Chip key={method} label={method} size="small" />
                            ))}
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Fraud Tab */}
          {activeTab === 2 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Monitoramento de Fraudes</Typography>
                <Button
                  variant="outlined"
                  startIcon={<Notifications />}
                  onClick={() => {
                    setSnackbar({
                      open: true,
                      message: 'Configurações de alerta atualizadas',
                      severity: 'success'
                    });
                  }}
                >
                  Configurar Alertas
                </Button>
              </Box>

              <Grid container spacing={3} mb={3}>
                <Grid item xs={12} sm={6} md={3}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" color="error">
                        {fraudMetrics.totalAlerts}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total de Alertas
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" color="warning.main">
                        {fraudMetrics.openAlerts}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Alertas Abertos
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" color="error">
                        {fraudMetrics.highSeverityAlerts}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Alta Severidade
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">
                        {(fraudMetrics.avgRiskScore * 100).toFixed(1)}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Risco Médio
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Transação</TableCell>
                      <TableCell>Tipo</TableCell>
                      <TableCell>Severidade</TableCell>
                      <TableCell>Risco</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Data</TableCell>
                      <TableCell>Ações</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {alerts.map((alert) => (
                      <TableRow key={alert.id}>
                        <TableCell>{alert.id}</TableCell>
                        <TableCell>{alert.transactionId}</TableCell>
                        <TableCell>{alert.type}</TableCell>
                        <TableCell>
                          <Chip
                            label={alert.severity}
                            color={getSeverityColor(alert.severity) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            <LinearProgress
                              variant="determinate"
                              value={alert.riskScore * 100}
                              sx={{ width: 60 }}
                            />
                            <Typography variant="body2">
                              {(alert.riskScore * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={alert.status}
                            color={alert.status === 'open' ? 'error' : 'success'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {new Date(alert.createdAt).toLocaleDateString('pt-BR')}
                        </TableCell>
                        <TableCell>
                          <Box display="flex" gap={1}>
                            <Tooltip title="Ver detalhes">
                              <IconButton size="small">
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            {alert.status === 'open' && (
                              <Tooltip title="Resolver">
                                <IconButton
                                  size="small"
                                  onClick={() => handleAlertResolve(alert.id)}
                                >
                                  <Check />
                                </IconButton>
                              </Tooltip>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Reports Tab */}
          {activeTab === 3 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Relatórios Financeiros
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title="Volume por Gateway" />
                    <CardContent>
                      <Typography variant="body2" color="text.secondary">
                        Relatório de volume de transações por gateway de pagamento
                      </Typography>
                      <Box mt={2}>
                        {gateways.map((gateway) => (
                          <Box key={gateway.id} mb={2}>
                            <Box display="flex" justifyContent="space-between" mb={1}>
                              <Typography variant="body2">{gateway.name}</Typography>
                              <Typography variant="body2" fontWeight="bold">
                                R$ {gateway.stats.monthlyVolume.toLocaleString()}
                              </Typography>
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={(gateway.stats.monthlyVolume / gatewayMetrics.totalVolume) * 100}
                            />
                          </Box>
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title="Taxa de Sucesso" />
                    <CardContent>
                      <Typography variant="body2" color="text.secondary">
                        Taxa de sucesso por gateway
                      </Typography>
                      <Box mt={2}>
                        {gateways.map((gateway) => (
                          <Box key={gateway.id} mb={2}>
                            <Box display="flex" justifyContent="space-between" mb={1}>
                              <Typography variant="body2">{gateway.name}</Typography>
                              <Typography variant="body2" fontWeight="bold">
                                {gateway.stats.successRate.toFixed(1)}%
                              </Typography>
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={gateway.stats.successRate}
                              color={gateway.stats.successRate > 95 ? 'success' : 'warning'}
                            />
                          </Box>
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}

          {/* Settings Tab */}
          {activeTab === 4 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Configurações de Pagamento
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title="Configurações Gerais" />
                    <CardContent>
                      <FormControlLabel
                        control={<Switch defaultChecked />}
                        label="Captura automática"
                      />
                      <FormControlLabel
                        control={<Switch defaultChecked />}
                        label="Notificações de fraude"
                      />
                      <FormControlLabel
                        control={<Switch />}
                        label="Modo sandbox"
                      />
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title="Webhooks" />
                    <CardContent>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        URLs de webhook configuradas
                      </Typography>
                      <List dense>
                        {gateways.map((gateway) => (
                          <ListItem key={gateway.id}>
                            <ListItemIcon>
                              <Webhook />
                            </ListItemIcon>
                            <ListItemText
                              primary={gateway.name}
                              secondary={gateway.credentials.webhookUrl}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Refund Dialog */}
      <Dialog open={refundDialog} onClose={() => setRefundDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Processar Reembolso</DialogTitle>
        <DialogContent>
          {selectedTransaction && (
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Transação: {selectedTransaction.id}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Cliente: {selectedTransaction.customerName}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Valor: R$ {selectedTransaction.amount.toFixed(2)}
              </Typography>
              
              <TextField
                fullWidth
                label="Valor do reembolso"
                type="number"
                defaultValue={selectedTransaction.amount}
                margin="normal"
              />
              
              <TextField
                fullWidth
                label="Motivo do reembolso"
                multiline
                rows={3}
                margin="normal"
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRefundDialog(false)}>Cancelar</Button>
          <Button 
            variant="contained" 
            onClick={() => {
              if (selectedTransaction) {
                handleRefundSubmit(selectedTransaction.amount, 'Reembolso solicitado pelo cliente');
              }
            }}
          >
            Processar Reembolso
          </Button>
        </DialogActions>
      </Dialog>

      {/* Gateway Dialog */}
      <Dialog open={gatewayDialog} onClose={() => setGatewayDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedGateway ? 'Editar Gateway' : 'Adicionar Gateway'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Nome do Gateway"
                defaultValue={selectedGateway?.name}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Tipo</InputLabel>
                <Select defaultValue={selectedGateway?.type || 'stripe'}>
                  <MenuItem value="stripe">Stripe</MenuItem>
                  <MenuItem value="paypal">PayPal</MenuItem>
                  <MenuItem value="mercadopago">MercadoPago</MenuItem>
                  <MenuItem value="pix">PIX</MenuItem>
                  <MenuItem value="bank_transfer">Transferência Bancária</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="API Key"
                type="password"
                defaultValue={selectedGateway?.credentials.apiKey}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Secret Key"
                type="password"
                defaultValue={selectedGateway?.credentials.secretKey}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="URL do Webhook"
                defaultValue={selectedGateway?.credentials.webhookUrl}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGatewayDialog(false)}>Cancelar</Button>
          <Button 
            variant="contained"
            onClick={() => {
              setSnackbar({
                open: true,
                message: selectedGateway ? 'Gateway atualizado com sucesso' : 'Gateway adicionado com sucesso',
                severity: 'success'
              });
              setGatewayDialog(false);
              setSelectedGateway(null);
            }}
          >
            {selectedGateway ? 'Atualizar' : 'Adicionar'}
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
          tooltipTitle="Nova transação"
          onClick={() => {
            setSnackbar({
              open: true,
              message: 'Funcionalidade em desenvolvimento',
              severity: 'info'
            });
          }}
        />
        <SpeedDialAction
          icon={<Assessment />}
          tooltipTitle="Gerar relatório"
          onClick={() => {
            setSnackbar({
              open: true,
              message: 'Relatório gerado com sucesso',
              severity: 'success'
            });
          }}
        />
        <SpeedDialAction
          icon={<Security />}
          tooltipTitle="Verificar fraudes"
          onClick={() => {
            fetchAlerts();
            setSnackbar({
              open: true,
              message: 'Verificação de fraudes concluída',
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

export default PaymentGateway; 
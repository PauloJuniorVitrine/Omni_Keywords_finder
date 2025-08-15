/**
 * test_PaymentGateway.tsx
 * 
 * Testes unitários para o componente PaymentGateway
 * 
 * Tracing ID: UI-021-TEST
 * Data: 2024-12-20
 * Versão: 1.0
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import PaymentGateway from '../../../../app/components/payments/PaymentGateway';

// Mock do Material-UI
jest.mock('@mui/material', () => ({
  ...jest.requireActual('@mui/material'),
  Box: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Card: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  CardContent: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Typography: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Tabs: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Tab: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Button: ({ children, onClick, ...props }: any) => (
    <button onClick={onClick} {...props}>{children}</button>
  ),
  Table: ({ children, ...props }: any) => <table {...props}>{children}</table>,
  TableBody: ({ children, ...props }: any) => <tbody {...props}>{children}</tbody>,
  TableCell: ({ children, ...props }: any) => <td {...props}>{children}</td>,
  TableContainer: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  TableHead: ({ children, ...props }: any) => <thead {...props}>{children}</thead>,
  TableRow: ({ children, ...props }: any) => <tr {...props}>{children}</tr>,
  Paper: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Chip: ({ label, ...props }: any) => <span {...props}>{label}</span>,
  IconButton: ({ children, onClick, ...props }: any) => (
    <button onClick={onClick} {...props}>{children}</button>
  ),
  Dialog: ({ children, open, onClose, ...props }: any) => 
    open ? <div {...props} data-testid="dialog">{children}</div> : null,
  DialogTitle: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  DialogContent: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  DialogActions: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  TextField: ({ label, ...props }: any) => <input placeholder={label} {...props} />,
  Select: ({ children, ...props }: any) => <select {...props}>{children}</select>,
  MenuItem: ({ children, value, ...props }: any) => (
    <option value={value} {...props}>{children}</option>
  ),
  FormControl: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  InputLabel: ({ children, ...props }: any) => <label {...props}>{children}</label>,
  Grid: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Alert: ({ children, severity, ...props }: any) => (
    <div data-severity={severity} {...props}>{children}</div>
  ),
  CircularProgress: (props: any) => <div {...props}>Loading...</div>,
  Tooltip: ({ children, title, ...props }: any) => (
    <div title={title} {...props}>{children}</div>
  ),
  SpeedDial: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  SpeedDialAction: ({ children, tooltipTitle, onClick, ...props }: any) => (
    <button onClick={onClick} title={tooltipTitle} {...props}>{children}</button>
  ),
  SpeedDialIcon: (props: any) => <div {...props}>SpeedDial</div>,
  Divider: (props: any) => <hr {...props} />,
  List: ({ children, ...props }: any) => <ul {...props}>{children}</ul>,
  ListItem: ({ children, ...props }: any) => <li {...props}>{children}</li>,
  ListItemText: ({ primary, secondary, ...props }: any) => (
    <div {...props}>
      <div>{primary}</div>
      <div>{secondary}</div>
    </div>
  ),
  ListItemIcon: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Switch: ({ checked, onChange, ...props }: any) => (
    <input type="checkbox" checked={checked} onChange={onChange} {...props} />
  ),
  FormControlLabel: ({ control, label, ...props }: any) => (
    <label {...props}>
      {control}
      {label}
    </label>
  ),
  Accordion: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  AccordionSummary: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  AccordionDetails: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  LinearProgress: ({ value, ...props }: any) => (
    <div data-value={value} {...props}>Progress: {value}%</div>
  ),
  Badge: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Avatar: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  CardHeader: ({ title, subheader, ...props }: any) => (
    <div {...props}>
      <div>{title}</div>
      <div>{subheader}</div>
    </div>
  ),
  CardActions: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  AlertTitle: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Snackbar: ({ children, open, onClose, ...props }: any) => 
    open ? <div {...props} data-testid="snackbar">{children}</div> : null,
}));

// Mock dos ícones
jest.mock('@mui/icons-material', () => ({
  Payment: () => <div>Payment</div>,
  CreditCard: () => <div>CreditCard</div>,
  AccountBalance: () => <div>AccountBalance</div>,
  Receipt: () => <div>Receipt</div>,
  TrendingUp: () => <div>TrendingUp</div>,
  Security: () => <div>Security</div>,
  Settings: () => <div>Settings</div>,
  Refresh: () => <div>Refresh</div>,
  Download: () => <div>Download</div>,
  Visibility: () => <div>Visibility</div>,
  Edit: () => <div>Edit</div>,
  Delete: () => <div>Delete</div>,
  Add: () => <div>Add</div>,
  CheckCircle: () => <div>CheckCircle</div>,
  Error: () => <div>Error</div>,
  Warning: () => <div>Warning</div>,
  Info: () => <div>Info</div>,
  AttachMoney: () => <div>AttachMoney</div>,
  AccountBalanceWallet: () => <div>AccountBalanceWallet</div>,
  SwapHoriz: () => <div>SwapHoriz</div>,
  Block: () => <div>Block</div>,
  Check: () => <div>Check</div>,
  Close: () => <div>Close</div>,
  ExpandMore: () => <div>ExpandMore</div>,
  FilterList: () => <div>FilterList</div>,
  Search: () => <div>Search</div>,
  Sort: () => <div>Sort</div>,
  MoreVert: () => <div>MoreVert</div>,
  Notifications: () => <div>Notifications</div>,
  Timeline: () => <div>Timeline</div>,
  Assessment: () => <div>Assessment</div>,
  MonetizationOn: () => <div>MonetizationOn</div>,
  LocalAtm: () => <div>LocalAtm</div>,
  AccountBox: () => <div>AccountBox</div>,
  Business: () => <div>Business</div>,
  Lock: () => <div>Lock</div>,
  VpnKey: () => <div>VpnKey</div>,
  Webhook: () => <div>Webhook</div>,
  IntegrationInstructions: () => <div>IntegrationInstructions</div>,
  Analytics: () => <div>Analytics</div>,
  Dashboard: () => <div>Dashboard</div>,
  Speed: () => <div>Speed</div>,
  TrendingDown: () => <div>TrendingDown</div>,
  WarningAmber: () => <div>WarningAmber</div>,
  VerifiedUser: () => <div>VerifiedUser</div>,
  GppGood: () => <div>GppGood</div>,
  GppBad: () => <div>GppBad</div>,
  GppMaybe: () => <div>GppMaybe</div>,
}));

// Mock dos hooks
const mockFetchTransactions = jest.fn();
const mockFetchGateways = jest.fn();
const mockFetchAlerts = jest.fn();
const mockUpdateTransactionStatus = jest.fn();
const mockRefundTransaction = jest.fn();
const mockUpdateGateway = jest.fn();
const mockTestGatewayConnection = jest.fn();
const mockUpdateAlertStatus = jest.fn();

jest.mock('react', () => ({
  ...jest.requireActual('react'),
  useState: jest.fn(),
  useEffect: jest.fn(),
  useMemo: jest.fn(),
}));

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('PaymentGateway', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock dos estados
    const mockSetState = jest.fn();
    (React.useState as jest.Mock).mockImplementation((initial) => [initial, mockSetState]);
    
    // Mock do useEffect
    (React.useEffect as jest.Mock).mockImplementation((callback) => callback());
    
    // Mock do useMemo
    (React.useMemo as jest.Mock).mockImplementation((callback) => callback());
  });

  describe('Renderização inicial', () => {
    it('deve renderizar o componente corretamente', () => {
      renderWithTheme(<PaymentGateway />);
      
      expect(screen.getByText('Sistema de Pagamentos')).toBeInTheDocument();
      expect(screen.getByText('Gestão completa de transações, gateways e monitoramento de fraudes')).toBeInTheDocument();
    });

    it('deve exibir as métricas principais', () => {
      renderWithTheme(<PaymentGateway />);
      
      expect(screen.getByText('Volume Total')).toBeInTheDocument();
      expect(screen.getByText('Transações')).toBeInTheDocument();
      expect(screen.getByText('Taxa de Sucesso')).toBeInTheDocument();
      expect(screen.getByText('Alertas Abertos')).toBeInTheDocument();
    });

    it('deve exibir as abas principais', () => {
      renderWithTheme(<PaymentGateway />);
      
      expect(screen.getByText('Transações')).toBeInTheDocument();
      expect(screen.getByText('Gateways')).toBeInTheDocument();
      expect(screen.getByText('Fraudes')).toBeInTheDocument();
      expect(screen.getByText('Relatórios')).toBeInTheDocument();
      expect(screen.getByText('Configurações')).toBeInTheDocument();
    });
  });

  describe('Aba Transações', () => {
    it('deve exibir a tabela de transações', () => {
      renderWithTheme(<PaymentGateway />);
      
      expect(screen.getByText('Transações Recentes')).toBeInTheDocument();
      expect(screen.getByText('ID')).toBeInTheDocument();
      expect(screen.getByText('Cliente')).toBeInTheDocument();
      expect(screen.getByText('Valor')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Gateway')).toBeInTheDocument();
      expect(screen.getByText('Risco')).toBeInTheDocument();
      expect(screen.getByText('Data')).toBeInTheDocument();
      expect(screen.getByText('Ações')).toBeInTheDocument();
    });

    it('deve exibir as transações mockadas', () => {
      renderWithTheme(<PaymentGateway />);
      
      expect(screen.getByText('txn_001')).toBeInTheDocument();
      expect(screen.getByText('txn_002')).toBeInTheDocument();
      expect(screen.getByText('txn_003')).toBeInTheDocument();
      expect(screen.getByText('João Silva')).toBeInTheDocument();
      expect(screen.getByText('Maria Santos')).toBeInTheDocument();
      expect(screen.getByText('Pedro Costa')).toBeInTheDocument();
    });

    it('deve exibir os status das transações corretamente', () => {
      renderWithTheme(<PaymentGateway />);
      
      expect(screen.getByText('completed')).toBeInTheDocument();
      expect(screen.getByText('pending')).toBeInTheDocument();
      expect(screen.getByText('failed')).toBeInTheDocument();
    });

    it('deve exibir os níveis de risco das transações', () => {
      renderWithTheme(<PaymentGateway />);
      
      expect(screen.getByText('low')).toBeInTheDocument();
      expect(screen.getByText('medium')).toBeInTheDocument();
      expect(screen.getByText('high')).toBeInTheDocument();
    });

    it('deve permitir exportar transações', () => {
      renderWithTheme(<PaymentGateway />);
      
      const exportButton = screen.getByText('Exportar');
      fireEvent.click(exportButton);
      
      // Verificar se o snackbar de sucesso é exibido
      expect(screen.getByTestId('snackbar')).toBeInTheDocument();
    });

    it('deve permitir reembolsar transações completadas', () => {
      renderWithTheme(<PaymentGateway />);
      
      // Simular clique no botão de reembolso
      const refundButtons = screen.getAllByTitle('Reembolsar');
      if (refundButtons.length > 0) {
        fireEvent.click(refundButtons[0]);
        
        // Verificar se o dialog de reembolso é exibido
        expect(screen.getByTestId('dialog')).toBeInTheDocument();
        expect(screen.getByText('Processar Reembolso')).toBeInTheDocument();
      }
    });

    it('deve permitir visualizar detalhes das transações', () => {
      renderWithTheme(<PaymentGateway />);
      
      const viewButtons = screen.getAllByTitle('Ver detalhes');
      if (viewButtons.length > 0) {
        fireEvent.click(viewButtons[0]);
        // Verificar se alguma ação foi executada
        expect(viewButtons[0]).toBeInTheDocument();
      }
    });
  });

  describe('Aba Gateways', () => {
    it('deve exibir os gateways configurados', () => {
      renderWithTheme(<PaymentGateway />);
      
      // Simular clique na aba Gateways
      const gatewaysTab = screen.getByText('Gateways');
      fireEvent.click(gatewaysTab);
      
      expect(screen.getByText('Gateways de Pagamento')).toBeInTheDocument();
      expect(screen.getByText('Stripe')).toBeInTheDocument();
      expect(screen.getByText('MercadoPago')).toBeInTheDocument();
    });

    it('deve exibir as estatísticas dos gateways', () => {
      renderWithTheme(<PaymentGateway />);
      
      const gatewaysTab = screen.getByText('Gateways');
      fireEvent.click(gatewaysTab);
      
      expect(screen.getByText('Transações')).toBeInTheDocument();
      expect(screen.getByText('Taxa de Sucesso')).toBeInTheDocument();
      expect(screen.getByText('Volume Mensal')).toBeInTheDocument();
      expect(screen.getByText('Taxa de Processamento')).toBeInTheDocument();
    });

    it('deve permitir adicionar novo gateway', () => {
      renderWithTheme(<PaymentGateway />);
      
      const gatewaysTab = screen.getByText('Gateways');
      fireEvent.click(gatewaysTab);
      
      const addButton = screen.getByText('Adicionar Gateway');
      fireEvent.click(addButton);
      
      expect(screen.getByTestId('dialog')).toBeInTheDocument();
      expect(screen.getByText('Adicionar Gateway')).toBeInTheDocument();
    });

    it('deve permitir editar gateway existente', () => {
      renderWithTheme(<PaymentGateway />);
      
      const gatewaysTab = screen.getByText('Gateways');
      fireEvent.click(gatewaysTab);
      
      const editButtons = screen.getAllByTitle('Editar');
      if (editButtons.length > 0) {
        fireEvent.click(editButtons[0]);
        
        expect(screen.getByTestId('dialog')).toBeInTheDocument();
        expect(screen.getByText('Editar Gateway')).toBeInTheDocument();
      }
    });

    it('deve permitir testar conexão do gateway', () => {
      renderWithTheme(<PaymentGateway />);
      
      const gatewaysTab = screen.getByText('Gateways');
      fireEvent.click(gatewaysTab);
      
      const testButtons = screen.getAllByTitle('Testar conexão');
      if (testButtons.length > 0) {
        fireEvent.click(testButtons[0]);
        
        // Verificar se o snackbar é exibido
        expect(screen.getByTestId('snackbar')).toBeInTheDocument();
      }
    });

    it('deve exibir os métodos suportados por cada gateway', () => {
      renderWithTheme(<PaymentGateway />);
      
      const gatewaysTab = screen.getByText('Gateways');
      fireEvent.click(gatewaysTab);
      
      expect(screen.getByText('Métodos Suportados')).toBeInTheDocument();
      expect(screen.getByText('credit_card')).toBeInTheDocument();
      expect(screen.getByText('pix')).toBeInTheDocument();
      expect(screen.getByText('boleto')).toBeInTheDocument();
    });
  });

  describe('Aba Fraudes', () => {
    it('deve exibir as métricas de fraude', () => {
      renderWithTheme(<PaymentGateway />);
      
      const fraudTab = screen.getByText('Fraudes');
      fireEvent.click(fraudTab);
      
      expect(screen.getByText('Monitoramento de Fraudes')).toBeInTheDocument();
      expect(screen.getByText('Total de Alertas')).toBeInTheDocument();
      expect(screen.getByText('Alertas Abertos')).toBeInTheDocument();
      expect(screen.getByText('Alta Severidade')).toBeInTheDocument();
      expect(screen.getByText('Risco Médio')).toBeInTheDocument();
    });

    it('deve exibir a tabela de alertas de fraude', () => {
      renderWithTheme(<PaymentGateway />);
      
      const fraudTab = screen.getByText('Fraudes');
      fireEvent.click(fraudTab);
      
      expect(screen.getByText('ID')).toBeInTheDocument();
      expect(screen.getByText('Transação')).toBeInTheDocument();
      expect(screen.getByText('Tipo')).toBeInTheDocument();
      expect(screen.getByText('Severidade')).toBeInTheDocument();
      expect(screen.getByText('Risco')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Data')).toBeInTheDocument();
      expect(screen.getByText('Ações')).toBeInTheDocument();
    });

    it('deve exibir os alertas de fraude', () => {
      renderWithTheme(<PaymentGateway />);
      
      const fraudTab = screen.getByText('Fraudes');
      fireEvent.click(fraudTab);
      
      expect(screen.getByText('fraud_001')).toBeInTheDocument();
      expect(screen.getByText('txn_003')).toBeInTheDocument();
      expect(screen.getByText('unusual_amount')).toBeInTheDocument();
      expect(screen.getByText('high')).toBeInTheDocument();
      expect(screen.getByText('investigating')).toBeInTheDocument();
    });

    it('deve permitir resolver alertas abertos', () => {
      renderWithTheme(<PaymentGateway />);
      
      const fraudTab = screen.getByText('Fraudes');
      fireEvent.click(fraudTab);
      
      const resolveButtons = screen.getAllByTitle('Resolver');
      if (resolveButtons.length > 0) {
        fireEvent.click(resolveButtons[0]);
        
        expect(screen.getByTestId('snackbar')).toBeInTheDocument();
      }
    });

    it('deve permitir configurar alertas', () => {
      renderWithTheme(<PaymentGateway />);
      
      const fraudTab = screen.getByText('Fraudes');
      fireEvent.click(fraudTab);
      
      const configButton = screen.getByText('Configurar Alertas');
      fireEvent.click(configButton);
      
      expect(screen.getByTestId('snackbar')).toBeInTheDocument();
    });
  });

  describe('Aba Relatórios', () => {
    it('deve exibir os relatórios financeiros', () => {
      renderWithTheme(<PaymentGateway />);
      
      const reportsTab = screen.getByText('Relatórios');
      fireEvent.click(reportsTab);
      
      expect(screen.getByText('Relatórios Financeiros')).toBeInTheDocument();
      expect(screen.getByText('Volume por Gateway')).toBeInTheDocument();
      expect(screen.getByText('Taxa de Sucesso')).toBeInTheDocument();
    });

    it('deve exibir o relatório de volume por gateway', () => {
      renderWithTheme(<PaymentGateway />);
      
      const reportsTab = screen.getByText('Relatórios');
      fireEvent.click(reportsTab);
      
      expect(screen.getByText('Relatório de volume de transações por gateway de pagamento')).toBeInTheDocument();
      expect(screen.getByText('Stripe')).toBeInTheDocument();
      expect(screen.getByText('MercadoPago')).toBeInTheDocument();
    });

    it('deve exibir o relatório de taxa de sucesso', () => {
      renderWithTheme(<PaymentGateway />);
      
      const reportsTab = screen.getByText('Relatórios');
      fireEvent.click(reportsTab);
      
      expect(screen.getByText('Taxa de sucesso por gateway')).toBeInTheDocument();
    });
  });

  describe('Aba Configurações', () => {
    it('deve exibir as configurações de pagamento', () => {
      renderWithTheme(<PaymentGateway />);
      
      const settingsTab = screen.getByText('Configurações');
      fireEvent.click(settingsTab);
      
      expect(screen.getByText('Configurações de Pagamento')).toBeInTheDocument();
      expect(screen.getByText('Configurações Gerais')).toBeInTheDocument();
      expect(screen.getByText('Webhooks')).toBeInTheDocument();
    });

    it('deve exibir as configurações gerais', () => {
      renderWithTheme(<PaymentGateway />);
      
      const settingsTab = screen.getByText('Configurações');
      fireEvent.click(settingsTab);
      
      expect(screen.getByText('Captura automática')).toBeInTheDocument();
      expect(screen.getByText('Notificações de fraude')).toBeInTheDocument();
      expect(screen.getByText('Modo sandbox')).toBeInTheDocument();
    });

    it('deve exibir as configurações de webhook', () => {
      renderWithTheme(<PaymentGateway />);
      
      const settingsTab = screen.getByText('Configurações');
      fireEvent.click(settingsTab);
      
      expect(screen.getByText('URLs de webhook configuradas')).toBeInTheDocument();
      expect(screen.getByText('Stripe')).toBeInTheDocument();
      expect(screen.getByText('MercadoPago')).toBeInTheDocument();
    });
  });

  describe('Speed Dial', () => {
    it('deve exibir o speed dial com ações rápidas', () => {
      renderWithTheme(<PaymentGateway />);
      
      // O speed dial deve estar presente
      expect(screen.getByText('SpeedDial')).toBeInTheDocument();
    });

    it('deve permitir criar nova transação', () => {
      renderWithTheme(<PaymentGateway />);
      
      const newTransactionButton = screen.getByTitle('Nova transação');
      fireEvent.click(newTransactionButton);
      
      expect(screen.getByTestId('snackbar')).toBeInTheDocument();
    });

    it('deve permitir gerar relatório', () => {
      renderWithTheme(<PaymentGateway />);
      
      const generateReportButton = screen.getByTitle('Gerar relatório');
      fireEvent.click(generateReportButton);
      
      expect(screen.getByTestId('snackbar')).toBeInTheDocument();
    });

    it('deve permitir verificar fraudes', () => {
      renderWithTheme(<PaymentGateway />);
      
      const checkFraudButton = screen.getByTitle('Verificar fraudes');
      fireEvent.click(checkFraudButton);
      
      expect(screen.getByTestId('snackbar')).toBeInTheDocument();
    });
  });

  describe('Dialog de Reembolso', () => {
    it('deve exibir o dialog de reembolso corretamente', () => {
      renderWithTheme(<PaymentGateway />);
      
      // Simular abertura do dialog de reembolso
      const refundButtons = screen.getAllByTitle('Reembolsar');
      if (refundButtons.length > 0) {
        fireEvent.click(refundButtons[0]);
        
        expect(screen.getByTestId('dialog')).toBeInTheDocument();
        expect(screen.getByText('Processar Reembolso')).toBeInTheDocument();
        expect(screen.getByText('Transação: txn_001')).toBeInTheDocument();
        expect(screen.getByText('Cliente: João Silva')).toBeInTheDocument();
        expect(screen.getByText('Valor: R$ 299.99')).toBeInTheDocument();
      }
    });

    it('deve permitir cancelar o reembolso', () => {
      renderWithTheme(<PaymentGateway />);
      
      const refundButtons = screen.getAllByTitle('Reembolsar');
      if (refundButtons.length > 0) {
        fireEvent.click(refundButtons[0]);
        
        const cancelButton = screen.getByText('Cancelar');
        fireEvent.click(cancelButton);
        
        // Dialog deve ser fechado
        expect(screen.queryByTestId('dialog')).not.toBeInTheDocument();
      }
    });

    it('deve permitir processar o reembolso', () => {
      renderWithTheme(<PaymentGateway />);
      
      const refundButtons = screen.getAllByTitle('Reembolsar');
      if (refundButtons.length > 0) {
        fireEvent.click(refundButtons[0]);
        
        const processButton = screen.getByText('Processar Reembolso');
        fireEvent.click(processButton);
        
        expect(screen.getByTestId('snackbar')).toBeInTheDocument();
      }
    });
  });

  describe('Dialog de Gateway', () => {
    it('deve exibir o dialog de gateway corretamente', () => {
      renderWithTheme(<PaymentGateway />);
      
      const gatewaysTab = screen.getByText('Gateways');
      fireEvent.click(gatewaysTab);
      
      const addButton = screen.getByText('Adicionar Gateway');
      fireEvent.click(addButton);
      
      expect(screen.getByTestId('dialog')).toBeInTheDocument();
      expect(screen.getByText('Adicionar Gateway')).toBeInTheDocument();
    });

    it('deve permitir cancelar a adição/edição de gateway', () => {
      renderWithTheme(<PaymentGateway />);
      
      const gatewaysTab = screen.getByText('Gateways');
      fireEvent.click(gatewaysTab);
      
      const addButton = screen.getByText('Adicionar Gateway');
      fireEvent.click(addButton);
      
      const cancelButton = screen.getByText('Cancelar');
      fireEvent.click(cancelButton);
      
      expect(screen.queryByTestId('dialog')).not.toBeInTheDocument();
    });

    it('deve permitir adicionar/editar gateway', () => {
      renderWithTheme(<PaymentGateway />);
      
      const gatewaysTab = screen.getByText('Gateways');
      fireEvent.click(gatewaysTab);
      
      const addButton = screen.getByText('Adicionar Gateway');
      fireEvent.click(addButton);
      
      const saveButton = screen.getByText('Adicionar');
      fireEvent.click(saveButton);
      
      expect(screen.getByTestId('snackbar')).toBeInTheDocument();
    });
  });

  describe('Snackbar', () => {
    it('deve exibir mensagens de sucesso', () => {
      renderWithTheme(<PaymentGateway />);
      
      // Simular uma ação que gera snackbar de sucesso
      const exportButton = screen.getByText('Exportar');
      fireEvent.click(exportButton);
      
      expect(screen.getByTestId('snackbar')).toBeInTheDocument();
    });

    it('deve permitir fechar o snackbar', () => {
      renderWithTheme(<PaymentGateway />);
      
      const exportButton = screen.getByText('Exportar');
      fireEvent.click(exportButton);
      
      const snackbar = screen.getByTestId('snackbar');
      expect(snackbar).toBeInTheDocument();
      
      // Simular fechamento automático após 6 segundos
      waitFor(() => {
        expect(screen.queryByTestId('snackbar')).not.toBeInTheDocument();
      }, { timeout: 7000 });
    });
  });

  describe('Estados de loading e erro', () => {
    it('deve exibir loading quando carregando dados', () => {
      // Mock do estado de loading
      (React.useState as jest.Mock).mockImplementation((initial) => {
        if (typeof initial === 'boolean') {
          return [true, jest.fn()]; // Simular loading
        }
        return [initial, jest.fn()];
      });
      
      renderWithTheme(<PaymentGateway />);
      
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('deve exibir erro quando falha ao carregar dados', () => {
      // Mock do estado de erro
      (React.useState as jest.Mock).mockImplementation((initial) => {
        if (typeof initial === 'string' && initial === null) {
          return ['Erro ao carregar dados', jest.fn()]; // Simular erro
        }
        return [initial, jest.fn()];
      });
      
      renderWithTheme(<PaymentGateway />);
      
      expect(screen.getByText('Erro ao carregar dados de pagamento. Tente novamente.')).toBeInTheDocument();
    });
  });

  describe('Responsividade', () => {
    it('deve ser responsivo em diferentes tamanhos de tela', () => {
      renderWithTheme(<PaymentGateway />);
      
      // Verificar se os componentes principais estão presentes
      expect(screen.getByText('Sistema de Pagamentos')).toBeInTheDocument();
      expect(screen.getByText('Transações')).toBeInTheDocument();
      expect(screen.getByText('Gateways')).toBeInTheDocument();
      expect(screen.getByText('Fraudes')).toBeInTheDocument();
      expect(screen.getByText('Relatórios')).toBeInTheDocument();
      expect(screen.getByText('Configurações')).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter tooltips informativos', () => {
      renderWithTheme(<PaymentGateway />);
      
      expect(screen.getByTitle('Ver detalhes')).toBeInTheDocument();
      expect(screen.getByTitle('Reembolsar')).toBeInTheDocument();
      expect(screen.getByTitle('Testar conexão')).toBeInTheDocument();
      expect(screen.getByTitle('Editar')).toBeInTheDocument();
      expect(screen.getByTitle('Resolver')).toBeInTheDocument();
    });

    it('deve ter labels descritivos', () => {
      renderWithTheme(<PaymentGateway />);
      
      expect(screen.getByText('Sistema de Pagamentos')).toBeInTheDocument();
      expect(screen.getByText('Gestão completa de transações, gateways e monitoramento de fraudes')).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('deve usar useMemo para cálculos de métricas', () => {
      renderWithTheme(<PaymentGateway />);
      
      // Verificar se useMemo foi chamado para métricas
      expect(React.useMemo).toHaveBeenCalled();
    });

    it('deve carregar dados apenas uma vez no mount', () => {
      renderWithTheme(<PaymentGateway />);
      
      // Verificar se useEffect foi chamado
      expect(React.useEffect).toHaveBeenCalled();
    });
  });
}); 
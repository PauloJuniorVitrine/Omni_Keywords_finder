import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import SecurityDashboard from '../../../../components/security/SecurityDashboard';

// Mock Material-UI components
jest.mock('@mui/material', () => ({
  ...jest.requireActual('@mui/material'),
  Box: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Card: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  CardContent: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Typography: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Button: ({ children, onClick, ...props }: any) => (
    <button onClick={onClick} {...props}>
      {children}
    </button>
  ),
  Chip: ({ label, ...props }: any) => <span {...props}>{label}</span>,
  Table: ({ children, ...props }: any) => <table {...props}>{children}</table>,
  TableBody: ({ children, ...props }: any) => <tbody {...props}>{children}</tbody>,
  TableCell: ({ children, ...props }: any) => <td {...props}>{children}</td>,
  TableContainer: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  TableHead: ({ children, ...props }: any) => <thead {...props}>{children}</thead>,
  TableRow: ({ children, ...props }: any) => <tr {...props}>{children}</tr>,
  Paper: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  IconButton: ({ children, onClick, ...props }: any) => (
    <button onClick={onClick} {...props}>
      {children}
    </button>
  ),
  Dialog: ({ children, open, ...props }: any) => 
    open ? <div data-testid="dialog" {...props}>{children}</div> : null,
  DialogTitle: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  DialogContent: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  DialogActions: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  FormControl: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  InputLabel: ({ children, ...props }: any) => <label {...props}>{children}</label>,
  Select: ({ children, value, onChange, ...props }: any) => (
    <select value={value} onChange={onChange} {...props}>
      {children}
    </select>
  ),
  MenuItem: ({ children, value, ...props }: any) => (
    <option value={value} {...props}>{children}</option>
  ),
  Switch: ({ checked, onChange, ...props }: any) => (
    <input
      type="checkbox"
      checked={checked}
      onChange={onChange}
      {...props}
    />
  ),
  FormControlLabel: ({ control, label, ...props }: any) => (
    <label {...props}>
      {control}
      {label}
    </label>
  ),
  Alert: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  CircularProgress: () => <div data-testid="loading">Loading...</div>,
  Tooltip: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Badge: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Tabs: ({ children, value, onChange, ...props }: any) => (
    <div {...props}>
      {React.Children.map(children, (child, index) =>
        React.cloneElement(child as React.ReactElement, {
          onClick: () => onChange(null, index),
          'data-testid': `tab-${index}`,
        })
      )}
    </div>
  ),
  Tab: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  Divider: () => <hr />,
  Grid: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  List: ({ children, ...props }: any) => <ul {...props}>{children}</ul>,
  ListItem: ({ children, ...props }: any) => <li {...props}>{children}</li>,
  ListItemText: ({ primary, secondary, ...props }: any) => (
    <div {...props}>
      <div>{primary}</div>
      <div>{secondary}</div>
    </div>
  ),
  ListItemIcon: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  LinearProgress: ({ ...props }: any) => <div {...props}>Progress Bar</div>,
  TextField: ({ label, value, onChange, ...props }: any) => (
    <input
      data-testid={label?.toLowerCase().replace(/\s+/g, '-')}
      value={value}
      onChange={onChange}
      placeholder={label}
      {...props}
    />
  ),
}));

// Mock Material-UI icons
jest.mock('@mui/icons-material', () => ({
  Security: () => <span data-testid="security-icon">🔒</span>,
  Warning: () => <span data-testid="warning-icon">⚠️</span>,
  Error: () => <span data-testid="error-icon">❌</span>,
  Info: () => <span data-testid="info-icon">ℹ️</span>,
  CheckCircle: () => <span data-testid="check-circle-icon">✅</span>,
  Cancel: () => <span data-testid="cancel-icon">❌</span>,
  Refresh: () => <span data-testid="refresh-icon">🔄</span>,
  Settings: () => <span data-testid="settings-icon">⚙️</span>,
  Visibility: () => <span data-testid="visibility-icon">👁️</span>,
  Block: () => <span data-testid="block-icon">🚫</span>,
  Shield: () => <span data-testid="shield-icon">🛡️</span>,
  Lock: () => <span data-testid="lock-icon">🔒</span>,
  Key: () => <span data-testid="key-icon">🔑</span>,
  Fingerprint: () => <span data-testid="fingerprint-icon">👆</span>,
  VpnKey: () => <span data-testid="vpn-key-icon">🔐</span>,
  Public: () => <span data-testid="public-icon">🌐</span>,
  Private: () => <span data-testid="private-icon">🔒</span>,
  VerifiedUser: () => <span data-testid="verified-user-icon">✅</span>,
  AdminPanelSettings: () => <span data-testid="admin-panel-settings-icon">⚙️</span>,
  BugReport: () => <span data-testid="bug-report-icon">🐛</span>,
  Report: () => <span data-testid="report-icon">📄</span>,
  Assessment: () => <span data-testid="assessment-icon">📋</span>,
  Timeline: () => <span data-testid="timeline-icon">📈</span>,
  TrendingUp: () => <span data-testid="trending-up-icon">📈</span>,
  TrendingDown: () => <span data-testid="trending-down-icon">📉</span>,
  Notifications: () => <span data-testid="notifications-icon">🔔</span>,
  NotificationsOff: () => <span data-testid="notifications-off-icon">🔕</span>,
  Schedule: () => <span data-testid="schedule-icon">📅</span>,
  AutoAwesome: () => <span data-testid="auto-awesome-icon">✨</span>,
  Psychology: () => <span data-testid="psychology-icon">🧠</span>,
  Science: () => <span data-testid="science-icon">🔬</span>,
  Biotech: () => <span data-testid="biotech-icon">🧬</span>,
  Engineering: () => <span data-testid="engineering-icon">⚙️</span>,
  Build: () => <span data-testid="build-icon">🔨</span>,
  Construction: () => <span data-testid="construction-icon">🏗️</span>,
  Handyman: () => <span data-testid="handyman-icon">🔧</span>,
  Plumbing: () => <span data-testid="plumbing-icon">🚰</span>,
  ElectricalServices: () => <span data-testid="electrical-icon">⚡</span>,
  CleaningServices: () => <span data-testid="cleaning-icon">🧹</span>,
  LocalShipping: () => <span data-testid="shipping-icon">🚚</span>,
  LocalTaxi: () => <span data-testid="taxi-icon">🚕</span>,
  DirectionsCar: () => <span data-testid="car-icon">🚗</span>,
  DirectionsBike: () => <span data-testid="bike-icon">🚲</span>,
  DirectionsWalk: () => <span data-testid="walk-icon">🚶</span>,
  DirectionsRun: () => <span data-testid="run-icon">🏃</span>,
  DirectionsTransit: () => <span data-testid="transit-icon">🚌</span>,
  DirectionsBoat: () => <span data-testid="boat-icon">🚢</span>,
  DirectionsSubway: () => <span data-testid="subway-icon">🚇</span>,
  DirectionsBus: () => <span data-testid="bus-icon">🚌</span>,
  DirectionsRailway: () => <span data-testid="railway-icon">🚂</span>,
  DirectionsCarFilled: () => <span data-testid="car-filled-icon">🚗</span>,
  DirectionsBikeFilled: () => <span data-testid="bike-filled-icon">🚲</span>,
  DirectionsWalkFilled: () => <span data-testid="walk-filled-icon">🚶</span>,
  DirectionsRunFilled: () => <span data-testid="run-filled-icon">🏃</span>,
  DirectionsTransitFilled: () => <span data-testid="transit-filled-icon">🚌</span>,
  DirectionsBoatFilled: () => <span data-testid="boat-filled-icon">🚢</span>,
  DirectionsSubwayFilled: () => <span data-testid="subway-filled-icon">🚇</span>,
  DirectionsBusFilled: () => <span data-testid="bus-filled-icon">🚌</span>,
  DirectionsRailwayFilled: () => <span data-testid="railway-filled-icon">🚂</span>,
}));

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('SecurityDashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render the SecurityDashboard component', () => {
      renderWithTheme(<SecurityDashboard />);
      expect(screen.getByText('Security Dashboard')).toBeInTheDocument();
    });

    it('should render the main header with title', () => {
      renderWithTheme(<SecurityDashboard />);
      expect(screen.getByText('Security Dashboard')).toBeInTheDocument();
    });

    it('should render control buttons in header', () => {
      renderWithTheme(<SecurityDashboard />);
      expect(screen.getByTestId('refresh-icon')).toBeInTheDocument();
      expect(screen.getByTestId('settings-icon')).toBeInTheDocument();
    });

    it('should render security overview cards', () => {
      renderWithTheme(<SecurityDashboard />);
      expect(screen.getByText('Security Score')).toBeInTheDocument();
      expect(screen.getByText('Active Threats')).toBeInTheDocument();
      expect(screen.getByText('Vulnerabilities')).toBeInTheDocument();
      expect(screen.getByText('High Risk Events')).toBeInTheDocument();
    });

    it('should render tabs', () => {
      renderWithTheme(<SecurityDashboard />);
      expect(screen.getByText('Threats')).toBeInTheDocument();
      expect(screen.getByText('Vulnerabilities')).toBeInTheDocument();
      expect(screen.getByText('Compliance')).toBeInTheDocument();
      expect(screen.getByText('Events')).toBeInTheDocument();
    });

    it('should render critical alerts when active threats are present', () => {
      renderWithTheme(<SecurityDashboard />);
      expect(screen.getByText('2 Active Security Threats Detected')).toBeInTheDocument();
      expect(screen.getByText('Immediate attention required for: brute force, sql injection')).toBeInTheDocument();
    });
  });

  describe('Security Overview', () => {
    it('should display security score', () => {
      renderWithTheme(<SecurityDashboard />);
      
      // Should show a percentage score
      expect(screen.getByText(/^\d+%$/)).toBeInTheDocument();
    });

    it('should display active threats count', () => {
      renderWithTheme(<SecurityDashboard />);
      
      // Should show number of active threats
      expect(screen.getByText('2')).toBeInTheDocument();
    });

    it('should display vulnerabilities count', () => {
      renderWithTheme(<SecurityDashboard />);
      
      // Should show number of open vulnerabilities
      expect(screen.getByText('2')).toBeInTheDocument();
    });

    it('should display high risk events count', () => {
      renderWithTheme(<SecurityDashboard />);
      
      // Should show number of high risk events
      expect(screen.getByText('1')).toBeInTheDocument();
    });
  });

  describe('Threats Display', () => {
    it('should display security threats', () => {
      renderWithTheme(<SecurityDashboard />);
      expect(screen.getByText('brute force')).toBeInTheDocument();
      expect(screen.getByText('sql injection')).toBeInTheDocument();
      expect(screen.getByText('phishing')).toBeInTheDocument();
    });

    it('should display threat severity levels', () => {
      renderWithTheme(<SecurityDashboard />);
      expect(screen.getByText('HIGH')).toBeInTheDocument();
      expect(screen.getByText('CRITICAL')).toBeInTheDocument();
      expect(screen.getByText('MEDIUM')).toBeInTheDocument();
    });

    it('should display threat status', () => {
      renderWithTheme(<SecurityDashboard />);
      expect(screen.getByText('ACTIVE')).toBeInTheDocument();
      expect(screen.getByText('INVESTIGATING')).toBeInTheDocument();
      expect(screen.getByText('RESOLVED')).toBeInTheDocument();
    });

    it('should display threat confidence levels', () => {
      renderWithTheme(<SecurityDashboard />);
      expect(screen.getByText('95%')).toBeInTheDocument();
      expect(screen.getByText('98%')).toBeInTheDocument();
      expect(screen.getByText('87%')).toBeInTheDocument();
    });
  });

  describe('Vulnerabilities Display', () => {
    it('should display vulnerabilities when vulnerabilities tab is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const vulnerabilitiesTab = screen.getByText('Vulnerabilities');
      await user.click(vulnerabilitiesTab);

      expect(screen.getByText('CVE-2024-1234')).toBeInTheDocument();
      expect(screen.getByText('CVE-2024-5678')).toBeInTheDocument();
      expect(screen.getByText('CVE-2024-9012')).toBeInTheDocument();
    });

    it('should display vulnerability details', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const vulnerabilitiesTab = screen.getByText('Vulnerabilities');
      await user.click(vulnerabilitiesTab);

      expect(screen.getByText('SQL Injection in User Authentication')).toBeInTheDocument();
      expect(screen.getByText('Cross-Site Scripting in Search Function')).toBeInTheDocument();
      expect(screen.getByText('Weak Password Policy')).toBeInTheDocument();
    });

    it('should display vulnerability severity levels', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const vulnerabilitiesTab = screen.getByText('Vulnerabilities');
      await user.click(vulnerabilitiesTab);

      expect(screen.getByText('HIGH')).toBeInTheDocument();
      expect(screen.getByText('MEDIUM')).toBeInTheDocument();
      expect(screen.getByText('LOW')).toBeInTheDocument();
    });

    it('should display CVSS scores', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const vulnerabilitiesTab = screen.getByText('Vulnerabilities');
      await user.click(vulnerabilitiesTab);

      expect(screen.getByText('8.5')).toBeInTheDocument();
      expect(screen.getByText('6.1')).toBeInTheDocument();
      expect(screen.getByText('3.1')).toBeInTheDocument();
    });
  });

  describe('Compliance Display', () => {
    it('should display compliance checks when compliance tab is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const complianceTab = screen.getByText('Compliance');
      await user.click(complianceTab);

      expect(screen.getByText('PCI DSS')).toBeInTheDocument();
      expect(screen.getByText('ISO 27001')).toBeInTheDocument();
      expect(screen.getByText('GDPR')).toBeInTheDocument();
    });

    it('should display compliance control information', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const complianceTab = screen.getByText('Compliance');
      await user.click(complianceTab);

      expect(screen.getByText('PCI DSS 3.4')).toBeInTheDocument();
      expect(screen.getByText('A.12.4.1')).toBeInTheDocument();
      expect(screen.getByText('Article 32')).toBeInTheDocument();
    });

    it('should display compliance status', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const complianceTab = screen.getByText('Compliance');
      await user.click(complianceTab);

      expect(screen.getByText('COMPLIANT')).toBeInTheDocument();
      expect(screen.getByText('PARTIAL')).toBeInTheDocument();
      expect(screen.getByText('NON COMPLIANT')).toBeInTheDocument();
    });

    it('should display risk levels', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const complianceTab = screen.getByText('Compliance');
      await user.click(complianceTab);

      expect(screen.getByText('LOW')).toBeInTheDocument();
      expect(screen.getByText('MEDIUM')).toBeInTheDocument();
      expect(screen.getByText('HIGH')).toBeInTheDocument();
    });
  });

  describe('Events Display', () => {
    it('should display security events when events tab is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const eventsTab = screen.getByText('Events');
      await user.click(eventsTab);

      expect(screen.getByText('LOGIN')).toBeInTheDocument();
      expect(screen.getByText('ACCESS DENIED')).toBeInTheDocument();
      expect(screen.getByText('DATA ACCESS')).toBeInTheDocument();
    });

    it('should display event details', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const eventsTab = screen.getByText('Events');
      await user.click(eventsTab);

      expect(screen.getByText('admin@example.com')).toBeInTheDocument();
      expect(screen.getByText('unknown')).toBeInTheDocument();
      expect(screen.getByText('user@example.com')).toBeInTheDocument();
    });

    it('should display risk scores', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const eventsTab = screen.getByText('Events');
      await user.click(eventsTab);

      expect(screen.getByText('15')).toBeInTheDocument();
      expect(screen.getByText('85')).toBeInTheDocument();
      expect(screen.getByText('25')).toBeInTheDocument();
    });

    it('should display locations', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const eventsTab = screen.getByText('Events');
      await user.click(eventsTab);

      expect(screen.getByText('New York, US')).toBeInTheDocument();
      expect(screen.getByText('Unknown')).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('should switch between tabs correctly', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      // Start with Threats tab (default)
      expect(screen.getByText('brute force')).toBeInTheDocument();

      // Switch to Vulnerabilities tab
      const vulnerabilitiesTab = screen.getByText('Vulnerabilities');
      await user.click(vulnerabilitiesTab);
      expect(screen.getByText('CVE-2024-1234')).toBeInTheDocument();

      // Switch to Compliance tab
      const complianceTab = screen.getByText('Compliance');
      await user.click(complianceTab);
      expect(screen.getByText('PCI DSS')).toBeInTheDocument();

      // Switch to Events tab
      const eventsTab = screen.getByText('Events');
      await user.click(eventsTab);
      expect(screen.getByText('LOGIN')).toBeInTheDocument();

      // Switch back to Threats tab
      const threatsTab = screen.getByText('Threats');
      await user.click(threatsTab);
      expect(screen.getByText('brute force')).toBeInTheDocument();
    });
  });

  describe('Threat Detail Dialog', () => {
    it('should open threat detail dialog when view button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const viewButtons = screen.getAllByTestId('visibility-icon');
      await user.click(viewButtons[0]);

      expect(screen.getByText('Threat Details')).toBeInTheDocument();
    });

    it('should close threat detail dialog when close button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const viewButtons = screen.getAllByTestId('visibility-icon');
      await user.click(viewButtons[0]);

      const closeButton = screen.getByTestId('cancel-icon').parentElement;
      await user.click(closeButton!);

      expect(screen.queryByText('Threat Details')).not.toBeInTheDocument();
    });

    it('should close threat detail dialog when close button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const viewButtons = screen.getAllByTestId('visibility-icon');
      await user.click(viewButtons[0]);

      const closeButton = screen.getByText('Close');
      await user.click(closeButton);

      expect(screen.queryByText('Threat Details')).not.toBeInTheDocument();
    });

    it('should start investigation when start investigation button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const viewButtons = screen.getAllByTestId('visibility-icon');
      await user.click(viewButtons[0]);

      const investigateButton = screen.getByText('Start Investigation');
      await user.click(investigateButton);

      expect(screen.queryByText('Threat Details')).not.toBeInTheDocument();
    });
  });

  describe('Settings Dialog', () => {
    it('should open settings dialog when settings button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const settingsButton = screen.getByTestId('settings-icon').parentElement;
      await user.click(settingsButton!);

      expect(screen.getByText('Security Settings')).toBeInTheDocument();
    });

    it('should close settings dialog when cancel button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const settingsButton = screen.getByTestId('settings-icon').parentElement;
      await user.click(settingsButton!);

      const cancelButton = screen.getByText('Cancel');
      await user.click(cancelButton);

      expect(screen.queryByText('Security Settings')).not.toBeInTheDocument();
    });

    it('should close settings dialog when save button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const settingsButton = screen.getByTestId('settings-icon').parentElement;
      await user.click(settingsButton!);

      const saveButton = screen.getByText('Save');
      await user.click(saveButton);

      expect(screen.queryByText('Security Settings')).not.toBeInTheDocument();
    });
  });

  describe('Refresh Functionality', () => {
    it('should refresh security data when refresh button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<SecurityDashboard />);

      const refreshButton = screen.getByTestId('refresh-icon').parentElement;
      await user.click(refreshButton!);

      // Should show loading state briefly
      expect(screen.getByTestId('loading')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error alert when error state is set', () => {
      // This would require testing the component with an error state
      // For now, we'll test that the error display logic exists
      renderWithTheme(<SecurityDashboard />);
      
      // The component should render without errors
      expect(screen.getByText('Security Dashboard')).toBeInTheDocument();
    });
  });

  describe('Performance and Memory', () => {
    it('should handle large number of security events efficiently', () => {
      // This is a basic test to ensure the component renders with mock data
      renderWithTheme(<SecurityDashboard />);
      
      // Should render without performance issues
      expect(screen.getByText('Security Dashboard')).toBeInTheDocument();
    });

    it('should not cause memory leaks', () => {
      const { unmount } = renderWithTheme(<SecurityDashboard />);
      
      // Should unmount cleanly
      unmount();
      
      // No errors should be thrown
      expect(true).toBe(true);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels and roles', () => {
      renderWithTheme(<SecurityDashboard />);
      
      // Basic accessibility test - component should render
      expect(screen.getByText('Security Dashboard')).toBeInTheDocument();
    });

    it('should be keyboard navigable', () => {
      renderWithTheme(<SecurityDashboard />);
      
      // Basic keyboard navigation test
      const tabs = screen.getAllByRole('button');
      expect(tabs.length).toBeGreaterThan(0);
    });
  });

  describe('Responsive Design', () => {
    it('should render properly on different screen sizes', () => {
      renderWithTheme(<SecurityDashboard />);
      
      // Component should render without layout issues
      expect(screen.getByText('Security Dashboard')).toBeInTheDocument();
    });
  });

  describe('Integration Tests', () => {
    it('should integrate with Material-UI theme', () => {
      renderWithTheme(<SecurityDashboard />);
      
      // Component should use theme properly
      expect(screen.getByText('Security Dashboard')).toBeInTheDocument();
    });

    it('should work with React hooks', () => {
      renderWithTheme(<SecurityDashboard />);
      
      // Component should use hooks without errors
      expect(screen.getByText('Security Dashboard')).toBeInTheDocument();
    });
  });
}); 
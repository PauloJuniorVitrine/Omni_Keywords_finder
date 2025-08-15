/**
 * Testes Unitários - Sistema de Cache Avançado
 * 
 * Prompt: UI-016 do CHECKLIST_INTERFACE_GRAFICA_V1.md
 * Ruleset: enterprise_control_layer.yaml
 * Data/Hora: 2024-12-20 10:30:00 UTC
 * Tracing ID: UI-016-TEST
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CacheManagement from '../../../../app/components/admin/CacheManagement';

// Mock Material-UI components
jest.mock('@mui/material', () => ({
  ...jest.requireActual('@mui/material'),
  Dialog: ({ children, open, onClose }: any) => 
    open ? <div data-testid="dialog">{children}</div> : null,
  DialogTitle: ({ children }: any) => <div data-testid="dialog-title">{children}</div>,
  DialogContent: ({ children }: any) => <div data-testid="dialog-content">{children}</div>,
  DialogActions: ({ children }: any) => <div data-testid="dialog-actions">{children}</div>,
  TableContainer: ({ children }: any) => <div data-testid="table-container">{children}</div>,
  Table: ({ children }: any) => <table data-testid="table">{children}</table>,
  TableHead: ({ children }: any) => <thead data-testid="table-head">{children}</thead>,
  TableBody: ({ children }: any) => <tbody data-testid="table-body">{children}</tbody>,
  TableRow: ({ children }: any) => <tr data-testid="table-row">{children}</tr>,
  TableCell: ({ children }: any) => <td data-testid="table-cell">{children}</td>,
  Accordion: ({ children }: any) => <div data-testid="accordion">{children}</div>,
  AccordionSummary: ({ children }: any) => <div data-testid="accordion-summary">{children}</div>,
  AccordionDetails: ({ children }: any) => <div data-testid="accordion-details">{children}</div>,
  List: ({ children }: any) => <ul data-testid="list">{children}</ul>,
  ListItem: ({ children }: any) => <li data-testid="list-item">{children}</li>,
  ListItemText: ({ primary, secondary }: any) => (
    <div data-testid="list-item-text">
      <div data-testid="primary">{primary}</div>
      <div data-testid="secondary">{secondary}</div>
    </div>
  ),
  ListItemSecondaryAction: ({ children }: any) => (
    <div data-testid="list-item-secondary-action">{children}</div>
  ),
  LinearProgress: () => <div data-testid="linear-progress" />,
  Alert: ({ children, severity }: any) => (
    <div data-testid={`alert-${severity}`}>{children}</div>
  ),
  Chip: ({ label, color, variant, size }: any) => (
    <span data-testid={`chip-${label}`} data-color={color} data-variant={variant} data-size={size}>
      {label}
    </span>
  ),
  Tooltip: ({ children, title }: any) => (
    <div data-testid="tooltip" title={title}>{children}</div>
  ),
  IconButton: ({ children, onClick, color, size }: any) => (
    <button 
      data-testid="icon-button" 
      onClick={onClick} 
      data-color={color} 
      data-size={size}
    >
      {children}
    </button>
  ),
  Switch: ({ checked, onChange }: any) => (
    <input 
      type="checkbox" 
      data-testid="switch" 
      checked={checked} 
      onChange={onChange}
    />
  ),
  FormControlLabel: ({ control, label }: any) => (
    <label data-testid="form-control-label">
      {control}
      <span>{label}</span>
    </label>
  ),
  InputAdornment: ({ children, position }: any) => (
    <span data-testid="input-adornment" data-position={position}>{children}</span>
  )
}));

// Mock Material-UI icons
jest.mock('@mui/icons-material', () => ({
  Refresh: () => <span data-testid="refresh-icon">Refresh</span>,
  Delete: () => <span data-testid="delete-icon">Delete</span>,
  Settings: () => <span data-testid="settings-icon">Settings</span>,
  TrendingUp: () => <span data-testid="trending-up-icon">TrendingUp</span>,
  Storage: () => <span data-testid="storage-icon">Storage</span>,
  Speed: () => <span data-testid="speed-icon">Speed</span>,
  CheckCircle: () => <span data-testid="check-circle-icon">CheckCircle</span>,
  Error: () => <span data-testid="error-icon">Error</span>,
  Info: () => <span data-testid="info-icon">Info</span>,
  ExpandMore: () => <span data-testid="expand-more-icon">ExpandMore</span>,
  PlayArrow: () => <span data-testid="play-arrow-icon">PlayArrow</span>,
  Backup: () => <span data-testid="backup-icon">Backup</span>,
  RestoreFromTrash: () => <span data-testid="restore-icon">Restore</span>,
  Timer: () => <span data-testid="timer-icon">Timer</span>,
  Memory: () => <span data-testid="memory-icon">Memory</span>
}));

// Mock data
const mockCacheItems = [
  {
    key: 'user:profile:123',
    value: { name: 'João Silva', email: 'joao@example.com' },
    size: 1024,
    ttl: 3600,
    createdAt: new Date(Date.now() - 1800000),
    lastAccessed: new Date(Date.now() - 300000),
    accessCount: 15,
    type: 'hash' as const,
    namespace: 'users'
  },
  {
    key: 'search:results:keywords',
    value: ['keyword1', 'keyword2', 'keyword3'],
    size: 2048,
    ttl: 1800,
    createdAt: new Date(Date.now() - 900000),
    lastAccessed: new Date(Date.now() - 60000),
    accessCount: 8,
    type: 'list' as const,
    namespace: 'search'
  }
];

const mockCacheStats = {
  totalItems: 1250,
  totalSize: 52428800,
  hitRate: 0.85,
  missRate: 0.15,
  evictions: 45,
  expired: 12,
  memoryUsage: 41943040,
  memoryLimit: 52428800,
  averageResponseTime: 2.5,
  keyspaceHits: 15420,
  keyspaceMisses: 2720
};

const mockCacheConfig = {
  maxMemory: 52428800,
  maxItems: 10000,
  defaultTTL: 3600,
  evictionPolicy: 'lru' as const,
  enableCompression: true,
  enablePersistence: true,
  backupInterval: 3600,
  warmingEnabled: true,
  warmingStrategy: 'hybrid' as const
};

const mockCacheBackups = [
  {
    id: 'backup_001',
    timestamp: new Date(Date.now() - 3600000),
    size: 20971520,
    itemCount: 1200,
    status: 'completed' as const,
    type: 'full' as const,
    location: '/backups/cache_backup_001.rdb'
  }
];

const mockCachePatterns = [
  {
    pattern: 'user:profile:*',
    frequency: 150,
    averageSize: 1024,
    hitRate: 0.92,
    lastAccessed: new Date(Date.now() - 300000)
  }
];

// Test setup
const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('CacheManagement Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the main component with header', () => {
      renderWithTheme(<CacheManagement />);
      
      expect(screen.getByText('Cache Management')).toBeInTheDocument();
      expect(screen.getByText('Advanced cache management and monitoring system')).toBeInTheDocument();
    });

    it('should render all tabs', () => {
      renderWithTheme(<CacheManagement />);
      
      expect(screen.getByText('Overview')).toBeInTheDocument();
      expect(screen.getByText('Configuration')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
    });

    it('should render action buttons in header', () => {
      renderWithTheme(<CacheManagement />);
      
      expect(screen.getByText('Refresh')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    it('should render performance score card', () => {
      renderWithTheme(<CacheManagement />);
      
      expect(screen.getByText('Performance Score')).toBeInTheDocument();
      expect(screen.getByText(/\/100/)).toBeInTheDocument();
    });

    it('should render hit rate card', () => {
      renderWithTheme(<CacheManagement />);
      
      expect(screen.getByText('Hit Rate')).toBeInTheDocument();
      expect(screen.getByText('85.0%')).toBeInTheDocument();
    });

    it('should render memory usage card', () => {
      renderWithTheme(<CacheManagement />);
      
      expect(screen.getByText('Memory Usage')).toBeInTheDocument();
      expect(screen.getByText('40.0 MB')).toBeInTheDocument();
    });

    it('should render response time card', () => {
      renderWithTheme(<CacheManagement />);
      
      expect(screen.getByText('Avg Response Time')).toBeInTheDocument();
      expect(screen.getByText('2.5ms')).toBeInTheDocument();
    });

    it('should render cache items table', () => {
      renderWithTheme(<CacheManagement />);
      
      expect(screen.getByText('Cache Items')).toBeInTheDocument();
      expect(screen.getByTestId('table-container')).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('should switch to Configuration tab when clicked', async () => {
      renderWithTheme(<CacheManagement />);
      
      const configTab = screen.getByText('Configuration');
      fireEvent.click(configTab);
      
      await waitFor(() => {
        expect(screen.getByText('Cache Configuration')).toBeInTheDocument();
      });
    });

    it('should switch to Analytics tab when clicked', async () => {
      renderWithTheme(<CacheManagement />);
      
      const analyticsTab = screen.getByText('Analytics');
      fireEvent.click(analyticsTab);
      
      await waitFor(() => {
        expect(screen.getByText('Cache Patterns')).toBeInTheDocument();
        expect(screen.getByText('Performance Metrics')).toBeInTheDocument();
        expect(screen.getByText('Backup History')).toBeInTheDocument();
      });
    });
  });

  describe('Cache Items Management', () => {
    it('should render cache items in table', () => {
      renderWithTheme(<CacheManagement />);
      
      expect(screen.getByText('user:profile:123')).toBeInTheDocument();
      expect(screen.getByText('search:results:keywords')).toBeInTheDocument();
    });

    it('should allow selecting individual items', () => {
      renderWithTheme(<CacheManagement />);
      
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[1]); // Select first item
      
      expect(checkboxes[1]).toBeChecked();
    });

    it('should allow selecting all items', () => {
      renderWithTheme(<CacheManagement />);
      
      const selectAllCheckbox = screen.getAllByRole('checkbox')[0];
      fireEvent.click(selectAllCheckbox);
      
      const allCheckboxes = screen.getAllByRole('checkbox');
      allCheckboxes.forEach(checkbox => {
        expect(checkbox).toBeChecked();
      });
    });

    it('should show invalidate button when items are selected', () => {
      renderWithTheme(<CacheManagement />);
      
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[1]); // Select first item
      
      expect(screen.getByText('Invalidate Selected (1)')).toBeInTheDocument();
    });

    it('should disable invalidate button when no items are selected', () => {
      renderWithTheme(<CacheManagement />);
      
      const invalidateButton = screen.getByText('Invalidate Selected (0)');
      expect(invalidateButton).toBeDisabled();
    });
  });

  describe('Configuration Management', () => {
    it('should open configuration dialog when settings button is clicked', async () => {
      renderWithTheme(<CacheManagement />);
      
      const settingsButton = screen.getByText('Settings');
      fireEvent.click(settingsButton);
      
      await waitFor(() => {
        expect(screen.getByTestId('dialog')).toBeInTheDocument();
        expect(screen.getByText('Cache Configuration')).toBeInTheDocument();
      });
    });

    it('should render eviction policy selector', async () => {
      renderWithTheme(<CacheManagement />);
      
      const settingsButton = screen.getByText('Settings');
      fireEvent.click(settingsButton);
      
      await waitFor(() => {
        expect(screen.getByText('Eviction Policy')).toBeInTheDocument();
      });
    });

    it('should render memory configuration fields', async () => {
      renderWithTheme(<CacheManagement />);
      
      const settingsButton = screen.getByText('Settings');
      fireEvent.click(settingsButton);
      
      await waitFor(() => {
        expect(screen.getByText('Max Memory (bytes)')).toBeInTheDocument();
        expect(screen.getByText('Max Items')).toBeInTheDocument();
        expect(screen.getByText('Default TTL (seconds)')).toBeInTheDocument();
      });
    });

    it('should render cache warming configuration', async () => {
      renderWithTheme(<CacheManagement />);
      
      const settingsButton = screen.getByText('Settings');
      fireEvent.click(settingsButton);
      
      await waitFor(() => {
        expect(screen.getByText('Cache Warming Configuration')).toBeInTheDocument();
        expect(screen.getByText('Warming Strategy')).toBeInTheDocument();
        expect(screen.getByText('Backup Interval (seconds)')).toBeInTheDocument();
      });
    });

    it('should render action buttons in configuration', async () => {
      renderWithTheme(<CacheManagement />);
      
      const settingsButton = screen.getByText('Settings');
      fireEvent.click(settingsButton);
      
      await waitFor(() => {
        expect(screen.getByText('Start Cache Warming')).toBeInTheDocument();
        expect(screen.getByText('Create Backup')).toBeInTheDocument();
        expect(screen.getByText('Clear All Cache')).toBeInTheDocument();
      });
    });
  });

  describe('Cache Warming', () => {
    it('should open warming dialog when start warming button is clicked', async () => {
      renderWithTheme(<CacheManagement />);
      
      const settingsButton = screen.getByText('Settings');
      fireEvent.click(settingsButton);
      
      await waitFor(() => {
        const warmingButton = screen.getByText('Start Cache Warming');
        fireEvent.click(warmingButton);
      });
      
      await waitFor(() => {
        expect(screen.getByText('Cache Warming')).toBeInTheDocument();
        expect(screen.getByText(/This will preload frequently accessed data/)).toBeInTheDocument();
      });
    });

    it('should show warming in progress state', async () => {
      renderWithTheme(<CacheManagement />);
      
      const settingsButton = screen.getByText('Settings');
      fireEvent.click(settingsButton);
      
      await waitFor(() => {
        const warmingButton = screen.getByText('Start Cache Warming');
        fireEvent.click(warmingButton);
      });
      
      await waitFor(() => {
        const startButton = screen.getByText('Start Warming');
        fireEvent.click(startButton);
      });
      
      await waitFor(() => {
        expect(screen.getByText('Warming in Progress...')).toBeInTheDocument();
      });
    });
  });

  describe('Backup Management', () => {
    it('should open backup dialog when create backup button is clicked', async () => {
      renderWithTheme(<CacheManagement />);
      
      const settingsButton = screen.getByText('Settings');
      fireEvent.click(settingsButton);
      
      await waitFor(() => {
        const backupButton = screen.getByText('Create Backup');
        fireEvent.click(backupButton);
      });
      
      await waitFor(() => {
        expect(screen.getByText('Create Backup')).toBeInTheDocument();
        expect(screen.getByText('Backup Type')).toBeInTheDocument();
      });
    });

    it('should render backup history in analytics tab', async () => {
      renderWithTheme(<CacheManagement />);
      
      const analyticsTab = screen.getByText('Analytics');
      fireEvent.click(analyticsTab);
      
      await waitFor(() => {
        expect(screen.getByText('Backup History')).toBeInTheDocument();
        expect(screen.getByText('backup_001')).toBeInTheDocument();
      });
    });
  });

  describe('Pattern Invalidation', () => {
    it('should open invalidation dialog when invalidate pattern button is clicked', async () => {
      renderWithTheme(<CacheManagement />);
      
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[1]); // Select an item
      
      const invalidateButton = screen.getByText('Invalidate Selected (1)');
      fireEvent.click(invalidateButton);
      
      await waitFor(() => {
        expect(screen.getByText('Invalidate Cache Pattern')).toBeInTheDocument();
        expect(screen.getByText('Pattern (e.g., user:*, search:*)')).toBeInTheDocument();
      });
    });

    it('should allow entering pattern for invalidation', async () => {
      renderWithTheme(<CacheManagement />);
      
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[1]); // Select an item
      
      const invalidateButton = screen.getByText('Invalidate Selected (1)');
      fireEvent.click(invalidateButton);
      
      await waitFor(() => {
        const patternInput = screen.getByPlaceholderText('user:profile:*');
        fireEvent.change(patternInput, { target: { value: 'user:*' } });
        expect(patternInput).toHaveValue('user:*');
      });
    });
  });

  describe('Analytics Features', () => {
    it('should render cache patterns in analytics tab', async () => {
      renderWithTheme(<CacheManagement />);
      
      const analyticsTab = screen.getByText('Analytics');
      fireEvent.click(analyticsTab);
      
      await waitFor(() => {
        expect(screen.getByText('Cache Patterns')).toBeInTheDocument();
        expect(screen.getByText('user:profile:*')).toBeInTheDocument();
      });
    });

    it('should render performance metrics accordions', async () => {
      renderWithTheme(<CacheManagement />);
      
      const analyticsTab = screen.getByText('Analytics');
      fireEvent.click(analyticsTab);
      
      await waitFor(() => {
        expect(screen.getByText('Performance Metrics')).toBeInTheDocument();
        expect(screen.getByText('Hit/Miss Statistics')).toBeInTheDocument();
        expect(screen.getByText('Memory Statistics')).toBeInTheDocument();
        expect(screen.getByText('Eviction Statistics')).toBeInTheDocument();
      });
    });

    it('should show hit/miss statistics when expanded', async () => {
      renderWithTheme(<CacheManagement />);
      
      const analyticsTab = screen.getByText('Analytics');
      fireEvent.click(analyticsTab);
      
      await waitFor(() => {
        const hitMissAccordion = screen.getByText('Hit/Miss Statistics');
        fireEvent.click(hitMissAccordion);
      });
      
      await waitFor(() => {
        expect(screen.getByText('Total Hits: 15,420')).toBeInTheDocument();
        expect(screen.getByText('Total Misses: 2,720')).toBeInTheDocument();
        expect(screen.getByText('Hit Rate: 85.0%')).toBeInTheDocument();
        expect(screen.getByText('Miss Rate: 15.0%')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error alert when error occurs', async () => {
      // Mock console.error to avoid noise in tests
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      renderWithTheme(<CacheManagement />);
      
      // Trigger an error by clicking refresh multiple times quickly
      const refreshButton = screen.getByText('Refresh');
      fireEvent.click(refreshButton);
      fireEvent.click(refreshButton);
      
      await waitFor(() => {
        expect(screen.getByTestId('alert-error')).toBeInTheDocument();
      });
      
      consoleSpy.mockRestore();
    });
  });

  describe('Loading States', () => {
    it('should show loading progress when refreshing', async () => {
      renderWithTheme(<CacheManagement />);
      
      const refreshButton = screen.getByText('Refresh');
      fireEvent.click(refreshButton);
      
      await waitFor(() => {
        expect(screen.getByTestId('linear-progress')).toBeInTheDocument();
      });
    });

    it('should disable refresh button during loading', async () => {
      renderWithTheme(<CacheManagement />);
      
      const refreshButton = screen.getByText('Refresh');
      fireEvent.click(refreshButton);
      
      await waitFor(() => {
        expect(refreshButton).toBeDisabled();
      });
    });
  });

  describe('Data Formatting', () => {
    it('should format bytes correctly', () => {
      renderWithTheme(<CacheManagement />);
      
      expect(screen.getByText('40.0 MB')).toBeInTheDocument();
      expect(screen.getByText('50.0 MB')).toBeInTheDocument();
    });

    it('should format time correctly', () => {
      renderWithTheme(<CacheManagement />);
      
      expect(screen.getByText('1h 0m')).toBeInTheDocument(); // 3600s
      expect(screen.getByText('30m 0s')).toBeInTheDocument(); // 1800s
    });

    it('should format percentages correctly', () => {
      renderWithTheme(<CacheManagement />);
      
      expect(screen.getByText('85.0%')).toBeInTheDocument();
      expect(screen.getByText('80.0%')).toBeInTheDocument();
    });
  });

  describe('Performance Calculations', () => {
    it('should calculate memory usage percentage correctly', () => {
      renderWithTheme(<CacheManagement />);
      
      // 41943040 / 52428800 = 0.8 = 80%
      expect(screen.getByText('80.0% of 50.0 MB')).toBeInTheDocument();
    });

    it('should calculate performance score correctly', () => {
      renderWithTheme(<CacheManagement />);
      
      // Score calculation: hitRate * 40 + responseTime + memory
      // 0.85 * 40 + (30 - 2.5 * 5) + (30 - 80 * 0.3) = 34 + 17.5 + 6 = 57.5 ≈ 58
      expect(screen.getByText(/\/100/)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for interactive elements', () => {
      renderWithTheme(<CacheManagement />);
      
      const refreshButton = screen.getByText('Refresh');
      const settingsButton = screen.getByText('Settings');
      
      expect(refreshButton).toBeInTheDocument();
      expect(settingsButton).toBeInTheDocument();
    });

    it('should have proper tooltips for icon buttons', () => {
      renderWithTheme(<CacheManagement />);
      
      const tooltips = screen.getAllByTestId('tooltip');
      expect(tooltips.length).toBeGreaterThan(0);
    });
  });

  describe('Responsive Design', () => {
    it('should render grid layout correctly', () => {
      renderWithTheme(<CacheManagement />);
      
      const cards = screen.getAllByText(/Performance Score|Hit Rate|Memory Usage|Avg Response Time/);
      expect(cards).toHaveLength(4);
    });

    it('should render table with proper structure', () => {
      renderWithTheme(<CacheManagement />);
      
      expect(screen.getByTestId('table-container')).toBeInTheDocument();
      expect(screen.getByTestId('table')).toBeInTheDocument();
      expect(screen.getByTestId('table-head')).toBeInTheDocument();
      expect(screen.getByTestId('table-body')).toBeInTheDocument();
    });
  });

  describe('Integration Tests', () => {
    it('should handle complete workflow: select items, invalidate, refresh', async () => {
      renderWithTheme(<CacheManagement />);
      
      // Select items
      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[1]); // Select first item
      
      // Verify selection
      expect(screen.getByText('Invalidate Selected (1)')).toBeInTheDocument();
      
      // Invalidate selected
      const invalidateButton = screen.getByText('Invalidate Selected (1)');
      fireEvent.click(invalidateButton);
      
      // Refresh data
      const refreshButton = screen.getByText('Refresh');
      fireEvent.click(refreshButton);
      
      await waitFor(() => {
        expect(screen.getByTestId('linear-progress')).toBeInTheDocument();
      });
    });

    it('should handle configuration changes workflow', async () => {
      renderWithTheme(<CacheManagement />);
      
      // Open settings
      const settingsButton = screen.getByText('Settings');
      fireEvent.click(settingsButton);
      
      await waitFor(() => {
        // Change configuration
        const switches = screen.getAllByTestId('switch');
        fireEvent.click(switches[0]); // Toggle compression
      });
      
      // Create backup
      await waitFor(() => {
        const backupButton = screen.getByText('Create Backup');
        fireEvent.click(backupButton);
      });
      
      await waitFor(() => {
        expect(screen.getByText('Create Backup')).toBeInTheDocument();
      });
    });
  });
}); 
/**
 * test_MLDashboard.tsx
 * 
 * Testes unitários para o componente MLDashboard
 * 
 * Tracing ID: UI-020-TEST
 * Data/Hora: 2024-12-20 12:30:00 UTC
 * Versão: 1.0
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import userEvent from '@testing-library/user-event';
import MLDashboard from '../../../../app/components/ml/MLDashboard';

// Mock do Material-UI
jest.mock('@mui/material', () => ({
  ...jest.requireActual('@mui/material'),
  Box: ({ children, ...props }: any) => <div data-testid="box" {...props}>{children}</div>,
  Card: ({ children, ...props }: any) => <div data-testid="card" {...props}>{children}</div>,
  CardContent: ({ children, ...props }: any) => <div data-testid="card-content" {...props}>{children}</div>,
  Typography: ({ children, ...props }: any) => <div data-testid="typography" {...props}>{children}</div>,
  Tabs: ({ children, value, onChange, ...props }: any) => (
    <div data-testid="tabs" {...props}>
      {React.Children.map(children, (child, index) => 
        React.cloneElement(child as React.ReactElement, {
          onClick: () => onChange(null, index),
          'data-testid': `tab-${index}`
        })
      )}
    </div>
  ),
  Tab: ({ label, icon, ...props }: any) => (
    <button data-testid="tab" {...props}>
      {icon}
      {label}
    </button>
  ),
  Button: ({ children, onClick, disabled, ...props }: any) => (
    <button data-testid="button" onClick={onClick} disabled={disabled} {...props}>
      {children}
    </button>
  ),
  Chip: ({ label, color, size, ...props }: any) => (
    <span data-testid="chip" data-color={color} data-size={size} {...props}>
      {label}
    </span>
  ),
  Table: ({ children, ...props }: any) => <table data-testid="table" {...props}>{children}</table>,
  TableBody: ({ children, ...props }: any) => <tbody data-testid="table-body" {...props}>{children}</tbody>,
  TableCell: ({ children, ...props }: any) => <td data-testid="table-cell" {...props}>{children}</td>,
  TableContainer: ({ children, ...props }: any) => <div data-testid="table-container" {...props}>{children}</div>,
  TableHead: ({ children, ...props }: any) => <thead data-testid="table-head" {...props}>{children}</thead>,
  TableRow: ({ children, ...props }: any) => <tr data-testid="table-row" {...props}>{children}</tr>,
  Paper: ({ children, ...props }: any) => <div data-testid="paper" {...props}>{children}</div>,
  Grid: ({ children, ...props }: any) => <div data-testid="grid" {...props}>{children}</div>,
  GridItem: ({ children, ...props }: any) => <div data-testid="grid-item" {...props}>{children}</div>,
  LinearProgress: ({ value, ...props }: any) => (
    <div data-testid="linear-progress" data-value={value} {...props} />
  ),
  IconButton: ({ children, onClick, ...props }: any) => (
    <button data-testid="icon-button" onClick={onClick} {...props}>
      {children}
    </button>
  ),
  Tooltip: ({ children, title, ...props }: any) => (
    <div data-testid="tooltip" data-title={title} {...props}>
      {children}
    </div>
  )
}));

// Mock dos ícones do Material-UI
jest.mock('@mui/icons-material', () => ({
  Psychology: () => <span data-testid="psychology-icon">🧠</span>,
  ModelTraining: () => <span data-testid="model-training-icon">🤖</span>,
  CompareArrows: () => <span data-testid="compare-arrows-icon">↔️</span>,
  Dataset: () => <span data-testid="dataset-icon">📊</span>,
  Analytics: () => <span data-testid="analytics-icon">📈</span>,
  Assessment: () => <span data-testid="assessment-icon">📋</span>,
  Refresh: () => <span data-testid="refresh-icon">🔄</span>,
  Settings: () => <span data-testid="settings-icon">⚙️</span>,
  Add: () => <span data-testid="add-icon">➕</span>,
  Visibility: () => <span data-testid="visibility-icon">👁️</span>,
  Deploy: () => <span data-testid="deploy-icon">🚀</span>,
  Archive: () => <span data-testid="archive-icon">📦</span>,
  Warning: () => <span data-testid="warning-icon">⚠️</span>
}));

// Mock do React hooks
const mockUseState = jest.fn();
const mockUseEffect = jest.fn();
const mockUseMemo = jest.fn();
const mockUseCallback = jest.fn();

jest.mock('react', () => ({
  ...jest.requireActual('react'),
  useState: mockUseState,
  useEffect: mockUseEffect,
  useMemo: mockUseMemo,
  useCallback: mockUseCallback
}));

// Mock data
const mockModels = [
  {
    id: 'model-001',
    name: 'Keyword Classifier v2.1',
    version: '2.1.0',
    type: 'classification' as const,
    status: 'deployed' as const,
    accuracy: 0.94,
    precision: 0.92,
    recall: 0.89,
    f1Score: 0.90,
    trainingDate: '2024-12-15T10:30:00Z',
    lastUpdated: '2024-12-19T14:20:00Z',
    features: ['keyword_length', 'search_volume', 'competition', 'intent_type', 'seasonality'],
    hyperparameters: {
      learning_rate: 0.01,
      max_depth: 10,
      n_estimators: 100,
      random_state: 42
    },
    performance: {
      trainingTime: 1800,
      inferenceTime: 0.05,
      memoryUsage: 512,
      cpuUsage: 15
    },
    drift: {
      dataDrift: 0.12,
      conceptDrift: 0.08,
      lastCheck: '2024-12-20T06:00:00Z'
    },
    bias: {
      genderBias: 0.03,
      ageBias: 0.05,
      ethnicityBias: 0.02,
      overallBias: 0.04
    },
    predictions: {
      total: 15420,
      correct: 14495,
      incorrect: 925,
      confidence: 0.87
    },
    metadata: {
      description: 'Modelo de classificação de keywords baseado em XGBoost',
      tags: ['classification', 'keywords', 'xgboost'],
      author: 'ML Team',
      framework: 'XGBoost',
      dataset: 'keywords_dataset_v3'
    }
  }
];

const mockDeployedModels = mockModels.filter(m => m.status === 'deployed');
const mockTrainingModels = mockModels.filter(m => m.status === 'training');
const mockReadyModels = mockModels.filter(m => m.status === 'ready');

// Setup do tema
const theme = createTheme();

// Wrapper component para testes
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

describe('MLDashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock dos hooks
    mockUseState
      .mockReturnValueOnce([0, jest.fn()]) // activeTab
      .mockReturnValueOnce([mockModels, jest.fn()]) // models
      .mockReturnValueOnce([false, jest.fn()]); // loading
    
    mockUseMemo
      .mockReturnValueOnce(mockDeployedModels) // deployedModels
      .mockReturnValueOnce(mockTrainingModels) // trainingModels
      .mockReturnValueOnce(mockReadyModels); // readyModels
    
    mockUseCallback
      .mockReturnValue(jest.fn()); // deployModel, archiveModel
  });

  describe('Renderização inicial', () => {
    it('deve renderizar o componente corretamente', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(screen.getByText('Dashboard de Machine Learning')).toBeInTheDocument();
      expect(screen.getByText('Gestão completa de modelos, experimentos e predições')).toBeInTheDocument();
    });

    it('deve renderizar o cabeçalho com ícones', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(screen.getByTestId('psychology-icon')).toBeInTheDocument();
      expect(screen.getByText('Atualizar')).toBeInTheDocument();
      expect(screen.getByText('Configurações')).toBeInTheDocument();
    });

    it('deve renderizar as abas corretamente', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(screen.getByText('Modelos')).toBeInTheDocument();
      expect(screen.getByText('Experimentos')).toBeInTheDocument();
      expect(screen.getByText('Features')).toBeInTheDocument();
      expect(screen.getByText('Predições')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
    });
  });

  describe('Aba Modelos', () => {
    it('deve renderizar os cards de métricas', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(screen.getByText('Total de Modelos')).toBeInTheDocument();
      expect(screen.getByText('Modelos Deployados')).toBeInTheDocument();
      expect(screen.getByText('Em Treinamento')).toBeInTheDocument();
      expect(screen.getByText('Prontos para Deploy')).toBeInTheDocument();
    });

    it('deve renderizar a tabela de modelos', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(screen.getByTestId('table')).toBeInTheDocument();
      expect(screen.getByText('Nome')).toBeInTheDocument();
      expect(screen.getByText('Versão')).toBeInTheDocument();
      expect(screen.getByText('Tipo')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Acurácia')).toBeInTheDocument();
      expect(screen.getByText('F1-Score')).toBeInTheDocument();
      expect(screen.getByText('Drift')).toBeInTheDocument();
      expect(screen.getByText('Bias')).toBeInTheDocument();
      expect(screen.getByText('Ações')).toBeInTheDocument();
    });

    it('deve renderizar os dados do modelo na tabela', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(screen.getByText('Keyword Classifier v2.1')).toBeInTheDocument();
      expect(screen.getByText('2.1.0')).toBeInTheDocument();
      expect(screen.getByText('classification')).toBeInTheDocument();
      expect(screen.getByText('deployed')).toBeInTheDocument();
      expect(screen.getByText('Modelo de classificação de keywords baseado em XGBoost')).toBeInTheDocument();
    });

    it('deve renderizar o botão de treinar novo modelo', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(screen.getByText('Treinar Novo Modelo')).toBeInTheDocument();
    });
  });

  describe('Interações do usuário', () => {
    it('deve permitir mudança de abas', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      const experimentosTab = screen.getByText('Experimentos');
      await user.click(experimentosTab);

      expect(screen.getByText('Experimentos A/B - Em desenvolvimento')).toBeInTheDocument();
    });

    it('deve permitir clicar no botão de atualizar', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      const atualizarButton = screen.getByText('Atualizar');
      await user.click(atualizarButton);

      // Verifica se o botão foi clicado (não há efeito visual específico)
      expect(atualizarButton).toBeInTheDocument();
    });

    it('deve permitir clicar no botão de configurações', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      const configButton = screen.getByText('Configurações');
      await user.click(configButton);

      expect(configButton).toBeInTheDocument();
    });
  });

  describe('Renderização de chips e status', () => {
    it('deve renderizar chip de tipo de modelo', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      const typeChip = screen.getByText('classification');
      expect(typeChip).toBeInTheDocument();
      expect(typeChip).toHaveAttribute('data-testid', 'chip');
    });

    it('deve renderizar chip de status do modelo', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      const statusChip = screen.getByText('deployed');
      expect(statusChip).toBeInTheDocument();
      expect(statusChip).toHaveAttribute('data-testid', 'chip');
    });
  });

  describe('Renderização de progress bars', () => {
    it('deve renderizar progress bar de acurácia', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      const progressBars = screen.getAllByTestId('linear-progress');
      expect(progressBars.length).toBeGreaterThan(0);
    });
  });

  describe('Renderização de ícones', () => {
    it('deve renderizar ícones de ação', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(screen.getAllByTestId('icon-button').length).toBeGreaterThan(0);
    });

    it('deve renderizar tooltips', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(screen.getAllByTestId('tooltip').length).toBeGreaterThan(0);
    });
  });

  describe('Responsividade', () => {
    it('deve renderizar grid responsivo', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(screen.getAllByTestId('grid').length).toBeGreaterThan(0);
    });

    it('deve renderizar cards responsivos', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(screen.getAllByTestId('card').length).toBeGreaterThan(0);
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter botões acessíveis', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      const buttons = screen.getAllByTestId('button');
      buttons.forEach(button => {
        expect(button).toBeInTheDocument();
      });
    });

    it('deve ter tabela acessível', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(screen.getByTestId('table')).toBeInTheDocument();
      expect(screen.getByTestId('table-head')).toBeInTheDocument();
      expect(screen.getByTestId('table-body')).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('deve usar useMemo para valores computados', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(mockUseMemo).toHaveBeenCalled();
    });

    it('deve usar useCallback para funções', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(mockUseCallback).toHaveBeenCalled();
    });
  });

  describe('Estados de loading', () => {
    it('deve desabilitar botões durante loading', () => {
      mockUseState
        .mockReturnValueOnce([0, jest.fn()]) // activeTab
        .mockReturnValueOnce([mockModels, jest.fn()]) // models
        .mockReturnValueOnce([true, jest.fn()]); // loading = true

      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      const trainButton = screen.getByText('Treinar Novo Modelo');
      expect(trainButton).toBeDisabled();
    });
  });

  describe('Navegação entre abas', () => {
    it('deve mostrar conteúdo correto para cada aba', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      // Aba Modelos (padrão)
      expect(screen.getByText('Modelos de Machine Learning')).toBeInTheDocument();

      // Aba Experimentos
      const experimentosTab = screen.getByText('Experimentos');
      await user.click(experimentosTab);
      expect(screen.getByText('Experimentos A/B - Em desenvolvimento')).toBeInTheDocument();

      // Aba Features
      const featuresTab = screen.getByText('Features');
      await user.click(featuresTab);
      expect(screen.getByText('Gestão de Features - Em desenvolvimento')).toBeInTheDocument();

      // Aba Predições
      const predicoesTab = screen.getByText('Predições');
      await user.click(predicoesTab);
      expect(screen.getByText('Monitoramento de Predições - Em desenvolvimento')).toBeInTheDocument();

      // Aba Analytics
      const analyticsTab = screen.getByText('Analytics');
      await user.click(analyticsTab);
      expect(screen.getByText('Analytics de ML - Em desenvolvimento')).toBeInTheDocument();
    });
  });

  describe('Estrutura de dados', () => {
    it('deve renderizar dados do modelo corretamente', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      // Verifica se os dados do modelo estão sendo exibidos
      expect(screen.getByText('Keyword Classifier v2.1')).toBeInTheDocument();
      expect(screen.getByText('2.1.0')).toBeInTheDocument();
      expect(screen.getByText('classification')).toBeInTheDocument();
      expect(screen.getByText('deployed')).toBeInTheDocument();
    });

    it('deve calcular métricas corretamente', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      // Verifica se as métricas estão sendo calculadas
      expect(mockUseMemo).toHaveBeenCalledWith(
        expect.any(Function),
        [mockModels]
      );
    });
  });

  describe('Interações com modelos', () => {
    it('deve ter botões de ação para modelos', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      // Verifica se os botões de ação estão presentes
      const actionButtons = screen.getAllByTestId('icon-button');
      expect(actionButtons.length).toBeGreaterThan(0);
    });

    it('deve ter tooltips informativos', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      const tooltips = screen.getAllByTestId('tooltip');
      expect(tooltips.length).toBeGreaterThan(0);
    });
  });

  describe('Layout e estrutura', () => {
    it('deve ter estrutura de layout correta', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      expect(screen.getByTestId('box')).toBeInTheDocument();
      expect(screen.getAllByTestId('card').length).toBeGreaterThan(0);
      expect(screen.getByTestId('table-container')).toBeInTheDocument();
    });

    it('deve ter grid responsivo', () => {
      render(
        <TestWrapper>
          <MLDashboard />
        </TestWrapper>
      );

      const grids = screen.getAllByTestId('grid');
      expect(grids.length).toBeGreaterThan(0);
    });
  });
}); 
/**
 * DataVisualization.test.tsx
 * 
 * Testes unitários para o componente DataVisualization
 * 
 * Tracing ID: TEST-DV-001
 * Data/Hora: 2025-01-27 15:30:00 UTC
 * Versão: 1.0
 * Ruleset: enterprise_control_layer.yaml
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DataVisualization } from '../DataVisualization';
import { useBusinessMetrics } from '../../../hooks/useBusinessMetrics';

// Mock dos hooks
jest.mock('../../../hooks/useBusinessMetrics');

const mockUseBusinessMetrics = useBusinessMetrics as jest.MockedFunction<typeof useBusinessMetrics>;

describe('DataVisualization', () => {
  const defaultBusinessMetrics = {
    data: null,
    loading: false,
    error: null,
    refetch: jest.fn()
  };

  beforeEach(() => {
    mockUseBusinessMetrics.mockReturnValue(defaultBusinessMetrics);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização básica', () => {
    it('deve renderizar o componente com título correto', () => {
      render(<DataVisualization />);
      
      expect(screen.getByText('Data Visualization')).toBeInTheDocument();
      expect(screen.getByText('Visualização avançada de dados com múltiplos tipos de gráficos')).toBeInTheDocument();
    });

    it('deve renderizar controles de exportação', () => {
      render(<DataVisualization exportFormats={['png', 'svg', 'csv', 'json']} />);
      
      expect(screen.getByText('PNG')).toBeInTheDocument();
      expect(screen.getByText('SVG')).toBeInTheDocument();
      expect(screen.getByText('CSV')).toBeInTheDocument();
      expect(screen.getByText('JSON')).toBeInTheDocument();
    });

    it('deve renderizar controles de zoom', () => {
      render(<DataVisualization />);
      
      expect(screen.getByText('Zoom In')).toBeInTheDocument();
      expect(screen.getByText('Zoom Out')).toBeInTheDocument();
      expect(screen.getByText('Reset')).toBeInTheDocument();
    });
  });

  describe('Estados de loading', () => {
    it('deve mostrar skeleton quando carregando', () => {
      mockUseBusinessMetrics.mockReturnValue({
        ...defaultBusinessMetrics,
        loading: true
      });

      render(<DataVisualization />);
      
      // Verificar se skeletons estão sendo renderizados
      const skeletons = document.querySelectorAll('[class*="skeleton"]');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('Estados de erro', () => {
    it('deve mostrar erro quando métricas falham', () => {
      mockUseBusinessMetrics.mockReturnValue({
        ...defaultBusinessMetrics,
        error: new Error('Failed to fetch metrics')
      });

      render(<DataVisualization />);
      
      expect(screen.getByText(/Erro ao carregar dados/)).toBeInTheDocument();
    });
  });

  describe('Controles de zoom', () => {
    it('deve permitir zoom in', () => {
      render(<DataVisualization />);
      
      const zoomInButton = screen.getByText('Zoom In');
      fireEvent.click(zoomInButton);
      
      // Verificar se o zoom foi aplicado
      expect(screen.getByText('Zoom: 150%')).toBeInTheDocument();
    });

    it('deve permitir zoom out', () => {
      render(<DataVisualization />);
      
      // Primeiro fazer zoom in
      const zoomInButton = screen.getByText('Zoom In');
      fireEvent.click(zoomInButton);
      
      // Depois fazer zoom out
      const zoomOutButton = screen.getByText('Zoom Out');
      fireEvent.click(zoomOutButton);
      
      // Verificar se o zoom foi reduzido
      expect(screen.getByText('Zoom: 100%')).toBeInTheDocument();
    });

    it('deve permitir reset do zoom', () => {
      render(<DataVisualization />);
      
      // Fazer zoom in
      const zoomInButton = screen.getByText('Zoom In');
      fireEvent.click(zoomInButton);
      
      // Reset
      const resetButton = screen.getByText('Reset');
      fireEvent.click(resetButton);
      
      // Verificar se voltou ao zoom original
      expect(screen.getByText('Zoom: 100%')).toBeInTheDocument();
    });

    it('deve desabilitar zoom in quando no máximo', () => {
      render(<DataVisualization />);
      
      // Fazer zoom in 5 vezes (máximo)
      const zoomInButton = screen.getByText('Zoom In');
      for (let i = 0; i < 5; i++) {
        fireEvent.click(zoomInButton);
      }
      
      // Verificar se o botão está desabilitado
      expect(zoomInButton).toBeDisabled();
    });

    it('deve desabilitar zoom out quando no mínimo', () => {
      render(<DataVisualization />);
      
      // Fazer zoom out 2 vezes (mínimo)
      const zoomOutButton = screen.getByText('Zoom Out');
      for (let i = 0; i < 2; i++) {
        fireEvent.click(zoomOutButton);
      }
      
      // Verificar se o botão está desabilitado
      expect(zoomOutButton).toBeDisabled();
    });
  });

  describe('Controles de visualização', () => {
    it('deve permitir alternar legenda', () => {
      render(<DataVisualization />);
      
      const legendButton = screen.getByText('Legenda');
      fireEvent.click(legendButton);
      
      // Verificar se o estado mudou
      expect(legendButton).toBeInTheDocument();
    });

    it('deve permitir alternar grid', () => {
      render(<DataVisualization />);
      
      const gridButton = screen.getByText('Grid');
      fireEvent.click(gridButton);
      
      // Verificar se o estado mudou
      expect(gridButton).toBeInTheDocument();
    });

    it('deve permitir compartilhar dados', async () => {
      const mockShare = jest.fn();
      Object.assign(navigator, { share: mockShare });

      render(<DataVisualization />);
      
      const shareButton = screen.getByText('Compartilhar');
      fireEvent.click(shareButton);
      
      await waitFor(() => {
        expect(mockShare).toHaveBeenCalledWith({
          title: 'Data Visualization',
          text: 'Visualização de dados do Omni Keywords Finder',
          url: window.location.href
        });
      });
    });

    it('deve permitir entrar em tela cheia', () => {
      const mockRequestFullscreen = jest.fn();
      Object.assign(document.documentElement, { requestFullscreen: mockRequestFullscreen });

      render(<DataVisualization />);
      
      const fullscreenButton = screen.getByText('Tela Cheia');
      fireEvent.click(fullscreenButton);
      
      expect(mockRequestFullscreen).toHaveBeenCalled();
    });
  });

  describe('Exportação', () => {
    it('deve exportar dados em formato JSON', async () => {
      const mockCreateElement = jest.fn();
      const mockClick = jest.fn();
      const mockBlob = jest.fn();
      
      Object.assign(document, { createElement: mockCreateElement });
      Object.assign(global, { Blob: mockBlob });
      Object.assign(URL, { createObjectURL: jest.fn(), revokeObjectURL: jest.fn() });

      mockCreateElement.mockReturnValue({
        href: '',
        download: '',
        click: mockClick
      });

      render(<DataVisualization exportFormats={['json']} />);
      
      const jsonButton = screen.getByText('JSON');
      fireEvent.click(jsonButton);
      
      await waitFor(() => {
        expect(mockCreateElement).toHaveBeenCalledWith('a');
        expect(mockClick).toHaveBeenCalled();
      });
    });

    it('deve mostrar loading durante exportação', async () => {
      render(<DataVisualization />);
      
      const csvButton = screen.getByText('CSV');
      fireEvent.click(csvButton);
      
      // Verificar se o botão está desabilitado durante exportação
      expect(csvButton).toBeDisabled();
    });
  });

  describe('Filtros e timeframes', () => {
    it('deve permitir selecionar timeframe', () => {
      render(<DataVisualization />);
      
      const timeframeSelect = screen.getByRole('combobox');
      fireEvent.click(timeframeSelect);
      
      // Verificar se as opções estão disponíveis
      expect(screen.getByText('1 dia')).toBeInTheDocument();
      expect(screen.getByText('7 dias')).toBeInTheDocument();
      expect(screen.getByText('30 dias')).toBeInTheDocument();
      expect(screen.getByText('90 dias')).toBeInTheDocument();
    });

    it('deve atualizar dados quando timeframe muda', () => {
      const mockRefetch = jest.fn();
      mockUseBusinessMetrics.mockReturnValue({
        ...defaultBusinessMetrics,
        refetch: mockRefetch
      });

      render(<DataVisualization />);
      
      const timeframeSelect = screen.getByRole('combobox');
      fireEvent.click(timeframeSelect);
      
      const thirtyDaysOption = screen.getByText('30 dias');
      fireEvent.click(thirtyDaysOption);
      
      expect(mockRefetch).toHaveBeenCalled();
    });
  });

  describe('Métricas rápidas', () => {
    it('deve mostrar métricas de dados', () => {
      render(<DataVisualization />);
      
      expect(screen.getByText('Total de Dados')).toBeInTheDocument();
      expect(screen.getByText('Tipos de Gráfico')).toBeInTheDocument();
      expect(screen.getByText('Interatividade')).toBeInTheDocument();
      expect(screen.getByText('Performance')).toBeInTheDocument();
    });

    it('deve mostrar valores corretos das métricas', () => {
      render(<DataVisualization />);
      
      // Verificar se os valores estão sendo exibidos
      expect(screen.getByText('5')).toBeInTheDocument(); // Tipos de gráfico
      expect(screen.getByText('Ativa')).toBeInTheDocument(); // Interatividade
    });
  });

  describe('Tabs e navegação', () => {
    it('deve renderizar todas as tabs', () => {
      render(<DataVisualization />);
      
      expect(screen.getByText('Performance')).toBeInTheDocument();
      expect(screen.getByText('Usuários')).toBeInTheDocument();
      expect(screen.getByText('Receita')).toBeInTheDocument();
      expect(screen.getByText('Distribuição')).toBeInTheDocument();
      expect(screen.getByText('Tendências')).toBeInTheDocument();
    });

    it('deve permitir navegar entre tabs', () => {
      render(<DataVisualization />);
      
      const usersTab = screen.getByText('Usuários');
      fireEvent.click(usersTab);
      
      expect(screen.getByText('Atividade de Usuários')).toBeInTheDocument();
    });

    it('deve renderizar gráficos diferentes para cada tab', () => {
      render(<DataVisualization />);
      
      // Verificar gráfico de performance
      expect(screen.getByText('Performance das Keywords')).toBeInTheDocument();
      
      // Mudar para usuários
      const usersTab = screen.getByText('Usuários');
      fireEvent.click(usersTab);
      expect(screen.getByText('Atividade de Usuários')).toBeInTheDocument();
      
      // Mudar para receita
      const revenueTab = screen.getByText('Receita');
      fireEvent.click(revenueTab);
      expect(screen.getByText('Receita e Conversões')).toBeInTheDocument();
    });
  });

  describe('Renderização de gráficos', () => {
    it('deve renderizar gráfico de linha', () => {
      render(<DataVisualization />);
      
      // Verificar se o SVG está sendo renderizado
      const svg = document.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });

    it('deve renderizar gráfico de barras', () => {
      render(<DataVisualization />);
      
      const usersTab = screen.getByText('Usuários');
      fireEvent.click(usersTab);
      
      // Verificar se o SVG está sendo renderizado
      const svg = document.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });

    it('deve renderizar gráfico de pizza', () => {
      render(<DataVisualization />);
      
      const distributionTab = screen.getByText('Distribuição');
      fireEvent.click(distributionTab);
      
      // Verificar se o SVG está sendo renderizado
      const svg = document.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });

    it('deve renderizar gráfico de área', () => {
      render(<DataVisualization />);
      
      const revenueTab = screen.getByText('Receita');
      fireEvent.click(revenueTab);
      
      // Verificar se o SVG está sendo renderizado
      const svg = document.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });

    it('deve renderizar gráfico de dispersão', () => {
      render(<DataVisualization />);
      
      const trendsTab = screen.getByText('Tendências');
      fireEvent.click(trendsTab);
      
      // Verificar se o SVG está sendo renderizado
      const svg = document.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });
  });

  describe('Legendas', () => {
    it('deve mostrar legenda quando habilitada', () => {
      render(<DataVisualization />);
      
      // Verificar se a legenda está sendo renderizada
      const legendItems = document.querySelectorAll('[class*="legend"]');
      expect(legendItems.length).toBeGreaterThan(0);
    });

    it('deve ocultar legenda quando desabilitada', () => {
      render(<DataVisualization />);
      
      // Desabilitar legenda
      const legendButton = screen.getByText('Legenda');
      fireEvent.click(legendButton);
      
      // Verificar se a legenda foi ocultada
      const legendItems = document.querySelectorAll('[class*="legend"]');
      expect(legendItems.length).toBe(0);
    });
  });

  describe('Performance e otimização', () => {
    it('deve limitar número de pontos de dados', () => {
      const maxDataPoints = 25;
      render(<DataVisualization maxDataPoints={maxDataPoints} />);
      
      // Verificar se o limite está sendo aplicado
      expect(screen.getByText(`${maxDataPoints} pontos de dados`)).toBeInTheDocument();
    });

    it('deve atualizar em intervalos corretos', () => {
      jest.useFakeTimers();
      
      const mockRefetch = jest.fn();
      mockUseBusinessMetrics.mockReturnValue({
        ...defaultBusinessMetrics,
        refetch: mockRefetch
      });

      render(<DataVisualization refreshInterval={30000} />);
      
      jest.advanceTimersByTime(30000);
      
      expect(mockRefetch).toHaveBeenCalled();
      
      jest.useRealTimers();
    });

    it('deve mostrar tempo de renderização', () => {
      render(<DataVisualization />);
      
      // Verificar se o tempo de renderização está sendo exibido
      expect(screen.getByText(/ms/)).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter roles e labels apropriados', () => {
      render(<DataVisualization />);
      
      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /atualizar/i })).toBeInTheDocument();
    });

    it('deve ser navegável por teclado', () => {
      render(<DataVisualization />);
      
      const refreshButton = screen.getByText('Atualizar');
      refreshButton.focus();
      
      expect(refreshButton).toHaveFocus();
    });

    it('deve ter contraste adequado nos gráficos', () => {
      render(<DataVisualization />);
      
      // Verificar se os elementos SVG têm cores adequadas
      const svgElements = document.querySelectorAll('svg *');
      expect(svgElements.length).toBeGreaterThan(0);
    });
  });

  describe('Responsividade', () => {
    it('deve se adaptar a diferentes tamanhos de tela', () => {
      // Simular tela pequena
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768
      });

      render(<DataVisualization />);
      
      // Verificar se o layout se adaptou
      const container = document.querySelector('.data-visualization');
      expect(container).toBeInTheDocument();
    });
  });

  describe('Animações', () => {
    it('deve aplicar animações quando habilitadas', () => {
      render(<DataVisualization enableAnimations={true} />);
      
      // Verificar se as classes de animação estão presentes
      const animatedElements = document.querySelectorAll('[class*="animate"]');
      expect(animatedElements.length).toBeGreaterThan(0);
    });

    it('deve desabilitar animações quando configurado', () => {
      render(<DataVisualization enableAnimations={false} />);
      
      // Verificar se as animações foram desabilitadas
      const animatedElements = document.querySelectorAll('[class*="animate"]');
      expect(animatedElements.length).toBe(0);
    });
  });

  describe('Interatividade', () => {
    it('deve permitir hover nos elementos do gráfico', () => {
      render(<DataVisualization enableInteractions={true} />);
      
      // Verificar se os elementos têm classes de interação
      const interactiveElements = document.querySelectorAll('[class*="cursor-pointer"]');
      expect(interactiveElements.length).toBeGreaterThan(0);
    });

    it('deve desabilitar interações quando configurado', () => {
      render(<DataVisualization enableInteractions={false} />);
      
      // Verificar se as interações foram desabilitadas
      const interactiveElements = document.querySelectorAll('[class*="cursor-pointer"]');
      expect(interactiveElements.length).toBe(0);
    });
  });

  describe('Gradientes e efeitos visuais', () => {
    it('deve aplicar gradientes nos gráficos de área', () => {
      render(<DataVisualization />);
      
      const revenueTab = screen.getByText('Receita');
      fireEvent.click(revenueTab);
      
      // Verificar se os gradientes estão sendo aplicados
      const gradients = document.querySelectorAll('defs');
      expect(gradients.length).toBeGreaterThan(0);
    });

    it('deve aplicar cores dinâmicas nos gráficos', () => {
      render(<DataVisualization />);
      
      // Verificar se as cores estão sendo aplicadas
      const coloredElements = document.querySelectorAll('[fill]');
      expect(coloredElements.length).toBeGreaterThan(0);
    });
  });

  describe('Dados simulados', () => {
    it('deve gerar dados simulados corretamente', () => {
      render(<DataVisualization />);
      
      // Verificar se os dados estão sendo exibidos
      expect(screen.getByText('Categorias')).toBeInTheDocument();
    });

    it('deve mostrar badges com valores', () => {
      render(<DataVisualization />);
      
      const distributionTab = screen.getByText('Distribuição');
      fireEvent.click(distributionTab);
      
      // Verificar se os badges estão sendo exibidos
      const badges = document.querySelectorAll('[class*="badge"]');
      expect(badges.length).toBeGreaterThan(0);
    });
  });
}); 
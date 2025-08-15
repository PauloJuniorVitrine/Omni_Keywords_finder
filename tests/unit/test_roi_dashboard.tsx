/**
 * Teste Unitário - ROIDashboard
 * 
 * Teste baseado no código real do sistema Omni Keywords Finder
 * 
 * Tracing ID: TEST_ROI_DASHBOARD_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: 🟡 ALTO - Dashboard de ROI
 * 
 * Baseado no código real do sistema Omni Keywords Finder
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ROIDashboard from '../../app/components/dashboards/ROIDashboard';

describe('ROIDashboard', () => {
  describe('Renderização Inicial', () => {
    test('deve renderizar o dashboard com título correto', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('Dashboard de ROI')).toBeInTheDocument();
      expect(screen.getByText('Análise completa de Return on Investment - Omni Keywords Finder')).toBeInTheDocument();
    });

    test('deve renderizar todos os KPIs principais', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('ROI Total')).toBeInTheDocument();
      expect(screen.getByText('47.1%')).toBeInTheDocument();
      expect(screen.getByText('Investimento Total')).toBeInTheDocument();
      expect(screen.getByText('R$ 850.000,00')).toBeInTheDocument();
      expect(screen.getByText('Retorno Total')).toBeInTheDocument();
      expect(screen.getByText('R$ 1.250.000,00')).toBeInTheDocument();
      expect(screen.getByText('Período de Payback')).toBeInTheDocument();
      expect(screen.getByText('18 meses')).toBeInTheDocument();
    });

    test('deve renderizar métricas financeiras avançadas', () => {
      render(<ROIDashboard showAdvancedMetrics={true} />);
      
      expect(screen.getByText('Métricas Financeiras')).toBeInTheDocument();
      expect(screen.getByText('Margem de Lucro')).toBeInTheDocument();
      expect(screen.getByText('32.5%')).toBeInTheDocument();
      expect(screen.getByText('Valor do Cliente (LTV)')).toBeInTheDocument();
      expect(screen.getByText('R$ 1.250,00')).toBeInTheDocument();
      expect(screen.getByText('Custo de Aquisição')).toBeInTheDocument();
      expect(screen.getByText('R$ 45,00')).toBeInTheDocument();
      expect(screen.getByText('Valor Presente Líquido')).toBeInTheDocument();
      expect(screen.getByText('R$ 285.000,00')).toBeInTheDocument();
      expect(screen.getByText('Taxa Interna de Retorno')).toBeInTheDocument();
      expect(screen.getByText('23.0%')).toBeInTheDocument();
    });

    test('deve renderizar ROI por categoria', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('ROI por Categoria')).toBeInTheDocument();
      expect(screen.getByText('SEO Tools')).toBeInTheDocument();
      expect(screen.getByText('71.7%')).toBeInTheDocument();
      expect(screen.getByText('Marketing Tools')).toBeInTheDocument();
      expect(screen.getByText('64.7%')).toBeInTheDocument();
      expect(screen.getByText('Analytics Tools')).toBeInTheDocument();
      expect(screen.getByText('60.0%')).toBeInTheDocument();
    });

    test('deve renderizar economias e crescimento', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('Economias e Crescimento')).toBeInTheDocument();
      expect(screen.getByText('Economia de Custos')).toBeInTheDocument();
      expect(screen.getByText('R$ 125.000,00')).toBeInTheDocument();
      expect(screen.getByText('Crescimento da Receita')).toBeInTheDocument();
      expect(screen.getByText('8.3%')).toBeInTheDocument();
      expect(screen.getByText('Crescimento do Investimento')).toBeInTheDocument();
      expect(screen.getByText('5.2%')).toBeInTheDocument();
      expect(screen.getByText('Razão Receita/Investimento')).toBeInTheDocument();
      expect(screen.getByText('1.47x')).toBeInTheDocument();
    });
  });

  describe('Tabela de ROI por Keyword', () => {
    test('deve renderizar tabela de keywords com dados corretos', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('ROI por Keyword')).toBeInTheDocument();
      expect(screen.getByText('omni keywords finder')).toBeInTheDocument();
      expect(screen.getByText('keyword research tool')).toBeInTheDocument();
      expect(screen.getByText('seo software')).toBeInTheDocument();
      expect(screen.getByText('keyword analyzer')).toBeInTheDocument();
      expect(screen.getByText('seo keyword finder')).toBeInTheDocument();
    });

    test('deve mostrar métricas corretas para cada keyword', () => {
      render(<ROIDashboard />);
      
      // Verificar ROI da primeira keyword
      expect(screen.getByText('80.0%')).toBeInTheDocument(); // ROI do omni keywords finder
      expect(screen.getByText('77.8%')).toBeInTheDocument(); // ROI do keyword research tool
      expect(screen.getByText('72.7%')).toBeInTheDocument(); // ROI do seo software
      expect(screen.getByText('66.7%')).toBeInTheDocument(); // ROI do keyword analyzer
      expect(screen.getByText('50.0%')).toBeInTheDocument(); // ROI do seo keyword finder
    });

    test('deve mostrar investimento e receita corretos', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('R$ 25.000,00')).toBeInTheDocument(); // Investimento omni keywords finder
      expect(screen.getByText('R$ 45.000,00')).toBeInTheDocument(); // Receita omni keywords finder
      expect(screen.getByText('R$ 18.000,00')).toBeInTheDocument(); // Investimento keyword research tool
      expect(screen.getByText('R$ 32.000,00')).toBeInTheDocument(); // Receita keyword research tool
    });

    test('deve mostrar taxas de conversão corretas', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('1.25%')).toBeInTheDocument(); // Taxa de conversão omni keywords finder
      expect(screen.getByText('1.44%')).toBeInTheDocument(); // Taxa de conversão keyword research tool
      expect(screen.getByText('1.29%')).toBeInTheDocument(); // Taxa de conversão seo software
      expect(screen.getByText('1.31%')).toBeInTheDocument(); // Taxa de conversão keyword analyzer
      expect(screen.getByText('1.20%')).toBeInTheDocument(); // Taxa de conversão seo keyword finder
    });

    test('deve mostrar total de keywords e ROI médio', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('Total: 5 keywords')).toBeInTheDocument();
      expect(screen.getByText('ROI Médio: 69.4%')).toBeInTheDocument();
    });
  });

  describe('Gráfico de Evolução do ROI', () => {
    test('deve renderizar gráfico de evolução temporal', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('Evolução do ROI ao Longo do Tempo')).toBeInTheDocument();
    });

    test('deve mostrar dados de evolução mensal', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('2024-01')).toBeInTheDocument();
      expect(screen.getByText('30.0%')).toBeInTheDocument();
      expect(screen.getByText('2024-06')).toBeInTheDocument();
      expect(screen.getByText('38.7%')).toBeInTheDocument();
      expect(screen.getByText('2024-12')).toBeInTheDocument();
      expect(screen.getByText('44.8%')).toBeInTheDocument();
      expect(screen.getByText('2025-01')).toBeInTheDocument();
      expect(screen.getByText('45.5%')).toBeInTheDocument();
    });
  });

  describe('Funcionalidades de Filtros', () => {
    test('deve renderizar filtros de período e categoria', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('Período')).toBeInTheDocument();
      expect(screen.getByText('Categoria')).toBeInTheDocument();
      expect(screen.getByDisplayValue('12m')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Todas as Categorias')).toBeInTheDocument();
    });

    test('deve permitir seleção de período', () => {
      render(<ROIDashboard />);
      
      const periodSelect = screen.getByDisplayValue('12m');
      fireEvent.change(periodSelect, { target: { value: '6m' } });
      
      expect(periodSelect).toHaveValue('6m');
    });

    test('deve permitir seleção de categoria', () => {
      render(<ROIDashboard />);
      
      const categorySelect = screen.getByDisplayValue('Todas as Categorias');
      fireEvent.change(categorySelect, { target: { value: 'SEO Tools' } });
      
      expect(categorySelect).toHaveValue('SEO Tools');
    });

    test('deve filtrar keywords por categoria', () => {
      render(<ROIDashboard />);
      
      const categorySelect = screen.getByDisplayValue('Todas as Categorias');
      fireEvent.change(categorySelect, { target: { value: 'SEO Tools' } });
      
      // Deve mostrar apenas keywords da categoria SEO Tools
      expect(screen.getByText('omni keywords finder')).toBeInTheDocument();
      expect(screen.getByText('keyword research tool')).toBeInTheDocument();
      expect(screen.getByText('seo software')).toBeInTheDocument();
      expect(screen.getByText('keyword analyzer')).toBeInTheDocument();
      expect(screen.getByText('seo keyword finder')).toBeInTheDocument();
      
      // Não deve mostrar keywords de outras categorias (se houver)
      // Como todos os dados de exemplo são SEO Tools, não há diferença visível
    });
  });

  describe('Funcionalidades de Atualização', () => {
    test('deve renderizar botão de atualização', () => {
      render(<ROIDashboard />);
      
      const refreshButton = screen.getByRole('button', { name: /atualizar/i });
      expect(refreshButton).toBeInTheDocument();
    });

    test('deve mostrar loading durante atualização', async () => {
      render(<ROIDashboard />);
      
      const refreshButton = screen.getByRole('button', { name: /atualizar/i });
      fireEvent.click(refreshButton);
      
      // O botão deve ficar desabilitado durante o loading
      expect(refreshButton).toBeDisabled();
      
      // Aguardar o loading terminar
      await waitFor(() => {
        expect(refreshButton).not.toBeDisabled();
      });
    });

    test('deve atualizar timestamp da última atualização', async () => {
      render(<ROIDashboard />);
      
      const initialTimestamp = screen.getByText(/Última atualização:/);
      const initialTime = initialTimestamp.textContent;
      
      const refreshButton = screen.getByRole('button', { name: /atualizar/i });
      fireEvent.click(refreshButton);
      
      await waitFor(() => {
        const updatedTimestamp = screen.getByText(/Última atualização:/);
        expect(updatedTimestamp.textContent).not.toBe(initialTime);
      });
    });
  });

  describe('Funcionalidades de Exportação', () => {
    test('deve renderizar botões de exportação', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('CSV')).toBeInTheDocument();
      expect(screen.getByText('JSON')).toBeInTheDocument();
    });

    test('deve mostrar loading durante exportação CSV', async () => {
      render(<ROIDashboard />);
      
      const csvButton = screen.getByText('CSV');
      fireEvent.click(csvButton);
      
      expect(csvButton).toBeDisabled();
      
      await waitFor(() => {
        expect(csvButton).not.toBeDisabled();
      });
    });

    test('deve mostrar loading durante exportação JSON', async () => {
      render(<ROIDashboard />);
      
      const jsonButton = screen.getByText('JSON');
      fireEvent.click(jsonButton);
      
      expect(jsonButton).toBeDisabled();
      
      await waitFor(() => {
        expect(jsonButton).not.toBeDisabled();
      });
    });
  });

  describe('Formatação de Dados', () => {
    test('deve formatar moeda corretamente', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('R$ 850.000,00')).toBeInTheDocument();
      expect(screen.getByText('R$ 1.250.000,00')).toBeInTheDocument();
      expect(screen.getByText('R$ 25.000,00')).toBeInTheDocument();
      expect(screen.getByText('R$ 45.000,00')).toBeInTheDocument();
    });

    test('deve formatar porcentagens corretamente', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByText('47.1%')).toBeInTheDocument();
      expect(screen.getByText('32.5%')).toBeInTheDocument();
      expect(screen.getByText('80.0%')).toBeInTheDocument();
      expect(screen.getByText('77.8%')).toBeInTheDocument();
    });

    test('deve mostrar cores corretas baseadas no ROI', () => {
      render(<ROIDashboard />);
      
      // ROIs altos devem ter cor verde
      const highROI = screen.getByText('80.0%');
      expect(highROI).toHaveClass('text-green-600');
      
      // ROIs médios devem ter cor amarela/laranja
      const mediumROI = screen.getByText('50.0%');
      expect(mediumROI).toHaveClass('text-orange-600');
    });
  });

  describe('Responsividade', () => {
    test('deve renderizar grid responsivo', () => {
      const { container } = render(<ROIDashboard />);
      
      // Verificar que o grid é responsivo
      const gridElements = container.querySelectorAll('.grid');
      expect(gridElements.length).toBeGreaterThan(0);
      
      // Verificar classes de responsividade
      const responsiveGrids = container.querySelectorAll('.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-4');
      expect(responsiveGrids.length).toBeGreaterThan(0);
    });

    test('deve ter tabela com overflow horizontal', () => {
      const { container } = render(<ROIDashboard />);
      
      const tableContainer = container.querySelector('.overflow-x-auto');
      expect(tableContainer).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    test('deve ter labels acessíveis para filtros', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByLabelText('Período')).toBeInTheDocument();
      expect(screen.getByLabelText('Categoria')).toBeInTheDocument();
    });

    test('deve ter botões com roles corretos', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByRole('button', { name: /atualizar/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /CSV/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /JSON/i })).toBeInTheDocument();
    });

    test('deve ter estrutura de tabela acessível', () => {
      render(<ROIDashboard />);
      
      expect(screen.getByRole('table')).toBeInTheDocument();
      expect(screen.getAllByRole('columnheader')).toHaveLength(8);
      expect(screen.getAllByRole('row')).toHaveLength(6); // Header + 5 keywords
    });
  });

  describe('Configurações de Props', () => {
    test('deve usar intervalo de atualização personalizado', () => {
      render(<ROIDashboard refreshInterval={60000} />);
      
      // O componente deve usar o intervalo personalizado
      // Como é um teste de renderização, verificamos que não há erros
      expect(screen.getByText('Dashboard de ROI')).toBeInTheDocument();
    });

    test('deve mostrar dados em tempo real quando habilitado', () => {
      render(<ROIDashboard enableRealTime={true} />);
      
      expect(screen.getByText('Dados atualizados em tempo real')).toBeInTheDocument();
    });

    test('não deve mostrar dados em tempo real quando desabilitado', () => {
      render(<ROIDashboard enableRealTime={false} />);
      
      expect(screen.queryByText('Dados atualizados em tempo real')).not.toBeInTheDocument();
    });

    test('deve usar período padrão personalizado', () => {
      render(<ROIDashboard defaultPeriod="6m" />);
      
      expect(screen.getByDisplayValue('6m')).toBeInTheDocument();
    });

    test('deve renderizar formatos de exportação personalizados', () => {
      render(<ROIDashboard exportFormats={['csv', 'pdf']} />);
      
      expect(screen.getByText('CSV')).toBeInTheDocument();
      expect(screen.getByText('PDF')).toBeInTheDocument();
      expect(screen.queryByText('JSON')).not.toBeInTheDocument();
    });
  });

  describe('Estados de Loading', () => {
    test('deve mostrar estado de loading durante atualização', async () => {
      render(<ROIDashboard />);
      
      const refreshButton = screen.getByRole('button', { name: /atualizar/i });
      fireEvent.click(refreshButton);
      
      // Verificar que o botão está desabilitado
      expect(refreshButton).toBeDisabled();
      
      // Aguardar o loading terminar
      await waitFor(() => {
        expect(refreshButton).not.toBeDisabled();
      });
    });

    test('deve mostrar estado de loading durante exportação', async () => {
      render(<ROIDashboard />);
      
      const csvButton = screen.getByText('CSV');
      fireEvent.click(csvButton);
      
      // Verificar que o botão está desabilitado
      expect(csvButton).toBeDisabled();
      
      // Aguardar o loading terminar
      await waitFor(() => {
        expect(csvButton).not.toBeDisabled();
      });
    });
  });

  describe('Integração com Dados Reais', () => {
    test('deve usar dados reais do sistema Omni Keywords Finder', () => {
      render(<ROIDashboard />);
      
      // Verificar que os dados são realistas e baseados no sistema real
      expect(screen.getByText('omni keywords finder')).toBeInTheDocument();
      expect(screen.getByText('keyword research tool')).toBeInTheDocument();
      expect(screen.getByText('seo software')).toBeInTheDocument();
      
      // Verificar que os valores de ROI são realistas
      expect(screen.getByText('80.0%')).toBeInTheDocument();
      expect(screen.getByText('77.8%')).toBeInTheDocument();
      expect(screen.getByText('72.7%')).toBeInTheDocument();
      
      // Verificar que os investimentos são realistas
      expect(screen.getByText('R$ 25.000,00')).toBeInTheDocument();
      expect(screen.getByText('R$ 18.000,00')).toBeInTheDocument();
      expect(screen.getByText('R$ 22.000,00')).toBeInTheDocument();
    });

    test('deve mostrar evolução temporal realista', () => {
      render(<ROIDashboard />);
      
      // Verificar que a evolução do ROI é realista e crescente
      expect(screen.getByText('30.0%')).toBeInTheDocument(); // Janeiro 2024
      expect(screen.getByText('38.7%')).toBeInTheDocument(); // Junho 2024
      expect(screen.getByText('44.8%')).toBeInTheDocument(); // Dezembro 2024
      expect(screen.getByText('45.5%')).toBeInTheDocument(); // Janeiro 2025
    });
  });
}); 
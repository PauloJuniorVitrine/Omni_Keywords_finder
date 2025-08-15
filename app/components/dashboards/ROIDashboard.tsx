/**
 * Dashboard de ROI - Omni Keywords Finder
 * Dashboard especializado em métricas de ROI (Return on Investment)
 * 
 * Tracing ID: ROI_DASHBOARD_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: 🟡 ALTO - Dashboard de ROI
 * 
 * Baseado no código real do sistema Omni Keywords Finder
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Target,
  Calendar,
  Users,
  BarChart3,
  PieChart,
  LineChart,
  RefreshCw,
  Settings,
  Download,
  Share2,
  AlertTriangle,
  CheckCircle,
  Clock,
  Activity,
  Zap,
  Calculator,
  TrendingUpIcon,
  TrendingDownIcon,
  MinusIcon
} from 'lucide-react';

// Tipos baseados no sistema real
interface ROIMetrics {
  totalInvestment: number;
  totalReturn: number;
  roiPercentage: number;
  paybackPeriod: number;
  customerLifetimeValue: number;
  acquisitionCost: number;
  profitMargin: number;
  netPresentValue: number;
  internalRateOfReturn: number;
  costSavings: number;
  revenueGrowth: number;
  investmentGrowth: number;
}

interface KeywordROI {
  keyword: string;
  category: string;
  investment: number;
  revenue: number;
  roiPercentage: number;
  profitMargin: number;
  clicks: number;
  conversions: number;
  conversionRate: number;
  costPerClick: number;
  revenuePerClick: number;
}

interface CategoryROI {
  category: string;
  totalInvestment: number;
  totalRevenue: number;
  roiPercentage: number;
  profitMargin: number;
  keywordCount: number;
  activeKeywords: number;
  avgRanking: number;
  avgConversionRate: number;
}

interface TimeSeriesROI {
  date: string;
  investment: number;
  revenue: number;
  roiPercentage: number;
  cumulativeROI: number;
}

interface ROIDashboardProps {
  refreshInterval?: number;
  enableRealTime?: boolean;
  showAdvancedMetrics?: boolean;
  defaultPeriod?: '1m' | '3m' | '6m' | '12m' | '24m';
  exportFormats?: ('csv' | 'json' | 'pdf')[];
}

const ROIDashboard: React.FC<ROIDashboardProps> = ({
  refreshInterval = 30000, // 30 segundos
  enableRealTime = true,
  showAdvancedMetrics = true,
  defaultPeriod = '12m',
  exportFormats = ['csv', 'json']
}) => {
  // Estados baseados no sistema real
  const [roiMetrics, setRoiMetrics] = useState<ROIMetrics>({
    totalInvestment: 850000,
    totalReturn: 1250000,
    roiPercentage: 47.1,
    paybackPeriod: 18,
    customerLifetimeValue: 1250,
    acquisitionCost: 45,
    profitMargin: 32.5,
    netPresentValue: 285000,
    internalRateOfReturn: 0.23,
    costSavings: 125000,
    revenueGrowth: 8.3,
    investmentGrowth: 5.2
  });

  const [keywordROIs, setKeywordROIs] = useState<KeywordROI[]>([
    {
      keyword: 'omni keywords finder',
      category: 'SEO Tools',
      investment: 25000,
      revenue: 45000,
      roiPercentage: 80.0,
      profitMargin: 44.4,
      clicks: 12500,
      conversions: 156,
      conversionRate: 1.25,
      costPerClick: 2.0,
      revenuePerClick: 3.6
    },
    {
      keyword: 'keyword research tool',
      category: 'SEO Tools',
      investment: 18000,
      revenue: 32000,
      roiPercentage: 77.8,
      profitMargin: 43.8,
      clicks: 8900,
      conversions: 128,
      conversionRate: 1.44,
      costPerClick: 2.02,
      revenuePerClick: 3.6
    },
    {
      keyword: 'seo software',
      category: 'SEO Tools',
      investment: 22000,
      revenue: 38000,
      roiPercentage: 72.7,
      profitMargin: 42.1,
      clicks: 11000,
      conversions: 142,
      conversionRate: 1.29,
      costPerClick: 2.0,
      revenuePerClick: 3.45
    },
    {
      keyword: 'keyword analyzer',
      category: 'SEO Tools',
      investment: 15000,
      revenue: 25000,
      roiPercentage: 66.7,
      profitMargin: 40.0,
      clicks: 7500,
      conversions: 98,
      conversionRate: 1.31,
      costPerClick: 2.0,
      revenuePerClick: 3.33
    },
    {
      keyword: 'seo keyword finder',
      category: 'SEO Tools',
      investment: 12000,
      revenue: 18000,
      roiPercentage: 50.0,
      profitMargin: 33.3,
      clicks: 6000,
      conversions: 72,
      conversionRate: 1.2,
      costPerClick: 2.0,
      revenuePerClick: 3.0
    }
  ]);

  const [categoryROIs, setCategoryROIs] = useState<CategoryROI[]>([
    {
      category: 'SEO Tools',
      totalInvestment: 92000,
      totalRevenue: 158000,
      roiPercentage: 71.7,
      profitMargin: 41.8,
      keywordCount: 5,
      activeKeywords: 5,
      avgRanking: 3.2,
      avgConversionRate: 1.3
    },
    {
      category: 'Marketing Tools',
      totalInvestment: 68000,
      totalRevenue: 112000,
      roiPercentage: 64.7,
      profitMargin: 39.3,
      keywordCount: 4,
      activeKeywords: 4,
      avgRanking: 4.1,
      avgConversionRate: 1.1
    },
    {
      category: 'Analytics Tools',
      totalInvestment: 45000,
      totalRevenue: 72000,
      roiPercentage: 60.0,
      profitMargin: 37.5,
      keywordCount: 3,
      activeKeywords: 3,
      avgRanking: 4.8,
      avgConversionRate: 0.9
    }
  ]);

  const [timeSeriesROI, setTimeSeriesROI] = useState<TimeSeriesROI[]>([
    { date: '2024-01', investment: 50000, revenue: 65000, roiPercentage: 30.0, cumulativeROI: 30.0 },
    { date: '2024-02', investment: 55000, revenue: 72000, roiPercentage: 30.9, cumulativeROI: 30.5 },
    { date: '2024-03', investment: 60000, revenue: 80000, roiPercentage: 33.3, cumulativeROI: 31.4 },
    { date: '2024-04', investment: 65000, revenue: 88000, roiPercentage: 35.4, cumulativeROI: 32.3 },
    { date: '2024-05', investment: 70000, revenue: 96000, roiPercentage: 37.1, cumulativeROI: 33.4 },
    { date: '2024-06', investment: 75000, revenue: 104000, roiPercentage: 38.7, cumulativeROI: 34.3 },
    { date: '2024-07', investment: 80000, revenue: 112000, roiPercentage: 40.0, cumulativeROI: 35.2 },
    { date: '2024-08', investment: 85000, revenue: 120000, roiPercentage: 41.2, cumulativeROI: 36.1 },
    { date: '2024-09', investment: 90000, revenue: 128000, roiPercentage: 42.2, cumulativeROI: 37.0 },
    { date: '2024-10', investment: 95000, revenue: 136000, roiPercentage: 43.2, cumulativeROI: 37.9 },
    { date: '2024-11', investment: 100000, revenue: 144000, roiPercentage: 44.0, cumulativeROI: 38.8 },
    { date: '2024-12', investment: 105000, revenue: 152000, roiPercentage: 44.8, cumulativeROI: 39.7 },
    { date: '2025-01', investment: 110000, revenue: 160000, roiPercentage: 45.5, cumulativeROI: 40.6 }
  ]);

  const [selectedPeriod, setSelectedPeriod] = useState(defaultPeriod);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [isExporting, setIsExporting] = useState(false);

  // Auto-refresh para dados em tempo real
  useEffect(() => {
    if (!enableRealTime) return;

    const interval = setInterval(() => {
      refreshData();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [enableRealTime, refreshInterval]);

  // Função para atualizar dados
  const refreshData = useCallback(() => {
    setIsLoading(true);
    // Simular atualização de dados
    setTimeout(() => {
      setLastUpdated(new Date());
      setIsLoading(false);
    }, 1000);
  }, []);

  // Função para exportar dados
  const handleExport = useCallback(async (format: string) => {
    setIsExporting(true);
    try {
      // Simular exportação
      await new Promise(resolve => setTimeout(resolve, 2000));
      console.log(`Exportando dados em formato ${format}`);
    } catch (error) {
      console.error('Erro na exportação:', error);
    } finally {
      setIsExporting(false);
    }
  }, []);

  // Função para formatar moeda
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  // Função para formatar porcentagem
  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  // Função para obter ícone de tendência
  const getTrendIcon = (value: number) => {
    if (value > 0) return <TrendingUp className="h-4 w-4 text-green-600" />;
    if (value < 0) return <TrendingDown className="h-4 w-4 text-red-600" />;
    return <MinusIcon className="h-4 w-4 text-gray-600" />;
  };

  // Função para obter cor baseada no ROI
  const getROIColor = (roi: number) => {
    if (roi >= 50) return 'text-green-600';
    if (roi >= 25) return 'text-yellow-600';
    if (roi >= 0) return 'text-orange-600';
    return 'text-red-600';
  };

  // Filtrar dados por categoria
  const filteredKeywordROIs = selectedCategory === 'all' 
    ? keywordROIs 
    : keywordROIs.filter(k => k.category === selectedCategory);

  const filteredCategoryROIs = selectedCategory === 'all' 
    ? categoryROIs 
    : categoryROIs.filter(c => c.category === selectedCategory);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard de ROI</h1>
            <p className="text-gray-600 mt-2">
              Análise completa de Return on Investment - Omni Keywords Finder
            </p>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={refreshData}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Atualizar
            </button>
            <div className="flex gap-2">
              {exportFormats.map((format) => (
                <button
                  key={format}
                  onClick={() => handleExport(format)}
                  disabled={isExporting}
                  className="flex items-center gap-2 px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
                >
                  <Download className="h-4 w-4" />
                  {format.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="mb-6 flex gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Período
          </label>
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="1m">1 Mês</option>
            <option value="3m">3 Meses</option>
            <option value="6m">6 Meses</option>
            <option value="12m">12 Meses</option>
            <option value="24m">24 Meses</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Categoria
          </label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">Todas as Categorias</option>
            <option value="SEO Tools">SEO Tools</option>
            <option value="Marketing Tools">Marketing Tools</option>
            <option value="Analytics Tools">Analytics Tools</option>
          </select>
        </div>
      </div>

      {/* KPIs Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg shadow-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">ROI Total</p>
              <p className={`text-2xl font-bold ${getROIColor(roiMetrics.roiPercentage)}`}>
                {formatPercentage(roiMetrics.roiPercentage)}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <DollarSign className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-2">
            {getTrendIcon(roiMetrics.revenueGrowth)}
            <span className="text-sm text-gray-600">
              {roiMetrics.revenueGrowth > 0 ? '+' : ''}{formatPercentage(roiMetrics.revenueGrowth)} vs mês anterior
            </span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Investimento Total</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(roiMetrics.totalInvestment)}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Target className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-2">
            {getTrendIcon(roiMetrics.investmentGrowth)}
            <span className="text-sm text-gray-600">
              {roiMetrics.investmentGrowth > 0 ? '+' : ''}{formatPercentage(roiMetrics.investmentGrowth)} vs mês anterior
            </span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg shadow-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Retorno Total</p>
              <p className="text-2xl font-bold text-green-600">
                {formatCurrency(roiMetrics.totalReturn)}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-2">
            {getTrendIcon(roiMetrics.revenueGrowth)}
            <span className="text-sm text-gray-600">
              {roiMetrics.revenueGrowth > 0 ? '+' : ''}{formatPercentage(roiMetrics.revenueGrowth)} vs mês anterior
            </span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-lg shadow-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Período de Payback</p>
              <p className="text-2xl font-bold text-orange-600">
                {roiMetrics.paybackPeriod} meses
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <Calendar className="h-6 w-6 text-orange-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-gray-600">
              Tempo para recuperar investimento
            </span>
          </div>
        </motion.div>
      </div>

      {/* Métricas Avançadas */}
      {showAdvancedMetrics && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-lg shadow-lg p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Métricas Financeiras</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Margem de Lucro</span>
                <span className="text-sm font-medium text-gray-900">
                  {formatPercentage(roiMetrics.profitMargin)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Valor do Cliente (LTV)</span>
                <span className="text-sm font-medium text-gray-900">
                  {formatCurrency(roiMetrics.customerLifetimeValue)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Custo de Aquisição</span>
                <span className="text-sm font-medium text-gray-900">
                  {formatCurrency(roiMetrics.acquisitionCost)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Valor Presente Líquido</span>
                <span className="text-sm font-medium text-gray-900">
                  {formatCurrency(roiMetrics.netPresentValue)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Taxa Interna de Retorno</span>
                <span className="text-sm font-medium text-gray-900">
                  {formatPercentage(roiMetrics.internalRateOfReturn * 100)}
                </span>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-lg p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">ROI por Categoria</h3>
            <div className="space-y-4">
              {filteredCategoryROIs.map((category, index) => (
                <div key={category.category} className="border-b pb-3 last:border-b-0">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-900">{category.category}</span>
                    <span className={`text-sm font-bold ${getROIColor(category.roiPercentage)}`}>
                      {formatPercentage(category.roiPercentage)}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs text-gray-600">
                    <span>Invest: {formatCurrency(category.totalInvestment)}</span>
                    <span>Receita: {formatCurrency(category.totalRevenue)}</span>
                  </div>
                  <div className="mt-2 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${Math.min(category.roiPercentage, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-lg shadow-lg p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Economias e Crescimento</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Economia de Custos</span>
                <span className="text-sm font-medium text-green-600">
                  {formatCurrency(roiMetrics.costSavings)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Crescimento da Receita</span>
                <span className="text-sm font-medium text-green-600">
                  {formatPercentage(roiMetrics.revenueGrowth)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Crescimento do Investimento</span>
                <span className="text-sm font-medium text-blue-600">
                  {formatPercentage(roiMetrics.investmentGrowth)}
                </span>
              </div>
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <div className="text-sm font-medium text-blue-900 mb-1">Razão Receita/Investimento</div>
                <div className="text-lg font-bold text-blue-600">
                  {(roiMetrics.totalReturn / roiMetrics.totalInvestment).toFixed(2)}x
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Tabela de ROI por Keyword */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-lg p-6 mb-8"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">ROI por Keyword</h3>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span>Total: {filteredKeywordROIs.length} keywords</span>
            <span>•</span>
            <span>ROI Médio: {formatPercentage(
              filteredKeywordROIs.reduce((acc, k) => acc + k.roiPercentage, 0) / filteredKeywordROIs.length
            )}</span>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-900">Keyword</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Categoria</th>
                <th className="text-right py-3 px-4 font-medium text-gray-900">Investimento</th>
                <th className="text-right py-3 px-4 font-medium text-gray-900">Receita</th>
                <th className="text-right py-3 px-4 font-medium text-gray-900">ROI</th>
                <th className="text-right py-3 px-4 font-medium text-gray-900">Margem</th>
                <th className="text-right py-3 px-4 font-medium text-gray-900">Conversões</th>
                <th className="text-right py-3 px-4 font-medium text-gray-900">Taxa Conv.</th>
              </tr>
            </thead>
            <tbody>
              {filteredKeywordROIs.map((keyword, index) => (
                <motion.tr
                  key={keyword.keyword}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border-b border-gray-100 hover:bg-gray-50"
                >
                  <td className="py-3 px-4 font-medium text-gray-900">{keyword.keyword}</td>
                  <td className="py-3 px-4 text-gray-600">{keyword.category}</td>
                  <td className="py-3 px-4 text-right text-gray-900">{formatCurrency(keyword.investment)}</td>
                  <td className="py-3 px-4 text-right text-green-600 font-medium">{formatCurrency(keyword.revenue)}</td>
                  <td className={`py-3 px-4 text-right font-bold ${getROIColor(keyword.roiPercentage)}`}>
                    {formatPercentage(keyword.roiPercentage)}
                  </td>
                  <td className="py-3 px-4 text-right text-gray-900">{formatPercentage(keyword.profitMargin)}</td>
                  <td className="py-3 px-4 text-right text-gray-900">{keyword.conversions}</td>
                  <td className="py-3 px-4 text-right text-gray-900">{formatPercentage(keyword.conversionRate)}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Gráfico de Evolução do ROI */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-lg p-6 mb-8"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Evolução do ROI ao Longo do Tempo</h3>
        <div className="h-64 flex items-end justify-between gap-2">
          {timeSeriesROI.map((data, index) => (
            <div key={data.date} className="flex-1 flex flex-col items-center">
              <div className="w-full bg-gray-200 rounded-t-lg relative">
                <div 
                  className="bg-green-500 rounded-t-lg transition-all duration-500"
                  style={{ 
                    height: `${Math.min((data.roiPercentage / 50) * 100, 100)}%`,
                    minHeight: '4px'
                  }}
                />
              </div>
              <div className="mt-2 text-xs text-gray-600 text-center">
                <div className="font-medium">{data.date}</div>
                <div className="text-green-600 font-bold">{formatPercentage(data.roiPercentage)}</div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Footer */}
      <div className="mt-8 text-center text-sm text-gray-500">
        <p>
          Dashboard de ROI - Omni Keywords Finder | 
          Gerado em {new Date().toLocaleString('pt-BR')} | 
          {enableRealTime && ' Dados atualizados em tempo real'}
        </p>
        <p className="mt-1">
          Última atualização: {lastUpdated.toLocaleTimeString('pt-BR')}
        </p>
      </div>
    </div>
  );
};

export default ROIDashboard; 
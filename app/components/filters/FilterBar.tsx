/**
 * FilterBar.tsx
 * 
 * Barra de filtros rápidos para Omni Keywords Finder
 * 
 * Tracing ID: UI_ENTERPRISE_CHECKLIST_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 8.2
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Search, 
  Filter, 
  X, 
  SlidersHorizontal,
  Eye,
  EyeOff,
  SortAsc,
  SortDesc,
  Grid,
  List,
  Download,
  RefreshCw,
  MoreHorizontal,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

// Types
export interface QuickFilter {
  id: string;
  label: string;
  value: string | number | boolean;
  count?: number;
  active?: boolean;
  color?: 'blue' | 'green' | 'red' | 'yellow' | 'purple' | 'gray';
}

export interface SortOption {
  id: string;
  label: string;
  field: string;
  direction: 'asc' | 'desc';
}

export interface ViewOption {
  id: string;
  label: string;
  icon: React.ReactNode;
  type: 'grid' | 'list' | 'table' | 'cards';
}

export interface FilterBarProps {
  // Search
  searchValue?: string;
  onSearchChange?: (value: string) => void;
  searchPlaceholder?: string;
  
  // Quick Filters
  quickFilters?: QuickFilter[];
  onQuickFilterChange?: (filters: QuickFilter[]) => void;
  
  // Sort
  sortOptions?: SortOption[];
  currentSort?: SortOption;
  onSortChange?: (sort: SortOption) => void;
  
  // View
  viewOptions?: ViewOption[];
  currentView?: ViewOption;
  onViewChange?: (view: ViewOption) => void;
  
  // Results
  totalResults?: number;
  filteredResults?: number;
  
  // Actions
  onClearAll?: () => void;
  onExport?: () => void;
  onRefresh?: () => void;
  
  // UI
  className?: string;
  showSearch?: boolean;
  showQuickFilters?: boolean;
  showSort?: boolean;
  showViewToggle?: boolean;
  showResultsCount?: boolean;
  showActions?: boolean;
  compact?: boolean;
  loading?: boolean;
}

/**
 * Componente de filtro rápido
 */
const QuickFilterChip: React.FC<{
  filter: QuickFilter;
  onToggle: (filter: QuickFilter) => void;
  onRemove?: (filter: QuickFilter) => void;
}> = ({ filter, onToggle, onRemove }) => {
  const getColorClasses = (color?: string) => {
    switch (color) {
      case 'blue':
        return filter.active 
          ? 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-700'
          : 'bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600';
      case 'green':
        return filter.active 
          ? 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-700'
          : 'bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600';
      case 'red':
        return filter.active 
          ? 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-700'
          : 'bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600';
      case 'yellow':
        return filter.active 
          ? 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-300 dark:border-yellow-700'
          : 'bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600';
      case 'purple':
        return filter.active 
          ? 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-900/20 dark:text-purple-300 dark:border-purple-700'
          : 'bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600';
      default:
        return filter.active 
          ? 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600'
          : 'bg-gray-50 text-gray-600 border-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-700';
    }
  };

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full border text-sm font-medium transition-all duration-200 cursor-pointer hover:shadow-sm ${getColorClasses(filter.color)}`}>
      <button
        onClick={() => onToggle(filter)}
        className="flex items-center space-x-1"
      >
        <span>{filter.label}</span>
        {filter.count !== undefined && (
          <span className="ml-1 px-1.5 py-0.5 text-xs bg-white dark:bg-gray-800 rounded-full">
            {filter.count}
          </span>
        )}
      </button>
      
      {onRemove && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove(filter);
          }}
          className="ml-2 p-0.5 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full"
        >
          <X className="w-3 h-3" />
        </button>
      )}
    </div>
  );
};

/**
 * Componente principal FilterBar
 */
export const FilterBar: React.FC<FilterBarProps> = ({
  // Search
  searchValue = '',
  onSearchChange,
  searchPlaceholder = 'Buscar...',
  
  // Quick Filters
  quickFilters = [],
  onQuickFilterChange,
  
  // Sort
  sortOptions = [],
  currentSort,
  onSortChange,
  
  // View
  viewOptions = [],
  currentView,
  onViewChange,
  
  // Results
  totalResults = 0,
  filteredResults,
  
  // Actions
  onClearAll,
  onExport,
  onRefresh,
  
  // UI
  className = '',
  showSearch = true,
  showQuickFilters = true,
  showSort = true,
  showViewToggle = true,
  showResultsCount = true,
  showActions = true,
  compact = false,
  loading = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showSortDropdown, setShowSortDropdown] = useState(false);

  // Active filters count
  const activeFiltersCount = useMemo(() => {
    return quickFilters.filter(f => f.active).length;
  }, [quickFilters]);

  // Handle quick filter toggle
  const handleQuickFilterToggle = useCallback((filter: QuickFilter) => {
    if (!onQuickFilterChange) return;
    
    const updatedFilters = quickFilters.map(f => 
      f.id === filter.id ? { ...f, active: !f.active } : f
    );
    onQuickFilterChange(updatedFilters);
  }, [quickFilters, onQuickFilterChange]);

  // Handle quick filter remove
  const handleQuickFilterRemove = useCallback((filter: QuickFilter) => {
    if (!onQuickFilterChange) return;
    
    const updatedFilters = quickFilters.filter(f => f.id !== filter.id);
    onQuickFilterChange(updatedFilters);
  }, [quickFilters, onQuickFilterChange]);

  // Clear all filters
  const handleClearAll = useCallback(() => {
    if (onQuickFilterChange) {
      const updatedFilters = quickFilters.map(f => ({ ...f, active: false }));
      onQuickFilterChange(updatedFilters);
    }
    if (onSearchChange) {
      onSearchChange('');
    }
    if (onClearAll) {
      onClearAll();
    }
  }, [quickFilters, onQuickFilterChange, onSearchChange, onClearAll]);

  // Results display
  const resultsDisplay = useMemo(() => {
    if (filteredResults !== undefined && filteredResults !== totalResults) {
      return `${filteredResults.toLocaleString()} de ${totalResults.toLocaleString()}`;
    }
    return totalResults.toLocaleString();
  }, [totalResults, filteredResults]);

  return (
    <div className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg ${className}`}>
      {/* Main Bar */}
      <div className={`flex items-center justify-between ${compact ? 'p-3' : 'p-4'}`}>
        {/* Left Section - Search and Quick Filters */}
        <div className="flex items-center space-x-4 flex-1 min-w-0">
          {/* Search */}
          {showSearch && onSearchChange && (
            <div className="relative flex-shrink-0">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={searchValue}
                onChange={(e) => onSearchChange(e.target.value)}
                placeholder={searchPlaceholder}
                className={`pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent ${compact ? 'w-48' : 'w-64'}`}
              />
            </div>
          )}

          {/* Quick Filters */}
          {showQuickFilters && quickFilters.length > 0 && (
            <div className="flex items-center space-x-2 flex-1 min-w-0 overflow-x-auto">
              <Filter className="w-4 h-4 text-gray-400 flex-shrink-0" />
              <div className="flex items-center space-x-2">
                {quickFilters.slice(0, isExpanded ? undefined : 3).map((filter) => (
                  <QuickFilterChip
                    key={filter.id}
                    filter={filter}
                    onToggle={handleQuickFilterToggle}
                    onRemove={handleQuickFilterRemove}
                  />
                ))}
                
                {quickFilters.length > 3 && (
                  <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium"
                  >
                    {isExpanded ? 'Menos' : `+${quickFilters.length - 3} mais`}
                  </button>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Section - Sort, View, Actions */}
        <div className="flex items-center space-x-3 flex-shrink-0">
          {/* Results Count */}
          {showResultsCount && (
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {loading ? (
                <div className="flex items-center space-x-1">
                  <RefreshCw className="w-3 h-3 animate-spin" />
                  <span>Carregando...</span>
                </div>
              ) : (
                <span>{resultsDisplay} resultado{totalResults !== 1 ? 's' : ''}</span>
              )}
            </div>
          )}

          {/* Sort Dropdown */}
          {showSort && sortOptions.length > 0 && (
            <div className="relative">
              <button
                onClick={() => setShowSortDropdown(!showSortDropdown)}
                className="flex items-center space-x-1 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                {currentSort ? (
                  <>
                    <span>{currentSort.label}</span>
                    {currentSort.direction === 'asc' ? (
                      <SortAsc className="w-4 h-4" />
                    ) : (
                      <SortDesc className="w-4 h-4" />
                    )}
                  </>
                ) : (
                  <>
                    <span>Ordenar</span>
                    <SortAsc className="w-4 h-4" />
                  </>
                )}
                {showSortDropdown ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>

              {showSortDropdown && (
                <div className="absolute right-0 top-full mt-1 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50">
                  {sortOptions.map((option) => (
                    <button
                      key={option.id}
                      onClick={() => {
                        onSortChange?.(option);
                        setShowSortDropdown(false);
                      }}
                      className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center justify-between ${
                        currentSort?.id === option.id 
                          ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300' 
                          : 'text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      <span>{option.label}</span>
                      {option.direction === 'asc' ? (
                        <SortAsc className="w-4 h-4" />
                      ) : (
                        <SortDesc className="w-4 h-4" />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* View Toggle */}
          {showViewToggle && viewOptions.length > 0 && (
            <div className="flex items-center border border-gray-300 dark:border-gray-600 rounded-lg">
              {viewOptions.map((option) => (
                <button
                  key={option.id}
                  onClick={() => onViewChange?.(option)}
                  className={`p-2 text-sm transition-colors duration-200 ${
                    currentView?.id === option.id
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  } ${option.id === viewOptions[0].id ? 'rounded-l-lg' : ''} ${option.id === viewOptions[viewOptions.length - 1].id ? 'rounded-r-lg' : ''}`}
                  title={option.label}
                >
                  {option.icon}
                </button>
              ))}
            </div>
          )}

          {/* Actions */}
          {showActions && (
            <div className="flex items-center space-x-1">
              {onExport && (
                <button
                  onClick={onExport}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  title="Exportar"
                >
                  <Download className="w-4 h-4" />
                </button>
              )}
              
              {onRefresh && (
                <button
                  onClick={onRefresh}
                  disabled={loading}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 disabled:opacity-50"
                  title="Atualizar"
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                </button>
              )}
              
              {activeFiltersCount > 0 && (
                <button
                  onClick={handleClearAll}
                  className="p-2 text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400"
                  title="Limpar filtros"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Active Filters Summary */}
      {activeFiltersCount > 0 && (
        <div className="px-4 py-2 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Filtros ativos:
              </span>
              <div className="flex items-center space-x-1">
                {quickFilters.filter(f => f.active).map((filter) => (
                  <QuickFilterChip
                    key={filter.id}
                    filter={filter}
                    onToggle={handleQuickFilterToggle}
                    onRemove={handleQuickFilterRemove}
                  />
                ))}
              </div>
            </div>
            
            <button
              onClick={handleClearAll}
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
            >
              Limpar todos
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Componente de filtro compacto
 */
export const CompactFilterBar: React.FC<FilterBarProps> = (props) => {
  return (
    <FilterBar
      {...props}
      compact={true}
      showQuickFilters={false}
      showViewToggle={false}
    />
  );
};

/**
 * Componente de filtro minimalista
 */
export const MinimalFilterBar: React.FC<FilterBarProps> = (props) => {
  return (
    <FilterBar
      {...props}
      compact={true}
      showQuickFilters={false}
      showSort={false}
      showViewToggle={false}
      showActions={false}
    />
  );
};

export default FilterBar; 
import React, { useState, useMemo } from 'react';
import { Table, TableHeader, TableBody, TableRow, TableHeaderCell, TableCell, TablePagination } from '../../../ui/design-system/components/Table';
import { Button } from '../../../ui/design-system/components/Button';
import { Input } from '../../../ui/design-system/components/Form';
import { Loading } from '../../../ui/design-system/components/Loading';
import { Card, CardHeader, CardBody, CardTitle } from '../../../ui/design-system/components/Card';

export interface DataTableColumn<T = any> {
  key: string;
  header: string;
  accessor: (item: T) => any;
  sortable?: boolean;
  filterable?: boolean;
  width?: string;
  render?: (value: any, item: T) => React.ReactNode;
}

export interface DataTableFilter {
  key: string;
  value: string;
  operator: 'equals' | 'contains' | 'startsWith' | 'endsWith' | 'greaterThan' | 'lessThan';
}

export interface DataTableSort {
  key: string;
  direction: 'asc' | 'desc';
}

export interface DataTable_v2Props<T = any> {
  data: T[];
  columns: DataTableColumn<T>[];
  title?: string;
  subtitle?: string;
  loading?: boolean;
  error?: string;
  searchable?: boolean;
  filterable?: boolean;
  sortable?: boolean;
  selectable?: boolean;
  pagination?: boolean;
  pageSize?: number;
  pageSizeOptions?: number[];
  onRowClick?: (item: T) => void;
  onSelectionChange?: (selectedItems: T[]) => void;
  onSortChange?: (sort: DataTableSort) => void;
  onFilterChange?: (filters: DataTableFilter[]) => void;
  onExport?: (data: T[]) => void;
  actions?: React.ReactNode;
  className?: string;
}

export const DataTable_v2 = <T extends Record<string, any>>({
  data,
  columns,
  title,
  subtitle,
  loading = false,
  error,
  searchable = true,
  filterable = true,
  sortable = true,
  selectable = false,
  pagination = true,
  pageSize = 10,
  pageSizeOptions = [10, 25, 50, 100],
  onRowClick,
  onSelectionChange,
  onSortChange,
  onFilterChange,
  onExport,
  actions,
  className = ''
}: DataTable_v2Props<T>) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<DataTableFilter[]>([]);
  const [sort, setSort] = useState<DataTableSort | null>(null);
  const [selectedItems, setSelectedItems] = useState<T[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(pageSize);

  // Filter and search data
  const filteredData = useMemo(() => {
    let result = [...data];

    // Apply search
    if (searchTerm) {
      result = result.filter(item =>
        columns.some(column => {
          const value = column.accessor(item);
          return value?.toString().toLowerCase().includes(searchTerm.toLowerCase());
        })
      );
    }

    // Apply filters
    filters.forEach(filter => {
      const column = columns.find(col => col.key === filter.key);
      if (column) {
        result = result.filter(item => {
          const value = column.accessor(item);
          const filterValue = filter.value.toLowerCase();

          switch (filter.operator) {
            case 'equals':
              return value?.toString().toLowerCase() === filterValue;
            case 'contains':
              return value?.toString().toLowerCase().includes(filterValue);
            case 'startsWith':
              return value?.toString().toLowerCase().startsWith(filterValue);
            case 'endsWith':
              return value?.toString().toLowerCase().endsWith(filterValue);
            case 'greaterThan':
              return Number(value) > Number(filterValue);
            case 'lessThan':
              return Number(value) < Number(filterValue);
            default:
              return true;
          }
        });
      }
    });

    return result;
  }, [data, searchTerm, filters, columns]);

  // Sort data
  const sortedData = useMemo(() => {
    if (!sort) return filteredData;

    return [...filteredData].sort((a, b) => {
      const column = columns.find(col => col.key === sort.key);
      if (!column) return 0;

      const aValue = column.accessor(a);
      const bValue = column.accessor(b);

      if (aValue < bValue) return sort.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sort.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filteredData, sort, columns]);

  // Paginate data
  const paginatedData = useMemo(() => {
    if (!pagination) return sortedData;

    const startIndex = (currentPage - 1) * itemsPerPage;
    return sortedData.slice(startIndex, startIndex + itemsPerPage);
  }, [sortedData, currentPage, itemsPerPage, pagination]);

  // Handle sort
  const handleSort = (key: string) => {
    const newSort: DataTableSort = {
      key,
      direction: sort?.key === key && sort.direction === 'asc' ? 'desc' : 'asc'
    };
    setSort(newSort);
    onSortChange?.(newSort);
  };

  // Handle selection
  const handleSelectAll = (checked: boolean) => {
    const newSelection = checked ? [...paginatedData] : [];
    setSelectedItems(newSelection);
    onSelectionChange?.(newSelection);
  };

  const handleSelectItem = (item: T, checked: boolean) => {
    const newSelection = checked
      ? [...selectedItems, item]
      : selectedItems.filter(selected => selected !== item);
    setSelectedItems(newSelection);
    onSelectionChange?.(newSelection);
  };

  // Handle export
  const handleExport = () => {
    if (onExport) {
      onExport(sortedData);
    } else {
      // Default CSV export
      const csvContent = [
        columns.map(col => col.header).join(','),
        ...sortedData.map(item =>
          columns.map(col => {
            const value = col.accessor(item);
            return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
          }).join(',')
        )
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'data-export.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loading variant="spinner" size="lg" text="Loading data..." />
      </div>
    );
  }

  if (error) {
    return (
      <Card variant="outlined" className="text-center py-12">
        <CardBody>
          <div className="text-error-500 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-secondary-900 mb-2">Error Loading Data</h3>
          <p className="text-secondary-600">{error}</p>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      {(title || subtitle || actions || onExport) && (
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              {title && <CardTitle>{title}</CardTitle>}
              {subtitle && <p className="text-sm text-secondary-600 mt-1">{subtitle}</p>}
            </div>
            
            <div className="flex items-center space-x-2">
              {actions}
              {onExport && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleExport}
                  leftIcon={
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  }
                >
                  Export
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
      )}

      {/* Search and Filters */}
      {(searchable || filterable) && (
        <div className="flex items-center space-x-4">
          {searchable && (
            <div className="flex-1 max-w-md">
              <Input
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                leftIcon={
                  <svg className="w-4 h-4 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                }
              />
            </div>
          )}
          
          {filterable && (
            <Button variant="outline" size="sm">
              Filters ({filters.length})
            </Button>
          )}
        </div>
      )}

      {/* Table */}
      <Card>
        <Table variant="striped" size="md">
          <TableHeader>
            <TableRow>
              {selectable && (
                <TableHeaderCell width="40px">
                  <input
                    type="checkbox"
                    checked={selectedItems.length === paginatedData.length && paginatedData.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                  />
                </TableHeaderCell>
              )}
              
              {columns.map(column => (
                <TableHeaderCell
                  key={column.key}
                  sortable={sortable && column.sortable}
                  sortDirection={sort?.key === column.key ? sort.direction : null}
                  onSort={sortable && column.sortable ? () => handleSort(column.key) : undefined}
                  style={{ width: column.width }}
                >
                  {column.header}
                </TableHeaderCell>
              ))}
            </TableRow>
          </TableHeader>
          
          <TableBody>
            {paginatedData.length > 0 ? (
              paginatedData.map((item, index) => (
                <TableRow
                  key={index}
                  onClick={onRowClick ? () => onRowClick(item) : undefined}
                  hoverable={!!onRowClick}
                >
                  {selectable && (
                    <TableCell>
                      <input
                        type="checkbox"
                        checked={selectedItems.includes(item)}
                        onChange={(e) => handleSelectItem(item, e.target.checked)}
                        className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                        onClick={(e) => e.stopPropagation()}
                      />
                    </TableCell>
                  )}
                  
                  {columns.map(column => (
                    <TableCell key={column.key}>
                      {column.render
                        ? column.render(column.accessor(item), item)
                        : column.accessor(item)
                      }
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length + (selectable ? 1 : 0)} className="text-center py-8">
                  <div className="text-secondary-500">
                    No data found
                  </div>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Pagination */}
      {pagination && (
        <TablePagination
          currentPage={currentPage}
          totalPages={Math.ceil(sortedData.length / itemsPerPage)}
          totalItems={sortedData.length}
          itemsPerPage={itemsPerPage}
          onPageChange={setCurrentPage}
          onItemsPerPageChange={setItemsPerPage}
          itemsPerPageOptions={pageSizeOptions}
        />
      )}
    </div>
  );
};

// DataTable Hook
export const useDataTable = <T extends Record<string, any>>(initialData: T[]) => {
  const [data, setData] = useState<T[]>(initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshData = async (fetchFunction: () => Promise<T[]>) => {
    setLoading(true);
    setError(null);
    
    try {
      const newData = await fetchFunction();
      setData(newData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const addItem = (item: T) => {
    setData(prev => [...prev, item]);
  };

  const updateItem = (id: string, updates: Partial<T>) => {
    setData(prev => prev.map(item => 
      (item as any).id === id ? { ...item, ...updates } : item
    ));
  };

  const removeItem = (id: string) => {
    setData(prev => prev.filter(item => (item as any).id !== id));
  };

  return {
    data,
    loading,
    error,
    refreshData,
    addItem,
    updateItem,
    removeItem,
    setLoading,
    setError
  };
}; 
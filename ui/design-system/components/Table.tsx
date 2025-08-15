import React, { forwardRef } from 'react';

export type TableVariant = 'default' | 'striped' | 'bordered' | 'compact';

export type TableSize = 'sm' | 'md' | 'lg';

export interface TableProps extends React.TableHTMLAttributes<HTMLTableElement> {
  variant?: TableVariant;
  size?: TableSize;
  children: React.ReactNode;
}

const getTableClasses = (
  variant: TableVariant = 'default',
  size: TableSize = 'md'
): string => {
  const baseClasses = [
    'w-full border-collapse',
    'text-left'
  ];

  const variantClasses = {
    default: [
      'bg-white',
      'border border-secondary-200'
    ],
    striped: [
      'bg-white',
      'border border-secondary-200',
      '[&>tbody>tr:nth-child(odd)]:bg-secondary-50'
    ],
    bordered: [
      'bg-white',
      'border border-secondary-200',
      '[&>thead>tr>th]:border-r [&>thead>tr>th]:border-secondary-200',
      '[&>tbody>tr>td]:border-r [&>tbody>tr>td]:border-secondary-200',
      '[&>tbody>tr]:border-b [&>tbody>tr]:border-secondary-200'
    ],
    compact: [
      'bg-white',
      'border border-secondary-200'
    ]
  };

  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return [
    ...baseClasses,
    ...variantClasses[variant],
    sizeClasses[size]
  ].join(' ');
};

export const Table = forwardRef<HTMLTableElement, TableProps>(
  (
    {
      variant = 'default',
      size = 'md',
      children,
      className = '',
      ...props
    },
    ref
  ) => {
    const tableClasses = getTableClasses(variant, size);

    return (
      <div className="overflow-x-auto">
        <table
          ref={ref}
          className={`${tableClasses} ${className}`}
          {...props}
        >
          {children}
        </table>
      </div>
    );
  }
);

Table.displayName = 'Table';

// Table Header Component
interface TableHeaderProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  children: React.ReactNode;
}

export const TableHeader: React.FC<TableHeaderProps> = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <thead
      className={`bg-secondary-50 ${className}`}
      {...props}
    >
      {children}
    </thead>
  );
};

// Table Body Component
interface TableBodyProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  children: React.ReactNode;
}

export const TableBody: React.FC<TableBodyProps> = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <tbody
      className={`bg-white ${className}`}
      {...props}
    >
      {children}
    </tbody>
  );
};

// Table Footer Component
interface TableFooterProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  children: React.ReactNode;
}

export const TableFooter: React.FC<TableFooterProps> = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <tfoot
      className={`bg-secondary-50 ${className}`}
      {...props}
    >
      {children}
    </tfoot>
  );
};

// Table Row Component
interface TableRowProps extends React.HTMLAttributes<HTMLTableRowElement> {
  children: React.ReactNode;
  selected?: boolean;
  hoverable?: boolean;
  onClick?: () => void;
}

export const TableRow: React.FC<TableRowProps> = ({
  children,
  selected = false,
  hoverable = true,
  onClick,
  className = '',
  ...props
}) => {
  const rowClasses = [
    hoverable ? 'hover:bg-secondary-100' : '',
    selected ? 'bg-primary-50 border-primary-200' : '',
    onClick ? 'cursor-pointer' : ''
  ].filter(Boolean).join(' ');

  return (
    <tr
      className={`${rowClasses} ${className}`}
      onClick={onClick}
      {...props}
    >
      {children}
    </tr>
  );
};

// Table Header Cell Component
interface TableHeaderCellProps extends React.ThHTMLAttributes<HTMLTableCellElement> {
  children: React.ReactNode;
  sortable?: boolean;
  sortDirection?: 'asc' | 'desc' | null;
  onSort?: () => void;
}

export const TableHeaderCell: React.FC<TableHeaderCellProps> = ({
  children,
  sortable = false,
  sortDirection = null,
  onSort,
  className = '',
  ...props
}) => {
  const sortClasses = sortable ? 'cursor-pointer select-none' : '';
  const sortIcon = sortable && (
    <span className="ml-1">
      {sortDirection === 'asc' && '↑'}
      {sortDirection === 'desc' && '↓'}
      {!sortDirection && '↕'}
    </span>
  );

  return (
    <th
      className={`px-4 py-3 font-semibold text-secondary-900 ${sortClasses} ${className}`}
      onClick={sortable ? onSort : undefined}
      {...props}
    >
      <div className="flex items-center">
        {children}
        {sortIcon}
      </div>
    </th>
  );
};

// Table Cell Component
interface TableCellProps extends React.TdHTMLAttributes<HTMLTableCellElement> {
  children: React.ReactNode;
  align?: 'left' | 'center' | 'right';
}

export const TableCell: React.FC<TableCellProps> = ({
  children,
  align = 'left',
  className = '',
  ...props
}) => {
  const alignClasses = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right'
  };

  return (
    <td
      className={`px-4 py-3 text-secondary-700 ${alignClasses[align]} ${className}`}
      {...props}
    >
      {children}
    </td>
  );
};

// Table Empty State Component
interface TableEmptyStateProps {
  message?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export const TableEmptyState: React.FC<TableEmptyStateProps> = ({
  message = 'No data available',
  icon,
  action
}) => {
  return (
    <tr>
      <td colSpan={100} className="px-4 py-12 text-center">
        <div className="flex flex-col items-center space-y-3">
          {icon && (
            <div className="text-secondary-400">
              {icon}
            </div>
          )}
          <p className="text-secondary-600">{message}</p>
          {action && (
            <div>
              {action}
            </div>
          )}
        </div>
      </td>
    </tr>
  );
};

// Table Loading State Component
interface TableLoadingStateProps {
  columns?: number;
  rows?: number;
}

export const TableLoadingState: React.FC<TableLoadingStateProps> = ({
  columns = 5,
  rows = 3
}) => {
  return (
    <>
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <tr key={rowIndex}>
          {Array.from({ length: columns }).map((_, colIndex) => (
            <td key={colIndex} className="px-4 py-3">
              <div className="h-4 bg-secondary-200 rounded animate-pulse" />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
};

// Table Pagination Component
interface TablePaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
  onPageChange: (page: number) => void;
  onItemsPerPageChange?: (itemsPerPage: number) => void;
  showItemsPerPage?: boolean;
  itemsPerPageOptions?: number[];
}

export const TablePagination: React.FC<TablePaginationProps> = ({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage,
  onPageChange,
  onItemsPerPageChange,
  showItemsPerPage = true,
  itemsPerPageOptions = [10, 25, 50, 100]
}) => {
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  return (
    <div className="flex items-center justify-between px-4 py-3 bg-white border-t border-secondary-200">
      <div className="flex items-center space-x-4">
        <span className="text-sm text-secondary-700">
          Showing {startItem} to {endItem} of {totalItems} results
        </span>
        
        {showItemsPerPage && onItemsPerPageChange && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-secondary-700">Show:</span>
            <select
              value={itemsPerPage}
              onChange={(e) => onItemsPerPageChange(Number(e.target.value))}
              className="px-2 py-1 text-sm border border-secondary-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {itemsPerPageOptions.map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="flex items-center space-x-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="px-3 py-1 text-sm text-secondary-700 bg-white border border-secondary-300 rounded hover:bg-secondary-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        
        {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
          <button
            key={page}
            onClick={() => onPageChange(page)}
            className={`px-3 py-1 text-sm rounded ${
              page === currentPage
                ? 'bg-primary-600 text-white'
                : 'text-secondary-700 bg-white border border-secondary-300 hover:bg-secondary-50'
            }`}
          >
            {page}
          </button>
        ))}
        
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="px-3 py-1 text-sm text-secondary-700 bg-white border border-secondary-300 rounded hover:bg-secondary-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    </div>
  );
}; 
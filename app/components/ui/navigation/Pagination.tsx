import React from 'react';
import { ChevronLeftIcon, ChevronRightIcon, EllipsisHorizontalIcon } from '../icons/SimpleIcons';

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems?: number;
  itemsPerPage?: number;
  onPageChange: (page: number) => void;
  showFirstLast?: boolean;
  showPageNumbers?: boolean;
  maxVisiblePages?: number;
  className?: string;
  'aria-label'?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage,
  onPageChange,
  showFirstLast = true,
  showPageNumbers = true,
  maxVisiblePages = 5,
  className = '',
  'aria-label': ariaLabel = 'Pagination navigation'
}) => {
  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      onPageChange(page);
    }
  };

  const getVisiblePages = () => {
    if (totalPages <= maxVisiblePages) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    const halfVisible = Math.floor(maxVisiblePages / 2);
    let start = Math.max(1, currentPage - halfVisible);
    let end = Math.min(totalPages, start + maxVisiblePages - 1);

    if (end - start + 1 < maxVisiblePages) {
      start = Math.max(1, end - maxVisiblePages + 1);
    }

    const pages = [];
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }

    return pages;
  };

  const visiblePages = getVisiblePages();
  const hasPrevious = currentPage > 1;
  const hasNext = currentPage < totalPages;

  const getPageInfo = () => {
    if (!totalItems || !itemsPerPage) return null;
    
    const start = (currentPage - 1) * itemsPerPage + 1;
    const end = Math.min(currentPage * itemsPerPage, totalItems);
    
    return `${start}-${end} de ${totalItems}`;
  };

  const renderPageButton = (page: number, isCurrent = false) => (
    <button
      key={page}
      onClick={() => handlePageChange(page)}
      className={`relative inline-flex items-center px-4 py-2 text-sm font-medium border ${
        isCurrent
          ? 'z-10 bg-blue-600 border-blue-600 text-white'
          : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
      } focus:z-20 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200`}
      aria-current={isCurrent ? 'page' : undefined}
      aria-label={isCurrent ? `Página ${page}, página atual` : `Ir para página ${page}`}
    >
      {page}
    </button>
  );

  const renderEllipsis = (key: string) => (
    <span
      key={key}
      className="relative inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300"
      aria-hidden="true"
    >
      <EllipsisHorizontalIcon className="h-5 w-5" />
    </span>
  );

  return (
    <div className={`flex items-center justify-between ${className}`}>
      {/* Informações da página */}
      {getPageInfo() && (
        <div className="flex-1 flex justify-start">
          <p className="text-sm text-gray-700">
            Mostrando <span className="font-medium">{getPageInfo()}</span>
          </p>
        </div>
      )}

      {/* Navegação */}
      <nav
        className="relative z-0 inline-flex shadow-sm -space-x-px"
        aria-label={ariaLabel}
      >
        {/* Botão Primeira Página */}
        {showFirstLast && hasPrevious && (
          <button
            onClick={() => handlePageChange(1)}
            className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200"
            aria-label="Ir para primeira página"
          >
            <span className="sr-only">Primeira</span>
            <ChevronLeftIcon className="h-5 w-5" />
            <ChevronLeftIcon className="h-5 w-5 -ml-1" />
          </button>
        )}

        {/* Botão Anterior */}
        {hasPrevious && (
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            className={`relative inline-flex items-center px-2 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200 ${
              !showFirstLast ? 'rounded-l-md' : ''
            }`}
            aria-label="Ir para página anterior"
          >
            <span className="sr-only">Anterior</span>
            <ChevronLeftIcon className="h-5 w-5" />
          </button>
        )}

        {/* Números das Páginas */}
        {showPageNumbers && (
          <>
            {/* Primeira página se não visível */}
            {visiblePages[0] > 1 && (
              <>
                {renderPageButton(1)}
                {visiblePages[0] > 2 && renderEllipsis('start-ellipsis')}
              </>
            )}

            {/* Páginas visíveis */}
            {visiblePages.map(page => renderPageButton(page, page === currentPage))}

            {/* Última página se não visível */}
            {visiblePages[visiblePages.length - 1] < totalPages && (
              <>
                {visiblePages[visiblePages.length - 1] < totalPages - 1 && 
                  renderEllipsis('end-ellipsis')}
                {renderPageButton(totalPages)}
              </>
            )}
          </>
        )}

        {/* Botão Próximo */}
        {hasNext && (
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            className={`relative inline-flex items-center px-2 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200 ${
              !showFirstLast ? 'rounded-r-md' : ''
            }`}
            aria-label="Ir para próxima página"
          >
            <span className="sr-only">Próximo</span>
            <ChevronRightIcon className="h-5 w-5" />
          </button>
        )}

        {/* Botão Última Página */}
        {showFirstLast && hasNext && (
          <button
            onClick={() => handlePageChange(totalPages)}
            className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 focus:z-20 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200"
            aria-label="Ir para última página"
          >
            <span className="sr-only">Última</span>
            <ChevronRightIcon className="h-5 w-5" />
            <ChevronRightIcon className="h-5 w-5 -ml-1" />
          </button>
        )}
      </nav>
    </div>
  );
};

export default Pagination; 
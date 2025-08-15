import React from 'react';
import { ChevronRightIcon, HomeIcon } from '../icons/SimpleIcons';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ComponentType<{ className?: string }>;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  separator?: React.ComponentType<{ className?: string }>;
  showHome?: boolean;
  homeHref?: string;
  className?: string;
  'aria-label'?: string;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({
  items,
  separator = ChevronRightIcon,
  showHome = true,
  homeHref = '/',
  className = '',
  'aria-label': ariaLabel = 'Breadcrumb navigation'
}) => {
  const Separator = separator;
  
  const allItems = showHome 
    ? [{ label: 'Home', href: homeHref, icon: HomeIcon }, ...items]
    : items;

  return (
    <nav 
      aria-label={ariaLabel}
      className={`flex items-center space-x-2 text-sm ${className}`}
    >
      <ol className="flex items-center space-x-2">
        {allItems.map((item, index) => {
          const isLast = index === allItems.length - 1;
          const isLink = item.href && !isLast;
          
          const ItemIcon = item.icon;
          
          return (
            <li key={index} className="flex items-center">
              {index > 0 && (
                <Separator 
                  className="h-4 w-4 text-gray-400 mx-2" 
                  aria-hidden="true"
                />
              )}
              
              {isLink ? (
                <a
                  href={item.href}
                  className="flex items-center text-gray-600 hover:text-gray-900 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
                  aria-current={isLast ? 'page' : undefined}
                >
                  {ItemIcon && (
                    <ItemIcon className="h-4 w-4 mr-1" aria-hidden="true" />
                  )}
                  <span>{item.label}</span>
                </a>
              ) : (
                <span 
                  className="flex items-center text-gray-900 font-medium"
                  aria-current="page"
                >
                  {ItemIcon && (
                    <ItemIcon className="h-4 w-4 mr-1" aria-hidden="true" />
                  )}
                  <span>{item.label}</span>
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumb; 
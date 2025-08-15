import React, { forwardRef, useState } from 'react';

export type NavigationVariant = 'horizontal' | 'vertical' | 'tabs' | 'pills';

export type NavigationSize = 'sm' | 'md' | 'lg';

export interface NavigationProps extends React.HTMLAttributes<HTMLElement> {
  variant?: NavigationVariant;
  size?: NavigationSize;
  children: React.ReactNode;
}

const getNavigationClasses = (
  variant: NavigationVariant = 'horizontal',
  size: NavigationSize = 'md'
): string => {
  const baseClasses = [
    'flex items-center'
  ];

  const variantClasses = {
    horizontal: 'space-x-8',
    vertical: 'flex-col space-y-2',
    tabs: 'border-b border-secondary-200 space-x-8',
    pills: 'space-x-2'
  };

  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return [
    ...baseClasses,
    variantClasses[variant],
    sizeClasses[size]
  ].join(' ');
};

export const Navigation = forwardRef<HTMLElement, NavigationProps>(
  (
    {
      variant = 'horizontal',
      size = 'md',
      children,
      className = '',
      ...props
    },
    ref
  ) => {
    const navigationClasses = getNavigationClasses(variant, size);
    const Element = variant === 'vertical' ? 'nav' : 'nav';

    return (
      <Element
        ref={ref}
        className={`${navigationClasses} ${className}`}
        role="navigation"
        {...props}
      >
        {children}
      </Element>
    );
  }
);

Navigation.displayName = 'Navigation';

// Navigation Item Component
interface NavigationItemProps extends React.HTMLAttributes<HTMLLIElement> {
  children: React.ReactNode;
  active?: boolean;
  disabled?: boolean;
  href?: string;
  onClick?: () => void;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
}

export const NavigationItem: React.FC<NavigationItemProps> = ({
  children,
  active = false,
  disabled = false,
  href,
  onClick,
  icon,
  badge,
  className = '',
  ...props
}) => {
  const baseClasses = [
    'flex items-center space-x-2 px-3 py-2 rounded-md transition-colors duration-200',
    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
  ];

  const stateClasses = active
    ? 'bg-primary-100 text-primary-700 border-primary-200'
    : 'text-secondary-700 hover:bg-secondary-100 hover:text-secondary-900';

  const disabledClasses = disabled
    ? 'opacity-50 cursor-not-allowed pointer-events-none'
    : 'cursor-pointer';

  const itemClasses = [
    ...baseClasses,
    stateClasses,
    disabledClasses,
    className
  ].join(' ');

  const content = (
    <>
      {icon && <span className="flex-shrink-0">{icon}</span>}
      <span className="flex-1">{children}</span>
      {badge && <span className="flex-shrink-0">{badge}</span>}
    </>
  );

  if (href && !disabled) {
    return (
      <li {...props}>
        <a href={href} className={itemClasses}>
          {content}
        </a>
      </li>
    );
  }

  return (
    <li {...props}>
      <button
        type="button"
        className={itemClasses}
        onClick={onClick}
        disabled={disabled}
      >
        {content}
      </button>
    </li>
  );
};

// Navigation Group Component
interface NavigationGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  title?: string;
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

export const NavigationGroup: React.FC<NavigationGroupProps> = ({
  children,
  title,
  collapsible = false,
  defaultExpanded = true,
  className = '',
  ...props
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className={`space-y-2 ${className}`} {...props}>
      {title && (
        <div
          className={`flex items-center justify-between px-3 py-2 ${
            collapsible ? 'cursor-pointer' : ''
          }`}
          onClick={collapsible ? () => setIsExpanded(!isExpanded) : undefined}
        >
          <h3 className="text-xs font-semibold text-secondary-500 uppercase tracking-wider">
            {title}
          </h3>
          
          {collapsible && (
            <svg
              className={`w-4 h-4 text-secondary-400 transition-transform ${
                isExpanded ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          )}
        </div>
      )}
      
      {(!collapsible || isExpanded) && (
        <ul className="space-y-1">
          {children}
        </ul>
      )}
    </div>
  );
};

// Breadcrumb Component
interface BreadcrumbProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode;
  separator?: React.ReactNode;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({
  children,
  separator = '/',
  className = '',
  ...props
}) => {
  return (
    <nav
      className={`flex items-center space-x-2 ${className}`}
      aria-label="Breadcrumb"
      {...props}
    >
      {React.Children.map(children, (child, index) => (
        <React.Fragment key={index}>
          {child}
          {index < React.Children.count(children) - 1 && (
            <span className="text-secondary-400">{separator}</span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

// Breadcrumb Item Component
interface BreadcrumbItemProps {
  children: React.ReactNode;
  href?: string;
  current?: boolean;
}

export const BreadcrumbItem: React.FC<BreadcrumbItemProps> = ({
  children,
  href,
  current = false
}) => {
  const classes = current
    ? 'text-secondary-500 cursor-default'
    : 'text-secondary-700 hover:text-secondary-900';

  if (current) {
    return (
      <span className={classes} aria-current="page">
        {children}
      </span>
    );
  }

  if (href) {
    return (
      <a href={href} className={classes}>
        {children}
      </a>
    );
  }

  return (
    <span className={classes}>
      {children}
    </span>
  );
};

// Pagination Component
interface PaginationProps extends React.HTMLAttributes<HTMLElement> {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  showFirstLast?: boolean;
  showPrevNext?: boolean;
  size?: NavigationSize;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  showFirstLast = true,
  showPrevNext = true,
  size = 'md',
  className = '',
  ...props
}) => {
  const sizeClasses = {
    sm: 'px-2 py-1 text-sm',
    md: 'px-3 py-2 text-base',
    lg: 'px-4 py-3 text-lg'
  };

  const buttonClasses = (active: boolean) => [
    'flex items-center justify-center rounded-md transition-colors duration-200',
    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
    sizeClasses[size],
    active
      ? 'bg-primary-600 text-white'
      : 'text-secondary-700 bg-white border border-secondary-300 hover:bg-secondary-50'
  ].join(' ');

  const getVisiblePages = () => {
    const delta = 2;
    const range = [];
    const rangeWithDots = [];

    for (
      let i = Math.max(2, currentPage - delta);
      i <= Math.min(totalPages - 1, currentPage + delta);
      i++
    ) {
      range.push(i);
    }

    if (currentPage - delta > 2) {
      rangeWithDots.push(1, '...');
    } else {
      rangeWithDots.push(1);
    }

    rangeWithDots.push(...range);

    if (currentPage + delta < totalPages - 1) {
      rangeWithDots.push('...', totalPages);
    } else {
      rangeWithDots.push(totalPages);
    }

    return rangeWithDots;
  };

  return (
    <nav
      className={`flex items-center justify-center space-x-1 ${className}`}
      aria-label="Pagination"
      {...props}
    >
      {showFirstLast && currentPage > 1 && (
        <button
          onClick={() => onPageChange(1)}
          className={buttonClasses(false)}
          aria-label="Go to first page"
        >
          «
        </button>
      )}
      
      {showPrevNext && currentPage > 1 && (
        <button
          onClick={() => onPageChange(currentPage - 1)}
          className={buttonClasses(false)}
          aria-label="Go to previous page"
        >
          ‹
        </button>
      )}
      
      {getVisiblePages().map((page, index) => (
        <React.Fragment key={index}>
          {page === '...' ? (
            <span className="px-3 py-2 text-secondary-500">...</span>
          ) : (
            <button
              onClick={() => onPageChange(page as number)}
              className={buttonClasses(page === currentPage)}
              aria-label={`Go to page ${page}`}
              aria-current={page === currentPage ? 'page' : undefined}
            >
              {page}
            </button>
          )}
        </React.Fragment>
      ))}
      
      {showPrevNext && currentPage < totalPages && (
        <button
          onClick={() => onPageChange(currentPage + 1)}
          className={buttonClasses(false)}
          aria-label="Go to next page"
        >
          ›
        </button>
      )}
      
      {showFirstLast && currentPage < totalPages && (
        <button
          onClick={() => onPageChange(totalPages)}
          className={buttonClasses(false)}
          aria-label="Go to last page"
        >
          »
        </button>
      )}
    </nav>
  );
};

// Tabs Component
interface TabsProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  value?: string;
  onChange?: (value: string) => void;
  variant?: 'default' | 'pills' | 'underline';
  size?: NavigationSize;
}

export const Tabs: React.FC<TabsProps> = ({
  children,
  value,
  onChange,
  variant = 'default',
  size = 'md',
  className = '',
  ...props
}) => {
  const variantClasses = {
    default: 'border-b border-secondary-200',
    pills: 'space-x-1',
    underline: 'border-b border-secondary-200'
  };

  return (
    <div className={`${variantClasses[variant]} ${className}`} {...props}>
      <Navigation variant="horizontal" size={size}>
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child)) {
            return React.cloneElement(child, {
              active: child.props.value === value,
              onClick: () => onChange?.(child.props.value)
            });
          }
          return child;
        })}
      </Navigation>
    </div>
  );
};

// Tab Component
interface TabProps extends Omit<NavigationItemProps, 'active'> {
  value: string;
  label: string;
}

export const Tab: React.FC<TabProps> = ({ value, label, ...props }) => {
  return (
    <NavigationItem {...props}>
      {label}
    </NavigationItem>
  );
}; 
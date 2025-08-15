import React, { useState, useEffect } from 'react';
import { Button } from '../../../ui/design-system/components/Button';
import { Card } from '../../../ui/design-system/components/Card';
import { Loading } from '../../../ui/design-system/components/Loading';
import { Tooltip } from '../../../ui/design-system/components/Tooltip';

export interface NavigationItem {
  id: string;
  label: string;
  href?: string;
  icon?: React.ReactNode;
  badge?: string | number;
  children?: NavigationItem[];
  disabled?: boolean;
  external?: boolean;
  onClick?: () => void;
}

export interface NavigationSection {
  id: string;
  title?: string;
  items: NavigationItem[];
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

export interface Navigation_v2Props {
  items?: NavigationItem[];
  sections?: NavigationSection[];
  variant?: 'horizontal' | 'vertical' | 'sidebar' | 'breadcrumb';
  size?: 'sm' | 'md' | 'lg';
  activeItem?: string;
  onItemClick?: (item: NavigationItem) => void;
  showIcons?: boolean;
  showBadges?: boolean;
  collapsible?: boolean;
  searchable?: boolean;
  loading?: boolean;
  className?: string;
}

const NavigationItemComponent: React.FC<{
  item: NavigationItem;
  active?: boolean;
  variant: string;
  size: string;
  showIcons: boolean;
  showBadges: boolean;
  onClick?: (item: NavigationItem) => void;
}> = ({ item, active, variant, size, showIcons, showBadges, onClick }) => {
  const baseClasses = [
    'flex items-center justify-between px-3 py-2 rounded-md transition-colors duration-200',
    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
  ];

  const stateClasses = active
    ? 'bg-primary-100 text-primary-700 border-primary-200'
    : 'text-secondary-700 hover:bg-secondary-100 hover:text-secondary-900';

  const disabledClasses = item.disabled
    ? 'opacity-50 cursor-not-allowed pointer-events-none'
    : 'cursor-pointer';

  const itemClasses = [
    ...baseClasses,
    stateClasses,
    disabledClasses
  ].join(' ');

  const handleClick = () => {
    if (!item.disabled && onClick) {
      onClick(item);
    }
  };

  const content = (
    <>
      <div className="flex items-center space-x-3">
        {showIcons && item.icon && (
          <span className="flex-shrink-0">{item.icon}</span>
        )}
        <span className="flex-1">{item.label}</span>
      </div>
      
      {showBadges && item.badge && (
        <span className="flex-shrink-0 ml-2 px-2 py-1 text-xs font-medium bg-primary-100 text-primary-800 rounded-full">
          {item.badge}
        </span>
      )}
      
      {item.external && (
        <svg className="w-4 h-4 ml-2 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
        </svg>
      )}
    </>
  );

  if (item.href && !item.disabled) {
    return (
      <a
        href={item.href}
        target={item.external ? '_blank' : undefined}
        rel={item.external ? 'noopener noreferrer' : undefined}
        className={itemClasses}
        onClick={handleClick}
      >
        {content}
      </a>
    );
  }

  return (
    <button
      type="button"
      className={itemClasses}
      onClick={handleClick}
      disabled={item.disabled}
    >
      {content}
    </button>
  );
};

const NavigationSectionComponent: React.FC<{
  section: NavigationSection;
  variant: string;
  size: string;
  showIcons: boolean;
  showBadges: boolean;
  activeItem?: string;
  onItemClick?: (item: NavigationItem) => void;
}> = ({ section, variant, size, showIcons, showBadges, activeItem, onItemClick }) => {
  const [isExpanded, setIsExpanded] = useState(section.defaultExpanded ?? true);

  return (
    <div className="space-y-2">
      {section.title && (
        <div
          className={`flex items-center justify-between px-3 py-2 ${
            section.collapsible ? 'cursor-pointer' : ''
          }`}
          onClick={section.collapsible ? () => setIsExpanded(!isExpanded) : undefined}
        >
          <h3 className="text-xs font-semibold text-secondary-500 uppercase tracking-wider">
            {section.title}
          </h3>
          
          {section.collapsible && (
            <svg
              className={`w-4 h-4 text-secondary-400 transition-transform ${
                isExpanded ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          )}
        </div>
      )}
      
      {(!section.collapsible || isExpanded) && (
        <div className="space-y-1">
          {section.items.map(item => (
            <NavigationItemComponent
              key={item.id}
              item={item}
              active={activeItem === item.id}
              variant={variant}
              size={size}
              showIcons={showIcons}
              showBadges={showBadges}
              onClick={onItemClick}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const Navigation_v2: React.FC<Navigation_v2Props> = ({
  items = [],
  sections = [],
  variant = 'horizontal',
  size = 'md',
  activeItem,
  onItemClick,
  showIcons = true,
  showBadges = true,
  collapsible = false,
  searchable = false,
  loading = false,
  className = ''
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isCollapsed, setIsCollapsed] = useState(false);

  const filteredItems = items.filter(item =>
    searchTerm === '' || item.label.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredSections = sections.map(section => ({
    ...section,
    items: section.items.filter(item =>
      searchTerm === '' || item.label.toLowerCase().includes(searchTerm.toLowerCase())
    )
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-32">
        <Loading variant="spinner" size="md" text="Loading navigation..." />
      </div>
    );
  }

  const renderHorizontalNavigation = () => (
    <nav className="flex items-center space-x-8">
      {filteredItems.map(item => (
        <NavigationItemComponent
          key={item.id}
          item={item}
          active={activeItem === item.id}
          variant={variant}
          size={size}
          showIcons={showIcons}
          showBadges={showBadges}
          onClick={onItemClick}
        />
      ))}
    </nav>
  );

  const renderVerticalNavigation = () => (
    <nav className="space-y-2">
      {filteredItems.map(item => (
        <NavigationItemComponent
          key={item.id}
          item={item}
          active={activeItem === item.id}
          variant={variant}
          size={size}
          showIcons={showIcons}
          showBadges={showBadges}
          onClick={onItemClick}
        />
      ))}
    </nav>
  );

  const renderSidebarNavigation = () => (
    <div className="h-full flex flex-col">
      {searchable && (
        <div className="p-4 border-b border-secondary-200">
          <input
            type="text"
            placeholder="Search navigation..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      )}
      
      <div className="flex-1 overflow-y-auto p-4">
        {filteredSections.length > 0 ? (
          <div className="space-y-6">
            {filteredSections.map(section => (
              <NavigationSectionComponent
                key={section.id}
                section={section}
                variant={variant}
                size={size}
                showIcons={showIcons}
                showBadges={showBadges}
                activeItem={activeItem}
                onItemClick={onItemClick}
              />
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {filteredItems.map(item => (
              <NavigationItemComponent
                key={item.id}
                item={item}
                active={activeItem === item.id}
                variant={variant}
                size={size}
                showIcons={showIcons}
                showBadges={showBadges}
                onClick={onItemClick}
              />
            ))}
          </div>
        )}
      </div>
      
      {collapsible && (
        <div className="p-4 border-t border-secondary-200">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="w-full"
          >
            {isCollapsed ? 'Expand' : 'Collapse'}
          </Button>
        </div>
      )}
    </div>
  );

  const renderBreadcrumbNavigation = () => {
    const findBreadcrumbPath = (items: NavigationItem[], targetId: string): NavigationItem[] => {
      for (const item of items) {
        if (item.id === targetId) {
          return [item];
        }
        if (item.children) {
          const path = findBreadcrumbPath(item.children, targetId);
          if (path.length > 0) {
            return [item, ...path];
          }
        }
      }
      return [];
    };

    const breadcrumbPath = activeItem ? findBreadcrumbPath(items, activeItem) : [];

    return (
      <nav className="flex items-center space-x-2" aria-label="Breadcrumb">
        {breadcrumbPath.map((item, index) => (
          <React.Fragment key={item.id}>
            {index > 0 && (
              <svg className="w-4 h-4 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            )}
            <NavigationItemComponent
              item={item}
              active={index === breadcrumbPath.length - 1}
              variant={variant}
              size={size}
              showIcons={showIcons}
              showBadges={showBadges}
              onClick={onItemClick}
            />
          </React.Fragment>
        ))}
      </nav>
    );
  };

  const renderContent = () => {
    switch (variant) {
      case 'horizontal':
        return renderHorizontalNavigation();
      case 'vertical':
        return renderVerticalNavigation();
      case 'sidebar':
        return renderSidebarNavigation();
      case 'breadcrumb':
        return renderBreadcrumbNavigation();
      default:
        return renderHorizontalNavigation();
    }
  };

  return (
    <div className={`${className} ${isCollapsed ? 'w-16' : ''}`}>
      {renderContent()}
    </div>
  );
};

// Navigation Hook
export const useNavigation = () => {
  const [activeItem, setActiveItem] = useState<string>('');
  const [navigationHistory, setNavigationHistory] = useState<string[]>([]);

  const navigateTo = (itemId: string) => {
    setActiveItem(itemId);
    setNavigationHistory(prev => [...prev, itemId]);
  };

  const goBack = () => {
    if (navigationHistory.length > 1) {
      const newHistory = navigationHistory.slice(0, -1);
      setNavigationHistory(newHistory);
      setActiveItem(newHistory[newHistory.length - 1]);
    }
  };

  const goForward = () => {
    // Implementation for forward navigation
  };

  return {
    activeItem,
    navigationHistory,
    navigateTo,
    goBack,
    goForward
  };
}; 
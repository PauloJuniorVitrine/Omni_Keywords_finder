import React, { useState, useEffect } from 'react';
import { Card } from '../../../ui/design-system/components/Card';
import { Button } from '../../../ui/design-system/components/Button';
import { Loading } from '../../../ui/design-system/components/Loading';
import { Tooltip } from '../../../ui/design-system/components/Tooltip';

export interface SidebarItem {
  id: string;
  label: string;
  href?: string;
  icon?: React.ReactNode;
  badge?: string | number;
  children?: SidebarItem[];
  disabled?: boolean;
  external?: boolean;
  onClick?: () => void;
}

export interface SidebarSection {
  id: string;
  title?: string;
  items: SidebarItem[];
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

export interface Sidebar_v2Props {
  items?: SidebarItem[];
  sections?: SidebarSection[];
  variant?: 'default' | 'compact' | 'floating';
  size?: 'sm' | 'md' | 'lg';
  width?: string;
  collapsed?: boolean;
  collapsible?: boolean;
  onCollapse?: (collapsed: boolean) => void;
  activeItem?: string;
  onItemClick?: (item: SidebarItem) => void;
  showIcons?: boolean;
  showBadges?: boolean;
  searchable?: boolean;
  loading?: boolean;
  className?: string;
}

const SidebarItemComponent: React.FC<{
  item: SidebarItem;
  active?: boolean;
  collapsed?: boolean;
  variant: string;
  size: string;
  showIcons: boolean;
  showBadges: boolean;
  onClick?: (item: SidebarItem) => void;
}> = ({ item, active, collapsed, variant, size, showIcons, showBadges, onClick }) => {
  const baseClasses = [
    'flex items-center justify-between px-3 py-2 rounded-md transition-colors duration-200',
    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
    'w-full text-left'
  ];

  const stateClasses = active
    ? 'bg-primary-100 text-primary-700 border-primary-200'
    : 'text-secondary-700 hover:bg-secondary-100 hover:text-secondary-900';

  const disabledClasses = item.disabled
    ? 'opacity-50 cursor-not-allowed pointer-events-none'
    : 'cursor-pointer';

  const collapsedClasses = collapsed ? 'justify-center px-2' : '';

  const itemClasses = [
    ...baseClasses,
    stateClasses,
    disabledClasses,
    collapsedClasses
  ].join(' ');

  const handleClick = () => {
    if (!item.disabled && onClick) {
      onClick(item);
    }
  };

  if (collapsed) {
    return (
      <Tooltip content={item.label} position="right">
        <button
          type="button"
          className={`${itemClasses} w-10 h-10 flex items-center justify-center`}
          onClick={handleClick}
          disabled={item.disabled}
        >
          {showIcons && item.icon ? item.icon : item.label.charAt(0)}
        </button>
      </Tooltip>
    );
  }

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

const SidebarSectionComponent: React.FC<{
  section: SidebarSection;
  collapsed?: boolean;
  variant: string;
  size: string;
  showIcons: boolean;
  showBadges: boolean;
  activeItem?: string;
  onItemClick?: (item: SidebarItem) => void;
}> = ({ section, collapsed, variant, size, showIcons, showBadges, activeItem, onItemClick }) => {
  const [isExpanded, setIsExpanded] = useState(section.defaultExpanded ?? true);

  if (collapsed) {
    return (
      <div className="space-y-2">
        {section.items.map(item => (
          <SidebarItemComponent
            key={item.id}
            item={item}
            active={activeItem === item.id}
            collapsed={collapsed}
            variant={variant}
            size={size}
            showIcons={showIcons}
            showBadges={showBadges}
            onClick={onItemClick}
          />
        ))}
      </div>
    );
  }

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
            <SidebarItemComponent
              key={item.id}
              item={item}
              active={activeItem === item.id}
              collapsed={collapsed}
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

export const Sidebar_v2: React.FC<Sidebar_v2Props> = ({
  items = [],
  sections = [],
  variant = 'default',
  size = 'md',
  width = '280px',
  collapsed = false,
  collapsible = true,
  onCollapse,
  activeItem,
  onItemClick,
  showIcons = true,
  showBadges = true,
  searchable = false,
  loading = false,
  className = ''
}) => {
  const [isCollapsed, setIsCollapsed] = useState(collapsed);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    setIsCollapsed(collapsed);
  }, [collapsed]);

  const handleCollapse = () => {
    const newCollapsed = !isCollapsed;
    setIsCollapsed(newCollapsed);
    onCollapse?.(newCollapsed);
  };

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
      <div className="flex items-center justify-center h-64">
        <Loading variant="spinner" size="lg" text="Loading sidebar..." />
      </div>
    );
  }

  const sidebarClasses = [
    'h-full bg-white border-r border-secondary-200 flex flex-col transition-all duration-300',
    variant === 'floating' ? 'shadow-lg rounded-r-lg' : '',
    className
  ].join(' ');

  const sidebarStyle = {
    width: isCollapsed ? '64px' : width
  };

  return (
    <div className={sidebarClasses} style={sidebarStyle}>
      {/* Header */}
      {!isCollapsed && (
        <div className="p-4 border-b border-secondary-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-secondary-900">Navigation</h2>
            {collapsible && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCollapse}
                className="p-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                </svg>
              </Button>
            )}
          </div>
          
          {searchable && (
            <div className="mt-4">
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
              />
            </div>
          )}
        </div>
      )}

      {/* Collapsed Header */}
      {isCollapsed && (
        <div className="p-2 border-b border-secondary-200">
          <div className="flex items-center justify-center">
            {collapsible && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCollapse}
                className="p-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                </svg>
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {filteredSections.length > 0 ? (
          <div className="space-y-6">
            {filteredSections.map(section => (
              <SidebarSectionComponent
                key={section.id}
                section={section}
                collapsed={isCollapsed}
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
              <SidebarItemComponent
                key={item.id}
                item={item}
                active={activeItem === item.id}
                collapsed={isCollapsed}
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

      {/* Footer */}
      {!isCollapsed && (
        <div className="p-4 border-t border-secondary-200">
          <div className="text-xs text-secondary-500 text-center">
            © 2024 Omni Keywords Finder
          </div>
        </div>
      )}
    </div>
  );
};

// Sidebar Hook
export const useSidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [activeItem, setActiveItem] = useState<string>('');

  const toggleCollapse = () => {
    setCollapsed(!collapsed);
  };

  const setActive = (itemId: string) => {
    setActiveItem(itemId);
  };

  return {
    collapsed,
    activeItem,
    toggleCollapse,
    setActive
  };
}; 
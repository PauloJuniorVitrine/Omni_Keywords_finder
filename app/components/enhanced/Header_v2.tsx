import React, { useState, useEffect } from 'react';
import { Button } from '../../../ui/design-system/components/Button';
import { Card } from '../../../ui/design-system/components/Card';
import { Loading } from '../../../ui/design-system/components/Loading';
import { Tooltip } from '../../../ui/design-system/components/Tooltip';

export interface HeaderAction {
  id: string;
  label: string;
  icon?: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  disabled?: boolean;
  badge?: string | number;
}

export interface HeaderNotification {
  id: string;
  title: string;
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  timestamp: Date;
  read?: boolean;
  action?: () => void;
}

export interface HeaderUser {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role?: string;
  status?: 'online' | 'offline' | 'away';
}

export interface Header_v2Props {
  title?: string;
  subtitle?: string;
  logo?: React.ReactNode;
  actions?: HeaderAction[];
  notifications?: HeaderNotification[];
  user?: HeaderUser;
  variant?: 'default' | 'minimal' | 'elevated';
  size?: 'sm' | 'md' | 'lg';
  showSearch?: boolean;
  searchPlaceholder?: string;
  onSearch?: (query: string) => void;
  showNotifications?: boolean;
  showUserMenu?: boolean;
  onNotificationClick?: (notification: HeaderNotification) => void;
  onUserAction?: (action: string) => void;
  loading?: boolean;
  className?: string;
}

const HeaderActionComponent: React.FC<{
  action: HeaderAction;
  size: string;
}> = ({ action, size }) => {
  const handleClick = () => {
    if (!action.disabled && action.onClick) {
      action.onClick();
    }
  };

  return (
    <Button
      variant={action.variant || 'ghost'}
      size={action.size || size}
      onClick={handleClick}
      disabled={action.disabled}
      leftIcon={action.icon}
      className="relative"
    >
      {action.label}
      {action.badge && (
        <span className="absolute -top-1 -right-1 px-1.5 py-0.5 text-xs font-medium bg-error-500 text-white rounded-full">
          {action.badge}
        </span>
      )}
    </Button>
  );
};

const NotificationDropdown: React.FC<{
  notifications: HeaderNotification[];
  onNotificationClick?: (notification: HeaderNotification) => void;
}> = ({ notifications, onNotificationClick }) => {
  const [isOpen, setIsOpen] = useState(false);
  const unreadCount = notifications.filter(n => !n.read).length;

  const getNotificationIcon = (type?: string) => {
    switch (type) {
      case 'success':
        return (
          <svg className="w-4 h-4 text-success-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'warning':
        return (
          <svg className="w-4 h-4 text-warning-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      case 'error':
        return (
          <svg className="w-4 h-4 text-error-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="md"
        onClick={() => setIsOpen(!isOpen)}
        className="relative"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM4.83 2.83l4.24 4.24M14.83 2.83l-4.24 4.24M20.12 12.29l-4.24-4.24M14.83 17.66l-4.24-4.24M4.83 17.66l4.24-4.24M2.88 12.29l4.24 4.24" />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 px-1.5 py-0.5 text-xs font-medium bg-error-500 text-white rounded-full">
            {unreadCount}
          </span>
        )}
      </Button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-secondary-200 z-50">
          <div className="p-4 border-b border-secondary-200">
            <h3 className="text-lg font-semibold text-secondary-900">Notifications</h3>
          </div>
          
          <div className="max-h-96 overflow-y-auto">
            {notifications.length > 0 ? (
              notifications.map(notification => (
                <div
                  key={notification.id}
                  className={`p-4 border-b border-secondary-100 cursor-pointer hover:bg-secondary-50 ${
                    !notification.read ? 'bg-primary-50' : ''
                  }`}
                  onClick={() => {
                    onNotificationClick?.(notification);
                    setIsOpen(false);
                  }}
                >
                  <div className="flex items-start space-x-3">
                    {getNotificationIcon(notification.type)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-secondary-900">
                        {notification.title}
                      </p>
                      <p className="text-sm text-secondary-600 mt-1">
                        {notification.message}
                      </p>
                      <p className="text-xs text-secondary-400 mt-2">
                        {notification.timestamp.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-4 text-center text-secondary-500">
                No notifications
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const UserMenu: React.FC<{
  user: HeaderUser;
  onUserAction?: (action: string) => void;
}> = ({ user, onUserAction }) => {
  const [isOpen, setIsOpen] = useState(false);

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'online':
        return 'bg-success-500';
      case 'away':
        return 'bg-warning-500';
      default:
        return 'bg-secondary-400';
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-3 p-2 rounded-lg hover:bg-secondary-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
      >
        <div className="relative">
          {user.avatar ? (
            <img
              src={user.avatar}
              alt={user.name}
              className="w-8 h-8 rounded-full"
            />
          ) : (
            <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white font-medium">
              {user.name.charAt(0)}
            </div>
          )}
          <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${getStatusColor(user.status)}`} />
        </div>
        
        <div className="hidden md:block text-left">
          <p className="text-sm font-medium text-secondary-900">{user.name}</p>
          <p className="text-xs text-secondary-500">{user.role}</p>
        </div>
        
        <svg className="w-4 h-4 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-secondary-200 z-50">
          <div className="p-4 border-b border-secondary-200">
            <p className="text-sm font-medium text-secondary-900">{user.name}</p>
            <p className="text-xs text-secondary-500">{user.email}</p>
          </div>
          
          <div className="py-2">
            <button
              onClick={() => {
                onUserAction?.('profile');
                setIsOpen(false);
              }}
              className="w-full px-4 py-2 text-left text-sm text-secondary-700 hover:bg-secondary-100"
            >
              Profile
            </button>
            <button
              onClick={() => {
                onUserAction?.('settings');
                setIsOpen(false);
              }}
              className="w-full px-4 py-2 text-left text-sm text-secondary-700 hover:bg-secondary-100"
            >
              Settings
            </button>
            <button
              onClick={() => {
                onUserAction?.('logout');
                setIsOpen(false);
              }}
              className="w-full px-4 py-2 text-left text-sm text-error-600 hover:bg-error-50"
            >
              Sign out
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export const Header_v2: React.FC<Header_v2Props> = ({
  title,
  subtitle,
  logo,
  actions = [],
  notifications = [],
  user,
  variant = 'default',
  size = 'md',
  showSearch = false,
  searchPlaceholder = 'Search...',
  onSearch,
  showNotifications = true,
  showUserMenu = true,
  onNotificationClick,
  onUserAction,
  loading = false,
  className = ''
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    onSearch?.(query);
  };

  const headerClasses = [
    'bg-white border-b border-secondary-200',
    variant === 'elevated' ? 'shadow-lg' : '',
    className
  ].join(' ');

  const contentClasses = {
    sm: 'px-4 py-2',
    md: 'px-6 py-4',
    lg: 'px-8 py-6'
  };

  if (loading) {
    return (
      <div className={headerClasses}>
        <div className={contentClasses[size]}>
          <Loading variant="spinner" size="md" text="Loading header..." />
        </div>
      </div>
    );
  }

  return (
    <header className={headerClasses}>
      <div className={contentClasses[size]}>
        <div className="flex items-center justify-between">
          {/* Left Section */}
          <div className="flex items-center space-x-4">
            {logo && (
              <div className="flex-shrink-0">
                {logo}
              </div>
            )}
            
            {(title || subtitle) && (
              <div>
                {title && (
                  <h1 className="text-lg font-semibold text-secondary-900">{title}</h1>
                )}
                {subtitle && (
                  <p className="text-sm text-secondary-600">{subtitle}</p>
                )}
              </div>
            )}
          </div>

          {/* Center Section - Search */}
          {showSearch && (
            <div className="flex-1 max-w-md mx-8">
              <div className="relative">
                <input
                  type="text"
                  placeholder={searchPlaceholder}
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="w-full px-4 py-2 pl-10 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <svg
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          )}

          {/* Right Section */}
          <div className="flex items-center space-x-4">
            {/* Actions */}
            {actions.map(action => (
              <HeaderActionComponent
                key={action.id}
                action={action}
                size={size}
              />
            ))}

            {/* Notifications */}
            {showNotifications && notifications.length > 0 && (
              <NotificationDropdown
                notifications={notifications}
                onNotificationClick={onNotificationClick}
              />
            )}

            {/* User Menu */}
            {showUserMenu && user && (
              <UserMenu
                user={user}
                onUserAction={onUserAction}
              />
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

// Header Hook
export const useHeader = () => {
  const [notifications, setNotifications] = useState<HeaderNotification[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  const addNotification = (notification: HeaderNotification) => {
    setNotifications(prev => [notification, ...prev]);
  };

  const markAsRead = (notificationId: string) => {
    setNotifications(prev => prev.map(n => 
      n.id === notificationId ? { ...n, read: true } : n
    ));
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  return {
    notifications,
    searchQuery,
    addNotification,
    markAsRead,
    clearNotifications,
    setSearchQuery
  };
}; 
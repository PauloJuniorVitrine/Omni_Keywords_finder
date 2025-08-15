/**
 * SkeletonLoader.tsx
 * 
 * Sistema de skeleton loaders para Omni Keywords Finder
 * 
 * Tracing ID: UI_ENTERPRISE_CHECKLIST_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 9.1
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React from 'react';
import { cn } from '../../utils/cn';

// Types
export type SkeletonType = 
  | 'text' 
  | 'title' 
  | 'paragraph' 
  | 'avatar' 
  | 'button' 
  | 'input' 
  | 'card' 
  | 'table-row' 
  | 'table-cell' 
  | 'list-item' 
  | 'image' 
  | 'badge' 
  | 'progress';

export interface SkeletonProps {
  type?: SkeletonType;
  className?: string;
  width?: string | number;
  height?: string | number;
  lines?: number;
  animated?: boolean;
  rounded?: boolean;
}

export interface SkeletonGroupProps {
  children: React.ReactNode;
  className?: string;
  animated?: boolean;
}

// Individual Skeleton Component
export const Skeleton: React.FC<SkeletonProps> = ({
  type = 'text',
  className = '',
  width,
  height,
  lines = 1,
  animated = true,
  rounded = true,
}) => {
  const baseClasses = cn(
    'bg-gray-200 dark:bg-gray-700',
    animated && 'animate-pulse',
    rounded && 'rounded',
    className
  );

  const getSkeletonClasses = () => {
    switch (type) {
      case 'title':
        return cn(baseClasses, 'h-6 w-3/4');
      case 'paragraph':
        return cn(baseClasses, 'h-4 w-full');
      case 'avatar':
        return cn(baseClasses, 'h-10 w-10 rounded-full');
      case 'button':
        return cn(baseClasses, 'h-10 w-24');
      case 'input':
        return cn(baseClasses, 'h-10 w-full');
      case 'card':
        return cn(baseClasses, 'h-32 w-full');
      case 'table-row':
        return cn(baseClasses, 'h-12 w-full');
      case 'table-cell':
        return cn(baseClasses, 'h-6 w-full');
      case 'list-item':
        return cn(baseClasses, 'h-16 w-full');
      case 'image':
        return cn(baseClasses, 'h-48 w-full');
      case 'badge':
        return cn(baseClasses, 'h-6 w-16');
      case 'progress':
        return cn(baseClasses, 'h-2 w-full');
      default:
        return cn(baseClasses, 'h-4 w-full');
    }
  };

  const getSkeletonStyle = () => {
    const style: React.CSSProperties = {};
    if (width) style.width = typeof width === 'number' ? `${width}px` : width;
    if (height) style.height = typeof height === 'number' ? `${height}px` : height;
    return style;
  };

  if (lines > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={getSkeletonClasses()}
            style={getSkeletonStyle()}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={getSkeletonClasses()}
      style={getSkeletonStyle()}
    />
  );
};

// Skeleton Group Component
export const SkeletonGroup: React.FC<SkeletonGroupProps> = ({
  children,
  className = '',
  animated = true,
}) => {
  return (
    <div className={cn('space-y-4', className)}>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, { animated } as any);
        }
        return child;
      })}
    </div>
  );
};

// Predefined Skeleton Components
export const TableSkeleton: React.FC<{
  rows?: number;
  columns?: number;
  className?: string;
}> = ({ rows = 5, columns = 4, className = '' }) => {
  return (
    <div className={cn('space-y-2', className)}>
      {/* Header */}
      <div className="flex space-x-4">
        {Array.from({ length: columns }).map((_, index) => (
          <Skeleton key={index} type="table-cell" className="flex-1" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex space-x-4">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} type="table-cell" className="flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
};

export const CardSkeleton: React.FC<{
  className?: string;
  showAvatar?: boolean;
  showActions?: boolean;
}> = ({ className = '', showAvatar = true, showActions = true }) => {
  return (
    <div className={cn('p-4 border border-gray-200 dark:border-gray-700 rounded-lg', className)}>
      <div className="flex items-start space-x-3">
        {showAvatar && <Skeleton type="avatar" />}
        <div className="flex-1 space-y-3">
          <Skeleton type="title" />
          <Skeleton type="paragraph" lines={2} />
          {showActions && (
            <div className="flex space-x-2">
              <Skeleton type="button" />
              <Skeleton type="button" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export const FormSkeleton: React.FC<{
  fields?: number;
  className?: string;
}> = ({ fields = 4, className = '' }) => {
  return (
    <div className={cn('space-y-4', className)}>
      {Array.from({ length: fields }).map((_, index) => (
        <div key={index} className="space-y-2">
          <Skeleton type="text" width="w-24" />
          <Skeleton type="input" />
        </div>
      ))}
      <div className="flex space-x-2 pt-4">
        <Skeleton type="button" />
        <Skeleton type="button" />
      </div>
    </div>
  );
};

export const ListSkeleton: React.FC<{
  items?: number;
  className?: string;
}> = ({ items = 5, className = '' }) => {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: items }).map((_, index) => (
        <div key={index} className="flex items-center space-x-3">
          <Skeleton type="avatar" />
          <div className="flex-1 space-y-2">
            <Skeleton type="title" width="w-1/2" />
            <Skeleton type="paragraph" width="w-3/4" />
          </div>
          <Skeleton type="badge" />
        </div>
      ))}
    </div>
  );
};

export const DashboardSkeleton: React.FC<{
  className?: string;
}> = ({ className = '' }) => {
  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="space-y-2">
        <Skeleton type="title" width="w-1/3" />
        <Skeleton type="paragraph" width="w-1/2" />
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <CardSkeleton key={index} showAvatar={false} showActions={false} />
        ))}
      </div>
      
      {/* Table */}
      <TableSkeleton rows={5} columns={4} />
    </div>
  );
};

// Hooks
export const useSkeleton = (loading: boolean, content: React.ReactNode, skeleton: React.ReactNode) => {
  if (loading) {
    return skeleton;
  }
  return content;
};

export default Skeleton; 
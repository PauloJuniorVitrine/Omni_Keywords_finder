/**
 * Virtualization System for Large Lists
 * 
 * Tracing ID: VIRTUALIZATION_20250127_001
 * Prompt: CHECKLIST_INTERFACE_2.md - Item 4.3
 * Ruleset: enterprise_control_layer.yaml
 * Date: 2025-01-27
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';

// Types for virtualization
export interface VirtualizationOptions {
  itemHeight: number;
  overscan?: number;
  containerHeight?: number;
  containerWidth?: number;
  horizontal?: boolean;
  dynamicHeight?: boolean;
}

export interface VirtualItem {
  index: number;
  start: number;
  end: number;
  size: number;
  offset: number;
}

export interface VirtualListProps<T> {
  items: T[];
  itemHeight: number;
  containerHeight: number;
  containerWidth?: number;
  overscan?: number;
  horizontal?: boolean;
  dynamicHeight?: boolean;
  renderItem: (item: T, index: number, virtualItem: VirtualItem) => React.ReactNode;
  onScroll?: (scrollTop: number, scrollLeft: number) => void;
  className?: string;
  style?: React.CSSProperties;
}

// Calculate visible range based on scroll position
const calculateVisibleRange = (
  scrollTop: number,
  containerHeight: number,
  itemHeight: number,
  totalItems: number,
  overscan: number = 5
): { start: number; end: number } => {
  const start = Math.floor(scrollTop / itemHeight);
  const end = Math.min(
    start + Math.ceil(containerHeight / itemHeight) + overscan,
    totalItems
  );
  
  return {
    start: Math.max(0, start - overscan),
    end
  };
};

// Virtual list component
export const VirtualList = <T extends any>({
  items,
  itemHeight,
  containerHeight,
  containerWidth,
  overscan = 5,
  horizontal = false,
  dynamicHeight = false,
  renderItem,
  onScroll,
  className,
  style
}: VirtualListProps<T>) => {
  const [scrollTop, setScrollTop] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const totalItems = items.length;
  const totalHeight = totalItems * itemHeight;
  const totalWidth = horizontal ? totalItems * (containerWidth || itemHeight) : 0;

  // Calculate visible range
  const visibleRange = useMemo(() => {
    if (horizontal) {
      return calculateVisibleRange(scrollLeft, containerWidth || 0, itemHeight, totalItems, overscan);
    }
    return calculateVisibleRange(scrollTop, containerHeight, itemHeight, totalItems, overscan);
  }, [scrollTop, scrollLeft, containerHeight, containerWidth, itemHeight, totalItems, overscan, horizontal]);

  // Generate virtual items
  const virtualItems = useMemo(() => {
    const items: VirtualItem[] = [];
    for (let i = visibleRange.start; i < visibleRange.end; i++) {
      const offset = i * itemHeight;
      items.push({
        index: i,
        start: offset,
        end: offset + itemHeight,
        size: itemHeight,
        offset
      });
    }
    return items;
  }, [visibleRange, itemHeight]);

  // Handle scroll events
  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    const target = event.target as HTMLDivElement;
    const newScrollTop = target.scrollTop;
    const newScrollLeft = target.scrollLeft;
    
    setScrollTop(newScrollTop);
    setScrollLeft(newScrollLeft);
    onScroll?.(newScrollTop, newScrollLeft);
  }, [onScroll]);

  // Scroll to specific item
  const scrollToItem = useCallback((index: number, align: 'start' | 'center' | 'end' = 'start') => {
    if (!containerRef.current) return;
    
    let scrollPosition = index * itemHeight;
    
    if (align === 'center') {
      scrollPosition -= containerHeight / 2 - itemHeight / 2;
    } else if (align === 'end') {
      scrollPosition -= containerHeight - itemHeight;
    }
    
    containerRef.current.scrollTop = Math.max(0, scrollPosition);
  }, [itemHeight, containerHeight]);

  // Scroll to specific position
  const scrollToPosition = useCallback((position: number) => {
    if (!containerRef.current) return;
    containerRef.current.scrollTop = position;
  }, []);

  return (
    <div
      ref={containerRef}
      className={`virtual-list ${className || ''}`}
      style={{
        height: containerHeight,
        width: containerWidth,
        overflow: 'auto',
        position: 'relative',
        ...style
      }}
      onScroll={handleScroll}
    >
      <div
        style={{
          height: totalHeight,
          width: horizontal ? totalWidth : '100%',
          position: 'relative'
        }}
      >
        {virtualItems.map((virtualItem) => (
          <div
            key={virtualItem.index}
            style={{
              position: 'absolute',
              top: virtualItem.offset,
              left: horizontal ? virtualItem.offset : 0,
              height: virtualItem.size,
              width: horizontal ? virtualItem.size : '100%'
            }}
          >
            {renderItem(items[virtualItem.index], virtualItem.index, virtualItem)}
          </div>
        ))}
      </div>
    </div>
  );
};

// Hook for virtual scrolling
export const useVirtualScroll = (
  totalItems: number,
  itemHeight: number,
  containerHeight: number,
  overscan: number = 5
) => {
  const [scrollTop, setScrollTop] = useState(0);
  
  const visibleRange = useMemo(() => {
    return calculateVisibleRange(scrollTop, containerHeight, itemHeight, totalItems, overscan);
  }, [scrollTop, containerHeight, itemHeight, totalItems, overscan]);
  
  const virtualItems = useMemo(() => {
    const items: VirtualItem[] = [];
    for (let i = visibleRange.start; i < visibleRange.end; i++) {
      const offset = i * itemHeight;
      items.push({
        index: i,
        start: offset,
        end: offset + itemHeight,
        size: itemHeight,
        offset
      });
    }
    return items;
  }, [visibleRange, itemHeight]);
  
  const totalHeight = totalItems * itemHeight;
  
  return {
    scrollTop,
    setScrollTop,
    visibleRange,
    virtualItems,
    totalHeight
  };
};

// Dynamic height virtualization
export const useDynamicVirtualScroll = (
  items: Array<{ height: number }>,
  containerHeight: number,
  overscan: number = 5
) => {
  const [scrollTop, setScrollTop] = useState(0);
  const [itemPositions, setItemPositions] = useState<number[]>([]);
  
  // Calculate cumulative positions
  useEffect(() => {
    const positions: number[] = [0];
    let cumulativeHeight = 0;
    
    for (const item of items) {
      cumulativeHeight += item.height;
      positions.push(cumulativeHeight);
    }
    
    setItemPositions(positions);
  }, [items]);
  
  // Find visible range for dynamic heights
  const visibleRange = useMemo(() => {
    if (itemPositions.length === 0) return { start: 0, end: 0 };
    
    const start = itemPositions.findIndex(pos => pos > scrollTop) - 1;
    const end = itemPositions.findIndex(pos => pos > scrollTop + containerHeight);
    
    return {
      start: Math.max(0, start - overscan),
      end: Math.min(items.length, end + overscan)
    };
  }, [scrollTop, containerHeight, itemPositions, items.length, overscan]);
  
  const virtualItems = useMemo(() => {
    const items: VirtualItem[] = [];
    for (let i = visibleRange.start; i < visibleRange.end; i++) {
      const start = itemPositions[i] || 0;
      const end = itemPositions[i + 1] || 0;
      const size = end - start;
      
      items.push({
        index: i,
        start,
        end,
        size,
        offset: start
      });
    }
    return items;
  }, [visibleRange, itemPositions]);
  
  const totalHeight = itemPositions[itemPositions.length - 1] || 0;
  
  return {
    scrollTop,
    setScrollTop,
    visibleRange,
    virtualItems,
    totalHeight
  };
};

// Grid virtualization
export const VirtualGrid = <T extends any>({
  items,
  itemWidth,
  itemHeight,
  containerWidth,
  containerHeight,
  overscan = 5,
  renderItem,
  onScroll,
  className,
  style
}: {
  items: T[];
  itemWidth: number;
  itemHeight: number;
  containerWidth: number;
  containerHeight: number;
  overscan?: number;
  renderItem: (item: T, index: number, row: number, col: number) => React.ReactNode;
  onScroll?: (scrollTop: number, scrollLeft: number) => void;
  className?: string;
  style?: React.CSSProperties;
}) => {
  const [scrollTop, setScrollTop] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const columnsPerRow = Math.floor(containerWidth / itemWidth);
  const totalRows = Math.ceil(items.length / columnsPerRow);
  const totalHeight = totalRows * itemHeight;
  const totalWidth = columnsPerRow * itemWidth;
  
  // Calculate visible range
  const visibleRange = useMemo(() => {
    const startRow = Math.floor(scrollTop / itemHeight);
    const endRow = Math.min(
      startRow + Math.ceil(containerHeight / itemHeight) + overscan,
      totalRows
    );
    
    return {
      startRow: Math.max(0, startRow - overscan),
      endRow
    };
  }, [scrollTop, containerHeight, itemHeight, totalRows, overscan]);
  
  // Generate grid items
  const gridItems = useMemo(() => {
    const items: Array<{ item: T; index: number; row: number; col: number; offset: number }> = [];
    
    for (let row = visibleRange.startRow; row < visibleRange.endRow; row++) {
      for (let col = 0; col < columnsPerRow; col++) {
        const index = row * columnsPerRow + col;
        if (index < items.length) {
          items.push({
            item: items[index],
            index,
            row,
            col,
            offset: row * itemHeight
          });
        }
      }
    }
    
    return items;
  }, [visibleRange, columnsPerRow, items, itemHeight]);
  
  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    const target = event.target as HTMLDivElement;
    setScrollTop(target.scrollTop);
    setScrollLeft(target.scrollLeft);
    onScroll?.(target.scrollTop, target.scrollLeft);
  }, [onScroll]);
  
  return (
    <div
      ref={containerRef}
      className={`virtual-grid ${className || ''}`}
      style={{
        height: containerHeight,
        width: containerWidth,
        overflow: 'auto',
        position: 'relative',
        ...style
      }}
      onScroll={handleScroll}
    >
      <div
        style={{
          height: totalHeight,
          width: totalWidth,
          position: 'relative'
        }}
      >
        {gridItems.map(({ item, index, row, col, offset }) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              top: offset,
              left: col * itemWidth,
              width: itemWidth,
              height: itemHeight
            }}
          >
            {renderItem(item, index, row, col)}
          </div>
        ))}
      </div>
    </div>
  );
};

// Performance monitoring for virtualization
export const useVirtualizationMetrics = () => {
  const [metrics, setMetrics] = useState({
    totalItems: 0,
    visibleItems: 0,
    renderedItems: 0,
    scrollEvents: 0,
    averageRenderTime: 0
  });
  
  const trackRender = (renderTime: number) => {
    setMetrics(prev => ({
      ...prev,
      renderedItems: prev.renderedItems + 1,
      averageRenderTime: 
        (prev.averageRenderTime * (prev.renderedItems - 1) + renderTime) / 
        prev.renderedItems
    }));
  };
  
  const trackScroll = () => {
    setMetrics(prev => ({
      ...prev,
      scrollEvents: prev.scrollEvents + 1
    }));
  };
  
  const getRenderEfficiency = () => {
    return metrics.totalItems > 0 ? (metrics.visibleItems / metrics.totalItems) * 100 : 0;
  };
  
  return {
    metrics,
    trackRender,
    trackScroll,
    getRenderEfficiency
  };
};

export default {
  VirtualList,
  useVirtualScroll,
  useDynamicVirtualScroll,
  VirtualGrid,
  useVirtualizationMetrics
}; 
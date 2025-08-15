/**
 * Performance Monitoring System
 * 
 * Tracing ID: PERFORMANCE_MONITORING_20250127_001
 * Prompt: CHECKLIST_INTERFACE_2.md - Item 4.5
 * Ruleset: enterprise_control_layer.yaml
 * Date: 2025-01-27
 */

import { useEffect, useRef, useState, useCallback } from 'react';

// Types for performance monitoring
export interface PerformanceMetrics {
  // Web Vitals
  fcp: number; // First Contentful Paint
  lcp: number; // Largest Contentful Paint
  fid: number; // First Input Delay
  cls: number; // Cumulative Layout Shift
  ttfb: number; // Time to First Byte
  
  // Custom metrics
  domLoadTime: number;
  resourceLoadTime: number;
  jsExecutionTime: number;
  cssLoadTime: number;
  
  // Memory metrics
  memoryUsage: number;
  memoryLimit: number;
  
  // Network metrics
  networkRequests: number;
  networkErrors: number;
  averageResponseTime: number;
  
  // Component metrics
  componentRenderTime: number;
  componentMountTime: number;
  componentUpdateTime: number;
}

export interface PerformanceThresholds {
  fcp: number; // 1.5s
  lcp: number; // 2.5s
  fid: number; // 100ms
  cls: number; // 0.1
  ttfb: number; // 600ms
}

export interface PerformanceEvent {
  type: string;
  value: number;
  timestamp: number;
  metadata?: Record<string, any>;
}

// Default performance thresholds
const DEFAULT_THRESHOLDS: PerformanceThresholds = {
  fcp: 1500,
  lcp: 2500,
  fid: 100,
  cls: 0.1,
  ttfb: 600
};

// Performance observer for Web Vitals
class PerformanceObserver {
  private observers: Map<string, any> = new Map();
  private metrics: PerformanceMetrics;
  private events: PerformanceEvent[] = [];
  private thresholds: PerformanceThresholds;

  constructor(thresholds: PerformanceThresholds = DEFAULT_THRESHOLDS) {
    this.thresholds = thresholds;
    this.metrics = this.initializeMetrics();
    this.setupObservers();
  }

  private initializeMetrics(): PerformanceMetrics {
    return {
      fcp: 0,
      lcp: 0,
      fid: 0,
      cls: 0,
      ttfb: 0,
      domLoadTime: 0,
      resourceLoadTime: 0,
      jsExecutionTime: 0,
      cssLoadTime: 0,
      memoryUsage: 0,
      memoryLimit: 0,
      networkRequests: 0,
      networkErrors: 0,
      averageResponseTime: 0,
      componentRenderTime: 0,
      componentMountTime: 0,
      componentUpdateTime: 0
    };
  }

  private setupObservers(): void {
    // First Contentful Paint
    this.observeFCP();
    
    // Largest Contentful Paint
    this.observeLCP();
    
    // First Input Delay
    this.observeFID();
    
    // Cumulative Layout Shift
    this.observeCLS();
    
    // Time to First Byte
    this.observeTTFB();
    
    // Memory usage
    this.observeMemory();
    
    // Network requests
    this.observeNetwork();
  }

  private observeFCP(): void {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new (window as any).PerformanceObserver((list: any) => {
          const entries = list.getEntries();
          const fcpEntry = entries.find((entry: any) => entry.name === 'first-contentful-paint');
          if (fcpEntry) {
            this.metrics.fcp = fcpEntry.startTime;
            this.recordEvent('fcp', fcpEntry.startTime);
          }
        });
        observer.observe({ entryTypes: ['paint'] });
        this.observers.set('fcp', observer);
      } catch (error) {
        console.warn('FCP observer not supported:', error);
      }
    }
  }

  private observeLCP(): void {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new (window as any).PerformanceObserver((list: any) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          if (lastEntry) {
            this.metrics.lcp = lastEntry.startTime;
            this.recordEvent('lcp', lastEntry.startTime);
          }
        });
        observer.observe({ entryTypes: ['largest-contentful-paint'] });
        this.observers.set('lcp', observer);
      } catch (error) {
        console.warn('LCP observer not supported:', error);
      }
    }
  }

  private observeFID(): void {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new (window as any).PerformanceObserver((list: any) => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            this.metrics.fid = entry.processingStart - entry.startTime;
            this.recordEvent('fid', this.metrics.fid);
          });
        });
        observer.observe({ entryTypes: ['first-input'] });
        this.observers.set('fid', observer);
      } catch (error) {
        console.warn('FID observer not supported:', error);
      }
    }
  }

  private observeCLS(): void {
    if ('PerformanceObserver' in window) {
      try {
        let clsValue = 0;
        const observer = new (window as any).PerformanceObserver((list: any) => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
              this.metrics.cls = clsValue;
              this.recordEvent('cls', clsValue);
            }
          });
        });
        observer.observe({ entryTypes: ['layout-shift'] });
        this.observers.set('cls', observer);
      } catch (error) {
        console.warn('CLS observer not supported:', error);
      }
    }
  }

  private observeTTFB(): void {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new (window as any).PerformanceObserver((list: any) => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            if (entry.entryType === 'navigation') {
              this.metrics.ttfb = entry.responseStart - entry.requestStart;
              this.recordEvent('ttfb', this.metrics.ttfb);
            }
          });
        });
        observer.observe({ entryTypes: ['navigation'] });
        this.observers.set('ttfb', observer);
      } catch (error) {
        console.warn('TTFB observer not supported:', error);
      }
    }
  }

  private observeMemory(): void {
    if ('memory' in performance) {
      const updateMemory = () => {
        const memory = (performance as any).memory;
        this.metrics.memoryUsage = memory.usedJSHeapSize;
        this.metrics.memoryLimit = memory.jsHeapSizeLimit;
        this.recordEvent('memory', memory.usedJSHeapSize);
      };
      
      updateMemory();
      setInterval(updateMemory, 5000); // Update every 5 seconds
    }
  }

  private observeNetwork(): void {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new (window as any).PerformanceObserver((list: any) => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            if (entry.entryType === 'resource') {
              this.metrics.networkRequests++;
              this.metrics.averageResponseTime = 
                (this.metrics.averageResponseTime * (this.metrics.networkRequests - 1) + entry.duration) / 
                this.metrics.networkRequests;
              
              if (entry.transferSize === 0) {
                this.metrics.networkErrors++;
              }
              
              this.recordEvent('network', entry.duration, { url: entry.name });
            }
          });
        });
        observer.observe({ entryTypes: ['resource'] });
        this.observers.set('network', observer);
      } catch (error) {
        console.warn('Network observer not supported:', error);
      }
    }
  }

  private recordEvent(type: string, value: number, metadata?: Record<string, any>): void {
    const event: PerformanceEvent = {
      type,
      value,
      timestamp: Date.now(),
      metadata
    };
    
    this.events.push(event);
    
    // Keep only last 1000 events
    if (this.events.length > 1000) {
      this.events = this.events.slice(-1000);
    }
  }

  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  getEvents(): PerformanceEvent[] {
    return [...this.events];
  }

  getEventsByType(type: string): PerformanceEvent[] {
    return this.events.filter(event => event.type === type);
  }

  getAverageMetric(type: string): number {
    const events = this.getEventsByType(type);
    if (events.length === 0) return 0;
    
    const sum = events.reduce((total, event) => total + event.value, 0);
    return sum / events.length;
  }

  checkThresholds(): Record<string, boolean> {
    const results: Record<string, boolean> = {};
    
    results.fcp = this.metrics.fcp <= this.thresholds.fcp;
    results.lcp = this.metrics.lcp <= this.thresholds.lcp;
    results.fid = this.metrics.fid <= this.thresholds.fid;
    results.cls = this.metrics.cls <= this.thresholds.cls;
    results.ttfb = this.metrics.ttfb <= this.thresholds.ttfb;
    
    return results;
  }

  disconnect(): void {
    this.observers.forEach(observer => {
      if (observer && typeof observer.disconnect === 'function') {
        observer.disconnect();
      }
    });
    this.observers.clear();
  }
}

// Global performance observer instance
let globalPerformanceObserver: PerformanceObserver | null = null;

// Hook for performance monitoring
export const usePerformanceMonitoring = (thresholds?: PerformanceThresholds) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [events, setEvents] = useState<PerformanceEvent[]>([]);
  const [thresholdResults, setThresholdResults] = useState<Record<string, boolean>>({});
  const observerRef = useRef<PerformanceObserver | null>(null);

  useEffect(() => {
    if (!globalPerformanceObserver) {
      globalPerformanceObserver = new PerformanceObserver(thresholds);
    }
    
    observerRef.current = globalPerformanceObserver;

    const updateMetrics = () => {
      if (observerRef.current) {
        const currentMetrics = observerRef.current.getMetrics();
        const currentEvents = observerRef.current.getEvents();
        const currentThresholds = observerRef.current.checkThresholds();
        
        setMetrics(currentMetrics);
        setEvents(currentEvents);
        setThresholdResults(currentThresholds);
      }
    };

    // Update immediately
    updateMetrics();

    // Update every second
    const interval = setInterval(updateMetrics, 1000);

    return () => {
      clearInterval(interval);
    };
  }, [thresholds]);

  const recordCustomEvent = useCallback((type: string, value: number, metadata?: Record<string, any>) => {
    if (observerRef.current) {
      (observerRef.current as any).recordEvent(type, value, metadata);
    }
  }, []);

  const getMetricHistory = useCallback((type: string, limit: number = 100) => {
    if (observerRef.current) {
      return observerRef.current.getEventsByType(type).slice(-limit);
    }
    return [];
  }, []);

  const getAverageMetric = useCallback((type: string) => {
    if (observerRef.current) {
      return observerRef.current.getAverageMetric(type);
    }
    return 0;
  }, []);

  return {
    metrics,
    events,
    thresholdResults,
    recordCustomEvent,
    getMetricHistory,
    getAverageMetric
  };
};

// Hook for component performance
export const useComponentPerformance = (componentName: string) => {
  const startTime = useRef<number>(0);
  const mountTime = useRef<number>(0);
  const updateTime = useRef<number>(0);
  const { recordCustomEvent } = usePerformanceMonitoring();

  const startRender = useCallback(() => {
    startTime.current = performance.now();
  }, []);

  const endRender = useCallback(() => {
    const renderTime = performance.now() - startTime.current;
    recordCustomEvent('component-render', renderTime, { component: componentName });
  }, [componentName, recordCustomEvent]);

  const startMount = useCallback(() => {
    mountTime.current = performance.now();
  }, []);

  const endMount = useCallback(() => {
    const mountDuration = performance.now() - mountTime.current;
    recordCustomEvent('component-mount', mountDuration, { component: componentName });
  }, [componentName, recordCustomEvent]);

  const startUpdate = useCallback(() => {
    updateTime.current = performance.now();
  }, []);

  const endUpdate = useCallback(() => {
    const updateDuration = performance.now() - updateTime.current;
    recordCustomEvent('component-update', updateDuration, { component: componentName });
  }, [componentName, recordCustomEvent]);

  return {
    startRender,
    endRender,
    startMount,
    endMount,
    startUpdate,
    endUpdate
  };
};

// Utility for measuring function performance
export const measurePerformance = <T extends (...args: any[]) => any>(
  fn: T,
  name: string
): T => {
  return ((...args: Parameters<T>): ReturnType<T> => {
    const start = performance.now();
    const result = fn(...args);
    const duration = performance.now() - start;
    
    // Record the performance event
    if (globalPerformanceObserver) {
      (globalPerformanceObserver as any).recordEvent('function-execution', duration, { function: name });
    }
    
    return result;
  }) as T;
};

// Utility for measuring async function performance
export const measureAsyncPerformance = <T extends (...args: any[]) => Promise<any>>(
  fn: T,
  name: string
): T => {
  return (async (...args: Parameters<T>): Promise<Awaited<ReturnType<T>>> => {
    const start = performance.now();
    const result = await fn(...args);
    const duration = performance.now() - start;
    
    // Record the performance event
    if (globalPerformanceObserver) {
      (globalPerformanceObserver as any).recordEvent('async-function-execution', duration, { function: name });
    }
    
    return result;
  }) as T;
};

// Performance reporting utility
export const reportPerformance = (endpoint: string, metrics: PerformanceMetrics) => {
  fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      timestamp: Date.now(),
      metrics,
      userAgent: navigator.userAgent,
      url: window.location.href
    })
  }).catch(error => {
    console.warn('Failed to report performance metrics:', error);
  });
};

// Initialize performance monitoring
export const initializePerformanceMonitoring = (thresholds?: PerformanceThresholds) => {
  if (!globalPerformanceObserver) {
    globalPerformanceObserver = new PerformanceObserver(thresholds);
  }
  return globalPerformanceObserver;
};

// Cleanup performance monitoring
export const cleanupPerformanceMonitoring = () => {
  if (globalPerformanceObserver) {
    globalPerformanceObserver.disconnect();
    globalPerformanceObserver = null;
  }
};

export default {
  PerformanceObserver,
  usePerformanceMonitoring,
  useComponentPerformance,
  measurePerformance,
  measureAsyncPerformance,
  reportPerformance,
  initializePerformanceMonitoring,
  cleanupPerformanceMonitoring
}; 
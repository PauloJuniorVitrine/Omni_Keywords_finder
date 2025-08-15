/**
 * Analytics and Usage Tracking System
 * 
 * Tracing ID: ANALYTICS_20250127_001
 * Prompt: CHECKLIST_INTERFACE_2.md - Item 4.7
 * Ruleset: enterprise_control_layer.yaml
 * Date: 2025-01-27
 */

import { useEffect, useRef, useState, useCallback } from 'react';

// Types for analytics
export interface AnalyticsEvent {
  id: string;
  type: string;
  name: string;
  timestamp: number;
  userId?: string;
  sessionId: string;
  properties?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface UserSession {
  id: string;
  startTime: number;
  lastActivity: number;
  pageViews: number;
  events: number;
  duration: number;
  referrer?: string;
  userAgent: string;
  screenResolution: string;
  language: string;
}

export interface PageView {
  id: string;
  url: string;
  title: string;
  timestamp: number;
  sessionId: string;
  userId?: string;
  referrer?: string;
  loadTime?: number;
  metadata?: Record<string, any>;
}

export interface UserBehavior {
  clicks: number;
  scrolls: number;
  formSubmissions: number;
  downloads: number;
  timeOnPage: number;
  bounceRate: number;
  conversionRate: number;
}

export interface AnalyticsConfig {
  endpoint?: string;
  batchSize?: number;
  flushInterval?: number;
  enableTracking?: boolean;
  respectPrivacy?: boolean;
  anonymizeData?: boolean;
  trackPageViews?: boolean;
  trackEvents?: boolean;
  trackUserBehavior?: boolean;
}

// Analytics service
class AnalyticsService {
  private static instance: AnalyticsService;
  private config: AnalyticsConfig;
  private events: AnalyticsEvent[] = [];
  private pageViews: PageView[] = [];
  private sessions: Map<string, UserSession> = new Map();
  private currentSession: UserSession | null = null;
  private batchQueue: AnalyticsEvent[] = [];
  private flushTimer: NodeJS.Timeout | null = null;
  private isTracking = false;

  constructor(config: AnalyticsConfig = {}) {
    this.config = {
      batchSize: 10,
      flushInterval: 30000, // 30 seconds
      enableTracking: true,
      respectPrivacy: true,
      anonymizeData: false,
      trackPageViews: true,
      trackEvents: true,
      trackUserBehavior: true,
      ...config
    };

    this.initializeSession();
    this.setupTracking();
  }

  static getInstance(config?: AnalyticsConfig): AnalyticsService {
    if (!AnalyticsService.instance) {
      AnalyticsService.instance = new AnalyticsService(config);
    }
    return AnalyticsService.instance;
  }

  private initializeSession(): void {
    const sessionId = this.generateSessionId();
    const userId = this.getUserId();
    
    this.currentSession = {
      id: sessionId,
      startTime: Date.now(),
      lastActivity: Date.now(),
      pageViews: 0,
      events: 0,
      duration: 0,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
      screenResolution: `${screen.width}x${screen.height}`,
      language: navigator.language
    };

    this.sessions.set(sessionId, this.currentSession);
    this.updateSessionActivity();
  }

  private setupTracking(): void {
    if (!this.config.enableTracking) return;

    this.isTracking = true;

    // Track page views
    if (this.config.trackPageViews) {
      this.trackPageView();
      this.setupPageViewTracking();
    }

    // Track user behavior
    if (this.config.trackUserBehavior) {
      this.setupBehaviorTracking();
    }

    // Setup batch flushing
    this.setupBatchFlushing();
  }

  private setupPageViewTracking(): void {
    // Track initial page view
    this.trackPageView();

    // Track navigation changes (for SPA)
    let currentUrl = window.location.href;
    
    const observer = new MutationObserver(() => {
      if (window.location.href !== currentUrl) {
        currentUrl = window.location.href;
        this.trackPageView();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  private setupBehaviorTracking(): void {
    // Track clicks
    document.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      this.trackEvent('click', {
        element: target.tagName.toLowerCase(),
        id: target.id,
        className: target.className,
        text: target.textContent?.substring(0, 100),
        x: event.clientX,
        y: event.clientY
      });
    });

    // Track scrolls
    let scrollTimeout: NodeJS.Timeout;
    window.addEventListener('scroll', () => {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        this.trackEvent('scroll', {
          scrollY: window.scrollY,
          scrollX: window.scrollX,
          maxScrollY: document.documentElement.scrollHeight - window.innerHeight
        });
      }, 100);
    });

    // Track form submissions
    document.addEventListener('submit', (event) => {
      const form = event.target as HTMLFormElement;
      this.trackEvent('form_submit', {
        formId: form.id,
        formAction: form.action,
        formMethod: form.method
      });
    });

    // Track downloads
    document.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      const link = target.closest('a');
      if (link && this.isDownloadLink(link.href)) {
        this.trackEvent('download', {
          url: link.href,
          filename: this.getFilenameFromUrl(link.href)
        });
      }
    });
  }

  private setupBatchFlushing(): void {
    this.flushTimer = setInterval(() => {
      this.flushEvents();
    }, this.config.flushInterval);
  }

  trackEvent(name: string, properties?: Record<string, any>, metadata?: Record<string, any>): void {
    if (!this.isTracking || !this.currentSession) return;

    const event: AnalyticsEvent = {
      id: this.generateEventId(),
      type: 'event',
      name,
      timestamp: Date.now(),
      userId: this.getUserId(),
      sessionId: this.currentSession.id,
      properties,
      metadata
    };

    this.events.push(event);
    this.batchQueue.push(event);
    this.currentSession.events++;
    this.updateSessionActivity();

    // Flush if batch is full
    if (this.batchQueue.length >= this.config.batchSize!) {
      this.flushEvents();
    }
  }

  trackPageView(metadata?: Record<string, any>): void {
    if (!this.isTracking || !this.currentSession) return;

    const pageView: PageView = {
      id: this.generateEventId(),
      url: window.location.href,
      title: document.title,
      timestamp: Date.now(),
      sessionId: this.currentSession.id,
      userId: this.getUserId(),
      referrer: document.referrer,
      metadata
    };

    this.pageViews.push(pageView);
    this.currentSession.pageViews++;
    this.updateSessionActivity();

    // Track as event too
    this.trackEvent('page_view', {
      url: pageView.url,
      title: pageView.title,
      referrer: pageView.referrer
    }, metadata);
  }

  trackUserAction(action: string, properties?: Record<string, any>): void {
    this.trackEvent(`user_action_${action}`, properties);
  }

  trackError(error: Error, context?: Record<string, any>): void {
    this.trackEvent('error', {
      message: error.message,
      stack: error.stack,
      ...context
    });
  }

  trackPerformance(metric: string, value: number, properties?: Record<string, any>): void {
    this.trackEvent('performance', {
      metric,
      value,
      ...properties
    });
  }

  private async flushEvents(): Promise<void> {
    if (this.batchQueue.length === 0 || !this.config.endpoint) return;

    const eventsToSend = [...this.batchQueue];
    this.batchQueue = [];

    try {
      const response = await fetch(this.config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          events: eventsToSend,
          session: this.currentSession,
          timestamp: Date.now()
        })
      });

      if (!response.ok) {
        console.warn('Failed to send analytics events:', response.status);
        // Re-queue failed events
        this.batchQueue.unshift(...eventsToSend);
      }
    } catch (error) {
      console.error('Error sending analytics events:', error);
      // Re-queue failed events
      this.batchQueue.unshift(...eventsToSend);
    }
  }

  private updateSessionActivity(): void {
    if (this.currentSession) {
      this.currentSession.lastActivity = Date.now();
      this.currentSession.duration = this.currentSession.lastActivity - this.currentSession.startTime;
    }
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateEventId(): string {
    return `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getUserId(): string | undefined {
    // In a real app, this would come from authentication
    return localStorage.getItem('analytics_user_id') || undefined;
  }

  private isDownloadLink(url: string): boolean {
    const downloadExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.mp4', '.mp3'];
    return downloadExtensions.some(ext => url.toLowerCase().includes(ext));
  }

  private getFilenameFromUrl(url: string): string {
    try {
      const urlObj = new URL(url);
      const pathname = urlObj.pathname;
      return pathname.split('/').pop() || 'unknown';
    } catch {
      return 'unknown';
    }
  }

  getSessionData(): UserSession | null {
    return this.currentSession;
  }

  getEvents(): AnalyticsEvent[] {
    return [...this.events];
  }

  getPageViews(): PageView[] {
    return [...this.pageViews];
  }

  getUserBehavior(): UserBehavior {
    const clicks = this.events.filter(e => e.name === 'click').length;
    const scrolls = this.events.filter(e => e.name === 'scroll').length;
    const formSubmissions = this.events.filter(e => e.name === 'form_submit').length;
    const downloads = this.events.filter(e => e.name === 'download').length;
    
    const timeOnPage = this.currentSession?.duration || 0;
    const bounceRate = this.pageViews.length <= 1 ? 100 : 0; // Simplified
    const conversionRate = 0; // Would be calculated based on business logic

    return {
      clicks,
      scrolls,
      formSubmissions,
      downloads,
      timeOnPage,
      bounceRate,
      conversionRate
    };
  }

  setUserId(userId: string): void {
    localStorage.setItem('analytics_user_id', userId);
  }

  clearUserId(): void {
    localStorage.removeItem('analytics_user_id');
  }

  enableTracking(): void {
    this.isTracking = true;
  }

  disableTracking(): void {
    this.isTracking = false;
  }

  destroy(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
    this.flushEvents();
    this.isTracking = false;
  }
}

// Global analytics instance
let globalAnalytics: AnalyticsService | null = null;

// Hook for analytics
export const useAnalytics = (config?: AnalyticsConfig) => {
  const [analytics, setAnalytics] = useState<AnalyticsService | null>(null);

  useEffect(() => {
    if (!globalAnalytics) {
      globalAnalytics = AnalyticsService.getInstance(config);
    }
    setAnalytics(globalAnalytics);
  }, [config]);

  const trackEvent = useCallback((
    name: string,
    properties?: Record<string, any>,
    metadata?: Record<string, any>
  ) => {
    analytics?.trackEvent(name, properties, metadata);
  }, [analytics]);

  const trackPageView = useCallback((metadata?: Record<string, any>) => {
    analytics?.trackPageView(metadata);
  }, [analytics]);

  const trackUserAction = useCallback((
    action: string,
    properties?: Record<string, any>
  ) => {
    analytics?.trackUserAction(action, properties);
  }, [analytics]);

  const trackError = useCallback((
    error: Error,
    context?: Record<string, any>
  ) => {
    analytics?.trackError(error, context);
  }, [analytics]);

  const trackPerformance = useCallback((
    metric: string,
    value: number,
    properties?: Record<string, any>
  ) => {
    analytics?.trackPerformance(metric, value, properties);
  }, [analytics]);

  return {
    analytics,
    trackEvent,
    trackPageView,
    trackUserAction,
    trackError,
    trackPerformance
  };
};

// Hook for component analytics
export const useComponentAnalytics = (componentName: string) => {
  const { trackEvent, trackUserAction } = useAnalytics();

  const trackComponentEvent = useCallback((
    eventName: string,
    properties?: Record<string, any>
  ) => {
    trackEvent(`component_${componentName}_${eventName}`, {
      component: componentName,
      ...properties
    });
  }, [componentName, trackEvent]);

  const trackComponentAction = useCallback((
    action: string,
    properties?: Record<string, any>
  ) => {
    trackUserAction(`${componentName}_${action}`, {
      component: componentName,
      ...properties
    });
  }, [componentName, trackUserAction]);

  return {
    trackComponentEvent,
    trackComponentAction
  };
};

// Hook for page analytics
export const usePageAnalytics = (pageName: string) => {
  const { trackPageView, trackEvent } = useAnalytics();

  useEffect(() => {
    trackPageView({ page: pageName });
  }, [pageName, trackPageView]);

  const trackPageEvent = useCallback((
    eventName: string,
    properties?: Record<string, any>
  ) => {
    trackEvent(`page_${pageName}_${eventName}`, {
      page: pageName,
      ...properties
    });
  }, [pageName, trackEvent]);

  return {
    trackPageEvent
  };
};

// Analytics provider component
export const AnalyticsProvider: React.FC<{
  config?: AnalyticsConfig;
  children: React.ReactNode;
}> = ({ config, children }) => {
  useEffect(() => {
    if (!globalAnalytics) {
      globalAnalytics = AnalyticsService.getInstance(config);
    }
  }, [config]);

  return <>{children}</>;
};

// Utility functions
export const initializeAnalytics = (config?: AnalyticsConfig): AnalyticsService => {
  if (!globalAnalytics) {
    globalAnalytics = AnalyticsService.getInstance(config);
  }
  return globalAnalytics;
};

export const getAnalytics = (): AnalyticsService | null => {
  return globalAnalytics;
};

export const destroyAnalytics = (): void => {
  globalAnalytics?.destroy();
  globalAnalytics = null;
};

export default {
  AnalyticsService,
  useAnalytics,
  useComponentAnalytics,
  usePageAnalytics,
  AnalyticsProvider,
  initializeAnalytics,
  getAnalytics,
  destroyAnalytics
}; 
/**
 * Sistema de Analytics
 * 
 * Tracing ID: COMM_CHECKLIST_20250127_004
 * Prompt: Implementação itens criticidade alta pendentes
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Responsável por tracking de eventos e comportamento do usuário
 * Integra com Google Analytics, Mixpanel, Amplitude e sistemas internos
 */

import { logger } from './logger';

// Tipos de analytics suportados
export enum AnalyticsProvider {
  GOOGLE_ANALYTICS = 'GOOGLE_ANALYTICS',
  MIXPANEL = 'MIXPANEL',
  AMPLITUDE = 'AMPLITUDE',
  INTERNAL = 'INTERNAL',
  CUSTOM = 'CUSTOM'
}

// Interface para evento de analytics
export interface AnalyticsEvent {
  id: string;
  name: string;
  category: string;
  action: string;
  label?: string;
  value?: number;
  timestamp: string;
  properties: Record<string, any>;
  context: {
    userId?: string;
    sessionId: string;
    pageUrl: string;
    userAgent: string;
    referrer?: string;
    utmSource?: string;
    utmMedium?: string;
    utmCampaign?: string;
  };
  metadata: {
    version: string;
    environment: string;
    timestamp: number;
  };
}

// Interface para configuração do analytics
export interface AnalyticsConfig {
  enabled: boolean;
  providers: AnalyticsProvider[];
  trackingId?: string;
  enablePageTracking: boolean;
  enableEventTracking: boolean;
  enableUserTracking: boolean;
  enableSessionTracking: boolean;
  enableUTMTracking: boolean;
  samplingRate: number;
  batchSize: number;
  batchTimeout: number;
  enableDebug: boolean;
  customEndpoints?: Record<AnalyticsProvider, string>;
  apiKeys?: Record<AnalyticsProvider, string>;
}

// Interface para propriedades de usuário
export interface UserProperties {
  userId: string;
  email?: string;
  name?: string;
  plan?: string;
  signupDate?: string;
  lastLogin?: string;
  preferences?: Record<string, any>;
  customProperties?: Record<string, any>;
}

// Classe principal do Analytics
export class AnalyticsService {
  private static instance: AnalyticsService;
  private config: AnalyticsConfig;
  private eventQueue: AnalyticsEvent[] = [];
  private batchTimeout: NodeJS.Timeout | null = null;
  private isProcessing = false;
  private sessionId: string;
  private userId?: string;
  private userProperties?: UserProperties;

  private constructor(config: Partial<AnalyticsConfig> = {}) {
    this.config = {
      enabled: true,
      providers: [AnalyticsProvider.GOOGLE_ANALYTICS, AnalyticsProvider.INTERNAL],
      enablePageTracking: true,
      enableEventTracking: true,
      enableUserTracking: true,
      enableSessionTracking: true,
      enableUTMTracking: true,
      samplingRate: 1.0,
      batchSize: 20,
      batchTimeout: 5000,
      enableDebug: false,
      ...config
    };

    this.sessionId = this.generateSessionId();
    this.initialize();
  }

  public static getInstance(config?: Partial<AnalyticsConfig>): AnalyticsService {
    if (!AnalyticsService.instance) {
      AnalyticsService.instance = new AnalyticsService(config);
    }
    return AnalyticsService.instance;
  }

  // Inicializar analytics
  private initialize(): void {
    if (!this.config.enabled) {
      return;
    }

    // Configurar providers
    this.config.providers.forEach(provider => {
      switch (provider) {
        case AnalyticsProvider.GOOGLE_ANALYTICS:
          this.initializeGoogleAnalytics();
          break;
        case AnalyticsProvider.MIXPANEL:
          this.initializeMixpanel();
          break;
        case AnalyticsProvider.AMPLITUDE:
          this.initializeAmplitude();
          break;
        case AnalyticsProvider.INTERNAL:
          this.initializeInternal();
          break;
      }
    });

    // Configurar tracking de página
    if (this.config.enablePageTracking) {
      this.setupPageTracking();
    }

    // Configurar tracking de UTM
    if (this.config.enableUTMTracking) {
      this.setupUTMTracking();
    }

    logger.info('[ANALYTICS] Service initialized', {
      sessionId: this.sessionId,
      providers: this.config.providers
    });
  }

  // Inicializar Google Analytics
  private initializeGoogleAnalytics(): void {
    if (typeof window !== 'undefined' && window.gtag) {
      // Configurar GA4
      window.gtag('config', this.config.trackingId || 'GA_TRACKING_ID', {
        page_title: document.title,
        page_location: window.location.href,
        custom_map: {
          user_id: 'user_id',
          session_id: 'session_id'
        }
      });

      logger.info('[ANALYTICS] Google Analytics initialized');
    } else {
      logger.warn('[ANALYTICS] Google Analytics not available');
    }
  }

  // Inicializar Mixpanel
  private initializeMixpanel(): void {
    if (typeof window !== 'undefined' && window.mixpanel) {
      window.mixpanel.init(this.config.apiKeys?.[AnalyticsProvider.MIXPANEL] || 'MIXPANEL_TOKEN');
      logger.info('[ANALYTICS] Mixpanel initialized');
    } else {
      logger.warn('[ANALYTICS] Mixpanel not available');
    }
  }

  // Inicializar Amplitude
  private initializeAmplitude(): void {
    if (typeof window !== 'undefined' && window.amplitude) {
      window.amplitude.getInstance().init(this.config.apiKeys?.[AnalyticsProvider.AMPLITUDE] || 'AMPLITUDE_API_KEY');
      logger.info('[ANALYTICS] Amplitude initialized');
    } else {
      logger.warn('[ANALYTICS] Amplitude not available');
    }
  }

  // Inicializar sistema interno
  private initializeInternal(): void {
    logger.info('[ANALYTICS] Internal analytics system initialized');
  }

  // Configurar tracking de página
  private setupPageTracking(): void {
    // Track mudanças de rota
    const originalPushState = history.pushState;
    const originalReplaceState = history.replaceState;

    history.pushState = (...args) => {
      originalPushState.apply(history, args);
      this.trackPageView(window.location.pathname);
    };

    history.replaceState = (...args) => {
      originalReplaceState.apply(history, args);
      this.trackPageView(window.location.pathname);
    };

    // Track popstate
    window.addEventListener('popstate', () => {
      this.trackPageView(window.location.pathname);
    });

    // Track página inicial
    this.trackPageView(window.location.pathname);
  }

  // Configurar tracking de UTM
  private setupUTMTracking(): void {
    const urlParams = new URLSearchParams(window.location.search);
    const utmParams = {
      utmSource: urlParams.get('utm_source'),
      utmMedium: urlParams.get('utm_medium'),
      utmCampaign: urlParams.get('utm_campaign'),
      utmTerm: urlParams.get('utm_term'),
      utmContent: urlParams.get('utm_content')
    };

    // Armazenar UTM params na sessão
    if (Object.values(utmParams).some(param => param)) {
      sessionStorage.setItem('utm_params', JSON.stringify(utmParams));
    }
  }

  // Track evento
  public track(
    name: string,
    category: string,
    action: string,
    properties: Record<string, any> = {},
    label?: string,
    value?: number
  ): void {
    if (!this.config.enabled || !this.config.enableEventTracking) {
      return;
    }

    // Verificar sampling
    if (Math.random() > this.config.samplingRate) {
      return;
    }

    const event: AnalyticsEvent = {
      id: this.generateEventId(),
      name,
      category,
      action,
      label,
      value,
      timestamp: new Date().toISOString(),
      properties: {
        ...properties,
        category,
        action,
        label,
        value
      },
      context: {
        userId: this.userId,
        sessionId: this.sessionId,
        pageUrl: window.location.href,
        userAgent: navigator.userAgent,
        referrer: document.referrer,
        ...this.getUTMParams()
      },
      metadata: {
        version: process.env.REACT_APP_VERSION || 'unknown',
        environment: process.env.NODE_ENV || 'development',
        timestamp: Date.now()
      }
    };

    this.eventQueue.push(event);

    // Processar se atingiu batch size
    if (this.eventQueue.length >= this.config.batchSize) {
      this.processBatch();
    } else if (!this.batchTimeout) {
      // Agendar processamento
      this.batchTimeout = setTimeout(() => {
        this.processBatch();
      }, this.config.batchTimeout);
    }

    // Log do evento
    if (this.config.enableDebug) {
      logger.debug('[ANALYTICS] Event tracked', {
        name,
        category,
        action,
        properties
      });
    }
  }

  // Track visualização de página
  public trackPageView(path: string, title?: string): void {
    if (!this.config.enablePageTracking) {
      return;
    }

    this.track('page_view', 'navigation', 'view', {
      path,
      title: title || document.title,
      referrer: document.referrer
    }, path);

    // Enviar para Google Analytics
    if (window.gtag) {
      window.gtag('config', this.config.trackingId || 'GA_TRACKING_ID', {
        page_title: title || document.title,
        page_location: window.location.origin + path
      });
    }
  }

  // Track evento de conversão
  public trackConversion(
    conversionType: string,
    value?: number,
    properties: Record<string, any> = {}
  ): void {
    this.track('conversion', 'conversion', conversionType, {
      ...properties,
      conversionType,
      value
    }, conversionType, value);
  }

  // Track evento de erro
  public trackError(
    errorType: string,
    errorMessage: string,
    properties: Record<string, any> = {}
  ): void {
    this.track('error', 'error', errorType, {
      ...properties,
      errorType,
      errorMessage
    }, errorType);
  }

  // Track evento de performance
  public trackPerformance(
    metricName: string,
    value: number,
    unit: string,
    properties: Record<string, any> = {}
  ): void {
    this.track('performance', 'performance', metricName, {
      ...properties,
      metricName,
      value,
      unit
    }, metricName, value);
  }

  // Track evento de usuário
  public trackUserAction(
    action: string,
    properties: Record<string, any> = {}
  ): void {
    this.track('user_action', 'user', action, properties, action);
  }

  // Identificar usuário
  public identify(userId: string, properties?: Partial<UserProperties>): void {
    if (!this.config.enableUserTracking) {
      return;
    }

    this.userId = userId;
    this.userProperties = {
      userId,
      ...properties
    };

    // Enviar para providers
    if (window.gtag) {
      window.gtag('config', this.config.trackingId || 'GA_TRACKING_ID', {
        user_id: userId
      });
    }

    if (window.mixpanel) {
      window.mixpanel.identify(userId);
      if (properties) {
        window.mixpanel.people.set(properties);
      }
    }

    if (window.amplitude) {
      window.amplitude.getInstance().setUserId(userId);
      if (properties) {
        window.amplitude.getInstance().setUserProperties(properties);
      }
    }

    logger.info('[ANALYTICS] User identified', { userId, properties });
  }

  // Definir propriedades do usuário
  public setUserProperties(properties: Partial<UserProperties>): void {
    if (!this.config.enableUserTracking || !this.userId) {
      return;
    }

    this.userProperties = {
      ...this.userProperties,
      ...properties
    };

    // Enviar para providers
    if (window.mixpanel) {
      window.mixpanel.people.set(properties);
    }

    if (window.amplitude) {
      window.amplitude.getInstance().setUserProperties(properties);
    }

    logger.info('[ANALYTICS] User properties set', { properties });
  }

  // Processar lote de eventos
  private async processBatch(): Promise<void> {
    if (this.isProcessing || this.eventQueue.length === 0) {
      return;
    }

    this.isProcessing = true;

    // Limpar timeout
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }

    const batch = this.eventQueue.splice(0, this.config.batchSize);

    try {
      // Enviar para todos os providers
      const promises = this.config.providers.map(provider => 
        this.sendToProvider(provider, batch)
      );

      await Promise.allSettled(promises);

      logger.info('[ANALYTICS] Batch processed successfully', {
        batchSize: batch.length,
        remainingInQueue: this.eventQueue.length
      });

    } catch (error) {
      logger.error('[ANALYTICS] Failed to process batch', { error });
      
      // Recolocar eventos na fila para retry
      this.eventQueue.unshift(...batch);
    } finally {
      this.isProcessing = false;

      // Processar próximo lote se houver
      if (this.eventQueue.length > 0) {
        setTimeout(() => this.processBatch(), 1000);
      }
    }
  }

  // Enviar para provider específico
  private async sendToProvider(provider: AnalyticsProvider, events: AnalyticsEvent[]): Promise<void> {
    try {
      switch (provider) {
        case AnalyticsProvider.GOOGLE_ANALYTICS:
          await this.sendToGoogleAnalytics(events);
          break;
        case AnalyticsProvider.MIXPANEL:
          await this.sendToMixpanel(events);
          break;
        case AnalyticsProvider.AMPLITUDE:
          await this.sendToAmplitude(events);
          break;
        case AnalyticsProvider.INTERNAL:
          await this.sendToInternal(events);
          break;
        case AnalyticsProvider.CUSTOM:
          await this.sendToCustom(events);
          break;
      }
    } catch (error) {
      logger.error(`[ANALYTICS] Failed to send to ${provider}`, { error });
      throw error;
    }
  }

  // Enviar para Google Analytics
  private async sendToGoogleAnalytics(events: AnalyticsEvent[]): Promise<void> {
    if (!window.gtag) {
      throw new Error('Google Analytics not available');
    }

    events.forEach(event => {
      window.gtag('event', event.name, {
        event_category: event.category,
        event_label: event.label,
        value: event.value,
        custom_parameters: event.properties,
        user_id: event.context.userId,
        session_id: event.context.sessionId
      });
    });
  }

  // Enviar para Mixpanel
  private async sendToMixpanel(events: AnalyticsEvent[]): Promise<void> {
    if (!window.mixpanel) {
      throw new Error('Mixpanel not available');
    }

    events.forEach(event => {
      window.mixpanel.track(event.name, {
        ...event.properties,
        category: event.category,
        action: event.action,
        label: event.label,
        value: event.value,
        userId: event.context.userId,
        sessionId: event.context.sessionId
      });
    });
  }

  // Enviar para Amplitude
  private async sendToAmplitude(events: AnalyticsEvent[]): Promise<void> {
    if (!window.amplitude) {
      throw new Error('Amplitude not available');
    }

    events.forEach(event => {
      window.amplitude.getInstance().logEvent(event.name, {
        ...event.properties,
        category: event.category,
        action: event.action,
        label: event.label,
        value: event.value,
        userId: event.context.userId,
        sessionId: event.context.sessionId
      });
    });
  }

  // Enviar para sistema interno
  private async sendToInternal(events: AnalyticsEvent[]): Promise<void> {
    const endpoint = this.config.customEndpoints?.[AnalyticsProvider.INTERNAL] || '/api/analytics';

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAuthToken()}`
      },
      body: JSON.stringify({
        events,
        sessionId: this.sessionId,
        timestamp: new Date().toISOString()
      })
    });

    if (!response.ok) {
      throw new Error(`Internal analytics failed: ${response.status}`);
    }
  }

  // Enviar para sistema customizado
  private async sendToCustom(events: AnalyticsEvent[]): Promise<void> {
    const endpoint = this.config.customEndpoints?.[AnalyticsProvider.CUSTOM];
    
    if (!endpoint) {
      throw new Error('Custom endpoint not configured');
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.apiKeys?.[AnalyticsProvider.CUSTOM]}`
      },
      body: JSON.stringify({
        events,
        sessionId: this.sessionId,
        timestamp: new Date().toISOString()
      })
    });

    if (!response.ok) {
      throw new Error(`Custom analytics failed: ${response.status}`);
    }
  }

  // Utilitários
  private generateEventId(): string {
    return `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateSessionId(): string {
    let sessionId = sessionStorage.getItem('analytics_session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('analytics_session_id', sessionId);
    }
    return sessionId;
  }

  private getUTMParams(): Record<string, string | null> {
    try {
      const utmParams = sessionStorage.getItem('utm_params');
      return utmParams ? JSON.parse(utmParams) : {};
    } catch {
      return {};
    }
  }

  private getAuthToken(): string {
    return localStorage.getItem('authToken') || '';
  }

  // Métodos públicos
  public flush(): Promise<void> {
    return this.processBatch();
  }

  public updateConfig(newConfig: Partial<AnalyticsConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  public getConfig(): AnalyticsConfig {
    return { ...this.config };
  }

  public getQueueSize(): number {
    return this.eventQueue.length;
  }

  public clearQueue(): void {
    this.eventQueue = [];
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }
  }

  public getUserId(): string | undefined {
    return this.userId;
  }

  public getUserProperties(): UserProperties | undefined {
    return this.userProperties;
  }
}

// Instância singleton
export const analytics = AnalyticsService.getInstance();

// Hook para usar analytics
export const useAnalytics = () => {
  return analytics;
};

// Hook para tracking de eventos
export const useAnalyticsTracking = () => {
  const track = (name: string, category: string, action: string, properties?: Record<string, any>, label?: string, value?: number) => {
    analytics.track(name, category, action, properties, label, value);
  };

  const trackPageView = (path: string, title?: string) => {
    analytics.trackPageView(path, title);
  };

  const trackConversion = (conversionType: string, value?: number, properties?: Record<string, any>) => {
    analytics.trackConversion(conversionType, value, properties);
  };

  const trackError = (errorType: string, errorMessage: string, properties?: Record<string, any>) => {
    analytics.trackError(errorType, errorMessage, properties);
  };

  const trackPerformance = (metricName: string, value: number, unit: string, properties?: Record<string, any>) => {
    analytics.trackPerformance(metricName, value, unit, properties);
  };

  const trackUserAction = (action: string, properties?: Record<string, any>) => {
    analytics.trackUserAction(action, properties);
  };

  return {
    track,
    trackPageView,
    trackConversion,
    trackError,
    trackPerformance,
    trackUserAction
  };
};

export default analytics; 
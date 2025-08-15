/**
 * OpenTelemetry Client for Frontend
 * Tracing ID: FINE_TUNING_IMPLEMENTATION_20250127_001
 * Created: 2025-01-27
 * Version: 1.0
 * 
 * This module provides OpenTelemetry client functionality for the frontend,
 * including correlation ID propagation, span creation, and integration with React hooks.
 */

import { trace, context, SpanStatusCode, SpanKind } from '@opentelemetry/api';
import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch';
import { XMLHttpRequestInstrumentation } from '@opentelemetry/instrumentation-xml-http-request';
import { DocumentLoadInstrumentation } from '@opentelemetry/instrumentation-document-load';
import { UserInteractionInstrumentation } from '@opentelemetry/instrumentation-user-interaction';

// Types
export interface TracingConfig {
  serviceName: string;
  serviceVersion: string;
  environment: string;
  endpoint?: string;
  samplingRate?: number;
}

export interface SpanAttributes {
  [key: string]: string | number | boolean;
}

export interface TracingContext {
  correlationId: string;
  traceId: string;
  spanId: string;
}

// Global tracer instance
let tracer: ReturnType<typeof trace.getTracer> | null = null;
let currentCorrelationId: string | null = null;

/**
 * Initialize OpenTelemetry tracing for the frontend
 */
export function initializeTracing(config: TracingConfig): void {
  try {
    // Create resource with service information
    const resource = new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: config.serviceName,
      [SemanticResourceAttributes.SERVICE_VERSION]: config.serviceVersion,
      [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: config.environment,
    });

    // Create tracer provider
    const provider = new WebTracerProvider({
      resource,
    });

    // Configure exporters
    const exporters = [];

    // Add OTLP exporter if endpoint is provided
    if (config.endpoint) {
      exporters.push(
        new OTLPTraceExporter({
          url: `${config.endpoint}/v1/traces`,
          headers: {
            'Content-Type': 'application/json',
          },
        })
      );
    }

    // Add span processors
    exporters.forEach((exporter) => {
      provider.addSpanProcessor(new BatchSpanProcessor(exporter));
    });

    // Register the provider
    trace.setGlobalTracerProvider(provider);

    // Register instrumentations
    registerInstrumentations({
      instrumentations: [
        new FetchInstrumentation({
          propagateTraceHeaderCorsUrls: [/.*/],
          clearTimingResources: true,
        }),
        new XMLHttpRequestInstrumentation({
          propagateTraceHeaderCorsUrls: [/.*/],
        }),
        new DocumentLoadInstrumentation(),
        new UserInteractionInstrumentation(),
      ],
    });

    // Get tracer
    tracer = trace.getTracer(config.serviceName);

    console.info('OpenTelemetry tracing initialized for frontend');
  } catch (error) {
    console.error('Failed to initialize OpenTelemetry tracing:', error);
  }
}

/**
 * Generate a new correlation ID
 */
export function generateCorrelationId(): string {
  return `frontend-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Set the current correlation ID
 */
export function setCorrelationId(correlationId: string): void {
  currentCorrelationId = correlationId;
  
  // Store in session storage for persistence
  if (typeof window !== 'undefined') {
    sessionStorage.setItem('correlation_id', correlationId);
  }
}

/**
 * Get the current correlation ID
 */
export function getCorrelationId(): string | null {
  if (currentCorrelationId) {
    return currentCorrelationId;
  }

  // Try to get from session storage
  if (typeof window !== 'undefined') {
    const stored = sessionStorage.getItem('correlation_id');
    if (stored) {
      currentCorrelationId = stored;
      return stored;
    }
  }

  return null;
}

/**
 * Create a new span for an operation
 */
export function createSpan(
  operationName: string,
  attributes: SpanAttributes = {},
  kind: SpanKind = SpanKind.INTERNAL
): ReturnType<typeof trace.getTracer>['startSpan'] | null {
  if (!tracer) {
    console.warn('Tracer not initialized');
    return null;
  }

  const correlationId = getCorrelationId();
  const spanAttributes = {
    ...attributes,
    'operation.name': operationName,
    'service.type': 'frontend',
  };

  if (correlationId) {
    spanAttributes['correlation_id'] = correlationId;
  }

  return tracer.startSpan(operationName, {
    kind,
    attributes: spanAttributes,
  });
}

/**
 * Trace an operation with automatic span management
 */
export async function traceOperation<T>(
  operationName: string,
  operation: () => Promise<T> | T,
  attributes: SpanAttributes = {}
): Promise<T> {
  const span = createSpan(operationName, attributes);
  
  if (!span) {
    // Fallback if tracing is not available
    return await operation();
  }

  try {
    const result = await operation();
    span.setStatus({ code: SpanStatusCode.OK });
    return result;
  } catch (error) {
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error instanceof Error ? error.message : String(error),
    });
    span.recordException(error as Error);
    throw error;
  } finally {
    span.end();
  }
}

/**
 * Trace API calls with automatic correlation ID propagation
 */
export async function traceApiCall<T>(
  url: string,
  options: RequestInit = {},
  operationName?: string
): Promise<T> {
  const correlationId = getCorrelationId();
  const opName = operationName || `api.${options.method || 'GET'}`;

  // Add correlation ID to headers
  const headers = new Headers(options.headers);
  if (correlationId) {
    headers.set('X-Correlation-ID', correlationId);
    headers.set('X-Request-ID', correlationId);
  }

  const span = createSpan(opName, {
    'http.url': url,
    'http.method': options.method || 'GET',
    'http.target': new URL(url).pathname,
  }, SpanKind.CLIENT);

  if (!span) {
    // Fallback if tracing is not available
    const response = await fetch(url, { ...options, headers });
    return response.json();
  }

  try {
    const startTime = performance.now();
    const response = await fetch(url, { ...options, headers });
    const duration = performance.now() - startTime;

    span.setAttributes({
      'http.status_code': response.status,
      'http.duration': duration,
    });

    if (response.ok) {
      span.setStatus({ code: SpanStatusCode.OK });
      const result = await response.json();
      return result;
    } else {
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: `HTTP ${response.status}`,
      });
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  } catch (error) {
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error instanceof Error ? error.message : String(error),
    });
    span.recordException(error as Error);
    throw error;
  } finally {
    span.end();
  }
}

/**
 * Trace user interactions
 */
export function traceUserInteraction(
  element: string,
  action: string,
  attributes: SpanAttributes = {}
): void {
  const span = createSpan(`user.interaction.${action}`, {
    'ui.element': element,
    'ui.action': action,
    ...attributes,
  }, SpanKind.INTERNAL);

  if (span) {
    span.setStatus({ code: SpanStatusCode.OK });
    span.end();
  }
}

/**
 * Trace component lifecycle events
 */
export function traceComponentLifecycle(
  componentName: string,
  lifecycle: 'mount' | 'unmount' | 'update',
  attributes: SpanAttributes = {}
): void {
  const span = createSpan(`component.${lifecycle}`, {
    'component.name': componentName,
    'component.lifecycle': lifecycle,
    ...attributes,
  }, SpanKind.INTERNAL);

  if (span) {
    span.setStatus({ code: SpanStatusCode.OK });
    span.end();
  }
}

/**
 * Trace performance metrics
 */
export function tracePerformance(
  metricName: string,
  value: number,
  unit: string = 'ms',
  attributes: SpanAttributes = {}
): void {
  const span = createSpan(`performance.${metricName}`, {
    'performance.metric': metricName,
    'performance.value': value,
    'performance.unit': unit,
    ...attributes,
  }, SpanKind.INTERNAL);

  if (span) {
    span.setStatus({ code: SpanStatusCode.OK });
    span.end();
  }
}

/**
 * Get current tracing context
 */
export function getTracingContext(): TracingContext | null {
  const correlationId = getCorrelationId();
  if (!correlationId || !tracer) {
    return null;
  }

  const currentSpan = trace.getActiveSpan();
  if (!currentSpan) {
    return null;
  }

  const spanContext = currentSpan.spanContext();
  
  return {
    correlationId,
    traceId: spanContext.traceId,
    spanId: spanContext.spanId,
  };
}

/**
 * Add attributes to the current span
 */
export function addSpanAttributes(attributes: SpanAttributes): void {
  const currentSpan = trace.getActiveSpan();
  if (currentSpan) {
    Object.entries(attributes).forEach(([key, value]) => {
      currentSpan.setAttribute(key, value);
    });
  }
}

/**
 * Add an event to the current span
 */
export function addSpanEvent(
  name: string,
  attributes: SpanAttributes = {}
): void {
  const currentSpan = trace.getActiveSpan();
  if (currentSpan) {
    currentSpan.addEvent(name, attributes);
  }
}

/**
 * React Hook for tracing component operations
 */
export function useTracing() {
  return {
    traceOperation,
    traceApiCall,
    traceUserInteraction,
    traceComponentLifecycle,
    tracePerformance,
    getCorrelationId,
    setCorrelationId,
    getTracingContext,
    addSpanAttributes,
    addSpanEvent,
  };
}

/**
 * Higher-order component for automatic component tracing
 */
export function withTracing<P extends object>(
  Component: React.ComponentType<P>,
  componentName?: string
): React.ComponentType<P> {
  const WrappedComponent = (props: P) => {
    const name = componentName || Component.displayName || Component.name;
    
    React.useEffect(() => {
      traceComponentLifecycle(name, 'mount');
      return () => {
        traceComponentLifecycle(name, 'unmount');
      };
    }, []);

    return React.createElement(Component, props);
  };

  WrappedComponent.displayName = `withTracing(${name})`;
  return WrappedComponent;
}

/**
 * Initialize correlation ID on app startup
 */
export function initializeCorrelationId(): void {
  // Generate new correlation ID if none exists
  if (!getCorrelationId()) {
    const newCorrelationId = generateCorrelationId();
    setCorrelationId(newCorrelationId);
  }
}

/**
 * Export tracing headers for external requests
 */
export function getTracingHeaders(): Record<string, string> {
  const correlationId = getCorrelationId();
  const headers: Record<string, string> = {};

  if (correlationId) {
    headers['X-Correlation-ID'] = correlationId;
    headers['X-Request-ID'] = correlationId;
  }

  return headers;
}

// Auto-initialize correlation ID when module is loaded
if (typeof window !== 'undefined') {
  initializeCorrelationId();
} 
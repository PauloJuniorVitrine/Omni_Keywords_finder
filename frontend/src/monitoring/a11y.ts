/**
 * Accessibility Metrics and Monitoring System
 * 
 * Tracing ID: A11Y_METRICS_20250127_001
 * Prompt: CHECKLIST_INTERFACE_2.md - Item 4.8
 * Ruleset: enterprise_control_layer.yaml
 * Date: 2025-01-27
 */

import { useEffect, useState, useCallback, useRef } from 'react';

// Types for accessibility monitoring
export interface A11yMetrics {
  // WCAG Compliance
  wcagAA: number; // Percentage compliance with WCAG 2.1 AA
  wcagAAA: number; // Percentage compliance with WCAG 2.1 AAA
  
  // Core metrics
  contrastRatio: number; // Average contrast ratio
  focusableElements: number; // Number of focusable elements
  keyboardNavigable: number; // Percentage of elements keyboard navigable
  screenReaderCompatible: number; // Percentage of elements screen reader compatible
  
  // ARIA metrics
  ariaLabels: number; // Elements with ARIA labels
  ariaDescribedby: number; // Elements with aria-describedby
  ariaLabelledby: number; // Elements with aria-labelledby
  ariaRequired: number; // Required form elements with aria-required
  
  // Semantic HTML
  semanticElements: number; // Number of semantic HTML elements
  headingStructure: number; // Proper heading hierarchy (1-6)
  landmarkRoles: number; // Number of landmark roles
  
  // Color and visual
  colorDependentInfo: number; // Elements that don't rely solely on color
  textResizable: number; // Percentage of text that can be resized
  sufficientSpacing: number; // Elements with sufficient touch targets
  
  // Form accessibility
  formLabels: number; // Form elements with proper labels
  errorIndication: number; // Forms with proper error indication
  fieldsetUsage: number; // Proper use of fieldset elements
  
  // Media accessibility
  imageAltText: number; // Images with alt text
  videoCaptions: number; // Videos with captions
  audioTranscripts: number; // Audio with transcripts
}

export interface A11yIssue {
  id: string;
  type: 'error' | 'warning' | 'info';
  rule: string;
  element: string;
  message: string;
  impact: 'critical' | 'serious' | 'moderate' | 'minor';
  wcagLevel: 'A' | 'AA' | 'AAA';
  timestamp: number;
  selector?: string;
  suggestions?: string[];
}

export interface A11yReport {
  timestamp: number;
  url: string;
  metrics: A11yMetrics;
  issues: A11yIssue[];
  summary: {
    totalIssues: number;
    criticalIssues: number;
    seriousIssues: number;
    moderateIssues: number;
    minorIssues: number;
    complianceScore: number;
  };
}

export interface A11yConfig {
  enableMonitoring?: boolean;
  checkInterval?: number;
  reportEndpoint?: string;
  includeWarnings?: boolean;
  includeInfo?: boolean;
  wcagLevel?: 'A' | 'AA' | 'AAA';
  customRules?: A11yRule[];
}

export interface A11yRule {
  id: string;
  name: string;
  description: string;
  selector: string;
  test: (element: Element) => boolean;
  impact: 'critical' | 'serious' | 'moderate' | 'minor';
  wcagLevel: 'A' | 'AA' | 'AAA';
}

// Accessibility monitoring service
class A11yMonitor {
  private static instance: A11yMonitor;
  private config: A11yConfig;
  private metrics: A11yMetrics;
  private issues: A11yIssue[] = [];
  private checkInterval: NodeJS.Timeout | null = null;
  private isMonitoring = false;
  private listeners: Set<(report: A11yReport) => void> = new Set();

  constructor(config: A11yConfig = {}) {
    this.config = {
      enableMonitoring: true,
      checkInterval: 5000, // 5 seconds
      includeWarnings: true,
      includeInfo: false,
      wcagLevel: 'AA',
      ...config
    };

    this.metrics = this.initializeMetrics();
  }

  static getInstance(config?: A11yConfig): A11yMonitor {
    if (!A11yMonitor.instance) {
      A11yMonitor.instance = new A11yMonitor(config);
    }
    return A11yMonitor.instance;
  }

  private initializeMetrics(): A11yMetrics {
    return {
      wcagAA: 0,
      wcagAAA: 0,
      contrastRatio: 0,
      focusableElements: 0,
      keyboardNavigable: 0,
      screenReaderCompatible: 0,
      ariaLabels: 0,
      ariaDescribedby: 0,
      ariaLabelledby: 0,
      ariaRequired: 0,
      semanticElements: 0,
      headingStructure: 0,
      landmarkRoles: 0,
      colorDependentInfo: 0,
      textResizable: 0,
      sufficientSpacing: number,
      formLabels: 0,
      errorIndication: 0,
      fieldsetUsage: 0,
      imageAltText: 0,
      videoCaptions: 0,
      audioTranscripts: 0
    };
  }

  startMonitoring(): void {
    if (this.isMonitoring) return;

    this.isMonitoring = true;
    this.runAccessibilityCheck();

    if (this.config.checkInterval) {
      this.checkInterval = setInterval(() => {
        this.runAccessibilityCheck();
      }, this.config.checkInterval);
    }
  }

  stopMonitoring(): void {
    this.isMonitoring = false;
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
  }

  private runAccessibilityCheck(): void {
    this.issues = [];
    this.metrics = this.initializeMetrics();

    // Run all accessibility checks
    this.checkWCAGCompliance();
    this.checkContrastRatios();
    this.checkFocusableElements();
    this.checkARIAUsage();
    this.checkSemanticHTML();
    this.checkFormAccessibility();
    this.checkMediaAccessibility();

    // Generate report
    const report = this.generateReport();

    // Notify listeners
    this.listeners.forEach(listener => listener(report));

    // Send report to endpoint if configured
    if (this.config.reportEndpoint) {
      this.sendReport(report);
    }
  }

  private checkWCAGCompliance(): void {
    const totalElements = document.querySelectorAll('*').length;
    let compliantElements = 0;
    let aaCompliant = 0;
    let aaaCompliant = 0;

    document.querySelectorAll('*').forEach(element => {
      const isCompliant = this.checkElementCompliance(element);
      if (isCompliant) {
        compliantElements++;
        aaCompliant++;
        aaaCompliant++;
      }
    });

    this.metrics.wcagAA = totalElements > 0 ? (aaCompliant / totalElements) * 100 : 0;
    this.metrics.wcagAAA = totalElements > 0 ? (aaaCompliant / totalElements) * 100 : 0;
  }

  private checkElementCompliance(element: Element): boolean {
    // Basic compliance check
    const hasAriaLabel = element.hasAttribute('aria-label') || element.hasAttribute('aria-labelledby');
    const hasAltText = element.tagName === 'IMG' ? element.hasAttribute('alt') : true;
    const hasRole = element.hasAttribute('role');
    const isFocusable = this.isElementFocusable(element);
    const hasKeyboardSupport = this.hasKeyboardSupport(element);

    return hasAriaLabel && hasAltText && (hasRole || isFocusable) && hasKeyboardSupport;
  }

  private checkContrastRatios(): void {
    let totalContrast = 0;
    let elementCount = 0;

    document.querySelectorAll('*').forEach(element => {
      const contrast = this.calculateContrastRatio(element);
      if (contrast > 0) {
        totalContrast += contrast;
        elementCount++;
      }
    });

    this.metrics.contrastRatio = elementCount > 0 ? totalContrast / elementCount : 0;
  }

  private calculateContrastRatio(element: Element): number {
    const styles = window.getComputedStyle(element);
    const backgroundColor = styles.backgroundColor;
    const color = styles.color;

    // Simplified contrast calculation
    // In a real implementation, you'd use a proper color contrast library
    return 4.5; // Placeholder value
  }

  private checkFocusableElements(): void {
    const focusableElements = document.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    this.metrics.focusableElements = focusableElements.length;

    let keyboardNavigable = 0;
    focusableElements.forEach(element => {
      if (this.hasKeyboardSupport(element)) {
        keyboardNavigable++;
      }
    });

    this.metrics.keyboardNavigable = focusableElements.length > 0 
      ? (keyboardNavigable / focusableElements.length) * 100 
      : 0;
  }

  private isElementFocusable(element: Element): boolean {
    const tagName = element.tagName.toLowerCase();
    const tabIndex = element.getAttribute('tabindex');
    
    return (
      tagName === 'button' ||
      tagName === 'input' ||
      tagName === 'select' ||
      tagName === 'textarea' ||
      tagName === 'a' ||
      tabIndex !== null
    );
  }

  private hasKeyboardSupport(element: Element): boolean {
    // Check if element has keyboard event handlers
    const hasKeyDown = element.hasAttribute('onkeydown');
    const hasKeyUp = element.hasAttribute('onkeyup');
    const hasKeyPress = element.hasAttribute('onkeypress');
    
    return hasKeyDown || hasKeyUp || hasKeyPress;
  }

  private checkARIAUsage(): void {
    const elementsWithAriaLabel = document.querySelectorAll('[aria-label]');
    const elementsWithAriaDescribedby = document.querySelectorAll('[aria-describedby]');
    const elementsWithAriaLabelledby = document.querySelectorAll('[aria-labelledby]');
    const elementsWithAriaRequired = document.querySelectorAll('[aria-required="true"]');

    this.metrics.ariaLabels = elementsWithAriaLabel.length;
    this.metrics.ariaDescribedby = elementsWithAriaDescribedby.length;
    this.metrics.ariaLabelledby = elementsWithAriaLabelledby.length;
    this.metrics.ariaRequired = elementsWithAriaRequired.length;
  }

  private checkSemanticHTML(): void {
    const semanticElements = document.querySelectorAll(
      'header, nav, main, article, section, aside, footer, figure, figcaption, time, mark, details, summary'
    );
    
    this.metrics.semanticElements = semanticElements.length;

    // Check heading structure
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    let properStructure = 0;
    let currentLevel = 0;

    headings.forEach(heading => {
      const level = parseInt(heading.tagName.charAt(1));
      if (level <= currentLevel + 1) {
        properStructure++;
        currentLevel = level;
      }
    });

    this.metrics.headingStructure = headings.length > 0 
      ? (properStructure / headings.length) * 100 
      : 0;

    // Check landmark roles
    const landmarks = document.querySelectorAll(
      '[role="banner"], [role="navigation"], [role="main"], [role="complementary"], [role="contentinfo"]'
    );
    this.metrics.landmarkRoles = landmarks.length;
  }

  private checkFormAccessibility(): void {
    const forms = document.querySelectorAll('form');
    let formsWithLabels = 0;
    let formsWithErrors = 0;
    let formsWithFieldsets = 0;

    forms.forEach(form => {
      const inputs = form.querySelectorAll('input, select, textarea');
      const labels = form.querySelectorAll('label');
      const errors = form.querySelectorAll('[aria-invalid="true"], .error, .invalid');
      const fieldsets = form.querySelectorAll('fieldset');

      if (inputs.length === labels.length) {
        formsWithLabels++;
      }
      if (errors.length > 0) {
        formsWithErrors++;
      }
      if (fieldsets.length > 0) {
        formsWithFieldsets++;
      }
    });

    this.metrics.formLabels = formsWithLabels;
    this.metrics.errorIndication = formsWithErrors;
    this.metrics.fieldsetUsage = formsWithFieldsets;
  }

  private checkMediaAccessibility(): void {
    const images = document.querySelectorAll('img');
    const videos = document.querySelectorAll('video');
    const audios = document.querySelectorAll('audio');

    let imagesWithAlt = 0;
    images.forEach(img => {
      if (img.hasAttribute('alt')) {
        imagesWithAlt++;
      }
    });

    let videosWithCaptions = 0;
    videos.forEach(video => {
      const tracks = video.querySelectorAll('track');
      if (tracks.length > 0) {
        videosWithCaptions++;
      }
    });

    let audiosWithTranscripts = 0;
    audios.forEach(audio => {
      // Check for transcript links or descriptions
      const hasTranscript = audio.hasAttribute('aria-describedby') || 
                           audio.closest('[data-transcript]');
      if (hasTranscript) {
        audiosWithTranscripts++;
      }
    });

    this.metrics.imageAltText = imagesWithAlt;
    this.metrics.videoCaptions = videosWithCaptions;
    this.metrics.audioTranscripts = audiosWithTranscripts;
  }

  private generateReport(): A11yReport {
    const criticalIssues = this.issues.filter(i => i.impact === 'critical').length;
    const seriousIssues = this.issues.filter(i => i.impact === 'serious').length;
    const moderateIssues = this.issues.filter(i => i.impact === 'moderate').length;
    const minorIssues = this.issues.filter(i => i.impact === 'minor').length;

    const complianceScore = Math.max(0, 100 - (criticalIssues * 10) - (seriousIssues * 5) - (moderateIssues * 2) - minorIssues);

    return {
      timestamp: Date.now(),
      url: window.location.href,
      metrics: { ...this.metrics },
      issues: [...this.issues],
      summary: {
        totalIssues: this.issues.length,
        criticalIssues,
        seriousIssues,
        moderateIssues,
        minorIssues,
        complianceScore
      }
    };
  }

  private async sendReport(report: A11yReport): Promise<void> {
    if (!this.config.reportEndpoint) return;

    try {
      await fetch(this.config.reportEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(report)
      });
    } catch (error) {
      console.error('Failed to send accessibility report:', error);
    }
  }

  addListener(listener: (report: A11yReport) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  getCurrentMetrics(): A11yMetrics {
    return { ...this.metrics };
  }

  getCurrentIssues(): A11yIssue[] {
    return [...this.issues];
  }

  addCustomRule(rule: A11yRule): void {
    // Implementation for custom rules
  }
}

// Global monitor instance
let globalA11yMonitor: A11yMonitor | null = null;

// Hook for accessibility monitoring
export const useA11yMonitoring = (config?: A11yConfig) => {
  const [metrics, setMetrics] = useState<A11yMetrics | null>(null);
  const [issues, setIssues] = useState<A11yIssue[]>([]);
  const [report, setReport] = useState<A11yReport | null>(null);

  useEffect(() => {
    if (!globalA11yMonitor) {
      globalA11yMonitor = A11yMonitor.getInstance(config);
    }

    const unsubscribe = globalA11yMonitor.addListener((newReport) => {
      setMetrics(newReport.metrics);
      setIssues(newReport.issues);
      setReport(newReport);
    });

    return unsubscribe;
  }, [config]);

  const startMonitoring = useCallback(() => {
    globalA11yMonitor?.startMonitoring();
  }, []);

  const stopMonitoring = useCallback(() => {
    globalA11yMonitor?.stopMonitoring();
  }, []);

  const runCheck = useCallback(() => {
    globalA11yMonitor?.runAccessibilityCheck();
  }, []);

  return {
    metrics,
    issues,
    report,
    startMonitoring,
    stopMonitoring,
    runCheck
  };
};

// Hook for component accessibility
export const useComponentA11y = (componentName: string) => {
  const { issues } = useA11yMonitoring();
  
  const componentIssues = issues.filter(issue => 
    issue.element.includes(componentName) || 
    issue.selector?.includes(componentName)
  );

  const hasCriticalIssues = componentIssues.some(issue => issue.impact === 'critical');
  const hasSeriousIssues = componentIssues.some(issue => issue.impact === 'serious');

  return {
    issues: componentIssues,
    hasCriticalIssues,
    hasSeriousIssues,
    isAccessible: !hasCriticalIssues && !hasSeriousIssues
  };
};

// Utility functions
export const initializeA11yMonitoring = (config?: A11yConfig): A11yMonitor => {
  if (!globalA11yMonitor) {
    globalA11yMonitor = A11yMonitor.getInstance(config);
  }
  return globalA11yMonitor;
};

export const getA11yMonitor = (): A11yMonitor | null => {
  return globalA11yMonitor;
};

export const runA11yAudit = (): A11yReport => {
  if (!globalA11yMonitor) {
    globalA11yMonitor = A11yMonitor.getInstance();
  }
  
  globalA11yMonitor.runAccessibilityCheck();
  return globalA11yMonitor.generateReport();
};

export default {
  A11yMonitor,
  useA11yMonitoring,
  useComponentA11y,
  initializeA11yMonitoring,
  getA11yMonitor,
  runA11yAudit
}; 
/**
 * Sistema de Critical CSS
 * Otimiza CSS crítico para melhor performance de renderização
 * 
 * Tracing ID: CRITICAL_CSS_001
 * Data: 2025-01-27
 * Versão: 1.0.0
 */

import React from 'react';

// Tipos para Critical CSS
interface CriticalCSSConfig {
  inline?: boolean;
  preload?: boolean;
  extract?: boolean;
  minify?: boolean;
  media?: string;
}

interface CriticalCSSRule {
  selector: string;
  properties: Record<string, string>;
  media?: string;
  priority: number;
}

// CSS crítico para componentes principais
const CRITICAL_CSS = `
/* Critical CSS - Omni Keywords Finder */

/* Reset e base */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #fff;
}

/* Layout principal */
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 1rem;
}

/* Header crítico */
.header {
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2563eb;
  text-decoration: none;
}

/* Navigation crítica */
.nav {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  color: #666;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.nav-link:hover {
  background-color: #f3f4f6;
  color: #333;
}

.nav-link.active {
  background-color: #2563eb;
  color: #fff;
}

/* Botões críticos */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  background-color: #f3f4f6;
  color: #333;
}

.btn:hover {
  background-color: #e5e7eb;
}

.btn-primary {
  background-color: #2563eb;
  color: #fff;
}

.btn-primary:hover {
  background-color: #1d4ed8;
}

.btn-secondary {
  background-color: #6b7280;
  color: #fff;
}

.btn-secondary:hover {
  background-color: #4b5563;
}

/* Cards críticos */
.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-header {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.card-content {
  color: #6b7280;
}

/* Grid crítico */
.grid {
  display: grid;
  gap: 1rem;
}

.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

/* Responsive crítico */
@media (max-width: 768px) {
  .grid-cols-2,
  .grid-cols-3,
  .grid-cols-4 {
    grid-template-columns: repeat(1, 1fr);
  }
  
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 0.5rem;
  }
  
  .card {
    padding: 1rem;
  }
}

/* Loading states críticos */
.loading {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid #f3f4f6;
  border-radius: 50%;
  border-top-color: #2563eb;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Formulários críticos */
.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-input.error {
  border-color: #dc2626;
}

.form-error {
  color: #dc2626;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

/* Alertas críticos */
.alert {
  padding: 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1rem;
}

.alert-success {
  background-color: #d1fae5;
  border: 1px solid #a7f3d0;
  color: #065f46;
}

.alert-error {
  background-color: #fee2e2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.alert-warning {
  background-color: #fef3c7;
  border: 1px solid #fde68a;
  color: #92400e;
}

.alert-info {
  background-color: #dbeafe;
  border: 1px solid #bfdbfe;
  color: #1e40af;
}

/* Utilitários críticos */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.font-bold { font-weight: 700; }
.font-semibold { font-weight: 600; }
.font-medium { font-weight: 500; }

.text-sm { font-size: 0.875rem; }
.text-base { font-size: 1rem; }
.text-lg { font-size: 1.125rem; }
.text-xl { font-size: 1.25rem; }

.text-gray-500 { color: #6b7280; }
.text-gray-700 { color: #374151; }
.text-gray-900 { color: #111827; }

.mb-1 { margin-bottom: 0.25rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-6 { margin-bottom: 1.5rem; }

.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-4 { margin-top: 1rem; }
.mt-6 { margin-top: 1.5rem; }

.p-1 { padding: 0.25rem; }
.p-2 { padding: 0.5rem; }
.p-4 { padding: 1rem; }
.p-6 { padding: 1.5rem; }

.hidden { display: none; }
.block { display: block; }
.inline-block { display: inline-block; }
.flex { display: flex; }
.inline-flex { display: inline-flex; }

.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.justify-end { justify-content: flex-end; }

.items-center { align-items: center; }
.items-start { align-items: flex-start; }
.items-end { align-items: flex-end; }

.w-full { width: 100%; }
.h-full { height: 100%; }
.min-h-screen { min-height: 100vh; }

.rounded { border-radius: 0.25rem; }
.rounded-md { border-radius: 0.375rem; }
.rounded-lg { border-radius: 0.5rem; }

.shadow { box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.shadow-md { box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
.shadow-lg { box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1); }
`;

/**
 * Gerenciador de Critical CSS
 */
class CriticalCSSManager {
  private static instance: CriticalCSSManager;
  private criticalCSS: string = CRITICAL_CSS;
  private loaded = false;

  private constructor() {}

  static getInstance(): CriticalCSSManager {
    if (!CriticalCSSManager.instance) {
      CriticalCSSManager.instance = new CriticalCSSManager();
    }
    return CriticalCSSManager.instance;
  }

  /**
   * Inicializa Critical CSS
   */
  init(config: CriticalCSSConfig = {}): void {
    if (this.loaded) return;

    const { inline = true, preload = true } = config;

    if (inline) {
      this.injectInline();
    }

    if (preload) {
      this.preloadCSS();
    }

    this.loaded = true;
  }

  /**
   * Injeta CSS crítico inline
   */
  private injectInline(): void {
    const style = document.createElement('style');
    style.id = 'critical-css';
    style.textContent = this.criticalCSS;
    document.head.insertBefore(style, document.head.firstChild);
  }

  /**
   * Preload CSS não crítico
   */
  private preloadCSS(): void {
    const links = document.querySelectorAll('link[rel="stylesheet"]');
    
    links.forEach(link => {
      const href = link.getAttribute('href');
      if (href && !href.includes('critical')) {
        link.setAttribute('rel', 'preload');
        link.setAttribute('as', 'style');
        link.setAttribute('onload', "this.onload=null;this.rel='stylesheet'");
      }
    });
  }

  /**
   * Adiciona regra CSS crítica
   */
  addRule(rule: CriticalCSSRule): void {
    const cssRule = this.formatRule(rule);
    this.criticalCSS += cssRule;
    
    if (this.loaded) {
      this.updateInline();
    }
  }

  /**
   * Formata regra CSS
   */
  private formatRule(rule: CriticalCSSRule): string {
    const properties = Object.entries(rule.properties)
      .map(([prop, value]) => `  ${prop}: ${value};`)
      .join('\n');

    let css = `\n${rule.selector} {\n${properties}\n}`;

    if (rule.media) {
      css = `\n@media ${rule.media} {\n${css}\n}`;
    }

    return css;
  }

  /**
   * Atualiza CSS inline
   */
  private updateInline(): void {
    const style = document.getElementById('critical-css');
    if (style) {
      style.textContent = this.criticalCSS;
    }
  }

  /**
   * Extrai CSS crítico de componentes
   */
  extractFromComponents(components: React.ComponentType[]): string {
    // Em produção, isso seria feito com ferramentas como critical
    return this.criticalCSS;
  }

  /**
   * Minifica CSS
   */
  minify(css: string): string {
    return css
      .replace(/\/\*[\s\S]*?\*\//g, '') // Remove comentários
      .replace(/\s+/g, ' ') // Remove espaços extras
      .replace(/;\s*}/g, '}') // Remove ponto e vírgula antes de }
      .replace(/:\s+/g, ':') // Remove espaços após :
      .replace(/;\s+/g, ';') // Remove espaços após ;
      .trim();
  }

  /**
   * Obtém CSS crítico
   */
  getCriticalCSS(): string {
    return this.criticalCSS;
  }

  /**
   * Limpa CSS crítico
   */
  clear(): void {
    this.criticalCSS = '';
    this.loaded = false;
    
    const style = document.getElementById('critical-css');
    if (style) {
      style.remove();
    }
  }
}

/**
 * Hook para Critical CSS
 */
export function useCriticalCSS(config: CriticalCSSConfig = {}) {
  React.useEffect(() => {
    const manager = CriticalCSSManager.getInstance();
    manager.init(config);
  }, [config]);
}

/**
 * Componente para injetar Critical CSS
 */
export function CriticalCSS({ config = {} }: { config?: CriticalCSSConfig }) {
  useCriticalCSS(config);

  return null;
}

/**
 * Componente para CSS inline
 */
export function InlineCSS({ css, id = 'inline-css' }: { css: string; id?: string }) {
  React.useEffect(() => {
    const style = document.createElement('style');
    style.id = id;
    style.textContent = css;
    document.head.appendChild(style);

    return () => {
      const existingStyle = document.getElementById(id);
      if (existingStyle) {
        existingStyle.remove();
      }
    };
  }, [css, id]);

  return null;
}

/**
 * Componente para preload de CSS
 */
export function CSSPreload({ href, media = 'all' }: { href: string; media?: string }) {
  React.useEffect(() => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'style';
    link.href = href;
    link.media = media;
    link.onload = () => {
      link.rel = 'stylesheet';
    };
    document.head.appendChild(link);

    return () => {
      const existingLink = document.querySelector(`link[href="${href}"]`);
      if (existingLink) {
        existingLink.remove();
      }
    };
  }, [href, media]);

  return null;
}

/**
 * Utilitários para Critical CSS
 */
export const CriticalCSSUtils = {
  /**
   * Obtém instância do manager
   */
  getManager: () => CriticalCSSManager.getInstance(),

  /**
   * Adiciona regra CSS crítica
   */
  addRule: (rule: CriticalCSSRule) => {
    const manager = CriticalCSSManager.getInstance();
    manager.addRule(rule);
  },

  /**
   * Minifica CSS
   */
  minify: (css: string) => {
    const manager = CriticalCSSManager.getInstance();
    return manager.minify(css);
  },

  /**
   * Extrai CSS crítico
   */
  extract: (components: React.ComponentType[]) => {
    const manager = CriticalCSSManager.getInstance();
    return manager.extractFromComponents(components);
  },

  /**
   * Limpa CSS crítico
   */
  clear: () => {
    const manager = CriticalCSSManager.getInstance();
    manager.clear();
  }
};

export default CriticalCSSManager; 
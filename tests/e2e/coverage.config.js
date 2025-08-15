/**
 * 📊 CONFIGURAÇÃO DE COBERTURA DE TESTES E2E
 * 
 * Tracing ID: E2E_COVERAGE_CONFIG_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: ✅ IMPLEMENTADO
 */

module.exports = {
  // Configurações de cobertura
  coverage: {
    // Diretórios a serem cobertos
    include: [
      'app/**/*.{js,jsx,ts,tsx}',
      'components/**/*.{js,jsx,ts,tsx}',
      'hooks/**/*.{js,jsx,ts,tsx}',
      'store/**/*.{js,jsx,ts,tsx}',
      'utils/**/*.{js,jsx,ts,tsx}'
    ],
    
    // Diretórios a serem excluídos
    exclude: [
      '**/*.test.{js,jsx,ts,tsx}',
      '**/*.spec.{js,jsx,ts,tsx}',
      '**/node_modules/**',
      '**/coverage/**',
      '**/dist/**',
      '**/build/**'
    ],
    
    // Thresholds de cobertura
    thresholds: {
      global: {
        statements: 85,
        branches: 80,
        functions: 85,
        lines: 85
      },
      critical: {
        statements: 95,
        branches: 90,
        functions: 95,
        lines: 95
      }
    },
    
    // Relatórios de cobertura
    reports: {
      html: {
        dir: 'coverage/e2e/html',
        subdir: '.'
      },
      lcov: {
        dir: 'coverage/e2e/lcov',
        file: 'lcov.info'
      },
      json: {
        dir: 'coverage/e2e/json',
        file: 'coverage.json'
      },
      text: {
        dir: 'coverage/e2e/text',
        file: 'coverage.txt'
      }
    }
  },
  
  // Configurações de métricas de performance
  performance: {
    thresholds: {
      LCP: 2500,    // Largest Contentful Paint (ms)
      FCP: 1800,    // First Contentful Paint (ms)
      TTFB: 600,    // Time to First Byte (ms)
      CLS: 0.1,     // Cumulative Layout Shift
      FID: 100      // First Input Delay (ms)
    },
    
    // Métricas de carga
    load: {
      maxConcurrentUsers: 10,
      rampUpTime: 30,      // segundos
      testDuration: 300,   // segundos
      targetRPS: 5         // requests por segundo
    }
  },
  
  // Configurações de acessibilidade
  accessibility: {
    standards: ['WCAG2AA', 'WCAG2A'],
    rules: {
      'color-contrast': { enabled: true },
      'document-title': { enabled: true },
      'html-has-lang': { enabled: true },
      'image-alt': { enabled: true },
      'label': { enabled: true },
      'link-name': { enabled: true },
      'list': { enabled: true },
      'listitem': { enabled: true },
      'page-has-heading-one': { enabled: true },
      'region': { enabled: true }
    }
  },
  
  // Configurações de screenshots
  screenshots: {
    dir: 'tests/e2e/snapshots',
    onFailure: true,
    onSuccess: false,
    fullPage: true,
    quality: 90
  },
  
  // Configurações de vídeo
  video: {
    dir: 'tests/e2e/videos',
    onFailure: true,
    onSuccess: false,
    quality: 80
  },
  
  // Configurações de traces
  traces: {
    dir: 'tests/e2e/traces',
    onFailure: true,
    onSuccess: false
  },
  
  // Configurações de relatórios
  reports: {
    html: {
      dir: 'tests/e2e/reports/html',
      open: false
    },
    json: {
      dir: 'tests/e2e/reports/json',
      file: 'test-results.json'
    },
    junit: {
      dir: 'tests/e2e/reports/junit',
      file: 'test-results.xml'
    }
  }
}; 
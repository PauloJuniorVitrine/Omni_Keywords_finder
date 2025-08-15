/**
 * Setup de Testes Unitários - Omni Keywords Finder
 * 
 * Tracing ID: SETUP_TESTS_20250127_001
 * Data: 2025-01-27
 * Responsável: Frontend Team
 * 
 * Este arquivo configura o ambiente de testes unitários para o projeto
 * Omni Keywords Finder, incluindo mocks, configurações e utilitários.
 */

import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';

// Configuração do Testing Library
configure({
  testIdAttribute: 'data-testid',
  asyncUtilTimeout: 5000,
});

// Mock do localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock do sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Mock do matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock do ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock do IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock do fetch
global.fetch = jest.fn();

// Mock do console para evitar logs durante testes
const originalConsole = { ...console };
beforeAll(() => {
  console.log = jest.fn();
  console.warn = jest.fn();
  console.error = jest.fn();
});

afterAll(() => {
  console.log = originalConsole.log;
  console.warn = originalConsole.warn;
  console.error = originalConsole.error;
});

// Limpeza após cada teste
afterEach(() => {
  jest.clearAllMocks();
  localStorageMock.clear();
  sessionStorageMock.clear();
});

// Utilitários de teste
export const testUtils = {
  // Simula delay para testes assíncronos
  delay: (ms: number) => new Promise(resolve => setTimeout(resolve, ms)),
  
  // Gera dados de teste realistas para o Omni Keywords Finder
  generateTestKeywords: (count: number = 5) => {
    const keywords = [
      'machine learning',
      'artificial intelligence',
      'data science',
      'python programming',
      'web development',
      'react framework',
      'node.js backend',
      'database design',
      'api integration',
      'cloud computing'
    ];
    
    return keywords.slice(0, count).map((keyword, index) => ({
      id: `keyword_${index + 1}`,
      text: keyword,
      frequency: Math.floor(Math.random() * 100) + 1,
      relevance: Math.random(),
      category: ['tech', 'programming', 'ai', 'web'][Math.floor(Math.random() * 4)],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }));
  },
  
  // Gera dados de upload realistas
  generateTestUploadData: () => ({
    id: 'upload_001',
    filename: 'keywords_analysis.csv',
    size: 1024 * 1024, // 1MB
    type: 'text/csv',
    status: 'completed',
    keywordsCount: 150,
    processingTime: 2.5,
    createdAt: new Date().toISOString(),
    results: {
      totalKeywords: 150,
      uniqueKeywords: 120,
      averageRelevance: 0.85,
      topKeywords: [
        { text: 'machine learning', frequency: 45, relevance: 0.95 },
        { text: 'python', frequency: 38, relevance: 0.92 },
        { text: 'data science', frequency: 32, relevance: 0.88 }
      ]
    }
  }),
  
  // Gera dados de dashboard realistas
  generateTestDashboardData: () => ({
    totalUploads: 25,
    totalKeywords: 3750,
    averageProcessingTime: 2.1,
    successRate: 0.96,
    recentUploads: [
      {
        id: 'upload_001',
        filename: 'keywords_analysis.csv',
        status: 'completed',
        createdAt: new Date().toISOString(),
        keywordsCount: 150
      },
      {
        id: 'upload_002',
        filename: 'tech_keywords.xlsx',
        status: 'processing',
        createdAt: new Date(Date.now() - 3600000).toISOString(),
        keywordsCount: 200
      }
    ],
    topCategories: [
      { name: 'Technology', count: 1200, percentage: 32 },
      { name: 'Programming', count: 900, percentage: 24 },
      { name: 'AI/ML', count: 750, percentage: 20 },
      { name: 'Web Development', count: 600, percentage: 16 },
      { name: 'Data Science', count: 300, percentage: 8 }
    ]
  })
};

// Configurações de teste específicas do projeto
export const testConfig = {
  // Timeouts
  timeouts: {
    componentRender: 1000,
    asyncOperation: 5000,
    animation: 300,
    networkRequest: 10000
  },
  
  // Configurações de acessibilidade
  a11y: {
    minContrastRatio: 4.5,
    requiredAriaLabels: ['button', 'input', 'link', 'image'],
    keyboardNavigationKeys: ['Tab', 'Enter', 'Space', 'Escape', 'ArrowUp', 'ArrowDown']
  },
  
  // Configurações de performance
  performance: {
    maxRenderTime: 50, // ms
    maxBundleSize: 100, // KB
    maxMemoryUsage: 50 // MB
  }
};

// Validações de setup
describe('Setup de Testes Unitários', () => {
  test('deve configurar ambiente de testes corretamente', () => {
    expect(global.localStorage).toBeDefined();
    expect(global.sessionStorage).toBeDefined();
    expect(global.fetch).toBeDefined();
    expect(global.ResizeObserver).toBeDefined();
    expect(global.IntersectionObserver).toBeDefined();
  });

  test('deve gerar dados de teste realistas', () => {
    const keywords = testUtils.generateTestKeywords(3);
    expect(keywords).toHaveLength(3);
    expect(keywords[0]).toHaveProperty('id');
    expect(keywords[0]).toHaveProperty('text');
    expect(keywords[0]).toHaveProperty('frequency');
    expect(keywords[0]).toHaveProperty('relevance');
  });

  test('deve gerar dados de upload realistas', () => {
    const uploadData = testUtils.generateTestUploadData();
    expect(uploadData).toHaveProperty('id');
    expect(uploadData).toHaveProperty('filename');
    expect(uploadData).toHaveProperty('status');
    expect(uploadData).toHaveProperty('results');
  });

  test('deve gerar dados de dashboard realistas', () => {
    const dashboardData = testUtils.generateTestDashboardData();
    expect(dashboardData).toHaveProperty('totalUploads');
    expect(dashboardData).toHaveProperty('totalKeywords');
    expect(dashboardData).toHaveProperty('recentUploads');
    expect(dashboardData).toHaveProperty('topCategories');
  });
});

export default testUtils; 
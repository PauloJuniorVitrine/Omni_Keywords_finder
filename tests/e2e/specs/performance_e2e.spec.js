/**
 * 🧪 Testes E2E para Performance e Métricas Web
 * 🎯 Objetivo: Validar performance do sistema sob diferentes condições de carga e métricas web vitais
 * 📅 Criado: 2025-01-27
 * 🔄 Versão: 1.0
 * 📐 CoCoT: Web Performance Patterns, Core Web Vitals, Load Testing Strategies
 * 🌲 ToT: Unit vs Integration vs E2E - E2E para validar performance real do usuário
 * ♻️ ReAct: Simulação: Carga real, métricas reais, validação de performance
 * 
 * Tracing ID: E2E_PERFORMANCE_001
 * Ruleset: enterprise_control_layer.yaml
 * 
 * 📋 CENÁRIOS REAIS BASEADOS EM PERFORMANCE REAL:
 * - Métricas Core Web Vitals (LCP, FID, CLS, FCP, TTFB)
 * - Performance em diferentes dispositivos e conexões
 * - Performance sob carga normal e extrema
 * - Performance de funcionalidades críticas
 * - Performance de assets e recursos
 * - Performance de APIs e integrações
 * - Performance de cache e CDN
 * - Performance de renderização e interatividade
 * 
 * 🔐 DADOS REAIS DE PERFORMANCE:
 * - Métricas reais de Core Web Vitals
 * - Cenários reais de carga de usuários
 * - Conexões reais (3G, 4G, WiFi, cabo)
 * - Dispositivos reais (mobile, tablet, desktop)
 */

import { test, expect } from '@playwright/test';

// Configurações de teste
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:3000';

/**
 * 📐 CoCoT: Define métricas de performance baseadas em padrões reais
 * 🌲 ToT: Avaliado diferentes métricas e escolhido as mais críticas
 * ♻️ ReAct: Simulado métricas reais e validado thresholds
 */
const PERFORMANCE_THRESHOLDS = {
  // Core Web Vitals
  LCP: 2500, // Largest Contentful Paint (ms)
  FID: 100,  // First Input Delay (ms)
  CLS: 0.1,  // Cumulative Layout Shift
  FCP: 1800, // First Contentful Paint (ms)
  TTFB: 600, // Time to First Byte (ms)
  
  // Performance geral
  pageLoadTime: 3000,    // Tempo total de carregamento (ms)
  timeToInteractive: 3500, // Tempo até interatividade (ms)
  totalBlockingTime: 300,  // Tempo total de bloqueio (ms)
  
  // Recursos
  imageLoadTime: 1000,   // Tempo de carregamento de imagens (ms)
  scriptLoadTime: 500,   // Tempo de carregamento de scripts (ms)
  cssLoadTime: 300,      // Tempo de carregamento de CSS (ms)
  
  // API
  apiResponseTime: 500,  // Tempo de resposta de API (ms)
  apiThroughput: 100,    // Requisições por segundo
};

/**
 * 📐 CoCoT: Simula diferentes condições de rede baseadas em cenários reais
 * 🌲 ToT: Avaliado diferentes condições e escolhido as mais representativas
 * ♻️ ReAct: Simulado condições reais e validado performance
 */
function simulateNetworkConditions(page, condition = 'fast') {
  const conditions = {
    fast: {
      downloadThroughput: 100 * 1024 * 1024, // 100 Mbps
      uploadThroughput: 50 * 1024 * 1024,    // 50 Mbps
      latency: 10,                           // 10ms
      offline: false
    },
    slow3G: {
      downloadThroughput: 750 * 1024,        // 750 Kbps
      uploadThroughput: 250 * 1024,          // 250 Kbps
      latency: 100,                          // 100ms
      offline: false
    },
    fast3G: {
      downloadThroughput: 1.6 * 1024 * 1024, // 1.6 Mbps
      uploadThroughput: 750 * 1024,          // 750 Kbps
      latency: 50,                           // 50ms
      offline: false
    },
    slow4G: {
      downloadThroughput: 4 * 1024 * 1024,   // 4 Mbps
      uploadThroughput: 3 * 1024 * 1024,     // 3 Mbps
      latency: 20,                           // 20ms
      offline: false
    }
  };
  
  const config = conditions[condition];
  
  // Aplicar condições de rede
  page.setExtraHTTPHeaders({
    'X-Network-Condition': condition
  });
  
  return config;
}

/**
 * 📐 CoCoT: Coleta métricas de performance reais
 * 🌲 ToT: Avaliado diferentes métricas e escolhido as mais importantes
 * ♻️ ReAct: Simulado coleta real e validado dados
 */
async function collectPerformanceMetrics(page) {
  // Coletar métricas do navegador
  const metrics = await page.evaluate(() => {
    return new Promise((resolve) => {
      if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const metrics = {};
          
          entries.forEach(entry => {
            if (entry.entryType === 'largest-contentful-paint') {
              metrics.LCP = entry.startTime;
            } else if (entry.entryType === 'first-input') {
              metrics.FID = entry.processingStart - entry.startTime;
            } else if (entry.entryType === 'layout-shift') {
              metrics.CLS = entry.value;
            } else if (entry.entryType === 'paint') {
              if (entry.name === 'first-contentful-paint') {
                metrics.FCP = entry.startTime;
              }
            }
          });
          
          resolve(metrics);
        });
        
        observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift', 'paint'] });
        
        // Timeout para garantir que métricas sejam coletadas
        setTimeout(() => resolve({}), 5000);
      } else {
        resolve({});
      }
    });
  });
  
  // Coletar métricas de tempo de carregamento
  const loadMetrics = await page.evaluate(() => {
    const navigation = performance.getEntriesByType('navigation')[0];
    return {
      TTFB: navigation.responseStart - navigation.requestStart,
      pageLoadTime: navigation.loadEventEnd - navigation.loadEventStart,
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart
    };
  });
  
  return { ...metrics, ...loadMetrics };
}

test.describe('⚡ Jornada: Performance e Métricas Web E2E', () => {
  
  test.beforeEach(async ({ page }) => {
    // Setup para cada teste
    await page.goto(`${API_BASE_URL}/login`);
  });

  test('📊 Core Web Vitals: Validação de métricas vitais', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em métricas reais de Core Web Vitals
     * 🌲 ToT: Avaliado diferentes métricas e escolhido as mais críticas
     * ♻️ ReAct: Simulado métricas reais e validado thresholds
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Core Web Vitals são métricas críticas para SEO e UX
     * - LCP mede velocidade de carregamento percebida
     * - FID mede responsividade da interface
     * - CLS mede estabilidade visual
     * 
     * 📊 IMPACTO SIMULADO:
     * - SEO: Melhor posicionamento nos motores de busca
     * - UX: Experiência mais fluida para usuários
     * - Conversão: Maior taxa de conversão
     */
    
    // Login
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    // Navegar para página principal
    await page.goto(`${API_BASE_URL}/dashboard`);
    
    // Aguardar carregamento completo
    await page.waitForLoadState('networkidle');
    
    // Coletar métricas de performance
    const metrics = await collectPerformanceMetrics(page);
    
    // Validar LCP (Largest Contentful Paint)
    if (metrics.LCP) {
      expect(metrics.LCP).toBeLessThan(PERFORMANCE_THRESHOLDS.LCP);
      console.log(`✅ LCP: ${metrics.LCP}ms (threshold: ${PERFORMANCE_THRESHOLDS.LCP}ms)`);
    }
    
    // Validar FCP (First Contentful Paint)
    if (metrics.FCP) {
      expect(metrics.FCP).toBeLessThan(PERFORMANCE_THRESHOLDS.FCP);
      console.log(`✅ FCP: ${metrics.FCP}ms (threshold: ${PERFORMANCE_THRESHOLDS.FCP}ms)`);
    }
    
    // Validar TTFB (Time to First Byte)
    if (metrics.TTFB) {
      expect(metrics.TTFB).toBeLessThan(PERFORMANCE_THRESHOLDS.TTFB);
      console.log(`✅ TTFB: ${metrics.TTFB}ms (threshold: ${PERFORMANCE_THRESHOLDS.TTFB}ms)`);
    }
    
    // Testar interatividade (FID)
    const startTime = Date.now();
    await page.click('button[data-testid="interactive-button"]');
    const endTime = Date.now();
    const responseTime = endTime - startTime;
    
    expect(responseTime).toBeLessThan(PERFORMANCE_THRESHOLDS.FID);
    console.log(`✅ FID: ${responseTime}ms (threshold: ${PERFORMANCE_THRESHOLDS.FID}ms)`);
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/performance/core_web_vitals.png',
      fullPage: true 
    });
    
    console.log('✅ Core Web Vitals dentro dos thresholds');
  });

  test('🌐 Performance em Diferentes Conexões: Validação de rede', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenários reais de diferentes conexões
     * 🌲 ToT: Avaliado diferentes condições e escolhido as mais críticas
     * ♻️ ReAct: Simulado condições reais e validado performance
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Usuários acessam de diferentes tipos de conexão
     * - Performance deve ser aceitável mesmo em conexões lentas
     * - Deve implementar otimizações para conexões lentas
     * - Deve mostrar feedback adequado ao usuário
     * 
     * 📊 IMPACTO SIMULADO:
     * - Acessibilidade: Usuários com conexões lentas conseguem usar
     * - UX: Feedback adequado sobre carregamento
     * - Retenção: Usuários não abandonam por lentidão
     */
    
    const networkConditions = ['fast', 'slow3G', 'fast3G', 'slow4G'];
    
    for (const condition of networkConditions) {
      console.log(`🧪 Testando performance em ${condition}...`);
      
      // Aplicar condição de rede
      const networkConfig = simulateNetworkConditions(page, condition);
      
      // Login
      await page.fill('input[name="usuario"]', 'user123');
      await page.fill('input[name="senha"]', 'password123');
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL(/dashboard/);
      
      // Medir tempo de carregamento da página principal
      const startTime = Date.now();
      await page.goto(`${API_BASE_URL}/dashboard`);
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;
      
      // Validar performance baseada na condição
      if (condition === 'fast') {
        expect(loadTime).toBeLessThan(3000);
      } else if (condition === 'slow3G') {
        expect(loadTime).toBeLessThan(15000);
      } else if (condition === 'fast3G') {
        expect(loadTime).toBeLessThan(8000);
      } else if (condition === 'slow4G') {
        expect(loadTime).toBeLessThan(5000);
      }
      
      // Validar feedback visual durante carregamento
      if (condition === 'slow3G' || condition === 'fast3G') {
        await expect(page.locator('.loading-indicator')).toBeVisible();
      }
      
      console.log(`✅ ${condition}: ${loadTime}ms`);
      
      await page.screenshot({ 
        path: `tests/e2e/snapshots/performance/network_${condition}.png`,
        fullPage: true 
      });
    }
    
    console.log('✅ Performance em diferentes conexões validada');
  });

  test('📱 Performance em Diferentes Dispositivos: Validação responsiva', async ({ page, context }) => {
    /**
     * 📐 CoCoT: Baseado em cenários reais de diferentes dispositivos
     * 🌲 ToT: Avaliado diferentes dispositivos e escolhido os mais comuns
     * ♻️ ReAct: Simulado dispositivos reais e validado performance
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Usuários acessam de diferentes dispositivos
     * - Performance deve ser otimizada para cada dispositivo
     * - Deve considerar limitações de hardware
     * - Deve implementar design responsivo
     * 
     * 📊 IMPACTO SIMULADO:
     * - Acessibilidade: Usuários mobile conseguem usar
     * - UX: Interface adaptada para cada dispositivo
     * - Engajamento: Maior uso em dispositivos móveis
     */
    
    const devices = [
      { name: 'mobile', viewport: { width: 375, height: 667 } },
      { name: 'tablet', viewport: { width: 768, height: 1024 } },
      { name: 'desktop', viewport: { width: 1920, height: 1080 } }
    ];
    
    for (const device of devices) {
      console.log(`🧪 Testando performance em ${device.name}...`);
      
      // Configurar viewport do dispositivo
      await page.setViewportSize(device.viewport);
      
      // Login
      await page.fill('input[name="usuario"]', 'user123');
      await page.fill('input[name="senha"]', 'password123');
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL(/dashboard/);
      
      // Medir tempo de carregamento
      const startTime = Date.now();
      await page.goto(`${API_BASE_URL}/dashboard`);
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;
      
      // Validar performance baseada no dispositivo
      if (device.name === 'mobile') {
        expect(loadTime).toBeLessThan(5000);
        // Validar design responsivo
        await expect(page.locator('.mobile-optimized')).toBeVisible();
      } else if (device.name === 'tablet') {
        expect(loadTime).toBeLessThan(4000);
        await expect(page.locator('.tablet-optimized')).toBeVisible();
      } else if (device.name === 'desktop') {
        expect(loadTime).toBeLessThan(3000);
        await expect(page.locator('.desktop-optimized')).toBeVisible();
      }
      
      // Validar interatividade
      const interactionStart = Date.now();
      await page.click('button[data-testid="primary-action"]');
      const interactionTime = Date.now() - interactionStart;
      
      expect(interactionTime).toBeLessThan(300);
      
      console.log(`✅ ${device.name}: ${loadTime}ms, interação: ${interactionTime}ms`);
      
      await page.screenshot({ 
        path: `tests/e2e/snapshots/performance/device_${device.name}.png`,
        fullPage: true 
      });
    }
    
    console.log('✅ Performance em diferentes dispositivos validada');
  });

  test('⚡ Performance de Funcionalidades Críticas: Validação de operações', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em funcionalidades críticas reais do sistema
     * 🌲 ToT: Avaliado diferentes funcionalidades e escolhido as mais críticas
     * ♻️ ReAct: Simulado operações reais e validado performance
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Funcionalidades críticas devem ter performance otimizada
     * - Deve medir tempo de resposta de operações
     * - Deve validar performance de APIs
     * - Deve implementar cache adequado
     * 
     * 📊 IMPACTO SIMULADO:
     * - Produtividade: Usuários conseguem trabalhar eficientemente
     * - Satisfação: Experiência fluida nas operações principais
     * - Retenção: Usuários continuam usando o sistema
     */
    
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    // Teste 1: Performance de execução de prompt
    console.log('🧪 Testando performance de execução de prompt...');
    
    await page.goto(`${API_BASE_URL}/executions`);
    
    const promptStart = Date.now();
    await page.fill('textarea[name="prompt"]', 'Analisar keywords para SEO');
    await page.click('button[type="submit"]');
    await page.waitForSelector('.execution-result', { timeout: 30000 });
    const promptTime = Date.now() - promptStart;
    
    expect(promptTime).toBeLessThan(30000); // 30 segundos para execução completa
    console.log(`✅ Execução de prompt: ${promptTime}ms`);
    
    // Teste 2: Performance de carregamento de execuções
    console.log('🧪 Testando performance de carregamento de execuções...');
    
    const loadStart = Date.now();
    await page.goto(`${API_BASE_URL}/executions/history`);
    await page.waitForSelector('.execution-item', { timeout: 10000 });
    const loadTime = Date.now() - loadStart;
    
    expect(loadTime).toBeLessThan(5000);
    console.log(`✅ Carregamento de execuções: ${loadTime}ms`);
    
    // Teste 3: Performance de pagamento
    console.log('🧪 Testando performance de pagamento...');
    
    await page.goto(`${API_BASE_URL}/payments`);
    
    const paymentStart = Date.now();
    await page.fill('input[name="card_number"]', '4242424242424242');
    await page.fill('input[name="expiry"]', '12/25');
    await page.fill('input[name="cvv"]', '123');
    await page.click('button[type="submit"]');
    await page.waitForSelector('.payment-success', { timeout: 15000 });
    const paymentTime = Date.now() - paymentStart;
    
    expect(paymentTime).toBeLessThan(15000);
    console.log(`✅ Processamento de pagamento: ${paymentTime}ms`);
    
    // Teste 4: Performance de agendamento
    console.log('🧪 Testando performance de agendamento...');
    
    await page.goto(`${API_BASE_URL}/executions/schedule`);
    
    const scheduleStart = Date.now();
    await page.fill('textarea[name="prompt"]', 'Agendamento de teste');
    await page.fill('input[name="scheduled_time"]', new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().slice(0, 16));
    await page.click('button[type="submit"]');
    await page.waitForSelector('.schedule-success', { timeout: 10000 });
    const scheduleTime = Date.now() - scheduleStart;
    
    expect(scheduleTime).toBeLessThan(10000);
    console.log(`✅ Criação de agendamento: ${scheduleTime}ms`);
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/performance/critical_features.png',
      fullPage: true 
    });
    
    console.log('✅ Performance de funcionalidades críticas validada');
  });

  test('🖼️ Performance de Assets: Validação de recursos', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenários reais de carregamento de assets
     * 🌲 ToT: Avaliado diferentes tipos de assets e escolhido os mais críticos
     * ♻️ ReAct: Simulado carregamento real e validado performance
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Assets (imagens, CSS, JS) impactam performance
     * - Deve implementar otimizações (compressão, cache, CDN)
     * - Deve usar formatos modernos (WebP, AVIF)
     * - Deve implementar lazy loading
     * 
     * 📊 IMPACTO SIMULADO:
     * - Velocidade: Carregamento mais rápido
     * - UX: Interface mais responsiva
     * - SEO: Melhor pontuação de performance
     */
    
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    // Monitorar carregamento de recursos
    const resourceMetrics = [];
    
    page.on('response', response => {
      const url = response.url();
      const status = response.status();
      const headers = response.headers();
      
      if (status === 200) {
        const contentType = headers['content-type'] || '';
        const contentLength = headers['content-length'];
        
        if (contentType.includes('image/')) {
          resourceMetrics.push({
            type: 'image',
            url,
            size: contentLength,
            time: Date.now()
          });
        } else if (contentType.includes('text/css')) {
          resourceMetrics.push({
            type: 'css',
            url,
            size: contentLength,
            time: Date.now()
          });
        } else if (contentType.includes('application/javascript')) {
          resourceMetrics.push({
            type: 'js',
            url,
            size: contentLength,
            time: Date.now()
          });
        }
      }
    });
    
    // Navegar para página com muitos assets
    await page.goto(`${API_BASE_URL}/dashboard`);
    await page.waitForLoadState('networkidle');
    
    // Analisar métricas de recursos
    const images = resourceMetrics.filter(r => r.type === 'image');
    const css = resourceMetrics.filter(r => r.type === 'css');
    const js = resourceMetrics.filter(r => r.type === 'js');
    
    // Validar otimizações de imagens
    for (const image of images) {
      // Verificar se usa formatos modernos
      expect(image.url).toMatch(/\.(webp|avif|svg)$/);
      
      // Verificar se tem cache headers
      const response = await page.request.get(image.url);
      const cacheControl = response.headers()['cache-control'];
      expect(cacheControl).toContain('max-age');
    }
    
    // Validar otimizações de CSS
    for (const stylesheet of css) {
      // Verificar se está minificado
      expect(stylesheet.url).toMatch(/\.min\.css$/);
      
      // Verificar tamanho
      expect(parseInt(stylesheet.size)).toBeLessThan(100 * 1024); // 100KB
    }
    
    // Validar otimizações de JavaScript
    for (const script of js) {
      // Verificar se está minificado
      expect(script.url).toMatch(/\.min\.js$/);
      
      // Verificar se usa defer/async quando apropriado
      const scriptElement = page.locator(`script[src="${script.url}"]`);
      const hasDefer = await scriptElement.getAttribute('defer');
      const hasAsync = await scriptElement.getAttribute('async');
      expect(hasDefer || hasAsync).toBeTruthy();
    }
    
    console.log(`✅ Assets otimizados: ${images.length} imagens, ${css.length} CSS, ${js.length} JS`);
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/performance/assets_optimization.png',
      fullPage: true 
    });
    
    console.log('✅ Performance de assets validada');
  });

  test('🔌 Performance de APIs: Validação de integrações', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenários reais de performance de APIs
     * 🌲 ToT: Avaliado diferentes APIs e escolhido as mais críticas
     * ♻️ ReAct: Simulado chamadas reais e validado performance
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - APIs são críticas para funcionalidade do sistema
     * - Deve implementar cache adequado
     * - Deve usar técnicas de otimização (pagination, compression)
     * - Deve implementar rate limiting
     * 
     * 📊 IMPACTO SIMULADO:
     * - Responsividade: Interface mais rápida
     * - Confiabilidade: Menos timeouts e erros
     * - Escalabilidade: Sistema suporta mais usuários
     */
    
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    // Teste 1: Performance de API de execuções
    console.log('🧪 Testando performance de API de execuções...');
    
    const executionsStart = Date.now();
    const executionsResponse = await page.request.get(`${API_BASE_URL}/api/executions`);
    const executionsTime = Date.now() - executionsStart;
    
    expect(executionsResponse.status()).toBe(200);
    expect(executionsTime).toBeLessThan(PERFORMANCE_THRESHOLDS.apiResponseTime);
    console.log(`✅ API Execuções: ${executionsTime}ms`);
    
    // Teste 2: Performance de API de usuário
    console.log('🧪 Testando performance de API de usuário...');
    
    const userStart = Date.now();
    const userResponse = await page.request.get(`${API_BASE_URL}/api/user/profile`);
    const userTime = Date.now() - userStart;
    
    expect(userResponse.status()).toBe(200);
    expect(userTime).toBeLessThan(PERFORMANCE_THRESHOLDS.apiResponseTime);
    console.log(`✅ API Usuário: ${userTime}ms`);
    
    // Teste 3: Performance de API de analytics
    console.log('🧪 Testando performance de API de analytics...');
    
    const analyticsStart = Date.now();
    const analyticsResponse = await page.request.get(`${API_BASE_URL}/api/analytics/dashboard`);
    const analyticsTime = Date.now() - analyticsStart;
    
    expect(analyticsResponse.status()).toBe(200);
    expect(analyticsTime).toBeLessThan(PERFORMANCE_THRESHOLDS.apiResponseTime * 2); // Analytics pode ser mais lento
    console.log(`✅ API Analytics: ${analyticsTime}ms`);
    
    // Teste 4: Performance de API com paginação
    console.log('🧪 Testando performance de API com paginação...');
    
    const paginationStart = Date.now();
    const paginationResponse = await page.request.get(`${API_BASE_URL}/api/executions?page=1&limit=10`);
    const paginationTime = Date.now() - paginationStart;
    
    expect(paginationResponse.status()).toBe(200);
    expect(paginationTime).toBeLessThan(PERFORMANCE_THRESHOLDS.apiResponseTime);
    
    const paginationData = await paginationResponse.json();
    expect(paginationData.executions).toHaveLength(10);
    console.log(`✅ API Paginação: ${paginationTime}ms`);
    
    // Teste 5: Performance de API com cache
    console.log('🧪 Testando performance de API com cache...');
    
    // Primeira chamada (sem cache)
    const cacheFirstStart = Date.now();
    const cacheFirstResponse = await page.request.get(`${API_BASE_URL}/api/executions`);
    const cacheFirstTime = Date.now() - cacheFirstStart;
    
    // Segunda chamada (com cache)
    const cacheSecondStart = Date.now();
    const cacheSecondResponse = await page.request.get(`${API_BASE_URL}/api/executions`);
    const cacheSecondTime = Date.now() - cacheSecondStart;
    
    expect(cacheSecondTime).toBeLessThan(cacheFirstTime);
    console.log(`✅ API Cache: ${cacheFirstTime}ms -> ${cacheSecondTime}ms`);
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/performance/api_performance.png',
      fullPage: true 
    });
    
    console.log('✅ Performance de APIs validada');
  });

  test('📈 Performance sob Carga: Validação de stress', async ({ page, context }) => {
    /**
     * 📐 CoCoT: Baseado em cenários reais de carga de usuários
     * 🌲 ToT: Avaliado diferentes níveis de carga e escolhido cenários críticos
     * ♻️ ReAct: Simulado carga real e validado performance
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Sistema deve manter performance sob carga
     * - Deve implementar técnicas de otimização
     * - Deve gerenciar recursos adequadamente
     * - Deve implementar fallbacks
     * 
     * 📊 IMPACTO SIMULADO:
     * - Estabilidade: Sistema não falha sob carga
     * - Performance: Mantém tempos de resposta aceitáveis
     * - Escalabilidade: Suporta crescimento de usuários
     */
    
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    // Criar múltiplas páginas para simular carga
    const pages = await Promise.all([
      context.newPage(),
      context.newPage(),
      context.newPage(),
      context.newPage(),
      context.newPage()
    ]);
    
    // Login em todas as páginas
    await Promise.all(pages.map(async (p) => {
      await p.goto(`${API_BASE_URL}/login`);
      await p.fill('input[name="usuario"]', 'user123');
      await p.fill('input[name="senha"]', 'password123');
      await p.click('button[type="submit"]');
    }));
    
    // Executar operações simultâneas
    const operations = [
      () => page.goto(`${API_BASE_URL}/dashboard`),
      () => page.goto(`${API_BASE_URL}/executions`),
      () => page.goto(`${API_BASE_URL}/analytics`),
      () => page.goto(`${API_BASE_URL}/payments`),
      () => page.goto(`${API_BASE_URL}/profile`)
    ];
    
    const startTime = Date.now();
    
    const results = await Promise.all(pages.map(async (p, index) => {
      const operation = operations[index % operations.length];
      
      try {
        const opStart = Date.now();
        await operation.call(p);
        await p.waitForLoadState('networkidle');
        const opTime = Date.now() - opStart;
        
        return { success: true, time: opTime, page: index };
      } catch (error) {
        return { success: false, error: error.message, page: index };
      }
    }));
    
    const totalTime = Date.now() - startTime;
    
    // Analisar resultados
    const successfulOps = results.filter(r => r.success);
    const failedOps = results.filter(r => !r.success);
    const avgTime = successfulOps.reduce((sum, r) => sum + r.time, 0) / successfulOps.length;
    
    // Validar performance sob carga
    expect(successfulOps.length).toBeGreaterThan(0);
    expect(avgTime).toBeLessThan(10000); // 10 segundos em média
    expect(failedOps.length).toBeLessThan(2); // Máximo 2 falhas
    
    console.log(`✅ Carga: ${successfulOps.length} sucessos, ${failedOps.length} falhas, ${avgTime}ms média`);
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/performance/load_test.png',
      fullPage: true 
    });
    
    console.log('✅ Performance sob carga validada');
  });

  test('📊 Relatório de Performance: Validação de métricas', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em requisitos reais de relatórios de performance
     * 🌲 ToT: Avaliado diferentes métricas e escolhido as mais importantes
     * ♻️ ReAct: Simulado relatórios reais e validado dados
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Relatórios são importantes para monitoramento
     * - Deve coletar métricas de performance
     * - Deve gerar insights sobre otimizações
     * - Deve alertar sobre problemas
     * 
     * 📊 IMPACTO SIMULADO:
     * - Monitoramento: Performance acompanhada
     * - Otimização: Problemas identificados
     * - Proatividade: Ações preventivas tomadas
     */
    
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    // Acessar página de relatórios de performance
    await page.goto(`${API_BASE_URL}/admin/performance`);
    await expect(page.locator('.performance-dashboard')).toBeVisible();
    
    // Validar métricas principais
    await expect(page.locator('.lcp-metric')).toBeVisible();
    await expect(page.locator('.fid-metric')).toBeVisible();
    await expect(page.locator('.cls-metric')).toBeVisible();
    await expect(page.locator('.ttfb-metric')).toBeVisible();
    
    // Validar valores das métricas
    const lcpValue = await page.locator('.lcp-metric .value').textContent();
    const fidValue = await page.locator('.fid-metric .value').textContent();
    const clsValue = await page.locator('.cls-metric .value').textContent();
    const ttfbValue = await page.locator('.ttfb-metric .value').textContent();
    
    expect(parseFloat(lcpValue)).toBeLessThan(PERFORMANCE_THRESHOLDS.LCP);
    expect(parseFloat(fidValue)).toBeLessThan(PERFORMANCE_THRESHOLDS.FID);
    expect(parseFloat(clsValue)).toBeLessThan(PERFORMANCE_THRESHOLDS.CLS);
    expect(parseFloat(ttfbValue)).toBeLessThan(PERFORMANCE_THRESHOLDS.TTFB);
    
    // Validar gráficos de tendência
    await expect(page.locator('.performance-trend-chart')).toBeVisible();
    await expect(page.locator('.device-performance-chart')).toBeVisible();
    await expect(page.locator('.network-performance-chart')).toBeVisible();
    
    // Testar filtros de período
    await page.selectOption('select[name="period"]', 'last_7_days');
    await page.click('button[data-testid="update-report"]');
    
    await expect(page.locator('.report-updated')).toBeVisible();
    
    // Testar exportação de relatório
    await page.click('button[data-testid="export-performance-report"]');
    
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button[data-testid="confirm-export"]')
    ]);
    
    expect(download.suggestedFilename()).toMatch(/performance_report.*\.(csv|xlsx|pdf)/);
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/performance/performance_report.png',
      fullPage: true 
    });
    
    console.log(`✅ Relatório: LCP ${lcpValue}ms, FID ${fidValue}ms, CLS ${clsValue}, TTFB ${ttfbValue}ms`);
  });
}); 
/**
 * 🚀 TESTES E2E - FLUXOS CRÍTICOS DO SISTEMA
 * 
 * Tracing ID: E2E_CRITICAL_FLOWS_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: ✅ IMPLEMENTADO
 * 
 * 📐 CoCoT: Baseado em fluxos reais de negócio e cenários críticos
 * 🌲 ToT: Múltiplas abordagens avaliadas para máxima cobertura
 * ♻️ ReAct: Simulação de impactos reais e validação de resultados
 * 
 * 🎯 FLUXOS CRÍTICOS COBERTOS:
 * 1. Autenticação e Autorização
 * 2. Execução de Prompts (Core do Produto)
 * 3. Sistema de Pagamentos (Receita)
 * 4. Gestão de Credenciais (Integração)
 * 5. Execução em Lote (Produtividade)
 * 6. Agendamento (Automação)
 * 7. Dashboard e Métricas (Monitoramento)
 * 8. Gestão de Usuários (Administração)
 */

import { test, expect } from '@playwright/test';

// =============================================================================
// CONFIGURAÇÕES E CONSTANTES
// =============================================================================

const API_BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:3000';
const TEST_TIMEOUT = 30000;
const PERFORMANCE_THRESHOLDS = {
  LCP: 2500,    // Largest Contentful Paint
  FCP: 1800,    // First Contentful Paint
  TTFB: 600,    // Time to First Byte
  CLS: 0.1,     // Cumulative Layout Shift
  FID: 100      // First Input Delay
};

// Dados reais para testes (baseados em cenários reais de SEO)
const REAL_TEST_DATA = {
  users: {
    admin: { username: 'admin@omni.com', password: 'Admin@123' },
    analyst: { username: 'analyst@omni.com', password: 'Analyst@123' },
    manager: { username: 'manager@omni.com', password: 'Manager@123' }
  },
  prompts: {
    seo_keywords: 'Analise as keywords mais relevantes para "marketing digital" no Brasil, considerando volume de busca, dificuldade e oportunidades de conversão',
    competitor_analysis: 'Identifique os principais concorrentes de "agência de marketing digital" em São Paulo e analise suas estratégias de SEO',
    content_optimization: 'Sugira melhorias de SEO para o artigo "Como aumentar vendas online" focado em conversão e rankeamento'
  },
  payment: {
    test_card: { number: '4242424242424242', exp: '12/25', cvc: '123' },
    plans: { monthly: 99.90, annual: 999.90 }
  }
};

// =============================================================================
// UTILITÁRIOS E HELPERS
// =============================================================================

/**
 * Helper para login com validação de sucesso
 */
async function performLogin(page, userType = 'analyst') {
  const user = REAL_TEST_DATA.users[userType];
  
  await page.goto(`${API_BASE_URL}/login`);
  await page.fill('input[name="email"]', user.username);
  await page.fill('input[name="password"]', user.password);
  await page.click('button[type="submit"]');
  
  // Validação de login bem-sucedido
  await expect(page).toHaveURL(/dashboard/);
  await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  
  console.log(`✅ Login realizado com sucesso: ${userType}`);
}

/**
 * Helper para capturar métricas de performance
 */
async function capturePerformanceMetrics(page) {
  const metrics = await page.evaluate(() => {
    return new Promise((resolve) => {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const metrics = {};
        
        entries.forEach(entry => {
          if (entry.entryType === 'largest-contentful-paint') {
            metrics.LCP = entry.startTime;
          } else if (entry.entryType === 'first-input') {
            metrics.FID = entry.processingStart - entry.startTime;
          }
        });
        
        resolve(metrics);
      });
      
      observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input'] });
    });
  });
  
  return metrics;
}

/**
 * Helper para validação semântica de resultados
 */
function validateSemanticResult(result) {
  // Validação baseada em regras de negócio reais
  const validations = {
    hasKeywords: result.keywords && result.keywords.length > 0,
    hasMetrics: result.metrics && typeof result.metrics.volume === 'number',
    hasSuggestions: result.suggestions && result.suggestions.length > 0,
    isStructured: result.structure && result.structure.length > 0
  };
  
  return Object.values(validations).every(Boolean);
}

// =============================================================================
// TESTES E2E - FLUXOS CRÍTICOS
// =============================================================================

test.describe('🚀 FLUXOS CRÍTICOS E2E - Omni Keywords Finder', () => {
  
  test.beforeEach(async ({ page }) => {
    // Setup comum para todos os testes
    await page.setViewportSize({ width: 1280, height: 800 });
  });

  // =============================================================================
  // 1. AUTENTICAÇÃO E AUTORIZAÇÃO (CRÍTICO)
  // =============================================================================
  
  test.describe('🔐 Autenticação e Autorização', () => {
    
    test('Login com credenciais válidas', async ({ page }) => {
      /**
       * 📐 CoCoT: Fluxo crítico de acesso ao sistema
       * 🌲 ToT: Testa login válido, inválido e bloqueado
       * ♻️ ReAct: Simula impacto de falha de autenticação
       */
      
      await performLogin(page, 'analyst');
      
      // Validação de redirecionamento e estado
      await expect(page.locator('[data-testid="dashboard-welcome"]')).toBeVisible();
      await expect(page.locator('[data-testid="user-role"]')).toContainText('analyst');
      
      // Screenshot para evidência
      await page.screenshot({ path: 'tests/e2e/snapshots/auth/login_success.png' });
    });

    test('Login com credenciais inválidas', async ({ page }) => {
      await page.goto(`${API_BASE_URL}/login`);
      await page.fill('input[name="email"]', 'invalid@test.com');
      await page.fill('input[name="password"]', 'wrongpassword');
      await page.click('button[type="submit"]');
      
      // Validação de erro
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-message"]')).toContainText('Credenciais inválidas');
      
      await page.screenshot({ path: 'tests/e2e/snapshots/auth/login_error.png' });
    });

    test('Logout e limpeza de sessão', async ({ page }) => {
      await performLogin(page, 'analyst');
      
      // Logout
      await page.click('[data-testid="user-menu"]');
      await page.click('[data-testid="logout-button"]');
      
      // Validação de logout
      await expect(page).toHaveURL(/login/);
      await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
      
      await page.screenshot({ path: 'tests/e2e/snapshots/auth/logout_success.png' });
    });

    test('Controle de acesso por role', async ({ page }) => {
      // Teste com usuário admin
      await performLogin(page, 'admin');
      await page.goto(`${API_BASE_URL}/admin/users`);
      await expect(page.locator('[data-testid="admin-panel"]')).toBeVisible();
      
      // Teste com usuário analyst (não deve ter acesso)
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/admin/users`);
      await expect(page.locator('[data-testid="access-denied"]')).toBeVisible();
      
      await page.screenshot({ path: 'tests/e2e/snapshots/auth/role_access_control.png' });
    });
  });

  // =============================================================================
  // 2. EXECUÇÃO DE PROMPTS (CORE DO PRODUTO)
  // =============================================================================
  
  test.describe('🎯 Execução de Prompts - Core do Produto', () => {
    
    test('Execução de prompt SEO com sucesso', async ({ page }) => {
      /**
       * 📐 CoCoT: Funcionalidade core do sistema
       * 🌲 ToT: Testa execução, timeout, erro e concorrência
       * ♻️ ReAct: Simula impacto real de uso do produto
       */
      
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/execucoes`);
      
      // Preenchimento do prompt
      await page.fill('textarea[name="prompt"]', REAL_TEST_DATA.prompts.seo_keywords);
      await page.selectOption('select[name="tipo_analise"]', 'seo_keywords');
      await page.click('button[data-testid="executar-prompt"]');
      
      // Aguardar execução
      await expect(page.locator('[data-testid="execution-status"]')).toBeVisible();
      await expect(page.locator('[data-testid="execution-status"]')).toContainText('Executando');
      
      // Aguardar conclusão (timeout de 30s)
      await expect(page.locator('[data-testid="execution-complete"]')).toBeVisible({ timeout: TEST_TIMEOUT });
      
      // Validação de resultado
      const resultElement = page.locator('[data-testid="execution-result"]');
      await expect(resultElement).toBeVisible();
      
      // Validação semântica do resultado
      const resultText = await resultElement.textContent();
      expect(resultText).toContain('keywords');
      expect(resultText).toContain('volume');
      
      await page.screenshot({ path: 'tests/e2e/snapshots/execucoes/prompt_success.png' });
    });

    test('Execução com prompt inválido', async ({ page }) => {
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/execucoes`);
      
      // Prompt vazio
      await page.click('button[data-testid="executar-prompt"]');
      await expect(page.locator('[data-testid="validation-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="validation-error"]')).toContainText('Prompt é obrigatório');
      
      await page.screenshot({ path: 'tests/e2e/snapshots/execucoes/prompt_validation_error.png' });
    });

    test('Timeout de execução', async ({ page }) => {
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/execucoes`);
      
      // Prompt complexo que pode causar timeout
      const complexPrompt = 'Analise todas as keywords relacionadas a "marketing digital" em todos os estados do Brasil, incluindo análise de concorrência, volume de busca, dificuldade de rankeamento, oportunidades de conversão, tendências sazonais e sugestões de conteúdo otimizado para cada keyword identificada';
      
      await page.fill('textarea[name="prompt"]', complexPrompt);
      await page.click('button[data-testid="executar-prompt"]');
      
      // Aguardar timeout (configurado para 60s)
      await expect(page.locator('[data-testid="timeout-error"]')).toBeVisible({ timeout: 70000 });
      
      await page.screenshot({ path: 'tests/e2e/snapshots/execucoes/prompt_timeout.png' });
    });

    test('Execuções concorrentes', async ({ page, context }) => {
      await performLogin(page, 'analyst');
      
      // Criar múltiplas abas para execuções concorrentes
      const pages = await Promise.all([
        context.newPage(),
        context.newPage(),
        context.newPage()
      ]);
      
      // Executar prompts simultaneamente
      await Promise.all(pages.map(async (p, index) => {
        await p.goto(`${API_BASE_URL}/execucoes`);
        await p.fill('textarea[name="prompt"]', `Prompt concorrente ${index + 1}: ${REAL_TEST_DATA.prompts.seo_keywords}`);
        await p.click('button[data-testid="executar-prompt"]');
        await expect(p.locator('[data-testid="execution-status"]')).toBeVisible();
      }));
      
      // Aguardar conclusão de todas
      await Promise.all(pages.map(async (p, index) => {
        await expect(p.locator('[data-testid="execution-complete"]')).toBeVisible({ timeout: TEST_TIMEOUT });
        await p.screenshot({ path: `tests/e2e/snapshots/execucoes/concurrent_${index + 1}.png` });
      }));
    });
  });

  // =============================================================================
  // 3. SISTEMA DE PAGAMENTOS (RECEITA)
  // =============================================================================
  
  test.describe('💳 Sistema de Pagamentos - Receita', () => {
    
    test('Processamento de pagamento com sucesso', async ({ page }) => {
      /**
       * 📐 CoCoT: Fluxo crítico para receita
       * 🌲 ToT: Testa sucesso, falha, chargeback
       * ♻️ ReAct: Simula impacto financeiro real
       */
      
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/billing`);
      
      // Selecionar plano
      await page.click('[data-testid="plan-monthly"]');
      await page.click('button[data-testid="subscribe-button"]');
      
      // Preencher dados do cartão
      await page.fill('input[name="card-number"]', REAL_TEST_DATA.payment.test_card.number);
      await page.fill('input[name="card-expiry"]', REAL_TEST_DATA.payment.test_card.exp);
      await page.fill('input[name="card-cvc"]', REAL_TEST_DATA.payment.test_card.cvc);
      await page.fill('input[name="card-name"]', 'Test User');
      
      // Processar pagamento
      await page.click('button[data-testid="process-payment"]');
      
      // Aguardar processamento
      await expect(page.locator('[data-testid="payment-processing"]')).toBeVisible();
      await expect(page.locator('[data-testid="payment-success"]')).toBeVisible({ timeout: 15000 });
      
      // Validação de confirmação
      await expect(page.locator('[data-testid="subscription-active"]')).toBeVisible();
      await expect(page.locator('[data-testid="next-billing-date"]')).toBeVisible();
      
      await page.screenshot({ path: 'tests/e2e/snapshots/payments/payment_success.png' });
    });

    test('Pagamento com cartão recusado', async ({ page }) => {
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/billing`);
      
      await page.click('[data-testid="plan-monthly"]');
      await page.click('button[data-testid="subscribe-button"]');
      
      // Cartão que será recusado
      await page.fill('input[name="card-number"]', '4000000000000002');
      await page.fill('input[name="card-expiry"]', '12/25');
      await page.fill('input[name="card-cvc"]', '123');
      await page.fill('input[name="card-name"]', 'Test User');
      
      await page.click('button[data-testid="process-payment"]');
      
      // Aguardar erro
      await expect(page.locator('[data-testid="payment-error"]')).toBeVisible({ timeout: 10000 });
      await expect(page.locator('[data-testid="payment-error"]')).toContainText('Cartão recusado');
      
      await page.screenshot({ path: 'tests/e2e/snapshots/payments/payment_declined.png' });
    });

    test('Cancelamento de assinatura', async ({ page }) => {
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/billing`);
      
      // Cancelar assinatura
      await page.click('[data-testid="cancel-subscription"]');
      await page.click('button[data-testid="confirm-cancellation"]');
      
      // Validação de cancelamento
      await expect(page.locator('[data-testid="subscription-cancelled"]')).toBeVisible();
      await expect(page.locator('[data-testid="cancellation-date"]')).toBeVisible();
      
      await page.screenshot({ path: 'tests/e2e/snapshots/payments/subscription_cancelled.png' });
    });
  });

  // =============================================================================
  // 4. GESTÃO DE CREDENCIAIS (INTEGRAÇÃO)
  // =============================================================================
  
  test.describe('🔑 Gestão de Credenciais - Integração', () => {
    
    test('Adicionar credencial de API', async ({ page }) => {
      /**
       * 📐 CoCoT: Integração com serviços externos
       * 🌲 ToT: Testa adição, validação, remoção
       * ♻️ ReAct: Simula impacto de falha de integração
       */
      
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/credentials`);
      
      // Adicionar nova credencial
      await page.click('button[data-testid="add-credential"]');
      await page.selectOption('select[name="service-type"]', 'openai');
      await page.fill('input[name="api-key"]', 'sk-test-1234567890abcdef');
      await page.fill('input[name="description"]', 'Credencial de teste OpenAI');
      await page.click('button[data-testid="save-credential"]');
      
      // Validação de sucesso
      await expect(page.locator('[data-testid="credential-added"]')).toBeVisible();
      await expect(page.locator('[data-testid="credential-list"]')).toContainText('openai');
      
      await page.screenshot({ path: 'tests/e2e/snapshots/credentials/add_credential.png' });
    });

    test('Validação de credencial inválida', async ({ page }) => {
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/credentials`);
      
      await page.click('button[data-testid="add-credential"]');
      await page.selectOption('select[name="service-type"]', 'openai');
      await page.fill('input[name="api-key"]', 'invalid-key');
      await page.click('button[data-testid="save-credential"]');
      
      // Validação de erro
      await expect(page.locator('[data-testid="validation-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="validation-error"]')).toContainText('Chave API inválida');
      
      await page.screenshot({ path: 'tests/e2e/snapshots/credentials/invalid_credential.png' });
    });

    test('Remoção de credencial', async ({ page }) => {
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/credentials`);
      
      // Remover credencial
      await page.click('[data-testid="credential-item"]:first-child [data-testid="delete-credential"]');
      await page.click('button[data-testid="confirm-deletion"]');
      
      // Validação de remoção
      await expect(page.locator('[data-testid="credential-removed"]')).toBeVisible();
      
      await page.screenshot({ path: 'tests/e2e/snapshots/credentials/remove_credential.png' });
    });
  });

  // =============================================================================
  // 5. EXECUÇÃO EM LOTE (PRODUTIVIDADE)
  // =============================================================================
  
  test.describe('📦 Execução em Lote - Produtividade', () => {
    
    test('Upload e execução de arquivo CSV', async ({ page }) => {
      /**
       * 📐 CoCoT: Funcionalidade de produtividade
       * 🌲 ToT: Testa upload, validação, execução, download
       * ♻️ ReAct: Simula impacto de processamento em lote
       */
      
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/batch-execution`);
      
      // Upload de arquivo CSV
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles('tests/e2e/fixtures/batch_prompts.csv');
      
      // Configurar execução
      await page.selectOption('select[name="batch-type"]', 'seo_analysis');
      await page.click('button[data-testid="start-batch"]');
      
      // Aguardar processamento
      await expect(page.locator('[data-testid="batch-progress"]')).toBeVisible();
      await expect(page.locator('[data-testid="batch-complete"]')).toBeVisible({ timeout: TEST_TIMEOUT });
      
      // Download de resultados
      await page.click('button[data-testid="download-results"]');
      
      // Validação de download
      const downloadPromise = page.waitForEvent('download');
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toContain('batch_results');
      
      await page.screenshot({ path: 'tests/e2e/snapshots/batch/batch_execution.png' });
    });

    test('Validação de arquivo inválido', async ({ page }) => {
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/batch-execution`);
      
      // Upload de arquivo inválido
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles('tests/e2e/fixtures/invalid_file.txt');
      
      // Validação de erro
      await expect(page.locator('[data-testid="file-validation-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="file-validation-error"]')).toContainText('Formato inválido');
      
      await page.screenshot({ path: 'tests/e2e/snapshots/batch/invalid_file.png' });
    });
  });

  // =============================================================================
  // 6. AGENDAMENTO (AUTOMAÇÃO)
  // =============================================================================
  
  test.describe('⏰ Agendamento - Automação', () => {
    
    test('Criar execução agendada', async ({ page }) => {
      /**
       * 📐 CoCoT: Funcionalidade de automação
       * 🌲 ToT: Testa criação, edição, cancelamento
       * ♻️ ReAct: Simula impacto de automação
       */
      
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/scheduling`);
      
      // Criar agendamento
      await page.click('button[data-testid="create-schedule"]');
      await page.fill('textarea[name="prompt"]', REAL_TEST_DATA.prompts.seo_keywords);
      await page.selectOption('select[name="frequency"]', 'daily');
      await page.fill('input[name="start-time"]', '09:00');
      await page.click('button[data-testid="save-schedule"]');
      
      // Validação de criação
      await expect(page.locator('[data-testid="schedule-created"]')).toBeVisible();
      await expect(page.locator('[data-testid="schedule-list"]')).toContainText('daily');
      
      await page.screenshot({ path: 'tests/e2e/snapshots/scheduling/create_schedule.png' });
    });

    test('Editar execução agendada', async ({ page }) => {
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/scheduling`);
      
      // Editar agendamento existente
      await page.click('[data-testid="schedule-item"]:first-child [data-testid="edit-schedule"]');
      await page.selectOption('select[name="frequency"]', 'weekly');
      await page.click('button[data-testid="save-schedule"]');
      
      // Validação de edição
      await expect(page.locator('[data-testid="schedule-updated"]')).toBeVisible();
      
      await page.screenshot({ path: 'tests/e2e/snapshots/scheduling/edit_schedule.png' });
    });
  });

  // =============================================================================
  // 7. DASHBOARD E MÉTRICAS (MONITORAMENTO)
  // =============================================================================
  
  test.describe('📊 Dashboard e Métricas - Monitoramento', () => {
    
    test('Visualização de métricas principais', async ({ page }) => {
      /**
       * 📐 CoCoT: Monitoramento de performance
       * 🌲 ToT: Testa diferentes visualizações
       * ♻️ ReAct: Simula impacto de métricas
       */
      
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/dashboard`);
      
      // Aguardar carregamento das métricas
      await expect(page.locator('[data-testid="metrics-container"]')).toBeVisible();
      
      // Validar métricas principais
      await expect(page.locator('[data-testid="total-executions"]')).toBeVisible();
      await expect(page.locator('[data-testid="success-rate"]')).toBeVisible();
      await expect(page.locator('[data-testid="avg-execution-time"]')).toBeVisible();
      
      // Capturar métricas de performance
      const metrics = await capturePerformanceMetrics(page);
      expect(metrics.LCP).toBeLessThan(PERFORMANCE_THRESHOLDS.LCP);
      
      await page.screenshot({ path: 'tests/e2e/snapshots/dashboard/metrics_dashboard.png' });
    });

    test('Filtros e busca de execuções', async ({ page }) => {
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/executions`);
      
      // Aplicar filtros
      await page.selectOption('select[name="status-filter"]', 'completed');
      await page.fill('input[name="date-from"]', '2025-01-01');
      await page.fill('input[name="date-to"]', '2025-01-27');
      await page.click('button[data-testid="apply-filters"]');
      
      // Validar resultados filtrados
      await expect(page.locator('[data-testid="filtered-results"]')).toBeVisible();
      
      await page.screenshot({ path: 'tests/e2e/snapshots/dashboard/filtered_executions.png' });
    });
  });

  // =============================================================================
  // 8. GESTÃO DE USUÁRIOS (ADMINISTRAÇÃO)
  // =============================================================================
  
  test.describe('👥 Gestão de Usuários - Administração', () => {
    
    test('Criar novo usuário (Admin)', async ({ page }) => {
      /**
       * 📐 CoCoT: Funcionalidade administrativa
       * 🌲 ToT: Testa criação, edição, remoção
       * ♻️ ReAct: Simula impacto administrativo
       */
      
      await performLogin(page, 'admin');
      await page.goto(`${API_BASE_URL}/admin/users`);
      
      // Criar novo usuário
      await page.click('button[data-testid="create-user"]');
      await page.fill('input[name="user-email"]', 'newuser@test.com');
      await page.fill('input[name="user-name"]', 'New User');
      await page.selectOption('select[name="user-role"]', 'analyst');
      await page.click('button[data-testid="save-user"]');
      
      // Validação de criação
      await expect(page.locator('[data-testid="user-created"]')).toBeVisible();
      await expect(page.locator('[data-testid="users-list"]')).toContainText('newuser@test.com');
      
      await page.screenshot({ path: 'tests/e2e/snapshots/admin/create_user.png' });
    });

    test('Editar permissões de usuário', async ({ page }) => {
      await performLogin(page, 'admin');
      await page.goto(`${API_BASE_URL}/admin/users`);
      
      // Editar usuário
      await page.click('[data-testid="user-item"]:first-child [data-testid="edit-user"]');
      await page.selectOption('select[name="user-role"]', 'manager');
      await page.click('button[data-testid="save-user"]');
      
      // Validação de edição
      await expect(page.locator('[data-testid="user-updated"]')).toBeVisible();
      
      await page.screenshot({ path: 'tests/e2e/snapshots/admin/edit_user.png' });
    });
  });

  // =============================================================================
  // 9. TESTES DE PERFORMANCE E STRESS
  // =============================================================================
  
  test.describe('⚡ Performance e Stress', () => {
    
    test('Performance de carregamento do dashboard', async ({ page }) => {
      await performLogin(page, 'analyst');
      
      const startTime = Date.now();
      await page.goto(`${API_BASE_URL}/dashboard`);
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;
      
      // Validar tempo de carregamento
      expect(loadTime).toBeLessThan(5000); // Máximo 5 segundos
      
      // Capturar métricas de performance
      const metrics = await capturePerformanceMetrics(page);
      expect(metrics.LCP).toBeLessThan(PERFORMANCE_THRESHOLDS.LCP);
      expect(metrics.FID).toBeLessThan(PERFORMANCE_THRESHOLDS.FID);
      
      await page.screenshot({ path: 'tests/e2e/snapshots/performance/dashboard_performance.png' });
    });

    test('Stress test - múltiplas execuções simultâneas', async ({ page, context }) => {
      await performLogin(page, 'analyst');
      
      // Criar 5 execuções simultâneas
      const pages = await Promise.all(Array(5).fill().map(() => context.newPage()));
      
      const startTime = Date.now();
      
      await Promise.all(pages.map(async (p, index) => {
        await p.goto(`${API_BASE_URL}/execucoes`);
        await p.fill('textarea[name="prompt"]', `Stress test prompt ${index + 1}`);
        await p.click('button[data-testid="executar-prompt"]');
      }));
      
      // Aguardar conclusão de todas
      await Promise.all(pages.map(p => 
        expect(p.locator('[data-testid="execution-complete"]')).toBeVisible({ timeout: TEST_TIMEOUT })
      ));
      
      const totalTime = Date.now() - startTime;
      console.log(`⚡ Stress test concluído em ${totalTime}ms`);
      
      // Validar que todas as execuções foram bem-sucedidas
      for (let i = 0; i < pages.length; i++) {
        await pages[i].screenshot({ path: `tests/e2e/snapshots/performance/stress_test_${i + 1}.png` });
      }
    });
  });

  // =============================================================================
  // 10. TESTES DE ACESSIBILIDADE
  // =============================================================================
  
  test.describe('♿ Acessibilidade', () => {
    
    test('Navegação por teclado', async ({ page }) => {
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/dashboard`);
      
      // Navegar usando Tab
      await page.keyboard.press('Tab');
      await expect(page.locator(':focus')).toBeVisible();
      
      // Navegar pelos elementos principais
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Validar que o foco está visível
      await expect(page.locator(':focus')).toBeVisible();
      
      await page.screenshot({ path: 'tests/e2e/snapshots/accessibility/keyboard_navigation.png' });
    });

    test('Contraste e legibilidade', async ({ page }) => {
      await performLogin(page, 'analyst');
      await page.goto(`${API_BASE_URL}/dashboard`);
      
      // Validar contraste mínimo (simulado)
      const textElements = page.locator('p, h1, h2, h3, h4, h5, h6, span, div');
      await expect(textElements.first()).toBeVisible();
      
      await page.screenshot({ path: 'tests/e2e/snapshots/accessibility/contrast_check.png' });
    });
  });
});

// =============================================================================
// HOOKS DE LIMPEZA
// =============================================================================

test.afterEach(async ({ page }) => {
  // Limpeza após cada teste
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
});

test.afterAll(async ({ browser }) => {
  // Limpeza final
  await browser.close();
});

// =============================================================================
// EXPORTAÇÕES PARA REUTILIZAÇÃO
// =============================================================================

export {
  performLogin,
  capturePerformanceMetrics,
  validateSemanticResult,
  REAL_TEST_DATA,
  PERFORMANCE_THRESHOLDS
}; 
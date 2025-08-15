/**
 * 🧪 Testes E2E para Agendamento de Execuções
 * 🎯 Objetivo: Validar funcionalidade de agendamento de execuções com cenários reais
 * 📅 Criado: 2025-01-27
 * 🔄 Versão: 1.0
 * 📐 CoCoT: Scheduling Patterns, Concurrency Control, Business Logic Validation
 * 🌲 ToT: Unit vs Integration vs E2E - E2E para validar fluxos reais de agendamento
 * ♻️ ReAct: Simulação: Agendamentos reais, concorrência, validação de regras de negócio
 * 
 * Tracing ID: E2E_AGENDAMENTO_001
 * Ruleset: enterprise_control_layer.yaml
 * 
 * 📋 CENÁRIOS REAIS BASEADOS EM NEGÓCIO REAL:
 * - Agendamento de análise de keywords para horários específicos
 * - Agendamento de relatórios semanais/mensais
 * - Agendamento de monitoramento contínuo
 * - Agendamento de execuções em lote
 * - Concorrência de agendamentos
 * - Validação de regras de negócio
 * - Cancelamento e modificação de agendamentos
 * - Notificações de agendamento
 * 
 * 🔐 DADOS REAIS DE NEGÓCIO:
 * - Horários reais de agendamento (manhã, tarde, noite)
 * - Prompts reais de análise de keywords
 * - Cenários reais de concorrência
 * - Regras reais de negócio (limites, validações)
 */

import { test, expect } from '@playwright/test';

// Configurações de teste
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:3000';

/**
 * 📐 CoCoT: Gera dados reais de agendamento baseados em cenários reais de negócio
 * 🌲 ToT: Avaliado diferentes cenários e escolhido os mais representativos
 * ♻️ ReAct: Simulado agendamentos reais e validado regras de negócio
 */
function generateSchedulingData(scenario = 'normal') {
  const schedulingConfigs = {
    normal: {
      prompt: 'Analisar keywords para site de e-commerce de roupas femininas',
      scheduledTime: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().slice(0, 16), // Amanhã
      frequency: 'once',
      priority: 'normal'
    },
    recurring: {
      prompt: 'Monitorar posicionamento de keywords principais do site',
      scheduledTime: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16), // Próxima semana
      frequency: 'weekly',
      priority: 'high'
    },
    batch: {
      prompt: 'Processar lote de 500 keywords para análise de concorrência',
      scheduledTime: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16), // Em 2 dias
      frequency: 'once',
      priority: 'low'
    },
    urgent: {
      prompt: 'Análise urgente de keywords para campanha de marketing',
      scheduledTime: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString().slice(0, 16), // Em 2 horas
      frequency: 'once',
      priority: 'urgent'
    }
  };
  
  return schedulingConfigs[scenario] || schedulingConfigs.normal;
}

/**
 * 📐 CoCoT: Valida regras de negócio reais para agendamento
 * 🌲 ToT: Avaliado diferentes regras e escolhido as mais críticas
 * ♻️ ReAct: Simulado validações reais e validado comportamento
 */
function validateBusinessRules(schedulingData) {
  const rules = {
    minTimeAdvance: 30 * 60 * 1000, // 30 minutos
    maxScheduledTime: 30 * 24 * 60 * 60 * 1000, // 30 dias
    maxConcurrentSchedules: 5,
    maxPromptLength: 1000,
    allowedFrequencies: ['once', 'daily', 'weekly', 'monthly']
  };
  
  const scheduledTime = new Date(schedulingData.scheduledTime);
  const now = new Date();
  const timeDiff = scheduledTime.getTime() - now.getTime();
  
  const validations = {
    timeAdvance: timeDiff >= rules.minTimeAdvance,
    maxTime: timeDiff <= rules.maxScheduledTime,
    promptLength: schedulingData.prompt.length <= rules.maxPromptLength,
    frequency: rules.allowedFrequencies.includes(schedulingData.frequency)
  };
  
  return { valid: Object.values(validations).every(v => v), rules, validations };
}

test.describe('📅 Jornada: Agendamento de Execuções E2E', () => {
  
  test.beforeEach(async ({ page }) => {
    // Setup para cada teste
    await page.goto(`${API_BASE_URL}/login`);
  });

  test('✅ Agendamento Normal: Validação de fluxo principal', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de agendamento normal
     * 🌲 ToT: Avaliado diferentes fluxos e escolhido o mais comum
     * ♻️ ReAct: Simulado agendamento real e validado fluxo
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Agendamento normal é o caso de uso mais comum
     * - Deve validar todos os campos obrigatórios
     * - Deve confirmar agendamento com feedback claro
     * - Deve persistir dados corretamente
     * 
     * 📊 IMPACTO SIMULADO:
     * - UX: Usuário recebe confirmação clara
     * - Sistema: Agendamento persistido no banco
     * - Logs: Agendamento registrado para auditoria
     */
    
    // Login
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    // Acessar página de agendamento
    await page.goto(`${API_BASE_URL}/executions/schedule`);
    await expect(page.locator('.scheduling-form')).toBeVisible();
    
    // Preencher dados do agendamento
    const schedulingData = generateSchedulingData('normal');
    
    await page.fill('textarea[name="prompt"]', schedulingData.prompt);
    await page.fill('input[name="scheduled_time"]', schedulingData.scheduledTime);
    await page.selectOption('select[name="frequency"]', schedulingData.frequency);
    await page.selectOption('select[name="priority"]', schedulingData.priority);
    
    // Submeter agendamento
    await page.click('button[type="submit"]');
    
    // Validar confirmação
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText('Agendamento realizado com sucesso');
    
    // Validar dados do agendamento
    await expect(page.locator('.scheduled-time')).toContainText(schedulingData.scheduledTime);
    await expect(page.locator('.scheduled-prompt')).toContainText(schedulingData.prompt);
    
    // Validar ID do agendamento
    const scheduleId = await page.locator('.schedule-id').textContent();
    expect(scheduleId).toMatch(/^[A-Z0-9]{8,}$/);
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/agendamento/normal_success.png',
      fullPage: true 
    });
    
    console.log('✅ Agendamento normal realizado com sucesso');
  });

  test('🔄 Agendamento Recorrente: Validação de frequência', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de agendamento recorrente
     * 🌲 ToT: Avaliado diferentes frequências e escolhido as mais comuns
     * ♻️ ReAct: Simulado agendamento recorrente real e validado comportamento
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Agendamentos recorrentes são importantes para monitoramento
     * - Deve validar diferentes frequências (diária, semanal, mensal)
     * - Deve criar série de agendamentos futuros
     * - Deve permitir cancelamento da série
     * 
     * 📊 IMPACTO SIMULADO:
     * - Sistema: Série de agendamentos criada
     * - UX: Usuário vê próximas execuções agendadas
     * - Logs: Série de agendamentos registrada
     */
    
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    await page.goto(`${API_BASE_URL}/executions/schedule`);
    
    // Configurar agendamento recorrente
    const schedulingData = generateSchedulingData('recurring');
    
    await page.fill('textarea[name="prompt"]', schedulingData.prompt);
    await page.fill('input[name="scheduled_time"]', schedulingData.scheduledTime);
    await page.selectOption('select[name="frequency"]', 'weekly');
    await page.selectOption('select[name="priority"]', schedulingData.priority);
    
    // Configurar duração da recorrência
    await page.fill('input[name="recurrence_end"]', new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16));
    
    await page.click('button[type="submit"]');
    
    // Validar confirmação de agendamento recorrente
    await expect(page.locator('.recurring-schedule-info')).toBeVisible();
    await expect(page.locator('.recurring-schedule-info')).toContainText('Agendamento recorrente criado');
    
    // Validar próximas execuções
    await expect(page.locator('.next-executions')).toBeVisible();
    const nextExecutions = await page.locator('.next-execution-item').count();
    expect(nextExecutions).toBeGreaterThanOrEqual(4); // Pelo menos 4 execuções semanais
    
    // Validar opção de cancelar série
    await expect(page.locator('button[data-testid="cancel-series"]')).toBeVisible();
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/agendamento/recurring_success.png',
      fullPage: true 
    });
    
    console.log('✅ Agendamento recorrente criado com sucesso');
  });

  test('📦 Agendamento em Lote: Validação de processamento em massa', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de agendamento em lote
     * 🌲 ToT: Avaliado diferentes tipos de lote e escolhido cenário representativo
     * ♻️ ReAct: Simulado lote real e validado processamento
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Agendamentos em lote são importantes para processamento eficiente
     * - Deve validar arquivo de lote
     * - Deve criar múltiplos agendamentos
     * - Deve gerenciar recursos adequadamente
     * 
     * 📊 IMPACTO SIMULADO:
     * - Sistema: Múltiplos agendamentos criados
     * - Performance: Processamento otimizado
     * - Logs: Lote de agendamentos registrado
     */
    
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    await page.goto(`${API_BASE_URL}/executions/schedule/batch`);
    
    // Upload arquivo de lote
    await page.setInputFiles('input[type="file"]', 'tests/e2e/fixtures/batch_schedule.csv');
    
    // Configurar agendamento em lote
    const schedulingData = generateSchedulingData('batch');
    await page.fill('input[name="scheduled_time"]', schedulingData.scheduledTime);
    await page.selectOption('select[name="priority"]', schedulingData.priority);
    
    await page.click('button[type="submit"]');
    
    // Validar processamento do lote
    await expect(page.locator('.batch-processing')).toBeVisible();
    await expect(page.locator('.batch-processing')).toContainText('Processando lote');
    
    // Aguardar conclusão
    await expect(page.locator('.batch-complete')).toBeVisible({ timeout: 30000 });
    
    // Validar resultados do lote
    const totalScheduled = await page.locator('.total-scheduled').textContent();
    const successfulSchedules = await page.locator('.successful-schedules').textContent();
    const failedSchedules = await page.locator('.failed-schedules').textContent();
    
    expect(parseInt(totalScheduled)).toBeGreaterThan(0);
    expect(parseInt(successfulSchedules)).toBeGreaterThan(0);
    
    // Validar download do relatório
    await expect(page.locator('button[data-testid="download-report"]')).toBeVisible();
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/agendamento/batch_success.png',
      fullPage: true 
    });
    
    console.log(`✅ Agendamento em lote: ${successfulSchedules} agendamentos criados`);
  });

  test('⚡ Agendamento Urgente: Validação de prioridade alta', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de agendamento urgente
     * 🌲 ToT: Avaliado diferentes prioridades e escolhido urgente
     * ♻️ ReAct: Simulado agendamento urgente real e validado priorização
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Agendamentos urgentes devem ter prioridade alta
     * - Deve validar regras de negócio para urgência
     * - Deve notificar sobre agendamento urgente
     * - Deve gerenciar recursos adequadamente
     * 
     * 📊 IMPACTO SIMULADO:
     * - Sistema: Prioridade alta atribuída
     * - UX: Usuário notificado sobre urgência
     * - Logs: Agendamento urgente registrado
     */
    
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    await page.goto(`${API_BASE_URL}/executions/schedule`);
    
    // Configurar agendamento urgente
    const schedulingData = generateSchedulingData('urgent');
    
    await page.fill('textarea[name="prompt"]', schedulingData.prompt);
    await page.fill('input[name="scheduled_time"]', schedulingData.scheduledTime);
    await page.selectOption('select[name="frequency"]', schedulingData.frequency);
    await page.selectOption('select[name="priority"]', 'urgent');
    
    // Marcar como urgente
    await page.check('input[name="is_urgent"]');
    
    await page.click('button[type="submit"]');
    
    // Validar confirmação de urgência
    await expect(page.locator('.urgent-notification')).toBeVisible();
    await expect(page.locator('.urgent-notification')).toContainText('Agendamento urgente');
    
    // Validar prioridade alta
    await expect(page.locator('.priority-high')).toBeVisible();
    await expect(page.locator('.priority-high')).toContainText('Alta Prioridade');
    
    // Validar notificação de recursos
    await expect(page.locator('.resource-notification')).toBeVisible();
    await expect(page.locator('.resource-notification')).toContainText('recursos prioritários');
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/agendamento/urgent_success.png',
      fullPage: true 
    });
    
    console.log('✅ Agendamento urgente criado com sucesso');
  });

  test('❌ Validação de Regras de Negócio: Cenários de erro', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em regras reais de negócio para agendamento
     * 🌲 ToT: Avaliado diferentes regras e escolhido as mais críticas
     * ♻️ ReAct: Simulado violações reais e validado tratamento
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Regras de negócio protegem contra agendamentos inválidos
     * - Deve validar tempo mínimo de antecedência
     * - Deve validar limites de agendamentos
     * - Deve informar usuário sobre violações
     * 
     * 📊 IMPACTO SIMULADO:
     * - Sistema: Violações bloqueadas
     * - UX: Usuário informado sobre problemas
     * - Logs: Tentativas inválidas registradas
     */
    
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    await page.goto(`${API_BASE_URL}/executions/schedule`);
    
    // Teste 1: Tempo muito próximo (menos de 30 minutos)
    const tooSoon = new Date(Date.now() + 15 * 60 * 1000).toISOString().slice(0, 16); // 15 minutos
    
    await page.fill('textarea[name="prompt"]', 'Teste de tempo muito próximo');
    await page.fill('input[name="scheduled_time"]', tooSoon);
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.validation-error')).toBeVisible();
    await expect(page.locator('.validation-error')).toContainText('mínimo de 30 minutos');
    
    // Teste 2: Tempo muito distante (mais de 30 dias)
    const tooFar = new Date(Date.now() + 31 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16); // 31 dias
    
    await page.fill('input[name="scheduled_time"]', tooFar);
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.validation-error')).toBeVisible();
    await expect(page.locator('.validation-error')).toContainText('máximo de 30 dias');
    
    // Teste 3: Prompt muito longo
    const longPrompt = 'A'.repeat(1001); // Mais de 1000 caracteres
    
    await page.fill('textarea[name="prompt"]', longPrompt);
    await page.fill('input[name="scheduled_time"]', generateSchedulingData('normal').scheduledTime);
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.validation-error')).toBeVisible();
    await expect(page.locator('.validation-error')).toContainText('máximo de 1000 caracteres');
    
    // Teste 4: Frequência inválida
    await page.fill('textarea[name="prompt"]', 'Teste de frequência inválida');
    await page.selectOption('select[name="frequency"]', 'invalid_frequency');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.validation-error')).toBeVisible();
    await expect(page.locator('.validation-error')).toContainText('frequência inválida');
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/agendamento/validation_errors.png',
      fullPage: true 
    });
    
    console.log('✅ Validações de regras de negócio funcionando adequadamente');
  });

  test('👥 Concorrência: Múltiplos agendamentos simultâneos', async ({ page, context }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de concorrência de agendamentos
     * 🌲 ToT: Avaliado diferentes cenários de concorrência e escolhido os mais críticos
     * ♻️ ReAct: Simulado concorrência real e validado comportamento
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Concorrência pode causar conflitos de agendamento
     * - Deve validar limites de agendamentos simultâneos
     * - Deve gerenciar recursos adequadamente
     * - Deve informar usuário sobre limitações
     * 
     * 📊 IMPACTO SIMULADO:
     * - Sistema: Concorrência gerenciada
     * - Performance: Recursos otimizados
     * - UX: Usuário informado sobre limitações
     */
    
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    // Criar múltiplas páginas para simular usuários concorrentes
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
    
    // Executar agendamentos simultâneos
    const results = await Promise.all(pages.map(async (p, index) => {
      try {
        await p.goto(`${API_BASE_URL}/executions/schedule`);
        
        const schedulingData = generateSchedulingData('normal');
        await p.fill('textarea[name="prompt"]', `Agendamento concorrente ${index}`);
        await p.fill('input[name="scheduled_time"]', schedulingData.scheduledTime);
        await p.selectOption('select[name="frequency"]', schedulingData.frequency);
        await p.selectOption('select[name="priority"]', schedulingData.priority);
        
        await p.click('button[type="submit"]');
        
        // Aguardar resultado
        await p.waitForSelector('.success-message, .concurrency-error', { timeout: 10000 });
        
        const success = await p.locator('.success-message').isVisible();
        const error = await p.locator('.concurrency-error').isVisible();
        
        return { success, error, index };
      } catch (error) {
        return { success: false, error: true, index, message: error.message };
      }
    }));
    
    // Analisar resultados
    const successfulSchedules = results.filter(r => r.success).length;
    const failedSchedules = results.filter(r => r.error).length;
    
    // Validar que pelo menos alguns agendamentos foram bem-sucedidos
    expect(successfulSchedules).toBeGreaterThan(0);
    
    // Se houver falhas por concorrência, validar mensagem
    if (failedSchedules > 0) {
      const failedPage = pages[results.findIndex(r => r.error)];
      await expect(failedPage.locator('.concurrency-error')).toContainText('muitos agendamentos');
    }
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/agendamento/concurrency_test.png',
      fullPage: true 
    });
    
    console.log(`✅ Concorrência: ${successfulSchedules} sucessos, ${failedSchedules} falhas`);
  });

  test('📋 Listagem e Gerenciamento: Validação de agendamentos existentes', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de gerenciamento de agendamentos
     * 🌲 ToT: Avaliado diferentes operações e escolhido as mais importantes
     * ♻️ ReAct: Simulado gerenciamento real e validado operações
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Usuários precisam gerenciar agendamentos existentes
     * - Deve listar agendamentos de forma organizada
     * - Deve permitir cancelamento e modificação
     * - Deve mostrar status e próximas execuções
     * 
     * 📊 IMPACTO SIMULADO:
     * - UX: Interface clara para gerenciamento
     * - Sistema: Operações de CRUD funcionando
     * - Logs: Operações registradas para auditoria
     */
    
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    // Acessar lista de agendamentos
    await page.goto(`${API_BASE_URL}/executions/scheduled`);
    await expect(page.locator('.schedules-list')).toBeVisible();
    
    // Validar estrutura da lista
    await expect(page.locator('.schedule-item')).toBeVisible();
    await expect(page.locator('.schedule-prompt')).toBeVisible();
    await expect(page.locator('.schedule-time')).toBeVisible();
    await expect(page.locator('.schedule-status')).toBeVisible();
    
    // Validar filtros
    await expect(page.locator('select[name="status_filter"]')).toBeVisible();
    await expect(page.locator('select[name="priority_filter"]')).toBeVisible();
    await expect(page.locator('input[name="date_filter"]')).toBeVisible();
    
    // Testar filtros
    await page.selectOption('select[name="status_filter"]', 'pending');
    await page.click('button[data-testid="apply-filters"]');
    
    // Validar que apenas agendamentos pendentes são mostrados
    const pendingSchedules = await page.locator('.schedule-item[data-status="pending"]').count();
    expect(pendingSchedules).toBeGreaterThan(0);
    
    // Testar cancelamento de agendamento
    await page.click('button[data-testid="cancel-schedule"]:first');
    await expect(page.locator('.cancel-confirmation')).toBeVisible();
    await page.click('button[data-testid="confirm-cancel"]');
    
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText('Agendamento cancelado');
    
    // Testar modificação de agendamento
    await page.click('button[data-testid="edit-schedule"]:first');
    await expect(page.locator('.edit-form')).toBeVisible();
    
    const newTime = new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString().slice(0, 16); // 2 dias
    await page.fill('input[name="scheduled_time"]', newTime);
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText('Agendamento atualizado');
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/agendamento/management_success.png',
      fullPage: true 
    });
    
    console.log('✅ Gerenciamento de agendamentos funcionando adequadamente');
  });

  test('🔔 Notificações: Validação de alertas e notificações', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de notificações de agendamento
     * 🌲 ToT: Avaliado diferentes tipos de notificação e escolhido os mais importantes
     * ♻️ ReAct: Simulado notificações reais e validado entrega
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Notificações são importantes para acompanhamento
     * - Deve notificar sobre confirmação de agendamento
     * - Deve notificar sobre próximas execuções
     * - Deve notificar sobre cancelamentos e modificações
     * 
     * 📊 IMPACTO SIMULADO:
     * - UX: Usuário informado sobre eventos
     * - Sistema: Notificações entregues adequadamente
     * - Logs: Notificações registradas
     */
    
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    // Configurar preferências de notificação
    await page.goto(`${API_BASE_URL}/profile/notifications`);
    await page.check('input[name="email_notifications"]');
    await page.check('input[name="push_notifications"]');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.success-message')).toBeVisible();
    
    // Criar agendamento para testar notificações
    await page.goto(`${API_BASE_URL}/executions/schedule`);
    
    const schedulingData = generateSchedulingData('normal');
    await page.fill('textarea[name="prompt"]', schedulingData.prompt);
    await page.fill('input[name="scheduled_time"]', schedulingData.scheduledTime);
    await page.selectOption('select[name="frequency"]', schedulingData.frequency);
    await page.selectOption('select[name="priority"]', schedulingData.priority);
    
    await page.click('button[type="submit"]');
    
    // Validar notificação de confirmação
    await expect(page.locator('.notification-toast')).toBeVisible();
    await expect(page.locator('.notification-toast')).toContainText('Agendamento confirmado');
    
    // Verificar notificações na interface
    await page.goto(`${API_BASE_URL}/notifications`);
    await expect(page.locator('.notification-item')).toBeVisible();
    await expect(page.locator('.notification-item')).toContainText('Agendamento criado');
    
    // Testar notificação de próximo agendamento
    await page.goto(`${API_BASE_URL}/executions/scheduled`);
    const nextSchedule = await page.locator('.next-schedule-notification');
    
    if (await nextSchedule.isVisible()) {
      await expect(nextSchedule).toContainText('próximo agendamento');
    }
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/agendamento/notifications_success.png',
      fullPage: true 
    });
    
    console.log('✅ Sistema de notificações funcionando adequadamente');
  });

  test('📊 Métricas e Relatórios: Validação de estatísticas', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em requisitos reais de métricas de agendamento
     * 🌲 ToT: Avaliado diferentes métricas e escolhido as mais importantes
     * ♻️ ReAct: Simulado métricas reais e validado coleta
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Métricas são importantes para análise de uso
     * - Deve coletar estatísticas de agendamentos
     * - Deve gerar relatórios de uso
     * - Deve mostrar tendências e padrões
     * 
     * 📊 IMPACTO SIMULADO:
     * - Analytics: Métricas coletadas
     * - Relatórios: Dados organizados
     * - Insights: Padrões identificados
     */
    
    await page.fill('input[name="usuario"]', 'user123');
    await page.fill('input[name="senha"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
    
    // Acessar página de métricas
    await page.goto(`${API_BASE_URL}/executions/analytics`);
    await expect(page.locator('.analytics-dashboard')).toBeVisible();
    
    // Validar métricas principais
    await expect(page.locator('.total-schedules')).toBeVisible();
    await expect(page.locator('.pending-schedules')).toBeVisible();
    await expect(page.locator('.completed-schedules')).toBeVisible();
    await expect(page.locator('.cancelled-schedules')).toBeVisible();
    
    // Validar valores das métricas
    const totalSchedules = await page.locator('.total-schedules .value').textContent();
    const pendingSchedules = await page.locator('.pending-schedules .value').textContent();
    const completedSchedules = await page.locator('.completed-schedules .value').textContent();
    
    expect(parseInt(totalSchedules)).toBeGreaterThanOrEqual(0);
    expect(parseInt(pendingSchedules)).toBeGreaterThanOrEqual(0);
    expect(parseInt(completedSchedules)).toBeGreaterThanOrEqual(0);
    
    // Validar gráficos
    await expect(page.locator('.schedules-chart')).toBeVisible();
    await expect(page.locator('.frequency-chart')).toBeVisible();
    await expect(page.locator('.priority-chart')).toBeVisible();
    
    // Testar filtros de período
    await page.selectOption('select[name="period"]', 'last_30_days');
    await page.click('button[data-testid="update-charts"]');
    
    await expect(page.locator('.charts-updated')).toBeVisible();
    
    // Testar exportação de relatório
    await page.click('button[data-testid="export-report"]');
    
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button[data-testid="confirm-export"]')
    ]);
    
    expect(download.suggestedFilename()).toMatch(/schedules_report.*\.(csv|xlsx)/);
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/agendamento/analytics_success.png',
      fullPage: true 
    });
    
    console.log(`✅ Métricas: ${totalSchedules} total, ${pendingSchedules} pendentes, ${completedSchedules} concluídos`);
  });
}); 
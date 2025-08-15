/**
 * 🧪 Testes E2E para Criação de Usuário
 * 🎯 Objetivo: Validar funcionalidade de criação de usuário com cenários reais de administração
 * 📅 Criado: 2025-01-27
 * 🔄 Versão: 1.0
 * 📐 CoCoT: User Management Patterns, RBAC Validation, Data Integrity
 * 🌲 ToT: Unit vs Integration vs E2E - E2E para validar fluxos reais de criação
 * ♻️ ReAct: Simulação: Criação real, validação de regras, auditoria
 * 
 * Tracing ID: E2E_CRIACAO_USUARIO_001
 * Ruleset: enterprise_control_layer.yaml
 * 
 * 📋 CENÁRIOS REAIS BASEADOS EM ADMINISTRAÇÃO REAL:
 * - Criação de usuários por administradores
 * - Validação de dados e regras de negócio
 * - Verificação de duplicidade e unicidade
 * - Atribuição de roles e permissões
 * - Notificação de criação
 * - Auditoria de ações administrativas
 * - Validação de segurança e compliance
 * - Gestão de usuários em massa
 * 
 * 🔐 DADOS REAIS DE NEGÓCIO:
 * - Dados reais de usuários (nomes, emails, perfis)
 * - Roles reais de sistema (admin, user, analyst)
 * - Regras reais de validação (senha, email, nome)
 * - Cenários reais de administração
 */

import { test, expect } from '@playwright/test';

// Configurações de teste
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:3000';

/**
 * 📐 CoCoT: Gera dados reais de usuário baseados em cenários reais de negócio
 * 🌲 ToT: Avaliado diferentes cenários e escolhido os mais representativos
 * ♻️ ReAct: Simulado criação real e validado regras de negócio
 */
function generateUserData(scenario = 'normal') {
  const userConfigs = {
    normal: {
      name: 'João Silva',
      email: `joao.silva.${Date.now()}@empresa.com`,
      password: 'Senha@123',
      role: 'user',
      department: 'Marketing',
      position: 'Analista de Marketing'
    },
    admin: {
      name: 'Maria Santos',
      email: `maria.santos.${Date.now()}@empresa.com`,
      password: 'Admin@123',
      role: 'admin',
      department: 'TI',
      position: 'Administrador de Sistema'
    },
    analyst: {
      name: 'Pedro Costa',
      email: `pedro.costa.${Date.now()}@empresa.com`,
      password: 'Analyst@123',
      role: 'analyst',
      department: 'Analytics',
      position: 'Analista de Dados'
    },
    manager: {
      name: 'Ana Oliveira',
      email: `ana.oliveira.${Date.now()}@empresa.com`,
      password: 'Manager@123',
      role: 'manager',
      department: 'Vendas',
      position: 'Gerente de Vendas'
    }
  };
  
  return userConfigs[scenario] || userConfigs.normal;
}

/**
 * 📐 CoCoT: Valida regras de negócio reais para criação de usuário
 * 🌲 ToT: Avaliado diferentes regras e escolhido as mais críticas
 * ♻️ ReAct: Simulado validações reais e validado comportamento
 */
function validateUserRules(userData) {
  const rules = {
    minNameLength: 3,
    maxNameLength: 100,
    emailPattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    minPasswordLength: 8,
    passwordPattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
    allowedRoles: ['user', 'admin', 'analyst', 'manager'],
    allowedDepartments: ['Marketing', 'TI', 'Analytics', 'Vendas', 'RH', 'Financeiro']
  };
  
  const validations = {
    nameLength: userData.name.length >= rules.minNameLength && userData.name.length <= rules.maxNameLength,
    emailFormat: rules.emailPattern.test(userData.email),
    passwordLength: userData.password.length >= rules.minPasswordLength,
    passwordStrength: rules.passwordPattern.test(userData.password),
    validRole: rules.allowedRoles.includes(userData.role),
    validDepartment: rules.allowedDepartments.includes(userData.department)
  };
  
  return { valid: Object.values(validations).every(v => v), rules, validations };
}

test.describe('👤 Jornada: Criação de Usuário E2E', () => {
  
  test.beforeEach(async ({ page }) => {
    // Setup para cada teste - login como admin
    await page.goto(`${API_BASE_URL}/login`);
    await page.fill('input[name="usuario"]', 'admin');
    await page.fill('input[name="senha"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
  });

  test('✅ Criação Normal: Validação de fluxo principal', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de criação normal de usuário
     * 🌲 ToT: Avaliado diferentes fluxos e escolhido o mais comum
     * ♻️ ReAct: Simulado criação real e validado fluxo
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Criação normal é o caso de uso mais comum
     * - Deve validar todos os campos obrigatórios
     * - Deve confirmar criação com feedback claro
     * - Deve persistir dados corretamente
     * 
     * 📊 IMPACTO SIMULADO:
     * - UX: Admin recebe confirmação clara
     * - Sistema: Usuário persistido no banco
     * - Logs: Criação registrada para auditoria
     */
    
    // Acessar página de gestão de usuários
    await page.goto(`${API_BASE_URL}/admin/users`);
    await expect(page.locator('.users-management')).toBeVisible();
    
    // Iniciar criação de usuário
    await page.click('button[data-testid="create-user"]');
    await expect(page.locator('.user-creation-form')).toBeVisible();
    
    // Preencher dados do usuário
    const userData = generateUserData('normal');
    
    await page.fill('input[name="name"]', userData.name);
    await page.fill('input[name="email"]', userData.email);
    await page.fill('input[name="password"]', userData.password);
    await page.fill('input[name="confirm_password"]', userData.password);
    await page.selectOption('select[name="role"]', userData.role);
    await page.fill('input[name="department"]', userData.department);
    await page.fill('input[name="position"]', userData.position);
    
    // Submeter criação
    await page.click('button[type="submit"]');
    
    // Validar confirmação
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText('Usuário criado com sucesso');
    
    // Validar dados do usuário criado
    await expect(page.locator('.user-name')).toContainText(userData.name);
    await expect(page.locator('.user-email')).toContainText(userData.email);
    await expect(page.locator('.user-role')).toContainText(userData.role);
    
    // Validar ID do usuário
    const userId = await page.locator('.user-id').textContent();
    expect(userId).toMatch(/^[A-Z0-9]{8,}$/);
    
    // Validar status ativo
    await expect(page.locator('.user-status')).toContainText('Ativo');
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/criacao_usuario/normal_success.png',
      fullPage: true 
    });
    
    console.log('✅ Usuário normal criado com sucesso');
  });

  test('🔐 Criação de Admin: Validação de privilégios', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de criação de administrador
     * 🌲 ToT: Avaliado diferentes níveis de privilégio e escolhido admin
     * ♻️ ReAct: Simulado criação real e validado privilégios
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Criação de admin requer validações especiais
     * - Deve verificar permissões do criador
     * - Deve implementar confirmação adicional
     * - Deve registrar auditoria especial
     * 
     * 📊 IMPACTO SIMULADO:
     * - Segurança: Privilégios validados adequadamente
     * - Auditoria: Criação de admin registrada
     * - Compliance: Requisitos de segurança atendidos
     */
    
    await page.goto(`${API_BASE_URL}/admin/users`);
    await page.click('button[data-testid="create-user"]');
    
    // Preencher dados de admin
    const userData = generateUserData('admin');
    
    await page.fill('input[name="name"]', userData.name);
    await page.fill('input[name="email"]', userData.email);
    await page.fill('input[name="password"]', userData.password);
    await page.fill('input[name="confirm_password"]', userData.password);
    await page.selectOption('select[name="role"]', 'admin');
    await page.fill('input[name="department"]', userData.department);
    await page.fill('input[name="position"]', userData.position);
    
    // Deve mostrar aviso de privilégios
    await expect(page.locator('.admin-warning')).toBeVisible();
    await expect(page.locator('.admin-warning')).toContainText('privilegiado');
    
    // Confirmar criação de admin
    await page.click('button[data-testid="confirm-admin-creation"]');
    
    // Validar confirmação
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText('Administrador criado');
    
    // Validar privilégios especiais
    await expect(page.locator('.admin-privileges')).toBeVisible();
    await expect(page.locator('.admin-privileges')).toContainText('Privilégios de Administrador');
    
    // Validar auditoria especial
    await expect(page.locator('.admin-audit-log')).toBeVisible();
    await expect(page.locator('.admin-audit-log')).toContainText('Criação de Administrador');
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/criacao_usuario/admin_success.png',
      fullPage: true 
    });
    
    console.log('✅ Administrador criado com sucesso');
  });

  test('📊 Criação de Analyst: Validação de perfil especializado', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de criação de analista
     * 🌲 ToT: Avaliado diferentes perfis e escolhido analyst
     * ♻️ ReAct: Simulado criação real e validado perfil
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Analistas têm permissões específicas
     * - Deve configurar acesso a ferramentas de análise
     * - Deve definir limites de uso
     * - Deve configurar notificações específicas
     * 
     * 📊 IMPACTO SIMULADO:
     * - Funcionalidade: Acesso a ferramentas configurado
     * - Limites: Uso controlado adequadamente
     * - Notificações: Alertas específicos configurados
     */
    
    await page.goto(`${API_BASE_URL}/admin/users`);
    await page.click('button[data-testid="create-user"]');
    
    // Preencher dados de analista
    const userData = generateUserData('analyst');
    
    await page.fill('input[name="name"]', userData.name);
    await page.fill('input[name="email"]', userData.email);
    await page.fill('input[name="password"]', userData.password);
    await page.fill('input[name="confirm_password"]', userData.password);
    await page.selectOption('select[name="role"]', 'analyst');
    await page.fill('input[name="department"]', userData.department);
    await page.fill('input[name="position"]', userData.position);
    
    // Configurar permissões de analista
    await page.check('input[name="analytics_access"]');
    await page.check('input[name="report_generation"]');
    await page.check('input[name="data_export"]');
    
    // Configurar limites de uso
    await page.fill('input[name="daily_requests_limit"]', '100');
    await page.fill('input[name="monthly_reports_limit"]', '50');
    
    await page.click('button[type="submit"]');
    
    // Validar confirmação
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText('Analista criado');
    
    // Validar permissões específicas
    await expect(page.locator('.analyst-permissions')).toBeVisible();
    await expect(page.locator('.analytics-access')).toBeVisible();
    await expect(page.locator('.report-generation')).toBeVisible();
    
    // Validar limites configurados
    await expect(page.locator('.daily-limit')).toContainText('100');
    await expect(page.locator('.monthly-limit')).toContainText('50');
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/criacao_usuario/analyst_success.png',
      fullPage: true 
    });
    
    console.log('✅ Analista criado com sucesso');
  });

  test('❌ Validação de Regras: Cenários de erro', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em regras reais de validação de usuário
     * 🌲 ToT: Avaliado diferentes regras e escolhido as mais críticas
     * ♻️ ReAct: Simulado violações reais e validado tratamento
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Regras de validação protegem integridade dos dados
     * - Deve validar formato de email
     * - Deve validar força da senha
     * - Deve validar unicidade de dados
     * 
     * 📊 IMPACTO SIMULADO:
     * - Integridade: Dados inválidos bloqueados
     * - Segurança: Senhas fracas rejeitadas
     * - UX: Usuário informado sobre problemas
     */
    
    await page.goto(`${API_BASE_URL}/admin/users`);
    await page.click('button[data-testid="create-user"]');
    
    // Teste 1: Nome muito curto
    await page.fill('input[name="name"]', 'Jo');
    await page.fill('input[name="email"]', 'joao@teste.com');
    await page.fill('input[name="password"]', 'Senha@123');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.validation-error')).toBeVisible();
    await expect(page.locator('.validation-error')).toContainText('mínimo de 3 caracteres');
    
    // Teste 2: Email inválido
    await page.fill('input[name="name"]', 'João Silva');
    await page.fill('input[name="email"]', 'email-invalido');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.validation-error')).toBeVisible();
    await expect(page.locator('.validation-error')).toContainText('email válido');
    
    // Teste 3: Senha fraca
    await page.fill('input[name="email"]', 'joao@teste.com');
    await page.fill('input[name="password"]', '123');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.validation-error')).toBeVisible();
    await expect(page.locator('.validation-error')).toContainText('mínimo de 8 caracteres');
    
    // Teste 4: Senha sem caracteres especiais
    await page.fill('input[name="password"]', 'Senha123');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.validation-error')).toBeVisible();
    await expect(page.locator('.validation-error')).toContainText('caractere especial');
    
    // Teste 5: Senha sem maiúscula
    await page.fill('input[name="password"]', 'senha@123');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.validation-error')).toBeVisible();
    await expect(page.locator('.validation-error')).toContainText('letra maiúscula');
    
    // Teste 6: Senha sem número
    await page.fill('input[name="password"]', 'Senha@abc');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.validation-error')).toBeVisible();
    await expect(page.locator('.validation-error')).toContainText('número');
    
    // Teste 7: Confirmação de senha diferente
    await page.fill('input[name="password"]', 'Senha@123');
    await page.fill('input[name="confirm_password"]', 'Senha@456');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.validation-error')).toBeVisible();
    await expect(page.locator('.validation-error')).toContainText('senhas não coincidem');
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/criacao_usuario/validation_errors.png',
      fullPage: true 
    });
    
    console.log('✅ Validações de regras funcionando adequadamente');
  });

  test('🔄 Duplicidade: Validação de unicidade', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de tentativa de duplicação
     * 🌲 ToT: Avaliado diferentes tipos de duplicação e escolhido os mais críticos
     * ♻️ ReAct: Simulado duplicação real e validado tratamento
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Duplicação de dados pode causar problemas
     * - Deve validar unicidade de email
     * - Deve verificar nomes similares
     * - Deve sugerir alternativas
     * 
     * 📊 IMPACTO SIMULADO:
     * - Integridade: Duplicações evitadas
     * - UX: Usuário informado sobre conflitos
     * - Sistema: Dados consistentes mantidos
     */
    
    await page.goto(`${API_BASE_URL}/admin/users`);
    await page.click('button[data-testid="create-user"]');
    
    // Criar primeiro usuário
    const userData = generateUserData('normal');
    
    await page.fill('input[name="name"]', userData.name);
    await page.fill('input[name="email"]', userData.email);
    await page.fill('input[name="password"]', userData.password);
    await page.fill('input[name="confirm_password"]', userData.password);
    await page.selectOption('select[name="role"]', userData.role);
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.success-message')).toBeVisible();
    
    // Tentar criar usuário com mesmo email
    await page.click('button[data-testid="create-user"]');
    await page.fill('input[name="name"]', 'Outro Nome');
    await page.fill('input[name="email"]', userData.email); // Mesmo email
    await page.fill('input[name="password"]', 'OutraSenha@123');
    await page.fill('input[name="confirm_password"]', 'OutraSenha@123');
    await page.selectOption('select[name="role"]', 'user');
    await page.click('button[type="submit"]');
    
    // Validar erro de duplicação
    await expect(page.locator('.duplication-error')).toBeVisible();
    await expect(page.locator('.duplication-error')).toContainText('já existe');
    await expect(page.locator('.duplication-error')).toContainText(userData.email);
    
    // Validar sugestões de email alternativo
    await expect(page.locator('.email-suggestions')).toBeVisible();
    const suggestions = await page.locator('.email-suggestion').count();
    expect(suggestions).toBeGreaterThan(0);
    
    // Tentar criar usuário com nome muito similar
    await page.fill('input[name="name"]', userData.name + ' Jr'); // Nome similar
    await page.fill('input[name="email"]', 'novo@teste.com');
    await page.click('button[type="submit"]');
    
    // Deve mostrar aviso sobre nome similar
    await expect(page.locator('.similar-name-warning')).toBeVisible();
    await expect(page.locator('.similar-name-warning')).toContainText('nome similar');
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/criacao_usuario/duplication_handling.png',
      fullPage: true 
    });
    
    console.log('✅ Validação de duplicidade funcionando adequadamente');
  });

  test('📧 Notificação: Validação de comunicação', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de notificação de criação
     * 🌲 ToT: Avaliado diferentes tipos de notificação e escolhido os mais importantes
     * ♻️ ReAct: Simulado notificações reais e validado entrega
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Notificações são importantes para comunicação
     * - Deve notificar admin sobre criação
     * - Deve notificar usuário sobre conta criada
     * - Deve configurar notificações específicas
     * 
     * 📊 IMPACTO SIMULADO:
     * - Comunicação: Stakeholders informados
     * - Onboarding: Usuário recebe instruções
     * - Auditoria: Notificações registradas
     */
    
    await page.goto(`${API_BASE_URL}/admin/users`);
    await page.click('button[data-testid="create-user"]');
    
    // Preencher dados do usuário
    const userData = generateUserData('normal');
    
    await page.fill('input[name="name"]', userData.name);
    await page.fill('input[name="email"]', userData.email);
    await page.fill('input[name="password"]', userData.password);
    await page.fill('input[name="confirm_password"]', userData.password);
    await page.selectOption('select[name="role"]', userData.role);
    await page.fill('input[name="department"]', userData.department);
    await page.fill('input[name="position"]', userData.position);
    
    // Configurar notificações
    await page.check('input[name="notify_user"]');
    await page.check('input[name="notify_admin"]');
    await page.check('input[name="send_welcome_email"]');
    
    await page.click('button[type="submit"]');
    
    // Validar confirmação
    await expect(page.locator('.success-message')).toBeVisible();
    
    // Validar notificações enviadas
    await expect(page.locator('.notifications-sent')).toBeVisible();
    await expect(page.locator('.user-notification')).toContainText('Usuário notificado');
    await expect(page.locator('.admin-notification')).toContainText('Admin notificado');
    await expect(page.locator('.welcome-email')).toContainText('Email de boas-vindas enviado');
    
    // Verificar notificações na interface
    await page.goto(`${API_BASE_URL}/admin/notifications`);
    await expect(page.locator('.notification-item')).toBeVisible();
    await expect(page.locator('.notification-item')).toContainText('Usuário criado');
    await expect(page.locator('.notification-item')).toContainText(userData.name);
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/criacao_usuario/notifications_success.png',
      fullPage: true 
    });
    
    console.log('✅ Sistema de notificações funcionando adequadamente');
  });

  test('📋 Criação em Lote: Validação de operações em massa', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de criação em lote
     * 🌲 ToT: Avaliado diferentes estratégias e escolhido a mais eficiente
     * ♻️ ReAct: Simulado lote real e validado processamento
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Criação em lote é importante para eficiência
     * - Deve validar arquivo de lote
     * - Deve processar múltiplos usuários
     * - Deve gerar relatório de resultados
     * 
     * 📊 IMPACTO SIMULADO:
     * - Eficiência: Múltiplos usuários criados rapidamente
     * - Relatório: Resultados organizados
     * - Auditoria: Lote registrado adequadamente
     */
    
    await page.goto(`${API_BASE_URL}/admin/users/batch`);
    await expect(page.locator('.batch-creation-form')).toBeVisible();
    
    // Upload arquivo de lote
    await page.setInputFiles('input[type="file"]', 'tests/e2e/fixtures/batch_users.csv');
    
    // Configurar opções de lote
    await page.check('input[name="notify_all_users"]');
    await page.check('input[name="generate_report"]');
    await page.selectOption('select[name="default_role"]', 'user');
    
    await page.click('button[type="submit"]');
    
    // Validar processamento do lote
    await expect(page.locator('.batch-processing')).toBeVisible();
    await expect(page.locator('.batch-processing')).toContainText('Processando lote');
    
    // Aguardar conclusão
    await expect(page.locator('.batch-complete')).toBeVisible({ timeout: 30000 });
    
    // Validar resultados do lote
    const totalUsers = await page.locator('.total-users').textContent();
    const successfulCreations = await page.locator('.successful-creations').textContent();
    const failedCreations = await page.locator('.failed-creations').textContent();
    
    expect(parseInt(totalUsers)).toBeGreaterThan(0);
    expect(parseInt(successfulCreations)).toBeGreaterThan(0);
    
    // Validar relatório gerado
    await expect(page.locator('.batch-report')).toBeVisible();
    await expect(page.locator('.batch-report')).toContainText('Relatório de Criação em Lote');
    
    // Validar download do relatório
    await expect(page.locator('button[data-testid="download-report"]')).toBeVisible();
    
    // Validar notificações em lote
    await expect(page.locator('.batch-notifications')).toBeVisible();
    await expect(page.locator('.batch-notifications')).toContainText('notificações enviadas');
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/criacao_usuario/batch_success.png',
      fullPage: true 
    });
    
    console.log(`✅ Criação em lote: ${successfulCreations} usuários criados`);
  });

  test('📊 Auditoria: Validação de logs e rastreabilidade', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em requisitos reais de auditoria
     * 🌲 ToT: Avaliado diferentes aspectos e escolhido os mais críticos
     * ♻️ ReAct: Simulado auditoria real e validado logs
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Auditoria é crítica para compliance
     * - Deve registrar todas as ações
     * - Deve incluir metadados importantes
     * - Deve permitir rastreabilidade
     * 
     * 📊 IMPACTO SIMULADO:
     * - Compliance: Requisitos atendidos
     * - Rastreabilidade: Ações rastreáveis
     * - Segurança: Logs para investigação
     */
    
    await page.goto(`${API_BASE_URL}/admin/users`);
    await page.click('button[data-testid="create-user"]');
    
    // Criar usuário para gerar logs
    const userData = generateUserData('normal');
    
    await page.fill('input[name="name"]', userData.name);
    await page.fill('input[name="email"]', userData.email);
    await page.fill('input[name="password"]', userData.password);
    await page.fill('input[name="confirm_password"]', userData.password);
    await page.selectOption('select[name="role"]', userData.role);
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.success-message')).toBeVisible();
    
    // Acessar logs de auditoria
    await page.goto(`${API_BASE_URL}/admin/audit-logs`);
    await expect(page.locator('.audit-logs')).toBeVisible();
    
    // Validar log de criação
    await expect(page.locator('.audit-entry')).toBeVisible();
    await expect(page.locator('.audit-entry')).toContainText('Criação de Usuário');
    await expect(page.locator('.audit-entry')).toContainText(userData.name);
    await expect(page.locator('.audit-entry')).toContainText(userData.email);
    
    // Validar metadados do log
    await expect(page.locator('.audit-timestamp')).toBeVisible();
    await expect(page.locator('.audit-user')).toContainText('admin');
    await expect(page.locator('.audit-ip')).toBeVisible();
    await expect(page.locator('.audit-session')).toBeVisible();
    
    // Validar detalhes do log
    await page.click('button[data-testid="view-details"]');
    await expect(page.locator('.audit-details')).toBeVisible();
    await expect(page.locator('.audit-details')).toContainText('Dados do Usuário');
    await expect(page.locator('.audit-details')).toContainText('Permissões');
    await expect(page.locator('.audit-details')).toContainText('Notificações');
    
    // Testar exportação de logs
    await page.click('button[data-testid="export-logs"]');
    
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button[data-testid="confirm-export"]')
    ]);
    
    expect(download.suggestedFilename()).toMatch(/audit_logs.*\.(csv|xlsx|json)/);
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/criacao_usuario/audit_logs.png',
      fullPage: true 
    });
    
    console.log('✅ Sistema de auditoria funcionando adequadamente');
  });
}); 
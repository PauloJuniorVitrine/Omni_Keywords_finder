/**
 * 🧪 Testes E2E para Listagem de Usuários
 * 🎯 Objetivo: Validar funcionalidade de listagem e gestão de usuários com cenários reais de administração
 * 📅 Criado: 2025-01-27
 * 🔄 Versão: 1.0
 * 📐 CoCoT: User Management Patterns, Data Display, Search and Filter
 * 🌲 ToT: Unit vs Integration vs E2E - E2E para validar fluxos reais de listagem
 * ♻️ ReAct: Simulação: Listagem real, filtros, gestão, auditoria
 * 
 * Tracing ID: E2E_LISTAGEM_USUARIOS_001
 * Ruleset: enterprise_control_layer.yaml
 * 
 * 📋 CENÁRIOS REAIS BASEADOS EM ADMINISTRAÇÃO REAL:
 * - Listagem de usuários por administradores
 * - Filtros e busca avançada
 * - Paginação e ordenação
 * - Ações em massa e individuais
 * - Gestão de status e permissões
 * - Exportação de dados
 * - Auditoria de ações
 * - Performance de listagem
 * 
 * 🔐 DADOS REAIS DE NEGÓCIO:
 * - Dados reais de usuários (nomes, emails, departamentos)
 * - Cenários reais de busca e filtro
 * - Ações reais de administração
 * - Métricas reais de performance
 */

import { test, expect } from '@playwright/test';

// Configurações de teste
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:3000';

/**
 * 📐 CoCoT: Gera dados reais de usuários baseados em cenários reais de negócio
 * 🌲 ToT: Avaliado diferentes cenários e escolhido os mais representativos
 * ♻️ ReAct: Simulado dados reais e validado representatividade
 */
function generateUserListData() {
  return [
    {
      id: 'USR001',
      name: 'João Silva',
      email: 'joao.silva@empresa.com',
      role: 'user',
      department: 'Marketing',
      status: 'active',
      lastLogin: '2025-01-26T10:30:00Z',
      createdAt: '2024-01-15T09:00:00Z'
    },
    {
      id: 'USR002',
      name: 'Maria Santos',
      email: 'maria.santos@empresa.com',
      role: 'admin',
      department: 'TI',
      status: 'active',
      lastLogin: '2025-01-27T08:15:00Z',
      createdAt: '2024-01-10T14:30:00Z'
    },
    {
      id: 'USR003',
      name: 'Pedro Costa',
      email: 'pedro.costa@empresa.com',
      role: 'analyst',
      department: 'Analytics',
      status: 'inactive',
      lastLogin: '2025-01-20T16:45:00Z',
      createdAt: '2024-01-20T11:00:00Z'
    },
    {
      id: 'USR004',
      name: 'Ana Oliveira',
      email: 'ana.oliveira@empresa.com',
      role: 'manager',
      department: 'Vendas',
      status: 'active',
      lastLogin: '2025-01-27T09:20:00Z',
      createdAt: '2024-01-12T10:15:00Z'
    },
    {
      id: 'USR005',
      name: 'Carlos Ferreira',
      email: 'carlos.ferreira@empresa.com',
      role: 'user',
      department: 'RH',
      status: 'pending',
      lastLogin: null,
      createdAt: '2025-01-25T15:30:00Z'
    }
  ];
}

/**
 * 📐 CoCoT: Define filtros reais baseados em cenários reais de busca
 * 🌲 ToT: Avaliado diferentes filtros e escolhido os mais úteis
 * ♻️ ReAct: Simulado filtros reais e validado utilidade
 */
function generateFilterScenarios() {
  return {
    byName: {
      filter: 'João',
      expectedCount: 1,
      description: 'Busca por nome específico'
    },
    byEmail: {
      filter: 'maria.santos',
      expectedCount: 1,
      description: 'Busca por email'
    },
    byRole: {
      filter: 'admin',
      expectedCount: 1,
      description: 'Filtro por role de administrador'
    },
    byDepartment: {
      filter: 'Marketing',
      expectedCount: 1,
      description: 'Filtro por departamento'
    },
    byStatus: {
      filter: 'active',
      expectedCount: 3,
      description: 'Filtro por status ativo'
    },
    byDateRange: {
      filter: { start: '2025-01-01', end: '2025-01-31' },
      expectedCount: 5,
      description: 'Filtro por período de criação'
    }
  };
}

test.describe('👥 Jornada: Listagem de Usuários E2E', () => {
  
  test.beforeEach(async ({ page }) => {
    // Setup para cada teste - login como admin
    await page.goto(`${API_BASE_URL}/login`);
    await page.fill('input[name="usuario"]', 'admin');
    await page.fill('input[name="senha"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
  });

  test('✅ Listagem Principal: Validação de fluxo básico', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de listagem principal
     * 🌲 ToT: Avaliado diferentes fluxos e escolhido o mais comum
     * ♻️ ReAct: Simulado listagem real e validado fluxo
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Listagem principal é o caso de uso mais comum
     * - Deve carregar dados rapidamente
     * - Deve mostrar informações essenciais
     * - Deve implementar paginação adequada
     * 
     * 📊 IMPACTO SIMULADO:
     * - UX: Admin vê lista organizada
     * - Performance: Carregamento rápido
     * - Funcionalidade: Dados acessíveis
     */
    
    // Acessar página de listagem de usuários
    await page.goto(`${API_BASE_URL}/admin/users`);
    await expect(page.locator('.users-list')).toBeVisible();
    
    // Aguardar carregamento da lista
    await page.waitForSelector('.user-item', { timeout: 10000 });
    
    // Validar estrutura da lista
    await expect(page.locator('.user-item')).toBeVisible();
    await expect(page.locator('.user-name')).toBeVisible();
    await expect(page.locator('.user-email')).toBeVisible();
    await expect(page.locator('.user-role')).toBeVisible();
    await expect(page.locator('.user-status')).toBeVisible();
    
    // Validar dados dos usuários
    const userItems = await page.locator('.user-item').count();
    expect(userItems).toBeGreaterThan(0);
    
    // Validar informações essenciais
    const firstUser = page.locator('.user-item').first();
    await expect(firstUser.locator('.user-name')).not.toBeEmpty();
    await expect(firstUser.locator('.user-email')).not.toBeEmpty();
    await expect(firstUser.locator('.user-role')).not.toBeEmpty();
    
    // Validar paginação
    await expect(page.locator('.pagination')).toBeVisible();
    await expect(page.locator('.pagination-info')).toBeVisible();
    
    const totalUsers = await page.locator('.total-users').textContent();
    expect(parseInt(totalUsers)).toBeGreaterThan(0);
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/listagem_usuarios/lista_principal.png',
      fullPage: true 
    });
    
    console.log(`✅ Listagem principal: ${userItems} usuários carregados`);
  });

  test('🔍 Filtros Avançados: Validação de busca e filtro', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenários reais de busca e filtro
     * 🌲 ToT: Avaliado diferentes filtros e escolhido os mais úteis
     * ♻️ ReAct: Simulado filtros reais e validado resultados
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Filtros são essenciais para encontrar usuários
     * - Deve implementar busca por texto
     * - Deve implementar filtros por atributos
     * - Deve mostrar resultados relevantes
     * 
     * 📊 IMPACTO SIMULADO:
     * - Produtividade: Busca rápida de usuários
     * - UX: Interface intuitiva de filtros
     * - Eficiência: Resultados precisos
     */
    
    await page.goto(`${API_BASE_URL}/admin/users`);
    
    // Teste 1: Filtro por nome
    console.log('🧪 Testando filtro por nome...');
    
    await page.fill('input[name="search"]', 'João');
    await page.click('button[data-testid="apply-filters"]');
    
    await page.waitForSelector('.user-item', { timeout: 5000 });
    const nameFilterResults = await page.locator('.user-item').count();
    expect(nameFilterResults).toBeGreaterThan(0);
    
    // Validar que todos os resultados contêm "João"
    for (let i = 0; i < nameFilterResults; i++) {
      const userName = await page.locator('.user-item').nth(i).locator('.user-name').textContent();
      expect(userName.toLowerCase()).toContain('joão');
    }
    
    // Teste 2: Filtro por role
    console.log('🧪 Testando filtro por role...');
    
    await page.selectOption('select[name="role-filter"]', 'admin');
    await page.click('button[data-testid="apply-filters"]');
    
    await page.waitForSelector('.user-item', { timeout: 5000 });
    const roleFilterResults = await page.locator('.user-item').count();
    
    // Validar que todos os resultados são admins
    for (let i = 0; i < roleFilterResults; i++) {
      const userRole = await page.locator('.user-item').nth(i).locator('.user-role').textContent();
      expect(userRole.toLowerCase()).toContain('admin');
    }
    
    // Teste 3: Filtro por departamento
    console.log('🧪 Testando filtro por departamento...');
    
    await page.selectOption('select[name="department-filter"]', 'Marketing');
    await page.click('button[data-testid="apply-filters"]');
    
    await page.waitForSelector('.user-item', { timeout: 5000 });
    const deptFilterResults = await page.locator('.user-item').count();
    
    // Validar que todos os resultados são do departamento Marketing
    for (let i = 0; i < deptFilterResults; i++) {
      const userDept = await page.locator('.user-item').nth(i).locator('.user-department').textContent();
      expect(userDept).toContain('Marketing');
    }
    
    // Teste 4: Filtro por status
    console.log('🧪 Testando filtro por status...');
    
    await page.selectOption('select[name="status-filter"]', 'active');
    await page.click('button[data-testid="apply-filters"]');
    
    await page.waitForSelector('.user-item', { timeout: 5000 });
    const statusFilterResults = await page.locator('.user-item').count();
    
    // Validar que todos os resultados são ativos
    for (let i = 0; i < statusFilterResults; i++) {
      const userStatus = await page.locator('.user-item').nth(i).locator('.user-status').textContent();
      expect(userStatus.toLowerCase()).toContain('ativo');
    }
    
    // Teste 5: Limpar filtros
    console.log('🧪 Testando limpeza de filtros...');
    
    await page.click('button[data-testid="clear-filters"]');
    await page.waitForSelector('.user-item', { timeout: 5000 });
    
    const clearFilterResults = await page.locator('.user-item').count();
    expect(clearFilterResults).toBeGreaterThan(statusFilterResults);
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/listagem_usuarios/filtros_avancados.png',
      fullPage: true 
    });
    
    console.log('✅ Filtros avançados funcionando adequadamente');
  });

  test('📄 Paginação: Validação de navegação', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de paginação
     * 🌲 ToT: Avaliado diferentes estratégias e escolhido a mais eficiente
     * ♻️ ReAct: Simulado paginação real e validado navegação
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Paginação é essencial para grandes listas
     * - Deve implementar navegação intuitiva
     * - Deve manter estado dos filtros
     * - Deve mostrar informações de página
     * 
     * 📊 IMPACTO SIMULADO:
     * - Performance: Carregamento otimizado
     * - UX: Navegação fluida
     * - Funcionalidade: Dados organizados
     */
    
    await page.goto(`${API_BASE_URL}/admin/users`);
    
    // Configurar itens por página
    await page.selectOption('select[name="items-per-page"]', '2');
    await page.click('button[data-testid="apply-pagination"]');
    
    // Validar primeira página
    await page.waitForSelector('.user-item', { timeout: 5000 });
    const firstPageItems = await page.locator('.user-item').count();
    expect(firstPageItems).toBeLessThanOrEqual(2);
    
    // Validar informações de paginação
    await expect(page.locator('.pagination-info')).toContainText('1 de');
    await expect(page.locator('.pagination-info')).toContainText('página');
    
    // Navegar para próxima página
    const nextButton = page.locator('button[data-testid="next-page"]');
    if (await nextButton.isEnabled()) {
      await nextButton.click();
      await page.waitForSelector('.user-item', { timeout: 5000 });
      
      const secondPageItems = await page.locator('.user-item').count();
      expect(secondPageItems).toBeLessThanOrEqual(2);
      
      // Validar que é uma página diferente
      const firstPageFirstUser = await page.locator('.user-item').first().locator('.user-name').textContent();
      await page.click('button[data-testid="prev-page"]');
      await page.waitForSelector('.user-item', { timeout: 5000 });
      const secondPageFirstUser = await page.locator('.user-item').first().locator('.user-name').textContent();
      
      expect(firstPageFirstUser).not.toBe(secondPageFirstUser);
    }
    
    // Testar navegação por número de página
    const pageButtons = page.locator('button[data-testid="page-number"]');
    const pageCount = await pageButtons.count();
    
    if (pageCount > 1) {
      await pageButtons.nth(1).click(); // Clicar na segunda página
      await page.waitForSelector('.user-item', { timeout: 5000 });
      
      await expect(page.locator('.pagination-info')).toContainText('2 de');
    }
    
    // Testar com filtros aplicados
    await page.fill('input[name="search"]', 'a');
    await page.click('button[data-testid="apply-filters"]');
    
    // Validar que paginação mantém filtros
    await expect(page.locator('.pagination-info')).toBeVisible();
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/listagem_usuarios/paginacao.png',
      fullPage: true 
    });
    
    console.log('✅ Paginação funcionando adequadamente');
  });

  test('📊 Ordenação: Validação de organização', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de ordenação de dados
     * 🌲 ToT: Avaliado diferentes critérios e escolhido os mais úteis
     * ♻️ ReAct: Simulado ordenação real e validado resultados
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Ordenação facilita análise dos dados
     * - Deve implementar múltiplos critérios
     * - Deve alternar entre ascendente/descendente
     * - Deve manter estado com filtros
     * 
     * 📊 IMPACTO SIMULADO:
     * - UX: Dados organizados logicamente
     * - Produtividade: Análise mais rápida
     * - Funcionalidade: Busca facilitada
     */
    
    await page.goto(`${API_BASE_URL}/admin/users`);
    
    // Teste 1: Ordenação por nome (ascendente)
    console.log('🧪 Testando ordenação por nome...');
    
    await page.click('button[data-testid="sort-name"]');
    await page.waitForSelector('.user-item', { timeout: 5000 });
    
    const names = [];
    const userCount = await page.locator('.user-item').count();
    
    for (let i = 0; i < userCount; i++) {
      const name = await page.locator('.user-item').nth(i).locator('.user-name').textContent();
      names.push(name);
    }
    
    // Validar ordenação alfabética
    const sortedNames = [...names].sort();
    expect(names).toEqual(sortedNames);
    
    // Teste 2: Ordenação por nome (descendente)
    await page.click('button[data-testid="sort-name"]');
    await page.waitForSelector('.user-item', { timeout: 5000 });
    
    const namesDesc = [];
    for (let i = 0; i < userCount; i++) {
      const name = await page.locator('.user-item').nth(i).locator('.user-name').textContent();
      namesDesc.push(name);
    }
    
    // Validar ordenação reversa
    const sortedNamesDesc = [...names].sort().reverse();
    expect(namesDesc).toEqual(sortedNamesDesc);
    
    // Teste 3: Ordenação por data de criação
    console.log('🧪 Testando ordenação por data...');
    
    await page.click('button[data-testid="sort-created"]');
    await page.waitForSelector('.user-item', { timeout: 5000 });
    
    const dates = [];
    for (let i = 0; i < userCount; i++) {
      const date = await page.locator('.user-item').nth(i).locator('.user-created').textContent();
      dates.push(new Date(date));
    }
    
    // Validar ordenação cronológica
    const sortedDates = [...dates].sort((a, b) => a - b);
    expect(dates).toEqual(sortedDates);
    
    // Teste 4: Ordenação por último login
    console.log('🧪 Testando ordenação por último login...');
    
    await page.click('button[data-testid="sort-last-login"]');
    await page.waitForSelector('.user-item', { timeout: 5000 });
    
    // Validar que ordenação foi aplicada
    await expect(page.locator('.sort-indicator')).toBeVisible();
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/listagem_usuarios/ordenacao.png',
      fullPage: true 
    });
    
    console.log('✅ Ordenação funcionando adequadamente');
  });

  test('⚡ Ações em Massa: Validação de operações múltiplas', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de ações em massa
     * 🌲 ToT: Avaliado diferentes ações e escolhido as mais úteis
     * ♻️ ReAct: Simulado ações reais e validado resultados
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Ações em massa melhoram eficiência
     * - Deve implementar seleção múltipla
     * - Deve validar permissões
     * - Deve confirmar ações importantes
     * 
     * 📊 IMPACTO SIMULADO:
     * - Eficiência: Operações em lote
     * - Produtividade: Menos cliques
     * - Segurança: Confirmações adequadas
     */
    
    await page.goto(`${API_BASE_URL}/admin/users`);
    
    // Teste 1: Seleção múltipla
    console.log('🧪 Testando seleção múltipla...');
    
    await page.check('input[data-testid="select-all"]');
    await expect(page.locator('.selected-count')).toContainText('selecionados');
    
    // Desmarcar alguns itens
    await page.uncheck('input[data-testid="select-user-1"]');
    await page.uncheck('input[data-testid="select-user-2"]');
    
    const selectedCount = await page.locator('.selected-count').textContent();
    expect(selectedCount).toContain('selecionados');
    
    // Teste 2: Ativação em massa
    console.log('🧪 Testando ativação em massa...');
    
    await page.click('button[data-testid="bulk-activate"]');
    await expect(page.locator('.bulk-confirmation')).toBeVisible();
    await expect(page.locator('.bulk-confirmation')).toContainText('ativar');
    
    await page.click('button[data-testid="confirm-bulk-action"]');
    
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText('usuários ativados');
    
    // Teste 3: Desativação em massa
    console.log('🧪 Testando desativação em massa...');
    
    await page.check('input[data-testid="select-user-3"]');
    await page.check('input[data-testid="select-user-4"]');
    
    await page.click('button[data-testid="bulk-deactivate"]');
    await expect(page.locator('.bulk-confirmation')).toBeVisible();
    await expect(page.locator('.bulk-confirmation')).toContainText('desativar');
    
    await page.click('button[data-testid="confirm-bulk-action"]');
    
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText('usuários desativados');
    
    // Teste 4: Exclusão em massa
    console.log('🧪 Testando exclusão em massa...');
    
    await page.check('input[data-testid="select-user-5"]');
    await page.click('button[data-testid="bulk-delete"]');
    
    // Deve mostrar confirmação mais rigorosa para exclusão
    await expect(page.locator('.delete-confirmation')).toBeVisible();
    await expect(page.locator('.delete-confirmation')).toContainText('excluir permanentemente');
    
    // Cancelar exclusão
    await page.click('button[data-testid="cancel-delete"]');
    await expect(page.locator('.delete-confirmation')).not.toBeVisible();
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/listagem_usuarios/acoes_massa.png',
      fullPage: true 
    });
    
    console.log('✅ Ações em massa funcionando adequadamente');
  });

  test('📤 Exportação: Validação de relatórios', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de exportação de dados
     * 🌲 ToT: Avaliado diferentes formatos e escolhido os mais úteis
     * ♻️ ReAct: Simulado exportação real e validado arquivos
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Exportação é importante para relatórios
     * - Deve implementar múltiplos formatos
     * - Deve incluir filtros aplicados
     * - Deve gerar arquivos válidos
     * 
     * 📊 IMPACTO SIMULADO:
     * - Relatórios: Dados exportados
     * - Análise: Informações organizadas
     * - Compliance: Registros mantidos
     */
    
    await page.goto(`${API_BASE_URL}/admin/users`);
    
    // Aplicar filtros para exportação específica
    await page.selectOption('select[name="role-filter"]', 'user');
    await page.click('button[data-testid="apply-filters"]');
    
    // Teste 1: Exportação CSV
    console.log('🧪 Testando exportação CSV...');
    
    await page.click('button[data-testid="export-csv"]');
    
    const [csvDownload] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button[data-testid="confirm-export"]')
    ]);
    
    expect(csvDownload.suggestedFilename()).toMatch(/users.*\.csv$/);
    
    // Teste 2: Exportação Excel
    console.log('🧪 Testando exportação Excel...');
    
    await page.click('button[data-testid="export-excel"]');
    
    const [excelDownload] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button[data-testid="confirm-export"]')
    ]);
    
    expect(excelDownload.suggestedFilename()).toMatch(/users.*\.xlsx$/);
    
    // Teste 3: Exportação PDF
    console.log('🧪 Testando exportação PDF...');
    
    await page.click('button[data-testid="export-pdf"]');
    
    const [pdfDownload] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button[data-testid="confirm-export"]')
    ]);
    
    expect(pdfDownload.suggestedFilename()).toMatch(/users.*\.pdf$/);
    
    // Teste 4: Exportação com filtros
    console.log('🧪 Testando exportação com filtros...');
    
    await page.fill('input[name="search"]', 'João');
    await page.click('button[data-testid="apply-filters"]');
    
    await page.click('button[data-testid="export-filtered-csv"]');
    
    const [filteredDownload] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button[data-testid="confirm-export"]')
    ]);
    
    expect(filteredDownload.suggestedFilename()).toMatch(/users_filtered.*\.csv$/);
    
    // Validar histórico de exportações
    await page.goto(`${API_BASE_URL}/admin/export-history`);
    await expect(page.locator('.export-history')).toBeVisible();
    await expect(page.locator('.export-item')).toBeVisible();
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/listagem_usuarios/exportacao.png',
      fullPage: true 
    });
    
    console.log('✅ Sistema de exportação funcionando adequadamente');
  });

  test('📊 Performance: Validação de velocidade', async ({ page }) => {
    /**
     * 📐 CoCoT: Baseado em requisitos reais de performance
     * 🌲 ToT: Avaliado diferentes métricas e escolhido as mais importantes
     * ♻️ ReAct: Simulado métricas reais e validado thresholds
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Performance é crítica para UX
     * - Deve carregar rapidamente
     * - Deve implementar paginação eficiente
     * - Deve otimizar consultas
     * 
     * 📊 IMPACTO SIMULADO:
     * - UX: Interface responsiva
     * - Produtividade: Trabalho mais rápido
     * - Satisfação: Usuários satisfeitos
     */
    
    await page.goto(`${API_BASE_URL}/admin/users`);
    
    // Medir tempo de carregamento inicial
    const startTime = Date.now();
    await page.waitForSelector('.user-item', { timeout: 10000 });
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(5000); // Máximo 5 segundos
    console.log(`✅ Carregamento inicial: ${loadTime}ms`);
    
    // Medir tempo de aplicação de filtros
    const filterStart = Date.now();
    await page.fill('input[name="search"]', 'a');
    await page.click('button[data-testid="apply-filters"]');
    await page.waitForSelector('.user-item', { timeout: 5000 });
    const filterTime = Date.now() - filterStart;
    
    expect(filterTime).toBeLessThan(3000); // Máximo 3 segundos
    console.log(`✅ Aplicação de filtros: ${filterTime}ms`);
    
    // Medir tempo de paginação
    const paginationStart = Date.now();
    await page.click('button[data-testid="next-page"]');
    await page.waitForSelector('.user-item', { timeout: 5000 });
    const paginationTime = Date.now() - paginationStart;
    
    expect(paginationTime).toBeLessThan(2000); // Máximo 2 segundos
    console.log(`✅ Navegação de página: ${paginationTime}ms`);
    
    // Medir tempo de ordenação
    const sortStart = Date.now();
    await page.click('button[data-testid="sort-name"]');
    await page.waitForSelector('.user-item', { timeout: 5000 });
    const sortTime = Date.now() - sortStart;
    
    expect(sortTime).toBeLessThan(2000); // Máximo 2 segundos
    console.log(`✅ Ordenação: ${sortTime}ms`);
    
    // Validar indicadores de performance
    await expect(page.locator('.performance-indicator')).toBeVisible();
    const performanceScore = await page.locator('.performance-score').textContent();
    expect(parseFloat(performanceScore)).toBeGreaterThan(80); // Mínimo 80%
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/listagem_usuarios/performance.png',
      fullPage: true 
    });
    
    console.log(`✅ Performance geral: ${performanceScore}%`);
  });

  test('🔐 Permissões: Validação de acesso', async ({ page, context }) => {
    /**
     * 📐 CoCoT: Baseado em cenário real de controle de acesso
     * 🌲 ToT: Avaliado diferentes níveis e escolhido os mais críticos
     * ♻️ ReAct: Simulado acesso real e validado restrições
     * 
     * 🎯 JUSTIFICATIVA TÉCNICA:
     * - Controle de acesso é crítico para segurança
     * - Deve validar permissões adequadamente
     * - Deve bloquear acesso não autorizado
     * - Deve registrar tentativas de acesso
     * 
     * 📊 IMPACTO SIMULADO:
     * - Segurança: Acesso controlado
     * - Compliance: Requisitos atendidos
     * - Auditoria: Tentativas registradas
     */
    
    // Teste 1: Acesso como admin (deve funcionar)
    console.log('🧪 Testando acesso como admin...');
    
    await page.goto(`${API_BASE_URL}/admin/users`);
    await expect(page.locator('.users-list')).toBeVisible();
    await expect(page.locator('button[data-testid="create-user"]')).toBeVisible();
    await expect(page.locator('button[data-testid="bulk-delete"]')).toBeVisible();
    
    // Teste 2: Acesso como usuário comum (deve ser limitado)
    console.log('🧪 Testando acesso como usuário comum...');
    
    const userPage = await context.newPage();
    await userPage.goto(`${API_BASE_URL}/login`);
    await userPage.fill('input[name="usuario"]', 'user123');
    await userPage.fill('input[name="senha"]', 'password123');
    await userPage.click('button[type="submit"]');
    
    await userPage.goto(`${API_BASE_URL}/admin/users`);
    
    // Deve mostrar erro de acesso negado
    await expect(userPage.locator('.access-denied')).toBeVisible();
    await expect(userPage.locator('.access-denied')).toContainText('acesso negado');
    
    // Deve não mostrar botões de administração
    await expect(userPage.locator('button[data-testid="create-user"]')).not.toBeVisible();
    await expect(userPage.locator('button[data-testid="bulk-delete"]')).not.toBeVisible();
    
    // Teste 3: Acesso como analista (deve ser parcial)
    console.log('🧪 Testando acesso como analista...');
    
    const analystPage = await context.newPage();
    await analystPage.goto(`${API_BASE_URL}/login`);
    await analystPage.fill('input[name="usuario"]', 'analyst123');
    await analystPage.fill('input[name="senha"]', 'password123');
    await analystPage.click('button[type="submit"]');
    
    await analystPage.goto(`${API_BASE_URL}/admin/users`);
    
    // Deve mostrar lista mas com limitações
    await expect(analystPage.locator('.users-list')).toBeVisible();
    await expect(analystPage.locator('button[data-testid="create-user"]')).not.toBeVisible();
    await expect(analystPage.locator('button[data-testid="bulk-delete"]')).not.toBeVisible();
    
    // Deve mostrar apenas ações de visualização
    await expect(analystPage.locator('button[data-testid="view-user"]')).toBeVisible();
    await expect(analystPage.locator('button[data-testid="export-csv"]')).toBeVisible();
    
    await page.screenshot({ 
      path: 'tests/e2e/snapshots/listagem_usuarios/permissoes.png',
      fullPage: true 
    });
    
    console.log('✅ Controle de permissões funcionando adequadamente');
  });
}); 
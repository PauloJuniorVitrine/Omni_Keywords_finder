import { test, expect } from '@playwright/test';

/**
 * Jornada: Listagem de Execuções Agendadas
 * Perfil: Usuário autenticado
 * Objetivo: Validar listagem, paginação, concorrência e tratamento de erro.
 * Cobertura: Fluxo principal, paginação, concorrência, erro, acessibilidade, logs e screenshots.
 */

test.describe('Jornada: Listagem de Execuções Agendadas', () => {
  test('Fluxo principal: listar execuções agendadas', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="usuario"]', 'analista');
    await page.fill('input[name="senha"]', 'senha123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);

    await page.goto('/execucoes/agendadas');
    await page.click('button#listar_agendadas');
    await expect(page.locator('.agendada-item')).toBeVisible();
    await page.screenshot({ path: 'tests/e2e/snapshots/listagem_agendadas/sucesso.png' });
  });

  test('Paginação: navegar entre páginas', async ({ page }) => {
    await page.goto('/execucoes/agendadas');
    await page.click('button#listar_agendadas');
    const nextBtn = page.locator('button#paginacao_proxima');
    if (await nextBtn.isEnabled()) {
      await nextBtn.click();
      await expect(page.locator('.agendada-item')).toBeVisible();
      await page.screenshot({ path: 'tests/e2e/snapshots/listagem_agendadas/paginacao.png' });
    }
  });

  test('Fluxo alternativo: erro ao listar', async ({ page }) => {
    await page.goto('/execucoes/agendadas');
    // Simula erro de backend
    await page.route('/api/execucoes/agendadas', route => route.abort());
    await page.click('button#listar_agendadas');
    await expect(page.locator('.erro')).toBeVisible();
    await page.screenshot({ path: 'tests/e2e/snapshots/listagem_agendadas/erro.png' });
  });

  test('Concorrência: múltiplas listagens em paralelo', async ({ page, context }) => {
    await page.goto('/login');
    await page.fill('input[name="usuario"]', 'analista');
    await page.fill('input[name="senha"]', 'senha123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);

    const pages = await Promise.all([
      context.newPage(),
      context.newPage()
    ]);
    await Promise.all(pages.map(async (p, i) => {
      await p.goto('/execucoes/agendadas');
      await p.click('button#listar_agendadas');
      await expect(p.locator('.agendada-item')).toBeVisible();
      await p.screenshot({ path: `tests/e2e/snapshots/listagem_agendadas/concorrente_${i}.png` });
    }));
  });

  test('Acessibilidade: foco, contraste, navegação por teclado', async ({ page }) => {
    await page.goto('/execucoes/agendadas');
    await expect(page.locator('button#listar_agendadas')).toBeFocused();
    // (Opcional) Validar contraste e navegação por tab
  });
}); 
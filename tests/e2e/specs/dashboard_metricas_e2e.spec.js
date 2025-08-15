import { test, expect } from '@playwright/test';

test.describe('Jornada 6: Dashboard e Métricas', () => {
  test('Fluxo principal e variações', async ({ page }) => {
    // 1. Login
    await page.goto('/login');
    await page.fill('input[name="usuario"]', 'admin');
    await page.fill('input[name="senha"]', 'senha123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);

    // 2. Acesso ao dashboard
    await page.click('a[href="/dashboard"]');
    await expect(page).toHaveURL(/dashboard/);

    // 3. Validação de exibição de métricas agregadas
    await expect(page.locator('.dashboard-metricas')).toBeVisible();
    await expect(page.locator('.dashboard-metricas .card')).toHaveCountGreaterThan(0);

    // 4. Simulação de erro de carregamento (mock/fake)
    // (Assumindo flag de teste ou manipulação de rede)
    await page.route('/api/dashboard/metrics', route => route.abort());
    await page.reload();
    await expect(page.locator('.erro')).toBeVisible();

    // 5. Acessibilidade: foco, contraste, navegação por teclado
    await expect(page.locator('button#refresh')).toBeFocused();

    // 6. Screenshot por etapa
    await page.screenshot({ path: 'tests/e2e/snapshots/dashboard/sucesso.png' });
  });
}); 
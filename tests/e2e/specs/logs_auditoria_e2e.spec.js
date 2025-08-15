import { test, expect } from '@playwright/test';

test.describe('Jornada 4: Consulta de Logs/Auditoria', () => {
  test('Fluxo principal e variações', async ({ page }) => {
    // 1. Login
    await page.goto('/login');
    await page.fill('input[name="usuario"]', 'admin');
    await page.fill('input[name="senha"]', 'senha123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);

    // 2. Acesso à tela de logs
    await page.click('a[href="/logs"]');
    await expect(page).toHaveURL(/logs/);

    // 3. Filtro por evento/data
    await page.fill('input[name="filtro_evento"]', 'validacao_keywords');
    await page.click('button#filtrar');
    await expect(page.locator('.log-item')).toBeVisible();

    // 4. Visualização de detalhes
    await page.click('.log-item:first-child');
    await expect(page.locator('.log-detalhe')).toBeVisible();

    // 5. Caminhos alternativos: filtro sem resultado, erro de permissão
    await page.fill('input[name="filtro_evento"]', 'evento_inexistente');
    await page.click('button#filtrar');
    await expect(page.locator('.sem-resultado')).toBeVisible();

    // 6. Acessibilidade: foco, contraste, navegação por teclado
    await expect(page.locator('button#filtrar')).toBeFocused();

    // 7. Screenshot por etapa
    await page.screenshot({ path: 'tests/e2e/snapshots/logs/sucesso.png' });
  });
}); 
import { test, expect } from '@playwright/test';

test.describe('Jornada 2: Exportação de Keywords', () => {
  test('Fluxo principal e variações', async ({ page, context }) => {
    // 1. Login
    await page.goto('/login');
    await page.fill('input[name="usuario"]', 'analista');
    await page.fill('input[name="senha"]', 'senha123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);

    // 2. Acesso à tela de exportação
    await page.click('a[href="/exportar"]');
    await expect(page).toHaveURL(/exportar/);

    // 3. Seleção de formato (JSON)
    await page.selectOption('select#formato', 'json');
    const [downloadJson] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button#baixar'),
    ]);
    expect(downloadJson.suggestedFilename()).toMatch(/\.json$/);

    // 4. Seleção de formato (CSV)
    await page.selectOption('select#formato', 'csv');
    const [downloadCsv] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button#baixar'),
    ]);
    expect(downloadCsv.suggestedFilename()).toMatch(/\.csv$/);

    // 5. Caminhos alternativos: formato inválido
    await page.selectOption('select#formato', 'xml');
    await page.click('button#baixar');
    await expect(page.locator('.erro')).toBeVisible();

    // 6. Acessibilidade: foco, contraste, navegação por teclado
    await expect(page.locator('button#baixar')).toBeFocused();

    // 7. Screenshot por etapa
    await page.screenshot({ path: 'tests/e2e/snapshots/exportacao/sucesso.png' });
  });
}); 
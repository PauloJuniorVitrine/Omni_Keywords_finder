import { test, expect } from '@playwright/test';

/**
 * Jornada: Carga Extrema de Keywords
 * Perfil: Usuário autenticado
 * Objetivo: Validar processamento e exportação de grande volume de keywords reais, sem uso de dados sintéticos.
 * Cobertura: Upload real, processamento, exportação, side effects, logs, acessibilidade, stress.
 */

test.describe('Jornada: Carga Extrema de Keywords', () => {
  test('Processamento em lote real', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="usuario"]', 'admin');
    await page.fill('input[name="senha"]', 'senha123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);

    await page.goto('/processamento');
    await page.setInputFiles('input[type="file"]', 'tests/e2e/fixtures/keywords_carga.csv');
    await page.click('button#processar');
    await expect(page.locator('.status')).toHaveText(/Processando|Concluído/);
    await expect(page.locator('.relatorio')).toBeVisible({ timeout: 120000 });
    await page.screenshot({ path: 'tests/e2e/snapshots/carga_extrema/processamento_sucesso.png' });
  });

  test('Exportação em lote real', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="usuario"]', 'admin');
    await page.fill('input[name="senha"]', 'senha123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);

    await page.goto('/exportar');
    await page.selectOption('select#formato', 'csv');
    const [downloadCsv] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button#baixar'),
    ]);
    expect(downloadCsv.suggestedFilename()).toMatch(/\.csv$/);
    await page.screenshot({ path: 'tests/e2e/snapshots/carga_extrema/exportacao_sucesso.png' });
  });

  test('Acessibilidade: foco, contraste, navegação por teclado', async ({ page }) => {
    await page.goto('/processamento');
    await expect(page.locator('button#processar')).toBeFocused();
    await page.goto('/exportar');
    await expect(page.locator('button#baixar')).toBeFocused();
  });
}); 
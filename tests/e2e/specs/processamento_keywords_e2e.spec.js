import { test, expect } from '@playwright/test';

test.describe('Jornada 1: Processamento Completo de Keywords', () => {
  test('Fluxo principal e variações', async ({ page }) => {
    // 1. Login
    await page.goto('/login');
    await page.fill('input[name="usuario"]', 'admin');
    await page.fill('input[name="senha"]', 'senha123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);

    // 2. Acesso à página de processamento
    await page.click('a[href="/processamento"]');
    await expect(page).toHaveURL(/processamento/);

    // 3. Upload/entrada de lista de keywords
    await page.setInputFiles('input[type="file"]', 'tests/e2e/fixtures/keywords.csv');
    await page.click('button#processar');
    await expect(page.locator('.status')).toHaveText(/Processando|Concluído/);

    // 4. Visualização do relatório/resultados
    await expect(page.locator('.relatorio')).toBeVisible();

    // 5. Download/exportação dos resultados
    await page.click('button#exportar');
    // Validar download, conteúdo, side effects

    // 6. Caminhos alternativos: keywords inválidas, erro, timeout
    await page.setInputFiles('input[type="file"]', 'tests/e2e/fixtures/keywords_invalidas.csv');
    await page.click('button#processar');
    await expect(page.locator('.erro')).toBeVisible();

    // 7. Acessibilidade: foco, contraste, navegação por teclado
    await expect(page.locator('button#processar')).toBeFocused();

    // 8. Screenshot por etapa
    await page.screenshot({ path: 'tests/e2e/snapshots/processamento/sucesso.png' });
  });
}); 
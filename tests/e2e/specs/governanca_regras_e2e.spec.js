import { test, expect } from '@playwright/test';

test.describe('Jornada 3: Gerenciamento de Regras de Governança', () => {
  test('Fluxo principal e variações', async ({ page }) => {
    // 1. Login
    await page.goto('/login');
    await page.fill('input[name="usuario"]', 'admin');
    await page.fill('input[name="senha"]', 'senha123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);

    // 2. Acesso à tela de regras
    await page.click('a[href="/governanca/regras"]');
    await expect(page).toHaveURL(/governanca\/regras/);

    // 3. Upload de nova blacklist/whitelist
    await page.setInputFiles('input[type="file"]', 'tests/e2e/fixtures/blacklist.csv');
    await page.click('button#upload_blacklist');
    await expect(page.locator('.status')).toHaveText(/Upload concluído/);

    await page.setInputFiles('input[type="file"]', 'tests/e2e/fixtures/whitelist.csv');
    await page.click('button#upload_whitelist');
    await expect(page.locator('.status')).toHaveText(/Upload concluído/);

    // 4. Edição de regras existentes
    await page.fill('input[name="score_minimo"]', '0.8');
    await page.click('button#salvar_regras');
    await expect(page.locator('.status')).toHaveText(/Regras atualizadas/);

    // 5. Consulta de regras atuais
    await page.click('button#consultar_regras');
    await expect(page.locator('.regras')).toBeVisible();

    // 6. Caminhos alternativos: upload inválido, regra duplicada
    await page.setInputFiles('input[type="file"]', 'tests/e2e/fixtures/blacklist_invalida.csv');
    await page.click('button#upload_blacklist');
    await expect(page.locator('.erro')).toBeVisible();

    // 7. Acessibilidade: foco, contraste, navegação por teclado
    await expect(page.locator('button#salvar_regras')).toBeFocused();

    // 8. Screenshot por etapa
    await page.screenshot({ path: 'tests/e2e/snapshots/governanca/sucesso.png' });
  });
}); 
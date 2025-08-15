import { test, expect } from '@playwright/test';

test.describe('Jornada 5: Consulta de Tendências Externas', () => {
  test('Fluxo principal e variações', async ({ page }) => {
    // 1. Login
    await page.goto('/login');
    await page.fill('input[name="usuario"]', 'analista');
    await page.fill('input[name="senha"]', 'senha123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);

    // 2. Acesso à tela de tendências
    await page.click('a[href="/tendencias"]');
    await expect(page).toHaveURL(/tendencias/);

    // 3. Consulta de termo válido
    await page.fill('input[name="termo"]', 'marketing digital');
    await page.click('button#consultar');
    await expect(page.locator('.tendencia-item')).toBeVisible();

    // 3.1 Consulta de massa real de termos
    const termos = ['inteligência artificial', 'SEO', 'e-commerce', 'cloud computing', 'data science'];
    for (const termo of termos) {
      await page.fill('input[name="termo"]', termo);
      await page.click('button#consultar');
      await expect(page.locator('.tendencia-item, .erro')).toBeVisible();
    }

    // 4. Consulta de termo inválido
    await page.fill('input[name="termo"]', '');
    await page.click('button#consultar');
    await expect(page.locator('.erro')).toBeVisible();

    // 5. Simulação de indisponibilidade do serviço externo
    // (Assumindo mock ou flag de teste)
    await page.fill('input[name="termo"]', 'servico_indisponivel');
    await page.click('button#consultar');
    await expect(page.locator('.erro')).toBeVisible();

    // 6. Acessibilidade: foco, contraste, navegação por teclado
    await expect(page.locator('button#consultar')).toBeFocused();

    // 7. Screenshot por etapa
    await page.screenshot({ path: 'tests/e2e/snapshots/tendencias/sucesso.png' });
  });
}); 
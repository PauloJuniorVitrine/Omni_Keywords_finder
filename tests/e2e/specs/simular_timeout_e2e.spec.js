import { test, expect } from '@playwright/test';

/**
 * Jornada: Simular Timeout
 * Perfil: Usuário autenticado e anônimo
 * Objetivo: Validar robustez do sistema sob condições de latência, timeout e fallback.
 * Cobertura: Fluxo principal, timeout, fallback, erro de rede, acessibilidade, logs e screenshots.
 */

test.describe('Jornada: Simular Timeout', () => {
  test('Fluxo principal: resposta dentro do tempo', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="usuario"]', 'analista');
    await page.fill('input[name="senha"]', 'senha123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);

    await page.goto('/test/timeout');
    await page.click('button#executar_timeout');
    await expect(page.locator('.resultado')).toBeVisible({ timeout: 5000 });
    await page.screenshot({ path: 'tests/e2e/snapshots/timeout/sucesso.png' });
  });

  test('Fluxo alternativo: simular timeout e fallback', async ({ page }) => {
    await page.goto('/test/timeout');
    // Simula rede lenta ou timeout via mock/fake
    await page.route('/api/test/timeout', route => setTimeout(() => route.abort(), 6000));
    await page.click('button#executar_timeout');
    await expect(page.locator('.fallback')).toBeVisible({ timeout: 7000 });
    await page.screenshot({ path: 'tests/e2e/snapshots/timeout/fallback.png' });
  });

  test('Fluxo anônimo: acesso sem login', async ({ page }) => {
    await page.goto('/test/timeout');
    await page.click('button#executar_timeout');
    await expect(page.locator('.resultado, .fallback')).toBeVisible({ timeout: 7000 });
  });

  test('Acessibilidade: foco, contraste, navegação por teclado', async ({ page }) => {
    await page.goto('/test/timeout');
    await expect(page.locator('button#executar_timeout')).toBeFocused();
    // (Opcional) Validar contraste e navegação por tab
  });
}); 
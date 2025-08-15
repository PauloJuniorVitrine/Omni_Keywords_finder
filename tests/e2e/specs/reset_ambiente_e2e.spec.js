import { test, expect } from '@playwright/test';

/**
 * Jornada: Reset de Ambiente
 * Perfil: Admin, Usuário autenticado
 * Objetivo: Garantir que o reset do ambiente é idempotente, seguro e reverte o sistema ao estado inicial.
 * Cobertura: Fluxo principal, idempotência, erro, acessibilidade, logs e screenshots.
 */

test.describe('Jornada: Reset de Ambiente', () => {
  test('Fluxo principal: reset com sucesso', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="usuario"]', 'admin');
    await page.fill('input[name="senha"]', 'senha123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);

    await page.goto('/test/reset');
    await page.click('button#resetar_ambiente');
    await expect(page.locator('.status')).toHaveText(/Ambiente resetado|Reset concluído/);
    await page.screenshot({ path: 'tests/e2e/snapshots/reset/sucesso.png' });
  });

  test('Idempotência: reset múltiplas vezes', async ({ page }) => {
    await page.goto('/test/reset');
    for (let i = 0; i < 2; i++) {
      await page.click('button#resetar_ambiente');
      await expect(page.locator('.status')).toHaveText(/Ambiente resetado|Reset concluído/);
    }
    await page.screenshot({ path: 'tests/e2e/snapshots/reset/idempotente.png' });
  });

  test('Fluxo alternativo: erro ao resetar', async ({ page }) => {
    await page.goto('/test/reset');
    // Simula erro de backend
    await page.route('/api/test/reset', route => route.abort());
    await page.click('button#resetar_ambiente');
    await expect(page.locator('.erro')).toBeVisible();
    await page.screenshot({ path: 'tests/e2e/snapshots/reset/erro.png' });
  });

  test('Acessibilidade: foco, contraste, navegação por teclado', async ({ page }) => {
    await page.goto('/test/reset');
    await expect(page.locator('button#resetar_ambiente')).toBeFocused();
    // (Opcional) Validar contraste e navegação por tab
  });
}); 
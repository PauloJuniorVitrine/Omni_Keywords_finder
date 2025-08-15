import { test, expect } from '@playwright/test';

test.describe('Jornada: Rotas Públicas/Anônimas', () => {
  test('Acesso à página inicial sem autenticação', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
    // Validar elementos públicos
    await expect(page.locator('header')).toBeVisible();
    await page.screenshot({ path: 'tests/e2e/snapshots/publico/home.png' });
  });

  test('Acesso negado a rota restrita sem login', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('.login-form, .erro, .auth-required')).toBeVisible();
    await page.screenshot({ path: 'tests/e2e/snapshots/publico/acesso_negado.png' });
  });

  test('Acessibilidade: navegação pública', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('a, button')).toBeVisible();
  });
}); 
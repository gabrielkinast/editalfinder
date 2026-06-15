// Camada 1 — Public smoke (QA 1.1): sem login, sem dados reais obrigatórios.
import { test, expect } from '@playwright/test';
import {
  enableQaDebug,
  collectConsoleErrors,
  expectNoFatalError,
  appPath,
  isLoginPage,
} from './_helpers.js';

test.describe('public smoke [Camada 1]', () => {
  test.beforeEach(async ({ page }) => {
    await enableQaDebug(page);
  });

  test('app-load: raiz redireciona para login quando não autenticado [P0]', async ({ page }) => {
    await page.goto(appPath('/'));
    await expect(page.getByTestId('login-page')).toBeVisible({ timeout: 15_000 });
    await expect(page.getByRole('tab', { name: 'Entrar' })).toBeVisible();
    await expectNoFatalError(page);
  });

  test('login-page: formulário renderiza sem erro fatal [P0]', async ({ page }) => {
    await page.goto(appPath('/login'));
    await expect(page.getByTestId('login-page')).toBeVisible();
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.getByTestId('login-submit')).toBeVisible();
    await expectNoFatalError(page);
  });

  test('protected-route: /editais redireciona para login sem auth [P0]', async ({ page }) => {
    await page.goto(appPath('/editais'));
    const onLogin = await isLoginPage(page);
    expect(onLogin, 'rota protegida deve mostrar login').toBe(true);
    await expectNoFatalError(page);
  });

  test('protected-route: /dashboard redireciona para login sem auth [P0]', async ({ page }) => {
    await page.goto(appPath('/dashboard'));
    const onLogin = await isLoginPage(page);
    expect(onLogin).toBe(true);
    await expectNoFatalError(page);
  });

  test('router-basename: assets da SPA carregam (sem tela em branco) [P0]', async ({ page }) => {
    const errors = collectConsoleErrors(page);
    await page.goto(appPath('/login'));
    await expect(page.getByTestId('login-page')).toBeVisible();
    const bodyLen = (await page.locator('body').innerText()).trim().length;
    expect(bodyLen, 'body não deve estar vazio').toBeGreaterThan(20);
    // Erros de rede 404 em chunk são falha de basename/build
    const chunk404 = errors.filter((e) => /Failed to load|404.*\.js/i.test(e));
    expect(chunk404, `erros de asset: ${chunk404.join('\n')}`).toEqual([]);
  });
});

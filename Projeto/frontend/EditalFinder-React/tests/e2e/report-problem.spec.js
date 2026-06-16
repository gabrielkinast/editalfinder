// Camada 2 — Reporte de problema (requer auth). QA 1.1 + QA 1.2.
import { test, expect } from '@playwright/test';
import {
  enableQaDebug,
  appPath,
  skipIfNoAuth,
  loginIfConfigured,
  expectNoFatalError,
  closeReportProblemModal,
} from './_helpers.js';

test.describe('report problem [Camada 2]', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    skipIfNoAuth(testInfo);
    await enableQaDebug(page);
    await page.goto(appPath('/dashboard'));
    if (await page.getByTestId('login-page').isVisible({ timeout: 3_000 }).catch(() => false)) {
      await loginIfConfigured(page);
    }
  });

  test('modal geral mostra ambiente + orientação de reporte [P1]', async ({ page }) => {
    await page.goto(appPath('/dashboard'));
    await expect(page.getByTestId('dashboard-page')).toBeVisible({ timeout: 20_000 });

    const btn = page.getByTestId('report-problem-button').first();
    await expect(btn).toBeVisible({ timeout: 15_000 });
    await btn.click();

    await expect(page.getByTestId('report-problem-modal')).toBeVisible();
    await expect(page.getByTestId('app-feedback-runtime-badge')).toBeVisible();

    const guidance = await page.getByTestId('app-feedback-guidance').innerText();
    expect(guidance.toLowerCase()).toMatch(/print|detalhes/);

    const badge = await page.getByTestId('app-feedback-runtime-badge').innerText();
    expect(badge.length).toBeGreaterThan(5);

    await closeReportProblemModal(page);
    await expectNoFatalError(page);
  });

  test('botão de envio Gmail ou fallback existe sem enviar e-mail [P2]', async ({ page }) => {
    await page.goto(appPath('/dashboard'));
    await expect(page.getByTestId('dashboard-page')).toBeVisible({ timeout: 20_000 });

    await page.getByTestId('report-problem-button').first().click();
    await expect(page.getByTestId('report-problem-modal')).toBeVisible();

    const fallback = page.getByTestId('app-feedback-fallback');
    const submit = page.getByTestId('app-feedback-submit');

    const hasFallback = await fallback.isVisible({ timeout: 2_000 }).catch(() => false);
    const hasSubmit = await submit.isVisible({ timeout: 2_000 }).catch(() => false);

    expect(hasFallback || hasSubmit).toBe(true);

    if (hasSubmit) {
      await expect(submit).toBeEnabled();
      expect(await submit.innerText()).toMatch(/Gmail|reporte/i);
    }

    await closeReportProblemModal(page);
    await expectNoFatalError(page);
  });
});

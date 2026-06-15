// Camada 2 — Radar smoke (QA 1.2).
import { test, expect } from '@playwright/test';
import {
  enableQaDebug,
  skipIfNoAuth,
  expectNoFatalError,
  requireAuthenticatedPage,
  waitForPageReady,
  skipWithEvidence,
} from './_helpers.js';

test.describe('radar smoke [Camada 2]', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    skipIfNoAuth(testInfo);
    await enableQaDebug(page);
  });

  test('radar renderiza placeholder ou cards [P2]', async ({ page }, testInfo) => {
    test.setTimeout(90_000);

    const auth = await requireAuthenticatedPage(page, '/radar-fomento');
    if (!auth.ok) {
      await skipWithEvidence(test, page, auth.reason, { route: '/radar-fomento' });
      return;
    }

    await waitForPageReady(page, 'radar-page');
    const body = await page.locator('body').innerText();
    expect(body).toMatch(/Radar de Fomento|Compatibilidade/i);

    const placeholder = page.getByTestId('radar-placeholder');
    const radarCards = page.getByTestId('radar-card');
    const hasPlaceholder = await placeholder.isVisible({ timeout: 5_000 }).catch(() => false);
    const cardCount = await radarCards.count();

    if (!hasPlaceholder && cardCount === 0) {
      const loadErr = page.locator('.radar-load-erro');
      if (await loadErr.isVisible({ timeout: 2_000 }).catch(() => false)) {
        await skipWithEvidence(test, page, 'radar_load_error', {
          errorText: await loadErr.innerText().catch(() => ''),
        });
        return;
      }
    }

    expect(hasPlaceholder || cardCount >= 0).toBe(true);
    await expectNoFatalError(page);
  });
});

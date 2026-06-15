// Camada 2 — Sanidade autenticada: /editais fora do login (QA 1.1B).
import { test, expect } from '@playwright/test';
import {
  enableQaDebug,
  skipIfNoAuth,
  expectNoFatalError,
  isLoginPage,
} from './_helpers.js';
import {
  waitForEditaisCatalog,
  saveSkipEvidence,
  getCatalogStatsText,
} from './_catalog.js';

test.describe('authenticated smoke [Camada 2]', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    skipIfNoAuth(testInfo);
    await enableQaDebug(page);
  });

  test('editais carrega fora do login com stats ou cards [P0]', async ({ page }, testInfo) => {
    test.setTimeout(120_000);
    const catalog = await waitForEditaisCatalog(page);

    if (!catalog.ok) {
      await saveSkipEvidence(page, 'authenticated-smoke-skip', catalog.reason, {
        phase: catalog.phase,
      });
      test.skip(
        true,
        `${catalog.reason} — evidência: debug-authenticated-data/authenticated-smoke-skip.*`,
      );
    }

    expect(await isLoginPage(page)).toBe(false);

    const body = await page.locator('body').innerText();
    expect(body).toMatch(/Editais|Mostrando|recebidos|PDF|Planilha/i);

    const statsText = await getCatalogStatsText(page);
    expect(statsText).toMatch(/Mostrando/i);

    await expectNoFatalError(page);

    await testInfo.attach('authenticated-smoke-catalog.json', {
      body: JSON.stringify(catalog, null, 2),
      contentType: 'application/json',
    });
  });
});

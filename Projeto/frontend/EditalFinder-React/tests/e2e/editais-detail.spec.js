// Camada 2+3 — Detalhe de editais (QA 1.1B).
import { test, expect } from '@playwright/test';
import {
  enableQaDebug,
  expectNoFatalError,
  skipIfNoAuth,
} from './_helpers.js';
import { requireCatalogReady, getFirstNEditalCards } from './_catalog.js';

const N = Number(process.env.QA_DETAIL_SAMPLE || 10);

test.describe('editais detail [Camada 2/3]', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    skipIfNoAuth(testInfo);
    await enableQaDebug(page);
  });

  test(`abre os primeiros ${N} editais e registra detalhes quebrados [P1]`, async ({ page }, testInfo) => {
    test.setTimeout(180_000);

    const catalog = await requireCatalogReady(page, testInfo, 'editais-detail', { minCards: 1 });
    if (!catalog) return;

    const cardLocators = await getFirstNEditalCards(page, N);
    const total = cardLocators.length;

    expect(total, 'deveria haver pelo menos 1 card visível').toBeGreaterThan(0);

    const broken = [];

    for (let i = 0; i < total; i += 1) {
      const card = cardLocators[i];
      const id = await card.getAttribute('data-edital-id');
      const source = await card.getAttribute('data-source');
      const fonte = await card.getAttribute('data-fonte');
      const title =
        (await card.locator('.edital-title').innerText().catch(() => '')) || `card#${i}`;

      if (!id) {
        broken.push({ index: i, id, source, fonte, title: title.slice(0, 80), note: 'missing_id' });
      }

      await card.getByTestId('edital-open-detail').click();
      await page.waitForTimeout(800);

      const body = await page.locator('body').innerText();
      if (body.includes('Não foi possível carregar os dados do edital')) {
        broken.push({ index: i, id, source, fonte, title: title.slice(0, 80) });
      }

      await page.keyboard.press('Escape').catch(() => {});
      if (page.url().includes('/edital/')) {
        await page.goBack().catch(() => {});
      }
      await page.waitForTimeout(250);
    }

    await testInfo.attach('broken-details.json', {
      body: JSON.stringify({ sampled: total, broken }, null, 2),
      contentType: 'application/json',
    });

    await expectNoFatalError(page).catch(() => {});
    expect(broken, `detalhes quebrados: ${JSON.stringify(broken)}`).toEqual([]);
  });
});

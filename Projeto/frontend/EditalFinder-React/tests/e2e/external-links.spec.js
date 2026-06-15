// Camada 2/3 — Links externos genéricos (QA 1.2).
import { test, expect } from '@playwright/test';
import { enableQaDebug, skipIfNoAuth, skipWithEvidence } from './_helpers.js';
import { requireCatalogReady } from './_catalog.js';
import { installGrantsE2eHooks } from './_grants.js';

const BAD_URL_PATTERNS = [
  /^javascript:/i,
  /^about:blank/i,
  /^$/i,
  /page-not-found/i,
  /page_not_found/i,
];

function isBadExternalUrl(url) {
  const s = String(url || '').trim();
  if (!s) return true;
  return BAD_URL_PATTERNS.some((re) => re.test(s));
}

test.describe('external links [Camada 2/3]', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    skipIfNoAuth(testInfo);
    await installGrantsE2eHooks(page);
    await enableQaDebug(page);
  });

  test('botões externos de cards não usam URLs inválidas [P2]', async ({ page }, testInfo) => {
    test.setTimeout(90_000);

    const catalog = await requireCatalogReady(page, test, 'external-links', {
      minCards: 1,
      minReceived: 1,
    });
    if (!catalog) return;

    const meta = await page.evaluate(() => {
      const cards = [...document.querySelectorAll('[data-testid="edital-card"]')].slice(0, 8);
      return cards.map((el) => {
        const official = el.querySelector('[data-testid="edital-open-official"]');
        const btnView = el.querySelector('.btn-view');
        const btnInsc = el.querySelector('.btn-inscricao');
        const pick = official || btnView || btnInsc;
        return {
          idEdital: el.getAttribute('data-edital-id'),
          href: pick?.getAttribute('href') || '',
          title: pick?.getAttribute('title') || '',
          qaUrl: pick?.getAttribute('data-qa-resolved-url') || '',
        };
      });
    });

    const withButtons = meta.filter((m) => m.href || m.qaUrl);
    if (!withButtons.length) {
      await skipWithEvidence(test, page, 'no_external_buttons_on_cards', { sampled: meta.length });
      return;
    }

    const clicked = [];
    for (let i = 0; i < Math.min(3, withButtons.length); i += 1) {
      const card = page.locator(`[data-testid="edital-card"][data-edital-id="${withButtons[i].idEdital}"]`);
      const btn = card.getByTestId('edital-open-official').first();
      const target = (await btn.isVisible().catch(() => false))
        ? btn
        : card.locator('.btn-view, .btn-inscricao').first();
      if (!(await target.isVisible().catch(() => false))) continue;
      await target.click();
      await page.waitForTimeout(200);
    }

    const captured = await page.evaluate(() => window.__QA_EXTERNAL_URLS__ || []);
    const staticUrls = withButtons.flatMap((m) => [m.href, m.qaUrl].filter(Boolean));
    const allUrls = [...new Set([...staticUrls, ...captured])];

    const bad = allUrls.filter(isBadExternalUrl);
    await testInfo.attach('external-urls.json', {
      body: JSON.stringify({ allUrls, bad, sampledCards: withButtons.length }, null, 2),
      contentType: 'application/json',
    });

    expect(bad, `URLs inválidas: ${JSON.stringify(bad)}`).toEqual([]);
  });
});

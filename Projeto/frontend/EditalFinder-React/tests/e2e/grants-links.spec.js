// Camada 2+3 — Grants.gov links (QA 1.1C — targeting determinístico).
import { test, expect } from '@playwright/test';
import { enableQaDebug, skipIfNoAuth } from './_helpers.js';
import { requireCatalogReady } from './_catalog.js';
import {
  installGrantsE2eHooks,
  discoverGrantsCards,
  collectGrantsUrlsFromCards,
  clickGrantsOfficialButtons,
  saveGrantsSkipEvidence,
  saveGrantsFailureEvidence,
  GRANTS_SEARCH_DEADLINE_MS,
} from './_grants.js';

test.describe('grants links [Camada 2/3]', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    skipIfNoAuth(testInfo);
    await installGrantsE2eHooks(page);
    await enableQaDebug(page);
  });

  test('botões externos não apontam para page-not-found [P1]', async ({ page }, testInfo) => {
    test.setTimeout(120_000);

    const catalog = await requireCatalogReady(page, testInfo, 'grants-links', {
      minCards: 1,
      catalogTimeout: 90_000,
    });
    if (!catalog) return;

    const discovery = await discoverGrantsCards(page, {
      deadlineMs: GRANTS_SEARCH_DEADLINE_MS,
    });

    if (discovery.grantsEntries.length === 0) {
      await saveGrantsSkipEvidence(page, {
        reason: 'no_grants_cards_visible',
        ...discovery,
      });
      test.skip(
        true,
        `Nenhum card Grants.gov em ${discovery.elapsedMs}ms — evidência: debug-authenticated-data/grants-links-skip.*`,
      );
      return;
    }

    const staticUrls = await collectGrantsUrlsFromCards(discovery.grantsMeta);
    const clickedUrls = await clickGrantsOfficialButtons(page, discovery.grantsEntries, 3);

    const merged = new Map();
    for (const row of [...staticUrls, ...clickedUrls]) {
      const key = row.url;
      if (!key) continue;
      merged.set(key, row);
    }
    const report = [...merged.values()];

    await testInfo.attach('grants-external-urls.json', {
      body: JSON.stringify(
        {
          grantsCardsFound: discovery.grantsEntries.length,
          strategies: discovery.strategies,
          elapsedDiscoveryMs: discovery.elapsedMs,
          urls: report,
        },
        null,
        2,
      ),
      contentType: 'application/json',
    });

    const pageNotFound = report.filter((r) => r.pageNotFound);
    const badGrants = report.filter((r) => r.simplerOpportunity || r.viewOpportunity);

    if (pageNotFound.length > 0 || badGrants.length > 0) {
      const firstBad = pageNotFound[0] || badGrants[0];
      const cardMeta = discovery.grantsMeta.find((m) => m.idEdital === firstBad.idEdital) || {};
      await saveGrantsFailureEvidence(page, {
        title: cardMeta.textPreview?.split('\n')[0]?.slice(0, 120),
        id_edital: firstBad.idEdital || cardMeta.idEdital,
        fonte: firstBad.fonte || cardMeta.fonte,
        chosenUrl: firstBad.url,
        reason: firstBad.pageNotFound
          ? 'page_not_found_url_selected'
          : 'non_canonical_grants_url_selected',
      });
    }

    expect(pageNotFound, `URLs page-not-found: ${JSON.stringify(pageNotFound)}`).toEqual([]);
    expect(badGrants, `URLs Grants.gov não canonicalizadas: ${JSON.stringify(badGrants)}`).toEqual(
      [],
    );
  });
});

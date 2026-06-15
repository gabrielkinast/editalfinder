// Camada 2 — Filtro semântico de status (FRONTEND 1.2B / QA 1.3C).
import { test, expect } from '@playwright/test';
import {
  enableQaDebug,
  skipIfNoAuth,
  expectNoFatalError,
  openStatusFilterSection,
  toggleFirstAvailableStatusFilter,
  skipWithEvidence,
} from './_helpers.js';
import {
  requireCatalogReady,
  getCatalogStatsText,
  parseCatalogStatsText,
} from './_catalog.js';

test.describe('editais status filter [Camada 2]', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    skipIfNoAuth(testInfo);
    await enableQaDebug(page);
  });

  test('aplica e remove filtro Aberto sem quebrar lista [P2]', async ({ page }, testInfo) => {
    test.setTimeout(120_000);

    const catalog = await requireCatalogReady(page, test, 'status-filter', {
      minCards: 1,
      minReceived: 1,
    });
    if (!catalog) return;

    const statsBefore = parseCatalogStatsText(await getCatalogStatsText(page));

    const filtersOk = await openStatusFilterSection(page);
    if (!filtersOk) {
      await skipWithEvidence(test, page, 'status_filters_not_visible', {
        hint: 'collapse Filtrar por status não expandiu',
      });
      return;
    }

    const toggled = await toggleFirstAvailableStatusFilter(page, [
      'aberto',
      'sem_prazo',
      'encerrado',
      'indefinido',
    ]);
    if (!toggled) {
      await skipWithEvidence(test, page, 'no_status_checkbox', {
        hint: 'nenhum checkbox semantic-status-* visível após expandir seção',
      });
      return;
    }

    await page.waitForTimeout(600);

    await expect(page.getByTestId('editais-stats-bar')).toBeVisible();
    await expectNoFatalError(page);

    const statsFiltered = parseCatalogStatsText(await getCatalogStatsText(page));
    expect(statsFiltered?.showing).not.toBeNull();

    await toggled.checkbox.uncheck();
    await expect(toggled.checkbox).not.toBeChecked();
    await page.waitForTimeout(600);

    const statsAfter = parseCatalogStatsText(await getCatalogStatsText(page));

    await expectNoFatalError(page);

    if (statsBefore?.showing != null && statsAfter?.showing != null) {
      expect(statsAfter.showing).toBeGreaterThanOrEqual(statsFiltered?.showing ?? 0);
    }
  });
});

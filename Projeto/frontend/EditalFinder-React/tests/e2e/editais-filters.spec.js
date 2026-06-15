// Camada 2+3 — Filtros básicos Editais (QA 1.2 / QA 1.3C).
import { test, expect } from '@playwright/test';
import {
  enableQaDebug,
  skipIfNoAuth,
  expectNoFatalError,
  getFirstVisibleEditalCard,
  getSearchableCardTitle,
  openStatusFilterSection,
  toggleFirstAvailableStatusFilter,
  skipWithEvidence,
} from './_helpers.js';
import { requireCatalogReady, getCatalogStatsText } from './_catalog.js';

test.describe('editais filters [Camada 2/3]', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    skipIfNoAuth(testInfo);
    await enableQaDebug(page);
  });

  test('busca por título do card + filtro status sem erro fatal [P2]', async ({ page }, testInfo) => {
    test.setTimeout(90_000);

    const catalog = await requireCatalogReady(page, test, 'editais-filters', {
      minCards: 1,
      minReceived: 1,
    });
    if (!catalog) return;

    const card = await getFirstVisibleEditalCard(page);
    if (!card) {
      await skipWithEvidence(test, page, 'no_visible_cards', { phase: 'filters' });
      return;
    }

    const searchTerm = await getSearchableCardTitle(card);
    if (!searchTerm || searchTerm.length < 4) {
      await skipWithEvidence(test, page, 'card_title_too_short', { searchTerm });
      return;
    }

    const searchInput = page.getByTestId('editais-search-input');
    await expect(searchInput).toBeVisible({ timeout: 10_000 });
    await searchInput.fill(searchTerm);
    await page.waitForTimeout(700);

    await expect(searchInput).toHaveValue(searchTerm);
    await expect(page.getByTestId('editais-stats-bar')).toBeVisible();
    await expectNoFatalError(page);

    await searchInput.fill('');
    await page.waitForTimeout(500);

    const filtersOk = await openStatusFilterSection(page);
    if (!filtersOk) {
      await skipWithEvidence(test, page, 'status_filters_not_visible', {
        hint: 'sidebar mobile ou collapse Filtrar por status não expandiu',
      });
      return;
    }

    const toggled = await toggleFirstAvailableStatusFilter(page);
    if (!toggled) {
      await skipWithEvidence(test, page, 'no_status_checkbox', {});
      return;
    }

    await page.waitForTimeout(600);
    await expectNoFatalError(page);
    await expect(page.getByTestId('editais-stats-bar')).toBeVisible();

    await toggled.checkbox.uncheck();
    await expect(toggled.checkbox).not.toBeChecked();
    await page.waitForTimeout(500);
    await expectNoFatalError(page);

    const statsText = await getCatalogStatsText(page);
    expect(statsText).toMatch(/Mostrando/i);
  });
});

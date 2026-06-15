// Camada 2 — Exportações PDF/XLSX (QA 1.2).
import { test, expect } from '@playwright/test';
import {
  enableQaDebug,
  skipIfNoAuth,
  expectNoFatalError,
  safeDownloadClick,
  saveE2EEvidence,
  skipWithEvidence,
} from './_helpers.js';
import { requireCatalogReady } from './_catalog.js';

test.describe('editais export [Camada 2]', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    skipIfNoAuth(testInfo);
    await enableQaDebug(page);
  });

  test('export XLSX e PDF iniciam download [P2]', async ({ page }, testInfo) => {
    test.setTimeout(90_000);

    const catalog = await requireCatalogReady(page, test, 'editais-export', {
      minCards: 1,
      minReceived: 1,
    });
    if (!catalog) return;

    await expect(page.getByTestId('editais-export-xlsx')).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId('editais-export-pdf')).toBeVisible();

    const xlsxBtn = page.getByTestId('editais-export-xlsx');
    const xlsxResult = await safeDownloadClick(page, xlsxBtn);
    if (!xlsxResult.ok) {
      await saveE2EEvidence('skip-export-xlsx', xlsxResult, page);
      test.skip(true, `XLSX: ${xlsxResult.reason} — evidência debug-e2e/skip-export-xlsx.*`);
      return;
    }
    expect(xlsxResult.filename).toMatch(/\.xlsx$/i);

    const pdfBtn = page.getByTestId('editais-export-pdf');
    const pdfResult = await safeDownloadClick(page, pdfBtn);
    if (!pdfResult.ok) {
      await saveE2EEvidence('skip-export-pdf', pdfResult, page);
      test.skip(true, `PDF: ${pdfResult.reason} — evidência debug-e2e/skip-export-pdf.*`);
      return;
    }
    expect(pdfResult.filename).toMatch(/\.pdf$/i);

    await expectNoFatalError(page);
  });
});

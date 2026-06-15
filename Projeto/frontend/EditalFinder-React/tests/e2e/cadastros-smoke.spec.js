// Camada 2 — Cadastros smoke; escrita opt-in (QA 1.2 / QA 1.3C).
import { test, expect } from '@playwright/test';
import {
  enableQaDebug,
  skipIfNoAuth,
  expectNoFatalError,
  requireAuthenticatedPage,
  waitForPageReady,
  skipWithEvidence,
  isWriteTestsAllowed,
  skipIfNoWriteTests,
  saveE2EEvidence,
  navigateCadastrosEditaisTab,
  closeAdminEditalModal,
} from './_helpers.js';

test.describe('cadastros smoke [Camada 2]', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    skipIfNoAuth(testInfo);
    await enableQaDebug(page);
  });

  test('abre modal novo edital sem salvar [P2]', async ({ page }, testInfo) => {
    test.setTimeout(90_000);

    const auth = await requireAuthenticatedPage(page, '/cadastros');
    if (!auth.ok) {
      await skipWithEvidence(test, page, auth.reason, { route: '/cadastros' });
      return;
    }

    await waitForPageReady(page, 'cadastros-page');
    const body = await page.locator('body').innerText();
    expect(body).toMatch(/Cadastros|Editais/i);

    await navigateCadastrosEditaisTab(page);

    const novoBtn = page.getByTestId('cadastro-novo-edital');
    if (!(await novoBtn.isVisible({ timeout: 10_000 }).catch(() => false))) {
      const bodyAfterTab = await page.locator('body').innerText();
      const reason = bodyAfterTab.match(/permissão|permission|acesso negado/i)
        ? 'cadastro_without_permission'
        : 'cadastro_novo_edital_not_visible';
      await skipWithEvidence(test, page, reason, {
        hint: 'usuário pode não ter permissão canCreate ou aba Editais indisponível',
        activeTab: 'editais-cadastrados',
      });
      return;
    }

    await novoBtn.click();
    await expect(page.getByTestId('edital-form-titulo')).toBeVisible({ timeout: 10_000 });
    await expect(page.getByTestId('edital-form-link')).toBeVisible({ timeout: 10_000 });
    await page.getByTestId('edital-form-titulo').fill('E2E smoke — não salvar');
    await page.getByTestId('edital-form-link').fill('https://example.com/e2e-smoke-preview');

    await closeAdminEditalModal(page);
    await expectNoFatalError(page);
  });

  test('cria edital manual com flag E2E_ALLOW_WRITE_TESTS [P3]', async ({ page }, testInfo) => {
    skipIfNoWriteTests(testInfo);
    test.setTimeout(120_000);

    const auth = await requireAuthenticatedPage(page, '/cadastros');
    if (!auth.ok) {
      await skipWithEvidence(test, page, auth.reason, { route: '/cadastros', write: true });
      return;
    }

    await waitForPageReady(page, 'cadastros-page');
    await navigateCadastrosEditaisTab(page);

    const novoBtn = page.getByTestId('cadastro-novo-edital');
    if (!(await novoBtn.isVisible({ timeout: 10_000 }).catch(() => false))) {
      await skipWithEvidence(test, page, 'cadastro_novo_edital_not_visible', { write: true });
      return;
    }

    const ts = Date.now();
    const uniqueLink = `https://example.com/e2e-cadastro-${ts}`;
    const uniqueTitle = `E2E cadastro ${ts}`;

    await novoBtn.click();
    await page.getByTestId('edital-form-titulo').fill(uniqueTitle);
    await page.getByTestId('edital-form-link').fill(uniqueLink);
    await page.getByTestId('edital-form-submit').click();

    await expect(page.locator('body')).toContainText(/sucesso|cadastrado/i, { timeout: 45_000 });

    const body = await page.locator('body').innerText();
    const found = body.includes(uniqueTitle) || body.includes(String(ts));
    expect(found).toBe(true);

    await saveE2EEvidence('cadastros-write-ok', {
      title: uniqueTitle,
      link: uniqueLink,
      writeFlag: isWriteTestsAllowed(),
    });

    await expectNoFatalError(page);
  });
});

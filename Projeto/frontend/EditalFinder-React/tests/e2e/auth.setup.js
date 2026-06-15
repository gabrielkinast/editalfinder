/**
 * Setup de autenticação — roda uma vez antes dos projetos `authenticated`.
 * Salva storageState em playwright/.auth/user.json (gitignored).
 */
import { test as setup, expect } from '@playwright/test';
import { AUTH_STORAGE_PATH, ensureAuthDir, isAuthConfigured } from './_env.js';
import { enableQaDebug, loginIfConfigured, SKIP_NO_AUTH } from './_helpers.js';

setup('authenticate for E2E', async ({ page }) => {
  setup.skip(!isAuthConfigured(), SKIP_NO_AUTH);

  await enableQaDebug(page);
  const ok = await loginIfConfigured(page);
  expect(ok, 'login E2E deveria concluir com dashboard visível').toBe(true);

  ensureAuthDir();
  await page.context().storageState({ path: AUTH_STORAGE_PATH });
});

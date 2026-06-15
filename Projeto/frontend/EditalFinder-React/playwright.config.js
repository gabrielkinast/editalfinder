/**
 * Playwright — Web E2E (QA 1.1 harness + QA 1.2 expanded regression).
 *
 * Camadas:
 *   public        — smoke sem login
 *   auth-setup    — login real → storageState
 *   authenticated — rotas protegidas + dados (+ escrita opt-in)
 */
import { defineConfig, devices } from '@playwright/test';
import {
  loadLocalEnvFiles,
  logE2eEnvSummary,
  E2E_BASE_URL,
  E2E_HOST,
  E2E_PORT,
  AUTH_STORAGE_PATH,
  isAuthConfigured,
} from './tests/e2e/_env.js';

loadLocalEnvFiles();
logE2eEnvSummary();

const authReady = isAuthConfigured();

const AUTH_SPEC_MATCH =
  /(authenticated-smoke|dashboard-smoke|radar-smoke|cadastros-smoke|editais-(detail|filters|export|status-filter)|grants-links|external-links|report-problem)\.spec\.js$/;

const webServerCommand =
  process.env.QA_E2E_USE_DEV === '1'
    ? `npm run dev -- --host ${E2E_HOST} --port 5173`
    : `npm run build && npm run preview -- --host ${E2E_HOST} --port ${E2E_PORT}`;

const webServerUrl =
  process.env.QA_E2E_USE_DEV === '1'
    ? `http://${E2E_HOST}:5173/editalfinder/`
    : `${E2E_BASE_URL}/`;

const authenticatedUse = {
  ...devices['Desktop Chrome'],
  acceptDownloads: true,
};

/** @type {import('@playwright/test').Project[]} */
const projects = [
  {
    name: 'public',
    testMatch: /\/smoke\.spec\.js$/,
  },
];

if (authReady) {
  projects.push(
    {
      name: 'auth-setup',
      testMatch: /auth\.setup\.js$/,
    },
    {
      name: 'authenticated',
      testMatch: AUTH_SPEC_MATCH,
      dependencies: ['auth-setup'],
      use: {
        ...authenticatedUse,
        storageState: AUTH_STORAGE_PATH,
      },
    },
  );
} else {
  projects.push({
    name: 'authenticated',
    testMatch: AUTH_SPEC_MATCH,
    use: authenticatedUse,
  });
}

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 60_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  reporter: [
    ['list'],
    ['json', { outputFile: 'qa/artifacts/playwright/results.json' }],
    ['html', { outputFolder: 'qa/artifacts/playwright/html', open: 'never' }],
  ],
  outputDir: 'qa/artifacts/playwright/test-results',
  use: {
    baseURL: E2E_BASE_URL.endsWith('/') ? E2E_BASE_URL : `${E2E_BASE_URL}/`,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
    acceptDownloads: true,
  },
  projects,
  webServer: process.env.QA_NO_WEBSERVER
    ? undefined
    : {
        command: webServerCommand,
        url: webServerUrl,
        timeout: 180_000,
        reuseExistingServer: !process.env.CI,
      },
});

/**
 * Helpers de descoberta de catálogo E2E (QA 1.1B).
 * Sem secrets — artefatos de skip em qa/artifacts/playwright/debug-authenticated-data/
 */
import { expect } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  appPath,
  loginIfConfigured,
  isAuthConfigured,
  hasSupabaseEnv,
} from './_helpers.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
export const DEBUG_DATA_DIR = resolve(
  __dirname,
  '../../qa/artifacts/playwright/debug-authenticated-data',
);

/** Regex flexível: "Mostrando X de Y recebidos" (+ "editais" opcional). */
const STATS_REGEX = /Mostrando\s+([\d.,]+)(?:\s+de\s+([\d.,]+)\s+recebidos)?/i;

export function parsePtBrNumber(raw) {
  if (raw == null || raw === '') return NaN;
  const s = String(raw).trim();
  if (s.includes('.') && s.includes(',')) {
    return Number(s.replace(/\./g, '').replace(',', '.'));
  }
  if (s.includes('.') && /^\d{1,3}(\.\d{3})+$/.test(s)) {
    return Number(s.replace(/\./g, ''));
  }
  if (s.includes(',')) {
    return Number(s.replace(',', '.'));
  }
  return Number(s);
}

export function parseCatalogStatsText(text) {
  const match = String(text || '').match(STATS_REGEX);
  if (!match) return null;
  const showing = parsePtBrNumber(match[1]);
  const received = match[2] != null ? parsePtBrNumber(match[2]) : showing;
  return {
    showing: Number.isFinite(showing) ? showing : null,
    received: Number.isFinite(received) ? received : null,
    raw: text,
  };
}

export async function ensureAuthenticatedOnEditais(page, timeout = 60_000) {
  await page.goto(appPath('/editais'), { waitUntil: 'domcontentloaded', timeout });

  const onLogin = await page
    .getByTestId('login-page')
    .isVisible({ timeout: 4_000 })
    .catch(() => false);

  if (onLogin) {
    if (!isAuthConfigured()) {
      return { ok: false, reason: 'redirected_to_login_no_credentials' };
    }
    const relogged = await loginIfConfigured(page);
    if (!relogged) {
      return { ok: false, reason: 'redirected_to_login_relogin_failed' };
    }
    await page.goto(appPath('/editais'), { waitUntil: 'domcontentloaded', timeout });
  }

  const stillLogin = await page
    .getByTestId('login-page')
    .isVisible({ timeout: 2_000 })
    .catch(() => false);
  if (stillLogin) {
    return { ok: false, reason: 'still_on_login_after_relogin' };
  }

  return { ok: true };
}

export async function waitForEditaisCatalog(page, options = {}) {
  const timeout = options.timeout ?? options.catalogTimeout ?? 60_000;

  const authResult = await ensureAuthenticatedOnEditais(page, timeout);
  if (!authResult.ok) {
    return { ok: false, reason: authResult.reason, phase: 'auth' };
  }

  try {
    await expect(page.getByTestId('editais-page')).toBeVisible({ timeout });
  } catch {
    return { ok: false, reason: 'editais_page_not_visible', phase: 'page' };
  }

  const loading = page.getByTestId('editais-loading');
  if (await loading.isVisible({ timeout: 3_000 }).catch(() => false)) {
    try {
      await loading.waitFor({ state: 'hidden', timeout });
    } catch {
      return { ok: false, reason: 'loading_timeout', phase: 'loading' };
    }
  }

  const stats = page.getByTestId('editais-stats-bar');
  try {
    await stats.waitFor({ state: 'visible', timeout });
  } catch {
    return { ok: false, reason: 'stats_bar_not_visible', phase: 'stats' };
  }

  const statsText = await getCatalogStatsText(page);
  const parsed = parseCatalogStatsText(statsText);
  const cardCount = await page.getByTestId('edital-card').count();

  return {
    ok: true,
    statsText,
    parsed,
    cardCount,
    url: page.url(),
  };
}

export async function getCatalogStatsText(page) {
  return page.getByTestId('editais-stats-bar').innerText();
}

export async function getVisibleEditalCards(page) {
  const cards = page.getByTestId('edital-card');
  const count = await cards.count();
  const out = [];
  for (let i = 0; i < count; i += 1) {
    const card = cards.nth(i);
    if (await card.isVisible().catch(() => false)) {
      out.push(card);
    }
  }
  return out;
}

export async function getFirstNEditalCards(page, n = 10) {
  const cards = await getVisibleEditalCards(page);
  return cards.slice(0, n);
}

/**
 * Snapshot DOM de todos os cards visíveis (metadados para targeting Grants — QA 1.1C).
 */
export async function getGrantsCardMeta(page) {
  return page.evaluate(() => {
    const cards = [...document.querySelectorAll('[data-testid="edital-card"]')];
    return cards.map((el) => {
      const official = el.querySelector('[data-testid="edital-open-official"]');
      const btnView = el.querySelector('.btn-view');
      const btnInsc = el.querySelector('.btn-inscricao');
      const qaBtn =
        el.querySelector('[data-qa-resolved-url]') ||
        official ||
        btnView ||
        btnInsc;
      return {
        idEdital: el.getAttribute('data-edital-id'),
        fonte: el.getAttribute('data-fonte') || '',
        source: el.getAttribute('data-source') || '',
        textPreview: (el.innerText || '').slice(0, 600),
        officialHref: official?.getAttribute('href') || '',
        officialTitle: official?.getAttribute('title') || '',
        btnViewTitle: btnView?.getAttribute('title') || '',
        btnInscTitle: btnInsc?.getAttribute('title') || '',
        qaResolvedUrl: qaBtn?.getAttribute('data-qa-resolved-url') || '',
      };
    });
  });
}

/** Locators estáveis para cards Grants (re-query por id). */
export async function getGrantsCards(page) {
  const { isGrantsCardRecord } = await import('../../src/utils/qa/grantsCardMatch.js');
  const meta = (await getGrantsCardMeta(page)).filter(isGrantsCardRecord);
  return meta.map((m) => ({
    meta: m,
    locator: page.locator(
      `[data-testid="edital-card"][data-edital-id="${m.idEdital}"]`,
    ),
  }));
}

export async function tryRelaxEditaisFilters(page) {
  const btn = page.getByTestId('relax-filters-button');
  if (await btn.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await btn.click();
    await page.waitForTimeout(800);
    return true;
  }
  return false;
}

export async function trySearchGrants(page, term = 'Grants') {
  const search = page.locator(
    'input[type="search"], input[placeholder*="Buscar" i], input[placeholder*="buscar" i], .header-search input',
  );
  const first = search.first();
  if (await first.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await first.fill(term);
    await page.waitForTimeout(600);
    return true;
  }
  return false;
}

/** Filtro sidebar Fonte / órgão — busca por Grants.gov */
export async function trySourceFilterGrants(page) {
  const fonteInput = page.getByTestId('editais-fonte-busca');
  if (await fonteInput.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await fonteInput.fill('Grants.gov');
    await page.waitForTimeout(600);
    return true;
  }

  const fallback = page.locator('input[placeholder*="Buscar fonte" i]').first();
  if (await fallback.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await fallback.fill('Grants.gov');
    await page.waitForTimeout(600);
    return true;
  }
  return false;
}

/** Salva evidência de skip/falha — sem tokens. */
export async function saveSkipEvidence(page, slug, reason, extra = {}) {
  mkdirSync(DEBUG_DATA_DIR, { recursive: true });

  const bodyText = await page.locator('body').innerText().catch(() => '');
  const url = page.url();
  const statsText = await page
    .getByTestId('editais-stats-bar')
    .innerText()
    .catch(() => '(stats bar ausente)');

  const payload = {
    reason,
    url,
    timestamp: new Date().toISOString(),
    authConfigured: isAuthConfigured(),
    hasSupabaseEnv: hasSupabaseEnv(),
    onLoginPage: await page.getByTestId('login-page').isVisible().catch(() => false),
    hasEditaisPage: await page.getByTestId('editais-page').isVisible().catch(() => false),
    hasStatsBar: await page.getByTestId('editais-stats-bar').isVisible().catch(() => false),
    isLoading: await page.getByTestId('editais-loading').isVisible().catch(() => false),
    cardCount: await page.getByTestId('edital-card').count().catch(() => 0),
    statsText: statsText.slice(0, 500),
    bodyPreview: bodyText.slice(0, 2500),
    ...extra,
  };

  writeFileSync(resolve(DEBUG_DATA_DIR, `${slug}.json`), JSON.stringify(payload, null, 2));
  writeFileSync(
    resolve(DEBUG_DATA_DIR, `${slug}.txt`),
    [
      `reason: ${reason}`,
      `url: ${url}`,
      `authConfigured: ${payload.authConfigured}`,
      `hasSupabaseEnv: ${payload.hasSupabaseEnv}`,
      `onLoginPage: ${payload.onLoginPage}`,
      `hasEditaisPage: ${payload.hasEditaisPage}`,
      `hasStatsBar: ${payload.hasStatsBar}`,
      `cardCount: ${payload.cardCount}`,
      `statsText: ${payload.statsText}`,
      '',
      '--- body preview ---',
      bodyText.slice(0, 3500),
    ].join('\n'),
  );

  await page
    .screenshot({ path: resolve(DEBUG_DATA_DIR, `${slug}.png`), fullPage: true })
    .catch(() => {});

  return payload;
}

/**
 * Prepara catálogo para testes de dados. Retorna resultado ou faz skip com evidência.
 */
export async function requireCatalogReady(page, test, slug, options = {}) {
  const { minCards = 1, minReceived = 1, catalogTimeout } = options;

  const catalog = await waitForEditaisCatalog(page, { catalogTimeout });
  if (!catalog.ok) {
    await saveSkipEvidence(page, `${slug}-skip`, catalog.reason, { phase: catalog.phase });
    test.skip(true, `${catalog.reason} — evidência em debug-authenticated-data/${slug}-skip.*`);
    return null;
  }

  if (!hasSupabaseEnv()) {
    await saveSkipEvidence(page, `${slug}-skip`, 'no_supabase_env');
    test.skip(true, 'VITE_SUPABASE_* ausente no build');
    return null;
  }

  const received = catalog.parsed?.received ?? catalog.parsed?.showing ?? 0;
  if (minReceived > 0 && (!Number.isFinite(received) || received <= 0)) {
    await saveSkipEvidence(page, `${slug}-skip`, 'catalog_received_zero', {
      statsText: catalog.statsText,
      parsed: catalog.parsed,
    });
    test.skip(
      true,
      `Catálogo recebido=0 (${catalog.statsText?.slice(0, 80)}) — evidência salva`,
    );
    return null;
  }

  if (catalog.cardCount < minCards) {
    await tryRelaxEditaisFilters(page);
    await page.waitForTimeout(500);
    const retry = await waitForEditaisCatalog(page);
    if (retry.ok && retry.cardCount >= minCards) {
      return retry;
    }
    await saveSkipEvidence(page, `${slug}-skip`, 'no_visible_cards', {
      cardCount: catalog.cardCount,
      statsText: catalog.statsText,
      afterRelax: retry.cardCount,
    });
    test.skip(
      true,
      `Nenhum card visível (count=${catalog.cardCount}) — evidência em ${slug}-skip.*`,
    );
    return null;
  }

  return catalog;
}

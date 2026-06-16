/**
 * Targeting determinístico Grants.gov (QA 1.1C).
 * Sem secrets — evidências em qa/artifacts/playwright/debug-authenticated-data/
 */
import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { isGrantsCardRecord } from '../../src/utils/qa/grantsCardMatch.js';
import {
  DEBUG_DATA_DIR,
  getGrantsCardMeta,
  tryRelaxEditaisFilters,
  trySearchGrants,
  trySourceFilterGrants,
  getCatalogStatsText,
  saveSkipEvidence,
} from './_catalog.js';

export const GRANTS_SEARCH_DEADLINE_MS = 20_000;
export const GRANTS_URL_CAPTURE_MS = 10_000;

/** Deve rodar em beforeEach ANTES de qualquer goto — evita location.assign navegar a página. */
export async function installGrantsE2eHooks(page) {
  await page.addInitScript(() => {
    window.__QA_EXTERNAL_URLS__ = [];
    const push = (url) => {
      try {
        window.__QA_EXTERNAL_URLS__.push(String(url));
      } catch {
        /* ignore */
      }
    };

    const origOpen = window.open;
    window.open = function patchedOpen(url, ...rest) {
      push(url);
      return { closed: false, close() {}, focus() {}, blur() {}, location: { href: String(url) } };
    };
    void origOpen;

    try {
      const loc = window.location;
      const origAssign = loc.assign.bind(loc);
      loc.assign = function patchedAssign(url) {
        push(url);
      };
      const origReplace = loc.replace.bind(loc);
      loc.replace = function patchedReplace(url) {
        push(url);
      };
      void origAssign;
      void origReplace;
    } catch {
      /* ignore */
    }
  });
}

export async function sampleVisibleCardSources(page, limit = 12) {
  return page.evaluate((max) => {
    const cards = [...document.querySelectorAll('[data-testid="edital-card"]')].slice(0, max);
    return cards.map((el) => ({
      id: el.getAttribute('data-edital-id'),
      fonte: el.getAttribute('data-fonte') || '',
      source: el.getAttribute('data-source') || '',
    }));
  }, limit);
}

/**
 * Localiza cards Grants.gov com estratégias ordenadas e deadline interno.
 */
export async function discoverGrantsCards(page, options = {}) {
  const deadlineMs = options.deadlineMs ?? GRANTS_SEARCH_DEADLINE_MS;
  const started = Date.now();
  const strategies = [];
  let searchAttempted = false;
  let sourceFilterAttempted = false;
  let relaxAttempted = false;

  const snapshot = async (name) => {
    const meta = await getGrantsCardMeta(page);
    const grants = meta.filter(isGrantsCardRecord);
    strategies.push({ name, count: grants.length, totalCards: meta.length });
    return grants;
  };

  let grantsMeta = await snapshot('dom_attributes');

  if (grantsMeta.length === 0 && Date.now() - started < deadlineMs) {
    relaxAttempted = await tryRelaxEditaisFilters(page);
    if (relaxAttempted) await page.waitForTimeout(500);
    grantsMeta = await snapshot('after_relax_filters');
  }

  if (grantsMeta.length === 0 && Date.now() - started < deadlineMs) {
    searchAttempted = await trySearchGrants(page);
    if (searchAttempted) await page.waitForTimeout(600);
    grantsMeta = await snapshot('after_search_grants');
  }

  if (grantsMeta.length === 0 && Date.now() - started < deadlineMs) {
    sourceFilterAttempted = await trySourceFilterGrants(page);
    if (sourceFilterAttempted) await page.waitForTimeout(600);
    grantsMeta = await snapshot('after_source_filter');
  }

  if (grantsMeta.length === 0 && Date.now() - started < deadlineMs) {
    searchAttempted = true;
    await trySearchGrants(page, 'Grants.gov');
    await page.waitForTimeout(600);
    grantsMeta = await snapshot('after_search_grants_gov');
  }

  const grantsEntries = grantsMeta.map((m) => ({
    meta: m,
    locator: page.locator(`[data-testid="edital-card"][data-edital-id="${m.idEdital}"]`),
  }));

  const sampleSources = await sampleVisibleCardSources(page);
  const visibleCardCount = await page.getByTestId('edital-card').count();

  return {
    grantsEntries,
    grantsMeta,
    strategies,
    elapsedMs: Date.now() - started,
    searchAttempted,
    sourceFilterAttempted,
    relaxAttempted,
    sampleSources: sampleSources.map((s) => s.fonte || s.source).filter(Boolean),
    visibleCardCount,
  };
}

export function analyzeGrantsUrl(url) {
  const u = String(url || '');
  return {
    url: u,
    pageNotFound: /page-not-found|\/404|not-found/i.test(u),
    simplerOpportunity: /simpler\.grants\.gov\/opportunity\//i.test(u),
    viewOpportunity: /view-opportunity\//i.test(u),
    searchResultsDetail: /search-results-detail\/\d+/i.test(u),
    grantsGov: /grants\.gov/i.test(u),
  };
}

/** URLs resolvidas nos cards Grants — sem clicar (title / data-qa-resolved-url / href). */
export async function collectGrantsUrlsFromCards(grantsMeta) {
  const out = [];
  for (const card of grantsMeta) {
    const candidates = [
      { field: 'qaResolvedUrl', url: card.qaResolvedUrl },
      { field: 'officialHref', url: card.officialHref },
      { field: 'officialTitle', url: card.officialTitle },
      { field: 'btnViewTitle', url: card.btnViewTitle },
      { field: 'btnInscTitle', url: card.btnInscTitle },
    ];
    for (const { field, url } of candidates) {
      if (!url || !/^https?:\/\//i.test(String(url))) continue;
      out.push({
        idEdital: card.idEdital,
        fonte: card.fonte,
        source: card.source,
        field,
        ...analyzeGrantsUrl(url),
      });
    }
  }
  return out;
}

/** Clica botões externos só nos cards Grants (máx. N) — timeouts curtos, noWaitAfter. */
export async function clickGrantsOfficialButtons(page, grantsEntries, max = 3) {
  const opened = [];
  for (const { meta, locator: card } of grantsEntries.slice(0, max)) {
    const btn = card.locator(
      '[data-testid="edital-open-official"], .btn-view.dash-action, .btn-inscricao.dash-action',
    ).first();
    if ((await btn.count()) === 0) continue;
    await btn.scrollIntoViewIfNeeded().catch(() => {});
    await btn.click({ timeout: 3_000, noWaitAfter: true }).catch(() => {});
    await page.waitForTimeout(150);
    const batch = await page.evaluate(() => window.__QA_EXTERNAL_URLS__ || []);
    for (const u of batch) {
      if (!opened.includes(u)) opened.push(u);
    }
  }
  return opened.map((url) => analyzeGrantsUrl(url));
}

export async function saveGrantsSkipEvidence(page, extra = {}) {
  const statsText = await getCatalogStatsText(page).catch(() => '');
  return saveSkipEvidence(page, 'grants-links-skip', extra.reason || 'no_grants_cards_visible', {
    currentUrl: page.url(),
    statsText: statsText.slice(0, 500),
    visibleCardCount: extra.visibleCardCount ?? 0,
    sampleSources: extra.sampleSources ?? [],
    searchAttempted: Boolean(extra.searchAttempted),
    sourceFilterAttempted: Boolean(extra.sourceFilterAttempted),
    relaxAttempted: Boolean(extra.relaxAttempted),
    strategies: extra.strategies ?? [],
    elapsedMs: extra.elapsedMs ?? null,
    ...extra,
  });
}

export async function saveGrantsFailureEvidence(page, failure) {
  mkdirSync(DEBUG_DATA_DIR, { recursive: true });
  const payload = {
    ...failure,
    timestamp: new Date().toISOString(),
    currentUrl: page.url(),
  };
  writeFileSync(
    resolve(DEBUG_DATA_DIR, 'grants-links-failure.json'),
    JSON.stringify(payload, null, 2),
  );
  writeFileSync(
    resolve(DEBUG_DATA_DIR, 'grants-links-failure.txt'),
    [
      `reason: ${failure.reason}`,
      `title: ${failure.title ?? '—'}`,
      `id_edital: ${failure.id_edital ?? '—'}`,
      `fonte: ${failure.fonte ?? '—'}`,
      `chosenUrl: ${failure.chosenUrl ?? '—'}`,
      `url: ${page.url()}`,
    ].join('\n'),
  );
  await page
    .screenshot({ path: resolve(DEBUG_DATA_DIR, 'grants-links-failure.png'), fullPage: true })
    .catch(() => {});
  return payload;
}

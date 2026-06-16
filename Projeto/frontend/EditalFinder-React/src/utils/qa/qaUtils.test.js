import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  isExternalLinkDebugEnabled,
  buildExternalLinkDebugRecord,
  classifyExternalUrl,
  logExternalLinkDebug,
  EXTERNAL_LINKS_LS_KEY,
} from './externalLinkDebug.js';
import {
  isRouteDebugEnabled,
  detectFatalError,
  buildRouteDebugRecord,
} from './routeDebug.js';
import { SMOKE_FLOWS, getSmokeFlows, getSmokeFlowsByPriority, FATAL_ERROR_TEXTS } from './smokeFlows.js';

function fakeWin(store = {}) {
  return {
    localStorage: {
      getItem: (k) => (k in store ? store[k] : null),
    },
  };
}

test('externalLinkDebug desabilitado por padrão', () => {
  assert.equal(isExternalLinkDebugEnabled({ env: {}, win: fakeWin() }), false);
});

test('externalLinkDebug habilita por env VITE_DEBUG_EXTERNAL_LINKS', () => {
  assert.equal(isExternalLinkDebugEnabled({ env: { VITE_DEBUG_EXTERNAL_LINKS: '1' }, win: fakeWin() }), true);
});

test('externalLinkDebug habilita por localStorage', () => {
  const win = fakeWin({ [EXTERNAL_LINKS_LS_KEY]: 'true' });
  assert.equal(isExternalLinkDebugEnabled({ env: {}, win }), true);
});

test('classifyExternalUrl detecta page-not-found e canônicos', () => {
  assert.equal(classifyExternalUrl('https://www.grants.gov/page-not-found').pageNotFound, true);
  assert.equal(classifyExternalUrl('https://www.grants.gov/search-results-detail/361410').searchResultsDetail, true);
  assert.equal(classifyExternalUrl('https://simpler.grants.gov/opportunity/1').simplerOpportunity, true);
});

test('buildExternalLinkDebugRecord canonicaliza Grants.gov e não vaza segredo', () => {
  const rec = buildExternalLinkDebugRecord({
    titulo: 'NSF Grant',
    fonte: 'Grants.gov',
    link: 'https://simpler.grants.gov/opportunity/361410',
  });
  assert.equal(rec.chosenUrl, 'https://www.grants.gov/search-results-detail/361410');
  assert.equal(rec.canonicalized, true);
  assert.equal(rec.flags.searchResultsDetail, true);
  assert.ok(!('token' in rec) && !('key' in rec));
});

test('logExternalLinkDebug não loga quando desabilitado', () => {
  let called = 0;
  const logger = { log: () => { called += 1; }, warn: () => { called += 1; } };
  const did = logExternalLinkDebug({ titulo: 'x', link: 'https://x' }, { env: {}, win: fakeWin(), logger });
  assert.equal(did, false);
  assert.equal(called, 0);
});

test('logExternalLinkDebug usa warn em page-not-found quando habilitado', () => {
  const calls = [];
  const logger = { log: (...a) => calls.push(['log', ...a]), warn: (...a) => calls.push(['warn', ...a]) };
  const did = logExternalLinkDebug(
    { titulo: 'x', fonte: 'Grants.gov', link: 'https://www.grants.gov/page-not-found' },
    { env: { VITE_DEBUG_EXTERNAL_LINKS: '1' }, win: fakeWin(), logger },
  );
  assert.equal(did, true);
  // chosenUrl cai no fallback de busca (não page-not-found), então loga normal.
  assert.ok(calls.length === 1);
});

test('routeDebug desabilitado por padrão / habilita por env', () => {
  assert.equal(isRouteDebugEnabled({ env: {}, win: fakeWin() }), false);
  assert.equal(isRouteDebugEnabled({ env: { VITE_DEBUG_ROUTES: '1' }, win: fakeWin() }), true);
});

test('detectFatalError encontra mensagens conhecidas', () => {
  assert.equal(detectFatalError('tudo certo').hasFatalError, false);
  const r = detectFatalError('Erro: Não foi possível carregar os dados do edital.');
  assert.equal(r.hasFatalError, true);
  assert.match(r.matched, /Não foi possível carregar/);
});

test('buildRouteDebugRecord aceita rota explícita', () => {
  const rec = buildRouteDebugRecord({ route: '/editais', win: fakeWin() });
  assert.equal(rec.route, '/editais');
  assert.ok(typeof rec.ts === 'string');
});

test('smokeFlows: matriz íntegra e por prioridade', () => {
  assert.ok(Array.isArray(SMOKE_FLOWS) && SMOKE_FLOWS.length >= 3);
  assert.deepEqual(getSmokeFlows(), SMOKE_FLOWS);
  const p0 = getSmokeFlowsByPriority('P0');
  assert.ok(p0.every((f) => f.priority === 'P0'));
  for (const flow of SMOKE_FLOWS) {
    assert.ok(flow.id && flow.route && Array.isArray(flow.actions));
  }
  assert.ok(FATAL_ERROR_TEXTS.includes('Não foi possível carregar os dados do edital'));
});

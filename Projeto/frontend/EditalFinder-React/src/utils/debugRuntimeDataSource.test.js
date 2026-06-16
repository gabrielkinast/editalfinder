import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  detectRuntime,
  safeHost,
  redactKey,
  listEditalLocalStorageKeys,
  getRuntimeDataSourceInfo,
} from './debugRuntimeDataSource.js';
import {
  dataCountsEnabled,
  isDataCountDebugEnabled,
  DATA_COUNTS_LS_KEY,
  probeCount,
  logEditalDataCounts,
  logEditaisClientCounts,
} from './debugDataCounts.js';

// --------------------------------------------------------------------------
// detectRuntime
// --------------------------------------------------------------------------

test('detectRuntime: build Tauri => desktop_tauri', () => {
  assert.equal(detectRuntime({ win: {}, isTauriBuild: true }), 'desktop_tauri');
});

test('detectRuntime: window.__TAURI__ presente => desktop_tauri', () => {
  assert.equal(detectRuntime({ win: { __TAURI__: {} }, isTauriBuild: false }), 'desktop_tauri');
  assert.equal(
    detectRuntime({ win: { __TAURI_INTERNALS__: {} }, isTauriBuild: false }),
    'desktop_tauri',
  );
});

test('detectRuntime: window sem Tauri => web', () => {
  assert.equal(detectRuntime({ win: { location: {} }, isTauriBuild: false }), 'web');
});

test('detectRuntime: sem window => unknown', () => {
  assert.equal(detectRuntime({ win: undefined, isTauriBuild: false }), 'unknown');
});

// --------------------------------------------------------------------------
// segurança: nunca expõe a chave
// --------------------------------------------------------------------------

test('safeHost extrai apenas o host', () => {
  assert.equal(safeHost('https://abc.supabase.co/rest/v1?x=1'), 'abc.supabase.co');
  assert.equal(safeHost('not a url'), '');
});

test('redactKey nunca devolve a chave completa', () => {
  const key = 'eyJABCDEFGHIJKLMNOPqrstuvwxyz0123456789';
  const r = redactKey(key);
  assert.equal(r.hasKey, true);
  assert.ok(!('full' in r));
  assert.ok(!Object.values(r).some((v) => String(v).length >= key.length));
  assert.match(r.keyPreview, /^eyJA….*6789$/);
});

test('redactKey vazio => hasKey false', () => {
  assert.deepEqual(redactKey(''), { hasKey: false });
  assert.deepEqual(redactKey(null), { hasKey: false });
});

test('getRuntimeDataSourceInfo não inclui a anon key (só host + hasKey)', () => {
  const info = getRuntimeDataSourceInfo({
    env: { DEV: true, MODE: 'tauri', VITE_APP_VERSION: '0.1.0', VITE_APP_ENV: 'local' },
    win: { location: { pathname: '/editais', origin: 'tauri://localhost' } },
    isTauriBuild: true,
    supabaseUrl: 'https://abc.supabase.co',
    supabaseAnonKey: 'super-secret-anon-key-value',
    viewEditais: 'vw_editais_front',
  });
  const blob = JSON.stringify(info);
  assert.ok(!blob.includes('super-secret-anon-key-value'));
  assert.equal(info.hasSupabaseAnonKey, true);
  assert.equal(info.supabaseUrlHost, 'abc.supabase.co');
  assert.equal(info.runtime, 'desktop_tauri');
  assert.equal(info.isTauri, true);
  assert.equal(info.appVersion, '0.1.0');
  assert.equal(info.dataSourceMode, 'supabase_live');
});

test('listEditalLocalStorageKeys filtra chaves relevantes sem valores', () => {
  const store = {
    editais_favoritos_v1: '[]',
    editaisPagePrefs: '{}',
    theme: 'dark',
    randomKey: 'x',
  };
  const keys = Object.keys(store);
  const win = {
    localStorage: {
      length: keys.length,
      key: (i) => keys[i],
      getItem: (k) => store[k],
    },
  };
  const found = listEditalLocalStorageKeys(win);
  assert.ok(found.includes('editais_favoritos_v1'));
  assert.ok(found.includes('editaisPagePrefs'));
  assert.ok(!found.includes('theme'));
});

// --------------------------------------------------------------------------
// debugDataCounts
// --------------------------------------------------------------------------

test('dataCountsEnabled só liga com valores truthy', () => {
  assert.equal(dataCountsEnabled({ VITE_DEBUG_DATA_COUNTS: '1' }), true);
  assert.equal(dataCountsEnabled({ VITE_DEBUG_DATA_COUNTS: 'true' }), true);
  assert.equal(dataCountsEnabled({ VITE_DEBUG_DATA_COUNTS: 'on' }), true);
  assert.equal(dataCountsEnabled({ VITE_DEBUG_DATA_COUNTS: '0' }), false);
  assert.equal(dataCountsEnabled({ VITE_DEBUG_DATA_COUNTS: '' }), false);
  assert.equal(dataCountsEnabled({}), false);
});

test('isDataCountDebugEnabled liga por env OU por localStorage', () => {
  // env liga
  assert.equal(isDataCountDebugEnabled({ env: { VITE_DEBUG_DATA_COUNTS: '1' }, win: {} }), true);
  // env desligado + localStorage ligado
  const win = { localStorage: { getItem: (k) => (k === DATA_COUNTS_LS_KEY ? '1' : null) } };
  assert.equal(isDataCountDebugEnabled({ env: {}, win }), true);
  // ambos desligados
  const off = { localStorage: { getItem: () => null } };
  assert.equal(isDataCountDebugEnabled({ env: {}, win: off }), false);
});

function fakeSupabase(count, error = null) {
  const calls = {};
  return {
    calls,
    from(table) {
      calls.table = table;
      return {
        select(cols, opts) {
          calls.select = { cols, opts };
          return Promise.resolve({ count, error: error ? { message: error } : null });
        },
      };
    },
  };
}

test('probeCount usa head:true e count:exact (não traz payload)', async () => {
  const sb = fakeSupabase(1051);
  const r = await probeCount(sb, 'vw_editais_front');
  assert.equal(r.count, 1051);
  assert.equal(r.error, null);
  assert.equal(sb.calls.table, 'vw_editais_front');
  assert.equal(sb.calls.select.opts.head, true);
  assert.equal(sb.calls.select.opts.count, 'exact');
});

test('logEditalDataCounts é no-op sem a flag', async () => {
  const sb = fakeSupabase(1051);
  const out = await logEditalDataCounts({
    supabase: sb,
    viewName: 'vw_editais_front',
    env: {},
    consoleObj: { info() {} },
  });
  assert.equal(out, null);
  assert.equal(sb.calls.table, undefined); // nem chegou a consultar
});

test('logEditalDataCounts separa rawCount, catalogCount e filteredCount', async () => {
  const sb = fakeSupabase(1051);
  let logged = null;
  const out = await logEditalDataCounts({
    supabase: sb,
    viewName: 'vw_editais_front',
    catalogCount: 1051,
    filteredCount: 430,
    env: { VITE_DEBUG_DATA_COUNTS: '1', VITE_APP_VERSION: '0.1.0' },
    consoleObj: { info: (_tag, payload) => { logged = payload; } },
  });
  assert.equal(out.rawCount, 1051);
  assert.equal(out.catalogCount, 1051);
  assert.equal(out.filteredCount, 430);
  assert.equal(logged.rawCount, 1051);
  assert.equal(logged.filteredCount, 430);
});

test('logEditaisClientCounts é no-op sem a flag e não consulta rede', () => {
  const out = logEditaisClientCounts({
    catalogCount: 1051,
    filteredCount: 430,
    env: {},
    consoleObj: { info() {} },
  });
  assert.equal(out, null);
});

test('logEditaisClientCounts loga catalog/filtered + runtime com a flag', () => {
  let logged = null;
  const out = logEditaisClientCounts({
    catalogCount: 1051,
    filteredCount: 430,
    env: { VITE_DEBUG_DATA_COUNTS: '1', VITE_SUPABASE_URL: 'https://abc.supabase.co', VITE_APP_VERSION: '0.1.0' },
    consoleObj: { info: (_tag, payload) => { logged = payload; } },
  });
  assert.equal(out.catalogCount, 1051);
  assert.equal(out.filteredCount, 430);
  assert.equal(logged.supabaseHost, 'abc.supabase.co');
  assert.equal(logged.viewEditais, 'vw_editais_front');
});

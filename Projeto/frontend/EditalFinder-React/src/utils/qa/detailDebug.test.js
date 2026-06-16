import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  isDetailDebugEnabled,
  buildDetailDebugRecord,
  logDetailDebug,
  DETAIL_DEBUG_LS_KEY,
} from './detailDebug.js';

function fakeWin(store = {}) {
  return {
    localStorage: {
      getItem: (k) => (k in store ? store[k] : null),
    },
  };
}

test('detailDebug desabilitado por padrão', () => {
  assert.equal(isDetailDebugEnabled({ env: {}, win: fakeWin() }), false);
});

test('detailDebug habilita por env ou localStorage', () => {
  assert.equal(isDetailDebugEnabled({ env: { VITE_DEBUG_ROUTE_DETAIL: '1' }, win: fakeWin() }), true);
  assert.equal(
    isDetailDebugEnabled({ env: {}, win: fakeWin({ [DETAIL_DEBUG_LS_KEY]: 'true' }) }),
    true,
  );
});

test('buildDetailDebugRecord monta campos esperados', () => {
  const rec = buildDetailDebugRecord({
    routeParam: '42',
    normalizedId: '42',
    lookupBaseFound: false,
    lookupViewFound: true,
    finalFound: true,
    lookupMode: 'view',
    attachmentsOk: false,
    attachmentsError: 'RLS',
    errorKind: null,
  });
  assert.equal(rec.routeParam, '42');
  assert.equal(rec.lookupViewFound, true);
  assert.equal(rec.attachmentsOk, false);
  assert.ok(!('token' in rec));
});

test('logDetailDebug só loga quando habilitado', () => {
  let n = 0;
  const logger = { log: () => { n += 1; } };
  assert.equal(logDetailDebug({ routeParam: '1' }, { env: {}, win: fakeWin(), logger }), false);
  assert.equal(n, 0);
  assert.equal(
    logDetailDebug({ routeParam: '1' }, { env: { VITE_DEBUG_ROUTE_DETAIL: '1' }, logger }),
    true,
  );
  assert.equal(n, 1);
});

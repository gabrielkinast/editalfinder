import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  normalizeEditalRouteId,
  normalizeEditalDetailRow,
  lookupEditalForDetail,
  lookupAnexosForDetail,
  getEditalDetailErrorMessage,
  DETAIL_ERROR_KIND,
  DETAIL_LOOKUP_MODE,
} from './editalDetailLookup.js';

function makeSupabase(handlers) {
  const calls = [];
  const supabase = {
    calls,
    from(table) {
      const state = { table, filters: [], order: null };
      const builder = {
        select() {
          return builder;
        },
        eq(col, val) {
          state.filters.push({ col, val });
          return builder;
        },
        order(col, opts) {
          state.order = { col, opts };
          return builder;
        },
        async maybeSingle() {
          calls.push({ table, filters: [...state.filters], method: 'maybeSingle' });
          const key = `${table}:${state.filters.map((f) => `${f.col}=${f.val}`).join('&')}:maybeSingle`;
          const fn = handlers[key] ?? handlers[`${table}:maybeSingle`] ?? handlers.defaultMaybeSingle;
          if (typeof fn === 'function') return fn(state);
          return { data: null, error: null };
        },
        async then(resolve, reject) {
          try {
            calls.push({ table, filters: [...state.filters], method: 'select' });
            const key = `${table}:${state.filters.map((f) => `${f.col}=${f.val}`).join('&')}:select`;
            const fn = handlers[key] ?? handlers[`${table}:select`] ?? handlers.defaultSelect;
            const result = typeof fn === 'function' ? fn(state) : { data: [], error: null };
            resolve(result);
          } catch (e) {
            reject(e);
          }
        },
      };
      return builder;
    },
  };
  return supabase;
}

test('normalizeEditalRouteId aceita string, numérico e prefixo manual-', () => {
  const a = normalizeEditalRouteId('manual-42');
  assert.ok(a.candidates.includes('42'));
  assert.ok(a.candidates.includes(42));
  assert.equal(a.normalizedId, '42');

  const b = normalizeEditalRouteId('99');
  assert.ok(b.candidates.includes('99'));
  assert.ok(b.candidates.includes(99));
});

test('normalizeEditalDetailRow mapeia extras e aliases da view', () => {
  const row = normalizeEditalDetailRow(
    { id_edital: 1, extras_raw: { x: 1 }, fonte: 'FAPESP', fim_inscricao: '2026-01-01' },
    DETAIL_LOOKUP_MODE.VIEW,
  );
  assert.deepEqual(row.extras, { x: 1 });
  assert.equal(row.fonte_recurso, 'FAPESP');
  assert.equal(row.prazo_envio, '2026-01-01');
  assert.equal(row._detailLookupSource, 'view');
});

test('lookupEditalForDetail encontra na tabela base (maybeSingle, 0 linhas não lança)', async () => {
  const sb = makeSupabase({
    'edital:id_edital=42:maybeSingle': () => ({
      data: { id_edital: 42, titulo: 'Base OK', extras: {} },
      error: null,
    }),
  });
  const r = await lookupEditalForDetail(sb, { routeParam: '42', isConfigured: true });
  assert.equal(r.edital?.titulo, 'Base OK');
  assert.equal(r.lookupMode, DETAIL_LOOKUP_MODE.BASE);
  assert.equal(r.lookupBaseFound, true);
  assert.equal(r.errorKind, null);
  assert.ok(sb.calls.some((c) => c.method === 'maybeSingle'));
  assert.ok(!sb.calls.some((c) => c.method === 'single'));
});

test('lookupEditalForDetail faz fallback na view quando base retorna null', async () => {
  const sb = makeSupabase({
    defaultMaybeSingle: () => ({ data: null, error: null }),
    'vw_editais_front:id_edital=77:maybeSingle': () => ({
      data: { id_edital: 77, titulo: 'View OK', extras: { a: 1 } },
      error: null,
    }),
  });
  const r = await lookupEditalForDetail(sb, {
    routeParam: '77',
    viewName: 'vw_editais_front',
    isConfigured: true,
  });
  assert.equal(r.edital?.titulo, 'View OK');
  assert.equal(r.lookupMode, DETAIL_LOOKUP_MODE.VIEW);
  assert.equal(r.lookupViewFound, true);
  assert.equal(r.lookupBaseFound, false);
});

test('lookupEditalForDetail retorna not_found quando base e view não encontram', async () => {
  const sb = makeSupabase({
    defaultMaybeSingle: () => ({ data: null, error: null }),
  });
  const r = await lookupEditalForDetail(sb, { routeParam: '999', isConfigured: true });
  assert.equal(r.edital, null);
  assert.equal(r.errorKind, DETAIL_ERROR_KIND.NOT_FOUND);
});

test('lookupEditalForDetail classifica erro Supabase', async () => {
  const sb = makeSupabase({
    defaultMaybeSingle: () => ({ data: null, error: { message: 'permission denied', code: '42501' } }),
  });
  const r = await lookupEditalForDetail(sb, { routeParam: '1', isConfigured: true });
  assert.equal(r.edital, null);
  assert.equal(r.errorKind, DETAIL_ERROR_KIND.SUPABASE);
});

test('lookupAnexosForDetail: falha de anexos não impede edital (retorno ok:false)', async () => {
  const sb = makeSupabase({
    'edital_anexo:id_edital=5:select': () => ({
      data: null,
      error: { message: 'RLS blocked', code: '42501' },
    }),
  });
  const r = await lookupAnexosForDetail(sb, '5', { isConfigured: true });
  assert.equal(r.ok, false);
  assert.deepEqual(r.data, []);
  assert.match(r.error.message, /RLS blocked/);
});

test('lookupAnexosForDetail: sucesso retorna lista', async () => {
  const sb = makeSupabase({
    'edital_anexo:id_edital=5:select': () => ({
      data: [{ id_anexo: 1, nome: 'pdf' }],
      error: null,
    }),
  });
  const r = await lookupAnexosForDetail(sb, '5', { isConfigured: true });
  assert.equal(r.ok, true);
  assert.equal(r.data.length, 1);
});

test('getEditalDetailErrorMessage diferencia not_found e rede/supabase', () => {
  assert.match(getEditalDetailErrorMessage(DETAIL_ERROR_KIND.NOT_FOUND), /catálogo atual/i);
  assert.match(getEditalDetailErrorMessage(DETAIL_ERROR_KIND.SUPABASE), /agora/i);
  assert.match(getEditalDetailErrorMessage(DETAIL_ERROR_KIND.NETWORK), /agora/i);
});

test('Promise.allSettled: edital ok + anexos rejeitados — edital carrega (simulação)', async () => {
  const editalSb = makeSupabase({
    'edital:id_edital=10:maybeSingle': () => ({
      data: { id_edital: 10, titulo: 'OK' },
      error: null,
    }),
  });
  const anexosSb = makeSupabase({
    'edital_anexo:id_edital=10:select': () => ({
      data: null,
      error: { message: 'anexo fail' },
    }),
  });

  const [editalResult, anexosResult] = await Promise.allSettled([
    lookupEditalForDetail(editalSb, { routeParam: '10', isConfigured: true }),
    lookupAnexosForDetail(anexosSb, '10', { isConfigured: true }),
  ]);

  assert.equal(editalResult.status, 'fulfilled');
  assert.equal(editalResult.value.edital?.titulo, 'OK');
  assert.equal(anexosResult.status, 'fulfilled');
  assert.equal(anexosResult.value.ok, false);
});

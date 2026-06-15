import assert from 'node:assert/strict';
import { describe, it, beforeEach, afterEach } from 'node:test';
import {
  PENDING_MANUAL_EDITAIS_KEY,
  savePendingManualEditalDraft,
  listPendingManualEditalDrafts,
  removePendingManualEditalDraft,
  clearPendingManualEditalDrafts,
} from './pendingManualEditalDrafts.js';
import { buildAdminPermissionDiagnostic } from './adminPermissionDiagnostic.js';
import {
  processManualEditalSaveError,
  buildManualEditalReportContext,
} from './handleManualEditalSaveError.js';
import { buildEditalWritePayload } from './buildEditalWritePayload.js';
import { SUPABASE_ERROR_KIND } from '../supabase/supabaseErrorClassifier.js';

const mockStorage = (() => {
  let store = {};
  return {
    getItem: (k) => (k in store ? store[k] : null),
    setItem: (k, v) => {
      store[k] = String(v);
    },
    removeItem: (k) => {
      delete store[k];
    },
    clear: () => {
      store = {};
    },
  };
})();

describe('pendingManualEditalDrafts', () => {
  beforeEach(() => {
    mockStorage.clear();
    globalThis.localStorage = mockStorage;
    clearPendingManualEditalDrafts();
  });

  afterEach(() => {
    clearPendingManualEditalDrafts();
    delete globalThis.localStorage;
  });

  it('savePendingManualEditalDraft salva rascunho com localId', () => {
    const id = savePendingManualEditalDraft(
      { titulo: 'Edital teste', link: 'https://example.com' },
      { errorKind: 'rls_policy', operation: 'insert' },
    );
    assert.ok(id);
    const list = listPendingManualEditalDrafts();
    assert.equal(list.length, 1);
    assert.equal(list[0].localId, id);
    assert.equal(list[0].payload.titulo, 'Edital teste');
    assert.equal(list[0].context.errorKind, 'rls_policy');
  });

  it('listPendingManualEditalDrafts lista rascunhos', () => {
    savePendingManualEditalDraft({ link: 'https://a' }, { errorKind: 'network' });
    savePendingManualEditalDraft({ link: 'https://b' }, { errorKind: 'schema' });
    assert.equal(listPendingManualEditalDrafts().length, 2);
  });

  it('removePendingManualEditalDraft remove', () => {
    const id = savePendingManualEditalDraft({ link: 'https://a' }, { errorKind: 'rls_policy' });
    removePendingManualEditalDraft(id);
    assert.equal(listPendingManualEditalDrafts().length, 0);
    assert.equal(mockStorage.getItem(PENDING_MANUAL_EDITAIS_KEY), '[]');
  });
});

describe('buildAdminPermissionDiagnostic', () => {
  it('frontendIsAdmin + rls_policy gera mensagem admin', () => {
    const result = buildAdminPermissionDiagnostic({
      user: { tipo: 'admin', nome_email: 'admin@test.com', id_usuario: 1 },
      frontendIsAdmin: true,
      operation: 'insert',
      error: { message: 'new row violates row-level security policy', code: '42501', status: 403 },
      errorKind: SUPABASE_ERROR_KIND.RLS_POLICY,
      isAuthenticated: true,
    });
    assert.equal(result.title, 'Permissão de administrador não reconhecida pelo banco');
    assert.equal(result.errorKind, SUPABASE_ERROR_KIND.RLS_POLICY);
    assert.equal(result.diagnostic.frontendIsAdmin, true);
    assert.equal(result.diagnostic.hasUserId, true);
  });
});

describe('processManualEditalSaveError / reporte', () => {
  beforeEach(() => {
    mockStorage.clear();
    globalThis.localStorage = mockStorage;
    clearPendingManualEditalDrafts();
  });

  afterEach(() => {
    clearPendingManualEditalDrafts();
    delete globalThis.localStorage;
  });

  it('submit com erro RLS salva rascunho local', () => {
    const { saveError, localDraftId } = processManualEditalSaveError({
      error: { message: 'new row violates row-level security policy', code: '42501', status: 403 },
      formPayload: { titulo: 'X', link: 'https://x' },
      user: { tipo: 'admin', id_usuario: 1 },
      authenticated: true,
      operation: 'insert',
    });
    assert.ok(localDraftId);
    assert.equal(listPendingManualEditalDrafts().length, 1);
    assert.equal(saveError.errorKind, SUPABASE_ERROR_KIND.RLS_POLICY);
  });

  it('metadata do reporte inclui operation/table/errorKind', () => {
    const { saveError } = processManualEditalSaveError({
      error: { message: 'permission denied', status: 403 },
      formPayload: { link: 'https://x' },
      user: { tipo: 'consultor' },
      authenticated: true,
      operation: 'insert',
    });
    const ctx = buildManualEditalReportContext(saveError);
    const meta = ctx.extraContext;
    assert.equal(meta.operation, 'insert');
    assert.equal(meta.table, 'edital');
    assert.equal(meta.errorKind, SUPABASE_ERROR_KIND.PERMISSION_DENIED);
    assert.equal(meta.componente, 'Cadastros');
    assert.equal(ctx.origem, 'manual_edital_create');
  });

  it('metadata do reporte não inclui token/key', () => {
    const { saveError } = processManualEditalSaveError({
      error: {
        message: 'access_token=leak refresh_token=bad service_role=secret',
        code: '42501',
        status: 403,
      },
      formPayload: { link: 'https://x', anon_key: 'should-strip' },
      user: { tipo: 'admin' },
      authenticated: true,
      operation: 'insert',
    });
    const blob = JSON.stringify(buildManualEditalReportContext(saveError)).toLowerCase();
    assert.equal(blob.includes('access_token'), false);
    assert.equal(blob.includes('refresh_token'), false);
    assert.equal(blob.includes('service_role'), false);
    assert.equal(blob.includes('anon_key'), false);
  });

  it('erro RLS não limpa payload do formulário (saveError retornado, modal permanece)', () => {
    const formPayload = { titulo: 'Preservado', link: 'https://keep.me', descricao: 'texto' };
    const { saveError } = processManualEditalSaveError({
      error: { message: 'violates row-level security policy' },
      formPayload,
      user: { tipo: 'admin' },
      authenticated: true,
      operation: 'insert',
    });
    assert.ok(saveError);
    assert.equal(saveError.operation, 'insert');
    const draft = listPendingManualEditalDrafts()[0];
    assert.equal(draft.payload.titulo, 'Preservado');
    assert.equal(draft.payload.link, 'https://keep.me');
  });
});

describe('buildEditalWritePayload — sanitização manual', () => {
  it('payload manual não contém organizacao_responsavel', () => {
    const payload = buildEditalWritePayload({
      link: 'https://a',
      organizacao_responsavel: 'Nunca enviar',
      orgao_responsavel: 'FINEP',
    });
    assert.equal('organizacao_responsavel' in payload, false);
    assert.equal(payload.orgao_responsavel, 'FINEP');
  });
});

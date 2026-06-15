import assert from 'node:assert/strict';
import { describe, it, beforeEach, afterEach } from 'node:test';
import {
  MANUAL_CADASTRO_FONTE_FALLBACK,
  CREATE_EDITAL_RETURN_COLUMNS,
  buildManualEditalOrFilter,
  filterManualCadastroEditais,
  isManualCadastroEdital,
  isCadastrosDebugEnabled,
  logCadastrosDebug,
  mergeCadastrosEditalRows,
  mergeManualCadastroExtras,
} from './manualCadastroEdital.js';
import { buildEditalWritePayload } from './buildEditalWritePayload.js';

const mockStorage = (() => {
  let store = {};
  return {
    getItem: (k) => (k in store ? store[k] : null),
    setItem: (k, v) => {
      store[k] = String(v);
    },
    clear: () => {
      store = {};
    },
  };
})();

describe('mergeManualCadastroExtras / buildEditalWritePayload manual', () => {
  it('adiciona extras.manual_entry para cadastro manual', () => {
    const payload = buildEditalWritePayload({ titulo: 'X', link: 'https://a' }, { manualCadastro: true });
    assert.equal(payload.extras.manual_entry, true);
    assert.equal(payload.extras.origem_cadastro, 'manual_admin');
    assert.equal(payload.extras.created_via, 'cadastros_page');
  });

  it('preserva extras existentes', () => {
    const payload = buildEditalWritePayload(
      {
        link: 'https://a',
        extras: { curadoria_front: { visibility: 'ok' }, origem_cadastro: 'legado' },
      },
      { manualCadastro: true },
    );
    assert.deepEqual(payload.extras.curadoria_front, { visibility: 'ok' });
    assert.equal(payload.extras.origem_cadastro, 'legado');
    assert.equal(payload.extras.manual_entry, true);
  });

  it('define fonte_recurso Cadastro Manual quando fonte vazia', () => {
    const payload = buildEditalWritePayload({ link: 'https://a', fonte_recurso: '' }, { manualCadastro: true });
    assert.equal(payload.fonte_recurso, MANUAL_CADASTRO_FONTE_FALLBACK);
  });

  it('mantém fonte informada pelo usuário', () => {
    const payload = buildEditalWritePayload(
      { link: 'https://a', fonte_recurso: 'Teste Manual' },
      { manualCadastro: true },
    );
    assert.equal(payload.fonte_recurso, 'Teste Manual');
  });

  it('payload manual não contém organizacao_responsavel', () => {
    const payload = buildEditalWritePayload(
      { link: 'https://a', organizacao_responsavel: 'X' },
      { manualCadastro: true },
    );
    assert.equal('organizacao_responsavel' in payload, false);
  });
});

describe('isManualCadastroEdital / listagem Cadastros', () => {
  it('reconhece extras.manual_entry = true', () => {
    assert.equal(isManualCadastroEdital({ extras: { manual_entry: true } }), true);
  });

  it('reconhece extras.origem_cadastro = manual_admin', () => {
    assert.equal(isManualCadastroEdital({ extras: { origem_cadastro: 'manual_admin' } }), true);
  });

  it('reconhece fonte_recurso Cadastro Manual', () => {
    assert.equal(isManualCadastroEdital({ fonte_recurso: MANUAL_CADASTRO_FONTE_FALLBACK }), true);
  });

  it('ignora edital de loader sem marcador', () => {
    assert.equal(isManualCadastroEdital({ fonte_recurso: 'FINEP', extras: {} }), false);
  });

  it('filterManualCadastroEditais filtra apenas manuais', () => {
    const rows = filterManualCadastroEditais([
      { id_edital: 1, fonte_recurso: 'FINEP' },
      { id_edital: 2, extras: { manual_entry: true } },
    ]);
    assert.equal(rows.length, 1);
    assert.equal(rows[0].id_edital, 2);
  });

  it('mergeCadastrosEditalRows mantém item recém-inserido após reload vazio', () => {
    const merged = mergeCadastrosEditalRows([], [{ id_edital: 99, titulo: 'Novo' }]);
    assert.equal(merged.length, 1);
    assert.equal(merged[0].id_edital, 99);
  });
});

describe('createEdital return columns', () => {
  it('CREATE_EDITAL_RETURN_COLUMNS inclui id_edital para insert+select', () => {
    assert.match(CREATE_EDITAL_RETURN_COLUMNS, /id_edital/);
    assert.match(CREATE_EDITAL_RETURN_COLUMNS, /extras/);
  });

  it('buildManualEditalOrFilter cobre marcadores manuais', () => {
    const f = buildManualEditalOrFilter();
    assert.match(f, /manual_entry/);
    assert.match(f, /manual_admin/);
    assert.match(f, /cadastros_page/);
    assert.match(f, /Cadastro Manual/);
  });
});

describe('logCadastrosDebug seguro', () => {
  beforeEach(() => {
    mockStorage.clear();
    globalThis.localStorage = mockStorage;
  });

  afterEach(() => {
    delete globalThis.localStorage;
  });

  it('só loga com flag localStorage', () => {
    assert.equal(isCadastrosDebugEnabled(), false);
    mockStorage.setItem('editalfinder:debug:cadastros', '1');
    assert.equal(isCadastrosDebugEnabled(), true);
  });

  it('não inclui tokens em payload de debug', () => {
    mockStorage.setItem('editalfinder:debug:cadastros', '1');
    const logs = [];
    const orig = console.info;
    console.info = (...args) => logs.push(args.join(' '));
    try {
      logCadastrosDebug('test', {
        access_token: 'secret-token',
        id_edital: 1,
      });
    } finally {
      console.info = orig;
    }
    const blob = logs.join(' ').toLowerCase();
    assert.equal(blob.includes('secret-token'), false);
    assert.match(blob, /id_edital/);
  });
});

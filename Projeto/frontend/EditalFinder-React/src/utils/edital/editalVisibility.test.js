import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  filterPublicVisibleEditais,
  getCuradoriaFront,
  isCuradoriaHidden,
  isHiddenDuplicateCuradoria,
} from './editalVisibility.js';

function edital(extras, extra = {}) {
  return {
    id: 1,
    titulo: 'Oportunidade teste',
    ativo: true,
    fonte_recurso: 'Grants.gov',
    ...extra,
    extras,
  };
}

describe('isCuradoriaHidden — duplicata defensiva (10.3C)', () => {
  it('true para visibility hidden_duplicate', () => {
    const e = edital({ curadoria_front: { visibility: 'hidden_duplicate' } });
    assert.equal(isCuradoriaHidden(e), true);
  });

  it('true para hidden_duplicate boolean', () => {
    const e = edital({
      curadoria_front: {
        hidden_duplicate: true,
        duplicate_of_id_edital: 10,
      },
    });
    assert.equal(isCuradoriaHidden(e), true);
  });

  it('true para ambos visibility e boolean', () => {
    const e = edital({
      curadoria_front: {
        hidden_duplicate: true,
        visibility: 'hidden_duplicate',
      },
    });
    assert.equal(isCuradoriaHidden(e), true);
  });

  it('true para hidden_duplicate string "true"', () => {
    const e = edital({ curadoria_front: { hidden_duplicate: 'true' } });
    assert.equal(isCuradoriaHidden(e), true);
  });

  it('false para visibility visible', () => {
    const e = edital({ curadoria_front: { visibility: 'visible' } });
    assert.equal(isCuradoriaHidden(e), false);
  });

  it('false para extras ausente', () => {
    assert.equal(isCuradoriaHidden({ titulo: 'x' }), false);
    assert.equal(isCuradoriaHidden(null), false);
  });

  it('false para extras inválido (array/string JSON inválido)', () => {
    assert.equal(isCuradoriaHidden({ extras: [] }), false);
    assert.equal(isCuradoriaHidden({ extras: '{not-json' }), false);
  });

  it('funciona com extras_raw', () => {
    const e = {
      extras_raw: {
        curadoria_front: { hidden_duplicate: true, visibility: 'hidden_duplicate' },
      },
    };
    assert.equal(isCuradoriaHidden(e), true);
    assert.equal(getCuradoriaFront(e).hidden_duplicate, true);
  });

  it('funciona com extras como string JSON', () => {
    const e = {
      extras: JSON.stringify({
        curadoria_front: { visibility: 'hidden_duplicate' },
      }),
    };
    assert.equal(isCuradoriaHidden(e), true);
  });
});

describe('isHiddenDuplicateCuradoria', () => {
  it('identifica duplicata por boolean ou visibility', () => {
    assert.equal(isHiddenDuplicateCuradoria({ hidden_duplicate: true }), true);
    assert.equal(isHiddenDuplicateCuradoria({ visibility: 'hidden_duplicate' }), true);
    assert.equal(isHiddenDuplicateCuradoria({ visibility: 'hidden_resultado' }), false);
  });
});

describe('filterPublicVisibleEditais', () => {
  it('remove duplicata por visibility', () => {
    const list = [
      edital({ curadoria_front: { visibility: 'hidden_duplicate' } }, { id: 1 }),
      edital({}, { id: 2, titulo: 'Canônico' }),
    ];
    const out = filterPublicVisibleEditais(list);
    assert.equal(out.length, 1);
    assert.equal(out[0].id, 2);
  });

  it('remove duplicata por boolean', () => {
    const list = [
      edital({ curadoria_front: { hidden_duplicate: true } }, { id: 1 }),
      edital({}, { id: 2 }),
    ];
    assert.equal(filterPublicVisibleEditais(list).length, 1);
  });

  it('preserva canônico visível', () => {
    const canon = edital(
      {},
      { id: 99, link: 'https://www.grants.gov/search-results-detail/500' },
    );
    const dup = edital(
      { curadoria_front: { hidden_duplicate: true, visibility: 'hidden_duplicate' } },
      { id: 100 },
    );
    const out = filterPublicVisibleEditais([dup, canon]);
    assert.equal(out.length, 1);
    assert.equal(out[0].id, 99);
  });
});

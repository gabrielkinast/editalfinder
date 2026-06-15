import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  buildEditalWritePayload,
  normalizeEditalFormInitialData,
} from './buildEditalWritePayload.js';

describe('buildEditalWritePayload', () => {
  it('remove campos inexistentes e join organizacao', () => {
    const payload = buildEditalWritePayload({
      titulo: 'Teste',
      link: 'https://example.com/edital',
      status: 'Ativo',
      organizacao: { nome: 'FINEP' },
      organizacao_responsavel: 'Não deve ir',
      id_edital: 99,
      campo_fantasma: 'x',
    });

    assert.equal(payload.titulo, 'Teste');
    assert.equal(payload.link, 'https://example.com/edital');
    assert.equal(payload.ativo, true);
    assert.equal('status' in payload, false);
    assert.equal('organizacao' in payload, false);
    assert.equal('organizacao_responsavel' in payload, false);
    assert.equal('id_edital' in payload, false);
    assert.equal('campo_fantasma' in payload, false);
  });

  it('omite id_organizacao vazio e aceita numérico', () => {
    assert.equal('id_organizacao' in buildEditalWritePayload({ link: 'https://a', id_organizacao: '' }), false);
    assert.equal(
      buildEditalWritePayload({ link: 'https://a', id_organizacao: '12' }).id_organizacao,
      12,
    );
  });

  it('persiste orgao_responsavel textual', () => {
    const payload = buildEditalWritePayload({
      link: 'https://a',
      orgao_responsavel: '  FINEP  ',
    });
    assert.equal(payload.orgao_responsavel, 'FINEP');
  });

  it('mapeia status Inativo para ativo=false', () => {
    const payload = buildEditalWritePayload({ link: 'https://a', status: 'Inativo' });
    assert.equal(payload.ativo, false);
  });
});

describe('normalizeEditalFormInitialData', () => {
  it('mapeia ativo e orgao_responsavel na edição', () => {
    const form = normalizeEditalFormInitialData({
      titulo: 'Edital X',
      ativo: false,
      orgao_responsavel: 'BNDES',
      id_organizacao: 3,
      data_publicacao: '2026-01-15T00:00:00Z',
    });
    assert.equal(form.status, 'Inativo');
    assert.equal(form.orgao_responsavel, 'BNDES');
    assert.equal(form.id_organizacao, 3);
    assert.equal(form.data_publicacao, '2026-01-15');
  });
});

/**
 * Testes da lógica de filtros Concursos (Node built-in runner).
 */
import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  applyConcursosFilters,
  buildConcursoSearchBlob,
  buildInstituicaoOrgaoBlob,
  filterByTab,
  getActiveFilterChips,
  getInitialConcursosFilters,
  inferTipoInstituicao,
} from './concursosFilters.js';

const sample = {
  titulo: 'Concurso Porto Alegre',
  orgao: 'Prefeitura',
  instituicao: 'Prefeitura POA',
  banca: 'Quadrix',
  fonte: 'quadrix',
  estado: 'RS',
  municipio: 'Porto Alegre',
  tipo_selecao: 'concurso_publico',
  status: 'inscricoes_abertas',
  validacao_status: 'valido',
  link_edital: 'https://example.com/ed.pdf',
  data_fim_inscricao: '2026-12-01',
  inscricoes_abertas: true,
  prova_proxima: false,
  salario_min: 5000,
  taxa_inscricao: 80,
  tags: ['quadrix', 'wave1'],
};

describe('concursosFilters', () => {
  it('filterByTab includes processo_seletivo in concursos publicos', () => {
    const rows = [
      { tipo_selecao: 'concurso_publico' },
      { tipo_selecao: 'processo_seletivo' },
      { tipo_selecao: 'vestibular' },
    ];
    const out = filterByTab(rows, 'concurso_publico');
    assert.equal(out.length, 2);
  });

  it('filterByTab includes programa_ingresso in vestibulares', () => {
    const rows = [{ tipo_selecao: 'programa_ingresso' }, { tipo_selecao: 'residencia' }];
    assert.equal(filterByTab(rows, 'vestibulares').length, 1);
  });

  it('search matches municipio and estado', () => {
    const blob = buildConcursoSearchBlob(sample);
    assert.ok(blob.includes('porto alegre'));
    assert.ok(blob.includes('rs'));
    const f = { ...getInitialConcursosFilters(), search: 'porto alegre' };
    assert.equal(applyConcursosFilters([sample], f).length, 1);
  });

  it('instituicaoOrgao filters orgao instituicao titulo', () => {
    assert.ok(buildInstituicaoOrgaoBlob(sample).includes('prefeitura'));
    const f = { ...getInitialConcursosFilters(), instituicaoOrgao: 'conselho' };
    const conselho = {
      titulo: 'CREFONO',
      orgao: 'Conselho Regional de Fonoaudiologia',
      instituicao: 'CREFONO-RJ',
    };
    assert.equal(applyConcursosFilters([conselho], f).length, 1);
    assert.equal(applyConcursosFilters([sample], f).length, 0);
  });

  it('inferTipoInstituicao heuristics', () => {
    assert.equal(
      inferTipoInstituicao({ orgao: 'Prefeitura Municipal de Campinas' }),
      'prefeitura'
    );
    assert.equal(
      inferTipoInstituicao({ instituicao: 'Universidade de São Paulo (USP)' }),
      'universidade'
    );
    assert.equal(
      inferTipoInstituicao({ titulo: 'Conselho Regional de Enfermagem' }),
      'conselho'
    );
  });

  it('tipoInstituicao filter', () => {
    const rows = [
      { orgao: 'Prefeitura de X' },
      { orgao: 'Universidade Federal do Rio Grande do Sul' },
    ];
    const f = { ...getInitialConcursosFilters(), tipoInstituicao: 'universidade' };
    assert.equal(applyConcursosFilters(rows, f).length, 1);
  });

  it('somenteValidos and comEdital', () => {
    const f = {
      ...getInitialConcursosFilters(),
      somenteValidos: true,
      comEdital: true,
    };
    assert.equal(applyConcursosFilters([sample], f).length, 1);
    assert.equal(
      applyConcursosFilters([{ ...sample, validacao_status: 'incompleto' }], f).length,
      0
    );
  });

  it('active chips use Instituição/órgão label', () => {
    const f = { ...getInitialConcursosFilters(), instituicaoOrgao: 'CESAMA' };
    const chips = getActiveFilterChips(f, 'all');
    const inst = chips.find((c) => c.key === 'instituicaoOrgao');
    assert.ok(inst);
    assert.equal(inst.label, 'Instituição/órgão');
    assert.equal(inst.display, 'CESAMA');
  });

  it('active chips include search and tab', () => {
    const f = { ...getInitialConcursosFilters(), search: 'usp' };
    const chips = getActiveFilterChips(f, 'vestibulares');
    assert.ok(chips.some((c) => c.key === 'search'));
    assert.ok(chips.some((c) => c.key === '__tab'));
  });
});

import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  getEditalStatusBadges,
  getPrimaryEditalStatusBadge,
  getEditalStatusFilterKeys,
  getEditalStatusSemantic,
  getEditalStatusLabel,
  editalMatchesSemanticStatusSelection,
  resolveDeadlineDate,
  resolveSemPrazoKind,
  isResultPublished,
  isPostResultCall,
  isPortalUseful,
} from './editalStatusBadges.js';
import { filterPublicVisibleEditais, isCuradoriaHidden } from './editalVisibility.js';

const NOW = new Date('2026-06-09T12:00:00');

function inDays(days, base = NOW) {
  const d = new Date(base);
  d.setHours(12, 0, 0, 0);
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

function kinds(edital) {
  return getEditalStatusBadges(edital, NOW).map((b) => b.kind);
}

describe('getEditalStatusBadges — prazos', () => {
  it('prazo em 40 dias => Aberto', () => {
    assert.deepEqual(kinds({ prazo_envio: inDays(40) }), ['open']);
  });

  it('prazo em 5 dias => Vencendo em 7 dias', () => {
    assert.deepEqual(kinds({ prazo_envio: inDays(5) }), ['due_7']);
  });

  it('prazo em 20 dias => Vencendo em 30 dias', () => {
    assert.deepEqual(kinds({ prazo_envio: inDays(20) }), ['due_30']);
  });

  it('prazo ontem => Encerrado', () => {
    assert.deepEqual(kinds({ prazo_envio: inDays(-1) }), ['closed']);
  });

  it('encerrado NÃO gera Ruído provável', () => {
    assert.ok(!kinds({ prazo_envio: inDays(-30) }).includes('noise'));
  });

  it('prazo_envio tem prioridade sobre fim_inscricao', () => {
    const date = resolveDeadlineDate({ prazo_envio: inDays(40), fim_inscricao: inDays(-5) });
    assert.equal(date.toISOString().slice(0, 10), inDays(40));
    assert.deepEqual(kinds({ prazo_envio: inDays(40), fim_inscricao: inDays(-5) }), ['open']);
  });
});

describe('getEditalStatusBadges — sem prazo', () => {
  it('sem prazo + oportunidade => Sem prazo informado', () => {
    assert.deepEqual(kinds({ titulo: 'Chamada de inovação' }), ['no_deadline']);
  });

  it('sem prazo NÃO gera Ruído provável', () => {
    assert.ok(!kinds({ titulo: 'Chamada' }).includes('noise'));
  });

  it('sem_prazo_kind deadline_in_pdf_or_detail => Prazo em PDF/detalhe', () => {
    assert.deepEqual(kinds({ extras: { sem_prazo_kind: 'deadline_in_pdf_or_detail' } }), [
      'deadline_in_detail',
    ]);
  });

  it('sem_prazo_kind deadline_tbd => Prazo a definir', () => {
    assert.deepEqual(kinds({ extras: { sem_prazo_kind: 'deadline_tbd' } }), ['deadline_tbd']);
  });

  it('sem_prazo_kind permanent_funding_line => Linha permanente', () => {
    assert.deepEqual(kinds({ extras: { sem_prazo_kind: 'permanent_funding_line' } }), [
      'permanent_line',
    ]);
  });
});

describe('getEditalStatusBadges — semântica', () => {
  it('actionability_type resultado => Resultado publicado', () => {
    assert.ok(kinds({ extras: { actionability_type: 'resultado' } }).includes('result_published'));
  });

  it('BNDES com Resultado Final divulgado => Chamada pós-resultado', () => {
    const e = {
      fonte: 'BNDES',
      titulo: 'Chamada X',
      descricao: 'Resultado Final divulgado da chamada.',
    };
    assert.ok(kinds(e).includes('post_result'));
  });

  it('BNDES pós-resultado não aparece como Aberto mesmo com prazo futuro', () => {
    const e = {
      fonte: 'BNDES',
      prazo_envio: inDays(40),
      descricao: 'processo de seleção concluído; classificação final divulgada.',
    };
    const ks = kinds(e);
    assert.ok(ks.includes('post_result'));
    // post_result tem prioridade sobre open
    assert.equal(ks[0], 'post_result');
  });

  it('portal útil => Portal útil', () => {
    assert.ok(kinds({ extras: { actionability_type: 'portal_util' } }).includes('portal_useful'));
  });

  it('is_noise true => Ruído provável', () => {
    assert.ok(kinds({ extras: { is_noise: true }, prazo_envio: inDays(10) }).includes('noise'));
  });
});

describe('robustez', () => {
  it('datas inválidas não quebram', () => {
    assert.doesNotThrow(() => getEditalStatusBadges({ prazo_envio: 'not-a-date' }, NOW));
    assert.deepEqual(kinds({ prazo_envio: 'not-a-date' }), ['no_deadline']);
  });

  it('extras ausente não quebra', () => {
    assert.doesNotThrow(() => getEditalStatusBadges({ titulo: 'X' }, NOW));
  });

  it('edital null/undefined retorna lista vazia', () => {
    assert.deepEqual(getEditalStatusBadges(null), []);
    assert.deepEqual(getEditalStatusBadges(undefined), []);
  });

  it('objeto vazio => Sem prazo informado (potencial oportunidade)', () => {
    assert.deepEqual(kinds({}), ['no_deadline']);
  });

  it('lê extras_raw (shape do mapper do front)', () => {
    assert.ok(kinds({ extras_raw: { sem_prazo_kind: 'deadline_tbd' } }).includes('deadline_tbd'));
  });
});

describe('helpers exportados', () => {
  it('resolveSemPrazoKind lê extras', () => {
    assert.equal(resolveSemPrazoKind({ extras: { sem_prazo_kind: 'deadline_tbd' } }), 'deadline_tbd');
    assert.equal(resolveSemPrazoKind({}), null);
  });

  it('isResultPublished detecta texto', () => {
    assert.ok(isResultPublished({ descricao: 'Resultado final publicado' }));
    assert.ok(!isResultPublished({ descricao: 'Chamada aberta' }));
  });

  it('isPostResultCall só para BNDES', () => {
    assert.ok(isPostResultCall({ fonte: 'BNDES', descricao: 'diligência em andamento' }));
    assert.ok(!isPostResultCall({ fonte: 'Grants.gov', descricao: 'diligência em andamento' }));
  });

  it('isPortalUseful', () => {
    assert.ok(isPortalUseful({ extras: { actionability_type: 'portal_util' } }));
    assert.ok(!isPortalUseful({}));
  });

  it('getPrimaryEditalStatusBadge retorna o de maior prioridade', () => {
    const primary = getPrimaryEditalStatusBadge({ extras: { is_noise: true }, prazo_envio: inDays(40) }, NOW);
    assert.equal(primary.kind, 'noise');
  });
});

describe('FRONTEND 1.2B — getEditalStatusFilterKeys / filtros', () => {
  it('retorna aberto', () => {
    assert.ok(getEditalStatusFilterKeys({ prazo_envio: inDays(40) }, NOW).includes('aberto'));
  });

  it('retorna vencendo_7', () => {
    assert.ok(getEditalStatusFilterKeys({ prazo_envio: inDays(5) }, NOW).includes('vencendo_7'));
  });

  it('retorna vencendo_30', () => {
    assert.ok(getEditalStatusFilterKeys({ prazo_envio: inDays(20) }, NOW).includes('vencendo_30'));
  });

  it('retorna encerrado', () => {
    assert.ok(getEditalStatusFilterKeys({ prazo_envio: inDays(-2) }, NOW).includes('encerrado'));
  });

  it('sem_prazo não vira ruido_provavel', () => {
    const keys = getEditalStatusFilterKeys({ titulo: 'Chamada' }, NOW);
    assert.ok(keys.includes('sem_prazo'));
    assert.ok(!keys.includes('ruido_provavel'));
  });

  it('BNDES pós-resultado não vira aberto', () => {
    const e = {
      fonte: 'BNDES',
      prazo_envio: inDays(40),
      descricao: 'processo de seleção concluído; classificação final divulgada.',
    };
    const keys = getEditalStatusFilterKeys(e, NOW);
    assert.ok(keys.includes('chamada_pos_resultado'));
    assert.ok(!keys.includes('aberto'));
    assert.equal(getEditalStatusSemantic(e, NOW), 'chamada_pos_resultado');
  });

  it('filtros status funcionam como OR', () => {
    const aberto = { prazo_envio: inDays(40) };
    const encerrado = { prazo_envio: inDays(-1) };
    const sel = { aberto: true, encerrado: true };
    assert.equal(editalMatchesSemanticStatusSelection(aberto, sel, NOW), true);
    assert.equal(editalMatchesSemanticStatusSelection(encerrado, sel, NOW), true);
    assert.equal(editalMatchesSemanticStatusSelection({ titulo: 'x' }, sel, NOW), false);
  });

  it('sem status selecionado não filtra', () => {
    assert.equal(editalMatchesSemanticStatusSelection({ titulo: 'x' }, {}, NOW), true);
    assert.equal(editalMatchesSemanticStatusSelection({ titulo: 'x' }, null, NOW), true);
  });

  it('combina com critério de fonte (AND manual)', () => {
    const e = { prazo_envio: inDays(40), fonte_recurso: 'FAPESP' };
    const passStatus = editalMatchesSemanticStatusSelection(e, { aberto: true }, NOW);
    const passFonte = String(e.fonte_recurso).includes('FAPESP');
    assert.equal(passStatus && passFonte, true);
    assert.equal(editalMatchesSemanticStatusSelection(e, { encerrado: true }, NOW), false);
  });

  it('duplicata oculta classificada mas removida da lista pública', () => {
    const dup = {
      prazo_envio: inDays(40),
      extras: { curadoria_front: { hidden_duplicate: true, visibility: 'hidden_duplicate' } },
    };
    assert.ok(getEditalStatusFilterKeys(dup, NOW).includes('duplicata_oculta'));
    assert.equal(isCuradoriaHidden(dup), true);
    assert.equal(editalMatchesSemanticStatusSelection(dup, { aberto: true }, NOW), true);
    assert.equal(filterPublicVisibleEditais([dup]).length, 0);
  });

  it('getEditalStatusLabel retorna texto curto', () => {
    assert.equal(getEditalStatusLabel({ prazo_envio: inDays(40) }, NOW), 'Aberto');
  });

  it('badges existentes continuam compatíveis', () => {
    const e = { extras: { is_noise: true }, prazo_envio: inDays(40) };
    assert.equal(getEditalStatusBadges(e, NOW)[0].kind, 'noise');
    assert.equal(getEditalStatusSemantic(e, NOW), 'ruido_provavel');
  });
});

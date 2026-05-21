import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { prefilterRadarCatalog, hasStrongStrategicSignals } from './radarCatalogPrefilter.js';

describe('prefilterRadarCatalog', () => {
  it('remove encerrado sem includeExpired', () => {
    const editais = [
      {
        id: '1',
        titulo: 'Chamada FINEP inovacao 2026',
        link: 'https://finep.gov.br/edital/1',
        prazo_envio: '2020-01-01',
        orgao: 'FINEP',
      },
      {
        id: '2',
        titulo: 'Programa bolsa CAPES',
        link: 'https://capes.gov.br/2',
        prazo_envio: '2027-06-01',
        orgao: 'CAPES',
      },
    ];
    const { items, stats } = prefilterRadarCatalog(editais, {});
    assert.equal(stats.removed_expired, 1);
    assert.equal(items.length, 1);
    assert.equal(items[0].id, '2');
  });

  it('mantém incompleto com sinal forte', () => {
    const e = {
      id: '3',
      titulo: 'Chamada publica CNPq pesquisa aplicada',
      descricao: 'x'.repeat(200),
      orgao: 'CNPq',
    };
    assert.equal(hasStrongStrategicSignals(e), true);
    const { items, stats } = prefilterRadarCatalog([e], {});
    assert.equal(stats.removed_missing_link, 0);
    assert.equal(items.length, 1);
  });

  it('deduplica por link', () => {
    const editais = [
      { id: 'a', titulo: 'Edital A', link: 'https://exemplo.org/edital-a', orgao: 'X' },
      { id: 'b', titulo: 'Edital A cópia', link: 'https://www.exemplo.org/edital-a/', orgao: 'X' },
    ];
    const { items, stats } = prefilterRadarCatalog(editais, {});
    assert.equal(stats.removed_duplicate, 1);
    assert.equal(items.length, 1);
  });
});

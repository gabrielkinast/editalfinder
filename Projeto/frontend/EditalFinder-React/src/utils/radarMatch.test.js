/**
 * Testes rápidos do motor do Radar (Node built-in runner).
 */
import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  calcularMatchRadar,
  toRadarCliente,
  toRadarOportunidade,
  isOportunidadeElegivelParaRadar,
  recomendarOportunidadesRadar,
  diasAtePrazo,
} from './radarMatch.js';

const clienteTech = {
  id_cliente: 1,
  nome_empresa: 'Acme TI',
  setor: 'tecnologia inovacao tic',
  area_inovacao: 'software ia',
  interesse_temas: 'inovacao tecnologia pesquisa',
  descricao_projeto: 'plataforma de dados',
  estado: 'rs',
  regiao: 'sul',
  porte_empresa: 'Média',
  nivel_maturidade: 'Validação',
  data_abertura: '2020-01-01',
  interesse_valor_min: 0,
  interesse_valor_max: 5_000_000,
  status: 'Ativo',
  regular_fiscal: true,
  regular_trabalhista: true,
  possui_certidao_negativa: true,
};

const clienteAgro = {
  ...clienteTech,
  id_cliente: 2,
  setor: 'agropecuaria',
  area_inovacao: 'cooperativa rural',
  interesse_temas: 'agricultura sustentável',
};

const clienteVazio = {
  id_cliente: 3,
  nome_empresa: 'Vazio SA',
  status: 'Ativo',
};

/** Formato próximo ao retorno de dataService.getEditais */
function opEdital(overrides) {
  const base = {
    id: 'manual-99',
    titulo: 'Chamada XYZ',
    descricao: 'programa tecnologia startups inovacao',
    orgao: 'FAKE',
    area: 'Tecnologia',
    estado: '',
    regiao: 'nacional',
    temas: 'ti software',
    dataLimite: new Date(Date.now() + 40 * 24 * 3600 * 1000).toISOString().slice(0, 10),
    linkOriginal: 'https://exemplo.gov.br/edital',
    tipoRecurso: 'Subvenção econômica',
    valorMinimo: 0,
    valorMaximo: 2_000_000,
    status: 'Ativo',
  };
  return { ...base, ...overrides };
}

describe('filtros eliminatórios', () => {
  const mappedOk = toRadarOportunidade(opEdital({}));
  assert.equal(isOportunidadeElegivelParaRadar(mappedOk, {}).ok, true);

  assert.equal(
    isOportunidadeElegivelParaRadar(toRadarOportunidade(opEdital({ titulo: 'FAQ institucional' })), {})
      .motivo,
    'titulo_ruidoso',
  );

  const mappedSemLink = toRadarOportunidade(opEdital({ linkOriginal: '' }));
  assert.equal(mappedSemLink.link, '');
  assert.equal(isOportunidadeElegivelParaRadar(mappedSemLink, {}).ok, false);
});

describe('dias até prazo', () => {
  it('datas passadas são negativas', () => {
    const futuro = diasAtePrazo(new Date(Date.now() + 5 * 24 * 3600 * 1000).toISOString());
    const passado = diasAtePrazo(new Date(Date.now() - 5 * 24 * 3600 * 1000).toISOString());
    assert.ok(futuro != null && futuro >= 4);
    assert.ok(passado != null && passado < 0);
  });
});

describe('calcularMatchRadar — granulação cliente × tema', () => {
  const agroHit = calcularMatchRadar(toRadarCliente(clienteAgro), toRadarOportunidade(opEdital()), {});
  const techHit = calcularMatchRadar(toRadarCliente(clienteTech), toRadarOportunidade(opEdital()), {});

  it('scores não são clones artificiais', () => {
    assert.ok(Math.abs((techHit.percentual || 0) - (agroHit.percentual || 0)) > 8);
  });

  it('afinidade mínima maior para cliente alinhado', () => {
    assert.ok(techHit.criterios.afinidade.pontos > agroHit.criterios.afinidade.pontos + 6);
  });
});

describe('recomendação e ranking', () => {
  it('lista ordenável por score (sem corte mínimo agressivo no teste)', () => {
    const opts = {
      limite: 10,
      scoreMinimoExibir: 0,
      cortePrincipal: 0,
      corteFallback: 0,
    };
    const lista = recomendarOportunidadesRadar(
      clienteTech,
      [
        opEdital({ id: 'a', titulo: 'A tecnologia', descricao: 'tecnologia inovacao tic' }),
        opEdital({ id: 'b', titulo: 'B outros', descricao: 'literatura filosofia arte' }),
      ],
      opts,
    );

    assert.ok(lista.length >= 2);
    assert.ok(lista[0].radar_score >= lista[1].radar_score);
  });
});

describe('cliente cadastro superficial', () => {
  it('tem score mais baixo e critérios com ausências', () => {
    const h = calcularMatchRadar(toRadarCliente(clienteVazio), toRadarOportunidade(opEdital({})), {});
    assert.ok(h.percentual < 72);
    assert.ok(Object.keys(h.criterios || {}).length > 3);
  });
});

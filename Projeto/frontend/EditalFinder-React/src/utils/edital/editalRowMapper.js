import { classificarEdital } from '../../services/classificationService';
import { getDisplayTitle } from '../displayTitle';
import { coerceStringArray } from './coerceArrays';
import { normalizeText } from './normalizeText';

function pickValorPrincipal(m) {
  const v =
    m.valor_estimado ?? m.valor_total ?? m.valor_maximo ?? m.valor_minimo ?? 0;
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

function inferAtivo(m) {
  if (m.ativo === false || m.ativo === 0) return false;
  if (m.ativo === true || m.ativo === 1) return true;
  const astr = String(m.ativo ?? '').trim().toLowerCase();
  if (astr === 'false' || astr === '0' || astr === 'n' || astr === 'no') return false;

  const st = normalizeText(String(m.situacao ?? m.status ?? ''));
  if (!st) return true;
  const inativos = new Set(
    [
      'inativo',
      'inactive',
      'cancelado',
      'cancelada',
      'desativado',
      'desativada',
    ].map((x) => normalizeText(x)),
  );
  if (inativos.has(st)) return false;

  return true;
}

/** Normaliza uma linha de vw_editais_front ou edital para o objeto usado na listagem dashboard. */
export function mapRawEditalRow(m) {
  const idEdital = m.id_edital ?? m.id;

  const tituloRaw = (m.titulo || '').trim();

  const rowForClass = {
    ...m,
    titulo: tituloRaw,
    temas: m.temas ?? m.area ?? '',
    fonte_recurso: m.fonte_recurso ?? m.fonte ?? '',
  };

  const classificacao = classificarEdital(rowForClass);

  const estado = String(m.uf ?? m.estado ?? '').trim();
  const prazo_envio_raw = m.prazo_envio ?? null;
  const dataLimite = prazo_envio_raw || m.fim_inscricao || null;

  const perfil_ideal_list = coerceStringArray(m.perfil_ideal);
  const setor_list = coerceStringArray(m.setor_estrategico);
  const atec_list = coerceStringArray(m.area_tecnologica);

  const valor_principal_num = pickValorPrincipal(m);

  return {
    id: `manual-${idEdital}`,
    idNumerico: Number(idEdital),
    isManual: true,

    titulo_original_raw: tituloRaw,
    titulo: getDisplayTitle({
      titulo: tituloRaw,
      link: m.link,
      descricao: m.descricao,
      objetivo: m.objetivo,
      temas: m.temas ?? m.area,
      fonte_recurso: m.fonte_recurso ?? m.fonte,
    }),

    descricao: m.descricao ?? null,
    objetivo: m.objetivo ?? null,

    orgao: (m.fonte_recurso || m.fonte || 'Manual').trim(),
    fonte_recurso_display: (m.fonte_recurso || m.fonte || '').trim(),
    fonte_raw: m.fonte ?? null,

    linkOriginal: m.link ?? null,
    link_raw: m.link ?? null,
    pdfUrl: m.pdf_url ?? null,
    pdf_url_raw: m.pdf_url ?? null,

    valor: valor_principal_num || 0,
    valorMaximo: m.valor_maximo ?? valor_principal_num,
    valorMinimo: m.valor_minimo ?? 0,
    valor_estimado_raw: m.valor_estimado,
    valor_total_raw: m.valor_total,
    valor_maximo_raw: m.valor_maximo,
    valor_principal_num,

    estado:
      estado ||
      (m.pais && !/^brasil|brazil|\bbr\b/i.test(String(m.pais))
        ? 'Internacional'
        : 'Nacional'),
    localidade:
      m.regiao ??
      (m.pais ? String(m.pais) : null) ??
      undefined,

    regiao: m.regiao ?? undefined,
    regiao_raw: m.regiao ?? null,
    uf_raw: m.uf ?? null,
    cidade_raw: m.cidade ?? null,
    pais_raw: m.pais ?? null,

    dataLimite,
    prazo_envio_raw,
    fim_inscricao_raw: m.fim_inscricao ?? null,
    data_publicacao_raw: m.data_publicacao ?? null,
    data_encerramento_raw: m.data_encerramento ?? null,

    tipoRecurso: classificacao.tipo,
    tipo_recurso: m.tipo_recurso ?? null,
    tipo_recurso_raw: m.tipo_recurso ?? null,
    tipo_oportunidade_raw: m.tipo_oportunidade ?? null,

    codigo_oportunidade_raw: m.codigo_oportunidade ?? null,
    numero_edital_raw: m.numero_edital ?? null,
    numero_chamada_raw: m.numero_chamada ?? null,

    area: (m.area ?? m.temas ?? classificacao.area?.join(', ') ?? '').trim() || '',
    area_cientifica_raw: m.area_cientifica ?? null,

    area_tecnologica_raw: atec_list,
    area_tecnologica_list: atec_list,
    area_tecnologica_flat: atec_list.join(' '),

    setor_estrategico_raw: setor_list,
    setor_estrategico_list: setor_list,
    setor_estrategico_flat: setor_list.join(' '),

    perfil_ideal_raw: perfil_ideal_list,
    publico_alvo_raw: m.publico_alvo ?? null,
    publico_alvo_arr_raw: coerceStringArray(m.publico_alvo_arr),

    setor_economico_raw: m.setor_economico ?? null,

    validacao_status_raw: m.validacao_status ?? null,
    validacao_status: m.validacao_status ?? null,
    qualidade_dado_raw: m.qualidade_dado != null ? Number(m.qualidade_dado) : null,
    qualidade_dado: m.qualidade_dado != null ? Number(m.qualidade_dado) : null,
    classificacao_confianca_raw: m.classificacao_confianca ?? null,

    ativo: inferAtivo(m),
    situacao_raw: m.situacao ?? null,
    /** Texto combinado apenas para diagnóstico — não usar .includes('inativ') nos filtros. */
    status_raw: m.status ?? m.situacao ?? null,

    /** PDF / documentos adicionais se existirem na view */
    documentos: m.documentos ?? m.documentos_anexo ?? null,

    criado_em_raw: m.criado_em ?? null,
    atualizado_em_raw: m.atualizado_em ?? null,
    moeda_raw: m.moeda ?? null,
    origem_portal_raw: m.origem_portal ?? null,
    idioma_original_raw: m.idioma_original ?? null,
    extras_raw: m.extras ?? null,

    reembolsavel:
      typeof m.reembolsavel === 'boolean' ? m.reembolsavel : undefined,
    natureza_recurso_raw: m.natureza_recurso ?? null,
    linha_credito_raw: m.linha_credito ?? null,
    modalidade_financiamento_raw: m.modalidade_financiamento ?? null,
    modalidade_financiamento: m.modalidade_financiamento ?? null,

    score: m.score ?? 0,
    scoreDetalhado: m.score_detalhado || {},
    justificativa: m.justificativa ?? null,
    compatibilidade: m.compatibilidade ?? null,
    recomendacao: m.recomendacao ?? null,
    linkInscricao: m.link_inscricao ?? null,
    regiao_legacy: m.regiao ?? null,
    situacao: m.situacao ?? null,
    status: m.status ?? null,

    elegibilidade: m.elegibilidade ?? null,
    contrapartida: m.contrapartida ?? null,
    ods: m.ods ?? null,
    contato: m.contato ?? null,

    tags: m.tags ?? null,

    temas: m.temas ?? null,
    temAnexos: !!(m.pdf_url),
  };
}

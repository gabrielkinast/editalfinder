import { dataService } from '../../services/dataService';
import { matchScientificItemToInterests } from './scientificInterestMatcher';
import { logScientificWorkspace } from './scientificWorkspaceLog';

function pickLink(row) {
  return (
    row?.link ||
    row?.link_original ||
    row?.linkOriginal ||
    row?.url ||
    row?.link_inscricao ||
    row?.site ||
    ''
  );
}

function pickDate(row) {
  return (
    row?.data_publicacao ||
    row?.publicado_em ||
    row?.created_at ||
    row?.data_limite ||
    row?.prazo_envio ||
    row?.atualizado_em ||
    null
  );
}

function normalizeRow(row, feedType) {
  const id = row?.id ?? row?.id_edital ?? row?.id_noticia ?? `${feedType}-${pickLink(row)}`;
  return {
    id: String(id),
    feedType,
    titulo: row?.titulo || row?.nome || row?.titulo_original_raw || 'Sem título',
    resumo: row?.resumo || row?.descricao || row?.sinopse || '',
    descricao: row?.descricao || '',
    fonte: row?.fonte || row?.fonte_recurso || row?.orgao || row?.instituicao || '',
    fonte_recurso: row?.fonte_recurso || '',
    link: pickLink(row),
    data: pickDate(row),
    tags: Array.isArray(row?.tags) ? row.tags : [],
    eixos: Array.isArray(row?.eixos) ? row.eixos : row?.eixos ? [row.eixos] : [],
    setores_estrategicos: row?.setores_estrategicos || row?.setor || '',
    area: row?.area || row?.area_inovacao || '',
    tipo_conteudo: row?.tipo_conteudo || row?.content_type || feedType,
    raw: row,
  };
}

/**
 * Carrega e classifica itens das fontes existentes (sem backend novo).
 * @param {string[]} activeInterests
 * @param {{ limit?: number }} [options]
 */
export async function loadScientificFeed(activeInterests = [], options = {}) {
  const limit = options.limit ?? 80;
  const results = [];

  const loaders = [
    { type: 'noticia', fn: () => dataService.getNoticias() },
    { type: 'pesquisa', fn: () => dataService.getPesquisas() },
    { type: 'edital', fn: () => dataService.getEditais() },
    {
      type: 'portal',
      fn: async () => {
        const [f, i] = await Promise.all([
          dataService.getPortaisFornecedoresFront().catch(() => []),
          dataService.getPortaisInvestimentosFront().catch(() => []),
        ]);
        return [...(f || []), ...(i || [])];
      },
    },
  ];

  const batches = await Promise.all(
    loaders.map(async ({ type, fn }) => {
      try {
        const rows = await fn();
        return (Array.isArray(rows) ? rows : []).map((r) => normalizeRow(r, type));
      } catch {
        return [];
      }
    }),
  );

  for (const batch of batches) {
    results.push(...batch);
  }

  const withMatch = results.map((item) => {
    const match = matchScientificItemToInterests(item, activeInterests);
    return {
      ...item,
      matchScore: match.score,
      matchedInterests: match.matchedInterests,
      matchReasons: match.reasons,
    };
  });

  const filtered =
    activeInterests.length > 0
      ? withMatch.filter((i) => i.matchScore > 0)
      : withMatch.slice(0, limit * 2);

  filtered.sort((a, b) => {
    if (b.matchScore !== a.matchScore) return b.matchScore - a.matchScore;
    const da = a.data ? new Date(a.data).getTime() : 0;
    const db = b.data ? new Date(b.data).getTime() : 0;
    return db - da;
  });

  const out = filtered.slice(0, limit);
  logScientificWorkspace('feed_loaded', {
    total_sources: results.length,
    matched: out.length,
    interests: activeInterests.length,
  });
  return out;
}

export const FEED_TYPE_LABEL = {
  noticia: 'Notícia',
  pesquisa: 'Pesquisa',
  edital: 'Edital',
  portal: 'Portal',
};

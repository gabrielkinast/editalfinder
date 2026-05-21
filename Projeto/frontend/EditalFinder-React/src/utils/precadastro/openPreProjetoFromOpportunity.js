import { logPrecadastro } from './precadastroLog';
import { openPreProjetoFromOpportunities } from './openPreProjetoFromOpportunities';

export const CONTEXT_PREFIX = 'precadastro_context_';

/**
 * Persiste contexto de oportunidade (edital/Radar) para o pré-projeto em Cadastros.
 * Integração futura: Workspace → Cadastros via esta função.
 *
 * @param {{
 *   cliente: { id_cliente?: number|string; nome_empresa?: string } | null;
 *   edital?: object | null;
 *   radarMatch?: object | null;
 *   initialDraft?: Record<string, unknown> | null;
 * }} params
 * @returns {{
 *   cliente: object | null;
 *   editalAssociado: object | null;
 *   radarMatch: object | null;
 *   initialDraft: Record<string, unknown> | null;
 *   editalFingerprint: string;
 *   contextStorageKey: string | null;
 * }}
 */
export function openPreProjetoFromOpportunity({
  cliente,
  edital = null,
  radarMatch = null,
  initialDraft = null,
}) {
  const ctx = openPreProjetoFromOpportunities({
    cliente,
    opportunities: edital || radarMatch ? [{ edital, radarMatch }] : [],
    source: 'single_opportunity',
  });
  return {
    cliente: ctx.cliente,
    editalAssociado: ctx.editalAssociado,
    radarMatch: ctx.radarMatch,
    initialDraft: initialDraft || ctx.initialEnvelope?.form || null,
    initialEnvelope: ctx.initialEnvelope,
    oportunidadesSelecionadas: ctx.oportunidadesSelecionadas,
    primaryOpportunity: ctx.primaryOpportunity,
    relatedOpportunities: ctx.relatedOpportunities,
    editalFingerprint: ctx.editalFingerprint,
    contextStorageKey: ctx.contextStorageKey,
  };
}

/**
 * Lê contexto salvo em sessionStorage (mesma chave usada em Cadastros.jsx).
 * @param {number|string} clienteId
 */
export function readPreProjetoContext(clienteId) {
  if (clienteId == null || typeof sessionStorage === 'undefined') {
    return { editalAssociado: null, radarMatch: null };
  }
  try {
    const raw = sessionStorage.getItem(`${CONTEXT_PREFIX}${clienteId}`);
    if (!raw) return { editalAssociado: null, radarMatch: null };
    const j = JSON.parse(raw);
    const titulo = j.titulo || j.titulo_edital || j.tituloEdital;
    const editalAssociado = titulo
      ? { titulo: String(titulo), id_edital: j.id_edital }
      : j.id_edital
        ? { id_edital: j.id_edital }
        : null;
    const radarMatch =
      titulo || typeof j.scorePct === 'number'
        ? {
            tituloEdital: titulo ? String(titulo) : undefined,
            scorePct: typeof j.scorePct === 'number' ? j.scorePct : undefined,
            idEdital: j.id_edital,
          }
        : null;
    return { editalAssociado, radarMatch };
  } catch {
    return { editalAssociado: null, radarMatch: null };
  }
}

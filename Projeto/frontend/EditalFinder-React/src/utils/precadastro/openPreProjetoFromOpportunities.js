import {
  buildInitialPrecadastroState,
  fingerprintPrecadContext,
  loadPrecadEnvelope,
  migratePrecadForm,
} from '../precadastroProjetoInitialState';
import { buildPreCadastroDraft } from './buildPreCadastroDraft';
import { logPrecadastro } from './precadastroLog';
import {
  normalizeSelectedOpportunity,
  pickPrimaryOpportunity,
  relatedOpportunities,
} from '../consultor/opportunitySelection';
const CONTEXT_PREFIX = 'precadastro_context_';

/**
 * @typedef {object} PreProjetoMultiContext
 * @property {object|null} cliente
 * @property {object|null} editalAssociado — principal
 * @property {object|null} radarMatch — principal
 * @property {object|null} primaryOpportunity
 * @property {object[]} relatedOpportunities
 * @property {object[]} oportunidadesSelecionadas — normalizadas
 * @property {object} initialEnvelope — { form, fieldIntel }
 * @property {string} editalFingerprint
 * @property {string|null} contextStorageKey
 * @property {string} source
 */

/**
 * Gera contexto e rascunho inicial a partir de uma ou várias oportunidades.
 *
 * @param {{
 *   cliente: object;
 *   opportunities: Array<object|{ edital?: object; radarMatch?: object; row?: object }>;
 *   primaryOpportunityId?: string;
 *   source?: string;
 * }} params
 * @returns {PreProjetoMultiContext}
 */
export function openPreProjetoFromOpportunities({
  cliente,
  opportunities = [],
  primaryOpportunityId,
  source = 'workspace_consultor',
}) {
  const clienteId = cliente?.id_cliente ?? cliente?.id;
  if (!cliente) {
    const err = new Error('Cliente obrigatório para iniciar pré-projeto.');
    logPrecadastro('open_multi_error', { message: err.message, source });
    throw err;
  }

  const normalized = (opportunities || []).map((item) => {
    if (item?.row) return normalizeSelectedOpportunity(item.row);
    if (item?.edital || item?.radarMatch) {
      return normalizeSelectedOpportunity({
        edital: item.edital,
        score: item.radarMatch?.scorePct,
        scorePct: item.radarMatch?.scorePct,
        compatibilidade: item.radarMatch?.compatibilidade,
        razoes: item.radarMatch?.razoes,
        razoesPositivas: item.radarMatch?.razoesPositivas,
        matchLinha: item.radarMatch?.matchLinha,
      });
    }
    return normalizeSelectedOpportunity(item);
  });

  if (normalized.length === 0) {
    const err = new Error('Selecione pelo menos uma oportunidade.');
    logPrecadastro('open_multi_error', { message: err.message, source });
    throw err;
  }

  const primary = pickPrimaryOpportunity(normalized, primaryOpportunityId);
  const related = relatedOpportunities(normalized, primary);
  const editalAssociado = primary.edital;
  const radarMatch = primary.radarMatch;

  const editalFingerprint = fingerprintPrecadContext(editalAssociado, '', radarMatch);
  let contextStorageKey = null;

  if (clienteId != null && typeof sessionStorage !== 'undefined') {
    contextStorageKey = `${CONTEXT_PREFIX}${clienteId}`;
    try {
      sessionStorage.setItem(
        contextStorageKey,
        JSON.stringify({
          titulo: primary.titulo,
          tituloEdital: primary.titulo,
          scorePct: primary.scorePct,
          id_edital: primary.edital?.id_edital ?? primary.edital?.id,
          opportunitiesCount: normalized.length,
          primaryOpportunityKey: primary.key,
          opportunityKeys: normalized.map((o) => o.key),
          source,
          savedAt: new Date().toISOString(),
        }),
      );
    } catch (e) {
      logPrecadastro('open_multi_context_error', { message: e?.message });
    }
  }

  const base = buildInitialPrecadastroState(cliente, { edital: editalAssociado, radarMatch });
  const env = loadPrecadEnvelope(clienteId, base, editalFingerprint);
  const draftOut = buildPreCadastroDraft({
    cliente,
    edital: editalAssociado,
    radarMatch,
    oportunidadesSelecionadas: normalized,
    oportunidadePrincipal: primary,
    oportunidadesRelacionadas: related,
    existingForm: env.form,
    existingFieldIntel: env.fieldIntel,
    options: {},
  });

  logPrecadastro('open_multi_draft_built', {
    id_cliente: clienteId,
    count: normalized.length,
    primary_key: primary.key,
    source,
  });

  return {
    cliente,
    editalAssociado,
    radarMatch,
    primaryOpportunity: primary,
    relatedOpportunities: related,
    oportunidadesSelecionadas: normalized,
    initialEnvelope: {
      form: migratePrecadForm(draftOut.mergedForm),
      fieldIntel: draftOut.mergedFieldIntel,
    },
    editalFingerprint,
    contextStorageKey,
    source,
  };
}

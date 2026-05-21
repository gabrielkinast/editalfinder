import {
  buildInitialPrecadastroState,
  fingerprintPrecadContext,
  loadPrecadEnvelope,
  storageKeyPrecadDraft,
} from '../precadastroProjetoInitialState';
import { calculatePreCadastroCompleteness } from './calculatePreCadastroCompleteness';
import { readPreProjetoContext } from './openPreProjetoFromOpportunity';

const EMPTY = {
  hadDraft: false,
  status: 'rascunho',
  score: 0,
  pendenciesCount: 0,
  consultivePendencies: [],
  editalFingerprint: 'geral',
};

/**
 * Resumo do rascunho local de pré-projeto (sem alterar localStorage).
 * @param {object|null} cliente
 * @param {{ editalFingerprint?: string; useSessionContext?: boolean }} [options]
 */
export function getClientPrecadSummary(cliente, options = {}) {
  const id = cliente?.id_cliente ?? cliente?.id;
  if (id == null) return { ...EMPTY };

  let fp = options.editalFingerprint ?? 'geral';
  if (!options.editalFingerprint && options.useSessionContext !== false) {
    const ctx = readPreProjetoContext(id);
    fp = fingerprintPrecadContext(ctx.editalAssociado, '', ctx.radarMatch);
  }

  try {
    const initial = buildInitialPrecadastroState(cliente, {});
    const env = loadPrecadEnvelope(id, initial, fp);
    const comp = calculatePreCadastroCompleteness(env.form);
    return {
      hadDraft: env.hadStoredDraft,
      status: env.form?.bloco_estr_status_precadastro || 'rascunho',
      score: comp.score,
      pendenciesCount:
        (comp.requiredMissing?.length || 0) + (comp.consultivePendencies?.length || 0),
      consultivePendencies: comp.consultivePendencies || [],
      editalFingerprint: fp,
      storageKey: storageKeyPrecadDraft(id, fp),
      ultimaEdicao: env.draftMeta?.ultimaEdicaoManualEm ?? null,
    };
  } catch {
    return { ...EMPTY, editalFingerprint: fp };
  }
}

/** Label de status para UI do Workspace. */
export function precadStatusLabel(summary) {
  if (!summary?.hadDraft) return { label: 'Sem rascunho', tone: 'none' };
  const s = String(summary.status || 'rascunho').toLowerCase();
  if (s === 'pronto') return { label: 'Pronto para exportar', tone: 'ready' };
  if (s === 'revisao') return { label: 'Em revisão', tone: 'wip' };
  return { label: 'Rascunho', tone: 'draft' };
}

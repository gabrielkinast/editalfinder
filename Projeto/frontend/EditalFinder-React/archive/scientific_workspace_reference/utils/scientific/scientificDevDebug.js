import { deduplicateProjectIdeas } from './deduplicateProjectIdeas';

const MAPPED_BUTTONS = 28;

/**
 * Tabela de debug no console (somente DEV). Nunca lança.
 */
export function logScientificWorkspaceDebugTable({
  notebookCount = 0,
  notebookDeduped = 0,
  ideasCount = 0,
  ideasDeduped = 0,
}) {
  if (!import.meta.env.DEV) return;

  try {
    console.table([
      { métrica: 'Botões mapeados (checklist)', valor: MAPPED_BUTTONS },
      { métrica: 'Itens no caderno', valor: notebookCount },
      { métrica: 'Duplicatas removidas (caderno)', valor: notebookDeduped },
      { métrica: 'Ideias exibíveis', valor: ideasCount },
      { métrica: 'Duplicatas removidas (ideias)', valor: ideasDeduped },
    ]);
  } catch {
    /* console.table não deve quebrar a UI */
  }
}

export function countIdeasDedup(rawIdeas) {
  try {
    const list = Array.isArray(rawIdeas) ? rawIdeas : [];
    const deduped = deduplicateProjectIdeas(list);
    return {
      before: list.length,
      after: deduped.length,
      removed: Math.max(0, list.length - deduped.length),
    };
  } catch {
    return { before: 0, after: 0, removed: 0 };
  }
}

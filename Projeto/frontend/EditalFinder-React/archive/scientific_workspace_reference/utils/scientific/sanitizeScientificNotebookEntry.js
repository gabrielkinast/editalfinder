import { cleanScientificTitle } from './cleanScientificTitle';
import { logScientificWorkspace } from './scientificWorkspaceLog';

const OMIT_IF_EMPTY_ARRAY = new Set([
  'conceitos',
  'projetos',
  'perguntas',
  'routeSteps',
  'nextSteps',
  'disciplines',
  'tools',
  'interesses',
]);

/**
 * Remove undefined/null e strings vazias desnecessárias antes de persistir.
 * @param {object} entry
 */
export function sanitizeScientificNotebookEntry(entry = {}) {
  const rawTitle = entry.titulo ?? entry.title ?? '';
  const titulo = cleanScientificTitle(rawTitle, { logContext: 'notebook_save' }) || 'Sem título';
  const hadTitleFix = String(rawTitle).trim() !== titulo;

  const out = {
    ...entry,
    titulo,
    title: titulo,
  };

  if (out.resumo != null) {
    const r = String(out.resumo).trim();
    out.resumo = r || undefined;
  }
  if (out.notes != null) {
    const n = String(out.notes).trim();
    out.notes = n;
  }
  if (out.fonte != null) {
    const f = String(out.fonte).trim();
    out.fonte = f || undefined;
  }
  if (out.link != null) {
    const l = String(out.link).trim();
    out.link = l || undefined;
  }
  if (out.expectedOutput != null) {
    const e = String(out.expectedOutput).trim();
    out.expectedOutput = e || undefined;
  }

  for (const key of Object.keys(out)) {
    if (out[key] === undefined || out[key] === null) {
      delete out[key];
      continue;
    }
    if (OMIT_IF_EMPTY_ARRAY.has(key) && Array.isArray(out[key]) && out[key].length === 0) {
      delete out[key];
    }
  }

  if (hadTitleFix || String(rawTitle).includes('Aprofundar: Aprofundar')) {
    logScientificWorkspace('notebook_save_sanitized', {
      id: out.id,
      tipo: out.tipo,
      titleFixed: hadTitleFix,
    });
  }

  return out;
}

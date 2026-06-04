import {
  buildPowerIdeaProgressKey,
  buildRouteStepProgressKey,
  buildStudyProgressKey,
} from './scientificStudyProgressKeys';
import {
  DEFAULT_STUDY_PROGRESS_STATUS,
  STUDY_PROGRESS_STATUS_LABELS,
} from './scientificStudyProgressConstants';
import { getProgressStatusFromMap } from './scientificStudyProgressStorage';
import { logScientificWorkspace } from './scientificWorkspaceLog';

/**
 * Lista itens rastreáveis de um bloco de trilha.
 * @param {object} block
 * @returns {Array<{ progressKey: string, label: string, kind: string }>}
 */
export function collectBlockProgressItems(block) {
  const canonicalKey = block.canonicalKey || block.interestId || 'geral';
  const items = [];
  const deep = block.deep;

  if (deep?.theory) {
    for (const [layer, topics] of Object.entries(deep.theory)) {
      for (const topic of topics || []) {
        items.push({
          progressKey: buildStudyProgressKey(canonicalKey, 'theory', layer, topic),
          label: topic,
          kind: 'theory',
        });
      }
    }
  } else {
    for (const topic of block.fundamentals || []) {
      items.push({
        progressKey: buildStudyProgressKey(canonicalKey, 'theory', 'foundations', topic),
        label: topic,
        kind: 'theory',
      });
    }
    for (const topic of block.intermediate || []) {
      items.push({
        progressKey: buildStudyProgressKey(canonicalKey, 'theory', 'intermediate', topic),
        label: topic,
        kind: 'theory',
      });
    }
  }

  if (deep?.books) {
    for (const [level, lines] of Object.entries(deep.books)) {
      for (const line of lines || []) {
        items.push({
          progressKey: buildStudyProgressKey(canonicalKey, 'book', level, line),
          label: line,
          kind: 'book',
        });
      }
    }
  }

  if (deep?.bookEntries?.length) {
    for (const book of deep.bookEntries) {
      const label = book.author ? `${book.author} — ${book.title}` : book.title;
      items.push({
        progressKey: buildStudyProgressKey(canonicalKey, 'book', book.level || 'book', label),
        label,
        kind: 'book',
      });
    }
  }

  if (deep?.projectTracks) {
    for (const [track, topics] of Object.entries(deep.projectTracks)) {
      for (const topic of topics || []) {
        items.push({
          progressKey: buildStudyProgressKey(canonicalKey, 'project', track, topic),
          label: topic,
          kind: 'project',
        });
      }
    }
  }

  const questions = deep?.professorQuestions || block.professorQuestions || [];
  for (const q of questions) {
    items.push({
      progressKey: buildStudyProgressKey(canonicalKey, 'question', 'question', q),
      label: q,
      kind: 'question',
    });
  }

  const powerIdeas = block.powerIdeas || deep?.powerIdeas || [];
  for (const idea of powerIdeas) {
    items.push({
      progressKey: buildPowerIdeaProgressKey(canonicalKey, idea),
      label: idea.title,
      kind: 'powerIdea',
    });
  }

  return items;
}

function tallyStatuses(items, progressMap) {
  const counts = {
    total: items.length,
    marked: 0,
    a_estudar: 0,
    estudando: 0,
    dominado: 0,
    ignorar_agora: 0,
  };

  for (const item of items) {
    const status = getProgressStatusFromMap(progressMap, item.progressKey);
    if (progressMap[item.progressKey]) counts.marked += 1;
    if (status === 'a_estudar') counts.a_estudar += 1;
    else if (status === 'estudando') counts.estudando += 1;
    else if (status === 'dominado') counts.dominado += 1;
    else if (status === 'ignorar_agora') counts.ignorar_agora += 1;
  }

  return counts;
}

/**
 * @param {object} block
 * @param {Record<string, object>} progressMap
 */
export function buildTrailProgressSummary(block, progressMap = {}) {
  const items = collectBlockProgressItems(block);
  const counts = tallyStatuses(items, progressMap);
  const pct = counts.total ? Math.round((counts.marked / counts.total) * 100) : 0;

  const summary = {
    ...counts,
    percentMarked: pct,
    label: block.label,
    canonicalKey: block.canonicalKey || block.interestId,
    line:
      counts.total === 0
        ? ''
        : `Progresso: ${counts.marked} de ${counts.total} tópicos marcados · ${counts.dominado} dominado${counts.dominado !== 1 ? 's' : ''}`,
    detailLine:
      counts.estudando || counts.dominado
        ? `${counts.estudando} estudando · ${counts.dominado} dominado${counts.dominado !== 1 ? 's' : ''}`
        : '',
  };

  return summary;
}

/**
 * @param {Array<object>} blocks
 * @param {Record<string, object>} progressMap
 * @param {Array<object>} [goalRoutes]
 */
export function buildGlobalStudyProgressSummary(blocks = [], progressMap = {}, goalRoutes = []) {
  const allItems = [];
  for (const block of blocks) {
    allItems.push(...collectBlockProgressItems(block));
  }
  for (const route of goalRoutes) {
    for (const step of route.steps || []) {
      allItems.push({
        progressKey: buildRouteStepProgressKey(route.id, step),
        label: step,
        kind: 'route_step',
      });
    }
  }

  const counts = tallyStatuses(allItems, progressMap);
  const projectsInProgress = allItems.filter(
    (i) =>
      i.kind === 'project' &&
      getProgressStatusFromMap(progressMap, i.progressKey) === 'estudando',
  ).length;

  const summary = {
    ...counts,
    projectsInProgress,
    items: allItems,
  };

  if (import.meta.env.DEV) {
    logScientificWorkspace('study_progress_summary_generated', {
      total: counts.total,
      estudando: counts.estudando,
      dominado: counts.dominado,
    });
  }

  return summary;
}

/**
 * @param {string} status
 * @param {string} filterId
 */
export function matchesStudyProgressFilter(status, filterId) {
  if (!filterId) return true;
  const s = status || DEFAULT_STUDY_PROGRESS_STATUS;
  return s === filterId;
}

export function studyProgressStatusLabel(status) {
  return STUDY_PROGRESS_STATUS_LABELS[status] || STUDY_PROGRESS_STATUS_LABELS.a_estudar;
}

/**
 * Anexa status ao item do caderno (compatível com itens antigos).
 * @param {object} entry
 * @param {string} [status]
 */
export function withStudyProgressOnNotebookEntry(entry, status) {
  if (!entry || !status || status === DEFAULT_STUDY_PROGRESS_STATUS) return entry;
  const label = studyProgressStatusLabel(status);
  const resumoBase = entry.resumo ? String(entry.resumo) : '';
  const hasStatus = resumoBase.toLowerCase().includes('status:');
  return {
    ...entry,
    studyProgressStatus: status,
    resumo: hasStatus ? resumoBase : [resumoBase, `status: ${label}`].filter(Boolean).join(' · '),
  };
}

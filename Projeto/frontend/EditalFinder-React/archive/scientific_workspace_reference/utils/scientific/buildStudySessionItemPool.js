import { collectBlockProgressItems } from './buildStudyProgressSummary';
import {
  buildStudyProgressKey,
  buildPowerIdeaProgressKey,
  buildRouteStepProgressKey,
  slugifyStudyProgressLabel,
} from './scientificStudyProgressKeys';
import { getProgressStatusFromMap } from './scientificStudyProgressStorage';
import { getBooksForArea } from './scientificBookCatalog';
import { buildBookProgressKey, BOOK_READ_STATUSES } from './scientificBookProgressStorage';
import { resolveCanonicalInterest } from './scientificInterestAliases';
import { interestLabelById } from './scientificInterestsConfig';
import { getPowerIdeasForArea } from './getPowerIdeasForArea';
import {
  POWER_IDEA_LEVEL_LABELS,
  POWER_IDEA_TYPE_LABELS,
} from './scientificPowerIdeasHelpers';
import { getScientificNotebookEntryKey } from './getScientificNotebookEntryKey';
import { dedupeStudySessionItems } from './dedupeStudySessionItems';
import { logScientificWorkspace } from './scientificWorkspaceLog';

const SEGMENT_LEVEL_LABEL = {
  foundations: 'Fundamentos',
  intermediate: 'Intermediário',
  advanced: 'Avançado',
  researchLevel: 'Pesquisa/Mestrado',
  basic: 'Básico',
  ictcc: 'IC/TCC',
  masters: 'Mestrado',
  introductory: 'Graduação',
  computational: 'Computacional',
  referencia: 'Referência',
};

const TRACK_SEGMENT = {
  basic: 'basic',
  intermediate: 'intermediate',
  advanced: 'advanced',
  ictcc: 'ictcc',
  masters: 'masters',
};

function normalizeKind(kind) {
  if (kind === 'question') return 'professorQuestion';
  if (kind === 'route_step') return 'goalRouteStep';
  return kind;
}

function resolveStatus(progressState, progressKey) {
  if (!progressKey) return 'none';
  const st = getProgressStatusFromMap(progressState, progressKey);
  return progressState[progressKey] ? st : 'none';
}

function levelLabel(segment, level, kind) {
  if (level && POWER_IDEA_LEVEL_LABELS[level]) return POWER_IDEA_LEVEL_LABELS[level];
  if (SEGMENT_LEVEL_LABEL[segment]) return SEGMENT_LEVEL_LABEL[segment];
  if (kind === 'book' && level) return SEGMENT_LEVEL_LABEL[level] || level;
  return level || segment || '';
}

function parseSegmentFromProgressKey(progressKey) {
  const parts = String(progressKey || '').split('::');
  return parts[2] || '';
}

function makeSearchableText(parts) {
  return parts.filter(Boolean).join(' ').toLowerCase();
}

function createPoolItem({
  progressKey,
  canonicalKey,
  areaLabel,
  kind,
  source,
  title,
  subtitle = '',
  level = '',
  segment = '',
  status,
  priority = 50,
  metadata = {},
}) {
  const nk = normalizeKind(kind);
  const id = progressKey || `${canonicalKey}::${nk}::${slugifyStudyProgressLabel(title)}`;
  return {
    id,
    progressKey: progressKey || id,
    canonicalKey,
    areaLabel,
    kind: nk,
    source,
    title,
    subtitle,
    level: level || levelLabel(segment, '', nk),
    segment,
    status: status || 'none',
    priority,
    searchableText: makeSearchableText([title, subtitle, areaLabel, nk, segment, level, metadata.ideaType]),
    metadata,
  };
}

function addFromCollect(pool, block, progressState, bookProgress) {
  const canonicalKey = block.canonicalKey || block.interestId || 'geral';
  const areaLabel = block.label || interestLabelById(canonicalKey) || canonicalKey;

  for (const raw of collectBlockProgressItems(block)) {
    const kind = normalizeKind(raw.kind);
    const segment = parseSegmentFromProgressKey(raw.progressKey);
    let subtitle = '';
    const bp = bookProgress[raw.progressKey];
    if (kind === 'book' && bp) {
      const stLabel = BOOK_READ_STATUSES.find((s) => s.id === bp.status)?.label || bp.status;
      subtitle = `${stLabel}${bp.progressPercent != null ? ` ${bp.progressPercent}%` : ''}`;
    }

    pool.push(
      createPoolItem({
        progressKey: raw.progressKey,
        canonicalKey,
        areaLabel,
        kind,
        source: 'deepStudyCatalog',
        title: raw.label,
        subtitle,
        level: levelLabel(segment, '', kind),
        segment,
        status: resolveStatus(progressState, raw.progressKey),
        priority: 45,
        metadata: { sources: ['deepStudyCatalog'], bookProgressPercent: bp?.progressPercent },
      }),
    );
  }
}

function addBooksFromCatalog(pool, canonicalKey, areaLabel, progressState, bookProgress) {
  for (const book of getBooksForArea(canonicalKey)) {
    const progressKey = buildBookProgressKey(book, canonicalKey);
    const label = book.author ? `${book.author} — ${book.title}` : book.title;
    const bp = bookProgress[progressKey];
    let subtitle = book.useFor || '';
    if (bp) {
      const stLabel = BOOK_READ_STATUSES.find((s) => s.id === bp.status)?.label || bp.status;
      subtitle = `${stLabel}${bp.progressPercent != null ? ` · ${bp.progressPercent}%` : ''}`;
    }
    pool.push(
      createPoolItem({
        progressKey,
        canonicalKey,
        areaLabel,
        kind: 'book',
        source: 'bookCatalog',
        title: label,
        subtitle,
        level: levelLabel(book.level, book.level, 'book'),
        segment: book.level || 'book',
        status: resolveStatus(progressState, progressKey),
        priority: bp?.status === 'lendo' ? 35 : 48,
        metadata: { sources: ['bookCatalog'], bookProgressPercent: bp?.progressPercent },
      }),
    );
  }
}

function addPowerIdeasExtras(pool, canonicalKey, areaLabel, progressState) {
  for (const idea of getPowerIdeasForArea(canonicalKey)) {
    const ideaKey = buildPowerIdeaProgressKey(canonicalKey, idea);
    const typeLabel = POWER_IDEA_TYPE_LABELS[idea.type] || idea.type;
    const lvl = POWER_IDEA_LEVEL_LABELS[idea.level] || idea.level;

    pool.push(
      createPoolItem({
        progressKey: ideaKey,
        canonicalKey,
        areaLabel,
        kind: 'powerIdea',
        source: 'powerIdeasCatalog',
        title: idea.title,
        subtitle: idea.whyItMatters || '',
        level: lvl,
        segment: idea.level || 'general',
        status: resolveStatus(progressState, ideaKey),
        priority: 42,
        metadata: {
          sources: ['powerIdeasCatalog'],
          ideaType: typeLabel,
          ideaId: idea.id,
        },
      }),
    );

    for (const q of idea.professorQuestions || []) {
      const qKey = buildStudyProgressKey(canonicalKey, 'question', 'power_idea', `${idea.id}::${q}`);
      pool.push(
        createPoolItem({
          progressKey: qKey,
          canonicalKey,
          areaLabel,
          kind: 'professorQuestion',
          source: 'powerIdeasCatalog',
          title: q,
          subtitle: idea.title,
          level: lvl,
          segment: 'power_idea',
          status: resolveStatus(progressState, qKey),
          priority: 44,
          metadata: { sources: ['powerIdeasCatalog'], relatedIdea: idea.title },
        }),
      );
    }

    for (const proj of idea.projectIdeas || []) {
      const pKey = buildStudyProgressKey(canonicalKey, 'project', 'power_idea', `${idea.id}::${proj}`);
      pool.push(
        createPoolItem({
          progressKey: pKey,
          canonicalKey,
          areaLabel,
          kind: 'project',
          source: 'powerIdeasCatalog',
          title: proj,
          subtitle: idea.title,
          level: lvl,
          segment: 'power_idea',
          status: resolveStatus(progressState, pKey),
          priority: 46,
          metadata: { sources: ['powerIdeasCatalog'], relatedIdea: idea.title },
        }),
      );
    }
  }
}

function addProjectQuestions(pool, block, progressState) {
  const canonicalKey = block.canonicalKey || block.interestId;
  const areaLabel = block.label || interestLabelById(canonicalKey);
  const tracks = block.deep?.projectTracks || {};
  for (const [track, projects] of Object.entries(tracks)) {
    for (const proj of projects || []) {
      const qKey = buildStudyProgressKey(canonicalKey, 'question', 'project', `${track}::${proj}`);
      pool.push(
        createPoolItem({
          progressKey: qKey,
          canonicalKey,
          areaLabel,
          kind: 'professorQuestion',
          source: 'projectTracks',
          title: `Como validar o projeto: ${proj}?`,
          subtitle: proj,
          level: levelLabel(TRACK_SEGMENT[track] || track, '', 'project'),
          segment: track,
          status: resolveStatus(progressState, qKey),
          priority: 52,
          metadata: { sources: ['projectTracks'], projectTitle: proj },
        }),
      );
    }
  }
}

function addGoalRoutes(pool, goalRoutes, activeInterests, progressState) {
  const interestSet = new Set((activeInterests || []).map(resolveCanonicalInterest));
  for (const route of goalRoutes || []) {
    const related = route.relatedCanonicalKeys || [];
    const routeAreas = related.length ? related : interestSet;
    for (const step of route.steps || []) {
      const progressKey = buildRouteStepProgressKey(route.id, step);
      const canonicalKey = related[0] || [...interestSet][0] || 'geral';
      pool.push(
        createPoolItem({
          progressKey,
          canonicalKey,
          areaLabel: route.title,
          kind: 'goalRouteStep',
          source: 'goalRoute',
          title: step,
          subtitle: route.title,
          level: 'Rota',
          segment: route.id,
          status: resolveStatus(progressState, progressKey),
          priority: 40,
          metadata: { sources: ['goalRoute'], routeId: route.id },
        }),
      );
    }
  }
}

function notebookKind(entry) {
  const t = String(entry.tipo || entry.contentCategory || '').toLowerCase();
  if (t.includes('pergunta')) return 'professorQuestion';
  if (t === 'livro' || entry.notebookGroup === 'livros') return 'book';
  if (t === 'ideia_poderosa') return 'powerIdea';
  if (entry.contentCategory === 'projeto' || entry.level) return 'project';
  if (t === 'teoria') return 'theory';
  return 'notebook';
}

function addNotebook(pool, notebookItems, progressState) {
  for (const entry of notebookItems || []) {
    const interesses = entry.interesses || [];
    if (!interesses.length) continue;
    const nbKey = getScientificNotebookEntryKey(entry);
    const title = entry.titulo || entry.title || 'Item do caderno';
    const kind = notebookKind(entry);

    for (const interestId of interesses) {
      const canonicalKey = resolveCanonicalInterest(interestId);
      const progressKey =
        entry.powerIdeaId && kind === 'powerIdea'
          ? buildPowerIdeaProgressKey(canonicalKey, {
              id: entry.powerIdeaId,
              title,
              level: entry.level,
            })
          : buildStudyProgressKey(canonicalKey, 'notebook', kind, `${nbKey || title}`);

      pool.push(
        createPoolItem({
          progressKey,
          canonicalKey,
          areaLabel: interestLabelById(canonicalKey) || canonicalKey,
          kind,
          source: 'notebook',
          title,
          subtitle: entry.resumo || entry.fonte || 'Salvo no caderno',
          level: entry.level || '',
          segment: 'notebook',
          status: resolveStatus(progressState, progressKey),
          priority: 38,
          metadata: { sources: ['notebook'], inNotebook: true, notebookKey: nbKey },
        }),
      );
    }
  }
}

/**
 * Pool global de itens estudáveis (Fase 2L-B).
 * @param {object} params
 */
export function buildStudySessionItemPool(params = {}) {
  const {
    studyBlocks = [],
    activeInterests = [],
    goalRoutes: rawGoalRoutes = [],
    progressState = {},
    bookProgress = {},
    notebookItems: rawNotebookItems = [],
  } = params;

  const goalRoutes = Array.isArray(rawGoalRoutes) ? rawGoalRoutes : [];
  const notebookItems = Array.isArray(rawNotebookItems) ? rawNotebookItems : [];

  const pool = [];

  for (const block of studyBlocks) {
    addFromCollect(pool, block, progressState, bookProgress);
    const canonicalKey = block.canonicalKey || block.interestId;
    const areaLabel = block.label || interestLabelById(canonicalKey);
    addBooksFromCatalog(pool, canonicalKey, areaLabel, progressState, bookProgress);
    addPowerIdeasExtras(pool, canonicalKey, areaLabel, progressState);
    addProjectQuestions(pool, block, progressState);
  }

  addGoalRoutes(pool, goalRoutes, activeInterests, progressState);
  addNotebook(pool, notebookItems, progressState);

  const deduped = dedupeStudySessionItems(pool);

  const byKind = {};
  const byArea = {};
  for (const item of deduped) {
    byKind[item.kind] = (byKind[item.kind] || 0) + 1;
    byArea[item.canonicalKey] = (byArea[item.canonicalKey] || 0) + 1;
  }

  logScientificWorkspace('study_session_pool_built', {
    total: deduped.length,
    byKind,
    byArea,
    studyBlockCount: studyBlocks.length,
    focus: params.focus,
    goalRoutesCount: goalRoutes.length,
  });

  return deduped;
}

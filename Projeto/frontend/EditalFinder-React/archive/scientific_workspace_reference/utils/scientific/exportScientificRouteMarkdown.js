import { interestLabelById } from './scientificInterestsConfig';
import { buildGlobalStudyProgressSummary, buildTrailProgressSummary } from './buildStudyProgressSummary';
import { getProgressStatusFromMap } from './scientificStudyProgressStorage';
import { STUDY_PROGRESS_STATUS_LABELS } from './scientificStudyProgressConstants';
import { buildPowerIdeaProgressKey, buildRouteStepProgressKey } from './scientificStudyProgressKeys';
import { POWER_IDEA_LEVEL_LABELS, POWER_IDEA_TYPE_LABELS } from './scientificPowerIdeasHelpers';
import { buildScientificLevelSummary } from './buildScientificLevelSummary';
import { BOOK_READ_STATUSES } from './scientificBookProgressStorage';
import { getStudySessionStats } from './scientificStudySessionStorage';
import { SESSION_FOCUS_OPTIONS, KIND_DISPLAY_LABELS } from './scientificStudySessionConstants';
import { buildAreaGoalsForActiveInterests } from './buildScientificAreaGoals';
import { displayStudyProgressStatus, displayScientificKind } from './displayScientificLabels';
import { logScientificWorkspace } from './scientificWorkspaceLog';

function mdList(items) {
  return (items || []).map((x) => `- ${x}`).join('\n');
}

function appendProgressSection(lines, studyProgress = {}, studyBlocks = [], goalRoutes = []) {
  const global = buildGlobalStudyProgressSummary(studyBlocks, studyProgress, goalRoutes);
  if (!global.total) return;

  lines.push('## Progresso');
  lines.push('');
  lines.push(`- A estudar: ${global.a_estudar}`);
  lines.push(`- Estudando: ${global.estudando}`);
  lines.push(`- Dominado: ${global.dominado}`);
  lines.push(`- Ignorar por agora: ${global.ignorar_agora}`);
  lines.push('');

  const byStatus = { estudando: [], dominado: [], a_estudar: [], ignorar_agora: [] };
  for (const item of global.items) {
    const status = getProgressStatusFromMap(studyProgress, item.progressKey);
    if (byStatus[status]) byStatus[status].push(item.label);
  }

  if (byStatus.estudando.length) {
    lines.push('### Estudando');
    lines.push(mdList(byStatus.estudando.slice(0, 30)));
    lines.push('');
  }
  if (byStatus.dominado.length) {
    lines.push('### Dominado');
    lines.push(mdList(byStatus.dominado.slice(0, 30)));
    lines.push('');
  }

  lines.push('### Por trilha');
  for (const block of studyBlocks) {
    const trail = buildTrailProgressSummary(block, studyProgress);
    if (!trail.total) continue;
    lines.push(
      `- **${block.label}** — ${trail.dominado} dominado${trail.dominado !== 1 ? 's' : ''}, ${trail.estudando} estudando`,
    );
  }
  lines.push('');

  for (const route of goalRoutes || []) {
    const steps = (route.steps || []).filter((step) => {
      const key = buildRouteStepProgressKey(route.id, step);
      const s = getProgressStatusFromMap(studyProgress, key);
      return s !== 'a_estudar';
    });
    if (!steps.length) continue;
    lines.push(`### Rota: ${route.title}`);
    for (const step of steps) {
      const key = buildRouteStepProgressKey(route.id, step);
      const label = STUDY_PROGRESS_STATUS_LABELS[getProgressStatusFromMap(studyProgress, key)];
      lines.push(`- ${step} (${label})`);
    }
    lines.push('');
  }
}

/**
 * Gera Markdown da rota e trilhas (Fase 2H-F).
 * @param {object} payload
 */
export function buildScientificRouteMarkdown(payload = {}) {
  try {
    return buildScientificRouteMarkdownInner(payload);
  } catch (err) {
    const date = new Date().toISOString().slice(0, 10);
    logScientificWorkspace('markdown_export_failed', { message: err?.message });
    return [
      `# Rota científica — ${date}`,
      '',
      '_Não foi possível gerar o conteúdo completo. Exportação parcial._',
      '',
      `Erro: ${err?.message || 'desconhecido'}`,
      '',
      '---',
      '*Gerado pelo Workspace Científico (EditalFinder)*',
    ].join('\n');
  }
}

function buildScientificRouteMarkdownInner(payload = {}) {
  const date = new Date().toISOString().slice(0, 10);
  const interests = Array.isArray(payload.activeInterests) ? payload.activeInterests : [];
  const goalRoute = payload.goalRoute || null;
  const studyBlocks = Array.isArray(payload.studyBlocks) ? payload.studyBlocks : [];
  const goalRoutes = Array.isArray(payload.goalRoutes) ? payload.goalRoutes : [];
  const studyProgress =
    payload.studyProgress && typeof payload.studyProgress === 'object' ? payload.studyProgress : {};
  const lines = [`# Rota científica — ${date}`, ''];

  lines.push('## Interesses ativos');
  lines.push(mdList(interests.map(interestLabelById)) || '- (nenhum)');
  lines.push('');

  if (goalRoute) {
    lines.push(`## Rota sugerida: ${goalRoute.title}`);
    lines.push(goalRoute.description || '');
    lines.push('');
    lines.push('### Passos');
    lines.push(mdList(goalRoute.steps));
    lines.push('');
    if (goalRoute.suggestedProjects?.length) {
      lines.push('### Projetos sugeridos');
      lines.push(mdList(goalRoute.suggestedProjects));
      lines.push('');
    }
    if (goalRoute.suggestedBooks?.length) {
      lines.push('### Livros recomendados');
      lines.push(mdList(goalRoute.suggestedBooks));
      lines.push('');
    }
  }

  appendProgressSection(lines, studyProgress, studyBlocks, goalRoutes);

  const levelSummary =
    payload.levelSummary || buildScientificLevelSummary(payload.xpState || { totalXp: 0 });
  const xpState = payload.xpState || { totalXp: 0 };
  if (levelSummary?.global) {
    lines.push('## Nível e XP');
    lines.push('');
    lines.push(`- **Nível global:** ${levelSummary.global.level} — ${levelSummary.global.label}`);
    lines.push(`- **XP total:** ${levelSummary.global.totalXp}`);
    if (levelSummary.topAreas?.length) {
      lines.push('- **Áreas mais fortes:**');
      for (const a of levelSummary.topAreas) {
        lines.push(`  - ${a.label}: ${a.xp} XP (nível de área ${a.areaLevel})`);
      }
    }
    lines.push('');
  }

  const badges = payload.badges || [];
  const unlockedBadges = badges.filter((b) => b.unlocked);
  if (unlockedBadges.length) {
    lines.push('## Badges');
    lines.push(mdList(unlockedBadges.map((b) => `${b.icon} ${b.label} — ${b.description}`)));
    lines.push('');
  }

  const masteryChecks = payload.masteryChecks || {};
  const masteryList = Object.values(masteryChecks);
  if (masteryList.length) {
    lines.push('## Verificações de domínio');
    for (const m of masteryList.slice(0, 30)) {
      lines.push(`### ${m.title}`);
      lines.push(`- Área: ${m.canonicalKey} · Tipo: ${m.kind}`);
      if (m.xpAwarded) lines.push(`- XP concedido: ${m.xpAwarded}`);
      for (const a of (m.answers || []).slice(0, 3)) {
        const ans = String(a.answer || '').trim();
        lines.push(`- **P:** ${a.question}`);
        if (ans) lines.push(`  - **R:** ${ans.slice(0, 200)}${ans.length > 200 ? '…' : ''}`);
      }
      lines.push('');
    }
  }

  const bookProgress = payload.bookProgress || {};
  const bookEntries = Object.values(bookProgress);
  if (bookEntries.length) {
    lines.push('## Livros — progresso de leitura');
    const statusLabel = (id) => BOOK_READ_STATUSES.find((s) => s.id === id)?.label || id;
    for (const b of bookEntries) {
      lines.push(
        `- **${b.title}** — ${statusLabel(b.status)} · ${b.progressPercent ?? 0}%${b.currentChapter ? ` · ${b.currentChapter}` : ''}`,
      );
    }
    lines.push('');
  }

  lines.push('## Teoremas e ideias poderosas');
  lines.push('');
  for (const block of studyBlocks) {
    const ideas = block.powerIdeas || block.deep?.powerIdeas || [];
    if (!ideas.length) continue;
    lines.push(`### ${block.label}`);
    for (const idea of ideas) {
      const statusKey = buildPowerIdeaProgressKey(block.canonicalKey || block.interestId, idea);
      const status = getProgressStatusFromMap(studyProgress, statusKey);
      const statusNote =
        status !== 'a_estudar' ? ` — *${STUDY_PROGRESS_STATUS_LABELS[status]}*` : '';
      const typeLabel = POWER_IDEA_TYPE_LABELS[idea.type] || idea.type;
      const levelLabel = POWER_IDEA_LEVEL_LABELS[idea.level] || idea.level;
      lines.push(`- **${idea.title}** (${typeLabel}, ${levelLabel})${statusNote}`);
      lines.push(`  - ${idea.whyItMatters}`);
    }
    lines.push('');
  }

  const studySessions = payload.studySessions || [];
  if (studySessions.length) {
    const stats = getStudySessionStats(studySessions);
    lines.push('## Sessões de estudo');
    lines.push('');
    lines.push(`- **Total de sessões:** ${stats.sessionCount}`);
    lines.push(`- **Tempo total:** ${stats.totalMinutes} min`);
    lines.push(`- **XP de sessões:** ${stats.totalXp}`);
    lines.push('');
    lines.push('### Sessões recentes');
    for (const s of studySessions.slice(0, 10)) {
      const focusLabel =
        SESSION_FOCUS_OPTIONS.find((f) => f.id === s.focus)?.label || s.focus || '';
      lines.push(
        `- **${s.title}** — ${s.durationMinutes} min · Foco: ${focusLabel} · Área: ${s.areaLabel || s.canonicalKey} · +${s.xpAwarded || 0} XP`,
      );
      const kinds = [
        ...new Set((s.selectedItems || []).map((i) => KIND_DISPLAY_LABELS[i.kind] || i.kind)),
      ];
      if (kinds.length) {
        lines.push(`  - Tipos estudados: ${kinds.join(', ')}`);
      }
      for (const item of (s.selectedItems || []).slice(0, 12)) {
        const kindLabel = displayScientificKind(item.kind) || KIND_DISPLAY_LABELS[item.kind] || 'Item';
        const before = displayStudyProgressStatus(item.statusBefore) || '—';
        const after = displayStudyProgressStatus(item.statusAfter) || '—';
        lines.push(`  - ${item.title} (${kindLabel}) — ${before} → ${after}`);
      }
      if (s.reflection?.learned) {
        lines.push(`  - Estudou: ${String(s.reflection.learned).slice(0, 160)}`);
      }
      if (s.reflection?.confused) {
        lines.push(`  - Confuso: ${String(s.reflection.confused).slice(0, 120)}`);
      }
      if (s.reflection?.nextAction) {
        lines.push(`  - Próxima ação: ${String(s.reflection.nextAction).slice(0, 120)}`);
      }
    }
    lines.push('');
  }

  const activeInterests = payload.activeInterests || interests;
  const blocksByKey = {};
  for (const block of studyBlocks) {
    const k = block.canonicalKey || block.interestId;
    if (k) blocksByKey[k] = block;
  }
  const areaGoalsList = buildAreaGoalsForActiveInterests(activeInterests, blocksByKey, {
    studyProgress,
    studySessions,
    notebookItems: payload.notebookItems || [],
    bookProgress: payload.bookProgress || {},
    xpState: payload.xpState,
  });
  if (areaGoalsList.length) {
    lines.push('## Próximas metas por área');
    lines.push('');
    for (const area of areaGoalsList) {
      lines.push(`### ${area.areaLabel} (Nv. ${area.currentAreaLevel} → ${area.nextAreaLevel})`);
      for (const g of area.goals) {
        const done = g.current >= g.target;
        lines.push(`- [${done ? 'x' : ' '}] ${g.label} (${Math.min(g.current, g.target)}/${g.target})`);
      }
      lines.push('');
    }
  }

  lines.push('## Trilhas ativas');
  for (const block of studyBlocks) {
    lines.push(`### ${block.label}`);
    if (block.formationGoal) lines.push(`> ${block.formationGoal}`);
    if (block.matchedInterestLabels?.length > 1) {
      lines.push(`Interesses: ${block.matchedInterestLabels.join(', ')}`);
    }
    if (block.deep?.theory?.foundations?.length) {
      lines.push('');
      lines.push('**Fundamentos (amostra)**');
      lines.push(mdList(block.deep.theory.foundations.slice(0, 8)));
    }
    if (block.books?.length || block.deep?.books) {
      lines.push('');
      lines.push('**Livros**');
      const bk = block.books?.length
        ? block.books
        : [
            ...(block.deep?.books?.introductory || []),
            ...(block.deep?.books?.intermediate || []),
          ];
      lines.push(mdList(bk.slice(0, 6)));
    }
    if (block.deep?.projectTracks) {
      lines.push('');
      lines.push('**Projetos por nível (amostra)**');
      for (const [lvl, items] of Object.entries(block.deep.projectTracks)) {
        if (items?.length) lines.push(`- *${lvl}*: ${items.slice(0, 3).join('; ')}`);
      }
    }
    const questions = block.deep?.professorQuestions || block.professorQuestions;
    if (questions?.length) {
      lines.push('');
      lines.push('**Perguntas ao orientador**');
      lines.push(mdList(questions.slice(0, 5)));
    }
    lines.push('');
  }

  lines.push('---');
  lines.push('*Gerado pelo Workspace Científico (EditalFinder)*');
  return lines.join('\n');
}

/**
 * Dispara download de arquivo .md no navegador.
 * @param {object} payload
 */
export function downloadScientificRouteMarkdown(payload = {}) {
  const md = buildScientificRouteMarkdown(payload);
  const date = new Date().toISOString().slice(0, 10);
  try {
    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rota_cientifica_${date}.md`;
    a.click();
    URL.revokeObjectURL(url);
    logScientificWorkspace('markdown_exported', {
      length: md.length,
      interests: (payload.activeInterests || []).length,
    });
  } catch (err) {
    logScientificWorkspace('markdown_export_failed', { message: err?.message });
  }
  return md;
}

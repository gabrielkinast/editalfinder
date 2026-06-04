import { interestLabelById, SCIENTIFIC_INTERESTS } from './scientificInterestsConfig';
import { SCIENTIFIC_PROJECT_CATALOG } from './scientificProjectCatalog';
import { normalizeProjectLevel, levelLabel } from './scientificProjectLevels';
import { cleanScientificTitle } from './cleanScientificTitle';
import { deduplicateProjectIdeas } from './deduplicateProjectIdeas';
import { projectMaturityFromLevel } from './scientificProjectLevels';

function hasAll(active, required) {
  if (!required?.length) return false;
  return required.every((r) => active.includes(r));
}

function normalizeIdea(raw) {
  const level = normalizeProjectLevel(raw.level);
  const title = cleanScientificTitle(raw.title || raw.titulo || 'Projeto') || 'Projeto';
  const maturity = raw.maturity || projectMaturityFromLevel(level).label;
  return {
    id: raw.id,
    title,
    titulo: title,
    level,
    levelLabel: levelLabel(level),
    maturity,
    type: raw.type || raw.tipo || 'projeto',
    why: raw.why || raw.porque || '',
    porque: raw.why || raw.porque || '',
    disciplines: raw.disciplines || raw.disciplinas || [],
    disciplinas: raw.disciplines || raw.disciplinas || [],
    tools: raw.tools || raw.ferramentas || [],
    ferramentas: raw.tools || raw.ferramentas || [],
    prerequisites: raw.prerequisites || [],
    theoryTopics: raw.theoryTopics || [],
    expectedOutput: raw.expectedOutput || '',
    difficulty: raw.difficulty || levelLabel(level),
    duration: raw.duration || '',
    nextSteps: raw.nextSteps || [],
    possibleDeliverables: raw.possibleDeliverables || [],
    professorQuestions: raw.professorQuestions || [],
    interesses: raw.needs || raw.interesses || [],
    needs: raw.needs || raw.interesses || [],
    fromNotebook: Boolean(raw.fromNotebook),
    continuationFromNotebook: Boolean(raw.continuationFromNotebook),
  };
}

/**
 * @param {string[]} activeInterests
 * @param {Array<object>} [notebookItems]
 */
export function buildScientificProjectIdeas(activeInterests = [], notebookItems = []) {
  const active = Array.isArray(activeInterests) ? activeInterests : [];
  const ideas = [];

  for (const tpl of SCIENTIFIC_PROJECT_CATALOG) {
    const needs = tpl.needs || tpl.interests || [];
    const interests = tpl.interests || needs;
    if (needs.length > 0 && hasAll(active, needs)) {
      ideas.push(normalizeIdea({ ...tpl, interesses: interests, needs }));
    }
  }

  if (ideas.length < 4 && active.length >= 1) {
    const primary = active[0];
    ideas.push(
      normalizeIdea({
        id: `idea-generic-${primary}-basico`,
        needs: [primary],
        title: `Exploração guiada em ${interestLabelById(primary)}`,
        level: 'basico',
        type: 'estudo dirigido',
        why: `Ponto de partida no interesse ${interestLabelById(primary)}.`,
        disciplines: [interestLabelById(primary)],
        tools: ['Python', 'caderno científico'],
        expectedOutput: 'Resumo de 3 fontes + conceitos do catálogo.',
        nextSteps: ['Abrir trilha de fundamentos', 'Salvar 2 itens do feed', 'Definir mini-projeto'],
      }),
    );
  }

  if (notebookItems.length > 0) {
    const top = notebookItems.find((n) => n.contentCategory === 'projeto') || notebookItems[0];
    const baseTitle =
      cleanScientificTitle(top.titulo || top.title) || 'item do caderno';
    ideas.push(
      normalizeIdea({
        id: `idea-from-notebook-${top.id}`,
        needs: top.interesses?.length ? top.interesses : active.slice(0, 2),
        title: baseTitle,
        level: top.level || 'intermediario',
        type: top.tipo || 'revisão a partir do caderno',
        why: 'Continuação de um item do seu caderno científico.',
        disciplines: (top.disciplines || top.interesses || active).map((x) =>
          typeof x === 'string' && x.includes('_') ? interestLabelById(x) : x,
        ),
        tools: top.tools || ['caderno', 'literatura'],
        expectedOutput: top.expectedOutput || 'Relatório curto ou notebook.',
        nextSteps: top.nextSteps?.length
          ? top.nextSteps
          : ['Revisar anotações', 'Buscar 5 referências', 'Propor extensão ao orientador'],
        fromNotebook: true,
        continuationFromNotebook: true,
      }),
    );
  }

  return deduplicateProjectIdeas(ideas);
}

/**
 * @param {Array} ideas
 * @param {string} levelFilter — 'todos' ou id de nível
 */
export function filterProjectIdeasByLevel(ideas, levelFilter) {
  if (!levelFilter || levelFilter === 'todos') return ideas;
  return ideas.filter((i) => normalizeProjectLevel(i.level) === levelFilter);
}

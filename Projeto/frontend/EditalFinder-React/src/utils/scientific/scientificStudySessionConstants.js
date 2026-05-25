/** Foco, nível, status e quantidade — sessão de estudo (Fase 2L-B / 2L-C). */

import { STUDY_PROGRESS_STATUS_LABELS } from './scientificStudyProgressConstants';

export const SESSION_FOCUS_OPTIONS = [
  { id: 'theory', label: 'Teoria', kinds: ['theory'] },
  { id: 'powerIdea', label: 'Ideias poderosas', kinds: ['powerIdea'] },
  { id: 'book', label: 'Livros', kinds: ['book'] },
  { id: 'project', label: 'Projetos', kinds: ['project'] },
  { id: 'professorQuestion', label: 'Perguntas para professor', kinds: ['professorQuestion'] },
  { id: 'review', label: 'Revisão ativa', kinds: null },
  { id: 'mixed', label: 'Misto recomendado', kinds: null },
];

export const FOCUS_DESCRIPTIONS = {
  theory:
    'Estude tópicos da trilha: fundamentos, intermediário, avançado e pesquisa.',
  powerIdea: 'Teoremas, princípios e conceitos que destravam a área.',
  book: 'Acompanhe leituras e capítulos.',
  project: 'Ideias práticas, IC/TCC e mestrado.',
  professorQuestion: 'Prepare perguntas para professor/orientador.',
  review: 'Revise o que está estudando ou dominou há algum tempo.',
  mixed: 'Combina teoria, ideia poderosa, livro, projeto e pergunta.',
};

export const SESSION_LEVEL_OPTIONS = [
  { id: '', label: 'Todos' },
  { id: 'foundations', label: 'Fundamentos', segments: ['foundations'], levels: ['basico', 'introductory', 'base'] },
  { id: 'intermediate', label: 'Intermediário', segments: ['intermediate'], levels: ['intermediario', 'intermediate'] },
  { id: 'advanced', label: 'Avançado', segments: ['advanced'], levels: ['avancado', 'advanced'] },
  { id: 'research', label: 'Pesquisa/Mestrado', segments: ['researchlevel', 'research'], levels: ['pesquisa', 'referencia'] },
  { id: 'basic', label: 'Básico', segments: ['basic'], levels: ['basic', 'basico'] },
  { id: 'ictcc', label: 'IC/TCC', segments: ['ictcc'], levels: [] },
  { id: 'masters', label: 'Mestrado', segments: ['masters'], levels: [] },
];

export const SESSION_STATUS_OPTIONS = [
  { id: '', label: 'Todos' },
  { id: 'a_estudar', label: 'A estudar' },
  { id: 'estudando', label: 'Estudando' },
  { id: 'dominado', label: 'Dominado' },
  { id: 'ignorar_agora', label: 'Ignorar por agora' },
  { id: 'none', label: 'Novo / sem status' },
];

export const SESSION_SOURCE_OPTIONS = [
  { id: '', label: 'Todas as origens' },
  { id: 'deepStudyCatalog', label: 'Trilha profunda' },
  { id: 'powerIdeasCatalog', label: 'Ideias poderosas' },
  { id: 'bookCatalog', label: 'Catálogo de livros' },
  { id: 'projectTracks', label: 'Projetos' },
  { id: 'goalRoute', label: 'Rota por objetivo' },
  { id: 'notebook', label: 'Caderno' },
];

export const SESSION_QUANTITY_OPTIONS = [
  { id: 5, label: '5' },
  { id: 10, label: '10' },
  { id: 20, label: '20' },
  { id: 0, label: 'Todos' },
];

export const KIND_DISPLAY_LABELS = {
  theory: 'Teoria',
  powerIdea: 'Ideia poderosa',
  book: 'Livro',
  project: 'Projeto',
  professorQuestion: 'Pergunta',
  goalRouteStep: 'Passo da rota',
  notebook: 'Caderno',
};

export const SOURCE_DISPLAY_LABELS = {
  deepStudyCatalog: 'Trilha profunda',
  powerIdeasCatalog: 'Ideia poderosa',
  bookCatalog: 'Catálogo de livros',
  projectTracks: 'Projeto',
  goalRoute: 'Rota',
  notebook: 'Caderno',
};

/** Rótulo de status na lista do modal (Fase 2L-C). */
export function displaySessionItemStatus(status, item = null) {
  if (item?.kind === 'book' && item.subtitle) {
    const m = item.subtitle.match(/Lendo\s+(\d+)%/i);
    if (m) return `Lendo ${m[1]}%`;
  }
  if (!status || status === 'none') return 'Novo';
  return STUDY_PROGRESS_STATUS_LABELS[status] || status;
}

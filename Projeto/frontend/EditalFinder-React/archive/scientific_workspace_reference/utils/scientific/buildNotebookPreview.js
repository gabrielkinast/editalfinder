import { getNotebookDisplayGroup } from './scientificNotebookGroups';

/**
 * Preview do caderno: limites por grupo (Fase 2H-F).
 * @param {Array<object>} items
 */
export function buildNotebookPreview(items = []) {
  const byGroup = {
    projetos: [],
    livros: [],
    teoria: [],
    ideias_poderosas: [],
    perguntas: [],
    fontes: [],
    rotas: [],
    outros: [],
  };

  for (const item of items) {
    const g = getNotebookDisplayGroup(item);
    if (g === 'projetos') byGroup.projetos.push(item);
    else if (g === 'livros') byGroup.livros.push(item);
    else if (g === 'teoria') byGroup.teoria.push(item);
    else if (g === 'ideias_poderosas') byGroup.ideias_poderosas.push(item);
    else if (g === 'perguntas') byGroup.perguntas.push(item);
    else if (g === 'fontes') byGroup.fontes.push(item);
    else if (g === 'rotas') byGroup.rotas.push(item);
    else byGroup.outros.push(item);
  }

  const preview = [];
  if (byGroup.projetos.length) {
    preview.push({ id: 'projetos', label: 'Projetos', items: byGroup.projetos.slice(0, 2), total: byGroup.projetos.length });
  }
  const lit = [...byGroup.livros, ...byGroup.teoria, ...byGroup.ideias_poderosas];
  if (lit.length) {
    preview.push({ id: 'lit', label: 'Livros, teoria e ideias', items: lit.slice(0, 2), total: lit.length });
  }
  if (byGroup.perguntas.length) {
    preview.push({ id: 'perguntas', label: 'Perguntas', items: byGroup.perguntas.slice(0, 1), total: byGroup.perguntas.length });
  }
  const rest = [...byGroup.fontes, ...byGroup.rotas, ...byGroup.outros]
    .sort((a, b) => new Date(b.savedAt || 0) - new Date(a.savedAt || 0))
    .slice(0, 5);
  if (rest.length) {
    preview.push({ id: 'recent', label: 'Recentes', items: rest, total: rest.length });
  }

  return preview;
}

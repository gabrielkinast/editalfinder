/** Agrupamento visual do caderno (Fase 2D). */
export const NOTEBOOK_DISPLAY_GROUPS = [
  { id: 'fontes', label: 'Fontes salvas' },
  { id: 'projetos', label: 'Projetos salvos' },
  { id: 'rotas', label: 'Rotas/estudos' },
  { id: 'livros', label: 'Livros' },
  { id: 'teoria', label: 'Teoria' },
  { id: 'ideias_poderosas', label: 'Ideias poderosas' },
  { id: 'perguntas', label: 'Perguntas' },
];

export const NOTEBOOK_GROUP_FILTER_OPTIONS = [
  { id: '', label: 'Todos' },
  { id: 'fontes', label: 'Fontes' },
  { id: 'projetos', label: 'Projetos' },
  { id: 'rotas', label: 'Rotas/estudos' },
  { id: 'livros', label: 'Livros' },
  { id: 'teoria', label: 'Teoria' },
  { id: 'perguntas', label: 'Perguntas' },
];

/**
 * @param {object} item
 * @returns {'fontes'|'projetos'|'perguntas'|'rotas'|'livros'|'teoria'}
 */
export function getNotebookDisplayGroup(item) {
  const tipo = String(item?.tipo || '').toLowerCase();
  const cat = String(item?.contentCategory || '').toLowerCase();
  if (tipo === 'livro' || cat === 'livro' || item?.notebookGroup === 'livros') return 'livros';
  if (tipo === 'teoria' || cat === 'teoria' || item?.notebookGroup === 'teoria') return 'teoria';
  if (
    tipo === 'ideia_poderosa' ||
    cat === 'ideia_poderosa' ||
    item?.notebookGroup === 'ideias_poderosas'
  ) {
    return 'ideias_poderosas';
  }
  if (tipo === 'rota_estudo' || tipo.includes('rota de estudo')) return 'rotas';
  if (item?.contentCategory === 'feed' || item?.feedId) return 'fontes';
  if (tipo === 'pergunta_professor' || item?.categoria === 'pergunta') return 'perguntas';
  if (tipo.includes('pergunta') || item?.notebookGroup === 'perguntas') return 'perguntas';
  if (item?.contentCategory === 'projeto' || item?.level) return 'projetos';
  if (item?.contentCategory === 'estudo') return 'rotas';
  return 'fontes';
}

/**
 * @param {Array<object>} items
 */
export function groupNotebookItems(items = []) {
  const groups = Object.fromEntries(NOTEBOOK_DISPLAY_GROUPS.map((g) => [g.id, []]));
  for (const item of items) {
    const key = getNotebookDisplayGroup(item);
    if (groups[key]) groups[key].push(item);
  }
  return NOTEBOOK_DISPLAY_GROUPS.map((g) => ({
    ...g,
    items: groups[g.id] || [],
    count: (groups[g.id] || []).length,
  })).filter((g) => g.count > 0);
}

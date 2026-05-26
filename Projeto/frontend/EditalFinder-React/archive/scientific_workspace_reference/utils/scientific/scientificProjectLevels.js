/** Níveis de projeto/estudo (Fase 2). */
export const PROJECT_LEVELS = [
  { id: 'basico', label: 'Básico', order: 1 },
  { id: 'intermediario', label: 'Intermediário', order: 2 },
  { id: 'avancado', label: 'Avançado', order: 3 },
  { id: 'ic_tcc', label: 'IC/TCC', order: 4 },
  { id: 'mestrado', label: 'Mestrado', order: 5 },
];

export const PROJECT_LEVEL_FILTER_ALL = 'todos';

export const LEVEL_DESCRIPTIONS = {
  fundamentals: 'Conceitos que o estudante precisa dominar para entender a área.',
  practical: 'Projetos pequenos em Python, revisão bibliográfica, simulação simples ou estudo dirigido.',
  advanced_research: 'Ideias com cara de iniciação científica, TCC, mestrado ou projeto computacional mais sério.',
  graduate: 'Temas que exigem base matemática/física maior, literatura científica e possível orientação.',
};

export function levelLabel(levelId) {
  return PROJECT_LEVELS.find((l) => l.id === levelId)?.label || levelId || '—';
}

/** Maturidade pedagógica derivada do nível (Fase 2D). */
export function projectMaturityFromLevel(level) {
  const id = normalizeProjectLevel(level);
  const map = {
    basico: { id: 'inicial', label: 'Ideia inicial' },
    intermediario: { id: 'pratico', label: 'Projeto prático' },
    avancado: { id: 'professor', label: 'Projeto para discutir com professor' },
    ic_tcc: { id: 'ic_tcc', label: 'Potencial IC/TCC' },
    mestrado: { id: 'mestrado', label: 'Potencial mestrado' },
  };
  return map[id] || { id: 'pratico', label: 'Projeto prático' };
}

export function normalizeProjectLevel(level) {
  if (!level) return 'intermediario';
  const s = String(level).toLowerCase().replace(/\s+/g, '_');
  const map = {
    basico: 'basico',
    básico: 'basico',
    basic: 'basico',
    intermediario: 'intermediario',
    intermediário: 'intermediario',
    intermediate: 'intermediario',
    avancado: 'avancado',
    avançado: 'avancado',
    advanced: 'avancado',
    ic_tcc: 'ic_tcc',
    ic: 'ic_tcc',
    tcc: 'ic_tcc',
    mestrado: 'mestrado',
    master: 'mestrado',
    graduate: 'mestrado',
  };
  return map[s] || (PROJECT_LEVELS.some((l) => l.id === s) ? s : 'intermediario');
}

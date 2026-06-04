/** XP por tipo ao confirmar domínio (Fase 2K). */
export const XP_BY_KIND = {
  theory: 10,
  powerIdea: 15,
  book: 30,
  project: 40,
  question: 10,
  route_step: 15,
  route_saved: 20,
  study_session: 0,
};

export const XP_BONUS_ANSWERS_FILLED = 5;

export const GLOBAL_LEVELS = [
  { level: 1, minXp: 0, label: 'Iniciante científico' },
  { level: 2, minXp: 100, label: 'Estudante em formação' },
  { level: 3, minXp: 250, label: 'Explorador de área' },
  { level: 4, minXp: 500, label: 'Iniciante em projeto' },
  { level: 5, minXp: 900, label: 'Pesquisador júnior' },
  { level: 6, minXp: 1400, label: 'Pré-IC/TCC' },
  { level: 7, minXp: 2000, label: 'IC/TCC em andamento' },
  { level: 8, minXp: 2800, label: 'Pós-graduação inicial' },
  { level: 9, minXp: 3800, label: 'Especialista em formação' },
  { level: 10, minXp: 5000, label: 'Trilha de mestrado' },
];

/** XP por área para subnível local (a cada 60 XP na área). */
export const AREA_XP_PER_SUBLEVEL = 60;

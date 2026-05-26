/** Status de progresso na trilha (Fase 2I). */
export const STUDY_PROGRESS_STATUSES = [
  'a_estudar',
  'estudando',
  'dominado',
  'ignorar_agora',
];

export const STUDY_PROGRESS_STATUS_LABELS = {
  a_estudar: 'A estudar',
  estudando: 'Estudando',
  dominado: 'Dominado',
  ignorar_agora: 'Ignorar por agora',
};

export const STUDY_PROGRESS_FILTER_OPTIONS = [
  { id: '', label: 'Todos' },
  { id: 'a_estudar', label: 'A estudar' },
  { id: 'estudando', label: 'Estudando' },
  { id: 'dominado', label: 'Dominados' },
  { id: 'ignorar_agora', label: 'Ignorados' },
];

export const DEFAULT_STUDY_PROGRESS_STATUS = 'a_estudar';

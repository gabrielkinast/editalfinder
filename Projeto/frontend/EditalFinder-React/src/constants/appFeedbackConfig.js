export const TABLE_APP_FEEDBACK = 'app_feedback';

export const APP_FEEDBACK_PENDING_KEY = 'app_feedback_pending';
export const APP_FEEDBACK_QUEUE_KEY = 'editalfinder:app_feedback_queue:v1';
export const APP_FEEDBACK_QUEUE_MAX = 50;

export const APP_FEEDBACK_EMAIL_FUNCTION = 'send-app-feedback-email';

/** Desliga compositor de e-mail no submit (emergência); app continua renderizando. */
export const ENABLE_APP_FEEDBACK_MAILTO = true;

/** Fluxo principal: Gmail Web Compose → mailto → localStorage (FRONTEND 1.1C.4). */
export const MSG_APP_FEEDBACK_SUCCESS_GMAIL =
  'O Gmail foi aberto no navegador. Revise e envie o relatório para o suporte.';
export const MSG_APP_FEEDBACK_SUCCESS_MAILTO =
  'Seu aplicativo de e-mail foi aberto. Revise e envie o relatório para o suporte.';
export const MSG_APP_FEEDBACK_SUCCESS_LOCAL =
  'Não foi possível abrir o Gmail ou o aplicativo de e-mail. O relatório foi salvo localmente.';
export const MSG_APP_FEEDBACK_FALLBACK_TITLE =
  'Não foi possível abrir o Gmail ou o aplicativo de e-mail automaticamente.';
export const MSG_APP_FEEDBACK_FALLBACK_BODY =
  'Seu reporte foi salvo neste dispositivo. Você também pode copiar o reporte abaixo e enviar manualmente para:';
export const MSG_APP_FEEDBACK_MODAL_HINT =
  'Ao enviar, abriremos o Gmail no navegador com o reporte pronto para Suporte.EditalFinder@gmail.com. Revise e clique em Enviar no Gmail.';

/** Legado — Edge Function / Resend (opcional, não é prioridade) */
export const MSG_APP_FEEDBACK_SUCCESS_EMAIL =
  'Relatório enviado para a equipe. Obrigado por ajudar a melhorar o EditalFinder.';
export const MSG_APP_FEEDBACK_SUCCESS_REMOTE =
  'Relatório enviado. Obrigado por ajudar a melhorar o EditalFinder.';
export const MSG_APP_FEEDBACK_VALIDATION =
  'Revise os campos do relatório.';
export const MSG_APP_FEEDBACK_FAILED =
  'Não foi possível abrir o e-mail nem guardar o reporte. Tente novamente.';

export const APP_FEEDBACK_COMMENT_MAX = 2000;
export const APP_FEEDBACK_COMMENT_MIN = 10;
export const APP_FEEDBACK_STACK_MAX = 8000;
export const APP_FEEDBACK_ERROR_MSG_MAX = 2000;

/** Taxonomia canónica (FRONTEND 1.1C.3). Campos: value, label, group. */
export const APP_FEEDBACK_PROBLEM_TYPES = [
  { value: 'page_broken', label: 'Erro na página / tela quebrou', group: 'app' },
  { value: 'browser_error', label: 'Erro inesperado no navegador', group: 'app' },
  { value: 'desktop_exe_error', label: 'Erro no aplicativo desktop / EXE', group: 'desktop' },
  {
    value: 'desktop_open_link_error',
    label: 'Desktop/EXE: link, PDF ou inscrição não abriu',
    group: 'desktop',
  },
  { value: 'desktop_startup_error', label: 'Desktop/EXE: erro ao abrir o aplicativo', group: 'desktop' },
  {
    value: 'desktop_update_install_error',
    label: 'Desktop/EXE: problema de instalação ou atualização',
    group: 'desktop',
  },
  { value: 'save_load_error', label: 'Falha ao carregar ou salvar dados', group: 'data' },
  { value: 'wrong_data', label: 'Dado incorreto na tela', group: 'data' },
  { value: 'button_action_error', label: 'Botão ou ação não funcionou', group: 'ui' },
  { value: 'visual_layout_problem', label: 'Problema visual / layout', group: 'ui' },
  { value: 'pdf_export_error', label: 'Erro ao gerar ou exportar PDF', group: 'export' },
  { value: 'spreadsheet_export_error', label: 'Erro ao exportar planilha', group: 'export' },
  { value: 'filter_search_error', label: 'Filtro, busca ou ordenação não funcionou', group: 'ui' },
  { value: 'performance_slow', label: 'Lentidão ou travamento', group: 'performance' },
  { value: 'login_auth_error', label: 'Erro de login ou permissão', group: 'auth' },
  { value: 'other', label: 'Outro', group: 'other' },
];

export const DEFAULT_APP_FEEDBACK_TYPE_VALUE =
  APP_FEEDBACK_PROBLEM_TYPES.find((item) => item.value === 'other')?.value ||
  APP_FEEDBACK_PROBLEM_TYPES[0]?.value ||
  'other';

/** Níveis de severidade (FRONTEND 1.1C.5). */
export const APP_FEEDBACK_SEVERITY_LEVELS = [
  {
    value: 'low',
    label: 'Baixa',
    description: 'Pequeno problema visual, texto incorreto ou incômodo leve.',
    emailPrefix: 'BAIXA',
  },
  {
    value: 'medium',
    label: 'Média',
    description: 'Atrapalha o uso, mas existe contorno.',
    emailPrefix: 'MÉDIA',
  },
  {
    value: 'high',
    label: 'Alta',
    description: 'Impede uma funcionalidade importante.',
    emailPrefix: 'ALTA',
  },
  {
    value: 'critical',
    label: 'Crítica',
    description: 'App travou, tela branca, perda de dados ou EXE não abre.',
    emailPrefix: 'CRÍTICA',
  },
];

export const DEFAULT_APP_FEEDBACK_SEVERITY_VALUE = 'medium';

/** Labels humanos para grupos técnicos de categoria. */
export const APP_FEEDBACK_CATEGORY_LABELS = {
  app: 'Aplicativo',
  desktop: 'Desktop/EXE',
  data: 'Dados',
  ui: 'Interface',
  export: 'Exportação',
  performance: 'Performance',
  auth: 'Login/permissão',
  other: 'Outro',
};

/** @deprecated Use APP_FEEDBACK_PROBLEM_TYPES — compatibilidade. */
export const APP_FEEDBACK_TIPOS = APP_FEEDBACK_PROBLEM_TYPES.map((t) => ({
  id: t.value,
  label: t.label,
}));

export const APP_FEEDBACK_ORIGENS = [
  'error_boundary',
  'window_error',
  'unhandled_rejection',
  'api_error',
  'user_report',
  'toast_error',
  'workspace_cientifico',
  'workspace_consultor',
  'editais',
  'radar',
  'cadastros',
  'noticias',
  'pesquisas',
  'portais',
  'concursos',
  'dashboard',
];

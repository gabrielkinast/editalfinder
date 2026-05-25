export const TABLE_APP_FEEDBACK = 'app_feedback';

export const APP_FEEDBACK_PENDING_KEY = 'app_feedback_pending';

export const APP_FEEDBACK_COMMENT_MAX = 2000;
export const APP_FEEDBACK_COMMENT_MIN = 10;
export const APP_FEEDBACK_STACK_MAX = 8000;
export const APP_FEEDBACK_ERROR_MSG_MAX = 2000;

export const APP_FEEDBACK_TIPOS = [
  { id: 'erro_pagina', label: 'Erro na página (tela quebrou)' },
  { id: 'erro_global', label: 'Erro inesperado no navegador' },
  { id: 'erro_api', label: 'Falha ao carregar ou salvar dados' },
  { id: 'botao_nao_funciona', label: 'Botão ou ação não funcionou' },
  { id: 'bug_visual', label: 'Problema visual / layout' },
  { id: 'lentidao', label: 'Lentidão ou travamento' },
  { id: 'dado_incorreto', label: 'Dado incorreto na tela' },
  { id: 'outro', label: 'Outro' },
];

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

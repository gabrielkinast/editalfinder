import { APP_FEEDBACK_PROBLEM_TYPES } from '../../constants/appFeedbackConfig.js';
import { getRuntimeContext } from './runtimeContext.js';

const BY_VALUE = new Map(APP_FEEDBACK_PROBLEM_TYPES.map((t) => [t.value, t]));

/** IDs legados (pré-1.1C.3) → value canónico. */
const LEGACY_TIPO_TO_VALUE = {
  erro_pagina: 'page_broken',
  erro_global: 'browser_error',
  erro_api: 'save_load_error',
  botao_nao_funciona: 'button_action_error',
  bug_visual: 'visual_layout_problem',
  lentidao: 'performance_slow',
  dado_incorreto: 'wrong_data',
  outro: 'other',
};

/** Mapeamento para CHECK constraint de `app_feedback.tipo_feedback` no SQL. */
const VALUE_TO_LEGACY_DB_TIPO = {
  page_broken: 'erro_pagina',
  browser_error: 'erro_global',
  desktop_exe_error: 'erro_global',
  desktop_open_link_error: 'botao_nao_funciona',
  desktop_startup_error: 'erro_global',
  desktop_update_install_error: 'outro',
  save_load_error: 'erro_api',
  wrong_data: 'dado_incorreto',
  button_action_error: 'botao_nao_funciona',
  visual_layout_problem: 'bug_visual',
  pdf_export_error: 'outro',
  spreadsheet_export_error: 'outro',
  filter_search_error: 'botao_nao_funciona',
  performance_slow: 'lentidao',
  login_auth_error: 'erro_api',
  other: 'outro',
};

const FALLBACK_PROBLEM_TYPE = {
  value: 'other',
  label: 'Outro',
  group: 'other',
};

function fallbackProblemType() {
  const fromList =
    APP_FEEDBACK_PROBLEM_TYPES.find((item) => item.value === 'other') ||
    APP_FEEDBACK_PROBLEM_TYPES[0];
  return fromList ? { ...fromList } : { ...FALLBACK_PROBLEM_TYPE };
}

export function resolveProblemType(value) {
  const normalized = LEGACY_TIPO_TO_VALUE[value] ?? value;
  const found = BY_VALUE.get(normalized);
  if (found) return { ...found };
  return fallbackProblemType();
}

/** Alias canónico — nunca retorna null. */
export function getFeedbackProblemType(value) {
  return resolveProblemType(value);
}

export function mapToLegacyTipoFeedback(value) {
  const meta = resolveProblemType(value);
  return VALUE_TO_LEGACY_DB_TIPO[meta.value] ?? 'outro';
}

/**
 * Sugere tipo inicial a partir do contexto do modal / erro global.
 */
export function mapContextToDefaultTipo(context) {
  const ctx = context ?? {};
  if (ctx.tipo) return resolveProblemType(ctx.tipo).value;
  if (ctx.payload?.tipo) return resolveProblemType(ctx.payload.tipo).value;
  if (ctx.payload?.tipo_feedback) {
    return resolveProblemType(ctx.payload.tipo_feedback).value;
  }

  const origem = ctx.origem;

  const runtime = getRuntimeContext();

  if (origem === 'window_error' || origem === 'unhandled_rejection') {
    return runtime.is_desktop ? 'desktop_exe_error' : 'browser_error';
  }
  if (origem === 'error_boundary') return 'page_broken';
  if (origem === 'api_error' || origem === 'toast_error') return 'save_load_error';

  if (runtime.is_desktop && ctx.actionType?.includes?.('edital')) {
    return 'desktop_open_link_error';
  }

  return 'other';
}

export function isHighPriorityProblemType(value) {
  const v = resolveProblemType(value).value;
  return [
    'page_broken',
    'browser_error',
    'desktop_exe_error',
    'desktop_startup_error',
    'desktop_open_link_error',
  ].includes(v);
}

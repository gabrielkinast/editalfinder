/**
 * Orientação de reporte (DESKTOP QA 1.0 — seção 7).
 *
 * Desktop/EXE → pedir print/foto da tela.
 * Web/site → pedir descrição detalhada.
 * Combinado → texto único usado no corpo do e-mail.
 */

import { getRuntimeContext } from './runtimeContext.js';

export const REPORT_GUIDANCE_DESKTOP =
  'De preferência, anexe uma foto/print da tela no e-mail para ajudar a resolvermos mais rápido.';

export const REPORT_GUIDANCE_WEB =
  'De preferência, descreva o problema com o máximo de detalhes possível para ajudar a resolvermos mais rápido.';

export const REPORT_GUIDANCE_COMBINED =
  'De preferência, inclua uma foto/print da tela no e-mail e descreva o problema com detalhes ' +
  'para ajudar a resolvermos mais rápido.';

export const REPORT_GUIDANCE_EMAIL_BODY =
  'Se possível, anexe uma foto/print da tela mostrando o erro. Caso esteja usando a versão ' +
  'web/site, descreva o problema com o máximo de detalhes possível. Isso ajuda a resolvermos mais rápido.';

/**
 * Texto de orientação conforme runtime.
 * @param {{ is_desktop?: boolean }|null} [ctx] — usa getRuntimeContext() se omitido
 * @returns {string}
 */
export function getReportProblemGuidanceText(ctx) {
  const resolved = ctx ?? safeRuntime();
  if (resolved?.is_desktop) return REPORT_GUIDANCE_DESKTOP;
  return REPORT_GUIDANCE_WEB;
}

function safeRuntime() {
  try {
    return getRuntimeContext();
  } catch {
    return { is_desktop: false };
  }
}

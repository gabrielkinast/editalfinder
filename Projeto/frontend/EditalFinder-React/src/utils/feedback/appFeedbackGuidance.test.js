import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  getReportProblemGuidanceText,
  REPORT_GUIDANCE_DESKTOP,
  REPORT_GUIDANCE_WEB,
  REPORT_GUIDANCE_COMBINED,
  REPORT_GUIDANCE_EMAIL_BODY,
} from './appFeedbackGuidance.js';
import { buildSupportEmailBody } from './appFeedbackMailto.js';

test('desktop pede print/foto da tela', () => {
  const txt = getReportProblemGuidanceText({ is_desktop: true });
  assert.equal(txt, REPORT_GUIDANCE_DESKTOP);
  assert.match(txt, /print/i);
  assert.match(txt, /foto/i);
});

test('web pede descrição detalhada', () => {
  const txt = getReportProblemGuidanceText({ is_desktop: false });
  assert.equal(txt, REPORT_GUIDANCE_WEB);
  assert.match(txt, /detalhes/i);
});

test('texto combinado cobre print + detalhes', () => {
  assert.match(REPORT_GUIDANCE_COMBINED, /print/i);
  assert.match(REPORT_GUIDANCE_COMBINED, /detalhes/i);
});

test('corpo do e-mail inclui orientação de print/descrição', () => {
  const body = buildSupportEmailBody({
    descricao: 'teste',
    runtime: 'web_browser',
    rota: '/editais',
  });
  assert.ok(body.includes(REPORT_GUIDANCE_EMAIL_BODY));
  assert.match(body, /print da tela/i);
  assert.match(body, /web\/site/i);
});

test('getReportProblemGuidanceText sem contexto não quebra (default web)', () => {
  const txt = getReportProblemGuidanceText();
  assert.ok(txt === REPORT_GUIDANCE_DESKTOP || txt === REPORT_GUIDANCE_WEB);
});

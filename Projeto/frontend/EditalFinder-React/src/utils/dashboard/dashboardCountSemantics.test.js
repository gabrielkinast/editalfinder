import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  buildDashboardCountContexts,
  DASHBOARD_COUNT_HELP_TEXT,
  DASHBOARD_MONITORED_LABEL,
} from './dashboardCountSemantics.js';

const SCENARIO = {
  totalEditais: 437,
  catalogEditais: 1051,
  prazoConfirmado: 6,
  semPrazoEstruturado: 300,
  expiringSoon: 0,
  expiring30: 4,
  reportedProblemsPending: 0,
};

test('diferencia catalogCount (recebido) de totalEditais (priorizado)', () => {
  const ctx = buildDashboardCountContexts(SCENARIO);
  assert.match(ctx.monitored, /1\.051 recebidos no catálogo/);
  assert.match(ctx.monitored, /subconjunto priorizado do Dashboard/);
});

test('card principal não chama o subconjunto de "total recebido"', () => {
  const ctx = buildDashboardCountContexts(SCENARIO);
  // O número priorizado (437) nunca aparece rotulado como recebido/total.
  assert.ok(!/437\s*(recebidos|total)/i.test(ctx.monitored));
  // O rótulo evita "monitorados/total" ambíguo.
  assert.equal(DASHBOARD_MONITORED_LABEL, 'Editais priorizados');
  assert.match(ctx.monitoredLabel, /priorizados/i);
});

test('subtexto cita o total recebido quando catalogEditais existe', () => {
  const ctx = buildDashboardCountContexts(SCENARIO);
  assert.ok(ctx.monitored.includes('1.051'));
  assert.match(ctx.monitored, /De 1\.051 recebidos/);
});

test('quando catálogo == priorizado, não usa "De X" (sem contradição)', () => {
  const ctx = buildDashboardCountContexts({
    totalEditais: 1051,
    catalogEditais: 1051,
    prazoConfirmado: 10,
  });
  assert.match(ctx.monitored, /1\.051 recebidos no catálogo/);
  assert.ok(!/De 1\.051 recebidos/.test(ctx.monitored));
});

test('sem catalogEditais, contexto continua renderizando sem quebrar', () => {
  const ctx = buildDashboardCountContexts({ totalEditais: 437, prazoConfirmado: 6 });
  assert.equal(typeof ctx.monitored, 'string');
  assert.ok(ctx.monitored.length > 0);
  assert.match(ctx.monitored, /subconjunto priorizado do Dashboard/);
  assert.ok(!/recebidos no catálogo/.test(ctx.monitored));
});

test('objeto vazio não quebra', () => {
  const ctx = buildDashboardCountContexts();
  assert.equal(typeof ctx.monitored, 'string');
  assert.equal(typeof ctx.total, 'string');
  assert.equal(typeof ctx.open, 'string');
});

test('mantém compatibilidade: total, open, expiring, reports', () => {
  const ctx = buildDashboardCountContexts(SCENARIO);
  assert.match(ctx.total, /com prazo confirmado/);
  assert.match(ctx.open, /sem prazo estruturado/);
  assert.match(ctx.expiring, /vencem em até 30 dias/);
  assert.equal(ctx.reports, 'Fila local em dia');
});

test('texto de ajuda menciona catálogo completo vs subconjunto priorizado', () => {
  assert.match(DASHBOARD_COUNT_HELP_TEXT, /subconjunto priorizado/i);
  assert.match(DASHBOARD_COUNT_HELP_TEXT, /catálogo completo/i);
  assert.match(DASHBOARD_COUNT_HELP_TEXT, /tela de Editais/i);
});

test('truncated adiciona nota de amostra', () => {
  const ctx = buildDashboardCountContexts(SCENARIO, { truncated: true });
  assert.match(ctx.monitored, /amostra da base/);
});

/**
 * Matriz de fluxos de smoke test (DESKTOP QA 1.0).
 *
 * Fonte única de verdade consumida pelos specs Playwright (Web E2E) e pela
 * documentação. Cada fluxo descreve rota, ações e prioridade.
 *
 * kinds suportados:
 *  - expectText        { text }
 *  - expectTextRegex   { regex }
 *  - expectNoText      { text }
 *  - expectAnyText     { texts: [] }
 *  - click             { label }            (por texto acessível)
 *  - clickTestId       { testId }
 *  - clickFirstCard    {}                    (primeiro data-testid="edital-card")
 *  - expectNoFatalError {}                   (sem "Não foi possível carregar")
 *  - expectUrlRegex    { regex }
 */

export const FATAL_ERROR_TEXTS = [
  'Não foi possível carregar',
  'Não foi possível carregar os dados do edital',
  'Edital não encontrado',
];

export const SMOKE_FLOWS = [
  {
    id: 'dashboard-load',
    route: '/',
    priority: 'P0',
    actions: [
      { kind: 'expectText', text: 'Dashboard' },
      { kind: 'expectNoText', text: 'Não foi possível carregar' },
      { kind: 'clickTestId', testId: 'dashboard-refresh-button' },
      { kind: 'expectNoFatalError' },
    ],
  },
  {
    id: 'editais-list-load',
    route: '/editais',
    priority: 'P0',
    actions: [
      { kind: 'expectAnyText', texts: ['Editais Disponíveis', 'Editais'] },
      { kind: 'expectTextRegex', regex: 'Mostrando .* recebidos' },
      { kind: 'expectNoFatalError' },
    ],
  },
  {
    id: 'open-first-edital-detail',
    route: '/editais',
    priority: 'P1',
    actions: [
      { kind: 'clickFirstCard' },
      { kind: 'expectNoText', text: 'Não foi possível carregar os dados do edital' },
      { kind: 'expectAnyText', texts: ['Informações Gerais', 'Voltar', 'Documentos'] },
    ],
  },
  {
    id: 'report-problem-opens',
    route: '/',
    priority: 'P1',
    actions: [
      { kind: 'clickTestId', testId: 'report-problem-button' },
      { kind: 'expectText', text: 'Reportar problema' },
      { kind: 'expectAnyText', texts: ['Ambiente detectado', 'print', 'detalhes'] },
    ],
  },
];

/** @returns {typeof SMOKE_FLOWS} */
export function getSmokeFlows() {
  return SMOKE_FLOWS;
}

/** @param {string} priority */
export function getSmokeFlowsByPriority(priority) {
  return SMOKE_FLOWS.filter((f) => f.priority === priority);
}

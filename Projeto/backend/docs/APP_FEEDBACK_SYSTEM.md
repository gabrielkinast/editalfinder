# Sistema universal de feedback — EditalFinder (`app_feedback`)

## Objetivo

Permitir que o usuário reporte problemas da **aplicação** (telas, erros globais, API, UX) de forma separada do reporte de **edital** (`edital_feedback`).

## Tabelas

| Tabela | Uso |
|--------|-----|
| `public.edital_feedback` | Problema em uma oportunidade/edital específica |
| `public.app_feedback` | Problema da app (página, botão, erro global, lentidão) |

SQL opcional: [`sql/CREATE_APP_FEEDBACK.sql`](./sql/CREATE_APP_FEEDBACK.sql)

## Frontend

| Peça | Caminho |
|------|---------|
| Payload + sanitização | `src/utils/feedback/buildAppFeedbackPayload.js` |
| Service | `src/services/appFeedbackService.js` |
| Contexto global | `src/contexts/AppFeedbackContext.jsx` |
| Modal | `src/components/feedback/AppFeedbackModal.jsx` |
| Botão | `src/components/feedback/AppReportProblemButton.jsx` |
| Toast com ação | `src/components/feedback/AppFeedbackToast.jsx` |
| Error boundary | `src/components/common/AppErrorBoundary.jsx` |
| Estado vazio/erro | `src/components/common/EmptyOrErrorState.jsx` |
| Erros globais | `src/utils/errors/globalErrorReporter.js` |
| Erros de ação | `src/utils/errors/reportableActionError.js` |

## Camadas de captura

1. **AppErrorBoundary** — erros de renderização React (rotas em `router/index.jsx`).
2. **GlobalErrorReporter** — `window.error` e `unhandledrejection` (instalado em `AppFeedbackProvider`).
3. **handleAppActionError** — falhas controladas (toast + contexto para modal).
4. **Botão manual** — header “Reportar problema” (`origem: user_report`).

## Sanitização

- Stack e comentário truncados.
- Tokens/JWT redigidos.
- `extras.localStorageKeysRelevant`: **somente nomes de chaves**, nunca valores.
- Fila offline: `localStorage` `app_feedback_pending` se Supabase falhar.

## Uso em nova página

```jsx
import AppReportProblemButton from '../components/feedback/AppReportProblemButton';
import { handleAppActionError } from '../utils/errors/reportableActionError';
import EmptyOrErrorState from '../components/common/EmptyOrErrorState';

// Botão manual
<AppReportProblemButton origem="minha_pagina" pagina="minha_pagina" tipo="outro" />

// Erro de ação
try {
  await saveSomething();
} catch (e) {
  handleAppActionError({
    origem: 'api_error',
    pagina: 'minha_pagina',
    acao: 'salvar',
    error: e,
    userMessage: 'Não foi possível salvar.',
  });
}

// Lista vazia por falha
<EmptyOrErrorState
  title="Falha ao carregar"
  message="Não foi possível buscar os dados."
  origem="api_error"
  pagina="minha_pagina"
  error={err}
  onRetry={reload}
/>
```

Rotas principais já usam `withAppErrorBoundary(origem, pagina, element)` em `src/router/index.jsx`.

## Não misturar com edital

No card de edital: **“Reportar problema no edital”** → `edital_feedback`.  
No header / erro de tela: **“Reportar problema”** → `app_feedback`.

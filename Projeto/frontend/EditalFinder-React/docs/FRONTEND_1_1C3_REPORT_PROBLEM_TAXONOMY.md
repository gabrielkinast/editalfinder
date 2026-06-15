# FRONTEND 1.1C.3 — Report Problem Taxonomy + Desktop/EXE

## Objetivo

Melhorar o modal **Reportar problema** (feedback geral da aplicação) com taxonomia ampliada, categorias Desktop/EXE e contexto automático de runtime (Web vs Tauri).

**Não altera** `edital_feedback` (reporte por edital).

## Taxonomia

Definida em `src/constants/appFeedbackConfig.js` como `APP_FEEDBACK_PROBLEM_TYPES`:

| value | label (resumo) | group |
|-------|----------------|-------|
| `page_broken` | Erro na página / tela quebrou | app |
| `browser_error` | Erro inesperado no navegador | app |
| `desktop_exe_error` | Erro no aplicativo desktop / EXE | desktop |
| `desktop_open_link_error` | Desktop/EXE: link, PDF ou inscrição não abriu | desktop |
| `desktop_startup_error` | Desktop/EXE: erro ao abrir o aplicativo | desktop |
| `desktop_update_install_error` | Desktop/EXE: instalação ou atualização | desktop |
| `save_load_error` | Falha ao carregar ou salvar dados | data |
| `wrong_data` | Dado incorreto na tela | data |
| `button_action_error` | Botão ou ação não funcionou | ui |
| `visual_layout_problem` | Problema visual / layout | ui |
| `pdf_export_error` | Erro ao gerar ou exportar PDF | export |
| `spreadsheet_export_error` | Erro ao exportar planilha | export |
| `filter_search_error` | Filtro, busca ou ordenação | ui |
| `performance_slow` | Lentidão ou travamento | performance |
| `login_auth_error` | Erro de login ou permissão | auth |
| `other` | Outro | other |

Tipos legados (`erro_pagina`, `botao_nao_funciona`, …) são convertidos automaticamente via `appFeedbackTaxonomy.js`.

## Detecção de ambiente

`src/utils/feedback/runtimeContext.js` — `getRuntimeContext()`:

- `window.__TAURI__` / `window.__TAURI_INTERNALS__` ou build Tauri (`IS_TAURI_BUILD`)
- Retorna `runtime`: `desktop_tauri` | `web_browser`, mais `user_agent`, `platform`, `language`

O modal exibe: **Ambiente detectado: Desktop/EXE** ou **Navegador**.

## Payload

`buildAppFeedbackPayload()` inclui:

- `tipo`, `tipo_label`, `categoria` (group)
- `runtime`, `platform_context`, `is_desktop`
- `tipo_feedback` — valor legado para INSERT em `app_feedback` (CHECK SQL)
- Campos anteriores: `descricao`, `rota`, `pagina_url`, `app_version`, `metadata`, …

## E-mail (Edge Function)

`backend/supabase/functions/_shared/appFeedbackEmailLogic.js`:

- Assunto: `[EditalFinder] Reporte — Navegador|Desktop/EXE — /rota` (ou `PDF export` para `pdf_export_error`)
- Corpo destaca tipo, categoria, ambiente, rota, descrição e `platform_context`

Prioridade de envio (inalterada desde 1.1C.2): e-mail → `app_feedback` opcional → fila local.

## Fila local

Chave: `editalfinder:app_feedback_queue:v1`

`normalizeQueuedFeedback()` preenche `tipo`, `tipo_label`, `categoria`, `runtime` em itens antigos sem apagar dados existentes.

## Testes

```bash
cd frontend/EditalFinder-React
npm test
npm run build
```

Cobertura: taxonomia desktop, payload, runtime mock, e-mail, fila legada.

## Teste manual

### Navegador

1. `npm run dev`
2. Abrir **Reportar problema**
3. Ver badge **Navegador** e lista com opções Desktop/EXE
4. Enviar com descrição ≥ 10 caracteres
5. DevTools → Application → `editalfinder:app_feedback_queue:v1` se remoto falhar

### Desktop/EXE

1. Build Tauri ou portable EXE
2. Repetir fluxo; badge deve mostrar **Desktop/EXE**
3. Testar tipo `desktop_open_link_error` após falha de link externo

## Limitações

- PDF export não é corrigido neste patch; apenas categoria de reporte
- `app_feedback.tipo_feedback` no Supabase continua com valores legados (mapeamento no frontend)
- Sem nova tabela/migration/RLS

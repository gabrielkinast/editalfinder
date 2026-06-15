# FRONTEND 1.1C.3 — Mailto Support Feedback + Report Problem Taxonomy

## Fluxo principal

O **Reportar problema** (feedback geral da app) usa **`mailto:`** como canal principal:

1. Usuário abre o modal, escolhe o tipo e descreve o problema.
2. Ao clicar **Enviar**, o app monta o payload e abre o cliente de e-mail do sistema.
3. Destinatário fixo: **Suporte.EditalFinder@gmail.com**
4. Assunto e corpo vêm preenchidos; o usuário **revisa e envia manualmente**.
5. Se `mailto:` falhar → relatório vai para a fila local `editalfinder:app_feedback_queue:v1`.

**Não há** envio automático de e-mail pelo frontend, senha Gmail, API key Resend ou `VITE_*` com segredo.

## Por que mailto (e não Resend no frontend)

| Abordagem | Segredo no app? |
|-----------|-----------------|
| `mailto:` | Não — o cliente de e-mail do usuário envia |
| Resend / SMTP no React/Tauri | Sim — qualquer `VITE_*` ou string no bundle pode ser extraída |

### Nota de segurança

- `.gitignore` evita **commitar** arquivos; **não protege** segredos embutidos no build final.
- Variáveis `VITE_*` entram no bundle do Vite.
- Código em React/Tauri pode ser inspecionado no EXE ou no DevTools.
- Envio automático exige backend (Edge Function). Mantida como **opcional/futura**, não prioridade.

## Implementação

| Arquivo | Função |
|---------|--------|
| `src/utils/feedback/appFeedbackMailto.js` | `buildSupportMailtoUrl`, `openSupportMailto` |
| `src/services/appFeedbackService.js` | `submitAppFeedback` — mailto → local |
| `src/utils/feedback/appFeedbackSubmitFlow.js` | Orquestração testável |
| `src/constants/appFeedbackConfig.js` | Taxonomia + mensagens UX |
| `src/utils/feedback/runtimeContext.js` | Web vs Desktop/Tauri |

### Prioridade de `submitAppFeedback`

1. Validar payload  
2. `openSupportMailto(payload)`  
3. Sucesso → `status: opened_email_client`  
4. Falha → `saveAppFeedbackLocal` → `status: saved_local`  

Edge Function `send-app-feedback-email` e tabela `app_feedback` **permanecem no repo** mas **não são chamados** no fluxo principal.

## Taxonomia

`APP_FEEDBACK_PROBLEM_TYPES` — 16 tipos, incluindo Desktop/EXE:

- `desktop_exe_error`, `desktop_open_link_error`, `desktop_startup_error`, `desktop_update_install_error`
- `pdf_export_error`, `page_broken`, `browser_error`, …

## Ambiente

`getRuntimeContext()` detecta `window.__TAURI__` → `desktop_tauri`, senão `web_browser`.

O modal mostra: **Ambiente detectado: Desktop/EXE** ou **Navegador**.

Payload inclui: `tipo`, `tipo_label`, `categoria`, `runtime`, `platform_context`, `is_desktop`, etc.

## Fila local

- Chave: `editalfinder:app_feedback_queue:v1`
- `normalizeQueuedFeedback()` preenche campos novos em itens antigos
- `flushPendingAppFeedback()` tenta reabrir `mailto:` para itens pendentes

## Testes

```bash
cd frontend/EditalFinder-React
npm test
npm run build
```

`appFeedbackMailto.test.js` cobre URL, assunto, corpo, redação de segredos e fluxo submit/flush.

## Teste manual

### Navegador

1. `npm run dev`
2. Reportar problema → preencher → Enviar
3. Deve abrir Gmail/Outlook com **Suporte.EditalFinder@gmail.com**, assunto `[EditalFinder] Reporte — …` e corpo preenchido

### Desktop (Tauri)

1. `npm run desktop:dev`
2. Repetir; badge **Desktop/EXE**; mailto via plugin opener

### Falha mailto

- Bloquear handlers de mailto ou ambiente headless → mensagem de salvamento local e entrada na fila no DevTools → Application → Local Storage

## Limitações

- Tamanho do `mailto:` limitado (~7k URL); corpo/metadata são truncados/resumidos
- Flush de fila pode abrir vários clientes de e-mail (um por item)
- Usuário precisa confirmar envio no cliente de e-mail
- Não substitui `edital_feedback` (reporte por edital)

## Relacionado

- FRONTEND 1.1C — fila local resiliente  
- FRONTEND/BACKEND 1.1C.2 — Edge Function Resend (opcional)  
- `docs/FRONTEND_1_1C3_REPORT_PROBLEM_TAXONOMY.md` — detalhes da taxonomia (se existir)

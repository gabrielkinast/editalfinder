# FRONTEND 1.1C.3-HOTFIX — Restore App Render After Feedback Mailto Patch

## Sintoma

EXE/Tauri com janela vazia/azul (webview sem React).

## Causas

1. **Vite `base: '/'` no build Tauri** (principal no EXE) — `index.html` referenciava `/assets/*.js`, que o webview não resolve → React não monta → tela azul escura (`#0f172a` do tema ou fundo vazio). **Correção:** `base: './'` quando `TAURI_ENV_PLATFORM` está definido.
2. **`window.location.href = mailto:...`** em `openSupportMailto` — webview navegava para `mailto:` (corrigido em 1.1C.3-HOTFIX).
3. **Flush de fila no startup** — mailto automático ao abrir o app (corrigido em 1.1C.3-HOTFIX).

## Correção

- Removido fallback `location.href` em `appFeedbackMailto.js`; Tauri usa só `@tauri-apps/plugin-opener`.
- Removido flush automático na montagem; flush só ao abrir o modal “Reportar problema” (best-effort com `.catch`).
- `getRuntimeContext()` com guards `hasWindow` / `hasNavigator`.
- `submitFeedback` e instalação do error reporter envolvidos em try/catch.
- Flag `ENABLE_APP_FEEDBACK_MAILTO` (emergência) em `appFeedbackConfig.js`.

## Validação

```bash
cd frontend/EditalFinder-React
npm test
npm run desktop:release
```

Confirme em `dist/index.html` após o build Tauri:

```html
<script src="./assets/index-xxxxx.js">
```

(não `/assets/...`)

Instale o **novo** `releases/EditalFinder_v*_Windows_x64_Setup.exe` — o EXE antigo continua quebrado até rebuild.

Limpar fila pendente se necessário: DevTools → Application → `editalfinder:app_feedback_queue:v1` → `[]`.

# FRONTEND 1.1C.4 — Gmail Web Compose para reporte de problema

## Contexto

O patch **1.1C.3** usava `mailto:` para abrir o cliente de e-mail do sistema. No **Windows/Tauri**, isso frequentemente:

- abre apenas o navegador sem compor o e-mail;
- não abre o Gmail com destinatário/assunto/corpo preenchidos;
- falha silenciosamente no WebView2.

## Solução (1.1C.4)

O fluxo principal passa a usar **Gmail Web Compose** via URL HTTPS:

```
https://mail.google.com/mail/?view=cm&fs=1&to=Suporte.EditalFinder@gmail.com&su=...&body=...
```

### Ordem de fallback

1. **Gmail Web Compose** (`openExternalUrl` → navegador padrão / Tauri opener)
2. **mailto:** (somente com `allowMailto: true` em `openExternalUrl`)
3. **localStorage** — fila `editalfinder:app_feedback_queue:v1`

### Destinatário fixo

`Suporte.EditalFinder@gmail.com`

O usuário **sempre** revisa a mensagem e clica em **Enviar** no Gmail ou no cliente de e-mail. O app **não** envia e-mail automaticamente.

## Segurança

- **Sem** senha Gmail no frontend.
- **Sem** API key / Resend no fluxo principal.
- Corpo e assunto passam por `sanitizePayloadForSupportEmail` (redação de tokens, chaves, senhas).
- Corpo truncado (~6000 caracteres) para evitar URL excessivamente longa.

## Arquivos principais

| Arquivo | Papel |
|---------|--------|
| `src/utils/feedback/appFeedbackMailto.js` | `buildGmailComposeUrl`, `openSupportEmailComposer` |
| `src/utils/externalActions/openExternalUrl.js` | Abre HTTPS e mailto (com flag) |
| `src/utils/feedback/appFeedbackSubmitFlow.js` | Orquestra Gmail → mailto → local |
| `src/constants/appFeedbackConfig.js` | Mensagens de UX |

## Edge Function / Resend

Permanecem **opcionais/futuros**. Não são chamados no submit do modal.

## Validação manual (EXE)

1. `npm run desktop:release:quick`
2. Instalar o Setup em `releases/`
3. Abrir **Reportar problema**, preencher e enviar
4. Confirmar que o **navegador abre o Gmail** com `to`, assunto `[EditalFinder] Reporte — …` e corpo preenchidos
5. Se Gmail falhar (sem rede/conta), verificar fallback mailto ou painel de cópia local

## Comandos

```bash
cd frontend/EditalFinder-React
npm test
npm run build
npm run build:tauri
```

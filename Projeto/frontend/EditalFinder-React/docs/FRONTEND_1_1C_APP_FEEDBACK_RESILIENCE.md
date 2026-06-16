# FRONTEND 1.1C — App feedback / Reportar problema (resiliência)

## Bug observado

O modal **Reportar problema** abria, mas ao enviar exibia:

> Não foi possível enviar o relatório agora. Tente novamente.

Mesmo quando a fila local já existia, o service retornava `ok: false` com `pending: true`, e a UI tratava como erro fatal.

## Causa técnica

- Insert em `app_feedback` falha no staging (**PGRST205** — tabela não exposta no PostgREST).
- `createAppFeedback` salvava em `localStorage`, mas retornava **`ok: false`**, fazendo o modal mostrar erro.
- Payload e fila estavam acoplados ao service sem classificação de erro remoto.

## app_feedback vs edital_feedback

| Fluxo | Tabela | Service | Fallback local |
|-------|--------|---------|----------------|
| **App / Reportar problema** | `app_feedback` (não exposta no staging) | `appFeedbackService.submitAppFeedback` | Sim — fila v1 |
| **Problema em edital** | `edital_feedback` (exposta) | `editalFeedbackService` | Não alterado neste patch |

Não misturar os dois fluxos.

## Arquitetura (atualizada — 1.1C.2)

```
UI (AppFeedbackModal)
  → submitAppFeedback()
       1. sendAppFeedbackEmail → Edge Function send-app-feedback-email → editalfinder@gmail.com
       2. (opcional) sendAppFeedbackRemote → app_feedback
       3. saveAppFeedbackLocal → editalfinder:app_feedback_queue:v1
```

Ver também: `backend/docs/backend/APP_FEEDBACK_EMAIL_DELIVERY.md`

### Resultado padronizado

| status | ok | UX |
|--------|-----|-----|
| `sent_email` | true | **Principal** — enviado para a equipe por e-mail |
| `sent_remote` | true | Fallback Supabase (se e-mail falhar) |
| `saved_local` | true | Sucesso parcial — fila local |
| `invalid_payload` | false | Corrigir campos |
| `failed` | false | Erro real (auth, localStorage, etc.) |

## Fila local

- **Chave:** `editalfinder:app_feedback_queue:v1`
- **Legado migrado de:** `app_feedback_pending`
- **Limite:** 50 entradas
- **Estrutura:** `{ id_local, payload, saved_at, attempts, last_error_reason }`

## Retry

`flushPendingAppFeedback()` tenta **e-mail primeiro**; item só sai da fila após e-mail OK.

Roda ao autenticar e ao abrir o modal (silencioso).

## Arquivos

| Arquivo | Papel |
|---------|--------|
| `src/utils/feedback/appFeedbackPayload.js` | Payload, validação, map remoto |
| `src/utils/feedback/appFeedbackQueue.js` | Fila localStorage |
| `src/utils/feedback/postgrestFeedbackErrors.js` | Classificação PGRST205/rede/RLS |
| `src/services/appFeedbackService.js` | `submitAppFeedback`, flush, remote |
| `src/contexts/AppFeedbackContext.jsx` | Integração UI |
| `src/components/feedback/AppFeedbackModal.jsx` | Mensagens sucesso/erro |

## Testes

```bash
npm test
```

Inclui `src/utils/feedback/appFeedback.test.js`.

## Validação manual

1. Web ou EXE → Reportar problema → descrever (≥10 caracteres) → Enviar.
2. Se `app_feedback` indisponível → mensagem de **salvo localmente** (não erro fatal).
3. DevTools → Application → Local Storage → `editalfinder:app_feedback_queue:v1`.
4. Descrição curta → validação inline, sem envio.
5. Detalhe de edital → **Reportar problema neste edital** → fluxo `edital_feedback` intacto.

## Limitações

- Fila local não sincroniza entre dispositivos.
- Sem tela admin para pendentes.
- Flush só reenvia quando remoto estiver disponível e usuário autenticado.

## Recomendação futura

1. Expor `public.app_feedback` no Supabase staging com RLS de insert autenticado.
2. Painel admin para fila remota + pendentes locais (opcional export).
3. Edge Function para e-mail em casos críticos.

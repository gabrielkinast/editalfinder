# APP FEEDBACK — entrega por e-mail (1.1C.2)

## Objetivo

O feedback **geral** do app (“Reportar problema”) deve chegar principalmente ao e-mail da equipe:

**`editalfinder@gmail.com`** (configurável via `FEEDBACK_EMAIL_TO`).

Persistência em `app_feedback` é **opcional**. O frontend **nunca** envia e-mail diretamente.

## Canais

| Canal | Uso |
|-------|-----|
| **Edge Function `send-app-feedback-email`** | Principal — envia e-mail via Resend |
| **`app_feedback` (Supabase)** | Best-effort após e-mail OK, ou fallback se e-mail falhar |
| **Fila local** `editalfinder:app_feedback_queue:v1` | Se e-mail e Supabase falharem |

## Edge Function

**Path:** `backend/supabase/functions/send-app-feedback-email/index.ts`

**Endpoint:** `POST /functions/v1/send-app-feedback-email`

**Lógica compartilhada:** `backend/supabase/functions/_shared/appFeedbackEmailLogic.js`

### Variáveis de ambiente (Supabase secrets)

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `RESEND_API_KEY` | Sim (para envio real) | API key do Resend |
| `FEEDBACK_EMAIL_TO` | Não | Destino (default: `editalfinder@gmail.com`) |
| `FEEDBACK_EMAIL_FROM` | Não | Remetente verificado no Resend |
| `SUPPORT_EMAIL` | Não | Alias legado para destino |

**Não commitar** API keys, senhas Gmail ou service role no repositório.

### Deploy

Com Supabase CLI configurado no projeto:

```bash
cd backend/supabase
supabase secrets set RESEND_API_KEY=re_xxxx FEEDBACK_EMAIL_TO=editalfinder@gmail.com FEEDBACK_EMAIL_FROM="EditalFinder <noreply@seudominio.com>"
supabase functions deploy send-app-feedback-email
```

Sem CLI: criar a função no Dashboard Supabase e definir secrets manualmente.

## Frontend

**Service:** `src/services/appFeedbackService.js`

```js
submitAppFeedback()  // prioridade: e-mail → Supabase → local
sendAppFeedbackEmail() // supabase.functions.invoke('send-app-feedback-email')
flushPendingAppFeedback() // reenvia fila só após e-mail OK
```

**Nenhuma** variável `VITE_*` de e-mail/SMTP no frontend.

## Respostas UX

| status | Mensagem |
|--------|----------|
| `sent_email` | Relatório enviado para a equipe… |
| `sent_remote` | Relatório registrado… (fallback Supabase) |
| `saved_local` | Relatório salvo localmente… |
| `failed` | Não foi possível salvar… |

## Diferença de `edital_feedback`

- **`edital_feedback`** — problema em edital específico; fluxo próprio (`editalFeedbackService`, função `report-edital-feedback`).
- **`app_feedback` / e-mail app** — problema geral da aplicação.

## Testes

```bash
cd frontend/EditalFinder-React
npm test
```

Inclui testes de orquestração (`appFeedbackSubmitFlow.test.js`) e lógica da Edge Function (`appFeedbackEmailLogic.test.js`).

## Validação manual

1. Configurar secrets e fazer deploy da função.
2. App → Reportar problema → descrição ≥10 caracteres → Enviar.
3. Verificar caixa `editalfinder@gmail.com`.
4. Desligar `RESEND_API_KEY` → deve cair em fila local com mensagem amigável.
5. Reativar secret → abrir app (flush) ou reenviar pendente.

## Limitações

- Resend exige domínio/remetente verificado em produção.
- Fila local não sincroniza entre dispositivos.
- Sem painel admin de pendentes.

## Próximo passo recomendado

Expor tabela `app_feedback` no staging + RLS, e painel admin para histórico além do e-mail.

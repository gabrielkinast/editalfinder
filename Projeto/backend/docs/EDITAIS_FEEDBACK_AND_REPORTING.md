# Editais — Reporte de problemas (feedback manual)

**Status:** MVP ativo — INSERT em `public.edital_feedback` via Supabase (RLS). E-mail via Edge Function permanece opcional/futuro.

---

## Objetivo

Permitir que usuários autenticados (consultores e demais perfis com acesso à aba **Editais**) reportem manualmente itens problemáticos após a primeira curadoria global de ruído. O reporte **não** altera visibilidade, **não** deleta linhas e **não** dispara curadoria automática.

---

## Persistência (MVP)

Tabela: **`public.edital_feedback`**

Policies (exemplo em [`docs/sql/CREATE_EDITAL_FEEDBACK.sql`](./sql/CREATE_EDITAL_FEEDBACK.sql)):

- `edital_feedback_insert_own` — `authenticated` insere se `id_usuario` pertence ao `auth.uid()` via `public.usuario`
- `edital_feedback_select_own` — utilizador lê os próprios reportes

O front grava com **`appUser.id_usuario`** (bigint em `public.usuario`), **nunca** o UUID de `auth.users` na coluna `id_usuario`.

### Prioridade automática

| `tipo_feedback` | `prioridade` |
|-----------------|--------------|
| `link_quebrado`, `nao_e_oportunidade` | `alta` |
| Demais | `normal` |

### Validação SQL após envio

```sql
SELECT
  id_feedback,
  id_edital,
  id_usuario,
  tipo_feedback,
  comentario,
  status,
  prioridade,
  fonte_recurso,
  edital_titulo,
  criado_em
FROM public.edital_feedback
ORDER BY criado_em DESC
LIMIT 20;
```

---

## Fluxo de envio (`submitEditalFeedback`)

1. Monta payload (`buildEditalFeedbackPayload`).
2. Exige `appUser.id_usuario` válido; senão: *“Entre na sua conta para reportar problemas.”*
3. **Se** `VITE_EDITAL_FEEDBACK_ENDPOINT` estiver definido → POST para o endpoint (legado/opcional).
4. **Senão** → `INSERT` em `public.edital_feedback` via cliente Supabase anon + JWT da sessão.
5. Sucesso na UI: *“Obrigado! Seu reporte foi enviado para revisão.”*

Erro genérico (RLS, rede, etc.): *“Não foi possível enviar o reporte agora. Tente novamente.”*

---

## Variáveis de ambiente

| Variável | Uso |
|----------|-----|
| `VITE_SUPABASE_URL` + `VITE_SUPABASE_ANON_KEY` | Obrigatórios para INSERT |
| `VITE_EDITAL_FEEDBACK_ENDPOINT` | Opcional; se definido, tem **prioridade** sobre INSERT |
| `VITE_EDITAL_FEEDBACK_MOCK_DEV` | Só DEV, sem Supabase nem endpoint |
| `VITE_SUPPORT_EMAIL` | E-mail de suporte (template / Edge Function futura). Padrão: **`editalfinder@gmail.com`** |

Constante de fallback: `src/constants/editalFeedbackConfig.js` → `DEFAULT_SUPPORT_EMAIL`.

---

## E-mail de suporte

**Padrão do produto:** `editalfinder@gmail.com`

- Lido de `VITE_SUPPORT_EMAIL` ou fallback em `config/env.js`
- Incluído no corpo do template (`buildEditalFeedbackEmailBody`) como referência
- **MVP não envia e-mail** — apenas persiste na tabela

Edge Function futura (`supabase/functions/report-edital-feedback`): secret `SUPPORT_EMAIL=editalfinder@gmail.com`.

---

## Motivos (`tipo_feedback`)

| Label (UI) | Valor interno |
|------------|---------------|
| Link quebrado | `link_quebrado` |
| Não é edital/oportunidade | `nao_e_oportunidade` |
| Edital encerrado | `edital_encerrado` |
| Duplicado | `duplicado` |
| Informação incorreta | `informacao_incorreta` |
| Outro | `outro` |

---

## Logs DEV

Prefixo `[edital-feedback]`:

| Evento | Significado |
|--------|-------------|
| `submit_db_start` | INSERT iniciado |
| `submit_db_success` | INSERT OK (`id_feedback`) |
| `submit_db_error` | Falha Supabase (code, message, details, hint) |
| `missing_app_user` | Sem `id_usuario` na sessão app |
| `modal_open` / `modal_close_*` | UI do modal |

---

## Como testar

1. Login com utilizador que tenha linha em `public.usuario` (`id_usuario` na sessão).
2. Editais → **Reportar problema** → enviar.
3. Confirmar linha em `public.edital_feedback` (query acima).
4. Sem Supabase configurado: erro amigável (ou `VITE_EDITAL_FEEDBACK_MOCK_DEV=true` só em DEV).

---

## Limitações atuais

- Sem envio de e-mail automático.
- Sem fila admin no front.
- Um reporte não altera curadoria nem oculta edital.

---

## Ficheiros principais

| Ficheiro | Função |
|----------|--------|
| `src/services/editalFeedbackService.js` | INSERT Supabase + fallback endpoint |
| `src/components/editais/EditalFeedbackModal.jsx` | UI + `submitEditalFeedback(payload, { appUser })` |
| `src/constants/editalFeedbackConfig.js` | `DEFAULT_SUPPORT_EMAIL`, nome da tabela |
| `src/utils/edital/buildEditalFeedbackPayload.js` | Payload do formulário |

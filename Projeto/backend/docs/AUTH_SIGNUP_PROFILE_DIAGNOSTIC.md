# Cadastro (Criar conta) — Diagnóstico Auth + perfil interno

Documento para o fluxo **Criar conta** no EditalFinder React. Não altera regras de negócio de tipo/nível de utilizador (novos cadastros: `Consultor`, `nivel_acesso: 2`, `status: Ativo`).

---

## 1. Fluxo atual (após correção frontend)

| Passo | Onde | Ação |
|-------|------|------|
| UI | `pages/Login.jsx` (aba **Criar conta**) | Valida nome, e-mail, senha |
| Contexto | `contexts/AuthContext.jsx` → `register()` | Chama `authService.registerUser` |
| Auth | `services/authService.js` → `registerWithSupabaseAuth` | `supabase.auth.signUp` |
| Perfil | `createInternalProfileRow` | `INSERT` em `public.usuario` |
| Fallback login | `ensureInternalProfileFromAuthUser` | Após confirmação de e-mail ou login sem linha em `usuario` |

### Sequência corrigida

```
signUp(email, password)
  ├─ user.id ausente → erro
  ├─ session == null (confirmação de e-mail ativa)
  │     → NÃO faz INSERT (cliente anon → RLS bloqueia)
  │     → retorna pending_email_confirmation + mensagem clara
  │     → perfil deve ser criado por trigger SQL ou no 1º login com sessão
  └─ session com access_token
        → INSERT usuario (auth_user_id = user.id)
        ├─ OK → status complete → dashboard
        └─ falha → mensagem específica (RLS / duplicado); sem falso sucesso
```

---

## 2. Tabela de perfil interno

| Item | Valor |
|------|--------|
| Tabela | `public.usuario` |
| Ligação Auth | `auth_user_id` (UUID) = `auth.users.id` |
| ID app | `id_usuario` (serial/bigint) — usado em `cliente.id_usuario`, RLS |
| E-mail app | `nome_email` (único na prática) |
| Campos no signup | `nome`, `nome_email`, `auth_user_id`, `tipo_usuario`, `nivel_acesso`, `status` |
| Senha na tabela | **Não** gravada no fluxo Supabase Auth (legado DEV ainda lê `senha` em login antigo) |

Funções RLS dependentes: `public.current_app_user_id()`, `public.current_app_user_is_admin()` (ver `docs/sql/RLS_CLIENTE.sql`).

---

## 3. Erro observado (sintoma reportado)

**Mensagem:** “Conta criada no Auth, mas falhou ao criar o perfil interno.”

### Hipótese principal

`signUp` devolve `user` mas **`session` é `null`** quando **confirmação de e-mail** está ligada no Supabase.

O código antigo executava `INSERT` em `public.usuario` **antes** de verificar a sessão, com o cliente **anon** (sem JWT `authenticated`). As policies em `usuario` exigem `auth.uid() = auth_user_id` → **42501 / RLS**.

Efeitos colaterais do código antigo:

- `signOut()` após falha do INSERT (não remove o user de `auth.users` → **órfão**).
- Mensagem enganosa (parecia falha genérica, não “confirme o e-mail”).

### Hipóteses secundárias

- RLS em `usuario` sem policy `INSERT` para `authenticated` mesmo com sessão.
- `nome_email` ou `auth_user_id` duplicado (`23505`).
- Coluna obrigatória em falta no schema remoto (trigger/default ausente).

---

## 4. Policies necessárias (Opção B — referência)

Além do trigger (Opção A), para signup só com frontend:

```sql
-- Exemplo — ajustar ao schema real antes de aplicar
CREATE POLICY usuario_insert_own ON public.usuario
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = auth_user_id);
```

`SELECT`/`UPDATE` próprios: ver `docs/sql/SECURITY_RLS_EXAMPLES.sql`.

---

## 5. Correções aplicadas no frontend

1. **Sem sessão após signUp** → não insere perfil; mensagem de confirmação de e-mail; sem `signOut` desnecessário.
2. **Com sessão** → insert + retry após `refreshSession`.
3. **Erros RLS** → mensagem orientando admin (sem “sucesso completo”).
4. **`ensureInternalProfileFromAuthUser`** no login e no `AuthStateChange` (fallback se trigger SQL ainda não existir).
5. Logs DEV `[auth-signup]`: signUp, session, payload sem senha, erros Supabase completos.

---

## 6. Plano de correção definitiva (recomendado)

| Prioridade | Ação | Ficheiro |
|------------|------|----------|
| 1 | Trigger `handle_new_auth_user` em `auth.users` | `docs/sql/FIX_SIGNUP_PROFILE_CREATION.sql` |
| 2 | Policy `INSERT` own profile | mesmo SQL |
| 3 | Backfill órfãos (manual) | secção 4 do SQL |
| 4 | Staging: testar com e-mail confirm ON e OFF | checklist abaixo |

### Checklist staging

- [ ] Criar conta com confirmação **desligada** → login imediato + linha em `usuario`.
- [ ] Criar conta com confirmação **ligada** → mensagem de e-mail; após confirmar, login cria/acha perfil.
- [ ] Utilizador órfão em `auth.users` → backfill SQL → login OK.

---

## 7. Logs DEV

Filtrar no console: `[auth-signup]`

Fases: `signUp_start`, `signUp_result`, `signUp_pending_email`, `profile_insert_start`, `profile_insert_session`, `profile_insert_ok`, `profile_insert_error`, `signUp_complete`.

---

## 8. Confirmação de e-mail em produção

### Variáveis `.env` (frontend)

| Variável | Dev (exemplo) | Produção (obrigatório) |
|----------|---------------|-------------------------|
| `VITE_PUBLIC_SITE_URL` | `http://localhost:5173/editalfinder` | `https://seudominio.com/editalfinder` |
| `VITE_AUTH_CALLBACK_URL` | `http://localhost:5173/editalfinder/auth/callback` | `https://seudominio.com/editalfinder/auth/callback` |

Regra em `getAuthCallbackRedirectUrl()`:

1. Se `VITE_AUTH_CALLBACK_URL` existir → usa essa URL no `signUp` (`emailRedirectTo`).
2. Senão → `VITE_PUBLIC_SITE_URL` + `/auth/callback`.
3. Em **`import.meta.env.PROD`**, URLs com `localhost` são rejeitadas no log e substituídas pelo site público configurado.

**Nunca** fazer deploy de produção sem `VITE_PUBLIC_SITE_URL` / `VITE_AUTH_CALLBACK_URL` apontando para o domínio real — caso contrário o e-mail do Supabase pode gerar link para `localhost`.

### Supabase Dashboard → Authentication → URL Configuration

| Campo | Valor |
|-------|--------|
| **Site URL** | `https://seudominio.com/editalfinder` |
| **Redirect URLs** | `https://seudominio.com/editalfinder/auth/callback` |
| Dev (adicional) | `http://localhost:5173/editalfinder/auth/callback` |
| Staging (se houver) | `https://staging.seudominio.com/editalfinder/auth/callback` |

A URL do e-mail **só funciona** se estiver listada em **Redirect URLs**.

### Fluxo esperado (UX)

```
Criar conta → e-mail de confirmação
Link do e-mail → https://DOMINIO/editalfinder/auth/callback#access_token=... (ou ?code=)
AuthCallback.jsx (rota pública)
  → "Confirmando…" (máx. ~8s)
  → "E-mail confirmado com sucesso." + botão "Ir para login"
  → NÃO redireciona automaticamente ao dashboard
Login → mensagem "E-mail confirmado. Entre com sua conta."
```

### Motor Auth (SPA)

- `supabaseClient`: `flowType: 'implicit'`, `detectSessionInUrl: true`
- Hash `#access_token` tratado primeiro; `?code=` tenta PKCE com fallback amigável
- Erros técnicos (PKCE verifier, lock, flow state) **não** aparecem na UI
- Após confirmar: `signOut({ scope: 'local' })` para o utilizador entrar explicitamente no login
- URL limpa: `/editalfinder/auth/callback` (sem tokens na barra)

### Mensagens na UI

| Situação | Mensagem |
|----------|----------|
| Sucesso | E-mail confirmado com sucesso. |
| Sem sessão / PKCE | Seu e-mail foi confirmado. Faça login para continuar. |
| Timeout (~8s) | Não conseguimos finalizar automaticamente. Tente fazer login. |
| Link expirado | Este link de confirmação expirou ou já foi usado… |

### Logs DEV

| Prefixo | Eventos |
|---------|---------|
| `[auth-signup]` | `signUp_redirect` (+ `emailRedirectTo`, `isProd`, `containsLocalhost`) |
| `[auth-callback]` | `callback_start`, `has_code`, `has_hash_token`, `exchange_success`, `exchange_error`, `manual_login`, `timeout`, `redirect_to_login_clicked` |

Não logar: senha, `access_token`, `refresh_token`.

### Como testar

**Dev**

1. `.env.local` com URLs localhost (ver `.env.example`).
2. Supabase Redirect URLs inclui `http://localhost:5173/editalfinder/auth/callback`.
3. Criar conta → abrir link do e-mail → página de confirmação → **Ir para login** → login OK.

**Produção / staging**

1. Build com `VITE_AUTH_CALLBACK_URL` do domínio real (verificar no log `[auth-signup] signUp_redirect` que `containsLocalhost` é `false`).
2. Link do e-mail **não** deve conter `localhost`.
3. Página mostra sucesso ou orientação de login — nunca erro técnico cru.

---

## 9. Referências no repositório

- `frontend/EditalFinder-React/src/services/authService.js`
- `frontend/EditalFinder-React/src/services/authCallbackService.js`
- `frontend/EditalFinder-React/src/pages/AuthCallback.jsx`
- `frontend/EditalFinder-React/src/pages/Login.jsx`
- `frontend/EditalFinder-React/src/contexts/AuthContext.jsx`
- `frontend/EditalFinder-React/src/utils/authSignupDevLog.js`
- `frontend/EditalFinder-React/src/utils/authCallbackRoute.js`
- `frontend/EditalFinder-React/src/auth/authCallbackCoordinator.js`
- `docs/sql/FIX_SIGNUP_PROFILE_CREATION.sql` (**não executar automaticamente**)

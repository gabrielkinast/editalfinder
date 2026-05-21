# Migração para Supabase Auth

Este documento descreve a autenticação do EditalFinder (React): fluxo anterior, fluxo actual com **Supabase Auth** como fonte de sessão, e o papel de `public.usuario` como **perfil interno**.

## Fluxo antigo

- Credenciais eram validadas contra `public.usuario` (comparação directa do campo `senha`).
- O objecto de utilizador era guardado em `localStorage` (`editalFinderUser`) e tratado como sessão.
- Não havia integração com `auth.users` nem coluna `auth_user_id`.

## Fluxo novo

1. **Login:** `supabase.auth.signInWithPassword({ email, password })`.
2. Com `session.user.id`, o perfil é carregado em `public.usuario` onde `auth_user_id = session.user.id`.
3. Se não existir linha de perfil, a sessão Auth é terminada (`signOut`) e o utilizador vê: *«Perfil interno não encontrado para este usuário.»*
4. **Cadastro:** `supabase.auth.signUp` → `INSERT` em `public.usuario` com `auth_user_id`, `nome`, `nome_email`, `tipo_usuario = "Consultor"`, `nivel_acesso = 2`, `status = "Ativo"`. **Não** se grava `senha` na tabela neste fluxo.
5. O estado React (`AuthContext`) segue a **sessão Supabase**; `localStorage` serve apenas como **cache** (reidratação rápida / offline leve), não como fonte de autoridade em produção.

## Campo `auth_user_id`

- Liga cada linha de `public.usuario` ao UUID em `auth.users.id`.
- Todas as consultas de perfil pós-login usam este vínculo (`fetchProfileByAuthUserId` em `authService.js`).

## Criar conta (frontend público)

- Campos: nome, e-mail, senha, confirmar senha.
- Validações: nome obrigatório, e-mail válido, senha ≥ 6 caracteres, senhas iguais.
- O tipo **Administrador** não pode ser criado por esta rota; novos utilizadores são sempre **Consultor**, nível **2**, **Ativo**.

## Login

- Campos: e-mail e senha.
- Em primeiro lugar tenta-se sempre Supabase Auth quando o cliente está configurado.

### Confirmação de e-mail

Se o projecto Supabase exigir confirmação de e-mail, após `signUp` pode não haver `session`. Nesse caso o código faz `signOut`, limpa o cache e mostra uma mensagem a pedir que o utilizador confirme o e-mail (ou desactive a confirmação no painel Supabase para testes locais).

## Objecto de utilizador na app

Campos expostos (com aliases legados onde aplicável):

| Campo            | Notas                                      |
|-----------------|--------------------------------------------|
| `id_usuario`    | Chave interna do perfil                    |
| `auth_user_id`| UUID Supabase Auth                         |
| `nome`          |                                            |
| `nome_email`    | E-mail normalizado                         |
| `tipo_usuario`  | Alias: `tipo`                              |
| `nivel_acesso`  | Alias: `nivel`                             |
| `status`        |                                            |
| `email`         | Alias de `nome_email`                      |

## Fallback DEV (temporário)

Quando `import.meta.env.DEV === true` e o login Supabase falha:

1. Pode usar-se a conta demo `admin@finder.com` / `123456` (sem linha em Auth).
2. Pode usar-se **login legado**: leitura de `public.usuario` por `nome_email` e comparação com `senha` em texto (apenas para desenvolvimento).

**Em produção** não se deve depender da coluna `senha` em `public.usuario` para autenticação. Este fallback deve ser **removido** antes de endurecimento de produção.

## Limitações actuais

- Utilizadores antigos **sem** `auth_user_id` não entram via Supabase Auth até serem ligados a uma conta Auth (ou migrados).
- **RLS** restritiva ainda não está activa nesta fase; políticas futuras devem alinhar `auth.uid()` com `auth_user_id` em `usuario` e tabelas relacionadas.
- Não se usa `service_role` no frontend (apenas a chave `anon` / cliente público).

## Próximos passos (RLS e endurecimento)

1. Garantir que todos os perfis relevantes têm `auth_user_id` preenchido (script de migração / convites).
2. Activar políticas RLS em `public.usuario` e tabelas dependentes (`SELECT`/`UPDATE` onde `auth_user_id = auth.uid()`).
3. Remover fallback DEV (`tryLegacyDevLogin`, demo admin, `hydrateDevLegacyFromCache` em produção).
4. Opcional: triggers ou edge functions para criar perfil em `usuario` no primeiro `SIGNED_UP`, evitando duplicação entre cliente e servidor.

## Ficheiros relevantes

- `frontend/EditalFinder-React/src/services/authService.js` — login, registo, sessão, cache, fallback DEV.
- `frontend/EditalFinder-React/src/contexts/AuthContext.jsx` — estado React, `onAuthStateChange`, inicialização.
- `frontend/EditalFinder-React/src/pages/Login.jsx` — UI login / criar conta.

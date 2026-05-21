# Editais — favoritos (diagnóstico e correção)

**Data:** 2026-05-20  
**Escopo:** apenas módulo Editais (`public.edital_favorito` + estrela nos cards). Sem alteração em Notícias, Pesquisas, Concursos ou Radar.

---

## Causa raiz

As policies RLS em `public.edital_favorito` estavam **fixas em `id_usuario = 1`** (`edital_favorito_*_mvp`). Qualquer utilizador autenticado com `public.usuario.id_usuario` diferente de 1 não conseguia `INSERT`/`UPDATE`/`SELECT` dos próprios favoritos.

Sintoma na UI: estrela visível, clique sem efeito persistente (ou erro silencioso no PostgREST).

---

## Identidades (não misturar)

| Camada | Tipo | Uso |
|--------|------|-----|
| `auth.users.id` | UUID | Supabase Auth (`auth.uid()` nas policies) |
| `public.usuario.id_usuario` | BIGINT | FK em `edital_favorito.id_usuario` |
| `public.usuario.auth_user_id` | UUID | Liga perfil interno ao Auth |

O frontend deve enviar **`appUser.id_usuario`** (via `AuthContext` / `buildAppUser`), **nunca** `session.user.id` como `id_usuario`.

---

## Schema `public.edital_favorito` (resumo)

- PK: `id_favorito` (uuid)
- Chave lógica: `id_usuario` + (`id_edital` **ou** `edital_link`)
- Soft delete: `ativo = false`
- `alertar_com_dias` ∈ {1, 3, 7, 15, 30} (default **7** no insert)
- `alerta_ativo` default **false** no favoritar pela listagem

View de leitura: `public.vw_editais_favoritos_front` (lista; toggle grava na tabela base).

---

## Correção frontend

| Ficheiro | Alteração |
|----------|-----------|
| `src/hooks/useEditalFavorites.js` | Aguarda `authLoading`; só ativa remoto com `user.id_usuario`; UI otimista com rollback; logs `[favoritos]` |
| `src/services/favoritosService.js` | Payload insert/reactivate; toggle unfavorite / reactivate / insert; logs DEV |
| `src/pages/Dashboard.jsx` | Mensagem se não logado / sem perfil interno |
| `src/utils/edital/editalRowMapper.js` | Expõe `id_edital` no objeto do card |

Fluxo toggle:

1. Favorito ativo em cache → `UPDATE ativo=false`
2. Linha inativa na tabela → `UPDATE ativo=true` (reativar)
3. Sem linha → `INSERT`

Identificação do edital: `id_edital` (de `vw_editais_front` → `idNumerico` / `id_edital`) ou `edital_link` normalizado.

---

## Correção RLS (SQL manual)

Ficheiro: [`sql/FIX_EDITAL_FAVORITO_RLS.sql`](./sql/FIX_EDITAL_FAVORITO_RLS.sql)

Policies `*_own` com:

```sql
EXISTS (
  SELECT 1 FROM public.usuario u
  WHERE u.id_usuario = edital_favorito.id_usuario
    AND u.auth_user_id = auth.uid()
)
```

**Não executar automaticamente pelo repositório** — aplicar no SQL Editor do Supabase após revisão.

---

## Como testar

1. Aplicar `FIX_EDITAL_FAVORITO_RLS.sql` em staging.
2. Login com utilizador que tenha linha em `public.usuario` (`auth_user_id` preenchido).
3. Abrir **Editais** → clicar estrela em um card.
4. Recarregar: estrela preenchida.
5. Clicar de novo: desfavoritar; recarregar: estrela vazia.
6. No banco:

```sql
SELECT id_favorito, id_usuario, id_edital, edital_link, ativo, origem, contexto
FROM public.edital_favorito
WHERE id_usuario = <seu_id_usuario>
ORDER BY atualizado_em DESC
LIMIT 10;
```

7. Consola DEV: logs `[favoritos]` com `id_usuario`, `auth_user_id`, `action`, payload e erros Supabase (`code`, `message`, `details`, `hint`).

---

## Variáveis de ambiente

- `VITE_ENABLE_EDITAL_FAVORITOS=true` (default)
- `VITE_DEV_FAVORITOS_USER_ID` — opcional, só DEV, para testar sem Auth (não usar em produção)

---

## Documentos relacionados

- [`FRONTEND_BACKEND_CONTEXT.md`](./FRONTEND_BACKEND_CONTEXT.md) — views e módulos
- [`sql/FIX_SIGNUP_PROFILE_CREATION.sql`](./sql/FIX_SIGNUP_PROFILE_CREATION.sql) — perfil `public.usuario` após signup

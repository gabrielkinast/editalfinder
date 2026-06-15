# FRONTEND 1.1I — Cadastros Saved Edital Visibility Fix

**Data:** 2026-06-10  
**Contexto:** SECURITY 1.0B aplicado — INSERT admin em `public.edital` OK; registro aparece no banco mas não na aba **Cadastros → Editais**.

---

## 1. Sintoma

Após salvar edital manual como admin:

- INSERT confirmado no Supabase (`id_edital`, título, link).
- Tela **Cadastros → Editais** continua com **“Nenhum item encontrado.”**

---

## 2. Evidência SQL (staging)

```txt
id_edital: 2445
titulo: TESTE STAGING RLS ADMIN - 20260610
fonte_recurso: NULL
extras: {} (sem marcador manual)
```

RLS de escrita não é mais a causa — o registro persiste.

---

## 3. Causa encontrada

Combinação de fatores no frontend:

1. **Listagem sem critério de “cadastro manual”** — `getAllEditaisAdmin()` buscava `public.edital` sem filtrar marcadores; após o patch, a aba lista **apenas** editais manuais/complementares (não o catálogo inteiro do loader).
2. **Payload sem marcador** — `buildEditalWritePayload` não enviava `extras.manual_entry` nem fallback de `fonte_recurso`; registros novos eram indistinguíveis do catálogo e podiam ficar fora do critério da aba.
3. **`createEdital` sem RETURNING** — insert não devolvia a linha; após reload, se a query filtrada viesse vazia, a UI não tinha como manter o item recém-criado.
4. **Registro de teste pré-patch** — sem `extras`/`fonte_recurso` manual, não entra no filtro (esperado; sem migração de dados).

---

## 4. Mudança no payload manual

`buildEditalWritePayload(formData, { manualCadastro: true })` (usado em `createEdital` / `updateEdital`):

- Mescla `extras` existentes.
- Define marcadores:
  - `origem_cadastro: "manual_admin"`
  - `created_via: "cadastros_page"`
  - `manual_entry: true`

---

## 5. Fallback `fonte_recurso`

Se o usuário deixar fonte vazia → `fonte_recurso = "Cadastro Manual"`.  
Se informar (ex.: `"Teste Manual"`), preserva o valor.

---

## 6. `createEdital`

```js
.insert([row]).select(CREATE_EDITAL_RETURN_COLUMNS).single()
```

- Em erro → propaga para handler FRONTEND 1.1F (`processManualEditalSaveError`).
- Em sucesso → retorna objeto com `id_edital` e demais colunas listadas.

---

## 7. Listagem (`getAllEditaisAdmin`)

1. Query PostgREST com `.or()` nos marcadores manuais + `fonte_recurso = Cadastro Manual`.
2. Filtro client-side `isManualCadastroEdital()` como rede de segurança.
3. `mergeCadastrosEditalRows()` com `pinRows` — itens recém-salvos permanecem visíveis se o reload vier vazio.
4. Ordenação por `id_edital` descendente (mais recentes primeiro).

---

## 8. UI após salvar (`Cadastros.jsx`)

- Modal fecha **somente** após sucesso confirmado.
- `loadData({ pinRows: [savedRow] })` mescla o retorno do insert.
- Banner de sucesso com `id_edital` quando disponível.

---

## 9. Debug seguro

```js
localStorage.setItem('editalfinder:debug:cadastros', '1');
```

Logs:

- `[EditalFinder][Cadastros] create payload keys`
- `[EditalFinder][Cadastros] insert success id_edital`
- `[EditalFinder][Cadastros] reload list count`
- `[EditalFinder][Cadastros] list filters`

Não loga tokens, keys ou senhas.

---

## 10. Teste manual

1. Login admin → **Cadastros → Editais**.
2. Criar edital (fonte vazia ou “Teste Manual”).
3. Salvar → item na tabela + banner de sucesso.
4. SQL:

```sql
select id_edital, titulo, link, fonte_recurso, orgao_responsavel, extras, criado_em
from public.edital
where link = 'https://example.com/teste-front-cadastros-visibility-20260610';
```

Esperado: `extras.manual_entry = true`, `extras.created_via = cadastros_page`, `fonte_recurso` preenchido.

---

## 11. Limitações

- Editais manuais **antes** deste patch (sem marcador) não aparecem até backfill SQL opcional.
- Se `authenticated` não tiver policy SELECT em `public.edital`, o reload remoto pode vir vazio — o **pin** do insert mantém visibilidade imediata; correção definitiva de leitura é policy no banco (fora deste patch).
- A aba **não** lista o catálogo completo do loader — só cadastros manuais/complementares.

---

## 12. Próximo patch recomendado

- **SECURITY 1.0C** (opcional): `edital_admin_select` para admin + backfill `extras` em registros manuais legados.
- **FRONTEND 1.1J** (opcional): toast dismissível, coluna “Origem” na tabela, link para `/edital/:id`.

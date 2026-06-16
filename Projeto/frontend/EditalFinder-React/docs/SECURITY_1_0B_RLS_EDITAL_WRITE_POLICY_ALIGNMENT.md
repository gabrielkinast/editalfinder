# SECURITY 1.0B — RLS Edital Admin Write + Select Policy Alignment

**Data:** 2026-06-10  
**Tipo:** Migration + documentação + testes estáticos  
**Status:** **Aplicada em staging** (INSERT/UPDATE + hotfix SELECT `edital_admin_select`)

---

## 1. Problema

Usuário admin no EXE/Tauri recebia erro de policy/RLS ao cadastrar edital manual em `/cadastros`. Após apply inicial (INSERT/UPDATE), o INSERT passou mas o retorno `.insert().select().single()` e a listagem **Cadastros → Editais** falhavam sem policy SELECT para `authenticated` admin.

## 2. Diagnóstico do SECURITY 1.0A (confirmado)

| Item | Conclusão |
|------|-----------|
| Auth | Supabase Auth + perfil `public.usuario` via `auth_user_id` |
| Admin UI | `tipo_usuario` Administrador/Admin ou `nivel_acesso = 1` |
| Write path | `supabase.from('edital').insert([row]).select().single()` — sem `service_role` |
| Schema `edital` | Sem `created_by` / `id_usuario` |
| Policies versionadas | RLS ON; sem INSERT/SELECT `authenticated` canónico; loader usa `service_role` |

## 3. Estado após apply (staging)

| Operação | Role | Quem |
|----------|------|------|
| SELECT | **authenticated** | Apenas `current_app_user_is_admin() = true` (`edital_admin_select`) |
| SELECT | anon / service_role | Conforme policies legadas (preservadas) |
| INSERT | **authenticated** | Apenas admin (`edital_admin_insert`) |
| UPDATE | **authenticated** | Apenas admin (`edital_admin_update`) |
| DELETE | — | **Não liberado** neste patch |
| INSERT/UPDATE/SELECT admin | anon | **Bloqueado** (sem policy admin para anon) |

### Hotfix SELECT (aplicado manualmente no Supabase)

```sql
CREATE POLICY edital_admin_select
ON public.edital
FOR SELECT
TO authenticated
USING (public.current_app_user_is_admin());
```

**Motivo:** `createEdital` usa `.insert(...).select(...).single()` e `getAllEditaisAdmin` lê `public.edital`. Sem SELECT admin, INSERT passava mas RETURNING/listagem eram bloqueados por RLS.

A migration versionada (`20260610_security_1_0b_edital_admin_write_policy.sql`) foi atualizada para incluir esta policy de forma idempotente.

## 4. Teste manual confirmado (staging)

| Verificação | Resultado |
|-------------|-----------|
| Cadastro admin | **OK** — edital salvo com **ID 2448** |
| Listagem Cadastros → Editais | **OK** — item visível na tabela |
| Coluna Fonte | **OK** — exibiu `Cadastro Manual` (FRONTEND 1.1I) |
| Consultor não-admin | INSERT bloqueado (esperado) |

## 5. Queries manuais — confirmar cluster

Rodar no **Supabase SQL Editor** (staging/prod). Não colar resultados com PII em tickets públicos.

### 5.1 Policies atuais

```sql
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('edital', 'usuario', 'cliente', 'edital_feedback')
ORDER BY tablename, policyname;
```

Esperado em `edital` (mínimo):

- `edital_admin_select` — `SELECT`, `authenticated`, `USING (current_app_user_is_admin())`
- `edital_admin_insert` — `INSERT`, `authenticated`, `WITH CHECK (current_app_user_is_admin())`
- `edital_admin_update` — `UPDATE`, `authenticated`, `USING` + `WITH CHECK` admin

### 5.2 RLS ligado

```sql
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('edital', 'usuario', 'cliente', 'edital_feedback')
ORDER BY tablename;
```

### 5.3 Colunas `edital` / `usuario`

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'edital'
ORDER BY ordinal_position;
```

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'usuario'
ORDER BY ordinal_position;
```

### 5.4 Funções admin

```sql
SELECT routine_schema, routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name ILIKE '%admin%';
```

## 6. Migration proposta / versionada

**Arquivo:** `backend/migrations/20260610_security_1_0b_edital_admin_write_policy.sql`

Conteúdo resumido:

1. `CREATE OR REPLACE` `current_app_user_id()` e `current_app_user_is_admin()` (SECURITY DEFINER, `search_path = public`)
2. `ALTER TABLE public.edital ENABLE ROW LEVEL SECURITY`
3. `edital_admin_select` — `FOR SELECT TO authenticated USING (current_app_user_is_admin())`
4. `edital_admin_insert` — `FOR INSERT TO authenticated WITH CHECK (current_app_user_is_admin())`
5. `edital_admin_update` — `FOR UPDATE TO authenticated USING/WITH CHECK (admin)`
6. `GRANT SELECT, INSERT, UPDATE ON edital TO authenticated`
7. `REVOKE INSERT, UPDATE ON edital FROM anon`
8. `GRANT EXECUTE` nas funções para `authenticated`

## 7. Por que não `with check (true)` / `using (true)`

Policy ampla permitiria qualquer utilizador autenticado (incluindo consultor) ler/inserir editais. O produto exige **apenas admin** alinhado ao banco.

## 8. Por que não liberar DELETE

Princípio do projeto: não deletar registros; `dataService.deleteEdital` existe na UI mas DELETE em massa não é objetivo deste patch.

## 9. Por que não adicionar `created_by` agora

Schema versionado não tem coluna de dono em `edital`. Admin gate via `current_app_user_is_admin()` é suficiente para cadastro manual.

## 10. Função admin — alinhamento com `RLS_CLIENTE.sql`

| Aspecto | `RLS_CLIENTE.sql` | Migration 1.0B |
|---------|-------------------|----------------|
| SECURITY DEFINER | Sim | Sim |
| `search_path = public` | Sim | Sim |
| `auth.uid()` | Sim | Sim |
| `status = 'Ativo'` | Sim | Sim |
| `tipo_usuario` | Administrador, Admin | Igual |
| `nivel_acesso = 1` | Não | **Sim** (alinha `isAdminUser()` frontend) |

## 11. Compatibilidade com policies existentes

| Policy legada | Ação desta migration |
|---------------|---------------------|
| `service_role_all_edital` | **Preservar** |
| `anon_all_edital` (SELECT/FOR ALL) | **Não remover** — leitura pública do catálogo |
| `edital_admin_*` | Adicionadas/recriadas idempotentemente |

## 12. Como aplicar manualmente (novos ambientes)

1. Rodar queries §5 em **staging**
2. Abrir SQL Editor → colar `20260610_security_1_0b_edital_admin_write_policy.sql`
3. Executar transação `BEGIN`/`COMMIT`
4. Validar:

```sql
SELECT policyname, cmd, roles, qual, with_check
FROM pg_policies
WHERE schemaname = 'public' AND tablename = 'edital'
ORDER BY policyname;
```

5. Teste manual §4
6. Repetir em produção após validação

**Não** executar via CI/CD automático.

## 13. Plano de rollback

```sql
BEGIN;
DROP POLICY IF EXISTS edital_admin_select ON public.edital;
DROP POLICY IF EXISTS edital_admin_insert ON public.edital;
DROP POLICY IF EXISTS edital_admin_update ON public.edital;
REVOKE SELECT, INSERT, UPDATE ON TABLE public.edital FROM authenticated;
COMMIT;
```

Opcional: repor `current_app_user_is_admin()` exatamente como `RLS_CLIENTE.sql` (sem `nivel_acesso = 1`).

## 14. Ferramentas locais (sem Supabase)

```bash
python backend/scripts/security_1_0b_rls_checklist.py
cd backend && pytest tests/test_security_1_0b_rls_migration.py -q
cd frontend/EditalFinder-React && npm test
```

## 15. Riscos restantes

- Policies legadas `anon_all` com escrita ampla (patch separado)
- `deleteEdital` na UI sem policy DELETE — continuará a falhar
- Editais manuais pré-1.1I sem marcador em `extras` podem não aparecer na aba Cadastros

## 16. Próximo passo

- **Produção:** aplicar migration completa (inclui SELECT) se staging validado
- **SECURITY 1.0C** (opcional): auditoria `anon_all_edital`; backfill `extras` em registros legados; decisão sobre DELETE admin

## Referências

- `docs/SECURITY_1_0A_RLS_AUTH_ADMIN_AUDIT.md`
- `docs/FRONTEND_1_1F_CADASTRO_POLICY_ERROR_HANDLING.md`
- `docs/FRONTEND_1_1I_CADASTROS_SAVED_EDITAL_VISIBILITY_FIX.md`
- `backend/docs/sql/RLS_CLIENTE.sql`

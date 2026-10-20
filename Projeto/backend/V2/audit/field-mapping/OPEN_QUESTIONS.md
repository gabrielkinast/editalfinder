# Questões abertas / não confirmadas

## Supabase e schema

1. O schema remoto atual ainda corresponde ao snapshot introspectado em 2026-06-03 (`backend/database/schema_current.sql`)?
2. Existem FKs/checks/defaults remotos não expostos no snapshot, especialmente para `id_organizacao`?
3. Qual DDL de `vw_editais_front` está instalado: staging 20260505, visibility update, hotfix relaxado ou outro?
4. `VITE_VIEW_EDITAIS` em cada build aponta realmente para `vw_editais_front`?
5. Qual é a definição completa de `vw_editais_favoritos_front`?
6. As views usam `security_invoker`; quais grants/policies se aplicam?

## RLS e identidades

7. Quais policies RLS estão ativas em `edital`, `edital_favorito`, tabelas de detalhe e views?
8. Usuários anon/auth/admin veem o mesmo catálogo?
9. `current_app_user_id` e associação `auth_user_id` estão consistentes?

## Dados e volume

10. Quantos registros existem em `edital` e quantos a view retorna hoje, por ambiente e fonte?
11. Quantos possuem `pais`, `uf`, `regiao`, `area`, tipos e prazo preenchidos?
12. Quantos estão `ativo=false`, suspeitos, vencidos ou ocultos por `extras.curadoria_front`?
13. Há merges antigos que preservaram valores diferentes dos JSONs locais?
14. Os três estudos de caso locais existem no banco e com quais IDs/valores finais?

## Ambientes e secrets

15. Quais projetos Supabase correspondem a dev/staging/produção?
16. Quais variáveis/feature flags estão ativas: schema estendido, backend enrichment, deadline backfill, favoritos?
17. Secrets/tokens existem nos `.env`, CI ou plataforma; **não foram lidos nem copiados**. Rotação/validade é não confirmada.

## Operação

18. Qual migração é considerada canônica e qual processo garante sua aplicação?
19. O loader roda com schema estendido e contra staging antes de produção?
20. Como dry-run é obtido operacionalmente, dado que o CLI local não oferece essa opção?
21. Quais crawlers/artefatos locais representam a coleta mais recente?

Responder exige acesso read-only autorizado ao Supabase/configuração de deployment; nenhuma dessas verificações foi executada nesta tarefa.

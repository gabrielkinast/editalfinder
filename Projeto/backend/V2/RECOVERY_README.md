# EditalFinder V2 — Recovery Package

Pacote reconstruído a partir dos artefatos enviados na conversa após a perda da cópia local.

## Conteúdo principal

- `docs/v2/`: contratos, decisões, desenho de schema e roteiros de validação.
- `supabase/migrations/`: migrations 000001 (schema) e 000002 (seeds), nas versões mais recentes enviadas.
- `audit/field-mapping/`: pacote de auditoria do Legacy.
- `FIELD_MAPPING_AUDIT.md`: auditoria consolidada do mapeamento Legacy.

## Estado operacional conhecido

- Migration 000001 foi aplicada com sucesso no Supabase V2 staging.
- Migration 000002 foi aplicada com sucesso no Supabase V2 staging.
- 12 tabelas e `vw_oportunidades_front_v2` existem no staging.
- RLS está habilitada nas 12 tabelas.
- Não há policies/grants públicos definidos pelas migrations iniciais.
- Seeds aplicados: 8 tipos de oportunidade, 9 tipos de recurso, 15 áreas e 10 fontes piloto.
- O V2 ainda não possuía oportunidades reais no momento da validação.

## Importante

Este pacote não contém `.env`, credenciais, `.venv` ou segredos.
Após restaurar no repositório, versionar imediatamente com Git e manter uma cópia remota.

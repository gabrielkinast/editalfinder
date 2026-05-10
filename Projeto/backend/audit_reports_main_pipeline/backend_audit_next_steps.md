# Backend Audit - Próximos Passos

## Melhoria imediata

1. Criar uma validação global pós-carga, apenas leitura, que consolide `public.edital`, `public.noticia`, `public.pesquisa` e as quatro views em um único relatório.
2. Fazer o `main.py` considerar falhas de validação pós-carga como erro real em `last_run_errors.json`, não apenas como step com `status=error`.
3. Trocar a semântica operacional de `config/pipeline_sources.json`: `stable_apply_sources: []` deve significar "nenhuma fonte liberada para apply automático", ou exigir uma flag explícita como `allow_all_ready_sources: true`.
4. Corrigir ou isolar os erros recentes de crawler: `bae_systems_suppliers`, `china_nsfc` e `fapergs`.
5. Investigar a falha recente de `validate_news_research_after_load` para `eurekalert_science_filtered/eurekalert_wave1` antes de promover essa fonte como saudável no diário.

## Melhoria curta

1. Criar detector geral de resíduos por fonte: comparar links ativos no banco com links do payload atual em `audit_reports_retransform/standardized` e `audit_reports_news_research_loader`.
2. Generalizar a desativação segura para qualquer fonte/tabela suportada, sempre com `ativo=false`, nunca com remoção da linha principal.
3. Revisar o script de desativação Onda A para usar a coluna canônica correta (`fonte_recurso`) ou uma estratégia compatível com o schema real.
4. Adicionar resumo diário orientado a operação: status por fase, fontes processadas, would_upsert, inserted/updated, validações, warnings, resíduos e recomendação final.
5. Padronizar o contrato entre payload real do loader e documentação de schema: gerar relatório de drift a partir dos campos efetivamente enviados.

## Melhoria futura

1. Unificar readiness derivado e readiness curado com histórico de decisão por fonte, evitando promoção silenciosa.
2. Criar política de frontend nas views: ocultar `ativo=false`, destacar ou filtrar `suspeito`, prazos vencidos, `access_limited`, fonte experimental e `ready_with_notes`.
3. Separar melhor os gates por destino: edital, notícia e pesquisa devem ter checks independentes e um agregador final.
4. Transformar `DANGER_RESET_STAGING_SCHEMA.sql` em procedimento documentado de emergência, fora de qualquer fluxo automatizado.
5. Adicionar testes unitários leves para seleção de fontes, guards de apply, roteamento de conteúdo e geração de payloads news/research.

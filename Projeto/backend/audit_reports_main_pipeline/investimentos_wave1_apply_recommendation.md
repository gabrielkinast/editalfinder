# Investimentos Wave 1 — recomendação de apply

## Opções

### 1. Aplicar os 15 portais em staging (recomendado)

- **O quê:** `python scripts/load_portais_estrategicos.py --apply --staging --sources apex,bndes,eic --input-dir audit_reports_main_pipeline/investimentos_wave1_portais/standardized --output-dir audit_reports_main_pipeline/investimentos_wave1_portais_apply`
- **Porquê:** Dry-run sem erros; lote pequeno; apenas hubs; `mostrar_no_radar=false`; não toca `public.edital`.
- **Pré-requisitos:** guardas de ambiente já usadas na Wave fornecedores; confirmar que a equipa DB/FE está alinhada com `frontend_section=investimentos` e com a view ou API de leitura.

### 2. Aplicar só parte (ex.: eic + bndes)

- **O quê:** `--sources eic,bndes` (ou só `eic`) até o standardized Apex de base crescer além de 2 itens “ruidosos”.
- **Porquê:** Reduz risco operacional se houver dúvidas sobre URLs institucionais Apex/BNDES.

### 3. Não aplicar ainda

- **O quê:** Manter apenas `investimentos_wave1_portais_dryrun/` e revisões de conteúdo/SEO.
- **Porquê:** Falta `vw_investimentos_front` consumível, ou política de deduplicação contra `edital` ainda em discussão.

## Recomendação

**Opção 1**, desde que exista forma de **ler** os dados em staging (view ou SQL acordado). Se a view ainda não existir, preferir **Opção 3** até o contrato de leitura estar fechado — ou **Opção 2** (subconjunto EIC) como passo intermédio.

**Nesta tarefa:** nenhum apply foi executado; nenhuma escrita em Supabase.

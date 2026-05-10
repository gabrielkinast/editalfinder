# IARPA — `ready_with_notes` — dry-run do loader

Data: 2026-05-02

## Diff de readiness

### `config/source_readiness.json`

- **Removido** `iarpa` de `blocked`.
- **Adicionado** `iarpa` a `ready_with_notes` (entre `horizon_europe` e `mapa`).

### `audit_reports_retransform/readiness_for_loader.json`

- **Removido** `iarpa` de `fontes_bloqueadas_temporariamente`.
- **Inserido** `iarpa` em `fontes_prontas_para_loader` na fatia **pronto com observações** (logo após `lockheed_martin_suppliers`, antes de `mapa`).
- `status_distribution.pronto_com_observacoes`: **8 → 9**
- `status_distribution.bloquear_temporariamente`: **23 → 22**

### Nota sobre `load_ready_sources.py`

O script **reescreve** `config/source_readiness.json` com base no slice `fontes_prontas_para_loader` (primeiros 54 = pronto; seguintes 9 = com observações) **mais** as listas bloqueadas do JSON de readiness. Para manter a **lista completa** de fontes em `ready` / `ready_with_notes` / `blocked` do projeto (incluindo entradas que só existem no config e não no slice do loader), o ficheiro `config/source_readiness.json` foi **restaurado** após o dry-run com o conteúdo canónico do repositório **e** `iarpa` em `ready_with_notes`.

## Standardized copiado

- Origem: `audit_reports_blocked_sources/lote2_fix_iarpa/standardized/iarpa_standardized.json`
- Destino: `audit_reports_retransform/standardized/iarpa_standardized.json`

## Resultado do dry-run

Comando:

```text
python scripts/load_ready_sources.py --dry-run --sources iarpa --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

| Métrica | Valor |
|--------|------:|
| Fontes selecionadas | 1 (`iarpa`) |
| Itens standardized | 8 |
| **would_upsert** | **8** |
| would_ignore | 0 |
| mapping_errors | 0 |
| critical_empty_items | 0 |
| documentos_perdidos_no_payload | 0 |
| validacao_status preservados (itens) | 8 |
| qualidade_dado preservados (itens) | 8 |

Detalhe por fonte: `audit_reports_loader_ready/load_ready_by_source.json`. Resumo global: `audit_reports_loader_ready/load_ready_summary.json`.

## Verificações pedidas (8 itens)

| Verificação | Resultado |
|-------------|-----------|
| Itens standardized | 8 |
| would_upsert | 8 |
| Erros de mapeamento | 0 |
| critical_empty | 0 |
| tipo_oportunidade | `funding_opportunity` em todos |
| tipo_recurso | `fomento_pdi` em todos |
| perfil_ideal | Presente em todos |
| setor_estrategico | Presente em todos |
| area_tecnologica | Sem ciber/cyber indevidos nas listas |
| validacao_status | Preservado (8/8) |
| qualidade_dado | Preservado (8/8) |
| codigo_oportunidade / oppId | Campo `extras.codigo_oportunidade` **vazio** no standardized; **oppId** só na **URL** Grants.gov |
| Links oficiais | 8× `https://www.grants.gov/web/grants/view-opportunity.html?oppId=…` |
| Archived | `grants_opp_status`: **archived** nos 8 |
| pdf_url | Vazio; **não** preenchido artificialmente |
| Documentos | Bruto sem `documentos` / PDF; **0 perdas** no fluxo simulado |
| Cibersegurança indevida | Não identificada (sem termos fortes agregados) |

## Apply e Supabase

- **Apply**: não solicitado (`apply_status`: `not_requested`).
- O script pode **registar** execução em `carga_execucao` / histórico local conforme implementação atual; **não** foi pedido `apply` nem alteração de dados de negócio além do que o próprio script de dry-run fizer por logging.

## Recomendação para staging

**Aplicável com revisão humana:** o dry-run está limpo para **8 upserts** simulados. Antes de um `apply` real em staging: confirmar política para **oppId** (URL vs coluna `codigo_oportunidade`), aceitar que os anúncios estão **archived**, e usar os flags `--apply --staging` apenas quando o ambiente e a governança o permitirem.

Não foi executado `apply` nesta tarefa.

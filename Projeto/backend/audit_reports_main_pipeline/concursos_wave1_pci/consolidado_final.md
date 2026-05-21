# Wave 1 PCI Concursos — consolidado final

**Fonte:** `pci_concursos`  
**Máquina legível:** `consolidado_final.json` (mesma pasta)  
**Consolidado (UTC):** ver campo `consolidado_em_utc` no JSON.

## Artefactos analisados

| Artefacto | Caminho |
|-----------|---------|
| Standardized | `audit_reports_main_pipeline/concursos_wave1_pci/standardized/pci_concursos_standardized.json` |
| Crawler | `audit_reports_main_pipeline/concursos_wave1_pci/crawler_summary.json` |
| Loader dry-run v2 | `audit_reports_main_pipeline/concursos_wave1_pci/loader_dryrun_v2/load_concursos_selecao_summary.json` |

## Totais

- **12** itens standardized (`pci_concursos_standardized.json`).
- Crawler: **24** URLs brutas na listagem, **0** descartados, **0** erros de crawl.
- Loader dry-run v2: **`errors_count` = 0**, **`would_upsert_total` = 12**, `expired_items_count` = 0, `duplicate_fonte_link_in_batch` = 0.

## Qualidade antes vs depois (parser)

| Aspeto | Antes (piloto inicial) | Depois (parser atual) |
|--------|-------------------------|------------------------|
| Vagas com milhar PT (`1.100 vagas`) | Risco de ler só `100` | **1100** onde o texto traz milhar corretamente (ex.: Exército na amostra). |
| Salários (`mil`, `até R$`, milhares) | Truncagens e um único campo | **`parse_salario_min_max_br`**; exemplo NAV **até R$ 10.868,68** → `salario_max` 10868.68. |
| Órgão / UF / município | Quase sempre null | **`orgao` 9/12**, **`estado` e `municipio` 4/12** (padrões título + UF). |
| Extras | Mínimos | **`extracted_fields`**, **`missing_core_fields`**, **`extraction_confidence`**, **`official_link_missing`**, **`pci_noticia_url`**, `cadastro_reserva` quando aplicável. |
| `qualidade_dado` | Fixo | **baixa** 3 / **media** 9 na amostra atual. |
| Confiança extraída | — | **baixa** 3 / **media** 5 / **alta** 4 (`extras.extraction_confidence`). |

## Cobertura de campos (sobre 12 linhas)

Destaques do `field_fill` do crawler (taxas ≈ preenchidos / 12):

- **1,0:** `titulo`, `tipo_selecao`, `link`, `link_edital`, `fonte`, `banca`, `nivel_escolaridade`, `salario_max`, `extras`, `tags`, `status`, …
- **0,75:** `orgao` (9/12).
- **0,33:** `estado`, `municipio` (4/12).
- **0,917:** `numero_vagas` (11/12).
- **0,667:** `salario_min` (8/12).
- **0,0 nesta wave:** `data_fim_inscricao`, `data_prova`, `data_publicacao`, `cargo`, `curso`, `area`, … (lista completa em `campos_sempre_ausentes_wave` no JSON e no `crawler_summary.json`).

**Validação no lote:** `validacao_status` = **incompleto** em **12/12** (regra atual: falta `data_fim_inscricao` extraída do HTML).

## Exemplos bons (referência)

Ver array `exemplos_bons` em `consolidado_final.json`. Em resumo:

1. **Exército**, **1100 vagas**, órgão inferido, `link_edital` militar.
2. **Marinha do Brasil**, **49 vagas**, faixa de salário no texto (min/max distintos no standardized).
3. **NAV BRASIL**, **`salario_max` 10868.68** alinhado a “até R$ 10.868,68”, vagas e link oficial (órgão continua null — ver incompletos).

## Exemplos incompletos ou frágeis

Ver `exemplos_incompletos_ou_frageis` no JSON. Pontos principais:

- **Todas** as linhas sem **`data_fim_inscricao`** (e sem **`data_prova`**) → **`validacao_status` incompleto**.
- Linhas **baixa** `qualidade_dado` / **baixa** confiança: órgão e UF ausentes (ex.: ESFCEx, EsPCEx, NAV).
- **Salário frágil:** títulos com “mil” mas valor numérico muito baixo (**15,6** / **22,0** em vez de milhares) quando o PCI usa **hífen** no slug (`15-6`) — risco documentado; curadoria ou próximo ajuste de parser.

## Riscos (agregador)

- Texto **editorial**, não edital: datas e prazos podem faltar ou estar errados.
- **`link_edital`** é o primeiro link HTTP externo “útil”, não garantia de edital oficial.
- Valores **R$** podem ser **taxa**, referência ou intervalo parcialmente citado.
- **Heurísticas** de nível de escolaridade e tipo de seleção dependem do texto disponível no crawl.

## Recomendação de apply em staging

**Recomendado com ressalvas:** o dry-run v2 está **limpo** (`errors_count = 0`, 12 upserts previstos). A carga é **adequada para staging** (API, `vw_concursos_front`, testes de UI), assumindo que **12 linhas incompletas** em validação e possíveis **salários frágeis** são aceitáveis até curadoria ou segunda passagem de parser.

**Não recomendado** usar esta wave como fonte única em **produção** sem revisão.

## Comando exato de apply staging (não executado)

Definir ambiente e autorização explícita de apply; a raiz de comandos é o repositório `edital`.

**PowerShell (Windows):**

```powershell
$env:EDITALFINDER_ENV="staging"; $env:EDITALFINDER_ALLOW_STAGING_APPLY="1"; python scripts/load_concursos_selecao.py --input-dir audit_reports_main_pipeline/concursos_wave1_pci/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_pci/loader_apply_staging --sources pci_concursos --apply-staging --staging
```

**Bash:**

```bash
EDITALFINDER_ENV=staging EDITALFINDER_ALLOW_STAGING_APPLY=1 python scripts/load_concursos_selecao.py --input-dir audit_reports_main_pipeline/concursos_wave1_pci/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_pci/loader_apply_staging --sources pci_concursos --apply-staging --staging
```

**Pré-requisitos:** `SUPABASE_URL` e chave de serviço (`SUPABASE_SERVICE_ROLE_KEY` ou `SUPABASE_KEY`) carregadas no ambiente (por exemplo via `.env.staging`). O consolidado **não** executa apply.

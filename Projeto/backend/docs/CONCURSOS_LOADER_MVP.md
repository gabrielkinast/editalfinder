# Loader Concursos & Seleções — MVP

Script Python que lê JSON **standardized**, valida campos alinhados a `public.concurso_selecao` e, em modo apply, faz **upsert** por `(fonte, link)` sem apagar linhas que não apareçam no lote.

**Política de retenção / visibilidade pública:** [`DATA_RETENTION_AND_EXPIRATION_POLICY.md`](./DATA_RETENTION_AND_EXPIRATION_POLICY.md) — nunca `DELETE` por vencimento; histórico na tabela; listagem via `vw_concursos_front`.

## Ficheiros

| Caminho | Descrição |
|---------|-----------|
| `scripts/load_concursos_selecao.py` | Loader com `--dry-run`, `--apply-staging`, `--staging`, `--input-dir`, `--output-dir`, `--sources` |
| `audit_reports_main_pipeline/concursos_wave1_manual/standardized/` | Pasta padrão de entrada; ficheiros `{chave}_standardized.json` (lista de objetos) |
| `audit_reports_main_pipeline/concursos_wave1_manual/standardized/concursos_wave1_manual_standardized.json` | Exemplo manual com 6 registos (tipos: concurso público, vestibular, professor, técnico-administrativo, residência, bolsa) |

## Relatórios gerados (`--output-dir`)

- `load_concursos_selecao_summary.json` / `.md`
- `load_concursos_selecao_errors.json` / `.md`
- `load_concursos_selecao_payload_examples.json`
- `load_concursos_selecao_by_source.json`
- `load_concursos_selecao_warnings.json` — itens válidos que **não** passariam na recência atual de `vw_concursos_front` (ver abaixo)

## Recência (alinhado à view `vw_concursos_front`)

O loader **não remove** linhas na base; apenas:

1. **Aviso** (`[AVISO]` em stderr + lista em `load_concursos_selecao_warnings.json`) para cada registo preparado que **não** satisfaz a mesma lógica de recência da view pública:
   - `data_fim_inscricao >= hoje` **ou**
   - `data_prova >= hoje` **ou**
   - sem ambas as datas e (`data_publicacao` nos últimos 90 dias **ou** `criado_em` no JSON nos últimos 90 dias).
2. **`expired_items_count`** no `load_concursos_selecao_summary.json`: número de itens preparados nessa situação (dry-run continua com exit 0 se não houver erros de validação).
3. **Coerência de `status`:** se `data_fim_inscricao` e `data_prova` existem, ambas **anteriores a hoje**, e o JSON **não** define `status` (chave ausente, `null` ou string vazia), o payload é ajustado para `status = encerrado` antes da validação. Se o ficheiro define `status`, o valor é respeitado.

A listagem pública no Supabase só muda após aplicar o SQL em [`sql/UPDATE_VW_CONCURSOS_FRONT_RECENCY.sql`](./sql/UPDATE_VW_CONCURSOS_FRONT_RECENCY.sql) (ou recriar a partir de [`sql/CREATE_CONCURSO_SELECAO.sql`](./sql/CREATE_CONCURSO_SELECAO.sql)). Critérios de produto (encerrado, em andamento sem inscrição, sem delete) estão consolidados em [`DATA_RETENTION_AND_EXPIRATION_POLICY.md`](./DATA_RETENTION_AND_EXPIRATION_POLICY.md) §1.

## Dry-run (recomendado)

Não contacta o Supabase:

```bash
python scripts/load_concursos_selecao.py --dry-run --output-dir audit_reports_main_pipeline/concursos_wave1_manual/loader_dryrun
```

Parâmetros opcionais: `--input-dir`, `--sources` (lista separada por vírgulas, default `concursos_wave1_manual`).

## Apply em staging (não executado no MVP da documentação)

1. `EDITALFINDER_ENV=staging` ou `local` (nunca `production` / `prod`).
2. `EDITALFINDER_ALLOW_STAGING_APPLY=true`
3. `SUPABASE_URL` + chave de serviço (`SUPABASE_SERVICE_ROLE_KEY` ou `SUPABASE_KEY` compatível com service).
4. Comando:

```bash
python scripts/load_concursos_selecao.py --apply-staging --staging --output-dir audit_reports_main_pipeline/concursos_wave1_manual/loader_apply
```

Sem `--staging`, o apply é recusado. Em ambiente marcado como produção, o apply é bloqueado.

## Mapeamento e validações

O script mapeia os campos do JSON (snake_case, com aliases mínimos `title`→`titulo`, `url`→`link`, `uf`→`estado`) para as colunas da tabela. Valida entre outros:

- `titulo`, `link` (http/https), `fonte` obrigatórios
- `tipo_selecao`, `status`, `validacao_status` nos conjuntos permitidos pelo CHECK SQL
- `fonte_tipo` permitido quando presente
- datas presentes parseáveis (`YYYY-MM-DD` ou prefixo ISO)
- `salario_min` ≤ `salario_max` quando ambos existem
- `data_inicio_inscricao` ≤ `data_fim_inscricao` quando ambas existem

## Upsert

- Tabela: `public.concurso_selecao`
- Conflito: `fonte`, `link` (índice único existente na DDL)
- Não há passo de delete: registos antigos mantêm-se

## Wave 1 — fontes e apply staging

Consolidado (2026-05-16): [`concursos_wave1_consolidado.md`](../audit_reports_main_pipeline/concursos_wave1_consolidado.md) · [`.json`](../audit_reports_main_pipeline/concursos_wave1_consolidado.json).

| `fonte` | Standardized | Apply staging | Dry-run errors |
|---------|-------------:|--------------:|---------------:|
| `pci_concursos` | 12 | 12 upserts | 0 |
| `fundatec` | 7 (2 válidos no subset) | 2 inserts (subset) | 0 |
| `quadrix` | 10 | 10 inserts | 0 |
| `legalle` | 5 | 5 inserts | 0 |
| `objetiva` | 3 | 3 inserts | 0 |
| `ibfc` | 1 | 1 insert | 0 |
| `fgv` | 3 | — | 0 |
| `cebraspe` | 0 | — | 0 |
| `aocp` | 0 | — | 0 |

**Total aplicado em staging (relatórios loader):** 33 upserts, `errors_count` 0 em todos os apply analisados.

Pastas: `audit_reports_main_pipeline/concursos_wave1_{fonte}/` com `standardized/`, `loader_dryrun/`, e `loader_apply_staging/` quando apply foi feito. Fundatec apply: `concursos_wave1_fundatec_subset_valido/`.

Exemplo dry-run por fonte:

```bash
python scripts/load_concursos_selecao.py --dry-run \
  --input-dir audit_reports_main_pipeline/concursos_wave1_quadrix/standardized \
  --output-dir audit_reports_main_pipeline/concursos_wave1_quadrix/loader_dryrun \
  --sources quadrix
```

## Próximos passos

- Re-apply periódico das bancas com volume ativo (Quadrix, Legalle, Objetiva).
- Wave 2: FCC, Concursos no Brasil, Vunesp (ver consolidado).
- CI: falhar se `errors_count` > 0 após dry-run.

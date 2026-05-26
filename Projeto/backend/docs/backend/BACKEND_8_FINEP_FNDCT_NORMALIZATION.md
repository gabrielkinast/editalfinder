# Backend 8 — Normalização FINEP vs FNDCT

Correção da **fonte institucional** no classificador backend, sem UPDATE no banco e sem alterar o frontend nesta fase.

---

## Problema

Alguns editais operados pela **FINEP** apareciam na UI com fonte **FNDCT**, porque `fonte_recurso` ou metadados do crawler trazem o fundo de origem do recurso em vez da agência operadora.

| Conceito | Papel |
|----------|--------|
| **FINEP** | Agência operadora / fonte institucional visível |
| **FNDCT** | Fundo Nacional de Desenvolvimento Científico e Tecnológico — **origem do recurso** |

Na UI, o utilizador deve ver **FINEP** quando o edital é da FINEP, mesmo que o texto mencione FNDCT.

---

## Regra de normalização

Implementada em `CORE/opportunity_classifier.py` → `classify_source_normalized()`.

### Sinais fortes de FINEP (qualquer um)

- Link/domínio `finep.gov.br`
- `fonte_recurso` / `fonte` / `orgao` contém FINEP
- Título ou descrição contém FINEP
- `extras.agencia` / `extras.orgao` = FINEP

**Então:**

```
fonte_normalizada = "FINEP"
fonte_original    = valor legado preservado
source_scope      = "brasil"
pais_origem       = "Brasil"
```

Se também há FNDCT:

```
fundo_origem   = "FNDCT"
programa_fundo = "FNDCT"
source_notes   += "FNDCT tratado como fundo/origem do recurso..."
```

### Quando NÃO forçar FINEP

- Fonte apenas **FNDCT** sem indício de FINEP → mantém `fonte_normalizada = FNDCT`
- **CNPq**, Grants.gov, etc. → regras existentes inalteradas
- **Não** substituir globalmente todo FNDCT por FINEP

---

## Enrichment (Backend 8)

`CORE/opportunity_enricher.py` — versão `backend_8.0`

Novos campos (top-level + `extras.backend_enrichment`):

- `fundo_origem`
- `programa_fundo`
- `source_notes` (lista)

Sem migration obrigatória — campos vivem em `backend_enrichment` até colunas existirem.

---

## Comandos

```bash
python scripts/audit_finep_fndct_sources.py --from-db --limit 5000
python scripts/dry_run_finep_fndct_normalization.py --from-db --limit 5000
python -m pytest tests/test_source_normalization.py -q
```

Saídas:

- `outputs/audit_finep_fndct_sources/`
- `outputs/finep_fndct_normalization_dry_run/`

### Resultado no corpus atual (~1232 registros)

| Métrica | Valor |
|---------|-------|
| Menções FNDCT (fonte/título/descrição) | 3 |
| Relacionados FINEP ou FNDCT (dry-run) | 17 |
| Passariam a `fonte_normalizada=FINEP` | 1 (título explícito) |
| FNDCT-only sem FINEP (ex.: CNPq/MCTI/FNDCT) | mantém CNPq — **não força FINEP** |

Exemplo corrigido: título `Smart Factory- FINEP (SENAI)` → `fonte_normalizada=FINEP` (sinal `titulo_finep`).

Chamadas CNPq/MCTI/FNDCT permanecem com agência **CNPq**; FNDCT pode ser tratado como `fundo_origem` futuro via enriquecimento de texto, sem trocar a agência.

---

## SQL proposta (não aplicada)

Atualizado `docs/sql/PROPOSAL_BACKEND_ENRICHMENT_COLUMNS.sql`:

- `fundo_origem text`
- `programa_fundo text`
- `source_notes jsonb`

Atualizado `docs/sql/PROPOSAL_VW_EDITAIS_FRONT_WITH_SHADOW.sql`:

- expõe `fonte_normalizada` e `fundo_origem`

---

## Impacto futuro no frontend

Quando a view expuser `fonte_normalizada` + `fundo_origem`:

- Dashboard/filtros por fonte → usar **FINEP**
- Detalhe opcional → mostrar “Recurso: FNDCT” como linha secundária

Até lá, o frontend continua a usar `fonte_recurso` legado.

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| FNDCT legítimo sem FINEP classificado como FINEP | Exige sinal FINEP explícito |
| Menção incidental a FINEP no texto | Preferível a ocultar agência real; revisar amostra no dry-run |
| Crawlers futuros mudam metadados | Reexecutar audit + dry-run |

Nenhum UPDATE em produção nesta fase.

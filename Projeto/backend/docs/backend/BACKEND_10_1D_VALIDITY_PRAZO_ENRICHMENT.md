# BACKEND 10.1D — Validity / Prazo Enrichment

Enriquecimento de extração, normalização e classificação de prazo/validade em dry-run — sem apply, sem migration, sem persistência em `public.edital`.

## Problema

Após 10.1A (acionabilidade) e 10.1C (perfis por fonte), o gargalo principal era **prazo/validade**:

- Muitas oportunidades acionáveis como `oportunidade_sem_prazo` (128 em 1232 registros).
- `validade_status` e `prazo` só existiam no enricher/auditoria — não no banco.
- Parsers limitados: sem prioridade Grants.gov/DOE, sem locale EN/US, rejeição fraca de publicação.
- `_has_structured_deadline` checava só `prazo_envio` / `fim_inscricao` / `prazo_data` no topo do registro.

### Diagnóstico pré-patch (10.1C)

| Métrica | Valor |
|---------|-------|
| Acionáveis | 186 |
| `sem_prazo` (validade) | 112 |
| Acionáveis sem validade útil | 112 |
| Top fontes sem prazo | BNDES 20, Grants.gov 16, DOE_ARPAE 14 |

Campos com data no banco: `prazo_envio` (116), `data_publicacao` (659) — **nunca** usar publicação como deadline. Grants.gov usa `prazo_envio` como close ISO; `extras` quase vazio no snapshot atual.

## Solução

### Arquivos alterados

| Arquivo | Mudança |
|---------|---------|
| `CORE/deadline_normalizer.py` | Candidatos priorizados, `parse_deadline_date`, perfil DOE NOFO, `has_useful_deadline` |
| `CORE/date_parser.py` | Parsers PT/EN, rejeição publicação/resultado, locale BR/US |
| `CORE/noise_classifier.py` | `_has_structured_deadline` → `has_useful_deadline` |
| `CORE/validity_resolver.py` | `validade_reason`, `prazo_detectado`, `prazo_fonte` |
| `CORE/opportunity_enricher.py` | Reconciliação actionability ↔ validade; versão `backend_10.1d` |
| `tests/test_validity_resolver.py` | 19 novos casos regressivos |
| `scripts/audit_noise_backend.py` | Versão relatório 10.1D |

### Parsers PT-BR

- `inscrições até DD/MM/YYYY`, `submissão até`, `prazo final:`, `data limite:`, `encerramento:`
- `até o dia DD/MM/YYYY`, `até DD de mês de YYYY`
- Períodos `de X a Y` → data fim
- Formatos: `DD/MM/YYYY`, `DD.MM.YYYY`, texto com meses PT

**Rejeição:** `publicado em`, `divulgado em`, `lançou em`, `Em DD.MM.YYYY` (publicação BNDES), `resultado em`, `evento em`, `palestra/webinar`.

### Parsers EN

- `full/application/proposal/submission deadline`, `closing/close date`, `due date`, `responses due`
- `NOFO closes on`, `call deadline`, `call closes`
- Texto: `March 31, 2026`, `M/D/YYYY` com locale `en_US`

### Campos priorizados (menor = melhor)

1. `full_application_deadline`
2. `application_deadline` / `applicationDeadline`
3. `proposal_deadline`
4. `prazo_envio` / `fim_inscricao`
5. `closeDate` / `close_date` / `opportunityCloseDate`
6. `submission_deadline`
7. `concept_paper_deadline`
8. `archiveDate` — **somente** com contexto `close/deadline` e sem close principal

**Nunca:** `postedDate`, `data_publicacao`, `openDate`, `inscricoes_inicio`.

### Perfis por fonte

| Fonte | Melhoria |
|-------|----------|
| **Grants.gov** | `closeDate`/`prazo_envio` em extras; rejeita `closeDateExplanation` “No closing date” |
| **DOE_ARPAE** | Linha NOFO: duas datas → segunda (full application); `TBD` sem segunda data → sem prazo |
| **BNDES** | Prazo só com marcador de inscrição/submissão; publicação `Em DD.MM.YYYY` rejeitada |
| **Eureka/ERC** | Padrões EN `call deadline`, `application deadline` no texto |
| **AMAZUL** | Mantém `prazo_envio` existente; não promove licitação sem deadline explícito |

### Integração actionability

- `has_useful_deadline(record)` alimenta `_has_structured_deadline` no classificador.
- `opportunity_enricher._reconcile_actionability_with_validity`: `oportunidade_sem_prazo` + prazo útil → `oportunidade_principal`; inverso quando validade `sem_prazo`.
- **Não promove:** `portal_util`, `resultado`, `noticia`, `evento`.

### Saídas enricher (dry-run)

- `validade_status`, `validade_data`, `validade_reason`
- `prazo_detectado`, `prazo_fonte`, `prazo_source_field`
- `validade_confianca` → `validade_confidence` (nome legado preservado)

## Métricas antes / depois (1232 registros, `--from-db`)

| Métrica | 10.1C (antes) | 10.1D (depois) | Δ |
|---------|---------------|----------------|---|
| `oportunidade_principal` | 58 | 65–66 | **+7~8** |
| `oportunidade_sem_prazo` | 128 | 120–121 | **−7~8** |
| `sem_prazo` (validade) | 112 | 120 | +8* |
| `encerrado` | 58 | 46 | −12 |
| `aberto` | 11 | 15 | +4 |
| `vencendo_30` | 5 | 5 | 0 |
| `prazo_invalido` | 0 | 0 | 0 |
| `is_noise` | 32 | 32 | 0 |

\* O aumento de `sem_prazo` reflete **remoção de falsos positivos**: datas NOFO com `TBD` ou data de publicação deixam de contar como prazo. Qualidade de classificação melhora; acionáveis com prazo real sobem para `oportunidade_principal`.

### Efeito por fonte (pós-patch)

| Fonte | `oportunidade_principal` | `oportunidade_sem_prazo` | `sem_prazo` validade |
|-------|--------------------------|--------------------------|----------------------|
| BNDES | 0 | 20 | 20 |
| DOE_ARPAE | 4 | 10 | 10 (+4 encerrado com NOFO dupla data) |
| Grants.gov | 6 | 16 | 16 |
| Eureka | 1 | 10 | 9 |
| ERC | 0 | 5 | 5 |
| AMAZUL | 14 | 6 | 6 |

## Casos em que o sistema recusou prazo falso

- `Publicado em 10/05/2026` sem marcador de inscrição → `sem_prazo`
- `lançou, em 29.10.2025` (BNDES) → publicação, não deadline
- `postedDate` / `data_publicacao` isolados → ignorados
- `archiveDate` sem `closeDate` e sem texto “close/deadline” → ignorado
- NOFO `2/14/2025 … TBD` → sem prazo (forecast)
- `closeDateExplanation: No closing date` → sem prazo
- Webinar/evento com data no título → não vira oportunidade por data

## Testes

```bash
cd backend
python -m pytest tests/test_noise_classifier.py tests/test_validity_resolver.py -q
# 71 passed
```

Casos: PT numérico/textual, rejeição publicação/resultado, EN deadline, Grants closeDate, posted/archive rejeitados, DOE full_application > concept, NOFO dupla data, BNDES linha permanente, locale ambíguo, enricher promote/demote.

## Limitações

- **BNDES (38/38):** textos no banco são notícias de lançamento sem deadline estruturado — ganho real exige recrawl/PDF.
- **Grants.gov (79/127 sem prazo):** API close não persistido em `prazo_envio` para muitos registros — backfill no loader (fora deste patch).
- **DOE_ARPAE:** descrições curtas com `TBD` permanecem sem prazo (correto).
- Campos **não persistidos** em `public.edital` — apenas dry-run / `extras.backend_enrichment`.

## Próximos passos (recomendado)

1. **BACKEND 10.1E — Loader deadline backfill:** persistir `closeDate` Grants.gov e texto PDF BNDES no ingest (sem alterar schema público além de `prazo_envio`).
2. **Recrawl DOE_ARPAE detail:** extrair `full_application_deadline` do portal eXCHANGE.
3. **portal_estrategico** para suppliers/BDMG (loader), após prazo estável.

## Comandos de auditoria

```bash
python scripts/audit_validity_backend.py --from-db --limit 5000
python scripts/dry_run_quality_enrichment.py --from-db --limit 5000
python scripts/audit_noise_backend.py --from-db --limit 5000
```

Nenhum apply executado. Nenhuma alteração em Supabase.

# Backend 7 — Staging migration e backfill dry-run

Backend 7 prepara **validação em staging** dos campos enriquecidos (Backends 1–9) sem alterar `public.edital` nem o frontend.

**Antes do backfill real:** revisar campos de ruído, validade e `quality_score` do Backend 9 (`docs/backend/BACKEND_9_NOISE_VALIDITY_QUALITY.md`, dry-runs em `outputs/audit_noise_backend/` e `outputs/backend_9_quality_dry_run/`).

---

## O que a tabela sombra faz

A tabela `editais_backend_enrichment_shadow` armazena o resultado de `enrich_opportunity_record()` para cada `id_edital`, permitindo:

- comparar enriquecimento vs dados legados;
- revisar baixa confiança antes de backfill real;
- expor campos via view com `LEFT JOIN` sem migration na tabela principal.

**Não substitui** `public.edital`. Campos legados (`prazo_envio`, `area`, `extras`, etc.) permanecem intactos.

SQL: `docs/sql/STAGING_BACKEND_ENRICHMENT_SHADOW_TABLE.sql`

---

## Como gerar payload (dry-run)

```bash
python scripts/generate_backend_enrichment_shadow_payload.py --from-db --limit 5000
```

Saída: `outputs/backend_7_shadow_payload/`

| Arquivo | Conteúdo |
|---------|----------|
| `shadow_payload.json` | Linhas prontas para upsert na sombra |
| `summary.md` | Cobertura e contagens de revisão |
| `low_confidence_rows.json` | Qualquer campo com confiança baixa |
| `risky_kind_changes.json` | tipo_registro → notícia/pesquisa/concurso |
| `risky_area_changes.json` | Área baixa confiança ou sem_classificacao |
| `deadline_low_confidence.json` | Prazos não confiáveis para alertas |

Por padrão **não escreve no banco**.

---

## Como escrever em staging

1. Aplicar SQL da tabela sombra **apenas em staging** (manual).
2. Definir variável de proteção:

```bash
set EDITALFINDER_ALLOW_SHADOW_WRITE=true
python scripts/generate_backend_enrichment_shadow_payload.py --from-db --limit 5000 --write-shadow
```

Sem `EDITALFINDER_ALLOW_SHADOW_WRITE=true`, o script **aborta** com código 2.

Nunca grava em `public.edital`.

---

## Como comparar shadow vs principal

```bash
python scripts/compare_backend_enrichment_shadow.py --from-db --limit 5000
```

Saída: `outputs/backend_7_shadow_comparison/`

Responde:

- quantos registros têm linha shadow;
- cobertura de `prazo_data`, `tipo_registro`, modalidade, área;
- distribuições de prazo, kind, modalidade, área;
- quantos com baixa confiança;
- quantos `tipo_registro` ≠ edital;
- quantos `sem_classificacao`.

Se a tabela sombra estiver vazia, o comparador usa **fallback computado** (enricher) e indica isso no `summary.md`.

---

## View proposta (não aplicada)

`docs/sql/PROPOSAL_VW_EDITAIS_FRONT_WITH_SHADOW.sql`

- `FROM public.edital e`
- `LEFT JOIN editais_backend_enrichment_shadow s ON s.id_edital = e.id_edital`
- Campos legados + enriquecidos opcionais

Frontend pode consumir `area_tematica_label` gradualmente; campos antigos continuam disponíveis.

---

## Métricas a revisar antes de aprovar backfill real

| Métrica | Onde ver | Limite sugerido |
|---------|----------|-----------------|
| `area_tematica_confidence = baixa` | `low_confidence_rows.json` | < ~50% do corpus |
| `sem_classificacao` | `area_distribution.json` | Aceitável se texto pobre; revisar amostra |
| `tipo_registro` sensível | `risky_kind_changes.json` | Revisar manualmente top casos |
| `prazo_confidence = baixa` | `deadline_low_confidence.json` | **Não** usar para alertas de vencimento |
| Cobertura `prazo_data` | `field_coverage.json` | Alinhar expectativa Backend 3/4 (re-crawl) |
| Flags `revisao_humana` | `risky_review.json` | Amostragem antes de produção |

Referência Backend 6 (área temática):

| Área | Contagem esperada (~1232 registros) |
|------|-------------------------------------|
| sem_classificacao | ~371 |
| multissetorial | ~170 |
| defesa_seguranca | ~130 |
| aeroespacial | ~9 |
| espaco | ~15 |

---

## Critérios para seguir ou não para backfill real

### Aprovar próxima fase se:

- [ ] Tabela sombra populada em staging sem erros
- [ ] **Normalização FINEP/FNDCT revisada** (Backend 8 — `docs/backend/BACKEND_8_FINEP_FNDCT_NORMALIZATION.md`)
- [ ] `area_tematica_label` com baixa confiança abaixo do limite aceito pela equipe
- [ ] Casos em `risky_kind_changes.json` revisados (notícia vs edital)
- [ ] Prazos baixa confiança excluídos de alertas automáticos
- [ ] View preserva campos legados (smoke test em staging)
- [ ] Frontend pode ler campos novos opcionalmente (sem remover fallback ainda)

### Não seguir se:

- Distribuição de área diverge muito do dry-run Backend 6 sem explicação
- Muitos editais reclassificados como notícia sem revisão
- Escrita shadow falhou ou env de proteção foi ignorada
- Tentativa de UPDATE direto em `public.edital` sem aprovação

---

## Próximos passos (Backend 8+)

1. Aprovação humana com base neste documento e artefatos em `outputs/backend_7_*`.
2. Migration de colunas em `public.edital` (`PROPOSAL_BACKEND_ENRICHMENT_COLUMNS.sql`) — **staging primeiro**.
3. Backfill controlado por lote (não mass UPDATE cego).
4. Atualizar view produção (`PROPOSAL_VW_EDITAIS_FRONT_BACKEND_6.sql` ou variante shadow).
5. Frontend: trocar fallback `Tecnologia e Inovação` por `area_tematica_label` quando disponível.

---

## Comandos

```bash
python scripts/generate_backend_enrichment_shadow_payload.py --from-db --limit 5000
python scripts/compare_backend_enrichment_shadow.py --from-db --limit 5000
python -m pytest tests/test_backend_shadow_payload.py -q
```

Nenhum commit automático. Nenhuma alteração em produção nesta fase.

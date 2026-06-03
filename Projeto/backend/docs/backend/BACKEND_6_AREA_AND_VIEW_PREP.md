# Backend 6 — Refinamento de área temática e preparação de migration/view

Backend 6 reduz a **inflação de aeroespacial** no classificador backend, separa **Espaço**, **Defesa** e **Tecnologias estratégicas**, e documenta migration/view para o frontend consumir `area_tematica_label` no futuro — **sem UPDATE no banco** e **sem alterar o frontend**.

---

## Problema: inflação de aeroespacial

No dry-run Backend 5 (`outputs/thematic_area_dry_run/`), após eliminar o fallback genérico de Tecnologia e Inovação, surgiu nova concentração:

| Área | Backend 5 dry-run | Backend 6 dry-run | Δ |
|------|-------------------|-------------------|---|
| aeroespacial | 1093 | 9 | −1084 |
| espaco | 0 | 15 | +15 |
| defesa_seguranca | 26 | 130 | +104 |
| multissetorial | 0 | 170 | +170 |
| sem_classificacao | 41 | 371 | +330 |

**309 registros** foram rebaixados por tag aeroespacial sem confirmação em título/descrição (`aerospace_reclassified.json`).

**Causa raiz:** o classificador Backend 5 pontuava um blob único que incluía `thematic_tags` e `setor_estrategico` com o mesmo peso que título/descrição. Crawlers internacionais propagam tags genéricas (`aeroespacial`, `veiculos`, `dual_use`, `ciencia_tecnologia`) via `taxonomy_filtros.py`, inflando aeroespacial sem termos explícitos no texto.

Auditoria dedicada: `scripts/audit_aerospace_area_inflation.py` → `outputs/audit_aerospace_area_inflation/`.

---

## Ajustes no classificador (Backend 6)

Arquivo: `CORE/opportunity_classifier.py` → `classify_thematic_area()`.

### Canais com pesos distintos

| Canal | Peso relativo | Exemplos |
|-------|---------------|----------|
| título / descrição | alto (×3) | satélite, propulsão, NATO |
| campo `area` / `setor` | médio-alto (×2) | área explícita no registro |
| `thematic_tags` / `setor_estrategico` | baixo (×0.35) | tags do blob |
| fonte | hint (×0.5) | DARPA, ESA no nome da fonte |

### Regras novas

1. **Tag-only downgrade:** se primária seria `aeroespacial`, `espaco`, `defesa_seguranca`, `nuclear` ou `tecnologias_estrategicas` **só por tags**, primária → `multissetorial` ou `sem_classificacao`; área original vira **secundária** com baixa confiança.
2. **Espaço separado de aeroespacial:** categoria `espaco` (“Espaço / sistemas orbitais”) para orbital, spacecraft, constellation, space debris.
3. **Defesa vs aero:** NATO/DARPA/military/counter-drone → `defesa_seguranca` sem termos orbitais; não confundir com aeroespacial.
4. **Tecnologias estratégicas:** critical/strategic technology, supply chain, advanced manufacturing broad.
5. **Sem fallback** Tecnologia e Inovação (herdado do Backend 5).

Função de diagnóstico: `explain_thematic_area(record)` para auditorias.

Versão do enricher: `backend_6.0` (`CORE/opportunity_enricher.py`).

---

## Resultados do dry-run Backend 6

```bash
python scripts/dry_run_thematic_area_classification.py --from-db --limit 5000
```

Saídas em `outputs/thematic_area_dry_run/`:

| Arquivo | Conteúdo |
|---------|----------|
| `backend_6_summary.md` | Comparação Backend 5 → 6 |
| `area_distribution_backend_6.json` | Distribuição pós-refino |
| `aerospace_reclassified.json` | Casos rebaixados por tag-only |

Critério de sucesso: **aeroespacial cai** para registros com evidência textual clara; aumento esperado em `multissetorial`, `sem_classificacao`, `defesa_seguranca` e `espaco`.

---

## Migration proposta (não aplicada)

`docs/sql/PROPOSAL_BACKEND_ENRICHMENT_COLUMNS.sql` — colunas opcionais:

- prazo: `prazo_data`, `prazo_raw`, `prazo_status`, `prazo_confidence`, `prazo_source_field`
- tipo/modalidade/escopo/fonte
- área: `area_tematica_normalizada`, `area_tematica_label`, `area_tematica_confidence`, `area_tematica_secondary`
- `qualidade_flags`, `backend_enrichment` (jsonb)

**Por que ainda não aplicar:** dry-run e revisão humana de `risky_updates_review.json` são pré-requisitos; frontend ainda usa `area` legado + fallback React.

---

## View proposta (não aplicada)

`docs/sql/PROPOSAL_VW_EDITAIS_FRONT_BACKEND_6.sql`

- Preserva campos legados: `titulo`, `link`, `fonte_recurso`, `prazo`, `area`, `setor`, `categoria`, `extras`
- Expõe campos novos como **opcionais**: `area_tematica_label`, `prazo_status`, `tipo_registro`, etc.
- Frontend pode migrar gradualmente para `area_tematica_label` sem quebra imediata.

---

## Dry-run de backfill (sem UPDATE)

```bash
python scripts/dry_run_backend_backfill_payload.py --from-db --limit 5000
```

Saída: `outputs/backend_backfill_payload_dry_run/` — payload JSON que **seria** usado em UPDATE, com contagem por coluna e revisão de baixa confiança.

---

## Dependência futura no frontend

Enquanto `classificationService.js` usar:

```javascript
area: areas.length > 0 ? areas : ['Tecnologia e Inovação']
```

o dashboard continuará inflando Tech/Inovação (~825) independentemente do backend.

**Próximo passo (fase separada):** quando `vw_editais_front` expuser `area_tematica_label`, o frontend deve preferir esse campo e remover o fallback genérico.

---

## Comandos

```bash
python scripts/audit_aerospace_area_inflation.py --from-db --limit 5000
python scripts/dry_run_thematic_area_classification.py --from-db --limit 5000
python scripts/dry_run_backend_backfill_payload.py --from-db --limit 5000
python -m pytest tests/test_thematic_area_classifier.py -q
```

---

## Artefatos

| Pasta / arquivo | Descrição |
|-----------------|-----------|
| `outputs/audit_aerospace_area_inflation/` | Auditoria de inflação |
| `outputs/thematic_area_dry_run/backend_6_summary.md` | Antes/depois |
| `docs/sql/PROPOSAL_BACKEND_ENRICHMENT_COLUMNS.sql` | Migration documental |
| `docs/sql/PROPOSAL_VW_EDITAIS_FRONT_BACKEND_6.sql` | View documental |

Nenhum dado em produção foi alterado nesta fase.

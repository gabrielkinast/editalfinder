# Backend 5 — Área temática

Auditoria e classificação de **área temática** no backend, sem UPDATE no banco e sem alterar o frontend.

---

## Problema observado

No dashboard, o filtro “Área temática” concentra ~825 registros em **Tecnologia e Inovação**, com poucas ocorrências nas demais áreas. Causas prováveis:

1. **Frontend:** `classificationService.js` usa fallback `['Tecnologia e Inovação']` quando nenhuma keyword casa (`area: areas.length > 0 ? areas : ['Tecnologia e Inovação']`).
2. **Backend / taxonomia:** `taxonomy_filtros.AREA_NEGOCIO` trata “inovação” e “tecnologia” como padrões amplos; `setor_estrategico`/`ciencia_tecnologia` domina em crawlers internacionais.
3. **Confusão conceitual:** área temática ≠ modalidade (`fomento`, `licitação`) ≠ `tipo_registro` (`edital`, `notícia`).

---

## Solução Backend 5

| Componente | Caminho |
|------------|---------|
| Classificador | `CORE/opportunity_classifier.py` → `classify_thematic_area()` |
| Enriquecimento | `CORE/opportunity_enricher.py` → campos `area_tematica_*` em `extras.backend_enrichment` |
| Auditoria | `scripts/audit_thematic_area_backend.py` |
| Dry-run | `scripts/dry_run_thematic_area_classification.py` |

### Regras principais

- **Não** usar Tecnologia e Inovação como fallback automático.
- Palavras genéricas isoladas (`tecnologia`, `inovação`) **não** classificam sozinhas → `multissetorial` ou `sem_classificacao`.
- Tecnologia e Inovação só com evidência explícita: inovação aberta, P&D empresarial, transferência de tecnologia, etc.
- Área **primária** + **secundárias** (ex.: saúde + Tecnologia e Inovação).

### Categorias

`tecnologia_inovacao`, `computacao_ia`, `saude`, `educacao_pesquisa`, `energia`, `meio_ambiente`, `agronegocio`, `industria`, `defesa_seguranca`, `aeroespacial`, `nuclear`, `materiais`, `biotecnologia`, `cidades_mobilidade`, `cultura_social`, `economia_negocios`, `startups`, `multissetorial`, `sem_classificacao`.

---

## Comandos

```bash
python scripts/audit_thematic_area_backend.py --from-db --limit 5000
python scripts/dry_run_thematic_area_classification.py --from-db --limit 5000
python -m pytest tests/test_thematic_area_classifier.py -q
```

Saídas:

- `outputs/audit_thematic_area_backend/`
- `outputs/thematic_area_dry_run/`

---

## Diferença: área vs modalidade vs tipo

| Campo | Pergunta |
|-------|----------|
| `tipo_registro` | É edital, notícia, pesquisa, concurso? |
| `modalidade_normalizada` | É fomento, licitação, bolsa, notícia institucional? |
| `area_tematica_normalizada` | **Sobre qual domínio** é a oportunidade (energia, saúde, defesa…)? |

---

## Backfill futuro (Backend 6+)

Ver **`docs/backend/BACKEND_6_AREA_AND_VIEW_PREP.md`** para:

- refinamento do classificador (canais de peso, categoria `espaco`, tag-only downgrade);
- dry-run Backend 6 e comparação aeroespacial;
- `docs/sql/PROPOSAL_BACKEND_ENRICHMENT_COLUMNS.sql`;
- `docs/sql/PROPOSAL_VW_EDITAIS_FRONT_BACKEND_6.sql`;
- `scripts/dry_run_backend_backfill_payload.py`.

### Backend 6 — resumo

| Item | Status |
|------|--------|
| Auditoria aeroespacial | `scripts/audit_aerospace_area_inflation.py` |
| Classificador refinado | `classify_thematic_area()` com pesos por canal |
| Categoria `espaco` | Adicionada |
| Migration/view | Propostas SQL (não aplicadas) |
| Frontend | **Não alterado** — ainda usa fallback Tech/Inovação |

1. Migration: colunas `area_tematica_normalizada`, `area_tematica_label` (opcional JSON secundárias).
2. Job report-only: diff `area` atual vs classificador (`dry_run_backend_backfill_payload.py`).
3. Atualizar `vw_editais_front` para expor `area_tematica_label` pronta (reduzir heurística React).
4. **Frontend (fase separada):** remover fallback genérico em `classificationService.js` após backend populado.

---

## Riscos

- Registros com texto pobre continuam `sem_classificacao` — melhor que fallback errado.
- Campo `area` legado no banco **não** é alterado nesta fase.
- Frontend ainda pode inflar Tech/Inovação até corrigir fallback client-side.

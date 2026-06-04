# Backend 2 — Dry-run de enriquecimento

Integração **somente leitura** do normalizador de prazos e do classificador no fluxo backend, medindo impacto antes de migration ou backfill.

---

## O que foi entregue

| Componente | Caminho |
|------------|---------|
| Enriquecedor | `CORE/opportunity_enricher.py` |
| Dry-run | `scripts/dry_run_backend_enrichment.py` |
| Hook opcional | `CORE/transformer.py`, `CORE/loader.py` (flag desligada) |
| Testes | `tests/test_opportunity_enricher.py` |
| Mapa pipeline | `docs/backend/BACKEND_2_PIPELINE_MAP.md` |

---

## Como rodar o dry-run

```bash
cd "d:\Computational_Physics\My Projects\edital"

# Base Supabase (.env.staging com URL + service key)
python scripts/dry_run_backend_enrichment.py --from-db --limit 5000

# Export JSON
python scripts/dry_run_backend_enrichment.py --input exports/editais_sample.json --output outputs/backend_enrichment_dry_run/
```

### Saídas

| Arquivo | Conteúdo |
|---------|----------|
| `summary.md` | métricas agregadas |
| `report.json` | mesmo conteúdo em JSON |
| `enriched_sample.json` | até 25 registros antes/depois |
| `changes_by_field.json` | contagem de campos novos preenchidos |
| `low_confidence_review.json` | candidatos com flag `revisao_humana` |
| `kind_changes_review.json` | tipo ≠ edital implícito na tabela |

---

## O que os relatórios significam

### Prazos

- **Ganham prazo_data:** tinham `prazo_envio`/`fim_inscricao` vazio ou não-ISO e o normalizador encontrou data (inclui texto).
- **Continuam sem_prazo:** sem evidência estruturada — backfill de crawler/transformer ainda necessário.
- **Confiança baixa:** extração de título/descrição; não usar como única fonte para alertas.

### Classificação

- **tipo_registro:** edital | noticia | pesquisa | concurso | portal | desconhecido.
- **modalidade_normalizada:** buckets do dashboard (Backend 1).
- **escopo_geografico:** brasil | internacional | multilateral | desconhecido.
- **kind_changes:** registro na tabela `edital` que o classificador rotularia diferente — candidato a roteamento futuro, não DELETE automático.

### Qualidade

- **qualidade_flags:** lista estável (`sem_prazo`, `revisao_humana`, `possivel_noticia_em_edital`, …).
- Use `low_confidence_review.json` para amostragem humana antes de backfill.

---

## Feature flag (integração gradual)

```bash
# .env.staging — padrão: desligado
EDITALFINDER_ENABLE_BACKEND_ENRICHMENT=false
```

Com `true`:

- **Transformer** e **loader** chamam `apply_backend_enrichment_if_enabled`.
- Apenas `extras.backend_enrichment` é anexado no item que vai ao upsert.
- Colunas novas (`prazo_status`, `modalidade_normalizada`, …) **não** são enviadas ao Postgres até existirem na tabela.

Comentário no código: *não ativar em produção sem dry-run aprovado*.

---

## Por que não aplicar UPDATE ainda

1. Schema sem colunas dedicadas — risco de strip no loader ou erro Supabase.
2. Auditoria Backend 1: 83% sem prazo; muitos ganhos seriam só `texto_derivado` (baixa confiança).
3. Mudanças de `tipo_registro` exigem política de roteamento (noticia/pesquisa), não update cego.
4. Backfill deve gerar relatório diff + rollback plan (fase Backend 3).

---

## Próximos passos (Backend 3 sugerido)

1. Migration: colunas da proposta SQL + índices leves.
2. Job backfill: preencher colunas a partir de `enrich_opportunity_record`, relatório CSV de diffs.
3. Recriar `vw_editais_front` com campos prontos.
4. Ativar flag em staging; validar dashboard sem heurística React.
5. Ajustar crawlers top problemáticos (China International, Araucária, Grants.gov).

---

## Testes

```bash
python -m pytest tests/test_deadline_normalizer.py tests/test_opportunity_classifier.py tests/test_opportunity_enricher.py -q
```

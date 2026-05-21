# Política de visibilidade e ruído — aba Editais

## Princípio

| Camada | Função |
|--------|--------|
| `public.edital` | Histórico completo — **não apagar** por ruído ou vencimento |
| `public.vw_editais_front` | Listagem pública filtrada — oportunidades úteis, atuais ou plausivelmente vigentes |
| `extras.curadoria_front` | Metadados de auditoria (visibility, reason, confidence) — aplicados **manualmente** |

## Feedback manual do utilizador

Utilizadores podem reportar problemas na aba Editais (link quebrado, não é oportunidade, encerrado, duplicado, informação incorreta, outro). O reporte **não** altera `curadoria_front` nem oculta o item automaticamente.

Ver [`EDITAIS_FEEDBACK_AND_REPORTING.md`](./EDITAIS_FEEDBACK_AND_REPORTING.md). Agregação futura de reportes pode informar revisão humana e scripts de auditoria — nunca com base num único clique.

---

## Classificações (`visibility`)

### Visíveis (padrão na view após curadoria temporal)

- `visible_current` — prazo futuro
- `visible_continuous_flow` — fluxo contínuo / rolling / permanente
- `visible_recent_strong_signal` — publicação ≤12m + sinal forte de oportunidade
- `visible_manual_reviewed` — curadoria humana explícita

### Revisão (fora da view até decisão)

- `review_missing_deadline` — oportunidade plausível sem prazo
- `review_possible_opportunity` — sinal fraco, sem temporal claro
- `review_possible_continuous_flow` — possível fluxo contínuo
- `review_link_suspicious` — link 403/suspeito (não é broken automático)

### Ocultos (candidatos — não deletar linha)

- `hidden_institutional` — home, conduta, governança, etc.
- `hidden_resultado` — resultado final, homologação, ata
- `hidden_historical` — ano ≤2024 sem vigência atual
- `hidden_expired` — prazo passado sem fluxo contínuo
- `hidden_not_opportunity` — notícia/portal/relatório
- `hidden_invalid_link` — `link_health` broken sem link alternativo
- `hidden_duplicate` — link/hash duplicado

## Regras temporais (view SQL)

Ver `docs/sql/UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql`:

- `ativo = true`
- Exclui `curadoria_front.visibility` em `hidden_*`
- Mostra se: prazo futuro, fluxo contínuo, curadoria visible_*, publicação recente + qualidade, ou valido + qualidade ≥80

## Fluxo contínuo

Não ocultar automaticamente quando houver:

- `status_prazo = fluxo_continuo`
- Texto: rolling basis, chamada permanente, continuously open, enquanto houver recursos, etc.

## Link health

Reaproveita `CORE/link_health.py`:

| Status | Efeito na visibilidade |
|--------|------------------------|
| `broken_spa_not_found` | Grants.gov `view-opportunity` legado → `hidden_invalid_link`; migrar para Simpler |
| `broken_404`, `timeout`, `invalid_url` | `hidden_invalid_link` se sem outro link |
| `forbidden_403`, `suspicious` | `review_link_suspicious` |

## Por fonte (orientação)

| Fonte | Orientação |
|-------|------------|
| NUCLEP | Ocultar conduta/home; manter licitação com objeto |
| EMBRAPII | Ocultar resultados e chamadas antigas encerradas |
| NEDO | Ocultar PDFs institucionais sem chamada |
| Grants.gov | Coleta Simpler (`Posted`/`Forecasted` → `visible_current`); `Closed`/`Archived` ou prazo passado → `hidden_*`; link legado `view-opportunity` → auditoria migração |
| AFWERX | Close date futuro → visible |
| SENAI / Plataforma Inovação | Vigentes + fluxo contínuo |
| FINEP / CNPq / CAPES / FAPs | Prazo futuro ou recente; ocultar resultado |

Relatório detalhado: `source_quality_report.json` da auditoria.

## Como auditar

```bash
python scripts/audit_editais_visibility_noise.py \
  --from-db --source all --limit 2000 \
  --output-dir audit_reports_main_pipeline/editais_visibility_noise_global
```

Opcional (lento): `--include-link-health --sample-per-source 20`

Saídas:

- `summary.json` / `summary.md`
- `hidden_candidates.json`, `review_candidates.json`
- `source_quality_report.json`
- `sql_updates_sugeridos.sql` (comentado)

## Aplicação em duas etapas (manual)

### Etapa 1 — segura (alta confiança)

**Arquivo:** `docs/sql/APPLY_EDITAIS_CURADORIA_FRONT_SAFE_STEP1.sql`  
**Plano:** `audit_reports_main_pipeline/editais_visibility_noise_global/step1_apply_plan.json`  
**Gerador:** `python scripts/generate_editais_curadoria_step1.py`

Inclui apenas:

| visibility | Critério |
|------------|----------|
| `hidden_institutional` | home, conduta, governança, etc. |
| `hidden_resultado` | resultado/homologação sem chamada ativa |
| `hidden_duplicate` | hash/link duplicado |
| `hidden_invalid_link` | link essencial quebrado (+ `extras.link_health` Grants) |

**Fora da etapa 1:** `hidden_historical`, `hidden_expired`, `hidden_not_opportunity`, todos os `review_*`.

Volume típico (auditoria 1232 itens): **326 UPDATEs** (234 visibilidade + 92 Grants `hidden_invalid_link` com `link_health`).

Ordem sugerida em staging:

1. `BEGIN` → executar `APPLY_EDITAIS_CURADORIA_FRONT_SAFE_STEP1.sql`
2. Validar contagem em `public.edital` (extras preenchidos)
3. **View:** usar `docs/sql/HOTFIX_VW_EDITAIS_FRONT_RELAX_VISIBILITY.sql` (conservador, ~906 linhas) — **não** `UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql` até a Etapa 2 (filtros temporais reduzem a view para ~312)
4. Conferir `vw_editais_front` (`NOTIFY` PostgREST já está no hotfix)

### Etapa 2 — ambíguos (pendente)

- `hidden_historical` (~198)
- `review_missing_deadline` (~504)
- `hidden_expired`, `hidden_not_opportunity`, `review_*`

## Aplicar manualmente (fluxo completo)

1. Revisar `hidden_candidates.json` e `step1_apply_plan.md`
2. Executar **etapa 1:** `APPLY_EDITAIS_CURADORIA_FRONT_SAFE_STEP1.sql`
3. Opcional etapa 2: `sql_updates_sugeridos.sql` (restantes, após revisão humana)
4. Aplicar `docs/sql/UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql` em staging
5. Validar:

```sql
SELECT fonte_recurso, COUNT(*) AS total
FROM public.vw_editais_front
GROUP BY fonte_recurso
ORDER BY total DESC;
```

## Reverter

- Remover ou ajustar `extras.curadoria_front` no registro
- Recriar view sem filtro (DDL anterior em `migrations/20260505_recreate_edital_views_credito_staging.sql`)

## Referências

- `CORE/editais_visibility.py` — motor de regras `editais_visibility_v1`
- `docs/DATA_RETENTION_AND_EXPIRATION_POLICY.md`
- `docs/EDITAIS_LINK_HEALTH_POLICY.md`

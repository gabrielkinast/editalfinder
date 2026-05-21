# Consolidado — Frente militar / técnico-científica (EditalFinder)

**Gerado:** 2026-05-20  
**Escopo:** Defesa, aeroespacial, espaço, pesquisa aplicada, indústria estratégica  
**JSON:** [consolidado_militar.json](./consolidado_militar.json)

---

## 1. Resumo executivo

A frente militar/técnico-científica do EditalFinder reúne **11 fontes já aplicadas** em staging, com **187 registros** no total:

| Tabela | Fontes | Registros |
|--------|-------:|----------:|
| `public.noticia` | 8 | **132** |
| `public.pesquisa` | 3 | **55** |

Pipeline: crawl → dry-run → subset → `load_news_research_sources.py` (staging). **Oportunidades** (DARPA BAA/RFI, ARL BAA) e hubs `.af.mil` bloqueados **não** entram no feed automático — ficam em **review/Radar** ou **latente**.

---

## 2. Fontes aplicadas por tabela

### `public.noticia` (8 fontes, 132 registros)

| `fonte_recurso` | Exibição | Registros | Classificação |
|-----------------|----------|----------:|---------------|
| `f35_news` | F-35 Lightning II | 20 | Corporativa (programa) |
| `lockheed_martin_news` | Lockheed Martin | 20 | Corporativa (indústria) |
| `darpa_news` | DARPA | 10 | Agência de pesquisa |
| `war_gov_news` | U.S. DoD / War.gov | 20 | Governo oficial |
| `nato_news` | NATO | 20 | Instituição internacional |
| `afrl_news` | AFRL | 12 | Laboratório (USAF) |
| `arl_news` | DEVCOM ARL | 12 | Laboratório (Army) |
| `space_force_news` | U.S. Space Force | 18 | Força (espaço) |

### `public.pesquisa` (3 fontes, 55 registros)

| `fonte_recurso` | Exibição | Registros | Tipo principal |
|-----------------|----------|----------:|----------------|
| `darpa_programs_research` | DARPA Programs | 25 | `programa_pesquisa` |
| `afrl_technology_areas` | AFRL Technology Areas | 12 | `area_tecnologica` (catálogo) |
| `arl_resources` | ARL Resources | 18 | portal/documento/programa |

---

## 3. Totais por fonte

Ver tabela acima. Subsets e `load_news_research_summary.json` em:

- `audit_reports_news_research/f35_news_subset_top20/`
- `audit_reports_news_research/lockheed_martin_news_subset_top20/`
- `audit_reports_news_research/darpa_news_subset_valido/`
- `audit_reports_news_research/war_gov_news_subset_top20/`
- `audit_reports_news_research/nato_news_subset_top20/`
- `audit_reports_news_research/afrl_news_subset_valido/`
- `audit_reports_news_research/arl_news_subset_valido/`
- `audit_reports_news_research/space_force_news_subset_valido/`
- `audit_reports_news_research/darpa_programs_research_subset_valido/`
- `audit_reports_news_research/afrl_technology_areas_subset_valido/`
- `audit_reports_news_research/arl_resources_subset_valido/`

---

## 4. Totais por eixo estratégico (agregado)

Contagem de **menções** nos subsets aplicados (um item pode ter vários eixos):

| Eixo | Menções |
|------|--------:|
| defesa | 83 |
| aeroespacial | 37 |
| espaco | 31 |
| geopolitica_tecnologica | 30 |
| industria_estrategica | 29 |
| pesquisa | 25 |
| engenharia_avancada | 20 |
| aviacao_militar | 19 |
| autonomia | 17 |
| ia_cyber | 10 |
| materiais_avancados | 10 |

Detalhe por fonte: `consolidado_militar.json` → `eixos_estrategicos.por_fonte`.

---

## 5. Notícias vs pesquisas

- **Notícias (70,6%):** narrativa recente (12m), operações, demonstrações, parcerias — feed de vigilância.
- **Pesquisas (29,4%):** programas DARPA, áreas tecnológicas AFRL, recursos ARL — estrutura de capacidades e TRL.

---

## 6. Fontes latentes e motivo

| Fonte | Status | Motivo |
|-------|--------|--------|
| `afrl_air_warfare_research` | latente | Diretoria RA 403; portal + highlights sem apply |
| `afrl_space_warfare_research` | latente | Diretoria RJ 403 |
| `afrl_technology_transition` | latente | RR portal; possivel_edital |
| `afrl_mission_highlights` | latente | Datas/recência; fetch live RA/RJ/RR |
| `afnwc_innovation` | precisa_melhoria | 4 válidos dry-run; revisar subset |
| `afnwc_weapon_systems` | precisa_melhoria | Hub 403; 1 registro |
| `afmc_news` | latente | 0 válidos; Wayback + relevância |
| `afnwc_news` | latente | 0 itens no lote dry-run |

---

## 7. Review candidates e motivo

| Grupo | Qtd | Destino | Motivo |
|-------|----:|---------|--------|
| `darpa_opportunities_research` | 9 | Radar / review | RFI/BAA — nunca `public.edital` auto |
| `arl_resources` BAA | 2 | Radar | `possivel_edital`; excluídos do subset pesquisa |
| `space_force_news` (review) | 2 | Radar/descarte | Oportunidade orçamentária ou discurso fraco |
| `afrl_strategic` | 1 | review | SBIR/AFWERX/sinal oportunidade |

Artefatos: `darpa_strategic_dryrun/review_candidates.json`, `military_research_expansion_dryrun/review_candidates.json`.

---

## 8. Observação de produto

As fontes desta frente são **oficiais governamentais**, **instituições internacionais** (OTAN) ou **comunicação corporativa** de defesa (Lockheed Martin, F-35). **Não são jornalismo independente.** O produto deve apresentar `fonte` / `fonte_recurso` de forma neutra e evitar tratar releases institucionais como cobertura editorial.

---

## 9. Como isso diferencia o EditalFinder

1. **Roteamento explícito** — notícia / pesquisa / review (Radar), separado do pipeline de editais.
2. **Curadoria técnica** — eixos estratégicos (defesa, espaço, IA, hipersonicos, …).
3. **Cobertura internacional + indústria** num inventário auditável (dry-run + subset + summary por fonte).
4. **Governança** — BAA/RFI não viram notícia nem edital automático.
5. **Rastreabilidade** — cada apply documentado em `load_news_research_summary.json`.

---

## 10. Próximas fontes futuras

1. **AFMC / AFNWC news** — estabilizar Wayback-first (prioridade alta).
2. **AFNWC Innovation** — subset após revisão manual.
3. **AFRL highlights / diretorias** — quando hubs .af.mil acessíveis.
4. **DefesaNet (BR)** — frente BR em paralelo ao lote internacional.
5. **Publicações OTAN** — pesquisa (fase seguinte).

---

## 11. Comandos SQL de validação

### Contagem por fonte — notícias

```sql
SELECT fonte_recurso, COUNT(*) AS n, COUNT(*) FILTER (WHERE ativo IS TRUE) AS ativos
FROM public.noticia
WHERE fonte_recurso IN (
  'f35_news','lockheed_martin_news','darpa_news','war_gov_news','nato_news',
  'afrl_news','arl_news','space_force_news'
)
GROUP BY fonte_recurso
ORDER BY n DESC;
```

### Contagem por fonte — pesquisas

```sql
SELECT fonte_recurso, COUNT(*) AS n, COUNT(*) FILTER (WHERE ativo IS TRUE) AS ativos
FROM public.pesquisa
WHERE fonte_recurso IN (
  'darpa_programs_research','afrl_technology_areas','arl_resources'
)
GROUP BY fonte_recurso
ORDER BY n DESC;
```

### Total da frente

```sql
SELECT 'noticia' AS tabela, COUNT(*) AS total
FROM public.noticia
WHERE fonte_recurso IN ('f35_news','lockheed_martin_news','darpa_news','war_gov_news','nato_news','afrl_news','arl_news','space_force_news')
UNION ALL
SELECT 'pesquisa', COUNT(*)
FROM public.pesquisa
WHERE fonte_recurso IN ('darpa_programs_research','afrl_technology_areas','arl_resources');
```

### Visibilidade nas views de front

```sql
SELECT fonte_recurso, COUNT(*) AS visiveis
FROM public.vw_noticias_front
WHERE fonte_recurso IN ('f35_news','lockheed_martin_news','darpa_news','war_gov_news','nato_news','afrl_news','arl_news','space_force_news')
GROUP BY fonte_recurso;

SELECT fonte_recurso, COUNT(*) AS visiveis
FROM public.vw_pesquisas_front
WHERE fonte_recurso IN ('darpa_programs_research','afrl_technology_areas','arl_resources')
GROUP BY fonte_recurso;
```

### Misroute DARPA (corretivo)

```sql
SELECT id, titulo, link, fonte_recurso
FROM public.pesquisa
WHERE lower(trim(coalesce(fonte_recurso,''))) IN ('darpa news','darpa_news')
   OR (link ILIKE '%darpa.mil/news/%' AND coalesce(fonte_recurso,'') <> 'darpa_programs_research');
```

Referências: `docs/sql/FIX_DARPA_PROGRAMS_RESEARCH_TYPES.sql`, `docs/sql/UPDATE_VW_PESQUISAS_FRONT_ATIVO.sql`.

---

## Referências

| Documento | Conteúdo |
|-----------|----------|
| [STRATEGIC_NEWS_RESEARCH_SOURCES.md](../../docs/STRATEGIC_NEWS_RESEARCH_SOURCES.md) | Mapa estratégico e §22 consolidado |
| [expansion_plan.md](../expansion_plan.md) | Ondas e lote militar |
| [BACKEND_SOURCES_INVENTORY.md](../../docs/BACKEND_SOURCES_INVENTORY.md) | Inventário backend |

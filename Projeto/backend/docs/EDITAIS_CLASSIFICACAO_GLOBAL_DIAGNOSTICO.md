# Diagnóstico global — classificação setorial nos editais (Editais / cards)

## Problema observado

Na página **Editais**, muitos cards mostravam (ou ainda mostram, conforme dados na BD) valores como **`defesa_industrial`**, **`aeroespacial`**, **`cyber_defesa`** para editais **genéricos** de pesquisa, inovação, saúde, educação, agro, etc. O fenómeno **não** se limita à FAPESC: aparece em **várias fontes**, o que aponta para causa **sistémica** (pipeline + taxonomia + merge), não para um único crawler.

## PARTE 1 — Origem dos campos no frontend (ficheiros analisados)

| Ficheiro | Papel |
|----------|--------|
| `frontend/EditalFinder-React/src/config/env.js` | `VITE_VIEW_EDITAIS` (padrão `vw_editais_front`). |
| `frontend/EditalFinder-React/src/services/dataService.js` | `getEditais()` lê a view configurada. |
| `frontend/EditalFinder-React/src/pages/Dashboard.jsx` | Orquestra lista, filtros, favoritos; em DEV pode registar amostra FAPESC. |
| `frontend/EditalFinder-React/src/utils/edital/editalRowMapper.js` | `mapRawEditalRow`: `setor_estrategico` → `setor_estrategico_raw`; `area_tecnologica` → `area_tecnologica_raw`; `setor_economico` → `setor_economico_raw`; `tags`, `extras_raw` preservados. |
| `frontend/EditalFinder-React/src/utils/edital/formatEditalUi.js` | `humanizeTaxonomyList`, `resumirEdital` (resumo do card). |
| `frontend/EditalFinder-React/src/utils/portaisDisplayLabels.js` | `humanizeTechnicalLabel` + overrides de slugs. |
| `frontend/EditalFinder-React/src/components/dashboard/EditalCard.jsx` | Meta do card: **Setor econômico**, **Setores estratégicos**, **Áreas tecnológicas** (humanizados); não junta mais tudo num único “Setor / Área tech”. |
| `frontend/EditalFinder-React/src/components/dashboard/EditalDetailsModal.jsx` | Detalhe: listas humanizadas + setor econômico. |

### Respostas (checklist)

1. **O card exibia “Setor / Área tech”?** Em versões anteriores, sim (uma linha). Na versão actual do repo, **não**: passou a **três linhas opcionais** (e humanização) — ver `EditalCard.jsx`.
2. **Usa `setor_estrategico`?** Sim — via `setor_estrategico_raw` (vindo da coluna / view).
3. **Usa `setor_economico`?** Sim — `setor_economico_raw`.
4. **Usa `area`?** No card compacto **não** como linha dedicada de “setor”; existe em `edital.area` para resumo/filtros. Modal: “Área (campo texto)”.
5. **Usa `area_tecnologica`?** Sim — `area_tecnologica_raw`.
6. **Usa `tags`?** **Não** directamente na secção setorial do card; podem existir no objecto para outras features.
7. **Usa `extras`?** **Não** directamente no card para essas três linhas; o mapper guarda `extras_raw`. A classificação nas colunas tipicamente veio do pipeline → `extras` → `extras_to_filter_columns` no loader.
8. **Junta vários campos?** O mapper **não** mistura `setor_estrategico` com `area` num só campo; cada um tem o seu `*_raw`. O **merge no backend** (extras + colunas) é que pode **acumular** listas longas ou incoerentes.
9. **Fallback que prioriza `setor_estrategico` indevidamente?** No front, **não** há fallback que copie `setor_economico` para `setor_estrategico`. O “prior” enganoso era **UX**: uma única etiqueta misturava estratégico + tecnológico.

## PARTE 2 — Banco vs view vs frontend

| Camada | Hipótese |
|--------|----------|
| **Frontend** | Mostrava dados **reais** da API; rotulagem antiga podia **parecer** que “área geral” = `setor_estrategico`. Humanização **não** corrige verdade dos dados. |
| **`public.edital`** | Se as colunas `setor_estrategico` / `area_tecnologica` estão preenchidas com os mesmos slugs em massa, a **contaminação está na tabela** (carga histórica + pipeline). |
| **`public.vw_editais_front`** | Se a view apenas projecta colunas da tabela **sem** transformação setorial, o padrão na view = padrão na tabela. Se houver `COALESCE` ou joins que injectem defaults, comparar com a tabela nas queries abaixo. |

### Queries manuais (preencher resultados no ambiente)

**A) Distribuição por fonte + setor_estrategico**

```sql
SELECT
  fonte_recurso,
  setor_estrategico,
  COUNT(*) AS total
FROM public.edital
WHERE ativo = true
GROUP BY fonte_recurso, setor_estrategico
ORDER BY total DESC
LIMIT 50;
```

**B) Amostra recente — tabela**

```sql
SELECT
  id_edital,
  titulo,
  fonte_recurso,
  tipo_oportunidade,
  tipo_recurso,
  setor_economico,
  setor_estrategico,
  area,
  area_tecnologica,
  tags,
  extras
FROM public.edital
WHERE ativo = true
ORDER BY id_edital DESC
LIMIT 30;
```

**C) Amostra recente — view**

```sql
SELECT
  id_edital,
  titulo,
  fonte_recurso,
  tipo_oportunidade,
  tipo_recurso,
  setor_economico,
  setor_estrategico,
  area,
  area_tecnologica,
  tags
FROM public.vw_editais_front
WHERE ativo = true
ORDER BY id_edital DESC
LIMIT 30;
```

### O que verificar nos resultados (checklist)

1. **`setor_estrategico` contaminado na tabela?** — Se (B) mostra os mesmos três slugs para títulos claramente não-defesa → **sim, na tabela**.
2. **Só na view?** — Se (B) ≠ (C) nas colunas de setor → investigar definição da view; caso contrário → **não é “só view”**.
3. **`setor_economico` mais coerente?** — Comparar (B) linha a linha; se sim, o UI pode **priorizar** setor econômico na hierarquia visual (proposta; ver plano de recovery / UX).
4. **`area` / `area_tecnologica`?** — Ver se `area_tecnologica` replica o mesmo ruído (ex.: regras “cyber” em `taxonomy_filtros`).
5. **`extras` com setores antigos?** — Inspeccionar JSON em (B); merge no loader preserva fragmentos (`loader.py` + `merge_extras_dict`).
6. **Mesmos setores em muitas fontes?** — Query (A): se o mesmo `setor_estrategico` aparece no topo para fontes diversas → regra **global** (ex.: `enrich_opportunity_classification` + `keyword_taxonomy`).

## PARTE 3 — Diagnóstico do pipeline (Python; ficheiros analisados)

| Ficheiro | Achados relevantes |
|----------|---------------------|
| `CORE/taxonomy_filtros.py` | `enrich_opportunity_classification`: `classify_thematic_tags` → `_thematic_to_setor_estrategico` → **`_merge_list("setor_estrategico", ...)`** que **acrescenta** a listas já vindas do crawler (**merge não destrutivo**). `extras_to_filter_columns` copia `extras['setor_estrategico']` para a coluna espelho. `calibrate_dod_sbir_sttr_extras`: se não há tags, **default** `["defesa_industrial", "aeroespacial", "defesa"]` (apenas quando essa calibração corre para fonte `dod_sbir_sttr`). `recovery_c_cap_setor_estrategico_br` só é chamado em **`calibrate_embrapii_extras`** e **`calibrate_nuclep_extras`** — **não** há cap global pós-enriquecimento para todas as fontes. |
| `CORE/transformer.py` | **`enrich_opportunity_classification(out)`** corre para **todas** as fontes antes dos `calibrate_*` específicos (ordem ~3024). |
| `CORE/loader.py` | `_rebuild_merged_extras` funde extras antigos (BD + fragmentos) com novos; `taxonomy_replace_keys` pode substituir chaves, mas **nem sempre** é usado. `_merge_db_row` com schema estendido pode **preservar** colunas espelho antigas se o payload novo vier vazio. |
| `keyword_taxonomy.py` (raiz do repo) | `THEMATIC_PATTERNS["aeroespacial"]` inclui **`"ita"`** como padrão. Em texto normalizado, **“digital”** contém a substring **`ita`** (…**dig**`ita`…). Isso dispara o tema **aeroespacial** em massa → `_thematic_to_setor_estrategico` → **`aeroespacial`** em `setor_estrategico`. Padrão **“defesa”** como substring pode sobre-disparar em textos com “defesa” não militar. |
| `defense_intel.py` / `asia_intel.py` / crawlers `defesa`, `diu`, etc. | Pacotes com `defesa_industrial` / `cyber_defesa` esperados **nessas** fontes; o risco sistémico é **mistura** com o enriquecimento global e **merge** acumulativo. |

### Respostas (pipeline)

1. **Regra global agressiva?** — Sim: **`enrich_opportunity_classification`** para **todas** as transformações + **`classify_thematic_tags`** com padrões **substrings curtas** (`ita` → falso positivo com “digital”).
2. **Default em defesa?** — Explícito só em **`calibrate_dod_sbir_sttr_extras`** quando tags vazias; não explica sozinho **todas** as fontes, mas soma ao ruído onde aplicável.
3. **Merge preservando setores antigos?** — Sim: `merge_extras_dict`, fragmentos `edital_extra_campo`, e `_merge_list` **unem** listas.
4. **Loader une listas?** — Sim, via extras + colunas espelho (`extras_to_filter_columns`).
5. **Overwrite só EMBRAPII/NUCLEP?** — O **cap por evidência** `recovery_c_cap_setor_estrategico_br` está ligado a **embrapii** e **nuclep**; **não** cobre FAPESC, FINEP, etc.
6. **Dados antigos acumulados?** — **Provável** em combinação com merges sucessivos sem `taxonomy_replace_keys` agressivo.

## PARTE 4 — UX / percepção (sem nova alteração obrigatória nesta entrega)

- **`setor_estrategico`** é **auxiliar / estratégico**; não deve ser tratado como “área principal” do edital sem contexto.
- Ajustes possíveis **após** validar queries: renomear para **“Marcadores estratégicos”**; esconder quando `classificacao_confianca` / `validacao_status` indicar baixa confiança; **priorizar** `area` + `setor_economico` no resumo. **Não** aplicar silenciosamente sem fechar o diagnóstico com dados reais do vosso Supabase.

## Causa provável (síntese)

| Prioridade | Causa |
|------------|--------|
| **Alta** | **`keyword_taxonomy.THEMATIC_PATTERNS`**: padrão **`ita`** dentro de `aeroespacial` → falsos positivos (ex.: **“digital”**). |
| **Alta** | **`enrich_opportunity_classification`** aplicado **globalmente** no `transformer.py` + **merge** que **acrescenta** a `setor_estrategico` em vez de substituir. |
| **Média** | **Merge de extras** e colunas espelho no **`loader.py`** preservando histórico. |
| **Média/baixa** | Calibradores pontuais (ex. DoD SBIR) e fontes `defense_intel` — relevantes para subconjuntos, não para explicar 100% das fontes sozinhos. |

**Origem dominante:** **pipeline / dados na BD**, com **contribuição de UX** antiga (rótulo único). O frontend **não inventa** `defesa_industrial`; **reflete** colunas + mapper.

## Riscos

| Área | Risco |
|------|--------|
| **Radar** | Se o Radar usa os mesmos campos para match/score, **ruído setorial** pode deslocar ranking ou matches (o pedido actual pediu **não** alterar score nesta tarefa — apenas registar risco). |
| **UX** | Utilizadores perdem confiança na taxonomia; filtros laterais por setor estratégico ficam **poluídos**. |
| **Favoritos** | **Diagnóstico separado** — ver secção abaixo; **não** misturar correção de favoritos com classificação. |

## Plano de correção recomendado (ordem)

1. Correr queries **A–C** em **staging** e colar resultados representativos neste doc (ou anexo).
2. Corrigir **`keyword_taxonomy.py`**: remover ou tornar **word-boundary** os padrões perigosos (`ita`, `iae` se falso positivo); testar com corpus de editais reais.
3. Avaliar **`_merge_list` para `setor_estrategico`**: modo **substituição** ou cap global pós-enriquecimento (nova função tipo `recovery_c_cap` genérica **conservadora**).
4. Recovery de dados: seguir **`docs/RECOVERY_CLASSIFICACAO_SETOR_GLOBAL_PLAN.md`** (dry-run, staging, validação).
5. Só então refinar **frontend** (prioridade de campos, ocultar quando suspeito).

---

## Anexo — Favoritos (só diagnóstico; não corrigir neste âmbito)

Verificar no browser (DEV) se aparecem:

- `[useEditalFavorites][DEV]` com `favoriteUserId` nulo em produção → cai em localStorage.
- `[favoritosService.toggleFavorito] Sem access_token` → sessão expirada.
- `[favoritosService.fetchFavoritos]` / `toggle` com `code`, `details`, `hint` → **RLS**, view, ou coluna em falta.
- Conflito **`id_usuario`** vs JWT.

Documentação relacionada: `docs/EDITAIS_FAVORITOS_ALERTAS_MVP.md` (secção debug pós-Auth).

---

## Ficheiros analisados (lista)

- `frontend/EditalFinder-React/src/pages/Dashboard.jsx`
- `frontend/EditalFinder-React/src/components/dashboard/EditalCard.jsx`
- `frontend/EditalFinder-React/src/components/dashboard/EditalDetailsModal.jsx`
- `frontend/EditalFinder-React/src/utils/edital/editalRowMapper.js`
- `frontend/EditalFinder-React/src/utils/edital/formatEditalUi.js`
- `frontend/EditalFinder-React/src/utils/portaisDisplayLabels.js`
- `frontend/EditalFinder-React/src/services/dataService.js`
- `frontend/EditalFinder-React/src/config/env.js`
- `CORE/taxonomy_filtros.py`
- `CORE/transformer.py`
- `CORE/loader.py`
- `keyword_taxonomy.py`
- `defense_intel.py` (referência grep)
- `docs/scripts/generate_recovery_c_setores_reports.py` (menção a pacotes genéricos)

## Resultado das queries sugeridas

_Preencher após execução manual no SQL Editor (staging/produção)._

## Precisa de Recovery global?

**Sim, é provável** — se as queries confirmarem os mesmos slugs na **`public.edital`** para títulos não relacionados a defesa. O recovery deve ser **gradual**, com **dry-run** e amostragem humana (ver plano dedicado).

## Build

**Nenhuma alteração de código** foi feita nesta entrega do relatório; **não** foi necessário `npm run build` para esta tarefa.

# Plano de recovery global — `setor_estrategico` / taxonomia (sem execução automática)

## Âmbito

Corrigir **contaminação** de `setor_estrategico` (e, se necessário, `area_tecnologica`) em **`public.edital`** quando a auditoria confirmar falsos positivos em massa (ex.: `aeroespacial` por padrão curto `ita` em “digital”, merges acumulativos, etc.).

**Não** executar este plano automaticamente a partir do repositório. **Não** alterar schema nesta fase. **Não** apagar linhas de edital. **Não** desactivar RLS. **Não** usar `service_role` no frontend.

Ver diagnóstico: [`EDITAIS_CLASSIFICACAO_GLOBAL_DIAGNOSTICO.md`](EDITAIS_CLASSIFICACAO_GLOBAL_DIAGNOSTICO.md).

---

## Estado do código (onda de correção taxonómica — 2026)

### Concluído no repositório (antes de qualquer `UPDATE` em BD)

1. **`keyword_taxonomy.py`**
   - Removidos padrões perigosos tipo **`ita`** isolado em `aeroespacial`.
   - `_pattern_matches`: frases com espaço → substring; tokens **≥12** caracteres → substring; tokens **mais curtos** → `re` com fronteiras `(^|[^a-z0-9])…([^a-z0-9]|$)` sobre texto **já normalizado** (sem acentos), para evitar substring dentro de palavras comuns.
   - Comentário de **excepções** no bloco de `THEMATIC_PATTERNS` (siglas curtas só com fronteira; sem tokens de 2–3 letras sem contexto).

2. **`CORE/taxonomy_filtros.py` — `enrich_opportunity_classification`**
   - **`setor_estrategico`**: deixa de usar merge por união com lista antiga.
   - Comportamento por defeito: **substitui** `extras["setor_estrategico"]` pelo resultado de `classify_thematic_tags` → `_thematic_to_setor_estrategico`.
   - Se existir lista anterior **diferente** (como conjunto), a lista antiga é guardada em **`extras["setor_estrategico_historico_merge"]`** (até 5 entradas, mais recente primeiro).
   - Se **`extras["setor_estrategico_crawler_locked"]`** for verdadeiro (`True`, `1`, `"true"`, `"yes"`, `"on"`), **não** altera `setor_estrategico` neste passo (curadoria explícita do crawler).

3. **Dry-run local (sem Supabase)**

   - Amostra / JSON à medida:

     ```text
     python scripts/dry_run_taxonomy_setor_recovery.py
     python scripts/dry_run_taxonomy_setor_recovery.py --json caminho/itens.json --out audit_reports/taxonomy_setor_dryrun.json
     ```

   - **Catálogo standardized** (102 ficheiros `*_standardized.json` em `audit_reports_retransform/standardized/`, **1294** editais na última geração):

     ```text
     python scripts/dry_run_recovery_classificacao_global_catalog.py
     python scripts/generate_recovery_classificacao_global_review.py
     ```

     Saídas geradas no repositório:

     - [`audit_reports_main_pipeline/recovery_classificacao_global_dryrun.json`](../audit_reports_main_pipeline/recovery_classificacao_global_dryrun.json)
     - [`audit_reports_main_pipeline/recovery_classificacao_global_dryrun.md`](../audit_reports_main_pipeline/recovery_classificacao_global_dryrun.md)
     - [`audit_reports_main_pipeline/recovery_classificacao_global_review.json`](../audit_reports_main_pipeline/recovery_classificacao_global_review.json) (após `generate_recovery_classificacao_global_review.py`)
     - [`audit_reports_main_pipeline/recovery_classificacao_global_review.md`](../audit_reports_main_pipeline/recovery_classificacao_global_review.md)

4. **Testes automáticos**

   ```text
   pytest tests/test_keyword_taxonomy.py -q
   ```

---

## Resultados do dry-run sobre o catálogo standardized (2026-05-13 UTC)

Corpus: **`audit_reports_retransform/standardized/`** (1294 editais). Método: para cada linha, `enrich_opportunity_classification` com taxonomia e merge actuais; comparação com `extras.setor_estrategico` **antes** (payload standardized) vs **depois** (simulação). **Não** reflecte estado live do Supabase; aproxima o efeito da próxima transformação global sobre estes artefactos.

| Métrica | Valor |
| --- | ---: |
| Editais analisados | 1294 |
| Mudariam `setor_estrategico` | 1114 |
| Perderiam `defesa_industrial` | 591 |
| Perderiam `aeroespacial` | 304 |
| Perderiam `cyber_defesa` **em `setor_estrategico`** | 0 (slug quase ausente nesta coluna; aparece sobretudo em `area_tecnologica` / `subtema`) |
| Ficariam sem `setor_estrategico` | 920 |
| … já estavam sem setor antes | 130 |
| … tinham slugs e passam a vazio | 790 |

**Top fontes por número de linhas alteradas:** Grants.gov (127), Fundação Araucária (88), China International Tendering MOFCOM (74), JSPS (40), European Defence Fund (39), CAS (34), NSFC (29), ANEEL (27), … (lista completa no JSON/MD).

**Sanidade em fontes militares / defesa** (contagens no relatório JSON; “regressão militar” = tinham slug *defense-like*, deixam de ter, e o texto contém marcadores militares em inglês heurísticos):

| Família (ficheiro / `fonte`) | Linhas | Com slug defense-like **depois** | Regressão militar (heurística) |
| --- | ---: | ---: | ---: |
| DoD SBIR/STTR | 15 | 15 | 0 |
| NUCLEP | 20 | 20 | 0 |
| AMAZUL | 19 | 5 | 0 |
| ESA OSIP | 17 | 3 | 0 |
| DARPA Opportunities | 15 | 1 | 9 |
| IARPA | 8 | 0 | 8 |

Interpretação: **DoD** e **NUCLEP** mantêm classificação defesa/aero coerente com o esperado neste corpus. **IARPA** e **DARPA** perdem muito `setor_estrategico` porque o texto está sobretudo em inglês (“Dept of the Army”, etc.) e os padrões temáticos actuais ainda não cobrem bem essas evidências; recomenda-se **`setor_estrategico_crawler_locked`** nessas fontes até extensão de padrões EN, ou calibração pós-enrich por fonte (sem alterar o score Radar nesta tarefa).

Detalhe de exemplos (boas / duvidosas / lock) e amostras completas: ver o **Markdown** e o **JSON** referidos acima.

---

## Validação amostral (pré-apply) — 2026-05-13 UTC

Artefactos gerados por `python scripts/generate_recovery_classificacao_global_review.py`:

- [`audit_reports_main_pipeline/recovery_classificacao_global_review.json`](../audit_reports_main_pipeline/recovery_classificacao_global_review.json)
- [`audit_reports_main_pipeline/recovery_classificacao_global_review.md`](../audit_reports_main_pipeline/recovery_classificacao_global_review.md)

Classificação **exclusiva** por linha: **D** (ficheiros IARPA / DARPA Opportunities / `darpa_news` se existir — política de `crawler_locked`) **>** `unchanged` **>** **C** (regressão provável: texto com marcadores militares EN e perda de slugs *defense-like*) **>** **B** (tinha `setor_estrategico` e fica vazio) **>** **A** (correção segura: remoção de ruído DI/aero/cyber sem evidência militar heurística, ou mudança coerente sem esvaziamento).

| Métrica (1294 linhas) | Valor |
| --- | ---: |
| **A** — apply global relativamente seguro (fora de ficheiros lock) | 310 |
| **B** — review manual recomendada | 633 |
| **C** — regressão provável (militar EN + perda de slugs) | 148 |
| **D** — linhas em ficheiros com lock obrigatório (IARPA + DARPA opps; 23 linhas neste corpus) | 23 |
| `unchanged` | 180 |
| Sem `setor_estrategico` após enrich | 920 |
| Tinham slugs e ficam vazios | 790 |

**Recomendação de apply em staging:** adoptar **Opção B** (lotes: primeiro ficheiros com baixo `pct_had_to_empty`, depois Brasil, depois internacional CTI, por fim defesa com spot-check). **IARPA** e **DARPA Opportunities** devem usar **`setor_estrategico_crawler_locked`** até calibração EN ou `calibrate_*` por fonte. **Opção A** (global exceto lock) só após tratamento da categoria **B** nas fontes críticas. **Opção C** como complemento cirúrgico. Listas concretas de ficheiros por política (`aplicar_recovery_normalmente`, `…_crawler_locked`, `…_calibracao_en`, `excluir_apply_global`) estão no JSON/MD do review.

---

## Pré-requisitos (quando for hora de dados)

1. Queries de distribuição e amostra (documento global) executadas em **staging**.
2. Correcção **commitada** (acima) **antes** ou **em paralelo** com recovery de dados — evita recontaminar na próxima carga.
3. Backup lógico ou snapshot da tabela `edital` (export CSV/PG dump) antes de `UPDATE` em massa.

## Fases propostas (execução real)

### 1) Diagnóstico por fonte

- Agregar: `fonte_recurso`, `setor_estrategico`, `count(*)`.
- Listar top 20 “tuplos” suspeitos: ex. `{defesa_industrial, aeroespacial, defesa}` repetidos em fontes não-defesa.
- Cruzar com `metodo_classificacao` / `extras->metodo_classificacao` se existir na coluna `extras`.

### 2) Recalcular com regra mais conservadora (código) — **feito no repo**

- `THEMATIC_PATTERNS` + matcher com fronteiras.
- Overwrite de `setor_estrategico` no enrich + histórico + lock de crawler.

### 3) Não preservar setores antigos na onda de “correcção taxonómica”

- No loader, considerar `taxonomy_replace_keys={'setor_estrategico', 'area_tecnologica'}` na primeira carga **após** fix do transformer, para **substituir** em vez de acumular (validar gancho em `_rebuild_merged_extras` nas rotas de upsert).

### 4) Overwrite controlado em `setor_estrategico` (dados)

- **Dry-run SQL**: `SELECT` com expressão de `UPDATE` simulada (CTE `proposta` + `JOIN` edital) contando linhas afetadas.
- Regras exemplo (ajustar com negócio):
  - Se `titulo`+`descricao` **não** contêm marcadores fortes de defesa **e** `setor_estrategico` ⊆ conjunto ruído conhecido → `setor_estrategico = '{}'`, ou `'{ciencia_tecnologia}'`, ou `NULL` conforme schema.
  - Fontes específicas: regras mais estritas ou mais permissivas.

### 5) Separar conceitos na persistência

- Manter `setor_economico`, `area`, `area_tecnologica`, `setor_estrategico` **coerentes**; não copiar automaticamente um para o outro.

### 6) Dry-run SQL

- Transacção `BEGIN` … `SELECT count(*) FROM edital WHERE <condição do update>;` … `ROLLBACK`.
- Exportar CSV de `id_edital`, titulo, setor_estrategico antes/depois simulado.

### 7) Validar amostras

- 50 linhas aleatórias por fonte grande (FAPESC, CNPq, FINEP, …).
- Revisão humana: “aceitável / inaceitável”.

### 8) Aplicar em staging (**não nesta tarefa**)

- `UPDATE` em batch com `atualizado_em = now()` e, se disponível, anotação em `extras` (`"taxonomy_recovery_wave": "2026-xx"`).

### 9) `post_daily_validation`

- Se existir job/script de validação diária no projecto, correr após carga/recovery para regressões.

### 10) Ajustar frontend

- Só **depois** dos dados estáveis: prioridade visual, labels, ocultação condicional.

## O que não fazer

- `UPDATE` cego `SET setor_estrategico = array[]` em toda a tabela sem critério.
- Apagar `extras` completo (perde histórico útil).
- Confiar apenas em humanização no UI como “fix” definitivo.

## Checklist de entrega pós-recovery

- [ ] Query (A) mostra distribuição mais diversa / menos colisão global.
- [ ] Amostra manual por 3 fontes críticas.
- [ ] Nova carga de uma fonte de teste não repõe o padrão tóxico (regressão no `keyword_taxonomy`).
- [ ] Radar smoke test (sem alterar motor de score, apenas verificar se listas não explodem).

## Build frontend

- Apenas após PRs que alterem código React; alterações só Python desta onda **não** exigem `npm run build`.

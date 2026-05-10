# Recovery B.1 AMAZUL — Consolidado

## 1. Resumo executivo

A Recovery B.1 teve como foco **falsos positivos de `credito_tipo_recurso_incoerente`** na AMAZUL (texto de licitação que mencionava “crédito” no sentido operacional, não linha bancária). A equipa aplicou em **staging** um pacote de **20** registos AMAZUL; a validação global manteve **`ok=true`** e **zero erros críticos**. O **ganho principal** foi a queda **global** de **`credito_tipo_recurso_incoerente` de 6 para 4**, alinhada à remoção dos **dois** casos AMAZUL identificados no diagnóstico (ids **2102** e **436**). O contador **`suspeito_ativo_true` permaneceu em 47** porque agrega **todo** o catálogo: a AMAZUL ainda contribui com **12** suspeitos no `warnings_by_source`, e as restantes linhas suspeitas vêm sobretudo de **outras fontes** ou de registos que **não entraram** neste lote de 20 updates. **Recomendação:** considerar a **B.1 AMAZUL concluída** quanto ao objetivo de crédito; **não** é necessário novo apply só para esse ganho; o passo seguinte é **curadoria / nova onda** para suspeitos e, à parte, **prazo vencido** e **setor amplo**.

## 2. Contexto

**Estado antes (pós Recovery B, referência da equipa):** validação global com `credito_tipo_recurso_incoerente` **6**, `suspeito_ativo_true` **47**, `prazo_vencido_ativo_true` **48**, `setor_estrategico_muito_amplo` **72**. Na AMAZUL, o diagnóstico apontava **2** créditos incoerentes, **12** suspeitos e **7** prazos vencidos ativos (subconjunto documentado).

**Problema que motivou a B.1:** ruído de classificação de **crédito/financiamento** em **licitações** AMAZUL; risco de decisões erradas no produto sem tocar em gates globais.

**Fonte afetada:** apenas **AMAZUL** (crawler + `CORE/taxonomy_filtros`, `CORE/item_quality` — fora do âmbito deste documento detalhar diff de código).

**Artefatos base:** `recovery_b1_amazul_diagnostico.json`, `recovery_b1_amazul_loader_dryrun.json`, `recovery_b1_amazul_apply_recommendation.json`, `staging_load_summary.json`, `post_daily_validation.json`.

## 3. O que foi alterado

### Código

- Calibração **local** AMAZUL: `reembolsavel=false` em ramos de compra pública / procurement; **cap** de `setor_estrategico` (≤ 3); ajuste de `validacao_status` em páginas de **detalhe de licitação** (p.ex. aviso `recovery_b1_amazul_licitacao_detalhe`). Ver alterações já integradas em `CORE/taxonomy_filtros.py` e `CORE/item_quality.py` (histórico da recovery).

### Crawler

- Sem mudança de escopo de fonte nesta onda documental; continuação do pipeline **amazul**.

### Transformação / qualidade

- Menos disparos da regra de **crédito incoerente** em licitação; standardized local do dry-run com **0** suspeitos na amostra gerada; staging recebeu payload alinhado ao dry-run (**0** erros de mapeamento no resumo).

## 4. Resultado operacional

| Métrica | Antes | Depois | Variação | Interpretação |
|---|---:|---:|---:|---|
| `credito_tipo_recurso_incoerente` | 6 | 4 | −2 | melhora — remoção dos 2 falsos positivos AMAZUL |
| `suspeito_ativo_true` | 47 | 47 | 0 | sem mudança global; AMAZUL mantém 12 no by_source |
| `prazo_vencido_ativo_true` | 48 | 48 | 0 | sem mudança; política de arquivo fora desta onda |
| `setor_estrategico_muito_amplo` | 72 | 72 | 0 | fora do escopo; dominado por outras fontes |

**Saúde do banco (staging):** `ok=true`, `critical_errors=0` no `post_daily_validation.json` referido.

## 5. Resultado por fonte

| Fonte | Antes | Depois | Ganho | Observação |
|---|---:|---:|---:|---|
| AMAZUL (`credito_tipo_recurso_incoerente`) | 2 (diagnóstico) | 0 no `by_source` analisado | −2 | Objetivo da B.1 atingido para este warning |
| AMAZUL (`suspeito_ativo_true`) | 12 | 12 | 0 | Fora do ganho principal desta onda |
| AMAZUL (`prazo_vencido_ativo_true`) | 7 | 7 | 0 | Prazos reais vencidos; documentar, não inventar datas |
| Outras fontes (crédito incoerente) | 4 | 4 | 0 | Trabalho futuro (CNPQ, FAPEMIG, FAPERGS, IPEN nos exemplos) |

## 6. Interpretação

- **Ganho real:** a métrica global de **crédito incoerente** desceu **2** unidades de forma **coerente** com a correção **AMAZUL**; o validador deixa de listar AMAZUL nesse `by_source`.
- **`suspeito_ativo_true` estável (47):** não é falha da validação global — a B.1 **não prometeu** limpar suspeitos em massa; o agregado inclui **dezenas** de linhas noutras fontes; na AMAZUL os **12** suspeitos exigem **outra** intervenção (regras ou curadoria).
- **Prazo vencido / setor:** ausência de mudança **não invalida** a recovery; apenas indica que o **próximo investimento** de produto/dados deve ser outra onda (política de `ativo`, arquivo, ou cap de setor **transversal**).

## 7. Riscos e limitações

- **Suspeitos AMAZUL (12)** continuam visíveis em relatórios e possivelmente no frontend se não houver filtro/badge.
- **Lote de 20 linhas:** outras URLs AMAZUL em staging podem não refletir o último `amazul_standardized.json` do dry-run B.1.
- **Crédito incoerente remanescente (4)** pode gerar pressão de “trabalho incompleto” se só se olhar para o total global — clarificar que **saiu da AMAZUL**.
- **Prazos vencidos** com `ativo=true` geram ruído operacional até existir política explícita.

## 8. Decisão recomendada

**Decisão recomendada:** **concluir** a Recovery **B.1 AMAZUL** em relação ao objetivo de **crédito incoerente**; **não** abrir nova rodada **só AMAZUL** para esse warning. **Não aplicar** novamente o mesmo pacote sem mudança de código. **Próximo alvo sugerido:** onda **multi-fonte** para **`suspeito_ativo_true`** e/ou **Recovery / onda dedicada** a **`setor_estrategico_muito_amplo`** e política de **`prazo_vencido_ativo_true`**.

## 9. Próximos passos

1. Revisar as **12** linhas AMAZUL ainda `suspeito` (lista no `post_daily_validation` / exemplos).
2. Tratar os **4** `credito_tipo_recurso_incoerente` restantes **fora** da AMAZUL.
3. Definir **política de arquivo** ou `ativo=false` para prazos historicamente vencidos (sem inventar datas).
4. Manter **`validate_full_staging_after_daily.py --staging`** após cargas relevantes.

## 10. Evidências técnicas

**Arquivos lidos**

- `audit_reports_main_pipeline/recovery_b1_amazul_diagnostico.json`
- `audit_reports_main_pipeline/recovery_b1_amazul_loader_dryrun.json`
- `audit_reports_main_pipeline/recovery_b1_amazul_apply_recommendation.json`
- `audit_reports_loader_ready/staging_load_summary.json` (apply **2026-05-10T06:26:21Z**, 20 atualizados, 0 erros)
- `audit_reports_main_pipeline/post_daily_validation.json` (validação **2026-05-10T06:32:32Z**, staging)

**Arquivos gerados / atualizados (documentação)**

- `audit_reports_main_pipeline/recovery_b1_amazul_consolidado.md`
- `audit_reports_main_pipeline/recovery_b1_amazul_consolidado.json` (inclui `padrao_documentacao_onda`)

**Comandos (ciclo B.1 documentado; não reexecutados nesta edição do relatório)**

- `python amazul/main_amazul.py`
- `python scripts/retransform_all.py --sources amazul --dry-run --output-dir audit_reports_main_pipeline/recovery_b1_amazul`
- `python scripts/audit_semantic_classification.py` (dirs em `recovery_b1_amazul_loader_dryrun.json`)
- `python scripts/load_ready_sources.py --dry-run --sources amazul ...` (comando completo em `recovery_b1_amazul_loader_dryrun.json`)

**Segurança e restrições**

- **Apply:** não executado na geração deste markdown; apply AMAZUL em staging foi feito **antes** pela equipa.
- **Supabase / schema / readiness / opportunity_gate global:** **sem alterações** nesta tarefa de relatório.

**Template reutilizável:** `scripts/recovery_report_template.py` — usar em futuros `*_consolidado.{md,json}`.

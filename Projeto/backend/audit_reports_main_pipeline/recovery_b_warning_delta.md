# Recovery B — delta de warnings (`prazo_vencido_ativo_true` e `credito_tipo_recurso_incoerente`)

## Metodologia

- **Baseline (antes da Recovery B):** totais globais em `audit_reports_main_pipeline/recovery_a_consolidado.json` → `validacao_global_pos_carga` (validação staging com timestamp **2026-05-10T04:59:30Z**): **`prazo_vencido_ativo_true` = 41**, **`credito_tipo_recurso_incoerente` = 4**.
- **Depois:** `audit_reports_main_pipeline/post_daily_warning_examples.json` (**2026-05-10T05:51:55Z**): **48** e **6**.
- **Histórico `post_daily_warning_examples` pré-Recovery B:** não há segunda cópia do ficheiro no repositório; a atribuição por fonte no “antes” usa **decomposição aritmética** (ver JSON).

## `prazo_vencido_ativo_true` (41 → 48, **+7**)

### Por fonte (`summary_by_warning` → `by_source`, estado atual)

| Fonte | Contagem |
|-------|----------:|
| AMAZUL | 7 |
| CNPQ | 10 |
| EMBRAPII | 9 |
| Grants.gov | 9 |
| IARPA | 8 |
| ANP | 2 |
| Apex Brasil | 1 |
| BDMG | 1 |
| NATO DIANA | 1 |
| **Soma** | **48** |

### Onde entram Ambev e BADESUL

- **Ambev** e **BADESUL**: **0** linhas neste warning (não entram no `by_source`).

### Leitura do aumento global

- Soma **sem AMAZUL**: 48 − 7 = **41**, igual ao total global **antes** da Recovery B.
- Logo, o **+7** no agregado corresponde, na prática, às **7** ocorrências **AMAZUL** que passam a entrar na contagem deste warning (licitações com `prazo_envio` vencido e `ativo=true`), sem necessidade de supor alterações nas outras fontes entre os dois cortes temporais.

### Exemplos (amostra `examples_by_warning`)

Incluem, entre outros, dispensa por valor AMAZUL com `prazo_envio` datado e `motivo` explícito de prazo vencido — ver `recovery_b_warning_delta.json`.

---

## `credito_tipo_recurso_incoerente` (4 → 6, **+2**)

### Por fonte (estado atual)

| Fonte | Contagem |
|-------|----------:|
| AMAZUL | 2 |
| CNPQ | 1 |
| FAPEMIG | 1 |
| FAPERGS | 1 |
| IPEN | 1 |
| **Soma** | **6** |

### Ambev e BADESUL

- **0** em ambas.

### Leitura do aumento global

- Soma **sem AMAZUL**: 6 − 2 = **4**, igual ao total **antes**.
- O **+2** corresponde às **2** linhas **AMAZUL** com `motivo` do validador sobre crédito/financiamento sem `reembolsavel` / `natureza_recurso` (itens de licitação com `tipo_recurso` “licitação” ainda disparam a heurística — candidato a ajuste futuro de regra ou extras, **fora** do âmbito deste relatório).

---

## Conclusão (fontes Recovery B)

| Fonte | `prazo_vencido_ativo_true` | `credito_tipo_recurso_incoerente` |
|-------|----------------------------|-------------------------------------|
| **AMAZUL** | **7** (explica **+7** global) | **2** (explica **+2** global) |
| **Ambev** | 0 | 0 |
| **BADESUL** | 0 | 0 |

Os aumentos agregados **não** são explicados por Ambev nem BADESUL no estado atual do `post_daily_warning_examples.json`; concentram-se em **AMAZUL**, coerente com a carga/atualização dessa fonte após a Recovery B e com o validador a aplicar regras de prazo e coerência de crédito a linhas já mapeadas como `edital`.

---

Versão estruturada: **`recovery_b_warning_delta.json`**.

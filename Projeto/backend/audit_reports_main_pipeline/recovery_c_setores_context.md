# Recovery C — Setores estratégicos (contexto)

Gerado em **2026-05-10T06:56:08Z**.

## Situação na validação global

- **ok:** `True`
- **Erros críticos:** 0
- **setor_estrategico_muito_amplo (total edição):** **72**

## Ranking de fontes (warning setor amplo)

| Fonte | setor_estrategico_muito_amplo | total warnings (fonte) |
|---|---:|---:|
| EMBRAPII | 13 | 22 |
| NUCLEP | 12 | 12 |
| DoD SBIR/STTR | 9 | 9 |
| EIC | 9 | 9 |
| Eureka Network | 5 | 5 |
| DIU | 3 | 3 |
| European Defence Fund | 3 | 3 |
| Ministério da Defesa | 3 | 3 |
| Mitsubishi Heavy Industries (Suppliers) | 3 | 3 |
| IPEN | 2 | 3 |
| AFWERX | 2 | 2 |
| ANEEL | 2 | 2 |
| SENAI | 1 | 3 |
| CNEN | 1 | 1 |
| CONFAP | 1 | 1 |

## Por que o excesso?

O enrich_opportunity_classification agrega tags temáticas em setor_estrategico e mantém até 4 entradas; várias fontes recebem pacotes defesa_industrial+aeroespacial+ciencia_tecnologia+industria sem poda por evidência. URLs de listagem e textos longos aumentam acertos genéricos.

## Estratégia de correção (fase 1)

Recovery C: função recovery_c_cap_setor_estrategico_br em calibrate_embrapii_extras e calibrate_nuclep_extras — máximo 3 setores com pontuação por evidência em título/descrição/URL/tipos; excedentes em tags_secundarias; lista completa também em setores_detectados. NUCLEP: páginas institucionais (quem somos, composição, etc.) recebem tipo_oportunidade noticia_institucional + aviso recovery_c_nuclep_pagina_institucional.

## Exemplos EMBRAPII (validator)


## Exemplos NUCLEP (validator)


## Referências

- `audit_reports_main_pipeline/recovery_a_consolidado.json`
- `audit_reports_main_pipeline/recovery_b_consolidado.json`
- `audit_reports_main_pipeline/recovery_b1_amazul_consolidado.json`
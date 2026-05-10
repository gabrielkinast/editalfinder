# Recovery C — Diagnóstico por fonte (EMBRAPII / NUCLEP)

## Estado **após** retransform Recovery C

Pasta standardized: `audit_reports_main_pipeline/recovery_c_setores/standardized`

Neste bundle, **não há** itens com mais de 3 setores — a calibração já foi aplicada no pipeline.

## EMBRAPII (pós-transformação)

- Itens: **21**
- Com `setor_estrategico` > 3: **0**

## NUCLEP (pós-transformação)

- Itens: **20**
- Com `setor_estrategico` > 3: **0**

---

## Linha de base (**antes** da calibração no código)

Simulação sobre `audit_reports_retransform/standardized` (13 itens EMBRAPII e 12 NUCLEP com 4 setores) documentada em:

`audit_reports_main_pipeline/recovery_c_setores_diagnostico_linha_base.json`

Para cada item: `setor_antes`, `setor_depois_simulado` (top 3 por evidência), `excedentes` movidos para tags/secundários no fluxo real.

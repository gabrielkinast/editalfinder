# Lote 3A — diagnóstico fontes japonesas

## Ambiente desta execução

- Crawlers: exit 0; listagens falharam; `*_editais.json` com 0 itens.
- Retransform (`audit_reports_blocked_sources/lote3a_fix_japan`): 0 brutos / 0 transformados.
- Calibrações `calibrate_japan_*_extras` em `CORE/taxonomy_filtros.py` e chamadas em `CORE/transformer.py`.

## Por fonte

### japan_jst

- Readiness sugerido (este relatório): **blocked — sem itens úteis após crawl neste ciclo; repetir crawl com acesso às origens; não promover readiness com JSON vazio.**
- Bruto atual / std canônico: **0** / **0**
- Problema principal: acesso_rede_ou_listagem; lógica do crawler ok
- Natureza (canônico/histórico): Histórico frequentemente vazio ou listagens inacessíveis.

### japan_jaea

- Readiness sugerido (este relatório): **blocked — sem itens úteis após crawl neste ciclo; repetir crawl com acesso às origens; não promover readiness com JSON vazio.**
- Bruto atual / std canônico: **0** / **30**
- Problema principal: acesso_rede_ou_listagem; lógica do crawler ok
- Natureza (canônico/histórico): Mix: página R&D Results / annual report (notícia ou institucional), não edital; procurement real pode existir mas com ruído.

### japan_jaxa

- Readiness sugerido (este relatório): **blocked — sem itens úteis após crawl neste ciclo; repetir crawl com acesso às origens; não promover readiness com JSON vazio.**
- Bruto atual / std canônico: **0** / **1**
- Problema principal: acesso_rede_ou_listagem; lógica do crawler ok
- Natureza (canônico/histórico): Índice institucional / imprensa (página genérica), não chamada.

### japan_e_rad

- Readiness sugerido (este relatório): **blocked — sem itens úteis após crawl neste ciclo; repetir crawl com acesso às origens; não promover readiness com JSON vazio.**
- Bruto atual / std canônico: **0** / **1**
- Problema principal: acesso_rede_ou_listagem; lógica do crawler ok
- Natureza (canônico/histórico): Procedimento de registro (organ/procedure), não grant.

## Listas

- **Pode sair de blocked:** nenhuma neste ciclo (sem dados novos válidos).
- **Continua blocked / manual:** as quatro até crawl bem-sucedido e itens reais.

## 3B China

Repetir o mesmo pipeline para fontes china_* prioritárias (ex.: caea, cas, most, tendering): diagnóstico, filtros locais, calibrate_*_extras se necessário, crawl, retransform dry-run, auditorias semântica/docs/acesso, sem loader apply.

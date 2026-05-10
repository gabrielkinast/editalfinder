# Investimentos Wave 1 — diagnóstico (apex, bndes, eic)

**Data:** 2026-05-10  
**Standardized analisado:** `audit_reports_retransform/standardized/{apex,bndes,eic}_standardized.json`

## Volumes atuais

| Fonte | N.º de itens no standardized (retransform) |
|--------|---------------------------------------------|
| apex | 2 |
| bndes | 19 |
| eic | 14 |

## Apex

- **Situação:** o ficheiro standardized atual tem apenas **dois** URLs: um produto (IAra), outro institucional/transparência (“licitações e contratos”). Ambos aparecem com **qualidade limitada** e `validacao_status` problemático no rasto existente — não são uma base larga de “investimento” no mesmo sentido que BNDES/EIC.
- **Portais/hubs úteis (fora do JSON mínimo, mas usados no projeto):** internacionalização de empresas, Exporta Mais Brasil, IAra, Qualifica (ver `apex/extrair_informacoes_apex.py` e `apex/outputs/`).
- **Chamadas individuais em `public.edital`:** no standardized atual não há editais de concurso; no futuro, chamadas Apex com objeto/prazo devem seguir o pipeline **edital**.
- **Ruído:** páginas de transparência/licitações não entram na Wave 1 de **investimentos/portais estratégicos**.
- **Wave 1 portal_estrategico:** cinco hubs curados em `investimentos_wave1_portais/standardized/apex_standardized.json` (internacionalização ×2 URLs canónicas, exporta mais, IAra sem UTM, Qualifica).

## BNDES

- **Situação:** a maior parte dos 19 itens são **chamadas públicas nomeadas** (FIP IA 2026, ETF, mitigação climática, IoT, energia sustentável, etc.) — são **candidatos naturais a `public.edital`**, não a substituir por um único portal estratégico.
- **Portais/hubs:** níveis agregadores do site WPS — `mercado-de-capitais`, `fundos-de-investimentos`, listagem de **chamadas para seleção de fundos**, **CRIATEC**, eixo **fundos em empresas e projetos**.
- **Ruído:** URLs com estado longo `!ut/p/...` são frágeis para curadoria; na Wave 1 preferimos **âncoras de secção** sem token quando possível.
- **Wave 1:** cinco hubs em `bndes_standardized.json` dedicado — **nenhuma** URL de FIP/chamada individual da lista atual.

## EIC

- **Situação:** 14 itens misturam **páginas de programa** (Pathfinder, Transition, Accelerator, STEP), **listagem** `eic-funding-opportunities_en`, **calls 2026** (`calls-proposals/...`) e **PDFs**.
- **Portais/hubs:** listagem principal + páginas estáveis de programa (Pathfinder, Transition, Accelerator, STEP Scale).
- **Chamadas individuais:** `eic-accelerator-2026_en`, `eic-step-scale_en` — manter lógica **edital**; não foram incluídas na Wave 1 de `portal_estrategico`.
- **Ruído:** PDFs isolados (DPN, work programme como único link) — excluídos da Wave 1 como portal.
- **Wave 1:** cinco URLs de programa/hub em `eic_standardized.json` dedicado.

## Taxonomia alinhada a `portal_estrategico`

- `categoria`: **investimentos**
- `portal_tipo`: valores da lista técnica (investment, funding_hub, internationalization, …)
- `extras` canónicos: `frontend_section=investimentos`, `mostrar_no_radar=false`, `mostrar_em_investimentos=true`, `mostrar_em_fornecedores=false`, `investment_portal=true`, `wave=investimentos_wave1`

## JSON

Detalhe estruturado: `investimentos_wave1_diagnostico.json`

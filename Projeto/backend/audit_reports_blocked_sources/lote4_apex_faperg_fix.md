# Correção lote 4 — Apex e FAPERGS (`faperg`)

**Data:** 2026-05-02  

**Escopo:** ajustes locais de crawler, `scraper_generic`, calibrações e relaxamento **local** do gate no transformer (`apex` / `faperg`). Não foi executado loader apply, nem migrations, nem alteração global do `opportunity_gate`. O ficheiro `source_readiness.json` **não** foi atualizado automaticamente.

## Resumo pós-correção (retransform dry-run)

| Fonte  | Brutos | Transformados | Rejeitados |
|--------|--------|---------------|------------|
| apex   | 3      | 3             | 0          |
| faperg | 2      | 2             | 0          |

Relatório detalhado: `audit_reports_blocked_sources/lote4_fix_apex_faperg/retransform_by_source.json`.

## ApexBrasil

**Problema anterior:** um único item com título “Menu” / página de eventos genérica.  

**Correção:**

- Seeds focados em **Exporta Mais**, **transparência** e **internacionalização** (URLs `/content/...` e `exporta-mais-brasil`), sem listagem ampla de eventos/notícias.
- Filtros de URL (bloqueio de `/eventos`, `/noticias`, `/conteudo/noticias/`, redes sociais, `brasilexportacao.com.br`, etc.), títulos de navegação e sinais fortes no link e no corpo antes de persistir.
- `utils_apex.get_soup`: **curl `-skL` primeiro**, depois `requests` (reduz 404 em redirects).
- **Transformer:** `calibrate_apex_extras`, `_apex_soft_continue` e exclusão de `build_defense_extras` para a fonte `apex`.

**Bruto atual:** três inscrições **Exporta Mais** (domínio `crm-apps.apexbrasil.com.br`) com descrição substantiva (programa, empresas, exportação).

**Readiness recomendado:** **ready_with_notes** — oportunidades reais, mas formulário CRM sem PDF no bruto; convém revisão humana de área/taxonomia (auditoria semântica apontou `tipo_oportunidade_generico` em parte dos itens agregados).

## FAPERGS (pasta `faperg`)

**Problema anterior:** 0 brutos (URLs antigas e/ou bloqueio TLS/403 com `requests`).

**Correção:**

- Listagem: `https://fapergs.rs.gov.br/chamadas-e-editais`.
- `scraper_generic.fetch_soup`: fallback **curl `-skL`**.
- Não gravar a própria página de listagem como item (`link == listing`).
- Exclusão de páginas de **RH/PSS** (`/selecao-2025`, convocação PSS) e de resultados preliminares/finais onde configurado.
- **Transformer:** `calibrate_faperg_extras` (UF **RS**, origem **FAPERGS**), `_faperg_soft_continue` e exclusão de `build_defense_extras` para `faperg`.

**Bruto atual:** 2 itens (ex.: Centelha/aditivo; edital SICT–FAPERGS inovação), com PDF preservado em pelo menos um caso no dry-run.

**Readiness recomendado:** **ready_with_notes** — cobertura depende do HTML da listagem; validar se `/abertos` ou outras rotas devem ser acrescentadas após inspeção manual.

## Auditorias auxiliares

- Semântica: `audit_reports_blocked_sources/lote4_fix_apex_faperg_semantic/audit_semantic_summary.json`
- Documentos: `audit_reports_blocked_sources/lote4_fix_apex_faperg_docs/audit_docs_summary.json` (inclui contagem de downloads falhados, se houver)

## JSON consolidado

Métricas e recomendações estruturadas: `audit_reports_blocked_sources/lote4_apex_faperg_fix.json`.

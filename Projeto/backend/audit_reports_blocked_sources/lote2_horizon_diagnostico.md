# Lote 2 — Diagnóstico Horizon Europe (output antes da correção do crawler)

**Ficheiro:** `horizon_europe/outputs/horizon_europe_editais.json`  
**Itens:** 18  
**Data:** 2026-05-02  

## Conclusão executiva

Todos os 18 registos são **a mesma página institucional do programa** “Horizon Europe” em **variantes de idioma** (`horizon-europe_en`, `horizon-europe_bg`, …). Não há **topic id**, **call id**, **deadline** nem metadados de concurso. **Não servem como oportunidades concretas.**

## Contagens por tipo (classificação pedida)

| Tipo | Quantidade |
|------|------------|
| pagina_institucional_generica | 18 |
| variante_idioma | 18 |
| programa_geral | 18 |
| funding_topic | 0 |
| call_for_proposals | 0 |
| work_programme | 0 |
| documento | 1 (nota) |
| outro | 0 |

**Nota “documento”:** só o item `horizon-europe_en` inclui PDFs institucionais (apresentação do programa); não são editais nem topics.

## Causa técnica

- A listagem usada (`research-and-innovation.../horizon-europe_en`) expõe links de **mudança de idioma** para o mesmo conteúdo.
- O filtro `link_url_must_contain_any` incluía **`horizon`**, o que coincide com o slug `horizon-europe_XX` sem exigir `topic-details` ou identificador de chamada.

## Fonte pública mais adequada (sem login, sem scraping agressivo)

O portal disponibiliza **HTML estático** com milhares de links para páginas de detalhe de tópicos:

- `https://ec.europa.eu/info/funding-tenders/opportunities/data/topic-list.html`

Cada entrada relevante aponta para URLs do tipo:

- `.../portal/screen/opportunities/topic-details/horizon-...`

**Filtro recomendado:** aceitar apenas URLs que contenham **`/topic-details/horizon-`**, excluindo `funding-programmes-and-open-calls/horizon-europe` e `topic-search` sem detalhe.

## Correções aplicadas (resumo)

Ver `horizon_europe/main_horizon_europe.py` e `scraper_generic.py` (`link_url_must_contain_all`). O crawler passa a usar `topic-list.html`, exige `horizon-` no segmento do tópico, deduplica por slug e remove rotas institucionais genéricas.

## Readiness (após nova execução)

Avaliar com base no dry-run de retransformação e nas auditorias em `audit_reports_blocked_sources/lote2_fix_horizon_*`.

### Atualização pós-correção (2026-05-02)

- **Crawler:** `topic-list.html` + filtro `/topic-details/horizon-` → **25** tópicos reais (códigos HORIZON-CL2-…), sem variantes `horizon-europe_XX`.
- **Retransform (dry-run):** 25 brutos, **25 transformados**, 0 rejeitados; **25 suspeitos** (qualidade média ~53; descrição mínima porque muitas páginas de detalhe são **SPA / pouco HTML**).
- **Auditoria semântica:** flag `oportunidade_fomento_sem_fomento` em **25/25** (ajuste futuro de taxonomia/transformer por fonte, **fora** do gate global nesta tarefa).
- **Auditoria de documentos:** sem PDFs/anexos no bruto; sem perdas.
- **Recomendação:** ver secção final da resposta do assistente (`needs_manual_review` + manter **blocked** na lista até revisão e eventual enriquecimento de detalhe/prazo).

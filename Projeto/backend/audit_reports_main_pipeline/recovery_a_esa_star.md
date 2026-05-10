# Recovery A — ESA STAR

## Resultado

- **Crawler:** removido fallback para `https://esastar-publication-ext.sso.esa.int`; domínios permitidos apenas públicos (`esa.int`, `procurement.esa.int`, `esamultimedia.esa.int`); exclusão explícita de `sso.esa.int`.
- **Output bruto:** `[]` com `coleta_vazia_confirmada` (`allow_empty=True`).
- **Standardized (pasta isolada):** 0 itens.

## Conclusão

Não há, neste momento, **listagem HTML estável** a partir das URLs oficiais configuradas que produza links de ITT públicos passando nos filtros de ação/tender **sem** apontar para SSO. **Manter `blocked` no readiness oficial** até existir seed/feed/sitemap público com oportunidades verificáveis.

## Ficheiros

- JSON: `recovery_a_esa_star.json`
- Raw: `recovery_a/raw/esa_star_editais.json`

# NASA Wave 2 — build de payloads (sem Supabase)

- Gerado: `2026-05-09T14:00:40Z`
- Entrada: `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\standardized\nasa_news_standardized.json`
- Linhas entrada: **95**
- Após dedupe: **95** (removidos **0**)

## Payloads de carga (validados pelo contrato do loader)

- `nasa_wave2_payload_noticia.json`: **76** itens
- `nasa_wave2_payload_pesquisa.json`: **19** itens

## Fora dos payloads de carga

- `nasa_wave2_review_candidates.json`: **0** (não carregados pelo loader)
- Rejeitados por roteamento (`rejected_noise`): **0**
- Excluídos na validação (campos/genérico): **0**

## Validações

- Links únicos (notícia): **True**
- Links únicos (pesquisa): **True**
- Sobreposição notícia/pesquisa: **0** links
- **Nenhum** item destinado a `public.edital` neste módulo.

## Próximo passo

```
python scripts/load_news_research_sources.py --dry-run --staging --wave nasa_wave2
```

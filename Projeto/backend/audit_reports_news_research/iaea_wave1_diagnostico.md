# IAEA Wave 1 — diagnóstico

- Gerado: `2026-05-05T01:42:11Z`
- Standardized: `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\standardized\iaea_news_publications_standardized.json`

## Seeds (config)

```json
{
  "seed_urls_news": [
    "https://www.iaea.org/feeds/topnews",
    "https://www.iaea.org/feeds/news"
  ],
  "seed_urls_publications": [
    "https://www.iaea.org/feeds/publications"
  ],
  "seed_urls_legacy": [
    "https://www.iaea.org/feeds/topnews",
    "https://www.iaea.org/feeds/news",
    "https://www.iaea.org/feeds/publications"
  ],
  "page_enrich_max": 36,
  "max_items": 55
}
```

## Contagens

- Total itens (standardized): **45**
- Por `tipo_conteudo`: `{'pesquisa': 15, 'noticia': 30}`
- Por `extras.seed_kind`: `{'publications': 15, 'news': 30}`
- `missing_summary` (heurística): **26**
- Sem `data_publicacao`: **0**
- Genéricos (heurística `_is_generic`): **0**

### Por seed URL (agregado no standardized)

```json
{
  "https://www.iaea.org/feeds/publications": 15,
  "https://www.iaea.org/feeds/topnews": 15,
  "https://www.iaea.org/feeds/news": 15
}
```

## Por que `missing_summary`?

Resumo curto ou ausente quando: (1) o item RSS não traz `description` útil; (2) o HTML da página não foi obtido (429/403/timeout); (3) a página não tem `meta description`/`og:description` nem parágrafo `<p>` suficientemente longo após strip HTML.

## Por que itens sem data?

Sem `data_publicacao` quando: (1) `pubDate` ausente ou num formato não parseado; (2) meta/JSON-LD sem datas válidas na página; (3) URL sem segmento de data reconhecível; (4) item é hub/listagem sem data editorial.

## Campos típicos RSS/Atom

- `title`, `link`, `description|encoded|summary|content`, `pubDate|published|updated`

## Enriquecimento (meta / JSON-LD / parágrafo / URL)

Os feeds RSS/Atom da IAEA expõem tipicamente: `title`, `link`, `description` (ou `summary`/`content` em Atom), `pubDate` ou `published`/`updated`. Muitos itens chegam com `description` vazio ou HTML mínimo — daí `missing_summary` até enriquecimento por página (`meta description`, `og:description`, primeiro `<p>` útil em `<main>`/`<article>`, datas em `article:published_time` / JSON-LD `datePublished`/`dateModified`, ou data inferível apenas do URL quando presente).

## Amostras: bons candidatos

### Notícia (data + resumo ≥40, não genérico)

```json
[
  {
    "titulo": "IAEA ZODIAC Week Sets Roadmap to Strengthen Global Pandemic Readiness",
    "link": "http://www.iaea.org/newscenter/news/iaea-zodiac-week-sets-roadmap-to-strengthen-global-pandemic-readiness",
    "data_publicacao": "2026-04-29"
  },
  {
    "titulo": "Nuclear Techniques Help Liberia Develop Climate-Resilient Rice",
    "link": "http://www.iaea.org/newscenter/news/nuclear-techniques-help-liberia-develop-climate-resilient-rice",
    "data_publicacao": "2026-04-29"
  },
  {
    "titulo": "Singapore Signs its Fourth Country Programme Framework (CPF) for 2026–2031",
    "link": "http://www.iaea.org/newscenter/news/singapore-signs-its-fourth-country-programme-framework-cpf-for-2026-2031",
    "data_publicacao": "2026-04-23"
  },
  {
    "titulo": "IAEA Delivers Report to Viet Nam on its Nuclear Power Infrastructure Development",
    "link": "http://www.iaea.org/newscenter/news/iaea-delivers-report-to-viet-nam-on-its-nuclear-power-infrastructure-development",
    "data_publicacao": "2026-04-22"
  },
  {
    "titulo": "Ecuador and Panama Use Nuclear Techniques to Research, Restore and Protect their Cultural Heritage",
    "link": "http://www.iaea.org/newscenter/news/ecuador-and-panama-use-nuclear-techniques-to-research-restore-and-protect-their-cultural-heritage",
    "data_publicacao": "2026-04-08"
  }
]
```

### Pesquisa / publicação técnica

```json
[
  {
    "titulo": "Nuclear Data Newsletter No. 80 \nIssue No. 80, January 2026",
    "link": "http://www.iaea.org/publications/16047/nuclear-data-newsletter-no-80-issue-no-80-january-2026",
    "data_publicacao": "2026-03-10"
  },
  {
    "titulo": "Clinical Training of Medical Physicists Specializing in Diagnostic Radiology",
    "link": "http://www.iaea.org/publications/8574/clinical-training-of-medical-physicists-specializing-in-diagnostic-radiology",
    "data_publicacao": "2026-02-27"
  },
  {
    "titulo": "Clinical Training of Medical Physicists Specializing in Nuclear Medicine",
    "link": "http://www.iaea.org/publications/8656/clinical-training-of-medical-physicists-specializing-in-nuclear-medicine",
    "data_publicacao": "2026-02-27"
  },
  {
    "titulo": "Specific Infrastructure Considerations for Nuclear Energy Applications Beyond Electricity",
    "link": "http://www.iaea.org/publications/16023/specific-infrastructure-considerations-for-nuclear-energy-applications-beyond-electricity",
    "data_publicacao": "2026-02-23"
  },
  {
    "titulo": "Syllabus for the Training of Radiation Protection Officers",
    "link": "http://www.iaea.org/publications/16022/syllabus-for-the-training-of-radiation-protection-officers",
    "data_publicacao": "2026-02-23"
  },
  {
    "titulo": "Interlaboratory Comparison on the Determination of Trace Elements and Rare Earth Element Mass Fractions in Marine Sediment Sample IAEA-MESL-2024-ILC-TE-SEDIMENT",
    "link": "http://www.iaea.org/publications/15969/interlaboratory-comparison-on-the-determination-of-trace-elements-and-rare-earth-element-mass-fractions-in-marine-sediment-sample-iaea-mesl-2024-ilc-te-sediment",
    "data_publicacao": "2026-02-18"
  },
  {
    "titulo": "Good Practices and Lessons Learned from the Long Term Operation of Nuclear Power Plants",
    "link": "http://www.iaea.org/publications/16017/good-practices-and-lessons-learned-from-the-long-term-operation-of-nuclear-power-plants",
    "data_publicacao": "2026-02-18"
  },
  {
    "titulo": "Decommissioning and Waste Management Considerations for Fusion Facilities",
    "link": "http://www.iaea.org/publications/16013/decommissioning-and-waste-management-considerations-for-fusion-facilities",
    "data_publicacao": "2026-02-18"
  },
  {
    "titulo": "SSDL Newsletter Issue No. 82, December 2025",
    "link": "http://www.iaea.org/publications/16018/ssdl-newsletter-issue-no-82-december-2025",
    "data_publicacao": "2026-01-23"
  },
  {
    "titulo": "Technological Obsolescence Management of Nuclear Power Plants",
    "link": "http://www.iaea.org/publications/15989/technological-obsolescence-management-of-nuclear-power-plants",
    "data_publicacao": "2026-01-22"
  },
  {
    "titulo": "Integrated Review Service for Radioactive Waste and Spent Fuel Management, Decommissioning and Remediation (ARTEMIS) Guidelines",
    "link": "http://www.iaea.org/publications/16009/integrated-review-service-for-radioactive-waste-and-spent-fuel-management-decommissioning-and-remediation-artemis-guidelines",
    "data_publicacao": "2026-01-14"
  },
  {
    "titulo": "Volcanic Tephra Fallout Hazard Assessment and the Associated Design and Operational Considerations for Nuclear Installations",
    "link": "http://www.iaea.org/publications/16010/volcanic-tephra-fallout-hazard-assessment-and-the-associated-design-and-operational-considerations-for-nuclear-installations",
    "data_publicacao": "2025-12-31"
  },
  {
    "titulo": "Approaches to Operating Nuclear Power Plants to Mitigate Production Losses Caused by Climate Change and Environmental Hazards",
    "link": "http://www.iaea.org/publications/16008/approaches-to-operating-nuclear-power-plants-to-mitigate-production-losses-caused-by-climate-change-and-environmental-hazards",
    "data_publicacao": "2025-12-31"
  },
  {
    "titulo": "Ageing Management Programmes for Spent Fuel Dry Storage Systems",
    "link": "http://www.iaea.org/publications/15913/ageing-management-programmes-for-spent-fuel-dry-storage-systems",
    "data_publicacao": "2025-12-31"
  }
]
```

## Notas técnicas

- Feeds com XML inválido (ex.: `<br>` em `<title>`) são lidos via extrator `rss_loose` no crawler.
- Publicações RSS muitas vezes vêm sem `description`: o standardized pode usar o título oficial (≥40 caracteres) como texto descritivo mínimo para `pesquisa`, após strip.

## Recomendação (staging)

Avaliar `build_iaea_wave1_payloads` + `load_news_research_sources.py --dry-run --wave iaea_wave1`; só considerar apply manual após rever `iaea_wave1_review_candidates.json` e confirmar `errors_count==0` no resumo do loader.

## Próximo passo

```
python scripts/build_iaea_wave1_payloads.py
```

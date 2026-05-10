# NASA news — Onda 1 (dry-run integração)

- Gerado em: `2026-05-04T15:50:24Z`
- Entrada: `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\standardized\nasa_news_standardized.json`
- **Sem apply**, sem Supabase, sem `public.edital`.

## Totais

- Itens lidos (standardized): **19**
- Após dedupe interno: **19**
- Removidos no dedupe: **0**
- Payload `public.noticia`: **13**
- Payload `public.pesquisa`: **5**
- `review_for_edital` (fora do payload): **1**
- Excluídos do payload (ruído / gates / campos): **0**

## Campos faltantes (validação payload)

- Notícia: **0** registos com falhas
- Pesquisa: **0** registos com falhas

## Aptidão staging futuro

- **apto_staging_futuro**: `True`
- Motivo: ok_todos_requisitos_wave1

## Exclusões (amostra)

```json
[]
```

## Exemplos (payload)

```json
[
  {
    "tipo": "noticia",
    "titulo": "Cyclone Rains Spur Papua New Guinea Landslides",
    "link": "https://science.nasa.gov/earth/earth-observatory/cyclone-rains-spur-papua-new-guinea-landslides/"
  },
  {
    "tipo": "noticia",
    "titulo": "Record-Setting Retreat of Hektoria Glacier",
    "link": "https://science.nasa.gov/earth/earth-observatory/record-setting-retreat-of-hektoria-glacier/"
  },
  {
    "tipo": "pesquisa",
    "titulo": "Artemis Moon Tree Dedicated in Honor of Mary W. Jackson",
    "link": "https://science.nasa.gov/learning-resources/science-activation/artemis-moon-tree-dedicated-in-honor-of-mary-w-jackson/"
  },
  {
    "tipo": "pesquisa",
    "titulo": "Science Through Shadows: How Astronomical Alignments Reveal the Universe",
    "link": "https://science.nasa.gov/learning-resources/science-activation/science-through-shadows-how-astronomical-alignments-reveal-the-universe/"
  },
  {
    "tipo": "noticia",
    "titulo": "Hubble Spots a Starry Spiral",
    "link": "https://science.nasa.gov/missions/hubble/hubble-spots-a-starry-spiral/"
  },
  {
    "tipo": "pesquisa",
    "titulo": "For NASA’s TESS, Stellar Eclipses Shed Light on Possible New Worlds",
    "link": "https://science.nasa.gov/missions/tess/for-nasas-tess-stellar-eclipses-shed-light-on-possible-new-worlds/"
  },
  {
    "tipo": "pesquisa",
    "titulo": "NASA’s STORIE Mission to Tell Tale of Earth’s Ring Current",
    "link": "https://science.nasa.gov/science-research/heliophysics/nasas-storie-mission-to-tell-tale-of-earths-ring-current/"
  },
  {
    "tipo": "noticia",
    "titulo": "NASA Announces 32nd Annual Human Exploration Rover Challenge Winners",
    "link": "https://www.nasa.gov/centers-and-facilities/marshall/nasa-announces-32nd-annual-human-exploration-rover-challenge-winners/"
  },
  {
    "tipo": "noticia",
    "titulo": "Key Support Equipment Arrives at Kennedy for Roman Space Telescope",
    "link": "https://www.nasa.gov/image-article/key-support-equipment-arrives-at-kennedy-for-roman-space-telescope/"
  },
  {
    "tipo": "noticia",
    "titulo": "NASA Artemis II Crew Rings Nasdaq Closing Bell",
    "link": "https://www.nasa.gov/image-article/nasa-artemis-ii-crew-rings-nasdaq-closing-bell/"
  }
]
```

## Artefatos

- `nasa_wave1_payload_noticia.json`
- `nasa_wave1_payload_pesquisa.json`
- `nasa_wave1_review_candidates.json`
- `nasa_wave1_dry_run.json`

## Comando futuro (não executado)

```text
# Comando futuro sugerido (NÃO executar neste ciclo — sem apply / sem Supabase):
# Quando existir loader dedicado notícia/pesquisa em staging:
#   CORE\.venv\Scripts\python.exe scripts\<loader_noticia_pesquisa>.py --input audit_reports_news_research_loader\nasa_wave1_payload_noticia.json --table noticia --dry-run
#   CORE\.venv\Scripts\python.exe scripts\<loader_noticia_pesquisa>.py --input audit_reports_news_research_loader\nasa_wave1_payload_pesquisa.json --table pesquisa --dry-run
```

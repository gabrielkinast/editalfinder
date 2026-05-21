# DARPA Programs Research — subset válido (staging)

- **Execução:** 2026-05-19T21:19:30Z
- **Destino:** `public.pesquisa` · `tipo_pesquisa=programa_pesquisa`
- **Janela:** 24 meses (corte ≥ `2024-05-29`)

## Totais

| Original | 40 |
| Válidos no original | 25 |
| **Subset** | **25** |
| Incompletos (latentes) | 15 |

## Loader dry-run

- **would_upsert_pesquisa:** 25
- **errors_count:** 0
- **apply:** não

## Eixos

- `engenharia_avancada`: 10
- `defesa`: 8
- `materiais_avancados`: 4
- `sensores`: 2
- `aeroespacial`: 1
- `comunicacoes`: 1
- `espaco`: 1
- `guerra_eletronica`: 1
- `ia`: 1
- `microeletronica`: 1
- `propulsao`: 1
- `semicondutores`: 1

## Programas (título · data)

- **2026-05-15** — Media Forensics
- **2026-05-15** — Robotic Servicing Of Geosynchronous Satellites
- **2026-05-15** — Discord
- **2026-05-15** — Automated Process For Codesign Of Radiation Hardening And Security
- **2026-05-14** — Nascent National Security Economic Theory
- **2026-05-14** — Protean
- **2026-05-14** — Amped
- **2026-05-14** — Bark
- **2026-05-13** — Warrior Web
- **2026-05-13** — Wound Stasis System
- **2026-05-13** — Extended Solids
- **2026-05-13** — Z Man
- **2026-05-13** — Transformative Apps
- **2026-05-13** — Transparent Computing
- **2026-05-13** — Vetting Commodity It Software And Firmware
- **2026-05-13** — Visual Media Reasoning
- **2026-05-13** — Xdata
- **2026-05-13** — Thermal Management Technologies
- **2026-05-13** — Thermal Management Technologies
- **2026-05-13** — Thermal Management Technologies
- **2026-05-13** — Thz Electronics
- **2026-05-13** — Transmit And Receive Optimized Photonics
- **2026-05-13** — Trusted Integrated Circuits
- **2026-05-13** — Upward Falling Payloads
- **2026-05-13** — Video Synthetic Aperture Radar

## Apply staging (não executado)

```powershell
# NÃO EXECUTADO — apply staging pesquisa
$env:EDITALFINDER_ENV='staging'
$env:EDITALFINDER_ALLOW_STAGING_APPLY='true'
python scripts/load_news_research_sources.py `
  --apply --staging --test-db-before-apply `
  --source darpa_programs_research `
  --input-dir audit_reports_news_research/darpa_programs_subset_valido
```

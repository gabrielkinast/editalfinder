# Onda C ? quality fix curto

Gerado: `2026-05-09T15:36:54Z`

## Seguran?a

- Apply executado: **n?o**
- Supabase tocado: **n?o** (`SUPABASE_URL` local falso no dry-run loader)
- Schema alterado: **n?o**
- `opportunity_gate` global alterado: **n?o**
- `config/source_readiness.json` alterado: **n?o**

## Mudan?as feitas

- Poda de publico_alvo/perfil_ideal por evidencia textual nas calibracoes internacionais locais.
- Compactacao de area/classificacao ampla e preservacao de excedentes em tags_secundarias.
- Melhoria de extracao de prazo por closing date/deadline/apply by/submission date em detalhes HTML.
- Filtro de URLs agregadoras UKRI (/feed e /page/) para reduzir ruido.

## Antes x Depois

- Flags antes: `{'publico_alvo_sem_evidencia': 15, 'classificacao_muito_ampla': 1}`
- Flags depois: `{'publico_alvo_sem_evidencia': 4}`
- Itens standardized depois: **46**
- `classificacao_muito_ampla`: **0**

## Por fonte

| Fonte | Standardized | Com prazo | setor > 3 | Flags | Recomenda??o |
|---|---:|---:|---:|---|---|
| `innovate_uk` | 1 | 1 | 0 | `{'publico_alvo_sem_evidencia': 1}` | `needs_manual_review` |
| `ukri_funding` | 10 | 8 | 0 | `{'publico_alvo_sem_evidencia': 2}` | `ready_with_notes` |
| `eurostars` | 2 | 1 | 0 | `{}` | `needs_manual_review` |
| `eit` | 16 | 0 | 0 | `{}` | `ready_with_notes` |
| `esa_star` | 0 | 0 | 0 | `{}` | `blocked` |
| `esa_osip` | 17 | 1 | 0 | `{'publico_alvo_sem_evidencia': 1}` | `ready_with_notes` |

## Loader Dry-Run

- Readiness usado: `D:\Computational_Physics\My Projects\edital\audit_reports_credito\lote_inovacao_internacional_onda_c_quality_fix_readiness_temp.json`
- Fontes selecionadas: **3**
- Fontes exclu?das: **3**
- Would upsert: **43**
- Mapping errors: **0**
- Critical empty: **0**

## Flags remanescentes

- `esa_osip` ? European Space for Sustainability Award 2026: `['publico_alvo_sem_evidencia']`
- `innovate_uk` ? Funding opportunity: Dual-use aviation systems and autonomy: `['publico_alvo_sem_evidencia']`
- `ukri_funding` ? Funding opportunity: Dual-use aviation systems and autonomy: `['publico_alvo_sem_evidencia']`
- `ukri_funding` ? Funding opportunity: National Materials Innovation Programme: Feasibility studies Round 2: `['publico_alvo_sem_evidencia']`

## Recomenda??o final

- `ukri_funding`, `eit`, `esa_osip`: podem seguir para `ready_with_notes` depois de revis?o humana.
- `innovate_uk`, `eurostars`: manter `needs_manual_review` por volume baixo.
- `esa_star`: manter `blocked` at? existir feed/API p?blica ou estrat?gia oficial sem login.
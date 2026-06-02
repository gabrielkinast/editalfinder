# Auditoria FINEP / FNDCT — Backend 8

**Registros analisados:** 1232
**Com menção FNDCT (fonte/título/descrição):** 3
**Normalizados como FNDCT (sem FINEP):** 0
**Provavelmente FINEP (sinais fortes):** 0
**Passariam a fonte_normalizada=FINEP:** 0

## Conceito

- **FINEP** — agência operadora / fonte institucional visível na UI.
- **FNDCT** — fundo de origem do recurso (`fundo_origem`), não substitui FINEP quando ambos aparecem.

## Sinais FINEP auditados

- Domínio `finep.gov.br` no link
- FINEP em fonte, título, descrição ou extras (`agencia`, `orgao`)

Artefatos: `report.json`, `finep_fndct_examples.json`, `suspicious_source_names.json`.
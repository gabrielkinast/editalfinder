# Dry-run Backend 2 — enriquecimento

**Registros analisados:** 1232

## Prazos

- Ganham `prazo_data` sem `prazo_envio`/`fim_inscricao` na BD: **91** (7.4%)
- Ganho *novo* (nem normalizer no registro bruto): **0**
- Continuam `sem_prazo`: **1025** (83.2%)
- Prazo com confiança baixa: **91**

### prazo_status (antes → depois)

**Antes:**
- `sem_prazo`: 1025 (83.2%)
- `encerrado`: 148 (12.0%)
- `prazo_confortavel`: 40 (3.2%)
- `vencendo_30`: 11 (0.9%)
- `vencendo_7`: 8 (0.6%)

**Depois (enriquecido):**
- `sem_prazo`: 1025 (83.2%)
- `encerrado`: 148 (12.0%)
- `prazo_confortavel`: 40 (3.2%)
- `vencendo_30`: 11 (0.9%)
- `vencendo_7`: 8 (0.6%)

### Confiança de prazo (depois)

- `nenhuma`: 1025
- `alta`: 116
- `baixa`: 91

### Top fontes — melhora de prazo

- KEK: +16
- Eureka Network: +10
- EIC: +10
- European Defence Fund: +9
- UKRI Funding: +9
- DIU: +7
- NSFC: +6
- JETRO Government Procurement: +6
- EIT: +4
- CAS: +2
- ERC: +2
- Lockheed Martin Suppliers: +2
- WELLCOME: +2
- DoD SBIR/STTR: +1
- ATLA: +1
- Mitsubishi Heavy Industries (Suppliers): +1
- QST: +1
- NSF: +1
- ESA OSIP: +1

### Top fontes — ainda sem prazo

- China International Tendering (MOFCOM): 131
- Fundação Araucária: 88
- Grants.gov: 79
- BNDES: 38
- BDMG: 37
- BASA: 30
- CAS: 29
- ANEEL: 27
- KAKENHI: 26
- HORIZON_EUROPE: 25
- BNB: 24
- NSFC: 24
- SENAI: 22
- NUCLEP: 20
- CGN: 16

## Classificação

### tipo_registro

- `edital`: 821 (66.6%)
- `desconhecido`: 317 (25.7%)
- `pesquisa`: 32 (2.6%)
- `portal`: 24 (1.9%)
- `concurso`: 23 (1.9%)
- `noticia`: 15 (1.2%)

### modalidade_normalizada

- `bolsa_formacao`: 289
- `fomento_chamada_publica`: 248
- `noticia_institucional`: 246
- `compra_licitacao`: 220
- `outro`: 150
- `premio_desafio`: 66
- `pesquisa_cientifica`: 6
- `evento_capacitacao`: 3
- `concurso_selecao`: 2
- `pesquisa_publicacao`: 2

### escopo_geografico

- `internacional`: 636
- `brasil`: 448
- `multilateral`: 141
- `desconhecido`: 7

### Mudanças de kind (edital na BD → outro tipo): **411**

## Qualidade (flags)

- `sem_prazo`: 1025
- `revisao_humana`: 570
- `kind_baixa_confianca`: 408
- `kind_desconhecido`: 317
- `possivel_noticia_em_edital`: 201
- `modalidade_baixa_confianca`: 150
- `prazo_baixa_confianca`: 91
- `prazo_texto_derivado`: 91
- `escopo_desconhecido`: 7
- `titulo_parece_noticia`: 1

## Artefatos

- `enriched_sample.json` — amostra antes/depois
- `changes_by_field.json` — contagem por campo novo
- `low_confidence_review.json` — revisão humana sugerida
- `kind_changes_review.json` — kind diferente de edital implícito

**Nenhum UPDATE foi executado.** Integração real exige migration + backfill com relatório.
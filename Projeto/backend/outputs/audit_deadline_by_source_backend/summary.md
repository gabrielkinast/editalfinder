# Auditoria de prazos por fonte — Backend 3

**Registros:** 1232 | **Fontes:** 82

## Top fontes problemáticas (sem prazo)

| Fonte | Total | Com prazo BD | Sem prazo | % sem |
|-------|------:|-------------:|----------:|------:|
| China International Tendering (MOFCOM) | 131 | 0 | 131 | 100.0% |
| Fundação Araucária | 88 | 0 | 88 | 100.0% |
| Grants.gov | 127 | 48 | 79 | 62.2% |
| BNDES | 38 | 0 | 38 | 100.0% |
| BDMG | 38 | 1 | 37 | 97.4% |
| BASA | 30 | 0 | 30 | 100.0% |
| CAS | 31 | 0 | 29 | 93.5% |
| ANEEL | 27 | 0 | 27 | 100.0% |
| KAKENHI | 26 | 0 | 26 | 100.0% |
| HORIZON_EUROPE | 25 | 0 | 25 | 100.0% |
| BNB | 24 | 0 | 24 | 100.0% |
| NSFC | 30 | 0 | 24 | 80.0% |
| SENAI | 22 | 0 | 22 | 100.0% |
| NUCLEP | 20 | 0 | 20 | 100.0% |
| CGN | 16 | 0 | 16 | 100.0% |
| MOST China | 16 | 0 | 16 | 100.0% |
| NEDO | 16 | 0 | 16 | 100.0% |
| DARPA Opportunities | 15 | 0 | 15 | 100.0% |
| ESA OSIP | 17 | 1 | 15 | 88.2% |
| DOE_ARPAE | 14 | 0 | 14 | 100.0% |
| IPEN | 14 | 0 | 14 | 100.0% |
| JSPS | 14 | 0 | 14 | 100.0% |
| DoD SBIR/STTR | 15 | 0 | 14 | 93.3% |
| Lockheed Martin Suppliers | 16 | 0 | 14 | 87.5% |
| NIMS | 13 | 0 | 13 | 100.0% |

## Recomendações (top 3 foco Backend 3)

### China International Tendering (MOFCOM)
- Crawler: `china_mofcom_tendering/main_china_mofcom_tendering.py`
- Extrair bid/tender closing date no detail HTML; flag deadline_missing_in_source se só publicação.

### Fundação Araucária
- Crawler: `fappr/main_fappr.py + extrair_informacoes_fappr.py`
- Expandir regex PT + texto PDF já extraído; deadline_requires_pdf quando só link PDF.

### Grants.gov
- Crawler: `grants_gov/main_simpler_grants_gov.py`
- Garantir close_date ISO em fim_inscricao; não usar postedDate como prazo.

### MOST China
- Crawler: `transformer.py (genérico) / scraper da fonte`
- Extrair bid/tender closing date no detail HTML; flag deadline_missing_in_source se só publicação.

### China Tendering & Bidding
- Crawler: `transformer.py (genérico) / scraper da fonte`
- Extrair bid/tender closing date no detail HTML; flag deadline_missing_in_source se só publicação.

Ver `sources_ranked.json` e `examples_by_source.json`.
# CAPES Notícias — subset recente (12m, consolidado)

- **Execução:** 2026-05-17T05:55:44Z
- **Origem:** `audit_reports_news_research/capes_noticias_dryrun/standardized/capes_noticias_standardized.json`
- **Subset:** `audit_reports_news_research/capes_noticias_subset_recente/standardized/capes_noticias_standardized.json`
- **Janela pública:** 12 meses (corte ≥ `2025-05-22`)
- **Apply executado:** não

## Totais

- **Original:** 10
- **Válidas no original:** 10
- **Recente (válido + 12m):** 7
- **Excluídas:** 3
- **would_upsert_noticia:** 7
- **errors_count:** 0

## Itens incluídos

### 1. CAPES e CNPq debatem equidade de gênero

- **Data:** 2026-02-12
- **Categoria:** Formação
- **Eixos:** ciencia_tecnologia, formacao_cientifica
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/capes-e-cnpq-debatem-equidade-de-genero

### 2. Projeto aproxima meninas e mulheres da área de transição energética

- **Data:** 2026-02-11
- **Categoria:** Ciência
- **Eixos:** ciencia_tecnologia
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/projeto-aproxima-meninas-e-mulheres-da-area-de-transicao-energetica

### 3. Censo da Pós-Graduação registra 70% de participação

- **Data:** 2026-02-03
- **Categoria:** Pós-graduação
- **Eixos:** ciencia_tecnologia, pos_graduacao
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/censo-da-pos-graduacao-registra-70-de-participacao

### 4. CAPES realiza sete treinamentos em fevereiro

- **Data:** 2026-01-30
- **Categoria:** Ciência
- **Eixos:** ciencia_tecnologia
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/capes-realiza-sete-treinamentos-em-fevereiro

### 5. CAPES atualiza regras para repasses de recursos financeiros

- **Data:** 2026-01-28
- **Categoria:** Inovação
- **Eixos:** ciencia_tecnologia, inovacao, engenharia
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/capes-atualiza-regras-para-repasses-de-recursos-financeiros

### 6. Sobre o Qualis Periódicos na Avaliação Quadrienal 2021-2024

- **Data:** 2026-01-20
- **Categoria:** Ciência
- **Eixos:** ciencia_tecnologia
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/sobre-o-qualis-periodicos-na-avaliacao-quadrienal-2021-2024

### 7. Divulgados inscritos de chamada para pesquisas na Alemanha

- **Data:** 2025-12-29
- **Categoria:** Bolsas
- **Eixos:** ciencia_tecnologia, bolsas_fomento
- **Link:** https://www.gov.br/capes/pt-br/assuntos/noticias/divulgados-inscritos-de-chamada-para-pesquisas-na-alemanha

## Excluídas do subset

- **Instituições de todas as regiões do país aderiram ao GoPG** — 2025-05-08 — _fora_janela_12m_
- **MEC institui Comitê de Governança do Mais Professores** — 2025-04-29 — _fora_janela_12m_
- **Aberta seleção para mestrado profissional em roteiro nos EUA** — 2025-02-28 — _fora_janela_12m_

## Dry-run loader

```text
C:\Program Files\Python312\python.exe D:\Computational_Physics\My Projects\edital\scripts\load_news_research_sources.py --dry-run --source capes_noticias --input-dir audit_reports_news_research/capes_noticias_subset_recente
```

- Relatório: `audit_reports_news_research/capes_noticias_subset_recente/load_news_research_summary.json`

## Apply staging (não executado)

```powershell
# NÃO EXECUTADO — apply staging (executar manualmente após validar .env.staging)
$env:EDITALFINDER_ENV='staging'
$env:EDITALFINDER_ALLOW_STAGING_APPLY='true'
python scripts/load_news_research_sources.py `
  --apply --staging --test-db-before-apply `
  --source capes_noticias `
  --input-dir audit_reports_news_research/capes_noticias_subset_recente
```

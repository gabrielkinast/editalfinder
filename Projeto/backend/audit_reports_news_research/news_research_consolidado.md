# Módulo notícia/pesquisa — consolidado final

**Gerado:** ver `news_research_consolidado.json` (`gerado_em`).  
**Objetivo:** documentar o estado do módulo antes de retornar ao trabalho nas fontes de **crédito / fomento / desenvolvimento** (órgãos de edital).

Este consolidado foi montado a partir da configuração, dos payloads em `audit_reports_news_research_loader/` e dos relatórios de pipeline já existentes — **sem** executar `apply`, **sem** consultas novas ao Supabase nesta geração.

---

## 1. Resumo executivo

O módulo mantém **roteamento explícito**: editais acionáveis são domínio de `public.edital`; **notícias** e **pesquisa técnica** vão para `public.noticia` e `public.pesquisa`, sem misturar automaticamente com edital.

Quatro ondas operacionais estão documentadas com payloads e, para NASA, DARPA News e EurekAlert, **validação pós-carga** nos artefatos `*_post_load_validation.json`. A **IAEA Wave 1** tem pipeline completo de build (incl. fallbacks e rejected/review); **DARPA Opportunities Research** permanece **fora de apply automático**, apenas como candidata a triagem humana.

---

## 2. Separação conceitual

| Destino | Conteúdo |
|---------|-----------|
| **`public.edital`** | Oportunidades **acionáveis**: chamadas com prazo, requisitos de elegibilidade, crédito/fomento típico do produto edital. |
| **`public.noticia`** | Notícias, releases e atualizações; narrativa curta; `tipo_conteudo = noticia`. |
| **`public.pesquisa`** | Relatórios, artigos técnicos, estudos; texto mais denso; `tipo_conteudo = pesquisa` e metadados de pesquisa conforme contrato. |

**Review:** candidatos a edital identificados pelo dry-run podem ir para `review_for_edital` **sem** upsert automático para `public.edital`.

---

## 3. Tabela por fonte / onda

| Fonte | Wave | Status (config) | Crawl (ref.) | Payload notícia | Payload pesquisa | review_for_edital | rejected | Dry-run | Apply staging | Validação pós-carga | Problemas conhecidos | Recomendação |
|-------|------|-----------------|--------------|-----------------|------------------|-------------------|----------|---------|---------------|---------------------|----------------------|--------------|
| `nasa_news` | `nasa_wave2` | ready_for_wave | ~95 std (expansão) | 78 | 17 | 0 | — | OK | Sim (histórico projeto) | OK (`nasa_wave2_post_load_validation`) | Volume alto | Referência de onda estável |
| `darpa_news` | `darpa_news_wave1` | needs_cleanup | ~10 | 9 | 1 | 0 | — | OK | Sim | OK (`darpa_news_wave1_post_load_validation`) | BAA/RFI → review | 2ª prioridade EUA/defesa |
| `iaea_news_publications` | `iaea_wave1` | wave1_preparation | 45 entrada build | 5 | 14 | 2 | 24 | OK | Com guardas | Script disponível; relatório dedicado sob demanda | Fallback título em pesquisas sem resumo longo | Reduzir fallback; subset `valido` |
| `eurekalert_science_filtered` | `eurekalert_wave1` | experimental_wave | 3 (snapshot) | 0 | 3 | 0 | 0 | OK | Sim (último load summary) | OK (`eurekalert_wave1_post_load_validation`) | WAF; defense bio vs militar | Manter experimental |
| `darpa_opportunities_research` | — | active_candidate | ~1 | 0 | 0 | política manual | — | parcial | **Não auto** | n/a até lote estável | Volume baixo; risco confusão | Review apenas |

*(Valores de payload contados nos JSON em `audit_reports_news_research_loader/`.)*

---

## 4. Totais consolidados

| Métrica | Valor (notas) |
|---------|----------------|
| **Soma payloads notícia** (NASA + DARPA News + IAEA + EurekAlert) | **92** (= 78 + 9 + 5 + 0) |
| **Soma payloads pesquisa** | **35** (= 17 + 1 + 14 + 3) |
| **review_for_edital** (JSON IAEA Wave 1) | **2** |
| **rejected** (JSON IAEA Wave 1) | **24** |
| **Fontes ativas** (pipeline principal) | NASA, DARPA News, IAEA |
| **Fontes experimentais** | EurekAlert |
| **Sem apply automático** | DARPA Opportunities |

Carregamento em staging deve coincidir com estas contagens **quando** cada apply foi executado no mesmo ambiente; para auditoria fina, reconciliar com o Supabase.

---

## 5. Status esperado por onda

| Onda | Estado |
|------|--------|
| **NASA Wave 2** | Ativa / validada (pós-carga OK) |
| **DARPA News Wave 1** | Ativa / validada (pós-carga OK) |
| **IAEA Wave 1** | Ativa / validada no fluxo; **atenção** ao fallback de descrição a partir do título em publicações com resumo curto |
| **EurekAlert Wave 1** | **Experimental** / validada pós-carga — **3** linhas em `pesquisa` |
| **DARPA Opportunities Research** | Manter em **revisão**; **não** aplicar automaticamente |

---

## 6. Comandos usados (referência)

**Build de payloads** (por onda):

```bash
python scripts/build_nasa_wave2_payloads.py
python scripts/build_iaea_wave1_payloads.py
python scripts/build_eurekalert_wave1_payloads.py
```

*(DARPA News segue o mesmo padrão se existir script dedicado; caso contrário usar payloads já versionados.)*

**Dry-run do loader:**

```bash
python scripts/load_news_research_sources.py --dry-run --staging --source <fonte> --input-dir audit_reports_news_research_loader --wave <onda>
```

**Apply staging (guard):**

```bash
# PowerShell exemplo
$env:EDITALFINDER_ENV="staging"
$env:EDITALFINDER_ALLOW_STAGING_APPLY="true"
python scripts/load_news_research_sources.py --apply --staging --test-db-before-apply --source <fonte> --input-dir audit_reports_news_research_loader --wave <onda>
```

**Validação pós-carga:**

```bash
python scripts/validate_news_research_after_load.py --staging --source <fonte> --wave <onda> --input-dir audit_reports_news_research_loader
```

---

## 7. Regras de governança

1. **Nada** do fluxo notícia/pesquisa vai para `public.edital` automaticamente.  
2. **`review_for_edital`** nunca é aplicado como upsert para edital sem decisão humana.  
3. **Scraping:** feeds oficiais, limites `max_items` / `page_enrich_max`, sem crawl agressivo do site inteiro.  
4. **Fontes experimentais:** volume baixo, filtros fortes, curadoria (ex.: EurekAlert).  
5. **Apply:** só staging, com `EDITALFINDER_ALLOW_STAGING_APPLY` e `--test-db-before-apply`.

*(Espelhado em `config/news_research_sources.json` → `governance`.)*

---

## 8. Próximos passos

1. **IAEA:** melhorar publicações sem depender do fallback título→corpo quando o RSS vem pobre.  
2. **DARPA:** ampliar com critérios anti-ruído e separação notícia vs oportunidade.  
3. **EurekAlert:** manter **experimental**; rever seeds se bloqueio WAF.  
4. **Produto:** voltar o foco prioritário para **fontes de crédito, fomento e desenvolvimento** (novos órgãos de edital).

---

## Artefato máquina-legível

`audit_reports_news_research/news_research_consolidado.json`

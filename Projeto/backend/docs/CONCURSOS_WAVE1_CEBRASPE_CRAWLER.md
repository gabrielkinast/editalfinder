# Wave 1 — Crawler piloto Cebraspe

## Diagnóstico da estrutura pública

| Aspeto | Observação |
|--------|------------|
| **Site institucional** | `https://www.cebraspe.org.br` — menu liga **Concursos** a `https://www.cebraspe.org.br/concursos/` e subsecções **Novos**, **Inscrições abertas**, **Em andamento**, **Encerrados** (`/concursos/novos`, `/concursos/inscricoes-abertas/`, `/concursos/em-andamento/`, `/concursos/encerrado`). |
| **Renderização** | As páginas sob `/concursos/` devolvem **shell SPA** (mensagem de necessidade de JavaScript); **não** há listagem estável em HTML estático para BeautifulSoup. |
| **API usada pelo front** | O bundle `concursos/static/js/main.*.chunk.js` referencia `apiLink: "https://apis.cebraspe.org.br/cebraspe/"` e usa `pas/subprogramas` (jQuery `ajax` / JSON). |
| **Endpoint piloto** | `GET https://apis.cebraspe.org.br/cebraspe/pas/subprogramas` — lista de **subprogramas PAS** (Programa de Avaliação Seriada) com **etapas**, datas de inscrição/prova (`eventoDaEtapa`, `strData*`), `isEtapaVigente`, `provaRealizada`, `arquivosEdital` / `arquivosGabarito` (quando existem). |
| **Página de detalhe (URL canónica)** | `https://www.cebraspe.org.br/concursos/pas/{subProgramaId}` (HTTP 200; conteúdo dinâmico). Usada como **`link`** único por `(fonte, link)` no loader. |
| **robots.txt** | `https://www.cebraspe.org.br/robots.txt` — `User-agent: *` com `Disallow:` vazio. API `apis.cebraspe.org.br` sem `robots.txt` (404); pedido único conservador + `--sleep`. |

## Decisão wave 1 (tentativa como diagnóstico)

- **Implementado:** crawler PAS em `concursos/main_cebraspe_concursos.py` sobre `GET …/pas/subprogramas` (único endpoint público mapeado nesta fase).
- **Cobertura:** limitada ao **PAS** (Programa de Avaliação Seriada / fluxo associado ao endpoint); **não** cobre a carteira geral de concursos Cebraspe exposta no site SPA.
- **Corrida de referência (data atual):** dry-run típico devolve **0 linhas standardized** quando todas as etapas relevantes estão encerradas; **apply não** foi executado neste piloto.
- **Manutenção:** tratar como **fonte latente** — manter o script e a documentação; não priorizar carga ativa até existir (com uso ético) um **endpoint ou contrato estável** para concursos gerais além do PAS.

### Campos disponíveis na API (PAS)

- Identificação: `subProgramaId`, `subProgramaDescricao`, `periodo`, `anosPeriodo`, `possuiEtapaVigente`.
- Por etapa: `etapaId`, `etapaDescricao`, `dataProva`, `eventoDaEtapa.dataIniInscricao` / `dataFimInscricao` (ISO), strings `strDataInicioInscricao` / `strDataFimInscricao` (pt), `isEtapaVigente`, `provaRealizada`, `arquivosEdital`, `arquivosGabarito`.
- **Não** observados neste endpoint: número de vagas, remuneração, taxa (não inferidos).

## Script

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_cebraspe_concursos.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave1_cebraspe/standardized/cebraspe_standardized.json` |
| Resumo | `audit_reports_main_pipeline/concursos_wave1_cebraspe/crawler_summary.json` / `.md` |

### Comandos

```bash
python concursos/main_cebraspe_concursos.py --max-items 20 --sleep 1.5
# Opcional: data de referência para encerrados / recência (reprodução com API histórica)
python concursos/main_cebraspe_concursos.py --max-items 20 --sleep 1.5 --as-of-date 2025-09-01

python -m pytest tests/test_cebraspe_crawler.py -q

python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_cebraspe/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_cebraspe/loader_dryrun --sources cebraspe
```

## Mapeamento para `concurso_selecao`

| Campo | Origem |
|--------|--------|
| `titulo` | Texto construído: PAS — `{subProgramaDescricao}` — `{etapaDescricao}` (Cebraspe). |
| `tipo_selecao` | `programa_ingresso` (PAS); `infer_tipo_selecao_meta` sobre título/corpo. |
| `categoria` | `banca_cebraspe_pas`. |
| `orgao` / `instituicao` | PAS UnB: **Universidade de Brasília** (fixo neste piloto). |
| `banca` | **Cebraspe**. |
| `estado` / `municipio` | **DF** / **Brasília**. |
| `nivel_escolaridade` | `infer_nivel_escolaridade` (default **superior**). |
| `data_inicio_inscricao` / `data_fim_inscricao` / `data_prova` | API (ISO ou dd/mm/yyyy), sem inventar. |
| `link_edital` | Primeiro URL em `arquivosEdital` se lista; senão `null`. |
| `link` | `https://www.cebraspe.org.br/concursos/pas/{id}`. |
| `fonte` | `cebraspe` |
| `fonte_tipo` | `banca` |
| `validacao_status` | `valido` se **ambos** `link_edital` e `data_fim_inscricao`; senão `incompleto`. |
| `qualidade_dado` | `pci_infer_qualidade_dado` (+ ajuste se não válido). |
| `numero_vagas`, `salario_*`, `taxa_inscricao` | **Não preenchidos** (API não fornece). |

## Regras implementadas

- Um pedido GET ao endpoint oficial; `--sleep` antes do GET.
- Etapa **primária**: prioriza `isEtapaVigente`, depois fim de inscrições futuro, depois prova futura.
- **Descarte** `cebraspe_pas_etapa_encerrada`: etapa com inscrições e prova já passadas (`provaRealizada` ou datas).
- **Descarte** de etapas de **resultado/gabarito** encerradas (`etapa_resultado_ou_gabarito_encerrada`).
- `recency_should_discard` (alinhado à wave PCI/Fundatec) após extração.
- **Sem** vagas/salário/taxa inventados.

## Última corrida de referência (ambiente de desenvolvimento)

Valores típicos com **`--as-of-date` = hoje** e API na data da corrida:

| Métrica | Valor típico |
|---------|----------------|
| **Itens brutos (API)** | 12 subprogramas |
| **Standardized** | **0** se todos os PAS estiverem encerrados em relação a `as_of_date` |
| **Descartados** | até 12 (`cebraspe_pas_etapa_encerrada`, etc.) |
| **Loader dry-run** | `errors_count = 0` (lista vazia ou com itens) |

Com `--as-of-date 2025-09-01` é possível obter linhas **não descartadas** (inscrições ainda abertas naquele contexto temporal) para testes manuais.

## Limitações

1. **Âmbito PAS apenas** — não cobre todos os “concursos públicos” divulgados pela banca noutros fluxos sem endpoint público identificado.
2. **`link_edital`** depende de `arquivosEdital` na API; quando `null`, `validacao_status` permanece **incompleto**.
3. **Listagem HTML** não utilizada (SPA); dependência da **API** mantida pelo Cebraspe.
4. **Volume 0** possível quando não há etapa ativa face à data de referência — comportamento esperado, não erro.

## Recomendação de apply staging

- Correr **dry-run** após cada crawl; só aplicar em staging com revisão dos `link` e das datas.
- **Apply não** executado na entrega deste piloto.
- Próximo incremento sugerido: descobrir endpoints adicionais (outros programas) **sem** aumentar taxa de pedidos sem consentimento explícito do site.

# Wave 1 — Crawler piloto (PCI)

## Papel dos agregadores (camada de descoberta)

A PCI Concursos e fontes semelhantes são **agregadores**: reúnem notícias e links úteis para **descoberta**, não substituem o **edital oficial** nem o site do órgão emissor.

- **`link`**: página da notícia na PCI (rastreável).
- **`link_edital`**: primeiro link HTTP externo “útil” no HTML — pode ser o portal do órgão, não necessariamente o PDF do edital.
- **`validacao_status = incompleto`**: frequente enquanto **datas oficiais** não forem extraídas do texto; o frontend pode mostrar **“Dados parciais”** e mensagens explícitas (“Inscrição / prova não identificadas”).
- **`extras.source_is_aggregator`**: `true` nos itens PCI para deixar explícito no payload que a origem é agregada.

**A PCI não substitui a fonte oficial:** prazos, valores e requisitos devem ser confirmados no órgão (e no edital) antes de decisões.

## Resumo

| Item | Valor |
|------|--------|
| **Fonte piloto** | PCI Concursos (`pci_concursos`) |
| **Script** | `concursos/main_pci_concursos.py` |
| **Helpers** | `concursos/common.py` |
| **Standardized** | `audit_reports_main_pipeline/concursos_wave1_pci/standardized/pci_concursos_standardized.json` |
| **Relatório crawler** | `.../concursos_wave1_pci/crawler_summary.json` e `.md` |
| **Dry-run loader** | `loader_dryrun_v2` (corrida anterior) ou **`loader_dryrun_v3`** (após separação taxa/salário e extras) |
| **Decisão Vunesp vs PCI** | `docs/CONCURSOS_WAVE1_PILOT_DECISION.md` |
| **Catálogo fontes** | `docs/CONCURSOS_FONTES_WAVE1.md` |

## Campos frequentemente parciais (esperado)

| Campo | Nota |
|-------|------|
| `data_fim_inscricao`, `data_prova` | Muitas notícias sem frases padronizadas “inscrições até …” / “prova …” no corpo. |
| `data_publicacao` | Depende de datas `dd/mm/aaaa` parseáveis no texto. |
| `orgao`, `estado`, `municipio` | Inferidos do **título** por padrões (Prefeitura/Câmara/UF, forças armadas, etc.); fora do padrão ficam vazios. |
| `salario_min` / `salario_max` | `parse_remuneracao_taxa_br` tenta separar **remuneração** de **taxa de inscrição** por contexto (`taxa`, `inscrição`, `salário`, `remuneração`, …); valores ambíguos geram notas em `extras.value_extraction_notes` e flags `possible_fee_detected` / `possible_salary_detected`. |
| `taxa_inscricao` | Preenchida quando o texto associa `R$` a taxa/inscrição. |
| `cargo`, `curso`, `banca` real | Wave PCI usa `banca = "PCI Concursos"`; cargo/curso em geral ausentes. |

## Comportamento do piloto PCI

1. Lê `https://www.pciconcursos.com.br/robots.txt` (`urllib.robotparser`).
2. Obtém `https://www.pciconcursos.com.br/concursos` e extrai links `https://www.pciconcursos.com.br/noticias/<slug>` (sem `.php`).
3. Para cada notícia (até `--max-items`), espera `--sleep` segundos, faz GET, extrai título (`og:title`), texto, datas heurísticas, vagas, **remuneração vs taxa** (`parse_remuneracao_taxa_br` sobre `título + corpo`), órgão/local, nível, tipo, link externo, **`extras`** (`source_is_aggregator`, `value_extraction_notes`, `possible_fee_detected`, `possible_salary_detected`, `extracted_fields`, `missing_core_fields`, `extraction_confidence`, `official_link_missing`, `pci_noticia_url`), e **`qualidade_dado`** (`alta` / `media` / `baixa` conforme completude).
4. Filtro de antiguidade: `concursos.common.recency_should_discard`.
5. JSON para `scripts/load_concursos_selecao.py`.

## Antes vs depois (extração)

Referência histórica: `crawler_summary.json` após `python concursos/main_pci_concursos.py --max-items 12 --sleep 1.5`.

| Aspeto | Piloto inicial | Melhorias |
|--------|----------------|-----------|
| Milhar em vagas (`1.100 vagas`) | Podia ler só `100` | Milhar PT-BR correto |
| `R$` no texto | Um único campo salário; taxa confundida com piso | **Taxa** vs **salário** por contexto; `taxa_inscricao` separada |
| `qualidade_dado` | Heurística simples | **Alta**: órgão + local + fim inscrição + prova; **Média** / **Baixa** conforme sinais |
| UI `/concursos` | “Validação incompleta” genérico | **Dados parciais**, inscrição/prova com texto explícito, **Fonte agregadora** |

## Comandos

```bash
python -m pytest tests/test_concursos_common.py -q
python concursos/main_pci_concursos.py --max-items 12 --sleep 1.5
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_pci/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_pci/loader_dryrun_v3 --sources pci_concursos
```

**Apply** em staging continua manual, com guardas (`EDITALFINDER_ENV`, `EDITALFINDER_ALLOW_STAGING_APPLY`, `--apply-staging --staging`).

## Testes unitários

```bash
python -m pytest tests/test_concursos_common.py -q
```

## Limitações restantes

- Agregador: texto editorial; **não** garante edital nem PDF.
- **Salário / taxa**: heurística por janela de texto; valores ambíguos (ex.: faixa média sem palavras-chave) podem ser omitidos do salário com nota em `value_extraction_notes`.
- Títulos com valores em slug (`15-6-mil`) podem ainda distorcer números até novo ajuste.
- Nível de escolaridade e tipo de seleção: inferência por texto.
- Volume e frequência de crawl: respeitar `robots.txt` e política de carga.

## Recomendação de apply

Não aplicar cargas novas automaticamente. Preferir **dry-run** (`loader_dryrun_v3`) e revisão humana antes de qualquer `apply` em staging.

## Pós-apply staging (Wave 1 PCI)

**Data de referência do apply:** `2026-05-13T23:17:24Z` (ver `loader_apply_staging/load_concursos_selecao_summary.json`).

**Relatórios gerados:**

| Ficheiro | Conteúdo |
|----------|-----------|
| `concursos_wave1_pci/pos_apply_validation.json` | Métricas, distribuições, exemplos, riscos, checklist |
| `concursos_wave1_pci/pos_apply_validation.md` | Versão legível para revisão |

**Síntese:** 12 itens processados, **0 inserts** / **12 updates**, **0 erros**. `validacao_status`: **12× incompleto**; `qualidade_dado`: **12× media**. Campos sempre vazios no lote: datas (`data_fim_inscricao`, `data_prova`, `data_publicacao`), `cargo`, `curso`. **Taxa de inscrição** preenchida em **12/12** exemplos de payload; **salário** em **9/12** (três linhas só com taxa ou sem remuneração clara).

**View:** validar em staging `public.vw_concursos_front` que os registos `pci_concursos` aparecem como esperado para o front (`/concursos`).

**Conclusão:** apply coerente com o desenho de agregador; PCI mantém-se adequada à **Wave 1 em staging** como descoberta, não como substituto do edital oficial.

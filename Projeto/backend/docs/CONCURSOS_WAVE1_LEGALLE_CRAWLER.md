# Wave 1 — Crawler piloto Legalle Concursos

## Diagnóstico (estrutura pública)

| Aspeto | Observação |
|--------|------------|
| **Portal** | `https://portal.editais.legalleconcursos.com.br` — HTML (Bootstrap, ACT SISTEMAS). |
| **Listagens** | `/edital/index/abertos/` (inscrições abertas), `/edital/index/1/` (em andamento). Menu também: futuros, finalizados, suspensos. |
| **Detalhe** | `/edital/ver/{id}/` — cabeçalho (tipo em `<u>`, órgão), inscrições (`Inscrições de … até …`), local (`Cidade - UF`), aba `#arquivos` (PDFs S3 `cdn.legalle.com.br`), aba `#vagas` (cargos, requisitos, remuneração). |
| **Inscrição** | Período no HTML da ficha; link de inscrição costuma estar na listagem / área do candidato (`candidato.legalleconcursos.com.br`), não extraído neste piloto. |
| **Tipo** | **HTML** servido; página de listagem grande (~850 KB) com várias secções; links `/edital/ver/{id}`. |
| **robots.txt** | Frequentemente **404** no portal de editais; sem blocos `User-agent:` → crawler não bloqueia via `RobotFileParser` vazio. |

## Script e comandos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_legalle_concursos.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave1_legalle/standardized/legalle_standardized.json` |
| Resumo | `crawler_summary.json` / `.md` |
| Testes | `tests/test_legalle_crawler.py` |

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_legalle_concursos.py --max-items 15 --sleep 1.5
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_legalle/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_legalle/loader_dryrun --sources legalle
python -m pytest tests/test_legalle_crawler.py -q
```

## Regras implementadas

- **Fonte:** `fonte=legalle`, `fonte_tipo=banca`, `banca=Legalle`, `categoria=banca_legalle_concurso`.
- **`validacao_status`:** `valido` com `link_edital` (PDF «Abertura e Inscrições» / «Abertura» em `#arquivos`) + `data_fim_inscricao`.
- **Descarte:** `recency_should_discard`, heurísticas de resultado/gabarito/homologação em título/corpo.
- **Sem invenção:** vagas = contagem de cargos na aba `#vagas`; salário a partir de blocos «Remuneração» quando existirem.

## Limitações

1. Listagem única pode incluir certames de várias secções; filtro de recência e listagens `abertos` + `andamento` limitam o ruído.
2. **`data_prova`** só quando aparecer no texto (sem cronograma tabular dedicado como Quadrix).
3. **`numero_vagas`** = número de linhas de cargo na aba vagas, não necessariamente total do edital.
4. **`taxa_inscricao`** depende de menção explícita no HTML.

## Última corrida de referência (2026-05-15)

| Métrica | Valor |
|---------|--------:|
| URLs candidatas (bruto, cap) | **60** |
| Descartados | **55** (maioria `data_fim_inscricao_passada_sem_prova_futura`) |
| **Standardized** | **5** |
| Loader dry-run | `errors_count` **0**, `would_upsert_total` **5**, todos `valido` |

Campos bem preenchidos no subset: título, tipo, órgão/instituição, banca, cargo, nível, estado, município, vagas (contagem de cargos), salário (blocos Remuneração), datas de inscrição, `link`, `link_edital`, validação, qualidade.

Costumam ausentes: `taxa_inscricao`, `data_prova`, `area`, `curso`.

## Recomendação de apply em staging

Dry-run limpo com **5** registos `valido`: recomenda-se **apply em staging** após amostragem rápida de PDFs e datas (atenção a `numero_vagas` = contagem de linhas de cargo, não total oficial do edital). **Apply não executado neste piloto.**

## Relação com o módulo

- **Tabela alvo:** `public.concurso_selecao`.
- **PCI:** fonte banca regional; deduplicação global por `link` / metadados.

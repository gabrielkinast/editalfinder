# Lote 1 — Diagnóstico **SENAI** e **Softex**

**Escopo:** apenas estas duas fontes. **Não** alterado: `opportunity_gate` global, Supabase, migrations, loader apply, `source_readiness.json`.

**Artefactos gerados:**

| Ficheiro | Conteúdo |
|----------|----------|
| `lote1_senai_softex_diagnostico.md` | Este relatório |
| `lote1_senai_softex_diagnostico.json` | Resumo estruturado + métricas |
| `lote1_senai_softex_by_source.json` | Respostas 1–12 por fonte |
| `lote1_senai_softex_examples.json` | Exemplos compactos |

**Pós-correção (pipeline local):**

- Retransformação: `audit_reports_blocked_sources/lote1_fix_senai_softex/`
- Auditoria semântica: `audit_reports_blocked_sources/lote1_fix_senai_softex_semantic/`
- Auditoria documentos: `audit_reports_blocked_sources/lote1_fix_senai_softex_docs/`

---

## PARTE 1 — Diagnóstico por fonte

### SENAI

| # | Pergunta | Resposta |
|---|----------|----------|
| 1 | O crawler roda? | Sim (`python senai/main_senai.py`). |
| 2 | Existe output bruto? | Sim: `senai/outputs/senai_editais.json`. |
| 3 | Quantos itens brutos? | **22** (após correções). Antes: **0** úteis + **1** fallback de índice. |
| 4 | Quantos transformam? | **22** / 22 (dry-run `retransform_all`). |
| 5 | Quantos rejeitados? | **0** (após correções). Antes: o fallback era barrado pelo gate. |
| 6 | Motivos de rejeição? | Nenhum no lote atual. Historicamente: `Pontuacao abaixo do minimo` no índice genérico. |
| 7 | Natureza dos itens? | **Páginas de categoria** da Plataforma Inovação (linhas Smart Factory, Rota 2030, etc.) — misto de **programa/chamada agregada**, não um único PDF de edital. |
| 8 | Onde estava o problema? | **Crawler** (timeout 10s, falta de URL da plataforma, fallback que gravava índice) + **gate** (domínio fora da lista `trusted_fin` do gate global). |
| 9 | Link real ou genérico? | URLs reais em `portaldaindustria.com.br` com path `/categoria/...`. |
| 10 | Detalhe acedido? | Sim (`scrape_source` faz fetch da página de cada candidato). |
| 11 | Documentos/anexos? | Sim: muitos links a PDF na página de categoria → extras com `documentos` / `pdf_url` no standardized. |
| 12 | Recomendação inicial | Coletar está estável; decidir **política de negócio**: aceitar uma linha = um registro ou exigir drill-down por edital. |

### Softex

| # | Pergunta | Resposta |
|---|----------|----------|
| 1 | O crawler roda? | Sim. |
| 2 | Output bruto? | `softex/outputs/softex_editais.json`. |
| 3 | Brutos | **2** (programa Amazônia Geek — inscrições + lançamento com CAIXA). |
| 4 | Transformam | **2** / 2. |
| 5 | Rejeitados | **0** (com soft-continue local). |
| 6 | Motivos (histórico) | Gate por score baixo / “página genérica”. |
| 7 | Natureza | **Chamada / programa** com texto de notícia — **oportunidade real**, não menu. |
| 8 | Problema | **Gate** + descrição curta; crawler OK. |
| 9 | Links | Reais (`softex.br/...`). |
| 10 | Detalhe | Sim (`process_detail_page`). |
| 11 | Anexos | Vazios nestas duas páginas. |
| 12 | Recomendação | Enriquecer corpo/descrição; revisar `validacao_status` suspeito. |

---

## PARTE 2 — Regras esperadas (checklist rápido)

- **SENAI:** conteúdo alinhado a inovação/indústria/fomento; evitar índice puro (removido). Categorias ainda são **agregadores** — monitorizar ruído futuro.
- **Softex:** apenas programas/chamadas; filtros existentes continuam a cortar notícias “Brasil IT” sem inscrição.

---

## PARTE 3 — Correções aplicadas (locais)

1. **`scraper_generic.py`:** timeout HTTP configurável; filtros opcionais de URL e profundidade mínima do path.
2. **`senai/main_senai.py`:** nova listagem, keywords, exclusões, sem fallback de índice.
3. **`softex/main_softex.py`:** hints positivos alargados.
4. **`CORE/transformer.py`:** `_senai_soft_continue` e `_softex_soft_continue` (sem mexer no módulo `opportunity_gate`).

---

## PARTE 4 — Retransformação e auditorias

Comandos executados:

```text
python scripts/retransform_all.py --sources senai,softex --dry-run --output-dir audit_reports_blocked_sources/lote1_fix_senai_softex
python scripts/audit_semantic_classification.py --input-dir audit_reports_blocked_sources/lote1_fix_senai_softex/standardized --output-dir audit_reports_blocked_sources/lote1_fix_senai_softex_semantic
python scripts/audit_docs_pipeline.py --sources senai,softex --output-dir audit_reports_blocked_sources/lote1_fix_senai_softex_docs --max-items 40
```

**Resumo numérico (`retransform_summary`):** 24 brutos, 24 transformados, 0 rejeitados.

**Documentos:** `audit_docs_summary.json` — `perdas_total: 0` (preservação estrutural). Downloads PDF podem falhar no ambiente de auditoria; isso não implica perda de lista de URLs no payload.

---

## PARTE 5 — Readiness (recomendação **sem** editar `config/source_readiness.json`)

| Fonte | Recomendação | Motivo |
|--------|----------------|--------|
| **senai** | **`ready_with_notes`** | Volume OK, 0 rejeições; todos **incompletos**; `perfil_ideal` 0% no standardized; itens são **categorias** agregadas. |
| **softex** | **`ready_with_notes`** | 2 oportunidades claras; **2 suspeitos**, qualidade média **53**, `area` só em metade; sem anexos PDF. |
| **blocked** | Não obrigatório para estas duas após este lote | Critérios mínimos de pipeline atendidos; bloqueio pode ser só política de produto. |
| **ready** (pleno) | Ainda não | Falta maturidade de classificação (`perfil_ideal` / suspeitos / granularidade SENAI). |

### 8–10. Entregáveis finais

8. **Podem sair de `blocked`:** `senai`, `softex` — após aceitar notas acima e revisão humana curta.  
9. **Devem continuar `blocked`:** nenhuma das duas **por defeito técnico** após este trabalho; opcional manter se a equipa não aceitar categorias como registos.  
10. **Próximo passo:** (1) validar negocialmente categorias SENAI; (2) alongar texto Softex no crawler; (3) `load_ready_sources.py --dry-run` só estas fontes; (4) aí sim mover readiness no JSON de configuração.

---

*Nota: durante a retransformação pode aparecer log de perfis Supabase inexistentes no schema local — não faz parte deste escopo e não altera o dry-run de transformação.*

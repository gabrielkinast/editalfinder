# Diagnóstico AMBEV (lote 4)

**Data:** 2026-05-03  
**Objetivo:** Decidir se a fonte entra no módulo edital como oportunidade real (inovação aberta / aceleração / startups) ou permanece fora por marketing/notícia institucional.

## 1. O que a fonte coleta

- **Crawler:** `ambev/main_ambev.py` chama `AmbevScraper`, filtra com `_is_relevant_item` (exclui subchallenge, “resultado final”/closed/newsroom; mantém URLs `100accelerator.com/challenges/<slug>`).
- **Extrator:** `ambev/extrair_informacoes_ambev.py` — listagem curada 100+ e hub `ambev.com.br/startups`.
- **Bruto atual:** `ambev/outputs/ambev_editais.json` — **7** registros, todos desafios temáticos do **100+ Accelerator** (AB InBev / ecossistema Ambev), texto em **inglês**, `fim_inscricao` **null** no JSON (prazos no HTML podem ser ambíguos; o main zera datas inválidas para challenges).

## 2. O crawler roda?

**Sim.** Execução local: `python ambev/main_ambev.py` — concluiu em poucos segundos, processou as 7 páginas de detalhe e gravou 7 itens em `ambev/outputs/`.

## 3. Contagens (antes vs depois da correção local)

| Métrica | Lote 4 legado (`lote4_brasil_legado_diagnostico`) | Após correção (dry-run `lote4_fix_ambev`) |
|--------|-----------------------------------------------------|-------------------------------------------|
| Brutos | 7 | 7 |
| Transformam | 0 | **7** |
| Rejeitam | 7 (gate pontuação/relevância) | **0** |

Correção **sem** alterar `opportunity_gate` global: relaxamento **`_ambev_soft_continue`** em `CORE/transformer.py` + **`calibrate_ambev_extras`** em `CORE/taxonomy_filtros.py`.

## 4. Oportunidade real ou marketing?

- **Não é** marketing institucional genérico, notícia, página de produto ou sustentabilidade “só conteúdo”: cada item é uma **rota de desafio** (`/challenges/<slug>`) com texto de convite a **soluções** / impacto na cadeia.
- **É** oportunidade no critério pedido: **open innovation / aceleração / seleção de soluções e startups** (programa corporativo global 100+), análogo a “chamada” no sentido de **inovação aberta**, não edital público governamental.

## 5. Inscrição, chamada, edital, prazo, formulário, anexos

- No **JSON bruto** não há `fim_inscricao`, `anexos` vazios; **não** preenchemos prazos nem formulários por inferência (evita inventar dados).
- **Documentos:** `audit_docs_pipeline` — 0 PDFs no bruto/transformado; nada a perder na cadeia de docs.
- Detalhes operacionais (formulário, janelas) estão no **site oficial**; o pipeline preserva o **link canônico** da página de desafio.

## 6. A fonte ainda faz sentido no escopo?

**Sim, com ressalva de produto:** faz sentido se o módulo edital incluir **programas de inovação aberta / aceleração corporativa**. Não faz sentido se o escopo for **apenas** editais e chamadas públicas **governamentais** — nesse caso seria **fora_de_escopo** para esse subconjunto, não por ruído, mas por definição de produto.

## 7. Comandos executados (pedido do utilizador)

```text
python scripts/retransform_all.py --sources ambev --dry-run --output-dir audit_reports_blocked_sources/lote4_fix_ambev
python scripts/audit_semantic_classification.py --input-dir audit_reports_blocked_sources/lote4_fix_ambev/standardized --output-dir audit_reports_blocked_sources/lote4_fix_ambev_semantic
python scripts/audit_docs_pipeline.py --sources ambev --output-dir audit_reports_blocked_sources/lote4_fix_ambev_docs
```

## 8. Leitura dos audits pós-fix

- **Semântico:** `audit_semantic_summary.json` — flag `publico_alvo_sem_evidencia` em 7/7 (alerta genérico do script; `perfil_ideal` vem da calibração local).
- **Docs:** sem perdas; sem PDFs na fonte.

## 9. Readiness recomendado (não atualizar `source_readiness.json` aqui)

**`ready_with_notes`**

**Notas obrigatórias para curadoria / produto:**

1. Conteúdo **EN**; `necessita_traducao` pode ser falso no item mas o utilizador final pode querer resumo PT.
2. **`opportunity_gate_relaxed`** com `opportunity_gate_relax_scope=ambev_local` — transparência de que o gate global, sozinho, ainda barra por pontuação/idioma.
3. Ausência de **prazo e valor** no bruto → `validacao_status` tende a **suspeito**; não confundir com fraude de dados, é limite da extração curada.

Se a política de produto **excluir** corporate accelerators do módulo edital, passar a **`fora_de_escopo`** (ou manter **`needs_manual_review`** até decisão explícita) — **não** `blocked` por falha técnica; a fonte é estável e alinhada a URLs oficiais.

## 10. Artefactos desta análise

| Ficheiro |
|----------|
| `audit_reports_blocked_sources/lote4_ambev_diagnostico.md` (este) |
| `audit_reports_blocked_sources/lote4_ambev_diagnostico.json` |
| `audit_reports_blocked_sources/lote4_ambev_examples.json` |

Saídas dos scripts: `audit_reports_blocked_sources/lote4_fix_ambev/`, `lote4_fix_ambev_semantic/`, `lote4_fix_ambev_docs/`.

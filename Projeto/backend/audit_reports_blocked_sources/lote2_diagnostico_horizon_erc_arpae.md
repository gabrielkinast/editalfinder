# Lote 2 — Diagnóstico: Horizon Europe, ERC, DOE ARPA-E

Data de consolidação: 2026-05-02.

**Restrições cumpridas:** não alteração do `opportunity_gate` global, sem `loader apply`, sem Supabase, sem migrations, sem atualização automática de `config/source_readiness.json`.

---

## 1. Horizon Europe

| Pergunta | Resposta |
|----------|----------|
| O crawler roda? | Sim. |
| Existe output bruto? | Sim: `horizon_europe/outputs/horizon_europe_editais.json`. |
| Quantos itens brutos? | **0** (após correções locais). |
| Quantos transformam? | **0** no dry-run (`retransform_by_source.json`). |
| Quantos rejeitados? | **0** (sem bruto, não há rejeição no passo atual). |
| Motivos de rejeição | Nenhum neste ciclo. |
| Natureza do que era coletado antes | Hub de **busca de tópicos** do portal EC — **página institucional / busca**, não uma chamada concreta com objeto e prazo. |
| Onde estava o problema? | Principalmente **crawler/listagem** (nenhum card de oportunidade passando) e **aceitação de hub** no pipeline; **gate/taxonomia** complementares para não classificar índice como oportunidade. |
| Link real ou genérico? | **Genérico** (`topic-search`). |
| Detalhe acessado? | Não havia item de detalhe; apenas o índice. |
| Documentos/anexos? | Não no histórico analisado. |
| Recomendação inicial | **Manter `blocked`**. Código orientado a calls/topics reais; falta **evidência em bruto** (rede estável + URLs de tópico/chamada). |

**Classificação esperada (alvo):** `tipo_oportunidade` em {chamada_publica, grant, chamada_internacional, funding_opportunity}; `tipo_recurso` fomento/grant/financiamento_não_reembolsável/pesquisa; UE/Europa; `idioma_original` en quando aplicável.

---

## 2. ERC

| Pergunta | Resposta |
|----------|----------|
| O crawler roda? | Sim. |
| Output bruto? | `erc/outputs/erc_editais.json`. |
| Itens brutos | **0**. |
| Transformam / rejeitados | **0 / 0** no retransform dry-run. |
| Motivos rejeição | — |
| Histórico | Um item **`fallback_public_index`** para `https://erc.europa.eu/funding` — **hub institucional**, não Starting/Consolidator/Advanced/Synergy/PoC. |
| Problema | **Crawler** (lista) + remoção de hub como único “edital”; **transformer/taxonomia** com calibração local ERC. |
| Link | **Genérico** (/funding). |
| Detalhe | Não. |
| Documentos | Não. |
| Recomendação | **Manter `blocked`** até listagem real de páginas de grant/call. |

**Alvo:** grants ERC; `tipo_oportunidade` grant/chamada_publica/bolsa_pesquisa; perfil pesquisador/universidade/ICT; UE; en.

---

## 3. DOE ARPA-E

| Pergunta | Resposta |
|----------|----------|
| O crawler roda? | Sim. |
| Output bruto? | `doe_arpae/outputs/doe_arpae_editais.json`. |
| Itens brutos | **0**. |
| Transformam / rejeitados | **0 / 0**. |
| Motivos rejeição | — |
| Histórico | **`fallback_public_index`** para `https://arpa-e.energy.gov/funding-opportunities` — **índice**, não FOA/programa concreto. |
| Problema | **Crawler:** uso de `re` sem import no topo (corrigido); filtros que excluem o hub como único item; **transformer** com caminho local ARPA-E. |
| Link | **Genérico** (índice). |
| Detalhe | Não. |
| Documentos | Não no histórico. |
| Recomendação | **Manter `blocked`** até FOAs/program announcements na lista bruta. |

**Alvo:** funding_opportunity / chamada_publica / programa; energia/inovação; EUA; en.

---

## 4. Correções locais aplicadas (resumo)

- **Crawlers:** listagens e filtros por domínio/path; exclusão de hubs genéricos como única “captura”; `doe_arpae`: `import re` corrigido.
- **`CORE/transformer.py`:** relax/continuação **local** por fonte (domínio + marcadores), calibradores pós-enriquecimento; exclusão de defesa genérica onde aplicável.
- **`CORE/taxonomy_filtros.py`:** calibradores Horizon / ERC / ARPA-E (metadados região, idioma, tipos com evidência, evitar tokens ambíguos em ERC).

Nenhuma alteração ao gate global nem ao schema.

---

## 5. Retransformação (dry-run)

```text
python scripts/retransform_all.py --sources horizon_europe,erc,doe_arpae --dry-run --output-dir audit_reports_blocked_sources/lote2_fix_horizon_erc_arpae
```

Resultado: **0 brutos, 0 transformados, 0 rejeitados** por fonte. `old_vs_new` remove os três hubs listados acima (comportamento desejado: não persistir índice como oportunidade).

`CORE/transformer.py --sources horizon_europe,erc,doe_arpae` foi executado para alinhar `CORE/transformer/*_standardized.json` a **listas vazias** coerentes com o bruto atual.

---

## 6. Auditoria semântica

```text
python scripts/audit_semantic_classification.py --input-dir audit_reports_blocked_sources/lote2_fix_horizon_erc_arpae/standardized --output-dir audit_reports_blocked_sources/lote2_fix_horizon_erc_arpae_semantic
```

**0 itens** — sem flags semânticas (`audit_semantic_summary.json`).

---

## 7. Auditoria de documentos

```text
python scripts/audit_docs_pipeline.py --sources horizon_europe,erc,doe_arpae --output-dir audit_reports_blocked_sources/lote2_fix_horizon_erc_arpae_docs
```

**0 itens analisados** — sem perdas nem downloads (`audit_docs_summary.json`). O relatório ainda lista as três fontes com “pior preservação” por score trivial com amostra vazia; interpretar como **N/A**, não regressão real.

---

## 8. Readiness por fonte

| Fonte | Recomendação | Motivo |
|--------|--------------|--------|
| horizon_europe | **blocked** | Sem itens brutos; critérios `ready` / `ready_with_notes` exigem transformados > 0 e evidência de oportunidades reais. |
| erc | **blocked** | Idem. |
| doe_arpae | **blocked** | Idem. |

**`needs_manual_review`** seria adequado apenas como etiqueta de processo (“código revisado, falta validação com rede”); para **sair de `blocked` na lista oficial** recomenda-se primeiro **lote de brutos não vazio** com chamadas/FOAs reais.

Não se recomenda **`ready_with_notes`** neste estado (transformados = 0).

---

## 9. Fontes que podem sair de `blocked`

**Nenhuma** das três neste momento.

---

## 10. Fontes que devem continuar `blocked`

**horizon_europe**, **erc**, **doe_arpae** até nova coleta com itens válidos.

---

## 11. Próximo passo no restante do Lote 2

Outras fontes ainda em `blocked` com perfil internacional/estratégico (para auditoria semelhante, sem gate global): por exemplo **iarpa**, **nato_diana**, **sam_gov**; em seguida **japan_e_rad**, **japan_jaxa**, **science_scraper**, conforme prioridade de negócio.

---

## Ficheiros de entrega

| Ficheiro |
|----------|
| `audit_reports_blocked_sources/lote2_diagnostico_horizon_erc_arpae.md` (este) |
| `audit_reports_blocked_sources/lote2_diagnostico_horizon_erc_arpae.json` |
| `audit_reports_blocked_sources/lote2_horizon_erc_arpae_by_source.json` |
| `audit_reports_blocked_sources/lote2_horizon_erc_arpae_examples.json` |

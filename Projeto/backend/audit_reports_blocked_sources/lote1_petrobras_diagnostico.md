# Lote 1 — Diagnóstico Petrobras

## Resumo

| Métrica | Valor |
|--------|------:|
| Itens brutos (atual) | 4 |
| Transformados | 4 |
| Rejeitados | 0 |

**Bruto:** `petrobras/outputs/petrobras_editais.json` (listagens oficiais de seleções públicas / patrocínio, sem notícias genéricas).

## Situação anterior (para contexto)

- **5** linhas no JSON bruto: duplicata **http** vs **https** para a mesma página de inscrições incentivadas.
- O **opportunity_gate** global rejeitava todos com **«Pontuacao abaixo do minimo (oportunidade nao evidenciada)»** — texto curto na listagem e domínio externo (`bussolasocial.com.br`).
- **Nenhuma** alteração foi feita ao módulo `opportunity_gate`; o fluxo passa por **`_petrobras_soft_continue`** e **`calibrate_petrobras_extras`** apenas no `transformer`.

## Classificação dos links (lote atual)

| Link / padrão | Interpretação |
|---------------|-----------------|
| `investidor.bussolasocial.com.br/petrobras/editais/...` | **Chamada pública** de inscrição a seleções de patrocínio (incentivados / não incentivados). |
| `petrobras.com.br/documents/.../*.pdf` | **Regulamento** (PDF) da mesma seleção pública — documento oficial, não página institucional vazia. |

Não há no lote: licitação/pregão, portal de fornecedores, notícia pura ou hub genérico.

## Crawler

- `DENY_PATH` / `DENY_TITLE` continuam a afastar notícias e ruído.
- **`normalize_petrobras_url`**: HTTPS na Bússola + dedupe no `main_petrobras`.
- Sem fallback de índice; sem scraping agressivo (mantém `curl`/requests existentes).

## Transformer / classificação

- **`build_defense_extras`** não corre em `petrobras` (evita confundir com licitação/fornecedor).
- **`calibrate_petrobras_extras`**: `tipo_oportunidade` → `chamada_publica`; metadados `tipo_conteudo_petrobras`; `tipo_recurso` alinhado a patrocínio/subvenção cultural onde aplicável.

## Artefactos

- `lote1_petrobras_diagnostico.json` — métricas e resumo por URL.
- `lote1_petrobras_examples.json` — amostra pós-transformação (tipo, documentos, gate relaxado).

## Recomendação de readiness (manual)

Com **4/4** transformados, **0** rejeitados, itens alinhados a **seleções de patrocínio** e **regulamentos**, sugerir **`ready_with_notes`**:

- Notas: volume pequeno; datas de inscrição podem estar desatualizadas no portal; dois itens Bússola sem PDF anexo no crawler (apenas HTML); gate relaxado localmente (`opportunity_gate_relaxed`).

**Não** promover a `ready` pleno até validar em staging se as páginas Bússola ainda respondem e se convém enriquecer descrição com mais texto do detalhe (sem burlar login).

Não alterar `source_readiness.json` / `readiness_for_loader.json` nesta tarefa (apenas relatório).

## Retransformação e auditorias (artefactos)

- **Retransformação:** `audit_reports_blocked_sources/lote1_fix_petrobras/` — 4 brutos → 4 transformados, 0 rejeitados (`retransform_summary.json`).
- **Semântica:** `audit_reports_blocked_sources/lote1_fix_petrobras_semantic/` — com 4 itens há flags esperadas de heurística genérica (ex.: `publico_alvo_sem_evidencia`, `classificacao_incoerente_com_fonte` em parte dos itens); volume baixo; revisar com texto ampliado do detalhe se necessário.
- **Documentos:** `audit_reports_blocked_sources/lote1_fix_petrobras_docs/` — **0** perdas no payload; PDFs dos regulamentos preservados no transformado/payload; downloads no audit podem falhar por rede (não implica perda estrutural no JSON).

# Diagnóstico lote 3B China

Gerado em (UTC): 2026-05-02T21:31:41Z

## Política
- Exit code **2** nos crawlers asiáticos: operação esperada quando o JSON anterior é preservado; **não** tratar como crash.
- Falha de coleta **não** deve sobrescrever `*_editais.json` com `[]` se houver dados anteriores.

## Resumo por fonte
### china_nsfc
- **Exit code:** 0
- **Itens em `*_editais.json`:** 28 (bruto_real_para_retransform: True)
- **Tipo dominante:** `coleta_com_itens`
- **Diagnóstico (rede vs filtro):** n/a (sem latest_error após sucesso)
- **latest_error.json:** não
- **Linhas em failures.jsonl (esta fonte):** 0 (novas desde o limiar UTC 2026-05-02T21:19:00Z: 0)
- **Readiness recomendado (manual):** **ready_with_notes** — Coleta com itens; algumas listagens NSFC ou espelhos falharam (HTTP não OK). Sem latest_error após gravação bem-sucedida.

### china_cnnc
- **Exit code:** 2
- **Itens em `*_editais.json`:** 1 (bruto_real_para_retransform: True)
- **Tipo dominante:** `falha_de_coleta`
- **Diagnóstico (rede vs filtro):** rede_acesso_listagem
- **latest_error.json:** sim
- **Linhas em failures.jsonl (esta fonte):** 2 (novas desde o limiar UTC 2026-05-02T21:19:00Z: 1)
- **Readiness recomendado (manual):** **blocked** — Todas as listagens falharam (rede ou bloqueio); exit 2 preservou JSON anterior (1 item). Atualização em tempo real bloqueada.

### china_avic
- **Exit code:** 0
- **Itens em `*_editais.json`:** 15 (bruto_real_para_retransform: True)
- **Tipo dominante:** `coleta_com_itens`
- **Diagnóstico (rede vs filtro):** n/a (sem latest_error após sucesso)
- **latest_error.json:** não
- **Linhas em failures.jsonl (esta fonte):** 0 (novas desde o limiar UTC 2026-05-02T21:19:00Z: 0)
- **Readiness recomendado (manual):** **ready** — 15 itens gravados; coleta estável nesta execução.

### china_norinco
- **Exit code:** 2
- **Itens em `*_editais.json`:** 1 (bruto_real_para_retransform: True)
- **Tipo dominante:** `coleta_vazia_sem_confirmacao` (secundário: `coleta_vazia_pos_filtros`)
- **Diagnóstico (rede vs filtro):** filtro_keyword_gate_com_listagem_ok
- **latest_error.json:** sim
- **Linhas em failures.jsonl (esta fonte):** 2 (novas desde o limiar UTC 2026-05-02T21:19:00Z: 1)
- **Readiness recomendado (manual):** **needs_manual_review** — A execução devolveu 0 itens após filtros ou gate; subsítios EN falham; JSON anterior preservado (1 item). Requer revisão de URLs, listagens ou calibração.

### china_university_procurement
- **Exit code:** 0
- **Itens em `*_editais.json`:** 6 (bruto_real_para_retransform: True)
- **Tipo dominante:** `coleta_com_itens`
- **Diagnóstico (rede vs filtro):** n/a (sem latest_error após sucesso)
- **latest_error.json:** não
- **Linhas em failures.jsonl (esta fonte):** 0 (novas desde o limiar UTC 2026-05-02T21:19:00Z: 0)
- **Readiness recomendado (manual):** **ready_with_notes** — 6 itens (USTC); Tsinghua e PKU com falhas de listagem nesta execução.

## Eventos novos em failures.jsonl (após o limiar)
- Linha 4 | china_cnnc | ts=2026-05-02T21:23:00Z | kind=falha_de_coleta | tipo=falha_de_coleta
- Linha 5 | china_norinco | ts=2026-05-02T21:23:23Z | kind=coleta_vazia_sem_confirmacao | tipo=coleta_vazia_pos_filtros

## Pipelines locais (sem loader apply)
- `retransform_all.py` dry-run -> `audit_reports_blocked_sources/lote3b_fix_china`
- `audit_semantic_classification.py` -> `lote3b_fix_china_semantic`
- `audit_docs_pipeline.py` -> `lote3b_fix_china_docs`
- `audit_source_access_methods.py` -> relatórios em `audit_reports_access`

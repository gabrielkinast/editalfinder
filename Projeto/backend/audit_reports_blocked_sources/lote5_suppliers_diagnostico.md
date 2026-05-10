# Lote 5 — Fornecedores / defesa corporativa (diagnóstico)

**Data:** 2026-05-03  
**Fontes:** `bae_systems_suppliers`, `rheinmetall_suppliers`, `thales_suppliers`, `japan_kawasaki_heavy`  
**Estado em `config/source_readiness.json`:** as quatro em **`needs_manual_review`** (não alterado automaticamente nesta tarefa).

---

## Resumo executivo

Trata-se de **portais corporativos** de procurement/fornecedores, não de editais de fomento público. Após correções locais de **URLs**, **filtros de ruído** (privacidade/careers/paginação falsa) e **calibração + relaxamento local do gate** (sem editar `opportunity_gate.py` global), apenas **`rheinmetall_suppliers`** produziu **2** itens brutos estáveis, ambos **transformados** (2/2, 0 rejeitados). As outras três fontes ficaram com **0** brutos neste ambiente: **BAE/Thales** por **heurística de extração e/ou resposta HTML mínima (WAF)**; **Kawasaki** por **falha de rede/HTTP** nas listagens.

---

## PARTE 1 — Diagnóstico por fonte (11 perguntas)

| # | Pergunta | BAE | Rheinmetall | Thales | Kawasaki |
|---|----------|-----|-------------|--------|----------|
| 1 | Crawler corre? | Sim | Sim | Sim | Sim (com falha de coleta) |
| 2 | Output bruto existe? | Sim (`[]`) | Sim | Sim (`[]`) | Sim (`[]` + `latest_error.json`) |
| 3 | Qtd brutos | 0 | **2** | 0 | 0 |
| 4 | Qtd transformam | 0 | **2** | 0 | 0 |
| 5 | Qtd rejeitam (gate) | 0 | 0 | 0 | 0 |
| 6 | Natureza dos links | Sem âncoras úteis no HTML recebido | Onboarding + portal Ivalua | Site rico; scrape 0 âncoras | Listagens falharam |
| 7 | Ação concreta fornecedor? | Não no bruto | **Sim** | No site, não no bruto | Não |
| 8 | Formulário/onboarding? | Esperado HICX | **Sim** (texto + portal) | Ferramentas restritas | Não extraído |
| 9 | Documento/anexo? | Não | Não (itens finais) | PDFs no site, não colhidos | Não |
| 10 | Faz sentido no produto? | Sim, com anti-bot/estratégia | **Sim** | Sim, com novo extrator | Condicional (acesso .jp) |
| 11 | Problema principal | Acesso/heurística | ~~Gate login~~ mitigado localmente | Crawler/heurística | Acesso/rede |

Detalhe estruturado: `audit_reports_blocked_sources/lote5_suppliers_by_source.json`.

---

## PARTE 2 — Regra de escopo (produto)

- **Entram** apenas com **ação concreta** para fornecedor (cadastro, portal, onboarding, sourcing corporativo, etc.), classificados como **`supplier_portal` / `cadastro_fornecedor` / `procurement_corporativo`**, com **`tipo_recurso`** orientado a **`oportunidade_fornecedor`** e **`perfil_ideal`** `fornecedor`/`empresa`.
- **Não entram** páginas puramente institucionais, notícias, careers, investors, política sem ação, etc.
- **`setor_estrategico`**: só com **evidência no texto** — a calibração local **remove** tags de defesa genéricas quando o texto não contém termos militares/defesa.

---

## PARTE 3 — Correções locais (ficheiros)

1. **`bae_systems_suppliers/main_bae_systems_suppliers.py`** — listagem UK; `hicx.net` em `allowed_domains`.  
2. **`rheinmetall_suppliers/main_rheinmetall_suppliers.py`** — URLs oficiais válidas; domínios do portal; sem microsite que gerava página só GDPR.  
3. **`thales_suppliers/main_thales_suppliers.py`** — `supplier-relations` + `/supplier`.  
4. **`japan_kawasaki_heavy/main_japan_kawasaki_heavy.py`** — remoção de `/en/news/`.  
5. **`defense_source_common.py`** — sem `?page=2` artificial em páginas supplier estáticas; exclusão de URLs `datenschutz`, `privacy-policy`, `careers`, `investors`, etc.  
6. **`CORE/taxonomy_filtros.py`** — `calibrate_corporate_supplier_sources_extras`.  
7. **`CORE/transformer.py`** — `_corporate_supplier_soft_continue` + integração na cadeia do gate; calibração por fonte.

**Não feito (conforme pedido):** apply, Supabase, migrations, alteração global do gate, `source_readiness.json`.

---

## PARTE 4 — Pipeline executado

- Crawlers dos quatro `main_*.py`.  
- `retransform_all.py` → `audit_reports_blocked_sources/lote5_fix_suppliers/`.  
- `audit_semantic_classification.py` → `lote5_fix_suppliers_semantic/`.  
- `audit_docs_pipeline.py` → `lote5_fix_suppliers_docs/`.  
- `audit_source_access_methods.py` → `audit_reports_access/`.

**Totais finais (retransform):** 2 brutos, 2 transformados, 0 rejeitados (apenas Rheinmetall com dados).

---

## PARTE 5 — Readiness recomendado

| Fonte | Readiness | Comentário breve |
|--------|------------|------------------|
| **rheinmetall_suppliers** | **`ready_with_notes`** | 2 itens; onboarding + portal; `oportunidade_fornecedor`; gate relax **local** documentado em `extras`. |
| **bae_systems_suppliers** | **`needs_manual_review`** | 0 itens; provável **WAF/anti-bot** ou filtro de âncoras — não promover sem dados. |
| **thales_suppliers** | **`needs_manual_review`** | 0 itens; site correto mas **crawler** não segue PDFs/âncoras úteis. |
| **japan_kawasaki_heavy** | **`blocked`** | Falha de **acesso/rede** às listagens; `latest_error.json` com `todas_as_listagens_falharam_ou_rede`. |

### Quem pode sair de `needs_manual_review`?

- **Pode:** **`rheinmetall_suppliers`** (com notas: volume baixo, portal com login na continuação, sem prazos tipo edital).  
- **Não deve ainda:** **`bae_systems_suppliers`**, **`thales_suppliers`**, **`japan_kawasaki_heavy`** (sem bruto útil ou com bloqueio de acesso).

---

## Auditorias — leitura rápida

- **Semântica:** `publico_alvo_sem_evidencia` em **2/2** itens Rheinmetall (flag genérica do audit; `publico_alvo` vem preenchido na calibração).  
- **Docs:** 2 itens analisados; ver `audit_docs_summary.json` (downloads PDF opcionais podem falhar por rede).  
- **Acesso:** seeds em `source_access_by_source.json` podem ainda apontar URLs antigas na política; probes mistos (404 legado Rheinmetall, etc.) — alinhar política numa tarefa futura.

---

## Artefactos gerados

| Ficheiro |
|----------|
| `audit_reports_blocked_sources/lote5_suppliers_diagnostico.md` (este) |
| `audit_reports_blocked_sources/lote5_suppliers_diagnostico.json` |
| `audit_reports_blocked_sources/lote5_suppliers_by_source.json` |
| `audit_reports_blocked_sources/lote5_suppliers_examples.json` |

---

## Próximo passo sugerido

1. **Rheinmetall:** revisão humana curta dos 2 links; depois eventual dry-run loader (fora do âmbito deste pedido).  
2. **Thales:** implementar colheita dirigida a **PDFs** e secções “Key documents” / âncoras com `supplier`.  
3. **BAE:** testar **UA/browser** ou lista curada aprovada (`official_link_only` documentado) sem burlar WAF.  
4. **Kawasaki:** novo mapeamento de URL ou execução com **proxy/JP** conforme política; até lá manter **blocked**.

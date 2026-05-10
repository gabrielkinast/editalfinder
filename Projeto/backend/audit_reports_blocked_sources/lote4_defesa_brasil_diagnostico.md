# Lote 4 — diagnóstico defesa Brasil (AMAZUL, Marinha, DCTA/ITA/IAE)

**Data:** 2026-05-02  

**Restrições:** sem alterar `opportunity_gate` global, sem `loader apply`, sem Supabase, sem migrations, sem contornar Cloudflare/captcha/paywall.

## Resumo executivo

| Fonte | Brutos | Transformam | Rejeitados | Problema principal | Readiness sugerido |
|-------|--------|-------------|------------|--------------------|--------------------|
| AMAZUL | 20 | 19 | 1 | URLs antigas 404 (corrigido); 1 item barrado pelo gate | **ready_with_notes** |
| Marinha | 0 | 0 | 0 | HTTP 403 Cloudflare nas listagens | **manter blocked** |
| DCTA/ITA/IAE | 0 | 0 | 0 | HTTP 404 nas URLs `gov.br/dcta|ita|iae/pt-br/*` | **manter blocked** |

Artefactos numéricos: `lote4_defesa_brasil_by_source.json`, exemplos: `lote4_defesa_brasil_examples.json`, detalhe estruturado: `lote4_defesa_brasil_diagnostico.json`.

## AMAZUL

1. **Crawler roda?** Sim.  
2. **Output bruto?** `amazul/outputs/amazul_editais.json`.  
3. **Brutos:** 20.  
4. **Transformam (dry-run):** 19.  
5. **Rejeitados:** 1 (`Noticia ou pagina generica sem chamada evidenciada` — `dispensa-de-licitacao-032024`).  
6. **Motivos:** ver `retransform_by_source.json` → `motivos_rejeicao_principais`.  
7. **Tipo de itens:** em geral **licitação / dispensa / compra pública** com extratos e PDFs; não são menus genéricos.  
8. **Problema:** antes **URL** (`/licitacoes` 404); após correção, **documento/ruído** — PDF DOU pode trazer trechos de outros órgãos no texto agregado.  
9. **PDFs?** Sim (extratos, termos); pipeline de auditoria marca `downloads_falharam` com `pdf_skip`/heurística de re-leitura — metadados de `pdf_url` e `documentos` preservados no payload.  
10. **Prazo / processo / órgão / objeto?** Presentes em muitos registos (UASG, NUP, objeto, DOU).  
11. **Manter no projeto?** Sim.  
12. **Recomendação:** **ready_with_notes** — validar se compras administrativas (ex.: serviços postais) entram no produto; auditoria semântica: `fonte_defesa_sem_defesa` = 2 (10,53%) após moderar `setor_estrategico` só com evidência no texto.

**Correções:** listagem → `https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos`; calibração local e `source_access_policy.json` (seed + nota).

## Marinha

1. **Crawler roda?** Sim (sem exceção).  
2. **Output bruto?** `marinha/outputs/marinha_editais.json` (lista vazia).  
3. **Brutos:** 0.  
4. **Transformam:** 0.  
5. **Rejeitados:** 0.  
6. **Motivos:** —  
7. **Conteúdo:** não há itens; resposta às listagens é **página de desafio Cloudflare**, não HTML de editais.  
8. **Problema:** **acesso** (intermediário), não taxonomia.  
9. **PDFs?** Não na amostra atual.  
10. **Metadados de edital:** não aplicável.  
11. **Manter no projeto?** Sim enquanto houver estratégia futura (fonte alternativa ou curadoria).  
12. **Recomendação:** **manter blocked** até existir endpoint público estável sem challenge para o mesmo perfil de cliente HTTP usado pelo projeto.

**Correções:** calibração e política de acesso (nota); sem bypass de WAF.

## DCTA / ITA / IAE

1. **Crawler roda?** Sim.  
2. **Output bruto?** `dcta_ita_iae/outputs/dcta_ita_iae_editais.json` (vazio).  
3. **Brutos:** 0.  
4. **Transformam:** 0.  
5. **Rejeitados:** 0.  
6. **Motivos:** —  
7. **Conteúdo:** não aplicável; URLs configuradas não servem mais de listagem.  
8. **Problema:** **crawler + URL** — `gov.br/dcta|ita|iae/pt-br/...` devolve **404** (conteúdo removido ou migrado).  
9. **PDFs?** Não na coleta atual.  
10. **Metadados:** não aplicável.  
11. **Manter no projeto?** Sim, após redescobrir URLs oficiais ou integração PNCP/FAB documentada.  
12. **Recomendação:** **manter blocked** até novo hub verificável (sem inventar caminhos).

**Correções:** comentário em `main_dcta_ita_iae.py`, calibração DCTA (área/setor por texto), nota em `source_access_policy.json`.

## Retransformação e auditorias (executado)

- `python scripts/retransform_all.py --sources amazul,marinha,dcta_ita_iae --dry-run --output-dir audit_reports_blocked_sources/lote4_fix_defesa_brasil`
- `python scripts/audit_semantic_classification.py --input-dir .../standardized --output-dir ..._semantic`
- `python scripts/audit_docs_pipeline.py --sources amazul,marinha,dcta_ita_iae --output-dir ..._docs`
- `python scripts/audit_source_access_methods.py --sources amazul,marinha,dcta_ita_iae`

## Fontes que podem sair de `blocked` vs permanecem

- **Podem sair (com notas):** **AMAZUL** — há oportunidades reais de contratação e metadados; depende da política de produto para compras administrativas.  
- **Continuam blocked:** **Marinha** (acesso Cloudflare), **DCTA/ITA/IAE** (URLs 404 até novo mapeamento).

`source_readiness.json` **não** foi alterado, conforme pedido.

## Contexto dos relatórios anteriores

- `audit_reports_blocked_sources/lote4_brasil_legado_diagnostico.md` — estado anterior com 0 brutos nas três fontes.  
- `audit_reports_blocked_sources/lote1_dcta_ita_iae_diagnostico.md` — histórico de fallback de índice removido.

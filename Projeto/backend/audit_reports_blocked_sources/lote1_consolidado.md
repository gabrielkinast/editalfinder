# Lote 1 — relatório consolidado (fontes bloqueadas → prontas)

**Data:** 2026-05-02  
**Âmbito:** `badesul`, `pncp`, `senai`, `softex`, `plataforma_industria`, `petrobras`, `marinha`, `amazul`, `dcta_ita_iae`.

**Gate global:** não alterado neste lote.  
**Supabase / migrations / apply:** não executados nesta entrega (excepto registo opcional de dry-run em `carga_execucao` se o script o fizer — o apply real continua pendente).

---

## 1. Tabela por fonte

| Fonte | Estado antes (resumo) | Estado depois | Itens `*_standardized.json` | Documentos (std) | pdf_url (std) | Problemas corrigidos (resumo) | Readiness | Já em staging? | Pode aplicar agora? | Observações |
|--------|------------------------|----------------|------------------------------|------------------|---------------|-------------------------------|-------------|----------------|---------------------|-------------|
| badesul | Blocked; gate agressivo | ready_with_notes | 10 | 0 | 0 | Gate/calibração local crédito | ready_with_notes | **Sim** (histórico equipa) | **Sim** | Dry-run: 10 would_upsert, 0 erros. |
| pncp | Blocked; URL raiz / gate | ready_with_notes | 1 | 0 | 0 | Link PNCP + `calibrate_pncp_extras` | ready_with_notes | Não confirmado | **Sim** | Volume baixo no crawl actual. |
| senai | Blocked; Portal Indústria | ready_with_notes | 1 | 0 | 0 | Gate local + calibração portal | ready_with_notes | Não confirmado | **Sim** | **Canónico** para Plataforma Inovação. |
| softex | Blocked; texto curto | ready_with_notes | 2 | 0 | 0 | Gate Softex + calibração | ready_with_notes | Não confirmado | **Sim** | Monitorizar flags semânticas / texto curto. |
| plataforma_industria | Blocked | ready_with_notes | 1 | 0 | 0 | Gate partilhado + canonização | ready_with_notes | Não confirmado | **Sim** | **Alias** de `senai`; loader ignora duplicado de URL (ver `source_canonicalization.json`). |
| petrobras | Blocked; Bússola/PDF | ready_with_notes | 5 | 0 | 2 | Gate Petrobras + calibração | ready_with_notes | Não confirmado | **Sim** | pdf_url preservado no dry-run combinado (2 itens). |
| marinha | Fallback índice | blocked / needs_manual_review | 1* | 0 | 0 | Sem fallback; filtros; gate/calibração local | blocked | Não | **Não** | *Possível linha legada no standardized; brutos JSON vazios — nova coleta. |
| amazul | Idem | blocked / needs_manual_review | 1* | 0 | 0 | Idem Marinha | blocked | Não | **Não** | *Idem. |
| dcta_ita_iae | Fallback DCTA | blocked / needs_manual_review | 0 | 0 | 0 | Sem fallback; secções gov.br; gate/calibração | blocked | Não | **Não** | Ver `lote1_dcta_ita_iae_diagnostico.*`. |

**Nota métricas “brutos / transformados / rejeitados” iniciais:** o ficheiro `lote1_by_source.json` reflecte um snapshot **antes** das correcções; para contagens actuais use os JSON em `CORE/transformer/*_standardized.json` e os relatórios `lote1_*_diagnostico.*` por fonte.

---

## 2. Listas operacionais

### 2.1 Prontas para incluir em staging (lote 1)

`badesul`, `pncp`, `senai`, `softex`, `plataforma_industria`, `petrobras`

### 2.2 Permanecem bloqueadas (lote 1)

`marinha`, `amazul`, `dcta_ita_iae`

---

## 3. Canonização SENAI / Plataforma Indústria

- **Canónico:** `senai`  
- **Alias:** `plataforma_industria`  
- **Configuração:** `config/source_canonicalization.json` (grupo `plataforma_inovacao`, política `skip_alias_if_canonical_exists`).  
- **Dry-run combinado:** `canonical_skipped_total = 0` (sem colisões de URL no conjunto actual).

---

## 4. Dry-run combinado do loader

- **JSON:** `audit_reports_blocked_sources/lote1_ready_sources_loader_dryrun.json`  
- **Markdown:** `audit_reports_blocked_sources/lote1_ready_sources_loader_dryrun.md`  
- **Input actualizado:** `audit_reports_retransform/standardized` (não `CORE/transformer`). Antes do dry-run, `badesul` e `pncp` foram **copiados** para essa pasta a partir das calibrações mais recentes (listado no JSON/MD do dry-run).
- **Resumo (última execução):** **89** standardized → **67** would_upsert (**22** saltos por canonização SENAI vs `plataforma_industria`); **0** erros de mapeamento; **0** itens críticos vazios; **48** itens com documentos preservados; **25** `pdf_url` preservados; **67** com `validacao_status` e `qualidade_dado` preservados nos itens que seriam upsert.

**Readiness:** `badesul` foi movido de `fontes_bloqueadas_temporariamente` para `fontes_prontas_para_loader` em `audit_reports_retransform/readiness_for_loader.json` para o `--exclude-blocked` não o bloquear indevidamente (alinhado com “já carregado / pronto com notas”).

---

## 5. Comando recomendado para apply staging (não executar)

Definir confirmação explícita de staging (exemplo PowerShell):

```powershell
$env:EDITALFINDER_ALLOW_STAGING_APPLY = "1"
$env:EDITALFINDER_ENV = "staging"
python scripts/load_ready_sources.py --apply --staging --sources badesul,pncp,senai,softex,plataforma_industria,petrobras --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

Ajustar variáveis ao que o projecto já usa em `.env.staging` / documentação interna. **Não** correr sem rever o guard de ambiente (`has_allow_staging_apply`, host Supabase).

---

## 6. Próximos passos (lote 2)

1. Tratar outras fontes em `fontes_bloqueadas_temporariamente` fora deste lote (ex.: `ambev`, `apex`, `china_*`, `doe_arpae`, `erc`, `horizon_europe`, `iarpa`, `sam_gov`, `science_scraper`) com o mesmo pipeline de diagnóstico → correcções locais → retransform → auditorias.  
2. Triar `fontes_para_revisao` (`bae_systems_suppliers`, `faperg`, `japan_*`, fornecedores NATO, etc.).  
3. Após nova coleta **Marinha / AMAZUL / DCTA**, actualizar brutos, `transformer.py` por fonte, readiness e repetir dry-run antes de desbloquear.

---

## 7. JSON máquina-legível

Dados estruturados completos: `audit_reports_blocked_sources/lote1_consolidado.json`.

# BACKEND 10.2D — BNDES Controlled Detail/PDF Deadline Discovery

## Objetivo

Fluxo controlado para descobrir prazos BNDES em páginas de detalhe e PDFs, sem inventar deadline e sem apply automático.

## Por que BNDES é mais difícil

| Tipo | Exemplo | Tratamento |
|------|---------|------------|
| Chamada com prazo | "Inscrições até DD/MM/YYYY" | Candidato a update |
| Chamada sem prazo | Edital sem deadline no texto | `missing_from_loader` |
| Linha permanente | BNDES Mais Inovação | `permanent_funding_line` — não é ruído |
| Notícia de lançamento | "BNDES lançou, em ..." | Data **não** vira prazo; PDF/detail se houver link |
| Publicação/resultado | "Publicado em ..." | Rejeitado como deadline |

## Flags

| Flag | Default |
|------|---------|
| `EDITALFINDER_ENABLE_DEADLINE_BACKFILL` | OFF |
| `EDITALFINDER_ALLOW_CONTROLLED_APPLY` | OFF |

Lote máximo BNDES: **50** (`--confirm-large` acima disso).

## Recrawl

```bash
cd backend
python scripts/recrawl_bndes.py --limit 50 --output outputs/recrawl/bndes/bndes_recrawl.json --no-network
python scripts/recrawl_bndes.py --limit 200 --output outputs/recrawl/bndes/bndes_recrawl.json
```

Limites live: `--max-detail-fetches 30`, `--max-pdf-fetches 10`, `--http-timeout 15`.

## Extração HTML

- `fetch_bndes_detail_page()` — timeout, host `bndes.gov.br` only, max 1.5MB
- `extract_bndes_html_text()` — BeautifulSoup leve
- `discover_bndes_documents()` — links PDF/edital

## Extração PDF leve

- Usa `pdf_enrichment.extract_pdf_text_with_fallback` (pypdf → pdfplumber)
- Max 5MB, 5 páginas, timeout 15s
- Sem OCR de imagem

Se biblioteca indisponível: `error: no_library` — documentado como limitação.

## Dry-run

```bash
python scripts/dry_run_bndes_deadline_apply.py --input outputs/recrawl/bndes/bndes_recrawl.json
python scripts/dry_run_bndes_deadline_apply.py --input ... --compare-db
```

Saídas: `outputs/bndes_deadline_apply/` incluindo `pdf_candidates.json`.

## Apply controlado

**Bash:**

```bash
EDITALFINDER_ENABLE_DEADLINE_BACKFILL=1 \
EDITALFINDER_ALLOW_CONTROLLED_APPLY=1 \
python scripts/apply_bndes_deadline_backfill.py \
  --input outputs/bndes_deadline_apply/candidates_to_update.json
```

**PowerShell:**

```powershell
$env:EDITALFINDER_ENABLE_DEADLINE_BACKFILL="1"
$env:EDITALFINDER_ALLOW_CONTROLLED_APPLY="1"
python scripts/apply_bndes_deadline_backfill.py --input outputs/bndes_deadline_apply/candidates_to_update.json
Remove-Item Env:EDITALFINDER_ENABLE_DEADLINE_BACKFILL
Remove-Item Env:EDITALFINDER_ALLOW_CONTROLLED_APPLY
```

## Auditoria pós-ingest

```bash
python scripts/audit_validity_backend.py --from-db --source bndes --limit 1000
python scripts/audit_noise_backend.py --from-db --source bndes --limit 1000
python scripts/dry_run_quality_enrichment.py --from-db --source bndes --limit 1000 --with-deadline-backfill
```

## Limitações

- Sem OCR pesado; PDFs escaneados não são lidos.
- Live recrawl limitado a N fetches de detalhe/PDF por execução.
- Notícias nunca usam data de publicação como prazo.
- Sem migration/schema/frontend.

## Próximo patch recomendado

**BACKEND 10.3** — consolidação cross-source de métricas pós-apply ou detail fetch DOE eXCHANGE leve.

## Confirmação

- Nenhum apply automático neste patch.
- Nenhuma migration criada.
- Nenhuma alteração de schema Supabase.

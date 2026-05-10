# Recovery A — DoD SBIR/STTR

## Alterações (crawler + transformação)

- **API:** primária; em **429** fallback HTML só em `/topics` e `/solicitations`.
- **Deny paths:** `/api`, `/data-resources`, `/participating-agencies`, `/impact`, `/faq`, `/about`, `/company-registration`, `/awards`, `/portfolio`, `/resources`, `/lab2market`, `/community`, **`/success-stories`**, **`/events-listing`**, `/events`, `/news`, `/program-highlights`.
- **Fallback HTML:** só entram URLs de **detalhe** — `/topics/<id>`, `/solicitation/...` ou `/solicitations/<slug>` (hubs institucionais excluídos antes do transform).
- **Calibração:** `calibrate_dod_sbir_sttr_extras` — `setor_estrategico` ≤ 3; título genérico "Topic" → rótulo com ID do tópico.
- **Gate (sem alterar `opportunity_gate` global):** `_dod_sbir_sttr_topic_soft_continue` no `transformer.py` com scope `dod_sbir_sttr_recovery_a_local`; em `item_quality.py`, esses itens ficam **`incompleto`** (não `suspeito`).

## Resultado atual (dry-run `recovery_a/`)

- **6** brutos e **6** standardized (tópicos reais).
- **mapping_errors:** 0 (loader-only).
- **API:** ainda sujeita a 429 — volume depende da disponibilidade da API.

## Ficheiros

- JSON: `recovery_a_dod_sbir.json`
- Raw: `recovery_a/raw/dod_sbir_sttr_editais.json`
- Standardized: `recovery_a/standardized/dod_sbir_sttr_standardized.json`

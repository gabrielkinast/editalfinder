# Recomendação de readiness — PNCP (pós-calibração local)

## Classificação: **ready_with_notes**

O pipeline **transforma com qualidade** os itens PNCP com a calibração local (taxonomia + metadados + links oficiais). O **gate global da fonte permanece `blocked`** conforme decisão operacional — esta nota descreve prontidão **técnica**, não liberação automática.

## Critérios atendidos (ready_with_notes)

| Critério | Situação |
|----------|----------|
| Transformados > 0 | Sim (`31` itens no dry-run com o `pncp_editais.json` atual). |
| Ruído baixo | `ruido_passou=0` no quick audit. |
| `perfil_ideal` coerente | 100% preenchido após `calibrate_pncp_extras`. |
| Flags semânticas | **0** flags agregadas (`audit_semantic_summary.json`). |
| Links oficiais | `links_oficiais` + documentos com tipos `sistema_origem` / `processo_eletronico` / `edital_pncp` quando presentes na API. |
| Duplicata de link | **Explicada** (falso positivo: URL raiz `https://pncp.gov.br` repetida no bruto; correção no crawler exige **nova coleta**). |
| API conservadora | Padrões `PNCP_*` + timeouts + pausa documentados no plano. |

## Notas (o “with_notes”)

1. **Duplicata de link**: resolvida no **transformer** (canonização de `https://pncp.gov.br` → `/app/editais/{codigo_oportunidade}` quando o controle existe nos extras). O crawler também ignora a URL raiz em novas coletas.
2. **Validação**: vários itens `incompletos` e **1** `suspeito` (itens com `opportunity_gate_relaxed`) — revisão humana antes de qualquer `loader apply`.
3. **`pdf_url`**: ausência continua aceitável; não é critério de bloqueio para PNCP nesta política.

## Rejeição residual (análise)

- **Antes:** um item com link em `portaldecompraspublicas.com.br` era barrado por relevância porque `_pncp_soft_continue` exigia `pncp.gov.br` no link.
- **Depois:** relaxamento local permite **portal externo** quando há `codigo_oportunidade` / `numero_controle_pncp` / `numero_edital` nos extras e sinais de contratação no texto — mantendo bloqueio ao índice genérico `.../app/editais` sem controle.

## Duplicata de link (análise)

- **Tipo:** falso positivo operacional (mesma URL raiz, controles PNCP distintos).
- **Correção:** link canonizado cedo no `_transform_item_with_result` para fonte `pncp`; **hash** inclui `codigo_oportunidade` + processo para distinguir itens com texto parecido.

## Decisão final

- **Manter PNCP `blocked` no gate global** até revisão manual e nova coleta opcional.
- **Tecnicamente:** classificar como **`ready_with_notes`** — pronto para revisão humana e para eventual carga futura, com as ressalvas acima.

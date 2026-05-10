# Recovery B.1 — diagnóstico AMAZUL

- **Post-daily:** `audit_reports_main_pipeline\post_daily_warning_examples.json` (2026-05-10T05:51:55Z)

## Contagens AMAZUL (`summary_by_warning`)

| Warning | AMAZUL (count) |
|---------|---------------:|
| `suspeito_ativo_true` | 12 |
| `prazo_vencido_ativo_true` | 7 |
| `credito_tipo_recurso_incoerente` | 2 |

## Itens (exemplos filtrados)

### `suspeito_ativo_true`

- **id 425** — chamada_editais_reais: Dispensa de Licitação por Valor 02/2025
  - Link: `https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-022025`
  - Ação: Calibração local + validacao incompleto (Recovery B.1); não desativar sem curadoria.
- **id 426** — chamada_editais_reais: Dispensa de Licitação por Valor 03/2025
  - Link: `https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-032025`
  - Ação: Calibração local + validacao incompleto (Recovery B.1); não desativar sem curadoria.
- **id 429** — chamada_editais_reais: Dispensa de Licitação por Valor 06/2025
  - Link: `https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-062025`
  - Ação: Calibração local + validacao incompleto (Recovery B.1); não desativar sem curadoria.
- **id 430** — chamada_editais_reais: Dispensa de Licitação por Valor 07/2025
  - Link: `https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-072025`
  - Ação: Calibração local + validacao incompleto (Recovery B.1); não desativar sem curadoria.

### `prazo_vencido_ativo_true`

- **id 425** — oportunidade_vencida: Dispensa de Licitação por Valor 02/2025
  - Link: `https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-022025`
  - Ação: Documentar prazo vencido; política de arquivo ou ativo=false em passo futuro (sem inventar datas).
- **id 430** — oportunidade_vencida: Dispensa de Licitação por Valor 07/2025
  - Link: `https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-072025`
  - Ação: Documentar prazo vencido; política de arquivo ou ativo=false em passo futuro (sem inventar datas).

### `credito_tipo_recurso_incoerente`

- **id 2102** — chamada_editais_reais: Dispensa de Licitação 03/2024
  - Link: `https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-032024`
  - Ação: Marcar reembolsavel=false para compra pública AMAZUL no transformer; texto com 'crédito' no objeto ≠ linha de crédito bancário.
- **id 436** — chamada_editais_reais: Dispensa de Licitação por Valor 04/2023
  - Link: `https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos/dispensa-de-licitacao-por-valor-042023`
  - Ação: Marcar reembolsavel=false para compra pública AMAZUL no transformer; texto com 'crédito' no objeto ≠ linha de crédito bancário.

## Pipeline local Recovery B.1 (pós-ajuste CORE)

- **Retransform:** `audit_reports_main_pipeline/recovery_b1_amazul/standardized/amazul_standardized.json` (20 itens)
- **Sem `validacao_status=suspeito`** no standardized gerado; **`reembolsavel=false`** nas licitações calibradas
- **Loader dry-run:** ver `recovery_b1_amazul_loader_dryrun.json` / pasta `recovery_b1_amazul_loader_dryrun/`

Detalhe JSON: `recovery_b1_amazul_diagnostico.json`.
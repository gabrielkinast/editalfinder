# Caso Residual PNCP Defesa

- **Fonte:** `pncp_defesa`
- **Título:** `AQUISIÇÃO DE MOVEIS SOB MEDIDA E MATERIAL DE INFORMATICA`
- **Link:** `https://pregaobanrisul.com.br/editais/0021_2025/334656`
- **Motivo na auditoria original:** `Relevancia limite: poucos sinais de oportunidade`

## Evidências coletadas

- O item bruto tem sinais claros de contratação pública: `Pregão - Eletrônico`, `numero_edital`, `numero_processo`, prazo e valor.
- Avaliação do gate no item bruto: `keep=False`, `intent=generic_page`, `score=3`.
- Sinais detectados pelo gate: `pdf_or_docs`, `numero_edital`, `title_ok`, `short_desc`.
- Documento/anexo bruto presente: `Sistema de origem` com URL do próprio edital.

## Classificação manual (heurística)

- `oportunidade_real`: sim
- `licitacao`: sim
- `compra_publica`: sim
- `contrato_publico`: sim
- `pagina_generica`: não
- `ruido`: não
- `duvidoso`: não

## Julgamento do motivo de rejeição

Para este caso específico, `Relevancia limite` é **inadequado**.  
O item representa compra pública real (não é ruído/menu/notícia).

## Decisão recomendada

- Status recomendado: `suspeito` (não descarte duro).
- `pdf_url`: vazio (correto, pois não há PDF explícito).
- `extras.documentos`: preservar link de origem.

## Ajuste local aplicado (sem alterar gate global)

- Escopo: `transformer` apenas para `pncp_defesa` e `compras_defesa`.
- Regra: em rejeição por relevância/pontuação, permitir continuação quando houver:
  - marcador de compra pública (`pregão`, `licitação`, `aquisição`, `contratação`, etc.),
  - e metadado oficial (`numero_edital`/`numero_processo`/`numero_controle_pncp`) ou valor/prazo.
- Segurança: não altera `opportunity_gate` global.

## Validação pós-ajuste local

- Auditoria dirigida: `audit_reports_docs_pncp_check`
- Resultado: `perdas_total = 0`
- Arquivo de perdas: vazio (`audit_docs_losses.json`).

Detalhe estruturado no JSON: `audit_reports_docs/PNCP_DEFESA_caso_residual.json`.

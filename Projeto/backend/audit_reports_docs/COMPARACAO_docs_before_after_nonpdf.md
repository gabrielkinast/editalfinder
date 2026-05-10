# Comparação auditoria de documentos

- Antes: `audit_reports_docs\audit_docs_summary_before_nonpdf.json`
- Depois: `audit_reports_docs\audit_docs_summary.json`

| Métrica | Antes | Depois | Delta |
|---|---:|---:|---:|
| itens_analisados | 111 | 111 | 0 |
| raw_com_documentos | 67 | 67 | 0 |
| transformado_com_documentos | 52 | 67 | 15 |
| payload_com_documentos | 52 | 67 | 15 |
| bruto_com_documentos_pdf | 0 | 52 | 52 |
| bruto_com_documentos_nao_pdf | 0 | 21 | 21 |
| transformado_com_documentos_pdf | 0 | 52 | 52 |
| transformado_com_documentos_nao_pdf | 0 | 21 | 21 |
| payload_com_documentos_pdf | 0 | 52 | 52 |
| payload_com_documentos_nao_pdf | 0 | 21 | 21 |
| perdas_pdf | 0 | 0 | 0 |
| perdas_nao_pdf | 0 | 0 | 0 |
| perdas_total | 16 | 1 | -15 |
| downloads_falharam | 9 | 9 | 0 |

## Formatos detectados (depois)

- pdf: 0 -> 139 (delta 139)
- xlsx: 0 -> 20 (delta 20)
- outro: 0 -> 14 (delta 14)
- docx: 0 -> 8 (delta 8)
- doc: 0 -> 3 (delta 3)
- zip: 0 -> 1 (delta 1)
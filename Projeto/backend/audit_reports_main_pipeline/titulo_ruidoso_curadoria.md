# Curadoria rápida - titulo_ruidoso

Fonte: `audit_reports_main_pipeline/post_daily_warning_examples.json`

Política: itens com título claramente institucional, FAQ, contato ou conta bancária não são oportunidades acionáveis para `public.edital`. A ação recomendada é desativar em staging com `ativo=false`, nunca deletar.

## Decisões

| Fonte | Título | Link | Decisão | Motivo |
|---|---|---|---|---|
| BASA | Conta PJ | https://www.bancoamazonia.com.br/empresas/conta-pj | desativar | Página de produto bancário/conta, não edital/chamada/oportunidade acionável. |
| BDMG | Entre em contato | https://www.bdmg.mg.gov.br/investimento | desativar | Página genérica de contato/investimento, sem chamada ou submissão específica. |
| General Dynamics Suppliers | Supplier FAQs | https://www.gd.com/suppliers/supplier-faqs | desativar | FAQ de fornecedor; material informativo, não oportunidade acionável. |
| KAKENHI | 科研費FAQ | https://www.jsps.go.jp/j-grantsinaid/01_seido/05_faq/index.html | desativar | FAQ institucional do programa; não é chamada específica. |
| NATO DIANA | NATO DIANA — Programme FAQ (challenges, eligibility, portal) | https://www.diana.nato.int/faq.html | desativar | FAQ do programa; útil como referência, mas não deve ficar como edital ativo. |
| NUCLEP | Quem Somos | https://www.nuclep.gov.br/quem-somos | desativar | Página institucional, não licitação/chamada. |

## Resultado

- Itens revisados: 6
- Aprovados para desativação: 6
- Mantidos: 0
- Input específico: `audit_reports_main_pipeline/titulo_ruidoso_deactivation_input.json`

Nenhum apply foi executado nesta curadoria.

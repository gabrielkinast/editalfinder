# Curadoria titulo_ruidoso: candidatos para desativação segura

- Gerado: `2026-05-09T00:00:00Z`
- Fonte: `audit_reports_main_pipeline/post_daily_warning_examples.json`
- Tabela: `public.edital`
- Ação recomendada: `ativo=false`
- Apply executado: **não**
- Supabase tocado: **não**
- DELETE/TRUNCATE/DROP: **não**

Arquivo JSON compatível com `scripts/deactivate_removed_items.py`:

`audit_reports_main_pipeline/titulo_ruidoso_deactivate_candidates.json`

## Candidatos

| Fonte | Título | Link | Motivo | Confiança |
|---|---|---|---|---|
| BASA | Conta PJ | https://www.bancoamazonia.com.br/empresas/conta-pj | Página de produto bancário/conta, não é oportunidade acionável. | high |
| BDMG | Entre em contato | https://www.bdmg.mg.gov.br/investimento | Página genérica de contato/investimento, sem chamada específica. | high |
| General Dynamics Suppliers | Supplier FAQs | https://www.gd.com/suppliers/supplier-faqs | FAQ de fornecedor, não é oportunidade acionável. | high |
| KAKENHI | 科研費FAQ | https://www.jsps.go.jp/j-grantsinaid/01_seido/05_faq/index.html | FAQ institucional do programa, não é chamada específica. | high |
| NATO DIANA | NATO DIANA — Programme FAQ (challenges, eligibility, portal) | https://www.diana.nato.int/faq.html | FAQ do programa, não é edital/chamada ativa. | high |
| NUCLEP | Quem Somos | https://www.nuclep.gov.br/quem-somos | Página institucional, não é licitação/chamada. | high |

## Uso seguro posterior

Dry-run:

```powershell
python scripts/deactivate_removed_items.py --input audit_reports_main_pipeline/titulo_ruidoso_deactivate_candidates.json --table edital --confidence high
```

Apply posterior, somente se autorizado explicitamente:

```powershell
$env:EDITALFINDER_ENV="staging"
$env:EDITALFINDER_ALLOW_STAGING_APPLY="true"
$env:ALLOW_DEACTIVATE_REMOVED_ITEMS="1"
python scripts/deactivate_removed_items.py --input audit_reports_main_pipeline/titulo_ruidoso_deactivate_candidates.json --table edital --confidence high --staging --apply --reason "Curadoria titulo_ruidoso"
```

O apply seguro marca `ativo=false` e preserva os dados para auditoria.

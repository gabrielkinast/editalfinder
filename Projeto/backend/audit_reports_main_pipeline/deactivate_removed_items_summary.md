# Desativação segura de resíduos

- Gerado: `2026-05-09T13:38:47Z`
- Modo: **apply**
- Ambiente: `staging`
- Candidatos lidos: **6**
- Candidatos filtrados: **6**
- Alterados: **6**
- Não encontrados: **0**
- Erros: **0**

Nenhum DELETE/TRUNCATE/DROP é usado. O apply, quando permitido, marca `ativo=false`.

## Exemplos dry-run

- `edital` `BASA` `high`: https://www.bancoamazonia.com.br/empresas/conta-pj
- `edital` `BDMG` `high`: https://www.bdmg.mg.gov.br/investimento
- `edital` `General Dynamics Suppliers` `high`: https://www.gd.com/suppliers/supplier-faqs
- `edital` `KAKENHI` `high`: https://www.jsps.go.jp/j-grantsinaid/01_seido/05_faq/index.html
- `edital` `NATO DIANA` `high`: https://www.diana.nato.int/faq.html
- `edital` `NUCLEP` `high`: https://www.nuclep.gov.br/quem-somos
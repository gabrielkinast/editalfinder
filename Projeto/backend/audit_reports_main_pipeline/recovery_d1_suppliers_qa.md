# Recovery D.1 — QA Supplier Portals

Leituras de contexto prévias (Recovery D): `recovery_d_suppliers_context.json`, `recovery_d_suppliers_loader_dryrun.json`, `recovery_d_suppliers_apply_recommendation.json`, `recovery_d_suppliers_deactivate_candidates.json`, e standardized Recovery D (~28 itens antes do recorte D.1).

Recovery D.1: URLs Lockheed Martin fora do path /suppliers foram recusadas; em gdls.com mantêm-se apenas /suppliers/* e PDFs em /wp-content/; gd.com apenas /suppliers/*.

**Baseline Recovery D (~28 standardized)** vs **Recovery D.1 atual: 26** — ver `comparativo_recovery_d_linha_anterior` no JSON.

**Itens nesta tabela:** 26

## Verificação automática

```json
{
  "itens_total": 26,
  "faq_help_support_url_heuristic": 0,
  "login_isolado_warnings": 0,
  "validacao_suspeito_top_level": 0,
  "setor_estrategico_gt3": 0,
  "titulo_generico_suppliers_sem_normalizacao": 0,
  "capabilities_na_colecao": 0,
  "gdls_lav_na_colecao": 0,
  "criterios_apply": {
    "sem_faq_help": true,
    "sem_login_isolado_forte": true,
    "sem_capabilities_fantasma": true,
    "sem_lav_produto": true,
    "suspeito_zero_ou_explicado": true,
    "mapping_loader_zero": true
  }
}
```

| # | Fonte | Título | tipo_op | validação | Decisão QA | Motivo | Ação recomendada |
|---:|---|---|---|---|---|---|---|
| 1 | `bae_systems_suppliers` | New supplier registration (HICX) | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Self-registration HICX com contexto público mínimo. | Manter tipo_recurso oportunidade_fornecedor; validação incompleto; portal credential. |
| 2 | `bae_systems_suppliers` | Responsible supply chain \| BAE Systems UK suppliers | `oportunidade_fornecedor` | `acesso_limitado` | `acesso_limitado_institucional` | Página institucional supply chain / stub WAF. | acesso_limitado; uso informativo, não cadastro direto aqui. |
| 3 | `general_dynamics_suppliers` | Mentor-Protégé Program | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Programa Mentor-Protégé com texto operacional público. | Manter oportunidade_fornecedor; incompleto até haver objeto/prazo estruturado. |
| 4 | `general_dynamics_suppliers` | General Dynamics Land Systems — Suppliers (hub) | `programa_agregado` | `incompleto` | `hub_programa_agregado` | Hub oficial de fornecedores com múltiplos recursos; não é formulário único. | Manter programa_agregado + incompleto; badge supplier hub no frontend. |
| 5 | `general_dynamics_suppliers` | CYBERSECURITY | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Secções supplier GDLS/GD com requisitos (quality, cybersecurity, trade). | incompleto; manter índice navegável. |
| 6 | `general_dynamics_suppliers` | iSUPPLIER | `oportunidade_fornecedor` | `acesso_limitado` | `manter_oportunidade_fornecedor` | Portal Oracle / onboarding com camada autenticada. | validacao_status=acesso_limitado; não promover como edital aberto. |
| 7 | `general_dynamics_suppliers` | QUALITY | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Secções supplier GDLS/GD com requisitos (quality, cybersecurity, trade). | incompleto; manter índice navegável. |
| 8 | `general_dynamics_suppliers` | TRANSPORTATION AND TRADE COMPLIANCE | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Secções supplier GDLS/GD com requisitos (quality, cybersecurity, trade). | incompleto; manter índice navegável. |
| 9 | `lockheed_martin_suppliers` | Lockheed Martin — Supplier portal (hub) | `programa_agregado` | `incompleto` | `hub_programa_agregado` | Hub oficial de fornecedores com múltiplos recursos; não é formulário único. | Manter programa_agregado + incompleto; badge supplier hub no frontend. |
| 10 | `lockheed_martin_suppliers` | Doing Business | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 11 | `lockheed_martin_suppliers` | Business Area Procurement | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 12 | `lockheed_martin_suppliers` | Small Business Innovation Research | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 13 | `lockheed_martin_suppliers` | Cybersecurity | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 14 | `lockheed_martin_suppliers` | Supplier Ethics | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 15 | `lockheed_martin_suppliers` | Small Business Programs | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 16 | `lockheed_martin_suppliers` | Sustainable Supply Chain Management | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 17 | `lockheed_martin_suppliers` | Supplier Documentation | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 18 | `lockheed_martin_suppliers` | Webinars & Programs | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 19 | `lockheed_martin_suppliers` | Supplier News and Events | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 20 | `lockheed_martin_suppliers` | LM eInvoicing 2026 Training | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 21 | `lockheed_martin_suppliers` | Maintaining Cybersecurity Maturity Model Certification | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 22 | `lockheed_martin_suppliers` | Shared Commitment to Equal Employment Opportunity | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 23 | `lockheed_martin_suppliers` | Power Of A Shared Focus | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 24 | `lockheed_martin_suppliers` | Document CMMC status in Exostar | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 25 | `lockheed_martin_suppliers` | Discontinuation of Phone-Based OTP for Supplier Access | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |
| 26 | `lockheed_martin_suppliers` | Upcoming CMMC Requirements | `oportunidade_fornecedor` | `incompleto` | `manter_oportunidade_fornecedor` | Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias). | incompleto; não destacar como licitação; útil como referência fornecedor. |

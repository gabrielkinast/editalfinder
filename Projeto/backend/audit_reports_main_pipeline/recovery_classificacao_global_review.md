# Review — Recovery global de classificação de setores (pré-apply staging)

- **Gerado (UTC):** 2026-05-13T01:21:51.998340+00:00
- **Referência dry-run:** `audit_reports_main_pipeline/recovery_classificacao_global_dryrun.json`

## Legenda A/B/C/D

- **A:** Correção segura — perda de DI/aero/cyber em setor sem evidência militar (heurística) ou mudança coerente sem esvaziamento.
- **B:** Correção provável — precisa review manual (tipicamente tinha setor(s) e ficou vazio).
- **C:** Regressão provável — evidência militar no texto e perda de slugs defense-like (ex.: Grants.gov misto, EDF).
- **D:** Política de lock por ficheiro — todas as linhas de IARPA / DARPA Opportunities (e darpa_news se existir); não aplicar overwrite global sem `setor_estrategico_crawler_locked`.

## Métricas (staging, estimativa)

- **itens_aplicacao_segura_estimados_categoria_A:** 310
- **itens_revisao_manual_prioritaria_categoria_B:** 633
- **itens_regressao_provavel_categoria_C:** 148
- **itens_fonte_lock_categoria_D:** 23
- **linhas_tot_em_ficheiros_lock_D:** 23
- **itens_mudam_em_ficheiros_lock:** 23
- **itens_inalterados:** 180
- **total_ficariam_sem_setor_estrategico:** 920
- **total_tinham_slugs_e_ficam_vazios:** 790
- **nota:** D = todas as linhas dos ficheiros IARPA/DARPA listados (política de lock). Outras linhas: unchanged > C > B > A. Apply global seguro ~ categoria A fora de ficheiros lock; B+C exigem wave com QA ou calibração antes do apply.

## Recomendação final (resumo executivo)

Adoptar **Opção B** com primeiro wave limitado a ficheiros de baixo `pct_had_to_empty`. Manter **IARPA** e **DARPA Opportunities** (e `darpa_news` se existir) com `setor_estrategico_crawler_locked` até extensão EN da taxonomia ou `calibrate_*` dedicado. Rever **categoria B** (tinha setor → vazio) antes de apply em massa. **Opção A** só após fecho de B em fontes críticas. **Opção C** como complemento cirúrgico a Opção B.

## Estratégias de apply

### opcao_A_global_exceto_lock
Aplicar overwrite taxonómico globalmente excepto ficheiros em `aplicar_com_setor_estrategico_crawler_locked` e `excluir_apply_global_por_enquanto`; adiar linhas categoria B para wave com QA ou manter merge antigo só nessas PKs.

### opcao_B_lotes
- 1) Lote 'genérico seguro': ficheiros em apply_normal com pct_had_to_empty < 0.25.
- 2) Lote 'Brasil': demais apply_normal BR (FAP*, CNPq, ANEEL, BNDES, …).
- 3) Lote 'internacional CTI': apply_normal restante com EN leve ou já calibrado.
- 4) Lote 'defesa': DoD/NUCLEP apply normal com spot-check; IARPA/DARPA só com lock ou pós-calibração EN.

### opcao_C_so_limpeza_nao_militar
UPDATE/loader só remove defesa_industrial/aeroespacial de setor_estrategico quando arquivo fonte ∉ conjunto militar e texto normalizado não contém MILITARY_MARKERS; não altera linhas que ficariam totalmente vazias (deixa para wave B).

## Fontes por política

### aplicar_recovery_normalmente (53)
- `afwerx_standardized.json`
- `amazul_standardized.json`
- `ambev_standardized.json`
- `aneel_standardized.json`
- `anp_standardized.json`
- `apex_standardized.json`
- `badesul_standardized.json`
- `caixa_standardized.json`
- `capes_standardized.json`
- `cbpf_standardized.json`
- `china_caea_standardized.json`
- `china_cgn_standardized.json`
- `china_mod_public_standardized.json`
- `china_tendering_bidding_standardized.json`
- `china_university_procurement_standardized.json`
- `cnen_standardized.json`
- `compras_defesa_standardized.json`
- `confap_standardized.json`
- `defesa_standardized.json`
- `diu_standardized.json`
- `dod_sbir_sttr_standardized.json`
- `doe_arpae_standardized.json`
- `eletronuclear_standardized.json`
- `embrapii_standardized.json`
- `erc_standardized.json`
- `fapemig_standardized.json`
- `faperg_standardized.json`
- `fapergs_standardized.json`
- `fapesc_standardized.json`
- `fnde_standardized.json`
- `horizon_europe_standardized.json`
- `impa_standardized.json`
- `ipen_standardized.json`
- `japan_aist_standardized.json`
- `japan_ihi_standardized.json`
- `japan_jaea_standardized.json`
- `japan_jetro_procurement_standardized.json`
- `japan_mext_standardized.json`
- `japan_mitsubishi_heavy_standardized.json`
- `japan_mod_standardized.json`
- `japan_qst_standardized.json`
- `mapa_standardized.json`
- `mcti_standardized.json`
- `mma_standardized.json`
- `nsf_standardized.json`
- `nuclep_standardized.json`
- `petrobras_standardized.json`
- `plataforma_industria_standardized.json`
- `pncp_defesa_standardized.json`
- `saude_standardized.json`
- `senai_standardized.json`
- `softex_standardized.json`
- `wellcome_standardized.json`

### aplicar_com_setor_estrategico_crawler_locked (2)
- `darpa_opportunities_standardized.json`
- `iarpa_standardized.json`

### aplicar_so_depois_calibracao_en (26)
- `banco_da_amazonia_standardized.json`
- `bdmg_standardized.json`
- `bnb_standardized.json`
- `bndes_standardized.json`
- `china_cas_standardized.json`
- `china_mofcom_tendering_standardized.json`
- `china_most_standardized.json`
- `china_nsfc_standardized.json`
- `cnpq_standardized.json`
- `eic_standardized.json`
- `eit_standardized.json`
- `esa_osip_standardized.json`
- `eureka_network_standardized.json`
- `european_defence_fund_standardized.json`
- `fappr_standardized.json`
- `grants_gov_standardized.json`
- `japan_atla_standardized.json`
- `japan_jsps_standardized.json`
- `japan_kakenhi_standardized.json`
- `japan_kek_standardized.json`
- `japan_nedo_standardized.json`
- `japan_nims_standardized.json`
- `japan_riken_standardized.json`
- `lockheed_martin_suppliers_standardized.json`
- `pncp_standardized.json`
- `ukri_funding_standardized.json`

### excluir_apply_global_por_enquanto (5)
- `bae_systems_suppliers_standardized.json`
- `general_dynamics_suppliers_standardized.json`
- `nato_diana_standardized.json`
- `rheinmetall_suppliers_standardized.json`
- `thales_suppliers_standardized.json`

## Amostras por categoria

### Categoria A
- **AFWERX** (`afwerx_standardized.json`) — SBIR/STTR Overview
  - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `['defesa']`
- **AFWERX** (`afwerx_standardized.json`) — Open Topic
  - antes: `['defesa_industrial', 'aeroespacial', 'defesa', 'dual_use']` → depois: `['defesa', 'dual_use']`
- **AFWERX** (`afwerx_standardized.json`) — Specific Topic
  - antes: `['defesa_industrial', 'aeroespacial', 'defesa', 'dual_use']` → depois: `['defesa', 'dual_use']`
- **AFWERX** (`afwerx_standardized.json`) — STRATFI/TACFI
  - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `['defesa']`
- **AFWERX** (`afwerx_standardized.json`) — Phase III
  - antes: `['defesa_industrial', 'defesa']` → depois: `['defesa']`
- **AFWERX** (`afwerx_standardized.json`) — Risk-Based Analysis
  - antes: `['defesa_industrial', 'defesa']` → depois: `['defesa']`
- **AFWERX** (`afwerx_standardized.json`) — Augmentee Program
  - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `['defesa']`
- **AFWERX** (`afwerx_standardized.json`) — SAGE Fellowship Program
  - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `['defesa']`
- **AMAZUL** (`amazul_standardized.json`) — Dispensa de Licitação 05/2024
  - antes: `['nuclear', 'defesa']` → depois: `['defesa', 'nuclear', 'aeroespacial']`
- **ANEEL** (`aneel_standardized.json`) — Sistemas de Armazenamento de Energia
  - antes: `['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia', 'energia']` → depois: `['ciencia_tecnologia', 'energia']`
- **ANEEL** (`aneel_standardized.json`) — Chamadas de Projetos de PDI Estratégicos
  - antes: `['defesa_industrial', 'aeroespacial', 'energia']` → depois: `['energia']`
- **ANEEL** (`aneel_standardized.json`) — Guia de Avaliação da Maturidade Tecnológica da ANEEL
  - antes: `['defesa_industrial', 'ciencia_tecnologia']` → depois: `['aeroespacial', 'ciencia_tecnologia']`

### Categoria B
- **ANEEL** (`aneel_standardized.json`) — ANEEL - adsp2024778 2
  - antes: `['defesa_industrial']` → depois: `[]`
- **ANEEL** (`aneel_standardized.json`) — ANEEL - Call for Projects H2 PDI
  - antes: `['defesa_industrial']` → depois: `[]`
- **ANEEL** (`aneel_standardized.json`) — PDI ANEEL
  - antes: `['defesa_industrial']` → depois: `[]`
- **ANEEL** (`aneel_standardized.json`) — Sandboxes Tarifários
  - antes: `['defesa_industrial']` → depois: `[]`
- **ANEEL** (`aneel_standardized.json`) — Planejamento de Tecnologia da Informação
  - antes: `['defesa_industrial', 'aeroespacial']` → depois: `[]`
- **ANEEL** (`aneel_standardized.json`) — Plano de Desenvolvimento da Distribuição
  - antes: `['defesa_industrial']` → depois: `[]`
- **ANEEL** (`aneel_standardized.json`) — Programa de Pesquisa, Desenvolvimento e Inovação da ANEEL
  - antes: `['defesa_industrial']` → depois: `[]`
- **ANEEL** (`aneel_standardized.json`) — PDI ANEEL
  - antes: `['defesa_industrial']` → depois: `[]`
- **ANEEL** (`aneel_standardized.json`) — PDI ANEEL
  - antes: `['defesa_industrial']` → depois: `[]`
- **ANEEL** (`aneel_standardized.json`) — Desenvolvimento, cuidados e educação pré-escolar
  - antes: `['defesa_industrial']` → depois: `[]`
- **ANP** (`anp_standardized.json`) — Consultas e Audiências Públicas
  - antes: `['defesa_industrial']` → depois: `[]`
- **Apex Brasil** (`apex_standardized.json`) — licitações e contratos
  - antes: `['aeroespacial']` → depois: `[]`

### Categoria C
- **ERC** (`erc_standardized.json`) — Starting Grant
  - antes: `['aeroespacial']` → depois: `[]`
- **ERC** (`erc_standardized.json`) — Consolidator Grant
  - antes: `['aeroespacial']` → depois: `[]`
- **European Defence Fund** (`european_defence_fund_standardized.json`) — esespañol
  - antes: `['defesa_industrial']` → depois: `[]`
- **European Defence Fund** (`european_defence_fund_standardized.json`) — csčeština
  - antes: `['defesa_industrial']` → depois: `[]`
- **European Defence Fund** (`european_defence_fund_standardized.json`) — dadansk
  - antes: `['defesa_industrial']` → depois: `[]`
- **European Defence Fund** (`european_defence_fund_standardized.json`) — deDeutsch
  - antes: `['defesa_industrial']` → depois: `[]`
- **European Defence Fund** (`european_defence_fund_standardized.json`) — eteesti
  - antes: `['defesa_industrial']` → depois: `[]`
- **European Defence Fund** (`european_defence_fund_standardized.json`) — frfrançais
  - antes: `['defesa_industrial']` → depois: `[]`
- **European Defence Fund** (`european_defence_fund_standardized.json`) — ititaliano
  - antes: `['defesa_industrial', 'aeroespacial']` → depois: `[]`
- **European Defence Fund** (`european_defence_fund_standardized.json`) — lvlatviešu
  - antes: `['defesa_industrial']` → depois: `[]`
- **European Defence Fund** (`european_defence_fund_standardized.json`) — ltlietuvių
  - antes: `['defesa_industrial']` → depois: `[]`
- **European Defence Fund** (`european_defence_fund_standardized.json`) — humagyar
  - antes: `['defesa_industrial']` → depois: `[]`

### Categoria D
- **DARPA Opportunities** (`darpa_opportunities_standardized.json`) — R&D Opportunities
  - antes: `['defesa_industrial']` → depois: `[]`
- **DARPA Opportunities** (`darpa_opportunities_standardized.json`) — Offices
  - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `[]`
- **DARPA Opportunities** (`darpa_opportunities_standardized.json`) — Contracts Management Office
  - antes: `['defesa_industrial', 'aeroespacial']` → depois: `[]`
- **DARPA Opportunities** (`darpa_opportunities_standardized.json`) — Academia
  - antes: `['defesa_industrial']` → depois: `[]`
- **DARPA Opportunities** (`darpa_opportunities_standardized.json`) — Industry
  - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `[]`
- **DARPA Opportunities** (`darpa_opportunities_standardized.json`) — Small Business
  - antes: `['defesa_industrial', 'aeroespacial']` → depois: `[]`
- **DARPA Opportunities** (`darpa_opportunities_standardized.json`) — Ideas Under Incubation
  - antes: `['defesa_industrial', 'aeroespacial']` → depois: `[]`
- **DARPA Opportunities** (`darpa_opportunities_standardized.json`) — About DARPA
  - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `[]`
- **DARPA Opportunities** (`darpa_opportunities_standardized.json`) — Defense Sciences Office
  - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `[]`
- **DARPA Opportunities** (`darpa_opportunities_standardized.json`) — Microsystems Technology Office
  - antes: `['defesa_industrial', 'aeroespacial', 'defesa', 'dual_use']` → depois: `['dual_use']`
- **DARPA Opportunities** (`darpa_opportunities_standardized.json`) — Usage Policy
  - antes: `['defesa_industrial']` → depois: `[]`
- **DARPA Opportunities** (`darpa_opportunities_standardized.json`) — R&D Opportunities
  - antes: `['defesa_industrial']` → depois: `[]`

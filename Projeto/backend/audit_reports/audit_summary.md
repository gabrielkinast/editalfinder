# Resumo da auditoria (dry-run)

- Ficheiros processados: **95**
- Itens analisados (amostra): **961** (máx. 25 por ficheiro)
- Fontes com dados na amostra: **88**
- PDFs na auditoria: **desativados (skip)**

## Matriz (resumo)

| Crawler | Categoria | Status | Qualidade | Ruído |
|---------|-----------|--------|-----------|-------|
| abdi|abdi_editais.json | industria | maduro | alta | baixo |
| afwerx|afwerx_editais.json | outros | bom | alta | baixo |
| amazul|amazul_editais.json | defesa | quebrado | n/d | baixo |
| ambev|ambev_editais.json | outros | quebrado | n/d | baixo |
| aneel|aneel_editais.json | energia | quebrado | alta | baixo |
| anp|anp_editais.json | energia | quebrado | n/d | baixo |
| apex|apex_editais.json | industria | ruidoso | n/d | alto |
| badesul|badesul_editais.json | credito | quebrado | n/d | baixo |
| bae_systems_suppliers|bae_systems_suppliers_editais.json | outros | não testado | n/d | baixo |
| bndes|bndes_editais.json | credito | quebrado | n/d | baixo |
| brde|brde_editais.json | credito | quebrado | n/d | baixo |
| caixa|caixa_editais.json | credito | quebrado | n/d | baixo |
| capes|capes_editais.json | fomento | quebrado | n/d | baixo |
| cbpf|cbpf_editais.json | ciencia | quebrado | n/d | baixo |
| china_avic|china_avic_editais.json | outros | quebrado | n/d | baixo |
| china_caea|china_caea_editais.json | outros | maduro | alta | baixo |
| china_cas|china_cas_editais.json | outros | maduro | alta | baixo |
| china_cgn|china_cgn_editais.json | outros | bom | alta | baixo |
| china_cnnc|china_cnnc_editais.json | outros | quebrado | n/d | baixo |
| china_mod_public|china_mod_public_editais.json | outros | bom | alta | baixo |
| china_mofcom_tendering|china_mofcom_tendering_editais.json | internacional | parcial | alta | baixo |
| china_most|china_most_editais.json | outros | bom | alta | baixo |
| china_norinco|china_norinco_editais.json | outros | quebrado | n/d | baixo |
| china_nsfc|china_nsfc_editais.json | internacional | não testado | n/d | baixo |
| china_tendering_bidding|china_tendering_bidding_editais.json | internacional | maduro | alta | baixo |
| china_university_procurement|china_university_procurement_editais.json | internacional | parcial | alta | baixo |
| cnen|cnen_editais.json | ciencia | quebrado | n/d | baixo |
| cnpq|cnpq_editais.json | fomento | quebrado | n/d | baixo |
| compras_defesa|compras_defesa_editais.json | defesa | quebrado | n/d | baixo |
| confap|confap_editais.json | fomento | quebrado | n/d | baixo |
| darpa_opportunities|darpa_opportunities_editais.json | outros | parcial | média | baixo |
| dcta_ita_iae|dcta_ita_iae_editais.json | defesa | quebrado | n/d | baixo |
| defesa|defesa_editais.json | defesa | fraco | alta | baixo |
| defesa|defesa_noticias_militares.json | defesa | quebrado | n/d | baixo |
| diu|diu_editais.json | outros | bom | alta | baixo |
| dod_sbir_sttr|dod_sbir_sttr_editais.json | outros | bom | alta | baixo |
| doe_arpae|doe_arpae_editais.json | outros | quebrado | n/d | baixo |
| eletronuclear|eletronuclear_editais.json | defesa | quebrado | n/d | baixo |
| embrapii|embrapii_editais.json | industria | quebrado | n/d | baixo |
| erc|erc_editais.json | outros | quebrado | n/d | baixo |
| … | … | *+55 linhas em audit_matrix_crawlers.json* | … | … |

## Ruído que passou o transformer
Total registos: **0** (ver `audit_noise_examples.json`).

## Top correções sugeridas (automático)
1. Rever fontes classificadas como **ruidoso** ou **quebrado** em `audit_by_source.json`.
2. Reduzir campos vazios nas fontes no topo de `audit_empty_fields.json`.
3. Tratar perdas PDF/descrição em `audit_data_loss_examples.json`.
4. Afinar `tipo_recurso` para crédito (BNDES/BRDE/Caixa) com base nos exemplos de classificação.
5. Inferir `perfil_ideal` para fontes estratégicas listadas em `audit_profile_issues.json`.
6. Corrigir datas/prazo vs `situacao` nos casos de `audit_classification_issues.json` / datas.
7. Rever duplicados de link no mesmo JSON (`audit_duplicates.json`).
8. Planejar deprecação de score/relevância com base em `audit_score_legacy.json`.

Detalhe completo das 22 secções pedidas: consolidar a partir dos JSON em `audit_reports/` + este ficheiro.
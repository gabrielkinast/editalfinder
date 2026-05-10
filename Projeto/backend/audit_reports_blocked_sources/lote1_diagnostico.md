# Diagnóstico inicial — fontes bloqueadas (Lote 1)

## Resumo
- Fontes no lote: **9**
- Bloqueadas no config atual: **9**
- Itens brutos (total): **23**
- Itens transformados (total): **0**
- Itens rejeitados (total): **23**
- Fontes com output bruto: **9**
- Fontes com transformados > 0: **0**

## Diagnóstico por fonte

### badesul
- crawler roda: **True**
- output bruto existe: **True** (`badesul\outputs\badesul_editais.json`)
- bruto/transformados/rejeitados: **10/0/10**
- motivos de rejeição: `{'Relevancia limite: poucos sinais de oportunidade': 10}`
- classificação rejeitados: `{'oportunidade_real': 4, 'noticia': 0, 'pagina_generica': 0, 'erro_login_restrito': 0, 'documento_oficial': 0, 'licitacao_compra_publica': 0, 'linha_credito_fomento': 0, 'ruido_duvidoso': 6}`
- problema no crawler: **False**
- problema no transformer/gate: **True**
- problema em taxonomia: **False**
- problema docs/pdf: **False**
- problema links/URLs: **False**
- sem oportunidade real no momento: **False**
- recomendação técnica: Aplicar ajuste local por fonte com critérios objetivos e logs de relaxamento.
- recomendação de status: **ajuste_local_gate_transformer**

### petrobras
- crawler roda: **True**
- output bruto existe: **True** (`petrobras\outputs\petrobras_editais.json`)
- bruto/transformados/rejeitados: **5/0/5**
- motivos de rejeição: `{'Pontuacao abaixo do minimo (oportunidade nao evidenciada)': 5}`
- classificação rejeitados: `{'oportunidade_real': 0, 'noticia': 0, 'pagina_generica': 0, 'erro_login_restrito': 0, 'documento_oficial': 0, 'licitacao_compra_publica': 0, 'linha_credito_fomento': 0, 'ruido_duvidoso': 5}`
- problema no crawler: **True**
- problema no transformer/gate: **False**
- problema em taxonomia: **False**
- problema docs/pdf: **False**
- problema links/URLs: **True**
- sem oportunidade real no momento: **False**
- recomendação técnica: Rever extração do crawler (título/descrição/link detalhe) antes de mexer no gate.
- recomendação de status: **ajuste_local_crawler**

### senai
- crawler roda: **True**
- output bruto existe: **True** (`senai\outputs\senai_editais.json`)
- bruto/transformados/rejeitados: **1/0/1**
- motivos de rejeição: `{'Pontuacao abaixo do minimo (oportunidade nao evidenciada)': 1}`
- classificação rejeitados: `{'oportunidade_real': 1, 'noticia': 0, 'pagina_generica': 0, 'erro_login_restrito': 0, 'documento_oficial': 0, 'licitacao_compra_publica': 0, 'linha_credito_fomento': 0, 'ruido_duvidoso': 0}`
- problema no crawler: **False**
- problema no transformer/gate: **True**
- problema em taxonomia: **False**
- problema docs/pdf: **False**
- problema links/URLs: **False**
- sem oportunidade real no momento: **False**
- recomendação técnica: Aplicar ajuste local por fonte com critérios objetivos e logs de relaxamento.
- recomendação de status: **ajuste_local_gate_transformer**

### softex
- crawler roda: **True**
- output bruto existe: **True** (`softex\outputs\softex_editais.json`)
- bruto/transformados/rejeitados: **2/0/2**
- motivos de rejeição: `{'Pontuacao abaixo do minimo (oportunidade nao evidenciada)': 2}`
- classificação rejeitados: `{'oportunidade_real': 0, 'noticia': 0, 'pagina_generica': 0, 'erro_login_restrito': 0, 'documento_oficial': 0, 'licitacao_compra_publica': 0, 'linha_credito_fomento': 0, 'ruido_duvidoso': 2}`
- problema no crawler: **True**
- problema no transformer/gate: **False**
- problema em taxonomia: **False**
- problema docs/pdf: **False**
- problema links/URLs: **True**
- sem oportunidade real no momento: **False**
- recomendação técnica: Rever extração do crawler (título/descrição/link detalhe) antes de mexer no gate.
- recomendação de status: **ajuste_local_crawler**

### plataforma_industria
- crawler roda: **True**
- output bruto existe: **True** (`plataforma_industria\outputs\plataforma_editais.json`)
- bruto/transformados/rejeitados: **1/0/1**
- motivos de rejeição: `{'Pontuacao abaixo do minimo (oportunidade nao evidenciada)': 1}`
- classificação rejeitados: `{'oportunidade_real': 1, 'noticia': 0, 'pagina_generica': 0, 'erro_login_restrito': 0, 'documento_oficial': 0, 'licitacao_compra_publica': 0, 'linha_credito_fomento': 0, 'ruido_duvidoso': 0}`
- problema no crawler: **False**
- problema no transformer/gate: **True**
- problema em taxonomia: **False**
- problema docs/pdf: **False**
- problema links/URLs: **True**
- sem oportunidade real no momento: **False**
- recomendação técnica: Aplicar ajuste local por fonte com critérios objetivos e logs de relaxamento.
- recomendação de status: **ajuste_local_gate_transformer**

### pncp
- crawler roda: **True**
- output bruto existe: **True** (`pncp\outputs\pncp_editais.json`)
- bruto/transformados/rejeitados: **1/0/1**
- motivos de rejeição: `{'Pontuacao abaixo do minimo (oportunidade nao evidenciada)': 1}`
- classificação rejeitados: `{'oportunidade_real': 0, 'noticia': 0, 'pagina_generica': 0, 'erro_login_restrito': 0, 'documento_oficial': 0, 'licitacao_compra_publica': 0, 'linha_credito_fomento': 0, 'ruido_duvidoso': 1}`
- problema no crawler: **True**
- problema no transformer/gate: **False**
- problema em taxonomia: **False**
- problema docs/pdf: **False**
- problema links/URLs: **True**
- sem oportunidade real no momento: **False**
- recomendação técnica: Rever extração do crawler (título/descrição/link detalhe) antes de mexer no gate.
- recomendação de status: **ajuste_local_crawler**

### marinha
- crawler roda: **True**
- output bruto existe: **True** (`marinha\outputs\marinha_editais.json`)
- bruto/transformados/rejeitados: **1/0/1**
- motivos de rejeição: `{'Pontuacao abaixo do minimo (oportunidade nao evidenciada)': 1}`
- classificação rejeitados: `{'oportunidade_real': 0, 'noticia': 0, 'pagina_generica': 0, 'erro_login_restrito': 0, 'documento_oficial': 0, 'licitacao_compra_publica': 1, 'linha_credito_fomento': 0, 'ruido_duvidoso': 0}`
- problema no crawler: **False**
- problema no transformer/gate: **True**
- problema em taxonomia: **False**
- problema docs/pdf: **False**
- problema links/URLs: **False**
- sem oportunidade real no momento: **False**
- recomendação técnica: Aplicar ajuste local por fonte com critérios objetivos e logs de relaxamento.
- recomendação de status: **ajuste_local_gate_transformer**

### amazul
- crawler roda: **True**
- output bruto existe: **True** (`amazul\outputs\amazul_editais.json`)
- bruto/transformados/rejeitados: **1/0/1**
- motivos de rejeição: `{'Pontuacao abaixo do minimo (oportunidade nao evidenciada)': 1}`
- classificação rejeitados: `{'oportunidade_real': 0, 'noticia': 0, 'pagina_generica': 0, 'erro_login_restrito': 0, 'documento_oficial': 0, 'licitacao_compra_publica': 1, 'linha_credito_fomento': 0, 'ruido_duvidoso': 0}`
- problema no crawler: **False**
- problema no transformer/gate: **True**
- problema em taxonomia: **False**
- problema docs/pdf: **False**
- problema links/URLs: **False**
- sem oportunidade real no momento: **False**
- recomendação técnica: Aplicar ajuste local por fonte com critérios objetivos e logs de relaxamento.
- recomendação de status: **ajuste_local_gate_transformer**

### dcta_ita_iae
- crawler roda: **True**
- output bruto existe: **True** (`dcta_ita_iae\outputs\dcta_ita_iae_editais.json`)
- bruto/transformados/rejeitados: **1/0/1**
- motivos de rejeição: `{'Pontuacao abaixo do minimo (oportunidade nao evidenciada)': 1}`
- classificação rejeitados: `{'oportunidade_real': 0, 'noticia': 0, 'pagina_generica': 0, 'erro_login_restrito': 0, 'documento_oficial': 0, 'licitacao_compra_publica': 0, 'linha_credito_fomento': 0, 'ruido_duvidoso': 1}`
- problema no crawler: **True**
- problema no transformer/gate: **False**
- problema em taxonomia: **False**
- problema docs/pdf: **False**
- problema links/URLs: **True**
- sem oportunidade real no momento: **False**
- recomendação técnica: Rever extração do crawler (título/descrição/link detalhe) antes de mexer no gate.
- recomendação de status: **ajuste_local_crawler**
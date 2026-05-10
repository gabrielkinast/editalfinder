# Auditoria de duplicatas no banco

- Total registros analisados: **790**

## Quantidade por critério

- link: grupos=0, linhas_afetadas=0
- hash_deduplicacao: grupos=13, linhas_afetadas=34
- pdf_url: grupos=16, linhas_afetadas=105
- fonte_titulo_normalizado: grupos=21, linhas_afetadas=52
- codigo_oportunidade: grupos=0, linhas_afetadas=0
- numero_edital: grupos=0, linhas_afetadas=0
- numero_processo: grupos=0, linhas_afetadas=0
- fuzzy: grupos=84, linhas_afetadas=249

## Top fontes com duplicatas

- EMBRAPII: 80
- KEK: 66
- JETRO Government Procurement: 38
- AIST: 30
- DARPA Opportunities: 24
- NUCLEP: 20
- ANEEL: 17
- CAS: 16
- IPEN: 14
- MCTI: 13
- Mitsubishi Heavy Industries (Suppliers): 12
- FAPEMIG: 12
- FAPESC: 11
- Lockheed Martin Suppliers: 11
- ATLA: 10
- JSPS: 10
- IHI Corporation (Suppliers): 8
- MMA / FNMA: 6
- WELLCOME: 6
- Ministério da Defesa: 6

## Top duplicatas prováveis

- hash_deduplicacao | qtd=5 | canonico=230 | chave=174b50a8522ccffbba64123ca235d728fa9631ea4f2a784cc0cbab3e313ade41
- hash_deduplicacao | qtd=5 | canonico=568 | chave=d168ddd6a21486e96cbc6aed61532e9116a479fbae2ff4641a3a705629e2d151
- hash_deduplicacao | qtd=3 | canonico=29 | chave=3ee0f5535407cda6e29998e2c26d4c329152cae85bddbabf6d2de6c8e362f018
- hash_deduplicacao | qtd=3 | canonico=550 | chave=b67469c530031d06548b013ffc4222b1084960ccce350df4227d5dd783da7e38
- hash_deduplicacao | qtd=2 | canonico=92 | chave=969f5ab1d827e424e3f9fcbd7af7b9d44b3600cd21488e1d7ad33b891df38d6a
- hash_deduplicacao | qtd=2 | canonico=93 | chave=4a62fe09faff5c6e3478d7a42f383c13a629ff9ecb1a807963c173f09463845e
- hash_deduplicacao | qtd=2 | canonico=529 | chave=015182766142666baa7a451062aabb0e784139c5dc10f6ac258afacf7be8efd4
- hash_deduplicacao | qtd=2 | canonico=530 | chave=a3885ec5751dcb4082416384bdbc22b61b0be42e5908f79fabb85bc3067616b3
- hash_deduplicacao | qtd=2 | canonico=531 | chave=0446eaa4ef16cdf5f4a6eb9ce99ea48db1aee510df35ef7b8ffd41ed06fd7f2c
- hash_deduplicacao | qtd=2 | canonico=532 | chave=12345ed709d23e02c8f451711a7ce160756ce65a1001b6e7ec0ca781dc2ac5ec

## Falsos positivos prováveis

- Nenhum grupo classificado como falso_positivo_provavel.

## Recomendações

- Ver `dedup_recommendations.md` para estratégia e SQLs de inspeção (somente SELECT).
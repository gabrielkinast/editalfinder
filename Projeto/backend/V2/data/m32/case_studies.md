# Estudos de caso M3.2 — PROVISIONAL / EXPLORATORY

Inspeção qualitativa AI do corpus já conhecido, não adjudicação humana. Offsets são Unicode [start,end); páginas PDF são físicas 1-based. Os limites originais não foram alterados. JSON completo por documento em per_document; trechos abreviados abaixo são rotulados.

## M30-F01

Artefato completo: `per_document/document-008.json`. Fonte: https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao. SHA original `042687cd2d281eee9ca961cdf7734495dbce975aaee2b021b5974fcc96426eb9`; texto `a9a0eefdd71c4ae2260fcc4a9b89f2956f3fb55909bfc08c8748abf0606fe167`.

### M30-F01-R1

Referência provisória: `{"discovery_label": "confirmed_opportunity", "modality": "fomento", "opportunity_label": "genuine_opportunity", "review_status": "provisional", "temporal_status": "open"}`; unidade [5784,6736).

Interpretação original: Provisional AI source reading: Named research/bursary/event support call with explicit registration interval containing 2026-10-19; sibling calls have separate non-overlapping scopes.

Fonte congelada (evidências da referência, não labels certificados):

  [5784,5890) página None: Chamada Pública CNPq/CAPES Nº 30/2026 – Programa de Mestrado e Doutorado Acadêmico para Inovação – MAI/DAI

  [6108,6525) página None: A edição de 2026 do Programa de Mestrado e Doutorado para Inovação (MAI/DAI), que estimula a realização de pesquisas de mestrado e doutorado em universidades em parceria com empresas, recebe propostas até o dia 11 de dezembro. A chamada é realizada pelo Conselho Nacional de Desenvolvimento Científico e Tecnológico (CNPq) e conta com a parceria da Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES).

  [6700,6735) página None: Inscrições: / 19/08/2026 a 11/12/2026

Previsão representative real: `{"discovery": "confirmed_opportunity", "end": 6735, "modality": "fomento", "segment_id": "segment-0008", "start": 5784, "temporal": "open"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=1; coverage textual=951/952; histograma de descoberta={"confirmed_opportunity": 1}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0008 | [5784,6735) | 0.998950 | 1.000000 | confirmed_opportunity / fomento / open |

Campos reais nesses segmentos (não combinar em candidato novo):

- `segment-0008/field[0] title`: 'Chamada Pública CNPq/CAPES Nº 30/2026 – Programa de Mestrado e Doutorado Acadêmico para Inovação – MAI/DAI'; witness [5784,5890), página None; quote trecho: 'Chamada Pública CNPq/CAPES Nº 30/2026 – Programa de Mestrado e Doutorado Acadêmico para Inovação – MAI/DAI'; suporte qualitativo=unreviewed.
- `segment-0008/field[1] unknown_temporal_expression`: '19/08/2026'; witness [6060,6076), página None; quote trecho: '19/08/2026 08h53'; suporte qualitativo=unreviewed.
- `segment-0008/field[2] unknown_temporal_expression`: '13/10/2026'; witness [6091,6107), página None; quote trecho: '13/10/2026 12h34'; suporte qualitativo=unreviewed.
- `segment-0008/field[3] funding_organization_expression`: 'A edição de 2026 do Programa de Mestrado e Doutorado para Inovação (MAI/DAI), que estimula a realização de pesquisas de mestrado e doutorado em universidades em parceria com empresas, recebe propostas' [expressão abreviada]; witness [6108,6525), página None; quote trecho: 'A edição de 2026 do Programa de Mestrado e Doutorado para Inovação (MAI/DAI), que estimula a realização de pesquisas de mestrado e doutorado em universidades em parceria com empres'; suporte qualitativo=unresolved.
- `segment-0008/field[4] attachment_unavailable`: 'Anexo II: Plano de Trabalho Programa MAI/DAI'; witness [6534,6578), página None; quote trecho: 'Anexo II: Plano de Trabalho Programa MAI/DAI'; suporte qualitativo=unreviewed.
- `segment-0008/field[5] attachment_unavailable`: 'Anexo III: Declaração Institucional do Representante MAI/DAI'; witness [6579,6639), página None; quote trecho: 'Anexo III: Declaração Institucional do Representante MAI/DAI'; suporte qualitativo=unreviewed.
- `segment-0008/field[6] attachment_unavailable`: 'Anexo IV: Carta de Concordância da Instituição Parceira'; witness [6640,6695), página None; quote trecho: 'Anexo IV: Carta de Concordância da Instituição Parceira'; suporte qualitativo=unreviewed.
- `segment-0008/field[7] opening_date`: '19/08/2026'; witness [6712,6735), página None; quote trecho: '19/08/2026 a 11/12/2026'; suporte qualitativo=unreviewed.
- `segment-0008/field[8] submission_deadline`: '11/12/2026'; witness [6712,6735), página None; quote trecho: '19/08/2026 a 11/12/2026'; suporte qualitativo=unreviewed.

Discordâncias contra referência: []. Isso não determina automaticamente qual lado está correto.

- Revisão AI `M30-F01:segment-0008:field:3`: strong_hypothesis, unresolved. realizada pelo CNPq e parceria CAPES comprovam organização/realização. Isoladamente não discriminam emissor e financiador de cada componente. Não certificar instituição financiadora só por esse gatilho. Causa (high): role_patterns associa realizada pelo a funding_organization_expression.

Incerteza restante: Only the four records in this frozen page are covered; pagination not followed.

### M30-F01-R2

Referência provisória: `{"discovery_label": "confirmed_opportunity", "modality": "fomento", "opportunity_label": "genuine_opportunity", "review_status": "provisional", "temporal_status": "open"}`; unidade [6736,7491).

Interpretação original: Provisional AI source reading: Named research/bursary/event support call with explicit registration interval containing 2026-10-19; sibling calls have separate non-overlapping scopes.

Fonte congelada (evidências da referência, não labels certificados):

  [6736,6840) página None: Chamada CNPq Nº 34/2026 - Auxílio à Promoção de Eventos Científicos, Tecnológicos e/ou de Inovação - ARC

  [7058,7442) página None: O CNPq torna pública a Chamada CNPq nº 34/2026, que tem por objeto a / poiar a realização no Brasil de eventos de grande porte, de abrangência mundial, internacional ou nacional, relacionados a ciência, tecnologia e inovação, tais como encontros, congressos e outros similares que visem contribuir significativamente para o desenvolvimento científico e tecnológico e a inovação do País.

  [7451,7486) página None: Inscrições: / 14/10/2026 a 04/12/2026

Previsão representative real: `{"discovery": "confirmed_opportunity", "end": 7490, "modality": "fomento", "segment_id": "segment-0009", "start": 6736, "temporal": "open"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=1; coverage textual=754/755; histograma de descoberta={"confirmed_opportunity": 1}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0009 | [6736,7490) | 0.998675 | 1.000000 | confirmed_opportunity / fomento / open |

Campos reais nesses segmentos (não combinar em candidato novo):

- `segment-0009/field[0] title`: 'Chamada CNPq Nº 34/2026 - Auxílio à Promoção de Eventos Científicos, Tecnológicos e/ou de Inovação - ARC'; witness [6736,6840), página None; quote trecho: 'Chamada CNPq Nº 34/2026 - Auxílio à Promoção de Eventos Científicos, Tecnológicos e/ou de Inovação - ARC'; suporte qualitativo=unreviewed.
- `segment-0009/field[1] unknown_temporal_expression`: '14/10/2026'; witness [7010,7026), página None; quote trecho: '14/10/2026 07h50'; suporte qualitativo=unreviewed.
- `segment-0009/field[2] unknown_temporal_expression`: '14/10/2026'; witness [7041,7057), página None; quote trecho: '14/10/2026 10h48'; suporte qualitativo=unreviewed.
- `segment-0009/field[3] publishing_organization_expression`: 'O CNPq torna pública a Chamada CNPq nº 34/2026, que tem por objeto a'; witness [7058,7126), página None; quote trecho: 'O CNPq torna pública a Chamada CNPq nº 34/2026, que tem por objeto a'; suporte qualitativo=unreviewed.
- `segment-0009/field[4] execution_location_expression`: 'poiar a realização no Brasil de eventos de grande porte, de abrangência mundial, internacional ou nacional, relacionados a ciência, tecnologia e inovação, tais como encontros, congressos e outros simi' [expressão abreviada]; witness [7127,7442), página None; quote trecho: 'poiar a realização no Brasil de eventos de grande porte, de abrangência mundial, internacional ou nacional, relacionados a ciência, tecnologia e inovação, tais como encontros, cong'; suporte qualitativo=unreviewed.
- `segment-0009/field[5] opening_date`: '14/10/2026'; witness [7463,7486), página None; quote trecho: '14/10/2026 a 04/12/2026'; suporte qualitativo=unreviewed.
- `segment-0009/field[6] submission_deadline`: '04/12/2026'; witness [7463,7486), página None; quote trecho: '14/10/2026 a 04/12/2026'; suporte qualitativo=unreviewed.

Discordâncias contra referência: []. Isso não determina automaticamente qual lado está correto.


Incerteza restante: Only the four records in this frozen page are covered; pagination not followed.

### M30-F01-R3

Referência provisória: `{"discovery_label": "confirmed_opportunity", "modality": "fomento", "opportunity_label": "genuine_opportunity", "review_status": "provisional", "temporal_status": "open"}`; unidade [7491,8213).

Interpretação original: Provisional AI source reading: Named research/bursary/event support call with explicit registration interval containing 2026-10-19; sibling calls have separate non-overlapping scopes.

Fonte congelada (evidências da referência, não labels certificados):

  [7491,7531) página None: Chamada Pública MCTI/CNPq/ANR N° 32/2026

  [7749,8070) página None: Chamada Pública entre o Conselho Nacional de Desenvolvimento Científico e Tecnológico - CNPq e a Agência Nacional de Pesquisa - ANR, tendo por objetivo selecionar projetos de pesquisa conjuntos entre grupos brasileiros e franceses, que visem contribuir para o desenvolvimento científico, tecnológico e a inovação do país.

  [8079,8114) página None: Inscrições: / 03/09/2026 a 31/03/2027

Previsão representative real: `{"discovery": "confirmed_opportunity", "end": 8212, "modality": "fomento", "segment_id": "segment-0010", "start": 7491, "temporal": "open"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=1; coverage textual=721/722; histograma de descoberta={"confirmed_opportunity": 1}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0010 | [7491,8212) | 0.998615 | 1.000000 | confirmed_opportunity / fomento / open |

Campos reais nesses segmentos (não combinar em candidato novo):

- `segment-0010/field[0] title`: 'Chamada Pública MCTI/CNPq/ANR N° 32/2026'; witness [7491,7531), página None; quote trecho: 'Chamada Pública MCTI/CNPq/ANR N° 32/2026'; suporte qualitativo=unreviewed.
- `segment-0010/field[1] unknown_temporal_expression`: '03/09/2026'; witness [7701,7717), página None; quote trecho: '03/09/2026 08h00'; suporte qualitativo=unreviewed.
- `segment-0010/field[2] unknown_temporal_expression`: '04/09/2026'; witness [7732,7748), página None; quote trecho: '04/09/2026 11h26'; suporte qualitativo=unreviewed.
- `segment-0010/field[3] opening_date`: '03/09/2026'; witness [8091,8114), página None; quote trecho: '03/09/2026 a 31/03/2027'; suporte qualitativo=unreviewed.
- `segment-0010/field[4] submission_deadline`: '31/03/2027'; witness [8091,8114), página None; quote trecho: '03/09/2026 a 31/03/2027'; suporte qualitativo=unreviewed.

Discordâncias contra referência: []. Isso não determina automaticamente qual lado está correto.


Incerteza restante: Only the four records in this frozen page are covered; pagination not followed.

### M30-F01-R4

Referência provisória: `{"discovery_label": "confirmed_opportunity", "modality": "fomento", "opportunity_label": "genuine_opportunity", "review_status": "provisional", "temporal_status": "open"}`; unidade [8213,9578).

Interpretação original: Provisional AI source reading: Named research/bursary/event support call with explicit registration interval containing 2026-10-19; sibling calls have separate non-overlapping scopes.

Fonte congelada (evidências da referência, não labels certificados):

  [8213,8270) página None: Chamada CNPq nº 33/2026 - Bolsas de Produtividade do CNPq

  [8488,9183) página None: O CNPq torna pública a Chamada CNPq nº 33/2026, que tem por objeto conceder bolsas nas seguintes modalidades: Produtividade em Desenvolvimento Tecnológico e Extensão Inovadora (DT), Produtividade em Pesquisa (PQ) e Produtividade em Pesquisa Sênior (PQSr). / São objetivos desta chamada: / a) valorizar pesquisadores que possuam produção científica, tecnológica e de inovação de destaque em suas respectivas áreas do conhecimento; / b) incentivar o aumento da produção científica, tecnológica e de inovação de qualidade; / c) selecionar projetos de pesquisa que sejam propostos considerando o rigor e o método científico, bem como outros conceitos fundamentais para a produção do conhecimento científico.

  [9542,9577) página None: Inscrições: / 07/10/2026 a 07/01/2027

Previsão representative real: `{"discovery": "confirmed_opportunity", "end": 9577, "modality": "fomento", "segment_id": "segment-0011", "start": 8213, "temporal": "open"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=1; coverage textual=1364/1365; histograma de descoberta={"confirmed_opportunity": 1}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0011 | [8213,9577) | 0.999267 | 1.000000 | confirmed_opportunity / fomento / open |

Campos reais nesses segmentos (não combinar em candidato novo):

- `segment-0011/field[0] title`: 'Chamada CNPq nº 33/2026 - Bolsas de Produtividade do CNPq'; witness [8213,8270), página None; quote trecho: 'Chamada CNPq nº 33/2026 - Bolsas de Produtividade do CNPq'; suporte qualitativo=unreviewed.
- `segment-0011/field[1] unknown_temporal_expression`: '07/10/2026'; witness [8440,8456), página None; quote trecho: '07/10/2026 10h29'; suporte qualitativo=unreviewed.
- `segment-0011/field[2] unknown_temporal_expression`: '13/10/2026'; witness [8471,8487), página None; quote trecho: '13/10/2026 17h16'; suporte qualitativo=unreviewed.
- `segment-0011/field[3] publishing_organization_expression`: 'O CNPq torna pública a Chamada CNPq nº 33/2026, que tem por objeto conceder bolsas nas seguintes modalidades: Produtividade em Desenvolvimento Tecnológico e Extensão Inovadora (DT), Produtividade em P' [expressão abreviada]; witness [8488,8743), página None; quote trecho: 'O CNPq torna pública a Chamada CNPq nº 33/2026, que tem por objeto conceder bolsas nas seguintes modalidades: Produtividade em Desenvolvimento Tecnológico e Extensão Inovadora (DT)'; suporte qualitativo=unreviewed.
- `segment-0011/field[4] attachment_unavailable`: 'Anexo I - Critérios para avaliação de Bolsas de Produtividade'; witness [9192,9253), página None; quote trecho: 'Anexo I - Critérios para avaliação de Bolsas de Produtividade'; suporte qualitativo=unreviewed.
- `segment-0011/field[5] rectification_date_expression`: '13/10/2026'; witness [9254,9349), página None; quote trecho: 'Anexo I - Critérios para avaliação de Bolsas de Produtividade - versão atualizada em 13/10/2026'; suporte qualitativo=unreviewed.
- `segment-0011/field[6] attachment_unavailable`: 'Anexo I - Critérios para avaliação de Bolsas de Produtividade - versão atualizada em 13/10/2026'; witness [9254,9349), página None; quote trecho: 'Anexo I - Critérios para avaliação de Bolsas de Produtividade - versão atualizada em 13/10/2026'; suporte qualitativo=unreviewed.
- `segment-0011/field[7] rectification_date_expression`: '13/10/2026'; witness [9354,9378), página None; quote trecho: 'Errata nº 1 - 13/10/2026'; suporte qualitativo=unreviewed.
- `segment-0011/field[8] attachment_unavailable`: 'O CNPq informa alteração no critério de julgamento do CA-DT, constante do Anexo I da Chamada. A versão atualizada consta com a modificação assinalada em vermelho.'; witness [9379,9541), página None; quote trecho: 'O CNPq informa alteração no critério de julgamento do CA-DT, constante do Anexo I da Chamada. A versão atualizada consta com a modificação assinalada em vermelho.'; suporte qualitativo=unreviewed.
- `segment-0011/field[9] opening_date`: '07/10/2026'; witness [9554,9577), página None; quote trecho: '07/10/2026 a 07/01/2027'; suporte qualitativo=unreviewed.
- `segment-0011/field[10] submission_deadline`: '07/01/2027'; witness [9554,9577), página None; quote trecho: '07/10/2026 a 07/01/2027'; suporte qualitativo=unreviewed.

Discordâncias contra referência: []. Isso não determina automaticamente qual lado está correto.


Incerteza restante: Only the four records in this frozen page are covered; pagination not followed.

## M30-C05

Artefato completo: `per_document/document-004.json`. Fonte: https://www.bndes.gov.br/wps/portal/site/home/financiamento/finame. SHA original `c0e0a40383fa1af0c4a6ffb82b23908c61a349952cc5ac9ae7985bddd91833d9`; texto `fe14ed41c970329144230b15000fa3d0cd3f8ba5b5d78fabaad8b89e4708a359`.

### M30-C05-R1

Referência provisória: `{"discovery_label": "opportunity_signal", "modality": "credito", "opportunity_label": "uncertain", "review_status": "provisional", "temporal_status": "undetermined"}`; unidade [305,836).

Interpretação original: Overview/navigation points to credit lines and financing agents but this scoped overview does not establish a particular complete instrument with beneficiary access conditions. Relevant discovery signal, not a confirmed application opportunity.

Fonte congelada (evidências da referência, não labels certificados):

  [305,836) página None: BNDES Finame / Como obter um financiamento BNDES Finame? / Entenda o BNDES Finame, as linhas de financiamento disponíveis e o processo de solicitação de apoio. / Máquinas e equipamentos / Conheça os itens credenciados pelo BNDES. / Instituições financeiras / Saiba quais são os agentes financeiros credenciados a conceder financiamentos BNDES Finame. / Desempenho operacional - BNDES Finame / Acompanhe o desempenho das linhas do BNDES Finame, com números de operações e valores aprovados por região, ranking dos agentes financeiros e outros dados

Previsão representative real: `{"discovery": "abstain", "end": 836, "modality": "undetermined", "segment_id": "segment-0019", "start": 682, "temporal": "undetermined"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=9; coverage textual=523/531; histograma de descoberta={"abstain": 6, "opportunity_signal": 3}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0011 | [305,317) | 0.022599 | 1.000000 | abstain / undetermined / undetermined |
| segment-0012 | [318,359) | 0.077213 | 1.000000 | opportunity_signal / credito / undetermined |
| segment-0013 | [360,460) | 0.188324 | 1.000000 | opportunity_signal / credito / undetermined |
| segment-0014 | [461,484) | 0.043315 | 1.000000 | abstain / undetermined / undetermined |
| segment-0015 | [485,526) | 0.077213 | 1.000000 | abstain / undetermined / undetermined |
| segment-0016 | [527,551) | 0.045198 | 1.000000 | abstain / undetermined / undetermined |
| segment-0017 | [552,643) | 0.171375 | 1.000000 | opportunity_signal / credito / undetermined |
| segment-0018 | [644,681) | 0.069680 | 1.000000 | abstain / undetermined / undetermined |
| segment-0019 | [682,836) | 0.290019 | 1.000000 | abstain / undetermined / undetermined |

Campos reais nesses segmentos (não combinar em candidato novo):

- `segment-0011/field[0] title`: 'BNDES Finame'; witness [305,317), página None; quote trecho: 'BNDES Finame'; suporte qualitativo=unreviewed.
- `segment-0012/field[0] title`: 'Como obter um financiamento BNDES Finame?'; witness [318,359), página None; quote trecho: 'Como obter um financiamento BNDES Finame?'; suporte qualitativo=unreviewed.
- `segment-0018/field[0] title`: 'Desempenho operacional - BNDES Finame'; witness [644,681), página None; quote trecho: 'Desempenho operacional - BNDES Finame'; suporte qualitativo=unreviewed.

Discordâncias contra referência: ['discovery_label', 'modality']. Isso não determina automaticamente qual lado está correto.


Incerteza restante: Overview and navigation are not a canonical opportunity; details are on unacquired linked pages. Finame Direto is annotated as a separate record.

### M30-C05-R2

Referência provisória: `{"discovery_label": "confirmed_opportunity", "modality": "credito", "opportunity_label": "genuine_opportunity", "review_status": "provisional", "temporal_status": "undetermined"}`; unidade [837,994).

Interpretação original: The separate Finame Direto record identifies a credit instrument, its equipment purpose, the annual-revenue threshold and the ability to request a credit limit online. This supports existence, not automatic approval or an explicit deadline.

Fonte congelada (evidências da referência, não labels certificados):

  [837,994) página None: Finame Direto / Empresas com faturamento anual acima de R$ 80 milhões agora podem solicitar online limite de crédito para aquisição de máquinas e equipamentos.

Previsão representative real: `{"discovery": "confirmed_opportunity", "end": 994, "modality": "credito", "segment_id": "segment-0021", "start": 851, "temporal": "undetermined"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=2; coverage textual=156/157; histograma de descoberta={"abstain": 1, "confirmed_opportunity": 1}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0020 | [837,850) | 0.082803 | 1.000000 | abstain / undetermined / undetermined |
| segment-0021 | [851,994) | 0.910828 | 1.000000 | confirmed_opportunity / credito / undetermined |

Campos reais nesses segmentos (não combinar em candidato novo):

- `segment-0020/field[0] title`: 'Finame Direto'; witness [837,850), página None; quote trecho: 'Finame Direto'; suporte qualitativo=unreviewed.
- `segment-0021/field[0] borrower_revenue_requirement`: 'R$ 80 milhões'; witness [851,994), página None; quote trecho: 'Empresas com faturamento anual acima de R$ 80 milhões agora podem solicitar online limite de crédito para aquisição de máquinas e equipamentos.'; suporte qualitativo=supported.
- `segment-0021/field[1] applicant_requirements`: 'Empresas com faturamento anual acima de R$ 80 milhões agora podem solicitar online limite de crédito para aquisição de máquinas e equipamentos.'; witness [851,994), página None; quote trecho: 'Empresas com faturamento anual acima de R$ 80 milhões agora podem solicitar online limite de crédito para aquisição de máquinas e equipamentos.'; suporte qualitativo=unreviewed.
- `segment-0021/field[2] application_instructions`: 'Empresas com faturamento anual acima de R$ 80 milhões agora podem solicitar online limite de crédito para aquisição de máquinas e equipamentos.'; witness [851,994), página None; quote trecho: 'Empresas com faturamento anual acima de R$ 80 milhões agora podem solicitar online limite de crédito para aquisição de máquinas e equipamentos.'; suporte qualitativo=unreviewed.

Discordâncias contra referência: []. Isso não determina automaticamente qual lado está correto.


Incerteza restante: No verified application cutoff or continuous-availability guarantee in this record. Snapshot existence is not proof of current openness.

## M30-C07

Artefato completo: `per_document/document-006.json`. Fonte: https://www.brde.com.br/noticia/creditur-rs-amplia-acesso-ao-credito-para-fortalecer-turismo-na-area-metropolitana-de-porto-alegre/. SHA original `41e772a70b3273f3ecd6ca791b0e182c824a0ac7c7bbf95394f56c2c85eb8a5c`; texto `763bd4272c86a8110be6132d5851b7675e79e2c694cc945bbd930cb5cafdc696`.

### M30-C07-R1

Referência provisória: `{"discovery_label": "unrelated_or_non_actionable", "modality": "credito", "opportunity_label": "not_opportunity", "review_status": "provisional", "temporal_status": "not_applicable"}`; unidade [1963,2746).

Interpretação original: This first scoped record reports an already celebrated R$2m financing for one named business. It does not create a new financing opportunity for another applicant. The following general-program paragraphs are a different record, not discarded as news.

Fonte congelada (evidências da referência, não labels certificados):

  [1963,2746) página None: CrediTur RS amplia acesso ao crédito para fortalecer turismo na área metropolitana de Porto Alegre / 07/10/2026 | Aldemir Lauri Kerschner / BRDE e Sicredi Origens celebram financiamento com a Quinta da Estância, de Viamão. / Referência nacional em turismo rural pedagógico e educação ambiental, a Quinta da Estância, localizada em Viamão, está entre as novas empresas contempladas através do programa CrediTur RS, voltado ao fortalecimento do setor turístico em diferentes regiões do estado. Nesta terça-feira (dia 6/10), a partir da parceria entre o Banco Regional de Desenvolvimento do Extremo Sul (BRDE) e a Sicredi Origens RS, ocorreu a celebração do financiamento de R$ 2 milhões, recursos que serão destinados ao capital de giro e à ampliação da capacidade de atendimento da empresa.

Previsão representative real: `{"discovery": "opportunity_signal", "end": 2746, "modality": "credito", "segment_id": "segment-0001", "start": 2182, "temporal": "undetermined"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=2; coverage textual=646/783; histograma de descoberta={"opportunity_signal": 1, "unrelated_or_non_actionable": 1}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0000 | [2099,2181) | 0.104725 | 1.000000 | unrelated_or_non_actionable / credito / not_applicable |
| segment-0001 | [2182,2746) | 0.720307 | 1.000000 | opportunity_signal / credito / undetermined |

Campos reais nesses segmentos (não combinar em candidato novo):

- `segment-0001/field[0] financing_amount_expression`: 'R$ 2 milhões'; witness [2182,2746), página None; quote trecho: 'Referência nacional em turismo rural pedagógico e educação ambiental, a Quinta da Estância, localizada em Viamão, está entre as novas empresas contempladas através do programa Cred'; suporte qualitativo=unreviewed.
- `segment-0001/field[1] beneficiary_expression`: 'Referência nacional em turismo rural pedagógico e educação ambiental, a Quinta da Estância, localizada em Viamão, está entre as novas empresas contempladas através do programa CrediTur RS, voltado ao ' [expressão abreviada]; witness [2182,2746), página None; quote trecho: 'Referência nacional em turismo rural pedagógico e educação ambiental, a Quinta da Estância, localizada em Viamão, está entre as novas empresas contempladas através do programa Cred'; suporte qualitativo=unreviewed.

Discordâncias contra referência: ['discovery_label', 'temporal_status']. Isso não determina automaticamente qual lado está correto.

- Revisão AI `M30-C07:segment-0001:discovery:classification`: confirmed_defect, unsupported. A unidade é financiamento já celebrado a Quinta da Estância; sinal como nova oportunidade é excessivo. A manchete anterior contém celebram financiamento, enquanto o maior parágrafo isolado perde esse gatilho. Causa (high): classify completed depende de padrões locais; segmentação por nós separa a frase de conclusão.

Incerteza restante: Negative for new opportunity existence in this transaction record, not a claim the CrediTur program does not exist.

### M30-C07-R2

Referência provisória: `{"discovery_label": "confirmed_opportunity", "modality": "credito", "opportunity_label": "genuine_opportunity", "review_status": "provisional", "temporal_status": "undetermined"}`; unidade [2747,4270).

Interpretação original: Unlike the completed-transaction record above, these paragraphs describe a distinct credit program for tourism businesses with Cadastur and a per-company limit. Primary bank communication confirms conditions; no submission date or guaranteed funding is inferred.

Fonte congelada (evidências da referência, não labels certificados):

  [2747,3647) página None: Conforme o secretário estadual de Turismo, Raphael Ayub, o CrediTur RS foi estruturado justamente para ampliar o acesso ao crédito e incentivar novos investimentos no setor. “Queremos dar condições para que os nossos empreendedores possam crescer, qualificar seus negócios e ampliar a capacidade de atendimento. A Quinta da Estância é um exemplo muito importante, porque une turismo, educação e preservação ambiental. É esse tipo de investimento que fortalece os destinos, gera oportunidades e faz o turismo contribuir cada vez mais para o desenvolvimento econômico do nosso estado”, afirmou Auyb. / O programa é destinado a empresas de todos os portes, desde que possuam o Cadastro de Prestadores de Serviços Turísticos (Cadastur), do Ministério do Turismo. O limite de financiamento é de R$ 4 milhões por empresa, com juros ao redor de 10% ao ano (IPCA mais 6%) e prazo de cinco anos para amortização [trecho; evidência integral no JSON]

Previsão representative real: `{"discovery": "opportunity_signal", "end": 3344, "modality": "credito", "segment_id": "segment-0002", "start": 2747, "temporal": "undetermined"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=4; coverage textual=1520/1523; histograma de descoberta={"abstain": 1, "opportunity_signal": 3}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0002 | [2747,3344) | 0.391989 | 1.000000 | opportunity_signal / credito / undetermined |
| segment-0003 | [3345,3684) | 0.222587 | 1.000000 | opportunity_signal / credito / undetermined |
| segment-0004 | [3685,3702) | 0.011162 | 1.000000 | abstain / undetermined / undetermined |
| segment-0005 | [3703,4270) | 0.372292 | 1.000000 | opportunity_signal / credito / undetermined |

Campos reais nesses segmentos (não combinar em candidato novo):

- `segment-0003/field[0] financing_amount_expression`: 'R$ 4 milhões'; witness [3345,3684), página None; quote trecho: 'O programa é destinado a empresas de todos os portes, desde que possuam o Cadastro de Prestadores de Serviços Turísticos (Cadastur), do Ministério do Turismo. O limite de financiam'; suporte qualitativo=unreviewed.
- `segment-0003/field[1] applicant_requirements`: 'O programa é destinado a empresas de todos os portes, desde que possuam o Cadastro de Prestadores de Serviços Turísticos (Cadastur), do Ministério do Turismo. O limite de financiamento é de R$ 4 milhõ' [expressão abreviada]; witness [3345,3684), página None; quote trecho: 'O programa é destinado a empresas de todos os portes, desde que possuam o Cadastro de Prestadores de Serviços Turísticos (Cadastur), do Ministério do Turismo. O limite de financiam'; suporte qualitativo=unreviewed.
- `segment-0003/field[2] repayment_expression`: 'O programa é destinado a empresas de todos os portes, desde que possuam o Cadastro de Prestadores de Serviços Turísticos (Cadastur), do Ministério do Turismo. O limite de financiamento é de R$ 4 milhõ' [expressão abreviada]; witness [3345,3684), página None; quote trecho: 'O programa é destinado a empresas de todos os portes, desde que possuam o Cadastro de Prestadores de Serviços Turísticos (Cadastur), do Ministério do Turismo. O limite de financiam'; suporte qualitativo=unreviewed.

Discordâncias contra referência: ['discovery_label']. Isso não determina automaticamente qual lado está correto.

- Revisão AI `M30-C07:segment-0002:discovery:classification`: strong_hypothesis, partial. O programa tem Cadastur, teto por empresa e condições na mesma unidade anotada; apenas sinal é conservador, possivelmente incompleto, sem inventar janela. Causa (medium): Rota/condições são distribuídas em blocos; confirmed depende de gatilhos de acesso estreitos.

Incerteza restante: No application URL is asserted from this news paragraph. Stated loan interest and maturity are not submission deadlines and are not normalized.

## M30-I03

Artefato completo: `per_document/document-017.json`. Fonte: https://criatec4.com/portfolio/. SHA original `2a45f9082c03eceee8b385e336abb270659653523213f12532214492cddba24a`; texto `dcf2157aa3bc2353e1cd10599f179754ce4a4a0e41d06cd064f526df59161e3c`.

### M30-I03-R1

Referência provisória: `{"discovery_label": "unrelated_or_non_actionable", "modality": "investimentos", "opportunity_label": "not_opportunity", "review_status": "provisional", "temporal_status": "not_applicable"}`; unidade [46,172).

Interpretação original: Hard negative: o conteúdo central é portfólio de investimentos feitos pelo time, não oferta de nova rodada nem chamada. O menu Aplicar para investimento não transforma cases passados em oportunidade atual.

Fonte congelada (evidências da referência, não labels certificados):

  [46,69) página None: Conheça nosso / Portfólio

  [70,172) página None: Estes são alguns dos principais investimentos feitos pelo time do Fundo e que viraram cases de sucesso

Previsão representative real: `{"discovery": "abstain", "end": 172, "modality": "undetermined", "segment_id": "segment-0003", "start": 70, "temporal": "undetermined"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=3; coverage textual=124/126; histograma de descoberta={"abstain": 2, "unrelated_or_non_actionable": 1}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0001 | [46,59) | 0.103175 | 1.000000 | abstain / undetermined / undetermined |
| segment-0002 | [60,69) | 0.071429 | 1.000000 | unrelated_or_non_actionable / undetermined / not_applicable |
| segment-0003 | [70,172) | 0.809524 | 1.000000 | abstain / undetermined / undetermined |

Campos reais nesses segmentos (não combinar em candidato novo):

- Nenhum campo extraído nos segmentos com overlap.

Discordâncias contra referência: ['discovery_label', 'modality', 'temporal_status']. Isso não determina automaticamente qual lado está correto.

- Revisão AI `M30-I03:segment-0003:discovery:classification`: unresolved_disagreement, unresolved. Portfólio concluído não é nova oferta. Abstenção do maior trecho não é falsa confirmação; outros trechos classificam portfólio corretamente. Causa (medium): O título é dividido em nós e o maior trecho não transporta todo o contexto.

Incerteza restante: Portfólio do time não comprova que todos os aportes tenham sido feitos pelo Criatec 4.; Não usar placeholders Ano de investimento: 00/00/00 como data real; empresas são pessoas jurídicas, não lista de candidatos individuais.

## M30-I05

Artefato completo: `per_document/document-019.json`. Fonte: https://agenciadenoticias.bndes.gov.br/noticia/BNDES-e-FINEP-recebem-19-propostas-para-FIP-Conexoes-Startups/. SHA original `8aefb421c842dd07d8779deec4988f1e6bbb8a9a13b2050b614aca2265e920af`; texto `14f436eae3452a361a3fd16f92b9f447b8a2ed2ef6a7f843980adf34f7fd9c9b`.

### M30-I05-R1

Referência provisória: `{"discovery_label": "opportunity_signal", "modality": "investimentos", "opportunity_label": "uncertain", "review_status": "provisional", "temporal_status": "undetermined"}`; unidade [0,2234).

Interpretação original: Notícia de estruturação de futuro FIP sinaliza investimento em startups. O prazo encerrado em agosto refere-se exclusivamente à seleção do gestor; classificação prevista até novembro não é prazo de startups. Não contar a chamada vencida como oportunidade vigente.

Fonte congelada (evidências da referência, não labels certificados):

  [0,61) página None: BNDES e FINEP recebem 19 propostas para FIP Conexões Startups

  [1057,1419) página None: O Banco Nacional de Desenvolvimento Econômico e Social (BNDES) e a Financiadora de Estudos e Projetos (Finep) receberam 19 propostas na chamada pública para seleção do gestor do FIP Conexões Startups. O prazo para apresentação das propostas foi encerrado em 12 de agosto. A divulgação da classificação final está prevista para ocorrer até 23 de novembro de 2026.

  [1420,1838) página None: A iniciativa busca estruturar um fundo de investimento em participações voltado a startups em estágio inicial, especialmente aquelas que tenham recebido apoio de programas de fomento à inovação, subvenção ou aceleração realizados no país. O objetivo é ampliar a conversão dessas empresas em oportunidades aptas a receber investimentos de fundos de capital semente, venture capital e outros investidores institucionais.

  [1839,2234) página None: O FIP tem estimativa de mobilizar até R$ 250 milhões para investir em startups em fase inicial. A BNDESPAR, subsidiária integral do BNDES, comprometerá até R$ 100 milhões. Já a Finep, com recursos do Fundo Nacional de Desenvolvimento Científico e Tecnológico (FNDCT), irá comprometer R$ 50 milhões. Caberá ao gestor selecionado mobilizar outros investidores para complementar o capital do fundo.

  [836,868) página None: Publicado em 17/08/2026 às 12:36

Previsão representative real: `{"discovery": "opportunity_signal", "end": 1838, "modality": "undetermined", "segment_id": "segment-0018", "start": 1420, "temporal": "undetermined"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=20; coverage textual=1781/2234; histograma de descoberta={"abstain": 16, "opportunity_signal": 4}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0000 | [105,136) | 0.013876 | 1.000000 | abstain / undetermined / undetermined |
| segment-0001 | [137,159) | 0.009848 | 1.000000 | abstain / undetermined / undetermined |
| segment-0002 | [160,182) | 0.009848 | 1.000000 | abstain / undetermined / undetermined |
| segment-0003 | [183,306) | 0.055058 | 1.000000 | abstain / undetermined / undetermined |
| segment-0004 | [307,315) | 0.003581 | 1.000000 | abstain / undetermined / undetermined |
| segment-0005 | [316,325) | 0.004029 | 1.000000 | abstain / undetermined / undetermined |
| segment-0006 | [326,360) | 0.015219 | 1.000000 | abstain / undetermined / undetermined |
| segment-0007 | [361,393) | 0.014324 | 1.000000 | abstain / undetermined / undetermined |
| segment-0008 | [394,408) | 0.006267 | 1.000000 | abstain / undetermined / undetermined |
| segment-0009 | [409,411) | 0.000895 | 1.000000 | abstain / undetermined / undetermined |
| segment-0010 | [412,414) | 0.000895 | 1.000000 | abstain / undetermined / undetermined |
| segment-0011 | [744,805) | 0.027305 | 1.000000 | opportunity_signal / investimentos / undetermined |
| segment-0012 | [806,835) | 0.012981 | 1.000000 | abstain / undetermined / undetermined |
| segment-0013 | [836,868) | 0.014324 | 1.000000 | abstain / undetermined / undetermined |
| segment-0014 | [869,902) | 0.014772 | 1.000000 | abstain / undetermined / undetermined |
| segment-0015 | [903,919) | 0.007162 | 1.000000 | abstain / undetermined / undetermined |
| segment-0016 | [920,1056) | 0.060877 | 1.000000 | abstain / undetermined / undetermined |
| segment-0017 | [1057,1419) | 0.162041 | 1.000000 | opportunity_signal / investimentos / undetermined |
| segment-0018 | [1420,1838) | 0.187108 | 1.000000 | opportunity_signal / undetermined / undetermined |
| segment-0019 | [1839,2234) | 0.176813 | 1.000000 | opportunity_signal / investimentos / undetermined |

Campos reais nesses segmentos (não combinar em candidato novo):

- `segment-0013/field[0] publication_date_expression`: '17/08/2026'; witness [836,868), página None; quote trecho: 'Publicado em 17/08/2026 às 12:36'; suporte qualitativo=unreviewed.
- `segment-0014/field[0] unknown_temporal_expression`: '17/08/2026'; witness [869,902), página None; quote trecho: 'Atualizado em 17/08/2026 às 13:06'; suporte qualitativo=unreviewed.
- `segment-0019/field[0] fund_capital_estimate`: 'R$ 250 milhões'; witness [1839,2234), página None; quote trecho: 'O FIP tem estimativa de mobilizar até R$ 250 milhões para investir em startups em fase inicial. A BNDESPAR, subsidiária integral do BNDES, comprometerá até R$ 100 milhões. Já a Fin'; suporte qualitativo=partial.
- `segment-0019/field[1] monetary_expression_unresolved`: 'R$ 100 milhões'; witness [1839,2234), página None; quote trecho: 'O FIP tem estimativa de mobilizar até R$ 250 milhões para investir em startups em fase inicial. A BNDESPAR, subsidiária integral do BNDES, comprometerá até R$ 100 milhões. Já a Fin'; suporte qualitativo=unreviewed.
- `segment-0019/field[2] fund_capital_estimate`: 'R$ 50 milhões'; witness [1839,2234), página None; quote trecho: 'O FIP tem estimativa de mobilizar até R$ 250 milhões para investir em startups em fase inicial. A BNDESPAR, subsidiária integral do BNDES, comprometerá até R$ 100 milhões. Já a Fin'; suporte qualitativo=unsupported.
- `segment-0019/field[3] funding_organization_expression`: 'O FIP tem estimativa de mobilizar até R$ 250 milhões para investir em startups em fase inicial. A BNDESPAR, subsidiária integral do BNDES, comprometerá até R$ 100 milhões. Já a Finep, com recursos do ' [expressão abreviada]; witness [1839,2234), página None; quote trecho: 'O FIP tem estimativa de mobilizar até R$ 250 milhões para investir em startups em fase inicial. A BNDESPAR, subsidiária integral do BNDES, comprometerá até R$ 100 milhões. Já a Fin'; suporte qualitativo=unreviewed.

Discordâncias contra referência: ['modality']. Isso não determina automaticamente qual lado está correto.

- Revisão AI `M30-I05:segment-0019:field:2`: confirmed_defect, unsupported. R$ 50 milhões é compromisso da Finep/FNDCT como investidor; a meta de capital do fundo é até R$ 250 milhões. O label fund_capital_estimate aplicado aos 50 milhões troca o papel. Causa (high): Janela monetária encontra FIP/mobilizar/capital de outras orações e toma precedência sobre o vínculo com comprometer.
- Revisão AI `M30-I05:segment-0019:field:0`: confirmed_defect, partial. O numeral e o papel são relacionados ao campo correto, mas o literal perde até, que qualifica o valor como teto/estimativa. Não equiparar o numeral isolado ao valor com qualificador. Causa (high): MONEY inicia em R$ e não inclui qualificadores precedentes.
- Revisão AI `M30-I05:segment-0018:discovery:classification`: supported_observation, supported. Selecionar gestor e receber 19 propostas de gestores não prova elegibilidade startup. Sinal de estruturação de fundo é sustentado. Causa (medium): Ramo manager precede confirmação no classify; público precisa continuar explícito.

Incerteza restante: Sem canal ou janela de candidatura para startups na notícia.; Capital estimado do fundo não é valor de aporte por startup.

## M30-I06

Artefato completo: `per_document/document-020.json`. Fonte: https://agenciadenoticias.bndes.gov.br/noticia/BNDES-e-Finep-selecionam-a-Monashees-para-gestao-de-fundo-de-IA-de-R$-500-mi. SHA original `5f633c52d2262ab5256b02f695f7c978cbcc7b6a1432f7a3b936ba307cb6d751`; texto `400eabec7ff0762ba07be36655d0acd27deb0a987ab9da461a71b9ac5d98aa3e`.

### M30-I06-R1

Referência provisória: `{"discovery_label": "announced_future_opportunity", "modality": "investimentos", "opportunity_label": "uncertain", "review_status": "provisional", "temporal_status": "undetermined"}`; unidade [0,3490).

Interpretação original: Authoritative announcement identifies a forthcoming IA investment fund, selected manager, intended startup audience and analysis/diligence/structuring still to occur. This supports announced_future_opportunity for discovery, not a presently accessible confirmed instrument. No startup application opening or date is stated, so temporal availability remains undetermined, rather than future merely because fund operations are planned.

Fonte congelada (evidências da referência, não labels certificados):

  [0,76) página None: BNDES e Finep selecionam a Monashees para gestão de fundo de IA de R$ 500 mi

  [1173,1556) página None: O Banco Nacional do Desenvolvimento Econômico e Social (BNDES) e a Financiadora de Estudos e Projetos (Finep) selecionaram a Monashees Gestão de Investimentos como gestora do Fundo de Investimento em Participações de Inteligência Artificial. A chamada pública recebeu 17 propostas. A partir de agora, a proposta selecionada seguirá para a etapa de análise, diligência e estruturação.

  [1557,1935) página None: O novo fundo, que tem estimativa de mobilizar até R$ 500 milhões, é voltado ao apoio a startups intensivas no uso de inteligência artificial, tendo como desafio central ampliar o número, o faturamento e a presença global de startups brasileiras que tenham IA como elemento central do modelo de negócios e geração de valor, e não apenas como ferramenta acessória ou complementar.

  [3048,3490) página None: Serão alvos do investimento startups que tenham como diferencial competitivo a incorporação estruturante da inteligência artificial à sua proposta de valor, e cujo desenvolvimento, adaptação e operação das soluções de inteligência artificial demandem investimentos em dados, modelos, infraestrutura computacional e profissionais especializados, indo além do simples consumo pontual ou acessório de soluções de inteligência artificial prontas.

  [866,898) página None: Publicado em 14/09/2026 às 10:35

Previsão representative real: `{"discovery": "opportunity_signal", "end": 3490, "modality": "investimentos", "segment_id": "segment-0024", "start": 3048, "temporal": "undetermined"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=25; coverage textual=3017/3490; histograma de descoberta={"abstain": 22, "opportunity_signal": 3}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0000 | [120,151) | 0.008883 | 1.000000 | abstain / undetermined / undetermined |
| segment-0001 | [152,174) | 0.006304 | 1.000000 | abstain / undetermined / undetermined |
| segment-0002 | [175,197) | 0.006304 | 1.000000 | abstain / undetermined / undetermined |
| segment-0003 | [198,321) | 0.035244 | 1.000000 | abstain / undetermined / undetermined |
| segment-0004 | [322,330) | 0.002292 | 1.000000 | abstain / undetermined / undetermined |
| segment-0005 | [331,340) | 0.002579 | 1.000000 | abstain / undetermined / undetermined |
| segment-0006 | [341,375) | 0.009742 | 1.000000 | abstain / undetermined / undetermined |
| segment-0007 | [376,408) | 0.009169 | 1.000000 | abstain / undetermined / undetermined |
| segment-0008 | [409,423) | 0.004011 | 1.000000 | abstain / undetermined / undetermined |
| segment-0009 | [424,426) | 0.000573 | 1.000000 | abstain / undetermined / undetermined |
| segment-0010 | [427,429) | 0.000573 | 1.000000 | abstain / undetermined / undetermined |
| segment-0011 | [759,835) | 0.021777 | 1.000000 | opportunity_signal / undetermined / undetermined |
| segment-0012 | [836,865) | 0.008309 | 1.000000 | abstain / undetermined / undetermined |
| segment-0013 | [866,898) | 0.009169 | 1.000000 | abstain / undetermined / undetermined |
| segment-0014 | [899,932) | 0.009456 | 1.000000 | abstain / undetermined / undetermined |
| segment-0015 | [933,949) | 0.004585 | 1.000000 | abstain / undetermined / undetermined |
| segment-0016 | [950,1172) | 0.063610 | 1.000000 | abstain / undetermined / undetermined |
| segment-0017 | [1173,1556) | 0.109742 | 1.000000 | opportunity_signal / investimentos / undetermined |
| segment-0018 | [1557,1935) | 0.108309 | 1.000000 | abstain / undetermined / undetermined |
| segment-0019 | [1936,2202) | 0.076218 | 1.000000 | abstain / undetermined / undetermined |
| segment-0020 | [2203,2461) | 0.073926 | 1.000000 | abstain / undetermined / undetermined |
| segment-0021 | [2462,2707) | 0.070201 | 1.000000 | abstain / undetermined / undetermined |
| segment-0022 | [2708,3023) | 0.090258 | 1.000000 | abstain / undetermined / undetermined |
| segment-0023 | [3024,3047) | 0.006590 | 1.000000 | abstain / undetermined / undetermined |
| segment-0024 | [3048,3490) | 0.126648 | 1.000000 | opportunity_signal / investimentos / undetermined |

Campos reais nesses segmentos (não combinar em candidato novo):

- `segment-0011/field[0] title`: 'BNDES e Finep selecionam a Monashees para gestão de fundo de IA de R$ 500 mi'; witness [759,835), página None; quote trecho: 'BNDES e Finep selecionam a Monashees para gestão de fundo de IA de R$ 500 mi'; suporte qualitativo=unreviewed.
- `segment-0011/field[1] monetary_expression_unresolved`: 'R$ 500 mi'; witness [759,835), página None; quote trecho: 'BNDES e Finep selecionam a Monashees para gestão de fundo de IA de R$ 500 mi'; suporte qualitativo=unreviewed.
- `segment-0013/field[0] publication_date_expression`: '14/09/2026'; witness [866,898), página None; quote trecho: 'Publicado em 14/09/2026 às 10:35'; suporte qualitativo=unreviewed.
- `segment-0014/field[0] unknown_temporal_expression`: '14/09/2026'; witness [899,932), página None; quote trecho: 'Atualizado em 14/09/2026 às 10:41'; suporte qualitativo=unreviewed.
- `segment-0017/field[0] managing_organization_expression`: 'O Banco Nacional do Desenvolvimento Econômico e Social (BNDES) e a Financiadora de Estudos e Projetos (Finep) selecionaram a Monashees Gestão de Investimentos como gestora do Fundo de Investimento em ' [expressão abreviada]; witness [1173,1556), página None; quote trecho: 'O Banco Nacional do Desenvolvimento Econômico e Social (BNDES) e a Financiadora de Estudos e Projetos (Finep) selecionaram a Monashees Gestão de Investimentos como gestora do Fundo'; suporte qualitativo=unreviewed.
- `segment-0017/field[1] fund_stage_expression`: 'O Banco Nacional do Desenvolvimento Econômico e Social (BNDES) e a Financiadora de Estudos e Projetos (Finep) selecionaram a Monashees Gestão de Investimentos como gestora do Fundo de Investimento em ' [expressão abreviada]; witness [1173,1556), página None; quote trecho: 'O Banco Nacional do Desenvolvimento Econômico e Social (BNDES) e a Financiadora de Estudos e Projetos (Finep) selecionaram a Monashees Gestão de Investimentos como gestora do Fundo'; suporte qualitativo=unreviewed.
- `segment-0018/field[0] fund_capital_estimate`: 'R$ 500 milhões'; witness [1557,1935), página None; quote trecho: 'O novo fundo, que tem estimativa de mobilizar até R$ 500 milhões, é voltado ao apoio a startups intensivas no uso de inteligência artificial, tendo como desafio central ampliar o n'; suporte qualitativo=partial.
- `segment-0019/field[0] monetary_expression_unresolved`: 'R$ 125 milhões'; witness [1936,2202), página None; quote trecho: 'A BNDESPAR poderá comprometer até R$ 125 milhões, enquanto o FNDCT/Finep poderá aportar até R$ 80 milhões. O valor a ser comprometido por cotista-âncora estará limitado a 25% de pa'; suporte qualitativo=unreviewed.
- `segment-0019/field[1] monetary_expression_unresolved`: 'R$ 80 milhões'; witness [1936,2202), página None; quote trecho: 'A BNDESPAR poderá comprometer até R$ 125 milhões, enquanto o FNDCT/Finep poderá aportar até R$ 80 milhões. O valor a ser comprometido por cotista-âncora estará limitado a 25% de pa'; suporte qualitativo=unreviewed.

Discordâncias contra referência: ['discovery_label']. Isso não determina automaticamente qual lado está correto.

- Revisão AI `M30-I06:segment-0018:field:0`: confirmed_defect, partial. O numeral e o papel são relacionados ao campo correto, mas o literal perde até, que qualifica o valor como teto/estimativa. Não equiparar o numeral isolado ao valor com qualificador. Causa (high): MONEY inicia em R$ e não inclui qualificadores precedentes.
- Revisão AI `M30-I06:segment-0024:discovery:classification`: unresolved_disagreement, unresolved. Fundo futuro de IA está em análise/diligência/estruturação. Sinal é defensável e anúncio futuro também pode ser: o protocolo exige compromisso de acesso futuro. Nada estabelece candidaturas abertas de startups. A divergência é de nível de confirmação, não de janela future. Causa (medium): Ramo manager sempre devolve signal e future_access só reconhece abertura de inscrições; rubric de anúncio de instrumento é mais ampla.

Incerteza restante: Não há data de início nem prazo de candidatura para startups.; Estruturação ainda condicionada a análise e diligência; existência permanece uncertain.; Não usar capital global estimado como ticket individual.; Parent AI consistency check corrected an initial future temporal proposal: future investment intent is not a verified future application stage. No human adjudication or approval is claimed.

## M30-I07

Artefato completo: `per_document/document-021.json`. Fonte: https://brde.com.br/wp-content/uploads/2026/01/Folder-2026-Mais-Inovacao-AGCUR.pdf. SHA original `974d6f4bc6e3b5872b2e3cbcf5fd861c9cbbe671cdd3d2f0d914b8bc8e6ca3b3`; texto `f5fc847f69f336ab6e0bb59db12d5df0ab417590e50fd64c7dcbed4d64f9752c`.

### M30-I07-R1

Referência provisória: `{"discovery_label": "opportunity_signal", "modality": "investimentos", "opportunity_label": "uncertain", "review_status": "provisional", "temporal_status": "undetermined"}`; unidade [11450,12376).

Interpretação original: Unidade da página de fundos do folder institucional descreve Sul Ventures e estágio de captação dos FIPs. Captação de capital do fundo não equivale a recebimento de candidaturas de startups; sinal de investimento sem janela verificada. Demais páginas de crédito não pertencem à unidade anotada.

Fonte congelada (evidências da referência, não labels certificados):

  [11450,11472) página 12: FUNDOS DE PARTICIPAÇÃO

  [11779,11838) página 12: Atualmente, os seguintes FIPs estão em estágio de captação:

  [11840,11852) página 12: SUL VENTURES

  [11873,12376) página 12: O Fundo Sul Ventures nasceu com o propósito / de impulsionar e desenvolver o ecossistema de / inovação da região Sul do Brasil, por meio de uma / estratégia estruturada de investimentos em Venture / Capital, operando de forma transversal e hands-on, / acompanhando de perto cada investimento para / maximizar seu potencial de crescimento. O Fundo é / focado os ecossistemas dos três estados do Sul do Brasil, / com setores estratégicos definidos, incluindo Adtech & / Retail Tech, Healthtech, Fintech, Smart Infra e SaaS.

Previsão representative real: `{"discovery": "abstain", "end": 12376, "modality": "undetermined", "segment_id": "segment-0074", "start": 11873, "temporal": "undetermined"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=5; coverage textual=918/926; histograma de descoberta={"abstain": 4, "opportunity_signal": 1}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0070 | [11450,11777) | 0.353132 | 1.000000 | opportunity_signal / investimentos / undetermined |
| segment-0071 | [11779,11838) | 0.063715 | 1.000000 | abstain / undetermined / undetermined |
| segment-0072 | [11840,11852) | 0.012959 | 1.000000 | abstain / undetermined / undetermined |
| segment-0073 | [11854,11871) | 0.018359 | 1.000000 | abstain / undetermined / undetermined |
| segment-0074 | [11873,12376) | 0.543197 | 1.000000 | abstain / undetermined / undetermined |

Campos reais nesses segmentos (não combinar em candidato novo):

- `segment-0071/field[0] fund_stage_expression`: 'Atualmente, os seguintes FIPs estão em estágio de captação:'; witness [11779,11838), página 12; quote trecho: 'Atualmente, os seguintes FIPs estão em estágio de captação:'; suporte qualitativo=supported.

Discordâncias contra referência: ['discovery_label', 'modality']. Isso não determina automaticamente qual lado está correto.

- Revisão AI `M30-I07:segment-0074:discovery:classification`: strong_hypothesis, partial. Há fundo Sul Ventures e estágio de captação na página física 12. O maior fragmento abstém apesar de irmãos emitirem sinal; captação de veículo não é oferta de ticket para startup. Causa (medium): Venture e Capital quebrados entre linhas e nós PDF fragmentam o contexto de modalidade e estágio.
- Revisão AI `M30-I07:segment-0071:field:0`: supported_observation, supported. A frase estabelece FIPs em captação. Não declara abertura de candidaturas para startups; quote e página física 12 resolvem. Causa (high): Regex fund_stage_expression corresponde exatamente ao estágio de captação.

Incerteza restante: Data de criação do PDF e diretório /2026/01/ não comprovam publicação; publication_date permanece null.; Página 12 calculada pelos separadores reais de pdftotext; página inicial sem texto também conta.; Não deduzir captação ativa em outubro a partir de material sem prazo.

## M30-F03

Artefato completo: `per_document/document-010.json`. Fonte: https://www.gov.br/cnpq/pt-br/chamadas/todas-as-chamadas/chamadas-2026/chamada-no-30-2026. SHA original `9d1ff57437c72dc427ed7143aaecbd4c9873f0275ca056adad9ba4bd8939bca3`; texto `78bf8f9bed1539e843a1d71cf59cd22ac84b0b54c6ebc42ff8b1ab0dad05ae13`.

### M30-F03-R1

Referência provisória: `{"discovery_label": "opportunity_signal", "modality": "fomento", "opportunity_label": "uncertain", "review_status": "provisional", "temporal_status": "undetermined"}`; unidade [5732,5917).

Interpretação original: Provisional AI source reading: Current call folder lists MAI/DAI call and attachments but carries no application interval in this document; do not import the interval from other documents.

Fonte congelada (evidências da referência, não labels certificados):

  [5732,5838) página None: Chamada Pública CNPq/CAPES Nº 30/2026 – Programa de Mestrado e Doutorado Acadêmico para Inovação – MAI/DAI

  [5877,5917) página None: chamadapublica30_2026_MAIDAI_2766773.pdf

  [5839,5876) página None: — última modificação 13/10/2026 12h34

Previsão representative real: `null`. Não é identidade canônica nem agregação semântica.

Fragmentação=0; coverage textual=0/185; histograma de descoberta={}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|

Campos reais nesses segmentos (não combinar em candidato novo):

- Nenhum campo extraído nos segmentos com overlap.

Discordâncias contra referência: ['discovery_label', 'modality', 'temporal_status']. Isso não determina automaticamente qual lado está correto.


Incerteza restante: Contextual folder for live MAI/DAI call evidenced separately in F01 and F08; no deadline asserted from this folder.

## M30-N04

Artefato completo: `per_document/document-026.json`. Fonte: https://finep.gov.br/w/mcti-e-finep-anunciam-aporte-de-r-450-milh%C3%B5es-para-114-empresas-das-regi%C3%B5es-norte-nordeste-e-centro-oeste. SHA original `98318fd47d92b74fcdc3a251e5fc79fe6625d92e18c04d43dfc287448a476dce`; texto `2258b3625a2c1dac226c633f0a3aba28eb638bb59505baf7a632ede9901f4ed3`.

### M30-N04-R1

Referência provisória: `{"discovery_label": "unrelated_or_non_actionable", "modality": "fomento", "opportunity_label": "not_opportunity", "review_status": "provisional", "temporal_status": "not_applicable"}`; unidade [2778,5993).

Interpretação original: The additional R$150m is explicitly for 36 proposals ALREADY analyzed and recommended for contracting. Supplementing the budget for existing proposals does not announce a new application window. This is a deliberately difficult monetary-press-release negative.

Fonte congelada (evidências da referência, não labels certificados):

  [2778,3678) página None: MCTI e Finep anunciam aporte de R$ 450 milhões para 114 empresas das regiões Norte, Nordeste e Centro-Oeste / Postado em: / 16/10/26 08:18 / Temas: / Tags: / Compartilhar: / Edital, com volume inicial de R$ 300 milhões, receberá suplementação de 50% para incluir mais projetos das regiões / A ministra Luciana Santos, do Ministério da Ciência, Tecnologia e Inovação (MCTI) anunciou hoje (16), no auditório da Sudene, no Recife (PE), os resultados da segunda rodada da chamada Mais Inovação Brasil Subvenção Econômica, edital da Finep (Financiadora de Estudos e Projetos, agência de inovação vinculada ao MCTI) que direcionava, inicialmente, R$ 300 milhões em recursos não reembolsáveis para empresas de todos os portes que atuam nas regiões Norte, Nordeste e Centro-Oeste. O financiamento irá fomentar 78 projetos inovadores e de risco tecnológico com impacto no desenvolvimento regional e relevância social. A min [trecho; evidência integral no JSON]

Previsão representative real: `{"discovery": "unrelated_or_non_actionable", "end": 3982, "modality": "fomento", "segment_id": "segment-0006", "start": 3055, "temporal": "not_applicable"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=12; coverage textual=3190/3215; histograma de descoberta={"abstain": 6, "opportunity_signal": 3, "unrelated_or_non_actionable": 3}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0000 | [2778,2885) | 0.033281 | 1.000000 | abstain / undetermined / undetermined |
| segment-0001 | [2886,2897) | 0.003421 | 1.000000 | abstain / undetermined / undetermined |
| segment-0002 | [2898,2912) | 0.004355 | 1.000000 | abstain / undetermined / undetermined |
| segment-0003 | [2913,2919) | 0.001866 | 1.000000 | abstain / undetermined / undetermined |
| segment-0004 | [2920,2925) | 0.001555 | 1.000000 | abstain / undetermined / undetermined |
| segment-0005 | [2940,3054) | 0.035459 | 1.000000 | abstain / undetermined / undetermined |
| segment-0006 | [3055,3982) | 0.288336 | 1.000000 | unrelated_or_non_actionable / fomento / not_applicable |
| segment-0007 | [3983,4407) | 0.131882 | 1.000000 | opportunity_signal / undetermined / undetermined |
| segment-0008 | [4408,4730) | 0.100156 | 1.000000 | unrelated_or_non_actionable / fomento / not_applicable |
| segment-0009 | [4731,5019) | 0.089580 | 1.000000 | opportunity_signal / undetermined / undetermined |
| segment-0010 | [5020,5411) | 0.121617 | 1.000000 | unrelated_or_non_actionable / fomento / not_applicable |
| segment-0011 | [5412,5993) | 0.180715 | 1.000000 | opportunity_signal / fomento / undetermined |

Campos reais nesses segmentos (não combinar em candidato novo):

- `segment-0000/field[0] monetary_expression_unresolved`: 'R$ 450 milhões'; witness [2778,2885), página None; quote trecho: 'MCTI e Finep anunciam aporte de R$ 450 milhões para 114 empresas das regiões Norte, Nordeste e Centro-Oeste'; suporte qualitativo=unreviewed.
- `segment-0005/field[0] program_budget`: 'R$ 300 milhões'; witness [2940,3054), página None; quote trecho: 'Edital, com volume inicial de R$ 300 milhões, receberá suplementação de 50% para incluir mais projetos das regiões'; suporte qualitativo=unreviewed.
- `segment-0006/field[0] monetary_expression_unresolved`: 'R$ 300 milhões'; witness [3055,3982), página None; quote trecho: 'A ministra Luciana Santos, do Ministério da Ciência, Tecnologia e Inovação (MCTI) anunciou hoje (16), no auditório da Sudene, no Recife (PE), os resultados da segunda rodada da cha'; suporte qualitativo=unreviewed.
- `segment-0006/field[1] monetary_expression_unresolved`: 'R$ 150 milhões'; witness [3055,3982), página None; quote trecho: 'A ministra Luciana Santos, do Ministério da Ciência, Tecnologia e Inovação (MCTI) anunciou hoje (16), no auditório da Sudene, no Recife (PE), os resultados da segunda rodada da cha'; suporte qualitativo=unreviewed.
- `segment-0006/field[2] beneficiary_expression`: 'A ministra Luciana Santos, do Ministério da Ciência, Tecnologia e Inovação (MCTI) anunciou hoje (16), no auditório da Sudene, no Recife (PE), os resultados da segunda rodada da chamada Mais Inovação B' [expressão abreviada]; witness [3055,3982), página None; quote trecho: 'A ministra Luciana Santos, do Ministério da Ciência, Tecnologia e Inovação (MCTI) anunciou hoje (16), no auditório da Sudene, no Recife (PE), os resultados da segunda rodada da cha'; suporte qualitativo=unreviewed.
- `segment-0008/field[0] borrower_revenue_requirement`: 'R$ 1 milhão'; witness [4408,4730), página None; quote trecho: 'Entre os projetos aprovados inicialmente, 75% são de microempresas (faturamento abaixo de R$ 1 milhão) e empresas de pequeno porte (faturamento de R$ 1 milhão até R$ 4,8 milhões). '; suporte qualitativo=unreviewed.
- `segment-0008/field[1] borrower_revenue_requirement`: 'R$ 1 milhão'; witness [4408,4730), página None; quote trecho: 'Entre os projetos aprovados inicialmente, 75% são de microempresas (faturamento abaixo de R$ 1 milhão) e empresas de pequeno porte (faturamento de R$ 1 milhão até R$ 4,8 milhões). '; suporte qualitativo=unreviewed.
- `segment-0008/field[2] borrower_revenue_requirement`: 'R$ 4,8 milhões'; witness [4408,4730), página None; quote trecho: 'Entre os projetos aprovados inicialmente, 75% são de microempresas (faturamento abaixo de R$ 1 milhão) e empresas de pequeno porte (faturamento de R$ 1 milhão até R$ 4,8 milhões). '; suporte qualitativo=unreviewed.
- `segment-0008/field[3] beneficiary_expression`: 'Entre os projetos aprovados inicialmente, 75% são de microempresas (faturamento abaixo de R$ 1 milhão) e empresas de pequeno porte (faturamento de R$ 1 milhão até R$ 4,8 milhões). A chamada também vai' [expressão abreviada]; witness [4408,4730), página None; quote trecho: 'Entre os projetos aprovados inicialmente, 75% são de microempresas (faturamento abaixo de R$ 1 milhão) e empresas de pequeno porte (faturamento de R$ 1 milhão até R$ 4,8 milhões). '; suporte qualitativo=unreviewed.
- `segment-0009/field[0] geographic_eligibility`: 'Empresas sediadas em 35 cidades das regiões serão beneficiadas pelo edital, sendo que sete cidades serão atendidas pela primeira vez em uma chamada da Finep (Inhumas/GO, Santa Bárbara do Pará/PA, Salg' [expressão abreviada]; witness [4731,5019), página None; quote trecho: 'Empresas sediadas em 35 cidades das regiões serão beneficiadas pelo edital, sendo que sete cidades serão atendidas pela primeira vez em uma chamada da Finep (Inhumas/GO, Santa Bárb'; suporte qualitativo=unreviewed.
- `segment-0009/field[1] beneficiary_expression`: 'Empresas sediadas em 35 cidades das regiões serão beneficiadas pelo edital, sendo que sete cidades serão atendidas pela primeira vez em uma chamada da Finep (Inhumas/GO, Santa Bárbara do Pará/PA, Salg' [expressão abreviada]; witness [4731,5019), página None; quote trecho: 'Empresas sediadas em 35 cidades das regiões serão beneficiadas pelo edital, sendo que sete cidades serão atendidas pela primeira vez em uma chamada da Finep (Inhumas/GO, Santa Bárb'; suporte qualitativo=unreviewed.
- `segment-0010/field[0] proposal_amount_expression`: 'R$ 50 milhões'; witness [5020,5411), página None; quote trecho: 'Todos os projetos estão enquadrados dentro de uma ou mais missões da Nova Indústria Brasil (NIB). Do valor total da chamada, a região Norte recebeu R$ 50 milhões; a região Centro-O'; suporte qualitativo=unsupported.
- `segment-0010/field[1] proposal_amount_expression`: 'R$ 100 milhões'; witness [5020,5411), página None; quote trecho: 'Todos os projetos estão enquadrados dentro de uma ou mais missões da Nova Indústria Brasil (NIB). Do valor total da chamada, a região Norte recebeu R$ 50 milhões; a região Centro-O'; suporte qualitativo=unsupported.
- `segment-0010/field[2] proposal_amount_expression`: 'R$ 150 milhões'; witness [5020,5411), página None; quote trecho: 'Todos os projetos estão enquadrados dentro de uma ou mais missões da Nova Indústria Brasil (NIB). Do valor total da chamada, a região Norte recebeu R$ 50 milhões; a região Centro-O'; suporte qualitativo=unsupported.
- `segment-0010/field[3] proposal_amount_expression`: 'R$ 2 milhões'; witness [5020,5411), página None; quote trecho: 'Todos os projetos estão enquadrados dentro de uma ou mais missões da Nova Indústria Brasil (NIB). Do valor total da chamada, a região Norte recebeu R$ 50 milhões; a região Centro-O'; suporte qualitativo=supported.
- `segment-0010/field[4] proposal_amount_expression`: 'R$ 5 milhões'; witness [5020,5411), página None; quote trecho: 'Todos os projetos estão enquadrados dentro de uma ou mais missões da Nova Indústria Brasil (NIB). Do valor total da chamada, a região Norte recebeu R$ 50 milhões; a região Centro-O'; suporte qualitativo=supported.
- `segment-0010/field[5] proposal_amount_expression`: 'R$ 3,8 milhões'; witness [5020,5411), página None; quote trecho: 'Todos os projetos estão enquadrados dentro de uma ou mais missões da Nova Indústria Brasil (NIB). Do valor total da chamada, a região Norte recebeu R$ 50 milhões; a região Centro-O'; suporte qualitativo=supported.

Discordâncias contra referência: []. Isso não determina automaticamente qual lado está correto.

- Revisão AI `M30-N04:segment-0010:field:0`: confirmed_defect, unsupported. R$ 50/100/150 milhões são alocações regionais do total da chamada. O mesmo parágrafo menciona limites POR PROPOSTA de R$ 2 a 5 milhões. Os três primeiros não são valores por proposta. Causa (high): rules.py:133-153 usa janela +/-120 caracteres e detecta cada proposta posterior à alocação regional.
- Revisão AI `M30-N04:segment-0010:field:1`: confirmed_defect, unsupported. R$ 50/100/150 milhões são alocações regionais do total da chamada. O mesmo parágrafo menciona limites POR PROPOSTA de R$ 2 a 5 milhões. Os três primeiros não são valores por proposta. Causa (high): rules.py:133-153 usa janela +/-120 caracteres e detecta cada proposta posterior à alocação regional.
- Revisão AI `M30-N04:segment-0010:field:2`: confirmed_defect, unsupported. R$ 50/100/150 milhões são alocações regionais do total da chamada. O mesmo parágrafo menciona limites POR PROPOSTA de R$ 2 a 5 milhões. Os três primeiros não são valores por proposta. Causa (high): rules.py:133-153 usa janela +/-120 caracteres e detecta cada proposta posterior à alocação regional.

Incerteza restante: Negative applies to this record as a distinct new/current/future opportunity; it does not erase the existence of the underlying program. No new application is supported by these paragraphs.

## M30-I02

Artefato completo: `per_document/document-016.json`. Fonte: https://criatec4.com/novos-investimentos/. SHA original `ac1efac88dfffde6cd30cb3e79f158e040958ee920f014103b0a1516e74c4663`; texto `7cb851b19c2b9929d1cbe4be53395226801202bece1d4bc53b68746fb2d438cf`.

### M30-I02-R1

Referência provisória: `{"discovery_label": "confirmed_opportunity", "modality": "investimentos", "opportunity_label": "genuine_opportunity", "review_status": "provisional", "temporal_status": "undetermined"}`; unidade [56,940).

Interpretação original: Convite explícito a projeto ou empresa inovadora para submeter projeto e ter o Criatec 4 como sócio confirma mecanismo de candidatura a capital de participação. Não se inferem prazo aberto ou fluxo contínuo da falta de datas.

Fonte congelada (evidências da referência, não labels certificados):

  [56,75) página None: Novos / Investimentos

  [76,231) página None: O fundo Criatec 4 tem como um dos seus principais objetivos o fomento de inciativas inovadoras ligadas ao empreendedorismo em diferentes regiões do Brasil.

  [667,940) página None: Se você tem um projeto ou empresa com produtos e soluções inovadoras e deseja ter o Criatec 4 como sócio, clique na região onde a sua empresa está localizada, preencha o formulário de submissão do seu projeto e em breve você receberá o contato de um representante do fundo.

Previsão representative real: `{"discovery": "abstain", "end": 666, "modality": "undetermined", "segment_id": "segment-0004", "start": 232, "temporal": "undetermined"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=5; coverage textual=880/884; histograma de descoberta={"abstain": 5}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0001 | [56,61) | 0.005656 | 1.000000 | abstain / undetermined / undetermined |
| segment-0002 | [62,75) | 0.014706 | 1.000000 | abstain / undetermined / undetermined |
| segment-0003 | [76,231) | 0.175339 | 1.000000 | abstain / undetermined / undetermined |
| segment-0004 | [232,666) | 0.490950 | 1.000000 | abstain / undetermined / undetermined |
| segment-0005 | [667,940) | 0.308824 | 1.000000 | abstain / undetermined / undetermined |

Campos reais nesses segmentos (não combinar em candidato novo):

- Nenhum campo extraído nos segmentos com overlap.

Discordâncias contra referência: ['discovery_label', 'modality']. Isso não determina automaticamente qual lado está correto.

- Revisão AI `M30-I02:segment-0004:discovery:classification`: strong_hypothesis, partial. Fonte convida projeto/empresa inovadora a ter Criatec 4 como sócio e preencher formulário. Ausência de confirmação no representative é uma omissão de contexto; não prova ausência do instrumento. Causa (medium): Convite e identidade do fundo espalhados entre nós; padrões locais não mantêm título/formulário/descrição juntos.

Incerteza restante: Data e duração da janela não informadas.; Formulário não aberto, executado ou submetido; confirmação documental, não teste operacional.

## M30-I04

Artefato completo: `per_document/document-018.json`. Fonte: https://criatec4.com/aplique-sua-startup/. SHA original `6ba793bf4dfd7e78987723ef9640c50527a137be86ab6a2ba329bf53ecc47f68`; texto `d678f86d497a776a57b65a7112e2e7d24753ccf5078fe63a0a3c51fab5c22c0f`.

### M30-I04-R1

Referência provisória: `{"discovery_label": "confirmed_opportunity", "modality": "investimentos", "opportunity_label": "genuine_opportunity", "review_status": "provisional", "temporal_status": "undetermined"}`; unidade [30,305).

Interpretação original: Instruções explícitas para enviar plano de negócios à análise da equipe confirmam acesso à avaliação de investimento. Investimento é condicionado à tese e não é garantia de aporte. Não há prazo verificável.

Fonte congelada (evidências da referência, não labels certificados):

  [56,77) página None: Aplique a / sua Startup

  [78,305) página None: Escolha a região onde a sede da sua empresa está localizada e preencha os campos abaixo com o seu plano de negócios. Nossa equipe de análise fará a avaliação da oportunidade e, caso se encaixe na tese do fundo, faremos contato.

  [30,55) página None: Aplicar para investimento

Previsão representative real: `{"discovery": "abstain", "end": 305, "modality": "undetermined", "segment_id": "segment-0003", "start": 78, "temporal": "undetermined"}`. Não é identidade canônica nem agregação semântica.

Fragmentação=4; coverage textual=272/275; histograma de descoberta={"abstain": 4}.

| Segmento | Limites | IoU textual | Pureza contra recorte | Descoberta / modalidade / temporal |
|---|---|---:|---:|---|
| segment-0000 | [30,55) | 0.090909 | 1.000000 | abstain / undetermined / undetermined |
| segment-0001 | [56,65) | 0.032727 | 1.000000 | abstain / undetermined / undetermined |
| segment-0002 | [66,77) | 0.040000 | 1.000000 | abstain / undetermined / undetermined |
| segment-0003 | [78,305) | 0.825455 | 1.000000 | abstain / undetermined / undetermined |

Campos reais nesses segmentos (não combinar em candidato novo):

- Nenhum campo extraído nos segmentos com overlap.

Discordâncias contra referência: ['discovery_label', 'modality']. Isso não determina automaticamente qual lado está correto.

- Revisão AI `M30-I04:segment-0003:discovery:classification`: strong_hypothesis, partial. Fonte solicita plano de negócios para avaliação pela tese do fundo. Confirmação é de acesso à avaliação, não promessa de investimento ou janela contínua. Maior bloco abstém. Causa (medium): Nós isolados não contêm simultaneamente vocabulário financeiro e rota de candidatura.

Incerteza restante: Nenhum formulário foi aberto ou submetido.; Sem data, não concluir status open ou continuous; sobreposição de programa com I01 e I02.

## Achados transversais

F01 ainda contém controles Compartilhe/Facebook dentro do intervalo contíguo, embora haja exclusão de blocos e nenhum empréstimo de deadline entre as quatro chamadas observado. Distinguir poluição do span de uma extração financeira/temporal contaminada efetivamente demonstrada. F02/F08 têm recortes de referência que incluem grande prefixo de navegação; baixa coverage textual neles não significa baixa recuperação do conteúdo principal. F05/F06 têm manchetes fora do recorte de referência, mas relacionadas ao mesmo programa: o avaliador final marca isso UNRESOLVED, não atribuição estrangeira provada. F03 tem todos os três blocos do recorte marcados excluded pelo parser: probe documentado em diagnostic_probes.json. I06 mantém estágio do fundo separado de disponibilidade da candidatura; a interpretação announcement versus signal permanece pendente de adjudicação.

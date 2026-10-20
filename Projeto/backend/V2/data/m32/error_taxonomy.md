# Taxonomia diagnóstica m32-error-taxonomy-v1

Somente avaliação offline PROVISIONAL / EXPLORATORY. Não é taxonomia SQL, M1 decisão ou autoridade de publicação. Classes de status: confirmed_defect (contraste fonte/claim reproduzido sob a rubrica explicitada), supported_observation (observação estrutural), strong_hypothesis (causa provável), unresolved_disagreement (necessita adjudicação). Mesmo confirmed_defect é julgamento técnico AI provisório, não assinatura humana nem decisão de produção.

| Código | Significado / cuidado |
|---|---|
| SEGMENTATION_OVER | Mais de um segmento sobrepõe um recorte; precisa contexto para saber se fragmentação é semanticamente nociva. |
| SEGMENTATION_UNDER | Um segmento sobrepõe mais de uma referência; ambiguidade, não fusão autorizada. |
| SEGMENTATION_BOUNDARY | Diferença de fronteira; whitespace sozinho não prova erro de conteúdo. |
| NAVIGATION_CONTAMINATION | Controles/menu presentes no span; separar de campos realmente contaminados. |
| RELATED_STORY_CONTAMINATION | Previews de outros artigos confundidos com contexto do registro. |
| RECORD_ATTRIBUTION | Evidência ligada ao registro errado; fora de um recorte provisório não basta para provar isso. |
| DOCUMENT_ATTRIBUTION | Documento/hash incorreto ou testemunha estrangeira. |
| MODALITY_CONFUSION | Empréstimo/subvenção/equity confundidos; unknown não é classe errada presumida. |
| FINANCIAL_ROLE_CONFUSION | Orçamento/ticket/faturamento/capital do fundo/compromisso de cotista trocados. |
| FINANCIAL_VALUE_ERROR | Literal financeiro incorreto, não simples ausência de normalização. |
| TEMPORAL_ROLE_CONFUSION | Data de publicação/resultado/abertura/deadline trocada. |
| TEMPORAL_AVAILABILITY_INFERENCE | Janela/status inferido sem suporte ou no estágio errado. |
| GEOGRAPHIC_ROLE_CONFUSION | Local de sede/execução tomado por elegibilidade. |
| ORGANIZATION_ROLE_CONFUSION | Emissor, gestor, beneficiário e financiador intercambiados. |
| FUTURE_SIGNAL_CONFUSION | Fundo/evento futuro confundido com chamada, ou sinal/anúncio sem discriminar compromisso. |
| OPPORTUNITY_EXISTENCE_CONFUSION | Nível de descoberta incompatível com escopo/acesso; desacordo de label não prova defeito sozinho. |
| UNSUPPORTED_INFERENCE | Informação acrescentada sem testemunha suficiente. |
| EVIDENCE_LOCATOR_INVALID | Locator/hash/quote/página/unidade estrutural não resolve. |
| EVIDENCE_SEMANTIC_MISMATCH | Locator resolve, mas não sustenta papel/classificação atribuída. |
| EXTRACTION_OMISSION | Informação suportada não representada; diferenciar do fora de escopo. |
| EXCESSIVE_ABSTENTION | Abstenção plausivelmente evitável com contexto realmente presente, não toda abstenção. |
| REFERENCE_AMBIGUITY | Rubrica ou fonte não permite adjudicação segura. |
| REFERENCE_POSSIBLE_ERROR | Há motivo fonte/rubrica para questionar anotação; jamais editar automaticamente. |
| CONTRACT_UNSUPPORTED | Campo/papel fora da capacidade implementada/aprovada; não marcar automaticamente como incorreto. |

## Categorias de comparação de campos

MATCH: mesmo papel e literal no registro; apenas candidato a concordância, não entailment aprovado.
PARTIAL: literal relacionado/papel alias explícito; preservar qualificadores/estágios faltantes.
ROLE_ERROR: mesmo literal em papéis semanticamente distintos; candidato de regra, exige contexto.
VALUE_ERROR: valor não sustentado pela própria testemunha; input deve ser recusado antes de medir quando inválido.
ATTRIBUTION_ERROR: valor em outro registro explicitamente delimitado, não só fora de um recorte.
MISSING: nenhum campo correspondente dentro do escopo M31; não equivale abstenção explícita.
ABSTAINED: declínio explícito de um campo; M31 não emite esse contrato, portanto zero não é falha de contagem.
UNRESOLVED: escopo não implementado, valores diferentes não comparáveis, referência ambígua ou fronteira insuficiente.

O ledger referencia case_id, document_id, record_id/segment_id, locador/quote, severidade, esperado/observado, confiança de causa e ação. Itens gerados só de desacordo ficam unresolved_disagreement. Revisão qualitativa dos campos extraídos é separada das 127 comparações de referência: um campo extra pode ter papel incorreto sem existir um slot de referência com aquele mesmo nome. Não ocultar esse efeito de denominador.

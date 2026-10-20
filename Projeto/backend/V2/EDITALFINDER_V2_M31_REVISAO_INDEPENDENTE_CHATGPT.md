# EditalFinder V2 — Revisão técnica independente da M3.1 (run-v2)

**Escopo:** pacote `V2.tar(20261019-210930).gz`, código final de extração offline e artefatos congelados. **Parecer: READY limitado ao baseline experimental offline; NÃO READY para produção, disponibilização automatizada de oportunidades, publicação, promoção, ponte de autoridade M1/M2 ou métricas certificadas.**

## 1. Procedimentos independentes executados

Ambiente de revisão: Python 3.13.5, Pydantic 2.13.5, pytest 9.0.2. O ambiente do projeto documenta Python 3.11.16 / Pydantic 2.14.1; resultados entre ambientes não constituem certificação de equivalência universal.

- Suíte completa: `PYTHONPATH=src python -m pytest -q -p no:cacheprovider` — **2.134 passed in 32.92s** (execução completa independente, exit 0).
- Novos testes: `PYTHONPATH=src python -m pytest -q -p no:cacheprovider tests/test_m31_extraction.py` — **39 passed in 2.63s**.
- `predictions.json`: digest SHA-256 conferido com `run-v2/freeze.json`: `c4c32df2850ac101b4389ae1d91c643f87d1bc129a45e7b96f8586c3fc9ee388`.
- Cada `DocumentOutcome` dos 28 documentos foi reconstruído com `model_validate_json()` e submetido a `verify_evidence()` após leitura real do documento congelado. **28/28 processados e verificados**.
- Reexecução independente de `run(data/m3, '2026-10-19')`: todas as representações JSON de documentos coincidiram exatamente com as previsões congeladas (comparação estrutural).
- Comparação de integridade com o pacote M3.0 anterior (`V2.tar(20261019-195049).gz`): **108 arquivos do corpus idênticos por SHA-256, zero adicionados/removidos/modificados**. O inventário inicial M3.1 confirma separadamente a integridade dos 107 arquivos sob `data/m3/` listados nele. Parte de outras entradas do inventário está ausente do tar de distribuição e não foi tomada como modificação de projeto.
- Não executei Ruff nem mypy neste ambiente porque suas CLIs não estão instaladas aqui. O relatório enviado contém resultados verdes de ambas ferramentas sob o ambiente do projeto; isso **não** equivale a reprodução independente dessas ferramentas.

## 2. Reproduções adversariais da versão final

Todos os exemplos abaixo foram testados contra resultados reais `M30-F01` reconstruídos do `run-v2`, sem alterar o código:

1. Aumentar os limites do último segmento da F01 — **REJEITADO**, `segment_structure_mismatch`.
2. Inserir no último segmento testemunha pertencente ao segmento anterior — **REJEITADO** no contrato Pydantic de ownership.
3. Inventar o valor original de um campo preservando sua testemunha antiga — **REJEITADO** no contrato de relação literal/testemunha.
4. Substituir o texto de uma testemunha preservando seus offsets — **REJEITADO**, `evidence_quote_mismatch`.
5. Fronteira corrigida da última chamada F01: `segment-0011` começa em **8213** e termina em **9577**, e não inclui `Refazer a busca`; na revisão antiga o limite era **13344**. A documentação do projeto demonstra também a reprodução da falha de empréstimo de provas antes da correção.

**Limite indispensável:** a verificação de evidência é **estrutural**, não um classificador semântico autenticado. Em testes independentes, mudar uma previsão de `opportunity_signal` para `confirmed_opportunity` mantendo seus campos, contexto e testemunhas internamente consistentes passou pelo verificador em `M30-F01`, `M30-C07` e `M30-I06`. Isso não constitui uma nova falha de isolamento: a validação nunca prometeu executar novamente a função de classificação nem certificar as implicações semânticas. Entretanto, demonstra que **um resultado recebido de outra origem não deve adquirir autoridade apenas porque tem locadores válidos**. A integridade do recibo SHA-256 também não é autenticação de emissor.

## 3. Resultados de extração e qualidade semântica

- 28 documentos processados, 0 falhas operacionais.
- 1.649 segmentos passivos, **não** 1.649 oportunidades.
- 332 campos textuais extraídos; 1.413 segmentos resultaram em `abstain`.
- Distribuição: `confirmed_opportunity=11`, `opportunity_signal=206`, `unrelated_or_non_actionable=19`, `abstain=1413`; nenhuma previsão `announced_future_opportunity` nesta execução.
- 32 das 33 unidades anotadas tiveram sobreposição com algum segmento; **0 fronteiras exatas**; 26 referências foram sobresegmentadas.
- 27 coincidências exatas de papel e valor em 127 campos anotados. **Isso não representa precisão, recall ou F1 certificados**, nem é porcentagem de campos corretamente interpretados em produção.
- Nove rótulos de referência continuam `uncertain`; todos os 33 permanecem `provisional`.
- Há forte fraqueza na granularidade de segmentação, sobretudo fora das listas com cabeçalho `Chamada`, e na interpretação de oportunidades de crédito/investimento. Em `M30-I06`, o anúncio de fundo futuro foi conservadoramente rotulado `opportunity_signal`, com disponibilidade indeterminada: não se fabricou janela de candidatura; a divergência entre sinal e anúncio futuro continua relevante para a evolução do método.
- `M30-C07-R1` e `M30-N01-R1` mostram sinais extraídos de conteúdos negativos/proximamente relacionados, requerendo análise semântica adicional antes de notificação automatizada.

## 4. Revisão v1: rastreabilidade e honestidade de estado

O relatório `docs/v2/M31_INDEPENDENT_REVIEW.md` da primeira revisão AI permanece **FAIL**, com dois problemas HIGH no código v1. A solução v2 foi criada depois, e o revisor v1 não aprovou a nova versão. Minha revisão independente da versão v2 rejeitou os ataques direcionados descritos acima e reproduziu as verificações básicas; ela **não** certifica a ausência de todos os ataques possíveis nem a veracidade das previsões.

## 5. Recomendações para M3.2

1. **Segurança e teste de fronteiras:** preservar testes de não compartilhamento de evidências e adicionar casos novos de HTML com estrutura diferente (sem redesenho da camada de confiança sem reproduzir defeitos).
2. **Segmentação por unidade semântica:** melhorar a associação entre chamada, programa, notícia, parágrafo e seus campos, reduzindo a sobresegmentação, sem inferir que 1 DOM node = 1 instrumento.
3. **Análise de erros por modalidade:** crédito e investimento sofrem alta abstenção em vários casos do ledger; priorizar exemplos de notícias futuras, seleção de gestora, captação de fundo e crédito concedido versus crédito disponível.
4. **Distinção de estágios:** evidência de programa futuro, candidatura futura, fundo em captação e janela aberta são conceitos diferentes; manter disponibilidade indeterminada quando não comprovada.
5. **Proveniência semântica:** localizar a frase exata não prova que papel financeiro, instituição, temporalidade ou elegibilidade inferidos estejam certos. Uma etapa de verificação semântica separada será necessária antes de produzir alertas acionáveis.
6. **Avaliação séria:** manter os resultados como exploratórios no corpus exposto durante desenvolvimento; montar conjunto independente rotulado por revisores humanos antes de publicar estatísticas de precisão/recall.
7. **Sem integração autorizada:** nenhuma promoção, fusão de oportunidades, persistência ou ponte autenticada M1/M2 nesta aprovação.

## 6. Decisão

**READY para encerrar a M3.1 como implementação e baseline experimental offline, com revisão técnica independente da versão final dentro dos limites listados.** A M3.2 pode começar como fase de **avaliação e melhoria experimental**, não como deploy ou operação autônoma de descoberta. O sistema ainda não está pronto para publicar oportunidades ou alertas por conta própria.

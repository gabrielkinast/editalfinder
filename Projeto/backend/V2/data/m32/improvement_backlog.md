# Backlog M3.3 — propostas, NÃO implementadas

Evidência: evaluation_results.json, semantic_reviews.json, diagnostic_probes.json e case_studies.md. Todos os rótulos/juízos são PROVISIONAL / EXPLORATORY. Priorização por dano semântico e generalização, não por aumento do número de testes ou concordância com 33 rótulos. Nada autoriza iniciar M3.3, alterar M1/M2 ou publicar.

## B01 — P0: associação de quantias a papéis e cláusulas

Problema: janela +/-120 toma frase posterior de proposta e aplica a alocações regionais; contexto de meta do fundo contamina compromisso de cotista.
Casos: N04 segment-0010 campos 0/1/2; I05 segment-0019 campo 2. Source/claim e offsets reproduzidos no ledger; locadores são válidos.
Benefício: evitar orçamento regional/ticket e compromisso/capital total incorretos em textos novos.
Efeitos colaterais: separar por frase cegamente perde anáforas e sujeito compartilhado; preservar papéis não resolvidos quando associação insuficiente.
Componentes: rules/extração de expressões e contexto local; manter witnesses originais por cláusula/valor.
Contratos: nenhum M1/M2. Possível evolução versionada do DTO de extração para qualifier e relação de papel; não normalizar equity/FX por fora dos contratos.
Regressões: várias quantias em uma frase/parágrafo, faixas, cotistas, regional vs por proposta, mesma cifra em papéis legítimos distintos, transferência cross-record proibida.
Dificuldade: média/alta.
Verificação: corrigir quatro contraexemplos sem transformar números em tickets ou mover evidências; validar em fixtures novas de layout/vocabulário e reexecutar diagnóstico completo, mantendo abstention/unknown.

## B02 — P0: contexto de transação concluída versus acesso

Problema: notícias de transação concluída podem gerar sinais como nova descoberta, apesar de guardas locais.
Casos: C07-R1 signal no maior parágrafo, non-actionable quando apenas o contexto do mesmo registro é restaurado; N01 Renault aprovado/veículo futuro. A decisão de relevância ampla requer adjudicação: uma notícia concluída pode continuar útil como pista de programa, sem provar oferta nova.
Benefício: tornar produto explícito sobre sinal informativo versus acesso para novo requerente.
Efeitos colaterais: bloquear notícia inteira eliminaria C07-R2 e anúncios legítimos; distinguir registros e nível de descoberta.
Componentes: análise de papel documental/record context e detector; não regra por gênero/domínio.
Contratos: manter separados classe de descoberta e status de aplicação; nenhuma decisão M1.
Regressões: transação e programa na mesma página; evento futuro do beneficiário; resultados/suplementação; notícia anuncia chamada real; guardas sem depender de nome próprio.
Dificuldade: média/alta.
Verificação: zero promoção de transação a chamada aberta nos contraexemplos, sem apagar programa vizinho; revisão humana da definição de signal para notícias concluídas antes de metas semânticas.

## B03 — P1: contexto hierárquico, whitespace e record units

Problema: um DOM data node não é uma oportunidade; campos e acesso ficam separados. Pureza 1 contra referência ampla pode coexistir com IoU baixo e fragmentação alta.
Casos: C01/C02/C04, I02/I04, I07; C04 tem 87 fragmentos. Probe I02 continua abstain com contexto completo contendo newline e só muda ao achatar whitespace; I04 não muda mesmo com contexto completo/achatado. São fatores diferentes.
Benefício: contexto suficiente sem empréstimo de irmãos, generalizável a layouts novos.
Efeitos colaterais: juntar demais recria bugs de isolamento v1; normalização do texto não pode invalidar offsets. Usar representação auxiliar com mapa reverso, não sobrescrever visão congelada.
Componentes: reader/structure, contexto de classificação; DTO com fronteiras e ownership explícito.
Contratos: talvez schema versionado do extrator; nenhum contrato M1/M2 precisa mudar nesta proposta.
Regressões: containers aninhados, títulos duplicados, main headers, estruturas sem headings, inline vs newline, múltiplos programas, related stories, PDF com quebra de linha física, expansão maliciosa de bounds.
Dificuldade: alta.
Verificação: novos layouts com ownership preservado; reduzir fragmentação semanticamente nociva, não otimizar exact boundary/33 IDs; manter todos os links diagnósticos e ausência de merge automático.

## B04 — P1: estágios financeiros e públicos de investimento

Problema: gestor, fundo futuro, captação do veículo, startup avaliada e janela de submissão são estágios diferentes. future_access no baseline é mais estreito que anúncio futuro de instrumento.
Casos: I05/I06/I07 e acesso real I02/I04; I06 signal versus announced_future é disputa de rubrica, não data de inscrição perdida.
Benefício: descobrir iniciativas futuras sem notificar uma candidatura inexistente.
Efeitos colaterais: predizer future por toda linguagem futura gera falsos abertos/eventos; diferenciar temporalidade de funding, operação, produto e candidatura.
Componentes: detector/role graph de estágio e público; avaliação por estágio separada.
Contratos: proposta de extração versionada de estágio/beneficiário/rota, sem inventar semântica de investimento em contratos financeiros M2.
Regressões: gestor selecionado, LP capta, programa lançado sem application, janela futura explícita, startup form, aportes concluídos, híbridos crédito/equity.
Dificuldade: alta.
Verificação: preserve unknown para janela em I05–I07; detectar convites sustentados em fixtures inéditas; adjudicar a fronteira signal/future antes de afirmar ganho.

## B05 — P1: qualificadores, ranges e papéis de datas

Problema: MONEY perde até; publicação extraída só como dia perde hora; datas por extenso e etapas distribuídas não estabelecem disponibilidade.
Casos: C01 teto R$150m, I05/I06 meta até R$250m/500m; F05/F06 deadlines por extenso; F07 cronograma PDF. Sem inferir que perda de precisão seja valor numericamente errado.
Benefício: reter significado financeiro e temporal para consumidores futuros.
Efeitos colaterais: regex gulosa pode capturar outro número/data; não normalizar data sem ano, cutoff ou timezone.
Componentes: field expression extraction e papéis temporais, mapas de spans.
Contratos: evoluir extração se necessário; respeitar normalizadores aprovados, sem FX, novos formatos de principal equity ou precedência inventada.
Regressões: até/a partir de/entre, média versus limite, duas quantias iguais, publicação/retificação/resultado/abertura, prazo no próprio dia, timezone ausente, fases internacional/nacional.
Dificuldade: média/alta.
Verificação: conservar qualifiers e relacionamentos em testemunhas; ampliar expressão sem ampliar autoridade; datas conflitantes continuam unresolved.

## B06 — P2: papéis organizacionais e cobertura seletiva de campos

Problema: realizada pelo não prova financiador; header Quem pode solicitar não é público efetivo; 45 campos de referência estão fora do escopo implementado, não erros automáticos.
Casos: F01/CNPq-CAPES, C01/C02/C04, I05 BNDESPAR/Finep, I06 gestora, títulos de notícia F05/F06 fora do recorte anotado.
Benefício: diminuir atribuições de entidade e audience genéricas, sem inferir elegibilidade por país/domínio/moeda.
Efeitos colaterais: exigir nome normalizado pode perder descrição útil; não fundir entidades por sigla/contexto.
Componentes: rules/contexto de campos e declaração pública de escopo.
Contratos: nenhum M1/M2; papéis originais não autenticados e granularidade de extração explícita.
Regressões: publisher/funder/manager/beneficiary diferentes, lista de tomadores, sede/execução/eligibilidade, título da matéria versus nome do programa.
Dificuldade: média.
Verificação: campo audience não contém só cabeçalho; funded-by não derivado de publisher; diferenças de título vão a revisão, não falso cross-record automático.

## B07 — P2: seleção de conteúdo e ruído estrutural

Problema: F03 perde 185 caracteres de título/link porque todos os blocos foram excluded; F01 ainda tem share controls no intervalo contíguo. F02/F08 têm referências iniciando no prefixo de navegação: coverage baixa não mede perda de conteúdo principal.
Benefício: maior utilidade de spans e interpretação correta do benchmark sem maximizar coverage de menus.
Efeitos colaterais: admitir todo header/sidebar reintroduz navegação e related stories; não inferir conteúdo dos PDFs não congelados.
Componentes: leitor/seleção estrutural, diagnóstico de exclusão e comparabilidade de fronteiras.
Contratos: preservar hash/visão e offsets, sem alterar referência congelada; revisão de referência só nova release autorizada.
Regressões: main article header versus global header, preview de anexos, cookies, share nodes internos, related link com prazo de outra chamada.
Dificuldade: média.
Verificação: evidência de landing page preservada como sinal sem fabricar anexo; manter filtros de navegação e isolamento.

## B08 — P0 de governança, antes de métricas públicas

Problema: 33 labels provisórios expostos e juízos AI não são referência humana nem holdout.
Casos: I06 nível de confirmação, F02/F08 fronteiras, notícias de negócios e candidatos da fila de revisão.
Benefício: medidas semanticamente interpretáveis e estimativa fora do piloto.
Efeitos colaterais: revisão consome tempo; nunca editar release antiga para subir score.
Componentes: protocolo de anotação, seleção temporal/source-family de conjunto novo, adjudicação autorizada; manter pipeline offline.
Contratos: nova release de referência/governança, não fake ReviewAttestation M1.
Regressões: binding de hashes/escopo, desacordos preservados, uncertain separado, um revisor não vira autoridade por flag JSON.
Dificuldade: alta/organizacional.
Verificação: dois julgamentos humanos independentes e autorização real segundo protocolo, antes de referência certificada; corpus não visto por desenvolvedor para generalização. Nenhuma implementação/autorização de aquisição ou revisão humana é simulada nesta M3.2.

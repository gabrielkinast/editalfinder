# EditalFinder V2 — Revisão técnica independente da M2.3b

**Parecer:** `READY`, **somente para o escopo offline, conservador e não autorizador**, com ressalvas explícitas de qualidade e de cobertura semântica. **Não** é aprovação para produção, persistência, merge, autenticação ou publicação.

**Pacote examinado:** `V2.tar(9).gz`, fornecido pelo usuário em 18/10/2026. O TAR foi inspecionado quanto a caminhos absolutos, escapes por `..` e entradas não regulares; nenhuma entrada insegura foi encontrada. Arquivos de origem foram analisados sem modificar o projeto do usuário. Provas e benchmarks foram executados com dados sintéticos do próprio pacote e alterações em memória.

## 1. Testes realmente executados nesta revisão

Ambiente independente: Python **3.13.5**, Pydantic **2.13.5**, pytest **9.0.2**. Isto complementa, mas não certifica, o ambiente Python 3.11.16 / Pydantic 2.14.1 informado pelo Hermes.

```bash
PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -p no:cacheprovider -q
# 1691 passed in 18.40s

PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -q -p no:cacheprovider \
  --ignore=tests/test_m23b_consistency.py --ignore=tests/test_m23b_boundaries.py
# 1517 passed in 12.92s
```

Ruff e mypy **não foram reexecutados** neste ambiente: seus executáveis não estavam disponíveis. De acordo com o relatório do Hermes, mypy passou nos 28 arquivos de origem. O Ruff **global não passa** por sete ocorrências e formatação no `tests/m23_fixtures.py`; os gates excluindo somente esse arquivo passaram no ambiente do Hermes. Portanto, não se deve afirmar que o lint global está verde.

## 2. Inspeção dos contratos e da integração

Examinados diretamente: `integration_consistency.py`, `integration.py`, `integration_models.py`, `integration_budget.py`, `semantic_common.py`, os normalizadores relacionados, os novos testes e `docs/v2/INTEGRATION_CONSISTENCY_M23B.md`.

O subsistema compõe os relatórios existentes e registra observações ordenadas usando `DomainClaimReference(domain, claim_index)`; não converte observações em decisões `ACCEPTED`/`REJECTED`. O envelope de `IntegrationReport` inclui o corpo integral, e a validação do relatório reexecuta as operações e compara as saídas esperadas. `promotable` continua sempre `False`.

Aspectos positivos confirmados nos fluxos examinados:

- Comprovação da unidade de origem e do papel semântico antes de emitir evidências locais.
- Índices de claims qualificados por domínio, sem reutilizar índices ambíguos.
- Ausência de fusão automática mesmo com resolução contextual `exact_match`.
- Nenhum uso de relógio externo, LLM, acesso a rede, banco ou políticas implícitas nessa camada.
- Classes separadas para `contradiction`, `potential_conflict`, `insufficient_information` e `no_conflict_detected`.
- Crédito, fomento e instrumentos híbridos não são automaticamente declarados inconsistentes; venture capital/equity fora do catálogo não ganham categoria inventada.

## 3. Probes independentes adicionais

### 3.1 Casos de domínio e round-trip

Foram executados os fixtures `grant`, `credit`, `investment` e `ambiguous` como integrações completas, com reconstrução JSON e igualdade entre relatórios. Todos passaram.

Diagnósticos observados:

- `grant`: `consistency_no_conflict_detected` (significa apenas ausência de conflito detectado pelas regras existentes).
- `credit`: `consistency_credit_terms_unrepresented` (sem inferir condições financeiras).
- `investment`: `consistency_taxonomy_unsupported` (sem fallback inventado).
- `ambiguous`: prazos potenciais, retificação sem precedência e classificações/interpretações não resolvidas foram preservados.

### 3.2 Adulteração de relatórios

Em um relatório com faixa financeira reversa válida como fixture, foram alterados isoladamente: código do diagnóstico, remoção completa da lista, inclusão de diagnóstico contraditório e `semantic_role` de uma prova. Os quatro casos foram **rejeitados** na validação por JSON.

A remoção **integral** do audit (`audit=None`) foi **aceita após recomputação completa**, conforme contrato explícito de nova avaliação local; isso NÃO equivale a validar um envelope histórico ausente. Em contraste, um envelope contendo **somente** `report_digest` foi rejeitado pelo requisito de metadados obrigatórios. Esse comportamento está coerente com a correção M2.3a.2.

### 3.3 Evidências entre registros e comparação de identidade

Foi criado lote com dois registros, cada qual com sua `DocumentUnit`. Ao transplantar as afirmações normalizadas de **taxonomia** ou **finanças** do registro B para o candidato A, a integração retornou `consistency_claim_evidence_unavailable`, com evidência vazia, sem emitir a classificação não suportada ou contradição da faixa de B como pertencente a A.

Em outro ensaio, solicitou-se explicitamente a comparação de identidade entre os dois candidatos: a resolução contextual retornou `exact_match` para os identificadores fornecidos, mas o lote continuou com **dois candidatos distintos** e nenhum deles recebeu autorização de promoção. Isto confirma separação prática entre comparação de identidade e merge.

## 4. Ressalvas e recomendações

1. **Cobertura semântica estreita e proposital.** A única contradição definitiva implementada está associada a *endpoints reversos da mesma expressão financeira*, já identificados pelo normalizador. Muitas relações entre domínios apenas produzem `insufficient_information` ou `potential_conflict`. Não interpretar `READY` como motor completo de consistência entre fomento, crédito e investimentos.
2. **A origem das declarações ainda precisa de confiança externa.** Formato numérico, papel das afirmações, namespaces e classificações declarados pelo adaptador não são autenticados por este subsistema.
3. **O contrato não dispõe de vínculos tipados de fase, tranche, instrumento financeiro e entidade jurídica.** Portanto, o motor corretamente se abstém de afirmar conflitos mais fortes, mas não detectará necessariamente incompatibilidades reais entre essas entidades.
4. **Taxonomia de investimento incompleta.** As categorias existentes não descrevem todos os instrumentos de venture capital/equity; `credit_principal`, juros, carência, amortização, participação societária e valuation continuam fora do contrato financeiro normalizado.
5. **Ruff global pendente.** O fixture `tests/m23_fixtures.py` tem sete apontamentos reportados; recomenda-se corrigir com autorização explícita numa etapa de higiene limitada, sem alterar as expectativas de teste.
6. **Custo e limites de transporte.** A admissão de 64 MiB é conservadora e pode recusar relatórios menores; não constitui limite de RSS nem substitui limites sobre bytes JSON antes do parsing. A verificação integral recompõe o pipeline e custa tempo adicional.
7. **Validação real ainda não realizada.** Não há métricas de precisão/recall para páginas de bancos de desenvolvimento, agências de fomento, chamadas de investimento e outros documentos externos; a confiança em produção depende de um conjunto ouro anotado por humanos e de políticas por fonte.

## 5. Parecer

**`READY` para encerrar a M2.3b como componente offline e conservador.** Não foram reproduzidos defeitos bloqueantes nos testes examinados. Esse parecer é independente do relatório do Hermes, mas baseado em um conjunto finito de cenários sintéticos; não é prova exaustiva nem auditoria profissional humana formal.

**Próximo passo recomendado:** M2.3c — fluxo end-to-end com snapshots congelados, relatórios de extração simulada e cenários representativos de **fomento, crédito e investimento**, incluindo falsos positivos (notícias, resultados e comunicados); a seguir M2.3d, auditoria adversarial de ponta a ponta. Manter promoção, persistência, crawling e merge desligados. Resolver separadamente a higiene do fixture antes de exigir Ruff global verde.

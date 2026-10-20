# EditalFinder V2 — Parecer independente M2.3a.2

**Decisão:** **READY para o escopo offline da correção de metadados do `IntegrationAudit`**, sem autorização para produção, persistência, merges ou promoção.  
**Base:** `V2.tar(8).gz`, recebido em 18/10/2026.  
**Revisão:** inspeção estática, comparação com `V2.tar(7).gz`, suíte completa e reproduções independentes.

## 1. Escopo e ambiente

- Python **3.13.5**, Pydantic **2.13.5**, pytest **9.0.2**.
- `PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -q -p no:cacheprovider` → **1.517 passed in 9.30s**.
- O Hermes informou execução adicional em Python 3.11.16 / Pydantic 2.14.1, além de mypy e Ruff escopados. **Ruff e mypy não estavam instalados no ambiente desta revisão, portanto não foram reexecutados independentemente.**
- O pacote inclui o novo `tests/test_m23_audit_metadata.py`, com 80 testes; a baseline declarada era de 1.437.

## 2. Verificação do diff

A comparação SHA-256 entre os membros regulares dos dois arquivos TAR identificou **uma única mudança em arquivo Python de produção**:

- `src/editalfinder_v2/domain/integration_models.py` — mudança nos requisitos e geração de `IntegrationAudit`.

Adicionados:

- `tests/test_m23_audit_metadata.py`;
- `docs/v2/INTEGRATION_AUDIT_REPROCESSING.md`;
- `EDITALFINDER_V2_M23A1_AUDIT_METADATA_RESULTADOS.md`.

Observação de empacotamento: o documento `EDITALFINDER_V2_M23A1_RESULTADOS.md` que aparecia no pacote anterior não aparece no novo TAR. **Isso não prova exclusão no working tree** e não indica alteração no código; verificar se o relatório histórico continua arquivado localmente.

## 3. Achado corrigido

Na versão anterior, `IntegrationAudit` preenchia automaticamente `output_budget_version`, `algorithm`, `hash_version`, `limits_version` e `schema_version` herdado. Portanto, um envelope recebido contendo apenas `report_digest` era aceito, mesmo sem declarar as versões.

Na versão atual, todos os seis campos são obrigatórios:

- `schema_version`;
- `output_budget_version`;
- `report_digest`;
- `algorithm`;
- `hash_version`;
- `limits_version`.

O modelo local de relatório preenche os metadados **explicitamente ao gerar nova avaliação**, não ao completar um envelope recebido. Os valores são comparados ao envelope esperado e os resultados do pipeline são recomputados.

### Reproduções independentes

1. Remoção de cada um dos seis campos, em `model_validate` e `model_validate_json`: **12/12 rejeições com erro `missing` no campo exato**.
2. Envelope contendo somente `report_digest`: **rejeitado**, com cinco campos ausentes.
3. Metadados contraditórios (digest adulterado, algoritmo, schema, limites e versão de orçamento): **5/5 rejeições**.
4. Round-trips dos relatórios de **fomento, crédito, investimento e ambiguidade**: **4/4 relatórios idênticos**.
5. Os relatórios completos mantiveram os resultados e a versão de orçamento esperados; cenário de 32 candidatos ainda retorna `OperationalError(code='integration_output_budget_exceeded')`.

## 4. Reprocessamento histórico

`docs/v2/INTEGRATION_AUDIT_REPROCESSING.md` distingue dois procedimentos:

- **Validação estrita de envelope recebido:** metadados presentes são exigidos integralmente e conferidos.
- **Nova avaliação de entrada histórica:** preserva o registro original e seu envelope como recebido; extrai `input` e chama `integrate()` usando a política atual; registra `original_policy_inferred=False` e `historical_outputs_verified=False`.

Essa distinção está correta para a milestone. O exemplo de reprocessamento é exercitado nos testes, mas **não é um parser de transporte, verificador de autenticidade ou mecanismo de persistência**.

## 5. Ressalvas não bloqueantes e próximas fronteiras

1. `IntegrationReport` permite `audit` ausente ou `None` para **gerar uma avaliação local nova**, após reexecutar o pipeline. Reproduzi as duas rotas: ambas geram um novo envelope válido. **Isso é comportamento deliberado e documentado, não um bypass da correção.** Entretanto, uma futura API que aceite *relatórios históricos* deve exigir audit presente, em vez de expor indistintamente a rota de nova avaliação.
2. Hashes SHA-256 verificam consistência, **não** autenticidade da fonte, do revisor ou autorização para publicar; `promotable=False` permanece.
3. O orçamento de 64 MiB é uma estimativa conservadora de trabalho/saída, **não** teto de RSS; limites de tamanho de transporte antes do `json.loads` permanecem pendentes.
4. O relatório do Hermes registra sete problemas antigos de Ruff e uma pendência de formatação em `tests/m23_fixtures.py` (fora da correção). A revisão atual não reexecutou Ruff/mypy, pois as ferramentas não estavam disponíveis.
5. Não há auditoria em documentos reais, nem certificação de matriz Python 3.11–3.14 ou de carga em produção.

## 6. Conclusão

**READY — apenas para o escopo offline da M2.3a.2.** A omissão parcial de metadados recebidos foi corrigida e reproduzi a rejeição de todas as seis ausências. Não identifiquei regressão bloqueante no escopo analisado. É razoável iniciar **M2.3b — Consistência semântica entre domínios**, preservando o bloqueio de publicação, persistência e merge automático.

**Não interpretamos esta aprovação como segurança de produção ou autenticação de relatórios históricos.**

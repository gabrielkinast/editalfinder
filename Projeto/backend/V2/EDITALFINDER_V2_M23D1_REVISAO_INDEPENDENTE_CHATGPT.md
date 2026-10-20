# EditalFinder V2 — Parecer independente da M2.3d.1

**Status: READY apenas para a correção offline F01/F03.** Revisão baseada no arquivo recebido `V2.tar(20261019-005555).gz`, com comparação ao pacote da auditoria anterior `V2.tar(20261019-002226).gz`. A conclusão não autoriza operação em produção, crawler, persistência, merge ou promoção de oportunidades.

## 1. Método e ambiente

- Arquivos TAR inspecionados sem executar conteúdo durante a extração; módulos Python foram executados depois apenas em ambiente local isolado, sem acesso a Supabase, rede, Legacy ou migrations.
- Ambiente independente: **Python 3.13.5, Pydantic 2.13.5, pytest 9.0.2**. O responsável pela implementação relatou Python 3.11.16 e Pydantic 2.14.1.
- Comando independente: `PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 pytest -p no:cacheprovider -q`.
- **Resultado: 2.000 testes aprovados em 30,43 s.**
- Ruff e mypy não estavam instalados no ambiente independente. Seus gates globais foram **informados como aprovados pelo Hermes**, mas não foram repetidos aqui.

## 2. Mudanças efetivas entre os pacotes

Comparando os hashes dos arquivos comuns, as fontes alteradas restringem-se a:

- `src/editalfinder_v2/domain/models.py`
- `src/editalfinder_v2/domain/identity_models.py`
- `src/editalfinder_v2/domain/semantic_common.py`
- `src/editalfinder_v2/domain/m22b_common.py`
- `docs/v2/INTEGRATION_AUDIT_REPROCESSING.md`

Arquivos novos: `tests/test_m23d1_utc_boundaries.py`, `tests/test_m23d1_audit_metadata.py`, `docs/v2/M23D1_HARDENING_EVIDENCE.json`, `EDITALFINDER_V2_M23D1_RESULTADOS.md`. O relatório de auditoria M2.3d anterior constava no TAR precedente, mas não foi incluído no TAR novo. Essa diferença no **pacote** não demonstra sua exclusão do repositório local.

## 3. F01 — overflow na conversão UTC

Nos validadores `RawSnapshot.utc_timestamp()` e `ReviewAttestation.utc_review()`, a conversão `astimezone(UTC)` agora captura explicitamente `OverflowError` e o transforma em `ValueError` para que Pydantic retorne `ValidationError` estruturado.

Probes independentes adicionais:

- Oito tentativas de datas com deslocamento extremo (dois modelos × dois extremos × duas rotas Python/JSON) foram rejeitadas com `ValidationError`; **zero `OverflowError` escaparam**.
- Quatro datas adjacentes e representáveis foram aceitas e normalizadas para UTC.
- A suíte do projeto inclui controles adicionais para instanciamento direto e modelos aninhados.

**Parecer F01: corrigido nos limites e rotas examinados.**

## 4. F03 — ausência silenciosa de metadados de auditoria

Os campos dos seis DTOs de audit passaram a ser explicitamente obrigatórios: `SnapshotAudit`, `ValidationAudit`, `IdentityAudit`, `NormalizationAudit`, `M22BAudit`, `IntegrationAudit`. A construção local fornece os valores, enquanto envelopes recebidos incompletos são recusados. A guarda de `Contract` requer também os campos `*_version` dos corpos quando carregam `audit` não nulo.

Probes independentes sobre os relatórios integrados `M23C-A-001` e `M23C-I-005`:

| Tentativa de adulteração | Rejeições | Aceitações indevidas |
|---|---:|---:|
| Remover um campo de um envelope aninhado retido | **338** | **0** |
| Remover uma versão do corpo com envelope retido | **118** | **0** |

Foram percorridas recursivamente as instâncias de audit presentes nos relatórios, sem regenerar o envelope externo após as mutações. Todas as 456 omissões foram rejeitadas durante a reconstrução JSON.

**Parecer F03: corrigido para envelopes presentes nos relatórios e casos examinados.**

### Limite de confiança preservado

O contrato ainda permite **`audit=None` ou ausência total do envelope**, interpretadas como **nova avaliação local**, não como comprovação de registro histórico. Consumidores futuros precisam diferenciar explicitamente verificação de arquivo histórico e reprocessamento; hashes não autenticam autor, fonte ou revisor. Isso não é um novo defeito introduzido pela M2.3d.1.

## 5. Compatibilidade byte a byte

Utilizando as **duas implementações** carregadas em processos separados, foi gerado um manifesto independente de inputs e outputs completos para os 26 casos de `tests/fixtures/m23c_v1.json`.

- Casos: **26/26 idênticos**.
- SHA-256 agregado dos inputs e relatórios, ambos os pacotes: `48f4ec5219e493fc39fa6c97e9ff755e677191c825a1f0058a8a6b939994f89a`.
- Cada caso também apresentou igualdade individual dos bytes de entrada e saída.

Isso sustenta compatibilidade dos cenários legítimos congelados, **não** de qualquer arquivo externo desconhecido.

## 6. Pendências não bloqueantes e recomendações

1. **M23D-F02:** o oráculo E2E não observa integralmente `normalized_name` e a classificação dos diagnósticos. Fortalecer cobertura antes de proclamar qualidade semântica medida em situações reais.
2. **M23D-F04:** M1 e M2.1 diferem na validação de certos URLs malformados. Definir política de fronteira antes de coletar URLs externas, sem forçar equivalência semântica entre 'URL sintaticamente utilizável' e 'URL que identifica um instrumento'.
3. **Fronteira histórica/autenticidade:** a validade de um digest sem referência externa confiável não estabelece autoria, aprovação humana nem autorização de persistência.
4. **Transporte:** orçamento de integração de 64 MiB não equivale a limite estrito de RSS ou tamanho máximo de entrada HTTP/PDF.
5. **Qualidade de descoberta:** 2.000 testes com entradas estruturadas sintéticas não medem precisão/revocação de extração e não validam fontes reais. **Promoção e merge continuam desabilitados.**
6. **Git:** antes de iniciar trabalho sobre documentos reais, registrar um checkpoint revisado e selecionar arquivos explicitamente; não incluir a exclusão SQL preexistente acidentalmente.

## 7. Decisão e liberação condicionada

**READY — M2.3d.1 F01/F03 e encerramento técnico condicional da fundação offline**, pois os bloqueadores reproduzidos pela M2.3d foram eliminados nas verificações disponíveis. Não constitui certificação universal de segurança nem sinal verde para produção.

**Próxima etapa indicada: M3.0**, um piloto offline com pequeno corpus real e rótulos humanos independentes, incluindo fomento, crédito e investimento, positivos, negativos, históricos e ambíguos. Inicialmente, preservar snapshots e referências originais, definir o protocolo de anotação e métricas; não implementar crawler massivo, publicação nem conexão Supabase antes de revisar a fronteira de aquisição e transporte.

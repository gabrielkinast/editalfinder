# EditalFinder V2 — Revisão técnica independente da M2.3c

**Parecer: READY para o escopo offline de composição de entradas estruturadas, com ressalvas documentadas.**

Data da revisão: 2026-10-18.
Pacote analisado: `V2.tar(10).gz`.

## 1. Escopo e metodologia

- Extração estática controlada dos arquivos regulares do TAR, sem executar arquivos compilados, sem rede, Supabase ou banco.
- Leitura do manifesto `tests/fixtures/m23c_v1.json`, do oráculo `docs/v2/M23C_FROZEN_ORACLE.md`, da implementação de integração e dos novos testes.
- Execução da suíte completa, da suíte anterior isolada e de verificações próprias de recomputação, proveniência e auditoria.
- Comparação por SHA-256 dos arquivos Python `src/` contra `V2.tar(9).gz`.
- Ambiente disponível: Python **3.13.5**, Pydantic **2.13.5**, pytest instalado no ambiente de revisão. Ruff e mypy **não estavam disponíveis** para nova execução; os resultados dessas ferramentas dependem dos registros do Hermes.

## 2. Resultados reproduzidos

| Verificação | Resultado |
|---|---|
| Testes completos (`pytest -q -p no:cacheprovider`) | **1.810 passed in 23.28s** |
| Testes anteriores, excluídos os cinco módulos `test_m23c_*.py` | **1.691 passed in 14.92s** |
| Scripts de revisão próprios sobre todo o manifesto | **26 relatórios, 37 candidatos, 14 comparações de identidade** |
| Round-trip JSON e avaliação determinística | **26/26 casos** |
| Digest integral do relatório reproduzido | **26/26 casos** |
| Proveniência das testemunhas dos diagnósticos ligada ao candidato certo | Verificada nos casos presentes |
| Decisões M1 no manifesto | **37 REVIEW**, nenhuma promoção |
| Comparações de identidade | `exact_match` 4; `no_supported_match` 4; `insufficient_information` 4; `distinct_cycles` 2 |
| Código de produção comparado a `V2.tar(9).gz` | **28 arquivos Python idênticos**, nenhum novo, removido ou modificado |

Os 26 casos cobrem categorias A–I; seis são controles negativos declarados. O manifesto projeta valores financeiros, temporais, geográficos, taxonômicos e organizacionais, exige códigos de diagnósticos ordenados e compara resultados de identidade. Verificações de round-trip e de integridade ocorrem pelo ponto de entrada real `integrate`.

## 3. Inspeção dos mecanismos

**Evidências e identidade.** Os cenários de múltiplos registros e os testes de transplante cobrem fatos vindos de candidatos diferentes, sem autorizar fusão de identidades. O algoritmo mantém as comparações como solicitações explícitas e preserva os candidatos isolados. O resultado `exact_match` não é uma autorização de mesclar provas.

**Segurança dos relatórios.** Os testes tentam adulterar snapshots, valores, papéis, proveniência, diagnósticos, identidades, versões e digest, com envelope retido e omitido. Não encontrei bloqueador reproduzível nas verificações examinadas. A omissão do envelope significa **nova recomputação local**, nunca verificação de uma assinatura histórica.

**Orçamento operacional.** O limite de admissão de 64 MiB permanece. O relatório apresenta cenário adjacente de admissão/recusa e pico `tracemalloc` acima de 64 MiB no caso admitido. Isso é coerente com a distinção entre estimador de admissão e limite real de RSS/bytes recebidos.

## 4. Ressalvas e dívida técnica

1. **Ruff global ainda falha:** sete erros em `tests/m23_fixtures.py` (três B023 e quatro E501), e a formatação global ainda acusa o mesmo arquivo. Os comandos que o excluem passam segundo o relatório enviado; **não declarar o gate global verde**. A captura de variáveis de loop pelo closure (B023) merece correção explícita com verificação de equivalência, separada dos testes da M2.3c.
2. **Todos os 37 candidatos permanecem REVIEW.** Isso corresponde à política de autorização desabilitada, mas não mede acerto de classificação positiva, precision/recall ou seletividade da futura descoberta.
3. **Os controles negativos já recebem afirmações estruturadas, incluindo `actionable=False` nos casos aplicáveis.** Demonstram preservação e bloqueio de autoridade, não detecção autônoma de notícias, resultados ou ofertas falsas a partir de texto bruto.
4. **Oráculo manual é estático e tem projeções deliberadas.** A regra `required_issue_codes` verifica um subconjunto dos issues M1, não a lista exata; mutações relevantes do catálogo podem exigir expectativas ampliadas. O relatório anterior também reconhece esse limite.
5. **Contratos financeiros incompletos para crédito e investimentos:** juros, carência, amortização, garantias, equity, valuation e rodadas ainda não possuem representação normalizada aprovada. Essa ausência foi preservada e documentada, não preenchida por suposição.
6. **Transporte, autenticação e cadeia de custódia:** não há limites de bytes antes da desserialização pública, checagem de autenticidade da fonte/revisor, persistência ou caminho legítimo de promoção. Hash local não é assinatura.
7. **Ambiente:** revisão aqui em Python 3.13.5/Pydantic 2.13.5; o relatório do Hermes traz Python 3.11.16/Pydantic 2.14.1. Isso não certifica a matriz 3.11–3.14.

## 5. Decisão e próximo passo

**READY — M2.3c, exclusivamente testes ponta a ponta do pipeline offline com entradas já estruturadas.** A revisão reproduziu a suíte completa e não localizou um defeito bloqueante para este recorte. Não há autorização de produção, promoção, crawling, persistência, merge ou alegação de eficácia em documentos reais.

Recomendo: (i) corrigir em mudança isolada os erros globais do Ruff com teste de equivalência das fixtures; (ii) avançar para **M2.3d — auditoria adversarial final offline**; (iii) só depois planejar a M3 com dados reais rotulados de **fomento, crédito e investimentos**, separando avaliação do extrator da avaliação do validador e sem habilitar publicação.

## 6. Comandos executados na revisão

```bash
# no diretório extraído: src/ e tests/
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests \
 python -B -m pytest -p no:cacheprovider -q tests/
# 1810 passed in 23.28s

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests \
 python -B -m pytest -p no:cacheprovider -q \
 --ignore=tests/test_m23c_adversarial.py \
 --ignore=tests/test_m23c_metamorphic.py \
 --ignore=tests/test_m23c_pipeline.py \
 --ignore=tests/test_m23c_product_contracts.py \
 --ignore=tests/test_m23c_resources.py tests/
# 1691 passed in 14.92s
```

Os probes próprios percorreram os 26 casos, comparando cada saída ao input, recomputando os resultados e o SHA-256 do corpo serializado sem o envelope externo, conferindo a ausência de promoção, o vínculo das testemunhas dos diagnósticos e o round-trip Pydantic JSON. Nenhuma modificação foi aplicada ao pacote original.

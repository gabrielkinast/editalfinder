# EditalFinder V2 — Revisão técnica independente da M2.2a.1

**Parecer:** **READY, exclusivamente para o domínio offline da M2.2a.1**, condicionado às restrições existentes (sem persistência, promoção, crawling ou certificação de produção).

**Material examinado:** `/mnt/data/V2.tar(4).gz`; comparação de conteúdo fonte com `V2.tar(3).gz`. Arquivos inspecionados: `temporal_models.py`, `temporal_normalization.py`, `geography_normalization.py`, `geography_models.py`, `semantic_common.py`, novos testes da M2.2a.1 e `EDITALFINDER_V2_M22A1_RESULTADOS.md`. Revisão sem alterações ao projeto do usuário.

## 1. Verificações reexecutadas

Ambiente deste revisor: **Python 3.13.5 / Pydantic 2.13.5 / pytest 9.0.2**. Sem conexão a banco, crawler ou serviços externos.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python -B -m pytest -q -p no:cacheprovider
# 1075 passed in 4.62s

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python -B -m pytest -q -p no:cacheprovider \
  --ignore=tests/test_m22a1_temporal_contract.py \
  --ignore=tests/test_m22a1_geography_contract.py
# 958 passed in 4.28s
```

**Ruff e mypy não estavam instalados no ambiente do revisor;** não afirmo ter reexecutado esses gates. O relatório do Hermes documenta sucesso no Python 3.11.16 / Pydantic 2.14.1. O pacote enviado também não contém os arquivos `pyproject.toml`, `README.md` ou `uv.lock`, impossibilitando revisar seu estado atual a partir dele.

## 2. Inspeção das duas correções

### Temporal — `temporal_models.py:58–129`

- O contrato compara o offset indicado por `timezone` com `local_datetime.utcoffset()`.
- Se a conversão UTC é representável, o objeto requer `instant_utc` presente, em UTC (offset zero) e igual ao instante calculado.
- Se a conversão sai do intervalo de `datetime` do Python, o objeto permite UTC ausente **apenas** com `temporal_timezone_conversion_out_of_range` no próprio evento.
- Diagnóstico de overflow falso é rejeitado.
- Com `timezone=None` e com `-00:00`, o horário local continua naive e nenhum UTC é inventado.
- Regras de precisão fracionária continuam explícitas.

### Geografia — `geography_normalization.py:65–79`

- Um `GeographyLocationClaim` sem qualquer componente recebe `geo_location_empty` com `claim_index` da posição original.
- O local permanece no relatório, com papel e entrada originais; país, UF, região, município e confiança não são preenchidos artificialmente.
- O escopo é tratado separadamente da existência de componentes geográficos.

## 3. Probes próprios adicionais

Foi executado um script separado, sem alterar arquivos do projeto, com **3.000 instantes pseudoaleatórios de offset conhecido** e datas internas representáveis, verificando por caso:

- **3.000 rejeições** de `instant_utc` ausente.
- **3.000 rejeições** de UTC incorreto (+1 minuto).
- **3.000 aceitações** com UTC calculado corretamente.
- **3.000 round-trips** `model_dump_json()` → `model_validate_json()` estáveis.
- **2 casos** com timezone desconhecido ou ausente preservados sem UTC.
- **4 relatórios** de localização vazia em índices distintos, com diagnóstico indexado e round-trip estável.
- **4 rejeições** por adulteração do índice de diagnóstico com envelope de auditoria retido.
- **2 extremos adicionais**, ano 0001 com +14:00 e ano 9999 com -14:00: sem diagnóstico, rejeitados; com diagnóstico correto, aceitos sem UTC e com round-trip.

Não houve falha nessas verificações. As regras de overflow são ainda cobertas amplamente pelos testes da suíte enviada, mas meus probes pseudoaleatórios focaram datas internas.

## 4. Comparação entre os arquivos V2.tar(3).gz e V2.tar(4).gz

Mudanças de **código de produção**: somente `temporal_models.py` e `geography_normalization.py`. Mudança documental: `docs/v2/SEMANTIC_NORMALIZATION_M22A.md`. Novos testes no pacote: `tests/test_m22a1_temporal_contract.py` e `tests/test_m22a1_geography_contract.py`. Novo relatório: `EDITALFINDER_V2_M22A1_RESULTADOS.md`.

Os arquivos de resultados da M2.1 e M2.2a existentes no tar anterior não estão neste novo tar. **Isso indica diferença na composição dos pacotes, não prova de exclusão no repositório local do usuário.** Não foi possível verificar o status Git real usando apenas o arquivo compactado.

## 5. Riscos deliberadamente fora do escopo

- Hash SHA-256 garante detecção de alteração contra uma referência preservada; **não autentica o autor, a fonte ou o revisor**.
- A promoção automática continua bloqueada; ausência de caminho de autorização confiável permanece uma restrição esperada.
- Sem validação externa de fuso IANA/DST, nem determinação de horários de corte de editais ou precedência de retificações.
- Nenhum teste com fontes reais, persistência Supabase, matriz completa de versões Python/Pydantic ou orçamento de memória/transporte extremo foi realizado nesta revisão.
- Testes automatizados e probes não são uma prova formal de ausência de defeitos.

## 6. Conclusão

**READY para encerrar a correção offline M2.2a.1.** Os dois defeitos anteriormente identificados não foram reproduzidos após a correção; invariantes de UTC e diagnósticos de localização vazia passaram nos testes da suíte e nos probes independentes. **Não significa READY para produção**, persistência, merge, publicação ou promoções automáticas.

Próxima etapa recomendada: **M2.2b (normalização financeira, organizações e taxonomias)**, somente após checkpoint seguro do código/documentação e com autorização de promoção ainda desabilitada. Manter decisões pendentes sobre modelagem SQL e autenticidade separadas.

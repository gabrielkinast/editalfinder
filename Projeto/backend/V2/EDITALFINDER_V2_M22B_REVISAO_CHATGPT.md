# EditalFinder V2 — Parecer independente M2.2b

**Data:** 2026-10-17  
**Escopo:** pacote enviado `V2.tar(5).gz`, revisão offline de finanças, organizações e taxonomias.  
**Decisão:** **READY para a M2.2b offline, com ressalvas explícitas de cobertura e fronteira de confiança; NOT READY para coleta real, publicação, merge ou persistência.**

## 1. Verificações realmente executadas

- O TAR foi examinado quanto a caminhos de travessia e links; arquivos regulares extraídos para diretório isolado.
- `PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -q -p no:cacheprovider` → **1.348 passed in 5.73s**.
- Ambiente independente: **Python 3.13.5 / Pydantic 2.13.5 / pytest 9.0.2**. Não constitui certificação de toda a matriz.
- Ruff/mypy **não disponíveis neste ambiente**. O relatório do Hermes declara aprovação no Python 3.11.16; não foram reexecutados aqui.
- 28 adulterações dirigidas em relatórios (`FinancialReport`, `OrganizationNormalizationReport`, `TaxonomyReport`), mantendo ou removendo `audit`, foram rejeitadas com `pydantic.ValidationError`. Nenhum bypass demonstrado nesses cenários. Não são testes exaustivos.

## 2. Contratos examinados

- `src/editalfinder_v2/domain/m22b_common.py`: preparação de contexto e envelope SHA-256; `matches_m22b` exige papel semântico, snapshot, unidade, fonte, execução, prova de afirmação e papel da linha estruturada.
- `financial_models.py`, `financial_parsing.py`, `financial_normalization.py`: `Decimal`, papéis distintos, moeda explícita, preservação de formato, valores originais e diagnósticos; sem conversão ou autorização de escrita.
- `organization_models.py`, `organization_normalization.py`: papéis institucionais independentes, CNPJ sintático/checksum versus existência jurídica, nomes sem merge automático; comparação contextual, não identidade legal.
- `taxonomy_models.py`, `taxonomy_normalization.py`: somente códigos oficiais exatos por dimensão, sem classificar notícia como oportunidade e sem promover.
- `docs/v2/SEMANTIC_NORMALIZATION_M22B.md` e `EDITALFINDER_V2_M22B_RESULTADOS.md`: limites, restrições e fronteiras declarados.

## 3. Atenções para integração — não são bloqueios demonstrados da milestone offline

### 3.1 Formato monetário depende da declaração do extrator

O próprio contrato declara que `format`, `currency` e `unit` são metadados **não autenticados** do adaptador, embora as evidências estejam vinculadas ao texto/papel.

Reprodução independente com o mesmo valor e a mesma evidência textual, `R$ 1.234`:

- `format='brazilian'` → `Decimal('1234')`, sem diagnóstico.
- `format='us'` → `Decimal('1.234')`, sem diagnóstico.
- `format='unspecified'` → unresolved, `financial_ambiguous_format`.

Não se deve inferir que o parser fez algo diferente de seu contrato: ele respeitou a política indicada. Porém, **o formato declarado pelo extrator não pode ser tratado como semanticamente comprovado** só porque o relatório passou na verificação estrutural. Antes de persistir valores de crédito ou investimento, exigir proveniência/verificação da política de interpretação ou marcar o resultado para revisão quando essa política não estiver aprovada.

### 3.2 Catálogo atual não representa investimento societário de maneira específica

`src/editalfinder_v2/domain/policies.py` oferece `credito`, `financiamento_reembolsavel`, `financiamento_nao_reembolsavel` etc., mas não código explícito de `investimento`, `capital_de_risco`, `equity`, `coinvestimento` ou equivalentes. Um claim `resource_type='investimento'` produz `unknown` e `taxonomy_mapping_not_approved`, preservando o original. Comportamento **seguro**, mas **cobertura insuficiente para o objetivo de negócio completo** (fomento, crédito e oportunidades de investimento).

Também não há contratos especializados para juros, CET, carência, amortização, garantias, elegibilidade de crédito, equity/diluição/participação, valuation e ticket de investimento. Não inventar categorias nem converter `financiamento_reembolsavel` em investimento. Fazer decisão de domínio versionada e revisar seeds/SQL antes da persistência, caso categorias adicionais sejam aprovadas.

### 3.3 Integração ainda não testada

- Origem/autenticidade do documento, do extrator, de namespace e da política de formato não são autenticadas aqui.
- A identidade organizacional não está verificada em cadastro governamental; chave contextual não autoriza merge.
- A assinatura/hash dos relatórios não autentica emissor ou cadeia de custódia.
- Nada comprova precisão/recall com fontes reais; não houve extração, persistência ou `ACCEPTED` em produção.
- Os SQLs existentes não representam todas as formas financeiras e etapas temporais; requerer decisão de projeção antes da M5.

## 4. Recomendação

**Aprovar a M2.2b para o propósito contratado de normalização offline conservadora**, mantendo qualquer autorização de gravação/publicação desligada.

**Próximo checkpoint sugerido:** contrato de integração `extract → role/evidence binding → normalize → validate` com dados sintéticos e, separadamente, definição explícita do **escopo de fomento/crédito/investimentos** antes de elaborar um conjunto ouro e crawlers reais. Não adicionar categorias de investimento automaticamente só para os testes passarem.

*Parecer restrito ao conteúdo disponibilizado no pacote e às verificações explicitamente executadas.*

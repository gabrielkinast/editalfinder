# Relatório técnico de auditoria (dry-run)

Gerado: `2026-05-01T06:57:27Z` · Amostra: até **25** itens por ficheiro · PDF: **on**.

## 0. Como ler estes números (sem alarme falso)
- **«Quebrado»** na matriz reflete sobretudo *amostra + PDF off + gate*; valide com `--no-skip-pdf` em poucas fontes antes de mexer em crawlers.
- **«Ruído que passou = 0»** é bom sinal, mas não substitui revisão de *oportunidades boas rejeitadas* (veja motivos agregados na secção 4).
- **Login (242)** pode misturar lixo real e falsos positivos; o projeto agora **suprime padrões de login fracos** em contexto `gov.br`/bancos públicos com sinais de chamada/edital.
- **Loader-only:** `python scripts/audit_pipeline.py --only-loader` para separar perdas do loader.
- **Score:** `EDITALFINDER_SKIP_SCORING=true` remove cálculo de relevância no transformer (caminho mais leve).

## 1. Resumo executivo
- **4** ficheiros JSON processados; **68** itens na amostra.
- **4** ficheiros tinham itens brutos na amostra.
- Distribuição heurística de maturidade: {'maduro': 4}.
- O `opportunity_gate` e regras de relevância excluem muitas URLs institucionais/PDFs sem texto — várias fontes ficam com **0 aceites** na amostra (ver secção 8 e `audit_by_source.json`).

## 2. Quantidade de fontes testadas
4

## 3. Quantidade de itens analisados
68

## 4. Principais bugs / causas de rejeição (agregado)

| Motivo (rejection_reason) | Contagem na amostra |
|---------------------------|---------------------|

## 5. Principais ruídos
- Títulos de lista negra **no bruto** contam-se por ficheiro; exemplos que **passaram** o transformer: **0** (ficheiro `audit_noise_examples.json`).

## 6. Campos mais vazios (só itens transformados)

- **documentos**: score acumulado 292
- **fim_inscricao**: score acumulado 196
- **area_cientifica**: score acumulado 169
- **pdf_url**: score acumulado 152
- **data_publicacao**: score acumulado 97
- **valor**: score acumulado 85
- **programa**: score acumulado 17
- **titulo**: score acumulado 0
- **descricao**: score acumulado 0
- **link**: score acumulado 0
- **fonte**: score acumulado 0
- **situacao**: score acumulado 0

## 7. Dados perdidos no transformer
- Exemplos: **0** em `audit_data_loss_examples.json`.

## 8. Dados perdidos no loader
- Simulação: `map_to_db_schema` + `_strip_payload`; ver `audit_loader_payload.json` (chaves após strip vs extras fora do strip em modo legado).

## 9. Duplicidade
- Por ficheiro: contagem de links repetidos no bruto e nos aceites — `audit_duplicates.json`.

## 10. Classificação
- Flags heurísticas (ex.: crédito sem tipo): **0** exemplos em `audit_classification_issues.json`.

## 11. perfil_ideal
- **0** exemplos em `audit_profile_issues.json`.

## 12. Datas
- **1** flags em `audit_by_source.json` (por fonte) + agregado nos exemplos.

## 13. Valores
- **0** exemplos de valor bruto sem valor transformado.

## 14. PDF / documentos
- Nesta corrida os PDFs **não foram baixados** (`pdf_skip`); percentagens de `pdf_url` nos aceites reflectem só metadados do crawler + extras.

## 15. Performance
- Tempos por ficheiro: `audit_performance.json`.

## 16. Score / relevância legado
- Ficheiros Python com ocorrências: **30** — detalhe em `audit_score_legacy.json`.

## 17. Status por crawler (amostra)
- **Maduro** (exemplos): aneel, bndes, cnpq, finep
- **Ruidoso**: —
- **Quebrado** (0 aceites ou erro): 0 fontes — primeiras: —

## 18. Top 10 correções mais importantes
1. Rever falsos positivos do **opportunity_gate** (login em páginas gov.br reais de editais).
2. Separar **PDF só como documento** vs página de oportunidade no gate.
3. Afinar **relevância mínima** para BNDES/BRDE/Caixa/Badesul (muitas exclusões na amostra).
4. Melhorar **tipo_recurso** para linhas de crédito.
5. Preencher **perfil_ideal** nas fontes estratégicas.
6. Reduzir **campos vazios** nas fontes no topo de `audit_empty_fields.json`.
7. **Deduplicação** por link dentro do mesmo JSON de crawler.
8. Preservar **pdf_url** quando presente no bruto.
9. Auditoria com **PDF on** apenas num subconjunto controlado.
10. Documentar **fontes com_zero_aceites** como risco de gate vs risco de crawler.

## 19. Correções rápidas
- Ajustar listas de ruído / títulos genéricos no crawler ou em `noise_filter` com base em `audit_noise_examples.json`.

## 20. Correções médias
- Refinar `opportunity_gate` por domínio (gov.br, bndes.gov.br, etc.).

## 21. Correções grandes
- Separar pipeline **crawl → normalização mínima → gate pesado opcional**.

## 22. Próximas etapas
- Correr amostra maior (`--max-items 100`) em subset de fontes críticas.
- Correr subconjunto com `--no-skip-pdf` em staging.
- Validar matriz completa em `audit_matrix_crawlers.json`.

---
*Maturidade é heurística sobre a amostra; não substitui revisão humana dos JSONs.*
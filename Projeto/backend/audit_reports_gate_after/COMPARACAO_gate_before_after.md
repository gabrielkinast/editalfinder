# Comparação gate: antes vs depois

## Diretórios

- **Antes:** `D:\Computational_Physics\My Projects\edital\audit_reports_pdf_subset_skipscore`
- **Depois:** `D:\Computational_Physics\My Projects\edital\audit_reports_gate_after`
- **Falsos positivos (snapshot):** `audit_reports_gate\audit_gate_false_positives.json`

## Agregados (audit_by_source)

| Métrica | Antes | Depois | Delta |
|---|---:|---:|---:|
| Itens brutos (amostra) | 68 | 68 | 0 |
| Transformados (aceitos) | 4 | 68 | 64 |
| Rejeitados | 64 | 0 | -64 |
| Rejeições «Relevancia limite» | 56 | 0 | -56 |
| Rejeições «Pontuacao abaixo» | 8 | 0 | -8 |
| Ruído que passou (lista noise) | 0 | 0 | 0 |

## Recuperação no snapshot de falsos positivos

- Itens do relatório FP que o gate **aceitaria agora** (`keep=True`): **0**

_Se o JSON de FP tiver 0 itens, o gate atual já não emite essas duas rejeições na amostra bruta das quatro fontes — não há linhas para «recuperar» nesse ficheiro; use um baseline antigo ou histórico git para listar casos._

## Possíveis falsos positivos restantes (gate ainda rejeita com motivo alvo)

_Nenhum ou relatório FP ausente._

## Campos vazios (score global no audit_summary)

- **area:** antes=200 · depois=0
- **tipo_oportunidade:** antes=200 · depois=0
- **perfil_ideal:** antes=200 · depois=0
- **setor_economico:** antes=200 · depois=0
- **documentos:** antes=200 · depois=292

_Nota: o «score» global de campos vazios no `audit_summary` soma vazios em **todos** os itens transformados; com muito mais aceites, alguns campos (ex.: `documentos`, `fim_inscricao`) podem subir no ranking mesmo com melhoria por item — comparar também `campos_preenchidos_pct` em `audit_by_source.json`._

## Respostas objetivas

1. **Oportunidades antes rejeitadas e agora aceitas (agregado):** delta de transformados = **64** (na mesma amostra/max-items; depende de ter corrido o pipeline com os mesmos parâmetros).
2. **Lixo passou?** entradas em `noise_passou_transformer`: antes **0**, depois **0**.
3. **Campos ricos:** `br_public_hints` + relax do gate; o auditor agora lê `tipo_oportunidade`/`area`/setores em `extras` (ver `campos_preenchidos_pct` por fonte).
4. **BNDES/CNPq/Finep/Aneel:** ver delta por fonte em `audit_by_source.json` de cada pasta.
5. **Regras a ajustar:** se «Relevancia limite»/«Pontuacao abaixo» ainda dominam, rever `trusted_fin` + lista de marcadores ou expandir `trusted_br_relevance_soft_continue` com critérios mais rígidos contra notícias.

## Próxima etapa (recomendações)

- Rever manualmente uma amostra dos **25 aceites por fonte** (guias vs chamadas reais) para calibrar `noticia_sem_oportunidade` e `content_type_detectado`.
- Melhorar **extração de `documentos`/`pdf_url`** quando o HTML não traz PDF mas o crawler já tem `extras.pdf_url`.
- Opcional: persistir `opportunity_gate_category` no loader/schema quando for ligar o Supabase.
- Expandir taxonomia só com evidência (novos padrões PT) para `area_cientifica` quando o texto tiver disciplinas explícitas.
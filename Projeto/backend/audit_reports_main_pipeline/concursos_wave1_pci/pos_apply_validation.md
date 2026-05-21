# Pós-apply — Wave 1 PCI Concursos (staging)

**Fonte:** `pci_concursos`  
**Tabela:** `public.concurso_selecao`  
**View de consumo:** `public.vw_concursos_front`  
**Relatório máquina:** `pos_apply_validation.json` (mesma pasta)  
**Apply registado em:** `loader_apply_staging/load_concursos_selecao_summary.json` (`2026-05-13T23:17:24Z`)

## Resumo do apply

| Métrica | Valor |
|---------|--------|
| Itens processados | **12** |
| Upsert previsto / aplicado | **12** |
| **Inserts** | **0** |
| **Updates** | **12** |
| Erros (map / apply / total) | **0** / **0** / **0** |
| Duplicados no batch | 0 |
| Itens expirados | 0 |
| `apply_status` | **applied** |
| Ambiente | `EDITALFINDER_ENV=staging`, `has_allow_staging_apply=true` |

**Interpretação dos 0 inserts:** o loader faz upsert por `(fonte, link)`. Doze *updates* e zero *inserts* indicam que os doze `link` da PCI **já existiam** em `concurso_selecao` em staging (re-aplicação ou carga anterior), e o apply atualizou os registos.

## Distribuições (lote aplicado)

| Campo | Distribuição |
|--------|----------------|
| `validacao_status` | **incompleto: 12** |
| `qualidade_dado` | **media: 12** (nenhum item com ambas as datas + órgão + local para subir a `alta`) |
| `tipo_selecao` | concurso_publico: **8**, processo_seletivo: **4** |
| `status` | ativo: **12** |

## Cobertura de campos (sobre os 12 exemplos de payload)

Contagens em `load_concursos_selecao_payload_examples.json`:

| Preenchidos (≥1) | 12/12 |
|------------------|-------|
| `titulo`, `link_edital`, `fonte_tipo`, `nivel_escolaridade`, `taxa_inscricao`, `validacao_status`, `qualidade_dado` | 12 |

| Preenchidos (parcial) | Contagem / 12 |
|------------------------|---------------|
| `orgao` | 9 |
| `instituicao` | 2 |
| `estado` / `municipio` | 4 |
| `numero_vagas` | 11 |
| `salario_min` / `salario_max` | 9 (em 3 linhas ambos ausentes) |

**Sempre vazios no lote:** `data_fim_inscricao`, `data_prova`, `data_publicacao`, `cargo`, `curso`.

## Exemplos aplicados (referência)

1. NAV BRASIL — salário + taxa; sem órgão inferido; `incompleto`.  
2. Exército — 1100 vagas; só `taxa_inscricao` na amostra (sem faixa salarial); `incompleto`.  
3. Marinha Escola Naval — órgão, vagas, salário e taxa; `incompleto`.  
4. Câmara Presidente Prudente — órgão, UF, município, vagas, faixa salarial e taxa; `incompleto`.

Lista completa no JSON (`exemplos_aplicados` + ficheiro de payload).

## Riscos restantes (agregador)

- **100% `incompleto`:** não confundir com erro de pipeline — reflete ausência de `data_fim_inscricao` extraída.  
- **Link “edital”:** pode ser portal, não PDF.  
- **Valores monetários:** heurística taxa/salário; notas em `extras.value_extraction_notes` onde houve valor ambíguo.  
- **`qualidade_dado` só “media”:** coerente com ausência de datas oficiais; não inflacionar percepção de completude.

## Recomendação — PCI na Wave 1

**Sim, pode continuar** na Wave 1 **em staging** como camada de **descoberta**: apply limpo, dados utilizáveis na view/UI com rótulos de parcialidade, separação taxa/salário na maioria dos casos. **Não** usar sozinha em produção sem curadoria ou sem cruzamento com fonte oficial para prazos e remuneração.

## Checklist manual (pós-apply)

- [ ] Validar **`/concursos`** em staging (carregamento, sem erro 500).  
- [ ] Validar **cards** (título, “Dados parciais”, “Fonte agregadora”, inscrição/prova quando ausentes).  
- [ ] Validar **filtros** (tipo, status, busca) com dados PCI.  
- [ ] Validar **taxa vs salário** nos casos NAV, Marinha, IME, Câmaras, Exército/ESFCEx/EsPCEx.  
- [ ] Validar **datas ausentes** (não mostrar datas inventadas).  
- [ ] Validar **`public.vw_concursos_front`** (SQL ou dashboard: contagem e colunas para `fonte = pci_concursos`).

---

*Este ficheiro foi gerado a partir dos artefactos em `loader_apply_staging`, sem novo apply e sem alteração a schema ou código de aplicação.*

# Diagnóstico PNCP — API pública de consulta

## Endpoint funcional

- **URL:** `https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao`
- **Método:** GET público (sem autenticação no diagnóstico).

## Parâmetros obrigatórios (comportamento observado + manual/Swagger)

| Parâmetro | Observação |
|-----------|------------|
| `dataInicial` | AAAAMMDD; sem isso a API responde 400. |
| `dataFinal` | AAAAMMDD. |
| `codigoModalidadeContratacao` | Inteiro (tabela de modalidades); sem isso 400. |
| `pagina` | Paginação (1-based nas amostras). |
| `tamanhoPagina` | Mínimo **10** (`must be greater than or equal to 10`). |

## Parâmetros opcionais úteis

- `uf`: reduz volume e estabiliza tempo de resposta em alguns casos.
- `codigoMunicipioIbge`, `cnpj`, `codigoUnidadeAdministrativa`, `codigoModoDisputa`, `idUsuario` (refino).

## Resposta e campos úteis

- Corpo JSON paginado: lista em **`data`** (schema atual).
- Identificação: `numeroControlePNCP`, `processo`, `anoCompra` + `sequencialCompra`.
- Objeto e prazos: `objetoCompra`, `dataPublicacaoPncp` / `dataInclusao`, `dataEncerramentoProposta`, `dataAberturaProposta`.
- Órgão/unidade: objetos aninhados `orgaoEntidade` e `unidadeOrgao` (razão social, UF, município) — o crawler deve achatar para compatibilidade.
- Modalidade: `modalidadeId`, `modalidadeNome`.
- Links/anexos: `linkSistemaOrigem`, `linkProcessoEletronico`, etc. (varia por registro).

## Prefixo legado

- `https://pncp.gov.br/api/pncp/v1/contratacoes/publicacao` tende a **404** (não usar).

## Melhor tentativa (mais linhas na página 1)

```json
{
  "name": "ok_nacional_3d_mod8",
  "url": "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao",
  "params": {
    "pagina": 1,
    "tamanhoPagina": 10,
    "dataInicial": "20260429",
    "dataFinal": "20260501",
    "codigoModalidadeContratacao": 8
  },
  "status": 200,
  "row_count": 10,
  "elapsed_ms": 414
}
```

- Relatório JSON: `D:\Computational_Physics\My Projects\edital\audit_reports_blocked_sources\pncp_endpoint_diagnosis.json`
- Amostras mascaradas: `D:\Computational_Physics\My Projects\edital\audit_reports_blocked_sources\pncp_endpoint_samples.json`

## Rodada local (crawler + transformação + auditorias, sem loader)

Execução após ajuste do `pncp/main_pncp.py` (parâmetros obrigatórios, `tamanhoPagina` ≥ 10, janelas curtas, achatamento de `orgaoEntidade` / `unidadeOrgao`):

| Métrica | Valor |
|---------|------:|
| Itens brutos (`pncp/outputs/pncp_editais.json`) | 21 |
| Transformados (dry-run) | 20 |
| Rejeitados pelo `opportunity_gate` | 1 |
| Duplicata de link (quick audit) | 1 |

Saídas auxiliares nesta pasta:

- `pncp_retransform_run/` — `retransform_summary.json`, `standardized/pncp_standardized.json`
- `pncp_semantic_audit/` — `audit_semantic_summary.json` (ex.: 6 flags `classificacao_incoerente_com_fonte` em 20 itens)
- `pncp_docs_audit/` — `audit_docs_summary.json` (preservação de documentos não-PDF; `pdf_url` vazio na amostra)

## Recomendação de readiness (PNCP continua **blocked** no gate global)

Motivo: a fonte ainda está marcada como bloqueada por decisão operacional; esta rodada só prova viabilidade técnica do endpoint e do pipeline local.

Checklist para **reavaliar** desbloqueio (alinhado ao pedido):

1. **Transformados > 0** — atendido na amostra (20).
2. **Objeto real** — atendido (`objetoCompra` / título de contratação, não página índice).
3. **Não é página índice** — atendido (links `pncp.gov.br/app/editais/{controle}` ou sistemas de origem).
4. **Metadados oficiais** — atendido na amostra (`numeroControlePNCP`, órgão, modalidade, processo, amparo legal quando presente).
5. **`tipo_oportunidade` coerente** — em geral `compra_publica` / `contrato_publico`; revisar flags semânticas (taxonomia vs texto PNCP).
6. **`perfil_ideal`** — ainda fraco no standardized (0% preenchido no resumo); reforçar regra ou aceitar default explícito antes do gate.
7. **Ruído / duplicatas** — 1 duplicata de link e 1 rejeição por relevância; rodadas maiores exigem dedupe e eventual rotação de `codigoModalidadeContratacao` ou filtros `uf` para estabilidade.

Riscos operacionais a tratar antes de produção: **timeouts intermitentes** em páginas/janelas largas na API nacional; mitigação atual — janelas de 3 dias, no máximo 2 páginas por janela, pausa leve entre requisições, chunks recentes primeiro.

**Conclusão:** manter **blocked** até revisão de gate/taxonomia para PNCP e política de cobertura (mais modalidades/dias sem estourar timeout). O endpoint `.../api/consulta/v1/contratacoes/publicacao` com `dataInicial` + `dataFinal` + `codigoModalidadeContratacao` é a via segura de dados reais (GET público).
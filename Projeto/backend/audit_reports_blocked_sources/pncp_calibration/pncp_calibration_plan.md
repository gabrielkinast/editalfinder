# Plano de calibração PNCP (rodada local)

## Objetivo

Melhorar coerência semântica e preservação de links oficiais **sem** desbloquear PNCP no gate global, **sem** loader/apply e **sem** alterar `opportunity_gate` global.

## Endpoint e contrato da API

| Item | Valor |
|------|--------|
| URL ativa | `https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao` |
| Legado | `/api/pncp/v1/...` → **404** (não usar) |
| Obrigatórios | `dataInicial`, `dataFinal`, `codigoModalidadeContratacao`, `pagina` |
| Paginação | `tamanhoPagina` **≥ 10** |

## Limites operacionais (conservador)

Controlados por variáveis de ambiente (valores padrão):

| Variável | Padrão | Notas |
|----------|--------|--------|
| `PNCP_TOTAL_DAYS` | 9 | Cobertura em dias |
| `PNCP_CHUNK_DAYS` | 3 | Tamanho do bloco de datas por requisição |
| `PNCP_MAX_PAGES` | 2 | Máximo de páginas por bloco |
| `PNCP_PAGE_SIZE` | 10 | Mínimo exigido pela API |

Timeouts e pausa entre GETs permanecem modestos para não estressar o serviço público.

## Riscos

- **Timeouts** em janelas amplas ou páginas altas na consulta nacional.
- **Variabilidade** por modalidade/UF (algumas combinações podem falhar ou demorar).

## Estado antes desta calibração

- 21 itens brutos, 20 transformados (dry-run), 1 rejeição por relevância.
- 6 flags `classificacao_incoerente_com_fonte` (confiança baixa na taxonomia).
- 1 duplicata de link no quick audit (antes): dois registros com `https://pncp.gov.br`; após canonização no transformer, **duplicatas_link = 0**.

## Ajustes implementados (código)

1. **`CORE/taxonomy_filtros.calibrate_pncp_extras`**: `perfil_ideal`, `classificacao_confianca`, `tipo_recurso`, poda de `setor_economico`, teto de `setor_estrategico`, `links_oficiais`.
2. **`CORE/transformer`**: hash de conteúdo PNCP enriquecido; preservação de `tipo` em documentos oficiais; chamada à calibração após hints BR; `_pncp_soft_continue` aceita portal externo com metadados PNCP.
3. **`pncp/main_pncp.py`**: ignora URL genérica `https://pncp.gov.br` ao escolher `link`; documentos com `linkProcessoEletronico` / tipos; `numero_controle_pncp` nos extras; env `PNCP_*`.
4. **`scripts/audit_semantic_classification.py`**: exceção PNCP para `licitacao_sem_licitacao` quando o texto traz sinais de contratação.

## Por que manter **blocked**

- Decisão de produto: não liberar carga automática até revisão humana.
- Recomenda-se **nova coleta** com o crawler corrigido para eliminar o par `link` genérico residual no JSON bruto antigo.

## Próximos passos (operacional)

1. `python pncp/main_pncp.py` (regenerar bruto).
2. Rodar novamente os três comandos da pasta `pncp_calibration/` (retransform, semantic, docs).
3. Revisar `pncp_readiness_recommendation.*`.

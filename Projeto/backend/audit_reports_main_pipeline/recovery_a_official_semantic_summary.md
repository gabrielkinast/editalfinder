# Recovery A — auditoria semântica (dry-run oficial)

- Fontes no input: **2** (banco_da_amazonia + dod_sbir_sttr)
- Itens total: **32**

## Flags (audit_semantic_classification)

- `publico_alvo_sem_evidencia`: **1**

## Verificações Recovery A (scan do standardized oficial)

- setor_estrategico > 3: **0**
- titulo_ruidoso: **0**
- login isolado / SSO ESA: **0**
- API/Data Resources / Success / Events (URLs): **0**
- títulos institucionais genéricos: **0**

## Critérios booleanos

- `setor_estrategico_gt3_eq_0`: **True**
- `titulo_ruidoso_eq_0`: **True**
- `login_isolado_eq_0`: **True**
- `api_docs_eq_0`: **True**
- `paginas_institucionais_genericas_eq_0`: **True**

## Nota

1 ocorrência no conjunto oficial — baixo; reforçar extração de público-alvo se promover a staging.

JSON: `recovery_a_official_semantic_summary.json`
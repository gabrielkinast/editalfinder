# Cobertura de gates/filtros

- Fontes totais: **94**
- Passam por `transform_generic`: **94**
- Aplicam `opportunity_gate`: **94**
- Aplicam `noise_filter`: **94**
- Normalizam documentos: **94**
- Vão para loader: **94**
- Fontes que pulam gate: **0**

## Distribuição de risco

- medio: 94

## Teste sintético

- `Contato` rejeitado em todos os caminhos: **True**
- `Edital válido` mantido nos caminhos testados: **True**

Ver detalhes em `synthetic_gate_test.json` e cobertura por fonte em `gate_coverage_by_source.json`.
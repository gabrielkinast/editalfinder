# Crawler piloto — Fundatec (notícias)

- **Fonte:** `fundatec`
- **Listagem:** `https://www2.fundatec.org.br/category/concursos/`
- **Coleta (UTC):** `2026-05-14T17:56:27.297879+00:00`
- **URLs brutas (listagem):** 10
- **Descartados:** 3
- **Standardized:** 7
- **Ficheiro:** `D:/Computational_Physics/My Projects/edital/audit_reports_main_pipeline/concursos_wave1_fundatec/standardized/fundatec_standardized.json`

## Campos preenchidos

```json
{
  "titulo": 7,
  "tipo_selecao": 7,
  "categoria": 7,
  "orgao": 4,
  "instituicao": 0,
  "banca": 7,
  "cargo": 0,
  "curso": 0,
  "area": 0,
  "nivel_escolaridade": 7,
  "estado": 4,
  "municipio": 3,
  "regiao": 0,
  "modalidade": 0,
  "numero_vagas": 0,
  "salario_min": 5,
  "salario_max": 5,
  "taxa_inscricao": 6,
  "data_publicacao": 7,
  "data_inicio_inscricao": 0,
  "data_fim_inscricao": 2,
  "data_prova": 7,
  "status": 7,
  "link": 7,
  "link_edital": 7,
  "fonte": 7,
  "fonte_tipo": 7,
  "validacao_status": 7,
  "qualidade_dado": 7,
  "tags": 7,
  "extras": 7,
  "ativo": 7
}
```

## Riscos

- Conteúdo editorial; `link_edital` aponta para o portal de concursos Fundatec quando encontrado.
- `parse_vagas` não lê números por extenso (ex.: “três vagas”).

## Próximo passo

`python scripts/load_concursos_selecao.py --dry-run --input-dir .../standardized --output-dir .../loader_dryrun_v4 --sources fundatec`

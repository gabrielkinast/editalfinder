# Crawler piloto — PCI Concursos

- **Fonte:** `pci_concursos`
- **Coleta (UTC):** `2026-05-13T20:18:41.069565+00:00`
- **URLs brutas consideradas:** 24
- **Descartados (total):** 0
- **Descartados (antiguidade / heurística):** 0
- **Standardized gravados:** 12
- **Ficheiro:** `D:/Computational_Physics/My Projects/edital/audit_reports_main_pipeline/concursos_wave1_pci/standardized/pci_concursos_standardized.json`

## Campos preenchidos (contagem)

```json
{
  "titulo": 12,
  "tipo_selecao": 12,
  "categoria": 12,
  "orgao": 9,
  "instituicao": 2,
  "banca": 12,
  "cargo": 0,
  "curso": 0,
  "area": 0,
  "nivel_escolaridade": 12,
  "estado": 4,
  "municipio": 4,
  "regiao": 0,
  "modalidade": 0,
  "numero_vagas": 11,
  "salario_min": 9,
  "salario_max": 9,
  "taxa_inscricao": 12,
  "data_publicacao": 0,
  "data_inicio_inscricao": 0,
  "data_fim_inscricao": 0,
  "data_prova": 0,
  "status": 12,
  "link": 12,
  "link_edital": 12,
  "fonte": 12,
  "fonte_tipo": 12,
  "validacao_status": 12,
  "qualidade_dado": 12,
  "tags": 12,
  "extras": 12,
  "ativo": 12
}
```

## Campos tipicamente ausentes neste piloto

cargo, curso, area, regiao, modalidade, data_publicacao, data_inicio_inscricao, data_fim_inscricao, data_prova

## Riscos

- Agregador: texto editorial; datas podem estar incompletas → `validacao_status = incompleto`.
- Link oficial pode faltar → `extras.official_link_missing`.
- Respeitar sempre `robots.txt` e limites; não aumentar `--max-items` sem revisão.

## Recomendação de apply

**Não aplicar** automaticamente. Correr `scripts/load_concursos_selecao.py --dry-run` e só depois `apply` em staging com guardas.

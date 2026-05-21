# Concursos & Seleções — crawlers (wave 1)

Módulo **Python** ao nível da raiz do repositório (`concursos/`), **separado** de crawlers de `public.edital` e do Radar.

## Piloto ativo

```bash
cd /path/to/edital
python concursos/main_pci_concursos.py --max-items 10 --sleep 2.0
```

Saída padrão:

- `audit_reports_main_pipeline/concursos_wave1_pci/standardized/pci_concursos_standardized.json`
- `audit_reports_main_pipeline/concursos_wave1_pci/crawler_summary.json` e `.md`

## Loader (dry-run)

```bash
python scripts/load_concursos_selecao.py --dry-run ^
  --input-dir audit_reports_main_pipeline/concursos_wave1_pci/standardized ^
  --output-dir audit_reports_main_pipeline/concursos_wave1_pci/loader_dryrun ^
  --sources pci_concursos
```

## Princípios

1. Ler `robots.txt` antes de escalar volume.
2. User-Agent identificável; pausa entre pedidos (`--sleep`).
3. Não seguir URLs `*.php` na PCI (robots).
4. Não inventar salário, vagas ou datas — `validacao_status = incompleto` quando faltar confiança.
5. Nunca `apply` automático no Supabase a partir destes scripts.

## Vunesp

`main_vunesp_concursos.py` é apenas diagnóstico/stub até termos acesso estável (ver documentação de decisão do piloto).

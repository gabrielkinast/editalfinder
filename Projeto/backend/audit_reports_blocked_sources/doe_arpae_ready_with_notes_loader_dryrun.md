# DOE ARPA-E — `ready_with_notes` e dry-run do loader

## Diff de readiness

### `config/source_readiness.json`

- **`doe_arpae` removido** de `blocked`.
- **`doe_arpae` adicionado** a `ready_with_notes`.
- **Nota:** ao executar `load_ready_sources.py`, o script **reconstrói** este ficheiro a partir de `readiness_for_loader.json` (primeiros 54 = `ready`, seguintes 17 = `ready_with_notes`), com ordenação alfabética dentro de cada lista.

### `audit_reports_retransform/readiness_for_loader.json`

- **`doe_arpae` retirado** de `fontes_bloqueadas_temporariamente`.
- **`doe_arpae` inserido** em `fontes_prontas_para_loader` no segmento **pronto com observações** (entre `badesul` e `erc`).
- **`status_distribution`:** `pronto_com_observacoes` **16 → 17**; `bloquear_temporariamente` **15 → 14**.

### Standardized

- Cópia: `CORE/transformer/doe_arpae_standardized.json` → `audit_reports_retransform/standardized/doe_arpae_standardized.json`.

## Comando do dry-run

```text
python scripts/load_ready_sources.py --dry-run --sources doe_arpae --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

**Execução:** `id_execucao` `cf2d0d73-5fb7-41a9-9b93-2e5c4a52dc35` (ver `audit_reports_loader_ready/load_ready_summary.json`).

## Resultado agregado

| Métrica | Valor |
|--------|------:|
| Fontes selecionadas | 1 |
| Itens standardized | 14 |
| **would_upsert** | **14** |
| would_ignore | 0 |
| Erros de mapeamento | 0 |
| **critical_empty_items** | **0** |
| Documentos (input → preservados) | 0 → 0 (sem perdas) |
| pdf_url | 0 → 0 (não inventado) |
| validacao_status / qualidade_dado preservados | 14 / 14 |
| canonical_skipped | 0 |

## Verificações pedidas

- **tipo_oportunidade:** 14/14 no payload (`funding_opportunity` para `DE-FOA-*`, `chamada_publica` para RFIs de teaming nos exemplos).
- **tipo_recurso:** **fomento** em todos os exemplos.
- **perfil_ideal:** listas preenchidas (14/14).
- **validacao_status:** **incompleto** (prazo/valor ausentes, coerente com a listagem sem segunda passagem em NOFO PDF).
- **qualidade_dado:** 60–70 nos exemplos de `load_ready_payload_examples.json`.
- **origem_portal:** **ARPA-E eXCHANGE** no standardized.
- **codigo_oportunidade / numero_chamada:** códigos **RFI-*** ou **DE-FOA-*** alinhados ao título.
- **Links oficiais:** `link` e `extras.url_detalhe` / `url_listagem` no domínio **`arpa-e-foa.energy.gov`** (portal público).
- **pdf_url:** `null` ou vazio — **não** preenchido artificialmente.
- **Documentos:** 0 no bruto; **0** `documentos_perdidos_no_payload`.

## Environment guard

- `has_allow_staging_apply`: **false** (`missing_staging_flag`). Não impede dry-run; define política para **apply** real.

## Recomendação: apply em staging?

**Sim, de forma condicional:** o dry-run está limpo para **14** upserts simulados. Antes de `--apply --staging`, alinhar variáveis de ambiente e flags do projeto, e aceitar que os registos ficam **incompletos** em prazo/valor até eventual enriquecimento (ex. `FileContent.aspx` controlado). **Produção** só após política de dados e qualidade acordarem com `ready_with_notes`.

**Apply não foi executado.** **Gate global** não foi alterado.

**Supabase:** o script pode continuar a gravar metadados de execução (ex.: `carga_execucao`); não houve apply de editais.

---

Ficheiro irmão: `doe_arpae_ready_with_notes_loader_dryrun.json`.

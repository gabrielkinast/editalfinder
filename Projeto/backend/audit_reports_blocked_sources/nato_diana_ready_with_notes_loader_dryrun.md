# NATO DIANA — `ready_with_notes` e dry-run do loader

## Diff de readiness

### `config/source_readiness.json`

- **Removido de `blocked`:** `nato_diana`.
- **Adicionado a `ready_with_notes`:** `nato_diana`.
- **Nota:** ao correr `load_ready_sources.py`, o script **reconstrói** este ficheiro a partir de `audit_reports_retransform/readiness_for_loader.json` (primeiros 54 = `ready`, seguintes 18 = `ready_with_notes`). A lista fica **ordenada alfabeticamente** dentro de cada bucket.

### `audit_reports_retransform/readiness_for_loader.json`

- **`nato_diana` retirado** de `fontes_bloqueadas_temporariamente`.
- **`nato_diana` inserido** em `fontes_prontas_para_loader` no segmento **pronto_com_observacoes** (entre `mma` e `nsf`).
- **`status_distribution`:** `pronto_com_observacoes` 17→**18**; `bloquear_temporariamente` 14→**13**.

### Standardized para o loader

- Cópia: `CORE/transformer/nato_diana_standardized.json` → `audit_reports_retransform/standardized/nato_diana_standardized.json`.

## Comando do dry-run

```text
python scripts/load_ready_sources.py --dry-run --sources nato_diana --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

**Execução bem-sucedida** (`id_execucao`: `eda92b2d-85a3-40da-b0b3-b31807f4109f`, ver `audit_reports_loader_ready/load_ready_summary.json`).

## Resultado agregado

| Métrica | Valor |
|--------|------:|
| Fontes selecionadas | 1 |
| Itens standardized | 2 |
| **would_upsert** | **2** |
| would_ignore | 0 |
| Erros de mapeamento | 0 |
| **critical_empty_items** | **0** |
| Documentos (input → preservados) | 0 → 0 |
| pdf_url (input → preservados) | 0 → 0 |
| validacao_status / qualidade_dado preservados | 2 / 2 |
| canonical_skipped | 0 |

## Verificações pedidas

- **tipo_oportunidade:** presente nos 2 payloads — **`accelerator`** (calibração DIANA).
- **tipo_recurso:** **`fomento_pdi`** nos dois.
- **perfil_ideal:** **`pequenas empresas`** nos dois.
- **setor_estrategico:** preenchido — `defesa_industrial`, `inovacao_defesa`, `dual_use`; **sem** setor de cibersegurança por match genérico a “security”.
- **area_tecnologica:** listas **vazias** nos standardized (alto nível; não é erro de mapeamento neste dry-run).
- **validacao_status:** um registo **`valido`** (challenge); um **`incompleto`** (FAQ, com `prazo_ausente` e `valor_ausente` no standardized).
- **qualidade_dado:** **88** e **70** nos exemplos do payload.
- **Links oficiais:** `https://www.diana.nato.int/challenges.html` e `https://www.diana.nato.int/faq.html`.
- **pdf_url:** string vazia no standardized → **`null`** no payload; **não** há URL inventada.
- **Cibersegurança indevida:** não há flags de setor ciber por “security” genérico; só texto narrativo no FAQ (“defence and security experience”).

## Environment guard

- `editalfinder_env`: staging; **`has_allow_staging_apply`: false** (`block_reason`: `missing_staging_flag`).
- O dry-run corre sem apply; o guard impede apply automático sem o fluxo de flags de staging.

## Recomendação: apply em staging?

**Sim, de forma condicional:** o dry-run indica **2 upserts** simulados sem erros nem `critical_empty`, alinhado ao estatuto **ready_with_notes** (volume baixo, parte curada por acesso/Cloudflare, um item incompleto por desenho). Antes de `--apply --staging`, confirmar variáveis e `EDITALFINDER_ALLOW_STAGING_APPLY` (ou equivalente) no fluxo do projeto. **Apply não foi executado**; **Supabase** não foi alterado manualmente nesta tarefa; **gate global** não foi mexido.

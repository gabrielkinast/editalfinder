# Dry-run loader — `petrobras` (ready_with_notes)

**Execução:** `2026-05-02T02:10:26Z` · `id_execucao` `39afcbff-cd7c-4fce-b7e4-393c23292c41`

```text
python scripts/load_ready_sources.py --dry-run --sources petrobras --exclude-blocked
```

## Diff / resumo do readiness

1. **`config/source_readiness.json`** (também regravado pelo loader a partir do JSON de readiness): `petrobras` **saiu** de `blocked` e entrou em **`ready_with_notes`**.
2. **`audit_reports_retransform/readiness_for_loader.json`**: `petrobras` removido de **`fontes_bloqueadas_temporariamente`**; incluído no fim de **`fontes_prontas_para_loader`**; **`pronto_com_observacoes`** 12 → **13**; **`bloquear_temporariamente`** 19 → **18**.
3. **`audit_reports_retransform/standardized/petrobras_standardized.json`**: cópia do standardized corrigido (`lote1_fix_petrobras/standardized/…`).

## Resultado do dry-run

| Verificação | Valor |
|-------------|------:|
| Itens standardized | 4 |
| `would_upsert` | 4 |
| `would_ignore` | 0 |
| Erros de mapeamento | 0 |
| Itens com campos críticos vazios | 0 |
| Documentos perdidos no payload | 0 |
| Itens com docs na entrada / preservados | 2 / 2 |
| `pdf_url` na entrada / preservado | 2 / 2 |
| `canonical_skipped` | 0 |

## Campos semânticos (entrada → payload → preservados)

Contagens do `load_ready_summary.json` para os campos rastreados pelo script:

- **tipo_oportunidade:** 4 / 4 / 4  
- **tipo_recurso:** 4 / 4 / 4  
- **publico_alvo:** 4 / 4 / 4  
- **validacao_status:** 4 / 4 / 4  
- **qualidade_dado:** 4 / 4 / 4  
- **area** (e correlatos rastreados): 2 / 2 / 2  

O loader não rastreia **`perfil_ideal`** na mesma tabela de agregados; no JSON standardized ele pode existir em `extras` quando o transformador preenche.

## Flags / risco

- No standardized, alguns itens (sobretudo páginas HTML da Bússola) podem ter **`validacao_status`: `suspeito`** (descrição curta, prazo/valor ausentes); o dry-run **não** os exclui — coerente com **ready_with_notes**.
- **Apply** não foi executado; Supabase não foi alterado nesta etapa.

## Recomendação para staging

**Sim:** o dry-run está **limpo** para carregar **4** registos (upsert por `link`), sem erros de mapeamento e **sem perda** de documentos/PDF no payload. Recomenda-se **apply em staging** quando for intencional, com o processo habitual (`--staging`, variáveis de ambiente e revisão humana breve por causa do volume baixo e de `validacao_status` suspeito em parte dos itens).

JSON espelhado: `petrobras_ready_with_notes_loader_dryrun.json`.

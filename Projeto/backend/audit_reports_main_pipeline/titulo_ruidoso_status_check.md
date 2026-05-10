# Auditoria: `titulo_ruidoso` vs desativação (`ativo=false`)

**Data do snapshot (JSON):** ver campo `timestamp` em `titulo_ruidoso_status_check.json`  
**Ambiente:** staging (consulta read-only via cliente Supabase do projeto)  
**Restrição:** apenas `SELECT`; nenhum `UPDATE`.

## Conclusão

O `post_daily_validation` mostrava **`titulo_ruidoso=6`** mesmo após desativar os ruídos porque o validador **contava todas as linhas com título “ruidoso”**, **incluindo** registros com **`ativo=false`**. Os seis links pedidos estão em staging com **`ativo: false`**; o título ainda contém termos da lista `NOISE_TITLES` (por exemplo FAQ, Conta PJ, Entre em contato, Quem Somos, ou substring `faq`), logo **continuavam a ser contados** no agregado único `titulo_ruidoso`.

A correção no script **`scripts/validate_full_staging_after_daily.py`** separa:

| Problema | Severidade | Efeito no resumo global |
|----------|------------|-------------------------|
| `titulo_ruidoso_ativo_true` | `warning` | Entra nos totais de warnings / `post_daily_validation` no topo |
| `titulo_ruidoso_inativo` | `info` | Fica apenas em `tables.edital.problems` (histórico desativado) |

Regra alinhada a `prazo_vencido_ativo_true`: ignora-se **apenas** `ativo is False` explícito para o contador “ativo”; `null`/ausente continua no bucket ativo.

## Evidência: staging (`SELECT` por `link`)

Consulta: `edital.select('id_edital,titulo,link,ativo,validacao_status,fonte_recurso').eq('link', <url>)`.

| Fonte / rótulo | `id_edital` | `ativo` | `validacao_status` | `titulo` (resumo) |
|----------------|-------------|---------|-------------------|-------------------|
| BASA — Conta PJ | 2 | **false** | incompleto | Conta PJ |
| BDMG — Entre em contato | 52 | **false** | incompleto | Entre em contato |
| General Dynamics Suppliers — FAQ | 1014 | **false** | suspeito | Supplier FAQs |
| KAKENHI — FAQ | 1252 | **false** | incompleto | 科研費FAQ |
| NATO DIANA — FAQ | 1419 | **false** | incompleto | NATO DIANA — Programme FAQ (…) |
| NUCLEP — Quem Somos | 1432 | **false** | incompleto | Quem Somos |

Detalhe completo (incluindo URLs) está em **`titulo_ruidoso_status_check.json`** → chave `queries`.

## Referência de código

Definição de ruído e split ativo/inativo:

```409:427:scripts/validate_full_staging_after_daily.py
def _noise_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        title = str(r.get("titulo") or "").strip().casefold()
        if not title:
            continue
        if any(n in title for n in NOISE_TITLES) or title in {"menu", "faq"}:
            out.append(r)
    return out


def _noise_rows_active(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ruído de título ainda relevante para dashboards (mesma regra que prazo_vencido_ativo_true: ignora só ativo=false explícito)."""
    return [r for r in _noise_rows(rows) if r.get("ativo") is not False]


def _noise_rows_inactive(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ruído já desativado (histórico); não deve inflacionar o mesmo contador que exige ação."""
    return [r for r in _noise_rows(rows) if r.get("ativo") is False]
```

Registro dos dois problemas em `_validate_edital`:

```563:565:scripts/validate_full_staging_after_daily.py
    _add_problem(problems, "prazo_vencido_ativo_true", _expired_active(rows), severity="warning")
    _add_problem(problems, "titulo_ruidoso_ativo_true", _noise_rows_active(rows), severity="warning")
    _add_problem(problems, "titulo_ruidoso_inativo", _noise_rows_inactive(rows), severity="info")
```

Agregação global: `info` não entra na lista de warnings do topo (`_collect_problem_summaries`); `_warnings_by_source` só soma `severity == "warning"`.

## Próximo passo (opcional)

Regenerar o relatório diário com `--staging` para ver **`titulo_ruidoso_ativo_true`** zerado (ou reduzido) e **`titulo_ruidoso_inativo`** refletindo estes históricos, conforme o dataset completo carregado pelo script.

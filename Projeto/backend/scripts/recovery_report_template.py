# -*- coding: utf-8 -*-
"""
Template padronizado para relatórios consolidados de Recoveries / ondas do backend.

Uso:
- Importar `build_consolidado_markdown` e `padrao_documentacao_onda` em geradores
  que escrevem `*_consolidado.{md,json}`.
- Chaves interpretativas recomendadas (JSON): ver `PADRAO_DOCUMENTACAO_ONDA_KEYS`.

Não altera pipeline, loaders nem base de dados — apenas texto e estrutura de relatório.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

# Chaves do envelope JSON (aninhadas sob "padrao_documentacao_onda" nos consolidados
# existentes para não colidir com "proximos_passos" / métricas legadas).
PADRAO_DOCUMENTACAO_ONDA_KEYS = (
    "resumo_executivo",
    "problema_original",
    "fontes_tratadas",
    "resultado_principal",
    "metricas_antes_depois",
    "interpretacao",
    "decisao_recomendada",
    "riscos",
    "proximos_passos",
    "evidencias_tecnicas",
)


def metricas_row_md(
    metrica: str,
    antes: Any,
    depois: Any,
    variacao: Any,
    interpretacao: str,
) -> str:
    """Uma linha de tabela markdown (sem cabeçalho)."""
    return f"| `{metrica}` | {antes} | {depois} | {variacao} | {interpretacao} |"


def tabela_metricas_operacionais(
    linhas: Sequence[Mapping[str, Any]],
) -> str:
    """
    linhas: dicts com chaves metrica, antes, depois, variacao, interpretacao
    """
    out: List[str] = [
        "| Métrica | Antes | Depois | Variação | Interpretação |",
        "|---|---:|---:|---:|---|",
    ]
    for row in linhas:
        out.append(
            metricas_row_md(
                str(row["metrica"]),
                row.get("antes", ""),
                row.get("depois", ""),
                row.get("variacao", ""),
                str(row.get("interpretacao", "")),
            )
        )
    return "\n".join(out)


def tabela_resultado_por_fonte(
    linhas: Sequence[Mapping[str, Any]],
) -> str:
    """
    linhas: dicts com chaves fonte, antes, depois, ganho, observacao
    """
    out: List[str] = [
        "| Fonte | Antes | Depois | Ganho | Observação |",
        "|---|---:|---:|---:|---|",
    ]
    for row in linhas:
        out.append(
            "| {fonte} | {antes} | {depois} | {ganho} | {obs} |".format(
                fonte=row.get("fonte", ""),
                antes=row.get("antes", "—"),
                depois=row.get("depois", "—"),
                ganho=row.get("ganho", "—"),
                obs=str(row.get("observacao", "")),
            )
        )
    return "\n".join(out)


def lista_numerada(itens: Iterable[str]) -> str:
    return "\n".join(f"{i}. {t}" for i, t in enumerate(itens, start=1))


def padrao_documentacao_onda(
    *,
    resumo_executivo: str,
    problema_original: str,
    fontes_tratadas: List[str],
    resultado_principal: str,
    metricas_antes_depois: Dict[str, Any],
    interpretacao: Dict[str, List[str]],
    decisao_recomendada: Dict[str, str],
    riscos: List[str],
    proximos_passos: List[str],
    evidencias_tecnicas: Dict[str, Any],
) -> Dict[str, Any]:
    """Monta o objeto interpretativo pedido para JSON."""
    return {
        "resumo_executivo": resumo_executivo,
        "problema_original": problema_original,
        "fontes_tratadas": list(fontes_tratadas),
        "resultado_principal": resultado_principal,
        "metricas_antes_depois": metricas_antes_depois,
        "interpretacao": {
            "ganhos": list(interpretacao.get("ganhos", [])),
            "regressoes_aparentes": list(interpretacao.get("regressoes_aparentes", [])),
            "sem_mudanca": list(interpretacao.get("sem_mudanca", [])),
            "limitacoes": list(interpretacao.get("limitacoes", [])),
        },
        "decisao_recomendada": {
            "acao": decisao_recomendada.get("acao", ""),
            "justificativa": decisao_recomendada.get("justificativa", ""),
            "proximo_alvo": decisao_recomendada.get("proximo_alvo", ""),
        },
        "riscos": list(riscos),
        "proximos_passos": list(proximos_passos),
        "evidencias_tecnicas": dict(evidencias_tecnicas),
    }


def evidencias_padrao(
    *,
    arquivos_lidos: List[str],
    arquivos_gerados: List[str],
    comandos: Optional[List[str]] = None,
    apply_executado: bool = False,
    schema_alterado: bool = False,
    supabase_tocado: bool = False,
    notas_seguranca: Optional[List[str]] = None,
) -> Dict[str, Any]:
    return {
        "arquivos_lidos": list(arquivos_lidos),
        "arquivos_gerados": list(arquivos_gerados),
        "comandos": list(comandos or []),
        "apply_executado": apply_executado,
        "schema_alterado": schema_alterado,
        "supabase_tocado": supabase_tocado,
        "notas_seguranca": list(notas_seguranca or []),
    }


def build_consolidado_markdown(
    titulo_cabecalho: str,
    sec1_resumo_executivo: str,
    sec2_contexto: str,
    sec3_o_que_foi_alterado: str,
    sec4_resultado_operacional_md: str,
    sec5_resultado_por_fonte_md: str,
    sec6_interpretacao: str,
    sec7_riscos: str,
    sec8_decisao: str,
    sec9_proximos_passos_md: str,
    sec10_evidencias: str,
) -> str:
    """Monta o Markdown com as 10 secções numeradas do padrão de onda."""
    parts: List[str] = [
        f"# {titulo_cabecalho}",
        "",
        "## 1. Resumo executivo",
        "",
        sec1_resumo_executivo.strip(),
        "",
        "## 2. Contexto",
        "",
        sec2_contexto.strip(),
        "",
        "## 3. O que foi alterado",
        "",
        sec3_o_que_foi_alterado.strip(),
        "",
        "## 4. Resultado operacional",
        "",
        sec4_resultado_operacional_md.strip(),
        "",
        "## 5. Resultado por fonte",
        "",
        sec5_resultado_por_fonte_md.strip(),
        "",
        "## 6. Interpretação",
        "",
        sec6_interpretacao.strip(),
        "",
        "## 7. Riscos e limitações",
        "",
        sec7_riscos.strip(),
        "",
        "## 8. Decisão recomendada",
        "",
        sec8_decisao.strip(),
        "",
        "## 9. Próximos passos",
        "",
        sec9_proximos_passos_md.strip(),
        "",
        "## 10. Evidências técnicas",
        "",
        sec10_evidencias.strip(),
        "",
    ]
    return "\n".join(parts)


def merge_padrao_into_consolidado(
    doc: Dict[str, Any], padrao: Dict[str, Any]
) -> Dict[str, Any]:
    """Devolve uma cópia superficial de doc com padrao_documentacao_onda inserido."""
    out = dict(doc)
    out["padrao_documentacao_onda"] = padrao
    return out

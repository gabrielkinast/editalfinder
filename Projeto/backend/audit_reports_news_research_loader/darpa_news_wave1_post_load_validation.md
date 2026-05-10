# DARPA News Wave 1 — validação pós-carga

- Gerado: `2026-05-09T06:13:18Z`
- Staging: **True**
- Fonte / onda: `darpa_news` / `darpa_news_wave1`
- Resultado global: **OK**

## Contagens esperadas (payload)

- Notícia: **8**
- Pesquisa: **2**
- Review (ficheiro JSON, não carregado pelo loader): **0**
- Rejected (ficheiro JSON, auditoria): **0**

## Checks

- **payload_links_noticia_unicos**: OK
- **payload_links_pesquisa_unicos**: OK
- **payload_sem_overlap_noticia_pesquisa**: OK
- **review_payload_legivel**: OK
- **rejected_payload_legivel**: OK
- **supabase_conexao**: OK
- **noticia_count_igual_esperado**: OK
- **pesquisa_count_igual_esperado**: OK
- **noticia_data_publicacao_preenchida**: OK
- **noticia_resumo_preenchido**: OK
- **noticia_extras_jsonb_objeto**: OK
- **noticia_arrays_nao_string**: OK
- **noticia_sem_tipo_pesquisa_incoerente_em_extras**: OK
- **pesquisa_data_publicacao_preenchida**: OK
- **pesquisa_descricao_preenchida**: OK
- **pesquisa_extras_jsonb_objeto**: OK
- **pesquisa_arrays_nao_string**: OK
- **nenhum_link_payload_em_public_edital**: OK
- **review_candidates_nao_sobrepoe_payload_de_carga**: OK
- **rejected_nao_sobrepoe_payload_de_carga**: OK
- **review_candidates_ignorados_sem_linha_noticia_nem_pesquisa**: OK
- **rejected_ignorados_sem_linha_noticia_nem_pesquisa**: OK
- **vw_noticias_front_contem_todos_links_noticia**: OK
- **vw_pesquisas_front_contem_todos_links_pesquisa**: OK
- **vw_noticias_front_consultavel**: OK
- **vw_pesquisas_front_consultavel**: OK

## Cruze com o último `load_news_research_summary.json`

- Alinhado (source + wave + would_upsert): **False**
- Ficheiro: `D:\Computational_Physics\My Projects\edital\audit_reports_news_research_loader\load_news_research_summary.json`

## Ficheiro JSON

- `darpa_news_wave1_post_load_validation.json`

```json
{
  "gerado_em": "2026-05-09T06:13:18Z",
  "staging_flag": true,
  "source": "darpa_news",
  "wave": "darpa_news_wave1",
  "payload_paths": {
    "noticia": "D:\\Computational_Physics\\My Projects\\edital\\audit_reports_news_research_loader\\darpa_news_wave1_payload_noticia.json",
    "pesquisa": "D:\\Computational_Physics\\My Projects\\edital\\audit_reports_news_research_loader\\darpa_news_wave1_payload_pesquisa.json",
    "review": "D:\\Computational_Physics\\My Projects\\edital\\audit_reports_news_research_loader\\darpa_news_wave1_review_candidates.json",
    "rejected": ""
  },
  "expected_counts": {
    "noticia": 8,
    "pesquisa": 2,
    "review_candidates_json": 0,
    "rejected_json": 0
  },
  "ok": true,
  "checks": [
    {
      "name": "payload_links_noticia_unicos",
      "ok": true,
      "detail": {
        "count": 8,
        "unique": 8
      }
    },
    {
      "name": "payload_links_pesquisa_unicos",
      "ok": true,
      "detail": {
        "count": 2,
        "unique": 2
      }
    },
    {
      "name": "payload_sem_overlap_noticia_pesquisa",
      "ok": true,
      "detail": {
        "overlap": []
      }
    },
    {
      "name": "review_payload_legivel",
      "ok": true,
      "detail": {
        "path": "D:\\Computational_Physics\\My Projects\\edital\\audit_reports_news_research_loader\\darpa_news_wave1_review_candidates.json",
        "count": 0
      }
    },
    {
      "name": "rejected_payload_legivel",
      "ok": true,
      "detail": {
        "path": "",
        "count": 0
      }
    },
    {
      "name": "supabase_conexao",
      "ok": true,
      "detail": "cliente criado (apenas leituras)"
    },
    {
      "name": "noticia_count_igual_esperado",
      "ok": true,
      "detail": {
        "esperado": 8,
        "encontrados": 8,
        "missing": [],
        "missing_total": 0
      }
    },
    {
      "name": "pesquisa_count_igual_esperado",
      "ok": true,
      "detail": {
        "esperado": 2,
        "encontrados": 2,
        "missing": [],
        "missing_total": 0
      }
    },
    {
      "name": "noticia_data_publicacao_preenchida",
      "ok": true,
      "detail": {
        "bad": [],
        "count": 0
      }
    },
    {
      "name": "noticia_resumo_preenchido",
      "ok": true,
      "detail": {
        "bad": [],
        "count": 0
      }
    },
    {
      "name": "noticia_extras_jsonb_objeto",
      "ok": true,
      "detail": {
        "bad": [],
        "count": 0
      }
    },
    {
      "name": "noticia_arrays_nao_string",
      "ok": true,
      "detail": {
        "bad": [],
        "count": 0
      }
    },
    {
      "name": "noticia_sem_tipo_pesquisa_incoerente_em_extras",
      "ok": true,
      "detail": {
        "bad": [],
        "count": 0
      }
    },
    {
      "name": "pesquisa_data_publicacao_preenchida",
      "ok": true,
      "detail": {
        "bad": [],
        "count": 0
      }
    },
    {
      "name": "pesquisa_descricao_preenchida",
      "ok": true,
      "detail": {
        "bad": [],
        "count": 0
      }
    },
    {
      "name": "pesquisa_extras_jsonb_objeto",
      "ok": true,
      "detail": {
        "bad": [],
        "count": 0
      }
    },
    {
      "name": "pesquisa_arrays_nao_string",
      "ok": true,
      "detail": {
        "bad": [],
        "count": 0
      }
    },
    {
      "name": "nenhum_link_payload_em_public_edital",
      "ok": true,
      "detail": {
        "edital_rows_matching_links": 0
      }
    },
    {
      "name": "review_candidates_nao_sobrepoe_payload_de_carga",
      "ok": true,
      "detail": {
        "overlap": []
      }
    },
    {
      "name": "rejected_nao_sobrepoe_payload_de_carga",
      "ok": true,
      "detail": {
        "overlap": []
      }
    },
    {
      "name": "review_candidates_ignorados_sem_linha_noticia_nem_pesquisa",
      "ok": true,
      "detail": {
        "presentes_na_bd_indevidamente": [],
        "count": 0
      }
    },
    {
      "name": "rejected_ignorados_sem_linha_noticia_nem_pesquisa",
      "ok": true,
      "detail": {
        "presentes_na_bd_indevidamente": [],
        "count": 0
      }
    },
    {
      "name": "vw_noticias_front_contem_todos_links_noticia",
      "ok": true,
      "detail": {
        "esperado_links": 8,
        "vistos_na_view": 8,
        "missing": []
      }
    },
    {
      "name": "vw_pesquisas_front_contem_todos_links_pesquisa",
      "ok": true,
      "detail": {
        "esperado_links": 2,
        "vistos_na_view": 2,
        "missing": []
      }
    },
    {
      "name": "vw_noticias_front_consultavel",
      "ok": true,
      "detail": {
        "ok": true,
        "erro": "",
        "amostra_rows": 5
      }
    },
    {
      "name": "vw_pesquisas_front_consultavel",
      "ok": true,
      "detail": {
        "ok": true,
        "erro": "",
        "amostra_rows": 5
      }
    }
  ],
  "loader_summary_alignment": {
    "path": "D:\\Computational_Physics\\My Projects\\edital\\audit_reports_news_research_loader\\load_news_research_summary.json",
    "alinhado": false,
    "wave_ficheiro": "eurekalert_wave1",
    "source_ficheiro": "eurekalert_science_filtered",
    "would_upsert_noticia": 0,
    "would_upsert_pesquisa": 1,
    "expected_noticia": 8,
    "expected_pesquisa": 2,
    "nota": "Referência ao último load_news_research_summary.json; pode não coincidir se a última execução foi outra fonte/onda."
  },
  "output_paths": {
    "json": "D:\\Computational_Physics\\My Projects\\edital\\audit_reports_news_research_loader\\darpa_news_wave1_post_load_validation.json",
    "markdown": "D:\\Computational_Physics\\My Projects\\edital\\audit_reports_news_research_loader\\darpa_news_wave1_post_load_validation.md"
  }
}
```

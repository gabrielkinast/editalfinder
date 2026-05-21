# Wave 2 — Militar/Aeroespacial — IME (CFG, CFrm, CG, CP/IME)

Crawler multi-processo do **Instituto Militar de Engenharia** para `public.concurso_selecao`.

## Diagnóstico por processo

| Processo | Página oficial | Edital / documento | Inscrição | Datas no HTML | PDF texto |
|----------|----------------|-------------------|-----------|---------------|-----------|
| **CFG ATIVA** | [inscrições CFG](https://www.ime.eb.mil.br/vestibular-e-concursos/cfg-ensino-medio/inscricoes) | `CFG ATIVA 2026.pdf` | [SIPS_CFG](https://inscricoes.ime.eb.br/SIPS_CFG/Login) | Não (só requisitos/locais) | Escaneado (`text_len` baixo) |
| **CFG RESERVA** | mesma página | `CFG RESERVA 2026.pdf` | SIPS_CFG | Idem | Escaneado |
| **CFrm** | [informações CFrm](https://www.ime.eb.mil.br/vestibular-e-concursos/cfrm/informacoes-cfrm) | `CFORM 2026.pdf` | [SIPS_CFrm](https://inscricoes.ime.eb.br/SIPS_CFrm/Login) | Ciclo 2025/2026 no texto | Escaneado |
| **CG (EQA)** | [informações CG](https://www.ime.eb.mil.br/vestibular-e-concursos/cg/informacoes-gerais-cg) + [legislação](https://www.ime.eb.mil.br/vestibular-e-concursos/cg/legislacao-cg) | `MIC_EQA_2025PUBLICADO.pdf` (manual); calendário separado | [Portal #cg](https://inscricoes.ime.eb.br/#cg) | Requisitos AMAN/CP | Escaneado |
| **CP/IME** | [CP-IME](https://www.ime.eb.mil.br/vestibular-e-concursos/cp-ime) | `Calendario_CP_IME_2026.pdf` | N/A (matrícula interna EB) | **90 vagas** 2026 no HTML | Escaneado |

**Hub:** [inscricoes.ime.eb.br](https://inscricoes.ime.eb.br/) — landing com seções CFG / CG / CFrm (sem datas na home).

**CP/IME:** curso preparatório obrigatório para CG; não é vestibular aberto ao público geral — `tipo_selecao=programa_ingresso` (classificação semântica: formação militar; tag `programa_formacao` em `tags`).

**Limitação:** PDFs militares `.mil.br` são predominantemente escaneados; **sem OCR** → `data_fim_inscricao` / `data_prova` em geral ausentes → `validacao_status=incompleto` quando falta fim de inscrição.

**SSL:** certificado exige contexto com verificação desligada (igual ITA).

## Script e artefatos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_militar_aeroespacial_ime.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave2_militar_aeroespacial_ime/standardized/ime_standardized.json` |
| Mapeamento geral | [CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_FONTES.md](./CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_FONTES.md) |

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_militar_aeroespacial_ime.py --max-items 10 --sleep 2.0
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave2_militar_aeroespacial_ime/standardized --output-dir audit_reports_main_pipeline/concursos_wave2_militar_aeroespacial_ime/loader_dryrun --sources ime
python -m pytest tests/test_militar_aeroespacial_ime_crawler.py -q
```

## Mapeamento

| Campo | Valor |
|--------|--------|
| `fonte` | `ime` |
| `fonte_tipo` | `instituicao` |
| `orgao` | Exército Brasileiro |
| `instituicao` | Instituto Militar de Engenharia |
| `banca` | IME / Exército Brasileiro |
| `estado` / `municipio` | RJ / Rio de Janeiro |
| `area` | Engenharia / Defesa / Militar / Aeroespacial |
| `categoria` | `militar_aeroespacial_ime_cfg` \| `_cfrm` \| `_cg` \| `_cp` |
| `tipo_selecao` | `vestibular` (CFG), `programa_ingresso` (CFrm, CG, CP) |
| `validacao_status` | `valido` iff `link_edital` + `data_fim_inscricao` |

`link_inscricao` fica em `extras` (portal SIPS ou hash do hub).

## Regras

- Não inventar datas, vagas (exceto CP quando explícito no HTML) ou taxa.
- Descartar PDFs de resultado final / gabarito / listas de aprovados antigas.
- Apply **não** executado nesta wave.

## Última corrida de referência (2026-05-17)

| Métrica | Valor |
|---------|------:|
| Standardized | **5** (CFG ATIVA, CFG RESERVA, CFrm, CG, CP/IME) |
| `valido` | **0** (PDFs escaneados — sem `data_fim_inscricao`) |
| `incompleto` | **5** |
| CP `numero_vagas` | **90** (HTML) |
| Loader dry-run | `errors_count` **0**, `would_upsert` **5** |
| pytest | **7** passed |

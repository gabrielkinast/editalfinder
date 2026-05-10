# Auditoria de itens rejeitados / bloqueados (amostra estruturada)

**Data:** 2026-05-10  
**Restrições:** leitura de relatórios existentes; sem apply, sem Supabase, sem alterar código.

## Origens dos dados

- `audit_reports_credito/lote_inovacao_internacional_onda_c_fix/retransform_by_source.json` — contagens e `motivos_rejeicao_principais` por fonte.
- `audit_reports_credito/lote_credito_multilateral_onda_b_fix/retransform_by_source.json` — Eureka, Fonplata.
- `audit_reports_credito/lote_inovacao_internacional_onda_c_quality_fix_docs/audit_docs_download_failures.json` — falhas `pdf_nao_lido_no_transformer`.
- `audit_reports_main_pipeline/post_daily_warning_examples.json` — exemplos de `setor_estrategico_muito_amplo`, `suspeito_ativo_true`, `titulo_ruidoso`.
- `japan_jaea/outputs/latest_error.json`, `china_norinco/outputs/latest_error.json` — `coleta_vazia_sem_confirmacao`.

## Legenda de classificação de motivo

| Categoria | Critério usado nesta auditoria |
|-----------|-------------------------------|
| `login_autenticacao` | SSO/Hicx/ideas.esa; título “Login…” |
| `texto_curto` | (reservado) poucos tokens após normalização |
| `institucional_generico` | Página de produto banco / “Quem Somos” / RH Fonplata |
| `faq` | FAQ explícito (ex.: sbir.gov/faq) |
| `pagina_hub` | Agências participantes, impact, topics index |
| `parser_falhou` | Coleta vazia com URLs parciais sem confirmação |
| `documento_pdf_sem_texto` | `pdf_nao_lido_no_transformer` em auditoria de docs |
| `WAF/bloqueio` | Listing `ok: false` em domínio internacional |
| `outro` | API técnica classificada como edital |

Cada registo em **`blocked_rejected_items_audit.json`** inclui: `fonte`, `titulo`, `link`, `motivo_original`, `tipo_erro`, `categoria`, `parece_oportunidade_acionavel`, `eh_ruido_real`, `recomendacao`.

## Destaques qualitativos

1. **ESA STAR:** um único bruto aponta para **publicação SSO**; o transformer corretamente marca **login** — recuperação passa por **fonte alternativa pública** (ITT list na ESA), não por “abrir” o SSO no pipeline de edital.
2. **DoD SBIR:** convivem **hub útil** (`/topics`) com **FAQ, API e páginas institucionais** — estes últimos devem permanecer **fora** do tipo edital acionável.
3. **BASA:** mistura **linhas FNO/FUNGENTUR** (possível valor) com **renegociação / produto** (ruído ou baixa prioridade) e **Conta PJ** (ruído confirmado).
4. **Fornecedores (BAE):** exemplo explícito de **login portal** — alinhado à política de não promover login isolado.

## Tabela resumo (amostra)

| ID auditoria | Fonte | Título (curto) | Categoria | Acionável? |
|--------------|-------|----------------|-----------|------------|
| ESA-STAR-001 | ESA STAR | esa-star Publication | login | Sim (via canal público) |
| DOD-SBIR-FAQ-001 | DoD SBIR | FAQ | faq | Não |
| DOD-SBIR-HUB-002 | DoD SBIR | Data Resources (API) | outro | Não |
| BASA-FNO-001 | BASA | FNO Biodiversidade | institucional | Parcial |
| BAE-LOGIN-001 | BAE | Login to your account | login | Não |

Lista completa e campos normalizados: **`blocked_rejected_items_audit.json`**.

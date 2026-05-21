# Wave 1 — Decisão da fonte piloto

## Opções avaliadas

| Critério | Vunesp (`www.vunesp.com.br`) | PCI Concursos | Cebraspe |
|----------|------------------------------|---------------|----------|
| Facilidade de extração | **Média** — páginas institucionais, mas respostas **403** com `urllib` padrão (WAF/bot filtering) no ambiente de teste | **Média** — listagem `/concursos` + páginas `/noticias/<slug>` em HTML estável | **Média** — tabelas e PDFs; mais parsing |
| Estabilidade | Alta (instituição) | Alta (site maduro) | Alta |
| Qualidade do dado | Alta (fonte primária) | **Média** — agregador; texto editorial; link oficial nem sempre óbvio | Alta quando edital oficial linkado |
| Cobertura | Boa (SP e contratos) | **Muito ampla** (nacional) | Forte em concursos públicos |
| Risco legal / robots | robots permissivo; risco WAF | `robots.txt` permite `/` com exclusões (`*.php`, `/pdf/`); **não** seguir URLs `.php` | robots a verificar; uso moderado |
| Mapeamento `concurso_selecao` | Excelente | Bom com `fonte_tipo = agregador`, `extras.official_link_missing` quando aplicável | Excelente |

## Escolha: **PCI Concursos** (piloto)

**Justificativa:**

1. **Acessibilidade técnica imediata:** a página `https://www.pciconcursos.com.br/concursos` responde **200** com User-Agent identificável e texto útil; **Vunesp** devolveu **403** no mesmo ambiente com cliente HTTP simples — piloto Vunesp exigiria browser headless ou acordo institucional antes de automatizar.
2. **Cobertura:** PCI agrega muitos anúncios nacionais num único ponto de entrada — ideal para validar pipeline (crawler → standardized → loader dry-run) com volume pequeno mas real.
3. **Robots:** verificámos `robots.txt` — caminhos de listagem e notícias usados **não** estão em `Disallow` (evitamos `*.php`, `/pdf/`, etc.).
4. **Riscos mitigados:** limite baixo de itens (`--max-items`), pausa entre pedidos, sem scraping de fóruns (`/discussao/`), `validacao_status = incompleto` por defeito quando datas/salário/vagas não forem extraídos com segurança, e `extras.official_link_missing = true` quando não houver URL oficial clara no HTML.

**Vunesp** mantém-se como **prioridade 1** para a *segunda* implementação (headers/cookies ou parceria / export manual controlado).

**Cebraspe** como candidato forte quando quisermos menos ruído editorial e mais ligação direta a edital.

## Referências no repositório

- Crawler: `concursos/main_pci_concursos.py`
- Helpers: `concursos/common.py`
- Documentação operacional: `docs/CONCURSOS_WAVE1_CRAWLER_PILOT.md`

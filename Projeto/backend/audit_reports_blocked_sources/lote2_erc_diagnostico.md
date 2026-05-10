# Lote 2 — Diagnóstico ERC (European Research Council)

## Resumo executivo

- **Brutos:** 8 registos em `erc/outputs/erc_editais.json`, todos com URL sob `https://erc.europa.eu/apply-grant/…` (páginas oficiais de esquemas ou satélites do hub).
- **Transformação (dry-run):** 8 recebidos → **8 transformados**, **0 rejeitados** (`audit_reports_blocked_sources/lote2_fix_erc/retransform_by_source.json`).
- **Incompletos:** 8 (principalmente **prazo explícito** ausente ao nível do registo; calendário indicativo está muitas vezes no Work Programme em PDF).
- **Causa histórica de lista vazia:** `https://erc.europa.eu/apply-grants` (plural) devolvia **404**; o hub correto é `https://erc.europa.eu/apply-grant` (singular).

## Classificação dos links (grant real vs ruído)

| Link | Interpretação |
|------|----------------|
| `…/starting-grant`, `consolidator-grant`, `advanced-grant`, `synergy-grant`, `proof-concept`, `erc-plus-grant` | **Páginas de esquema / grant** oficiais; ancoragem a PDFs Horizon (WP, regras, guias). **Não** são notícias isoladas nem páginas institucionais genéricas sem objeto de funding. |
| `…/non-european-researchers` | **Elegibilidade e financiamento adicional** para investigadores; documento de países associados; continua no âmbito de oportunidade ERC. |
| `…/additional-opportunities` | **Hub secundário** (empregos em equipas ERC, visitas nacionais, mentoring, Ucrânia); conteúdo **híbrido** mas ligado a carreira e funding em torno do ERC. |

Nenhum item atual é “só notícia” ou “só institucional” no sentido de home genérica sem objeto de grant/call.

## Motivos de rejeição (estado atual)

- **Nenhum** no último dry-run (`motivos_rejeicao_principais` vazio no `retransform_by_source`).

### Histórico (antes das correções locais)

- **Falso positivo de login** no opportunity gate para **Synergy** e **ERC Plus**, apesar de URLs públicas sob `/apply-grant/`. Mitigado com continuação suave e categorização `grant` no ramo ERC, sem alterar o gate global.

## Tipos de conteúdo possíveis (taxonomia pedida)

| Tipo | Ocorrência neste lote |
|------|------------------------|
| **grant** | Dominante nos seis esquemas principais (+ PoC, Plus). |
| **call_for_proposals** | Informação de chamadas e prazos (muito no texto/PDF do WP 2026). |
| **bolsa_pesquisa** | Enquadramento de investigadores / reforços (ex.: non-European). |
| **pesquisa_cientifica** | Objeto transversal dos esquemas. |
| **calendário de chamadas** | Não como página dedicada única; dados dispersos + PDF. |
| **notícia institucional** | Filtrada no crawler onde possível (ex. painéis, empregos). |
| **página genérica** | Evitada pelo hub e filtros de slug. |

## Auditorias executadas

1. **Retransform (dry-run):** `audit_reports_blocked_sources/lote2_fix_erc/`
2. **Semântica:** `audit_reports_blocked_sources/lote2_fix_erc_semantic/` — **flags totais vazias** em `audit_semantic_summary.json` (8 itens).
3. **Documentos:** `audit_reports_blocked_sources/lote2_fix_erc_docs/` — **0 perdas** de ligação bruto→transformado→payload; downloads com falha coerente com `pdf_skip`/não ir buscar PDFs na auditoria.

## Qualidade e notas (ready_with_notes)

Pontos fortes: títulos e descrições ricas, **documentos oficiais preservados**, `tipo_oportunidade` e `tipo_recurso` coerentes (`grant` / `chamada_publica` + **fomento** após calibração).

Pontos a melhorar numa iteração seguinte (não bloqueiam a recomendação abaixo):

- Campo **`valor`** por vezes em **R$** por heurística brasileira sobre texto em **EUR**.
- **`codigo_oportunidade`** ocasionalmente truncado (ex.: fragmento tipo `entifier`).
- **`publico_alvo` / setores** por vezes estreitos ou amplos demais (ex.: ICT) sem evidência forte no título.

## Readiness recomendado

**`ready_with_notes`**

Critérios atendidos: transformados > 0; URLs são esquemas ou páginas satélite oficiais ERC; classificação coerente; descrição útil; documentos preservados; auditoria semântica sem flags agregadas.

Critérios ainda não plenos para **`ready`** sem notas: todos os itens **incompletos** no validador (prazo ao nível de registo); normalização de valor/código/setor; eventual refinamento da página “Additional opportunities” se se quiser apenas calls com identificador explícito.

**Não recomendado:** `blocked` (há conteúdo de funding real). **`needs_manual_review`** só se a política de produto excluir páginas híbridas como `additional-opportunities`.

---

Ficheiros irmãos: `lote2_erc_diagnostico.json`, `lote2_erc_examples.json`.

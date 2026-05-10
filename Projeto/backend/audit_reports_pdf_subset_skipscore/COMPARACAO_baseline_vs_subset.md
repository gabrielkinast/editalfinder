# Comparação: baseline global vs subset (PDF + gate)

**Data desta análise:** 2026-05-01 (UTC)

## 1. O que foi pedido

- Corrida **subset** com `--no-skip-pdf --sources aneel,bndes,cnpq,finep --max-items 25`.
- Variável **`EDITALFINDER_SKIP_SCORING=true`** numa das corridas para medir impacto nas **rejeições** (o `opportunity_gate` corre **antes** do score; espera-se impacto **nulo** nas contagens de rejeição).

## 2. Comandos executados

```powershell
cd "d:\Computational_Physics\My Projects\edital"

$env:EDITALFINDER_SKIP_SCORING='true'
python scripts/audit_pipeline.py --no-skip-pdf --sources aneel,bndes,cnpq,finep --max-items 25 --output-dir audit_reports_pdf_subset_skipscore

Remove-Item Env:EDITALFINDER_SKIP_SCORING -ErrorAction SilentlyContinue
python scripts/audit_pipeline.py --no-skip-pdf --sources aneel,bndes,cnpq,finep --max-items 25 --output-dir audit_reports_pdf_subset_withscore
```

## 3. Baseline de referência (auditoria global anterior)

Ficheiro: `audit_reports/audit_relatorio_tecnico.md` (corrida **PDF off**, **95** ficheiros, **961** itens, max 25/itens por ficheiro).

| Motivo (rejection_reason) | Contagem |
|--------------------------|-----------:|
| Pagina de login ou autenticacao | 242 |
| Relevancia limite: poucos sinais de oportunidade | 165 |
| Pontuacao abaixo do minimo (oportunidade nao evidenciada) | 161 |
| titulo_ruido_exato | 11 |
| noticia_sem_oportunidade | 9 |
| Acesso restrito (IP/campus/intranet) | 1 |

**Interpretação:** o baseline **não** é comparável 1:1 ao subset (universo de fontes e amostras diferentes), mas serve para contextualizar o peso histórico de **login** vs **relevância/pontuação**.

## 4. Resultado do subset (68 itens, 4 ficheiros, PDF **ligado**)

| Métrica | `audit_reports_pdf_subset_skipscore` | `audit_reports_pdf_subset_withscore` |
|---------|----------------------------------------|----------------------------------------|
| Itens analisados | 68 | 68 |
| `pdf_skip` | false | false |
| **Rejeições — Relevancia limite** | **56** | **56** |
| **Rejeições — Pontuacao abaixo do minimo** | **8** | **8** |
| **Rejeições — Pagina de login** | **0** | **0** |

**Por fonte (transformados / rejeitados / amostra):**

| Fonte | Skip score | Com score |
|-------|------------|-----------|
| aneel | 3 / 22 / 25 | idem |
| bndes | 0 / 19 / 19 | idem |
| cnpq | 0 / 14 / 14 | idem |
| finep | 1 / 9 / 10 | idem |

### Conclusão A — `EDITALFINDER_SKIP_SCORING`

As contagens de rejeição do **`opportunity_gate`** são **idênticas** com e sem scoring, como esperado (o score de relevância do transformer corre **depois** do gate, no ramo de PDF).

### Conclusão B — “antes vs depois” do ajuste de login (gate)

Não foi refeita aqui uma corrida com o **código antigo** do gate (exigiria checkout de commit anterior). O que se observa **empiricamente** neste subset:

- **Zero** rejeições por **«Pagina de login ou autenticacao»** nas 4 fontes com **PDF ligado**, enquanto no baseline global (PDF off, muitas fontes) havia **242** ocorrências agregadas — parte é **volume/universo**, parte é o **afinamento** de login fraco + contexto `gov.br`/bancos públicos (`login_fraco_suprimido_contexto_publico` em `CORE/opportunity_gate.py`).

### Conclusão C — próximo gargalo visível no subset

As rejeições passam a ser **dominadas por «Relevancia limite»** (56/64 rejeições agregadas neste subset), ou seja: o trabalho seguinte provável é **calibrar score de oportunidade do gate** (limiares / sinais para PDF só com metadado HTML, BNDES WCM, etc.), não correr atrás de 46 crawlers sem evidência.

## 5. Artefactos

- `audit_reports_pdf_subset_skipscore/` — auditoria completa com `EDITALFINDER_SKIP_SCORING=true`.
- `audit_reports_pdf_subset_withscore/` — mesma corrida com scoring padrão.
- `audit_reports/audit_relatorio_tecnico.md` — baseline global citado acima.

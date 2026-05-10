# Plano de recuperação por ondas

**Data:** 2026-05-10  
**Estado:** planeamento apenas (sem código, sem crawlers pesados, sem apply, sem Supabase).

## Onda Recovery A (no máximo 3 fontes)

Foram escolhidas três fontes com melhor relação **valor / risco / evidência em relatórios existentes**:

1. **`esa_star`** — grupo `recovery_esa_star`  
2. **`dod_sbir_sttr`** — grupo `recovery_dod_sbir`  
3. **`banco_da_amazonia` (BASA)** — grupo `recovery_basa`  

O conjunto **`recovery_supplier_portals`** fica como **Onda B sugerida** (múltiplas fontes, padrão comum), fora do limite de três da Onda A.

---

### 1) `recovery_esa_star`

**Investigar:** listagens públicas de Open ITT na ESA; existência de RSS/sitemap/export; se algum ITT tem metadados públicos fora do SSO.

**Crawler/parser (futuro):** seeds na página pública; bloqueio de itens cujo único URL seja `*.sso.esa.int` sem evidência de tender público.

**Ficheiros prováveis (futuro):** `esa_star/main_esa_star.py`, regras de rejeição “login” no pipeline de transform.

**Riscos:** ToS, mudança de SSO, falso negativo se conteúdo só existir atrás de login.

**`ready_with_notes`:** pelo menos um item com URL pública ESA ou documento ITT; diagnóstico sem “0 transformados com bruto”.

**Manter `blocked`:** se a única fonte estável continuar a ser SSO sem metadado público.

---

### 2) `recovery_dod_sbir`

**Investigar:** uso da API como **fonte técnica** (não como linha de edital); HTML de `/topics` e filhos com deadline; denylist para `/faq`, `/api`, `/data-resources`, `/impact`, `/participating-agencies` quando forem só contexto.

**Crawler/parser (futuro):** allowlist/denylist de path; heurística de deadline ou topic ID.

**Ficheiros prováveis (futuro):** crawler `dod_sbir_sttr`, calibração de `tipo_oportunidade` hub vs oportunidade.

**Riscos:** mudança de layout; duplicata hub vs topic.

**`ready_with_notes`:** queda de `setor_estrategico_muito_amplo` em URLs de hub; itens com prazo ou topic explícito.

**Manter bloqueio / excluir de edital:** se só hubs estáveis existirem sem descida para topics.

---

### 3) `recovery_basa`

**Investigar:** padrões de URL e texto para FNO, FUNGETUR, PRONAF, Finame; critérios para `valido` vs `suspeito`; denylist permanente para Conta PJ / internet banking.

**Crawler/parser (futuro):** extração de condições comerciais; `tipo_oportunidade` alinhado a linha de crédito quando aplicável.

**Ficheiros prováveis (futuro):** crawler BASA, calibrações em transformer/taxonomia.

**Riscos:** classificar marketing como chamada; efeitos em `credito_tipo_recurso_incoerente`.

**`ready_with_notes`:** queda forte de `suspeito_ativo_true` com notas sobre exceções documentadas.

**Manter estratégia conservadora:** se o site exigir sessão ou a separação automática falhar sem curadoria.

---

## Onda B (sugestão): `recovery_supplier_portals`

BAE, GD, Lockheed, Rheinmetall, Thales — **padrão único** (supplier + `access_limited` quando couber). Só depois da Onda A por custo de análise e risco de login.

## Métricas de verificação pós-implementação (futuro)

- `validate_full_staging_after_daily.py --staging` com `ok=true`.  
- Totais de `suspeito_ativo_true` (BASA, DoD).  
- `setor_estrategico_muito_amplo` em DoD SBIR.  
- `esa_star`: `standardized_count > 0` **ou** decisão explícita de manter `blocked`.

JSON estruturado: **`recovery_wave_plan.json`**.

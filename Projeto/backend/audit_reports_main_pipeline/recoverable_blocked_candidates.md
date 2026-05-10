# Candidatos a recuperação (bloqueados / rejeitados / suspeitos)

**Data:** 2026-05-10  
**Escopo:** priorização qualitativa; não altera readiness nem código.

## Critérios de recuperabilidade

- **high:** fonte oficial; indícios de call/procurement; bloqueio por técnica (PDF, parser, falso login); não é FAQ/contact puro.
- **medium:** hub ou linha de produto que pode ser oportunidade após curadoria ou melhoria de prazo/tipo.
- **low:** WAF, login obrigatório, ou coleta vazia não explicada.
- **none:** FAQ, about, careers, API/docs como edital, conta genérica.

## Candidatos prioritários (resumo)

| Fonte | Recuperabilidade | Ação | Nota |
|-------|------------------|------|------|
| esa_star | high | Fonte alternativa pública (Open ITT / export) | Não liberar SSO como edital |
| dod_sbir_sttr | high | Afinar crawler para **topics** filhos | Excluir FAQ/API/impact como edital |
| ukri_funding | high | Pipeline PDF + HTML | Já gera valor; falha é técnica |
| banco_da_amazonia (BASA) | medium | Curadoria FNO/FUNGETUR/PRONAF | Separar linha real de página genérica |
| eurostars | medium | Parser + nota readiness | Volume baixo |
| fonplata | medium | Curadoria RH vs projeto | needs_manual_review |
| bae_systems_suppliers | low | Manter suspeito/bloqueado | Login Hicx |
| general_dynamics_suppliers (FAQ) | none | Inativo / ruído | Não recuperar como edital |
| japan_jaea | low | Soft-continue | Validar seletores |
| china_norinco | low | Alternativa / acesso | WAF ou estrutura |

Detalhe campo a campo: **`recoverable_blocked_candidates.json`**.

## Casos explícitos pedidos no briefing

### ESA STAR

Estado: **blocked** em `source_readiness.json`. Bruto único = portal **SSO** (`esastar-publication-ext.sso.esa.int`). **Recuperação:** página pública **Open Invitations to Tender** na ESA + eventual feed/export — **não** promover login isolado.

### DoD SBIR/STTR

Em staging, exemplos de **hub** (Participating Agencies, Impact, Portfolio, Data Resources, FAQ) convivem com **Funding Opportunities /topics**. **Manter** API/resource **fora** de edital; **focar** ingestão em **topics** com deadlines reais.

### BASA

22× `suspeito_ativo_true`: mistura **Renegociação** (ruído provável), **FNO/FUNGENTUR** (possível linha real), **Giro produtor** (meio-termo). **Conta PJ** = ruído confirmado.

### Fornecedores internacionais

Separar **portal login** (BAE Hicx) de **cadastro público com instruções**. FAQ (GD) = **none**.

### NUCLEP / AMAZUL

**Quem Somos** / institucional: **none** para edital. Licitações reais: outro padrão de URL e texto — exigem **semente** de procurement, não página corporativa.

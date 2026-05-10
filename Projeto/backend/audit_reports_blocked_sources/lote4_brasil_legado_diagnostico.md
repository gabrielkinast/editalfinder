# Lote 4 — Brasil / legado: diagnóstico de fontes problemáticas

**Data:** 2026-05-01  
**Fontes:** amazul, marinha, dcta_ita_iae, faperg, apex, ambev, science_scraper  

**Restrições respeitadas:** sem loader apply, sem Supabase, sem migrations, sem alteração global do `opportunity_gate`, sem atualização automática de readiness. Evidência de retransformação em `audit_reports_blocked_sources/lote4_brasil_legado_retransform/retransform_by_source.json`.

## Resumo numérico

| Fonte            | Brutos | Transformam | Rejeitados |
|------------------|--------|-------------|------------|
| amazul           | 0      | 0           | 0          |
| marinha          | 0      | 0           | 0          |
| dcta_ita_iae     | 0      | 0           | 0          |
| faperg           | 0      | 0           | 0          |
| apex             | 1      | 0           | 1          |
| ambev            | 7      | 0           | 7          |
| science_scraper  | 14     | 0           | 14         |

## Por fonte (10 perguntas)

### amazul

1. **Crawler roda?** Sim (smoke concluiu com 0 registros).  
2. **Output bruto?** `amazul/outputs/amazul_editais.json`  
3. **Brutos:** 0  
4. **Transformam:** 0  
5. **Rejeitados:** 0  
6. **Motivos:** —  
7. **Oportunidade real?** Não no estado atual.  
8. **Relevante ao escopo?** Sim (licitações/chamadas nuclear-defesa), em tese.  
9. **Problema:** crawler/heurística; link antigo tipo índice de licitações não refletido no bruto (`old_vs_new` no retransform).  
10. **Continuar?** Sim, após corrigir alvos ou validar URLs atuais.

### marinha

1. **Crawler roda?** Sim.  
2. **Output bruto?** `marinha/outputs/marinha_editais.json`  
3. **Brutos:** 0  
4. **Transformam:** 0  
5. **Rejeitados:** 0  
6. **Motivos:** —  
7. **Oportunidade real?** Não.  
8. **Relevante ao escopo?** Sim (concursos/licitações).  
9. **Problema:** crawler/heurística; índice `/editais` não gera item.  
10. **Continuar?** Sim, com mapeamento de páginas reais de chamada.

### dcta_ita_iae

1. **Crawler roda?** Sim.  
2. **Output bruto?** `dcta_ita_iae/outputs/dcta_ita_iae_editais.json`  
3. **Brutos:** 0  
4. **Transformam:** 0  
5. **Rejeitados:** 0  
6. **Motivos:** —  
7. **Oportunidade real?** Não.  
8. **Relevante ao escopo?** Sim.  
9. **Problema:** crawler/heurística (sem fallback de índice institucional).  
10. **Continuar?** Sim.

### faperg

1. **Crawler roda?** Sim.  
2. **Output bruto?** `faperg/outputs/faperg_editais.json`  
3. **Brutos:** 0  
4. **Transformam:** 0  
5. **Rejeitados:** 0  
6. **Motivos:** —  
7. **Oportunidade real?** Não observado.  
8. **Relevante ao escopo?** Sim (fomento estadual RS).  
9. **Problema:** crawler/acesso a editais.  
10. **Continuar?** Sim; alta prioridade se cobertura RS for obrigatória.

### apex

1. **Crawler roda?** Sim.  
2. **Output bruto?** `apex/outputs/apex_editais.json`  
3. **Brutos:** 1  
4. **Transformam:** 0  
5. **Rejeitados:** 1  
6. **Motivos:** `titulo_ruido_exato` (título literal “Menu”).  
7. **Oportunidade real?** Não — calendário/eventos, não chamada.  
8. **Relevante ao escopo?** Parcial (instituição pode ter programas; bruto atual não os mostra).  
9. **Problema:** crawler + ruído de extração + confusão eventos vs fomento.  
10. **Continuar?** Sim, após refinar fontes e filtros.

### ambev

1. **Crawler roda?** Sim.  
2. **Output bruto?** `ambev/outputs/ambev_editais.json`  
3. **Brutos:** 7  
4. **Transformam:** 0  
5. **Rejeitados:** 7  
6. **Motivos:** pontuação abaixo do mínimo (6); relevância limite (1).  
7. **Oportunidade real?** Parcial — *challenges* 100accelerator (inovação aberta).  
8. **Relevante ao escopo?** Parcial — depende de incluir corporate open calls no produto.  
9. **Problema:** gate (sem alterar o global), texto EN, poucos sinais lexicais de edital público.  
10. **Continuar?** Condicional até definição de escopo; se incluir, calibrar só nesta fonte.

### science_scraper

1. **Crawler roda?** Sim; log com **404** em URL AEB (`gov.br/.../editais-e-chamadas-publicas-1`).  
2. **Output bruto?** `science_scraper/outputs/science_editais.json`  
3. **Brutos:** 14  
4. **Transformam:** 0  
5. **Rejeitados:** 14  
6. **Motivos:** todos pontuação abaixo do mínimo.  
7. **Oportunidade real?** Não como “edital” do pipeline — sobretudo eventos EC e páginas temáticas.  
8. **Relevante ao escopo?** Fraco para edital/fomento BR atual.  
9. **Problema:** ruído (agenda), gate, idioma, URL quebrada em uma seed.  
10. **Continuar?** Rever produto: candidato a notícias/agenda, não tabela de edital; manter fora ou bloqueado no pipeline atual.

## Recomendações (sem alterar readiness automaticamente)

| Ação | Fontes |
|------|--------|
| **Corrigir agora** (crawler/URLs/heurística local) | apex (eliminar “Menu”/eventos; apontar para programas reais), faperg, amazul, marinha, dcta_ita_iae |
| **Manter blocked** (até decisão) | science_scraper no fluxo de edital |
| **needs_manual_review** | ambev (política de escopo open innovation), apex (lista oficial de chamadas vs marketing) |
| **Fora do escopo do pipeline atual** | science_scraper como fonte principal de edital BR (conteúdo majoritariamente agenda/internacional) |

## Artefatos gerados

- `lote4_brasil_legado_diagnostico.json` — diagnóstico estruturado + recomendações agregadas  
- `lote4_brasil_legado_by_source.json` — métricas e classificação por fonte  
- `lote4_brasil_legado_examples.json` — exemplos de bruto onde há itens  

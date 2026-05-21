# Plano de recovery — classificação FAPESC (dados no banco)

## Âmbito

Este documento é uma **proposta** para quando a auditoria SQL confirmar que `public.edital` (ou camadas upstream) contém `setor_estrategico` / `area_tecnologica` **incorrectos ou excessivos** para editais gerais FAPESC.

**Não** executar os passos automaticamente a partir deste repositório. **Não** alterar schema sem revisão explícita. **Não** mascarar silenciosamente erros graves: o frontend já separa e humaniza a exibição; a recovery trata da **verdade dos dados**.

## Objetivos

1. Identificar linhas FAPESC com taxonomia suspeita (lista de slugs conhecidos ou regra por título).
2. Opcionalmente **limpar** ou **reclassificar** campos (`setor_estrategico`, `area_tecnologica`) com base em regras aprovadas pelo negócio.
3. Registar auditoria (`atualizado_em`, comentário em `extras` ou tabela de histórico, se existir).

## Pré-requisitos

- Backup ou staging.
- Query de leitura (ver `EDITAIS_CLASSIFICACAO_FAPESC_DIAGNOSTICO.md`) que quantifica linhas afectadas.
- Definição de **“suspeito”** (ex.: título contém “bolsa”, “pesquisa”, “inovação” **e** `setor_estrategico` contém tokens `defesa`, `cyber`, `aeroespacial`).

## Opções de recovery (exemplos — não executar cegamente)

### A) Limpeza conservadora (só slugs de defesa/ciber em editais “genéricos”)

```sql
-- RASCUNHO — ajustar critérios WHERE antes de correr
BEGIN;
UPDATE public.edital e
SET
  setor_estrategico = ARRAY[]::text[],
  area_tecnologica = ARRAY[]::text[],
  atualizado_em = now()
WHERE e.fonte_recurso ILIKE '%FAPESC%'
  AND (
    EXISTS (
      SELECT 1 FROM unnest(coalesce(e.setor_estrategico, '{}')) s
      WHERE lower(s::text) ~ '(defesa|defense|cyber|aeroespacial)'
    )
  )
  AND lower(coalesce(e.titulo, '')) ~ '(bolsa|pesquisa|inovação|fomento|auxílio|auxilio|chamada pública)';
-- Revisar rowcount; COMMIT ou ROLLBACK;
ROLLBACK;
```

### B) Repovoar a partir de `extras` legado

Só se existir convenção documentada de onde repor valores “bons”. Requer script dedicado e validação humana.

### C) Reprocessar via pipeline Python

Preferível a longo prazo: corrigir o classificador na origem. Fora do âmbito deste ficheiro se não houver diagnóstico no backend.

## O que não fazer

- Apagar editais inteiros.
- Desactivar RLS de outras tabelas como “solução”.
- `service_role` no frontend.

## Validação pós-recovery

- Reexecutar a query de amostra FAPESC.
- Abrir página Editais e confirmar cards + modal.
- `npm run build` no frontend após qualquer alteração de código relacionada.

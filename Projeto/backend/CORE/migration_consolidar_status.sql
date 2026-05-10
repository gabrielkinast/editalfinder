-- ============================================================
-- MIGRAÇÃO: CONSOLIDAÇÃO DE STATUS E ESTADO EM SITUACAO
-- ============================================================
-- AVISO: remove as colunas legadas `estado` e `status` da tabela `edital`
-- (valores de workflow: Ativo/Encerrado). NÃO executar depois da secção 7
-- de `schema_sql_completo.sql` se já existir a coluna geográfica `estado`
-- (UF/município) — nesse caso, esta migração é apenas para bases antigas
-- antes do schema estendido, ou deve ser adaptada (renomear colunas antes).
-- ============================================================

-- 1. Atualizar a coluna situacao com base nos valores de estado e status
-- Prioridade: se situacao for 'Aberto' ou NULL, tenta pegar do estado ou status.
update public.edital
set situacao = coalesce(
  case 
    when estado in ('Ativo', 'Encerrado', 'Em Elaboração', 'Suspenso') then estado
    when status in ('Ativo', 'Encerrado', 'Suspenso') then status
    else situacao
  end,
  'Aberto'
)
where situacao is null or situacao = 'Aberto';

-- 2. Remover índices antigos
drop index if exists public.idx_edital_estado;

-- 3. Remover as colunas redundantes
alter table public.edital drop column if exists estado;
alter table public.edital drop column if exists status;

-- 4. Garantir que situacao tenha um índice para performance
create index if not exists idx_edital_situacao on public.edital (situacao);

-- 5. Adicionar uma constraint para garantir valores válidos (opcional, mas recomendado para produção)
-- alter table public.edital add constraint chk_edital_situacao check (situacao in ('Aberto', 'Encerrado', 'Em Elaboração', 'Suspenso', 'Retificado'));

raise notice 'Migração concluída com sucesso: status e estado consolidados em situacao.';

-- ============================================================
-- EditalFinder — Tabela de feedback/reporte em editais (FUTURO)
-- NÃO executar automaticamente. Revisar RLS e índices no ambiente.
-- ============================================================

begin;

create table if not exists public.edital_feedback (
  id_feedback uuid primary key default gen_random_uuid(),
  id_edital bigint references public.edital(id_edital) on delete set null,
  id_usuario bigint references public.usuario(id_usuario) on delete set null,
  tipo_feedback text not null,
  comentario text,
  status text not null default 'novo',
  prioridade text default 'normal',
  fonte_recurso text,
  edital_titulo text,
  edital_link text,
  extras jsonb default '{}'::jsonb,
  criado_em timestamptz default now(),
  atualizado_em timestamptz default now(),
  constraint edital_feedback_status_check
    check (status in ('novo', 'em_analise', 'resolvido', 'ignorado')),
  constraint edital_feedback_prioridade_check
    check (prioridade in ('baixa', 'normal', 'alta', 'critica')),
  constraint edital_feedback_tipo_check
    check (tipo_feedback in (
      'link_quebrado',
      'nao_e_oportunidade',
      'edital_encerrado',
      'duplicado',
      'informacao_incorreta',
      'outro'
    ))
);

create index if not exists idx_edital_feedback_edital on public.edital_feedback (id_edital);
create index if not exists idx_edital_feedback_usuario on public.edital_feedback (id_usuario);
create index if not exists idx_edital_feedback_status on public.edital_feedback (status);
create index if not exists idx_edital_feedback_criado on public.edital_feedback (criado_em desc);

comment on table public.edital_feedback is
  'Reportes manuais de problemas em editais (aba Editais). Não oculta nem altera edital automaticamente.';

-- RLS (exemplo — ajustar ao cluster)
alter table public.edital_feedback enable row level security;

drop policy if exists edital_feedback_insert_own on public.edital_feedback;
create policy edital_feedback_insert_own
on public.edital_feedback
for insert
to authenticated
with check (
  id_usuario is null
  or exists (
    select 1 from public.usuario u
    where u.id_usuario = edital_feedback.id_usuario
      and u.auth_user_id = auth.uid()
  )
);

drop policy if exists edital_feedback_select_own on public.edital_feedback;
create policy edital_feedback_select_own
on public.edital_feedback
for select
to authenticated
using (
  exists (
    select 1 from public.usuario u
    where u.id_usuario = edital_feedback.id_usuario
      and u.auth_user_id = auth.uid()
  )
);

-- TODO: policy admin/suporte SELECT/UPDATE em todos os feedbacks

commit;

-- NOTIFY pgrst, 'reload schema';

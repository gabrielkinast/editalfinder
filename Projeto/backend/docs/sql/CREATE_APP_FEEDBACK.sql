-- ============================================================
-- EditalFinder — Feedback universal da aplicação (app_feedback)
-- NÃO executar automaticamente. Revisar RLS no ambiente.
-- Separado de public.edital_feedback (problemas em edital específico).
-- ============================================================

begin;

create table if not exists public.app_feedback (
  id_feedback uuid primary key default gen_random_uuid(),
  id_usuario bigint references public.usuario(id_usuario) on delete set null,
  user_auth_id uuid,
  tipo_feedback text not null,
  origem text not null,
  rota text,
  pagina text,
  componente text,
  acao text,
  mensagem_erro text,
  stack_erro text,
  comentario text,
  status text not null default 'novo',
  prioridade text not null default 'normal',
  user_agent text,
  app_version text,
  extras jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint app_feedback_status_check
    check (status in ('novo', 'em_analise', 'resolvido', 'ignorado')),
  constraint app_feedback_prioridade_check
    check (prioridade in ('baixa', 'normal', 'alta', 'critica')),
  constraint app_feedback_tipo_check
    check (tipo_feedback in (
      'erro_pagina',
      'erro_global',
      'erro_api',
      'botao_nao_funciona',
      'bug_visual',
      'lentidao',
      'dado_incorreto',
      'outro'
    ))
);

create index if not exists idx_app_feedback_usuario on public.app_feedback (id_usuario);
create index if not exists idx_app_feedback_auth on public.app_feedback (user_auth_id);
create index if not exists idx_app_feedback_origem on public.app_feedback (origem);
create index if not exists idx_app_feedback_tipo on public.app_feedback (tipo_feedback);
create index if not exists idx_app_feedback_status on public.app_feedback (status);
create index if not exists idx_app_feedback_created on public.app_feedback (created_at desc);

comment on table public.app_feedback is
  'Reportes de problemas da aplicação (telas, erros globais, API, UX). Não substitui edital_feedback.';

alter table public.app_feedback enable row level security;

drop policy if exists app_feedback_insert_authenticated on public.app_feedback;
create policy app_feedback_insert_authenticated
on public.app_feedback
for insert
to authenticated
with check (
  user_auth_id is null
  or user_auth_id = auth.uid()
  or exists (
    select 1 from public.usuario u
    where u.id_usuario = app_feedback.id_usuario
      and u.auth_user_id = auth.uid()
  )
);

drop policy if exists app_feedback_select_own on public.app_feedback;
create policy app_feedback_select_own
on public.app_feedback
for select
to authenticated
using (
  user_auth_id = auth.uid()
  or exists (
    select 1 from public.usuario u
    where u.id_usuario = app_feedback.id_usuario
      and u.auth_user_id = auth.uid()
  )
);

-- TODO: policy admin/suporte SELECT/UPDATE em todos os app_feedback

commit;

-- NOTIFY pgrst, 'reload schema';

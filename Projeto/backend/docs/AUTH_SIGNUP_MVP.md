# Autenticação — Criação de conta (MVP)

## Visão geral

Na tela de **Login** (`src/pages/Login.jsx`) existe um modo alternável **Entrar** / **Criar conta**. O registo grava na tabela **`public.usuario`** via Supabase (chave **anon**), com os mesmos campos usados pelo login existente. Após criar a conta com sucesso, o fluxo faz **login automático** (sessão em `localStorage` + `AuthContext`) e redireciona para o dashboard.

## Tabela e campos gravados

| Coluna | Valor no registo público |
|--------|---------------------------|
| `nome` | Informado pelo utilizador (trim) |
| `nome_email` | E-mail normalizado (`trim` + minúsculas) |
| `senha` | Texto indicado (MVP — ver limitações) |
| `tipo_usuario` | **`Consultor`** (fixo) |
| `nivel_acesso` | **`2`** (fixo) |
| `status` | **`Ativo`** (fixo) |

O `id_usuario` é gerado pela base (serial/identity) e devolvido no `INSERT … select` para preencher a sessão (`id_usuario`, `nome`, `email`, `tipo`, `nivel`, `status`).

## Por que o utilizador público não pode criar administrador

A UI de registo **não envia** `tipo_usuario`, `nivel_acesso` nem `status` — estes campos são definidos **apenas** no objeto de insert em `authService.registerUser`. Assim não é possível escalar privilégios para **Administrador** ou outro nível pela tela pública.

## Ficheiros envolvidos

- `src/services/authService.js` — `normalizeAuthEmail`, `registerUser`, login com e-mail normalizado.
- `src/contexts/AuthContext.jsx` — método `register` que chama o service e actualiza `user`.
- `src/pages/Login.jsx` — tabs Entrar/Criar conta, validação, mensagens de erro.
- `src/styles/global.css` — estilos para tabs, alerta, botão secundário e links (compatível com tema claro/escuro).

## Limitações de segurança

1. **Senha em texto plano** na coluna `usuario.senha` — mesmo problema do login legado. **Próximo passo:** hash (bcrypt/argon2) no backend ou migração para **Supabase Auth** (JWT + `auth.users`).
2. **RLS** em `public.usuario`: o insert com anon só funciona se as políticas permitirem; caso contrário o utilizador vê erro genérico. Ajuste de políticas é responsabilidade do projeto Supabase.
3. Não há confirmação de e-mail nem CAPTCHA neste MVP.

## Próximos passos recomendados

- Substituir armazenamento de senha por hash ou Supabase Auth.
- Políticas RLS restritivas em `usuario` (insert apenas para perfis anónimos controlados, ou via Edge Function).
- Opcional: fluxo “esqueci a senha” e verificação de e-mail.

## Testes sugeridos

Ver checklist na entrega do PR (criar conta, duplicado de e-mail, validações, `tipo_usuario = Consultor`, `localStorage` com `id_usuario`, temas claro/escuro, `npm run build`).

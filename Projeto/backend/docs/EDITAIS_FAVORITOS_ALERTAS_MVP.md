# Editais — Favoritos e alertas de prazo (MVP Fase 1)

## Objetivo

Permitir **favoritar / desfavoritar** editais no frontend com persistência em `public.edital_favorito` (soft delete com `ativo=false`), leitura agregada via **`public.vw_editais_favoritos_front`**, e **alerta visual** de prazo nos favoritos (banner na página Editais + badge nos cards quando o edital está favoritado).

Não inclui: backend Python, cron, e-mail, Edge Functions, alteração ao motor do Radar, Portais ou PDF.

## Tabela e view

| Objeto | Uso |
|--------|-----|
| `public.edital_favorito` | `INSERT` ao favorizar; `UPDATE` (`ativo=false`) ao desfavoritar; atualizações de alerta/visualizado quando aplicável. |
| `public.vw_editais_favoritos_front` | `SELECT` para listar favoritos ativos no cliente. |

Campos usados na escrita (MVP): `id_usuario`, `id_edital`, `edital_link`, `edital_titulo`, `edital_fonte`, `prazo_envio`, `status_prazo`, `alerta_ativo`, `alertar_com_dias`, `origem`, `contexto`, `ativo`, `visualizado`, `extras` (JSON), timestamps quando existirem na tabela.

## Variáveis de ambiente

Definidas em `.env.example` e lidas em `src/config/env.js`:

| Variável | Fallback |
|----------|----------|
| `VITE_VIEW_EDITAIS_FAVORITOS` | `vw_editais_favoritos_front` |
| `VITE_TABLE_EDITAL_FAVORITO` | `edital_favorito` |
| `VITE_ENABLE_EDITAL_FAVORITOS` | `true` |

A feature só usa Supabase quando **`VITE_ENABLE_EDITAL_FAVORITOS`** é verdadeiro **e** `VITE_SUPABASE_URL` + chave anon estão configurados **e** existe **`id_usuario` resolvido** (utilizador autenticado com `id_usuario` na sessão — ver abaixo). Caso contrário, a página **Editais** continua com favoritos apenas em **localStorage** (`editais_favoritos_v1`), como antes.

| Variável | Uso |
|----------|-----|
| `VITE_DEV_FAVORITOS_USER_ID` (opcional) | Só em **desenvolvimento**: se o utilizador em sessão não tiver `id_usuario`, o hook usa este número; se ausente, usa **1**. Em **produção** não há este fallback — é obrigatório `id_usuario` após login na tabela `usuario`. |

## Ficheiros criados

- `src/services/favoritosService.js` — leitura da view, escrita na tabela, `toggleFavorito`, `markFavoritoVisualizado`, `updateFavoritoAlerta`, helpers de match (`id_edital` + fallback por link normalizado).
- `src/utils/deadlineAlerts.js` — `parsePrazoEnvio`, `getDaysUntilDeadline`, estados de alerta, labels, variantes de badge, `getFavoriteDeadlineSummary`.
- `src/hooks/useEditalFavorites.js` — estado, `isFavorite`, `toggleFavorite`, `refreshFavorites`, resumo de alertas.

## Ficheiros alterados

- `src/services/authService.js` — `id_usuario` na sessão após login Supabase; demo `admin@finder.com` com `id_usuario` só em DEV.
- `src/hooks/useEditalFavorites.js` — `useAuth`, `resolveFavoriteUserId`, `favoritosRemoteEnabled`, fetch/toggle com `id_usuario`.
- `src/services/favoritosService.js` — leitura/escrita com filtro por utilizador; reativação preservada; sem fallback numérico implícito no service.
- `src/config/env.js` — constantes da feature favoritos.
- `.env.example` — variáveis documentadas (incl. opcional `VITE_DEV_FAVORITOS_USER_ID`).
- `src/pages/Dashboard.jsx` — `favoritosRemote` = `favHook.favoritosRemoteEnabled`; filtro **☆ Favoritos**, banner, chips, export, empty state, badges de prazo.
- `src/components/dashboard/EditalCard.jsx` — estrela e badge de prazo para favoritos.
- `src/pages/RadarFomento.jsx` + `src/components/radar/CardEditalRadar.jsx` — mesmo hook remoto (`contexto: "radar"`) ou `localStorage` por cliente.
- `src/utils/edital/filtersEngine.js` — `toggleSomenteFavoritos` no estado inicial dos filtros.
- `src/styles/global.css` — banner, filtro ativo, faixa de erro de toggle, badge de prazo no card.

## Como favoritar

1. Com Supabase configurado, feature ativa e **`id_usuario` na sessão** (login na tabela `usuario`): clique em **☆** no card (Editais ou Radar).  
2. É feito `INSERT` (ou reactivação) em `edital_favorito` com o **`id_usuario` do utilizador logado**, `origem: "frontend"`, `contexto: "editais"` ou `"radar"`, `alerta_ativo: true`, `alertar_com_dias: 7`, `status_prazo` calculado no cliente.

Identificação: **prioridade** a `id_edital` (a partir de `idNumerico` / `manual-{n}`); **fallback** por URL normalizada (`linkOriginal` / `link`).

## Como desfavoritar

`UPDATE` na tabela com **`ativo=false`** (sem delete físico). O match usa a mesma lógica de identificação.

## Cálculo do alerta de prazo

Funções em `deadlineAlerts.js`, com base na data de hoje (início do dia local):

| Estado | Regra resumida |
|--------|----------------|
| `prazo_indefinido` | Sem prazo nos campos conhecidos |
| `encerrado` | Prazo &lt; hoje |
| `vence_hoje` | Prazo = hoje |
| `vence_3_dias` | 1–3 dias |
| `vence_7_dias` | 4–7 dias |
| `vence_15_dias` | 8–15 dias |
| `prazo_confortavel` | &gt; 15 dias |

Campos considerados: `prazo_envio`, `prazo`, `data_limite`, `dataLimite`, `prazo_final`, `encerramento`, `fim_inscricao`, e os `*_raw` usados no mapper.

O **banner** na página Editais conta favoritos cuja situação é `vence_hoje`, `vence_3_dias` ou `vence_7_dias` (linhas devolvidas pela view com esses prazos inferidos no cliente).

## Utilizador autenticado e `id_usuario`

- O login (`src/services/authService.js`) persiste em `localStorage` (`editalFinderUser`) o campo **`id_usuario`** vindo da linha em `public.usuario` (Supabase).
- O hook **`useEditalFavorites`** lê **`useAuth().user`** e resolve o id com `resolveFavoriteUserId` (`src/hooks/useEditalFavorites.js`).
- **`fetchFavoritos`** filtra na view por **`.eq('id_usuario', …)`**; escritas e reativações usam o mesmo id; **`removeFavorito`** restringe o `UPDATE` com **`.eq('id_usuario', …)`** quando o id está definido.
- **Editais** e **Radar** usam `favHook.favoritosRemoteEnabled`, que exige Supabase + feature + **`id_usuario` resolvido** — assim cada sessão só vê os próprios favoritos.
- Conta de demonstração `admin@finder.com`: em **produção** não recebe `id_usuario` no objeto guardado (favoritos remotos desligados → **localStorage**); em **desenvolvimento** usa-se `id_usuario: 1` para não quebrar testes locais.
- **Administrador**: vê apenas os **seus** favoritos (mesmo `id_usuario` que na tabela `usuario`). Uma consola global “todos os favoritos” fica para **TODO** futuro (fora deste MVP).

## Limitações

- **Sessões antigas** sem `id_usuario` no JSON guardado: em produção o utilizador deve **voltar a fazer login** para passar a gravar `id_usuario` e activar favoritos remotos.
- **RLS**: insert/update/select dependem das políticas no projeto; erros são registados com `console.warn` / `console.error` (DEV) com `message`, `code`, `details`, `hint` — sem expor chaves. O carregamento inicial da lista de favoritos **propaga** erro ao estado do hook para a faixa na UI.
- **View**: nomes de colunas supõem-se alinhados à tabela + join com `edital`; se a view não expuser `id_favorito` / `ativo` / prazos, ajustar o mapeamento ou a view no Supabase (fora do âmbito deste PR).
- **Ordenação** na leitura da view: `id_favorito` descendente (evita dependência de colunas opcionais como `atualizado_em`).

## Correção da estrela/filtro Favoritos

### Causa encontrada

Vários fatores em conjunto faziam parecer que a estrela “não fazia nada”:

1. **`handleCardFavorite` não aguardava** `toggleFavorite` quando o Supabase estava ativo; falhas de RLS/rede ficavam invisíveis e o estado só atualizava após refresh incoerente.
2. **Objeto instável** retornado pelo hook (novo literal a cada render) quebrava memoização de callbacks dependentes de `favHook`, podendo manter handlers antigos.
3. **Match frágil** entre linhas da view e o objeto `edital` do dashboard (IDs e links com nomes/casing diferentes); favoritos gravados mas não reconhecidos na UI.
4. **`refreshFavorites` a repor `loading: true`** após cada toggle gerava flicker e sensação de “não mudou”.
5. **Soft delete** com colunas extras no `UPDATE` podia falhar se a tabela não expuser `atualizado_em` da forma esperada.

### Ficheiros corrigidos

- `src/hooks/useEditalFavorites.js` — `toggleError` / `clearToggleError`, `toggleFavorite` assíncrono com refresh após toggle, retorno estável com `useMemo`, `refreshFavorites` sem pôr loading em cada refresh.
- `src/services/favoritosService.js` — match por `id_edital` e link canónico (`link_inscricao`, vários aliases de coluna), payload de insert mais robusto, `removeFavorito` só `{ ativo: false }`.
- `src/config/env.js` — `truthyEnv` com trim (evita flags “falsas” por espaços em `.env`).
- `src/pages/Dashboard.jsx` — `await` no toggle remoto, deps estáveis, contagem **Favoritos (N)**, faixa de erro quando o Supabase devolve falha.
- `src/pages/RadarFomento.jsx` — mesmo padrão `await` no toggle remoto.
- `src/components/dashboard/EditalCard.jsx` — `stopPropagation` no clique da estrela para não abrir o card.
- `src/styles/global.css` — estilos `.editais-fav-toggle-error` e botão fechar.

### Onde os favoritos aparecem

- Página **Editais (Dashboard)**: botão **☆ Favoritos (X)** na barra de ações; ao ativar, só cards favoritados; estado vazio com texto a explicar o uso da estrela.
- **Banner de prazo** (até 7 dias) no topo quando aplicável, com **Ver favoritos** que liga o filtro.
- **Radar**: mesma stack (hook + service) quando a feature e o Supabase estão ativos; caso contrário mantém-se `localStorage` local.

### Como testar

Seguir a checklist na secção [Como testar](#como-testar) abaixo; acrescentar: provocar um erro de permissão (ex. RLS) e confirmar a **faixa vermelha** com mensagem e botão **Fechar**.

### Limitações restantes

- Políticas RLS e forma exacta das colunas da view continuam a determinar sucesso do `INSERT`/`UPDATE`; o cliente apenas mostra o erro devolvido pelo Supabase (sem secrets).

## Correção de reativação de favorito

Os favoritos usam **soft delete**: ao desfavoritar, o registo em `public.edital_favorito` permanece com **`ativo=false`**. O índice único **`uq_edital_favorito_usuario_edital`** (e afins) continua a impedir um segundo `INSERT` com o mesmo `id_usuario` + `id_edital`.

**Comportamento corrigido:** antes de inserir, o cliente consulta a **tabela** `edital_favorito` (não só a view, que filtra `ativo=true`). Se existir linha para o mesmo utilizador e edital (`id_edital` ou `edital_link` / match canónico), faz-se **`UPDATE`** com `ativo=true`, alertas e metadados actualizados — **reactivação** da mesma linha. Se um `INSERT` ainda devolver **`23505` duplicate key** (corrida ou mismatch temporário), o fluxo tenta de novo localizar o registo e **reactivar**; nesse caso o utilizador não vê erro de duplicado.

O índice único no Supabase **não foi alterado** nem removido.

Implementação: `src/services/favoritosService.js` (`findExistingFavoritoRowInTable`, `buildReactivatePatch`, `reactivateFavoritoRow`, `addFavorito`); `src/hooks/useEditalFavorites.js` (limpar `toggleError` após sucesso).

## Próximos passos sugeridos

- Painel administrativo opcional: listagem global de favoritos (vários `id_usuario`) — hoje cada utilizador só vê os seus.
- Backend ou Edge Function para e-mails / push e `ultimo_alerta_em` / `proximo_alerta_em`.
- Cron para lembretes fora do browser.
- Sincronizar migração de favoritos localStorage → Supabase (one-shot).

## Como testar

1. Definir `.env.local` com Supabase anon e as três variáveis da feature.  
2. Abrir **Editais**, favoritar um edital; confirmar linha em `edital_favorito`.  
3. Desfavoritar; confirmar `ativo=false`.  
4. Recarregar; confirmar que a lista de favoritos reflete a view.  
5. Ativar **☆ Favoritos**; testar empty state sem favoritos.  
6. Com favorito a 7 dias ou menos, verificar o **banner** e **Ver favoritos**.  
7. Edital sem prazo → badge “Prazo não informado”.  
8. Temas claro / escuro (tokens).  
9. **Radar**: favoritar com feature ativa e verificar em **Editais** (mesmo `id_usuario` e mesma tabela).  
10. Favoritar → desfavoritar → favoritar de novo: mesma linha com `ativo=true`, sem erro `23505`.  
11. Dois utilizadores distintos: favoritar com A; entrar com B; confirmar que o favorito de A **não** aparece; favoritar com B; voltar a A e confirmar **isolamento**.  
12. `npm run build` (última execução desta entrega: **sucesso**, ~1,8 s).

---

## Debug pós-Supabase Auth / RLS

### Contexto

Com **Supabase Auth**, `public.usuario.auth_user_id` e **RLS** (ex.: em `cliente`), os favoritos continuam a usar **`id_usuario`** inteiro da app em `edital_favorito`. O cliente Supabase envia o **JWT** da sessão: sem sessão válida, `SELECT`/`INSERT`/`UPDATE` podem falhar ou devolver vazio conforme políticas.

### Como checar `favoriteUserId`

- Em **DEV**, o hook regista `[useEditalFavorites][DEV]` com `currentUser_id_usuario`, `favoriteUserId`, `favoritosRemoteEnabled`, `FEATURE_EDITAL_FAVORITOS`, `hasSupabaseSession`, `auth_user_id`.
- Em **produção**, `favoriteUserId` vem só de `useAuth().user.id_usuario` (sem fallback numérico). Se for `null`, `favoritosRemoteEnabled` fica **false** e a página usa **localStorage** (`editais_favoritos_v1`).

### Como checar sessão

- Consola (DEV): `[favoritosService.toggleFavorito]` avisa se não há `access_token`.
- Rede: pedidos a `/rest/v1/edital_favorito` ou view de favoritos devem incluir `Authorization: Bearer …`.

### RLS em `edital_favorito`

- Se **não** existir RLS, o acesso depende apenas de **GRANT** para `authenticated` / `anon` (não recomendado em produção).
- Se existir RLS, as policies devem permitir ao utilizador:
  - **SELECT** das próprias linhas (`id_usuario` = perfil actual);
  - **INSERT** / **UPDATE** com o mesmo `id_usuario`.
- Reutilizar padrão `public.current_app_user_id()` **SECURITY DEFINER** (como em `docs/sql/RLS_CLIENTE.sql`) é uma opção coerente.

### Erros comuns

| Sintoma | Causa provável |
|---------|----------------|
| Lista de favoritos vazia + faixa “Não foi possível carregar favoritos” | Erro PostgREST no `SELECT` da view (RLS, view inexistente, coluna errada). |
| Estrela não muda + faixa de toggle | `INSERT`/`UPDATE` bloqueado (RLS), `id_edital` e `edital_link` ambos nulos, ou sessão expirada. |
| `duplicate key` | Índice único `(id_usuario, id_edital)`; o fluxo tenta reactivar linha `ativo=false` — se `SELECT` na tabela falhar, pode não encontrar a linha antiga. |
| Política usando só `anon` | Pedidos autenticados usam role **`authenticated`**; políticas devem alinhar com JWT. |

### Queries SQL de teste (manual no Supabase SQL Editor)

Ajustar nomes de colunas se a sua `vw_editais_favoritos_front` diferir.

**1. Utilizadores**

```sql
SELECT id_usuario, nome_email, tipo_usuario, status, auth_user_id
FROM public.usuario
ORDER BY id_usuario;
```

**2. Favoritos recentes (tabela)**

```sql
SELECT id_favorito, id_usuario, id_edital, edital_titulo, edital_link, ativo, criado_em, atualizado_em
FROM public.edital_favorito
ORDER BY atualizado_em DESC
LIMIT 20;
```

**3. Favoritos ativos (view de front)**

```sql
SELECT id_favorito, id_usuario, id_edital, titulo, link, fonte, prazo_envio
FROM public.vw_editais_favoritos_front
ORDER BY criado_em DESC
LIMIT 20;
```

**4. Classificação — editais FAPESC (tabela)**

```sql
SELECT
  id_edital,
  titulo,
  fonte_recurso,
  setor_economico,
  setor_estrategico,
  area,
  area_tecnologica,
  tags,
  extras
FROM public.edital
WHERE fonte_recurso ILIKE '%FAPESC%'
ORDER BY id_edital DESC
LIMIT 30;
```

**5. Classificação — view de editais front**

```sql
SELECT
  id_edital,
  titulo,
  fonte_recurso,
  setor_economico,
  setor_estrategico,
  area,
  area_tecnologica,
  tags
FROM public.vw_editais_front
WHERE fonte_recurso ILIKE '%FAPESC%'
ORDER BY id_edital DESC
LIMIT 30;
```

### Logs no frontend (DEV)

- `[favoritosService.*]` — `console.error` com `message`, `code`, `details`, `hint` em falhas Supabase.
- `[useEditalFavorites][DEV]` — estado de utilizador e sessão.
- `[useEditalFavorites] toggle falhou` / `toggle erro bruto` — detalhe do toggle.

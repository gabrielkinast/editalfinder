# Frontend EditalFinder — estado do MVP

**Data de fecho desta fase:** 2026-05-10  
**App:** React + Vite (`EditalFinder-React`)  
**Base URL (produção / deploy típico):** caminhos abaixo são relativos ao **`BrowserRouter` com `basename="/editalfinder"`** — URL completa exemplo: `https://…/editalfinder/dashboard`.

---

## Verificação de build

- **`npm run build`** — executado com sucesso nesta fase (bundle gerado em `dist/`).
- **`npm run lint`** — pode falhar se não existir `eslint.config.js` no projeto (configuração ESLint 9); não bloqueia o MVP documentado aqui.

---

## Rotas principais (após autenticação)

| Área no menu | Rota no código | Nota |
|----------------|----------------|------|
| Editais (lista) | **`/dashboard`** | Não existe rota `/editais`; o item “Editais” aponta para `/dashboard`. |
| Cadastros | `/cadastros` | Exige permissão `canViewCadastros`. |
| Radar de Fomento | `/radar-fomento` | |
| Notícias | `/noticias` | |
| Pesquisas | `/pesquisas` | |
| Portais Estratégicos | `/portais-estrategicos` | |
| Índice (compatibilidade) | `/indice` | Rota ativa; **link no menu oculto** salvo `VITE_ENABLE_INDICE=true`. |
| Detalhe de edital | `/edital/:id` | |
| Login | `/login` | |
| Raiz `/` | redireciona para `/dashboard` | |

**Verificação manual recomendada:** com `npm run dev`, abrir `http://localhost:5173/editalfinder/` (ou a URL que o Vite indicar), autenticar, e navegar pelos itens acima. Rotas protegidas sem sessão redirecionam conforme `ProtectedRoute`.

---

## Páginas / áreas existentes (MVP)

1. **Login** — entrada na aplicação.  
2. **Dashboard (Editais)** — listagem, filtros, cards de editais.  
3. **Cadastros** — utilizadores, clientes, editais manuais; **pré-cadastro de projeto** (modal) com PDF/localStorage.  
4. **Radar de Fomento** — match cliente × editais, filtros, cards, opções avançadas.  
5. **Notícias** — feed a partir da view configurada.  
6. **Pesquisas** — idem.  
7. **Portais Estratégicos** — abas Fornecedores / Investimentos, filtros, cards dedicados (sem `public.edital`).  
8. **Índice de compatibilidade** — página dedicada (menu opcional).  
9. **Detalhes do edital** — rota com parâmetro `id`.  
10. **Configurações** (admin) — modal no header quando aplicável.

---

## Funcionalidades concluídas (nesta fase de MVP)

- **Portais Estratégicos:** duas origens de dados em paralelo, stats, filtros, ordenação, grid responsivo, rótulos humanizados, estados vazio/erro.  
- **Radar:** UX de loading, contagens explicadas, painel avançado colapsável, cards com hierarquia e critérios em “details”.  
- **Pré-cadastro de projeto:** UI do cabeçalho e assistente, PDF jsPDF sem sobreposição crítica no fim do documento, um único fechamento visível no header + Escape + overlay.  
- **Menu:** item Índice oculto por defeito (`VITE_ENABLE_INDICE`); label curta “Radar”.  
- **Modal pré-cadastro:** sem botão × duplicado do `Modal` (`hideCloseButton`).

---

## Views Supabase consumidas (via `.env`)

Variáveis típicas (ver `.env.example`):

| Variável | Uso principal |
|----------|----------------|
| `VITE_VIEW_EDITAIS` | Lista de editais (`vw_editais_front` por defeito) |
| `VITE_VIEW_NOTICIAS` | Feed de notícias |
| `VITE_VIEW_PESQUISAS` | Pesquisas |
| `VITE_VIEW_FORNECEDORES` | Aba Fornecedores em Portais |
| `VITE_VIEW_INVESTIMENTOS` | Aba Investimentos em Portais |

**Radar / pré-cadastro / cadastros** dependem também de dados de clientes e editais carregados pelos serviços existentes (mesmo projeto Supabase; sem alteração de backend nesta fase).

---

## Limitações conhecidas

- **RLS / anon:** se as policies não permitirem leitura, listas podem vir vazias sem “erro” explícito na UI.  
- **Pré-cadastro:** persistência de rascunho em **localStorage** (não sincroniza com servidor).  
- **PDF:** gerado no cliente (jsPDF); alertas de pendências usam `window.alert` em alguns fluxos.  
- **Bundle:** aviso de chunk &gt; 500 kB no build — melhoria futura: code-splitting.  
- **ESLint:** script `lint` pode exigir ficheiro de configuração flat config (ESLint 9).

---

## Próximos passos sugeridos

- Testes E2E ou smoke checklist antes de cada release.  
- Configurar `eslint.config.js` e integrar `lint` no CI.  
- Opcional: code splitting na rota (Radar, Portais, Cadastros).  
- Sincronização de rascunho pré-cadastro com backend, quando existir API.  
- Documentação de operação (variáveis obrigatórias em produção).

---

## Documentação relacionada

- `PORTAIS_ESTRATEGICOS_FRONTEND_MVP.md`  
- `RADAR_UX_POLISH.md`  
- `PRE_CADASTRO_PROJETO_UX_FIX.md`  
- `FRONTEND_STRUCTURE_AUDIT.md` / `FRONTEND_REORGANIZATION_PHASE1.md`

---

## Consola do browser

Não há substituto completo ao teste manual: abrir as rotas acima autenticado e confirmar ausência de **`console.error` crítico** (falhas de rede, Supabase ou React). O build estático por si não executa a app contra Supabase.

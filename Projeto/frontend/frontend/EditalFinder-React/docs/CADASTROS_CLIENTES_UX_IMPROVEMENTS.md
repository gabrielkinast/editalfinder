# Melhorias UX — Cadastros / Clientes

## Arquivos alterados

- `src/pages/Cadastros.jsx` — hero, cards, filtros (incl. setor por `select`), colunas e badges, ações de linha, integração pré-cadastro inalterada.
- `src/components/admin/AdminTable.jsx` — `rowIdKey`, `extraRowActions`, `wrapClassName`.
- `src/styles/global.css` — bloco de estilos `.cad-*`, sidebar `button.sidebar-link`, tabela compacta `.cad-table-users`, scroll horizontal `.cad-table-wrap`.
- `docs/CADASTROS_CLIENTES_UX_AUDIT.md` — auditoria.
- `docs/CADASTROS_CLIENTES_UX_IMPROVEMENTS.md` — este arquivo.

## Melhorias feitas

- **Clientes**: título e subtítulo alinhados ao produto (Radar de Fomento); cards com total, ativos, com pré-cadastro, completude média estimada, interesse máximo configurado.
- **Filtros**: painel único, labels explícitos, **Setor** como `select` com valores distintos dos clientes carregados, slider “Interesse até” integrado, **Limpar filtros** visível quando há filtro ativo.
- **Tabela**: coluna Cliente com nome em destaque e linha secundária; badges de status e pré-projeto; ação principal **Abrir pré-cadastro** + Editar/Excluir como texto.
- **Usuários**: mesmo padrão de hero e cards resumo; tabela mais compacta; badge no tipo; status com badge.
- **Responsivo**: `overflow-x: auto` na área da tabela; ações em coluna flexível em mobile.

## O que não foi alterado

- Backend, banco, `dataService` (exceto uso existente).
- Lógica interna de PDF, Radar, Portais Estratégicos, geração/download de documentos.
- Conteúdo e fluxo do modal `ProjetoPrecadastroForm` (apenas rótulo/botão de entrada).
- Campos dos formulários removidos ou renomeados no modelo de dados.

## Como testar

1. `npm run build` (deve concluir sem erros).
2. `npm run dev`; entrar em **Cadastros** → **Clientes**.
3. Conferir cards, filtros (incluindo setor e limpar), ordenação visual da tabela.
4. Clicar **Abrir pré-cadastro**: mesmo modal e fluxo de rascunho/PDF que antes.
5. Aba **Usuários**: layout hero + tabela compacta + badges.

## Limitações restantes

- Estatísticas de pré-cadastro e completude são calculadas no browser a partir de rascunhos locais — listas muito grandes podem ficar lentas.
- “Completude média” é estimada via `calculatePreCadastroCompleteness`, não substitui métricas oficiais do servidor.
- Filtro de setor só lista setores já presentes nos clientes carregados (sem busca parcial por texto além da busca geral).

## Próximos passos sugeridos (Pré-cadastro / PDF)

- Endpoint agregado de status de pré-cadastro por cliente para evitar N leituras locais.
- Indicadores de PDF gerado / última exportação na própria linha, quando houver dado na API.
- Testes E2E da aba Clientes (filtros + abrir modal).

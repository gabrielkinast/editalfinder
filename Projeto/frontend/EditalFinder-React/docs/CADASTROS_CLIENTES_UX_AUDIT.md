# Auditoria UX — Cadastros / Clientes

## Arquivos envolvidos

| Área | Arquivo |
|------|---------|
| Página Cadastros (abas, filtros, tabela, modais) | `src/pages/Cadastros.jsx` |
| Tabela administrativa reutilizável | `src/components/admin/AdminTable.jsx` |
| Formulário cliente | `src/components/admin/ClientForm.jsx` |
| Modal pré-cadastro (fora do escopo de alteração de lógica) | `src/components/admin/ProjetoPrecadastroForm.jsx` |
| Estado inicial / envelope pré-cadastro | `src/utils/precadastroProjetoInitialState.js` |
| Completude (somente leitura para resumo) | `src/utils/precadastro/calculatePreCadastroCompleteness.js` |
| Estilos | `src/styles/global.css` |

## Fluxo atual

1. Usuário abre **Cadastros** pelo app; menu lateral: **Usuários** (se permissão), **Clientes**, **Editais cadastrados**.
2. Em **Clientes**: carrega lista via `dataService`; opcionalmente calcula metadados locais de pré-cadastro por cliente (`loadPrecadEnvelope` + `calculatePreCadastroCompleteness`) para badges e cards de resumo.
3. Filtros: busca textual, status, porte, **setor** (lista derivada dos registros), faixa de interesse (min/max já existentes).
4. **Abrir pré-cadastro** abre o mesmo `Modal` + `ProjetoPrecadastroForm` que antes; demais ações: criar/editar cliente, excluir.

## Problemas visuais (antes da melhoria)

- Aparência genérica de CRUD (cabeçalho pobre, pouco contexto de negócio).
- Filtros e slider sem hierarquia visual clara; “Setor” não era um filtro real.
- Tabela com ações grandes empilhadas; pouca leitura rápida de pré-projeto e status.
- Classes `cad-*` referenciadas sem folha de estilo dedicada (layout inconsistente).

## Riscos

- **Performance**: cálculo por cliente do envelope/pré-cadastro para estatísticas e coluna “Pré-projeto” pode pesar com muitos registros (tudo no cliente, sem mudança de API).
- **Dados**: badges de pré-projeto dependem de rascunho local + `bloco_estr_status_precadastro`; podem divergir do backend até sincronizar.
- **Regressão de permissões**: `extraRowActions` só na aba clientes; demais abas mantêm fluxo padrão da tabela.

## Plano de melhoria aplicado

- Hero + cards de resumo na aba Clientes; hero alinhado na aba Usuários.
- Painel de filtros com rótulos claros, slider em bloco próprio, **Limpar filtros** condicionado a filtros ativos.
- Tabela com colunas Cliente / CNPJ / Setor / Porte / Status / Pré-projeto; ações com botão primário “Abrir pré-cadastro” e links secundários Editar/Excluir.
- `AdminTable`: `rowIdKey`, `extraRowActions` substitui pilha padrão quando necessário, `wrapClassName` para tabela compacta em Usuários.
- Estilos `cad-*` centralizados em `global.css`; scroll horizontal controlado em telas estreitas.

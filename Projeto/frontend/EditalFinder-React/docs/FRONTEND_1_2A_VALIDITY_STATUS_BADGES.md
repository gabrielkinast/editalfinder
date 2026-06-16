# FRONTEND 1.2A — Validity / Deadline / Semantic Badges

## Objetivo

Mostrar badges/status visuais para que o usuário entenda rapidamente a situação
de cada edital/oportunidade sem abrir os detalhes, refletindo a semântica
consolidada no backend (patches 10.1–10.3).

Sem alterar backend, schema, migrations ou regras de crawler.

## Badges disponíveis

| kind | label | tone | quando |
|------|-------|------|--------|
| `noise` | Ruído provável | danger | `extras.is_noise === true` |
| `post_result` | Chamada pós-resultado | muted | BNDES com resultado final/diligência/seleção concluída |
| `result_published` | Resultado publicado | muted | `actionability_type=resultado` ou texto de resultado |
| `closed` | Encerrado | muted | prazo < hoje |
| `due_7` | Vencendo em 7 dias | danger | prazo entre hoje e +7 dias |
| `due_30` | Vencendo em 30 dias | warning | prazo entre +8 e +30 dias |
| `open` | Aberto | success | prazo > +30 dias |
| `deadline_in_detail` | Prazo em PDF/detalhe | info | `sem_prazo_kind=deadline_in_pdf_or_detail` / `recrawl_candidate` |
| `deadline_tbd` | Prazo a definir | neutral | `sem_prazo_kind=deadline_tbd` |
| `permanent_line` | Linha permanente | info | `sem_prazo_kind=permanent_funding_line` ou texto/tipo permanente |
| `no_deadline` | Sem prazo informado | neutral | sem prazo e potencial oportunidade |
| `portal_useful` | Portal útil | info | `actionability_type=portal_util` |
| `unknown` | Status indefinido | muted | fallback de segurança |

## Campos usados (resilientes)

A util lê tanto o shape do mapper do front (`*_raw`, `extras_raw`) quanto objetos
crus do backend (`prazo_envio`, `extras`):

- prazo: `prazo_envio_raw` / `prazo_envio` / `extras.prazo_envio` (prioridade)
  e fallback `fim_inscricao_raw` / `fim_inscricao` / `dataLimite` /
  `extras.grants_close_date` / `extras.closeDate`;
- `extras.validade_status`, `extras.actionability_type`,
  `extras.classification_by_actionability_type`;
- `extras.sem_prazo_kind`, `extras.sem_prazo_reason`, `extras.recrawl_candidate`;
- `extras.is_noise`, `extras.noise_type`, `extras.bndes_classification`;
- `extras.deadline_source_field` / `extras.deadline_source` (texto auxiliar no detalhe).

Datas inválidas, `extras` ausente e `edital` nulo nunca quebram a renderização.

## Regras de prioridade

Ordenadas por `priority` (menor primeiro):

1. Ruído provável
2. Resultado publicado / Chamada pós-resultado
3. Encerrado
4. Vencendo em 7 dias
5. Vencendo em 30 dias
6. Aberto
7. Prazo em PDF/detalhe
8. Prazo a definir
9. Linha permanente
10. Sem prazo informado
11. Portal útil
12. Status indefinido

`prazo_envio` tem prioridade sobre `fim_inscricao`.

## Semântica importante

- **`sem_prazo` ≠ ruído** — registros sem prazo recebem "Sem prazo informado".
- **`encerrado` ≠ ruído** — recebem "Encerrado", tom neutro/muted.
- **BNDES pós-resultado** — recebe "Chamada pós-resultado" e nunca aparece como
  "Aberto" mesmo com prazo futuro, pois `post_result` tem prioridade sobre `open`.
- **Portal útil / resultado** — não são tratados como ruído.

## Arquivos

- `src/utils/edital/editalStatusBadges.js` — util central + helpers.
- `src/components/editais/EditalStatusBadges.jsx` — componente reutilizável
  (`maxVisible`, `compact`, "+N").
- `src/styles/global.css` — tom `neutral` e container `.edital-status-badges`.

## Onde aparecem

- Cards do dashboard (`EditalCard`) — compacto, até 3 badges.
- Cards do Radar (`CardEditalRadar`) — compacto, até 2 badges.
- Modal de detalhes (`EditalDetailsModal`) — todos os badges + `sem_prazo_reason`
  e "Fonte do prazo".
- Página de detalhe (`EditalDetalhes`) — todos os badges no cabeçalho.

## Testes

`src/utils/edital/editalStatusBadges.test.js` (node:test), registrado no
`npm test`. Cobre prazos (7/30/aberto/encerrado), sem prazo + kinds,
resultado/pós-resultado BNDES, portal útil, ruído, prioridade `prazo_envio`,
e robustez (datas inválidas, extras ausente, null).

## Limitações

- Não foram adicionados filtros por status (deixado para FRONTEND 1.2B conforme spec).
- Exportação PDF/XLSX não foi alterada (sem risco de regressão); a coluna de
  status pode ser adicionada depois usando `getPrimaryEditalStatusBadge`.
- Detecção de pós-resultado/resultado usa heurística textual além de campos
  estruturados; depende da qualidade do texto vindo do backend.

## Próximo patch recomendado

- **FRONTEND 1.2B** — filtros por status (Aberto/Vencendo/Encerrado/Sem prazo/
  Resultado/Prazo em PDF) e coluna "Status" na exportação PDF/XLSX.

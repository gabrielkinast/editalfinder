# FRONTEND 1.1C.5 — Severidade e polish do e-mail de reporte

## Objetivo

Melhorar triagem da equipe ao reportar problemas: campo **Severidade** no modal, assunto e corpo do Gmail mais legíveis, labels humanos em vez de valores técnicos (`other`, `normal`).

## Níveis de severidade

| Valor | Label | Prefixo no assunto | Quando usar |
|-------|-------|-------------------|-------------|
| `low` | Baixa | BAIXA | Visual, texto, incômodo leve |
| `medium` | Média | MÉDIA | Atrapalha mas há contorno (**default**) |
| `high` | Alta | ALTA | Funcionalidade importante bloqueada |
| `critical` | Crítica | CRÍTICA | Travamento, tela branca, perda de dados, EXE |

## Modal

- Campo **Severidade** após **Tipo do problema**
- Default: **Média**
- Descrição curta da opção selecionada abaixo do select

## Assunto do Gmail

```
[EditalFinder][ALTA] Reporte — Erro no aplicativo desktop / EXE — /dashboard
```

Componentes: prefixo de severidade + `tipo_label` + rota normalizada (`/dashboard` ou `sem rota`).

## Corpo do e-mail

Seções: **Resumo**, **Descrição**, **Localização**, **Contexto técnico**, **Observação**.

- Severidade: label humano (ex.: `Alta`, não `high`)
- Categoria: label humano (ex.: `Desktop/EXE`, não `other`)
- Data em formato pt-BR legível

## Compatibilidade payload antigo

| Legado | Novo |
|--------|------|
| `severidade: "normal"` | `medium` / Média |
| `severidade: "urgent"` | `high` |
| sem severidade | `medium` |
| `categoria: "other"` | exibe `Outro` no e-mail |

Fila localStorage normaliza itens antigos via `normalizeFeedbackPayload`.

## Fluxo inalterado (1.1C.4)

Gmail Web Compose → mailto → localStorage

## Arquivos

- `src/constants/appFeedbackConfig.js` — `APP_FEEDBACK_SEVERITY_LEVELS`
- `src/utils/feedback/appFeedbackSeverity.js` — `getFeedbackSeverity`
- `src/utils/feedback/appFeedbackLabels.js` — rotas e categorias humanas
- `src/components/feedback/AppFeedbackModal.jsx` — UI severidade
- `src/utils/feedback/appFeedbackMailto.js` — assunto/corpo

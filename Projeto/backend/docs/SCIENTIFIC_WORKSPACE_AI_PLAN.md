# Plano de IA — Workspace Científico

Documento de preparação. **Nesta fase não há chamada de IA no browser** e **nenhuma chave no frontend**.

## Princípios de segurança

| Permitido | Proibido |
|-----------|----------|
| `OPENAI_API_KEY` (ou similar) só no **Supabase Edge Function** ou backend | `VITE_OPENAI_API_KEY` |
| Cliente chama `POST /functions/v1/scientific-ai-assistant` com JWT Supabase | Chave em `localStorage` |
| Feature flag `VITE_ENABLE_SCIENTIFIC_AI=false` no Vite | Enviar API key no body/query do browser |

## Endpoint futuro

```
POST /functions/v1/scientific-ai-assistant
Authorization: Bearer <supabase_session>
Content-Type: application/json
```

### Entrada

```json
{
  "task": "project_ideas | professor_questions | study_path | explain_item",
  "interests": ["nuclear", "materiais"],
  "notebookItems": [],
  "feedItems": [],
  "level": "intermediario"
}
```

### Saída

```json
{
  "suggestions": [],
  "rationale": "…",
  "warnings": []
}
```

## Casos de uso (futuro)

1. Gerar projetos sugeridos com melhor aderência ao perfil.
2. Gerar perguntas para professor/orientador.
3. Explicar “por que isso importa” em itens do feed ou caderno.
4. Criar trilha personalizada além do catálogo local.
5. Resumir itens salvos no caderno.
6. Sugerir plano de estudo semanal.

## Implementação no frontend (quando existir Edge Function)

1. `ENABLE_SCIENTIFIC_AI` em `src/config/env.js` (já existe; padrão `false`).
2. Serviço `scientificAiClient.js` que chama apenas a Edge Function (sem modelo nem chave).
3. UI substitui placeholders “IA científica — em breve” por fluxos reais.
4. Fallback: se a função falhar, manter heurísticas locais atuais (`buildScientificProjectIdeas`, `buildScientificProfessorQuestions`, etc.).

## Edge Function (esboço)

Nome sugerido: `scientific-ai-assistant`

- Validar usuário autenticado (RLS / JWT).
- Montar prompt a partir de `task` + payload sanitizado.
- Chamar OpenAI (ou outro provedor) com `Deno.env.get('OPENAI_API_KEY')`.
- Limitar tamanho de resposta e rate limit por usuário.
- Nunca logar chave nem prompt com dados sensíveis em produção.

## Flag de ambiente

```env
# .env.local — frontend
VITE_ENABLE_SCIENTIFIC_WORKSPACE=true
VITE_ENABLE_SCIENTIFIC_AI=false

# Supabase / Edge (servidor apenas)
OPENAI_API_KEY=sk-...
```

## Estado atual (pós correções UX)

- Briefing, rota, ideias e caderno são **100% locais** (catálogos + heurísticas + `localStorage`).
- Placeholder `ScientificAiPlaceholder` e log `ai_placeholder_clicked` quando o usuário interage.
- Títulos sanitizados com `cleanScientificTitle` para evitar prefixos duplicados ao salvar no caderno.

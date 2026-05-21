# Radar de Fomentos — Diagnóstico de performance

Documento gerado para orientar otimização **sem alterar regras de score** nem executar mudanças destrutivas no banco. SQL proposto em `docs/sql/RADAR_CLIENTE_CACHE.sql` (não aplicado automaticamente).

---

## 1. Fluxo atual (frontend)

| Etapa | Onde | O que acontece |
|-------|------|----------------|
| Rota | `App` → `/radar-fomento` | Página `RadarFomento.jsx` |
| Mount | `useEffect` em `RadarFomento` | `Promise.all([dataService.getClients(), dataService.getEditais()])` |
| Clientes | `dataService.getClients()` | Tabela/view `cliente` (RLS do usuário) |
| Editais | `dataService.getEditais()` | `vw_editais_front` (fallback `edital`), paginação ~800–1000/req até esgotar |
| Favoritos (opcional) | `useEditalFavorites` | `vw_editais_favoritos_front` se habilitado |
| Clique cliente | `ListaClientes` → `handleSelecionarCliente` | `setClienteIdSelecionado` + limpar filtros UI (síncrono) |
| Match | `useRadarMatches` → worker ou `recomendarEditaisAsync` | **Cálculo no browser** (`radarMatch.js`); preferencialmente **Web Worker** (Fase 0.6) |
| Lotes | chunks de 72 editais | Worker: sem yield na main thread; fallback: `setTimeout(0)` entre chunks |
| Cache local | `Map` em `useRadarMatches.js` | até 24 entradas; chave = cliente + assinatura catálogo + opções |

### Queries Supabase **por clique em cliente**

**0** — se o catálogo de editais e clientes já foi carregado no mount. O gargalo percebido é CPU/JS no cliente, não rede no clique.

### Queries no **carregamento inicial** da página

| Chamada | Alvo típico |
|---------|-------------|
| `getClients` | `cliente` |
| `getEditais` | `vw_editais_front` (N páginas até fim) |
| Favoritos remotos (se ativo) | view de favoritos |

---

## 2. Componentes e serviços

| Papel | Arquivo |
|-------|---------|
| Página | `frontend/EditalFinder-React/src/pages/RadarFomento.jsx` |
| Lista clientes | `components/radar/ListaClientes.jsx` |
| Cards | `components/radar/CardEditalRadar.jsx` |
| Hook cache/cálculo | `hooks/useRadarMatches.js` |
| Score | `services/matchService.js` → `utils/radarMatch.js` |
| Dados | `services/dataService.js` |
| Logs DEV | `utils/radarPerfLog.js` |
| Worker | `workers/radarMatchWorker.js`, `utils/radar/radarMatchCore.js`, `utils/radar/radarWorkerClient.js` |
| Virtual list | `components/radar/RadarVirtualResultsList.jsx`, `constants/radarVirtual.js`, `utils/radarRenderPerfLog.js` |
| Skeleton | `components/radar/RadarResultsSkeleton.jsx` |

---

## 3. Gargalos prováveis

1. **O(N) no catálogo completo** — cada troca de cliente (cache miss) percorre todos os editais elegíveis após pré-filtro; N pode ser centenas/milhares.
2. **Cache miss frequente** — chave inclui assinatura do catálogo e opções avançadas; muitas combinações → poucos hits ao alternar clientes.
3. **UI bloqueada visualmente** — antes: `setResults([])` + spinner único; cards só após fim do cálculo.
4. **Renderização** — `visibleCap` (40 cards) + `useMemo` de filtros sobre lista inteira; custo menor que o score, mas soma após cálculo.
5. **`debugRadar` em DEV** — segundo passe síncrono após cálculo (apenas desenvolvimento).
6. **Carga inicial pesada** — download paginado de todo o catálogo antes de qualquer clique.

---

## 4. O que já foi feito (fase 0 — frontend)

- Seleção visual do cliente **imediata** (já era por `clienteIdSelecionado`).
- **Skeleton** de cards em cache miss (sem limpar lista em recálculo do mesmo cliente — stale overlay).
- Cache em memória ampliado (12 → 24 entradas).
- Logs DEV: `[radar-perf]` click, cache hit/miss, fetch/calc, transform, complete.
- Documento + SQL de cache Postgres (não executado).

### Fase 0.5 — Renderização progressiva (atual)

| Comportamento | Detalhe |
|---------------|---------|
| Primeiro lote | Após **72** editais pós-pré-filtro (1 chunk), emite prévia |
| Prévia na UI | Top **20** via `finalizarRankingOportunidadesRadar` + `ordenarLinhasRadarUi` (mesma ordenação por score) |
| Background | Continua chunks até fim; substitui lista pela versão **completa** |
| Race | `generationRef` descarta callbacks de cliente anterior |
| Cache | `partial: true` na prévia; `partial: false` no fim; hit completo evita recálculo |
| Logs DEV | `first_results_ms`, `full_results_ms`, `items_first_batch`, `items_total`, `cliente_id`, cache hit/miss |

Arquivos: `matchService.recomendarEditaisAsync` (`onPartialResults`), `useRadarMatches` (`hasPreviewResults`, `isPartial`).

### Fase 0.6 — Web Worker (atual)

| Objetivo | Mover o cálculo pesado (score/ranking em lote) para **off main thread**, mantendo as mesmas regras em `radarMatch.js`. |
|----------|----------------------------------------------------------------------------------------------------------------------|

**Arquitetura**

```text
RadarFomento → useRadarMatches
  ├─ cache hit (completo / parcial) → UI imediata
  └─ cache miss
       ├─ runRadarMatchViaWorker (preferencial)
       │    └─ workers/radarMatchWorker.js → utils/radar/radarMatchCore.js → radarMatch.js
       └─ fallback: recomendarEditaisAsync (main thread) → mesmo radarMatchCore
```

**Mensagens do worker**

| Direção | Tipo | Conteúdo |
|---------|------|----------|
| → Worker | `START_RADAR_MATCH` | `{ jobId, cliente, editais, options, chunkSize, startedAt }` |
| → Worker | `CANCEL_RADAR_MATCH` | `{ jobId }` |
| → Worker | `PING` | health check (DEV) |
| ← Worker | `RADAR_PARTIAL_RESULTS` | top 20, `partial: true`, após 1º chunk (72) |
| ← Worker | `RADAR_PROGRESS` | processed / total |
| ← Worker | `RADAR_FULL_RESULTS` | lista completa, `partial: false` |
| ← Worker | `RADAR_ERROR` | erro → hook faz fallback |
| ← Worker | `RADAR_CANCELLED` | job antigo ou abort |

**Race / cancelamento**

- `generationRef` + `jobId` por execução (`radar-{gen}-{clienteId}-{ts}`).
- Respostas com `jobId` diferente do ativo são ignoradas.
- `AbortController` + `CANCEL_RADAR_MATCH` ao trocar cliente ou desmontar.

**Fallback**

- Worker indisponível, erro de construção ou `RADAR_ERROR` → `recomendarEditaisAsync` na main thread.
- Log DEV: `[radar-perf] worker_fallback=true`.

**Cache** (inalterado na forma, campos extras)

```json
{
  "clienteId": "...",
  "rows": [],
  "meta": {},
  "partial": false,
  "source": "worker | main_thread | cache",
  "generatedAt": 1234567890
}
```

**Logs DEV** (`[radar-perf]`)

- `worker_start`, `worker_partial`, `worker_full`, `worker_error`, `worker_cancel`, `worker_fallback`
- `worker_first_results_ms`, `worker_full_results_ms` (via `first_results_ms` / `full_results_ms` com `source: worker`)
- `main_thread_block_avoided: true` quando o worker conclui o lote
- `jobId`, `cliente_id`, `items_first_batch`, `items_total`, `cache_hit` / `cache_miss` / `cache_hit_partial`

**Arquivos**

| Arquivo | Papel |
|---------|--------|
| `src/utils/radar/radarMatchCore.js` | Pipeline async puro (chunks + prévia + ranking) |
| `src/workers/radarMatchWorker.js` | Worker entry |
| `src/utils/radar/radarWorkerClient.js` | PostMessage + cancel + fallback |
| `src/hooks/useRadarMatches.js` | Orquestra worker vs main thread + cache |
| `src/services/matchService.js` | Delega `recomendarEditaisAsync` ao core |

**Validar no DevTools**

1. Console → filtrar `[radar-perf]`.
2. Performance → Main thread: cliques no cliente **não** devem exibir long tasks de `calcularMatchRadar` (vão para Worker no painel Workers).
3. Clique cliente pesado: `worker_start` → `worker_partial` (≤20 cards, pill “Prévia”) → `worker_full`.
4. Mesmo cliente de novo: `cache_hit`, sem `worker_start`.
5. Alternar clientes rápido: só `jobId` mais recente atualiza a lista.
6. Simular falha: em Application → desabilitar workers não é trivial; forçar erro quebrando worker uma vez → `worker_fallback` + resultado igual.

### Fase 0.7 — Virtualização da lista de resultados (atual)

| Objetivo | Renderizar só cards visíveis no scroll, reduzindo custo React/DOM com muitas oportunidades. |
|----------|---------------------------------------------------------------------------------------------|

**Ativação:** `RADAR_USE_VIRTUAL_LIST` em `src/constants/radarVirtual.js`. **≤ 30** cards → grid + `visibleCap`; **> 30** → `react-window` `VariableSizeList`.

**Componentes:** `RadarVirtualResultsList.jsx`, `RadarResultsGrid.jsx`, `CardEditalRadar` com `memo`.

**Logs:** `[radar-render]` — `render_start`, `render_end`, `render_ms`, `virtual_enabled`, `visible_range`, `items_total`, `partial`/`full`.

**Validar:** cliente com >30 resultados → poucos nós `CardEditalRadar` no React DevTools; scroll fluido; filtros/pill prévia intactos.

---

## 5. Plano de otimização em fases

### Fase 1 — Leitura Postgres (proposta; SQL em arquivo)

- Tabela `public.radar_cliente_resultado` com scores pré-calculados por `(id_cliente, id_edital)`.
- View `vw_radar_cliente_front` com joins mínimos ao edital para o card.
- Job/worker ou trigger controlado para **popular/atualizar** cache (fora do clique).
- Frontend passa a ler a view no clique; fallback para cálculo local se vazio/stale.

### Fase 2 — Invalidação e freshness

- Coluna `stale boolean` + `calculado_em`.
- Invalidar por cliente quando cadastro muda; por edital quando edital novo/atualizado.
- Endpoint ou RPC `refresh_radar_cliente(id_cliente)` (admin/cron).

### Fase 3 — Redis / Upstash (futuro)

- Cache de resposta HTTP agregada por `clienteId` + hash de filtros.
- TTL curto (ex. 5–15 min); invalidação por cliente.
- Útil se Postgres ainda não entregar &lt;200 ms com RLS.

### Fase 4 — UX avançada

- Prefetch do próximo cliente na lista após idle.
- ~~Web Worker para `recomendarEditaisAsync`~~ → **feito na Fase 0.6**.
- ~~Virtualização da grade de cards~~ → **feito na Fase 0.7** (`react-window`).

---

## 6. Riscos

| Risco | Mitigação |
|-------|-----------|
| Divergência cache DB vs score JS | Mesma versão de algoritmo no worker; flag `stale`; não alterar regras sem versionar |
| RLS | Políticas espelhando `cliente`/`edital`; revisar com doc de segurança antes de apply |
| Tamanho da tabela cache | Particionar por cliente; índices; limpar editais encerrados |
| Stale UI mostrando cliente errado | `resultsForClienteId` / `resultsReady` no hook |
| Regressão em produção | Feature flag `VITE_RADAR_READ_CACHE` para ler view |

---

## 7. Redis (registro fase futura)

Não implementado nesta entrega. Cenário: leitura Supabase ainda lenta com índices + view; cachear JSON da resposta por `id_cliente` com TTL e purge on write.

---

## 8. Como depurar em DEV

1. Abrir Radar, DevTools → Console.
2. Filtrar `[radar-perf]` e `[radar]`.
3. Clicar cliente A (miss) → `first_results_ms` (prévia ~1 chunk) e depois `full_results_ms`.
4. Clicar cliente B → miss; voltar A → `cache_hit` com `partial: false` e `ms` baixo.
5. Recalcular mesmo cliente → lista antiga com opacidade + novo cálculo.
6. Conferir `items_first_batch` ≤ 20 e `items_total` após conclusão.
7. Fase 0.6: confirmar `worker_start` / `worker_partial` / `worker_full` e `main_thread_block_avoided: true` (aba **Workers** no Performance).
8. Fase 0.7: filtrar `[radar-render]`; com >30 cards, `virtual_enabled: true` e `visible_range` ao rolar.

---

## 9. Referências SQL

Ver `docs/sql/RADAR_CLIENTE_CACHE.sql` — **não executar** sem revisão e backup.

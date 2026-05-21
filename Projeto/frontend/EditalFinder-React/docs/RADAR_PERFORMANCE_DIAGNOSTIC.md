# Radar de Fomento — Diagnóstico de performance (frontend)

Documentação das otimizações progressivas no cálculo e renderização do Radar, sem alteração de score, backend ou Supabase.

## Fases anteriores (resumo)

| Fase | Objetivo | Artefatos principais |
|------|----------|----------------------|
| 0.5 | Prévia top 20 após 1º chunk | `recomendarEditaisAsync`, cache em memória, pill “Prévia” |
| 0.6 | Cálculo em Web Worker | `radarMatchCore.js`, `radarMatchWorker.js`, `radarWorkerClient.js` |
| 0.7 | Virtualização da lista (**experimental, OFF**) | `react-window`, `RadarVirtualResultsList.jsx` — desativada por sobreposição de cards |
| 0.8 | Cache `sessionStorage` | `radarPersistentCache.js`, fingerprints pré-calculados |

**Configuração recomendada (atual):** Web Worker (0.6) + sessionStorage (0.8) + **grid paginado** (`RADAR_VISIBLE_INITIAL_CAP = 24`, botão “Mostrar mais”) — **sem** virtualização.

Logs comuns: prefixo `[radar-perf]` via `radarPerfLog.js` e `radarRenderPerfLog.js`.

---

## Fase 0.7 — Virtualização (experimental, desativada)

### Problema observado

Com `RADAR_USE_VIRTUAL_LIST = true`, o grid virtualizado (`react-window` + linhas com 1–3 colunas) gerou **cards sobrepostos**, grid quebrado e UX pior que o grid CSS normal.

### Estado atual

- `src/constants/radarVirtual.js`: `RADAR_USE_VIRTUAL_LIST = false` (padrão).
- `RadarFomento.jsx` usa apenas `RadarResultsGrid` + `.radar-grid` + `visibleCap`.
- `RadarVirtualResultsList.jsx` permanece no repo para correção futura (altura fixa / lista simples / paginação).

### Alternativa estável (em uso)

- `RADAR_VISIBLE_INITIAL_CAP = 24`
- `RADAR_VISIBLE_LOAD_MORE_STEP = 24`
- Botão “Mostrar mais oportunidades”
- Durante cálculo completo, só os primeiros N cards são pintados na main thread.

### Reativar virtualização (futuro)

1. Medir altura real com `ResizeObserver`, ou
2. Lista simples de uma coluna (sem grid 3-col virtualizado), ou
3. Infinite scroll / paginação em vez de `VariableSizeList`.

---

## Payload compacto + profiling pré-worker

### `compactRadarWorkerPayload.js`

Antes de `postMessage`, editais e cliente são reduzidos aos campos usados em `toRadarOportunidade` / `toRadarCliente` (textos truncados, sem blobs Supabase/crawler).

### Fingerprints pré-calculados

- `catalogFingerprint`: `useMemo` quando `editais` carrega (`RadarFomento`).
- `clientesFingerprintMap`: `useMemo` quando `clientes` carrega.
- Passados a `loadRadarSessionCache` / `saveRadarSessionCache` — **não** revarrem o catálogo inteiro no clique.

### Logs `[radar-perf]` (main thread antes do worker)

| Evento | Significado |
|--------|-------------|
| `click_received_ms` | Tempo até handler do clique processar |
| `select_cliente_state_ms` | Após `setClienteIdSelecionado` (microtask) |
| `time_until_effect_ms` | Clique → início do `useEffect` do hook |
| `before_session_cache_lookup` / `after_session_cache_lookup` | Leitura sessionStorage |
| `before_worker_payload_build` / `after_worker_payload_build` | Compactação do payload |
| `worker_payload_size_items` | Nº de editais no payload |
| `before_worker_postMessage` / `after_worker_postMessage` | structured clone |
| `time_until_worker_start` | Clique → `postMessage` |
| `main_thread_pre_worker_ms` | Trabalho síncrono na main antes do worker |

### UI no clique

- Cliente selecionado imediatamente.
- Pill **“Preparando cálculo…”** enquanto `isPreparing` (antes do `postMessage`).
- Lista anterior mantida se houver cache/prévia/stale do mesmo cliente.

---

## Fase 0.8 — Cache persistente em sessionStorage

### Problema

O cache em memória (`Map` em `useRadarMatches.js`) é perdido ao recarregar a página ou ao sair e voltar ao Radar na mesma aba, forçando novo cálculo completo por cliente.

### Solução

Cache leve em **sessionStorage** apenas para **resultados completos** (`partial: false`), com invalidação por TTL, versão do algoritmo e fingerprints de catálogo, cliente e opções do Radar.

### Arquivos

- `src/utils/radar/radarPersistentCache.js` — leitura/gravação, prune, quota
- `src/hooks/useRadarMatches.js` — ordem: memória → sessionStorage → worker
- `src/pages/RadarFomento.jsx` — pill opcional ao refrescar em background

### Constantes

| Constante | Valor | Descrição |
|-----------|-------|-----------|
| `RADAR_MATCH_CACHE_VERSION` | `'v2'` | Versão do algoritmo/formato; incrementar se mudar score ou shape dos itens |
| `RADAR_USE_COMPACT_WORKER_PAYLOAD` | `true` | Desligar em `constants/radarWorker.js` se regressão no worker |
| `RADAR_SESSION_CACHE_TTL_MS` | `2 * 60 * 60 * 1000` (2 h) | TTL; para testes curtos usar `30 * 60 * 1000` (30 min) |
| `RADAR_SESSION_CACHE_MAX_ENTRIES` | `10` | Máximo de clientes (chaves) na sessão |
| `RADAR_SESSION_CACHE_STALE_SOON_RATIO` | `0.75` | Idade ≥ 75% do TTL → hit válido + recálculo em background |

### Chave de armazenamento

```
radar:v1:<clienteId>:<catalogFingerprint>:<clienteFingerprint>:<optionsFingerprint>
```

- **catalogFingerprint**: assinatura da lista de editais (tamanho, amostragem por stride, hash)
- **clienteFingerprint**: hash dos campos de perfil usados no match (`id`, `perfil`, `setor`, `porte`, `cnae`, `area_inovacao`, `interesse_temas`, etc.)
- **optionsFingerprint**: hash das opções do Radar (`incluirSuspeitos`, cortes, `limite`, etc.)

Índice auxiliar: `radar:session:index` (lista de chaves + `updatedAt` para LRU prune).

### Payload salvo

```json
{
  "clienteId": "...",
  "generatedAt": 1710000000000,
  "expiresAt": 1710007200000,
  "partial": false,
  "source": "session_cache",
  "items": [ /* linhas do radar, só o necessário para cards */ ],
  "meta": {
    "catalogFingerprint": "...",
    "clienteFingerprint": "...",
    "optionsFingerprint": "...",
    "algorithmVersion": "v1",
    "totalIn": 1200,
    "afterPreFilter": 800
  }
}
```

**Não** persistir resultados parciais (prévia top 20).

### Fluxo (`useRadarMatches`)

1. Cache em memória (entrada completa) → render imediato, `cache_hit`.
2. Senão, `loadRadarSessionCache` → se válido:
   - Hidrata memória + UI imediata.
   - Log `[radar-perf] session_cache_hit`.
   - Se `staleSoon` (TTL quase expirado): worker em background, pill “Resultado em cache — atualizando…”.
   - Senão: fim (sem worker).
3. Miss → worker / main thread como nas fases 0.5–0.6.
4. Ao `full_results`: `saveRadarSessionCache` (apenas completo).

`recalculate()` chama `invalidateRadarSessionCacheForCliente(clienteId)`.

### Invalidação

Entrada rejeitada (removida) se:

- `expiresAt` passou (log `session_cache_stale` ou miss com `reason: expired`);
- `meta.algorithmVersion !== RADAR_MATCH_CACHE_VERSION`;
- `catalogFingerprint`, `clienteFingerprint` ou `optionsFingerprint` divergem;
- `clienteId` não confere.

### Segurança e limites

- Tratamento de `QuotaExceededError`: prune agressivo (metade do máximo) e uma nova tentativa de gravação.
- Prune LRU ao exceder `RADAR_SESSION_CACHE_MAX_ENTRIES`.
- Sem `localStorage` nesta fase.
- Dados limitados aos itens já renderizados nos cards (mesmo shape do resultado em memória).

### Logs DEV (`[radar-perf]`)

| Evento | Quando |
|--------|--------|
| `session_cache_hit` | Entrada válida lida |
| `session_cache_miss` | Sem entrada ou fingerprint inválido |
| `session_cache_stale` | Hit com TTL quase expirado (background refresh) |
| `session_cache_save` | Gravação após cálculo completo |
| `session_cache_prune` | Remoção por LRU ou `invalidate` |
| `session_cache_error` | Erro de parse, quota, etc. |

### Como validar

1. Abrir Radar, selecionar cliente, aguardar lista completa.
2. Recarregar a página (F5) — resultados devem aparecer sem skeleton longo; console com `session_cache_hit`.
3. Alterar opções do Radar (ex. incluir aproximados) — deve dar `session_cache_miss` (options fingerprint).
4. `recalculate()` — invalida session do cliente e recalcula.
5. `npm run build` em `frontend/EditalFinder-React`.

### Restrições mantidas

- Sem alteração de `radarMatch.js` / regras de score.
- Sem backend, Supabase ou SQL.
- Sem mudanças em Notícias, Concursos ou Editais.

---

## Fase 0.9A — Pré-filtro anti-ruído do catálogo

### Objetivo

Reduzir itens enviados ao Worker **antes** do score, removendo ruído do catálogo sem apagar dados no banco e sem alterar o cálculo dos itens válidos.

### Arquivos

- `src/utils/radar/radarCatalogPrefilter.js` — `prefilterRadarCatalog`, `logRadarCatalogNoise`
- `src/constants/radarPrefilter.js` — `RADAR_USE_CATALOG_PREFILTER`, `RADAR_PREFILTER_VERSION`
- `src/hooks/useRadarMatches.js` — aplica pré-filtro em `runComputation` → Worker / main thread
- `RadarFomento.jsx` — hint em opções avançadas

### Flag

| Constante | Padrão | Descrição |
|-----------|--------|-----------|
| `RADAR_USE_CATALOG_PREFILTER` | `true` | Desligar em `radarPrefilter.js` se regressão |
| `RADAR_PREFILTER_VERSION` | `9a-v1` | Incluída na chave de cache em memória |

### Regras (ordem de avaliação)

| Regra | Remoção | Exceção |
|-------|---------|---------|
| A) Prazo encerrado | `removed_expired` | `incluirEncerrados` / `includeExpired` |
| B) Sem link útil | `removed_missing_link` | `id_edital` + descrição longa (≥180 chars) |
| C) Tipo inadequado | `removed_invalid_type` | Sinais fortes de fomento |
| D) Título genérico | `removed_generic_title` | Sinais fortes |
| E) Qualidade baixa | `removed_low_quality` | Fonte estratégica / sinais fortes |
| F) Duplicata | `removed_duplicate` | link, título+fonte, `hash_deduplicacao` |

**Allowlist (sinais fortes):** chamada pública, edital de fomento, subvenção, bolsa, programa, financiamento, CNPq, FINEP, CAPES, FAPERGS, FAPESC, FAPESP, MCTI, SENAI, EMBRAPII, BNDES, internacional, etc.

### Logs DEV `[radar-noise]`

- `catalog_total`
- `after_existing_filters` (com id + título)
- `removed_expired`
- `removed_invalid_type`
- `removed_missing_link`
- `removed_duplicate`
- `removed_low_quality`
- `sent_to_worker`
- `rejected_sample` (até 12 itens com `reason`)

Também: `[radar-perf] catalog_prefilter` no mark da sessão DEV.

### UI

Em **Opções avançadas**: “Catálogo filtrado: **X** de **Y** oportunidades consideradas no cálculo”.

### Como validar

1. Abrir Radar, cliente qualquer — console `[radar-noise]` com `sent_to_worker` &lt; `catalog_total`.
2. Marcar “Incluir editais encerrados” — `removed_expired` deve cair.
3. Recalcular — stats atualizam; Worker recebe menos itens (`worker_payload_size_items`).
4. Resultados: menos encerrados/ruído na lista; score dos válidos inalterado.
5. `RADAR_USE_CATALOG_PREFILTER = false` — catálogo integral volta ao Worker (comparar tempos).
6. `npm run build` — sem erros.

---

## Explicabilidade do match (consultor)

### Objetivo

Deixar claro **por que** cada edital aparece para o cliente, sem alterar o score (`calcularMatchRadar`).

### Arquivos

- `src/utils/radar/radarMatchExplain.js` — `buildRadarCardExplanation(hit, edital, prazo)`
- `radarMatchToCardPayload` — anexa `razoesPositivas`, `radar_alertas`, `radar_dimensoes`, `matchLinha` (resumo)
- `CardEditalRadar.jsx` — seção **“Por que combina com este cliente?”**

### Estrutura no card

1. **Resumo** — compatibilidade % + destaques fortes  
2. **Motivos positivos** — afinidade, perfil, tipo, localização, prazo, valor  
3. **Alertas** — prazo curto, dados incompletos, título genérico, baixa aderência por dimensão, penalidades  
4. **Dimensões avaliadas** — 6 linhas: afinidade temática, modalidade/recurso, área/setor/perfil, localização, prazo, valor/porte  
5. **Pontuação técnica** (opcional, `<details>`) — barras com pts/max (inalterado)

### Dimensões exibidas

| Chave | Rótulo no card |
|-------|----------------|
| `afinidade` | Afinidade temática |
| `tipo` | Modalidade / recurso |
| `perfil` | Área, setor e perfil |
| `localizacao` | Localização |
| `prazo` | Prazo |
| `valor` | Valor e porte |

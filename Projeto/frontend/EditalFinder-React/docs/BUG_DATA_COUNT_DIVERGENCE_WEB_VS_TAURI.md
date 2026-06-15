# BUG — Divergência de contagem de editais entre site e EXE/Tauri

**Status:** diagnóstico (sem correção de risco aplicada). Foram criados apenas
utilitários dev-only de diagnóstico + testes.

## 1. Sintoma

- Site/web mostra **~1057** editais.
- App desktop (EXE/Tauri) mostra **~430 e poucos** editais.

## 2. Onde o número ~1057 é calculado

Origem: `src/services/dataService.js → getEditais()`. Ele pagina a view
`vw_editais_front` (env `VITE_VIEW_EDITAIS`) em páginas de **1000** até esgotar:

```12:14:src/services/editaisService.js
export async function fetchEditaisCatalog() {
  return dataService.getEditais();
}
```

O total exibido vem do `EditaisStatsBar` em `EditaisPage.jsx`:

```19:23:src/components/dashboard/EditaisStatsBar.jsx
        <strong>
          Mostrando {filteredCount}
          {catalogCount != null ? ` de ${catalogCount} recebidos` : ''} editais
        </strong>
```

- `catalogCount` = `allEditais.length` = linhas recebidas da view (**~1051**).
- `filteredCount` = `sortedFiltered.length` = após filtros client-side (**~430**).

**Evidência direta (anon key, leitura ao vivo):**

```
GET /rest/v1/vw_editais_front?select=id  (Prefer: count=exact)
Content-Range: 0-0/1051
```

Ou seja, a anon key (a mesma usada por web E desktop) enxerga **1051** linhas na
view. O “~1057” do site é o `catalogCount`.

## 3. Onde o número ~430 é calculado

Dois caminhos possíveis, ambos compatíveis com “430 e poucos”:

1. **`filteredCount`** — após os filtros padrão de `INITIAL_SIDEBAR_FILTERS()`
   (`filtersEngine.js`), que por padrão **ocultam**:
   - inativos (`ativo === false`),
   - `suspeito` (`validacao_status`),
   - prazo vencido / encerrados (`toggleIncluirEncerrados: false`),
   - títulos de ruído (até liberar nas preferências).

   Reduzir ~1051 → ~430 é exatamente o esperado (sobram abertos + sem prazo não-ruído).

2. **Build antigo** — o EXE instalado embute um frontend mais velho que busca/filtra
   de forma diferente (ver §8).

## 4. Diferenças de query (web vs EXE)

Não há diferença de query no **código atual**: o mesmo `getEditais()` roda nos dois.
Não há `.limit(500)`, `.range(0,499)`, `MAX_ITEMS` nem `PAGE_SIZE` fixo pequeno — a
paginação é um loop com `PAGE = 1000` até a página vir incompleta:

```96:108:src/services/dataService.js
        const q = await supabase
          .from(table)
          .select('*')
          .order(orderCol, { ascending: false, nullsFirst: false })
          .range(from, from + PAGE - 1);
        if (q.error) throw q.error;
        if (!q.data?.length) break;
        all.push(...q.data);
        if (q.data.length < PAGE) break;
        from += PAGE;
```

Há um **fallback** para a tabela `edital` se a view falhar — mas isso traria *mais*
linhas (a tabela tem ~1232), não menos. Logo o fallback **não** explica 430.

## 5. Diferenças de ambiente

- `.env.local` é o **mesmo** para web e desktop. Não existem `.env.tauri` /
  `.env.production` no projeto (só `.env.local` e `.env.example`).
- `vite build --mode tauri` só muda `VITE_ROUTER_BASENAME`, `VITE_TAURI` e `base`
  (assets relativos). **Não** muda Supabase URL/key nem a view.
- Portanto, no código atual, web e desktop apontam para o **mesmo** projeto Supabase
  (`dofppvnjbegwwhvtfnec.supabase.co`) e a **mesma** view.

> ⚠️ Ressalva: não dá para garantir qual `.env.local` estava em disco no momento do
> build do EXE (Jun 5). Se na época apontasse para outro projeto, o EXE consultaria
> outro banco. O debug de runtime (§10) loga `supabaseHost` para confirmar.

## 6. Diferenças de filtros

Os filtros padrão são iguais no código, **mas o estado persiste em `localStorage`,
que é por origem**:

- Web (GitHub Pages): origem `https://…github.io`.
- Desktop (Tauri webview): origem `tauri://localhost` / `https://tauri.localhost`.

São *stores separados*. Se no navegador o usuário já clicou em “Mostrar tudo” /
“Relaxar filtros” / “Incluir encerrados” (persistido), o site mostra muito mais que
o EXE recém-instalado, que está no default restritivo (~430).

## 7. Diferenças de cache / fallback / mock

- **Sem snapshot/mock/fallback bundled** no frontend (busca em `src/` por
  `snapshot|mockEditais|fallbackData|editais.json` não achou fonte de dados local).
- Cache relevante = `localStorage` de filtros/prefs/favoritos (por origem, ver §6).
- Não há service worker de dados.

## 8. Hipótese principal

**Combinação de (a) build desktop desatualizado + (b) filtros padrão client-side.**

Evidência de build velho:

| Artefato | LastWriteTime |
|---|---|
| `dist/assets/index-*.js` (web atual) | **2026-06-09 18:40** |
| `src-tauri/target/release/editalfinder.exe` | **2026-06-05 04:51** |
| `…/bundle/nsis/EditalFinder_0.1.0_x64-setup.exe` | **2026-06-05 04:51** |

O EXE instalado é **4 dias mais velho** que o build web atual. Nesse intervalo houve
mudanças relevantes (patches de backend 10.3A/10.3B e frontend 1.2A). Se o frontend
embutido no EXE de Jun 5 tinha lógica de busca/filtro diferente (ou apontava para
outro `.env`), ele exibe menos itens mesmo lendo dados ao vivo.

Mesmo que o EXE de Jun 5 leia os mesmos 1051 da view, o número “430” bate com o
`filteredCount` padrão — e o “1057” do site bate com o `catalogCount`. Ou seja, em
boa parte dos casos **os dois números corretos estão na mesma tela** (“Mostrando 430
de 1051 recebidos”), e a “divergência” é de **leitura/estado de filtro**, não de dados.

## 9. Evidência no código (resumo)

- Fonte única: view `vw_editais_front` paginada sem limite fixo (`dataService.js`).
- `catalogCount` vs `filteredCount` exibidos juntos (`EditaisStatsBar.jsx`).
- Filtros padrão restritivos (`filtersEngine.js → INITIAL_SIDEBAR_FILTERS`).
- RLS de `edital`: `anon_all_edital ... USING (true)` (`CORE/schema_sql_completo.sql`)
  → anon vê tudo; a view é SECURITY DEFINER → não há divergência por auth.
- Anon ao vivo: `Content-Range: 0-0/1051` na view.

## 10. Correção recomendada

Nada de risco foi alterado. Para **confirmar a causa em cada plataforma**, foi
adicionado um diagnóstico dev-only (ligado por flag):

```
# .env.local (apenas para investigar)
VITE_DEBUG_DATA_COUNTS=1
```

Com a flag, `getEditais()` loga:

```
[EditalFinder][DataCountDebug] { rawCount, catalogCount, filteredCount, runtime, supabaseHost, appVersion, buildMode }
```

E `logRuntimeDataSourceInfo()` (de `src/utils/debugRuntimeDataSource.js`) loga runtime,
host do Supabase e `hasSupabaseAnonKey` (sem vazar a chave).

Interpretação:

- **rawCount diferente entre web e EXE** → build/env diferentes (rebuild ou `.env`).
- **rawCount igual, filteredCount menor no EXE** → é estado de filtro/localStorage;
  basta “Relaxar filtros / Incluir encerrados” ou comparar o `catalogCount`.

Ação prática mais provável: **rebuildar e reinstalar o desktop**
(`npm run build:tauri` + `npm run desktop:build`) para alinhar o EXE ao código atual,
e então comparar os números de novo com a flag de debug ligada.

## 11. Riscos

- Nenhuma alteração de schema, Supabase, policies, filtros padrão ou regra de negócio.
- O diagnóstico só roda com `VITE_DEBUG_DATA_COUNTS=1`; em produção sem a flag é no-op.
- `probeCount` usa `head: true` (não baixa payload) — custo desprezível.

## 12. Testes necessários / executados

`src/utils/debugRuntimeDataSource.test.js` (node --test), 13 casos:

- runtime desktop/web/unknown detectado;
- env não expõe a anon key (só host + `hasSupabaseAnonKey`);
- `redactKey` nunca devolve a chave completa;
- `dataCountsEnabled` só liga com flag truthy;
- `probeCount` usa `head:true`/`count:exact`;
- `logEditalDataCounts` é no-op sem flag e separa raw/catalog/filtered.

Suite completa do front: **145/145 passam**.

## Próximo passo recomendado

1. Ligar `VITE_DEBUG_DATA_COUNTS=1`, rodar **no site** e **no EXE atual**, comparar
   `rawCount`/`catalogCount`/`filteredCount`/`supabaseHost`.
2. Rebuildar/reinstalar o desktop e repetir.
3. Se confirmar que é só estado de filtro: avaliar (patch separado) mostrar o
   `catalogCount` de forma mais proeminente e/ou resetar filtros no primeiro load do
   desktop. Se confirmar env/build divergente: corrigir o pipeline de release do EXE.

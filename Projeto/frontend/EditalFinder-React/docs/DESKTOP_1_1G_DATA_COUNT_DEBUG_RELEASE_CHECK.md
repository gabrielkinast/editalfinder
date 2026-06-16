# DESKTOP 1.1G — DATA COUNT DEBUG RELEASE CHECK

Patch pequeno de **validação/release**. Objetivo: confirmar, no EXE novo, se a
divergência **1057 (site) vs ~430 (EXE)** era causada por **build desktop antigo +
diferença entre `catalogCount` e `filteredCount`** (e não por dados/env diferentes).

> Nada de filtros, regra de contagem, Supabase ou backend foi alterado.

## 1. Sintoma

- Site/web: **~1057** editais.
- EXE/Tauri (build antigo, 05/06): **~430 e poucos** editais.

## 2. Diagnóstico atual (resumo do patch anterior)

- A anon key (mesma no web e no EXE) enxerga **1051** linhas na view
  `vw_editais_front` ao vivo (`Content-Range: 0-0/1051`).
- O `EditaisStatsBar` mostra **"Mostrando {filteredCount} de {catalogCount} recebidos"**:
  - `catalogCount` ≈ 1051 (linhas recebidas);
  - `filteredCount` ≈ 430 (após filtros padrão client-side: oculta encerrados,
    suspeitos, ruídos e inativos).
- RLS de `edital` é `anon ... USING(true)` e a view é SECURITY DEFINER → sem
  divergência por autenticação. Sem snapshot/mock/fallback no frontend.
- O EXE instalado era **4 dias mais velho** que o build web → suspeita de build antigo.

Conclusão provável: **build antigo + confusão visual entre total recebido e total
filtrado** (Caso C abaixo).

## 3. Como o debug funciona (sem vazar secrets)

Dois jeitos de ligar (qualquer um):

1. **Build/dev time** — variável Vite em `.env.local`:

   ```
   VITE_DEBUG_DATA_COUNTS=1
   ```

   Obs.: o Vite **inlina** `import.meta.env` no bundle; para o EXE, a flag precisa
   estar setada **antes** do `tauri build`.

2. **Runtime (sem rebuild)** — `localStorage` (web e `desktop:dev`):

   ```js
   localStorage.setItem('EDITALFINDER_DEBUG_DATA_COUNTS', '1'); // depois recarregar
   ```

Quando ligado, ao abrir a lista de editais aparecem no console:

```
[EditalFinder][DataCountDebug]        { rawCount, catalogCount, runtime, supabaseHost, viewEditais, appVersion, buildMode, rawError }
[EditalFinder][DataCountDebug][client] { catalogCount, filteredCount, runtime, supabaseHost, viewEditais, appVersion, buildMode }
```

Segurança: nunca loga a anon key (apenas `supabaseHost` e, no runtime-info,
`hasSupabaseAnonKey: true/false`). `probeCount` usa `head:true` (não baixa payload).

### Sem devtools no EXE release?

O build release do Tauri normalmente não tem inspector. Nesse caso, use o
**método sem ferramentas**: leia o texto do `EditaisStatsBar` na própria tela:

> **"Mostrando 430 de 1051 recebidos editais"**

- O número depois de **"de … recebidos"** é o `catalogCount` (o que importa para
  comparar com o site).
- Para ver `rawCount`/`supabaseHost`/`runtime`, rode em **`npm run desktop:dev`**
  (modo dev tem console) com a flag ligada.

## 4. Comandos

Testes + builds (executados neste patch):

```powershell
cd frontend/EditalFinder-React
npm test
npm run build          # build web (GitHub Pages)
npm run build:tauri    # dist do desktop (sem compilar Rust)
npm run desktop:build  # = tauri build (EXE + instalador NSIS)
```

Coletar logs:

- **Web (dev):**
  ```powershell
  # .env.local: VITE_DEBUG_DATA_COUNTS=1
  npm run dev
  # abrir /editalfinder/editais, ver console
  ```
- **Web (deploy):** abrir o site, no console:
  ```js
  localStorage.setItem('EDITALFINDER_DEBUG_DATA_COUNTS','1'); location.reload();
  ```
- **Desktop (dev, com console):**
  ```powershell
  # .env.local: VITE_DEBUG_DATA_COUNTS=1
  npm run desktop:dev
  ```
- **Desktop (EXE release):** instalar o novo
  `src-tauri/target/release/bundle/nsis/EditalFinder_0.1.0_x64-setup.exe` e ler o
  `EditaisStatsBar` ("de X recebidos").

## 5. Logs a coletar (web vs EXE)

| Campo | Web | EXE/Tauri |
|---|---|---|
| `rawCount` (servidor, view) | | |
| `catalogCount` (recebido) | | |
| `filteredCount` (após filtros) | | |
| `supabaseHost` | | |
| `runtime` | `web` | `desktop_tauri` |
| `buildMode` | `production` | `tauri` |

## 6. Como interpretar

**Caso A — `rawCount` igual, `catalogCount` igual, `filteredCount` diferente**
→ A diferença é **estado/filtros client-side** (localStorage por origem).
→ Próximo patch: **UX do contador/filtros** (ex.: destacar total recebido, opção de
   reset de filtros). Sem problema de dados.

**Caso B — `rawCount` diferente e/ou `supabaseHost` diferente**
→ O EXE foi buildado com **env diferente** (outro projeto Supabase/chave).
→ Próximo patch: **release/env hardening** (fixar `.env` do build, validar host).

**Caso C — `rawCount`, `catalogCount` e `filteredCount` iguais no EXE novo**
→ Era **build antigo** + confusão visual entre total recebido e total filtrado.
→ Próximo patch: **UX opcional do contador** (ou nenhum ajuste necessário).

## 7. Resultado deste patch

- `npm test`: **148/148** ok.
- `npm run build`: ok (`✓ built`).
- `npm run build:tauri`: ok (`✓ built`).
- `npm run desktop:build`: ok — novo EXE e instalador gerados (09/06 ~19:2x),
  substituindo o build de 05/06.

O EXE novo já contém o build atual + o debug ligável por env ou `localStorage`.
A confirmação final (A/B/C) deve ser feita instalando o EXE novo e comparando os
números com o site usando esta doc.

## 8. Limitações

- Sem a flag (env ou localStorage), tudo é **no-op** — seguro em produção.
- No EXE release sem devtools, só o `catalogCount` é legível na tela; para os demais
  campos use `desktop:dev`.
- A flag por env precisa estar no `.env.local` **antes** do `tauri build`.

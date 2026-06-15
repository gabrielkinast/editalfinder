import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const __dirname = dirname(fileURLToPath(import.meta.url))

/** Versão canônica do app desktop (alinhar release com tauri.conf.json). */
function readTauriAppVersion() {
  try {
    const confPath = resolve(__dirname, 'src-tauri/tauri.conf.json')
    const conf = JSON.parse(readFileSync(confPath, 'utf-8'))
    return conf.version || '0.1.0'
  } catch {
    return '0.1.0'
  }
}

const appVersion = readTauriAppVersion()

/**
 * Desktop: `vite build --mode tauri` (beforeBuildCommand) ou TAURI_ENV_PLATFORM no `tauri dev`.
 * Não depender só da env do CLI — no Windows ela pode falhar e gerar base `/editalfinder/` no EXE.
 */
function resolveIsTauri(mode) {
  return mode === 'tauri' || Boolean(process.env.TAURI_ENV_PLATFORM || process.env.TAURI_PLATFORM)
}
const webBase = '/editalfinder/'

/** Em dev web, quem abre só `http://localhost:5173/` cai fora do basename; redireciona para a SPA. */
function redirectRootToBase() {
  return {
    name: 'redirect-root-to-editalfinder-base',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const pathOnly = (req.url || '').split('?')[0]
        if (pathOnly === '/' || pathOnly === '') {
          res.statusCode = 302
          res.setHeader('Location', webBase)
          res.end()
          return
        }
        next()
      })
    },
  }
}

export default defineConfig(({ mode }) => {
  const isTauri = resolveIsTauri(mode)
  const assetBase = isTauri ? './' : webBase
  const routerBasename = isTauri ? '' : '/editalfinder'

  return {
    plugins: [react(), ...(isTauri ? [] : [redirectRootToBase()])],
    base: assetBase,
    define: {
      'import.meta.env.VITE_ROUTER_BASENAME': JSON.stringify(routerBasename),
      'import.meta.env.VITE_TAURI': JSON.stringify(isTauri ? '1' : ''),
      'import.meta.env.VITE_APP_VERSION': JSON.stringify(appVersion),
    },
    build: {
      commonjsOptions: {
        transformMixedEsModules: true,
      },
    },
    server: {
      open: isTauri ? '/' : webBase,
    },
  }
})

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/** Em dev, quem abre só `http://localhost:5173/` cai fora do basename; redireciona para a SPA. */
function redirectRootToBase() {
  return {
    name: 'redirect-root-to-editalfinder-base',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const pathOnly = (req.url || '').split('?')[0]
        if (pathOnly === '/' || pathOnly === '') {
          res.statusCode = 302
          res.setHeader('Location', '/editalfinder/')
          res.end()
          return
        }
        next()
      })
    },
  }
}

export default defineConfig({
  plugins: [react(), redirectRootToBase()],
  base: "/editalfinder/", // Tem que ser EXATAMENTE assim (alinhar com BrowserRouter basename)
  server: {
    /** Abre já na rota correta (evita página em branco na raiz). */
    open: '/editalfinder/',
  },
})
# Checklist — Release Desktop EditalFinder

## Antes de gerar

- [ ] Versão atualizada em `src-tauri/tauri.conf.json` e `package.json`
- [ ] `.env.production` / `.env.local` de build revisado (não commitar)
- [ ] `VITE_SUPABASE_URL` aponta para o projeto correto
- [ ] `VITE_SUPABASE_ANON_KEY` — **nunca** `service_role`
- [ ] `VITE_ENABLE_CONSULTOR_WORKSPACE=true` (se o cliente usa Workspace)
- [ ] `npm run build` passa (build web)
- [ ] `npm run desktop:build` passa (ou `npm run desktop:release`)

## Depois de gerar (`/releases`)

- [ ] `EditalFinder_v*_Windows_x64_Setup.exe` presente
- [ ] `SHA256SUMS_v*.txt` gerado; hash conferido se necessário
- [ ] Nenhum `.exe` / `.msi` staged no Git (`git status`)

## Teste do instalador (máquina limpa ou usuário de teste)

- [ ] Instalar via **Setup.exe** (NSIS)
- [ ] App abre em janela desktop
- [ ] **Login** funciona
- [ ] **Dashboard** carrega
- [ ] **Editais** lista e abre detalhe
- [ ] Menu **☰** (hambúrguer) funciona
- [ ] **Ajuda / Tutorial** abre
- [ ] **Workspace do Consultor** visível (se flag ativa e permissão)
- [ ] **Reportar problema** envia / não quebra
- [ ] `/workspace-cientifico` redireciona para `/dashboard` (não aparece no menu)
- [ ] Versão exibida no menu ou em **Configurações** (`EditalFinder vX.Y.Z`)

## Entrega ao cliente

- [ ] Enviar Setup.exe (+ README_RELEASE opcional)
- [ ] Informar necessidade de **internet**
- [ ] Informar que **atualização é manual** (sem auto-update)

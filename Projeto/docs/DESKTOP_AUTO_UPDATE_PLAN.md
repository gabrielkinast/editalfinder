# Plano futuro — Auto-update EditalFinder Desktop

**Status:** não implementado. Releases atuais são **manuais** (`DESKTOP_RELEASE_PROCESS.md`).

## Objetivo

Permitir que o app desktop verifique novas versões e instale atualizações com confirmação do usuário, sem redistribuir `.exe` por e-mail a cada patch.

## Componentes previstos

### 1. Plugin oficial Tauri

- [`@tauri-apps/plugin-updater`](https://v2.tauri.app/plugin/updater/)
- Configuração em `tauri.conf.json` + permissões em `capabilities/`
- Endpoint ou `latest.json` com metadados da versão

### 2. Assinatura

- Gerar par de chaves (`tauri signer generate`)
- Assinar bundles no CI ou na máquina de release
- Chave privada **nunca** no repositório (secrets do CI)

### 3. Hospedagem dos instaladores

Opções:

- **GitHub Releases** — tags `desktop-v0.1.1`, anexar `Setup.exe` + `latest.json`
- **S3 / blob storage** — URL pública ou assinada
- **Site próprio** — CDN com HTTPS

`latest.json` exemplo (conceitual):

```json
{
  "version": "0.1.1",
  "notes": "Correções no Radar e no tutorial.",
  "pub_date": "2026-06-01T12:00:00Z",
  "platforms": {
    "windows-x86_64": {
      "url": "https://.../EditalFinder_0.1.1_x64-setup.exe",
      "signature": "..."
    }
  }
}
```

### 4. Fluxo no app

1. Ao abrir (ou menu “Verificar atualizações”), GET no manifest
2. Comparar com `APP_VERSION` / versão Tauri
3. Se houver update → diálogo “Nova versão disponível”
4. Download + apply via plugin (Windows: substitui via instalador silencioso ou pacote assinado)

### 5. CI/CD (futuro)

- Workflow: tag → `npm run desktop:build` → assinar → upload → atualizar `latest.json`
- Reutilizar `scripts/create_desktop_release.py` como base de naming/hash

## Pré-requisitos antes de codar

- [ ] Certificado de código Windows (reduz SmartScreen)
- [ ] Política de versionamento semver documentada
- [ ] Canal estável vs beta (opcional)

## O que não fazer na fase 1 (atual)

- Não adicionar plugin-updater ao `Cargo.toml` ainda
- Não expor endpoint de update sem autenticação/rate limit se houver custo

## Referência

Documentação Tauri v2 Updater: https://v2.tauri.app/plugin/updater/

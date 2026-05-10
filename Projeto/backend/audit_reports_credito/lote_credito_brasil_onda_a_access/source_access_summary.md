# Auditoria de métodos de acesso por fonte

- Fontes analisadas: **5**
- Critério: pedidos HTTP modestos; respeito a `robots.txt` (não GET se `Disallow` explícito para o path).

## Resumo por classificação

- `ok_html_publico`: 3
- `captcha`: 1
- `cloudflare_403`: 1

## Por fonte

### `agerio`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_rss`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.agerio.com.br/linhas-de-credito/`

### `banco_da_amazonia`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.bancoamazonia.com.br/empresas/credito-e-financiamentos`

### `bdmg`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Seed:** `https://www.bdmg.mg.gov.br/`

### `bnb`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.bnb.gov.br/web/guest/produtos-e-servicos`

### `desenvolve_sp`
- **Classificação:** `cloudflare_403`
- **Método seguro recomendado:** `blocked_access_limited`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** acesso_limitado_waf_ou_robots
- **Seed:** `https://www.desenvolvesp.com.br/empresas/opcoes-de-credito/`

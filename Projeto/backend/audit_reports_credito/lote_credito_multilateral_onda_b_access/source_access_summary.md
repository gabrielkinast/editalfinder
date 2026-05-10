# Auditoria de métodos de acesso por fonte

- Fontes analisadas: **5**
- Critério: pedidos HTTP modestos; respeito a `robots.txt` (não GET se `Disallow` explícito para o path).

## Resumo por classificação

- `ok_html_publico`: 2
- `cloudflare_403`: 1
- `endpoint_quebrado`: 1
- `captcha`: 1

## Por fonte

### `bid_lab`
- **Classificação:** `cloudflare_403`
- **Método seguro recomendado:** `blocked_access_limited`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** acesso_limitado_waf_ou_robots
- **Seed:** `https://bidlab.org/en/call-for-proposals`

### `caf`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.caf.com/es/trabaja-con-nosotros/convocatorias/`

### `eic`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://eic.ec.europa.eu/eic-funding-opportunities_en`

### `eureka_network`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_rss`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.eurekanetwork.org/open-calls/`

### `fonplata`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Seed:** `https://www.fonplata.org/es/oportunidades`

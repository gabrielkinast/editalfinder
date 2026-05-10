# Auditoria de métodos de acesso por fonte

- Fontes analisadas: **102**
- Critério: pedidos HTTP modestos; respeito a `robots.txt` (não GET se `Disallow` explícito para o path).

## Resumo por classificação

- `ok_html_publico`: 55
- `endpoint_quebrado`: 19
- `captcha`: 13
- `fonte_sem_dados`: 6
- `cloudflare_403`: 3
- `access_http_403`: 3
- `spa_pouco_html`: 2
- `rate_limit_429`: 1

## Por fonte

### `abdi`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.abdi.com.br/`

### `afwerx`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_rss`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Seed:** `https://afwerx.com/divisions/afventures/`

### `amazul`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Domínio militar .mil.br; listagem ativa em /acesso-a-informacao/licitacoes-e-contratos (rotas /licitacoes e /chamadas-publicas retornam 404).
- **Seed:** `https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos`

### `ambev`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Hub externo 100accelerator; pode ser SPA — validar HTML real vs curadoria.
- **Seed:** `https://www.100accelerator.com/challenges`

### `aneel`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_json_ld`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.gov.br/aneel/pt-br`

### `anp`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_json_ld`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.gov.br/anp/pt-br`

### `apex`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Portal institucional Brasil.
- **Seed:** `https://apexbrasil.com.br/br/pt/acesso-a-informacao/licitacoes-e-contratos/editais.html`

### `badesul`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Seed:** `https://www.badesul.com.br`

### `bae_systems_suppliers`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Página corporativa suppliers.
- **Seed:** `https://www.baesystems.com/en/suppliers`

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
- **Seed:** `https://www.bdmg.mg.gov.br/linhaspermanentes`

### `bid_lab`
- **Classificação:** `cloudflare_403`
- **Método seguro recomendado:** `blocked_access_limited`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** acesso_limitado_waf_ou_robots
- **Seed:** `https://bidlab.org/en/call-for-proposals`

### `bnb`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.bnb.gov.br/web/guest/produtos-e-servicos`

### `bndes`
- **Classificação:** `fonte_sem_dados`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** sem_url_seed_configurada

### `brde`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_rss`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Seed:** `https://www.brde.com.br/`

### `caf`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.caf.com/es/trabaja-con-nosotros/convocatorias/`

### `caixa`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_rss`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.caixa.gov.br/empresa/credito-financiamento/Paginas/default.aspx`

### `capes`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.gov.br/capes/pt-br/assuntos/editais-e-resultados`

### `cbpf`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_json_ld`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.gov.br/cbpf/pt-br/acesso-a-informacao/acoes-e-programas`

### `china_avic`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Institucional CN; latência e WAF possíveis; manter escopo público declarado no crawler.
- **Seed:** `http://www.avic.com/`

### `china_caea`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.caea.gov.cn/`

### `china_cas`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.cas.cn/`

### `china_cgn`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.cgnpc.com.cn/`

### `china_cnnc`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Portal institucional; verificar robots.
- **Seed:** `https://www.cnnc.com.cn/`

### `china_mod_public`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `http://www.mod.gov.cn/`

### `china_mofcom_tendering`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.chinabidding.mofcom.gov.cn/`

### `china_most`
- **Classificação:** `spa_pouco_html`
- **Método seguro recomendado:** `usar_pagina_alternativa_oficial`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.most.gov.cn/`

### `china_norinco`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** HTTP legado no crawler; preferir HTTPS institucional se disponível.
- **Seed:** `http://en.norincogroup.com.cn/`

### `china_nsfc`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Gov.cn; latência e filtros regionais possíveis.
- **Seed:** `https://www.nsfc.gov.cn/`

### `china_tendering_bidding`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.cebpubservice.com/`

### `china_university_procurement`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Notas política:** Multi-universidade; robots por host.
- **Seed:** `https://cwc.tsinghua.edu.cn/`

### `cnen`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_json_ld`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.gov.br/cnen/pt-br`

### `cnpq`
- **Classificação:** `fonte_sem_dados`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** sem_url_seed_configurada

### `compras_defesa`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://dadosabertos.compras.gov.br/modulo-licitacoes/1_consultarLicitacao`

### `confap`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://confap.org.br/pt/editais`

### `darpa_opportunities`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_rss`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Seed:** `https://www.darpa.mil/work-with-us`

### `dcta_ita_iae`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** gov.br — listagens padronizadas.
- **Seed:** `https://www.gov.br/dcta/pt-br/chamamentos-e-licitacoes`

### `defesa`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.gov.br/defesa/pt-br/assuntos/editais`

### `diu`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.diu.mil/work-with-us`

### `dod_sbir_sttr`
- **Classificação:** `rate_limit_429`
- **Método seguro recomendado:** `blocked_access_limited`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** acesso_limitado_waf_ou_robots
- **Seed:** `https://api.www.sbir.gov/public/api/solicitations`

### `doe_arpae`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_curadoria_oficial_minima`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://arpa-e-foa.energy.gov/Default.aspx`

### `eic`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://eic.ec.europa.eu/eic-funding-opportunities_en`

### `eletronuclear`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.eletronuclear.gov.br/Paginas/canais-de-negocios.aspx`

### `embrapii`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Seed:** `https://embrapii.org.br/transparencia/#chamadas`

### `erc`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://erc.europa.eu/apply-grant`

### `eureka_network`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_rss`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.eurekanetwork.org/open-calls/`

### `european_defence_fund`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://defence-industry-space.ec.europa.eu/eu-defence-industry/european-defence-fund-edf_en`

### `fapemig`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://fapemig.br/pt/`

### `faperg`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Crawler faperg usa URLs FAPERGS RS (verificar consistência de naming).
- **Seed:** `https://fapergs.rs.gov.br/editais-abertos`

### `fapergs`
- **Classificação:** `fonte_sem_dados`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** sem_url_seed_configurada

### `fapesc`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_rss`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Seed:** `https://fapesc.sc.gov.br/`

### `fapesp`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://fapesp.br/chamadas/`

### `fappr`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.fappr.pr.gov.br/`

### `finep`
- **Classificação:** `fonte_sem_dados`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** sem_url_seed_configurada

### `fnde`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_json_ld`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas`

### `fonplata`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Seed:** `https://www.fonplata.org/es/oportunidades`

### `general_dynamics_suppliers`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.gd.com/suppliers`

### `grants_gov`
- **Classificação:** `access_http_403`
- **Método seguro recomendado:** `blocked_access_limited`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** acesso_limitado_waf_ou_robots
- **Seed:** `https://api.grants.gov/v1/api/search2`

### `horizon_europe`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://ec.europa.eu/info/funding-tenders/opportunities/data/topic-list.html`

### `iarpa`
- **Classificação:** `access_http_403`
- **Método seguro recomendado:** `usar_curadoria_oficial_minima`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** acesso_limitado_waf_ou_robots
- **Notas política:** Programas listados em iarpa.gov; oportunidades detalhadas costumam estar em catálogos Grants.gov (API pública documentada para integradores).
- **Seed:** `https://www.iarpa.gov/research-programs`

### `impa`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://impa.br/pt-br/`

### `inb`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.inb.gov.br/`

### `ipen`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_json_ld`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.gov.br/ipen/pt-br`

### `japan_aist`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_rss`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Seed:** `https://www.aist.go.jp/index_en.html`

### `japan_atla`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.mod.go.jp/atla/en/`

### `japan_e_rad`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** e-Rad institucional.
- **Seed:** `https://www.e-rad.go.jp/`

### `japan_ihi`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.ihi.co.jp/en/all_news/`

### `japan_jaea`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Institucional JAEA.
- **Seed:** `https://www.jaea.go.jp/english/`

### `japan_jaxa`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_curadoria_oficial_minima`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Press global vs site jp; validar duas origens.
- **Seed:** `https://global.jaxa.jp/press/`

### `japan_jetro_procurement`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.jetro.go.jp/en/database/procurement/`

### `japan_jsps`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.jsps.go.jp/english/index.html`

### `japan_jst`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** JST costuma expor feeds de notícias.
- **Seed:** `https://www.jst.go.jp/EN/news/index.html`

### `japan_kakenhi`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.jsps.go.jp/j-grantsinaid/03_keikaku/index.html`

### `japan_kawasaki_heavy`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Procurement global Kawasaki.
- **Seed:** `https://global.kawasaki.com/en/corp/profile/procurement/`

### `japan_kek`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_rss`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.kek.jp/en/news/`

### `japan_mext`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.mext.go.jp/en/news/index.htm`

### `japan_mitsubishi_heavy`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.mhi.com/finance/procurement/`

### `japan_mod`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.mod.go.jp/en/index.html`

### `japan_nedo`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.nedo.go.jp/english/index.html`

### `japan_nims`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_rss`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.nims.go.jp/eng/news/index.html`

### `japan_qst`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.qst.go.jp/site/qst-english/`

### `japan_riken`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_rss`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.riken.jp/en/news_pubs/news/index.html`

### `lockheed_martin_suppliers`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.lockheedmartin.com/en-us/suppliers.html`

### `mapa`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_json_ld`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.gov.br/agricultura/pt-br`

### `marinha`
- **Classificação:** `cloudflare_403`
- **Método seguro recomendado:** `blocked_access_limited`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** acesso_limitado_waf_ou_robots
- **Notas política:** gov.br; verificar listagens gov e anexos PDF oficiais.
- **Seed:** `https://www.marinha.mil.br/editais`

### `mcti`
- **Classificação:** `fonte_sem_dados`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** sem_url_seed_configurada

### `mma`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_json_ld`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.gov.br/mma/pt-br`

### `nato_diana`
- **Classificação:** `cloudflare_403`
- **Método seguro recomendado:** `usar_curadoria_oficial_minima`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** acesso_limitado_waf_ou_robots
- **Notas política:** HTML simples pode receber 403 Cloudflare. Preferir curadoria a partir de URLs oficiais publicadas; sitemap/robots se permitirem.
- **Seed:** `https://www.diana.nato.int/challenges.html`

### `nsf`
- **Classificação:** `access_http_403`
- **Método seguro recomendado:** `blocked_access_limited`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** acesso_limitado_waf_ou_robots
- **Seed:** `https://new.nsf.gov/funding/opportunities`

### `nuclep`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.nuclep.gov.br/`

### `petrobras`
- **Classificação:** `fonte_sem_dados`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** sem_url_seed_configurada

### `plataforma_industria`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.portaldaindustria.com.br/canais/plataforma-inovacao-para-industria/`

### `pncp`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Seed:** `https://github.com`

### `pncp_defesa`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Seed:** `https://github.com`

### `rheinmetall_suppliers`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Corporate DE.
- **Seed:** `https://www.rheinmetall.com/en/company/suppliers`

### `sam_gov`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_meta_tags`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** SAM.gov expõe APIs públicas documentadas (OpenAPI); evitar scraping pesado de UI.
- **Seed:** `https://sam.gov/content/opportunities`

### `saude`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_json_ld`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.gov.br/saude/pt-br`

### `science_scraper`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Agregador multi-domínio; validar robots e feeds por sítio alvo.
- **Seed:** `https://science.osti.gov/grants/FOAs/Open`

### `senai`
- **Classificação:** `endpoint_quebrado`
- **Método seguro recomendado:** `revisar_manualmente`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://www.portaldaindustria.com.br/senai/canais/chamadas-publicas/`

### `softex`
- **Classificação:** `captcha`
- **Método seguro recomendado:** `usar_rss`
- **Tag readiness (acesso):** `blocked_access_limited`
- **Interpretação:** destino_exige_login_ou_captcha_publico
- **Seed:** `https://softex.br/`

### `thales_suppliers`
- **Classificação:** `spa_pouco_html`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Notas política:** Procurement público.
- **Seed:** `https://www.thalesgroup.com/en/group/procurement`

### `wellcome`
- **Classificação:** `ok_html_publico`
- **Método seguro recomendado:** `usar_sitemap`
- **Tag readiness (acesso):** `ok`
- **Interpretação:** crawler_nao_evidenciado_como_quebrado_por_acesso
- **Seed:** `https://wellcome.org/grant-funding`

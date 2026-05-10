# Matriz de Fontes Asia (Japao + China)

Foco: oportunidades publicas e institucionais (P&D, chamadas, grants,
procurement publico, comunicados oficiais) ligadas a fisica, matematica,
quimica, ciencia dos materiais, nuclear (uso pacifico), aceleradores,
radiacao, semicondutores, tecnologias quanticas, aeroespacial, defesa
industrial publica e dual-use.

Nivel de sensibilidade fixado em `publico_institucional`. Conteudo
sensivel (manuais de armamento, fabricacao, municao, agentes quimicos /
radiologicos) e filtrado por `asia_intel.has_sensitive_content`.

## Japao - implementadas

| Pasta | Fonte | URL principal | Tipo | Idioma | Dificuldade | Robots | Status |
|---|---|---|---|---|---|---|---|
| `japan_jst` | JST - Japan Science and Technology Agency | https://www.jst.go.jp/ | HTML | ja/en | Baixa | Sim | implementado |
| `japan_jsps` | JSPS - Japan Society for the Promotion of Science | https://www.jsps.go.jp/ | HTML | ja/en | Baixa | Sim | implementado |
| `japan_kakenhi` | KAKENHI Grants-in-Aid | https://www.jsps.go.jp/j-grantsinaid/ | HTML | ja/en | Media | Sim | implementado |
| `japan_e_rad` | e-Rad (area publica) | https://www.e-rad.go.jp/ | HTML | ja | Media (parte publica) | Sim | implementado |
| `japan_mext` | MEXT | https://www.mext.go.jp/ | HTML | ja/en | Media | Sim | implementado |
| `japan_qst` | QST | https://www.qst.go.jp/ | HTML | ja/en | Media | Sim | implementado |
| `japan_jaea` | JAEA | https://www.jaea.go.jp/ | HTML | ja/en | Media | Sim | implementado |
| `japan_nims` | NIMS | https://www.nims.go.jp/ | HTML | ja/en | Baixa | Sim | implementado |
| `japan_riken` | RIKEN | https://www.riken.jp/ | HTML | ja/en | Media | Sim | implementado |
| `japan_kek` | KEK | https://www.kek.jp/ | HTML | ja/en | Media | Sim | implementado |
| `japan_jetro_procurement` | JETRO Government Procurement | https://www.jetro.go.jp/en/database/procurement/ | HTML | en | Baixa | Sim | implementado |
| `japan_atla` | ATLA - apenas oportunidades publicas | https://www.mod.go.jp/atla/ | HTML | ja/en | Media/Alta | Sim | implementado (escopo publico) |
| `japan_mod` | Japan MoD - apenas comunicados publicos | https://www.mod.go.jp/ | HTML | ja/en | Media | Sim | implementado (escopo publico) |
| `japan_jaxa` | JAXA | https://www.jaxa.jp/ | HTML | ja/en | Media | Sim | implementado |
| `japan_nedo` | NEDO | https://www.nedo.go.jp/ | HTML | ja/en | Media | Sim | implementado |
| `japan_aist` | AIST | https://www.aist.go.jp/ | HTML | ja/en | Media | Sim | implementado |

## China - implementadas

| Pasta | Fonte | URL principal | Tipo | Idioma | Dificuldade | Robots | Status |
|---|---|---|---|---|---|---|---|
| `china_nsfc` | NSFC | https://www.nsfc.gov.cn/ | HTML | zh/en | Media | Sim | implementado |
| `china_most` | MOST | https://www.most.gov.cn/ | HTML | zh/en | Media | Sim | implementado |
| `china_cas` | CAS | https://www.cas.cn/ | HTML | zh/en | Media | Sim | implementado |
| `china_caea` | CAEA - apenas comunicados publicos | https://www.caea.gov.cn/ | HTML | zh/en | Media/Alta | Sim | implementado (escopo publico) |
| `china_cnnc` | CNNC - procurement publico | https://www.cnnc.com.cn/ | HTML | zh/en | Media | Sim | implementado |
| `china_cgn` | CGN - procurement publico | https://www.cgnpc.com.cn/ | HTML | zh | Media | Sim | implementado |
| `china_mofcom_tendering` | MOFCOM / China International Tendering | https://www.chinabidding.mofcom.gov.cn/ | HTML | zh/en | Media | Sim | implementado |
| `china_tendering_bidding` | China Tendering and Bidding Public Service | https://www.cebpubservice.com/, https://www.ggzy.gov.cn/ | HTML | zh | Media/Alta | Parcial | implementado (apenas area publica) |
| `china_university_procurement` | Tsinghua + Peking U. + USTC (consolidado) | varios | HTML | zh/en | Media | Sim | implementado |
| `china_mod_public` | China MoND - apenas comunicados publicos | http://www.mod.gov.cn/ | HTML | zh/en | Media | Sim | implementado (escopo publico) |

## Fase 2 - Suppliers privados (implementadas, escopo publico)

| Pasta | Fonte | URL principal | Tipo | Idioma | Dificuldade | Robots | Status |
|---|---|---|---|---|---|---|---|
| `japan_mitsubishi_heavy` | Mitsubishi Heavy Industries | https://www.mhi.com/finance/procurement/ | HTML | en/ja | Media | Sim | implementado (escopo publico) |
| `japan_kawasaki_heavy` | Kawasaki Heavy Industries | https://global.kawasaki.com/en/corp/profile/procurement/ | HTML | en/ja | Media | Sim | implementado (escopo publico) |
| `japan_ihi` | IHI Corporation | https://www.ihi.co.jp/en/company/procurement/ | HTML | en/ja | Media | Sim | implementado (escopo publico) |
| `china_norinco` | NORINCO Group | http://en.norincogroup.com.cn/ | HTML | zh/en | Media/Alta | Sim | implementado (apenas comunicados publicos) |
| `china_avic` | Aviation Industry Corporation of China | http://en.avic.com/ | HTML | zh/en | Media | Sim | implementado (apenas comunicados publicos) |

## Roadmap (nao implementadas)

- `dsei_japan` - apenas mapeamento institucional; evento privado, sem feed publico.
- `pla_equipment_procurement` - so apos confirmacao de legalidade, robots.txt e escopo publico estrito.
- TED Tenders Daily (Asia chapters) - se for publicado feed dedicado.
- Agregadores academicos (J-STAGE, CNKI) - fora do escopo de oportunidades.
- Outros primes JP (Toshiba Energy Systems, Hitachi Energy/Power) e CN (CASC, CASIC, CSSC) - terceira onda.

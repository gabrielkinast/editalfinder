# Diagnostico de ruido — Onda A Credito/Desenvolvimento (Brasil)

**Data:** 2026-05-06 (UTC)

## Objetivo

Identificar paginas institucionais, atendimento, navegacao, conta/login e hubs de licitacao/noticia que foram capturadas como se fossem oportunidades de credito, para endurecer filtros **sem** alterar `opportunity_gate` global.

## Fontes

`bnb`, `banco_da_amazonia`, `bdmg`, `agerio`, `desenvolve_sp`

## Padroes observados (exemplos reais)

| Padrao | Exemplo |
|--------|---------|
| Hub investimento / contato disfarçado | BDMG titulo **Entre em contato** em `…/investimento` |
| Parceiros / correspondentes | **Correspondentes Bancários** → `sejaparceiro` |
| Institucional “sobre” | **Sobre o BDMG**, abas Atuação / LGPD / segurança |
| Carreiras | **Trabalhe no BDMG** |
| Imprensa | **Sala de Imprensa**, Notícias, Eventos |
| Licitações (fora do foco credito produto) | **Licitações e Contratos** em editais-venda-bens etc. |
| Documentação genérica | **Documentação BDMG** em `/documentos` |
| Idioma | **English** `/en` |
| Conta PJ | BASA **Conta PJ** `/empresas/conta-pj` |
| Educacao financeira | AgeRio `…/educacaofinanceira/` |

## Artefatos JSON

- `audit_reports_credito/lote_credito_brasil_onda_a_ruido_diagnostico.json` — lista completa (scan retroativo do standardized anterior em `…/onda_a_semantic_fix/standardized/`).
- `audit_reports_credito/lote_credito_brasil_onda_a_ruido_by_source.json` — agregado por fonte + contagens antes/depois da limpeza.
- `audit_reports_credito/lote_credito_brasil_onda_a_ruido_examples.json` — ate 4 exemplos por fonte.

## Implementacao tecnica (resumo)

- Novo modulo `CORE/credito_brasil_onda_a_noise.py`: regex de URL, titulos institucionais, titulos curtos de navegacao; funcao `credito_brasil_onda_a_ruido_motivo` usada no **transformer** (rejeicao local `onda_a_ruido_institucional:*`) e nos **crawlers**.
- Crawlers: exclusoes adicionais em `link_url_exclude_substrings` + `crawler_should_drop_item` pos-coleta.
- BDMG: removida listagem da **home** (`/`) para reduzir captura de rodape global.
- Transformer: `_credito_brasil_onda_a_soft_continue` endurecido (menos marcadores fracos tipo só “empresa”) e estendido a rejeicoes **Noticia ou pagina generica** para nao perder microcredito AgeRio; bloqueio explicito se `credito_brasil_onda_a_ruido_motivo` disser ruido.
- `taxonomy_filtros`: `perfil_ideal` limitado a 4 entradas; “empresa” só com evidencia de credito/micro/rural; limpeza de setor/perfil em URLs de ouvidoria/fale-conosco/etc. na AgeRio.

## Nota sobre descricao

Páginas válidas de **Linhas Permanentes Municipais** podem ainda mencionar “Internet Banking” ou “correspondentes” no **corpo** herdado do layout do site; o filtro atua sobre **URL e titulo** e sobre páginas cuja função é só serviço bancário ou institucional.

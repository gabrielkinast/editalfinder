# Modulo Defesa Industrial

## Relatorio tecnico inicial

- Arquitetura mantida: `main.py` orquestra crawlers por fonte, depois `CORE/transformer.py` e `CORE/loader.py`.
- Padrao preservado: uma pasta por fonte, `main_*.py`, JSON bruto em `outputs/*_editais.json`.
- Persistencia preservada: `loader.py` faz `upsert` no Supabase por `link` e salva extras sem quebrar compatibilidade.
- Deduplicacao preservada: chave principal por `link` no banco e chave composta no transformer.
- Tratamento de erro preservado: falha por fonte nao derruba pipeline global.

## Estrutura de classificacao em extras

Todos os novos crawlers passam a produzir:

```json
{
  "setor_estrategico": "defesa_industrial",
  "subtema": [],
  "tipo_oportunidade": "",
  "empresa_prime": "",
  "orgao_contratante": "",
  "pais": "",
  "nivel_sensibilidade": "publico_institucional",
  "origem": "",
  "palavras_chave_detectadas": []
}
```

## Fontes implementadas nesta fase

- `sam_gov`
- `dod_sbir_sttr`
- `grants_gov`
- `darpa_opportunities`
- `european_defence_fund`
- `nato_diana`
- `pncp_defesa`
- `compras_defesa`
- `lockheed_martin_suppliers`
- `bae_systems_suppliers`
- `general_dynamics_suppliers`
- `rheinmetall_suppliers`
- `thales_suppliers`

## Fontes em roadmap

- `ted_tenders_eu`
- `nato_innovation_fund`
- `uk_defence_sourcing`
- `boeing_suppliers`
- `northrop_grumman_suppliers`
- `leonardo_suppliers`
- `saab_suppliers`
- `elbit_suppliers`
- `rtx_suppliers`

## Cuidados de scraping responsavel

- User-Agent identificavel.
- Tentativa de respeito a `robots.txt` por fonte HTML.
- Delay entre requests e timeout configurado.
- API oficial priorizada quando disponivel.
- Sem bypass de login/captcha/paywall.

## Execucao

- Rodar um crawler isolado:
  - `python grants_gov/main_grants_gov.py`
  - `python pncp_defesa/main_pncp_defesa.py`
- Rodar pipeline completo:
  - `python main.py`

## Limitacoes conhecidas

- Alguns portais internacionais mudam layout e podem retornar 0 itens em certos dias.
- APIs podem exigir chave/limite por IP e retornar timeout.
- Portais de fornecedores privados podem expor pouco conteudo publico sem autenticacao.

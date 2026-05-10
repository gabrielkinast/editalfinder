# Checklist de baseline para crawlers internacionais

Este checklist consolida os padrões usados como referência nos crawlers maduros (`cnpq`, `fapergs`, `finep`) para orientar refatorações internacionais.

## Estrutura mínima por crawler
- `main.py` com `main()` executável de forma isolada.
- Funções separadas para listagem, detalhe, normalização e persistência de saída.
- Saída em `outputs/<fonte>_editais.json` com `ensure_ascii=False`.

## Robustez de requisição
- `Session` com retry/backoff para status transitórios.
- Timeout explícito por requisição.
- User-Agent identificável.
- Delay curto entre detalhes para reduzir agressividade.
- Respeito a `robots.txt` quando aplicável (com fail-open conservador).

## Extração e qualidade de dados
- Coleta em duas etapas: listagem -> detalhe.
- Paginação limitada por configuração (`MAX_PAGES`).
- Dedupe por link e por identificador específico da oportunidade.
- Normalização de datas para ISO quando confiável.
- Fallback seguro quando detalhe falha.

## Contrato de saída
- Campos base: `titulo`, `descricao`, `link`, `fonte`, `data_publicacao`, `fim_inscricao`, `situacao`, `valor`, `programa`, `acao`, `tipo_recurso`, `extras`.
- `extras` sempre como objeto (`dict`), nunca string/lista.
- Preservar idioma original e metadados de extração em `extras`.

## Compatibilidade com pipeline
- Não quebrar mapeamentos do `CORE/transformer.py`.
- Manter `link` válido (chave de upsert no loader).
- Nunca derrubar o pipeline inteiro por erro de uma fonte.

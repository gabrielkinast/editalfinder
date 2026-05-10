# Recomendações de deduplicação futura

- Não executar merge automático sem revisão humana dos grupos `precisa_revisao_manual`.
- Priorizar dedupe por `link`, `codigo_oportunidade`, `numero_processo` e `hash_deduplicacao` (alto sinal).
- Em `pdf_url`, tratar como revisão manual (documento compartilhado entre oportunidades é comum).
- Definir canônico pelo score composto: qualidade_dado + completude + atualizado_em.
- Mesclar `extras.documentos` por URL única e preservar arrays ricos sem sobrescrever por vazio.
- Guardar histórico de IDs mesclados em tabela auxiliar/auditoria antes de qualquer purge.

## SQLs seguros para inspeção manual

`-- Duplicatas por link`
`select link, count(*) as n from public.edital where link is not null and btrim(link) <> '' group by 1 having count(*) > 1 order by n desc;`
`-- Duplicatas por hash_deduplicacao`
`select hash_deduplicacao, count(*) as n from public.edital where hash_deduplicacao is not null and btrim(hash_deduplicacao) <> '' group by 1 having count(*) > 1 order by n desc;`
`-- Duplicatas por fonte + titulo normalizado`
`select lower(fonte_recurso) as fonte, lower(regexp_replace(titulo, '\s+', ' ', 'g')) as titulo_norm, count(*) as n from public.edital where titulo is not null and btrim(titulo) <> '' group by 1,2 having count(*) > 1 order by n desc;`
`-- Duplicatas por pdf_url`
`select pdf_url, count(*) as n from public.edital where pdf_url is not null and btrim(pdf_url) <> '' group by 1 having count(*) > 1 order by n desc;`
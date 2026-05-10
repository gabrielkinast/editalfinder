# Diagnóstico — suporte atual para `noticia` e `pesquisa`

## Respostas diretas

1. **O backend já consegue gravar notícia?**  
   Sim. `upsert_routed_item()` roteia para `noticia` e usa `inserir_ou_atualizar_conteudo(..., on_conflict="link")`.

2. **O backend já consegue gravar pesquisa?**  
   Sim. Mesmo fluxo de roteamento para `pesquisa`, também com upsert por `link`.

3. **Quais campos existem?**  
   Pelas migrations atuais (`20260504_create_noticia_pesquisa_tables.sql`), ambas têm: `titulo`, `resumo`, `link`, `fonte`, `data_publicacao`, `pais`, `orgao`, arrays (`setor_estrategico`, `area_cientifica`, `area_tecnologica`, `tags`), `url_documento`, `content_type`, `extras`, `hash_deduplicacao`, `ultima_coleta`, `criado_em`, `atualizado_em`.

4. **Quais campos faltam?**  
   Para o objetivo de módulo de notícias/pesquisas, faltam apenas campos opcionais de conveniência (ex.: `noticia.conteudo`, `noticia.imagem_url`, `pesquisa.tipo_pesquisa`), mas **não faltam campos críticos** para roteamento básico.

5. **O que o loader espera?**  
   - `destination_table_for_item()` define `edital`/`noticia`/`pesquisa`;  
   - `map_to_content_schema()` monta payload enxuto;  
   - `inserir_ou_atualizar_conteudo()` faz upsert por `link` em `public.noticia`/`public.pesquisa`.

6. **`science_scraper` deve migrar para notícia?**  
   Sim, **parcialmente**: conteúdos informativos e releases devem ir para `noticia`; relatórios e publicações técnicas para `pesquisa`; oportunidades acionáveis continuam em `edital`.

7. **Quais ajustes antes de apply?**  
   - crawler dedicado e seguro por fonte;  
   - auditoria de classificação (`noticia` vs `pesquisa`);  
   - limites por fonte + janela de 12 meses;  
   - somente após validação, ativar escrita em staging.

## Diagnóstico técnico

- `content_routing.py` já contém heurística de `infer_content_type` e `destination_table_for_item`.
- `map_to_content_schema()` já normaliza arrays (`text[]`) para evitar erro de array literal.
- `upsert_routed_item()` já separa o fluxo de `edital` vs `noticia/pesquisa`.
- O suporte de banco para `noticia/pesquisa` existe nas migrations do projeto.


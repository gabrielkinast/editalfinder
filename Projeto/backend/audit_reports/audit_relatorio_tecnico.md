# Relatório técnico de auditoria (dry-run)

Gerado: `2026-05-01T05:58:38Z` · Amostra: até **25** itens por ficheiro · PDF: **off**.

## 1. Resumo executivo
- **95** ficheiros JSON processados; **961** itens na amostra.
- **88** ficheiros tinham itens brutos na amostra.
- Distribuição heurística de maturidade: {'maduro': 11, 'bom': 14, 'quebrado': 46, 'ruidoso': 3, 'não testado': 7, 'parcial': 11, 'fraco': 3}.
- O `opportunity_gate` e regras de relevância excluem muitas URLs institucionais/PDFs sem texto — várias fontes ficam com **0 aceites** na amostra (ver secção 8 e `audit_by_source.json`).

## 2. Quantidade de fontes testadas
95

## 3. Quantidade de itens analisados
961

## 4. Principais bugs / causas de rejeição (agregado)

| Motivo (rejection_reason) | Contagem na amostra |
|---------------------------|---------------------|
| Pagina de login ou autenticacao | 242 |
| Relevancia limite: poucos sinais de oportunidade | 165 |
| Pontuacao abaixo do minimo (oportunidade nao evidenciada) | 161 |
| titulo_ruido_exato | 11 |
| noticia_sem_oportunidade | 9 |
| Acesso restrito (IP/campus/intranet) | 1 |

## 5. Principais ruídos
- Títulos de lista negra **no bruto** contam-se por ficheiro; exemplos que **passaram** o transformer: **0** (ficheiro `audit_noise_examples.json`).

## 6. Campos mais vazios (só itens transformados)

- **tipo_oportunidade**: score acumulado 4200
- **area**: score acumulado 4200
- **publico_alvo**: score acumulado 4200
- **perfil_ideal**: score acumulado 4200
- **setor_economico**: score acumulado 4200
- **area_cientifica**: score acumulado 4200
- **area_tecnologica**: score acumulado 4200
- **setor_estrategico**: score acumulado 4200
- **fim_inscricao**: score acumulado 3772
- **valor**: score acumulado 3748
- **data_publicacao**: score acumulado 2656
- **pdf_url**: score acumulado 2170

## 7. Dados perdidos no transformer
- Exemplos: **0** em `audit_data_loss_examples.json`.

## 8. Dados perdidos no loader
- Simulação: `map_to_db_schema` + `_strip_payload`; ver `audit_loader_payload.json` (chaves após strip vs extras fora do strip em modo legado).

## 9. Duplicidade
- Por ficheiro: contagem de links repetidos no bruto e nos aceites — `audit_duplicates.json`.

## 10. Classificação
- Flags heurísticas (ex.: crédito sem tipo): **0** exemplos em `audit_classification_issues.json`.

## 11. perfil_ideal
- **1** exemplos em `audit_profile_issues.json`.

## 12. Datas
- **1** flags em `audit_by_source.json` (por fonte) + agregado nos exemplos.

## 13. Valores
- **0** exemplos de valor bruto sem valor transformado.

## 14. PDF / documentos
- Nesta corrida os PDFs **não foram baixados** (`pdf_skip`); percentagens de `pdf_url` nos aceites reflectem só metadados do crawler + extras.

## 15. Performance
- Tempos por ficheiro: `audit_performance.json`.

## 16. Score / relevância legado
- Ficheiros Python com ocorrências: **28** — detalhe em `audit_score_legacy.json`.

## 17. Status por crawler (amostra)
- **Maduro** (exemplos): abdi, china_caea, china_cas, china_tendering_bidding, fapesp, japan_atla, japan_ihi, japan_jetro_procurement, japan_kakenhi, japan_nims, japan_riken
- **Ruidoso**: apex, fapemig, japan_aist
- **Quebrado** (0 aceites ou erro): 46 fontes — primeiras: amazul, ambev, aneel, anp, badesul, bndes, brde, caixa, capes, cbpf, china_avic, china_cnnc, china_norinco, cnen, cnpq, compras_defesa, confap, dcta_ita_iae, defesa, doe_arpae

## 18. Top 10 correções mais importantes
1. Rever falsos positivos do **opportunity_gate** (login em páginas gov.br reais de editais).
2. Separar **PDF só como documento** vs página de oportunidade no gate.
3. Afinar **relevância mínima** para BNDES/BRDE/Caixa/Badesul (muitas exclusões na amostra).
4. Melhorar **tipo_recurso** para linhas de crédito.
5. Preencher **perfil_ideal** nas fontes estratégicas.
6. Reduzir **campos vazios** nas fontes no topo de `audit_empty_fields.json`.
7. **Deduplicação** por link dentro do mesmo JSON de crawler.
8. Preservar **pdf_url** quando presente no bruto.
9. Auditoria com **PDF on** apenas num subconjunto controlado.
10. Documentar **fontes com_zero_aceites** como risco de gate vs risco de crawler.

## 19. Correções rápidas
- Ajustar listas de ruído / títulos genéricos no crawler ou em `noise_filter` com base em `audit_noise_examples.json`.

## 20. Correções médias
- Refinar `opportunity_gate` por domínio (gov.br, bndes.gov.br, etc.).

## 21. Correções grandes
- Separar pipeline **crawl → normalização mínima → gate pesado opcional**.

## 22. Próximas etapas
- Correr amostra maior (`--max-items 100`) em subset de fontes críticas.
- Correr subconjunto com `--no-skip-pdf` em staging.
- Validar matriz completa em `audit_matrix_crawlers.json`.

---
*Maturidade é heurística sobre a amostra; não substitui revisão humana dos JSONs.*
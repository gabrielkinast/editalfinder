# Dry-run — Recovery global de classificação de setores

- **Gerado (UTC):** 2026-05-13T01:09:49.972180+00:00
- **Corpus:** `audit_reports_retransform/standardized` (standardized local, sem Supabase)

## Totais

| chave | valor |
| --- | ---: |
| Editais analisados | 1294 |
| Mudariam `setor_estrategico` | 1114 |
| Perderiam `defesa_industrial` | 591 |
| Perderiam `aeroespacial` | 304 |
| Perderiam `cyber_defesa` (só em `setor_estrategico`) | 0 |
| Ficariam sem `setor_estrategico` | 920 |
| … desses, já vazios antes do enrich | 130 |
| … desses, tinham slugs antes e esvaziam | 790 |

**Nota `cyber_defesa`:** Contagem só em extras.setor_estrategico. Neste corpus, cyber_defesa aparece sobretudo em area_tecnologica/subtema, não na lista de setor estratégico — por isso perda em setor pode ser 0.

## Interpretação rápida (sanidade militar)

- **DoD SBIR/STTR** e **NUCLEP**: no snapshot, todos os itens da família mantêm pelo menos um slug *defense-like* após o enrich — alinhado ao esperado.
- **IARPA** / **DARPA** (e parte do **Grants.gov** agregado): muitos títulos/descrições estão em inglês com agências militares sem bater nas frases actuais de `THEMATIC_PATTERNS` (acento PT + listas focadas em PT). O enrich taxonómico pode **esvaziar** ou **reduzir** `setor_estrategico`; para cargas curadas, usar **`setor_estrategico_crawler_locked`** ou alargar padrões noutra PR.
- **ESA OSIP / AMAZUL**: ver contagens na tabela abaixo; `aeroespacial` depende de evidência orbital/espacial no texto.

## Top fontes mais afetadas (por nº de linhas com alteração)

- **Grants.gov**: 127
- **Fundação Araucária**: 88
- **China International Tendering (MOFCOM)**: 74
- **JSPS**: 40
- **European Defence Fund**: 39
- **CAS**: 34
- **NSFC**: 29
- **ANEEL**: 27
- **KAKENHI**: 26
- **PNCP Defesa**: 22
- **SENAI**: 22
- **EMBRAPII**: 21
- **KEK**: 21
- **NUCLEP**: 20
- **PLATAFORMA_INDUSTRIA**: 20
- **BNB**: 19
- **BNDES**: 19
- **Japan MOD**: 19
- **PNCP**: 19
- **MOST China**: 16

## Sanidade — fontes militares / defesa (evidência textual heurística)

### amazul
| chave | valor |
| --- | ---: |
| linhas | 19 |
| com_defense_like_depois | 5 |
| regressao_militar | 0 |

### darpa
| chave | valor |
| --- | ---: |
| linhas | 15 |
| com_defense_like_depois | 1 |
| regressao_militar | 9 |

### dod_sbir_sttr
| chave | valor |
| --- | ---: |
| linhas | 15 |
| com_defense_like_depois | 15 |
| regressao_militar | 0 |

### esa_osip
| chave | valor |
| --- | ---: |
| linhas | 17 |
| com_defense_like_depois | 3 |
| regressao_militar | 0 |

### iarpa
| chave | valor |
| --- | ---: |
| linhas | 8 |
| com_defense_like_depois | 0 |
| regressao_militar | 8 |

### nuclep
| chave | valor |
| --- | ---: |
| linhas | 20 |
| com_defense_like_depois | 20 |
| regressao_militar | 0 |

## Correções claramente boas (amostra)

1. **AFWERX** — SBIR/STTR Overview
   - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `['defesa']`

2. **AFWERX** — Open Topic
   - antes: `['defesa_industrial', 'aeroespacial', 'defesa', 'dual_use']` → depois: `['defesa', 'dual_use']`

3. **AFWERX** — Specific Topic
   - antes: `['defesa_industrial', 'aeroespacial', 'defesa', 'dual_use']` → depois: `['defesa', 'dual_use']`

4. **AFWERX** — STRATFI/TACFI
   - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `['defesa']`

5. **AFWERX** — Phase III
   - antes: `['defesa_industrial', 'defesa']` → depois: `['defesa']`

6. **AFWERX** — Risk-Based Analysis
   - antes: `['defesa_industrial', 'defesa']` → depois: `['defesa']`

7. **AFWERX** — Augmentee Program
   - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `['defesa']`

8. **AFWERX** — SAGE Fellowship Program
   - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `['defesa']`

9. **ANEEL** — ANEEL - adsp2024778 2
   - antes: `['defesa_industrial']` → depois: `[]`

10. **ANEEL** — ANEEL - Call for Projects H2 PDI
   - antes: `['defesa_industrial']` → depois: `[]`

11. **ANEEL** — Sistemas de Armazenamento de Energia
   - antes: `['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia', 'energia']` → depois: `['ciencia_tecnologia', 'energia']`

12. **ANEEL** — Chamadas de Projetos de PDI Estratégicos
   - antes: `['defesa_industrial', 'aeroespacial', 'energia']` → depois: `['energia']`

13. **ANEEL** — Guia de Avaliação da Maturidade Tecnológica da ANEEL
   - antes: `['defesa_industrial', 'ciencia_tecnologia']` → depois: `['aeroespacial', 'ciencia_tecnologia']`

14. **ANEEL** — Guia de Comunicação dos Programas de PDI e EE ANEEL
   - antes: `['defesa_industrial', 'energia']` → depois: `['energia']`

15. **ANEEL** — Prêmio ANEEL de Inovação
   - antes: `['defesa_industrial', 'energia']` → depois: `['energia']`

16. **ANEEL** — PDI ANEEL
   - antes: `['defesa_industrial']` → depois: `[]`

17. **ANEEL** — Sandboxes Tarifários
   - antes: `['defesa_industrial']` → depois: `[]`

18. **ANEEL** — Temas Estratégicos do PEQuI
   - antes: `['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia', 'energia']` → depois: `['ciencia_tecnologia', 'energia']`

19. **ANEEL** — Planejamento de Tecnologia da Informação
   - antes: `['defesa_industrial', 'aeroespacial']` → depois: `[]`

20. **ANEEL** — Programa de Eficiência Energética
   - antes: `['defesa_industrial', 'aeroespacial', 'energia']` → depois: `['energia']`

21. **ANEEL** — Programa de Pesquisa, Desenvolvimento e Inovação (PDI)
   - antes: `['defesa_industrial', 'energia']` → depois: `['energia']`

22. **ANEEL** — Programas Setoriais
   - antes: `['defesa_industrial', 'energia']` → depois: `['energia']`

23. **ANEEL** — Plano de Desenvolvimento da Distribuição
   - antes: `['defesa_industrial']` → depois: `[]`

24. **ANEEL** — Programa de Pesquisa, Desenvolvimento e Inovação da ANEEL
   - antes: `['defesa_industrial']` → depois: `[]`

25. **ANEEL** — PDI ANEEL
   - antes: `['defesa_industrial']` → depois: `[]`

26. **ANEEL** — Pesquisa e Desenvolvimento e Eficiência Energética
   - antes: `['defesa_industrial', 'energia']` → depois: `['energia']`

27. **ANEEL** — PDI ANEEL
   - antes: `['defesa_industrial']` → depois: `[]`

28. **ANEEL** — Procedimentos dos Programas de Eficiência Energética e de Pesquisa e Desenvolvimento
   - antes: `['defesa_industrial', 'energia']` → depois: `['energia']`

29. **ANEEL** — Revista de Pesquisa e Desenvolvimento (P&D)
   - antes: `['defesa_industrial', 'ciencia_tecnologia', 'energia']` → depois: `['ciencia_tecnologia', 'energia']`

30. **ANEEL** — Pesquisa e Desenvolvimento e Eficiência Energética
   - antes: `['defesa_industrial', 'ciencia_tecnologia', 'energia']` → depois: `['ciencia_tecnologia', 'energia']`

31. **ANEEL** — 1ª Chamada Pública
   - antes: `['defesa_industrial', 'energia']` → depois: `['energia']`

32. **ANEEL** — 2ª Chamada Pública
   - antes: `['defesa_industrial', 'energia']` → depois: `['energia']`

33. **ANEEL** — Demais Projetos
   - antes: `['defesa_industrial', 'energia']` → depois: `['energia']`

34. **ANEEL** — Desenvolvimento, cuidados e educação pré-escolar
   - antes: `['defesa_industrial']` → depois: `[]`

35. **ANEEL** — ANEEL - dd projetos de pd em energia eletrica
   - antes: `['defesa_industrial', 'energia']` → depois: `['energia']`

36. **ANP** — Edital de Chamada Pública
   - antes: `['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia']` → depois: `['ciencia_tecnologia']`

37. **ANP** — Consultas e Audiências Públicas
   - antes: `['defesa_industrial']` → depois: `[]`

38. **Apex Brasil** — licitações e contratos
   - antes: `['aeroespacial']` → depois: `[]`

39. **BADESUL** — Badesul divulga projetos contemplados
   - antes: `['defesa_industrial']` → depois: `[]`

40. **BADESUL** — Lista de entidades inscritas
   - antes: `['defesa_industrial', 'aeroespacial']` → depois: `[]`

## Casos duvidosos (amostra)

1. **AMAZUL** — Dispensa de Licitação 05/2024
   - antes: `['nuclear', 'defesa']` → depois: `['defesa', 'nuclear', 'aeroespacial']`

2. **BASA** — Crédito e financiamento
   - antes: `['agro']` → depois: `[]`

3. **BASA** — PRONAF
   - antes: `['agro']` → depois: `[]`

4. **BASA** — Plano Safra
   - antes: `['agro']` → depois: `[]`

5. **BASA** — Fundo da Marinha Mercante
   - antes: `[]` → depois: `['defesa']`

6. **BASA** — Giro Produtor Rural
   - antes: `['agro']` → depois: `[]`

7. **BASA** — Giro Produtor Rural
   - antes: `['agro']` → depois: `[]`

8. **BASA** — Máquinas e Equipamentos
   - antes: `['agro']` → depois: `[]`

9. **BASA** — Financiamento de Veículo Produtor Rural
   - antes: `['agro']` → depois: `[]`

10. **BASA** — Renegociação de Dívidas
   - antes: `['agro']` → depois: `[]`

11. **BASA** — PRONAF A
   - antes: `['agro']` → depois: `[]`

12. **BASA** — Programa Nacional de Fortalecimento da Agricultura Familiar
   - antes: `['agro']` → depois: `[]`

13. **BDMG** — Se é novo para sua empresa, é inovação para o BDMG.
   - antes: `['inovacao', 'industria']` → depois: `[]`

14. **BDMG** — Agronegócio Para empresas e cooperativas que exercem as mais diversas atividades ligadas à agropecuária.
   - antes: `['agro', 'sustentabilidade']` → depois: `[]`

15. **BDMG** — Não apenas prover o crédito, mas mensurar o seu impacto
   - antes: `['sustentabilidade']` → depois: `[]`

16. **BDMG** — Linhas Permanentes de Financiamento Municipal
   - antes: `['sustentabilidade']` → depois: `[]`

17. **BDMG** — Linhas Permanentes de Financiamento Municipal
   - antes: `['sustentabilidade']` → depois: `[]`

18. **BDMG** — Linhas Permanentes de Financiamento Municipal
   - antes: `['sustentabilidade']` → depois: `[]`

19. **BDMG** — Linhas Permanentes de Financiamento Municipal
   - antes: `['sustentabilidade']` → depois: `[]`

20. **BNB** — Microcrédito – soluções para pequenos negócios – Banco do Nordeste
   - antes: `['agro']` → depois: `[]`

21. **BNB** — Empréstimos e Financiamentos - Soluções para você - Banco do Nordeste
   - antes: `['energia', 'sustentabilidade', 'inovacao']` → depois: `['energia']`

22. **BNB** — Micro e Pequenas Empresas - Crédito e soluções para o seu negócio - Banco do Nordeste
   - antes: `[]` → depois: `['energia']`

23. **BNB** — Miniprodutor Rural – crédito e soluções para o campo – Banco do Nordeste
   - antes: `['agro']` → depois: `[]`

24. **BNB** — Crédito para Poder Público – financiamento de projetos – Banco do Nordeste
   - antes: `['sustentabilidade', 'industria', 'desenvolvimento_regional']` → depois: `[]`

25. **BNB** — Publicações para Agricultura Familiar - Setor Rural - Produtos e Serviços
   - antes: `['agro']` → depois: `[]`

26. **BNB** — Agricultura Familiar – atividades financiadas – Banco do Nordeste
   - antes: `['agro', 'inovacao']` → depois: `[]`

27. **BNB** — Apicultura – atividades financiadas – Banco do Nordeste
   - antes: `['agro']` → depois: `[]`

28. **BNB** — Bovinocultura – atividades financiadas – Banco do Nordeste
   - antes: `['agro', 'sustentabilidade', 'inovacao']` → depois: `[]`

29. **BNB** — Carcinicultura – atividades financiadas – Banco do Nordeste
   - antes: `['agro', 'sustentabilidade', 'industria']` → depois: `['defesa']`

30. **BNB** — Educação – atividades financiadas – Banco do Nordeste
   - antes: `['inovacao']` → depois: `['energia']`

31. **BNB** — Floricultura - Atividades Financiadas - Banco do Nordeste
   - antes: `['agro']` → depois: `[]`

32. **BNB** — Fruticultura – atividades financiadas – Banco do Nordeste
   - antes: `['agro', 'industria']` → depois: `[]`

33. **BNB** — Grãos – atividades financiadas – Banco do Nordeste
   - antes: `['agro', 'industria']` → depois: `[]`

34. **BNB** — Industrial – atividades financiadas – Banco do Nordeste
   - antes: `['inovacao', 'industria']` → depois: `['industria']`

35. **BNB** — Meio Ambiente – atividades financiadas – Banco do Nordeste
   - antes: `['agro', 'sustentabilidade', 'inovacao']` → depois: `[]`

36. **BNB** — Ovinocaprinocultura – atividades financiadas – Banco do Nordeste
   - antes: `['agro', 'industria']` → depois: `[]`

37. **BNB** — Pesca – atividades financiadas – Banco do Nordeste
   - antes: `['agro', 'industria']` → depois: `[]`

38. **BNB** — Piscicultura – atividades financiadas – Banco do Nordeste
   - antes: `['agro', 'industria']` → depois: `[]`

39. **CAEA** — CNNC and NASA sign EPC contract for building an HPR1000 unit in Argentina
   - antes: `['nuclear']` → depois: `['aeroespacial', 'nuclear']`

40. **CAS** — 科研进展
   - antes: `['ciencia_tecnologia']` → depois: `[]`

## Lock de crawler recomendado (amostra)

1. **DARPA Opportunities** (military_family_evidence_loss) — Offices
   - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `[]`

2. **DARPA Opportunities** (military_family_evidence_loss) — Contracts Management Office
   - antes: `['defesa_industrial', 'aeroespacial']` → depois: `[]`

3. **DARPA Opportunities** (military_family_evidence_loss) — Academia
   - antes: `['defesa_industrial']` → depois: `[]`

4. **DARPA Opportunities** (military_family_evidence_loss) — Industry
   - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `[]`

5. **DARPA Opportunities** (military_family_evidence_loss) — Small Business
   - antes: `['defesa_industrial', 'aeroespacial']` → depois: `[]`

6. **DARPA Opportunities** (military_family_evidence_loss) — Ideas Under Incubation
   - antes: `['defesa_industrial', 'aeroespacial']` → depois: `[]`

7. **DARPA Opportunities** (military_family_evidence_loss) — About DARPA
   - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `[]`

8. **DARPA Opportunities** (military_family_evidence_loss) — Defense Sciences Office
   - antes: `['defesa_industrial', 'aeroespacial', 'defesa']` → depois: `[]`

9. **DARPA Opportunities** (military_family_evidence_loss) — Usage Policy
   - antes: `['defesa_industrial']` → depois: `[]`

10. **IARPA** (military_family_evidence_loss) — Targeted Evaluation of Ionizing Radiation Exposure (TEI-REX)
   - antes: `['defesa_industrial', 'inteligencia', 'pesquisa_avancada']` → depois: `[]`

11. **IARPA** (military_family_evidence_loss) — IARPA Advanced Materials and Fabrication for Coherent Superconducting Qubits Program
   - antes: `['defesa_industrial', 'inteligencia', 'pesquisa_avancada']` → depois: `[]`

12. **IARPA** (military_family_evidence_loss) — Advanced Materials and Fabrication for Coherent Superconducting Qubits -
   - antes: `['defesa_industrial', 'inteligencia', 'pesquisa_avancada']` → depois: `[]`

13. **IARPA** (military_family_evidence_loss) — SuperCables
   - antes: `['defesa_industrial', 'inteligencia', 'pesquisa_avancada']` → depois: `[]`

14. **IARPA** (military_family_evidence_loss) — TrojAI
   - antes: `['defesa_industrial', 'inteligencia', 'pesquisa_avancada']` → depois: `[]`

15. **IARPA** (military_family_evidence_loss) — BROAD AGENCY ANNOUNCEMENT FOR Entangled Logical Qubits (ELQ)
   - antes: `['defesa_industrial', 'inteligencia', 'pesquisa_avancada']` → depois: `[]`

16. **IARPA** (military_family_evidence_loss) — Intelligence Community Centers For Academic Excellence
   - antes: `['defesa_industrial', 'inteligencia', 'pesquisa_avancada']` → depois: `[]`

17. **IARPA** (military_family_evidence_loss) — Intelligence Community Centers for Academic Excellence
   - antes: `['defesa_industrial', 'inteligencia', 'pesquisa_avancada']` → depois: `[]`

---
Métricas derivadas de `enrich_opportunity_classification` + taxonomia corrente. **Não** constitui apply em base de dados.
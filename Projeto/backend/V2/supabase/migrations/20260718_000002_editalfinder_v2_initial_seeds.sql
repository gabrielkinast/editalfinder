-- EditalFinder V2 — minimal staging seeds.
-- Stable UUIDs are explicit. Conflicts by codigo preserve later editorial changes.

begin;

insert into public.tipo_oportunidade (
    id, codigo, nome, descricao, ativo, ordem_exibicao
) values
    (
        '10000000-0000-4000-8000-000000000001',
        'chamada_publica',
        'Chamada pública',
        'Convocação pública para apresentação de propostas, projetos ou manifestações de interesse.',
        true,
        10
    ),
    (
        '10000000-0000-4000-8000-000000000002',
        'edital',
        'Edital',
        'Instrumento formal com regras, requisitos e procedimento de seleção definidos.',
        true,
        20
    ),
    (
        '10000000-0000-4000-8000-000000000003',
        'bolsa',
        'Bolsa',
        'Processo seletivo cujo objeto principal é a concessão de bolsa a pessoa elegível.',
        true,
        30
    ),
    (
        '10000000-0000-4000-8000-000000000004',
        'premio',
        'Prêmio',
        'Seleção competitiva destinada ao reconhecimento de trabalhos, iniciativas ou resultados.',
        true,
        40
    ),
    (
        '10000000-0000-4000-8000-000000000005',
        'concurso',
        'Concurso',
        'Seleção competitiva de propostas, soluções ou candidatos segundo critérios publicados.',
        true,
        50
    ),
    (
        '10000000-0000-4000-8000-000000000006',
        'credenciamento',
        'Credenciamento',
        'Procedimento para habilitar interessados que cumpram requisitos previamente definidos.',
        true,
        60
    ),
    (
        '10000000-0000-4000-8000-000000000007',
        'encomenda_tecnologica',
        'Encomenda tecnológica',
        'Instrumento orientado à contratação de pesquisa, desenvolvimento ou solução tecnológica específica.',
        true,
        70
    ),
    (
        '10000000-0000-4000-8000-000000000008',
        'outra',
        'Outra',
        'Oportunidade válida que não se enquadra nas categorias iniciais após classificação explícita.',
        true,
        80
    )
on conflict (codigo) do nothing;

insert into public.tipo_recurso (
    id, codigo, nome, descricao, ativo, ordem_exibicao
) values
    (
        '20000000-0000-4000-8000-000000000001',
        'financiamento_nao_reembolsavel',
        'Financiamento não reembolsável',
        'Recurso financeiro que, cumpridas as condições, não exige restituição pelo beneficiário.',
        true,
        10
    ),
    (
        '20000000-0000-4000-8000-000000000002',
        'financiamento_reembolsavel',
        'Financiamento reembolsável',
        'Recurso financeiro sujeito a restituição segundo condições contratuais.',
        true,
        20
    ),
    (
        '20000000-0000-4000-8000-000000000003',
        'bolsa',
        'Bolsa',
        'Auxílio financeiro periódico ou definido para formação, pesquisa ou atuação elegível.',
        true,
        30
    ),
    (
        '20000000-0000-4000-8000-000000000004',
        'premio_financeiro',
        'Prêmio financeiro',
        'Recompensa monetária concedida por seleção ou reconhecimento.',
        true,
        40
    ),
    (
        '20000000-0000-4000-8000-000000000005',
        'credito',
        'Crédito',
        'Linha de crédito ou instrumento financeiro com condições próprias de contratação.',
        true,
        50
    ),
    (
        '20000000-0000-4000-8000-000000000006',
        'apoio_nao_financeiro',
        'Apoio não financeiro',
        'Acesso a mentoria, infraestrutura, capacitação, rede ou serviço sem repasse financeiro principal.',
        true,
        60
    ),
    (
        '20000000-0000-4000-8000-000000000007',
        'contratacao',
        'Contratação',
        'Contrapartida decorrente da contratação de serviço, solução, pesquisa ou desenvolvimento.',
        true,
        70
    ),
    (
        '20000000-0000-4000-8000-000000000008',
        'misto',
        'Misto',
        'Combinação explícita de duas ou mais modalidades de recurso.',
        true,
        80
    ),
    (
        '20000000-0000-4000-8000-000000000009',
        'nao_identificado',
        'Não identificado',
        'A fonte não oferece evidência suficiente para classificar o recurso sem inventar informação.',
        true,
        90
    )
on conflict (codigo) do nothing;

insert into public.area (
    id, codigo, nome, descricao, ativo, ordem_exibicao
) values
    (
        '30000000-0000-4000-8000-000000000001',
        'multidisciplinar',
        'Multidisciplinar',
        'Oportunidade que integra de forma explícita várias áreas; não deve ser usada como fallback automático.',
        true,
        10
    ),
    (
        '30000000-0000-4000-8000-000000000002',
        'ciencias_exatas_e_da_terra',
        'Ciências exatas e da Terra',
        'Matemática, física, química, geociências e campos amplos correlatos.',
        true,
        20
    ),
    (
        '30000000-0000-4000-8000-000000000003',
        'engenharias',
        'Engenharias',
        'Engenharias e desenvolvimento de sistemas, processos, infraestrutura e produtos.',
        true,
        30
    ),
    (
        '30000000-0000-4000-8000-000000000004',
        'ciencias_biologicas',
        'Ciências biológicas',
        'Biologia, biodiversidade, biotecnologia e ciências da vida não clínicas.',
        true,
        40
    ),
    (
        '30000000-0000-4000-8000-000000000005',
        'ciencias_da_saude',
        'Ciências da saúde',
        'Saúde humana, saúde coletiva, medicina e áreas clínicas correlatas.',
        true,
        50
    ),
    (
        '30000000-0000-4000-8000-000000000006',
        'ciencias_agrarias',
        'Ciências agrárias',
        'Agricultura, pecuária, alimentos, florestas e sistemas produtivos rurais.',
        true,
        60
    ),
    (
        '30000000-0000-4000-8000-000000000007',
        'ciencias_sociais_aplicadas',
        'Ciências sociais aplicadas',
        'Administração, economia, direito, comunicação, planejamento e campos aplicados correlatos.',
        true,
        70
    ),
    (
        '30000000-0000-4000-8000-000000000008',
        'ciencias_humanas',
        'Ciências humanas',
        'Educação, filosofia, história, sociologia, antropologia e campos correlatos.',
        true,
        80
    ),
    (
        '30000000-0000-4000-8000-000000000009',
        'linguistica_letras_e_artes',
        'Linguística, letras e artes',
        'Linguagens, literatura, artes e produção cultural.',
        true,
        90
    ),
    (
        '30000000-0000-4000-8000-000000000010',
        'tecnologia_e_inovacao',
        'Tecnologia e inovação',
        'Desenvolvimento tecnológico, inovação, transferência e empreendedorismo inovador.',
        true,
        100
    ),
    (
        '30000000-0000-4000-8000-000000000011',
        'energia',
        'Energia',
        'Geração, armazenamento, eficiência, redes e transição energética.',
        true,
        110
    ),
    (
        '30000000-0000-4000-8000-000000000012',
        'meio_ambiente',
        'Meio ambiente',
        'Clima, conservação, sustentabilidade, recursos naturais e controle ambiental.',
        true,
        120
    ),
    (
        '30000000-0000-4000-8000-000000000013',
        'defesa_e_aeroespacial',
        'Defesa e aeroespacial',
        'Defesa, segurança estratégica, espaço, aeronáutica e tecnologias associadas.',
        true,
        130
    ),
    (
        '30000000-0000-4000-8000-000000000014',
        'materiais',
        'Materiais',
        'Pesquisa, desenvolvimento, caracterização e aplicação de materiais.',
        true,
        140
    ),
    (
        '30000000-0000-4000-8000-000000000015',
        'computacao_e_dados',
        'Computação e dados',
        'Computação, software, inteligência artificial, dados e infraestrutura digital.',
        true,
        150
    )
on conflict (codigo) do nothing;

insert into public.fonte (
    id, codigo, nome, url_base, status_integracao
) values
    (
        '40000000-0000-4000-8000-000000000001',
        'fapergs',
        'FAPERGS',
        'https://fapergs.rs.gov.br',
        'piloto'
    ),
    (
        '40000000-0000-4000-8000-000000000002',
        'fapesp',
        'FAPESP',
        'https://fapesp.br',
        'piloto'
    ),
    (
        '40000000-0000-4000-8000-000000000003',
        'cnpq',
        'CNPq',
        'https://www.gov.br/cnpq/pt-br',
        'piloto'
    ),
    (
        '40000000-0000-4000-8000-000000000004',
        'finep',
        'Finep',
        'https://www.finep.gov.br',
        'piloto'
    ),
    (
        '40000000-0000-4000-8000-000000000005',
        'bndes',
        'BNDES',
        'https://www.bndes.gov.br',
        'piloto'
    ),
    (
        '40000000-0000-4000-8000-000000000006',
        'grants_gov',
        'Grants.gov',
        'https://www.grants.gov',
        'piloto'
    ),
    (
        '40000000-0000-4000-8000-000000000007',
        'nsf',
        'NSF',
        'https://www.nsf.gov',
        'piloto'
    ),
    (
        '40000000-0000-4000-8000-000000000008',
        'arpa_e',
        'ARPA-E',
        'https://arpa-e.energy.gov',
        'piloto'
    ),
    (
        '40000000-0000-4000-8000-000000000009',
        'horizon_europe',
        'Horizon Europe',
        'https://research-and-innovation.ec.europa.eu/funding/funding-opportunities/funding-programmes-and-open-calls/horizon-europe_en',
        'piloto'
    ),
    (
        '40000000-0000-4000-8000-000000000010',
        'erc',
        'European Research Council (ERC)',
        'https://erc.europa.eu',
        'piloto'
    )
on conflict (codigo) do nothing;

commit;

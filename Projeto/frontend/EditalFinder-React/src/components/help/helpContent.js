/**
 * Conteúdo do tutorial / ajuda do EditalFinder.
 * Edite aqui para atualizar textos sem alterar componentes.
 */

export const HELP_STORAGE_KEY = 'editalfinder_help_seen';

/** @typedef {{ id: string; title: string; group: string; objective?: string; whenToUse?: string; steps?: string[]; tips?: string[]; commonErrors?: string[]; blocks?: { title: string; body: string }[]; extra?: string }} HelpSection */

/** @type {HelpSection[]} */
export const HELP_SECTIONS = [
  {
    id: 'getting-started',
    title: 'Como começar',
    group: 'Começando',
    objective: 'Primeiros passos no EditalFinder.',
    steps: [
      'Entre no sistema com seu usuário e senha.',
      'Use o menu ☰ (canto superior esquerdo) para acessar as páginas.',
      'Comece pelo Dashboard para ver o resumo geral.',
      'Use Editais para procurar oportunidades.',
      'Use Cadastros para manter os dados dos clientes.',
      'Use Radar para comparar clientes com oportunidades.',
      'Use Workspace do Consultor para organizar o trabalho de consultoria.',
      'Se algo der errado, clique em Ajuda ou em Reportar problema.',
    ],
    tips: [
      'Você não precisa usar todas as páginas no mesmo dia. Comece pelo Dashboard e pelos Editais.',
    ],
  },
  {
    id: 'menu',
    title: 'Menu principal',
    group: 'Começando',
    objective: 'O botão ☰ abre o menu com todas as áreas do sistema.',
    steps: [
      'Dashboard — resumo e prioridades.',
      'Editais — todas as oportunidades.',
      'Cadastros — clientes e usuários (conforme sua permissão).',
      'Radar — cruza clientes com editais compatíveis.',
      'Workspace do Consultor — atendimento organizado por cliente.',
      'Notícias e Pesquisas — contexto e referências.',
      'Portais — links para fontes externas úteis.',
      'Ajuda — este tutorial.',
      'Reportar problema — erros no site ou em um edital.',
      'Configurações — preferências (administradores).',
    ],
  },
  {
    id: 'dashboard',
    title: 'Dashboard',
    group: 'Páginas',
    objective: 'O Dashboard é a tela inicial. Ele mostra um resumo do que merece atenção.',
    whenToUse: 'Use ao entrar no sistema ou quando quiser uma visão geral rápida.',
    steps: [
      'Veja os cards de métricas no topo.',
      'Confira o painel “Prioridades agora”.',
      'Veja editais que vencem em breve.',
      'Use os gráficos para entender fontes, modalidades e prazos.',
      'Clique em atalhos como “Ver editais vencendo” para abrir listas já filtradas.',
      'Use os atalhos rápidos para ir às páginas principais.',
    ],
    tips: [
      'Se muitos editais aparecem sem prazo, a fonte pode ainda não ter trazido uma data estruturada.',
      'Use o filtro de escopo Brasil / Internacional para separar oportunidades nacionais e internacionais.',
    ],
  },
  {
    id: 'editais',
    title: 'Editais',
    group: 'Páginas',
    objective: 'Buscar, filtrar e abrir oportunidades.',
    whenToUse: 'Quando você procura editais, chamadas ou programas de fomento.',
    steps: [
      'Use a busca para procurar por palavra-chave.',
      'Use filtros de prazo, fonte, escopo e modalidade.',
      'Clique em um edital para ver os detalhes.',
      'Marque favoritos quando quiser acompanhar depois.',
      'Veja os chips de filtro para saber o que está ativo.',
      'Clique no × de um chip para remover aquele filtro.',
    ],
    tips: [
      '“Vencendo em 7 dias” mostra oportunidades urgentes.',
      '“Sem prazo estruturado” significa que o sistema não encontrou data de encerramento confiável.',
      'Sempre abra o link oficial do edital antes de decidir.',
    ],
    commonErrors: [
      'Achar que falta edital quando os filtros estão muito restritos — limpe os chips.',
      'Confiar só no resumo sem abrir a fonte oficial.',
    ],
  },
  {
    id: 'edital-detalhe',
    title: 'Detalhe do edital',
    group: 'Páginas',
    objective: 'Mostra as informações principais de uma oportunidade.',
    whenToUse: 'Depois de clicar em um edital na lista.',
    steps: [
      'Leia título, fonte, prazo e descrição.',
      'Abra o link oficial.',
      'Verifique se o edital ainda está aberto.',
      'Use favorito se quiser acompanhar.',
      'Clique em “Reportar problema no edital” se encontrar link quebrado, duplicidade, prazo errado ou se não for um edital.',
    ],
    tips: [
      'O EditalFinder ajuda a encontrar oportunidades, mas a fonte oficial sempre deve ser conferida.',
    ],
  },
  {
    id: 'radar',
    title: 'Radar de Fomento',
    group: 'Páginas',
    objective: 'Compara clientes cadastrados com editais e mostra oportunidades compatíveis.',
    whenToUse: 'Quando você já tem um cliente cadastrado e quer sugestões automáticas.',
    steps: [
      'Escolha um cliente na lista.',
      'Aguarde o sistema calcular as oportunidades.',
      'Veja os melhores resultados e o score de compatibilidade.',
      'Leia o motivo da compatibilidade e os alertas.',
      'Abra o edital para confirmar na fonte oficial.',
      'Salve ou selecione oportunidades importantes.',
    ],
    tips: [
      'Quanto melhor o cadastro do cliente, melhor o Radar funciona.',
      'Se o cliente tem poucos dados, faça o briefing no Workspace do Consultor primeiro.',
      'O score ajuda a priorizar, mas não substitui análise humana.',
    ],
  },
  {
    id: 'cadastros',
    title: 'Cadastros',
    group: 'Páginas',
    objective: 'Guarda dados de clientes e usuários.',
    whenToUse: 'Antes de usar Radar ou Workspace do Consultor com um cliente novo.',
    steps: [
      'Abra Cadastros no menu.',
      'Cadastre ou edite um cliente.',
      'Preencha dados básicos, contato, localização e perfil.',
      'Salve.',
      'Use esse cliente no Radar ou no Workspace do Consultor.',
    ],
    tips: [
      'Não precisa preencher tudo de uma vez.',
      'Dados melhores geram recomendações melhores.',
      'Evite duplicar clientes com o mesmo nome.',
    ],
  },
  {
    id: 'workspace-consultor',
    title: 'Workspace do Consultor',
    group: 'Páginas',
    objective: 'Organiza o trabalho de consultoria com cada cliente.',
    whenToUse: 'Durante o atendimento a um cliente — triagem, seleção e pré-projeto.',
    steps: [
      'Escolha um cliente na lista à esquerda.',
      'Veja o status do cliente no topo.',
      'Faça o briefing rápido do perfil.',
      'Confira as oportunidades recomendadas (carteira).',
      'Selecione as mais promissoras.',
      'Gere relatório de triagem quando precisar documentar.',
      'Crie pré-projeto consultivo para proposta inicial.',
      'Acompanhe oportunidades salvas e o histórico de ações.',
      'Exporte dados (CSV) quando necessário.',
    ],
    blocks: [
      {
        title: 'Briefing rápido',
        body: 'Resumo rápido do perfil e necessidades do cliente. Comece por aqui.',
      },
      {
        title: 'Carteira de oportunidades',
        body: 'Editais que podem combinar com o cliente, com score e filtros.',
      },
      {
        title: 'Triagem',
        body: 'Ajuda a decidir quais oportunidades valem atenção antes de avançar.',
      },
      {
        title: 'Pré-projeto',
        body: 'Rascunho inicial de proposta para o cliente.',
      },
      {
        title: 'Plano de ação',
        body: 'Próximos passos recomendados para o consultor.',
      },
      {
        title: 'Histórico',
        body: 'Registro do que já foi feito com aquele cliente.',
      },
    ],
    tips: [
      'Comece sempre pelo briefing.',
      'Não selecione edital só pelo título — abra e confira.',
      'Use triagem antes de gerar pré-projeto.',
    ],
  },
  {
    id: 'noticias',
    title: 'Notícias',
    group: 'Páginas',
    objective: 'Acompanhar notícias relevantes para inovação, ciência e oportunidades.',
    whenToUse: 'Para entender o contexto do mercado e políticas públicas.',
    steps: [
      'Abra Notícias no menu.',
      'Use busca e filtros se disponíveis.',
      'Leia os títulos recentes.',
      'Abra a notícia original para detalhes completos.',
    ],
    tips: ['Notícias ajudam no contexto, mas não são editais para inscrição.'],
  },
  {
    id: 'pesquisas',
    title: 'Pesquisas',
    group: 'Páginas',
    objective: 'Acompanhar publicações, estudos e informações técnicas.',
    whenToUse: 'Como apoio técnico para consultoria e projetos.',
    steps: [
      'Abra Pesquisas no menu.',
      'Busque por tema.',
      'Veja fonte, data e resumo.',
      'Abra o link original.',
    ],
    tips: ['Pesquisas complementam editais; não substituem chamadas abertas.'],
  },
  {
    id: 'portais',
    title: 'Portais',
    group: 'Páginas',
    objective: 'Reunir fontes externas úteis para encontrar oportunidades.',
    whenToUse: 'Quando quiser pesquisar diretamente em sites de fomento e instituições.',
    steps: [
      'Abra Portais no menu.',
      'Escolha o tipo de portal.',
      'Clique para acessar a fonte oficial.',
      'Use como pesquisa complementar aos Editais do sistema.',
    ],
  },
  {
    id: 'reportar-problema',
    title: 'Reportar problema',
    group: 'Sistema',
    objective: 'Registrar erros ou sugestões e enviar ao suporte pelo seu aplicativo de e-mail.',
    blocks: [
      {
        title: 'Problema em um edital específico',
        body: 'Use no detalhe do edital. Exemplos: link quebrado, duplicado, prazo errado, não é edital, informação incorreta.',
      },
      {
        title: 'Problema no sistema (site)',
        body: 'Use o botão “Reportar problema” no topo ou no menu ☰. O app abre seu e-mail com o reporte preenchido; revise e envie a mensagem. Exemplos: página não abriu, botão travou, erro na tela.',
      },
    ],
    steps: [
      'Clique em Reportar problema.',
      'Escolha o tipo (edital ou sistema).',
      'Descreva o que aconteceu com clareza.',
      'Abra o e-mail com o reporte e confirme o envio no seu cliente de e-mail.',
    ],
    tips: ['Quanto mais claro o comentário, mais fácil será corrigir.'],
  },
  {
    id: 'configuracoes',
    title: 'Configurações',
    group: 'Sistema',
    objective: 'Ajustar preferências e dados da conta quando disponível.',
    steps: [
      'Abra Configurações (menu ☰ ou topo, se você for administrador).',
      'Revise logo, tema e opções disponíveis.',
      'Salve alterações.',
    ],
    tips: ['Algumas opções podem estar disponíveis apenas para administradores.'],
  },
  {
    id: 'faq',
    title: 'Dúvidas frequentes',
    group: 'Referência',
    blocks: [
      {
        title: 'Preciso preencher todos os dados do cliente?',
        body: 'Não. Mas quanto mais completo o cadastro, melhor o Radar e o Workspace funcionam.',
      },
      {
        title: 'O score do Radar decide sozinho?',
        body: 'Não. Ele ajuda a priorizar; o consultor deve conferir o edital oficial.',
      },
      {
        title: 'O que significa “sem prazo estruturado”?',
        body: 'O sistema ainda não encontrou uma data de encerramento confiável para aquele edital.',
      },
      {
        title: 'Link quebrado — o que faço?',
        body: 'Abra o detalhe do edital e use Reportar problema no edital.',
      },
      {
        title: 'Por onde começo?',
        body: 'Dashboard primeiro. Depois Editais ou Workspace do Consultor.',
      },
      {
        title: 'O que é briefing?',
        body: 'Resumo rápido do perfil e das necessidades do cliente no Workspace do Consultor.',
      },
    ],
  },
  {
    id: 'glossario',
    title: 'Glossário rápido',
    group: 'Referência',
    blocks: [
      { title: 'Edital', body: 'Oportunidade publicada por uma instituição.' },
      { title: 'Fonte', body: 'Instituição ou portal onde a oportunidade foi encontrada (ex.: FINEP, CNPq).' },
      { title: 'Prazo', body: 'Data limite para inscrição ou submissão.' },
      { title: 'Radar', body: 'Ferramenta que cruza clientes com oportunidades.' },
      { title: 'Briefing', body: 'Resumo rápido do cliente.' },
      { title: 'Triagem', body: 'Análise para decidir se vale avançar com uma oportunidade.' },
      { title: 'Pré-projeto', body: 'Rascunho inicial de uma proposta.' },
      {
        title: 'Escopo',
        body: 'Origem geográfica: Brasil, Internacional ou Multilateral.',
      },
      {
        title: 'Modalidade',
        body: 'Tipo da oportunidade: fomento, bolsa, licitação, concurso, etc.',
      },
    ],
  },
];

const ROUTE_SECTION_MAP = [
  { prefix: '/workspace-consultor', sectionId: 'workspace-consultor' },
  { prefix: '/edital/', sectionId: 'edital-detalhe' },
  { prefix: '/editais', sectionId: 'editais' },
  { prefix: '/radar-fomento', sectionId: 'radar' },
  { prefix: '/cadastros', sectionId: 'cadastros' },
  { prefix: '/noticias', sectionId: 'noticias' },
  { prefix: '/pesquisas', sectionId: 'pesquisas' },
  { prefix: '/portais-estrategicos', sectionId: 'portais' },
  { prefix: '/dashboard', sectionId: 'dashboard' },
];

export function getSectionById(id) {
  return HELP_SECTIONS.find((s) => s.id === id) || HELP_SECTIONS[0];
}

export function sectionFromPathname(pathname) {
  const hit = ROUTE_SECTION_MAP.find((r) => pathname.startsWith(r.prefix));
  return hit?.sectionId || 'getting-started';
}

export function buildSearchableText(section) {
  const parts = [
    section.title,
    section.group,
    section.objective,
    section.whenToUse,
    ...(section.steps || []),
    ...(section.tips || []),
    ...(section.commonErrors || []),
    ...(section.blocks || []).flatMap((b) => [b.title, b.body]),
  ];
  return parts.filter(Boolean).join(' ').toLowerCase();
}

export const HELP_SECTIONS_WITH_SEARCH = HELP_SECTIONS.map((s) => ({
  ...s,
  searchText: buildSearchableText(s),
}));

export function filterHelpSections(query) {
  const q = (query || '').trim().toLowerCase();
  if (!q) return HELP_SECTIONS_WITH_SEARCH;
  return HELP_SECTIONS_WITH_SEARCH.filter(
    (s) => s.searchText.includes(q) || s.title.toLowerCase().includes(q),
  );
}

export const HELP_NAV_GROUPS = [
  'Começando',
  'Páginas',
  'Sistema',
  'Referência',
];

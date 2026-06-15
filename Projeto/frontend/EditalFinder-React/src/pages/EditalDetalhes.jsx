import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/layout/Header';
import { dataService } from '../services/dataService';
import { formatDate, formatCurrency } from '../utils/formatters';
import { getDisplayTitle } from '../utils/displayTitle';
import { calcularScore } from '../services/matchService';
import { classificarEdital } from '../services/classificationService';
import { resolveActionLinks } from '../utils/edital/linkHealth';
import EditalReportProblemButton from '../components/editais/EditalReportProblemButton';
import AppReportProblemButton from '../components/feedback/AppReportProblemButton';
import EditalStatusBadges from '../components/editais/EditalStatusBadges';
import HelpPageLink from '../components/help/HelpPageLink';
import ExternalActionButton, { EXTERNAL_ACTION_TYPES } from '../utils/externalActions';
import { getEditalDetailErrorMessage } from '../utils/edital/editalDetailLookup';
import { logDetailDebug } from '../utils/qa/detailDebug';

// Perfis representativos para cálculo dinâmico de compatibilidade
// Campos alinhados com os nomes esperados pelo matchService.js
const PERFIS_MOCK = {
  'Startup': {
    setor: 'Tecnologia', area_inovacao: 'startup inovação tecnologia software',
    interesse_temas: 'inovação tecnologia digital empreendedorismo',
    descricao_projeto: 'desenvolvimento de produto tecnológico inovador',
    porte_empresa: 'ME', estado: 'SP', regiao: 'Sudeste',
    regular_fiscal: true, regular_trabalhista: true,
    possui_certidao_negativa: true, disponibilidade_contrapartida: false,
  },
  'MEI': {
    setor: 'Comércio', area_inovacao: 'mei microempreendedor serviços comércio',
    interesse_temas: 'empreendedorismo negócio microempresa',
    descricao_projeto: 'pequeno negócio individual de serviços',
    porte_empresa: 'MEI', estado: 'SP', regiao: 'Sudeste',
    regular_fiscal: true, regular_trabalhista: false,
    possui_certidao_negativa: false, disponibilidade_contrapartida: false,
  },
  'Universidade': {
    setor: 'Educação', area_inovacao: 'pesquisa ciência educação universidade laboratório',
    interesse_temas: 'pesquisa científica inovação acadêmica bolsa graduação pós-graduação',
    descricao_projeto: 'pesquisa e desenvolvimento científico em ambiente universitário',
    porte_empresa: 'Grande', estado: 'SP', regiao: 'Sudeste',
    regular_fiscal: true, regular_trabalhista: true,
    possui_certidao_negativa: true, disponibilidade_contrapartida: true,
  },
  'Pesquisador': {
    setor: 'Pesquisa', area_inovacao: 'pesquisa ciência laboratório desenvolvimento',
    interesse_temas: 'pesquisa desenvolvimento científico inovação tecnológica',
    descricao_projeto: 'projeto de pesquisa aplicada e desenvolvimento experimental',
    porte_empresa: 'ME', estado: 'SP', regiao: 'Sudeste',
    regular_fiscal: true, regular_trabalhista: true,
    possui_certidao_negativa: true, disponibilidade_contrapartida: false,
  },
  'ONG': {
    setor: 'Terceiro Setor', area_inovacao: 'ong social impacto comunidade sustentabilidade',
    interesse_temas: 'impacto social sustentabilidade inclusão ambiental',
    descricao_projeto: 'organização sem fins lucrativos de impacto social',
    porte_empresa: 'ME', estado: 'SP', regiao: 'Sudeste',
    regular_fiscal: true, regular_trabalhista: true,
    possui_certidao_negativa: true, disponibilidade_contrapartida: false,
  },
  'Empresa Industrial': {
    setor: 'Indústria', area_inovacao: 'indústria manufatura produção industrial automação',
    interesse_temas: 'processo produtivo automação indústria 4.0 manufatura',
    descricao_projeto: 'empresa de médio/grande porte no setor industrial',
    porte_empresa: 'Grande', estado: 'SP', regiao: 'Sudeste',
    regular_fiscal: true, regular_trabalhista: true,
    possui_certidao_negativa: true, disponibilidade_contrapartida: true,
  },
  'Cooperativa': {
    setor: 'Agronegócio', area_inovacao: 'cooperativa agro rural agrícola agricultura',
    interesse_temas: 'cooperativismo agronegócio rural pecuária alimentos',
    descricao_projeto: 'cooperativa agrícola do sul do Brasil',
    porte_empresa: 'Média', estado: 'PR', regiao: 'Sul',
    regular_fiscal: true, regular_trabalhista: true,
    possui_certidao_negativa: true, disponibilidade_contrapartida: true,
  },
  'Escola': {
    setor: 'Educação', area_inovacao: 'escola educação ensino aluno aprendizagem',
    interesse_temas: 'educação ensino básico formação pedagógica',
    descricao_projeto: 'instituição de ensino básico ou médio',
    porte_empresa: 'ME', estado: 'SP', regiao: 'Sudeste',
    regular_fiscal: true, regular_trabalhista: true,
    possui_certidao_negativa: true, disponibilidade_contrapartida: false,
  },
  'Hospital': {
    setor: 'Saúde', area_inovacao: 'saúde hospital medicina clínica tratamento',
    interesse_temas: 'saúde medicina pesquisa clínica hospitalar',
    descricao_projeto: 'hospital ou clínica de saúde de grande porte',
    porte_empresa: 'Grande', estado: 'SP', regiao: 'Sudeste',
    regular_fiscal: true, regular_trabalhista: true,
    possui_certidao_negativa: true, disponibilidade_contrapartida: true,
  },
  'Governo': {
    setor: 'Governo', area_inovacao: 'governo público municipal estadual federal',
    interesse_temas: 'gestão pública políticas públicas infraestrutura social',
    descricao_projeto: 'órgão público municipal ou estadual',
    porte_empresa: 'Grande', estado: 'SP', regiao: 'Sudeste',
    regular_fiscal: true, regular_trabalhista: true,
    possui_certidao_negativa: true, disponibilidade_contrapartida: true,
  },
};

const ICONE_TIPO = {
  pdf:   '📄',
  doc:   '📝',
  docx:  '📝',
  xls:   '📊',
  xlsx:  '📊',
  zip:   '🗜️',
  image: '🖼️',
};

function iconeAnexo(tipo = '', nome = '') {
  const ext = (tipo || nome.split('.').pop() || '').toLowerCase();
  return ICONE_TIPO[ext] || '📎';
}

/** Retorna string de URL pronta para href, ou null se inválida/vazia */
function urlDisponivel(val) {
  if (val == null || typeof val !== 'string') return null;
  const t = val.trim();
  return t.length > 0 ? t : null;
}


export default function EditalDetalhes() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [edital, setEdital]   = useState(null);
  const [anexos, setAnexos]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro]       = useState(null);
  const [errorKind, setErrorKind] = useState(null);
  const [anexosAviso, setAnexosAviso] = useState(null);

  // ⚠️ Todos os hooks ANTES dos early returns (Regras de Hooks)
  const perfisCompativeis = useMemo(() => {
    if (!edital) return [];
    const clf = classificarEdital(edital);
    const editalFormatado = {
      titulo:       edital.titulo,
      temas:        edital.temas,
      objetivo:     edital.objetivo,
      descricao:    edital.descricao,
      publico_alvo: edital.publico_alvo,
      elegibilidade: edital.elegibilidade,
      estado:       edital.estado,
      regiao:       edital.regiao,
      valor:        edital.valor_maximo,
      valorMinimo:  edital.valor_minimo,
      valorMaximo:  edital.valor_maximo,
      tipoRecurso:  clf?.tipo ?? 'Subvenção econômica',
      linkOriginal: edital.link || edital.link_inscricao || '',
      situacao:     edital.situacao,
      status:       edital.status,
      compatibilidade: edital.compatibilidade,
      validacao_status: edital.validacao_status,
      qualidade_dado: edital.qualidade_dado,
      dataLimite:   edital.prazo_envio,
    };
    return Object.entries(PERFIS_MOCK)
      .map(([nomePerfil, mockCliente]) => {
        const { score, compatibilidade: compat } = calcularScore(mockCliente, editalFormatado);
        return { perfil: nomePerfil, score, compatibilidade: compat };
      })
      .sort((a, b) => b.score - a.score);
  }, [edital]);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setErro(null);
      setErrorKind(null);
      setAnexosAviso(null);
      setEdital(null);
      setAnexos([]);

      const [editalSettled, anexosSettled] = await Promise.allSettled([
        dataService.getEditalById(id),
        dataService.getAnexosByEditalSafe(id),
      ]);

      let lookupResult = null;
      if (editalSettled.status === 'fulfilled') {
        lookupResult = editalSettled.value;
      } else {
        lookupResult = {
          edital: null,
          errorKind: 'supabase',
          routeParam: String(id ?? ''),
          normalizedId: String(id ?? ''),
          lookupBaseFound: false,
          lookupViewFound: false,
        };
        console.error(editalSettled.reason);
      }

      let anexosResult = { ok: true, data: [], error: null };
      if (anexosSettled.status === 'fulfilled') {
        anexosResult = anexosSettled.value;
      } else {
        anexosResult = {
          ok: false,
          data: [],
          error: { message: String(anexosSettled.reason?.message ?? anexosSettled.reason) },
        };
      }

      logDetailDebug({
        routeParam: lookupResult.routeParam,
        normalizedId: lookupResult.normalizedId,
        lookupBaseFound: lookupResult.lookupBaseFound,
        lookupViewFound: lookupResult.lookupViewFound,
        finalFound: Boolean(lookupResult.edital),
        lookupMode: lookupResult.lookupMode,
        attachmentsOk: anexosResult.ok,
        attachmentsError: anexosResult.error?.message ?? null,
        errorKind: lookupResult.errorKind,
      });

      if (!lookupResult.edital) {
        setErrorKind(lookupResult.errorKind || 'not_found');
        setErro(getEditalDetailErrorMessage(lookupResult.errorKind));
        setLoading(false);
        return;
      }

      setEdital(lookupResult.edital);
      setAnexos(anexosResult.ok ? anexosResult.data : []);
      if (!anexosResult.ok) {
        setAnexosAviso('Não foi possível carregar os anexos deste edital.');
      }
      setLoading(false);
    }
    load();
  }, [id]);

  if (loading) {
    return (
      <div className="page-wrapper">
        <Header />
        <div className="detalhes-loading">Carregando edital...</div>
      </div>
    );
  }

  if (erro || !edital) {
    return (
      <div className="page-wrapper" data-testid="edital-detail-error">
        <Header />
        <div className="detalhes-erro">
          <p data-testid="edital-detail-error-message">{erro || 'Edital não encontrado.'}</p>
          <div className="detalhes-erro-actions">
            <button className="detalhes-btn-voltar" onClick={() => navigate(-1)} data-testid="edital-detail-back">
              ← Voltar
            </button>
            <AppReportProblemButton
              origem="edital_detail_load"
              pagina="EditalDetalhes"
              componente="EditalDetalhes"
              acao="load_edital_failed"
              label="Reportar problema"
              variant="secondary"
              extraContext={{
                routeParam: id,
                errorKind: errorKind || 'unknown',
                lookupMode: 'base_then_view',
              }}
            />
          </div>
        </div>
      </div>
    );
  }

  const tags = edital.recomendacao
    ? edital.recomendacao.split(/[,;]/).map(t => t.trim()).filter(Boolean)
    : [];

  const tituloPagina = getDisplayTitle({
    titulo: edital.titulo,
    link: edital.link,
    descricao: edital.descricao,
    objetivo: edital.objetivo,
    temas: edital.temas,
    fonte_recurso: edital.fonte_recurso,
  });

  // Áreas temáticas do edital
  const areasTags = (edital.temas || edital.objetivo || '')
    .split(/[,;]/)
    .map(a => a.trim())
    .filter(a => a.length > 0 && a.length < 60);

  const corCompatibilidade = (pct) => {
    const v = parseFloat(pct);
    if (v >= 80) return '#16a34a';
    if (v >= 50) return '#d97706';
    return '#dc2626';
  };

  const linkActions = resolveActionLinks({
    linkOriginal: edital.link,
    linkInscricao: edital.link_inscricao,
    pdfUrl: edital.pdf_url,
    extras_raw: edital.extras,
  });
  const linkInscricao = urlDisponivel(linkActions.inscricao);
  const linkEdital = urlDisponivel(linkActions.site);
  const linkSite =
    linkEdital && linkInscricao && linkEdital === linkInscricao ? null : linkEdital;
  const pdfUrl = urlDisponivel(linkActions.pdf);
  const temAcoesLaterais =
    !!(linkInscricao || linkSite || pdfUrl) ||
    linkActions.inscDisabled ||
    linkActions.siteDisabled ||
    linkActions.pdfDisabled;

  return (
    <div className="page-wrapper">
      <Header />

      <div className="detalhes-page">
        {/* Botão voltar */}
        <button className="detalhes-btn-voltar" onClick={() => navigate(-1)}>
          ← Voltar para Editais
        </button>
        <HelpPageLink sectionId="edital-detalhe" label="Como ler o detalhe do edital?" />

        {/* Cabeçalho do edital */}
        <div className="detalhes-hero">
          <div className="detalhes-hero-info">
            <span className="detalhes-orgao-badge">{edital.fonte_recurso || (edital.organizacao?.nome) || '—'}</span>
            {linkActions.health.showUnavailableBadge ? (
              <span className="detalhes-link-health-badge" title="Auditoria: link oficial indisponível">
                Link indisponível
              </span>
            ) : null}
            <h1 className="detalhes-titulo">{tituloPagina}</h1>
            <div className="detalhes-status-badges">
              <EditalStatusBadges edital={edital} maxVisible={99} />
            </div>
          </div>
        </div>

        <div className="detalhes-grid">
          {/* ── Coluna principal ── */}
          <div className="detalhes-coluna-principal">

            {/* Informações gerais */}
            <section className="detalhes-secao">
              <h2 className="detalhes-secao-titulo">Informações Gerais</h2>
              <div className="detalhes-info-grid">
                {[
                  ['Área / Temas',     edital.temas || edital.objetivo],
                  ['Tipo de recurso',  edital.fonte_recurso],
                  ['Estado',           edital.estado || 'Nacional'],
                  ['Região',           edital.regiao],
                  ['Situação',         edital.situacao || edital.status],
                  ['Prazo de envio',   edital.prazo_envio ? formatDate(edital.prazo_envio) : 'Não informado'],
                  ['Data publicação',  edital.data_publicacao ? formatDate(edital.data_publicacao) : null],
                  ['Valor mínimo',     edital.valor_minimo ? formatCurrency(edital.valor_minimo) : null],
                  ['Valor máximo',     edital.valor_maximo ? formatCurrency(edital.valor_maximo) : null],
                  ['Contrapartida',    edital.contrapartida],
                  ['ODS vinculados',   edital.ods],
                  ['Contato',          edital.contato],
                ].filter(([, v]) => v).map(([label, valor]) => (
                  <div key={label} className="detalhes-info-row">
                    <span className="detalhes-info-label">{label}</span>
                    <span className="detalhes-info-valor">{valor}</span>
                  </div>
                ))}
              </div>
            </section>

            {/* Descrição */}
            {edital.descricao && (
              <section className="detalhes-secao">
                <h2 className="detalhes-secao-titulo">Descrição</h2>
                <p className="detalhes-descricao">{edital.descricao}</p>
              </section>
            )}

            {/* Objetivo */}
            {edital.objetivo && edital.objetivo !== edital.temas && (
              <section className="detalhes-secao">
                <h2 className="detalhes-secao-titulo">Objetivo</h2>
                <p className="detalhes-descricao">{edital.objetivo}</p>
              </section>
            )}

            {/* Elegibilidade */}
            {edital.elegibilidade && (
              <section className="detalhes-secao">
                <h2 className="detalhes-secao-titulo">Quem pode participar</h2>
                <p className="detalhes-descricao">{edital.elegibilidade}</p>
              </section>
            )}

            {/* Público-alvo */}
            {edital.publico_alvo && (
              <section className="detalhes-secao">
                <h2 className="detalhes-secao-titulo">Público-alvo</h2>
                <p className="detalhes-descricao">{edital.publico_alvo}</p>
              </section>
            )}

            {/* ── Documentos e PDFs ── */}
            <section className="detalhes-secao">
              <h2 className="detalhes-secao-titulo">📎 Documentos e PDFs</h2>

              {anexosAviso ? (
                <p className="detalhes-anexos-aviso" role="status" data-testid="edital-detail-anexos-warning">
                  {anexosAviso}
                </p>
              ) : null}

              {/* PDF principal — href só com URL válida */}
              {pdfUrl ? (
                <div className="detalhes-doc-principal">
                  <div className="detalhes-doc-icon">📄</div>
                  <div className="detalhes-doc-info">
                    <span className="detalhes-doc-nome">Edital Principal (PDF)</span>
                    <span className="detalhes-doc-tipo">Documento oficial do edital</span>
                  </div>
                  <ExternalActionButton
                    item={edital}
                    actionType={EXTERNAL_ACTION_TYPES.EDITAL_PDF}
                    url={pdfUrl}
                    label="📥 Baixar PDF"
                    className="detalhes-doc-btn detalhes-doc-btn-pdf"
                    logEdital
                    logCampo="pdf_url"
                  />
                </div>
              ) : (
                <p className="detalhes-sem-doc">PDF principal não cadastrado.</p>
              )}

              {/* Anexos do banco */}
              {anexos.length > 0 ? (
                <div className="detalhes-anexos-lista">
                  <h3 className="detalhes-anexos-subtitulo">Documentos Anexos ({anexos.length})</h3>
                  {anexos.map(anx => {
                    const urlAnexo = urlDisponivel(anx.url);
                    return (
                    <div key={anx.id_anexo} className="detalhes-doc-item">
                      <div className="detalhes-doc-icon">{iconeAnexo(anx.tipo, anx.nome || '')}</div>
                      <div className="detalhes-doc-info">
                        <span className="detalhes-doc-nome">{anx.nome || 'Documento sem nome'}</span>
                        {anx.tipo && <span className="detalhes-doc-tipo">{anx.tipo.toUpperCase()}</span>}
                        {anx.criado_em && (
                          <span className="detalhes-doc-data">
                            Adicionado em {formatDate(anx.criado_em)}
                          </span>
                        )}
                      </div>
                      {urlAnexo ? (
                        <ExternalActionButton
                          item={edital}
                          actionType={EXTERNAL_ACTION_TYPES.GENERIC_URL}
                          url={urlAnexo}
                          label="📥 Abrir"
                          className="detalhes-doc-btn"
                        />
                      ) : (
                        <span className="detalhes-doc-btn-disabled">Sem link</span>
                      )}
                    </div>
                    );
                  })}
                </div>
              ) : (
                <p className="detalhes-sem-doc" style={{ marginTop: '12px' }}>
                  Nenhum documento anexo cadastrado para este edital.
                </p>
              )}
            </section>
          </div>

          {/* ── Coluna lateral ── */}
          <div className="detalhes-coluna-lateral">

            {/* Ações rápidas: ordem Inscrição → Site → PDF; href só com URL válida */}
            {temAcoesLaterais ? (
              <div className="detalhes-acoes">
                {linkInscricao && (
                  <ExternalActionButton
                    item={edital}
                    actionType={EXTERNAL_ACTION_TYPES.EDITAL_INSCRICAO}
                    url={linkInscricao}
                    label="✅ Ir para Inscrição"
                    className="detalhes-btn-inscricao"
                    logEdital
                    logCampo="link_inscricao"
                  />
                )}
                {linkSite && (
                  <ExternalActionButton
                    item={edital}
                    actionType={EXTERNAL_ACTION_TYPES.EDITAL_PRIMARY}
                    url={linkSite}
                    label="🌐 Acessar Site do Edital"
                    className="detalhes-btn-site"
                    logEdital
                    logCampo="link"
                  />
                )}
                {pdfUrl && (
                  <ExternalActionButton
                    item={edital}
                    actionType={EXTERNAL_ACTION_TYPES.EDITAL_PDF}
                    url={pdfUrl}
                    label="📄 Baixar PDF Principal"
                    className="detalhes-btn-pdf"
                    logEdital
                    logCampo="pdf_url"
                  />
                )}
                {linkActions.inscDisabled && !linkInscricao && (
                  <span className="detalhes-doc-btn-disabled">Inscrição — link indisponível</span>
                )}
                {linkActions.siteDisabled && !linkSite && (
                  <span className="detalhes-doc-btn-disabled">Site — link indisponível</span>
                )}
                {linkActions.pdfDisabled && !pdfUrl && (
                  <span className="detalhes-doc-btn-disabled">PDF — link indisponível</span>
                )}
              </div>
            ) : (
              <p className="detalhes-sem-doc detalhes-acoes-vazio">
                Nenhum link externo cadastrado (site, inscrição ou PDF).
              </p>
            )}

            <div className="detalhes-report-problem-wrap">
              <EditalReportProblemButton edital={edital} variant="details" />
            </div>

            {/* Compatibilidade por Perfil */}
            <div className="detalhes-card-lateral">
              <h3 className="detalhes-card-lateral-titulo">👥 Compatibilidade por Perfil</h3>
              {perfisCompativeis.map(({ perfil, score, compatibilidade: compat }) => {
                const cor = corCompatibilidade(score);
                const badgeClass = compat === 'Alta' ? 'radar-badge-alta' : compat === 'Média' ? 'radar-badge-media' : 'radar-badge-baixa';
                return (
                  <div key={perfil} className="detalhes-perfil-row">
                    <span className="detalhes-perfil-nome">{perfil}</span>
                    <div className="detalhes-score-barra-wrap">
                      <div
                        className="detalhes-score-barra"
                        style={{ width: `${score}%`, background: cor }}
                      />
                    </div>
                    <span className="detalhes-perfil-pct" style={{ color: cor }}>{score}%</span>
                    <span className={`radar-badge ${badgeClass}`} style={{ fontSize: '10px', padding: '2px 6px' }}>{compat}</span>
                  </div>
                );
              })}
            </div>

            {/* Áreas Temáticas */}
            {areasTags.length > 0 && (
              <div className="detalhes-card-lateral">
                <h3 className="detalhes-card-lateral-titulo">🗂️ Áreas Temáticas</h3>
                <div className="detalhes-tags">
                  {areasTags.map(area => (
                    <span key={area} className="detalhes-tag detalhes-tag-area">{area}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Tags de recomendação */}
            {tags.length > 0 && (
              <div className="detalhes-card-lateral">
                <h3 className="detalhes-card-lateral-titulo">Recomendado para</h3>
                <div className="detalhes-tags">
                  {tags.map(tag => (
                    <span key={tag} className="detalhes-tag">{tag}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

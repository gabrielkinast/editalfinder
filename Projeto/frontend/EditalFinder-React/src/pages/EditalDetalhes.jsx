import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/layout/Header';
import { dataService } from '../services/dataService';
import { formatDate, formatCurrency } from '../utils/formatters';

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


export default function EditalDetalhes() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [edital, setEdital]   = useState(null);
  const [anexos, setAnexos]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro]       = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const [ed, anx] = await Promise.all([
          dataService.getEditalById(id),
          dataService.getAnexosByEdital(id),
        ]);
        setEdital(ed);
        setAnexos(anx);
      } catch (e) {
        setErro('Não foi possível carregar os dados do edital.');
        console.error(e);
      } finally {
        setLoading(false);
      }
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
      <div className="page-wrapper">
        <Header />
        <div className="detalhes-erro">
          <p>{erro || 'Edital não encontrado.'}</p>
          <button className="detalhes-btn-voltar" onClick={() => navigate(-1)}>← Voltar</button>
        </div>
      </div>
    );
  }

  const tags = edital.recomendacao
    ? edital.recomendacao.split(/[,;]/).map(t => t.trim()).filter(Boolean)
    : [];

  // Compatibilidade por perfil (JSONB do banco)
  const compatibilidade = edital.compatibilidade || {};
  const perfisCompativeis = Object.entries(compatibilidade)
    .filter(([, v]) => parseFloat(v) > 0)
    .sort(([, a], [, b]) => parseFloat(b) - parseFloat(a));

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

  return (
    <div className="page-wrapper">
      <Header />

      <div className="detalhes-page">
        {/* Botão voltar */}
        <button className="detalhes-btn-voltar" onClick={() => navigate(-1)}>
          ← Voltar para Editais
        </button>

        {/* Cabeçalho do edital */}
        <div className="detalhes-hero">
          <div className="detalhes-hero-info">
            <span className="detalhes-orgao-badge">{edital.fonte_recurso || (edital.organizacao?.nome) || '—'}</span>
            <h1 className="detalhes-titulo">{edital.titulo}</h1>
            {edital.justificativa && (
              <p className="detalhes-justificativa">"{edital.justificativa}"</p>
            )}
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

              {/* PDF principal */}
              {edital.pdf_url ? (
                <div className="detalhes-doc-principal">
                  <div className="detalhes-doc-icon">📄</div>
                  <div className="detalhes-doc-info">
                    <span className="detalhes-doc-nome">Edital Principal (PDF)</span>
                    <span className="detalhes-doc-tipo">Documento oficial do edital</span>
                  </div>
                  <a
                    href={edital.pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="detalhes-doc-btn detalhes-doc-btn-pdf"
                  >
                    📥 Baixar PDF
                  </a>
                </div>
              ) : (
                <p className="detalhes-sem-doc">PDF principal não cadastrado.</p>
              )}

              {/* Anexos do banco */}
              {anexos.length > 0 ? (
                <div className="detalhes-anexos-lista">
                  <h3 className="detalhes-anexos-subtitulo">Documentos Anexos ({anexos.length})</h3>
                  {anexos.map(anx => (
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
                      {anx.url ? (
                        <a
                          href={anx.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="detalhes-doc-btn"
                        >
                          📥 Abrir
                        </a>
                      ) : (
                        <span className="detalhes-doc-btn-disabled">Sem link</span>
                      )}
                    </div>
                  ))}
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

            {/* Ações rápidas */}
            <div className="detalhes-acoes">
              {edital.link_inscricao && (
                <a href={edital.link_inscricao} target="_blank" rel="noopener noreferrer" className="detalhes-btn-inscricao">
                  ✅ Ir para Inscrição
                </a>
              )}
              {edital.link && (
                <a href={edital.link} target="_blank" rel="noopener noreferrer" className="detalhes-btn-site">
                  🌐 Acessar Site do Edital
                </a>
              )}
              {edital.pdf_url && (
                <a href={edital.pdf_url} target="_blank" rel="noopener noreferrer" className="detalhes-btn-pdf">
                  📄 Baixar PDF Principal
                </a>
              )}
            </div>


            {/* Compatibilidade por Perfil */}
            {perfisCompativeis.length > 0 && (
              <div className="detalhes-card-lateral">
                <h3 className="detalhes-card-lateral-titulo">👥 Compatibilidade por Perfil</h3>
                {perfisCompativeis.map(([perfil, pct]) => {
                  const cor = corCompatibilidade(pct);
                  const pctNum = Math.min(Math.round(parseFloat(pct)), 100);
                  return (
                    <div key={perfil} className="detalhes-perfil-row">
                      <span className="detalhes-perfil-nome">{perfil}</span>
                      <div className="detalhes-score-barra-wrap">
                        <div
                          className="detalhes-score-barra"
                          style={{ width: `${pctNum}%`, background: cor }}
                        />
                      </div>
                      <span className="detalhes-perfil-pct" style={{ color: cor }}>{pctNum}%</span>
                    </div>
                  );
                })}
              </div>
            )}

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

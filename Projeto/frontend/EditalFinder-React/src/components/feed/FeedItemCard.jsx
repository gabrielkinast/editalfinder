import { formatDate, formatDateLoose } from '../../utils/formatters';
import { getDisplayTitle } from '../../utils/displayTitle';

function joinArrays(...lists) {
  const out = [];
  lists.forEach((arr) => {
    if (Array.isArray(arr)) arr.forEach((x) => x && out.push(String(x)));
  });
  return [...new Set(out)].join(', ') || '—';
}

export default function FeedItemCard({ item }) {
  const tituloCard = getDisplayTitle({
    titulo: item.titulo,
    link: item.link,
    descricao: item.conteudo,
    objetivo: null,
    temas: Array.isArray(item.tags) ? item.tags.join(', ') : null,
    fonte_recurso: item.fonte_recurso || item.fonte,
    resumo: item.resumo,
  });

  const badge = item.fonte_recurso || item.fonte || item.origem_portal || '—';
  const areas = joinArrays(item.area_cientifica, item.area_tecnologica, item.setor_estrategico);
  return (
    <div className="edital-card">
      <div className="edital-title-wrap">
        <h3 className="edital-title">{tituloCard}</h3>
      </div>

      <span className="edital-badge">{badge}</span>

      <div className="edital-meta">
        <div className="edital-meta-row">
          <span className="edital-meta-label">Áreas / setores:</span>
          <span>{areas}</span>
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">País / Região:</span>
          <span>{[item.pais, item.regiao].filter(Boolean).join(' · ') || '—'}</span>
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">Tipo:</span>
          <span>{item.tipo_conteudo || item.content_type || '—'}</span>
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">Validação:</span>
          <span>{item.validacao_status || '—'}</span>
        </div>
        {item.ativo === false && (
          <div className="edital-meta-row">
            <span className="edital-meta-label">Ativo:</span>
            <span>Não</span>
          </div>
        )}
        {item.publico_alvo && (
          <div className="edital-meta-row">
            <span className="edital-meta-label">Público:</span>
            <span>{item.publico_alvo}</span>
          </div>
        )}
      </div>

      {Array.isArray(item.tags) && item.tags.length > 0 && (
        <div className="edital-tags-perfil">
          {item.tags.slice(0, 4).map((t, i) => (
            <span key={`${t}-${i}`} className="edital-tag-recomendacao">{t}</span>
          ))}
        </div>
      )}

      <div className="edital-date">
        📅 Publicação: {formatDate(item.data_publicacao)} · Limite: {formatDate(item.prazo_envio)}
      </div>

      <div className="edital-actions" style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
        {item.link ? (
          <a href={item.link} target="_blank" rel="noopener noreferrer" className="btn-view" style={{ textDecoration: 'none', textAlign: 'center', flex: 1 }}>
            Site
          </a>
        ) : (
          <span className="btn-view disabled" style={{ opacity: 0.5, cursor: 'not-allowed', flex: 1 }}>Site</span>
        )}
        {item.imagem_url ? (
          <a href={item.imagem_url} target="_blank" rel="noopener noreferrer" className="btn-pdf" style={{ textDecoration: 'none', textAlign: 'center', flex: 1 }}>
            Imagem
          </a>
        ) : (
          <span className="btn-pdf disabled" style={{ opacity: 0.5, cursor: 'not-allowed', flex: 1 }}>
            —
          </span>
        )}
      </div>

      {item.resumo && (
        <p style={{ marginTop: '10px', fontSize: '13px', color: 'var(--text-muted, #666)', lineHeight: 1.45 }}>
          {(item.resumo || '').slice(0, 220)}{(item.resumo || '').length > 220 ? '…' : ''}
        </p>
      )}
      <p style={{ marginTop: '6px', fontSize: '11px', color: '#888' }}>
        Atualizado: {formatDateLoose(item.atualizado_em || item.criado_em)}
      </p>
    </div>
  );
}

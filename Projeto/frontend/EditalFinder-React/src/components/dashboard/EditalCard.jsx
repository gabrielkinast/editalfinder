import { useNavigate } from 'react-router-dom';
import { formatCurrency, formatDateLoose } from '../../utils/formatters';
import { prazoVencido } from '../../utils/edital/dates';
import { resumirEdital, formatTipoAmigavel, humanizeTaxonomyList } from '../../utils/edital/formatEditalUi';
import { coerceStringArray } from '../../utils/edital/coerceArrays';
import { resolveActionLinks } from '../../utils/edital/linkHealth';
import { showReviewPrazoBadge } from '../../utils/edital/editalVisibility';
import { onEditalLinkClick, siteLinkCampoEscolhido } from '../../utils/edital/logEditalLinkClick';
import HighlightedText from './HighlightedText';
import EditalReportProblemButton from '../editais/EditalReportProblemButton';

const ORG_WEBSITES = {
  FINEP: 'https://www.finep.gov.br',
  BNDES: 'https://www.bndes.gov.br',
  CNPQ: 'https://www.cnpq.br',
  CNPq: 'https://www.cnpq.br',
  FAPERGS: 'https://fapergs.rs.gov.br',
  FAPESP: 'https://fapesp.br',
  CORDIS: 'https://cordis.europa.eu',
  MCTI: 'https://www.gov.br/mcti',
  MAPA: 'https://www.gov.br/agricultura',
  MEC: 'https://www.gov.br/mec',
  'MINISTÉRIO DA SAÚDE': 'https://www.gov.br/saude',
};

function badgeClass(kind) {
  if (kind === 'ok') return 'edital-badge-mini edital-b-ok';
  if (kind === 'warn') return 'edital-badge-mini edital-b-warn';
  if (kind === 'bad') return 'edital-badge-mini edital-b-bad';
  if (kind === 'info') return 'edital-badge-mini edital-b-info';
  return 'edital-badge-mini edital-b-muted';
}

export default function EditalCard({
  edital,
  searchTokensNorm = [],
  isFavorite = false,
  onToggleFavorite,
  deadlineFavoriteBadge = null,
  density = 'normal',
  onOpenDetails,
}) {
  const navigate = useNavigate();

  const orgLabel = (edital.orgao || '').toUpperCase?.() || edital.orgao;
  const actions = resolveActionLinks(edital);
  const siteLink =
    actions.site ||
    (!actions.siteDisabled ? edital.orgSite || ORG_WEBSITES[orgLabel] : null) ||
    null;
  const pdfLink = actions.pdf;
  const inscricaoLink = actions.inscricao;
  const linkHealth = actions.health;
  const siteCampo = siteLinkCampoEscolhido(edital, actions, orgLabel, ORG_WEBSITES);
  const idNumerico = String(edital.id).replace('manual-', '');
  const deadline = edital.prazo_envio_raw || edital.dataLimite;
  const expired = deadline ? prazoVencido(deadline) : false;

  const vs = String(edital.validacao_status_raw || '').toLowerCase();
  const q = Number(edital.qualidade_dado_raw ?? 0);

  const badges = [];
  if (expired) badges.push({ k: 'Encerrado', c: 'bad' });
  else if (deadline) badges.push({ k: 'Aberto', c: 'ok' });
  else badges.push({ k: 'Sem prazo', c: 'warn' });

  if (!Number.isNaN(q) && q >= 70) badges.push({ k: 'Alta qualidade', c: 'ok' });
  if (vs === 'incompleto') badges.push({ k: 'Incompleto', c: 'warn' });
  if (vs === 'acesso_limitado') badges.push({ k: 'Acesso limitado', c: 'warn' });
  if (vs === 'suspeito') badges.push({ k: 'Suspeito', c: 'bad' });
  if (pdfLink) badges.push({ k: 'PDF', c: 'ok' });
  if (edital.pais_raw && !/brasil|brazil/i.test(edital.pais_raw))
    badges.push({ k: 'Internacional', c: 'info' });
  if (linkHealth.showUnavailableBadge) badges.push({ k: 'Link indisponível', c: 'warn' });
  if (showReviewPrazoBadge(edital)) badges.push({ k: 'Revisar prazo', c: 'warn' });

  const tipoR = String(edital.tipo_recurso_raw || '').toLowerCase();
  if (tipoR.includes('cred') || tipoR.includes('financi')) badges.push({ k: 'Crédito / finan.', c: 'info' });
  else if (tipoR.includes('subv') || tipoR.includes('grant')) badges.push({ k: 'Subvenção / grant', c: 'info' });
  if (edital.reembolsavel === true) badges.push({ k: 'Reembolsável', c: 'muted' });
  if (edital.reembolsavel === false) badges.push({ k: 'Não reembolsável', c: 'muted' });

  const valorN = Number(edital.valor_principal_num ?? edital.valor ?? 0);
  const valorFmt = valorN > 0 ? formatCurrency(valorN) : null;

  return (
    <div
      className={`edital-card ${edital.isManual ? 'edital-card-manual' : ''} edital-card-density-${density}`}
    >
      <div className="edital-card-top-row">
        <div className="edital-title-wrap">
          <h3 className="edital-title">
            <HighlightedText text={edital.titulo} tokensNorm={searchTokensNorm} />
          </h3>
        </div>
        <button
          type="button"
          className={`edital-fav-star ${isFavorite ? 'on' : ''}`}
          aria-label={isFavorite ? 'Remover dos favoritos' : 'Favoritar edital'}
          aria-pressed={isFavorite}
          title={isFavorite ? 'Remover dos favoritos' : 'Favoritar para acompanhamento e alertas de prazo'}
          onClick={(e) => {
            e.stopPropagation();
            onToggleFavorite?.(edital);
          }}
        >
          {isFavorite ? '★' : '☆'}
        </button>
      </div>

      <div className="edital-badges-row">
        <span className="edital-badge edital-badge-fonte">{edital.orgao || 'Fonte não informada'}</span>
        {badges.slice(0, 6).map((b) => (
          <span key={b.k} className={badgeClass(b.c)}>
            {b.k}
          </span>
        ))}
      </div>

      {deadlineFavoriteBadge?.label ? (
        <div className="edital-fav-prazo-wrap" aria-label="Prazo do favorito">
          <span className={badgeClass(deadlineFavoriteBadge.variant || 'info')}>
            {deadlineFavoriteBadge.label}
          </span>
        </div>
      ) : null}

      {edital.descricao && (
        <p className={`edital-card-desc clamp-${density === 'compact' ? 2 : density === 'detailed' ? 4 : 2}`}>
          {edital.descricao}
        </p>
      )}

      <p className="edital-intel-sum">{resumirEdital(edital)}</p>

      <div className="edital-meta compact-meta">
        <div className="edital-meta-row">
          <span className="edital-meta-label">Fonte recurso:</span>
          <span>{edital.fonte_recurso_display || edital.orgao}</span>
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">Oport./recurso:</span>
          <span>
            {formatTipoAmigavel(edital.tipo_oportunidade_raw)} ·{' '}
            {formatTipoAmigavel(edital.tipo_recurso_raw || edital.tipoRecurso)}
          </span>
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">Perfil:</span>
          <span>
            {coerceStringArray(edital.perfil_ideal_raw).slice(0, 3).join(', ') || (
              <span className="edital-muted-soft">—</span>
            )}
          </span>
        </div>
        {humanizeTaxonomyList(edital.setor_economico_raw) ? (
          <div className="edital-meta-row">
            <span className="edital-meta-label">Setor econômico:</span>
            <span>{humanizeTaxonomyList(edital.setor_economico_raw)}</span>
          </div>
        ) : null}
        {humanizeTaxonomyList(edital.setor_estrategico_raw) ? (
          <div className="edital-meta-row">
            <span className="edital-meta-label">Setores estratégicos:</span>
            <span>{humanizeTaxonomyList(edital.setor_estrategico_raw)}</span>
          </div>
        ) : null}
        {humanizeTaxonomyList(edital.area_tecnologica_raw) ? (
          <div className="edital-meta-row">
            <span className="edital-meta-label">Áreas tecnológicas:</span>
            <span>{humanizeTaxonomyList(edital.area_tecnologica_raw)}</span>
          </div>
        ) : null}
        {!humanizeTaxonomyList(edital.setor_economico_raw) &&
        !humanizeTaxonomyList(edital.setor_estrategico_raw) &&
        !humanizeTaxonomyList(edital.area_tecnologica_raw) ? (
          <div className="edital-meta-row">
            <span className="edital-meta-label">Classificação setorial:</span>
            <span className="edital-muted-soft">—</span>
          </div>
        ) : null}
        <div className="edital-meta-row">
          <span className="edital-meta-label">Local:</span>
          <span>
            {[edital.cidade_raw, edital.uf_raw, edital.regiao_raw, edital.pais_raw]
              .filter(Boolean)
              .join(' · ') || edital.estado || <span className="edital-muted-soft">—</span>}
          </span>
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">Valor:</span>
          {valorFmt ? <span>{valorFmt}</span> : <span className="edital-muted-soft">valor não informado</span>}
        </div>
        <div className="edital-meta-row">
          <span className="edital-meta-label">Qualidade:</span>
          <span>{edital.qualidade_dado_raw != null ? `${edital.qualidade_dado_raw}` : <span className="edital-muted-soft">sem aval.</span>}</span>
        </div>
      </div>

      <div
        className={`edital-date edital-prazo-chip ${deadline ? (expired ? 'deadline-exp' : '') : 'deadline-empty'}`}
      >
        {deadline ? (
          <>
            Prazo: <strong>{formatDateLoose(deadline)}</strong>
          </>
        ) : (
          <span className="edital-muted-soft">📅 Sem prazo informado</span>
        )}
      </div>

      <div className="edital-actions edital-actions-balanced">
        {inscricaoLink ? (
          <a
            href={inscricaoLink}
            target="_blank"
            rel="noreferrer"
            className="btn-inscricao dash-action"
            onClick={onEditalLinkClick(edital, 'link_inscricao', inscricaoLink)}
          >
            Inscrição
          </a>
        ) : siteLink ? (
          <a
            href={siteLink}
            target="_blank"
            rel="noreferrer"
            className="btn-view dash-action"
            onClick={onEditalLinkClick(edital, siteCampo, siteLink)}
          >
            Site
          </a>
        ) : actions.inscDisabled || actions.siteDisabled ? (
          <span className="dash-action-muted" title="Link indisponível (auditoria)">
            Link indisponível
          </span>
        ) : (
          <span className="dash-action-muted">Sem link</span>
        )}

        {pdfLink ? (
          <a
            href={pdfLink}
            target="_blank"
            rel="noreferrer"
            className="btn-pdf dash-action"
            onClick={onEditalLinkClick(edital, 'pdf_url', pdfLink)}
          >
            PDF
          </a>
        ) : actions.pdfDisabled ? (
          <span className="dash-action-muted" title="PDF indisponível (auditoria)">
            PDF indispon.
          </span>
        ) : null}

        <button
          type="button"
          className="btn-detalhes dash-action-outline"
          onClick={() =>
            typeof onOpenDetails === 'function' ? onOpenDetails(edital) : navigate(`/edital/${idNumerico}`)
          }
        >
          Detalhes
        </button>
      </div>

      <div className="edital-card-report-row">
        <EditalReportProblemButton edital={edital} variant="card" />
      </div>
    </div>
  );
}

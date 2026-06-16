import { useState, useCallback, useMemo } from 'react';
import ExternalActionButton, { EXTERNAL_ACTION_TYPES } from '../../utils/externalActions';
import {
  labelPortaisValidacaoBadge,
  labelQualidadeDado,
} from '../../utils/labels';
import {
  getPortalTipoDisplay,
  getPortalTipoSemanticKey,
  parseExtras,
  pickPortalResumo,
  isAcessoLimitadoRow,
} from '../../utils/portaisEstrategicos';
import {
  labelCategoriaPortal,
  labelFontePortal,
  formatSetoresPortalDisplay,
} from '../../utils/portaisDisplayLabels';
import StatusBadge from '../badges/StatusBadge';
import './PortalEstrategicoCard.css';

function badgeVariantForValidacao(v) {
  const k = String(v || '').toLowerCase();
  if (k === 'valido' || k === 'validado') return 'success';
  if (k === 'acesso_limitado') return 'warning';
  if (k === 'suspeito') return 'danger';
  if (k === 'incompleto') return 'muted';
  return 'default';
}

/**
 * Classes visuais do tipo contextual (aba fornecedores vs investimentos).
 * @param {'fornecedores'|'investimentos'} tabContext
 * @param {string} tipoKey
 */
function tipoVisualClass(tabContext, tipoKey) {
  const slug = tipoKey.replace(/_/g, '-');
  if (tabContext === 'fornecedores') return `portais-tipobadge portais-tipobadge--fn portais-tipobadge--fn-${slug}`;
  return `portais-tipobadge portais-tipobadge--inv portais-tipobadge--inv-${slug}`;
}

export default function PortalEstrategicoCard({ row, tabContext = 'fornecedores' }) {
  const [copied, setCopied] = useState(false);
  const titulo = (row?.titulo || '').trim() || 'Portal sem título';
  const fonteCruda = row?.fonte_recurso || row?.fonte || '';
  const fonteExibicao = labelFontePortal(fonteCruda || '—');

  const tipoLabel = getPortalTipoDisplay(row);
  const tipoKey = useMemo(() => getPortalTipoSemanticKey(row), [row]);
  const tipoClass = useMemo(() => tipoVisualClass(tabContext, tipoKey), [tabContext, tipoKey]);

  const categoria = labelCategoriaPortal(row?.categoria, row?.frontend_section);
  const validacao = row?.validacao_status;
  const qualidade = labelQualidadeDado(row?.qualidade_dado);
  const setores = formatSetoresPortalDisplay(row?.setor_estrategico);
  const resumo = pickPortalResumo(row);

  const precisaLogin = row?.requer_login === true;
  const limitado = isAcessoLimitadoRow(row) || precisaLogin;

  const ex = parseExtras(row?.extras);
  const tipoTooltipParts = [];
  if (ex.portal_tipo_wave1 && String(ex.portal_tipo_wave1).trim()) {
    tipoTooltipParts.push(`Classificação: ${tipoLabel}`);
  }
  tipoTooltipParts.push(
    tabContext === 'fornecedores'
      ? 'Hub, cadastro, documentação ou procurement de fornecedores quando aplicável.'
      : 'Investimento, hubs de funding ou internacionalização quando aplicável.',
  );

  const copyLink = useCallback(async () => {
    const url = row?.link;
    if (!url) return;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2200);
    } catch {
      window.prompt('Copiar link:', url);
    }
  }, [row?.link]);

  const hintLoginTitulo =
    'Este portal pode exigir login ou cadastro próprio antes de navegar até o recurso ou documentação.';

  return (
    <article className="portais-card edital-card">
      <header className="portais-card-head">
        <h3 className="portais-card-title">{titulo}</h3>
        <p className="portais-card-fonte" title={fonteCruda ? `Valor original: ${fonteCruda}` : undefined}>
          {fonteExibicao}
        </p>
      </header>

      <div className="portais-card-badge-row">
        <span className={`${tipoClass} portais-tipobadge--ellipsis`} title={tipoTooltipParts.join(' ')}>
          {tipoLabel}
        </span>
        <StatusBadge variant={badgeVariantForValidacao(validacao)}>
          {labelPortaisValidacaoBadge(validacao)}
        </StatusBadge>
        {(limitado || precisaLogin) && (
          <StatusBadge variant="warning" title={hintLoginTitulo}>
            Acesso especial
          </StatusBadge>
        )}
      </div>

      {(limitado || precisaLogin) && (
        <p className="portais-card-microhint" title={hintLoginTitulo}>
          {precisaLogin
            ? 'Pode exigir login ou cadastro no site de destino.'
            : 'Acesso pode estar sujeito a convite ou etapas adicionais no portal.'}
        </p>
      )}

      <dl className="portais-meta-dl">
        <div className="portais-meta-item">
          <dt>Categoria</dt>
          <dd>{categoria}</dd>
        </div>
        <div className="portais-meta-item">
          <dt>Consulta</dt>
          <dd>
            {precisaLogin || String(row?.acesso_tipo || '').toLowerCase().includes('limitado')
              ? 'Requer passos extras no portal'
              : 'Aberto para consulta pública'}
          </dd>
        </div>
        <div className="portais-meta-item">
          <dt>Qualidade do dado</dt>
          <dd>{qualidade}</dd>
        </div>
        <div className="portais-meta-item portais-meta-item--full">
          <dt>Setores estratégicos</dt>
          <dd>{setores}</dd>
        </div>
      </dl>

      <div className="portais-card-resumo-wrap">{resumo}</div>

      <div className="portais-card-actions">
        {row?.link ? (
          <ExternalActionButton
            item={row}
            actionType={EXTERNAL_ACTION_TYPES.PORTAL_PRIMARY}
            label="Abrir portal"
            className="portais-card-btn portais-card-btn-primary"
          />
        ) : (
          <span className="portais-card-btn portais-card-btn-primary portais-card-btn--disabled">Link indisponível</span>
        )}
        <button type="button" className="portais-card-btn portais-card-btn-secondary" disabled={!row?.link} onClick={copyLink}>
          {copied ? 'Link copiado' : 'Copiar link'}
        </button>
      </div>
    </article>
  );
}

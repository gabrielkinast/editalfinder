import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { buildConsultorTrackedOpportunities } from '../../utils/consultor/buildConsultorTrackedOpportunities';
import { removeTrackedOpportunity } from '../../utils/consultor/consultorTrackedOpportunitiesStorage';
import { logConsultorWorkspace } from '../../utils/consultorWorkspaceLog';
import ConsultorTrackedOpportunitiesModal from './ConsultorTrackedOpportunitiesModal';
import ConsultorTrackedOpportunityRow from './ConsultorTrackedOpportunityRow';

const VISIBLE_LIMIT = 5;

/**
 * Card “Oportunidades acompanhadas” no Workspace do Consultor.
 */
export default function ConsultorTrackedOpportunitiesCard({
  cliente = null,
  selectedOpportunities = [],
  allMatches = [],
  remoteFavorites = [],
  refreshTick = 0,
  favoritosRemoteEnabled = false,
  onOpenPortfolio,
  onOpenRadar,
  onTrackedRemoved,
}) {
  const navigate = useNavigate();
  const [modalOpen, setModalOpen] = useState(false);
  const [localTick, setLocalTick] = useState(0);

  const clienteId = cliente?.id_cliente ?? cliente?.id ?? null;
  const clienteNome = cliente?.nome_empresa || cliente?.razao_social || '';

  const trackedItems = useMemo(
    () =>
      buildConsultorTrackedOpportunities({
        cliente,
        selectedOpportunities,
        allMatches,
        remoteFavorites,
      }),
    [cliente, selectedOpportunities, allMatches, remoteFavorites, refreshTick, localTick],
  );

  useEffect(() => {
    if (!clienteId) return;
    logConsultorWorkspace('tracked_opportunities_loaded', {
      id_cliente: clienteId,
      count: trackedItems.length,
    });
  }, [clienteId, trackedItems.length]);

  const visibleItems = trackedItems.slice(0, VISIBLE_LIMIT);
  const hasMore = trackedItems.length > VISIBLE_LIMIT;

  const handleOpenItem = useCallback(
    (item, action) => {
      logConsultorWorkspace('tracked_opportunity_open', {
        id_cliente: clienteId,
        key: item.key,
        action,
      });
      if (action === 'radar') onOpenRadar?.(item);
    },
    [clienteId, onOpenRadar],
  );

  const handleRemove = useCallback(
    (item) => {
      if (!clienteId || !item?.key) return;
      removeTrackedOpportunity(clienteId, item.key);
      setLocalTick((t) => t + 1);
      logConsultorWorkspace('tracked_opportunity_remove', {
        id_cliente: clienteId,
        key: item.key,
      });
      onTrackedRemoved?.(item);
    },
    [clienteId, onTrackedRemoved],
  );

  const handleViewFavorites = useCallback(() => {
    navigate('/dashboard', { state: { somenteFavoritos: true } });
  }, [navigate]);

  if (!cliente) return null;

  return (
    <>
      <section
        id="consultor-tracked-section"
        className="consultor-section consultor-section--tracked consultor-placeholder-card"
      >
        <div className="consultor-section-head">
          <div>
            <h3 className="consultor-section-title consultor-placeholder-title">
              Oportunidades acompanhadas
            </h3>
            <p className="consultor-section-sub consultor-placeholder-desc">
              Seleção atual, último pré-projeto e favoritos reunidos para este cliente.
            </p>
          </div>
        </div>

        {trackedItems.length === 0 ? (
          <p className="consultor-tracked-empty">
            Nenhuma oportunidade acompanhada ainda. Selecione oportunidades na carteira ou favorite
            editais para acompanhar.
          </p>
        ) : (
          <ul className="consultor-tracked-list consultor-tracked-list--card">
            {visibleItems.map((item) => (
              <ConsultorTrackedOpportunityRow
                key={item.key}
                item={item}
                onOpenRadar={(it) => handleOpenItem(it, 'radar')}
                onRemove={handleRemove}
                showRemove={!item.badges?.includes('selecionada')}
              />
            ))}
          </ul>
        )}

        <div className="consultor-tracked-card-footer">
          {onOpenPortfolio ? (
            <button type="button" className="btn-view consultor-tracked-footer-btn" onClick={onOpenPortfolio}>
              Explorar carteira
            </button>
          ) : null}
          {favoritosRemoteEnabled ? (
            <button
              type="button"
              className="btn-detalhes dash-action-outline consultor-tracked-footer-btn"
              onClick={handleViewFavorites}
            >
              Ver favoritos
            </button>
          ) : null}
          {hasMore ? (
            <button
              type="button"
              className="consultor-tracked-show-all"
              onClick={() => setModalOpen(true)}
            >
              Ver todas acompanhadas ({trackedItems.length})
            </button>
          ) : null}
        </div>
      </section>

      <ConsultorTrackedOpportunitiesModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        items={trackedItems}
        clienteNome={clienteNome}
        onOpenRadar={(it) => handleOpenItem(it, 'radar')}
        onRemoveTracked={handleRemove}
      />
    </>
  );
}

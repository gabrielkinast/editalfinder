import { usePermissions } from '../../hooks/usePermissions';
import { openExternalUrl, EXTERNAL_ACTION_TYPES } from '../../utils/externalActions';

function formatCell(raw) {
  if (raw == null || raw === '') return '—';
  const t = typeof raw;
  if (t === 'string' || t === 'number' || t === 'boolean') return String(raw);
  if (t === 'bigint') return raw.toString();
  if (t === 'object') {
    if (Array.isArray(raw)) return raw.length ? raw.join(', ') : '—';
    try {
      const s = JSON.stringify(raw);
      return s.length > 80 ? `${s.slice(0, 77)}…` : s;
    } catch {
      return '—';
    }
  }
  return '—';
}

/**
 * @param {object} props
 * @param {string} [props.rowIdKey] — chave do ID para delete/keys (ex.: `id_cliente` se a primeira coluna não for o ID).
 * @param {(item: object, helpers: { onEdit: (i: object) => void; onDelete: (id: unknown) => void; idKey: string }) => import('react').ReactNode} [props.extraRowActions]
 * @param {string} [props.wrapClassName] — classes extras no wrapper da tabela (ex.: compactação por aba).
 */
export default function AdminTable({ columns, data, onEdit, onDelete, extraRowActions, rowIdKey, wrapClassName }) {
  const permissions = usePermissions();

  const idKey = rowIdKey ?? columns[0]?.key;

  const showsActionsColumn =
    permissions.canEdit ||
    permissions.canDelete ||
    typeof extraRowActions === 'function' ||
    data.some((item) => {
      const link = typeof item.link === 'string' && item.link.trim().length > 0;
      const pdf = typeof item.pdf_url === 'string' && item.pdf_url.trim().length > 0;
      return link || pdf;
    });

  const rowNeedsExternalActions = (item) => {
    if (!item || typeof item !== 'object') return false;
    const link = typeof item.link === 'string' && item.link.trim().length > 0;
    const pdf = typeof item.pdf_url === 'string' && item.pdf_url.trim().length > 0;
    return link || pdf;
  };

  const useCustomActions = typeof extraRowActions === 'function';

  return (
    <div className={['table-container', 'cad-table-wrap', wrapClassName].filter(Boolean).join(' ')}>
      <table className="admin-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key}>{col.label}</th>
            ))}
            {showsActionsColumn && <th className="admin-th-actions">Ações</th>}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length + (showsActionsColumn ? 1 : 0)}
                className="admin-table-empty"
              >
                Nenhum item encontrado.
              </td>
            </tr>
          ) : (
            data.map((item, idx) => (
              <tr key={item[idKey] || idx}>
                {columns.map((col) => (
                  <td key={col.key} data-label={col.label}>
                    {col.render ? col.render(item[col.key], item) : formatCell(item[col.key])}
                  </td>
                ))}
                {(permissions.canEdit ||
                  permissions.canDelete ||
                  useCustomActions ||
                  rowNeedsExternalActions(item)) && (
                  <td className="admin-td-actions" data-label="Ações">
                    {useCustomActions ? (
                      extraRowActions(item, {
                        onEdit,
                        onDelete,
                        idKey,
                      })
                    ) : (
                      <div className="admin-actions-stack">
                        {typeof item.pdf_url === 'string' && item.pdf_url.trim() && (
                          <button
                            type="button"
                            className="btn-action btn-open-pdf"
                            onClick={() => openExternalUrl(item.pdf_url, { actionType: EXTERNAL_ACTION_TYPES.EDITAL_PDF })}
                          >
                            Abrir PDF
                          </button>
                        )}
                        {typeof item.link === 'string' && item.link.trim() && (
                          <button
                            type="button"
                            className="btn-action btn-open-link"
                            onClick={() => openExternalUrl(item.link, { actionType: EXTERNAL_ACTION_TYPES.EDITAL_PRIMARY })}
                          >
                            Abrir Link
                          </button>
                        )}
                        {permissions.canEdit && (
                          <button type="button" className="btn-action btn-edit" onClick={() => onEdit(item)}>
                            Editar
                          </button>
                        )}
                        {permissions.canDelete && (
                          <button type="button" className="btn-action btn-delete" onClick={() => onDelete(item[idKey])}>
                            Deletar
                          </button>
                        )}
                      </div>
                    )}
                  </td>
                )}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

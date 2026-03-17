export default function AdminTable({ columns, data, onEdit, onDelete }) {
  return (
    <div className="table-container">
      <table className="admin-table">
        <thead>
          <tr>
            {columns.map((col) => <th key={col.key}>{col.label}</th>)}
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length + 1} style={{ textAlign: 'center', padding: '20px' }}>
                Nenhum item encontrado.
              </td>
            </tr>
          ) : (
            data.map((item, idx) => (
              <tr key={item.id || item.id_usuario || item.id_cliente || item.id_organizacao || item.id_edital || idx}>
                {columns.map((col) => (
                  <td key={col.key}>
                    {col.render ? col.render(item[col.key], item) : item[col.key]}
                  </td>
                ))}
                <td>
                  <button className="btn-action btn-edit" onClick={() => onEdit(item)}>Editar</button>
                  <button className="btn-action btn-delete" onClick={() => onDelete(item.id_usuario || item.id_cliente || item.id_organizacao || item.id_edital || item.id)}>Deletar</button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

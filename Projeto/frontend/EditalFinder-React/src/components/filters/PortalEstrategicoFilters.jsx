import { useMemo } from 'react';
import { getPortalTipoDisplay } from '../../utils/portaisEstrategicos';
import {
  labelFontePortal,
  labelValidacaoPortalSelect,
  formatSetoresPortalDisplay,
} from '../../utils/portaisDisplayLabels.js';
import { labelQualidadeDado } from '../../utils/labels.js';

function uniqSorted(vals) {
  const s = new Set();
  vals.forEach((v) => {
    if (v != null && String(v).trim() !== '') s.add(String(v).trim());
  });
  return [...s].sort((a, b) => a.localeCompare(b, 'pt-BR'));
}

function flattenSetores(rows) {
  const out = [];
  rows.forEach((r) => {
    const se = r?.setor_estrategico;
    if (Array.isArray(se)) se.forEach((x) => x && out.push(String(x)));
    else if (se) out.push(String(se));
  });
  return uniqSorted(out);
}

const EMPTY_FILTERS = {
  search: '',
  fonte: '',
  tipoPortal: '',
  validacao: '',
  acesso: '',
  setor: '',
  qualidade: '',
  includeSuspeitos: false,
};

export function getInitialPortalFilters() {
  return { ...EMPTY_FILTERS };
}

/**
 * @param {object} props
 * @param {object} props.filters
 * @param {(f: object) => void} props.onChange
 * @param {object[]} props.optionSourceRows — linhas ativas para gerar listas (inclui todas as validações para opções)
 * @param {() => void} props.onClear
 */
export default function PortalEstrategicoFilters({ filters, onChange, optionSourceRows, onClear }) {
  const fontes = useMemo(
    () => uniqSorted(optionSourceRows.map((r) => r?.fonte_recurso || r?.fonte)),
    [optionSourceRows]
  );
  const tipos = useMemo(() => uniqSorted(optionSourceRows.map((r) => getPortalTipoDisplay(r))), [optionSourceRows]);
  const validacoes = useMemo(() => uniqSorted(optionSourceRows.map((r) => r?.validacao_status)), [optionSourceRows]);
  const qualidades = useMemo(() => uniqSorted(optionSourceRows.map((r) => r?.qualidade_dado)), [optionSourceRows]);
  const setores = useMemo(() => flattenSetores(optionSourceRows), [optionSourceRows]);

  const handle = (e) => {
    const { name, value, type, checked } = e.target;
    onChange({
      ...filters,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  return (
    <div className="filters-section portais-filters-sidebar">
      <div className="filters-header portais-filters-head">
        <h2 className="filter-title portais-filters-title">Filtros</h2>
        <button type="button" className="btn-clear-filters portais-filters-clear-btn" onClick={onClear}>
          Limpar filtros
        </button>
      </div>

      <div className="filter-group">
        <h3 className="filter-label">Buscar</h3>
        <input
          type="search"
          name="search"
          className="filter-input-large"
          placeholder="Buscar portal, fonte ou tag…"
          value={filters.search}
          onChange={handle}
          style={{ width: '100%', padding: '8px 10px', borderRadius: '8px', border: '1px solid var(--border-light, #e0e0e0)' }}
        />
      </div>

      <div className="filter-group">
        <label className="checkbox-label">
          <input type="checkbox" name="includeSuspeitos" checked={filters.includeSuspeitos} onChange={handle} />
          <span>Incluir itens em revisão</span>
        </label>
      </div>

      <div className="filter-group">
        <h3 className="filter-label">Fonte</h3>
        <select name="fonte" className="filter-select" value={filters.fonte} onChange={handle}>
          <option value="">Todas</option>
          {fontes.map((f) => (
            <option key={f} value={f}>
              {labelFontePortal(f)}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <h3 className="filter-label">Tipo de portal</h3>
        <select name="tipoPortal" className="filter-select" value={filters.tipoPortal} onChange={handle}>
          <option value="">Todos</option>
          {tipos.map((f) => (
            <option key={f} value={f}>
              {f}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <h3 className="filter-label">Validação</h3>
        <select name="validacao" className="filter-select" value={filters.validacao} onChange={handle}>
          <option value="">Todas</option>
          {validacoes.map((f) => (
            <option key={f} value={f}>
              {labelValidacaoPortalSelect(f)}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <h3 className="filter-label">Acesso</h3>
        <select name="acesso" className="filter-select" value={filters.acesso} onChange={handle}>
          <option value="">Todos</option>
          <option value="publico">Consulta pública</option>
          <option value="limitado">Login, cadastro ou limitado</option>
        </select>
      </div>

      <div className="filter-group">
        <h3 className="filter-label">Setor estratégico</h3>
        <select name="setor" className="filter-select" value={filters.setor} onChange={handle}>
          <option value="">Todos</option>
          {setores.map((f) => (
            <option key={f} value={f}>
              {formatSetoresPortalDisplay(f)}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <h3 className="filter-label">Qualidade</h3>
        <select name="qualidade" className="filter-select" value={filters.qualidade} onChange={handle}>
          <option value="">Todas</option>
          {qualidades.map((f) => (
            <option key={f} value={f}>
              {labelQualidadeDado(f)}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

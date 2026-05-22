import { useMemo } from 'react';
import {
  TIPO_OPORTUNIDADE_OPTIONS,
  TIPO_RECURSO_OPTIONS,
  PERFIL_IDEAL_OPTIONS,
  SETOR_ESTRATEGICO_OPTIONS,
  AREA_TECNOLOGICA_OPTIONS,
  REGIOES_BR,
  STATUS_PRESET_OPTIONS,
} from '../../utils/edital/editalCatalogConstants';

function CollapseSection({ title, children, defaultOpen }) {
  return (
    <details className="editai-filter-collapse" open={defaultOpen}>
      <summary className="editai-filter-summary">{title}</summary>
      <div className="editai-filter-collapse-body">{children}</div>
    </details>
  );
}

export default function EditaisFiltersSidebar({
  filters,
  setFilters,
  facets,
  prefs,
  updatePrefs,
  uniquePaises = [],
  uniqueUFs = [],
  dynamicAreas = [],
  onReset,
}) {
  const mergedTipoRecurso = useMemo(() => {
    const s = new Set([
      ...TIPO_RECURSO_OPTIONS.map((t) => t.toLowerCase()),
      ...(facets?.tipoRecurso ?? []).map(([l]) => String(l).toLowerCase()),
    ]);
    return [...s].sort((a, b) =>
      String(a).localeCompare(String(b), 'pt-BR'),
    );
  }, [facets]);

  const patch = (partial) =>
    setFilters((prev) => ({
      ...prev,
      ...partial,
    }));

  const toggleObjKey = (keySection, dictKey, checked) => {
    setFilters((prev) => ({
      ...prev,
      [keySection]: {
        ...(prev[keySection] || {}),
        [dictKey]: checked,
      },
    }));
  };

  const fontList = facets?.fonte ?? [];
  const filtFonteLower = String(filters.fonteBusca || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
  const fontDisplayed = filtFonteLower.length
    ? fontList.filter(([lbl]) =>
        String(lbl || '')
          .toLowerCase()
          .normalize('NFD')
          .replace(/[\u0300-\u036f]/g, '')
          .includes(filtFonteLower),
      )
    : fontList;

  return (
    <div className="filters-section editai-filters-v2">
      <div className="filters-header editai-filters-head">
        <h2 className="filter-title">Filtros</h2>
        <button type="button" className="btn-clear-filters" onClick={onReset}>
          Limpar filtros
        </button>
      </div>

      <CollapseSection title="Preferências (este navegador)" defaultOpen={false}>
        <p className="editai-help">Salvo automaticamente ao marcar/desmarcar.</p>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={!!prefs.showRuidos}
            onChange={(e) => updatePrefs({ showRuidos: e.target.checked })}
          />
          Mostrar títulos ruídosos (menus, conta PJ etc.)
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={!!prefs.preferPdf}
            onChange={(e) => updatePrefs({ preferPdf: e.target.checked })}
          />
          Preferir editais com PDF (prioridade)
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={!!prefs.preferNacional}
            onChange={(e) => updatePrefs({ preferNacional: e.target.checked })}
          />
          Preferir oportunidades nacionais
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={!!prefs.preferInternacional}
            onChange={(e) => updatePrefs({ preferInternacional: e.target.checked })}
          />
          Preferir oportunidades internacionais
        </label>
        <label className="checkbox-label editai-muted">
          Densidade:{' '}
          <select
            className="filter-select"
            value={prefs.density}
            onChange={(e) => updatePrefs({ density: e.target.value })}
          >
            <option value="compact">Compacta</option>
            <option value="normal">Normal</option>
            <option value="detailed">Detalhada</option>
          </select>
        </label>
        <label className="checkbox-label editai-muted">
          Cards por página:{' '}
          <select
            className="filter-select"
            value={String(prefs.pageSize)}
            onChange={(e) => updatePrefs({ pageSize: Number(e.target.value) })}
          >
            {[24, 40, 60, 120].map((n) => (
              <option key={n} value={String(n)}>
                {n}
              </option>
            ))}
          </select>
        </label>
      </CollapseSection>

      <CollapseSection title="Regras rápidas" defaultOpen>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={filters.toggleIncluirEncerrados}
            onChange={(e) => patch({ toggleIncluirEncerrados: e.target.checked })}
          />
          Incluir encerrados (prazo vencido)
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={filters.toggleIncluirSuspeitos}
            onChange={(e) => patch({ toggleIncluirSuspeitos: e.target.checked })}
          />
          Incluir suspeitos (validação)
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={filters.toggleMostrarInativos}
            onChange={(e) => patch({ toggleMostrarInativos: e.target.checked })}
          />
          Mostrar inativos
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={filters.toggleSoPdf}
            onChange={(e) => patch({ toggleSoPdf: e.target.checked })}
          />
          Mostrar apenas com PDF
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={filters.toggleAltaQualidade}
            onChange={(e) => patch({ toggleAltaQualidade: e.target.checked })}
          />
          Apenas alta qualidade (≥70)
        </label>
      </CollapseSection>

      <CollapseSection title="Status (filtro adicional)" defaultOpen={false}>
        <div className="checkbox-list">
          {STATUS_PRESET_OPTIONS.map((opt) => (
            <label key={opt.id} className="checkbox-label">
              <input
                type="checkbox"
                checked={!!filters.statusSelections?.[opt.id]}
                onChange={(e) =>
                  toggleObjKey('statusSelections', opt.id, e.target.checked)
                }
              />
              {opt.label}
            </label>
          ))}
        </div>
      </CollapseSection>

      <CollapseSection title="Tipo de oportunidade">
        <select
          className="filter-select"
          value={filters.tipoOportunidade}
          onChange={(e) => patch({ tipoOportunidade: e.target.value })}
        >
          {TIPO_OPORTUNIDADE_OPTIONS.map((x) => (
            <option key={x.label} value={x.id}>
              {x.label || '(todos)'}
            </option>
          ))}
        </select>
      </CollapseSection>

      <CollapseSection title="Tipo de recurso">
        <select
          className="filter-select"
          value={filters.tipoRecurso}
          onChange={(e) => patch({ tipoRecurso: e.target.value })}
        >
          <option value="">Todos os tipos</option>
          {mergedTipoRecurso.map((t) => {
            const c = facets?.tipoRecursoCounts?.get?.(t)
              ?? facets?.tipoRecursoCounts?.[t];
            const countStr = typeof c === 'number' ? ` (${c})` : '';
            return (
              <option key={t} value={t}>
                {t.replace(/_/g, ' ')}
                {countStr}
              </option>
            );
          })}
        </select>

        <h4 className="filter-subhdr">Lista antiga de visualização</h4>
        <select
          className="filter-select"
          value={filters.resourceTypeLegacy}
          onChange={(e) => patch({ resourceTypeLegacy: e.target.value })}
        >
          <option value="">(compat — ignorar)</option>
          <option value="Linha de crédito">Linha de crédito</option>
          <option value="Subvenção econômica">Subvenção econômica</option>
          <option value="Híbrido">Híbrido</option>
        </select>
      </CollapseSection>

      <CollapseSection title="Prazo">
        <select
          className="filter-select"
          value={filters.prazoPreset}
          onChange={(e) => {
            const v = e.target.value;
            patch({
              prazoPreset: v,
              ...(v === 'encerrados' ? { toggleIncluirEncerrados: true } : {}),
            });
          }}
        >
          <option value="">Todos</option>
          <option value="vencendo_7">Vencendo em 7 dias</option>
          <option value="vencendo_30">Vencendo em 30 dias</option>
          <option value="prazo_confortavel">Prazo confortável</option>
          <option value="sem_prazo">Sem prazo estruturado</option>
          <option value="encerrados">Encerrados</option>
          <option value="prazo_invalido">Prazo inválido</option>
          <option value="d90">Fecha em até 90 dias (legado)</option>
        </select>
      </CollapseSection>

      <CollapseSection title="Escopo geográfico">
        <select
          className="filter-select"
          value={filters.queryScope || 'todos'}
          onChange={(e) => {
            const v = e.target.value;
            patch({ queryScope: v === 'todos' ? '' : v });
          }}
        >
          <option value="todos">Todos</option>
          <option value="brasil">Brasil</option>
          <option value="internacional">Internacional</option>
          <option value="multilateral">Multilateral</option>
        </select>
      </CollapseSection>

      <CollapseSection title="Valor (R$)">
        <select
          className="filter-select"
          value={filters.valorPreset}
          onChange={(e) => patch({ valorPreset: e.target.value })}
        >
          <option value="">Faixa livre (use mín/máx)</option>
          <option value="ate50k">Até R$ 50 mil</option>
          <option value="50_500k">R$ 50 mil – R$ 500 mil</option>
          <option value="500k_5m">R$ 500 mil – R$ 5 milhões</option>
          <option value="acima5m">Acima de R$ 5 milhões</option>
          <option value="naoInformado">Valor não informado</option>
        </select>
        <div className="valor-range">
          <input
            type="number"
            className="filter-input-valor"
            placeholder="Mínimo"
            value={filters.valorMin}
            onChange={(e) => patch({ valorMin: e.target.value })}
          />
          <span className="valor-range-sep">até</span>
          <input
            type="number"
            className="filter-input-valor"
            placeholder="Máximo"
            value={filters.valorMax}
            onChange={(e) => patch({ valorMax: e.target.value })}
          />
        </div>
      </CollapseSection>

      <CollapseSection title="Qualidade dos dados">
        <label className="checkbox-label">
          <input type="checkbox" checked={filters.qualAlta} onChange={(e)=>patch({qualAlta:e.target.checked})}/>
          Alta (≥70)
        </label>
        <label className="checkbox-label">
          <input type="checkbox" checked={filters.qualMedia} onChange={(e)=>patch({qualMedia:e.target.checked})}/>
          Média (40–69)
        </label>
        <label className="checkbox-label">
          <input type="checkbox" checked={filters.qualBaixa} onChange={(e)=>patch({qualBaixa:e.target.checked})}/>
          Baixa (&lt;40 mas &gt;0)
        </label>
        <label className="checkbox-label">
          <input type="checkbox" checked={filters.qualIncomplete} onChange={(e)=>patch({qualIncomplete:e.target.checked})}/>
          Dados incompletos
        </label>
        <label className="checkbox-label">
          <input type="checkbox" checked={filters.qualSuspeitos} onChange={(e)=>patch({qualSuspeitos:e.target.checked})}/>
          Suspeitos
        </label>
        <label className="checkbox-label">
          <input type="checkbox" checked={filters.qualLimited} onChange={(e)=>patch({qualLimited:e.target.checked})}/>
          Acesso limitado
        </label>
      </CollapseSection>

      <CollapseSection title="Documento">
        <label className="checkbox-label"><input type="checkbox" checked={filters.docComPdf} onChange={(e)=>patch({docComPdf:e.target.checked})}/> Com PDF</label>
        <label className="checkbox-label"><input type="checkbox" checked={filters.docSemPdf} onChange={(e)=>patch({docSemPdf:e.target.checked})}/> Sem PDF</label>
        <label className="checkbox-label"><input type="checkbox" checked={filters.docComLink} onChange={(e)=>patch({docComLink:e.target.checked})}/> Com link oficial</label>
        <label className="checkbox-label"><input type="checkbox" checked={filters.docComCodigo} onChange={(e)=>patch({docComCodigo:e.target.checked})}/> Com código / nº chamada ou edital</label>
      </CollapseSection>

      <CollapseSection title="Perfil ideal" defaultOpen={false}>
        <div className="checkbox-scroll">
          {PERFIL_IDEAL_OPTIONS.map((p) => (
            <label key={p} className="checkbox-label">
              <input
                type="checkbox"
                checked={!!filters.perfil_ideal?.[p]}
                onChange={(e) => toggleObjKey('perfil_ideal', p, e.target.checked)}
              />
              {p.replace(/_/g, ' ')}
            </label>
          ))}
        </div>
      </CollapseSection>

      <CollapseSection title="Setor estratégico" defaultOpen={false}>
        <div className="checkbox-scroll">
          {SETOR_ESTRATEGICO_OPTIONS.map((p) => (
            <label key={p} className="checkbox-label">
              <input
                type="checkbox"
                checked={!!filters.setor_estrategico?.[p]}
                onChange={(e) => toggleObjKey('setor_estrategico', p, e.target.checked)}
              />
              {p}
            </label>
          ))}
        </div>
      </CollapseSection>

      <CollapseSection title="Área tecnológica" defaultOpen={false}>
        <div className="checkbox-scroll">
          {AREA_TECNOLOGICA_OPTIONS.map((p) => (
            <label key={p} className="checkbox-label">
              <input
                type="checkbox"
                checked={!!filters.area_tecnologica?.[p]}
                onChange={(e) => toggleObjKey('area_tecnologica', p, e.target.checked)}
              />
              {p}
            </label>
          ))}
        </div>
      </CollapseSection>

      <CollapseSection title="Região / País">
        <h4 className="filter-subhdr">Região (campo texto legado)</h4>
        <select
          className="filter-select"
          value={filters.regiaoLegacy}
          onChange={(e) => patch({ regiaoLegacy: e.target.value })}
        >
          <option value="">Todas as regiões</option>
          {REGIOES_BR.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
        <h4 className="filter-subhdr">País</h4>
        <select className="filter-select" value={filters.pais} onChange={(e)=>patch({pais:e.target.value})}>
          <option value="">Todos</option>
          {uniquePaises.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
        <h4 className="filter-subhdr">UF</h4>
        <select className="filter-select" value={filters.uf} onChange={(e)=>patch({uf:e.target.value})}>
          <option value="">Todas</option>
          {uniqueUFs.map((uf) => (
            <option key={uf} value={uf}>
              {uf}
            </option>
          ))}
        </select>
        <h4 className="filter-subhdr">Cidade (busca parcial)</h4>
        <input
          className="filter-input-valor"
          style={{ width: '100%', marginBottom: 8 }}
          placeholder="Nome da cidade"
          value={filters.cidadeBusca}
          onChange={(e)=>patch({cidadeBusca:e.target.value})}
        />
      </CollapseSection>

      <CollapseSection title="Fonte / órgão" defaultOpen={false}>
        <input
          className="filter-input-valor"
          style={{ width: '100%' }}
          placeholder="Buscar fonte..."
          value={filters.fonteBusca}
          onChange={(e) => patch({ fonteBusca: e.target.value })}
        />
        <div className="checkbox-scroll fonte-checkbox-scroll">
          {fontDisplayed.slice(0, 60).map(([lbl, cnt]) => {
            const key = String(lbl || '').toLowerCase().trim();
            if (!key || key === '— não informado') return null;
            return (
              <label key={lbl} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={!!filters.fontesSelectedKeys?.[key]}
                  onChange={(e) =>
                    toggleObjKey('fontesSelectedKeys', key, e.target.checked)
                  }
                />
                {lbl}{typeof cnt === 'number' ? ` (${cnt})` : ''}
              </label>
            );
          })}
        </div>
      </CollapseSection>

      <CollapseSection title="Área temática">
        <div className="checkbox-scroll">
          {dynamicAreas.map(({ label, count }) => {
            const dk = label.toLowerCase().trim();
            return (
              <label key={label} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={!!filters.areas?.[dk]}
                  onChange={(e) => toggleObjKey('areas', dk, e.target.checked)}
                />
                {label}
                {typeof count === 'number' ? ` (${count})` : ''}
              </label>
            );
          })}
        </div>
      </CollapseSection>

    </div>
  );
}

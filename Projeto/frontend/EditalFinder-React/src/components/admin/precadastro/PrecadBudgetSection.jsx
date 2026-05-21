import PrecadFieldMeta from './PrecadFieldMeta';
import PrecadSectionHint from './PrecadSectionHint';

export default function PrecadBudgetSection({ form, fieldIntel, onChangeTxt, onChangeChk }) {
  return (
    <section id="precad-orcamento" className="precad-consultor-section">
      <h3 className="precad-section-title">E) Orçamento preliminar</h3>
      <PrecadSectionHint>
        Valores orientativos — confirme com o cliente e com o regulamento. Não substitui planilha oficial de submissão.
      </PrecadSectionHint>
      <div className="precad-form-grid">
        <div className="precad-field-row full">
          <label className="precad-field-label">Resumo do valor total estimado</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_orcamento_resumo"
            rows={3}
            value={form.bloco_estr_orcamento_resumo}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_orcamento_resumo" /> : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Contrapartida</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_orcamento_contrapartida"
            rows={2}
            value={form.bloco_estr_orcamento_contrapartida}
            onChange={onChangeTxt}
          />
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Categorias de gasto sugeridas</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_orcamento_categorias"
            rows={4}
            value={form.bloco_estr_orcamento_categorias}
            onChange={onChangeTxt}
          />
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Referências financeiras (edital)</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_ref_fin_texto"
            rows={3}
            value={form.bloco_estr_ref_fin_texto}
            onChange={onChangeTxt}
          />
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Observações financeiras</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_orcamento_observacoes"
            rows={2}
            value={form.bloco_estr_orcamento_observacoes}
            onChange={onChangeTxt}
          />
        </div>
        <div className="precad-field-row">
          <label className="precad-check precad-check-inline">
            <input
              type="checkbox"
              name="bloco2_valor_projeto_sem_def"
              checked={!!form.bloco2_valor_projeto_sem_def}
              onChange={onChangeChk}
            />
            Valor ainda não definido com o cliente
          </label>
        </div>
      </div>
    </section>
  );
}

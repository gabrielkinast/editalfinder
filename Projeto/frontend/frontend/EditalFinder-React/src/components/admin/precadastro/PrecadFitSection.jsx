import PrecadFieldMeta from './PrecadFieldMeta';

export default function PrecadFitSection({ form, fieldIntel, onChangeTxt }) {
  return (
    <section className="precad-fit-section" id="precad-fit-aderencia">
      <h3 className="precad-section-title">Enquadramento / aderência ao edital</h3>

      <div className="precad-form-grid">
        <div className="precad-field-row full">
          <label className="precad-field-label">Por que o projeto combina com a linha</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_por_que_linha"
            rows={3}
            value={form.bloco_estr_por_que_linha}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_por_que_linha" /> : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Requisitos já atendidos (cadastro)</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_requisitos_atendidos"
            rows={3}
            value={form.bloco_estr_requisitos_atendidos}
            onChange={onChangeTxt}
          />
          {fieldIntel ? (
            <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_requisitos_atendidos" />
          ) : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Lacunas de informação / riscos</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_lacunas"
            rows={3}
            value={form.bloco_estr_lacunas}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_lacunas" /> : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Documentos recomendados</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_docs_recomendados"
            rows={4}
            value={form.bloco_estr_docs_recomendados}
            onChange={onChangeTxt}
          />
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Próximos passos</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_proximos_passos"
            rows={3}
            value={form.bloco_estr_proximos_passos}
            onChange={onChangeTxt}
          />
        </div>
      </div>
    </section>
  );
}

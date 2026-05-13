export default function PrecadObservations({ form, onChangeTxt }) {
  return (
    <section className="precad-obs-section" id="precad-observacoes">
      <h3 className="precad-section-title">Observações internas</h3>
      <div className="precad-field-row full">
        <label className="precad-field-label">Notas internas</label>
        <textarea
          className="precad-textarea"
          name="bloco_estr_obs_internas"
          rows={3}
          value={form.bloco_estr_obs_internas}
          onChange={onChangeTxt}
        />
      </div>
      <div className="precad-field-row full">
        <label className="precad-field-label">Pendências / checklist rápido</label>
        <textarea
          className="precad-textarea"
          name="bloco_estr_pendencias_checklist"
          rows={4}
          value={form.bloco_estr_pendencias_checklist}
          onChange={onChangeTxt}
          placeholder={"Ex.: CNPJ validado ✓&#10;Contrato social anexo ☐"}
        />
      </div>
      <div className="precad-field-row full">
        <label className="precad-field-label">Pendências (texto corrido)</label>
        <textarea
          className="precad-textarea"
          name="bloco_estr_pendencias"
          rows={2}
          value={form.bloco_estr_pendencias}
          onChange={onChangeTxt}
        />
      </div>
    </section>
  );
}

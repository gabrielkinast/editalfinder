import PrecadFieldMeta from './PrecadFieldMeta';
import PrecadSectionHint from './PrecadSectionHint';

export default function PrecadDocumentsRisksSection({ form, fieldIntel, onChangeTxt }) {
  return (
    <div className="precad-docs-risks-stack">
      <section id="precad-documentos" className="precad-consultor-section">
        <h3 className="precad-section-title">F) Documentos necessários</h3>
        <PrecadSectionHint>Organize por tipo para facilitar a reunião com o cliente e o checklist de submissão.</PrecadSectionHint>
        <div className="precad-form-grid">
          <div className="precad-field-row full">
            <label className="precad-field-label">Documentos do cliente</label>
            <textarea
              className="precad-textarea"
              name="bloco_estr_docs_cliente"
              rows={4}
              value={form.bloco_estr_docs_cliente}
              onChange={onChangeTxt}
            />
          </div>
          <div className="precad-field-row full">
            <label className="precad-field-label">Documentos técnicos</label>
            <textarea
              className="precad-textarea"
              name="bloco_estr_docs_tecnicos"
              rows={3}
              value={form.bloco_estr_docs_tecnicos}
              onChange={onChangeTxt}
            />
          </div>
          <div className="precad-field-row full">
            <label className="precad-field-label">Documentos financeiros / jurídicos</label>
            <textarea
              className="precad-textarea"
              name="bloco_estr_docs_financeiros"
              rows={3}
              value={form.bloco_estr_docs_financeiros}
              onChange={onChangeTxt}
            />
          </div>
          <div className="precad-field-row full">
            <label className="precad-field-label">Documentos do edital / regulamento</label>
            <textarea
              className="precad-textarea"
              name="bloco_estr_docs_edital_regulamento"
              rows={3}
              value={form.bloco_estr_docs_edital_regulamento}
              onChange={onChangeTxt}
            />
          </div>
          <div className="precad-field-row full">
            <label className="precad-field-label">Visão agregada (legado / PDF)</label>
            <textarea
              className="precad-textarea"
              name="bloco_estr_docs_recomendados"
              rows={3}
              value={form.bloco_estr_docs_recomendados}
              onChange={onChangeTxt}
            />
            {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_docs_recomendados" /> : null}
          </div>
        </div>
      </section>

      <section id="precad-riscos" className="precad-consultor-section">
        <h3 className="precad-section-title">G) Riscos e pendências</h3>
        <PrecadSectionHint>
          Prazo curto, elegibilidade incerta, dados incompletos ou necessidade de reunião — registre aqui para o consultor.
        </PrecadSectionHint>
        <div className="precad-form-grid">
          <div className="precad-field-row full">
            <label className="precad-field-label">Riscos e pendências consolidados</label>
            <textarea
              className="precad-textarea"
              name="bloco_estr_riscos_pendencias"
              rows={5}
              value={form.bloco_estr_riscos_pendencias}
              onChange={onChangeTxt}
            />
            {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_riscos_pendencias" /> : null}
          </div>
          <div className="precad-field-row full">
            <label className="precad-field-label">Lacunas / alertas complementares</label>
            <textarea
              className="precad-textarea"
              name="bloco_estr_lacunas"
              rows={3}
              value={form.bloco_estr_lacunas}
              onChange={onChangeTxt}
            />
          </div>
          <div className="precad-field-row full">
            <label className="precad-field-label">Alertas do Radar</label>
            <textarea
              className="precad-textarea"
              name="bloco_estr_alertas_radar"
              rows={3}
              value={form.bloco_estr_alertas_radar}
              onChange={onChangeTxt}
            />
          </div>
          <div className="precad-field-row full">
            <label className="precad-field-label">Checklist inicial</label>
            <textarea
              className="precad-textarea"
              name="bloco_estr_checklist_inicial"
              rows={5}
              value={form.bloco_estr_checklist_inicial}
              onChange={onChangeTxt}
            />
          </div>
        </div>
      </section>

      <section id="precad-proximos-passos" className="precad-consultor-section">
        <h3 className="precad-section-title">H) Próximos passos</h3>
        <PrecadSectionHint>Sequência sugerida até a submissão no portal — adapte ao fluxo do consultor.</PrecadSectionHint>
        <div className="precad-field-row full">
          <textarea
            className="precad-textarea"
            name="bloco_estr_proximos_passos"
            rows={6}
            value={form.bloco_estr_proximos_passos}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_proximos_passos" /> : null}
        </div>
      </section>
    </div>
  );
}

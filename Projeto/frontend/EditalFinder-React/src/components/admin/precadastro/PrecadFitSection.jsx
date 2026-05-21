import PrecadFieldMeta from './PrecadFieldMeta';
import PrecadSectionHint from './PrecadSectionHint';

export default function PrecadFitSection({ form, fieldIntel, onChangeTxt }) {
  return (
    <section className="precad-fit-section" id="precad-fit-aderencia">
      <h3 className="precad-section-title">B) Aderência ao edital</h3>
      <PrecadSectionHint>
        Explique ao cliente por que a oportunidade faz sentido, o que falta confirmar e quais critérios de elegibilidade
        revisar no regulamento.
      </PrecadSectionHint>

      <div className="precad-form-grid">
        <div className="precad-field-row full">
          <label className="precad-field-label">Por que esta oportunidade combina com o cliente</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_motivo_recomendacao"
            rows={4}
            value={form.bloco_estr_motivo_recomendacao}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_motivo_recomendacao" /> : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Pontos fortes de aderência</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_principais_aderencias"
            rows={4}
            value={form.bloco_estr_principais_aderencias}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_principais_aderencias" /> : null}
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Por que o projeto combina com a linha de fomento</label>
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
          <label className="precad-field-label">Critérios de elegibilidade já atendidos (cadastro)</label>
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
          <label className="precad-field-label">Lacunas e pontos a complementar</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_pontos_complementar"
            rows={3}
            value={form.bloco_estr_pontos_complementar}
            onChange={onChangeTxt}
          />
        </div>
        <div className="precad-field-row full">
          <label className="precad-field-label">Lacunas / alertas de risco (aderência)</label>
          <textarea
            className="precad-textarea"
            name="bloco_estr_lacunas"
            rows={3}
            value={form.bloco_estr_lacunas}
            onChange={onChangeTxt}
          />
          {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_lacunas" /> : null}
        </div>
      </div>
    </section>
  );
}

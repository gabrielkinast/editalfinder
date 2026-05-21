import PrecadFieldMeta from './PrecadFieldMeta';
import PrecadSectionHint from './PrecadSectionHint';

export default function PrecadWorkPlanSection({ form, fieldIntel, onChangeTxt, onGoCompleto }) {
  return (
    <section id="precad-plano-trabalho" className="precad-consultor-section">
      <h3 className="precad-section-title">D) Plano de trabalho</h3>
      <PrecadSectionHint>
        Etapas, responsáveis e cronograma preliminar. Para metas detalhadas com datas, use também o formulário completo
        (quadro de metas físicas).
      </PrecadSectionHint>
      <div className="precad-field-row full">
        <label className="precad-field-label">Plano de trabalho (fases e atividades)</label>
        <textarea
          className="precad-textarea"
          name="bloco_estr_plano_trabalho"
          rows={6}
          value={form.bloco_estr_plano_trabalho}
          onChange={onChangeTxt}
        />
        {fieldIntel ? <PrecadFieldMeta fieldIntel={fieldIntel} fieldKey="bloco_estr_plano_trabalho" /> : null}
      </div>
      {onGoCompleto ? (
        <button type="button" className="precad-mini-btn" onClick={onGoCompleto}>
          Abrir cronograma detalhado (metas físicas)
        </button>
      ) : null}
    </section>
  );
}

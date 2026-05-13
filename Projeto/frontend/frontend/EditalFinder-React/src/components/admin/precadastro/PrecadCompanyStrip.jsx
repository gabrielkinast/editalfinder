export default function PrecadCompanyStrip({ form }) {
  return (
    <div className="precad-co-strip">
      <div className="precad-co-strip-inner">
        <div>
          <span className="k">Nome fantasia</span>
          <span className="v">{form.bloco1_nome_fantasia || '—'}</span>
        </div>
        <div>
          <span className="k">Razão social</span>
          <span className="v">{form.bloco1_razao_social || '—'}</span>
        </div>
        <div>
          <span className="k">CNPJ</span>
          <span className="v">{form.bloco1_cnpj || '—'}</span>
        </div>
        <div>
          <span className="k">Porte</span>
          <span className="v">{form.bloco1_porte_empresa || '—'}</span>
        </div>
        <div>
          <span className="k">Setor</span>
          <span className="v">{form.bloco1_setor_empresa || '—'}</span>
        </div>
        <div>
          <span className="k">UF / Município</span>
          <span className="v">{[form.bloco1_municipio, form.bloco1_uf].filter(Boolean).join(' / ') || '—'}</span>
        </div>
      </div>
      <p className="precad-muted small co-hint">
        Dados cadastrais detalhados e contatos ficam na aba <strong>Formulário completo</strong>.
      </p>
    </div>
  );
}

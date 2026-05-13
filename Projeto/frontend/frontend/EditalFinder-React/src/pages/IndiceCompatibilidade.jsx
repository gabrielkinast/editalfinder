import Header from '../components/layout/Header';

export default function IndiceCompatibilidade() {
  return (
    <div className="page-wrapper">
      <Header />

      <div className="indice-page">
        <div className="radar-legenda-box indice-legenda-box">
          <div className="radar-legenda-titulo">📊 Como funciona o Índice de Compatibilidade</div>
          <p className="radar-legenda-descricao">
            O Radar de Fomento compara cliente e edital por etapas: normalização de texto, filtros eliminatórios (inativo,
            ruído de título, prazo ou validação quando aplicável), sete fatores pontuados até 100, penalidades e explicações
            legíveis. Não há API externa nem embeddings nesta versão.
          </p>
          <p className="radar-legenda-descricao" style={{ marginTop: '8px' }}>
            Pontuação (total 100 pts), composta por 7 critérios:
          </p>
          <div className="radar-legenda-criterios">
            <div className="radar-legenda-criterio">
              <div><strong>Afinidade temática</strong><span>setor, temas e descrições cruzadas com título/texto/tags do edital e expansão de sinônimos</span></div>
              <span className="radar-legenda-pts">30</span>
            </div>
            <div className="radar-legenda-criterio">
              <div><strong>Perfil e elegibilidade</strong><span>público-alvo do edital, porte mencionado, idade mínima de CNPJ (quando aparece no texto), regularidade do cadastro</span></div>
              <span className="radar-legenda-pts">20</span>
            </div>
            <div className="radar-legenda-criterio">
              <div><strong>Tipo de recurso</strong><span>modalidade declarada/agenciada versus preferências de modalidade inferidas ou indicadas pelo cliente</span></div>
              <span className="radar-legenda-pts">15</span>
            </div>
            <div className="radar-legenda-criterio">
              <div><strong>Localização</strong><span>UF/região/âmbito nacional ou internacional, sem superfaturar vagas geograficamente</span></div>
              <span className="radar-legenda-pts">10</span>
            </div>
            <div className="radar-legenda-criterio">
              <div><strong>Prazo e situação</strong><span>datas de encerramento; prazos muito próximos recebem menos pontuação</span></div>
              <span className="radar-legenda-pts">10</span>
            </div>
            <div className="radar-legenda-criterio">
              <div><strong>Qualidade e confiança</strong><span>marcadores opcionais (validação, qualidade declarada pela fonte, PDF)</span></div>
              <span className="radar-legenda-pts">10</span>
            </div>
            <div className="radar-legenda-criterio">
              <div><strong>Faixa de valor</strong><span>interesse configurado pelo cliente versus valores informados na oportunidade</span></div>
              <span className="radar-legenda-pts">5</span>
            </div>
          </div>
          <p className="radar-legenda-descricao" style={{ marginTop: '8px' }}>
            O JSON histórico de <strong>compatibilidade</strong> não é mais misturado ao percentual: o resultado reflete apenas
            o motor local e os dados do cadastro/edital. Você pode ativar filtros opcionais (encerrados, suspeitos, aproximados)
            na tela do Radar.
          </p>
          <div className="radar-legenda-cores" style={{ marginTop: '12px' }}>
            <span className="radar-legenda-cor radar-legenda-cor-alta">● Alta — 85%+</span>
            <span className="radar-legenda-cor radar-legenda-cor-media">● Média — 62 a 84%</span>
            <span className="radar-legenda-cor radar-legenda-cor-baixa">● Baixa — abaixo de 62%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

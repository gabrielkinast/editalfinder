import Header from '../components/layout/Header';

export default function IndiceCompatibilidade() {
  return (
    <div className="page-wrapper">
      <Header />

      <div className="indice-page">
        <div className="radar-legenda-box indice-legenda-box">
          <div className="radar-legenda-titulo">📊 Como funciona o Índice de Compatibilidade</div>
          <p className="radar-legenda-descricao">
            O índice mede o quanto cada edital combina com o cadastro do cliente (perfil, localização, porte, maturidade, valores, regularidade, prazo e idade) e, quando existe, com o JSON <strong>compatibilidade</strong> publicado no edital — mas só quando uma chave do JSON corresponde ao cliente.
          </p>
          <p className="radar-legenda-descricao" style={{ marginTop: '8px' }}>
            Pontuação do cadastro (total 100 pts), composta por 8 critérios:
          </p>
          <div className="radar-legenda-criterios">
            <div className="radar-legenda-criterio">
              <div><strong>Afinidade temática</strong><span>setor, CNAE, área de inovação, temas, projeto × temas, objetivo, público-alvo, elegibilidade, ODS</span></div>
              <span className="radar-legenda-pts">até 30</span>
            </div>
            <div className="radar-legenda-criterio">
              <div><strong>Localização</strong><span>estado / região / abrangência nacional</span></div>
              <span className="radar-legenda-pts">até 15</span>
            </div>
            <div className="radar-legenda-criterio">
              <div><strong>Porte e elegibilidade</strong><span>porte da empresa e menção ao CNAE na elegibilidade</span></div>
              <span className="radar-legenda-pts">até 15</span>
            </div>
            <div className="radar-legenda-criterio">
              <div><strong>Maturidade do projeto</strong><span>Ideação / Validação / Operação / Escala × vocabulário do edital</span></div>
              <span className="radar-legenda-pts">até 10</span>
            </div>
            <div className="radar-legenda-criterio">
              <div><strong>Faixa de valor</strong><span>interesse do cliente × valor do edital + capacidade financeira</span></div>
              <span className="radar-legenda-pts">até 10</span>
            </div>
            <div className="radar-legenda-criterio">
              <div><strong>Regularidade</strong><span>fiscal, trabalhista, certidão e contrapartida</span></div>
              <span className="radar-legenda-pts">até 10</span>
            </div>
            <div className="radar-legenda-criterio">
              <div><strong>Prazo e situação</strong><span>{'> 30d = 5 · 7–30d = 3 · < 7d = 1 · expirado = 0'}</span></div>
              <span className="radar-legenda-pts">até 5</span>
            </div>
            <div className="radar-legenda-criterio">
              <div><strong>Idade da empresa</strong><span>tempo de CNPJ vs. exigência explícita do edital</span></div>
              <span className="radar-legenda-pts">até 5</span>
            </div>
          </div>
          <p className="radar-legenda-descricao" style={{ marginTop: '8px' }}>
            Quando o edital traz JSON <strong>compatibilidade</strong> com uma chave que bate no seu cadastro, o índice final é <strong>35% do JSON + 65% do cadastro</strong>. Sem correspondência no JSON, é só cadastro. Editais expirados ficam no final mesmo com score alto.
          </p>
          <div className="radar-legenda-cores" style={{ marginTop: '12px' }}>
            <span className="radar-legenda-cor radar-legenda-cor-alta">● Alta — 75 a 100%</span>
            <span className="radar-legenda-cor radar-legenda-cor-media">● Média — 45 a 74%</span>
            <span className="radar-legenda-cor radar-legenda-cor-baixa">● Baixa — 0 a 44%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

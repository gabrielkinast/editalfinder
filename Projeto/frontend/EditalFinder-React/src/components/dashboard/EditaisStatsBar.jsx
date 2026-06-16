/** Resumo textual + métricas da lista atual (os pills “Abertos / Com PDF…” não são filtros ligados — são apenas contagem dentro da seleção atual). */
export default function EditaisStatsBar({
  filteredCount,
  catalogCount,
  abertosNaLista,
  comPdfNaLista,
  altaQualNaLista,
  showPdfToggle,
  showQualToggle,
  semPdfOcultos,
  baixaQualOcultos,
  encerradosOcultosHint,
  suspeitosOcultosHint,
  ruidosOcultosHint,
}) {
  return (
    <div className="editais-stats-bar" aria-label="Resumo dos editais" data-testid="editais-stats-bar">
      <div className="editais-stats-primary">
        <strong>
          Mostrando {filteredCount}
          {catalogCount != null ? ` de ${catalogCount} recebidos` : ''} editais
        </strong>
      </div>
      <p className="editais-stats-default-hint">
        Filtros padrão implícitos: cadastro não inativo (<code>ativo ≠ false</code>), sem{' '}
        <code>suspeito</code>, sem prazo vencido (prazo nulo é mantido), títulos de ruído ocultos
        até você liberar nas preferências.
      </p>
      {filteredCount > 0 ? (
        <div className="editais-stats-mini" aria-label="Contagens na seleção atual (não são toggles de filtro)">
          <span className="editais-stat-pill stat-plain" title="Quantos ficaram com prazo futuro nesta lista filtrada">
            Abertos nesta lista: {abertosNaLista ?? '—'}
          </span>
          <span className="editais-stat-pill stat-plain">Com PDF (nesta lista): {comPdfNaLista ?? '—'}</span>
          <span className="editais-stat-pill stat-plain">Alta qualidade (nesta lista): {altaQualNaLista ?? '—'}</span>
        </div>
      ) : null}

      <div className="editais-stats-mini editais-stats-ocultos">
        {(encerradosOcultosHint ?? 0) > 0 && (
          <span className="editais-stat-pill stat-muted" title="Itens com prazo passado ficam ocultos até incluir encerrados">
            Encerrados ocultos: {encerradosOcultosHint}
          </span>
        )}
        {(suspeitosOcultosHint ?? 0) > 0 && (
          <span className="editais-stat-pill stat-muted" title="validacao_status=suspeito">
            Suspeitos ocultos: {suspeitosOcultosHint}
          </span>
        )}
        {(ruidosOcultosHint ?? 0) > 0 && (
          <span className="editais-stat-pill stat-muted" title="Títulos de menu/FAQ etc. quando preferências bloqueiam">
            Ruídos ocultos: {ruidosOcultosHint}
          </span>
        )}
        {showPdfToggle && (semPdfOcultos ?? 0) > 0 && (
          <span className="editais-stat-pill stat-warn">
            Sem PDF (excluídos pelo toggle): {semPdfOcultos}
          </span>
        )}
        {showQualToggle && (baixaQualOcultos ?? 0) > 0 && (
          <span className="editais-stat-pill stat-warn">
            Fora de alta qualidade (excluídos): {baixaQualOcultos}
          </span>
        )}
      </div>
    </div>
  );
}

/** Motivos de reporte de problema em editais (aba Editais). */

export const EDITAL_FEEDBACK_REASONS = [
  {
    value: 'link_quebrado',
    label: 'Link quebrado',
    placeholder: 'Ex.: o botão Site abre uma página Page Not Found.',
  },
  {
    value: 'nao_e_oportunidade',
    label: 'Não é edital/oportunidade',
    placeholder: 'Ex.: parece uma página institucional, não uma chamada aberta.',
  },
  {
    value: 'edital_encerrado',
    label: 'Edital encerrado',
    placeholder: 'Ex.: o prazo já passou ou a chamada é de 2022.',
  },
  {
    value: 'duplicado',
    label: 'Duplicado',
    placeholder: 'Ex.: este item aparece repetido com outro título.',
  },
  {
    value: 'informacao_incorreta',
    label: 'Informação incorreta',
    placeholder: 'Ex.: o prazo, fonte ou valor parece errado.',
  },
  {
    value: 'outro',
    label: 'Outro',
    placeholder: 'Descreva o que está errado neste item.',
  },
];

export const EDITAL_FEEDBACK_COMMENT_MIN_OUTRO = 10;
export const EDITAL_FEEDBACK_COMMENT_MAX = 1000;

export function getEditalFeedbackReason(value) {
  return EDITAL_FEEDBACK_REASONS.find((r) => r.value === value) || null;
}

export function formatCurrency(value) {
    if (value === undefined || value === null) return 'R$ 0';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

export function formatDate(dateString) {
    if (!dateString) return '-';
    try {
        const date = new Date(dateString + 'T00:00:00');
        if (isNaN(date.getTime())) return '-';
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    } catch (e) {
        return '-';
    }
}

/** Aceita date ISO (timestamptz) ou string somente data. */
export function formatDateLoose(value) {
    if (value == null || value === '') return '-';
    const s = String(value);
    const d = s.includes('T') ? new Date(s) : new Date(s + 'T00:00:00');
    if (isNaN(d.getTime())) return '-';
    return d.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
    });
}

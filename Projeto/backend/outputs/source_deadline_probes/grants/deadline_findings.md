# Deadline findings — grants

- Fixture closeDate: 2027-09-30
- Fixture só posted: missing=True
- Amostra: 15/20 com prazo ISO

## Fixture
```json
{
  "with_close": {
    "grants_close_date": "2027-09-30",
    "deadline_source_field": "close_date",
    "posted_date_reference": "2026-05-09",
    "fim_inscricao": "2027-09-30",
    "prazo_envio_raw": "2027-09-30",
    "deadline": "2027-09-30",
    "deadline_source": "close_date",
    "deadline_confidence": "alta"
  },
  "posted_only": {
    "grants_close_date": null,
    "deadline_source_field": null,
    "posted_date_reference": "2026-05-09",
    "deadline_missing_in_source": true,
    "deadline_confidence": "nenhuma"
  }
}
```
# EditalFinder V2 — recuperação de arquivos (15/10/2026)

Este arquivo ZIP reúne os artefatos autênticos recuperados das conversas anteriores.
Seu conteúdo foi extraído do `editalfinder-v2-recovery.zip`, criado em julho de 2026.

Contém:
- `docs/v2/` — 9 documentos de contratos, decisões, plano e validações.
- `supabase/migrations/` — migrations V2 000001 e 000002.
- `audit/field-mapping/` — 10 artefatos de auditoria.
- `FIELD_MAPPING_AUDIT.md` — relatório consolidado.
- `RECOVERY_README.md` e `SHA256SUMS.txt` — pacote original.

NÃO contém `backend/v2/`, implementação Python, testes, `.env` ou credenciais.
A implementação de Python relatada posteriormente nas conversas não foi recuperada neste ZIP.

Extraia na raiz do repositório com `unzip -n editalfinder-v2-restauracao-pronta.zip -d /caminho/Projeto`.
A opção `-n` evita sobrescrever arquivos presentes.

ATENÇÃO:
- Não execute as migrations automaticamente. Verifique antes o estado do Supabase staging.
- Não altere as migrations originais.
- Não modifique o Legacy sem plano explícito de migração.
- Faça commit da documentação recuperada em uma branch própria.
- Depois, reconstrua `backend/v2/` de forma isolada, guiando-se pelos contratos.

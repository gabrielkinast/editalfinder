# EditalFinder V2 — Parecer técnico independente da M1.1

**Escopo:** código recebido em `V2.tar(1).gz`, revisão offline dos contratos Pydantic, `validation.py`, `safety.py`, testes e documentação. **Não houve** execução de crawler, Supabase ou alterações no projeto do usuário.

## Parecer

**M1.1: apta como base offline conservadora, com correção recomendada antes de declarar a auditoria durável completa. Não apta para promoção automática nem persistência canônica.** O segundo ponto é uma decisão de segurança intencional, não um bug: `promotable` é sempre falso e as afirmações de intenção exigem revisão de confiança ainda não implementada. A M1.1 não mede precisão ou recall de oportunidades reais.

## Verificações

- Reexecução no ambiente de revisão: **274 passed in 0.59s** (`python -B -m pytest -q -p no:cacheprovider`), Python 3.13.5. Não equivale a certificar a matriz 3.11–3.14.
- No ambiente do usuário, `ruff check` e `mypy src` passaram; `ruff format --check` apontou apenas `models.py` e `tests/test_integrity.py`. Ruff/mypy não estavam disponíveis no ambiente de revisão, portanto não foram reexecutados aqui.
- Reproduzidos diretamente: mistura de dois registros retorna `REVIEW` e `evidence_scope_mismatch`; valor `date` indevido para `title` continua `REVIEW` antes/depois de serialização; JSON `1e999` gera ValueError; JSON Pointer extremo retorna `(False, None)`; URL com controle é inválida; `ValidationReport.promotable=False`.
- Teste exploratório adicional: **1.000 candidatos válidos perante os modelos, com mutações determinísticas** em campos, valores, ponteiros e payloads. Resultado: 882 relatórios, 118 erros operacionais, **zero exceções não tratadas e zero divergências no round-trip de relatórios** nesse conjunto. Não é prova de ausência de bugs.

## Achado 1 — Envelope de auditoria do relatório não cobre todos os dados (MÉDIA; antes de persistência durável)

**Local:** `src/editalfinder_v2/domain/models.py`, `ValidationReport.bind_validation_audit()` e `ValidationAudit`.

O envelope vincula candidato, evidências, snapshots, catálogo e versões de regras. Ele **não** vincula integralmente `decision`, `reference_date`, `temporal_status`, conteúdo/mensagens das `issues`, nem seus vínculos com evidências. É uma limitação do escopo atual do digest, não um bypass de autorização, pois `promotable` continua falso.

Reprodução, com `PYTHONPATH=src:tests` e sem I/O remoto:

```python
import json
from datetime import date
from fixtures import example
from editalfinder_v2.domain.models import ValidationReport
from editalfinder_v2.domain.validation import validate

s, c = example(deadline=date(2025, 1, 1))
original = validate(c, (s,), reference_date=date(2026, 6, 1))
dados = json.loads(original.model_dump_json())
dados["temporal_status"] = "nao_determinada"
dados["reference_date"] = "2027-01-01"
dados["issues"][0]["message"] = "texto adulterado"
alterado = ValidationReport.model_validate(dados)
assert alterado.audit == original.audit  # passa apesar das mudanças
```

**Recomendação:** antes de gravar relatórios como auditoria durável, definir um envelope com digest da representação completa do resultado (ou hashes individuais dos campos acima), incluindo `decision`, data de referência, status temporal, issues com campos e evidências, atestados e versões. Não calcular hash circular incluindo o próprio envelope; distinguir integridade de autenticidade. Criar testes que alterem **um campo de cada vez** e esperem falha de validação. Não basta regenerar o digest do conteúdo adulterado; autenticidade exige referência externa confiável quando a persistência for implementada.

## Achado 2 — Custo superlinear sem limite de afirmações (BAIXA/MÉDIA; antes de aceitar grandes lotes não confiáveis)

**Local:** `validation.py`, função local `issue()` e laços sobre `candidate.assertions`.

Cada issue revarre as afirmações para buscar evidências. Muitos campos inválidos podem gerar múltiplas varreduras e custo aproximadamente quadrático. Medição local com candidatos Pydantic válidos contendo campos não suportados e valor `None`:

| Número de afirmações | Tempo medido (uma execução) |
|---:|---:|
| 100 | 0,001 s |
| 300 | 0,007 s |
| 600 | 0,025 s |
| 1.200 | 0,198 s |

**Recomendação:** indexar afirmações/evidências uma vez por campo; estabelecer limites explícitos e versionados de afirmações/evidências por candidato; testar cenários próximos aos limites. Não é um bug funcional na coleta piloto normal.

## Correções da M1 confirmadas

- `DocumentUnit` mais caminho estrutural direto e papel semântico de evidência; políticas para relações interdocumentais ainda bloqueadas conscientemente.
- Transporte de escalares tipado por tag para estabilidade de `date`, `bool`, `Decimal` e `str`.
- `safety.py` com limites explícitos, checagem de finitude e validação HTTP(S) conservadora.
- `manual_review` não autentica ninguém e não concede promoção.
- Relatórios recebidos como DTO nunca concedem capacidade de escrita.
- Ausência de `ACCEPTED`/`REJECTED` automáticos é limitação temporária explicitamente documentada no README.

## Próximas ações recomendadas

1. Aplicar `ruff format` apenas aos dois arquivos apontados e reexecutar `pytest`/Ruff/mypy.
2. Implementar o **digest completo do relatório** em correção pequena M1.1a, sem alterar o Legacy, as migrations ou a política de bloqueio de revisão humana.
3. Adicionar limites de tamanho e melhorar a indexação no validador antes de ingestão em volume.
4. Aprovar separadamente a política de interpretação de acionabilidade por fonte e o mecanismo externo de autorização de revisão antes de habilitar `ACCEPTED` operacional.
5. Só depois iniciar M2 de identidade e normalização; preservar a decisão de **não** publicar automaticamente candidatos enquanto a confiança não estiver resolvida.

**Nota:** escopo limitado a testes sintéticos e auditoria estática/execução offline. Não houve avaliação em documentos reais da FAPERGS.

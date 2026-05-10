# Diagnóstico — `thales_suppliers` (lote 5)

## O crawler corre?

Sim. `python thales_suppliers/main_thales_suppliers.py` termina com exit code 0. Antes da correção, gravava **0** registos porque a saída bruta era `[]`.

## Quais seeds foram usadas?

**Atuais (após análise):**

- `https://www.thalesgroup.com/en/supplier`
- `https://www.thalesgroup.com/en/supplier-relations`

**Histórico / problemáticas (referência lote 5 suppliers):**

- `/en/group/procurement` — 404 ou institucional fora do foco.
- `/en/countries` — ruído geográfico.

## Por que 0 brutos?

1. **Incapsula / Imperva:** respostas `requests` frequentemente são HTML mínimo (~1 KB) com scripts de desafio, não o DOM com âncoras reais.
2. **`scrape_html_portal`:** exige âncora com texto ≥ 6 caracteres e keywords em `título + URL`; na página Thales, PDFs aparecem muitas vezes com rótulo curto (“PDF”) ou estrutura onde o texto útil não está no `<a>`.
3. Com listagem inútil, **nenhum URL de detalhe** passa nos filtros → lista vazia.

## Há PDFs de Supplier Requirements?

Sim, na secção pública **Key documents** (Supplier Relations), por exemplo:

- Security Requirements — Purchasing  
- GRAEP (Generic Requirements Applicable to External Providers)  
- General terms and conditions of purchase  

URLs em `sites/default/files/...pdf` (ver `lote5_thales_examples.json`).

## Há página supplier relations / procurement?

Sim: o hub `.../en/supplier` (e conteúdo paralelo em supplier-relations) descreve procurement, documentos-chave e ferramentas colaborativas.

## Há ação concreta para fornecedor?

Sim: documentação contractual/técnica aplicável a fornecedores; referência a onboarding/sourcing em ferramentas com **acesso restrito** (não criámos URLs de login inventadas).

## Login / portal sem contexto?

- **e-ACQuisition / Air Supply:** descritos como acesso restrito — não são itens isolados de “só login”.
- **Anti-bot:** limita fetch automatizado; **não** foi contornado com captcha bypass ou paywall.

## Artefactos gerados

- `lote5_thales_diagnostico.json` — máquina-legível.  
- `lote5_thales_examples.json` — exemplos de URLs e campos pós-transformação.

# Diagnóstico — `bae_systems_suppliers` (lote 5)

## O crawler corre?

Sim. `python bae_systems_suppliers/main_bae_systems_suppliers.py` conclui com sucesso. Antes da correção, a saída bruta era `[]`.

## Quais seeds foram usadas?

- `https://www.baesystems.com/en-uk/suppliers/responsible-supply-chain`
- `https://www.baesystems.com/en/suppliers`

(Referência histórica em `source_access`: seed `.../en/suppliers` com HTML muito curto no probe.)

## Por que 0 brutos antes?

1. **`baesystems.com`**: respostas **403 / Incapsula / “Pardon Our Interruption”** com HTML curto — `scrape_html_portal` quase não vê âncoras úteis.
2. **Heurística de âncoras**: texto mínimo + keywords em `título + URL`; sem DOM real, nada entra na fila de detalhe.
3. **HICX**: links oficiais estão noutro host (`baesystems.hicx.net`); se a listagem corporativa falha, o crawler genérico **nunca** chega ao portal.

## Há página oficial suppliers / portal / registo?

- **Corporate:** URLs UK/en de suppliers / responsible supply chain são oficiais, mas frequentemente **bloqueadas a bots**.
- **HICX:** páginas públicas com texto explícito de **New Supplier Registration** e **Supplier Portal** (login) em `baesystems.hicx.net`.

## Há portal HICX oficial?

Sim — **Supplier Manager powered by HICX** em `baesystems.hicx.net` (caminho `.../hicxesm-portal/app/...`), alinhado à relação BAE–HICX documentada publicamente (sem usar páginas de blog `hicx.com` como fonte primária).

## Documentos / supplier requirements?

Nesta colheita: **sem PDFs** (páginas HICX são HTML de registo/login; corporate PDFs não foram obtidos por WAF). Documentos podem ser acrescentados no futuro se URLs públicas forem identificáveis sem inventário.

## Ação concreta para fornecedor?

Sim — registo de nova empresa na base de fornecedores (texto na página `discovery-login`) e portal de conta (index).

## Login sem contexto útil?

Não — itens descrevem **registo** ou **login a contas de fornecedor** com contacto `ebusiness@baesystems.com`; não há URL de login inventada.

## Ficheiros gerados

- `lote5_bae_diagnostico.json`
- `lote5_bae_examples.json`

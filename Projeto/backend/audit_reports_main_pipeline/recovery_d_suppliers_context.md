# Recovery D — Contexto e diagnóstico (Supplier Portals)

## Totais

- **suspeito_ativo_true** (staging, post_daily): **47**

## Ranking parcial (fontes com suspeito_ativo_true)

- AMAZUL: 12
- General Dynamics Suppliers: 6
- Apex Brasil: 4
- Petrobras: 4
- BASA: 3
- Lockheed Martin Suppliers: 3
- SENAI: 2
- BADESUL: 2
- BAE Systems Suppliers: 2
- EIT: 2
- Rheinmetall Suppliers: 2
- Softex: 2
- ESA OSIP: 1
- Thales Suppliers: 1
- UKRI Funding: 1

## Esta onda (apenas GD / LM / BAE)

```
{"General Dynamics Suppliers": 6, "Lockheed Martin Suppliers": 3, "BAE Systems Suppliers": 2}
```

## Classificação preliminar (Parte 2)

- **supplier_registration_real** — `general_dynamics_suppliers` — [Mentor-Protégé Program](https://www.gd.com/suppliers/mentor-protege-program) — Conteudo publico programa fornecedor; manter incompleto se faltar prazo/valor.
- **institucional_generico** — `general_dynamics_suppliers` — [SUPPLIERS (landing gdls)](https://www.gdls.com/suppliers/) — Hub ethics/blue book; candidato ativo=false ou revisao manual.
- **supplier_registration_real** — `general_dynamics_suppliers` — [iSUPPLIER](https://www.gdls.com/suppliers/isupplier) — Portal Oracle; acesso_limitado.
- **supplier_registration_real** — `lockheed_martin_suppliers` — [Doing Business](https://www.lockheedmartin.com/en-us/suppliers/information.html) — Informacao publica procurement.
- **institucional_generico** — `lockheed_martin_suppliers` — [C4ISR / capabilities](https://www.lockheedmartin.com/en-us/capabilities/c4isr.html) — Produto/capability; nao cadastro — candidato ativo=false.
- **supplier_registration_real** — `bae_systems_suppliers` — [New supplier registration (HICX)](https://baesystems.hicx.net/bae/hicxesm-portal/app/discovery-login.html) — Registo self-service com contexto publico; incompleto/acesso_limitado.
- **login_isolado** — `bae_systems_suppliers` — [Login index (removido crawl)](https://baesystems.hicx.net/bae/hicxesm-portal/app/index.html) — Removido do harvest; se reaparecer manter suspeito + ocultar frontend.

## Causa provável

Classificacao supplier_portal + validacao suspeito por falta de prazo/valor e mistura de landings e PDFs de politica.

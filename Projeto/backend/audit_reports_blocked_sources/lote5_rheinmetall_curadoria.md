# Curadoria — `rheinmetall_suppliers` (lote 5)

**Data:** 2026-05-03  
**Bruto:** `rheinmetall_suppliers/outputs/rheinmetall_suppliers_editais.json` (**2** itens).

---

## 1. Análise dos 2 brutos

### Item A — `Become a supplier`

- **URL:** `https://www.rheinmetall.com/en/suppliers/become-a-supplier`
- **Classificação curatorial:** **onboarding de fornecedor** + texto que descreve o **procurement portal** corporativo (não é página institucional genérica nem política isolada).
- **Rótulos:** `onboarding_fornecedor` ✓ · `procurement_portal` ✓ · **não** `página institucional` · **não** `política genérica` · **não** `login sem contexto` (menções a login fazem parte do fluxo de registo descrito).
- **Ações concretas no texto:** *become a supplier*, *New supplier / Registration*, *procurement portal*, *self-registration*, *onboarding*, *sourcing*, *contract management*.

### Item B — `Rheinmetall procurement portal`

- **URL:** `https://rheinmetall-supplier.ivalua.app`
- **Classificação curatorial:** **supplier_portal real** (Ivalua), entrada do **procurement** do grupo.
- **Rótulos:** `supplier_portal_real` ✓ · `procurement_portal` ✓ · **não** institucional genérico · **não** política-only · **não** `login sem contexto` isolado (o destino é portal; login é passo esperado, não contornado).
- **Evidência:** título + domínio **ivalua** alinhado ao ecossistema público descrito na página “Become a supplier”; descrição no bruto é **curta** → tratamento como **menos detalhe**, não como fora de escopo.

**Conclusão:** **ambos úteis** para o produto como **oportunidade de fornecedor**; **nenhum** removido do crawler nesta curadoria.

---

## 2. Campos alinhados (após ajuste em `calibrate_corporate_supplier_sources_extras`)

| Campo | Política aplicada |
|--------|-------------------|
| `tipo_oportunidade` | `cadastro_fornecedor` (A) · `supplier_portal` (B) |
| `tipo_recurso` | `oportunidade_fornecedor` |
| `perfil_ideal` | `fornecedor`, `empresa` |
| `origem_portal` | `Rheinmetall` |
| `validacao_status` (nível superior) | `incompleto` (A — sem prazo/valor) · `acesso_limitado` (B — descrição curta + portal) |
| Defesa / setor | **Sem** `setor_estrategico` por nome da empresa; **tags ML** (`thematic_tags`) **limpas** para Rheinmetall; `setor_economico` **vazio** sem evidência textual militar/defesa |

**Gate:** mantém-se `opportunity_gate_relaxed` com `corporate_supplier_local` onde aplicável — **sem** alteração ao `opportunity_gate` global.

---

## 3. Pipeline executado (pedido tarefa 6)

```text
python scripts/retransform_all.py --sources rheinmetall_suppliers --dry-run --output-dir audit_reports_blocked_sources/lote5_rheinmetall_curated
python scripts/audit_semantic_classification.py --input-dir audit_reports_blocked_sources/lote5_rheinmetall_curated/standardized --output-dir audit_reports_blocked_sources/lote5_rheinmetall_curated_semantic
python scripts/audit_docs_pipeline.py --sources rheinmetall_suppliers --output-dir audit_reports_blocked_sources/lote5_rheinmetall_curated_docs
```

**Standardized:** `audit_reports_blocked_sources/lote5_rheinmetall_curated/standardized/rheinmetall_suppliers_standardized.json`  
**Auditorias:** `lote5_rheinmetall_curated_semantic/`, `lote5_rheinmetall_curated_docs/` (2 itens; sem PDFs; sem perdas de documentos).

---

## 4. Readiness recomendado

### **`ready_with_notes`**

**Motivos:** dois links oficiais; ação de fornecedor clara no primeiro e portal real no segundo; taxonomia coerente com **fornecedor corporativo**, não edital público; **não** há política corporativa isolada nem página “about” como único conteúdo.

**Notas obrigatórias:** (1) volume **baixo**; (2) segundo registo com **descrição curta** e continuação em **portal com login**; (3) `publico_alvo_sem_evidencia` pode aparecer no audit semântico genérico — o `publico_alvo` em `extras` está preenchido pela calibração.

**Não recomendado:** `blocked`, `fora_de_escopo`, ou `needs_manual_review` **para a fonte inteira** após esta curadoria — desde que o produto aceite **corporate supplier** com observações.

---

## 5. O que **não** foi feito (conforme pedido)

- `source_readiness.json` **não** atualizado.  
- Loader **apply** não executado.  
- Supabase / migrations / gate global **inalterados**.  
- Outras fontes do lote 5 **não** alteradas.

---

## JSON

`audit_reports_blocked_sources/lote5_rheinmetall_curadoria.json`

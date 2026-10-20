# EditalFinder V2 — M2.3c: End-to-End Offline Pipeline Validation

## A. Baseline and scope

Baseline independently executed before edits: **1691 passed in 8.92s**.
Historical 1691 was not assumed. Final previous-only regression run: **1691 passed in 9.14s**.
New M2.3c run: **119 passed in 5.29s**. Full run: **1810 passed in 13.98s**.
No tests skipped/xfail'd or historical expectations weakened.

Git inspection covered repository-wide tracked changes and untracked files. Preexisting
README modifications, prior untracked milestones/tests/normalizers and the SQL deletion
were preserved. Initial SHA-256 inventory of 115 existing V2 files (src/tests/docs/root
Markdown, excluding caches) was rechecked: **zero modified or missing**. No production
code, README, Legacy or SQL was edited. No staging or commits occurred.

Inspected README, architecture decisions/data/geography/schema contracts, M23B results and
independent review, all integration modules, M1 engine/policies, M2 identity/temporal/
geography/financial/organization/taxonomy normalization contracts and implementations,
M23B consistency rules and existing integration, output-budget and audit fixtures/tests.
Current approved contracts take precedence over superseded proposal text.

This is end-to-end composition from structured inputs through the actual `integrate`
entry point. It is NOT raw-text extraction, website crawling or PDF processing. No remote
source, API, database, Supabase or real document was accessed. No persistence, promotion,
merge or following milestone was implemented.

## B–D. Frozen fixtures, manual oracle and E2E scenarios

Primary deliverables: `tests/fixtures/m23c_v1.json`,
`tests/fixtures/m23c_operational_v1.json`, and `docs/v2/M23C_FROZEN_ORACLE.md`.
The architecture document contains the explicit oracle-to-contract traceability table,
case register A–I and product coverage matrix. It is part of this report.

26 semantic cases, 37 candidate slots, seven operational manifest cases. Synthetic IDs,
source records, record pointers, candidate assertions, evidence and comparison instructions
are deterministic. Expectations were manually specified before evaluation, not captured
from the system under test. Test-only projections reuse existing DTO fields; no duplicate
domain contract or new financial/taxonomy code was added.

The manifest specifies ordered diagnostic codes, normalized financial roles/endpoints/
currency, temporal roles/civil values/timezone/UTC, geography roles/components, taxonomy
code/status, organization roles/names, M1 constraints/status, identity results, scope,
audit replay and operational status. Every expected section has contract support.
Each semantic case invokes `integrate`, checks meaningful fields and revalidates Python/JSON
reports. Inputs, claims, originals, source contexts and output order remain traceable.

New tests by module:
- `tests/test_m23c_adversarial.py`: 45 tests.
- `tests/test_m23c_metamorphic.py`: 19 tests.
- `tests/test_m23c_pipeline.py`: 27 tests.
- `tests/test_m23c_product_contracts.py`: 20 tests.
- `tests/test_m23c_resources.py`: 8 tests.

## E–F. Product and negative controls

FOMENTO: BRL 10,000,000 program budget and BRL 500,000 proposal ceiling stay distinct.
Publication/opening/submission roles, publisher/funder, research area/type/resource and BR
eligibility are preserved. No funded-project count, guaranteed award, inferred eligibility
or automatic approval is created.

CRÉDITO: an explicit development-bank repayable program retains purpose, application text,
principal/limit and conditional guarantee statement as original evidenced assertions.
Approved repayable taxonomy maps exactly; `consistency_credit_terms_unrepresented` is
required. Principal/interest/carência/repayment/guarantees have no approved normalized
financial-term roles. Interest and carência are absent, not filled with invented values.

INVESTIMENTOS: entity, program/cycle, geographic restrictions, applicant/application text,
ticket/range and equity expression are preserved. `venture_capital` remains unknown, with
`taxonomy_mapping_not_approved` and `consistency_taxonomy_unsupported`; no taxonomy code,
valuation, ownership percentage, credit fallback or investment approval is fabricated.

Hybrid: grant ceiling and original credit principal remain separate. Coexistence produces
unverified-relationship observations, not a contradiction. Reverse endpoints within one
expression do produce the existing definite range contradiction. Min/max across claims
remain potential conflict without instrument identity. A typed relationship proving two
claims concern the very same instrument does not exist and was not invented.

All six explicit negative controls remain REVIEW and non-promotable: completed-program
news, selection results, investment press release, historical closed instrument, general
product page and auxiliary edital reference. The historical direct date produces
`encerrada` at fixed reference date 2026-07-01. No future M2 collection deadline implies
current M1 availability. REVIEW is deliberately not presented as authenticated rejection
or acceptance.

## G. Metamorphic verification

Candidate permutation changes batch order/digest but preserves each complete candidate
result. Adding unrelated records/news preserves per-candidate semantic projections,
diagnostics and M1 issues/decision while snapshots/audits legitimately change. Changing
publisher-origin country does not alter applicant eligibility. Additional independent
money does not relabel existing amounts. Repeated inputs have byte-identical ordered
reports; Python/JSON reconstruction preserves results. Changing an explicit cycle prevents
an unsupported exact match. Mutation controls change manual expected codes/roles and
require assertion failure, guarding against vacuous oracle checks.

## H–I. Adversarial, identity and evidence isolation

Received report mutations cover snapshots, units, pointers, financial roles/amounts/
currency, geographic roles, temporal stages, organization roles, taxonomy dimension,
diagnostic codes, M1 decisions, diagnostic evidence, identity decisions/order, audit
metadata and report digest. Twelve mutations are tested both with retained envelopes and
with ALL audit envelopes removed; replay still rejects altered results. Five additional
mutations exercise constructor, Python validation and JSON validation routes.

The multi-record chimera keeps news title/URL but borrows actionability/deadline from the
funding record and principal from the credit record. It remains REVIEW/non-promotable;
foreign normalized facts are unavailable, diagnostic rejected-witness evidence is empty,
and the valid funding, credit, investment and selection-result candidates remain exactly
unchanged in the same batch. Separate transplants cover all five normalization domains.

Organization nuance: approved M22B preserves lexical normalized names even for unsupported
proof, but emits `organization_evidence_invalid` and suppresses comparison keys. Tests
assert that exact contract; lexical presentation is not certified legal identity.

Explicit comparisons are ordered, never implicit all-pairs. Equivalent approved URL
normalizations do not grant identity by themselves; official identifier/cycle context is
required. Different official IDs, namespaces, publication cycles, foreign proof and missing
IDs are exercised. Same snapshot/hash never substitutes for identity. Exact contextual
matches keep two distinct candidates with distinct financial claims/proofs and no merge.

## J. Audit and serialization

Complete ordered reports round-trip through strict Python/JSON validation and deterministic
recomputation. SHA-256 of the full serialized body excluding only the outer audit equals
the retained report digest. Domain audits and bound contexts remain present. Forged
metadata/digests are refused; omission of an envelope allows new local recomputation,
not restoration of historical authority. An archived envelope missing budget policy is
refused strictly; input-only reprocessing succeeds separately without modifying or
backfilling the archived envelope. Manual-review extraction labels and arbitrary input
flags never confer trusted review, promotion or merge authority. Hashes detect divergence
against retained envelopes; they are not signatures or source authenticity.

Initial harness failures are documented in M23C_FROZEN_ORACLE.md. They are not represented
as RED proof of missing production features. This milestone characterizes existing code;
there is no production implementation RED→GREEN claim. No runtime correction was needed.

## K. Resource and performance measurements

Unchanged policy: 64 MiB admission budget, `m2.3a.1-output-budget-v1`; 32 candidates,
64 explicit comparisons, 4800 combined claims, 16 MiB unique snapshot input, existing
per-domain/M1/parser limits remain in force. Refusals are OperationalError, not REJECTED,
and never silently truncate. Collision tests fail both affected shared-snapshot owners
and comparisons while preserving an unrelated healthy candidate.

The bounded near/over search changes one padding character per each of four records;
the admissible case reaches exactly **67108864 charge bytes**. The estimator's over-limit
return is saturated at **67108865**, not an exact measurement of uncapped projected cost.
Only about 305 KB of unique snapshot input is used. The four-candidate near case retains
every candidate and round-trips its roughly 10 MB report. Duplicate IDs, conflicting shared
snapshots, over-budget batches and 65 identity comparisons have explicit error expectations.

Benchmark: three fresh sequential processes per scenario; inputs constructed before
measurement. `time.perf_counter` measures actual integrate (including report replay), dump
and received DTO validation. `tracemalloc` spans those phases. No timing pass threshold.
It is NOT RSS, a transport limit or a production SLA. In particular the near-case Python
allocation peak exceeds 64 MiB, demonstrating why admission cost is not a memory ceiling.
Over-budget validation below is validation of OperationalError, not report validation.

Actual environment: Python 3.11.16, Pydantic 2.14.1, pytest 9.1.1, Ruff 0.17.1,
mypy 2.4.0 (compiled); Linux 7.0.0-38-generic x86_64, glibc 2.43, 12 logical CPUs.
No cross-version determinism guarantee is asserted.

Full samples/environment/methodology: `docs/v2/M23C_BENCHMARK.json`.

| Scenario | Result | Admission bytes | Serialized bytes | Integrate median s | Dump median s | Validate median s | Python peak median bytes |
|---|---|---:|---:|---:|---:|---:|---:|
| M23C-A-001 | IntegrationReport | 7020928 | 166688 | 0.060164 | 0.002205 | 0.080185 | 2340972 |
| M23C-B-001 | IntegrationReport | 4567344 | 116689 | 0.041661 | 0.001605 | 0.054554 | 1649239 |
| M23C-C-001 | IntegrationReport | 4520240 | 115936 | 0.039978 | 0.001619 | 0.053598 | 1643836 |
| M23C-E-001 | IntegrationReport | 21705888 | 654467 | 0.194339 | 0.007645 | 0.282845 | 7437960 |
| near | IntegrationReport | 67108864 | 9969994 | 0.774043 | 0.013430 | 0.562682 | 71342429 |
| over | OperationalError | 67108865 | 163 | 0.004735 | 0.000019 | 0.000020 | 305904 |

Reproduce: `PYTHONPATH=src:tests .venv/bin/python -B tests/benchmark_m23c_pipeline.py --output <new-path.json>`.

## L. Product coverage matrix and future decisions

See the full FOMENTO/CRÉDITO/INVESTIMENTOS matrix in M23C_FROZEN_ORACLE.md, including
represented concepts, unresolved originals, unsupported normalized terms, evidence and
future contracts. Credit rates/basis, carência, repayment schedules, guarantee models and
credit eligibility require approved instrument/terms/applicant contracts. Investment
rounds, equity, valuation, instrument and ownership conditions require approved taxonomy
and typed relationships. These gaps were documented, not implemented.

Remaining common limitations: structured-input provenance is not source truth; no extraction
quality or precision/recall measured; no trusted human-review adapter; M2 does not automatically
project values into M1; no instrument/tranche/proposal/stage/window/legal-entity identity;
no rectification precedence; no municipal certification, implicit country, automatic
current availability, real-data gold set, transport cap, historical-policy verifier or
persisted chain of custody. Full permutation invariance of ordered batches is NOT promised.

## M. Files created and modified

Created in this milestone (all under V2):

- tests/fixtures/m23c_v1.json
- tests/fixtures/m23c_operational_v1.json
- tests/m23c_fixtures.py
- tests/test_m23c_pipeline.py
- tests/test_m23c_metamorphic.py
- tests/test_m23c_adversarial.py
- tests/test_m23c_product_contracts.py
- tests/test_m23c_resources.py
- tests/benchmark_m23c_pipeline.py
- docs/v2/M23C_FROZEN_ORACLE.md
- docs/v2/M23C_BENCHMARK.json
- docs/v2/M23C_QUALITY_GATES.json
- EDITALFINDER_V2_M23C_RESULTADOS.md

No preexisting file modified. Only these new Python files were formatted/fixed for lint.
The preexisting m23_fixtures.py remains byte-identical and has not been silently repaired.
Review evidence/inventory files, if added after this draft, are listed in section P.

## N. Exact executed quality gates

Ruff GLOBAL DOES NOT PASS: the same seven preexisting findings and the same single fixture
formatting failure were reproduced before and after this milestone. Excluding only that
file passes both checks; this is supplemental evidence, not a claim that global gates pass.
Mypy passes; git diff --check passes. Untracked M23C files receive separate content/hash/
whitespace inspection because git diff --check alone does not inspect them.

Machine-readable exact command/exit/stdout records: `docs/v2/M23C_QUALITY_GATES.json`.
Actual output follows, without inventing successful results for failed gates.

### full_pytest (exit 0)

```text
$ .venv/bin/python -B -m pytest -p no:cacheprovider -q
........................................................................ [  3%]
........................................................................ [  7%]
........................................................................ [ 11%]
........................................................................ [ 15%]
........................................................................ [ 19%]
........................................................................ [ 23%]
........................................................................ [ 27%]
........................................................................ [ 31%]
........................................................................ [ 35%]
........................................................................ [ 39%]
........................................................................ [ 43%]
........................................................................ [ 47%]
........................................................................ [ 51%]
........................................................................ [ 55%]
........................................................................ [ 59%]
........................................................................ [ 63%]
........................................................................ [ 67%]
........................................................................ [ 71%]
........................................................................ [ 75%]
........................................................................ [ 79%]
........................................................................ [ 83%]
........................................................................ [ 87%]
........................................................................ [ 91%]
........................................................................ [ 95%]
........................................................................ [ 99%]
..........                                                               [100%]
1810 passed in 13.98s
```

### previous_pytest (exit 0)

```text
$ .venv/bin/python -B -m pytest -p no:cacheprovider -q --ignore=tests/test_m23c_adversarial.py --ignore=tests/test_m23c_metamorphic.py --ignore=tests/test_m23c_pipeline.py --ignore=tests/test_m23c_product_contracts.py --ignore=tests/test_m23c_resources.py
........................................................................ [  4%]
........................................................................ [  8%]
........................................................................ [ 12%]
........................................................................ [ 17%]
........................................................................ [ 21%]
........................................................................ [ 25%]
........................................................................ [ 29%]
........................................................................ [ 34%]
........................................................................ [ 38%]
........................................................................ [ 42%]
........................................................................ [ 46%]
........................................................................ [ 51%]
........................................................................ [ 55%]
........................................................................ [ 59%]
........................................................................ [ 63%]
........................................................................ [ 68%]
........................................................................ [ 72%]
........................................................................ [ 76%]
........................................................................ [ 80%]
........................................................................ [ 85%]
........................................................................ [ 89%]
........................................................................ [ 93%]
........................................................................ [ 97%]
...................................                                      [100%]
1691 passed in 9.14s
```

### new_pytest (exit 0)

```text
$ .venv/bin/python -B -m pytest -p no:cacheprovider -q tests/test_m23c*.py
........................................................................ [ 60%]
...............................................                          [100%]
119 passed in 5.29s
```

### ruff_check (exit 1)

```text
$ .venv/bin/ruff check --no-cache src tests
B023 Function definition does not bind loop variable `unit`
  --> tests/m23_fixtures.py:70:22
   |
68 |                 method_version="m23-synthetic-v1",
69 |                 confidence="1",
70 |                 unit=unit,
   |                      ^^^^
71 |                 semantic_role=role,
72 |             )
   |

B023 Function definition does not bind loop variable `assertions`
  --> tests/m23_fixtures.py:73:13
   |
71 |                 semantic_role=role,
72 |             )
73 |             assertions.append(FieldAssertion(field=role, value=original, evidence=(evidence,)))
   |             ^^^^^^^^^^
74 |             return SemanticValue(
75 |                 original=literal,
   |

B023 Function definition does not bind loop variable `cid`
  --> tests/m23_fixtures.py:77:34
   |
75 |                 original=literal,
76 |                 provenance=IdentityEvidence(
77 |                     candidate_id=cid,
   |                                  ^^^
78 |                     source_id=source,
79 |                     execution_id=execution,
   |

E501 Line too long (102 > 100)
   --> tests/m23_fixtures.py:147:101
    |
145 |                     TemporalClaim(role=row["role"], value=components["value"], format=row["format"])
146 |                     for row, components in zip(
147 |                         record.get("temporal_events", []), collections["temporal_events"], strict=True
    |                                                                                                     ^^
148 |                     )
149 |                 ),
    |

E501 Line too long (104 > 100)
   --> tests/m23_fixtures.py:166:101
    |
164 |                     )
165 |                     for row, components in zip(
166 |                         record.get("financial_claims", []), collections["financial_claims"], strict=True
    |                                                                                                     ^^^^
167 |                     )
168 |                 ),
    |

E501 Line too long (110 > 100)
   --> tests/m23_fixtures.py:172:101
    |
170 |                     OrganizationClaim(role=row["role"], name=components.get("name"))
171 |                     for row, components in zip(
172 |                         record.get("organization_claims", []), collections["organization_claims"], strict=True
    |                                                                                                     ^^^^^^^^^^
173 |                     )
174 |                 ),
    |

E501 Line too long (102 > 100)
   --> tests/m23_fixtures.py:178:101
    |
176 |                     TaxonomyClaim(role=row["role"], value=components["value"])
177 |                     for row, components in zip(
178 |                         record.get("taxonomy_claims", []), collections["taxonomy_claims"], strict=True
    |                                                                                                     ^^
179 |                     )
180 |                 ),
    |

Found 7 errors.
```

### ruff_format (exit 1)

```text
$ .venv/bin/ruff format --check --no-cache src tests
unformatted: File would be reformatted
   --> tests/m23_fixtures.py:147:59
    |
146 |                     for row, components in zip(
    -                         record.get("temporal_events", []), collections["temporal_events"], strict=True
147 +                         record.get("temporal_events", []),
148 +                         collections["temporal_events"],
149 +                         strict=True,
150 |                     )
--------------------------------------------------------------------------------
162 |                     FinancialClaim(
    -                         role=row["role"], value=components.get("value"),
163 +                         role=row["role"],
164 +                         value=components.get("value"),
165 |                         format=row.get("format", "unspecified"),
    -                         currency=row.get("currency"), unit=row.get("unit", "amount"),
166 +                         currency=row.get("currency"),
167 +                         unit=row.get("unit", "amount"),
168 |                     )
169 |                     for row, components in zip(
    -                         record.get("financial_claims", []), collections["financial_claims"], strict=True
170 +                         record.get("financial_claims", []),
171 +                         collections["financial_claims"],
172 +                         strict=True,
173 |                     )
--------------------------------------------------------------------------------
177 |                     for row, components in zip(
    -                         record.get("organization_claims", []), collections["organization_claims"], strict=True
178 +                         record.get("organization_claims", []),
179 +                         collections["organization_claims"],
180 +                         strict=True,
181 |                     )
--------------------------------------------------------------------------------
185 |                     for row, components in zip(
    -                         record.get("taxonomy_claims", []), collections["taxonomy_claims"], strict=True
186 +                         record.get("taxonomy_claims", []),
187 +                         collections["taxonomy_claims"],
188 +                         strict=True,
189 |                     )
    |

1 file would be reformatted, 83 files already formatted
```

### mypy (exit 0)

```text
$ .venv/bin/mypy --no-incremental --cache-dir=/dev/null src
Success: no issues found in 28 source files
```

### git_diff_check (exit 0)

```text
$ git diff --check

```

### ruff_except_preexisting (exit 0)

```text
$ .venv/bin/ruff check --no-cache --extend-exclude m23_fixtures.py src tests
All checks passed!
```

### format_except_preexisting (exit 0)

```text
$ .venv/bin/ruff format --check --no-cache --extend-exclude m23_fixtures.py src tests
83 files already formatted
```

## O. Unresolved decisions

No blocking production inconsistency was reproduced. Unsupported product concepts and
relationships listed above remain explicitly unresolved and require later contract approval.
Current synthetic coverage cannot certify all attacks, all source schemas, real offers,
authenticity, real-world precision/recall, publication safety or production memory bounds.
Global Ruff hygiene remains a known preexisting exception, not a newly passing gate.

## P. Independent review

One independent read-only AI reviewer completed the frozen-snapshot review and returned
**READY**, no blockers. It independently ran the full suite: **1810 passed in 14.11s**,
reproduced the seven preexisting global Ruff errors and the formatting failure, checked
benchmark medians and reran the actual near/over boundary. An additional URL-fragment
probe confirmed that shared official identifier/cycle can still establish contextual
identity while different fragments are not treated as the same locator.

Review artifact created after the draft:
`EDITALFINDER_V2_M23C_REVISAO_INDEPENDENTE.md` (findings, commands, limitations and hashes).
Delegation `deleg_2e75c01d`; transcript:
`/home/lorenzozm/.hermes/cache/delegation/live/deleg_2e75c01d/task-0.log`.

Snapshot `/home/lorenzozm/.hermes/cache/scratch/m23c-readonly-review`, 130 files;
FROZEN_HASHES.json SHA-256:
`b205bd790db9d59870988847d59a4c95bf130d64f94d6d6e60a025a0d811701c`.
The parent independently verified the manifest hash and all snapshot/current counterparts:
zero mismatches before this final report update. Initial 115 preexisting files also remain
unchanged. No tests, fixtures or runtime files changed following review. This report and
the new review artifact are the only post-review documentation changes.

Nonblocking reviewer suggestions, explicitly retained as limitations:

- Oracle-corruption controls prove active assertions, not general mutation sensitivity.
- M1 required-issue subsets do not reject every possible additional issue. Exact ordered
  integration and identity diagnostic expectations must not be confused with exact M1
  issue-list coverage; future fixture revisions can freeze permitted/exact M1 issues.
- Negative controls are declared structured records, not evidence of text classification
  accuracy. The frozen snapshot cannot independently establish authorship chronology.

This is additional AI review, not authenticated human approval or a professional audit.

## Q. Final assessment

**READY — only for M2.3c's existing conservative offline structured-input composition
verification scope, with the documented preexisting global Ruff exception.**

All 1691 previous tests and 119 new tests pass; the independent review found no blocker.
No production behavior was changed. This is not production, extraction, persistence,
authenticated review, promotion or merge readiness. Global Ruff is still NOT green.
Stop after M2.3c; await technical review. Do not start M2.3d or M3.
